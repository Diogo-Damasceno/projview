"""Constrói o site estático do portfólio em docs/.

Pipeline do build (tudo local, offline, seguro):
  1. para cada projeto público configurado:
     - roda os testes (tester.run_tests)  -> SuiteResult
     - analisa a estrutura (analyzer.analyze) -> Analysis
     - pega o fluxo de algoritmo (algorithms_data.ALGORITHMS) -> SVG
  2. renderiza:
     - docs/index.html         (home: grade de cards)
     - docs/proj/<nome>.html   (página por projeto)
     - docs/assets/style.css
     - docs/assets/site.js
"""

from __future__ import annotations

import os
import html
import json

from projview.config import PROJECTS, local_path, repo_url
from projview import tester, analyzer
from projview.algorithms_data import ALGORITHMS
from projview.algo import render as render_svg

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs")


# --------------------------------------------------------------------------
# render de pedaços
# --------------------------------------------------------------------------

def _card(p: dict, status: dict) -> str:
    name = p["name"]
    lang = p.get("lang", "")
    cat = p.get("category", "")
    desc = p.get("desc", "")
    if status.get("ran"):
        badge = (f'<span class="badge ok">{status["passed"]}/{status["total"]} passou</span>'
                 if status["failed"] == 0 else
                 f'<span class="badge bad">{status["failed"]} falhou</span>')
    else:
        badge = '<span class="badge none">sem testes</span>'
    return f"""
    <a class="card" href="proj/{name}.html">
      <div class="card-top">
        <span class="lang">{html.escape(lang)}</span>
        <span class="cat">{html.escape(cat)}</span>
      </div>
      <h3>{html.escape(name)}</h3>
      <p>{html.escape(desc)}</p>
      <div class="card-foot">{badge}</div>
    </a>"""


def _tests_html(suite) -> str:
    if not suite.get("ran"):
        return f'<p class="muted">Este projeto não possui suíte de testes configurada ({html.escape(suite.get("error",""))}).</p>'
    rows = []
    for t in suite["tests"]:
        cls = {"passed": "pass", "failed": "fail", "error": "fail",
               "skipped": "skip"}[t["status"]]
        detail = ""
        if t["detail"]:
            detail = f'<pre class="tb">{html.escape(t["detail"])}</pre>'
        rows.append(
            f'<li class="trow {cls}"><span class="dot"></span>'
            f'<span class="tname">{html.escape(t["name"])}</span>'
            f'<span class="ttime">{t["duration"]:.2f}s</span>'
            f'<div class="tdetail">{detail}</div></li>'
        )
    summary = (f'<p class="summary"><b>{suite["total"]}</b> testes · '
               f'<span class="ok">{suite["passed"]} passou</span> · '
               f'<span class="bad">{suite["failed"]} falhou</span> · '
               f'<span class="muted">{suite["skipped"]} skip</span></p>')
    return summary + f'<ul class="tests">{"".join(rows)}</ul>'


def _analysis_html(an) -> str:
    eps = "".join(f"<li><code>{html.escape(e)}</code></li>" for e in an.entrypoints) or "<li>—</li>"
    mods = []
    for m in an.modules[:12]:
        funcs = "".join(
            f'<li><code>{html.escape(f.name)}()</code>{" — " + html.escape(f.doc) if f.doc else ""}</li>'
            for f in m.functions[:8]
        ) or "<li>—</li>"
        mods.append(f'<details><summary>{html.escape(m.path)}</summary><ul>{funcs}</ul></details>')
    tree = "".join(f"<li>{html.escape(f)}</li>" for f in an.file_tree[:30]) or "<li>—</li>"
    return f"""
    <h3>Entrypoints (CLI)</h3><ul class="eps">{eps}</ul>
    <h3>Módulos e funções principais</h3>{''.join(mods)}
    <h3>Estrutura de arquivos</h3><ul class="tree">{tree}</ul>
    """


def _algo_html(name: str) -> str:
    steps = ALGORITHMS.get(name)
    if not steps:
        return '<p class="muted">Diagrama de fluxo em breve.</p>'
    svg = render_svg(steps, title=name)
    return f'<div class="algo">{svg}</div>'


# --------------------------------------------------------------------------
# páginas
# --------------------------------------------------------------------------

