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
from projview.examples_data import EXAMPLES
from projview.about_data import ABOUT
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


def _examples_html(name: str) -> str:
    exs = EXAMPLES.get(name)
    if not exs:
        return '<p class="muted">Exemplo em breve.</p>'
    blocks = []
    for cmd, out in exs:
        blocks.append(f"""
        <div class="ex">
          <div class="ex-cmd"><span class="prompt">$ </span>{html.escape(cmd)}</div>
          <div class="ex-out"><pre>{html.escape(out)}</pre></div>
        </div>""")
    return '<p class="lead">Como rodar na prática (entrada → saída):</p>' + "".join(blocks)


def _hero_html() -> str:
    name = html.escape(ABOUT["name"])
    tag = html.escape(ABOUT["tagline"])
    socials = "".join(
        f'<a class="social" href="{html.escape(u)}" target="_blank" rel="noopener">'
        f'<span class="social-ic">{html.escape(ic)}</span>{html.escape(lbl)}</a>'
        for ic, lbl, u in ABOUT["socials"]
    )
    return f"""
    <header class="hero">
      <div class="hero-glow"></div>
      <p class="hero-kicker">// portfólio de segurança &amp; código</p>
      <h1 class="hero-name">{name}</h1>
      <p class="hero-tag">{tag}</p>
      <div class="hero-socials">{socials}</div>
    </header>"""


