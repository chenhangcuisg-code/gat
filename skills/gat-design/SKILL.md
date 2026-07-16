---
name: gat-design
description: "Continue the design pipeline after brainstorm by writing system GDDs, content data, and system art docs; or add one missing system GDD with art."
argument-hint: "[<system-name>]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
---

# Design

This skill writes system-level design and art documents after `/gat-brainstorm`
has established the game overview, systems index, and global art direction. For
story, worldbuilding, characters, quests, dialogue, or authored narrative content,
delegate to `/gat-story`. For the initial concept interview, it delegates to
`/gat-brainstorm`.

## Phase 1: Resolve Mode

Check existing files:

- If `design/gdd/game.md` or `design/gdd/systems-index.md` missing → hand off: tell the user to run `/gat-brainstorm [hint]` first. Stop.
- If `design/art/art-direction.md` missing → hand off: tell the user to run `/gat-brainstorm [hint]` to establish global art direction. Stop.
- If argument matches a system name in `systems-index.md` → Mode: `system`

With `game.md`, `systems-index.md`, and `art-direction.md` present, assess completeness:

- Any system in `systems-index.md` lacks a GDD → Mode: `continue`
- Any system in `systems-index.md` lacks an art doc → Mode: `continue`
- All of the above are present → report design is complete, stop

## Phase 2: Execute

Read templates:

- `templates/design/system-gdd.md`
- `templates/design/system-art.md`
- `templates/design/content-data.md`

Also read existing `design/narrative/*.md` when present and pass relevant narrative context to spawned agents. Do not create or rewrite narrative docs here; use `/gat-story` for that.

### Continue mode

**Step 1** — For each system in `systems-index.md` lacking a GDD, in order:

Spawn `gat-designer` → `design/gdd/<system>.md`:
- Pass `game.md`, `systems-index.md`, system-gdd template
- Pass existing system GDD if present

**Step 2 — Content Fill** (for systems with high content volume)

For each system whose system GDD is complete AND which requires substantial content data, spawn `gat-designer` to write `design/content/<system>-data.md`:

- Pass the system GDD, `game.md`, `systems-index.md`, content-data template
- Pass existing content doc if present
- The content doc fills specific instances, parameters, sequences, and groups — the **data** that instantiates the **rules** defined in the system GDD

A system needs a content-data doc when its GDD defines data structures that need many concrete instances (e.g. an `enemy` GDD defines enemy attributes → content doc fills 25+ specific enemies; a `stage` GDD defines wave scheduling → content doc fills wave-by-wave scripts for all 5 stages).

Systems that are purely mechanical (e.g. `input`, `tbs-scoring`) typically do NOT need content-data docs — their parameters fit within the GDD itself.

**Step 3** — For each system in `systems-index.md` lacking an art doc, in order:

Spawn `gat-artist` → `design/art/<system>-art.md`:
- Pass `game.md`, `art-direction.md`, the system GDD, the content-data doc (if it exists), system-art template
- Pass existing system art doc if present
- The artist now has both the GDD (rules/schema) and the content-data doc (specific instances) to design complete visuals

### System mode

Require `design/gdd/game.md` and `design/gdd/systems-index.md`.

**Step 0 — Activate architecture knowledge for the new system.** If the project has been
scaffolded (`.gat/architecture.md` exists) and the catalog maps this system
(`knowledge/architecture/catalog.yaml` `by_system`), add its module(s) so implementation stays
grounded (`$GAT_HOME` = the toolkit path from `.gat/gat.env`):
```bash
python "$GAT_HOME/tools/arch_init.py" --add modules/system-<name>.md --out .gat/architecture.md
```
(Skip silently if not yet scaffolded — `/gat-scaffold` resolves the full set later.)

**Step 1** — Spawn `gat-designer` → `design/gdd/<system>.md`

**Step 2** — If the system needs content data, spawn `gat-designer` → `design/content/<system>-data.md`

**Step 3** — Spawn `gat-artist` → `design/art/<system>-art.md`:
- Pass `game.md`, `art-direction.md`, the system GDD, the content-data doc (if it exists), system-art template
- Pass existing system art doc if present

## Phase 3: Review

Summarize what was created or updated.

Use `AskUserQuestion`:

- `Plan milestones (Recommended)` → Run `/gat-milestone`
- `Add another system` → Run `/gat-design <name>`
- `Stop here`
