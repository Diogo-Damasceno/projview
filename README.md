# projview

> ## 🌐 SITE DO PORTFÓLIO: https://diogo-damasceno.github.io/projview/
> Clique e veja todos os meus projetos com testes, explicação e diagrama de algoritmo.
>
> [![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-ver%20site-blue?style=for-the-badge)](https://diogo-damasceno.github.io/projview/)

Gerador de **portfólio estático** para os meus projetos de cibersegurança e DevOps.

Ele roda os testes de cada projeto **localmente** (na minha máquina, no
momento do build), analisa a estrutura do código e gera um **site HTML/CSS/SVG
puro** — sem backend, sem JavaScript pesado, sem build de framework.

O visitante do portfólio **só consome conteúdo**: nada é executado no servidor
nem no navegador. Por isso é seguro publicar no GitHub Pages.

## O que o site mostra

- **Home**: grade de cards, um por projeto (linguagem, categoria, descrição e
  badge de status dos testes).
- **Página do projeto** (3 abas):
  - **Testes**: fluxo visual dos testes (verde/vermelho/amarelo), tempo e
    traceback expansível.
  - **Como funciona**: entrypoints (CLI), módulos e funções principais,
    estrutura de arquivos e o README.
  - **Algoritmo**: diagrama de fluxo em SVG do funcionamento da ferramenta.

## Uso

```bash
git clone https://github.com/Diogo-Damasceno/projview.git
cd projview
python3 -m venv .venv && . .venv/bin/activate
pip install -e .

projview scan     # lista os projetos e o que cada um tem
projview build    # gera o site em docs/
```

O `docs/` resultante é o que o GitHub Pages publica (source = `/docs`).

## Segurança

- Os testes rodam **apenas no build local**, nunca no servidor público.
- Projetos que fazem varredura de rede/honeypot são documentados de forma
  estática — o visitante não dispara nenhuma ação.
- Sem dependências de execução no navegador: só HTML, CSS e SVG.

## Requisitos

- Python 3.10+
- Os projetos alvo devem estar no disco (em `~/projects/...`) para o build
  rodar os testes; caso contrário, a página mostra "sem testes" e mesmo assim
  exibe estrutura + algoritmo.

## Licença

MIT — veja `LICENSE`.
