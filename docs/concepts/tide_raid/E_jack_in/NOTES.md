# E "Cyberspace / Jack-in" (round 2)

**Thesis:** while the raid is planned the player has jacked in: the real night city stays, but every Site grows a translucent ICE data-tower, the corp HQ sits in a lattice cage, and each raid line is a black-ICE daemon whose head silhouette (not just its hue) says what it is.

Frames are 1920x1080 in `frames/`: 01_decay, 02_draw, 03_plan, 04_forecast, 05_response, 06_playout_impact, 07_playout_home, 08_aftermath, 09_hq_step, 10_city_lost, 11_panels_removed, plus a bonus 12_reveal_sealed_hunter. `squint/` has `_320` and `_blur4` per frame. `colorblind/` has deutan and tritan sims (Machado 2009, linear RGB) of 04, 06, 07, 12. `sheet.jpg` is the contact sheet. `scripts/`: `build.py` (frames), `post.py` (strips, sims, sheet); needs numpy, Pillow, scipy; plates are read from `D:/rc_scratch/tide_concepts/plates`; a static-layer cache is written to `D:/rc_scratch/tide_concepts/e_work`.

## Refs (what I take / avoid)
Web search was thin (it confirmed only the "bright lattices of logic" passage and the Breach Protocol screen anatomy); the rest is from my own knowledge of the works.
- **Gibson, Neuromancer (cyberspace, ICE, black ICE):** take lattice-of-light geometry, data as architecture, ICE as a lethal wall. Avoid green-on-black text rain as the main look.
- **Ghost in the Shell (1995 / SAC net dives):** take the city seen with a data layer over it, wireframe volumes, glitch tears. Avoid long diagnostic text.
- **Shadowrun Returns matrix:** take the idea that a place has a second, node-based skin with ICE guarding nodes. Avoid the flat node-map UI that abandons the world.
- **Uplink / Hacknet / Hackmud:** take the black-box attitude and the trace as a visible threat in a place. Avoid terminal windows and typed commands (hard-fail text wall).
- **Cyberpunk 2077 breach protocol:** take the daemon as a named, typed program with a fixed shape, and hex cells as the wall vocabulary. Avoid the code-matrix puzzle UI.
- **Into the Breach:** take ghosted pre-committed intent (forecast ghost heads) and numbers on the target. Avoid pretending sealed routes are telegraphed.
- **Google Maps / Mini Metro (round 1 lessons):** take one clean route line per beam with direction chevrons on the real streets. Avoid the daytime regrade.
- **Tron (1982), Johnny Mnemonic:** take the iso wireframe volume with a bright edge and dark glass. Avoid a flat black void: the real plate stays.
- **Own refs:** (1) hazard-striped industrial plant machinery (E enforcer body); (2) braided DNA-rope / cable macro photography (N strand); (3) airport flight-path "ghost" projections (forecast echoes).

## Medium mapping
The cel + ink plate is untouched except a colder, about 25 percent darker grade so the data layer is the brightest thing. Departures from the game vocabulary: the cyan wireframe ICE layer, and scanlines / vignette / edge fringe (jack-in post). Reused: vinyl sticker cards (die-cut paper border), CRT chips for the HUD, corp paper tag + rubber stamp (DAMAGED), grease-pencil marks (DOWN = white double slash, TAKEN = red double X, drag arrow white), binary bits + hex shards for destruction, the glyph atlas, Bloom A necrosis (plum-black body, pink Voronoi veins, hot hairline front, windows dying behind).

## Palette
Night void 070515 / 0A0C24; lattice cyan-white 7FEFFF, lattice mid 2FB8E8; D blue 3D86FF; N magenta FF40D6; E signal yellow FFD800. Tiers: untouched B8FFF2, holds 19C9B4, sites lost FFB21E, damaged FF6A1A, breached FF3347. Lime C6FF2E is the focus halo and nothing else. Plum 1A0B1F / 4A1440, vein FF3FA8, hot front FFD6F0. Paper F6F1E4. DOWN mark F6F1E4, TAKEN mark FF2A3A. Sealed fog 9C8CFF.

## Daemons: shape first, hue second
- **D DRONE:** thin chain of diamond links, sharp swept-wing arrowhead (blue).
- **N NETRUNNER:** braided double strand with rungs, square cursor head (magenta; white-hot core and black casing so it reads on plum).
- **E ENFORCER:** fat armoured hazard-striped blocks, blunt horned ram head with one lens (signal yellow).

The same three silhouettes appear on the card type band, on the firewall top, on the lock when it opens, and on the forecast ghost heads.

