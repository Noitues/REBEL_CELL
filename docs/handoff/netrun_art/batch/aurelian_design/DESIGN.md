DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id aur__design; status ok; tokens in 38586 cache-write 20794 cache-read 60175 out 9225; cost $0.117 -->

# AURELIAN CONCORD HQ netrun: THE CIRCUS AURELIUS (design pass, round 3 draft)

Status: plan and surface only. Nothing here was rendered or run. Sources: `new_corps/roman/` (identity, NOTES, hq_overview), the plan-2 batch draft `hq__aurelian`, PIPELINE_SPEC (cited "spec n"), designer rulings D1-D10. The mechanic (TURNING GATES, VERDICT, Favor, Grand Stand, Rostrum) is the batch draft's and is not redesigned here. Names: THE ROSTRUM is the working Central Server name (the Aurelian gap name under D2); its hub is THE GRAND STAND. The bible's "Civic Core" is not used.

## 0. What I see and what I assume

Seen in the supplied images:
- `hq_overview.png`: a colosseum with 4 concentric lit teal rings; the arena floor at the center with a white stacked-ring server in a red pencil TARGET circle; a camera high 3/4 from the south; route stickers on the far half of the bowl, 6 / 5 / 4 / 3 per ring from outside in; a lime walked line, orange options 1 and 2, white dashed ahead links; a yellow pencil "NEXT STEP: GATE TURNS HERE" circle; a "GATE OPEN" tag; an info panel "THE TURNING GATES" (step 3 of a 4-step turn, ring gate angles 100/280 CW, 60/240 CCW, 118/298 CW, 80/260 CCW; rule "drop only where aligned"); lamp posts on the outer rim; a fine cityscape beyond the wall.
- `hq_mechanic.png`: four step panels, plan view, with green squares for open gates and bronze barriers with sparks for shut gates; the visual-state key (GATE OPEN, GATE SHUT, NEXT STEP, RE-MADE, THE ROSTRUM).
- `building_kit.png`: basilica, aqueduct, triumph gate, piazza, 3 insula types, campanile, all on magenta plinths. Light fog; the beams barely show (known gap in NOTES).
- `identity_board.png`: verdigris #29DBA6, travertine, porphyry, gilt, marble.
- `site_street.png`: the street netrun in the same palette.

ASSUMPTION: the overview is a concept render at kit scale (bowl r 150), not at one-city units. ASSUMPTION: the "terraces" read as flat teal rings with no visible riser, barrier or gate geometry at this resolution; the gates in the image are only a UI panel and tags.

## 1. Concept

THE CIRCUS AURELIUS is a colosseum whose four seating terraces are the four rings of the run. The player descends from the cheap seats to the arena floor, where THE ROSTRUM stands. Each ring wears a bronze gate barrier with 2 gates that turn one step per completed node. The stone is a brand skin: travertine with verdigris trim lines and thin neon, statues as billboard mounts (identity.md), not a museum.

The silhouette rule (spec 8.3 and 8.6b): from the full-city map camera it reads as a **round open bowl of arcaded storeys with four lit seating rings**, the only round arcaded stadium in the city. It must stay distinct from Orbital's round podium (r 64 with a rocket) by arcade rhythm, stepped terraces and the absence of a vertical needle, and from Tethys's circular pier city by being dry, stone and tiered.

## 2. What it is not

- Not Halcyon: no eye, no pyramid; the clock is geometric, not a watcher.
- Not Solace: no vertical ladder; descent is inward.
- Not Orbital: no vertical object on the lot. Keep the Rostrum below the bowl rim.
- Not Meridian: no freight line, no crane.
- Not a museum: statues are lit billboard mounts; the travertine albedo is dark enough to sit in the AAA-2 band.

## 3. The named mechanic and how the art shows it

