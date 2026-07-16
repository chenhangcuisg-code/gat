"""国风水墨简笔 skill VFX: FLUX ink-wash texture on WHITE paper + INVERSE key (alpha=darkness,
fixed ink color) + RGBA over-compositing motion. Alpha-blend over light bg (NOT additive)."""
import os, math, torch, numpy as np
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import FluxPipeline
from PIL import Image, ImageDraw, ImageFont
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import save_sheet, save_frames, save_tres, ink_key, ink_gif, INK

BASE="/data/chenhang/pixgen_work/vfx/ink"; os.makedirs(BASE,exist_ok=True)
W,H=768,512

def xform(spr,afac,scale,dx,dy,ang):
    im=spr
    if afac!=1.0:
        r,g,b,a=im.split(); a=a.point(lambda v:int(v*afac)); im=Image.merge("RGBA",(r,g,b,a))
    if scale!=1.0:
        nw,nh=max(1,int(W*scale)),max(1,int(H*scale)); im2=im.resize((nw,nh),Image.BILINEAR)
        c=Image.new("RGBA",(W,H),(0,0,0,0)); c.paste(im2,((W-nw)//2,(H-nh)//2)); im=c
    if ang: im=im.rotate(ang,resample=Image.BILINEAR,center=(W//2,H//2))
    if dx or dy:
        c=Image.new("RGBA",(W,H),(0,0,0,0)); c.paste(im,(int(dx),int(dy)),im); im=c
    return im

def spatter(canvas,cx,cy,rad,n,rng,amax=200):
    d=ImageDraw.Draw(canvas)
    for _ in range(n):
        ang=rng.uniform(0,2*math.pi); rr=rad*rng.uniform(0.3,1.1)
        x=int(cx+math.cos(ang)*rr); y=int(cy+math.sin(ang)*rr); s=rng.integers(2,7)
        d.ellipse([x-s,y-s,x+s,y+s],fill=(INK[0],INK[1],INK[2],int(rng.uniform(90,amax))))

def animate(spr,arch,N,rng):
    fr=[]
    for t in range(N):
        p=t/(N-1); c=Image.new("RGBA",(W,H),(0,0,0,0))
        if arch=="projectile":
            env=min(1,p/0.12) if p<0.12 else (max(0,1-(p-0.8)/0.2) if p>0.8 else 1)
            dx=int(W*(-0.30+0.60*p)); ang=18*p
            for lag,dim in [(0.12,0.28),(0.06,0.5)]:
                c=Image.alpha_composite(c,xform(spr,env*dim,0.9,int(W*(-0.30+0.60*(p-lag))),0,ang))
            c=Image.alpha_composite(c,xform(spr,env,0.94,dx,0,ang))
            sp=Image.new("RGBA",(W,H),(0,0,0,0)); spatter(sp,int(W*(0.16+0.60*p)),H//2,40,int(6*env),rng,170)
            c=Image.alpha_composite(c,sp)
        elif arch=="burst":
            ease=1-(1-p)**2; scale=0.4+1.05*ease
            env=min(1,p/0.1) if p<0.1 else max(0,1-(p-0.1)/0.9)
            c=Image.alpha_composite(c,xform(spr,env,scale,0,0,12*p))
            sp=Image.new("RGBA",(W,H),(0,0,0,0)); spatter(sp,W//2,H//2,int(80+230*ease),int(16*env),rng,150)
            c=Image.alpha_composite(c,sp)
        elif arch=="spin":
            ang=360*p; scale=1.0+0.04*math.sin(2*math.pi*p); env=0.85+0.15*math.sin(2*math.pi*p)
            c=Image.alpha_composite(c,xform(spr,env,scale,0,0,ang))
        fr.append(c)
    return fr

EFFECTS=[
 ("ink_jianbo","traditional chinese ink wash painting sumi-e, a single dynamic crescent sword slash brush stroke, bold black ink, splashing ink droplets, xieyi calligraphy, minimalist, few strokes, on white rice paper, high contrast, negative space, monochrome, no color","projectile",5),
 ("ink_burst","traditional chinese ink wash painting sumi-e, an explosive splash of black ink bursting outward, ink splatter droplets radiating, xieyi, minimalist, on white rice paper, high contrast, monochrome, no color","burst",21),
 ("ink_enso","traditional chinese ink wash painting sumi-e, a single zen enso circle brush ring, one bold incomplete black ink stroke, calligraphy, minimalist, on white rice paper, monochrome, no color","spin",8),
]
ARCH={"projectile":(16,14),"burst":(14,16),"spin":(24,18)}

pipe=FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16); pipe.to("cuda")
for name,prompt,arch,seed in EFFECTS:
    out=f"{BASE}/{name}"; os.makedirs(out,exist_ok=True)
    tex=pipe(prompt,num_inference_steps=4,guidance_scale=0.0,height=H,width=W,
             generator=torch.Generator("cuda").manual_seed(seed)).images[0]
    tex.convert("RGB").save(f"{out}/{name}_texture.png")
    spr=ink_key(tex); N,fps=ARCH[arch]; rng=np.random.default_rng(seed)
    fr=animate(spr,arch,N,rng)
    names=save_frames(fr,out,name); save_sheet(fr,f"{out}/{name}_sheet.png")
    ink_gif(fr,f"{out}/{name}_preview.gif"); save_tres(names,f"vfx/ink/{name}",f"{out}/{name}.tres",name,fps)
    print(f"[{name}] {arch} {N}f DONE")
print("INK BATCH DONE")
