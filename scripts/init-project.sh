#!/usr/bin/env bash
# Initialize HTML→Kadence framework (v1.1.0) in a WordPress project.
#
# Usage:
#   bash /path/to/html-to-kadence-skill/scripts/init-project.sh [project_root]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="${1:-.}"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

if [[ ! -d "$PACKAGE_ROOT/template" ]]; then
  echo "Error: template not found at $PACKAGE_ROOT/template"
  exit 1
fi

echo "HTML→Kadence v1.1.0 init"
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

# 1. Copy agent skills and templates to .cursor (if using Cursor)
copy_tree "$PACKAGE_ROOT/template" "$PROJECT_ROOT/.cursor"

# 2. Tool-neutral primary project overlay (.html-to-kadence/)
mkdir -p "$PROJECT_ROOT/.html-to-kadence"
if [[ ! -f "$PROJECT_ROOT/.html-to-kadence/project.yaml" ]]; then
  cp "$PACKAGE_ROOT/project-config.template.yaml" \
     "$PROJECT_ROOT/.html-to-kadence/project.yaml"
  echo "  created: .html-to-kadence/project.yaml (EDIT REQUIRED FIELDS)"
else
  echo "  skip (exists): .html-to-kadence/project.yaml"
fi

# Cursor backward-compatibility link
if [[ ! -e "$PROJECT_ROOT/.cursor/html-to-kadence" ]]; then
  ln -s ../.html-to-kadence "$PROJECT_ROOT/.cursor/html-to-kadence" 2>/dev/null || cp -r "$PROJECT_ROOT/.html-to-kadence" "$PROJECT_ROOT/.cursor/html-to-kadence"
  echo "  linked: .cursor/html-to-kadence -> .html-to-kadence"
fi

# 3. Copy QA Engine & Validator scripts
mkdir -p "$PROJECT_ROOT/scripts"
cp "$PACKAGE_ROOT/scripts/qa-engine.py" "$PROJECT_ROOT/scripts/qa-engine.py"
cp "$PACKAGE_ROOT/scripts/validate-blocks.py" "$PROJECT_ROOT/scripts/validate-blocks.py"
chmod +x "$PROJECT_ROOT/scripts/qa-engine.py" "$PROJECT_ROOT/scripts/validate-blocks.py"
echo "  created: scripts/qa-engine.py and scripts/validate-blocks.py"

# 4. Initialize documentation
mkdir -p "$PROJECT_ROOT/docs"
if [[ ! -f "$PROJECT_ROOT/docs/kadence-html-mapping.md" ]]; then
  cat > "$PROJECT_ROOT/docs/kadence-html-mapping.md" << 'INNER_EOF'
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

Move repeatable rules to `.html-to-kadence/project.yaml` → `learnings`.
INNER_EOF
  echo "  created: docs/kadence-html-mapping.md"
fi

echo ""
echo "Done. Next steps:"
echo "  1. bash $PACKAGE_ROOT/scripts/link-skill.sh"
echo "  2. Edit .html-to-kadence/project.yaml"
echo "  3. Create .credentials/wordpress-api.env"
echo "  4. Invoke: 'Convert HTML using html-to-kadence skill'"
