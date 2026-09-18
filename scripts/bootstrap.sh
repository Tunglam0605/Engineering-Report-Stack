#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for cmd in python3 node npm; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 2
  fi
done

if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

python3 -m unittest discover -s tests -v
npm run docs:build

echo
echo "Engineering Report Stack is ready."
echo "Run: npm run docs:dev"
