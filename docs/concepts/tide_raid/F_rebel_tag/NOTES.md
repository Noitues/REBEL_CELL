# F "Rebel Tag / Street Hack": Infected Tide raid, round 2

**Thesis (one line):** the corp projects a cold, perfect AR raid over the night city and the Cell defaces it live with spray, stencil, vinyl and wheatpaste, so every beat is read by what the paint did to the clean vector.

Frames are composites over the real Godot plate (`city_noraid_nonet.png`, default-scenario coordinates) in Python/PIL. Rebuild: `python scripts/ft_frames.py` then `python scripts/ft_post.py` (plates from `D:/rc_scratch/tide_concepts/plates`; the graded plate is cached in `D:/rc_scratch/tide_concepts/f_work/`). No Godot code, nothing committed.

## Deliverables
`01_decay` `02_draw` `03_plan` `04_forecast` `05_response` `06_playout_impact` `07_playout_home` `08_aftermath` `09_hq_step` `10_city_lost` `11_panels_removed` (the forecast with every panel removed) and an extra `12_reveal_sealed_hunter` (the sealed + HUNTER reveal, the thing round 1 failed). Also `squint/` (320 px and 4 px blur), `colorblind/` (deutan and tritan of 04, 06, 07), `sheet.jpg`, `scripts/`.

