DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id tsh__shots; status ok; tokens in 30130 cache-write 20787 cache-read 60175 out 9603; cost $0.110 -->

# Tethys DECISION and HOVER finals: shot spec (D1, D8)

Scope: PLAN AND SURFACE only. Nothing here was rendered. Pixel estimates come from the downscaled 1568 x 882 frames supplied; mark any as "uncertain". Topology comes from the game graph (spec 8.4, C15); the rooms named below are slot candidates from `hq_tethys/DESIGN.md` section 6, not route rules. Names: THE BLACK SMOKER (Central Server), THE VENT CAP (Hub), the DOCK LOCK (entry), ATLANTIS STATION.

## 0. Shared setup for both shots

| Item | Value | Note |
|---|---|---|
| Source scene | `hq_tethys/scripts/` (`tethys_build.py`, `run_tethys.py`), the Finals v2 build | The Godot-side kit is not touched |
| Resolution / quality | 2560 x 1440, 40 spp, OIDN, via the GPU lock (spec 8.1 "final") | Finals v2 render was about 130 s each; ASSUMPTION: DECISION and HOVER cost about the same |
| Units | The shipped Tethys scene is in city BU (lot r 34). Camera distances below are city BU | If the scene is later rescaled by `k_fit`, scale distances with it (8.6) |
| Slot source | `<stem>_rooms.json` pixel anchors (DESIGN.md section 6, `tethys_build.py` part 4) | Used for the overlay and the check boxes |
| Overlay | Same UI kit as the other corps (sidebar, HUD, route panel, legend, DECISION / OVERVIEW toggle) | See section 5 |
| Look | Tethys v2 water values (DESIGN.md section 5), caustics x0.03 inside the breakwater, x0.30 outside | Do not retune for these shots |

Tethys has a fixed OVERVIEW camera at yaw 135 (DESIGN.md section 11, open item 1). The DECISION and HOVER cameras are new and must not break the "see-through window" (calm ring, moon pool, server).

## 1. SHOT D1: Tethys DECISION

### 1.1 Purpose
Show the player the current room and its 2 options on the station, with the TARGET readable. It is the CHOOSE beat (spec 10, beat 7) at its resting state. It is the DECISION counterpart of the supplied OVERVIEW; the framing is closer so the rooms read at the 46 px target (12.6).

### 1.2 Camera (orbit pose, spec 6.4)

ASSUMPTION: The current room is a **pier-end pod on the causeway axis** (the arrival pod), and the two options are an **inner pod** on that pier and the **adjacent ring pod**. This keeps the DECISION in the cluster the OVERVIEW already shows. The pose below is a starting point to be solved by the framing solver.

| Key | Proposed default | Rule |
|---|---|---|
| Azimuth | yaw 135 (the map direction), plus the hover rule: the mean of the look vectors of the distinct room normals holding current + options; pods are round, so use the bearing from the station to the current pod (6.4 DECISION azimuth) | Orbit moves up to about +-25 deg from 135 and no further; the dam must stay at the frame bottom |
| Elevation (pitch) | 38 deg (range 34-42) | The calm window works at pitch 50; at pitch 40 the server shifts toward the front pods (DESIGN.md section 11). 38 is lower, so re-check; see Q1 |
| Distance / lens | Lens 30 mm (rig default), `dmin` on the order of 110 city BU; solved by the 6.1 bisection for fill 0.66 / 0.70 | ASSUMPTION: fill matches the other corps' DECISION (spec 6.4 table: Halcyon 0.66 / 0.70) |
| Look-at (F) | The centre of the decision set (current pod + 2 options); the lens shift then puts the current room on the usable-area centre ("front and centre", `centre_current`) | Range from the station about 12-30 BU |
| Hold | Static; the beam and the fish still run (always-alive rule 9.6) | The sweep of the hero beam is allowed |
| Lens shift | From 6.1: centre the decision set in x 300-1900, y 138-1012 at 1080p | |

Why this camera: the station is the tallest object, and at pitch 38 the mast and halo ring cross the upper third while the pods fill the middle. Fish and whales sit outside the main read.

