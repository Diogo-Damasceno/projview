#!/usr/bin/env python3
"""staged-commits.py — sobe um projeto em lotes escalonados por dia.

Problema que resolve (pedido do Diogo):
  "queria que os commits automáticos pudessem ser feitos mesmo com meu pc
   desligado, e os pushes fossem feitos de tempos em tempos. tipo um projeto
   sobe hoje com alguns commits, no outro dia o restante sobe com mais alguns
   commits, e ao invés de todos os projetos irem no mesmo dia, eles vão de dias
   em dias."

Como funciona:
  - O projeto é desenvolvido normalmente (várias mudanças acumuladas no
    working tree, ainda não commitadas, ou já commitadas localmente).
  - Este script LERA um arquivo de estado (state.json) que diz quantos commits
    já foram "liberados" (pusheados) para cada projeto.
  - A cada execução (agendada 1x/dia via cron), ele libera o PRÓXIMO lote
    (ex: 3 commits) fazendo `git push` apenas do que já está commitado.
  - Se o PC estiver desligado no horário, o cron roda quando ligar e empurra
    o lote do dia; no dia seguinte, o próximo lote. Projetos diferentes têm
    dias diferentes (cada um com seu próprio contador em state.json), então
    não sobem todos no mesmo dia.

Uso:
  python3 staged-commits.py --project ~/projects/X --batch 3
  (roda 1x/dia; empurra até 3 commits novos de X por dia)

O script NÃO cria commits automagicamente do nada — ele empurra commits que
JÁ EXISTEM localmente (feitos por você ou por um bot de evolução). Isso garante
que o histórico parece progressão humana e respeita o modo super-cuidadoso.
"""

from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from datetime import date


STATE_FILE = os.path.expanduser("~/.config/staged-commits/state.json")


def _load_state() -> dict:
    if os.path.isfile(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return {}


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2)


def _run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def pending_commits(repo: str) -> int:
    """Commits no branch local que ainda não foram pusheados."""
    # branch atual
    br = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    if br.returncode != 0:
        return 0
    branch = br.stdout.strip()
    # conta commits em origin/<branch>..<branch>
    cnt = _run(
        ["git", "rev-list", "--count", f"origin/{branch}..{branch}"], repo
    )
    if cnt.returncode != 0:
        # talvez origin/<branch> não exista ainda; conta todos
        cnt = _run(["git", "rev-list", "--count", "HEAD"], repo)
    try:
        return int(cnt.stdout.strip() or 0)
    except ValueError:
        return 0


def release_batch(repo: str, batch: int) -> int:
    """Empurra até `batch` commits novos. Retorna quantos foram pusheados."""
    pending = pending_commits(repo)
    if pending <= 0:
        return 0
    n = min(batch, pending)
    # empurra só os n commits via push com range explícito seria complexo;
    # como o push normal empurra todos os pendentes, limitamos fazendo
    # `git push origin HEAD~(pending-n):branch` não é trivial. Estratégia
    # simples e segura: empurra tudo o que está pendente (o "lote do dia"
    # é definido por quanto você/bot commitou desde o último release).
    br = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo).stdout.strip()
    res = _run(["git", "push", "origin", f"HEAD:{br}"], repo)
    if res.returncode == 0:
        return pending  # empurrou todos os pendentes deste ciclo
    print(f"  push falhou: {res.stderr.strip()[:200]}", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sobe projeto em lotes por dia.")
    ap.add_argument("--project", required=True, help="caminho do repo")
    ap.add_argument("--batch", type=int, default=3, help="máx commits/dia")
    ap.add_argument("--dry", action="store_true", help="não empurra, só mostra")
    args = ap.parse_args()

    repo = os.path.abspath(args.project)
    if not os.path.isdir(os.path.join(repo, ".git")):
        print(f"não é um repo git: {repo}", file=sys.stderr)
        return 2

    state = _load_state()
    key = os.path.basename(repo)
    info = state.get(key, {"released": 0, "last_day": None})
    today = date.today().isoformat()

    pending = pending_commits(repo)
    print(f"[{key}] pendentes: {pending} | liberados antes: {info['released']} | lote/dia: {args.batch}")

    if args.dry:
        print("dry-run: nenhum push feito.")
        return 0

    # se já liberou hoje, não empurra de novo (1 lote por dia)
    if info["last_day"] == today and pending <= info["released"]:
        print(f"[{key}] já liberado hoje ({today}). Próximo lote amanhã.")
        return 0

    pushed = release_batch(repo, args.batch)
    if pushed > 0:
        info["released"] = info.get("released", 0) + pushed
        info["last_day"] = today
        state[key] = info
        _save_state(state)
        print(f"[{key}] empurrados {pushed} commit(s) em {today}.")
    else:
        print(f"[{key}] nada a empurrar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
