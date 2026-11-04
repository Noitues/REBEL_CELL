# Effects on the locked board: M motion, P protect, S system, T commit

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

## History (before the 2026-11-03 rebuild; superseded)

Everything below is the record of the earlier passes (roadmap step 4, O-30, O-30 board). Its totals, echoes, flash numbers and file sizes describe plates that no longer exist; the rebuild section above replaces them. It is kept so earlier reviews can be traced.

This section covers the four families M, P, S and T: 12 effects plus the shove-collision variant. The C, D, H and L families are in their own notes. Every effect is rebuilt on the final locked plates (`../final/`, state E10). Corp-side versions are drawn for Solace and Meridian wherever the effect crosses corp rings. No game number, word or rule was changed, and nothing was committed.

### Files

| File | What it is |
|---|---|
| `fx_M_motion.png` | Spin, twist, pull, shove (plus the bump variant), rings step, hold, wave enter |
| `fx_P_protect.png` | Shield block, brace block, soak take |
| `fx_S_system.png` | Trace add |
| `fx_T_commit.png` | Commit |
| `strips/<id>_<skin>.jpg` | One strip per effect per skin (33 files, each under 2 MB). It holds 6 keyframes labelled with ms, plus a yellow-framed reduce-motion tile |
| `timings_MPST.json` | Per effect: phases (start, end, easing), total, keyframe times, skins, the reduce-motion note, and the measured flash check per skin (full motion and reduce motion) |

Each sheet block carries:
- the STILL, SOURCE, STYLE MUST KEEP, REDUCE MOTION and NOTE lines;
- a timing chart (phases on a ms axis, with easing);
- the flash panel: per skin, the mean-luminance curve for full and reduce motion, plus the numbers;
- the neutral strip, with the Solace and Meridian strips under it.

Generator: `D:/rc_scratch/combat_redesign/locked/fx_mpst/src/`.
- `fxlib.py`: geometry, polar remaps, the 3x overlay layer, easing, the arrowed outline and the flash check.
- `fx_eff.py`: the 12 effects and the bump variant.
- `render_bases.py`: extra base plates from the shared generator, imported read-only.
- `run_fx.py`: one effect on one skin, giving its frames, check and strip.
- `build_sheets.py`: the sheets and `timings_MPST.json`.

The shared generator files were not edited.

### Effects and skins

| id | fam | skins | total ms | source in the state |
|---|---|---|---|---|
| fx_spin | M | neutral (tower only, the same on every corp) | 820 | f1 hand Spin 3: the tower turns 3 sectors |
| fx_twist | M | neutral, Solace, Meridian | 660 | f2 Twist [1, 1]: ring +1 turns one sector clockwise |
| fx_pull | M | neutral, Solace, Meridian | 600 | Pull ("Pull a unit in"), shown on Packet 7, ring +2 to ring +1, sector 5 |
| fx_shove | M | neutral, Solace, Meridian | 580 | Shove ("Slide a unit 1"), shown on Packet 5, ring +1, sector 0 to 1 |
| fx_shove_bump | M (D variant) | neutral, Solace, Meridian | 540 | Shove into an occupied cell: Packet 7 bumps Packet 6 and springs back |
| fx_rings_step | M | neutral, Solace, Meridian | 900 | END TURN, schedule [2, 0, 0]: one ring in, plus 2 sectors |
| fx_hold | M | neutral, Solace, Meridian | 700 | Hold: schedule [2, 0, 0] becomes [0, 2, 0] |
| fx_wave_enter | M | neutral, Solace, Meridian | 760 | W4 ticket (Jammer w1 s0, Jammer w2 s4) enters ring +2 |
| fx_shield_block | P | neutral, Solace, Meridian | 920 | f2: Packet 5 lands 2 on sector 3 SHIELD, absorbed 2 |
| fx_brace_block | P | neutral, Solace, Meridian | 1060 | f2: Brace on sector 2 TURRET, Worm 3 braced, through 0 |
| fx_soak_take | P | neutral (tower wedge only) | 960 | f2: sector 1 SHIELD soaked 1 |
| fx_trace_add | S | neutral (card and HUD) | 400 | Trigger played: Trace 3 to 4 |
| fx_commit | T | neutral, Solace, Meridian | 760 | SEND IT on the best line: the p2 marks become the p3 marks |

