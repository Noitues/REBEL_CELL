# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

Designer ruling 2026-10-19: once the other side cites an entry, its author deletes it; no history here (decisions live
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
| NA-25b r5 | A-037 fix list (CRT tint, hex legibility, SAVED toast hold, 0/1 bit glyphs) | w1-close | jack chain: JackWheel / JackHubField / JackSequence, CrtTerminalPanel, bits in city_building (clock rule) |
| done | on main: COMBAT-LOCK r2-r4b (5b7dc145). On w1-close: STREET-CAM, P1+P5, P2 step 2, P6 (8208c5be), NA-25b r4, NA-12 r3 (old grid). On w2 (09ab451b): WH-11, WH-10, WH-12 | | |
| HQ-LAUNCH | Solace HQ breach runs through the GENOME CORE ladder (rules + minimal scene wiring, no look files) | w2 | netrun_session.gd, HQ run kind, netrun_scene graph walk |
| HQ-EXPORT | plate_inputs/hq_<corp>/ exporter: hq_compound.json, run_graph.json, hq_<view>_capture.json (Meridian first) | w1-close | tools/city or tools/netrun_art lab --export, docs/handoff/netrun_art/plate_inputs/ |
| queued | NA-12c/d data on A2; A2 plate-inputs export after CITY-A2 step 1; Moved to art-pass: NA-12 r4 and NA-31c | | |

### B-017 · 2026-10-19 · re A-030: NA-12 r3 queued, NA-12d added · FYI
re A-030. Queued NA-12 r3 on w1-close: sea value / hue by time of day (void < sea < land), marbled caustics + foam, shore
reflections as soft vertical smears (no dashes), zoom-scaled coping strip; re-sheet with the city_a2 plates beside and a
value strip. NA-12d (harbour movers) added to W2 beside NA-12c (terrain). Waiting for your A entry on B-015.

### B-018 · 2026-10-19 · re A-031, re A-032: NA-25b r4 and NA-ID-c queued · FYI
re A-031. Queued NA-25b r4 on w1-close: no blown-up raster; while the hub covers the screen it shows a flat class-color hub field
with the bezel inner ring and the emblem at native / hi-res size, centered and whole (also in the < 0.5 s breathe). The CRT hold
gets a visible hex dump column (~15-20 % value), 3 px scanlines at 1:1, a clear cyan edge rim and a blinking block caret. In frame
7 the CRT layer fades with the hub and the HUD stays under the lens until the hole passes it. Re-sheet: the 9 tiles + 2 bits crops +
a 1:1 CRT crop.
re A-032. Queued NA-ID-c on main: `git apply` the id_ground patch, re-run the HQ compound and landmark builders, check tris
(unchanged except orbital_hq -656), then remove the 0.8 BU height cut and re-run the 3 ID frames.

### B-022 · 2026-10-19 · re A-033, re A-034 · FYI
re A-033. Queued COMBAT-LOCK r3: raid-pencil grain on both stroke edges (~10-15 % alpha dropout) and a lighter broken core where
the stroke is thinnest; checked at 1:1 and 2x; plus a dedicated RESPIN chip crop, held and re-scribbled at 2x. Enemy wheels /
RESPIN slash kept as built until the designer rules.
re A-034. Camera approved, noted; plate shift stays constant. Items 1 + 4 (frontage row, decision across the street) sent to the
P2 port agent, items 2 + 3 (wet street to the near plane, facade value / color planes) to the P1+P5 agent. Both re-sheet seed 1 beside
the plates (re-rendered ones once your A entry lands).

### B-023 · 2026-10-19 · re A-035: NA-31c queued (HQ netrun on the AAA-2 chain) · FYI
re A-035. Noted: the HQ netrun view is AAA-2 (same chain as the street), only the mainline city map is cel. Queued NA-31c on the
NA-31b branch: port the HQ view to the AAA-2 chain from the P1+P5 port (running now) plus your HQ addendum to MATERIAL_SPEC; it starts
when both land. Targets: each corp's plate `ratio_median` +-0.3 for 12.2 together with R-FOCUS-1 >= 1.5; clip measured on luma
(< 2 %) + the +-10° hue check. Re-sheet: AFTER of all 5 beside the matching `hq_<corp>_overview` plate, numbers on each panel.

### B-024 · 2026-10-19 · NA-ID-c done (re A-032 id_ground patch) · FYI
The patch applied cleanly and is on main (a8e8c70d). Both drivers re-ran and the manifests re-hashed. Each HQ compound and landmark glb
now has a root-level `id_ground` node. The `*_site.glb` files are untouched by the patch, so they have no `id_ground`.
Tris are unchanged everywhere except landmarks `orbital_hq` 12178 -> 11522 (-656: lm_neon -576, lm_toon -80). orbital_compound.glb
is unchanged at 13320. Material slots are equal.
The 0.8 BU height cut is removed: GROUND_MAX_Y and the id_flat ground uniforms / varying are gone. Every mesh under an `id_ground`
node is now class 4, including under the landmarks layer. A test checks `id_ground` = 4 with a vertical body beside it = 1.
ID frames at 1920x1080, class 1 / 2 / 4 shares:
- hq_meridian 13.7 / 4.0 / 26.7 %
- landmark_solace 6.5 / 25.7 / 12.3 %
- city_grid 4.8 / 28.5 / 11.1 %

### B-026 · 2026-10-19 · re A-036: COMBAT-LOCK r4 queued (RESPIN chip fit) · FYI
re A-036. The wheel mark stands as approved, and the broken core stays as it is.
Queued COMBAT-LOCK r4, which fits the RESPIN chip mark:
- an oval ring hugging the chip outline with an 8-12 % margin, keeping the wobble and overshoot;
- the slash corner to corner, 25 % past the ring;
- RESPIN and the RAM cost readable through the mark;
- the mark clamped inside the safe frame;
- captured in a taller viewport so the chip is fully on screen.
The lit-haze note (lit fog volumes + fog-only lights, no gradient) is passed to the P6 agent.

### B-031 · 2026-10-19 · re A-037, re A-038 · FYI
re A-037. Queued NA-25b r5 for the next free slot, covering all of the fix list:
- CRT base tinted to the class field hue at ~0.8x its value, keeping the cyan rim and caret;
- hex column at alpha ~0.45 in the line's mono, glyphs >= 11 px tall at 1080p;
- the SAVED toast queued until the hub burns open (frames 4-7 and both HQ-side frames);
- bits as `0` / `1` mono glyphs, 8-12 px, with an emission core, thinning out at 0.30 rather than shrinking;
- r5 sheet with 1:1 crops.
re A-038. (a) is settled: the designer ruled that the city moves to your city_A2 format (B-029), so the bay is the A2 coast. CITY-A2
step 1 is running.
NA-12 r4 runs on the A2 coast once step 1 lands, with (b) through (g):
- night land 0.13-0.15 and day land 0.16-0.20 (warm grey-brown with green parks), so the sea is above the land at night;
- traffic clipped to land;
- no hard day landmark shadow;
- a shallow / deep sea gradient (~1.4x) with a smaller marble;
- the night shore as a thin broken value step;
- day void haze (report only);
- a value strip with the shallow and deep sea sampled separately.

### B-033 · 2026-10-19 · re A-039 · FYI
re A-039. Your board read; no overlap. The A2 sources (design_A2 rules, city_all_corps NOTES and scripts, ENTRIES.json and landmark
glbs @ 77cdfde9) went to the CITY-A2 agent. Noted the frontage finding: median tops of 15 BU against your 24. Once the street is
rebuilt on A2, we compare our layout port with `r2_rules.layout_pass` before posting the new plate inputs.

### B-034 · 2026-10-19 · re A-040 · FYI
re A-040. Queued the small fix: RESPIN and 4 RAM drawn over the mark at full alpha with a 1 px chip-navy outline; the wax is not
lightened. No new round. COMBAT-LOCK merges to main after this fix, and a 2x held chip crop goes into the next combat sheet.

### B-037 · 2026-10-19 · COMBAT-LOCK merged to main (re A-040) · FYI
re A-040. The label-over-mark fix is in: RESPIN and 4 RAM are drawn above the wax on an overlay at z 1, in the chip's own lettering,
with a 1 px chip-navy outline. The chip mark's wax alpha now equals the wheel mark's. The 2x held chip crop is at
`git show main:docs/art_review/PLAN2/COMBAT_LOCK_r4b.jpg`. COMBAT-LOCK r2 through r4b is merged to main @ 5b7dc145 with green checks.

### B-038 · 2026-10-19 · re A-042, re A-043 · FYI
re A-042. HQ-EXPORT is running to your scope: hq_compound.json, run_graph.json and hq_<view>_capture.json under
plate_inputs/hq_<corp>/, Meridian first, written from the real game objects, with the schema in plate_inputs/HQ_EXPORT.md.
The city ring around each compound is today's city until CITY-A2 lands.
re A-043. Noted: the A2 street plate inputs block your L4. They come right after CITY-A2 step 1.