Mechanic (batch draft 3.1): after each node, each ring's gates rotate by its step (the draft's authored table: ring 1 +24, ring 2 -26, ring 3 +29, ring 4 -31 degrees). A descent link is powered only if a gate overlaps the leaving room's azimuth. The pencil shows the next positions.

Art shows (all driven by game state per frame; spec 8.4 rule 4):

| State | Visual | Source in images |
|---|---|---|
| Gate open | gap in the bronze barrier with lit verdigris jambs, stair visible, link lit as normal route link | green square, hq_mechanic |
| Gate shut | bronze barrier, two sparks, link de-powered dark red | "GATE SHUT" |
| Next step | yellow pencil circle at each ring's next gate azimuth (1 step, 4 with Intel) | yellow circle, hq_overview |
| Held (Breach or Thumbs-Up) | bronze lock plate on the barrier | batch 9, new, ASSUMPTION |
| Rotation | tween between integer-angle tables; the barrier ring turns as a rigid band, 0.9 s step like other HQ steps (spec 6.4) | new |
| Favor | terrace crowd light fill 0 to 5: warm at high, dark at 0 | batch 3.3 |
| VERDICT mark | thumb badge on the marked slice shown on the room sticker | batch 3.2 |
| Grand Stand | emperor's box lit OPEN / NEUTRAL / SEALED | batch 3.4 |

**Conflict flag (A):** the overview image shows the ring panel angles as "gates 100 / 280" (two gates 180 degrees apart). The batch draft gives only the step angles, so the 2-gate 180-degree layout is ASSUMPTION from the image and NOTES (`gates_now`, `gate_w` 9).

## 4. Disagreements between the art and the mechanic draft

| # | Art (images / NOTES) | Mechanic draft | Proposed reconciliation |
|---|---|---|---|
| A1 | 18 rooms: 6 / 5 / 4 / 3 on rings 1-4, plus the Rostrum | 19 nodes in 9 layers: rings 6 / 5 / 4 / 3 (matches) plus the L8 Grand Stand room, plus the Rostrum | The Grand Stand needs a slot not in the art. Put it on the arena rim (a box on the inside edge of ring 4, azimuth facing the camera), not a fifth ring. |
| A2 | rings counted from the outside (ring 1 outer) | same | agree |
| A3 | Rooms are on the far half only (to face the camera) | generator is told to walk the slot list from the far half | agree; a ring with more nodes than far-half slots wraps to the near half, where occlusion (spec 7) and cut-aways handle it |
| A4 | The image panel says "4-step turn" (the cycle repeats every 4 steps) | the draft has no cycle; angle math runs forever | ASSUMPTION: angles reduce mod 360, and the 4-step label is a concept leftover; drop it from the UI |
| A5 | NOTES: the walk along a ring is always open, descent only through gates; "drop taken on a Perfect turn could skip the next fight" | draft does not include this | not used; flag as dropped |
| A6 | Rooms in the image are a mix of nodes per ring with no layer grouping | draft puts 1 or 2 layers on each ring (L1-L2 on ring 1, etc.) | rooms need a layer-ordered azimuth: layer 1 outermost-left to right, then layer 2 |
| A7 | One link from ring 4 to the Rostrum (a straight vertical line) | the Rostrum is reached via the Grand Stand (L8 to L9) | route the last link ring 4 to the Grand Stand to the Rostrum, in a straight line down the stair |
| A8 | The image's gates are on the route links, not drawn as barrier geometry | spec 8.5 landmark needs geometry | build the geometry (section 6) |

## 5. Layer count

**Recommended: 9 layers** (L1-L2 ring 1, L3-L4 ring 2, L5-L6 ring 3, L7 ring 4 with L8 the Grand Stand, L9 the Rostrum), per the batch draft. Reason: four rings need at least two layers on the outer ones for the gate clock to matter, and a 7-layer run (GDD 4.2) would leave one layer per ring and no waiting to catch a gate; D10 allows it. The generator must still accept any layer count (spec 8.4 rule 5); fewer layers drop ring 1 first.

