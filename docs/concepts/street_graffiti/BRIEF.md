# Street graffiti cyberpunk: concept brief (2026-10-21)

A style exploration, not a change of direction. Six Blender stills restyle the existing game as street-graffiti cyberpunk:
Tokyo canyon streets, vibrant graffiti on most building surfaces, strong neon colour, and foggy distance haze lit in soft
neon. Concept art only: no Godot, no game design, nothing merged to main. The designer picks from the contact sheet before
any iteration. (The art-deco set in `../art_deco/` is a separate, earlier exploration and is untouched.)

## The vocabulary
Real-world forms and placements, from `RESEARCH.md`:
- **Street band** (ground to about 3 floors): bubble pieces with extrude, outlines, fills and drips; chrome throw-ups; skull
  characters; wheat-paste posters; Latin and kana / kanji tags over everything; old faded pieces and grey buffs under it all.
- **Above it:** the street layer survives in patches; **heaven spots** (blockbuster roller letters, big tags) on a share of the
  high walls, readable from the city cameras.
- **Tokyo signage** at street level: vertical lit shop signs in kana / kanji.
- **Paint is paint:** it takes the scene light; fluoro fills get a small self-glow (night neon and UV spill); outlines,
  posters and buffs never glow. Wear: patchy fading, speckle, grime.
- **Air:** the base fog thickened and tinted toward soft neon, with the fog-glow lights pushed to the Cell's neon hues (pink,
  cyan, violet), so the distance haze is neon-lit.

**Where it shows (designer, 2026-10-21):** the netrun street carries the graffiti. The city and HQ overviews only hint at it:
paint on the lower floors and a few rare heaven spots, with the neon haze doing most of the work at that zoom.

## Constraints from the bible and the rulings
- These views are **AAA-2 "Realistic night"** (ART_BIBLE 1.2 exception, DIRECTION_REVIEW 2026-10-14): Cycles, PBR, volume
  fog, wet ground, light-streak traffic. Graffiti re-dresses the materials; it does not swap the medium.
- **Canonical landmarks** (2026-10-16) and **corp identity = hue + material + crest + landmark** (ART_BIBLE 2.4): the corp
  compounds keep their look; graffiti goes on the city round them and only on the compound's street band.
- **The city is always alive:** traffic streaks, beams, fog, rain stay.
- **Bible tension, flagged:** ART_BIBLE 1.2 rejects "spray paint and stencils, the dripping marker" and "neon-painting cities"
  as media. Here graffiti is *world surface dressing* (diegetic paint on walls), not a UI medium, and the panels test exactly
  that question for the designer. The combat mockup's painted frame is the one place it touches UI; slices stay CRT and
  live numbers stay bare Anton.
- Procedural: everything is seeded rules (atlas generator + shader overlay + placement), so it rebuilds on any layout.

## The six panels
| # | Subject | Base scene / camera | Current look for the side-by-side |
|---|---|---|---|
| 1 | Whole city | A2 city scene (`city_all_corps/scripts`), hero camera | `golden_plates/city_a2_night.png` |
| 2 | Corp HQs: Halcyon, Meridian, Orbital, Solace (one sheet, four renders) | `route_map_graph/hq_*`, overview camera | `golden_plates/hq_<corp>_overview.png` |
| 3 | Netrun street route, street level | `route_map_graph/street_r2`, decision camera | `golden_plates/street_decision.png` |
| 4 | Combat-wheel frame mockup (2D over panel 3) | round-41/44 combat screen, backdrop = panel 3 | `round41_wheel_stack/combat_typical_v4.png` |
