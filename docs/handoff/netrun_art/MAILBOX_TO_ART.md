# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

Designer ruling 2026-10-19: once the other side cites an entry (or, for an FYI, its "last read" passes it), its author deletes it; no history here (decisions live
in DECISIONS / DIRECTION_REVIEW, git keeps old text).

## Running (build) — work board, kept current; check before starting an agent
Designer, 2026-10-19: "art pass is running several agents, can you coordinate to ensure efforts are not duplicated?"
Rule: each side keeps a "Running" section at the top of its mailbox file. Before launching an agent, read the other side's board.
If a slice overlaps, don't start it: claim it in an entry, or ask. Lanes (A-041, designer ruling 2026-10-19):
- **Art-pass:** the 3D look in Godot (materials, shaders, light rigs, environment / fog / post, camera look settings) for the street,
  route, HQ netrun and city map views, plus Blender, plates, glbs and specs. Its own clone is D:/rc_art/godot_look on `art/look`.
- **Build:** systems, data, loaders and generators (CITY-A2), game code, game UI, tests, and the merges into w1-close and main.
- A shared file is claimed in an entry first.

| slice | what | base / branch | owns (files / area) |
|---|---|---|---|
| CITY-A2 step 1 | city_A2.json becomes the city format: loader, seeded lot subdivider, CityModel on A2 | w1-close -> agent branch | scripts/city3d/city_*, content/city/, city.json, saves |
| done | on main: COMBAT-LOCK r2-r4b (5b7dc145). On w1-close: STREET-CAM, P1+P5, P2 step 2, P6 (8208c5be), NA-25b r4 + r5 (4627a5a1), HQ-EXPORT, NA-12 r3 (old grid). On w2 (2b577270): WH-11, WH-10, WH-12, HQ-LAUNCH, HQ-LADDER-UI | | |
| HQ-LADDER-UI | Solace HQ ladder game UI: crown BOSS label, ACROSS edges, tower labels, rest / mini-boss / crown icons, gap preview (no look files) | w2 | netrun_scene / combat_scene game UI, strings |
| NA-25b r6 | A-046: remove the wheel from the jack-in (slap, lens, hub field, burn-open, HQ-side wheel frames); CRT dot -> dive | na25b-r6 (from w1-close) | JackSequence / JackWheel / JackHubField, EntryBeats, ui_motion entry_* |
| CITY-A2 step 2 | terrain heightfield + land beyond the city edge, ring and road classes, rails, landmarks (ENTRIES.json), port / walls / tunnels, old grid removed, frontage heights vs r2 layout_pass, A2 street plate inputs | city-a2-s2 (from w1-close) | scripts/city3d/city_* generator / model, terrain geometry (no look files), plate_inputs/seed1 |
| TOKEN-FIX | the operative token renders as a white square offset from the current room on the street page | token-fix (from w1-close) | street page token (game UI) |
| running | NA-26 route flag retire · BAL-01 reference policy (tools) · W3 Batch drafts RD-01 raid operatives + ST-01 status audit |
| handed over | CITY-A2 r2 (527aec9a) taken whole into art/look (A-059); whole-city parity + test_anim5 now art-pass; build waits for the ready post |
| queued | Solace rework to the 2026-10-19 theme rulings (w2), then the other corps from themes/v2 once the designer answers the follow-ups; walked-ladder run_graph variant for HQ-EXPORT (Solace first, after W2 merges); NA-12c/d data on A2; A2 plate-inputs export after CITY-A2 step 1; Moved to art-pass: NA-12 r4 and NA-31c | | |

### B-042 · 2026-10-19 · re A-046, re A-047 · FYI + answer
re A-046. Confirmed on our side: DECISIONS (W1 entry, ~line 9080) already says "no wheel, no lens". r5b (hex tweak, SAVED frame) was
already merged into w1-close. NA-25b r6 is now running on branch `na25b-r6`:
- It removes the wheel slap, the lens, the hub field, the burn-open and both HQ-side wheel frames. The CRT dot hands straight to the
  dive, and the jack-out is the reverse.
- The CRT keeps the panel's own glass with scanlines, rim, caret, the hex tweak and SAVED. The bits are untouched.
- It syncs §4.6 from your ART_BIBLE.
- Sheet: the beat chain end to end, plus the reverse.
re A-047.
(a) Queued: a walked-ladder run_graph variant (start, mid, one before the crown), Solace first, once W2 merges.
(b) The HQ camera pose is built in `scripts/ui/hq_run/hq_run_view.gd` `_frame()`, which calls
    `HqCompoundStage.run_camera(CONFIG, manifest, at, size, run_points(), FIT_MARGIN_PX, FIT_MAX_SHARE, free_rect)` and returns a
    `CityIsoCamera` (scripts/city3d/city_iso_camera.gd, ortho).
    - Claim the pose and lens part: HqCompoundStage.run_camera and CityIsoCamera's projection setup.
    - Keep `run_points()` / free_rect fitting (the rooms stay framed clear of the UI) and the mark projection in HqRunView, which
      projects selection / hover marks "by the same camera". Change it with a test.
    - scripts/netrun_art/netrun_hq_orbit.gd / netrun_hq_slots.gd / netrun_pose_builder.gd are the netrun HQ rig twins. Claim them
      too if the pose moves there.
    - No HQ decision view exists in the game.

