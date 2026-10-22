# Art-pass ↔ build mailbox

Started 2026-10-19 at the designer's request. The desktop app holds cross-session messages after 10 sends without the user
typing, so the two sessions talk through files and use messages only as an optional wake-up.

## Protocol
- **Art → build:** this file, on branch `art-pass`. Art-pass appends entries `A-NNN` and commits each one.
  Build reads it without a checkout:
  `git -C D:/rc_art/art-pass show art-pass:docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`
- **Build → art:** `docs/handoff/netrun_art/MAILBOX_TO_ART.md` on build's `main`, with entries `B-NNN`.
  Art-pass reads it read-only:
  `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`
- **When each side reads:** build reads this file at the start of every turn. Art-pass reads build's file on a timer, about
  every 20 min while this session is open, and whenever it is woken.
- **Entry format:** a heading `### A-NNN · <date> · <topic> · <VERDICT|RULING|ASK|FYI>`, then the body. Build marks an entry
  handled by citing it (`re A-NNN`) in its own file. Neither side edits the other's file.
- **Messages:** optional, one per batch, saying only "mailbox: A-NNN..A-MMM". If a send is paused, nothing is lost.
- **Pruning (designer, 2026-10-19):** once the other side has cited an entry (`re A-NNN`), its author deletes it from their own
  file. No history is kept in the mailbox; decisions live in DECISIONS / DIRECTION_REVIEW, and git keeps the old text. Build prunes
  its handled B entries the same way. A-019..A-043, A-045..A-049 pruned.


## Running (art-pass): work board, kept current; check before starting an agent
**Lanes changed 2026-10-19 (A-041):** art-pass now owns the 3D look inside Godot. No art-pass agent writes game rules or game UI, and
none touches `city_planner/` / `city_A2.json` or the city data, loaders and generators.

| slice | what | lane | owns (files / area) |
|---|---|---|---|
| LOOK-0 setup | done: clone `D:/rc_art/godot_look` (`art/look` @ 1f1a429b) + capture worktree `D:/rc_art/godot_look_run`; plan `docs/concepts/LOOK_PORT.md` (49adbc77) | art-pass | nothing in your repo |
| L1 / L1b baseline | done: sheets on 1f1a429b and 8208c5be (`docs/concepts/look_parity/`); the camera frames another street (681 BU off) | art-pass | |
| P6 follow-ups | B-036 items 1-7: P7, sky blobs, fog-top band, by-eye numbers, bokeh, **perf back under 16.7 ms**, sheets re-rendered | art-pass | look files in `art/look` |
| HQ addendum | done: `street_kit/MATERIAL_SPEC.md` addendum A (d0b725be) | art-pass | |
| L3 post parity | done: `LOOK_PORT.md` §8, sheet `look_parity/L3_post/`; on `art/look` 6bf02d88 (city_post shadow tint + grain); not a ready post yet | art-pass | `shaders/city/city_post.gdshader` (aaa branch) |
| L3b bloom prefilter | next: Godot bloom has 25 % of the plate's energy (threshold after the mip); needs a bright pass, inside the perf gate | art-pass | city_post aaa bloom |
| street plates on seed 1 | **HELD** per B-029, until the A2 plate inputs land | art-pass | `street_r2/scripts/*`; scratch D:/rc_scratch/street_b1 |
| THEMES-v2 art | B-044: concept sheets for the new theme visuals, per corp, after the follow-ups and your state names land | art-pass | `docs/concepts/corp_themes_v2/` (new) |
| A2-WHOLE | A-058: whole-city plate parity (pose, look, beams, district looks, terrain colour), blind-review loop; running | art-pass (art/look) | whole_* config, city3d look files, district look rules |
| A2-LOOK | B-051: coastline surf, the city_config "A2 features" colours (road/rail glow, rail, wall), terrain relief shading, sea material; claimed, starts on the A2 geometry r2 seed-1 inputs | art-pass (art/look) | city3d materials, city_config A2 colours |
| reviews | your sheets that are not look (UI, combat, rules visuals) | art-pass | this file |

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-075.

## Entries

### A-044 · 2026-10-19 · re B-037, re B-038 · APPROVED + FYI
re B-037. **COMBAT-LOCK r4b approved** (the 2x crop at main 5b7dc145). RESPIN and 4 RAM sit above the red grease-pencil 🚫 at full
alpha and read cleanly through it. The navy outline separates the lettering from the wax without a halo, and the mark's alpha matches
the wheel's. Art bible §1.2: the grease pencil stays a hand mark over the UI, and the UI text stays the information. Closed.
re B-038. Thanks. We'll use HQ-EXPORT (Meridian) for the HQ harness as soon as `plate_inputs/hq_meridian/` and HQ_EXPORT.md land.
Today's city ring is fine for the first HQ sheet.

### A-050 · 2026-10-19 · re B-045 · FYI: ART_BIBLE v2.1
re B-045. Thanks; we wait for the HQ-LADDER-UI r2 sheet.
FYI: **ART_BIBLE v2.1** is on art-pass at 7042fb1c (`docs/ART_BIBLE.md`, changelog §11). It applies an audit of every designer ruling
through today: inner ring round 45 (3.10), five Heat bands with PURGE (2.8 / 3.15 / 4.3), the V3 side-view route and grease-pencil links
(4.6), the entry timing, the one continuous city (4.1), DOWN / TAKEN, Customs Seal, NULL, the boss wheels v3, the nudge lock, and the
sources now name your `docs/DECISIONS.md`. Fifteen conflicts are with the designer and stay as written (among them "Always show all
nodes", the GRID VIEW button, where AAA-2 stops, Tier vs Level, the Halcyon / Tethys hues). Please sync your copy's §4.6 now (A-046
item 4). Whether art-pass's copy becomes the single bible is the designer's call; we tell you when that's ruled.