The rings-step geometry matches the state: a unit lands at its sector plus the live schedule value.
- Packet 5 (s0) lands on 2.
- Payload 4 (s3-4) lands on 5 and 0.
- Packet 7 (s5) lands on 1.
- Packet 6 (s2-4) lands on 4, 5 and 0 after +2 then +0.

So the step brings each unit one ring in and turns it 120 degrees clockwise.

### Family materials (distinct from the skins)

**M motion**
- The material is print echoes plus the arrowed outline. Three echoes trail at 26, 52 and 78 ms (9, 18 and 27 ms on the fast tower). They are tinted 25 % toward the mover's colour and exist only while the thing moves.
  - On a turning disc or ring, an echo shows only where it differs from the current frame (edges, icons, marks), so the board stays legible.
  - Unit cells slide as their own layer: p1 minus an empty-board render. The ring material stays put, except on Twist, where the ring itself turns.
- The colour says who moves it:
  - Pink: the Cell's card at resolve. Pencil yellow is the hover form only.
  - Silver: the clock. It is the THIS TURN tape stock with a white specular core, drawn at r 426 beside the tape and never on it.
  - Corp colour: the enemy wave. That is lime on Solace, orange on Meridian, and graphite enamel on the neutral corp.
- Orange is no longer the clock colour. It is now the WAVE card colour and Meridian's hazard rim.

**P protect**
- Bone card #F1EAD6 with a 3.4 px ink key line, a pink double line, ink rivets, and a hard offset shadow (3, 5) at 55 %.
- Tints are flat (pink 18 % for a block, SOAK 16 % for a soak). Impacts throw white spark ticks.
- No starburst (that is D), no red on the plate (H), no glow.
- The plates stay clear of the icon and the pips:
  - the shield plate sits at r 171-203;
  - the clamp is a frame round the wedge;
  - the funnel apex stops at r 158.

**S system**
- Stepped violet glitch: band shears of 6 px, a 3 px R/B split, a 35 % violet tint, and scanlines.
- 33 ms steps, with new rows at every step, so no pixel flickers twice.
- The settled pip is cut from the HUD's own lit pip. Violet means Trace only.

**T commit**
- Pencil yellow becomes the generator's pink resolve mark. The front runs in geodesic order along each mark from the route start and is white-hot 2 frames deep.
- A pink ping marks the route end. Then the rest of the board steps from preview to resolve.

None of the four uses facets (the WPAP cards), paper inks or Ben-Day (the spinner), enamel fills (the corp rings), or cyan (the HUD).

### Flash check: method

The numbers are per skin in `timings_MPST.json` and on each sheet's flash panel.

1. Every frame of the effect is rendered at 60 fps over its whole length plus 100 ms. Each frame is converted to WCAG relative luminance (linear sRGB, 0.2126 R + 0.7152 G + 0.0722 B). Frames are decimated 2x2 for speed, which leaves area fractions unchanged.
2. **Region the effect covers (footprint):** every pixel whose luminance moves more than 0.02 from frame 0 at any time. This is stricter than using the crop, because a small effect is judged against its own area.
3. **Per pixel:** an extremum tracker logs a swing event when the luminance moves 0.10 or more (10 % of full scale) away from the last extreme, in the opposite direction from the last swing. A slow ramp counts once, and jitter under 0.10 never counts.
4. **Region event:** 25 % or more of the footprint swings the same way within a 100 ms window (6 frames).
5. **Flash:** two opposite region events, up then down or down then up. **Pass:** no 1 s window holds more than 3 flashes.
6. Also logged: the per-frame mean luminance of the footprint (the curve), its largest frame-to-frame step, and its range.

### Flash check: results

The same method runs on the reduce-motion variant.

