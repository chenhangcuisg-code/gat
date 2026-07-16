"""P1 - AnimateDiff txt2vid: pure generative motion. Model invents the whole slash animation."""
import os, torch
os.environ.setdefault("HF_ENDPOINT","https://hf-mirror.com")
from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
import sys; sys.path.insert(0,"/data/chenhang/pixgen_work")
from vfx_util import luminance_key, save_gif, save_sheet, save_frames, save_tres

OUT="/data/chenhang/pixgen_work/vfx/p1"; os.makedirs(OUT,exist_ok=True)
adapter=MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=torch.float16)
pipe=AnimateDiffPipeline.from_pretrained("kohbanye/pixel-art-style", motion_adapter=adapter, torch_dtype=torch.float16)
pipe.scheduler=DDIMScheduler.from_config(pipe.scheduler.config, beta_schedule="linear",
                                         clip_sample=False, timestep_spacing="linspace", steps_offset=1)
pipe.enable_vae_slicing(); pipe.to("cuda")

prompt=("pixelartstyle, a bright horizontal crescent sword energy slash wave sweeping across, "
        "glowing cyan and white plasma arc with blue edges, sparks and energy trails, dynamic motion, "
        "pure solid black background, high contrast, japanese anime game skill vfx effect")
neg=("character, person, human, hand, weapon, sword blade, background scenery, text, watermark, "
     "realistic photo, 3d render, dull, dark, dim, gray")
out=pipe(prompt=prompt, negative_prompt=neg, num_frames=16, guidance_scale=8.0,
         num_inference_steps=25, generator=torch.Generator("cuda").manual_seed(42))
raw=out.frames[0]
for i,f in enumerate(raw): f.convert("RGB").save(f"{OUT}/p1_src_{i:02d}.png")

keyed=[luminance_key(f) for f in raw]
names=save_frames(keyed, OUT, "p1")
save_sheet(keyed, f"{OUT}/p1_sheet.png")
save_gif(keyed, f"{OUT}/p1_preview.gif", duration=90)
save_tres(names, "vfx/p1", f"{OUT}/p1_jianbo.tres", anim_name="jianbo", fps=12)
print("P1 DONE", len(keyed))
