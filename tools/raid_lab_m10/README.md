# Sweep-raid lab, round 7 (L7: the target frames' look and the suspense motion; the L5 rules, the L6 readability pass)

A playable Godot prototype of the round-5 sweep raid, so a critic can judge suspense, decision depth and readability in motion
with every number coming from one rules engine. A design tool, not part of the game: nothing outside `tools/raid_lab_m10/` is
touched. Briefs: `docs/handoff/raid_lab_l5/BRIEF.md` (rules), `docs/handoff/raid_lab_l6/BRIEF.md` (readability),
`docs/handoff/raid_lab_l7/BRIEF.md` (look and motion). Rules source of truth: `tools/raid_concepts/sweep_l5.py` (python; it builds
on `sweep_l4.py`, `sweep_l3.py` and `sweep_l2.py`). The folder name `raid_lab_m10` and the scene `raid_lab_m10.tscn` are kept as
the entry point.

## Round 7 (L7): what changed

**No rule changed.** `l5_rules.gd` and `data/l5_golden.json` are untouched and `parity_check.gd` passes unchanged (2433 checks).
The designer ruled on 2026-10-22 that the raid lab does its own visual and motion pass (no art-pass routing). Target: the three
Blender frames in `docs/design/raid_concepts/raid_target/` (README there: palette, board, camera). Motion follows
`docs/STYLE_GUIDE.md` section 5.3: raids play from the resolver's events and are never recomputed.

### The look

- **A 3D board behind the 2D overlay.** `l7_board.gd` (`L7Board`) builds the frames' set in a `SubViewport` the size of the screen:
  the slab with its amber rim and faint cyan grid, the copper links, a hex pedestal and tower per asset (gold caps and slits; DOWN
  grey and scattered; TAKEN cobalt on corp ground; go dark a black dome; the decoy a gold octahedron; a ghost a gold wire holo
  with a dashed floor ring; HOME's three-tier tower), cobalt-eyed pylons where lines start, the wireframe skyline, the data motes,
  bloom. It holds no rule and no state: the view hands it the cell statuses every frame (`apply`) and it rebuilds only the cells
  whose look changed. Geometry, palette and materials are `tools/raid_concepts/target/raid_scene.py`'s.
- **The same camera for the overlay.** `l7_cam.gd` (`L7Cam`) is the Blender camera (116 mm lens, the frames' position) as a pure
  pinhole projection at 0.54 of the frame, shifted so the board sits left of the side panel. Beams, rings, chips and pills are
  drawn in 2D at projected positions (`nx(c)` the beam plane over a cell, `chip_at(c)` the chip floating over the tower), so they
  land on the 3D towers and stay deterministic and headless-testable. The L6 lanes (`LANE` px apart, centered) are unchanged.
- **Palette and type** (`l5_glyphs.gd`): threats cobalt `#3D6BFF` with a hot `#9FC0FF` core, the Cell and HOME gold `#FFD24D` and
  amber `#FFB020`, Heat orange `#FF6A1A`, loss red `#FF3D4D`, the spoof and what holds in the Cell's acid `#D4FF00` (it replaces the
  old teal everywhere: SKIP and JAM marks, the lime chevron, EVADED). Anton for numbers, stamps and headlines, Share Tech Mono for
  labels, IBM Plex Sans Condensed for body text, chosen by `font_for` so every measure and every draw agree.
- **Restyled, not removed** (every L6 no-words glyph is still there): value pips (under the number in the chip), the dark eye and
  its struck income pip, the Heat meter's notches with their beam glyphs (the meter is the frames' orange bar; the glyph pops and
  pulses when a line is crossed), the lanes, the sealed-outcome pills, the kit strip, the DECIDED banner, the BREACH warning. Panels
  are dark slabs with a hairline edge and a soft glow in the edge colour (amber the Cell's, cobalt threats, acid the spoof, red loss);
  buttons are Anton on gold. New from the frames: word tags over placed levers (GHOST, DECOY, DARK) and over the hunter's column,
  a PLACED chip on a lever card, SKIP TARGET and JAM TARGET tags, the big BEAM 2 UNSEALED headline.
- **Where the frames and the rules disagree, the rules win.** The impact stamp reads the rules' tier word (CELL BATTERED, CELL
  DAMAGED, BREACHED ... with `2 DOWN  HOME -1` under it), never the frame's "HOME -1 / HOLDS" (a home hit is DAMAGED). The frames
  omit HOLD; the response screen keeps HOLD beside every SKIP and JAM.

