**Status 2026-11-04: re-rendered on the rebuilt board** (the 2026-11-03 rebuild with gate 1, as published in `../final/`). All four family sheets, all 33 strips, `timings_MPST.json`, `resolve_beat_strip.jpg` and `resolve_beat.gif` are new. AD review items **1.6, 1.8, 2.10, 2.11 and 3.10 are done** for M, P, S and T, and the resolve beat is rebuilt **under 4 s with a skip** (3800 ms). Items still open are under **Not done**.

This file covers four families: M motion, P protect, S system and T commit. That is 12 effects plus the shove-collision variant. The C, D, H and L families are in `NOTES_CDHL.md`. No game number, word or rule was changed. Nothing was committed.

## 2026-11-03 rebuild

**How the numbers were measured**
- All values are CIE L* (D65), using the rb_tokens maths. The reviewer's probe (`ad_measure.py`, copied into the source folder) uses the same L* (116 ∛Y − 16).
- Loudness, flash, layer and colour counts are measured on the 60 fps frames that the published keyframes are cut from.
- The P-stock count is measured on the published `fx_P_protect.png`.

**The board**
- Every base plate was rendered from `corp/src`, imported read-only, with the plates' own capture hooks.
- They match `../final/` to max 1-3 / 255 on p1, p2 and p3 of every skin, and the glyph diff is 0.
- `corp/src` was not edited.

### Files

| File | What it is |
|---|---|
| `fx_M_motion.png` | Spin, twist, pull, shove (plus the bump variant), rings step, hold, wave enter |
| `fx_P_protect.png` | Shield block, brace block, soak take |
| `fx_S_system.png` | Trace add |
| `fx_T_commit.png` | Commit |
| `strips/<id>_<skin>.jpg` | 33 strips, one per effect per skin, on the same skins as before. Each has 6 keyframes labelled in ms, plus a yellow-framed reduce-motion tile. The header line carries the flash and loudness numbers. |
| `timings_MPST.json` | Per effect (`effects.<id>`): `phases`, `reduce_phases`, `total_ms`, `total_ms_before_rebuild`, `flash_check` and `loudness` per skin, `layer_check_neutral`, `strips`. Also `loudness_order` (plus `_solace` and `_meridian`) and `resolve_beat_e10` (tracks, skip, flash full and reduce, GIF, strip, kill-colour check). |
| `resolve_beat_strip.jpg` | The rebuilt E10 p3 resolve beat (2900 x 2212). It holds a track chart, 17 full-motion keyframes, 5 reduce-motion keyframes and 3 skip frames. |
| `resolve_beat.gif` | The beat at 640 x 360 (plus a 20 px caption bar), 30 fps, 136 frames, 1.0 MB. Then 0.5 s of the settled frame. |

### What was done, per review finding

