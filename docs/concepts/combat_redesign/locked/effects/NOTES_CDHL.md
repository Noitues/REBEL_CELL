# Effects C / D / H / L on the locked final board (roadmap step 4)

Families: **C corp, D damage, H harm, L life** (16 effects + 3 variants), plus `fx_block_vs_break.png`. The M / P / S / T families are the other effects designer's (their notes sit beside these). Every frame here is the real locked final board (the `locked/final` generator, E10 state); nothing is painted on a stand-in. No game number, word or rule was changed.

## Files

| File | What it is |
|---|---|
| `fx_C_corp.png` | grow, ward_on: neutral, Solace, Meridian rows |
| `fx_D_damage.png` | gun_hit, strike, trigger_hit, kill, ricochet (+ gold), firewall_burn: all three skins |
| `fx_H_harm.png` | hit_land (+ worm, adjuster), shield_break, slice_crack, slice_break, hp_through: player skin |
| `fx_L_life.png` | refund, clear (all three skins), repair_mend (player skin) |
| `fx_block_vs_break.png` | shield block (P) and shield break (H) on the same slice: peak in colour and luma, then both strips |
| `strips/<id>.jpg` | one per effect (19 files, all under 2 MB): the same block at larger size |
| `timings_CDHL.json` | in / hold / out, phases, easing, keyframes, reduce-motion note, board crop, base plates and the full flash numbers per skin |

Each block shows 5-6 keyframes labelled in ms, then a yellow-framed **reduce-motion still**. Its header gives STILL, TIMING, the measured FLASH line, REDUCE MOTION, STYLE MUST KEEP and SOURCE (the state the effect comes from).

## Skins and where each effect is shown
- **Corp rings (all three skins: neutral, Solace, Meridian):** grow, ward_on, gun_hit, strike, trigger_hit, kill, ricochet, ricochet_gold, firewall_burn, refund (it pops from a ring cell) and clear (on the landing arc, next to the corp rim).
- **Player skin only:** the tower effects (hit_land and its variants, shield_break, slice_crack, slice_break, repair_mend) and hp_through (arc to the HUD). The tower and the HUD are the same on every corp, so corp rows would repeat the same pixels.
- **Slice-wide overlays:** hit_land, shield_break, slice_crack, slice_break and repair_mend cover their whole tower slice. The icon seat (r 37 around the icon) stays clear, except where the effect fades the icon on purpose (shield_break, slice_break).

## Family materials (distinct from WPAP cards, xerox/linocut spinner, corp enamel, cyan HUD)

| Family | Material | Why it doesn't clash |
|---|---|---|
| C corp | The corp's own frame enamel as a flat, opaque shutter slab with a hard 2 px lip. Neutral: steel (188,200,214), straight lip. Solace: porcelain (226,238,216) with a lime (150,236,120) rounded membrane lip. Meridian: stencil paint (236,214,178) with an oxide (224,128,40) notched lip. One flat 4-frame flash, no texture. Ward uses boss gold. | The state change wears the corp's own frame material, so it reads as the corp acting. It never uses pink, and it never uses the silver THIS TURN tape, which is time grammar. |
| D damage | Player-owned comic hit frame: a painted pink tracer (a tapered ribbon with an ink key), an ink-keylined pink starburst with a white core, converging white speed lines, flat vector shards (pink, paper, ink). | Pink belongs to the player, so we hurt them in pink. Flat vector, no Ben-Day, so it stays off the spinner print. |
| H harm | Misregistered red print: an X-only halftone flood (crossed marks, never round dots), black krackle with a 2 px red offset, a red stencil X. | Round dots would merge with the BURST slice's Ben-Day. The X screen is never used elsewhere. |
| L life | The one soft rising glow in the set: brush-stroke ribbons, plus signs, four-point sparkles. GAIN green on dark, **mint (214,255,206) with an ink key on the green REPAIR wedge** (GAIN green vanishes on it), NET_CYAN for the RAM coin. | Glow is used by no other family. Cyan is used only for RAM, matching the HUD. |

Rules kept: no dashed or dotted lines (trails are one continuous tapered ribbon; I replaced the round-2 echo dots with ribbons because a diamond train read as a dotted line). No needle. Cross-hatch only means HP lost at this END TURN: an effect resolves the existing hatch into a gone socket or dark pip and never adds new hatch. The arrowed outline is not used (no effect is a movement). Pink stays the player's.

## Flash check (measured, 60 fps)

