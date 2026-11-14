#!/usr/bin/env bash
# Run SongCutter from the source tree without installing the package.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m songcutter "$@"
