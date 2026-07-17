#!/usr/bin/env python3
"""Generate GAT's GitHub social-preview card (the 1280x640 link-unfurl image).

Same dark neon-pixel identity as the README banner, sized to GitHub's social spec so
the repo looks sharp when shared on X / Discord / Slack / HN.
    python tools/make_social.py docs/img/social-card.svg
Render:  node /tmp/svgrender/render.js docs/img/social-card.svg docs/img/social-card.png 1280
"""
import sys

BG_TOP, BG_BOT = "#070b16", "#0b1524"
GRID = "#16263f"
CYAN, BLUE, VIOLET, MAGENTA = "#34e6f2", "#3b82f6", "#a855f7", "#d946ef"
GOLD = "#f5b942"
DIM, BRIGHT = "#6f8fbf", "#dbeafe"
W, H = 1280, 640

FONT = {
    "G": ["01110","10001","10000","10111","10001","10001","01110"],
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
}

def pixel_word(word, x, y, px, fill_id):
    rects, cx = [], x
    for ch in word:
        glyph = FONT[ch]
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    rects.append(
                        f'<rect x="{cx + c*px}" y="{y + r*px}" width="{px-1}" height="{px-1}" '
                        f'rx="1" fill="url(#{fill_id})"/>')
        cx += (len(glyph[0]) + 1) * px
    return "\n".join(rects), cx - x - px

def chip(x, y, w, h, label, accent):
    return f'''<g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#0e1b30" stroke="{accent}" stroke-width="1.5"/>
    <rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{accent}"/>
    <text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-family="'Consolas','DejaVu Sans Mono',monospace"
          font-size="15" font-weight="700" letter-spacing="1" fill="{BRIGHT}">{label}</text>
  </g>'''

def pill(x, y, w, label, accent):
    return f'''<g>
    <rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="#0e1b30" stroke="{accent}" stroke-width="1.5"/>
    <circle cx="{x+18}" cy="{y+17}" r="5" fill="{accent}"/>
    <text x="{x+34}" y="{y+22}" font-family="'Consolas',monospace" font-size="15" font-weight="700"
          letter-spacing="0.5" fill="{BRIGHT}">{label}</text>
  </g>'''

def build():
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="monospace">']
    out.append(f'''<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOT}"/>
    </linearGradient>
    <linearGradient id="wm" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="0.55" stop-color="{BLUE}"/><stop offset="1" stop-color="{VIOLET}"/>
    </linearGradient>
    <radialGradient id="orbC" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.5"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="orbV" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.5"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="24"/></filter>
  </defs>''')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<circle cx="200" cy="90" r="300" fill="url(#orbC)" filter="url(#soft)"/>')
    out.append(f'<circle cx="1120" cy="560" r="320" fill="url(#orbV)" filter="url(#soft)"/>')
    dots = []
    for gy in range(14, H, 30):
        for gx in range(14, W, 30):
            dots.append(f'<rect x="{gx}" y="{gy}" width="2" height="2" fill="{GRID}"/>')
    out.append('<g opacity="0.6">' + "".join(dots) + '</g>')
    out.append(f'<rect x="0" y="0" width="{W}" height="3" fill="{CYAN}" opacity="0.55"/>')
    out.append(f'<rect x="0" y="{H-3}" width="{W}" height="3" fill="{VIOLET}" opacity="0.55"/>')

    # lockup: emblem + GAT wordmark, centered as a unit
    px = 30
    _, wmw = pixel_word("GAT", 0, 0, px, "wm")
    u = 15
    emblem_w = 5 * u
    gap = 46
    lockup_w = emblem_w + gap + wmw
    lx = (W - lockup_w) / 2
    ecx, ecy = lx + emblem_w/2, 150
    diamond = [(0,-2),(-1,-1),(0,-1),(1,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1),(0,2)]
    em = []
    for dx, dy in diamond:
        col = CYAN if (dx+dy) % 2 == 0 else VIOLET
        em.append(f'<rect x="{ecx+dx*u-u/2}" y="{ecy+dy*u-u/2}" width="{u-1}" height="{u-1}" rx="1" fill="{col}"/>')
    for ox, oy, oc in [(-3.4,-3.4,GOLD),(3.4,-3.4,CYAN),(3.4,3.4,VIOLET),(-3.4,3.4,BLUE)]:
        em.append(f'<rect x="{ecx+ox*u-4}" y="{ecy+oy*u-4}" width="8" height="8" rx="1" fill="{oc}"/>')
    out.append('<g filter="url(#glow)">' + "".join(em) + '</g>')
    wm_x = lx + emblem_w + gap
    rects, _ = pixel_word("GAT", wm_x, ecy - 7*px/2, px, "wm")
    out.append(f'<g filter="url(#glow)">{rects}</g>')

    # subtitle + one-line pitch
    out.append(f'<text x="{W/2}" y="278" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="26" font-weight="700" letter-spacing="11" fill="{CYAN}">GODOT · AGENT · TEAM</text>')
    out.append(f'<text x="{W/2}" y="320" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="19" letter-spacing="1" fill="{BRIGHT}">a full-cycle Godot game-dev agent — one-line idea ▸ running, verified build</text>')

    # feature pills
    pills = [("style-locked", GOLD, 168), ("self-evolving", VIOLET, 178), ("Claude + Codex", CYAN, 190)]
    pgap = 22
    ptot = sum(w for _,_,w in pills) + pgap*(len(pills)-1)
    ppx = (W - ptot) / 2
    py = 356
    for lab, acc, w in pills:
        out.append(pill(ppx, py, w, lab, acc)); ppx += w + pgap

    # pipeline chips
    chips = [("DESIGN", CYAN), ("STYLE-LOCK", GOLD), ("ASSETS", MAGENTA), ("IMPLEMENT", BLUE), ("VERIFY", "#34d399")]
    cw, cgap, ch, yy = 150, 34, 40, 452
    total = len(chips)*cw + (len(chips)-1)*cgap
    sx = (W - total) / 2
    for i in range(len(chips)-1):
        lxc = sx + (i+1)*cw + i*cgap
        out.append(f'<rect x="{lxc}" y="{yy+ch/2-1}" width="{cgap}" height="2" fill="{DIM}"/>')
        out.append(f'<polygon points="{lxc+cgap-7},{yy+ch/2-5} {lxc+cgap},{yy+ch/2} {lxc+cgap-7},{yy+ch/2+5}" fill="{CYAN}"/>')
    for i, (lab, acc) in enumerate(chips):
        out.append(chip(sx + i*(cw+cgap), yy, cw, ch, lab, acc))

    # bottom url
    out.append(f'<text x="{W/2}" y="556" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="17" letter-spacing="2" fill="{DIM}">github.com/chenhangcuisg-code/gat</text>')
    out.append('</svg>')
    return "\n".join(out)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "social-card.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote", path)