### 1.3 Framing
- **Landmark share of the frame:** the station and the pods in the current cluster fill about 50-60 % of the frame width (ASSUMPTION; Halcyon's pyramid fills about 65 %, Orbital's tower about 45 %, see section 6).
- **Current room** on the usable-area centre line (x about 1100 of 1920, y about 575 of 1080).
- **Station drum and mast** in the upper-centre third; the TARGET marker (the Black Smoker) must stay inside the frame and not behind the sidebar. If the server (16 BU to screen-left of the station at the overview camera) falls under the sidebar after the orbit, reduce the orbit; see Q1.
- **The dam** is allowed to appear at the bottom 12-18 % of the frame; it is not a subject here. If it falls under the legend bar, that is fine.
- **Safe areas (1080p, spec 6.1):** x 300-1900, y 138-1012 free. Sidebar (x 0-300), top strip (HUD and DISPATCH line), the legend (y > 1012). Keep every option room at least 12 px from these (the 12.6 "available rooms unblocked" rule, 12 px margin, 40 px on top for the sticker).
- **Water level and layers:** the surface is seen from above through glass-calm water inside the breakwater; chop outside (DESIGN.md section 2). The drowned streets show as in the OVERVIEW.

### 1.4 States shown (the game passes these in; these are test fixtures)

| Element | State |
|---|---|
| Walked rooms | 2-3 pods behind the current one, lime ring and room frame, links lime |
| Current room | The arrival pod, lime frame and ring |
| Options | 2 rooms, orange frame, numbers 1 and 2, orange links |
| Ahead | White dashed links toward the station and down the moon pool |
| Past | Grey, 38 % alpha |
| TARGET | Red pencil circle and word on THE BLACK SMOKER, label "CENTRAL SERVER // THE BLACK SMOKER" chip; visible share rule 9.5b: if over 50 % of its box is in the usable area, only the partial circle |
| Black Smoker glow | The hot orange core and the white server ring, as in the OVERVIEW; keep the server patch at the 12.2 helper ratio (the finals v2 value was 5.3 x peak / 1.9 x mean) |
| Water layers visible | The calm surface, glass walkways, pods, the deep stair decks, the moon pool well. Marine snow as in the post |
| Fog / beams | Default fog and the station hero beam; no extra beams |
| Dam | Lit by its own sodium uplights |

**Mock-data note:** the route above is a concept fixture. Real topology is the game's, mapped onto the landmark's slots (spec 8.4).

### 1.5 The DECISION node set
- Pick two options of different kinds so the sticker shapes read (route requirement 3). ASSUMPTION: **1 = elite (inner pod on the pier, orange kind color 1.0, 0.38, 0.16)**, **2 = fight (ring pod)**. Another valid set: 1 = shop, 2 = event.
- The options sit on different rings of the station (inner pod vs ring pod), so their screen separation is at least 150 px at 1080p. Neither may be blocked by a stilt, the breakwater or the station tiers (12.6: at most 8 % of the opening blocked).
- Room kit cutaways use the node-kind room light colors in `ROOM_TL` (3.3).
- Each option shows its number chip to the left of the sticker (9.3), tags hidden until hover.

### 1.6 UI overlay assumptions
- The same layout as the other corps: top-left NETRUN logo, HEAT / HP / CYCLES strip, DISPATCH line, left personnel file card, ROUTE panel with CONFIRM / GRID VIEW / Save & quit, a top-right mechanic panel, the bottom legend, the DECISION | OVERVIEW toggle at the bottom right.
- **Top-right mechanic panel for Tethys:** the BALLAST TIDE panel (LOW / RISING / HIGH / FALLING) is a PROPOSAL (`new_corps/atlantis/NOTES.md`; it is game design, 14.3). ASSUMPTION: draw it as a placeholder with the tide step shown. Do not claim it as a rule. If the design session has not approved it, the frame shows a neutral panel; see Q2.
- **Legend:** FIGHT, ELITE, EVENT, SHOP, walked, next, ahead, past; plus a Tethys-specific item only if the mechanic is approved (flooded / airlock link states).
- **DISPATCH line:** a line in the Tethys voice (calm, lowercase, short; `identity.md`). Example placeholder: "Tide's rising. The inner pod's open; the ring pod's across. Go deep while they bail." It is copy for the mockup, not final text.
- The file card shows the game's data (CELL-9), and its header says TETHYS DEEP with the corp subtitle.
- Overlay is composited per `hq_compose` (on black and on 50 % grey), UI masked for the value checks.

