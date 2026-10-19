DRAFT (Batch API, Sonnet, 2026-10-18; AD review pending)

# Halcyon campaign theme: ART plan

**Theme (designer ruling, 2026-10-18):** the Eye scans the city. Spotted territory raises difficulty. The Eye moves. After an Exploit it fixes on that area for 2 netruns. The HQ run keeps it as the rotating watcher.

This is an art plan. It draws things and does not set rules. Every rule I need is listed in "Questions for the build session".

## 0. Sources and conflicts

| Source | Status | How I use it |
|---|---|---|
| `hq_halcyon/NOTES.md` (route-map look, AAA-2 r3) | Approved landmark and look | Kept as is. Pyramid, eye turret, gaze, blade, lighthouse beam, lockdown, orbit rig, kit and value numbers are unchanged. |
| `drafts/hq/halcyon.md` | Unapproved design draft, nothing built | Only its "Art hooks" (section 9) are used. Its rules (Alert, Blade riders, Annex, shuttered state, Stall) are not assumed. |

**Conflicts I found. The art is built to survive either answer.**

| Topic | NOTES | Draft |
|---|---|---|
| Route size | 21 rooms in a chain, rows 6-5-4-3-2-1, 3 climbs | 13 layers, about 30 nodes, up to 4 per layer |
| Tier size | Fixed (half-size 73 / 61.5 / 50 / 38.5 / 27 / 15.5 BU) | Derived from the rooms it must hold |
| "Power cut" | Hover dimming of everything outside the branch | "Cut the Power" = the eye sleeps (an Annex effect) |
| Red | Scanned room turns lockdown red | Red band on the pyramid rises with an Alert meter |

**Art consequence.** All HQ art is slot-driven: it asks the layout for room positions and never hard-codes them. Whether the tiers scale is Q8.

**Assumptions I make because I have no notes on them:**
- (a) The raid map is the Grid (city map) in raid mode. C and D are two layers on one map.
- (b) Street netruns use the same orbit and decision camera rig and the same occlusion rule as the HQ notes.
- (c) The Grid has no style notes available to me. D reuses the overlay grammar (stickers, wax, grease pencil).

## 1. One Eye, two forms

The street netrun shows a light form and the HQ shows the full form. Both use the same marks, so the player knows it is the same Eye.

| Mark | Street netrun (light) | HQ netrun (full) |
|---|---|---|
| Eye body | Small distant mast with an amber almond rim. No lashes. | Approved turret on the apex (drum 12.5 BU radius, amber rim, lashes, teal iris). Unchanged. |
| Lighthouse beam | Yes, low power, sways | Yes, approved (2.2° and 6° cones, pitched 9° down) |
| Gaze wash | Soft ellipse, no hard edge | 90° sector with gobo edges, light-linked to the compound |
| Blade scan line | Only when FIXED | Yes, one white line across the sector |
| Red | Eye badge and difficulty pips only | Room ring, lockdown light, scan plane, badge, chip |
| Dial | Single glyph | Eye dial (next 3 centres) |

**Shared constants**

| Item | Rule |
|---|---|
| Loop | 96 frames at 24 fps (4.0 s). Every periodic term uses a whole number of cycles in 96 frames. |
| Step turn (not a loop) | 45° in 18 frames (0.75 s), ease in-out |
| Lock-on / release (not loops) | 24 frames each, ease-out / ease-in |
| Seamless noise | Fog noise: 4D noise with `w` on a circle. Rain and traffic: whole-period offsets. |
| Gaze colour | `scan` (white, teal fringe). |
| Amber | Eye hardware rim only. |
| Red | Only for consequence marks: ring, badge, pips, lockdown. Never for beams. |
| Colours to avoid for Eye light | Lime and orange route colours, gold (climbs). |
| Violet #B06EFF | UI accent on stickers only. |
| Value targets (plates, no UI) | Median ≈ 0.14. 25-40 % of pixels under 0.10. At most 2.5 % over 0.85. |
| Value targets (with UI) | At most 3.5 % over 0.85 (the established UI-white margin). |
| Landmark rule | Landmark median ≈ 2× its local background (box grown 35 %). Accept 1.6-2.4. Measure with `hq_landmark.py`. |
| Eye light budget | Render with the Eye in its own light group. Frame median with it must stay within +0.02 of the same frame without it. |
| Eye pixels over 0.85 | At most 0.3 % of the frame. The reveal beam-pass is exempt. |

