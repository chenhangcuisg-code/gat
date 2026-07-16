---
name: gat-learn-from-ref
description: "Learn game-design and asset-convention lessons from a REFERENCE game you own or an open-source game — study structure, data layouts, skill/economy tuning, art conventions — and distil them into the knowledge base to inform your own original game. Study/learning use only; commercial use of this module requires prior approval (see LICENSING.md). Reverse-engineering only on titles you have the legal right to inspect. Triggers: 学习参考游戏, learn from reference, study this game's design, reference a game's structure, 拆解参考."
argument-hint: "<a reference project you own/an open game, or notes about one> [--aspect design|economy|art|architecture]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, WebSearch, WebFetch
---

# gat-learn-from-ref — study reference games to sharpen your own design

Request: $ARGUMENTS

Great original games are informed by careful study of prior art. This skill turns a
**reference game you have the right to inspect** (an open-source game, a game you own, your own
past project) into **design lessons** written into GAT's knowledge base — so your original game
starts from a higher baseline. The output is *understanding and conventions*, never copied
content.

## ⚖️ Boundaries — read first (non-negotiable)

- **Study only.** Purpose is learning design/economy/art conventions to inform *your own
  original* work. Do **not** extract-and-ship another game's assets, code, story, or data.
- **Only titles you may inspect.** Open-source games, games you own for personal study, your own
  projects. Respect each game's licence and terms of service. If you do not have the right to
  inspect it, stop.
- **No redistribution.** Never commit or publish extracted third-party assets/code/data. They
  are for local study and are deleted or `.gitignore`d.
- **Commercial gate.** This module (and any workflow built on it) is source-available for
  study/personal use; **commercial use requires prior approval** — see `LICENSING.md`.
- **No DRM circumvention here.** This public skill does *not* ship key-extraction / packer-
  bypass tooling. Those capabilities live in a separate local-only companion (`game-unpack`)
  and are out of scope for this open module. If a target is encrypted/DRM-protected, this skill
  stops and defers to whatever rights and tools you have offline.

If the request would cross any of these lines, refuse the crossing and offer the legitimate
path (study an open game, or an original design exploration instead).

## What to study (`--aspect`)

- **design** — core loop, progression pacing, system interlock, what makes it feel good
- **economy** — resource sources/sinks, currency flow, gating, soft/hard walls
- **art** — palette discipline, resolution/silhouette conventions, VFX language (→ can inform a
  Style Contract for *your* game, in *your* style)
- **architecture** — folder/data layout, data-driven vs coded content, mod/extension surface

## Procedure

1. **Confirm rights.** State what the reference is and why you may inspect it. If unclear, ask.
2. **Study, don't strip.** Read the game's *observable structure*: for an open game, its repo;
   for a game you own, its public data files / your own notes / documented behavior. Extract
   *lessons and conventions*, not files.
3. **Abstract the lesson.** Convert observations into transferable principles ("this idle game
   keeps the prestige loop engaging by …", "this roguelike's data layout separates X from Y").
   Cite the relevant `knowledge/architecture/*` reference the lesson maps to.
4. **Write to the knowledge base** (via the `/gat-evolve` protocol): reference lessons →
   `knowledge/wiki/patterns.md` (tagged `reference-study`), format observations →
   `formats.md`, pitfalls-to-avoid → `pitfalls.md`. Keep them game-agnostic.
5. **Apply forward.** Point out how a lesson should shape the current game's GDD / economy /
   Style Contract — as an original design decision, not a copy.
6. **Clean up.** Remove any locally-fetched third-party material once lessons are extracted.

## Self-evolving

The lessons themselves ARE the evolution — they compound in `knowledge/wiki/`. Note in
`cases.md` which reference informed which decision, so the provenance of your design taste is
traceable.
