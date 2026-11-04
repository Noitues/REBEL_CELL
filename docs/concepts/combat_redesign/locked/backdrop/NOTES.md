# Backdrop and loudness re-tune (roadmap step 6)

> **2026-11-03 rebuild stage 2:** the plates, `grade.json`, `checks.json` and `before_after.jpg` in this folder are now the **rb2-1** set (AD review 2.8: the step-6 grade "switched the room off"). Meridian moved to the shop room: `p1_shop_meridian.png` replaces `p1_bio_meridian.png`. See "2026-11-03 stage 2: grade rb2-1" at the end. The step-6 text below is history.

This step re-grades the 7 v3.1 cutaway rooms behind the final locked p1 board (`../final/`). The board reads first, and each room still reads as its Solace location. Nothing on the board was changed: the board pixels are the final fix-pass render. Only the room grade under the board scrim is new. Every game number, word and rule on the plate is unchanged.

## Files

| File | What it is |
|---|---|
| `p1_bio.png`, `p1_srv.png`, `p1_gh.png`, `p1_rec.png`, `p1_lobby.png`, `p1_event.png`, `p1_shop.png` | Final p1 board, neutral skin, on each room with its new grade |
| `p1_bio_solace.png`, `p1_bio_meridian.png` | The bio room behind the Solace and Meridian corp skins |
| `before_after.jpg` | One row per plate: the locked grade vs the new grade at 1/2, the room at 1:1, the squint grids (red = loud cells) with their numbers, and the room's grade parameters |
| `grade.json` | The post grade as per-room parameters for Godot, with the order of operations and the formulas |
| `checks.json` | Every number below, before and after, per region; targets and pass flags; the real-render cross-check |

## How the plates are made

- The board is recovered as a linear transfer, `plate = F + T * backdrop`. The final p1 board is rendered twice by the locked generator (`corp/src`, unchanged) with flat backdrops of 0 and 128. Every layer above the backdrop is an alpha composite, so the plate is linear in the backdrop. This was done once per skin (neutral, Solace, Meridian).
- Cross-checks:
  - Composite vs a real render with the old grade (bio, neutral): mean error 0.09/255, max 1.7/255.
  - The generator's p1 vs the published `final/p1_decide.png`: max 1/255.
  - `p1_bio` and `p1_event` vs real renders through the generator with `r2_ground.grade` swapped for the new grade: mean 0.10/255, max 2/255.
- **Before** is the current locked grade: `r2_ground.grade('P')` (hull at x0.595 value with neon saturation pulled to 0.6; city blurred 2 px at x0.85) plus the board scrim. **After** is `bd_grade.grade` with the room's parameters plus the same scrim. The scrim is board ground and is not touched.

## The grade (one recipe, solved per room)

All the maths runs on sRGB-encoded values in 0-1, in this order:
1. A focus hull: an ellipse round the cutaway, the same as before.
2. Blur: 0.4 px on the room, 4 px on the city.
3. Chroma: overall chroma, a neon pull (0.8) and a player-pink pull.
4. Contrast: 1.12 around a pivot of 0.16.
5. Value: hull and city multipliers.
6. A luma highlight shoulder from 0.18 toward 0.30.
7. Haze: in the recipe, but set to 0 in every room.
8. Vignette (0.30) and a falloff toward the board side (0.30).

- `hull_value` and `chroma` are solved per room by bisection. The targets are a room squint mean of 0.135 and a room mean saturation of min(before, 0.44). Everything else is shared, except the event room: contrast 1.24, shoulder ceiling 0.32 and pink pull 0.42. Without these its relative detail fell to 0.79 of before, and its rose seats stayed above the pink limit.
- The idea: drop the room's value and cap its highlights, which takes the room out of the loud band. Raise the contrast and keep the chroma, which keeps the room legible and keeps its identity colour. The city around the board loses the most, so the board sits on a dark field and the room stays a lit, readable island.
- Pink belongs to the player. Magenta-to-rose hues (about 302-350 degrees) in the room lose 45 % of their chroma, or 58 % in the event room. The violet night city is left alone.

