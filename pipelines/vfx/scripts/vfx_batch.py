"""B - other skill effects: FLUX texture (per-effect prompt, black bg) + parametric procedural
motion archetype. One script -> N effects. Reuses the P2 (winning) paradigm."""
import os, math, torch, numpy as np
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import FluxPipeline
from PIL import Image
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

BASE="/data/chenhang/pixgen_work/vfx/batch"; os.makedirs(BASE,exist_ok=True)
W,H=768,512

EFFECTS=[
 ("fireball","a blazing fireball projectile, bright orange yellow flames with white-hot core, fiery embers and smoke trail, isolated on pure solid black background, centered, game vfx effect, no character","projectile",3),
 ("lightning","a jagged vertical bolt of lightning, brilliant white core with purple and electric blue arcs, crackling branches, isolated on pure solid black background, centered, game vfx effect","bolt",11),
 ("frost_nova","an icy frost nova, radiating pale blue and white ice crystal shards and frozen mist bursting outward, sharp crystalline spikes, pure solid black background, centered, game vfx effect","burst",21),
 ("heal_aura","a glowing healing aura, soft green and golden holy light ring, sparkling ascending particles, circular radiant glow, pure solid black background, centered, game vfx effect","aura",7),
 ("explosion","a fiery explosion blast, orange red fireball with bright yellow white core, flying debris and smoke, pure solid black background, centered, game vfx effect","burst",42),
 ("arcane_circle","a mystical magic summoning circle, glowing cyan and gold arcane runes and concentric geometric rings, top-down view, pure solid black background, centered, game vfx effect","spin",15),
]
ARCH={"projectile":(16,14),"bolt":(12,16),"burst":(14,18),"aura":(16,14),"spin":(24,20)}

def xform(sp,bright,scale,dx,dy,ang):
    im=Image.fromarray(np.clip(sp*bright,0,255).astype(np.uint8),"RGB")
    if scale!=1.0:
        nw,nh=max(1,int(W*scale)),max(1,int(H*scale)); im=im.resize((nw,nh),Image.BILINEAR)
        c=Image.new("RGB",(W,H),(0,0,0)); c.paste(im,((W-nw)//2,(H-nh)//2)); im=c
    if ang: im=im.rotate(ang,resample=Image.BILINEAR,center=(W//2,H//2))
    a=np.asarray(im).astype(np.float32)
    if dx or dy:
        a=np.roll(a,(int(dy),int(dx)),axis=(0,1))
        if dx>0:a[:,:int(dx)]=0
        elif dx<0:a[:,int(dx):]=0
        if dy>0:a[:int(dy),:]=0
        elif dy<0:a[int(dy):,:]=0
    return a

def sparks(canvas,cx,cy,sxr,syr,n,rng,tint):
    for _ in range(n):
        sx=cx+int(rng.normal(0,sxr)); sy=cy+int(rng.normal(0,syr))
        if 2<=sx<W-2 and 2<=sy<H-2:
            b=rng.uniform(120,255); canvas[sy-1:sy+2,sx-1:sx+2]+=np.array(tint,np.float32)*b/255

def animate(sp,arch,N,rng):
    fr=[]
    for t in range(N):
        p=t/(N-1); c=np.zeros((H,W,3),np.float32)
        if arch=="projectile":
            env=min(1,p/0.1) if p<0.1 else (max(0,1-(p-0.85)/0.15) if p>0.85 else 1)
            dx=int(W*(-0.32+0.64*p)); ang=25*p
            c+=xform(sp,1.15*env,0.9,dx,0,ang)
            for lag,dim in [(0.06,0.42),(0.12,0.2)]:
                c+=xform(sp,1.15*env*dim,0.86,int(W*(-0.32+0.64*(p-lag))),0,ang)
            sparks(c,int(W*(0.18+0.64*p)),H//2,22,44,int(8*env),rng,(255,200,120))
        elif arch=="burst":
            ease=1-(1-p)**2; scale=0.25+1.5*ease
            env=(p/0.12)*1.3 if p<0.12 else max(0,1.3*(1-(p-0.12)/0.88))
            c+=xform(sp,env,scale,0,0,10*p)
            sparks(c,W//2,H//2,int(70+180*ease),int(55+140*ease),int(14*env),rng,(255,190,110))
        elif arch=="bolt":
            flick=0.35+0.65*abs(math.sin(p*math.pi*3.5))*rng.uniform(0.7,1.1)
            jx=int(rng.normal(0,6))
            c+=xform(sp,min(1.4,1.1*flick),1.0,jx,0,0)
            sparks(c,W//2,H//2,30,H//3,int(6*flick),rng,(210,190,255))
        elif arch=="aura":
            scale=1.0+0.13*math.sin(2*math.pi*p); ang=360*p
            env=0.9+0.1*math.sin(2*math.pi*p)
            c+=xform(sp,env,scale,0,0,ang)
            for k in range(6):
                sy=int(H*0.7-(H*0.5)*((p+k/6)%1)); sx=int(W*0.5+math.sin((p+k/6)*6)*W*0.18)
                if 2<=sx<W-2 and 2<=sy<H-2: c[sy-1:sy+2,sx-1:sx+2]+=np.array([120,255,150],np.float32)
        elif arch=="spin":
            ang=360*p; scale=1.0+0.05*math.sin(2*math.pi*p); env=0.82+0.18*math.sin(2*math.pi*2*p)
            c+=xform(sp,env,scale,0,0,ang)
        fr.append(luminance_key(Image.fromarray(np.clip(c,0,255).astype(np.uint8),"RGB")))
    return fr

pipe=FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16); pipe.to("cuda")
for name,prompt,arch,seed in EFFECTS:
    out=f"{BASE}/{name}"; os.makedirs(out,exist_ok=True)
    tex=pipe(prompt,num_inference_steps=4,guidance_scale=0.0,height=H,width=W,
             generator=torch.Generator("cuda").manual_seed(seed)).images[0]
    tex.convert("RGB").save(f"{out}/{name}_texture.png")
    N,fps=ARCH[arch]; rng=np.random.default_rng(seed)
    fr=animate(np.asarray(tex.convert("RGB")).astype(np.float32),arch,N,rng)
    names=save_frames(fr,out,name); save_sheet(fr,f"{out}/{name}_sheet.png")
    save_gif(fr,f"{out}/{name}_preview.gif",duration=80); save_tres(names,f"vfx/batch/{name}",f"{out}/{name}.tres",name,fps)
    print(f"[{name}] {arch} {N}f DONE")
print("BATCH DONE")
