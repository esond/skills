---
name: sync-core-docs
description:
  Create or audit a repo's README.md, AGENTS.md/CLAUDE.md, and REVIEW.md docs.
disable-model-invocation: true
argument-hint: "[--readme] [--claude] [--review]"
---

Call the Skill tool with "sync-core-repo-docs", passing these flags straight
through as its targets: $ARGUMENTS

The flags are `--readme`, `--claude`, `--review`. They combine, and no flags
means process all three in the canonical README → AGENTS → REVIEW order. The
skill owns the runbook; this one only routes the invocation and its flags.
