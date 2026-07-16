"""国风水墨 via AnimateDiff: organic black-ink-in-water diffusion (txt2vid excels at this).
White-bg gen -> inverse ink_key -> transparent RGBA."""
import os, torch
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import save_sheet, save_frames, save_tres, ink_key, ink_gif

BASE="/data/chenhang/pixgen_work/vfx/ink"
adapter=MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
pipe=AnimateDiffPipeline.from_pretrained("Lykon/dreamshaper-8", motion_adapter=adapter, torch_dtype=torch.float16)
pipe.scheduler=DDIMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear",
                                         clip_sample=False, timestep_spacing="linspace", steps_offset=1)
pipe.enable_vae_slicing(); pipe.to("cuda")

JOBS=[
 ("ink_diffuse","black ink diffusing and blooming in clear water, traditional chinese ink wash sumi-e, abstract flowing ink tendrils spreading, minimalist, bright white background, monochrome",31),
 ("ink_dragon","a chinese dragon formed of swirling black ink brush strokes, sumi-e xieyi, flowing calligraphy ink, minimalist, bright white background, monochrome",52),
]
neg="color, colorful, vibrant, character face, photo, realistic, 3d, text, watermark, dark background, black background, gray background"
for name,prompt,seed in JOBS:
    out=f"{BASE}/{name}"; os.makedirs(out,exist_ok=True)
    raw=pipe(prompt=prompt,negative_prompt=neg,num_frames=16,guidance_scale=8.0,num_inference_steps=28,
             generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
    fr=[ink_key(f.convert("RGB")) for f in raw]
    names=save_frames(fr,out,name); save_sheet(fr,f"{out}/{name}_sheet.png")
    ink_gif(fr,f"{out}/{name}_preview.gif"); save_tres(names,f"vfx/ink/{name}",f"{out}/{name}.tres",name,12)
    print(f"[{name}] DONE")
print("INK ADIFF DONE")
