"""Executa os testes de um projeto com segurança, na máquina do dono.

Roda `pytest` em subprocess com:
  - timeout (não trava o build)
  - sem acesso de rede forçado (best-effort: desliga env de proxy e usa
    --disable-warnings; projetos que precisam de rede simplesmente falham
    e viram "falhou no build", sem risco pro visitante)
  - saída capturada e parseada em lista de testes (nome, status, tempo)

NUNCA é executado no site — só no momento do build, localmente.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import json
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


def run_tests(project_path: str, timeout: int = 120) -> SuiteResult:
    """Roda pytest em project_path e devolve SuiteResult.

    Se não houver suíte de testes, retorna ran=False.
    """
    # confirma que tem pytest configurado
    if not _has_pytest(project_path):
        return SuiteResult(ran=False, total=0, passed=0, failed=0, skipped=0, tests=[],
                           error="sem suíte de testes (pytest não configurado)")

    env = dict(os.environ)
    env.pop("HTTP_PROXY", None)
    env.pop("HTTPS_PROXY", None)
    env.pop("http_proxy", None)
    env.pop("https_proxy", None)

    # usa o python do venv do próprio projeto (onde pytest está instalado),
    # caindo pro python3 do sistema se não houver venv
    py = os.path.join(project_path, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = "python3"

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
            # fallback: parseia a saída textual
            tests = _parse_text(proc.stdout + proc.stderr)
        total = len(tests)
        passed = sum(1 for t in tests if t.status == "passed")
        failed = sum(1 for t in tests if t.status in ("failed", "error"))
        skipped = sum(1 for t in tests if t.status == "skipped")
        return SuiteResult(ran=True, total=total, passed=passed, failed=failed,
                           skipped=skipped, tests=tests)


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
    # procura arquivos test_*.py
    for cur, _, files in os.walk(project_path):
        for fn in files:
            if fn.startswith("test_") and fn.endswith(".py"):
                return True
    return False


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
        # formato: PASSED tests/foo.py::test_bar
        parts = s.split(None, 1)
        nodeid = parts[1] if len(parts) > 1 else s
        name = nodeid.split("::")[-1] or nodeid
        out_list.append(TestResult(nodeid=nodeid, name=name, status=status,
                                   duration=0.0, detail=""))
    return out_list


def suite_to_dict(s: SuiteResult) -> dict:
    return asdict(s)
