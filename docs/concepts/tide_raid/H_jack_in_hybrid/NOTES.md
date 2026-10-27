# H "Jack-in over the Night City" (hybrid concept set, for the designer's sign-off)

**Thesis:** the real vivid night city with the Cell's jacked-in data layer on top. ICE data-towers stand on the Sites only, every raid line is ONE cased, chevroned route ribbon on the real streets headed by a type-silhouette daemon, and the forecast, response and verdict live on the targets, on HOME and in the Cell's hand-made marks. No panels anywhere.

Frames are 1920x1080 in `frames/`: 01_decay, 02_draw, 03_plan, 04_forecast, 05_response, 06_playout_impact, 07_playout_home, 08_aftermath, 09_hq_step, 10_city_lost, 11_panels_removed, 12_reveal_sealed_hunter, plus 13_declutter_t1 (the t1 cluster before / after the declutter rules). `squint/` has `_320` and `_blur4` per frame and `check_1280_*` (04 and 07 downscaled to 1280x720). `colorblind/` has deutan and tritan sims (Machado 2009) of 04, 06, 07, 12. `sheet.jpg` is the contact sheet.

Story note: 01 uses the plates' `decay` scenario (two DOWN Sites turn TAKEN, INFECTED 3); 10 uses the `lost` scenario; 02-09 and 11-12 are one raid on the `default` scenario. Raid story: a D guard on t1_c stops both D beams; K2 first takes t1_b DOWN; the player hedged against D only, so the sealed N route C reaches HOME for -6; DAMAGED verdict; HQ step repairs t1_a.

