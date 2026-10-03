#!/bin/sh
# Render all 9 (option x state) at full res into scratch/, then copy finals next to SPEC.md.
D="$(cd "$(dirname "$0")/.." && pwd)"
export MF_PCT=100 MF_SAMPLES=${MF_SAMPLES:-48}
for o in f1 f2 f3; do for s in rain day night; do
  sh "$D/scripts/render_one.sh" $o $s && cp "$D/scratch/${o}_${s}.png" "$D/${o}_${s}.png"
done; done