## Two voices (the whole idea)
- **Corp AR = cold, exact, sterile.** CORP white (#E2F4FF) hairlines, perfect hex pins, perfect circles, scanline sweeps, small numbers and percent glyphs. Beams D/N/E live here, with a black casing so they hold on plum and neon.
- **The Cell = hand-made.** BONE paint (#F6F0DE) with a black outline, overspray speckle, drips, wobble. Marker tags (letters A B C, verbs), stencil slabs (GUARD, in the beam's colour), a spray arrow (SHIFT), a glitched RGB-split sticker (ghost), a grease-pencil tally and D28 marks, a wheatpaste verdict poster. Where the Cell touches the corp line, the line's state changes.

## Beam grammar (hue and shape)
| type | hue | shape | head |
|---|---|---|---|
| D | blue #3A96FF | fat beads | quad-rotor X |
| N | magenta #FF40D6 | zig-zag, white core, black casing (reads on plum) | diamond eye |
| E | signal yellow #FFE01A | chevron band | shield badge |

Sealed A/B/C = a corp **censor band** (black bar, static blocks, tape edges) on the three routes, each with a padlock and the Cell's spray letter (the Cell's guess). HUNTER = a corp **eye-drone** hovering over the fork with two dashed yellow ghost streets.

## How each beat reads with no text
1. **Decay:** a DOWN site carries a grease slash; decay turns it plum (Bloom A: plum-black body, pink Voronoi veins, hot hairline front, drips, biohazard stencil, X on the pin). Two plum INFECTED vinyl cards fly from the sites to the HUD counter (0 to 2, "+2").
2. **Draw:** the corp projects its routes from the HQ pad: K1 done, K2 mid-draw with sparks; order dots 1, 2; the sealed band with A/B/C locks; the eye over the fork.
3. **Plan:** the hand is vinyl cards (colour = the beam type it stops). One is dragged on a spray line to a district under a lime halo (the only lime). Placed: a stencil slab in the beam's colour (GUARD), a spray arrow (SHIFT), a glitched sticker (ghost). The left chip stack is a beam order/type legend (a panel).
4. **Forecast:** the corp "computes": a scan sweep and percent glyphs at threatened sites. Intent tiles (Into the Breach) on targets: tier glyph (second channel) + hue + number. A stopped beam ends in a teal flat-end bar, then grey dots. The Cell's grease tally at HOME is the odds: 12 tier glyphs (ring, shield, slashed square, broken heart, octagon X).
5. **Response:** four stencil discs (DEPLOY, HOLD, MOVE, SACRIFICE: glyph plus one word). Above each, three tier glyphs = worst/likely/best outcome of that choice. Lime on the pick; the map dims.
6. **Playout, impact:** the blue head reaches the stencil: hex flash, AR glass shatter, paint splat in the guard's colour, binary bits, a teal HOLDS tile.
7. **Playout, HOME hit:** the N zig-zag reaches HOME: orange splat and glass, orange ring pulses, "-6" tag, DAMAGED tile, HUD 44 to 38 in orange, cold corner brackets (corp alert).
8. **Aftermath:** an Obey-style wheatpaste poster slapped on the city (orange halftone, broken heart, "DAMAGED"). Newly DOWN sites wear a grease slash and a dashed red clock ring (next raid = TAKEN). Spent beams are grey dots.
9. **HQ step:** a spray menu of five stencil discs at HOME (wrench, shield+, heat-down, purge card, plus) with prices. Lime on the wrench; a mint spray arrow to the DOWN site, which shows a mint ghost of the repaired hex (the consequence).
10. **City lost:** the plum Bloom floods the map, the corp glass is cracked, a huge white stencil skull (the skull glyph), HUD balance tipped (9 INFECTED vs 8 healthy).
11. **Panels removed:** 04 minus the launch/back chips and the outcome strip. Nothing is lost: the tally, tiles, beams and HUD still carry it.
12. **Reveal:** lock A opens with a bit burst, its fog tears away and the route lights in its type (E chevrons); B and C stay locked. The eye's brackets snap on one street and the other is crossed out.

## Palette (hex)
Corp white E2F4FF; CRT bg 081224, CRT edge 5CE1FF; Cell bone F6F0DE; ink 0E0A16; D 3A96FF; N FF40D6; E FFE01A. Tiers: untouched mint BFFBF0, holds teal 1FB8A6, sites lost amber F29A1F, damaged orange FF7014, breached HARM red FF3B30 (only as the fifth glyph in the tally/outcome dots, never in a played frame), city lost = skull in bone. Infection: plum 1A0B1F / 3A163E, vein FF3FA0, front FF96D7. Grease pencil FF4A3A. Focus lime D4FF00 (only the halo).

## Medium mapping and departures
Uses: vinyl sticker cards, CRT chips, corp paper (the poster), grease pencil (D28: DOWN = one slash plus ring, TAKEN = X), binary-bit bursts and hex flash, the glyph vocabulary, Bloom A necrosis.
Departures:
- (a) The corp alert is cold white, not red. Red is ruled BREACHED only and a DAMAGED hit is orange; the brief's "sterile red alert" would read as BREACHED.
- (b) Camera pushed to 2.0x on the territory (the shipped raid camera is 1.0x).
- (c) City regraded: saturation up, window bloom, mids down. Still night.
- (d) The poster and spray layers are screen-space overlays, not world-attached.

## Research (web search was thin; flagged where it is my knowledge)
- **Jet Set Radio** (searched: thick outlines, flat fills, a blocky stylised tag typeface; kana/kanji tags noted as hard to read). Take: a heavy black outline round every paint mark so it separates from a busy city. Avoid: ornate lettering; tags here are single letters or one short word.
- **Banksy stencils** (searched: two stencil layers, a limited palette with one colour accent). Take: GUARD = a one-colour slab with a cut shield and a second layer for the type glyph, with bridges. Avoid: figurative detail.
- **Shepard Fairey / Obey** (searched: sticker and wheatpaste origins, bold lines, limited palette). Take: the verdict is a wheatpaste poster, halftone plus black ink plus two colours. Avoid: portraits.
- **Mirror's Edge Catalyst** (searched: one saturated colour guides the eye through a restrained world, GPS-style recalculation). Take: beams are the only saturated lines on a dark cool city; lime and the tier hues stay rare. Avoid: whole-object tinting (fights the plate).
- **Ruiner, Akira (1988) graffiti, The Ascent** (my knowledge, not searched). Ruiner/Ascent: dirty-neon info chips at street level, taken for the HUD chips. Akira: hand-sprayed marks on a hard city, taken for drips and tag scale. Avoid: the Ascent's HUD density.
- **Google/Apple Maps 3D, Waze, Cities: Skylines, Frostpunk, Watch Dogs ctOS, Into the Breach, Mini Metro** (my knowledge). ITB: intent tiles with numbers on targets and the flat-end stop bar. Maps: one cased route, a destination pin. Skylines: state as colour per segment (avoided: it fights beam type). Frostpunk: one readable gauge (the tally). ctOS: tags on targets (avoided: per-site clutter). Mini Metro: a few clean lines.
- **Own two:** *Watch Dogs 2* DedSec (stickers and spray over a corporate AR layer, the same conceit; we keep the vinyl and the clean/dirty contrast) and *Blade Runner* signage clutter (cold vector over wet neon: the rain and the bloom).

## What build would have to change (spec list)
1. A raid-camera framing option (about 2x on the territory) or a scrolling raid view; HOME and HQ must both fit with the bottom third free for the hand and discs.
2. Beam renderer: cased line along the existing site_path with a per-type pattern (beads, zig-zag, chevrons) and a head glyph; lane offsets (about +/-26 px at this zoom) so up to 3 corridors share a street; a per-beam stop point from the forecast.
3. Sealed band: one censor-band shader on the candidate routes plus a lock and letter pin per sealed route. Reveal = lock-open FX + band dissolve + route lights in type colour. HUNTER: an eye pin and two ghost streets; lock-on brackets at reveal.
4. Replace the text panels with intent tile pins (tier glyph, hue, number), the HOME tally (12 glyphs from the forecast distribution), response discs with three outcome glyphs, and HQ-step discs with prices.
5. Defense marks: stencil slab (beam colour), spray arrow, glitch sticker as decals on the site pad (a decal shader with overspray noise).
6. Reuse the shared D28 helper for DOWN (slash and clock ring) and TAKEN (X) on the AR pin.
7. Verdict: a poster node with a halftone shader and the per-tier glyph (reuse the tier glyph set); CITY LOST = a skull decal over the Bloom flood.

## What the Godot look would need
Spray shader = noisy-threshold alpha (soft mask plus noise, speckle from a blurred halo) with a dilated-mask outline; glass shatter = a pre-baked radial crack sprite plus shard quads with refraction; scanline sweep = a screen-space mask; window bloom and saturation grade scoped to the raid camera; Bloom A necrosis shader driven from TAKEN sites (already in the game).

## Risks and honest weak points
- Squint: the forecast (04) and plan (03) read as a dark map with small marks; only the tally, tiles and the card hand pop. Strong at squint: 06 (blue burst), 07 (magenta zig-zag plus orange), 08 (poster), 10 (skull), 12 (yellow route).
- The t1 cluster is still dense (4 pins, 2 slabs, tiles within about 120 px). Guards were moved aside, but at 1280 it needs a collapse rule.
- Sealed bands overlap the known beams on shared streets. Lanes separate them, but three parallel ribbons plus the censor band are heavy near HOME.
- Beams follow the game's lattice (lifted 12 px above the street polylines), not the street grid itself.
- Graffiti letters are single glyphs; real tags would need a legibility budget. Spray looks good in a still and may look noisy in motion.
- Colour-blind: amber and orange merge in deutan and tritan; the slashed square vs broken heart glyph carries it. Teal HOLDS goes grey in deutan; the shield shape carries it.
- Poster and spray are screen-space; attaching them to the 3D city (perspective, occlusion) is the big build question.
- The stencil slab sits beside the corp pin, so Site identity depends on position; the tier pips on the pin are small.
- The HOME tally row sits on the street, which can collide with the hand in the plan beat if the map scrolls.
