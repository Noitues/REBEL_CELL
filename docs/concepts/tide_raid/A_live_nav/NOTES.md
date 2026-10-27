# Tide raid, direction A "Live Nav"

**Thesis:** the Solace raid is a turn-by-turn route problem on a living night-city map: every beam is a route ribbon laid on the Grid, HOME is the destination pin, the forecast is traffic colouring, and the playout is a live trip progress bar with "road closed" and "you have arrived" moments, so the whole loop reads with no sentences.

Concept art only: every frame is composited in Python over the real Godot plates (`plates/city_noraid_nonet.png` plus the coords JSON for the `decay` scenario, `lost` for CITY LOST), nothing is committed to the game tree. Rebuild: `python scripts/build.py` (all frames, about 8 min) then `python scripts/post.py` (squint strips, deutan/tritan, sheet.jpg).

## Files
- `sheet.jpg` all beats in order, each with its 320 px squint and 4 px blur strip.
- `frames/` 1920x1080: `01_decay`, `02_draw`, `03_plan`, `04_forecast`, `05_response`, `06a_playout_shield`, `06b_playout_home_hit`, `07_aftermath`, `08_hq_step`, `09_city_lost`, `10_forecast_ALL_PANELS_REMOVED` (the pass/fail proof: map marks, glyphs and the HUD only; no route list, no hand, no mode chips).
- `squint/<frame>_320.png` and `<frame>_blur4.png` (4 px Gaussian at 1920 scale).
- `colorblind/` deutan and tritan (Machado 2009, severity 1.0, linear RGB) of forecast and both playout frames.
- `scripts/` `lib.py` (SDF ribbon rasteriser, grade, glyph atlas), `ui.py` (pins, bubbles, HUD, cards, Bloom, traffic, lens), `scene.py` (geometry, lane offsets), `build.py` (frames), `post.py`.