## A. Street netrun, light form

### A1. What is drawn

1. **The mast.** A far-skyline civic watch mast with an amber almond rim and a teal iris. It sits beyond the farthest route room in depth. It is a skyline accent, not a landmark. Its local luma ratio is at most 2.
2. **The beam.** One lighthouse beam from the mast. It is additive, in fog, and pitched slightly down.
3. **The wash.** A soft white-teal ellipse on building faces that look toward the mast. It is light-linked to city buildings only.
4. **FIXED extras.** The sector gobo edges (same 90° shape as the HQ), a ground pool with a ring, and the blade line.

### A2. States

| State | Look | Motion (96-frame loop) | Overlay | Luma notes |
|---|---|---|---|---|
| **AWAY** (Eye elsewhere) | Beam at ×0.35 power, swaying away from the route area. No wash on route buildings. | Beam sway ±12° sine, 1 cycle. Iris pulse 2 cycles. | Dim teal eye glyph in the header corner | Eye adds under 0.005 to the median |
| **SCAN** (Eye sweeping this area) | Beam at ×0.7, sway centred on the area. Wash follows the beam with an 8-frame lag. | Same sway and iris. Wash intensity follows the beam. | Bright teal eye glyph | Wash facade luma at most 0.22, area at most 15 % |
| **SPOTTED** (territory flagged) | Low steady cold cast (×0.35) over the whole view. Fine scan lines travel over window glass. | Scan lines 1 cycle. Beam sway as SCAN. | Eye glyph with a red badge, plus difficulty pips (fill from Q2) | Cast adds at most 0.02 to the median |
| **FIXED, 2 left** | Beam stops and lands on the area. Gobo edges appear. Ground pool with a closed ring. Iris dilated by 20 %. Blade line inside the sector. | Beam tremble ±1.5°, 4 cycles. Blade sweep 1 cycle (fade in 0-8, fade out 88-96). Ring tick marks scroll 1 cycle. | Lock-on glyph (eye in a crosshair) with 2 pips filled | Pool at most 0.25, area at most 4 %. Blade at most 0.70, area at most 0.4 %. |
| **FIXED, 1 left** | As above at ×0.85. Pool ring broken into 4 arcs. Iris rim flickers 15 % dimmer. | As above, plus rim flicker 8 cycles | Lock-on glyph with 1 pip filled, 1 hollow | Same caps |
| **RELEASE** | Beam lifts off. Gobo edges soften out. Ring arcs fade. Returns to AWAY or SCAN. | 24 frames, ease-in | Glyph shrinks to the dim form | n/a |

*Lock-on on entry:* at netrun entry in FIXED, the beam swings from sway to hold over 24 frames.

### A3. Overlay glyphs and gauges

| Glyph | Spec |
|---|---|
| Eye glyph | Almond with iris dot. 24 px in the header at 2560 × 1440. Stroke 2 px. Teal off, white on. |
| Red eye badge | Existing `states.eye_badge`. Used on stickers and the header. |
| Lock-on glyph | Eye glyph inside a thin ring with 4 ticks. 32 px. |
| Pips | 2 round pips for FIXED turns left. Filled = remaining. |
| Difficulty pips | Pip bar with slots for 1-4 pips. Count and meaning come from the build session (Q2). Placeholder fill in stills. |
| Words | Reuse `rule_word` ("SPOTTED", "IN THE EYE"). Any new label ("FIXED") is placeholder copy. |

**Layer order.** Scene, then beam matte, then Eye marks, then route links, then room stickers. Eye marks never overlap a room sticker footprint.

### A4. Occlusion (never hide route rooms)

