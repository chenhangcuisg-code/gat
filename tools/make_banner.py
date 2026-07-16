#!/usr/bin/env python3
"""Generate GAT's README hero banner as a tech-pixel SVG.

Dark neon aesthetic: hand-built pixel wordmark (no font needed), circuit pipeline,
glow filters, faint pixel grid. Rendered to PNG via @resvg/resvg-js for GitHub.
    python tools/make_banner.py docs/img/banner.svg
"""
import sys

# ---- palette ----
BG_TOP, BG_BOT = "#070b16", "#0b1524"
GRID = "#16263f"
CYAN, BLUE, VIOLET, MAGENTA = "#34e6f2", "#3b82f6", "#a855f7", "#d946ef"
GOLD = "#f5b942"
DIM, BRIGHT = "#6f8fbf", "#dbeafe"

W, H = 1200, 374

# ---- 5x7 pixel font for the letters we need ----
FONT = {
    "G": ["01110","10001","10000","10111","10001","10001","01110"],
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
}

def pixel_word(word, x, y, px, fill_id):
    rects = []
    cx = x
    for ch in word:
        glyph = FONT[ch]
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    rects.append(
                        f'<rect x="{cx + c*px}" y="{y + r*px}" width="{px-1}" height="{px-1}" '
                        f'rx="1" fill="url(#{fill_id})"/>')
        cx += (len(glyph[0]) + 1) * px
    width = cx - x - px
    return "\n".join(rects), width

def chip(x, y, w, h, label, accent):
    return f'''
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0e1b30" stroke="{accent}" stroke-width="1.5"/>
    <rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{accent}"/>
    <rect x="{x+7}" y="{y+h-9}" width="{w-14}" height="2" rx="1" fill="{accent}" opacity="0.35"/>
    <text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-family="'Consolas','DejaVu Sans Mono',monospace"
          font-size="13" font-weight="700" letter-spacing="1" fill="{BRIGHT}">{label}</text>
  </g>'''

def build():
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="monospace">')
    # defs
    out.append(f'''<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOT}"/>
    </linearGradient>
    <linearGradient id="wm" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="0.55" stop-color="{BLUE}"/><stop offset="1" stop-color="{VIOLET}"/>
    </linearGradient>
    <radialGradient id="orbC" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.55"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="orbV" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.5"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="18"/></filter>
  </defs>''')
    # bg + glow orbs
    out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    out.append(f'<circle cx="180" cy="70" r="220" fill="url(#orbC)" filter="url(#soft)"/>')
    out.append(f'<circle cx="1040" cy="300" r="240" fill="url(#orbV)" filter="url(#soft)"/>')
    # faint pixel grid
    dots = []
    for gy in range(12, H, 26):
        for gx in range(12, W, 26):
            dots.append(f'<rect x="{gx}" y="{gy}" width="2" height="2" fill="{GRID}"/>')
    out.append('<g opacity="0.6">' + "".join(dots) + '</g>')
    # neon hairlines
    out.append(f'<rect x="0" y="0" width="{W}" height="2" fill="{CYAN}" opacity="0.5"/>')
    out.append(f'<rect x="0" y="{H-2}" width="{W}" height="2" fill="{VIOLET}" opacity="0.5"/>')

    # ---- emblem: pixel diamond core + orbit dots ----
    ecx, ecy, u = 405, 132, 11
    diamond = [(0,-2),(-1,-1),(0,-1),(1,-1),(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,1),(0,1),(1,1),(0,2)]
    em = []
    for dx, dy in diamond:
        col = CYAN if (dx+dy) % 2 == 0 else VIOLET
        em.append(f'<rect x="{ecx+dx*u-u/2}" y="{ecy+dy*u-u/2}" width="{u-1}" height="{u-1}" rx="1" fill="{col}"/>')
    # orbit pixels
    for ox, oy, oc in [(-4,-4,GOLD),(4,-4,CYAN),(4,4,VIOLET),(-4,4,BLUE)]:
        em.append(f'<rect x="{ecx+ox*u-3}" y="{ecy+oy*u-3}" width="6" height="6" rx="1" fill="{oc}"/>')
    out.append(f'<g filter="url(#glow)">' + "".join(em) + '</g>')

    # ---- wordmark GAT ----
    wm_x, wm_y, px = 470, 62, 20
    rects, wmw = pixel_word("GAT", wm_x, wm_y, px, "wm")
    out.append(f'<g filter="url(#glow)">{rects}</g>')

    # ---- subtitle + tagline (centered under lockup) ----
    cx = (405 + wm_x + wmw) / 2 - 20
    out.append(f'<text x="{cx}" y="238" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="20" font-weight="700" letter-spacing="8" fill="{CYAN}">GODOT · AGENT · TEAM</text>')
    out.append(f'<text x="{cx}" y="266" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="13.5" letter-spacing="1.5" fill="{DIM}">full-cycle game-dev agent — design ▸ implementation</text>')

    # ---- pipeline circuit strip ----
    chips = [("DESIGN", CYAN), ("STYLE-LOCK", GOLD), ("ASSETS", MAGENTA), ("IMPLEMENT", BLUE), ("VERIFY", "#34d399")]
    cw, gap, ch, yy = 122, 30, 34, 300
    total = len(chips)*cw + (len(chips)-1)*gap
    sx = (W - total) / 2
    # connectors
    for i in range(len(chips)-1):
        lx = sx + (i+1)*cw + i*gap
        out.append(f'<rect x="{lx}" y="{yy+ch/2-1}" width="{gap}" height="2" fill="{DIM}"/>')
        out.append(f'<polygon points="{lx+gap-6},{yy+ch/2-4} {lx+gap},{yy+ch/2} {lx+gap-6},{yy+ch/2+4}" fill="{CYAN}"/>')
    for i, (lab, acc) in enumerate(chips):
        x = sx + i*(cw+gap)
        out.append(chip(x, yy, cw, ch, lab, acc))
    # evolve return loop label
    out.append(f'<text x="{W/2}" y="352" text-anchor="middle" font-family="\'Consolas\',monospace" '
               f'font-size="11" letter-spacing="3" fill="{VIOLET}">↺  S E L F - E V O L V I N G   ·   S T Y L E - L O C K E D  ↺</text>')

    out.append('</svg>')
    return "\n".join(out)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "banner.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote", path)