### 1.7 Checks it must pass

| Check | Rule | Expected for this shot |
|---|---|---|
| 12.1 value band | median 0.14 +- 0.03, 25-40 % under 0.10, <= 2.5 % over 0.85, on the no-UI plate | Finals v2 were 0.140 / 30.9 % / not reported; a closer camera shows more dark water and less lit city; see section 7 |
| 12.2 landmark ratio | 1.5-2.0 pass; above 2.0 is a warning; below 1.5 fails | The shipped finals were 3.7-3.9 x peak and 1.87 x mean on the post helper (the mean ratio); the 12.2 helper uses medians, so measure it fresh. Above 2 warns only |
| R-FOCUS-1 | landmark / ring mean luma >= 1.5 | Likely pass |
| 12.7 composition | R-CALM-1 detail CV 0.45-0.85; R-CALM-2 calm tiles 12-32 %; R-HUE-1 / 2 exempt for corp HQ views; R-REP-1 p90 <= 0.60; R-DET-1 / 2 apply to street only | The deep water is calm area, so the CALM test is likely to help; the drowned-street clutter is dense, so R-REP-1 needs a look |
| 12.6 room readability | every available room front >= 46 px at the OVERVIEW; at DECISION the option rooms and current room read | Pods are small (drum r 2.5-4.2 BU); verify 46 px; see Q3 |
| 12.6 rooms unblocked | <= 8 % blocked | Check against stilts and rings |
| 7 occlusion | Cone over the current + option rooms; 0.35 s ease; never fully hidden | At this orbit DESIGN.md measured 0 cut at pitch 50; the rule must be re-run at pitch 38. Drowned towers that stand out of the water also count (open item 2) |
| 12.3 determinism | same seed gives identical placements | Seeds from `art_seeds` |
| Thumbnail | 320 px written for review | Silhouette of mast and pods must read |

### 1.8 Render budget (11.4)
- Frame budget, fog and beams are open numbers (N3). Report the Blender figures instead: about 130 s final render, 12-13 s scene build.
- Water absorption is a per-material fade (no volume), so there is no volume step-rate cost; the shipped Tethys scene is a heavy geometry scene (drowned-street clutter of about 340 cars, 659 kelp cables, 825 debris pieces, 952 shop fronts plus fish and whales).
- The Godot cost for the runtime mapping stays with the build session (N3, N5). Note the tris: the clutter should reach Godot as MultiMesh.

## 2. SHOT D8: Tethys HOVER

### 2.1 Purpose
The same camera and state as DECISION with the pointer on option 2. It shows the power cut (spec 9.4) and the hover tag. ONE value for street and HQ.

### 2.2 Camera
Identical to D1 (pose, lens, shift, frame). Per the hover rule in 6.4: the camera yaws 3 deg toward the hovered room (sign by its side in camera right), pulls 22 % of the way to it, and dollies x 0.96. It is exempt from the value band (12.1) but keep it reviewable. The hover pose is to be solved by the rig, not hand-set. Hover easing is 0.30 s in, 0.35 s out.

### 2.3 Framing
- The hovered room sits closer to the usable-area centre than in D1 (22 % pull); its tag ("FIGHT L6"-style chip above the sticker) is drawn above the room, as in the other corps' HOVER frames.
- The mouse cursor sits on the room, as in the supplied frames.
- The bottom-left hover info panel (type, tier, rewards, HP on arrival) and its ticker line at the bottom of the screen are as in the other corps.

### 2.4 States shown

