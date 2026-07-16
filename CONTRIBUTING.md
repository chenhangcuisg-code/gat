# Contributing to GAT

Thanks for your interest. GAT is source-available under
[PolyForm Noncommercial 1.0.0](LICENSE); by contributing you agree your contribution is licensed
under the same terms and that the maintainer may also offer it under a commercial license (see
[`LICENSING.md`](LICENSING.md)).

## Where things live

| You want to change… | Edit… |
|---|---|
| A skill's behavior | `skills/<name>/SKILL.md` (the single source of truth for both runtimes) |
| A role's remit | `agents/<name>.md` |
| Domain knowledge | `knowledge/architecture/*` |
| Cross-project lessons | `knowledge/wiki/*` (prefer `/gat-evolve` to add these) |
| Style enforcement | `tools/style_prompt.py`, `tools/art_audit.py`, `knowledge/style/*` |
| Runtime wiring | `runtimes/`, `install.sh`, `install.ps1` |

## Principles to keep

1. **One source, two runtimes.** Never fork a skill for Claude vs. Codex. Both load the same
   `SKILL.md`; the runtime layer only shims invocation.
2. **Style-lock is law.** Any new asset path must load the contract, compose via
   `style_prompt.py`, and gate via `art_audit.py`. No freehand prompts.
3. **Self-evolving stays safe.** Skills may edit the knowledge base freely, but changes to
   executable behavior (`skills/`, `agents/`, `tools/`, `templates/`) land via PR — never as a
   silent runtime side effect.
4. **Honesty in verification.** Don't add a check that can pass without actually running.
5. **Reference study stays learning-only.** No DRM/circumvention/extraction tooling enters this
   repo, ever.

## Practical

- Test the installer both ways: `bash install.sh --runtime both --target /tmp/g` and the PS1.
- Run the style tools against `examples/ember-and-ink/design/art/style-contract.yaml` after
  touching them (`style_prompt.py` compose + `art_audit.py` on a sample).
- Keep docs bilingual where the README is (EN + 中文) if you touch user-facing top-level docs.
- Record any non-obvious lesson from your change in `knowledge/wiki/` so the toolkit learns it.

## Reporting

Bugs / features → GitHub issues. Security or licensing questions → issue titled `security` or
`commercial licensing`.