### The motion (all timings in `l7_config.gd`, `L7Config`)

| # | Beat | What plays | Config |
|---|------|-----------|--------|
| 1 | Launch | a beam glows at its pylon (lead), then its head sweeps cell by cell along its fixed lane; every touched cell flashes (a hex ring spreads on the floor, the chip rings out, the tower lights); a decoy pulls the beam aside with three arcs and stops it | `BEAM_LEAD`, `STEP_T`, `FLASH_T`, `DECOY_PULL_T` |
| 2 | Unseal | the three sealed lines shimmer; two collapse back to their pylons and are struck out with a red X; the real line ignites end to end; the lit line then holds before it fires | `UNSEAL_T`, `UNSEAL_SHIMMER_END`, `UNSEAL_COLLAPSE_END`, `FIRE_HOLD` |
| 3 | Spoof window | every SKIP target pulses in lime brackets, JAM pulses on the hunter's column; a countdown ring and a draining bar run in the response box and never force a pick (the lab is turn-based); the pick draws the skipped node's bypass arc, or strikes the hunter's turn out with a red X | `DECIDE_RING_T`, `PICK_FX_T`, `PULSE_T` |
| 4 | Hunter | the turn arrow draws from the first touch, then the beam runs down the column | `TURN_T`, `HUNTER_LEAD` |
| 5 | Impact | DOWN: the wrench drops onto the node with a bounce and the node shakes; TAKEN: the ground flips (the tower squashes through zero and comes back in corp cobalt, the flag pops in); HOME: the tower and ring flash red, a red -1 floats up, the HUD pip goes at once and a white lag bar drains behind it | `WRENCH_T`, `SHAKE_T`, `FLIP_T`, `HOME_LAG_DELAY`, `HOME_LAG_T`, `HOME_NUM_T` |
| 6 | Stamp | the tier stamp drops in large and slams onto the board with echo slabs and speed lines, and stays into the aftermath; on the leg record the verdict counts up (CELL KEPT, HOME, the score bars, the difference) | `STAMP_DELAY`, `STAMP_T`, `END_T`, `COUNT_UP_T` |
| 7 | Heat | the meter eases to the new Heat; every line crossed pulses (a ring, the notch glyph popping); on the between screen the NEXT RAID strip shows one chip per beam as the meter fills, the new beam's chip popping in | `HEAT_EASE_T`, `HEAT_PULSE_T` |
| 8 | Settled breach | the L6 fast playout under THE CELL FALLS, HOME draining to 0 with its lag bar, the BREACHED stamp, then the BREACHED card slamming in over the dead board | `FAST_*`, `BREACH_CARD_T` |

Controls: speed 1x / 2x / 4x (keys 1 2 4 or the buttons; it scales the whole raid layer), SKIP (S), and **INSTANT** (key I or the
button; `--instant` on the command line): the playout runs to the next decision or to its end in one frame with every effect drawn
settled, for captures. The same events happen in the same order either way.

How it is built (STYLE_GUIDE 5.3): `L5Play` still sequences the beats from `L5Rules.resolve`; `L7Fx` (`l7_fx.gd`) reads the new
events after every advance into an ordered cue list (launch, touch, decoy pull, unseal, spoof window, pick, hunter turn, impact,
stamp); the view draws every effect from the events' own times and those cues. Nothing is recomputed for the show.

### Checks

`parity_check.gd`: unchanged, PASS (log `D:/rc_tmp/raid_design_lab/lab_l7/parity_final.log`). `flow_check.gd`: all L6 checks, plus
(`_motion` and the per-raid ones): **the event order of the animation equals the resolver's touch order** (every raid of the planned
and naive lines of all golden legs, and the scene runs), **instant mode yields the same final state, ledger and cues as animated
mode** (legs 0 and 3 planned, 0 and 8 naive, and the settled breach), instant needs no pacing, 1x / 2x / 4x finish a raid in
about 1 : 1/2 : 1/4 of the frames, key I and the button toggle instant, the camera (the aim point lands, chip above beam above
floor, columns left to right, the whole slab left of the panel and under the HUD), and the timings are positive and ordered.

### Captures (`capture_l7.py`, `compare_sheet.py`)

