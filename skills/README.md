# skills/ — the GAT skill standard

Every GAT capability is a **skill**: a self-contained folder with a `SKILL.md` procedure. Both
runtimes load the *same* files — Claude Code natively, Codex via a generated shim (see
`docs/dual-runtime.md`). This doc is the contract a skill must follow so install + path
resolution are uniform.

## Skill format

```
skills/<name>/
  SKILL.md            # required — the procedure (front-matter + body)
  scripts/ …          # optional — helper code the skill calls
  references/ …       # optional — deep-dive docs the skill reads on demand
```

### SKILL.md front-matter (standard fields)

```yaml
---
name: gat-example                     # must equal the folder name; invoked as /gat-example
description: "One line: what it does + when to use + trigger words."
argument-hint: "[what the user passes]"
allowed-tools: Read, Write, Edit, Bash, PowerShell, Glob, Grep, Agent   # Claude; Codex ignores
---
```

Body: numbered procedure, hard rules, and a **Self-evolving** section (read the knowledge base
before, write lessons back via `/gat-evolve` after). Keep it implementation-facing.

## Path resolution — the one rule that makes skills portable

A skill runs from inside a **game repo**, but the toolkit resources (`tools/`, `knowledge/`,
`templates/`, `pipelines/`) live in the **GAT toolkit** elsewhere (e.g. `~/gat`). Resolve them
via **`$GAT_HOME`**, written to `<game>/.gat/gat.env` by the installer:

```bash
set -a; . .gat/gat.env; set +a          # sets $GAT_HOME
python "$GAT_HOME/tools/arch_init.py" …  # toolkit script
cat  "$GAT_HOME/knowledge/style/style-contract.schema.md"
```

Convention used throughout the SKILL.md files:

| Path style | Resolves to | Examples |
|---|---|---|
| `$GAT_HOME/…` | the **toolkit** (shared, read-only) | `tools/`, `knowledge/`, `templates/`, `pipelines/` |
| plain relative (`design/`, `data/`, `.gat/`, `assets/`) | the **game repo** (the CWD) | design docs, code, save state, generated assets |

When a SKILL.md shows a bare `tools/x.py` for brevity, it means `$GAT_HOME/tools/x.py`. Outputs
and game content are always game-repo-relative. (Codex prompts embed the absolute `$GAT_HOME`
directly; Claude reads `.claude/CLAUDE.md`, which also records the toolkit path.)

## Install flow (standard)

`install.sh` / `install.ps1` (see `docs/dual-runtime.md`) wire a game repo:

1. **Discover** — glob `skills/*/` and `agents/*.md` (adding a new skill = drop a folder, re-run
   install; nothing else to register).
2. **Link** — Claude: symlink/copy into `.claude/skills` + `.claude/agents`, append the GAT rules
   include to `CLAUDE.md`. Codex: write `AGENTS.md` + one `~/.codex/prompts/<name>.md` shim per
   skill.
3. **Anchor** — write `.gat/gat.env` (`GAT_HOME`) so every skill resolves the toolkit; seed
   `.gat/journal.md` + `.gat/decisions.md`.

```bash
bash install.sh --runtime both --target /path/to/game     # or install.ps1 -Runtime both -Target …
```

## Adding a new skill (checklist)

1. `skills/<name>/SKILL.md` with the front-matter above (`name` == folder).
2. Reference toolkit resources via `$GAT_HOME/…`; write outputs game-repo-relative.
3. End with a **Self-evolving** section.
4. Re-run the installer in your game repo (or it's auto-picked next install — discovery is a glob).
5. If it introduces a new asset path, keep it inside the Style Contract's discipline
   (`docs/style-lock.md`). If it adds architecture needs, wire `tools/arch_init.py`.

## The skills

Design: `gat-workflow-start` · `gat-brainstorm` · `gat-story` · `gat-design` · `gat-milestone`
Style/assets: `gat-style-lock` · `gat-asset` · `gat-vfx`
Implement: `gat-scaffold` · `gat-implement` · `godot-editor-control`
Verify/evolve: `gat-verify` · `gat-evolve` · `gat-learn-from-ref`
