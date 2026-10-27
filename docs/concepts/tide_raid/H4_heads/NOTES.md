# H4 beam heads, round 2 (exploration, not polish)

Brief: designer liked round 1's B (creature identity) but its icons were too detailed; asked for simpler, themed options: computer hacking, Solace corporation (bacteria/virus or medical), military. Goal: B's character at A's simplicity. Each head is one bold solid silhouette, 1-2 shapes, at most one ink cut, same footprint as before (bbox 2.1 units = 24 / 32 px), hues unchanged (D 4690FF, N FF40D6, E FFEE3A).

Files: `heads_board.jpg` (6 new families at 2x, round 1 A and B as 1x reference columns, new bottom row = motion), `family_<id>_*.png` (one detail sheet per family: construction, 24/32 px on the real plate in normal / deutan / tritan, 4 px blur, leading a ribbon + ribbon blur, card-tab glyph, 2-frame motion at game size and at 120 px with a frame-difference plot), `scripts/` (`shapes.py` all polygons with `fn(t, frame)`, `render.py`, `metrics.py` + `metrics.json`, `build.py`, `cb.py`, `shapes_h3.py` = round 1 A/B for the reference columns). Rebuild: `python metrics.py metrics.json`, `python build.py <outdir>`. Same plate crops, ribbon and card panels as H3, so boards compare directly. Nothing committed.

## Research (quick; principles only, no images reproduced)
- **APP-6 / NATO** (web check): frame shape = affiliation (rectangle friendly, diamond hostile, quatrefoil unknown), shape and colour are deliberately redundant so it survives a monochrome display; unit type is a simple inner icon: infantry saltire, cavalry/recon single diagonal (the sabre strap), signals a simplified lightning flash; the armour oval and the air dome frame are from the same set (from memory). Taken: M2 (dome + slash, diamond + signals, ground frame + oval).
- **Into the Breach** (web search found nothing specific on the Vek art; this is memory of the game): each Vek is one flat silhouette with a dark outline, identity from the outline and one or two big masses, motion from a 2-frame idle. Taken: no internal detail under ~3 px, 2-frame motion hint, outline carries the identity.
- **Mini Metro**: one primitive per category. Taken: every head here is one primitive-scale mass; heavier type = bigger/rounder mass (virion, cylinder, tank).
- **Phage / virus iconography** (web check of BioRender / Mind the Graph): the phage icon is a squashed icosahedral head, tail tube, baseplate, splayed fibres; the virion icon is a disc with knobbed spikes. Taken: both, reduced to head + stalk + 2 legs, and disc + 10 knobs.
- **Cyberpunk 2077 quickhacks** (memory): bold single-glyph pictograms in a frame, hex tiles for breach codes. Taken: pictogram-first thinking (bolt, hook, ghost), and avoid hex for anything but the one place the grammar already uses it.

## Families (D drone / N netrunner / E enforcer)
| id | theme | D | N | E | frame-2 motion |
|---|---|---|---|---|---|
| H1 malware | hacking | worm: one S body, round head | ghost (rootkit daemon): dome leads, zig-zag hem, two eye cuts | logic bomb: ball, fuse, spark | worm ripples, hem swaps teeth, spark blinks |
| H2 exploits | hacking | zero-day bolt | phishing hook: thick J, barb, eye ring | data cylinder, one lid cut | bolt mirrors, hook swings, lid lifts |
| B1 pathogens | Solace bio | bacillus rod + flagellum | bacteriophage: capsid, stalk, plate, 2 legs | virion: disc + 10 knobbed spikes | flagellum waves, legs splay, spike ring turns |
| B2 clinical | Solace medical | pill capsule, one seam | antibody Y | syringe, one window cut | pill tumbles, arms flex, plunger pushes |
| M1 vehicles | military | quadcopter (4 rotors on an X) | radar / ECM dish | tank (hull, hatch cut, barrel) | wobble, dish sweeps, barrel recoils (treads at 40 px+) |
| M2 APP-6 | military | air dome + recon slash | hostile diamond + signals bolt | ground frame + armour oval | slash and bolt flip, oval squashes |

