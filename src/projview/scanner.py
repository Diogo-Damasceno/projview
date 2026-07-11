"""Scanner: lista os projetos configurados e o que cada um possui.

Usado por `projview scan`. Não roda testes — só inspeciona a estrutura
(localmente, offline) para o dono saber o que vai entrar no portfólio.
"""

from __future__ import annotations

import os

from projview.config import PROJECTS, local_path, repo_url


def _inspect(name: str) -> dict:
    info = dict(PROJECTS.get(name, {}))
    path = local_path(name)
    info["local"] = path
    info["repo"] = repo_url(name)
    if not path:
        info["has_tests"] = None
        info["has_readme"] = None
        return info
    # tem suíte de testes?
    tests_dir = (
        _find(path, "tests") or _find(path, "test") or _has_pytest_ini(path)
    )
    info["has_tests"] = bool(tests_dir) or _has_pytest_ini(path)
    info["has_readme"] = os.path.isfile(os.path.join(path, "README.md"))
    return info


def _find(root: str, dirname: str) -> str | None:
    import os
    for cur, dirs, _ in os.walk(root):
        if dirname in dirs:
            return os.path.join(cur, dirname)
    return None


def _has_pytest_ini(root: str) -> bool:
    import os
    for f in ("pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"):
        p = os.path.join(root, f)
        if os.path.isfile(p):
            try:
                if "pytest" in open(p, encoding="utf-8", errors="ignore").read():
                    return True
            except OSError:
                pass
    return False


def scan_projects() -> list[dict]:
    rows = []
    for name in sorted(PROJECTS):
        info = _inspect(name)
        info["name"] = name
        rows.append(info)
    return rows


def main() -> None:
    rows = scan_projects()
    print(f"{'projeto':24} {'lang':7} {'cat':12} {'local?':7} {'tests?':7} repo")
    for r in rows:
        local = "sim" if r.get("local") else "nao"
        tests = {True: "sim", False: "nao", None: "?"}[r.get("has_tests")]
        print(f"{r['name']:24} {r.get('lang',''):7} {r.get('category',''):12} {local:7} {tests:7} {r['repo']}")


if __name__ == "__main__":
    main()