**Method** (`fxk_lib.flash_check`):
1. **Frames.** Every frame of the animation is rendered at 60 fps over the board crop. That runs from 100 ms before the start (pre-state held) to 300 ms past the end (settled state held). Each frame is composited on the real plate: pre base, post base through the state mask, then the effect layer.
2. **Luminance.** Per pixel I take relative luminance Y (WCAG 2: linearised sRGB, 0.2126 R + 0.7152 G + 0.0722 B).
3. **Region.** The *footprint* is every pixel whose Y moves more than 0.02 at any time: the frame region the effect covers. I also test against the whole crop.
4. **Transitions.** Each pixel's Y path is cut into swings between local extremes, with hysteresis 0.10. A transition is a swing of at least 0.10 whose darker end is below 0.80.
5. **Waves.** For each frame I count the share of the region that completed a transition in the last 100 ms. A wave is the moment an up-share or a down-share first crosses 25 % (edge-triggered).
6. **Flashes.** One flash is an opposing pair of waves (up then down, or down then up). Flashes per second is the most flashes in any 1 s window. The pass bar is 3 or fewer.
7. **Also reported** in `timings_CDHL.json`: the region-mean luminance series, its largest frame-to-frame step, the peak up and down shares, and the same test on the reduce-motion variant (neutral).

| Effect | Fam | Total ms | In / hold / out | Skins | Max flashes/s (worst skin) | Footprint (share of crop) | Peak swing share up / down | Mean-lum max step | Reduce flashes/s | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| `fx_grow` | C | 650 | 250 / 67 / 333 | neu, sol, mer | 1 | 32 % | 51 / 88 % | 0.17 | 0 | pass |
| `fx_ward_on` | C | 750 | 450 / 67 / 233 | neu, sol, mer | 2 | 44 % | 52 / 50 % | 0.06 | 0 | pass |
| `fx_gun_hit` | D | 600 | 170 / 160 / 270 | neu, sol, mer | 1 | 6 % | 49 / 50 % | 0.08 | 0 | pass |
| `fx_strike` | D | 700 | 200 / 180 / 320 | neu, sol, mer | 1 | 12 % | 47 / 39 % | 0.07 | 1 | pass |
| `fx_trigger_hit` | D | 900 | 420 / 230 / 250 | neu, sol, mer | 0 | 3 % | 29 / 21 % | 0.04 | 0 | pass |
| `fx_kill` | D | 600 | 110 / 220 / 270 | neu, sol, mer | 1 | 20 % | 92 / 87 % | 0.40 | 0 | pass |
| `fx_ricochet` | D | 500 | 100 / 150 / 250 | neu, sol, mer | 1 | 3 % | 45 / 42 % | 0.04 | 0 | pass |
| `fx_ricochet_gold` | D | 500 | 100 / 220 / 200 | neu, sol, mer | 1 | 4 % | 40 / 38 % | 0.06 | 1 | pass |
| `fx_firewall_burn` | D | 1000 | 460 / 240 / 300 | neu, sol, mer | 1 | 17 % | 39 / 76 % | 0.03 | 0 | pass |
| `fx_hit_land` | H | 700 | 160 / 170 / 370 | neu | 1 | 16 % | 55 / 40 % | 0.04 | 1 | pass |
| `fx_hit_land_worm` | H | 700 | 160 / 170 / 370 | neu | 1 | 17 % | 54 / 39 % | 0.04 | 1 | pass |
| `fx_hit_land_adjuster` | H | 700 | 160 / 170 / 370 | neu | 1 | 20 % | 62 / 49 % | 0.05 | 1 | pass |
| `fx_shield_break` | H | 700 | 190 / 190 / 320 | neu | 1 | 40 % | 35 / 32 % | 0.03 | 1 | pass |
| `fx_slice_crack` | H | 500 | 260 / 40 / 200 | neu | 2 | 12 % | 42 / 42 % | 0.07 | 0 | pass |
| `fx_slice_break` | H | 650 | 200 / 180 / 270 | neu | 0 | 35 % | 24 / 62 % | 0.05 | 0 | pass |
| `fx_hp_through` | H | 1150 | 880 / 100 / 170 | neu | 0 | 5 % | 22 / 26 % | 0.02 | 0 | pass |
| `fx_refund` | L | 900 | 650 / 0 / 250 | neu, sol, mer | 0 | 14 % | 26 / 24 % | 0.02 | 1 | pass |
| `fx_clear` | L | 800 | 300 / 100 / 400 | neu, sol, mer | 1 | 12 % | 64 / 40 % | 0.03 | 0 | pass |
| `fx_repair_mend` | L | 900 | 560 / 0 / 340 | neu | 1 | 19 % | 33 / 30 % | 0.01 | 0 | pass |
| `fx_shield_block` | P | 560 | 100 / 260 / 200 | neu | 1 | 20 % | 40 / 39 % | 0.03 | 0 | pass |