`python tools/raid_lab_m10/capture_l7.py` runs, one at a time through `tools/run_windowed.py`: the four still sets, the two Movie
Maker clips and the comparison sheet. Output (this round, all under `D:/rc_tmp/raid_design_lab/lab_l7/`):

- `shots/` leg 0 planned line, `shots_breach/` leg 0 naive line (the settled breach and the BREACHED card), `shots_scrambled/`
  leg 5 planned with `--scramble`, `shots_jam/` leg 3 planned (raid 1 jams the hunter). New frames per raid, by label:
  `launch_b1`, `beam_*`, `impact_down` / `impact_taken` / `impact_home` / `impact_decoy`, `unseal_shimmer`, `unseal_collapse`,
  `unseal_ignite`, `decision`, `after_decision`, `hunter_turn`, `stamp_slam`, `after_open` / `after_heat`, `between_fill_a` /
  `between_fill_b` (the meter filling), `fall_home_drain`.
- `clips/planned_raid.avi` and `clips/breach_raid.avi` (Movie Maker, 1280x720, 30 fps), key frames in `clips/frames/planned_raid/`
  and `clips/frames/breach_raid/` (8 each, saved from the very frames the clip records).
- `comparison_sheet.png`: each target frame next to its lab still.

Which frames show which beat (stills in `shots/`, raid 1 unless noted; clip key frames in `clips/frames/planned_raid/` (P) and
`clips/frames/breach_raid/` (B)):

| Beat | Stills | Clip frames |
|---|---|---|
| 1 Launch (cell by cell, flash, decoy pull) | `04_r1_launch_b1`, `05_r1_impact_down`, `06_r1_beam_b1`, `07_r1_impact_decoy` | P `01_launch_flash`, P `02_impact_down` |
| 2 Unseal (shimmer, two collapse, real ignites) | `08_r1_unseal_shimmer`, `09_r1_unseal_collapse`, `10_r1_unseal_ignite` | P `03_unseal_collapse`, P `04_unseal_ignite` |
| 3 Spoof window and pick | `11_r1_decision`, `12_r1_after_decision` (SKIP bypass arc); JAM struck out in `shots_jam/` `11_r1_decision` to `13_r1_beam_b2` | P `05_spoof_window` |
| 4 Hunter | `14_r1_hunter_turn`, `15_r1_beam_hunter` | |
| 5 Impact (wrench, flip, HOME drain) | `06_r1_impact_down`, `30_r2_impact_taken` (flip), HOME in `shots_breach/` `13_r1_impact_home` and `34_r2_impact_home` | P `02_impact_down`, B `02_home_hit`, B `03_home_drain` |
| 6 Stamp, count-up | `16_r1_stamp_slam`, `19_r1_aftermath`; `72_record` (settled count) | P `06_stamp`, B `04_stamp`, B `07_record_count` |
| 7 Heat pulse, next-raid beams | `17_r1_after_open`, `18_r1_after_heat`, `20_r1_between_fill_a` / `21_r1_between_fill_b` | P `07_between_fill` |
| 8 Settled breach | `shots_breach/` `51_r2_between_picked` (DECIDED), `52_r3_fall_start`, `53_r3_fall_home_breached`, `54_r3_fall_home_drain`, `55_r3_breach` | B `00_decided` to `06_breached_card` |

New flags: `--instant`, `--speed=0|1|2`, `--maxshots=N`, `--clip=planned|breach` with `--clipdir=<dir>` (a scripted real-time run for
Movie Maker: `... res://tools/raid_lab_m10/raid_lab_m10.tscn --write-movie <file>.avi --fixed-fps 30 -- --clip=planned --clipdir=<dir>`).

### L7 known gaps

- The overlay is 2D over the 3D board: beams and rings are light ribbons drawn with layered alpha, not 3D light, so the board is not
  lit by the beams (the towers light only through the per-cell flash light). The frames' translucent blue beam volumes are a flat
  ribbon with a floor wash here.
- The board is drawn at 0.54 of the target frame so that it fits left of the 460 px side panel in the lab's 1280x720 window; the
  towers and chips read smaller than in the frames. The 3D set (pylons, skyline) is dressing: it never changes the rules' picture.
- Pylons are lit by where a line starts (rows from left or right, columns from the top); a column that starts at the bottom has no pylon.
- The fast breach has no head travel (L6: one 0.5 s beat per beam, all steps at once), so its motion is the flashes, the HOME
  drain and the card, not a sweep.