| Risk | Rule |
|---|---|
| Mast in front of rooms | Its screen position must stay outside the target-volume hull grown 10 % (the same margin as the occlusion cone). If not, slide it along the skyline. If it still fails, drop the mast and keep beam and wash. |
| Beam veils rooms | Render the beam as its own light-group pass. Composite it under the overlay with alpha × (1 − 0.85 × room-opening mask). |
| Wash lifts room openings | Wash is light-linked to city buildings only. A room's own light drives its opening. Wash luma is at most 0.65× the current room opening median. |
| Pool over rooms | The pool is a ground decal. It fades to 0 above 2 BU of height. |
| Buildings hide rooms | Existing flatten and ghost rule (`downtown.py`). The mast counts as a building in that rule. The beam is air and is never cut. |
| Glyphs over rooms | Glyphs sit in header and corners. Verify against the room hull in every still. |

### A5. Frames to render (street)

| ID | Frame | Notes |
|---|---|---|
| A01 | AWAY, decision frame | 2560 × 1440 with UI |
| A02 | SCAN, beam crossing mid-frame | Plate and UI |
| A03 | SPOTTED, early decision | Shows cast, scan lines, pips |
| A04 | FIXED 2 left | Plate and UI |
| A05 | FIXED 1 left | Same camera as A04 for comparison |
| A06 | Occlusion proof | Low camera behind a tall tower, beam crossing a route room. Show the matte on and off. |
| A07 | Eye light budget A/B | Same camera, Eye group off and on, with value tables |
| AL1-AL3 | Loops: AWAY, SPOTTED, FIXED | 96 frames, 1280 × 720, plus a 4-frame strip each (frames 0, 24, 48, 72) |
| AT1 | Lock-on transition | 24 frames |
| AT2 | Release transition | 24 frames |

## B. HQ netrun, full form

### B1. What is drawn

The approved landmark and run are kept unchanged:
- the stepped pyramid with the helix route
- the turret on the apex with its gaze gobo, blade and lighthouse beam
- the red lockdown room light with its scan-line plane
- the orbit camera, the OVERVIEW and the reveal

This plan adds only loops, a step-turn clip, the dial animation and the checks below. Nothing in the landmark geometry changes.

### B2. States

| State | Look | Motion | Overlay |
|---|---|---|---|
| **WAKE** | Existing reveal (eye wakes, beam passes the camera at 3.0 s) | Existing 144-frame clip | Route and UI draw in at the end |
| **WATCH** | 90° sector holds on the lit faces. Blade line sweeps inside it. Beam holds. | See B3 loop table | Dial, ring, badge, chip |
| **STEP** | Sector, beam and turret rotate 45° against the climb | 18 frames, ease in-out. The dial needle turns in sync. | Dial updates. Rooms newly in the eye get ring and badge, with a 6-frame fade. |
| **ROOM IN THE EYE** | Red ring, badge and chip. Room light red ×2.2. Translucent red scan plane over the opening. | Plane lines scroll 4 cycles in 96 frames | Existing |
| **ROOM BLOCKED** | Same marks, plus a solid red frame (the rule word picks the label, Q8) | Same | Existing |
| **CLIMB / CLEAR** | No Eye marks. Existing climb colours. | n/a | Existing |

The draft's shuttered, Alert-band and eye-asleep states are not drawn until the build session confirms them (Q7).

### B3. Loop (WATCH, 96 frames)

| Element | Cycles in 96 frames |
|---|---|
| Gaze wash breathing ±6 % | 1 |
| Blade line sweep (fade in 0-8, fade out 88-96) | 1 |
| Beam sway ±3° | 1 |
| Iris pulse | 2 |
| Pylon warning lights blink (24-frame period) | 4 |
| Lockdown plane scroll | 4 |
| Ring-road streaks | Whole-period offset |
| Fog | `w` on a circle |

### B4. Colour, value and the landmark rule

- Gaze and beam stay white-teal. The amber rim stays on the hardware.
- The approved plates measured a landmark ratio of 2.9 (0.337 vs 0.115). That is above the 2× rule. The theme must not raise it. If the designer wants about 2×, lower the uplights and coves. Do not change the geometry (see Risks).
- Plate targets stay as in NOTES (median 0.12-0.15, 36-41 % under 0.10, at most 0.30 % over 0.85).
- The Eye light group must stay within the +0.02 median budget.

