"""Exemplos de uso (entrada -> saída) de cada projeto do portfólio.

Estático e seguro: são exemplos reais da CLI, escritos à mão para o
portfólio. Nada é executado no servidor nem no navegador — apenas
exibido como um "terminal" visual para o visitante entender como rodar.
"""

# cada exemplo: (comando, saida)
EXAMPLES: dict[str, list[tuple[str, str]]] = {
    "log-forensics": [
        ("lf auth.log --top 3",
         "IP                 tentativas  usuarios\n192.0.2.10         142        root, admin, user\n198.51.100.7       31         root\n203.0.113.22       12         deploy\n\n3 IPs com varredura de senha (user-scanning)"),
        ("lf auth.log --json",
         '[{"ip":"192.0.2.10","attempts":142,"users":["root","admin"]}]'),
    ],
    "cve-watch": [
        ("cve-watch scan inventory.toml",
         "VERIFICADO  openssl 1.1.1   -> CVE-2023-2650 (HIGH)\nVERIFICADO  curl 7.68     -> CVE-2023-32001 (MED)\nOK          python 3.11    sem CVE conhecido"),
    ],
    "pwned-check": [
        ("pwned-check 's3nh4fraca'",
         "Vazada 381 times (k-anonymity: 38BDD...)\nSenha NAO é segura — aparece em vazamentos conhecidos"),
        ("pwned-check '9xF$k2!mQz8vLp'",
         "Nao encontrada em vazamentos conhecidos\nSenha segura"),
    ],
    "subdomain-recon": [
        ("subdomain-recon exemplo.com",
         "crt.sh: 14 certificados\n  api.exemplo.com      -> 192.0.2.40 (A)\n  blog.exemplo.com     -> 198.51.100.9 (A)\n  cdn.exemplo.com      -> CNAME -> fastly\n\n14 subdominios descobertos"),
    ],
    "file-integrity-monitor": [
        ("fim baseline /etc",
         "baseline.json criado (1284 arquivos, SHA-256)"),
        ("fim check /etc",
         "ALTERADO  /etc/passwd\nREMOVIDO  /etc/cron.d/backdoor\nINTEGRO   1282/1284 arquivos"),
    ],
    "tls-auditor": [
        ("tls-auditor exemplo.com:443",
         "TLS 1.2/1.3 ok\nCifra fraca: TLS_RSA_WITH_AES_128_CBC_SHA (MEDIO)\nCertificado valido ate 2026-08-01\nNota: 78/100"),
    ],
    "pentest-agent": [
        ("pentest-agent 10.0.0.5 --authorize --max-steps 5",
         "[allowlist] alvo autorizado\n[1] recon: portas abertas 22,80,443\n[2] recon: servicos/versoes\n[3] recon: enumeracao web\n[4] correlacao com CVEs\n[5] relatorio gerado -> report.md"),
    ],
    "honeypot": [
        ("honeypot --ports 22,80",
         "[fake-ssh] 198.51.100.7 tentou root:admin\n[fake-http] 203.0.113.9 scan /wp-admin\nregistros: 2"),
        ("honeypot --stats",
         "IP            tentativas  credenciais\n198.51.100.7   1          root:admin\n203.0.113.9    1          (scan)"),
    ],
    "host-ids": [
        ("host-ids --once",
         "baseline: 312 processos, 48 conexoes\nmonitor ativo (intervalo 30s)"),
        ("host-ids",
         "ALERTA: novo processo 'miner-x' (PID 8841) fora do baseline\nALERTA: conexao saida 185.220.101.x:4444"),
    ],
    "phishing-detector": [
        ("phishing-detector 'http://g00gle-login.com/login'",
         "homografo: g00gle (~ goog1e)\nIP direto: nao\npontuacao de risco: 87/100\nRESULTADO: SUSPEITO"),
    ],
    "password-auditor": [
        ("password-auditor 'P@ssw0rd'",
         "entropia: 42.1 bits\nem wordlist comum: SIM (rockyou)\ntempo de quebra estimado: < 1s\nqualidade: FRACA"),
        ("password-auditor 'Tr0ub4dor&3'",
         "entropia: 28.0 bits\nsequencia de teclado detectada\nqualidade: FRACA"),
    ],
    "malware-analyzer": [
        ("malware-analyzer suspicious.bin",
         "md5  9f3a...\nsha256 1c7e...\nentropia 7.9 (ALTA -> possivel packing)\nIOC: 185.220.101.4, submit.php\nrisco: ALTO (relatorio estatico)"),
    ],
    "network-scanner": [
        ("network-scanner 10.0.0.0/24",
         "HOST 10.0.0.5    up  (Linux 5.x)\n  22/tcp   open  ssh\n  80/tcp   open  http  nginx\nHOST 10.0.0.12   up  (Windows 10)\n  445/tcp  open  smb"),
    ],
    "threat-intel": [
        ("threat-intel add ip 185.220.101.4 --confidence high --tag tor",
         "IOC registrado: ip 185.220.101.4 (tor, high)"),
        ("threat-intel lookup 185.220.101.4",
         "ip 185.220.101.4\n  tags: tor\n  confianca: high\n  fontes: 3"),
    ],
    "mini-siem": [
        ("mini-siem ingest auth.log",
         "142 eventos (failed_password)\nALERTA: brute-force de 192.0.2.10 (142 tentativas)"),
        ("mini-siem query 'SELECT * FROM alerts'",
         "id=1 brute-force 192.0.2.10\nid=2 web-scan 203.0.113.22"),
    ],
    "dockview": [
        ("dockview",
         "  (tela da baleia)\n  ENTER -> abre painel\n  setas: navega abas (Containers/Imagens/.../Labs)\n  s/x/d/l: start/stop/rm/log"),
    ],
    "DDfetch": [
        ("ddfetch",
         "       .--.     diogo@arch\n      |o_o |    OS: Arch Linux x86_64\n      |:_/ |    Kernel: 6.9.0-arch1\n     //   \\ \\   Memoria: 4812MiB / 15920MiB\n    (|     | )  Shell: zsh 5.9\n   /'\\_   _/`\\  WM: Hyprland\n   \\___)=(___/"),
    ],
    "BIGMAN": [
        ("(WhatsApp) cliente: 'qual o status do meu pedido 8821?'",
         "[webhook] assinatura valida\n[Gemini] consulta pedido 8821 -> 'em transporte'\n[Supabase] histórico salvo\n-> responde cliente no WhatsApp"),
    ],
    "Umbra": [
        ('umbra anon data.json',
         '{\n  "nome": "***",\n  "cpf": "***.***.***-**",\n  "email": "***@***",\n  "pedido": "8821",\n  "valor": 149.90\n}\n\n3 campos sensíveis anonimizados (privacidade ética)'),
    ],
}