| Room | hull_value | chroma | contrast | shoulder | pink pull |
|---|---|---|---|---|---|
| bio | 0.466 | 0.876 | 1.12 | 0.18 -> 0.30 | 0.55 |
| srv | 0.439 | 0.814 | 1.12 | 0.18 -> 0.30 | 0.55 |
| gh | 0.470 | 0.891 | 1.12 | 0.18 -> 0.30 | 0.55 |
| rec | 0.458 | 0.941 | 1.12 | 0.18 -> 0.30 | 0.55 |
| lobby | 0.450 | 0.849 | 1.12 | 0.18 -> 0.30 | 0.55 |
| event | 0.478 | 0.836 | 1.24 | 0.18 -> 0.32 | 0.42 |
| shop | 0.415 | 0.826 | 1.12 | 0.18 -> 0.30 | 0.55 |

Shared: city_value 0.55, neon_chroma 0.8, hull blur 0.4 px, city blur 4 px, vignette 0.30 (d 0.9-2.6), board falloff 0.30 (x 700-1250). For reference, the old hull value was 0.595, applied after a stronger neon saturation pull.

## Measurements

- The squint is the locked metric: a 1/16 box downscale, a 1 px blur, Rec709 luma, and loud = cells above 0.38. Values are given as mean / p95 / loud share.
- **Room** is the hull wherever the backdrop shows through (T > 0.5). **City+room** is every visible backdrop cell. **Board** is r <= 500.
- **Board/room** is (board mean + 0.05) / (room mean + 0.05).
- **Detail rel** is the RMS of the luma high-pass divided by the room's mean luma: legibility, independent of brightness.

| Plate | Room before | Room after | City+room before | City+room after | Whole plate before | Whole plate after | Board/room | Detail rel | Sat | Pink |
|---|---|---|---|---|---|---|---|---|---|---|
| bio | 0.187 / 0.335 / 1.1 % | 0.135 / 0.231 / 0 % | 0.165 / 0.312 / 0.5 % | 0.101 / 0.217 / 0 % | 0.228 / 0.494 / 12.4 % | 0.205 / 0.493 / 12.2 % | 1.27 -> 1.61 | 0.37 -> 0.31 | 0.42 -> 0.42 | 8.6 -> 0.0 % |
| srv | 0.192 / 0.348 / 1.5 % | 0.135 / 0.233 / 0 % | 0.169 / 0.321 / 0.7 % | 0.102 / 0.216 / 0 % | 0.230 / 0.494 / 12.5 % | 0.205 / 0.493 / 12.2 % | 1.24 -> 1.61 | 0.35 -> 0.30 | 0.47 -> 0.44 | 0.8 -> 0.0 % |
| gh | 0.183 / 0.314 / 0.1 % | 0.135 / 0.219 / 0 % | 0.164 / 0.303 / 0.1 % | 0.102 / 0.209 / 0 % | 0.228 / 0.494 / 12.3 % | 0.205 / 0.493 / 12.2 % | 1.28 -> 1.61 | 0.38 -> 0.31 | 0.41 -> 0.40 | 1.1 -> 0.0 % |
| rec | 0.185 / 0.318 / 0 % | 0.135 / 0.224 / 0 % | 0.165 / 0.310 / 0.1 % | 0.102 / 0.212 / 0 % | 0.229 / 0.494 / 12.3 % | 0.205 / 0.493 / 12.2 % | 1.27 -> 1.61 | 0.35 -> 0.31 | 0.38 -> 0.38 | 9.1 -> 0.0 % |
| lobby | 0.190 / 0.346 / 1.4 % | 0.135 / 0.232 / 0 % | 0.163 / 0.307 / 0.7 % | 0.100 / 0.215 / 0 % | 0.228 / 0.494 / 12.4 % | 0.204 / 0.493 / 12.2 % | 1.25 -> 1.61 | 0.35 -> 0.30 | 0.42 -> 0.42 | 6.9 -> 0.0 % |
| event | 0.174 / 0.293 / 0.5 % | 0.135 / 0.214 / 0 % | 0.160 / 0.286 / 0.2 % | 0.102 / 0.205 / 0 % | 0.227 / 0.494 / 12.3 % | 0.205 / 0.493 / 12.2 % | 1.33 -> 1.61 | 0.38 -> 0.32 | 0.45 -> 0.45 | 1.2 -> 0.0 % |
| shop | 0.198 / 0.344 / 1.5 % | 0.135 / 0.225 / 0 % | 0.170 / 0.317 / 0.7 % | 0.101 / 0.212 / 0 % | 0.230 / 0.495 / 12.5 % | 0.205 / 0.493 / 12.2 % | 1.21 -> 1.61 | 0.30 -> 0.27 | 0.39 -> 0.39 | 0.7 -> 0.0 % |
| bio, Solace | 0.187 / 0.335 / 1.1 % | 0.135 / 0.231 / 0 % | 0.166 / 0.312 / 0.5 % | 0.103 / 0.218 / 0 % | 0.233 / 0.495 / 12.7 % | 0.210 / 0.493 / 12.5 % | 1.31 -> 1.67 | 0.37 -> 0.31 | 0.42 -> 0.42 | 8.6 -> 0.0 % |
| bio, Meridian | 0.187 / 0.335 / 1.1 % | 0.135 / 0.231 / 0 % | 0.164 / 0.311 / 0.5 % | 0.100 / 0.217 / 0 % | 0.228 / 0.494 / 12.5 % | 0.204 / 0.493 / 12.2 % | 1.27 -> 1.62 | 0.37 -> 0.31 | 0.42 -> 0.42 | 8.6 -> 0.0 % |