| id | full motion: flashes, max per s (neutral / Solace / Meridian) | largest area swinging at once | reduce motion max per s |
|---|---|---|---|
| fx_spin | 1, 1 | 65 % | 1 |
| fx_twist | 1, 1 / 1, 1 / 1, 1 | 29-32 % | 0 |
| fx_pull | 0 / 0 / 0 | 18-21 % | 0 |
| fx_shove | 1 / 1 / 1 | 37-42 % | 0 |
| fx_shove_bump | 1 / 1 / 1 | 34-44 % | 1 |
| fx_rings_step | 1 / 1 / 1 | 28-33 % | 0 |
| fx_hold | 1 / 1 / 1 | 30 % | 1 |
| fx_wave_enter | 0 / 0 / 0 | 23-25 % | 0 |
| fx_shield_block | 1 / 1 / 1 | 49-50 % | 2 |
| fx_brace_block | 1 / 1 / 1 | 47-54 % | 2 |
| fx_soak_take | 0 | 22-27 % | 1 |
| fx_trace_add | 1 | 50 % | 0 |
| fx_commit | 0 / 0 / 0 | 15 % up, 54 % down (one way only) | 0 |

**All 13 effects (12 plus the bump variant) pass on every skin, in full and reduce motion.**
- The worst case is 1 flash per second in full motion and 2 in reduce motion.
- Each counted flash is the effect arriving and leaving, for example the plate going on and off. No effect strobes.
- The reduce-motion 2 on shield and brace comes from the plate and the stopped chevrons fading in and out as two separately timed layers.
- The check is per effect. Effects that share one beat are sequenced by the layer order in VISUAL_PLAN G (GUNS, then LANDS, then RINGS STEP, then W4 enters), so they never stack in the same 100 ms window.

### Reduce motion (per effect)

All of these are on the sheets and in `timings_MPST.json`. In every reduce form: no echoes, no travel, no overshoot, no sparks and no glitch steps. State changes become dissolves of 260-300 ms, and arrows, plates and stamps appear whole with a 100-120 ms fade.

| Effect | Reduce-motion form |
|---|---|
| Spin, Twist, Pull, Shove | The arrow appears, and the moved thing dissolves from the old place to the new one |
| Rings step | Every cell dissolves into its new ring and angle |
| Hold | The band dissolves to the new schedule |
| Wave enter | The ticket fades out, the new cells fade in, and the queue cross-fades |
| Shield and brace | Everything appears with the chevrons already stopped; the brace stamp stays |
| Soak | The funnel, wash and pip appear, and the flow chevrons are still |
| Trace | The pip lights in one step |
| Commit | Yellow cross-fades to pink, then the board steps to resolve |

### Honest caveats

1. **Pull and Shove targets are examples.** Neither card is in the E10 hand, so each is shown on a unit with an empty legal target cell.
2. **Shove collision is drawn here even though it is a D effect.** `fx_shove_bump` is registered in the D family in the round-2 source. NOTES_CDHL does not cover it, so it is drawn on the M sheet as a variant of Shove, using the D material (small keylined pink starbursts on the shared edge).
   - Round 2 said both units lose a tick on a bump. That rule is not in the E10 state, so the effect draws no HP change. This is an open point for the designer.
3. **What moves and what does not redraw during the effect:**
   - The moved cells keep their old HOT/COLD/FAR grade.
   - Ring tags (NOW W1, +1 W2, +2 W3) and the landing arcs are not moved. Rings step lifts the arcs off and does not redraw them.
   - The schedule tape keeps its cells after Rings step.
   - Spin fades the gun-preview marks, which aim from the old slice positions.
   - All of these are redrawn by the board for the next state, not by the effect.
   - On Shove the moved token comes to rest over the +1 W2 tag until that redraw.
