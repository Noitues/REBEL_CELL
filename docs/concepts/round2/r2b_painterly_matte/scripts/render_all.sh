#!/usr/bin/env bash
# Renders every Blender pass for r2b_painterly_matte into <workdir>. Usage: render_all.sh <workdir> [samples]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$1"; SAMPLES="${2:-48}"
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
mkdir -p "$WORK"; WW="$(cygpath -w "$WORK")"
bash "$HERE/render_city.sh" "$WORK" "$SAMPLES" day night alarm depth
timeout 900 "$BL" -b --factory-startup --python "$(cygpath -w "$HERE/spinner_scene.py")" -- "$WW" "$SAMPLES" > "$WORK/spin.log" 2>&1 &
timeout 900 "$BL" -b --factory-startup --python "$(cygpath -w "$HERE/shop_scene.py")" -- beauty "$WW\shop_beauty.png" "$SAMPLES" > "$WORK/shop.log" 2>&1 &
timeout 900 "$BL" -b --factory-startup --python "$(cygpath -w "$HERE/shop_scene.py")" -- depth "$WW\shop_depth.png" > "$WORK/shopd.log" 2>&1 &
wait
grep -h "^DONE" "$WORK"/*.log
