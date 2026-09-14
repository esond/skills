# AGENTS.md

This file provides guidance to coding agents (Claude Code, Codex, and others)
when working with code in this repository. `CLAUDE.md` is a symlink to it.

## What this repo is

Eric's personal skills (`esond/skills`), published as five independently
installable plugins, one per bucket. Claude Code consumes the repo as a
**plugin marketplace** through `.claude-plugin/`; Codex and other agents
consume the same tree through skills.sh (`npx skills@latest add esond/skills`)
or the Codex plugin marketplace in `.agents/plugins/`.

- `eng` — writing software: planning workflows, code review, git history,
  .NET hygiene, system design, repo docs.
- `comms` — external communications and human-facing writing.
- `behavior` — tweaks to the agent's behavior: output shaping.
- `docs` — documentation: Diátaxis-guided writing and auditing of tutorials,
  how-to guides, reference, and explanation.
- `esond` — personal to Eric: how he writes and works. Anything tuned to him
  rather than useful to anyone belongs here.

There is no build, no tests, no runtime — every consumer reads the manifest
JSON and skill markdown files directly.

## Choosing a bucket for new content

Every skill, output style, hook, or agent belongs to exactly one plugin. When
adding one and the user hasn't said which plugin it goes in, suggest a bucket
from the five above and confirm before proceeding. If it genuinely fits none of
them, propose creating a new plugin bucket rather than forcing a bad fit — the
whole point of the split is that buckets toggle independently per context. A
new bucket needs a directory under `plugins/`, a `.claude-plugin/plugin.json`,
a root `plugin.json`, and an entry in both marketplace files
(`.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`). It
starts at the version the other plugins are already on, not at `0.1.0`; CI
rejects a plugin that disagrees.

Skills that hand off to each other (`plan-repl` and `plan-repl-resume`,
`sync-core-docs` and `sync-core-repo-docs`, the `diataxis` router and its four
siblings) must stay in one plugin, and a skill that reads a sibling's
`references/` file must live in the same plugin as that sibling.

## Manifest layout

These files drive discovery; changing one without the others will break
loading. Each consumer reads a different subset.

**Read by every agent**

- `plugins/<plugin>/skills/<skill-name>/SKILL.md` — the skill. One per
  directory. The directory name is the skill name. skills.sh and Codex discover
  skills by walking `plugins/*/skills/*/`; Claude Code reads the `skills` array
  in the plugin's `.claude-plugin/plugin.json`, so both must agree.
- `plugins/<plugin>/skills/<skill-name>/agents/openai.yaml` — per-skill
  metadata for Codex: `interface.display_name` and
  `interface.short_description`, plus `policy.allow_implicit_invocation: false`
  when the skill is user-invoked. Every skill has one; CI checks that it exists
  and that `policy` agrees with the `SKILL.md` frontmatter (see Authoring
  skills).
- `plugins/<plugin>/skills/<skill-name>/references/<name>.md` — prose a skill
  reads on demand. A file used by one skill lives in that skill's own
  `references/`. Prose shared by two skills lives in one skill's `references/`
  and the other reads it as `../<owner-skill>/references/<name>.md`, relative
  to its `SKILL.md`; both skills must be in the same plugin. There is no
  plugin-level `references/` directory and no include mechanism: each reader
  tells the agent to read the file, and to say so in one line when the read
  fails rather than proceeding as if the shared rules had loaded. Do not make
  it stop — a stop-and-ask checkpoint is for a destructive action, not for a
  missing prose file. CI checks the link from both ends — every
  `../<skill>/references/<file>.md` path a skill names must resolve, and every
  `references/*.md` must be named by its owner or a sibling. It cannot catch a
  read that fails at runtime. The relative hop resolves under every install
  because skills.sh and the Claude Code plugin install both keep sibling skill
  directories side by side.

**Claude Code**

- `.claude-plugin/marketplace.json` — declares the marketplace (`esond`) and
  lists its plugins. Each plugin entry has `name`, `source` (relative path to
  plugin root, e.g. `./plugins/eng`), `description`, `version`.
