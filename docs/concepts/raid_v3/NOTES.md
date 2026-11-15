# Raid in Deface v3, on the 3D city (set 2), 2026-11-15

The raid screen in the Takeover fight's look (Deface v3, A-119), now played on the 3D Solace city as the designer ruled
(2026-11-15, below). The raid rules and words are prototype Variant B v39. Layout as Takeover option A: CREW, rows and core tape
on the left; INCOMING, the shop and SEND IT on the right; the forecast HUD line at the bottom centre; the raid district in the
centre. Concept plates only (PIL); the numbers are illustrative. The first set (2D cell grid under glass) is kept in `grid_v1/`
as the record; it is superseded.

## The city and the raid camera
- **Pixels:** `tide_concepts/p3_work/city_albedo4k.png` (3840x2160), the 4k render of the same frame as
  `p2_base/city_default.png` (aligned at 0,0 px). The raid camera is the same orthographic camera **2x closer**: a native-pixel
  1920x1080 crop of the 4k plate, window at (450, 20) on city_default. No upscale. Desaturated and darkened under the glass;
  the district stays brightest, the flanks under the panels darkest.
- **Geometry:** the camera is orthographic, so world to screen is affine. `city_geo.py` fits it from `world_pos_f16.npz`
  (residual 0.23 px median), then maps through the crop (x2). The ground visibility mask comes from the 1080 world positions,
  cropped and scaled 2x, so it is coarser than the picture.
- **District:** the lamp-lit plaza north of the Solace towers. The grid is 10 x 10 cells on the city's own 6 BU lot lattice
  (edges at 3 mod 6 BU in world x and z; streets are on this lattice). Cell names a-j along the north-east edge, 1-10 along
  the north-west edge. The cell diamond is about 82 x 53 px.

## Layers (bible 1.2 + designer rulings 2026-11-15)
| Raid element | Layer | Drawn as |
|---|---|---|
| Placement grid | system | thin cyan lines on the ground, faint the whole raid; hidden behind trees and towers at a 22 % ghost. While something is held, legal cells get a dashed outline and a light fill |
| Operatives on the map | city (holo) | 2D stand-in for the bible 4.8 R3 class beacon: a pad on the cell, a cone opening up to a cap ring (about 112 px tall), a scanlined emblem disc with the class glyph, in the role colour. A faint dashed reach outline on the ground when relevant (playback) |
| Operatives in CREW | runner: vinyl sticker | option B: the full roster in full colour; placed ones get "on e8" and a tick in pencil |
| Corp units | corp icon (bible 4.8 v4) | SHAPE = type: Trooper / Riot / Sniper = plain Solace capsule (Riot with a shield plate, Sniper with a barrel), Bike = capsule + `>>` badge, Heavy = block, Drone = diamond with four rotors and a 2x2 dot glyph, Wrecker = hexagon with a hammer glyph. FILL = Solace teal = health, draining top-down with a white line. RING = dashed teal circle, 1.85x, with status pips clockwise from top right (S slowed, H held, J jammed). Stack badge "x5". A ground disc under the unit drains the same way |
| Unit status values | pencil | the duration beside the pip ("2", "1") |
| INCOMING | corp paper under glass | the intercepted work order: Solace letterhead, WORK ORDER ref, a redaction bar, the v39 rows ("ROUND 1 (now) · 8 units", "A Trooper ×5  B Bike ×3"...) with mini v4 icons, a red INTERCEPTED stamp, a paper clip, glass sheen and cyan corners. The Cell's yellow pencil bracket marks the current round |
| Drag (held operative) | runner sticker | Takeover's model: the sticker trails the pointer (spring lag), lifted with a long shadow, tilted, motion streaks; a faint liner stays in its CREW slot; a yellow pencil arrow to the hovered cell, yellow circle = valid |
| Barricade, Safehouse, site B2, site core | runner: sticker | on the glass over their cell, larger than set 1 (barricade 0.8, Safehouse 1.0). Barricade hp in pencil beside it |
| Routes, entries | pencil, red | along the lattice streets of the plaza, A/B/C circles at the district edge |
| Forecast, kill ticks, notes | pencil | as set 1 (stop bar, "holds f9", "2 leak" arrow, "8 → 6", "+3/+2/+1", hatched reach) |
| Rows, chips, HUD line, SEND IT, shop sheet, report | unchanged from set 1 | |