| # | Class | Done as | Measured |
|---|---|---|---|
| 1.6 Effects above the HUD | IMPL | Every frame is the board layer, then the effect, then the HUD and the hand (`mp_lib.comp(below, above)`), with the plates' own split. **fx_trace_add** is the one M/P/S/T effect drawn over the HUD (allowed with hp_through and refund). | `layer_check.py` checks every 60 fps frame, full and reduce, neutral. Changed px on opaque HUD or hand px: **0** for every effect whose box holds any (twist 15760, rings_step 41889, hold 21660, brace 6610, commit 189490 HUD px in the box). The other boxes hold no HUD px. trace_add changes up to 1696 px on the HUD (allowed). |
| 1.8 Kill marks | IMPL | No M/P/S/T effect draws a kill mark. In the beat, both kills are the C/D/H/L designer's fx_kill in the cause colour, CELL_PINK. The bump's two small starbursts are CELL_PINK (D material, our card). | `beat_guard.py`, round each kill token within 90 px, peak px added over the settled frame. Packet 1: 0 GAIN, 0 FOCUS, 0 lime, 2044 CELL_PINK. Worm 2: 0 / 0 / 0, 1456 CELL_PINK. |
| 2.10 Loudness order | IMPL | **Order holds on all three skins: damage > kill > block > state** (tables below). Changes, all through constants in `mp_eff.py` / `mp_lib.py`, listed after this table. | |
| 2.11 Lengths | IMPL | Every effect is **600 ms or less, with no per-effect override**. The registry asserts the total, every phase end and every reduce phase against `CAP_MS = 600`. | Old to new: spin 820 → 600, twist 660 → 540, pull 600 → 500, shove 580 → 500, bump 540 → 480, rings_step 900 → 600, hold 700 → 560, wave_enter 760 → 600, shield 920 → 600, brace 1060 → 600, soak 960 → 600, commit 760 → 600, trace_add 400 (unchanged). Reduce forms 400-600. |
| 2.11 The beat | IMPL | Rebuilt as concurrent tracks: **3800 ms against a 4000 ms limit, skip on any input** (see "Resolve beat"). | |
| 3.10 Block plate stock | IMPL | The FX-P plate, clamp brackets, soak inner line, rivet heads and sparks use their own stock, **P stock #F6C8DE** (shade #D696B8). This is the same value the C/D/H/L designer uses for the break shards (`fxk_lib.P_STOCK`), so the block and the break show one paper. It is never the card bone PAPER #F2EEE4. | P stock L* 85.1, PAPER L* 94.2, dE76 24.2 apart. On the published `fx_P_protect.png`, 55217 px fall within dE76 8 of the P stock, at median L* 84.7. On the hold frames, of the px each block adds: shield 281 P stock / 0 PAPER, brace 636 / 3, soak 133 / 0. |

**The 2.10 changes**
- **M:** the print echoes are retired: on the shared meter, the echo copies were the loudest light of every motion effect. The arrow is a 3 px core with a 2.5 px ink casing and an 11 px open head (it was 5, 4 and 15 px).
- **M stubs:** on spin, twist, shove, rings step and Hold, the arrow is a stub (60 / 30 / 30 / 32 / 22 deg, `ARROW_STUB`). It runs ahead of the mover and is eaten when the mover arrives. The pull and the bump keep their short whole arrow.
- **P:** the flat wedge tint and the SOAK wash are retired. The shield plate is small (r 186-204 x 26 deg on the trim band). The brace is four clamp brackets on the wedge corners. The brace stamp is smaller: it slams from 1.2x to 1.0x of a 16 px square (it was 1.5x to 1.0x of 18 px).
- **T:** the commit's white-hot burn edge is narrowed from 3.5 % of the route at 75 % white to 1.8 % at 60 % (`COMMIT_HOT`). The old edge measured 1277, which was louder than every block.
- **S:** one glitch band per 33 ms step, 4-7 px tall.

### Per effect (neutral first, then Solace / Meridian where drawn)

| id | fam | total ms (before) | reduce ms | loudness, shared gated meter: neutral / Solace / Meridian | brighter-only (neutral) | flash max per s, full / reduce (worst skin) |
|---|---|---|---|---|---|---|
| fx_spin | M | 600 (820) | 520 | 584 / - / - | 241 | 1 / 1 |
| fx_twist | M | 540 (660) | 520 | 382 / 382 / 380 | 222 | 1 / 0 |
| fx_pull | M | 500 (600) | 520 | 200 / 200 / 197 | 127 | 1 / 0 |
| fx_shove | M | 500 (580) | 520 | 358 / 353 / 352 | 245 | 1 / 0 |
| fx_shove_bump | M | 480 (540) | 480 | 698 / 704 / 697 | 461 | 1 / 1 |
| fx_rings_step | M | 600 (900) | 520 | 611 / 613 / 613 | 594 | 1 / 0 |
| fx_hold | M | 560 (700) | 520 | 761 / 768 / 761 | 475 | 0 / 0 |
| fx_wave_enter | M | 600 (760) | 600 | 630 / 642 / 550 | 548 | 0 / 0 |
| fx_shield_block | P | 600 (920) | 600 | 1276 / 1277 / 1276 | 962 | 1 / 1 |
| fx_brace_block | P | 600 (1060) | 600 | 1677 / 1678 / 1678 | 1041 | 1 / 1 |
| fx_soak_take | P | 600 (960) | 600 | 841 / - / - | 584 | 1 / 1 |
| fx_trace_add | S | 400 (400) | 400 | 720 / - / - | 399 | 2 / 0 |
| fx_commit | T | 600 (760) | 600 | 749 / 749 / 749 | 358 | 0 / 0 |