- In a capture the effects of one frame are paced by the capture script (a fixed step of 0.05 s, settled before each screen shot);
  the clips are the real-time motion.
- Text scale 1.0, mouse and keyboard only, as before.

## Round 6 (L6): what changed

Presentation only. The rules (`l5_rules.gd`, `l5_golden.json`, `sweep_l5.py`) are untouched and `parity_check.gd` passes unchanged.
Brief: `docs/handoff/raid_lab_l6/BRIEF.md`; the findings it answers are in `docs/design/raid_concepts/_reviews/REVIEW_LAB_L5.md`.

**No-words pass** (every item reads with `--scramble` on):

- **Node value as pips.** One small square per 2 of value under the number (`L5Glyphs.pips`, `PIP_VALUE`), on every node status
  (OK yellow, DOWN grey, TAKEN cobalt). Income chips (go dark, between screen) use the same pip, one per point of income.
- **Go dark has its own look.** A hollow, dimmed node (no fill, thin grey ring) with a closed-eye glyph and dim pips, and its income
  chip struck in red. It no longer resembles DOWN (grey fill, bolt). Dark on a DOWN or TAKEN node keeps that look and gets a
  closed-eye chip.
- **Heat meter as a danger gradient** (calm blue, warm yellow, hot red), with two hard notches at 50 and 75. Each notch carries
  the glyph of the beam it adds (a beam arrow with one "+" at 50, two at 75), and that same glyph is the badge on the beam it adds
  (`L5Glyphs.beam_plus`, used by `badge` for "+" and "++": the start badge, the track, the contact chips).
- **Beams in fixed lanes.** `_offsets()`: beams on one row or column take fixed, ordered lanes (beam 1, extra, extra 2, the three
  sealed lines), `LANE` = 18 px apart, **centered on the row or column**, so none sits on another or drifts between rows. Only the
  beams that run this raid take a lane (`lane_extra`). Every column also reserves a lane after its own lines for the hunter
  (`_h_off`), and the plan's per-shape hunter columns take the lanes beyond. Fixes `shots_jam/36_r3_no_spoof_left`.
- **Sealed-line outcomes on the board.** In the forecast each sealed line's result is a pill on its own line, in its lane, next to
  the cell it hits: the line's shape plus DOWN (bolt), TAKEN (corp flag) or HOME with -1 (`_outcome_pill`); the hunter's touch
  under that line sits in the hunter's lane below the node. The side-panel table stays.
- **Good play reads as good.** The leg record has a verdict strip: the assets as glyphs, "CELL KEPT 4/6", "HOME 3/3" with pips, and
  the score against the golden careless line of the same leg (two bars and the difference; "CARELESS: BREACH" when that line loses
  the campaign). Presentation of `final_score()` and the golden `naive` score.

**No dead raids.**

- **A certain loss is settled at once.** When `breach_risk` for the next raid is 3/3 on every intensity (`L5Model.breach_settled()`,
  live with the picks), the between screen shows a red DECIDED banner and the button reads "LAUNCH: THE CELL FALLS". Launch plays
  the raid in **fast mode** (`L5Play.fast`: one 0.5 s beat per beam, all steps of a beam at once, no decision, no "no spoof left"
  beat, HOLD, no levers) straight to the BREACHED card, under a "THE CELL FALLS" banner. No contact, plan or forecast screen. The
  result is the slow playout's (checked): every plan and every response loses HOME in that raid.
