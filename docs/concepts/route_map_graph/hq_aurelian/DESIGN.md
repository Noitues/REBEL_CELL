# Aurelian Concord HQ: THE CIRCUS AURELIUS (design pass, 2026-10-18)

Status: **concept B approved (designer, 2026-10-18); v1 finals done (13.6); AD round 3 built: route outside-in, Roman arcade, occlusion fix, ENTRY (section 14); v2 finals done.**
Builds on the draft head start `D:/Godot/rebel_cell/docs/handoff/netrun_art/batch/aurelian_design/DESIGN.md`
(unverified, not approved). Where this file and the draft differ, this file wins. Section 10 lists the differences.

Sources:
- `new_corps/roman/identity.md`;
- the canonical full-city colosseum (`city_all_corps/scripts/landmarks.py` `aurelian()`, `city_preset.AURELIAN_LM`);
- PIPELINE_SPEC §6.4, §7, §8 (8.3, 8.4, 8.5, 8.6, 8.6b, 8.6c);
- the Meridian v3 pass (`hq_meridian_v3/`), as the model to follow;
- designer rulings D10 (an HQ run may have more than 7 layers, each one unique) and A3 (the Central Server is
  **THE CONCORDAT VAULT**).

## 1. The rule that shapes everything: the city colosseum is canonical (spec 8.6b)

The HQ netrun view must match the full-city landmark. Therefore:
- this pass does **not** redesign the silhouette;
- all three concepts in section 9 use the *same* colosseum;
- they differ only in **where the route lives inside it**.

`scripts/aurelian_landmark.py` `canonical()` is a 1:1 port of the built-in `aurelian()`: same numbers, same faces. It
serves both the city (`build(ctx)`, the 8.6c hook) and the HQ. The HQ adds only:
- route slots and cutaway rooms;
- doorway bays (concept B, section 4.3);
- the state and TARGET visuals;
- close-range detail tiers (spec 5.2b);
- the HQ light rig (section 6).

**The draft's "four turning seating rings with bronze gate barriers" is not used.** Both the rings and the barriers
change the canonical massing. The mechanic is not approved either (section 8).

## 2. Massing (canonical; city BU, 1 floor = 1.9 BU, x east, y north)

| Element | Canonical value | Notes |
|---|---|---|
| Bowl | ellipse, semi-major A 31 (x), minor 24.8 (ratio 0.8), 64 segments | the long axis runs E-W |
| Outer colonnade | 3 tiers × 5.0 BU; **60 round columns** (r 0.62) on the outer ellipse; per tier a base band (0.25) and an entablature (0.7) | the columns stand clear of the wall |
| Loggia wall | recessed 1.7 BU behind the columns, lit gilt arches (`wc` 1.0/0.76/0.42, `wl` 0.8) | at night the columns read dark against a lit loggia |
| Attic | solid band, z 15-18, faint windows (`wl` 0.25); a cap ring and a **gilt neon crown ring** at z 18.3 | the rim |
| Cavea | **4 seating rings × 4 stepped terraces** (16 terraces), edge radii A × (0.98, 0.86, 0.72, 0.60, 0.48), ring tops at z 18 / 15 / 10.5 / 6.5, arena at z 3; a gilt neon line on each ring's inner edge | alternating terrace tones |
| Arena | lit sand disc (emission 0.35 warm), r 14.9 × 11.9, z 0-3 | |
| The Rostrum | a porphyry plinth (r 5, z 3-4.2), a **tholos of 12 columns** (r 4.2, z 4.2-7.5) with an entablature, a core column (r 1.6) to z 22 with 4 gilt rings, a **laurel holo ring** (r 7, z 25, 16 leaves), a gilt lamp at z 22-23.4 | the crown and beam origin (0, 0, 26) |
| Campanili | 4 on the diagonals, r 2.3, 8 lit drums to about z 31.6, flat crowns with a gilt ring and lantern | the tallest masses; the footprint is the `LANDMARK_FP` ellipse, 36 × 30 |
| Searchlights | 2 arena floods (warm 2.4e6 W, cone 40; gilt 1.4e6 W, cone 38) | they satisfy 12.5: cone above 10°, blend ≥ 0.8 to set, no shadow |

Height ladder:
- the city near the lot: about 34 BU median (`bld_med` aurelian);
- the colosseum rim: 18 BU;
- the Rostrum column: 22-26 BU;
- the campanili: 31.6 BU.

The landmark is a **low, wide bowl** that the city looks down into. That is its identity against Halcyon's pyramid,
Orbital's needle, Solace's helix and Meridian's Π.

Scale (spec 8.6): the model is authored in city units, so the city needs no `k_units`. `k_fit` is 1.0 on the concept
city, because the circus and its campanili are the `LANDMARK_FP` ellipse. The HQ kit scenes run in kit units
(1 storey = 8 BU), so `build_hq` wraps K with the Meridian `place()` proxy at k = 1 / 0.2375. That is the same model,
scaled up.

Colour note: in the city, the neon on the landmark is **gilt** (`DISTRICTS.aurelian.sec`), not verdigris. The draft's
teal rings come from an older concept render. The canonical colours are kept (Q1).

## 3. The Central Server: THE CONCORDAT VAULT

The vault is **the Rostrum's tholos**: the 12-column ring temple on the porphyry plinth at the centre of the arena.

| Part | Role |
|---|---|
| The tholos | the vault room: open on all sides, so the TARGET reads from any azimuth |
| The core column | the server core: its 4 gilt rings are the lit "server rings" |
| The laurel ring above | the TARGET's crown and the hero beam source (the city crown, (0, 0, 26)) |

