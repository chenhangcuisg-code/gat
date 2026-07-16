"""国风水墨发光 contact sheet on dark bg: 1 row/effect, 6 sampled frames (additive glow reads on dark)."""
import os, glob
from PIL import Image, ImageDraw, ImageFont
B="/data/chenhang/pixgen_work/vfx/inkglow"; BG=(14,14,18)
ORDER=[("ink_jianbo","剑波 slash (projectile)"),("ink_burst","墨爆 splash (burst)"),
       ("ink_halo","光环 halo (spin loop)"),("ink_dragon","墨龙 dragon [AnimateDiff]"),
       ("ink_swirl","墨漩 swirl [AnimateDiff]")]
TH=120; PAD=6; NCOL=6; LBL=170
rows=[]
for name,label in ORDER:
    fs=sorted(glob.glob(f"{B}/{name}/{name}_[0-9][0-9].png"))
    if not fs: continue
    ims=[]
    for f in fs:
        im=Image.open(f).convert("RGBA"); base=Image.new("RGB",im.size,BG); base.paste(im,(0,0),im); ims.append(base)
    idx=[round(k*(len(ims)-1)/(NCOL-1)) for k in range(NCOL)]
    rows.append((label,[ims[i] for i in idx],ims[0].size))
cw=int(TH*rows[0][2][0]/rows[0][2][1])
GW=LBL+NCOL*(cw+PAD)+PAD; GH=PAD+len(rows)*(TH+PAD)
sheet=Image.new("RGB",(GW,GH),(8,8,10)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",15)
except: font=ImageFont.load_default()
for i,(label,frs,_) in enumerate(rows):
    y=PAD+i*(TH+PAD); d.text((6,y+TH//2-8),label,fill=(235,235,245),font=font)
    for j,im in enumerate(frs): sheet.paste(im.resize((cw,TH),Image.LANCZOS),(LBL+j*(cw+PAD),y))
sheet.save(f"{B}/inkglow_compare.png"); print("INKGLOW COMPARE", sheet.size)
