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
COMMAND = "cargo run --release --bin joao"
LINES = [
    [("g", "   Compiling"), ("v", " ist-cse v1.0.0 "), ("m", "(Instituto Superior Técnico)")],
    [("g", "   Compiling"), ("v", " systems v0.7.0 "), ("m", "(rust, c, c++, go, risc-v)")],
    [("g", "   Compiling"), ("v", " backend v0.9.0 "), ("m", "(fastapi, axum, postgresql)")],
    [("g", "   Compiling"), ("v", " cloud v0.8.0 "), ("m", "(cf workers, docker, linux)")],
    [("g", "   Compiling"), ("v", " ai v0.6.0 "), ("m", "(python, rag, llms)")],
    [],
    [("y", "warning"), ("w", ": `rust_skills` is still being improved")],
    [("b", "  -->"), ("v", " src/joao.rs:2026:11")],
    [("b", "   ="), ("w", " note"), ("v", ": this is intentional, keep shipping")],
    [],
    [("g", "    Finished"), ("v", " `release` profile [optimized]"), ("m", "{stats}")],
    [("g", "     Running"), ("v", " `target/release/joao`")],
    [],
    [("o", "Hi, I'm João Rodrigues!")],
    [("v", "Backend, systems, cloud & AI @ IST Lisbon.")],
    [],
    [("r", "★"), ("v", " 1st place · AInnovation Hackathon 2026")],
    [("m", "  └─ Caixa Explica, AI for financial literacy")],
    [("g", "●"), ("v", " Open to summer 2027 internships")],
    [],
    [("m", "✉ "), ("b", "joao.sousa.rodrigues@tecnico.ulisboa.pt")],
    [("m", "in "), ("b", "linkedin.com/in/joão-rodrigues-9b02562b1")],
]
TITLE = "joao@ist: ~/profile"

# Animação
ROW_TIME = 0.045      # segundos que o cursor demora a varrer cada linha
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
INFO_FS, INFO_CW, INFO_LH = 15.0, 9.0, 25.0
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


# ===================== CARGO BUILD (segunda animação) =====================
# As "dependências" do Cargo.toml do README, compiladas uma a uma.
CARGO_DEPS = [
    ("rust", "1.91.0"), ("c", "17.0.0"), ("cpp", "20.0.0"), ("go", "1.25.0"),
    ("risc-v-asm", "2.1.0"), ("python", "3.13.0"), ("java", "21.0.0"),
    ("typescript", "5.9.0"), ("sql", "2023.0.0"), ("fastapi", "0.115.0"),
    ("axum", "0.8.0"), ("postgresql", "17.0.0"), ("cloudflare-workers", "4.0.0"),
    ("git", "2.51.0"), ("linux", "6.17.0"), ("docker", "28.0.0"),
]
CARGO_SELF = ("joao-rodrigues", "2026.11.0", "(/home/joao/profile)")
CARGO_CMD = "cargo build --release"
CARGO_CYCLE = 14.0      # segundos de cada ciclo (a animação repete-se)
CARGO_STEP = 0.24       # segundos entre cada "Compiling"
CARGO_WINDOW = 10       # linhas de log visíveis (o resto faz scroll)


