# GAT architecture — how the agent thinks

GAT (Godot Agent Team) is a **full-cycle** game-dev agent: it carries a game from a one-line
idea to a running, verified Godot build, and it gets better every time it does. It is not one
mega-prompt — it is a small team of role agents, a set of skills they run, a domain knowledge
base they consult, and two memories they read and write.

```
                         ┌─────────────────────────────────────────────┐
   idea ──►  DESIGN  ──►  │  STYLE-LOCK  │  ──►  IMPLEMENT  ──►  VERIFY   │  ──► game
             (docs)       │  (contract)  │       (Godot)        (gate)    │
                         └───────────────┴──────────────┬──────────────┘
                                                        │
                          every step reads ▲ / writes ▼ │
                       ┌──────────────────────────────────────────────┐
                       │  KNOWLEDGE  ·  architecture refs  ·  wiki (self-evolving)  │
                       └──────────────────────────────────────────────┘
```

## The five phases

| Phase | Skills | Owner | Output |
|---|---|---|---|
| **Design** | `gat-brainstorm` · `gat-story` · `gat-design` · `gat-milestone` | Designer, Writer, Planner | `design/` docs + `production/milestone.md` |
| **Style-lock** | `gat-style-lock` | VFX/Asset Artist | `design/art/style-contract.yaml` (frozen) |
| **Assets** | `gat-asset` · `gat-vfx` | VFX/Asset Artist | style-audited art + Godot VFX |
| **Implement** | `gat-scaffold` · `gat-implement` (+ `godot-editor-control`) | Engineer | Godot project + code + scenes |
| **Verify** | `gat-verify` | QA | evidence-backed PASS/needs-work |

Cross-cutting: **`gat-evolve`** + **`gat-learn-from-ref`** (Curator) run the self-evolving loop
around all of it. `gat-workflow-start` tells you the next step at any point.

## Where each source lives

GAT unifies four codebases into one workflow:

- **`gat` design pipeline** (from the game-dev-wiki) → the Design phase. This was originally a
  *pre-production-only* workflow that deliberately stopped before code. GAT keeps it and adds
  the implementation half it pointed at.
- **`game-architect`** (30+ references) → `knowledge/architecture/`. The domain brain the
  Engineer consults for paradigm choice and per-system design.
- **`game-skill-vfx`** → `pipelines/vfx/`. The FLUX/AnimateDiff/SDXL VFX pipeline, wrapped by
  `gat-vfx` and bound to the Style Contract.
- **`godot-editor-control`** (Hastur) → `skills/godot-editor-control/`. The hands that build in a
  live Godot editor.
- **`game-unpack`** → informs `gat-learn-from-ref` (learning-only; DRM tooling stays offline).

## Two ideas that make GAT more than a script

1. **Style-lock** (`docs/style-lock.md`) — the answer to "generate one image in a style, then
   keep the *whole game* in that style forever." A frozen, enforceable contract wraps every
   prompt and audits every output. Style drift becomes a decision, not an accident.
2. **Self-evolving** (`docs/self-evolving.md`) — every skill reads the knowledge base before
   work and writes lessons back after. The toolkit compounds across games; it can even propose
   improvements to its own skills (via review, never silently).

## Dual runtime

Everything is portable Markdown + Python. One installer wires a game repo to run GAT under
**Claude Code** (`.claude/skills` + `.claude/agents`) or **Codex** (`AGENTS.md` + `~/.codex/
prompts`) or both. See `docs/dual-runtime.md`.

## Directory map

```
gat/
  agents/            8 role agents (designer, writer, planner, artist, engineer, vfx-artist, qa, curator)
  skills/            13 gat-* skills (design 5 + style/asset 3 + implement 3 + evolve 2) + godot-editor-control
  knowledge/
    architecture/    game-architect references (paradigms + per-system design)
    style/           style-contract schema + art lenses
    wiki/            self-evolving cross-project memory
  pipelines/
    vfx/             game-skill-vfx generation pipeline + samples
    unpack/          learn-from-reference boundary doc (no DRM tooling)
  tools/             style_prompt.py, art_audit.py
  templates/         design/plan doc templates + godot project skeleton
  runtimes/          claude/ + codex/ wiring
  docs/              this file + guides + deployment
  examples/          ember-and-ink worked example
  install.sh / install.ps1
```
