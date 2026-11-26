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
BIRTHDAY = date(2000, 1, 1)  # usado pelo placeholder "{uptime}" (não usado de momento)

# Painel da direita: um terminal a correr "cargo run".
# Cada linha é uma lista de (classe, texto). Classes: g=verde, y=amarelo, b=azul,
# w=branco forte, m=cinzento, o=laranja, r=cor de Rust, v=normal. [] = linha vazia.
# Placeholders disponíveis: {repos} {stars} {followers} {commits}
COMMAND = "whoami"
K = lambda k: ("b", f"{k:<10}")  # coluna das chaves
LINES = [
    [("o", "João Rodrigues")],
    [("m", "─" * 44)],
    [K("Study"), ("v", "Computer Science & Engineering")],
    [K("Uni"), ("v", "Instituto Superior Técnico")],
    [K("Location"), ("v", "Lisbon, Portugal")],
    [K("Focus"), ("v", "Backend · Systems · Cloud · AI")],
    [K("Learning"), ("v", "Rust")],
    [K("Speaks"), ("v", "Portuguese, English")],
    [],
    [K("Award"), ("r", "★ "), ("v", "1st place · Hackathon 2026")],
    [K("Status"), ("g", "● "), ("v", "Open to summer 2027 internships")],
    [],
    [K("Email"), ("v", "joao.sousa.rodrigues@tecnico.ulisboa.pt")],
    [K("LinkedIn"), ("v", "in/joão-rodrigues-9b02562b1")],
]
TITLE = "joao@ist: ~/profile"

# Animação
ROW_TIME = 0.09       # segundos que o cursor demora a varrer cada linha
START_DELAY = 0.4     # pausa antes de começar
# ====================================================================

THEMES = {
    "dark": dict(bg="#161b22", art="#c9d1d9", cursor_fill="#ffffff", cursor_stroke="#000000", term_border="#30363d"),
    "light": dict(bg="#f6f8fa", art="#24292f", cursor_fill="#000000", cursor_stroke="#ffffff", term_border="#d0d7de"),
}
# O terminal é escuro nos dois temas.
TERM = dict(bg="#0d1117", bar="#21262d", text="#c9d1d9", title="#8b949e")