- **Warn one step earlier, in the plan.** A "kit after this raid" strip under the grid (`L5Model.kit_after_preview()`,
  `_draw_kit_strip`): the kit the plan leaves (ghosts, decoys, spoofs, go dark; a spoof counts whole, it is spent only if used after
  the reveal), the Heat the plan leaves on a meter with the 50 and 75 glyphs (the ghost's +5, no evade credit), and "next raid: N
  beams, M levers left" with N = beams at that Heat plus the cheapest run (LOW, +6). **Amber** when the plan spends the last kit item
  and N is more beams than this raid. No new rule: `kit_left`, `heat_now`, `extra_count`. Demo frames: `--demo=amber`.

Capture flags added: `--demo=amber`. New checks in `flow_check.gd`: the lanes (distinct, ordered, centered, hunter lane clear, over
the six legs and 0/1/2 extras), pips = value / 2, the kit strip against what every golden planned raid really leaves (kit, Heat,
beams, and the real next raid after a LOW run), the amber cases, the settled breach (settled after raid 2 on the naive leg 0, not
settled on a planned leg, fast playout with no decision screen and no contact / plan / forecast, one beat per beam, same result as
the slow playout).

Delivered L6 runs are in `D:/rc_tmp/raid_design_lab/lab_l6/`: `shots/` (leg 0, planned, 45 frames), `shots_breach/` (leg 0, naive,
35 frames: `30_r2_between_picked` DECIDED, `31_r3_fall_start`, `32_r3_fall_home_breached`, `33_r3_breach`, `34_record`),
`shots_scrambled/` (leg 5, planned, scrambled, 42 frames), `shots_jam/` (leg 3, planned, 42 frames), `shots_amber/` (2 frames).

**Earlier rounds were replaced, not kept behind a `RULESET` constant.** The L4 code (`l4_*.gd`, `l4_golden.json`) is in git
history (commit 14a7f25f and earlier); L3 and L2 before that. The critic reviews that drove the rounds are
`docs/design/raid_concepts/_reviews/REVIEW_LAB_L2.md`, `REVIEW_LAB_L3.md` and `REVIEW_LAB_L4.md`.

## Run it

- Play: open `res://tools/raid_lab_m10/raid_lab_m10.tscn` and run the scene (1280x720, text 1.0, mouse and keyboard).
  Windowed runs from a script go through `python tools/run_windowed.py` only.
- Parity check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/parity_check.gd`
- Flow check (headless): `godot --headless --path . -s res://tools/raid_lab_m10/flow_check.gd`
- Captures: `python tools/run_windowed.py --log <log> -- --resolution 1280x720 res://tools/raid_lab_m10/raid_lab_m10.tscn -- --shots=<abs dir> [--leg=0|3|5|8|11|14] [--line=planned|greedy|naive] [--lite] [--scramble] [--spoofview=range|off] [--key=<label>] [--demo=breachfix|ownline]`
  plays the whole leg of 3 raids through the lab's own input path (each raid really played: levers, forecast, sweep with the
  response after the reveal, aftermath, the between screen with the repair, shop and intensity), following a golden line, saving a
  numbered PNG per screen and per playout beat. `--lite` takes fewer frames, `--scramble` runs the no-words test.
  `--demo=breachfix` takes 3 frames of the pre-launch breach warning that names a lever (golden naive leg 0 at raid 3 with one
  ghost put back in the kit). `--demo=ownline` takes frames of the hunter's own line (every asset TAKEN, HOME ghosted).
  L5 runs (in `D:/rc_tmp/raid_design_lab/lab_l5/`; L6 runs are listed above): `shots/` (leg 0, planned line, 45 frames), `shots_breach/` (leg 0, naive
  line, breach in raid 3, 38 frames; in L6 the naive leg 0 skips raid 3's screens and plays it fast), `shots_scrambled/` (leg 5, planned, scrambled, 42 frames), `shots_jam/` (leg 3, planned:
  raid 1 jams the hunter, 42 frames), `shots_ownline/` (9 frames). Leg 0's planned line never uses JAM (it holds or skips), so the
  JAM frames are in `shots_jam/` (`06_r1_decision`, `07_r1_after_decision`, `08_r1_beam_b2`, `09_r1_aftermath`); the scrambled
  leg 5 also jams in raid 2 (`22_r2_decision` .. `25_r2_aftermath`). Every frame was re-read after the last code change.

## Rules (as built, from `sweep_l5.py`)

Unchanged from L2: ONE network for the leg of 3 raids (4 x 3 grid, 6 assets of value v, the HOME server with integrity 3);
OK -> DOWN -> TAKEN, a find on HOME costs 1 integrity and 0 is BREACHED; Heat bands (extra known beams from 50 and from 75); the
sealed beam (3 candidates), the hunter, the ghost's +5 Heat, the evade's -10 Heat, repair = v // 2.
Unchanged from L3 and L4: the leg kit (2 ghosts, 2 decoys, 2 spoofs, 2 go dark; at most 1 ghost, 2 decoys, 1 dark per raid), one
shop buy and the run intensity between raids, Heat carries into the score (1.0 per point above 44), the seeded real sealed line
and the shape shuffle (no reveal tell), the BATTERED tier.