No new mass is needed: the canonical model already has a temple at the bottom of the bowl. HQ-only additions:
- interior light in the tholos;
- an inscribed band on the entablature, `CONCORDAT · VAVLT` (inscription capitals, identity.md);
- the red pencil TARGET ring on the plinth.

Concept C moves the vault under the arena (section 9).

## 4. Slots for the game graph (spec 8.4; D10)

### 4.1 Rules

1. Topology always comes from the game graph. `slots(layers, concept)` generates slots **on demand** for any layer
   count: at least 7 layers, and more under D10. The tools make no nodes, edges or kinds.
   `fixture_edges()` is mock data for concept renders only.
2. A **level** is an arc of slots on one part of the landmark. Slots run **left to right as seen from the OVERVIEW**:
   - the south (near) face runs west to east, t from 205° to 335°;
   - the north (far) cavea runs west to east through north, t from 160° to 20°.

   The walk direction alternates per level (boustrophedon), so every level change happens at an end of the arc.
3. **Layer to level** (`level_of`): route layers are every layer except the last, which is the vault.
   - With *n* route layers and *L* levels, when n ≥ L: `level = floor(i · L / n)`. Consecutive layers share a level
     and walk along it.
   - When n < L: `level = round(i · (L − 1) / (n − 1))`. The run spreads from the first level to the last, so it
     always starts at the entry and ends at the vault.
4. Within a level, each layer takes a contiguous sub-arc. Its nodes are spread evenly, with one empty slot between
   layer groups, so the layers read as separate steps (D10: every layer is unique).
5. Slot record: `layer, node, level, kind, t, pos` (the front-centre at floor level), `normal`, `size`, `tier`.
   - The room is the kit cutaway at city scale, 3.3 w × 1.9 h × 2.4 d. Loggia rooms are 3.4 tall to fill their arch bay; attic rooms 2.9 (their band); cavea rooms are 3.5-tall loges (section 13.2), all sized to the 46 px OVERVIEW target.
   - The box goes *behind* the front face: into the loggia wall, the attic or the terrace riser.

   No room crosses the outer silhouette. The loges stand up to about 0.6 BU proud of the seats behind them, inside the bowl and level with the rim (section 13.2).

### 4.2 Recommended levels (concept B) and their capacity

| # | Level | Where | z (floor) | Faces | Arc | Capacity (4.2 BU per slot) |
|---|---|---|---|---|---|---|
| 1-3 | T1, T2, T3 | outer loggia tiers, south arc | 0.6 / 5.6 / 10.6 | out (south) | 62 BU | 14 each |
| 4 | AT | the attic band, south arc | 15.3 | out | 66 BU | 15 |
| 5-8 | R1-R4 | the seating rings, north arc | 17.3 / 13.8 / 9.4 / 5.6 | in (south) | 65 / 56 / 46 / 38 BU | 15 / 13 / 11 / 9 |
| vault | VAULT | the Rostrum tholos | 4.2 | all | - | 1 |

Layer counts:
- 9 route layers (a 10-layer run, as in the thumbnails) map to levels 1,1,2,3,4,5,6,7,8.
- A 7-layer GDD run maps to 1,2,4,5,7,8 (`level_of`).
- With two layers per level, the generator holds **16 route layers + the vault** with at most 4 nodes each, and every
  level stays inside its arc capacity.
- Beyond that (more than 2 layers per level), the cavea arcs widen symmetrically onto the near half. The near
  colosseum wall is compound geometry and is never cut (spec 7.1 rule 3), so near-half cavea slots are seen only
  from DECISION cameras. **Accepted for now (designer default, 2026-10-18):** runs over 16 route layers spill onto the near half, which the OVERVIEW does not see.

### 4.3 Link geometry by step class (spec 8.4 rule 3; the type is a hint only)

