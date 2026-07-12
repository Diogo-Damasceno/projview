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
    "warden-codec": [
        ("warden-codec encode base64 '<?php eval($_GET[x]);?>'", "PD89cGhwIGV2YWwoJF9HRVRbeF0pOz8+"),
        ("warden-codec decode hex 4142", "AB"),
    ],
    "b64kit": [
        ("java b64tool.Main enc oi", "b2k="),
        ("java b64tool.Main dec b2k=", "oi"),
    ],
    "jurlmask": [
        ("java jurlmask.Main enc 'http://a.com/x?q=1'", "http%3A%2F%2Fa.com%2Fx%3Fq%3D1"),
    ],
    "hashforge-cli": [
        ("hashforge-cli e99a18c428cb38d5f260853678922e03 wordlist.txt", "e99a18c428cb38d5f260853678922e03 -> 'abc123' (encontrado em 12ms)"),
    ],
    "apibrute": [
        ("apibrute -u admin -w senhas.txt https://api.proprio/login", "POST /login admin:admin123 -> 200 OK (credencial valida)"),
    ],
    "hashvault": [
        ("java hashvault.Main 'minhaSenha123'", "sha256: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"),
    ],
    "jhashcrack": [
        ("java jhashcrack.Main 5f4dcc3b5aa765d61d8327deb882cf99 rockyou.txt", "5f4dcc3b5aa765d61d8327deb882cf99 -> 'password'"),
    ],
    "portscope": [
        ("portscope 127.0.0.1 22,80,443", "22/tcp   open   ssh\\n80/tcp   open   http\\n443/tcp  open   https"),
    ],
    "jportscan": [
        ("java jportscan.Main 127.0.0.1 20-25", "22 -> open\\n23 -> closed\\n25 -> closed"),
    ],
    "subdns-recon": [
        ("subdns-recon exemplo.com wordlist.txt", "api.exemplo.com -> 192.0.2.40\\nblog.exemplo.com -> 198.51.100.9\\n6 subdominios descobertos"),
    ],
    "jsubdomain": [
        ("java jsubdomain.Main exemplo.com www,api,dev", "www -> 192.0.2.10\\napi -> 192.0.2.20\\ndev -> NXDOMAIN"),
    ],
    "jdnslook": [
        ("java jdnslook.Main exemplo.com", "A 192.0.2.10\\nMX mail.exemplo.com\\nTXT v=spf1 ..."),
    ],
    "reconmap": [
        ("reconmap exemplo.com", "hosts: 3 | portas abertas: 22,80,443 | exposicao: 1 (80 sem HSTS)"),
    ],
    "subdomain-recon": [
        ("subdomain-recon exemplo.com", "crt.sh: 14 certificados\\n  api.exemplo.com -> 192.0.2.40\\n14 subdominios descobertos"),
    ],
    "jwtpeek": [
        ("jwtpeek eyJhbGc...eyJzdWIiOiIxMjMifQ.sign", "header: {\"alg\":\"HS256\",\"typ\":\"JWT\"}\\npayload: {\"sub\":\"123\",\"role\":\"user\"}"),
    ],
    "jsonmask": [
        ("java jsonmask.Main '{\"cpf\":\"123.456.789-00\",\"nome\":\"Joao\"}'", "{\"cpf\":\"***\",\"nome\":\"Joao\"} (1 campo anonimizado)"),
    ],
    "sha-sentinel": [
        ("sha-sentinel baseline /etc", "baseline.json criado (1284 arquivos, SHA-256)"),
        ("sha-sentinel check /etc", "ALTERADO /etc/passwd\\nINTEGRO 1282/1284 arquivos"),
    ],
    "backupseal": [
        ("backupseal verificar backup1.tar backup2.tar", "backup1.tar OK (sha256 confere)\\nbackup2.tar CORROMPIDO"),
    ],
    "hostwatch": [
        ("hostwatch /bin /usr/bin", "ALTERADO /usr/bin/ssh (perm 0755 -> 0777)\\nINTEGRO 4231/4232"),
    ],
    "jfilehash": [
        ("java jfilehash.Main documento.pdf", "sha256: 9f3a...e7c1 (documento.pdf)"),
    ],
    "http-hardener": [
        ("http-hardener https://meusite.com", "HSTS: ausente\\nCSP: ausente\\nX-Frame-Options: DENY\\nNota: 62/100"),
    ],
    "phishscore": [
        ("phishscore 'http://g00gle-login.com/login'", "homografo: g00gle (~ goog1e)\\npontuacao: 87/100\\nRESULTADO: SUSPEITO"),
    ],
    "leakheaders": [
        ("leakheaders headers.txt", "Server: nginx/1.18.0 (vaza versao)\\nX-Powered-By: PHP/8.1 (vaza runtime)"),
    ],
    "cookieguard": [
        ("cookieguard https://meusite.com", "sessionid: sem Secure, sem HttpOnly (FRAGIL)\\ncsrftoken: Secure+HttpOnly OK"),
    ],
    "csrfmith": [
        ("csrfmith encode url '<form action=/transfer>'", "<form action=/transfer method=POST>\\n<input name=csrf value=> (PoC sem token)"),
    ],
    "lfiscope": [
        ("lfiscope 'http://127.0.0.1:8080/file?path=../../etc/passwd'", "LFI confirmado: /etc/passwd lido via ../../"),
    ],
    "sqlinja": [
        ("sqlinja encode hex \"' OR '1'='1\"", "0x27204f522031273d2731 (payload SQLi ofuscado)"),
    ],
    "xssmith": [
        ("xssmith encode url '<script>alert(1)</script>'", "%3Cscript%3Ealert(1)%3C%2Fscript%3E (payload XSS ofuscado)"),
    ],
    "wafbypass": [
        ("wafbypass '<ScRiPt>alert(1)</sCrIpT>'", "vetor: case-mixing\\nrisco: 78/100 (bypassa WAF simples)"),
    ],
    "paramfuzz": [
        ("paramfuzz encode url 'role=admin'", "role%3Dadmin (teste de Mass Assignment)"),
    ],
    "openredir": [
        ("openredir 'http://a.com//evil.com'", "redireciona para externo\\nrisco: 64/100 (open-redirect provavel)"),
    ],
    "headerspoof": [
        ("headerspoof http://127.0.0.1:8080", "Host: spoofed.com aceito pelo servidor (relatado)"),
    ],
    "secretlint": [
        ("secretlint ./src", "AWS_KEY=AKIA...**** em config.py:12 (MASTER)\\nTOKEN=ghp_...**** em .env:3"),
    ],
    "phishforge": [
        ("phishforge 'http://clique-aqui.login'", "URL de simulacao gerada\\npontuacao: 91/100 (eficaz em lab)"),
    ],
    "aeslock": [
        ("java aestool.Main enc chave segredo", "U2FsdGVkX1+abc... (AES/CBC, demo)"),
    ],
    "jrc4stream": [
        ("java rc4tool.Main enc chave x", "stream cifrado (RC4, educacional): 0x9f 0x2a 0x1c"),
    ],
    "cpfvalid": [
        ("cpfvalid 123.456.789-09", "formato OK | digitos verificadores: INVALIDO"),
    ],
    "jcpfcheck": [
        ("java jcpfcheck.Main cpf 12345678909", "digitos verificadores conferem: VALIDO"),
    ],
    "authsentry": [
        ("authsentry auth.log", "192.0.2.10: 142 tentativas (brute-force)\\nroot,admin,user alvos"),
    ],
    "iochunt": [
        ("iochunt relatorio.txt", "IOC: 185.220.101.4 (ip)\\nIOC: 1c7e... (hash)\\n3 indicadores"),
    ],
    "pktwatch": [
        ("pktwatch dump.txt", "SCAN: 192.0.2.10 -> 192.0.2.5:22 (varredura)\\nEXFIL: 10 pacotes >1MB"),
    ],
    "blackview": [
        ("blackview", "  [BlackArch] 76 ferramentas\\n  Tab Files: navegue o PC\\n  'i' instala (sudo pacman)\\n  'x' mostra --help"),
        ("blackview  (tecla i em 'wireshark')", "[sudo] pacman -S blackarch/wireshark\\ninstalando wireshark... OK"),
    ],
    "gitview": [
        ("gitview ~/projects/meu-repo", "  [GitView] repo: meu-repo\\n  Tab Stage: space marca, 'c' commit, 'p' push\\n  Tab Files: 'a' copia arquivo do PC"),
        ("gitview  (aba Files, 'a' em /home/diogo/docs/relatorio.pdf)", "adicionado ao repo: relatorio.pdf (staged)"),
    ],
    "cvematic": [
        ("cvematic scan inventory.toml", "VERIFICADO openssl 1.1.1 -> CVE-2023-2650 (HIGH)\\nOK python 3.11 sem CVE"),
    ],
    "tlssentry": [
        ("tlssentry exemplo.com:443", "TLS 1.2/1.3 ok\\nCifra fraca: TLS_RSA_WITH_AES_128_CBC_SHA\\nCert valido ate 2026-08-01"),
    ],
    "cve-watch": [
        ("cve-watch scan inventory.toml", "VERIFICADO openssl 1.1.1 -> CVE-2023-2650 (HIGH)\\nOK python 3.11 sem CVE"),
    ],
    "tls-auditor": [
        ("tls-auditor exemplo.com:443", "TLS 1.2/1.3 ok\\nCifra fraca: TLS_RSA_WITH_AES_128_CBC_SHA\\nCert valido ate 2026-08-01"),
    ],
    "file-integrity-monitor": [
        ("fim baseline /etc", "baseline.json criado (1284 arquivos, SHA-256)"),
        ("fim check /etc", "ALTERADO /etc/passwd\\nINTEGRO 1282/1284 arquivos"),
    ],
    "log-forensics": [
        ("lf auth.log --top 3", "192.0.2.10 142 root,admin\\n3 IPs com user-scanning"),
    ],
    "pwned-check": [
        ("pwned-check 's3nh4fraca'", "Vazada 381 vezes\\nSenha NAO e segura"),
    ],

}