New in L5:

- **The response after the reveal has two forms, plus holding.** A spoof from the kit is either **SKIP** (beam 2 skips one node of
  the revealed line, as before) or **JAM** (the hunter does not run this raid). Either adds `SPOOF_HEAT` (2) Heat after the sweep,
  so saving now trades against the next raid's beam count. HOLD costs nothing and keeps the spoof. `responses(state, b2)` lists
  them: HOLD, one SKIP per node of the lit line, JAM (HOLD only when the kit holds no spoof).
- **Re-drawn sealed lines.** The golden's candidates are used as given: each raid's three lines are distinct and hit different,
  non-empty sets of asset / HOME cells, so the reveal always matters (checked in `parity_check.gd`).
- **One repair per between step** (`REPAIR_SLOTS` = 1; the rules ignore a second one). DOWN assets pile up; a second find TAKES.
- **`breach_risk(leg, i, state)`**: over every allocation the kit allows, the fewest sealed lines on which every response (hold,
  each SKIP, JAM) still empties HOME. 0 means some plan avoids a breach on every line. Ported as a rule; its search is exact (a
  lean sweep that only asks "is HOME touched"; with HOME at 2 or 3 it is 0 at once).

Intensities: LOW +6 Heat, income x0.5; NORMAL +12, x1; HOT +18, x1.5 (income = sum of v // 3 over OK, non-dark assets, rounded
down). **Leg score** = bank + assets kept - HOME lost x 8 - Heat carried; a breach has no leg score (the campaign is lost).
**Tiers**: EVADED lime (acid), HOLDS neutral, BATTERED amber, DAMAGED orange, BREACHED red.

## How to play

The leg is golden leg 0 (`--leg=N` for 3, 5, 8, 11, 14). The corp's real sealed line is seeded per raid; the player sees three
candidates (a different shape on each) and learns which was real only at the reveal.

1. **Contact.** The raid's strength by Heat band, the chain Heat -> line 50 -> line 75 -> beams, the network counts, what the run
   between raids did, the kit tray. DOWN assets say how many raids they have stayed down ("down 2 raids", amber from 2).
2. **Plan.** Levers (keys 1 2 3, then click a node; click a placed lever or Z to take it off). Each lever draws its effect. The
   hunter's rule is a glyph: a dashed column with down chevrons and an arrow that comes in over the first touch and **ends on the
   column** (a quarter turn; the column may be shifted a few pixels to stay clear of another line, the arrow follows it). When
   nothing is touched the hunter runs its own line, drawn as a ring on a pin above its column, no word. A red **BREACH warning**
   above the grid when every sealed line empties HOME even with the best response; it names the fewest levers that clear it.
3. **Forecast** (Enter). Per sealed line (triangle, square, circle): the result if you hold, the best a spoof can do (a range, no
   node named), and the nodes **or JAM** that could save (small circles, a struck-chevron mark for JAM).
4. **Playout**, hands-off: beam 1, the known extras, beam 2 unseals, then **the response screen**, beam 2, the hunter turns (not
   when jammed), the hunter beam. Speed 1x/2x/4x (keys 1 2 4), SKIP (S) stops at the response screen.
   - **The response screen** (when the kit holds a spoof) lists HOLD, every SKIP target and JAM side by side. Each row shows the
     result (DOWN, TAKEN, HOME, BREACH chips) and **the Heat after, +2 included**: "Heat 49 -> 51 (spoof +2) crosses 50: +1 beam"
     (or "evaded -10", or "under 75 again"). Nothing is highlighted as best. The grid previews the row under the pointer; on
     JAM it draws the hunter's column and turn it would take **struck out** with a red X. Click a row or a lit node; H holds,
     J jams.
   - With no spoof in the kit the screen is skipped, but not silently: a "no spoof left" beat (struck spoof key, 0.9 s) shows.
   - After JAM the track shows beam 3 struck out and a "JAM: the hunter does not run" chip sits on the grid.
   - A touch that empties HOME ends the sweep at that touch ("HOME BREACHED"); no response follows, the spoof stays in the kit.
5. **Aftermath.** The tier stamp, node tags, the ledger (kit before -> after, Heat before / ghost / evaded / **spoof (SKIP|JAM)
   +2** / after, HOME, network counts, assets kept, the leg value rebuilt from the numbers).