## How each beat reads with no text
1. **Decay:** the two DOWN Sites go plum: tower stump, red double X, Bloom necrosis blooms from their pads, and INFECTED cards lift off and fly to the deck strip (plum cards 3 vs healthy 8).
2. **Draw:** the HQ cage flares with shock rings; D daemons uncoil out of it; three letter locks A B C appear with fog corridors leaving; a hunter eye opens; the hand is dealt (two cards still in flight).
3. **Plan:** route lines (dashed D, dotted N, solid E) with chevrons on the streets; placed programs on Sites (N firewall on t1_a, E decoy on t1_b); the dragged card has a lime outline, a white grease arrow, a lime ring and a ghost wall on its target.
4. **Forecast:** ghost heads where each daemon will stand (echoes) and where it dies; tier chips whose glyph shape is the second channel (shield HOLDS, tower-down SITES LOST, cracked heart DAMAGED, shattered heart BREACHED, ring UNTOUCHED); orange ghost ticks on HOME's 50-tick ring; five iso odds bars with the same glyphs; sealed routes are fogged corridors with letter locks; the hunter is an eye with two ghost heads on its two streets.
5. **Response:** four keycaps (deploy, hold, move, sacrifice), each with three outcome pips (glyph + colour); lime halo on the chosen one; the HQ shock ring means launch.
6. **Playout impact:** a D head slams the D firewall: hex cells fly, bits, flash, teal shield chip; the earlier D is an ink-grey husk; the Site that went DOWN carries the white double slash.
7. **Playout HOME hit:** the magenta braid reaches the deck: orange flash, shock rings, glitch tear, ticks leave the ring in orange, "-6", and the HUD HOME chip turns orange (44 to 38).
8. **Aftermath:** corp-paper DAMAGED stamp with a heart-crack glyph; DOWN Sites with strikes and plum decay rings (the clock); HOME ring with orange scar ticks.
9. **HQ step:** action coins around our deck (wrench 10, card-X 20, snowflake 25); the selected wrench draws a cable to the DOWN Site and ghosts it rebooted; the double chevron is end step.
10. **City lost:** plum flood with veins, all t1 towers TAKEN, deck strip plum 11 vs 8 with the balance tipped, giant skull and "CITY LOST".
11. **Panels removed:** the plan beat minus hand, drag card and arrow: only map marks, locks, programs, lime ring and the HUD.
12. **Reveal (bonus):** lock A opens into the E silhouette and the yellow daemon walks its route; B and C fog dissolve into bits; the hunter eye drops a reticle on one of its two streets while the other street disappears. This is the wordless sealed + hunter answer: fog corridor + letter lock opens to a type silhouette; eye + two ghost heads locks onto one.

## What build would have to change (layout / flow)
- Expose per-Site tier, state and program slot (type + verb) to the tower renderer, and per-route beam type and `site_path`.
- Forecast must output per-beam stop site, per-Site predicted state, the 5-tier probability vector (odds bars) and predicted HOME ticks lost.
- Sealed routes need a reveal event per route (open the lock, fire it); the hunter needs a reveal event that picks one of its two streets.
- Each response chip needs a 3-tier outcome preview.
- Lane assignment (right-hand lanes) for beams that share streets.
- A deck-strip HUD of INFECTED vs healthy cards replaces "INFECTED outnumber" text.
- No PLAN / HQ STEP / AFTERMATH / RESPONSE panels; the verdict is a corp tag stamp.

## What the Godot look would need
Tower shader (iso box / obelisk / stepped, fresnel edges, lattice bands, scan band) on additive meshes; cage and ground lattice as additive meshes; data-shadow boxes seeded from the existing rooftop window instances; the daemon as a path-following instanced chain (arc-length) with per-type head meshes; the firewall as an instanced hex-cell wall with a shatter shader; a screen post (scanline, fringe, vignette) scoped to the raid camera only; the glitch tear as a UV-displace post pass on a masked region; the Bloom A shader already exists. The colder, darker plate grade must be raid-camera only.

## Risks / weak points
- Density: the t1 cluster (three Sites, programs, chips, two worms) is still the busiest 100 px; the playouts use a focus dim, forecast does not.
- The cyan wireframe is loud at squint: towers compete with the daemons for the first read. The daemons win in 06, 07, 12 but not in 04.
- Forecast carries many marks (ghosts, chips, odds bars, locks, eye); the sealed fog is subtle at 1x.
- Deutan: N magenta collapses toward blue-grey and amber/orange merge; shape (square head, braid, heart vs tower glyph) carries it. Tritan: orange vs red chips stay separable only by glyph.
- The hunter eye is small and the reticle weak; the type-neutral eye does not say "E" by itself.
- Bloom is still a bit pink-saturated; "windows dying" is only partly visible.
- Stills only: slither and echo-trail motion is unproven; the data-towers are fake-iso overlays, so occlusion is by painter order.
- Not drawn: DEPLOY / SACRIFICE / MOVE consequences on the map, the hunter playout, the sentry-shield variant.
