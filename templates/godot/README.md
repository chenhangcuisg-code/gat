# Godot project skeleton (template)

`/gat-scaffold` copies and customizes this into your game repo. It encodes GAT's structural
rules from `knowledge/architecture/` so the game stays change-tolerant from day one.

## Layout scaffold generates

```
project.godot            # this template, with {{GAME_NAME}} filled + autoloads per systems
autoload/                # EventBus, GameState, DataDB, SaveSystem (module framework)
src/
  core/                  # event bus, id lookups, module lifecycle
  systems/<system>/      # one folder per GDD system (code)
data/                    # data-driven content: skills.json, items.json, foes.json, ...
scenes/                  # .tscn by system
assets/                  # art/audio — REGISTERED (see asset-conventions.md), not loose
ui/
tests/                   # smoke + sim harness for /gat-verify
```

## Rules baked in

- **Data / logic / art isolation** — content in `data/*.json`, logic in `src/`, art registered.
  Reference across modules by **id**, pass **DTO copies**, decouple via **EventBus**
  (`knowledge/architecture/evolution.md`). This is what lets requirement changes stay contained.
- **Save-slot discipline** — a dedicated **test slot** (default 5) that `/gat-implement` and
  `/gat-verify` use, so automated runs never touch player progress
  (`knowledge/wiki/pitfalls.md#save-slot`).
- **Style-lock ready** — `assets/` + `res://vfx/` folders match the Style Contract's categories.

## Data file shape

Each entity carries an `art:`/`vfx:` key so `/gat-verify` can audit asset coverage. Example
`data/skills.json`:

```json
{
  "jianbo": {
    "name": "剑波 Sword-Beam",
    "school": "sword",
    "power": 42, "cost": 12, "cooldown": 3,
    "vfx": "res://vfx/ink_jianbo/ink_jianbo.tres",
    "icon": "assets/icons/jianbo.png"
  }
}
```
