---
name: gat-scaffold
description: "Turn the milestone plan + GDDs into a real Godot project skeleton: project.godot, autoloads, a data-driven content layout (data/*.json), scene/script folder structure, an asset registry, and a save-slot discipline. Chooses the architecture paradigm (DDD / data-driven / prototype) using the game-architect knowledge base. Use once, after /gat-milestone, to go from design docs to an engine project ready for /gat-implement. Triggers: 搭项目, scaffold, create godot project, project structure, bootstrap game."
argument-hint: "[--engine godot4] [--paradigm ddd|data-driven|prototype|auto]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell
---

# gat-scaffold — design docs → Godot project skeleton

Request: $ARGUMENTS

Creates the engine-side skeleton so `/gat-implement` has a real project to build into. This
is the bridge from GAT's document world (`design/`, `production/`) to a running Godot project.

Read from the knowledge base before deciding structure:
- `knowledge/architecture/project-structure.md` — folder layout
- `knowledge/architecture/macro-design.md` + `principles.md` — module framework
- `knowledge/architecture/data-driven-design.md` / `domain-driven-design.md` — paradigm choice
- `knowledge/architecture/asset-conventions.md` — asset registry + data isolation
- `knowledge/architecture/data-files.md` — config/data formats

## Procedure

1. **Read the design.** `design/gdd/game.md`, `systems-index.md`, and `production/milestone.md`.
   Understand the systems and their order.
2. **Pick the paradigm** (`--paradigm auto` = decide from the Paradigm Selection Guide in
   `knowledge/architecture/_ARCHITECT-INDEX.md`):
   - rule-heavy combat/AI → DDD for those entities;
   - content/flow/management (inventory, quests, skills-as-data) → data-driven;
   - most games mix — state the split explicitly.
3. **Create the skeleton** (Godot 4):
   ```
   project.godot
   autoload/            # EventBus, GameState, SaveSystem, DataDB (singletons)
   src/
     core/              # module framework, event bus, id lookups
     systems/<system>/  # one folder per GDD system
   data/                # data-driven content: skills.json, items.json, foes.json, ...
   scenes/              # .tscn by system
   assets/              # art, audio (see asset-conventions; registered, not loose)
   ui/
   tests/               # smoke + sim harness for /gat-verify
   ```
4. **Seed data from content docs.** For each `design/content/<system>-data.md`, create the
   matching `data/<system>.json` with the documented instances (skills, items, foes). Keep an
   `art:`/`vfx:` key per entity so `gat-asset`/`gat-vfx` can register outputs and `/gat-verify`
   can audit coverage. This realizes "extract config data" from `architecture/evolution.md`.
5. **Save-slot discipline.** Create a `SaveSystem` autoload with clearly numbered slots and a
   dedicated **test slot** so verification never touches player progress. Document it in
   `docs/` of the game project.
6. **Wire the style contract.** Ensure `design/art/style-contract.yaml` exists (`/gat-style-lock`)
   and add `res://vfx/` + `assets/` folders that match its categories.
7. **Verify it opens.** If Godot + the Hastur broker are available, use
   `skills/godot-editor-control` to open the project and confirm it loads clean (no import
   errors). Otherwise validate `project.godot` syntax and JSON data files.
8. **Report** the paradigm choice + rationale, the created tree, and the first milestone that
   `/gat-implement` should tackle.

## Hard rules

- Do not implement gameplay here — only structure, autoload stubs, and data seeds.
- Keep data and code isolated (data-driven content in `data/*.json`, not hard-coded).
- Reference entities by **id**, pass **DTOs/copies**, decouple modules via the **EventBus** —
  per `knowledge/architecture/evolution.md` (isolation + abstraction). This is what makes the
  game survive requirement changes.
- Never create save code that can overwrite non-test slots by default.

## Self-evolving

Record the paradigm decision + rationale in `.gat/journal.md` (project) and any reusable
scaffold decisions in `knowledge/wiki/patterns.md`.
