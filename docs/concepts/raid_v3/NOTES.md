# Raid in Deface v3, on the 3D city (set 6), 2026-11-15

The raid screen in the Takeover fight's look (Deface v3, A-119), played on the 3D Solace city as the designer ruled
(2026-11-15, below). The raid rules and words are prototype Variant B v39. Layout as Takeover option A: CREW, rows and core tape
on the left; INCOMING, the shop and SEND IT on the right; the forecast HUD line at the bottom centre; the raid district in the
centre. Concept plates only (PIL); the numbers are illustrative. The first set (2D cell grid under glass) is kept in `grid_v1/`
as the record; it is superseded. Set 4 applies the designer's review of set 3 (the street district at 2x): smaller side
columns, a 3.5x camera, map objects sized to a cell, routes drawn cell to cell, one barricade representation. Set 5 put
it on a native Godot capture of the raid window (no upscale). Set 6 applies the designer's review of set 5: city detail in
the city layer (windows, shopfronts, blade signs, street lamps with pools) and routes as the red pencil line only.

## The city and the raid camera
- **Pixels: a native Godot capture of the raid window, no upscale.** Captured from **origin/main at `885975b6`** in a
  detached throwaway worktree (`D:/rc_tmp/capture_main`, removed afterwards; nothing committed or pushed). A scratch scene
  (`src/capture/raid_hi_capture.gd/.tscn`, adapted from the P3 `p1_depth_capture.gd`) sets up the same campaign as the P3
  capture (seed 7, HQ scene, raid shown, overlays and the network layer hidden), keeps the P3 depth30 camera's direction
  (rotation -40 / 45), aims the camera centre at the raid window's centre on city_default (1489.30, 942.11) and sets the
  ortho size to **124.0148 BU** (the window at 3.5x plus 10 %), at **3840x2160**. Camera position (1237.565, 1671.248,
  1297.660). That is K = 6.3636 capture px per city_default px. Run from the worktree after a headless `--import`:
  `python tools/run_windowed.py --log <log> --timeout 1500 -- res://tools/_scratch_capture/raid_hi_capture.tscn -- --out=<dir>`.
- **Grade:** `src/hi_grade.py` is the P2/P3 chain (recon, geo, grade, signs, reflections, haze, tone, as in
  `make_albedo4k`) ported to the capture: every screen-space field (warmth and ripple noise, the water streak, the hero light,
  haze noise and the depth range) is evaluated at each capture pixel's city_default coordinate, so it lines up with the 4k
  plate; blur radii are scaled by K and morphology by round(K). Sign walls are chosen on the P3 data and drawn by world
  position (1 of the 15 falls in this frame: the hero tower sign). Output `city_albedo_hi.png` (3840x2160) plus
  `ground_vis_hi.png` and `hi_frame.json`.