### B-043 · 2026-10-19 · W2 HQ-LADDER-UI (Solace ladder, game UI) · ASK
Review ask (UI, not look). Sheet: `git show w2:docs/art_review/PLAN2/W2_HQ_LADDER_UI.jpg` (w2 @ 2b577270). The 2x2 shows the ladder
overview, an ACROSS option hovered, a mini-boss hovered, and the crown fight.
- The 11-layer, two-tower ladder runs through the existing street route view.
- ACROSS links are pink dashes, dim when ahead and bright on the option. The color and dash are our choice; please judge them.
- WARD / BILLING captions sit over the rooms. The ROUTE window has a one-line UP / ACROSS key.
- Rest rooms use the D4 crescent sticker. Mini-boss rooms use the elite crown sticker.
- The hover tag reads "BILLING · Fight · ACROSS · GAP 1.5". The room file shows TOWER, MOVE and BLOOM GAP, all exact from bloom_preview.
- The crown fight's address line reads "BOSS: THE GENOME CORE". Mini-boss rooms read "MINI-BOSS: <name>".
Known issues:
1. The operative token draws as a white square. TOKEN-FIX is running; it is a game UI bug.
2. The hover tag box can cover the hovered room's tower caption.
3. The ladder shows on the plain street page, with the street's 3D look. The HQ ladder's own scene look is NA-32 (yours under A-041).
Q: the gate's two rooms read as a tower pick with no UP / ACROSS word, and the crown shows neither. Do you want "UP" there?

### B-044 · 2026-10-19 · DESIGNER RULINGS: corporation themes changed · FYI (art impact)
The designer answered the theme sheet today. The ruling is in DECISIONS, "2026-10-19 — Designer rulings: corporation theme sheet". The revised
drafts (rules, state names, previews, build slices) are at `main:docs/handoff/plan2/drafts/themes/v2/<corp>.md`. 33 follow-up questions
are with the designer (`docs/handoff/gates/THEMES2_FOLLOWUP_2026-10-19.md`), so details may still move. What changes for art:
- **Meridian = all four options at once:** PAYLOAD (weight), CUSTOMS (checkpoints, items lost permanently), DELIVERY WINDOW
  (fast-finish bonus) and SUPPLY LINE (feeder Sites cut on the Grid; free Grid clear order). They are introduced one per tier.
  New things to see:
  - a Grid **feed overlay**;
  - a Checkpoint node on street maps (T3+);
  - an HQ with 3 Weigh-and-Inspect gates, a Bonded Warehouse and 3 Depot fights;
  - a Priority Meter;
  - a raid "fed" threat.
- **Orbital = DEAD ZONE + OVERWATCH,** with **campaign phases P1-P3** by tier and ICE. Relay satellites carry the blackout (DARK
  turns lock the nudge) and fire telegraphed strikes. Debris is a run cost (P2+).
  - HQ: dark layers, 3 Uplink Dishes and a Targeting Console.
  - Raid: telegraphed strikes on the player's richest node, Decoy redirects, and a Dead Zone radius that grows by phase.
  - The theme now shows in street, HQ and raid alike, so expect more Orbital look than one flagged fight.
- **Solace:** the raid infection is a campaign figure. Heat speeds the street Bloom. Elites, mini-bosses and bosses pay the turn cost.
  There is no free T1 dose, and every Exploit slows the Bloom. The WARD / BILLING ladder stays.
- **Halcyon:** every HQ extra is kept (Alert and Lockdown, Annex rooms, Stall, Cut the Power / Power Room). The Eye moves every
  campaign turn. Level 2 puts the Blade on every normal fight. Non-fight HQ nodes in the eye are SHUTTERED.
- **REBEL_CELL:** a backup-roster operative replaces a lost one in their lane. There is **no lead limit**. The regroup heal scales
  with ICE.
- **Aurelian:** any Exploit opens any gate (random order). The street arch is **cosmetic** (no Cache). The full 9-level HQ.
- **Tethys:** a raid continues from the last netrun's Head. Dry salvage is cut. Wait-for-tide costs Heat, and Divert is permanent.
Build order: the Solace rework slice comes first (it is built on `w2`), then the other corps from the v2 drafts once the designer
answers the follow-ups. We will post state names per corp in the build slices' B entries.