# Geometria da arte (forçada com textLength, por isso não depende da fonte)
ART_FS, ART_CW, ART_LH = 7.8, 4.7, 8.9
PAD = 20
INFO_FS, INFO_CW, INFO_LH = 15.0, 9.0, 31.0
INFO_COLS = 60
BAR_H = 36
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
    panel_x = PAD + art_w + 30
    text_x = panel_x + 22
    width = int(text_x + INFO_COLS * INFO_CW + 22 + PAD)
    rows = sum(1 if l else 0.6 for l in LINES) + 4  # comando + prompt final + margens
    height = int(max(art_h, BAR_H + rows * INFO_LH) + 2 * PAD)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="{FONT}">']
    total_art = START_DELAY + len(art_lines) * ROW_TIME
    out.append(f"""<style>
  .art {{ fill:{c['art']}; font-size:{ART_FS}px; white-space:pre; }}
  .info {{ font-size:{INFO_FS}px; white-space:pre; fill:{TERM['text']}; opacity:0;
           animation: in .3s ease-out forwards; }}
  .cmd {{ font-size:{INFO_FS}px; white-space:pre; fill:{TERM['text']}; }}
  .ttl {{ font-size:13px; fill:{TERM['title']}; }}
  .g {{ fill:#3fb950; font-weight:bold; }} .y {{ fill:#d29922; font-weight:bold; }}
  .b {{ fill:#58a6ff; }} .w {{ fill:#f0f6fc; font-weight:bold; }} .m {{ fill:#8b949e; }}
  .o {{ fill:#f0883e; font-weight:bold; }} .r {{ fill:#dea584; }} .v {{ fill:{TERM['text']}; }}
  @keyframes in {{ from {{ opacity:0; transform:translateY(4px); }} to {{ opacity:1; transform:none; }} }}
  #cursor {{ animation: hide .3s {total_art + 0.3:.2f}s forwards; }}
  @keyframes hide {{ to {{ opacity:0; }} }}
  @keyframes on {{ to {{ opacity:1; }} }}
  @keyframes blink {{ 0% {{ opacity:1; }} 50% {{ opacity:0; }} }}
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

    # ---- terminal "cargo run" ----
    ph = height - 2 * PAD
    out.append(f'<rect x="{panel_x}" y="{PAD}" width="{width - PAD - panel_x}" height="{ph}" rx="10" '
               f'fill="{TERM["bg"]}" stroke="{c["term_border"]}"/>')
    out.append(f'<path d="M{panel_x + 10} {PAD} H{width - PAD - 10} A10 10 0 0 1 {width - PAD} {PAD + 10} '
               f'V{PAD + BAR_H} H{panel_x} V{PAD + 10} A10 10 0 0 1 {panel_x + 10} {PAD} Z" fill="{TERM["bar"]}"/>')
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{panel_x + 20 + i * 20}" cy="{PAD + BAR_H / 2}" r="6" fill="{col}"/>')
    out.append(f'<text class="ttl" x="{(panel_x + width - PAD) / 2:.1f}" y="{PAD + BAR_H / 2 + 4.5:.1f}" '
               f'text-anchor="middle">{escape(TITLE)}</text>')

    # comando escrito letra a letra
    y = PAD + BAR_H + INFO_LH + 8
    n = len(COMMAND)
    cmd_x = text_x + 2 * INFO_CW
    t_start, t_type = 0.3, 1.1
    vals = ";".join(f"{k * INFO_CW:.1f}" for k in range(n + 1))
    keys = ";".join(f"{k / n:.4f}" for k in range(n + 1))
    out.append(f'<clipPath id="cmdclip"><rect x="{cmd_x:.1f}" y="{y - INFO_LH:.1f}" width="0" height="{INFO_LH + 6}">'
               f'<animate attributeName="width" values="{vals}" keyTimes="{keys}" calcMode="discrete" '
               f'begin="{t_start}s" dur="{t_type}s" fill="freeze"/></rect></clipPath>')
    out.append(f'<text class="cmd" x="{text_x:.1f}" y="{y:.1f}"><tspan class="g">❯</tspan></text>')
    out.append(f'<text class="cmd" x="{cmd_x:.1f}" y="{y:.1f}" clip-path="url(#cmdclip)">'
               f'<tspan class="w">{escape(COMMAND.split(" ")[0])}</tspan> {escape(" ".join(COMMAND.split(" ")[1:]))}</text>')

    def line(svg_inner, d):
        out.append(f'<text class="info" x="{text_x:.1f}" y="{y:.1f}" style="animation-delay:{d:.2f}s">{svg_inner}</text>')

    delay = t_start + t_type + 0.4
    step = max(total_art - delay, 1.5) / len(LINES)
    y += 8
    for segs in LINES:
        y += INFO_LH
        if not segs:
            y -= INFO_LH * 0.4  # linhas vazias ocupam menos espaço
            continue
        delay += step
        inner = "".join(f'<tspan class="{k}">{escape(t.format(**values))}</tspan>' for k, t in segs)
        line(inner, delay)

    # prompt final com cursor a piscar
    y += INFO_LH * 1.4
    delay += step + 0.2
    line('<tspan class="g">❯</tspan>', delay)
    out.append(f'<rect style="opacity:0;animation:on .01s {delay:.2f}s forwards, blink 1s step-end {delay + 0.5:.2f}s infinite" x="{text_x + 2 * INFO_CW:.1f}" y="{y - INFO_LH * 0.72:.1f}" '
               f'width="{INFO_CW:.1f}" height="{INFO_LH * 0.85:.1f}" fill="{TERM["text"]}"/>')

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


# ===================== CARTÕES DE PROJETOS =====================
# Um SVG por projeto (card_<slug>.svg). No README cada cartão é um link para o repositório.
PROJECTS = [
    dict(slug="caixa-explica", name="Caixa Explica", badge="★ Hackathon winner",
         desc=["AI-powered financial literacy assistant that makes",
               "financial information easier to understand."],
         tags=["FastAPI", "Next.js", "RAG"], lang=("Python", "#3572A5")),
    dict(slug="edgeguard", name="EdgeGuard", badge=None,
         desc=["Serverless monitoring and incident detection API",
               "running on Cloudflare's edge."],
         tags=["Workers", "D1", "Queues"], lang=("TypeScript", "#3178c6")),
    dict(slug="axum-notes-api", name="Axum Notes API", badge=None,
         desc=["REST API with async request handling",
               "and PostgreSQL persistence."],
         tags=["Axum", "SQLx", "PostgreSQL", "Docker"], lang=("Rust", "#dea584")),
]
REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7"
             ".75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1"
             " .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")


def build_card(p):
    w, h, px = 440, 170, 22
    cw = 7.2  # largura de um carácter a 12px (forçada com textLength)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
         '<style>text{white-space:pre}</style>',
         f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>',
         f'<path transform="translate({px} 22)" fill="#8b949e" d="{REPO_ICON}"/>',
         f'<text x="{px + 24}" y="35" font-size="17" font-weight="bold" fill="#58a6ff">{escape(p["name"])}</text>']
    if p["badge"]:
        bw = len(p["badge"]) * cw + 18
        o.append(f'<rect x="{w - px - bw}" y="19" width="{bw}" height="22" rx="11" fill="none" stroke="#d29922"/>')
        o.append(f'<text x="{w - px - bw / 2}" y="34" font-size="12" fill="#d29922" text-anchor="middle" '
                 f'textLength="{len(p["badge"]) * cw}" lengthAdjust="spacingAndGlyphs">{escape(p["badge"])}</text>')
    for i, line in enumerate(p["desc"]):
        o.append(f'<text x="{px}" y="{68 + i * 20}" font-size="13" fill="#c9d1d9">{escape(line)}</text>')
    # etiquetas (tags)
    x = px
    for t in p["tags"]:
        tw = len(t) * cw + 18
        o.append(f'<rect x="{x}" y="{h - 42}" width="{tw}" height="22" rx="11" fill="#1f6feb26"/>')
        o.append(f'<text x="{x + tw / 2}" y="{h - 27}" font-size="12" fill="#58a6ff" text-anchor="middle" '
                 f'textLength="{len(t) * cw}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>')
        x += tw + 8
    # linguagem principal (canto inferior direito)
    lang, col = p["lang"]
    lx = w - px - len(lang) * cw
    o.append(f'<circle cx="{lx - 10}" cy="{h - 31}" r="6" fill="{col}"/>')
    o.append(f'<text x="{lx}" y="{h - 27}" font-size="12" fill="#8b949e" textLength="{len(lang) * cw}" '
             f'lengthAdjust="spacingAndGlyphs">{escape(lang)}</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in PROJECTS:
        with open(os.path.join(here, f"card_{p['slug']}.svg"), "w", encoding="utf-8") as f:
            f.write(build_card(p))
    with open(os.path.join(here, "ascii.txt"), encoding="utf-8") as f:
        art = f.read().rstrip("\n").split("\n")
    stats = github_stats()
    extra = f" · {stats['commits']} commits" if isinstance(stats["commits"], int) else ""
    values = dict(uptime=uptime(), stats=extra, **stats)
    for theme in THEMES:
        with open(os.path.join(here, f"{theme}_mode.svg"), "w", encoding="utf-8") as f:
            f.write(build(theme, art, values))
    print("ok:", ", ".join(f"{t}_mode.svg" for t in THEMES))


if __name__ == "__main__":
    main()