4. **The Adjuster (amber boss arc on ring +1) is not moved by Rings step.** It does turn with ring +1 in Twist. No rule for the boss at END TURN was found in the state.
5. **Wave enter draws the new W4 cells as enamel outlines** with the ticket's Jammer glyphs. The full unit cells come from the next board redraw. Also, no plate exists without the tickets, so the vacated queue slot is drawn as a dark empty slot.
6. **Hold is shown as a demonstration** (the card is not in the hand). Its end state is the generator's own render of schedule [0, 2, 0].
7. **Rings step, Hold and Wave enter are the busiest strips.** They read best on the sheets, where the neutral strip is drawn larger. Wave enter's scan-in outlines and glyphs are small at strip scale.
8. **Soak take:** the board's own soak hatch is already on sector 1 in p3. So the pip "drain" is a SOAK fill sweeping over that pip, which then hands back to the printed hatch.
9. **Process:** no Godot, no Blender, nothing committed, nothing written under D:/Godot/rebel_cell. Base renders and frames are under `D:/rc_scratch/combat_redesign/locked/fx_mpst/`.

### O-30 pass

This pass answers the art director's fix 4: the full E10 p3 resolve beat is now sequenced on the final board and flash-measured as a whole. It also fixes the reduce-motion versions of shield_block and brace_block, and checks the fx_refund RAM count. No game number, word or rule was changed. Nothing was committed.

#### New files
| File | What it is |
|---|---|
| `resolve_beat_strip.jpg` | 16 keyframes of the whole beat, each labelled with its sequence time and its time inside the effect. A timeline row shows every step, and two rows of ticks mark every counted flash (full and reduce motion). |
| `resolve_beat.gif` | The whole beat at 960x540, 20 fps, 13.0 s, 2.3 MB. A 30 fps copy is at `D:/rc_scratch/combat_redesign/locked/fx_o30/resolve_beat_full_960_30fps.gif`. |
| `strips/fx_shield_block_*.jpg`, `strips/fx_brace_block_*.jpg` | Re-rendered on all three skins with the new reduce-motion timing. |

Changed JSON entries:
- `timings_MPST.json`: in fx_shield_block and fx_brace_block, `reduce_motion`, a new `reduce_phases`, and `flash_check` on all three skins.
- `timings_CDHL.json`: fx_refund `source`, and a new `in_sequence` note on fx_trigger_hit.
- `port/fx_timings.json`: the same entries, plus a new top-level `resolve_beat_e10` block. It holds the step list, the gaps and the measured numbers, and it is meant as the golden sequence for `FlashLimiter.stream_is_safe`. The effect count stays at 32.

Source: `D:/rc_scratch/combat_redesign/locked/fx_o30/src/`.
- `o30_seq.py` is the sequencer.
- `o30_render.py` builds the canvases and the frames.
- `o30_meter.py` is the flash meter.
- `o30_publish.py` builds the strip and the GIF.
- `o30_json.py` writes the JSON.

It works from copies: `fx_eff.py`, `fxlib.py`, `fx_cdhl.py` and `fxk_lib.py` come from the two effects folders, and the generator copy in `gen_src/` comes from `final/src_snapshot`. `corp/src` was not touched.

#### The beat
The order is the p3 HUD chain (1 TWIST, 2 TRIGGER, 3 BRACE, 4 GUNS, 5 LANDS, 6 RINGS STEP / W4 enters), opened by SEND IT. Brace's block plays where the braced landing stops, in LANDS, as spec 8.3 says.

Spacing follows spec 8.2:
- Effects run one after another. Each starts 100 ms after the previous one ends, so no two effects share a 100 ms window.
- One exception, found by the meter: the END TURN hand-off holds 400 ms before RINGS STEP (see the results).

Each effect is the designers' own render function. Its base plate is the previous step's settled frame, so nothing pops between effects.

