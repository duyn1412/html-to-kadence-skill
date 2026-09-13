#!/usr/bin/env bash
# Symlink this package into ~/.cursor/skills/html-to-kadence
# so Cursor discovers the html-to-kadence skill.
#
# Usage:
#   bash packages/html-to-kadence-framework/scripts/link-skill.sh
#   bash packages/html-to-kadence-framework/scripts/link-skill.sh /path/to/other-checkout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "${1:-$SCRIPT_DIR/..}" && pwd)"
SKILL_LINK="${HOME}/.cursor/skills/html-to-kadence"
SKILLS_DIR="${HOME}/.cursor/skills"

if [[ ! -f "$PACKAGE_ROOT/SKILL.md" ]]; then
  echo "Error: SKILL.md not found in $PACKAGE_ROOT"
  exit 1
fi

mkdir -p "$SKILLS_DIR"

if [[ -L "$SKILL_LINK" ]]; then
  current="$(readlink "$SKILL_LINK")"
  if [[ "$current" == "$PACKAGE_ROOT" ]]; then
    echo "Already linked: $SKILL_LINK -> $PACKAGE_ROOT"
    exit 0
  fi
  echo "Replacing existing symlink ($current)"
  rm "$SKILL_LINK"
elif [[ -e "$SKILL_LINK" ]]; then
  echo "Error: $SKILL_LINK exists and is not a symlink."
  echo "Move or remove it manually, then re-run."
  exit 1
fi

ln -s "$PACKAGE_ROOT" "$SKILL_LINK"
echo "Linked: $SKILL_LINK -> $PACKAGE_ROOT"
echo "Cursor skill 'html-to-kadence' is ready."