| Element | State |
|---|---|
| Hovered branch lit | Option 2 plus every room to the TARGET (the whole branch to the TARGET lights, 9.4 rule 1); with a pier layout that is the pods on that pier, the station deck, the deep stair drops and the moon pool |
| Current room | Lit |
| Everything else | Cut (see 2.5) |
| Links | The path to the TARGET powered; other links dim |
| TARGET | Red pencil circle; the Black Smoker keeps its glow only if it belongs to the branch (it does, as the TARGET); expect it to read as the brightest thing in the dark frame |
| Water | The grade is a 2D post pass, so the water, caustics and fish go dark with the rest; no change to the scene |
| Hover tag | Shown; other tags stay hidden |

### 2.5 The HOVER cut (spec 9.4, Designer 2026-10-16, Q6)

| Preset | Value |
|---|---|
| `hover.cut_level` | x 0.20 outside the branch and the current room |
| `hover.cut_desat` | 0.70 |
| `hover.branch_boost` | x 1.35 |
| `hover.type_glow` | 1.0 |
| Mask | room polygons grown 8 px, blurred 8 px |
| Ease | 0.30 s in, 0.35 s out |
| Tuning | tunable toward x 0.35 in playtest |

Do NOT use any 3D cut (dropped, 9.4 rule 3). The supplied Halcyon / Orbital / Solace / Meridian hover frames show the old storyboard-era darker cut with a pale branch; Rebel Cell's too. They are probably rendered with the previous values (x 0.62 / 25 % in the storyboard, or the HQ's 3D 22 %). ASSUMPTION: the new Tethys frame is therefore darker outside the branch than the supplied frames, and this is intended (the ruling replaced them). Flag this to the art director before comparing (Q4).

### 2.6 UI overlay
As D1, plus the hover panel and ticker. On hover the branch rooms show the type-colored glow; the numbers stay on the options only.

### 2.7 Checks
- Exempt from 12.1 (hover power-cut frames) and from the landmark ratio shots (12.2: hover exempt). Report the numbers anyway.
- 12.6: wax clear of stickers and UI; the hovered room not blocked; the hover panel readable at 1280 x 720 (review frame auto-produced).
- No black frame in a hover sequence (mean luma above 0.05, 12.6 continuity). With x 0.20 on an already dark Tethys plate this is the real risk; see section 7.
- Frame-to-frame: ease uses the hover curve; no spike.

### 2.8 Render budget
The cut is a post grade, so D8 is the D1 plate plus a mask render; no second Cycles pass is needed if the room polygons come from `_rooms.json`. The cost is small (the compose step only).

## 3. What is special for Tethys

| Topic | Notes |
|---|---|
| Water | A material fade, not a volume: extinction sigma (0.052, 0.017, 0.0072) per BU, red dies first. Everything under the surface goes blue-green; the lightless red security lights vanish at depth (identity.md). The HOVER grade desaturates this further |
| Calm ring | The breakwater ring (r about 25.5 BU, +-3 soft) is the see-through window; at the DECISION pitch keep the moon pool and the server visible through it |
| Drowned streets | Dense clutter within 480 BU, depth 5-24 BU; lit windows (min 0.62 lit share); fine detail that tests R-REP-1 and R-DET. Keep the apron rule (13.1 rule 3): dimmer lit-window density near the compound is a lighting rule, never empty ground |
| Fish | Tuned for motion; they read as faint specks in a still. Do not brighten them for the plate (Finals v2 note). In HOVER they fall into the cut |
| Whales | A pod of 4 plus a calf on a r 45 BU arc beyond the breakwater at depth ZW -7 to -12, partly hidden by pods in the close-up. At DECISION they may sit in frame as background life; do not let one cross a room opening or a sticker. ASSUMPTION: freeze a whale away from the option rooms for the plate |
| Underwater lighting | Cool white key spot (0.9e6), abyss-blue fill, photophore strips, a soft cool spot under the whale pod, and the server rim light. Warm is the dam; cool is Tethys (the temperature border rule). Station emitters are at x0.75 (`PIER.emit_k`) |
| Occlusion | The towers that stand out of the water, and any cut city near the dam, need the 7 rule at the new orbit (DESIGN.md open item 2) |
| Entry | The DOCK LOCK is the entry (decided). It lies at the frame bottom; for a late-route DECISION it is far behind and may be out of frame, in which case the 9.5b arrow rules apply only to the TARGET |