def build_cargo():
    fs, cw, lh = 14.0, 8.4, 22.0
    pad_x, bar_h = 20, 34
    width = 760
    log_top = bar_h + 16 + lh * 1.5          # depois da linha do comando
    height = int(log_top + lh * (CARGO_WINDOW + 3) + 10)
    T = CARGO_CYCLE
    css, body = [], []
    kid = [0]

    def pct(t):
        return max(0.0, min(100.0, t / T * 100))

    def show(t_on, t_off=None):
        """Classe CSS que mostra o elemento entre t_on e t_off (ou até ao fim do ciclo)."""
        kid[0] += 1
        n = f"k{kid[0]}"
        end = T - 0.4 if t_off is None else t_off
        css.append(f"@keyframes {n}{{0%,{pct(t_on):.3f}%{{opacity:0}}{pct(t_on) + 0.01:.3f}%,{pct(end):.3f}%{{opacity:1}}"
                   f"{pct(end) + 0.01:.3f}%,100%{{opacity:0}}}}")
        return f'style="opacity:0;animation:{n} {T}s linear infinite"'

    # cronologia
    t_type0, t_type = 0.3, 0.9
    t_upd = t_type0 + t_type + 0.35
    t_dl = t_upd + 0.45
    crates = [(n, v, "") for n, v in CARGO_DEPS] + [CARGO_SELF]
    t_comp = [t_dl + 0.4 + i * CARGO_STEP for i in range(len(crates))]
    t_fin = t_comp[-1] + 0.5
    t_prompt = t_fin + 0.35

    # janela do terminal
    body.append(f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>')
    body.append(f'<path d="M10.5 0.5 H{width - 10.5} A10 10 0 0 1 {width - 0.5} 10.5 V{bar_h} H0.5 V10.5 A10 10 0 0 1 10.5 0.5 Z" fill="#21262d"/>')
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        body.append(f'<circle cx="{20 + i * 20}" cy="{bar_h / 2}" r="6" fill="{col}"/>')
    body.append(f'<text class="ttl" x="{width / 2}" y="{bar_h / 2 + 4.5}" text-anchor="middle">joao@ist: ~/profile</text>')

    # comando, "escrito" por uma máscara que anda para a direita
    y = bar_h + 16 + lh * 0.8
    cmd_x = pad_x + 2 * cw
    body.append(f'<text x="{pad_x}" y="{y}"><tspan class="g">❯</tspan></text>')
    body.append(f'<text x="{cmd_x}" y="{y}"><tspan class="w">cargo</tspan> {escape(CARGO_CMD[6:])}</text>')
    n = len(CARGO_CMD)
    frames = "".join(f"{pct(t_type0 + t_type * k / n):.3f}%{{transform:translateX({k * cw:.1f}px)}}" for k in range(n + 1))
    css.append(f"@keyframes typing{{0%{{transform:translateX(0)}}{frames}100%{{transform:translateX({n * cw:.1f}px)}}}}")
    body.append(f'<rect x="{cmd_x - 1}" y="{y - lh * 0.8}" width="{n * cw + 12}" height="{lh}" fill="#0d1117" '
                f'style="animation:typing {T}s step-end infinite"/>')

    # linhas de log (com scroll quando passam da janela)
    log = [(t_upd, '<tspan class="g">    Updating</tspan> crates.io index'),
           (t_dl, f'<tspan class="g">  Downloaded</tspan> {len(CARGO_DEPS)} crates (4.2 MB) in 0.42s')]
    for (name, ver, extra), t in zip(crates, t_comp):
        log.append((t, f'<tspan class="g">   Compiling</tspan> {escape(name)} v{ver}'
                       + (f' <tspan class="m">{escape(extra)}</tspan>' if extra else "")))
    log.append((t_fin, '<tspan class="g">    Finished</tspan> `release` profile [optimized] target(s) in 4.20s'))

    lines = []
    for i, (t, inner) in enumerate(log):
        lines.append(f'<text x="{pad_x}" y="{log_top + (i + 1) * lh:.1f}" {show(t)}>{inner}</text>')
    # scroll: quando a linha i aparece e i >= janela, sobe tudo uma linha
    sframes = ["0%{transform:translateY(0)}"]
    for i, (t, _) in enumerate(log):
        if i >= CARGO_WINDOW:
            sframes.append(f"{pct(t):.3f}%{{transform:translateY({-(i - CARGO_WINDOW + 1) * lh:.1f}px)}}")
    sframes.append(f"{pct(T - 0.39):.3f}%{{transform:translateY(0)}}")
    css.append("@keyframes scroll{" + "".join(sframes) + "}")
    body.append(f'<clipPath id="win"><rect x="0" y="{log_top + 4}" width="{width}" height="{CARGO_WINDOW * lh + 2}"/></clipPath>')
    body.append(f'<g clip-path="url(#win)"><g style="animation:scroll {T}s step-end infinite">' + "".join(lines) + "</g></g>")

    # barra de progresso (por baixo da janela), muda a cada crate
    y_bar = log_top + (CARGO_WINDOW + 1) * lh + 4
    total, bw = len(crates), 28
    for i, ((name, _, _), t) in enumerate(zip(crates, t_comp)):
        done = int(bw * i / total)
        bar = "=" * done + (">" if done < bw else "") + " " * (bw - done - 1)
        t_off = t_comp[i + 1] if i + 1 < total else t_fin
        body.append(f'<text x="{pad_x}" y="{y_bar}" {show(t, t_off)}><tspan class="c">    Building</tspan> '
                    f'[{bar}] {i}/{total}: {escape(name)}</text>')

    # prompt final com cursor a piscar
    y_p = y_bar + lh * 1.2
    body.append(f'<text x="{pad_x}" y="{y_p}" {show(t_prompt)}><tspan class="g">❯</tspan></text>')
    kid[0] += 1
    css.append(f"@keyframes k{kid[0]}{{0%,{pct(t_prompt):.3f}%{{opacity:0}}"
               + "".join(f"{pct(t_prompt + s * 0.5):.3f}%{{opacity:{1 - s % 2}}}" for s in range(int((T - 0.4 - t_prompt) / 0.5)))
               + f"{pct(T - 0.4):.3f}%,100%{{opacity:0}}}}")
    body.append(f'<rect x="{pad_x + 2 * cw}" y="{y_p - lh * 0.72}" width="{cw}" height="{lh * 0.85}" fill="#c9d1d9" '
                f'style="opacity:0;animation:k{kid[0]} {T}s step-end infinite"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="{FONT}" font-size="{fs}px">\n<style>\n'
            "text{fill:#c9d1d9;white-space:pre}.ttl{font-size:13px;fill:#8b949e}\n"
            ".g{fill:#3fb950;font-weight:bold}.c{fill:#39c5cf;font-weight:bold}.w{fill:#f0f6fc;font-weight:bold}.m{fill:#8b949e}\n"
            + "\n".join(css) + "\n</style>\n" + "\n".join(body) + "\n</svg>")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "cargo_build.svg"), "w", encoding="utf-8") as f:
        f.write(build_cargo())
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
