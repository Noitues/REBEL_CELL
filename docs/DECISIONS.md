# Decision Log

Append new entries at the top of the relevant section. Never delete entries; mark them
superseded instead.

## Locked design decisions (v0.9)
- Wheel is 30 ticks / 6 slices / 5 ticks per slice (was 24). Enables a true centre tick.
- No Miss precision tier; "Miss" means the Miss slice only.
- Enemy jitter replaced by spin resistance (passive trait or Hub-sourced). Flip and
  Respin are blocked while resistance > 0.
- Flip mirrors the wheel across the horizontal axis (opposite slice to the pointer).
- Triggering: every pointer triggers its slice on End Turn. Pointer attacks hit every
  pointer of the target wheel. Satellites act as bodyguards.
- Resolution order: defensive → offensive → statuses, simultaneous.
- Three-layer progression: netrun / campaign / profile. Class unlocks are profile-level.
- Rank (runs survived) replaces veterans/Trace: wheel upgrades, netrun tier access,
  station bonus scaling. Survivors keep everything; difficulty scales to match.
- Heat is one campaign meter. Threshold events fire once; modifiers apply while at/above.
- City Grid is one shared map for netruns, territory and raids; cleared Sites are used up
  and become claimable.
- Armory (cap 6) + persistent deployed assets resolves the audit's persistence question.
- Mainframe gate: minimum 3 Exploits (Intel, Breach, Virus); extras weaken the boss.
- Story paths: 5–6 per corporation, hidden and random; beats unlock in Exploit order.
- REBEL_CELL (the handler AI) is the final unlock corporation at ICE 10 on all others.
- ICE difficulty: 20 cumulative levels, ICE 5 is the average-player tuning target.
- ~~Visual baseline: three worlds (cyberdeck / wireframe / zine), Cell colour hot pink.~~
  **Superseded** by "2026-10-05 — Designer rulings: art reintegration, pause point 0", ruling 4:
  the baseline is ART_BIBLE v2 (cel-shaded low-poly city with ink lines, CRT screens with white
  glyphs, vinyl stickers, grease pencil, light spill; GDD 9.1). Cell colour stays hot pink.
- Full voice acting; fully solvable combat preview; rewind with checkpoints at random
  events.

## Implementation decisions
### 2026-10-05 — FIX-REDS (M14): known full-tier reds and the boss HP plate overlap
- `test_anim_r6_rules::test_no_tween_shape_is_written_inline`: the Central Server gate's BREACH tween
  (`central_server_gate.gd`) wrote `Tween.EASE_OUT` / `TRANS_SINE` as a fallback for a missing entry; it now
  sets ease and trans only from its `gate_breach_ready` entry (a required id, so it is always there).
- `test_anim_r6_rules::test_every_script_that_animates_registers_or_says_why_not`: `CityView3D` (ART-5 5e's
  Cell blackout reveal, `cell_fist_reveal`) now joins MotionSkip as a short motion (`register_passive`, as
  `rubber_stamp.gd`): `motion_running()` while the reveal plays, `complete_motion()` shows the fist at once.
- The boss HP plate (timeline row 19_art2): the "guard-arc marker" over "895/1475" in phase 2 was the boss's
  second blade (Renewal Engine phase 2 adds a needle at tick 15, straight down): the D4 blade reaches 96 master
  units past the frame, onto the HP number. Following the art pass (M13 W3, `hp_layout`: "under the arc and under
  every needle's reach; a multi-needle boss never sweeps a needle over its HP"), the HP row now sits under the
  lowest blade of the state's needles (`WheelView.needle_floor`, `NEEDLE_HP_GAP` 4 px) and the disc's vertical fit
  keeps that room (`_fit_radius` / `_below_need`; a wheel with no needle pointing down lays out exactly as
  before). The state's needles, not the animated ones, so the row and the disc hold still while a needle
  migrates. Test: `test_art2_wheel_stack::test_no_needle_covers_the_hp_number_at_every_text_scale` (a second
  needle at every tick, both wheels, 1.0 / 1.6 / 2.0: no blade box meets the HP number, which stays on screen).
  Checked windowed: `arena_lab --corp=solace --boss --fixture=worst --phase=2 --scales=1.0,1.6,2.0` (the lab
  gains `--phase=N` and `--scales=` for one launch over the three scales).

### 2026-10-05 — Designer ruling: the M14 audit is a side-by-side art-pass parity audit
Designer (Noitues), 2026-10-05 evening: "I want my main to look just like art pass."
- The M14 audit is no longer the vertical / horizontal / naive code audit over the stored reports. It is a visual
  parity audit: every screen and state captured on the art pass (run from a scratch copy of the `art-pass` branch,
  never written to) and on main under identical conditions (size, text scale, seed, state), shown side by side, with a
  ranked list of every visible difference (layout, colour, type, materials, assets, motion) and the fix that makes main
  match. Fix agents close the gaps; re-capture and repeat until the pairs match.
- Where the art pass has no runnable screen for a state, the approved concept image (tag `art-concepts-r43`) is the
  reference. Mechanics the rules lack (G1–G16) are still not built: a difference that needs one is listed, not built.
- The old audit agents and `docs/handoff/m14_audit/` stored reports are not inputs to this effort.
- The full-suite run in isolation, fixes to green and the CI re-enable stay after it.
- **Amended the same evening (designer):** some art-pass looks are off or not better than main, so every difference
  the audit finds goes to the designer for a comment and a decision (match the art pass / keep main / something else)
  before any fix. This replaces "the art pass design is correct, follow it without asking" for parity work. Bug fixes
  that are not a look choice (test reds, overlaps) still go ahead.

### 2026-10-05 — Parity fix — TITLE-01 title backdrop (designer decision)
Designer decision 2026-10-05: the title follows concept round 33 (`round33_ui_chrome/title_screen.png` / `.gif`,
art-concepts-r43). Audit item TITLE-01 (P1, `docs/art_review/PARITY/GAPS.md`): main's title drew the 2D NeonCity
line-art city, unblurred and saturated, under a flat 0.58 dim.
- **The real 3D city.** New `BlurredCityBackdrop` (`scripts/ui/kit/blurred_city_backdrop.gd`): its own `CityView3D`
  (the unified city of the Grid / raid / netrun, 5a; band held at GRID: solid buildings, the full city life) with 5c's
  `CityViewMotion` (traffic, sky lanes, lights), a fixed camera with the corp's HQ landmark at a screen anchor, night
  look, drawn under a tilt-shift + darkening ColorRect (`shaders/city/city_tilt_shift.gdshader`: reads the screen like
  `glass_blur`, with glass_blur's two-ring mip kernel for the soft copy, mixed with the sharp one by the focus band).
- **The concept's own numbers** (round 33 `title.py` `backdrop()`, art-concepts-r43 dcfdf74, ported, not re-tuned):
  Gaussian 5 px at 1080 for the soft copy; sharp band centre 0.56, half 0.36, power 0.8; menu-side darkening 0.62
  fading over 900 / 1920 of the width at power 1.4; foot 0.35 from 0.82 down; vignette 0.35 round (0.6, 0.5) scaled
  (1.3, 1.1); gain 0.86. They live in a new read-only `CityBackdropLook` resource (`scripts/city3d/city_backdrop_look.gd`,
  not under scripts/data: no smoke check) — the title's is `content/config/title_city_backdrop.tres` — together with
  the tiers (`city_tiers` [false, true, true], as D17's `backdrop_city_tiers`), the framing (ortho 300 BU, the HQ's
  point 20 BU up its lot's centre at (0.86, 0.64) of the view: the ziggurat's eye lands where the concept's does) and
  `focus_at` / `field_at`, the shader's maths in GDScript for the tests. A reusable piece: LOOT-04's loot / event /
  shop overlays can take it with their own look and one call if the designer rules that way (not switched here).
- **Which HQ:** the last-played campaign's target (`corp_of_slot(continue_slot)`: the slot the Continue line offers,
  else RunManager.latest_slot), else **Halcyon** (`default_corp`, the concept's ziggurat). The Cell and a corp with no
  HQ on the city fall back to Halcyon too.
- **Fallback.** `CyberdeckBackground.use_blurred_city(look, corp)` swaps it in only where the look's city quality tier
  takes the 3D city and a renderer is there (tier 0 and headless keep the 2D NeonCity and CITY_DIM, as D17 keeps its
  stills) and none of the title's 2D design-review args (`--demo-overview`, `--demo-district=` ...) is given. The 2D
  city stays in the tree (hidden, process off) for the title's references. Only the title calls it: the HQ, the
  netrun / HQ warm-ups and the labs are unchanged. `title_scene.gd`: three backdrop lines (the look, the call, the
  dim hidden over the 3D city, which darkens itself).
- **Motion.** The city fades in over the night sky when its model is in with the existing `city_bake_fade` (the 2D
  bake's arrival; T0), MotionSkip passive; the title's own entries (sign, glitch, ticker) are untouched. Reduce
  effects / reduce motion: a still frame (the city renders once, then holds; again on a resize).
- **Measured** (windowed, `tools/city/title_backdrop_capture.tscn`, 1920x1080, v-sync off as city_lab): tier 2 frame
  3.31 ms avg / 5.20 max, backdrop city GPU 2.31 ms, rest of the title 0.46 ms; tier 1 3.22 / 5.16, city 1.80 ms.
  Under the 8 ms city budget.
- **Tests:** new `tests/unit/test_parity_title01_backdrop.gd` (fast): tiers 1–2 take the 3D city, tier 0 / no renderer
  / a 2D design-review arg keep the 2D city; the title asks for it and keeps its 2D fallback and dim headless; only the
  title calls `use_blurred_city` and a plain CyberdeckBackground is as before; the corp choice; the camera puts the HQ
  on the anchor; the darkening equals `title.py`'s; the arrival's entry, MotionSkip and the still frame; legibility:
  the verb chips' words and every MORE / PROFILE label reach 4.5:1 on their glass over pure white darkened by the
  backdrop (3D field and 2D dim), the verb stickers' two-tone edge (white die-cut, VINYL_INK rim) 3:1. No test dropped.
- **Review:** `docs/art_review/PARITY/fixes/TITLE-01.jpg` (before / after / concept; text 1.6, 2.0; tier 1; reduce
  effects; tier 0 fallback). Remaining difference from the concept: its city (round 26's 2D render) shows more
  saturated pink street light and a little more haze than the 3D city's night grade; the framing, blur and darkening
  match. Changing the city's grade would change the Grid too, so it is left for the designer.

### 2026-10-05 — Art direction — ART-3 6w raid on the city
ART-3 wave 2b, ART-6 on the unified city (ART_BIBLE v2 §4.1, §4.8, Appendix C #13, plan G10; refs round 40
`raid_view_v3`, `raid_gifs/`, `unified40.py` "the Cell's nodes: uplink pads + risers"). Builds on 3A's raid 2D
presentation and 5e's live Grid.
- **The raid's pages on CityView3D at the RAID band.** The setup, the playout and the report
  (`hq_scene.RAID_CITY_PAGES`) turn the unified 3D city on through 7w's `WireframeBackground.use_city3d(on, band)`
  holding `CityLod.Band.RAID` (see-through buildings at any zoom, management lane glow, 5c's motion via 5e's
  CityViewMotion); the Grid keeps GRID. The overlay's projection is the city camera's (5a), so 3A's sockets, pencil
  routes, state marks, vehicle icons, beacons and drag pencil all follow the city camera through `RaidMapAnchor`
  unchanged; its network goes to the city's ground decal (lime links through buildings). Picking, the drag model
  and the raid verdict are unchanged (views only).
- **Raid zoom fit (G10, Appendix C #13): `RaidZoomFit`** (pure, `scripts/city3d/`). The setup frames its network
  (the map's nodes: the Cell's, the entry Sites and the Sites the threats cross) plus `raid_fit_margin` (40 BU)
  inside the map's free part once per layout, then 3A's framing passes only correct it; the furthest out is now
  `raid_fit_max`'s zoom (was RAID_MIN_ZOOM 0.45 on the 2D city). **Call: `raid_fit_max` 380 -> 640.** Round 39's
  380 framed the x1 layout; 5e's x2 Site spread doubles the network, which needs ~490-570 on the setup's map part
  at text 1.0 (measured: Halcyon 491, Solace 565, Meridian 566). The playout's camera stays in the raid range too
  (`playout_zoom` = `raid_fit_min`'s 220, a framed fight no wider than 640): the 2D city's PLAYOUT_ZOOM 1.9 /
  PLAYOUT_MIN_ZOOM 1.2 were ortho ~84 / ~133 on the 3D city, the netrun transit's band. The fight framing
  (`WireframeBackground.frame_points`) measures the network with the city's own ground step (3D: TILE_A x sin 40°).
- **Building nodes as uplink pads (reuse rule).** `tools/art_pipeline/raid/build_uplink_pads_v1.py` runs the round 40
  concept's own lines in Blender 5.2 (`unified40.py` 420-428, the pad: dark slab, lime trim, mast with its lime cap;
  430-433, the riser: three lime traces up the corner facing the socket; vendored unchanged by 5e in
  `tools/art_pipeline/city/concept_r40/`, ported from art-pass ace98b9, on concept_r31's `target_corps.py`) on a
  stand-in footprint (pad half-size 1 BU at roof 0; riser 10 BU) and exports `assets/raid/uplink/uplink_pads.glb`
  (+ art_export/1 manifest; 5e's lm_toon / lm_neon roles, drawn in the landmark materials). `RaidUplinkPads.of`
  places them by the concept's rule on each of the Cell's nodes (the map's lot): the tallest prism over the lot,
  half-size `uplink_pad_share` (0.32) x its roof's shorter side, roofs under `uplink_min_top` (3 BU) carry none, the
  riser on the footprint corner nearest the node's street door (`CityMapOverlay.street_door`), scaled to the roof.
  `CityView3D.set_uplink_pads` draws them in the props layer (shadows off); they go with the raid's map.
  **Calls:** (1) a tapered roof keeps its pad, shrunk with the roof (the concept skipped tapered buildings and took
  the nearest flat one within 1.9 lots; the game's socket stands over its own lot's roof, so the pad stays under
  it); (2) the socket keeps floating over its roof (3A's overlay placement, label avoidance and fits) rather than
  moving onto the street as the concept's circuit inlay: the pad on the roof under it is "the socket's twin"; (3) a
  node's pad stays through the playout (a TAKEN node's socket burns; the building keeps its pad until the map goes).
- **The 3D picture covers a held frame.** A zoom-in camera ease (setup -> playout, fight to fight) shows the held frame
  by shrinking the picture through the camera rig; the 2D city's bake reached past the control, the 3D city stopped
  at its edge and the sky showed round it. `NeonCity.view_cover` (set by the rig while it holds a frame, cleared at
  rest) grows the 3D viewport and its camera to cover the screen, at most `COVER_MAX` (3) times the control (a file
  of 5a's, smallest change; the overlays' projection is untouched).
- **Raid setup fixes (orchestrator):** (1) the SAVED stamp could land on the greyed SKIP of the Speed / Skip strip
  (3A's note): `Fx.avoid_rects` keeps off `RaidSpeedStrip` (its keys are drawn, not buttons; `scripts/autoload/fx.gd`,
  one condition). (2) At text 2.0 the third defence card wrapped under the side column's view (3A pinned START at its
  foot): `hq_scene._fit_card_row` lets the cards share one row, each as wide as the row allows down to
  `CARD_ROW_MIN_SHARE` (0.8) of its size (fixes `test_horizontal_pass22_screens::test_defence_cards_are_on_screen...`).
- **Tools.** `tools/design_lab/raid_lab.tscn` waits for the 3D city's chunks, prints the raid ortho and the pads, and
  gains the `uplink_close` state (ortho 90 on the largest pad).
- **Tests.** New `tests/unit/test_art3_6w_raid_city.gd` (fast): the zoom fit and its clamp; the raid pages on the 3D
  city at the RAID band, fitted, nodes in the free part, pads on the Cell's nodes only, the playout in the raid
  range, the Grid back on GRID; the pads (the concept's export, its rule, the riser's corner, deterministic); the
  picture's cover and its cap; SAVED keeps off the strip. Changed (behaviour kept): `test_anim_r6_city`
  `test_your_nodes_fills_its_window_and_counts_the_withdraw_row` accepts the side column's MORE BELOW when YOUR
  NETWORK's own tag sits outside the column's view (3A's `ScrollHint.in_outer_views` hides it there).
- **Dependency on 5e:** the x2 spread (the clamp call above), CityViewMotion on every 3D NeonCity, the vendored
  concept_r40 / concept_r31 sources and the landmark material roles for the pads.

### 2026-10-05 — Art direction — ART-6 3A raid presentation
Group 3 wave 1, ART-6's 2D parts (ART_BIBLE v2 §1.2, §4.8; rulings 6.2 words and 11 DOWN), on
the **current** raid map (wave 2 moves it onto 1D's real-time unified city). Generator recipes
ported from art-concepts-r43 rounds 19-23 (`ui19-ui22`, `netdecal21`, `icons22`). Captured
windowed with `tools/design_lab/raid_lab.tscn` (one launch walks the kit sheet, the setup for
every corp, the drag valid / refused, a pencil mark in its hold, the playout's end, the report and
BREACHED); crops in `docs/art_review/ART-6/3A/`.
1. **Panels by fiction** on 1B's materials: RAID INCOMING = the raiding corp's intercepted WORK
   ORDER (`RaidPaper` over `CorpPaperPanel`: letterhead, the corp seal, division line, Courier
   fields, redactions, clip, INTERCEPTED) with the Cell's forecast stamp on it; YOUR NETWORK =
   the Cell's CRT (`RaidTerminal` over `CrtTerminalPanel`) with a socket glyph and a status
   chip per node (`RaidChip`: HOLDS green, DOWN amber, TAKEN red, always the word); THREAT
   INTEL = decrypted holo (`RaidHolo` over `DecryptedHoloPanel`, a local scrim, not the modal
   one) with a row per entry route (A, B, C), the units entering there, their routing rule, and
   the scanned v4 icons; panels re-skin per raiding corp (`RaidSkin`: hue, ink, seal crest,
   letterhead line, order number); START DEFENSE is a vinyl sticker (`RaidSticker` over
   `VinylSticker`) with the Speed / Skip terminal strip under it (greyed in setup); in the
   playout START peels away (1B's `sticker_peel`) and the live strip is the feed's foot.
   THREAT INTEL sits beside the loadout under the map at text scale 1.0 (the reference's
   bottom left), listing at most three entry routes (A, B, C; the rest as a count); above 1.0
   it joins the side column. The side column now scrolls at every text scale (the paper and
   the terminals are taller than the old badges; MORE BELOW says so), YOUR NETWORK keeping a
   150 px view of its own there; the go row wraps and the Speed / Skip strip's STEP readout
   shows only when the column has room, so nothing widens the page.
2. **Node status and health v2** (`RaidSocket`): an isometric chip socket with pins and the
   pin-1 notch, the type glyph (no tags), holds green / CORE pink; only the inner fill drains
   north to south with a hatch and a drain line, the outline and glyph stay lit; DOWN = the
   Site markers' white bolt over a greyed socket (ruling 11); TAKEN = a burnt socket with
   embers once its pencil mark has wiped; the setup's projected outcome is a dashed outer
   ring (DOWN amber, TAKEN red). Sockets drain and fall live in the playout
   (`CityMapOverlay.socket_live` from `RaidFxLayer.socket_state`). The node glyphs are vector
   stand-ins: 1C's atlas has no node-type glyphs yet.
3. **Grease pencil on 1B** (`GreasePencilMark` / `GreasePencilWord` through `RaidPencilPool`,
   on a scene CanvasLayer at 95, above every UI layer the raid shows and under Fx's jack cover,
   so PencilLint's rules hold): the threat routes in red along the real streets, snapped onto
   them (`PencilShapes.snap_to`), are the **projection's own routes** (each threat's entry and
   moves: preview equals result) with A/B/C circles at their entries; they write on
   (`raid_route_write`) and cloth-wipe at the verdict (`raid_route_wipe`). State marks: INCOMING
   once per entry Site, DOWN over its node, TAKEN v2 above its node, each written ~0.4 s, held
   1.5 s, wiped ~0.4 s **in real time** from its beat (`raid_mark_write` / `raid_mark_hold` /
   `raid_mark_wipe`: never shortened at 2x / 4x, longer below 1x; the hold keeps its time
   under reduce effects, write and wipe are instant); BREACHED is one slow heavy pass
   (`raid_breached_write`) with its underline, a red bit burst at CORE and CORE's links going
   dark from CORE outward (`raid_bits_burst`); home's verdict is pencil (the loss red, HOLDS
   yellow) and every node that holds gets a yellow tick. Every mark is anchored through one
   seam, `RaidMapAnchor` (Site, street, zoom), for wave 2's projection.
4. **Card drag** (`RaidDragPencil` over the DropLayer): the card peels and parks above its
   slot as a vinyl sticker, a yellow pencil arrow runs to the pointer, the dock circle draws
   round the node in reach (yellow; red + X where the rules refuse) with the IF PLACED terminal
   (the defence, the node's outcome and HOME before > after, from the rules on a copy of the
   campaign) or NO SLOT and the rules' reason. The DropLayer still does every drop (ANIM-4's
   behaviour and tests unchanged); its pointer ghost hides while the sticker is parked.
   **Not done:** "remove = click the node" (a click on a node still picks the target; returning
   a defence is its Withdraw button or a drag to the loadout) — a behaviour change, see the
   open question below.
5. **Threats** (`RaidVehicle`, icons v4): shape = type from the rules (FAST moves 2 links a
   step, SPECIAL freezes or alters links, else HEAVY; FLYING has no rule and stays in
   docs/art_reference), fill = corp colour = health draining from the top (the threat's
   integrity is now on its `threat_enters` event, a view field; the core change is that one
   key), a dashed corp ring with status pips (frozen by ICE, slowed by a stationed Ghost),
   the yellow heading arrow on hover only. ICE encases a held threat (crystals growing inward,
   `raid_ice_grow`), a stationed Ghost lays its slow field under the units (`raid_slow_field`),
   a Rigger's repair raises the fill with rising "+" sparks (`raid_repair_rise`). R3 class
   beacons for stationed operatives are **not done** in wave 1 (they stand on the Safehouse's
   roof pad, a 3D city part: wave 2).
6. **The raid report** is the raiding corp's AFTER-ACTION REPORT (corp paper, CLASSIFIED):
   operation, units deployed / destroyed, equipment lost (the reward), Sites reclaimed, nodes
   disabled, the home server, the Heat (settled here), each node's before > after; the Cell's
   pencil on it (`RaidReportPencil`: "THEY LOST n" and "OURS! +n" circled in yellow, RIP by
   reclaimed Sites, a tick by an intact home); **CELL HOLDS** is slapped on (1B's
   `sticker_slap`) whenever the Cell survived the raid (GDD 7.2 "a survived raid ends CELL
   HOLDS"); the raid's one verdict (RaidVerdict) keeps its stamp on the table, so a raid that
   cost HOME -5 shows both CELL HOLDS and HOME -5. BACK TO THE GRID is a sticker.
- Motion: new entries (REQUIRED_IDS + lab demos): raid_mark_write / _hold / _wipe,
  raid_breached_write, raid_bits_burst, raid_slow_field, raid_ice_grow, raid_repair_rise,
  raid_route_write / _wipe, raid_dock_circle, raid_drag_arrow. Every one shows its end state
  under reduce effects and headless and ends with any press (MotionSkip passive); the hold is
  a reading time. No existing entry dropped (raid_flip, raid_result_banner and the others are
  still read for their timing).
- Tests: `tests/unit/test_art6_raid_presentation.gd` (routes = projection = the raid's own,
  marks name what the raid did and end at a skip, sockets fall, holds never shortened at
  2x / 4x, reduce effects = end state, IF PLACED = placing, the report's CELL HOLDS).
  Tests changed because they pinned the superseded look (behaviour kept): pass 21 reads the
  work order's title (RaidPaper), pass 24 reads the work order's fields as Labels, ANIM-R5 P8
  reads the report's value as a Label. No test dropped.
- Files outside 3A's area (smallest edits): `scripts/core/raid_resolver.gd` (`integrity` on
  `threat_enters`), `tools/design_lab/motion_lab.gd` (demos + raid kinds),
  `scripts/data/ui_motion_data.gd` / `content/config/ui_motion.tres` (union).
- **Designer correction (never redraw concept art) and M14 resume.** Everything above that was first
  drawn procedurally from the concept's recipes is now the concept's own art, baked by running its
  generator script on tag art-concepts-r43 unchanged (bake scripts in `tools/art_pipeline/raid/`, each
  with stand-in modules for the heavy kits and a black / white difference matte for alpha). This
  supersedes, above: "the node glyphs are vector stand-ins" (2) and "R3 class beacons are not done" (5).
  Raid visual sources:

  | Piece | Source | Asset |
  |---|---|---|
  | Threat vehicle icons v4 (shape, corp fill draining, ring) | concept `round22_raid_world/icons22.py` | `assets/raid/icons/` (320 PNG) |
  | Node sockets, health v2 fill, status key, YOUR NETWORK glyph marks | concept `netdecal19.Net.pad` + `netdecal21.Net.health_pad` | `assets/raid/sockets/` (7 glyphs x 10 looks) |
  | ICE freeze crystals | concept `ui22.ice` | `assets/raid/ice/` (8 growth steps) |
  | R3 class beacons (stationed operatives) | concept `screens21.beacon` | `assets/raid/beacons/` (8 strips x 16 frames) |
  | BREACHED bit burst (flash, shock ring, 0 / 1 bits) | concept `ui21.bit_burst`, called as `screens22` 26_home_breached | `assets/raid/bits/bits.png` (24 frames) |
  | Pencil routes, marks, entry circles and letters, TAKEN / BREACHED words | 1B kit (GreasePencilMark / Word, PencilShapes) | — |
  | START, CELL HOLDS, parked card | 1B kit (VinylSticker) | — |
  | YOUR NETWORK / RAID INCOMING / THREAT INTEL / report panels | 1B kit (CrtTerminalPanel, CorpPaperPanel, DecryptedHoloPanel) | — |
  | Procedural (they move, or no concept image) | DOWN bolt (ruling 11 addition); hover heading arrow (turns with the threat); slow field rings (drift inward, `fx_slow_v2` geometry); repair "+" sparks and streaks (rise, `fx_repair_v2`); CORE's links de-powering at BREACHED (follow the live links); drag pencil arrow and dock circle (follow the pointer) | — |

  Calls made: **Compiler Rack** has no concept glyph: it uses round 17's `picto_ram` (orchestrator:
  scheduled in the post-M14 glyph concept slice, see "Open questions"). **DOWN** is the concept's
  disabled socket greyed (`RaidSocket` tint) under the procedural white bolt. New palette token
  `Palette.RAID_SLOW_BLUE` (the slow field's blue; palette.gd is 1A's file, reported). The BREACHED
  burst plays frame = u x 24 of the strip, sized so the bake's radius (190 px) is `BITS_R` x screen_k,
  centred 10 bake px above CORE as screens22 draws it; the procedural 0 / 1 glyph loop is gone.
- **M14 resume fixes (2026-10-05):**
  - The fallen home server's label read "2 → 0 HOLDS" (the core keeps the home's outcome "holds"; the
    campaign is lost, the node is not taken): the map label, YOUR NETWORK's chip and the report row now
    say **BREACHED** (`hq_scene.shown_outcome`, view only; its tip says the campaign is lost).
  - START DEFENSE sat under MORE BELOW at text scale 1.0 (the scrolling column held the work order,
    YOUR NETWORK, then START): **START and the Speed / Skip strip are pinned at the column's foot**
    (`RaidFoot`, outside the scroll), so the page's action is on the first screen at 1.0 / 1.6 / 2.0.
    YOUR NETWORK's own MORE BELOW then drew over START (its list ran past the column's view):
    `ScrollHint.in_outer_views` hides a tag whose spot an outer scroll view clips (kit file, smallest
    change; the outer view's tag says there is more).
  - INCOMING overlapped an entry's pencil letter ("A"): a mark written above an entry now clears the
    letter (`RaidFxLayer.mark_centres`, `entry_letters` from the route layer); DOWN stays over its node.
  - 4C's audit P3 "the SAVED note on the raid setup is nearly invisible grey" (`Fx`, the autosave
    stamp): 14 → 20 px with a dark keyline (`SAVED_OUTLINE`, `SAVED_KEYLINE` = NIGHT_SKY 0.9), so the
    pink reads over any page and in greyscale. `scripts/autoload/fx.gd` is outside 3A (smallest change).
  - Tests: `test_breached_bits_are_the_concepts_baked_burst`, `test_a_fallen_home_reads_breached_not_holds`,
    `test_a_mark_above_an_entry_clears_its_letter` (test_art6_raid_presentation). Raid lab states added:
    `breached_bits` (mid burst), `saved_stamp`.

_(Claude Code: add entries here as you make them.)_

### 2026-10-05 — Art direction — ART-8 8w HQ runs on the city
ART_BIBLE v2 §3.14 (D17), §4.6, §4.7, §4.9; ART_3_BATCH "Wave 2b" 8w; references
`round34_rebel_cell/canyon_dispatch.jpg`, `round38_landing_exploits/central_server_gate.png`,
`exploit_items.png`; 8p's compounds; 5a's CityView3D; 5d's SiteWonLights.
- **DISPATCH's HQ run plays in the round 43 Tokyo canyon** (the open question 8p logged, resolved):
  `tools/art_pipeline/city/build_dispatch_canyon.py` runs round 34's own `hq34.py` chain (street34 /
  kit26 / cfg28 vendored unchanged in `vendor_r34/` from art-pass d14b8f6) in the DISPATCH state as a
  still, origin = the canyon's midpoint, placed on round 34's own canyon lots (`place_lot` 36.5, 36.5 in the
  manifest). It replaces 8p's rebel_base compound for rebel_cell. Text signs at curve resolution 2 (as 5b):
  2.67 MB, 78k triangles.
- **Canyon camera yaw 180 / pitch 40** (looking down the street toward its head, round 34's direction, at
  the city's own pitch so the sides read as rooftops); the corps keep the city azimuth at 55 degrees.
  `hq_compound_spec.py` carries per-layout yaw / pitch / snap / seek / builder / lot centre.
- **Canyon slots:** per layer the left rooftop, both pavement edges and the right rooftop (Sync Strike's
  three lanes); the right alley slot stands 8 BU further up the street (stagger, so the pair reads apart);
  rows at 10 / 28 / 46 / 64 / 80 / 100 BU along the street and a rooftop over a gap seeks a roof only toward
  the camera end (rows 82 + both-way seek put 5a / 6a 18 px and 5d / 6d 1 px apart: the validator's 50 px
  rule failed). DISPATCH CORE stands in the head crossing under the REBEL_CELL billboard.
- **Godot seams:** `HqCompoundStage` (pure: manifest, layout, place transform = the manifest's
  `place_lot` else the HQ lot's centre, world node points through HqCompoundLayout, footprint, camera from
  the manifest, `run_camera` widening the framing up to 2x only when a node or the entry falls outside);
  `HqCompoundMaterials` maps hq_toon / lit / neon / win / sign / beam onto LandmarkMaterials roles
  0 / 2 / 3 / 4 / 8 and the light cone (same corp tint); `CityView3D.stage_compound` / `unstage_compound`
  hide the corp's landmark (for the Cell its district: the canyon runs through it), give its cleared lot
  back, clear the compound's footprint and rebuild the chunks under both (landmarks are not placed while
  their compound is staged).
- **HQ-run page (HqRunView):** its own CityView3D framed on the compound; the run in the route's ink
  (RouteOverlay's stickers and state rings, walked lime line, live orange crawling dash, later white dash),
  the entry ring and the operative pin, and the Central Server as the rack sticker with the red pencil
  **TARGET** circle (bible 4.5's boss mark, not the server's name in pencil) and the yellow chip
  `CENTRAL SERVER // <Site name>` above the circle (below it when the server is at the top edge). The
  netrun page mounts it instead of the transit route when `run.kind == "boss"` (a few lines in
  `_show_map`; `_mount_hq_run`).
- **Central Server gate (CentralServerGate):** opened by the UI press paths only (`_request_node`: the map
  click and the ROUTE button); `enter_node` is unchanged so tests and tools reach the fight directly. The
  panel (EXPLOITS n/min, 3 sockets + 2 dashed extras, the footer), the boss WheelView from the new pure
  `NetrunSession.breach_preview()` (`_start_combat`'s setup factored into `_combat_setup`; the preview draws
  from a COPY of the combat stream, tested equal to the real start and leaving run, streams and campaign
  unchanged), the BREACH vinyl off -> on, Back to the compound. New motion entries `gate_keycard_stagger`,
  `gate_socket_ring`, `gate_breach_ready` (REQUIRED_IDS, lab "kit" demos); the cards reuse `sticker_slap`;
  MotionSkip one press; reduce effects / headless = end state; pad focus lands on BREACH (lime frame).
- **Keycards and the BREACH vinyl are the generator's art:** `tools/art_pipeline/hq_run/export_gate_assets.py`
  runs round 38 `exploits.py` unchanged on art-concepts-r43 (3082e99) -> `assets/hq_run/` (15 keycards at
  2x, breach_off / breach_on, manifest). The cards keep their baked English words (orchestrator's call;
  translation question below).
- **Names:** the Cell's Central Server is **DISPATCH CORE** (the concept's name; Site display name
  "DISPATCH" -> "DISPATCH CORE", its id `dispatch_core_site` already follows it; strings re-exported).
- **D17 on the city:** `BackdropCatalog.city_mode` / `city_shot`: per city quality tier
  (`CityConfig.backdrop_city_tiers`, default [false, true, true]) the combat backdrop is a CityView3D
  close-up drawn through the same `combat_backdrop.gdshader` (pools and bands unchanged): the corp's HQ for a
  boss (ortho 140, target 30 BU up), the staged DISPATCH canyon for the Cell's boss (the HQ-run camera at
  0.7x), the run's Site building for a regular fight (ortho 90; the nearest lot with a roof within 4 lots of
  the layout point). The still shows until the city's model is in and stays the tier-0 fallback. Won on the
  city: 5d's SiteWonLights on the Site building and the district dims outside an ellipse round the target
  (new shader uniforms `use_mask` / `keep_at` / `keep_radius`; the masked still path is unchanged).
  `BackdropCatalog.place` gained an optional `site` (the run's Site id). New CityConfig fields
  (`backdrop_*`, group "Combat backdrop"): CityConfig is not under scripts/data, no smoke check needed.
- **Measured (windowed, 1920x1080 window, `hq_run_lab`):** city GPU per view: HQ-run pages 3.8–5.9 ms, gate
  5.0–5.2 ms, backdrop close-ups tier 2 3.4–6.6 ms, tier 1 4.0–5.0 ms; all under the 8 ms city budget, so tier 1
  (Deck) keeps the city close-up and only tier 0 uses the stills. Frames held 16.7 ms (v-sync).
- **No tests dropped.** New: `tests/unit/test_hq_run_city.gd` (fast).
- **Files outside 8w's area (smallest change):** `scripts/ui/netrun_scene.gd` (`_show_map` hook,
  `_request_node`, gate open / close, `_clear_route`), `scripts/core/netrun_session.gd` (setup factored, preview),
  `scripts/ui/kit/materials/kit_demo.gd` and `tools/design_lab/motion_lab.gd` (gate demos),
  `scripts/city3d/city_view_3d.gd` (staging), `scripts/city3d/city_config.gd` (backdrop fields).

### 2026-10-05 — Art direction — ART-10 4C menus, title, settings, HQ
ART_BIBLE v2 §1.2, §1.3, §2.9–2.10, §4.13, §5.6; refs `menus/round33_ui_chrome/title_screen.jpg`,
`title_screen_alt_simulate.jpg`, `abandon_dialog.jpg`, `ui_kit.jpg`, `typography.jpg`,
`menus/round31_ui_chrome/settings_menu.jpg`. Built on 1A (palette v2, faces, theme) and 1B (material
kit) after both merged; generator scripts read on `art-concepts-r43` (round 33 `menu33.py`, `title.py`).
- **Chrome seam** `scripts/ui/kit/chrome/` (one class per file): `Chrome` (faces per medium, the
  terminal drawing helpers), `CrtWindow` (TerminalWindow's API, 1B's `CrtTerminalPanel` as its glass,
  a `> TITLE` header strip with tag chip and square marker, the foot bracket; `max_body` puts the body
  in a FitScroll), `CrtText` (terminal reference text: ZineNote's `label` / `append` / `make_reference`
  API, headings in terminal CAPS, prose in Plex), `VerbSticker` (a Button: PINK / YELLOW drawn by 1B's
  `VinylSticker` inside it; BLUE with the rebel-fist letter and GLITCH drawn by it with the kit's raster
  Anton; the lime die-cut halo on focus, never brackets), `MenuChip` (terminal button with a label
  and a line; `selected` = cyan fill), `CrtSwitch` (an Options row: name in CAPS, line in Plex, the
  ON / OFF pill with a visible OFF track; a CheckButton, so C's behaviour and tests are unchanged),
  `CrtTiles` (tiles fronting a hidden OptionButton), `HeatGlitchPreview`, `NeonSign`, `PencilPlan`,
  `PencilWords`, `OnAirTicker`, and `shaders/chrome/vinyl_sticker.gdshader` (the BLUE / GLITCH fill).
- **Concept art, not redrawn (designer correction 2026-10-05):** `tools/art/bake_menus_r33.py` runs
  the round 33 ui_chrome scripts from `art-concepts-r43` unchanged (only the font paths and the
  defaults that captured them are re-pointed at `assets/fonts`) and splits their output into
  `assets/ui/menus/`: the BREACH / SIMULATE / OVERTHROW stickers (rest, focus halo, BREACH's 12
  gloss-sweep frames, SIMULATE's two burst frames; `title.stk`, `menu33`), the yellow title stickers
  OPTIONS, PAUSED, CODEX, STATS, CAMPAIGN SLOTS, NEW CAMPAIGN (`ui31.sticker`, round 33 parameters),
  the REBEL_CELL sign per lit state of its 48-frame loop and its glow (`title.board` + `neon`), the
  pencil plan and NEVER SLEEP + crown (`ui31.Pencil`), the pill switches, slider handle, tab and tile
  plates and the title's chip plates (`ui31.toggle / slider / tabs / term_panel`, `settings.tiles`),
  the ON AIR block (`title.ticker`) and the Heat glitch preview frames (the round 18 storyboard,
  cropped as settings.py crops it). Stickers are at 2x the 1920 board (a third in the game), the
  rest at 1x (two thirds). The title's verb rows keep the concept's 112 px board pitch so the
  pencil numbers sit on them. **Every visual and its source:** sign, verb stickers, title stickers,
  plan, motto, switches, slider handle, tabs, tiles, chip plates, ON AIR, glitch preview = baked
  concept art (above). Drawn, with the reason: terminal windows (CrtWindow = 1B's CrtTerminalPanel
  glass, the coordinator's seam; its header, tag chip and square carry live, translated words), the
  MORE / PROFILE / Options / pause terminals (same), the chip and tile words, the ticker's crawl
  (live words), the codex / stats text, the HQ (no concept: G13 dropped the HQ room), the
  new-campaign page and its TRUST NO ONE pencil (no concept: §4.14 "new-campaign page" not
  designed), stickers for words the concept never drew (the kit's VinylSticker), the quit confirm (2D's
  ConfirmDialog). The abandon dialog's answer stickers are abandon.py's own (baked, below). The title's backdrop stays the live city (round 33 used pre-rendered city frames;
  the city is 1D / ART-5's), dimmed.
- **Title option A (D10, confirmed):** the REBEL_CELL neon tube sign on its circuit board (idle loop
  `title_sign_flicker`: underscore cursor, an E stutter, a two-frame drop to CELL); 1. BREACH (pink,
  default focus) = Continue with the slot line `slot // corp // run N // Heat H`; 2. SIMULATE (the
  CORRUPTED glitch inside the letters, bursts on frames 9–10 and 27–28 of 48, `title_glitch_burst`) =
  Tutorial; 3. OVERTHROW (blue, last O the red fist) = New campaign. DISABLE stays the Cell's motto
  (round 33 note 3). The grease-pencil plan numbers the stickers; NEVER SLEEP + crown in pencil; the
  MORE terminal (CAMPAIGN SLOTS [C], CODEX [X], STATS & ACHIEVEMENTS [S], OPTIONS [O], QUIT [ESC] — the
  keys work, pad Y opens the Codex, B / Esc backs out of a sub-page); PROFILE // THE CELL tags; the
  build line, pad prompts and the ON AIR ticker (`on_air_ticker`). The city is dimmed behind it.
  **Calls:** with no saved campaign BREACH is the grey disabled sticker and SIMULATE takes the focus;
  OVERTHROW starts a campaign in the first empty slot (the slots page when all three hold one); the
  stickers and their chips do the same action (the chip has no focus of its own; it lights with its
  sticker). Big text (≥ 1.6): MORE heads the right column, the chips drop their second line (it stays
  in the tooltip), the motto and the PROFILE panel give way (Stats shows the same tags).
- **Abandon dialog (resume, 2026-10-05):** `AbandonDialog` (kit/chrome) extends 2D's ConfirmDialog
  on its `HudDialogPanel`: `> CONFIRM // TITLE`, CANNOT UNDO + pip in HARM, the question, the body in
  Plex, the costs (terminal CAPS names, values beside them, two pairs a row), an optional Heat line in
  HARM and what stays in GAIN, the rule, then abandon.py's own stickers: yellow CANCEL (default focus,
  its lime die-cut halo) and the pink verb, tilted as abandon.py places them, each with its terminal
  caption (grey for the safe answer, pink for the verb). `tools/art/bake_menus_r33.py --only dialog`
  bakes `dialog_cancel`, `dialog_burn_it` and `dialog_delete` (rest + focus) with abandon.py's
  `ui31.sticker` parameters (DELETE with BURN IT's); a translated word falls back to the kit sticker.
  **Calls:** (1) there is no in-run abandon on main (the GDD has no voluntary abandon: building one is a
  mechanic), so the dialog serves the title's delete slot: `DELETE SLOT`, verb DELETE, costs TARGET /
  RUNS / HEAT / ICE from the slot, "Your stats and achievements stay." (the profile is its own file),
  captions "keep going [B]" / "erase slot N [A]"; `dialog_burn_it` is baked for when an abandon-run
  rule exists. The quit confirms (title, pause) stay 2D's ConfirmDialog. (2) The pad hold-A 0.8 s on
  the verb is a proposal in the bible (§4.13): not built (open question below). (3) The confirm
  re-centres as its panel takes its size (at 2.0 it ran off the bottom). (4) The title's page focus
  that lands when the page's enter motion ends no longer takes the focus from an open confirm
  (windowed, BREACH behind the scrim took it: CANCEL showed no halo). (5) Outside 4C, smallest edits:
  `confirm_dialog.gd` `_sticker` returns `Button` (AbandonDialog overrides it); `hud_dialog_panel.gd`
  draws its header words and tag on an unshaded Node2D child (the panel's CRT canvas shader sampled
  the MSDF font atlas raw: every dialog's header read dim and soft) and adds the tag's pip.
- **Title / pages fit (resume):** at 2.0 the verbs' chips are as wide as their labels and MORE's
  stats line reads STATS (its page's title; the tooltip names the achievements), so MORE clears the
  verbs; each MORE line keeps room for its key hint (`HINT_GAP`; the hint ran over STATS &
  ACHIEVEMENTS at 2.0); PROFILE sits above the pad prompts like MORE (`FOOT_GAP`; they overlapped at
  1.0); the title's terminal chips inset their words by the plate's baked glow (`MenuChip.CHIP_GLOW`:
  the words sat on the frame). Codex and stats texts share the page's room and scroll (`_flex`,
  `TEXT_FLOOR_H`), and from 1.6 the run history is a section of the records text (its own window did
  not fit over the ticker); slot rows keep `SLOT_ROW_GAP` for the focus brackets. The pause menu's
  PAUSED sticker sits over its header's right end (as OPTIONS does) so `> PAUSED` reads. The
  new-campaign setup is a form (`SetupForm`: names and their controls, two fields a row, one from 1.6)
  instead of one wrapping line.
- **Options (round 31):** `> TITLE // OPTIONS` or `> PAUSED // OPTIONS`, the yellow OPTIONS sticker,
  terminal tabs (LB / RB switch), Accessibility in two columns (EFFECTS & MOTION switches; TEXT SCALE
  slider with its value, ticks and live sample; colour-blind and resolve-speed tiles; the Heat glitch
  preview with ON / OFF frames and LIMITED under the flash limiter or reduce effects; HEAT GLITCH's row
  shows the LIMITED chip). Every row carries `UiFocus.META_NO_SCALE` (ART-0 carry-over: the pad focus
  scale moved full-width rows' words and put the brackets past the panel). Below text scale 1.5, and
  never inside the pause menu (`compact`), one column. **Call:** the reference's RESET TO DEFAULTS for
  every setting is not built (no such rule; the Controls section keeps its keybind reset); D13's
  "Always show all nodes" row is not on main yet (3B) — it takes a CrtSwitch row when it lands.
- **Pause, codex, stats, slots, new campaign:** yellow title stickers over v2 terminals; the codex and
  stats are terminal text (the zine note is a rejected medium); stats gain the profile tag grid; the
  pause lines are terminal CAPS menu items. The new-campaign page swaps the spray tag / scrawl
  (rejected) for its NEW CAMPAIGN sticker and TRUST NO ONE in pencil; its words say what they do
  (City seed, Next seed, ICE difficulty, with icons and tooltips; audit P3).
- **HQ (G13 not ruled: every action kept):** CYBERDECK, CELL STATUS, CITY GRID, CREW, BLACK MARKET, story,
  the Site card and RUNS OPEN NOW are CrtWindows; PIRATE RADIO is terminal text (the DJ is a voice on
  the Cell's feed); the dossier's name and fields are Courier Prime (corp paper). Raid parts (3A) and
  campaign end (4D) untouched. **Not done:** the crew dossier on 1B's `CorpPaperPanel` (it keeps its
  paper card with Courier Prime: the panel's letterhead / stamp slot would need the card's orders and
  HP strip re-laid; proposed slice) and JACK IN as a vinyl sticker (ZineStamp keeps `jack_ring_breathe`
  and its tests; a slice once 1B's sticker can breathe).
- **Audit (group1_naive) P2:** the top bar (HudStats, every screen) is terminal tags with names at the
  caption step, no colour-coded paper; Heat's value and icon in its band colour (§2.8); the Heat poster's
  number and bar in the band colour (ink on its paper for COOL). **Not done:** the Heat count-up vs the
  banner (P3, ART-5's poster timing; the banner names the threshold crossed, the number rolls on after
  it) and the raid setup's SAVED (Fx's stamp, 3A's screen: reported).
- **Motion:** new `title_glitch_burst`, `title_sign_flicker`, `on_air_ticker` (T0; REQUIRED_IDS; lab
  demos `screen title_glitch / title_sign / ticker`); the stickers use 1B's `sticker_hover` /
  `sticker_press`. Reduce effects, headless or an entry off: the sign holds lit, the glitch shows its
  light split, the ticker holds still, the stickers take their end states at once.
- **Tokens:** Palette gains STICKER_BLUE / STICKER_BLUE_LOW, NEON_TUBE / NEON_CORE, BOARD_* (smallest
  edit, reported). Fonts: the stickers and the sign draw from `VinylSticker.art_font()` (raster Anton:
  their outlines are wider than the MSDF field).
- **Merges:** the 1B merge resolved `ui_motion.tres` with the two-way tool, which kept 4C's copy of
  entries main had retuned; the Group 2 merge rebuilt the file as main's plus 4C's three entries, so
  main's tunings are back.
- **Tests:** `tests/unit/test_art10_menus.gd` (fast). Adapted (they pinned the M13 look the art
  replaces; behaviour kept): `test_visual_merge` pause menu = CrtWindow; `test_art0_kit_states` the
  confirm's scrim is a plain child behind it (still full screen, still takes the clicks);
  `test_horizontal_pass15` reads `window.body`; `test_horizontal_pass21_screens` the title profile is a
  caption + value grid (tooltips, never "none"), the MORE lines carry key hints instead of icons, the
  plan is the three stickers on screen at 2.0, the radio shows all its words; `test_horizontal_pass23
  / 24_screens` and `test_anim6_screen_motion` read PIRATE RADIO as CrtText, the plan's stickers are
  translated once, CONTINUE is a TerminalChip with the slot line (its tooltip at big text). No test
  dropped.

### 2026-10-05 — Art direction — ART-7 7w netrun on the city
ART-3 wave 2b (ART_BIBLE v2 §4.1, §4.6; round 38 `transit_v3` / `transit_step_v3`, round 40
`cars_lod`). The netrun route page moves onto the unified 3D city; node rooms are unchanged.
- **Transit v3 cables on the city's streets: `RouteCableRouter`** (pure, deterministic A* on a
  half-lot lattice): 45° / 90° turns only, streets crossed rather than ridden, crossings with
  cables already laid avoided, the rest bridged with a hop (the later cable hops). `RouteOverlay`
  routes every link in graph order plus the entry runs and draws each sticker -> ground lot ->
  run -> sticker; walked solid lime, live orange crawl, later white dash, cut grey. **Calls:**
  the router's costs (RIDE, TURN_45/90, CROSS, SHARE, END_FREE, HOP_END_SKIP, lattice and box
  sizes) are `RouteCableRouter` constants, not config: they shape a drawing, no rule or tuning
  reads them. The cables are the overlay's own, not the city's network decal (the route page
  clears the decal). `cable()` / `_axes()` stay as the 2D fallback.
- **The route page on CityView3D at the NETRUN band:** `WireframeBackground.use_city3d(on, band)`;
  the route page holds NETRUN and is see-through at any player zoom (bible §4.1 translucency
  rule; `CityView3D.view_lod`); GRID VIEW shows the whole Grid on the 3D city at the GRID band.
  **Other netrun pages (event, shop, loot, rooms) stay on the 2D city** until their own slices
  move them. The route page attaches 5c's `CityViewMotion` and the player's camera
  (`CityGridControls`, wheel zoom / drag; a view, no state).
- **CLOSE car tier at netrun close-ups** (answers 5c's open question 1): the transit keeps the
  sky-lane cars off at its fitted zoom (MEDIUM, bible §4.1) and shows the CLOSE cars once the
  player zooms the route below ortho 150 (`car_close_below`), as `cars_lod` shows (verified at
  ortho 60: wedge cars with tail lights and speed lines).
- **Fix: flat blue blocks over the route's city.** NeonCity's ANIM-R3 B4 bake stand-in
  silhouette (`CitySilhouette`, roof slabs lifted over every lot) stayed visible over the 3D city
  when a page turned the 3D city on after its first 2D frames. `NeonCity._sync_city3d` now hides
  it (a NeonCity file outside 7w's area; one guarded line). It was not 5a's landmark clearing.
- **Frame time (RX 6700 XT, 1920×1080, tier 2, other agents' Godot running, vsync off as
  city_lab measures):** route page 2.93–2.97 ms a frame (city GPU 1.94–1.96 ms, CPU 0.37 ms), the
  Cell's route at ortho 351 3.75 ms (2.74), the close-up at ortho 60 2.67 ms (1.46). Inside the
  8 ms budget. The capture lab `tools/design_lab/netrun_states.tscn` gains `--size=WxH`,
  `--perf=<s>`, `rebel_cell` and `close` states and CAM lines.
- **Bakes behind a 3D route (ANIM-R5 P2 / R6 B6 follow the route):** the route never draws a 2D
  bake now, so its bake-ahead (`_prebake_route`) and its kept bake (`ROUTE_KEEP`,
  `_keep_route_bake`, `release_route_bake`) are removed from `netrun_scene.gd`. The pages after
  it (fight arena, Mainframe, event, loot, shop) still draw the 2D city: `_prebake_backdrops`
  bakes their frame behind the 3D route through `NeonCity.prebake(..., under_3d)` /
  `prebake_frames(..., under_3d)` (a 3D city otherwise still bakes nothing: the HQ Grid's
  prebakes stay off). Verified windowed: the event page's first frames are its dressed room.
- **Tests:** `tests/unit/test_art7_netrun_city.gd` (fast, new). Changed:
  `test_city_motion.gd`, the "no sky cars in the netrun" assert now applies at the transit's own
  zoom (MEDIUM); at CLOSE they show. `test_anim_r5_city.gd`:
  `test_the_runs_pages_open_on_their_bake_and_the_route_stays_kept` ->
  `..._behind_the_3d_route` (the route is the 3D city; each page is 2D and covered on its first
  frames; the route-bake LRU asserts go with the kept bake), `test_a_raid_interlude_bakes_its_playout_and_the_route_after_it_ahead`
  -> `test_a_raid_interlude_bakes_its_playout_ahead` (the route-frame assert goes). **Dropped:**
  `test_anim_r6_netrun.gd::test_the_route_bake_is_let_go_at_the_run_end` (no route bake is kept
  any more).
- Review: `docs/art_review/ART-7/7w/route_on_city.jpg` (start, underway, the Cell's route,
  the close-up).

### 2026-10-05 — Art direction — asset parity: combat and foundations (M14)
Designer ruling "REUSE ART-PASS ASSETS": every combat or foundation image the art pass made is exported by its own
generator on tag art-concepts-r43 (wrappers in `tools/art/export_*.py` change only font paths and split live text off),
and the game draws that image. Inventory: `docs/handoff/m14_asset_parity/combat.md`.
- Replaced: firmware dies (4 rarities + lit), Daemon tiles (12 idle frames + fire), hand card faces (wheel/hack/system
  x 4 rarities; new `CardFace`, combat hand only), HUD marks from the 1C atlas, SEND IT, PERFECT/GOOD/WEAK stickers
  (`StickerArt`), the EVADE `>>` token (flight and standing on the wheel), the drone sticker and its six flying pieces.
- Landing word WEAK is now the word "WEAK" (was x0.5) and amber, as the concept; the x0.5 stays on the rail. Accepted.
- Procedural kept, each with its reason, in the inventory (no concept sprite: bricks, hexes, bits, tears, shards, rings,
  cracks, jaws, Heat mark, lethal skull, dock geometry, peel curl, live-text stickers, kit materials, the wheel disc's
  bezel/hub, which are live geometry).
- New strings: WEAK, WHEEL, HACK, SYSTEM (translated once; `CardFace.KIND_WORDS`).
- Motion is unchanged (slap, peel, dissolve, token flight, drone slap and burst keep their ui_motion entries).
- The two ANIM reds the brief named (`vinyl_sticker.gd` inline tween, `fx_draw.gd` literal) no longer show in
  `test_anim_r6_rules` / `test_anim_r2_combat` on this branch; the one remaining r6 failure is
  `test_every_script_that_animates_registers_or_says_why_not` for `campaign_end/rubber_stamp.gd` and
  `kit/route_overlay.gd` (ART-11 and ART-5 5d files, not mine).

### 2026-10-05 — Art direction — asset parity: city and screens
Designer ruling: art-pass assets are exported by the art pass's own generators (tag `art-concepts-r43`), never redrawn.
Inventory, sources and the procedural list: `docs/handoff/m14_asset_parity/city_screens.md`; wrappers in
`tools/art_pipeline/parity/`; before/after captures in `docs/art_review/ART-parity/city_screens/`.
- **Replaced:** Site discs, pads, slip, badge and DOWN bolt (`assets/city/grid_markers/`); route stickers and operative token
  (`assets/netrun/route/`); seal emblems, padlock, house motifs, post-its, print stock and manila (`assets/campaign_end/`);
  billboard panels (`assets/city/billboards/`, packed R = lightened mask, A = alpha, tinted by the instance colour in
  `holo_billboard.gdshader`); the CLOSE flying car, chopper and drone (`assets/city/vehicles/`, Blender 5.2 running the
  concept builders `unified38.flying_car`, `district20.heli_geo` / `drone_geo`, extracted with `ast` and run verbatim).
- **Exploit marker = the v4 generator's single gold key** (orchestrator call): approved art wins over the bible's "keyring".
  The Exploit key MEANINGS word is "Gold key"; strings re-exported.
- **Corp seals use the round 6 `EM_` emblems** the seal script builds (halo and triangle, hex), not the bible crests
  (orchestrator call: the art pass is correct).
- **Car model as data:** the car needs per-vertex CUSTOM0 (part id), and an imported mesh cannot be read back headless, so
  `CityMotionMeshes.car` reads `flying_car_tris.json` (the same triangles as `flying_car.glb`). Chopper and drone are used
  as the imported glb meshes; vertex colours of the toon bodies are tones relative to the concept body colour, so the tuned
  `chopper_color` / `drone_color` stay the body tone. The rotor blur disc takes the model's blade radius and height (the
  ANIM entry stays; the static blades are not drawn).
- **Dropped test assertion:** `GlyphIcon` sub-badge on the Site `type_glyph()` (the badge is baked into the disc art; `disc_art()`
  replaces it). **Tests:** `test_city_motion` gains the asset check; MotionSkip registration of `rubber_stamp` and
  `route_overlay` (`NOT_SKIPPABLE` with reason) kept.
- **Procedural, with reasons:** see the inventory (state rings, text rings and stamps, tape, portrait chrome, FAR/MEDIUM car
  tiers, the lane line and others the concept draws procedurally or that follow state, zoom or text).
- **Proposed slice (not built):** host the 2A WheelView as a ViewportTexture in `JackSequence._draw_wheel` (the concept's
  `zoom36.wheel` has fixed English labels), together with the combat parity sweep.

### 2026-10-05 — Art direction — ART-12 12s skins
Agent 12s (the M12 box "Skins": procedural palette skins on the v2 tokens, ART_12_BATCH).
- **Which skins.** The M12 box names none, so: `v2` (the default and first; the identity, ART_BIBLE §2
  exactly), `cobalt` (deep blue terminal) and `graphite` (neutral grey terminal). A fourth, `verdigris`
  (sea-green), was built and dropped: teal sits between PROTECT cyan and GAIN green and failed the
  OKLab ΔE > 0.1 separation test against both.
- **What a skin is** (`PaletteSkins`, `scripts/ui/kit/palette_skins.gd`): new values for the chrome
  tokens only (TERMINAL_BG / _HOT / _EDGE / _TEXT, TEXT_HI / MID / LO, SELECTED, ON_SELECTED,
  CRT_GLASS_TOP / BOTTOM), made procedurally in OKLCH from the v2 values by one recipe per skin
  (an ink hue, a glass hue, chroma scales, an accent lightness shift; v2 lightness kept elsewhere so
  contrast holds). No concept asset exists for skins (the art pass drew v2 only), so procedural is
  the reuse rule's allowed case; nothing is redrawn.
- **Where it is realised.** Palette's tokens are compile-time constants used in other files' `const`s,
  so they are not changed: a skin is applied where chrome is drawn, as HighContrast / ColorblindLayer
  are. `UiTheme.build` calls `PaletteSkins.apply(theme, active())` before high contrast (by exact v2
  rgb match, alpha kept); `UiTheme.terminal_box` / `terminal_button_boxes` call `apply_box`;
  `HudSkin.draw_terminal_panel` and `CrtTerminalPanel` (Cell cyan accent only, glass, text) wrap their
  colours in `PaletteSkins.chrome()`; `ZinePanel`'s terminal mode (the Options / pause / confirm glass,
  its edge and corner ticks) does too and redraws on `Settings.changed`, so the open Options dialog
  turns as a skin is picked (found in the captures: the dialog had kept v2 navy). A colour that is not a chrome token passes through unchanged, so
  a corp edge or a Heat word is never re-valued. `active()` finds Settings by node path (the autoload
  name breaks `-s` tools at compile time).
- **Semantics kept.** Where cyan means PROTECT / the TURN Daemon / Uncommon / NET_CYAN it stays #5CE1FF
  on every skin; HARM / GAIN, the Heat bands, the corp kits, FOCUS lime and the stickers keep v2;
  every Palette.PAIRED_WITH greyscale cue stays. Views that set their own `Palette.TEXT_*` overrides
  keep the v2 near-white text (still readable on every skin's glass) until their batch reads
  `PaletteSkins.chrome`; kit painters pick up a skin on their next redraw, the theme at once via
  `Settings.changed`.
- **Settings and Options.** `Settings.palette_skin` (default `v2`), `PALETTE_SKINS`, `set_palette_skin`
  (unknown ids ignored), to_dict / from_dict (an old file without the key, or an unknown id, loads v2),
  covered by snapshot / restore. Options > Display has an "Interface skin" row (`SettingsPanel.skin_option`,
  "SkinOption"); 4C's restyle of the panel should keep the row. Skins are free (no Profile unlock):
  see the open question.
- **Contrast.** Every skin passes 1A's checks (TEXT_HI / TERMINAL_TEXT / the edge colour >= 9:1 on
  glass, TEXT_MID / TEXT_LO >= 4.5, hover glass >= 7, focus lime >= 7, words on the selected fill
  >= 7, Heat bands / HARM / GAIN / WARN >= 4.5), the theme's own text on its own boxes, and ΔE > 0.1
  between each skin's edge / selected fill and HARM, GAIN, the Heat bands, FOCUS, the stickers and
  every corp colour, and between skins. Cobalt's accent lightness shift is -0.07 (at -0.09 its edge
  was 8.7:1 on glass).
- **Captures.** `tools/visual_qa/review_pack.gd --skins=v2,cobalt,graphite` walks the screens once per
  skin into `<out>/<skin>/`; contact sheets in `docs/art_review/ART-12/skins/` (title, HQ, Grid,
  combat start, Mainframe, event, Options at 800x450; read: every screen reads on every skin, paper
  panels, stickers, HP / Heat words and corp edges unchanged). Still v2 on every skin, by design until
  their batch reads `PaletteSkins.chrome`: view-drawn panel frames and headings that use `Palette`
  constants directly (e.g. HQ's panel corner frames and "CYBERDECK" heading cyan).
- Test: `tests/unit/test_art12_skins.gd` (fast tier, 10 tests). No M13 test dropped.
- **12s-b: skin chrome sweep (2026-10-05).** Every direct use of `Palette.TERMINAL_EDGE / TERMINAL_BG /
  TERMINAL_BG_HOT / NET_CYAN` and `HudSkin.TERMINAL_EDGE / TERMINAL_BG` in `scripts/` was classed
  CHROME (frames, panel glass, chrome headings) or SEMANTIC. **Chrome: 55 lines in 30 files now go
  through `PaletteSkins.chrome` / `track_box`** (HQ's CYBERDECK heading and corner frames via
  `CrtWindow` / `TerminalWindow` accent and `CrtTerminalPanel` corp accents, the CRT switch, menu chip,
  ON AIR ticker, Heat glitch preview, HUD bar rule, wheel arrow plates, terminal note, toast, tooltip rule,
  confirm rule, SEND IT system strip, deck / spinner tabs, route label plate, hover glass of cards, CRT
  hum, page roll, legend button, Raid speed strip, Options sample / sliders / headings, title SLOT
  heading, combat TURN banner, dialogue black glass, the kit state's rest edge). **Kept: 146 direct uses
  in 46 files**, each listed with a reason in `ALLOWED` of `tests/unit/test_art12b_skin_chrome.gd`:
  about 100 SEMANTIC (net / hack cyan on maps, the jack and the 3D city; PROTECT FX, wall and chips;
  badges and stat icons; world / portrait art; stickers; RAM and face-button colours), 29 in
  `ui_theme.gd` (all in the theme, re-valued by `PaletteSkins.apply`), and the rest declarations that
  carry a v2 value into a routed painter.
  Calls: (1) `KitState.edge_color` routes its edge (all its callers are glass chrome); (2) a corp accent
  is unchanged because `chrome` maps exact v2 values only, so `CrtWindow` routes any accent; (3) text
  tokens (TEXT_HI / MID / TERMINAL_TEXT) are still v2 in views that set them (outside this slice).
  New helpers: `PaletteSkins.watch` (redraw on Settings.changed), `bind`, `track_box` (a StyleBoxFlat
  re-valued live from its v2 colours, weak links). Lint: `test_no_new_direct_use_of_a_v2_chrome_colour_...`
  (fast tier, static; `tools/` lab scenes are not scanned: concept sheets, not game chrome). New test
  script `tests/unit/test_art12b_skin_chrome.gd` (7 tests).

### 2026-10-05 — Art direction — ART-0 audit fixes
Fixes every finding of `docs/handoff/m14_audit/ART-0_horizontal.md` (3 P2, 12 P3); nothing deferred.
- **E1 (P2) shakes held to their tier.** `Motion.shake` plays `Motion.shake_px(id)`, the amplitude
  clamped by `VfxTier.clamp_shake(VfxTier.of(id), …)`; `Fx.shake_px` delegates to it. Data made honest
  too: `heat_letters_shake` is T3 (a Heat crossing is a moment, like `heat_number_pop` and
  `heat_banner`; keeps 3 px), `precision_weak` 4 → 2 px (T2); `hit_shake` stays 2 px (2C). Not a shake
  in the bible's sense, left as is: `drop_reject`'s 6 px wiggle of the small no-entry mark (the
  refused-target glyph moving, not the scene). Tests `test_every_shake_fits_its_tier` (every id the
  scripts pass to Motion.shake), `test_motion_shake_clamps_an_amplitude_over_its_tier`.
- **E2 (P2) one-shots fit their tier; holds and loops are marked.** Schema: `UiMotionEntryData.kind`
  { ONE_SHOT (default), HOLD, LOOP } (smoke-checked in `_art0_tier`); `VfxTier.fits` holds only
  one-shots to `MAX_SECONDS`. HOLD (what the duration measures is a stay or a wait): `saved_stamp`,
  `toast`, `toast_note_hold`, `resolve_sequence` (a budget), `combat_end_hold`, `jack_arrival_wait`,
  `asset_drop_wait`, and the readable floats `ram_spend_float`, `ram_refill_float`, `forecast_change`.
  LOOP: `drop_zone_pulse`, `pointer_orbit`, `ram_pending_blink`, `send_it_ready`, `route_target_pulse`,
  `tutorial_next_pulse`. Retiered T1 → T2 (short outcomes, not 0.25 s feedback): `wheel_spin`,
  `wheel_respin`, `inner_ring_turn`, `enemy_turn_spin`, `pointer_migrate`, `site_outline_draw`,
  `map_camera_ease`, `route_pulse`, `visited_dim`, `loot_fan`, `count_up`, `number_roll`, `drip_grow`,
  `drip_halo`, `minimap_pulse`, `flight_land_pulse`; `city_bake_fade` T0 (the backdrop). `buy_fly`
  and `loot_pick` 0.7 → 0.6 s (the bible names buy_fly a T2 outcome; ANIM-R5's floor 0.6 holds).
  Merged with main's newer entries (2B, ART-11): `backdrop_won_lights` T3 (a fight won is a moment),
  `preview_chevron_chase` LOOP, `ransom_sticker_curl` / `ransom_sticker_drop` T4 (campaign end is the
  bible's T4), `ransom_countdown` / `ransom_wipe_hold` HOLD, `dossier_open` T3.
  Tests `test_every_one_shot_entry_fits_its_tier`,
  `test_holds_and_loops_are_marked_and_only_one_shots_are_held_to_the_duration`.
- **E3 shader rule everywhere.** `test_vfx_tiers` scans every `*.gdshader` outside `addons/`
  (subfolders of `shaders/`, `assets/`, `tools/`): game shaders include rc_common; any shader with
  TIME freezes it through `rc_time` / `rc_live`. Fixed on the way: the two animated city-spike
  shaders (`tools/spike/city/shaders/city_car`, `city_post`) and `glyph_sdf` now include rc_common.
  After merging main: the ten static city / landmark shaders main added (`shaders/city/city_building`,
  `city_glow(_xray)`, `city_ground`, `city_network(_xray)`, `city_pool(_xray)`,
  `assets/city/landmarks/landmark_beam`, `landmark_toon`) include it too, and rc_common is
  include-guarded (`RC_COMMON_INCLUDED`) since `city_glow` / `city_pool`'s own includes pull it in;
  all compiled cleanly in a windowed renderer check. `glyph_batch.gd`'s `Color.WHITE` reads
  `Palette.NO_TINT`; the lint baseline lowered again to main's counts.
  Test `test_the_shader_scan_reaches_every_folder`.
- **B1 (P2) the Heat glitch is built.** `HeatGlitchLayer` (`scripts/ui/fx/`) + `shaders/heat_glitch.gdshader`,
  in the combat scene between the backdrop (city + Heat lights) and the UI root, so wheels, FX and HUD
  draw above it: the bible's protect mask (wheel discs <= 35 %) is met at 0 %. Grows with the band per
  round 18-22 (COOL dip + line jitter; NOTICED tears; FLAGGED roll + macroblocks; HUNTED hold slip,
  RGB split, scanlines; PURGE = HUNTED). Off by default; exempt from VfxTier (Settings.VFX_TIER_EXEMPT,
  nothing clamps it); flash limiter on: no luminance dip and no roll brightening; option off: the
  static corp edge tint at HUNTED+ only (§5.5), in the fight's corporation colour (Heat's HEAT_B when
  none). CALL: **off under reduce effects** (the brief); §5.5 had "tears only at NOTICED strength, one
  burst per 3 s" — reduce effects means no tears anywhere else (§5.4), so off is the simpler reading.
  Timing: `ui_motion.tres` `heat_glitch` (LOOP; duration = a glitch state's hold, amplitude = the
  edge tint's alpha; REQUIRED_IDS, motion-lab demo `fx_glitch`); per band
  `CampaignConfigData.heat_glitch_period / _burst / _tears / _blocks` (schema, smoke-checked,
  validated); px sizes are the view's named constants (round 18 table). Verified windowed (lab fight,
  every band, the off tint). Test script `tests/unit/test_heat_glitch.gd` (fast tier).
- **B2 names sweep narrowed.** The quoted-key form of the old raid word counts only in a raid context
  (a raid file, or one that builds raid outcome dictionaries); `ui_theme.gd`,
  `type_chrome_sheet.gd` and `test_w9_accessibility_settings.gd` write `"disabled":` plainly again.
  Test `test_a_control_state_key_is_not_a_raid_word_but_a_raid_outcome_key_is`.
- **B3 Hub Breach reads LOCKDOWN.** BREACHED stays the home server falling (ruling 6.2); the Hub
  Breach log line ("<name> hub in LOCKDOWN for N turn(s)") and the hub line's " (LOCKDOWN)" take the
  bible's word (§3.3, Appendix C #11). Seen, not changed: the netrun loot title "RACK BREACHED" (a
  Server Rack, not home; the audit confirmed it). Test `test_a_hub_breach_says_lockdown_not_breached`.
- **B4 saves folder.** `CampaignConfigData.max_replays` (50; 0 = no cap; schema, smoke-checked):
  `SaveService.write_replay` prunes the oldest; replay names lead with the zero-padded wall-clock ms
  so they sort oldest first. `export_presets.cfg` excludes `saves/*` in all three presets. Tests
  `test_the_replay_folder_is_capped_and_drops_the_oldest`,
  `test_netrun_rewind_and_resumed_fights_replay_to_the_same_hash` (netrun plain / with a rewind /
  saved and resumed through JSON, two seeds each).
- **B5 + O1 stale lines.** Part 2's "enum keeps SHIELD / DEPLOY / MISS" and D11 "no band changes" are
  struck and marked superseded; "the glitch comes in ART-3 / ART-5" annotated; the SANDBOX question
  struck as resolved; the cut-off duplicate D11 question line removed.
- **C1 + D2 named colours.** `Palette.HC_BG` (#000) is high contrast's background; the colour lint
  also counts `Color.WHITE` / `BLACK` / `TRANSPARENT` and the like; all 22 uses in `scripts/ui` now
  read `Palette.NO_TINT` (multiplier white: shader carriers, masks, modulates), `CLEAR`, `WHITE_HOT`
  (victory disc flash, white-hot bits) or `HC_BG`; values unchanged. Test
  `test_named_colour_constants_are_palette_tokens`.
- **D1 no slack.** Baseline lowered to today's counts (`ui_theme.gd` colour 24 → 12);
  `test_the_baseline_has_no_slack` fails when a count drops without the baseline following.
- **O2** `.github/workflows/ci.yml` fast-checks runs `python3 tools/test_run_tests.py` (triggers stay manual).
- **O3** `docs/timeline/.gdignore`.

### 2026-10-05 — Art direction — ART-5 5e city integration
Agent 5e (wave 2b, critical path; ART_BIBLE v2 §4.1, §4.3, §4.4, §4.5, §5.4, §6.1; refs round 34
`map_fist_reveal`, round 39 `city_grid`, round 40 `unified40` / `three_views_v3`).
- **Reduce motion is not a pause.** CityView3D keeps `ambient_scale` 0 under reduce motion (its
  rain, fog and network decal hold), and gains `host_pause_changed` / `host_paused()` (covered or
  unfocused). CityViewMotion now pauses the layers on the host's pause only, so under reduce motion
  the street traffic keeps moving at `CityMotionConfigData.reduce_motion_street_rate` (0.4, new
  field, validated 0..1, smoke-checked in `_art5_city_motion`) without streaks, sky lanes show
  their markers without cars, everything else holds its steady look (bible 5.4; replaces 5c's
  "street traffic pauses", open question 5c (2) answered by the art pass). Measured windowed:
  street clock 0.45 s per wall second under reduce motion (frame-step noise round 0.4).
- **Day-look API** (5c's open question (3)): `CityView3D.set_night_share(n, day)` lerps the
  buildings', streets', post's and sky's night look toward `day` and restyles the landmarks (and
  roof props) day or night; `CityViewMotion.day_look(mcfg)` builds `day` from the motion config,
  and `_on_night_share` calls it (no more reaching into the view's materials). The Grid stays
  night: the game has no day / suspicion rule (orchestrator call (c), accepted).
- **The Grid's city life** (`GridCityLife.of(c, corp, cfg)`, pure, `scripts/city3d/`): the Heat
  band (`Palette.heat_band` on `HeatRules.band_levels`), the hardened Sites (the launchable Sites
  while ENEMY_RESISTANCE is on, sorted), the home lot, DISPATCH's fist (`corp.id == rebel_cell`:
  the REBEL_CELL campaign; orchestrator call (c), accepted), the Site landmark lot.
  `NeonCity.set_city_life(d)` (called by `hq_scene.show_grid` after `_mount_grid_camera`) sends
  it down: `view3d.set_site_landmark`, `show_cell_dispatch`, `CityViewMotion.set_heat` (the rig
  centres on the hardened Sites). Every 3D NeonCity now carries a `CityViewMotion` (motion on the
  live Grid; its attach is deferred one frame so the host's home lot and Heat land first).
- **Site landmarks.** 5b's `<corp>_site.glb` stands on the Site named by
  `CityConfig.site_landmarks` (Solace `t1_c` Patient Records Vault, Halcyon `lose_the_case_file`,
  Orbital `o1_d` Subscriber Uplink Office: open question below), centred on that Site's lot; the
  procedural buildings under 92 % of its ground box give way (chunks rebuilt). Meridian and the
  Cell have no Site model. The overlay's markers float over the landmark: `NeonCity._roof_3d`
  lifts the roofs of the lots under it (`CityLandmarks.lot_rect`) to the model's top, and
  `frame_stamp` carries the lifts so overlays re-place.
- **Crest blackout reveal.** `CityView3D.cell_reveal` is a property (its setter drives 5b's
  `reveal_q`); `play_cell_reveal()` tweens it 0 -> 1 with the new `cell_fist_reveal` entry (T0,
  2.0 s, IN_OUT sine; REQUIRED_IDS; motion-lab demo on 5b's district model). It plays once per
  process when the Grid's 3D city mounts; reduce effects, reduce motion, headless or the entry off
  show the fist at once; MotionSkip settles it (`Motion.run` hold).
- **x2 Site spread, aimed into each territory** (orchestrator call (a)). `CityLayout.site_points`
  spreads the layout by `CityConfig.site_spread` (2.0) round the HQ, the boss end kept 3.5 lots
  from the HQ's centre, and turns it by `CityConfig.site_aim_deg` (Halcyon 255°, Meridian 140°,
  Rebel_Cell 270°; Solace and Orbital 0°) with `site_mirror` (none). The aims are the middle of the
  ranges where every Site stands in its own territory, found by the sweep
  `tools/city/site_spread_probe.tscn -- --search` (72 headings x mirror): all five corporations
  32/32 Sites in territory, none on an HQ plaza, none off the city, one Site a lot (was Meridian
  9/32, Halcyon 6/32, Rebel_Cell 15/32 at 0°). Halcyon's and the Cell's Grids now run up the
  screen, Meridian's diagonally. Presentation only: no rule reads the layout. The Grid fit lands
  at ortho ~490-530 on a 1280 px window (the side column takes a third: ~330 on the map's free
  part); 5a's s = 1 gave 241.
- **Off-screen TARGET** (`TargetEdgeMarker`, `scripts/ui/kit/`): when the Central Server's marker
  is off the Grid's map area, a red grease-pencil arrow (PencilShapes.arrow, THREAT ink) sits on
  the area's edge (EDGE_MARGIN 46 px inside, above the key and the minimap) pointing at it, with
  the scrawled word TARGET behind it; clicking the arrow asks the page to centre on it
  (`pan_requested` -> `CityGridControls.centre_on`). The clamp `edge_point` is pure and tested.
- **Markers stay on the Grid overlay** (orchestrator call (b), accepted): the overlay keeps
  drawing 5d's SiteMarkerView v4 on the 3D-matched projection (5a); SiteMarkerLayer and
  `GridMarkerProjection.from_view` serve the views without a NeonCity (6w raid, 7w netrun). They
  differ by design: the overlay snaps a Site to the nearest building of its layout point (within
  4 lots), the projection keeps the layout's floor lot; a test pins the 4-lot bound.
- **Roof props** (bible 4.1: from raid zoom; reuse rule). `tools/art_pipeline/city/
  build_roof_props_v1.py` runs the round 40 concept's own drawing lines (unified40.py 204-227 and
  `cyl36` 231-237, vendored unchanged in `concept_r40/`, ported from art-pass ace98b9, on
  concept_r31's identical target_corps.py) in Blender 5.2, one prop per run with a scripted
  stand-in for the building's random (every chance passes, ranges at their middle), and exports
  `assets/city/roof_props/roof_props.glb` (AC unit, water tank, antenna with its red light, four
  holo billboard colours; toon + neon roles, art_export/1 manifest; `RoofPropAssetChecks` in
  validate_content). `CityRoofProps.place` applies the concept's rules (flat roofs, footprint >
  2 BU, AC 0-2, tank 18 %, antenna on roofs over 22 BU at 45 % scaled 3-7 BU, billboard over
  14 BU at 16 % scaled 4-7.5 BU wide) with a per-building hash, all numbers in CityConfig
  (`roof_*`). One deviation: a spot whose centre falls off a turned / odd roof is left out (the
  concept used the roof's bounding box; on the game's footprints that floated props over the
  street). CityView3D draws one MultiMesh per prop per chunk, shadows off, at ortho <=
  `roof_props_below` (420); ~15 k instances over the whole city. Perf (city_lab, 1920x1080, props
  on): tier 2 raid 3.3 ms avg (GPU 2.4), close 2.4 ms; tier 1 raid 2.5 ms, close 1.75 ms.
- **Tools.** `tools/city/city_integration_capture.tscn` (one windowed launch: per corp the Grid,
  the Site landmark close with props, the off-screen TARGET; the Cell's reveal; reduce motion's
  street rate), `tools/city/site_spread_probe.tscn` (the spread sweep), 5e's
  `tools/city/city_hosts_check.tscn` (buildings on every host).
- **Tests.** New `tests/unit/test_art5_city_integration.gd` (fast): reduce motion is not a host
  pause; the day-look call; the reveal (T0 entry, end state, tween, skip); the spread in every
  territory and x2; GridCityLife; the roof lift; the TARGET clamp; the roof props (export and
  rules); the Grid markers vs the projection. `test_city_motion` updated for the 40 % rule.
  Changed, not dropped: `test_horizontal_pass21_city.test_raid_sway_covers_each_corporations_own_sites`
  asserted that Halcyon's Grid reaches past its district (a property of the old layout the
  aimed spread removes); it now asks the border case (H21 #22) directly: a Halcyon Site's lot
  read as a neighbour's territory is still swayed.
- **Grid fit room** (file outside the area: `hq_scene.gd`, one constant): `GRID_MIN_ZOOM` 0.3 ->
  0.22. At 0.3 every corporation's x2 Grid fitted at the clamp (ortho 532 on 1280 px) and
  Meridian's key covered nodes at text size 2.0 (`test_city_map_sweeps`).
- **Heat-band and day-look review (orchestrator follow-up).** One windowed launch
  (`city_integration_capture.tscn -- --looks=1`) walks every Heat band through the real path
  (the campaign's Heat at each band level, then the Grid page again) and the day look (the
  motion layers' crossfade to DAY, i.e. `set_night_share`), for Solace and the Cell; frames
  `heat<k>_*` / `day_*` in `docs/art_review/ART-5/5e/`. Two fixes from reading them:
  (1) **the Grid's network decal vanished whenever the Grid page rebuilt** (every Site
  selection, claim, repair, upgrade): the old CityMapOverlay left the tree after the new one
  fed the decal and cleared it. It now clears only its own network (`_fed_network`; file
  outside the area, smallest change; test `test_a_rebuilt_map_keeps_the_newer_maps_decal`).
  (2) **the day look was warm and bloomed white**: 5c's day ramp turned Solace's teal olive and
  the night bloom (threshold 0.62) washed the landmarks out. Retuned to the round 26
  `hq_*_close_day` / `city_ambient_day_v4` cool day (ramp, sky, haze, grade in
  CityMotionConfigData) and new `day_bloom` 0.2 / `day_glow_threshold` 0.92 (schema
  addition, validated, smoke-checked) that `set_night_share` lerps. The Heat rig reads as
  round 37's calm Heat B (a few searchlight beams, alarm and node lights; police strobes and
  choppers are small at Grid zoom): kept as designed.

### 2026-10-05 — Art direction — ART-5 5c city motion
Agent 5c (ART_BIBLE v2 §4.1 car LOD, §4.2 city motion, §4.3 Heat on maps, §5.3–5.5, §6.1;
refs round 24 `motion_layers`, round 26 ambient v4, round 37 calm Heat B, round 40 `cars_lod`).
- **One seam.** The layers (`CityMotionLayers`, `scripts/city3d/`) read the city only through
  `CityMotionSite` (lot frame, avenues busiest first, roofs, street lots, home, bounds), built by
  `from_model` (5a's CityModel) or `from_district` (1D's spike). `CityViewMotion` puts them on 5a's
  `CityView3D`: groups `traffic`, `sky`, `props`, `heat` go to the view's scene layers (traffic,
  sky and heat also in the ground-only pass, so cars and Heat pools show under see-through
  buildings); `camera_changed` drives car LOD and sprite sizes, `band_changed` the view
  (GRID / RAID / NETRUN), `ambient_changed` pauses every layer, the spill goes to `set_spill`.
  `tools/spike/city/city_spike_motion.gd` keeps a spike host for windowed render checks.
- **Config.** New schema `CityMotionConfigData` (`scripts/data/`, shipped
  `content/config/city_motion_config.tres`; smoke check `_art5_city_motion`): counts, sizes,
  colours, road heights, band rigs, the day look. Every timing is a `ui_motion.tres` entry (all
  T0, in REQUIRED_IDS, each with a motion-lab demo on a small grid city): `sky_lane_cars`,
  `street_cars`, `holo_billboard`, `aviation_blink`, `searchlight_sweep`, `chopper_orbit`,
  `drone_orbit`, `police_strobe`, `alarm_beacon`, `heat_node_light`, `city_light_fade`. NeonCity's
  `city_traffic` / `beacon_blink` stay with the 2D city (its AWAITING_FIX entries are not hidden).
- **Sky lanes** (round 26 v4): the 16 road shapes (A double deck, B, C with its flyovers and
  1.75-turn spiral, F's cloverleaf of four 270° loops, the D×E four-level stack) on the city's own
  busiest avenues (three per axis, at least 6 lots apart), each a row per direction baked into a
  float texture (xyz, a = length), uniform by arc length; the car shader moves every vertex along
  its row, so lines bend through loops and ramps. A loop moves 14–20 whole gaps (seamless). Guide
  dots per road in its rail colour.
- **Colours from a derived stream.** Cars and street cars take their lane colour from
  `RngStreams.make_stream(city_seed, &"city_traffic")`, billboards and aviation phases from
  `&"city_ambient"`: seeded like RngService streams but never the campaign's own, so a view moves
  no game state.
- **Car LOD:** FAR / MEDIUM / CLOSE by ortho (400 / 150) with hysteresis **0.04** (1D's 0.06 kept
  the raid's 380 on FAR coming from the Grid; the bible and `cars_lod` put the raid on MEDIUM). At
  management zooms only the lane line drops to 35 %; the car stays full strength. The CLOSE model
  is a light toon-lit wedge (ToonInkMaterial's bands in the path shader; no ink hull: the cars are
  drawn after the city's ink pass). Choppers and drones use `ToonInkMaterial` with its ink.
- **Heat lights** (calm, centred on the hardened nodes' centre, home when none): every hardened
  node one circling red / blue light on a thin `HEAT_B` ring, drawn through buildings like the
  network decal; per band COOL nothing, NOTICED 3 alarm beacons, FLAGGED two slow searchlights
  (calm, lower alpha) + 2 alarms, HUNTED + 13 police strobes, 2 choppers, 6 drones with
  spotlights and ground pools; **PURGE uses HUNTED's look** (`CityHeatRig.look_of`). Suspicion
  (round 6) adds 13 strobes, 3 choppers, 5 drones round the Cell's home, day or night.
- **Day / night.** The layers crossfade (`city_light_fade`) and send the night share up; the host
  lerps its toon ramp, sky, windows, neon, haze and grade toward the config's day look; by day no
  rain and no fog at raid zoom (bible 4.2). 5a's CityView3D has no day-look call yet:
  `CityViewMotion` sets the view's materials directly (asked of 5a below).
- **Pause / reduce.** Every layer keeps its own clock: covered, unfocused or the host's ambient
  scale 0 → stopped where it is; reduce effects / headless / entry off → the end state at once
  (time 0, lights steady on, one billboard panel, searchlights at rest, aircraft parked);
  **reduce motion pauses every layer in its steady look** and shows the sky lanes' markers
  without cars (the brief and 5a's ambient scale; bible 5.4's "street traffic at 40 %" is not
  kept). Quiet windowed runs ignore focus (they never have it). The netrun transit turns the
  sky-lane cars off (bible 4.1); the CLOSE tier (< 150) therefore only shows outside the netrun
  band (open question below).
- **Frame cost** (spike host, this PC, 6 s averages, worst rig HUNTED): 1920×1080 tier 2 grid
  2.97 ms with the layers vs 2.93 without (GPU +0.03 ms, +46 draws); raid 3.04 vs 2.95. Deck tier 1
  at 1280×800: grid 2.10 vs 2.04, raid 2.17 vs 2.15. City total within the 8 ms budget.
- Tests: `tests/unit/test_city_motion.gd` (fast). Captures: `tools/city/city_motion_capture.tscn`
  (one launch walks 15 states; `--host=spike`; `--mperf`). Crops: `docs/art_review/ART-5/5c/`.

### 2026-10-05 — Art direction — ART-5 5d Grid markers and key
Agent 5d (Group 3 wave 2; bible §4.3, §4.5, §4.9, ruling 11, D17; refs `city/round42_site_markers/*`,
`round39_landing_exploits/exploit_on_map_v3.jpg`, `exploits_v2.jpg`, `round39_city_unified/city_grid.jpg`;
generator `art-concepts-r43:docs/concepts/round42_site_markers/scripts/markers42.py`).
- **Site markers v4 (`SiteMarker`, pure; `SiteMarkerView`).** One marker, five layers ported from
  `markers42.marker()` at its sizes (disc 30 px, Exploit 34, not-yet x0.85, ring gap 5 / width 4 (3),
  pad 17 (14), pips 5 px squares, badge 9, sub-badge 0.31 of the disc). The state is a pure function
  `SiteMarker.spec_for(campaign, corp, site, selectable)`. Per the coordinator, the disc is a 1B
  `VinylSticker` (node stickers are vinyl): CIRCLE, gloss, a 1.5 px die-cut rim, art at 2x on a holder
  (the sticker's own scale belongs to its motion). Cleared = grey vinyl (`grey` 1); DOWN = the
  sticker's DISABLED state under the white bolt.
- **Icons.** The Exploit type sub-badge is the glyph atlas (`GlyphIcon`, `exploit_<type>` keys). The
  atlas has no map icons yet, so the corp crests (Meridian crane-A, Solace helix, Halcyon eye, Orbital
  ringed planet, REBEL_CELL fist), the keyring, flame, tucked-thumb fist (`fist_mask` geometry), heart,
  bolt and check are vector ports of the round 42 masks. The locked link's padlock is the atlas's
  `state_locked`. Disc fills are night ink tinted by a token (no new Palette tokens).
- **DOWN** = `SiteMarker.draw_bolt` (the v3 `bolt_mask`, white with a dark shadow, spanning the marker,
  everything greyed). It is a static so 3A's raid view can draw the same bolt (ruling 11). **TAKEN** =
  the SEIZURE NOTICE slip (pale paper, violet hatch and letterhead with the corp crest, red bar, tilted
  -8 deg) with violet pips; orange ring while a Reclaim run is launchable. Links to a TAKEN or DOWN node
  are de-powered (grey double trace, broken, no packets); locked cross-links show (grey dashes,
  padlock disc). Both only on the Grid (`grid_graph(..., v4 = true)`); raid and netrun graphs keep
  their own look (3A / 3B).
- **Hidden-nodes rule (round 42 rules strip, bible §4.5 "Pinned").** Regular Sites that are not
  selectable are hidden; Exploit, Heat objective, the boss, yours, cleared and TAKEN Sites, the
  selected Site and a Site lit from its run row always show. The key's `HOVER: SHOW ALL` cell (pad:
  `OPEN KEY: SHOW ALL`, the key button opens it) shows them all. A hidden Site is not picked on the map,
  keeps no room in the fit or the icon stacking, and stays reachable by PREV / NEXT SITE (pad
  reachability unchanged).
- **Boss.** The red pencil TARGET is 1B's `GreasePencilMark` (hand circle, THREAT ink) plus
  `GreasePencilWord` "TARGET", on a pencil layer above every UI layer of the overlay; the chip
  `CENTRAL SERVER // EXPLOITS n/3` sits over the circle, clear of it.
- **Exploit tag on hover (bible §4.9).** On the map an Exploit Site shows only its badge and gold pips.
  Pointing at it (or lighting its run row) opens its decrypted file: a 1B `DecryptedHoloPanel` (corp
  tint, no scrim) with `CATEGORY // ITEM` from the corp's ExploitData (`Breach: Customs Override Keys`
  -> `BREACH // CUSTOMS OVERRIDE KEYS`), its effect at the breach and the Site. Its tooltip leads with
  the same tag.
- **Fight won (D17).** A cleared or claimed Site's building lights its windows in Cell pink with some
  lime (`SiteMarker.won_light`, deterministic by Site id): on today's Grid host as window rows on the
  roof's front walls; on 5a's 3D city as `SiteWonLights` (one MultiMesh of window quads for the `fx`
  layer, placement pure and tested). Call: a DOWN node's lights are out (no power), so DOWN reads
  apart from a won Site.
- **The Grid map key, restyled (carry-over item).** The Grid's key is the v4 key
  (`MapLegend.use_site_markers`). Each row draws the map's own marker (`SiteMarkerView`) or line, with
  a word or two. Pointing at a row gives its meaning in plain words (`SiteMarker.MEANINGS`, written from
  the rules as the v4 legend is). The strip keeps the reference's rows: next, cleared, yours, DOWN,
  TAKEN, exploit, heat obj., locked link, a threat route when a raid is coming, and SHOW ALL. The
  compact key holds every row (+ not yet, CORE, TARGET, no power). Fold, fit and live text size behave
  as before (H23/H24, `legend_fold`).
- **Group 1 naive audit P2s.** (1) The other maps' key: "cleared" had the corporate square; it is
  now `◇`, and a test checks that every key entry differs in greyscale (glyphs for the old key,
  `SiteMarker.grey_key` for v4). (2) A selected Site with no JACK IN says why in plain words and what
  to do first (`why_not_runnable`: CORE, the breach's Exploits, the linked Sites to clear first, or no
  operative).
- **Projection seam.** `GridMarkerProjection` attaches to 5a's seam (54ee7d2): `from_view(CityView3D)`
  (project, top_at; re-place on `camera_changed` / `band_changed`), `from_model(CityModel,
  CityIsoCamera)` headless, `from_camera` with no model. `SiteMarkerLayout` (pure) places discs apart
  and labels clear of markers, and picks. `SiteMarkerLayer` puts the markers on the 3D city. Today's
  Grid page still runs on its NeonCity host (the overlay places markers on its roofs, the same layers
  and rules). Moving the page onto CityView3D waits on 5a's Grid camera and fit. Proposed slice: when
  5a's Grid host lands, mount `SiteMarkerLayer` with `from_view`, and keep the overlay for the routes.
- **Tests changed (none dropped):** `test_horizontal_pass21_city` tooltips, `test_horizontal_pass22_city`
  pips and focus strip, and `test_city_map_sweeps` icon, node and overlap checks now skip hidden v4
  Sites. The boss and claimed nodes carry no pips (v4). New: `tests/unit/test_art5_grid_markers.gd`
  (fast).

- **Open questions (defaults built; also under "Open questions for the designer"):**
  - **SHOW ALL setting.** The Grid reveals hidden Sites by the key's hover / open. D13's "Always show all
    nodes" setting (3B, netrun) should drive the Grid too once it lands. Default: the key only.
  - **VIRUS badge.** The bible says the INFECT glyph. 1C's table maps `exploit_virus` to
    `status_corrupted` (the effect it causes). Default: the table.
  - **DOWN lights.** A won Site whose node is DOWN goes dark (no power). Default: dark.

### 2026-10-05 — Art direction — ART-5 5a city model
Bible §1.2 World, §4.1–4.3, §6.1; 1D's report (`docs/handoff/art_1/city_spike_report.md`, "What
ART-5 needs"); 1B's material kit. Agent 5a (Group 3 wave 2, M14).
- **Production classes (from 1D's spike).** `CitySpikeConfig` is renamed `CityConfig` (internal
  names follow the word; the spike keeps its district in `tools/spike/city/city_spike_config.tres`).
  The game's values are `content/config/city_config.tres`: the whole city `city_rect` (lots
  -80..85 on both axes: every territory, HQ and the Sprawl round them), `chunk_lots` 24, building
  LOD (`lod0_below` 400, `lod2_above` 760, `lod_rows_share`, `lod_cols`), zoom / pan (`grid_ortho`
  440, `zoom_ortho_min/max`, `zoom_step`, `pan_screens_s`, `band_netrun_below`, `minimap_size`) and
  the network decal (`net_*`).
- **`CityModel`** (`scripts/city3d/city_model.gd`): the whole city of the game's own layout
  (CityLayoutRecorder per chunk, the NeonCity placement code, seed 7): 13,306 buildings, 17,968
  extrusions, 9,267 street lots, 64 chunks; recorded in 1.4 s headless on one thread, in the game on
  the worker pool (`CityView3D`, chunks in order, so the model is deterministic). Shared once per
  process (`CityModel.shared`). Picking tests only the chunks the ray crosses (equal to testing every
  prism; ~3 ms a pick). The Cell's district keeps the street grid (round 34 lock); the HQs are
  stepped stand-ins until 5b's landmarks (`hide_stand_in`).
- **Building families** stay 1D's 12 unit-prism families (4 / 6 / 8 sides × 4 facet-row classes,
  the bible's "~6" is per side count) — one MultiMesh per family **per chunk**, so frustum culling
  works; LOD0 / LOD1 / LOD2 meshes (all rows / half the rows and 2 columns / one row: a plain
  extrusion) swap by camera ortho with the 6 % hysteresis (`CityLod.building_lod`), never by
  distance. Buffers are written whole (`CityMeshKit.instance_buffer`, 31 ms for the city).
- **View bands** (`CityLod.band`): GRID at and above the see-through band's top (ortho ≈ 440, 1D's
  lod 1.595), RAID down to ortho 200, NETRUN below, with hysteresis: the views move onto the city by
  zoom band, no scene change.
- **Materials: one seam** (`CityMaterials`). The building and ground shaders moved to
  `shaders/city/`; their toon bands and banded light spill now come from 1B's kit through a shared
  include, `shaders/kit/toon_bands.gdshaderinc` (`toon_band_index`, `toon_spill` and the
  `spill_*` uniforms), so `ToonInkMaterial.set_spill` / `LightSpill.uniforms_3d` drive the city as
  they drive props. **Small change to 1B's material:** `toon_ink.gdshader` includes that file
  instead of declaring its spill uniforms and loop itself (same uniforms, same maths). The city's
  ink stays 1D's depth / normal post pass (1B's note: the inverted hull splits at hard corners on
  big city meshes); the band edges and ramp colours stay the city's config values.
- **SEAMS for 5c / 5d / 5b / the views** (`CityView3D`, a SubViewport with its own World3D):
  - *Scene layers:* `layer(name)` for `ground, network, buildings, landmarks, props, traffic, sky,
    heat, fx`; `add_to_layer(name, node, ground_pass)` (ground_pass = also drawn in the ground-only
    pass, render layer 2, seen under see-through buildings); signals `camera_changed(iso)`,
    `band_changed(band)`, `building_lod_changed(lod)`, `ambient_changed(scale)` and
    `ambient_scale` (0 when the map is covered, the window unfocused, or reduce effects / reduce
    motion is on: every ambient layer pauses on it); `set_spill(sources)`; `landmark_slot(corp)`,
    `hide_stand_in(corp)`.
  - *Picking (pure, this viewport's pixels):* `pick(p)` → {prism, building, cell, lot, terr, world},
    `lot_at(p)`, `project(world)`, `unproject(p, height)`, `lot_world(lot, height)`, `top_at(lot)`;
    the same on `CityModel` with a `CityIsoCamera` for headless tests.
  - Overlays read the camera only through `CityIsoCamera` (1D's constraint).
- **The City Grid runs on the 3D city.** The Grid page sets `WireframeBackground.city3d`; its
  NeonCity then keeps every map API (camera, `grid_to_local`, `roof_of`, `nearest_building`,
  `is_street`, `camera_settled`, marks and the spread mask) but projects the way the 3D camera does
  (the ground's rows step `TILE_A × sin 40°` instead of the 2:1 `TILE_B`; roofs lifted to their 3D
  height, `height_px_bu × cos 40°`), answers from its placement with the fist roads dropped (the
  model's layout), never bakes (`view_covered` is true, `prebake` does nothing), and draws
  CityView3D's texture in place of the baked image (no 2D dim, no scanline live shader). So
  `CityMapOverlay`, the legend, the fits, labels, lean, ANIM motion (ease, crawl, packets, chevrons,
  drop, travel, the claim's marks and the influence spread mask, now over the 3D city) and their tests
  are unchanged; `test_city3d_grid` proves a lot's map point is `CityIsoCamera.project` of it. The
  raid / netrun / HQ-run pages keep the 2D city until the next step (they switch the same flag).
  Headless keeps the projection and placement (no 3D nodes): the tests measure the real Grid.
- **The map's links are the ground decal** (`CityMapOverlay.on_ground_decal`): the overlay feeds
  `CityNetworkData` to the city on every relayout (read-only), draws no veil and no static link
  strokes; the decal (`shaders/city/city_network*.gdshader`: single trace + halo + node disc and tier
  rings at city zoom, 3-trace bus with vias and packets at management zooms, dashed border links)
  sits on render layer 2 (under see-through buildings) and an x-ray pass with the depth test
  inverted shows hidden links through buildings (solid at the Grid, `net_xray`).
- **Call: the Grid holds the GRID band** (`band_lock`): its fit frames the Sites at ortho ≈ 200–300
  (CityLayout spreads the Sites ±7.5 lots; at the bible's ortho 440 they would take a third of the
  map and crowd the labels), so the Grid keeps solid buildings and the full city life at any player
  zoom rather than going see-through by ortho. Proposed slice with the raid / netrun move: spread the
  Site layout ×2 for every view at once (Grid at ortho 440 as round 39) — not now, because the 2D
  raid and netrun views share the layout and their fits.
- **Player camera** (`CityGridControls`, `CityMapCamera`, pure): the wheel and + / − zoom
  log-linearly about the cursor (`zoom_step`, clamped to `zoom_ortho_min/max`); a drag on the empty
  map, WASD (physical keys: no new input actions) and the pad's right stick pan, the frame's centre
  kept in the city; every move goes through the page's `_frame_city`, so fits and labels read the
  real camera. **Minimap terminal** (`CityMinimap`, a CrtTerminalPanel): the city's territories, the
  Sites (lime yours, red the target), the view box; a press or drag centres the camera. It sits at
  the map's foot left of the key (the key's strip is that much narrower) and labels avoid it.
- **Ambient pause:** `ambient_scale` is 0 when the map is covered, the window unfocused, or reduce
  effects / reduce motion is on; the post's rain / fog and the decal's packets freeze (end state).
- **Tests changed** (they pinned the 2D bake on the Grid, superseded): `test_anim_r5_city` "a claim
  stamps at once and the tint follows its bake" (the claim stamps once at once, the view stays
  covered) and `test_anim_r2_city` "the Grid draws its nodes before any bake lands" (the 3D city
  covers the Grid at once; the nodes, labels and settled camera on the first frame are kept).
- **Call: the minimap folds with the key.** At the text sizes where the map key folds to one line
  (`MapLegend.FOLD_SCALE`, 1.3 and up) the minimap's room is the map's, so it hides; the wheel,
  drag, WASD and the right stick still move the camera.
- **Not done in this slice (proposed next):** the edge chevrons and the red pencil marker for an
  off-screen TARGET (§4.1; with 5d's markers), the Cell's red-window crest and the HQ heroes (5b's
  glTFs: `landmark_slot` / `hide_stand_in` are ready), city motion layers (5c, on the layer seam), a
  Deck measurement (tier 1 on this PC only).
- **Perf** (`tools/city/city_lab.tscn --perf`, windowed through run_windowed.py, RX 6700 XT, 4–6
  other agents' Godot processes running): tier 2 at 1920×1080 — the Grid page's frame (ortho 220,
  GRID band) 2.54–2.72 ms a frame (city GPU 2.0–2.2 ms, 0.5–0.6 ms CPU), the bible Grid (440) 2.24,
  raid (300) 3.06, netrun (160) 2.75, the whole city (1300) 3.01 ms; 300–1,250 draw calls (chunks ×
  families × the shadow pass), 0.65–4.2 M primitives, 118–139 MB texture memory. Deck tier 1 at
  1280×800: 1.91 / 2.11 / 2.62 ms (Grid page / raid / whole city), 51–57 MB. All inside the 8 ms
  budget; the Deck itself is still unmeasured. The model records in 1.2–1.4 s on the worker pool
  (the city fills in nearest chunks first, 6 a frame).
- **Captures read** (`docs/art_review/ART-5/5a/`): the Grid page beside round 39 `city_grid`
  (same violet night city, solid toon bands, ink, roof neon, lane glow, the network as a ground
  decal under the icons and x-rayed through buildings, the minimap terminal; closer framing than the
  reference, see the GRID-band call); the lab at grid / raid / netrun (see-through at 0.68 from
  raid, LOD swaps), every corporation's Grid frame, the whole city and a close frame.
- **The art pass's own models, never redrawn (designer ruling 2026-10-05, "reuse the art pass's
  assets").** CityView3D places 5b's landmark glTFs with 5b's `LandmarkMaterials` (night) once the
  model is in: each corporation's `assets/city/landmarks/<corp>/<corp>_hq.glb` on its HQ lot (the
  stepped stand-in goes), and `rebel_cell/rebel_cell_district.glb` (the Cell's own street grid with
  the red-window fist) on the Cell's district centre; the procedural buildings inside a landmark's
  ground box give way to it (`_cleared`), so no lot holds two cities. A missing file keeps the
  stand-in. Visuals and their sources:
  - ordinary buildings, street lots, lane glow: the game's own layout (NeonCity placement through
    CityLayoutRecorder) extruded with 1D's port of the concept recipe (`unified40.fgrid` facets,
    `city_building` windows / ledges / shopfronts / roof trim, `target_corps.mat_toon` bands) —
    shader-shaded, the shapes are the layout's extrusions;
  - the four corporate HQs and the Cell's district: 5b's glTFs (Blender from the concept scripts,
    `tools/art_pipeline/city/`), shaded by 5b's `landmark_toon` / `landmark_beam` shaders;
  - ink, see-through, spill, bloom, fog, haze, rain, grade: 1D's port of `post40.finish`;
  - toon bands and light spill: 1B's kit include;
  - the network decal: `post36.Net36` / `netdecal21` as specified in bible §6.1 (a shader, no model);
  - not placed yet: 5b's `*_site.glb` Site landmarks (with 5d's markers), 8p's HQ compounds (they
    belong to the HQ-run view, the next step), the concept's roof props (AC, tanks, antennas) and
    billboards (no export exists yet: proposed as a 5b / 5c export job, never re-modelled here).
- **No buildings in 5c's / 5d's captures:** the seam commit (54ee7d2) had two bugs, both fixed in
  66e4f1a: `CityMeshKit.families_of` appended to a cast copy of a packed array (every family
  MultiMesh was empty), and a MultiMesh filled through `buffer` keeps no bounds (now the chunk's box
  as `custom_aabb`). Merge 66e4f1a or later; the buildings draw (captures above).
- **Moved files:** the city shaders moved from `tools/spike/city/shaders/` to `shaders/city/`; 5b's
  `landmark_review.gd` and 8p's `hq_compound_lab.gd` preloaded the old post path and now point at
  the new one (one line each).
- **Tests:** `tests/unit/test_city3d_grid.gd` (fast): the map layer projects like the 3D camera, roofs at their 3D height, the fist-free layout, zoom / pan / minimap maths, the Grid page in 3D feeding the decal, the camera controls. `tests/unit/test_city3d_model.gd` (fast): the whole-city config and its chunk tiling,
  the deterministic chunked model, the Cell's grid, picking through chunks = every prism,
  `top_at`, building LOD and view bands with hysteresis, log-linear zoom about the cursor and pan,
  the network decal's buffers, CityView3D's layer and picking API, ambient pause.

### 2026-10-05 — Art direction — ART-5 5b landmarks
ART_BIBLE v2 §1.2 (World), §2.4, §4.1, §4.4, §6.1; ART_3_BATCH "Wave 2" 5b; references `city/round26_hq_targets/*`,
`round27_hq_targets/*`, `round31_meridian_combat/*`, `round34_rebel_cell/*`, `foundations/round2/*`; 1D's pick
(real-time Godot 3D); 8p's export convention (`rebel_cell.art_export/1`).
- **Blender 5.2 headless from the concept generators.** `tools/art_pipeline/city/` (v1): `concept_r31/` holds the round
  31 builders unchanged (target_corps + heroes24–31, ported from art-pass 097a6c0); `landmark_build_v1.py` is the port
  of `hq_scene.py` (same seeds `2525 + job`, same reference cameras) that exports instead of compositing a city;
  `landmark_crest_v1.py` / `landmark_district_v1.py` port the round 34 crest (`map34.Crest.zone`, the blackout ring,
  the DISPATCH glitch bands; art-pass d14b8f6); `build_landmarks_v1.py blender|post|sheets|assemble` runs it all. Builds
  are deterministic (same bytes on a rebuild).
- **What is built, per bible 4.4:** Meridian container castle on texture A (round 29 t1), moat, gantry keep, rail yard
  and the round 31 crane + train loop; Solace lit helix (down-lights, cones, spotlight, 12-frame chaser) + the SOLACE
  GENERAL hospital Site; Halcyon seven-tier Civic Core with the scanning eye (own pivot, ±55°, searchlight) + Halcyon
  Court with the Justice statue (the round 27 default Site); Orbital silo crescent with the doors 1.6 below the rim,
  closed and open (rocket) as two state nodes + the OC-TV Site; REBEL_CELL district: a normal street grid whose window
  lights draw the tucked-thumb fist (home 70 %, DISPATCH 90 % with the glitch rows), detail lines on windowless
  buildings, the blackout ring and the reveal. Meridian's regular Site (the depot) is not one of the five landmarks
  and is not exported; it is one more job in `landmark_spec_v1.JOBS` when the Sites need it.
- **glTF is the primary and only export (coordinator, after 1D's pick); the 2× day/night layered sprites are dropped.**
  They would need their own render, holdout passes and finish per corp, mode and animation frame and would only
  serve the baked technique 1D did not pick. 5.9 MB in all (Meridian 1.27 MB, Solace 1.34, Halcyon 0.44, Orbital
  0.63, REBEL_CELL 2.38), uncompressed (Godot imports no Draco or meshopt).
- **On 8p's convention (`rebel_cell.art_export/1`):** no normals (the toon shader takes the facet normal from screen
  derivatives; rendered with and without normals: no difference); COLOR_0 linear = face colour × tone (0.86–1.12);
  alpha = a part value 0.55–1.0 written to ROUGHNESS (part edges ink as material edges; ≥ 0.5 marks a building for the
  spike post) or, on windows, the window's own seeded value; materials named by role `lm_toon`, `lm_lit`, `lm_neon`,
  `lm_win`, `lm_sign` (as 8p's `hq_*`) plus `lm_beam`, `lm_toon_lines`, `lm_win_ring`, `lm_win_lines`,
  `lm_win_fist_home`, `lm_win_fist_dispatch`. Manifest per corp (`assets/city/landmarks/<corp>/manifest.json`):
  source (scripts, commit, `scripts_sha256`), settings, origin and footprint (Godot frame) per landmark, the lot
  rectangle and overhang, triangles per role, animation, reference camera, files with sizes and sha256.
- **Origin convention for 5a:** glTF x = lot x, z = lot y (`CityIsoCamera.lot_to_world`), 1 unit = 1 BU, +Y up; an HQ's
  origin is its plaza's ground centre, to sit on the centre of its 10 × 10 HQ lot rectangle; a Site's on the centre of
  its 6 × 6 lot block; the district's at the palm. Some landmarks overhang their rectangle (`lot_rect.overhang_bu`:
  Meridian's rail yard runs ±90 BU along x).
- **Moving parts as glTF animation, written by `gltf_anim_v1.py`** (the exporter's action handling is not used):
  Meridian `loop` (3.0 s: 17 crane poses as step flipbooks over one shared portal, the train once, slid along the
  track, its new container from frame 9 to 14, motion streaks 11–14); Solace `chaser` (12 × 90 ms); Halcyon `eye_scan`
  (12 × 110 ms, rotation about +Y). The rest pose is the concept's still (Meridian frame 6, chaser frame 0; the eye at
  frame 0, its still angle 28° is in the manifest).
- **Locked Site renders face lot +y:** the round 26–27 `build_at` meant to turn new Sites 45° but turned only their
  sign objects, so the references show them unturned; the export matches the references (front +z), with a readable
  sign (the references' was turned into the wall).
- **Smaller than the concept, same picture:** signs at curve resolution 2 (the default 12 made a sign heavier than its
  building); Orbital's sign once on the root (not per state); the district's walls 4 jittered triangles each (the
  city's 1.7 BU facet grid is the CityModel shader's job) and mid-rise heights (7–27 BU, a few to 51) so the fist
  reads; the fist's panes 1.3 × 1.2 BU and `LandmarkLook.fist_gain` 1.8 (map34 lights the crest denser and spills red).
- **Godot side (no view changes):** `assets/city/landmarks/landmark_toon.gdshader` / `landmark_beam.gdshader` (the
  spike's 3-band light() and ramp × the corp `TINT`; the reveal: ring windows off as q passes their value with a
  ±0.12 flicker band, detail-line windows off, line buildings darken), `LandmarkLook` (`landmark_look.tres`: night and
  cool-day ramps, gains, the concept's numbers; `lit_emission` 0.25 as 8p, since the spike post blooms every bright
  pixel) and `LandmarkMaterials` (role → material, `set_reveal`, `show_dispatch`). The crest mask
  (`rebel_cell_crest_mask.png`, R home / G DISPATCH zone, B ring weight, on the iso screen plane; mapping in the
  manifest) is for the CityModel's window shader, so the fist can be drawn on the city's own buildings.
- **Validator hook and test:** `tools/landmark_asset_checks.gd` from `validate_content.gd` (every corporation, schema,
  files, sizes, sha256, stale pipeline); `tests/unit/test_art5_landmarks.gd` (fast): every glTF loads headless with
  landmark roles only, loops with their lengths, Orbital's states, the district's reveal meshes, the mask imports.
- **Renders read:** `tools/art_pipeline/city/landmark_review.tscn` (windowed, one launch, 26 shots) next to the Blender
  concept finish and the references in `docs/art_review/ART-5/5b/` (`.gdignore` in `ART-5/`). Halcyon, Orbital and
  Meridian match closely; Solace's strands read violet-grey in Godot where the concept's emission-pass bloom and the
  stand-in city's lime lanes tint them lime (the spike post blooms only what passes its threshold, so dim seams do not
  bloom); the fist reads in Blender and more faintly in Godot on the bare district, where it needs the lit city around
  the blackout ring for contrast.

### 2026-10-05 — Art direction — ART-7 3B netrun presentation
ART-7 wave 1, 2D parts (ART_BIBLE v2 §4.6, §1.2; D13 and D14 confirmed), on the **current**
route view (the route still sits on the neon city; wave 2 moves it onto the 3D city).
- **Route look (3B.1, 3B.5): `RouteOverlay`** (a CityMapOverlay subclass, so the route sweeps,
  label layout, moves and hover keep their rules). Option A: every node is a vinyl sticker in
  its kind's colour (white die-cut, ink keyline, StatIcon symbol), one ring carries the state:
  lime walked, orange selectable (soft glow, orange number chip), white not yet, `RING_CUT`
  grey cut off; each state also has its own ring style (§5.1 never colour alone, the Group 1
  naive-reader audit P2): walked a double ring, selectable a thick solid ring with its glow
  and number, not yet dashed, cut off dotted and struck through (`RouteOverlay.RING_STYLES`,
  the key's swatches draw the same `draw_state_ring`). The final Rack carries the red grease-pencil TARGET circle and word (the word
  is the node's map label, so the layout keeps it off other labels). "You are here" is the
  operative's pink sticker pinned over the node. Transit v3 cables: each link runs along the
  city's two ground axes with one turn (straight segments, no street-following); walked = solid
  lime, live = crawling orange dash, later = white dash, cut = grey dash. **Call:** one turn
  per link (no 45° jog, no bridge hops; crossings are not avoided): the hops need the real
  city's cable router (wave 2). **Projection seam:** everything the route draws goes through
  `RouteOverlay.cable()`, `_axes()` and CityMapOverlay's `icon_pos` / `_to_local`; the 3D city
  replaces those, nothing else.
- **D13 hidden nodes:** only walked nodes, the choices and the TARGET are drawn; hovering the
  legend strip shows all (`show_all`, `route_node_reveal` fade); the pointer reveals one hidden
  node within 40 px; `Settings.always_show_all_nodes` (additive key, default off, Options >
  Display row "Always show all nodes on the netrun map"; 4C restyles that panel). The pad
  reads "OPTIONS > DISPLAY: SHOW ALL NODES" on the strip instead of the hover words.
- **Route key:** the RouteLegend is now the foot strip (stickers COMBAT / ELITE / EVENT / SHOP
  / RACK as the map draws them, the four rings, the D13 cue), in a row of its own under the
  map, scaled down to its row at big text. `COLOR_KEYS` are now walked / next / later / cut
  (were here / next / later / visited / corp). Test edit: `test_horizontal_pass24_city` reads
  the key's rows under `strip` (the rows moved into the strip's HBox).
- **Calm Heat (D14, GDD 4.3 only):** a choice Heat has made harder carries a thin `HEAT_B`
  ring with a red and a blue light circling it (`route_heat_orbit`) and its effect as a
  second label line: fights (Routers, Racks) "HEAT: +N RESISTANCE" from
  `HeatRules.active_modifiers` ENEMY_RESISTANCE; the Mainframe "HEAT: SHOP STOCK -N" from a
  SHOP_STOCK complication. From NOTICED up two slow searchlights sweep the map
  (`route_searchlight`). **Not drawn (needs a rule):** "HEAT: +1 ELITE" per node: the elite
  frequency modifier changes map generation, not a node, so no node can honestly carry it.
- **Panels (3B.2):** `OperativeDossier` on 1B's CorpPaperPanel (letterhead = the target corp;
  Courier Prime fields: subject, class, rank, HP, RAM, wheel, hub core (the rank's upgrade
  else the wheel's own hub), deck, the class's raid station bonus via Codex; AT LARGE and
  "HEAT n: BAND" stamps). It folds to a compact file when the full one would take more than
  24 % of the screen's width (text 2.0 at 1280). `RouteNodePanel` on 1B's DecryptedHoloPanel
  (no full-screen scrim over the map): title (node word // layer), tier (the run's Site tier),
  type, rewards from the config (Cycles range x reward scale, Firmware, Rack Schematics by tier,
  Daemon / the Site's objective), Heat on entry and Heat marks. **D14 "only when decrypted":**
  under GDD 4.2 every node's kind is known, so every node the map shows is decrypted; the
  panel follows the hovered node or the focused ROUTE choice. DECK / MENU stickers from the
  reference are not added (VIEW LOADOUT and the pause menu already do that; ART-10 screens).
- **Jack-in (3B.3): `Fx.jack_in_link`** (`JackSequence`), used by `RunManager.go_to_netrun`
  with `RunManager.jack_link(site)` (the owned end: home or a claimed Site linked to the
  target, lowest id; the link's screen points from the HQ's City Grid overlay; the operative's
  slice colours). Beats: 1B's CrtTerminalPanel types `> jack --from A --to B`, routing,
  handshake, CONNECTED (`jack_terminal_type`); binary rain along the link only
  (`jack_link_rain`, drawn glyphs: BinaryBits flies to one target, the rain lands along a line);
  CRT collapse (`jack_crt_collapse`); the wheel slaps on and spins (`jack_wheel_slap`,
  `jack_wheel_spin`); the lens (`jack_lens`): the wheel swells until its hub covers the screen,
  the switch and the CONNECTING line happen under it, then the hub opens onto the run and the
  ring flies past. One press skips (the JackInputGate passes the press to the sequence; the
  press still reaches no screen): the switch at once, then the run. Reduce effects / reduce
  motion / headless / an entry off / no link: the old `jack_in` (its fade and end state). Plain
  `Fx.jack_in` (jack out, the tests) is unchanged.
- **Node backdrops (3B.4):** round 36's tower rooms (r32_scene.py, Blender 5.2 headless, the
  room camera per kind: fight, elite, event, shop = modem room, rack; recipe in
  `tools/art_pipeline/netrun_rooms/`: `make_rooms.py` builds rooms3b.py from the tag's
  r32_scene.py, `finish_all3b.py` runs the tag's finish.py) rendered per corp (the
  container families mixed 55 % toward the corp hue; Meridian as drawn) and finished with the
  round 32 Cv2 + E finish at 1280x720, JPEG q82, 25 stills, 2.7 MB in
  `assets/backdrops/netrun/<corp>_<kind>.jpg`. `NodeBackdrop` shows the current node's room
  behind its event, shop and loot pages (`_update_node_backdrop`); the fight keeps its arena.
- **Motion (union):** `route_node_reveal`, `route_heat_orbit`, `route_searchlight`,
  `jack_terminal_type`, `jack_link_rain`, `jack_crt_collapse`, `jack_wheel_slap`,
  `jack_wheel_spin`, `jack_lens` in ui_motion.tres, REQUIRED_IDS and the lab (`netrun
  route_heat`, `jack_link`). Capture walk: `tools/design_lab/netrun_states.tscn` (one windowed
  launch, every state). Tests: `tests/unit/test_art7_netrun.gd` (fast).
- **1B kit:** the dossier's sheet is `CorpPaperPanel` (letterhead = the corp's mark word, the
  sheet's letterhead is one fixed-size line), the node panel's plate `DecryptedHoloPanel`
  (scrim off: it would darken the map), the jack terminal `CrtTerminalPanel` (typed on the
  sequence's own clock). Not used: `BinaryBits` (it flies bits to one target; the rain lands
  along a line, drawn in the same mono glyphs) and `GreasePencilMark` (a Node2D of Line2Ds; the
  route redraws per camera frame in the overlay's own canvas, so the TARGET circle and word are
  drawn there in the pencil colours and face; the walked path is the Cell's lime line, not
  pencil, per §4.6).
- **Big text:** the dossier folds (above); the node panel widens to 1.3x at most and shows only
  when the ROUTE column has room under the window (the choices come first).
- **Files outside 3B's area (smallest change):** `scripts/autoload/fx.gd` (jack_in_link,
  _link_switch, the sequence node), `scripts/ui/kit/jack_input_gate.gd` (on_press),
  `scripts/autoload/run_manager.gd` (jack_link, the launch call), `settings.gd` /
  `settings_panel.gd` (the D13 key and row), `motion_lab.gd` (demos).
### 2026-10-05 — Art direction — ART-9 4A shop, rewards, events
ART_BIBLE v2 §1.2, §4.10, §4.11; references `docs/art_reference/shop_events/` (round 12 F1b
facade, round 33 sign v4 and `slice_wheel_offscreen`, round 34 `shop_v5`, rounds 31–32 reward and
event screens). Presentation only: prices, removal, rewards and event rules are unchanged.
- **Facade bakes.** `tools/art_bake/mainframe_facade_bake.py` runs round 33's Blender scene
  (F1 Tenement, `MF_VAR=b`: magenta spill, two wall-to-wall cables) per state (day, night, rain)
  three times with one seed (dark sign, blue sign + blue spill, red sign + red spill) and writes
  `assets/backdrops/shop/facade_<state>.webp` plus the two spill layers (1280x720 WebP, about
  450 KB in all). The game adds a spill layer at the sign's level over the dark facade (round 33's
  `dark + a * (normal - dark)`), so the street follows the sign. Rain streaks are left out of the
  bake and fall in the game (`mainframe_rain`; still under reduce effects). Which state a visit
  shows is a hash of the visit (night 2 in 4, rain 1, day 1): there is no time of day in the
  rules (open question below).
- **Sign v4 as baked light layers.** `tools/art_bake/mainframe_sign_bake.py` renders round 33's
  `flicker_sign.py` once per element: the dark plate, then the change each tube makes when lit
  (frame, rails, nine letters in blue and in red, the two A's as an "o"), the red glass tint, the
  soot and each dead letter's snapped glass, cropped into one atlas (`sign_layers.png`, 400 KB,
  table `sign_layers.json`). `MainframeSign` draws base + sum(level x layer) with add / subtract
  blending: exact for one tube, the halos of neighbours add. Data pulses on the traces are not
  drawn (static traces). The sign is the shop's name in the world: never translated (§1.2 "only
  diegetic signage"); `test_horizontal_pass24_screens` now checks it shows MAINFRAME.
- **Takeover.** The three LOCKED sequences play in round 33's frame plan (stutter into red, the
  Cell's red, dead letters drop out, dark, each word twice with a hum and a stutter between,
  the old sign flashes back), then the blue returns. Once per visit, `mainframe_takeover`'s delay
  after the warm-up; amplitude = frames per second. Which sequence: a hash of the visit. Stutters
  use `hash()`, never an RNG. Ambient: not a MotionSkip motion; off under reduce effects and
  headless (the lit blue sign is the end state). The warm-up keeps `mainframe_sign_warmup`,
  `_strike`, `_flicker` and `mainframe_trace` (now the rails lighting).
- **Spill seams.** The street's spill is the bake (the 1B `LightSpill` would light it twice);
  1B's `LightSpill` lights the pegboard beside the sign in the sign's colour at its level
  (`SHOP_SPILL_GAIN` 0.6 of the shop gain, reach 260 px).
- **The art is the concept's (designer, 2026-10-05: never redraw art the art pass made).**
  `tools/art_bake/mainframe_parts_bake.py` calls the concept scripts on `art-concepts-r43` with
  their drawing code unchanged and only crops / saves (`assets/ui/mainframe/`, 7.6 MB at the
  concepts' 1920 scale, `MainframeArt` draws them at 2/3). Visuals and their sources:
  | Visual | Source |
  |---|---|
  | Facade day / night / rain + spill layers | round 33 `scene.py` + `post.py` (Blender 5.2) via mainframe_facade_bake.py |
  | MAINFRAME sign v4, takeovers | round 33 `flicker_sign.py` + `board.py` per-letter layers via mainframe_sign_bake.py |
  | Firmware chips (normal / lit) | round 34 `fwlib.chip(id, 84)` |
  | Daemon cartridges | round 34 `shop_v5.daemon_row` (housing + `fwlib.daemon_tile`), cropped |
  | Pink foam strip and lip | `shop_v5.foam` |
  | Kraft price tags (ok / out of reach / sold) | `r31lib.price_tag("")` (no number: the price is lettered live) |
  | Pegboard | `shop.pegboard` (frame kept, hole grid cut to size) |
  | Section tapes CARDS / FIRMWARE / DAEMONS / RECYCLE BIN | `shop.dymo` (English; lettered live in another language) |
  | Stock wheel and wedges for sale | `assets.shop_wheel12` (the wheel) and `slicekit.wheel` per shop slice, cut at -30 / 0 / +30 so the read blocks stay upright; padlock `shop_layout.lock_icon` |
  | Recycle bin (shut / lid open on hover) | `recycle.scene` |
  | Clerk's face | `shop.clerk_panel` crop |
  | Loot sheet liner and kiss-cut slots | `reward.liner` (print band only), `reward.kiss_cut` |
  | Event choice stickers (plate, hover) | `event.plate_button("", "")` placed with `r31lib.place_sticker` |
  | LEAVE, FIGHT WON, SKIP, TERMINAL stickers | 1B `VinylSticker` (the port of the concept's sticker_lib) |
  | CRT windows (clerk, info strip, PAYOUT, FIRMWARE DROP, event terminal, deck viewer) | 1B `CrtTerminalPanel` inside `CrtWindow` |
  | Corp memo paper | 1B `CorpPaperPanel` |
  | Grease pencil notes and arrows | 1B `GreasePencilWord` / `GreasePencilMark` |
  | Sign light on the pegboard | 1B `LightSpill` |
  | Glyphs on objects with no baked art (new content only) | 1C `GlyphIcon` |
  Drawn procedurally, and why: every word and number (names, prices, rarity / slot lines, the
  sheet's header and foot, outcome chips: data-driven and translated; the concept bakes them as
  English pixels); the yellow rim arc on a wedge for sale and the acid focus edges (state marks
  the concept composed with ImageDraw over the art); the unaffordable padlock and pencil strike on
  a tag (naive-reader audit P2: a second cue the concept lacks); the CAM feed (the concept's feed is
  a crop of one corp target render; there is no per-event render, so the feed magnifies the game's
  own city through a BackBufferCopy); the loot sheet's peel flap (the concept's peel is the card
  sticker's own curl, which is Group 2's card); the rain streaks (the bakes leave them out so they
  can move).
- **Layout v5 (round 34 `shop_v5` x 2/3 on 1280x720).** The facade fills the screen behind the
  page; its picture moves down by what the top bar covers of the sign. Pegboard under the bar
  between the sign and the bin: CARDS, the socket list, the info strip (the focused item's name and
  what it does) with your spinner beside it (Firmware and slices still drag onto its slots);
  FIRMWARE chips in the foam, DAEMONS in cartridges. Clerk CRT bottom left (NO REFUNDS. NO NAMES.
  CYCLES ONLY., the WALLET, the price list from `campaign_config`). From text size 1.25 DAEMONS
  stands beside FIRMWARE, the clerk steps aside (the wallet joins the board) and the board may
  cover the sign; the wheel's hub moves down so its rim stays under the board. Drawn objects stop
  growing at x1.3 (`ShopItem.OBJECT_MAX_SCALE`) while their words and tags keep growing.
- **Prices.** Every item's price is its kraft tag (`BuyButton` restyled; the press still buys).
  Pricing is the current flat rule (no top-3 discount, G14). A card's tag hangs under the card,
  tied to its foot, as in `shop_v5` (resume, 2026-10-05: the concept tag's height, 28 px at 1.0,
  inside the card left a long card text no room at 1.0; `BuyButton.TAG_BELOW`, the card keeps the
  hand's foot, the row keeps the tag's room under it). test_horizontal_pass24_screens' "buy sticker
  inside its tile" and test_horizontal_pass23_screens' "the button sits on its item" now read "the
  card's tag hangs from its foot" for cards. A chip or cartridge widens to letter its price at the
  text size (its art stops at x1.3, the tag does not); a wedge's glyph spot stays inside the wedge's
  shown box at 2.0; the bin's art keeps the tag's edge above the tag. At big text the wallet stands
  under the Daemons (it sat at the board's foot, under the stock wheel's tags), and a pencil note
  (TOP 3 ONLY moves left; BIN IT never leaves its bin) is left out where it would cover an item, a
  tag, the wallet, the info strip or the spinner. The deck viewer's grid keeps room in the glass
  for a focused sticker's `card_hover` lift (the first row's card lost its top and left edge).
  Lint: `Color.WHITE` modulates are `Palette.NO_TINT`; the lint baseline lowered.
- **Slice stock wheel (option B).** `SliceStockWheel`: hub 100 px under the screen, spins in once
  (`shop_wheel_spin`, MotionSkip, `PageTransition.settle` lands it; reduce effects and headless: at
  rest); the stock wheel art turns greyed and darkened (`shaders/grey_dim.gdshader`, 60 %) with
  padlocks; the slices for sale are its top wedges in colour (ShopItem SLICE, tag on the rim). A
  wedge still opens the UPGRADE viewer (slot price as before). Pencil "TOP n ONLY" (n = the stock).
- **Removal = the recycle bin, cards only.** The bin maps 1:1 onto the current removal for cards
  (press → the deck viewer → pick → removed at the current price; drag a card onto the bin in the
  viewer). The bible's bin also takes a dropped slice: removing a slice is not a rule, so the bin
  never takes one. The crumple / fizz / lid-slam animation is not built (the lid lifts on hover;
  the viewer's `shred_feed` landing plays); proposed slice below.
- **LEAVE** is a holographic VinylSticker ("LEAVE", holo fill) over a pink "THE MAINFRAME" plate,
  with the pink EXIT glyph beside it.
- **Loot sheet (Reward A).** `LootSheet`: a dark header ("LOOT SHEET // FIGHT WON // PICK 1 OF 3"),
  the concept's liner and a kiss-cut slot under each sticker (the taken slot stays an empty
  outline), the foot line and a barcode. A pick peels (`loot_peel`: a corner flap on the sheet,
  MotionSkip) as the existing `loot_pick` flight carries the card to the deck; the rest fall as
  before (`loot_reject`, inside the sheet). The title sticker (the payout's words), the CRT strip
  `LootWindow`, PAYOUT (the run's Cycles and HP), a Firmware drop's terminal (socket list + your
  spinner), the DECK counter with a pencil "+1 = N" (true: one card), Skip. The entrance stays
  `loot_fan` (the bits-assembling entrance waits for the bits on cards: Group 2).
- **Events as drawn.** The story is in a CRT terminal (accent = the corp colour, red for
  DISPATCH) beside a CAM feed of the city (`CamFeed`, `event_cam_noise`); a corp speaker's story is
  an intercepted memo (`CorpMemo` on CorpPaperPanel: letterhead, Courier Prime, CLASSIFIED stamp,
  tape) and the terminal says INTERCEPTED; DISPATCH shows VOICE ONLY // NO FEED and says its name
  once (audit P3). Choices are the plate stickers (`ChoiceSticker`) with their outcome rows as
  framed chips (green gain, red cost, grey no change) with an up / down mark (audit P2: Heat gained
  is a cost). The stamp after the pick reads CHOSEN. The one pencil note "PLAY IT SAFE??" shows only
  when a choice changes nothing, its arrow ending on that choice (audit P3). From text size 1.6 the
  CAM feed, the speaker line and "> CHOOSE" step aside so the story and the choices fit.
- **Deck viewer** (now 4A's): the CRT glass, the glass scrim, its REMOVE drop target is the
  recycle bin; the cards stay Group 2's sticker cards.
- **Motion.** New entries `mainframe_takeover`, `mainframe_rain`, `shop_wheel_spin`, `loot_peel`,
  `event_cam_noise` (REQUIRED_IDS, lab demos `takeover`, `rain`, `stock_wheel`, `peel`, `cam`); the
  `mainframe` demo shows the sign on its facade. Nothing dropped. VFX tiers (ART-12's
  test_vfx_tiers, met at resume): the takeover, the rain and the CAM feed are T0 ambient (rain and
  CAM are loops), the stock wheel's spin a T3 moment of 1.2 s (was 1.5 s at T2); `grey_dim.gdshader`
  includes rc_common. The info strip's idle line has a pad twin (`SHOP_INFO_IDLE_PAD`); at big text
  the wallet is drawn at most x1.6 (`SHOP_WALLET_MAX_SCALE`) so it stands clear of the bin's tag,
  and the info strip is at most 0.92 x its width (`SHOP_INFO_WIDE_SCALE`) so the spinner beside it
  stays clear of the stock wheel's left tag (at 2.0 the strip shows the name and the start of the
  effect; the whole text is the item's tip).
- **One CrtWindow (merge with 4C, 2026-10-05).** 4A and 4C each built a `class_name CrtWindow`
  (TerminalWindow on 1B's CrtTerminalPanel glass); 4C's (`kit/chrome/crt_window.gd`, with the
  `> TITLE` header strip of §4.13) landed first, so 4A's (`kit/crt_window.gd`) is removed and 4A's
  windows use 4C's. Smallest edit to 4C's file: `with_kind(kind, corp)` and the static
  `kind_for(colour)` (the glass accent: FIRMWARE acid, DISPATCH red, CELL cyan / pink, else CORP).
  4A's titles drop their own "> " (the header letters it); `_crt_one_line` keeps a 4A window's
  title on one line (the strip widens to it, as the concepts draw them). The loot's strip shows
  its header line only; the loot's DECK counter is a small glass with DECK and the count on one
  line (no header strip: at 2.0 the header pushed Skip under a focused card's tip); Skip stands
  at the side column's left; the deck viewer gives up grid height when the v2 header and words
  would push it off the canvas (`DeckView._fit_canvas`, never under SCROLL_MIN).
- **Files outside 4A touched (smallest edits):** `palette.gd` (one ART-9 4A token block),
  `page_transition.gd` (settle lands the stock wheel), `outcome_row.gd` (chips; event-only),
  `buy_button.gd` (kraft tag; shop-only).
- **Tests ported (they pinned the M13 look; the behaviour they guard is kept):** test_vertical_pass2
  (event panel is a CRT terminal), test_anim6_screen_motion (event enters as glass; the sign is
  found on the screen, not the page), test_anim_r2_combat (a held choice sits on its sticker box),
  test_anim_r4_combat (loot title and strip on screen; the terminal sizes to its words),
  test_anim_r5_netrun (the story on its terminal at every size), test_anim_r6_netrun (the sign
  has its nine letters; LEAVE keeps EXIT), test_horizontal_pass20_screens (nothing sold back:
  the clerk's words), test_horizontal_pass24_screens (the sign is the shop's own name),
  test_anim_r5_netrun socket list (on the pegboard), test_horizontal_pass23_screens (a chip's effect
  is in its tip and the info strip, not on the tile), test_anim_r1_campaign (Skip beside the sheet:
  clear of every sticker). None dropped.
- Capture lab: `tools/design_lab/art9_4a_lab.tscn` (one windowed launch walks every state);
  review crops in `docs/art_review/ART-9/4A/`.

### 2026-10-05 — Art direction — ART-8 8p HQ compound prep
ART_BIBLE v2 §1.2 (World), §4.7 (HQ runs: the compound), §6.1; ART_3_BATCH "Wave 2" 8p; references
`hq/round43_hq_mechanics/hq_*_compound.jpg`, `hq/round35_netrun/hq_compound.jpg`; 1D's pick (real-time
Godot 3D, `docs/handoff/art_1/city_spike_report.md`).
- **Static compounds on the current rules, one per corporation.** `tools/art_pipeline/city/build_hq_compound.py`
  (Blender 5.2 headless) runs the round 43 exec chain (`vendor_r43/`: target_corps.py and heroes24–31/42/43,
  ported from art-pass 36d1f34, unchanged) with every G12 moving part at rest or out: Meridian's gantry keep
  stands parked (boom level, spreader up, no load) and no train runs (the rail yard stays); Solace's helix does not
  turn; Halcyon's eye stands at the still angle (28°, its own glTF nodes so G12 can turn it) without the
  searchlight cone; Orbital's silo doors are shut and the rocket is down; REBEL_CELL is DISPATCH's base (round 42
  `rebel_base`, STATE dispatch). Sync Strike, strands, switchback eye, silo loop and crane/train are not built.
  The city around a compound is not built either (ART-5's CityModel draws it): each model stops at its plaza.
- **glTF is the only export (coordinator, after 1D's pick); the layered sprites are dropped.** A day/night sprite
  set needs its own render and finish pass per corporation (passes, ink, bloom, per mode) and would only serve the
  baked technique 1D did not pick. `assets/city/hq_compounds/<corp>/<corp>_compound.glb` is 0.3–0.8 MB
  (8.6k–18k triangles), uncompressed (Godot imports no Draco), with `manifest.json`.
- **The glTF carries the spike's look as data.** No normals (the toon shader takes the facet normal from screen
  derivatives, as `city_building.gdshader` does); COLOR_0 = the concept face colour × its per-triangle tone
  (0.86–1.12, `mat_toon`), linear; COLOR_0.a = a part bit that the shader writes to ROUGHNESS (1.0 / 0.55) so the
  spike post pass inks part boundaries as material edges (the concept's id-pass ink). Materials carry the role in
  the name (`hq_toon`, `hq_lit`, `hq_neon`, `hq_win`, `hq_sign`); `tools/art_pipeline/city/hq_compound_toon.gdshader`
  shades them with the spike ramp × the corp's `target_corps.TINT` (manifest `settings.ramp_tint`).
  `hq_lit` adds 0.25 × its colour (the concept's 0.42 bloomed only in the emission pass; the spike post blooms
  every bright pixel, so 0.42 blew the Meridian towers out). The toon shader is a prototype until 1B's shared toon
  / ink material lands, like the spike's.
- **Manifest fields (shared export convention, `schema rebel_cell.art_export/1`, for 5b to reuse):** source
  (script, spec, driver, vendor tag @ sha, git commit, `scripts_sha256` of the pipeline), settings (Blender
  version, state, units 1 BU = 1 m, +Y up with (x, y, z) → (x, z, −y), tone, ramp tint, pitch 55° / yaw 135°,
  the reference camera target and ortho), origin (the compound's ground centre, to sit on the HQ lot's centre),
  footprint (min / max / size in the Godot frame), files (path, kind, bytes, sha256), triangles per role,
  materials, anchors, slot surfaces, validator. A stale export (pipeline changed since the build) fails validation.
- **Layout table (schema change, minimal):** `HqCompoundLayoutData` (`scripts/data/`), one per corporation at
  `content/city/hq_compounds/<corp>.tres`, id `hq_compound_<corp>` (found by id, so CorporationData is untouched):
  `corporation_id`, `asset_dir`, `slots_per_layer`, `layer_slots` (row-major PackedVector3Array), `central_server`,
  `entry`. Checked in `tools/schema_smoke_checks.gd` (`_art8_hq_compound`). Written by
  `make_hq_compounds.py` from `hq_compound_spec.py`, the same spec the model's anchors come from.
- **Which nodes, on the current rules.** Today's HQ run is the breach: `start_special("boss")` builds one node,
  the Central Server. A full run map at the HQ (GDD 4.2: 7 layers of 2–4, the last one node) is covered too, so
  the table holds whichever comes first: a row of `map_nodes_max` slots for each layer before the last, the last
  layer (and the breach) at the Central Server. `HqCompoundLayout` (pure, `scripts/core/`) maps a node of layer L,
  index i of n to slot round(i·(slots−1)/(n−1)) (n = 1: the middle slot), so a layer spreads over its row and the
  generator's non-crossing index order stays left to right on screen. Test: `tests/unit/test_hq_compound_layout.gd`.
- **Slots sit on the model.** Each slot is snapped onto the first surface under it at build (ray from 3 BU above
  its nominal height, lifted 0.3); never on a G12 moving part (train, trolley, doors, rocket). Rows are sorted left
  to right at the city azimuth and kept at least 50 px apart (with the server) at the reference framing (1920 px
  wide); `validate_hq_compounds.py` checks both. Meridian runs a south lane (wall top) and a north / back lane
  with the keep portal and house between, closing on THE MASTER MANIFEST tower; Solace's six rows climb both
  strands (spacing searched for the widest gap) to THE GENOME CORE at the cap; Halcyon's rows are the six
  switchback terraces of the front face to THE PANOPTICON; Orbital's rows close in round both sides of the podium
  from the steps to LAUNCH CONTROL at the mast foot (dishes as rows 4–5); DISPATCH's rows go round the rooftops
  into the courtyard to DISPATCH CORE on the mast.
- **Validator hooks:** `python tools/art_pipeline/city/validate_hq_compounds.py` (files, hashes, glTF content,
  stale scripts, anchors, spacing, the .tres = the manifest) and `tools/validate_content.gd`
  (`_hq_compound_errors`: every corporation has a layout, the layout fits the config's map, the manifest exists for
  that corporation and its files exist).
- **Review:** `tools/art_pipeline/city/hq_compound_lab.tscn` (windowed, one launch for all five) renders each
  glTF with the spike's light, ramp and post pass at the compound reference camera (55°, its ortho) and the
  anchors over it; crops beside the references in `docs/art_review/ART-8/8p/` (`.gdignore` in `ART-8/`).
  Read: Meridian (tan / orange towers, dark rust walls, hazard-striped boom over the rail yard, the server tower
  on the left corner as in the reference; no train, by rule); Solace (grey-green helix with lime trim and lit
  rungs over the lit podium rings; the reference's crossover walkways are G12); Halcyon (violet terraced ziggurat,
  lit terrace edges, the eye's ring on the pylon; windows read whiter than the reference's warm ones under the
  spike's window gain); Orbital (steel-blue podium, caution ring, dishes and lattice mast match closely); DISPATCH
  (the red-lit base; the round 43 ideas play in the Tokyo canyon instead, see the open question).
- No view changes; no mechanics; no change to how HQ runs play.

### 2026-10-05 — Art direction — ART-2 2A wheel stack

ART-2 2A (ART_BIBLE v2 §3.2–3.8, 3.10, 3.16, 3.19, 6.2): every wheel wears the D4 "Lens & rail"
frame and the family C "Screens & Data" slices, ported from the round 41 recipes on
`art-concepts-r43` (slicelib.render_slice, frames._d4 / blade / telemetry / banner, d4corp,
ringlock, skins / scenes18). Decided by the implementer:

- **One disc pass per wheel.** `WheelDisc` (a quad under the view, `shaders/wheel/wheel_disc.gdshader`)
  draws the radial layers in the round 41 order (screens, ring extension, tier, state wash, bezel and
  rail tint, threat ring, inner ring, hub CRT, the lifted slice and its cream outline, the glass
  crescent); `WheelView._draw` keeps the upright and line work (read blocks, badges, rail text,
  blades, HP arc, banner, lugs, hub words), and `WheelTelemetry` scrolls the ring as a node (no
  redraw). §6.2's Polygon2D-per-slice layout is replaced by this single pass (one material per
  wheel, no per-slice nodes); profile below.
- **Screens are baked, not hand-written shaders.** `tools/art/bake_wheel_screens.py` runs the
  concept recipes unchanged (fonts remapped to the shipped faces: Consolas → Share Tech Mono,
  Bahnschrift → Anton / Plex) into 12-frame flipbooks per kit (`assets/wheel/screens/`, 10 rows:
  the 9 slice types in `RC.SliceType` order + the corp special); corp kits add the upright corp
  scene atlas (round 16). The loop is `wheel_screen_loop` (T0, 3 s; frame 0 under reduce effects).
- **Glyphs** come from 1C's atlas through one seam (`WheelGlyphs`; cells decoded once into outlined
  coverage textures so one `_draw` can stamp many). The five corp crests are not in the atlas yet:
  interim PNGs from the round 15/18 recipes in `assets/wheel/glyphs_interim/` (`tools/art/bake_wheel_glyphs.py`).
- **Kits** (`WheelKit`): theme = player or the enemy's corp; tier by rank (regular I, elite II,
  boss III); tier colours from `Palette.corp_color` / `corp_secondary` (the player: RESIST_GOLD /
  PAPER); material tables (bezel bases, segment colours) stay in the shader as recipe material, not
  UI tokens. Boss phase 2 = hot threat ring, phase 3 = overdriven screens + bolted armour plates
  (round 14). Bosses without their own hub glyph use the bible's enemy-hub emblem by boss.
- **The rail reads `OVERFLOW 12 // PERFECT //`**: the recipe's kind word (ATK, CRIT ...) is a pre-rename word the names pass bans from player text, so it is dropped.
- **Tier I screen gain is 1.0, not 60 %** (§3.7): the combat v4 mocks show tier I screens at full
  gain and at 60 % the slices read black at combat size; a `screen_gain` of 1.6 stands in for the
  recipe's bloom pass. Tiers are a game to-do; only rank tiers show.
- **Geometry:** the view's radius is the slice rim (R_OUT 360 master); hub R_IN 130 (`BAND_SHARE`
  now 0.639), the needles' room over the rim stays the old 0.34 share (`ABOVE_SHARE`, layout
  unchanged); HP arc 6–26 master beyond the frame, the HP number 10 px lower (`HP_TEXT_GAP` 54).
  Badges hide under r 60 px and their ×1.5 / ×0.5 tags under r 100 px (720p; §3.8's 150 at 1080p).
  No status stacks exist in the game, so no ×N tab is drawn.
- **Precision landings** (`play_precision`, called by combat_scene's landing beat for the player's
  needles): PERFECT gold jaws (`precision_latch`), GOOD tick ring, WEAK sparks + stutter
  (`precision_stutter`), the word holding then leaving as 0/1 bits (`precision_word`); the slice
  flash / dim in the disc. The existing Perfect inversion, freeze and NULL static are kept.
  Reduce effects: the rail's tier colour only.
- **Hub states:** LOCKDOWN = cyan bit waterline + plate + turns while Hub Breach holds, draining on
  `hub_lockdown_drain`; the player's defeat drains the core into falling bits (`hub_defeat_drain`)
  before the stamp, which now says FLATLINED (round 40).
- **Profile** (worst-case fixture in the real combat scene, `tools/design_lab/wheel_lab.tscn --case=worst`,
  1920×1080 window, `profile_frames.gd`): mean 3.8 ms a frame for the whole screen, GPU 1.15 ms,
  render CPU 0.79 ms (budget: wheels + FX ≤ 4 ms).
- Seams for 2B (attachments): `art_scale()`, `frame_master()`, `window_radius()`, `slice_deg()`,
  `active_slot()`, `badge_spot()`, `WheelFace.at/axis`, `WheelFace.R_*` zones; the firmware square
  and satellite tokens are left as they were for 2B to replace.
- **On 1B's kit:** the disc shader includes `rc_common` (its clocks stop under the `reduce_effects`
  global as well as on the view's own gate); the landing word is a `VinylSticker` (yellow PERFECT,
  white GOOD, yellow WEAK x0.5) that slaps and `dissolve`s into `BinaryBits`; the defeat's core bits
  are a `BinaryBits` burst from the hub falling past its bottom edge. The slice screens stay their
  own polar CRT in the disc pass rather than `CrtTerminalPanel` (a rectangle panel can't bend into
  the wedge; the recipe's scanlines and vignette are the locked slice look); the LOCKDOWN plate stays
  drawn at hub size for the same reason.
- **Seams taken over from 2C:** `WheelView.hp_arc_spot(frac)` (the HP arc geometry, replaces 2C's
  copy); `rgb_split` (the crit's RGB split on the disc only, master units; off under reduce effects)
  and `pixelate` (the disc in cells, for the defeated pieces) on the view, pushed to the disc;
  `wheel_texture()` (a one-off readback of `wheel_rect()`, null headless) for pieces that need the
  wheel's pixels. The standing guards after their effect: DEFRAG bricks in three courses on the side
  facing the foe (the defend rule), SANDBOX hex plates beyond them, the `>>` EVADE token on the rim,
  each with its amount; they show whenever the state holds block / shield / evade (reduce effects:
  they simply stand).
- **Group 1 audit P2s.** (1) One glyph source for a slice: `SliceIcon.draw_icon` / `draw_on_slice`
  (every caller: wheels, tags, cards, the FX layer, spinners, Mainframe tiles) now draws 1C's atlas
  glyph through `WheelGlyphs` (`glyph_table.tres`); the drawn vector icons are gone, and the slice
  text symbols (✦ ▲ ■ ...) are dropped from the odds chips (combat_scene) and the Codex titles.
  2D and 2A share that one call (`SliceIcon.draw_icon`, or `WheelGlyphs.draw` with a table key;
  `GlyphIcon.make` for a node). The status chips' text symbols (☠ ⚡ ⌗ ✺) are the tags' layout (2D).
  (2) The boss HP arc's gold ticks are the D4 phase pips (§3.2, §3.16): each now carries its `P2` /
  `P3` label (the recipe's), and hovering the arc says "Gold mark P2: phase 2 starts at 66 % HP";
  the lime target reticle round the target wheel got its own tooltip.
- **Files outside 2A:** `scripts/ui/combat_scene.gd` (2D: the `play_precision` call in the landing
  beat; the odds chips without the text symbol), `scripts/ui/kit/slice_icon.gd`, `scripts/ui/kit/codex.gd`
  (the glyph source), `scripts/ui/kit/materials/vinyl_sticker.gd` and `scripts/ui/fx/fx_draw.gd`
  (1B / 2C: their inline tween shapes named, so `test_anim_r6_rules` passes), `tools/design_lab/motion_lab.gd`
  (demos), `tools/design_lab/wheel_lab.*` and `tools/art/*` (new).
- No test dropped. Captures: `docs/art_review/ART-2/2A/`.

### 2026-10-05 — Art direction — ART-2 2D HUD
ART-2 Group 2 area 2D (ART-4; ART_BIBLE v2 §3.1, §1.3, §4.13; refs `hud/round41_wheel_stack/combat_typical_v4`,
`hud/round22_combat_fx/send_it_sticker`, `menus/round33_ui_chrome/abandon_dialog`, `ui_kit`). D15 built on its plan
default, since confirmed by the designer. Views only: no rule, number or content changed.
- **D15 result chips** (`ResultChipModel`, `HudResultChips`, placed by `HudWheelLayer`): beside each wheel's HP, in the
  bible's order `[−N]` red boxed (HP its hits and CORRUPTED bites take; a skull when lethal), `(N shield)` blue (what
  block and shield absorb), `+N shield` green (block and shield gained), `+N HP` (healed), `+N evade`, `−N RAM` (RAM
  spent or drained; the turn's refill is the TURN banner's, not a chip), `±N heat` (the operative, scaled as the
  netrun applies it), `±N HP` (any other HP change: a boss phase), `<status>×N` (statuses put on its slices; `×glyph`
  for a clear). A random roll (a random card, a respin, a random slice pick) shows `?` and its odds in the breakdown,
  never the roll (GDD 2.10). The chips preview the **resolve** (the session's `resolved_state` and the events before
  `turn_start`): the next turn's start respins at random and is never previewed, so a boss's turn-start passive
  (Customs Seal +4 shield, Auto-Renew) shows on the next turn's chips, not this one's. Hover = the breakdown tooltip:
  each attacker's landing (slice and aim) and the HP it takes, what the guard absorbed, `= −N HP (from -> to)`, what
  the wheel itself lands on, every chip in words, then every line the old tag carried ("ALL RESULTS: …" and its
  notes), a hovered card's "YOUR <CARD>" and "Before this play: …" first.
- **The forecast tag and the NEXT plate are off** (WheelView.hud_results): the tag model (`intent`) stays as the
  breakdown's source and the replay's tick list; the chips hold through a SEND IT replay, tick as the replay does each
  one and fade, on the tag's own entries (`forecast_tick`, `forecast_fade`, `intent_flip` for a change flipping in;
  MotionSkip passive; reduce effects / headless = end state at once). **What did not fit on the chips** (carried by the
  breakdown tooltip only): the landing title (slice · aim dots: the wheel shows its landing, 2A §3.19), HUB BREACH,
  PHASE N, +N NEEDLE, NEW SLICES, RESIST a→b, DOWN / VICTORY / DEFEAT (the lethal skull says it on the chip), the
  satellites' own results (2B's satellite plates), "PUTS ☠ ON YOU" (the victim's status chip says it), the run results
  (DRAW, CYCLES, SCHEMATICS, FREE NUDGE NEXT, DAMAGE ±, +N DRONE, 2× NUDGE CARDS NEXT), the WAS row and the play tape.
  Proposed slice: a second, smaller chip row for run results if the designer wants them on screen.
- **Nudges above the wheels**: WheelView in HUD mode places its arrows on one line above the disc (CCW left, CW right,
  inner ring further out with a dot) and keeps hit-testing them (clicks, drops, tooltips unchanged); HudWheelLayer draws
  round glass buttons rimmed in the wheel's colour with 1C's `picto_spin_ccw` / `picto_spin` glyphs and the key under
  the driven pair. The line grows with the text up to 1.3 (`NUDGE_SCALE_MAX`, BIG_TEXT_RADIUS_KEEP holds). **Boss keys
  A / D: not bound** — the nudge keys drive one wheel and W switches own / target (H23); separate A / D binds would be a
  new rebindable action pair (Settings.REBINDABLE, the rebind UI, pad map): logged under Open questions, the W switch
  stays.
- **Bottom left**: the CELL // CLASS name sticker (HudNameSticker, pink vinyl, the operative's name and the class;
  "CELL" in the dev fight) overlapping the RAM terminal panel (RamBar restyled: "RAM", the count as a live number,
  cyan pips; every RamBar motion kept). At text 1.6+ the pair moves to the notes column's foot so the hand keeps its
  room. Deck / discard counters of the reference are not built (2C's piles own those spots).
- **SEND IT** (SendItSticker, a DripButton subclass carrying 1B's VinylSticker art so every SEND IT motion entry and test API stays): Anton in the
  sticker colour, light top, keyline, extrude, white die-cut, rest gloss, hover lift ×1.05 with the gloss sweep
  (`drip_halo`), press squash (`send_it_press`), the shadow snapping in (`send_it_drips`), the first slap
  (`drip_grow`), disabled grey with RESOLVING..., focus a lime die-cut; over the washed-out mono `EXECUTE` with
  `> turn_resolve.exe [Space]` under it (the key only above text 1.3). The next step (LOOT / CONTINUE / JACK OUT) is the
  same sticker over `PROCEED`. 1B's vinyl material plugs in at `HudSkin.vinyl_material()`.
- **RESPIN / UNDO** are TerminalChips (a StickerButton subclass): the verb in mono caps over its cost and key, `>`
  caret on hover, F's focus brackets; the undo block is UNDO greyed with KitState's lock tick (D12), never a word.
  Side by side up to text 1.3, stacked above it.
- **TURN banner**: a terminal panel centred at the top, "TURN 3 | FREE NUDGE 1" in Anton over the key-hint line (the
  status line no longer repeats the turn; `banner_text()` reads both).
- **Item 2 (map HUD / top bar)**: HudStats tags are terminal plates (dark glass, cyan edge, mono caps name, Anton
  value, no tilt or tape); layout, fitting, bumps and refusals unchanged.
- **Item 3 (kit)**: Toast is a terminal strip (cyan edge for a note, HARM edge and no-entry mark for a refusal);
  UiTip.make has a `> TITLE` mono header over a cyan rule and the body in Plex; ConfirmDialog is a HudDialogPanel
  (`> CONFIRM // TITLE`, CANNOT UNDO in HARM when destructive) with the question in Plex, a yellow CANCEL vinyl
  sticker (default focus, left) and the pink verb sticker (right), each with its caption; F's scrim, modal motion and
  focus trap unchanged. The quit confirm reads QUIT / CANCEL. There is no in-run "abandon run" flow on main: the
  dialog kit carries the look; the pad hold-to-confirm (0.8 s) stays a proposal (not built). The tooltip delay (350 ms)
  is a project setting (project.godot is not ours to touch): left as is.
- **Tutorial** (tutorial_overlay.gd, given to 2D): a TerminalNote with TerminalButton Next / Skip; its words name the
  chips and the nudge buttons instead of the tags, NEXT plate and curved arrows.
- **Seams**: HudSkin is the one place for colour roles (palette v2: STICKER_COMMIT / SAFE / DIE_CUT,
  LIVE_NUMBER_RIM), faces, the terminal panel, the 1B material seam (vinyl, CRT) and the 1C glyphs (atlas nodes:
  picto_block, picto_ram, picto_hp, status_*, picto_spin*; drawn marks for heat and evade, which have no atlas glyph).
- **Tests**: `tests/unit/test_art2_hud.gd` (D15 sweep: every enemy × seeds 1/5/9/13, SEND IT and a card's hover, each
  row equal to the model run on the real resolve, HP change, absorbed, gained and RAM equal to the real events, a
  random status announced is one that landed; the chip format and order; the row beside the HP with its breakdown;
  hold / tick / fade and one-press skip; end state without motion; SEND IT vinyl / terminal chips / undo block / name
  sticker; nudges on one line above each wheel; the layout at 1.0 / 1.6 / 2.0). **Updated on purpose** (they pinned
  the tag look): test_visual_merge (player has chips), test_anim2_combat_motion (the chips flip), test_anim_r1_combat
  (flip-in on the chips; banner_text), test_anim_r2_combat (the entering enemy keeps its chips), test_anim_r3_combat
  (the held chips and their ticks), test_anim_r5_combat (Before this play on the breakdown), test_anim_r6_combat
  (TerminalChip; YOUR <CARD> on the breakdown), test_horizontal_pass14 (CANCEL left, verb right), pass20 (chips grow
  with text; the breakdown tooltip), pass21 (chips on screen), pass23 (the banner's translated title),
  test_art0_kit_words (the toast is terminal, not paper). None dropped; `test_the_tape_never_clips_the_tag` now has no
  tape to measure (risky, kept for 2A's wheel pass to retire with the tag code).
- **Files outside 2D's area** (smallest edits): wheel_view.gd (2A: the `hud_results` flag, the nudge line in
  `arrow_center` / `arrow_hint_rect` / `_radius`, no rim arrows, no tag, no NEXT plate); pause_menu.gd (the quit
  confirm's words); test_art0_kit_words.gd (F's toast check); test_anim_r4_city.gd (the combat Heat poster is
  hidden: Heat is 2C's HeatCity backdrop); combat_beat_fx.gd and combat_fx_layer.gd (2C, see below); zine_card.gd
  (2C's card view, the hover growth below).
- **1B switch**: SEND IT / the next step / the dialog stickers draw 1B's `VinylSticker` (child `art`, fill PINK /
  YELLOW / WHITE from the button's paint; its REST / HOVER / PRESSED / DISABLED states follow the button's KitState;
  its `slap` plays on the first show) over the system word; SendItSticker keeps the DripButton entries and API, the
  terminal line and a lime focus halo. RESPIN / UNDO and the RAM panel sit on 1B's `CrtTerminalPanel` glass (a backing
  drawn behind them; the RAM panel with the hex dump). The drawn fallbacks stay behind `SendItSticker.use_kit_art`
  and `HudSkin.draw_terminal_panel`.
- **Items handed to 2D by the coordinator (2026-10-05)**: (1) `RamBar.pip_spot(k)`, and 2C's `CombatBeatFx.ram_pip`
  reads it (its copy of the old chip geometry is gone); (2) damage numbers draw with 1A's `UiTheme.live_number()`
  settings (font, LIVE_NUMBER_RIM rim, the glow in the number's colour) at their animated size; (3) a hovered hand card
  grows to `ZineCard.HOVER_SCALE` 1.36 about its foot (drawn only: slots and hit areas stay) on `card_hover`'s timing,
  its neighbours slide aside (`slide_aside`), and the RAM pips a previewed play would spend are hatched; (4) Daemon /
  firmware `trigger` events get no beat: `ResolveBeats.trigger_marks` times each on the first beat after it (or the
  result), so the schedule is unchanged (tested), and the replay calls `CombatBeatFx.trigger` (2C's `trigger_fx`, lime
  for firmware, violet for a Daemon) from 2B's DaemonRack (or the player's hub for firmware) to the player's wheel.
  Tests in `test_art2_hud.gd`.
- **Group 1 naive audit P2s (docs/handoff/m14_audit/group1_naive.md)**: pink is the action stickers' only: the
  combat's hit / loss chip colours are the one harm red (`Palette.HARM`), gains GAIN, plain counters (RAM, Heat) neutral;
  the D15 chips never draw pink. Hand cards fit their body text (`fit_whole`) and never draw it under the 12 px
  caption floor (ZineCard `FIT_MIN_TEXT` 12, the line step follows the font); what does not fit ends in an ellipsis
  and shows whole on the hover growth and the tooltip. The tutorial keeps a margin of lines so a page never cuts
  mid-sentence, and says how it goes on in words ("Press NEXT to go on." / "More on the next page" / "Do it in the
  fight to go on (or press NEXT)"). The tutorial fight is the standalone fight (no run): it has no run top bar to
  show; its turn, nudges and RAM are on the TURN banner and the RAM panel (asked under Open questions if a run bar
  is wanted there). Cards grow on the pointer only (a pad's focus lifts the card without the growth, so the
  focused first card never covers the HP chips). The HUD's numbers stay Anton on boxes / panels, distinct from the
  mono bits.

### 2026-10-05 — Art direction — ART-11 4D campaign end
ART-11 area 4D (Group 4 brief `docs/handoff/art_4/ART_4_BATCH.md` 4D.1–4D.3; ART_BIBLE v2 §1.2,
§4.8; refs `docs/art_reference/campaign_end/round20_raid_world/campaign_lost.jpg`,
`round21_raid_world/campaign_dossier.jpg`, `raid/round23_raid_ui/interactions_gifs/26_home_breached.frames.jpg`;
generators on tag `art-concepts-r43`: round 20 `lost20.py`, round 21 `dossier21.py`). Presentation only;
no rule, schema or save change. New views in `scripts/ui/campaign_end/` (one class per file).
- **4D.1 Campaign lost = option A, ransomware lock (`RansomLock`).** BREACHED is the cause (ruling
  6.2): a lost campaign (outcome LOST: the home server at 0, after a raid's BREACHED or a run's
  HOME FELL) shows the lock before the dossier. The winning corporation's house style
  (`CorpHouseStyle`: hue `corp_color`, accent `corp_secondary`, a dark back, a motif, the head-line
  face) and verb: PROCESSED (Halcyon), RECLAIMED (Meridian), TREATED (Solace; the concept sheet
  stamped STERILE, the bible's locked verb list wins), DE-ORBITED (Orbital), OVERWRITTEN (DISPATCH,
  which signs its own notice and keeps Share Tech Mono, §2.9). The takeover is a screen shader
  (`shaders/ransom_lock.gdshader`: tearing and RGB split as the home server falls, the wipe with a
  scan edge recolouring the city in the house hue and motif, the CRT collapse at the cut); a padlock
  stamps on every node of the Cell's network as the wipe passes it (the HQ mounts the network on the
  city, zoomed so the locks stand round the notice); the notice (house // NOTICE, reference, seal,
  head, sub line, HOME SERVER and NODES ENCRYPTED n/N with the progress bar, WIPE IN and the
  countdown, "decryption is not offered") with the verb stamped on it; the Cell's stickers on the
  glass (the CELL DEFENSE title, the Armory's defence cards, REBEL_CELL) are never tinted: they curl at
  a corner and drop off one after another. At zero the countdown holds (`ransom_wipe_hold`, a reading
  hold), then the CRT collapses and the audit dossier shows. The lock waits (bounded,
  `END_LOCK_WAIT_FRAMES`) for the city's bake before it starts; its first frame's picture is cropped
  for the dossier's prints. Hand-off from 3A: the playout's BREACHED mark plays out, `_after_playout`
  calls `show_end`, and the lock tears that same frame of the city.
- **4D.2 Campaign summary = the corporation's audit dossier (`AuditDossier`, facts in
  `DossierFacts`).** A manila folder on a desk, its tab CELL-nn / CLOSED (AT LARGE when won); the cover
  swings open about the spine. Left: three taped prints (the home server and the network cropped from
  the lock's picture, else drawn stand-ins; the crew's most troublesome operative; a won campaign's first
  print is the corporation's boss, OFFLINE), the PERSONNEL // IDENTIFIED OPERATIVES sheet (class bust,
  name and rank, struck through when DECEASED, AT LARGE (stationed: Site / reserve)), the annex (A:
  the intercepted story beats by title, their words in its tooltip; B: the profile's record and the
  next campaign's ICE cap). Right: the typed AUDIT REPORT on the house letterhead (seal, name,
  division // AUDIT n) with SUBJECT, OPERATIONS, STATUS (the verb, home server BREACHED; AT LARGE when
  won), ACTIVITY, NETWORK AT CLOSURE and the Heat trace, filed and signed by the house's auditor; CASE
  CLOSED (AT LARGE when won) stamped over it; four auditor's post-its in blue ballpoint (MOST
  TROUBLESOME, still at large, the Heat or the boss, the next ICE). Only true facts: the game keeps no
  Heat history, so the trace runs from 0 through the thresholds the campaign crossed (red dots: the
  raids they set off) to the Heat at closure; no "days" (runs instead). NEW CAMPAIGN (pink, the verb)
  and MAIN MENU (yellow, the safe choice and first focus, §2.10: the concept's grey plate is the
  disabled look) are vinyl stickers on the desk; they emit, the HQ calls. A won campaign is the same
  file in the corporation's failure: stamp, tab and status AT LARGE.
- **4D.3 Run end restyled.** The Cell's CRT window (cyan for JACKED OUT, red for a loss) with the
  verdict as a vinyl sticker slapped on the glass (1B's `sticker_slap`; JACKED OUT yellow, FLATLINED and
  HOME FELL red) and BACK TO HQ, the screen's one pink sticker verb, under it (one row: the window
  fits at 2.0); the fate, tags and Heat reason
  are kept. HOME FELL hands over to the HQ's lock.
- **Materials (Group 1 merged).** Courier Prime (`Palette.paper` / `paper_bold`, 1A) types the
  corp paper; the house accent is 1A's `corp_secondary`. 1B's `VinylSticker` is every Cell sticker:
  the lock's title, defence cards (object stickers framing a `DefenceCardFace`) and REBEL_CELL, whose
  `fold` (curl) and `lift` the lock drives from its own entries; the run end's verdict (1B's
  `slap`); the buttons (`VinylButton`: a Button whose rect is the sticker's body, the sticker's
  REST / HOVER / PRESSED / DISABLED following it, the lime halo on focus). The dossier's flowing
  sheets (`PaperSheet`) draw 1B's corp paper stock (`CorpPaperPanel.SHADER`); `CorpPaperPanel`
  itself places its fields by hand, so the container sheets keep their own layout. 4B's v2 portrait
  prints (`PortraitArt.draw`) fill the prints and the personnel rows, DECEASED with 4B's KIA look
  (`Polaroid` KIA values: greyed, crossed out in red pencil). Not used, on purpose: `GreasePencilMark`
  (the bible keeps grease pencil the Cell's own, true-to-the-rules marks, yellow / red; the dossier's
  marks are the corporation's auditor's, in blue ballpoint, §1.2 corp paper), `BinaryBits` (§1.2: bits
  for dissolves and damage; the lock's stickers curl and drop, never dissolve, round 20 notes), and
  `CorpPaperPanel` for the ransom notice (round 20 draws it as the house's screen takeover, not a
  printed sheet). The campaign end's own stock (manila, report, ballpoint, stamp red, post-its, desk,
  house backs) is a block of `END_*` tokens in `palette.gd` (Group 1's file, smallest edit, reported);
  `RubberStamp` (+ `shaders/rubber_stamp.gdshader`), `PostIt`, `DossierPhoto` and `CorpSeal` are 4D's.
  `TiltBox` holds a tilted piece in a container (a Container resets its children's rotation; a
  VinylSticker is held by its body, not its shadow pad).
- **Motion** (`ui_motion.tres`, REQUIRED_IDS, lab demos on the real pieces): `ransom_glitch`,
  `ransom_wipe`, `ransom_padlock`, `ransom_notice_in`, `ransom_verb_stamp`, `ransom_sticker_curl`,
  `ransom_sticker_drop`, `ransom_sticker_stagger` (a part), `ransom_countdown`, `ransom_wipe_hold`
  (a hold), `ransom_cut`, `dossier_open`, `dossier_stamp`, `dossier_note`, `dossier_note_stagger` (a
  part); the run end's verdict slaps with 1B's `sticker_slap`. One press completes the lock's takeover (every node padlocked, 00:00.00, no
  sticker left) and the dossier's opening; a press in the lock's hold cuts at once. Reduce effects shows
  the end state at once and still holds the notice to be read; headless shows no lock (the dossier at
  once) and never waits. Capture lab `tools/design_lab/campaign_end_lab.tscn` walks every end state for
  the five corporations in one windowed launch. Old motion kept: `forecast_stamp_resolve` (still the
  raid's), nothing dropped.
- **Tests changed (they pinned the superseded look):** `test_anim_r5_city`
  `test_the_campaign_end_is_a_see_through_page_with_a_verdict_stamp` → `..._is_the_audit_dossier_with_its_stamp`
  (the ForecastStamp WON / LOST and the display headline are gone; the story and profile stay as
  EndStory / ProfileFacts); `test_anim_r6_city` C13 (the dossier's motion completes with a press instead
  of the verdict stamp's pop) and C15 (the won file says AT LARGE instead of the WON stamp's icon);
  `test_anim_r5_netrun` and `test_horizontal_pass20_screens` (the ResultStamp is a VinylSticker, checked by its words). New:
  `tests/unit/test_art11_campaign_end.gd`. Dropped: the HQ constants END_STAMP*, END_WINDOW_W,
  END_HEADLINE*, END_BEAT_TITLE_FONT, END_CAPTION / END_WON / END_LOST and `_land_end_stamp`; the netrun's
  END_STAMP, END_CAPTION and `end_icon`.
### 2026-10-05 — Art direction — ART-2 2B attachments and arena
ART-2 area 2B (`docs/handoff/art_2/ART_2_BATCH.md`; ART_BIBLE v2 §3.9, §3.11, §3.13, §3.14, §3.17,
§3.21). Built on main behind seams while Group 1 (1A palette, 1B materials, 1C glyphs, 1D city) and
2A's wheel land in parallel. Tests: `tests/unit/test_art2_attachments.gd`. Lab: `tools/design_lab/
arena_lab.tscn` (windowed only; fixtures typical / worst, bloom, hover, won, per corporation).
- **Seams.** `scripts/ui/wheel/attach/` holds every attachment: `WheelAttachments` (one child of each
  WheelView, three layers in the §3.21 z-order: `FirmwareLayer` 5, `DroneDock` 10–12,
  `CardPreviewOverlay` 14), `MiniWheel`, `FirmwareSocket`, `DaemonRack`, and `AttachStyle`, the one
  place that picks tokens, glyphs and faces. After merging 1A / 1C: rarity from
  `Palette.RARITY_COLORS` / `RARITY_PIPS`, Daemon phosphors from `Palette.DAEMON_FAMILY_COLORS`, every
  glyph (slice, `fw_<id>`, `daemon_<id>`) from 1C's atlas through `GlyphBatch` (a child of each
  immediate-mode layer carrying `GlyphIcon`'s shader material; drawn firmware / sigil shapes remain only
  as the fallback for a name the atlas lacks), the rack plate is 1B's `CrtTerminalPanel` (after 1B merged).
  Trigger seams for 2D's beat and ART-3's FX: `FirmwareLayer.trigger_origin(slot)` and
  `DaemonRack.trigger_origin(id)` (global points). ToonInk / LightSpill / BinaryBits are not needed by
  these pieces (stills are baked; bits belong to the replace / destroy FX). Geometry is in master units of the round 41 stack (the slices end at 360), read
  from the view, so it follows 2A's new wheel. The backdrop is `scripts/ui/arena/` (`CombatBackdrop`,
  `BackdropCatalog`, `shaders/arena/combat_backdrop.gdshader`); `BackdropCatalog` is the seam ART-5's
  real city swaps.
- **Hooks in 2A's `wheel_view.gd` (smallest):** `WheelAttachments.attach(self)` in `_init`; a public
  `attachments` var, `rim_radius()` and `band_width()`; while attached, `_satellite_pos` asks the
  attachments (so zone_at, tooltips and FX follow the drawn drone) and the legacy satellite tokens,
  firmware marks and outer ghost arc are not drawn (`attachments == null` guards). **Hooks in 2D's
  `combat_scene.gd`:** the backdrop built over the (now hidden) WireframeBackground with
  `wheel_source = _views`; `arena_backdrop.play_won(instant)` in `_hold_victory`;
  `DaemonRack.mount(_player_view, daemon_row)` and the right-column DaemonRow hidden (it stays the
  rack's data source and the pad inspect text). Tests ported (a superseded look, not a dropped rule):
  `test_horizontal_pass22` "past the values" becomes "outside the rim"; `test_anim_r2_combat`
  `_check_satellites` skips the slice-value boxes on attached wheels (values move into 2A's read block;
  the tag check stays); `test_anim_r4_city` checks the Heat banner against the rack instead of the
  hidden row. The HP-block rules of passes 23 / 24 hold: a band slides along its slice, else steps out,
  to keep off the HP number, NEXT and LAST TURN plates.
- **Satellites and drones (§3.11, §3.21).** Collapsed by default: one band per slice outside the
  frame (master 414 + 6, 34 deep, floored at 15 px x text scale), as long as its tiles need, a tile
  per drone with its current effect (the slice its own needle reads: glyph + value) and its HP, on a
  short stem. Hovering the slice or its band, or a card aiming at a drone (its satellite zones), blooms
  the band into mini-wheels (0.22 of the host frame, floored at 26 px) on a waisted dock lobe in the
  owner's frame colour; values upright, the blade pointing away from the host with the value it reads,
  HP number and pips in the hub. Over the HP arc the dock stands outside it; in the arc's bottom gap
  (over the HP number) the band hugs the rim. Bloomed mini-wheels that would leave the view turn round
  the rim (clockwise first) until they fit. The game docks at most one satellite per slice; the
  layout handles two (±14°, wider when they would touch) for the bible's limit. Not built: parasites
  (G mechanic), replace / destroyed animations (ART-3's FX list).
- **Firmware socket (§3.9).** The die at master ρ 168 (zone 142–194), 50 master wide (floor 12 px),
  pins toward the core, octagon with 3-tone facets, lip and LED in the rarity colour (common cool
  white, uncommon cyan, rare gold, boss pink: §2.7 from Palette tokens), 1–3 pips, glyph upright;
  below 14 px it drops glyph and pips; below rim 100 px (720p) it draws 0.9x. `flash_slot` is ART-3's
  seam for the trigger cue's FLARE. "Spent" dimming of once/twice-per-combat chips is not drawn: the
  view has no CombatState (`per_combat_uses`); slice proposed below.
- **Daemon rack (§3.13).** The CRT plate on the left edge of the operative's wheel view, vertically on
  the wheel, "DAEMONS" over 40 px tiles (x text scale), 6 at most, the last saying "+N" past six;
  sigil (atlas) in its family phosphor (§2.6; DaemonData has no family field, so `AttachStyle.daemon_family`
  reads it from what fires the Daemon: Perfect, NULL slice, card / nudge = action, combat end / rack /
  netrun = run, raid = heat, else turn), rarity on the bezel; the wheel lays out right of the rack
  (`left_reserve`), idle scan bar (`daemon_rack_scan`, 2.4 s, phase per slot) and heartbeat LED.
  Fire cue is ART-3's (`fire_slot` seam).
- **Card-play preview (§3.17).** Fed only by `WheelView.ghost_rotation`, which the combat scene sets
  from `engine.preview(action)` (the forecast's path): landing slots = the slices under the needles at
  the ghost rotation, tested against the real `submit` (`test_the_card_play_preview_lands_where_the_card_lands`).
  Nine chevrons (87 master) at 1.36 x rim chase from the top needle to its landing the shortest way
  round (`preview_chevron_chase`, 1.2 s loop; reduce effects / headless: all lit, still); dashed ghost
  blades with value window and index tab (multi-needle); landing slices dashed in their program colour;
  a dashed ghost per drone where it ends up; labels "N LANDS HERE" / one "DRONE ENDS HERE" only while
  not aiming, the whole preview at 50 % while aiming; on commit the ghost rides the turning slices
  until the wheel lands (`preview_ghost` fades). The inner ring's legacy ghost arc stays (2A's ring).
- **Combat backdrop (§3.14, D17 on its default).** Baked stills, 1280x720 JPEG q84
  (`assets/backdrops/combat/<corp>_<hq|site>_<day|night>.jpg`, about 0.2 MB each) re-rendered with
  Blender 5.2 headless from the art-concepts-r43 generator scripts (round 31 `hq_scene.py`,
  `backdrop26.finish`, for the four corporations' HQs and Sites, day and night; round 34
  `run34.py` / `post34.py` for the REBEL_CELL canyon) **without** the baked wheel pools: the shader
  softens (9-tap) and darkens (to 55 %) a pool behind each shown wheel at its live position, and
  darkens bands under the top bar and the hand. Sites now render day too (the concepts had night
  only). Orbital's HQ uses the open silo at night (combat state) and the closed silo by day (the only
  day bake). A per-still `_won.png` (640x360: R the target's silhouette from an added Blender pass, G
  its own lights) drives the won look: district to 62 %, the target's lights lime with pink hazard
  stripes, a lime outline, then "OURS NOW" in yellow marker over its top (`backdrop_won_lights`,
  0.9 s; reduce effects / headless: at once; MotionSkip completes it). Calls: **day / night** follows
  the campaign's run count (odd runs by day; no game clock exists); **REBEL_CELL** is night only, its
  boss backdrop is the DISPATCH canyon and its regular one the HOME canyon (the MAINFRAME-shop Site is
  not modelled in any concept script), and winning there crossfades DISPATCH to HOME (the hijacked
  signs give way to the Cell's street) instead of a lights mask. The standalone combat scene (no
  campaign) uses the enemy's corporation. Heat on combat (§3.15) is ART-3's: `heat_layer` is its
  layer above the still. HQ-run room backdrops are not 2B's (ART-8).
- **Motion entries** (ui_motion.tres, REQUIRED_IDS, motion lab scene demos): `backdrop_won_lights`,
  `drone_bloom` (a hover state: never skipped), `preview_chevron_chase`, `preview_ghost`,
  `daemon_rack_scan`. Strings: "OURS NOW", "%d LANDS HERE", "DRONE ENDS HERE".

### 2026-10-05 — Art direction — ART-9 4B dialogue and portraits
ART_BIBLE v2 §4.11 (dialogue A), §4.12 (portraits v2), DECISIONS "Designer ruling: DISPATCH
text"; references `round31_reward_event/dialogue.jpg`, `round38_portraits/*`,
`round39_portraits/portraits_classes_v2.jpg`.
- **Bust sets, pre-rendered.** `tools/art_gen/portraits/bust_rig.py` + `render_busts.py`
  (ported from art-pass 9a62cec, round 39 rig with the r39 / r39b / r39c gear) render in
  headless Blender 5.2: 8 classes x 4 rookie seeds x 4 frames (idle, blink = dead eyes,
  talk, hurt = grimace + squint), 240x266 cells, one 256-colour atlas per class
  (`assets/portraits/busts_<class>.png`, 31-47 KB) and the corp's photo print of each rookie
  (`prints_<class>.jpg`, about 37 KB; desaturated, warmed, grained on a flat backdrop).
  The rig now draws the same random numbers in every frame of one rookie (the mouth's tilt
  and the brows are drawn whatever the frame; the mouth's jitter never shifts the shared
  stream), so blink / talk / hurt are the same face; idle is unchanged from round 39.
  Pre-rendered rather than a SubViewport per feed: no 3D cost per visible feed; the seed
  pool is 4 per class (variants), a later pass can raise it by re-running the script.
- **Which rookie.** `PortraitBust.variant_for(class, operative id)`: a hash of class and id
  (an empty id, the class's own face / an unhired rookie, is variant 0). No game RNG, no
  state change (no seed field added to OperativeState), the same face on every screen and in
  every session. Operative ids repeat between campaigns (op_1...), so a campaign's first
  Breaker wears the same rookie each time; storing a roster-RNG seed on the operative
  (round 38 NOTES) is a schema change left for the portrait pass.
- **One feed.** `PortraitFeed` (kit) + `shaders/portrait_feed.gdshader` with `mode` (idle,
  talk, hurt, stationed, dead, recruit, print, voice), `tint`, `split`, `tear`, `noise`,
  `fps_hold` (stationed), a feed clock; the chrome (label strip "● CLASS // CALLSIGN", LED
  green / red / class / amber / off, HP chip, voice bars, ON <SITE> // 12 fps, NO SIGNAL +
  red pencil X + FLATLINED, HIRE: 15 SCHEMATICS stamp, cracked glass) is drawn on top. The
  chrome's words show only where they reach the 12 px floor (roster chips show the LED and
  the marks). Hurt at HP ≤ 25 % (`set_hp`); the flatlined stay flatlined. Listener dim for
  dialogue (`set_dimmed`). The print mode is the corp-paper context.
- **Motion.** New entries `portrait_feed` (clock; rolling bar period 4 s; amplitude = the
  stationed frame rate, 12 fps), `portrait_blink` (0.14 s every 5 s, phase per operative),
  `portrait_talk` (0.11 s mouth / bar step), `dispatch_trace` (1.6 s sweep), all T0, in
  REQUIRED_IDS and the motion lab (`["screen", "feed"]`). Off, under reduce effects or
  headless the feed is a still in its end state (talking keeps the mouth-open frame,
  flatlined the dead eyes); nothing waits.
- **Paper views draw the print.** `PortraitArt.operative_subject` carries `class_id` and
  `variant` and the class accent for a class with a bust set; `PortraitArt.draw` draws the
  print (Polaroid, crew chip, WANTED poster, combat Polaroid) so an operative keeps one face
  everywhere. Enemies, bosses, corp faces keep the M13 drawn styles (no v2 reference).
  `Polaroid.kia` (campaign audit): the print dimmed and crossed out in pencil red.
- **Dialogue.** Every subtitle line is on the Cell's CRT terminal (1A `UiTheme.terminal_box`
  tinted: cyan for the Cell / operatives / narrator, the corp's colour for a corp speaker,
  DISPATCH red on black glass with its words in a lifted red); the paper strip for
  non-DISPATCH speakers is gone (ART_BIBLE §1.2: the dialogue feed is CRT). The speaker's
  feed sits in the bar's left margin (a Node2D holds it so the container never lays it out;
  the paging measures the words' room after it): an operative's bark shows its own class's
  bust talking (`say(..., class_id)`; `bark` passes the class, not its base class, so a
  Wrecker shows a Wrecker), DISPATCH a red voice trace (never a face). Narrator, corp and
  observer lines have no feed. The feed follows the dock's height (22-120 px at the text
  size, at most 22 % of the bar's width). Typing, paging, skip and the bar's slide-in are
  unchanged. 1B's CRT material replaces the panel's look when it lands (seam:
  `Dialogue.crt_style`).
- There is no dialogue screen with choices in the game (dialogue.jpg's briefing layout):
  the portrait lab's `dialogue` page composes it from the real pieces (speaker live,
  listener dimmed, DISPATCH, the bar) for review; a briefing screen would be a new screen.
- Lab: `tools/design_lab/portrait_lab.tscn` (one windowed launch, a PNG per page: classes,
  states, matrix, contexts, dialogue, strip / column at 1.0 / 1.6 / 2.0).
- Tests: `tests/unit/test_art9_portraits_dialogue.gd` (fast). No M13 test dropped.

### 2026-10-05 — Art direction — ART-1 1D city render spike
Bible §1.2, §4.1–4.2, §6.1; plan §5.1–5.2; ruling 7 (fidelity first, then optimise). Full report:
`docs/handoff/art_1/city_spike_report.md`; crops in `docs/art_review/ART-1/1D/` (`.gdignore`d).
- **Built both ways on one district of the game's own layout:** NeonCity's streets, lots,
  territories and buildings, seed 7, read by `CityLayoutRecorder` (NeonCity placement mode, nothing
  drawn, game code untouched): the Halcyon border, 50 lots around lot (34, 22), with 3,710
  buildings and 2,608 street lots.
  - (a) Real-time Godot 3D: MultiMesh unit-prism families with jittered facets; the 3-band toon
    light function; procedural windows, ledges, shopfronts and roof trim; one full-screen post
    pass porting `post40.finish` (ink from normal, depth and material edges, grime, spill, bloom,
    fog, haze, rain, grade); a half-resolution ground pass for the see-through band; three sky-lane
    car tiers; one orthographic `Camera3D`.
  - (b) Blender 5.2 bake with the concept recipe, plus the post40 port, with 2D car motion on top.
- **Choice: (a).** It is closer to the references at grid, raid and netrun (read side by side). It
  is also the only one that gives §4.1's continuous zoom, the see-through band, the LOD swaps and
  the camera fits without a bake per view and zoom; a whole-city bake at raid density is about
  220 MB per layer.
- **Numbers, after optimisation (RX 6700 XT, 1080p, tier 2):** grid / raid / netrun take
  2.69 / 2.78 / 2.53 ms a frame (GPU 2.31 / 2.22 / 1.95 ms), 31–33 draw calls, 2.2 M primitives,
  and 106–127 MB of texture memory.
  - Deck tier 1 at 1280×800 on this PC: 1.81 ms a frame (GPU 1.3–1.4 ms).
  - The budget (city ≤ 8 ms) is met. The Deck itself is not measured yet; scaling suggests about
    10–12 ms there, and tier 0's levers are ready in config.
  - Measured with 3–6 other agents' Godot processes running.
- **Optimisation round** (config only, frames compared, look unchanged): the tier 2 shadow atlas went
  from 4096 to 2048, MSAA went off (the ink draws the edges) and the ground pass went to half
  resolution. Texture memory fell from 210–283 MB to 106–127 MB and frame time by about 0.6 ms.
- **Calls:**
  1. The see-through band is lod 1.50–1.595, so the City Grid (ortho 440) is solid and the raid
     (ortho 380) sits at the locked v3 opacity of 0.68. The bible's 1.45–1.75 with post40's anchors
     gave the Grid an opacity of 0.83.
  2. The toon band edges include the concept's world ambient: N·L 0.118 and 0.363.
  3. The post works on display values, as post40 does. Bloom and spill come from screen mips over a
     threshold, because Godot has no emission-only pass; Godot's glow is off.
  4. Sky lanes run over the district's six busiest avenues. Car colours come from the
     `RngStreams` stream `city_traffic`.
  5. Round 34 lock: the Cell's district keeps the street grid, with no fist roads. The HQs are
     stepped stand-ins; the heroes are ART-5's.
  6. The toon, ink and post shaders are prototypes in `tools/spike/city/shaders/`, because 1B owns
     `shaders/kit/`. They are to be unified with 1B's material.
- **Tests:** `tests/unit/test_city3d_spike.gd` (fast tier) covers:
  - projection round trips and the locked iso;
  - picking;
  - LOD, see-through and detail tiers from config;
  - car tiers with hysteresis;
  - quality tiers, with the Deck at tier 1;
  - the deterministic district;
  - the unit-prism instance mapping (never mirrored);
  - seeded traffic.

  The render is verified windowed only. No shipped screen changed.

### 2026-10-05 — Art direction — ART-2 2C cards and FX
ART-3 in Group 2 (`docs/handoff/art_2/ART_2_BATCH.md` 2C.1–2C.5; ART_BIBLE v2 §3.15, §3.18, §3.20,
§5.3–5.4, §6.3). Tests: `tests/unit/test_art2_cards_fx.gd` (fast tier).
- **Seams until Group 1 lands.** Bits: `scripts/ui/fx/bits_seam.gd` (BitsSeam) draws a `BitPath`
  as Share Tech Mono 0/1/+ glyphs (dark rim, 80–100 ms white-hot core, one 28 % trail copy): the
  bible's CPU fallback; 1B's pooled emitter replaces this file only. Sticker material:
  `scripts/ui/fx/sticker_seam.gd` (StickerSeam) puts `shaders/fx/card_sticker_fx.gdshader` (gloss
  band, dissolve scan front; reads `reduce_effects` through rc_common) on the flying card; 1B's
  vinyl sticker material replaces it there. Palette: tokens from `Palette` only (1A's v2 palette
  follows through the tokens).
- **Bits are pure numbers.** `BitPath` (RefCounted) gives each bit as a function of time and its
  arrival time; the view schedules on the precomputed arrivals and never reads a particle back.
  Scatter is hashed (no RNG). Shard Beziers take their control point on the rim-side bisector at
  1.5 × R_out (round the wheel, never across its face).
- **D16 (confirmed by the designer 2026-10-05):** `CardFx.origin`: a beat in the "act" phase (a
  played card's effect) leaves from the card's slap point (`CombatFxLayer.slap_point`, set when the
  card is played, also under reduce effects); slice, hub, turn-start and enemy beats keep their own
  source. Tested on the scene's real `_play_beat` path.
- **Effects, reference strip, motion id, tier, reduce-effects end state.** Under reduce effects
  (and headless, and an entry switched off) none of these adds anything: HP, guards, statuses and
  drones show their end state at once on the wheel (2A) and the existing static chips; nothing
  waits.

  | Effect | Reference | Motion id(s) | Tier |
  |---|---|---|---|
  | Card peel / flight tilt | `round19_combat_fx/card_play_v2` | `card_peel`, `card_play` | T2 |
  | Card slap (squash 1.13/0.86, contact ring, gloss sweep) | card_play_v2 | `card_stamp`, `card_slap_ring` | T2 |
  | Dissolve A, the bit stream (17 px cells, 19–25 px glyphs, clockwise into the hub) | `round19_combat_fx/dissolve_A_bitstream` | `effect_burst` (its duration) | T2 |
  | Hit shards (count/size from config) | `binary_damage/01_hit`, `round18_combat_fx/damage_shards` | `hit_shards` | T2 |
  | Crit (cracks, 7 `0110 1001` streaks) | `binary_damage/03_crit` | `hit_crit_streaks` | T3 |
  | Blocked (wall pops, shards bounce, a share passes) | `binary_damage/04_blocked` | `hit_blocked_wall` | T2 |
  | Block gain: DEFRAG bricks course by course facing the foe | `round19_combat_fx/fx_block_shield` | `block_wall` | T2 |
  | Shield gain: SANDBOX hex plates with a ripple | fx_block_shield | `shield_hex` | T2 |
  | Heal: green +/1/0 in from outside, segments relight | `round19_combat_fx/fx_heal`, `binary_damage/05_heal` | `heal_inflow` | T2 |
  | Evade gain (token forms) / evaded (token flies up-left, the attack chases it) | `round23_combat_fx/fx_evade_v4` | `evade_token` | T2 |
  | Apply CORRUPTED (pink bits in, glitch wipe L→R, doubled tears) | `round23_combat_fx/fx_corrupt_apply_v4` | `corrupt_apply` | T2 |
  | CORRUPTED tick (flash, tear spike, pink/green bits round the rim to HP) | `round23_combat_fx/fx_corrupt_tick_v3` | `corrupt_tick` | T2 |
  | Drone deploy (bits pack into the hex, sticker slaps) | `round19_combat_fx/fx_drone` | `drone_deploy` | T2 |
  | Drone attack (lens charge) | fx_drone | `drone_attack` | T2 |
  | Drone destroyed (hex cracks into bits, clamp springs) | `round22_combat_fx/fx_drone_destroyed_v3` | `drone_destroyed` | T2 |
  | Enemy defeated (pieces fly apart and fall, shockwave, shed bits, DELETED) | `round23_combat_fx/fx_enemy_defeated_v2` | `enemy_break`, `enemy_defeated_bits` | T3 |
  | Phase change (orange bits from the crossed pip under the arc; PHASE N, N NEEDLES) | `round23_combat_fx/fx_phase_change_v3` | `wheel_burst_phase`, `phase_change_bits` | T3 |
  | Respin (spent RAM chips crack into cyan bits to the hub; RESPIN) | `round23_combat_fx/fx_respin_v3` | `respin_bits` | T2 |
  | Nudge resisted (grey bits; RESIST) | `round20_combat_fx/fx_nudge_resist` | `nudge_resist_bits` | T1 |
  | RAM gain (bits down the centre into the new chips, 4 per chip) | `round21_combat_fx/fx_ram_gain_origins` (B) | `ram_gain_bits` | T1 |
  | Temporary labels (every effect word: pop, hold, dissolve L→R into rising bits) | §3.20 | `temp_label` (+ `result_stamp`) | T2 |
  | Daemon / firmware trigger (source pulses, bits stream to where it acts) | §3.20 | `daemon_trigger`, `firmware_trigger` | T2 |
  | Heat H1 on the backdrop (beacons, searchlights, police lights per band) | `round22_combat_fx/heat_city_v4_strip` | `heat_city_beacon`, `heat_city_sweep` | T0 |
- **Small calls.** The shards burst where the hit meets the rim facing its attacker and curve round
  into the drained HP segments (the hit line still ends on the HP ring). `effect_burst`'s duration is
  now the dissolve (0.3 → 0.5 s) and `card_stamp` the slap (0.1 → 0.18 s): the card is gone before
  its effect, as ANIM-R3 A6i had it. The old green word box became the vinyl word sticker (white
  die-cut, colour fill, ink or paper lettering by contrast); every `word_stamp` dissolves into bits.
  The sticker card: white die-cut 5 px at hand size, fill by what the card does first (spin gold,
  harm pink, guards cyan, else violet, darkened 42 %), gloss band, yellow cost dot (grey + NEED n
  when the RAM is short), peel curl at the foot that grows on hover, holo-striped edge for Rare and
  Boss cards. HP arc geometry is mirrored from `WheelView.hp_ring_spot` and RAM chip spots from
  RamBar's draw (both other areas' files): a public `hp_arc_spot(frac)` (2A) and `pip_spot(k)` (2D)
  would replace the copies.
- **Schema (minimal):** CampaignConfigData "Combat FX" group: `fx_shard_base/per_dmg/max`,
  `fx_glyph_px_base/per_dmg/max` (round 18 NOTES numbers) and `heat_city_*` per-band counts (5
  entries each, validated); `fx_shard_count` / `fx_glyph_px`. Smoke check `_art2c`.
- **Carry-over:** combat `hit_shake` 3 → 2 px (T2's limit).
- **Hooks in other areas' files (smallest):** `combat_scene.gd` (2D): one `CombatBeatFx.play` line
  in `_play_beat`, `CombatBeatFx.spawn` on a spawn beat, RAM gain on the ram beat, the
  `nudge_absorbed` case in `_animate_wheels`, respin bits in `respin()`, the hub point for the
  dissolve (`cap["hub"]`), the drone destroyed / DELETED calls in `_death_beat`, the phase pip in
  `_boss_phase_feedback`, `N NEEDLES` in `_phase_beat`, `short_ram` on hand cards, the HeatCity node
  over the background and its band in `_sync_heat`. `motion_lab.gd`: 24 demos.
- **Not built yet (proposed slices):** Daemon / firmware triggers have their effect and demo but no
  game hook: the engine's `trigger` events make no replay beat (adding one to ResolveBeats moves the
  replay's pacing; slice: a non-timed "trigger" beat, then one hook). Crit RGB split on the wheel
  rect and the defeated pieces' pixelation (need the wheel as a texture: 2A). Hover scale 1.36 with
  neighbours shifting and the RAM meter hatching the cost (hand layout and RamBar: 2D), card idle bob.
  The standing walls / hexes / EVADE token after the effect (wheel overlays: 2A).
- **Dropped tests:** none.

### 2026-10-05 — Art direction — ART-1 1B material kit
The reusable materials every later group applies (ART_BIBLE v2 §1.2, §1.3, §5.3–5.4, §6.3, §6.4),
built new in Godot from the round 3 combined_v2 concept toolkit (`art-concepts-r43:docs/concepts/
round3_overlay/combined_v2/scripts/` `sticker_lib.py`, `kit.py`, `s04_kit_sheet.py`, `s05_lifecycle.py`;
the tactical-glass pencil `o_a_tactical_glass/scripts/tg_lib.py`; round 19/22 `sticker_lib19.py`
gloss_k). No screen is restyled. Files: `shaders/kit/*` (10 shaders + the bits atlas),
`scripts/ui/kit/materials/*` (one class per file), `tools/design_lab/kit_sheet.gd/.tscn`,
`tools/design_lab/bits_atlas_bake.py`.
- **Register.** `KitMaterials.ALL` lists each material, its component, shaders, VfxTier (of its
  resting look; T0 for all but the bits, T2) and motion ids. Every kit shader includes `rc_common`
  and reads the `reduce_effects` global; every TIME line goes through `rc_time` / `rc_live`.
- **1B.1 CRT terminal** (`CrtTerminalPanel`, `crt_terminal.gdshader`) vs `04_kit_sheet.jpg`
  (EXECUTE box) and §1.2: navy glass (Palette `CRT_GLASS_TOP/BOTTOM`), a 1.5 px accent edge with
  an outer glow, the corner notch, 3 px scanlines at 10 % over the text, a hex dump at 6 % that
  scrolls, Share Tech Mono text that types on behind `> ` (through `Typing`, so one press shows it
  whole) and a blinking `_` caret. Accent per use: cyan Cell, lime firmware, gold Schematics, corp
  colour, red DISPATCH. The glass is a separate shader from `shaders/crt_panel.gdshader` (UiTheme's
  existing glass, 1A's TerminalPanel variation may adopt this one).
- **1B.2 vinyl sticker** (`VinylSticker`, `vinyl_sticker.gdshader`, `sticker_fill.gdshader`) vs
  `04_kit_sheet.jpg` columns C and `send_it_sticker.jpg`: the art (die-cut body = every glyph grown
  by border + keyline with `draw_string_outline` plus a band that closes the notches between
  letters; extrude stepped down-right; ink keyline; gradient or holo fill per glyph with ±4° jitter
  from KitNoise) is drawn once into a SubViewport; the shader adds the rim light / shade and cut
  line, the gloss (soft band + two sharp lines on a 28° diagonal, `gloss_k` 0.22 at rest as round
  19's sticker_lib19, 1.0 while a sweep crosses), the peel (corner folded back with the adhesive
  back shaded across the fold, a bright crease, the flap's cast shadow), the two-layer drop shadow
  raised by `lift`, dissolve and disabled grey. Objects: `Shape.RECT/CIRCLE` on white, kraft or
  holo stock with any content under `content_root`. One sweep on one sticker at a time:
  `StickerSweepQueue` (join order, the entry's delay between sweeps). Word over a system word
  (§1.3): `SystemWordSticker` (washed mono word + scanlines + hint line, the verb slapped at -5°
  on the panel's bottom edge). Runtime sticker only (the per-locale baked atlas is ART-4/10's).
- **1B.3 grease pencil** (`GreasePencilMark`, `GreasePencilWord`, `PencilShapes`,
  `marker_stroke.gdshader`) vs the kit sheet's column A and round 11's pencil: Line2D strokes in
  writing order, round caps, width 10, TILE UVs so the shader knows along / across; wax = an
  opaque core, 9 bristle bands with dropouts toward the edge, a ragged grain edge, the round body
  lit on one side with a sheen line, alpha 0.96, the glint every `pencil_glint` delay; a duplicate
  under-shadow line offset (3, 4) and 3 px wider at 0.42; dashed = hand dashes cut in the shader
  (what-if). Write-on and the cloth wipe trim points (never alpha); the wipe also drags the wax.
  `PencilShapes.snap_to` moves a mark onto a real polyline. Words ("HIT IT", 1–2 a screen) use the
  marker face with the wax grain (mode 2) and write / wipe letter by letter.
  **Lint rule:** `PencilLint.violations` (cover: a drawing Control later in draw order whose rect
  meets a stroke segment; layer: any drawing UI on a CanvasLayer above the pencil's, cursor layers
  ≥ 128 excepted). Exported by `tools/visual_qa/review_pack.gd` (lint key `pencil`) and reported
  by `lint_report.py` as rule **f pencil** (two small edits in D's runtime lint).
- **1B.4 light spill** (`LightSpill`, `light_spill.gdshader`) vs the kit sheet's column D: a rect
  round the source reads the screen texture and adds `base × colour × light × 1.9 + colour × light
  × 0.28` through a tonemap shoulder (kit.py's light_spill); bright saturated pixels (the emitter)
  are not re-lit; two falloffs; `gain` per screen (`GAIN_COMBAT` 1.15, `GAIN_CITY` 0.38,
  `GAIN_SHOP` 1.2), `lit` follows the source. 3D: `LightSpill.uniforms_3d` packs up to 8 sources
  for the toon shader.
- **1B.5 decrypted holo** (`DecryptedHoloPanel`) and **corp paper** (`CorpPaperPanel`): holo =
  corp tint at 78 % over the deep, 4 px scanlines, 3.5 slow bands, a ±2 px RGB split on the edge
  only (0 under reduce effects), the 0.88 scrim (`Palette.HOLO_SCRIM`, a top-level full-screen
  rect behind it), the seal cracked by a red fracture and a DECRYPTED stamp slot. Paper = stock
  with cloud, tooth, fibres, toner speckle and handled edges (scales like a 9-patch), an IBM Plex
  Sans Condensed Medium letterhead and rule in the corp colour, Courier Prime fields (1A's
  `Palette.paper()`), a stamp slot (CLASSIFIED).
- **1B.6 binary bits** (`BinaryBits`, `BitsPath`, `binary_bits.gdshader`, `bits_atlas.png`):
  pooled GPUParticles2D (4 kept), one-shot, additive, `particles_animation` over a 4-cell atlas
  (0, 1, +, bit-rot; Share Tech Mono with a same-colour outline ~1/22, baked by
  `bits_atlas_bake.py`); the process shader lerps each bit along its quadratic Bezier (control on
  the rim-side bisector at 1.5 × R_out round a wheel; a bow of 0.25 of the length elsewhere),
  white-hot for the entry's amplitude, flipping every 60 ms, tumbling, shrinking in. Every number
  per bit (start, control, spawn delay ∝ x, flight ± 15 %, phase, spin) is computed by `BitsPath`
  and handed in, so `burst` returns the arrival times before anything flies. **Call made:** the
  CPU fallback draws the same plan from this node (≤ 44 bits) instead of a `CPUParticles2D`, which
  cannot run a process shader and could not follow the Bezier.
- **1B.7 cel / toon + ink** (`ToonInkMaterial`, `toon_ink.gdshader`, `toon_ink_hull.gdshader`):
  3 hard bands in `light()` (0.55 / 0.12 → 1 / 0.62 / 0.32, shadow tinted violet), per-face tone
  jitter (Cv2), world-space grime stronger low on a wall, banded spill from `spill_lights[8]` /
  `spill_colors[8]` / `spill_count`, depth haze; ink = an inverted hull next pass grown 2.5 screen
  px along its normals with a world-noise wobble. For 1D: the city may prefer a depth/normal
  post-process for ink on large meshes (hull splits at hard box corners); the toon pass and the
  spill uniforms are the same either way.
- **Motion** (`ui_motion.tres` + REQUIRED_IDS + motion-lab demos kind `kit` through `KitDemo`):
  `crt_type_on` 0.02 s/char T1, `crt_caret_blink` 0.5 s T0, `crt_hex_scroll` 14 px/s T0;
  `sticker_slap` 0.45 s T2 (lifecycle APPEAR in `05_lifecycle.jpg`: from 1.24x, over-rotated 13°,
  squash 1.13 / 0.84 for 90 ms, one overshoot (BACK), the shine sweep), `sticker_peel` 0.30 s T2
  (EXIT: fold 0 → 0.6, lift, curl away down-left), `sticker_dissolve` 0.5 s T2 (cells left to right,
  white-hot rim, bits from the sticker's rect), `sticker_gloss_sweep` 1.4 s + 4.0 s rest T0,
  `sticker_corner_flutter` 2.4 s, 0.08 ↔ 0.20 T0 (IDLE), `sticker_hover` 0.12 s ×1.05 T1 and
  `sticker_press` 0.08 s y 0.90 T1 (`send_it_sticker.jpg` HOVER / PRESSED); `pencil_write_on`
  900 px/s capped 0.6 s T2 (lifecycle "draws in writing order"), `pencil_wipe` 0.30 s T2 (EXIT "a
  palm drags the pencil"), `pencil_glint` 0.6 s every 3 s T0 (IDLE "a thin glint every ~3 s");
  `holo_bands` 4 s T0; `light_spill_breathe` 3.2 s ±8 % T0; `bits_flight` 0.55 s, 0.12 s spread,
  0.08 s white-hot T2. Every motion shows its end state at once under reduce effects, headless or
  switched off (`Motion.live`), and the one-shot ones join MotionSkip (passive).
- **Palette tokens** (palette.gd, a 1B block after 1A's): the kit uses 1A's `PENCIL_PLAN`
  #FFE200, `PENCIL_THREAT` #FF1C2C, `PENCIL_SHADOW`, `STICKER_DIE_CUT`, `STICKER_SAFE(_LOW)` and the
  faces `pencil()` (Permanent Marker, wax words) and `paper()` (Courier Prime); 1B adds
  `VINYL_WHITE_LO`, `VINYL_BACKING`, `VINYL_INK`, `VINYL_EXTRUDE`, `KRAFT`, `KRAFT_FIBRE`,
  `STICKER_FILL_PINK/RED/YELLOW` (yellow = 1A's safe pair), `CRT_GLASS_TOP/BOTTOM`,
  `PAPER_TYPE_INK`, `HOLO_SCRIM`, `TOON_INK`. (Merging 1A: 1B's own PENCIL_YELLOW / PENCIL_RED /
  VINYL_WHITE were dropped for 1A's tokens; `Palette.marker()` is now Anton, so the kit's pencil
  words and kraft notes use `pencil()`.)
- **Kit sheet, read windowed next to the references** (`docs/art_review/ART-1/1B/`):
  `--page=kit` vs `04_kit_sheet.jpg`: sticker words and objects match the reference's build (thick
  white die-cut, keyline, extrude, gloss, curl, shadow; holo SEND IT and crew card, kraft note);
  the pencil column reads as wax on glass (yellow plan circle and dashed route with a waypoint, red
  target circle, printed brackets and range ring, HIT IT + arrow); spill lights the facets round the
  neon sign (the reference's sign spelled with the shop's old name; the sheet's says MAINFRAME).
  Remaining gaps: the reference's letters carry a bevel highlight (not drawn), its pencil
  words are hand-lettered strokes (ours: the marker face with wax grain), its neon sign is the
  shop's own art. `--page=lifecycle` vs `05_lifecycle.jpg`: APPEAR (slap, the circle writing on),
  IDLE (flutter, holo drift, sweep) and EXIT (peel with the backing and crease, the pencil wiped)
  play as described. `--page=materials`: CRT (four accents), bits round a wheel rim (GPU and CPU
  frames), holo over its scrim, paper with a stamp, the toon + ink 3D sample.
- **Tests:** `tests/unit/test_art1_material_kit.gd` (fast): register (shaders, tiers, entries, lab
  demos), tokens, sticker build / states / reduce-effects end states / one press / one sweep at a
  time / word over system word, CRT accents and type-on, pencil write-on and wipe by trimming,
  reduce-effects and headless end states, look uniforms, shapes and snap, the pencil lint rule,
  bits round the rim / deterministic arrivals ∝ x / no flight under reduce effects / CPU cap, holo
  split, paper fields, spill breathe and 3D packing, toon bands and uniforms. No test dropped.

### 2026-10-05 — Art direction — ART-1 1A palette, faces, theme
ART_BIBLE v2 §2.1–2.10, §5.6, §6.4 applied through `Palette` and `UiTheme` only (no screen
restyled; screens pick it up through the tokens and the theme).
- **Palette v2:** every §2 row with a value has a token with the bible's value
  (`tests/unit/test_art1_palette_theme.gd` holds the bible's tables row by row). Corp kits move to
  round 18 (Solace #96FF46, Halcyon #B06EFF, Orbital #CDF0FF; ART-0 kept #DDE3FF for Orbital) with
  `CORP_*_2` secondaries and `corp_secondary()`; class accents to round 22 / 38 (App. C #4); new
  §2.2 tokens (PENCIL_PLAN / THREAT / SHADOW, HEAT_B, RING_AVAILABLE / UNAVAILABLE / CUT); Daemon
  families (§2.6, round 34 `fwlib.FAM` values where the bible names only a hue), rarity (§2.7,
  round 34 `RAR_COL`, gunmetal #3A4048 my pick), the five Heat bands as tokens with **HEAT_PURGE**
  of its own (HUNTED's look until art gives it one), §2.10 chrome (SELECTED cyan, ON_SELECTED navy,
  STICKER_SAFE yellow pair, STICKER_COMMIT pink, die-cut white), LIVE_NUMBER_RIM (the glyph outline is 1C's GLYPH_INK).
  `PAIRED_WITH` notes each meaningful token's non-colour cue (§5.1); the test checks every entry.
  Contrast checks (WCAG via `Palette.contrast`): terminal text on navy glass ≥ 9:1, TEXT_LO
  disabled words ≥ 4.5:1, navy on the cyan fill ≥ 7:1, ink on the pink / yellow stickers ≥ 4.5:1,
  the theme's own font colour against its own box per state.
- **Calls made (palette):** RING_CUT "dim grey" = the NULL slice grey #6A6A6A; the Daemon family the
  bible calls MISS is **NULL** (`DAEMON_NULL`, `&"null"`): it fires on the NULL slice, renamed by
  the 2026-10-05 ruling; TERMINAL_BG is rgb(5,13,28) at .95 exactly and TERMINAL_EDGE NET_CYAN at
  78 %; TERMINAL_BG_HOT moves from magenta to a cyan-lit navy (v2 hover is a lit edge + glow, never
  the verb's pink). RING_AVAILABLE equals Meridian's orange (App. C #22, kept until the designer
  says otherwise).
- **Faces (§2.9):** **MSDF on** (`Palette.FONTS_MSDF`, every `.import`, range 16). Courier Prime
  Regular + Bold copied to `assets/fonts/` with `OFL_CourierPrime.txt` (`FONT_PAPER(_BOLD)`,
  `paper()`, `paper_bold()`); README rewritten with one row per face. **Call made:** Permanent
  Marker is grease pencil only (`FONT_PENCIL`, `pencil()`; FONT_MARKER removed); `Palette.marker()`
  (the Cell's lettering on its fixed objects: verbs, tags, stamps, names; 105 call sites in 34
  files) now returns Anton, the §2.9 sticker face. The screens move to their v2 components in
  ART-2..12, so the name stays rather than churning 34 files while Group 2 builds on them.
- **MSDF fallout fixed:** MSDF faces report fractional heights (`get_height`: Share Tech Mono 30 px
  = 34.375) while a RichTextLabel lays lines at ceil(ascent) + ceil(descent) (35); the HQ's
  pirate radio and the subtitle pager measured with `get_height` and drifted (radio 11.2 lines,
  a page split at 14 lines instead of 15). New `UiTheme.line_px`, used by `Dialogue` (band
  height, lines fitting, page height, dock room) and the radio. The **signal-11 crash**
  (ART-0 carry-over) was not YOUR NODES but the raid setup at 2.0 in
  `test_the_home_banner_keeps_off_cores_label_and_the_tokens_and_the_packets_stop`: the NODE
  ORDERS list's `ScrollHint` flipped its room every frame (with the room, the view held at its
  least height gave the room out of the column instead of itself, so "overflows" said no; without
  it, yes) until the deferred calls on freed nodes flooded and the process crashed. `ScrollHint.overflows`
  now measures a view held at its least height against that height (kit file, smallest edit).
- **Theme (§6.4):** `TerminalPanel` = navy glass, cyan edge, the top-right corner cut
  (`corner_detail` 1) and a cyan edge glow; `GlassPanel`, popups and tooltips the same family
  (tooltips in Plex, §2.9); new variations `TerminalButton` (2 px edge, F's lime brackets),
  `HoloPanel` (`holo_box(corp)`: corp-tinted plate at .88 with the corp edge; 1B's holo shader
  draws over it), `PaperPanel` (paper stock, ink keyline, drop shadow); `UiTheme.live_number(step,
  colour)` LabelSettings (Anton, 2 px #06060A rim × text scale, own-colour glow at 50 %, size 10).
  Every terminal button, menu line, tab, toggle, slider and scroll grabber is cyan: hover = lit
  edge + glow, pressed = cyan fill with navy words, tabs selected = cyan fill; disabled = DISABLED
  edge with TEXT_LO words. `HotButton` is the pink vinyl verb (die-cut white border, round
  corners, ink extrude, Anton at the TITLE step × text scale) with the lime die-cut halo on focus
  (no brackets, as the coordinator relayed; F's test updated to that). HeaderLabel is tracked
  mono CAPS in TEXT_HI. High contrast is still applied last (tested). `TerminalWindow`'s title
  rule takes the window's accent instead of the Cell pink (kit file, one line).
- **Combat hand (call made, outside my area, smallest edit):** Anton is narrower than Permanent
  Marker, so the SEND IT and sticker column freed width, `_card_scale_for` grew the hand cards
  (148 x 1.39 at 2.0) and the wheels fell under `BIG_TEXT_RADIUS_KEEP` (90 vs 126). The hand card
  scale is now also held to `HAND_HEIGHT_SHARE` (0.24) of the screen's height (no change at 1.0).
  Dict keys spelled `"disabled":` trip the names-pass lint's raid-word check, so the few new ones
  are written `(&"DISABLED"):`.
- **Tests:** new `tests/unit/test_art1_palette_theme.gd` (fast). Changed pins (superseded looks):
  `test_art_w1_tokens` corp values and "the shared theme is unchanged" (now: mono system text,
  the verb at the title step, tracked header), the track_label check uses `pencil()`;
  `test_horizontal_pass20_screens` tooltip edge pink → cyan; `test_art0_kit_states` HotButton
  focus = the sticker halo; `test_accessibility` FONT_PENCIL; `test_horizontal_pass21_screens`
  measures the radio with `line_px`; `test_anim_r3_city` territory hue gap: Solace's locked
  #96FF46 sits 0.066 from the Cell's lime (bible §2.4 names the risk; the hatch, the stamp word
  and "Solace never on a link or ring" carry it), so Solace needs 0.05, every other corp still
  0.1. No test dropped.
- **Capture:** `tools/design_lab/type_chrome_sheet.tscn` read next to `typography.jpg` and
  `ui_kit.jpg`; before / after of title, HQ, a fight and the Mainframe at 1.0 and 2.0; crops in
  `docs/art_review/ART-1/1A/` (`.gdignore`d).
### 2026-10-05 — CI sharded (ready to re-enable after M14)
Follows "CI paused for M14". The workflow is rebuilt but still `workflow_dispatch` only; the push and
pull_request triggers sit in a commented block in `.github/workflows/ci.yml` to restore after ART-12.
- **Six GUT shards**, one matrix job each, via the new `tools/run_tests.py --shard K/N` (same longest-first
  balancing on the manifest's measured times as `-j N`; shards disjoint and complete; tested in
  `tools/test_run_tests.py`). Each shard runs in 2 local processes (`-j 2`, suited to a 4-core runner).
  Reason: 1752 s of measured script time / 6 = ~292 s per shard; assuming runners 3x slower than the dev PC
  that is about 7-8 min with 2 processes, about 10 min with setup and import, against a 25 min job limit
  (the old 30 min single process needed about 1 h on a runner). More shards would only add import overhead.
- **Separate `fast-checks` job** (schema smoke test judged by its "SCHEMA SMOKE TEST: PASS" output because
  Godot can exit 139 afterwards, content validation, text export diff); `export` needs it and all shards.
- **Caches**: the Godot download and `.godot/` (keyed on `project.godot`, `addons/`, `assets/`, `*.import`);
  `--import` still runs each time. The Godot download cache is best effort (unverified on a real runner).
- A failing shard uploads its `gut.log` and `results.xml` as an artifact.
- Not yet run on GitHub: the timing figures are estimates; check them on the first manual run and adjust
  `SHARDS`/`-j`. If the repo is private the runner has 2 cores, so use `-j 1` and more shards.

### 2026-10-05 — Art direction — ART-1 1C glyph pipeline
The production glyph atlas, its shader and an id → glyph table (ART_BIBLE 3.5, 5.2, 6.2; plan 5.3).
Nothing is swapped into the wheel views yet (ART-2).
- **Masters regenerated, not copied.** `tools/art_pipeline/glyphs/build_glyph_atlas.py` runs the concept
  generators from tag `art-concepts-r43` (round 40 `slicelib.glyph_mask`, which chains back to the round 17
  shapes; round 18 `glyph_priority`; round 34 `fwlib.icon`) at their 512 / 1024 px masters and builds a
  single-channel **SDF** from them (4x the cell's resolution; the sign from the master's coverage, the
  distance from sub-pixel edge points). Every round 17 glyph and PRIORITY regenerate identical to the
  `docs/art_reference/glyphs` PNGs (IoU 1.0 at 256 px, recorded in the manifest). SDF, not MSDF: the masters
  are PIL rasters, not vector contours; the outline is rounded by design (bible 3.5), so the corner
  rounding an SDF gives at 128 px cells is not visible at 16–128 px.
- **Files.** `assets/glyphs/glyph_atlas.png` (16 × 8 cells of 128 px, L8, glyph box 96 px centred, field
  ±16 px; imported with mipmaps), `glyph_atlas_manifest.json` (geometry, source tag and commit, per-glyph
  source ids, closest 16 px pairs, reference IoU), `masters/<name>.png` (256 px white-on-transparent copies,
  `.gdignore`d: the source record), `glyph_sdf.gdshader` (fill at smoothstep 0.5 ± aa from `fwidth`,
  outline at 0.075 × box in `Palette.GLYPH_INK` #0C0A16, fill `Palette.GLYPH_FILL`, node modulate applies).
- **Names and order.** `index.txt` order with the program names (`slice_shim`, `slice_overflow`,
  `slice_defrag`, `slice_sandbox`, `slice_detour`, `slice_hotfix`, `slice_infect`, `slice_trojan`,
  `slice_null`), JUDGEMENT's slot taken by `special_priority` (round 18; JUDGEMENT retired by D3), the
  eleven `placeholder_*` left out; then `hub_<core id>` (8 player cores + `hub_phantom_echo`, Phantom's static
  icon, + the 6 enemy hubs), `seg_<id>` (7), `fw_<id>` (18), `daemon_<id>` (24), `exploit_intel` /
  `exploit_breach` and `pending`. 114 cells.
- **Hubs, segments, Firmware, Daemons and Exploits joined the atlas** (bible 3.5 / 6.2 "join the same
  atlas") from their locked rounds' own generators rather than waiting: hub cores and segments from
  round 38–40 `glyphs38/39/40`, Firmware and Daemons from round 34 `fwlib`. The Manifest's hub is
  `customs_seal` in the game (renamed from Priority Routing), drawn with round 38's Priority Routing
  emblem (express arrow). Mk2 cores share their core's emblem (bible 3.3: Mk2 adds a rim and a tab).
- **Exploit glyphs reuse two round 17 placeholder shapes**: round 38/39's Exploit art draws INTEL with the
  RECON binoculars and BREACH with the KEY, so those two shapes enter the atlas as `exploit_intel` /
  `exploit_breach` (not as placeholders); VIRUS uses `status_corrupted`, as round 38 does.
- **Aliases** (bible 3.5) are table entries, not cells: FREEZE → `state_frozen`, RESIST → `special_weight`,
  DAMAGE → `slice_shim`, EVADE → `slice_detour`, HEAL → `slice_hotfix`. **SHIELD pts → `slice_sandbox`**,
  not `placeholder_shield` (placeholders are out of the game). AIRMAIL and GROWTH show their program's
  glyph (OVERFLOW, HOTFIX): round 18's kits give them their own screen, not their own glyph. DOUBLE_NUDGE_CARDS
  and RETRIGGER both use AGAIN; APPLY_STATUS uses INFECT; DEPLOY_DRONE uses TROJAN; a satellite uses DRONE.
- **Schema (minimal, new class):** `scripts/data/glyph_table_data.gd` `GlyphTableData` (atlas, glyph_names,
  columns, cell_px, box_px, spread_px, outline_width, twin_px, twin_max_iou, twin_exceptions, ids) with
  `validate()`; shipped as `content/config/glyph_table.tres`; checked in
  `tools/schema_smoke_checks.gd` `_art1_glyphs`. Keys by kind: `type_*`, `status_*`, `effect_*`
  (+ `effect_spin_ccw`, `effect_nudge_inner`), `hub_*`, `seg_*`, `firmware_*`, `daemon_*`, `exploit_*`,
  `slice_<id>` (specials: priority, citation, dose, solar_flare, shim_8_weight), `word_*`, `satellite`.
- **View:** `scripts/ui/kit/GlyphIcon` (new file; F's kit files untouched) draws one cell; `box_px` is the
  glyph box on screen, the control is the whole cell so the outline fits; one shared material per colour
  pair. `Palette.GLYPH_FILL` / `GLYPH_INK` appended at the end of palette.gd (1A's file: two lines).
- **16 px rule** checked from the atlas itself with the round 17 catalogue's metric (box-filtered coverage
  of the glyph box at 16 px, 0.6 px Gaussian, soft IoU): worst non-exempt pair below 0.68. Exempt: the
  pairs kept alike on purpose (SPIN / MOMENTUM, SPIN CW / CCW, HP / TAKE DMG, Phantom core / its echo icon),
  the bible's known borderlines and the 15 Firmware/Daemon pairs under the open question.
- **Capture:** `tools/design_lab/glyph_sheet.tscn` (every glyph at 64 / 32 / 16 px and 16 / 32 px at text
  scale 2.0, six pages, one Movie Maker run, one window), read next to `glyph_set_v3.jpg`; crop in
  `docs/art_review/ART-1/1C/glyphs_vs_round34.jpg`. Shapes match the reference cell for cell; at 16 px the
  outline stays closed and the silhouettes read (the HOTFIX band-aid pads drop out at 16 px, as in the
  reference).
- Tests: `tests/unit/test_art1_glyphs.gd` (fast tier). No test dropped.

### 2026-10-05 — Art direction — ART-0 kit behaviour (salvage S5, area F)
Ported by hand onto main's kit from art-pass (tag `art-m13-final`): 59b064e (W2 states, focus
brackets, focus scale), 77c96df (RefusalMark), ccf30fc (PadGlyph, glyph prompts), bb4f2e2 and the
W9F sweep (UiTip.for_input, pad wording), a155849 / d91a26f (W8a modal API, GlassScrim),
c77b99f / 9ad2133 (W9F UiWrap.whole_words), fc477fc (WF FitScroll / ScrollHint guards), b9af7e3
(WF PaperInk). Behaviour and tests only: no zine skin ported (ART-4 / ART-10 restyle), main's
colours kept, every new colour a Palette token (the static lint baseline is unchanged).
- **Component states:** `KitState` (six states, lift / glow, `draw_frame`, `force`,
  `force_native`) and `RefusalMark` (any control's refused flash; a reason shows as a warn
  ToastNote). StickerButton, ZineStamp and DripButton report `state()`, take `refuse()`, lift on
  hover / drop on press and draw the disabled lock badge and the refused HARM outline + no-entry
  mark. UiTheme's button, HotButton, NoteButton and MenuItem hover boxes lift 2 px and pressed
  boxes drop 1 px at the same minimum size (`UiTheme.shifted`). **Call:** the W2 button variants
  (Primary / Secondary / Tertiary / Danger, label + 32 px, the `StyleBoxLocked` disabled box) are a
  look and are not ported; main's native disabled boxes stay (ART-1 / ART-10). The no-entry mark
  is drawn by KitState (main's StatIcon has no NO_ENTRY; the W2 icon redraw is ART-1's).
- **Focus brackets (v2 §2.10, Appendix C #15, round 31):** `StyleBoxBrackets` at **3 px, 7 px
  outside** (M13: 2 px at 4 px), INK keyline, never adds to a minimum size; the theme's focus box
  for Button, OptionButton, CheckButton, CheckBox, NoteButton, MenuItem, LineEdit and LogText
  (`UiTheme.BRACKET_FOCUS_TYPES`; HotButton inherits Button's). TabBar's tab focus keeps its box.
  High contrast thickens them to `HC_FOCUS_BORDER` (4 px) in solid FOCUS (area C's HighContrast
  handles StyleBoxBrackets; C's test reads the brackets now). **Call:** stickers (StickerButton,
  ZineStamp, the SEND IT DripButton) keep their lime halo for focus and get no brackets (v2:
  "a focused sticker gets a lime die-cut halo instead"). The 1.03 pad focus scale (`UiFocus`,
  `focus_scale`, T1) is ported as M13 had it: pad only, headless never scales.
- **PadGlyph** draws every button of the four sets; its set is area C's
  `Settings.effective_glyph_set()` (stored choice, or the pad in use under auto) and
  `detect_set` is C's `Settings.glyph_set_for_joy_name` (one rule set). PadPrompts shows glyph +
  verb pairs (`glyphs()`); `texts()` still reads "A  Buy" (the glyph's name), so the H23 / ANIM
  prompt tests are unchanged. **Not ported:** the prompt bar's glass backing and compact mode
  (W9F looks) and the glyph on SEND IT / the buy stickers (W9F / W8 restyles, ART-3 / ART-4).
- **UiTip.for_input** (+ `has_mouse_words`, `pad_safe`); FocusTip swaps mouse words on a pad
  (the safety net). Every player string with a mouse word now has a pad variant: HQ (mini-map,
  dossier, boosts, crew chips, assets, raid steps), combat (aim hint, card tip), the deck viewer's
  shred tile, the loadout swaps, the rebind note, and netrun's drag lines through
  `netrun_scene.drag_tip(kind)` with `DRAG_TIPS_MORE` / `DRAG_TIPS_PAD` (the socket tips'
  "dragging ..." clause became a drag line; the old one-string keys are gone from strings.csv,
  re-exported). The M13 tooltip restyle (26-36 columns, body face, title said once) is not
  ported (a look, ART-10).
- **Modals:** `PageTransition.open_modal / close_modal / open_modals / modal_open /
  after_modals`, `MODAL_GROUP` (`rc_modal`), `modal_in` 0.18 s / `modal_out` 0.14 s (T1, new
  ui_motion entries, REQUIRED_IDS, lab demos `screen modal_open` / `modal_close`; with
  `focus_scale` → `screen kit_focus` and `button_refused` → `screen kit_refused`). Modals on main:
  ConfirmDialog (opens itself over a `GlassScrim.backdrop_for` that stops the page's clicks; Yes /
  No / Esc close through `close_modal`), LoadoutView and DaemonTray (open themselves), the netrun
  viewers (`_open_modal`). Page changes wait for them: the title's pages, slots, tutorial; the
  netrun's `_show_current` when the screen changes; the HQ's pad B and quit to title.
  **Calls:** main's viewers still close at once (`UiFocus.release`: focus returns the same
  frame, as ANIM made it); W8a's "one direction per material" page rule is not ported (main's
  ANIM directions stay); PauseMenu is not in the group (it pauses the tree itself).
  `GlassScrim` + `shaders/glass_blur.gdshader` (from the tag; it includes rc_common) is the
  v2 SCRIM (#02030A 55% + 6 px blur), opaque `HighContrast.BG` under high contrast.
- **UiWrap.whole_words**, and no `AUTOWRAP_WORD_SMART` / `ARBITRARY` left under `scripts/`
  (tested): Labels go through whole_words (never narrower than their longest word), Buttons
  and the SAVED note wrap at words (`AUTOWRAP_WORD`).
- **FitScroll** (the kit piece, from W8a) with WF's pre-layout guards, and ScrollHint's
  `degenerate_view`. WF's cap of the snap reserve at a row's share of the view is **not** ported:
  main's ANIM-R6 C8 measures a row's share against the view with no snap, and the cap cut the
  YOUR NODES snap at 2.0 short of the row (`test_anim_r5_city`
  `test_your_nodes_never_ends_in_a_cut_row`: 32 px of a 44 px row). **Call:** main's ScrollHint holds
  its view at its own least height (ANIM-R6 C8), which overrode FitScroll's sizing; FitScroll now
  sets it through `ScrollHint.set_view_min`. No view uses FitScroll yet: the shared panels
  (TerminalWindow, ZinePanel) adopt it in their restyle (ART-4 / ART-10).
- **PaperInk** on main's paper pieces: Polaroid (edge, caption, glitch bars), Toast (words, edge,
  mark), CrewCard (words, edge, HP strip, tape), ZineNote (words, edge, tape) and the subtitle
  paper (opaque, speaker in INK). CaseFileCard, RunReceipt and AchievementBadge are art-pass only.
- **MotionSkip:** it still owns the one-press skip; nothing new registers a helper. `kit_state`,
  `refusal_mark` (the refused flash answers the refused press) and `ui_focus` (the pad focus
  scale is a focus state) join `test_anim_r6_rules`' NOT_SKIPPABLE list and STYLE_GUIDE 5.5
  (outside F's files: one line each).
- **Windowed check** (review pack, title / HQ / Mainframe / Options / Loadout, 1.0, pad and mouse,
  1280x720): the lime brackets sit 7 px outside the focused menu line and option row; the
  Mainframe's prompt bar shows the Xbox glyphs (A green, X blue, B red, Menu) beside their verbs;
  its card tip reads "pick it up and move it"; the Loadout modal shows whole. No ERROR in the logs.
  Seen there: the pad focus scale on a full-width Options row moves its words about 18 px and puts
  the brackets past the panel's edge (M13 scaled them too); ART-10's Options restyle should give
  full-width rows `UiFocus.META_NO_SCALE` or narrower rows.
- **Visual QA harness:** `tools/visual_qa/review_pack.gd` needed **no change**: it already reads
  `PageTransition.MODAL_GROUP` and the `GlassScrim` class by name when they exist.
- **Tests:** `tests/unit/test_art0_kit_states.gd` and `test_art0_kit_words.gd` (fast). Ported:
  six states (on main's three drawn components), live states (on StickerButton), hover / pressed
  boxes (main's kinds, no glow asserts: main's normal boxes have no glow), refusal mark, focus
  brackets (3 px / 7 px), focus scale, cards / tilted controls, the four pad glyph tests, prompts
  as glyphs, pad wording, mouse words go through for_input, focus tip, pad pages (mouse words
  only), no mid-word wrap, whole_words, crew card tag at the ceiling, both FitScroll tests, paper
  inks, paper pieces in and out of high contrast (main's Polaroid / Toast / CrewCard), modals in
  budget, no page change under a modal, scrim opaque in high contrast. New: refused entry and
  tier, force_native, brackets on every focus type, high contrast thickens brackets,
  headless / mouse never scale, glyph set follows Settings, headless modals, the confirm on its
  scrim with pad reachability inside it, scrim shader include, drag tips have pad lines, the
  hint ignores a degenerate view. **Dropped** (looks restyled later, or pieces main lacks):
  from `test_art_w2_components.gd` — `test_every_button_variant_has_every_state_box`,
  `test_a_standalone_button_is_its_label_plus_32`, `test_menu_item_uses_a_type_step`,
  `test_disabled_labels_keep_4_5_to_1` (W2 button variants / StyleBoxLocked: ART-1 / ART-10),
  `test_the_toast_never_overlaps_a_bottom_button`, `test_one_toast_style_for_every_caller`,
  `test_toast_timings_follow_the_bible` (the W2 toast restyle), `test_tooltips_fold_to_26_to_36_columns_and_long_text_uses_the_body_face`,
  `test_a_tooltip_never_repeats_its_title` (W2 tooltip restyle), `test_stamp_hold_follows_the_reading_rule`,
  `test_a_stamp_says_three_words_at_most`, `test_one_banner_per_region_the_rest_queue`,
  `test_a_zine_stamp_word_never_falls_under_caption` (zine stamp / BannerQueue skins),
  `test_the_status_glyphs_are_stat_icons`, `test_status_icons_draw_filled_and_open` (W2 icon
  redraw, ART-1), `test_saved_is_a_type_step_with_4_5_to_1` (SAVED restyle),
  `test_inputs_emit_expose_value_and_take_focus`, `test_toggles_line_up_16_px_right_of_the_longest_label`,
  `test_the_tile_picker_moves_its_cursor_with_the_keys` (ZineToggle / ZineSlider / Stepper /
  TilePicker / CodeField: zine inputs main lacks, ART-10); from `test_art_wf_kit.gd` —
  `test_tile_names_wrap_at_words_and_fit_at_every_scale`, `test_wrap_words_never_breaks_a_word`
  (TilePicker), `test_a_sticker_yields_its_type_step_before_passing_its_share`,
  `test_without_a_cap_a_sticker_grows_as_before`, `test_respin_at_2_is_capped_and_1_0_is_unchanged`
  (sticker max_share, combat restyle ART-3), `test_the_polaroid_caption_always_fits_whole`,
  `test_a_polaroid_caption_abbreviates_by_w5s_rule` (W5 caption; main has ANIM-R6 C6's),
  `test_a_status_stamp_carries_its_stat_icon` (combat stamps, ART-3), `test_paper_pieces_use_the_paper_inks`
  (CaseFileCard), `test_a_first_run_on_a_deck_starts_the_city_at_quality_1`, `test_the_city_reads_the_deck_tier`
  (area C / ART-1), `test_tracking_is_px_per_type_step_and_never_rounds_away`,
  `test_a_tracked_font_carries_the_step_spacing` (area E); from `test_art_w9f_sweep.gd` —
  `test_every_layout_test_runs_at_the_text_scale_ceiling` (area C), the bracket-letter half of
  `test_pad_pages_speak_pad_and_show_their_prompt_bar` and `test_a_fight_has_a_pad_prompt_bar_and_glyphs_not_brackets`
  (SEND IT's glyph and the fight's prompt bar: combat restyle, ART-3), `test_netrun_hookups` (W8b),
  `test_flatline_is_a_city_context_that_blends_and_gives_the_colour_back`,
  `test_run_end_greys_the_whole_city_and_hands_it_back`, `test_clear_campaign_progress_forgets_the_lean`
  (city, ART-5), `test_settle_calls_any_settle_motion_and_the_stages_leave_typing_meta`
  (W9F run / campaign end stages main lacks), `test_empty_subtitle_band_holds_one_line_and_grows_when_a_line_comes`,
  `test_a_subtitle_page_never_shrinks_under_caption`, `test_polaroid_caption_band_keeps_the_floor_caption`,
  `test_spinner_hub_name_fits_the_disc_whole`, `test_spinner_viewer_price_on_upgrade_lettering_and_circle`,
  `test_modem_cards_window_is_never_a_quarter_empty_in_one_column`, `test_the_upgrade_viewer_stays_on_the_canvas_at_two`
  (screen restyles, ART-3 / ART-4 / ART-9), `test_lint_export_cuts_text_to_its_scroll_view_and_sees_modals`,
  `test_lint_report_uses_on_screen_size_and_leaves_out_hidden_text` (area D), `test_reduce_motion_shakes_nothing`
  (area C); from `test_art_w8a_menus.gd` — `test_glass_window_type_comes_from_the_scale_and_has_a_scrim`,
  `test_a_long_title_never_widens_its_window`, `test_panels_fit_their_content_and_scroll_past_the_cap`
  (TerminalWindow / ZinePanel restyle on FitScroll, ART-4 / ART-10), `test_glass_slides_from_the_right_and_paper_drops_whatever_the_caller_asks`
  (W8a direction rule, not ported), `test_reduce_motion_cross_fades_in_place` (area C), and the title-family
  look tests (`test_the_logo_is_baked_art_with_a_drip_that_stops_under_reduce_effects`,
  `test_the_title_has_one_primary_one_note_one_scrawl_taped_to_the_menu`, `test_never_sleep_is_art_with_a_subtitle_in_other_languages`,
  `test_slots_are_case_files_and_delete_is_danger_with_a_confirm`, `test_options_use_kit_components_one_size_and_aligned_toggles`,
  `test_codex_is_a_two_column_spread_of_short_lines_with_glyphs`, `test_stats_show_earned_and_unearned_badges_a_grid_and_receipts`,
  `test_pause_fits_its_content_one_primary_and_the_code_in_a_field`, `test_title_pages_fit_at_every_text_scale`,
  `test_every_option_row_stays_inside_the_view_focused_with_pad_or_mouse`: ART-10).
### 2026-10-05 — Art direction — ART-0 names pass, part 3
Applies "2026-10-05 — Designer rulings: SANDBOX / TROJAN / NULL and five Heat bands" (ART-0 B3).
Internal names follow the display names; no aliases, no migrations (old saves naming `shield_5`,
`deploy_1` or `miss` fail to load through the existing "can't load" path). `tests/unit/test_names_pass.gd`
(PART3 table) sweeps player strings and code for the old words.
- **Slice programs (ruling 1).** `RC.SliceType` is { SHIM, OVERFLOW, DEFRAG, DETOUR, SANDBOX, TROJAN,
  HOTFIX, INFECT, NULL } (same positions, so content keeps its ints). Content ids and files:
  `sandbox_5`, `sandbox_8` (were shield_*), `trojan_1` (deploy_1), `null` (miss); display names
  "Sandbox 5", "Sandbox 8", "Trojan 1", "Null"; their wheel sub-resources (`*_slot_null`, ...),
  the generators under `tools/content_gen/`. Enums and identifiers that named the slice follow:
  `RC.SlicePick.RANDOM_NON_NULL`, `RC.Trigger.ON_NULL_SLICE`, `Palette.SLICE_NULL` /
  `SLICE_TROJAN`, `CombatState.null_resolved` / `RunState.null_resolved` (Cold Exit), the combat
  event `"null"` (was "miss"), the operative bark trigger `bark:null`, the motion id
  `precision_null_static` (table, REQUIRED_IDS, motion lab demo `null`), `WheelView.play_null_static`.
  Schema: `CampaignConfigData.miss_slice_overwrite_price` → `null_slice_overwrite_price` (150) and
  `mirror_deploy_base` → `mirror_trojan_base` (6), checked in `schema_smoke_checks.gd` `_art0` with
  the enum's keys.
- **Words and tags.** Whole words (`Palette.SLICE_WORDS`) SANDBOX / TROJAN / NULL; compact tags
  (`Palette.SLICE_NAMES`) **SBOX / TRJN / NULL**, four letters like part 2's SHIM / OVFL / DFRG / DTOR /
  HFIX / INFC, so they take the room those tags already fit in at text size 2.0 (the mono face:
  test `test_b3_the_new_tags_fit_like_the_others_at_text_size_2`). Player text names the
  programs the way part 2 does: upper case in rules text ("The NULL slice restores 2 RAM",
  "DEFRAG and SANDBOX slices", "non-NULL slice", codex "SANDBOX: gains shield."), title case in
  wheel lists ("Shim, Shim, Defrag, Trojan, Trojan, Null"), the barks "Null. Rerouting power.",
  "Perfect Trojan. Something of mine is inside theirs now."; GDD 2.3, 2.4, 2.6, 5.2, 6.2, 10,
  11 and A.3 follow (the v0.9 change line "Miss precision tier removed" is history and stays).
- **Kept meanings (allow-listed in the sweep).** *Shield* the resource: block / shield, the
  shield cap 15, "+%d SHIELD", "SHIELD %d", hubs that "gain 4 shield", Shield Wall, Shield Cache,
  EffectType.GAIN_SHIELD; a SANDBOX slice *gains shield*. *Deploy* the verb: drones and Armory
  assets ("Deploy armory asset"), EffectType.DEPLOY_DRONE, the `"deploy"` combat event and
  `bark:deploy` (a drone deployed, by a TROJAN slice or a card). *Miss* in prose: "Miss a payment",
  "the cameras miss", "make a miss count", the precision rule "no miss tier".
- **Five Heat bands (ruling 2).** COOL / NOTICED / FLAGGED / HUNTED / PURGE, starting at the MAJOR
  levels and the PURGE level of `heat_thresholds` (25 / 50 / 75 / 100); no threshold or number
  changed and none is written in code. New `CampaignConfigData.heat_band_levels()` (a method, no
  field; smoke-checked in `_art0`) and `HeatRules.band_levels(campaign, config)`; the HQ's
  wanted poster and the combat top bar pass the latter. `HeatPoster.BAND_WORDS` gains "purge"
  (the index caps follow the array, no more `3`); `Palette.HEAT_BAND_COLORS` gains a fifth entry,
  HARM again: PURGE reuses HUNTED's colour (and the poster's red banner, by its existing clamp)
  until ART-1 with its own word. Call: the PURGE band starts where the Purge actually fires,
  so at ICE 17+ (PURGE_THRESHOLD 90) it reads PURGE from 90; `Palette.heat_band` without a
  campaign reads the config's 100. Unchanged: `CampaignState.heat_majors_crossed` (rules
  scaling, CORRUPTED) and the HQ backdrop's search lights (MAJOR count), and `consequence()`
  (the MAJOR modifiers in force; the PURGE event text is a one-time event). GDD 4.3: the
  duplicated "Bands" line is one line, with the ICE 17 note. Tests:
  `test_b3_every_heat_band_boundary_maps_to_its_word` (24/25, 49/50, 74/75, 99/100),
  `test_b3_the_poster_shows_purge_at_100`, `test_b3_the_purge_band_starts_where_the_purge_fires`;
  `test_heat_color_bands_follow_the_config_majors` caps at PURGE now.

### 2026-10-05 — Art direction — ART-0 names pass, part 2 (D2–D8, D11–D12)
Applies "2026-10-05 — Designer rulings: names for M14" (ART-0 area B part 2). Internal names follow
the display names; no aliases, no migrations. `tests/unit/test_names_pass.gd` (PART2 table) sweeps
player strings and code for each item's old words.
- **D2 slice programs.** `RC.SliceType` is { SHIM, OVERFLOW, DEFRAG, DETOUR, SHIELD, DEPLOY, HOTFIX,
  INFECT, MISS } (same positions, so content keeps its ints). Slice content ids and files follow:
  `shim_*` (was atk_*), `overflow_*` (crit_*), `defrag_*` (def_*), `detour_*` (evade_*), `hotfix_*`
  (heal_*); display names "Shim 14", "Overflow 24", "Defrag 12", "Detour", "Hotfix 6". Whole words
  (`Palette.SLICE_WORDS`) are the program names; the compact tags (`Palette.SLICE_NAMES`, slot lists
  and shop tiles) are SHIM / OVFL / DFRG / DTOR / HFIX / INFC (SHD / DEP / MISS kept): the whole
  words in those tiles pushed the shop's spinner onto LEAVE MAINFRAME at text size 1.6. Firmware,
  codex and GDD 2.6 texts name the programs. Kept on purpose: the *evade* mechanic
  (EffectType.EVADE, a card's "Evade the next incoming attack", the "%s EVADE" charge chip), *heal*
  as an effect ("Heal 6"), *attack* as a verb, and the damage beats' `crit` flag (a big-hit number
  style, set by OVERFLOW slices and Perfects alike). ~~SANDBOX / TROJAN / NULL (the art pass's SHIELD /
  DEPLOY / MISS) are not renamed: the ruling keeps them out of D2; the enum keeps SHIELD / DEPLOY /
  MISS (question below).~~ *Superseded (ART-0 audit B5):* the designer ruled SANDBOX / TROJAN / NULL
  ("Designer rulings: SANDBOX / TROJAN / NULL and five Heat bands"); ART-0 B3 renamed the enum and words.
- **D3 Meridian.** The RAM-drain slice is `priority` (`content/slices/priority.tres`, "Priority", its
  wheel sub-resources `*_slot_priority`; codex and descriptions). A corporation's own program word
  lives in `Palette.CORP_SLICE_WORDS` (view words, `# TR`), read by `Palette.slice_word(type,
  corporation_id)`; the combat tags over a wheel and its odds use the wheel's corporation
  (`combat_scene.corp_of`): Meridian's OVERFLOW reads **AIRMAIL** (test
  `test_a_meridian_wheel_says_airmail_for_its_overflow`). JUDGEMENT: no id, string or code carried
  it on main; the sweep keeps it out. Kept as flavour: the Tariff Collector enemy, the Tariff
  Calculation Office Site, "Tariff season" and tariffs in prose (allow-listed).
- **D4.** INERTIA is **WEIGHT**: `shim_8_weight` (was the inertia strike), the codex entry "Weight",
  the Cargo Hauler's text, GDD 8.4b. Solace's HOTFIX reads **GROWTH** through
  `Palette.CORP_SLICE_WORDS` (test `test_a_solace_wheel_says_growth_for_its_hotfix`).
- **D5 Central Server.** The boss Site is the corporation's Central Server: `RC.SiteObjective.CENTRAL_SERVER`
  (was BOSS, same position), `CityMapOverlay.KIND_CENTRAL_SERVER` ("central_server"), the map key,
  tooltips and HQ badge (CENTRAL SERVER). Each Central Server's name is its Site's content string
  and id: The Genome Core (`the_genome_core`, Solace), The Master Manifest (`the_master_manifest`,
  Meridian), The Panopticon (`the_panopticon`, Halcyon), Launch Control (`launch_control`,
  Orbital). REBEL_CELL's stays DISPATCH (`dispatch_core_site`): GDD 8.5 names no final server, only
  that the final boss is DISPATCH. The boss enemies keep their names (Renewal Engine, The Manifest…)
  and the run kind "boss" stays (it is the fight). GDD 11.7 and the summary; the part-1 "(name
  pending, D5)" note is gone (test `test_d5_each_central_server_has_its_name`).
- **D6 Firmware.** The Mainframe's top-left window is FIRMWARE (was MICROCHIPS); the small spinner's tip
  says "Drag Firmware or a slice onto a slot"; comments and the drag test
  (`test_a_firmware_chip_dropped_on_a_slot_matches_the_socket_list_and_buy`) follow. "Chip" stays as
  the drawing's word for a Firmware tile.
- **D8 WEAK.** `RC.PrecisionTier.WEAK` (was PARTIAL, same position), the tier tag WEAK, codex text, GDD
  2.4 / 10. Schema: `CampaignConfigData.partial_multiplier` → `weak_multiplier` (0.5; checked in
  `schema_smoke_checks.gd` `_art0`). Motion id `precision_partial` → `precision_weak` (table,
  REQUIRED_IDS, motion lab). "Partial" in other meanings (a partial cover, a partial patch) stays.
- **D11 Heat bands.** ~~Main already shows the bands ART_BIBLE v2 §2.8 / §3.15 sets (COOL, NOTICED 25+,
  FLAGGED 50+, HUNTED 75+; the bible's NOTICED is the "couple of alarms" band and the thresholds stay),
  so no band or threshold changes; the five-band reading is asked under "Open questions for the
  designer".~~ *Superseded (ART-0 audit B5):* the designer ruled five bands; ART-0 B3 built them
  ("ART-0 names pass, part 3"). Added: `Settings.heat_glitch` (off by default, saved in settings.json, listed in
  `Settings.VFX_TIER_EXEMPT`) and its row on the current panel (Accessibility, "Heat glitch (the
  screen distorts as Heat rises; off by default)"); ~~the glitch itself comes in ART-3 / ART-5~~
  *(annotated, ART-0 audit B1: the glitch was built by the ART-0 audit fixes, `HeatGlitchLayer`)* (test
  `test_the_heat_glitch_extra_is_off_by_default_and_round_trips`). settings.gd and settings_panel.gd
  are area C's files: additions only.
- **D12 RESPIN / UNDO.** The respin sticker already read RESPIN; its tips and the tutorial no longer say
  "checkpoint" ("UNDO stops here"). The undo block shows on UNDO: the sticker's tooltip says why it is
  off (`combat_scene.UNDO_BLOCKED`), and an undo pressed with nothing to undo (Ctrl+Z, the pad)
  shows that note over the UNDO sticker instead of the notes column (`show_undo_block`); the core's
  refusal text reads "Nothing to undo: a random event came since (UNDO stops there)". The rules word
  checkpoint stays internal (CombatSession, GDD 2.10). Test
  `test_respin_reads_respin_and_the_undo_block_shows_on_undo`.

### 2026-10-05 — Art direction — ART-0 names pass, part 1 + saves folder
Applies rulings 5, 6.1, 6.2 and 6.5 of the entry below (ART-0 area B, items B1–B4). Internal
names follow the display words; no aliases, no migrations.
- **Raid words (6.2).** `GridState.SiteStatus.TAKEN` (was SEIZED), `GridState.Condition.DOWN`
  (was DISABLED), `GridState.is_taken`, `RaidResult.taken` / `.down`, node outcomes and raid
  event types `"taken"` / `"down"`, `RC.RuleModifierType.TAKEN_RAID_STRENGTH_PCT` (same enum
  position, so `campaign_config.tres` keeps its int), the view constants (`RaidVerdict.TAKEN`,
  `DOWN`, `CELL_HOLDS`, `BREACHED`; `InfluenceSpread.MARK_TAKEN` / `MARK_DOWN`;
  `CityInfluence.WEIGHT_TAKEN` / `WEIGHT_DOWN`; the feed's `FEED_TAKEN` / `FEED_DOWN`) and the
  tests that named them. The raid verdict says **CELL HOLDS** when nothing is lost (was ALL HOLD)
  and **BREACHED** when the home server falls (was CAMPAIGN LOST; the banner already used the
  verdict's word); a raid with losses still lists them (HOME -5 / 1 DOWN / 1 TAKEN), as GDD 7.2
  "the summary shows DOWN/TAKEN nodes". Player text uses the upper-case state words ("TAKEN by
  a raid", "Bring the DOWN node back online", "The home server is BREACHED. Campaign lost.").
  Unchanged on purpose: the UI-control "disabled", Hub Breach's "disabled 1 turn", and the
  freight flavour (Freight Seizure, Asset Seizure, "Seized goods": allow-listed).
- **Mainframe (6.5).** `RC.InfilNodeType.MAINFRAME`, `MainframeSign`
  (`scripts/ui/kit/mainframe_sign.gd`), `tools/design_lab/mainframe_backdrops.*`, motion ids
  `mainframe_sign_warmup` / `mainframe_sign_strike` / `mainframe_sign_flicker` /
  `mainframe_trace`, and every string. Schema: `CampaignConfigData.map_modem_layers` →
  `map_mainframe_layers` (checked in `tools/schema_smoke_checks.gd` `_art0`). The shop's top-bar
  title is **MAINFRAME SHOP** and its exit tag **LEAVE MAINFRAME**: the longer words
  (MAINFRAME CYBER SHOP, LEAVE THE MAINFRAME) wrapped at text size 1.6 and pushed the shop's
  deck viewer and a control off the canvas (`test_end_state_layout_is_the_instant_layout_at_every_text_size`,
  `test_the_new_pieces_keep_the_layout_at_each_text_size`); the sign keeps CYBER SHOP. The sign
  stacks its 9 letters in the room its 5 had (the rows shrink with the word, as the code already
  did). The boss gate is written "Mainframe Gate (name pending, D5)" in the GDD until the
  designer rules on D5. Timeline images and history docs keep the old word.
- **Customs Seal (6.1).** The Manifest's hub `customs_seal` / "Customs Seal" (sub-resources
  `hub_customs_seal`, `te_customs_seal`); rules unchanged
  (`test_the_manifest_customs_seal_gains_4_shield_each_turn_unless_breached`).
- **Sweep.** `tests/unit/test_names_pass.gd` fails on the old words in strings.csv English, in
  every content `.tres` string, and (for the old names as code) under scripts / scenes / tests /
  tools / content.
- **Saves folder (S0, ruling 5).** Schema: `CampaignConfigData.save_dir_source`
  (`res://saves`), `save_dir_export` (`user://saves`), `replay_subdir` (`replays`),
  `write_replays` (true), checked in `_art0`. `SaveService` saves under `save_dir_source` when
  running from source (`OS.has_feature("editor")` or not `template`) and `save_dir_export` in an
  exported build; making a folder under the source folder writes `saves/.gdignore` so Godot
  never imports it; `.gitignore` has `/saves/`. GUT runs keep their per-process folder under
  `user://saves`. `SAVE_VERSION` is 2; the migrations table ships empty, so a version-1 file is
  refused by `load_dict` (push_error, `{}`): the title shows the slot empty and CONTINUE
  returns false, no crash. Replays: new pure `CombatReplay` (`scripts/core/combat_replay.gd`)
  records what the session already keeps (setup, seed as a string, action history, outcome,
  state hash as a string) and replays it; `CombatEngine.submit` calls
  `SaveService.record_replay` when a fight ends, which writes `saves/replays/replay_<seed>_<ms>.json`
  only on source runs, never in a test (`write_replay(session, dir)` for a test that asks).
  A replay is rebuilt with the shipped config and the content registry (the resolver every
  fight uses). Tests: `tests/integration/test_saves_folder.gd`; `test_save_service.gd` updated
  (no `SAVE_DIR` constant: the folders are config).
- Side effect worth knowing: tools run from source (storyboard, demos, the motion lab) now keep
  their saves in the checkout's `saves/` between runs instead of a per-run APPDATA; delete the
  folder for a clean title screen.

### 2026-10-05 — Designer ruling: reuse the art pass's assets, never redraw them
The designer saw hand-drawn stand-ins (e.g. the raid HEAVY vehicle icon drawn as a half circle) where the
art pass has approved images (`round22_raid_world/vehicle_icons_v4`). Ruling: **any icon, sprite, texture,
model or sheet the art pass already produced is used as is** — exported by running the concept's own
generator script on tag `art-concepts-r43` (unchanged drawing code; an export wrapper may split a sheet into
per-item transparent PNGs at 2×) or sliced from the approved image — never redrawn by hand or rebuilt
procedurally. Shaders may tint, fill, drain or animate an asset, not replace its shape. Procedural drawing
is allowed only where no concept asset exists or the shape must move in a way an image can't, and each
such case is listed with its reason. Every asset carries a manifest (source script / image, tag). An
asset-parity sweep replaces the stand-ins already merged (Groups 1–4); every running agent applies it now.

### 2026-10-05 — Designer ruling: rolling audits stopped; one audit at the end (risk accepted)
The designer found the rolling audits premature: they are stopped (the Group 1 vertical auditor was
stopped mid-run) and **audits run only once, after the art integration (ART-12)**, the designer accepting
the risk. The reports already written stay in `docs/handoff/m14_audit/` (ART-0 horizontal, Group 1 naive,
Group 1 horizontal) as input to that final audit; the ART-0 fix agent already running finishes; findings
already passed to building agents stay with them; the other findings wait for the final audit.
Supersedes item 1 of "rolling audits as groups merge"; its item 2 (Gantt in the hourly report) stands.

### 2026-10-05 — Designer ruling: rolling audits as groups merge; Gantt in the hourly report
1. **Rolling audits** (partly reverses "no audit until the end"): when an M14 group is merged (ART-0, Group 1,
   Group 2, Group 3, Group 4), its vertical / horizontal / naive auditors review that group on main while the
   other groups keep building (report only; rules in `docs/handoff/m14_audit/auditor_common_rules.txt`).
   Findings go to fix agents by owning area at once (nothing deferred, P3s included). The audit after ART-12
   remains one loop over all of M14 and should then be small. ART-0 is plumbing with no new look, so it gets
   the horizontal audit only.
2. **Hourly report** includes the Gantt of agents and dependencies with the critical path and the current
   finish estimate.
Context: the critical-path re-plan (Group 3 wave 2 started early: 5b landmarks, 8p HQ compounds; 5a/5c/5d on
the city spike's interim pick) moved the estimate from Thursday 18:00 to about Wednesday 12:00.

### 2026-10-05 — Designer rulings: D10, D13, D14 confirmed; the art pass design is correct
1. **D10, D13, D14 confirmed** at their plan defaults: title verbs BREACH / DISABLE / OVERTHROW with
   **SIMULATE** for the tutorial; an "Always show all nodes" setting with hidden-node visibility on the
   netrun map; the netrun presentation rules of plan §3.1 D14 (within the current GDD 4.2 rules).
2. **Standing ruling: assume the art pass design is correct.** From now on, where a view, word, layout,
   look or presentation rule differs between the game and ART_BIBLE v2 / the locked concepts
   (`docs/concepts/DIRECTION_REVIEW.md` locks, `docs/art_reference/`), the art pass wins without asking the
   designer; the change is logged in the area's DECISIONS entry and any GDD presentation line is updated
   citing this ruling. Mechanics the art shows but the rules do not have (plan §3.2 G1–G16) still follow
   ruling 8 of pause point 0 (re-evaluated after M14).

### 2026-10-05 — CI paused for M14 (designer: "stop those CI failures")
GitHub CI (`.github/workflows/ci.yml`) ran the whole suite in one process on every push to main; with
M14's frequent pushes each run outran the 30-minute job limit and was cancelled (reported as failures),
and the runs queued behind each other. The trigger is now `workflow_dispatch` only (run by hand from the
Actions tab), with a concurrency group that cancels a superseded run. Restore `push: [main]` and
`pull_request` after ART-12, together with the one M14 full-suite run; consider sharding the CI suite
(`tools/run_tests.py -j 4`) instead of single-process GUT so it fits the limit.

### 2026-10-05 — Designer rulings: D15–D17 defaults; Sonnet for mechanical tasks
1. **D15–D17 confirmed at their plan defaults** (plan §3.1): D15 combat HUD v4 result chips beside each HP
   replace the forecast tags and NEXT plates — the chip is the preview, GDD 2.10 still holds; D16 every
   card-caused effect stems from the card's slap and dissolve on the target wheel, never from the hand;
   D17 boss fight backdrop = the corp HQ, regular fights at the target Site, fight won → the building's
   lights turn Cell colours. GDD 2.10 / 9.2 wording follows in Group 2's DECISIONS entries.
2. **Agent models:** mechanical tasks (renames and sweeps, docs landing, test re-pointing, lint-baseline
   and merge follow-ups, wording-only docs) run on Sonnet; visual, rules-sensitive and judgment work
   (shaders, view ports, the city, merges touching ANIM motion, the audit) stay on Opus.

### 2026-10-05 — Designer ruling: groups in parallel, fast checks only, done within days
The designer asked to start ART-2 (Group 2) in parallel with Group 1, to skip every non-fast test run and
the audit until **all** art groups are done, and to finish M14 within a few days. From now:
- **Checks during M14:** only the fast checks (`checks_fast.sh`) at hand-back and at every merge, plus each
  agent's own test scripts. **No full-suite run per group.** One full-suite run (in isolation) and the one
  audit loop happen after ART-12, before "M14 complete". Supersedes item 1 of "one full run, one audit at
  the end" for the groups; its item 2 stands.
- **Groups overlap:** a group starts before the previous one merges. Its agents build on main as it is and
  `git merge main` whenever the orchestrator says a foundation landed (palette/theme 1A, material kit 1B,
  glyphs 1C, city spike 1D); views switch to the new foundations as they arrive.
- **Designer reviews are non-blocking:** each group's report goes to the designer when it lands; work on
  the next group continues meanwhile; rulings are applied as they come.
- **Agent cap raised** from 4–5 to about 9 at once; windowed captures limited to 1 window per agent while
  more than 5 agents run.
- **Pending presentation rulings** for Group 2 (plan §3.1 D15, D16, D17) are built on their plan defaults
  and listed in the next designer report for confirmation.

### 2026-10-05 — Designer ruling: one full run, one audit at the end
1. **One full-suite run** instead of three: each ART group (and ART-0) ends with one full run in isolation
   (`process/checks.sh`, `RUNS=3` only after a failure, to tell a flaky test from a real one; the runner
   already reruns failing scripts alone). Supersedes the "×3" in "Designer ruling: check cadence for M14".
2. **No per-batch or per-group audits.** The vertical / horizontal / naive audit loop runs **once**, after
   ART-12, over every M14 change, with its fix rounds until CLEAN (nothing deferred, P3s included). The
   designer review after each group stays. Supersedes the per-group audit in "Designer ruling: M14
   regrouped" and plan §4.1 step 5; MILESTONES M14 and the ART-0 brief updated.

### 2026-10-05 — Designer rulings: SANDBOX / TROJAN / NULL and five Heat bands
1. **Default accepted:** the remaining slice programs follow ART_BIBLE v2 §3 (rounds 32–34): SHIELD →
   **SANDBOX**, DEPLOY → **TROJAN**, MISS → **NULL**, display and internal names alike (ruling 5 of pause
   point 0). The names-for-M14 entry's "SANDBOX, TROJAN, NULL unchanged" meant "these program words are
   already settled", not "keep SHIELD / DEPLOY / MISS".
2. **Changed: five Heat bands.** The game is balanced around the five Heat levels the rules already have
   (GDD 4.3: below 25, MAJOR 25 / 50 / 75, PURGE 100), so the bands follow them: **COOL** 0–24,
   **NOTICED** 25–49, **FLAGGED** 50–74, **HUNTED** 75–99, **PURGE** 100. Thresholds unchanged; no new
   threshold. ART_BIBLE v2 (four bands, §2.8 / §3.15) is updated later to match ("art can be updated
   later"); until then the PURGE band reuses HUNTED's look with its own word. Supersedes the D11 wording
   about a new NOTICED band below 25 and area B's four-band call.

### 2026-10-05 — Designer ruling: reduce effects as a project-wide shader global
Asked after area E merged (E made `reduce_effects` a per-material uniform set by `ShaderReduce`, because
M13's global lives in `project.godot`, a designer file). Ruling: add the global to `project.godot`
(`[shader_globals]` `reduce_effects`, float, 0.0, as on `art-m13-final`). Agents may stage
`project.godot` **for that entry only** (area E2, ART-0); every other `project.godot` change still needs
the designer. `rc_common.gdshaderinc` reads the global; `Fx.apply_settings` sets it with
`RenderingServer.global_shader_parameter_set`; `ShaderReduce` is removed or reduced to what the global
cannot cover.

### 2026-10-05 — Designer ruling: M14 regrouped
The designer asked why integrating a one-week art pass would take 3–4 weeks. The reason: the locked v2
direction exists only as concept stills and GIFs (43 rounds, 5,915 files under `docs/concepts/`; after
`art-m13-final` the concept rounds added 5 design-lab files, 261 lines, to the game). The M13 code implements
the superseded v1 look, so v2 is built in Godot, not merged. The estimate was driven by 13 separate
batch → audit → fix → review loops. Ruling: **regroup M14** into ART-0, four groups and the final sweep:
Group 1 Foundations (ART-1); Group 2 Combat (ART-2, 3, 4); Group 3 City (ART-5, 6, 7, 8; ART-5's city
model first); Group 4 Screens (ART-9, 10, 11); Final (ART-12). A group's batches are built in parallel
(at most 4–5 agents), with one audit round and its fix rounds to CLEAN, one full suite ×3 in isolation,
and one designer review per group. Batch contents and acceptance lines are unchanged. MILESTONES M14
and plan §4 annotated. Estimate given at the time: about 1.5–2.5 weeks, re-estimated after ART-0.

### 2026-10-05 — Art direction — ART-0 tokens and VFX tiers (salvage S3 + S4, area E)
Ported from tag `art-m13-final` (W1, W6, WF items 6 and 9, W9F `track_label`) onto main's
files by hand; ANIM behaviour kept. No view restyled; values stay main's (ART-1 sets v2).
- **Tokens (S3):** `Palette` gains the semantic tokens (HARM, GAIN, HARM_INK, GAIN_INK,
  PROTECT, WARN, FOCUS, DISABLED, TEXT_HI/MID/LO, SCRIM, HEAT_FLAGGED, AUTO), named corp and
  slice constants, `CLASS_ACCENTS` / `class_accent`, `hp_color`, `heat_band` / `heat_color`
  (from the config's MAJOR levels), `luminance` / `contrast` / `over`, `FONT_BODY(_MEDIUM)`.
  Values: where main had one it is kept (`CORP_ORBITAL` stays #DDE3FF, not M13's #7FA8FF; the
  slice and corp hues unchanged); the new semantic tokens take the M13 values, which ART_BIBLE
  v2 §2.2 keeps; the class accents take the M13 values until ART-1 applies v2 §2.5. No view
  reads the new tokens yet.
- **Type (S3):** `UiTheme` gains the type steps (CAPTION..HERO, HERO_MAX), line heights,
  `font_px` / `font_px_at`, `line_spacing_px`, tracking (fraction and `TRACKING_PX` per step,
  `tracking_step_px`, `tracked`, `step_of`, `track_label`), spacing tokens and the `BodyText`
  variation (IBM Plex Sans Condensed, OFL in `assets/fonts/`). HeaderLabel reads its size
  from the TITLE step (the same 22 x scale). Not ported: the W2 button restyle, HotButton's
  scaled size and the tracked HeaderLabel / Primary fonts (looks, ART-1..12).
- **MSDF switch (call made):** the fonts' `.import` files are tracked (force-added) with
  `msdf_pixel_range=16`, but `multichannel_signed_distance_field` stays **false** with
  `Palette.FONTS_MSDF = false`. With MSDF on, main's text took different line metrics: the
  windowed capture showed multi-line text a little tighter (the combat tutorial note), and
  three checks failed: `test_horizontal_pass21_screens` (radio whole lines, 8.15 lines),
  `test_anim_r5_netrun` (a page paged at 14 lines instead of 15) and `test_anim_r5_city`
  `test_your_nodes_never_ends_in_a_cut_row`, which crashed the process (signal 11 after a
  flood of "Object was deleted while awaiting a callback": the raid's YOUR NODES list at 1.6).
  All three pass with MSDF off; main passes them. ART-1 turns the switch on (the constant
  and the five `.import` lines) together with the layouts it moves, and should find why the
  YOUR NODES list crashes under the new metrics.
- **Not ported:** `CorpPattern` and `Palette.corp_pattern_id` (ART_BIBLE v2 §2.4 gives each
  corp a material and crest instead of v1's patterns; the boss-phase burst carries long and
  short dashes as its non-colour cue); the W6 library shaders (glass_blur, crt_overlay,
  paper_burn, glitch_dissolve, marker_stroke, halftone: zine / v1 looks); the per-slice hit
  shapes (W6 item 5, a look; v2 §5 restyles hits as bits).
- **VFX tiers (S4):** `UiMotionEntryData.tier` (T0-T4, default T1; schema change, checked in
  `tools/schema_smoke_checks.gd` `_art0_tier`) is written on every `ui_motion.tres` entry:
  M13's tier per id where M13 had the entry; main's newer entries: `flight_land_pulse` T1,
  `tutorial_next_pulse` T1, `flight_lift_share` / `flight_fade_share` /
  `choice_stamp_down_share` / `choice_stamp_hold_share` / `raid_shot_stagger` /
  `raid_threat_withdraw` T2 (as the entries they tune), `heat_pulse_rise` T3. `VfxTier`
  (`scripts/ui/fx/vfx_tier.gd`, verbatim) holds the limits. `Fx.flash` takes a tier
  (default T3) and refuses anything below T4 (`refused_flashes`); `Fx.request_flash` puts
  local flashes under the one limiter; `Fx.shake_px` and the hit-stop are held to tier.
  The Perfect and boss-phase full-screen flashes become `CombatFxLayer.wheel_burst`
  (new entries `wheel_burst_perfect` 0.5 s / `wheel_burst_phase` 0.9 s, T3, REQUIRED_IDS,
  lab demos `scene perfect` / `scene phase_burst`); `disc_flash` goes through the limiter
  held to its tier (so VICTORY's 0.8 disc shows at T3's 0.7); the raid's hit ring and
  district wash are held to their tiers (`RaidFxLayer.FX_MOTION`, `fx_tier`; the ANIM-R6
  `raid_threat_withdraw` joins the list). Known gap for ART-3: combat's own 3 px hit shake
  (`hit_shake`, T2) still runs its own shake, over T2's 2 px (M13 W3 routed it through
  `Fx.shake_px`; that is the combat restyle's).
- **reduce_effects uniform (call made):** every shader includes
  `shaders/lib/rc_common.gdshaderinc` and its `reduce_effects` uniform (animated parts go
  static through `rc_live()` / `rc_time()`). M13 made it a global uniform registered in
  project.godot `[shader_globals]`; ART-0 agents never touch project.godot, and a runtime
  `global_shader_parameter_add` would come after Fx preloads its shaders, so here it is a
  per-material uniform set by `ShaderReduce` (`scripts/ui/fx/shader_reduce.gd`) on every
  material built on an animating shader (Fx's three, NeonCity's sketch / live / lights,
  UiTheme's glass), from Settings through `Fx.apply_settings`. Going global later is one line
  in rc_common plus project.godot. The unused `glow.gdshader` is removed, as on art-pass.
- **Tests:** `tests/unit/test_art_w1_tokens.gd` (ported; dropped: the corp-pattern tests,
  `test_hot_button_and_header_scale_with_the_text` (HotButton keeps main's size; the header
  part kept), the M13 value pins for Orbital and MSDF-on), `tests/unit/test_vfx_tiers.gd`
  (ported, plus the shader checks of M13's `test_shader_library.gd` adapted to the
  per-material uniform; its library-shader and project.godot checks dropped);
  `test_motion.gd` and `test_anim_r6_rules.gd` ask Fx.flash for T4.
- **Screens unchanged:** storyboard captures before and after (title, HQ, Grid, fight, card
  hover, shop) differ only in animated city content (rain, lights, traffic, the selection
  blink); text and layout match. The two bursts were read windowed in the motion lab.

### 2026-10-05 — Art direction — ART-0 accessibility settings (salvage S1, area C)
Ported by hand onto main's versions (main's ANIM behaviour kept) from art-pass d78e30b (text scale
2.0), 44f14bb (colour-blind), ec07661 (high contrast), f0a80ba (reduce motion, resolve speed, pad
glyph set, Steam Deck default), 35f3b34 (`city_quality`), eaa7a2c (tests) and the W9F sweep's
"every layout test at 2.0" (M13 W9s / W9F entries under "M13 art pass").
- **Settings** gains `colorblind_mode`, `high_contrast`, `reduce_motion`, `resolve_speed`,
  `pad_glyph_set`, `city_quality` (additive settings.json keys; unknown values fall back to the
  default; a file without them loads as before), `TEXT_SCALE_MAX` 2.0, the Steam Deck first-run
  defaults (text 1.2, city tier 1) through an injectable `device_probe_override` (test runs never
  probe the machine). Defaults equal main's behaviour.
- **Calls made (project.godot is off limits in ART-0):** M13's `ColorblindFilter` autoload is folded
  into Settings (the `ColorblindLayer` is Settings' own child, made only while a mode is on:
  `Settings.colorblind_layer()`, `active_colorblind_mode()`); the `resolve_fast_forward` action
  (Shift, right stick any direction) is added at runtime (`Settings.RUNTIME_ACTIONS`;
  `reset_keybinds` falls back to it). Either can move to project.godot later with no behaviour
  change. The correction layer and the last pad's device id are private session state; the
  snapshot (suite guard) holds every other new field, `device_probe_override` included.
- **High contrast** is `HighContrast.apply` at the end of `UiTheme.build` with area E's tokens
  (TEXT_HI, TEXT_MID, FOCUS); W2's focus brackets are not on main yet (F ports them). Views that
  draw or override their own colours are restyled with it in ART-1…12 (as M13 W9s said).
- **Reduce motion** (separate from reduce effects): `Motion.camera_moves_allowed / parallax_allowed
  / page_transition_style`; consumers on main: PageTransition cross-fades in place (no slide, no
  CRT roll jump), the map camera rig cuts (no hold, no ease), the Grid's lean and the city's pan
  drift stop, `Motion.shake` shakes nothing, the jack is the reduce-effects cross-fade.
- **Resolve speed:** x1 / x2 / instant; the SEND IT replay runs on `Engine.time_scale` (1x schedule,
  the clock faster) and gives the clock back on skip, end and exit; instant shows the end state at
  once; holding fast-forward runs at 4x and is never a skip press (`MotionSkip.is_press`).
- **Pad glyph set:** stored, detected (`effective_glyph_set`); the glyphs are drawn by PadGlyph,
  which area F ports. **`city_quality`:** stored and set on a Deck; main's city has one quality
  today, ART-1's renderer reads it.
- **Options rows** on main's current panel (no restyle; ART-10 restyles it): Reduce motion, High
  contrast, Colour-blind correction, Resolve speed (Accessibility), Pad button glyphs (Controls),
  the fast-forward rebind. Words in strings.csv (re-exported, 18 keys).
- **Tests:** `tests/unit/test_w9_accessibility_settings.gd` (fast tier; M13's W9 tests adapted:
  the colour pairs use E's HARM / GAIN, the options are OptionButtons not TilePickers, the
  correction layer is Settings'; plus round-trip through settings.json, defaults = main, page
  cross-fade, no shake, the combat clock, fast-forward never skips). No M13 test dropped.

**Text scale 2.0 (W9F's approach).** Main never had `LayoutScales`; its layout tests read
`Settings.TEXT_SCALE_MAX`, and the tests that named the old ceiling (1.6) now read it too (27
scripts), so every layout test runs at 1.0 (and 1.3 where it did) and 2.0. 1.6 was checked by
running the same 50 layout scripts with the ceiling set back to 1.6 (hand-back report). Fixes per
screen at 2.0 (unchanged at 1.6 and below unless said):
- **Top bar (HudStats, every screen):** the full tags' floor is `fit_floor(s)` = min(s x 0.85, 1.3)
  (was s x 0.85: two rows of 1.7x tags took 212 px and pushed every page down); one row's captions
  are measured at the tags' scale. This lowers the floor at 1.6 from 1.36 to 1.3 too;
  `test_stat_tags_keep_their_words_at_big_text` reads `HudStats.fit_floor`.
- **HQ:** the Scrub Heat and Patch home lines wrap in the menu column (as RAID PENDING did);
  compact dossiers widen again above 1.6 (`CrewCard.BIG_FROM` / `BIG_GROW`: 280 px at 2.0, two
  side by side, the name on one line); above 1.6 the crew window comes above the City Grid
  monitor (HP and Loadout on the first screen).
- **Raid setup:** the empty-Armory line wraps; above 1.6 (`RAID_SIDE_LOADOUT_ABOVE`) the DEFENSE
  LOADOUT heads the side column (its cards, then its steps) and the column scrolls on its own with
  MORE BELOW (bar hidden, focus follows), so the raid map takes the page's height (under the map
  the Armory left a 290 px map and a late campaign's nodes outside it; lowering the zoom floor was
  tried and spread the labelled nodes further apart).
- **Campaign end:** the story column's room takes the row's gap off (4 px past the screen).
- **Combat:** `TUTORIAL_MIN_HEIGHT` 130 (was 140): a one-line subtitle dock left 138 px and the
  tutorial jumped over the subtitles.
- **Mainframe (the shop):** its LEAVE button moves under the REMOVE A CARD row's pieces it would cover (the
  spinner grew into it); its exit icon follows (as at 1.6 it sits beside SHRED).
- **Loadout spinner view:** above 1.6 the Rank 3 swaps column scrolls inside the wheel area (five
  swaps took 564 px).
- **Focus tips:** a last lettering step at half size; no step goes under `UiTheme.CAPTION` (the
  type floor; 0.72 at 1.0 was 11 px). A big-text loot row left the tip no clear spot.
- **PageTransition.settle** ends a buy sticker's flap (`note_flap`); at 2.0 a mid-flap sticker sat
  more than a pixel from its end state (the tilt moves a wider sticker further).
- Tests that pinned a 1.6 value now read the value at TEXT_SCALE_MAX: the mini-map label size, the
  deck viewer's card scale (DeckView caps it where a row still holds four cards: 1.83 at 2.0) and
  a folded tooltip's words. `test_anim_r4_city` (word cut) and `test_anim_r3_city` (SAVED off
  titles) read what a scroll view shows (a control scrolled out of the raid side column is not
  cut), as M13 W8c did for `test_horizontal_pass20_screens`.
- Windowed check: the storyboard at `--scale=2.0` (15 screens, 1280x720), frames read: HQ,
  raid setup, fight, Mainframe shop, event and loot fit with nothing cut; no ERROR in the log.

### 2026-10-05 — Art direction — ART-0 reduce_effects shader global (area E2)
Following the designer ruling "reduce effects as a project-wide shader global" (above);
supersedes area E's "reduce_effects uniform" call. Ported from art-pass 290ae4c (W6 item 1).
- **project.godot:** only the `[shader_globals]` entry `reduce_effects` (float, 0.0), as on
  `art-m13-final`. Registered there, it exists before any shader compiles, so Fx's preloaded
  shaders and every material built later (script, scene or `.tres`) see it.
- **rc_common:** `global uniform float reduce_effects;` (was a per-material uniform);
  `rc_live()` / `rc_time()` unchanged, so no shader changed.
- **Fx:** `Fx.REDUCE_GLOBAL` and `_apply_shader_global()` set it with
  `RenderingServer.global_shader_parameter_set` (1.0 under reduce effects, else 0.0) first
  thing in `Fx._ready` (before Fx builds or warms any material, so before any shader draws)
  and on every `apply_settings` (Settings.changed). `Fx.shader_reduce` keeps the value sent,
  for tests (the headless renderer keeps no globals). `-s` tool scripts get the autoloads, so
  Fx sets it there too; the design-lab scripts that toggle reduce effects already go through
  `Fx.apply_settings` / `Settings.changed` (motion_lab `_play_jack_reduced`,
  profile_frames `--reduce`). Unset, the global is project.godot's 0.0 (effects on).
- **ShaderReduce removed** (`scripts/ui/fx/shader_reduce.gd` and its `.uid`), with its
  `track` calls (Fx 3, NeonCity 3, UiTheme 1) and `release`. Nothing remains that a global
  cannot cover: the scripts' own zeroing of shader strengths (Fx scanlines / distortion,
  UiTheme `_sync_crt`, NeonCity's live layers) is separate behaviour and stays.
- **Tests** (`tests/unit/test_vfx_tiers.gd`): the include declares the global and
  project.godot registers it; every shader includes rc_common and declares no
  `reduce_effects` of its own; no script keeps a per-material copy
  (`test_no_script_keeps_a_per_material_reduce_effects`); toggling Settings.reduce_effects
  changes the global's value (`test_toggling_the_setting_changes_the_global`; it also asks
  the renderer when not headless). Dropped (superseded by the global):
  `test_every_animating_material_is_tracked`, `test_shader_reduce_follows_the_setting`.
- **Windowed check:** HQ `--demo-grid` captured 150 frames with reduce effects off and on
  (settings.json in a redirected APPDATA): off, the city area changes frame to frame
  (3,000-8,000 px between frames); on, 0 px over 50 frames. No ERROR in either log.

### 2026-10-05 — Designer ruling: DISPATCH text
Default accepted for the ART-0a open question: DISPATCH text is always a clean CRT terminal feed (red
accent, ART_BIBLE v2 §1.2), never a sticker or pencil. GDD 8.2's "never zine-styled" reworded to that.

### 2026-10-05 — Designer ruling: check cadence for M14
The designer asked to run work in parallel and to stop re-running the full suite after every commit
and merge. From ART-0 on:
- **Agents** hand back after the fast tier (`python tools/run_tests.py --tier fast`), their own new or
  changed test scripts, the schema smoke test and content validation
  (`docs/handoff/art_0/process/checks_fast.sh`). No full-suite runs per agent.
- **Each merge into main:** import + the same fast checks, then push. A red fast check is never pushed.
- **End of each ART batch** (before its audit round and the designer report): the full suite ×3
  (`process/checks.sh`), smoke and validate, run **in isolation** (no agents or other heavy jobs running),
  so timing-sensitive tests see a quiet machine. Failures found there are fixed before the audit.
- Agents, audits and captures otherwise run in parallel (at most 4–5 agents at once).
CLAUDE.md's "full suite before declaring any task done" is met per batch: a batch is the unit that is
declared done.

### 2026-10-05 — Designer rulings: names for M14 (plan §3.1 D2–D8, D11–D12; resolved by the designer)
Defaults accepted for all (`docs/ART_REINTEGRATION_PLAN.md` §3.1). Per ruling 5 of "pause point 0" below,
internal names (enums, ids, files, classes) follow these display names; no compatibility kept.
1. **D2 slice programs:** ATTACK → **SHIM**, CRIT → **OVERFLOW**, DEFEND → **DEFRAG**, EVADE → **DETOUR**,
   HEAL → **HOTFIX**, AFFLICT → **INFECT**; SANDBOX, TROJAN, NULL unchanged (concept rounds 32–34).
2. **D3 Meridian:** JUDGEMENT retired; the RAM-drain slice (was Tariff) is **PRIORITY**; Meridian's CRIT is
   **AIRMAIL** (round 18).
3. **D4:** INERTIA → **WEIGHT**; Solace HEAL → **GROWTH** (rounds 14–18).
4. **D5:** "Mainframe Gate" → **Central Server** (GDD 11.7); per-corporation names The Master Manifest,
   The Genome Core, The Panopticon, Launch Control as content strings (rounds 33, 35).
5. **D6:** player-facing **Firmware** everywhere ("Microchips" retired; rounds 33–34).
6. **D8:** precision tier Partial → **WEAK** (GDD 2.4; round 39).
7. **D11 Heat bands:** old FLAGGED → **HUNTED**, old NOTICED → **FLAGGED**, new **NOTICED** = a couple of
   alarms; thresholds unchanged; the screen glitch only as an off-by-default Options extra `heat_glitch`,
   exempt from VfxTier (rounds 19–22).
8. **D12:** the respin control reads **RESPIN**, never CHECKPOINT; the undo block shows on UNDO (round 23).
9. D9 and D18–D20 are covered by the pause-point-0 rulings or are presentation only (agreed). D13–D17 are
   asked before the batch that needs them (ART-3, ART-4, ART-7).

### 2026-10-05 — Art direction — ART-0 docs landing (ART-0a, A1–A6)
The art docs land on main, ported from art-pass 9a62cec (tag `art-concepts-r43`) by
`git checkout`/`git show`, never by merge. Docs only: no code, content or test changed.
- **A1 docs:** `docs/ART_BIBLE.md` (v2), `docs/ART_BIBLE_v1.md`, `docs/ART_REINTEGRATION_PLAN.md`,
  `docs/ART_REINTEGRATION_PROMPT.md`, `docs/concepts/DIRECTION_REVIEW.md`,
  `docs/concepts/GDD_ART_COVERAGE.md`, `docs/concepts/.gdignore`. The plan gets a "Rulings applied"
  banner; plan §1 items 1, 5, 6.2, 6.5, 6.6, 7, 9 and (ours, same reason) the §5.1 risk row
  "Renames break saves or replays" are struck or annotated with the ruling, never rewritten. In
  the bible, Appendix C #12 is annotated with ruling 11 and #1 (its "Designer to confirm") with
  ruling 10, which confirmed it. Diff against the tag: those annotations only.
- **A2 `docs/art_reference/`** (ruling 3): 60.7 MB (59 MiB by `du -sh`), 257 files plus README and
  `.gdignore`, one README row per file (element, round + lock, ART_BIBLE v2 section, original
  path, ART-n batch, how it was copied). Every ART_BIBLE v2 Appendix A row and every §3.20 effect
  resolves to a README row (checked by a script). Appendix A names about 300 MB of images, so:
  stills over 600 KB (or wider than 1600 px) are 1600 px wide JPEG q82 copies (wide strips keep
  their width); stills with alpha (the glyphs) and GIFs up to 1.0 MB are byte-identical (22 GIFs);
  the 42 GIFs over 1.0 MB are replaced by an 8-frame keyframe sheet `<name>.frames.jpg` (34) or by
  the art pass's own strip / storyboard (8). No Pillow GIF re-encode was smaller than the
  originals, so none is re-encoded. The brief's "keep a > 2 MB original if Appendix A names it as
  final" is not applied: every Appendix A image is a named final, and keeping them would pass the
  80 MB cap; each original is one `git show art-concepts-r43:docs/concepts/<path>` away and the
  README "Not copied, why" table lists every one. Also there: the 31 round 40 raid GIFs
  (`raid_gifs/index.md` and its contact sheet are copied, the GIFs stay on the tag) and the rest of
  the 277 MB archive (earlier rounds, rejected media, superseded versions, scripts, `*.pyc`, the
  EVOLUTION slideshow, video and PDF). The round 17 glyph masters are 58 PNGs + `index.txt` (59
  files; the brief said 59 PNGs). Courier Prime Regular/Bold + `OFL_CourierPrime.txt` are in
  `fonts/` (from round 33). Appendix A writes `round18_combat_fx/binary_damage/`; the folder is
  the top-level `binary_damage/` on the tag.
- **A3:** `docs/art_history/ART_PLAN_M13.md` = art-pass `docs/ART_PLAN.md` with a superseded
  banner. The 14 M13 DECISIONS entries (Art pass rulings, wave 1, W9s, W2, W5, W4, W7, W3, W8a, WF,
  W8c, W8b, W8d, W9F) are below under "M13 art pass (art-pass branch, superseded in part)",
  verbatim except their heading level (### → ####, to sit under that heading). None of them names
  the Grid fit-pass constant, so `test_horizontal_pass24_city` needed no annotation.
- **A4:** GDD §9.1–9.4 rewritten around ART_BIBLE v2, every changed paragraph citing its ruling;
  9.6 notes that static CRT scanlines may stay under reduce effects (v2 §5.4); 9.5 unchanged. GDD
  "Changes since" line added; the locked line "Visual baseline: three worlds" is struck and marked
  superseded. GDD 8.2's "never zine-styled" (DISPATCH text) is outside §9 and describes no
  baseline, so it was left for the designer (open question below).
- **A5:** MILESTONES gains "M13 — Art pass v1 (art-pass branch, superseded in part)" and "M14 — Art
  direction v2" (ART-0…ART-12 acceptance lines from plan §4.2 unticked, ruling 7 and 11 adjustments,
  the post-ART-12 re-evaluations); plan §4.2 has no acceptance lines for ART-10 and ART-11, so
  their boxes list the batch's items.
- **A6:** STYLE_GUIDE pointer: ART_BIBLE v2 is the visual source of truth from M14; §5 stays binding.

### 2026-10-05 — Art direction — ART-0 D: visual QA harness and lint (salvage S2)
Ported from art-pass (tag `art-m13-final`; W10 visual QA, W9F additions) into
`tools/visual_qa/`: the review-pack harness (`review_pack.gd/.tscn`, `review_pack_log.gd`),
its driver `capture_pack.py` (every Godot run through `tools/run_windowed.py`, each with its
own user:// folder), `contact_sheet.py`, `diff_pack.py`, `filters.py` + `cvd_filter.gdshader`,
`lint_report.py` (runtime lint: on-screen sizes, overlaps, clipping incl. scroll views, modals,
contrast), and the static lint (`visual_lint_static.gd`, `lint_static_cli.gd`,
`update_lint_baseline.py`, `merge_shared_json.py`). M13's baseline images and lint baseline
are not ported (the brief: re-captured / re-seeded).
- **Static lint baseline:** `tests/unit/test_visual_lint_static.gd` (fast tier) gates
  `tools/visual_qa/lint_baseline.json`, seeded with main's violations today: **205 lines in
  41 files** (literal colours, literal font sizes in `scripts/ui/**`; `kit/palette.gd` exempt).
  ART-1…ART-12 drive it to zero. A count may only go down. A merge that ports art-pass files
  with their literals (E's `ui_theme.gd` mechanism, later batches) adds them to the baseline
  in that merge (only the ported file's rows, by hand or with `update_lint_baseline.py --reset`
  checked against `--check`), said in that merge's report, never silently.
- **Re-pointed at main's screens:** 58 screens (the art pass's 53, with the Modem pages
  named `mainframe*` after ruling 6.5, plus five ANIM states main has and M13 never saw:
  `hq_heat_band` (the Heat poster's band crossing and reading hold), `grid_influence` (the
  territory spread after a claim), `grid_drag_crew` and `raid_drag_asset` (ANIM-4 drags,
  mid-carry), `run_end_clean` (the clean-exit verdict). Setups go through `DemoSetup` and
  the views' own dev hooks (`_demo_drag`, `_demo_combat_end`, `_demo_city`) where main has
  them. No art-pass screen is skipped; the M13-only views main lacks are only seen as main's
  own version: the dossier-tile target picker and the slot-tile socket picker (main pops its
  OptionButton list), `CardDetailHolder` (main's `CardDetail` window), `GlassScrim` and the
  kit's modal group (read only when ART-0 F ports them).
- **Axes:** text scale 1.0 / 1.6 / 2.0 (written past main's 1.6 clamp), mouse / pad, reduce
  effects off / on, grey and deutan (Pillow, from the captured frame), and the accessibility
  settings high contrast, reduce motion and the colour-blind mode as a fifth combo part
  (`_hc`, `_rm`, `_cb-deutan`). Those are gated on the Settings property existing (ART-0 C
  ports them): the harness reports which exist (`--list`), the driver skips the others and
  names them in the manifest's `skipped`; `--matrix` runs them at 1.0 and 2.0 mouse.
- **Small packs out of git:** pictures are laid out and linted at 1280x720 and saved at
  800x450 (`--save-size`); the runtime lint scales them back up to measure contrast. Packs
  go under %TEMP%; a pack inside the project gets a `.gdignore` (review packs land later in
  `docs/art_review/ART-n/`). The driver refuses to start with < 5 GB free.
- **Runtime lint type steps:** the "override is not a type step" half of the font rule reads
  the build's `UiTheme.STEPS` (exported by the harness); a build without them skips that half
  (main before ART-0 E); since E merged, the steps are read and checked.
- **First matrix on main (with E merged), `--matrix -j 2`:** 58 screens x 12 combos, 696
  captures + 696 grey, all ok, 23 min, 587 MB at 800x450 (deleted after reading). Settings
  axes skipped (C not merged yet). Runtime lint totals (font / overlap / clipped / contrast):
  1.0 mouse 63 / 0 / 5 / 22, 1.6 mouse 219 / 0 / 8 / 22, 2.0 mouse 203 / 3 / 11 / 17,
  2.0 pad 196 / 3 / 11 / 11 (the font rule now checks E's type steps). Read by eye on the
  HQ sheet: at 2.0 the top bar takes two rows and the crew dossier and Pirate Radio text are
  cut at the bottom of their panels (area C's layout-at-2.0 work).
- **Lint baseline re-taken after merging main with E** (tokens and type steps): unchanged,
  205 lines in 41 files (E moved no literal out of `scripts/ui/**` views; ART-1…12 do).
- **Harness robustness on main:** main's views hold the bake they draw (ANIM-R6), so "no bake
  running" never holds: a screen waits for every visible city to show its current look,
  covered and faded in (at most 20 s real time, then a warning naming the city; a fight's
  held city, which lands between turns by design, is not waited for). Every screen starts
  from a cold city cache (`CityBakeCache.shutdown()` after the last screen's scenes are
  freed), as a fresh launch does: without it, bakes of freed scenes starved later screens and
  most pictures showed the silhouette stand-in. A screen given up
  on (timeout or script error) parks its coroutine instead of driving freed scenes on the
  next screen. `tests/unit/test_visual_qa_harness.gd` (fast) checks the harness compiles
  against main, every screen has its method, and the axes follow Settings.
- **Fixed on the way (outside D's files, smallest change):** `CityBakeCache._stop` assigned a
  record's painter to a typed variable before checking it; a scene freed mid-bake (the
  harness's grid-influence screen, also reachable in game) raised "Trying to assign invalid
  previously freed instance" and later crashed the run. It now checks the instance first
  (the M13 W10 entry logged the same bug at `city_bake_cache.gd:183`).

### 2026-10-05 — Designer rulings: art reintegration, pause point 0 (resolved by the designer)
Answered by the designer as a numbered list against `docs/ART_REINTEGRATION_PLAN.md` §1
(art-pass tag `art-concepts-r43`) plus the ANIM-R7 open question and ART_BIBLE v2
Appendix C items 1 and 12. Defaults accepted unless noted.
1. **Changed: M14 first.** The art pass covers so much that ANIM-R7 would iterate on work the
   art pass makes obsolete. Order: port the art pass (M14, ART-0…ART-12) → re-evaluate every
   ANIM-R7 finding (`docs/handoff/anim_r7/`) against the ported screens → fix the ones still
   valid (batches A–E, re-cut) → re-evaluate the horizontal list → H25+ → Queued passes.
   ANIM-R7 is **paused, not dropped**: each R7 item is re-checked after M14 (nothing deferred).
2. **Port, don't merge** (plan §2). The art direction takes precedence over existing views
   where they conflict; conflicts are raised as questions, defaulting to the art direction.
   Acceptance for M14 as a whole: the look and most of the feel of the art pass are present
   by the end of the milestone, or M14 has failed. ANIM motion behaviour (MotionSkip, holds,
   reduce effects = end state, entries in `ui_motion.tres`) is kept and restyled.
   Tags pushed: `art-m13-final` = `f80f393` (M13 final capture, the last M13 code state),
   `art-concepts-r43` = `9a62cec` (rounds 1–43, ART_BIBLE v2, the plan, the evolution
   slideshow and video).
3. **Curated `docs/art_reference/`** on main; the full concept archive stays on the tag.
4. **GDD §9 is rewritten** around ART_BIBLE v2 (cel city + CRT screens + vinyl stickers +
   grease pencil + light spill; "no UI ever covers grease pencil"). Done in ART-0a once the
   bible lands on main; GDD 9.1 cites this entry.
5. **Changed: no save or replay compatibility.** Old saves and replays are not preserved.
   Internal code and content names (enums, ids, file names, class names) are aligned with the
   new display names; nothing is kept static for compatibility. Saves and replays get a
   project folder that git ignores (ART-0 S0, see "Art direction — ART-0 saves folder").
6. **Name collisions:**
   1. Meridian's RAM-drain slice is **PRIORITY**. The Manifest's hub (was "Priority Routing",
      `priority_routing`: +4 shield each turn unless breached) is renamed (designer: "suggest a
      name and run with it"): **Customs Seal** (`customs_seal`): Meridian freight sealed for
      customs, a seal the Cell has to break (Hub Breach). Rules unchanged.
   2. **Changed:** the raid words replace the GDD words: **Seized → TAKEN**, **Disabled →
      DOWN**, **Holds → CELL HOLDS** (the raid result stamp; a node that holds shows HOLDS),
      and **BREACHED** = the home server (CORE) falls (integrity 0, campaign lost). GDD 3.3,
      7.1, 7.2 and every rule that names them are updated, then code and content (ruling 5).
   3. Upgrade tiers are Roman numerals (I–III); Site tiers stay T-numbers (T1–T4).
   4. VAULT / KEY / SPOOF and the raid node glyphs unify on the round 42 icons.
   5. **Changed:** the shop node "Modem" is renamed **Mainframe** everywhere (node type, ids,
      strings, GDD 4.2, 6.3, 11.x). The boss gate formerly "Mainframe Gate" therefore needs
      its own name: plan D5 already proposes **Central Server** (asked with §3.1).
   6. The art-pass direction stands: the fist crest is the Cell's mark. Telling the player's
      Cell apart from the eventual REBEL_CELL corporation is a future concept slice (logged
      under "Open questions for the designer" so it is not lost).
7. **Changed: fidelity first, then optimise.** The unified city follows the art pass as the
   final product; the ART-1 render spike picks the technique that reproduces the reference
   images most faithfully, then an optimisation round brings it inside the perf budget (plan
   §5.2) so it renders cleanly. The budget is a gate, not a reason to change the look.
8. **The G1–G16 mechanic proposals** are re-evaluated with the designer after the art
   integration. Until then art for them stays in `docs/art_reference/`.
9. **The R7 overkill wording** ("→ 1 LEFT") is re-evaluated after the art pass (the HP result
   chip, plan D15, may replace that line).
10. **Status badges** (ART_BIBLE v2 Appendix C #1): the overlay is the status; a small flat
    corner badge appears only to carry a ×N stack tab or a ×1.5 / ×0.5 tag.
11. **Changed** (Appendix C #12): the raid view drops its amber dashed socket for DOWN nodes
    and uses the Site markers' white bolt over a greyed marker, so DOWN reads the same at
    every zoom.

### M13 art pass (art-pass branch, superseded in part)
The DECISIONS entries the M13 art pass wrote on the `art-pass` branch (W1–W10, WF, W9s, W9F;
tag `art-m13-final` = `f80f393`), brought over **verbatim** by ART-0a so main keeps the record
(ported from art-pass 9a62cec). Only their heading level changed (### → ####) so they sit
under this heading. They implement **ART_BIBLE v1.0** (`docs/ART_BIBLE_v1.md`, plan
`docs/art_history/ART_PLAN_M13.md`): the zine / neon / cyberdeck look is **superseded** by
ART_BIBLE v2 (DECISIONS 2026-10-05 pause point 0, rulings 2 and 4); their direction-agnostic
infrastructure is ported in part by ART-0 salvage S1–S5. Where an entry names `art-pass` file
paths, tests or numbers, they describe that branch, not main.

#### 2026-09-28 — Art pass (branch `art-pass`): designer rulings and orchestration
Governed by `docs/ART_BIBLE.md` v1.0; plan in `docs/ART_PLAN.md`. Presentation only.
1. **Branch:** the whole art effort lives on `art-pass` (from `8ddfa86`), merged into `main`
   at a date the designer picks. Workstreams branch from it as `art/w<n>-<slug>`; only the
   orchestrator merges them back. Commit and push `art-pass` regularly.
2. **Q1 card art (§16.1):** about 30 base illustrations tinted per type, plus unique art for
   rares and class cards. Briefs are written per effect family first.
3. **Q2 class accents (§16.2):** the §7.1 proposals are accepted as the token values.
4. **Q3 body face (§16.3):** IBM Plex Sans Condensed (OFL) is added for text blocks over 3 lines.
5. **Q4 HQ (§16.4):** the full DECK frame (monitor bezel, keyboard edge, cables).
6. **Q5 text scale:** the `Settings.text_scale` range goes up to 2.0 (an additive settings
   change; old settings files load unchanged).
7. **Q6 vector and concept art:** agents author SVG for baked art (logo, signs, badges,
   landmark glyphs). Concept images for painted-art briefs are made as **pixel art and vector
   concepts drawn by script** (Pillow/SVG, deterministic). They live under
   `docs/art_review/<W>/concepts/` and are never shipped as game assets without the
   designer's approval.
8. **Autonomy:** the designer reviews in parallel and asked not to be asked. The
   orchestrator answers open questions itself, logs each here citing the bible section, and
   keeps the bible's §16 list current.
9. **Review output:** every workstream writes its before/after stills, strips, contact sheets
   and a `README.md` (what changed, the §14 checklist, decisions, known gaps) to
   `docs/art_review/W<n>/`.

#### 2026-09-28 — Art pass wave 1: W1 foundation, W6 VFX, W10 visual QA (merged into `art-pass`)
Review folders: `docs/art_review/W1/`, `W6/` and `W10/`. The baseline "before" pack is `W10/baseline/`; its full matrix is only local (git-ignored).

**W1 foundation (§3–§5, §15).**
- **Tokens and helpers:** the semantic, corp and class tokens, `hp_color`/`heat_color`/`contrast`/`over`, `CorpPattern`, `UiTheme.font_px` with the type scale and spacing tokens, and the IBM Plex body face with a `BodyText` variation. Views migrate their own call sites later.
- **MSDF:** on for every face, with `msdf_pixel_range` 16 so that 6–8 px outlines stay inside the field. The font `.import` files are force-tracked (`*.import` is git-ignored), and a test fails if MSDF is lost.
- **Numbers:**
  - Heat bands come from the config's MAJOR Heat levels; no copied numbers.
  - HP at exactly 50% is GAIN, and at exactly 25% it is WARN.
  - An unknown class gets the `TEXT_MID` accent.
  - Tracking is stored as a fraction of the font size.
- **Proposal for the bible (not applied):** +2% tracking rounds to 0 px below `heading`. §4.2's tracking could be given in px per step instead.
- **Orchestrator follow-up:**
  - The now-scaled HotButton pushed raid setup past 1280 px at 1.6. At `STEP_ICONS_SCALE` and above, Back to HQ now shows its icon only, with its words in the tooltip (the same pattern as the Grid's step buttons). The pass-12 width check asserts again instead of pending.
  - A wrapping row was tried first. It pushed the defence cards 1 px off screen, so it was rejected.

**W6 VFX (§8, §13).**
- **Reduce effects:** one `reduce_effects` global shader uniform, set by `Fx` from Settings, is read by every shader. The script-side zeroing stays too.
- **Removed and added:** `glow.gdshader` was unused and is removed. The new library shaders (`glass_blur`, `crt_overlay`, `paper_burn`, `glitch_dissolve`, `marker_stroke`, `halftone`) aren't yet wired into screens; W2, W7 and W8 do that.
- **Tier schema:** `UiMotionEntryData.tier` (T0–T4, default T1) is a schema change, logged here and covered by the smoke test. The limits live in `VfxTier`.
- **Flashes:**
  - `Fx.flash` defaults to T3, so a full-screen flash must pass T4 explicitly. It does nothing under reduce effects.
  - The stored `screen_flash` 0.45 and `victory_flash` 0.8 are clamped at runtime to 0.4 (T4) and 0.7 (T3).
  - Perfect and boss phase are now wheel-local bursts (`wheel_burst_perfect` 0.5 s, `wheel_burst_phase` 0.9 s, 70% peak).
- **Tier assignment:**
  - T0: loops and ambience.
  - T1: hover, focus and UI moves.
  - T2: hits, stamps, drops, buys, refusals and `raid_move`.
  - T3: Perfect, kill, phase, Heat band, claim, influence and VICTORY/DEFEAT.
  - T4: jack transitions and `screen_flash`.
- **Tier duration caps:** these bind only effects the FX layers draw. UI motion keeps §10's budgets; the 30 entries longer than their tier's VFX duration are listed in `W6/README.md`.
- **Proposal for the bible (not applied):** state in §8 that the duration column is for drawn effects only.
- **Hit shapes:** DEPLOY uses the attack slash. DEFEND and SHIELD share the hex plates. The crit's shattered glass replaces the star burst.
- **Orchestrator follow-ups:**
  - `Palette.AUTO` names the "use the element's own colour" default, so the static lint stays at zero for `combat_fx_layer.gd`.
  - `wheel_burst(..., pattern)` fills the phase ring with the boss corp's `CorpPattern`. W3 passes the pattern from `combat_scene`.
  - The shader lab's glass tint uses `Palette.SCRIM`.
  - Degenerate hit polygons (a slash on its first frame, a zero-size glow) are skipped. They raised a timing-dependent `indices.is_empty()` engine error in `test_anim_r3_combat`.
- **Open for W3:**
  - Miss static isn't triggered yet (`_land` needs `hit_vfx(..., HIT_MISS)`).
  - `slice_hit` should be called with the attacker's slice type.
  - `hit_shake` 3 px is over T2's 2 px; route it through `Fx.shake_px`.
  - `WheelView`'s hit flash goes through `Fx.request_flash`.
  - The attack slash is thin at its peak; scale hit size with damage.

**W10 visual QA (§13, §14).**
- **Harness:** `tools/visual_qa/` has 43 screens reached through clean states. Grey and deutan filters are made with Pillow by default (`--filter-mode shader` renders in-engine). Text scale is written straight into Settings, past the 1.6 clamp, until W9 raises the range.
- **Lint gate:** the static lint (`test_visual_lint_static.gd`, baseline `tools/visual_qa/lint_baseline.json`) fails when any file gains literal colours or font sizes. It never rises unless given `--reset`.
- **Runtime lint:** a report, not a gate, because it needs a renderer. It treats "from UiTheme" as a §4.2 step × text scale.
- **Top runtime lint offenders** (each owner's to-do list):
  - `terminal_window` fixed 14/15 px (W8);
  - the `fx.gd` "SAVED" label (fixed 14 px, contrast 1.6–2.9:1; W2);
  - `route_legend` shrinking to 9.8 px (W8b);
  - `crew_card` (W5);
  - clipped dialogue and `zine_note` text (W8).
- **Harness dependencies:** the harness calls some private members (`_panel`, `_show_current`, `_preview_card`, …). Screen owners keep them, or add public capture hooks.
- **City bake bug:** freeing a scene mid-bake raised a script error at `city_bake_cache.gd:183` (`_stop`). This goes to W7. It's likely also fixed by the ANIM-R5 city branch.

#### 2026-09-29 — Art pass W9s: accessibility settings (merged into `art-pass`)
Review folder: `docs/art_review/W9/`. The text-scale 2.0 breakage table there is W3's and W8's to-do list.
- **Text scale (Q5):** `Settings.TEXT_SCALE_MAX` is 2.0. The 12 layout test scripts that don't fit at 2.0 yet check up to `LayoutScales.VERIFIED_MAX` (1.6, in `tests/helpers`). W8 raises that to `TEXT_SCALE_MAX` screen by screen, and the art pass isn't done until it equals 2.0.
- **Colour-blind (§12):** "remap corp and semantic hues" is done as a global LMS daltonize **correction** in linear light, on canvas layer 127, because Palette values are compile-time constants.
  - Patterns and glyphs stay the primary cue.
  - `off` means no layer at all.
  - W10's simulation filter sits above it, at 128.
  - Proposal for the bible (not applied): say "correct" instead of "remap".
- **High contrast:** `HighContrast.apply(theme)` makes filled theme boxes #000, keeps each state's tint as an opaque 2 px edge, and sets text to `TEXT_HI`, focus to 4 px `FOCUS`, disabled to `TEXT_MID`, and button edges to 3 px.
  - Views with their own `_draw` or colour overrides (paper, HUD tags, wheels, cards) must read `Settings.high_contrast` in their own workstreams: W2, W3, W4, W5, W8.
  - Proposal for the bible (not applied): state how PAPER looks in high contrast.
- **Reduce motion** is independent of reduce effects. It works through `Motion.camera_moves_allowed()`, `parallax_allowed()` and `page_transition_style()` (slide or fade). Consumers are W7 (city camera) and W8 (page transitions, map framing).
- **Resolve speed:** `x1`/`x2`/`instant`, via `Motion.resolve_time_scale()` and `resolve_instant()`.
  - Holding `resolve_fast_forward` (Shift / right stick) runs at 4×.
  - W3 wires it and must exempt the action from MotionSkip's "a press completes the motion" rule.
- **Pad glyph set:** `auto`/`xbox`/`playstation`/`switch`/`deck`. Auto-detect matches substrings of the joy name; Sony counts as PlayStation, and anything unknown is xbox.
- **Steam Deck:** the first-run default is `text_scale` 1.2 (`TEXT_SCALE_STEAM_DECK`). Test runs skip the device probe unless one is injected.
- **Deviation:** items 4–7 share one commit, because they share Settings' declarations.

#### 2026-09-29 — Art pass W2: component library (merged into `art-pass`)
Review folder: `docs/art_review/W2/`. The component lab is `tools/design_lab/components_lab.tscn`.

**Focus (§6, §12)**
- `FOCUS` corner brackets (`StyleBoxBrackets`) replace the acid ring theme-wide.
- The 1.03 scale plays for **pad focus only**; mouse and keys get the brackets. Headless stays at 1.0.
- A focused plain row or menu line also colours its words `FOCUS`.
- High contrast thickens the brackets to 4 px. Orchestrator integration fix: `HighContrast.apply` now handles `StyleBoxBrackets`.

**Buttons (§6.4, §3.7, §4.2)**
- Only the named variants (Primary/`HotButton`, Secondary, Tertiary, Danger) size to label + 32 px. A plain `Button` keeps its 10 px row padding, because widening every button broke the HQ crew at 1.6.
- `MenuItem` text is at `body`, not `label`: at `label` the HQ menu pushed past the crew's two columns at 1.6.
- Disabled labels use `TEXT_MID`, because `DISABLED` is 3.9:1 on glass. The lock is a corner badge, so the button size doesn't change.
- `ConfirmDialog`: Yes is Danger, No is Secondary.

**Toast (§6.7)**
- The hold is the longer of 2.5 s and the stamp reading rule. `toast_note_hold` is retired but kept, because tests name it.
- The toast's tape is tilted; the note itself stays square.
- `Toast.spot` keeps the toast off usable controls and the prompt bar.

**Tooltips (§6.8):** 36 columns at every scale. `UiTip.for_input` replaces stray "click"/"drag" in pad text.

**Pad glyphs and colours (§12, §3.6)**
- Glyph auto-detect uses the first pad's name and falls back to Xbox.
- Glyph colours come from the §3.3 tokens.
- Asset and Daemon hues no longer use corp hues.

**Proposals for the bible (not applied):**
- Say "pad focus" for the 1.03 scale.
- Name `TEXT_MID` as the disabled label colour.

**To do for owners:**
- W3/W4/W8: switch `Palette.STATUS_GLYPHS` users to `StatIcon.draw_status`:
  - `combat_scene.gd` 2413, 2450, 2536, 2572, 3737
  - `wheel_view.gd` 1754, 1768
  - `zine_card.gd` 631
  - `codex.gd` 162
- W8/W3: replace the native controls with kit components. The call-site list is in `docs/art_review/W2/README.md`.
- W8: use `IconMark.attach(b, StatIcon.TRASH)` on real Delete buttons (the Danger X texture doesn't scale).
- W3: the RESPIN sticker's words overrun at 1.6.

#### 2026-09-29 — Art pass W5: characters (merged into `art-pass`)
Review folder: `docs/art_review/W5/`. Briefs are in `docs/art_briefs/characters/` (24). Concepts are in `W5/concepts/`: 47 pixel-art busts, not game assets.

**Operatives (§7.1)**
- Eight class silhouettes and props in `Palette.class_accent`.
- The operative's tint is the accent lightened or darkened by 7%. At 12%, a dark Overclocker drifted towards Breaker's pink.
- Four expressions (`PortraitArt.Expr`; `Expression` is a native class name):
  - hurt adds two `HARM` scratches and a crack;
  - triumphant raises a fist;
  - flatlined greys everything, with a flat line.
- The closest class pair (Rigger/Botnet) differs by a mask distance of 0.142. The test's floor is 0.12.

**Polaroids and dossiers**
- The Polaroid caption is the rank ("RANK n", or "R n" when compact), so the name isn't repeated.
- Polaroid handwriting is set at `label` and steps down only to fit, never below `caption`.
- Dossier stats are icon + number fields, read-only from the campaign.

**Stamps:** FLATLINED stamps and low-HP glitch bars use `HARM` (they were pink). "ON <SITE>" stamps are ink.

**Enemies and bosses (§7.2)**
- Enemies fill the body with their corp's `CorpPattern`. Bosses also get a pattern halo.
- `Hologram` shows a bust, or a boss at 40% of the screen height dimmed to 0.5 behind its wheel.
  - The intro is T4. Under reduce effects it's a cross-fade.
  - The `crt_overlay` settings are scan 0.18, roll 0.12, flicker 0.02.
- Enemies with no corp (the summoned drones and the Mirror templates) get no brief of their own.
- Text under 12 px in the WIRE and MUGSHOT looks was removed rather than enlarged.

**Proposal for the bible (not applied):** §4.1 says handwriting is never under 16 px. That can't hold on the 60 px compact Polaroid, so suggest "16 px where the frame allows".

**Orchestrator merge:** W2's and W5's appended motion entries were combined, and `ui_motion.tres` was rebuilt from W2's version plus W5's three hologram entries.

#### 2026-09-29 — Art pass W4: cards (merged into `art-pass`)
Review folder: `docs/art_review/W4/`. Briefs are in `docs/art_briefs/cards/`: 35 effect families and 12 unique cards. Concepts are pixel art, in `W4/concepts/`.
- **§6.3 faces.** Hand-size cards (112×148, unchanged) show a compact face: gem, title, 60% art and the band, with no rules text. Screens that must show every word (Modem, loot, deck view, detail at 288×320) show the full face.
- **No ellipsis anywhere (§4.3).** When text doesn't fit, the full face steps down in this order:
  1. the text shrinks one step;
  2. the art shrinks (floor 15%);
  3. the band is dropped;
  4. the card grows taller.

  Tested on all 71 cards at 1.0, 1.6 and 2.0.
- **Card type drives the card colour.** It comes from the first effect:
  - WHEEL (paper): moves wheels.
  - SYSTEM (black): defence, resources and buffs.
  - HACK (pink): damage, corrupt/parasite, breach, resistance strip and RAM drain.

  The colour no longer depends on hand position.
- **Riso stand-ins (§7.3).** Two inks, INK + `CELL_PINK`: key screen at 45°, spot at 15°, about 1.4% off register. Rares and class cards vary by a hash of the card id. Renders are cached, 2 per frame.
- **Art override.** `CardData.art`, an existing field that wasn't used, is now the final-art override. **No schema change.**
- **Rarity (§6.3).** Common is photocopy grain, uncommon a glossy die-cut sticker, rare/boss holographic foil (`shaders/foil.gdshader`, static under reduce effects). In greyscale, rarity also reads by pip (dot/diamond/star) and edge.
- **Cost gem** is `NOTE_YELLOW` (`CELL_ACID` is reserved for focus). A RAM refusal pulses `HARM`.
- **Motion constants.** Hover is 12 px + ×1.12 on `card_hover` timing. The ghost scale is 0.6. Both are named constants; there are no new motion ids.
- **Detail view (§2).** The paper card is taped *beside* a glass notes panel, never inside it. The notes never repeat the face text.
- **Orchestrator decision on W4's open gap.** In greyscale, paper and pink stock are hard to tell apart. Because §3.1 says colour is never alone, HACK stock gets a light diagonal hatch. This goes to W3/W8 as a follow-up: `zine_card.gd` is W4's file, and W4 has finished, so the orchestrator will apply it.
- **Orchestrator test fix.** `test_horizontal_pass19` now sets keyboard input itself. Earlier scripts in its shard leave the pad active, and the new shard layout exposed that (the hint showed "[LB]").

#### 2026-09-29 — Art pass W7: city (merged into `art-pass`)
Review folder: `docs/art_review/W7/`, with frame times in `perf.md`.

**How it's built (§9.1, §13)**
- HDR 2D stays off. All the lighting is done in shaders, in one city composite with no screen copy: per-ink glow, three haze bands, wet streets, rim light, searchlights and territory light.
- The per-context grade is parametric (contrast, saturation, warmth, lift, dim and corp lean), not a LUT texture. Its values live in `content/config/city_look.tres`, a new `CityLookData` schema: logged, smoke-tested and self-validating.

**Dim and progress**
- A context's dim is the total darkening. The screen's own `NeonCity.dim` veil counts towards it, so combat is never darkened twice.
- Bible tension: §9.1 gives a 35% combat dim, but combat's existing veil is 0.55. The context total rules.
- Default campaign progress is the claimed + cleared weight over the corp's Site count, taken from `CityInfluence`.
- A city that follows the campaign reads Heat, territory and progress read-only. Explicit setters win.

**Territory (§9.3):** a lasting 40% wash as a `CELL_TURF` hatch, a hatch on claimed roofs, 3 spray tags per Site, and ground lean 0.06. This replaces the khaki.

**Blinks and life timing**
- Window and beacon blinks are floored at 3 s in the shader.
- Life timings live in `city_look.tres`, not `ui_motion.tres`.
- Bible tension: §8 wants a T0 period of ≥ 3 s, but §9.3 wants the FLAGGED rim flicker at ≤ 1 Hz. The flicker is a §9.3 state signal and is off under reduce effects, so it's kept at ≤ 1 Hz.

**Reduce effects:** no aircraft or drones, billboards hold on frame 0, searchlights stand still and the rim flicker is off.

**Performance (§13)**
- `crt_overlay` isn't used on the city, because it would add a second full-screen pass.
- Frame time goes up 12% (combat), 22% (grid) and 23% (title), missing the plan's 15% relative budget. **Orchestrator ruling: accepted.** The absolute cost is +0.2–0.8 ms of GPU at 1080p, and the worst scene is 4.9 ms (about 200 fps), well inside §13's 60 fps target.
- There are quality tiers 0/1/2, default 2. The Steam Deck first-run default should be tier 1; W9's final sweep adds that to `apply_first_run_defaults`. The Deck itself hasn't been measured.

**Bake fix:** the `city_bake_cache.gd` freed-painter bug (W10's finding) is fixed with `_alive_painter`. The ANIM-R5 city branch doesn't touch `_stop`. `git merge-tree` shows W7's `neon_city.gd` and `city_bake_cache.gd` hooks auto-merging with that branch.

**Screen hookups (to do)**
- W8b: `set_map_mode` on Grid, Route and Raid, and calm zones on the HQ and event pages.
- W8a: calm zones on the title panels.
- W3: `set_context(&"combat")` in place of `city.dim = 0.55`.
- Audio: sirens can hook `CityAtmosphere.state.hunted()`.

**Orchestrator tool:** new `tools/visual_qa/merge_shared_json.py` resolves the recurring merge conflicts in `tests/test_manifest.json` (the union) and `lint_baseline.json` (a three-way minimum).

#### 2026-09-29 — Art pass W3: wheels and combat (merged into `art-pass`)
Review folder: `docs/art_review/W3/` (40 before/after sheets, class and corp bezel sheets, strips); the README lists 17 decisions.

**Wheels (§6.1, §7.1)**
- **Ownership by bezel:** the operative's bezel is stickered paper with a `CELL_PINK` rim and the Polaroid inset. The enemy's is its corp hue with the `CorpPattern` and a notched edge, and the W5 bust sits above it. `FOCUS` brackets mean target only.
- **Classes:** the eight bezels/hubs are pairwise distinct (tested). Ghost and Botnet move on a T0 loop.
- **HP arc:** 12 px on `hp_color`, a hatched `HARM` ghost, a two-stage drain, a heartbeat below 25%, and a 30% dim at 0.
- **HP number:** it sits under the arc on **every** wheel, not only on multi-needle bosses, so it's never under a needle.
- **Boss:** 120% with a taped nameplate, phase pips, the W5 hologram behind it and a T4 `BossIntro`. At a phase change the new needle draws on.

**The hub (§6.1, §4.3.4)**
- One stamp at a time (`HubQueue`).
- The hub's words each get their own row, in this order: inset, name, core, status. A row steps down to caption, then folds into the hub's tooltip. The inner ring's names run along its band, as 3-letter tags when they don't fit.
- W3 was sent back once for overlapping hub lines. It is fixed, and a test covers all 8 classes plus a boss at 1.0/1.6/2.0.

**Forecast and numbers (§6.2)**
- The "YOU TAKE/TAKES/BLOCKED" chips are gone from the operative's tag. One net line under its HP ("−3 ♥ (7 − 4)") equals the real result.
- Chips are `body`, not `label`, so one row holds the damage chips.
- Numbers: one per hit, `HARM` for a full hit or `WARN` with "7 − 4" for a partly blocked one. Overkill reads "(12 capped)". A fully guarded hit keeps its "0" equation, off the HP number.

**Layout and scale (§11, §12)**
- The NEXT plate reads "NEXT TURN 56". The bible's "−56" is read as a separator.
- "≤12% of the screen" is measured by area.
- Wheel lettering stops growing at 1.3, and the HP number stays at its 1.0 size, so wheels keep ≥70% of their size at 1.6/2.0.

**Resolve speed and dev pickers**
- Resolve speed works through `Engine.time_scale` during the replay. Instant shows the end state, and fast-forward is exempt from MotionSkip.
- The dev picker (TilePicker/Stepper) shows only when combat runs standalone.

**Open requests**
- W8b: the top bar is squeezed at 2.0.
- W5 (orchestrator follow-up): the Polaroid caption is clipped at 2.0 ("BREAKE").
- W6: `CombatFxLayer.stamp` could draw a StatIcon by status.
- W1: paper-ink variants of GAIN/HARM (OutcomeRow darkens them locally).
- W2: `StickerButton` grows very large at 2.0.

These go to the final sweep (W9/W10) unless a screen wave takes them first.

#### 2026-09-29 — Art pass W8a: title family and shared glass (merged into `art-pass`)
Review folder: `docs/art_review/W8a/`. It includes a 43-screen regression sheet at 1.0 mouse.

**Baked art (§4.3 rule 5)**
- The logo and the NEVER SLEEP / TRUST NO ONE scrawls are original path-drawn SVGs (`tools/art/w8a_svgs.py`), rasterised at the size they're drawn.
- The scrawls are solid marker graffiti. They were sent back once because the first version was a hollow outline.
- The NEVER SLEEP subtitle shows in every locale except English.

**Title (§11)**
- The profile readout stays, but as a GLASS "UPLINK" of icon + number fields, so the page keeps exactly one PAPER note.
- The Continue glyphs are ink on the pink primary.

**Options (§6.5, §5.3)**
- A picker tile is a short name plus a meta line. A toggle has a short label with its description as a caption underneath.
- Every section is built once and shown at the largest section's size, capped by the room available. Its scroll view keeps side room for the pad focus scale and brackets. It was sent back once for clipping at 1.6, and a test now covers every row, tab, scale and input.

**Pause (§5.3):** narrow around its lines, and `MENU_SIZE` wide only while Options or the Codex are open.

**Shared APIs**
- `PageTransition.enter`, `open_modal`, `close_modal` and `after_modals`.
- `TerminalWindow.scroll_body` and `ZinePanel.scroll_content` (FitScroll + ScrollHint), and `empty_share()`.

**Orchestrator grant.** In `netrun_scene.gd` (W8c's file), LEAVE THE MODEM now sits `SP_M` under the REMOVE A CARD spinner instead of at the fixed `LEAVE_AT` y. Placing it under the window put it off screen at 1.6. W8c keeps this rule.

**Open items for W2 (final sweep)**
- `FitScroll`/`ScrollHint` can crash when content measures thousands of px tall for one frame.
- `TilePicker` should wrap long tile names.

**Known gap:** high contrast doesn't restyle the custom-drawn paper pieces (case files, receipts, badges). This goes to the W9 sweep.

#### 2026-09-29 — Art pass WF: kit follow-ups (merged into `art-pass`)
Review folder: `docs/art_review/WF/`. This pass closes the open requests that W1, W2, W3, W5, W6, W8a and W9s logged against the shared kit.
- **FitScroll / ScrollHint:** a content height above 4096 px × text scale is treated as a pre-layout measure. It is waited out for up to 3 frames, then clamped. The crash itself still needs a windowed confirmation.
- **TilePicker:** names wrap at word boundaries onto up to 2 lines, stepping label → body → caption. After that the tiles grow, keeping one tile size per picker.
- **StickerButton:** the words yield before the sticker takes more than 0.2 of the page width. This is opt-in via `max_share`, and combat opts in.
- **Hand size (orchestrator):** `combat_scene.HAND_SCALE_MAX` is 1.15. Once the stickers were capped, the hand grew into their room at 2.0 and pushed the wheels under their 70% floor (§12).
- **Polaroid caption:** it steps down to caption, then abbreviates ("R n"; a name becomes first word + initials), then condenses to 70%. It never goes under 12 px and never clips.
- **Combat stamps:** `CombatFxLayer.stamp(..., icon)` now draws a StatIcon, and combat status stamps pass theirs.
- **New tokens (ART_BIBLE §3.3 row added):** `HARM_INK` #AB2E22 and `GAIN_INK` #396739. Both reach ≥ 4.8:1 on PAPER, PAPER_ALT, NOTE_PAPER and NOTE_YELLOW. They don't cover STICKER_PINK or NOTE_PINK. OutcomeRow, the CrewCard FLATLINED stamp, CaseFileCard's LOST and the toast's refusal mark use them.
- **High contrast on PAPER (ART_BIBLE §12 line added):** paper keeps its stock, words go INK at 7:1, edges are 2 px opaque INK, and tape and fills are opaque (`PaperInk`). This is applied to CaseFileCard, RunReceipt, AchievementBadge, Polaroid, Toast and CrewCard. CrewCard used to turn black; the orchestrator applied the change.
- **Steam Deck:** first run sets `Settings.city_quality` to 1 (additive setting; −1 means the look's default).
- **Tracking (ART_BIBLE §4.2 line updated):** tracking is now px per type step, via `UiTheme.TRACKING_PX`.
  - Anton: +1 at caption–title, +2 at heading/display, +3 at hero.
  - Mono caps: +1 at caption–label, +2 at title/heading, +3 at display, +4 at hero.

  No view calls `tracked()` yet; the W9 sweep does that.
- **Bug fixed on the way:** `RunReceipt.fields` raised a script error on the Stats page's run history.

#### 2026-09-29 — Art pass W8c: netrun pages and run end (merged into `art-pass`)
Review folder: `docs/art_review/W8c/` (28 before/after sheets, a FLATLINED T4 strip, a shred no-reflow strip). Its README lists 24 decisions; the main ones follow.

**Loot (§11)**
- "Hover size" means at least `HOVER_SCALE`, filling the modal's row up to 1.4×.
- The picked card is stamped TAKEN (T2) before it flies.

**Modem (§4.2, §5.3, §6.7)**
- Chip tiles letter at text scale × 15/12, so W4's caption step draws at `body`.
- Two columns up to text scale 1.15, then one scrolling column. Known gap: its CARDS window is more than 25% empty at 1.6/2.0 (W9 sweep).
- BUY/SHRED stickers are always buttons, and the sign carries no decorative notes.
- Unaffordable means the paper is kept, with a DISABLED edge, a lock and "NEED n · HAVE m".

**Raid interlude (critique 28):** the asset is picked once per interlude, and each node row has its own "Deploy here".

**Events (§11):** a leading "SPEAKER:" is dropped from the event title and story, so the speaker plate is the only mention.

**Run failed (§11, §8 T4)**
- The grey is a desaturate-and-dim shader inside the run-end page, because W7 has no grey context. W9 sweep: add a `flatline` context to CityAtmosphere so it also covers the subtitle band.
- The sequence is `run_end_flatline` (2.4 s, skippable). Under reduce effects the end state shows at once.

**Overlaps with the unmerged ANIM-R5 netrun branch, to resolve at its merge**
- B1: shares `EventText` and `VC_CHARS_AFTER_SHAPING`.
- B3: keep `RunEndStage` and feed its `end_fate()`/`heat_reason()` into `stage.fate_label`.
- B5: the loot hold is extended by the stamp.
- B9: `_ahead_row` keeps its node names.
- B11: keep `SlotPicker` and take its SOCKET_TIP words.
- B4: `words_typing()` must ignore `RunEndStage`'s `Typing.META` tween.

**Open requests, for W8b or the W9 sweep**
- A generic `PageTransition.settle` hook: today the run end rides `Typing.META`.
- The price on UPGRADE and the marker circle reveal in `spinner_view.gd`.
- DeckView's "Left click / Right click" wording, and it running off the canvas at 2.0.
- The top bar is two rows at 2.0 (W8b).

#### 2026-09-29 — Art pass W8b: HQ, new campaign, Grid, raid, maps, top bar (merged into `art-pass`)
Review folder: `docs/art_review/W8b/`. It holds 64 before/after sheets, strips of the ring swap and the crew stamp, and the README with the §14 checklist.

**Top bar and subtitles (§6.9, §5.2)**
- The top bar is always one row. Its height depends only on the text scale. Values step down instead of wrapping.
- From text scale 1.3, the tag labels, the page title and VIEW LOADOUT fold into tooltips.
- CARDS and DAEMONS show `FOCUS` brackets while a matching item is dragged (`HudBar.watch_drops`).
- The subtitle band is two lines above 1.0.

**Screens (§2, ruling Q4, §5.3)**
- The HQ gets the full DECK frame (`DeckFrame`, `DeckMonitor`). Other pages don't; they use the city's map mode.
- The raid setup re-lays out at text scale 1.3 and again at 1.8, so START DEFENSE is the one primary on its first screen.

**Words, maps and raid (§4.3 rule 3, §11, §10.2)**
- Wrapping is whole-word only (`AUTOWRAP_WORD`, including UiWrap). A chip grows rather than breaking a word.
- The raid map shows no tier pips. Its zoom floor is 0.36, or 0.2 at big text.
- Home hits that land together fly as one summed number.

**Edits outside W8b's files (minimal):** `raid_fx_layer.gd` and `ui_wrap.gd`.

**Handed to the final sweep (W9F)**
- Calls to add in `netrun_scene.gd`:
  - `hud.watch_drops(drops)`;
  - `route_legend.set_opened(...)` in `cycle_target`;
  - interlude START DEFENSE as `UiTheme.PRIMARY` with PLAY;
  - `city_overlay.corp_id` in the grid-zoom view.
- `crew_card.gd:107/126` uses WORD_SMART, which splits "BREAKE/R" at 2.0.
- The Polaroid's "R0" caption overlaps.
- The `spinner_view` hub name clips ("BREAKER COR").
- `dialogue.gd` `_fit_page` can shrink text below caption.
- The W10 runtime lint should measure scaled subtrees on screen and not measure contrast through modal scrims.
- The empty subtitle band is tall at 2.0.

#### 2026-09-29 — Art pass W8d: campaign end (merged into `art-pass`)
Review folder: `docs/art_review/W8d/`. It has 8 before/after sheets, the WON and LOST T4 strips, and the landmark art sheet.

**WON (§11)**
- The target corp's landmark (a new 200×300 SVG per corp) tips 20° and sinks 10%, so its shape still reads.
- It is then crossed out by two `CELL_PINK` `marker_stroke` strikes at ±48°, followed by baked overspray.
- CORP DOWN appears in `GAIN` at hero size.
- The crew wall shows survivors TRIUMPHANT and the dead FLATLINED. The cards are taped, with fixed tilts within ±4°.
- The city leans from its current campaign progress to 1.0 (`city_lean` signal). A new campaign resets it to 0.

**LOST (§11)**
- The Cell's hexagon (a ring with an upward chevron) cracks in `INK` from the top, then the halves part.
- CELL BURNED appears in `HARM`.
- The grey reuses W8c's run-end grade.
- Survivors on the wall are HURT and the dead FLATLINED.

**Contrast (§2):** a full-stage GlassScrim sits behind the stage, because the stamp met the lit city at under 3:1.

**Story text (§4.2, §5.3)**
- Story text is folded at word boundaries to 70 characters. Plex is narrow, so a width limit alone let about 85 characters through.
- At 1.0 a long story scrolls inside its paper. At 1.6 and 2.0 the page stacks and scrolls; never a scroll inside a scroll.
- The full ICE records sentence is the receipt's tooltip.

**Motion:** `campaign_end_won` and `campaign_end_lost` (T4, 2.4 s, skippable).

**Merge note for main:** `main` has its own ANIM-R5 `show_end` (`81f1a5f`). When art-pass merges into main, keep `CampaignEndStage`.

**Open, for the W9F sweep**
- `CityAtmosphere.clear_campaign_progress()` is missing.
- The grey and the scrim don't cover the subtitle band or the prompt strip (the same as W8c).
- The runtime lint should clip by scroll view.

#### 2026-09-29 — Art pass W9F: final accessibility sweep (merged into `art-pass`)
Review folder: `docs/art_review/W9F/`. It holds contact sheets of all 53 screens at 2.0 mouse, 2.0 pad, 1.0, grey, deutan, high contrast, reduce effects and reduce motion, plus the final runtime lint and the §12/§14 table (every item passes, with evidence).

**Text scale 2.0 is the verified maximum.** `LayoutScales` is gone, so every layout test now runs at `Settings.TEXT_SCALE_MAX`.

**Runtime lint findings at 2.0, mouse / pad:**

| Finding | Before | After |
|---|---|---|
| Font | 33 / 36 | 0 / 0 |
| Overlap | 34 / 71 | 0 / 4 |
| Clipped | 2 / 2 | 3 / 3 |
| Contrast | 76 / 101 | 7 / 5 |

Before covers 43 screens; after covers 53. The remaining findings are low-confidence (a mid-fade sticker, high-contrast button edges) or by design (the codex MORE BELOW tag).

**Decisions made in the sweep:**
- **§4.3.3:** a word that can't fit makes its label grow to the longest word. A width-driven font step-down was tried first and dropped: it looped the layout, and once filled the disk.
- **§5.2 / §10.5:** an empty subtitle band holds one line and grows once per screen, when the first line arrives.
- **§9 / §11:** `flatline` is an additive `CityLookData` context with an optional `lean` grade key. This is a schema change, covered by the smoke test. `CityAtmosphere.blend_context(ctx, mix)` and `clear_campaign_progress()` are new; a new campaign clears the lean. FLATLINED and campaign LOST both grey the whole city. The campaign end's scrim is HQ-level, full screen.
- **Motion settling:** `PageTransition.settle` calls `settle_motion()`, and the end stages no longer ride `Typing.META`.
- **Critique `55`:** the button reads "UPGRADE · n CYCLES", with NEED/HAVE in `HARM` when short. The marker circle draws on (`upgrade_circle_draw`).
- **§5.2.4 / §12 in fights:** the pad prompt bar sits in the status row with caption-size verbs. The Settings button hides on pad, and SEND IT draws its button glyph.
- **§12:** reduce motion also removes shake and turns the jack zoom into a cross-fade.
- **§6.10:** the raid playout and report map keys fold above 1.3.
- **§3.7:** the subtitle paper's speaker name is ink (pink read 2.3:1), and the pad prompt bar gets glass behind it.
- **Whole-word wrapping:** no `WORD_SMART` or `ARBITRARY` remains anywhere in `scripts/**` (tested). All mouse-worded strings have pad variants, and FocusTip filters out mouse words on pad.
- **Tracking:** `UiTheme.track_label` is applied to Anton and to mono caps labels.

**Open for the designer:**
- On a pad at 2.0, the SAVED toast can sit over an event's story for 2.5 s.
- Text drawn in `_draw` isn't linted, only checked by eye.
- Colour-blind support stays a daltonize correction (ART_BIBLE §12 says "remap").

### 2026-09-28 — Test suite: bounded waits
Tests that started a motion and then waited a fixed time (a timer, `wait_seconds`, a fixed
frame count, the wall clock) before asserting kept flaking under parallel shards (a few
were fixed one by one in "Test suite optimization" and "Animation pass — bake crash").
Audited every script under `tests/`; only the scripts that force live motion
(`Motion.force_live`) and the netrun scene test wait on motion (headless, everything
else shows its end state at once and waits frames only for layout). No game code changed.
- **Helper** `tests/helpers/bounded_wait.gd` (`BoundedWait`; not `test_`-prefixed, so GUT
  never collects it): `until(tree, cond, limit)` polls the real condition once a frame
  and gives up only after `limit` seconds of **game time** (the frames' deltas, the clock
  tweens and timers run on) **and** `MIN_FRAMES` (60) frames, so neither a few stalled
  frames nor many fast ones cut a tween chain short; it returns at once when the
  condition holds, so the generous `SLACK` (2 s over the Motion table's seconds,
  `motion_limit`) costs nothing on a passing run. `timed` returns the game time less the
  two longest frames (each link of a chain may end on an overshooting frame) for "ends in
  its time" asserts. `frozen_frames(tree, n)` runs `n` frames at `Engine.time_scale` 0
  for asserts that a motion is still under way after the layout's frames (the opposite
  flake: one slow frame finishing the motion first); layout, redraws and deferred calls
  still run. Existing view-side queries sufficed (`motion_busy()`, `_seq`,
  `PageTransition.running()`, `FlightFx.active_count()`, `WheelView.tag_flips`,
  `drop_t`, `banner_alpha`, `Fx.transitioning()` ...); no hook was added.
- **Converted** (assertions kept; each waits on the state it then asserts):
  anim2 `test_the_sequence_plays_out_by_itself` (both loops), `test_a_spin_ends_on_the_exact_core_tick`,
  `test_the_nudge_queue_never_desyncs_under_rapid_input`, `test_intent_tags_flip_only_when_their_content_changes`
  (counts `tag_flips`; was two frames then "flipping or mid-flip");
  anim3 `test_a_cancelled_drag_returns_the_card_to_its_slot`, `test_ram_chips_drain_with_a_tick_and_settle_on_the_state`,
  `test_the_hand_keeps_a_gap_while_a_card_flies` (frozen);
  anim4b `test_motion_plays_live_and_input_completes_it` (waits for the shred strips, not half the feed);
  anim5 `test_heat_pulse_fires_once_per_crossing_and_never_on_a_steady_value`, `test_a_netrun_move_ends_with_the_marker_on_the_chosen_node`,
  `test_an_asset_drops_onto_its_node_with_a_stamp`, `test_the_folding_key_slides_and_frames_for_its_folded_line`,
  `test_playout_ends_on_the_resolved_campaign_and_speed_scales_it` (frozen),
  `test_jack_transitions_never_show_both_scenes` (the reduce-effects fade drops its four
  overhead frames: two held frames and each fade's last);
  anim6 `_until` (all five timed motions; game-time ceiling instead of 10 s of wall
  clock), `test_end_state_layout_is_the_instant_layout_at_every_text_size`,
  `test_a_press_mid_entrance_completes_it` (frozen), `test_hq_idle_runs_live_and_rests_headless` (frozen);
  R1 campaign `test_a_second_press_during_the_jack_does_nothing` and
  `test_netrun_leave_buttons_ask_once_during_the_jack` (were unbounded loops),
  `test_saved_switched_off_shows_still_then_goes_at_once` (every alpha seen is 1 or 0,
  then 0; was two fixed looks), `test_a_heat_crossing_rolls_the_number_and_stamps_a_banner_then_goes`,
  `test_the_event_choices_wait_for_the_words` (frozen),
  `test_placement_loops_end_on_geometry_that_is_not_finite` ("returns at once" = the same
  frame, not under 500 wall ms);
  R1 combat `test_the_forecast_and_the_turn_wait_for_the_replay`, `test_the_result_holds_under_this_turn`
  (waits for THIS TURN itself), `test_a_number_travels_into_the_hp_counter_which_rolls_down`;
  R2 city `_until` (game time), `test_a_threaded_bake_builds_in_slices_and_lets_the_slot_go`
  (20 s of game time and 600 frames), `test_the_jack_says_where_it_connects_while_the_screen_builds`
  (was 240 frames), `test_an_asset_drop_waits_for_the_camera_then_lands_with_its_name`;
  R2 combat `_entrance` (both users), `test_held_choices_read_and_carry_a_typing_mark`,
  `test_the_entering_plate_never_hides_the_forecast`, `test_the_crt_roll_waits_for_the_glass_to_show` (frozen);
  netrun scene `test_a_whole_run_plays_through_the_scene_and_autosaves` (waits for the
  page after the combat end hold instead of 1 s).
- **Kept, marked `# fixed-wait-ok:`**: the 0.3 s / `SETTLE_WAIT` waits that only let
  motion run before a skip, `finish_all` or settle (anim2, anim3, anim4, anim4b, anim6
  game-state tests) and the resolver's performance bound (layout rules, best of 20
  batches; TECH_SPEC 10).
- **Suite rule** (`test_suite_integrity.gd`, `test_no_fixed_wait_gates_an_assertion`): a
  `create_timer(`, `wait_seconds(` or `Time.get_ticks_msec/usec(` in a test script is
  flagged when an assertion (`assert_*`, `pass_test`, `fail_test`, `pending`) follows it in
  the same test, or when it sits in a helper function (its caller asserts after it),
  unless the line or the comment line above carries `# fixed-wait-ok: <reason>`. Strings
  and comments are not code. Fixed frame counts are not flagged (a frame count is right
  for layout, and a rule could not tell the two apart); the review rule is in
  `docs/TEST_SUITE.md` ("Waiting on motion").
- **Left as is:** the R2 city multi-band Heat rise reads the banner at the first frame
  after each pulse; one frame long enough to carry the roll over both 25 and 50 would
  still miss the first banner (no flake seen). The combat scene's
  `motion_seconds_left()` measures wall time (game code; tests only use it for a limit
  plus slack).
- **Evidence** (969 tests; other agents ran Godot on the machine meanwhile): 10
  consecutive `python tools/run_tests.py -j 4` runs, all passing, 0 pending (176-305 s);
  5 consecutive `-j 8` runs, all passing, 0 pending (158-199 s); one more `-j 4` run after
  merging main; `tools/schema_smoke_test.gd` and `tools/validate_content.gd` pass. (Two
  last mid-motion looks, anim3 hand gap and anim5 playout, were frozen while the first
  `-j 4` run was under way; runs 2-10 and every `-j 8` run ran the final tests.)

### 2026-09-27 — Designer rulings on the open questions (resolved by the designer)
Answered by the designer as a numbered list against the open-questions digest. Defaults
accepted unless noted; the items that need work are scheduled in MILESTONES
("Queued passes").
1. **Late-campaign Grid labels** keep off other nodes' icons too (built in ANIM-R1).
2. **Grid at 1.6**: keep the folding map key, icon-only step buttons and LABEL_REACH 110 px.
3. **Subtitles outside combat** stay in the top band.
4. **Toasts** stay for refusals, saves and unlocks.
5. **Drag pick-up** is X / Space; A keeps each button's meaning.
6. **Recall** is a drop on CORE.
7. **Changed:** a drop on JACK IN does *not* start a run ("drag and drop to start is not
   intuitive"). Select the operative, then press JACK IN. Crew drags only select (ANIM-R1).
8. **Motion values** as chosen from the strips.
9. **Changed:** cards upgrade. Cards are in the shop and upgrades are a balance lever; a
   new horizontal pass designs and builds card upgrades (Queued passes).
10. **Changed:** players may rearrange wheel slices at any time outside combat (a new
    horizontal pass; Queued passes).
11. **Changed:** the daily run changes more than the seed. A horizontal pass builds a list
    of daily modifiers and tests that each one works (not exhaustive combinations).
12. **Pacing**: raise rewards slightly (not lower enemies); tune by simulation.
13. **Rigger at ICE 0**: a small buff to its hub or deck.
14. **Final Rack**: an extra Schematics payout; ICE 0 length is fine.
15. **REBEL_CELL difficulty**: leave the Mirror factor.
16. **Ghost**: leave until playtest.
17. **Rigger speed**: leave its Atk 16 slices.
18. **Changed:** each corporation unlocks differently. Beat Solace to open Meridian;
    Halcyon is bought with Schematics; REBEL_CELL opens after ICE X on each other
    corporation; Orbital's rule is set in the unlock pass (Queued passes).
19. **Meridian difficulty**: no change; the ICE ladder handles it.
20. **Boss stalls**: add a soft enrage.
21. **Solace**: no guaranteed Cleanse-type card.
22. **Enemy damage scaling**: leave 1.2 per tier.
23. **Patrol runs**: no cap.
24. **Schematics surplus**: add more sinks (boosts and unlocks).
25. **Confirmed as built**: Perfect-hook burst for every class, hooks repeat per resolution,
    alternatives cost 60 with no base unlock, the freeze cooldown, custom-handler Daemons
    not mirrored, and Meridian without raid music of its own for now.

### 2026-09-27 — Test suite optimization
The designer asked to look for overlapping tests and to speed up the suite (about 49 min
single-process for 858 tests, over 60 min on a busy machine). Details, the profile, the
coverage mapping and the commands: `docs/TEST_SUITE.md`.
- **The cost was the city, not the tests.** Profiling (GUT's JUnit times per test) showed
  that about 87% of the suite's test time was the headless neon city: its procedural geometry
  was rebuilt in GDScript (2-4 s a build) on every scene open, camera move and resize.
  Two test-run-only switches on `NeonCity`, both on only when the process runs GUT
  (`gut_cmdln.gd` on the command line) and off in the game:
  - `geometry_memo_enabled`: a built geometry is kept (at most `GEOMETRY_MEMO_CAP`, least
    recently used out), keyed by every input the build reads (seed, district, net mode,
    inks, face texture, cultures, exact creep and influence, colour, size and camera), and
    reused by a redraw with the same inputs.
  - `emit_triangles` off: the build skips emitting the triangles the dummy renderer never
    shows, and still places every roof, window light, trail, beacon and sign the overlays
    and tests read. `test_city_geometry_memo` builds every district, physical and net,
    both ways and checks the placed geometry is identical; it also keeps the drawing code
    running with triangles on.
- **Consolidation, coverage kept.** The four every-corporation Grid sweeps of H21-H24 city
  (50 settled Grids) are one sweep, `test_city_map_sweeps` (30 Grids: every corporation,
  text size 1.0/1.3/1.6, early and late), running every check the four made; the H21 and
  H22 route sweeps are one route sweep; the H23 SAVED-stamp screen sweep is covered by
  H24's. Every removed assertion is mapped to the test that keeps it in
  `docs/TEST_SUITE.md`. No UI sweep was sampled down: each corporation has its own Grid
  (per-corporation bugs have happened), 1.3 is `MapLegend.FOLD_SCALE`, early and late are
  different layouts, and after the city fix the whole sweep costs about a minute.
- **Isolation for parallel runs.** Under GUT, `SaveService.save_dir` is the run's own
  folder `user://saves/gut_<pid>` (removed when the run ends), as Settings already had
  `user://gut_settings_<pid>.json`; the tests' own temp files carry the process id. The
  parallel runner also gives each shard its own user:// (APPDATA / XDG_DATA_HOME).
- **Parallel runner and tiers.** `tools/run_tests.py` splits the scripts into N shards
  balanced by the times in `tests/test_manifest.json` (longest first), merges the JUnit
  results and fails on any failing test, crash, timeout or script that did not run (GUT
  skips a script that fails to parse and still exits 0). The manifest gives each script
  its tier: `fast` (the rule guards, every pure-core script and the cheap screen scripts,
  under 2 minutes) or `full`. The full suite stays required before work is declared done.
  `test_suite_integrity` checks every test script is listed once with a tier, holds a
  test, and that the fast tier keeps the preview, rewind, replay, RNG, wheel math, raid
  resolver, map generator and save guards.
- **Order and timing robustness** (shards run scripts in another order, and fast frames
  change timing): pad reachability now restores the pad state it switches on (it made a
  later key-hint test read "R3"); the anim6 motion checks and the anim5 jack fade measure
  game time less the longest frame, with slack of the motion's own length, instead of
  fixed waits or wall time; the anim6 event stamp compares with the row's own size (it
  caught the row mid-pop once frames were fast); the resolver timing takes the fastest
  of 20 short batches (same 300 turns, same 1 ms limit).
- **Result** (busy machine, 864 tests): one process 10-12 min (was about 49); the runner
  at N=4 about 4.7 min (median of three), N=2 about 7 min; the fast tier 1-2 min.

### 2026-09-27 — H24 combat: every drawn word translates once, text that fits at big sizes, turns that explain themselves
From pass 24 (both audits, a first-time player and a player who can't read English;
GAP_ANALYSIS H24). New standing rule from the designer: nothing is deferred. Every
finding gets a slice, and motion is now its own dedicated Animation pass.
- **Translate once**: the slice, aim and status words (`Palette.*_WORDS`), "YOU", SEND IT
  (drip lettering), the RAM bar, the Heat poster (WANTED, the ransom-note letters of the
  translated word, capped at `RANSOM_LETTERS_MAX`), "+N MORE", "? RANDOM STATUS", RESPIN
  and UNDO stickers, the aim hint and refusal toasts all go through `tr()`. Labels that
  get pre-translated text (the status line, the aim hint, the toast) and the combat
  stickers (`StickerButton.pre_translated`) don't translate it again. "%+d" keys became
  "%s" with `CombatScene.signed()`: Godot's pseudolocalisation override doesn't skip "%+d"
  and dropped the numbers.
- **Fit at big text**: the status line shrinks its font to its width (floor
  `STATUS_MIN_FONT`, re-entry guarded). The dev fight picker is one dropdown, so the line
  has its room in the standalone fight too. The aim hint sits above both the hand and
  the RAM row and shrinks to the room to the screen's edge. It is sized from its font,
  because a Label's minimum lags a font change by a frame.
- **HP block layout**: one `hp_layout()` places the HP number, the NEXT plate and the LAST
  TURN plate. Drawing, satellite tokens and satellite HP plates all use it. Tokens that
  would meet the block move beside it. Plates try sideways first under the disc and keep
  clear of the tag and the block.
- **LAST TURN** is a dark plate across the view's width. It first shrinks on one line to
  its text-scale-1.0 size, then takes a second line where the view has room, and only
  then goes smaller. The wheel keeps its size; a second reserved line had cost 10 px of
  radius at 1.6. The line also shows the RAM a new turn brings back ("RAM +4"), a
  satellite's or drone's block on its host ("GUARD +3 BLOCK"), and shield actually gained.
  `gain_shield` now reports the gain after the cap, with the request kept as
  `requested`.
- **Readable results**: a loss chip is followed by what block and shield soaked ("3
  BLOCKED", from a new `soaked` count in `CombatOutcome`). A hovered card or nudge puts
  "IF JOLT" / "IF NUDGE" first on the tag of the wheel it acts on. The hub tooltip says how
  the fight is won or lost. The tag tooltip explains the aim dots.
- **Hit-testing**: the nearest satellite or arrow within reach takes a click. At 1.6 the
  inner ring's arrow had answered as the outer one, and a drone beside an arrow took its
  clicks.
- **Hub names** shrink to their 1.0 size, then split onto two lines at the best space,
  and only then shrink further.
- **Toasts** (refusals and the respin note) sit at the foot of the right column under the
  subtitles, wrapped to its width. Over the hand they covered the cards (H21 had moved
  them off the HP arcs). They are re-anchored a frame later, when a wrapped label knows
  its height.
- **Aim line** is drawn under the UI root, so the wheels' HP and NEXT stay on top.
- **H23 wheel-size figures corrected**: 126 → 97 px was the standalone fight. In a run the
  wheel is 108 px at 1.0 and 81 px at 1.3 and 1.6 (75%). `BIG_TEXT_RADIUS_KEEP` is the
  bound the tests hold.
- Tests: `tests/unit/test_horizontal_pass24.gd`. Updated on purpose: pass-21 (the toast
  sits in the right column) and pass-23 (tokens measured against the real HP block).
  Views only, plus the shield event's amount: the balance numbers stand.

### 2026-09-27 — H24 city: a folding map key, runs that say what they give, one icon per concept
Pass-24 items K1-K8 (City Grid screen, map overlay, HQ mini-map, the icon set). Views
(`scripts/ui/kit/`, the Grid page of `hq_scene.gd`) and one pure preview in
`CampaignRules`; no rule or content change. This entry also answers the H23 city open
questions (the Grid at 1.6, the key's size, LABEL_REACH), removed from the list below.
- **The Grid at big text keeps its map (K1).** From text scale `MapLegend.FOLD_SCALE`
  (1.3) the Grid's key folds to one line, its MAP KEY button (StatIcon "more"); pointing at
  it or pressing it opens the rows over the map (pointer: they fold again when it leaves;
  press: until pressed again), and on a pad Y (`cycle_target`, prompt "Y Key" on the Grid
  at big text) does the same. The map is framed for the folded line (`MapLegend.fit_size`),
  so opening the key never reframes it. At 1.0 the key stays open as before (it took ~18 %
  of the map's height; at 1.3 about a third, at 1.6 over 40 %). From the same scale the
  step buttons show their icon only (PREV / NEXT keep "<" / ">" with the map icon of the
  Site they go to, Back to HQ its arrow), their words in the tooltip. Measured over all
  five corporations, early and after six runs: the Grid now keeps its own framing (city
  zoom 0.72, was ~0.4-0.57 at 1.6) at every text size.
  Labels are laid out inside the map area itself (`screen_rect` = the GridMapArea: below
  the top bar and the subtitle band, left of the column; "Kill-Switch Authority" sat at
  y≈86 on the top bar). A long name with no room on one line tries two lines
  (`CityMapOverlay.wrap_lines`) before it is left out.
- **LABEL_REACH stays 110 screen px, now measured, and it binds every label (K1).**
  Distance from a label's nearest point to its node, all Grid labels placed in the test
  above: x1.0 n=121 median 21 p90 67 max 98; x1.3 n=104 median 21 p90 75 max 76; x1.6
  n=89 median 21 p90 86 max 86. The one-line candidate rings reach at most ~91 px at 1.6
  (big icon 17 + gap 4 + two rings of a 31 px label + gaps), so 110 keeps every one-line
  spot and every placement measured, with room for an inward move; a two-line label's
  outer rings (up to ~135 px, seen before the cap) are now refused (`_free_spot` checks
  the reach too).
- **Every Site with room gets a label (K1).** The test checks, for every corporation,
  early and late, at 1.0 / 1.3 / 1.6, that no Site with a label to show is left out while
  a spot near it is free (`CityMapOverlay.unplaced_with_room`), labels never overlap,
  stay on the map area under the top bar, and within reach. Labelled of named Sites at
  1.6: 7-12 of 10-16 (the rest have tooltips, and the run rows light them, K4).
- **The step row stays in the column (K2).** The row sits in a MarginContainer that keeps
  it off the column's scroll-bar strip (Back to HQ reached x≈1275, past the windows'
  border); a button whose translated words are wider than the column takes its short
  form, and if still too wide wraps its words inside the column (`_fit_steps`). Tested
  pseudolocalised (accents, doubled vowels, fake bidi) at 1.0 and 1.6 with a raid pending.
- **GRID_FITS_MAX is 4 (K3).** The code has had 4 since H23; the H23 entry said 3 and is
  corrected (the code stands: four passes settle a 1.6 raid layout). A test reads the
  constant and the log.
- **Run rows say what clearing gives and risks (K4).** `CampaignRules.clear_preview(c,
  corp, cfg, site, lookup)` applies `on_run_completed` to a copy of the campaign (so the
  preview is the real result; tested for every open run of every corporation, early and
  late) and returns the Heat change, the Exploit, a raid queued, Schematics, the win, the
  Sites it opens and whether it becomes claimable. Under each RUNS OPEN NOW row a line of
  badges says it with icons (EXPLOIT, HEAT -n with the cooling icon, RAID, WIN, +n
  Schematics, OPENS n with the Sites named in the tooltip, CLAIM; "NO GAIN" for a
  patrol), and the row's tooltip says it in words. The ten opening T1 rows now differ by
  what they open. Hovering a row or giving it the pad's focus lights its node on the map
  (a paper ring with four ticks, and its name label even for an unnamed Site:
  `CityMapOverlay.hover_id`); pointing at a node lights its row (`node_hovered`, the row
  takes its hover look).
- **One icon per concept (K5).** Each map kind is a silhouette plus a symbol
  (`CityMapOverlay.KIND_SHAPES` / `KIND_SYMBOLS`, `icon_id`); no two kinds share a
  silhouette. The Heat reduction Site is a drop with a new StatIcon, COOLING (a small
  flame and a down arrow): the snowflake is ICE's only. The Modem shop is a price tag with
  the shop's bag (StatIcon SHOP), no longer the Exploit's diamond; the Exploit Site draws
  the Exploits StatIcon inside its diamond (as on the top bar); the Rack became a tall
  box (it shared the plain Site's hexagon). The key rows carry and draw the map's icon
  (`icon_id` meta), the HQ mini-map floats the same icons (it drew font glyphs ◈ ❄ ✦ ⌂),
  the Site card's heat badges use COOLING, and new StatIcons CLAIM (spray ring) and LINKS
  (Sites opened) serve the run rows. STYLE_GUIDE 4 lists the kinds. Words: the map
  screens use no SHD / shield wording (tested); the combat words DEFEND / ATTACK / EVADE
  are the ones to use there.
- **Grid icons never overlap (K6).** An icon's box now includes its tier pips (the pips of
  one icon sat on the icon below); a crowded icon takes the first free column beside its stalk
  at its height (ICON_FAN 0, +1, -1 icon widths; ±2 as well cost labels), then a step higher, up to
  ICON_STACK_MAX steps, then floats higher (up to ICON_STACK_LIMIT). Sideways first keeps
  a crowd low: stacking the taller boxes first pushed a Rebel Cell raid map at 1.6 past
  its frame (the H23 raid-framing test caught it). Same order, front to back, ties by node id. Tested: no
  two icon boxes overlap at 1.0 / 1.3 / 1.6 for every corporation, early and late.
- **Map words translated once (K7).** Words drawn with draw_string go through
  `CityMapOverlay.tr_word` (the TranslationServer): kind words, "CORE", the tier ("T%d":
  the letter translates, the number and pips carry it), the mini-map's labels and HOME
  line, the Site card's status badge and tag. Labels and buttons that get pre-translated
  text (key rows, run rows, the card's tag) have auto-translate off, so nothing is
  translated twice. Tested with pseudolocalisation on (and restored).
- **Mini-map labels keep off the Site blocks (K8).** The last-resort pass that let a label
  lie over other blocks is gone: a label shortens (name, "T2", the pips) or is left out
  (the Site keeps its tooltip). Tested against every Site's block and icon rect
  (`GridMapView.icon_rects`) at 1.0 / 1.3 / 1.6 for every corporation.
- Test expectation changed on purpose: pass21 city's "bigger boxes at a bigger text size"
  compares a label's height per line (a label may now take two lines at one size and one
  at the other). The H23 city test's label checks now also see two-line labels (still
  apart and in reach) and pass unchanged.
  Tests: `tests/unit/test_horizontal_pass24_city.gd`.

### 2026-09-27 — H24 screens: every word to the translators and translated once, a key that makes room, pages that carry words, lines that end with their screen
Pass-24 screens items S1-S17 (the audits, a first-time player and a player who can't read
English looking at the pass-24 storyboards, the scrambled one included). Views and tools
only: no rule, content number or balance changed.
- **The code's words reach the translators (S1).** `tools/export_text.gd` also exports
  every string literal passed to `tr`, `atr`, `TranslationServer.translate` or the new
  no-op marker `TextDb.mark` under `scripts/`, and every literal on a line ending in the
  marker `# TR` (words kept in constants: node words, map key rows, verbs): their English
  is the key itself (`TextDb.code_keys`, `TextDb.unescape`). `strings.csv` regenerated (the
  `.translation` is rebuilt by the import). **After merging another branch's new tr()
  words, run the export again** (a test checks every code key is in the CSV).
- **Signed numbers (S2).** `TextDb.signed(n)` ("+3", "-2", "0"); a translated line takes
  the number as `%s` (Godot's pseudolocalisation accents the `d` of `%+d` and the format
  broke). None of the H24 screens' translated lines has `%+`; the combat's
  (`combat_scene.gd`, `wheel_view.gd`, other owner) still do.
- **Translate exactly once (S3, S4), the rule:** a page translates its words where it
  builds them (`tr` for code words, `TextDb` for content) and shows them as given
  (`TextDb.shown_as_given`: auto-translate and tooltip auto-translate off for the page's
  tree). Applied to the HQ, Grid, raid setup and playout, the netrun pages but the fight,
  the title, the top bar, the pause and settings menus, the confirm dialog, the deck and
  spinner viewers, the Daemon tray, the raid playout panel, the MORE BELOW tag and the
  SAVED stamp. Parts that show their own fixed words as keys translate themselves
  (`TextDb.translates_itself`: the city agent's `MapLegend`, found by class name). Drawn
  words (Badge, ZineNote and ZinePanel titles, GraffitiTag, GraffitiScrawl, HudBar's
  title, CrewCard, route and raid map labels) come translated; kit parts that translate an
  internal key use `tr`, not `atr` (HudStats names, AssetCard HP/LEFT, StickerButton,
  ForecastStamp, BuyButton's verb, PadPrompts' verbs). The Modem sign draws its translated
  words in the cybernetic face when it has every letter (`CyberType.can_draw`), else in the
  display font. The route and raid overlays show the node tips the screens build as given.
  The REBEL_CELL tag on the title and start screens stays as the brand mark (not
  translated). `TextDb.t` / `ui` / `voice`: a key no catalogue has (a generated Mirror
  elite) gives the content's own text, pseudolocalised once, never the key
  (`TextDb.has_message`). Dialogue's speaker name is translated once (`speaker_name`), the
  name label shows it as given.
- **Late-campaign raid map (S5).** The raid key starts as the column at the map's left;
  when the nodes cannot fit beside it without zooming out past `RAID_MIN_ZOOM` (now 0.45,
  was 0.6), it becomes the Grid's strip key along the map's foot (`_use_raid_strip`), and
  the map is framed above it. The choice holds for the layout (`raid_layout_key`: text
  size, screen, network size), so redraws of the same setup keep it.
- **B-back (S6).** Only a pad's B (`InputEventJoypadButton`) leaves the Modem, the Grid
  and the raid setup; a keyboard's Esc is `ui_cancel` too and left when `open_settings`
  was rebound off Esc.
- **SAVED (S7).** `Fx.show_saved` places the stamp a frame later (a save runs before the
  new page is built: after a new campaign it sat on the Daemons button, stale geometry)
  and places it again every frame while it shows, so a pad prompt row or a late layout
  never ends up under it. `Fx.saved_screen` lets tests give the 1280x720 page.
- **Pager (S8).** `_wrap` takes the inline speaker's name as `lead`: a word that does not
  fit after the name fills the rest of the first line by characters, so page one always
  carries words (it showed "[SOLACE]:  …" alone).
- **Event (S9).** The choice column keeps `EVENT_RIGHT_GAP` (16 px x text size) from the
  screen's right edge. A choice that changes nothing shows a neutral empty-set mark and
  "no change" (`OutcomeRow.no_change`, kind `NO_CHANGE`) and says so in its tooltip.
- **Modem (S10).** Tiles lay out from `ZineCard.tile_parts`: the foot is the buy
  sticker's real height (`buy_room`), the icon shrinks (to `CHIP_ICON_SHRINK`) and centres
  in the room above the names, the effect lines fit between; shop tiles at 1.0 use the same
  layout when they carry a buy sticker. A shop card's corner chip mark is dropped under
  its buy sticker. The buy sticker's words go on two lines (verb over price) when one line
  would shrink under `TWO_LINES_BELOW` (85%) of the text size; slice tiles widen with the
  text as far as the SLICES window holds them (`slice_tile_size`). The shop items' effect
  text no longer carries an untranslated "firmware: " prefix.
- **HQ (S11).** From text scale `CrewCard.COMPACT_FROM` (1.3) dossiers are compact (the
  card grows only to `CARD_MAX_SCALE`, the Polaroid shrinks to 70%), so the crew sits side
  by side; every dossier fits the page view and is reached by the page scroll (mouse) and
  by focus (pad). The share code left the Pirate Radio note: it is in the note's tooltip and
  on the pause menu's seed line (`PauseMenu.code_line`).
- **Route (S12).** The route map is fitted into the area left of the ROUTE column
  (`fit_route_map`, at most `ROUTE_FITS_MAX` passes, never under `ROUTE_MIN_ZOOM`), as the
  Grid is. The Route Key lists what the node colours mean (here, next, later, visited, the
  corporation's). Each route choice says where it leads ("Fight > Event · Shop") and its
  tooltip what it pays (the fight's Cycle range) and what is after it: the enemy is rolled
  on entry, so what differs between two fights is the route beyond them.
- **Title (S13).** Continue is one word, with the saved campaign as a line of stat icons
  under it (`IconLine`: the corporation, Heat, ICE, runs, the state), the tooltip in words.
  Supersedes H23 S12's "left as is": the storyboard's title shows its own private slot
  (`title_scene.continue_slot`), created before the title shot, so it matches its HQ.
- **Raid setup (S14).** Defence cards carry a pictogram (crosshair: it shoots; snowflake:
  it holds threats; a lure: it pulls their routes) and a one-line effect built from the
  asset's numbers ("HITS 4 x2 · REACH 1", "HOLDS 2 STEPS", "LURES, PULL 3";
  `AssetCard.effect_of`). RUN THE RAID is START DEFENSE (and `ui.raid_intro`). The HQ badge
  and the DEFENSE LOADOUT title both read `armory_words()` ("ARMORY 3/6": assets waiting in
  the Armory, not those deployed, of its room) with the same tooltip.
- **Screen-tied lines (S15), the rule:** a line may be said with a `scope` (a screen); it
  ends when the player enters another screen (`Dialogue.enter_screen`, called by every
  page change), queued or showing; lines without a scope (Heat thresholds, raid warnings
  from a run, barks) play out. The briefing and the jack-in line belong to the route, the
  event text to the event, the Rack line to the loot, run end lines to the run's end, the
  raid warning to the raid setup.
- **Top bar (S16).** HudStats draws small captions before tag groups ("CAMPAIGN" at HQ;
  "CAMPAIGN" then "THIS RUN" in a run), each with a tooltip, outside a fight; every tag has
  a tooltip.
- **Whole text on focus (S17).** Loot stickers now carry `FocusTip` (the Modem's had it)
  and a tooltip with the name and the whole description. The combat hand's cards are the
  combat owner's.
- Notes for the other owners: the combat's translated lines still use `%+d` (use `%s` and
  `TextDb.signed`); the city files' constant words (`CityMapOverlay.KIND_WORDS`,
  `CityLayout.KIND_TIPS`) can take the `# TR` marker to be exported (the Grid page wraps
  them in `tr` already).
- Tests: `tests/unit/test_horizontal_pass24_screens.gd`. Updated on purpose: pass23's raid
  words test expects START DEFENSE; pass23's zero-outcome test lets the neutral "no
  change" item through; pass23's combat translation test uses a locale of its own (the
  English catalogue now holds the code's keys and answered first); `test_settings_extras`
  awaits `Fx.show_saved()` (placed a frame
  later).

### Motion pass
Motion choices (ANIMATION_HANDOFF 5), newest first. Timings live in
`content/config/ui_motion.tres`; each entry below says what was picked and why.

#### 2026-09-29 — Animation pass — ANIM-R6 rules
The sixth fix batch of the Animation pass review, motion rules, kit, test infrastructure and
docs (fix agent D, D1-D11). Every call below was the implementer's (nothing deferred).
Views, tools, tests and docs only. Tests: `tests/unit/test_anim_r6_rules.gd` (full tier)
unless named.

- **D1 the playout's own controls hold whichever helper sees the press.** The exception
  (a focus move, or a press on 1x / 2x / 4x / Skip, passes without ending the watched step)
  lived in the panel's own `_input`; when another running helper (a Typing label, the
  subtitle, a page entrance, a flight) saw the press first, `MotionSkip.handle` gave PASS
  and `complete_all` ended the panel's step anyway. Helpers may now answer
  `motion_passes(event)`; `complete_all(node, event)` (and so `handle` and `consume`) leaves
  a helper that lets the press pass running, and the playout answers it with
  `drives_playout`. Its `_input` is now plain `MotionSkip.handle` (fix agent C's file:
  the smallest change). The combat replay passes its press to `complete_all` too (fix agent
  A's file, one argument). A skip by hand (`complete_all` with no press) still completes
  every helper. Tests: a focus move and accept on 2x handled first by a typing label leave
  the step playing and complete the typing; a stray key handled by the label ends both.
- **D2 no inline motion numbers in the kit.** FlightFx's lift and fade shares and the
  choice stamp's down and hold shares move into the table (`flight_lift_share`,
  `flight_fade_share`, `choice_stamp_down_share`, `choice_stamp_hold_share`: tunings of the
  flight or stamp, `UiMotionData.ALWAYS_ON`, same values; the lift and the fade take their
  shape from their entry: the lift was an inline EASE_OUT); `FlightFx.lift_share()` replaces
  the netrun's read of the old const (fix agent B's file, one line). The jack's push eased in
  by an inline EASE_IN over the table's IN_OUT: it now takes the entry's ease and `jack_in`
  / `jack_out` say IN (the look kept). The reduced jack read the raw duration (it ignored
  1x / 2x / 4x): `Fx.reduced_fade_times()` reads `Motion.seconds` / `amplitude`, and the
  fades take the entry's shape. The shredder's fade takes `shred_feed`'s shape, the drop
  stamp's fade `drop_stamp`'s, the SEND IT drips' draw-back `send_it_drips`'s (it was an
  inline IN_OUT). A pop's grow ease is one named kit constant (`Motion.POP_GROW_EASE`),
  used by `Motion.pop`, SEND IT's squash and the wheel's resolve pulse (fix agent A's
  `wheel_view.gd`, one line). `combat_fx_layer.gd` (fix agent A's file) names its inline
  shapes: the played card's grow share (`PLAY_GROW_SHARE`), the dissolve's eases and the
  drawn marks' overshoot settle (`POP_SETTLE_TRANS` / `POP_SETTLE_EASE`). New entries play
  in the lab on the real flight and stamp. Tests: `test_no_tween_shape_is_written_inline`
  (scans every game script for a `Tween.EASE_*` / `TRANS_*` literal outside a const, an
  export default or a dictionary fallback, naming offenders; the dev-only demo drags are
  exempt), `test_the_reduced_jack_fade_runs_at_the_speed`,
  `test_a_flight_and_a_stamp_take_their_shares_from_the_table`.
- **D3 a view-level switch check.** R5's off-by-kind test checked only the kit's answers
  (`Motion.live` / `seconds` / `amplitude`), so a view that reads an entry's time and draws
  or tweens without asking whether it plays (the raid layer, the combat layer, the route
  crawl) passed. `Motion.recording` now also notes every `live` question (`Motion.asks`,
  the kit's helpers ask for their caller); two kit calls let a view ask in one step:
  `Motion.seconds_live(id)` (the seconds when it plays, else 0) and `Motion.switched_on(id)`
  (enabled, whatever reduce effects say: the reduced jack, reading times).
  `test_motion_lab_demos` plays every demo, keeps every entry read and every question, and
  fails on an entry with a motion of its own (not a part, a tuning or a hold) that a game
  script read but that no game script asks about, neither while the demos ran nor in its
  source (`live`, `seconds_live`, `switched_on`, or a helper that asks: `run`, `fade`,
  `pop`, ...), naming the entry and its readers ("switch ignored" lines). Holds (a time that
  is how long an end state or a word shows: `resolve_landing_hold`, `resolve_result_hold`,
  `combat_end_hold`, `toast_note_hold`, `jack_arrival_wait`, `asset_drop_wait`,
  `raid_incoming_hold`, `jack_connect`, `resolve_sequence`, `resolve_beat`,
  `resolve_pass`) are listed in the test and in STYLE_GUIDE 5.5. A runtime check was chosen
  over a pure source scan: most of the misses are drawn motions (a clock and an entry's
  seconds, no tween), which a scan for tweens does not see.
  Fixed here (this agent's files): the jack's reveal (`jack_arrive`), its dissolve wave
  (`jack_dissolve`: off, no wave), its scanlines' roll (`jack_scanlines`: off, still), the
  reduced jack's switch (asked through the kit), the screen flash on its default numbers
  (`screen_flash`), the drop's settle, stamp fade and shredder feed.
  **Found in other agents' files this round** (the test's `AWAITING_FIX`, which only shrinks:
  once a view asks, the test says to remove its id): fix agent A: `card_stamp`
  (combat_fx_layer; fixed by A's batch and taken off the list at the merge), `dead_wheel_fade` and `hp_lag` (wheel_view), `heal_number`,
  `hit_absorb` and `number_float` (combat_scene); fix agent C: `asset_drop_grow`,
  `route_crawl`, `route_target_pulse`, `select_ring_pulse` (city_map_overlay),
  `beacon_blink`, `city_sign_pick` (neon_city), `decoy_fire`, `home_lag`, `ice_lock_ring`,
  `node_damage_number`, `raid_flip`, `raid_hit_effect`, `raid_move`,
  `raid_outcome_stagger`, `raid_result_banner`, `turret_trace` (raid_fx_layer /
  raid_beats). Tests: `test_every_lab_demo_exercises_its_own_entry` (the switch check),
  `test_the_switch_check_names_a_view_that_never_asks`,
  `test_a_view_asks_whether_its_motion_plays_through_the_kit`,
  `test_fx_pieces_honour_their_switch`.
- **D4 the runner survives a broken results file.** `parse_junit` raised on an empty or
  cut-short `results.xml` (it happened under a full disk) and the uncaught error lost
  every shard's results. `read_results` never raises: a missing, empty or unparseable file
  is that shard's problem (with the free space left), the other shards count, and its
  scripts join the scripts that did not run in the alone-rerun (which now runs failing and
  not-run scripts). A free-disk check runs before the shards start: under 1 GB
  (`--min-free-gb`) the run stops with a clear message (exit 2), under 5 GB
  (`--warn-free-gb`) it warns. Tested by `tools/test_run_tests.py` (Python `unittest`: the
  runner is Python, so its tests are too; TEST_SUITE documents it), which
  `test_the_runners_own_tests_pass` runs inside the suite.
- **D5 where a schema check goes.** CLAUDE.md rule 8 and ANIMATION_HANDOFF said to update
  `tools/schema_smoke_test.gd` for a schema change; since ANIM-R5 P17 that file is a runner
  that must gain no checks (they live in `tools/schema_smoke_checks.gd`). Both now name the
  checks file (in CLAUDE.md only that reference changed). This batch's `scripts/data/`
  change is four ids in `REQUIRED_IDS` and `ALWAYS_ON` (D2), no field; the smoke checks
  already cover both lists. Test: `test_the_docs_send_a_schema_check_to_the_checks_file`.
- **D6 stale words.** The ANIM-R5 rules entry (R2) said the raid panel "still ends only its
  own step": a bracketed note now points to ANIM-R5 city P11 and D1 above (the entry itself
  is history). MotionSkip's helper list names RaidPlayoutPanel (D1). STYLE_GUIDE 5.2 said a
  won fight swaps SEND IT for LOOT / CONTINUE "at once"; since ANIM-R5 it swaps as the
  outcome lands (the replay's end beat, after every HP roll; a press lands it at once). The
  wording names no replay length, so fix agent A's retune of the replay (A7) leaves it true.
  Test: `test_the_docs_say_what_the_motion_does_now`.
- **D7 short motions join the one press.** The MODEM sign's warm-up, the top bar's bumps,
  rolls and landing pulses, SEND IT's drips, halo and squash, a card dealing or fanning in,
  and a wheel's spin after a card (outside the replay) joined no MotionSkip group: a press
  that ended a page entrance or a flight left them playing. Registering them as full
  helpers was rejected: each would take presses on its own, and a key pressed while a tag
  bumps would be consumed for a flourish of a fraction of a second (worse for the player).
  They join passively (`MotionSkip.register_passive`: `motion_running` /
  `complete_motion`, no `_input`): they complete with any press another helper takes, and
  a press when only they play passes on untouched. The WheelView completes only when still
  busy, so the replay's own skip (which stops its wheels first) is never redone
  (`wheel_view.gd` is fix agent A's file: registration and the two methods). Every other
  script that animates is listed with why a press does not complete it (hover and focus
  states, answers to the press itself, ambient loops, reading moments, pieces a registered
  helper ends, the jack) in STYLE_GUIDE 5.5 and the test's `NOT_SKIPPABLE`. Tests:
  `test_every_script_that_animates_registers_or_says_why_not` (a script that animates and
  joins no group fails unless listed; a listed script that registers or stops animating
  fails too; the guide names each),
  `test_a_short_motion_completes_with_a_press_another_helper_takes_and_takes_none_itself`.
- **D9 Settings as found, and frame counts under live motion.** `test_horizontal_pass20`
  left `tutorial_done` on; `pad_active` is not in `Settings.to_dict` (it is session state,
  not saved: kept out of the file on purpose), so tests restoring through
  `to_dict` / `from_dict` missed it. `Settings.snapshot()` (to_dict plus `pad_active`) and
  `Settings.restore()` (the InputMap's keys too) give tests one call for every field
  (a test fails when a new field is missing from the snapshot), and the suite guard
  (`tests/helpers/suite_guard.gd`, GUT's pre- and post-run hook, in `.gutconfig.json` and on
  every runner shard) compares a snapshot per test script: a change left behind is named
  (`SETTINGS LEAK`), put back, and fails the run. Its first full run found two more:
  `test_horizontal_pass16` and `test_polish` rebound a key back to its old key, which leaves
  it saved as a keybind; both restore their snapshot now. The fixed-wait rule now also
  flags a frame-count wait whose next statement asserts on live motion's progress
  (`frame_waits`, see TEST_SUITE); four sites: two now wait frozen frames, one frozen
  frame, one is marked (the bounded wait above it saw the entrance end). The manifest's
  times were refreshed from a green run (`--update-times`; the ANIM-R5 city and netrun
  scripts had placeholder times). Tests: `test_a_settings_snapshot_covers_every_field_and_restores_it`,
  `test_the_suite_guard_is_wired_into_every_run`,
  `test_no_frame_count_wait_gates_a_motion_assertion`,
  `test_the_suite_guards_findings_are_read_from_the_log` (tools/test_run_tests.py).
- **D10 no leaks at exit.** The exit leaks of a passing run (shard 1: 213 ObjectDB
  instances, 31 dummy textures, 68 shaped texts, 3 CanvasItems, 2 resources; shard 3: 19
  instances) were two orphaned node trees a test built and never freed: a reference
  ZineNote in `test_pad_reachability` (with its RichTextLabel, scroll bar and timer) and a
  tooltip body from `UiTip.make` in `test_horizontal_pass20_screens`; both are freed now
  and no shard prints a leak at exit. GUT's per-test orphan counts after
  `test_settings_extras` (74) and `test_horizontal_pass17` (22) were SettingsPanel's
  section swap: it took the old section's labels out of the tree and queued them, so they
  were orphans until the frame ended; now they are hidden and queued in place (no orphan at
  any time). The suite guard fails a run that leaves any node outside the tree at its end
  (`ORPHAN LEFT`); it found none after these fixes.
- **D8 one cap, one arrival, a flash that minds the setting.** Dialogue copied Typing's
  typing cap by hand: `Typing.seconds_for(chars, id)` is the one (seconds per character,
  at most the entry's amplitude, both at the speed), used by both. `beat_timing` counted
  the hit number's travel (`number_to_hp`) in "arrive" only while it plays, but always in
  "settle" and in the death's lead: `number_arrive()` is the one answer (0 when it does not
  play) for all three (fix agent A's `combat_scene.gd`: the three reads and the new
  static). `Fx.flash` had no reduce-effects check (its callers gate on their own entry, but
  the default flash did not): it never flashes under reduce effects, and on
  `screen_flash`'s numbers not when that entry is off (D3). Tests:
  `test_the_subtitle_types_under_typings_one_cap`,
  `test_a_number_that_does_not_travel_takes_no_time_anywhere`,
  `test_fx_pieces_honour_their_switch`.
- **D11 the system log speaks the player's language.** The log strip at the foot of the
  HQ and the run is an Options switch, so a player can read it: it is not dev-only. Its
  words ("New campaign", the seed line, "Resumed.", "Nothing to resume.", "No living
  operative or open Site: go to HQ.", "Saved.") go through `tr` now (the bbcode stays
  outside the key); strings.csv re-exported (fix agents B's and C's scene files: the
  log lines only). The lines the rules write into it (a raid's event text, a refused
  launch's reason) are the rules' English, as the toasts that show the same text are; the
  coordinator has this as a finding for the screens that show them. Test:
  `test_the_system_log_translates_its_words` (no English literal outside `tr` in a log
  line; the keys are in strings.csv).
- **After merging the netrun batch (B7):** HudBar's landing pops on DAEMONS and VIEW LOADOUT
  join the one press passively too (`Motion.held` / `Motion.settle`, new kit calls for a
  helper's tween on a property), and `MotionDemo.after_frames` (the coordinator's leftover)
  waits with one-shot connections (a `Waiter` per call, checking its node each frame and
  freeing itself), never an `await` that resumed on a scene freed meanwhile. Test:
  `test_a_demo_step_waits_its_frames_and_never_runs_on_a_freed_node`.
- **The guard watches the run's clocks too; one load flake fixed.** A full run failed
  `test_anim_r3_city`'s CONNECTING hold in its shard only (0.16 s measured, 0.35 wanted),
  passing alone. The guard now also compares `Engine.time_scale`, `Motion.speed` and
  `Motion.force_live` per script (a frozen frame or a 2x left behind would slow or speed
  every later motion): the next full run found no leak of any, so the cause was the test's
  measure: it timed the line from when it first saw it, and a slow frame before that under
  a loaded shard ate the hold. Fx now measures the line itself (`last_connect_shown`, wall
  time from showing to going) and the test reads that (fix agent C's test file: that
  assertion only).
- **The lab-demo check under load.** After the combat merge, `combat_end_hold`'s new netrun
  demo (fight_won: a netrun, its city's settle frames, a whole SEND IT) missed its read in
  2 of 3 full runs (passing alone once): its wait counted game time only, and a loaded
  shard's slow frames used the 12 s up before the lab's frame-counted context settle
  (`CONTEXT_SETTLE` + `CONTEXT_BAKE_FRAMES`) had run. The wait now also allows those frames
  plus 240 (`DEMO_EXTRA_FRAMES`); it still returns as soon as the entry is read.
- **After merging the city batch.** The switch check's `AWAITING_FIX` lost the ten entries fix
  agent C's raid layer and route now ask about (`decoy_fire`, `home_lag`, `ice_lock_ring`,
  `node_damage_number`, `raid_flip`, `raid_hit_effect`, `raid_move`, `raid_result_banner`,
  `route_crawl`, `turret_trace`); C's new `raid_threat_withdraw` is asked through the raid
  layer's own `beat_u` (a demo never reaches a withdrawal; the banner's ask came too late in
  one run of three): the check now also reads a view's own asking functions (`func f(id:
  StringName` whose body asks the kit, or another such function, about `id`, called with the
  id or a const naming it). Still awaiting after all three merges: fix agent
  A's `dead_wheel_fade`, `heal_number`, `hit_absorb`, `hp_lag`, `number_float` and fix agent
  C's `asset_drop_grow`, `beacon_blink`, `city_sign_pick`, `raid_outcome_stagger`,
  `route_target_pulse`, `select_ring_pulse` (the coordinator has the list). The Heat poster and
  the HQ's raid numbers joined the one press in C's batch, so the not-skippable list lost
  them; `raid_step_gap` is a part since C's batch, no longer a hold. C's new
  `test_anim_r6_city` asserted a roll still running after a plain frame (now a frozen frame),
  and A's new `test_anim_r6_combat` left `tutorial_done` on (it restores a snapshot now):
  both caught by the rules above.

#### 2026-09-29 — Animation pass — ANIM-R6 city, raid, HQ and bake
The sixth fix batch of the Animation pass review, city, raid, HQ and bake part (C1-C16, from the
R6 vertical, horizontal and naive-player audits). Views, tools and docs; content: the three
MAJOR Heat thresholds' `event_text` reworded (rules unchanged); `scripts/data/`: three table ids
(REQUIRED_IDS), `raid_step_gap` and `raid_shot_stagger` in OFF_PARTS, `heat_pulse_rise` in
ALWAYS_ON (consts only, no schema field; the smoke checks read the lists). Every call below was
the implementer's (nothing deferred). Tests: `tests/unit/test_anim_r6_city.gd` (full tier);
expectation changes in `test_anim_r4_city` (RAIDS holds through the raid's end line) and
`test_anim_r5_city` (the Heat note shows under reduce effects). Windowed captures through
`tools/run_windowed.py` (1280x720, no ERROR in any log): the HQ playout, the Heat crossing at
1.0 and 1.6, the raid setup at 1.0 and 1.6, the campaign end won / lost, the Grid's claim, the
route; page timings with `tools/design_lab/page_bake_probe.gd` (three runs).
- **C1 the Heat poster is a MotionSkip helper.** Its rise is a chain of one-shot steps (it was
  an await loop), the crossings still to play are known (`_rise_ups`, `_chain_rest`), and a
  press completes the roll, the crossings (the last one's banner stamped), the pops, the shake,
  the band stamp and the banner's fade. **Picked: the reading hold survives a press** (the
  item's alternative, with the note readable): the banner and its consequence note hold
  `heat_banner`'s delay whatever is pressed (a reading time like RAID INCOMING's), and the hold is
  not `motion_running`, so a press during it passes. STYLE_GUIDE 5.1 and MotionSkip's notes say
  so. In the raid feed a press that drives the playout (2x) is spared by D's `motion_passes`
  (ANIM-R6 D1) once it is on main.
- **C2** the raid's home-hit "-N" is a FlightFx flight (`fly_node` with `on_land`): it leaves the
  node at `home_number_fly`'s amplitude and shrinks into HOME; a press lands it and HOME drops
  then; the page's end lands any still flying.
- **C3** NeonCity holds the texture it draws (`drawn_texture`) until it draws another, so an
  LRU or byte-budget eviction never frees a kept bake viewport under the canvas.
- **C4 switched-off entries on views with their own clock.** RaidFxLayer reads `Motion.live` per
  beat (`motion_len` / `beat_u`): off (or under reduce effects and headless, where the playout is
  instant anyway), a beat keeps its time and shows its end state from its start (node_pop,
  raid_move, decoy_fire, ice_lock_ring, raid_hit_effect, turret_trace, node_damage_number,
  raid_flip, raid_result_banner, home_lag, influence_spread / influence_crossfade on the tints).
  `route_crawl` off: dashes and chevrons stand, no packet. `raid_step_gap` and the new
  `raid_shot_stagger` are OFF_PARTS (RaidBeats.raw_seconds gives 0 for a switched-off part).
  Inline numbers moved: SHOT_STAGGER 0.5 -> `raid_shot_stagger` (amplitude, a share),
  HEAT_PULSE_RISE 0.3 -> `heat_pulse_rise` (ALWAYS_ON: a tuning of heat_pulse), a mark's
  `mark_t * 2.0` -> `stamp_fade_in`'s share (0.5, as the raid's stamps), the raid number's
  0.66 hold -> NUMBER_HOLD_SHARE (a documented drawing constant). Lab demos for the new ids.
  (D owns ui_motion_data.gd: the three ids and the two lists were added minimally.)
- **C5** the Heat banner and its note show static for the hold under reduce effects (they never
  showed). The note keeps off every usable button and every word (Labels, rich text, the top
  bar's drawn tags, the pad prompts, the subtitles): spots below / above / right / left of the
  poster, each slid on in NOTE_SLIDE steps, at the full width, then 0.8 and 0.65 of it; the
  least covered one when none is free. At 1.0 and 1.6 it stands under PIRATE RADIO's words,
  covering none (at 1.6 a first try went up over the CREW tag: the drawn top bar is now
  avoided). The consequence reads "A raid is queued. While Heat stays at 25 or more, elites
  are more frequent." ("The corporation raids the Cell" read as a raid happening now); the
  first sentence is short so the longest (16 words) still reads in the 3.6 s hold.
- **C6** a Polaroid caption at `CAPTION_FONT` x the text size, never under `CAPTION_MIN` 12 x the
  text size (it went to 8 px), wrapped over as many lines as it needs (never cut), and the
  Polaroid is never narrower than its caption's longest word at that floor
  (`_get_minimum_size`): the dossier's compact 60 px Polaroid at 1.6 grows to fit "Breaker"
  rather than breaking it between letters.
- **C7** `CityMapOverlay.tr_word` literals are exported (TextDb.CODE_CALLS): WIN, EXPLOIT, NO
  GAIN, RAID, MAP KEY and its tip, T%d, difficulty %d of %d, the Clearing it ... tooltips, off,
  Heat %s. No `%+d` inside a translated format (TextDb.signed). The maps' pad prompt "Key" is a
  marked constant.
- **C8** YOUR NODES: the window's body takes its height (the list scrolled in a strip over empty
  window). ScrollHint's snap is keyed by its content's height too (it ran out of passes on the
  first layout; bounded by SNAP_PASSES_MAX in all), a skipped pass runs on the next frame, a
  flow's lines count as rows (the Withdraw buttons), a row's share is of the view with no snap,
  and a view held at its least height gives the snap's room out of that height (at 1.6 the
  list could not shrink, so the row stayed cut). ScrollHint is kit (D): changed minimally.
- **C9 measured** (`page_bake_probe.gd`, three runs; before: the audit's 1.9 s and R5's
  1.72-1.84 s): the HQ that New campaign opens is covered on its first frame (163-173 ms, the
  page's build) — the start page warms it with a hidden backdrop twin pinned to a new
  campaign's territory (`warm_start_hq`, re-asked when another corporation is picked, behind
  the start page's own city); the Grid's first open in that campaign is covered on its first
  frame (93-97 ms), and after a run 101-104 ms — the HQ page prebakes the Grid's mount frame and
  every node (`first_grid_region`), behind the HQ page's own city and only while the HQ page
  shows (a page left at once, the demo's campaign end, waited on the silhouette behind it).
  Unchanged: the claim's tint 1.62-1.74 s after its stamp, the start page itself 1.5-2.4 s on a
  cold start.
- **C10** a finished playout disables 1x / 2x / 4x and Skip and lights 1x (the speed buttons
  are toggles showing the speed playing); Continue takes the focus. The playout mounts on CORE
  and the entries (`playout_frame_points`), its first step starts on the panel's first frame
  (`play(..., start_now = false)`, once the page is laid out) and frames CORE and the entries
  with its fight, so no first frame clips CORE.
- **C11** at the verdict every threat still on the map is struck out (a red X) and withdraws
  (`raid_threat_withdraw`); a threat that hit CORE keeps its name on the map until then (it was
  named at its first step only). HOME -5 · HOLDS: the damage pink, HOLDS acid. **RAIDS drops
  with the verdict**, its tag pulsing (`land_pulse`), not with the "Raid over" line mid-feed
  (it read as a raid lost); the tag's word is unchanged.
- **C12** a claim cross-stamps: the change before's stamps (`fading_marks`) stay and fade as the
  new ones land. A map over the city draws the marks itself, so the city's own layer draws none
  (the "two CLEARED stamps" at 1.6: the city layer's, placed before the map's labels, and the
  map's). The green blob over the LOST end page was not reproduced (captured won and lost via
  the new flag: the only green is the claimed district's lasting tint, fixed in place).
- **C13** the HQ is a MotionSkip helper for the page's pops (`popping()`: any piece with a
  `Motion.pop` running: the verdict stamps' landings, the SITES bump, a crew card's pop as a
  drop lands). Kit-wide pops (ModemSign, HudStats, drips) are D's.
- **C14** `Fx.note_hold()` reads through the kit (`Motion.seconds`); `connect_hold()` takes each
  reading time by its own switch (switching `jack_connect` off skipped RAID INCOMING's hold).
  The lab's stamp says what the game says ("RAID INCOMING" over the corporation).
- **C15** an empty RUN ASSETS: / ARMORY: row says "none"; CLAIMABLE is CAN BE YOUR NODE (its tip
  says a claimed Site becomes a node raids come for); the WON stamp wears the win's star; the HQ
  page snaps its rows (the crew's Loadout was cut under MORE BELOW at 1.6; the other pages keep
  their own: the raid setup's card row is taller than any snap keeps whole); YOU ARE HERE
  stands on the street, joined by dashed roads to the choices ahead. The Solace subtitle cut
  ("Collecto") is the subtitle typing mid-line in the audit's frame; the page is whole once
  typed (Dialogue, not changed). "Unable to create shader cache" is disk-only (ignored).
- **C16** `--demo-campaign-end=won|lost` shows the campaign's end on a demo campaign in its own
  slot; the HQ's demos wait by one-shot connections (`_demo_wait`: a freed HQ drops them, no
  await resumes on it) and write state only through DemoSetup (roster, Schematics, Armory,
  Heat, the campaign's end; B's `set_rank`).
- **Words** (exported once): the tr_word literals above, Key, none, CAN BE YOUR NODE and its
  tip; dropped: CLAIMABLE, "Once cleared you can claim it: a node of your network.".

#### 2026-09-29 — Animation pass — ANIM-R6 combat
The sixth fix batch of the Animation pass review, combat part (A1-A19 of fix agent A, from the
R6 vertical, horizontal and naive-player audits). Views only: no rule changed (the numbers the
tags show come from the resolve's own events; preview = result). One new motion id (data):
`tutorial_next_pulse`. Every call below was the implementer's (the standing rule: nothing
deferred). Tests: `tests/unit/test_anim_r6_combat.gd` (full tier); new helper
`tests/helpers/pseudo_loc.gd`. Checked in windowed Movie Maker captures (`netrun_scene
--demo-combat --demo-end=lose|win|hover`, at 1.0 and 1.6; the lab's `wheel_nudge`), logs free of
ERRORs.
- **A1 one press, one job.** A press during a fight-ending replay landed the outcome (showing the
  next step) and then went on to it: the SEND IT key or a click on its spot also left the fight.
  The replay's press handling (`replay_press`) now notes whether the next step was on screen
  *before* the press; only then does it pass to it. Tested with a key and a click.
- **A2 a skip keeps the bark and the stamp whole.** The VICTORY / DEFEAT bark is said where the
  outcome lands (`_land_outcome`, once per turn), so a skipped end beat still barks; a skip lands
  the DEFEAT stamp whole (`WheelView.show_flatline`: no fresh 0.3 s pop after the press). Barks
  follow `Motion.animating()` (the same as before in the game; forced motion in tests hears them).
- **A3 a turn-start kill.** `outcome_time` counts the end beat in any phase and waits for every
  HP roll before it (a fight ended by an ON_TURN_START trigger landed its outcome at 0 s);
  `beat_delay` never gives a negative delay.
- **A4 every number is the applied one (presentation only).** Hit chips say who hits whom and
  what gets through the guard ("HITS YOU 8"; the victim's "N BLOCKED" says the rest); a hit on a
  wheel with fewer HP left says so honestly ("HITS YOU 8 → 1 LEFT", the same "→ N LEFT" in the
  equation where it struck and in the icon row). A wheel's own loss is never summed again on its
  own tag ("YOU TAKE 11" beside "HITS YOU 8"): the NEXT plate carries the total ("NEXT 49 (-11)",
  shrinking rather than running onto the HP number). Losses no hit names say their source
  ("☠ CORRUPTED BITES YOU 3"), heals are "+N HP", anything else (a boss refill) "HP +N". No
  fractions: the riding number is the whole hit ("12" shrinking into "6" at half power; the "6 ½"
  mark is gone). The icon row with no guard is one "-N HP" ("↓8 = 8" beside LAST TURN -1 HP).
  **Decided:** "→ N LEFT" for the clamp (the designer's "8 → 1 left"), and a fully blocked hit's
  chip says "HITS YOU 0" (applied) beside the victim's "N BLOCKED". Tested over 4 seeds x 3
  enemies x every hand card, the End Turn forecast and a lethal turn: each hit chip's numbers
  equal the events' applied damage, and the NEXT plate the resolved HP.
- **A5 the top bar's HP in a fight** (netrun_scene.gd, agent B's file, a minimal change): during a
  fight it reads the fight's HP (`combat_scene.top_bar_hp`; the run's is written at the end),
  keeping the turn's start HP while a replay plays and moving when it lands
  (`shown_hp_changed`), still held for the outcome beat.
- **A6 a lost fight waits for JACK OUT** (netrun_scene.gd, a minimal change): no auto-advance after
  DEFEAT (JACK OUT showed ~0.7 s). A win still moves on after `combat_end_hold`.
- **A7 the replay's pace.** Measured headless from the schedule (first turns of 15 fights; third
  turns): before, first turns 1.8-5.2 s (median 3.2), third turns 2.2-5.9 s (median 3.9). Retuned
  toward the documented feel where readability holds (the projectile's 0.27 s flight and one hit
  at a time kept): landing hold 0.3→0.25, number to HP delay 0.22→0.12 and travel 0.22→0.18, HP
  drain 0.3→0.2, side gap 0.35→0.2, result hold 0.5→0.35, absorb 0.3→0.25, turn spins 0.4→0.34,
  enemy spin delay 0.15→0.05. After: first turns 1.6-4.2 s (median 2.7), third turns 2.1-4.7 s
  (median 3.3), a plain turn (one hit each way) 2.3 s (tested ≤ 2.6). **Decided:** retune and
  write the measured numbers in STYLE_GUIDE 5.2 ("about 2 s" can't hold with one projectile at a
  time and each number entering its HP, rules the designer asked for in R2-R4; each further hit
  adds ~0.6 s).
- **A8** The portrait's glitch and HP tooltip follow the replay's HP (they read the end at SEND
  IT); the nudge arrows stay until the outcome lands.
- **A9** A fight left while its outcome waits lands it on the way out (`outcome_landed`: the
  flatline's DISPATCH line was dropped).
- **A10** The log playback's timers call a bound method (`_append_log`), no lambda holding the scene.
- **A11** Switched-off `card_stamp`, `card_exhaust` and `effect_burst` don't play and take no
  time; the card flight's grow share and eases are named drawing constants.
- **A12** Settings, RESPIN / UNDO from their first frame and the hidden notes' titles translate once.
- **A13** A hovered card names itself on the tag's tape with a card mark ("YOUR JOLT · WAS ..."),
  not as a chip among the enemy's results; the WAS words are bigger (13 px at 1.0) and firmer
  (ink 0.85, a thin lighter strike). **Decided:** a nudge hover says "YOUR NUDGE" the same way.
- **A14** The arena's city never switches in mid-replay: `NeonCity.hold_landing` (agent C's file,
  a minimal change) keeps the silhouette while a SEND IT replays; the bake lands and fades in
  between turns. **Decided** over prebaking the fight's look (the arena's look differs from the
  route's and the bake still raced the first turn).
- **A15** VICTORY stays at full strength until the fight is left (`CombatFxLayer.hold_word`; it
  faded to a ghost after ~1 s), a skip shows it too, and `combat_end_hold` is 1.4 s (was 0.8) so it
  reads before the loot opens. The lab's `combat_end_hold` demo is a won fight in the netrun
  (the scene no longer reads it).
- **A16** The tutorial box is sized to its step's text (the subtitle dock gives up lines for it);
  a step longer than the column shows in pages "(1/2)" that fit, never cut; Next pulses
  (`tutorial_next_pulse`, new) when it is what moves the tutorial on; the steps no play ends (the
  wheel, resistance, Heat) move on with the next turn.
- **A17** The nudge arrows turn down the wheel's sides (5° steps, at most 70°) while the tag
  would cover them (1.6); the inner ring's arrows carry a ring mark instead of "IN"; SEND IT's
  mark is a play button (a disc with a ▶) instead of the small ▶▶; the deck pile a card deals from
  sits far enough in that the first card starts whole on screen.
- **A18** `PseudoLoc` (test helper) turns pseudolocalisation on and puts the project's own values
  back (r2 / r4 / r5 set them to false); the empty assert in r5's Perfect test is a real check;
  the lab's `send_lose` turns the enemy's wheel until SEND IT loses when no fight tried does.
- **A19** `wheel_nudge` 0.16 s (was 0.08, too fast to see) with a 3 px recoil; a queue still
  catches up in the time of one step.
- Test expectations changed on purpose: r3's half mark (a whole number now), pass23's
  "YOU TAKE" (the enemy's tag says HITS YOU), pass20's HP chip (the NEXT plate), pass24's
  YOU PLAY chip and the r2 / r3 key checks (YOUR %s), r2's VICTORY word (the held word), the
  tutorial integration test (Next turns pages first).

#### 2026-09-29 — Animation pass — ANIM-R6 netrun screens
The sixth fix batch of the Animation pass review, netrun screens part (B1-B14, from the R6
vertical, horizontal and naive-player audits). Views only (no rule, no schema field, no new
motion id). Every call below was the implementer's (the standing rule: nothing deferred).
Tests: `tests/unit/test_anim_r6_netrun.gd` (full tier). Checked in windowed Movie Maker
captures (no ERROR in the logs).
- **B1 the loot's deal.** The fan-in (~0.42 s for three stickers) outlasted the page's
  entrance, and nothing took a press after the entrance: the deal is now a motion of the netrun
  screen on MotionSkip (`motion_running` / `complete_motion` land every sticker), and while it
  plays its row is kept (`motion_keeps`): a press on a sticker still fanning in lands the deal
  and picks nothing. A sticker invisible in its delay ignores the mouse until it shows
  (`ZineCard.fan_in`): an invisible offer could be picked.
- **B2 views never write game state.** The dev flags (`--demo-shop`, `--demo-daemons`,
  `--demo-loot`, `--demo-event`, `--demo-class`, `--demo-interlude`, `--demo-end`, the drag
  demos' Cycles, the combat end demo's HP) set the run, the campaign or the fight up through
  `DemoSetup` (`scripts/core/demo_setup.gd`, pure; the session's own steps where there is
  one); the netrun view calls it and writes nothing itself. A test scans `netrun_scene.gd`
  for state writes. `hq_scene.gd`'s loadout demo (`op.rank = 3`) calls `DemoSetup.set_rank`
  (one line in the city/HQ agent's file). **Left to that agent:** `hq_scene.gd`'s other dev
  flag writes (`--demo-classes` roster, `c.schematics = 100`, the Heat pulse demo's
  `c.heat = 20 / 30`) can move to DemoSetup the same way.
- **B3 frame waits.** `_frame_raid_map` and the combat end demo wait on one-shot connections to
  the scene's own methods (`_frame_raid_map_now`, `_when_ready`, `_after_frames_here`): freed
  mid-wait, the connection goes with the scene (no await resumes on it); out of the tree, the
  step stops. Tested: freeing the scene mid-wait logs no error.
- **B4 the flatline's run end.** It opened on the silhouette: a flatline adds Heat (the city's
  corporate creep, a new look when it crosses a step) and a fight can be a session's first page
  (a resumed run, the captures), with nothing of the city baked. Now the city's view with no
  route on it bakes behind the fight when it begins, and again under the new Heat when a SEND
  IT ends the run (the rules ran; the replay, DEFEAT and the hold still to play;
  `prebake_run_end`: the camera brought up to date first, hidden behind the fight the city's
  last camera was the route's). And a city that was hidden no longer fades a bake in over the
  sky it showed before it hid (`NeonCity`, one line in the city agent's file: the bake was
  ready, yet faded in over the silhouette for 20 frames). **Measured** (windowed Movie Maker,
  `--demo-combat --demo-end=lose`, the page switch on frame 115): before, frames 116-136 the
  silhouette fading to the city (brightness 8 -> 52); after, the city whole on the page's
  first frame. `page_bake_probe.gd` has the flatline path ("run end (flatline)": the next fight
  lost for real through the combat end demo): covered on its first frame (1 frame, 15 ms); in
  its flow the flatline's Heat stayed within the route's look step (it says so).
- **B5 the run end agrees with its verdict.** The top bar's title follows the stamp:
  NETRUN // FLATLINED, NETRUN // JACK OUT, NETRUN // HOME FELL (it said JACK OUT beside
  FLATLINED). The operative's barks are scoped to the fight (`CombatScene.BARK_SCOPE`, one line
  in the combat agent's file): the defeat bark shows in the fight and ends with it, so the run
  end's DISPATCH line ("Operative lost") is the last word, not the dead operative repeating
  the fight's line after it.
- **B6** the route's kept bake (`CityBakeCache.keep(ROUTE_KEEP)`) is let go at the run's end and
  when the scene leaves the tree (it pinned up to ~48 MB for the session).
- **B7** a toast holds `toast_note_hold` at the motion speed when that is slower, never shorter
  than its raw duration (a reading time: a raid at 4x or reduce effects never cut it; a slowed
  capture holds it as long as every other motion). **Decided** over "always at speed": the
  words must stay readable at any speed. `flight_land_pulse` waits its entry's delay. The
  landing's pops on DAEMONS and VIEW LOADOUT moved into `HudBar.land_pulse` (the netrun calls
  it); the motion lab's `flight_land_pulse` demo plays it on a real HudBar (CARDS pulses,
  DAEMONS and VIEW LOADOUT pop).
- **B8** the loot's socket list says "Chips go into:" as the Modem's does, with its own tip
  (dropped: "Socket into slot:").
- **B9** `netrun_scene --demo-combat --demo-end=win|lose` plays the fight's ending in context
  (the run end check took it first and showed FLATLINED): `run_end_demo(args)`.
- **B10** the loot window names what paid out, by the node the run stands on: FIGHT WON, ELITE
  DOWN, RACK BREACHED, EVENT PAYOUT (PAYOUT with no node); it said RACK BREACHED after every
  fight. RAM on a card's pictograms carries a RAM icon (a memory chip, new `StatIcon.RAM`)
  before its words ("RAM+3").
- **B11** the Modem under a language the player can't read: a neon shop bag heads the sign (the
  letters step down to make room), its BUY note wears a cart and its SHRED note a shredder (new
  `StatIcon.CART`, `StatIcon.SHRED`). LEAVE THE MODEM already had its exit glyph beside it.
- **B12 the event.** The subtitle bar no longer says the event's story (it repeated the paper
  word for word); the line still reaches the history and voice-over (`Dialogue.log_line`).
  **Decided:** the events have no operative line of their own (no content), so the bar is left
  to the lines that are not on the page. The chosen outcome stamps on the event page, which
  stays inert until the stamp has played (`event_choice_stamp`, 0.6 s; a press ends it), then
  the next page shows: the "no change" outcome popped over the route menu's option [2].
- **B13 the jack.** CONNECTING TO stays a small teal line; the destination has a line of its
  own under it, large (44 px x the text size, stepping down to fit) and bright (paper), with
  the Site's tier icon as the City Grid draws it (`JackSiteIcon`: the T hexagon and its pips;
  `RunManager.jack_tier`).
- **B14** a twin route choice says "(same road as choice 1)" (it said "(same as 1)", which
  puzzled a beginner), on its button and its map label, and its tip explains it (same kind,
  Heat and road ahead; the enemy is picked on entry).
- Words (exported once): the loot sources, the loot socket tip, the run end titles, the twin
  words and tip, CONNECTING TO; dropped: "RACK BREACHED // LOOT: pick a %s", "Socket into
  slot:", "The spinner slot the Firmware chip goes into.", "(same as %d)", "CONNECTING TO %s".
- Expectations changed on purpose: `test_anim_r5_netrun` (the event's band is checked with a
  line said on the event screen), `test_horizontal_pass23_screens` (the event's story is in
  the history, not the bar), `test_anim_r2_city` (the twin words; the jack's words read
  through `Fx.connect_words`).

#### 2026-09-28 — Animation pass — ANIM-R5 city, raid, HQ and bake
The fifth fix batch of the Animation pass review, city, raid, HQ and bake part (P1-P18; P18 is
the coordinator's lookup leak and Disabled-then-Seized ruling). Views only, save RunManager's
lookup reset (P18, an autoload, no rule) and no schema field. Every call below was the
implementer's (nothing deferred). Tests: `tests/unit/test_anim_r5_city.gd` (full tier), the
real renderer's bake in `tools/design_lab/bake_smoke.gd` (docs/TEST_SUITE.md), page timings in
`tools/design_lab/page_bake_probe.gd`. Measured on this machine (1280x720, RX 6700 XT, Vulkan
Forward+), other agents' runs sharing it.
- **P1 the bake draws.** ANIM-R4 H10 wrapped the kept bake viewport's render target in a
  Texture2DRD; Godot refuses one over a viewport's shared texture ("Please create the texture
  object using the original texture"), so every kept bake drew nothing (the hotfix d89ddc2 went
  back to the copy). Now `BakedTexture` (a Texture2D) draws the kept viewport through its
  ViewportTexture (`_get_rid`), owns the viewport (freed with the last reference: the cache's
  entry or a spread's old image, so nothing draws a freed target), or owns a GPU copy (the
  fallback: `keep_viewports` off). `CityBakeCache.usable` checks a picture (valid RID,
  non-empty, its viewport or copy alive); an unusable one marks the entry `failed` and the view
  shows the silhouette (it used to fall back to the seconds-long procedural build on the main
  thread) and never asks again. The "Parameter t is null at baked_texture.gd:16" and the RID
  leaks came from the Texture2DRD path and are gone (windowed runs: no ERROR; the only exit
  warning left is 2 audio objects Movie Maker keeps). **Picked the kept viewport** (no texture
  made or filled in the landing frame); measurements below. `bake_smoke.gd` passes on both paths
  (3264x2304 bakes, 545 distinct colours sampled, no error logged, no viewport left after
  shutdown).
- **P1 H10 re-measured with the city drawing** (numbers under "Measurements"; ANIM-R4's
  H10 figures are corrected there).
- **P2 pages open on their city.** Measured (`page_bake_probe.gd`) before any change on the
  copy path by the designer: loot / event ~2 s, fight ~3 s, Modem ~2 s, HQ ~3.5 s, interlude
  playout ~5 s, route after an interlude raid 6.5 s, claim 3.6 s with no feedback. Found: a
  raid's Heat changes the city's look (the corporate creep), so the playout rebaked mid-raid and
  the route after it baked twice; the route's bake fell out of the LRU behind the pages'.
  Changes: the route's bake is kept (`CityBakeCache.keep`, a named slot the LRU skips); a raid
  playout holds the pre-raid creep (netrun `_creep_heat`, HQ `_creep_band`) with its tint until
  the verdict; the interlude bakes its playout's fights and the route ahead (`_prebake_raid_playout`,
  `_prebake_route` via `NeonCity.region_for`), START DEFENSE bakes the route after the raid first
  (post-raid look, `prebake(..., creep)`) then the post-raid fights; the run's end page warms the
  HQ's city with a hidden backdrop twin, a bake that outlives the scene (`request(..., outlive)`:
  the cache's holder waits on it, so the jack out's stale drop keeps it); a claim stamps CLAIMED
  (the marks) at once over the old image and the tint spreads when the new look lands
  (`_mark_early`). Results under "Measurements"; the headless test lands the simulated bakes and
  checks each page is covered on its first frames.
- **P3** the raid's Heat line says why in the verdict's terms: "Heat +5: Collector reached
  CORE: 0 → 5." (threats that hit CORE), "Heat +5: Collector not destroyed: 0 → 5." (still
  standing), never "for the lost raid" beside HOME -5 · HOLDS. Swept over every corporation x
  home x ICE 0 / 20 x three setups.
- **P4** the campaign's end is a see-through page (no GlassPanel): a WON / LOST ForecastStamp
  lands on the table (`forecast_stamp_resolve`), the headline in display lettering with the next
  steps, STORY UNCOVERED (each beat's title over its text), PROFILE as badges and the ICE lines.
  The pause menu is as tall as its lines (`_fit_height`: its glass plus what it holds, up to
  MENU_SIZE and the screen's foot; Options and the Codex grow it), so the city shows round it.
- **P5** the interlude frames CORE and the raid's entries (`raid_frame_points`) in the area
  beside the RAID window, not the whole Grid.
- **P6** home's banner: the stamp_rect spot search (8 spots round home, three rings out, its
  tilted box against every stamp, label, icon, home's bar, threat token, and the map's panels and
  key; the map's visible area); the playout's labels keep off the key too.
- **P7** the network's packets stop at the verdict (`CityMapOverlay.packets`) and on the report.
- **P8** labels keep off the raid's tokens (`token_radius`: obstacles in the label layout), and
  the moving parts (tints, traces, tokens, locks, hits) draw on a layer under the labels
  (`RaidFxUnder`); stamps, numbers and the banner stay over them. The playout's forecast stamp
  turns see-through (0.3) while a raid node sits under it. The report's node row keeps its HP
  beside its name (an HBox; the name wraps). YOUR NODES snaps like the Grid's list (a ScrollHint,
  MORE BELOW). The forecast float says RAID FORECAST over its "45 → 50 ▲". The Grid's gains rows
  open with "IF CLEARED:" and read OPENS 1 SITE / OPENS 2 SITES and CLAIMABLE.
- **P9** the Heat banner's consequence is a flat note beside the poster (mono, never under
  12 px x the text size, 260 px x the text size wide, placed below / above / right / left where
  it covers no button), held `heat_banner`'s delay, **retuned 1.4 → 3.6 s** (the longest
  consequence is 17 words); the banner keeps the band line on the poster, under WANTED.
- **P10** a Polaroid caption shrinks to fit, then takes two lines over a smaller picture (never
  under 60 % of its side); Continue after the interlude's raid lets the fight camera go first
  (`_leave_raid_playout`).
- **P11** the playout asks `MotionSkip.verdict`; the one exception (presses that drive the
  playout: focus moves, 1x / 2x / 4x, Skip) is in STYLE_GUIDE 5.1 and MotionSkip's notes.
- **P12** YOU ARE HERE is a key, translated once in `label_lines`.
- **P13** tests for the preview cache, the music prewarm and reduce effects' end states.
- **P14** a warm pass hashes the campaign once (`_warm_key`; it was once a frame).
- **P15** RAID INCOMING fits the screen (the lettering steps down to 22 px x the text size,
  then wraps).
- **P16** heat_poster's notes name the banner as it reads.
- **P17 the schema smoke test's exit crash.** `tools/schema_smoke_test.gd` printed PASS and then
  crashed at shutdown about one exit in ten (exit 139). Found: an access violation inside the
  engine's GDScript clean-up at shutdown (the .NET runtime's event log gives the same fault
  address every time, in godot.exe's `GDScript::clear`, after every node, autoload and our
  static caches were already freed, so not a thread of ours: freeing each autoload by hand
  first, then quitting, still crashed after the last one). What decides it is the order the
  class scripts were loaded in: the checks, compiled as part of the `-s` script, loaded their
  dozens of data classes as that script's dependencies before any content; the same script
  with its checks left uncalled crashed as often, while a script instancing all 46 classes,
  `tools/validate_content.gd` (content first, 0 of 100) and the game never did. Fix: the tool is
  now a runner that loads the content first (the registry's scan, as validate_content does)
  and only then loads and runs the checks, now in `tools/schema_smoke_checks.gd` (a schema
  change adds its check there; CLAUDE.md's command is unchanged). The Fx exit hygiene (fonts,
  the terminal material, the chevron let go) stays but was not the cause.
- **P18 (coordinator).** a) `RunManager.build_generated` put the built REBEL_CELL (and its
  generated content) into the lookup for good; a test that built it left it to every later
  script (test_anim_r4_city then read raids of the built corporation). The lookup is rebuilt
  from the registry when the campaign is forgotten, a new one starts or one resumes
  (`_restore_lookup`). b) A node Disabled then Seized in one raid is one SEIZED node everywhere:
  the verdict (RaidVerdict counts outcomes), the report (each fallen node once, by outcome; it
  listed both), the feed's tally (by outcome); the feed still tells both lines as they happen
  (the ruling main adopted in c93fac9).
- **Words** (exported once): the Heat lines, IF CLEARED:, OPENS %d SITE(S), CLAIMABLE, RAID
  FORECAST, YOU ARE HERE, the end page's words; dropped: "Heat %s for the lost raid", "CAMPAIGN
  WON/LOST - ...", the one-line profile sentence.
- **Expectation changes:** `test_horizontal_pass24_city` (the gains row opens with its caption),
  `test_anim_r4_city` (a fallen node is named by its outcome).
- **Measurements** (this machine, 1280x720, RX 6700 XT, Vulkan Forward+, other agents' test
  runs sharing it; windowed runs through `tools/run_windowed.py`; no ERROR in any log):
  - **H10 corrected** (ANIM-R4's numbers were taken while every kept bake drew nothing, so the
    city cost nothing to show; min / median / max of 5 runs, `profile_frames.gd --timeline`,
    kept viewports vs `--bake-copy`): the Grid's first open from the HQ page 102 / 106 / 128 ms
    (copy 116 / 131 / 138; R4 said 136-170, median 149), the re-open 67 / 71 / 86 ms (copy
    75 / 87 / 89; R4 said 94-109). The route after a jack at 1.6 (`--demo-grid
    --demo-anim=jack_in`): its bake lands 0-6 frames before the jack's cover lifts (unseen), in
    a frame under 50 ms in 4 runs of 5 (53 ms once; copy: under 50 in 3 of 5, 50-51 twice);
    after the cover lifts no frame over 66 ms (51-66, copy 53-61, single frames the machine's
    load shows before the jack too). R4's "landing frame 54, 56, <50, <50, <50" was measured
    with nothing drawn. The kept viewport is faster on the open and re-open (about 15-25 ms)
    and ties on the landing; it stays the default.
  - **P2 page timings** (`page_bake_probe.gd`, three runs; the designer's copy-path numbers
    before in brackets): event, loot, Modem, fight, the route back after each and the run's
    end page each covered on their first frame (22-66 ms) [loot / event ~2 s, fight ~3 s,
    Modem ~2 s]; the HQ after the run covered on its first frame (the jack out's 1.6-1.7 s
    before it) [~3.5 s black behind the panels]; the interlude's playout 0 frames of 123
    uncovered [the whole raid over the silhouette, ~5 s]; the route after the interlude's raid
    covered on its first frame (55-68 ms) [6.5 s]; a claim stamps CLAIMED at once and the tint
    follows its bake 1.46-1.56 s later [3.6 s with no feedback]. Not changed: the Grid's very
    first open in a campaign (1.72-1.84 s: nothing remembered yet to bake ahead, ANIM-R2 R1),
    the raid interlude's own page (1.45-1.48 s, most of it under the jack's RAID INCOMING hold)
    and the first route of a run (4.7-5.4 s from the press, under the jack). A quick player
    (`--leave=20`, each page left 20 frames after it is covered) sees the event 0.48 s and the
    route after the interlude's raid 1.49 s on their silhouette (the prebakes still running).
  - **P17 proof:** before, 12 crashes in 100 runs, 10 in 70, 5 in 50, 3 in 20 (on the same
    machine the same day); after, 240 consecutive runs of
    `godot --headless --path . -s tools/schema_smoke_test.gd` (4 x 60, run 4 at a time) exit 0,
    every one printing SCHEMA SMOKE TEST: PASS; the runner layout in a scratch copy, 0 in 490.

#### 2026-09-28 — Animation pass — ANIM-R5 motion rules and tests
The fifth fix batch of the Animation pass review, motion rules, test infrastructure and docs
(fix agent D, R1-R8). Every call below was the implementer's (the standing rule: nothing
deferred). Views, tools, tests and docs only; `scripts/data/` gains two consts (below), no
field. Tests: `tests/unit/test_anim_r5_rules.gd` (full tier), `tests/unit/test_motion_lab_demos.gd`
(full tier), `tests/unit/test_suite_compiles.gd` (full tier, split out of the integrity
test); R4 / R1 tests adjusted where they pinned the old behaviour (below).

- **R1 one rule in every helper.** Typing, the Dialogue subtitle and MenuMotion hand-rolled
  the press test and the verdict (`is_press`, `pause_open`, `works_ui`); they now call
  `MotionSkip.handle` like the others. `MenuMotion.works_menu` is `MotionSkip.works_ui`, so
  a click on a menu line trusts the hovered control (a line under a panel isn't clicked)
  and the line's `button_mask` (a right-click works nothing), as `button_at` does. Menus
  lose two looser passes: an accept while focus is on no usable button and a click on a
  disabled line are now consumed (they worked nothing either way). `pause_open(node)` is
  false for a node inside the open PauseMenu (its lines' MenuMotion owns the menu's presses
  with it; MenuMotion's own check moved into MotionSkip as `in_pause_menu`).
- **R2 one press completes every running motion.** A consumed press reached only the first
  helper in `_input` order, so a stray key during a flight and a drop (or a page entrance and
  a flight) ended one of them; a focus move (passed on) ended all. Now defined once in
  MotionSkip: every helper joins `MotionSkip.GROUP` (`register`) and answers
  `motion_running()` / `complete_motion()` (and `motion_keeps()` when it keeps presses);
  `handle` gives one verdict (the keeps of every running helper count: a click on SEND IT
  seen first by a flight is kept, never played blind), then completes every running helper
  (PASS and CONSUME alike), then consumes on CONSUME; `consume` completes them all too, so a
  helper that consumes by hand still does. Helpers a PauseMenu covers are left alone.
  Registered: Typing's skip nodes, Dialogue, MenuMotion, DropLayer, FlightFx, PageTransition,
  the combat replay (keeps SEND IT, RESPIN, UNDO, the hand) and the netrun route move. The
  raid playout panel (fix agent C's file this round) still ends only its own step; its
  one-press fix should register it the same way (a `motion_running` / `complete_motion`
  pair and `MotionSkip.handle`). [Superseded: ANIM-R5 city P11 registered the panel (its
  step ends with every other motion, save a press that drives the playout), and ANIM-R6 D1
  made that exception hold whichever helper sees the press (`motion_passes`).]
  `test_anim_r4_combat` pushed two presses to end a flight and a drop ("one press each");
  it now pushes one.
- **R3 switching an entry off, by kind.** `enabled` was honoured only through
  `Motion.live`; entries a view reads as numbers ignored it. Three kinds, decided in one
  place (`Motion.seconds` / `delay_of` / `amplitude` and `UiMotionData`): an entry with a
  motion of its own (the default) never plays when off and keeps its time and size (they
  are the end state's hold and look: the saved stamp's and a toast's hold, a dim's alpha);
  a part of another motion (`UiMotionData.OFF_PARTS`: `hit_line_flight`, `ride_swap`,
  `ride_shrink`, `ride_perfect`, `break_crack`, `modem_sign_strike`, `modem_sign_flicker`,
  `forecast_change_fade`, `resolve_side_gap`, `resolve_attacker_gap`, `drag_ghost_tilt`,
  `hit_freeze`, `stamp_fade_in`) takes no time and shows no motion when off (seconds and
  delay 0, amplitude 0 for a share / px / frames, 1 for a scale); a tuning of another entry
  with nothing of its own (`UiMotionData.ALWAYS_ON`: `drag_ghost_tilt_speed`,
  `send_it_drips_share`) is refused off by `UiMotionData.validate` (content validation and
  the schema smoke test check it). A blanket "amplitude 0 when off" was rejected: many
  amplitudes are sizes the rest state keeps (a line's width, the ghost's alpha, a traffic
  threshold). The test switches every table entry off in turn and checks its kind, and the
  views' own shares (the projectile's floor 0.05, the forecast fade's floor 0.01, the
  combat's beat gaps).
- **R4 the lab shows the real motion.** 73 demos played a generic helper on a lab piece
  for a motion the game draws otherwise (a 0 s lift of 0.33 px for `forecast_change_fade`,
  an alpha loop on a sticker for `forecast_road_pulse`, a 1.2 s panel fade for
  `raid_incoming_hold`), or passed the numbers to Fx itself so the piece never read its id.
  Each now plays on the real piece: Fx's own flash and jack (with its CONNECTING line and
  the RAID INCOMING stamp; the reduced jack with reduce effects on for that jack only, the
  setting's value never saved), the real DropLayer (landing, purchase, shred, refusal,
  carry, market flight), the Heat poster crossing a threshold, Toast / ToastNote, the top
  bar's refusal, FlightFx's reject, the HQ scene on a demo campaign in the lab's own save
  slot `motion_lab` (never the player's; deleted when the demo ends) for the selection, the
  drop and its forecast road, the raid (turret and decoy; an ICE-lock raid for the lock and
  home's number fly), the minimap pulse, the key's fold and the influence spread; the
  netrun scene for the route move; the combat scene's own calls (`_perfect_feedback`,
  `_boss_phase_feedback`, `_victory_flash`, `_play_beat` with a made beat for a guard, a
  heal, a status landing and a PERFECT hit, `fx_layer.play_card`, a card that plays, the
  RAM spend float). A demo may stay a stand-in (the lab's Motion helper on a lab piece) only
  when the game plays that id with the same helper (a pop is a pop). `Motion.recording`
  notes, per entry read, the first script outside the kit that asked; `test_motion_lab_demos`
  plays every demo and fails any whose id no real piece read (or whose stand-in helper the
  game doesn't use). Eight ids are gated by the headless display inside their piece (Toast,
  the combat log, the hand's gap under the pointer) or need the GPU's bake (the influence
  spread and the bake fade): the test checks they play on a real piece and the windowed
  `--demo-check=<frames>` run confirmed each is read. Also fixed in the lab: a menu demo's
  timers held a window that the next demo freed (now a weak reference) and the city demo set
  a size on a full-rect control. Captured windowed: `forecast_road_pulse` (the pulse runs
  the real threat road to CORE) and `raid_incoming_hold` (the stamp under CONNECTING).
- **R5 a fast integrity test.** `test_suite_integrity` took 40 s alone (47 s in a shard; the
  manifest said 0.4 s): 31 s loaded every test script (and the whole game behind them) and
  8 s compiled three RegExes per line several times over. The compile check is now
  `test_suite_compiles.gd` (full tier, its measured time; the parallel runner also reports
  a script that did not run); the rules read each file once (`source`), compile each
  pattern once (`_re`) and read a line further only when it names a frame signal or a
  fixed-wait call. The integrity tests now take under a second. The manifest's times were
  refreshed from measured runs (`run_tests.py --update-times`). The runner now reruns a
  script that failed in its shard alone and reports it ORDER-DEPENDENT when it passes alone
  (the first full run here failed `test_anim_r4_city`'s verdict sweep in its shard only:
  the RunManager lookup kept a Mirror corporation built by an earlier script, which fix
  agent C is fixing); the run still fails.
- **R6 the fixed-wait rule scans `tests/helpers/`.** Every function there is a helper (its
  caller asserts), so any fixed wait in one is flagged. BoundedWait's polls (a frame at a
  time, counting game time) are no fixed wait: it needs no marker and the test asserts it
  carries none.
- **R7 docs.** STYLE_GUIDE: the focus tip never folds under 20 columns (`FocusTip.FOLD_MIN`,
  ANIM-R4 C7; it said 26), 5.1 gains the one-press-completes-all rule, switching entries
  off and the lab's real pieces. TEST_SUITE: frame lambdas are guarded in `scripts/`,
  `tests/` and `tools/` in every form; every fixed-wait form the rule knows (awaited
  `tween_interval`, `Timer.new` / `wait_time`, `OS.delay_*`, `get_unix_time`, the sleep in a
  poll's lambda, the helpers scan); headless has no RenderingDevice, so rendering paths get
  a windowed check; the integrity test's speed and the compile test.
- **R8** `docs/timeline/motion/README.md`: no combat or generic row changed (their strips
  were captured from scenes and demos this batch didn't change); the city rows are fix
  agent C's.
#### 2026-09-28 — Animation pass — ANIM-R5 combat
The fifth fix batch of the Animation pass review, combat part (items 1-13 of fix agent A).
Views only: no rule, no schema field changed (one new motion id is data). Every call below was
the implementer's (the standing rule: nothing deferred). Tests: `tests/unit/test_anim_r5_combat.gd`
(full tier). Strips recaptured in `docs/timeline/motion/` (CHOSEN on top, a variant under it,
quantized to 128 colours; raw frames never entered the repo): `combat_outcome` (new),
`resolve_sequence`, `enemy_break`. Every visual change was checked in windowed Movie Maker
captures (`netrun_scene --demo-combat --demo-end=lose|win|hover`, new dev flag; the lab's
`send_lose` for `defeat_stamp`), logs free of ERRORs.
- **1 the outcome at its beat.** The state is final at once, but a SEND IT that ends the fight
  now holds its outcome (`_outcome_held`) until the replay lands it: the status line's VICTORY /
  DEFEAT, the next-step button (SEND IT stays, spent, until then), the Heat poster, and in the
  netrun the top bar (HP, CYCLES, CARDS, RANK, BANKED, VIEW LOADOUT) and the run's report (its
  DISPATCH line) wait for `outcome_landed` (as the raid feed gates Heat, H11). The outcome lands
  at the end beat but never before every HP roll of the resolve has ended (`outcome_time`: DEFEAT
  stamped while the HP still read 1); a skip or the replay's end lands it too; reduce effects and
  headless show it at once. The VICTORY / DEFEAT bark moves to that beat.
- **2 a lost fight looks lost.** The operative's disc goes dark under a DEFEAT stamp with a
  skull that stays until the fight is left (`WheelView.flatlined`; `defeat_stamp`, new: 0.3 s
  BACK out from 1.6x; it replaces the transient DEFEAT word). The next step after a loss says
  JACK OUT (the netrun names it; `TextDb.mark("JACK OUT")`) in paper lettering without drips
  (SEND IT's pink drips read as the fight going on). No "hurt" bark on the hit that flatlines
  (`hurt_bark_due`). The FLATLINED summary page's words are the netrun screens' (agent B).
- **3 LETHAL by the HP.** The 6 px red cross over the hub (it struck through the name and read
  as "disabled") is gone. A turn that takes a living wheel (the operative's or an enemy's) to 0
  turns its NEXT plate solid red with a skull and LETHAL (tooltip "LETHAL: this turn takes you /
  it to 0 HP."), readable without colour; the plate shifts left rather than leave its view. The
  operative's tag says DEFEAT once (the DOWN chip beside it is merged into it, ranked first).
- **4 ticks off the words.** A held forecast keeps `tick_room` at each chip's end and the tick
  sits there (`chip_layout`); tested at 1.0 / 1.3 / 1.6 that no tick meets its chip's words.
- **5 a dead enemy never acts.** The engine resolves simultaneously (GDD 2.2) and is unchanged;
  the replay reorders its beats (`ResolveBeats.doomed_first`): a wheel that goes down in the
  resolve plays its own actions (and its satellites') before the hit that takes its HP to 0,
  keeping their order, each marked `same_moment`; every `hp_after` is recounted in the new
  order (the end HP is the engine's; tested). **Decided:** reorder rather than mark "same
  moment" with a badge: the replay then reads cause before effect with no new words.
- **6 NO DAMAGE off the name.** `stamp_slot(text, icon)` checks the stamp as drawn (tilted) fits
  above the name inside the hub; when it can't (BLOCK / SHIELD lines push the name up) it stands
  beside the HP number, in the NEXT plate's place, which is empty while a replay plays.
- **7 was → now.** A hover (card, nudge arrow, RESPIN) that changes a tag shows what it said
  before on the tag's tape, "WAS" and the old title and chips struck through (where IF YOU SEND IT
  stood), and in the tag's tooltip ("Before this play: ..."). **Decided:** the tape, not a row of
  its own: the tag keeps its size (a new row had no room under the screen's top at 1280x720).
  The "YOU PLAY X" chip isn't a change (`play`).
- **8 tags that say who gets what.** A random status chip says who gets it ("☠ YOU GET
  CORRUPTED" / "☠ GETS CORRUPTED"), and its odds follow a lead chip "ON A RANDOM SLICE:"; an
  AFFLICT names what it puts on whom on its own tag ("PUTS ☠ CORRUPTED ON YOU", from the
  replay's beats, in the colour of whose win it is; `afflict_chips`).
- **9 translated once.** Every combat tooltip is translated where it is built and shown as given
  (`shown_tip`: the status line, Settings, the Heat poster, SEND IT, the portrait, the cards,
  UNDO, RESPIN, the RAM bar, the wheels' `_get_tooltip` with TextDb names, the tag tooltip's
  lines, the random / respin chips, "Guarded by"). The tutorial's titles and texts are keys
  (`# TR`), filled in and then pseudolocalised once (its {placeholders} survive the scramble);
  Next / Skip tutorial / Finish and its title translate. A scan test flags any `tooltip_text = "`
  or `_get_tooltip` `return "..."` literal under `scripts/ui/` that isn't tr'd or `# TR`; it
  found two outside combat, fixed minimally: the Daemon row's empty tooltip and the spinner
  pads' "%s\n%d CYCLES". strings.csv re-exported (RANDOM SLICE dropped).
- **10** `_for_continue` asks `MotionSkip.button_at` (shown, not covered, the clicking button
  in its mask): a right-click on the next step during the replay is consumed like any press.
- **11** The Perfect inversion's two frames are one-shot connections to the scene's own method
  (dropped with the scene; the tree is checked before the next), no `await` on a freed scene.
- **12** STYLE_GUIDE 5.2's icon row uses the ANIM-R4 notation (sword 6 − shield 5 = 1); 5.2 gains
  "The outcome at its beat (ANIM-R5)".
- **13** Reduce effects for the R4 combat motions tested: no replay (so no side / attacker gaps),
  nothing busy, no card forecast hold, the RAM refill at once without a float, loot taken with no
  hold.
- New id (data; REQUIRED_IDS and the lab's `send_lose` demo): `defeat_stamp`. New dev flag:
  `netrun_scene --demo-combat --demo-end=win|lose|hover` (demo run only).
- Test expectations changed on purpose: `test_anim_r3_combat`
  `test_after_a_win_the_next_step_replaces_send_it_at_once` (the next step shows once VICTORY
  lands, not at the press); `test_anim_r4_combat` exports "ON A RANDOM SLICE:" (RANDOM SLICE gone).
#### 2026-09-28 — Animation pass — ANIM-R5 netrun screens
The fifth fix batch of the Animation pass review, netrun screens part (B1-B11). Views only
(no rule, no schema field; the one new motion id is data). Every call below was the
implementer's (the standing rule: nothing deferred). Tests: `tests/unit/test_anim_r5_netrun.gd`
(full tier, 14 tests). Checked in windowed Movie Maker captures (no ERROR in the logs); strips
recaptured in `docs/timeline/motion/` (CHOSEN on top, a variant under it, the whole screen,
quantized to 128 colours, raw frames never entered the repo): `buy_fly`, `loot_pick`,
`dispatch_type`, `route_pulse`, and new `event_page`, `run_end`.
- **B1 the event's paper (P1).** R4 C7's "as tall as its words" gave the ZinePanel no height
  at all: a ZinePanel is a plain Control with no minimum of its own, and the RichTextLabel,
  typing from `visible_characters = 0`, measured (fit_content) only the characters shown, so
  the paper was a sliver and the title and story drew in dark ink over the city. Now
  `ZinePanel.fit_to_content()` (opt-in; other panels size themselves) makes the paper's minimum
  its content's, and a typing label is shaped whole (`VC_CHARS_AFTER_SHAPING`, set by
  `Typing.type_in` for every typing label, and on the event's text and the subtitle): the words
  keep their full height from the first frame. Tested with typing ON at 1.0 / 1.3 / 1.6: the
  paper holds its title and every line while they type, and the height does not change when
  they finish.
- **B2 the subtitle.** The event's line was paged for the fallback band (two lines at 964 px)
  before the page's own one-line strip registered; the re-dock then fitted that two-line page
  into one line by shrinking the font (to 7 px), and nothing grew it back. A dock of another
  shape now pages the line on screen again (`Dialogue._repage_shown`: the page shown and the
  rest of its line, at the text size's font), and a page never shrinks below
  `Dialogue.MIN_FONT_SIZE` (12 px x the text size; past it the page clips). The event's and the
  run end's bands hold two lines (`SubtitleStrip.set_lines`, `SUBTITLE_LINES`): long lines wrap
  instead of paging with a "…" (the run end's "do not let it be for …").
- **B3 the run's end.** It was the glass sheet (solid over the city, which a flatline in a
  fight had also hidden: `background.visible` is now set for every page but a fight) with its
  words in the top 250 px. Now a window centred over the city: a verdict stamp (a resolved
  `ForecastStamp`, landing with `forecast_stamp_resolve`: FLATLINED / JACKED OUT / HOME FELL),
  the operative's fate in words (**a flatline is permanent**, GDD 4.2 / 5.1 permadeath: "X is
  gone for good (permadeath): an operative who flatlines never comes back. Banked Schematics are
  kept; Cycles and unbanked loot are lost."), the run's tags, and a Heat line beside the HEAT
  tag's number ("Heat +11: flatlined on a run."; with Heat from the route too, "+11 for
  flatlining on a run, +2 from the route's nodes and events", the flatline's share read from
  the session's own Heat event). Translated once. **Decided:** a completed run's verdict is
  JACKED OUT (the title bar already said "NETRUN // JACK OUT"), an aborted one's HOME FELL.
- **B4 words whole before the page settles.** A subtitle page now types within
  `dispatch_type`'s amplitude (new: 0.8 s, the event story's cap), and a netrun page's first
  focus lands once its entrance has ended and the words typing on it and in the subtitle are
  whole (`_settle_page`; the one-press rule completes them and the focus lands at once). The
  event page keeps its own rule (focus on the first choice at once, the choices held until the
  words are whole: ANIM-R2 E1).
- **B5 flights.** `buy_fly` 0.7 s to x0.55 (was 0.4 s to x0.35), `loot_pick` 0.7 s (was 0.35 s),
  and a flight's landing pulses the tag it went to (`flight_land_pulse`, new: 0.4 s to x1.3,
  bigger than a value's x1.08 bump; CARDS for a card, the DAEMONS icon or VIEW LOADOUT for the
  rest; `FlightFx.fly(..., on_land)`). Within the readability rule: nothing waits on it (any
  press ends a flight and the pulse still plays). The loot page (R4 C7) now waits for the picked
  card's flight too (its lift included), so no loot flies over the route that comes in.
- **B6 the route move.** The move's new choices were live and focused, and the "a choice
  pressed while travelling skips the move" guard in `enter_node` was dead: `_input` ended the
  move and passed the press on, and the choice then reached `NetrunSession.enter_node` after the
  move had opened the node (refused). Now the route page is the move's keep list
  (`MotionSkip.verdict(..., route_keep())`: a press on a choice, GRID VIEW or Save & quit ends the
  move and does nothing else) and nothing on the page takes focus during the move (the node's
  screen takes it). The guard stays as a defence.
- **B7 the route demo** reaches its first node through the session (`demo_first_node`:
  `enter_node`, the fight's SEND ITs, `skip_reward`); the view no longer sets the run's node or
  visited list.
- **B8** the mid-run raid playout is a screen of its own (`RAID_PLAYOUT_SCREEN`): its title is
  NETRUN // RAID (it said NETRUN // ROUTE, the run's phase being the route again), and the route
  after it enters as a new screen.
- **B9** a route choice's "then:" icons carry their words ("then: [bag] Shop", the route's own
  node words, translated), in a flow that wraps in the ROUTE window.
- **B10** `_frame_raid_map` stops when the scene left the tree during its frame's wait, and the
  demos' frame waits go through `_frames_in_tree` (never `get_tree()` on nothing).
- **B11** the Modem's socket list says what it is for: "Chips go into: [Slot 1: CRIT 12]" with a
  tooltip on both (what a chip does, that BUY sockets it there, that a drag picks the slot too).
  Presentation only.
- New id: `flight_land_pulse` (REQUIRED_IDS, lab demo). Retuned: `buy_fly`, `loot_pick`,
  `dispatch_type` (amplitude). Words (exported once): the fate lines, the Heat reasons, JACKED
  OUT, HOME FELL, Chips go into:, the socket tip; dropped: CLEAN EXIT, ABORTED, "Socket into
  %s", the old socket tip.
- Expectation changed on purpose: `test_horizontal_pass20_screens` (the result stamp is a
  resolved ForecastStamp saying JACKED OUT).

#### 2026-09-28 — Animation pass — ANIM-R4 combat, input and screens
The fourth fix batch of the Animation pass review, combat, input and screens part (C1-C7).
Views only (no rule, no schema field changed; new motion ids are data). Every call below was
the implementer's (the standing rule: nothing deferred). Tests: `tests/unit/test_anim_r4_combat.gd`
(full tier). Strips recaptured in `docs/timeline/motion/` (CHOSEN on top, a variant under it,
quantized to 128 colours; raw frames never entered the repo): `resolve_sequence` (both rows),
`number_float`, `enemy_break`, `card_play`, `loot_pick`.
- **C1 LOOT / CONTINUE translated once.** The netrun names the next step with the key
  (`TextDb.mark("LOOT")`), the drip lettering translates it once where it draws it, and the
  tooltip is that translation shown as given (`TextDb.shown_as_given` on the button). A
  DripButton measures what it draws: `lettering_room` is the source word's width or the
  translation's at the smallest size, whichever is wider, and `drawn_width` is the words as
  drawn (tests: under pseudolocalisation and with an "xx" catalogue). Found on the way and
  fixed the same way: LEAVE THE MODEM, the graffiti tag and the graffiti scrawl (they arrive
  translated; `draw_drip_text(..., translate)` false draws them as given).
- **C2 one press rule everywhere (`MotionSkip.verdict`).** IGNORE while a PauseMenu is open
  (the motion plays on; the press is the menu's), PASS for a press that works the screen,
  CONSUME otherwise. Applied to PageTransition, FlightFx, DropLayer, the route move and the
  combat replay (Typing, Dialogue and the raid playout already followed it). `works_ui`
  trusts the hovered control when it holds the point (a button under a panel is not
  clicked), requires the clicking button in `button_mask` (a right-click works no left-click
  button) and searches rects only when nothing hovered holds the point. **Decided:** the
  replay keeps the presses on the fight's own controls (`replay_keeps`: SEND IT, the
  stickers, the hand): such a press ends the replay and does nothing else, so a double tap
  never plays the next turn blind (the next-step LOOT / CONTINUE still works at once).
  `MenuMotion.works_menu` passes the Settings key; a menu behind an open pause menu leaves
  it its presses. STYLE_GUIDE 5.1 says so.
- **C3 leaks and orphans.** `SettingsPanel.show_section` frees what a section made (labels,
  the Controls grid, the note, Reset: queued, Reset calls it from its own press) and the
  built widgets waiting off the tree go with the panel (`NOTIFICATION_PREDELETE`); tested
  with Options opened and closed five times (node and orphan counts unchanged).
  `_build_hand` frees the old cards at once (queued only while a card's own press or a drag
  is being handled). The pass23 / pass24 tests call the scene script's statics instead of
  instantiating the scene for them.
- **C4 nudge key hints** (`WheelView.arrow_hint_rect`): above the arrow as before unless that
  touches the tag (at 1.3 / 1.6 a two-row tag reaches past the arrows), then beside the arrow
  on its outer side, then under it; `layout_violations` reports a hint on any tag.
- **C5 motion numbers in the table**: `hit_line_flight` (0.6; was the inline 0.5),
  `ride_swap` (0.45), `ride_shrink` (0.6), `ride_perfect` (1.35), `break_crack` (0.22),
  `modem_sign_strike` (0.45), `modem_sign_flicker` (0.25). Kept inline and documented as
  drawing, not motion: the tick's radius share (`TICK_SHARE`), the crack line's alpha and
  width, the flicker's lit chance, the equation's spacing. STYLE_GUIDE 5.2's "stamps
  BLOCKED or EVADED on impact" now says what the replay does.
- **C6 SEND IT for a beginner and a non-English reader.**
  - a. Beats carry their `side` and `wheel_source`; the schedule makes the first projectile
    of the other side wait until every HP roll so far has ended and every hit has landed,
    plus `resolve_side_gap` (new, 0.35 s), and another attacker on the same side (a drone
    after its wheel, a satellite after its host) wait `resolve_attacker_gap` (new, 0.15 s)
    after the last arrival. The engine already orders the operative, its drones, then each
    enemy and its satellites within a pass, so nothing is reordered (the HP a beat shows is
    the engine's order's). Turns with hits from both sides run longer (any press skips).
  - b. A hit's number, its equation and its HP change appear only at the impact (they did;
    now tested for every kind). The source slice is the landing of the needle's own
    resolution (`_landing_for`, a SHUNT / MIRROR neighbour resolves as a second entry under
    one needle), and the projectile leaves from that slice's band right under the needle
    (`needle_slot_spot`; the slice's middle when a neighbour rule resolved the slice beside it).
  - c. One notation everywhere: `hit_equation` (sword and the raw hit, minus the shield or the
    evade mark and what it took, = what got through; `CombatFxLayer.draw_equation`) is the
    mark where a guarded hit strikes and the LAST TURN icon row (no arrow; an HP change the
    hits don't explain follows after a dot). Any soak (block or shield) wears the shield
    glyph (DEFEND). What gets through pops fresh in the hub `hit_absorb` after the impact
    and travels; the raw number no longer morphs into it and no separate guard number shows
    for a soak. The raw hit value rides every projectile, the enemies' included.
  - d. Colours were already by side (acid, red), checked for drones too. The projectile is
    seen: `hit_line` 0.45 s (was 0.3) flying 60 % of it (0.27 s, was 0.15 s), a bigger head
    ringed in paper so the acid shot reads over the operative's acid wheel.
  - e. After a card or a respin that turns a wheel the forecast tags hide until the turn
    lands (`_card_hold`, released by the spin's end or a skip; `play_turn` / `play_pointers`
    return when they land). **The "MISS · half power" tag with a 14 hit was a demo
    artefact**: the lab's `numbers` demo played made-up beats over a live fight whose own
    forecast said MISS. The demo now plays a real SEND IT (the Breaker's ring makes its own
    hits pierce, so the guarded hit is the enemy's: a fight where the enemy hits, the
    operative given a block of a third of that hit, lab only, the forecast refreshed), so the
    tag says what happens. Regression test: over three enemies and three seeds the tag's landing
    slices equal the resolve's (no preview≠result found).
  - f. A status lands as its glyph in green (good for you) or red (bad for you:
    `WheelView.status_good_for_you`; OVERCLOCKED and ENCRYPTED help their slice's owner,
    CORRUPTED and PARASITE hurt it), and the slice's mark, its landing ring and rim and the
    tag's status chips wear the same colours; the slice's tooltip starts "Bad for you:" /
    "Good for you:". A random status's chip says which and whose ("☠ CORRUPTED · RANDOM
    SLICE", red on your wheel, the note in the tag's tooltip).
  - g. DEFEATED and its skull wear the beaten wheel's own colour (`defeated_color`); VICTORY
    stands in the room above the first enemy's disc (`room_above_disc`, fitted there by
    `CombatFxLayer.word_fit`), never over the crack.
  - h. A refusal ends any RAM float (it read as a loss; NEED / HAVE says it); the turn-start
    refill floats "+N RAM" in cyan (`ram_refill_float`, new); the float starts above the
    count's words and rises from there (`spend_rect` never meets `label_rect` at 1.0-1.6).
    The lab's refusal demo no longer floats the RAM it set to 0.
- **C7 screens.** The loot page stays, inert (a blocker, focus released), until the offers not
  taken have fallen inside its window (`loot_reject`; a press lands them and the page goes),
  then the route shows: they floated over the route map. The loot's graffiti tag shrinks to
  fit the loot row (`GraffitiTag.fit_width`, down to 22 px) and draws its words as given. A
  focus tip never folds under 20 columns (it folded to 16 at 1.6: a word a line); a crowded
  one tries the screen's top and bottom edges and corners, then steps its lettering down
  (0.85, 0.72 of the tooltip size) before covering anything, and keeps off the MODEM sign. A shop card's text keeps clear of its BUY sticker's flap (its reach
  is in `buy_room`). A price refusal under a tag narrower than its words wraps at its dot
  (NEED 53 over HAVE 5). An event's story types within 0.8 s (`event_type`, new: 0.02 s a
  character, the whole text within its amplitude; `Typing` caps any entry with an
  amplitude) and its paper is as tall as its words (no 200 px floor).
- New ids (data; REQUIRED_IDS and lab demos): `hit_line_flight`, `ride_swap`, `ride_shrink`,
  `ride_perfect`, `break_crack`, `modem_sign_strike`, `modem_sign_flicker`,
  `resolve_side_gap`, `resolve_attacker_gap`, `ram_refill_float`, `event_type` (188
  entries). Retuned: `hit_line` 0.45 s. Lab: `send_both` (both sides hit), `numbers` is a
  real SEND IT.
- Words (exported once, strings.csv): RANDOM SLICE, Good for you: %s, Bad for you: %s, +%d
  RAM; dropped: RANDOM STATUS.
- Test expectations changed on purpose: `test_anim_r1_combat` and `test_anim2_combat_motion`
  (the budget allows the arrival waits and the side and attacker gaps; the shared-predicate
  check accepts the verdict), `test_anim_r2_combat` (the hit's equation where it struck,
  no raw number in the hub, the HP number after `hit_absorb`), `test_anim_r3_combat` (the
  guard is in the equation; the icon row's `dealt`; the MODEM sign's shares from the table;
  the continue button carries the key), `test_horizontal_pass23` / `pass24` (the script's
  statics without an instance).

#### 2026-09-28 — Animation pass — ANIM-R4 city, raid, heat, route and HQ
The fourth fix batch of the Animation pass review, city, raid, Heat, route and HQ part
(H1-H11). Every call below was the implementer's (the standing rule: nothing deferred).
Views, save three small data additions named where they are (H4 the resolver's events carry
the threat's content id; H5 `HeatThresholdData.id`; H11a Heat events carry `before` /
`after`): no rule changed. Tests: `tests/unit/test_anim_r4_city.gd` (full tier, 14 tests), a
no-crew / raid-pending HQ case in `test_pad_reachability` and the rules' new forms in
`test_suite_integrity`; expectation changes at the end. Strips recaptured in
`docs/timeline/motion/` (CHOSEN on top, a variant under it, the whole screen at 0.4,
quantized to 128 colours, raw frames deleted): `raid_playout`, `influence_spread`,
`heat_pulse`, `jack_in`, `route_pulse`, `asset_drop`.
- **H1 the HQ menu by pad.** `UiFocus.link_layout` read a horizontal container as one row
  (a control per child: the menu column gave only City Grid, whose down led to the Black
  Market; RAID PENDING, Scrub Heat, Codex, Settings and Save were left to Godot's geometric
  search, which found none of them with no crew alive). Now a horizontal container whose
  children hold more than one row each is a block of columns: up / down walk a column item
  by item, left / right cross to the same row (clamped) of the next column, a column's last
  item goes down to the block below (its first up to the block above). A container whose
  children are one row each links as before (every other panel's paths unchanged). Tested
  with no operative alive, with and without a raid pending, at 1.0 / 1.3 / 1.6.
- **H2** the feed names operatives (`operative_word`: the roster's name; "an operative" when
  unknown), never "op_1 returns to the reserves"; tested with an operative stationed.
- **H3 one raid verdict.** `RaidVerdict` holds the words: ALL HOLD only when the raid costs
  nothing (home loses no integrity, no node Disabled or Seized), else the losses one per line
  in the words the nodes' labels and stamps use ("HOME -5", "1 DISABLED", "1 SEIZED"), and
  CAMPAIGN LOST when home falls. "HOME HIT" is gone (it sat beside home's "HOLDS" banner):
  home's loss is its number everywhere, and the map's banner is "HOME -5 · HOLDS" / "HOME
  HOLDS" / "CAMPAIGN LOST". The setup's and the interlude's forecast stamps, the playout's
  resolved stamp, the report's stamp (it said BREACHED for a raid home never felt: now the
  resolved verdict stamp) and the forecast's tooltip use it; `ForecastStamp` draws a verdict
  of several lines (one per loss) and shows a composed verdict as given (translated once).
  Swept over every corporation x every home variant x ICE 0 and 20 x three setups (150
  raids): the forecast's verdict is the result's, ALL HOLD exactly when nothing is lost.
- **H4 threat names translate.** Every resolver event naming a threat carries
  `threat_content` (its ThreatData id; the names were parsed from the English log line and
  run through tr, which had no key); the feed, the playout's markers and the node tooltips
  read `TextDb.t(ThreatData, "display_name")`.
- **H5 Heat consequences.** `HeatThresholdData` gains `id` ("heat_25"; schema change, logged
  here, `validate` requires one, unique; the smoke test checks it): its `event_text` has the
  key `HeatThresholdData.heat_25.event_text`, exported. The texts are whole sentences ("The
  corporation raids the Cell. While Heat stays at 25 or more, elites are more frequent.", not
  "Raid. While Heat stays at 25 or above..."); the poster reads them through TextDb.
- **H6 the Heat banner.** It says the Heat now, the band and where the band starts: "HEAT
  30 · NOTICED (25+)" ("HEAT 5 · COOL" below the first threshold). The band word under the
  number follows the number shown (`shown_band`: it said NOTICED while the roll still showed
  21). The banner is laid out in its room (`banner_layout`, worked out once per change): the
  wanted poster's header, the small poster's paper under its bar (the combat poster is 170 x
  134: its banner spilled 23-63 px over the Daemon row at 1.0-1.6); the words keep one line
  down to 12 px, then wrap at " · " and at spaces, a word too long for a line broken between
  letters, down to 8 px; the consequence shrinks with them and goes to the tooltip only when
  even the floor would not fit; a short small poster takes its bar too. The whole tilted box
  (sub-lines included) is tested inside its poster and its room, never over the number, with
  a long German translation, at 1.0 / 1.3 / 1.6, and in a live fight above the Daemon row.
- **H7** the map tooltips' sentences ("You are here.", "Raid: %s.", "Threats here: %s.", the
  kind names...) are keys translated once where the tip is built; the overlay shows its tip
  as given.
- **H8 integrity rules.** Frame lambdas: tests/ and tools/ are scanned too (the anim5 test's
  held lambda is a method now); a connect whose line ends open ("process_frame.connect(" with
  the `func` on the next line) is read with the lines after it; `Signal(obj, "process_frame")
  .connect(func` is caught; string literals are emptied first (a test's quoted example is not
  code). Fixed waits: an awaited `tween_interval`, `Timer.new()` / `wait_time`, `OS.delay_msec`
  / `delay_usec` and `get_unix_time` are caught; an interval nothing awaits (one that keeps a
  sequence running) and a sleep inside a poll's lambda (load, not a wait) are not; an inner
  class's methods are functions of their own. No false positive on the code base.
- **H9** B6's colour claim corrected in place (acid is at least 40 degrees of hue from every
  corporation, Meridian's orange the nearest; it said "furthest"), and in `Palette`.
  `CHANGE_FADE_SHARE` (1/3 inline) is `forecast_change_fade`'s amplitude.
- **H10 performance** (corrected by ANIM-R5 city, "Measurements": these were taken while every
  kept bake drew nothing) (this machine's display, 1280x720, RX 6700 XT; min / median of 5 runs,
  the baseline aa51ad2 measured in the same session, the machine busy with other test runs):
  - the Grid opened from the HQ page (`--demo-grid-open=150`): 136-170 ms, median 149
    (baseline 243-268, median 255; R2 measured 161). What its frame spent (instrumented): the
    Grid's music built on the main thread 59 ms (now built ahead on the worker pool:
    `AudioDirector.prewarm_music`, from the HQ page, the Grid and the route), the open runs'
    clear previews 44 ms (`CampaignRules.clear_preview` copies the campaign per Site: now
    cached by the campaign state's hash and worked out ahead on the HQ page, a Site a frame);
    the re-open 94-109 ms, median 101 (baseline 129-146);
  - the route after a jack at 1.6 (`--demo-grid --demo-anim=jack_in`): its 58-72 ms frame
    was the route view's bake landing, ~14 ms of it a GPU texture made and filled to copy the
    bake's viewport into; now the viewport is kept (never updated again) and shown as it is
    (`BakedTexture.held`): the landing frame 54, 56, <50, <50, <50 ms over five runs (before
    58-67 here, the baseline 54-89). No frame after the cover lifts over 50 ms in three runs of
    five; the rest single frames of 51-85 ms not tied to the map (the machine's load: frames
    before the jack showed the same). The jack itself is longer by design with a raid queued
    (the RAID INCOMING stamp's 1.2 s).
- **H11 a raid reads true.** The top bar's Heat and RAIDS change with the line that changes
  them (`RaidPlayoutPanel.event_shown`: Heat at its "Heat +5 for the lost raid: 1 → 6." line,
  RAIDS at the raid's end line and at a threshold's line that queues one); the Heat line says
  from and to (it said "now" with the campaign's final Heat: "+5 ... now 5" from 1; the Heat
  event carries `before` / `after`); a threshold crossed gets its own line with what it brings.
  A hit's line says the HP it really took and where it left the node ("Wearable Telemetry
  Farm takes 5 damage: HP 30 → 25."), the numbers the map's labels and floats show (a hit stops
  at 0, as the map's numbers do). A threat token stands on an opaque dark halo with a paper rim
  (its red glow over a pink node read pinkish): tested at WCAG's 3:1 for non-text on every node
  colour. RAID INCOMING is a stamp of its own under CONNECTING: large amber Anton (34 px x the
  text size) in a ruled box, tilted, naming the corporation ("RAID INCOMING" over "SOLACE
  BIOSYSTEMS"), held `raid_incoming_hold` 1.2 s (a reading time: under reduce effects too).
- **H11 b the drop and the forecast.** A landed defence sends a pulse along the threat road
  from its node to CORE (`forecast_road_pulse` 0.55 s, the road as threats take it: the Grid's
  next hops to home), then the forecast numbers it changed rise; CORE's label and its float
  show the same number (tested). Every forecast change reads "45 → 50 ▲" (green, a gain) or
  "50 → 45 ▼" (pink); the raid setup's, the interlude's and the report's HP badges and the map's
  result tags read "a → b" too. Share Tech Mono has no arrows: text that writes one (a
  badge, a map tag, the raid feed) uses `Palette.mono_arrows()`, a FontVariation over the file
  with Anton as its fallback (the file is untouched). Only that text: a first try gave every
  mono text the fallback, which raised the face's line height and broke 28 layout tests.
- **H11 c the route.** A move shows the new choices as it starts (`view_choices`: while the
  entered node plays, the nodes it leads to): the map's [1] / [2] labels and the ROUTE
  window's buttons (rebuilt in place; the old ones hidden and freed, one of them is the button
  pressed) at once, the marker travelling the link (never on a choice: tested along the move);
  the walked route stays as a faint solid trail (the Cell's pink at 0.4, 2.2 px). The capture
  demo is a real move now (the demo run stands on its first node, then moves on).
- **H11 d territory.** A CLAIMED / SEIZED stamp takes the first spot round its Site (above,
  below, right, left) whose tilted box covers no node label or icon (`NeonCity.stamp_rect`,
  the map's `stamp_avoid_rects`), the least covered when all do: it hid "Patch Distribution
  Node". The side panel's "RAID SETU" and "PRICING MEMO AR" were the ANIM-R3 strip's crop, not
  the game: the strips now show the whole screen, and a test checks that no word of the Grid's
  and the raid setup's side panels is cut at 1.0 / 1.3 / 1.6.
- **New ids:** `forecast_change_fade`, `raid_incoming_hold`, `forecast_road_pulse` (the lab
  plays each).
- **Expectation changes:** `test_anim5_map_motion` (the verdict is RaidVerdict's; the held
  lambda is a method), `test_horizontal_pass20_screens` (the verdict; "HP a → b"),
  `test_horizontal_pass22_screens` (no HOME HIT: home's loss is "HOME -N"),
  `test_anim_r3_city` (the jack note names the corporation), `test_pad_reachability` (the HQ
  case added), `test_suite_integrity` (the new forms and false-alarm cases).

#### 2026-09-28 — Animation pass — ANIM-R3 city, raid, jack, heat and route
The third fix batch of the Animation pass review, city, raid, jack, Heat and route part
(B1-B13). Views only (no rule or schema field changed). Every call below was the
implementer's (the standing rule: nothing deferred). Tests: `tests/unit/test_anim_r3_city.gd`
(full tier, 18 tests) and a lambda-rule test in `test_suite_integrity`; expectation changes
listed at the end. Strips recaptured in `docs/timeline/motion/` (CHOSEN on top, a variant
under it, quantized to 128 colours, raw frames deleted): `raid_playout`, `influence_spread`,
`heat_pulse`, `jack_in`, `route_pulse`, `asset_drop`. Measured on this machine's display
(1280x720, RX 6700 XT, Vulkan Forward+) with `tools/design_lab/profile_frames.gd --timeline`.
- **B1 the jack's first frame.** Two causes, both fixed. (1) The HQ's JACK IN built the run
  (`RunManager.start_run`: the map, the session, its autosave: ~44 ms measured in place) in
  the frame the cover started; now `RunManager.go_to_netrun(before_switch, site_id)` runs it
  at the scene switch, under the opaque cover (at once when no jack plays: tests, reduce
  effects' fade, switching off), and the cover names the Site from its id before the run
  exists. (2) The cover's and the Heat distortion's shaders compiled on their first draw:
  `Fx._warm_materials` draws both, invisibly (progress 0, intensity 0), for `WARM_FRAMES` (2)
  frames at start. Measured (`--demo-grid --demo-anim=jack_in`): before, the jack's frame
  took 92 ms (f94); after, no frame over 50 ms from the press to the switch (the switch
  frame itself, 148 ms, is under the opaque cover, as before).
- **B2:** `_hold_connect` is a reading time, not an effect: it holds under reduce effects
  too (the fade showed CONNECTING ~2 frames); only the entry switched off skips it.
- **B3 route twins.** "(same as N)" now means the same whole road: `subgraph_signatures`
  interns, from the last layer back, each node's kind, Heat and the multiset of its
  successors' signatures (linear, no unfolding), and `choice_twins` compares those. Checked
  against a plain recursive comparison on 60 generated maps (every same-layer pair; some
  real twins, and pairs the old next-layer label called twins that now differ). A choice
  that is not a twin shows a row under its button: its entering Heat as an icon and number
  (it was only words) and the icons of what only it reaches further on (Elite, Shop, Event,
  Rack, Heat: `choice_differences`, the kinds some but not all choices reach), each with its
  word as a tooltip; the map label carries the Heat too.
- **B4 never an empty map.** While a view bakes, NeonCity draws the city's silhouette on a
  layer of its own (`CitySilhouette`, under the veil): each building's footprint cell from
  the placement (`_front_of`, cheap; the buildings are not built) as a dim lifted block with
  a faint outline, from the view's middle outward, `SILHOUETTE_BUDGET_USEC` 8 ms a frame
  until every lot is known (the first Grid frame shows the middle; ~1 s fills the rest). The
  veil draws it too, so a landing image fades in from the silhouette, not from black, over
  `city_bake_fade` 0.8 s (was 0.35 s: the arena "popped in" mid-fight). A first attempt drew
  roofs (`placed_roof`): too slow per lot (the view filled over seconds) and it re-laid the
  maps each redraw (it drew on the view, whose redraw emits `rebuilt`); a deferred redraw
  from inside a draw looped in one frame. Both avoided by the layer and `_process` stepping.
- **B5 raids read true.**
  - One verdict per node: every node's stamp is its resolved outcome (`nodes[id].outcome`,
    the word its label says); home gets no stamp: its verdict is the banner ("HOME -5 -
    HOLDS", "HOME HOLDS", "HOME BREACHED" when the campaign is lost). The old code stamped
    home BREACHED whenever it lost anything, beside a label that said HOLDS.
  - Numbers: one per hit, the integrity it really took (a cascade or a hit on home stops at
    0); the hit that disables a node shows what was left, a Site seized with integrity left
    shows its loss, so a node's numbers add up to its before - after (checked for every
    corporation, three setups each). Node numbers rise on the node's right, a shot's on the
    threat's left (the -4 on the threat standing on CORE sat on home's -5), stacked when
    several show at once, drawn over the stamps.
  - The banner is placed clear of every stamp, node label and icon and inside the map
    (`banner_rect`: above home, below its bar, left, right, the least covered), so at 1.6 it
    no longer covers the stamps and labels; it stamps on `raid_result_banner`'s delay (now
    read: 0.2 s) after the last outcome flips, fading in over `stamp_fade_in`'s share.
  - The RAID FEED speaks in translated sentences with display names (`feed_line`: CORE, the
    Site's name, the threat's and defence's names), never an id ("Turret at t1_a"); the end
    is "Raid over after 2 step(s). Threats destroyed: 0. Reached home: 1. Disabled: 0.
    Seized: 0."; a Heat line only when Heat moved.
  - The playout page shows whole at once (no page entrance: its first frames were a dim,
    half-drawn map).
  - A landing defence falls 56 px (was 24) from x2.2 its size (`asset_drop_grow`), its stamp
    ring is thicker with a pink flash, and each forecast number it changed rises off its node
    ("25 > 30", green when better, pink when worse; `forecast_change` 1.4 s, fading over its
    last third); the HQ passes the forecast before the change (`forecast_values`).
  - The mid-run raid interlude is set up like the raid setup (the raid's warning, the dashed
    forecast stamp, HOME a > b and STOPPED badges, a badge per node with HP now > after and
    the outcome word) instead of a form of text lines; `--demo-interlude` opens it. The jack
    into a run that opens on it says "CONNECTING TO <SITE>" and "INTERRUPTED: RAID INCOMING"
    (`jack_note`: a raid queued on the campaign).
  - The jack's dissolve is a calm wave from the CRT: `jack_dissolve` (spread 0.9 of a cell's
    turn from its distance, 0.1 from its hash; each cell fades in over 0.08 of the progress)
    instead of scattered hard cells (spread 0.6, a step) that read as corruption.
- **B6 territory.** The CLAIMED / SEIZED stamps draw on the map's top layer, over the
  labels, right over their Site (`MARK_LIFT` 26, was 70 up a leader); the district is hatched
  (`MARK_HATCH` 9 px, alpha 0.5) over a 0.2 wash, and the lasting tint is 0.45 (`influence_tint`,
  was 0.3). The Grid's Site card rebuilds in place when a claim is seen (`refresh_site_card`):
  CLAIMED with the claim mark, no CLAIM offer. **Colour:** the Cell's territory (claimed Sites,
  its links, the tint, the marks, the spray ring and the key's rows) is `Palette.CELL_TURF`,
  the Cell's acid #D4FF00, never `cell_pink` (pink is damage and hits everywhere). Acid
  (hue 70) is at least 40 degrees of hue from every corporation's colour: Meridian's orange
  #FF8C1A (hue 30) is the nearest, at 40; Solace's mint 74, REBEL_CELL's red 73, Orbital's
  pale blue 159, Halcyon's violet 178. (Corrected in ANIM-R4 H9: this entry first said acid
  was *furthest* from every corporation, which is wrong for Meridian.) Hue alone does not
  carry it, so every territory mark carries a non-colour cue (spray ring, hatch, stamp word).
  STYLE_GUIDE 2 and 5.3.
- **B7 Heat.** The crossing's banner no longer sits on the number: on the wanted poster it
  covers the WANTED header and mugshot, on the small poster it hangs under the bar; it fades
  after its hold as before. Its colour is the band's warning (amber NOTICED, orange FLAGGED,
  red HUNTED), with a drawn eye before the words; the band's consequence (the threshold's own
  text) is under it when it fits and always in the tooltip. Long translations wrap to two lines
  (at " - ", else the middle space) before the lettering goes under 12 px (it was one line
  down to 8 px, 168 px in 164).
- **B8 route framing.** The route fits the whole route down to `ROUTE_FIT_FLOOR` 0.4 (icons
  keep their screen size), else the part the player decides on (where they are and the next
  choices), inside a `ROUTE_MARGIN` of 36 px x the text size; the you-are-here marker stands
  at the street before the first node (`here_at`: it was drawn nowhere at a run's start) and
  is kept in frame.
- **B9 cleanups.** `net_creep`, `net_creep_recede`, `corp_creep.gdshader` and the Fx creep path
  are gone (REQUIRED_IDS, the table, the lab); the lab's heat demo is the local pulse;
  `--demo-text-scale=` no longer saves the player's settings; `raid_result_banner`'s comment
  says what it does and its delay is read; the banner's fade-in share comes from
  `stamp_fade_in` (was `u * 3.0`); the drop's camera wait is `asset_drop_wait` (was
  DROP_WAIT_MAX); HeatPoster's `mouse_filter` is set in `_init` (it sat after a return).
- **B10 bakes.** `CityBakeCache.drop_stale()` (on every request and when the slot is wanted)
  drops queued bakes whose every waiter is gone and stops a building one (its slot given back:
  records carry `holding`): the HQ's Grid and playout prebakes no longer hold the one build
  slot after the jack into a run. A bake's coroutine checks its own record (`is_same`), never
  just the key (after `shutdown` a new request for the key has a record of its own).
- **B11 lambda rule.** `frame_lambda` now reads `<sig> .connect ( func`, `connect("<sig>",
  func` / `connect(&"<sig>", func`, `Callable(func` and a lambda held in a variable of the same
  script and then connected (`frame_lambda_lines`); method callables (and bound ones), other
  signals, comments, awaits and disconnects pass.
- **B12 orphans.** `PadPrompts` freed its old labels with `queue_free` after removing them:
  a text size change relabels twice (changed, hints_changed), so a page torn down in the same
  frame left 6 orphan Labels. They are freed at once now. **Not mine, seen in passing:**
  `test_netrun_scene.test_resume_restores_the_identical_run_mid_combat` leaves 5 orphan hand
  buttons (combat) and `test_accessibility.test_settings_panel_toggles_write_to_settings` 49
  (the settings panel's controls): both pre-existing, left to their owners.
- **B13.** SAVED keeps off the screen title (`HudBar.title_box`) and window titles and, when
  every edge spot covers something, searches a grid over the whole screen (`SAVED_INNER_STEP`
  40 px) (at 1.0 the least covered edge spot was over UNDO). The Grid's side column ends above
  the first run row it would cut (`ScrollHint.snap_rows`: the room under the view takes the
  cut row's height at the top of the content). The snap is worked out at most once a frame
  and `SNAP_PASSES` (3) times per page: unbounded, the room it set brought a scroll bar in or
  out, which rewrapped the rows it had measured, and the layout chased itself through deferred
  calls until the message queue ran out (`test_city_map_sweeps` crashed with signal 11 in the
  full run); a re-entrant refresh is refused too. The Site card also rebuilds only when what it
  shows changed (`refresh_site_card` compares the card's Site and status).
- **New ids:** `asset_drop_wait`, `asset_drop_grow`, `forecast_change`, `jack_dissolve`.
  Removed: `net_creep`, `net_creep_recede`. Retuned: `asset_drop` 56 px, `city_bake_fade` 0.8 s,
  `influence_tint` 0.45, `raid_result_banner` delay 0.2 s (now read).
- **Expectation changes:** `test_anim5_map_motion` (home's stamp is gone: the banner; the
  creep), `test_anim_r1_campaign` (the creep; the mark's colour), `test_anim_r2_city` (the
  outcomes stamp every node but home; the Heat banner's width is its widest line),
  `test_horizontal_pass20_city` (territory colour), `test_suite_integrity` (the rule's
  helper renamed `_frame_code` next to the bounded-wait rule's `_code_of`).

#### 2026-09-28 — Animation pass — ANIM-R3 combat, input and screens
The third fix batch of the Animation pass review, combat, input and screens part (A1-A8).
Views only (no rule, no schema field changed). Every call below was the implementer's (the
standing rule: nothing deferred). Tests: `tests/unit/test_anim_r3_combat.gd` (full tier, 33
tests); strips recaptured in `docs/timeline/motion/` (CHOSEN on top, a variant under it,
quantized to 128 colours; raw frames never entered the repo): `resolve_sequence` (with a
second CHOSEN row: an enemy hit soaked whole), `number_float`, `enemy_break`, `card_play`,
`drag_buy_card`, `loot_pick`.
- **A1 drone numbers.** `numbers_for`, `_play_beat`, `_source_spot` and `hit_color` look a
  combatant up in the state the resolve ends on when the state it started from doesn't have
  it (a drone deployed, a satellite launched mid-resolve): its hits fly in the operative's
  colour and its HP changes show at its token. The "every HP change has exactly one number
  of its size, and a combatant's numbers add up to its HP roll" sweep now runs every class
  (8) against every enemy in content (seed 3, three turns; spawned combatants start from
  their spawn HP), and a live `_play_beat` check finds a Botnet drone deployed and hit (or
  hitting) in the same resolve.
- **One press rule, third revision (A2-A4, `MotionSkip.works_ui`).** Outside menus too, a
  press that works the screen completes a motion and passes on: a focus move, the Settings
  key, accept on the focused usable button, a click on a usable button (the hovered one,
  else the topmost button under the point). Only presses aimed at the motion are consumed.
  - A2 the raid playout: such presses pass (so keys and the pad walk to Skip and 1x/2x/4x,
    now named `Speed1x`..., and press them); while a PauseMenu is open (group `pause_menu`,
    `MotionSkip.pause_open`) every press is the menu's; any other press skips one step.
    `_for_own_button` stays as the ANIM-R2 name for `works_ui`.
  - A3 ambient typing (`Typing`) and the Dialogue subtitle: a press shows the words whole;
    one that works the screen passes on (the first click on City Grid or JACK IN while the
    pirate radio types, accept on a focused button); a click on the words or a key that works
    nothing is consumed. An event's held choice still only shows its words on that press (its
    hold is released a frame later), so E1's pad flow is unchanged.
  - A4 `MotionSkip.consume(node, event)` hands the event to `Settings.observe_device` (the
    old `_input` body) before marking it handled: a pad press that ends a motion switches the
    prompts to the pad. Every helper passes its event.
- **A5 the result never shows mid-roll.** `_show_result` first lands every number still on
  its way (`CombatFxLayer.arrive_all`), ends every HP roll on its value
  (`WheelView.finish_hp`) and sets each wheel to the HP its resolve ends on. **Decided:** the
  snap, not slack in the table (slack shortens the hold and still loses to a long frame).
  Tested with every frame of the replay stalled 12 ms.
- **A6 SEND IT legibility (the naive reviewers' final push).**
  - a. A hit that gets nothing through shows where it struck (the arrowhead on the HP ring,
    or the token): its glyph (a shield when soaked whole, the evade mark when evaded) and "0"
    in a small box (`impact_mark`, new: 0.6 s, pops from x1.5). A wheel all of whose hits
    were soaked stamps ALL BLOCKED on its last hit's impact (the schedule marks that beat),
    NO DAMAGE still at the result; both carry a drawn mark (a shield over the empty-set sign,
    `CombatFxLayer.GUARD_NULL`). The red projectile to the HP ring with its arrowhead was
    already there (ANIM-R2); checked in the new `send_block` lab capture.
  - b. The forecast stays through the replay: the tag showing when SEND IT is pressed (the
    end-turn preview, never a hovered card's) is held on its view (`replay_tag`); each chip
    names the beats that make it happen (`ForecastTicks.filter`: kinds, source, target) and
    ticks (an acid check disc on its top-right corner, `forecast_tick`, new: 0.18 s from x1.6)
    once its last beat has landed (a hit on impact, an HP change once its number has settled);
    a chip no beat makes (RAM, Heat, odds) ticks when the result holds. The tape then reads
    THIS TURN (the plate caption is used only when no tag was held), and the tag fades
    (`forecast_fade`, new: 0.25 s) as the wheels turn on, before the next forecast flips in.
    **Decided:** a tick, not a strike-through (a struck line is harder to read and, preview =
    result, no line is ever contradicted); nothing is struck.
  - c. The riding number shows the aim: at half power the slice's own value rides first and
    shrinks into the dealt value marked ½ ("12" -> "6 ½", `RIDE_SWAP_SHARE` 0.45 of the flight,
    to x0.6); a PERFECT landing rides x1.35. `ResolveBeats` beats carry `source_tier`.
  - d. A projectile never launches before the last HP-changing hit's number has entered its
    counter (`ResolveBeats.arrive_after`: impact, absorb, `number_to_hp` hold and travel;
    `beat_timing().arrive`); one HP roll per hit (`play_hp` ends a running roll on its own value
    first). Turns with several hits now run longer (any press skips).
  - e. A guard is a glyph and its number from the blocker: the wheel's own guard under its
    hub lines (shield "5", "+3" block, "+1" evade), a satellite's or drone's beside its token;
    no "N BLOCKED" word badge in the replay (LAST TURN keeps the words).
  - f. An icon row left of each HP number after a turn (sword 6 -> shield 5 = -1; "-0" when
    soaked whole; a heal without hits shows the heal icon and +N), with LAST TURN, kept until
    the player acts (`last_turn_icons`, the resolve phase only); shrinks to 8 px to fit; the
    satellite tokens and plates keep off it.
  - g. The break cracks the real wheel: each slice piece keeps its fill, rim, icon and value,
    the dark hub cracks into a wedge per slice, white cracks draw along the borders for the
    first 22 % (`CRACK_SHARE`) with the pieces in place, then they fall. A skull (drawn) sits
    under DEFEATED on the beaten side.
  - h. Once the fight is over SEND IT, RESPIN and UNDO go at once and a CONTINUE drip button
    takes their place; the netrun names it (LOOT when a payout waits, else CONTINUE) and moves
    on when it is pressed (click, accept, or SEND IT's key; a press during the replay that is
    meant for it ends the replay and presses it). The `combat_end_hold` wait still moves on by
    itself; a generation counter stops it acting after an early leave.
  - i. A played card's effect (and so its wheel's spin) waits for the card's dissolve or burn
    (`play_card` returns fly + stamp + dissolve): it never covers a spinning wheel.
  - j. Words: "YOU PLAY JOLT" (PLAYING read as the enemy playing it); "NEED 3 · HAVE 2" for a
    RAM refusal and the same for a price refusal; NEXT, the HP number, LAST TURN and the icon
    row have tooltips (LAST TURN explains each status it names: GOT CORRUPTED says what
    corruption does); a status landing on a slice marks it at once on the view's own copy of
    the wheel (its mark rings out and the slice's rim lights, `status_mark`, new: 0.6 s, 10 px);
    the tag is never narrower than its tape's words and the tape stands above the title
    (`tape_width`, `tape_height`, `TAPE_INSET`).
- **A7 screens.** The Modem's first focus is its first item a player can afford (else its first
  item), never the socket list (`FIRST_FOCUS_META`). The MODEM sign: each tube strikes within
  the first 45 % of the warm-up, flickers 25 %, then holds lit, and the warm-up is 0.45 s (was
  0.8 s: a still mid-way showed one lit letter). A flight of a card flies a fresh copy of it
  (`FlightFx.picture_of`; the snapshot of a card still dealing in was the empty slot, a grey
  blank card); loot not taken falls clipped to its window (`FlightFx.fly(..., clip)`,
  `loot_window_rect`). The empty-set mark's slash ends on its ring. The loadout's swap chips
  wear a ring pictogram badge on their corner (`SegmentMark`: the segment it swaps in lit; the
  class default with its hub lit), so they keep their size. Every event choice shows outcome
  icons (tested over every event; they all did). Discards land inside the hand's row, clear
  of RESPIN / UNDO. The drag ghost of shop and loot drags already used the 0.92 alpha
  (ANIM-R2); only its strip was old: recaptured.
- **A8** `test_the_crt_roll_waits_for_the_glass_to_show` keeps main's frozen-frames check and
  then judges the roll frame by frame on the transition's own clock (`PageTransition.progress`).
- New ids (data; REQUIRED_IDS and lab demos): `impact_mark`, `forecast_tick`, `forecast_fade`,
  `status_mark` (175 entries). Retuned: `modem_sign_warmup` 0.45 s. Lab: `send_block` (a fight
  whose enemy hits the operative, soaked whole; lab only).
- Words (exported once, strings.csv): YOU PLAY %s, NEED %d · HAVE %d, LOOT, CONTINUE, the NEXT
  and HP tooltips, the LAST TURN icon note; dropped: PLAYING %s.
- Test expectations changed on purpose: `test_anim_r1_combat` (a blocked or evaded hit shows 0
  with its glyph, not a word stamp; NEED/HAVE; token numbers are not hub numbers),
  `test_anim_r2_combat` (the guard is a glyph and a number; the fully blocked hit's mark;
  NEED/HAVE; YOU PLAY; the sweep passes the end state), `test_anim2_combat_motion` (token
  numbers skipped by the hub rule), `test_horizontal_pass24` (YOU PLAY JOLT).

#### 2026-09-28 — Animation pass — bake crash
The parallel runner's shard holding `test_anim_r2_city.gd` sometimes died with "signal 11"
right after `test_the_route_and_the_raid_setup_draw_their_nodes_before_any_bake` (1 run in
3; the ANIM-R2 implementer saw it once too and suspected the bakes). Every call below was
the implementer's.
- **Not the bakes.** Headless, `can_bake()` is false; under `CityBakeCache.simulate` (that
  test) `request` frees each painter at once, so no worker task, SubViewport or
  RenderingDevice texture exists during it. Only two tests start real sliced builds (on
  purpose, by calling `request`), and `shutdown()` in their `after_each` joins them.
  Nothing to gate. (docs/TEST_SUITE.md "What bakes or threads run headless".)
- **Root cause: a lambda connected one-shot to `process_frame`.** ANIM-R2 R9 made
  `CityMapOverlay._queue_top` / `_queue_tags` defer a second redraw in a frame with
  `get_tree().process_frame.connect(func(): _top_later = false ..., CONNECT_ONE_SHOT)`. A
  GDScript lambda that uses self (`GDScriptLambdaSelfCallable`) keeps a raw `Object *`
  and reads it in `get_object()` / `is_valid()`. The engine drops one-shot slots from the
  signal (and from the target's connection list) before calling them, from a copied slot
  list. A test resumes from `await get_tree().process_frame` inside that emission, ends,
  and GUT's autofree `free()`s the HQ right there; the emission then reaches the overlay's
  slot, which its destructor could no longer disconnect, and reads freed memory: nothing
  when the block is untouched, a lambda run on whatever object took the block, or an access
  violation. Reproduced deterministically: with the old overlay the new test's lambda ran on
  other objects in every round (12 "Trying to call a lambda with an invalid instance", 2 on
  a fresh overlay); a method callable in the same place never did.
- **Fix:** those two, and `HqScene._scroll_to_top`'s next-frame reset (a lambda capturing
  the scroll: it logged "Lambda capture at index 0 was freed" in the suite), connect
  methods (`_redraw_top_later`, `_redraw_tags_later`, `_reset_scroll`); a method callable
  holds the object's id and is skipped once the object is gone. **Rule:** no lambda is
  connected to `process_frame`, `physics_frame`, `frame_pre_draw` or `frame_post_draw` in
  scripts/ (`test_suite_integrity.test_no_lambda_is_connected_to_a_frame_signal`). Other
  signals keep lambdas: a normal connection is removed by the destructor, and a one-shot
  one on a signal the freed view's own subtree emits (`tree_exiting`) runs before the free
  completes.
- **Tests:** `tests/unit/test_bake_crash.gd` (full tier): an overlay whose redraw waits for
  the next frame is freed inside that frame's emission, then 64 fresh overlays take its
  memory (fails on the old code, see above); the route and the Grid / raid setup opened and
  freed with `free()` mid-frame six times. Also `test_a_multi_band_rise_...` in
  test_anim_r2_city waits for each crossing (bounded at 4x its motion) instead of
  `number_roll + 0.08 s`: under four loaded shards one frame outlasted the slack (1 of 60
  loops failed there, no crash). Two more waits of that kind failed once each in the full-run
  evidence below and now poll too (bounded): `test_anim_r1_combat` number-to-HP arrival and
  `test_anim_r1_campaign` Heat crossing (it keeps the number's peak scale up to the stamp).
- **Stress tool:** `tools/design_lab/bake_stress.gd` (real display; `--simulate` headless)
  opens the route and the Grid and raid setup over and over while their bakes run and frees
  them mid-bake three ways in turn (`free()` inside process_frame, `queue_free`,
  `shutdown()` then `free()`).
- **Evidence** (this machine, 6 cores, RX 6700 XT, Vulkan Forward+). Before: 60 runs of
  test_anim_r2_city, four at once: 1 signal 11 (right after the route/raid test, as reported)
  and the Heat flake once. After: 50 runs, four at once, all clean (no crash, no failure, no
  "capture was freed" error); `python tools/run_tests.py -j 4` 15 times (968 tests), no crash:
  the first 10 had one timing failure each in two runs (the two waits above, then fixed), the
  last 5 all passed; `bake_stress.gd` on the display: 40 and 60 cycles, 41 and 60 bakes landed,
  13 and 20 shutdowns mid-bake, no error. **Uncertain:** the display stress does not reach the
  overlay's deferred redraw at the moment of a free (it ran clean on the old code too), so it
  covers the bake paths, not this bug; `test_bake_crash.gd` covers the bug.

#### 2026-09-28 — Animation pass — ANIM-R2 city, maps and transitions
The second fix batch of the Animation pass review, city, maps and transitions half (items
R1-R13 of the four reviewers). Views only. Every decision here was the implementer's (the
designer's standing rule: nothing deferred). Tests: `tests/unit/test_anim_r2_city.gd` (20),
two new checks in `test_city_geometry_memo` (the split build, the placement), a print guard
in `test_suite_integrity`. Measurements: `tools/design_lab/profile_frames.gd --timeline
--probe-map` on this machine's display (1280x720, 6 cores); "before" is a755e2d, run the same
way.
- **R1: a map is never empty.** A baked city's placement (where its buildings stand, its street
  grid and the fist) is now answered lot by lot the moment a map asks (`NeonCity._placement`: a
  world-space twin that runs the same building code with nothing emitted; `roof_of`,
  `nearest_building`, `is_street`). It is the bake's own geometry (`test_the_placement_places_the_roofs_a_build_does`:
  every lot of every district's view, the same roof), so nodes and labels draw on a map's
  first frame and do not move when the image lands. The baked city had never built its street
  grid: in the game the map's links cut straight across blocks (headless tests followed the
  streets); they now follow the streets everywhere. While a view's bake runs it shows the night
  sky under the drawn map (a finished bake of the look stands in only when it covers
  `STANDIN_COVER` 0.9 of the view, or the image on screen until now still covers it: a 245 px
  strip over the wheels read worse than the dark); the image fades in over the sky when it
  lands (`city_bake_fade` 0.35 s; at once headless and under reduce effects). A bake is asked
  for only after the camera has held still `BAKE_SETTLE_FRAMES` (3) frames (a fit's passes no
  longer each start one: the route asked for a 1792x1152 bake at frame 0), and a view that a
  running bake will cover waits on it (`CityBakeCache.find_pending`). On a baked city a map's
  fit passes measure at once under the new camera (`update_camera` places it), instead of one
  redraw per pass all inside the first frame. Prebakes: the HQ page bakes the Grid's last
  framed region (view memory per campaign) and works out its placement and routes; the route
  bakes the default frame (the Modem, event and loot backdrops and a fight's arena, at the
  scene's and the page's sizes and the sizes that frame was last drawn at); prebakes wait for
  the city's own view (they took the build slot first: the raid setup sat 3.5 s on the sky).
  **Builds are sliced**: a painter's lots run in `BUILD_SLICES` (12) slices plus the fist roads
  on the worker pool at once, joined in draw order without copying (the chunks are handed to
  the renderer from the slices' own arrays, `SUBMIT_BUDGET_USEC` 6 ms a frame); triangles are
  pushed one by one (`append_array` of a literal Array built a temporary per triangle: 4.5 s ->
  2.1 s for a 1280x720 build before slicing). Measured (after vs before):
  - first Grid (`--demo-grid`): nodes 32/32 on frame 1 (before: 0/32 until the bake, 4.0-4.2 s
    by the reviewers; within 300 frames here never); the city covers the view ~1.4 s after
    the first frame (a 2176x1536 region, 5.4M vertices: lots 60 ms, slices ~0.8 s, submission
    ~0.4 s); the landing frame under 50 ms (before 97-120 ms);
  - the Grid opened from the HQ page (`--demo-grid-open=150`): its frame 161 ms (before
    204 ms, and that drew no node), the HQ page back 113 ms (140), the re-open 96 ms (141;
    the reviewers' 325-340 ms);
  - route (`--demo-run`): 15/15 nodes on frame 1 (before 0/15 for its whole visit); a fight
    entered 1.4 s after it has its arena ~1.0 s after entering (before ~2.9 s here, ~5 s by the
    reviewers), dark sky meanwhile, never a strip;
  - raid setup after a claim (`--demo-raid`): 3/3 nodes on frame 1, covered 1.3 s in (before
    3.5 s; not within 300 frames here);
  - the only frames over 50 ms are a scene's first two frames (its page build: 150-205 ms,
    before 170-210 ms) and a page switch's first frame (Grid open 161 ms, a fight's page 177 ms).
  The jack lands once the page and its placement are there (`arrival_ready` no longer waits for
  the image): the arrival wait fell from ~3 s to the CONNECTING line's 0.35 s.
- **ANIM-R1 M2 corrected:** "the ~0.5 s the bake now takes" was wrong: measured, a map view's
  bake took 2.4-4.2 s on its worker thread then (the 3.5 s raid setup, the 4 s first Grid); after
  R1 1.0-1.5 s, and the map is drawn meanwhile.
- **R2:** the arena is covered by R1's rules (no strip stand-in, the backdrop prebake, the view
  bake ahead of prebakes); tested by `test_a_partial_stand_in_never_shows` and measured above.
- **R3: the jack blocks input first.** `_input` reaches nodes in reverse tree order, so Fx (an
  early child of the root) saw a press after the scene's own handlers. `JackInputGate` is added
  last under the root and moved back behind any node the root gains (the arriving scene), so it
  sees every event first; while a jack runs it stops each (but pointer motion). Tested with
  `get_viewport().push_input` through the real propagation, a node added under the root after
  the jack started included. Main's `MotionSkip.is_press` also returns false during a jack.
- **R4:** the `print("SBDBG ...")` on every bake request is gone. Rule (test_suite_integrity):
  scripts/ may only `print("<tag>` a frame-capture marker the strip tooling reads (`anim4: `,
  `anim4b: `, `anim5: `, `MotionDemo: `); any other print, prints, printt, print_raw, print_rich
  or print_debug under scripts/ fails. tools/ and tests/ may print.
- **R5:** "CONNECTING TO <SITE>" (the run's Site, translated; HQ on the way out; "the net"
  without a run) and a bar filling over `jack_arrival_wait` show on the opaque cover, whole at
  once, at least `jack_connect` 0.35 s (to be read), and lift with the cover. Reduce effects:
  the words on the black fade, no bar. Cap as before (4 s).
- **R6: raids at map scale.** Threat tokens x3.0 (was 2.2), a white diamond ringed in red on a
  dark keyline with the corporation's colour as a dot (Solace's green threats were green on
  green), a fading red trail of 7 dots behind a moving one. A step's beats set off 35 % of the
  way through its camera ease (`FRAME_WAIT_SHARE`; they waited all of it) and a step with no
  beats is not framed at all. The end's outcomes stamp node after node (`raid_outcome_stagger`
  0.3 s each, 0.12 s apart, home last) and a "HOME -5" / "HOME HOLDS" banner stamps over home
  (`raid_result_banner`) and stays. The log is a 330x150 strip that follows its newest line (it
  was 330x330). A deployed asset waits for the camera to settle (at most 1.5 s), drops, stamps a
  x2.4 ring (`asset_drop_stamp` 0.35 s) and keeps its name under its marker. The step skip now
  uses `_input` with `MotionSkip.is_press` / `consume`; a click on a button (the panel's or any
  under the pointer) and accept on a focused panel button stay the buttons'.
- **R7:** the spreading front's band at 0.9 (was 0.5), and the district it crosses keeps a
  lasting tint in the new owner's colour (`influence_tint` 0.3 alpha, faded in 0.6 s after 0.2 s)
  until the next change; with no spread (headless, reduce effects) the tint is the end state.
  The CLAIMED stamp and the SITES counter's bump stay.
- **R8: the Heat crossing in order.** Per threshold crossed going up: the number rolls to the
  threshold (`number_roll`), the "HEAT 25 - NOTICED" banner stamps, the poster distorts briefly
  round itself only (`Fx.heat_pulse_at`, `heat_pulse` 0.3 s, was 0.45 s full-screen), the letters
  shake; the next threshold after it; then the number rolls on to the Heat. No corporate
  wireframe creep on a crossing any more (it lingered and read as a display fault). **Decided:**
  a multi-band jump shows one banner per band crossed, in order (the DECISIONS line "one per
  crossing" and the code now agree); a drop across a band re-stamps the band word only (no
  banner, no distortion). The banner's lettering follows the text size and shrinks until the
  tilted banner fits the poster (to 8 px; French-length words ran 8-9 px past it at 18 px).
- **R9:** the Grid re-open is back under 150 ms (96 ms): a map's roofs, icons and labels are
  worked out once per frame change (`CityMapOverlay._frame_cache`, the label layout keyed by
  what it reads), the labels are a layer of their own (a sliding column redraws only them),
  the node and label layers draw at most once a process frame, a motion value (the selection's
  draw-on, a drop, a move) redraws only its layer (`MotionValues`), street routes are kept per
  placement, and a bake landing no longer re-lays the map (its placement did not change).
- **R10:** `CityBakeCache.shutdown()` (Fx on exit and on the window's close request) stops every
  running build (slices included), joins its worker tasks, frees its painter, slices and
  viewport and drops the queue and every texture; `clear()` lets go of every texture (tested
  with weak refs).
- **R11:** one bake builds at a time (`MAX_BUILDING`, the rest queue, a view's own bakes ahead
  of prebakes): geometry memory is bounded to one region's. A painter copies the influence
  (`_twin`). A painter no longer draws the live layer (signs, window lights) into its image: the
  synchronous path did, so the two paths differed; `tools/design_lab/bake_compare.gd` (real
  display) now finds the sliced threaded GPU-copy bake pixel-identical to the synchronous one on
  three regions (solace 1792x1152, rebel_cell 2048x1536 with signs and the fist, meridian
  2400x1500: 0 pixels differ).
- **R12:** the move's trail is a 7 px acid line with a white core over a dark keyline (it was a
  row of small dots) and the node it heads for pulses (`route_target_pulse`). The choice labels
  move to the new next nodes when the pulse lands (M7, seen in the live route). **Decided:**
  equal choices (the same kind, Heat and nodes beyond: the enemy is rolled on entry) are
  genuinely identical, so they say so: "(same as 1)" on the button and on the map label.
- **R13 (1.6):** the raid setup's key is the Grid's folding strip at `MapLegend.FOLD_SCALE` and
  up (Y opens it, as on the Grid); compact dossiers put the class tags beside a half-size
  Polaroid so the whole dossier and its Loadout are on the first screen; SAVED keeps off the top
  bar's captions. The route key sits under the ROUTE window in its own room (checked at 1.6).
- **New ids (data; REQUIRED_IDS and the lab):** `city_bake_fade`, `jack_connect`,
  `raid_outcome_stagger`, `raid_result_banner`, `asset_drop_stamp`, `influence_tint`,
  `route_target_pulse`. Retuned: `heat_pulse` 0.3 s.
- **Expectation changes:** `test_anim_r1_campaign` (a beatless step is not framed and beats set
  off at 35 % of the ease; the Heat banner comes after the roll and names the threshold),
  `test_horizontal_pass21_city` / `pass22_city` (the labels' own redraw hooks).
- **Input helpers that must check `Fx.transitioning()`:** `MotionSkip.is_press` (done on main),
  and so everything built on it (DropLayer carry and drops, PageTransition / Typing / MenuMotion
  / FlightFx / Dialogue skips, the combat replay skip, the netrun route travel skip, this
  playout's step skip). The gate already stops their `_input` during a jack; the check is the
  second line of defence for code that reads Input directly (`Input.is_action_just_pressed` in
  `_process`), which the gate cannot stop.
- Strips (`docs/timeline/motion/`, recaptured, quantized, raw frames deleted): `raid_playout`,
  `influence_spread`, `heat_pulse`, `jack_in`, `route_pulse`, `asset_drop`.

#### 2026-09-28 — Animation pass — ANIM-R2 combat, events and screens
The second fix batch of the Animation pass review (four reviewers), combat, events and
screens part (E1-E10). Views only; every call below was the implementer's (the standing
rule: nothing deferred). Tests: `tests/unit/test_anim_r2_combat.gd` (full tier, 28 tests);
strips recaptured in `docs/timeline/motion/` (CHOSEN on top, one variant under it, quantized):
`resolve_sequence`, `number_float`, `enemy_break`, `drag_ghost_follow`, `loot_pick`.
- **One press rule, revised (MotionSkip, STYLE_GUIDE 5.1).** (a) *Menus pass their own
  presses (E3):* in a MenuMotion menu a focus move, an accept (ui_accept: Enter, Space, pad A)
  and a click on one of the menu's lines complete the line's motion **and pass on**; only
  presses that don't work the menu are consumed (`MenuMotion.works_menu`). R1 consumed every
  non-focus press while a line typed, so Down then Enter the next frame never activated and a
  click on another line within 0.18 s was eaten. (b) *Words together (E2):* a press that
  completes typing shows every word typing on screen at once — all `Typing` labels and the
  Dialogue subtitle (`Typing.finish_all`, from both helpers) — so an event's story and its
  subtitle take one press, not two. (c) *Under the jack:* `MotionSkip.is_press` is false while
  `Fx.transitioning()` (looked up at run time: the kit compiles in `-s` tools), so no helper acts
  under the jack's cover (the other agent's input blocker swallows the press itself).
- **E1 pad-only events.** Held choices are no longer disabled: they stay enabled and
  focusable, so the entrance's focus lands on the first choice; a press on a held choice only
  shows the words (`_press_choice`), and when the words are whole the choices are released and
  the first takes focus if nothing on the page has it. Tested with the pad alone: A shows the
  words, the D-pad walks the choices, A takes one.
- **E2 held choices read.** A held choice keeps its paper note and outcome icons, its words at
  ink 0.7 and a "typing" mark (`EventHeldMark`: three paper dots just above the note's top-right
  corner, in the gap between choices, so never on its words). Root cause found on the way:
  `OutcomeRow` read the button's boxes before the button was in the tree, so it copied Godot's
  default grey boxes and **every event note had lost its paper** since R1 (disabled or not); it
  now reads them once the button is in the tree and again on a theme change. At 1.6 the top bar
  wrapped onto two rows because of the event's long title: the event screen is now titled
  "TERMINAL EVENT" (as short as the Modem's), so the bar keeps one row and the choices show.
- **E4 SEND IT reads.**
  - a. Hits play one at a time: after a beat that flies (a hit, a status put on a slice) the
    next waits `hit_line` (0.3 s; never squeezed), so two projectiles never fly at once. Every
    hit flies — a fully blocked or evaded one too (R1 drew none; the stamp now lands on impact),
    since who hit whom is the point. The projectile is thick (`hit_line` 6 → 8 px, a dark
    outline), leads with an arrowhead, is coloured by side (`PLAYER_HIT_COLOR` acid for the
    operative and its drones, `ENEMY_HIT_COLOR` red for enemies and satellites; R1 used the
    wheel colour, pink like the ATTACK slices), and the hit's raw number rides beside its head.
    The impact is at half its time (`CombatFxLayer.LINE_DRAW_SHARE`); numbers, stamps and
    satellite HP land then.
  - b. Numbers add up: a partly blocked hit lands its raw number ("-14"), the guard's part comes
    off as a chip under the hub's lines ("5 BLOCKED", existing words) and after `hit_absorb`
    (new, 0.3 s) the number pops to what got through ("-9"), which is what travels into the HP
    counter. A satellite's or drone's HP change now shows at its own token (in the hub it read as
    the host's HP, which didn't move: the likely source of "−14 → 21 lost", a drone and the
    wheel both hit). The "−6 with +3 block → 6 lost" still: the +3 BLOCK was the collections
    drone's own guard (a satellite guards itself), not the agent's; the hit took 6 as shown. No
    demo was wrong. Rule tested over 4 enemies × 6 seeds × 4 turns: every HP change has exactly
    one number of exactly its size, and each wheel's (and satellite's) numbers sum to its HP roll.
    Overkill: the raw number can exceed what got through plus the guard (the HP ran out); the
    travelling number is still the HP lost.
  - c. The result waits for every HP roll to finish (`ResolveBeats.settle_after`: impact,
    absorb, the number's travel, `hp_drain`), then THIS TURN holds `resolve_result_hold`
    (0.5 s) before the respin. The squeezable gap still fits `resolve_sequence` (2.0 s) beside
    the lead, hold, deaths and tail; the hits' spacing and the settle come on top, so a turn with
    hits runs about 2.5-3.5 s (any press skips). Test budgets changed on purpose (below).
  - d. The forecast tag's tape reads "IF YOU SEND IT" (before and after a resolution: the
    forecast always means what SEND IT does now); "NEXT TURN" read as "not this turn" and is
    gone from the tag (the word is dropped from the export).
  - e. The landing beats are at 0 with the discard alongside (checked in the capture: the
    landed slices pulse from the first frames); unchanged.
  - f. `result_stamps` stamps NO DAMAGE / ALL BLOCKED only on a wheel that took **no** HP-changing
    beat: damage and an equal heal net to zero but no longer say NO DAMAGE.
- **E5 the break.** The full-screen acid flash at VICTORY is gone: the breaking wheel gets a
  short local white disc flash (`victory_flash` retuned: amplitude 0.3 → 0.8, now the disc's
  alpha, 0.15 s) drawn by the fx layer (the wheel itself goes clear as it breaks). VICTORY lands
  centred over the enemies' side (`end_word_spot`), DEFEAT over the operative. When the fight
  ends on a break, the result (THIS TURN, NO DAMAGE on the operative) shows `enemy_break`'s
  delay before the last break, then the break and VICTORY.
- **E6 the Modem at big text.** Chip and Daemon tiles grow until their whole effect text fits
  at 10 px or more (`fit_chip_tile`: wider first — a microchip up to its window's share, a
  Daemon by a quarter of the text scale's growth — then taller, up to the lower row's tile
  height), measuring with the BUY sticker refitted at each width (its second line was the
  foot the old fit missed). Swept: seeds 1-6 × English and pseudolocalised × 1.0 / 1.3 / 1.6,
  every tile whole (was 14 of 72 at 1.6). A slice tile shows one price, what most slots cost
  ("BUY 100", not "BUY 100-150" wrapping onto three lines); the UPGRADE viewer shows the exact
  price of the slot picked before anything is paid and the tip names the pricier slot.
- **E7 big text combat.** The entering enemy's name plate shows only when it has no forecast
  (the tag slides in with the wheel; the name is in its hub). At big text (one chip row) the
  chips shrink down to their 1.3 size before any fold into "+N MORE" (`chip_font`); the fold
  order stays R1's (damage to you, dealt, HP, the rest), so what folds is odds and statuses.
  Satellite tokens dock past the slice value at their angle (the value's box is wider than
  tall: `satellite_out(a)`, two digits, the token's radius, a 3 px gap) and turn round the rim
  away from the top when they would sit on the tag (`SAT_TAG_STEP` 0.06 rad, at most 16).
- **E8 loot.** The stickers keep their rest tilt's reach apart (`ZineCard.REST_TILT_MAX` 4°:
  the gap is 14 px plus the card's height × sin 4°; CACHE lay on JAM's cost badge). A focus tip
  shows only when a key or pad moves focus (or pad mode is on), never on the page's own first
  focus for a mouse player; when every spot covers something the tip is folded narrower (0.7,
  0.5, 0.35 of its columns, at least 16) and may go to the screen's side margins, the spot
  covering least wins (at 1.6 a middle card's tip now sits clear of Skip and the other cards).
  The half-drawn band on loot_pick's first frame was the glass entrance's CRT roll firing while
  the page was still clear: the roll now comes once the glass is fully shown.
- **E9.** A long refusal note takes its size again a frame later (a wrapped label reports its
  height late: "…has no f"). A drop on a target that only picks (the crew chip on JACK IN) lands
  beside the button, never on its words (`DropLayer.LAND_BESIDE_KINDS`, left of it, else right).
  The drag ghost's alpha 0.6 → 0.92 (`drag_ghost_follow`). The Modem's wallet mirrors the top
  bar's CYCLES and redraws on its roll steps (`HudStats.mirror`, `rolled`): a redraw asked from
  _process drew the step before (the 119 vs 120). Spent RAM floats "-N RAM" off the count
  (`ram_spend_float`, new: 0.8 s, 22 px) on respins, card plays and extra nudges. A purchase
  refused for want of Cycles (a drag, the rules' refusal, or a click / A on an item out of
  reach) flashes the top bar's CYCLES tag and the wallet red with "PRICE > CYCLES"
  (`price_refusal`, new: 0.6 s, 2 pulses; static until the next change with motion off). The
  preview chip reads "PLAYING JOLT" (was "IF JOLT").
- **E10.** `combat_fx_layer.gd`'s inline fractions are named: `GROW_FROM` 0.6, `CRIT_POP_SCALE`
  1.35, `TRAVEL_FADE_TO` 0.6, `LINE_DRAW_SHARE` 0.5, `RIDE_FONT_SHARE` / `RIDE_OFFSET`.
- New ids (data only; REQUIRED_IDS in `scripts/data/ui_motion_data.gd` — a constant list, no
  field changed, the schema smoke test reads it — and motion lab demos): `hit_absorb`,
  `ram_spend_float`, `price_refusal` (164 entries). Retuned: `hit_line` width 8, `victory_flash`
  0.8 (local), `drag_ghost_follow` alpha 0.92. The lab's `number_float` demo plays two real hit
  beats (a partly blocked one), and `--demo-scale=<x>` on the netrun scene captures at a text
  size.
- Words (exported once, strings.csv): IF YOU SEND IT, PLAYING %s, -%d RAM, TERMINAL EVENT;
  dropped: NEXT TURN, IF %s, TERMINAL EVENT & DISPATCH.
- Test expectations changed on purpose: `test_anim_r1_combat` (a blocked or evaded hit flies;
  hit colour by side; the budget allows the hits' spacing and the settle; a fight ending on a
  break shows its result before the break), `test_anim2_combat_motion` (the same budget),
  `test_anim_r1_campaign` (held choices are held, not disabled), `test_horizontal_pass24`
  (PLAYING JOLT).

#### 2026-09-28 — Animation pass — ANIM-R1 combat and input
The first fix batch of the Animation pass review (four reviewers), combat and input part
(C1-C10). Views only, except two facts added to engine events (C4). Tests:
`tests/unit/test_anim_r1_combat.gd` (full tier); strips recaptured:
`docs/timeline/motion/resolve_sequence.png`, `number_float.png`, `enemy_break.png`
(chosen on top, one variant under each; README rows marked ANIM-R1).
- **C2 One press rule.** New kit class `MotionSkip`: `is_press` (a key going down, not an
  echo; mouse buttons 1-3 going down, never the wheel's scroll buttons; a pad button going
  down) and `consume`. The rule: *a press that completes a motion is consumed and does
  nothing else*. Applied in every helper that ends its motion on a press: the combat
  replay skip, DropLayer (it used to finish its flights and let the press act: a pad B
  during a shred landing closed the viewer and then left the Modem), FlightFx (mouse
  clicks now complete flights too), MenuMotion, Typing, the Dialogue subtitles,
  PageTransition and the netrun's route move (moved to `_input` so no button sees the
  press first; pad buttons skip it now). Decided exceptions: in a menu, a focus move
  (arrows, D-pad, Tab) completes the line's motion and is let through, since moving on
  ends it anyway and a menu must never drop a fast tap; the Dialogue subtitles follow the
  rule too (a line types for about a second; the press only shows it whole), accepted for
  one predictable rule. A second motion running on another layer at the same time needs a
  second press (each helper consumes the press it completed).
- **C1** `_perfect_feedback` shows the end state when `precision_perfect` isn't live
  (reduce effects, headless, entry off): no inversion, flash or freeze (headless used to
  call `Fx.freeze_frames`).
- **C3** `WheelView.stop_motion` also settles the kit's one-shot helpers on the view (the
  Partial shake, the Miss blink; the migration flicker is the scene's loop and stays) and,
  on a skip, takes the tag's content as shown so it lands without a flip;
  `motion_busy()` counts those helpers. Only a replay that plays out flips the tags in.
- **C4 Beats for every combatant.** `satellite_spawn` and `deploy` events now carry the
  newcomer's `hp`; `boss_phase` carries `spawned` ([{id, hp, slot}]) and `ticks` (its
  needles after the phase). Values the resolver already had; results, hashes and
  replays unchanged (engine events aren't part of any hash). `ResolveBeats` seeds those
  HPs, makes `spawn` and `phase` beats, sets HP 0 on `died` (satellites going down with
  their host get no damage event), and marks a whole wheel's death (`wheel`). Tested for
  every enemy in content (two seeds, six turns, cards played): the beats end on every
  combatant's HP, drones and satellites included. On the replay a satellite's token goes
  on its death beat, a launched satellite or deployed drone docks on its spawn beat, a
  boss phase stamps PHASE N (with its alarm and flash, moved from the state change to the
  beat) and MULTIPLY's needles fan out; satellite HP plates follow their beats.
- **C5 The SEND IT replay's legibility** (only the engine's own events):
  - a. Landing: the landed slices pulse in their colour (`landing_pulse`, 0.3 s, keeping a
    0.35 glow until the wheel turns on), a MISS slice gets a big grey X, and nothing
    resolves for `resolve_landing_hold` (0.3 s).
  - b. Hits: a thick projectile (`hit_line` width 3 → 6 px, with a bright head) in the
    attacker's colour from its landed slice (`source_slot` on the beat) to the victim's
    HP ring where its HP ends; none when nothing is dealt: a fully blocked hit stamps "N
    BLOCKED", an evaded one "EVADED N" (existing words) at the victim (`result_stamp`).
  - c. Numbers: HP changes (damage, heals) sit above the name, guards (block, shield,
    evade, what a partly blocked hit's guard soaked) under the hub's lines; each is sized
    so every corner stays inside 0.9 of the hub (at 1.6 they spilled over the slices) and
    never over the hub's words; a new number in a band sends the resting one on (never on
    each other). A damage or heal number holds 0.22 s, then travels 0.22 s into the HP
    counter (`number_to_hp`, arrives at x0.5); the HP rolls down with the white lag bar
    as it arrives and a loss flashes the disc (`hit_flash`) and shakes the wheel
    (`hit_shake` 3 px; none under reduce effects, where nothing replays).
  - d. A wheel whose HP the resolve didn't change stamps NO DAMAGE, or ALL BLOCKED when it
    was hit and nothing got through (new words), in its hub above the name.
  - e. After the beats the result holds `resolve_result_hold` (0.5 s) under a THIS TURN
    plate where the tag goes (new word), with LAST TURN sliding up then (it used to slide
    up after the spin); only then do the wheels spin to the next landing. The next turn's
    forecast (tags, NEXT plates) is withheld while the replay runs and flips in at its
    end; the tag's tape now reads NEXT TURN (new word). The status line's TURN counter
    shows the turn played until the replay ends. A skip puts the forecast on at once,
    without a flip.
  - f. A wheel's death waits for its HP to be seen at 0: the killing number's travel, the
    HP roll (`hp_drain`) and `enemy_break`'s new delay (0.15 s) come first. After the
    break a beaten enemy's view is its empty spot (dashed rings, its name, a red DEFEATED
    stamp; new word), during the replay and after it. A new fight's enemies enter from the
    right edge with their name on the tag's plate (`enemy_enter`, 0.35 s, 260 px), so a new
    enemy on the same view never reads as the beaten one coming back.
  - g. `resolve_sequence` 1.45 → 2.0 s (the beats' gap is squeezed to fit, as before).
    Variants shown: 1.6 s with holds 0.15 / 0.3 s lost the result before it read. A turn
    that kills a wheel and goes on (another enemy still up) can run to about 2.4 s: the
    HP-at-0 wait is not squeezed (tested budget: single-enemy fights).
- **C6 RAM refusal**: the RAM chips flash red and "COST > RAM" (e.g. "3 > 2") shows beside
  the count with a drawn RAM chip, pulsing (`ram_refusal` 0.6 s, 2 pulses); the refused
  card's cost circle pulses red, a refused respin pops the respin sticker
  (`ram_refusal_pop`). With motion off the red shows until the next RAM change. The
  toast stays.
- **C7 SEND IT's mark**: a drawn ▶▶ by its key hint (no layout change); it pulses gently
  (`send_it_ready`, x1.18 over 0.6 s each way) while no RAM is left; still under reduce
  effects.
- **C8 Chip order**: chips carry a rank (damage to you, damage dealt, HP, the rest) and are
  sorted stably; the fold keeps that order (rows fill in order, the first chip that no
  longer fits and all after it fold into "+N MORE", room for which is kept), so at 1.6 the
  damage chips always show.
- **C9 Inline numbers moved** (data only): `victory_flash`, `boss_phase_flash` (the three
  `Fx.flash(..., 0.3)` calls), `drag_ghost_tilt_speed` (1200 px/s), `ram_refusal` (the
  0.6 s flash), `toast_note_hold` (3.5 s, read raw: reading time is never sped up or cut),
  `stamp_fade_in` (FlightFx's 0.5 share), `send_it_drips_share` (the drips' 0.5 split).
  `UiMotionEntryData`'s doc comment now lists every amplitude unit in use (px, scale,
  alpha, degrees, frames, ticks per second, tenths of a tick, a seconds cap, shares, px
  per second, counts); STYLE_GUIDE 5.1 too. Comment-only change in `scripts/data/` (no
  field changed; the schema smoke test is unaffected).
- **C10 Menu typing is drawn**: `MenuMotion` no longer rewrites `Button.text`; the line's
  font colours go clear while the menu draws the typed part on top, so the text stays
  whole for screen readers and tests and nothing re-lays out.
- New ids (18, REQUIRED_IDS and motion lab demos; 152 entries): `resolve_landing_hold`,
  `landing_pulse`, `resolve_result_hold`, `result_caption`, `result_stamp`,
  `number_to_hp`, `hit_flash`, `hit_shake`, `enemy_enter`, `victory_flash`,
  `boss_phase_flash`, `ram_refusal`, `ram_refusal_pop`, `send_it_ready`,
  `send_it_drips_share`, `drag_ghost_tilt_speed`, `toast_note_hold`, `stamp_fade_in`.
  Retuned: `resolve_sequence` 2.0 s, `hit_line` 6 px, `enemy_break` delay 0.15 s. The
  lab's SEND IT capture now nudges the operative's wheel until the preview hits
  (`send_hit`) and `send_kill` starts the enemy at 3 HP (lab only).
- Words added (translated once; strings.csv exported): NEXT TURN, THIS TURN, NO DAMAGE,
  ALL BLOCKED, DEFEATED.
- Test expectations changed on purpose: `test_anim6_screen_motion` (menu typing: the
  line's text stays whole while `typed_count()` grows; a key press completes the typing
  and the slide together).

#### 2026-09-27 — Animation pass — ANIM-R1 campaign and screens
The first fix batch of the Animation pass review, campaign and screens half (items M1-M16
of the four reviewers). Views only, but for one rule (M1). Every decision here was the
implementer's (the designer's standing rule: nothing deferred). Tests:
`tests/unit/test_anim_r1_campaign.gd` (24); strips: `docs/timeline/motion/` (README rows
marked ANIM-5 / R1).
- **M1: one jack, one run, one scene change.** `CampaignRules.launch_error` takes
  `run_in_progress` and refuses ("A run is already in progress: finish it first.");
  `RunManager.launch_error` passes `has_active_run()` (pure rule, tested). `Fx._transition`
  ignores a jack asked for during one; while a jack runs its cover takes the mouse and
  `Fx._input` swallows every press. `RunManager.scene_change_pending()` (= `Fx.transitioning()`)
  guards `go_to_netrun` / `go_to_hq` / `go_to_title`, `hq_scene.launch` / `resume` and the
  netrun's Save & quit and Go to HQ; `change_scene` asks once per frame. A run saved and left
  (Save & quit goes to HQ) used to be overwritten by the next JACK IN; now the rule refuses
  that and the HQ's JACK IN stamp goes back into the saved run instead of opening the Grid.
- **Designer ruling (2026-09-27, "prefer select, then jack in"), applied:** a crew chip
  dropped on a Site card's JACK IN picks that operative in the list (`pick_operative`, focus
  on JACK IN); only the press launches. `test_anim4_drag_drop` changed on purpose (the drop
  starts no run; the pick then the press starts the same run as the list and the button).
- **M2: no bake freezes the raid flow.** A bake's geometry (seconds of GDScript) is built on a
  `WorkerThreadPool` task before the painter enters the tree (`NeonCity.prebuild`), submitted
  CHUNK_VERTS (240,000) vertices a frame (`submit_chunk`: one `canvas_item_add_triangle_array`
  of 4M vertices took ~190 ms), rendered once, and copied on the GPU into a `BakedTexture`
  (`Texture2DRD`; the readback and upload took ~60 ms; the Compatibility renderer falls back
  to the readback). Each chunk draws in order under the painter with its sketch material; a multi-chunk bake is pixel-identical to the old path (compared on a 1536x1024 region, threaded + GPU copy vs the synchronous readback). The raid setup bakes the
  playout's whole area behind itself (`_prebake_playout`, every node as the fight's focus at
  the widest fight zoom) and START DEFENSE bakes the post-raid look while the raid plays (the
  pre-raid one stays pinned), so the result spreads at once. `profile_frames.gd --timeline`
  (1280x720, `--demo-raid --demo-playout-delay=300`): before, max 1894 ms at the playout's end
  and 80-97 ms at its first frame; after, nothing over 50 ms but the scene's first two frames
  and the START DEFENSE press itself (65-70 ms: the raid resolves and the page builds, before any
  motion). Trade-off: a camera that leaves every baked region shows its stand-in (or the sky)
  for the ~0.5 s the bake now takes in the background instead of freezing for it. (ANIM-R2:
  wrong, measured 2.4-4.2 s then; see "ANIM-R2 city, maps and transitions".)
- **M3: switched-off entries.** `Fx.jack_in` / `jack_out` (switch at once), `heat_pulse`,
  the creep, `show_saved` (shown still for its hold and fade time, then gone at once) and the
  map's selection ring gate on `Motion.live`. The inline halves became entries:
  `jack_arrive` (the reveal, 0.4 s; `jack_in` / `jack_out` are now the 0.4 s push: 0.8 s in all
  as before; its amplitude 0.15 replaces JACK_ARRIVE_SHARE), `net_creep_recede` (0.6 s; `net_creep`
  0.6 s), `jack_fade_reduced`'s amplitude (0.5: the share spent going dark), the raid hit (it
  lands when the trace arrives, M4) and `select_ring_pulse` (3 px over 1.571 s, the old 4 rad/s).
- **M4: raids read at fight scale.** Each step first eases the camera to its fight
  (`RaidBeats.focus_sites`: where threats enter and move, the guns firing and their targets,
  the nodes hit; `WireframeBackground.frame_points` fits them into the map's free part beside
  its key, zoom 1.2-1.9 at HQ, 0.85-1.6 in a run) and its beats wait for the ease; the camera
  never cuts. A shot is strictly shot, hit, number: the trace flies to the threat over
  `turret_trace` from a ringing gun, the hit lands on arrival, the damage rises after it, and
  a threat breaks up only after its killing hit. Tokens 2.2x (was 1.5x), stamps 21 px (was
  14), numbers 28 px, traces thicker; threat routes carry chevrons pointing home (the Cell's
  links stay solid); placed defences stay on their node as map-icon-size markers. Each hit on
  home flies its red number into the top bar's HOME (`home_number_fly` 0.55 s after 0.15 s),
  which rolls down (the bar shows the value before the raid while it plays); the end is the
  resolved raid (tests unchanged and green).
- **M5: territory changes leave marks.** After a change spreads, each Site that changed hands
  keeps an outline and a tint and a CLAIMED / CLEARED / SEIZED / DISABLED stamp on a leader
  (`InfluenceSpread.marks`, `influence_mark` 0.3 s after 0.6 s, from 1.6x), on the city and over
  the map (under nodes and labels), until the next change. The CELL STATUS gains a SITES n
  badge (claimed Sites besides CORE): it bumps when a change lands (`territory_marked`).
- **M6: the Heat crossing on the number.** `heat_pulse` 0.45 s at peak 0.25 (was 0.7 s at 0.5;
  strip variants 0.5 / 0.25 / 0.15 now differ frame by frame). The poster's number rolls from
  the Heat last seen (`number_roll`), grows and flashes white on a crossing (`heat_number_pop`
  1.6x, 0.4 s), and a "HEAT 30 - NOTICED" banner stamps across the Heat block, holds 1.4 s and
  fades (`heat_banner`); one per crossing, nothing stays on.
- **M7: the route after a move.** When the pulse lands the map takes the run's new state (the
  [1] / [2] labels on the new next nodes, the edges out of the new node live); a node passed
  through is drawn at `visited_dim` with a tick, apart from the unreachable dim.
- **M8: the jack lands on a built screen.** After the switch the cover stays opaque, its
  scanlines rolling, until the new scene's `arrival_ready()` (a page on screen, the whole view
  drawn from a finished bake of the current look, the camera settled, no fit, legend or map
  framing pass waiting), at most `jack_arrival_wait` (4 s of game time; a bake of a whole
  Grid takes ~3 s on its worker thread). Same for the reduced fade. The mid-run raid
  interlude, a dark page of text before, is now a window beside the raid's map on the city
  (the Grid and the threats' routes, framed into the free part): a jack into it lands on the
  setup with its map.
- **M9: the event's words first.** While the story types in, its choices are disabled (shown so)
  and a press completes the typing (Typing's own rule: no skip handling of ours); the choices act
  once the words are whole. Outcome rows wrap inside their choice (six items at 1.6 ran past it).
- **M10: whole text.** Shop and loot cards (`ZineCard.fit_whole`) shrink the body, and chip tiles
  their icon (to 0.3) and then the lettering (to 8 px), until the whole description shows; the
  focus tip stays. A long refusal toast wraps inside the screen. (The raid dispatch's typing is
  the input agent's.)
- **M11: the Modem keeps its places.** A bought item stays as a SOLD stub (dimmed, stamped, no
  button) in its place for the visit; the others keep their spots and colours (`shop_slots`).
  The loot offers not taken fall away (`loot_reject` 0.45 s, 240 px) as one is picked. The loot
  fans from inside its row (it crossed the Skip bar at 1.6) with a gap above Skip. Focus tips go
  where they cover no button, tag or title (`FocusTip.spot`). The cyan band on loot_pick's first
  frame was the page roll band spanning a page of windows: it now crosses the windows only
  (`PageTransition.GLASS_META`, set by both scenes for pages over the city).
- **M12: HQ at 1.6.** SAVED keeps off the top bar's tags; a compact dossier shows HP right under
  the name; the Schematics icon sits right after "pay 25".
- **M13:** see the resolved open question: a focus label searches round its node (16
  directions out to LABEL_REACH), then takes a spot clear of other icons (one word a line, then
  cut short with an ellipsis), else is left out (the Site card names it); only YOU ARE HERE and
  threat tags may still cover an icon. The sweeps assert it in the late campaign and for every
  selected Site.
- **M15 (the full-suite hang):** not reproduced (20 runs of `test_horizontal_pass23_screens.gd`
  and 3 full suites pass after the fix; before it, the loops were reviewed). Loops that
  depend on measured geometry are bounded now: the raid map's framing per page
  (RAID_PASSES_MAX, RAID_CHECKS_MAX: a free rect that kept changing reset the per-layout count,
  each pass a new camera and city build), `LegendSpot.place` (maxf / minf with NaN never ended;
  at most SPOTS_MAX spots an axis), route dashes and lure dashes (DASHES_MAX, finite lengths),
  face hatching (HATCH_STEP_MIN) and the SAVED spot search (finite, SAVED_SCREEN_MAX).
- **M16:** the Heat poster's ransom strips close up (to 14 px a letter) so the number and
  "/100" stay on it with a long or pseudolocalised word. The SEND IT lettering's cut under
  pseudolocalisation is the combat agent's (drip_button.gd).
- **SAVED:** two saves in one frame each started a fade; the first one's now dies with the second.
- **New ids (data only; REQUIRED_IDS and the lab):** `net_creep_recede`, `jack_arrive`,
  `jack_arrival_wait` (4 s), `select_ring_pulse`, `loot_reject`, `home_number_fly`, `influence_mark`,
  `heat_number_pop`, `heat_banner`. Retuned: `jack_in` / `jack_out` (0.4 s push), `net_creep`
  (0.6 s, OUT), `jack_fade_reduced` (amplitude 0.5), `heat_pulse` (0.45 s, 0.25).
- **Expectation changes:** `test_anim4_drag_drop` (the ruling), `test_anim6_screen_motion`
  loot pick (two loot_reject falls beside the pick), `test_city_map_sweeps` (labels clear of
  icons asserted in the late campaign and per selection).

#### 2026-09-27 — Animation pass — ANIM-4b: drag and drop in the run
The designer's "drag and drop anything", run side: every item a netrun moves between
places now drags there as well, with ANIM-4's kit and feel. Views only: no rule changed.
Tests: `tests/unit/test_anim4b_run_drag_drop.gd`; strips: `docs/timeline/motion/drag_buy_*.png`,
`drag_shred.png`, `drag_loot.png` (README rows marked ANIM-4b).
- **Same kit as the HQ.** `netrun_scene` owns a `DropLayer` over every page (reset when a
  page is rebuilt; flights in the air keep going) and wires it as `hq_scene` does: `check`
  = `drop_error`, which runs **the button's own rule call** on `dry_session()` (a
  `NetrunSession.from_dict` of the run with its RNG streams, over
  `campaign.duplicate_state()`: the real run and campaign are never touched) and reads its
  refusal; `dropped` → `_on_dropped` makes the same call the button makes. Refusal texts
  name content and Sites as the screens do (the rules speak in ids). Views that open over
  the page (the REMOVE deck viewer, the UPGRADE spinner viewer) get a layer of their own
  added **after** them by the scene (`_modal_layer`), so it draws on top and outlives the
  viewer (it frees itself when done, `DropLayer.retire`). A drop there makes the call the
  viewer's UPGRADE / REMOVE makes at once (the state is final), and the viewer closes as
  that button closes it **once the landing on its wheel or shredder has played** (a
  flight's `on_done`; at once headless / reduce effects; any press ends it): closing first
  left the copy squashing over the Modem page (first capture). Focus then lands on the
  Modem's first control.
- **What drags, and the button path each mirrors:**
  - Modem: a card onto the top bar's CARDS tag = its BUY; a Daemon onto the DAEMONS icon =
    its BUY; a microchip onto a slot of the new small spinner = "Socket into Slot N" in
    the socket list, then BUY (the list stays and aims the carry: a chip picked up with
    the keys starts on the listed slot); a slice upgrade onto a slot of the small spinner
    = the UPGRADE viewer's select that slot + UPGRADE (`overwrite_slice`, the call the
    viewer's UPGRADE makes). In the UPGRADE viewer the slice being installed sits beside
    the wheel (`InstallSlice`) and drags onto a slot = select + UPGRADE. In the REMOVE
    viewer every card drags onto a new SHRED tile beside Close = select the card + REMOVE
    (`remove_card`; pressing the tile is REMOVE too).
    A click on BUY keeps ANIM-6's SOLD + flight; a drag doesn't also fly (`_buy` /
    `_choose_reward` take `fly`), its copy lands on the target instead.
  - The **small spinner** (`SpinnerMini`, new kit piece) sits in the REMOVE A CARD window
    beside the wallet: the slots as wedges in their slice colours with their icons, a cyan
    square where a chip is socketed, SPINNER under it, each slot's pad tooltip named as the
    socket list names it. It is no focus stop (the carry's reticle reaches the slots).
  - Loot: a card onto CARDS, a Daemon onto DAEMONS, a Firmware chip onto a slot of the
    small spinner (shown beside a chip offer; the offer's row gives it its width) = the
    sticker's press (with the slot list's slot). Skip stays a button.
  - Event: a choice that hands over a card or a Daemon drags onto CARDS / DAEMONS = pressing
    the choice. No second place (logged, no drag): a Firmware reward goes on to the loot
    (where it drags onto its slot), an asset reward is carried until a Rack banks it (no
    place on screen), a rescued operative joins the roster at HQ; choices without an item
    are decisions, not items.
  - Mid-run raid interlude: the run's assets and the Armory's are chips (`RunAsset_i`,
    `Armory_i`) above the node rows; a chip onto a node's row = its row's "Deploy run
    asset" / "Deploy armory asset" with that asset picked; a placed asset's Withdraw drags
    onto another row (`raid_move` there) or onto the ARMORY chips (= Withdraw). The lists
    and buttons stay.
  - Not drags (why): the netrun's VIEW LOADOUT and the Daemon tray only show (no rule
    moves anything there); combat cards are ANIM-3's; the route moves the operative, not an
    item (ANIM-5's travel); Rack payouts are the loot above (Schematics and assets bank
    by themselves).
- **Keys, pad, clicks** as ANIM-4: X / Space picks up the focused item; A keeps buying /
  taking / choosing on buttons and picks up the items that only move (raid chips, the
  slice beside the viewer's wheel); the D-pad walks the reticle, A drops, B puts it back
  (and does not leave the Modem while carrying); the pad prompts add "X Pick up" on the
  Modem, the loot, the raid interlude and an event with an item, then "A Drop / B
  Cancel". Click-select-click on move-only items. Tooltips name the drag. After a drop
  the rebuilt page's focus lands on its first control, as after a click purchase.
- **Motion** (ANIM-4's ids reused; two new): a purchase, loot pick or event reward travels
  from where it was let go onto its target **shrinking into it** (`drop_buy` 0.22 s CUBIC
  out, arriving at x0.45: the targets are small top bar tags and slots), a purchase with
  SOLD stamping on the copy as it goes (`sold_stamp`, ANIM-6's), then ANIM-4's settle and
  stamp ring. A deck card dropped on the shredder travels to its mouth and **squashes
  into it** while paper strips run out below (`shred_feed` 0.3 s QUAD in, strips 28 px;
  six strips of fixed lengths, no randomness). Raid chips land with ANIM-4's
  `loadout_swap`. Refusals (not enough Cycles, a chip that fits no slice there, a full
  node) are ANIM-4's: the no-entry mark shakes, the item glides home, the rules' reason is
  a toast. Variants shown (strips): `drop_buy` 0.16 s / x0.35, **0.22 s / x0.45**, 0.32 s
  / x0.6 (card to deck, chip to slot, loot to deck); `drop_reject` 0.12/3, **0.20/6**,
  0.35/10 (not enough Cycles); `shred_feed` 0.2 s / 18 px, **0.3 s / 28 px**, 0.45 s / 40
  px. Picked: the snappy middle, matching ANIM-4's landing; the slow ones held the item
  over the top bar after the Cycles had already rolled, the fast shred read as a vanish.
- **Rules of the pass kept**: the state is final when the drop's call returns. Reduce
  effects and headless: no pulses, flights, marks or strips, the end state at once. Any
  press during a landing completes it. Layout at 1.0 / 1.3 / 1.6 checked: the small
  spinner inside its window and clear of the wallet, SHRED and LEAVE; the REMOVE viewer's
  card grid gives the SHRED tile its room (the window keeps its height); the viewer's
  slice beside the wheel over no slot; a chip offer's spinner in its row with Skip on
  screen; the raid chips wrap inside the 1280 width.
- New ids (data only; schema unchanged; REQUIRED_IDS and the motion lab updated):
  `drop_buy`, `shred_feed`. Frame capture: `netrun_scene --demo-shop
  --demo-anim=drag_buy_card | drag_buy_chip | drag_buy_refuse | drag_shred` and `--demo-loot
  --demo-anim=drag_loot`, with `--demo-set` for variants.

#### 2026-09-27 — Animation pass — ANIM-4: drag and drop, HQ side
The designer's "drag and drop anything (loadout changes, card use, etc)", HQ side: every
item the HQ, the City Grid, the raid setup and the loadout view move between places now
drags, as interaction and motion. Views only: no rule changed. Tests:
`tests/unit/test_anim4_drag_drop.gd`; strips: `docs/timeline/motion/drag_*.png` (README
rows marked ANIM-4).
- **One kit: `DropLayer`** (`scripts/ui/kit/drop_layer.gd`), a full-screen layer over the
  HQ scene (and one inside the loadout view). A screen registers drop targets (id, the
  item kinds they take, a locator for their rect) and sources (`add_source`: Godot's drag
  forwarding, so any control drags, buttons included). A drop is an intent: the layer
  emits `dropped` / `refused` and `hq_scene._on_dropped` makes the **same call the item's
  button makes** (Signal Up, Call Down). Whether a target takes an item is asked of the
  rules themselves: `hq_scene.drop_error` runs the button's own rule call on
  `campaign.duplicate_state()` and reads its refusal (never a copy of a rule); a target
  where the item already is is not offered. Rule texts name Sites by their names there.
- **What drags, and the button path each mirrors:**
  - Raid setup: an Armory card onto any claimed node, on the map or its YOUR NODES row =
    pick the node, then press the card (`deploy_asset`); the node's ANIM-5 asset drop
    (`play_asset_drop`) is the landing and the forecast stamp shows the new projection. A
    placed asset (its badge in YOUR NODES, its Withdraw / "> Site" buttons, or the picked
    node itself on the map) onto another node = its "> Site" button (`move_asset`, the drop
    plays on the new node), onto DEFENSE LOADOUT = Withdraw. Picking the picked node again
    no longer rebuilds the page (so a press on it can go on into a drag).
  - HQ: a crew dossier onto a claimed node of the CITY GRID monitor = Station on it; onto
    CORE = Recall (refused, with the reason, when they are at HQ already). Black Market: a
    Recruit button onto CREW // ROSTER = the button; a next-run boost onto the next run's
    kit (a "queued: ..." slot now always shown) = the button. A click on either buys as
    before and the item flies (`market_fly`: 0.45 s, 60 px arc) to where it went; the new
    dossier or kit line shows as its copy lands.
  - City Grid: the Site card lays the living crew out as small Polaroids (`CrewChip`) above
    JACK IN; one dropped on JACK IN = picking them in the list (`pick_operative`; the
    designer's ruling of 2026-09-27, applied in ANIM-R1: "prefer select, then jack in", so
    the drop no longer launches). Only pressing JACK IN starts the run. The list stays.
  - Loadout view, SPINNER tab, Rank 3: the class's ring segment swaps (and "Class default")
    sit beside the wheel as chips; one dropped on an inner ring segment = the dossier's
    "seg k" list (`swap_segment`).
  - Not HQ-side drags (why): the HQ has no rule that moves cards, Firmware, Daemons or
    slices (they change in the netrun's Modem and loot, ANIM-4b's), so the deck viewer and
    the Daemon tray stay view-only; the roster has no order to drag.
- **Keys and pad**: X (keyboard Space, the `end_turn` action, unused on these screens) picks
  up the focused item (a dossier's own order buttons pick up its operative); A picks up an
  item that only moves (crew chips, swap chips) and keeps its meaning on buttons that do
  something (an Armory card still deploys to the target, a Recruit still buys). While an
  item is carried the D-pad / arrows step a reticle through every target in screen order
  (the item follows, `drag_follow` 0.12 s CUBIC out), A drops, B (or X again) puts it back.
  The pad prompts say "X Pick up", then "A Drop / B Cancel". The mouse also clicks an item
  that only moves, then clicks its target (click-select-click); the old click-the-node-then
  -the-card path is unchanged.
- **Motion** (all in `ui_motion.tres`; ANIM-3's card drag reused for consistency): pick-up
  pops (`drag_pickup` 0.1 s x1.06) and the slot dims while the item is away; the ghost
  trails the pointer with ANIM-3's lag and tilt (`drag_ghost_follow`, `drag_ghost_tilt`);
  targets that take the item pulse corner brackets (`drop_zone_pulse`), the hovered one
  lights fully; a refusing target under the item shows the drawn no-entry mark (the refusal
  toast's); the pad reticle is ANIM-3's (`target_snap`). A drop snaps the copy from where it
  was let go onto the target (`loadout_swap` 0.2 s, operatives `crew_assign` 0.2 s BACK),
  dips and springs back (`drop_settle` 0.15 s / 6 px) and stamps a ring (`drop_stamp`
  0.25 s / +18 px, new) as it fades; an operative's dossier pops (`crew_assign` x1.1). A
  refusal shakes the no-entry mark on the target (`drop_reject` 0.2 s / 6 px), the item
  glides home (`drag_cancel_return`, ANIM-3's 0.15 s) and the rules' reason shows as a
  toast; a drop on nothing just glides home. Variants shown (strips): `drop_settle`
  0.10/4, **0.15/6**, 0.25/10; `drop_stamp` 0.18/12, **0.25/18**, 0.35/26; `drag_pickup`
  x1.00, **x1.06**, x1.14; `drop_reject` 0.12/3, **0.20/6**, 0.35/10 (picked in bold: the
  handoff's "zine, tactile, 0.2-0.35 s" and ANIM-3's snappy card drag).
- **Rules of the pass kept**: the state is final when the drop's call returns; motion plays
  on top. Reduce effects and headless: no pulses, flights or marks, the end state at once.
  Any press during a flight completes it. The layer adds nothing to layout (new pieces:
  the Site card's crew chips, the next run's kit slot, the swap column beside the wheel;
  checked at 1.0 / 1.3 / 1.6). Tooltips name the drags; focus lands on the target after a
  pad drop.
- New ids (data only; REQUIRED_IDS, the lab and the schema unchanged otherwise):
  `drop_stamp`, `market_fly` (124 entries). Retuned: `drag_follow` (0.12 s CUBIC, the
  carried item's glide), comments of the ANIM-1 drag ids now say what each drives.
- Frame capture: `--demo-anim=drag_asset`, `drag_asset_refuse` (`--demo-raid`),
  `drag_crew`, `drag_crew_cancel`, `drag_crew_refuse` (`--demo-grid`), `drag_loadout`,
  `drag_loadout_cancel` (`--demo-hq`) on the HQ scene; `--demo-tune` for variants.

#### 2026-09-27 — Animation pass — ANIM-6: screens, menus and ambience
Roadmap 4.13 (the HQ's non-map panels), 4.17-4.24. Strips with variants:
`docs/timeline/motion/` (README table). Every value is in `ui_motion.tres`.
- **Screen transitions** (`PageTransition`, 4.17): terminal glass slides in from an edge
  (`panel_in` 0.22 s, 48 px, CUBIC out) with a one-frame CRT roll (`panel_crt_roll`: the
  glass drops 6 px and a bright scan band crosses it for its first frame); paper drops in
  and settles on its tape (`panel_drop` 0.22 s, 24 px, BACK out). A page's look comes from
  its surface (`look_of`: a zine paper panel or note = paper). Snappy 0.14 s / 32 px read
  as a cut; heavy 0.24 s / 96 px dragged on every page change; BOUNCE made paper jelly.
  Used by the netrun (`_set_panel`: route, Modem, loot, event, raid, end), the HQ (home
  from the left when coming back, Grid, raid, codex...), the title's pages (title → HQ is
  the HQ's first page entering), the pause menu (drops), Options and the Codex inside it,
  the confirm dialog and a newly recruited dossier. The helper moves the page by an
  offset from wherever its container lays it out, so it works in any container; the page
  is clear for its first frame (before layout). **A page rebuilt on the same screen does
  not re-enter** (the Modem after a purchase, the HQ after every action): only a new
  screen does (`entering`). **Focus lands when it ends**; any key, button or click during
  it completes it (and the fans, drips, typing and the sign under it,
  `PageTransition.settle`) and does nothing else, like a SEND IT skip.
- **Menus** (`MenuMotion`, 4.18) on the title's main menu, the HQ deck menu and the pause
  menu: the focus box slides from the old line to the new (`menu_highlight` 0.12 s QUAD
  out), the new line types in (`menu_type` 0.02 s a character, at most 0.18 s a line: its
  new amplitude; 0.4 s felt like waiting on the menu), and a block caret blinks after the
  focused line's words (`menu_cursor_blink` 0.5 s half-period; we read "the `> ITEM`
  cursor" as the terminal caret on the selected line). Typing holds the line's size, so
  nothing moves; a key press completes it; the first focus after a page opens shows at
  once (the page entrance is the motion then). The caret is steady under reduce effects.
- **Modem** (4.19): on entering, the neon tubes warm up (`modem_sign_warmup` 0.8 s: each
  tube lights at hash-picked steps, unlit = its colour darkened) and the circuit traces
  light one after another from 0.35 s, CYBER SHOP last (`modem_trace` 0.6 s). 0.45 s
  missed the flicker; 1.2 s left the sign dark while the player shops. A purchase: SOLD
  stamps on the item (`sold_stamp` x1.5 → 1, 0.14 s BACK), then a picture of it flies to
  its top bar icon (`buy_fly` 0.4 s CUBIC in-out, arriving at x0.35: cards to CARDS,
  Daemons to DAEMONS, chips and slices to VIEW LOADOUT) while Cycles roll down. The BUY /
  SHRED stickers flap on their tape while their item is hovered or focused (`note_flap`
  4°). **`FlightFx`** is the shared flight / stamp layer (a CanvasLayer on the screen, so a
  page rebuilt under it does not cut it): `fly(screen, source, to, id, stamp, lift)`,
  `fly_node(...)` for a node copy, `stamp_on(...)`, `finish_all`, `active_count` — open to
  ANIM-4 (asset drops). The picture is the source's last drawn frame (one viewport read
  on the click); headless it is a paper card of the same size.
- **Loot** (4.20): the stickers fan in from the foot of their row (`loot_fan` 0.3 s CUBIC
  out, 0.06 s stagger, 8° a card; drawn offsets, the slots never move); the picked card
  lifts 12 px and flies to the CARDS tag (`loot_pick` 0.35 s, its amplitude is the lift);
  Cycles and Schematics **count up** on the top bar when they rise (`count_up` 0.6 s).
- **Subtitles** (4.21): each page types in at 0.025 s a character (40 cps: ahead of
  reading, so it never holds the reader back; 0.045 s felt slow on long DISPATCH lines),
  the inline speaker's name shows at once, the bar slides in from above (`subtitle_bar_in`
  0.2 s, 40 px) when it appears. **Paging respects the typed text**: a page's time starts
  once its words are all shown. Any press shows the page whole. Options → Accessibility has
  "Subtitles type in (off: each line shows at once)" (`Settings.subtitle_typing`, on by
  default, saved). Only `visible_characters` changes, so `current_text()` and tests read
  the whole page at once. The Terminal event's text types in the same way (`Typing`).
- **Drip lettering** (4.22): the drips grow from the letters the first time a tag appears
  this session (`drip_grow` 0.6 s QUAD out; a page rebuilt with the same tag does not
  regrow it), then hold; hovering or focusing gives one halo pulse (the jitter reaches out
  to twice and back, `drip_halo` 0.4 s), then the steady halo. Nothing loops. ELASTIC
  wobbled like jelly; 0.35 s was missed.
- **City ambience** (4.23): the live dashes now show only on the busiest streets
  (`city_traffic` amplitude 0.55 of the street's traffic, 2.8 s along a lot; they were
  every recorded spark at 0.3 / 1.4 s) as short bright dashes with a white core; only a
  third of the HQ name signs flicker (`city_sign_pick` 0.34, `hq_sign_flicker` period
  3.2 s, a 0.22 s dip to 0.45 alpha). Both stop under reduce effects. The city stays one
  baked draw plus the light FX layer. **Profile** (`tools/design_lab/profile_frames.gd`,
  600 frames after 120 warm-up, vsync off, RX 6700 XT, 1280x720): title (the whole-screen
  panning city) mean 1.07 ms before and 1.07 ms after (p95 1.39-1.58 → 1.45-1.50), 0.77 ms
  with reduce effects; HQ `--demo-hq` (city through the window plus the HQ idle) 2.08 ms
  before → 1.89 ms after (p95 2.52-2.74 → 2.23-2.40, GPU 0.90-1.11 → 0.95-0.99 ms), 1.70 ms
  with reduce effects. The ambience costs nothing measurable.
- **Top bar** (4.24): a tag whose value changed bumps (`sticky_bump` x1.08, 0.12 s BACK)
  and its number rolls from the old value (`number_roll` 0.3 s; `count_up` for rising
  Cycles / Schematics). Tags are matched by name, so only a changed value moves; drawn
  only (rects never move). The CAMPAIGN / THIS RUN captions cross-fade when the set
  changes (`caption_crossfade` 0.2 s). x1.15 over 0.2 s shouted on every purchase.
- **HQ idle** (4.13): the deck monitor hums (`CrtHum`: a faint band rolls down the glass
  once per 2 s, 0.06 alpha), JACK IN's rings breathe (1 ↔ 1.04 over 2.4 s each way), the
  pirate radio types in on arrival (`radio_type` 0.03 s a character), a crew Polaroid
  tilts 3° further while its dossier is hovered (`polaroid_tilt`, from wherever the
  dossier lays it out), a new recruit's dossier drops in on its tape, and a Black Market
  boost or unlock stamps SOLD where its button was. The strong hum (0.14) read as a fault.
- **Event** (4.19-4.21 family): a choice's outcome icons pop when it is hovered or
  focused (`event_outcome_pop` x1.15); the chosen outcome stamps down over the next screen
  as it comes in, holds and fades (`event_choice_stamp` 0.6 s).
- **Small pieces**: the pad prompt row fades in when its prompts change
  (`pad_prompts_in`), a focus tip fades in (`focus_tip_in`), the SAVED stamp stamps down
  (`saved_stamp_in` x1.35 → 1) before its hold and fade.
- **Text size / language changes**: nothing animates (checked: a settings change re-lays
  the page out with no entrance, flight or bump; tested).
- **Reduce effects / headless**: every piece shows its end state at once (no helper node
  is even created), focus is given at once as before, flights and stamps are skipped.
  Scene captures take `--demo-set` / `--demo-speed` (`MotionDemo`), and the netrun has
  `--demo-buy`, `--demo-pick`, `--demo-choose` to act 30 frames in.
- New ids (data only, required by content validation): `saved_stamp_in`,
  `pad_prompts_in`, `focus_tip_in`, `event_outcome_pop`, `event_choice_stamp`,
  `sold_stamp`, `caption_crossfade`, `city_sign_pick`. Retuned meanings (comments in the
  .tres): `menu_type` amplitude = most seconds a line, `buy_fly` amplitude = every
  flight's arrival scale, `loot_pick` amplitude = lift px, `city_traffic` = seconds a lot
  and the traffic a street needs, `hq_sign_flicker` delay = dip seconds, `modem_trace`
  delay 0.35 s. No schema change. Words added: "SOLD", the typing switch's label.

#### 2026-09-27 — Animation pass — ANIM-3: card targeting and execution
- **Hover** (`card_hover`, 0.15 s, 12 px): the sticker lifts, tilts from its resting
  angle to 0 and glows. The lift and the deal-in offset are *drawn* offsets
  (`ZineCard.lift`, `draw_offset`, `draw_tilt`): the card's rect never moves, so the hand
  never shifts under the cursor and layout checks are unaffected. Every ZineCard gets it
  (loot and shop stickers too: one card kit).
- **Pick-up / drag** (`card_pickup` pop; `DragGhost`): the drag preview trails the cursor
  with an exponential lag (`drag_ghost_follow`: duration = time constant 0.08 s, amplitude
  = ghost alpha 0.6) and tilts with the cursor's speed (`drag_ghost_tilt`: 0.12 s smoothing,
  8° most). Variants tight 0.04 / loose 0.16 / 0.08: 0.08 reads as "carried" without
  feeling late.
- **Aiming** (mouse, keys and pad alike): valid zones pulse (`drop_zone_pulse`, the
  unhovered ones between 0.55 and 0.28 alpha; the hovered one stays full); the aim line
  draws in from the card each time the aim moves (`aim_line_draw`); a bracket reticle on
  the motion layer glides to the aimed zone with a snap pop (`target_snap`); the RAM cost
  chips blink while aiming (`ram_pending_blink`).
- **Cancel** (drop on nothing / on no legal target): a copy glides from where it was let
  go back to the card's slot (`drag_cancel_return`, chosen snappy 0.15 s over 0.3 heavy
  and 0.22 back-eased), the slot's card shows again when it lands. Key / pad cancel never
  moved the card, so nothing flies.
- **Play**: the card copy flies from its slot (or the drop point, upright) to the centre
  of the zone the action used (captured before the engine call), grows, stamps down
  (`card_stamp`) and dissolves into an acid burst (`effect_burst`) — or, with `exhaust`,
  curls flat and darkens with embers (`card_exhaust`). Chosen snappy: `card_play` 0.22 s,
  `card_stamp` 0.1 s (heavy 0.4 / bouncy 0.3 back-eased shown). The effect (spin, nudge,
  numbers, deaths) waits for the stamp.
- **No reflow under the cursor**: while the card flies, the hand keeps a gap in its slot
  at the old card scale; the gap closes (`hand_reflow`) only once the cursor is off the
  hand. Hand lookups go by `drag_index`, never child index.
- **Draw / discard**: SEND IT sends the old hand to a discard pile at the hand's right
  end (`card_discard` arc, staggered by `card_draw`'s delay); the new hand deals in from a
  deck pile at its left end with a fan (`card_draw`: 0.25 s, 0.04 s stagger, 6° fan) on
  the turn-start draw beat. The piles are drawn only while cards move (`card_pile`), so
  the static layout gains nothing.
- **RAM** (`ram_tick`): the chips drain / refill one chip per 0.05 s with a pop; the number
  is always the state's. SEND IT holds the old RAM until the turn-start RAM beat.
- New ids: `drag_ghost_tilt`, `card_pile`, `hand_reflow`, `ram_tick`, `ram_pending_blink`
  (data only, required by content validation).

#### 2026-09-27 — Animation pass — ANIM-2: spinners and end-turn resolution
- **The replay rule.** The engine's state is final when an action returns; motion replays
  the same `events` array on top (GDD 2.10: preview = result). `ResolveBeats.build(before,
  events)` turns events into beats (one per damage / heal / block / shield / evade /
  status / corrupted / death / breach / spin / orbit / migrate / RAM / draw / combat end,
  in event order) and tracks HP only by subtracting the events' own numbers, so the beats
  end on the state's HP (tested). It never runs a rule; the pulsing needle of a beat is
  picked from the landing events (the next needle of the actor on a slice of that kind).
  Views are overridden, never the state: `WheelView.shown_state` (a snapshot the scene
  took before SEND IT), `anim_rotation`, `anim_pointers`, `anim_hp`, `lag_hp`...
- **SEND IT sequence** (`resolve_sequence` = 1.45 s budget at 1x; variants 1.2 / 1.8 / 1.45
  shown, 1.45 kept: beginners asked to *see* what happened and it still fits "under
  ~1.5 s"). Press: the drip lettering squashes (`send_it_press`) and the drips run
  (`send_it_drips`). Then: needles latch (precision landings, all at 0); beats one gap apart
  in resolve order (defensive, offensive, statuses; a gap more at each pass), the gap being
  `resolve_beat` squeezed so everything fits; each beat pulses its needle (or satellite
  token), draws a hit line attacker → victim (`hit_line`), pops a number, drains the HP arc
  with a white lag bar (`hp_drain`, `hp_lag`), stamps statuses on their slice
  (`status_stamp`), cracks dead wheels; then the turn start: both wheels spin to the next
  landing (`wheel_respin`; enemies `enemy_turn_spin` 0.15 s later), needles orbit / migrate,
  RAM refills, the hand deals in; the LAST TURN plate slides up last (`last_turn_reveal`).
  The tags and NEXT plates hide while it plays (they forecast the *next* turn) and flip back
  in at the end. **Any press** (key, mouse button, pad button) skips to the end state and
  does nothing else (so a double click on SEND IT never ends two turns).
- **Numbers** float inside the victim's hub (inner disc x 0.62), stepping left / right when
  several land together: needles only reach the slice band and satellites sit outside the
  rim, so a number never covers the next resolving needle (tested for every beat at
  1.0/1.3/1.6). Damage red "-N", soaked hits "N BLOCKED", guard gains cyan "+N BLOCK /
  SHIELD", heals green "+N HP"; crits (a CRIT slice or a Perfect needle) are 1.5x with a star
  burst. Existing word keys only (no new translation keys).
- **Spin** (`wheel_spin` card spins, `wheel_respin`, `enemy_turn_spin`): the ring runs the
  exact ticks the core moved (rotation is unbounded, so the distance is exact) with the
  entry's ease, overshoots by amplitude x 0.1 tick and settles over the last 30%; its time
  scales with sqrt(distance in half turns) within 0.55x-1.35x of the entry (the handoff's
  0.25-0.6 s). Chosen snappy (0.35 s card spin, 0.4 s respin, overshoot 0.2 tick, CUBIC)
  over heavy (0.55 s QUART) and bouncy (BACK: its built-in overshoot grows with distance and
  showed a wrong slice on a 70-tick respin). Slices blur (faint trailing copies) above
  `wheel_spin_blur`'s 12 ticks/s.
- **Nudge** (`wheel_nudge` 0.08 s, 2 px recoil; `inner_ring_turn` for the inner ring): each
  step travels 70% of its time then the disc kicks back. Steps queue; a queue of n steps
  runs each at 1/n speed so it catches up; the last queued step is forced onto the core's
  tick (`sync_nudges`), so rapid input never desyncs (tested).
- **Precision landings**, distinct in greyscale: Perfect = inversion + 2-frame freeze + a
  limited `Fx.flash` + needle pop; Good = a clean white ring off the rim; Partial = stutter;
  Miss = static flecks over that slice only (it replaced the whole-wheel blink).
- **Pointers**: migrations glide the short way round (`pointer_migrate`); orbits leave a
  fading dashed trail arc (`orbit_trail`). The flicker stays.
- **Intent tags** flip on their tape (`intent_flip`, 90°) only when their text or chips
  change: the content signature is compared at draw time, so re-setting the same chips on
  every hover doesn't jitter.
- **Rewind**: VHS bands over the arena and a 5-step tape stutter of the rings and HP back
  to the restored state (`rewind_scrub`); every shown value stays between the two states,
  so it never crosses the checkpoint.
- **Death / breach / end**: a dead wheel falls apart into its slices (`enemy_break`,
  chosen heavy 0.75 s / 160 px: the climax of a fight) and its dim ghost fades back
  (`dead_wheel_fade`); a hub breach shatters the hub glass (`hub_shatter`); defeat breaks
  the operative's wheel; VICTORY / DEFEAT stamps over the arena (`victory_stamp`), the
  victory flash moved onto that beat. The netrun now waits for the replay (`motion_settled`)
  and then holds `combat_end_hold` (0.8 s, the old inline number).
- **FLIP** squashes the disc to a line and back (`wheel_flip`).
- **Reduce effects / headless**: nothing is captured or played; the end state shows at
  once. Tests drive the live path with `Motion.force_live`.
- Frame strips with variants: `docs/timeline/motion/` (README table).

#### 2026-09-27 — Animation pass — ANIM-5: campaign, map and raid motion
Handoff items 4.1, 4.12, 4.14, 4.15, 4.16, the city influence change the designer asked
for, and the HQ mini-map. Views only: no rule changed; the resolver's `move` event gained
two facts it already computed (below). Every value is in `content/config/ui_motion.tres`.
Reduce effects and headless show every end state at once (the jack: one short fade under
reduce effects). Tests: `tests/unit/test_anim5_map_motion.gd`. Frame strips:
`docs/timeline/motion/` (README rows marked ANIM-5).
- **City colour influence (the designer's ask).** A change of territory no longer jumps.
  The city still bakes once per look (H20's static image stays): the new look is baked
  while the old image stays on screen, then the new image shows through the old one as
  the tint spreads from the Site(s) whose pull changed (`InfluenceSpread`, pure; mask
  shader `shaders/influence_reveal.gdshader`). Distance is Manhattan along the street
  grid in lots, plus a per-block hash jitter, so whole blocks turn along the streets; a
  light band in the new owner's colour (the Cell's pink, or the corporation's) rides the
  front. Whatever changed beyond the front's reach (a raid's sway over the whole
  territory) cross-fades in behind it. A sway-only change spreads from the corporation's
  HQ. Values: `influence_spread` 1.0 s OUT CUBIC, reach 10 lots (CityInfluence.RADIUS is
  7.5); `influence_crossfade` 0.6 s after 0.4 s, IN_OUT SINE, front edge 1.5 lots. The
  bake happens BEFORE the spread (not at its end, as first sketched): then the end state is
  pixel-exact (the real bake) and the bake's hitch never lands mid-motion. It plays
  wherever the change is first seen: each city family (net/physical, district, campaign)
  remembers the influence it last showed (`NeonCity._seen`), so a Site cleared in a run
  spreads when the HQ backdrop shows it on return (and on the netrun's summary). Headless
  never spreads (no bake); an old image evicted from the cache leaves the light front only.
- **Raid execution (4.15).** The playout is built from the events the resolver returned
  (`RaidBeats`: grouped by step, beats in the resolver's phase order: enter, move/held,
  ICE LOCK and ghost holds, shots one after another half a trace apart, then damage,
  Disabled, Seized; the raid's end is its own group) and drawn on the city map by a
  `RaidFxLayer`: threats travel the street route between nodes (`raid_move` 0.5 s IN_OUT
  SINE), gun traces (`turret_trace` 0.15 s) with a hit ring (`raid_hit_effect`), ICE
  LOCK rings close from 2.2x (`ice_lock_ring` 0.25 s) and leave a frost ring while
  held, a DECOY's gold lure line pulls a threat 8 px aside (`decoy_fire`), numbers rise
  24 px off nodes (`node_damage_number` 0.6 s), HOLDS / DISABLED / SEIZED / BREACHED
  stamps flip in from 90 degrees (`raid_flip` 0.2 s), home integrity drains with a white
  lag bar (`home_lag` 0.45 s after 0.2 s), a rest of `raid_step_gap` 0.2 s after each
  step, and a Seized node spreads a corporate tint disc until the city's own tint lands.
  At 1x a typical step reads in about 1.2-1.8 s. The playout starts from the Grid as it
  stood (a view copy of the campaign), and the city holds its pre-raid tint
  (`NeonCity.pin_influence`) until the end, then lets the result spread (one bake). The
  end is snapped to the resolved raid (`last_raid.home_after`, node outcomes), never a sum
  of the beats. The setup's ForecastStamp rides along in the feed and resolves into the
  real verdict ("RAID / RESULT:", solid ring, `forecast_stamp_resolve` pop). Speed:
  1x / 2x / 4x set `Motion.speed` for the playout (the panel's clock and every motion it
  builds), back to 1x when it ends. Skip jumps every beat to its end and goes straight to
  the summary (HQ) or on (netrun). A click or accept press ends the current step's motion.
  The mid-run raid (netrun) plays the same way. Resolver facts: `move` events now carry
  `target` and `decoy` (whether a DECOY's pull chose the target), the values the routing
  already used (`_decoy_site` factored out; results and hashes unchanged, tested).
- **Answer to the ANIM-1 open question (does a sped-up raid hurry the city?): no.** The
  city backdrop (window lights, beacons, traffic, rain) keeps its own clock at every
  speed; 4x beacons would strobe. Everything that belongs to the raid (tokens, traces,
  numbers, stamps, the map's route dashes and packets) runs at the chosen speed.
- **City Grid / raid setup (4.14).** Selecting a Site draws its roof outline on (stroke
  reveal with a bright head, `site_outline_draw` 0.4 s OUT CUBIC) and its ring eases in
  from 1.8x (`select_ring_ease` 0.25 s OUT BACK). The camera eases instead of jumping: the
  net city hangs from a camera rig (`WireframeBackground.rig`). The camera itself always
  changes at once, so every H22-H24 fit and label layout reads the real frame (fits run
  with the rig at rest, `unrigged`); the rig only holds the old picture while the page
  refits and then eases it to the new one (`map_camera_ease` 0.5 s IN_OUT CUBIC). The
  camera leans toward the selected Site (`grid_lean`): at most 90 px, and only inside the
  slack that keeps every node in the fitted area, so the H23/H24 framing holds at the end
  state (tested). The raid playout's follow camera eases the same way, and the raid setup holds its map still while it rebuilds after a deploy or a new target (then eases to the refit). Threat route
  dashes crawl toward home at `route_crawl` 30 px per 1.0 s (the old DASH_SPEED, now in
  the table). Deploying an asset: it drops 24 px onto its node with a stamp ring
  (`asset_drop` 0.25 s BOUNCE); the hook for ANIM-4's drag and drop is
  `hq_scene.play_asset_drop(site_id)` (`CityMapOverlay.drop_asset`). The folding map key
  (H24 K1) slides its rows 14 px in and out with a fade (`legend_fold` 0.18 s); the map
  is framed for the folded line throughout, and the rows hide when they have slid out.
- **Heat thresholds (4.12).** `Fx.heat_pulse` is wired: `HeatPoster` remembers the Heat
  each campaign last showed (`_seen_heat`, view memory) and plays, once the poster shows
  and no jack runs: one pulse per threshold crossed going up (two at once play a pulse
  apart), the ransom letters shake once (`heat_letters_shake` 3 px), and the band word
  stamps on from 1.3x with an ink box (`poster_stamp`). The pulse also sends the
  corporation's wireframe creeping in from the screen edges over the zine layer to 30 %
  of the half-height and back (`net_creep` 1.2 s; `shaders/corp_creep.gdshader`). A
  steady value plays nothing; a crossing down (Heat bought off) only stamps the band (no
  pulse: the corporation's attention fading is not a threat event). Nothing stays on.
- **Netrun route (4.16).** Choosing a node applies the rule at once, then the route map
  plays the move before the node's screen opens: a light pulse with a fading trail runs
  the street route and carries the "you are here" marker (`route_pulse` 0.4 s), the new
  node pops from 1.2x with the marker on it (`node_pop` 0.25 s BACK) while the node left
  behind dims to 0.5 (`visited_dim` 0.3 s). About 0.65 s; any input (or another choice)
  skips it. The route map's "you are here" ring eases in when the map opens.
- **Jack in / jack out (4.1).** The real version (`Fx._transition`): the HQ scene scales
  2.6x about its deck CRT (the monitor on the HQ page, or the Site card's JACK IN;
  `Fx.JACK_FOCUS_GROUP`) while the screen dissolves cell by cell from that point into the
  wireframe city (the net's iso lattice) with scanlines rolling (`jack_scanlines` roll
  0.45 s, strength 0.35; `shaders/jack_cover.gdshader`); the scene changes under the
  opaque cover, and the net arrives from 1.24x as the cover clears. Jack out is the
  exact reverse (the net pulls back, the HQ comes out of the CRT from 2.6x). 0.8 s
  (`jack_in` / `jack_out`, IN_OUT CUBIC: the push eases in, the arrival out). No frame
  shows both scenes (tested at the switch). Reduce effects: a 0.2 s fade through black
  (`jack_fade_reduced`). Headless: the switch at once. The old growing CRT rect is gone.
- **HQ mini-map.** A Site whose status changed since the mini-map last showed (a run
  cleared it, a raid Seized it) pulses once, a ring growing 18 px as it fades
  (`minimap_pulse` 0.6 s); the home "you are here" rings (and a selected ring) ease in
  (`select_ring_ease`). Only the HQ's mini-map remembers (the Grid page's hidden model
  never counts as seen).
- **New ids (data only; REQUIRED_IDS and the lab updated):** `jack_scanlines`,
  `raid_step_gap`, `home_lag`, `minimap_pulse`, `select_ring_ease`, `legend_fold` (111
  entries). Retuned: `jack_in` / `jack_out` (0.8 s, zoom 2.6), `net_creep` (reach 0.3),
  `map_camera_ease` (lean 90 px), `heat_pulse` (peak 0.5, was 0.85), `route_crawl` (30 px per s), `ice_lock_ring` (start
  2.2x), `influence_spread` / `influence_crossfade` (above).
- **Variants shown (frame strips, docs/timeline/motion):** influence_spread 0.7 / **1.0** / 1.4 s (1.4 lingers after the panels have settled); raid_move 0.35 / **0.5** / 0.7 s (0.35 skips past the route, 0.7 drags a four-step raid past 6 s); heat_pulse peak 0.85 / **0.5** / 0.3 (0.85, ANIM-1's value, tore the UI apart; 0.3 barely reads as a threat; retuned); jack_in 0.6 / **0.8** / 0.9 s (the handoff's "heavy"); route_pulse 0.3 / **0.4** / 0.6 s; site_outline_draw 0.25 / **0.4** / 0.6 s. Picked values in bold; the owner may swap any of them in the table.
- Frame capture: `--demo-anim=<id>` on the HQ scene (`site_select`, `influence_spread`,
  `raid_playout`, `asset_drop`, `heat_pulse`, `jack_in`; with `--demo-grid` /
  `--demo-raid` / `--demo-hq`) and on the netrun scene (`--demo-run
  --demo-anim=route_pulse`) play one motion once the city has baked and print "anim5: <id>
  starts on frame N"; `--demo-tune=<id>:<duration>[:<amplitude>]` plays a variant from a
  duplicate of the table.

#### 2026-09-27 — Animation pass — ANIM-1: motion foundation
The designer made motion its own Animation pass ("nothing should be deferred"). ANIM-1
makes motion tunable before any new effect
is built (ANIMATION_HANDOFF 3).
- **Schema (CLAUDE.md rule 8):** two new resources in `scripts/data/`.
  `UiMotionEntryData` holds `id`, `duration`, `delay`, `ease` (Tween.EaseType), `trans`
  (Tween.TransitionType), `amplitude` and `enabled`. `UiMotionData` holds `entries` and
  `REQUIRED_IDS`. The table is a sub-resource per entry, so one entry reads as one
  block in the .tres and the lab prints paste-ready lines. `amplitude` has no unit of
  its own; the helper and the entry's comment name it (px for slides, lifts and shakes, a
  scale for pops, an alpha for fades and blinks, degrees for tilts, frames for the hit
  freeze). The schema smoke test round-trips both classes and checks that the shipped
  table has every required id.
- **One table, loaded by path.** `ContentRegistry` records the `UiMotionData` it scans
  (`motion`, `MOTION_PATH`), like the campaign config. A missing table fails content
  validation (`tools/validate_content.gd`) but not `ContentRegistry.validate()`. That
  keeps the registry's existing tests exact, and rules never read motion. Entry ids
  share the content id namespace, so the registry's duplicate check guards against clashes.
- **105 entries**: every roadmap item 4.1-4.24 has at least one id, plus the shared ones
  (`screen_flash`, `hit_freeze`, `saved_stamp`, `toast`). 33 more cover the pass scope the
  designer added beyond the roadmap. Raid execution: `ice_lock_ring` (not `ice_lock`, an asset id), `decoy_fire`,
  `raid_hit_effect`, `node_damage_number`, `forecast_stamp_resolve`. Card targeting:
  `card_pickup`, `drag_ghost_follow`, `drop_zone_pulse`, `aim_line_draw`, `target_snap`,
  `drag_cancel_return`. Card execution: `card_stamp`, `effect_burst`, `card_discard`.
  End-turn resolution: `resolve_beat`, `block_number`, `heal_number`, `hp_drain`,
  `status_stamp`, `last_turn_reveal`. Spinners: `wheel_respin`, `inner_ring_turn`,
  `pointer_migrate`, `pointer_orbit`, `enemy_turn_spin`. Drag and drop: `drag_pickup`,
  `drag_follow`, `drop_settle`, `drop_reject`, `loadout_swap`, `crew_assign`. City
  influence: `influence_crossfade`, `influence_spread`. Screen transitions, number rolls
  and top-bar bumps already had ids (4.17, 4.24). Ids are data: adding one needs no
  schema change. Where the handoff gives a
  range, the pick is its middle or the existing value. `jack_in` / `jack_out` keep 0.7 s
  (range 0.6-0.9). `wheel_spin` is 0.45 s for a half turn (range 0.25-0.6). `wheel_nudge`
  is 0.1 s (under 0.12). `card_*` run 0.15-0.35 s (0.2-0.35). `panel_in` is 0.22 s (under
  0.25). `intent_flip` is 0.15 s. `drip_grow` is 0.6 s. `sticky_bump` is 1.08 over
  0.12 s. `resolve_pass` stays 0.35 s: a full resolution of four passes plus statuses
  stays under 1.5 s. Values for effects later slices build are starting points; those
  slices may add ids.
- **`Motion` kit** (`scripts/ui/kit/motion.gd`): `run`, `fade`, `pop`, `slide_in`,
  `shake`, `blink`, `loop_pulse`, `number_roll` and `stop`, plus `seconds` / `delay_of` /
  `amplitude` / `live` for code that builds its own tweens. It returns null and applies
  the end state at once under reduce effects, under a headless display server and for a
  disabled entry (`force_live` lets tests and captures animate headless; reduce effects
  still wins). A helper started again mid-motion settles on the true rest value, which
  node meta records. `Motion.speed` (`set_speed`, clamped to 0.25x-4x) divides every duration
  and delay the kit hands out. It serves the lab (0.25x-2x) and raid playback (1x/2x/4x). Ambient loops (beacon
  period) read the raw duration, so a raid at 4x doesn't strobe the city.
- **Inline numbers moved**: `Fx.flash` (strength/seconds default to `screen_flash`),
  `freeze_frames` (`hit_freeze` frames), `show_saved` (`saved_stamp`: hold 0.6, fade
  1.2), `heat_pulse` (`heat_pulse` duration and peak), `jack_in` / `jack_out` (durations;
  the CRT rect runs between `jack_out`'s 0.3 and `jack_in`'s 1.2 of the viewport, eased by
  the entry). In combat: PASS_DELAY (`resolve_pass`), the Perfect flash
  (`precision_perfect`), the Partial stutter (`Motion.shake` on the wheel's `shake`, now
  redrawn each step, so it shows), the miss blink (`precision_blink`) and the migration
  flicker (`pointer_flicker`, looping). The NeonCity beacon uses `beacon_blink`: its
  period, with amplitude as the lit share. The DripButton hover halo takes its jitter
  reach from `drip_halo`, and the Toast its hold and fade from `toast`. Behaviour is
  unchanged at 1x. The one change: headless runs now show the migration telegraph's
  static state (pointer alpha 0.6, as under reduce effects) instead of a loop no one sees.
- **Motion lab** (`tools/design_lab/motion_lab.tscn`, not exported): it tunes a
  duplicate of the table (`Motion.use_config`), so the loaded resource never changes.
  Each id has a demo kind and a piece in `DEMOS`: the pieces are a ZineCard, a WheelView
  showing a real breaker fight, a StickerButton, SEND IT, a ZinePanel and a number.
  "Copy values" prints the entry's .tres lines and copies them to the clipboard.
- **Capture**: `--demo-anim=<id>` (plus `--demo-speed=<x>`) plays one motion once, on
  frame 6, then holds. `tools/design_lab/frame_strip.py` (Pillow) montages the Movie Maker
  frames into a strip labelled in ms. Verified on this Windows machine; the command is in
  ANIMATION_HANDOFF 6.
- **Tests**: `tests/unit/test_motion.gd` (18 tests) covers the table, reduce effects,
  headless, disabled entries, speed, config-driven values, `stop`, game state and a lab
  demo for every id.

### 2026-09-27 — H23 combat: subtitles that don't blank, wheels sized from the room below, turns that say what happened
From pass 23 (both audits, a first-time player and a player who can't read English
looking at the pass-23 storyboards; GAP_ANALYSIS H23).
- **Subtitle refit** (P1): a line already on screen is re-paged and refitted whenever the
  bar docks somewhere new (`dock_at`, `dock_default`). Zeroing the label's minimum height
  on the move back to the strip had left an empty framed box at almost every fight start.
- **Wheel size**: the centre is no longer fixed at 0.56 of the view. It rises when the HP
  number and the LAST TURN line need room below (`WheelView._center`, `_bottom_need`).
  The radius is the largest that fits the tag, the disc and that block. Below that, the tag
  may clamp under the arrows down to `RADIUS_FLOOR` of the unconstrained size, provided
  its title row still fits. At the biggest text the wheel keeps at least
  `BIG_TEXT_RADIUS_KEEP` (75%) of its 1.0 size. The view's height is fixed and the title
  row and HP block grow with the text, so 80% could not be promised (a fight at 1280x720:
  126 px at 1.0, 97 at 1.6; before, 91, and 60 inside a run). Hub lines shrink, then
  ellipsise, to fit the hub.
- **LAST TURN** splits the resolve from the next turn's start: "-6 HP · +6 AT TURN START"
  (a boss's Auto-Renew heal had cancelled the damage into "NO CHANGE" and disagreed with
  NEXT). It also counts block and shield gained, statuses put on the wheel ("GOT
  CORRUPTED") and statuses an Encrypted slice stopped. A turn that defended and was
  afflicted no longer reads "NO CHANGE".
- **Respin** says what it bought: a note over the hand ("RESPIN -4 RAM: DEFEND · GOOD AIM",
  with "AGAIN" when it landed on the same thing). The sticker reads "RESPIN 4 RAM". The
  toast gains a note mode without the no-entry mark.
- **Status line**: one nudge pair, "Q/E NUDGE YOUR WHEEL", then what the switches switch
  *to* ("W: NUDGE THE TARGET", and "R: INNER RING" only when the nudged wheel has an inner
  ring). "YOURS [W] OUTER [R]" had read as a second nudge pair.
- **Words**: a loss on a tag reads "YOU TAKE 11 HP" / "TAKES 8 HP", not "-11 HP" under DEFEND.
  The folded chip reads "+4 MORE" (the tag tooltip lists every chip). Satellite plates use
  " >2" like the wheels. The aim hint moves over the enemy side, off the RAM row; on a pad
  it names the D-pad and buttons, not "Drop". The tutorial takes its keys from Settings
  and says GOOD AIM / HALF POWER.
- **Satellite tokens** in the bottom sector sit beside the HP block, not on it; their target
  ring and crosshair scale with the token. Tokens are drawn after the tag and the arrows (they are
  hit-tested first), and a token's HP plate goes outward, else to a side, else inward,
  whichever first keeps clear of the tag (at 1.3+ the plate sat under it).
- **Drawn words translate**: the combat's drawn text (tag chips, LAST TURN, the status
  line, NEXT, hub lines, ring segment and wheel names) goes through `tr()`, and through
  `TranslationServer.translate` in static helpers, with format strings as keys. Before,
  only the subtitles translated, and the scrambled storyboard showed these words in
  English. Tooltips and sticker labels are left to translate where they are shown.
- Tests: `tests/unit/test_horizontal_pass23.gd`. Updated on purpose: the pass-21 LAST TURN
  test (resolve plus turn-start parts sum to the real change, now including Renewal
  Engine), the pass-21 pad status test (the switch key rather than "[LT]") and the pass-22
  big-text radius test (`BIG_TEXT_RADIUS_KEEP`, and no fallback clause). Views only: the
  balance numbers stand.

### 2026-09-27 — H23 screens: nothing over a control, speakers once, a key per map, words for every number, buy buttons, pad prompts
Pass-23 screens items S1-S18 (reviewers at text 1.0 and 1.6 with a pad; the horizontal
audit's S14-S18). Views only: no rule or balance changed.
- **SAVED** (S1): `Fx.place_saved` puts the stamp at the first spot along the screen's
  edges (bottom right to left, then the top, then the sides) that covers no usable
  control, map legend or pad prompt row on screen (`Fx.saved_spot`, pure), at the text
  size; the least covered spot when none is clear.
- **Subtitles** (S2, S3, S17): a line that opens with its own sender tag in capitals that
  starts with the speaker's name ("SOLACE COLLECTIONS: ...") keeps that tag as the name
  (`Dialogue.own_speaker`; it was "SOLACE: SOLACE COLLECTIONS: ..."). A page that goes on
  ends in " …" (`CONTINUED_MARK`); a line that pages is wrapped with room for the mark on
  each page's last line (a line that fits in one page is wrapped as before). The raid line
  at 1.6 was paging, but its first page ended mid-sentence with no cue. `say(...,
  translated = true)` skips the second translation: voice lines and event text come
  translated (they were pseudolocalised twice).
- **Voice lines translate** (S15): a voice line's key is `LineSetData.<set id>.lines.<n>`
  (a VoiceLineData has no id); `TextDb.collect` exports them and `tools/export_text.gd`
  regenerated `assets/text/strings.csv`; `Dialogue.speak` says `TextDb.voice(...)`; the
  corporate speaker's name is the first word of its TextDb name. Screen sentences that
  are not content live in `TextDb.UI_TEXT` (exported too; `TextDb.ui_text`).
- **Drawn words translate** (S16): ForecastStamp caption and verdict, HudStats tag names,
  AssetCard numbers' words, StickerButton lettering and the buy button's verb are drawn
  and measured through `atr` / `tr` (accessors `shown_verdict`, `tag_name`,
  `integrity_text`, `shown_text`).
- **Raid map** (S4, S14): one legend, listing only what the raid map shows
  (`MapLegend.show_only(MapLegend.keys_of(graph, grid))`: marks, statuses, link / threat
  edges and node kinds). Framing acts only on a settled measure (the free rect and the node
  icons' box unchanged for `RAID_STABLE_FRAMES` frames: the icons follow the camera a
  redraw or two late, the old pass aimed with stale positions and moved the camera twice
  as far): each pass zooms out as far as needed (never past `RAID_MIN_ZOOM` 0.6, never in)
  and moves the box into the map area right of the legend's column, the area as far as it
  is on screen; a move's size is corrected by how far the last move really took the box;
  at most `RAID_REFRAMES_MAX` (6) passes per layout. Tags make way for the legend as before
  (`avoid_controls`); the test checks node icons, pips, tags and labels against it.
- **Raid words** (S5): an opening sentence (`ui.raid_intro`: "The corp is raiding your
  CORE. Place defences to cut the damage, then RUN THE RAID."); the facts read "HOME 50 >
  40", "STOPPED 0/2", "STRENGTH +0%", "10 ENTRY SITES"; node rows "HP 50 > 40 HOLDS" (the
  map tag keeps "50 > 40 HOLDS" and its tooltip says it is HP and what HOLDS / BREACHED
  mean); asset cards "HP 10" and "1 LEFT", explained in their tooltips. Every badge keeps
  a tooltip.
- **ForecastStamp** (S18): icon, caption and verdict are stacked from their measured
  heights, centred, and shrink together when taller than `STACK_ROOM` of the ring.
- **HQ** (S6, S13): the wanted poster is as tall as its band word (it hung under the paper,
  under the radio note); PIRATE RADIO grows to its words (at least `RADIO_LINES`), no
  scroll bar. Scrub Heat reads "Scrub Heat -5 · pay 25" with the Schematics icon at the
  button's right end ("price_kind" meta) and a tooltip naming the currency and what you
  have.
- **Route key** (S7): `RouteLegend` lists the node kinds the route has (fight, elite,
  event, shop, rack; map icons from `CityMapOverlay.draw_icon`) and what each does; it is
  placed by `LegendSpot` in the room under ROUTE; the zoomed-out GRID VIEW keeps the
  campaign map's MapLegend. Node tooltips start with the same words ("Rack: fight, then
  bank Schematics and assets.").
- **Modem** (S8): every item carries a `BuyButton` (a StickerButton kind: coin, "BUY 45",
  "SHRED 50", "BUY 100-150" for a slice whose price depends on the slot) over where its
  price tag hung; the item stays the pad's focus stop and the sticker shows the pad button
  ("BUY 45  A") while it has focus; clicking the sticker presses the item. Microchip and
  Daemon tiles draw their effect text under the name (the chip icon shrinks for it), in
  the text colour (the disabled shade now dims the art only). `FocusTip` shows a focused
  item's tooltip (the whole text) under it when the focus did not come from the mouse.
- **Outcomes** (S9): `OutcomeRow.shown` drops zero amounts from the row and the button's
  words ("(+0 Heat) +0"); the tooltip says "HP: no change (HP is full)".
- **Event** (S10): the paper's title follows the text size (`ZinePanel.scale_title`) and
  the panel starts `EVENT_TOP_GAP` under the subtitle band; the bar is hidden with no line
  (the dock refit on main keeps a line's label its height).
- **Pad prompts** (S11): `PadPrompts`, a row under the page (it covers nothing), shown
  while a pad is in use: HQ "A Select / Menu Settings", Grid and raid setup add "B Back"
  (B goes to the HQ), route "A Go", Modem "A Buy / B Leave" (B leaves the Modem), loot "A
  Take", event "A Choose"; relabelled on `Settings.hints_changed`. On a keyboard Esc stays
  the settings key (B's action runs only for an event that is not also `open_settings`).
- **Title Continue vs HQ Heat** (S12): not a bug. The title's Continue line summarises the
  newest of the three player slots (`RunManager.latest_slot`); the storyboard plays its
  campaign in its private slot `gut_storyboard`, so its title shot shows the designer's
  own slot 1 (Heat 14) and its HQ shot a new campaign (Heat 0). Left as is.
- Tests: `tests/unit/test_horizontal_pass23_screens.gd`. Updated on purpose: pass20's
  raid order badge expects "HP 50 > 40 HOLDS"; pass21's event row test compares with
  `OutcomeRow.shown`; pass22's route legend test expects the RouteLegend.

### 2026-09-27 — H23 city: mini-map labels apart, labels by their nodes, the key on the map, nodes beside the column
Pass-23 items K1-K7 (the City Grid screen, the map overlay, the HQ mini-map). View-only
(`scripts/ui/kit/`, the Grid page of `hq_scene.gd`); no rule or content change.
- **Mini-map labels are placed (K1).** `GridMapView` no longer stamps a label under every
  block: labels go by priority (selected, CORE, claimed, the rest; ties by Site id) to the
  first free spot round their block (below, above, right, left, corners) inside the view,
  never on another label (the tier pips are part of the label, so they never cover one),
  preferring spots off the other blocks. A crowded label drops to a shorter variant (name
  and detail, name, "T2 glyph", the pips alone) and is left out when none fits; every Site
  keeps a tooltip (`_get_tooltip`: name, tier, kind, status). `label_rects` for checks.
- **A label stays by its node (K2).** "Renewal Engine" floated over PREV SITE because its
  node sat under the side column and the H22 inward move shifted its focus label up out of
  the column, far from anything. Now a node off the visible map (outside the label area or
  under a blocked control) gets no label, and a moved label must stay within LABEL_REACH
  (110 screen px, to its nearest point) of its node.
- **No two map labels overlap (K4).** A focus label with no clear spot used to take the
  first moved spot even over another label; it now takes one clear of every label (it may
  cover an icon) or is left out. Order unchanged: priority, then node id (= Site content id).
- **The key sits on the map (K3).** The Grid's MapLegend left the scrolling column (it was
  its last item, below the fold): it is a *strip* legend (`MapLegend.pin_to(area, corp,
  true)`) along the foot of the map area, as wide as the map, rows in as many columns as
  fit (`set_strip_width`), with shorter row words (STRIP_ROWS). Its text is the compact
  size x text scale (rebuilt live). The Settings switch hides it and the map refits.
- **Nodes stay beside the column (K5).** `hq_scene.fit_grid_map` fits the Grid map into the
  map area above the key, once the page's layout has settled (next frame): when a node's
  icon or pips lie outside it, the camera pans and zooms out (never in past the Grid's
  own framing, now GRID_ZOOM 0.72 at GRID_ANCHOR (0.31, 0.54), was 0.85 at (0.4, 0.56):
  at text scale 1.0 the Grid then fits above the key with no refit). `LegendSpot.fit_into` works the frame out from where the icons
  are now (only the spread between icon centres scales; icons and pips keep their screen
  size), aiming FIT_INSET (8 px) inside so drift never asks for another pass; it is
  checked again once the city has drawn under the new camera (`NeonCity.camera_settled`,
  new: the camera inputs of the last draw), at most GRID_FITS_MAX (4) passes (H24 K3: this entry said 3; the code has had 4 since the change landed, and 4 stands). A resize,
  a text size change or the legend switch fits again. At text scale 1.6 the map is
  smaller (the column and the key take more room), never clipped, and never below
  GRID_MIN_ZOOM (0.3). The step row (PREV / NEXT SITE, Back to HQ, RAID SETUP) wraps
  inside the column (an HFlowContainer): as one row at 1.6 with a raid pending it widened
  the column over most of the map.
- **Tooltips name the kind (K6).** `CityLayout.KIND_TIPS`: each Site tooltip says its kind
  word and icon shape and what it does ("Exploit Site (diamond): clearing it gives an
  Exploit for the boss breach."), then its status; `CityMapOverlay.KIND_WORDS` /
  `kind_word`, `CityLayout.site_kind`. Used by the map, the mini-map and the run rows.
- **Run rows and steps carry their Site's icon (K7).** RUNS OPEN NOW lists one run a row
  (wrapping long names), each with its Site's map icon and tier pips and, for an objective
  Site, its kind word ("· EXPLOIT"); the tooltip adds what the kind does. PREV SITE /
  NEXT SITE show the map icon of the Site they step to (no pips, to keep the row narrow)
  and name it in the tooltip. Both controls kept (decided before).
- Test expectation changed on purpose: none of the H20-H22 tests changed; the Grid legend
  is still one MapLegend that follows the switch live.

### 2026-09-27 — H22 combat: now vs next, satellites that read, wheels that stay big
From pass 22 (both audits, a first-time player and a player who can't read English
looking at the new storyboards; GAP_ANALYSIS H22).
- **Now vs next**: the HP number under a wheel is the HP now (it agrees with the top bar);
  the forecast after SEND IT is a separate dashed plate with an arrow ("▸ NEXT 49"); the
  greyed LAST TURN line is the past. LAST TURN comes from the real HP change since SEND IT
  (CORRUPTED bites, heals and turn-start effects count), plus what block soaked, evades and
  hits a bodyguard or drone took; it shrinks to fit its box.
- **Satellites** dock past the slice values (they sat on them), are hit-tested before the
  nudge arrows (a drone near the top couldn't be aimed at 1.3+), and show their own
  needle's landing slice in a hex token with their HP (the name and the landing in words
  are the tooltip).
- **Big text**: the wheel keeps at least 80% of its size (the tag clamps to the view's top
  and the arrows draw over it); one chip row above 1.3; ring names scale a little.
- **Words and marks**: tags carry aim-quality pips; odds chips use whole words; satellite
  chips and hub lines say BLOCK / SHIELD / status words; names go through TextDb (runtime
  names kept for generated Mirrors). RESPIN and UNDO stickers carry drawn icons, SEND IT's
  key sits big under its lettering, the reticle has a crosshair mark, the ghost arc runs on
  the rim clear of the values, and an aiming hint says what to do.
- **Pad and keys**: the status line names the wheel and ring the nudges drive and their
  switches (LT / RT on a pad, W / R on keys); the ring switch refuses (with a toast) on a
  wheel without an inner ring, and switching wheels drops back to the outer ring. Aiming
  steps left to right across the screen. The tutorial teaches the switches, LAST TURN and
  NEXT, and uses the new words.
- Scripted cards (Calibrate, Momentum, Ring Lock, Steady Hand, Undock) get pictogram tags;
  the drag ghost carries the pictograms.
- Tests: `tests/unit/test_horizontal_pass22.gd`; LAST TURN totals checked against the real
  HP change in `test_horizontal_pass21.gd`. Views only: the balance numbers stand.

### 2026-09-27 — H22 screens: subtitles for any language, raid forecast wording, readable defences, labels that stay
Pass-22 items H22 #7, #9, #10, #12 and the screens' part of #14 (GAP_ANALYSIS). Direction
as before: nothing the player must read, tooltips, big text reaches everything, pad
players reach everything.
- **Subtitles page what is shown** (#7): `Dialogue` translates a line once
  (`shown_text` = `tr`, pseudolocalised when that is on) and pages that; the label's own
  auto-translate is off (a page would be translated again). Lines break at spaces, and a
  word wider than the band (Japanese / Chinese have no spaces, a long German word, a
  narrow dock) breaks by characters (pages joined without a space there, so no character
  is added or lost). A paged dock's label is as tall as its page's wrapped lines (the
  fallback font's height counted); a page still taller than the dock (accents stacked by
  pseudolocalisation) is drawn one size smaller, and the label clips to the dock as the
  last resort. BBCode brackets in the words are escaped. `dock_at(rect, lines)`,
  `pages_of` and the paging contract are unchanged.
- **Raid forecast** (#9): the raid card's stamp is a `ForecastStamp` (dashed ring like
  combat's NEXT plate): "IF THE RAID RUNS NOW:" over ALL HOLD / HOME HIT / CAMPAIGN LOST
  (BREACHED read as if the raid had run, beside "50 > 40 HOLDS"); its tooltip says it is a
  forecast, exact, and how to change it. The result screens keep REPELLED / BREACHED.
- **Raid layout** (#9): the side column takes the full height (the node list fills the
  spare height, `ORDERS_MIN_HEIGHT` at least) and the DEFENSE LOADOUT sits under the map
  beside it, so the asset cards are whole on screen at 1.6. The cards (`AssetCard`) scale
  their lettering with the text size (their size follows half of it), their numbers sit
  on a dark plate in light lettering and the disabled shade is lighter. Deploy cue: "1
  Pick a node" (map icon), "2 Press a card" (Armory icon) and "> <target>" beside the
  cards, each with a tooltip.
- **Legends clear of nodes** (#9, #14): `LegendSpot.place` puts a pinned legend at the
  first spot of its area (columns left to right, bottom up) that covers no node icon or
  tier pips, scaling it down only if it is bigger than the area; the screen registers the
  legend with `CityMapOverlay.avoid_controls`, so labels make way. On the raid setup, when
  every spot covers a node (threat routes cross the city), the camera frames the map
  beside the legend's column (`LegendSpot.fit_beside`: moved, zoomed out as far as that
  needs, at most `RAID_REFRAMES_MAX` passes). The route view (not zoomed) mounts the map
  legend in the room under the ROUTE choices (it had none). `avoid_controls` is wired for
  the Grid column, the ROUTE window, the raid setup (side, loadout, legend), the raid
  playouts and the raid report.
- **MORE BELOW over no control** (#10): `ScrollHint` puts a room of its own
  (`ScrollHintRoom`) after its ScrollContainer in the box container; while the content
  overflows, the room takes the tag's height and the view ends above it (kept while the
  content overflows, so the view does not jump as the tag comes and goes).
- **Crew by pad** (#10): the HQ links each dossier's orders top to bottom, left / right to
  the same line of the dossier beside it (JACK IN after the last), and down from a
  dossier's last order to the next dossier, then the Black Market (the page's row links
  only saw each column's first control, so the second Loadout was unreachable). At 1.6 the
  second dossier wraps under the first; MORE BELOW (in its room) says so.
- **Event outcomes** (#12): `OutcomeRow.of_choice` reads the amounts the choice will apply
  now, in the order the session applies them, without changing anything: a heal stops at
  max HP (+0 at full HP), Heat stops at 0 and at the maximum (a sink of 3 at Heat 1 shows
  -1); capped items say why in the tooltip. A rescue names no class ("rescue an
  operative": the class is rolled from the roster). The choice button's words come from
  the same items (`OutcomeRow.words`), so words, icons and result agree.
- **Words that stay** (#14): outside a fight the stat tags never go icon-only: when the
  fixed-width full tags don't fit, tags are fitted to their own words (name over icon and
  value) and shrink as a row, wrapping to two rows only below `FULL_MIN_FIT` of the text
  size (a narrow window). A fight (`max_height`) still goes compact to keep its height.
- **Icons** (#14): route buttons draw their node's map icon with the map's own painter
  (`IconMark.attach_map` -> `CityMapOverlay.draw_icon`, the map's colour for a next node;
  the StatIcon kind stays in the "icon_kind" meta); Grid RUNS OPEN NOW rows carry the
  Site's map icon (objective or tier, the map's colour) and the map's tier pips
  (`CityMapOverlay.draw_tier`) before "T1 <name>"; the operative dropdown has the
  operative icon beside it; the HQ JACK IN stamp carries the plug (`ZineStamp.icon_kind`);
  dossier Loadout / Recall / Station buttons carry cards / back / shield icons.
- Tests: `tests/unit/test_horizontal_pass22_screens.gd` (CJK, a long word and
  pseudolocalised text page inside the HQ band and a narrow combat-like dock at 1.0/1.6;
  the page shown is the translated one; the forecast stamp's words and tooltip; the raid
  legend covers no node and stays in its area at 1.0/1.6; the asset cards whole on screen
  with the deploy steps; MORE BELOW over no control on the HQ, Grid and raid at
  1.0/1.3/1.6; every dossier Loadout reachable by D-pad; rescue wording and capped
  amounts equal to the applied result; stat tags keep words at 1.6 on HQ, Grid, raid,
  route, Modem and event; the route legend on screen; route buttons draw the map icon of
  their node; Grid runs with map icon and tier). Updated on purpose: pass21's event
  outcome test expects the capped amounts.

### 2026-09-27 — H22 city maps: labels stay on screen, translated names, scaled legend, tier pips
Pass-22 items H22 #11 (map labels off the screen edge / under the Grid column; labels
skip TextDb), #9 part (legend and mini-map labels don't scale) and #14 part (no tier
difficulty cue). View-only (`scripts/ui/kit/`), no rule or content change.
- **Labels stay on screen.** `CityMapOverlay` now places labels only inside its label
  area (the overlay's own rect, or `screen_rect` within it, less EDGE_MARGIN 4 screen px)
  and off the screen areas a scene names: `avoid_controls([Control])` (their on-screen
  rects are read at each layout; the labels redraw when those controls move or resize)
  or `set_blocked_rects([Rect2])` (viewport px). A focus label (selected, you are here,
  threats) or a landmark's (CORE, the boss Site: `big`) with no free spot near its node
  takes a candidate moved inward (clamped into the area, then shifted the least way out
  of a blocked area) with its leader line; focus labels always show, landmarks show when
  a moved spot is clear; other labels with no spot are left out as before. The scenes
  call it once after mounting the map (screen owners' files): the Grid page
  `city_overlay.avoid_controls([column])` (the `GridColumn`), the route and zoomed Grid
  in the netrun `city_overlay.avoid_controls([win])` (the ROUTE window), the raid maps
  their side panels. Tested with the Grid column blocked, every node of every
  corporation (REBEL_CELL included) selected in turn at text scale 1.0 and 1.6, and the
  route's YOU ARE HERE.
- **Translated names.** `CityLayout.grid_graph` takes Site names through
  `TextDb.t(sd, "display_name")` (labels and tooltips); so does `GridMapView`.
- **Legend and mini-map follow the text size.** `MapLegend` rows are plain Labels (not
  fit-content RichTextLabels) at COMPACT_FONT 12 (pinned) / FULL_FONT 15 x text scale,
  with icon swatches and title scaled; the legend rebuilds when the text scale changes.
  Labels report their minimum size at once, so a pinned legend grows upward from its
  corner (and shrinks back) and never runs off its area; the full legend in a column
  keeps its 230 px width and wraps its text. `GridMapView` (the HQ mini-map) draws its
  labels at 9/10 px x text scale and redraws on `Settings.changed`.
- **Tier pips.** "T1-T4" is jargon, so every Site but CORE gets a non-verbal difficulty
  cue: a row of TIER_PIPS_MAX (4, SiteData.tier's range) pips under its map icon, `tier`
  of them lit in the node's colour, the rest hollow. One painter,
  `CityMapOverlay.draw_tier(ci, at, tier, col, scale, alpha)` (with `tier_pips_size`),
  is used by the map, the MapLegend's tier row ("Site tier: more lit pips, harder") and
  the mini-map (pips lead each label); the Grid Site list can use it too. Labels keep
  clear of the pips; the Site tooltip says "T2: difficulty 2 of 4".
- Not done here (other owners' files): the one-line `avoid_controls` calls in
  `hq_scene.gd` / `netrun_scene.gd`; the raid setup's pinned legend covering CORE is
  framing.

### 2026-09-26 — H21 combat: pad triggers, turn results, odds for random picks, words and pictograms
From pass 21 (vertical and horizontal audits, a first-time player, a player who can't read
English; GAP_ANALYSIS H21).
- **Pad**: LT switches the wheel the nudge buttons drive (yours / the target), RT the ring;
  one toggle per squeeze; the status line names them on a pad. A switch between mouse and
  pad keeps focus on the card that had it (the hand used to be rebuilt without it).
- **What SEND IT did** stays under each HP number ("LAST TURN: -3 HP · 5 BLOCKED",
  "NO DAMAGE") until the player acts; the motion pass (ANIMATION_HANDOFF 4.7) adds floating
  numbers on top.
- **Random picks during the resolve** (DOSE, Citations, Solar Flares, the Handler's
  corrupt) show "? RANDOM STATUS" and the slice odds, no ghost on the rolled slot (GDD
  2.10). The preview after a card uses the card's own RNG draws, so a reshuffling draw
  (Pull, Data Surge, Scrap Code, Tailspin) previews the real resolve.
- **HITS** counts the damage that lands per pointer (multi-pointer targets were
  under-reported), per victim: "HITS YOU 14" on an enemy's tag.
- **Satellites and Undock**: a nudge card or Undock dropped on a satellite takes its way
  from the side it is dropped on (arrowheads mark both sides); a custom handler declares
  `USES_DIRECTION` and `SCREEN_SIGN` (Undock's slot + 1 is anticlockwise on screen).
- **Room at big text**: the wheel shrinks so its tag (title + two chip rows; more fold into
  a "+N" chip) and its HP number and last-turn line stay inside its view at every text
  scale; `layout_violations` checks it. The refusal toast sits over the hand (it covered
  the HP arcs) with a drawn no-entry mark, and the RAM bar flashes when RAM was short.
- **Words**: tags read "DEFEND · good aim", chips BLOCK / SHIELD / CORRUPTED (Palette
  SLICE_WORDS, STATUS_WORDS, TIER_WORDS); the reticle says TARGET.
- **Cards show what they do**: `ZineCard.pictos_of` draws spin / nudge / flip / respin
  arrows, slice icons for damage, block, shield, evade, heal, deploy, statuses, and short
  tags (RAM, DRAW, SNAP, 2x NUDGE...) on every card; the focused card on a pad shows [A].
  While a card is aimed the other cards dim and a dashed line runs to the aimed zone.
- **More chips**: PHASE n, +n NEEDLE, NEW SLICES, 2x NUDGE CARDS NEXT, satellites' block,
  shield, healing, statuses and moves; the inner ring gets its own ghost arc.
- The Modem / Loadout spinner lays slots out the same way round as combat. Retired
  keybinds in an old settings.json are dropped on load; Heat chips are scaled per change as
  the netrun applies them; hub names go through TextDb.
- Tests: `tests/unit/test_horizontal_pass21.gd`. No rule changed (views, and the preview's
  RNG), so the balance numbers stand.

### 2026-09-26 — H21 city maps: node tooltips, you-are-here, readable labels, influence on each corporation's Sites
Pass-21 audits and naive-player reviews (H21 #14, #15, #22): map nodes showed nothing on
hover; the route had no "you are here" and every node looked reachable; node icons were
tiny, alike font glyphs; labels were ~8 px and overlapped; Halcyon's raid sway missed most
of its own Grid. View-only throughout (`scripts/ui/kit/`), no rule or content change.
- **Tooltips.** `CityMapOverlay._get_tooltip` hit-tests the node under the pointer (its
  icon first, then its roof) and returns `UiTip.fold(tip_of(id))`. A node's tip is its
  "tip" key (the route's NODE_TIPS; the Grid and raid maps' `CityLayout.site_tip`: name,
  tier, status, objective, CORE's loss rule) or, when missing, one built from its label,
  icon kind and mark. The overlay adds the route state ("You are here." / "You can move
  here now." / "Out of reach from here."), the raid result and the threats on the node.
  Clicks use the same hit test, so an icon is clickable too.
- **You are here, dimmed nodes.** Route nodes carry `here` (the current node) and `next`
  (open now) — a two-line hunk in `netrun_scene.route_graph`, beside the tip. The current
  node gets a pink ring and a pin, and its label reads YOU ARE HERE. On any graph with
  route state, nodes that can no longer be reached along the directed edges from here
  (and the open nodes) are drawn at DIM_ALPHA with no label; the Server Rack ahead stays
  lit. Grid and raid graphs carry no route state, so nothing dims there.
- **Icons.** Node icons are drawn shapes, not font glyphs (a stray glyph fallback showed
  a "y"): route — fight (circle, crossed blades), elite (8-point star), Modem shop
  (diamond, $), Terminal event (square, ?), Server Rack (hexagon, server blades); Grid —
  exploit (diamond), heat reduction (circle, snowflake), boss (star), CORE (house), tier
  (hexagon, T1-T4). Each kind has its own silhouette on its map. Icons are 13 px (17 px
  for CORE / boss) on screen whatever the city zoom, float over the roof on a stalk, and
  an icon that would sit on a nearer one floats up a step (front to back, ties by id,
  cached per camera). The selection ring now circles the selected icon. `MapLegend`
  draws its icon rows with the same painter (`CityMapOverlay.draw_icon`).
- **Labels.** TAG_FONT 13 screen px x `Settings.text_scale` (redrawn on
  `Settings.changed`, never per frame). Placement is greedy and deterministic: priority
  selected / you are here / threats, then reachable, claimed and landmark nodes, then the
  rest, ties by id; each label takes the first spot round its icon (right, left, above,
  below, corners, then further out, with a leader line) that overlaps no placed label,
  no icon and not the selection ring; non-focus labels with no free spot are left out
  (their node keeps its tooltip). The raid result is a second line of the node's label.
- **Influence follows the Sites (H21 #22).** Per the audit, 18 of Halcyon's 32 Site points
  fall outside its district. Rather than move the Grid layout (every map, route and the
  Site-to-building mapping would shift), the raid sway now applies inside the
  corporation's territory *and* within SWAY_REACH (4.5 lots, fading over 1.5) of any of
  its own Sites, whatever territory they stand in (`CityInfluence.sway_share`). Site
  pulls were already centred on the Sites. The influence carries its Site points, and
  their hash is part of the signature, so the bake key stays correct for generated
  (REBEL_CELL) Grids. The bake cache and live lights are unchanged.
- Not done here (other owners' files): the route (non-zoomed) view mounts no legend, and
  the raid setup's pinned legend can cover CORE at the left of the frame (hq_scene
  framing).

### 2026-09-26 — H21 screens: icons for every stat, wallet and price tags, event outcome icons, subtitles clear of the stats, big text everywhere
Naive-player reviews (first-time player; player who can't read English) of the
storyboard: GAP_ANALYSIS H21 #10-15, #19, #21 on the HQ, Grid, raid, route, Modem,
event, loot and title screens. Direction: nothing the player must read; tooltips on
everything; big text reaches everything; pad players see pad buttons.
- **One icon set** (`StatIcon`, STYLE_GUIDE 4.1): line-drawn vector icons (no font glyphs
  or emoji), `StatIcon.draw(ci, centre, radius, kind, colour)` from any draw pass, so the
  combat scene can use them too. Every stat tag carries its resource's icon (`HudStats`
  item's 5th field, else `StatIcon.kind_for(name)`): flame Heat, blueprint Schematics,
  house Home, diamond Exploits, shield Raids, snowflake ICE, people Crew, heart HP, coin
  Cycles, cards Cards, chevrons Rank, vault Banked (+ run end and profile tags). The same
  icon wherever the resource shows: CELL STATUS badges (`Badge.with_icon`), Modem price
  tags and wallet (coin), event choice outcomes, the Site card's Exploit / Heat badges,
  raid home badges.
- **CELL STATUS** badges name what they count: `HOME 50/50`, `EXPLOITS 0/3`,
  `ARMORY 3/6`, each asset kind as `Turret x1` (asset icon + short name + tooltip), no
  bare "x1".
- **Stat tags follow the text size**: full tags (name, icon, value) while they fit at the
  text scale (down to 85 % of it); otherwise compact tags (icon + value, the name as the
  tooltip's title) scaled to fill the row, up to the text scale. The HUD band grows with
  them, except in a fight (`HudStats.max_height`: the band keeps 56 px so the arena keeps
  its height; tags there scale to at most ~1.04 full / 1.27 compact). The screen title in
  the band takes only its own width.
- **Subtitles** (#11): a `SubtitleStrip` of their own, laid out like any row, so no
  control and no stat tag can sit under it: under the top bar on the HQ and netrun screens
  (one line, the full 1264 px width: ~140 characters a line at 1.0, ~88 at 1.6, so most
  lines need no paging and the "Rack." stale fragments are gone), beside the tag in the
  title's header (two lines). The strip registers its rect (`Dialogue.set_default_rect`);
  `dock_default` / `dock_bottom` use it (DEFAULT_DOCK is only the fallback), so a fight's
  exit comes back to it. It hides during a fight (combat docks its own). `dock_at`'s
  signature and paging are unchanged. Cost: about 32 px of height at 1.0 and 42 px at 1.6
  on those screens. Modal viewers (DeckView, SpinnerView, DaemonTray) open under the band
  (`SubtitleStrip.top_below`).
- **The Modem shows the wallet** (coin + Cycles) beside the shredder, whatever covers the
  top bar; LEAVE THE MODEM moved up into that quadrant's free corner so the Modem ends on
  screen at 1.6.
- **Price tags** (#12): `ZineCard.with_price(p, from)` hangs the price on a yellow tag with
  the coin (pink when out of reach); a card's circle is its real RAM cost; shop tiles
  (Firmware, Daemons, slices "100+" since the slot sets the price, SHRED) show their tag.
  `ZineCard` changes are additions (`price`, `price_from`, `with_price`, `tile_text`,
  `price_tag_rect`, `_draw_price_tag`, `_draw_tile_scaled`); `_draw` calls the tag and
  picks the scaled tile drawing only when `text_scale != 1`. The socket lists name slots
  ("Socket into Slot 1: CRIT 12 + Barbed Wire", `slot_name`), never ids. `with_card` on
  every card sticker built from CardData (Modem, loot, deck view and its detail).
- **Event outcomes** (#13): `OutcomeRow.of_choice(session, choice)` reads the choice data
  the way `NetrunSession` applies it (Cycles cost, HP loss, Cycles / Heat through
  `HeatRules.scaled_delta` / heal / Schematics, the reward's kind) and draws icon + signed
  number under the choice's words (green helps, red costs); the tooltip says it in words.
- **Menu icons** (`IconMark.attach(button, kind)`: a transparent icon slot sized to the
  button's font, the icon drawn in it; in terminal menus it replaces the chevron): title
  menu and slots, HQ CYBERDECK and start menus, Grid nav, raid, run start, route
  (GRID VIEW, Save & quit), Skip, Back to HQ, Continue; LEAVE THE MODEM gets an exit icon
  beside it. Every one has a tooltip.
- **Route** (#14, my part): each button reads "[1] Fight" on the keyboard and "1 Fight" on
  a pad (index on every device, the map label carries the same index), the node type in a
  word (Fight, Elite fight, Event, Shop, Rack) and its icon (crosshair, crown, terminal,
  bag, rack); the route graph's nodes carry `"kind"` (the icon) and a tip that starts with
  the word, for the city worker's map.
- **Big text** (#15): crew dossiers scale lettering and width; Modem cards scale to what a
  quadrant holds (1.31 at 1.6) and tile lettering scales inside the tile; loot cards scale
  to a 900 px row; deck view cards scale while a row keeps 4; PIRATE RADIO shows whole
  lines (4, the rest scrolls); the title's plan note fits its three lines; the Grid side
  column is a ScrollContainer (wheel, pad focus), the card over the full width, RUNS OPEN
  NOW before the map legend; a `ScrollHint` "MORE BELOW" tag sits at the foot of the HQ
  page (the Black Market) and of the Grid column while there is more below (press to
  scroll on). A long RAID PENDING item wraps in the menu instead of widening the HQ.
- **TextDb** (#19): recruit, boost and unlock buttons, asset / node badges and pickers,
  raid card title and warning, station orders, segment names, story beats, corporation /
  class / home names, the netrun raid interlude (it showed raw ids).
- **Naming** (#21): the Site card's launch button is JACK IN (as the HQ stamp, whose
  tooltip says: pick a Site on the Grid, then JACK IN on its card); the title's Continue
  line names the corporation; profile values show "—" (`HudStats.ice_value`), never
  "none" (also the HQ profile and Stats notes).
- Tests: `tests/unit/test_horizontal_pass21_screens.gd` (icons on every tag, badges,
  dock clear of controls and tags on HQ, Grid, raid, route, Modem, event, loot and title
  at 1.0 and 1.6, wallet, price tags vs RAM circles, socket names, outcome icons vs the
  data with `HeatRules.scaled_delta`, menu icons, route buttons on both devices, heights
  at 1.6, TextDb, naming). Updated on purpose: pass20 (pad route index, the dock rect,
  JACK IN), vertical pass 2 (price tag, JACK IN).

### 2026-09-26 — H20 combat: drag to target, nudge arrows, the outcome on the spinners
Designer direction (H20): ditch the nudge and card-target buttons for card drag-and-target
as in Slay the Spire; nudge arrows round each spinner; no text logs the player must read;
tooltips; spinner nudges and card results must read the right way round.
- **Cards are aimed, not toggled.** `CardTargeting.options` lists every legal play of a
  card (wheel, and for nudge cards the ring and the way, for chosen-slice cards the slice).
  Dragging a card lights its drop zones (a wheel, a nudge arrow, a slice, a docked
  satellite) and dropping plays it there; a click, 1-9 or pad A picks the card, then a
  click on a zone, or arrows / Tab / D-pad and Enter / A, confirms; Esc / B / right-click
  cancels. A card with one legal play plays at once. The card-target (T), direction (D) and
  slice (F) toggles are gone from play and from the Controls list (their input-map entries
  stay in project.godot, which holds the designer's uncommitted editor changes).
- **Nudge arrows on every wheel**: curved arrows at the top left (anticlockwise) and top
  right (clockwise), a second pair for an inner ring. The nudge keys' hints sit on the
  arrows of the wheel they drive (W / R still switch wheel and ring from the keyboard).
- **Direction reads the right way round**: the wheel is drawn mirrored so rotation +1 turns
  it clockwise on screen: a right nudge / E / RB moves the top of the wheel to the right
  (it used to move it left). The ghost arc now runs from the arriving slice (its icon) to
  the needle with an arrowhead the way the rim moves, in place of "-> tick N". View only:
  the rules, the preview and the tick maths are unchanged.
- **The full outcome is on the spinners** (GDD 2.10): `CombatOutcome.between` diffs the state
  before and after the resolve (plus campaign effects). Each tag shows what the needles
  land on, then chips: HITS n (damage dealt), -n HP / +n HP, +n BLK / SHD / EVADE,
  RESIST a→b, HUB BREACH, status glyphs (and dashed ghosts on the slice), DOWN, docked
  satellites' hits and losses, and on the operative RAM, DRAW, HEAT (as
  `HeatRules.scaled_delta` applies it), CYCLES, SCHEMATICS, FREE NUDGE NEXT, DAMAGE,
  +DRONE, VICTORY / DEFEAT. HP arcs show the predicted loss in red; the RAM bar shows the
  pending change. Hovering a card or a nudge arrow, or aiming a card, shows that play's
  result; random effects (Respin, random slice picks) show odds chips on the wheel they
  roll. The preview wall and log strip stay hidden records for tests.
- **Refusals toast** over the hand ("Not enough RAM..."); the **target wears a reticle**
  (a targeted satellite a ring on its host).
- **Right column**: Polaroid (operative name) and Heat, the Daemons as sigils with tooltips
  (the DAEMONS / INSPECT note is gone; pad inspect opens a popup beside the thing), then the
  combat subtitles (paged at up to 3 lines, fewer while the tutorial needs the room) and
  the tutorial under them. The top-of-arena dock covered the tags. RESPIN and UNDO stand
  between the hand and SEND IT.
- **Text scale** reaches the tags, chips, hub text, values, HP numbers, stickers, RAM bar and
  hand cards (the hand shrinks cards to fit beside SEND IT; long card text ends in an
  ellipsis, the whole text is the tooltip and the inspect).
- **Tooltips** on every combat control (slices, arrows, satellites, hubs, tags, cards,
  stickers, SEND IT, RAM, Heat, Polaroid, Daemons). `RamBar` ignored the mouse, which is
  one reason tooltips never showed.
- **Hints follow the device** (H20 1/n): pad players see pad buttons on the stickers,
  arrows, SEND IT and in the tutorial, which was rewritten for the new controls.
- `layout_violations` checks everything against each wheel's full drawing (radius + 66:
  values, satellites, HP arc) as a circle, tags against other wheels, and the subtitles
  against the tags.
- Tests: `tests/unit/test_horizontal_pass20.gd` (combat), updated layout, keyboard, pad
  and tutorial tests (the design changed on purpose).

### 2026-09-26 — H20 city backdrop: baked image, live lights, territory influence
Designer: "the performance is slow due to the backdrop... take a static image... add
blinking lights... the city should change colour as we or the corporation gain or lose
ground in the raid battles".
- **Measured cause.** NeonCity built its city in GDScript as one triangle array: 2.2-4.4
  million vertices, 0.9-2.9 s per build, redone on every camera change (Grid mount, every
  raid-playout camera follow step: ~0.9-1.1 s hitches) and, on the title, on *every
  frame* (the menu pan moved four offsets separately, so the size jittered and each
  resize rebuilt: 2.6-3.5 s per frame). Steady frames also re-rasterised the whole mesh
  through the sketch shader, and the Grid overlay redrew every node, tag and route each
  frame.
- **Baked image** (`CityBakeCache`, static, shared by every scene): a painter copy of the
  city renders the camera's view grown by 160 px (snapped to 128) once into a SubViewport,
  the pixels are read back into an ImageTexture and every view of that look draws the
  texture. Key = look (seed, district, net/physical, ink set, texture, sketch params,
  cultures, Heat creep in 0.05 steps, territory influence signature, window stretch) +
  region; any camera whose view fits inside a baked region of its look reuses it
  (backdrop, netrun and combat share one; the zoomed playout sits inside the Grid's).
  Bake scale 1.5 for net maps (zoom up to 1.9), 1.0 for backdrops, times the window's
  stretch, capped at 12 Mpx per bake; cache of 8 entries / 160 MB, least recently used
  out. Painters draw in world space (world-anchored hashes), so bakes of one look match;
  they set a custom cull rect (they draw outside their control rect). While a bake runs
  the last image of the look (or the previous look) stands in. Headless has no renderer:
  `can_bake()` is false and the procedural path runs as before (tests unchanged); an
  empty readback marks the entry failed and the city falls back the same way.
- **Live layer** (all positions from layout hashes, no RNG): blinking window lights (3 %
  of lit windows, 2.4-7.4 s periods, lit 70 %) and beacons blink on the GPU
  (`shaders/city_lights.gdshader`, geometry built once per camera); traffic sparks on busy
  streets and a short sign flicker dip (7 % of a 3.2 s period) are the only per-frame
  drawing (caps: 220 lights, 240 beacons, 120 sparks visible). Reduce effects freezes it
  all (shader `animate` 0, no redraw). Scanlines and flicker stay live in
  `shaders/city_live.gdshader`. The CityMapOverlay is layered: static under-layer and
  nodes redraw only on change; only flowing dashes, packets and the selection pulse
  redraw per frame. The title pan moves the city (`position`) instead of resizing it.
- **Territory influence** (`CityInfluence`, pure, Sites in id order): claimed +1 (a
  disabled claimed Site -0.6 back), cleared +0.45, Seized -1, falloff (1 - d/7.5 lots)^2;
  raid balance sways the corporation's whole territory 0.08 per net raid (cap 0.32).
  Positive leans lines (up to 55 %) and ground (16 %) toward the Cell pink, negative
  toward the corporation. Backdrops follow `RunManager.campaign` (`follow_campaign`, read
  every 0.5 s and at each re-frame); a change re-keys the bake once.
- **Measured** (1280x720, RX 6700 XT, vsync off, 8 s after 120 warm-up frames,
  `tools/city_perf_probe.gd`), frame avg / max: HQ 6.06 / 10.7 ms -> 1.46 / 2.8; Grid
  16.90 / 29.1 -> 2.12 / 7.6; raid setup 7.70 / 12.6 -> 1.34 / 11.9; raid playout 5.73 /
  1108 (camera-follow rebuilds) -> 0.98 / 11.3; combat 5.91 / 11.6 -> 1.36 / 18.4; netrun
  Grid view 4.80 / 12.3 -> 0.68 / 2.4; title 2600-3500 ms per frame -> 1.10 / 8.3. GPU
  time 2.0-3.8 ms -> 0.3-0.9 ms. First bake of a view costs about what one build did
  (scene start 2.5-3.5 s -> 3.0-5.2 s including the bake's margin and readback); later
  visits cost nothing. Bake memory 7.6-22.5 MB per view; total VRAM 159-324 MB ->
  157-316 MB (the old per-view vertex buffers were larger than the textures).
- **H20 #14**: REBEL_CELL's colour is now #E8141E (deep red; was #FF2A6D next to the Cell
  pink). Claimed Sites carry a spray ring (with drips) and Seized ones a cross on every
  city map; MapLegend rows use their own glyphs (○ claimed, ✕ seized). The palette
  change also recolours REBEL_CELL's enemy wheels (wheel_view.gd reads Palette only).
  STYLE_GUIDE §2 updated to match.
- **H20 #22**: raid setup, playout and summary maps pin a compact MapLegend to the map's
  bottom-left; the HQ Grid's Site list resizes with the legend switch live
  (`MapLegend.link_size`); the mid-run raid playout plays on the city overlay (whole Grid,
  zoom 0.85, feed at the side) instead of the old GridMapView.

### 2026-09-26 — H20 screens: no text logs, tooltips, subtitles clear of controls, pad reach
Designer: "ditch any text logs that we expect the player to use" and "there are no
tooltips". GAP_ANALYSIS H20 items 7, 9, 10, 13, 16, 21, 23, 24 (ModemSign, unused kit),
25 (demo profile, STYLE_GUIDE 7), 15 (kit tests) on the non-combat screens.
- **What went and where each fact shows now**:
  - HQ `SYSTEM ONLINE` readout -> `CELL STATUS` badges (`Badge`, a hex glyph or asset
    icon + a short value + a tooltip): home integrity with a meter, each Exploit found (or
    `0/N`), each Armory asset kind by icon and count, every rule a crossed Heat threshold
    added ("Raid strength +10%", no enum names). Heat, Schematics, Home, Exploits, Raids,
    ICE and Crew stay on the top bar's tags, which now say what they mean on hover; the
    wanted poster's tooltip gives the next threshold and the rules in force.
  - Grid `THE PLAN` note and the `SITES // NODE STATUS` list (raw ids, raw links) -> the
    picked Site's card (`SelectedSite`: status, objective, node + integrity meter,
    upgrade level, assets, the stationed operative as badges; launch / claim / repair /
    upgrade under them), `RUNS OPEN NOW` (one button per launchable Site and patrol, the
    old plan's "->" lines), `< PREV SITE` / `NEXT SITE >` (every Site by pad), Back to HQ
    and, with a raid pending, RAID SETUP. The first open run is picked when nothing is.
    Links, statuses and objectives are on the map (unchanged). Dropped: "ICE switched
    off: ..." as a list (the Site card shows "off" on such a Site) and the plan's
    Exploit/ICE/Heat line (top bar).
  - Raid setup `THREAT ROUTE` text wall -> the raid card: the projected result as a stamp
    (HOLDS / BREACHED / LOST), badges for home before > after (meter), threats destroyed of
    all, strength %, one badge per entry Site, link changes (text in the tooltip); the
    raid's warning in the card's tooltip. `NODE ORDERS` text rows -> `YOUR NODES`: per node
    a target button (name) and its exact projected outcome badge ("30 > 22 HOLDS", GDD 9.3
    still visible per node, also on the map), its assets as icons; the target's row
    carries Withdraw / move buttons with names.
  - Raid report lines -> badges with Site names; the netrun end note -> the run's numbers
    as paper tags (`HudStats`); the title's SYSTEM ONLINE line -> profile tags.
  - The log strip stays behind its Options switch (off by default) as a record. What the
    player must see once (refusals, launch errors, "Saved.", unlocks) now also pops a
    `ToastNote` at the foot of the screen for 3.5 s (mouse- and focus-transparent).
- **Tooltips**: Godot's tooltip popup is parented to the hovered control, so it takes
  the screen theme (`TooltipPanel`: dark glass, pink edge; `TooltipLabel`: scaled mono);
  its label never wraps, so every long tooltip goes through `UiTip.fold` (56 columns at
  1.0, fewer at larger text). Kit controls that draw themselves build a titled body
  (`UiTip.make`, `_make_custom_tooltip`): badges, HUD tags (per tag, `_get_tooltip`),
  the wanted poster, crew dossiers. Tooltips on: HQ menu, market, dossiers and their
  orders, JACK IN, the monitor; Grid card actions, open runs, nav; raid card, targets,
  asset cards (with the target they deploy to), moves; route node buttons (what each node
  type holds, Heat); Modem firmware slot, LEAVE THE MODEM; reward skip and slot; deck
  stickers, spinner pads (with the slot's price), hub / ring pads, Daemon sigils.
  Mouse filters: the tags and the poster pass hover (they ignored it before).
  City map nodes: the route graph now carries a `"tip"` per node; drawing it on hover is
  CityMapOverlay's (city worker's file).
- **#7 subtitles**: the default dock (`Dialogue.dock_default`, `dock_bottom` kept as its
  alias for the combat scene's exit) is the top band `DEFAULT_DOCK` (8,2)-(972,54) over
  the screen title and the stat tags: every control on the HQ, Grid, raid, Modem, netrun,
  title, pause menu and viewers sits below it or right of it (VIEW LOADOUT, Daemons).
  The speaker's name leads the line ("DISPATCH: ...") and long lines page to the lines
  that fit at the current text size (`lines_fitting`; 2 at 1.0, 1 at 1.6). Paging reads
  the text size at each line. The HQ, netrun and title scenes dock on `_ready`; combat's
  own dock is unchanged. Trade-off: while a line is up it hides the stat tags.
- **#9 modals**: `UiFocus.hold(view)`: while DeckView, SpinnerView, LoadoutView or
  DaemonTray is open its siblings' `focus_behavior_recursive` is off (the D-pad, Tab and
  A can't reach the Modem or HQ behind), key / pad events stop at the view (no route
  1-9 behind the loadout), and on close the siblings come back and focus returns to the
  control that opened it. Views keep Godot's geometric D-pad search inside.
- **#10**: raid setup target by pad: each claimed node's target button in YOUR NODES
  (`select_target`), focus stays on it; asset cards then deploy there.
- **#13**: the Modem's UPGRADE A SLICE title has no price; `SpinnerView.set_prices`
  shows the picked slot's own price beside UPGRADE (pink and UPGRADE off when short);
  each pad's tooltip names its price (Miss 150 vs 100, config).
- **#16**: `Settings.hint()` everywhere outside combat, refreshed on
  `Settings.hints_changed`: HQ Settings / Options, Resume, the Close buttons of DeckView,
  SpinnerView and SettingsPanel, the viewers' "Left click / Right click" line (pad: its
  buttons), the route's node numbers (none on a pad) and the route map labels. ZineStamp
  has an optional `hint` (default ""): JACK IN shows none; result stamps are
  `display_only()` (no focus, no clicks), so Back to HQ gets the netrun end's first focus.
  The pad can inspect a deck card or slice with its inspect button.
- **#21**: Site display names everywhere (`site_name`; the home server is CORE as on the
  Grid): raid map labels, crew stamps "ON <SITE>", station / recall orders, raid orders
  and moves, the raid report; asset and node type display names; queued boosts by name.
- **#23**: `selected_operative`: a dossier's Loadout opens its operative and makes them
  the one the top bar's VIEW LOADOUT and DAEMONS show; LoadoutView's NEXT OPERATIVE tab
  cycles the living crew; the Daemon tray names its operative. The loadout spinner draws
  the hub core and the inner ring (rank rewards and Rank 3 swaps applied,
  `LoadoutView.core_of`) as pads with details. Faces: `PortraitArt.operative_subject(
  class_id, operative_id)` / `draw_operative(ci, rect, class_id, operative_id, name)` hash
  class + operative id (no RNG) into hair, visor and tint; `Polaroid.set_operative`,
  `CrewCard.set_operative`; the wanted poster shows the selected operative through
  PortraitArt (`Polaroid.draw_silhouette` removed). Combat can call the same API.
- **#24**: ModemSign's notes read BUY / SHRED (nothing is sold back) and its pink is
  `Palette.CELL_PINK`. Unused kit classes deleted: RaidBoardView, DripLabel, NeonSign,
  NeonTag, ScreenHeader (none served the redone screens). Netrun's `corp_creep` uses
  `heat_max`.
- **#25**: slots starting with `demo` keep a private profile like the `gut_` test slots
  (`RunManager.is_private_slot`), so `--demo-*` captures never bump the player's
  campaigns. STYLE_GUIDE 7 describes PortraitArt instead of grey placeholders.
- Tests: `tests/unit/test_horizontal_pass20_screens.gd` (with the bar-vs-control overlap
  measurement at 1.0 and 1.6 on HQ, loadout view, Grid, raid setup, HQ start, pause
  Options, Modem, title Codex and Controls). `test_layout_rules` checks the Site card
  instead of THE PLAN; `test_visual_merge` checks that the default dock pages.

### 2026-09-26 — Merge: visual/UI pass into main (H17-H19 behaviour kept)
The visual branch (`claude/game-visual-ui-update-pkc0aj`, forked at H16) is merged. Its
look wins; main's H17-H19 behaviour is kept or remapped onto the new controls:
- **Pause menu**: the branch's terminal-glass panel over main's full-screen click-eating
  `Backdrop` (H17), focus trap, Esc handling and `MENU_SIZE`.
- **Options**: the branch's map legend and system log switches (Display section) plus
  main's `bind_error` refusals in the wrapped `BindNote`, `reset_keybinds()` keeping pad
  buttons and `UiWrap.fit`. Settings serialise every field of both sides.
- **Combat key hints (H19 on the new UI)**: every sticker names its bound key
  (`[Q]`, `[W]`...) and SEND IT's drip lettering shows the bound End Turn key under it;
  both refresh on `Settings.changed`. The hidden dropdown row keeps its hint text (the keys
  still drive it and tests read it).
- **Stickers never lie on a slice (GDD 9.2)**: the branch placed them round the spinner,
  where they covered the value labels and the ring (worse with key hints and at text
  scale 1.6). They now stand in one column left of the player spinner and the spinner
  centres in the rest of its column (`WheelView.left_reserve`, shrinking if needed).
  Sticker lettering follows the text scale. `layout_violations` checks the stickers and
  the intent tags against every wheel.
- **Combat subtitles**: the dock spans the arena above the spinners and pages long lines
  at two lines (`Dialogue.dock_at(rect, max_lines)`), so at text scale 1.6 the longest
  line never reaches a wheel; the bottom bar grows upwards as in H18. History keeps the
  whole line.
- **Log strip, preview wall, dropdown row**: the visual pass wins (hidden; the intent
  tags carry the preview). H13's "tutorial over the log strip" is superseded by the
  branch's tutorial fit between the inspect note and SEND IT.
- HQ keeps main's `Settings.key_text` hints on the branch's CYBERDECK menus; recruits
  (with `rookie_price`) moved to the branch's market.
- Test: `tests/integration/test_visual_merge.gd`. Timeline: `13_merge`.

### Visual pass: readability and portraits (2026-09-26)
- The system log strip (HQ, netrun) shows only when "System log strip" is on in Options
  > Display (`Settings.system_log`, off by default). Test: `test_layout_rules`.
- Dripping pink lettering (every `DripButton.draw_drip_text` use: title and HQ tags,
  scrawls, SEND IT, LEAVE THE MODEM, deck/spinner actions, loot) has a thin white
  outline round letters and drips (`DripButton.OUTLINE_PX`).
- Terminal panels are more opaque with a soft dark halo, so text reads over the city.
- Combat docks the DISPATCH / corporate subtitle bar in the top strip
  (`Dialogue.dock_at`), clear of the hand and SEND IT; the tutorial note fits between
  the inspect note and SEND IT.
- Zine paper panels: the drop shadow no longer darkens the whole sheet, and the halftone
  is spaced in pixels (the event panel read as flat grey before).
- Portraits: `PortraitArt` draws every Polaroid until final art, in four review styles
  (`--demo-portrait=N`: 0 neon bust (default), 1 xerox zine, 2 wire scan, 3 mugshot) for
  operatives, corporate agents, machines, bosses and corporation faces; sheets from
  `tools/design_lab/portrait_concepts.tscn`. Enemies, bosses and corporations have no
  portrait slot on screen yet; the owner picks a style first.
- Motion roadmap handed off in `docs/ANIMATION_HANDOFF.md`.
- Godot note: a `const` typed as `Array[PackedVector2Array]` built from nested literals
  sometimes read back garbage coordinates at runtime (seen as a hang: a stroke millions of
  px long). `FIST_POLYS` is a plain nested Array, and `_stroke` caps its step count.

### Visual pass: spinner slices (2026-09-26)
- Slice colours: attack/crit neon pink (`CELL_PINK`), defend/shield cyan (`NET_CYAN`);
  evade/heal, afflict and deploy unchanged. Wedges are translucent (the city shows
  through) with a bright rim.
- Slice icons are solid black with a white outline (`SliceIcon.draw_on_slice`). Review
  styles behind `--demo-iconstyle=N` in combat: 0 black & white, 1 badge, 2 inverse
  badge, 3 glow, 4 bold. Owner's pick: 4 bold is the baseline.

### Visual pass: landmarks and the Cell's fist (2026-09-25)
- The Cell has no HQ tower on the city. Its territory builds like the Sprawl (its own
  colour kept) and its roads etch a raised fist (traced from the owner's reference icon;
  `NeonCity.FIST_*`). No ordinary street runs inside the fist's silhouette
  (`FIST_HULL`): streets end on its outline and the blocks inside are built up at the
  usual heights; only lots on the fist roads stay empty. `hq_of(&"rebel_cell")` still
  marks the fist's centre, so camera framing and the city layouts are unchanged.
- The city now draws all ground first (streets, plazas, lot floors), then the fist
  roads, then everything standing, back to front.
- Solace's HQ is a wide DNA double-helix tower in neon-outlined tubes with base-pair
  bridges on a plain podium; the Egyptian HQ's pyramid is lower on a flat terrace, with
  colonnades, gold hieroglyph friezes on the base and the pyramid, braziers and a doorway.
- Wall texture options (`NeonCity.face_texture`, `--demo-texture=N` on the title
  screen): none (default), panel seams, dark pen hatching, grime stipple, concrete grain,
  matte stone, brushed metal, hatching on stone, hatching on metal (4-8 in the sketch
  shader's `wall_mode`). (Superseded below: strong tinted slate is the baseline.)
- Added 9 painted slate and 10 dark slate, modelled on the reference sheet's panel 6:
  blue-grey walls lit from above and falling into shadow at the base, panel detail drawn
  in face space (ledges, recessed panels, ribs, vent grilles, amber light slots), roofs
  with a raised rim, a recessed deck and the odd plant box, a soft painted grain and a
  gentler saturation boost on the walls (shader `wall_mode` 4). Round towers keep only
  their silhouette and front edge lines so they read as one shaded mass. HQs keep their
  own look.
- Added 11 tinted slate and 12 strong tinted slate: the painted slate leans 30% / 50%
  toward each building's line colour (`SLATE_TINT`) with full saturation and the same
  painted grain (shader `wall_mode` 5), so territories keep their colour identity.
- Owner's pick: strong tinted slate (12) is now the baseline wall look everywhere the
  city is drawn (`NeonCity.DEFAULT_TEXTURE`); the other options stay behind
  `--demo-texture=N` for review.

### Visual pass: combat and Modem built (2026-09-25)
- Combat (owner's picks): spinners as neon gauge bars with drawn slice icons in the
  wedge, values outside (full slice text on hover), white in-slice "perfect" arrows, white
  gauge-needle pointers, HP as a segmented arc with the numbers in its gap, a bare RAM
  chip bar. What will resolve is a taped tag over each spinner (from the same end-turn
  preview as before, so tag = real result). The log strip and the preview wall are no
  longer shown (kept hidden as the text record the tutorial and tests read). Nudge,
  respin, undo and the old dropdown toggles are stickers around the player spinner (keys
  unchanged). Click an enemy spinner to target it. SEND IT is drip lettering.
  `test_layout_rules` updated to these rules.
- Modem: the vertical circuit-board MODEM CYBER SHOP sign on the left of the quadrants.
- City: HQs doubled (10x10 plazas) with added detail; streets without traffic dashes.

### Visual pass: owner picks (2026-09-25)
- City: sketch jitter 0; Cool Haze palette default; busy streets drawn as re-stroked bands.
- The Grid, raid setup, raid playout, raid summary and netrun route are drawn ON the city
  (CityMapOverlay): Grid = rest of the city greyed; raid setup greyed; raid live zoomed on
  the fight with the camera following the threats (no inset); route = blueprint look with
  a GRID VIEW toggle zooming out to the Grid. The floating summary maps remain for the
  HQ monitor only.
- Top bar: neon title + ransom-note stat tags + VIEW LOADOUT (deck and spinner).
- Deck / spinner views: left click selects (hand-drawn X to remove, drippy circle to
  upgrade), right click shows details; drip-lettered action beside Close.

### Visual pass: neon city (2026-09-25)
Directed by the project owner from `docs/reference/ChatGPT Image Sep 24, 2026, 08_08_40 PM.png`.
View code only; no rules, content or schema changed.
- **Backdrop:** `NeonCity` (scripts/ui/kit) replaces the flat window and wireframe skyline in
  both worlds. It draws an isometric city with dark masses (black, dark grey-blue, dark grey)
  inked in amber, purple, pink, cyan and green, over an irregular street grid. The
  `city_sketch` shader adds vertex wobble, grain, a saturation boost and faint scanlines.
  Each corporation has a district profile (building mix, height, colour share) and a
  unique landmark HQ; the backgrounds follow `campaign.corporation_id`.
- **CRT:** the screen-wide overlay keeps only a faint vignette and flicker (its uniforms
  remain for reduce-effects). Scanlines are applied locally, only to the city and terminal
  glass (`crt_panel` shader via `UiTheme.crt_material()`), never to paper, Polaroids or stamps.
- **Theme:** controls are terminal glass (navy, thin cyan edge, pink hover, acid focus).
  Type variations: MenuItem, TerminalPanel, GlassPanel, HudLabel, LogText, HotButton,
  NoteButton. New kit: TerminalWindow, ScreenHeader, HudBar, GraffitiScrawl, NeonSign,
  NeonTag, CrewCard, AssetCard, AssetIcon, RaidBoardView.
- **Screens:** HQ (menu, City Grid monitor, crew dossiers, wanted, radio), Modem (reference
  cyber shop), raid war table for setup, playout and summary, Terminal events with
  taped-note choices, and system dialogs as terminal glass.
- Screenshot shortcuts added: `--demo-event`, `--demo-dispatch`, `--demo-loot`,
  `--demo-playout`, `--demo-codex`, `--demo-stats`, `--demo-district=<corp>`.

### 2026-09-25 — Horizontal pass 19 fixes (GAP_ANALYSIS H19)
- **A refused rebind is explained in a wrapped note under the Controls grid** (the key
  button keeps its width), so Options never runs off the screen at text scale 1.6.
- **Every combat key hint follows the binds** (nudge wheel, ring, card target, direction,
  slot, nudges, Undo, Respin, Settings) and refreshes on `Settings.changed`; the HQ
  Options / Settings buttons show the bound Pause key.
- **A Mirror copy keeps a Parasite** (halved): H18 only meant to drop the Overclock boost.
- README lists all nine autoloads.

### 2026-09-25 — Horizontal pass 18 fixes (GAP_ANALYSIS H18)
- **Reset to defaults keeps the pad buttons** (it re-applies the controller binds).
  Rebind refusals name the action as the Controls list does.
- **The combat pause menu uses the game theme** (a CanvasLayer cuts theme inheritance, so
  it gets `UiTheme.apply`): the game font and the text scale reach it again.
- **Subtitles follow the text scale** (speaker 12, text 15 at 1.0), and the bar grows
  upwards.
- **A Mirror copy drops the slot's temporary statuses** (see the H17 entry); **Stolen
  Intent swaps slices without permanent statuses** (no Burner Overclock without its Heat).
- Balance after H18: Breaker ICE 5 2/8 in 48.8 runs.

### 2026-09-25 — Horizontal pass 17 fixes (GAP_ANALYSIS H17)
- **The pause menu blocks the mouse**: a full-screen backdrop (`MOUSE_FILTER_STOP`, dim)
  sits behind it, so clicking SEND IT, a map node or an HQ button behind the menu does
  nothing (H15 blocked keys and pad only).
- **A Shunt resolution is the landing everywhere**: its slice's CORRUPTED bite and
  OVERCLOCKED burn-out apply, Stolen Intent fires on a shunted Miss, and the operative's
  drones follow the slot that actually resolves (GDD 5.2).
- **A copy resolves the neighbour's slice, not its Firmware** or the permanent status
  that Firmware grants (Burner's Overclock without its Heat). H18/H19: a Mirror copy of an
  Overclocked slot is not boosted (the boost belongs to the landing that burns it out);
  other statuses still apply to the copy (a Parasite halves it; a copy never bites). A
  Shunt resolution is the landing and keeps them all.
- **Rebinding refuses 1-9, Enter and Esc and any key another action holds**
  (`Settings.bind_error`); the button says why and keeps waiting for another key.
- Balance after H17: Breaker ICE 5 3/8 in 48.1 runs (was 4/8 in 42.8).

### 2026-09-25 — Horizontal pass 16 fixes (GAP_ANALYSIS H16)
- **A landing is the pointer's slice, or what a Shunt resolves instead**
  (`CombatResolver.is_landing`). A Mirror copy of a neighbour is not a landing: Daemons
  don't fire on it (a Mirror Perfect used to fire Kernel Sync, Clean Signal, Botnet Seed
  three times), and a copied Miss doesn't resolve the Miss for Cold Exit, Zero Day or the
  consecutive-Perfect count. The copies still resolve the slice and the Hub (H17: not the
  neighbour's Firmware or the permanent status it grants).
- **A MULTIPLY or MIGRATE phase stops an earlier orbit**: Commons Array's 33% readers
  "lock on" as its phase line says.
- **Rebinding captures every key** in `_input` (arrow keys, Tab), before focus navigation.
- **The combat pause menu is on its own CanvasLayer**, centred on the viewport, so the
  netrun scroll can't clip it.
- **Esc in the pause-menu Codex returns to the menu** (as Esc in Options does).
- Balance after H16: Breaker ICE 5 4/8 in 42.8 runs (was 5/8 in 36.4; the bot's Mirror
  Firmware had been tripling its Daemons). See the pacing open question.

### 2026-09-25 — Horizontal pass 15 fixes (GAP_ANALYSIS H15)
- **Daemons fire once per landing.** A Perfect resolves two or three times (every Hub
  Core retriggers, Echo adds one), and each extra resolution used to fire the Daemons
  again: Clean Signal gave -4 Heat for "-2", Zero Day was a 6x Crit for "3x", Kernel Sync
  +2 for "+1". Now the slice, its Firmware, segment and Hub repeat with every resolution
  (the M1/M6 rulings stand) and Daemon listeners fire once after the resolutions. The Hub
  Core texts now say "on each resolution" for their hook effects.
- **Nothing acts behind the pause menu**: while it is open it swallows unhandled keys and
  pad buttons (Space, 1-9, Q/E, LB/RB, Tab), in combat, on the map and at HQ.
- **The pause menu is 760x520** and its Options panel reports its content's size, so the
  menu's scroll reaches Close, Reset and every rebind button at text scale 1.6.
- **Intel's phase reveal shows the real layouts** (`CombatResolver.phase_layout`: Breach
  removal and the ICE extra pointer), plus the orbit speed of an ORBIT phase.
- **Firmware per-combat limits: one counter per Firmware id, the limit times the copies
  socketed.** H14 keyed it by slot, and a Flip moves Firmware between slots, which gave
  fresh charges (Skimmer fired four times). Two copies still have two charges each.
- **Repair shows its price** (`CampaignRules.repair_cost`, ICE 13 included).
- **The End Turn preview shows odds only for random status picks** (DOSE); a fixed slot
  (Overclock burnout, a Perfect Parasite, the Corrupt segment) says which slot.
- **Config**: `achievement_ice_low` 5 and `achievement_ice_high` 10; the Rack tier index
  is bounded by the Rack tables. TECH_SPEC 8 lists the quit and window-close saves.
- **Balance after H15** (Daemons no longer doubled): Breaker ICE 5 5/8 in 36.4 runs;
  Ghost ICE 0 6/8 in 27.1; Botnet ICE 0 8/8 in 22.1; Rigger ICE 0 5/8 in 36.5 (was 7/8 in
  19.8: it leaned on doubled Daemons). Kept on the harder side; see the open question.

### 2026-09-24 — Horizontal pass 14 fixes (GAP_ANALYSIS H14)
- **Boss phases keep their layout and ICE extras**: an ORBIT phase that lists pointers
  sets them before orbiting (Commons Array 66%: two readers; Civic Core 33%: two). The ICE
  16-20 extra pointer and the ICE / Heat bonus resistance are stored at setup and re-added
  after every MULTIPLY / MIGRATE layout and wheel swap.
- **Heat-gated effects can ride attacks only** (`HeatGatedEffectData.offensive_slices_only`,
  schema change): Compliance Officer's Audit drains RAM on its Attack and Crit slices only.
- **Mirror elites run their own Daemons**: enemy hubs fire ON_COMBAT_START effects (Shield
  Cache), and enemy Perfect hooks need no streak (the consecutive-Perfect counter is the
  operative's; an enemy hook with consecutive_required > 1 never fires).
- **Rig Core's free nudge arrives**: free nudges earned while resolving are banked in
  `CombatState.free_nudges_next_turn` and added at the next start of turn.
- **Ghost Core covers card nudges**: the first N nudges on enemy wheels each turn, from an
  action or a card, ignore resistance (one shared counter).
- **Firmware per-combat limits count per slot**: two Coolant Loops have two charges.
- **Text fixed to match the rules**: Nanite Mesh "cleanses itself after resolving"; Snap
  "your outer ring"; Locked Ward rescues "another runner"; The Old Crew "Open the cells"
  (no rescue); the Armory sabotage no longer claims weaker raids; Returns Desk result.
- **Terminal Firmware that fits no slice is refused** (button disabled, reason shown);
  zero-Cycle filler effects no longer print "+0 Cycles".
- **Modals trap focus** (`UiFocus.trap`): confirm dialogs (Yes and No reach each other)
  and the pause menu, its Options and Codex. The pause menu scrolls vertically and wraps.
- **Text scale 1.6 fits**: the netrun and HQ status bars wrap, the standalone combat top
  row flows and hides the dev fight picker in the Tutorial, and the tutorial note starts
  at the top and scrolls by pad.
- **Achievement thresholds from config** (`achievement_racks` 10, `achievement_raids` 20,
  `achievement_perfects` 500); Purge Survivor tracks the top Heat threshold.
- **Closing the window saves** (`NOTIFICATION_WM_CLOSE_REQUEST`), so a fight resumes where
  it was; a resumed run's outcome is recorded in history and stats.
- Balance after H14: Breaker ICE 5 5/8 in 31.6 runs, Ghost ICE 0 7/8 in 24.0, Rigger ICE 0
  7/8 in 19.8.

### 2026-09-24 — Horizontal pass 13 fixes (GAP_ANALYSIS H13)
- **Cards move the ring they name**: a NUDGE effect with ring_scope INNER (Ring Tap,
  Ratchet, Inner Drift, Gear Shift) always moves the inner ring. An outer-ring nudge card
  (Fine Tune's "one ring", Jam, Tap Tap) follows the ring toggle, and falls back to the
  outer ring on a wheel without an inner one instead of spending the card for nothing.
  Snap's text now says it snaps the outer ring (Inner Snap does the inner one).
- **Resistance changed while the turn resolves lasts**: a change made during RESOLVE
  (Ghost Core strip on a Perfect, Tracer, an enemy's own +resistance slice) carries into
  the next turn's restore (`CombatantState.resistance_carry`), then full resistance
  returns a turn later. Changes made in the player phase (the Strip card) work as before.
- **A kill outside resolution ends the fight**: after a card play and after start-of-turn
  effects, deaths are settled and the outcome checked (Static Shock and friends no longer
  leave a 0-HP enemy standing).
- **Terminal choices show their real costs**: the button text uses the choice's data
  (Cycles, HP, Heat as it will apply at the current ICE, rewards) in place of the
  hand-written summary. A choice is refused, and its button disabled, when it costs
  Cycles you don't have, would flatline the operative, or grants a Daemon already
  installed. Returns Desk's "Return a Bug" (it never took a Bug) became "Trade in store
  credit".
- **Rack Heat labels include Scrubber's override**.
- **The tutorial sits over the log strip** (right column, never on a wheel), is part of
  the layout check, and names the bound keys; the combat buttons do too.
- **Momentum**: Spin `amount` (2), or amount x multiplier (5) after a spin, from the card.
- **Width tests restore the text scale in after_each**, so a failed run can't leave the
  player's settings at 1.6. Netrun panels wrap like HQ panels (`UiWrap.fit`).

### 2026-09-24 — Horizontal pass 12 fixes (GAP_ANALYSIS H12)
- **One profile for every campaign slot** (GDD 3.4, TECH_SPEC 8): slots 1-3 and the default
  slot share `profile.json`; deleting a slot's campaign keeps it. Test slots (`gut_` prefix)
  keep a private profile. A per-slot profile from before H12 is read when the shared one
  is missing.
- **The final Rack's rewards are claimable**: its card (and any Firmware) offer now waits
  in the REWARD phase and the run completes once it is resolved. **The final Rack offers
  no Daemon**; the layer-4 Rack is the Rack Daemon source. With a Daemon at both Racks the
  bot carried 12-13 Daemons into the boss and won ICE 5 in 8.8 runs (GDD 11.8: about 24).
  Raising elite and boss HP x1.3 and output x1.25 barely changed that (9.5 runs). Without
  the final Daemon: ICE 0 7/8 won in 31 runs, ICE 5 5/8 in 32.9 (H11: 4/8 in 30.1), on the
  harder side of the target (the "when in doubt, stronger" rule).
- **A patrol stays a patrol**: `RunState.patrol` is set at launch, so a raid Seizing the
  Site mid-run doesn't turn the completion into a clear. An Exploit already held is never
  extracted again (no second copy, Heat or story beat).
- **Long labels wrap on every HQ and title panel** (`UiWrap.fit`): labels stacked in a
  column wrap, and any row label or button wider than 560 px wraps at 560. Title slot rows
  are flow rows. Tested at text scale 1.0 and 1.6.
- **Tuning moved to content and config**: `DaemonData.amount` (schema change) holds Cold
  Exit 3, Scrubber 1, Kernel Sync 1, Zero Day 3 and Botnet Seed 2. Config gains
  `raid_wave_interval` 5, `raid_heat_scaling_step` 10, `dispatch_drift_mid` 3 and
  `dispatch_drift_late` 6.
- **Any player read head resolving the Miss spoils Cold Exit**, Twin Pointer's second
  one included. The consecutive-Perfect count stays on the first pointer.
- **Racks captured are counted** (`RunState.racks_captured`), no longer estimated from
  banked Schematics.

### 2026-09-24 — Horizontal pass 11 fixes (GAP_ANALYSIS H11)
- **Stationed operatives leave their post to run** (GDD 5.4, "instead of running"):
  launching a stationed operative recalls it (the launch picker says "leaves <site>"), and
  a death frees the post.
- **An empty roster can always recruit**: with no living operative a rookie costs
  `emergency_rookie_cost` (0), so the campaign can't stall with no operative and fewer
  than 15 Schematics.
- **Heat labels show the applied Heat**: map nodes, Scrub Heat and Heat-objective Sites
  use `HeatRules.scaled_delta` (ICE gain and sink modifiers included). A Daemon override
  of Rack Heat still applies only on capture.
- **ICE 13 raises home repairs** as well as node repairs (REPAIR_COST_PCT).
- **HQ boosts apply to the final breach and Reclaim runs** (Cycles, run-only cards, max
  RAM), and are spent there.
- **A Firewall Relay shares every station bonus** (GDD 3.2): hold, regen and turrets from
  an adjacent stationed operative, the best of each, as well as the Breaker damage bonus.
  This supersedes the M3 Breaker-only ruling.
- **Config**: `ice_base_cap` 3, `ice_unlock_step` 3, top ICE from the ladder
  (`max_ice_level()`), Modem stock `shop_card_stock` 3, `shop_firmware_stock` 2,
  `shop_daemon_stock` 1; Steady Hand's +2 RAM is the card effect's amount.
- **Large text scales wrap**: the combat controls row is a flow row, Grid Site labels
  wrap; widths are tested at `TEXT_SCALE_MAX`.

### 2026-09-24 — Horizontal pass 10 fix (GAP_ANALYSIS H10)
- **Netrun screens fit 1280**: the mid-run raid row wraps (HFlowContainer) and the netrun
  panel host scrolls vertically (horizontal scrolling disabled, follows focus), matching the
  H9 HQ rule.
- **Entering a fight focuses the hand**: the netrun scene calls `CombatScene.focus_hand()`
  (first playable card, else SEND IT) instead of linking or focusing the combat panel generically.

### 2026-09-24 — Horizontal pass 9 fix (GAP_ANALYSIS H9)
- **HQ panels fit the 1280 screen**: button rows (start panel, actions, boosts, unlocks,
  roster, Site rows, raid rows, codex tabs) are HFlowContainers that wrap; the HQ scroll
  area never scrolls sideways; long profile/unlock/record lines word-wrap. A test opens the
  start panel, HQ, codex and Grid with everything unlocked and all eight classes recruited
  and checks every panel is at most 1280 px wide.

### 2026-09-24 — Horizontal pass 7 fixes (GAP_ANALYSIS H7)
- **Settings sections relink**: `show_section` relinks the panel after swapping controls,
  `link_layout` clears old neighbour paths first, and sliders count as linkable, so every
  Options section (title and pause) is D-pad complete.
- **Reference notes are readable by pad**: codex, stats, run history and lines-heard notes
  start at the top, stop auto-following, and take focus (`ZineNote.make_reference`). H8: a
  focused note handles ui_up/ui_down itself (a RichTextLabel only scrolls on keyboard
  arrows), a quarter page per press, and passes focus on at the top or bottom edge.
- **Netrun combat** links its own hand; the netrun panel no longer links it before the
  fight pickers are hidden.

### 2026-09-24 — Horizontal pass 6 fixes (GAP_ANALYSIS H6)
- **Every panel is D-pad complete**: `UiFocus.link_layout` groups a panel's focusable
  controls into rows (a horizontal container is a row, a lone control is its own row),
  chains left/right within rows and up/down to the same column of the next row; SpinBox
  text fields are skipped (their -/+ buttons are used). HQ, title and netrun panels link on
  open, so reward and Modem stickers, the corporation picker and every Grid row are
  reachable; the Grid list scrolls to follow focus. Left from SEND IT returns to the hand.
- **Reward stickers** no longer show number-key hints that do nothing.
- **Assist label** reads its numbers from the config.
- `tests/unit/test_pad_reachability.gd` walks focus neighbours from the starting focus and
  asserts every usable control is reached (start panel, Grid, rewards, Modem, combat).

### 2026-09-24 — Horizontal pass 5 fixes (GAP_ANALYSIS H5)
- **Card previews follow navigation only**: a card shows its preview when the player moves
  focus onto it (D-pad, arrows, Shift+Tab); nudges, card keys and the automatic refocus
  after a refresh keep the End Turn preview the tutorial points at.
- **D-pad walks the hand**: explicit left/right neighbours between cards (tilted stickers
  confused Godot's geometric search), the last card leads to SEND IT.
- **Confirm dialogs give focus back** to whatever opened them.
- **Esc leaves the share-code field** instead of being swallowed.
- Tests drive real key events through the viewport (E, Right, Esc).

### 2026-09-24 — Horizontal pass 4 fixes (GAP_ANALYSIS H4)
- **Focus survives card plays**: a control queued for deletion no longer counts as focused,
  so the rebuilt hand takes focus; with no playable card, focus falls back to the controls
  row (SEND IT). Card previews follow focus only after keyboard or pad input (auto-focus at
  fight start keeps the End Turn preview).
- **Tab is Cycle target again**: Tab is removed from `ui_focus_next` (like Space from
  `ui_accept`); Shift+Tab still moves focus back.
- **Modals take focus**: the pause menu focuses its first button and gives focus back on
  close, the settings panel focuses itself, confirm dialogs focus "No".
- **Start panel for pads**: ICE -/+ and seed +1 buttons (SpinBoxes ignore the D-pad).

### 2026-09-24 — Horizontal pass 3 fixes (GAP_ANALYSIS H3)
- **Lost-raid Heat** names the next raid for the corporation: `CampaignRules.fight_raid`
  renames its own events (HQ, netrun interlude and simulator paths all go through it).
- **REBEL_CELL elite pool** = this campaign's Mirrors only (`corporation.elites`), sorted;
  netrun pools are rebuilt once the corporation is set. Before, Mirrors from earlier builds
  in the session leaked in and a resume in a fresh session could play differently.
- **Pad-only play**: every panel focuses its first usable button (`UiFocus`), the combat
  hand refocuses when focus is lost (H4: also after a card play frees the old hand), pad
  inspect inspects the focused control. Pad
  layout reworked: LB/RB nudge, Y target, X end turn, Back rewind, L3 inspect, R3 respin,
  Start options; the D-pad, A and B drive focus (`UI_PAD_BINDS`), so the combat pickers and
  cards are reached as on-screen buttons. Space no longer presses the focused button (it is
  End Turn). Confirm on real hardware.
- **More Mirror numbers in the config**: `mirror_resistance`, `mirror_deploy_base`,
  `mirror_threat_min_integrity`, `mirror_threat_min_damage`, `mirror_decoy_speed`; the
  designer's tuning knob is `config.mirror_output_factor`.

### 2026-09-24 — Horizontal pass 2 fixes (GAP_ANALYSIS H2)
- **Raid names per corporation**: `CampaignRules.name_pending_raids` rewrites HeatRules'
  "Raid incoming" text with the corporation's own raid (HQ report, netrun Heat, run end).
- **Raid warning keys**: mid-run interludes carry the queued (shared) raid id, so the
  corporation's specific warning plays on both screens.
- **Event speakers** carry their corporation (label and colour); "lines heard" too.
- **Held at home = no damage while held**; the damage lands on the step the hold ends.
- **Boss launch message**: with enough Exploits it now says the boss needs a cleared or
  claimed Site next to it (it used to repeat "needs 3 Exploits (3 held)").
- **Share codes** encode the campaign's starting class (`CampaignState.start_class_id`), so
  the code stays valid after that operative dies.
- **ICE records** skip a locked REBEL_CELL (no spoiler) and hint "something opens at ICE
  10 everywhere"; the stats screen shows records per corporation and assisted wins; run
  history names corporations.
- **No magic numbers**: Heat bands come from the config's MAJOR thresholds
  (`major_heat_levels()`); Mirror factors and the "final final" ICE moved to the config
  (`mirror_output_factor`, `mirror_threat_integrity`, `mirror_threat_damage_bonus`,
  `final_final_ice`; code keeps the same defaults for tools).
- **Colours**: Halcyon #8C7BFF (was too close to Solace), Orbital #DDE3FF (was too close to
  resist_gold); every corporation colour is in STYLE_GUIDE. Dead `CLASS_COLORS` removed.
- **Shared text**: the Medbay and DISPATCH ping events and two Breaker barks no longer name
  Solace.
- **Unlock matching by id** (bug found by the full suite): after a REBEL_CELL campaign the
  built corporation replaces the template in the lookup, and `unlock_for` compared objects,
  so REBEL_CELL looked open to everyone for the rest of the session. Unlocks now also match
  by content id.

### 2026-09-24 — Horizontal pass 1 fixes (GAP_ANALYSIS H1)
- **Corporation-aware everywhere**: the win text and end screen name the corporation's own
  boss; corporate subtitle lines carry the corporation's short name ("MERIDIAN") and colour
  (`Dialogue.speaker_name`); the boss-phase flash and the Heat poster use the corporation
  colour; the HQ pirate radio has DJ sets per corporation (generic lines kept apart).
- **Music per corporation**: `AudioDirector.CORP_CONTEXTS` maps generic contexts to a
  corporation's (Solace/Meridian/Halcyon/Orbital raids get their own loop; REBEL_CELL plays
  its slowed lo-fi at HQ and on the Grid). New code-generated loops for the three raids.
- **ICE records**: HQ and end screen list the best ICE for every corporation and the
  road to REBEL_CELL (n/4 cleared at ICE 10). The Target list is ordered open first, then
  by unlock price, REBEL_CELL last, and the ICE box starts from the first entry's cap.
- **Codex**: enemies appear once met (`RunManager.record_seen`, profile stat
  `use_seen:<id>`); REBEL_CELL shows as "???" until reached; new Classes, Corporations and
  Home servers sections; AFFLICT and PARASITE text generic; lexicon adds Tariff, Citation,
  Solar Flare, Inertia, Mirror.
- **Rescue**: every corporation has a rescue event; a rescued operative is one of the
  classes already on the roster (seeded draw, never bypasses class unlocks).
- **Built-in ICE Locks hold threats** (bug): raid holds only looked at deployed assets;
  built-in node and home assets now hold too, and a threat held at the home server does
  not damage it while held (the home defences keep firing). This makes the Ghost home work.
- **Raid warnings** use the queued (shared) raid id on both screens, so corporation lines
  play. **DISPATCH speaks its boss line** when a boss run starts.
- **Assisted wins** count in `stats.assisted_wins`, not `campaigns_won` (no "Breach").
- **Share codes for REBEL_CELL** are marked local on the HQ radio (it is built from your
  own profile; another player's code builds from theirs).
- **Breaker's second exclusive**: Shatter (breach the Hub 1 turn, strip 1 resistance),
  shared with the Wrecker; every class now has two exclusives.
- **Events per corporation**: target lowered to about 30 rollable (own + shared): the new
  corporations have 21 of their own plus 7 shared; Solace keeps 40. Writers can add more.
- Tests for Overclocker and Mk2 cores, home servers in raids, Mirror threat routing,
  REBEL_CELL resume mid-netrun, and every corporation's events in its own campaign.

### 2026-09-24 — M12 Polish and reach (GAP_ANALYSIS P1 10, P2 11-13)
- **Home-server variants 2 -> 5** (Profile unlocks, `tools/content_gen/gen_home.py`): Relay
  Nest (50 integrity spread over two nodes, 5 asset slots; 50 Schematics), Ghost (50
  integrity, 2 slots, built-in ICE Lock holding a threat 2 steps; 60), Fortress (100
  integrity, 2 slots, no gun; 80).
- **Skins deferred to art integration (M13)**: with placeholder art a skin would only be a
  palette swap; UnlockKind.SKIN stays for when portraits and card art arrive.
- **Controller support** (P2 11): `Settings.CONTROLLER_BINDS` adds a pad button to every
  combat action at startup (shoulders nudge, Y target, X end turn, Back rewind, B nudge
  wheel, D-pad toggles, stick clicks inspect/respin, Start options). Menus use Godot's pad
  ui_* bindings. Rebinding a key keeps the pad button. No pad rebinding UI yet.
- **Share codes and the daily run** (P2 12): `CampaignCode` encodes seed, corporation, ICE,
  home and class as RC1-<corp>-<ice>-<seed>-<home>-<class>; the core is deterministic, so a
  code replays the same campaign. HQ start panel: Daily run (seed YYYYMMDD from the system
  date, read in the UI only) and Start from code; the HQ radio shows the running code.
  Locked parts of a code fall back like the start panel.
- **Assist mode** (P2 13): an Accessibility option; campaigns started with it get
  `config.assist_free_nudges` (1) extra free nudges a turn and `config.assist_hp_multiplier`
  (1.25) operative HP, saved on the campaign. Assisted wins count as wins but set no ICE
  records and earn no campaign achievements; the HQ shows ASSIST. "Preview-only" from the
  GDD list is already how the game plays (every action previews before it commits).

### 2026-09-24 — M11 REBEL_CELL (GAP_ANALYSIS P1 9, GDD 8.5)
- **Built from the profile.** `ProfileState` now counts usage (stats `use_class:`,
  `use_daemon:`, `use_node:`, `use_asset:`) at the end of every run: the operative's class
  and Daemons, and the node types and assets standing on the Grid.
  `RebelCellBuilder.snapshot` takes the top 2 classes, 3 Daemons, 3 node types and 3
  assets (ties by id; starter fallbacks when empty). `RebelCellBuilder.build` deep-copies
  the template (never touches the loaded Resource) and:
  - replaces the elites with **Mirrors** of your classes: your wheel, each slice swapped
    for the closest plain slice of its type at 1.5x output (Deploy becomes Attack), one
    pointer, resistance 1, and a hub running the combat effects of your data Daemons
    (custom-handler Daemons cannot be copied);
  - prefixes Site names with your node types;
  - rebuilds every raid with **Mirror** threats made from your assets (1.5x integrity,
    +2 damage; turrets hunt the weakest node, ICE Locks freeze links, decoys run fast at
    the highest-value node).
- **Rebuilt on resume**: the campaign saves its snapshot (`CampaignState.generated`), so the
  enemy does not change when the profile moves on. The built corporation is registered in
  the lookup (`RunManager.build_generated`).
- **Unlock**: free, and opens by itself once every other corporation is cleared at ICE 10
  (`requires_all_corporations_at_ice = config.rebel_cell_unlock_ice`); free unlocks are
  not shown in the HQ buy row. Own ICE ladder (per-corporation caps already existed).
- **Static template** (`tools/content_gen/gen_rebel_cell.py`): normal enemies using every
  corporation's signature affliction (Dose, Tariff, Citation, Solar Flare); mini-boss The
  Handler; boss **DISPATCH** (460 HP; Root Access hub repairs 4 and shields 4 unless
  breached). Six reveal paths (The Handler, Every Collapse, The Buyer, Your Own Hands, The
  Founders, Final Final): DISPATCH is the rogue AI and the buyer behind every collapse.
  DISPATCH briefs the Cell as the enemy. Template elites have no corporation id so pools
  never draw them. Colour #FF2A6D.
- **"Final final"** achievement: REBEL_CELL and every other corporation at ICE 20
  (`Achievements.check` now takes the corporation list).
- **Balance** (8 seeds; the simulator builds REBEL_CELL from a profile that played the
  simulated class with the starter assets): first pass the Mirrors used two pointers and
  2x slices and killed rookies (Breaker 2/8); now one pointer and the closest 1.5x slice.
  Final: Breaker ICE 0 5/8 (27.5 runs), ICE 5 4/8, ICE 10 1/8; Rigger ICE 0 6/8; Botnet
  ICE 0 8/8. The hardest corporation by design.

### 2026-09-24 — M10 Orbital Commons (GAP_ANALYSIS P1 8)
- **Orbital Commons** (GDD 8.4 names): privatised orbital infrastructure (satellite
  internet, positioning, weather). Mechanical identity: **Solar Flares** (new AFFLICT slice:
  OVERCLOCK a random non-Miss player slice: 1.5x on its next trigger, then CORRUPTED, a
  double-edged status), fast orbits and heavy debris. Enemies Uplink Relay, Orbital Debris,
  Tracking Station, Weather Satellite (orbit 4), Ground Control, Launch Pad; elites Station
  Commander and Geostationary Guard; mini-boss Mission Director; boss **The Commons Array**
  (420 HP; Station Keeping hub repairs 3 and shields 3 a turn unless breached; 66% two
  pointers orbiting 4; 33% three pointers, Crit wheel, drones). Threats Lander, Debris
  Field, Signal Jammer; eight raids. Exploits: Launch Codes, Ground Station Override, Open
  Spectrum. Six story paths: The Enclosure, Blackout Weather, Positioning Tax, Final
  Transmission (DISPATCH clues; foreshadows REBEL_CELL, the satellite that names itself),
  Dead Satellites, The Commons. Twenty events, briefings, voice, colour gold #FFE14F.
  Unlock 160 Schematics.
- **Balance** (8 seeds): first pass easy (Breaker ICE 5 7/8 in 14.5 runs); as the fourth
  corporation it was strengthened: elites +10% HP, boss 380 -> 420. Final: Breaker ICE 0
  7/8 (14.3 runs), ICE 5 8/8 (18.4), Ghost ICE 5 8/8 (14.1), Botnet ICE 0 8/8 (13.3),
  Rigger ICE 0 8/8 (17.6).

### 2026-09-24 — M9 Halcyon Civic (GAP_ANALYSIS P1 8)
- **Halcyon Civic** (GDD 8.4 names): smart-city services contractor. Mechanical identity:
  **Citations** (new AFFLICT slice: PARASITE on a random non-Miss player slice, half output
  until cleansed), healing and shielding enemies, evasive surveillance masts. Enemies
  Parking Warden, Utility Meter, Transit Controller, Surveillance Mast, Patrol Unit, Permit
  Office; elites Riot Control and Zoning Board; mini-boss City Manager; boss **The Civic
  Core** (360 HP; Emergency Powers hub heals 4 and blocks 4 a turn unless breached; 66%
  three pointers; 33% orbit, Crit wheel, civic drones). Threats Inspector, Bailiff, Tow
  Truck; eight raids replacing the shared threshold raids. Exploits: Council Minutes,
  Emergency Override, Open Data Leak. Six story paths: Water Rights, Predictive Policing,
  Transit Blackout, The Census (DISPATCH clues), Orbital Uplink (foreshadows Orbital
  Commons), Smart Meters. Twenty events, briefings for every Site, corporate voice, colour
  mint #4FFFB0. Unlock 140 Schematics.
- **Shared generator**: `tools/content_gen/gen_corp_lib.py` builds a whole corporation from
  a spec dict; the M6-M9 generators now live in `tools/content_gen/` (README there).
- **Balance** (8 seeds): first pass the Civic Core killed Breakers (25 boss deaths at ICE 5,
  4/8 won); HP 400 -> 360 and heal 5 -> 4. Final: Breaker ICE 0 7/8 (19.0 runs), ICE 5
  6/8 (15.8), Rigger 7/8 (17.9), Ghost ICE 5 8/8 (10.3), Botnet 8/8 (11.9 before the boss
  change).

### 2026-09-24 — M8 Corporation selection and Meridian Freight Systems (GAP_ANALYSIS P0 3, P1 8)
- **Corporation selection** (P0 3): corporations with a `ProfileUnlockData` (kind
  CORPORATION) need it; the rest (Solace) are always open. `CampaignRules.available_
  corporations` / `corporation_available`; `RunManager.new_campaign` falls back to Solace
  for a locked one. The HQ start panel has a Target picker; the ICE spin box follows the
  chosen corporation's own ladder (GDD 3.4). The start button reads "New campaign".
- **Meridian unlock**: 120 Schematics (implementer's call; classes are 80). Buying it at HQ
  works like the other Profile unlocks.
- **Per-corporation raids** (schema): `RaidData.corporation_id` and `replaces`. The
  Heat-threshold raids live in the shared config; a corporation's raid with `replaces =
  raid_heat_25` stands in for it in that corporation's campaigns. Pending raids now carry
  the campaign's corporation id; old saves without it keep the shared raid. Claim, node,
  story and retaliation raids already came from `CorporationData.raids`.
- **Meridian Freight Systems** (GDD 8.4 names): logistics megacorp. 32-Site Grid mirroring
  Solace's shape (ten T1, eight T2 with the three Exploits, eight T3, four Heat objectives,
  The Manifest at T4). Site ids are global content ids, so Meridian's are prefixed (m_home,
  m1_a..). Enemy family: Customs Scanner, Cargo Hauler (resistance 2), Conveyor Warden
  (orbit 3), Route Optimizer (two pointers), Drone Dispatcher (courier drones), Tariff
  Collector (RAM drain); elites Port Authority and Last-Mile Enforcer; mini-boss Logistics
  Director; boss The Manifest (400 HP, Priority Routing hub: +4 shield a turn unless
  breached; 66% two pointers; 33% orbit, a Crit wheel and courier drones). New slices
  Tariff (AFFLICT: drains 3 RAM) and Attack 8 +1 resistance (Inertia). Threats Courier,
  Hauler, Customs Agent; eight raids. Exploits: Shipping Manifests, Customs Override Keys,
  Rogue Routing Table (same effects as Solace's three). Six story paths: Lost Cargo, The
  Night Shift, Customs Hold, Ghost Freight (DISPATCH clues), Civic Contract (foreshadows
  Halcyon Civic), Last Mile. Twenty Meridian events; DISPATCH briefings for every Site and
  a Meridian corporate voice for raids. Corporation colour amber #FF8C1A.
- **Tuning** (8 seeds, `tools/simulate_campaign.gd -- 8 <ice> class=<id> corp=meridian`):
  first pass Meridian was easier than Solace (Rigger won in 9.6 runs) and the boss stalled
  (95 fights at the turn cap: shield regen outpaced damage at low HP). Normal enemies +20%
  HP and +2 attack, elites +15% HP and +2 attack, Tariff drains 3, boss 400 HP but 4
  shield a turn (was 6). Final:

  | Class | ICE | Won | Mean runs | Stalls |
  |---|---|---|---|---|
  | Breaker | 0 | 7/8 | 18.4 | 40 |
  | Breaker | 5 | 7/8 | 16.8 | 49 |
  | Ghost | 0 | 8/8 | 10.6 | 12 |
  | Botnet | 0 | 8/8 | 13.3 | 3 |
  | Rigger | 0 | 7/8 | 22.6 | 68 |

- Dev shortcuts: `--demo-start` (the start panel) and `--demo-corp=<id>` with the HQ demo
  flags (campaign-only, bypasses Profile unlocks).

### 2026-09-24 — M7 Pools and Solace depth (GAP_ANALYSIS P1 6–7)
- **Only existing effect types.** Every new card, Firmware, Daemon, asset and event is data
  on the M1–M6 effect set; no new mechanics. Numbers are placeholders.
- **Shared cards 22 → 60** (38 new): rotation (Whirl, Backspin, Flick, Spin Cycle, Gear
  Mesh, Inner Drift, Ratchet, Tailspin), precision (Tap Tap, Feather Touch, Inner Snap,
  Lock On, Deep Calibrate, Nudge Driver), enemy control (Deep Strip, Short Circuit, Double
  Jam, Cold Snap, Corrupt Packet, Malware Drop, Leech Worm, Flip Switch, Reroll), defence
  (Firewall, Bulwark, Shield Wall, Duck, Patch Up, Sanitize, Armor Plate, Stim Patch) and
  utility (Hot Patch, Power Tap, Data Surge, Scrap Code, Static Shock, Overload, Arc
  Flash). Direct-damage cards stay small (the wheel is the damage engine, GDD pillar).
- **Firmware 6 → 18**: Overvolt, Bulkhead, Siphon, Static Coat, Barbed Wire, Tracer,
  Coolant Loop, Skimmer, Counterstrike, Nanite Mesh, Power Cell, Recycler. Heat and Cycle
  Firmware have per-combat limits.
- **Daemons 10 → 24**: Warm Boot, Shield Cache, Idle Armor, Adrenal Loop, Fail Forward,
  Feedback Loop, Tuning Fork, Static Field, Cascade, Salvager, Field Medic, Bounty Code,
  Rack Skimmer, Log Wiper.
- **Run-level Daemon hooks apply their data effects.** `NetrunSession._apply_hook_effects`
  applies Heat, Cycles, banked Schematics and healing for ON_COMBAT_END (now fired after a
  won fight), ON_SERVER_RACK_CAPTURE and ON_NETRUN_COMPLETE hooks. Before, only custom
  handlers and netrun-complete Heat worked.
- **Defense assets 3 → 8**: Railgun, Flak Array, Sentry, Tar Pit, Honeypot, using the
  existing targeting modes (highest damage, lowest integrity) and range 0 (own node).
- **Shop slices 7 → 12**: Atk 10, Crit 16, Heal 6, and new Shield 8 and Evade 2 (GDD 11.2's
  examples). Heal 6 gives the Nanite Mesh Firmware a slice to live on.
- **Events 19 → 40**: 21 written events. Nineteen are Solace-only; two (Rival Crew, Ghost
  Market) are corporation-neutral so later corporations share them. Every choice resolves
  (test), rewards include the new cards, Firmware, Daemons and assets.
- **Balance** after the pools (8 seeds, `tools/simulate_campaign.gd`):

  | Class | ICE | Won | Mean runs | Deaths |
  |---|---|---|---|---|
  | Breaker | 0 | 8/8 | 14.8 | 1.8 |
  | Breaker | 5 | 7/8 | 26.4 | 3.5 |
  | Wrecker | 0 | 8/8 | 14.6 | 1.8 |
  | Ghost | 0 | 8/8 | 22.6 | 1.6 |
  | Phantom | 0 | 8/8 | 23.6 | 1.5 |
  | Rigger | 0 | 8/8 | 20.3 | 1.9 |
  | Overclocker | 0 | 8/8 | 20.3 | 1.9 |
  | Botnet | 0 | 8/8 | 20.6 | 3.0 |
  | Hivemind | 0 | 7/8 | 18.0 | 0.8 |

- **Why the bot changed.** With 3x the pools the bot's "take option 0" policy stopped
  finding what beats Solace, and its campaigns fell to 2-5 wins in 8. A ranking run
  (every Daemon and card against the T4 boss, 12 seeds each) showed what matters:
  anti-corruption cards (Sanitize 9/12, Hot Patch 8, Cleanse and Armor Plate 7; the boss's
  Dose corrupts your wheel), Adrenal Loop 11/12, Kernel Sync 9, Zero Day 7, and the Heat
  sinks (Clean Signal alone removed 116 Heat per M6 campaign). `CampaignSimulator` now
  drafts cards, Firmware and Daemons by those measured values, skips self-damage and
  random cards, and spends surplus Schematics on Heat scrubs (keeping two recruits in
  reserve). It logs deaths and stalls with the enemy, and the boss loadout.
- **Enemies strengthened** ("when in doubt, up elite and boss strength"): the smarter bot
  finished campaigns in 12-16 runs. Elites +25% HP (Claims Adjuster 90 -> 112, Recall Unit
  85 -> 106, Account Manager 120 -> 150), Renewal Engine 300 -> 360 HP, and enemy damage per
  tier 1.2 -> 1.3. ICE 5 now matches GDD 11.8 pacing (26 runs vs 24); ICE 0 is the easier
  entry. GDD A.3 is annotated.
- **Ghost ring back to Pierce / x2 / Echo.** Against the boss Pierce did not help (the stall
  is damage against the heal, not block): Pierce / Echo / blank won 4/12 boss fights,
  Pierce / x2 / Echo 9/12.
- **Hive Core keeps the half retrigger** (like the Swarm Core) with 4 drones (Mk2 5) that
  do not persist; without it the Hivemind stalled against the boss.
- **Feedback Loop fixed**: it hit "the target", which is you when the card targets your own
  wheel; it now hits every enemy.

### 2026-09-24 — M6 Class roster: Ghost, Rigger, Botnet and four alternatives (GAP_ANALYSIS P0 1–2, P1 5)
- **Recruitment by class** (P0 1): `CampaignRules.available_classes` / `class_available`
  read the Profile unlocks; the Breaker is always available. HQ shows one Recruit button
  per available class and a "Crew:" picker on the new-campaign panel;
  `RunManager.new_campaign` falls back to the Breaker for a locked class.
- **Unlock costs**: base classes 80 Schematics (GDD 3.4), alternatives 60 (implementer's
  call: a variation is worth less than a new class). Alternatives do not require their
  base class to be unlocked first.
- **Botnet drones persist** (P0 2): `HubCoreData.drones_persist`; living drones are saved
  on `RunState.drones` after a victory and re-docked (with their HP) at the next fight of
  the run through the "drones" combat override.
- **New hub fields**: `max_ram_bonus` (Rigger) and `free_resistance_nudges` (Ghost: the
  first N nudges on an enemy wheel each turn ignore resistance, event "ghost_nudge").
- **PARASITE** is a new `RC.Status` (value 4): the slice resolves at
  `config.parasite_multiplier` (0.5) until cleansed. The Swarm Core hook plants it on the
  target's slice under the matching pointer after a Perfect on a DEPLOY slice.
- **Station bonuses** (GDD 5.2) from the class's `station_bonus` effect type:
  FREEZE = hold (Ghost: a threat entering the node is held once, 1 step), HEAL = regen
  (Rigger: +5 integrity after each wave and at raid end), DEPLOY_DRONE = free turrets
  (Botnet: `config.station_deploy_asset`, the Turret, for this raid). Rank scales each by
  `station_bonus_multiplier`, counts rounded.
- **Freeze cooldown** (found by the class simulation): a wheel that skipped its respin
  because it was frozen cannot be frozen again until it has respun
  (`WheelState.respin_skipped`, event "freeze_blocked"). Without it an Anchor segment
  landing a Perfect on a non-damage slice locked the wheel forever: a stalemate.
- **Every class needs burst** (found by the simulation): the Renewal Engine heals 10 a turn
  and only the Breaker could outpace it (its Perfect resolves the slice twice). GDD 5.2 is
  extended, not replaced: the Ghost Perfect also resolves the slice twice; the Rigger and
  Botnet Perfects also resolve it again at half (Botnet on any slice). Hook effects fire
  once per resolution (the existing Breaker Mk2 rule), so a retriggered Botnet Deploy
  plants its Parasite twice and a Rigger Perfect refunds twice.
- **Wheels are interleaved** so neighbouring slices differ and a one-tick miss does not
  land on the same slice type. Values are placeholders tuned by simulation:
  Ghost Atk 14, Def 6, Atk 14, Evade, Def 6, Miss; Rigger Atk 16, Def 6, Atk 14,
  Shield 5, Def 6, Miss; Botnet Atk 16, Deploy, Atk 16, Deploy, Def 8, Miss.
- **Rank 1 rings**: Ghost Pierce / Echo / blank; Rigger Accelerator / x2 / Echo; Botnet
  Echo / Corrupt / x2. Rank 3 swap options are the remaining segments. The Anchor moved out
  of the Ghost's default ring into its options.
- **Exclusive cards** (two each): Ghost Step, Blind Spot; Torque Wrench, Hot Swap; Spawn
  Drone, Parasite Pulse. **Mk2 cores** at Rank 2 for every class. Barks for every class.
- **Alternatives** (GDD 3.4, "same deck + different core"): `ClassData.alternative_of`;
  `pool_class_id()` makes an alternative draw its base class's exclusive cards and speak
  its barks.
  - *Wrecker* (Breaker): no spin bonus; Perfect resolves again at 1.5x.
  - *Phantom* (Ghost): a free nudge at each turn start; Perfect evades and resolves twice.
  - *Overclocker* (Rigger): +2 max RAM; Perfect gains 2 RAM and resolves again at half.
  - *Hivemind* (Botnet): up to 5 drones that do not persist; Perfect docks a drone and
    resolves again at half.
- **Balance** (`tools/simulate_campaign.gd -- 8 0 class=<id>`, ICE 0, greedy bot):

  | Class | Won | Mean runs | Deaths |
  |---|---|---|---|
  | Breaker | 8/8 | 25.9 | 4.9 |
  | Wrecker | 8/8 | 25.8 | 5.3 |
  | Ghost | 7/8 | 25.5 | 4.4 |
  | Phantom | 7/8 | 23.5 | 2.9 |
  | Rigger | 8/8 | 15.4 | 1.8 |
  | Overclocker | same as Rigger (see below) | | |
  | Botnet | 8/8 | 19.1 | 3.0 |
  | Hivemind | 8/8 | 24.0 | 3.8 |

  The bot never spends free nudges or RAM above what its hand costs, so the Rigger and
  the Overclocker play identically in simulation (every seed matched). Their difference
  (free nudges vs banked RAM) only shows with a human. Single slice values swing the
  results a lot (Rigger Atk 14/14 took 36 runs, 16/16 takes 15), so 8 seeds is a coarse
  tool.

- Dev shortcuts: `--demo-classes` (HQ roster with every class) and `--demo-class=<id>`
  (netrun) bypass Profile unlocks in the demo save slot only.
- The simulator logs which enemy a stuck fight was against.

### 2026-09-24 — Vertical-slice fixes, batch 5: gap analysis pass 2 and the balance simulation
- **Rank gating uses the operative's own class** (V1): `RunManager.launch_error` passes the
  operative's ClassData; `CampaignRules.launch_error` refuses a mismatched class instead of
  silently gating with the wrong Rank table.
- **Grid map clicks select a Site** (V2): the Site's row (status and every action) is
  listed first under "SELECTED >" and the Site gets a cell_acid ring on the map.
- **Netrun panels are zined** (V3): rewards and Modem stock are zine stickers (cards show
  RAM cost, stock shows the Cycle price in the cost circle, Firmware/Daemon offers show
  none), street/corporate events sit on a ZinePanel, DISPATCH events on a clean dark strip
  (never zined), the run end is a stamp plus a torn note.
- **Balance simulation** (V4): `CombatBot` plays greedily from the End Turn preview (the
  information a player has) and never plays random-outcome cards; `CampaignSimulator`
  plays whole campaigns with fixed policies; `tools/simulate_campaign.gd -- <seeds> <ice>
  [verbose]` prints pacing. A campaign takes 3-25 s. The first runs found four real
  problems, fixed as below; the numbers after the fixes (8 seeds each):

  | | GDD 11.8 | ICE 0 | ICE 5 |
  |---|---|---|---|
  | bot wins | — | 8/8 | 6/8 |
  | runs | ≈ 24 (fast 8) | 25.9 (fastest 9) | 21.0 |
  | raids | ≈ 7 (fast 3) | 5.3 | 6.1 |
  | Heat peak | 85-90 at ICE 5 | 78 | 84 |
  | hours | 6 h 35 m | 6.9 | 5.8 |

- **Home server patch** (found by the sim: home damage was permanent while Schematics
  piled up): HQ "Patch home" restores integrity at `home_repair_cost_per_point` (1)
  Schematics per point; partial patches buy what the Schematics allow. GDD 3.3 annotated.
- **Retaliation raids narrowed** (found by the sim: 8 raids in 8 runs): only Exploit
  extraction at Heat ≥ `retaliation_min_heat` (50) provokes one; Heat objectives never do
  (they are sinks). Supersedes the batch 2a rule. GDD 4.4 annotated.
- **Patrol runs** (found by the sim: a soft-lock when every Site is used up and no
  operative has Rank 3): any cleared or claimed Site except home and the boss can be run
  again as a full netrun with normal loot, Heat and Rank but no objective; completion leaves
  the Grid unchanged (node passives still apply). Launch kind "patrol"; the Grid lists them.
- **Enemy damage scales separately from HP** (found by the sim: every Rank 3 Breaker died to
  the T4 Renewal Engine, whose Crit at 1.6^3 hit for 98 against 60 HP): HP keeps
  `enemy_scale_per_tier` 1.6; slice outputs use `enemy_damage_scale_per_tier`, tuned to
  **1.2** by simulation (1.6: 2/8 wins and 41 runs; 1.35: 3/8; 1.2: 8/8 at 26 runs). The
  designer's ruling stands: both scales hit normal enemies, mini-bosses and the boss.
  `CombatantState.hp_scale` lets satellites inherit the host's HP scale. GDD 11.6 annotated.
- **The bot skips Burner Firmware** (Heat per trigger); a player weighs that cost too.
- **M5 "Vertical completion"** is recorded in MILESTONES.md with its acceptance list.
- **Schema changes**: `CampaignConfigData.home_repair_cost_per_point / retaliation_min_heat /
  enemy_damage_scale_per_tier`, `CombatantState.hp_scale`. Smoke test batch 5 extended.

### 2026-09-24 — Vertical-slice fixes, batch 4: menus, platform and onboarding (GAP_ANALYSIS §2.5)
- **Title scene** (`scenes/menu/title_scene.tscn`) is the main scene: Continue (the most
  recently saved numbered slot), Campaigns (three slots with corporation / Heat / ICE /
  runs / state, New / Load / Delete with a confirm), Tutorial, Codex, Stats &
  achievements (profile numbers, achievement list, the last 20 runs), Options, Quit
  (confirm). Saves carry `saved_at`; `SaveService.list_campaign_slots()` scans the save
  directory; test and demo slots are never offered.
- **Pause menu** (`PauseMenu`) replaces the bare accessibility popup on Esc in every
  scene: Resume, Options (the full `SettingsPanel` inline), Codex, Save & quit to title,
  Quit to desktop (confirm). The scene variable keeps its `_settings_panel` name so the
  keyboard test still checks it toggles.
- **Options** in five sections: Accessibility (unchanged), Display (windowed /
  fullscreen / borderless, resolution presets, v-sync, fps counter), Audio (master, music,
  SFX), Controls (rebind the twelve combat/menu actions by pressing a key; card keys stay
  1-9; Escape cancels; Reset restores the project defaults; bindings persist in
  `Settings.keybinds` and are applied to the InputMap at start-up), Language (locales
  with a loaded translation). Display changes are no-ops headless.
- **Autosave indicator**: Fx shows a marker "SAVED" that fades whenever SignalBus reports
  a completed save; **fps counter** in cell_acid top-right when enabled.
- **Tutorial** (`TutorialOverlay`): seven zine steps over the first fight (wheel, precision,
  resistance, cards & preview, rewind, End Turn, Heat & banking); steps with a trigger
  advance on the matching engine event (nudge, card, rewind, turn_start), the rest on
  Next; Skip or Finish sets `Settings.tutorial_done`. Starts automatically on a new
  profile's first fight (never headless) and from the title's Tutorial button
  (`RunManager.pending_tutorial` → the combat scene).
- **Achievements** (`Achievements.DEFS`, evaluated in `sync_profile_with_campaign`): First
  Blood, Banked (10 Racks), Breach, Clean Hands, Average Is a Lie (ICE 5), Cold Storage
  (ICE 10), Purge Survivor, The Wall (20 raids), Perfectionist (500 Perfects), Final Final
  (defined, unreachable until REBEL_CELL). The narrator announces new ones through
  Dialogue. `ProfileState.stats` (perfects, racks, cycles, runs per tier) and
  `run_history` (20 entries) feed the stats screen.
- **CI and export**: `.github/workflows/ci.yml` runs import, GUT, the schema smoke test,
  content validation and checks that `assets/text/strings.csv` is current, then exports
  Windows and Linux builds as artifacts (Godot 4.7.2 via setup-godot). `export_presets.cfg`
  (Windows, Linux, macOS; no credentials) is committed, so it left `.gitignore`.
  `application/config/version` is 0.9.0 and the title shows it.
- **Controller support** stays out of the vertical slice (GDD 9.5: PC mouse + keyboard);
  it remains a P2 horizontal item.
- **Performance**: TECH_SPEC's 1080p target still needs a human run; the fps counter is
  the tool for it. The core stays under 1 ms per turn in the automated check.

### 2026-09-24 — Vertical-slice fixes, batch 3: narrative, dialogue, subtitles, codex, text export (GAP_ANALYSIS §2.4)
- **Line database** (`LineSetData` of `VoiceLineData`): lines are keyed by moment
  (`site:<id>`, `raid:<id>`, `threshold:<heat>`, `boss/win/loss`, `run_start/complete/died`,
  `rack`, `bark:<trigger>`, `dj`) and carry a `drift_stage` and `dispatch_clue`. The
  **Dialogue** autoload picks a line deterministically (hash of key + salt, ties by text)
  and never uses global RNG; **DISPATCH drift** (GDD 8.2) is a profile stage: 0 for the
  first two campaigns started, 1 from the third, 2 from the sixth; a higher stage replaces
  the human line and those lines are the clues (impossible timestamps, evenly spaced
  breaths, "the projection allowed for it").
- **Subtitle bar** (GDD 9.6): bottom-centre CanvasLayer; speaker name; DISPATCH and Corpo
  on a dark strip in amber/corporate colour (clean system text, STYLE_GUIDE 3), everyone
  else on paper. Honours `Settings.subtitles`; `line_spoken` fires regardless for voice-over
  later; `history` feeds the codex's "lines heard". Queue of six, timed by text length.
- **Content**: 55 DISPATCH lines (a briefing for all 32 Solace Sites, boss/win/loss with
  drift variants, threshold lines, run lines), 8 Solace Collections raid warnings, 14
  Breaker barks (perfect, miss, hurt, victory, defeat, deploy, jack_in, boss; at most one
  per trigger per turn, never in headless/reduce-effects), 8 pirate-radio DJ lines at HQ
  (two carry stage-1/2 clues). Barks are per class (`LineSetData.class_id`), so each new
  class ships its own set.
- **Six written Solace story paths** replace the placeholders: Recall Notice, Clinical
  Trial, Terms of Service, The Cure, Ghost Patient (every beat a DISPATCH clue; beat II
  triggers the STORY raid; foreshadows `dispatch`) and Hostile Takeover (foreshadows
  `meridian`). Each has a premise, 3 beats in Exploit order, 2 bonus beats and a finale.
- **Corporations 2–4 named** (open question from the gap analysis, my call): **Meridian
  Freight Systems** (autonomous logistics; threats are fleet drones; Exploits: manifests,
  routing keys, fleet firmware), **Halcyon Civic** (municipal surveillance contractor;
  threats are wardens; Exploits: camera keys, warrant authority, the civic ledger) and
  **Orbital Commons** (satellite data commons gone private; threats are uplink hunters;
  Exploits: ephemeris, ground-station keys, the commons charter). Hostile Takeover points
  at Meridian. Horizontal work builds them.
- **Codex** (GDD 8.1): an HQ/start-screen panel built from `Codex.entries()` (slices,
  statuses and precision, cards, Firmware, Daemons, ring segments, enemies, nodes, assets,
  threats, lexicon) plus the last six lines heard.
- **Text externalisation** (GDD 10): `TextDb.key_for(res, field)` gives every content string
  a stable key (`CardData.jolt.description`); `tools/export_text.gd` writes
  `assets/text/strings.csv` (`keys,en`, 389 strings) keeping any locale columns already
  there; Godot's CSV importer produces the `.translation` files; `TextDb.t(res, field)`
  returns the loaded translation or the content text, so untranslated builds never show
  keys. `Settings.language` sets the locale. UI strings go through `TextDb.ui(key,
  fallback)` as they are touched. Voice recording stays out of scope for code (the
  `audio_path` field on lines is the hook).
- **Schema changes**: `VoiceLineData`, `LineSetData` (new), `Settings.language`, the
  `Dialogue` autoload (after Fx).

### 2026-09-24 — Vertical-slice fixes, batch 2b: Solace at size, events, map and raid presentation
- **Solace City Grid is 32 Sites** (GDD 4.1: 30-40), generated by a script and checked in:
  home → ten T1 Sites (all touch home, so the opening offers ten runs); eight T1 open one
  T2 each (Intel, Breach, Virus among them), every T2 opens a T3, every plain T3 reaches
  the Renewal Engine (minimum path stays T1 → T2 → T3 → boss); four Heat objectives
  (Scrub Records −5 off t1_a, Purge Camera Logs −5 off t1_i, Wipe Biometrics −8 at T2 off
  t1_j, Burn the Ledger −8 at T3 off t2_e, so ICE 2 switches off Wipe Biometrics first);
  eleven locked cross-links opened by the Intel Exploit or an Icebreaker. Slice ids
  (`t1_a`, `t2_intel`, `t3_core`, `scrub_records`, `renewal_engine_site`) are unchanged so
  saves and tests carry over. GDD A.6 is now historical.
- **Terminal events: 19** (5 placeholders kept + 14 written): corporate memos (Continuum
  pricing, clause 44, the silent recall), street-merc trades, an auditor on break, the
  dosage cabinet, a honeypot, a Daemon broker and a Burner vendor, the Patient 0000-0000
  ghost record, **a rescue** (Locked Ward: 12 HP or 60 Cycles for a runner of a roster class) and the
  **DISPATCH clue chain** (Early Reply at T1, Escrow Receipt at T2, Voice Note at T3, all
  `dispatch_clue` + `foreshadows = dispatch`). Events honour `min_tier` (the pool filters
  on the run's tier). Original slang only (leash, subbie, bricked, ghosting).
- **Netrun map as a wireframe graph** (`NetrunMapView`): layers left to right, glyph per
  node type, current node cell_pink, reachable nodes cell_acid with a glow, visited nodes
  dimmed, Heat cost labelled; click a reachable node or press 1-9.
- **Raid playout** (`RaidPlayoutPanel`, GDD 7.2/9.3): the precomputed events are grouped
  by step (setup = link freezes/openings), shown at 0.9 s per step with 1×/2×/4× and Skip;
  threat markers move on the `GridMapView` (corporate dots + names), frozen links draw in
  resist_gold. Instant (straight to the summary) when headless or under reduce-effects,
  so the integration tests and the accessibility toggle both skip the wait. HQ and the
  mid-run interlude share the panel.
- **HQ screens**: start panel picks the ICE level (0..cap, with the cumulative ladder text)
  and the home-server variant; HQ sells next-run boosts and Profile unlocks and offers
  Rank 3 segment swaps per operative; the Grid lists every installable node type (locked
  ones disabled), an Upgrade button with its cost, switched-off objectives and ICE.
- Dense grids (> 16 Sites) draw smaller blocks with "T<n> <glyph>" labels.

### 2026-09-24 — Vertical-slice fixes, batch 2a: netrun and campaign rules (GAP_ANALYSIS §2.2-2.3)
- **Every remaining `RuleModifierType` is applied**: `HEAT_GAIN_PCT` scales positive Heat
  deltas and `HEAT_SINK_PCT` negative ones inside `HeatRules.add_heat` (a non-zero delta
  never rounds to zero); `PURGE_THRESHOLD` (ICE 17, value 90) makes the PURGE threshold
  fire at 90 (recorded as 100 in `thresholds_fired`); `HEAT_OBJECTIVE_SITES` (ICE 2, −1)
  switches off that many Heat-objective Sites at campaign start, the last by id
  (`CampaignState.disabled_objectives`, read through `CampaignRules.site_objective`);
  `DEATH_HEAT` and `EXPLOIT_HEAT` add to the base amounts before gain scaling;
  `CYCLE_PRICE_PCT` scales every Modem price including removals and overwrites;
  `REPAIR_COST_PCT` scales repairs; `SEIZED_RAID_STRENGTH_PCT` adds to raid strength when
  any entry Site is Seized; `RAID_EXTRA_WAVE` repeats the raid's last wave 5 steps later.
  Modifiers stack multiplicatively with ICE 1's gain (a death at ICE 8 is (10 + tier + 5)
  × 1.1), which is how a cumulative ladder should feel.
- **Node types complete** (GDD 3.2): Compiler Rack (a run launched next to an active one
  starts in the REWARD phase with one 1-of-3 card offer per adjacent Rack), Vault Terminal
  (+3 Schematics per completed run via `passive_effects`, +2 more next to a Firewall Relay
  via `adjacency_bonuses`, raid_priority 2, building it queues the NODE_BUILT raid) and
  Proxy Relay (−1 Heat per completed run; counts as a Relay for reach). Passives and
  adjacency bonuses with trigger ON_NETRUN_COMPLETE are evaluated in
  `CampaignRules.on_run_completed` for active nodes in id order; Disabled nodes give
  nothing. The three new nodes are **Profile unlocks** (30 Schematics each,
  `content/unlocks/`); `claim_error` refuses a locked node when a profile is passed.
- **Node upgrades** (GDD 11.4): `upgrade_node` costs `node_upgrade_costs[level]` (30, 60);
  each level adds `node_upgrade_integrity_pct` (50%) of the base integrity and
  `node_upgrade_asset_slots` (1) slots (`GridState` site `upgrade_level`). Home is not
  upgradable this way (variants cover it).
- **Home-server variants** (GDD 3.1): internal nodes fold into the home server's capacity
  (integrity, asset slots, built-in defenses in `GridState.home_asset_slots /
  home_built_in`) rather than becoming Grid sites; the Bunker variant (40 + 30 integrity,
  1 + 2 slots, built-in turret) is a 40-Schematic Profile unlock. `RunManager.new_campaign`
  takes the ICE level and the variant.
- **Netrun boosts** (GDD 11.4): `NetrunBoostData` (cycles, run-only cards, max RAM bonus)
  listed in `config.netrun_boosts`; bought at HQ into `CampaignState.pending_boosts`, all
  consumed by the next run (`RunState.temp_cards` leave the deck on completion). Warm
  Cache 10 (+40 Cycles), Overclocked Deck 15 (two Jolts), Field Kit 20 (+2 max RAM).
- **Routers drop common Firmware** with `router_firmware_chance` (0.35), 1-of-2 from
  Firmware of rarity COMMON; elites keep 1-of-2 of any rarity.
- **Raid triggers** (GDD 4.4): RETALIATION raids follow every Exploit and Heat-objective
  run and enter from the Site just cleared; STORY raids fire from beats marked
  `StoryBeatData.triggers_raid` (Ghost Patient II); NODE_BUILT raids from nodes with
  `triggers_raid` (Vault Terminal), falling back to the claim raid when a corporation has
  no such template. Solace gained three raid templates and two threats: **Icebreaker**
  (`alters_edges`: opens the first locked link, by id, touching its entry; the route
  stays open) and **Lockdown Unit** (`freezes_edges`: freezes the link between home and
  the neighbour holding the most deployed assets for that raid only; nothing routes or
  shoots across a frozen link). Both resolve in setup so the projection shows them.
- **Stationed operatives** return unharmed from Disabled nodes too (cascade included).
- **Rank counts full netruns only**: Reclaim runs (one fight) no longer raise Rank; the
  breach ends the campaign. `runs_completed` still counts them.
- **ICE progression** (GDD 3.4): `ProfileState.ice_cap_for` = max(3, best on that
  corporation + 3, global best − `new_corp_ice_offset`), capped at 20. A fresh profile
  chooses ICE 0–3.
- **Schema changes**: `NetrunBoostData` (new), `CampaignConfigData.netrun_boosts /
  node_upgrade_integrity_pct / node_upgrade_asset_slots / router_firmware_chance /
  router_firmware_choices`, `StoryBeatData.triggers_raid`, `GridState.home_asset_slots /
  home_built_in / frozen_links / upgrade_level`, `CampaignState.pending_boosts /
  disabled_objectives / home_variant_id`, `RunState.temp_cards`. Smoke test batch 5.

### 2026-09-24 — Vertical-slice fixes, batch 1: combat rules (GAP_ANALYSIS §2.1)
Designer instruction: "make calls on every decision". Every call below is logged here
and annotated in the GDD where it changes a rule.
- **ICE/Heat combat modifiers are applied through `NetrunSession.rule_overrides()`**:
  `ENEMY_RESISTANCE` adds passive resistance to every non-satellite enemy (satellites are
  nudged individually and stay at 0); `BOSS_STRENGTH_PCT` multiplies HP and output of the
  final boss **and mini-bosses** (the designer's "up the boss numbers"); `BOSS_EXTRA_POINTER`
  adds pointers to the final boss only, evenly spaced (offsets 15, 10, 20, 5, 25 from
  pointer 0, first free wins) and survives phase changes via the trim/add rules;
  `NO_FIRST_TURN_FREE_NUDGE` zeroes the free nudge on turn 1 only; `STARTING_BUG_CARD`
  puts N **Bug** cards (0 RAM, drains 1 RAM, exhaust, `CardData.offered = false` so it is
  never a reward or Modem stock) into the working deck at run start — a Modem removal
  is the counterplay, and the roster copy only inherits them on completion.
- **HeatGatedEffectData is live**: an enemy's `heat_effects` join its listeners while the
  Heat at combat start (`CombatState.campaign_heat`) is at or above `min_heat`. Content:
  Compliance Officer at Heat 50+ drains 1 RAM per attack ("Audit"); Account Manager at
  Heat 75+ heals 5 per turn ("Retainer").
- **Satellite spawns**: `ON_TURN_START` spawns count every start of turn (turn 1
  included), fire every `every_n`, and only while fewer than `max_active` satellites of
  that template are alive on the host.
- **MIGRATE is telegraphed**: entering a MIGRATE phase stores the layout in
  `WheelState.pending_pointer_ticks` (event `boss_migrate_telegraph`); the pointers move at
  that wheel's next start of turn (event `boss_migrate`). The view draws the pending
  pointers dashed in cell_acid with a "next" tag and flickers the current ones. Account
  Manager gained a 25% MIGRATE phase (pointers 5 and 20).
- **`BossPhaseData.wheel_override`** swaps slices, Firmware, statuses (reset) and passive
  resistance; rotation, pointers and pending migrations are kept; the override's hub
  applies unless `hub_override` is set. The Renewal Engine's ORBIT phase now swaps its
  second Atk 14 for a Crit 24.
- **Player drones (GDD 5.2)** live in `CombatState.drones` as satellites with
  `is_player = true`, host `player`. A DEPLOY slice docks the Hub's `drone` template
  (new `HubCoreData.drone`) on the Deploy slice itself or the next free slice clockwise,
  up to `max_drones`; `DEPLOY_DRONE` effects may pick the slice (`slice_pick`). A drone
  resolves only in a turn where the slice it docks on resolves (any player pointer), at
  full output, against the player's target; enemy attacks aimed at a guarded slice hit
  the drone (same bodyguard rule as enemy satellites). Drones respin with the wheel, do
  not get Kernel Sync or Daemon listeners, and die like satellites (deaths of combatants
  spawned mid-resolve are reported the same turn). Drones persisting between combats
  (Botnet passive) is left to the Botnet class work.
- **Rule-breaking Daemons**: Linked Bus echoes nudge *actions* (not nudge cards) on
  enemy wheels to your wheel, free, ignoring resistance; Stolen Intent fires automatically
  once per combat when your first pointer would resolve Miss and the target's first
  pointer would not, swapping the two slices (own tiers kept) through the new
  `ON_RESOLVE` trigger that hands handlers the collected resolutions; Twin Pointer adds a
  pointer 15 ticks from yours at combat start (`ON_COMBAT_START` Daemon hooks now run in
  `begin_combat`) and halves max RAM rounding up (`CombatState.max_ram`, 12 → 6); Botnet
  Seed docks a 1-HP `seed_drone` on the Perfect slice, max 2 seed drones alive.
- **Ring segments** Corrupt (ON_SLICE_TRIGGER → CORRUPTED on the target's slice under the
  matching pointer, clamped to its last pointer), Anchor (ON_PERFECT → FREEZE own wheel),
  Accelerator (ON_SLICE_TRIGGER → `DOUBLE_NUDGE_CARDS`: nudge cards resolve twice next
  turn, `CombatState.double_nudge_cards[_next]`), Echo (RETRIGGER ×0.5) are data. **Rank 3
  swap flow**: `RankRewardData.ring_segment_options` (Breaker: all four),
  `OperativeState.ring_segment_ids`, `CampaignRules.swap_ring_segment()` (free, any time
  between runs, empty id restores the default), passed to combat as the
  `ring_segment_ids` override.
- **RAM Respin action** (GDD 2.5 lists Respin as a card, 11.3 prices it at 4 RAM; the card
  pool has none): `CombatAction.RESPIN` respins your own wheel for `respin_ram_cost`, is a
  random event (checkpoint) and previews exactly. Key X.
- **Combat UI**: chosen-slice picker (F cycles, auto = none) and card direction picker (D)
  feed `CombatAction.slot_index` / `direction`; random effects (Respin, random slice picks)
  show **odds** as the slice-type mix of the wheel instead of the roll; right-click
  **inspect** describes the slice, Firmware, status and guard under the cursor (or the
  hub/segments at the centre) via the new `Codex` helper, in the left-column note that
  otherwise lists the installed Daemons; revealed boss phases (Intel) print on the enemy
  wheel; the log strip plays the three passes with a 0.35 s beat between them (instant
  under headless or reduce-effects; the wheels always show the final state at once).
- **Schema changes** (rule 8): `CardData.offered`, `HubCoreData.drone`,
  `RC.Trigger.ON_RESOLVE` (appended), `CombatAction.Type.RESPIN` (appended),
  `WheelState.pending_pointer_ticks`, `CombatState.drones/max_ram/campaign_heat/
  double_nudge_cards[_next]`, `OperativeState.ring_segment_ids`. Smoke test batch 4.
- **Timeline captures** (`docs/timeline/`): the designer asked for screen captures per
  system over time; each batch adds dated frames.

### 2026-09-24 — M4 Look, Feel & Accessibility
- **No approved mockups are in the repo** (STYLE_GUIDE points at a private canvas), so the
  screens follow the style guide's component rules literally: three worlds per screen,
  colour tokens in `Palette`, the three fonts, zine kit elements by name (Polaroid,
  ransom-note Heat, marker RAM tally, torn-paper log strip, SEND IT stamp, card stickers,
  graffiti tag, wanted poster, pirate radio, JACK IN, THE PLAN sidebar). Automated
  layout rules: zine elements never intersect a wheel's disc; player wheel `cell_pink`,
  enemy wheels `corp_*`; each screen shows its world background.
- **Fonts** (Permanent Marker — Apache 2.0, Anton and Share Tech Mono — OFL 1.1) are
  vendored from github.com/google/fonts with their licences in `assets/fonts/`.
- **Effects architecture:** one `Fx` autoload (CanvasLayer) owns the scanline / flicker /
  chromatic overlay (all three are shader uniforms), the Heat distortion pulse, screen
  flashes and the jack-in / jack-out transition. `Settings.reduce_effects` hides the
  overlay, zeroes the distortion, freezes background animation and skips freeze frames and
  stutter shakes. The glow and paper shaders are static and stay on.
- **Flash limiter** is a pure sliding-window class (`FlashLimiter`, 3 per rolling second)
  used by `Fx.flash()` and by the automated event-stream check, which maps the flash-worthy
  combat event types (Perfect retrigger, boss phase, Heat threshold, combat end, Zero Day)
  onto a timeline and asserts no one-second window holds more than three.
- **Without-colour readability:** a distinct glyph per slice type (▲ ✦ ■ ◇ ⬢ ⬡ ✚ ◈ ✕) and
  per status (☠ ⚡ ⌗) plus text tags; the Miss slice has a dashed outline; resistance is
  labelled, not only gold.
- **Keyboard play:** 1–9 play cards, Q/E nudge, W nudge wheel toggle, R ring toggle, T card
  target toggle, Tab target, Space end turn, Z / Ctrl+Z rewind, Esc settings; cards and the
  stamp are focusable.
- **Placeholder audio is generated in code** (`AudioDirector`): ratchet ticks, spins as
  decelerating click runs, flip clack, latch/click/stutter/static precision feedback, and
  4-second loops per music context with a Heat layer for combat. Real assets swap in behind
  the same API.
- **Performance:** fps at 1080p cannot be measured headless; the core budget is enforced
  by test (< 1 ms per resolved turn including state duplication) and every effect is a
  cheap 2D shader or `_draw` call that reduce-effects can disable.

### 2026-09-24 — M3 Campaign & Raids
- **Grid runtime state** (`GridState`) records per Site: status (corporate / cleared /
  claimed / Seized), installed node id, integrity, condition (OK / Disabled), deployed
  assets and the stationed operative; plus home integrity and Intel-opened links. Layout
  stays in `CityGridData`. `NetworkNodeData` gained an `id` so nodes are content ids.
- **Heat thresholds** (`HeatRules`): events fire on upward crossings not yet in
  `thresholds_fired`; the MAJOR/PURGE raid goes to `pending_raids`, MINOR complications to
  `pending_complications` (consumed by the next netrun: shop stock −1, elite +25%).
  Modifiers are read live (`CampaignState.rule_modifier`), so they switch off by
  themselves below the threshold. ICE levels ≤ `ice_level` stack with them.
- **Raids resolve at HQ** (between runs). Threshold raids reached mid-run wait in the
  queue until the operative returns; the "mid-run interlude" of GDD §4.4 is deferred
  (open question). Setup projection and playout are the same pure `RaidResolver.resolve`
  on copies, so projection always equals the result.
- **Raid step rules** (TECH_SPEC §7 filled in): threats spawn wave *k* at step 1 + 5*k*
  at the entry Sites (corporate or Seized Sites adjacent to the territory; the boss Site
  as a last resort). Movement follows shortest paths (ties by Site id) toward the routing
  target: home, the highest-value node (`raid_priority`, then install cost) or the weakest
  node; a Decoy overrides the target. Entering a live claimed node (or home) ends the
  step's advance; Disabled and unclaimed Sites are passed through. A threat camps on its
  target node until it falls. ICE Locks hold each threat once per lock. Assets and
  built-in defenses fire per node in Site-id order (FIRST_IN_PATH = nearest to home,
  ties by content id then threat id). Node damage: 0 → Disabled, `floor(excess ×
  cascade_ratio)` to each adjacent claimed node (no chaining); a threat ending a step on a
  Disabled node Seizes it; a Seized Site loses its node, assets and station; damage at
  home reduces integrity, 0 = campaign lost; a threat that reaches home is done. Step cap
  30 then Seizes every node still occupied. Win = every threat destroyed → RaidData
  reward; otherwise +5 Heat. RAID_STRENGTH_PCT scales threat integrity and damage.
- **Claiming** needs a cleared Site adjacent to home or to a live Relay/Firewall Relay
  ("Relay lets you claim Sites beyond it"), costs the node's install cost, and provokes a
  TERRITORY_CLAIM raid when the Site touches a corporate or Seized Site (GDD §4.4).
- **Node slots** (content): Relay 1 asset slot, Firewall Relay 2 (+ built-in 3-damage
  turret), Safehouse 1 (+1 station slot), home 2. Station bonuses are recorded but not
  yet applied in raids (open question on scaling).
- **Special runs:** the final breach and Reclaim runs are one-node `NetrunSession`s
  (`kind` boss / reclaim) so save/resume and the netrun scene work unchanged. Reclaim pays
  the 10–20 "Combat" Cycles and offers nothing else.
- **Boss phases** (`CombatResolver._check_boss_phases`) enter after deaths each turn;
  MULTIPLY/MIGRATE set the pointer layout, ORBIT sets `pointer_orbit`, phase spawns dock,
  hub overrides swap the Hub. Breach removes pointers in every layout but never below one;
  Virus corrupts two random non-Miss boss slices at the start; Intel only flags
  `reveal_phases` for the HUD.
- **Story:** one path is picked at campaign start from the corporation's weighted list
  using the `events` stream of the campaign seed; each Exploit reveals the next beat; the
  finale is shown on the win. Solace ships five placeholder paths of 3 beats + finale.
- **Profile** (`ProfileState`, `profile.json`): campaigns started/won/lost, runs completed,
  operatives lost, raids won/lost, best ICE overall and per corporation.
- **State dictionaries are JSON-normalised on `to_dict()`** (`RunState`, `CampaignState`)
  so a saved-and-reloaded state hashes identically (ints become floats either way).
- **Breaker Rank 2/3 rewards** exist only for tier gating (T3 / T4); the Rank 2 Hub
  upgrade and Rank 3 segment options are content for later (CONTENT_SLICES.md).
- **Scenes:** the HQ scene is the main scene (start → HQ → City Grid → launch → netrun
  scene → back to HQ; raids from HQ). RunManager owns profile, campaign, corporation and
  run; scene switching can be disabled for tests.

### 2026-09-24 — M2 Netrun Loop
- **Run randomness** comes from the run's own `RngStreams` (pure core class; `RngService`
  now wraps it) seeded from a run seed drawn from the campaign `map` stream: `map` builds
  the map, `combat` picks enemies and seeds each fight, `rewards` rolls Cycles, asset drops,
  offers and shop stock, `events` picks Terminal events. Stream states are saved with the
  run, so a resumed run continues identically.
- **Map generator** follows TECH_SPEC §6 with non-crossing edges built as monotone chains
  (each node 1–2 forward edges; every next-layer node covered; provably reachable both
  ways). New config: `map_modem_layers` (3–5), `map_elite_layers` (3–6),
  `map_elites_per_layer` (1), `map_terminal_ratio` (0.25). Elite Heat (+1) is charged on
  entering the node; Server Rack Heat is charged on *capture* (11.5 says "capture", and
  Scrubber needs to replace it).
- **Cycles per node:** Router 15–25 (`cycles_router_range`), Elite Router and Server Rack
  30–40 (`cycles_elite_range`); "Combat 10–20" is reserved for non-node fights (Reclaim,
  events). Rewards scale ×1.7^(tier−1); enemy HP and slice outputs ×1.6^(tier−1) via
  `CombatantState.output_scale`.
- **Rewards:** every won fight offers 1-of-3 cards from the shared pool plus the class's
  exclusives (no duplicate within an offer; skip allowed); elite Routers add 1-of-2
  Firmware (the player picks the socket; must fit the slice type); Server Racks add 1-of-3
  Daemons not yet owned, bank `rack_schematics_by_tier` and any unbanked assets. Asset drop
  chance 0.4 per fight from the A.5 assets; assets are unbanked until a Rack.
- **Modem stock:** 3 cards, 2 Firmware, 1 Daemon (prices rolled in the §11.2 ranges), card
  removal at 50 (+25 per removal), slice overwrite 100 (150 for the Miss slot). The
  overwrite options are the distinct non-Miss slices already on the operative's wheel
  (open question: a real slice catalogue).
- **Enemy pools** are derived from content, not a CorporationData (arrives with the City
  Grid in M3): EnemyData with `corporation_id == "solace"`, 6-slice wheel, not boss;
  `is_elite` splits normal/elite. Terminal events: `TerminalEventData` with matching or
  empty corporation, weighted pick.
- **Operative state** (`OperativeState`) carries the current wheel layout (slice ids +
  Firmware sockets), deck, Daemons, HP and Rank; a run works on a copy written back to the
  roster only on completion (death: permadeath, the roster entry is marked dead).
- **Daemon hooks.** Data-driven Daemons are plain listeners in TECH_SPEC order after the
  Hub. Rule-breakers use `custom_handler` scripts with
  `handle(context, state, rng) -> Array[Dictionary]`; combat handlers get every trigger with
  `context.trigger`, run-level handlers get ON_SERVER_RACK_CAPTURE / ON_NETRUN_COMPLETE with
  the RunState. Kernel Sync's +1 applies from the *next* attack after the Perfect.
  Zero Day = 3 × the wheel's best Crit output (else best Attack) at the pointer target.
- **Custom card effects** (`EffectType.CUSTOM` + handler): Ring Lock, Momentum, Calibrate,
  Steady Hand, Undock. Per-combat markers live in `CombatState.flags` / `ring_locked` /
  `ram_bonus_next_turn` / `damage_bonus` so they save, preview and replay like everything
  else.
- **Firmware neighbour rules** add derived resolutions before the passes: Mirror copies the
  neighbour on the landed side (both on Perfect) at the landing's tier; Shunt resolves that
  neighbour instead at ×1.5 and does nothing special on Perfect. Positive offset = landed
  clockwise = neighbour slot +1.
- **Billing Daemon** drains RAM through DRAIN_RAM slice effects (`atk_7_drain`,
  `crit_12_drain`); **Recall Unit** orbit is a new `WheelData.pointer_orbit_per_turn` (+2,
  applied from turn 2 on); **Care Swarm** drones dock on random free slots.
- **Save file:** one JSON per campaign slot (`user://saves/campaign_<slot>.json`) holding
  the campaign, the run (with its live combat session, checkpoint and streams) and the
  campaign RNG. Autosave on entering a node, after each combat, after every reward/event/
  shop step and on quit. A combat's `setup` is JSON-normalised on creation so a resumed
  session hashes identically.
- **Scenes:** the netrun scene is the main scene (start screen → map → embedded combat →
  reward/event/shop → summary). The combat scene keeps its standalone picker for M1-style
  testing (`auto_start`).

### 2026-09-24 — M1 Combat Core
- **Designer rulings applied (from the M0 review):** Godot pin moved to **4.7** (GUT
  9.7.1); elite frequency placeholder 25% confirmed; `BOSS_PHASE_EARLY` dropped in favour
  of a new `RuleModifierType.BOSS_STRENGTH_PCT` (boss HP and damage +25% at ICE 9; the
  old enum value stays so stored numbers keep meaning; GDD §11.9 "bosses change pointers
  earlier" is superseded); minor Heat complications alternate shop stock −1 (10/30/60/80)
  and elite frequency +25% (20/40/70/90); RAM cap is **12** as GDD §2.2/§5.2 already state,
  carried by `ClassData.max_ram` (`ram_regen_per_turn` removed from the config so RAM has
  one source of truth).
- **Flip math.** GDD §2.3's code block and TECH_SPEC §5.1 both say
  `tick = (rotation + pointer + 15 if flipped) mod 30`; the prose ("mirrors… slice order
  reverses") would be `pointer + 15 − rotation`. The code block is implemented; the
  discrepancy is logged as an open question.
- **State references content by id.** `WheelState` stores slice / Firmware / Hub / ring
  segment ids and resolves them through a `ContentLookup` handed to the resolver, so the
  core never touches the ContentRegistry autoload and tests can inject in-memory content.
- **One status per slice.** ENCRYPTED absorbs the next status and clears; OVERCLOCKED
  becomes CORRUPTED after its trigger; permanent Firmware statuses (Hardened, Burner) come
  from the Firmware, not the status slot. CORRUPTED self-damage ignores block/shield and is
  applied in the status pass for every corrupted slice that resolved this turn.
- **Simultaneity.** All pointers are collected before any pass; a combatant reduced to 0 HP
  still resolves the rest of the turn; deaths and the outcome apply after the status pass.
  A dead host takes its satellites with it.
- **Pointer rule.** Every attack instance hits once per pointer of the target wheel; the
  bodyguard check uses the target's slice under *that* pointer. Pierce ignores satellites
  and block but not shield (shield is a separate resource; open question).
- **Retrigger.** RETRIGGER effects (Breaker Perfect hook, Echo) are counted before the
  slice resolves; each extra instance repeats the base action and the slice's listeners.
- **Output rounding:** `roundi(base × multipliers)` (Partial 0.5, Overclock 1.5, ring ×2).
- **Breaker "+1 spin on all cards"** is data: a PASSIVE-trigger SPIN effect on the Hub
  Core; the interpreter adds its amount to every SPIN a card performs.
- **Slice selection for slice-level effects** is a new `EffectData.slice_pick`
  (UNDER_POINTER / RANDOM_NON_MISS / CHOSEN). DOSE = RANDOM_NON_MISS, never an
  already-corrupted slice. Convention: a NUDGE effect with `multiplier 0.0` ignores
  resistance (Jam). Fine Tune's ring and direction come from the action.
- **Enemy targeting:** enemies and satellites always attack the operative; the operative's
  pointer attacks and cards aim at `CombatState.target_id` (Tab / target list), which may
  be a satellite.
- **Checkpoints are detected, not declared:** `CombatSession.apply()` compares the RNG
  state before and after; any action that consumed RNG (End Turn respins, DOSE's random
  slice, Respin, a reshuffle on draw) becomes the new checkpoint. Rewind restores the
  checkpoint and replays the rest. Preview clones the RNG, so the preview of a random
  effect is exact in the engine; the scene deliberately shows DOSE as "random non-Miss
  slice" rather than the exact slot (GDD §2.10 says random effects show odds).
- **Respin** adds `2×30 + rand(0..29)` ticks so views can animate direction and distance;
  the inner ring respins independently; a Respin clears `flipped`.
- **Hub Breach** removes the hub's resistance from the pool at once and disables hub
  passives; the breach counter decrements at the next start of turn (one full turn).
- **Combat scene starts the Breaker at Rank 1** (ring installed) so every M1 mechanic is
  visible; the rank-0 path is covered by tests.
- **Breaker slice values** are placeholders (Crit 12 / Atk 6 / Def 5, matching the schema
  smoke test) because GDD §5.2 lists types only.

### 2026-09-24 — M0 Foundation
- **Engine used for verification: Godot 4.7.2** (only 4.6.2 / 4.7.x are installed on the
  dev machine). M0 kept the 4.3 pin; _superseded in M1_: the designer moved the pin to 4.7,
  so `*.uid` sidecars are now committed.
- **GUT 9.4.0** was vendored in M0; _superseded in M1_ by GUT 9.7.1 (the Godot 4.7 tag).
  `.gutconfig.json` enables `include_subdirs` so `-gdir=res://tests` picks up `unit/`,
  `integration/` and the non-test `helpers/`.
- **Fresh clone needs one import** before the `-s` tools work:
  `godot --headless --path . --import` builds the global script-class cache.
- **`-s` tool scripts compile before autoloads exist.** `tools/validate_content.gd`
  preloads `content_registry.gd`, so the registry looks SignalBus up by node path instead
  of naming the singleton. Other autoloads may name singletons directly.
- **ContentRegistry:** ids are collected from every `.tres/.res` under `res://content`
  *and* from resources nested inside them (Hub Cores, cards, slices…). The same instance
  reached twice is fine; two different instances with the same id is a duplicate and fails
  validation. Files are visited in sorted path order (rule 7: no dictionary-order ties).
  `validate()` runs every resource's `validate()` and prefixes problems with class + id.
- **RngService:** stream seed = `hash([campaign_seed, stream_name])` (TECH_SPEC §4). Save
  representation stores seeds and states as decimal strings because JSON round-trips
  integers exactly only up to 2^53 and `RandomNumberGenerator.state` is 64-bit.
- **SaveService skeleton:** every file gets a top-level `"version"`; `migrate()` walks a
  table of `from_version -> Callable` steps. JSON numbers come back as floats, so loaders
  must `int()` what they read; 64-bit values travel as strings (see RngService).
- **CampaignConfigData schema additions** so every GDD §11 number lives in
  `content/config/campaign_config.tres` (rule 5): `exploit_heat`; Cycle reward ranges
  (`cycles_combat_range`, `cycles_elite_range`, `cycles_router_range`); new group
  **Shop** (card/firmware/daemon price ranges, card removal price + increment, slice and
  Miss-slice overwrite prices); new group **Schematic costs** (rookie, node base, node
  upgrade costs, netrun boost range, Heat purchase amount/cost/increment, class unlock);
  Combat `ram_regen_per_turn` and `respin_ram_cost`. Ranges use `Vector2i(min, max)`.
  `validate()` checks min ≤ max and non-empty upgrade costs. Smoke test batch 3 covers it.
- **Heat thresholds in data (GDD §4.3):** MINOR at 10/20/30/40/60/70/80/90, MAJOR at
  25/50/75, PURGE at 100. MAJOR ongoing modifiers: 25 → ELITE_FREQUENCY_PCT, 50 →
  ENEMY_RESISTANCE +1, 75 → RAID_STRENGTH_PCT +25. MINOR one-time complications alternate
  the two examples the GDD gives (shop stock −1 / extra elite). `event_raid` stays null
  until M3 authors RaidData.
- **ICE ladder in data (GDD §11.9):** one change per level, in the order the GDD lists them
  within each band (ICE 1 = Heat gain +10% … ICE 6 = Heat sinks −15%, matching the schema
  README example). Bands 6–10, 11–15 and 16–20 list four changes each, so levels 10, 15 and
  20 carry no modifier and are marked "Reserved" in their description.
- **Input map (GDD §9.5):** actions `nudge_left` (Q), `nudge_right` (E), `cycle_target`
  (Tab), `end_turn` (Space), `rewind` (Z and Ctrl+Z), `inspect` (right mouse). Physical
  keycodes, so layouts other than QWERTY keep the key positions.
- **Display:** 1280×720 viewport, `canvas_items` stretch, `keep` aspect (TECH_SPEC §10).

## Open questions for the designer
- **Parity fix TITLE-01 (2026-10-05, built, see "Parity fix — TITLE-01 title backdrop"):** (1) the title's HQ is the
  last-played campaign's target, else Halcyon (the concept's): keep, or always Halcyon? (2) the 3D city's night grade
  is less pink-saturated than round 33's 2D render: leave it (it is the Grid's grade too) or give the backdrop look its
  own grade? (3) LOOT-04: should the loot / event / shop overlays take the same blurred city (one call with their own
  `CityBackdropLook`)?
- **ART-3 6w raid on the city (2026-10-05, defaults built, see "Art direction — ART-3 6w raid on the city"):**
  (1) the raid's widest zoom is ortho 640 (the bible's round 39 clamp 220-380 no longer holds the x2 spread
  network on the setup's map part): keep, or shrink the network's spread for the raid? (2) the sockets float over
  their roofs above the uplink pads (3A's placement) instead of sitting on the street as the concept's circuit
  inlay: keep?
- **ART-8 8w keycard words (default implemented):** the Exploit keycards are the concept generator's
  own art (round 38 `exploits.py`) with their words baked in English (the corp band, the kind INTEL / BREACH
  / VIRUS, the item name, the effect line), so they cannot be translated. Kept as made (orchestrator's call,
  the reuse rule). Should a text-free card (art only, the words drawn by the game through tr()) be exported
  later for other languages?
- **ART-8 8w combat close-up framing (default implemented):** the city backdrop frames every corp's HQ at one
  ortho (140) and height (30 BU); Solace's helix (111 BU) is cut at its top. Per-corp framing (or a fit to
  the landmark's box) is a small follow-up if the designer wants the whole HQ in frame.
- **Asset parity, card kinds (2026-10-05, default implemented):** the concept's card face has three kinds, WHEEL / HACK /
  SYSTEM. The game's violet "other" family (rest and similar cards) is drawn as SYSTEM (cyan). Is a fourth face wanted?
- **ART-12 12s skins (2026-10-05; default built, see "Art direction — ART-12 12s skins"):** (1) skins are
  free in Options > Display; should they become Profile unlocks (UnlockKind.SKIN) instead? (2) the set is
  v2 + cobalt + graphite (a sea-green skin was dropped for sitting between PROTECT and GAIN); say if you
  want others, or skins for the corp kits too.

- **ART-5 5c city motion (defaults implemented):** (1) the netrun transit turns the sky-lane
  cars off (bible 4.1) while `cars_lod` shows the CLOSE tier at a netrun close-up: CLOSE is built
  and tested but only shows below ortho 150 outside the netrun band; should the transit show it?
  **Answered by ART-7 7w (art pass `cars_lod`):** yes, at a netrun close-up below ortho 150; at
  the transit's own fitted zoom the cars stay off.
  (2) reduce motion pauses street traffic (brief) where bible 5.4 says 40 % without streaks.
  (3) 5a: a public day-look call on CityView3D (CityViewMotion sets the view's materials for now).
  ART-5 5e: (2) and (3) are built (the art pass's 40 % rule; `CityView3D.set_night_share`).

- **ART-5 5e city integration (defaults built, see "Art direction — ART-5 5e city
  integration"):** (1) which Sites carry the Site landmarks: Solace `t1_c` Patient Records
  Vault, Halcyon `lose_the_case_file`, Orbital `o1_d` Subscriber Uplink Office
  (`CityConfig.site_landmarks`); Meridian and the Cell have none. (2) The x2 spread is aimed
  into each territory (Halcyon and the Cell run up the screen, Meridian diagonally); the
  alternative was a smaller spread with 5a's left-to-right Grids. (3) The Grid is always night:
  no rule drives day or suspicion. (4) DISPATCH's fist shows on the Cell's district in the
  REBEL_CELL campaign only. (5) The Cell's blackout reveal plays once per game session, on the
  first Grid visit.

- **ART-6 3A (raid):** "Remove to hand = click the node" (ART_BIBLE v2 §4.8 card drag) changes what a click on a
  claimed node does in the raid setup (today it picks the target for the cards, a behaviour the pad path and
  several tests rely on). Default kept: click = pick the target; a defence returns by its Withdraw button or a
  drag to the loadout. Confirm the change, and whether the pad keeps a separate target pick.

### 2026-10-05 — ART-10 4C: hold-to-confirm on the abandon dialog's verb
ART_BIBLE §4.13 calls the pad's 0.8 s hold on the committing verb (BURN IT) a proposal: not built
(A presses it like any button). Default: no hold. Build it if the designer wants it.

### 2026-10-05 — ART-10 4C: an in-run "abandon run" (the dialog's own subject)
The round 33 abandon dialog asks "Abandon the run?" (operative lost with everything unbanked, Heat
+10 + tier, banked Schematics stay). The GDD has no voluntary abandon (a run ends by death, jack-out
or completion), so it is a mechanic and is not built. Default: the dialog (`AbandonDialog`, with
`dialog_burn_it` baked) serves the title's delete slot. If the designer wants an abandon-run line in
the netrun pause menu, its rule would be the death rule (GDD 4.2) and the dialog takes its costs.

### 2026-10-05 — ART-10 4C: the HQ dossier on corp paper and JACK IN as a vinyl sticker
The crew dossier keeps its paper card with Courier Prime (1B's CorpPaperPanel would need its orders
and HP strip re-laid round the letterhead and stamp slot); JACK IN keeps its ZineStamp (its
`jack_ring_breathe` motion and tests). Default: as is; proposed as a slice with ART-5 / G13.

- **ART-5 5b: the REBEL_CELL fist on the real city (2026-10-05):** the landmark export carries a standalone district
  patch and the crest as a mask texture; on the unified city the fist must be the city's own buildings' windows
  (bible 4.4). Default: 5a's CityModel window shader samples `rebel_cell_crest_mask.png` at the palm of the Cell's
  district and the district glTF stays a reference. Also: crest size 110 BU tall on the iso screen (map34's 880 px at
  8 px/BU); say if the fist should scale with the zoom instead.

- **ART-7 3B (netrun):** (1) a per-node "HEAT: +1 ELITE" mark needs the elite-frequency
  Heat modifier to pick nodes (today it changes map generation), so it is not drawn; (2) the
  "available" ring stays the run orange for every corporation (Appendix C #22); (3) ~~transit v3's
  bridge hops and crossing avoidance wait for the 3D city's cable router (wave 2).~~ Built by
  ART-7 7w (`RouteCableRouter`, see "Art direction — ART-7 7w netrun on the city").

- **Grid Site markers v4 (2026-10-05, ART-5 5d; defaults built, see "Art direction — ART-5 5d Grid
  markers and key"):**
  1. Hidden Sites show only through the key's SHOW ALL, until D13's "Always show all nodes" setting
     covers the Grid too.
  2. The VIRUS badge follows 1C's table (`status_corrupted`), not the bible's INFECT glyph.
  3. A DOWN node's fight-won lights go dark.
- **MAINFRAME facade state and the recycle bin's slice (2026-10-05, ART-9 4A):** (1) the facade
  bakes exist for day, night and rain, but the game has no time of day or weather; a visit picks
  one by hash (night 2 in 4). Default: keep the hash until the city gets a time of day. (2) the
  bible's recycle bin also takes a dropped slice and plays crumple / fizz / lid; removing a slice
  is not a rule. Default: the bin takes cards only (the current removal); proposed slice: the
  bin's lid and crumple animation on a card removal (ART-12 polish), the slice drop only if the
  designer adds slice removal. (3) the takeover plays once per visit after 6 s; whether it should
  repeat while the player stays is open. Default: once.
- ~~**ART-8 8p: where is DISPATCH's HQ run, and does an HQ run become a map? (2026-10-05):**~~ resolved by the
  standing ruling "the art pass design is correct" (orchestrator, 2026-10-05): the latest lock wins, so DISPATCH's
  HQ run is set in the round 43 Tokyo canyon (built in ART-8 wave 2, static until G12); the HQ run stays a single
  breach node until G12 / G11 rule otherwise. Original note: the compounds are built
  on today's rules, where the HQ run is the single breach node (all slots exist for a full 7-layer run map at the
  HQ as well). Defaults: REBEL_CELL's compound is DISPATCH's base (round 42 `rebel_base`, dispatch state) with
  DISPATCH CORE on the relay mast; the round 43 Sync Strike / mirror ideas play in the Tokyo canyon instead and wait
  for G12 — say if the canyon should replace the base. Meridian's train and the crane's moves, Solace's crossover
  walkways, Halcyon's eye sweep and Orbital's silo loop are left out until G12 says how they play.

- **ART-2 2A: tier I screen gain, interim corp crests (2026-10-05):** the wheels show tier I
  slices at full screen gain (the combat v4 mocks), not ART_BIBLE §3.7's 60 %; say if tier I should
  dim once slice tiers exist. The corp crests are interim recipe renders until the glyph atlas
  carries them.

- **ART-2 2D: boss nudge keys A / D (2026-10-05):** ART_BIBLE v2 §3.1 proposes [A] / [D] for the
  boss wheel's nudges ("check bindings"). Main has one nudge key pair (Q / E) that drives the wheel W
  picks (own or target, H23); A / D would be a new rebindable pair (Settings, the rebind page, the pad
  map). Default kept: Q / E on the driven wheel, the key shown under its nudge buttons. Say if A / D
  should be added.
- **ART-2 2D: run results on the combat chips (2026-10-05):** the D15 chips carry the wheel's own
  results; the run-wide ones the tag used to list (DRAW, CYCLES, SCHEMATICS, FREE NUDGE NEXT, +N DRONE...)
  are in the operative's breakdown tooltip only. Say if they should get a small row of their own.

- **ART-11 4D: the auditor's ballpoint hand and the dossier's words (2026-10-05):** the bible names
  "auditor's blue ballpoint post-its" but ships no ballpoint face; the post-its, captions and signature
  use Permanent Marker (the one handwriting face) small and in ballpoint blue. Say if a ballpoint face
  (an OFL hand) should be fetched. The auditors' names (A. VANCE, R. OKAFOR, DR. L. MERCER, K. TANAKA,
  ECHO 00), the divisions and the notices' reference numbers are flavour picked from the concepts (Halcyon's)
  or made up in their style; the won file's stamp is AT LARGE (the bible says only "campaign won in the
  same language"). The intercepted story beats show by title (their text in a tooltip) so the open file
  fits one screen at text scale 1.0; say if the full text should come back (the page then scrolls).

- **Combat backdrop day / night and the REBEL_CELL Site (2026-10-05, ART-2 2B):** the game has no
  clock, so the backdrop alternates by run (odd runs by the cool day). Default applied; say if day
  should follow something else (Heat, a city clock in ART-5). The REBEL_CELL regular Site (the
  MAINFRAME shop) has no model in the concept scripts: regular fights there use the HOME canyon until
  it is modelled. Firmware chips that are spent for the fight are not dimmed yet (the wheel view does
  not see per-combat uses): proposed slice, the combat scene passes the spent firmware ids to the
  wheel views beside the satellites.
- **Unified city: real-time 3D or baked layers? (2026-10-05, ART-1 1D):** the spike recommends
  real-time Godot 3D. It is closer to the round 39/40 references and is the only option with the
  continuous zoom and the see-through band, at 2.5–2.8 ms at 1080p on this PC. See
  `docs/handoff/art_1/city_spike_report.md` and the crops in `docs/art_review/ART-1/1D/`.
  - Default: ART-5 builds on (a).
  - Also: the see-through band was moved to lod 1.50–1.595 so that the Grid is solid and the raid
    sits at 0.68. Say if the bible's 1.45–1.75 was meant literally.
  - Tier 1 still needs a measurement on a Steam Deck.

- **ART-2 2C defaults from the round 18 notes (2026-10-05):** (D16, every card-caused effect from
  the card's slap point, is confirmed by the designer and tested.) Defaults applied: an enemy's hit uses its own (attacker's) colour;
  blocked shards that don't get through fall away (not into the guard's number); heal bits come in
  from outside the wheel, not from the heal slice.

- **ART-1 1B: the bits' CPU fallback (2026-10-05):** ART_BIBLE §6.3 names a `CPUParticles2D`
  fallback (<= 44); a CPUParticles2D can't run the Bezier process shader, so the fallback draws the
  same precomputed plan from the emitter node (<= 44 bits, same look and arrival times). Default
  applied; say if a real CPUParticles2D (straight-line flight) is wanted instead.
- **ART-1 1B: "gloss 0.22" (2026-10-05):** read as round 19's `gloss_k` (the specular sheen's
  strength at rest, 1.0 while the one sweep crosses), not the band's position. Default applied.
- **ART-1 1B: the washed system word's alpha (2026-10-05):** round 22 says 30 %; the round 3 kit
  sheet's EXECUTE reads stronger, so `SystemWordSticker.WORD_ALPHA` is 45 %. Say if 30 % is wanted.
- **ART-1 1B: pencil words (2026-10-05):** the references' "HIT IT" is hand-lettered single strokes
  (tg_lib's stroke font); ours is the marker face with the wax grain, written letter by letter.
  A stroke font (true write-on per stroke) can follow if the designer wants it.
- **ART-1 1A: the Daemon family MISS, the PURGE look, the gunmetal (2026-10-05):** ART_BIBLE v2
  §2.6 calls the family that fires on the Miss slice MISS; the slice is NULL since the
  2026-10-05 ruling, so the token and id follow it (`DAEMON_NULL`, `&"null"`). Say if the family
  word should stay MISS. HEAT_PURGE uses HUNTED's colour until the art gives PURGE its own; §2.7's
  "gunmetal" has no value (#3A4048 picked). `Palette.marker()` now returns Anton (Permanent
  Marker is grease pencil only); the screens that still letter in it read as Anton until their
  ART-n restyle.

- **Glyph concept slice after M14 (designer, 2026-10-05, from the two ART-1 1C questions below):** draw
  glyphs for Heat, Cycles, Schematics and custom effects, and redraw the 16 px twins in the Firmware /
  Daemon set; both defaults hold for M14 (pending stand-in; twins allow-listed). Scheduled with the other
  post-M14 concept slice (the Cell's own crest). Also in this slice (orchestrator, 2026-10-05, from ART-6 3A):
  a **Compiler Rack** node glyph: the concept has none, so the raid socket and the YOUR NETWORK mark use
  round 17's `picto_ram` (baked with the other sockets) until the slice draws one.
- ~~**Card pictograms with no glyph yet (2026-10-05, ART-1 1C):**~~ resolved: default (see the glyph concept slice above). Original note: four card effect types have no glyph in
  the bible's set: `effect_modify_heat` (Heat up/down), `effect_gain_cycles` (Cycles),
  `effect_gain_schematics` (Schematics) and `effect_custom` (a custom handler's own effect; the card
  shows its tag). Default: they map to the `pending` stand-in (a neutral rounded square, bible 3.5's
  "rounded square = neutral" badge shape, not new art) in `content/config/glyph_table.tres`, and the cards
  keep their word tags. Say if you want glyphs drawn for Heat, Cycles and Schematics (they would join
  the atlas and the 16 px check).
- ~~**16 px twins in the Firmware / Daemon set (2026-10-05, ART-1 1C):**~~ resolved: default (see the glyph concept slice above). Original note: the 16 px rule (bible 5.2) run over
  the whole atlas (114 glyphs) finds 15 pairs above 0.68 besides the bible's known borderlines
  (CITATION / Phantom 0.69, CLEANSE / BLOCK 0.68). They all involve the round 33/34 Firmware and
  Daemon glyphs or the Ghost core, which were never scored against the round 17 set: Ghost core /
  Shield Cache 0.75, No-damage / Shield Cache 0.72, Bulkhead / Shield Cache 0.72, Respin / Bulkhead 0.71,
  RAM / Bulkhead 0.71, Ghost core / Bulkhead 0.71, CLEANSE / Bulkhead 0.71, Snap / Shield Cache 0.70,
  Respin / Hardened 0.70, Ghost core / Hardened 0.70, Ghost core / RAM 0.70, Corrupt segment / Bulkhead 0.70,
  Ghost core / No-damage 0.69, Barbed Wire / Tracer 0.69, CLEANSE / Hardened 0.68. They are compact
  round or square blobs at 16 px. Default: drawn as the concepts have them and listed in the table's
  `twin_exceptions`, so any new twin fails `test_the_16_px_rule_holds_over_the_whole_atlas`; most
  never share a context (chips, Daemon tiles, card pictos). Say if any should be redrawn.

- ~~**D11 Heat bands: is a fifth band wanted? (2026-10-05, ART-0 B part 2):**~~ resolved: five bands
  (DECISIONS "Designer rulings: SANDBOX / TROJAN / NULL and five Heat bands"; built by B3). Original note: the plan's "old FLAGGED →
  HUNTED, old NOTICED → FLAGGED, new NOTICED = a couple of alarms" comes from the concept rounds
  (DIRECTION_REVIEW round 21: the combat backdrop's intensity dialled down a band). ART_BIBLE v2 §2.8
  and §3.15 already state the result: COOL 0–24, NOTICED 25+ (three alarm beacons on side buildings,
  nothing on the target), FLAGGED 50+, HUNTED 75+, "thresholds unchanged", which is what main's
  Heat poster shows. Adding a NOTICED band below 25 would make five bands and disagree with the
  bible. Default applied: the band names and thresholds stay as the bible has them (no new band, no
  config value); the re-cut is the backdrop's look per band (ART-3 / ART-5). Say if you want the
  five-band version (and its lowest threshold).
- ~~**SANDBOX / TROJAN / NULL (2026-10-05, ART-0 B part 2, D2):**~~ resolved: the designer ruled SANDBOX /
  TROJAN / NULL ("Designer rulings: SANDBOX / TROJAN / NULL and five Heat bands"; built by ART-0 B3;
  struck by the ART-0 audit, B5). Original note: the art pass calls SHIELD, DEPLOY and
  MISS by these program names; the D2 ruling left them unchanged, so the game still shows SHIELD,
  DEPLOY and MISS (SHIELD is also the shield points' word). Default: unchanged until you say.
- **Merge commit `7e569ca` (ART-0 B):** its message keeps git's "# Conflicts:" lines (a merge commit
  cannot be reworded without rewriting the branch). Harmless; noted for the audit.

- ~~**GDD 8.2 "DISPATCH text is … never zine-styled" (2026-10-05, ART-0a):**~~ resolved: the designer took
  the default (2026-10-05); GDD 8.2 reworded citing "Designer ruling: DISPATCH text". Original note: the zine look is
  retired (ruling 4) but this §8 line still names it. Default (applied nowhere yet): read it as
  "DISPATCH text is always a clean CRT terminal feed (red accent, ART_BIBLE v2 §1.2), never a
  sticker or pencil"; reword GDD 8.2 to that if you agree.
- **The Cell's own crest vs the REBEL_CELL corporation (2026-10-05, ruling 6.6):** the art
  direction gives the Cell the fist crest; telling the player's Cell apart from the eventual
  REBEL_CELL corporation (art_asset A2) needs a future concept slice. Scheduled after M14.
- **ANIM-R7 findings and the horizontal list (2026-10-05, rulings 1 and 9):** re-evaluated
  against the ported screens after M14, then fixed (batches A–E re-cut), including the
  overkill wording "→ N LEFT".
- **G1–G16 mechanic proposals (2026-10-05, ruling 8):** re-evaluated with the designer after
  the art integration (plan §3.2).

- **Motion starting values (Animation pass ANIM-1, 2026-09-27):** the 105 entries in
  `content/config/ui_motion.tres` are guesses inside the handoff's ranges. None has been
  reviewed as a frame strip yet. Guesses that matter most: `wheel_spin` 0.45 s per half
  turn with BACK overshoot, `card_play` 0.3 s, `resolve_pass` 0.35 s between passes and
  `number_float` 28 px over 0.6 s. Each will be offered as snappy / heavy / bouncy
  variants when its slice is built.
- **Motion speed and ambience (Animation pass ANIM-1):** answered in ANIM-5 (decided by
  the implementer, as the designer asked): no. The city backdrop keeps its own clock at
  1x / 2x / 4x (sped-up beacons would strobe); the raid layer and the map's route dashes
  run at the chosen speed. See "Animation pass — ANIM-5".
- ~~**Drag and drop, HQ side (Animation pass ANIM-4, 2026-09-27):**~~ resolved: see "Designer rulings on the open questions" (items 5-7). Original note: decided by the
  implementer, confirm in playtest. (1) The pad and keyboard pick-up button is X / Space
  (the `end_turn` action, free on the HQ, the Grid and the raid setup), so A keeps every
  button's meaning; items that only move (crew and swap chips) also pick up with A. (2)
  Recall is a drop on CORE (the Cell's home) on the HQ's CITY GRID monitor. (3) The HQ drags only what HQ rules can
  move; card, Firmware, Daemon and slice moves live in the Modem and loot (ANIM-4b). See
  "Animation pass — ANIM-4".

- **The Grid at text scale 1.6 (H23 city, 2026-09-27):** with the side column and the map key along the map's foot (about 280
  px tall at 1.6), the Grid map is framed small enough that every node shows, and only the
  labels that fit are drawn (the rest keep tooltips); in the densest cluster (ten T1 Sites
  side by side) some icons touch, as the overlay stacks at most ICON_STACK_MAX (4) deep.
  Alternatives: a key that folds to
  its title (open on hover or a button), or a narrower column at big text (the steps as
  icon-only buttons). Which do you prefer? LABEL_REACH (110 px) is a guess too.

- **Subtitles over the stat tags; toasts (H20, 2026-09-26):** outside combat the subtitle
  bar now sits in the top band over the screen title and the stat tags (the only strip
  with no control on any screen), so the tags are hidden while a line is up. Refusals,
  saves and unlocks show as a toast at the foot of the screen for 3.5 s (it lets clicks
  through but can sit over a bottom control for that time). Alternatives: a reserved band
  under the HUD on every screen (costs ~50 px of the screens), or refusals shown on the
  control itself (disabled with the reason in its tooltip). Which do you prefer?

- **Deck / spinner viewers (2026-09-25):** added as look-and-pick views (DeckView,
  SpinnerView), used by the Modem and the HQ crew cards. The GDD has no card upgrades and
  no player rearranging of a wheel, so the viewers show card details and, for slices, the
  stronger same-type slices in the Modem catalogue. Needed from design: do cards upgrade
  (how, where, what changes)? When may a player rearrange slices (HQ only? cost?)?

- **Daily run modifiers (2026-09-25):** the start screen now has a TODAY'S RUN panel with
  room for the day's modifiers (`hq_scene.daily_modifiers`). Today the daily run fixes
  only the seed, so the list reads "none today". What should a day change: a forced
  corporation, ICE rules, a starting-deck or wheel twist, a boost? Needs a config table.

- **Pacing after H15/H16.** With Daemons firing once per landing the bot's Breaker needs
  about 43 runs at ICE 5 (4/8 won), 48 after H17 (3/8), 49 after H18 (2/8), against the GDD 11.8 average of 24. Should enemies
  come down, or Daemons / rewards go up, now that the multi-fire bugs are gone?
- **Rigger at ICE 0 (H15).** With Daemons firing once per Perfect the bot's Rigger wins
  5/8 at ICE 0 in about 36 runs (other classes 6-8/8). Should the Rigger's hub or deck
  get a buff, or is ICE 0 meant to be this hard for it?
- **Final Rack Daemon (H12).** The final Rack offers a card, not a Daemon (a Daemon at
  both Racks made campaigns about three times faster). Should the final Rack get something
  else, such as a rare Daemon on T4 only or an extra Schematics payout? ICE 0 now runs about
  31 runs: is that too long for the entry level?
_(Claude Code: add questions here instead of guessing on design.)_

### From M11, REBEL_CELL (2026-09-24) — decided by the implementer, confirm in playtest
- **REBEL_CELL is hard** (Breaker bot 4/8 at ICE 5, 1/8 at ICE 10). It opens only after
  ICE 10 everywhere, so a human arrives experienced; raise or lower the Mirror factor
  (`config.mirror_output_factor`) after playtests.
- **Custom-handler Daemons** (Kernel Sync, Zero Day...) are not mirrored: their code runs
  on the player's side only.
- **Music** (resolved in H1): each corporation now selects its own contexts.

### From M9, Halcyon Civic (2026-09-24) — decided by the implementer, confirm in playtest
- **Ghost is strongest against the new corporations** (about 10 runs vs 20 for the others);
  Pierce / x2 / Echo plus a full retrigger. Revisit in the horizontal analysis.
- **Halcyon unlock** 140 Schematics (Meridian 120).

### From M8, corporations (2026-09-24) — decided by the implementer, confirm in playtest
- **Meridian vs Solace difficulty**: the bot finds Meridian's ICE 0 about as hard as
  Solace's; as the second corporation it could be harder. The ICE ladder already starts a
  new corporation at (best - 5), which may be enough.
- **Meridian unlock price** 120 Schematics, or should it unlock by beating Solace?
- **Boss stalls**: the bot still reaches the turn cap against The Manifest (Hub Breach and
  Pierce are the counters; the bot does not time them). A soft enrage is an option.
- **Music**: Meridian has no raid music context of its own yet (Solace has solace_raid).

### From M7, pools and Solace depth (2026-09-24) — decided by the implementer, confirm in playtest
- **Solace's key counter is anti-corruption** (Cleanse, Encrypt, Sanitize, Hot Patch). In a
  60-card pool it is offered less often; consider a guaranteed Cleanse-type card in the
  first Modem of a Solace campaign if human players struggle with the boss.
- **Boss stalls**: lower-damage builds still reach the 60-turn cap against the Renewal
  Engine now and then (the bot rarely times Hub Breach). A human can respin or breach; a
  hard turn limit or an enrage is an option if playtests show stalls.
- **Enemy numbers raised** (elites +25% HP, boss 360 HP, damage 1.3 per tier) because the
  smarter bot won too quickly. GDD A.3 still shows the original values with an annotation.

### From M6, the class roster (2026-09-24) — decided by the implementer, confirm in playtest
- **Perfect hooks now carry burst for every class** (Ghost resolves twice; Rigger and
  Botnet again at half). GDD 5.2 listed only the utility part of those hooks. Without the
  burst no class but the Breaker beat the Renewal Engine.
- **Rigger is the fastest class in simulation** (15 runs vs about 25). Trim its Atk 16
  slices if human play agrees.
- **Hook effects repeat per resolution** (inherited from Breaker Mk2): a Rigger Perfect
  refunds RAM twice, a Botnet Perfect Deploy plants two Parasites.
- **Alternatives cost 60** and need no base-class unlock.
- **Freeze cooldown**: a wheel cannot be frozen on consecutive turns.

### From the vertical-completion loop (2026-09-24) — decided by the implementer, confirm in playtest
- **Enemy damage per tier 1.2 instead of 1.6** (HP stays 1.6). Chosen by simulation so a
  greedy bot wins every ICE 0 campaign in about 26 runs; a human with rewind should do
  better. Raise it if playtests find T3/T4 too soft.
- **Patrol runs** exist to prevent a soft-lock; they also let cautious players farm Rank at
  a Heat cost. Cap patrols per campaign if that feels cheap.
- **Late-campaign Schematics surplus**: the bot ends campaigns with 300-700 unspent. Class
  unlocks and more node/boost content (horizontal) are the planned sinks.

### From M1 (2026-09-24) — resolved by the designer on 2026-09-24
- **Flip** is a true mirror, implemented as a rearrangement: slot i's slice (with its
  status and Firmware) moves to slot −i mod n on both rings, docked satellites move with
  their slice, and the rotation is remapped (`r' = −r − 15`) so the tick under the top
  pointer becomes `15 − t` as GDD §2.3 states. Orientation stays clockwise, so nudges and
  spins need no special case; flipping twice restores the wheel. The `flipped` flag is gone
  from WheelState and the GDD code block no longer carries a `+15` term.
- **Breaker slice numbers** Crit 12 / Atk 6 / Def 5 confirmed.
- **Pierce ignores block and shield, not satellites** (GDD §2.7 and §6.4 updated). The
  bodyguard rule applies to piercing hits; the drone takes them.
- **Corrupted self-damage** straight to HP confirmed.
- **DOSE preview** stays hidden from the player (the engine still predicts it exactly).

### From M3 (2026-09-24) — resolved by the designer on 2026-09-24
- **Tier scaling hits everything**, including the final boss (T4 ×4.1) and the new
  **mini-bosses**: every netrun's final Server Rack is guarded by a corporation mini-boss
  (`EnemyData.is_mini_boss`, may have phases). Solace: *Account Manager* (120 HP, Atk 10,
  Def 8, Crit 16, Dose, Shield 5, Miss; resistance 1; at 50% multiplies to two pointers).
  Playtest risk noted: a T4 Renewal Engine Crit is 98 damage against 60 HP operatives.
- **Mid-run raid interludes** are in: whenever a run would return to the map with a raid
  queued, `RunState.Phase.RAID` opens the setup inside the netrun scene (projection, the
  run's own assets and the Armory both deployable, playout). Losing the home server there
  ends the run as ABORTED. Runs that launch with a raid already queued fight it first.
- **Station bonus scaling** (made up): the class `station_bonus` is a DEAL_DAMAGE effect
  whose `multiplier` is the asset damage factor (Breaker 1.5); Rank scales the bonus part
  by `RankRewardData.station_bonus_multiplier` = 1.25 / 1.5 / 2.0 at Ranks 1 / 2 / 3, so a
  Rank 3 Breaker doubles asset damage. It applies to the stationed node and to adjacent
  Firewall Relays.
- **Raid movement details** confirmed as a starting point.
- **Breaker Core Mk2** (Rank 2 Hub upgrade, made up): +2 spin on all cards; Perfect
  resolves the slice twice and refunds 1 RAM per resolution. Operatives fight with the
  highest hub upgrade their Rank has earned (`OperativeState.hub_id`).

### From M2 (2026-09-24) — resolved by the designer on 2026-09-24
- **Shop slice catalogue:** `CampaignConfigData.shop_slices` (Atk 6/8, Crit 12, Def 5/8,
  Shield 5, Evade) with `shop_slice_choices = 3` per Modem; new slices go in the catalogue
  rather than repeating the wheel. Tracked as a horizontal slice in
  `docs/CONTENT_SLICES.md` (new running list: vertical first, horizontal later).
- **Cycles ranges:** implementer's call stands (Router nodes 15–25, elites/Racks 30–40,
  10–20 reserved for non-node fights). Revisit in human playtest.
- **Elite frequency:** node combat type is always known before entering. ELITE_FREQUENCY_PCT
  adds a fraction of an elite per band layer at map generation; when the fraction reaches a
  whole node, one more Router in that layer is flipped to elite (never in place, never after
  the map is shown; each layer keeps a non-elite route). Elite Terminals are a horizontal
  backlog item.
- **Rescued operatives** become a free fresh rookie in the roster (as implemented).

### From M0 (2026-09-24) — resolved by the designer on 2026-09-24
- Godot version → 4.7 pin, GUT 9.7.1. "More elites" → 25% confirmed. ICE 9 → boss
  strength (+25% HP/damage) instead of BOSS_PHASE_EARLY. Minor Heat complications →
  alternate shop stock −1 / elite +25% (implementer's call). RAM cap → 12 (GDD §2.2).
- Still open: **ICE levels 10, 15 and 20** have no listed change; `REPAIR_COST_PCT = 25`
  (ICE 13) and `SEIZED_RAID_STRENGTH_PCT = 25` (ICE 14) are placeholders ("when in doubt,
  up elite and boss numbers" applied); MAJOR-threshold RaidData arrives in M3.
