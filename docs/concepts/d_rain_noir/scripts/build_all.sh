#!/usr/bin/env bash
# Full pipeline: Blender renders (raw, to $RAW) -> tilt-shift (city) -> post -> stills/ -> strip -> contact sheet.
# Usage: bash scripts/build_all.sh [01 02 03 04 05]   (default: all). Env: RAW (scratch dir), RN_SAMPLES, RN_PCT.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/../stills"
RAW="${RAW:-${TMP:-/tmp}/rn_raw}"
mkdir -p "$RAW" "$OUT"
export LOGDIR="$RAW"
W() { (cd "$1" && pwd -W 2>/dev/null || pwd); }
R="$(W "$RAW")"
todo="${*:-01 02 03 04 05}"
for s in $todo; do
  case $s in
    01) bash "$HERE/run.sh" s01_combat "$R/01.png" && python "$HERE/post.py" "$RAW/01.png" "$OUT/01_combat.png" --seed 1 --grain 5 ;;
    02) bash "$HERE/run.sh" s02_city_night "$R/02" && python "$HERE/tiltshift.py" "$RAW/02_beauty.png" "$RAW/02_depth.png" "$RAW/02_fog.json" "$RAW/02_ts.png" \
          && python "$HERE/post.py" "$RAW/02_ts.png" "$OUT/02_city_night.png" --seed 2 --grain 5 ;;
    03) bash "$HERE/run.sh" s03_heat "$R/03" && python "$HERE/tiltshift.py" "$RAW/03_beauty.png" "$RAW/03_depth.png" "$RAW/03_fog.json" "$RAW/03_ts.png" --seed 4 \
          && python "$HERE/post.py" "$RAW/03_ts.png" "$OUT/03_heat.png" --seed 3 --grain 6 --glitch 0.3 --desat 0.25 ;;
    04) bash "$HERE/run.sh" s04_hq_modem "$R/04.png" && python "$HERE/post.py" "$RAW/04.png" "$OUT/04_hq_modem.png" --seed 4 --grain 5 ;;
    05) bash "$HERE/run.sh" s05_marker_strip "$R/05" && for k in 1 2 3; do python "$HERE/post.py" "$RAW/05_stage$k.png" "$RAW/05_stage${k}_p.png" --seed $k --grain 5 --vignette 0.2; done \
          && python "$HERE/strip_layout.py" "$RAW/05_stage1_p.png" "$RAW/05_stage2_p.png" "$RAW/05_stage3_p.png" "$OUT/05_marker_strip.png" ;;
  esac
done
if [ -f "$OUT/01_combat.png" ] && [ -f "$OUT/05_marker_strip.png" ] && [ -f "$OUT/02_city_night.png" ] && [ -f "$OUT/03_heat.png" ] && [ -f "$OUT/04_hq_modem.png" ]; then
  python "$HERE/contact_sheet.py" "$OUT" "$HERE/../contact_sheet.jpg"
fi