**Every effect passes the flash check on every skin, in full and in reduce motion** (limit 3 per s). The flash method is unchanged (see History, "Flash check: method").

**Meters**
- **Loudness** is the shared gated meter, the C/D/H/L designer's `fxk_lib.loud_frame`, read from a read-only snapshot. A px counts when it differs by dE76 > 5 both from the same frame with the effect's marks off and from the settled frame. Each px is weighted by L* / 100, and the loudness is the peak over all frames.
- **Brighter-only** is the M/P/S/T measure from before the rebuild. It is kept as a second number and is not used for the order.

### Loudness order (review 2.10), all eight families on one meter

| Tier boundary | neutral | Solace | Meridian |
|---|---|---|---|
| damage min > kill max | hit_land 2817 > kill 1813 | 2817 > 1816 | 2817 > 1812 |
| kill min > block max | kill 1813 > brace_block 1677 | 1816 > 1678 | 1812 > 1678 |
| block min > state max | soak_take 841 > hold 761 | 841 > 768 | 841 > 761 |

**Kinds**
- Damage: D and H. Kill: fx_kill. Block: P and the ricochets.
- State: C, M, S, T and L gain. The C/D/H/L designer ranks gain with state.
- The C/D/H/L fx_shield_block is their comparison copy for the block-vs-break sheet, so the real P block stands for it.

**Neutral ranks**

| Kind | Effects and loudness |
|---|---|
| Damage | firewall_burn 9540, shield_break 8377, strike 5490, trigger_hit 5074, slice_break 4778, hit_land_adjuster 3749, gun_hit 3748, slice_crack 3121, hp_through 3035, hit_land_worm 2822, hit_land 2817 |
| Kill | kill 1813 |
| Block | brace_block 1677, shield_block 1276, ricochet 898, ricochet_gold 885, soak_take 841 |
| State | hold 761, commit 749, trace_add 720, repair_mend 700, shove_bump 698, refund 675, wave_enter 630, rings_step 611, spin 584, grow 533, ward_on 391, twist 382, shove 358, pull 200, clear 85 |

**Margins.** The thinnest margin is block > state: soak 841 against hold 761, which is 80 (73 on Solace). It passes, but any louder state effect would break the order.

The full rows are in `timings_MPST.json` `loudness_order*`, built by `mp_order.py`.

### Resolve beat (review 2.11)

**Reading order and sources**
- Each effect is its designer's own, at its own timing, and each is 600 ms or less.
  - M, P, S and T come from `mp_eff`.
  - C, D, H and L come from `fx_cdhl`, as a read-only snapshot of their 2026-11-04 03:35 source: the one their published plates use. Their totals match `timings_CDHL.json` for all 19 effects.
- The tracks overlap and play in the HUD chain order.

| ms | track | source in the state (E10 f2 / p3) |
|---|---|---|
| 0-600 | commit | SEND IT: the pencil marks burn into paint. The HUD steps from preview to resolve. |
| 420-960 | twist | 1 TWIST: ring +1 turns one sector |
| 600-1000 | trace_add | 2 TRIGGER: Trace 3 → 4 (over the HUD, allowed) |
| 760-1360 | trigger_hit | 2 TRIGGER: Packet 1 is hit in s3 at 120 ms and in s4 at 240 ms (the CDHL `in_sequence` clock) |
| 1000-1600 | kill (Packet 1) | 2 TRIGGER: Packet 1 dies |
| 1100-1700 | refund | 2 TRIGGER: refund, RAM 2 → 3 (over the HUD, allowed) |
| 1300-1900 | gun_hit | 4 GUNS: s0, shot 1 on Worm 2 |
| 1360-1960 | gun_hit (Adjuster) | 4 GUNS: s2 TURRET on the Adjuster |
| 1420-1920 | ricochet_gold | 4 GUNS: s4, 2 shots warded by Packet 6 |
| 1560-2160 | kill (Worm 2) | 4 GUNS: s0, shot 2, Worm 2 dies |
| 1900-2500 | shield_block | 5 LANDS: Worm 3 on s1 SHIELD, absorbed 2 |
| 1900-2500 | brace_block | 3 BRACE / 5 LANDS: Worm 3 on s2, braced 3 |
| 1930-2530 | soak_take | 5 LANDS: s1 soaked 1. Drawn under the shield plate, so the plate stays whole. |
| 2400-2800 | clear | 5 LANDS: THROUGH 0 |
| 2640-2840 | settle | Board hand-off: ring NOW clears (a 200 ms dissolve) |
| 2800-3400 | rings_step | 6 RINGS STEP |
| 3200-3800 | wave_enter | 6 W4 enters |