- **Match check** (`src/match_check.py`, the overlap brought to the 4k plate's density): raw capture against the P3 depth30
  raw, NCC 0.890, best shift 0, 0 px; 156 tiles of 64 px, median 0.869, p10 0.769, none under 0.5. Graded against
  `city_albedo4k.png`, NCC 0.928, shift 0, 0 px; tile median 0.896, p10 0.779, 1 % under 0.5. Same buildings in the same
  places; the city did not change in this district. (Measured on set 5, before the set 6 city detail was added.)
- **City detail (set 6):** `src/hi_detail.py`, called by `hi_grade.py` in linear light after the P3 signs and before
  reflections, haze and tone, so it is part of the city plate and sits under the raid's glass grade like the rest of the
  city. It follows the Near-street band of `netrun_cel/zoom_rules/ZOOM_RULES.md` (the plate is about 17 px per BU on
  screen), pruned for the raid. Everything is placed in world space from the capture's own per-pixel world positions and
  normals. Facade parts exist only on visible facade pixels, lamps are depth-tested against the capture's depth, and every
  choice is a hash of world-lattice ids (ZOOM_RULES salts 9810-9863), with no RNG. In this frame:
  - **Windows** on the 1.5 x 1.8 BU module above a 2.4 BU ground floor. They are dark glass slots, and about a third are lit
    in short vertical runs (amber, cream, a few teal), with a per-wall bias. Floor lines and the ground-floor ledge are
    darkened. About 330 lit windows.
  - **Storefronts** in 2 BU bays on walls whose pavement is open ground 1.6 BU out. 62 % of bays are lit shop windows
    (amber, cream, pink, teal, green), with two shelves and goods blocks; the rest are ribbed shutters with a warm seam.
    Each bay has a pilaster, a fascia board and, on about half the lit bays, a lit glyph strip. Lit bays spill a pool onto
    the pavement in front. 89 bays, 55 lit.
  - **Blade signs** on street-facing walls of buildings at least 6.6 BU tall: 0.9 x up to 3.4 BU, from 2.7 BU up, with a
    neon frame and five glyph blocks (glyph bars, since letters would be under 7 px). They are spaced at least 10 BU apart,
    in five hues, with light spilling onto the surrounding facade and a pool on the pavement. 8 in the frame.
  - **Street lamps** on the pavement, 1.4-2.0 BU off the building line: one candidate per 7 BU block, 72 % working, at least
    5 BU apart. Each has a 3.3 BU pole, a dark housing with a bright underside (78 % sodium, 22 % cool LED), a small halo, and
    a two-size ground pool. 41 lamps, 35 heads visible.
  - **Ground light:** pools and spill are splatted into a world (X, Z) raster at 0.25 BU and read back only at visible
    ground pixels, so they never land on roofs or hidden ground; a little also reaches the facade foot. Shop windows, signs
    and lamp heads feed the wet-street reflections at a low weight.
  - Values stay below the overlays: the glass grade desaturates and darkens the city, and routes, beacons and units read
    first on every plate.
- **Plate:** the raid window (548.6 x 308.6 px on city_default at (1214.8, 787.8)) is a float box of about 3491 x 1964
  capture px, Lanczos **down** about 1.82x to 1920x1080, then the under-glass grade (desaturated, darkened away from the
  district and under the side columns). No unsharp.
- **Geometry:** the camera is orthographic, so world to screen is affine. `city_geo.py` fits it from `world_pos_f16.npz`
  (residual 0.23 px median); the raid screen is `(p1080 - VIEW_O) * 3.5`. The plate and the map share the same float box,
  so the grid sits on the pixels. The ground visibility mask comes from the capture's own depth (world height above the
  ground under 1.6 BU, excluding the water id), at the capture's resolution.
- **District:** the low-rise street block south-west of the Solace HQ ring (the set 3 district, cropped tighter). The grid is
  7 x 7 cells on the city's own 6 BU lot lattice, X0 -195, Z0 -135 (edges at 3 mod 6 BU in world x and z). Cell names a-g along
  the north-east edge, 1-7 along the north-west edge. The cell diamond is about 145 x 93 px. Open streets: avenue b (world x
  -189..-183, the whole length), street 1 (north) and streets 6-7 (south), avenue e from row 3; low-rise blocks between them.
  The capture is centred on the district, so the district centre is at (960, 470) on screen as intended.
- **Side columns at 0.76:** CREW, rows, core tape and the left foot are drawn at full size on their own layer and shrunk 0.76
  towards the top-left corner; the work order, the BLACK MARKET sheet, REROLL and SEND IT towards the top-right corner (they
  stack in the top 760 px). The Evacuate chip shrinks about its own centre. The HUD line stays full size. The centre display
  between the columns grows from about 890 px to about 1130 px wide.

