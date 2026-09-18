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

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .

if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

.venv/bin/python -m unittest discover -s tests -v
npm run docs:build

echo
echo "Engineering Report Stack is ready."
echo "Run: npm run docs:dev"
