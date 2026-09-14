#!/usr/bin/env bash
# Create a PRIVATE GitHub repo from this localVoice/ folder and push it.
#
# Run it from a clone of the repo that contains localVoice/:
#
#     ./localVoice/bootstrap-private-repo.sh [repo-name]
#
# Default repo name: localvoice. The new repo gets this folder's contents at its
# root, with VoiceStudio re-added as a submodule pinned to the SAME upstream
# commit recorded here — so the security audit in security-audit/ still applies.
#
# Requires: git, and the GitHub CLI (gh) authenticated as the repo owner.
# Without gh, the script stops and prints the two manual commands instead.

set -euo pipefail

REPO_NAME="${1:-localvoice}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
REL="${HERE#"$SRC_REPO"/}"            # e.g. localVoice
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

say() { printf '\033[1;34m▸\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# ── The pinned upstream commit, read from the gitlink (not from a working tree,
#    so this is right even when the submodule was never initialised).
PIN="$(git -C "$SRC_REPO" ls-tree HEAD "$REL/VoiceStudio" | awk '{print $3}')"
[ -n "$PIN" ] || die "No submodule gitlink found at $REL/VoiceStudio."
say "VoiceStudio pinned at ${PIN:0:7}"

# ── Stage the docs (everything but the submodule and this script).
say "Staging files"
for f in "$HERE"/*; do
  base="$(basename "$f")"
  case "$base" in
    VoiceStudio|bootstrap-private-repo.sh) continue ;;
  esac
  cp -R "$f" "$STAGE/"
done
[ -f "$STAGE/README.md" ] || die "Expected README.md in $HERE."

# ── Paths shift up one level in the new repo: localVoice/X becomes X.
say "Rewriting paths for the new repo root"
find "$STAGE" -name '*.md' -type f -exec \
  sed -i.bak "s#$REL/VoiceStudio#VoiceStudio#g; s#$REL/security-audit#security-audit#g" {} +
find "$STAGE" -name '*.md.bak' -delete

# ── Build the repo.
say "Initialising repository"
cd "$STAGE"
git init -q -b main
git submodule add -q --depth 1 https://github.com/debpalash/VoiceStudio.git VoiceStudio
git -C VoiceStudio fetch -q --depth 1 origin "$PIN"
git -C VoiceStudio checkout -q "$PIN"
git add -A
git -c commit.gpgsign=false commit -q -m "Initial commit: VoiceStudio pinned at ${PIN:0:7}, security audit, Apple Silicon setup"

# ── Publish.
if ! command -v gh >/dev/null 2>&1; then
  cat <<MSG

The GitHub CLI (gh) is not installed, so the repo was built but not published.
Everything is committed in: $STAGE
(That path is a temp dir — copy it somewhere permanent before this shell exits.)

To finish by hand:
  1. Create an EMPTY private repo named "$REPO_NAME" at https://github.com/new
  2. cd <your copy> && git remote add origin git@github.com:<you>/$REPO_NAME.git
     git push -u origin main
MSG
  trap - EXIT
  exit 0
fi

say "Creating private repo: $REPO_NAME"
gh repo create "$REPO_NAME" --private --source=. --remote=origin --push

trap - EXIT
say "Done. Clone it on the other machine with:"
printf '    gh repo clone %s -- --recurse-submodules\n' "$REPO_NAME"
printf '\nThen follow SETUP-APPLE-SILICON.md.\n'
