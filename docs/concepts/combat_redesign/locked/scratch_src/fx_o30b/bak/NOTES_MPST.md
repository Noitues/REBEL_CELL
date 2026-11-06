# Effects on the locked board: M motion, P protect, S system, T commit (roadmap step 4)

This section covers the four families M, P, S and T: 12 effects plus the shove-collision variant. The C, D, H and L families are in their own notes. Every effect is rebuilt on the final locked plates (`../final/`, state E10). Corp-side versions are drawn for Solace and Meridian wherever the effect crosses corp rings. No game number, word or rule was changed, and nothing was committed.

## Files

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

## Effects and skins

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

## Family materials (distinct from the skins)

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

## Flash check: method

The numbers are per skin in `timings_MPST.json` and on each sheet's flash panel.

1. Every frame of the effect is rendered at 60 fps over its whole length plus 100 ms. Each frame is converted to WCAG relative luminance (linear sRGB, 0.2126 R + 0.7152 G + 0.0722 B). Frames are decimated 2x2 for speed, which leaves area fractions unchanged.
2. **Region the effect covers (footprint):** every pixel whose luminance moves more than 0.02 from frame 0 at any time. This is stricter than using the crop, because a small effect is judged against its own area.
3. **Per pixel:** an extremum tracker logs a swing event when the luminance moves 0.10 or more (10 % of full scale) away from the last extreme, in the opposite direction from the last swing. A slow ramp counts once, and jitter under 0.10 never counts.
4. **Region event:** 25 % or more of the footprint swings the same way within a 100 ms window (6 frames).
5. **Flash:** two opposite region events, up then down or down then up. **Pass:** no 1 s window holds more than 3 flashes.
6. Also logged: the per-frame mean luminance of the footprint (the curve), its largest frame-to-frame step, and its range.

## Flash check: results

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

## Reduce motion (per effect)

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

## Honest caveats

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

## O-30 pass

This pass answers the art director's fix 4: the full E10 p3 resolve beat is now sequenced on the final board and flash-measured as a whole. It also fixes the reduce-motion versions of shield_block and brace_block, and checks the fx_refund RAM count. No game number, word or rule was changed. Nothing was committed.

### New files
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

### The beat
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

### Flash meter over the whole beat
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

### Reduce motion: shield_block and brace_block
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

### fx_refund RAM count
The frames were right and the source line was wrong:
- E10 f2 starts the turn at 4 RAM (`ram0`).
- Twist costs 0, Trigger 1 and Brace 1, which leaves 2.
- The trigger kill refunds 1, giving 3, which matches f2 `ram` 3 and the p3 HUD (2 coins, the refunded coin, 1 empty).
- So "2 lit, slot 3 lights" is correct, and the source line "ram 3 + 1" was not. It now reads "RAM 2 + 1 = 3" in both JSONs.

The AD also wrote that the strip "pastes the RAM panel next to the board". In fact the RAM row is drawn where the p3 HUD has it (y 513, x 1150-1245), inside the effect's crop. In `resolve_beat_strip.jpg` (3520 ms) and the GIF it sits in the full frame.

### Open points for the designer
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

### Process
- **Rule break:** once, by mistake, I ran a bare `python -` in a shell chain (`python - 2>/dev/null`) while patching a test script. It ran no code and wrote nothing; it sat waiting on stdin. I stopped it, and that shell task, at once. All real work ran from script files.
- **Grade:** the final plates were re-graded by the room-grade pass at 04:30, while this pass was running.
  - The sequence frames, the strip, the GIF and the re-rendered shield and brace strips all read `final/p2_preview.png` and `final/p3_resolve.png` at render time (05:00 and later), so they carry the new grade.
  - Two helper plates come from before the re-grade, and they are used only on board pixels: the empty-rings plate (`fx_o30/work/base_neutral_p3_empty.png`, ring hole fills, settle, rings step) and the Worm-2-killed plate (`fx_cdhl/work/base_neutral_p3kill.png`, the kill cell).
  - Between the old and new p3, the board inside r 505 differs on 1.9 % of pixels (mean 0.8 levels); the room differs on 58 %.
  - Re-render those two from the new snapshot before any final reference capture.
- No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell, `corp/src` not edited.
- Big scratch is in `D:/rc_scratch/combat_redesign/locked/fx_o30/`. That covers the frames, the luminance memmaps (`work/lum_*.npy`, about 0.8 GB each) and the meter output (`work/meter_full.json`, `work/meter_red.json`).