Hard rules honoured: no cross anywhere (B2 uses Y, capsule, syringe only), no plum / no hex plate (the only hex is the elongated phage capsid), no skull, no eye (the grammar's HUNTER eye is taken, so the eye idea for N was dropped), no shield, no cursor or pointer shape, no lime ring.

## Metrics (silhouette incl. outline, frame 0)
Worst-case pair overlap = IoU over 24 rotations between types (lower = more distinct). Pieces = connected parts at 24 px. Frame delta = 1 - IoU(frame 1, frame 2) at 24 px (0 = identical silhouette; motion then lives only in the ink cut). Area at 24 px in px.

| family | 24 px D/N | D/E | N/E | pieces D/N/E | 32 px D/N, D/E, N/E | area 24 px D/N/E | frame delta 24 px D/N/E |
|---|---|---|---|---|---|---|---|
| R1 A frames | 0.58 | 0.57 | 0.74 | 1/1/1 | .58 .57 .73 | 309/288/384 | 0 / 0 / 0 |
| R1 B daemons | 0.79 | 0.59 | 0.55 | 1/1/1 | .79 .59 .55 | 259/237/360 | 0 / 0 / 0 |
| H1 malware | 0.46 | 0.67 | 0.60 | 1/1/1 | .46 .67 .60 | 209/460/294 | .39 / .07 / .06 |
| H2 exploits | 0.46 | **0.35** | 0.58 | 1/1/1 | .47 .35 .58 | 161/268/480 | .50 / .22 / .07 |
| B1 pathogens | 0.66 | 0.49 | 0.58 | 1/1/1 | .66 .49 .59 | 205/268/420 | .08 / .08 / .12 |
| B2 clinical | 0.56 | **0.79** | 0.63 | 1/1/1 | .56 .79 .63 | 266/278/272 | .25 / .19 / .13 |
| M1 vehicles | 0.59 | 0.60 | 0.67 | 1/1/1 | .59 .60 .67 | 428/278/326 | .29 / .40 / .07 |
| M2 APP-6 | 0.58 | **0.82** | 0.64 | 1/1/1 | .58 .82 .63 | 506/288/466 | 0 / 0 / 0 |

Every head is a single piece at 24 px; no head needs a cut finer than 3 px except the optional 1 px details that only exist at 40 px+. Worst pair overall: M2 D/E 0.82 (dome vs rounded rectangle), B2 D/E 0.79 (pill vs syringe, both long horizontal bars). R1 B's 0.79 pair was D/N; the new families beat it except M2 and B2.

## What reads at 24 px (squint + deutan / tritan, from the boards)
- **B1 pathogens**: best character per pixel. The virion is the single strongest E of anything in rounds 1 and 2: big, round, spiky, unmistakably "virus", survives deutan (yellow) and tritan (cream) and the 4 px blur as the largest hue blob. The phage reads as phage at 24 px (hex head + stalk + legs). The bacillus is the weak one: a small blue pill with a 2 px tail (area 205, second smallest), close to the phage in a squint (0.66).
- **M1 vehicles**: tank and quadcopter are instantly legible and big (areas 326 / 428); the tank has the best "heavy, armoured" read of all families. The radar dish is a crescent plus dot: at 24 px it reads as a bracket or a hook, not as a dish.
- **H1 malware**: ghost is excellent (largest N, clear eyes, strongly "daemon"), bomb is a clean heavy ball. The worm is a wiggly line (area 209) and at a squint is a blue smudge; pairing with the other two is fine (0.46 / 0.67).
- **H2 exploits**: most distinct set (D/E 0.35, D/N 0.46) and the bolt and cylinder are very legible, but the theme is looser (bolt = power / "fast", cylinder = a barrel to some) and the hook is the thinnest shape in the round (2 px barb); it can read as a "6" or a tadpole.
- **B2 clinical**: antibody Y is a great N (simple, bold, hacker-intrusive in spirit: it latches onto things). Pill is fine. The syringe is the busiest head in the round (flange, plunger, window = 4 features) and at 24 px is a noisy "T"; pill and syringe overlap in silhouette (0.79). Medical items also read as "pickup / heal" in a game, a real risk for a threat icon.
- **M2 APP-6**: simplest and most coherent system, but it is round 1 A again in a new coat (diamond, frames); direction is not shown by the shape (D dome leads, E does not) and the identity lives in 1 cut each, which is the thing 24 px loses first; frame delta is zero.
- On the ribbon (30 px head on 11 px ribbon) all six read as clear terminals; the creature heads (ghost, virion, bomb, tank, quad) look most like "a thing", the hook, flagellum and dish look like noise. At 4 px blur everything collapses to a hue blob, same as round 1, so the ribbon pattern (chain / braid / chevrons) and hue still carry type there.

## Motion
Silhouette-level motion at 24 px works best for worm (ripple), bolt (mirror), dish (sweep), pill (tumble), hook, tank (barrel recoil), quad (wobble). Virion, phage, bacillus, ghost and bomb have small frame deltas (0.06-0.12): at game size the second frame is a subtle shimmer (the spike ring turns, legs splay, hem teeth swap); the creature identity survives in motion because every frame keeps the same primary mass. M2 has no silhouette motion at all. Tank treads and rotor blades are 1 px details that only appear at >= 40 px (kept out of the 24 px silhouette on purpose).

## Ranking and recommendation
1. **B1 pathogens** (recommended). On-brand for Solace (spreads a virus), keeps R1-B's creature identity with far simpler shapes, best E of any family, and the three differ in mass: thin rod, headed stalk, big spiky disc, so the weight ramp D < N < E is by shape as well as hue. Before polish: fatten and shorten the bacillus (drop the flagellum to a 3 px stub or make the rod an oval with a nub) and thicken the phage legs.
2. **M1 vehicles.** Most readable at a squint and obviously "military / enforcer". Replace the dish N with the antibody Y (B2) or the ghost (H1) and it is the strongest set. Risk: theme is generic and does not say Solace.
3. **H1 malware.** Ghost and bomb are strong, the worm is weak; the ghost carries a Pac-Man association (playful, not menacing).
4. **H2 exploits.** The most distinct silhouettes, but the least coherent as a family and the hook is too thin.
5. **B2 clinical.** Y and pill good, syringe too busy; "medical pickup" semantics.
6. **M2 APP-6.** Same idea as round 1 A; keep as the fallback if designer wants a system rather than creatures.

Hybrid worth a look (best single read per type, all simple solid shapes): **D bolt (H2) or pill (B2), N ghost (H1) or antibody Y (B2), E virion (B1) or tank (M1)**. Cleanest mixed pick: D = quadcopter or bolt, N = antibody Y, E = virion.

## Weak points and collisions
- B1 N phage head is a stretched hexagon: stays distinct from the regular hex tier plates by aspect and legs, but at a squint it can read as a hex plate plus noise. Fallback: round the capsid to an octagon.
- Virion and bomb are both round (E in B1, E in H1) and spiky-disc shapes read as "mine / sun / gear" to some; the knobs on the virion are what make it a virus, and they are 2 px at 24 px.
- Syringe, pill, antibody are medical item icons: possible "pickup / health" misreading in a card game. Skin, and no cross (a protected emblem) was used anywhere.
- No head except the tank, bomb (fuse) and ghost (eyes, dome) has a strong inherent forward direction; virion, cylinder, quad, APP-6 E rotate invisibly, so the ribbon alone shows direction (the arrowheads of rounds 0 and A did that by shape).
- Tritan: E (yellow) turns cream and N turns red-pink, as in round 1; shape (virion / tank / syringe vs Y / phage / ghost) separates them, but pill vs syringe and dome vs rectangle (the 0.79 / 0.82 pairs) are the pairs most at risk when hue is lost.
- Cuts at 24 px: ghost eyes, pill seam, tank hatch, APP-6 slash, bolt and oval; the 2 px seam and slash can vanish on the busy plate. Hook eye ring and syringe window are below 3 px and should be dropped or enlarged before use.
- Numbers are for silhouettes with outline on a flat footprint, headings 0 and the 24-rotation sweep, 24 / 32 px only. Motion is judged on 2 frames at heading 0 (plus iso at 24 px), not on a real rotating head at a street turn.
- Round 1 reference columns are shown at 1x (half the size of the new columns) on purpose, so details are lost there; compare numbers, or open `../H3_heads/` for the full sheets.
