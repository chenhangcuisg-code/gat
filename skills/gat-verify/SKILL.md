---
name: gat-verify
description: "Verify an implemented milestone before claiming it works: runtime smoke test (drive the actual flow in Godot), data/balance simulation (combat/economy sims + pressure-band calibration, not 'feel'), asset & style-contract audit (every referenced asset exists and passes tools/art_audit.py), and design-coverage check (every GDD entity has data + assets). Reports honestly with evidence. Use after /gat-implement, before saying done. Triggers: 验证, verify, test the feature, balance check, 数值校验, smoke test, does it actually work."
argument-hint: "[milestone or system, e.g. 'skill system']"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent
---

# gat-verify — prove the slice works before claiming it

Request: $ARGUMENTS

GAT's honesty gate. A milestone is not "done" because the code compiles — it is done when the
flow runs, the numbers hold, the assets exist and match the style, and the design is covered.
Report with evidence; if something failed, say so with the output.

## Four checks

### 1. Runtime smoke (behavior, not tests)
Drive the actual feature end-to-end:
- With Hastur up: `skills/godot-editor-control/scripts/gop.py` → `play`, exercise the flow,
  read `get_debug_output`. Respect an open editor (smoke only; don't run headless `--import`).
- Logic-only: `godot --headless` a smoke scene that calls the new system.
Confirm: no errors, the feature does what the milestone's acceptance criteria say.

### 2. Balance / data simulation (for systems with numbers)
Do not tune by feel. Use the two-headed method (from `skill-design`):
- **Static audit** — compute a power/cost index for each skill/item/foe from `data/*.json`.
- **Combat/economy sim** — run staged benchmark characters through simulated fights/loops and
  measure survival / pressure %. Calibrate difficulty bands (easy 10–50 / mid 50–100 /
  hard 100–200, or the game's own bands).
Flag outliers (a skill 3× the band, a resource that never binds). Numbers, not vibes.

### 3. Asset & style audit
For every asset the milestone references (`data/*.json` `art:`/`vfx:` keys):
- Assert the file exists on disk.
- Gate it: `python tools/art_audit.py <file> --contract design/art/style-contract.yaml --category <cat>`.
- Report any missing or off-style asset (candidate for `/gat-asset` / `/gat-vfx` regen). No
  silent "close enough".

### 4. Design coverage
Cross-check the GDD against the implementation:
- Every entity in `design/content/<system>-data.md` has a row in `data/<system>.json`.
- Every system in the milestone's scope has code, a scene, and (if applicable) assets.
- List gaps explicitly — silent truncation of coverage reads as "done" when it isn't.

## Report format

```
MILESTONE: <name>
smoke:     PASS/FAIL   <what ran, key log lines>
balance:   PASS/FAIL   <outliers, bands>
assets:    N ok / M missing / K off-style  <list the bad ones>
coverage:  X/Y entities, A/B systems       <list gaps>
verdict:   done | needs-work (<blocking items>)
```

## Hard rules

- Never report PASS without having actually run the thing.
- If you skipped a check (no GPU, no editor), say so — do not imply it passed.
- Balance claims must come from the sim, not intuition.
- Test only on the dedicated test save slot.

## Self-evolving

Log recurring balance pitfalls / off-style causes to `knowledge/wiki/pitfalls.md` and any new
sim/audit technique to `knowledge/wiki/methods.md`. Update the project's `.gat/journal.md` with
the verdict.
