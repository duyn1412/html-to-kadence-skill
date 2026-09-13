#!/usr/bin/env bash
# Install kadence-ai-validator into a WordPress plugins directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$(cd "$SCRIPT_DIR/../wordpress-plugin/kadence-ai-validator" && pwd)"
DEST="${1:-}"

if [[ -z "$DEST" ]]; then
  if [[ -d "wp-content/plugins" ]]; then
    DEST="wp-content/plugins"
  elif [[ -d "coastbygmcdev/wp-content/plugins" ]]; then
    DEST="coastbygmcdev/wp-content/plugins"
  else
    echo "Usage: $0 /path/to/wp-content/plugins"
    exit 1
  fi
fi

mkdir -p "$DEST"
rsync -a --delete "$SRC/" "$DEST/kadence-ai-validator/"
echo "Installed → $DEST/kadence-ai-validator/"
echo "Activate: WP Admin → Plugins → Kadence AI Validator"
