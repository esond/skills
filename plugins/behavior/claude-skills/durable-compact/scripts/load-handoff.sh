#!/bin/sh
# SessionStart hook (matcher "compact"): sweeps stale handoff pointers, then prints the handoff /durable-compact
# wrote just before this compaction.
# Claude Code adds a SessionStart hook's stdout to the post-compaction context.
input=$(cat)
pending_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/handoffs/.pending"

# A pointer older than 30 minutes is from a handoff the user worked past, or left behind by /clear or a closed
# session, which never compact into it. The skill sweeps them too, each time it writes a new pointer.
[ -d "$pending_dir" ] && find "$pending_dir" -type f -mmin +30 -exec rm -f {} +

source=$(printf '%s' "$input" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
[ "$source" = compact ] || exit 0
session=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
[ -n "$session" ] || exit 0
pending="$pending_dir/$session"
[ -f "$pending" ] || exit 0

handoff=$(tr -d '\r' < "$pending")
if [ -f "$handoff" ]; then
  printf 'Handoff written by /durable-compact before this compaction (%s). Where it disagrees with the summary, the handoff wins.\n\n' "$handoff"
  cat "$handoff"
fi
rm -f "$pending"
exit 0