## Layers (bible 1.2 + designer rulings 2026-11-15)
| Raid element | Layer | Drawn as |
|---|---|---|
| Placement grid | system | thin cyan lines on the ground, faint the whole raid; hidden behind towers at a 22 % ghost. While something is held, legal cells get a dashed outline and a light fill |
| Operatives on the map | city (holo) | 2D stand-in for the bible 4.8 R3 class beacon, sized to one cell: a pad on the cell, a cone (about 8.5 BU, 110 px tall) opening to a cap ring about two-thirds of the cell wide, a scanlined emblem disc with the class glyph, in the role colour. A faint dashed reach outline on the ground when relevant (playback) |
| Operatives in CREW | runner: vinyl sticker | option B: the full roster in full colour; placed ones get "on c2" and a tick in pencil |
| Corp units | corp icon (bible 4.8 v4) | SHAPE = type: Trooper / Riot / Sniper = plain Solace capsule (Riot with a shield plate, Sniper with a barrel), Bike = capsule + `>>` badge, Heavy = block, Drone = diamond with four rotors and a 2x2 dot glyph, Wrecker = hexagon with a hammer glyph. FILL = Solace teal = health, draining top-down with a white line. RING = dashed teal circle, 1.85x, with status pips clockwise from top right (S slowed, H held, J jammed). Stack badge "x5". A ground disc under the unit drains the same way |
| Unit status values | pencil | the duration beside the pip ("2", "1") |
| INCOMING | corp paper under glass | the intercepted work order: Solace letterhead, WORK ORDER ref, a redaction bar, the v39 rows ("ROUND 1 (now) · 8 units", "A Trooper ×5  B Bike ×3"...) with mini v4 icons, a red INTERCEPTED stamp, a paper clip, glass sheen and cyan corners. The Cell's yellow pencil bracket marks the current round |
| Drag (held operative) | runner sticker | Takeover's model: the sticker trails the pointer (spring lag), lifted with a long shadow, tilted, motion streaks; a faint liner stays in its CREW slot; a yellow pencil arrow to the hovered cell, yellow circle = valid |
| Barricade, Safehouse, site B2, site core | runner: sticker | on the glass over their cell, sized to about one cell (Safehouse 0.66, barricade 0.56, site 0.66, core 0.56). The barricade is the sticker only; its health is a small pencil value beside it ("6 → 3") |
| Route cells | system | every cell a route travels: a faint red tint on the ground, with no chevrons (set 6). The entry cell (where the stack waits, off the district) is tinted stronger with a solid red edge; the end cell (Safehouse pink, site green) is tinted in its sticker colour with a solid edge |
| Routes, entries | pencil, red | one grease-pencil line through the cell centres, from the waiting stack cell to cell into the end cell, where it runs under the sticker. No arrowhead and no hatching; the direction is implied. A/B/C circles where it crosses the district edge |
| Forecast, kill ticks, notes | pencil | "2 leak" arrow, "8 → 6", "+3/+2/+1", hatched reach; no stop bar and no "holds" note (the HUD line says "A holds at b4") |
| Rows, chips, HUD line, SEND IT, shop sheet, report | unchanged from set 1, side ones at 0.76 | |

## Plates
| File | Shows |
|---|---|
| `r3_plan.png` | Round 1/4 at rest. KAI c2, VEX e5, MOTH a7 placed (beacons on the city; stickers stay in CREW with pencil cell + tick). Route A comes in from the north-west along street 1 and down avenue b; route B in from the south-east along street 6, then one cell down; both end at the Safehouse on c7. Barricade on b4 on route A, "6 → 3" beside it. Trooper ×5 waits at A, Bike ×3 at B. Pencil: red "2 leak" arrow into the Safehouse, "8 → 6". HUD: `A holds at b4 · B 2 leak · Core 8 → 6 · 6/8 killed`. |
| `r3_place.png` | RUNE held, Takeover drag: the sticker trails the pointer below right, the liner in its CREW slot, the yellow arrow to e7, circled. Legal cells lit. Reach hatched on the district's cells round e7; +3 / +2 / +1; B's "2 leak" struck, yellow 0; "safe". HUD: `IF PLACED e7 B 2 leak → 0 leak · Core safe · 8/8 killed`. |
| `r3_shop.png` | BLACK MARKET sheet: SHOTGUN peeled (glossy liner left) and slapped onto RUNE's SHOTGUN; "MERGE ☆+☆ → ☆☆"; credits 7 → 4. |
| `r3_playback.png` | Tick 3/8. A trooper held at the wall (H pip, pencil 2, −4), a bike slowed (S pip, pencil 1, −3, glide smear), a trooper bursting into teal/white bits; tracers from the KAI and VEX beacons, pencil ✕ tallies; reach outlines; HELD + BOMBARD ×2 word sticker; the wall's hp "6 → 4"; faint units still to enter; RUNE's beacon on e7; shop locked; SEND IT greyed + RESOLVING; tick bar. |
| `r3_site.png` | Site raid on B2, round 1/3: three lanes meet at the B2 site sticker on the b6 street crossing (A in from the south-east along street 6, B down avenue b from the north, C in from the south-west edge); the core one cell west (a6) with `8/8`; KAI "B2 crew" on e5; VEX "from C2" on a7 (arrow from off the map, lower left); the "who defends B2" note above left of the district; the Evacuate chip at the top centre; MOTH / RUNE grey "at A1" / "at D4". Core tape `CORE 8 → 7`, pencil "1 leak", "8 → 7". The chip reads exactly "Evacuate (give up B2 without a fight, KAI back to HQ)". |
| `r3_aftermath.png` | Solace AFTER-ACTION REPORT over the dimmed city: the Cell's pencil (circle, 30/34, ticks, "HQ untouched"), a yellow HELD sticker, CLASSIFIED in corp teal; the result panel; CONTINUE; CREW back with kill tallies. |
| `r3_sheet.jpg` | All six. |

