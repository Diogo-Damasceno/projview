"""Executa os testes de um projeto com segurança, na máquina do dono.

Suporta múltiplos ecossistemas (detectados por convenção de arquivos):
  - Python  : pytest (pyproject.toml / pytest.ini / test_*.py)
  - Java    : Maven + JUnit (pom.xml -> `mvn test`, parseia surefire)
  - Node    : node --test (package.json com "test": "node --test" / test/*.test.js)
  - Shell   : Makefile com alvo `test` (ou test/ddfetch-test.sh)

Tudo roda em subprocess com timeout; NUNCA é executado no site — só no
momento do build, localmente.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import glob
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    nodeid: str
    name: str
    status: str  # passed | failed | skipped | error
    duration: float
    detail: str  # traceback ou mensagem curta


@dataclass
class SuiteResult:
    ran: bool
    total: int
    passed: int
    failed: int
    skipped: int
    tests: list[TestResult]
    error: str = ""


def run_tests(project_path: str, timeout: int = 180) -> SuiteResult:
    """Roda a suíte de testes do projeto e devolve SuiteResult.

    Detecta o ecossistema e delega. Se nenhum reconhecido, ran=False.
    """
    if not os.path.isdir(project_path):
        return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error="caminho do projeto inexistente")

    env = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        env.pop(k, None)

    # ordem de detecção: mais específico primeiro
    if os.path.isfile(os.path.join(project_path, "pom.xml")):
        return _run_maven(project_path, timeout, env)
    if _has_node_test(project_path):
        return _run_node(project_path, timeout, env)
    if _has_make_test(project_path):
        return _run_make(project_path, timeout, env)
    if _has_pytest(project_path):
        return _run_pytest(project_path, timeout, env)
    return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                       error="sem suíte de testes reconhecida")


# ---------------------------------------------------------------------------
# Python / pytest
# ---------------------------------------------------------------------------
def _has_pytest(project_path: str) -> bool:
    for f in ("pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"):
        p = os.path.join(project_path, f)
        if os.path.isfile(p):
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
                if "[pytest]" in txt or "pytest" in txt:
                    return True
            except OSError:
                pass
    for cur, _, files in os.walk(project_path):
        for fn in files:
            if fn.startswith("test_") and fn.endswith(".py"):
                return True
    return False


def _run_pytest(project_path: str, timeout: int, env: dict) -> SuiteResult:
    if os.path.isfile(os.path.join(project_path, ".venv", "bin", "python")):
        py = os.path.join(project_path, ".venv", "bin", "python")
    else:
        # projeto sem venv: usa o python do sistema (absoluto) para não
        # herdar um venv ativo no PATH do shell chamador.
        py = "/usr/bin/python3"
    # PATH limpo para garantir que o python usado seja o do sistema
    env = dict(env)
    env["PATH"] = "/usr/bin:/bin:/usr/local/bin:" + env.get("PATH", "")
    # garante que o pacote do projeto (src/ ou raiz) seja importável no teste
    existing = env.get("PYTHONPATH", "")
    for cand in ("src", "."):
        cp = os.path.join(project_path, cand)
        if os.path.isdir(cp) and cp not in existing:
            existing = (existing + ":" + cp) if existing else cp
    env["PYTHONPATH"] = existing
    with tempfile.TemporaryDirectory() as td:
        junit = os.path.join(td, "results.xml")
        try:
            proc = subprocess.run(
                [py, "-m", "pytest", "-q", "--tb=short", f"--junitxml={junit}"],
                cwd=project_path, capture_output=True, text=True, timeout=timeout, env=env,
            )
        except subprocess.TimeoutExpired:
            return SuiteResult(ran=True, total=0, passed=0, failed=0, skipped=0, tests=[],
                               error=f"timeout após {timeout}s")
        except FileNotFoundError:
            return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                               error="pytest não instalado neste Python")
        tests = _parse_junit(junit)
        if not tests:
            tests = _parse_text(proc.stdout + proc.stderr)
        return _summarize(tests, error="" if tests else "pytest não gerou resultados")


# ---------------------------------------------------------------------------
# Java / Maven + JUnit
# ---------------------------------------------------------------------------
def _run_maven(project_path: str, timeout: int, env: dict) -> SuiteResult:
    mvn = os.path.join(os.path.expanduser("~"), ".local", "share",
                       "apache-maven-3.9.9", "bin", "mvn")
    if not os.path.exists(mvn):
        mvn = "mvn"
    try:
        proc = subprocess.run(
            [mvn, "-o", "test"],
            cwd=project_path, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        return SuiteResult(ran=True, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error=f"timeout após {timeout}s")
    except FileNotFoundError:
        return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error="mvn não encontrado")
    tests = _parse_surefire(project_path)
    return _summarize(tests, error="" if tests else _maven_error(proc))


def _parse_surefire(project_path: str) -> list[TestResult]:
    rep = os.path.join(project_path, "target", "surefire-reports")
    if not os.path.isdir(rep):
        return []
    out = []
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        return out
    for xmlf in glob.glob(os.path.join(rep, "*.xml")):
        # pula o report resumo do surefire (sem casos de teste)
        try:
            tree = ET.parse(xmlf)
        except ET.ParseError:
            continue
        root = tree.getroot()
        cls = root.get("name", "")
        cases = list(root.iter("testcase"))
        if not cases:
            continue
        for tc in cases:
            name = tc.get("name", "?")
            status = "passed"
            detail = ""
            fail = tc.find("failure")
            err = tc.find("error")
            skipped = tc.find("skipped")
            if fail is not None:
                status = "failed"
                detail = (fail.get("message") or "")[:600]
            elif err is not None:
                status = "error"
                detail = (err.get("message") or "")[:600]
            elif skipped is not None:
                status = "skipped"
                detail = (skipped.get("message") or "")[:300]
            try:
                dur = float(tc.get("time", 0))
            except ValueError:
                dur = 0.0
            out.append(TestResult(nodeid=f"{cls}::{name}", name=name, status=status,
                                  duration=dur, detail=detail))
    return out


def _maven_error(proc) -> str:
    out = (proc.stdout or "") + (proc.stderr or "")
    for line in out.splitlines():
        if "BUILD FAILURE" in line or "ERROR" in line:
            return line.strip()[:300]
    return "mvn test sem surefire-reports"


# ---------------------------------------------------------------------------
# Node / node --test
# ---------------------------------------------------------------------------
def _has_node_test(project_path: str) -> bool:
    pj = os.path.join(project_path, "package.json")
    if os.path.isfile(pj):
        try:
            import json
            d = json.load(open(pj, encoding="utf-8"))
            scripts = d.get("scripts", {})
            if "test" in scripts and "node --test" in scripts["test"]:
                return True
        except (OSError, ValueError):
            pass
    return bool(glob.glob(os.path.join(project_path, "test", "*.test.js")))


def _run_node(project_path: str, timeout: int, env: dict) -> SuiteResult:
    env = dict(env)
    env["NODE_ENV"] = "test"
    try:
        proc = subprocess.run(
            ["node", "--test"],
            cwd=project_path, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        return SuiteResult(ran=True, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error=f"timeout após {timeout}s")
    except FileNotFoundError:
        return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error="node não encontrado")
    tests = _parse_node_tap(proc.stdout + proc.stderr)
    return _summarize(tests, error="" if tests else "node --test sem resultados")


def _parse_node_tap(out: str) -> list[TestResult]:
    tests = []
    cur_name = None
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("# Subtest:") or s.startswith("# Subtest:"):
            cur_name = s.split(":", 1)[1].strip()
        elif s.startswith("ok ") or s.startswith("not ok "):
            parts = s.split(None, 2)
            if len(parts) < 2:
                continue
            status = "passed" if parts[0] == "ok" else "failed"
            # procura nome entre aspas ou após o número
            name = cur_name or (parts[2].strip() if len(parts) > 2 else parts[1])
            tests.append(TestResult(nodeid=name, name=name, status=status,
                                    duration=0.0, detail=""))
            cur_name = None
    return tests


# ---------------------------------------------------------------------------
# Shell / Makefile `test`
# ---------------------------------------------------------------------------
def _has_make_test(project_path: str) -> bool:
    if os.path.isfile(os.path.join(project_path, "Makefile")):
        try:
            txt = open(os.path.join(project_path, "Makefile"), encoding="utf-8",
                       errors="ignore").read()
            if "\ntest:" in txt or "\ttest:" in txt or "test:" in txt:
                return True
        except OSError:
            pass
    return False


def _run_make(project_path: str, timeout: int, env: dict) -> SuiteResult:
    try:
        proc = subprocess.run(
            ["make", "test"],
            cwd=project_path, capture_output=True, text=True, timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired:
        return SuiteResult(ran=True, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error=f"timeout após {timeout}s")
    except FileNotFoundError:
        return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error="make não encontrado")
    out = (proc.stdout or "") + (proc.stderr or "")
    tests = _parse_shell(out)
    return _summarize(tests, error="" if tests else "make test sem resultados")


def _parse_shell(out: str) -> list[TestResult]:
    tests = []
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("ok -") or s.startswith("ok  -"):
            tests.append(TestResult(nodeid=s, name=s.split("-", 1)[1].strip(),
                                    status="passed", duration=0.0, detail=""))
        elif s.startswith("FAIL -") or s.startswith("FAIL  -"):
            tests.append(TestResult(nodeid=s, name=s.split("-", 1)[1].strip(),
                                    status="failed", duration=0.0, detail=""))
        # formato genérico PASS <nome> / FAIL <nome> (ex: testes Java via make)
        elif s[:5].upper() == "PASS ":
            tests.append(TestResult(nodeid=s, name=s[5:].strip() or s,
                                    status="passed", duration=0.0, detail=""))
        elif s[:5].upper() == "FAIL ":
            tests.append(TestResult(nodeid=s, name=s[5:].strip() or s,
                                    status="failed", duration=0.0, detail=""))
    if "TODOS OS TESTES PASSARAM" in out:
        status = "passed"
    elif "TESTES FALHARAM" in out:
        status = "failed"
    else:
        status = None
    if not tests and status:
        # teste único implícito
        tests.append(TestResult(nodeid="smoke", name="smoke", status=status,
                                duration=0.0, detail=""))
    return tests


# ---------------------------------------------------------------------------
# util
# ---------------------------------------------------------------------------
def _summarize(tests: list[TestResult], error: str) -> SuiteResult:
    total = len(tests)
    passed = sum(1 for t in tests if t.status == "passed")
    failed = sum(1 for t in tests if t.status in ("failed", "error"))
    skipped = sum(1 for t in tests if t.status == "skipped")
    return SuiteResult(ran=total > 0, total=total, passed=passed, failed=failed,
                       skipped=skipped, tests=tests, error=error)


def _parse_junit(path: str) -> list[TestResult]:
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(path)
    except (OSError, ET.ParseError):
        return []
    out = []
    for tc in tree.iter("testcase"):
        name = tc.get("name", "?")
        classname = tc.get("classname", "")
        nodeid = f"{classname}::{name}" if classname else name
        status = "passed"
        detail = ""
        fail = tc.find("failure")
        err = tc.find("error")
        skip = tc.find("skipped")
        if fail is not None:
            status = "failed"
            detail = (fail.get("message") or "")[:600]
        elif err is not None:
            status = "error"
            detail = (err.get("message") or "")[:600]
        elif skip is not None:
            status = "skipped"
            detail = (skip.get("message") or "")[:300]
        try:
            dur = float(tc.get("time", 0))
        except ValueError:
            dur = 0.0
        out.append(TestResult(nodeid=nodeid, name=name, status=status,
                              duration=dur, detail=detail))
    return out


def _parse_text(out: str) -> list[TestResult]:
    out_list = []
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("PASSED") or s.startswith("PASS"):
            status = "passed"
        elif s.startswith("FAILED") or s.startswith("FAIL"):
            status = "failed"
        elif s.startswith("SKIPPED") or s.startswith("SKIP"):
            status = "skipped"
        else:
            continue
        parts = s.split(None, 1)
        nodeid = parts[1] if len(parts) > 1 else s
        name = nodeid.split("::")[-1] or nodeid
        out_list.append(TestResult(nodeid=nodeid, name=name, status=status,
                                   duration=0.0, detail=""))
    return out_list


def suite_to_dict(s: SuiteResult) -> dict:
    return asdict(s)
