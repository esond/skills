---
name: pr-review-resolver
description: >-
  Address outstanding review comments on a GitHub pull request. Fetches all
  unresolved review threads, submitted review bodies, and general PR comments,
  assesses each for validity, fixes the ones it agrees with, pushes and waits
  for CI, replies with the commit hash and resolves the thread, or — when
  declining — replies with justification and leaves the thread for the
  reviewer, then re-requests review. Use this skill whenever the user wants to
  address, fix, resolve, or work through PR review comments or feedback — even
  if they just say something like "handle the PR comments", "address the
  review feedback", "fix what the reviewers said", or "go through the PR".
  Also trigger when the user pastes a PR URL and asks you to act on the
  feedback there. Acts without confirmation by default, stopping only for
  calls that need the user; --ask shows the full triage for approval first.
argument-hint: "[--ask] [pr-number-or-url]"
---

# PR Review Resolver

Assess every piece of outstanding feedback on a PR, fix what the reviewer got
right, push back on what they got wrong, and close the loop with them.

## Arguments

`$ARGUMENTS` may carry a PR number or URL and `--ask`, in any order. "Ask me
first" or "let me review" in the request also turns on `--ask`.

- **Default:** act on every Fix and Decline without waiting; stop only for Ask
  items (Step 3).
- **`--ask`:** show the whole triage for approval before changing code or
  posting anything.

## Step 1: Identify the PR

Take the PR from the arguments. With a URL, read `OWNER`, `REPO`, and
`PR_NUMBER` from the URL itself, not from `gh repo view`. Otherwise detect it
from the current branch:

```bash
gh pr view --json number
gh repo view --json owner,name --jq '.owner.login + " " + .name'
```

With no PR on the branch and none passed, ask the user for one, in either
mode. Substitute the literal values into every later command.

## Step 2: Fetch the feedback

```bash
sh <this skill's directory>/scripts/fetch-feedback.sh OWNER REPO PR_NUMBER
```

It prints three JSON Lines sections: `## threads` (unresolved review threads),
`## reviews` (submitted review bodies), and `## comments` (general comments).
If it exits non-zero, stop and report its error.

Build the worklist:

- Each thread is one item. Read the whole thread; later replies can narrow or
  withdraw the first comment.
- Split each review body and comment into one item per distinct point, nits
  and non-blocking points included. Drop conversational comments (approvals,
  thanks, CI and deploy notices) and bot formatting.
- Drop a review-body item that restates a thread; the thread carries it.

If the worklist is empty, tell the user the PR has no outstanding feedback and
stop.

## Step 3: Triage

Form your own opinion on each item. The goal is better code, not every comment
satisfied. For each, ask:

- Is the reviewer right about the problem, or did they misread the code?
- Would the change improve the code, or make it more abstract, verbose, or
  coupled?
- Is it in scope for this PR?
- Is it a style preference that conflicts with the codebase's conventions?
- Does the reviewer have context you lack: a constraint, downstream impact, or
  domain knowledge?

Give each item a disposition:

- **Fix** — you agree and will change the code.
- **Decline** — the reviewer is wrong, out of scope, low-value, or against the
  codebase's conventions. Write the reply now: concrete reasoning, phrased for
  the reviewer.
- **Ask** — a product or preference call, a question addressed to the user, or
  a bot finding about security, auth, data, migration, or concurrency.

Decline concretely when you disagree; a fix you don't believe in degrades the
code to satisfy one review.

Lay out the triage as one table:

| # | Source | Summary | Disposition | Why |
|---|--------|---------|-------------|-----|
| 1 | `foo.ts:42` | use a native button | **Fix** | agree, keyboard a11y |
| 2 | `bar.ts:88` | extract a shared helper | **Decline** | single caller |
| 3 | review (Copilot) | reword the error copy | **Ask** | product wording |

**Default:** with no Ask rows, continue to Step 4. Otherwise show only the Ask
rows, wait for answers, then continue.

**`--ask`:** show the full table, and below it the full reply text for each
Decline. The user overrides by exception: Fix and Decline rows they don't
mention stand. Each Ask row needs an explicit answer; re-ask any left open.

If fixing shows a disposition was wrong, change it. In default mode, record the
change and the reason for Step 7. With `--ask`, put it to the user first.

## Step 4: Fix the code

If nothing is Fix, skip to Step 6.

Check whether the PR conflicts with its base:

```bash
gh pr view PR_NUMBER -R OWNER/REPO --json mergeStateStatus,baseRefName
```

If `mergeStateStatus` is `DIRTY`, run `git fetch origin`, rebase onto
`origin/<baseRefName>`, and resolve the conflicts before editing.

For a thread, start from its `path` and `line`. When `line` is null or
`isOutdated` is true, locate the code from the path and the comment text; if
the concern no longer applies, Decline with a reply saying where it was
addressed. For review bodies and comments, find the relevant code yourself.

## Step 5: Commit, push, and watch CI

Group small related fixes into one commit and give separate changes their own.
For fixes to review bodies or general comments, name what was addressed in the
commit message. Right after each commit, record `git rev-parse --short HEAD`
against the items it covers.

Push with `git push`, or `git push --force-with-lease` if you rebased in
Step 4. If the push fails, stop and report it; post no replies.

Watch CI:

```bash
gh pr checks PR_NUMBER -R OWNER/REPO --watch
```

If a check fails because of your commits, fix the root cause, commit, push,
and watch again, up to three rounds. Change a test's expected values only when
the behavior it pins genuinely changed. If checks still fail after three
rounds, stop and report before posting replies. Note failures your commits
didn't cause for Step 7 and continue. A PR with no checks continues.

## Step 6: Reply, resolve, and re-request review

`commentId` is the numeric ID for REST replies; `threadId` (`PRRT_…`) is for
the resolve mutation. For a thread fixed across several commits, cite the
last.

**Thread, Fix:** reply with the hash and a few words of context if they help,
then resolve:

```bash
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies -f body="Fixed in abc1234"
gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "THREAD_ID"}) { thread { isResolved } } }'
```

**Thread, Decline:** reply with the justification through the same replies
endpoint, with no hash, and leave the thread unresolved for the reviewer.

**Review body or comment, Fix:** no reply; the commit message is the record.

**Review body or comment, Decline:** post one top-level comment per source:

```bash
gh api repos/OWNER/REPO/issues/PR_NUMBER/comments -f body="..."
```

Open by quoting the point it answers. When the same source also had fixed
items, cover them in that comment too ("items 1 and 3 fixed in abc1234; on
item 2: …").

Then re-request review from each human (`type` `User`, not the PR author) whose
items you fixed or declined:

```bash
gh api -X POST repos/OWNER/REPO/pulls/PR_NUMBER/requested_reviewers -f 'reviewers[]=LOGIN'
```

## Step 7: Summarize

One line per item: its disposition, the commit hash for a Fix, and the URL of
the reply (`html_url` in the reply's response). Flag any disposition changed
mid-run with the reason, CI failures your commits didn't cause, and the
reviewers you re-requested.

## Guardrails

- Resolve a thread only when a pushed commit backs it.
- Add new commits on top; the conflict rebase in Step 4 is the only history
  rewrite.