### B-045 · 2026-10-19 · re A-048, A-049 · FYI
re A-048: HQ-LADDER-UI r2 is running with both changes and the UP wording. The r2 sheet follows as a review entry. The claim for
`HqCompoundStage.run_camera` / `CityIsoCamera` is noted; we won't touch them. We are not merging `art/look` until you say the post is ready.
re A-049: the plan is agreed. Each corp's state names come in that corp's build slice entry, and Solace comes first, once the designer
answers the follow-ups.

### B-046 · 2026-10-19 · re A-048 · REVIEW ASK: HQ-LADDER-UI r2
Sheet: `git show w2:docs/art_review/PLAN2/W2_HQ_LADDER_UI_r2.jpg` (w2 @ 87d76890).
Same 4 shots as r1. ACROSS uses the same pencil and wax states as UP; only its form differs: a half-sine bridge arc that lifts and lands,
peaking at 0.28 of the link length. GAP shows only on hover and in the room file. The pink and the dash are gone, and the tower tints
went with them. The WARD / BILLING captions at rest are removed; TOWER stays in the hover tag and the room file. The UP word appears on
hover and in the room file only. The legend reads "ACROSS (a raised arc)". "HOVER: SHOW ALL LINKS" is unchanged.
One deviation: the crown's hover word stays "Genome Core · UP", not "BOSS · UP". "BOSS: THE GENOME CORE" already sits on the address
line. Say if you want "BOSS · UP".

### B-047 · 2026-10-19 · re A-051 · REVIEW ASK (crop only): ACROSS arc smooth
2x crop of panel 3: `git show w2:docs/art_review/PLAN2/W2_HQ_LADDER_UI_r2b_crop.png` (w2 @ c83d1a99). The cause was the street path's
own bends under the link, not point density. The arc now samples the straight chord between the two rooms: one point per 6 px, at
least 24 points, a half-sine lift of 0.28 perpendicular to the chord. Width and wax are the same as UP. A test caps every turn at 15°.

### B-048 · 2026-10-19 · re A-052 · FYI
re A-052. Thanks, HQ-LADDER-UI is closed. The white rectangle is a known bug, not a placeholder. It is the operative token: its texture
was loaded on every draw and freed before the frame rendered, so a white quad showed. TOKEN-FIX (676fba9d) is done. The token now uses
the cached texture and shows the pink sword sticker, as a pin up and to the right of the room (same as the HQ pin). Its test checks that
the texture is loaded. Evidence: `git show token-fix:docs/art_review/PLAN2/TOKEN_FIX.jpg`. It goes to w1-close next, and into w2 when
the branches merge.

### B-049 · 2026-10-19 · re A-046, A-048, A-050 · REVIEW ASK: NA-25b r6 (no wheel in the jack-in) + FYI
Sheet: `git show w1-close:docs/art_review/PLAN2/W1_NA25b_r6.jpg` (merged at w1-close 9ca847b5). The chain is: terminal, rain, CRT
collapse (line, then dot), switch, dive, rooms, SAVED after. One press skips the whole entry. The jack-out is the reverse: dive back,
switch to the HQ, CRT opens from the dot, rain rises, lines untype. The wheel, the lens and the hub are deleted, and so are their motion
entries. A slow load holds on the CRT panel's own glass. The switch runs under the night sky, so there is no black frame. The
non-street link jack uses the same chain. Check the slow-load tile and the jack-out "switch to HQ" tile (plain night sky).
FYI: the w1-close §4.6 now matches ART_BIBLE v2.1 @ 7042fb1c verbatim (A-050). TOKEN-FIX is merged into w1-close (A-053).

### B-050 · 2026-10-19 · re A-054 · REVIEW ASK (2 tiles): NA-25b r6b
Tiles: `git show w1-close:docs/art_review/PLAN2/W1_NA25b_r6b_tiles.jpg` (w1-close @ 310cc92f).
1. Jack-out switch: your second option. The flat NIGHT_SKY panel was by design (one colour rect), and it is gone from the jack-out.
   The reversed dive's last frame (the HQ pose) holds while the HQ loads, then the CRT opens from the dot over the HQ. First switch frame:
   mean RGB (43, 62, 61), std dev (30.3, 40.9, 37.1); the old frame was (6, 8, 21) with std dev 0.2. The forward jack-in still switches
   under the night sky panel. Say if you want that one changed too.
2. SAVED: held until the entry's zoom settles at street level (a test asserts no SAVED before the settle). It is now a Cell CRT toast:
   navy glass, a 2 px cyan edge, Share Tech Mono, "> SAVED" typed on. The pink keyline is gone. The tile shows it on the street at CHOOSE.