| ms | step | source in the state (f2) |
|---|---|---|
| 0-760 | fx_commit | SEND IT on the best line: p2 pencil becomes p3 paint. The HUD outside the commit box steps from preview to resolve at 560-760. |
| 860-1520 | fx_twist | Twist [1, 1]: the ring +1 unit cells (Payload 4, Packet 5) turn one sector into their p3 places, with pink arrows and echoes |
| 1620-2020 | fx_trace_add | Trigger played: Trace 3 to 4. Retargeted to the p3 HUD: the TRIGGER PLAYED slot glitches, then TRACE pip 4 at (1510, 513) lights. |
| 2120-3020 | fx_trigger_hit | tlog trig_unit: Payload 4's trigger hits Packet 1 in sector 3, then sector 4 |
| 3120-4030 | fx_refund | tlog trig_refund: Packet 1 dies, +1 RAM, RAM 2 to 3 |
| 4130-4730 | fx_gun_hit | guns: sector 0 BURST, shot 1 on Worm 2 (h 1) |
| 4830-5430 | fx_kill | shot 2: Worm 2, hp 2 to 0 (fate dies) |
| 5530-6050 | fx_ricochet_gold | guns: sector 4 BURST, 2 shots warded by Packet 6 (h 0) |
| 6150-7070 | fx_shield_block | Worm 3 lands 3 on **sector 1** SHIELD: absorbed 2 |
| 7170-8130 | fx_soak_take | the same landing: soaked 1 |
| 8230-9290 | fx_brace_block | Worm 3 lands 3 on sector 2 TURRET: braced 3, through 0 |
| 9390-10190 | fx_clear | LANDS 3, THROUGH 0 |
| 10290-10550 | settle (sequencer step) | a 260 ms dissolve: Worm 3 and the spent gun marks leave ring 0, and the old arcs, the clear wash and the brace stamp lift off the lanes |
| 10950-11850 | fx_rings_step | END TURN, schedule [2, 0, 0] |
| 11950-12710 | fx_wave_enter | W4 (Jammer w1 s0, Jammer w2 s4) enters ring +2 |

Changes the sequence needed, all kept in the sequencer except the reduce-motion fix:

1. **shield_block moved to sector 1.** The stand-alone strip shows Packet 5 on sector 3. Packet 5 is k = 1, so it lands next turn. On this END TURN the only landing is Worm 3: sector 1 absorbs 2 and soaks 1, and sector 2 braces 3. The sequence draws the same plate on sector 1 (`make_shield(60)` in `o30_seq.py`).
2. **trigger_hit inside the sequence** drops its pencil-yellow ignite, because fx_commit has already burned the route and the Xs into paint. Drawing yellow again would turn paint back into pencil. The bursts keep their clock (sector 3 at 230 ms, sector 4 at 420 ms). This is written into `in_sequence` in both JSONs.
3. **Arc lift moved into the settle step.** In the stand-alone fx_rings_step, the old landing arcs lift off during its own 0-160 ms anticipate. In the sequence they lift in the settle step, so they never share a window with the tape arrow.
4. **HUD pre-state.** Until fx_trace_add, TRACE pip 4 shows unlit. Until the refund coin lands, RAM slot 3 shows empty. Both use the HUD's own pixels.

#### Flash meter over the whole beat
The method is the one in this file: 60 fps, WCAG relative luminance, footprint 0.02, swing 0.10, a 25 % area event in 100 ms, a flash is a pair of opposite events, and the limit is 3 in any 1 s. It runs over all 787 frames, which include 100 ms of p2 before SEND IT and 300 ms of the settled frame after.

Regions, each judged against its own footprint:
- the whole frame;
- each effect's crop box, over the **whole** beat, so hand-offs and neighbours count against it;
- every 240, 120 and 60 px tile on a half-size stride (104, 354 and 1,263 tiles).

| | whole frame | effect boxes | 240 px tiles | 120 px tiles | 60 px tiles | result |
|---|---|---|---|---|---|---|
| full motion, first run (all gaps 100 ms) | 0 | 1 | 2 | 2 | **4** | fail in one 60 px tile |
| full motion, final | 0 | 1 | 2 | 2 | 3 | pass |
| reduce motion, final | 0 | 1 | 1 | 2 | 2 | pass |

