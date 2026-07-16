#!/usr/bin/env python3
"""style_prompt.py — compose the ONE legal prompt for an asset, from the Style Contract.

Every GAT asset skill (gat-asset / gat-vfx / gat-icon) calls this instead of writing its
own prompt. You pass the *subject only*; the style comes from design/art/style-contract.yaml.

    python tools/style_prompt.py --contract design/art/style-contract.yaml \
        --subject "a wandering swordsman resting under a pine" --category character

Prints JSON: {positive, negative, params, seed, backend, size, resolution, reference_images}.
The rule (see knowledge/style/style-contract.schema.md): final positive is
    positive_prefix + subject + positive_suffix
with the contract's negative / params / seed applied verbatim. Never freehand a prompt.

Deps: PyYAML (pip install pyyaml). Falls back to JSON if the contract is .json.
"""
import argparse, json, sys, hashlib, os

def load_contract(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("ERROR: PyYAML not installed. `pip install pyyaml` or use a .json contract.")
    return yaml.safe_load(text)

def deep_merge(base, override):
    """Category overrides inherit everything, then patch nested keys."""
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def family_seed(base_seed, strategy, subject):
    if strategy == "free":
        return None
    if strategy == "fixed":
        return int(base_seed)
    # fixed-per-family: stable per subject-family so a set stays coherent but items differ
    h = int(hashlib.sha256(subject.encode("utf-8")).hexdigest(), 16)
    return int(base_seed) + (h % 100000)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--subject", required=True, help="describe ONLY the subject, not the style")
    ap.add_argument("--category", default=None, help="icon | character | vfx | tileset | ...")
    args = ap.parse_args()

    c = load_contract(args.contract)
    if not c.get("locked"):
        sys.exit("ERROR: style contract is not locked. Run /gat-style-lock first.")

    # apply category override
    if args.category and args.category in (c.get("categories") or {}):
        cat = c["categories"][args.category]
        for section in ("rendering", "prompt_contract", "model"):
            if section in cat:
                c[section] = deep_merge(c.get(section, {}), cat[section])

    pc = c.get("prompt_contract", {})
    prefix = (pc.get("positive_prefix") or "").strip().rstrip(", ")
    suffix = (pc.get("positive_suffix") or "").strip().lstrip(", ").rstrip()
    subject = args.subject.strip().strip(",").strip()
    positive = ", ".join(x for x in [prefix, subject, suffix] if x)

    # guard: every non-negotiable anchor phrase must survive
    missing = [p for p in pc.get("style_anchor_phrases", []) if p.lower() not in positive.lower()]
    if missing:
        sys.exit(f"ERROR: composed prompt dropped anchor phrase(s): {missing}. Fix the contract.")

    model = c.get("model", {})
    out = {
        "positive": positive,
        "negative": (pc.get("negative") or "").strip(),
        "backend": model.get("backend"),
        "size": model.get("size"),
        "params": model.get("params", {}),
        "seed": family_seed(model.get("base_seed", 0), model.get("seed_strategy", "fixed"), subject),
        "resolution": c.get("rendering", {}).get("resolution"),
        "background": c.get("rendering", {}).get("background"),
        "reference_images": pc.get("reference_images", []),
        "category": args.category,
        "contract_version": c.get("version"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
