# Art deco cyberpunk: concept brief (2026-10-20)

A style exploration, not a change of direction. Six Blender renders restyle the existing game in art-deco
cyberpunk, plus one combat-wheel mockup drawn over one of them. Concept art only: no Godot, no game design,
nothing merged to main. The designer picks from the contact sheet before any iteration.

## The deco vocabulary (what "deco" means here)
- **Massing:** Chrysler / Metropolis setbacks, stepped ziggurat towers (3-5 setbacks, each tier ~80 % of the one below),
  sunburst / fan crowns (stacked concentric arcs with triangular windows), vertical piers and fins that run past the roofline.
- **Ornament:** chevron spandrels and bands, fan and sunburst motifs, stepped parapets, fluted columns.
- **Materials:** black lacquer facades (near-black, glossy clearcoat) against brass and gold leaf (metallic trims,
  crowns, mullions, spandrels). Dark glass with gold mullion grids.
- **Light:** geometric neon as **thin parallel lines** (2-4 lines with a gap, tracing setbacks and piers), never blobs or
  signs-as-light. Floodlit setbacks from below, fan searchlights.
- **Atmosphere:** Hugh Ferriss charcoal fog massing: deep warm-grey volumetric fog, towers dissolving upward into it, lit from
  the base. Near-monochrome charcoal; gold and the corp neon are the only saturated colours.

## Constraints from the bible and the rulings
- These views are **AAA-2 "Realistic night"** today (ART_BIBLE 1.2 exception, DIRECTION_REVIEW 2026-10-14). Keep the AAA-2
  pipeline (Cycles, PBR, volume fog, wet ground, light-streak traffic, no toon bands or ink); deco re-reads its materials,
  massing and light, it does not swap the medium.
- **Canonical landmarks** (2026-10-16): each HQ keeps the silhouette and identity of its full-city landmark. Deco re-skins
  and re-ornaments it; it does not replace it.
- **Corp identity = hue + material + crest + landmark** (ART_BIBLE 2.4). Keep each corp's hue in its neon lines. Deco gold
  is the shared metal; the corp hue must still win the squint test.
- **The city is always alive:** traffic streaks, beams, fog, rain stay.
- Grease pencil, stickers, CRT and holo are unchanged media; the combat mockup may re-skin the wheel's frame (World / chrome)
  but slices stay CRT "Screens & Data" (3.4) and live numbers stay bare Anton.

## The seven panels
| # | Subject | Base scene / camera | "Current look" for the side-by-side |
|---|---|---|---|
| 1 | Whole city | A2 city golden plate scene (`city_all_corps/scripts`, A2 build), the plate's hero camera | `golden_plates/city_a2_night.png` |
| 2 | Halcyon HQ: seven-tier civic core + scanning eye, violet #B06EFF / amber | `route_map_graph/hq_halcyon`, overview camera | `golden_plates/hq_halcyon_overview.png` |
| 3 | Meridian HQ: Gatehouse Gantry, orange #FF8C1A / red | `route_map_graph/hq_meridian_v3`, overview camera | `golden_plates/hq_meridian_overview.png` |
| 4 | Orbital HQ: silo crescent, rocket, ice white #CDF0FF | `route_map_graph/hq_orbital`, overview camera | `golden_plates/hq_orbital_overview.png` |
| 5 | Solace HQ: lit double helix, lime #96FF46 / pink | `route_map_graph/hq_solace`, overview camera | `golden_plates/hq_solace_overview.png` |
| 6 | Netrun street route, street level | `route_map_graph/street_r2`, decision camera | `golden_plates/street_decision.png` |
| 7 | Combat-wheel frame mockup (2D over a deco render) | over a crop or variant of panel 6 (no 7th GPU job) | `round41_wheel_stack/combat_typical_v4.png` |

Per-corp deco reads (starting points, not rules):
- **Halcyon:** a true Mesoamerican-deco ziggurat (seven setbacks), the Eye as a sunburst crown, violet parallel neon on each
  setback edge, amber floodlights.
- **Meridian:** Machine-Age deco: the gantry as a riveted brass gatehouse with chevron hazard bands, streamline train,
  orange neon in triple lines.
- **Orbital:** Streamline Moderne: the dishes and silo as stepped concentric rings, the rocket as a Ferriss spire in fog,
  ice-white lines.
- **Solace:** the helix in brass ribs with green-glass fan windows, lime/pink double lines running the strands.

## Each panel ships
- `NN_<subject>_deco.png` (1920 x 1080), and `NN_<subject>_sbs.jpg` (current left, deco right, same camera).
- 2-3 lines in `NOTES.md` on what deco changes in that view.
- `contact_sheet.jpg`: the seven side-by-sides with their captions, at most 2560 px wide.
