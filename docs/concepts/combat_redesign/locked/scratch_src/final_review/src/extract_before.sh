#!/bin/sh
# Extract the 090ad870 versions of the plates used in review_rebuild.jpg
cd D:/rc_art/art-pass || exit 1
OUT=D:/rc_scratch/combat_redesign/locked/final_review/before
B=docs/concepts/combat_redesign/locked
for f in final/p1_decide.png final/p1_decide_solace.png final/p1_decide_meridian.png final/p2_preview.png \
         final/p2b_hover.png final/p3_resolve.png final/p1_nowords.png final/card_sheet.jpg \
         hover/h02_brace.png hover/h03_trigger.png hover/h04_twist.png hover/h05_strike.png \
         effects/fx_C_corp.png effects/fx_D_damage.png effects/fx_P_protect.png effects/resolve_beat_strip.jpg \
         effects/fx_block_vs_break.png \
         backdrop/p1_bio.png backdrop/p1_bio_meridian.png \
         transitions/sheet.jpg transitions/strip_t5.jpg transitions/strip_t6.jpg; do
  name=$(echo "$f" | tr '/' '_')
  git show "090ad870:$B/$f" > "$OUT/$name" || echo "FAIL $f"
done
ls -la "$OUT"
