# Patterns — design / art-prompt / architecture wins

Transferable patterns that worked. Tag with `[design]`, `[art]`, `[arch]`, `[reference-study]`.
Append, dated.

---

## [art] 2026-07-16 · Anchor an asset family to a master image
Words drift; pixels don't. Generate ONE canonical asset, get sign-off, save it as
`design/art/refs/<name>_master.png`, then generate the rest via img2img / edit / IP-adapter
anchored to it. Set it as `enforcement.family_resemblance_ref`. Biggest single anti-drift lever.

## [art] 2026-07-16 · Subject vs. style separation
In every prompt, the operator writes *only the subject* ("a coiled iron serpent"); all style
words live in the Style Contract's prefix/suffix. Prevents an operator from accidentally
re-styling one asset. `style_prompt.py` enforces the split and guarantees anchor phrases survive.

## [art] 2026-07-16 · Per-family fixed seed
`seed_strategy: fixed-per-family` keeps a set (e.g. 8 skill icons) coherent in lighting/line
weight while letting subjects vary. `fixed` for exact reproducibility; `free` only for one-offs.

## [arch] 2026-07-16 · Data / logic / art isolation for change-tolerance
Content in `data/*.json`, logic in code, art registered (not loose). Reference across modules by
**id**, pass **DTO copies**, decouple via **EventBus**. From `architecture/evolution.md`: this is
what lets requirement changes stay contained instead of rippling.

## [design] 2026-07-16 · Milestone slices, not a task plan
`production/milestone.md` is an ordered set of *handoff slices*, each independently
implementable + verifiable. Build and verify one before starting the next; scope stays bounded.

## [arch] 2026-07-16 · Paradigm split, stated explicitly
Rule-heavy combat/AI → DDD entities; content/flow/management → data-driven; write the split down
in `.gat/decisions.md`. Don't default the whole game to one paradigm.

<!-- Append new patterns above this line. -->
