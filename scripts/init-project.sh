#!/usr/bin/env bash
# Initialize HTML→Kadence framework in a WordPress project.
#
# Usage (submodule):
#   bash packages/html-to-kadence-framework/scripts/init-project.sh
#   bash packages/html-to-kadence-framework/scripts/init-project.sh /path/to/project
#
# Usage (personal skill):
#   bash ~/.cursor/skills/html-to-kadence/scripts/init-project.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="${1:-.}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

if [[ ! -d "$PACKAGE_ROOT/template" ]]; then
  echo "Error: template not found at $PACKAGE_ROOT/template"
  exit 1
fi

echo "HTML→Kadence init"
echo "  package: $PACKAGE_ROOT"
echo "  project: $PROJECT_ROOT"
echo ""

copy_tree() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  for item in "$src"/*; do
    local name
    name="$(basename "$item")"
    if [[ -e "$dest/$name" ]]; then
      echo "  skip (exists): $dest/$name"
    elif [[ -d "$item" ]]; then
      copy_tree "$item" "$dest/$name"
    else
      cp "$item" "$dest/$name"
      echo "  created: $dest/$name"
    fi
  done
}

copy_tree "$PACKAGE_ROOT/template" "$PROJECT_ROOT/.cursor"

mkdir -p "$PROJECT_ROOT/.cursor/html-to-kadence"
if [[ ! -f "$PROJECT_ROOT/.cursor/html-to-kadence/project.yaml" ]]; then
  cp "$PACKAGE_ROOT/project-config.template.yaml" \
     "$PROJECT_ROOT/.cursor/html-to-kadence/project.yaml"
  echo "  created: .cursor/html-to-kadence/project.yaml (EDIT REQUIRED FIELDS)"
else
  echo "  skip (exists): .cursor/html-to-kadence/project.yaml"
fi

mkdir -p "$PROJECT_ROOT/docs"
if [[ ! -f "$PROJECT_ROOT/docs/kadence-html-mapping.md" ]]; then
  cat > "$PROJECT_ROOT/docs/kadence-html-mapping.md" << 'EOF'
# Kadence HTML Mapping

Project-specific HTML → Kadence block mapping. Fill after bootstrap.

## Design tokens

Discover from live site / Customizer. Document palette slots, fonts, spacing.

## Block mapping

| HTML | Kadence block | Project notes |
|------|---------------|---------------|
| `<section>` | `kadence/rowlayout` | Clone from `clone_source` page |

## Site patterns

Document reusable row patterns found on reference pages.

## Learnings

Move repeatable rules to `.cursor/html-to-kadence/project.yaml` → `learnings`.
EOF
  echo "  created: docs/kadence-html-mapping.md"
fi

echo ""
echo "Done. Next steps:"
echo "  1. bash $PACKAGE_ROOT/scripts/link-skill.sh"
echo "  2. Edit .cursor/html-to-kadence/project.yaml"
echo "  3. Create .credentials/wordpress-api.env"
echo "  4. Invoke: 'Convert HTML using html-to-kadence skill'"