- `plugins/<plugin>/.claude-plugin/plugin.json` — declares one plugin. `skills`
  is an array of paths (relative to the plugin root) to skill directories;
  `agents` (optional) is an array of paths to bundled subagent definition
  files. `name` and `version` must match the corresponding marketplace entry,
  and every plugin carries the *same* `version` — see below.
- `plugins/<plugin>/agents/<name>.md` — a subagent bundled for a skill to
  spawn. Frontmatter sets its `name`, `description`, `tools`, and a pinned
  `model`; the file body is the agent's prompt. Listed in that plugin's
  `plugin.json` under `agents`, and invoked by a skill via `subagent_type`
  rather than by the user.
- `plugins/<plugin>/hooks/hooks.json` — event handlers, auto-discovered at the
  plugin root, so `plugin.json` does not list them. Scripts live beside it in
  `hooks/` and are invoked via `${CLAUDE_PLUGIN_ROOT}`. A hook fires for every
  session the plugin is enabled in, so it must exit 0 on all failure paths
  rather than block startup. Write them in POSIX `sh` (Git Bash runs them on
  Windows); `.gitattributes` pins `*.sh` to LF, since CRLF survives Git Bash
  but breaks dash.
- `plugins/<plugin>/output-styles/<name>.md` — an output style,
  auto-discovered at the plugin root, so `plugin.json` does not list it. (An
  `outputStyles` manifest key *replaces* the default scan rather than adding
  to it, so pointing it anywhere but `./output-styles/` hides this directory.)
  Frontmatter sets `name`, `description`, and `keep-coding-instructions` —
  leave that last one `true` unless the style really means to drop Claude
  Code's software-engineering instructions. Do not set `force-for-plugin`: it
  applies the style to anyone with the plugin enabled, so the only way to turn
  it off becomes disabling every skill in that plugin along with it.

**Codex**

- `.agents/plugins/marketplace.json` — the Codex marketplace, also named
  `esond`. Lists each plugin with a `local` source pointing at its directory
  (`./plugins/eng`).
- `plugins/<plugin>/plugin.json` — the portable plugin manifest (Agent Plugins
  schema). Carries the same `name`, `version`, `description`, `author`, and
  `repository` as the plugin's `.claude-plugin/plugin.json`; CI checks that
  `name` and `version` are equal. It lists no skills: Codex discovers them
  from `skills/`.

When adding or removing a skill, update the owning plugin's
`.claude-plugin/plugin.json` (`skills` array), give a new skill its
`agents/openai.yaml`, and — if the marketplace's surface area changed
meaningfully — bump the version. **The version is global**: one number shared
by all plugins, so bump it in every `plugins/*/.claude-plugin/plugin.json`,
every `plugins/*/plugin.json`, and every `.claude-plugin/marketplace.json`
plugin entry at once, including the plugins that didn't change. CI fails when
they diverge, and a `v*` release tag must equal that version. Also update that
plugin's skills table in `README.md`: add the new skill in alphabetical order
with a one-line summary of what it does, or remove the row on deletion.

When a skill bundles a subagent, add its file under the owning plugin's
`agents/`, list it in that plugin's `plugin.json` `agents` array, and add an
"Agents" subsection to the plugin's section in `README.md`.

When a skill bundles a hook, add the script under the owning plugin's
`hooks/`, register it in that plugin's `hooks/hooks.json`, and document it
under a "Hooks" subsection in the plugin's `README.md` section — no plugin has
one today, so create it. A hook that changes the agent's behavior should be
opt-in and reversible from the skill that owns it, so the hook stays inert
until the user turns it on.

When adding or removing an output style, add the file under the owning
plugin's `output-styles/`, add an "Output styles" table to that plugin's
`README.md` section, and bump the shared `version` as you would for a skill.
There is no manifest entry for the style itself to keep in sync. No plugin
ships an output style today.

## Authoring skills

Every skill is a single `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name # must match the directory name
description: | # THIS is how the agent decides to invoke the skill
  ...
---
```