## Calls I made (not designer rulings)
- **Zoom 3.5x** (designer: roughly 3.5-4x). At 4x a 7 x 7 district (1160 px wide) would not fit between the shrunk columns with
  room for the entry stacks; at 3.5x it is 1010 px wide with the stacks just inside.
- **Side columns: one uniform scale (0.76)**, not a re-layout. Everything shrinks together towards its corner, so the column
  layout and the sticker proportions stay as set 3. A rebuild of the work order with bigger type would be the next step (see
  weak points).
- **District kept: the SW street block, cropped to 7 x 7.** At 3.5x the camera window is small enough to centre on it (it could
  not be centred at 2x). It has real streets between low-rise blocks; the plaza is a park and the HQ-north block sits at the
  plate's top edge. Route A comes in along street 1 and down avenue b (one turn); B along street 6. The layout was re-placed
  for the 7 x 7 grid: Safehouse c7, barricade b4, KAI c2, VEX e5, MOTH a7, hovered cell e7; site B2 on b6, core a6.
- **Barricade: the sticker only.** The stop bar and the "holds f7" note are dropped; the HUD line already says "A holds at b4",
  and the hp is a small pencil value beside the sticker.
- **Routes are the pencil line only (set 6, designer).** Chevrons and the arrowhead are gone. The line runs 0.8 of the way
  from the last route cell's centre to the end cell's centre, so it ends under the Safehouse / site sticker.
- **Route-cell tint kept (my call, set 6).** I compared `r3_plan` with and without it. Without the tint the line alone carries
  the direction well, but which cells are on the path (what reach and placement are judged against) is harder to read, and
  the waiting entry stacks lose their cell. The tint stays faint (52/255, 70 on the entry cell), ghosted under buildings at 55 %.
  `python raid_v3_city.py --no-tint` renders without it.
