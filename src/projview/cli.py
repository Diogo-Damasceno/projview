"""projview — gerador de portfólio estático.

Uso:
  projview scan     # lista os projetos configurados e o que cada um tem
  projview build    # gera o site em docs/ (cards + páginas por projeto)

O site é 100% estático: nada é executado no servidor nem no navegador do
visitante. Os testes rodam AQUI, na sua máquina, no momento do build.
"""

from __future__ import annotations

import sys

from projview.builder import build_site
from projview.scanner import scan_projects


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    try:
        if cmd == "scan":
            from projview import scanner
            scanner.main()
        elif cmd == "build":
            build_site()
        else:
            print(f"comando desconhecido: {cmd} (use scan ou build)")
            sys.exit(2)
    except KeyboardInterrupt:
        print("\ninterrompido")
        sys.exit(130)


if __name__ == "__main__":
    main()
