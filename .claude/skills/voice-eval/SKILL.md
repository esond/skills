---
name: voice-eval
description: Run a blind 1-5 scoring round on the esond voice skill and turn the scores into skill edits.
argument-hint: "[resume [round] | report [round...] | <what to test this round>]"
disable-model-invocation: true
metadata:
  internal: true
---

# Voice eval

Each round is a blind comparison. Several **arms** (versions of the voice
skill, no skill at all, Eric's real messages) write or supply messages for the
same scenarios. Eric scores each message with the arm hidden, and the scores
decide what changes in the skill.

`SCRIPTS` is the `scripts/` folder beside this file. All data lives outside
the repo, in `~/.claude/voice-eval/`. It holds real messages, so nothing under
it is ever copied into the repo.

- `rounds/<YYYY-MM-DD-x>/`: `scenarios.json`, `arms/` (a snapshot of each
  arm's skill text), `items.json`, `scores.jsonl`.
- `claims.md`: the ledger. The skill is a hypothesis about how Eric writes,
  and each row is one claim it makes, with a status (untested, supported,
  refuted, open, stated) and the rounds behind it.
- `log.md`: one entry per round, with its purpose, arm means, findings, and
  open hypotheses.

Arguments: none or a free-text focus starts a new round. `resume [round]`
skips to Step 5 for that round, or the newest round. `report [round...]` skips
to Step 6.

## Step 1: Pick the round's purpose

Read `claims.md`, `log.md`, and the newest round's report. State the purpose in one line
(for example "first look at voice@3fa2c1e against conversational-voice", or
"does lowercase hold up past two sentences?"), then go. If Eric passed a
focus, that's the purpose.

## Step 2: Write scenarios

Write 8 to 10 new scenarios to `scenarios.json`. Spread them across internal
Slack messages and DMs with colleagues, external messages to a vendor or
partner, email, and technical writing (PR review comments, replies on a
review, issue comments). Vary length and stakes, and vary the subject far
beyond engineering ops: people and team stuff, kudos, saying no, scheduling,
hiring, vendors and money, venting to a peer. Favor messages long enough
that he'd ask Claude to draft them; he doesn't use it for one-liners. Check earlier rounds'
`scenarios.json` and don't repeat a situation. Keep them generic, with no
real employer, product, or person.

```json
{"id": "s3", "context": {"channel": "Slack DM", "to": "a teammate you work with daily",
  "situation": "They asked if the staging deploy went out; it failed on a migration you're fixing",
  "replying_to": "did staging go out?"},
 "ask": "tell him no, migration blew up, fixing now, should be out by 3"}
```

`context` is what the scorer shows. `ask` is what Eric would type to Claude.
Only the generators see it. Write it terse and lowercase, the way he asks,
and include every fact the message needs so arms differ on voice, not on
content.

## Step 3: Generate the arms

By default there are three arms. `none` is a model with no voice skill. It
still loads Eric's global CLAUDE.md, as real sessions do, so it measures what
the skill adds on top of those rules. A small gap means the skill restates
CLAUDE.md, not that it doesn't help.
`production` is the skill in daily use, `conversational-voice` until `voice`
replaces it. `candidate` is the working copy of
`plugins/esond/skills/voice/SKILL.md`, once it exists. Label a skill arm
`<skill>@<first 7 of the SKILL.md sha1>`, and copy its SKILL.md into `arms/`.

Spawn one subagent per arm, all in one turn, with `model: "opus"` so the arms
match real use:

> You draft messages the user will send under their own name. {Read
> `<abs path to SKILL.md>` and follow it for every message. | Do not load or
> invoke any skills.} Invoke no other skills. For each scenario in `<round_dir>/scenarios.json`, write exactly the message
> to send, given the context and the user's `ask`: no commentary, no options,
> no placeholders. Write a JSON array `[{"scenario": "<id>", "text": "..."}]`
> to `<round_dir>/out-<arm>.json`, then reply only "done".

## Step 4: Assemble the round

Add these to the generated messages:

- **Anchors**: 3 to 5 items Eric scored 5 in earlier rounds, copied with arm
  `anchor` and a tag `anchor-of:<original id>`. They check that his scale
  holds between sessions. If they average under 4, the scale has drifted or
  the context display is off, so look at that before trusting other
  differences. Rotate them so recent rounds don't repeat one. A rewrite Eric
  typed into a note counts as a 5.
- Every item is scored on one question: how close is this to how he'd write
  it? Rounds never mix in his real messages, so he isn't guessing what's
  AI-written.
- **Probes** for 2 to 3 claims that are untested, open, or leaning: each
  claim tested in at least two scenarios, each written 2 to 4 ways that
  differ in exactly one trait, the trait the claim is about. Tag each with
  the claim (`C8`) as well. A single score never settles a claim; the
  status rules are at the top of `claims.md`. They get arm `probe` and a tag
  `trait:value`, for example `caps:lowercase` vs `caps:sentence`.

Give generated items tags for traits you can see (`len:1-sentence`,
`greeting:yes`) when they matter to the purpose. Shuffle everything, assign
ids `<round>-01...`, and write `items.json`:
`{"purpose": "...", "items": [{"id", "context", "text", "arm", "tags": []}]}`.
Aim for 25 to 40 items.

## Step 5: Score

Run `python SCRIPTS/serve.py <round_dir>` in the background. It opens the
browser. Tell Eric it's up: `1`-`5` scores and advances, `←`/`→` moves, `n`
or a click focuses the note box, `s` skips. Every score saves as he goes, so he can stop and
`/voice-eval resume` later. A note box sits under the scale. The server exits when he finishes the round, and
that exit is your signal to continue.

## Step 6: Read the scores and propose edits

Run `python SCRIPTS/report.py <round_dir>`, adding the previous two rounds for
the trend. Notes are the highest-signal data, so read every one. Then:

1. Append the round to `log.md`: purpose, arm means, and what the evidence
   says. Update `claims.md`: move statuses, cite the round, and add a row for
   any new pattern the scores or notes suggest.
2. Propose concrete edits to the candidate skill, one per claim that moved.
   Tie each one to the items that support it, and state what it costs in lines. Prefer rewording or
   replacing to adding. When a section has no score evidence either way,
   propose removing it next round as a test.
3. Apply the edits once Eric agrees. Keep any example or phrasing in the
   skill generic, never lifted from his real messages.