## Research (what I take, what I avoid)
Web searches returned thin first-party detail for Google/Apple; the design points below are marked (V) where a source supports them and (K) where they come from my own knowledge of the products.
- **Google Maps route line / 3D / Immersive View.** (V) Mapbox and Maps-style navigation docs describe a route line with a darker casing beneath it, a thinner grey alternative route, and ETA colour (orange = delay, red = heavy) ([Mapbox route line](https://docs.mapbox.com/android/ja/navigation/guides/ui-components/route-line/), [BGR on ETA colours](https://bgr.com/2222643/google-maps-eta-time-color-meaning-explained/)). (V) Immersive View for routes previews each step in a 3D city with a time slider ([9to5Google](https://9to5google.com/2023/10/26/google-maps-immersive-view-routes-2/)), and the March 2026 navigation update shows buildings, lane and crosswalk highlights in 3D ([Droid Life](https://www.droid-life.com/2026/03/12/google-maps-navigation-gets-biggest-update-in-a-decade/)). TAKE: thick cased ribbon with flow chevrons, grey ghost alternates (our sealed A/B/C), ETA bubbles on the route (our order/letter bubbles with tier pips), traffic colouring per segment, the junction-view callout (our lens in `06a`). AVOID: the whole base map muted to white; our city keeps its cel-and-ink identity and only changes grade.
- **Apple Maps 3D city.** (K) Calm, desaturated base with saturated route and POI, soft ground shadows. TAKE: the calm base (I regrade the plate toward lit steel-blue, roads/parks/windows keep colour). AVOID: photoreal.
- **Waze.** (V) Map reports are small iconic badges (police, hazard) placed on the road ([Waze icons](https://www.ridester.com/waze-icons/)). TAKE: defenses as planted road-block barriers with a type flag, plus small live traffic dots with trails. AVOID: the cartoon mascot tone.
- **Cities: Skylines info views.** (V) Traffic view paints roads red by congestion; third-party notes confirm it is a whole-map colour mode, not per-lane. TAKE: colour the lane itself by outcome (our forecast bands). AVOID: switching the whole map to a mode; the forecast stays on the live map.
- **Frostpunk.** (K) The city is a clock; rings and radial gauges around the core. TAKE: a decay clock ring on a DOWN pin that fills toward TAKEN (frame 01, and a quarter ring at aftermath), and the territory-wide Bloom as the readable "temperature". AVOID: its heavy text ledgers.
- **Watch Dogs ctOS.** (K) Profiler tags popping off targets. TAKE nothing structurally (that is direction B); only the CRT chip vocabulary for the HUD. AVOID: scan-wireframe overlays on buildings.
- **Into the Breach.** (V) Every enemy action is telegraphed on the board with the damage shown, so the puzzle is wordless prediction ([GameSpot](https://gamespot.com/reviews/into-the-breach-review-a-mechanized-masterpiece/1900-6416865/), [Game Developer](https://gamedeveloper.com/game-platforms/road-to-the-igf-subset-games-i-into-the-breach-i-)). TAKE: forecast shows the consequence on the thing itself (segment colour, pin ring colour, the -4 on HOME), not in a table. AVOID: arrow-per-attack grid (that is direction C).
- **Mini Metro.** (K) Parallel coloured lines sharing a track are offset side by side, flat colour, station glyphs. TAKE: lane offsets so beams on the same street run side by side; type glyph stations in the bubbles. AVOID: 45/90 straightening (the streets stay the real iso streets).
- **Own 1: Mapbox/Citymapper-style route progress.** (V for the casing/traveled styling) The travelled part of a route is restyled while the remainder stays dim. TAKE: the playout fills the ribbon as a progress bar with a puck head. AVOID: greying the travelled part (ours stays bright, the untravelled part dims).
- **Own 2: Uber/Lyft pickup pin and arrival pulse.** (K) Destination pin with a ground ring that pulses on arrival. TAKE: HOME hit as a destination alert pulse. AVOID: car icons.

## Medium mapping (ART_BIBLE 1.2 vocabulary) and departures
- City map: the shipped cel and ink city, regraded (see Godot look). Netwire stays neon cyan on top ("the Grid stays night").
- Cards: vinyl sticker cards (white die-cut rim, peel curl corner, type pip, flame cost). Placed cards leave a dashed ghost slot. INFECTED cards are plum with the red X.
- HUD: CRT chips (cut corners, scanlines). Departure: HOME/HEAT/deck are three floating chips over a bright map instead of one bar.
- Corp paper: ETA bubbles are paper-white, and the verdict is a corp paper tag with a rubber-stamped word (`07`) and a stamped plate on CITY LOST.
- Grease pencil D28: yellow slash = DOWN, red X = TAKEN, yellow arrow with dark under-shadow for the dragged card. Near-opaque, thick, under-shadow, as in DIRECTION_REVIEW.
- Binary bits and shards (module 16): the burst on a stopped beam and on HOME.
- Glyph atlas: shield (GUARD), curved detour (SHIFT), zigzag (JAM), house, flame, skull; type shapes triangle = D, square = N, circle = E as in the shipped chips.
- **Departure A: Enforcer hue.** The shipped E glyph is orange, which collides with the DAMAGED tier orange now ruled. E is chalk-white here. Needs a designer ruling.
- **Departure B:** barriers and pins are paper-white objects on the map (nav-map objects) instead of the shipped neon hexes.

## Palette (hex)
Ruled tiers: UNTOUCHED/EVADED `#B8FFF2` (mint cyan-white), HOLDS `#19C9B4` (teal), SITES LOST `#FFB21E` (amber), DAMAGED `#FF6A1A` (orange), BREACHED `#FF3347` (HARM red; the skull on `09` is paper-white on plum, the red is the vignette and stamp).
Beam types: D `#3D86FF`, N `#FF40D6` (with a white-hot core line in each rail so it reads on plum), E `#F4F7FF` chalk. Sealed ghost `#C7C2E6`.
Bloom: body `#1A0B1F`, mid `#4A1440`, veins `#FF3FA8`, hot front `#FFD6F0`. Netwire `#62E6FF`. Ink `#0C0720`, paper `#F6F1E4`, HUD navy `#0A1330` with cyan `#5BE3FF`. Pin body indigo `#2B2278`. Grease yellow `#FFD800`, red `#FF2A2A`. Lime `#C6FF2E` appears only as the focus halo (drop target in `03`, the chosen chip in `05` and `08`).

## How each beat reads with no text
Short words used: the four RESPONSE verbs under their icons, the verdict word DAMAGED, CITY LOST. Numbers: HUD counters, order digits 1/2, letters A/B/C, prices, -4.
1. **DECAY (`01`):** DOWN pin with a ring clock nearly closed beside a pin already stamped with the red X; the plum Bloom grows out of the taken site along the street; two plum INFECTED cards fly to the deck chip, which ticks 2 to 3.
2. **DRAW (`02`):** the two known routes are being drawn out of the corp origin pin (light column, scan heads), dashed blue D and white chevroned E; the hand fans in from the left with smear.
3. **PLAN (`03`):** known routes full-strength, sealed A/B/C as thin grey ghost alternates with type glyph + letter bubbles, the hunter as a fork bubble; white drop rings on every district a known route crosses, the lime ring on the one being aimed at; the dragged card with a yellow arrow; barriers standing on the ribbons (the D barrier on the white E ribbon is faded = does nothing).
4. **FORECAST (`04`, `10`):** each segment is coloured by outcome like traffic: mint corp land, amber then orange approaching HOME on the unguarded route, teal where the D barrier stops the D route, then a grey dotted dead stretch. ETA bubbles carry tier pips; the HOME pin carries the 12-pip odds bar (worst to best). `10` is the same frame with the route list and hand removed.
5. **RESPONSE (`05`):** four mode chips (arrow into a ground ring, shield with pause bars, swap arrows, flame on a pin), lime on the chosen HOLD; sealed A is revealed as a full ribbon, B and C fade.
6. **PLAYOUT (`06a`, `06b`):** the ribbon fills as the route progresses with a typed puck at the head. Stop: hex shield flash on the barrier, beam head crumbles into bits, a teal "road closed" sign on the ribbon, the rest of the route dead-dotted, plus a junction-view lens with the hero marks drawn big. HOME hit: the ribbon reaches the destination pin, orange pulse rings, binary burst, the pin turns orange, the HUD HOME chip shakes to 40 with -4.
7. **AFTERMATH (`07`):** spent ribbons thin out, DOWN pin has a yellow slash and a quarter-ring decay clock, the Bloom has grown, the orange ring under HOME and the stamped DAMAGED tag with a broken heart.
8. **HQ STEP (`08`):** five action coins with prices (patch +, repair wrench, clean card, cool snowflake, build), lime on REPAIR, and its route drawn from HOME to the DOWN site with a wrench pin pulsing there; a chevron "go" button finishes the step.
9. **CITY LOST (`09`):** the Bloom floods the whole territory, every pin X'd, deck strip all plum past the lost line, red vignette, big skull, stamped CITY LOST.

## What build would have to change (layout and flow spec list; none implemented here)
1. Raid screen has no right-hand panel: the 3D city fills the screen at a tighter camera (about 1.55x the shipped raid ortho zoom, framed on HQ to HOME).
2. Beams become cased route ribbons (D dashed, N double rail, E solid + chevrons), lane-offset where they share a street, fill colour switchable between type hue and tier traffic colour.
3. A route list chip stack (pattern swatch, type glyph, 1/2/A/B/C, tier pips) replaces the plan text; hunter as a fork chip.
4. ETA bubbles on each ribbon with order/letter and tier pips; HOME pin carries the 12-pip odds bar.
5. Sites render as map pins on the street node with tier size, badge icon, state mark (D28 helper), decay clock ring, tier threat ring in forecast.
6. Defense cards become barrier, detour sign and jam sign standing on the ribbon at the district junction (not on the pin); mismatch is a faded barrier.
7. RESPONSE is four icon chips; HQ STEP is five priced icon coins plus a go button; lime halo marks the chosen one.
8. Playout drives ribbon progress (smax), puck, shield flash, bits burst, road-closed marker, destination pulse; a junction lens spawns on stops and hits.
9. Bloom is a world-space region around TAKEN sites (shader, ground-plane footprint), growing per decay; CITY LOST floods all of it.
10. Short-word set to localise: four verbs, the verdict word, CITY LOST.

## What the Godot look would need
- **Grade:** a day-ish street grade of the same city: violet tower bodies rotated toward lit steel-blue (hue shift about -40 deg and 40 percent less saturation on the purple band, plus value up), gamma 0.64, 1.5x saturation on everything else, mild contrast curve, a calm blend (about 38 percent soft) so ribbons win over window noise, top haze and a corridor vignette. This is a colour-grading post pass, no new assets.
- **Window bloom** on lit windows and roof signs (done in the concept by thresholded blur).
- Ribbon shader with arclength and lateral coordinates (the concept uses a signed distance field per route: dash, rail and chevron masks, casing, light halo, additive glow).
- Traffic dots with trails on the Grid links (GPUParticles on link paths).
- Bloom necrosis shader: metaball field warped by noise, Voronoi veins, hot hairline at the iso-flattened front, windows dying near the front.
- The ground-plane "lens" callout needs a second camera render target for crispness; the concept fakes it.
- Frames are an upscale (1.55x) of a 1920 plate, so they are softer than Godot at native.

## Risks
- Amber (SITES LOST) and orange (DAMAGED) collapse under deutan and are close under tritan (see `colorblind/`). The ruled hues do not separate in that vision; I would add ribbon chevron density or pip height per tier. Shape cues for D/N/E hold (dash, double rail, chevrons, glyphs).
- The t1 cluster near HOME is dense (pins, barriers, bubbles on one junction); real placement needs declutter rules.
- Lane offsets get wide when five routes share a street (plan/forecast near HOME).
- Forecast colouring semantics (which segment gets which tier) are mine; build owns the rule for what a beam does to the Sites it passes.
- White chalk E ribbon on a pale base relies on its casing and glow; it is the weakest hue contrast.
- Sealed routes are drawn as ghost ribbons with their type because the shipped plates show them; if the rules want paths hidden, show only the letter bubbles at the HQ.
- The story across frames is illustrative: pips, the DAMAGED outcome, -4 and who fires first are authored for the concept, the sealed A reveal differs from the plate JSON ordering.
- The lens (`06a`) is the least resolved piece: soft background, and it overlaps unused map.

## Self-critique per frame (squint test, see sheet.jpg)
- 01 decay and 07 aftermath: Bloom blob and red X read; the tag and orange ring read at 320 px. Decay is quiet beyond the Bloom.
- 02, 03, 05: the dominant read is the pair of ribbons; at 320 px type differences (dash vs chevron) survive, the hand and chips read as one dark band.
- 04: the orange run into HOME and the mint/teal split read at 320 px and with 4 px blur.
- 06a: the blue fill and lens read; the shield flash itself is small.
- 06b: the orange burst at HOME is the strongest signal in the set.
- 08: weakest at squint (dock and repair route are small).
- 09: reads instantly (skull and red vignette).
