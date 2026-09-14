# Review guidance

Reviewer-facing notes for automated code review agents. This repo has no build
or tests — review focuses on manifest integrity and the safety of what each
skill instructs the agent to do, not runtime bugs.

## Review priorities

1. **Manifest integrity.** Any change touching a skill must keep these things
   in agreement (AGENTS.md gives the authoring rule — verify it actually
   held): the owning plugin's `.claude-plugin/plugin.json` lists the skill
   dir; every plugin's `.claude-plugin/plugin.json`, root `plugin.json`, and
   `marketplace.json` entry carry one shared version (a bump moves all of
   them, not just the plugin that changed); `.agents/plugins/marketplace.json`
   lists every plugin; the plugin's skills table in the README has a matching
   alphabetical row; the skill has an `agents/openai.yaml` whose `policy`
   agrees with its `disable-model-invocation` frontmatter; and `CLAUDE.md` is
   still a symlink to `AGENTS.md`. Also check the skill landed in the right
   plugin bucket (`eng`/`comms`/`behavior`/`docs`/`esond` — AGENTS.md "Choosing
   a bucket").
2. **Description length.** Each SKILL.md `description` must stay under the
   ~1024-char upload-validation ceiling (see AGENTS.md "Authoring skills").
   Over-length descriptions fail marketplace upload — check any added/edited
   one.
3. **Trigger quality.** A new/changed `description` should enumerate concrete
   trigger phrases; a terse one silently fails to fire.

## Security-sensitive surfaces

- **Destructive skills.** Skills that rewrite git history, push, delete files,
  or edit tracked source must gate those actions behind an explicit stop-and-ask
  checkpoint. Scrutinize any new skill that takes such an action without one.
- **Shell commands in skills.** Review inline/bundled commands for unsafe
  patterns (unscoped `rm -rf`, `git checkout --` that discards work, force-push)
  and confirm they match the user's stated intent.

## Known false positives — do not flag

- Absence of build/test/CI — there is no runtime; by design.
- Forward slashes, `/dev/null`, Unix shell syntax in skill bodies — AGENTS.md
  mandates bash for skill commands; intentional, not a Windows bug.
- Verbose, repetitive skill `description` fields — verbosity is a deliberate
  triggering strategy.
