#!/bin/sh
# SessionStart hook (matcher "compact"): prints the handoff /durable-compact wrote just before this compaction.
# Claude Code adds a SessionStart hook's stdout to the post-compaction context.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$dir")
pending="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/handoffs/$(basename "$root")/.pending"
[ -f "$pending" ] || exit 0

# A pointer older than two hours is from a handoff the user never compacted after; drop it unread.
if [ -n "$(find "$pending" -mmin -120)" ]; then
  handoff=$(cat "$pending")
  if [ -f "$handoff" ]; then
    printf 'Handoff written by /durable-compact before this compaction (%s). Where it disagrees with the summary, the handoff wins.\n\n' "$handoff"
    cat "$handoff"
  fi
fi
rm -f "$pending"
exit 0