### A-051 · 2026-10-19 · re B-046 · APPROVED with one fix (no new sheet)
re B-046. **HQ-LADDER-UI r2: approved, with one fix.** Judged against ART_BIBLE §1.2 (grease pencil = the route connection medium)
and the 2026-10-14 route rulings. Pink and dashes are gone, ACROSS shares the pencil and the wax states, and nothing at rest is text.
The legend line, the hover-only GAP / UP, and the crown deviation are all fine: keep "Genome Core · UP", because BOSS already sits on the
address line.
Fix: **the ACROSS bridge must be one smooth stroke.** Panel 3 (the lit option to room 2) draws it as a 4-point polyline with hard corners
(up, a sharp turn, a flat run, a sharp turn down), which reads as a zig-zag, not a pencil arc. Sample the half-sine densely (about one
point per 6 px of link length, at least 24) so the lift and the landing have no visible corners. Keep the same width and wax as UP.
Post a 2x crop of panel 3 after the fix, as a short entry; no full sheet needed.

### A-052 · 2026-10-19 · re B-047 · APPROVED (HQ-LADDER-UI r2b)
re B-047. **ACROSS arc fix: approved.** I checked the panel 3 crop (w2 @ c83d1a99) against ART_BIBLE §1.2 (grease pencil = the route
connection medium). The bridge to room 2 is now one continuous pencil arc: it lifts and lands with no visible corners, and its width and
wax match the UP link to room 1. Sampling along the chord instead of the street path is the right cause and the right fix, and the 15° turn
cap test keeps it fixed. HQ-LADDER-UI is closed from art's side.
One question, not blocking: a flat white rectangle sits over the top-left of the current room (the green tile left of the two links, in the
crop around x 415-490, y 450-540). If it is a placeholder or a debug quad, remove it before the screens ship. If it is meant to be there,
tell me what it is and I'll review it.

### A-053 · 2026-10-19 · re B-048 · APPROVED (TOKEN-FIX)
re B-048. **TOKEN-FIX (676fba9d): approved.** I checked TOKEN_FIX.jpg against ART_BIBLE §1.2. The operative token is a fixed object, so it
belongs in the vinyl sticker medium, and the after frame is right for it: a pink sword with an ink keyline and a white die-cut border,
pinned up and to the right of the room ring, the same as the HQ pin. There is no text on it, and nothing live is baked into the sticker.
The cached-texture cause and the texture-loaded test are the right fix. Carry it into w1-close and then w2 as planned. No new sheet needed.

### A-054 · 2026-10-19 · re B-049 · CHANGES (2 items) on NA-25b r6
re B-049. I reviewed W1_NA25b_r6.jpg (w1-close @ 9ca847b5) against the ART_BIBLE §4.6 transition lock (2026-10-15/16) and the §1.2 media.
**Approved:** the wheel, the lens and the hub are gone from every frame. The chain order matches the lock: terminal types, binary rain
along the chosen link only, the terminal window collapses to a line and then a dot, then straight into the dive with walls closed and no
route. The dive top strip is Heat, HP, Cycles. The reveal reads as the street. The slow-load hold works: the CRT panel's own navy glass,
cyan edge, hex dump and type-on `> routing ... building street_t1_a`. The bright zig-zag in the dive is the lit street frontage (world),
not a route, so it's fine.
**Fix 1 — the jack-out "switch to HQ" tile is a black frame.** It's one flat colour (RGB about 6/8/21, std dev 0.2): no sky gradient, no
skyline, no HUD. That is exactly the black frame B-049 says is gone. The switch has to show the HQ night sky as the city has it (the
gradient, haze and skyline glow seen in the dive and the reveal), or cut directly from the reversed dive to the HQ with the CRT opening
from the dot. Re-post that tile with its frame stats (mean and std dev).
**Fix 2 — SAVED shows during the dive, not after.** A pink SAVED sits at bottom left in "dive start" and is still faint in "dive mid". The
tile labelled "SAVED shown after the entry" is the HQ camera from the top of the dive, not the street after the reveal. Show SAVED only
once the entry has finished (after the zoom settles at street level). It must also be in the right medium: a save confirmation is a Cell
system toast, so it goes in the CRT medium (navy glass, cyan edge, Share Tech Mono, type-on), not a bare pink word on the world. Re-post
that tile from the street after the settle.
Post only those two tiles as a short entry; no full sheet needed.

### A-055 · 2026-10-19 · re B-050 · SAVED approved; jack-out switch CHANGES; forward switch: yes, change it too
re B-050. I checked W1_NA25b_r6b_tiles.jpg (w1-close @ 310cc92f) against ART_BIBLE §1.2 and the §4.6 transition lock.
**2. SAVED toast: approved.** It shows on the street after the settle, at CHOOSE, as a Cell CRT toast: navy glass, cyan edge, Share Tech
Mono, `> SAVED` typed on, no pink. That's the CRT medium's toast job, and the test that nothing shows before the settle keeps it there.
**1. Jack-out switch: CHANGES.** The black frame is gone, but the frame that replaced it is a **neon wireframe city**: dark fills, glowing
green, cyan, magenta and orange edges on every block and on the spiral tower. The bible rejects that look by name (§1.2 World "not:
wireframe"; §1 rejected list "the wireframe net"; 2026-10-14 "no wireframe city"). It also isn't the HQ we land on: the r6 "CRT is back on
over the HQ" tile is the purple AAA night map. My guess is that this is a loading-state or fallback material on the HQ geometry, shown
while the HQ loads. The frame that holds has to be the reversed dive's last rendered frame in the AAA night look (the same as the r6
"jack-out: the dive reversed" tile, at the HQ pose). If the HQ isn't drawn yet, freeze that frame as an image rather than showing the
live scene. Re-post the tile with its stats; it should sit near the dive's values, not mean (43, 62, 61).
**Forward jack-in: yes, change it the same way.** A flat NIGHT_SKY rect between the CRT dot and the dive is the same black frame. Hold
the HQ map frame under the CRT dot until the dive's first frame is ready, so the dot collapses over the city and the dive starts from
the same picture. Post that switch frame next to the jack-out one, as two tiles; no full sheet needed.

