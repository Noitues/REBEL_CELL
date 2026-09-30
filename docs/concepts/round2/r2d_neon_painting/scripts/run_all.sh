#!/bin/bash
# Full pipeline: Blender renders -> Pillow post-pass -> stills/ + contact_sheet.jpg
# usage: bash run_all.sh [samples] [tmp_dir]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../stills"
SAMPLES="${1:-64}"
TMP="${2:-$HERE/../_tmp_raw}"
BLENDER="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
mkdir -p "$OUT" "$TMP"
TMPW="$(cd "$TMP" && pwd -W 2>/dev/null || pwd)"
i=1
for shot in city_day city_night city_suspicion combat shop; do
  n=$(printf "%02d" $i)
  timeout 900 "$BLENDER" -b --factory-startup --python "$HERE/render_shot.py" -- $shot "$TMPW/raw_$shot.png" $SAMPLES > "$TMP/$shot.log" 2>&1 < /dev/null
  grep -q "^DONE" "$TMP/$shot.log" || { echo "render failed: $shot (see $TMP/$shot.log)"; exit 1; }
  python "$HERE/post.py" $shot "$TMPW/raw_$shot.png" "$OUT/${n}_$shot.png" < /dev/null
  i=$((i+1))
done
python "$HERE/contact_sheet.py" "$OUT" "$HERE/../contact_sheet.jpg" < /dev/null
rm -rf "$TMP"
