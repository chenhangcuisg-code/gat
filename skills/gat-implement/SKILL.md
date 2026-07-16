---
name: gat-implement
description: "Implement ONE milestone slice into the Godot project: write GDScript, build scenes/nodes, wire data + signals, and drive a running Godot editor via the godot-editor-control (Hastur) skill to add nodes / attach scripts / set properties / run the project. Closes the design→implementation loop. Use after /gat-scaffold, one milestone at a time. Triggers: 实现, implement, build the feature, write gdscript, 做这个里程碑, wire it up in godot."
argument-hint: "[milestone id or name, e.g. 'M2: skill system']"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent
---

# gat-implement — build one milestone into the running game

Request: $ARGUMENTS

Takes one slice of `production/milestone.md` and makes it real in the Godot project: code,
scenes, data wiring, and (when a Godot editor + Hastur broker are running) live node/scene
construction via `skills/godot-editor-control`.

**One milestone at a time.** Do not try to build the whole game in one pass — that is how
scope explodes and verification becomes impossible.

## Inputs to read first

- The target milestone in `production/milestone.md`
- The relevant `design/gdd/<system>.md` (rules + data structures) and
  `design/content/<system>-data.md` (instances)
- **`.gat/architecture.md`** — this game's *active* architecture index (resolved by
  `/gat-scaffold`). Read the module it lists for the system you're building, e.g.
  `knowledge/architecture/modules/system-skill.md`, `modules/system-action-combat.md`,
  `modules/system-ui.md`, `modules/system-game-ai.md`, … If the module you need isn't active yet,
  add it: `python tools/arch_init.py --add modules/system-<name>.md --out .gat/architecture.md`.
- The project's paradigm decision (from `/gat-scaffold`, in `.gat/journal.md`)

## Procedure

1. **Scope the slice.** Restate the milestone's acceptance criteria in one or two lines. If the
   design is ambiguous, clarify before coding (per GAT working rules).
2. **Design the module** using the matching architecture reference. Keep it isolated: reference
   other systems by id/EventBus, not direct coupling (`architecture/evolution.md`).
3. **Implement:**
   - Write GDScript under `src/systems/<system>/`.
   - Load content from `data/<system>.json` — do not hard-code instances.
   - Emit/consume signals through the `EventBus` autoload.
4. **Build scenes in the live editor** (if Hastur is up — see
   `docs/deployment/godot-hastur.md`). Use `skills/godot-editor-control/scripts/gop.py`:
   - `open_scene` / `add_node` / `attach_script` / `set_prop` / `instantiate_scene` / `save_scene`
   - Attach generated VFX (`res://vfx/...` from `/gat-vfx`) to the skills that fire them.
   - If no editor is running, write `.tscn` files directly and note that a live pass is pending.
   Respect the user's editor: prefer `smoke`/targeted ops, do **not** run headless `--import`
   while their editor is open (it fights over `.godot/imported/`).
5. **Run it.** `gop.py` `play` (or `godot --headless` for logic-only smoke) to confirm the
   slice works. Watch the debug output for errors.
6. **Hand to verification.** Call `/gat-verify` for this slice (smoke + balance sim + asset/style
   audit) before declaring it done.
7. **Report** honestly: what works, what's stubbed, what failed, and the next milestone.

## Hard rules

- Build only the current milestone's scope. Note anything you deliberately deferred.
- Never claim a feature works without running it — drive the actual flow, observe behavior.
- Data-driven content stays in `data/*.json`; logic stays in code; art stays registered.
- Test only on the dedicated test save slot; never touch player progress slots.
- If you touched balance numbers, they must pass `/gat-verify`'s sim, not "feel".

## Self-evolving

After the slice: append a one-paragraph case to `.gat/journal.md` (project) and, if you hit a
reusable Godot/GDScript/Hastur gotcha, add it to `knowledge/wiki/pitfalls.md` and the fix to
`knowledge/wiki/methods.md`. This is what makes the next milestone faster.
