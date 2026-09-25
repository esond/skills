---
name: reorganize-branch-commits
description: >-
  Reorganize the commits on a non-default git branch into a clean, logical
  history by rewriting the branch — `git reset` + re-commit by default,
  `git rebase -i` when commit boundaries already align. Propose groupings
  based on the actual work done (features, refactors, tests, fixes, docs), get
  explicit user approval, back the branch up, then rewrite history. Use this
  skill whenever the user wants to tidy up, clean up, reorganize, restructure,
  squash, or curate commits on a feature branch — even if they phrase it as
  "my branch is a mess", "squash this down", "combine these commits", "fix up
  the commit log before I open a PR", or "make the commits presentable for
  review". Trigger proactively when the user is about to open or push a PR and
  the branch has scrappy/WIP/"fix" commits to collapse. Refuses to operate on
  default or release-shaped branches (main, master, develop, trunk,
  production, release, or the repo default) — a feature-branch-only tool.
---

# reorganize-branch-commits

Rewrite the commits on a feature branch into a clean, logical history. Every commit from the base forward gets a new hash.

## Step 1 — check the branch

The repo default is `git symbolic-ref refs/remotes/origin/HEAD --short | sed 's@^origin/@@'`. The base is `git merge-base HEAD origin/<default>`, unless the user names another (a branch stacked on another feature branch).

Stop and tell the user if any of these hold:

- HEAD is detached, or the branch is `main`, `master`, `trunk`, `develop`, `production`, `release`, or the repo default.
- `git status` shows uncommitted changes or an in-progress rebase, merge, or cherry-pick. A reset would fold uncommitted edits into the new commits.
- The branch has fewer than two commits past the base.

## Step 2 — propose a history

Read `git log --name-status <base>..HEAD` and the diffs behind it. Group by what the diffs actually do, not by the existing messages: one logical change per commit, refactors before the feature that needs them, and "wip" / "fix typo" / "address review" commits folded into the change they serve. Match the subject style of recent commits on the default branch.

Present a numbered list of new commits, each with its subject, the source commits folded into it, and the files it touches. Every existing commit must be accounted for. Flag merge commits (they'll be flattened) and commits by other authors (a reset re-attributes them to the current user).

If the branch has an upstream, say that finishing will need a force push. Don't rewrite anything until the user approves the proposal.

## Step 3 — back up

```bash
git branch "backup/<branch>/$(date -u +%Y%m%dT%H%M%SZ)"
```

Tell the user the backup's name; `git reset --hard <backup>` restores the original branch.

## Step 4 — rewrite

`git reset <base>`, then stage and commit each group in order. Use `git add -p` when one file's hunks belong to different groups. Let hooks run; never pass `--no-verify`.

Use `git rebase -i <base>` instead when the existing commit boundaries already match the groups, or when other authors' commits must keep their authorship. If it stops on a conflict, report the paths and let the user decide whether to resolve or abort.

## Step 5 — verify and hand off

`git diff <backup> HEAD` must be empty. If it isn't, show the user the difference: a missed hunk goes into a commit, while hook output (formatters, codegen) needs the user's OK. Then show `git log --oneline <base>..HEAD`.

Once the diff is empty or the user has accepted what's left, ask whether to push, and push only on a yes: `git push --force-with-lease` if the branch has an upstream, otherwise `git push -u origin <branch>`. Never use plain `--force`.

After the push succeeds, offer to delete the backup with `git branch -D <backup>`, and keep it if the user declines.
