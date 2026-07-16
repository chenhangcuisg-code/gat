"""P3 - SDXL controlled img2img: a procedural moving crescent drives each frame's LAYOUT,
SDXL re-paints it into a rich energy slash. Game-controllable motion + AI texture per frame."""
import os, math, torch, numpy as np
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import StableDiffusionXLImg2ImgPipeline, AutoencoderKL
from PIL import Image, ImageDraw, ImageFilter
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

OUT="/data/chenhang/pixgen_work/vfx/p3"; os.makedirs(OUT,exist_ok=True)
W,H,N=768,512,14

vae=AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
pipe=StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", vae=vae, torch_dtype=torch.float16, variant="fp16")
pipe.to("cuda")

def make_init(p):
    """procedural control: bright crescent arc that grows & sweeps L->R on black."""
    im=Image.new("RGB",(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    cx=int(W*(0.20+0.55*p)); cy=H//2
    r=int(110+120*min(1,p/0.6))
    w=max(6,int(r*0.34))
    bb=[cx-r,cy-r,cx+r,cy+r]
    d.arc(bb, start=-62, end=62, fill=(150,225,255), width=w)          # outer glow
    d.arc([cx-r,cy-int(r*0.9),cx+r,cy+int(r*0.9)], start=-58, end=58,
          fill=(235,250,255), width=max(3,int(w*0.45)))                # bright core
    return im.filter(ImageFilter.GaussianBlur(max(3,r*0.05)))

prompt=("a brilliant crescent sword energy slash wave, sharp curved plasma blade of light, "
        "glowing cyan white core with electric blue edges, sparks and energy trails, "
        "pure solid black background, anime game vfx effect, high contrast, no character, no weapon")
neg="character, person, hand, sword handle, text, watermark, realistic photo, dull, gray background, frame, border"

frames=[]
for i in range(N):
    p=i/(N-1)
    init=make_init(p); init.save(f"{OUT}/p3_init_{i:02d}.png")
    env=1.0 if 0.1<=p<=0.62 else (p/0.1 if p<0.1 else max(0,1-(p-0.62)/0.38))
    img=pipe(prompt=prompt, negative_prompt=neg, image=init, strength=0.62,
             guidance_scale=6.5, num_inference_steps=18,
             generator=torch.Generator("cuda").manual_seed(123)).images[0]
    arr=np.clip(np.asarray(img.convert("RGB")).astype(np.float32)*env,0,255).astype(np.uint8)
    Image.fromarray(arr,"RGB").save(f"{OUT}/p3_src_{i:02d}.png")
    frames.append(luminance_key(Image.fromarray(arr,"RGB")))

names=save_frames(frames, OUT, "p3")
save_sheet(frames, f"{OUT}/p3_sheet.png")
save_gif(frames, f"{OUT}/p3_preview.gif", duration=85)
save_tres(names, "vfx/p3", f"{OUT}/p3_jianbo.tres", anim_name="jianbo", fps=12)
print("P3 DONE", len(frames))