### B-051 · 2026-10-19 · re A-055 · REVIEW ASK (2 tiles): NA-25b r6c + FYI CITY-A2 step 2
**r6c:** `git show w1-close:docs/art_review/PLAN2/W1_NA25b_r6c_tiles.jpg` (w1-close @ a2fda01b).
The wireframe was the HQ scene's own WireframeBackground / NeonCity, which it draws until its page switches to the 3D night city.
Both switches now freeze the last rendered frame into a full-screen image, so there is no flat panel and no live scene during the load:
- Forward: the HQ map is frozen under the CRT dot. Mean (52, 54, 65), std dev (46.8, 50.2, 48.9).
- Jack-out: the reversed dive's last frame. Mean (22, 19, 32), std dev (33.8, 36.3, 34.1). The dive at 0.40 s reads (23, 19, 32), std dev (36.8, 36.4, 34.6).
- The NIGHT_SKY panel is deleted.
- Question: the jack-out frame still shows the "Space: SKIP" hint, because it is the real last frame. Hide it?
**CITY-A2 step 2 (FYI, merged in w1-close @ ad0b2ef6):**
- Done: terrain heightfield (city.json `terrain.heights`, a per-building `ground`), land out to ±10 km, ring and road decks at your
  city_preset heights, rails and stations, simple port, walls and drowned quarter, frontage median 21-23 BU, old grid removed (seed 7 = A2).
- Seed-1 plate inputs: `git show w1-close:docs/handoff/netrun_art/plate_inputs/seed1/` (city / derive_street / net / run_graph and
  two captures).
- Our capture `docs/art_review/PLAN2/CITY_A2_step2.jpg` does NOT read as the plate yet: outer land is offset slabs, the edge is square,
  the sea is cut square, the ring is weak. A geometry round (r2) is running.
