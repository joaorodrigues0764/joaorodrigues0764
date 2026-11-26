#!/usr/bin/env python3
"""Ajusta os SVGs do gráfico 3D: troca as datas por "Last Year" e remove estrelas e forks."""
import re
import sys

DATES = re.compile(r">\d{4}-\d{2}-\d{2} / \d{4}-\d{2}-\d{2}</text>")
ICON_AND_COUNT = re.compile(
    r'<g transform="translate\(\d+, \d+\), scale\(2\)"><path[^>]*></path></g>'
    r'<text[^>]*>[^<]*<title>[^<]*</title></text>')

for path in sys.argv[1:]:
    s = open(path, encoding="utf-8").read()
    s, n_dates = DATES.subn(">Last Year</text>", s)
    s, n_icons = ICON_AND_COUNT.subn("", s)
    if n_dates != 1 or n_icons != 2:
        sys.exit(f"{path}: layout mudou (datas={n_dates}, ícones={n_icons}), revê o tweak_3d.py")
    open(path, "w", encoding="utf-8").write(s)
    print("ok:", path)