| Step | Geometry |
|---|---|
| Same level | a lit run along the terrace or the loggia floor, following the ellipse |
| Loggia tier up (T1→T2→T3→AT) | an external stair in the end bays (the colosseum's stair vomitoria), drawn as a rising link at the arc's end |
| AT → R1 (the **crossing**) | along the **rim walk** on the attic cap at z 18.6, round the end of the ellipse (the short way), then down into ring 1. The one long link: the route turns the circus |
| Ring down (R1→R4) | a **vomitorium** stair cut through the riser, a falling link |
| R4 → vault | a straight stair across the arena sand to the tholos |

Doorway bays: a loggia room needs its arch clear (spec 12.4: no dressing in front of an opening). Its own bay (about
±2.2 BU) **drops its column**. That is 1-2 of the 60 columns per room, invisible at 320 px, so the 8.6b IoU is
unaffected. The bay frame gets the room's state light. The city build passes no open bays, so the city keeps all 60
columns.

## 5. Mapping notes for the game sessions (places only; art makes no rule)

The bowl offers natural places for a mechanic hook if the game sessions want one: the 16 terraces, the vomitoria, the
tholos, the arena floor and the four campanili. Art visualises game state per frame and decides nothing (8.4 rule 4).
Any mechanic panel in a render is a **neutral placeholder** (Meridian's `hq_mechui.py` pattern).

## 6. Landmark lighting (the landmark ≈ 2× its local background, spec 8.3)

Target: landmark (pass indices 1, 5, 6) median ≈ 2 × the local background (0, 2) in the box grown by 35 %. That is
1.8-2.2: under 1.5 fails, over 2.0 only warns. The frame value band is 0.14 ± 0.03. The light comes from the
landmark, not from exposure.

The look: the colosseum at night, with **columns dark against a lit loggia**:

| Light | What | Why |
|---|---|---|
| Loggia glow | the recessed wall's lit arches (canonical `wl` 0.8, warm 1.0/0.76/0.42), plus a warm cove strip under each entablature | the 60 columns read as dark bars against warm light: the colosseum signature at any zoom |
| Travertine key | low warm uplights at the base band, grazing the columns (sodium-white, light-linked to the landmark) | lifts the stone without raising exposure; the travertine albedo (0.86) is high, so the uplights stay low and grazing |
| Gilt lines | the attic crown ring and the 4 ring-edge lines (canonical NEON, gilt) | draws the stepped cavea from above |
| Cavea fill | two soft area lights over the far rim, aimed down the far half | the route rings face the camera and must read; the near half stays darker |
| Arena | the lit sand (canonical 0.35) and the 2 canonical searchlights | the pool of light at the bottom that the eye falls into |
| The vault | the tholos interior light, the 4 lit rings and the laurel ring (gilt × 1.2), plus the beam | the brightest point; the TARGET |
| Campanili | lit drums (canonical `wl` 0.8) and lantern boxes | they frame the bowl at the 4 diagonals |
| Rim | two area lights behind, light-linked to the landmark only (as in Meridian v3) | separates the attic edge from the city behind |

Watch:
- The travertine is the brightest albedo of any HQ. The over-0.85 share (2.5 % at most) is the first risk.
  - Fix: darken the HQ shader's tone jitter, not the canonical colour.
- The gilt lines sit near the route's option orange. The option links must stay brighter and thicker than the
  gilt lines (Q2).
- R-REP-1: 60 identical columns. They are guarded by seeded tone jitter, with `max_same_module_adjacent` 2 on the
  loggia arches.

## 7. Cameras (spec 6.4; city BU, ×4.21 for kit units)

| Key | Value | Notes |
|---|---|---|
| OVERVIEW | bearing 200° (SSW), pitch 40, lens 36, distance about 116 BU (488 kit), target (0, 2, 7); fill 0.95 / 0.90 | sees both route faces at once: the south loggia (near, facing the camera) and the north cavea (far, facing the camera over the near rim). The two campanili in the frame bracket the bowl |
| DECISION, loggia / attic | camera outside, azimuth along the room's outward normal; **revised in 13.2:** pitch `lerp(30, 34)` across T1-AT, lens 42, `dmin` 260 kit (62 BU), above the roofs across the boulevard | the city blocks in front are flattened or ghosted by the spec 7 rule; the columns are compound geometry and never cut, hence the doorway bays |
| DECISION, cavea | camera **inside the bowl**, above the arena on the room's inward normal; pitch `lerp(26, 36)` R1-R4; lens 30; `dmin` 32 BU | deeper rings get steeper pitch; the near rim is behind the camera, so nothing occludes |
| DECISION, vault | the OVERVIEW bearing, pitch 38, 0.6 × the OVERVIEW distance | frames the tholos, the column and the laurel ring |
| DECISION azimuth | the spec rule (the mean of the distinct room normals). **Exception:** when the mean is degenerate (\|mean\| < 0.3, as at the AT→R1 crossing, where the normals are opposite), use the options' normal | proposal; flagged |
| Step | 0.9 s along a level; 1.6 s per level change; the AT→R1 crossing 2.4 s, an orbit over the rim (the "turn of the circus") | proposal |
| HOVER | kit: a 22 % pull, 3°, × 0.96; the hovered branch lit, the rest power-cut × 0.20 and 70 % desaturated (spec 9.4) | exempt from the value band |
| Entrance beat | 6.0-6.5 s: from the boulevard at street level, a half-orbit rising past the colonnade and over the attic, ending on OVERVIEW; route and UI drawn in over the last 0.9 s | hand-set, as for every corp |

## 8. The draft's mechanic

The draft carries a batch mechanic: TURNING GATES, VERDICT, Favor, the Grand Stand. **It is not approved, and art
invents none.**

| Draft element | What this pass does with it |
|---|---|
| Gate barriers and rotating rings | not built: they would change the canonical massing |
| Favor crowd fill, Grand Stand box | not built |
| The mechanic panel in the renders | a neutral placeholder |

If the game sessions adopt a mechanic, its visuals go on the places in section 5, driven per frame by game state.

## 9. The three concepts (`concepts_sheet.jpg`) and the recommendation

All three are the same canonical colosseum (quick Eevee, mock 10-layer route, 28 nodes).

| | Concept | Verdict |
|---|---|---|
| A | **CAVEA DESCENT**: the four seating rings (far half), then a ring of arena gates; the vault in the tholos | Clean and readable, but it uses only the inside. The **columns carry no route**, so the canonical colonnade is dressing. Its 5 levels are crowded: a 10-layer run puts 2 layers on every level. |
| **B** | **LOGGIA AND CAVEA**: up the outer colonnade (3 loggia tiers and the attic, near face), round the rim walk, down the four seating rings, ending at the vault in the tholos | **Recommended.** |
| C | **HYPOGEUM**: two seating rings, then down through a cut-open arena floor into three underground rings; the vault under the column | The strongest "descent" story, but it needs pitch 54 to see into the pit, and that flattens the colonnade out of the OVERVIEW. It cuts the canonical arena (the city has a sand floor). The hypogeum rooms are open-top cells, a new room kit. The pit is the darkest part of the frame, the opposite of the 2× rule. |

Why B:
1. **It uses the whole canonical model.** The columns, the stepped tiers, the rim and the temple at the bottom all
   carry route, so the HQ *is* the city landmark in use (8.6b), not a model with a route laid on top.
2. **One camera sees both faces.** The near loggia faces out toward the camera, and the far cavea faces in toward
   the same camera over the near rim. The OVERVIEW holds the whole run without orbiting.
3. **The route explains itself.** It climbs the outside, turns the circus on the rim walk, descends the seats and
   ends in the arena. That is the spectator's path into the games, and the single long link (the crossing) is the
   memorable beat.
4. **The most capacity.** 8 levels with 9-15 slots each: 16 route layers at 2 layers per level, so D10's long runs fit
   without touching the near half.
5. **The lighting rule works for it.** Lit loggia rooms sit between dark columns, and lit cavea rooms sit on the gilt
   lines.

Risks of B, to test first:
- The near-face loggia rooms are small at the OVERVIEW (thumbnail: about 15 px tall at 960 × 540, so about 30 px at 1080p,
  under the 46 px target). Fix options: a closer OVERVIEW (fill to the bowl, not the campanili), or loggia rooms two bays wide.
- The doorway bays must not show as gaps at city zoom.
- The 2.4 s crossing beat.

## 10. Where this differs from the draft

| Draft | This pass |
|---|---|
| THE ROSTRUM is the Central Server, THE GRAND STAND the hub | **THE CONCORDAT VAULT** (A3) in the Rostrum's tholos; no Grand Stand node (that came from the mechanic) |
| A kit-scale bowl (r 150 kit), with the `k_fit` 0.45 worry (draft Q1) | the canonical city-unit model; `k_fit` 1.0; the HQ scales it up to kit units |
| Four flat teal terraces with bronze gate rings | the canonical 16 stepped terraces with gilt lines; no barriers |
| A fixed 9-layer, 20-slot table | slots generated for any layer count (section 4) |
| A "replace the city model with the Circus" open question (draft Q3) | moot: the city model is canonical and the HQ follows it |
| The camera from the south, pitch 40 | kept (bearing 200, pitch 40), plus the cavea DECISION from inside the bowl |

## 11. Open questions for the designer (round 1; all four settled 2026-10-18, see 13.1)

1. **Gilt or verdigris neon?** The canonical landmark's neon is gilt, and the corp hue verdigris appears nowhere on
   it. Keep gilt (default), or change the city model's crown and ring lines to verdigris? That would be a city change,
   and the HQ follows.
2. **Gilt next to option orange.** Default: the option links are drawn brighter and thicker than the gilt lines.
   Accept, or dim the gilt lines in the HQ's DECISION frames?
3. **Runs of more than 16 route layers.** With more than 2 layers per level, the cavea arcs spill onto the near half,
   which the OVERVIEW cannot see (the colosseum wall is never cut). Accept DECISION-only visibility there, or add a
   third layer group per level?
4. **Doorway bays.** A loggia room drops 1-2 columns in its bay (HQ only). Accept, or keep every column and frame the
   room between two columns (it would be about 1.7 BU clear, too narrow for the cutaway)?

## 12. Files

| File | What |
|---|---|
| `DESIGN.md` | this file |
| `concepts_sheet.jpg` | the three thumbnails, 1278 × 880 |
| `scripts/aurelian_landmark.py` | the standalone landmark module: `canonical()`, the city `build(ctx)` (8.6c), `slots()`, `level_of()`, `fixture_edges()` (mock), `state_colour()` (from the shared `hq_kit.states`); `build_hq` (the HQ-kit hook: the canonical model in kit units, doorway bays, room cuts, lit loggia arches, the vault core, the light rig) |
| `scripts/thumbs.py` | the Eevee massing thumbnails (city-primitive shim, a seeded stand-in city, mock route) |
| `scripts/concepts_sheet.py` | the contact sheet |
| `scripts/hq_preset.py`, `hq_graph.py`, `hq_build.py`, `hq_mechui.py` | the corp modules for the HQ engine: preset (palette, light rig, city, cameras, post), the slots + MOCK graph + camera rule + stills, the build hook, the neutral mechanic UI |
| `scripts/aur_env.py`, `hq_scene.py`, `hq_run.py` | the engine runs **in place** from `hq_meridian_v3/scripts` (no copies): `aur_env` preloads the corp modules and the shared kit (`hq_meridian/scripts/hq_kit`); `hq_scene.py` is the Blender entry; `hq_run.py` runs px / cams / stills / post |
| `scripts/test_sheet.py`, `test_sheet.jpg` | the test frames + values, 1280 × 802 |

Rebuild (from `scripts/`):

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python thumbs.py -- D:/rc_scratch/aurelian/thumbs A,B,C
python concepts_sheet.py D:/rc_scratch/aurelian/thumbs
python hq_run.py px                       # the OVERVIEW room sizes against 46 px
python hq_run.py stills eevee             # layout preview, no GPU lock
python hq_run.py stills test              # Cycles test (takes and releases the GPU lock, owner "aurelian")
python test_sheet.py ../scratch/test ../test_sheet.jpg
```

## 13. Round 2: concept B built and tested (2026-10-18)

### 13.1 Designer defaults (round 1 questions)

| Q | Ruling | Done |
|---|---|---|
| 1 | Keep the gilt neon; the city model is unchanged | the canonical colours; verdigris is used only as rim *light*, never as paint |
| 2 | Dim the gilt lines next to the orange option links | the gilt lines are their own object, at × 0.45 in every DECISION / HOVER frame (zoom > 0.5; `GILT_DIM_DECISION`) |
| 3 | Over 16 route layers spill onto the near half; the OVERVIEW not seeing them is accepted for now | noted in 4.2 |
| 4 | Dropping 1-2 columns at a loggia room's bay is fine (HQ only) | `bays_for()`: 12 bays open in the test (12 loggia rooms) |

### 13.2 What the build changed against round 1

1. **Room size check first** (`hq_run.py px`, OVERVIEW at 1920 × 1080, target 46 px tall). With the closer bowl framing
   (the OVERVIEW frames the colonnade base and the rim all round plus the laurel crown, not the campanili tops), the
   near-colonnade rooms **pass as designed**: T1 46.3-48.6, T2 49.7-51.7, T3 52.2-55.4 px. Two-bay rooms were not
   needed. The other levels failed with the kit's 1.9-tall room (attic 31-33, cavea 29-34 px), so:
   - **attic rooms** fill their band: 2.9 tall (47.4-50.1 px);
   - **cavea rooms are loges**: the floor flush with the next ring's top, the opening in the ring-edge riser, cut
     2.4 BU back into the seats, 3.5 tall, the roof at most about 0.6 BU proud of the seats behind (R1 50.5-53.4,
     R2 48.7-51.5, R3 47.6-49.2, R4 46.3-47.3 px); the vault 46 px. **Every room passes.**
   - OVERVIEW: yaw 20 (camera SSW), **pitch 36** (was 40), lens 36, fill 0.97 / 0.94, distance 465 kit (110 BU).
2. **The loggia DECISION camera** (was pitch 14-22, `dmin` 135 kit): the city across the street is tall (the city
   looks down into the circus), so a low camera at 135 kit sat *inside* the blocks (a black frame in the Eevee
   check). Now pitch **30-34**, `dmin_loggia` **260 kit**, lens **42**: above the roofs, looking down onto the
   colonnade; the occlusion rule flattens the blocks in the cone.
3. **A boulevard round the circus**: downtown `street0` 40 kit (9.5 BU). This is a street, not a belt (the blocks still
   face it all round), but it is wider than the 6 BU apron alone. Flagged (Q5).
4. **The room cut**: every face of the canonical model is clipped against the room volumes (`Cutter`: a convex
   polygon minus oriented boxes, Sutherland-Hodgman), so the openings are clean holes in the loggia wall, the attic and
   the seats. The silhouette is untouched.
5. **The lit loggia**: an emissive round-headed arch panel in each of the 60 bays × 3 tiers, just proud of the recessed
   wall (the city shader's lit arches made explicit), with a fixed per-bay tone pattern against R-REP-1; a warm cove
   line under each entablature.
6. **THE CONCORDAT VAULT**: a server core in the tholos (state-driven emission: plinth disc, 5 rings round the core
   column, 6 racks), the gilt inscription band on the entablature, the kit's room light, a front key spot.
7. **The rig** (kit units; `light` in the preset): the two canonical searchlights (× 0.006 of the city power × k²),
   24 base uplights grazing the colonnade, two cavea fills over the near rim, the vault key, two rim lights behind
   (verdigris and warm) light-linked to the compound only, the beam from the laurel crown.
8. **Exposure**: the corp's post exposure is 1.6 with no zoom fall-off (Meridian: 2.85 × (1 − 0.55 zoom)). The
   travertine is the brightest HQ albedo, so the frame median is set by exposure and the landmark ratio by light.

### 13.3 Test values (Cycles, 1280 × 720, 32 spp; `scratch/test/values.json`; 4 frames in one locked batch of 3.5 min, 207 s)

| Shot | median (0.14 ± 0.03) | under 0.10 (25-40 %) | over 0.85 (≤ 2.5 %) | landmark / local bg (1.5-2.0; > 2 warns) |
|---|---|---|---|---|
| H_overview | **0.156** pass | **36.7 %** pass | **1.8 %** pass | 0.261 / 0.095 = **2.76** (warn) |
| H_decision (loggia) | 0.110 (warn edge) | 48.5 % (high) | 1.5 % | 0.348 / 0.060 = 5.83 (warn) |
| H_decision_cavea | 0.188 (warn) | 23.7 % (low) | 0.8 % | 0.243 / 0.113 = **2.15** (warn) |
| H_hover | exempt (power cut) | | | 6.21 |

Reading:
- The OVERVIEW passes the value band. Its ratio is above 2 (a warning, not a fail; Solace at 2.8 was accepted).
- The loggia DECISION is dark because the frame's left half is tall dark towers outside the occlusion cone, and its
  local background is the dark street below. A brighter near city or a tighter frame would fix both.
- The cavea DECISION is the brightest frame (the bowl fills 47 % of it); a −0.15 stop on DECISION frames would put it in band.
- Not checked yet: the 1280 × 720 sticker size (≥ 24 px), the 8.6b silhouette IoU against a full-city render (no city
  render was made this round), determinism of the derived JSON.

Known look issues: roof masts of the cut blocks still stand in front of the colonnade in the loggia DECISION (the
cut keeps a few antennas); the engine overlay draws the TARGET sticker over the colonnade when the vault is hidden
behind it (an engine behaviour, the same for every corp).

### 13.4 Open questions (round 2): both settled by the AD, 2026-10-18

5. **The boulevard.** Accept a 9.5 BU ring street round the circus (`street0` 40 kit), or keep the 6 BU apron and
   accept a closer, higher loggia camera?
   **Ruling: accepted.** The 9.5 BU boulevard round the circus stays.
6. **Loges.** The cavea rooms are 3.5-tall loges standing up to 0.6 BU proud of the seats. Accept, or shrink them and
   accept 30 px rooms on the seating rings at OVERVIEW?
   **Ruling: accepted.** The 3.5-tall loges in the seating rings stay: readability wins.

### 13.5 Test fixes (AD, 2026-10-18) and the re-test (Cycles, 1280 x 720, 32 spp)

Fixes (the light comes from the city, not from exposure, except the small per-frame trims at the end):
1. **The black "mast" in the loggia DECISION was not a mast.** A view ray down a column of cut blocks crosses two
   transparent walls per block; the engine's 16 transparent bounces ended it black (index pass 2, hiding the `city`
   object removed it). Aurelian now sets `transparent_max_bounces` 128 (`light.transparent_bounces`; the engine file is
   untouched, the corp hook sets it per frame).
2. **Antenna masts in the stub set.** `downtown.build` takes an optional `mast_pad` (default off, no change for the other
   corps; Aurelian 8): a block's roof clutter (antennas, tanks, holo poles) is tagged with the clutter top (top + 25) and a
   wider footprint, so the occlusion rule cuts it with the block.
3. **The city lift** (`light`, all light-linked to the city and ground, so the landmark is untouched): `cityfill_*` 40
   block uplights on the boulevard rectangle aimed up at the first row of blocks (`fill_w` 25 kW), and `camfill`, one
   soft cool area light at the camera aimed at the target (`camfill_w` 28 kW at 265 kit, scaled by distance squared). The
   warm landmark against a cool city is the intended colour split.
4. **Per-frame trims** (`hq.frame_stops`, post only): H_decision -0.45 stop, H_decision_cavea -0.20 stop (the brief said
   about -0.15; the city lift is off on that frame, `camfill_frame`/`fill_frame` 0), H_overview -0.08 stop. OVERVIEW also
   dims the arch glow x 0.80 and the laurel ring x 0.60 (`ov_loggia`, `ov_laurel`; the laurel is now its own object).

Re-test (`scratch/test/values.json`, `test_sheet.jpg`; the round-1 sheet is `test_sheet_round1.jpg`):

| Shot | median | under 0.10 | over 0.85 | landmark / local bg | round 1 |
|---|---|---|---|---|---|
| H_overview | 0.158 | 34.5 % | 1.3 % | 0.246 / 0.105 = 2.34 | 0.156, 36.7 %, 2.76 |
| H_decision | 0.154 | 31.4 % | 1.0 % | 0.274 / 0.113 = 2.41 | 0.110, 48.5 %, 5.83 |
| H_decision_cavea | 0.161 | 30.2 % | 1.2 % | 0.213 / 0.092 = 2.32 | 0.188, 23.7 %, 2.15 |
| H_hover | 0.029 (exempt) | 79 % | 0.9 % | 5.84 | |

Checks: stickers at 1280 x 720 on DECISION: smallest 25 px (the overlay's floor, 0.75 x 34); cavea 25 px. Silhouette:
`silhouette_check.jpg` (canonical colosseum from `city_all_corps_night.png` beside an Eevee render of the HQ landmark at
pitch 53; same elliptical three-tier bowl, tholos, laurel, four campanili; an eyeball check, no IoU computed).

### 13.6 Finals v1 (Cycles, 2560 x 1440, 64 spp)

Final-batch changes after the re-test: H_decision_cavea city lift back at x 0.5 and -0.30 stop (the unlifted frame drifted
to ratio 2.67 at 64 spp); `ov_loggia` 0.70. Files: `H_*_v1.png` (composite), `plates/H_*_v1_plate.png`,
`H_*_v1_values.json`, `H_*_v1_rooms.json` (room front corners, world and 2560 px; `scripts/finals_pack.py`),
`finals_sheet_v1.jpg`.

| Final | median | under 0.10 | over 0.85 | landmark / local bg |
|---|---|---|---|---|
| H_overview_v1 | 0.148 | 38.5 % | 0.7 % | 0.239 / 0.095 = 2.52 (0.02 over the 2.5 aim) |
| H_decision_v1 | 0.145 | 29.7 % | 0.9 % | 0.268 / 0.119 = 2.26 |
| H_decision_cavea_v1 | 0.148 | 30.8 % | 1.1 % | 0.193 / 0.087 = 2.22 |
| H_hover_v1 | 0.013 (exempt) | 81 % | 1.1 % | 12.7 (exempt) |

## 14. Round 3: AD rulings (2026-10-18), v2

Four rulings on the v1 finals. Everything below is built in `scripts/` and checked; the numbers are in 14.6. The v1 files
stay as they were (`*_v1.*`); v2 is `*_v2.*`. Concept B's up-colonnade / rim walk / down-seats order is replaced by
concept **R** (`aurelian_landmark._levels("R")`, `hq_graph.CONCEPT`); concepts A, B and C stay in the thumbnails code.

### 14.1 Ruling 1: occlusion (no building above stub height in front of any route room)

**Why the cone missed them.** The engine (`hq_jobs.frame`) builds the cone from the OVERVIEW's every route node, but in
DECISION and HOVER only from the **current room + its options**. Every other route room in frame (v1: the loggia rooms
on both sides, the rings behind, the vault) was not a target, so the towers in front of them kept their full height. In the
v1 DECISION frames 31 buildings overlapped 5 rooms, and in the HOVER frame 27. The OVERVIEW was already clean. The camera
distance (`dmin` 260 kit) was not the cause: the cone is built from the camera, whatever its distance.

**Fix** (`hq_run._frame`, a wrapper on the engine's `frame`; the engine files stay untouched): the cone target set is every
route room in the frame that faces the camera, plus the vault, plus the current room and its options (OVERVIEW: every route
node, as before). The rule itself (`downtown.occlusion_params`, spec 7: stub 6.4 BU, ghost 0.18) is unchanged.

**Measure** (two independent checks, both in `scripts/`):
- `occ_check.py` (the python twin, runs inside Blender for every rendered frame; `scratch/occ_<frame>.json`): for each room
  in frame, the buildings the rule leaves above stub height + 0.5 whose projected hull overlaps the room's screen box +12 px
  and that stand nearer the camera than the room.
- `occ_index.py` (on the render's object-index pass): the share of city pixels (index 2) in each room's front box. The raw
  Cycles pass is speckled (22-25 % of the landmark's own pixels carry the city index), so a building in front means a share
  above 50 %.

### 14.2 Ruling 2: the route runs from the outer ring to the centre

Bands, outer to inner (`aurelian_landmark._levels("R")`, `gates()`):

| Band | Level | Where | Room floor z | Faces | Arc | Capacity |
|---|---|---|---|---|---|---|
| (a) | **ARC** | the ground arcade (the ambulatory), south face, one room per arch opening | 0.3 | out | 205-332 deg, entry bay skipped | 12 |
| (b) | gate | the **outer vomitorium**: a lit arch in the arcade at 344 deg, a stair inside the wall up to the top ring | 0.3 up to 15.05 | | | |
| (c) | **R1** | top seating ring, north arc, loges in the ring edge | 15.05 | in | 160-20 deg | 15 |
| | gate | a stair cut through the riser, at the end of the ring, in a gilt arch frame (west) | 15.05 down to 10.55 | | | |
| (c) | **R2** | second ring | 10.55 | in | | 13 |
| | gate | riser stair (east) | 10.55 down to 6.55 | | | |
| (c) | **R3** | third ring | 6.55 | in | | 11 |
| | gate | riser stair (west) | 6.55 down to 3.05 | | | |
| (d) | **POD** | the podium / arena floor, loges at the arena edge | 3.05 | in | | 9 |
| | link | the arena stair straight across the sand | | | | |
| (e) | **VAULT** | THE CONCORDAT VAULT, the Rostrum's tholos | 4.2 | all | | 1 |

- **Layer to band** (deterministic, D10 kept): the route layers are every layer except the last (the vault). With *n*
  route layers and the 5 levels ARC, R1, R2, R3, POD (`level_of`): n >= 5 gives `level = floor(i * 5 / n)`, so consecutive
  layers share a level, 1-3 layers each up to 15 route layers (n = 9 gives 2, 2, 2, 2, 1; a 7-layer GDD run, n = 6, gives
  2, 1, 1, 1, 1); n < 5 spreads the layers from ARC to POD by `round(i * 4 / (n - 1))`. Above 15 route layers a level holds
  more than 3 layers and its arc widens (the DESIGN 4.2 rule, unchanged).
- **Slots**: within a level each layer takes a contiguous sub-arc, one empty slot between layer groups, nodes spread evenly.
  Walk directions alternate (ARC west to east, R1 east to west, ...), so a gate is at the end of the arc it leaves, 12 deg
  past the last slot. The ARC arc skips the entry bay (a room never takes the entry arch).
- **Edges**: a gate edge runs to the end of its level, through the gate's arch (14.2 table), and along the next level; the
  start's ramp runs in through the entry arch; the topology (nodes, edges, kinds) is still only the game's (the fixture is a
  mock for these renders).
- The ground-arcade room is 2.8 wide and 3.5 tall (it sits inside one arch opening, 4.0 wide with a 0.6 clear each side; 3.5
  keeps it at the 46 px OVERVIEW target, `hq_run.py px`: ARC 47.6-50.0, R1 50.1-54.7, R2 48.7-52.0, R3 47.4-49.9, POD
  46.3-47.3, vault 46.0). Where rooms stand, `arcade_piers()` puts a pier at each edge of the opening and drops the grid
  piers within 2.2 BU, so the arches next to a room are never narrower than 1.2 BU.

### 14.3 Cameras: the pitch rises as the route moves inward

OVERVIEW is unchanged (outside and above: bearing 200, pitch 36, lens 36). **DECISION** orbits round the colosseum to face
the current room's bearing (the spec rule: the mean look of the distinct room normals; the options' when that mean is
degenerate, as across a gate). The pitch is a function of the band (`hq_preset` `cam.pitch_band`):

| Band | ARC | R1 | R2 | R3 | POD | VAULT |
|---|---|---|---|---|---|---|
| Pitch (deg) | 30 | 38 | 44 | 50 | 55 | 55 |

The camera is outside the colonnade for the ARC rooms (`dmin_loggia` 260 kit, lens 42), inside the bowl above the arena for
the rings and the podium (lens 30, `dmin` 32 BU) looking down across it, and from the OVERVIEW bearing at 0.6 of its distance for
the vault. HOVER is the kit's (22 % pull, 3 deg, x 0.96).

### 14.4 Ruling 3: the outer wall is a Roman arcade (city model and HQ, spec 8.6b)

`arcade_tier()` / `arcade_piers()` (identical in `city_all_corps/scripts/landmarks.py aurelian()` and in
`aurelian_landmark.canonical()`), per tier: 60 piers (1.0 wide) on the outer ellipse, a **round arch** between each pair
(8 segments per half circle; the springing is set so the crown is the same on every arch) with an **archivolt** band (0.3,
proud by 0.1), a soffit and jambs through the 2.15 BU wall depth, spandrels to the entablature, an **engaged half-column**
(r 0.5, capital and base) on each pier's outer face, and the existing **entablature** band over each tier and the **attic** on
top. The recessed lit wall is behind (the lit arches show through the openings). Faces: about 3 900 per tier, against 600 for
the v1 free columns. The silhouette (the ellipses, the tier heights, the campanili, the cavea, the Rostrum) is unchanged.
HQ only: the room bays (a wide arch with piers at its edges, 14.2), the entry arch and the outer gate are extra openings; the
city has none.

### 14.5 Ruling 4: ENTRY

```
ENTRY = {"entry": [-15.547, -21.871, 0.0], "entry_nrm": [-0.342, -0.9397]}
```
(`aurelian_landmark.ENTRY`; BU relative to the HQ lot centre, x east, y north, z above ground.) It is the outer arcade's ground
arch at parameter 240.37 deg, whose outward normal is the overview bearing 200 (the camera's side). The Cell's box stands
6 BU in front of it; the start's ramp runs in through it.

### 14.6 Results (Cycles, 2560 x 1440, 64 spp; one frame per locked batch, about 7 min each)

Files: `H_overview_v2`, `H_decision_v2` (an outer-arcade room: current room layer 0, options layer 1), `H_decision_inner_v2`
(a seating-ring room, R2), `H_hover_v2` (`.png`, `_values.json`, `_rooms.json`), `plates/H_*_v2_plate.png`,
`finals_sheet_v2.jpg` (1280 x 802), `city_colosseum_before_after.jpg` (the city model, v1 free columns beside v2 arcade,
city a2 `dbg_aur`, Eevee main look). The v1 files are kept.

| Final | median (0.14 +- 0.03) | under 0.10 (25-40 %) | over 0.85 (<= 2.5 %) | landmark / local bg |
|---|---|---|---|---|
| H_overview_v2 | 0.152 | 38.1 % | 0.8 % | 0.234 / 0.095 = 2.46 (warn, aim 2.5) |
| H_decision_v2 | 0.153 | 36.0 % | 0.5 % | 0.262 / 0.094 = 2.79 (warn) |
| H_decision_inner_v2 | 0.133 | 39.9 % | 0.8 % | 0.210 / 0.125 = 1.67 |
| H_hover_v2 | 0.010 (exempt) | 88 % | 0.2 % | 10.49 (exempt) |

The decision frames are a little dark at the bottom: the wider cone (14.1) flattens more of the city that lit them. Per-frame trims in
`hq_preset` (`H_decision` -0.2 stop, uplights x 0.8; `H_decision_inner` -0.30). Flagged for the AD, not tuned further.

**Occluders** (buildings above stub height, in front of and overlapping a route room's screen box + 12 px; `scratch/occ_<frame>.json`,
written by the render job itself, and `occ_index.py` on the index pass; the count for the rooms in frame):

| Frame | rooms in frame | v1 (the cone = current + options) | v2 twin | v2 index pass (rooms with city > 50 % of the front box) |
|---|---|---|---|---|
| H_overview | 27 | 0 | **0** | 0 (max city share 0.26 = the pass speckle) |
| H_decision | 18 | 31 buildings on 5 rooms | **0** | 0 (0.25) |
| H_decision_inner | 19 | 1 (v1 cavea frame) | **0** | 0 (0.00) |
| H_hover | 18 | 27 on 5 rooms | **0** | 0 (0.26) |

Other checks: `hq_run.py px` (rooms at the 46 px OVERVIEW target) passes for every band (14.2); the city model vs the HQ module is
1:1 (the `CITY_LM_DUMP` check against the built-in `aurelian()`: 16 511 faces, 0 mismatches, 2 lights equal); a face-count budget of
about 3 900 faces per tier (14.4).

Settled by the AD (2026-10-18): Q8 accept the 2.8 x 3.5 arcade rooms; Q9 the gate arches and stairs are HQ-only dressing. Q7 (DECISION
`under 0.10` at 40.7 % / 42 %) was answered with a lift of the city fill, see 14.7. The table above is the 14.7 re-render of the two decision frames.

### 14.7 Follow-up round (AD, 2026-10-18): the face band, and Q7

1. **The face band joins the cone.** In the v2 H_decision a tall tower at the frame's left-centre still hid a third of the colonnade
   although no room stood behind it. DECISION and HOVER now also cover the landmark's **face band at the current level**
   (`hq_graph.band_points`, added to the cone in `hq_run._frame`): the AD's rule is the arcade bays from the current room to the
   options plus one bay either side (`BAND_BAYS`). That alone left the tower (it stood two bays past the +1 bay), so the band
   runs on to the frame edge: every point of the level's face (floor and room-top heights, 3 deg apart) that projects inside the
   frame. `occ_check.count_band` counts buildings above stub height that stand in front of and overlap the band's screen box
   +12 px (`band_occluders` in `scratch/occ_<frame>.json`, `occluders` in the values json).
2. **Q7, by light.** `fill_frame` / `camfill_frame` (the city lift) H_decision x 1.45 and H_decision_inner x 0.8 (were 1.0 and 0.5);
   H_decision trim -0.38 stop (was -0.2); the uplights stay x 0.8.

| Final (re-rendered, 2560 x 1440, 64 spp) | median | under 0.10 | over 0.85 | landmark / local bg | rooms occluded (twin / index) | band occluders |
|---|---|---|---|---|---|---|
| H_decision_v2 | 0.153 | 36.0 % | 0.5 % | 0.262 / 0.094 = 2.79 (warn) | 0 of 18 / 0 | 0 |
| H_decision_inner_v2 | 0.133 | 39.9 % | 0.8 % | 0.210 / 0.125 = 1.67 | 0 of 19 / 0 | 0 |

The wider cone flattens more of the near city, so the local background of H_decision is darker (ratio 2.44 to 2.79, a warn; the
ratio is the price of the cleared view). H_overview and H_hover are the 14.6 renders (not re-rendered; their rooms are unchanged).