Notes on the numbers:
- **kill (1/s).** The 2-frame 70 % white flare on the cell is the biggest single event in the set: 92 % of the footprint swings, and the mean-lum step is 0.40. It is one flash.
- **ward_on and slice_crack (2/s).** These are the only effects with two flashes. In ward_on they are the Adjuster pulse and the gold flash; in slice_crack, the rim flood pulse and the crack/pip change. Both are under the limit.
- **firewall_burn.** The flicker is a 7 Hz change in tongue height, not in luminance, and it measures 1/s.
- **Effects that share a beat.** No effect is above 2/s on its own. On the resolve beat, effects must stay sequenced by the VISUAL_PLAN G layer order, not overlapped. I did not measure a combined resolve sequence.

## Per effect: timing and reduce-motion

Easing names: eout = ease-out cubic, eio = ease-in-out cubic, back = ease-out back (overshoot). Full phases are in the JSON.

**C corp**
- **grow (650 ms).** Shutter wipe 0-250 (eio), flat flash 250-317 (4 frames), open 317-460 (eio), ring ping 300-560 (eout). The new hollow growth chevron is the post-state, rendered by the generator (land_hit = hit + 1). *Reduce:* no shutter or ping; the chevron fades in over 200 ms.
- **ward_on (750 ms).** Adjuster pulse 0-220 (sine, gold fill 22 % + bright edge), gold scan 150-450 (eio), gold flash 450-517 at 42 %, lozenge and ping 470-700. *Reduce:* the lozenge fades in over 200 ms.

**D damage**
- **gun_hit (600 ms).** Tracer 0-100 (eout), burst 100-170 (back), speed lines 100-280, shards 120-460, tick to gone socket at 170 with a pink pop, out 300-520. *Reduce:* tracer and burst static for 300 ms, fade 200; no lines or shards.
- **strike (700 ms).** Slash 0-120, burst 120-200 (back), two ticks gone at 200, out 380-640. *Reduce:* as gun_hit.
- **trigger_hit (900 ms).** The pencil route ignites to paint front to back over 0-420 (linear). Bursts at the struck cells in sector order: sector 3 at 230, sector 4 at 420. The Xs turn from pencil to pink paint as they are hit. *Reduce:* route painted at once; both bursts together for 300 ms.
- **kill (600 ms).** Flare on frames 1-2 (17-50 ms, cell only), KO burst with no word at 34-110, shards 60-560, cell empties 200-420 (eio). The post-state is rendered with the Worm and its shots removed. *Reduce:* no flare; a 25 % tint held for 200 ms, then the cell fades empty.
- **ricochet (500 ms).** Steel cap glint and sparks; no starburst, no HP. *Reduce:* tracer and glint static.
- **ricochet_gold (500 ms).** A curved gold streak, a single tapered ribbon, glances off the ward mark. In E10 the warded shots deal 0, so no tick changes. *Reduce:* full streak static.
- **firewall_burn (1000 ms).** Bands rise ring by ring (0, 130, 260 ms stagger, eout), up to 60 % of cell depth; inked pink with a lighter core and no white. The flames are cut clear of the unit token. Ticks gone at 330, embers 700-1000. *Reduce:* all bands at once, no flicker.

**H harm**
- **hit_land (700 ms).** Chevrons slam in 0-100 (ease-in), the wedge frame flashes HARM on 2 frames (100-134), the X flood rolls in 100-260 over the outer half (the seat stays clear), krackle 120-520, the hatched pip goes dark at 260. Variants: the worm hook stamps at 160-230 and stays; the Adjuster gives one gold rim flash at 100-200. *Reduce:* flood held at 80 % for 300 ms, no travel or krackle.
- **shield_break (700 ms).** Plate under load with a hairline crack 0-110, splits into 5 shards at 120 (eout + gravity, 120-560), flood 130-300, krackle, wedge dark 200-500 (stays), pips dark at 300. *Reduce:* shards shown split in place.
- **slice_crack (500 ms).** Rim flood pulse 0-300, white crack 60-260 beside the icon, pip dark at 200. *Reduce:* crack only, 150 ms.
- **slice_break (650 ms).** Flood, red stencil X in the outer corner 120-200 (strong back), black-out 150-450 and ink X-halftone over the icon 200-500 (both stay), pips dark at 250. *Reduce:* all in one 300 ms fade.
- **hp_through (1150 ms).** Six diamonds lift 0-220 and ride one shared curve 120-880 (eio, 30 ms stagger) behind one ribbon trail. One red slap on the taped YOU strip, then the six hatched segments go dark (920-1100). *Reduce:* segments go dark in 200 ms, no flight.