- **City detail is pruned from the Near-street band:** about one lit window in three (the street plate's 8-12 % is too dark
  at this zoom; the HQ overview's 35-45 % too busy); no awnings, AC units, balconies, wires, cars or fascia letters; lamps
  about one per 7 BU rather than ZOOM_RULES' 12 m pairs on avenues; at most 12 blade signs (8 fall in the frame).
- **Beacons sized to the cell:** cone 8.5 BU (was 15), cap radius 2.8 BU (was 4.9), pad 1.6 BU; the emblem disc stays 42 px.
- **Pencil moved with the layout:** the leak note under the Safehouse (left of RUNE's reach), "8 → 6" left of it; in `r3_site`
  "8/8" and "8 → 7" right of and above the core (clear of VEX's cone).
- **Beacons stand on the north side of the routes.** A cone rises over the cells above it on screen; placed south of a route it
  covers the units on the route.
- **Unit icons are drawn over the route pencil and the map stickers** (they are UI icons, "icons far"), so a held or slowed unit
  is never hidden under the barricade or a red line. Beacons stay under the stickers (they are in the city).
- **The held sticker trails below right of the pointer** in `r3_place`, at its CREW size (0.86 x 0.76).
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
- **Stills only;** kill and forecast numbers are not from the sim; pencil and stickers are hand placed (build needs an
  auto-placer); the measured checks (contrast, minimum text size) were not run.

## Honest weak points
- **The capture is closer than the 4k plate, and the game renders some things differently at this zoom.** A few tall towers
  near the left edge render see-through (the city's zoom-dependent see-through band and LOD), and the ink outlines are thinner
  than on the 4k plate. Both are the game's own rendering at this camera size.
- **The ported grade is close but not identical** to `city_albedo4k`: a little less warm, with fewer and smaller lamp pools.
- **Only 1 of the 15 P3 sign walls falls in the frame**; the set 6 blade signs make up for it.
- **City detail is painted on the capture, not built in the city.** Signs are flat on the wall (no 1 m stand-off, no side
  face), and lamp poles are 2-3 px dark lines that mostly vanish on the dark ground, so the lamps read as heads and pools.
  Windows only follow the two axis-aligned facade orientations; hex and octagon facets stay blank. Shop and window cells
  are cut where the facade mask ends (corners, roof edge), so a few partial windows appear. Some low-rise walls show only
  one row of dark slots and read as almost blank under the glass grade.
- **Lamp reflections:** the wet-street pass turns lamp heads and shop windows into vertical streaks. I kept them short (low
  weight), but they add vertical lines in the district streets.
- **The detail is not checked against the game:** ZOOM_RULES is a spec, and the game does not draw these at this zoom yet.
  The plates show the target, not the current build.
- **The ground visibility mask is new** (from the capture's depth, not the P2 world positions); it is sharper, but it has only
  been checked by eye on these plates.
- **Rules text in the side columns misses the 16 px cap-height aim.** Measured from the font sizes: the HUD line is about 21 px
  cap (full size); the core tape title, the rows and the chips about 13-15 px; the work order's round heads about 11 px; its unit
  rows ("Trooper ×5") about 9 px, the smallest rules text on screen. Uniform scaling cannot reach the aim for the memo; it needs
  re-laying out (fewer groups per line, bigger type) or a wider right column.
- **The lit zigzag road under the district** (bottom of the play area) is bright and busy behind route B, the leak notes and
  the entry stacks; it is part of the plate.
- **The space-elevator tether** crosses in front of the district's east side (columns d-g); it is part of the plate.
- **Street blocks in front of avenue b** hide parts of its cells from this camera (the route tint drops to the ghost there);
  the pencil line carries the route through.
- **18 of 49 cells are blocks or hidden behind them** (under 60 % open ground): the low-rise blocks between the streets and
  the west edge (a3-a6). They are not placeable; the grid shows them at the ghost alpha.
- **Busy spots:** the hovered cell in `r3_place` (hatch, circle, +3, +2, the route B line through the hatch, pointer,
  arrow head) and the wall in `r3_playback` (held unit, pip, value, −4, kill bits, KAI's cone and tally, tracers).
- **The B entry stack sits at the bottom right**, close to the HUD line, and the C stack in `r3_site` close to the left column.
- **The dashed unit ring is faint** on the dark streets; the fill and pips carry the read.

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

(Sets 2-6 apply all six; the sentences above about "the plates above" and `r3_site.png` refer to the first set, now in `grid_v1/`.)

## Source
`src/raid_v3_city.py` (set 6 plates + sheet) and `src/city_geo.py` (camera fit, ground height and visibility), copied from
`D:/rc_scratch/raid_v3/src/`. They import `raid_kit.py`, `raid_v3.py` (report paper) and the Takeover v3 scripts read-only; the
first set's `raid_v3.py` is unchanged and still renders `grid_v1`.
- **Run:** `python raid_v3_city.py [plan place shop playback site aftermath sheet] [--no-tint]`; the city plate first with
  `python hi_grade.py [--no-detail]`.
- **Reads:** `D:/rc_scratch/raid_v3/city_hi/` (`city_albedo_hi.png`, `ground_vis_hi.png`, `hi_frame.json`; it falls back
  to `tide_concepts/p3_work/city_albedo4k.png` with an upscale if they are missing), `tide_concepts/p2_base/layers/world_pos_f16.npz`,
  `street_mask.png`, `occluder_mask.png` (read-only).
- **The city plate:** `src/capture/raid_hi_capture.gd/.tscn` (the scratch capture scene; it was run from a detached worktree
  of origin/main `885975b6` under `tools/_scratch_capture/` and is not part of the project), `src/hi_grade.py` (the grade
  port; reads the capture and the P3 data read-only, writes `city_hi/`), `src/hi_detail.py` (the set 6 city detail, imported by `hi_grade.py`),
  `src/match_check.py [raw|graded]` (the overlap check
  against the P3 plate).

## CREW roster options (for designer ruling 4), `crew_options/`
Same round-1 plan state for all three. On the map, the operatives are drawn as a stand-in for the bible 4.8 R3 class beacon
(ring and emblem disc with initials), because on the 3D city the operative on the map is the beacon, not the sticker. Only the
CREW column changes.
- **A** (`crew_A.png`): the liner outline is left behind, with the cell in pencil (as in `r3_plan`).
- **B** (`crew_B.png`): the full roster. The sticker stays, with "on b3" and a tick in pencil under it.
- **C** (`crew_C.png`): the full roster, with placed operatives dimmed (lower value and colour) and the cell in pencil; the bench
  sticker stays full bright. Dimmed must not read as the grey "away" state (grey vinyl with a red pencil reason).
- `crew_sheet.jpg`: all three side by side (the left column and map only). Source: `src/crew_options.py`.