- **Board:** unchanged on every plate. Neutral is 0.249 / 0.455 / 12.2 % before and 0.248 / 0.455 / 12.2 % after. The board/room p95 ratio goes from 1.27-1.47 to 1.80-1.91.
- **Rooms:** each room's squint mean drops by 22-32 %, its p95 to 0.21-0.23, and its loud share to 0 (from up to 1.5 %). Relative detail keeps 82-92 % of before, and mean saturation stays within 0.03, so the rooms still read as places in their own colours.
- **Pink:** the measure counts room pixels of player-pink hue. Before, it caught the magenta-to-rose hues in the room (bio and rec high, 9 %). After, every plate is at or below 0.03 %.
- `checks.json` `all_pass` is true against these targets: room mean 0.125-0.145, room loud 0, room p95 <= 0.25, board/room >= 1.55, detail rel >= 0.80 of before, saturation within 0.05, pink < 0.1 %, and the board unchanged.

## Read on the plates

- The board is the brightest, most chromatic thing on every plate. The rooms read as lit green / teal / amber labs at about two thirds of their old value, with their props, tanks, racks and benches still separable at 1:1.
- The city around the board went from a busy purple window grid to a dark field (city+room mean 0.16-0.17 -> 0.10). That is where most of the "board first" gain comes from.
- **Solace skin:** its green enamel rings next to the green bio lab is the closest call. The room now sits clearly below the rings (board/room 1.67), and the membrane rings and helix rim still read as the corp.
- **Meridian skin:** the warm oxide rings separate from the green room by hue, as well as by value.
- **Whole-plate loud share** only moves from about 12.4 % to 12.2 %. The old grade already kept the room under the loud line (0-1.5 % loud), so nearly all the loud cells are on the board (tower and hand). The fix for the 14 % vs 4 % gap is the room's mean and p95, not its loud share. The mean of the whole plate drops from 0.228 to 0.205.

## Godot

- `grade.json` holds the order of operations and the per-room parameters. The grade is one full-screen post shader on the room layer, under the board:
  - an analytic ellipse mask;
  - two gaussian passes (0.4 and 4 px at 1080p), mixed by the mask;
  - per-pixel chroma, contrast, value, shoulder and vignette.
