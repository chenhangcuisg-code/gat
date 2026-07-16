"""Shared VFX post-processing: luminance-key (black->alpha), sheets, gifs, Godot .tres."""
import os, numpy as np
from PIL import Image

def luminance_key(img, gamma=0.85, boost=1.15):
    """VFX standard: black bg -> transparent. alpha = perceptual luminance.
    Keeps RGB intact so the frame works with BOTH normal-alpha and additive blending."""
    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    lum = (0.299*rgb[...,0] + 0.587*rgb[...,1] + 0.114*rgb[...,2]) / 255.0
    lum = np.clip((lum**gamma) * boost, 0, 1)
    a = (lum*255).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb.astype(np.uint8), a]), "RGBA")

def on_bg(frame, bg=(18,18,26)):
    """Composite an RGBA frame over a dark bg so glow is visible in a preview GIF."""
    base = Image.new("RGB", frame.size, bg)
    base.paste(frame, (0,0), frame)
    return base

def save_gif(frames, path, duration=80, bg=(18,18,26)):
    fr = [on_bg(f, bg) for f in frames]
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=duration, loop=0)

def save_sheet(frames, path, cols=8):
    n=len(frames); w,h=frames[0].size; rows=(n+cols-1)//cols
    sheet=Image.new("RGBA",(cols*w,rows*h),(0,0,0,0))
    for i,f in enumerate(frames): sheet.paste(f,((i%cols)*w,(i//cols)*h))
    sheet.save(path)

def save_frames(frames, outdir, prefix):
    os.makedirs(outdir, exist_ok=True)
    paths=[]
    for i,f in enumerate(frames):
        p=f"{outdir}/{prefix}_{i:02d}.png"; f.save(p); paths.append(os.path.basename(p))
    return paths

INK=(28,26,34); PAPER=(238,232,216)
def ink_key(img, floor=0.15, boost=1.45, gamma=0.8):
    """国风水墨 INVERSE key: WHITE paper -> transparent, dark ink -> opaque. alpha=darkness, fixed ink color."""
    W,H=img.size
    rgb=np.asarray(img.convert("RGB")).astype(np.float32)
    lum=(0.299*rgb[...,0]+0.587*rgb[...,1]+0.114*rgb[...,2])/255
    dark=np.clip(((1-lum)-floor)/(1-floor),0,1)
    a=np.clip((dark**gamma)*boost,0,1)
    out=np.zeros((H,W,4),np.uint8); out[...,0],out[...,1],out[...,2]=INK
    out[...,3]=(a*255).astype(np.uint8)
    return Image.fromarray(out,"RGBA")

def paper_bg(W,H):
    base=np.zeros((H,W,3),np.float32); base[...]=PAPER
    rng=np.random.default_rng(3); base+=rng.normal(0,4,(H,W,3))
    return Image.fromarray(np.clip(base,0,255).astype(np.uint8),"RGB")

def ink_gif(frames,path,dur=90):
    bg=paper_bg(*frames[0].size).convert("RGBA")
    comp=[Image.alpha_composite(bg,f).convert("RGB") for f in frames]
    comp[0].save(path,save_all=True,append_images=comp[1:],duration=dur,loop=0)

def save_tres(frame_names, res_dir, tres_path, anim_name="jianbo", fps=12):
    """Godot 4 SpriteFrames resource pointing at individual transparent frames under res://<res_dir>/."""
    n=len(frame_names)
    lines=[f'[gd_resource type="SpriteFrames" load_steps={n+1} format=3]',""]
    for i,fn in enumerate(frame_names):
        lines.append(f'[ext_resource type="Texture2D" path="res://{res_dir}/{fn}" id="{i+1}_f"]')
    lines.append("");lines.append("[resource]")
    frames_arr=", ".join(f'{{"duration": 1.0, "texture": ExtResource("{i+1}_f")}}' for i in range(n))
    lines.append("animations = [{")
    lines.append(f'"frames": [{frames_arr}],')
    lines.append('"loop": true,')
    lines.append(f'"name": &"{anim_name}",')
    lines.append(f'"speed": {float(fps)}')
    lines.append("}]")
    open(tres_path,"w").write("\n".join(lines))
