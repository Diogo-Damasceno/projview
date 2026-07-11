"""Análise estática de um projeto para o portfólio.

Extrai (offline, lendo o disco):
  - entrypoints do pyproject (comando do CLI)
  - módulos e funções públicas com suas docstrings
  - o README (primeiros parágrafos já cobrem a descrição)
  - árvore de arquivos relevante

Tudo usado para montar a aba "Como funciona" do site, sem executar nada.
"""

from __future__ import annotations

import os
import ast
import re
from dataclasses import dataclass, field


@dataclass
class FuncInfo:
    name: str
    doc: str
    is_entry: bool = False


@dataclass
class ModuleInfo:
    path: str          # relativo ao projeto
    functions: list[FuncInfo] = field(default_factory=list)
    doc: str = ""


@dataclass
class Analysis:
    entrypoints: list[str]
    modules: list[ModuleInfo]
    readme: str
    file_tree: list[str]


def analyze(project_path: str) -> Analysis:
    entrypoints = _entrypoints(project_path)
    modules = _modules(project_path)
    readme = _readme(project_path)
    tree = _tree(project_path)
    return Analysis(entrypoints=entrypoints, modules=modules,
                    readme=readme, file_tree=tree)


def _entrypoints(project_path: str) -> list[str]:
    p = os.path.join(project_path, "pyproject.toml")
    if not os.path.isfile(p):
        return []
    txt = open(p, encoding="utf-8", errors="ignore").read()
    eps = re.findall(r'\[project\.scripts\](.*?)(\[|\Z)', txt, re.S)
    if not eps:
        return []
    block = eps[0][0]
    cmds = re.findall(r'(\w[\w\-]*)\s*=\s*"', block)
    return cmds


def _modules(project_path: str) -> list[ModuleInfo]:
    out = []
    for cur, dirs, files in os.walk(project_path):
        # pula venv / build / cache
        dirs[:] = [d for d in dirs if d not in (".venv", "venv", "build",
                   "dist", "__pycache__", ".git", "node_modules", "target")]
        for fn in files:
            if not fn.endswith(".py") or fn.startswith("test_"):
                continue
            full = os.path.join(cur, fn)
            rel = os.path.relpath(full, project_path)
            mod = _parse_module(full, rel)
            if mod.functions or mod.doc:
                out.append(mod)
    out.sort(key=lambda m: m.path)
    return out[:40]  # limita para não inflar o site


def _parse_module(full: str, rel: str) -> ModuleInfo:
    try:
        src = open(full, encoding="utf-8", errors="ignore").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return ModuleInfo(path=rel)
    mod = ModuleInfo(path=rel, doc=_doc(tree))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            mod.functions.append(FuncInfo(name=node.name, doc=_doc(node)))
    return mod


def _doc(node) -> str:
    if not (d := ast.get_docstring(node)):
        return ""
    return d.strip().split("\n\n")[0][:240]


def _readme(project_path: str) -> str:
    p = os.path.join(project_path, "README.md")
    if not os.path.isfile(p):
        return ""
    return open(p, encoding="utf-8", errors="ignore").read()[:4000]


def _tree(project_path: str, max_depth: int = 2) -> list[str]:
    lines = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in (".venv", "venv", "build",
                   "dist", "__pycache__", ".git", "node_modules", "target", ".pytest_cache")]
        depth = root[len(project_path):].count(os.sep)
        if depth > max_depth:
            dirs[:] = []
            continue
        for fn in sorted(files):
            if fn.startswith("."):
                continue
            lines.append(os.path.relpath(os.path.join(root, fn), project_path))
    return sorted(lines)[:60]
