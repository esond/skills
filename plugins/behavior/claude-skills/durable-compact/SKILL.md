---
name: durable-compact
description: Write the session's state to a handoff file, then print a focused /compact command and a resume prompt.
disable-model-invocation: true
metadata:
  internal: true
---

# Durable compact

`/compact` keeps a lossy summary. This skill writes a **handoff** first: a file a cold reader can resume from, holding what the summary tends to drop. The cold reader is you after compaction, with a summary you didn't write and no memory of why anything happened. You can't run `/compact` yourself; the user does, with the line you print.

The whole run happens in context that compaction is about to fold away, so keep it cheap: one file write, at most one question, one short reply.

## Step 1: Draft the handoff

Write it from what is already in your context. You hold the full session, so you write it yourself; a fresh subagent sees none of the conversation.

Path: `handoffs/<project>/<YYYY-MM-DD-HHmm>-<topic-slug>.md` under the Claude config dir (`${CLAUDE_CONFIG_DIR:-$HOME/.claude}`), resolved to an absolute path. `<project>` is the basename of the git root of the session's primary working directory, or of that directory outside a repo. Get the timestamp from the shell rather than guessing it. Then write `handoffs/.pending/<session id>` holding only the handoff's absolute path, where the session id is `$CLAUDE_CODE_SESSION_ID` read from the shell; the compact hook loads the handoff for that session only.

Fill these sections, omitting any that would be empty:

- **Goal**: what the user is trying to achieve, in their words where you have them. Include the reason behind it if they gave one.
- **State**: what is done and verified, what is in progress, what is untouched. Say how each "done" was verified.
- **Decisions**: each choice made, why, and the options rejected. A rejected option with its reason stops the next session from proposing it again.
- **User corrections and preferences**: every time the user corrected you or stated how they want things done this session, quoted verbatim.
- **Hard-won facts**: things learned by effort that the repo doesn't record: tool or API behavior, gotchas, commands that work, dead ends and why they failed.
- **Open threads**: questions waiting on the user, things you were about to check, known problems not yet fixed.
- **Next step**: the single concrete action to take on resume.
- **Pointers**: exact identifiers: absolute file paths, branch names, PR/issue numbers, URLs, IDs, commands. Copy them, never paraphrase them.

Point to what lives on disk (code, git history, docs) instead of restating it; the handoff carries what exists only in this conversation. Prefer a dense line over a paragraph.

Done when a reader with only this file and the repo could take the next step without asking what anything means.

## Step 2: One check with the user

While drafting, note the borderline items: things you weren't sure deserved a place, or facts you inferred rather than saw. With two or more, ask one `AskUserQuestion` (multiSelect): "Which of these should the handoff keep?" with up to four of them as options. With fewer, ask a single-select "Anything else the handoff should keep?" with "No, it's complete" and, if there is one, "Keep <the borderline item>" as options. Either way the built-in "Other" box is where the user adds what you missed. Apply the answers to the file.

In the same `AskUserQuestion` call, check for the compact hook. It is already active when this skill came from the `behavior` plugin, which ships it: `<base dir>/../../hooks/hooks.json` exists and names `load-handoff.sh`. Otherwise search the user settings file (`settings.json` in the Claude config dir) and the project's `.claude/settings.json` and `.claude/settings.local.json` for `load-handoff.sh`. If the entry that names it has `"matcher": "compact"`, remove that matcher so the stale-pointer sweep runs on every session start. If it's in none of them, add a second question offering to install it: it loads the handoff into context automatically after every compaction that follows this skill, so the resume prompt becomes unnecessary. On yes, add this entry to the `hooks.SessionStart` array, keeping everything else in the file intact, with the script's absolute path from this skill's base directory:

```json
{
  "hooks": [{ "type": "command", "command": "sh \"<base dir>/scripts/load-handoff.sh\"", "timeout": 5 }]
}
```

A hook added mid-session may not be active until the user reviews it in `/hooks` or restarts, so the resume prompt still matters this time.

## Step 3: Print the commands

Reply with the handoff path, then two fenced blocks:

1. The compact command, with focus instructions naming the goal, the next step, and the handoff path, so the summary itself keeps the pointer:

   ```
   /compact Keep: <goal in a few words>; next step <next step>; full state in <absolute handoff path>
   ```

2. The resume prompt to paste after compaction:

   ```
   Resume from the handoff at <absolute handoff path>. Read it in full before acting; where it and the compaction summary disagree, the handoff wins. Then <next step>.
   ```

Add one line saying the resume prompt works after `/clear` too, which drops the summary for a cleaner start. If the hook was already installed, say the handoff loads on its own after `/compact`, and the resume prompt is the fallback if it doesn't show up.
