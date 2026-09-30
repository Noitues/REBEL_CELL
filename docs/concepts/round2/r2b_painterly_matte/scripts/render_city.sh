#!/usr/bin/env bash
# Renders the city passes into a work folder. Usage: render_city.sh <workdir> [samples] [modes...]
# Runs the modes in parallel; each Blender log goes to <workdir>/<mode>.log.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$1"; SAMPLES="${2:-64}"; shift; shift || true
MODES="${*:-day night alarm depth}"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
mkdir -p "$WORK"
WW="$(cygpath -w "$WORK")"
for m in $MODES; do
  timeout 900 "$BL" -b --factory-startup --python "$(cygpath -w "$HERE/city_scene.py")" -- \
    "$m" "$WW\\city_$m.png" "$WW\\city_$m.json" "$SAMPLES" > "$WORK/$m.log" 2>&1 &
done
wait
grep -h "^DONE" "$WORK"/*.log