### B5. Occlusion (never hide route rooms)

| Risk | Rule |
|---|---|
| Compound hides rooms | Existing rule. The compound is never an occluder. Rooms draw only on faces turned toward the camera. Far-face rooms ghost in the OVERVIEW. |
| Beam crosses in front of rooms (apex height, camera at pitch up to 24°, distance at least 135 BU) | When the beam azimuth is within ±30° of the camera azimuth, depth-fade the beam to 0 for distances below (farthest target depth + margin). It shows only as far field. |
| Lockdown plane hides contents | Plane opacity at most 35 %. Line coverage at most 40 %. |
| Dial hides rooms | Dial sits in a corner of the usable area. Verify against the room hull. |
| Reveal beam pass | Allowed. The route is not drawn until the last second. |

### B6. Frames to render (HQ)

Existing stills (H_overview, H_decision_S/E, H_hover_S/E, H_reveal) stay as baseline.

| ID | Frame | Notes |
|---|---|---|
| B01 | STEP strip, 5 frames (0, 4, 9, 14, 18) | Same camera, dial in shot |
| B02 | WATCH loop | 96 frames, 1280 × 720, plus a 4-frame strip |
| B03 | Beam near-clip proof | Camera azimuth equal to beam azimuth. Show near-clip on and off. |
| B04 | ROOM IN THE EYE close-up | Ring, chip, plane at the opacity caps |
| B05 | Reveal flash fix | `hq_all.py flash` for frames 60-71 |
| B06 | Value and landmark sheet | Median, under 0.10, over 0.85, ratio, 320 px thumbnail |

## C. Raid hook (city / raid map)

### C1. What is drawn

The designer ruled one raid hook per corp, but its rule is not given to me. This plan draws a rule-agnostic mark. **Halcyon watch mark:**
- the Eye's sector wedge lying over part of the raid map
- an eye badge on each home-server node inside the wedge
- one chip slot next to the badge for the hook's effect text (Q6)

### C2. States

| State | Look | Motion (96-frame loop) | Overlay |
|---|---|---|---|
| **IDLE** | Wedge at 12 % fill, thin white-teal edge line | Edge pulse 1 cycle | None |
| **HOOK ACTIVE** | Wedge 18 % fill. Badge appears on nodes in it. Beam line along the wedge centre. | Blade-style scan edge 1 cycle across the wedge. Badge pulse 2 cycles. | Chip slot filled with placeholder text |
| **FIXED** (if the hook uses it) | Wedge snaps to the fixed area (24 frames). Ring and 2 pips at the anchor. | Ring ticks 1 cycle | Lock-on glyph and pips |
| **RELEASE** | Wedge fades and widens back (24 frames) | n/a | Pips removed |

### C3. Colour, value and occlusion

- Colour: white-teal fill and edge. Red only on the badge.
- The wedge is drawn under the node layer. Each node and badge gets a 4 px knockout halo.
- Wedge fill alpha is at most 0.18. It never darkens a node or its label.
- No beam or wash ever covers a node icon. Nodes stay the brightest item on the map.
- Map frame median target follows the Grid's own value rule (see Q13).

### C4. Frames to render

| ID | Frame |
|---|---|
| C01 | IDLE, full raid map |
| C02 | HOOK ACTIVE, two nodes inside the wedge |
| C03 | HOOK ACTIVE close on one node, showing the halo and chip slot |
| C04 | FIXED (only if confirmed in Q6) |
| CL1 | HOOK ACTIVE loop, 96 frames |

## D. Grid layer (city map)

### D1. What is drawn

