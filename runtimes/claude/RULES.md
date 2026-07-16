# GAT working rules (shared by Claude Code and Codex)

You are operating a game project with **GAT — Godot Agent Team**, a full-cycle game-dev
workflow. These rules apply to every role and skill.

## The team
- **designer** owns `design/gdd/*` + `design/content/*-data.md`
- **writer** owns `design/narrative/*`
- **artist / vfx-artist** owns `design/art/*`, the **Style Contract**, and generated assets
- **planner** owns `production/milestone.md`
- **engineer** owns the Godot project, code, and scenes
- **qa** owns verification
- **curator** owns the knowledge base and self-evolution

## The pipeline
`brainstorm → story → design → milestone → style-lock → (asset/vfx → scaffold → implement → verify) × milestones`, with `evolve` closing the loop. `/gat-workflow-start` tells you the next step.

## Non-negotiables
1. **Style-lock discipline.** No asset is generated without a locked `design/art/style-contract.yaml`. Every asset composes its prompt via `tools/style_prompt.py` (subject only) and passes `tools/art_audit.py`. Off-style output is regenerated, never shipped. Change a locked style only via `/gat-style-lock --relock`.
2. **Design-grounded implementation.** Read the GDD + the matching architecture reference before coding. Architecture knowledge loads on demand: universal `knowledge/architecture/core/` is always active; system-specific `modules/` are activated per game into `.gat/architecture.md` by `/gat-scaffold` (add more with `tools/arch_init.py --add`). Read `.gat/architecture.md` to see what's live. Clarify ambiguous design instead of improvising gameplay.
3. **One milestone at a time.** Never balloon scope; note deferrals.
4. **Honest verification.** "Done" = it ran, numbers hold (from the sim, not feel), assets exist and match the style, design is covered — with evidence. Never claim a feature works without running it. If you skipped a check, say so.
5. **Change-tolerant architecture.** Content in `data/*.json`, logic in code, art registered; reference by id, pass DTO copies, decouple via EventBus (`knowledge/architecture/evolution.md`).
6. **Respect the user's editor + saves.** If their Godot editor is open, prefer Hastur smoke/targeted ops; no headless `--import`. Test only on the dedicated test save slot.
7. **Self-evolving.** Read `knowledge/wiki/*` + `.gat/journal.md` before work; write lessons back via `/gat-evolve` after. Edit the knowledge base freely; only *propose* edits to skills/templates/tools (via review).
8. **Reference study is learning-only.** `/gat-learn-from-ref` studies games you may legally inspect; never redistribute third-party content; commercial use needs approval (`LICENSING.md`); no DRM circumvention.

## Working style
- Keep design docs concise and implementation-facing; update existing files over creating variants.
- Use `$GAT_HOME/templates/*` as the canonical doc/code scaffolds.
- When in doubt about the next step, run `/gat-workflow-start`.

## Toolkit path resolution (the standard — see `skills/README.md`)
- Toolkit resources (`tools/`, `knowledge/`, `templates/`, `pipelines/`) live at **`$GAT_HOME`**,
  recorded in `.gat/gat.env` (`set -a; . .gat/gat.env; set +a`). Reference them as `$GAT_HOME/…`.
- Game content (`design/`, `data/`, `assets/`, `.gat/`, code) is **game-repo-relative** (the CWD).
- A bare `tools/x.py` in a skill is shorthand for `$GAT_HOME/tools/x.py`.

## Knowledge index
- Architecture references: `knowledge/architecture/_ARCHITECT-INDEX.md`
- Style law: `knowledge/style/style-contract.schema.md`
- Self-evolving memory: `knowledge/wiki/README.md`
