"""A - PROVE the frames are truly transparent (no background). Composite over checkerboard +
a game scene, both alpha-blend and additive-glow. Plus one animated proof GIF over a scene."""
import os, glob, numpy as np
from PIL import Image, ImageDraw, ImageFont
B="/data/chenhang/pixgen_work/vfx"
W,H=768,512

def checker(sq=32,a=(70,70,78),b=(120,120,130)):
    im=Image.new("RGB",(W,H))
    for y in range(0,H,sq):
        for x in range(0,W,sq):
            im.paste(a if ((x//sq+y//sq)%2==0) else b,(x,y,x+sq,y+sq))
    return np.asarray(im).astype(np.float32)

def scene():  # fake game scene: blue->purple gradient + faint noise
    yy=np.linspace(0,1,H)[:,None]
    r=(20+40*yy); g=(24+18*(1-yy)); bl=(55+70*yy)
    base=np.zeros((H,W,3),np.float32); base[...,0]=r; base[...,1]=g; base[...,2]=bl
    rng=np.random.default_rng(1); base+=rng.normal(0,6,(H,W,3))
    return np.clip(base,0,255)

def brightest(pfx_dir,pfx):
    fs=sorted(glob.glob(f"{pfx_dir}/{pfx}_[0-9][0-9].png")); best=None; bs=-1
    for f in fs:
        im=Image.open(f).convert("RGBA"); s=np.asarray(im.getchannel("A")).sum()
        if s>bs: bs=s; best=im
    return best

def alpha_over(bg,fr):
    a=np.asarray(fr.getchannel("A")).astype(np.float32)[...,None]/255
    rgb=np.asarray(fr.convert("RGB")).astype(np.float32)
    return np.clip(bg*(1-a)+rgb*a,0,255)

def additive(bg,fr):
    a=np.asarray(fr.getchannel("A")).astype(np.float32)[...,None]/255
    rgb=np.asarray(fr.convert("RGB")).astype(np.float32)
    return np.clip(bg+rgb*a,0,255)

EFF=[("jianbo 剑波",f"{B}/p2","p2"),("fireball 火球",f"{B}/batch/fireball","fireball"),
     ("frost_nova 冰霜",f"{B}/batch/frost_nova","frost_nova")]
CK=checker(); SC=scene(); TH=150
cw=int(TH*W/H); PAD=8; LBLc=22; LBLr=120
cols=["checkerboard (alpha)","game scene (alpha-blend)","game scene (ADDITIVE glow)"]
GW=LBLr+3*(cw+PAD)+PAD; GH=LBLc+len(EFF)*(TH+PAD)+PAD
grid=Image.new("RGB",(GW,GH),(12,12,16)); d=ImageDraw.Draw(grid)
try: font=ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",14)
except: font=ImageFont.load_default()
for j,cn in enumerate(cols): d.text((LBLr+j*(cw+PAD),4),cn,fill=(230,230,240),font=font)
for i,(label,dd,pfx) in enumerate(EFF):
    fr=brightest(dd,pfx); y=LBLc+i*(TH+PAD)
    d.text((6,y+TH//2-6),label,fill=(230,230,240),font=font)
    for j,comp in enumerate([alpha_over(CK,fr),alpha_over(SC,fr),additive(SC,fr)]):
        im=Image.fromarray(comp.astype(np.uint8),"RGB").resize((cw,TH),Image.LANCZOS)
        grid.paste(im,(LBLr+j*(cw+PAD),y))
grid.save(f"{B}/transparency_demo.png"); print("TRANSP DEMO", grid.size)

# animated proof: 剑波 additive over scene
fs=sorted(glob.glob(f"{B}/p2/p2_[0-9][0-9].png"))
gif=[Image.fromarray(additive(SC,Image.open(f).convert("RGBA")).astype(np.uint8),"RGB") for f in fs]
gif[0].save(f"{B}/jianbo_on_scene.gif",save_all=True,append_images=gif[1:],duration=70,loop=0)
print("SCENE GIF done")
