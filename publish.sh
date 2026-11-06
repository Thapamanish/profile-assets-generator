#!/usr/bin/env bash
set -euo pipefail

PRIVATE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBLIC_REPO_DIR="${1:?Usage: ./publish.sh /absolute/path/to/Thapamanish-clone}"
PUBLIC_REMOTE="git@github.com:Thapamanish/Thapamanish.git"

test -d "$PUBLIC_REPO_DIR/.git" || {
  echo "Not a Git working tree: $PUBLIC_REPO_DIR" >&2
  exit 1
}

test "$(git -C "$PUBLIC_REPO_DIR" branch --show-current)" = "master" || {
  echo "Public clone must be on master." >&2
  exit 1
}

test "$(git -C "$PUBLIC_REPO_DIR" remote get-url origin)" = "$PUBLIC_REMOTE" || {
  echo "origin is not $PUBLIC_REMOTE" >&2
  exit 1
}

git -C "$PUBLIC_REPO_DIR" diff --quiet
git -C "$PUBLIC_REPO_DIR" diff --cached --quiet
git -C "$PUBLIC_REPO_DIR" pull --ff-only origin master

python3 "$PRIVATE_ROOT/scripts/generate_assets.py"

install -m 0644 "$PRIVATE_ROOT/assets/header.svg" "$PUBLIC_REPO_DIR/assets/header.svg"
install -m 0644 "$PRIVATE_ROOT/assets/typing.svg" "$PUBLIC_REPO_DIR/assets/typing.svg"
install -m 0644 "$PRIVATE_ROOT/assets/journey.svg" "$PUBLIC_REPO_DIR/assets/journey.svg"

git -C "$PUBLIC_REPO_DIR" add assets/header.svg assets/typing.svg assets/journey.svg

if git -C "$PUBLIC_REPO_DIR" diff --cached --quiet; then
  echo "No generated asset changes to publish."
  exit 0
fi

git -C "$PUBLIC_REPO_DIR" commit -m "Update profile SVG assets"
git -C "$PUBLIC_REPO_DIR" push origin master
