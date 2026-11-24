#!/usr/bin/env python3
"""
Gera dark_mode.svg e light_mode.svg para o README de perfil do GitHub.

- À esquerda: a tua imagem ASCII (ascii.txt), "desenhada" linha a linha
  por um cursor de rato que varre da esquerda para a direita.
- À direita: um painel estilo neofetch com as tuas informações.

Edita o bloco CONFIG abaixo e corre:  python3 generate.py
Se GITHUB_TOKEN e USERNAME estiverem definidos (ex.: no GitHub Actions),
as estatísticas do GitHub são preenchidas automaticamente.
"""
import json
import os
import urllib.request
from datetime import date
from html import escape

# ============================== CONFIG ==============================
USERNAME = os.environ.get("USERNAME", "joaorodrigues0764")
HEADER = f"{USERNAME}@github"
BIRTHDAY = date(2000, 1, 1)  # usado pelo placeholder "{uptime}" (não usado de momento)

# (chave, valor). Use None como valor para criar um separador de secção.
INFO = [
    ("Name", "João Rodrigues"),
    ("Host", "Instituto Superior Técnico"),
    ("Degree", "Computer Science & Engineering"),
    ("Focus", "Backend, Systems, Cloud, AI"),
    ("Currently", "Improving my Rust skills"),
    ("Status", "Open to Summer 2027 Internships"),
    ("", ""),
    ("Languages.Systems", "Rust, C, C++, Go, RISC-V Asm"),
    ("Languages.General", "Python, Java, TypeScript, SQL"),
    ("Backend.Cloud", "FastAPI, Axum, PostgreSQL, CF Workers"),
    ("Tools", "Git, Linux, Docker, GitHub"),
    ("Languages.Real", "Portuguese, English"),
    ("— Achievements", None),
    ("Hackathon", "1st Place, AInnovation 2026"),
    ("Project", "Caixa Explica (AI fin. literacy)"),
    ("— Contact", None),
    ("Email", "joao.sousa.rodrigues@tecnico.ulisboa.pt"),
    ("LinkedIn", "in/joão-rodrigues-9b02562b1"),
    ("— GitHub Stats", None),
    ("Repos", "{repos}   |  Stars: {stars}"),
    ("Followers", "{followers}  |  Commits: {commits}"),
]

# Animação
ROW_TIME = 0.045      # segundos que o cursor demora a varrer cada linha
START_DELAY = 0.4     # pausa antes de começar
# ====================================================================

THEMES = {
    "dark": dict(bg="#161b22", art="#c9d1d9", key="#ffa657", val="#a5d6ff",
                 head="#ff7b72", dim="#616e7f", cursor_fill="#ffffff", cursor_stroke="#000000"),
    "light": dict(bg="#f6f8fa", art="#24292f", key="#953800", val="#0a3069",
                  head="#cf222e", dim="#8c959f", cursor_fill="#000000", cursor_stroke="#ffffff"),
}

# Geometria da arte (forçada com textLength, por isso não depende da fonte)
ART_FS, ART_CW, ART_LH = 7.8, 4.7, 8.9
PAD = 20
INFO_FS, INFO_CW, INFO_LH = 15.0, 9.0, 21.0
INFO_COLS = 58
FONT = "ConsolasFallback, Consolas, 'DejaVu Sans Mono', Menlo, 'Courier New', monospace"


def github_stats():
    token = os.environ.get("GITHUB_TOKEN")
    stats = dict(repos="—", stars="—", followers="—", commits="—")
    if not token or USERNAME == "teu-username":
        return stats

    def get(url):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-readme-generator",
        })
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    try:
        user = get(f"https://api.github.com/users/{USERNAME}")
        stats["repos"] = user["public_repos"]
        stats["followers"] = user["followers"]
        stars, page = 0, 1
        while True:
            repos = get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}")
            stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
            if len(repos) < 100:
                break
            page += 1
        stats["stars"] = stars
        stats["commits"] = get(
            f"https://api.github.com/search/commits?q=author:{USERNAME}&per_page=1")["total_count"]
    except Exception as e:  # nunca falha o build por causa das stats
        print("aviso: não foi possível obter stats:", e)
    return stats


def uptime():
    t = date.today()
    y = t.year - BIRTHDAY.year - ((t.month, t.day) < (BIRTHDAY.month, BIRTHDAY.day))
    last = BIRTHDAY.replace(year=BIRTHDAY.year + y)
    days = (t - last).days
    return f"{y} years, {days} days"