- The hue window for the pink pull is given as smoothsteps.
- Work on the sRGB-encoded colour, as in `grade.json` `colour_space`.
- The board scrim stays as it is (6 px frosted pool plus SCRIM #02030A at 55 %, r 330-560).

## Not done, and risks

- **Other beats:** only p1 was graded and measured, as briefed. p2, p2b and p3 use the same room layer, so the same grade applies, but they were not rendered here.
- **The SOLACE sign:** the building sign at the room's lower left sits mostly behind the hand (the hand was moved in fix pass O-29). It reads as "SOLA" at 1:1 both before and after. The Solace location reads through the green lab and the facade, not the sign. Moving the sign or the hand is a layout call.
- **The target is a choice:** the room squint mean target of 0.135 is my pick (between E10's whole-plate 0.184 and the dark rings). A brighter room is one number in `bd_solve.py` (`_target_mean`), and every room re-solves to it.
- **Absolute detail:** detail RMS drops with value (0.058-0.069 -> 0.037-0.043). The brightness-independent measure keeps 82-92 %. A very dark display may lose the room's shadow detail first.
- **Composites, not full renders:** the corp plates, and five of the seven neutral plates, are F + T composites. The method was checked against real renders (max 2/255), but it was not repeated per plate.

Sources (scratch, not in the repo): `D:/rc_scratch/combat_redesign/locked/backdrop/src/`
- `fg_extract.py`: the board transfer;
- `bd_grade.py`: the grade;
- `bd_measure.py`: compose and metrics;
- `bd_before.py`, `bd_solve.py`, `bd_tune.py`, `bd_collect.py`, `bd_verify.py`, `bd_publish.py`;
- final parameters: `work/final_params.json`.

## 2026-11-03 stage 2: grade rb2-1 (review 2.8)

**Why.** The AD review (2.8) measured the step-6 room at L* 21 in its probe box and called it switched off. `../REVIEW_RESPONSE.md` classes this as IMPL. The fix has five parts:
- the room reads at a mean L* of 28-34;
- the board still comes first by the family value-order check;
- Meridian gets a non-Solace room from the kit;
- the seam where the city strip meets the room gets a treatment;
- the camera stays the cutaway (DR-9).

Every value below is CIE L* measured on the published PNG.

### Files (replaced in this folder)

| File | What it is |
|---|---|
| `p1_bio.png`, `p1_srv.png`, `p1_gh.png`, `p1_rec.png`, `p1_lobby.png`, `p1_event.png`, `p1_shop.png` | The final p1 board (neutral skin, rebuild stage 2) on each room with its rb2-1 grade |
| `p1_bio_solace.png` | The Solace skin on its room, the bio lab |
| `p1_shop_meridian.png` | The Meridian skin on its new room, the shop under the amber corp light. Replaces `p1_bio_meridian.png` |
| `before_after.jpg` | One row per plate: the step6-1 grade vs rb2-1 (at 1/2), the room crop before and after, the numbers and the grade parameters. The sheet is saved at 2/3 scale |
| `grade.json` | Version rb2-1: the order of operations with formulas, `corp_room`, every room's parameters (and `shop_meridian`), and the old `rooms_step61` |
| `checks.json` | Per plate, before and after: the room numbers, the squint, the full `rb_checks` a-e, the composite vs real-render check, and `all_pass` |

### How the plates are made

- The plates use the same transfer as step 6: `plate = F + T * backdrop`.
- F and T were re-extracted from the **current** p1 board (`corp/src` with `rb_patch` and `rb2_patch`), one per skin, in fresh render caches. The step-6 cache held the pre-rebuild tower, which made the first stage-2 composites stale.
- **Composite vs the real renders** in `../final/` (same skin, same room): `p1_bio` vs `p1_decide.png`, `p1_bio_solace` vs `p1_decide_solace.png`, and `p1_shop_meridian` vs `p1_decide_meridian.png`. The error is mean 0.11-0.13/255 and max 2/255.
- The other five neutral rooms are composites only. The 15 final plates show the bio lab (neutral, Solace) and the shop (Meridian).

### The grade (rb2-1)

One recipe for every room. It runs on gamma-encoded sRGB, and `grade.json` `order` has the formulas. It is the step-6 shader plus these steps:
1. **Focus hull:** a polygon on the cutaway box (walls and floor slab), feathered 10 px inside and 3 px outside. It replaces the ellipse, which put the BAR facade in the transition.
2. **Blur ramp:** 0.4 → 1.6 → 4 px across the hull edge as one ramp, not a cross-fade.
3. **Corp light:** Meridian only. Hues 88-162 deg are pulled toward 20 deg by 0.88, with luma kept.
4. **City chroma:** the city keeps 30 % of its chroma.
5. **Local tone:** the gain comes from the local mean luma (14 px blur). The target is 0.17 + 0.21 (1 - e^(-x / 0.09)), and the gain is capped at 3.5. It applies fully in the hull, and at 45 % in the city out to hull distance 1.5-2.6.
6. **Shoulder:** the knee is at 0.24. The ceiling is solved per room (0.349-0.355), so the room's p95 is L* 38 on p1.
7. **Haze:** 0.05 in the room, ramping to 0.5 in the city. Its colour is the room's own key light at the box: the brightest 15 % of the hull, scaled to luma 0.38. Further out the colour moves to the night haze #141222.
8. **Vignette** 0.10 and **board falloff** 0.08.

Then the board scrim, unchanged.

| Room | ceil | chroma | contrast | pink pull | spill rgb |
|---|---|---|---|---|---|
| bio | 0.350 | 0.876 | 1.12 | 0.55 | 77, 106, 68 |
| srv | 0.350 | 0.814 | 1.12 | 0.55 | 65, 107, 85 |
| gh | 0.352 | 0.891 | 1.12 | 0.55 | 88, 103, 61 |
| rec | 0.355 | 0.941 | 1.12 | 0.55 | 94, 101, 69 |
| lobby | 0.349 | 0.849 | 1.12 | 0.55 | 69, 109, 59 |
| event | 0.350 | 0.836 | 1.24 | 0.42 | 88, 101, 81 |
| shop | 0.352 | 0.826 | 1.12 | 0.55 | 84, 104, 68 |
| shop_meridian | 0.352 | 1.05 (neon 0.9) | 1.12 | 0.55 | 106, 97, 70 (after the corp light) |

- `tone_lo` is 0.17 in every room.
- Chroma, contrast and pink pull are the step-6 per-room values.
- The solve is `bd2_solve.py`: bisection on `ceil` to reach p95 L* 38 on p1. `bd2_embed.py` writes the `ROOMS` table into `corp/src/bd_grade.py` and copies it to `backdrop/src`.

**Seam.** Where the city strip meets the room, three things happen:
- one blur ramp runs over the hull edge;
- the city's chroma drops to 30 %;
- the haze carries the room's own light out from the box.

So the facades next to the box read as one lit street, not a second picture pasted behind the board. The camera stays the cutaway (DR-9).

**Rooms per skin** (`bd_grade.CORP_ROOM`):
- Neutral and Solace use the bio lab.
- Meridian uses the shop, the only kit room without a Solace sign. Its lime light is turned amber by the corp light. The review's summary allows corp colour in the room ("colour on crest, lip and room").

### Measurements (`checks.json`)

The room region is the one `rb_checks` uses: x ≥ 1100, y ≥ 420, r > 505, with these cut out:
- the HUD, the hand, SEND IT, UNDO, the nameplate, the YOU strip and the hover tag, each dilated 4 px;
- the UI scrim slabs, where they darken the room by 15 % or more.

The values are the L* of the region's mean luminance, and its p95 L*.

| Plate | Room before (step6-1) | Room after (rb2-1) | Box part after | Street part after | Reviewer box mean | Detail rms | Detail rel | Sat | rb_checks a-e |
|---|---|---|---|---|---|---|---|---|---|
| bio | 16.8 / 30.5 | 32.0 / 38.1 | 32.3 | 29.0 | 23.9 → 34.5 | 0.039 → 0.035 | 0.27 → 0.12 | 0.42 → 0.32 | pass |
| srv | 16.8 / 29.9 | 32.5 / 38.1 | 32.7 | 29.8 | 23.6 → 34.8 | 0.038 → 0.033 | 0.26 → 0.11 | 0.44 → 0.37 | pass |
| gh | 16.3 / 30.1 | 31.9 / 38.1 | 32.1 | 29.4 | 23.5 → 34.4 | 0.041 → 0.036 | 0.29 → 0.13 | 0.40 → 0.30 | pass |
| rec | 16.6 / 29.4 | 32.3 / 38.1 | 32.5 | 29.9 | 23.3 → 34.6 | 0.040 → 0.037 | 0.27 → 0.13 | 0.36 → 0.26 | pass |
| lobby | 16.5 / 30.1 | 32.2 / 38.1 | 32.5 | 29.1 | 23.7 → 34.7 | 0.038 → 0.033 | 0.27 → 0.11 | 0.42 → 0.36 | pass |
| event | 16.8 / 32.3 | 31.8 / 38.1 | 32.1 | 29.3 | 23.6 → 34.2 | 0.042 → 0.034 | 0.29 → 0.12 | 0.43 → 0.28 | pass |
| shop | 16.0 / 28.5 | 32.2 / 38.1 | 32.5 | 29.6 | 23.5 → 34.8 | 0.036 → 0.035 | 0.26 → 0.12 | 0.39 → 0.29 | pass |
| bio, Solace | 16.8 / 30.5 | 32.0 / 38.1 | 32.3 | 29.0 | 23.9 → 34.5 | 0.039 → 0.035 | 0.27 → 0.12 | 0.42 → 0.32 | pass |
| shop, Meridian (before: bio lab) | 16.8 / 30.5 | 32.2 / 38.1 | 32.5 | 29.5 | 23.9 → 34.8 | 0.039 → 0.035 | 0.27 → 0.12 | 0.42 → 0.34 | pass |

- **Gate:**
  - The room mean is L* 31.8-32.5 on every backdrop plate (target 28-34).
  - The room p95 is 38.1. That is 13 below the ring-NOW occupied glass p95 (51.1-51.3); the gate asks for 1.
  - All five `rb_checks` pass on all 9 plates.
  - `checks.json` `all_pass` is true.
- **On the 15 final plates** (real renders, every beat): the room mean is L* 31.2-32.2 and its p95 37.5-38.1 (`../final/checks.json`).
- **Before**, the step6-1 grade read 16.0-16.8 in this region and failed the gate on every plate.
- **Board first:**
  - The value chain stays SEND IT > T HOT > lifted card > P tower > P hand > E occupied > E empty, each step 1 L* or more. The room sits below the occupied glass.
  - On the squint, the room has 0 loud cells (p95 0.31, under the 0.38 line). The board's p95 is 0.47, with 14 % loud cells.
  - The squint mean ratio, board / room, falls from 1.56-1.63 to 0.90-0.94. The room's mean is now above the board's. That mean includes the dark rings and the empty glass, so it is not the gate. The p95 ratio goes from 1.82-1.94 to 1.42-1.46.
- **Detail:**
  - The absolute high-pass detail in the box keeps 81-98 % of before: RMS 0.033-0.037, from 0.036-0.042. The event room is the lowest at 81 %.
  - Relative detail (RMS / mean luma) halves, because the mean roughly doubles.
  - At 1:1 the props, tanks, racks and benches still separate by their ink lines.
- **Saturation** in the box drops by 0.06-0.15: the haze and the lifted greys. The event room is the largest drop. Each room keeps its hue identity at 1:1: the green bio lab, the teal server room, the green-and-teal greenhouse, the violet event hall, and the amber shop on Meridian.
- **Pink share** stays at or under 0.034 % (limit 0.1 %).

### Godot

`grade.json` (rb2-1) and `../GODOT_PORT_SPEC.md` 4.1. The recommended path is still to bake the graded room offline, one PNG per room plus `room_shop_meridian_graded.png`. If the shader path is taken, it needs the rb2-1 steps from `order`. The skin picks the room through `corp_room`.

### Not done, and risks (stage 2)

- **The five other rooms** (srv, gh, rec, lobby, event) are composites on the p1 board. They are not real renders, and they are not checked on p2, p2b or p3. The real renders on all five beats use bio and shop, and pass. The grade is the same recipe, so they should behave the same.
- **The solve ran on composites** made before the scrim cut-out was added to the room region. The real-render numbers above come after the cut, and every plate lands inside the target.
- **Relative detail** is lower than step 6 (see Measurements). The review asked for a readable room, not a contrast target, and the absolute detail is kept. If a later review wants more snap in the room, the lever is `tone_s` / `tone_hi` (a stronger local curve), checked against the same gate.

Sources (scratch): `D:/rc_scratch/combat_redesign/locked/backdrop/src/`. Copies are in `../final/src_snapshot/backdrop/`:
- `fg_extract.py <corp>`: the board transfer, in a fresh cache per generator version (`FG_CACHE_TAG`);
- `bd2_lib.py`: compose and the room numbers;
- `bd2_solve.py` and `bd2_embed.py`: the ceiling solve and the `ROOMS` table;
- `bd2_publish.py`: this folder;
- `bd2_look.py`, `bd2_beats.py` and `bd2_shadow.py`: the looks and diagnostics used on the way.

## 2026-11-04 gate 1: re-published on the gate-1 board

The grade is unchanged (rb2-1, `grade.json`). All 9 plates were re-composited on the gate-1 p1 board: the `rb3_patch` fixes, the olive TURRET, K type and HP ticks at L* 84, the lit dying cell and the celadon Solace porcelain (`../final/NOTES.md`, "2026-11-04 gate 1").
- **Board transfer:** `fg_extract.py` re-run for neutral, Solace and Meridian, in fresh caches (`FG_CACHE_TAG=rb3b`).
- **Composite vs real render** (`../final/`): mean 0.107-0.125/255 and max 2/255, on `p1_bio`, `p1_bio_solace` and `p1_shop_meridian`.
- **Room** (gate region, scrim cut): mean L* 31.8-32.5 and p95 38.1 on every plate. The reference is the ring-NOW occupied glass p95, 51.1-51.3.
- **Checks:** `rb_checks` a-e pass on all 9 plates, and `checks.json` `all_pass` is true.
- **Room as seen** (scrim kept): on p1 it is within 2 L* of the gate value (`../final/checks.json`, room-as-seen row: 29.8-30.1). The p1 scrim is small. On p2 and p3 the taller HUD's scrim brings the as-seen value to 24.7-25.6 (`../final/NOTES.md`).
