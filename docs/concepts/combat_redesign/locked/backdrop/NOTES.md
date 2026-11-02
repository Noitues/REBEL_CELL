# Backdrop and loudness re-tune (roadmap step 6)

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
