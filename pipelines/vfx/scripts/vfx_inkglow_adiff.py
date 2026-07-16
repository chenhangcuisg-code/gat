"""国风水墨风 (RICH glow) via AnimateDiff: glowing luminous ink dragon + ink vortex on BLACK
-> luminance_key -> additive glow. txt2vid excels at organic flowing ink."""
import os, torch
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

BASE="/data/chenhang/pixgen_work/vfx/inkglow"
adapter=MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
pipe=AnimateDiffPipeline.from_pretrained("Lykon/dreamshaper-8", motion_adapter=adapter, torch_dtype=torch.float16)
pipe.scheduler=DDIMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear",
                                         clip_sample=False, timestep_spacing="linspace", steps_offset=1)
pipe.enable_vae_slicing(); pipe.to("cuda")

JOBS=[
 ("ink_dragon","a majestic chinese dragon made of glowing luminous flowing ink, swirling white and silver ink wash brush strokes with jade green and gold glow, dynamic soaring serpentine motion, richly detailed intricate, effect, pure solid black background, no character",52),
 ("ink_swirl","a swirling vortex of glowing luminous ink spinning, chinese ink wash energy, white silver ink with cyan glow, splashes wisps and mist, richly detailed intricate, effect, pure solid black background",88),
]
neg="character, person, face, hand, weapon, text, watermark, flat, minimalist, sparse, simple strokes, empty, plain white background, daylight, realistic photo, dull, gray background"
for name,prompt,seed in JOBS:
    out=f"{BASE}/{name}"; os.makedirs(out,exist_ok=True)
    raw=pipe(prompt=prompt,negative_prompt=neg,num_frames=16,guidance_scale=8.5,num_inference_steps=28,
             generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
    fr=[luminance_key(f.convert("RGB")) for f in raw]
    names=save_frames(fr,out,name); save_sheet(fr,f"{out}/{name}_sheet.png")
    save_gif(fr,f"{out}/{name}_preview.gif",duration=90); save_tres(names,f"vfx/inkglow/{name}",f"{out}/{name}.tres",name,12)
    print(f"[{name}] DONE")
print("INKGLOW ADIFF DONE")
