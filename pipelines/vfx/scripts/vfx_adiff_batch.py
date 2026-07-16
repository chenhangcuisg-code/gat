"""B(P1 route) - AnimateDiff txt2vid for effects where free-form motion shines: explosion, flame swirl."""
import os, torch
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

BASE="/data/chenhang/pixgen_work/vfx/batch"
adapter=MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
pipe=AnimateDiffPipeline.from_pretrained("Lykon/dreamshaper-8", motion_adapter=adapter, torch_dtype=torch.float16)
pipe.scheduler=DDIMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear",
                                         clip_sample=False, timestep_spacing="linspace", steps_offset=1)
pipe.enable_vae_slicing(); pipe.to("cuda")

JOBS=[
 ("adiff_explosion","a huge fiery explosion blast erupting, orange red flames and yellow white core, expanding smoke and debris, effect, 2d anime, pure solid black background, no character",77),
 ("adiff_flame_swirl","swirling vortex of fire and flames spinning, orange yellow blaze with sparks, effect, 2d anime, pure solid black background, no character",88),
]
neg="character, person, face, hand, weapon, landscape, scenery, buildings, text, watermark, realistic photo, dull, gray, colored background"
for name,prompt,seed in JOBS:
    out=f"{BASE}/{name}"; os.makedirs(out,exist_ok=True)
    raw=pipe(prompt=prompt,negative_prompt=neg,num_frames=16,guidance_scale=8.5,num_inference_steps=28,
             generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
    fr=[luminance_key(f) for f in raw]
    names=save_frames(fr,out,name); save_sheet(fr,f"{out}/{name}_sheet.png")
    save_gif(fr,f"{out}/{name}_preview.gif",duration=90); save_tres(names,f"vfx/batch/{name}",f"{out}/{name}.tres",name,12)
    print(f"[{name}] DONE")
print("ADIFF BATCH DONE")