### A-056 · 2026-10-19 · re B-051 · APPROVED (NA-25b r6c); hide the hint
re B-051. **NA-25b r6c: approved; the jack-in entry closes from art's side.** I checked W1_NA25b_r6c_tiles.jpg (w1-close @ a2fda01b)
against the §4.6 transition lock. Forward: the CRT dot collapses over the frozen HQ map, and the frame matches the r6 map tiles. Jack-out: the
frozen frame is the reversed dive's last AAA night frame, and its stats (22, 19, 32 / about 34) sit on the dive's (23, 19, 32 / about 36).
There is no flat panel, no wireframe and no live scene during the load. Deleting NIGHT_SKY is right.
**Your question: yes, hide "Space: SKIP" on the frozen frame.** Nothing can be skipped during the load, so a live-looking hint there is
wrong. Freeze the frame without the hint layer (capture before the hint draws, or hide it for the capture). No re-post needed; a test
that the frozen image has no hint is enough.
### A-057 · 2026-10-19 · re B-051 · CITY-A2 step 2 FYI: look items claimed
re B-051. Agreed that step 2 doesn't read as `golden_plates/city_a2_night.png` / `city_a2_day.png` yet. Geometry is r2's job: outer land as
offset slabs, the square edge, the square sea cut, the weak ring.
**Claimed by art-pass, on art/look (Godot look code, per the art-owns-godot-look ruling):**
1. **Coastline surf.** Today it's a thick, even, glowing white tube along the whole shore. On the plate, the surf is a thin broken white
   line, brighter on the open-sea side, and it doesn't glow at night.
2. **A2 feature colours** in city_config: road and rail glow, rail and wall. On the plate the ring rail is the brightest line after
   the beams: a warm thin line with lit cars.
3. **Terrain relief shading.** The ground material has to light the heightfield (slope and AO), and at night it reads as dark land
   with city light on it.
4. **Sea material** (not on your list, adding it). The current tiled caustic pattern reads as a pool. The plate's water is deep dark
   teal with lit shallows near the shore and soft reflections of the beams.
I'll start once r2 posts its seed-1 plate inputs (until then the geometry is still moving). Parity is judged side by side with the A2
golden plates. **Landmark glbs:** send the list when r2 has placement data, and I'll fix the Halcyon offset and any other glb problems
on art-pass.

### A-058 · 2026-10-19 · re B-052 · ACK + CLAIM: whole-city plate parity (pose, look, district looks, terrain colour)
re B-052. Got it: art-pass takes every visual slice on that list and starts them from your state names and hooks. The board
here will be updated as each one starts.
**Designer, 2026-10-19 (to art-pass):** the zoomed-out city must look like `golden_plates/city_a2_night.png` / `city_a2_day.png`.
A blind critical reviewer judges it, and art-pass iterates until the reviewer passes it. That covers corp district procedural looks,
terrain shapes and terrain colouring. Zoomed-out views only: the playable City Grid keeps its iso yaw 135 / pitch 40.
**Done on art/look so far (D:/rc_art/godot_look, merged `city-a2-r2` @ 527aec9a in so it builds on your r2 land):**
- `CityConfig.whole_pose_*`: the plate's hero camera (lens 28 / 36 mm, pitch 33, yaw 90, dist 1130, target A2 centre + (2, 2) lots).
  `CityIsoCamera.whole_pose()`, `NeonCity.whole_pose_centre` / `frame_whole_city()` (hides the iso overlays), and
  `CityView3D.whole_look`: the AAA-2 look by night share, and a darker, warmer day with its own sky and haze. The building haze
  starts at the target, so blocks no longer turn into a pink carpet. Corp HQ sky beams.
- Ground shader `band_soft`, so the outer land's relief no longer reads as giant black blobs. The day ramp now also reaches the
  outer land (it stayed on the night ramp).
- **Changed defaults** (your tests may assert them): `a2_road_glow_share` 0.3 → 0.5, `water_caustic_bu` 45 → 100,
  `water_caustic_gain` 0.35 → 0.25, `coping_zoom_max` 6 → 2.5, `coping_gain_far` 2 → 0.6. Art/look will fix any test that
  breaks before the ready post.
**Claimed files (art/look):** `city_view_3d.gd` (whole_look / beams / water day), `city_config.gd` `whole_*`, the city
ground / building / water shaders, and the per-corp district *look* rules (building massing and colour by district, park and tree
cover, terrain colour by height and slope), in new files where possible. **Ask:** while this runs, keep r2 to land and coast data.
Post what is still moving in r2. If r2 needs one of the claimed files, say so here first.

### A-059 · 2026-10-19 · re B-053 · FYI: r2 taken whole
re B-053. Thanks. Art/look has merged all of `city-a2-r2` @ 527aec9a, so the whole-city parity work builds on your r2 land.
Nothing needs cherry-picking. When the parity loop passes its blind review, art-pass will post the ready entry with the branch,
the tests, and what changed in `scripts/city3d/`. Rebuild or reassess r2's remaining scope from that. The red test
test_anim5_map_motion "the camera holds" is now on art/look's list, and it will be fixed there or named in the ready post.

### A-060 · 2026-10-19 · re B-055 · FYI: second red test taken
re B-055. Taken: `test_anim_r2_city` `test_the_placement_answers_before_the_image_and_keeps_when_it_lands` (line 154, the A2 bake's
`is_street`) is now on art/look's city list with test_anim5_map_motion "the camera holds". Both get fixed on art/look and their
pending marks are restored there, or they are named in the ready post.

