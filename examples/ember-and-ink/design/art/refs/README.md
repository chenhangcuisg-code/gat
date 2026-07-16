# Family reference images

The Style Contract anchors every asset family to a **master image** — a real pixel exemplar that
new assets are conditioned on (img2img / IP-adapter / gpt-image edit). This is the single
strongest anti-drift lever (see `../../../../../docs/style-lock.md`).

## Expected file

`hero_master.png` — the canonical wandering-swordsman, in the locked papercut-wuxia style.

It is **not committed** to keep the repo lean and to avoid shipping generated art in the example.
Create it with the first asset call, get sign-off, and drop it here:

```bash
# from the game repo root, after /gat-style-lock:
/gat-asset "the wandering swordsman, standing calm, sword sheathed" --category character
# review, then save the approved output as design/art/refs/hero_master.png
```

Once present, the contract's `reference_images` and `enforcement.family_resemblance_ref` point at
it, and `art_audit.py` will check new characters for family resemblance. (The example contract's
`enforcement.checks` omits `family_resemblance` so the tools run cleanly without this file; add it
back once you have a master.)