def build(theme, art_lines, values):
    c = THEMES[theme]
    art_w = max(len(l) for l in art_lines) * ART_CW
    art_h = len(art_lines) * ART_LH
    info_x = PAD + art_w + 30
    width = int(info_x + INFO_COLS * INFO_CW + PAD)
    height = int(max(art_h, (len(INFO) + 2) * INFO_LH) + 2 * PAD)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="{FONT}">']
    total_art = START_DELAY + len(art_lines) * ROW_TIME
    out.append(f"""<style>
  .art {{ fill:{c['art']}; font-size:{ART_FS}px; white-space:pre; }}
  .info {{ font-size:{INFO_FS}px; white-space:pre; opacity:0;
           animation: in .35s ease-out forwards; }}
  .k {{ fill:{c['key']}; }} .v {{ fill:{c['val']}; }} .h {{ fill:{c['head']}; font-weight:bold; }}
  .d {{ fill:{c['dim']}; }}
  @keyframes in {{ from {{ opacity:0; transform:translateX(-8px); }} to {{ opacity:1; transform:none; }} }}
  #cursor {{ animation: hide .3s {total_art + 0.3:.2f}s forwards; }}
  @keyframes hide {{ to {{ opacity:0; }} }}
</style>""")
    out.append(f'<rect width="{width}" height="{height}" rx="15" fill="{c["bg"]}"/>')

    # ---- arte ASCII + clips animados ----
    defs, texts, cursor_pts = [], [], []
    for i, line in enumerate(art_lines):
        y = PAD + (i + 1) * ART_LH
        content = line.rstrip()
        lead = len(content) - len(content.lstrip(" "))
        content = content.strip(" ")
        x0 = PAD + lead * ART_CW
        x1 = x0 + len(content) * ART_CW
        t0 = START_DELAY + i * ROW_TIME
        if content:
            defs.append(
                f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="{y - ART_LH:.1f}" width="0" height="{ART_LH + 1}">'
                f'<animate attributeName="width" from="0" to="{x1 - x0 + 2:.1f}" begin="{t0:.3f}s" '
                f'dur="{ROW_TIME:.3f}s" fill="freeze"/></rect></clipPath>')
            texts.append(
                f'<text class="art" x="{x0:.1f}" y="{y - 1.5:.1f}" textLength="{len(content) * ART_CW:.1f}" '
                f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{i})">{escape(content)}</text>')
        else:
            x1 = x0
        cursor_pts.append((t0, x0, y - ART_LH / 2))
        cursor_pts.append((t0 + ROW_TIME * 0.98, x1, y - ART_LH / 2))

    out.append("<defs>" + "".join(defs) + "</defs>")
    out.extend(texts)

    # ---- painel de informação ----
    y = PAD + INFO_LH
    delay = total_art * 0.25  # começa a aparecer enquanto a arte ainda está a ser desenhada
    step = (total_art * 0.75) / len(INFO)

    def line(svg_inner, d):
        out.append(f'<text class="info" x="{info_x:.1f}" y="{y:.1f}" style="animation-delay:{d:.2f}s">{svg_inner}</text>')

    line(f'<tspan class="h">{escape(HEADER)}</tspan> <tspan class="d">{"—" * (INFO_COLS - len(HEADER) - 1)}</tspan>', delay)
    for k, v in INFO:
        y += INFO_LH
        delay += step
        if v is None:  # separador de secção
            line(f'<tspan class="h">{escape(k)}</tspan> <tspan class="d">{"—" * (INFO_COLS - len(k) - 1)}</tspan>', delay)
            continue
        if not k:
            continue
        v = v.format(**values)
        dots = "." * max(1, INFO_COLS - len(k) - len(v) - 4)
        line(f'<tspan class="d">. </tspan><tspan class="k">{escape(k)}</tspan><tspan class="d">:{dots} </tspan>'
             f'<tspan class="v">{escape(v)}</tspan>', delay)

    # ---- cursor do rato ----
    dur = cursor_pts[-1][0] + 0.2
    first = cursor_pts[0]
    pts = [(0.0, first[1], first[2])] + cursor_pts + [(dur, cursor_pts[-1][1], cursor_pts[-1][2])]
    key_times = ";".join(f"{min(t / dur, 1):.5f}" for t, _, _ in pts)
    values_ = ";".join(f"{x:.1f} {yy:.1f}" for _, x, yy in pts)
    out.append(
        f'<g id="cursor"><g><animateTransform attributeName="transform" type="translate" '
        f'values="{values_}" keyTimes="{key_times}" dur="{dur:.3f}s" fill="freeze"/>'
        f'<path d="M0 0 L0 17 L4.5 13 L7.5 20 L10.5 18.6 L7.6 12 L13 12 Z" '
        f'fill="{c["cursor_fill"]}" stroke="{c["cursor_stroke"]}" stroke-width="1.2" stroke-linejoin="round"/>'
        f'</g></g>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "ascii.txt"), encoding="utf-8") as f:
        art = f.read().rstrip("\n").split("\n")
    values = dict(uptime=uptime(), **github_stats())
    for theme in THEMES:
        with open(os.path.join(here, f"{theme}_mode.svg"), "w", encoding="utf-8") as f:
            f.write(build(theme, art, values))
    print("ok:", ", ".join(f"{t}_mode.svg" for t in THEMES))


if __name__ == "__main__":
    main()
