#!/usr/bin/env python3
"""Generate a tech-pixel explainer for GAT's style-lock feature.
    python tools/make_stylelock.py docs/img/style-lock.svg
"""
import sys

BG_TOP, BG_BOT = "#070b16", "#0b1524"
GRID = "#16263f"
CYAN, BLUE, VIOLET, MAGENTA = "#34e6f2", "#3b82f6", "#a855f7", "#d946ef"
GOLD, GREEN, RED = "#f5b942", "#34d399", "#f43f5e"
DIM, BRIGHT = "#6f8fbf", "#dbeafe"
# the "locked palette" — every on-style asset only uses these
LOCK_PAL = ["#1A1712", "#C1332B", "#6B7C6E", "#8A6D3B", "#F2E9D8"]

W, H = 1040, 300

def gem(cx, cy, u, cols):
    """a small pixel diamond gem from a color list (cycled)."""
    cells = [(0,-2),(-1,-1),(0,-1),(1,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1),(0,2)]
    out = []
    for i,(dx,dy) in enumerate(cells):
        out.append(f'<rect x="{cx+dx*u-u/2:.0f}" y="{cy+dy*u-u/2:.0f}" width="{u-1}" height="{u-1}" rx="1" fill="{cols[i%len(cols)]}"/>')
    return "".join(out)

