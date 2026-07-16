"""Ink contact sheet over rice-paper bg: 1 row per ink effect, 6 sampled frames + also show
the raw FLUX ink texture. Proves transparency (composited over paper, no black box)."""
import os, glob, numpy as np
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import paper_bg
from PIL import Image, ImageDraw, ImageFont
B="/data/chenhang/pixgen_work/vfx/ink"
ORDER=[("ink_jianbo","剑波 slash (projectile)"),("ink_burst","墨爆 splash (burst)"),
       ("ink_enso","圆相 enso (spin loop)"),("ink_diffuse","墨扩散 [AnimateDiff]"),
       ("ink_dragon","墨龙 dragon [AnimateDiff]")]
TH=120; PAD=6; NCOL=6; LBL=170
rows=[]
for name,label in ORDER:
    fs=sorted(glob.glob(f"{B}/{name}/{name}_[0-9][0-9].png"))
    if not fs: continue
    bg=paper_bg(*Image.open(fs[0]).size).convert("RGBA")
    ims=[Image.alpha_composite(bg,Image.open(f).convert("RGBA")).convert("RGB") for f in fs]
    idx=[round(k*(len(ims)-1)/(NCOL-1)) for k in range(NCOL)]
    rows.append((label,[ims[i] for i in idx],ims[0].size))
cw=int(TH*rows[0][2][0]/rows[0][2][1])
GW=LBL+NCOL*(cw+PAD)+PAD; GH=PAD+len(rows)*(TH+PAD)
sheet=Image.new("RGB",(GW,GH),(30,28,26)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",15)
except: font=ImageFont.load_default()
for i,(label,frs,_) in enumerate(rows):
    y=PAD+i*(TH+PAD); d.text((6,y+TH//2-8),label,fill=(240,238,232),font=font)
    for j,im in enumerate(frs): sheet.paste(im.resize((cw,TH),Image.LANCZOS),(LBL+j*(cw+PAD),y))
sheet.save(f"{B}/ink_compare.png"); print("INK COMPARE", sheet.size)