All layers are 2D overlays on the Grid:
1. **Eye marker** at the HQ marker (the Eye's source).
2. **Sector wedge**, 90°, the same shape as the HQ. It turns 45° per move (the HQ rule, kept as art).
3. **Spotted territory** on district polygons: a cold white-teal 45° hatch, 12 px spacing, 25 % alpha, dashed teal border, and a small red eye badge on the district label.
4. **Fix mark**: when the Exploit fixes the Eye, the wedge turns to that area and locks (ring and 2 pips at the eye marker).

Fallback if the build session says the Eye roams instead of anchoring at the HQ: replace the wedge with a soft disc of the same colours. Nothing else changes.

### D2. States

| State | Look | Motion |
|---|---|---|
| **SCANNING** | Wedge at 12 % fill. Edge line white-teal. | Edge pulse 1 cycle. Eye iris pulse 2 cycles. |
| **MOVING** | Wedge rotates to the new centre | 18 frames, ease in-out. Trailing 4-frame ghost of the old edge. |
| **SPOTTED district** | Hatch, dashed border, red badge | Hatch drift 1 cycle (12 px) |
| **FIXED, 2 left** | Wedge locked on the area. Edge solid. Ring with 4 ticks at the eye marker. 2 pips filled. | Ticks 1 cycle. Blade-style scan edge 1 cycle. |
| **FIXED, 1 left** | One pip filled, one hollow. Ring broken into 4 arcs. | As above |
| **RELEASE** | Wedge unlocks and resumes SCANNING | 24 frames |

### D3. Overlay, colour, value and occlusion

| Item | Rule |
|---|---|
| Glyphs | Same set as A3. Pips sit next to the eye marker. |
| Colour | White-teal for Eye marks. Red only on the badge. No amber except the marker's rim. |
| Labels | Wedge and hatch sit under district labels. Labels get a knockout halo. |
| Nodes and links | Wedge fill at most 0.18 alpha. Hatch at most 0.25. Nodes and home servers stay on top. |
| Legibility | The hatch is a pattern, so SPOTTED does not rely on colour alone. |

### D4. Frames to render

| ID | Frame |
|---|---|
| D01 | Grid overview, SCANNING with two SPOTTED districts |
| D02 | FIXED, 2 left |
| D03 | FIXED, 1 left |
| D04 | MOVING strip (frames 0, 5, 10, 14, 18) |
| D05 | Exploit-to-fix strip (wedge turn, lock, pips, 24 frames) |
| D06 | Zoomed district with hatch, label halo and badge |
| D07 | Legend sheet (all glyphs, pips, hatch) |
| DL1 | SCANNING loop, 96 frames |

### Language sheet (one image)

Render `HT_language_sheet` in the style of `H_scan_states.png`. It shows the Eye ladder across A to D: glyphs, pips, wedge, hatch, rim, and the red / white-teal / amber rules.

## 2. Kit reuse vs new

| Item | Reuse | New |
|---|---|---|
| `hq_kit.layout` (Compound, `watch` lighthouse, scan rule) | Yes | `watch` type `fixed` (holds an azimuth) |
| `hq_kit.orbit` | Yes | None |
| `hq_kit.city_ring`, `lod` | Yes | Street city is a different generator. `lod_bands` reused: Eye detail rides `signage_on_at` and `small_lights_on_at`. |
| `hq_kit.states` (`STATE_COL`, `ring_colour`, `eye_badge`, `rule_word`, `scan_lines`) | Yes | Pips, lock-on glyph, hatch |
| `hq_scene.set_eye` (gaze gobo, blade, beam, turret) | Yes (HQ) | Street `eye_light` module: mast, soft wash, held beam, ground pool |
| `downtown.py` / `section.py` occlusion rule | Yes | Mast registered as an occluder candidate. Beam near-clip. |
| `hq_post` (auto-iris, flash, exposure by zoom) | Yes | Beam matte composite |
| `hq_overlay` (ring, chip, dial, x-ray) | Yes | Header glyphs, pip bar, Grid wedge and hatch layers |
| `hq_values.py`, `hq_landmark.py` | Yes | Eye-group A/B budget check |
| Loop harness | No | New: 96-frame loop with a periodicity validator. It fails any term that is not a whole number of cycles. |

## 3. Risks

| Risk | Effect | Handling |
|---|---|---|
| Beam veils route rooms | Route is no longer the clearest thing | Beam matte (A4), near-clip (B5), proof frames A06 and B03 |
| HQ landmark ratio is 2.9, rule is about 2× | Theme additions push it higher | Eye light group budget. If the designer wants about 2×, reduce uplights and coves, not geometry. |
| Red overload | Red is already the TARGET pencil, lockdown and raid lanes | Red only on consequence marks and badges |
| Amber rim vs orange "next" route | Colour clash | Amber on hardware only. Beam stays white-teal (NOTES Q1). |
| Light form reads as a different thing | Theme loses continuity | Shared marks (section 1). Frame A04 next to the HQ plates in the sheet. |
| Loop seams in fog, rain, traffic | Visible pop at frame 96 | `w` on a circle, whole-period offsets, validator |
| Route size unknown (21 chain vs 30 nodes) | Landmark and loops may be re-rendered | Slot-driven art. Build session confirms (Q7). |
| Grid and raid map style unknown | D and C may not match | Assumption (c). Stills use only the shared overlay grammar. |
| Godot fog ignores projectors | In-fog gaze edge is approximate. The exact edge is a wedge FogVolume. | Plain spot for the fog cone, as NOTES section 8 |
| Per-instance occlusion plus Eye | More per-instance data | Same `INSTANCE_CUSTOM` block, no new draw calls |
| Render cost | Street loops and HQ loop at 5-17 s a frame | About 3 street loops (about 25-30 min each clean), HQ loop (about 15-20 min), 18-frame clips, 13 stills. Everything under the GPU queue lock. |

## 4. Questions for the build session

| # | Question | Why art needs it |
|---|---|---|
| Q1 | What is "Spotted territory": a district, a netrun, or a set of rooms? How is it set and cleared? | Decides the Grid hatch, the street SPOTTED state and the header badge |
| Q2 | How many difficulty levels does Spotted add? Are they stepped or continuous? | Pip count and pip bar |
| Q3 | When does the Eye move (per netrun, per time, per Exploit)? Where is it anchored? Is its reach a wedge from the HQ or a roaming disc? Step size 45° as in the HQ? | Eye marker, wedge or disc, MOVING clip length |
| Q4 | "Fixes on that area for 2 netruns": which area (the Exploit's district?) and which netruns count? What happens at expiry? Does a second Exploit refresh or stack? | FIXED states, pips, RELEASE |
| Q5 | Does a street netrun show room-level "in the eye" marks, or territory-level only? | Whether street rooms wear red rings |
| Q6 | What does Halcyon's raid hook do, when is it active, and which nodes does it touch? Is the raid map the Grid? Does it use FIXED? | C is drawn rule-agnostic until this is answered |
| Q7 | HQ shape: 21 rooms in a chain or about 30 nodes in 13 layers? Do tiers scale to the graph? Are shuttered, Alert band, eye-asleep (Cut the Power), eye dial 3 vs 6 steps, Annex nodes and Warden lockdown in? | Slot count, tier sizes, and which HQ states to draw |
| Q8 | Rule word: SPOTTED or BLOCKED? Is there a narrow beam band (draft: ±4°) that blocks? | Labels and the ROOM BLOCKED look |
| Q9 | Does the HQ show the FIXED state? What does the HQ do when the Eye is fixed elsewhere? | Whether B needs a FIXED variant |
| Q10 | Which fields can art read per frame? Proposed: `eye_state` (away / scan / spotted / fixed), `eye_az`, `fixed_left` (0-2), `spotted` (bool), `difficulty_pips`, `phase`, `step`, per-node `state`, `alert`, `starting_alert` | Art hooks and stills inputs |
| Q11 | Is the Eye position a pure function of saved state? | Stills and loops must be reproducible |
| Q12 | Confirm amber rim, white-teal light (NOTES Q1) vs the bible's violet and amber | Palette lock |
| Q13 | What are the Grid and raid map's own value and style rules? Is there an idle OVERVIEW orbit in the HQ? | C and D value targets, loop use |
| Q14 | Do street netruns use the same orbit and decision rig and occlusion rule? | A4 depends on it |