## Element-by-element source map
| Element | Source | What changed in the hybrid |
|---|---|---|
| City grade | F | F's saturated night grade (sat 1.45, mids down, windows bloom, indigo shadows) applied to the real plate. Added: window yellow / orange is pulled toward warm white (so yellow = E beam only, orange = DAMAGED only); the plate's bright zig-zag banner (bottom right) is quieted. No blue grade, no city-wide wireframe, no data-shadow boxes, no lattice floor. |
| Sites | E | ICE towers (box / obelisk / stepped spire) on Sites only, alpha .66. Idle Sites in the cluster collapse to 45 percent stubs (declutter rule 1). |
| Network | E / A | Faint conduit rails on the real links under everything (the network is a street graph, not a decoration). |
| Beam body | A | One ribbon per beam on the street polyline: black casing, chevrons in the travel direction. Pattern is the second type cue: D dashed links, N braided double strand, E solid band with bold chevrons. At FORECAST the ribbon gets a tier-coloured rail either side (traffic colouring: the stretch leading to a Site takes that Site's predicted tier; mint = passes, teal = held, amber = Site lost, orange = HOME damaged). The beam itself keeps its type hue, so hue = type and rail = outcome. |
| Beam head | E | Head silhouette only: D swept arrow (blue), N square cursor with antennae (magenta), E horned ram (signal yellow, horns re-drawn as a lyre for the hybrid). Ghost outline heads at the stop point in FORECAST. |
| Sealed routes | E | Fog corridor (static, glyph rain, dashed rails) with a hex letter lock A / B / C that opens into the type silhouette (12). Corridors made wider and denser than E's. |
| HUNTER | E, fixed per CRITIC conflict 4 | WHITE eye. Two candidate streets in white dashes with a white E-ram ghost each; on lock a reticle snaps onto one street and the other fades under a strike. Never yellow until the beam it spawns fires. |
| Defenses | E | Hex-brick firewall on the Site (type-coloured edge, type glyph), decoy hologram + hand-off arrow (SHIFT), tracer (JAM, not drawn here). |
| Card hand | F | Vinyl cards, face colour = the beam type the card answers (D blue, N magenta, E yellow), die-cut paper border, verb glyph, type glyph in the corner. |
| Forecast | F + A + D | F's intent tile (hex plate, tier glyph, number) on every target on a hairline leader; F's grease-pencil tally at HOME (12 waxy tier glyphs grouped by tier = the odds); A's traffic-coloured ribbon; D's HOME tick ring with orange ghost ticks and a damage chip (-6). D's flat-line-at-the-fuse idea is the grey dotted remainder after a stop bar. |
| Response | F | Four stencil discs (DEPLOY / HOLD / MOVE / SACRIFICE), bone spray ring, three tier glyphs above each, one marker word below, lime halo on the pick (lime is used for nothing else). |
| Playout, stop | D / E | Hex shield flash, shockwave, binary bits, wall cells shatter, HOLDS tile pops. |
| Playout, HOME hit | D + E | Burst at the HOME deck, the 6 lost ticks fly off the ring as sparks, damage tile and -6, E's glitch tear, HUD HOME chip goes orange. |
| Aftermath | F + D28 | Wheatpaste verdict poster (one glyph, one word, tier colour, halftone, torn edge). DOWN = white grease double slash with a plum clock ring, TAKEN = red grease X. Burnt routes stay as grey dots. |
| Infection | D (+ E bloom) | Plum body, pink Voronoi veins, hot hairline front, windows dying behind it, tower stumps with X. CITY LOST: the plum flood over everything plus E's skull and a glitch tear, HUD counter tipped 11 to 8. |
| HQ step | E | Action coins around HOME (wrench 10, card-X 20, snowflake 25, double chevron = end), a cable to the DOWN Site, and a mint ghost of the repaired tower on the target. |
| HUD | F | HOME / HEAT chips top left; INFECTED (plum biohazard) vs healthy (card) balance top right with a tipping beam. |

Dropped as ruled: E's blue grade and side bars, D's copper and analyzer strip, F's paint-everywhere / outcome strip / legend stack, A's day grade, every text panel.

## Palette (hex)
Night ink 070515 / 0A0C24; ICE lattice cyan-white 7FEFFF, mid 2FB8E8; fog 9C8CFF. Beams: D 3D86FF, N FF40D6, E FFD800 (signal yellow, nothing else yellow). Tiers: UNTOUCHED/EVADED B8FFF2 (mint), HOLDS 19C9B4 (teal), SITES LOST FFB21E (amber), DAMAGED FF6A1A (orange), BREACHED FF3347 (HARM red, stamp), CITY LOST = skull HOT FFD6F0 on plum. Focus halo LIME C6FF2E only. Infection: plum 1A0B1F / 4A1440, vein FF3FA8, hot front FFD6F0. Paper F6F1E4, Cell paint (bone) F6F0DE. DOWN mark F6F1E4, TAKEN mark FF2A3A. HUNTER eye white.

## Text audit (hard fail: no wall of text)
Words anywhere in the loop: one word on each response disc (4), the verdict word on the poster, A / B / C on locks. Everything else is numbers (HOME, HEAT, counters, -6, 1, 10 / 20 / 25) and glyphs. No panels exist, so 11_panels_removed differs from 04 only by the card hand; the pass/fail check is that frame 04 minus the hand still runs the raid. The only boxes are the HUD CRT chips (allowed).

## Declutter (t1 cluster; shown in 13)
1. Idle collapse: a Site that is not a target and has no program or mark drops to a 45 percent stub.
2. One intent tile per target, fanned on hairline leaders, at least 66 px apart (screen px at 1920), pushed up and never onto a street (tiles are lifted off ribbons).
3. At most two ribbon lanes (plus or minus 13 px) in a cluster; sealed corridors sit on the centre lane under them.
4. Programs sit on the ground ring at the street side of the Site; the tile floats above the tower.
In the frames: t1_d is the idle stub, t1_b / t1_c have fanned tiles. Stress case (four targets) is in 13.

## Build spec: layout / flow changes (for build)
- Expose per Site: tier, state (healthy / DOWN / TAKEN), program slot (verb + type), "is target this beat", and the predicted tier for the beat (FORECAST).
- Expose per known beam: type, site_path, the stop site, and the predicted event list per Site (pass / stop / lost / HOME hit) so the ribbon can colour per segment.
- Per response option: a three-tier outcome preview. Per forecast: the 12-sample outcome tally (counts per tier) and the worst-case HOME ticks.
- Sealed-route reveal event per route (open lock, then fire) and a HUNTER lock event that picks one of its two streets.
- Lane assignment for beams sharing streets (K1 +13, K2 -13, sealed 0).
- Cluster logic: idle collapse flag and the tile fan (rule 2) as a layout pass.
- Remove PLAN / HQ STEP / AFTERMATH / RESPONSE panels; the verdict becomes the poster (one word + tier glyph); the INFECTED counter becomes the balance HUD chip.
- HQ step coins and the drag lime ring stay screen-space and world-anchored respectively.

## Art owns (tide_fx / tide_look / Palette / city3d grid Bloom)
- Palette: add the ruled tier ramp, E yellow, HUNTER white, tile plate colours; keep lime for focus only.
- tide_look: route ribbon shader (casing, three patterns, chevrons scrolling with the beam, tier rails), daemon head meshes (3), ghost head outline, stop bar, lock + fog corridor, hunter eye + reticle, intent tile / tally / stencil disc / poster sprites, grease slash / X / clock ring, vinyl card face colours.
- tide_fx: shield hex flash + bits, shockwave, HOME burst with ticks as particles, glitch tear (masked UV displace), plum flood, skull.
- city3d grid Bloom: the necrosis shader already matches (plum body, veins, hot front); add dying windows behind the front.
- Grade: raid-camera-only saturated night grade with the yellow/orange window desaturation; quiet the bright banner at the plate's bottom right.

## What the Godot look needs
ICE tower shader (translucent additive volume, edge lines, lattice bands; Sites only), the Solace cage as an additive cylinder, ribbon and head renderers on the street polylines (arc-length instancing), screen post (scanline, fringe, vignette) scoped to the raid camera, mask-limited glitch tear, a raid-camera colour-grade LUT (hue-band desaturation of yellow/orange windows), and the paint look for the Cell's marks (waxy edge noise, halftone, torn paper) as 2D sprites.

## Research (inherited; the round 2 notes of E, F, D, A hold the citations)
Google Maps 3D route ribbons (casing + chevrons, take; daytime grade avoided), Waze / Maps traffic colouring (take as the tier rails), Into the Breach (intent tile on the target, flat-ended stop bar), Mini Metro (one clean line per beam, no more than two lanes), Gibson / Ghost in the Shell (data layer sits on the city, never replaces it), Cyberpunk 2077 Breach Protocol (one highlighted next step; avoid its matrix UI), Jet Set Radio / Obey (the Cell's paint marks, poster). Own refs: hazard-striped plant machinery (E beam), braided cable macro (N), airport flight-path ghosts (forecast heads).

## Risks / weak points
- Hue by the beam is not enough in the squint: the mint (UNTOUCHED) rails and the cyan towers merge into one cold braid; D blue is lost at 320 px. Shape and pattern carry type, and the tier info (teal / amber rails, HOME chip) is small at the squint. Reads at 1920 and at 1280 (checked) but the cluster is the only place the tier colours really sing.
- Deutan: teal vs mint rails and amber vs orange collapse; the tier GLYPHS (shield, tower-down, cracked heart) keep it readable, the rails alone do not. The magenta and blue cards both go grey-blue; the type glyph on the card is the fallback. Tritan: blue beams on the purple city are the weakest pair.
- All three beam types are never co-visible in one frame (D in 02-06, N in 07, E in 12); the hand's type glyphs and card colours teach the code instead.
- Amber SITES LOST rail next to the E yellow is close; they separate by pattern (solid chevron band vs dashed D) and saturation only.
- Yellow cards and the yellow E decoy are type-coloured and read as "E", which dilutes "yellow = E beam".
- E horned-ram head is a busy outline at this size; the N cursor is plain next to it.
- The tower volumes are fake-iso overlays (painter order, no true occlusion); the helix on the plate is green and competes with the lime halo.
- Stills only: ribbon chevron flow, head slither, tile pop and poster slap-down are unproven in motion. Not drawn: DEPLOY / MOVE / SACRIFICE consequences on the map, the hunter's playout, the sentry-shield variant, MOVE ghost.
- Frame 01 and 10 use other plate scenarios than 02-09 (documented above), so the Site layout in 01 differs slightly (decay plate sits 22 px higher, corrected).

## Scripts (`scripts/`)
`hb.py` builds every frame (`python hb.py [frame ...]`, no args = all); `hy.py` is the hybrid layer library (ribbon, heads, tiles, tally, vinyl cards, HUD, stencil discs, poster, hex flash); `lib.py`, `scene.py`, `ui.py`, `glyphs.py`, `daemon.py`, `common.py` are E's modules (edited: F grade in `lib.base_city`, `scene.tower` height scale, wider fog corridors in `ui.fog_band`, idle-collapse and cage alpha in `common.draw_world`); `eb.py` is E's old build, kept only for its helpers (infected card, bezier, grease arrow, lime ring). `post.py` makes strips, sims, 1280 checks and the sheet. `crop.py`, `sq.py`, `probe.py` are review helpers. Needs numpy, Pillow, scipy; plates from `D:/rc_scratch/tide_concepts/plates`; the static cache is written to `D:/rc_scratch/tide_concepts/h_work`. Fonts: Anton and Permanent Marker (copied from F).