6. **Between raids** (one screen): 1 **REPAIRS, 1 crew: pick one** (click a DOWN asset; a second click moves the pick, "N stay
   DOWN" is said); 2 one shop buy; 3 run intensity. **Every intensity card shows the next raid's breach risk**, live as the repair
   and the buy change: red "BREACH on k/3 lines" with "whatever you pick" (k = 3, same on all three cards) or "even with the best
   plan"; amber "safe with levers" (a plan is needed: "no lever: n/3 breach"); lime "safe". The ledger shows Schematics next to Heat.
7. **Leg record.** Raid by raid: tier, Heat, beams, a mini map (ring = changed in this raid), what changed, kit used and the
   spoof kind with its Heat ("JAM  Heat +2"), the sealed line's shape, assets kept, the between step, and **the network after the
   raid (OK / DOWN / TAKEN)**; below the cards the score formula and **LEG END: n OK, n DOWN, n TAKEN**.

The HUD on every screen shows Heat, the raid pips, HOME integrity, the bank and ASSETS KEPT. Toggles (strip at the bottom, F1 F2):
SPOOF HINTS (RANGE / OFF), CURRENCY label. **The scramble** (`--scramble`) replaces each word by seeded random letters of the
same length (digits, glyphs and case stay), for the no-words test.

## What is ported

| GDScript | Python (`tools/raid_concepts/sweep_l5.py`, `sweep_l4.py`, `sweep_l2.py`) |
| --- | --- |
| `l5_rules.gd` (`L5Rules.sweep`, `resolve`, `between` / `between_parts`, `score`, `tier`, `responses`, `allocations`, `breach_risk` / `breach_lines`, `naive_decide`, `naive_repairs`) | `sweep` (JAM), `resolve` (SPOOF_HEAT), `between` (REPAIR_SLOTS), `score`, `tier`, `spoof_options`, `allocations`, `breach_risk`, `naive_leg`; the lab's own forecast `spoof_options` re-uses `resolve` per response |
| `l5_state.gd`, `l5_config.gd` | `State`, the constants of the files (checked against the golden `config`) |
| `l5_data.gd` | loads `data/l5_golden.json` (`tools/raid_concepts/l5_golden.py`): the legs with each raid's `real` and `shapes`, spoof `null` / `[x, y]` / `"JAM"`, `risk` per intensity on every between step |
| `l5_model.gd`, `l5_play.gd` | lab state (plan, undo, kit tray, forecast, worst case, breach warning, between picks with one repair slot, DOWN age, cached `risk_for`) and the playout state machine with the response options; they only call the rules |

The view is `raid_lab_m10.gd` (the 2D overlay: `_draw()` over the 3D board of `l7_board.gd`; projection `l7_cam.gd`, effect helpers `l7_draw.gd`, cues `l7_fx.gd`, timings `l7_config.gd`; glyphs, fonts and the scramble in `l5_glyphs.gd`). Deterministic
`RefCounted` rules, no randomness anywhere in the lab.

## Parity status: PASS

`parity_check.gd` (exit non-zero on any mismatch): the config constants (incl. SPOOF_HEAT, REPAIR_SLOTS, JAM); every step of the
planned, greedy and naive line of the 6 golden legs (18 lines, 54 steps: state before incl. kit, touches, tier, state after the
raid, the between step, state after, score, the lab's naive policy reproducing the naive line) **including the `risk` of every
intensity at every between step (breach_risk recomputed from the between state)**; each raid's `real` and `shapes`; the re-drawn
sealed lines (distinct, non-empty, pairwise different asset / HOME hit sets) in all 18 raids; all 200 random single-raid
resolutions (21 with JAM) and all 200 random between steps, with the 40 random `risk` values; every golden allocation passes the
lab's lever validation. Result (L7, unchanged from L6): 2433 checks, 148 breach_risk values, 0 failed, `PARITY PASS`, exit 0. Log:
`D:/rc_tmp/raid_design_lab/lab_l7/parity_final.log`.

`flow_check.gd`: PASS, 904 checks (log `D:/rc_tmp/raid_design_lab/lab_l7/flow_final.log`; the L6 and L7 checks are listed above; L6 had 734): kit and caps, undo, heat bands, the
forecast (JAM among the responses that save), the response rules (HOLD +0 Heat, SKIP and JAM +2 and one spoof, JAM removes exactly
the hunter's touches and beam), **the decision screen's forecast equals the result for every option** (a fresh playout of each
option gives the same touches, state, Heat after, summary, Heat-line crossings, and only JAM drops the hunter), the "no spoof
left" beat, the tiers, the seeded real line and shapes, the between step (one repair slot: a second pick moves the pick, the rules
ignore a second repair; budget, buy, intensity, refusals), the planned lines of legs 0, 3, 5 and 11 played through the model
against the golden (JAM raids included; ledger reconciles with the spoof Heat; the kit is conserved; DOWN age; the risk on each
card = `breach_risk` = golden), the naive line on all 6 legs ending as the golden (**breach on legs 0 and 8 only**; at the between
step after raid 2 every card says BREACH on 3/3 lines on legs 0 and 8), the breach warning, and the scene driven through its own
input path (a planned raid with the between screen and the risk cards, a JAM raid, a full naive breach leg to the record).

The headless flow check does not draw (no renderer); every `_draw` path is exercised by the windowed captures, whose logs are
scanned for script errors (0).

## Findings (rules ambiguities) and known gaps

L6 gaps:

- The kit strip's "next raid" beam count assumes the cheapest run (LOW, +6 Heat) and no evade credit; the real next raid can have
  more beams (a hotter run) or fewer (an untouched sweep gives -10). It is a floor, labeled with the Heat the plan leaves.
- "Settled" reads `breach_risk` 3/3 on all three intensity cards with the picks so far. A shop buy that changes the kit can unsettle
  it, which is correct (the banner follows the picks), but the fast raid is only offered when it is settled at Launch.
- The sealed-outcome pills share a row with the beam lanes: on a row with four or more lines they sit tight and can touch a beam
  badge. Hunter-lane pills below the node can touch the next row's node tag on the last column.
- The scramble leaves the digits and the "+" / "-" signs; node value, Heat notches, dark and the sealed outcomes read without words,
  but the response rows' "-1" and the Heat arrows still carry numbers.
- Speed and SKIP controls are hidden during the fast breach (it has no pacing choice).

- **The naive breach is settled after raid 2 on legs 0 and 8** (risk 3 on every intensity card; the warning before launch says "No
  lever left in the kit avoids it"). Leg 5's naive line no longer breaches at all (its between risk is 0). The cards say "BREACH
  on 3/3 lines whatever you pick", honestly: no intensity, repair or buy changes it, only the earlier raids could have.
- `breach_risk` counts only the sealed lines (hold, each SKIP and JAM all breach). It does not weigh the Heat the run adds later,
  and it is per raid: a "safe" next raid says nothing about the raid after it. The cards read the next raid only.
- "safe with levers" is the lab's reading of `breach_risk == 0` while the empty plan (no lever at all) still breaches on some line.
  The python has no such split; it is `breach_lines(empty plan)` in the lab.
- A SKIP that merely drops a repeated decoy touch costs +2 Heat and saves nothing; the decision rows show that honestly (same
  chips, more Heat), and the forecast does not list it as a node that saves.
- JAM changes nothing before beam 3, so the first touch (and the hunter column it would have used) is the hold result's; the
  struck-out column on the response screen is drawn from the hold resolution.
- The planned lines use JAM on legs 3, 5 and 11 (one raid each) and SKIP elsewhere; leg 0 never jams, so a critic who only plays leg 0
  does not meet JAM unless they choose it. `--leg=3` shows it in the first raid.
- Python resolves the whole sweep even after HOME hits 0; the lab cuts the playout at the HOME touch (the rules result, score
  sentinel and kit are unchanged). A golden naive breach step that records a spoof use is not reproduced in the kit when HOME falls
  before beam 2; nothing after a breach reads the kit.
- Python `between` silently skips a repair or buy the bank cannot pay; the lab refuses the pick with the reason, same result. With
  one slot the lab also moves the pick when a second asset is clicked (python just ignores repairs past the first).
- Three known beams (Heat 75 and up) still crowd the grid: badges are nudged apart but the hunter's `3` badge can sit on a node
  glyph, and the decision-row preview of a column shares that crowding. Heat is never capped; the meter is drawn to 100.
- The "down N raids" label sits top-left of the node; on a crowded grid it can overlap a start badge of a known beam.
- Vector glyphs (no art-pass assets), no sound, no save, no text scale or gamepad (out of
  scope).