## Plates
| File | Shows |
|---|---|
| `r3_plan.png` | Round 1/4 at rest. KAI e8, VEX f5, MOTH h8 placed (beacons on the city; stickers stay in CREW with pencil cell + tick). Barricade at f9 on route A; Trooper ×5 waits at A, Bike ×3 at B. Pencil: stop bar, "holds f9", wall hp "6 → 3", red "2 leak" arrow into the Safehouse, "8 → 6". HUD: `A holds at f9 · B 2 leak · Core 8 → 6 · 6/8 killed`. |
| `r3_place.png` | RUNE held, Takeover drag: the sticker trails the pointer below right, the liner in its CREW slot, the yellow arrow to i6, circled. Legal cells lit. Reach hatched on the ground (3x3 round i6); +3 / +2 / +1; B's "2 leak" struck, yellow 0; "safe". HUD: `IF PLACED i6 B 2 leak → 0 leak · Core safe · 8/8 killed`. |
| `r3_shop.png` | BLACK MARKET sheet: SHOTGUN peeled (glossy liner left) and slapped onto RUNE's SHOTGUN; "MERGE ☆+☆ → ☆☆"; credits 7 → 4. |
| `r3_playback.png` | Tick 3/8. A trooper held at the wall (H pip, pencil 2, −4), a bike slowed (S pip, pencil 1, −3, glide smear), a trooper bursting into teal/white bits; tracers from the KAI and VEX beacons, pencil ✕ tallies; reach outlines; HELD + BOMBARD ×2 word sticker; faint units still to enter; RUNE's beacon on i6; shop locked; SEND IT greyed + RESOLVING; tick bar. |
| `r3_site.png` | Site raid on B2, round 1/3: three lanes (A, B, C) cross at the B2 site sticker on the plaza streets; the core one cell behind with `8/8`; KAI "B2 crew"; VEX "from C2" (arrow from off the map); MOTH / RUNE grey "at A1" / "at D4". Core tape `CORE 8 → 7`, pencil "1 leak", "8 → 7". The chip reads exactly "Evacuate (give up B2 without a fight, KAI back to HQ)". |
| `r3_aftermath.png` | Solace AFTER-ACTION REPORT over the dimmed city: the Cell's pencil (circle, 30/34, ticks, "HQ untouched"), a yellow HELD sticker, CLASSIFIED in corp teal; the result panel; CONTINUE; CREW back with kill tallies. |
| `r3_sheet.jpg` | All six. |

## Calls I made (not designer rulings)
- **Raid zoom 2x, from the 4k plate** (designer update: the city_default zoom must not be the default). 2x was the closest
  zoom with native pixels; the district (grid, both routes, Safehouse) fills the centre and buildings read. A closer zoom would
  need upscaling; the script supports it (`VIEW_ZOOM`), Lanczos + light unsharp.
- **District = the plaza**, 10 x 10 cells. The towers south of it hide almost all street ground from this camera; the plaza is
  the one open district between the columns. Routes run on its lattice lanes.
- **Beacons stand on the north side of the routes.** A cone rises about two cells on screen; placed south of a route it covers
  the units on the route.
- **Unit icons are drawn over the route pencil and the map stickers** (they are UI icons, "icons far"), so a held or slowed unit
  is never hidden under the barricade or a red line. Beacons stay under the stickers (they are in the city).
- **The Safehouse sticker is slapped over the route ends**, so routes run into it instead of ending in arrowheads on top of it.
- **The held sticker trails below right of the pointer** in `r3_place`, not below left (the side it came from). Below left it
  would cover the Safehouse and the A route; the arrow still runs from the sticker to the cell.
- **Status pips carry a letter** (S / H / J) and the pencil carries the value; the bible gives the pip order, not a glyph set.
- **No "on slap" motion frame.** The slap → bits → beacon beat is not drawn (stills only).
- From set 1, still standing: the CLASSIFIED stamp is corp teal (a held raid is never red); the shop locks in playback with
  "shop opens after the round".
- **Removed:** set 1's invented "B2 to the corp, crew walks"; the site core is 8 (`CORE 8/8`, forecast 8 → 7).

## Placeholders and limits
- **Invented words:** street/site names, callsigns and roles, "CLEAN SWEEP", the report and work order rows outside v39's
  words (WORK ORDER ref, TARGET, AUTHORISED, DO NOT FORWARD), "BLACK MARKET", credits 12 at the end.
