# Architecture knowledge — index & activation model

Game-architecture domain knowledge: paradigm selection + per-system design references. GAT does
**not** load all of this at once. It keeps a small universal **`core/`** always active and adds
**`modules/`** on demand from the game's actual systems and flags.

## How it's activated

- **`core/`** — universal to every game; always in scope (10 refs).
- **`modules/`** — system-specific & multiplayer; added only when needed.
- **`catalog.yaml`** — the activation rules (core / default / by_system / by_flag / multiplayer).
- **`tools/arch_init.py`** — resolves the catalog + a game's needs into a per-game
  **`.gat/architecture.md`** active index. Run by `/gat-scaffold`; extend with `--add` when a new
  system appears.

```
python tools/arch_init.py --systems skill,combat,narrative --flags shipping --out .gat/architecture.md
python tools/arch_init.py --add modules/system-mod.md          # add one later
python tools/arch_init.py --minimal                            # core only (very general default)
```

Read the game's `.gat/architecture.md` first — it tells you exactly which references are live.

---

## Core (always active — `core/`)

| When | Read |
|------|------|
| Always (high-level structure) | `core/macro-design.md` |
| Always (core principles) | `core/principles.md` |
| Requirement analysis | `core/requirements.md` |
| Evolution & extensibility | `core/evolution.md` |
| Project structure & file org | `core/project-structure.md` |
| Data formats, bundles, metadata | `core/data-files.md` |
| Asset conventions & pipeline | `core/asset-conventions.md` |
| Choosing DDD paradigm | `core/domain-driven-design.md` |
| Choosing Data-Driven paradigm | `core/data-driven-design.md` |
| Choosing Prototype paradigm | `core/prototype-design.md` |

## On-demand modules (`modules/`)

Added by `arch_init.py` when the game needs them.

### Default (on for almost every game; skip with `--minimal`)
| System Category | Reference |
|----------------|-----------|
| Foundation & Core (Logs, Timers, Modules, Events, Resources, Audio, Input) | `modules/system-foundation.md` |
| Time & Logic Flow (Update Loops, Async, FSM, Command Queues) | `modules/system-time.md` |
| Scene (Scene Graphs, Spatial Partitioning, Loading) | `modules/system-scene.md` |
| UI & Modules (MVC/MVP/MVVM, UI Management, Data Binding, Reactive) | `modules/system-ui.md` |
| Effect & Feedback (Screen Shake, VFX, Hit-Stop, Floating Text, Orchestration) | `modules/system-effect-feedback.md` |

### By system (activated when `systems-index.md` / config declares it)
| Catalog key | System | Reference |
|---|---|---|
| `skill` | Skill System (Attribute, Skill, Buff) | `modules/system-skill.md` |
| `combat` | Action Combat (HitBox, Damage, Melee, Projectiles) | `modules/system-action-combat.md` (+ `system-3c.md`) |
| `action` | Camera/Character/Controller 3C | `modules/system-3c.md` |
| `ai` / `npc` | Game AI (Movement, Pathfinding, Decision, Tactical) | `modules/system-game-ai.md` |
| `narrative` / `dialogue` | Narrative (Dialogue, Cutscenes, Story Flow) | `modules/system-narrative.md` |
| `pcg` / `roguelike` | Procedural Content Generation | `modules/system-pcg.md` (+ `algorithm.md`) |
| `mod` / `dlc` | Mod & DLC (Plugin, Config DB, Scripting, Hooks) | `modules/system-mod.md` |
| — | Algorithms & Data Structures (Pathfinding, Search, Solver) | `modules/algorithm.md` |

### By flag
| Flag | Reference |
|------|-----------|
| `performance_critical` | `modules/performance-optimization.md` |
| `shipping` | `modules/distribution.md` |
| `multiplayer` | `modules/multiplayer-overview.md`, `-protocol.md`, `-server-architecture.md`, `-implementation-common.md` |

### Multiplayer style (only when `multiplayer` is on)
| Style | Reference |
|------|-----------|
| `room` | `modules/multiplayer-implementation-room.md` |
| `encounter` | `modules/multiplayer-implementation-encounter.md` |
| `world` | `modules/multiplayer-implementation-world.md` |
| `lockstep` / `rollback` | `modules/multiplayer-deterministic-sync.md` |

---

## Paradigm Selection Guide

| Paradigm | KeyPoint | Applicability | Examples | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Domain-Driven (DDD)** | OOP & Entity First | High rule complexity, rich domain, many entities | Combat logic, physics, damage/buff rules, complex AI | `core/domain-driven-design.md` |
| **Data-Driven** | Data Layer First | High content complexity, flow orchestration, simple mgmt | Quests, levels, skill execution, inventory, shop | `core/data-driven-design.md` |
| **Use-Case Prototype** | Use-Case First | Rapid validation | Game jam, core-mechanic testing | `core/prototype-design.md` |

### Mixing (most projects mix)
1. **Macro consistency** — all modules follow one Module Management Framework.
2. **Domain for core entities & rules** — combat actors, damage formulas, AI decisions.
3. **Data for content, flow & state** — quests, tutorials, inventory, narrative.
4. **Hybrid** — entities-as-data; data-driven flow + domain rules per step; separate layers only
   when edit-time and runtime truly diverge (bake/compile bridge).
5. **Interchangeable** — Actor hierarchy (DDD) ↔ ECS components+systems (data-driven); Buff
   objects (DDD) ↔ Tag+Effect entries (data-driven).
6. **Integration** — the Application Layer bridges paradigms.

### Selection signals
| Signal | Favor DDD | Favor Data-Driven |
|--------|-----------|-------------------|
| Entity interactions | Complex multi-entity rules | Mostly CRUD + display |
| Behavior source | Varies by type, hard as data | Config tables, designer content |
| Change frequency | Rules change with balance | Content/flow changes more often |
| Performance | Rich object graphs OK | Needs batch, cache-friendly |
| Networking | Stateful objects OK | Flat snapshots (sync, rollback) |
| Team workflow | Programmers own logic | Designers iterate without code |