- **The one part over 3:**
  - Where: a 60 px tile on the THIS TURN tape at (810, 240).
  - What counted: four flashes inside one second. The clear wash leaving gave one at 10100 ms; the rings-step cells and the tape arrow passing gave three at 10750-11033 ms.
  - Fix: the old arcs now lift in the settle step, and the hand-off holds 400 ms before RINGS STEP. That puts the clear flash more than 1 s before the rings-step flashes.
  - Same pattern: tile (900, 420) had the same pattern at 3 and is now 3.
  - No effect was changed for this.
- **Tightest spot left:**
  - fx_rings_step on its own reaches 3 flashes per second in a few 60 px tiles: at (690, 90), on the tape, and at (180, 450-480), where the moving ring +1 and +2 cell edges cross. That is at the limit, not over it.
  - Measured on its whole box, as in step 4, it is still 1.
  - If the port wants headroom, slow the spiral (160-760 ms) or drop the third echo. FlashLimiter also guards it in the engine.
- **Whole frame: 0.** The beat never moves 25 % of everything that changes at once.
- **Reduce motion stays at or below full motion.** Overall it is 2 against 3. The worst reduce regions are the sector 1 block and the sector 2 brace in 120 and 60 px tiles, at 2 per second. I checked the sector 1 tile (630, 420) directly: it is also 2 in full motion. I did not compare every tile pair.

#### Reduce motion: shield_block and brace_block
- **Before:** reduce motion counted 2 flashes per second on every skin, against 1 in full motion.
- **Cause:** the reduce form is compact, so its footprint is small. The plate, its ink key and the hard shadow fade in together within 100 ms, which makes an up wave and a down wave: one flash. They fade out together within 160 ms: a second flash, 0.7 s later.
  - In full motion the out-fade's down wave stays under 25 % of the larger footprint, so only one flash counts.
  - I measured that a slower ease-in-out fade (300-400 ms), an earlier chevron fade or a weaker shadow all still gave 2.
- **Fix:** the reduce form now appears over 120 ms (linear), holds, and dissolves out over 300 ms (linear). That is the 260-300 ms reduce dissolve the rest of the set already uses. The 300 ms dissolve spreads the per-pixel swings, so only one wave crosses 25 %.
  - shield: appear 0-120, hold 120-620, dissolve 620-920.
  - brace: appear 0-120, hold 120-760, dissolve 760-1060, and the stamp stays.
  - Totals are unchanged (920 and 1060 ms). The look is unchanged.
- **Measured:** reduce 1 per second on neutral, Solace and Meridian for both effects, equal to full motion (1).
- **Margin:** a 260 ms dissolve still counts 2, so do not shorten it.
- **Code:** `RED_SHIELD` and `RED_BRACE` in `fx_o30/src/fx_eff.py`.

#### fx_refund RAM count
The frames were right and the source line was wrong:
- E10 f2 starts the turn at 4 RAM (`ram0`).
- Twist costs 0, Trigger 1 and Brace 1, which leaves 2.
- The trigger kill refunds 1, giving 3, which matches f2 `ram` 3 and the p3 HUD (2 coins, the refunded coin, 1 empty).
- So "2 lit, slot 3 lights" is correct, and the source line "ram 3 + 1" was not. It now reads "RAM 2 + 1 = 3" in both JSONs.

The AD also wrote that the strip "pastes the RAM panel next to the board". In fact the RAM row is drawn where the p3 HUD has it (y 513, x 1150-1245), inside the effect's crop. In `resolve_beat_strip.jpg` (3520 ms) and the GIF it sits in the full frame.

#### Open points for the designer
1. **Twist versus the plates.**
   - The state stores ring +1 units at their pre-twist sectors (f1 and f2 have the same `s`), with `twr` [1, 1]. Packet 5's fate (lands on 3 = 0 + 1 twist + 2 step) shows the twist is real.
   - p2 and p3, however, draw ring +1 untwisted. To end on the final p3 board, the sequence shows ring +1 one sector back during SEND IT, and the twist turns it into the p3 places.
   - Side effect: in that pre-twist frame, the Payload cell sits over the Adjuster box for 1.4 s.
   - If the board should instead show s + twr after a twist, the generator must draw that. The trigger route's origin and the later rings step would then move with it.
   - The Adjuster is not turned, as in the plates.