**L life**
- **refund (900 ms).** A NET_CYAN coin with a plus pops at the REFUND mark (0-150, back) and flies one curve with a cyan ribbon and soft glow (150-650). The RAM slot lights with a glow ring (650-910); the slot reads empty until the coin lands. *Reduce:* coin fades at the mark; the slot lights at once.
- **clear (800 ms, round 2 was still-only).** GAIN wash sweeps the landing arc 0-240, a painted check stamps in at 160-300 (back), sparkles 300-680. *Reduce:* wash and check fade in over 200 ms.
- **repair_mend (900 ms).** Mint brush ribbons with a soft glow rise through the REPAIR wedge 0-645, plus signs 120-780, the mend-pending pip fills 380-560. *Reduce:* two static plus signs and the pip fill.

## Honest caveats and open points
1. **Latent effects.** strike, ricochet (steel), firewall_burn, the hit_land Adjuster variant and repair_mend have no source in the E10 state.
   - They are drawn on real units and slices, with stand-in marks: a steel cap on Packet 5, and a mend-pending pip on sector 5.
   - They were not checked against real game numbers.
   - In E10, warded shots deal 0, so ricochet_gold shows no HP change.
2. **Block vs break uses a pending slice.** The block demo sits on sector 1, which E10 forecasts to break, so the base already carries the red pending hatch under the block. That hatch is the board's, not the effect's. A real block would sit on a slice with no pending loss.
3. **Kill post-state.** It was rendered with the Worm removed from the state and its two gun shots dropped, so the gun tracer also leaves in the post-state. In the game the tracer ends with the shot anyway.
4. **Grow post-state.** It was rendered with land_hit = hit + 1 on Packet 5. That is how this board draws a hollow growth chevron; E10's `grown` field draws nothing on the board.
5. **Overlay layering.** Effects are composited over the finished plate, so on crops that touch the hand they would sit above the cards. The crops avoid the hand. In engine, the slot is above the board and HUD and below the hand (`extra` hook).
6. **Solace lime vs GAIN green.** The Solace shutter lip (150,236,120) is near GAIN green. It is a 2 px lip on a porcelain slab, on screen for under 0.5 s, and it never appears with a plus or a check.
7. **Flash check scope.** Each effect was measured alone, not as the combined resolve sequence.
8. **Process.** I ran a bare `python -` once by mistake, with an empty heredoc. It wrote nothing and I stopped it at once; all real work ran from script files. Earlier I also ran one `python -c` syntax check. No Godot, no Blender, nothing committed, nothing under D:/Godot/rebel_cell, no shared generator file edited.

## Source and re-render
Source is in `D:/rc_scratch/combat_redesign/locked/fx_cdhl/src`. It imports the shared generator read-only (`gen_env.py`), and its caches are redirected to `fx_cdhl/work/gen`.
- `base_render.py <skin> <p3|p3alt|p3grow|p3kill>` renders the base plates.
- `fx_cdhl.py` holds the effects: kit, geometry and registry.
- `fxk_lib.py` holds the layer kit, frame composer and flash meter.
- `fx_build.py <ids>` renders keyframes and runs the 60 fps flash check.
- `fx_sheets.py all` builds the sheets, strips, `timings_CDHL.json` and block-vs-break.
- `mk_notes.py` writes this file.

## O-30 pass

O-30 pass (2026-11-02): all C, D, H and L keyframes, reduce-motion stills and 60 fps flash checks are re-rendered on the O-30 board, on every skin. The outputs are the four family sheets, all 19 strips and `fx_block_vs_break.png`.
- **Board changes.** The step-6 room grade is now the default in `corp/src`. The FAR threat trim is one solid tapered stroke, with no beads. The HUD-label and hero occluders are in.
- **Base plates.** All 12 were rendered fresh from `corp/src` (neutral, Solace and Meridian; p3, p3alt, p3grow and p3kill), with clean caches. Before they were stale. Neutral p3 matches the published `final/p3_resolve.png` to within 1/255 (`px_over_8 = 0`). The geometry probe (`geom.json`) is byte-identical to the step-4 one.
- **What did not change:** effect code, timings, keys and easings.
- **Flash.** Max flashes per second are the same as step 4 for every effect and skin. All pass at 3 per second or less. The footprint and swing numbers moved by about 1 % or less, because the crops are board, not room.
- **`timings_CDHL.json`.** Only the measured `flash` fields were refreshed. The O-30 hand edits are kept: the trigger_hit `in_sequence` note and the refund RAM source. An `o30_pass` key records the refresh.
- **Source.** `D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/src` (a copy of `fx_cdhl/src` with the paths redirected and per-skin caches). The JSON merge is `fx_o30b/merge_json.py`.
