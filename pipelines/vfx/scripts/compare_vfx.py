"""Build a static contact sheet: 3 rows (P1/P2/P3), 6 evenly-sampled frames each, on dark bg."""
import os, glob
from PIL import Image, ImageDraw, ImageFont
BASE="/data/chenhang/pixgen_work/vfx"; BG=(16,16,22)
rows=[("P1  AnimateDiff txt2vid  (pure generative motion)","p1"),
      ("P2  FLUX texture + procedural  (deterministic, controllable)","p2"),
      ("P3  SDXL controlled img2img  (AI re-paint on moving control)","p3")]
TH=150; PAD=8; NCOL=6; LBL=26
def load(pfx):
    fs=sorted(glob.glob(f"{BASE}/{pfx}/{pfx}_[0-9][0-9].png"))
    ims=[]
    for f in fs:
        im=Image.open(f).convert("RGBA")
        base=Image.new("RGB",im.size,BG); base.paste(im,(0,0),im); ims.append(base)
    return ims
sel={}
for _,p in rows:
    ims=load(p)
    if not ims: sel[p]=[]; continue
    idx=[round(k*(len(ims)-1)/(NCOL-1)) for k in range(NCOL)]
    sel[p]=[ims[i] for i in idx]
cw=int(TH*ims[0].size[0]/ims[0].size[1]) if ims else TH
rowH=LBL+TH+PAD; W=PAD+NCOL*(cw+PAD); H=PAD+len(rows)*(rowH)
sheet=Image.new("RGB",(W,H),(8,8,10)); d=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",15)
except: font=ImageFont.load_default()
y=PAD
for label,p in rows:
    d.text((PAD,y),label,fill=(230,230,240),font=font); yy=y+LBL
    x=PAD
    for im in sel[p]:
        im2=im.resize((cw,TH),Image.LANCZOS); sheet.paste(im2,(x,yy)); x+=cw+PAD
    y+=rowH
sheet.save(f"{BASE}/vfx_compare.png"); print("COMPARE DONE", sheet.size)
