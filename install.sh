#!/usr/bin/env bash
# GAT installer — wire a game repo to run the Godot Agent Team under Claude Code and/or Codex.
#
#   bash install.sh --runtime both --target /path/to/my-game
#   bash install.sh --runtime claude --target .
#
# The GAT toolkit stays where it is (this repo); the installer just points a game repo at it.
set -euo pipefail

GAT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="both"
TARGET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --runtime) RUNTIME="$2"; shift 2 ;;
    --target)  TARGET="$2";  shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

[ -n "$TARGET" ] || { echo "ERROR: --target <game-repo> is required" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"
echo "GAT_HOME = $GAT_HOME"
echo "target   = $TARGET"
echo "runtime  = $RUNTIME"

link_or_copy() {  # $1 src  $2 dst
  rm -rf "$2"
  if ln -s "$1" "$2" 2>/dev/null; then echo "  linked $2"; else cp -r "$1" "$2"; echo "  copied $2"; fi
}

install_claude() {
  echo "== Claude Code =="
  mkdir -p "$TARGET/.claude/skills" "$TARGET/.claude/agents"
  for d in "$GAT_HOME"/skills/*/; do link_or_copy "$d" "$TARGET/.claude/skills/$(basename "$d")"; done
  for f in "$GAT_HOME"/agents/*.md; do link_or_copy "$f" "$TARGET/.claude/agents/$(basename "$f")"; done
  local marker="<!-- gat-rules -->"
  if ! grep -qF "$marker" "$TARGET/CLAUDE.md" 2>/dev/null; then
    { echo ""; echo "$marker"; echo "@$GAT_HOME/runtimes/claude/RULES.md"; echo "GAT toolkit: $GAT_HOME  ·  workflow: @$GAT_HOME/docs/workflow.md"; } >> "$TARGET/CLAUDE.md"
    echo "  wrote CLAUDE.md include"
  else
    echo "  CLAUDE.md already includes GAT rules"
  fi
}

install_codex() {
  echo "== Codex =="
  sed "s#{{GAT_HOME}}#$GAT_HOME#g" "$GAT_HOME/runtimes/codex/AGENTS.md.template" > "$TARGET/AGENTS.md"
  echo "  wrote $TARGET/AGENTS.md"
  local pdir="${CODEX_HOME:-$HOME/.codex}/prompts"
  mkdir -p "$pdir"
  for d in "$GAT_HOME"/skills/*/; do
    local name; name="$(basename "$d")"
    cat > "$pdir/$name.md" <<EOF
Read the GAT skill at \`$GAT_HOME/skills/$name/SKILL.md\` and execute its steps exactly,
following the GAT working rules at \`$GAT_HOME/runtimes/claude/RULES.md\`.
Arguments: \$ARGUMENTS
EOF
  done
  echo "  wrote $(ls "$GAT_HOME"/skills | wc -l | tr -d ' ') prompts to $pdir"
}

# per-project self-evolving journal
mkdir -p "$TARGET/.gat"
[ -f "$TARGET/.gat/journal.md" ] || printf '# %s — GAT project journal\n\n_Per-game memory. Paradigm choices, balance bands, conventions, open questions._\n' "$(basename "$TARGET")" > "$TARGET/.gat/journal.md"
[ -f "$TARGET/.gat/decisions.md" ] || printf '# %s — decisions log\n\n' "$(basename "$TARGET")" > "$TARGET/.gat/decisions.md"

case "$RUNTIME" in
  claude) install_claude ;;
  codex)  install_codex ;;
  both)   install_claude; install_codex ;;
  *) echo "ERROR: --runtime must be claude|codex|both" >&2; exit 1 ;;
esac

echo
echo "Done. Next:  cd $TARGET  &&  run /gat-workflow-start"