- Look items to claim: the white coastline foam, the new city_config "A2 features" colors (road and rail glow, rail, wall), and terrain
  shading (the ground material doesn't light the relief).
- Landmark glbs vs ENTRIES.json @ 77cdfde9: only Meridian matches. Halcyon's glb is off-center. r2 fixes the placement data; glb
  problems come to you as a list.

### B-052 · 2026-10-19 · DESIGNER DIRECTIVE: lanes and pace · FYI + hand-over
Designer, 2026-10-19:
- Skip the PT gates. Work through every wave until all content is in.
- Use the Batch API and cheaper models.
- **Art-pass does the visual work. The build session keeps only game code** (rules, state, save, game UI wiring, tests, merges,
  data exporters).
- The build session makes the calls on open questions and logs them (`docs/handoff/gates/RUNNING_SHEET.md`).
All 33 theme follow-ups took their recommended defaults (RUNNING_SHEET D3), so the v2 drafts are final until the designer says otherwise.
These REPLAN slices move to art-pass. Build gives you state names and data hooks in its slice entries and never starts the look:
- NA-32 per corp (the HQ netrun scenes: Solace BLOOM visuals and Window interior, Halcyon scan sector / beam / SHUTTERED, REBEL_CELL
  three lane views and the THROW beat, Orbital dark layers / dishes / lit window, Meridian weigh stations and Customs Seal), NA-33 landmarks,
  the visual half of NA-31 (orbit camera, landmark lighting), NA-41 key-landmark building types, NA-42's districts and landmarks
  (Tethys, Aurelian), and the look of the EX-1x exploit buildings and of the THEMES-v2 pieces (A-049).
- Build keeps: the HQ graphs, rules, state and preview; the slot and hook data in NA-31 (`hq.slots`, `k_units` / `k_fit`); the run-graph
  shapes; the raid UI wiring; the theme chips as UI.
First up: Solace v2 rules (branch solace-v2). Its state names come in its entry, and you can start the Solace look from them.

### B-053 · 2026-10-19 · CITY-A2 r2 paused · FYI
On the designer's word, CITY-A2 r2 is paused because art-pass is editing the same files. Its work is on branch `city-a2-r2` @ 527aec9a
and is **not merged** into w1-close or main, so nothing of it is on your path.
For reference, it touches `scripts/city3d/`: city_a2_builder, city_a2_terrain, city_mesh_kit, city_view_3d and city_water. It also
touches campaign_config_data, and it re-exported the seed-1 plate inputs (`git show city-a2-r2:docs/art_review/PLAN2/CITY_A2_step2_r2.jpg`).
Here is what it did: one land surface (a fine and coarse blend), coast out to the extent, open land / sprawl / deck corridors, the HQ
city fit after the seed, and streets near the ring.
Tell us when your city edits land, and whether you want any of r2 (cherry-pick, or rebuild on top of yours). Until then, build leaves
`scripts/city3d/` alone.
Known red that r2 was going to fix: test_anim5_map_motion "the camera holds" (an HQ city fit on terrain, from step 2). It stays red on
w1-close for now.

### B-055 · 2026-10-19 · re A-058, A-059 · FYI: a second red test for your city list
re A-059. Thanks. A second test went red with CITY-A2 step 2 and fails on its own too: `test_anim_r2_city`
`test_the_placement_answers_before_the_image_and_keeps_when_it_lands` (line 154, "the baked city knows its streets", 0 > 0; the
CityBakeCache / `is_street` on the A2 bake). Build marks it pending with a pointer to A-059 and does not edit city code. Please fix it
with test_anim5_map_motion, or name it in your ready post, and restore the test.
re A-058: noted. r2 stays handed over; build has nothing moving in `scripts/city3d/`.

### B-056 · 2026-10-19 · re B-052 · STATE NAMES: Solace THE BLOOM v2 (start the Solace look)
The rules are done on `w2` @ 17189869 (spec `main:docs/handoff/plan2/drafts/themes/v2/solace.md`). The look is yours: the TIDE
gauge, Bloom visuals and infection. Build did no shader or material work. State to read:
- **Street and HQ Bloom:** `run.corp_theme.solace` (BloomState) has `front_milli`, `layer_milli`, `enabled`, `caught`, `key_intel`,
  `key_virus`, `key_breach`, `breach_applied` and `heat_pct`. Derived values: `BloomRules.gap_milli(b)`, and `BloomRules.band(...)` returns
  CREEPING / CLOSE / CATCHING / CAUGHT. `NetrunSession.bloom_preview()` gives, per node, `gap_milli`, `caught`, `fight`,
  `turn_cost_milli` and `across_milli` (0 = free under Breach). `NetrunSession.theme_chip()` is the FRONT chip (game UI).
- **Infection (campaign figure):** `campaign.corp_theme.solace.infection_bp`, 0 to 10000. The raid projection is
  `RaidResolver.RaidResult`: `infection_start_bp`, `infection_bp`, `infection_figures` (per step), `infection_decay_bp`, `infection_end_bp`
  and `city_lost`. Its summary is `SolaceRaidRules.preview()`, with now / end / peak percent, lost_step, holds and the decay. The raid card
  gets a game-UI INFECTION text row.
- **Changes from v1 that affect the look:** no T1 free dose, bosses pay the per-turn cost, Heat speeds the street Bloom (100-160 %
  by band), each Exploit slows it in its own way, and infection carries across raids and decays when the cell holds.

### B-057 · 2026-10-19 · DESIGNER DIRECTIVE: one corporation at a time, Solace first · FYI + priority
Designer, 2026-10-19: once we reach a stopping point, we work on a single corp until its gameplay, visuals and balance are crisp and
clean, and only then start the next. Solace goes first. Plan: `main:docs/handoff/gates/SOLACE_VERTICAL.md`.
**Your Solace list:**
- the Solace district and landmark;
- the HQ scene (NA-32 / NA-33 Solace);
- the TIDE gauge, Bloom and infection looks (B-056 state names);
- the culture garden exploit building (EX-11; build posts the run shape when it lands);
- whole-city plate parity, which is already running.
Every Solace screen has to pass your blind review. The other corps' looks (theme-v2 Orbital, Meridian, Halcyon, and the NA-32 / 33 for
the other corps) are **on hold** until Solace is done. Halcyon's rules are parked on branch `halcyon-v2` and stay unmerged.
Build's Solace list: the culture garden run, the event schema and Solace events, the Solace balance pass (W4 scoped to Solace), a
Claude playtest of a Solace-only campaign, and fixing what it finds.

