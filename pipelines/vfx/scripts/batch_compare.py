"""Contact sheet of ALL new effects: 1 row per effect, 6 sampled frames on dark bg."""
import os, glob
from PIL import Image, ImageDraw, ImageFont
B="/data/chenhang/pixgen_work/vfx/batch"; BG=(16,16,22)
ORDER=["fireball","lightning","frost_nova","heal_aura","explosion","arcane_circle","adiff_explosion","adiff_flame_swirl"]
TH=120; PAD=6; NCOL=6; LBL=150
rows=[]
for name in ORDER:
    fs=sorted(glob.glob(f"{B}/{name}/{name}_[0-9][0-9].png"))
    if not fs: continue
    ims=[]
    for f in fs:
        im=Image.open(f).convert("RGBA"); base=Image.new("RGB",im.size,BG); base.paste(im,(0,0),im); ims.append(base)
    idx=[round(k*(len(ims)-1)/(NCOL-1)) for k in range(NCOL)]
    rows.append((name,[ims[i] for i in idx],ims[0].size))
cw=int(TH*rows[0][2][0]/rows[0][2][1])
GW=LBL+NCOL*(cw+PAD)+PAD; GH=PAD+len(rows)*(TH+PAD)
sheet=Image.new("RGB",(GW,GH),(8,8,10)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",15)
except: font=ImageFont.load_default()
LABELS={"fireball":"fireball 火球 (projectile)","lightning":"lightning 闪电 (bolt)","frost_nova":"frost nova 冰霜 (burst)",
 "heal_aura":"heal aura 治疗 (aura loop)","explosion":"explosion 爆炸 (burst)","arcane_circle":"arcane 法阵 (spin loop)",
 "adiff_explosion":"explosion [AnimateDiff]","adiff_flame_swirl":"flame swirl [AnimateDiff]"}
for i,(name,frs,_) in enumerate(rows):
    y=PAD+i*(TH+PAD); d.text((6,y+TH//2-8),LABELS.get(name,name),fill=(235,235,245),font=font)
    for j,im in enumerate(frs): sheet.paste(im.resize((cw,TH),Image.LANCZOS),(LBL+j*(cw+PAD),y))
sheet.save(f"{B}/batch_compare.png"); print("BATCH COMPARE", sheet.size)