The `description` field is the discovery mechanism — the agent reads it to
decide whether a user's request matches this skill. Write descriptions that
enumerate triggering phrases and scenarios explicitly (see existing skills for
the pattern: "Use this skill whenever the user says X, Y, or Z — even if they
phrase it as..."). A vague description means the skill never fires. Keep the
description under ~1024 characters, though — Claude Code marketplace upload
validation rejects longer ones, so enumerate triggers but trim to fit.

How far to go when enumerating:

- **Enumerate branches. Sample synonyms.** A branch is a distinct situation the
  skill handles — a bug versus a feature, drafting versus editing an existing
  issue. Those must all be named, because they define the skill's scope. A
  synonym is one situation said differently ("file a bug" / "log a bug" /
  "report a bug"); two or three anchors spanning the register are enough, and
  the fourth is a no-op.
- **Spell out vocabulary the name cannot carry.** `rev:` in `inline-review`,
  "CPM" in `clean-unused-cpm-packages` — the model cannot infer those. This is
  where verbosity is load-bearing and pruning breaks triggering.
- **State the boundary once several skills could match.** The `diataxis` family
  names what belongs to a sibling instead. As the installed set grows, a
  description's job shifts from being findable to being distinguishable, and a
  wrong fire costs more than a missed one.

A skill the user invokes by name rather than by description (`bro`,
`sync-core-docs`) sets `disable-model-invocation: true` in its frontmatter
**and** `policy.allow_implicit_invocation: false` in its `agents/openai.yaml`.
The two must agree; CI checks the pairing in both directions.

When a skill hands off to another skill, it calls the Skill tool with the bare
skill name (`diataxis-tutorial`), never a plugin-prefixed one
(`docs:diataxis-tutorial`). The prefix exists only under a Claude Code plugin
install, and the other install paths do not carry it.

The body of `SKILL.md` is the runbook the agent follows once invoked.
Conventions used throughout this repo:

- **Numbered `## Step N` sections** for linear workflows. Each step has a single
  clear action.
- **Explicit stop-and-ask checkpoints** for destructive or ambiguous operations
  — never push past a checkpoint without user confirmation.
- **"Things not to do" / "What this doesn't touch"** sections near the end to
  prevent scope creep when the agent executes the skill.

## Testing a change

CI runs the `validate` job in `.github/workflows/release.yml` on every pull
request and every push to `main`. It checks that both marketplace manifests,
every `plugins/*/.claude-plugin/plugin.json`, and every `plugins/*/plugin.json`
parse; that each plugin's name and version match its Claude Code marketplace
entry and its root `plugin.json` (and that every plugin directory is listed in
both marketplaces); that all plugins carry the same version; that every path
in a plugin's `skills` array has a `SKILL.md`; that each skill's frontmatter
carries `name` and `description` with `name` matching its directory; that
every skill has an `agents/openai.yaml` whose `policy` agrees with
`disable-model-invocation`; that every sibling reference path a skill names
resolves and every reference has a reader; and that `CLAUDE.md` is still a
symlink to `AGENTS.md`. Run the Claude Code structural checks locally with
`claude plugin validate plugins/<plugin>/.claude-plugin/plugin.json` per
plugin, which also covers `hooks/hooks.json` syntax. `claude plugin validate`
does not cover the reference, `openai.yaml`, symlink, or Codex checks — those
only run in CI.

Check the skills.sh view of the repo with
`npx skills@latest add esond/skills -l` (whole set) or
`npx skills@latest add esond/skills/plugins/<plugin> -l` (one bucket); every
skill should be listed. The Codex marketplace is checked with
`codex plugin marketplace add ./` in a Codex session; that needs the Codex
CLI, which CI does not run.

Nothing automated executes a skill, so behavior is still verified by hand:

1. Reload the plugins in Claude Code (via the marketplace).
2. Trigger the skill with a phrase from its `description` and confirm it runs.

Edits to a `SKILL.md` body apply immediately. Changes under a plugin's
`hooks/` and `output-styles/` do not — run `/reload-plugins` or restart. An
output style is also read once when the system prompt is built, so a change to
it needs `/clear` or a new session on top of the reload.

If the skill doesn't fire, the `description` is usually the problem — not the
body.

## Conventions worth preserving

- Skill descriptions are verbose and enumerate trigger phrases. Resist the urge
  to tighten them — terse descriptions miss matches.
- Skills that rewrite history, push, or otherwise take destructive actions must
  require explicit user confirmation at the relevant step. The existing skills
  model this carefully; match that style when adding new ones.
