# HQ netrun: REBEL_CELL / DISPATCH, "Sync Strike" (2026-10-15, option A)

The DISPATCH finale in the approved route-map look (AAA-2 r3) with the designer's HQ lighting rule. Revised the same
day after the designer's review: **no landmark tower** (the first version's DISPATCH stack is archived in
`D:\rc_scratch\hq_rebel_cell\v1_core\`); the district is the bible's normal street grid with the fist drawn in red
windows; the red is **subtle until the blackout** and then spreads through the fist; three concept options were
proposed for Sync Strike and the designer picked **option A: three stacked lanes in one side-view section**. Only A is
rendered (option C's graph and build stay in `scripts/` as `hq_graph_C.py` / `hq_build_C.py`, unused; B was never
built). Nothing is committed; Cycles HIP in the shared GPU queue; Eevee for layout previews.

## Files

| File | What it is |
|---|---|
| `H_overview.png` | Option A, the whole section: the rooftop lane (BREAKER), the street lane (GHOST), the service tunnel (RIGGER) under the street, all three mid-run; the kill-switch column, the service shaft, DISPATCH (TARGET) in the palm row's building. |
| `H_decision.png` | Mid-run (step 2): the two roof / tunnel detours chosen to wait for the GHOST's COUNTERED stall; the SYNC dial: all three at their switches on step 5. |
| `H_hover.png` | The same, hovering BREAKER's detour: the power cut, the lane's branch, the rule note. |
| `H_switch.png` | The kill-switch moment: all three switches THROWN on the same step; the fist's lines pulse red. |
| `H_showdown.png` | The convergence: two operatives PARKED at their switches (support), the third takes the shaft into DISPATCH. |
| `H_red_1_before.png` .. `H_red_4_full.png` | The red sequence from above (no UI): an ordinary district (the fist barely hinted), the BLACKOUT (the ring and the hand's lines go dark), the red SPREADING from the palm, the FULL fist. |
| `H_mechanic_states.png` | The sheet: the red sequence, the three option A frames, the rules (real vs proposal), the GDD questions. |
| `H_reveal.mp4` / `.gif` | 6.5 s HQ beat = the red sequence in motion (the round 34 blackout reveal, then the spread). |
| `plates/`, `scripts/` | Plates without UI; everything to rebuild. |

## 1. The district and the section (`scripts/rc_district.py`, `hq_graph_A.py`, `hq_build_A.py`)

| Element | Rule |
|---|---|
| District | A 12 BU block grid (9 BU blocks, 3 BU streets) over the fist's box plus a margin; one continuous city (the hq_kit ring beyond). Each block is classified from the round 15 fist glyph (`fist_mask.py`, cropped, 5 samples per block): FIST, a fist LINE (finger splits, thumb edge, cuff: windowless after the blackout), the blackout RING (round 34), or plain. |
| Windows | One shader for every block, two values per frame: `SEQ` (0 before: ~8 % of the fist's lit windows red and dim; 0-1 the sector washes out, then the ring and the lines go dark; 1-2 the red spreads from the palm, a front `spread_r` x (SEQ - 1); 2-3 full: 85 % red at full strength; the fist's roof skylights join in, so the fist reads from above) and `PULSE` (the kill switch: the LINE blocks glow red). The red stays a lit-window effect. Netrun frames use SEQ 2 (the fist lit, not at full blaze). |
| The section (option A) | Derived from the real grid (the designer: future netruns from real map lots, one continuous city): the cut is a street line of the block grid (`stack.cut`) just south of DISPATCH's row at the palm; blocks south of it and the ground in front of it are removed (a dollhouse); the first row behind it hosts the lanes: its blocks under the lane rooms become LANE BUILDINGS (ground floor = the street rooms, roof = the rooftop rooms; their windows still follow the fist sequence). The EARTH under the street is cut open: the service TUNNEL (third lane) and a deeper level for its detour. |
| Lanes | L BREAKER on the roofs (detour: over raised roof huts), C GHOST at street level (DISPATCH counters C2: STALL +1), R RIGGER in the tunnel (detour: the deeper level). 3 rooms + a KILL SWITCH each; the switches in one column; the SERVICE SHAFT beside it joins the three levels to DISPATCH's server floor. |
| How it generalises | A section = (a street line of the grid, a run of lots along it, the target lot). Any district can host the same three lanes: the roofs and ground floors of the lots along the line, the utility corridor under the street. |

## 2. Preset variant
r3 look; `PRESET["hq"]`: Cell red #E8141E for the windows, DISPATCH red for the switches / the shaft, per-operative
accents (pink BREAKER, cyan GHOST, green RIGGER: token frames and a thin edge line beside their wax only; the route keeps
lime / orange / white / grey), the window sequence numbers (`win_k`, `red_before_p`, `red_k`, `red_full_p`, `wash_k`,
`spread_r`, `pulse_k`), the section (`stack`). `HQ_VARIANT` (A | C) and `HQ_DISTRICT_ONLY` pick the build.

## 3. The mechanic: GDD vs proposal

| What | Source | Status |
|---|---|---|
| REBEL_CELL = the final unlock campaign built from your profile; elites use your wheels (M11: mirror elites x1.5, one pointer, your Daemons); the final boss is DISPATCH | GDD 8.5, M11, 8.2 | **Real.** Every elite wears MIRROR. |
| The district: a normal grid, the fist in red windows (90 % for DISPATCH), the blackout reveal | Bible 4.4, round 34 | Art direction, kept; the slow spread after the blackout is the review's. |
| SYNC STRIKE: three operatives, three kill switches thrown on the same step, a lone throw re-arms, DISPATCH counters a lane, ONE enters the showdown | Round 43 decision + the review | **Proposal** (not in the GDD). |
| STALL +1 on a countered room; detours (+1) to stay in step; the parked two as support | This round | **Proposal**. |

### GDD questions (for DECISIONS.md)
1. **Turn order**: do all three choose at once each step (as drawn: one step = three moves), or does the turn rotate between operatives?
2. **HP / RAM**: shared between the three, or each operative its own (the stationed crew)?
3. **One operative dies** before the switches: does the strike fail (retreat), or can the other two finish with a lone-throw penalty?
4. **The parked two in the showdown**: what support (a passive buff per class, a card each, absorbing DISPATCH's counter-attacks)?
5. **Mirror combats** (round 43 / M11): every elite (as drawn) or one per lane?
6. **Decks**: one deck or one per operative (round 43 open question; proposal: one per operative)?
7. **The countered room**: chosen from the player's most-used firmware (GDD 8.5 "built from your profile")?

## 4. Camera beats
| Beat | Rule |
|---|---|
| DECISION | The side view (the V3 dollhouse): straight at the section (yaw 0), nearly level (pitch 5-8), framing the three operatives and their options; each step it slides east along the street with them. |
| OVERVIEW | The whole section (pitch 7). |
| REVEAL | The red sequence from above (whole district), then the camera settles lower. |

## 5. Godot 4.7 mapping
| Element | Godot | Perf |
|---|---|---|
| District | One MultiMesh of blocks with per-instance category + height; the window shader reads the category and two global uniforms (`seq`, `pulse`). | 1 draw. |
| Section | A clip plane (or simply not spawning the lots south of the cut) + an earth mesh with the tunnel cavities; the lane buildings as scenes on their lots. | Small. |
| Lanes, tokens | Room scenes, 3 tokens with accent frames, the shaft as a scene. | ~17 rooms. |

## 6. Value checks and render log

| Still (2560 x 1440, 64 spp) | median | < 0.10 | > 0.85 | landmark / local background |
|---|---|---|---|---|
| H_overview (the section) | 0.157 | 22 % | 1.5 % | 0.171 / 0.116 = 1.48 |
| H_decision | 0.092 | 54 % | 1.1 % | 0.106 / 0.073 = 1.46 |
| H_red_1_before (from above) | 0.010 | 87 % | 0.1 % | 2.2 |
| H_red_4_full | 0.013 | 80 % | 0.1 % | 3.6 |

The section frames meet the landmark rule (~1.5x). The red sequence frames are far too dark overall (median ~0.01):
the overhead view looks down through the fog onto window-lit blocks with no street light; the fist reads, the frame
does not meet the r3 median. Fix for a next pass (light, not exposure): street lamps on the grid's streets and a
brighter `win_k` for the plain windows in the before / blackout beats.
Render log (one locked batch with Orbital's reveal): stills 201 s, the 3 option frames 211 s, the 4 red frames 252 s,
the reveal 156 frames in 696 s; compose 97 + 91 + 100 + 125 s, encode 13 s.

## 7. Gaps for the tools step
- The lane rooms' x positions and roof heights are preset numbers along the cut line (the cut and the lots are from the grid).
- The countered room is a preset id.
- The fist's box is a preset; the ring radius is a preset.

## 8. Open questions for the designer
See the GDD questions above; plus: does the netrun show the fist at full blaze (SEQ 3) or lit (SEQ 2, as drawn)?

<!-- hq_rev v2 r2 -->
## v2 revision, round 2 (hq_rev)

### v2 round 2 (art director 20:55)
- No fog plane. The fog volume starts at the kerb (`hq_fog.box`). The bottom of the frame is THE UNDERCROFT
  (`rc_undercroft.py`): the service tunnel (lane R) opens on its camera side onto a sunken service street one level
  down, a Tokyo two-level street. This keeps the three stacked lanes: L roofs, C the alley, R the tunnel.
  - The section face at the kerb is a retaining wall. It has a lit fascia band over the tunnel's arcade, multilingual
    blades in clusters between the rooms, pipes and a kerb railing.
  - Beyond the tunnel, undercroft shops (lit fronts and boards, or roll shutters) line the wall.
  - The lower floor is wet asphalt with puddles and sign reflections, 84 BU deep. It has yatai stalls with lanterns
    (never in front of a room), scooters, crates, and utility poles with sagging cable bundles up to the kerb, plus
    lantern strings.
  - In front of the deeper detour rooms (R2a / R2b) a sunken PIT with a stair keeps them open to the camera.
  - Thin dark LOW FOG STRATA (a 6 BU volume, layered noise, density 0.02) lie over the lower floor.
  - The camera looks down a little more (pitch 17-19, was 11-14).
- The MAINFRAME v4 red sign is the large hero landmark (`mf_w` 11 BU wide, about 45 BU tall, standing off the shop
  between the drop and lane 1 on brackets, with its own spill and floor wash). The red fist hologram is secondary
  (`fist_s` 20).
- The rooms are places in the alley look, not grey blanks (`rc_alley._rooms`):
  - street rooms: half-rolled shutters with tags, lit shop boards, paper lanterns and a counter;
  - roof rooms: corrugated rooftop shacks with bulb strings and a lit blade;
  - tunnel rooms: pipe runs, cage lamps and a status board.
  - The interiors are tinted dark (`room_inner`).
- Red sequence:
  - The arterials inside the blackout ring go dark in RS_2 and red in RS_4 (`rc_alley.seq_lights`).
  - The fist is the crest fist outline (`rc_fist_v2.py` -> `fist_mask_v2.json`), rasterised to the block grid by
    majority. A line is a block whose centre or 3 of 5 samples are line (was: any sample). The fingers keep the
    crest's widths, and the gaps are one street-line wide, so the top-left finger no longer reads as a "U".
  - Slight bloom (`post.bloom` 0.20 / 0.17 / 0.13, threshold 0.9) and a denser low haze (`hq_fog` peak 0.011, height
    28, haze 0.0009) let the red bleed into the air.

### Occlusion: camera-rig rule (v2, all five HQs; designer note 2026-10-15)

Designer, verbatim: "The foreground blocking buildings should be flattened or made transparent when the camera needs to
look through them to see the HQ." This replaces the v2 sloped section cut. Code: `hq_kit/downtown.py`
(`occlusion_params`, `occlusion_state`: pure python, the rule itself) and `hq_kit/section.py` (the same rule as a
clip in the city materials). Called per frame from `hq_jobs.frame()`; `hq_scene` logs how many buildings it touched.

| Step | Rule | Numbers (`downtown.OCC`, a corp may override in preset `downtown.occ`) |
|---|---|---|
| Inputs | The camera position, and the TARGET VOLUME: the front points of the active room plus the visible route nodes (decision / hover: the current room + its options; overview: every route node). | - |
| Cone | Every ray from the camera to the target volume. Horizontal frame: `u` = the direction to the targets' centroid. Per target: lateral tangent `t = across / along` and vertical tangent `v = (z - cam z) / along`. Only targets **behind** a building can be hidden by it, so the cone is sampled at `NK` depths (knots) from the nearest to the farthest target. At each knot it holds `[t_min, t_max]` and `v_min` (the lowest ray) over the targets behind that depth, widened by `margin` of the whole volume's span (the ~10 % margin). | `margin` 0.10, `NK` 5 |
| Occluder | A city building is an occluder when its footprint (radius = half-diagonal) overlaps `[t_min, t_max]` at its depth, it stands in front of the farthest target, and its top reaches into the cone (`(top - cam z) / (along + r) > v_min`). Compound geometry is never an occluder. | - |
| Step 1: FLATTEN | An occluder is section-cut to a lit stub of `stub` BU (1-2 storeys: shop fronts, awnings and the lowest windows stay lit). Its open top shows a near-black POCHE, so it reads as a cut model and not as a hollow shell. | `stub` 6.4 BU |
| Step 2: GHOST | If the stub still reaches into the cone, it fades to `ghost` opacity. Its window dots stay (dimmed with it) and a faint cool edge line traces its box edges. It is never fully invisible. | `ghost` 0.18, `edge` 0.6 |
| Outside | Buildings outside the cone keep their full height. Roof clutter (tanks, antennas, holo boards) is cut with its building. | - |
| Easing | The cone has soft borders (`tsoft` lateral tangent, `vsoft` vertical tangent). As the orbit camera moves, a building's cut height and opacity slide across the band and never snap. In the game the values are per-instance targets eased over 0.4 s (below). | `tsoft` 0.035, `vsoft` 0.025 |
| Outputs | Per building: cut height (`top` + clutter outside the cone, `stub` inside, interpolated across the soft band) and opacity (1, or `ghost`). `occlusion_state(params, building)` returns exactly these values. | - |

Godot 4.7 mapping (camera rig, not content):
- The city is MultiMeshes. Each instance carries `INSTANCE_CUSTOM = (cut_height, opacity, centre-relative edge
  data)`. Each frame the camera rig (a `RefCounted` helper fed by the orbit camera, outside the deterministic core)
  runs `occlusion_state` per building in the near rings and writes the per-instance target.
- The view tweens each instance's current value toward its target over 0.3-0.5 s (0.4 s default, ease in-out), so
  buildings never snap when the cone sweeps across them.
- City shader (spatial, opaque pipeline): `if (world_vertex.z > cut_height) discard;` gives the per-instance height
  clip. A back-face branch draws the poche colour, so the cut reads as solid.
- Ghost: a dithered alpha fade (an alpha-hash / screen-door `discard` against a 4x4 Bayer threshold scaled by
  `opacity`), which keeps depth sorting stable without a transparent pass. Edge lines come from the box-local
  distance in the same shader. The window emission stays on and is multiplied by `opacity`.
- Cost: one uniform block, one per-instance vec4, no extra draw calls.

<!-- hq_rev v2 full -->
### v2 full render: tweaks after t2 (art director)
- The two-level street is confirmed. The bottom of the frame no longer smears. The undercroft floor has its own wet
  asphalt (`uc_floor`): matte dry asphalt (roughness 0.55) with small SHARP puddles (roughness 0.03) that mirror the
  stalls, lanterns and signs crisply. It replaces the kit's glossy tiled ground (roughness 0.26 everywhere), which
  blurred the whole floor's reflections. The low strata are thinner (4 BU, density 0.012).
- MAINFRAME at 9.4x its background is accepted as a neon-on-dark exception (spec Q5).
- Red sequence: more haze bleed. The fist glow (light-linked to the fog) is up to 4.5e4 and the district fog peak to
  0.013, haze 0.0011, so the red tints the air above the fist; the RS values stay dark.
