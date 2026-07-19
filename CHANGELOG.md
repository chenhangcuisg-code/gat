# Changelog

All notable changes to GAT are documented here.

## [Unreleased]

### Changed
- **Discoverability** — added GitHub topics (`godot-agent`, `game-agent`, `godot-engine`,
  `gdscript`, `game-design`, `ai-game-development`, `multi-agent`, `autonomous-agent`,
  `agentic-ai`) and a bilingual keyword footer in the README, so the project surfaces under
  searches like "godot agent", "game agent godot", and "游戏制作智能体". Repo description now
  leads with "Godot game-development agent / 游戏制作智能体".

## [0.1.0] — 2026-07-16

First public release. Unifies four projects into one full-cycle Godot game-dev agent.

### Added
- **Full-cycle pipeline** — 13 skills across design → style-lock → assets → implement → verify →
  evolve, and 8 role agents (designer, writer, planner, artist, vfx-artist, engineer, qa,
  curator).
- **Design phase** — `gat-brainstorm` / `gat-story` / `gat-design` / `gat-milestone` /
  `gat-workflow-start` (document-driven pre-production, from the simplified Claude-Code-Game-
  Studios workflow).
- **⭐ Style-lock** — `gat-style-lock` freezes an enforceable `style-contract.yaml`; `gat-asset`
  and `gat-vfx` are bound to it. `tools/style_prompt.py` composes the one legal prompt;
  `tools/art_audit.py` gates every output (resolution, palette ΔE, background, family
  resemblance). Full schema in `knowledge/style/`.
- **VFX** — `pipelines/vfx/` vendored from `game-skill-vfx` (FLUX/AnimateDiff/SDXL, luminance-key
  transparency, energy + 国风水墨 styles), with two Godot-ready sample effects and a GPU-server
  deployment guide.
- **Implementation** — `gat-scaffold` + `gat-implement` build into Godot, driving a live editor
  via the vendored `godot-editor-control` (Hastur) skill; grounded in the `game-architect`
  knowledge base (`knowledge/architecture/`, 34 references).
- **On-demand architecture knowledge** — the 34 references are split into universal `core/`
  (always active, 10) + `modules/` (23, added per game). `catalog.yaml` + `tools/arch_init.py`
  resolve a game's systems/flags into a per-game `.gat/architecture.md` active index, so the agent
  carries only relevant refs (~20 for a typical RPG, 10 for a `--minimal` prototype).
- **Standard skill install & path resolution** — `skills/README.md` defines the skill contract;
  the installer writes `.gat/gat.env` (`$GAT_HOME`) so skills resolve toolkit resources
  (`tools/`, `knowledge/`, `templates/`) from any game repo, with game content kept repo-relative.
- **Verification** — `gat-verify` (runtime smoke + balance sim + style audit + design coverage).
- **⭐ Self-evolving** — `gat-evolve` (read-before/write-after loop; toolkit `knowledge/wiki/` +
  per-game `.gat/journal.md`; proposes but never silently applies skill changes) and
  `gat-learn-from-ref` (learning-only reference study).
- **Dual runtime** — `install.sh` / `install.ps1` wire a game repo for Claude Code and/or Codex
  from one set of `SKILL.md` files.
- **Docs** — architecture, workflow, style-lock, self-evolving, dual-runtime, and two deployment
  guides; bilingual (EN + 中文) README.
- **Visual identity** — dark neon-tech pixel-art hero banner + a style-lock explainer, generated
  by the repo's own `tools/make_banner.py` / `tools/make_stylelock.py` (SVG source + rendered PNG).
- **Example** — `examples/ember-and-ink` (papercut-wuxia) with a real, runnable Style Contract.

### License
- Source-available under PolyForm Noncommercial 1.0.0; commercial use requires prior approval
  (`LICENSING.md`). Reference-study module is learning-only and ships no DRM/circumvention tooling.
