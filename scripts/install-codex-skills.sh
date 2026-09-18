#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
FORCE=0

if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

mkdir -p "$TARGET_ROOT"

for skill in "$ROOT"/skills/*; do
  [[ -d "$skill" ]] || continue
  name="$(basename "$skill")"
  target="$TARGET_ROOT/$name"

  if [[ -e "$target" && "$FORCE" -ne 1 ]]; then
    echo "Refusing to overwrite existing skill: $target"
    echo "Re-run with --force if replacement is intentional."
    exit 3
  fi

  rm -rf "$target"
  cp -R "$skill" "$target"
  echo "Installed: $name -> $target"
done

echo
echo "Restart Codex so it can discover the installed skills."