- **Beacon is a 2D stand-in** (cone, ring, scanlined disc), not the R3 model. Unit icons are a first pass at v4 for Solace;
  the Riot / Sniper / Wrecker variants are my guesses at "plain body" and "verb glyph".
- **Ground visibility is coarse** (from 1080 world positions scaled 2x), so grid lines fade under trees with soft edges.
- **Stills only;** kill and forecast numbers are not from the sim; pencil and stickers are hand placed (build needs an
  auto-placer); the measured checks (contrast, minimum text size) were not run.

## Honest weak points
- **The 4k plate has a slightly different grade** from city_default (it is the albedo pass with lights); under the glass grade it
  reads fine, but it is not the shipped grade.
- **The plaza is a park, not a street grid.** Its lanes are lattice lines between tree clumps and lamps; the routes follow the
  lattice, but at this zoom they read as paths across a plaza more than as streets between buildings.
- **Busy spots:** at the wall in `r3_playback` (held unit, pip, value, −4, kill bits, KAI tally, tracers) and the hovered cell in
  `r3_place` (hatch, circle, +3, +2, pointer, arrow head).
- **Beacon cones overlap stickers and labels** where they rise (KAI over the B2 site sticker top in `r3_site`).
- **The dashed unit ring is faint** on the dark plaza; the fill and pips carry the read.
- **The lower centre is towers with little on them** (the forecast pencil and the "who defends" note sit there).

## Designer rulings, 2026-11-15 (on this set)
These replace the open questions that were here. The plates above predate them and are not re-rendered yet.
1. **3D city for everything.** The raid and the netrun play on the 3D city. v39's 2D grid was for gameplay testing and design
   only. The placement cell grid is drawn on the city, **faintly visible** the whole raid.
2. **Corp units: the bible's version** (4.8: locked vehicle models close, v4 icons far; fill = corp colour = health; the dashed
   status ring with pips). The enamel tokens and sticker statuses in these plates are a fallback if that does not work.
3. **INCOMING: the bible's intercepted work order** (memo under glass, corp letterhead, INTERCEPTED), not corp tickets.
4. **CREW shows the full roster: option B** (designer, from `crew_options/`). A placed operative's sticker stays in full colour
   with its cell and a tick in pencil under it; the map shows the operative as its R3 class beacon.
5. **Drag model: Takeover's.** The held sticker follows the cursor with spring lag and leaves a liner outline. This deviates from
   bible 4.8 (park above the slot).
6. **Site raid rules are not open.** v39 already sets them: the core is 8 (`siteRaidCore`); EVACUATE reads "Evacuate (give up B2
   without a fight, KAI back to HQ)" and ends the raid at once (site taken, no fight, Heat as an overrun raid). `r3_site.png`
   is wrong on both: its core reads 6 → 5 and its chip text "B2 to the corp, crew walks" is invented.

(Set 2 applies all six; the sentences above about "the plates above" and `r3_site.png` refer to the first set, now in `grid_v1/`.)

## Source
`src/raid_v3_city.py` (set 2 plates + sheet) and `src/city_geo.py` (camera fit, ground height and visibility), copied from
`D:/rc_scratch/raid_v3/src/`. They import `raid_kit.py`, `raid_v3.py` (report paper) and the Takeover v3 scripts read-only; the
first set's `raid_v3.py` is unchanged and still renders `grid_v1`.
- **Run:** `python raid_v3_city.py [plan place shop playback site aftermath sheet]`.
- **Reads:** `tide_concepts/p3_work/city_albedo4k.png`, `tide_concepts/p2_base/layers/world_pos_f16.npz`, `street_mask.png`,
  `occluder_mask.png` (read-only).

## CREW roster options (for designer ruling 4), `crew_options/`
Same round-1 plan state for all three. On the map, the operatives are drawn as a stand-in for the bible 4.8 R3 class beacon
(ring and emblem disc with initials), because on the 3D city the operative on the map is the beacon, not the sticker. Only the
CREW column changes.
- **A** (`crew_A.png`): the liner outline is left behind, with the cell in pencil (as in `r3_plan`).
- **B** (`crew_B.png`): the full roster. The sticker stays, with "on b3" and a tick in pencil under it.
- **C** (`crew_C.png`): the full roster, with placed operatives dimmed (lower value and colour) and the cell in pencil; the bench
  sticker stays full bright. Dimmed must not read as the grey "away" state (grey vinyl with a red pencil reason).
- `crew_sheet.jpg`: all three side by side (the left column and map only). Source: `src/crew_options.py`.