def _about_html() -> str:
    bio = "".join(f"<p>{html.escape(b)}</p>" for b in ABOUT["bio"])
    facts = "".join(
        f'<li><span class="fact-ic">{ic}</span><span class="fact-tx">{html.escape(tx)}</span></li>'
        for ic, tx in ABOUT["facts"]
    )
    return f"""
    <section class="about">
      <div class="about-bio">{bio}</div>
      <ul class="facts">{facts}</ul>
    </section>"""


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
    about = _about_html()
    home = _page("Projetos", f"""
      {_hero_html()}
      {about}
      <h2 class="sec-title">Projetos</h2>
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
          <button class="tab" data-tab="example">Exemplo</button>
        </div>
        <section class="pane active" id="tests">{_tests_html(p['suite'])}</section>
        <section class="pane" id="how">
          {_analysis_html(an)}
          <h3>README</h3>
          <div class="readme">{html.escape(an.readme) if an.readme else '<p class="muted">sem README</p>'}</div>
        </section>
        <section class="pane" id="algo">{_algo_html(p['name'])}</section>
        <section class="pane" id="example">{_examples_html(p['name'])}</section>
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
:root{--bg:#05060a;--panel:#0b1320;--panel2:#0e1a2e;--ocean:#1f6feb;--sky:#58a6ff;
--foam:#dbeafe;--mist:#7fb0d6;--ok:#56d364;--bad:#ff7b72;--line:#1f3a5f;
--accent:#22d3ee;--accent2:#7c3aed}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--foam);
font:16px/1.6 ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif;
background-image:radial-gradient(1200px 600px at 80% -10%, rgba(34,211,238,.08), transparent 60%),
radial-gradient(900px 500px at 0% 0%, rgba(124,58,237,.08), transparent 55%);}
.top{display:flex;align-items:center;justify-content:space-between;
padding:16px 26px;border-bottom:1px solid var(--line);
backdrop-filter:blur(8px);position:sticky;top:0;z-index:10;
background:rgba(5,6,10,.7)}
.brand{color:var(--sky);font-weight:700;font-size:19px;text-decoration:none;letter-spacing:.5px}
.brand:hover{color:var(--accent)}
nav a{color:var(--mist);text-decoration:none;margin-left:16px;transition:.15s}
nav a:hover{color:var(--foam)}
.wrap{max-width:1080px;margin:0 auto;padding:34px 20px}

/* ---------- HERO ---------- */
.hero{position:relative;text-align:center;padding:70px 16px 50px;overflow:hidden}
.hero-glow{position:absolute;inset:-20% 0 auto 0;height:340px;margin:auto;
width:680px;max-width:90%;border-radius:50%;
background:conic-gradient(from 0deg,var(--accent),var(--ocean),var(--accent2),var(--accent));
filter:blur(90px);opacity:.28;animation:spin 14s linear infinite;z-index:0}
@keyframes spin{to{transform:rotate(360deg)}}
.hero-kicker{position:relative;z-index:1;color:var(--accent);font-family:ui-monospace,Menlo,monospace;
font-size:13px;letter-spacing:2px;margin:0 0 14px;text-transform:uppercase}
.hero-name{position:relative;z-index:1;margin:0;font-size:clamp(2.4rem,7vw,4.2rem);
font-weight:800;letter-spacing:-1px;line-height:1.05;
background:linear-gradient(100deg,var(--foam),var(--sky) 45%,var(--accent));
-webkit-background-clip:text;background-clip:text;color:transparent;
animation:fadeUp .7s ease both}
.hero-tag{position:relative;z-index:1;max-width:680px;margin:18px auto 0;
color:var(--mist);font-size:clamp(1rem,2.4vw,1.2rem)}
.hero-socials{position:relative;z-index:1;margin-top:26px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.social{display:inline-flex;align-items:center;gap:9px;padding:11px 22px;border-radius:12px;
color:var(--foam);text-decoration:none;font-size:15px;font-weight:600;transition:.18s;
background:linear-gradient(120deg,var(--panel2),var(--panel));
border:1px solid var(--line);box-shadow:0 4px 14px rgba(0,0,0,.3)}
.social-ic{font-size:18px;line-height:1}
.social:hover{border-color:transparent;color:#fff;transform:translateY(-3px);
background:linear-gradient(120deg,var(--ocean),var(--accent));
box-shadow:0 12px 30px rgba(34,211,238,.28)}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

/* ---------- SOBRE ---------- */
.about{display:grid;grid-template-columns:1.4fr 1fr;gap:26px;align-items:start;
margin:10px 0 46px;padding:26px;border:1px solid var(--line);border-radius:16px;
background:linear-gradient(180deg,var(--panel),var(--panel2));
animation:fadeUp .8s ease both}
.about-bio p{margin:0 0 12px;color:var(--foam)}
.about-bio p:last-child{margin-bottom:0}
.facts{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.facts li{display:flex;align-items:center;gap:12px;background:var(--bg);
border:1px solid var(--line);border-radius:12px;padding:10px 14px;transition:.15s}
.facts li:hover{border-color:var(--sky);transform:translateX(4px)}
.fact-ic{font-size:20px}
.fact-tx{color:var(--mist);font-size:14px}

.sec-title{color:var(--sky);font-size:1.6rem;margin:30px 0 6px;
position:relative;padding-left:14px}
.sec-title::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:4px;
border-radius:4px;background:linear-gradient(var(--accent),var(--ocean))}
.lead{color:var(--mist)}

/* ---------- GRID DE CARDS ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px;margin-top:18px}
.card{display:block;background:linear-gradient(180deg,var(--panel),var(--panel2));
border:1px solid var(--line);border-radius:14px;padding:18px;text-decoration:none;
color:var(--foam);transition:.2s;min-height:172px;position:relative;overflow:hidden}
.card::after{content:"";position:absolute;inset:0;border-radius:14px;padding:1px;
background:linear-gradient(135deg,transparent,var(--accent),transparent);
-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
-webkit-mask-composite:xor;mask-composite:exclude;opacity:0;transition:.2s}
.card:hover{transform:translateY(-5px);box-shadow:0 16px 40px rgba(31,111,235,.18)}
.card:hover::after{opacity:1}
.card-top{display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px}
.lang{color:var(--sky)}.cat{color:var(--mist);background:var(--bg);padding:1px 8px;border-radius:8px}
.card h3{margin:.4em 0 .25em;color:var(--foam);font-size:1.15rem}
.card p{color:var(--mist);font-size:13px;margin:.2em 0}
.card-foot{margin-top:12px}
.badge{padding:2px 9px;border-radius:9px;font-size:12px}
.badge.ok{background:#0c2a16;color:var(--ok)}
.badge.bad{background:#2a0c10;color:var(--bad)}
.badge.none{background:#1a1a1a;color:var(--mist)}

/* ---------- PÁGINA DE PROJETO ---------- */
.tags .lang,.tags .cat{padding:2px 9px;border-radius:9px;font-size:12px;margin-right:6px}
.tags .cat{background:var(--bg);color:var(--mist)}.tags .lang{background:var(--bg);color:var(--sky)}
.repo{color:var(--sky);text-decoration:none;float:right}
.phead{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:16px}
.tabs{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.tab{background:var(--panel);color:var(--mist);border:1px solid var(--line);
border-radius:9px;padding:9px 18px;cursor:pointer;transition:.15s}
.tab:hover{color:var(--foam)}
.tab.active{background:linear-gradient(120deg,var(--ocean),var(--accent));color:#fff;border-color:transparent}
.pane{display:none;animation:fadeUp .35s ease both}.pane.active{display:block}
.tests{list-style:none;padding:0;margin:0}
.trow{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;
background:var(--panel);margin-bottom:6px;flex-wrap:wrap;transition:.15s}
.trow:hover{background:var(--panel2)}
.trow .dot{width:10px;height:10px;border-radius:50%}
.trow.pass .dot{background:var(--ok)}.trow.fail .dot{background:var(--bad)}
.trow.skip .dot{background:var(--mist)}
.tname{font-family:ui-monospace,Menlo,monospace;flex:1}
.ttime{color:var(--mist);font-size:12px}
.tdetail{flex-basis:100%}
.tb{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px;
max-height:240px;overflow:auto;color:var(--mist);font-size:12px;white-space:pre-wrap}
.summary{color:var(--foam)}.ok{color:var(--ok)}.bad{color:var(--bad)}.muted{color:var(--mist)}
details{margin:4px 0;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
summary{cursor:pointer;color:var(--sky)}
.eps,.tree,.tree li{list-style:square;color:var(--mist)}
.algo{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.flow .box{fill:#0b1f3a;stroke:var(--line);stroke-width:1.6}
.flow .dia{fill:#06122a;stroke:var(--sky);stroke-width:1.6}
.flow .oval{fill:#06122a;stroke:var(--ok);stroke-width:1.6}
.flow .oval.end{stroke:var(--bad)}
.flow .para{fill:#0b1f3a;stroke:var(--mist);stroke-width:1.6}
.flow .lbl{fill:var(--foam);font:13px ui-sans-serif;dominant-baseline:middle;text-anchor:middle}
.flow .flow-title{fill:var(--sky);font:14px ui-sans-serif;text-anchor:middle;font-weight:700}
.flow .edge-lbl{font:11px ui-sans-serif;text-anchor:middle;font-weight:700}
.readme{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:14px;
color:var(--mist);white-space:pre-wrap;font-size:13px;max-height:420px;overflow:auto}
.back{color:var(--mist);text-decoration:none}.back:hover{color:var(--accent)}
.ex{background:var(--bg);border:1px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden;
transition:.15s}.ex:hover{border-color:var(--sky)}
.ex-cmd{background:var(--panel2);padding:9px 13px;color:var(--sky);font-family:ui-monospace,Menlo,monospace;font-size:13px;border-bottom:1px solid var(--line)}
.ex-cmd .prompt{color:var(--ok)}
.ex-out{padding:11px 13px}
.ex-out pre{margin:0;color:var(--foam);font-family:ui-monospace,Menlo,monospace;font-size:12.5px;white-space:pre-wrap;line-height:1.45}
.foot{padding:26px 20px;text-align:center;color:var(--mist);font-size:12px;border-top:1px solid var(--line);margin-top:40px}

/* SVG do algoritmo fluido */
.algo .flow{width:100%;height:auto;max-width:100%;display:block;margin:0 auto}

/* ---------- responsivo: tablet ---------- */
@media (max-width:880px){
  .wrap{padding:26px 16px}
  .about{grid-template-columns:1fr;gap:18px}
  .grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}
  .card{min-height:150px;padding:15px}
  .tabs{flex-wrap:wrap}.tab{padding:8px 14px;font-size:13px}
}
/* ---------- responsivo: celular ---------- */
@media (max-width:560px){
  .top{padding:12px 14px;flex-wrap:wrap;gap:6px}
  .brand{font-size:16px}
  .wrap{padding:18px 13px}
  .hero{padding:48px 10px 34px}
  .lead{font-size:14px}
  .grid{grid-template-columns:1fr}
  .card{min-height:0;padding:15px}
  h1{font-size:1.3rem}
  .phead .tags .lang,.phead .tags .cat{font-size:11px}
  .readme,.tb,.ex-out pre{font-size:12px}
  .trow{flex-wrap:wrap}.ttime{flex-basis:100%}
  .foot{font-size:11px;padding:18px 10px}
}
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
