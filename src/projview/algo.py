"""Motor de fluxograma em SVG (estático, offline).

Recebe uma lista de passos e desenha um fluxograma vertical legível, com
setas connvetadas saindo de cada nó e entrando no topo do próximo:

  - start / end : elipse
  - process     : retângulo
  - decision    : losango (bifurca em S / N)
  - io          : paralelograma

Cada passo: {id, type, label, next (process/start/end/io), yes/no (decision)}.

Gera SVG puro, sem dependências — seguro para o portfólio (o visitante só
vê a imagem, nada executa).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Step:
    id: str
    type: str           # start | process | decision | io | end
    label: str
    next: str | None = None        # para process/start/end/io
    yes: str | None = None         # para decision
    no: str | None = None          # para decision


# geometria
W = 260
ROW = 76
PAD = 28
NH = ROW - 18          # altura do nó

_COLORS = {"next": "#58a6ff", "yes": "#56d364", "no": "#ff7b72"}


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(steps: list[Step], title: str = "") -> str:
    steps_by_id = {s.id: s for s in steps}
    n = len(steps)
    header = 26 if title else 0
    height = PAD * 2 + header + n * ROW
    width = W + PAD * 2
    mid = PAD + W / 2

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'class="flow" role="img" aria-label="{_esc(title)}">']
    # defs: 3 markers de seta (um por cor), definidos UMA vez
    svg.append('<defs>')
    for kind, col in _COLORS.items():
        svg.append(f'<marker id="arw-{kind}" markerWidth="9" markerHeight="9" refX="6" '
                   f'refY="3" orient="auto" markerUnits="userSpaceOnUse">'
                   f'<path d="M0,0 L6,3 L0,6 Z" fill="{col}"/></marker>')
    svg.append('</defs>')
    if title:
        svg.append(f'<text x="{width/2:.0f}" y="18" class="flow-title">{_esc(title)}</text>')

    y0 = PAD + header
    pos = {s.id: y0 + i * ROW for i, s in enumerate(steps)}
    cy = lambda sid: pos[sid] + NH / 2          # centro vertical do nó
    bottom = lambda sid: pos[sid] + NH         # base do nó
    top = lambda sid: pos[sid]                 # topo do nó

    # ---- arestas (atrás dos nós) ----
    def edge(x1, y1, x2, y2, kind, label=None):
        col = _COLORS[kind]
        d = (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
             f'stroke="{col}" stroke-width="1.8" marker-end="url(#arw-{kind})"/>')
        if label:
            # rótulo perto da origem da bifurcação
            lx = x2 + (14 if kind == "yes" else -14) if x2 != x1 else (x1 + 8)
            ly = (y1 + y2) / 2
            d += f'<text x="{lx:.0f}" y="{ly:.0f}" class="edge-lbl" fill="{col}">{label}</text>'
        return d

    for s in steps:
        if s.type == "decision":
            if s.yes:
                t = s.yes
                # sai pela direita, entra no topo do alvo (ou sobe se alvo acima)
                svg.append(edge(mid + W/2, cy(s.id), mid + W/2, cy(t), "yes", "S"))
                svg.append(edge(mid + W/2, cy(t), mid, top(t), "yes"))
            if s.no:
                t = s.no
                svg.append(edge(mid - W/2, cy(s.id), mid - W/2, cy(t), "no", "N"))
                svg.append(edge(mid - W/2, cy(t), mid, top(t), "no"))
        elif s.next:
            t = s.next
            svg.append(edge(mid, bottom(s.id), mid, top(t), "next"))

    # ---- nós ----
    for s in steps:
        y = pos[s.id]
        c = mid
        cyy = cy(s.id)
        if s.type == "process":
            svg.append(f'<g class="node"><rect x="{PAD}" y="{y}" width="{W}" height="{NH}" '
                       f'rx="9" class="box"/><text x="{c}" y="{cyy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "decision":
            pts = f"{c},{y} {PAD+W},{cyy} {c},{y+NH} {PAD},{cyy}"
            svg.append(f'<g class="node"><polygon points="{pts}" class="dia"/>'
                       f'<text x="{c}" y="{cyy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type in ("start", "end"):
            svg.append(f'<g class="node"><ellipse cx="{c}" cy="{cyy}" rx="{W/2}" ry="{NH/2}" '
                       f'class="oval{" end" if s.type=="end" else ""}"/>'
                       f'<text x="{c}" y="{cyy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "io":
            svg.append(f'<g class="node"><polygon points="{PAD+20},{y} {PAD+W},{y} '
                       f'{PAD+W-20},{y+NH} {PAD},{y+NH}" class="para"/>'
                       f'<text x="{c}" y="{cyy}" class="lbl">{_esc(s.label)}</text></g>')

    svg.append("</svg>")
    return "\n".join(svg)
