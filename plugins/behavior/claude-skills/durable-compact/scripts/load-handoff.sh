#!/bin/sh
# SessionStart hook (matcher "compact"): prints the handoff /durable-compact wrote just before this compaction.
# Claude Code adds a SessionStart hook's stdout to the post-compaction context.
session=$(sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
[ -n "$session" ] || exit 0
pending="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/handoffs/.pending/$session"
[ -f "$pending" ] || exit 0

# A pointer older than 30 minutes is from a handoff the user worked past without compacting; drop it unread.
if [ -n "$(find "$pending" -mmin -30)" ]; then
  handoff=$(tr -d '\r' < "$pending")
  if [ -f "$handoff" ]; then
    printf 'Handoff written by /durable-compact before this compaction (%s). Where it disagrees with the summary, the handoff wins.\n\n' "$handoff"
    cat "$handoff"
  fi
fi
rm -f "$pending"
exit 0