**Skip**
- Any input dissolves the frame on screen to the settled frame over 200 ms (easeInOutCubic).
- There is no on-screen word. That is an open question for the designer.

**Layer**
- Same split as the strips. Every effect is on the board, under the HUD and the hand.
- Only trace_add and refund are drawn over the HUD.

**Flash, 60 fps, the method in this file**
- Regions: the whole frame, each track's box over the whole beat, and every 240, 120 and 60 px tile on a half stride (106 / 385 / 1409 tiles in full motion). Skip paths start every 250 ms from 250 to 3750, and each is measured from 1 s before the skip.

| | whole frame | track boxes | 240 px | 120 px | 60 px | skips (worst) | result |
|---|---|---|---|---|---|---|---|
| full motion | 0 | 1 | 2 | 2 | 3 | 3 (skips at 2000, 2250, 2500) | pass |
| reduce motion | 0 | 0 | 1 | 2 | 2 | 2 | pass |

- **At the limit:** one 60 px tile at (300, 480) holds 3 flashes in one second, at 1617, 1733 and 1783 ms. They are the C/D/H/L kill and gun-hit cluster on the Worm 2 token. The skips at 2000-2500 count the same cluster inside their 1 s window; the dissolve itself adds 0-1.
- Nothing is over 3. Measured on neutral; the strips carry the per-skin checks.

**GIF palette.** The GIF uses one 255-colour palette taken from 32 frames, by median cut refined with k-means.
- Measured against the source frames: mean dE76 2.6, p95 8.4.
- The earlier 8-frame median cut measured 4.0 / 15.9, and it turned the slice inks: olive went tan and green went teal.

**NOT TO SHIP (rules question)**
- The state, f2, holds ring +1 where Twist leaves it, but the plates draw ring +1 untwisted.
- So the beat draws ring +1 one sector back from SEND IT until Twist turns it. This follows REVIEW_RESPONSE "Shove bump, Twist render", which marks it RULES.
- The strip header says so, and the GIF caption says so during 0-960 ms.

### Rulings this set follows (so a reader takes them as decided, not as defects)

