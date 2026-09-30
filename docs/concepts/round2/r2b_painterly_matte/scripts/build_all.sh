#!/usr/bin/env bash
# Full pipeline for r2b_painterly_matte: Blender passes -> Pillow paint-over -> stills + contact sheet.
# Usage: build_all.sh <workdir> [samples]   (workdir = any scratch folder; it is safe to delete afterwards)
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$1"; SAMPLES="${2:-48}"
ROOT="$(cd "$HERE/.." && pwd)"
bash "$HERE/render_all.sh" "$WORK" "$SAMPLES"
cd "$HERE"
WW="$(cygpath -w "$WORK")"; SW="$(cygpath -w "$ROOT/stills")"
python make_city.py "$WW" "$SW" day night alarm
python make_combat.py "$WW" "$SW"
python make_shop.py "$WW" "$SW"
python contact_sheet.py "$SW" "$(cygpath -w "$ROOT/contact_sheet.jpg")"
