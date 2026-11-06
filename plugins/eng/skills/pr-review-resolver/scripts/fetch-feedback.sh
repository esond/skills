#!/bin/sh
# Usage: fetch-feedback.sh OWNER REPO PR_NUMBER
# Prints a PR's outstanding feedback as three JSON Lines sections:
#   ## threads   unresolved review threads
#   ## reviews   submitted review bodies (non-empty, not PENDING or DISMISSED)
#   ## comments  general PR comments
# Exits non-zero if any gh call fails.
set -eu

if [ $# -ne 3 ]; then
  echo "usage: $0 OWNER REPO PR_NUMBER" >&2
  exit 2
fi
owner=$1
repo=$2
pr=$3

echo "## threads"
gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first: 50) {
            nodes { databaseId body author { login __typename } }
          }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
  | select(.isResolved | not)
  | {threadId: .id, commentId: .comments.nodes[0].databaseId, path, line, isOutdated,
     comments: [.comments.nodes[] | {author: .author.login, type: .author.__typename, body}]}'

echo "## reviews"
gh api --paginate "repos/$owner/$repo/pulls/$pr/reviews" --jq '.[]
  | select((.body // "") != "" and .state != "PENDING" and .state != "DISMISSED")
  | {reviewId: .id, state, author: .user.login, type: .user.type, body}'

echo "## comments"
gh api --paginate "repos/$owner/$repo/issues/$pr/comments" --jq '.[]
  | {commentId: .id, author: .user.login, type: .user.type, body}'
