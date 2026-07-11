"""Configuração dos projetos do portfólio.

Cada entrada aponta para um repositório PÚBLICO do Diogo e, quando disponível,
o caminho local onde o código vive (para o build rodar os testes e ler o
código de forma segura, offline, na máquina dele).

Nenhum desses projetos é executado no site: o build roda localmente e gera
HTML/CSS/SVG estático. O visitante do portfólio só consome conteúdo.
"""

from __future__ import annotations

import os

# Locais prováveis onde os projetos podem estar no disco.
_LOCAL_ROOTS = [
    "/home/diogo/projects/security",
    "/home/diogo/projects/tools",
    "/home/diogo/projects/ai",
    "/tmp/repos",
]

# Nome no GitHub -> metadados
# lang: usado só para badge; category: agrupa na home
PROJECTS: dict[str, dict] = {
    "log-forensics":         dict(lang="Python", category="Defensiva", desc="Detector de ataques em logs de autenticação (brute-force SSH, user scan, root login)."),
    "cve-watch":             dict(lang="Python", category="Defensiva", desc="Matcher local de CVEs: cruza inventário de software com base local de vulnerabilidades (offline)."),
    "pwned-check":           dict(lang="Python", category="Defensiva", desc="Verificador de vazamento de senhas via k-anonymity (HIBP range API, só 5 chars do SHA-1 saem)."),
    "subdomain-recon":       dict(lang="Python", category="Defensiva", desc="Enumeração passiva de subdomínios (crt.sh + DNS) para mapear superfície de ataque própria."),
    "file-integrity-monitor":dict(lang="Python", category="Defensiva", desc="Monitor de integridade de arquivos por hashes SHA-256 (baseline vs estado atual)."),
    "tls-auditor":           dict(lang="Python", category="Defensiva", desc="Auditor de configuração TLS/SSL: detecta protocolos/cifras fracas e certificados expirados."),
    "pentest-agent":         dict(lang="Python", category="Ofensiva",   desc="Agente de pentest autônomo com trava de autorização (recon não destrutivo)."),
    "honeypot":              dict(lang="Python", category="Defensiva", desc="Honeypot SSH/HTTP de baixa interação que registra IPs, credenciais e User-Agents."),
    "host-ids":              dict(lang="Python", category="Defensiva", desc="IDS baseado em host (Linux): monitora processos, conexões e integridade, sem deps externas."),
    "phishing-detector":     dict(lang="Python", category="Defensiva", desc="Detector de phishing por heurísticas de URL com pontuação de risco 0-100."),
    "password-auditor":      dict(lang="Python", category="Defensiva", desc="Auditor de qualidade de senhas: entropia, tempo de quebra e detecção de senhas comuns."),
    "malware-analyzer":      dict(lang="Python", category="Defensiva", desc="Análise estática de malware: hashes, entropia, strings, IOCs e APIs suspeitas."),
    "network-scanner":       dict(lang="Python", category="Defensiva", desc="Scanner de rede: hosts, portas, SO e relatório HTML com histórico SQLite."),
    "threat-intel":          dict(lang="Python", category="Defensiva", desc="TIP: armazena, busca e expõe IOCs via API REST (stdlib pura)."),
    "mini-siem":             dict(lang="Python", category="Defensiva", desc="Mini-SIEM: ingestão, normalização e correlação de logs com detecção de ataques."),
    "dockview":              dict(lang="Python", category="DevOps",    desc="TUI visual para Docker (Textual) com abas para todos os tipos de recurso."),
    "DDfetch":               dict(lang="Shell",  category="DevOps",    desc="System fetch em Bash com ASCII art customizável (estilo fastfetch/neofetch)."),
    "BIGMAN":                dict(lang="Node",   category="Web",       desc="Bot de WhatsApp com IA conversacional para barbearia (Node + Gemini + Supabase)."),
    "Umbra":                 dict(lang="Java",   category="Privacidade",desc="Simulador de privacidade em Java que detecta/anonimiza dados sensíveis em JSON."),
}


def local_path(name: str) -> str | None:
    """Resolve o caminho local de um projeto, se existir em algum root."""
    for root in _LOCAL_ROOTS:
        cand = os.path.join(root, name)
        if os.path.isdir(cand) and os.path.isdir(os.path.join(cand, ".git")):
            return cand
    return None


def repo_url(name: str) -> str:
    return f"https://github.com/Diogo-Damasceno/{name}"
