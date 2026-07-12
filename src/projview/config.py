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

    

    # >>> FORGE45 START
    "payload-coder":           dict(lang="Python", category="Defensiva", desc="Codifica/decodifica payloads em base64/hex/url para análise segura."),
    "hash-breaker":           dict(lang="Python", category="Defensiva", desc="Força-bruta de hash com wordlist (apenas testes autorizados)."),
    "auth-log-watch":           dict(lang="Python", category="Defensiva", desc="Detector de brute-force e varredura em logs de autenticação."),
    "port-lister":           dict(lang="Python", category="Defensiva", desc="Scanner de portas TCP (contra alvos que você possui)."),
    "subdomain-mapper":           dict(lang="Python", category="Defensiva", desc="Enumeração passiva de subdomínios (DNS) de seu próprio domínio."),
    "jwt-inspector":           dict(lang="Python", category="Defensiva", desc="Inspeciona claims de JWT (leitura, sem quebrar assinatura)."),
    "integrity-guard":           dict(lang="Python", category="Defensiva", desc="Monitor de integridade de arquivos por SHA-256 (baseline vs atual)."),
    "phish-rater":           dict(lang="Python", category="Defensiva", desc="Pontua risco de URL de phishing (0-100) por heurísticas."),
    "web-hardener":           dict(lang="Python", category="Defensiva", desc="Sonda cabeçalhos de segurança (HSTS, CSP, X-Frame) do seu site."),
    "cve-matcher":           dict(lang="Python", category="Defensiva", desc="Cruza inventário de software com base local de CVEs (offline)."),
    "tls-checker":           dict(lang="Python", category="Defensiva", desc="Auditor de configuração TLS: protocolos/cifras fracas e cert expirado."),
    "packet-sniffer":           dict(lang="Python", category="Defensiva", desc="Analisa dumps de tráfego (formato texto) por padrões suspeitos."),
    "host-audit":           dict(lang="Python", category="Defensiva", desc="Auditoria de integridade e permissões de arquivos do host."),
    "ioc-hunter":           dict(lang="Python", category="Defensiva", desc="Caça IOCs (IPs, hashes, domínios) em logs e relatórios."),
    "backup-verifier":           dict(lang="Python", category="Defensiva", desc="Verifica integridade de backups por hash antes de restaurar."),
    "xss-forge":           dict(lang="Python", category="Defensiva", desc="Forja/ofusca payloads XSS para testes de WAF/input-validation."),
    "sqli-forge":           dict(lang="Python", category="Defensiva", desc="Forja/ofusca payloads SQLi para testes de input-validation."),
    "waf-tester":           dict(lang="Python", category="Defensiva", desc="Classifica vetores de evasão de WAF por pontuação de risco."),
    "dir-brute":           dict(lang="Python", category="Defensiva", desc="Força-bruta de diretórios (wordlist) contra seu próprio alvo."),
    "header-spoof":           dict(lang="Python", category="Defensiva", desc="Testa cabeçalhos de host/spoofing em seu próprio servidor."),
    "token-leak":           dict(lang="Python", category="Defensiva", desc="Busca segredos vazados (API keys, tokens) em seus repositórios."),
    "csrf-forge":           dict(lang="Python", category="Defensiva", desc="Forja formulários CSRF para testar proteção do seu app."),
    "lfi-probe":           dict(lang="Python", category="Defensiva", desc="Sonda vulnerabilidades LFI/Path-traversal no seu app de teste."),
    "brute-api":           dict(lang="Python", category="Defensiva", desc="Força-bruta de endpoint de API (taxa controlada, só autorizado)."),
    "recon-foot":           dict(lang="Python", category="Defensiva", desc="Reconhecimento de footprint de seu próprio domínio (DNS)."),
    "evil-link":           dict(lang="Python", category="Defensiva", desc="Gera e pontua URLs de engenharia social para simulação própria."),
    "cert-linter":           dict(lang="Python", category="Defensiva", desc="Valida certificados TLS (expiração/emitente) de seus domínios."),
    "header-leak":           dict(lang="Python", category="Defensiva", desc="Detecta vazamento de headers sensíveis (Server, X-Powered-By)."),
    "cookie-flag":           dict(lang="Python", category="Defensiva", desc="Verifica flags de cookie (Secure, HttpOnly, SameSite) do seu app."),
    "param-tamper":           dict(lang="Python", category="Defensiva", desc="Forja/ofusca parâmetros para testar Mass Assignment (autorizado)."),
    "redirect-find":           dict(lang="Python", category="Defensiva", desc="Classifica redirecionamentos abertos por pontuação de risco."),
    "java-pass-hasher":           dict(lang="Java", category="Defensiva", desc="Hasher de senhas em Java (SHA-256) para testes autorizados."),
    "java-b64":           dict(lang="Java", category="Defensiva", desc="Codificador/decodificador base64 em Java."),
    "java-validator":           dict(lang="Java", category="Defensiva", desc="Valida CPF/CNPJ/email (formato) em Java."),
    "java-aes":           dict(lang="Java", category="Defensiva", desc="Cifra/decifra AES (demonstração, autorizado)."),
    "java-portscan":           dict(lang="Java", category="Defensiva", desc="Scanner de portas TCP em Java (contra alvos próprios)."),
    "java-dns":           dict(lang="Java", category="Defensiva", desc="Resolver DNS em Java (uso autorizado)."),
    "java-json-anon":           dict(lang="Java", category="Defensiva", desc="Anonimiza campos sensíveis em JSON (org.json)."),
    "java-hash-crack":           dict(lang="Java", category="Defensiva", desc="Hasher auxiliar para força-bruta de hash (md5) autorizada."),
    "java-url-coder":           dict(lang="Java", category="Defensiva", desc="Codificador URL em Java para ofuscar payloads (autorizado)."),
    "java-cpf-check":           dict(lang="Java", category="Defensiva", desc="Validador de CPF (dígitos verificadores) em Java."),
    "java-rc4":           dict(lang="Java", category="Defensiva", desc="Cifra de fluxo RC4 (demonstração educacional)."),
    "java-subdomain":           dict(lang="Java", category="Defensiva", desc="Resolver de subdomínios em Java para recon próprio."),
    "java-filehash":           dict(lang="Java", category="Defensiva", desc="Hash SHA-256 de arquivos em Java (integridade)."),
    "java-otp":           dict(lang="Java", category="Defensiva", desc="Gerador TOTP/HOTP simplificado em Java (base32)."),
    "java-logscan":           dict(lang="Java", category="Defensiva", desc="Marca padrões suspeitos em logs (heurística) em Java."),
    # <<< FORGE45 END
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