2. **Packet 1 is never seen alive.** Packet 1 is already absent on p2 and p3 (trigger-dead), so the sequence shows the trigger bursts on its sectors and the refund, but no fx_kill for it. A pre-state plate with Packet 1 drawn would let fx_kill play there.
3. **No effect for the TURRET shot on the Adjuster** (guns sector 2, h 1): fx_gun_hit has no Adjuster form. The shot is in the state and on the HUD chain; the beat does not animate it.
4. **Settle.** The 260 ms hand-off and the 400 ms hold before RINGS STEP are sequencer rules, not effects. They are written into `port/fx_timings.json` under `resolve_beat_e10`.
5. **Not updated in this pass:**
   - `fx_P_protect.png`, the sheet, still prints the step-4 reduce numbers (2). The strips and the JSON carry the new ones.
   - GODOT_PORT_SPEC Appendix A (shield and brace "1 / 2", the refund source) and section 14 item 5 ("never flash-measured") are out of date until the spec table is regenerated from `port/fx_timings.json`.
6. **Skins.** The sequence is measured on the neutral skin only. The shield and brace reduce fix was re-measured on all three.

#### Process
- **Rule break:** once, by mistake, I ran a bare `python -` in a shell chain (`python - 2>/dev/null`) while patching a test script. It ran no code and wrote nothing; it sat waiting on stdin. I stopped it, and that shell task, at once. All real work ran from script files.
- **Grade:** the final plates were re-graded by the room-grade pass at 04:30, while this pass was running.
  - The sequence frames, the strip, the GIF and the re-rendered shield and brace strips all read `final/p2_preview.png` and `final/p3_resolve.png` at render time (05:00 and later), so they carry the new grade.
  - Two helper plates come from before the re-grade, and they are used only on board pixels: the empty-rings plate (`fx_o30/work/base_neutral_p3_empty.png`, ring hole fills, settle, rings step) and the Worm-2-killed plate (`fx_cdhl/work/base_neutral_p3kill.png`, the kill cell).
  - Between the old and new p3, the board inside r 505 differs on 1.9 % of pixels (mean 0.8 levels); the room differs on 58 %.
  - Re-render those two from the new snapshot before any final reference capture.
- No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell, `corp/src` not edited.
- Big scratch is in `D:/rc_scratch/combat_redesign/locked/fx_o30/`. That covers the frames, the luminance memmaps (`work/lum_*.npy`, about 0.8 GB each) and the meter output (`work/meter_full.json`, `work/meter_red.json`).

### O-30 pass (board)

O-30 pass (2026-11-02): all 33 M, P, S and T strips and the four family sheets are re-rendered on the O-30 board.
- **Board changes.** The step-6 room grade is now the default in `corp/src`. The FAR threat trim is one solid tapered stroke, with no beads. The HUD-label and hero occluders are in.
- **Base plates.** The 11 extra base plates were rendered fresh from `corp/src` with clean caches:
  - neutral: p1_empty, p1_noguns and p1_hold;
  - Solace and Meridian: p1_empty, p1_hold, p2 and p3.
  The neutral and corp p1, p2, p3 and p2b come from the re-rendered `final/` plates.
- **Effect code** is the O-30 `fx_eff.py`, which includes the reduce-motion fix for shield_block and brace_block (reduce motion is now at 1 per second on all three skins, matching full motion).
- **What did not change:** timings, keys and easings.
- **Flash.** Every effect passes on every skin, in full and reduce motion. The worst case is 1 flash per second in both. The numbers moved by about 1 % or less.
- **`timings_MPST.json`.** Only the measured `flash_check` and `strips` fields were refreshed. The O-30 `reduce_phases` and notes are kept. An `o30_pass` key records the refresh.
- **Source.** `D:/rc_scratch/combat_redesign/locked/fx_o30b/mpst/src`.
- **Not re-rendered:** `resolve_beat.gif` and `resolve_beat_strip.jpg` (O-30 fix 4). They were built from bases rendered before the grade went default.