| Ruling | Source | How this set follows it |
|---|---|---|
| The arrowed outline is kept | Designer, DR-1 (VISUAL_PLAN) | The L5 marks are the board's: the THIS TURN schedule cell, the W4 queue feed and the hover path on the hover plates. They are untouched. The M resolve arrow is the effect's own short arrow, as it was before the rebuild, only thinner and as a stub. It is solid, never dashed (DR-1). |
| Motion colour by owner; yellow never in resolve | VISUAL_PLAN E "R51 review: motion colour" (the reviewer agreed, REVIEW_RESPONSE S3) | Cards (spin, twist, pull, shove, bump, commit ping) are CELL_PINK. The clock (rings step and Hold's slide) is SCHEDULE #FF8C1A, and the Hold stamp is the clock's gunmetal. The wave feed is neutral ENAMEL. |
| Corp theme by material, corp hue only on rim, lip, crest and cell edges | Designer, DR-6 | In wave_enter, the corp hue is only the scan line that draws the new cell edges. |
| No reserved fill colours | Designer, DR-5 | The P stock is a fill. Meaning tokens stay on marks: SOAK on the soak funnel. |
| Shove bump HP; Twist render | REVIEW_RESPONSE S3: RULES, open for the designer and the GDD | The bump draws no HP change. The beat's Twist workaround is marked NOT TO SHIP. |
| Beat under 4 s with skip; 0.6 s T2 cap, no overrides | REVIEW_RESPONSE 2.11 (an art-pass call, not a designer ruling) | As above. |

### Documents that now disagree with this set (shared files, not edited here)

These still describe the set before the rebuild. **Call:** they should take their values from `timings_MPST.json` (`effects.<id>`, `resolve_beat_e10`) and from this section.
- `VISUAL_PLAN.md` G:
  - The FX-M row says "Smear frames (3 echo copies...)". The echoes are retired.
  - The FX-P row says "over the wedge's outer 40 percent". It is now the small plate and the clamp brackets.
  - The fx_shield_block row says "white sparks". The sparks are now P stock.
  - The fx_spin, fx_twist and fx_rings_step rows give 12f / 16f echoes, and the fx_twist row says "Orange L5 sweep", where R51 says pink.
- `ART_BIBLE_COMBAT_DRAFT.md` FX table: M "Three print echoes" and P "A bone #F1EAD6 plate".
- `GODOT_PORT_SPEC.md`:
  - the M echo spec (print echoes at 26 / 52 / 78 ms);
  - Appendix A rows with the old totals (580-1060 ms);
  - the 8.2 sequencing of a 12.7 s beat.
- `port/fx_timings.json`: the old totals and the O-30 `resolve_beat_e10`.

### Not done

1. **The Twist workaround is not to ship.** It is a rules question. Until the designer rules, the beat is not a shipping reference for ring +1 during 0-960 ms.
2. **Skip has no on-screen word.** This is open for the designer.
3. **Packet 1 is never seen alive.** p2 already draws it trigger-dead, so the beat plays fx_kill's KO burst over its empty cell at 1000 ms. A pre-state plate with Packet 1 drawn (from the generator) would fix it.
4. **The Adjuster shot (guns s2, h 1) has no HP-tick change in the beat.** It plays the gun-hit tracer and burst, and the board's own hatched segment stands.
5. **The shared documents listed above are not updated,** including `port/fx_timings.json`. They are other owners' files.
6. **The block-vs-break comparison copy does not match this block.** The C/D/H/L designer's copy on `fx_block_vs_break.png` throws white sparks; the real P shield block throws P-stock sparks. Their file; for them to align.
7. **`corp/src` is order-dependent.** Rendering Solace or Meridian p3 after p1_clean in the same process drew a wrong TWIST glyph. Here each plate was rendered in its own process (glyph diff 0 against `../final/`). The bug itself is reported, not fixed: not my file.
8. The P stock is aligned with the C/D/H/L value but is **not yet a token in rb_tokens**.

### Source

`D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/`:
- `mp_lib.py`: layers, the arrow, the flash meter, P stock.
- `mp_eff.py`: the 13 effects and the `CAP_MS` asserts.
- `mp_run.py` and `mp_strips.py`: one effect on one skin: frames, flash, loudness, strip.
- `mp_order.py`, `mp_sheets.py`.
- `mp_beat.py`, `mp_beat_render.py`, `mp_beat_meter.py`, `mp_beat_out.py`.
- `layer_check.py`, `beat_guard.py`, `pstock_measure.py`, `notes_tables.py`.
- `../cdhl_snap/`: the read-only snapshot of `fx_cdhl.py` and `fxk_lib.py`, with md5 sums in `SNAPSHOT_TIME.txt`.

Frames, meters and JSON are in `../work/`.

### Process

- No Godot, no Blender, nothing committed.
- Nothing was written under D:/Godot/rebel_cell, and `corp/src` and the C/D/H/L source were not edited.
- **Rule slips: I ran `python -c` four times with empty or trivial code** (`pass`, `print(1)` and an empty string) inside shell chains. None was a bare `python -`, and none ran or wrote anything. All real work ran from script files.
