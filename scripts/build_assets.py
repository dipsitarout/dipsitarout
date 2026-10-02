#!/usr/bin/env python3
"""Generates every animated SVG in assets/ from config.json.

Usage (from repo root):   python scripts/build_assets.py
Then commit the updated files in assets/.
All animation is SMIL inside the SVG (no JavaScript) so it plays on GitHub.
"""
import html, json, math, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

BG, PANEL, TRACK = "#060a14", "#0a1222", "#0f1b30"
CY, BL, PU, GR, WH, DIM = "#00f0ff", "#2f6bff", "#b026ff", "#39ff88", "#eafcff", "#7a93b0"
GRADS = {"cyan": (CY, BL), "purple": (PU, CY), "green": (GR, CY), "blue": (BL, PU)}
ACC = {"cyan": CY, "purple": PU, "green": GR, "blue": BL}
FONT = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"

_n = [0]


def uid(p="i"):
    _n[0] += 1
    return f"{p}{_n[0]}"


def esc(s):
    return html.escape(str(s), quote=True)


def T(x, y, s, size=13, fill=WH, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" xml:space="preserve" {extra}>{esc(s)}</text>')


def defs():
    g = "".join(f'<linearGradient id="g-{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}"/>'
                f'<stop offset="1" stop-color="{b}"/></linearGradient>' for k, (a, b) in GRADS.items())
    return (f'<defs>{g}'
            '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<filter id="glow" x="-30%" y="-40%" width="160%" height="180%"><feGaussianBlur stdDeviation="4" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<filter id="soft" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="1.5" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".03"/></pattern>'
            '</defs>')


def write(name, w, h, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'font-family="{FONT}">{defs()}{body}</svg>')
    (OUT / name).write_text(svg, encoding="utf-8")


# ---------- building blocks ----------
def panel(w, h, title, accent=CY, tag=""):
    s = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{PANEL}" stroke="{accent}" stroke-width="1.4">'
         f'<animate attributeName="stroke-opacity" values=".3;.8;.3" dur="4s" repeatCount="indefinite"/></rect>'
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#scan)"/>')
    L = 16
    for cx, cy, sx, sy in ((9, 9, 1, 1), (w - 9, 9, -1, 1), (9, h - 9, 1, -1), (w - 9, h - 9, -1, -1)):
        s += (f'<path d="M{cx} {cy+sy*L}V{cy}H{cx+sx*L}" fill="none" stroke="{accent}" stroke-width="2.5" '
              f'stroke-linecap="round" filter="url(#soft)"/>')
    s += T(26, 34, title, 13, accent, weight="bold", extra='letter-spacing="3" filter="url(#soft)"')
    if tag:
        s += T(w - 26, 34, tag, 10, DIM, "end", extra='letter-spacing="2"')
    s += f'<rect x="26" y="44" width="{w-52}" height="1.5" fill="{accent}" opacity=".35"/>'
    return s


def bar(x, y, w, h, pct, grad="cyan", delay=0.0, dur=1.4, ticks=20):
    i = uid("c")
    pct = max(0, min(100, pct))
    fw = round(w * pct / 100, 1)
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{TRACK}" stroke="#1d3150"/>'
    s += f'<clipPath id="{i}"><rect x="{x}" y="{y}" width="{fw}" height="{h}" rx="3"/></clipPath>'
    s += (f'<rect x="{x}" y="{y}" width="{fw}" height="{h}" rx="3" fill="url(#g-{grad})" filter="url(#soft)">'
          f'<set attributeName="width" to="0" begin="0s"/>'
          f'<animate attributeName="width" from="0" to="{fw}" dur="{dur}s" begin="{delay}s" fill="freeze" '
          f'calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'
          f'<animate attributeName="opacity" values="1;.72;1" dur="2.8s" begin="{delay+dur:.2f}s" repeatCount="indefinite"/></rect>')
    s += (f'<rect x="{x-36}" y="{y}" width="36" height="{h}" fill="url(#shine)" clip-path="url(#{i})">'
          f'<animate attributeName="x" from="{x-36}" to="{x+fw}" dur="2.6s" begin="{delay+dur+.3:.2f}s" repeatCount="indefinite"/></rect>')
    d = "".join(f"M{x + w*k/ticks:.1f} {y}v{h}" for k in range(1, ticks))
    s += f'<path d="{d}" stroke="{PANEL}" stroke-width="1.6" opacity=".9"/>'
    return s


def dot(cx, cy, color=GR, r=4):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" filter="url(#soft)">'
            f'<animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}">'
            f'<animate attributeName="r" values="{r};{r*3}" dur="1.6s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".7;0" dur="1.6s" repeatCount="indefinite"/></circle>')


def bolt(x, y, color=GR, anim=""):
    return (f'<polygon points="{x+5},{y-12} {x-3},{y+1} {x+2},{y+1} {x},{y+12} {x+9},{y-3} {x+4},{y-3}" '
            f'fill="{color}" filter="url(#soft)" {"opacity=\"0\"" if anim else ""}>{anim}</polygon>')


def chips(x, y, labels, color, maxx, size=11, sep=None):
    s, cx, cy = "", x, y
    for k, lab in enumerate(labels):
        w = len(lab) * size * 0.62 + 20
        if cx + w > maxx:
            cx, cy = x, cy + 30
        s += (f'<rect x="{cx:.0f}" y="{cy}" width="{w:.0f}" height="22" rx="4" fill="{color}" fill-opacity=".1" '
              f'stroke="{color}" stroke-opacity=".75"/>' + T(f"{cx + w/2:.0f}", cy + 15, lab, size, color, "middle"))
        cx += w
        if sep and k < len(labels) - 1:
            s += T(f"{cx + 9:.0f}", cy + 16, sep, 14, PU, "middle", "bold")
            cx += 18
        else:
            cx += 8
    return s, cy + 22


def window(start, d, T_):
    kt = f"0;{start/T_:.4f};{(start+d)/T_:.4f};{(T_-.6)/T_:.4f};1"
    return (f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="{kt}" dur="{T_}s" repeatCount="indefinite"/>')


def typed(x, y, s, color, size, start, T_, extra=""):
    i = uid("t")
    n, cw = len(s), size * 0.6
    d = max(0.4, n * 0.045)
    W = n * cw + 8
    kt = f"0;{start/T_:.4f};{(start+d)/T_:.4f};{(T_-.6)/T_:.4f};1"
    clip = (f'<clipPath id="{i}"><rect x="{x-2}" y="{y-size-2}" width="0" height="{size+10}">'
            f'<animate attributeName="width" values="0;0;{W:.0f};{W:.0f};0" keyTimes="{kt}" dur="{T_}s" repeatCount="indefinite"/></rect></clipPath>')
    return clip + T(x, y, s, size, color, extra=f'clip-path="url(#{i})" {extra}'), d


def hexpts(cx, cy, r):
    return " ".join(f"{cx + r*math.cos(math.radians(60*k-30)):.1f},{cy + r*math.sin(math.radians(60*k-30)):.1f}" for k in range(6))


# ---------- assets ----------
def banner():
    w, h, p = 900, 280, CFG["profile"]
    s = (f'<clipPath id="bc"><rect width="{w}" height="{h}" rx="14"/></clipPath>'
         '<linearGradient id="bgv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1330"/><stop offset="1" stop-color="#050813"/></linearGradient>'
         '<radialGradient id="rc" cx=".15" cy=".2" r=".6"><stop offset="0" stop-color="#00f0ff" stop-opacity=".22"/><stop offset="1" stop-color="#00f0ff" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="rp" cx=".88" cy=".25" r=".6"><stop offset="0" stop-color="#b026ff" stop-opacity=".3"/><stop offset="1" stop-color="#b026ff" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="gn" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff"/><stop offset=".5" stop-color="#eafcff"/><stop offset="1" stop-color="#c04bff"/></linearGradient>'
         '<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff" stop-opacity="0"/><stop offset=".5" stop-color="#00f0ff"/><stop offset="1" stop-color="#b026ff" stop-opacity="0"/></linearGradient>')
    g = (f'<rect width="{w}" height="{h}" fill="url(#bgv)"/><rect width="{w}" height="{h}" fill="url(#rc)"/>'
         f'<rect width="{w}" height="{h}" fill="url(#rp)"/>')
    for i in range(-14, 15):
        g += f'<path d="M450 150L{450+i*90} {h}" stroke="{CY}" stroke-opacity=".13" fill="none"/>'
    for y, o in ((162, .1), (178, .12), (200, .14), (230, .17), (268, .2)):
        g += f'<path d="M0 {y}H{w}" stroke="{CY}" stroke-opacity="{o}" fill="none"/>'
    g += (f'<rect y="0" width="{w}" height="2" fill="{CY}" opacity=".3"><animate attributeName="y" values="0;{h}" dur="5s" repeatCount="indefinite"/></rect>'
          f'<rect width="{w}" height="{h}" fill="url(#scan)"/>')
    s += f'<g clip-path="url(#bc)">{g}</g>'
    s += (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="none" stroke="{CY}" stroke-width="1.5">'
          f'<animate attributeName="stroke-opacity" values=".35;.9;.35" dur="4s" repeatCount="indefinite"/></rect>')
    for cx, cy, sx, sy in ((12, 12, 1, 1), (w-12, 12, -1, 1), (12, h-12, 1, -1), (w-12, h-12, -1, -1)):
        s += f'<path d="M{cx} {cy+sy*24}V{cy}H{cx+sx*24}" fill="none" stroke="{CY}" stroke-width="3" stroke-linecap="round" filter="url(#soft)"/>'
    name = p["name"]
    nx = dict(x=450, y=140, **{"font-size": 66, "font-weight": 800, "text-anchor": "middle"})
    base = 'font-size="66" font-weight="800" text-anchor="middle" letter-spacing="7" y="140" xml:space="preserve"'
    s += f'<text x="450" {base} fill="{CY}" opacity=".55" filter="url(#glow)">{esc(name)}</text>'
    s += (f'<text x="450" {base} fill="{PU}" opacity=".6"><animate attributeName="x" values="453;453;460;446;453" keyTimes="0;.8;.82;.85;1" dur="6s" repeatCount="indefinite"/>{esc(name)}</text>')
    s += (f'<text x="450" {base} fill="{CY}" opacity=".6"><animate attributeName="x" values="447;447;441;455;447" keyTimes="0;.8;.82;.85;1" dur="6s" repeatCount="indefinite"/>{esc(name)}</text>')
    s += f'<text x="450" {base} fill="url(#gn)">{esc(name)}</text>'
    s += (f'<text x="450" y="188" font-size="15" font-weight="bold" text-anchor="middle" letter-spacing="3" xml:space="preserve">'
          f'<tspan fill="{CY}">{esc(p["class"])}</tspan><tspan fill="{PU}">  |  </tspan><tspan fill="{GR}">{esc(p["subtitle"])}</tspan></text>')
    s += (f'<rect x="270" y="206" width="360" height="2" fill="url(#gl)"><animate attributeName="opacity" values=".4;1;.4" dur="3s" repeatCount="indefinite"/></rect>')
    s += T(34, 40, "PLAYER 01 // PROFILE", 11, DIM, extra='letter-spacing="3"')
    s += dot(w - 100, 36, GR, 3.5) + T(w - 34, 40, "ONLINE", 11, GR, "end", extra='letter-spacing="3"')
    s += (f'<text x="450" y="252" font-size="13" fill="{WH}" text-anchor="middle" letter-spacing="7">'
          f'<animate attributeName="opacity" values="1;.15;1" dur="1.8s" repeatCount="indefinite"/>&#9654; PRESS START</text>')
    s += T(34, 258, f"LEVEL {CFG['level']}%", 11, CY, extra='letter-spacing="2"')
    s += T(w - 34, 258, p["degree"], 11, DIM, "end", extra='letter-spacing="2"')
    write("banner.svg", w, h, s)


def boot():
    w, h, T_ = 640, 150, 9.0
    s = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="#050912" stroke="{GR}" stroke-opacity=".5" stroke-width="1.4"/>'
         f'<rect x="1" y="1" width="{w-2}" height="28" rx="10" fill="#0b1426"/><rect x="1" y="18" width="{w-2}" height="11" fill="#0b1426"/>'
         f'<circle cx="20" cy="15" r="4" fill="{PU}"/><circle cx="36" cy="15" r="4" fill="{CY}"/><circle cx="52" cy="15" r="4" fill="{GR}"/>'
         + T(w/2, 19, "player.boot", 11, DIM, "middle") + f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#scan)"/>')
    lines = [("> INITIALIZING PLAYER PROFILE...", CY, .4), ("> LOADING SKILLS...", CY, 2.1),
             ("> LOADING QUESTS...", CY, 3.4), ("> SYSTEM ONLINE", GR, 4.8)]
    for k, (txt, col, st) in enumerate(lines):
        y = 62 + k * 26
        t, d = typed(26, y, txt, col, 15, st, T_, 'filter="url(#soft)"' if col == GR else "")
        s += t
    s += bolt(26 + 15 * .6 * 15 + 16, 62 + 3 * 26 - 5, GR, window(4.8 + 15 * .045, .3, T_))
    write("boot.svg", w, h, s)


def player_card():
    w, h, p = 420, 330, CFG["profile"]
    s = panel(w, h, "PLAYER CARD", CY, "ID: P-01")
    rows = [("CLASS", p["class"], WH), ("SPECIALTY", p["specialty"], WH), ("BASE", p["base"], WH), ("STATUS", p["status"], GR)]
    for k, (lab, val, col) in enumerate(rows):
        y = 84 + k * 32
        s += T(28, y, lab, 11, DIM, extra='letter-spacing="2"') + T(128, y, ":", 13, DIM)
        if lab == "STATUS":
            s += dot(146, y - 4, GR, 3.5) + T(160, y, val, 13, col, weight="bold", extra='filter="url(#soft)"')
        else:
            s += T(144, y, val, 13, col, weight="bold")
    s += f'<path d="M28 212H392" stroke="{CY}" stroke-opacity=".35" stroke-dasharray="4 4"/>'
    lvl = CFG["level"]
    s += T(28, 240, "\u2605 LEVEL", 13, CY, weight="bold", extra='letter-spacing="3"')
    s += T(392, 244, f"{lvl}%", 26, GR, "end", "bold", 'filter="url(#glow)"')
    s += bar(28, 256, 364, 22, lvl, "cyan", 0.2, 1.8, 20)
    for xx, lab in ((28, "0"), (210, "50"), (392, "100")):
        s += T(xx, 298, lab, 9, DIM, {28: "start", 210: "middle", 392: "end"}[xx])
    s += T(28, 316, "PLAYER 01 \u00b7 " + p["name"], 9, DIM, extra='letter-spacing="2"')
    write("player-card.svg", w, h, s)


def mission():
    w, h, m = 420, 330, CFG["mission"]
    s = panel(w, h, "\U0001F9E0 CURRENT MISSION".replace("\U0001F9E0 ", ""), PU, "QUEST LOG")
    for k, it in enumerate(m["items"]):
        y = 82 + k * 25
        s += T(28, y, "\u25b8", 14, CY, weight="bold") + T(48, y, it, 14, WH)
    s += f'<path d="M28 212H392" stroke="{PU}" stroke-opacity=".4" stroke-dasharray="4 4"/>'
    s += T(28, 236, "MISSION STATUS", 11, DIM, extra='letter-spacing="2"') + T(392, 236, m["status_label"], 12, GR, "end", "bold", 'letter-spacing="2" filter="url(#soft)"')
    s += bar(28, 244, 364, 14, m["status_pct"], "green", 0.3, 1.6, 20)
    xp = min(100, m["xp"] / m["xp_max"] * 100)
    s += T(28, 288, "XP", 11, DIM, extra='letter-spacing="2"') + T(392, 288, f'{m["xp"]} XP', 12, CY, "end", "bold", 'filter="url(#soft)"')
    s += bar(28, 296, 364, 14, xp, "purple", 0.5, 1.6, 20)
    write("mission.svg", w, h, s)


def stats():
    w, h = 520, 340
    s = panel(w, h, "CHARACTER STATS", CY, "7 CORE SKILLS")
    for k, st in enumerate(CFG["stats"]):
        y, c = 86 + k * 35, ACC[st["color"]]
        s += f'<rect x="28" y="{y-9}" width="7" height="7" fill="{c}" transform="rotate(45 31.5 {y-5.5})" filter="url(#soft)"/>'
        s += T(46, y, st["name"], 12, WH, extra='letter-spacing="1"')
        s += bar(184, y - 11, 256, 14, st["value"], st["color"], 0.15 * k, 1.3)
        s += T(494, y, st["value"], 16, c, "end", "bold", 'filter="url(#soft)"')
    write("stats.svg", w, h, s)


def attributes():
    w, h = 320, 340
    s = panel(w, h, "PLAYER ATTRIBUTES", PU, "")
    for k, a in enumerate(CFG["attributes"]):
        y, c = 84 + k * 42, ACC[a["color"]]
        s += T(24, y, a["name"], 11, WH, extra='letter-spacing="1"') + T(296, y, a["value"], 13, c, "end", "bold")
        s += bar(24, y + 8, 272, 10, a["value"], a["color"], 0.2 * k, 1.3, 10)
    write("attributes.svg", w, h, s)


def quest():
    w, h, q = 860, 226, CFG["quest"]
    s = panel(w, h, "CURRENT QUEST", GR, "")
    s += (f'<rect x="{w-150}" y="16" width="124" height="26" rx="5" fill="{GR}" fill-opacity=".12" stroke="{GR}">'
          f'<animate attributeName="fill-opacity" values=".08;.3;.08" dur="2s" repeatCount="indefinite"/></rect>')
    s += dot(w - 134, 29, GR, 3) + T(w - 88, 33, f'[ {q["state"]} ]', 12, GR, "middle", "bold", 'letter-spacing="2"')
    s += T(32, 84, q["title"], 14, DIM)
    c, ey = chips(32, 100, q["tags"], CY, 600, 12, "+")
    s += c
    s += T(32, 170, "QUEST PROGRESS", 11, DIM, extra='letter-spacing="2"') + T(580, 170, f'{q["progress"]}%', 18, GR, "end", "bold", 'filter="url(#glow)"')
    s += bar(32, 180, 548, 20, q["progress"], "green", 0.2, 2.0, 25)
    bx = 620
    s += f'<rect x="{bx}" y="64" width="204" height="140" rx="8" fill="{GR}" fill-opacity=".04" stroke="{GR}" stroke-opacity=".6" stroke-dasharray="6 4"/>'
    s += (f'<circle cx="{bx+102}" cy="134" r="52" fill="none" stroke="{PU}" stroke-opacity=".4" stroke-dasharray="3 7">'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {bx+102} 134" to="360 {bx+102} 134" dur="14s" repeatCount="indefinite"/></circle>')
    s += T(bx + 102, 90, "REWARD", 11, DIM, "middle", extra='letter-spacing="4"')
    s += T(bx + 102, 138, f'+{q["reward_xp"]} XP', 28, GR, "middle", "bold", 'filter="url(#glow)"')
    s += T(bx + 102, 168, "+ " + q["reward_text"], 10, CY, "middle", "bold", 'letter-spacing="1"')
    s += T(bx + 102, 190, "VISUAL GAME METRIC", 8, DIM, "middle", extra='letter-spacing="2"')
    write("quest.svg", w, h, s)


def builds():
    for k, p in enumerate(CFG["projects"]):
        w, h, c = 420, 222, ACC[p["color"]]
        s = panel(w, h, f"MISSION {k+1:02d}", c, "")
        s += bolt(34, 74, c) + T(52, 80, p["name"], 19, WH, weight="bold", extra=f'letter-spacing="1" filter="url(#soft)"')
        s += f'<rect x="{w-132}" y="58" width="106" height="24" rx="5" fill="{GR}" fill-opacity=".1" stroke="{GR}" stroke-opacity=".8"/>'
        s += dot(w - 118, 70, GR, 3) + T(w - 70, 75, p["status"], 11, GR, "middle", "bold", 'letter-spacing="2"')
        s += T(28, 112, p["desc"], 13, DIM)
        cs, ey = chips(28, 126, p["tags"], c, w - 28)
        s += cs
        y = 190
        s += T(28, y + 4, "DIFFICULTY", 10, DIM, extra='letter-spacing="2"')
        s += bar(112, y - 8, 160, 14, p["difficulty"], p["color"], 0.2 + .1 * k, 1.3, 10)
        s += T(392, y + 8, f'XP +{p["xp"]}', 18, GR, "end", "bold", 'filter="url(#soft)"')
        write(f"build-{k+1}.svg", w, h, s)


def achievements():
    items = CFG["achievements"]
    for k, a in enumerate(items):
        w, h, c = 280, 196, ACC[a["color"]]
        s = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{PANEL}" stroke="{c}" stroke-width="1.3">'
             f'<animate attributeName="stroke-opacity" values=".35;.9;.35" dur="{3+k*.4:.1f}s" repeatCount="indefinite"/></rect>'
             f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#scan)"/>')
        s += T(w/2, 26, "[ \u2713 ACHIEVEMENT UNLOCKED ]", 10, GR, "middle", "bold", 'letter-spacing="1"')
        s += (f'<circle cx="140" cy="78" r="38" fill="none" stroke="{c}" stroke-opacity=".5" stroke-dasharray="3 6">'
              f'<animateTransform attributeName="transform" type="rotate" from="0 140 78" to="360 140 78" dur="12s" repeatCount="indefinite"/></circle>')
        s += f'<polygon points="{hexpts(140, 78, 30)}" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-width="2" filter="url(#soft)"/>'
        s += T(140, 84, a["code"], 17, WH, "middle", "bold", 'filter="url(#soft)"')
        for j, ln in enumerate(textwrap.wrap(a["title"], 28)):
            s += T(w/2, 134 + j * 16, ln, 13, WH, "middle", "bold")
        off = 16 * len(textwrap.wrap(a["title"], 28))
        s += T(w/2, 134 + off + 2, a["event"], 11, c, "middle")
        s += T(w/2, 184, f'+{a["xp"]} XP  (visual)', 10, DIM, "middle", extra='letter-spacing="1"')
        write(f"achv-{k+1}.svg", w, h, s)
    w, h = 280, 196
    s = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{PANEL}" stroke="{DIM}" stroke-opacity=".6" stroke-dasharray="6 5"/>'
         f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#scan)"/>')
    s += T(w/2, 26, "[ LOCKED ]", 10, DIM, "middle", "bold", 'letter-spacing="2"')
    s += (f'<path d="M126 74V64a14 14 0 0 1 28 0V74" fill="none" stroke="{DIM}" stroke-width="3"/>'
          f'<rect x="118" y="72" width="44" height="34" rx="5" fill="{DIM}" fill-opacity=".25" stroke="{DIM}" stroke-width="2"/>'
          f'<circle cx="140" cy="86" r="4" fill="{DIM}"/><rect x="138.5" y="88" width="3" height="10" fill="{DIM}"/>')
    s += T(w/2, 140, "NEXT ACHIEVEMENT", 13, DIM, "middle", "bold", 'letter-spacing="2"')
    s += T(w/2, 160, "???", 14, CY, "middle", "bold")
    write("achv-locked.svg", w, h, s)


def experience():
    w, h = 860, 228
    s = panel(w, h, "XP TIMELINE", CY, "2024 \u2192 2026")
    ly = 98
    s += (f'<linearGradient id="tl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity=".2"/>'
          f'<stop offset=".5" stop-color="{CY}"/><stop offset="1" stop-color="{GR}"/></linearGradient>'
          f'<rect x="40" y="{ly-1}" width="{w-80}" height="2" fill="url(#tl)"/>'
          f'<circle r="3.5" cy="{ly}" fill="{WH}" filter="url(#soft)"><animate attributeName="cx" values="40;{w-40}" dur="5s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0;1;1;0" dur="5s" repeatCount="indefinite"/></circle>')
    cols = CFG["timeline"]
    for ci, col in enumerate(cols):
        cx = 150 + ci * 280
        s += T(cx, 80, col["year"], 20, CY, "middle", "bold", 'letter-spacing="3" filter="url(#soft)"')
        s += f'<polygon points="{cx},{ly-8} {cx+8},{ly} {cx},{ly+8} {cx-8},{ly}" fill="{PANEL}" stroke="{CY}" stroke-width="2" filter="url(#soft)"/>'
        x0, y, last_y = cx - 105, 136, 136
        ys = []
        for it in col["items"]:
            ys.append(y)
            y += 34 + (14 if it.get("sub") else 0)
        s += f'<path d="M{x0} {ly+12}V{ys[-1]-4}" stroke="{CY}" stroke-opacity=".5" stroke-dasharray="3 4"/>'
        for it, yy in zip(col["items"], ys):
            final = (ci == len(cols) - 1 and it is col["items"][-1])
            s += f'<path d="M{x0} {yy-4}h14" stroke="{GR if final else CY}" stroke-opacity=".8"/>'
            s += (dot(x0 + 20, yy - 4, GR, 3) if final else f'<circle cx="{x0+20}" cy="{yy-4}" r="3" fill="{CY}"/>')
            s += T(x0 + 32, yy, it["t"], 13, GR if final else WH, weight="bold" if final else "normal")
            if it.get("sub"):
                s += T(x0 + 32, yy + 15, it["sub"], 10, DIM)
    write("experience.svg", w, h, s)


def tree():
    w, h, t = 860, 450, CFG["tree"]
    s = panel(w, h, "SKILL TREE", CY, "UNLOCKED NODES")
    rx, ry = 430, 64

    def flow(d, color, op=".65"):
        return (f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="1.6" stroke-dasharray="3 5">'
                f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="1.2s" repeatCount="indefinite"/></path>')
    xs = [170, 430, 690]
    for x, b in zip(xs, t["branches"]):
        c = ACC[b["color"]]
        s += flow(f"M{rx} {ry+40}V{ry+60}H{x}V152", c)
        s += flow(f"M{x} 190V{222 + 14 + (len(b['skills'])-1)*36}", c, ".45")
    s += (f'<rect x="{rx-90}" y="{ry}" width="180" height="40" rx="8" fill="{CY}" fill-opacity=".12" stroke="{CY}" stroke-width="2" filter="url(#glow)"/>'
          + T(rx, ry + 26, t["root"], 17, WH, "middle", "bold", 'letter-spacing="4"')
          + T(rx, ry - 6, "ROOT", 9, DIM, "middle", extra='letter-spacing="4"'))
    for x, b in zip(xs, t["branches"]):
        c = ACC[b["color"]]
        s += (f'<rect x="{x-90}" y="152" width="180" height="38" rx="8" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-width="2" filter="url(#soft)"/>'
              + T(x, 177, b["name"], 15, c, "middle", "bold", 'letter-spacing="3"'))
        for k, sk in enumerate(b["skills"]):
            y = 222 + k * 36
            s += (f'<rect x="{x-75}" y="{y}" width="150" height="28" rx="6" fill="{PANEL}" stroke="{c}" stroke-opacity=".8"/>'
                  f'<rect x="{x-75}" y="{y}" width="150" height="28" rx="6" fill="{c}" fill-opacity=".07"/>'
                  + T(x, y + 19, sk, 13, WH, "middle")
                  + f'<circle cx="{x-62}" cy="{y+14}" r="2.5" fill="{c}"/>')
    write("skill-tree.svg", w, h, s)


def side_quests():
    w, h = 860, 232
    cols = list(ACC.values())
    items = CFG["side_quests"]
    s = ""
    for k, (name, desc) in enumerate(items):
        row, col = (0, k) if k < 4 else (1, k - 4)
        x = col * 220 if row == 0 else 110 + col * 220
        y = row * 124
        c = cols[k % 4]
        s += (f'<rect x="{x+1}" y="{y+1}" width="198" height="106" rx="9" fill="{PANEL}" stroke="{c}" stroke-opacity=".7">'
              f'<animate attributeName="stroke-opacity" values=".3;.9;.3" dur="{3.2+k*.35:.2f}s" repeatCount="indefinite"/></rect>'
              f'<rect x="{x+1}" y="{y+1}" width="198" height="106" rx="9" fill="url(#scan)"/>'
              f'<rect x="{x+1}" y="{y+14}" width="3" height="78" fill="{c}" filter="url(#soft)"/>')
        s += T(x + 16, y + 26, f"SIDE QUEST {k+1:02d}", 9, c, extra='letter-spacing="2"')
        lines = textwrap.wrap(name, 21)
        for j, ln in enumerate(lines):
            s += T(x + 16, y + 50 + j * 17, ln, 13, WH, weight="bold")
        s += T(x + 16, y + 94, desc, 8.5, DIM, extra='letter-spacing="1"')
    write("side-quests.svg", w, h, s)


def log():
    w, h = 860, 290
    s = panel(w, h, "EVENT LOG", CY, "undated entries: ----")
    for k, (d, tag, msg, col) in enumerate(CFG["log"]):
        y = 78 + k * 24
        s += (f'<text x="28" y="{y}" font-size="13" xml:space="preserve"><tspan fill="{DIM}">[{esc(d)}]</tspan>'
              f'<tspan fill="{PU}"> \u2192 </tspan><tspan fill="{ACC[col]}" font-weight="bold">{esc(tag)}</tspan>'
              f'<tspan fill="{DIM}"> :: </tspan><tspan fill="{WH}">{esc(msg)}</tspan></text>')
    y = 78 + len(CFG["log"]) * 24
    s += T(28, y, "> ", 13, GR, weight="bold")
    s += f'<rect x="46" y="{y-12}" width="8" height="15" fill="{GR}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    write("player-log.svg", w, h, s)


def terminal():
    w, h, T_, sz = 640, 262, 14.0, 14
    cw = sz * .6
    s = (f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="#050912" stroke="{CY}" stroke-opacity=".6" stroke-width="1.4"/>'
         f'<rect x="1" y="1" width="{w-2}" height="28" rx="10" fill="#0b1426"/><rect x="1" y="18" width="{w-2}" height="11" fill="#0b1426"/>'
         f'<circle cx="20" cy="15" r="4" fill="{PU}"/><circle cx="36" cy="15" r="4" fill="{CY}"/><circle cx="52" cy="15" r="4" fill="{GR}"/>'
         + T(w/2, 19, "dipsita@github \u2014 system_status", 11, DIM, "middle")
         + f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="url(#scan)"/>')
    cmd = "DIPSITA@GITHUB:~$ system_status"
    t, d = typed(24, 64, cmd, GR, sz, .4, T_)
    s += t
    st = .4 + d + .5
    for k, (lab, val, col) in enumerate(CFG["terminal"]["rows"]):
        y = 98 + k * 26
        t1, d1 = typed(24, y, f"{lab:<12}: ", DIM, sz, st, T_)
        t2, d2 = typed(24 + 14 * cw, y, val, ACC[col], sz, st + .35, T_, 'filter="url(#soft)"')
        s += t1 + t2
        last = (k, y, st + .35 + d2, d2, val)
        st += .9
    k, y, s0, d2, val = last
    s += bolt(24 + 14 * cw + len(val) * cw + 12, y - 4, GR, window(s0 + d2 - .1, .3, T_))
    py = 98 + len(CFG["terminal"]["rows"]) * 26 + 6
    t, dd = typed(24, py, "DIPSITA@GITHUB:~$", GR, sz, st + .3, T_)
    s += t
    s += (f'<g opacity="0">{window(st + .3 + dd, .3, T_)}<rect x="{24 + 17*cw + 8}" y="{py-12}" width="9" height="16" fill="{GR}">'
          f'<animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect></g>')
    write("terminal.svg", w, h, s)


def divider():
    w = 860
    s = ('<linearGradient id="gd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff" stop-opacity="0"/>'
         '<stop offset=".35" stop-color="#00f0ff"/><stop offset=".65" stop-color="#b026ff"/><stop offset="1" stop-color="#b026ff" stop-opacity="0"/></linearGradient>'
         f'<rect x="0" y="6" width="{w}" height="2" fill="url(#gd)" opacity=".7"/>'
         f'<polygon points="430,0 438,7 430,14 422,7" fill="{BG}" stroke="{CY}" stroke-width="1.5" filter="url(#soft)"/>'
         f'<circle cy="7" r="3" fill="{WH}" filter="url(#soft)"><animate attributeName="cx" values="0;{w}" dur="7s" repeatCount="indefinite"/>'
         '<animate attributeName="opacity" values="0;1;1;0" dur="7s" repeatCount="indefinite"/></circle>')
    write("divider.svg", w, 14, s)


if __name__ == "__main__":
    for fn in (banner, boot, player_card, mission, stats, attributes, quest, builds, achievements,
               experience, tree, side_quests, log, terminal, divider):
        fn()
    print("assets written:", len(list(OUT.glob("*.svg"))))