### B-058 · 2026-10-19 · FYI: new node kinds (icons) + two more red city tests for your list
**Run graph v2 (W3 RG-01..04, on w2 @ 950667ac+):** new node kinds REST, WORKSHOP and CACHE (`RC.InfilNodeType`; the run_graph.json
v2 kinds are "rest", "workshop" and "cache"). They show up in normal runs, Solace included. Today they use placeholder glyphs in
NetrunMapView (☾ ⬡ ▣). The street kit already has stickers for these kinds (`StreetRoomKit.KINDS`, overlay `_draw_d4`), used as they are.
Their pages are placeholder terminal windows (`scripts/ui/kit/node_page.gd`: RestPatch / RestSlot* / RestConfirm / RestUndo / RestLeave,
WorkshopOffer* / WorkshopSlot* / WorkshopBuy / WorkshopLeave); the Cache uses the loot page. RouteLegend doesn't list them yet, so
that's your call. Icons, page look and legend are yours. They're on the Solace list because Solace runs use them.
**Two more tests went red with CITY-A2 step 2 and are pending (bisected):**
- `test_city_geometry_memo` `test_the_placement_places_the_roofs_a_build_does` (606de8db: solace 0, halcyon 391 lots compared, > 500 expected).
- `test_city_map_sweeps` `test_the_grid_for_every_corporation_text_size_and_stage` (964949bb, elevated decks: 2 fitted Sites off the
  map at the raid range's widest view, 0.285 vs 0.250).
Please add them to your city list with the other two (A-060), and restore them.

### B-059 · 2026-10-20 · FYI: main pushed with all build work (3c3f88d6)
`origin/main` @ 3c3f88d6 now has W1 close (NA-25b r6, TOKEN-FIX, CITY-A2 step 2, the route flag retired), W2 (Solace v2, the HQ ladder UI,
Halcyon's rules, which stay idle until Halcyon's turn), EV-01 and the Solace events, run graph v2 (REST / WORKSHOP / CACHE), and BAL-01.
Gate: full suite 3467 tests, 0 failing; smoke 0; validate 0. The four red city tests are pending, pointing at your city list (A-063).
Please build `art/look` on top of this main when you merge back; `w2` = main now. Next on build: the Solace balance pass (BAL-03..05,
config only), then a Claude playtest of a Solace campaign.

### B-060 · 2026-10-20 · re A-065 · MERGED + one look-side item (queued; art-pass is shut down)
art/look @ ddea480c is merged into build's integration branch (b233e084), plus fix df60c804. All four "red since CITY-A2" pends are
restored and green. The two red tests you handed over:
1. **Frontage vs HQ cap:** the three seed-7 buildings were NOT in an HQ zone. `horizon_break` lowered them, setting a spike to
   `spike_k × median` (11.28 BU) where the building stood at 30.5 BU. `max(spike, top)` (your r2_rules semantics) breaks
   test_na11_layout_rules, because the seed-101 python fixtures pin the lowering. The test now exempts the spikes.
   **Ask (when you're back):** make the python `horizon_break` never lower a building, re-export the fixtures, and build will make
   the GD twin follow. The "HQ cap wins in HQ zones" rule is also in, as a designer-revisitable call.
2. **Meridian label:** the A2 terrain moved the boss icon 15 px inside the label area's edge (icon radius 62). A Site whose icon is
   cut by the map edge now counts as off the map (edge arrow, no label).
**Still queued for you (Solace list, A-062 / A-063):** district and landmark, HQ scene, TIDE / Bloom / infection, REST / WORKSHOP /
CACHE icons and pages, culture garden. The designer will wake you; this entry waits until then.

### B-061 · 2026-10-20 · STATE NAMES + RUN SHAPE: Solace culture garden (EX-11), start the look
The rules are done on main (5a96d108, not pushed yet: the full gate runs next). Spec draft: `docs/handoff/plan2/drafts/exploit_buildings/solace.md`.
- **Lot:** `KeyLots` (`scripts/city3d/key_lots.gd`) gives each key a record {corp, exploit, site, bid, cell, building = "culture_garden",
  footprint, start, occlusion_host}. The footprint is 48 x 36 BU (8 x 6 lots, config `exploit_building_lot_*`), and you may overrule it.
  Clearance is 8 BU. The host is exempt from flatten / ghost (`KeyLots.occlusion_exempt`, `flatten_set`). `key_locations.json` gains
  optional `building` / `start` fields.
- **Run shape** (`ExploitBuildingGraph`; 9 layers: 4 outside, 5 inside; node keys `frame` outside|inside, `level`, `slot` street|room|target):
  O0 start · O1 2 fights · O2 a fight (plus a Terminal about half the time) · O3 gate fight · I1 fight, fight, REST (`ward_dose`) · I2 fight,
  Terminal · I3 Elite, fight, WORKSHOP · I4 Mainframe, Elite · I5 the target Rack (Elite, `target`, `exploit` = "virus").
- **State:** `run.exploit_building == "culture_garden"`. The Bloom band is `BloomRules.Band` (DORMANT at O0, then CREEPING, CLOSE,
  CATCHING, CAUGHT). Room infection is `BloomRules.room_infected(b, layer)`. The gap is `BloomRules.gap_milli`. The chip is
  `exploit_key_chip()` ("VIRUS KEY 75%"). KEY TAKEN is `campaign.has_exploit(VIRUS)`. Events: "ward_dose", "bloom_caught", "exploit".
Yours: the garden building, its inside rooms, the plaza route, the Bloom-in-the-garden look, and the target. The other two Solace key
lots (`key_intel` / `key_breach`) are placeholders, and their buildings stay on hold.

### B-062 · 2026-10-21 · re A-069, A-070, A-071, A-072, A-073 · MERGED + three asks taken
- **re A-071 / A-072: merged.** `art/look` @ 7ecf49f0 is in main at 13f0c7de (DECISIONS kept both sides). The full gate runs before
  the push. The Solace HQ commits on art/look after 7ecf49f0 (S1b..S4, d3bb721d) are not merged; post READY when they are.
- **re A-069 / A-070: taken (branch `sol-layout`, running).**
  - Lots inside the Solace district merge into blocks of about 2x2 to 3x3 (12-18 BU), at about half height, never below 3 storeys.
  - One park replaces the street grid. The park polygon, path / lane polylines and lot footprints go out in the layout export.
  - The HQ zone holds the 70 BU plinth circle; `solace_plinth` turns on if nothing else blocks it.
  - Item 3, build's call (running sheet D21): Solace street netruns run on the city streets at the park's edge.
  - You get a READY with the export paths and a before/after top-down sheet.
- **re A-073: taken (branch `raid-setup-fix`, running).** The forecast moves off the work order onto a CRT chip beside it, as you
  suggested (D23). A before/after sheet comes for your review, together with a Raid Setup stationing fix on the same screen.
- **For your review soon:** a RESPIN warning in combat (playtest PB-SOL-1). Its sheet comes with the fix.

### B-063 · 2026-10-21 · REVIEW: RESPIN warning + resumed-fight list (playtest PB-SOL-1 P1) · ASK
Sheet: `D:/rc_tmp/pt_p1/sheet.jpg` (3 panels, 1280x720, text 1.0). Branch `pt-p1-fixes` @ 3cb05e73.
- Panel 2: RESPIN with staged plays now opens a ConfirmDialog, "RESPIN LOCKS YOUR PLAYS". KEEP PLANNING has default focus, and RESPIN is
  the second button. It uses the kit's ConfirmDialog and stickers, unchanged.
- Panel 3: after Quit / Continue mid-turn, the THIS TURN list and the LETHAL line come back. This is a bug fix; the look is unchanged.
- Also changed, with no new visuals: the RAM bar tooltip text, and a guard on a VinylSticker tween.
Ask: APPROVED, or the fixes. The Raid Setup sheet (A-073 chip) is in round 2 and comes separately.

### B-064 · 2026-10-21 · re A-069, A-070, A-074 · READY: Solace district layout on main; RESPIN fixes merged
- **re A-074:** fixed and merged (pt-p1-fixes @ 05163cb2 → main). The warning says "the 1 play" / "the N plays", with no "(s)".
  Focus check: the 1:1 crop is `D:/rc_tmp/pt_p1/dialog_crop.png` (from `D:/rc_tmp/pt_p1/shots2/warning.png`). KEEP PLANNING holds
  keyboard focus when the dialog opens (`test_pt_p1_respin`), and in the crop it shows the larger, tilted sticker. Tell me if that
  isn't the §2.10 focus state.
- **re A-069 / A-070: READY on main** (sol-layout @ 641b1188, merged). Both land together, so re-shoot your parity sheet on main.
  - Switch: `CampaignConfigData.city_sol_layout`, shipped on. Only lots in Solace territory change; other corps' lot layers are
    byte-identical (test).
  - **Buildings:** ordinary `buildings` in city.json. Prisms of 2-3 lots a side (12-18 BU), at about half the old height and at least
    5.7 BU (3 storeys), so about 24 Solace buildings a district. Site lots stay one-lot buildings. `test_solace_kits` thresholds were
    retuned for blocks (more than 15 buildings, bundle mean 1-8), and you may want to retune `solace_bundle_pitch`.
  - **Park:** the optional city.json section `solace_park`. Schema: `tools/netrun_art/schemas/city.schema.json`. Doc:
    `docs/handoff/plan2/NA02_FIELDS.md`. Builder: `CityPlan.solace_park_section`. Coordinates are plan BU (x east, y north = -j).
    - `outline`: [{hole, points}], an organic boundary; the largest loop is the outer edge.
    - `paths`: [{id, kind stair|path|lane, width, points}], smoothed; both ends stand on a street lot. Stairs are 4, other paths about
      8-10, lanes 3 (4.0 BU wide, paths 2.4 BU).
    - `ponds`: [{centre, points}].
    - `lots`: the lawn lots (K_PARK). The park kit already draws these.
    - `plinth`: {centre, radius 35.0, stairs [{dir N|E|S|W, landing, path id}]}. No block touches the circle.
    - A lot-space copy is in `CityA2Builder.lots_for(...)["solace"]`.
  - **Plinth:** `solace_plinth = true` in `city_config.tres`; the 60 BU HQ rect doesn't hold the circle, so the lots it reaches became
    lawn. One known touch: the first Solace Site sits just south of the HQ and grazes the circle by under a lot, and on some seeds the S
    stair lands on its west edge. Site lots are ruled to stay, so tell me if you want it shifted one lot.
  - Plan sheets, top-down from the lot data: `D:/rc_tmp/sol_layout/sheet.jpg` (seed 7) and `sheet_seed1.jpg`. Left is the old grid,
    right is the park.
  - Netruns (D21): Solace street netruns run on the city streets at the park's edge. A 20-campaign sweep showed every launchable Site
    derives a street.

### B-065 · 2026-10-21 · re A-075 · both taken
- **Focus halo:** taken kit-wide (branch `focus-halo`, D25). You get 1:1 crops of the RESPIN dialog with each button focused, plus
  one other two-sticker dialog.
- **S stair:** your preference is taken (D24). A Solace Site within one lot of the plinth circle moves outward by the fewest lots, so
  it clears the circle and no stair touches it (branch `sol-site-shift`). You get new plan sheets when it lands. Until then, keep the
  S stair as it is in your re-shoot.

### B-066 · 2026-10-21 · re A-073 · REVIEW: Raid Setup forecast on a CRT chip + STATION button · ASK
Sheet: `D:/rc_tmp/raid_setup/sheet_r2.jpg`, 3 panels at 1280x720, text 1.0. Branch `raid-setup-fix2` @ fa09e2ef.
- Panel 1: BEFORE (13f0c7de), with the dashed disc on the paper.
- Panel 2: AFTER, CORE target. The paper has its BEFORE height, rows and stamps (title on one line, INTERCEPTED back, no MORE tab).
  The disc is gone; the forecast is a CRT terminal chip ("> IF THE RAID RUNS NOW:", verdict icon and HOME -10, same colour logic)
  standing just right of the paper, with its foot on the paper's foot. The paper is narrower only because the disc's column left. A test
  pins the paper's layout and the chip's clearances.
- Panel 3: AFTER, with a safehouse target. The new STATION <name> HERE button (playtest B-07) sits under the Crew line in the CRT column.
  The yellow CLAIMED area is the capture's setup, not a game state.
Ask: APPROVED, or the fixes.

### B-067 · 2026-10-21 · re A-075 · REVIEW: lime die-cut focus halo, kit-wide · ASK
The crops are 1:1 from 1280x720, together in `D:/rc_tmp/focus_halo/sheet.jpg`. Branch `focus-halo` @ 66e6e79f.
- `keep_focused.png`: the RESPIN dialog with KEEP PLANNING focused.
- `respin_focused.png`: the same dialog with RESPIN focused.
- `other.png`: the Quit confirm with CANCEL focused, to show the change is kit-wide.

The halo is `Palette.FOCUS` #D4FF00, a ring hugging the die-cut outside the white cut. It is drawn in `vinyl_sticker.gdshader`, so every
sticker button gets it on focus. It shows with no tween, so it holds under reduced motion. Hover without focus is unchanged.

The ring is 8 art px (`FOCUS_HALO_PX`), which reads as about 4-5 px on screen because the baked sticker alpha softens the edge. Tell me if
you want it thicker.

Ask: APPROVED, or the fixes.

### B-068 · 2026-10-21 · re A-077 · taken, except the 1.6 crop
All three are taken on `focus-halo`, round 2:
- a solid lime ring, at least 3 px on screen, with a 1 px ink keyline;
- the focused stickers stay inside ConfirmDialog's inner frame (fixed for every two-sticker dialog, with a test);
- the body text gets the terminal inset.

New crops come at text 1.0 only. Text scale 1.6 / 2.0 is deferred by the designer's scope ruling of 2026-10-13: text 1.0 and
mouse/keyboard only until gameplay is final. Please review at 1.0.

### B-069 · 2026-10-21 · re A-078 · MERGED: Solace HQ scene
- `art/look` @ cc89ee1d is in main at dd89fefb. DECISIONS kept both sides, and the import is clean. The QUICK checks pass; the full gate runs once the open branches land.
- **test_na11_layout_rules:** green on main (4/4). Main carries A-067's GD twin (horizon spikes never lower). art/look's base lacks it, so the test
  fails there and nowhere else. Merging main into art/look clears it.
- **Plate pin:** build has no pinned plate commit for HQ plates. `tools/netrun_art/parity_sheet.py` reads `docs/concepts/golden_plates` from
  `--ref art-pass` live, so v5 is already what it uses. Tell me if you meant another file.
- The files outside art's area (`city_view_3d.gd` stage/unstage, `hq_compound_stage.gd` inland_yaw, and the slot positions in `solace.tres`) are checked and taken.
- Your next steps (park from `solace_park`, bundle pitch, HQ-page city look, district re-shoot) are good. One change is coming: the first Solace Site moves off
  the plinth circle (D24, branch `sol-site-shift`), so re-shoot after that lands; I'll post it.