## 4. Tethys-specific value risk

| Risk | Why | Mitigation to propose (calibration is the build session's) |
|---|---|---|
| Crushed lower band | The finals v2 plates sit at 30.9-31.0 % under 0.10 with a median of 0.140; a closer DECISION camera shows more water and station and less lit city, so the under-0.10 share may rise above 40 % | Solve exposure after the vignette (13.1 rule 10); use the 0.1 stop headroom noted in Meridian's test; keep photophore and window emitters rather than lifting exposure |
| Station over-bright | Ratio is above 2 (3.7-3.9 peak on the helper); this is a warning only (Q5) but the HQ should not blow past 2.5 % over 0.85 | Keep the key and ring levels from Finals v2 |
| HOVER darkness | x 0.20 on a dark water plate may fall under the black-frame limit (mean luma 0.05) | Check the mean luma of the hover frame. If under 0.05, tune toward x 0.35 as the ruling allows, and log it |
| Hue entropy | Water pushes the palette to teal | R-HUE exempts corp HQ views; still keep the red, amber and magenta accents from the dam and city |
| Calm tiles | Large calm water areas could push R-CALM-2 above 32 % at DECISION | Keep the drowned-street clutter across the frame; check the metric |
| Fish and whale noise | Specks could hit R-DET blobs | R-DET applies to street views only |

## 5. UI placement assumptions (both shots)

Based on the supplied frames (1568 px wide thumbnails, so values are 1568-scale estimates; multiply by 1.224 for 1920):
- Top strip: HEAT / FLAGGED / HP / CYCLES at x 205-670, y 10-65; DISPATCH line y 75-98 across x 205-1325.
- Left card: x 15-220, y 115-375 (personnel file). ROUTE panel x 12-237, y 390-580. In HOVER a node info panel replaces the lower space at x 12-243, y 590-805.
- Top-right mechanic panel x 1305-1555, y 10-145 (Halcyon THE EYE, Orbital THE RETARGET CYCLE, Rebel SYNC STRIKE, Solace THE SEQUENCE). Meridian has none in the supplied frame.
- Bottom legend x 280-1190, y 840-875 (varies a little per corp); DECISION | OVERVIEW toggle x 1318-1555, y 845-870.
- The usable scene area is therefore roughly x 245-1555, y 105-835 at 1568 scale (matching the spec's 300-1900 / 138-1012 at 1080p).

## 6. Comparison table: the other corps' DECISION and HOVER frames

All estimates from downscaled images; "uncertain" where noted. Elevation is the apparent view angle from the horizontal; the spec table gives the intended pitch ranges for comparison.

| Corp | Camera elevation estimate (spec pitch range) | Landmark share of frame | Current room / options placement | Landmark placement (thirds) | UI differences | Hover difference |
|---|---|---|---|---|---|---|
| Halcyon | about 15-25 deg, looking up the pyramid face (spec 13-24) | very large: the pyramid fills about 65-75 % of the width and nearly all the height (uncertain) | current + options on the bottom tier (y about 685) and top tier (y about 245); the route climbs the central axis | centered, apex near the upper third; TARGET circle at the top centre (x about 840, y 165) | THE EYE panel top right; legend includes "in the eye", "climb" | outside the branch is dark with the pyramid faces still faintly visible; branch rooms and orange link bright |
| Orbital | about 25-35 deg (spec 16-26; uncertain, the frame reads steeper) | large: the tower, ring and base fill about 55-60 % (uncertain) | current room near center (x about 890, y 490); options above (TARGET at x 895, y 305) | tower on the vertical axis, ring on the lower half | THE RETARGET CYCLE panel top right; legend adds "override" | the grade is strong; ring and dishes fade to near black; branch and red override link bright |
| Rebel Cell | about 20-30 deg, a side view (spec 17-19, DECISION is the side view at yaw 0) | the whole frame is the alley section; lanes span about 80 % of the width | rooms spread across two lanes (y about 240-500 and 650-720); TARGET at the right edge (x about 1520, y 400) | no single landmark; the section cut reads as a band | SYNC STRIKE panel top right | the signage and buildings fade; lanes and rooms stay lit |
| Solace | about 20-30 deg (spec 12-26) | the two helix towers fill about 45-50 % of the width, centered | current room at the lower left tower (x about 645, y 550); options at the upper tower (y about 215) and the right tower (y about 500) | towers off-center, bridges cross the center | THE SEQUENCE panel top right; legend adds "unread" | the city fades fully; towers keep a white edge; branch lit |
| Meridian | about 30-40 deg, a close high 3/4 (the v3 camera was pitch 36-38; supplied DECISION looks steeper; uncertain) | the wall and gantry fill about 60-70 % of the frame, cropped; the full Pi is not visible | current room at about center (x 920, y 485); options upper right (y 180, 330) | the wall runs diagonally; the room sits near the center | no mechanic panel in the frame; legend has no corp item | the hover frame is the darkest of all; the wall edges fade; branch and links bright |

Common to all five (verify Tethys matches):
- The DECISION frame is a full 16:9 plate with the UI over it, the landmark fills most of the middle and the current room is near the usable-area center, with the TARGET circle in the upper half.
- The HOVER frame is the same camera with a clear darkening outside the branch, the hovered room tagged, and the hover info panel at the lower left.
- Mechanic panel at the top right where the corp has one.
- The landmark share is large (about 45-75 %); the OVERVIEW supplied for Tethys shows the station at about 25-30 % of the width (uncertain), so the DECISION camera must come in noticeably closer than the supplied OVERVIEW and the supplied closeup, or Tethys will look small next to the others.

Tethys targets (ASSUMPTIONS to verify): station and the current pier cluster fill about 50-60 % of the width; elevation 34-42 deg; current room within 0.1 frame width of the usable-area center; TARGET in the upper half or the left-center and inside the safe area.

## 7. Verification list for the art-pass session
1. Render D1 at the proposed pose and check that the Black Smoker is still visible through the calm ring (the OVERVIEW placement was tuned to yaw 135, pitch 50).
2. Measure 12.1 and 12.2 on the no-UI plate with the object-index pass; report the median-based landmark ratio, not the 99th-percentile helper.
3. Re-run the occlusion rule for the new orbit, including drowned towers that stand out of the water.
4. Check every option opening against stilts, breakwater and rings (8 % rule).
5. Render D8 from the same plate and room polygons; confirm the mean luma stays above 0.05.
6. Compare thumbnails with the five other corps at 320 px for share and elevation.
7. Confirm the legend and mechanic panel carry only game-approved items (see Q2).

Q: Q1 (art director): the see-through window is tuned to pitch 50 and yaw 135, but the other corps' DECISION frames are lower. Do we accept a lower pitch (about 38) and re-place the server so it still shows through the calm ring, or hold pitch near 45-50 and accept a higher view than the other corps?
Q: Q2 (designer): is the BALLAST TIDE panel, and the flooded / airlock link states, approved as game mechanics for these frames, or should the top-right panel be neutral?
Q: Q3 (art director): the pods are small (drum r 2.5-4.2 BU). At DECISION should the current room and options be on the large pier-end and inner pods, or on the station's own decks, to hit the 46 px readability target?
Q: Q4 (art director): the supplied other-corp HOVER frames use the older, milder cut. Should Tethys use the new ruling (x 0.20, 70 % desaturation, branch x 1.35) and the other corps be re-rendered later, or should all hover finals share one value now?
Q: Q5 (designer): the station peaks at about 3.7-3.9x its surroundings. Is a warning-level ratio acceptable for the DECISION frame, given that closer framing will raise it further?
Q: Q6 (art director): should a whale be allowed in the DECISION frame as background life, or frozen out of frame so no sticker or opening competes with it?
