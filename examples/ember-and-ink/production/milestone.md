# Milestone Roadmap — Ember and Ink

> Example output of `/gat-milestone`. An ordered set of **handoff slices**, each independently
> implementable and verifiable — not a task list. Hand one at a time to `/gat-implement`.

## M1 — Cultivation core (idle spine)
Offline progression along one hard-coded technique tree; time-based accrual; save/load with a
dedicated test slot. **Done when:** closing and reopening after N minutes yields the correct
accrued progress, verified by `/gat-verify` smoke + a short sim.

## M2 — Skill system (data-driven)
Load techniques from `data/skills.json`; equip/drill; apply effects. One real skill end-to-end
(剑波 sword-beam) with its VFX wired from `/gat-vfx`. **Done when:** the skill fires, its effect
plays with the right blend mode, and its power sits inside the sim's balance band.

## M3 — Road trials (progression gate)
Periodic scripted encounters that consume skills and gate advancement; win/lose flow.
**Done when:** a trial can be entered, resolved both ways, and pressure-% sits in the target band.

## M4 — Economy pass
Spirit-stones + materials as skill/trial sources and sinks; no dead-end resources.
**Done when:** the economy sim shows no resource that never binds and no runaway inflation.

## M5 — First-run UX + art pass
Paper-panel UI, vermilion active states, all M1–M4 assets present and **style-audited**.
**Done when:** `/gat-verify` reports 0 missing / 0 off-style assets and the loop is legible to a
first-time player.

---
Each milestone: `/gat-implement "Mx"` → `/gat-verify "Mx"` → `/gat-evolve` before the next.
