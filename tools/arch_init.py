#!/usr/bin/env python3
"""arch_init.py — resolve the game-architect knowledge a specific game actually needs.

Instead of carrying all 34 architecture references, GAT keeps a universal `core/` always
active and adds `modules/` on demand from the game's systems + flags. This resolves the
catalog into a per-game active index (`.gat/architecture.md`) that every skill reads.

Initialize (usually called by /gat-scaffold once the systems are known):
    python tools/arch_init.py --systems skill,combat,narrative --flags shipping \
        --multiplayer none --out .gat/architecture.md

Add a module later (e.g. when /gat-design introduces a new system):
    python tools/arch_init.py --add modules/system-mod.md --out .gat/architecture.md

List the catalog:
    python tools/arch_init.py --list

Deps: PyYAML. Catalog: knowledge/architecture/catalog.yaml (override with --catalog).
"""
import argparse, os, sys

def load_yaml(path):
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def resolve(cat, systems, flags, mp_style, minimal):
    active, why = [], {}
    def add(paths, reason):
        for p in (paths or []):
            if p not in why:
                active.append(p); why[p] = reason
    add(cat.get("core"), "core (universal)")
    if not minimal:
        add(cat.get("default_modules"), "default")
    for s in systems:
        hit = (cat.get("by_system") or {}).get(s)
        if hit:
            add(hit, f"system:{s}")
        elif s:
            print(f"  note: no architecture module mapped for system '{s}' (skipped)", file=sys.stderr)
    mp_on = "multiplayer" in flags or (mp_style and mp_style != "none")
    for fl in flags:
        hit = (cat.get("by_flag") or {}).get(fl)
        if hit:
            add(hit, f"flag:{fl}")
        elif fl:
            print(f"  note: no architecture set mapped for flag '{fl}' (skipped)", file=sys.stderr)
    if mp_on:
        add(cat.get("by_flag", {}).get("multiplayer"), "flag:multiplayer")
        if mp_style and mp_style != "none":
            hit = (cat.get("multiplayer_style") or {}).get(mp_style)
            add(hit, f"multiplayer:{mp_style}")
    return active, why

def render(active, why, gat_home_rel):
    lines = [
        "# Active architecture knowledge (this game)",
        "",
        "_Resolved by `tools/arch_init.py` from `knowledge/architecture/catalog.yaml`._",
        "Read these before designing or implementing a system. Everything not listed lives in",
        f"`{gat_home_rel}/knowledge/architecture/modules/` — add it with",
        "`python \"$GAT_HOME/tools/arch_init.py\" --add modules/<file>.md`. Descriptions: `_ARCHITECT-INDEX.md`.",
        "",
    ]
    core = [p for p in active if why[p].startswith("core")]
    deft = [p for p in active if why[p] == "default"]
    rest = [p for p in active if p not in core and p not in deft]
    def block(title, items):
        if not items:
            return []
        out = [f"## {title}", ""]
        for p in items:
            out.append(f"- `{gat_home_rel}/knowledge/architecture/{p}`  — _{why[p]}_")
        out.append("")
        return out
    lines += block("Core (always)", core)
    lines += block("Default modules", deft)
    lines += block("On-demand modules (from this game's needs)", rest)
    lines.append(f"> {len(active)} references active "
                 f"(of the full catalog). Re-run arch_init when systems change.")
    return "\n".join(lines) + "\n"

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_cat = os.path.join(here, "..", "knowledge", "architecture", "catalog.yaml")
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default=default_cat)
    ap.add_argument("--systems", default="", help="comma list, e.g. skill,combat,narrative")
    ap.add_argument("--flags", default="", help="comma list, e.g. shipping,performance_critical")
    ap.add_argument("--multiplayer", default="none",
                    help="none | room | encounter | world | lockstep | rollback")
    ap.add_argument("--minimal", action="store_true", help="skip default_modules (core only + explicit)")
    ap.add_argument("--add", default=None, help="append one module path to an existing index")
    ap.add_argument("--out", default=".gat/architecture.md")
    ap.add_argument("--gat-home-rel", default="..",
                    help="relative path from the game repo to the GAT toolkit (for links)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    cat = load_yaml(args.catalog)

    if args.list:
        print("core:", *cat.get("core", []), sep="\n  ")
        print("default_modules:", *cat.get("default_modules", []), sep="\n  ")
        print("by_system:", *(f"{k}: {v}" for k, v in (cat.get("by_system") or {}).items()), sep="\n  ")
        print("by_flag:", *(f"{k}: {v}" for k, v in (cat.get("by_flag") or {}).items()), sep="\n  ")
        return

    if args.add:
        # append a single module to an existing index (or create with core if none)
        line = f"- `{args.gat_home_rel}/knowledge/architecture/{args.add}`  — _added_"
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        existing = ""
        if os.path.exists(args.out):
            existing = open(args.out, encoding="utf-8").read()
        if args.add in existing:
            print(f"already active: {args.add}")
            return
        with open(args.out, "a", encoding="utf-8") as f:
            f.write(("\n" if existing and not existing.endswith("\n") else "") + line + "\n")
        print(f"added {args.add} -> {args.out}")
        return

    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    flags = [s.strip() for s in args.flags.split(",") if s.strip()]
    active, why = resolve(cat, systems, flags, args.multiplayer, args.minimal)
    doc = render(active, why, args.gat_home_rel)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote {args.out}: {len(active)} active references "
          f"(core {sum(1 for p in active if why[p].startswith('core'))} + "
          f"{len(active) - sum(1 for p in active if why[p].startswith('core'))} modules)")

if __name__ == "__main__":
    main()
