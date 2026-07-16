"""P2 - FLUX texture + procedural motion: AI paints ONE slash texture, code animates it.
Deterministic, perfectly loopable/controllable -> the production game-asset route."""
import os, math, torch, numpy as np
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import FluxPipeline
from PIL import Image
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

OUT="/data/chenhang/pixgen_work/vfx/p2"; os.makedirs(OUT,exist_ok=True)
W,H,N=768,512,18

# --- 1. AI texture: a single crescent sword-wave, black bg ---
pipe=FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16); pipe.to("cuda")
prompt=("a single glowing crescent-shaped sword energy slash wave, sharp curved plasma blade of light, "
        "brilliant cyan and white core with electric blue edges, sparks flying, motion energy, "
        "isolated on pure solid black background, centered, high contrast, game vfx effect texture, no character")
tex=pipe(prompt, num_inference_steps=4, guidance_scale=0.0, height=H, width=W,
         generator=torch.Generator("cuda").manual_seed(5)).images[0]
tex.convert("RGB").save(f"{OUT}/p2_texture.png")
del pipe; torch.cuda.empty_cache()

# --- 2. procedural motion (CPU) ---
sprite = np.asarray(tex.convert("RGB")).astype(np.float32)           # HxWx3 glow on black
rng = np.random.default_rng(7)

def xform(bright, scale, dx, ang):
    """scale/rotate/translate the sprite, return HxWx3 float additive layer."""
    im = Image.fromarray(np.clip(sprite*bright,0,255).astype(np.uint8),"RGB")
    if scale!=1.0:
        nw,nh=int(W*scale),int(H*scale); im=im.resize((nw,nh),Image.BILINEAR)
        c=Image.new("RGB",(W,H),(0,0,0)); c.paste(im,((W-nw)//2,(H-nh)//2)); im=c
    if ang: im=im.rotate(ang, resample=Image.BILINEAR, center=(W//2,H//2))
    a=np.asarray(im).astype(np.float32)
    if dx: a=np.roll(a,int(dx),axis=1);
    if dx>0: a[:,:int(dx)]=0
    elif dx<0: a[:,int(dx):]=0
    return a

frames=[]
for t in range(N):
    p=t/(N-1)
    # envelope: quick attack, hold, decay
    if   p<0.12: env=p/0.12
    elif p>0.55: env=max(0,1-(p-0.55)/0.45)
    else: env=1.0
    scale=0.55+0.7*min(1,p/0.5)                     # grows as it forms
    dx=int(W*(-0.28+0.60*p))                        # sweeps left -> right
    ang=6*math.sin(p*math.pi)                       # slight arc wobble
    canvas=xform(1.15*env, scale, dx, ang)
    # trailing after-images (motion blur), dimmer & lagging
    for k,(lag,dim) in enumerate([(0.045,0.5),(0.09,0.28),(0.14,0.15)]):
        canvas+=xform(1.15*env*dim, scale*(1-0.04*(k+1)), int(W*(-0.28+0.60*(p-lag))), ang)
    # leading-edge sparks
    lead_x=int(W*(0.22+0.60*p));
    for _ in range(int(9*env)):
        sx=lead_x+int(rng.normal(0,26)); sy=H//2+int(rng.normal(0,60))
        if 2<=sx<W-2 and 2<=sy<H-2:
            b=rng.uniform(120,255)
            canvas[sy-1:sy+2,sx-1:sx+2]+=np.array([b*0.7,b*0.9,b],np.float32)
    frame=Image.fromarray(np.clip(canvas,0,255).astype(np.uint8),"RGB")
    frame.convert("RGB").save(f"{OUT}/p2_src_{t:02d}.png")
    frames.append(luminance_key(frame))

names=save_frames(frames, OUT, "p2")
save_sheet(frames, f"{OUT}/p2_sheet.png")
save_gif(frames, f"{OUT}/p2_preview.gif", duration=70)
save_tres(names, "vfx/p2", f"{OUT}/p2_jianbo.tres", anim_name="jianbo", fps=16)
print("P2 DONE", len(frames))
