#!/usr/bin/env bash
# Render the design SVGs to PNG for visual comparison.
# Output goes to build/design-renders/, which Git ignores.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out="$root/build/design-renders"
mkdir -p "$out"

shopt -s nullglob
svgs=("$root"/designs-ux_ui/*.svg)
if [ ${#svgs[@]} -eq 0 ]; then
    echo "No SVG files found in designs-ux_ui/" >&2
    exit 1
fi

for svg in "${svgs[@]}"; do
    base="$(basename "$svg" .svg)"
    if command -v inkscape >/dev/null 2>&1; then
        inkscape "$svg" --export-type=png --export-filename="$out/$base.png" \
            --export-width=1366 >/dev/null 2>&1
    elif command -v rsvg-convert >/dev/null 2>&1; then
        rsvg-convert -w 1366 "$svg" -o "$out/$base.png"
    else
        echo "Install Inkscape (sudo apt install inkscape) or librsvg2-bin." >&2
        exit 1
    fi
    echo "Rendered $out/$base.png"
done
