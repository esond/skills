#!/bin/sh
# Usage: resolve-thread.sh THREAD_ID
# Resolves a PR review thread by its GraphQL node ID (PRRT_...).
set -eu

if [ $# -ne 1 ]; then
  echo "usage: $0 THREAD_ID" >&2
  exit 2
fi

gh api graphql -f threadId="$1" -f query='
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) { thread { isResolved } }
}' --jq '.data.resolveReviewThread.thread.isResolved'
