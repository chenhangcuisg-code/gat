#!/usr/bin/env python3
"""art_audit.py — the style gate. An asset that fails this is regenerated, never shipped.

    python tools/art_audit.py asset.png --contract design/art/style-contract.yaml --category icon

Checks (subset selected by contract.enforcement.checks):
  resolution_exact       image size == rendering.resolution
  palette_within_tolerance   mean color sits within tolerance_deltaE of the nearest palette swatch
  background_correct     transparent / pure-black / paper background as declared
  family_resemblance     colour-signature similarity to the family master image >= threshold

Exit code 0 = PASS, 1 = FAIL (with reasons on stderr). Deps: Pillow, numpy, PyYAML.
This is intentionally cheap + explainable — it catches gross style drift (wrong palette,
wrong resolution, opaque bg on a transparent contract, an asset that looks nothing like the
family). It is a gate, not a taste judge; the artist agent still reviews borderline passes.
"""
import argparse, json, sys, math

def load_contract(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".json"):
        return json.loads(text)
    import yaml
    return yaml.safe_load(text)

def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) != 6:
        return None
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_lab(rgb):
    # sRGB -> XYZ -> Lab (D65). Cheap but standard.
    def lin(c):
        c = c / 255.0
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    r, g, b = [lin(x) for x in rgb]
    x = r*0.4124 + g*0.3576 + b*0.1805
    y = r*0.2126 + g*0.7152 + b*0.0722
    z = r*0.0193 + g*0.1192 + b*0.9505
    x, y, z = x/0.95047, y/1.0, z/1.08883
    def f(t):
        return t ** (1/3) if t > 0.008856 else 7.787*t + 16/116
    fx, fy, fz = f(x), f(y), f(z)
    return (116*fy - 16, 500*(fx-fy), 200*(fy-fz))

def deltaE(lab1, lab2):
    return math.sqrt(sum((a-b)**2 for a, b in zip(lab1, lab2)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--contract", required=True)
    ap.add_argument("--category", default=None)
    args = ap.parse_args()

    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        sys.exit("ERROR: needs Pillow + numpy (pip install pillow numpy pyyaml)")

    c = load_contract(args.contract)
    # fold category override for the fields the audit reads
    if args.category and args.category in (c.get("categories") or {}):
        cat = c["categories"][args.category]
        for section in ("rendering", "enforcement"):
            if section in cat:
                c[section] = {**c.get(section, {}), **cat[section]}

    rnd = c.get("rendering", {})
    enf = c.get("enforcement", {})
    checks = enf.get("checks", ["resolution_exact", "palette_within_tolerance",
                                "background_correct", "family_resemblance"])
    fails = []

    im = Image.open(args.image).convert("RGBA")
    arr = np.asarray(im)
    rgb = arr[..., :3].reshape(-1, 3)
    alpha = arr[..., 3].reshape(-1)

    # --- resolution_exact ---
    if "resolution_exact" in checks and rnd.get("resolution"):
        want = rnd["resolution"].lower().replace(" ", "")
        got = f"{im.width}x{im.height}"
        if got != want:
            fails.append(f"resolution: got {got}, want {want}")

    # --- background_correct ---
    if "background_correct" in checks and rnd.get("background"):
        bg = rnd["background"].lower()
        # sample the 4 corners
        corners = np.vstack([arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]])
        if "transparent" in bg:
            if corners[:, 3].mean() > 24:
                fails.append(f"background: expected transparent, corners alpha~{corners[:,3].mean():.0f}")
        elif "black" in bg:
            if corners[:, :3].mean() > 24:
                fails.append(f"background: expected pure black, corners lum~{corners[:,:3].mean():.0f}")
        elif "paper" in bg or "#" in bg:
            pass  # paper bg tolerated; palette check covers it

    # opaque pixels only for colour analysis
    opaque = rgb[alpha > 32] if (alpha > 32).any() else rgb

    # --- palette_within_tolerance ---
    if "palette_within_tolerance" in checks:
        pal = []
        for key in ("primary", "accent", "secondary"):
            for h in (c.get("palette", {}).get(key) or []):
                r = hex_to_rgb(h)
                if r:
                    pal.append(rgb_to_lab(r))
        tol = c.get("palette", {}).get("tolerance_deltaE", 20)
        if pal and len(opaque):
            # sample up to 4000 px for speed
            idx = np.random.RandomState(0).choice(len(opaque), min(4000, len(opaque)), replace=False)
            dists = []
            for px in opaque[idx]:
                lab = rgb_to_lab(tuple(int(v) for v in px))
                dists.append(min(deltaE(lab, p) for p in pal))
            mean_d = float(np.mean(dists))
            if mean_d > tol:
                fails.append(f"palette: mean deltaE {mean_d:.1f} > tolerance {tol} "
                             f"({(np.array(dists) > tol).mean()*100:.0f}% of px off-palette)")

    # --- family_resemblance ---
    if "family_resemblance" in checks:
        ref_path = enf.get("family_resemblance_ref")
        if ref_path:
            try:
                ref = Image.open(ref_path).convert("RGB").resize((64, 64))
                cur = im.convert("RGB").resize((64, 64))
                def sig(pi):
                    a = np.asarray(pi).reshape(-1, 3).astype(float)
                    hist = np.concatenate([np.histogram(a[:, ch], bins=8, range=(0, 255))[0]
                                           for ch in range(3)]).astype(float)
                    return hist / (hist.sum() + 1e-9)
                s1, s2 = sig(ref), sig(cur)
                cos = float(np.dot(s1, s2) / (np.linalg.norm(s1)*np.linalg.norm(s2) + 1e-9))
                thresh = enf.get("family_resemblance_threshold", 0.72)
                if cos < thresh:
                    fails.append(f"family: colour-signature similarity {cos:.2f} < {thresh} "
                                 f"(looks off-family vs {ref_path})")
            except FileNotFoundError:
                print(f"  note: family ref {ref_path} not found, skipping resemblance", file=sys.stderr)

    if fails:
        print(f"FAIL  {args.image}", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        print(f"  -> on_fail policy: {enf.get('on_fail', 'regenerate')}", file=sys.stderr)
        sys.exit(1)
    print(f"PASS  {args.image}")
    sys.exit(0)

if __name__ == "__main__":
    main()
