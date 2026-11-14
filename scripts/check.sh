#!/usr/bin/env bash
# Lint and test the source tree.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
export PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}"

if python3 -m ruff --version >/dev/null 2>&1; then
    python3 -m ruff check src tests
else
    echo "ruff is not installed; skipping lint (pip install -r requirements-dev.txt)" >&2
fi

exec python3 -m pytest "$@"
