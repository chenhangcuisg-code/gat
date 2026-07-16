"""国风水墨风 (RICH, not minimalist) via the PREVIOUS glow pipeline: FLUX luminous-ink-on-BLACK
+ luminance_key + additive glow. Flowing detailed ink-wash that GLOWS."""
import os, math, torch, numpy as np
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import FluxPipeline
from PIL import Image
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

BASE="/data/chenhang/pixgen_work/vfx/inkglow"; os.makedirs(BASE,exist_ok=True)
W,H=768,512

EFFECTS=[
 ("ink_jianbo","a dynamic sweeping crescent sword slash of luminous flowing ink, glowing white and silver ink brush stroke with splashing ink droplets wisps and mist, subtle jade cyan glow, richly detailed dramatic chinese ink wash energy, dynamic motion, pure solid black background, no character","projectile",5),
 ("ink_burst","an explosive splash burst of glowing luminous ink radiating outward, ink tendrils droplets and splatter, white silver ink with warm gold glow, dramatic chinese ink wash, richly detailed intricate, pure solid black background","burst",21),
 ("ink_halo","a glowing circular halo ring of luminous flowing ink brush strokes, chinese ink wash mandala with swirling ink, white silver ink with jade cyan glow, richly detailed intricate, pure solid black background","spin",8),
]
ARCH={"projectile":(16,14),"burst":(14,18),"spin":(24,20)}

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
    return a

def sparks(c,cx,cy,sxr,syr,n,rng,tint):
    for _ in range(n):
        sx=cx+int(rng.normal(0,sxr)); sy=cy+int(rng.normal(0,syr))
        if 2<=sx<W-2 and 2<=sy<H-2:
            b=rng.uniform(120,255); c[sy-1:sy+2,sx-1:sx+2]+=np.array(tint,np.float32)*b/255

def animate(sp,arch,N,rng):
    fr=[]
    for t in range(N):
        p=t/(N-1); c=np.zeros((H,W,3),np.float32)
        if arch=="projectile":
            env=min(1,p/0.1) if p<0.1 else (max(0,1-(p-0.82)/0.18) if p>0.82 else 1)
            dx=int(W*(-0.30+0.60*p)); ang=16*p
            c+=xform(sp,1.15*env,0.92,dx,0,ang)
            for lag,dim in [(0.06,0.45),(0.12,0.22)]:
                c+=xform(sp,1.15*env*dim,0.88,int(W*(-0.30+0.60*(p-lag))),0,ang)
            sparks(c,int(W*(0.18+0.60*p)),H//2,26,50,int(9*env),rng,(200,235,255))
        elif arch=="burst":
            ease=1-(1-p)**2; scale=0.3+1.5*ease
            env=(p/0.12)*1.3 if p<0.12 else max(0,1.3*(1-(p-0.12)/0.88))
            c+=xform(sp,env,scale,0,0,10*p)
            sparks(c,W//2,H//2,int(70+180*ease),int(55+140*ease),int(14*env),rng,(255,235,180))
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
    save_gif(fr,f"{out}/{name}_preview.gif",duration=80); save_tres(names,f"vfx/inkglow/{name}",f"{out}/{name}.tres",name,fps)
    print(f"[{name}] {arch} {N}f DONE")
print("INKGLOW BATCH DONE")