def _page(title: str, body: str, active: str = "", asset_prefix: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · ProjView</title>
<link rel="stylesheet" href="{asset_prefix}assets/style.css">
</head><body>
<header class="top">
  <a class="brand" href="{asset_prefix}index.html">◈ ProjView</a>
  <nav><a href="{asset_prefix}index.html">Projetos</a></nav>
</header>
<main class="wrap">{body}</main>
<footer class="foot">Portfólio estático gerado por projview — nenhum código é executado no servidor ou no navegador.</footer>
<script src="{asset_prefix}assets/site.js"></script>
</body></html>"""


def build_site() -> None:
    os.makedirs(os.path.join(DOCS, "proj"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)

    # coleta dados
    projects = []
    for name in sorted(PROJECTS):
        p = dict(PROJECTS[name]); p["name"] = name
        p["repo"] = repo_url(name)
        path = local_path(name)
        suite = {"ran": False, "total": 0, "passed": 0, "failed": 0,
                 "skipped": 0, "tests": [], "error": "fora do disco local"}
        an = analyzer.Analysis(entrypoints=[], modules=[], readme="", file_tree=[])
        if path:
            suite = tester.suite_to_dict(tester.run_tests(path))
            an = analyzer.analyze(path)
        p["suite"] = suite
        p["analysis"] = an
        projects.append(p)

    # ordena: projetos com testes passando primeiro, depois os sem testes
    def _has_tests(p):
        s = p["suite"]
        return s.get("ran") and s.get("total", 0) > 0
    projects.sort(key=lambda p: (not _has_tests(p), p["name"]))

    # home
    cards = "\n".join(_card(p, p["suite"]) for p in projects)
    home = _page("Projetos", f"""
      <h1>Meus projetos</h1>
      <p class="lead">Clique em um projeto para ver o fluxo dos testes, como funciona e o diagrama do algoritmo. Tudo gerado estaticamente — seguro para portfólio.</p>
      <section class="grid">{cards}</section>
    """, asset_prefix="")

    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(home)

    # páginas por projeto
    for p in projects:
        an = p["analysis"]
        body = f"""
        <a class="back" href="../index.html">← todos os projetos</a>
        <div class="phead">
          <h1>{html.escape(p['name'])}</h1>
          <div class="tags"><span class="lang">{html.escape(p.get('lang',''))}</span>
          <span class="cat">{html.escape(p.get('category',''))}</span>
          <a class="repo" href="{html.escape(p['repo'])}" target="_blank" rel="noopener">GitHub ↗</a></div>
          <p class="lead">{html.escape(p.get('desc',''))}</p>
        </div>
        <div class="tabs">
          <button class="tab active" data-tab="tests">Testes</button>
          <button class="tab" data-tab="how">Como funciona</button>
          <button class="tab" data-tab="algo">Algoritmo</button>
        </div>
        <section class="pane active" id="tests">{_tests_html(p['suite'])}</section>
        <section class="pane" id="how">
          {_analysis_html(an)}
          <h3>README</h3>
          <div class="readme">{html.escape(an.readme) if an.readme else '<p class="muted">sem README</p>'}</div>
        </section>
        <section class="pane" id="algo">{_algo_html(p['name'])}</section>
        """
        page = _page(p["name"], body, active=p["name"], asset_prefix="../")
        with open(os.path.join(DOCS, "proj", f"{p['name']}.html"), "w", encoding="utf-8") as fh:
            fh.write(page)

    # assets
    _write_assets()

    # dump de dados (debug/inspeção)
    with open(os.path.join(DOCS, "build.json"), "w", encoding="utf-8") as fh:
        json.dump({p["name"]: {"suite": p["suite"], "lang": p.get("lang"),
                                "category": p.get("category")} for p in projects}, fh, indent=2)

    print(f"site gerado em {DOCS} ({len(projects)} projetos)")


def _write_assets() -> None:
    css = """
:root{--bg:#030712;--panel:#0b1f3a;--ocean:#1f6feb;--sky:#58a6ff;
--foam:#a5d6ff;--mist:#7fb0d6;--ok:#56d364;--bad:#ff7b72;--line:#1f6feb;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--foam);
font:15px/1.5 ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif}
.top{display:flex;align-items:center;justify-content:space-between;
padding:14px 22px;border-bottom:1px solid var(--line);background:#06122a}
.brand{color:var(--sky);font-weight:700;font-size:18px;text-decoration:none;letter-spacing:.5px}
nav a{color:var(--mist);text-decoration:none;margin-left:14px}
.wrap{max-width:1080px;margin:0 auto;padding:26px 18px}
.lead{color:var(--mist)}
h1{color:var(--sky);margin:.2em 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:18px}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:16px;text-decoration:none;color:var(--foam);transition:.15s;min-height:170px}
.card:hover{border-color:var(--sky);transform:translateY(-3px)}
.card-top{display:flex;justify-content:space-between;font-size:12px}
.lang{color:var(--sky)}.cat{color:var(--mist);background:#06122a;padding:1px 8px;border-radius:8px}
.card h3{margin:.5em 0 .2em;color:var(--foam)}
.card p{color:var(--mist);font-size:13px;margin:.2em 0}
.card-foot{margin-top:10px}
.badge{padding:2px 9px;border-radius:9px;font-size:12px}
.badge.ok{background:#0c2a16;color:var(--ok)}
.badge.bad{background:#2a0c10;color:var(--bad)}
.badge.none{background:#1a1a1a;color:var(--mist)}
.tags .lang,.tags .cat{padding:2px 9px;border-radius:9px;font-size:12px;margin-right:6px}
.tags .cat{background:#06122a;color:var(--mist)}.tags .lang{background:#06122a;color:var(--sky)}
.repo{color:var(--sky);text-decoration:none;float:right}
.phead{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:16px}
.tabs{display:flex;gap:8px;margin-bottom:14px}
.tab{background:#06122a;color:var(--mist);border:1px solid var(--line);
border-radius:9px;padding:8px 16px;cursor:pointer}
.tab.active{background:var(--ocean);color:#fff;border-color:var(--sky)}
.pane{display:none}.pane.active{display:block}
.tests{list-style:none;padding:0;margin:0}
.trow{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;
background:var(--panel);margin-bottom:6px;flex-wrap:wrap}
.trow .dot{width:10px;height:10px;border-radius:50%}
.trow.pass .dot{background:var(--ok)}.trow.fail .dot{background:var(--bad)}
.trow.skip .dot{background:var(--mist)}
.tname{font-family:ui-monospace,Menlo,monospace;flex:1}
.ttime{color:var(--mist);font-size:12px}
.tdetail{flex-basis:100%}
.tb{background:#030712;border:1px solid var(--line);border-radius:8px;padding:10px;
max-height:240px;overflow:auto;color:var(--mist);font-size:12px;white-space:pre-wrap}
.summary{color:var(--foam)}.ok{color:var(--ok)}.bad{color:var(--bad)}.muted{color:var(--mist)}
details{margin:4px 0;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
summary{cursor:pointer;color:var(--sky)}
.eps,.tree,.tree li{list-style:square;color:var(--mist)}
.algo{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}
.flow .box{fill:#0b1f3a;stroke:var(--line);stroke-width:1.6}
.flow .dia{fill:#06122a;stroke:var(--sky);stroke-width:1.6}
.flow .oval{fill:#06122a;stroke:var(--ok);stroke-width:1.6}
.flow .oval.end{stroke:var(--bad)}
.flow .para{fill:#0b1f3a;stroke:var(--mist);stroke-width:1.6}
.flow .lbl{fill:var(--foam);font:13px ui-sans-serif;dominant-baseline:middle;text-anchor:middle}
.flow .flow-title{fill:var(--sky);font:14px ui-sans-serif;text-anchor:middle;font-weight:700}
.flow .edge-lbl{font:11px ui-sans-serif;text-anchor:middle}
.readme{background:#030712;border:1px solid var(--line);border-radius:8px;padding:14px;
color:var(--mist);white-space:pre-wrap;font-size:13px;max-height:420px;overflow:auto}
.back{color:var(--mist);text-decoration:none}
.foot{padding:20px;text-align:center;color:var(--mist);font-size:12px;border-top:1px solid var(--line);margin-top:30px}
"""
    with open(os.path.join(DOCS, "assets", "style.css"), "w", encoding="utf-8") as fh:
        fh.write(css)
    js = """
document.querySelectorAll('.tab').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.pane').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    document.getElementById(b.dataset.tab).classList.add('active');
  };
});
"""
    with open(os.path.join(DOCS, "assets", "site.js"), "w", encoding="utf-8") as fh:
        fh.write(js)
