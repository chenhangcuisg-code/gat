# pipelines/unpack — reference study (learning-only)

This directory is the **boundary marker** for GAT's reference-study capability, driven by the
[`gat-learn-from-ref`](../../skills/gat-learn-from-ref/SKILL.md) skill. It exists so your
*original* game can be informed by careful study of prior art — and so that study stays inside
clear legal and ethical lines.

## What this is

A workflow for extracting **design, economy, art, and architecture lessons** from a reference
game you have the right to inspect, and distilling them into GAT's knowledge base
(`knowledge/wiki/`) as transferable, game-agnostic principles.

## What this is NOT

This public module ships **no tooling** and is deliberately not a game-ripping kit:

- ❌ No DRM circumvention, encryption-key extraction, or packer/UPX unpacking.
- ❌ No asset/code/data extraction-and-redistribution.
- ❌ No bypassing of any technical protection measure.

Those capabilities are intentionally kept **out of this repository**. If you legitimately own a
game and want to study your own files offline with separate tools, that is between you, the
software, and its license — GAT does not provide or endorse circumvention.

## The rules (enforced by the skill)

1. **Study only** — the goal is *understanding* to inform original work, never copying.
2. **Only titles you may inspect** — open-source games, games you own for personal study, your
   own past projects. Respect every license and terms of service.
3. **No redistribution** — never commit or publish extracted third-party material. `_work/` and
   `reference-material/` here are git-ignored; delete them once lessons are extracted.
4. **Commercial gate** — commercial use of this module requires prior approval. See
   [`../../LICENSING.md`](../../LICENSING.md).

## Output

The valuable artifact is the *lesson*, written to `knowledge/wiki/patterns.md`
(tagged `reference-study`), `formats.md`, or `pitfalls.md` — game-agnostic, with provenance
noted in `cases.md`. That is what raises your original game's baseline.

If a request would cross any line above, the skill refuses the crossing and offers the
legitimate path (study an open game, or an original design exploration instead).
