# Deploying live Godot editor control (Hastur)

`gat-implement` and `gat-verify` can drive a **running Godot editor** — add nodes, attach
scripts, set properties, open/save scenes, run the project — through the vendored
`skills/godot-editor-control` skill, which talks to the **Hastur Operation Plugin** broker.
This is optional: without it, GAT writes `.tscn`/`.gd` files directly and flags a live pass as
pending.

## Components

```
GAT agent ──HTTP :5302──►  Hastur broker  ──TCP :5301──►  Godot editor (plugin)
   (gop.py, pure stdlib)                                   (runs your GDScript ops)
```

## Setup

1. **Install the Hastur Operation Plugin** into your Godot project's `addons/` and enable it in
   *Project → Project Settings → Plugins*. (See `skills/godot-editor-control/references/install.md`
   for the exact source and version notes.) Godot 4.x (tested 4.6.2 / 4.7).
2. **Start the broker.** The plugin exposes an HTTP broker on `:5302` that relays to the editor
   over TCP `:5301`. Confirm the editor is running with the plugin enabled.
3. **Point the client at it.** `skills/godot-editor-control/scripts/gop.py` needs no third-party
   deps. Set the broker URL if non-default (env or flag — see the skill's `references/protocol.md`).

## Smoke test (no game needed)

Run the mock broker to verify the client end-to-end without an editor:
```bash
python skills/godot-editor-control/scripts/mock_broker.py     # in one shell
python skills/godot-editor-control/scripts/gop.py tree        # in another; should print a mock tree
```

## Real ops

```bash
gop.py open_scene res://scenes/main.tscn
gop.py add_node --parent . --type Node2D --name Player
gop.py attach_script --node Player --path res://src/player.gd
gop.py set_prop --node Player --prop position --value "(64,64)"
gop.py instantiate_scene --parent . --path res://vfx/fireball.tscn
gop.py save_scene
gop.py play                       # run the project; then read debug output
```
The op templates live in `skills/godot-editor-control/gdscript/ops/*.gd` (listed in
`manifest.json`); the cookbook is `references/operations-cookbook.md`.

## Etiquette (from the wiki)

- **Respect an open editor.** If the user's editor is running, prefer targeted ops / `smoke`; do
  **not** run headless `godot --import` — it fights the editor over `.godot/imported/` and can
  hang it (`knowledge/wiki/pitfalls.md#godot-import-lock`).
- **Test slot only.** Any run that saves must target the dedicated test save slot, never player
  progress (`pitfalls.md#save-slot`).
- **Dry-run first** for destructive scene edits; `gop.py --dry-run` previews without applying.

## MCP alternative

If you use a Godot MCP server instead of Hastur, the same operations are available as MCP tools;
`gat-implement` will use whichever is present. Confirm the tools exist before relying on them.
