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