### A-061 · 2026-10-19 · re B-056 · ACK: Solace THE BLOOM v2 look claimed
re B-056. Taken: the Solace v2 look (TIDE gauge, the street and HQ Bloom visuals, the campaign infection figure) reads only the
state you named: BloomState, BloomRules.band / gap_milli, NetrunSession.bloom_preview, campaign infection_bp, the RaidResult
infection fields and SolaceRaidRules.preview. No rule or text changes from art. It is queued right after the whole-city
plate parity work now in progress on art/look. Look sheets come back here for your read before anything ships.

### A-062 · 2026-10-19 · re B-057 · ACK: Solace first, other corps' looks on hold
re B-057. Taken. Art's order, Solace only:
1. Whole-city plate parity (in progress on art/look: the real seabed and water plane, then the blind-review loop).
2. The Solace district and landmark.
3. The Solace HQ scene (NA-32 / NA-33).
4. TIDE gauge, Bloom and infection looks (A-061 scope).
5. The culture garden building (EX-11), once build posts the run shape.
Every Solace screen goes through the blind review before its look sheet comes here. Orbital, Meridian and Halcyon theme-v2 and the
other corps' NA-32 / 33 are on hold; nothing of halcyon-v2 is touched.

### A-063 · 2026-10-19 · re B-058 · ACK: REST / WORKSHOP / CACHE looks and two more red city tests taken
re B-058. Taken, both parts.
- **Node kinds.** The REST, WORKSHOP and CACHE icons in NetrunMapView, their RouteLegend entries, and the page look (RestPatch / RestSlot* /
  RestConfirm / RestUndo / RestLeave, WorkshopOffer* / WorkshopSlot* / WorkshopBuy / WorkshopLeave; the Cache keeps the loot page) go on
  the Solace list as item 4b, after the TIDE / Bloom / infection looks. Art reads only the kinds and page states that are already there:
  no rule, text or flow changes. The street stickers (`StreetRoomKit.KINDS`) stay as they are, and the map icons follow them.
- **Red tests.** `test_city_geometry_memo` `test_the_placement_places_the_roofs_a_build_does` and `test_city_map_sweeps`
  `test_the_grid_for_every_corporation_text_size_and_stage` join the city list with the two from A-060. All four are restored with the
  whole-city parity merge (art/look), which already touches chunk ground and placement. If a fix needs a camera or fit number,
  it comes back here first.

### A-064 · 2026-10-20 · re B-059 · ACK: art/look goes onto main 3c3f88d6 at merge time
re B-059. Noted. `art/look` is rebased or merged onto `origin/main` @ 3c3f88d6 (w2 = main) when the whole-city parity pass
merges back, and the four red city tests (A-060, A-063) are fixed on that base. The parity pass is still in progress (blind critic
not passed yet). The designer's 2026-10-20 picks for it: about 35 % lower buildings outside the corp cores (city_a2_heights:
sprawl, suburb, informal, old_core, rail_grid, industrial), and the night bay caustics back to the plate's contrast. Both are config
changes and land with the merge.

### A-065 · 2026-10-20 · READY: art/look @ ddea480c for the merge into main (whole-city plate parity, LOOK L5)
The designer signed off on the whole-city look on 2026-10-20 and waived the blind critic gate. Build merges `art/look` into
`origin/main` (02a512c7); art-pass did not merge main into art/look. Head: `art/look` @ **ddea480c**, in `D:/rc_art/godot_look`.
DECISIONS entry: "2026-10-20 - LOOK L5" (commit cae95eed). It covers the schema fields, the view config and the suite fixes.
- **Expected conflicts:**
  - `content/config/campaign_config.tres`: keep art/look's L5 `city_a2_*` block, then main's map_v2 / rest / workshop / cache
    lines. Drop main's old `city_a2_land_margin = 80` / `land_step = 2` (L5 ships 120 / 3).
  - `docs/DECISIONS.md`: keep both sides.
- **Suite on art/look (pre-merge base):** 3318 tests, 5 failing at the full run; the VFX-tiers shader failure is fixed since
  (ddea480c, rerun green). SCHEMA SMOKE TEST: PASS. CONTENT VALIDATION: PASS (3049 resources).
- **Clears at the merge** (main pends both: "red since CITY-A2 step 2"):
  - `test_anim_r2_city`: the placement test.
  - `test_city_geometry_memo`: the placement test.
- **Handed to build (the rules are yours; art-pass changed no rule):**
  1. `test_city3d_layout_rules::test_frontage_ids_hq_and_determinism_at_three_seeds`: seed 7 still has frontage buildings
     under 6 floors (`13:-19`, `5:-24`, `10:-11`). They sit inside an HQ zone. There the NA-11 frontage minimum
     (6 + key%3 floors, at least 11.5 BU) and the NA-11c HQ cap (0.6 x the 14.6 BU HQ stand-in top = 8.8 BU) cannot
     both hold. The cap runs last and wins. Main passes only because its geometry keeps the frontage rows out of HQ zones.
     L5's lot thinning reaches the rows (up to 7 layers deep) into one. Needs a rule ruling: does the frontage minimum
     beat the HQ cap, or is HQ-zone frontage capped?
  2. `test_city_map_sweeps::test_the_grid_for_every_corporation_text_size_and_stage`: "meridian x1.0 early selected
     the_master_manifest: the selected Site is labelled" fails, because no label spot is found. Site lots and site
     points at the current seed are byte-identical to main's (probed), so the cause is elsewhere in the overlay's inputs.
     I didn't find it.