## 6. Landmark and ring layout (kit units, then spec 8.6 scaling)

From NOTES (`roman_preset.PRESET["hq"]`), in kit units:

| Part | Value (kit) | Value after k_units 0.2375 |
|---|---|---|
| Outer wall | r 150, h 46, 40 arcade bays per storey, 4 storeys | r 35.6 BU, h 10.9 BU |
| Terraces (r_out, r_in, floor_z) | (142,116,34), (116,92,25), (92,70,16), (70,50,8) | (33.7, 27.5, 8.1), (27.5, 21.9, 5.9), (21.9, 16.6, 3.8), (16.6, 11.9, 1.9) |
| Arena floor | r < 50 | r < 11.9 BU |
| Gate rings | bronze barrier at each terrace edge, 2 gates, gate_w 9 degrees | gate width at ring 1: 5.3 BU |

Scale (spec 8.6): the lot is a game-given HQ lot, and `k_fit = min(lot_w / kit_w, lot_d / kit_d)`. The wall diameter at k_units is 71 BU against a lot of the order of 32 BU (the Meridian precedent; assumption), so the bowl is likely over 2x too big for the lot; `k_fit` would shrink it to about 0.45. At that scale a ring-1 room is about 1.5 BU wide. Rooms keep a pixel target, so the camera comes in closer rather than the rooms shrinking on screen. This needs a designer or art-director look (Q1).

Room box: the kit's cutaway box (about 3.3 x 1.9 x 2.4 BU after k_units), standing on the terrace against the riser behind.

Fills its lot (spec 8.6 rule 2): the bowl's outer wall is the lot edge; the slack goes to an apron of piazza and the triumph-gate toll road. Blocks touch the lot edge (spec 8.2); no belt.

Light (spec 8.3): landmark at 1.5-2.0x local background in median luma, by light not exposure:
- teal verdigris seam strips on every terrace edge (visible in the image);
- warm uplights on the 4 arcade storeys (travertine, so warm against the cool teal);
- cornice coves with a single neon tube per storey;
- the Rostrum core with lit rings and a laurel holo ring;
- a rim light linked to the landmark only.

Known risk: the image's teal rings already read very bright and flat. Watch the ratio above 2.0 (a warning, never a fail, spec 12.2).

## 7. Plan and room slots

Slots are generated per game graph (spec 8.4). The table below is the **default slot set for the 9-layer template**, not content. Ring azimuths are of the far half, 0 degrees = toward the camera's right. Lit state per spec 12.x is the state the plate must show.

| Slot id | Ring | Node type (default) | Lit state (golden OVERVIEW) |
|---|---|---|---|
| r1_01 | 1 | Router | walked (lime ring) |
| r1_02 | 1 | Router | current |
| r1_03 | 1 | Router | option 1 (orange) |
| r1_04 | 1 | Terminal | option 2 (orange) |
| r1_05 | 1 | Router | ahead (white) |
| r1_06 | 1 | Router | ahead |
| r2_01 | 2 | Router | ahead |
| r2_02 | 2 | Mainframe | ahead |
| r2_03 | 2 | Elite | ahead |
| r2_04 | 2 | Router | ahead |
| r2_05 | 2 | Router | ahead |
| r3_01 | 3 | Router | ahead |
| r3_02 | 3 | Rest | ahead |
| r3_03 | 3 | Elite | ahead |
| r3_04 | 3 | Cache | ahead |
| r4_01 | 4 | Router | ahead |
| r4_02 | 4 | Rest | ahead |
| r4_03 | 4 | Elite | ahead |
| gs_01 | arena rim | Grand Stand (puzzle) | ahead |
| ros_01 | arena floor | Rostrum (boss, TARGET) | target (red pencil) |

