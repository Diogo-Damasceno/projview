"""Motor de fluxograma em SVG (estático, offline).

Recebe uma lista de passos e desenha um fluxograma vertical:
  - start / end : elipse
  - process     : retângulo
  - decision    : losango
  - io          : paralelograma

Cada passo: {"id", "type", "label", "next" (id ou lista p/ decisão)}

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
W = 240
ROW = 70
PAD = 30
H_HEADER = 0


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render(steps: list[Step], title: str = "") -> str:
    steps_by_id = {s.id: s for s in steps}
    n = len(steps)
    height = PAD * 2 + n * ROW + (len(title) > 0) * 24
    width = W + PAD * 2

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'class="flow" role="img" aria-label="{_esc(title)}">']
    if title:
        svg.append(f'<text x="{width//2}" y="18" class="flow-title">{_esc(title)}</text>')
    y0 = PAD + (24 if title else 0)

    pos = {}
    for i, s in enumerate(steps):
        pos[s.id] = y0 + i * ROW

    # arestas primeiro (atrás)
    for s in steps:
        y = pos[s.id]
        cy = y + ROW / 2
        targets = []
        if s.type == "decision":
            if s.yes: targets.append((s.yes, "S", 1))
            if s.no: targets.append((s.no, "N", -1))
        elif s.next:
            targets.append((s.next, None, 0))
        for tid, label, side in targets:
            ty = pos.get(tid, cy)
            tcy = ty + ROW / 2
            x = width // 2
            # saída pela base ou lados
            if label == "S":
                x2 = x + 60
                svg.append(_edge(x + W/2 - W/2 + W, cy, x2, tcy, label, "yes"))
            elif label == "N":
                x2 = x - 60
                svg.append(_edge(x - W/2 + W/2 - W, cy, x2, tcy, label, "no"))
            else:
                svg.append(_edge(x, cy + ROW/2, x, tcy - ROW/2, None, "next"))

    # nós
    for s in steps:
        y = pos[s.id]
        cy = y + ROW / 2
        x = PAD
        if s.type == "process":
            svg.append(f'<g class="node"><rect x="{x}" y="{y}" width="{W}" height="{ROW-14}" '
                       f'rx="8" class="box"/><text x="{x+W/2}" y="{cy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "decision":
            pts = f"{x+W/2},{y} {x+W},{cy} {x+W/2},{y+ROW-14} {x},{cy}"
            svg.append(f'<g class="node"><polygon points="{pts}" class="dia"/><text x="{x+W/2}" y="{cy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "start":
            svg.append(f'<g class="node"><ellipse cx="{x+W/2}" cy="{cy}" rx="{W/2}" ry="{ROW/2-7}" class="oval"/><text x="{x+W/2}" y="{cy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "end":
            svg.append(f'<g class="node"><ellipse cx="{x+W/2}" cy="{cy}" rx="{W/2}" ry="{ROW/2-7}" class="oval end"/><text x="{x+W/2}" y="{cy}" class="lbl">{_esc(s.label)}</text></g>')
        elif s.type == "io":
            svg.append(f'<g class="node"><polygon points="{x+18},{y} {x+W},{y} {x+W-18},{y+ROW-14} {x},{y+ROW-14}" class="para"/><text x="{x+W/2}" y="{cy}" class="lbl">{_esc(s.label)}</text></g>')

    svg.append("</svg>")
    return "\n".join(svg)


def _edge(x1, y1, x2, y2, label, kind):
    color = "#56d364" if kind == "yes" else "#ff7b72" if kind == "no" else "#58a6ff"
    arrow = f'<marker id="a{id(label)}{kind}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{color}"/></marker>'
    # marcadores únicos simples
    svg = (f'<defs>{arrow}</defs>'
           f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
           f'stroke="{color}" stroke-width="1.6" marker-end="url(#a{id(label)}{kind})"/>')
    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        svg += f'<text x="{mx:.0f}" y="{my:.0f}" class="edge-lbl" fill="{color}">{label}</text>'
    return svg