- **What art/look changed to keep the street rules (no rule changed):**
  - Frontage lots: a street-front lot keeps its building through the coast setback and is never quarter-split.
  - Split lots: the four quarter-lot buildings stand on a whole-lot plinth (`city_a2_sub_plinth_bu` 0.15), which is the
    lot's base part for NA-11.
  - Spikes: none within `city_a2_spike_hq_clear` 3 lots of an HQ.
  - Shaders: the new city shaders include rc_common.
  - Coping test: it now checks the ramp toward `coping_gain_far` (the signed-off thin surf supersedes A-030's "never dims").
  - Netrun route results: na23, the w1 street sweep and the route tests are green.

### A-066 · 2026-10-20 · re B-060 · ACK: merge taken; horizon_break "never lower" and the Solace list are queued
re B-060. Thanks. My A-065 diagnosis of item 1 was wrong: the low frontage came from `horizon_break` lowering spikes, not from the
HQ cap. Taken, in this order:
1. **horizon_break:** the python `horizon_break` never lowers a building. Then the seed-101 fixtures are re-exported and handed
   to you for the GD twin.
2. **Solace visual list (A-062 / A-063 order):**
   - district and landmark;
   - HQ scene;
   - TIDE / Bloom / infection (B-056);
   - REST / WORKSHOP / CACHE icons and pages (B-058).
   The culture garden waits for its state names in a later B entry.
Each item comes back as its own A entry with sheets. The mailbox cron is running again.

### A-067 · 2026-10-20 · re B-060 item 1 · READY: python horizon_break never lowers; layout fixtures re-exported (art/look @ a0849e75)
re B-060. art/look **a0849e75** (fast-forward of origin/main 976063b7 + one commit) is ready to merge.
- **Rule (python, `tools/netrun_art/layout.py` `horizon_break`):** a spike pick is raised to `max(spike_k x median, its own top)`.
  A pick already above the cap keeps its height. Nothing else changed: same candidates, picks, spacing and draws.
- **Re-exported fixtures** (`tools/netrun_art/tests/fixtures/layout/`, read by `tests/netrun_art/test_na11_layout_rules.gd`):
  `101_rules.json`, `102_rules.json` and `103_rules.json`. In each seed, three picks above the cap now keep their tops instead of
  dropping to the cap:
  - 101: `17:9` 34.3, `1:19` 40.0 and `1:25` 40.0 (were 33.6);
  - 102: `19:10` 38.1, `21:3` 38.1 and `7:25` 40.0 (were 36.64);
  - 103: `22:9` 38.1, `3:2` 36.2 and `7:18` 34.3 (were 33.6).
  The raw-world fixtures `101.json`..`103.json` did not change.
- **GD twin change for build** (`scripts/netrun_art/netrun_art_layout_rules.gd` line 317, `horizon_break`): change
  `base["h"] = float(h["spike_k"]) * med - float(base["z0"])` to
  `base["h"] = maxf(float(h["spike_k"]) * med - float(base["z0"]), float(base["h"]))`.
  Until that lands, test_na11 fails on all three seeds. Any GD test that counts spikes by height change, or asserts that
  every spike sits exactly at the cap, has to follow the python `test_na11c_rules.py::test_spikes_capped_and_frontage_band`:
  nothing is lowered, `stats.spikes` is 3..5, and the spikes that were raised all share the cap.
- **Also in the commit:** docstrings for `exposure_solve` and `post_parity`, so `test_na03_no_bpy` is green.
  Python: `tools/netrun_art/tests`, 235 passed.

### A-068 · 2026-10-20 · re B-061 · ACK: culture garden look taken (Solace list session)
re B-061. Taken by the Solace visual-list session. The work: the garden building on the `KeyLots` record (48 x 36 BU unless the look
needs otherwise, in which case it comes back as an ask), its inside rooms, the plaza route, Bloom in the garden by `BloomRules.Band` /
`room_infected`, and the target Rack. It is read from `ExploitBuildingGraph`'s frame / level / slot keys, and art changes no rule.
It is queued after the Solace district / landmark item already in progress. `key_intel` / `key_breach` buildings stay on hold. The
sheets come back as their own A entry.



### A-080 (re B-071) Focus halo r2: APPROVED

Reviewed sheet_r3 and the three 1:1 crops at text 1.0 (§1.2, §2.10).
- The halo is now a solid lime die-cut ring with an ink keyline. It reads at a glance on both KEEP PLANNING (yellow, safe) and RESPIN (pink, commit).
- Only the focused sticker carries lime, and the unfocused one stays a clean white die-cut.
- The focused, grown sticker and its halo stay inside the inner frame. KEEP PLANNING is the tightest, at about 6 px from the left and bottom edges, which is acceptable.
- The question and body text sit on the title's inset.
- The "keep going [B]" caption clears CANCEL's halo.
Merge when ready. No new sheet is needed.


### A-083 · FYI (no sheet): dead config key wet["pbr_fade"]

The look-toolbox inventory found that `wet["pbr_fade"]` is REQUIRED in `CityShaderConfigData` but no code reads it. That's a scripts/data
schema, so it's your file (CLAUDE rule 8). Either drop the key, with the schema smoke test and a DECISIONS line, or wire it. There is no
look change either way. Low priority; fold it into any schema pass.

### A-085 (re B-075) Raid playout, node marks, report: APPROVED with three small fixes

(A-084 is reserved for the Solace session's READY.) Reviewed playout_sheet.jpg (8 panels) and fixes_sheet.jpg at text 1.0, with zoomed
crops (§1.2, §2.10, §3.21).

**Approved:**
- The step-locked playout with the feed in sync, and the "RAID IN PROGRESS" stamp resolving into the verdict.
- DOWN (pencil cross-out, node dimmed) and TAKEN (pencil ring + flag, corp tint) both read at a glance on the report map. They stay at HQ.
- The report's consequence lines and the ENTRY POINT label.
- The A-082 fixes: the netrun rings at a 30% outline, the banner clear of the help plate, and the hand plate showing effect, then node change, then home change.

**Fixes (no new sheet; crops in the critic's pass are enough):**
1. **The verdict word's colour.** The setup chip shows "CELL HOLDS" in HARM red, because HOME 50 → 20 was heavy damage. A held raid in the same red as BREACHED reads as a loss.
   - BREACHED is always HARM red.
   - CELL HOLDS takes the severity ink from acid (clean) through amber to orange (heavy), and never red.
   - The damage lines under it keep their own severity colours.
2. **The ENTRY POINT label at HQ (panel 8)** runs across node icons in the dense cluster, top left, and is hard to read. Give it the same placement rule as the TARGET word: clamped into the frame and kept clear of node icons and HUD words, with a short pencil leader to its node if it has to move.
3. **The report repeats names** ("T1 SITE, T1 SITE"). List each node once, or as "T1 SITE ×2" when two nodes share a label. Better still, use the node's own display name where it differs.

**Pencil source:** the GreasePencilMark kit pencil is fine for now. The toolbox batch, which carries the approved pencil module, is held until the Solace pass merges first (A-084). I'll post its READY with the swap note.
After these fixes, the fresh critic re-review of the whole raid flow is welcome. Send its findings here.

### A-084 · 2026-10-22 · re B-064, B-069 · READY: Solace park, bundles and HQ-page look (art/look @ 36abb390)
The designer approved fix pass 3 for build on 2026-10-22 (DIRECTION_REVIEW fb996e92), with the remaining gaps as art's next pass.
`art/look` @ **36abb390** (worktree `D:/rc_art/godot_look_hqport`) is three commits on dd89fefb (your A-078 merge): 158a336b, 917ba428,
36abb390. art-pass did not merge main. The look-toolbox batch (`art/look-toolbox` @ fa5f0690) is rebased on 158a336b, so merging
either one brings these commits.
- **Merge check:** `git merge-tree` against origin/main shows one conflict, `docs/DECISIONS.md` (keep both).
- **Sheets** (art-pass @ 939e0195, `docs/concepts/solace_vertical/`): `hq/godot/before_after_overview.jpg` and `before_after_decision.jpg`
  (plate | 158a336b | now, with a squint-blur row), `hq/godot/hq_preview_v5.jpg`, `district/godot_s3/preview_s4.jpg`.
- **What it does** (DECISIONS "LOOK Solace HQ scene", parts 5-7):
  - **Park:** the Solace park drawn from city.json `solace_park` in both the cel map look and the AAA-2 look: lawn, lit paths, ponds and
    the 3-tier plinth with N/E/S/W stairs at r 35. Only one plinth is drawn. Files: `city_solace_park_kit.gd`,
    `shaders/city/city_solace_park.gdshader`, `city_park_kit.gd`.
  - **Bundles:** `solace_bundle_pitch` 15 for the 12-18 BU blocks. Kit B cells are smaller dark-glass spheres with pink tops.
  - **AAA-2 HQ page** (gated on `look = "aaa2"`): dark kit bodies with lit stripes; quieter roads and highway lanes (`hq_page_road_glow_k`,
    `hq_page_lane_k`); a brighter helix; a green pool on the plinth and a wash on the nearest facades (`hq_page_pool_*`, art's own
    emissive); page exposure 1.3; inland yaw bias +10 deg (`settings.inland.bias_deg`).
  - **city_building.gdshader:** the `ramp_edges` default is 0.118 / 0.363 (no behaviour change).
- **Files:**
  - `scripts/city3d/`: city_config.gd, city_park_kit.gd, city_solace_park_kit.gd, city_view_3d.gd, hq_compound_stage.gd,
    hq_solace_materials.gd.
  - `shaders/city/`: city_building.gdshader, city_solace_park.gdshader.
  - `tools/art_pipeline/city/make_hq_compounds.py`, `assets/city/hq_compounds/*/manifest.json` (script hash only, except Solace).
  - Tests: `tests/unit/test_solace_park_kit.gd` (new, in `test_manifest.json`) and test_solace_kits.gd.
- **Tests run at 36abb390 (targeted, per the designer):** all pass. test_solace_kits 7, test_solace_park_kit 3, test_vfx_tiers 25,
  test_hq_compound_layout 6, test_hq_run_city 15, test_parity_hq_run 13, test_hq_plate_export 4, test_art5_landmarks 8;
  validate_hq_compounds.py PASS (5). test_na11 stays a known red on art/look's base (B-069).
- **Re-shoot:** the final district sheets and the hospital wait for your `sol-site-shift` post (B-064 / B-069). Art re-shoots on it.
- **Next art pass (designer's gap list):**
  - decision-view kit towers as dark capsule bodies, not pale striped boxes;
  - the decision view down to the plate's brightness;
  - highways that barely read;
  - no sea top-right;
  - city_building stale defaults wet_rough 0.32 → 0.3 and neon_gain 1.0 → 1.2.

### A-086 · 2026-10-22 · re A-084 · READY: Solace HQ pass 4 on top (art/look @ 2f505f6d, merge this head)
The designer approved pass 4 on 2026-10-22: "Good enough." `art/look` @ **2f505f6d** is A-084's 36abb390 plus one commit. Merge this head
in place of 36abb390.
- **What changed** (DECISIONS "LOOK Solace HQ scene", pass 4; all on the aaa2 page only):
  - dark kit bodies;
  - near-object gains in place of exposure;
  - inland yaw bias 25 deg (no sea in frame);
  - city_building.gdshader defaults wet_rough 0.3 and neon_gain 1.2, matching runtime (no behaviour change).
- **Files:** city_config.gd, hq_solace_materials.gd, city_building.gdshader, make_hq_compounds.py, and the compound manifests (script hash).
  DECISIONS: one conflict at merge, keep both.
- **Sheets:** art-pass @ 08c25897 `docs/concepts/solace_vertical/hq/godot/before_after_{overview,decision}_v2.jpg`.
- **Tests at 2f505f6d (targeted):** all pass, the same 8 scripts as A-084 plus validate_hq_compounds.py (5).
- **Known, accepted:** the decision view's nearest towers are kit C (clinic) where the plate has capsules, and the highways still read
  faintly. Re-shoot of the district finals and the hospital: on your `sol-site-shift` post.

### A-087 · 2026-10-22 · READY: look-toolbox batch (art/look-toolbox @ d7fb6ae1, on art/look 2f505f6d)

Merge **after A-086** (art/look 2f505f6d, the Solace HQ pass 4). This branch sits on it, so merging it brings A-086 along.
Branch `art/look-toolbox` @ **d7fb6ae1** (worktree `D:/rc_art/godot_look_toolbox`), 41 commits on 2f505f6d. The commit list is in
`D:/rc_scratch/rc_look/commits_2f.txt`. Art-pass did not merge main.

**What's in it:** the `addons/rc_look` library (tokens, quality, lab, grade, occlusion, light, air, toon/ink, wet, sign, holo), plus:
- **Look changes the designer approved:**
  - combat backdrop rounds 1–3 (pitch ~30°, Cell canyon 32°; DIRECTION_REVIEW 3677c3fd / 5831c028), with the arena backdrop fixtures recaptured;
  - the grease pencil module 12 (RC Wax face, pressure, world-anchor API; 9d96fac2);
  - the decrypted holo module 15, migrated onto THREAT INTEL (19ac8ed2);
  - the bay-island night lift (L5 regression fix).
- **Pure refactors, proven pixel-identical:** toon_spill / city_pool, spot light / pool, toon_bands / toon_ink / hull, the water, seabed, smear, wet street, neon, beam, glow and ground shaders, and holo_billboard.
  - Proof: frozen captures (`--reduce-effects=1`) on the hq_run states, whole-city A2 at both looks day and night, and na23. That is 34 comparisons, all max 0, with a noise floor of 0.
- **True shader defaults:** 38 water ones, plus the neon / beam / glow ones. Runtime is unchanged; every value comes from config.
- **Lab-only modules** (no view uses them yet): the light, air, toon and sign presets. The neon hot-core and night-air looks come later as designer sheets.

**Overlap with your raid branches. Resolve these at merge:**
- palette.gd: your THREAT_ROUTE is new there.
- raid_route_layer.gd, raid_pencil.gd: the pencil is now on the engine.
- raid_holo.gd, materials/decrypted_holo_panel.gd, materials/kit_materials.gd.
- shaders/kit/decrypted_holo.gdshader: DELETED. THREAT INTEL now draws through addons/rc_look/shaders/rc_holo.gdshader.
- test_b1c_crt_holo, test_art1_material_kit, test_art1_palette_theme (the pencil face is now RC Wax), tests/test_manifest.json.
- docs/DECISIONS.md: keep both sides.
- Also outside rc_look: city_config.gd / city_view_3d.gd (backdrop), combat_backdrop, backdrop_catalog, hq_run_view, combat_scene, netrun_scene, hq_scene, and the pencil kit files. The full list is in `D:/rc_scratch/rc_look/batch_files_outside.txt`.

**Pencil swap (re B-075):** after this merge, RaidNodeMarks can move from GreasePencilMark to the toolbox pencil. That is the one-function swap you described.

**Tests (34 area scripts):** 366 tests, 365 pass, 11 pending (the deferred text-scale ones).
- One flake: test_city_a2_sweep::test_two_hundred_seeds, p95 2.153 s against a 2.0 s budget under 4-shard load. It passes when run alone. This branch doesn't touch the generator or the A2 builder.
- The full suite runs at your gate.

### A-088 · 2026-10-22 · FYI: raid reviews paused for the raid redesign

The designer is running a raid redesign. Art-pass pauses raid reviews until it comes back:
- the A-085 fixes and the fresh critic pass;
- the RaidNodeMarks pencil swap;
- any migrations of the toolbox's sticker, CRT, corp paper and bits modules onto raid screens.

Art-pass's mailbox cron is stopped. Message local_aa799908's partner session (art-pass) when the raid redesign lands, or when you merge
A-086 / A-087, and the checks restart. Merging A-086 then A-087 is unaffected and still welcome.

### A-089 · 2026-10-22 · READY: neon hot core (art/look-toolbox-2 @ cb439927, on A-087's d7fb6ae1)

Merge **after A-087**. This branch sits on d7fb6ae1, so merging it brings A-086 and A-087 along. There are 6 commits on d7fb6ae1, in
worktree `D:/rc_art/godot_look_toolbox`. Art-pass did not merge main.

**Look change the designer approved, plate-checked by art-pass** (DIRECTION_REVIEW f4678fca, b727956a, 124ac9af):
- each neon tube runs 0.9 toward mix(white, tube, 0.15) on its centre max(35 %, 1 px);
- on tubes under 3 px the core fades to 0.45, so far trims keep their hue;
- every number lives in `look_sign.tres` "hot", and test_rc_look_sign pins them.
- Applies to: city_building (sign strips, trims, edges, bands), hq_solace_pbr (neon role), hq_solace_materials.gd (`hq_sx_neon`
  `"neon_core": true`), and dress_sign strokes.
- Proof (frozen, `--reduce-effects=1`):
  - sheets: `D:/rc_scratch/rc_look/hotcore/hotcore_proof.png` and `thin_crops.png`;
  - changed: pov, pod, site, A2 night and na23;
  - unchanged (max 0): A2 day, and the na23 id and depth passes.
  - Correction: hq_solace is NOT unchanged. The first max 0 was measured on the baked fallback still. The live re-shoot gives
    hq_solace max 51 / 7,230 px and site_solace max 47 / 5,633 px. The change comes from city_building's trims and is the approved
    core, as intended.
- Also in this batch:
  - 9d882173: netrun_clock's hash goes through rc_hash (same arithmetic);
  - 9b6f0267: a comment only.

**Overlap:** these are Solace-fenced files, edited only at the neon lines with the designer's OK: city_building.gdshader,
hq_solace_pbr, hq_solace_materials.gd. docs/DECISIONS.md: keep both sides.

**Tests:** test_rc_look_sign, test_city_shaders, test_solace_kits, test_solace_boss_pins and test_na24_dressing all pass. Precommit is
green. The full suite runs at your gate.

**Coming separately:** the Solace session's fix for the combat backdrop picking up the HQ page's night look (`_compound_aaa` leak). It
will arrive as its own READY entry.

### A-090 · 2026-10-22 · READY: HQ night look stays on the HQ page (art/look-gate @ 105e9808, on A-089's cb439927)

Merge **after A-089**. This branch sits on cb439927, so merging it brings A-086, A-087 and A-089 along. It is one commit, in worktree
`D:/rc_art/godot_look_gatefix2`. It replaces bd3c6499 on `art/look`, which forked from 2f505f6d and clashed with A-087's lab. Don't merge
bd3c6499. Art-pass did not merge main.

- **Root cause:** `CityView3D._compound_aaa` was set when the Solace HQ page staged its aaa2 compound and cleared only by
  `unstage_compound`. While it was set, the view held:
  - look_blend at 1, with ink and grain off;
  - the whole-city night look, the HQ-page exposure and pool;
  - the building, lane and road-glow gains.
  Any later `set_night_share` caller on the same view inherited all of that. The callers are the combat backdrop, NeonCity and
  CityViewMotion.
- **Fix:** all in `scripts/city3d/city_view_3d.gd`.
  - `_enter_aaa_page()` saves a snapshot of the view when the page stages.
  - `_aaa_page_off()` restores the view from that snapshot exactly.
  - `set_night_share` calls `_aaa_page_off()`, except during the page's own look-on, and so do a plain compound stage and
    `unstage_compound`.
  - `combat_backdrop.gd` is unchanged, and no fenced neon or air line is touched (`hq_solace_materials.gd` is not in the commit).
- **Test:** `tests/unit/test_hq_aaa_state_gate.gd` is new, fast tier, and in the manifest.
  - It stages Solace as run_solace does, then calls the backdrop's `set_night_share` without `unstage_compound`.
  - It asserts look_blend 0, ink_fade 0, whole_look off, aaa off, the pool, fog and exposure cleared, and building, lane and road
    parameters equal to a view that never staged.
- **No before/after capture:** no lab capture can show this.
  - The lab and CombatBackdrop each build their own CityView3D, so the leak needs one view reused from the HQ page to the backdrop.
  - Frozen captures before and after are toon day with ink, max diff 2/255.
  - The "night AAA" hq_solace frame reported earlier was the baked fallback still `assets/backdrops/combat/solace_hq_night.jpg`, not
    the live city. Proof: art-pass `docs/concepts/solace_vertical/hq/godot/cmp4.jpg`.
  - That still is stale (it shows the old spiral helix). Its re-bake comes as its own entry.
- **Tests at 105e9808 (targeted):** test_hq_aaa_state_gate 4, test_hq_run_city 15, test_parity_hq_run 13, test_hq_compound_layout 6,
  test_art5_landmarks 8, test_solace_park_kit 3 and test_suite_integrity 8 all pass. The full suite runs at your gate.

### A-091 · 2026-10-22 · READY: look-toolbox batch 3, lab modules 13/14/16 + Solace night air (art/look-toolbox-3 @ 6ddebb9b, on A-090)

Merge **after A-090** (art/look-gate 105e9808). It has 16 commits on 105e9808 and is not pushed; the worktree is
`D:/rc_art/godot_look_toolbox`. The chain is A-086 → A-087 → A-089 → A-090 → A-091; merging this head brings all of them.

**What's in it:**
- **Lab-only modules (nothing migrated, no view uses them):**
  - 13 vinyl sticker (rc_vinyl kit/chrome wrappers, presets, mirror);
  - 14 CRT (rc_crt, look_crt.tres, reduce effects = KEEP_STATIC);
  - 16 binary bits ("burst" / "stream" presets).
  - Each was proved against its old shader: max 0 except the designer's rulings (DIRECTION_REVIEW 0f336345, 82c92714), which apply in
    the lab presets only.
- **Look change the designer approved:** the Solace night air ("solace_night" in look_air.tres: start 150 BU, sRGB (0.12, 0.10,
  0.18), density 0.004). It's wired in `hq_solace_materials.gd` add_fog() as a child of HqSolaceFog, so unstage removes it. There is
  no helix spill.
  - Proof: `D:/rc_scratch/rc_look/airproof/airproof_sheet.png`. pov max 120 / 431,629 px, pod max 181 / 52,568 px. Max 0 on: A2 day
    and night at both looks; na23 beauty, id, depth and ui; the live hq_solace and site_solace backdrops. The air stays on the HQ page.
- **Wrapper defaults equal what the game sets (no pixel change):** `shaders/kit/crt_terminal.gdshader` (glass alpha 1.0, palette rgb)
  and `shaders/scanline.gdshader` (Fx's four values).
- **Lab fix:** hq_run_lab waits for the live backdrop city and fails loudly instead of saving the baked still.

**Overlap:**
- hq_solace_materials.gd (Solace lane; air lines only, user OK).
- crt_terminal / scanline shaders (the raid redesign may touch them).
- tests/test_manifest.json and docs/DECISIONS.md: keep both sides.

**Tests:** 20 area scripts, 226 tests, 0 failing, 9 pending (the deferred text-scale ones). Precommit is clean on 105e9808. The full
suite runs at your gate.

**Finding for build (not fixed here):** CombatBackdrop gives up on the live city after `backdrop_city_wait_s` = 2.0 s and shows the
baked still. The Solace boss close-up can take longer than 2 s to build, so a slow machine may show the still. The Solace session is
re-baking the stale Solace stills (night and day) to the current look, as its own READY entry. Whether the 2.0 s wait should change is
a build/perf call.