Count: 20 slots, against 19 nodes in the batch draft (6+5+4+3 = 18 rooms, plus the Grand Stand and the Rostrum = 20; the draft's own text says "19 nodes" and its layer table sums to 3+3+3+2+2+2+2+1+1 = 19, so one ring-room is not placed in its layer table; flagged, A9, Q2). The ring totals above follow the art (6/5/4/3); the layer table in the draft gives ring 1 six, ring 2 five, ring 3 four, ring 4 three, and the Grand Stand L8 as one node, which makes 19 only if ring 4's three rooms are L7 (2) and L8 (1), meaning L8 is a ring-4 room and not a separate Grand Stand. The art needs one decision (Q2).

State language follows `HK/states.py` (spec 8.1): walked lime #D4FF00, option orange, ahead white, past grey.

## 8. Camera and orbit (spec 6.4)

Kit values from the corp preset (assumptions, not in the supplied sources except the preset ranges in the identity):

| Key | Default (assumption) | Basis |
|---|---|---|
| OVERVIEW pitch / lens | 40 / 36 | the supplied overview appears about 40 deg high 3/4; confirm |
| OVERVIEW yaw | south, fixed; the far half faces the camera | NOTES `hq.cam` |
| DECISION pitch_lo-hi | 14-24 across layers (Halcyon-like ramp) | assumption |
| lens | 30 | kit default |
| `dmin` | 110 kit, times `k_units` and `k_fit` | like Orbital's round podium |
| fill | 0.62 / 0.66 | assumption |
| hover | 22 %, 3 degrees, x 0.96 | kit |
| step | 0.9 s; a ring drop is 1.6 s with a 45 degree swing | like the corner stair |

DECISION azimuth is the mean of the look vectors of the distinct room normals; on a round bowl every room faces the center, so rooms on one ring spread across azimuths. Rule: for a ring walk the camera sits on the outside of the current room's ring looking inward; for a drop it swings to the gate azimuth. Needs a check that a ring-1 room on the near half is not hidden by the wall (occlusion rule, spec 7, will cut the wall to a 2-floor stub, 3.8 BU).

Entrance beat (spec 6.4, 6.0-6.5 s, ends on OVERVIEW): half-orbit from the triumph-gate toll road over the rim, then dropping to the OVERVIEW. ASSUMPTION; it is hand-set today for every corp.

## 9. Shot list (all at 2560 x 1440 final; 1280 x 720 test)

| Shot | Camera | Framing | States shown |
|---|---|---|---|
| H_OVERVIEW | spec 6.4 OVERVIEW, fixed south, pitch about 40 | all four rings and the Rostrum within the usable frame (fill 0.95 / 0.90); the bowl's far half in focus | the batch-draft route state: current ring 1 room 2, options 1-2 lit, all others ahead, step counter 3, one gate open in ring 1, yellow next-step circle on ring 3, TARGET on the Rostrum |
| H_DECISION | decision rule, ring 1 walking | current room + its options on one ring face, front and centre (`centre_current`) | current lime, options orange 1 and 2, one drop link powered, one de-powered, telegraph one step ahead |
| H_DECISION_DROP | same, at a gate azimuth | the barrier gap in the center, the stair down visible | gate open, ring 2 below visible as ghost rooms |
| H_HOVER | hover pull 22 %, 3 degrees | the hovered branch from the current room to the Rostrum lit; the rest at power-cut x 0.20, 70 % desaturated | spec 9.4 grade; hover frames exempt from the value band |
| H_FAVOR_HIGH / H_FAVOR_LOW | OVERVIEW | terrace crowd light at Favor 5 and 0 | art test of the Favor fill |
| H_GRAND_STAND | DECISION on gs_01 | the emperor's box and the Rostrum behind | OPEN / NEUTRAL / SEALED (3 variants) |
| H_ENTRANCE | beat strip, 8 frames | the half-orbit | none |

## 10. States and lighting

- State rings and link colors per spec 9.2 (lime, orange, white dashed, grey).
- Active-room key (spec 8.3 rule 4): a key from the camera side plus a rim from behind, re-aimed per frame.
- Barrier: bronze, warm; its sparks when shut are 2 small emissive points, 0 to 1 flicker.
- Open gate: verdigris jambs (#29DBA6), 2.5x the arcade trim emission (assumption).
- Rostrum core: lit rings; phase 2 (boss) shifts arcade openings from verdigris to gilt (boss_wheel_ideas, batch 9).
- Hover cut: spec 9.4 as written; no separate 3D cut.
- Hue discipline: verdigris never on a Terminal edge or a gain chip (identity.md clash check); in the HQ the teal rings are close to NET_CYAN (dE 48); keep the ring emission distinct from the route's cyan links.

## 11. Dressing and signage

- The dense district to the walls (spec 8.2): insulae with colonnade shop fronts, campanili (25 % of second-row towers), the aqueduct line carrying the data stream, the piazza as the apron, triumph gates as the toll road entries.
- Hero sign (spec 9.1) per route "column": ASSUMPTION it maps to the rooms' arcade bay; one blade or wall sign in the district pair's hue inside the bay. LVDI LIVE and BE A CLIENT style boards on tall roofs.
- Statues: rooftop bronze on billboard mounts, uplit; eyes turn red at FLAGGED Heat (identity.md), two arena searchlights sweep.
- Seating: lit window dots on the terraces for the crowd; density follows Favor.
- Reveal tiers (spec 5.2b): neon shape for signs beyond 790 BU, full sign at 466-216, flicker at 216-152.
- `density.falloff` (spec 13.1 rule 3): the buildings near the bowl stay, with a quiet apron of dimmed windows and 20 % dark blocks, so the bowl leads.
- Known look gap: fog density 0.005 in the district render; use about 0.008 so beams show (NOTES).

## 12. Mapping the game graph onto the landmark (spec 8.4)

1. Slots are ordered by ring (outer to inner), then azimuth along the far half, then wrap to the near half.
2. The run graph's layers are assigned to rings in layer order: layers fill ring 1 first, two layers per ring for the 9-layer template, then ring 2, and so on. The Grand Stand and the Rostrum take the arena rim and floor.
3. A descent edge is placed through the gate anchor of the leaving ring; an along-ring edge runs flat on the terrace. The type is a hint only.
4. Mechanics come in per frame: `step_count`, `gate_angles_now`, `gate_angles_next`, `gate_w`, per link `powered` and `opens_in_steps`, per room `ring`, `azimuth`, `state`, `node_type`, `held_rings`, `favor`, `verdict_marked`, `grand_stand_state`, `rostrum_phase`, `telegraph_depth` (batch draft 9). The art visualizes them and decides nothing.
5. The tools generate no nodes, edges, kinds or gate schedules.
6. A graph with fewer layers than the template uses fewer rooms per ring from the outermost inward; a longer one adds rooms to the same rings (more azimuth slots; the near half is allowed).

## 13. Build order

1. Landmark module `corps/aurelian/landmark.py` with `build(K)`; slots on demand; barrier geometry, gate apertures, stairs; port the kit generators (`insula`, `campanile`, `piazza`, `triumph_arch`, `aqueduct`) as a key-landmark and fabric set (spec 8.8 later).
2. Gate rotation as a rigid-band rotation parameterized by angle, no baked animation.
3. Preset `corps/aurelian/preset.py`: AAA-2 deep copy plus the hq block, `variance_pref` LOW (assumption: civic order, like Halcyon).
4. Rooms and state ladder via the shared kit `states`.
5. Lighting by the 8.3 rule, then the value and ratio test frames (spec 12) before any final.
6. Camera beats (the entrance), HOVER grade, then goldens.
7. `k_fit` against a game HQ lot, and the canonical-silhouette check (spec 8.6b) against the full-city landmark. NOTE: the city still uses the built-in Aurelian landmark (spec 8.6c), which is not the Circus; the Circus becomes canonical on designer approval, and the city model must follow.

## 14. Acceptance checks (spec 12)

| Check | Rule for Aurelian |
|---|---|
| 12.1 value band | median 0.14 +- 0.03 (warn 0.09-0.11, 0.17-0.19); 25-40 % under 0.10; at most 2.5 % over 0.85; hover and flash frames exempt |
| 12.2 landmark ratio | 1.5-2.0 pass; above 2.0 warns only; below 1.5 fails; indices 1, 5, 6 over 0, 2 in the box grown 35 % |
| 12.3 determinism | derive JSON, placement lists and the gate-angle table byte-identical across two runs and a fresh process; seed sensitivity |
| 12.4 | no building footprint meets the bowl footprint or its apron; the toll road does not cross buildings; no foreground dressing in front of a room opening |
| 12.5 beams | the arena searchlights obey: no spot under 10 degrees linked to media, blend >= 0.8, no shadow |
| 12.6 | room >= 46 px tall at OVERVIEW 1080p; available rooms <= 8 % blocked; occlusion never hides (opacity >= 0.18); 1280 x 720 stickers >= 24 px; frame continuity on the entrance beat |
| 12.7 composition | R-FOCUS-1, R-CALM-1/2 (detail CV, calm tiles), R-HUE (corp HQ views exempt), R-REP-1 (40 arcade bays repeat; guard with `max_same_module_adjacent` 2 and seeded tone jitter) |
| 8.6 | landmark covers at least 90 % of the inset lot along its fitting axis and never crosses the lot edge |
| 8.6b | silhouette IoU >= 0.85 (provisional) at 320 px against the full-city view |
| Gate parity (new, proposed) | the angle the shader draws equals the integer table value for that step; the telegraph equals the next step's powered check |

Risk to test early: repetition of 40 identical bays (R-REP-1) and the flat, bright teal rings against the 2x ratio.

## 15. Golden plates (D8 hand-off: PNG + values JSON per plate with median, % under 0.10, landmark ratio, camera params)

| Plate | Frame | Notes |
|---|---|---|
| `aur_overview_s3` | H_OVERVIEW, step 3 | with and without UI; thumb at 320 px |
| `aur_decision_walk` | H_DECISION | |
| `aur_decision_drop` | H_DECISION_DROP | |
| `aur_hover_branch` | H_HOVER | exempt from value band; records the grade presets |
| `aur_favor_hi`, `aur_favor_lo` | OVERVIEW | tolerance on the crowd fill |
| `aur_grandstand_{open,neutral,sealed}` | DECISION | |
| `aur_gates_t0..t3` | plan-view strip of 4 steps | gate-angle parity |
| `aur_city_silhouette` | full-city map camera crop | for 8.6b IoU |
| `aur_entrance_strip` | 8 frames | continuity check |

Tolerances: ASSUMPTION, those of spec 12.3 (mean absolute difference <= 1/255 on a 320 x 180 downsample, max <= 8/255) for GPU finals; the build session reports drift.

Q: The overview's bowl (r about 35.6 BU at k_units) is likely larger than an HQ lot (Meridian's is about 32 BU square). Do we accept a `k_fit` near 0.45 (and a closer camera), or pull the bowl in to r 24 BU and lose arcade bays?
Q: The mechanic draft's layer table sums to 19 nodes, the art to 18 rooms plus the Rostrum plus a Grand Stand (20). Is the Grand Stand a separate node on the arena rim, or the single ring-4 room of L8?
Q: Should the city's built-in Aurelian landmark be replaced by the Circus (canonical, spec 8.6b), and by whom?
Q: The art shows a "4-step turn" cycle; the mechanic draft has no cycle. Drop the label, or make the gate table repeat every 4 steps?
Q: May the 4-step gate lookahead stay as the default art (the yellow pencil shows one step now), with Intel to 4, as the batch draft proposes?
Q: Is `variance_pref` LOW right for Aurelian, or MEDIUM for the Roman piazza clutter?
