#!/usr/bin/env python3
"""Ajusta os SVGs do gráfico 3D: troca as datas por "Last Year", remove estrelas e forks e melhora as cores das linguagens."""
import re
import sys

DATES = re.compile(r">\d{4}-\d{2}-\d{2} / \d{4}-\d{2}-\d{2}</text>")
ICON_AND_COUNT = re.compile(
    r'<g transform="translate\(\d+, \d+\), scale\(2\)"><path[^>]*></path></g>'
    r'<text[^>]*>[^<]*<title>[^<]*</title></text>')

# Cores da roda das linguagens: as do GitHub são parecidas entre si
# (Python/TypeScript azuis, C/other cinzentos), por isso troco por cores bem distintas.
LANG_COLORS = {
    "#3572A5": "#FFD43B",  # Python      -> amarelo
    "#3178c6": "#3B82F6",  # TypeScript  -> azul
    "#dea584": "#F74C00",  # Rust        -> laranja
    "#555555": "#A371F7",  # C           -> roxo
    "#6E4C13": "#3FB950",  # Assembly    -> verde
    "#444444": "#8B949E",  # other       -> cinzento claro
}

for path in sys.argv[1:]:
    s = open(path, encoding="utf-8").read()
    for old, new in LANG_COLORS.items():
        s = re.sub(re.escape(old), new, s, flags=re.IGNORECASE)
    s, n_dates = DATES.subn(">Last Year</text>", s)
    s, n_icons = ICON_AND_COUNT.subn("", s)
    if n_dates != 1 or n_icons != 2:
        sys.exit(f"{path}: layout mudou (datas={n_dates}, ícones={n_icons}), revê o tweak_3d.py")
    open(path, "w", encoding="utf-8").write(s)
    print("ok:", path)