def build():
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="monospace">')
    o.append(f'''<defs>
      <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOT}"/></linearGradient>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>''')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    dots = "".join(f'<rect x="{gx}" y="{gy}" width="2" height="2" fill="{GRID}"/>'
                   for gy in range(12,H,26) for gx in range(12,W,26))
    o.append(f'<g opacity="0.55">{dots}</g>')
    o.append(f'<rect x="0" y="0" width="{W}" height="2" fill="{GOLD}" opacity="0.5"/>')
    o.append(f'<rect x="0" y="{H-2}" width="{W}" height="2" fill="{VIOLET}" opacity="0.45"/>')

    # title
    o.append(f'<text x="34" y="42" font-family="\'Consolas\',monospace" font-size="20" font-weight="700" '
             f'letter-spacing="2" fill="{BRIGHT}">STYLE-LOCK <tspan fill="{GOLD}">🔒</tspan></text>')
    o.append(f'<text x="34" y="66" font-family="\'Consolas\',monospace" font-size="13" letter-spacing="1" '
             f'fill="{DIM}">one style, enforced forever — every asset obeys the frozen contract</text>')

    # 1) subject box
    sx, sy = 34, 108
    o.append(f'<rect x="{sx}" y="{sy}" width="176" height="86" rx="8" fill="#0e1b30" stroke="{CYAN}" stroke-width="1.5"/>')
    o.append(f'<text x="{sx+14}" y="{sy+24}" font-family="\'Consolas\',monospace" font-size="11" letter-spacing="2" fill="{CYAN}">YOU WRITE ONLY</text>')
    o.append(f'<text x="{sx+14}" y="{sy+52}" font-family="\'Consolas\',monospace" font-size="15" font-weight="700" fill="{BRIGHT}">"a healing</text>')
    o.append(f'<text x="{sx+14}" y="{sy+72}" font-family="\'Consolas\',monospace" font-size="15" font-weight="700" fill="{BRIGHT}"> gourd"</text>')
    o.append(f'<text x="{sx+14}" y="{sy+96}" font-family="\'Consolas\',monospace" font-size="10.5" fill="{DIM}">the subject — never the style</text>')

    def arrow(x1, x2, y, col):
        return (f'<rect x="{x1}" y="{y-1}" width="{x2-x1}" height="2" fill="{DIM}"/>'
                f'<polygon points="{x2-7},{y-5} {x2},{y} {x2-7},{y+5}" fill="{col}"/>')
    o.append(arrow(214, 250, 151, GOLD))

    # 2) contract card with locked palette
    cx0, cy0, cw, chh = 254, 82, 250, 150
    o.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{chh}" rx="10" fill="#0f1c2f" stroke="{GOLD}" stroke-width="2"/>')
    o.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="5" rx="2" fill="{GOLD}"/>')
    o.append(f'<text x="{cx0+16}" y="{cy0+30}" font-family="\'Consolas\',monospace" font-size="13" font-weight="700" letter-spacing="1" fill="{GOLD}">STYLE CONTRACT 🔒</text>')
    o.append(f'<text x="{cx0+16}" y="{cy0+50}" font-family="\'Consolas\',monospace" font-size="10.5" fill="{DIM}">frozen · versioned · re-lock only</text>')
    # palette swatches
    pw = 40
    for i,c in enumerate(LOCK_PAL):
        px = cx0+16+i*pw
        o.append(f'<rect x="{px}" y="{cy0+62}" width="{pw-6}" height="24" rx="3" fill="{c}" stroke="#000" stroke-opacity="0.3"/>')
    o.append(f'<text x="{cx0+16}" y="{cy0+108}" font-family="\'Consolas\',monospace" font-size="11" fill="{BRIGHT}">prefix + subject + suffix</text>')
    o.append(f'<text x="{cx0+16}" y="{cy0+126}" font-family="\'Consolas\',monospace" font-size="11" fill="{BRIGHT}">+ negative · seed · ref-image</text>')

    o.append(arrow(508, 546, 157, GREEN))

    # 3) audit gate
    gx, gy, gw, gh2 = 550, 128, 120, 58
    o.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh2}" rx="8" fill="#0e1b30" stroke="{GREEN}" stroke-width="1.5"/>')
    o.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="4" rx="2" fill="{GREEN}"/>')
    o.append(f'<text x="{gx+gw/2}" y="{gy+26}" text-anchor="middle" font-family="\'Consolas\',monospace" font-size="12.5" font-weight="700" fill="{BRIGHT}">AUDIT ▣</text>')
    o.append(f'<text x="{gx+gw/2}" y="{gy+44}" text-anchor="middle" font-family="\'Consolas\',monospace" font-size="9.5" fill="{DIM}">palette·res·bg</text>')

    o.append(arrow(674, 706, 157, GREEN))

    # 4) outputs — matching family (PASS)
    fam_cols = [LOCK_PAL[0], LOCK_PAL[1], LOCK_PAL[4]]
    for i,gxp in enumerate([740, 800, 860, 920]):
        o.append(f'<g filter="url(#glow)">{gem(gxp, 118, 8, fam_cols)}</g>')
    o.append(f'<text x="830" y="162" text-anchor="middle" font-family="\'Consolas\',monospace" font-size="12" font-weight="700" fill="{GREEN}">✓ ON-STYLE FAMILY</text>')
    # rejected (FAIL) + regenerate loop
    o.append(f'<g opacity="0.9">{gem(770, 214, 8, ["#22d3ee","#a3e635","#f472b6"])}</g>')
    o.append(f'<text x="770" y="196" text-anchor="middle" font-family="\'Consolas\',monospace" font-size="16" font-weight="700" fill="{RED}">✗</text>')
    o.append(f'<text x="812" y="212" font-family="\'Consolas\',monospace" font-size="11" font-weight="700" fill="{RED}">off-style</text>')
    o.append(f'<text x="812" y="228" font-family="\'Consolas\',monospace" font-size="10.5" fill="{DIM}">→ regenerate, never ship</text>')
    # curved regenerate arrow from reject back to gate
    o.append(f'<path d="M 748 214 C 640 240, 600 210, 600 190" fill="none" stroke="{RED}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    o.append(f'<polygon points="604,196 599,186 594,196" fill="{RED}"/>')

    o.append('</svg>')
    return "\n".join(o)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "style-lock.svg"
    open(path, "w", encoding="utf-8").write(build())
    print("wrote", path)
