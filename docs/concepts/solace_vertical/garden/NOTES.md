# Solace culture garden (EX-11, Virus key exploit building): concept round, three directions (art-pass, Solace list item 5)

Concept only: the designer picks, through art-pass, before anything is built. Art only: no rules, no game UI. Nothing here is committed; no Godot tree was touched.
Sheet: `sheet.jpg` (2550 wide; rows A / B / C, columns map | street | inside, each frame with its squint strip: 320 px, and the same with a 4 px blur at 1920 scale).
Frames: `<A|B|C>_map.png`, `_street.png`, `_inside.png` (1920 x 1080). Scripts and the rebuild are at the end.

## Recommendation

**A "Glass ward" for the build**, with B's mint cell skin kept as the alternative if the designer wants a more "biotech" read.

- A is the only direction whose route stays legible *over* the building: its tiers are flat, horizontal, evenly spaced bands, so the O-route rings and the glass door
  (the strongest vertical in the frame) separate from it, the stepped silhouette is the least busy at 320 px, and the stacked terraces are exactly the spec's
  "walkway through a planter row / stair along the glass front" geometry with no invention. It is the calmest and the closest to the HQ park.
- A is also the best "taller graph" rule (add a tier, shrink the next one by a fixed step).
- C is the most spectacular but, at the street camera, the diagrid and the spiral ramp turn the building into one big soft dome that out-shines the O-nodes, and in
  the map it is the weakest landmark; keep it only if the designer wants a "set piece" over a "stage".
- B is the richest and the most Solace, but the hex skin and the stacking posts are busy behind the route marks and the hex detail is gone at squint size.
- Cost note for build: A is the cheapest (boxes, arches, one dome); B needs the hex wall (instanced cell panel); C needs a diagrid shell and a spiral ramp.

## One line per direction: how it reads at the squint (320 px / 4 px blur)

| Direction | map | street (O2 decision camera) | inside |
|---|---|---|---|
| A Glass ward | a dim stepped grey-green pyramid with a pale cap; clearly smaller and quieter than the lime helix and the cross hospital, the five steps hold in the blur | the lit stepped silhouette is the brightest mass, the white door notch with its orange gate posts and the two yellow O-rings on the pink lane all separate from it; the best route read | the five tiers hold, the orange I5 frame on the crown is unmistakable, pink flood on the two lowest tiers reads as foreign on the cream-green |
| B Culture stack | a dark cone of rings with a grey drum on top; reads as "something stacked" but the hex skin and the mint are lost in the blur; weaker than A | banded tiers read as stacked discs and the mint is clearly teal against the HQ's lime; the O-rings read, but the four stacking posts add vertical clutter beside the door | bands plus the cryo drum under the orange frame read; the Bloom flood on the two lowest trays reads well on the round trays |
| C Hanging mountain | the weakest map read: a pale translucent dome barely above the lawn, saved only by its ink outline (that is the point of "under the HQ") | one big soft bright dome; the door is a small notch at its foot and the O-rings stay readable, but the building clearly out-shines the stage (the competing risk the brief named) | the dome and the orange pod crown read, the spiral ramp lights the interior; the infected base ring reads as pink on the rock |

Route readability (art-pass addition 1): in all three street frames the three O-route rings, the O3 gate (orange posts, white door) and the cyan operative token are
drawn as emissive proxies at world scale (rings r 2.8 to 3.6 BU, columns 5 to 19 BU) and survive the 4 px blur against both the pink lane and the building. The
building is held to a lower emission than the route chrome (neon x0.7 to 1.1, windows x0.5) so it is the stage; A still carries the brightest mass of the three.

## Refs researched (what each taught)

- **Kew Palm House** (Decimus Burton and Richard Turner, 1844 to 48, wrought-iron ribs, curved glass; 110 x 32 x 19 m): iron is the *structure*, glass is the skin, so
  A's tiers are glass boxes in dark iron mullions with a Victorian arch under each eave and a ribbed dome crown. Taken: arched iron over glass, a hip-and-dome profile.
  Avoided: copying the single long barrel; the tiers have to stack, so the huge curved span is cut into five steps. ([Wikipedia](https://en.wikipedia.org/wiki/Palm_House,_Kew_Gardens), [Lindahall](https://www.lindahall.org/about/news/scientist-of-the-day/richard-turner/))
- **Kew Temperate House** (central block + two octagons 1863, wings 1897 to 99): the stepped massing of a high nave over lower wings is the precedent for "levels read
  through the glass as stacked terraces": each step is a lower, wider roof. (Kew restoration pages.) ([designingbuildings](https://www.designingbuildings.co.uk/wiki/Restoring%20Kew's%20Temperate%20House))
- **Barbican Conservatory** (Chamberlin, Powell and Bon): planting climbing raw concrete tiers *inside* a brutalist shell, over fly-tower mass. Taught the planter row
  as the floor edge of every terrace (A's planter troughs with a lit line; C's strata ledges). ([Roadbook](https://roadbook.com/london/photography/max-miechowski-horticulturalists-barbican-conservatory/), [Ignant](https://www.ignant.com/?p=314856))
- **Eden Project biomes** (Grimshaw; hex-tri-hex steel space frame, ETFE pillows up to about 11 m across points; honeycomb as inspiration): B's hex skin. Taken: a
  hex cell per panel, a few cells lit and the rest clear; the Solace cell kit (district bundle B) echoes it. ([Wikipedia](https://www.wikipedia.org/wiki/Pillow_Dome), [Ingenia](https://ingenia.org.uk/articles/how-an-eden-was-created-in-cornwall/))
- **Gardens by the Bay Cloud Forest** (Wilkinson Eyre; a 35 m planted mountain with a waterfall, Cloud Walk / Canopy Walk / Forest Floor levels): C's mountain core,
  its levels being walkways that ring the mountain. ([Dezeen](https://www.dezeen.com/2012/06/19/gardens-by-the-bay-by-grant-associates-and-wilkinson-eyre-architects/amp/))
- **Jewel Changi** (Safdie; a toroidal steel-and-glass dome of 9,300 panels, a 40 m Rain Vortex falling through an oculus into a basement pool, Forest Valley on five
  terraced storeys): C's oculus crown, the water core (a pale column falling to a foot pool) and the terraces round the core. ([Wikipedia](https://en.wikipedia.org/wiki/Jewel_Changi_Airport), [Metropolis](https://metropolismag.com/projects/jewel-changi-airport-safdie-architects/))
- **Culture incubators and petri racks** (stacked CO2 incubators with heated glass doors, polycarbonate dish racks of 48 or 84 dishes, steel stacking frames): B's
  tray = a dish (agar disc, colonies, a glass lid with a steel rim), the posts = the stacking frame, the thin plates in the room = dish racks. ([NuAire](https://www.nuaire.com/products/accessories/nu-1553), [Bel-Art](https://www.belart.com/corporate/instructions/918982117.pdf))
- **BSL-3 airlocks** (interlocked double doors, clean and "polluted" zones, pass-through autoclaves): the glass door at O3 reads as a lock door (a lit slab in a
  frame under a canopy, nothing sliding open), and B's pressure hatch on the vault. ([biosafety.be](https://www.biosafety.be/sites/default/files/bsl3_e.pdf))
- **Svalbard Global Seed Vault** (a concrete wedge portal, a fibre-optic art piece in green-turquoise and white on the roof and the front) and **Millennium Seed
  Bank** (underground cold rooms around a main dry room at minus 20 C, flood and bomb proof): the vault as a *target* = a sealed, lit, very quiet object with a ring of
  seed drawers round a lit core; B's cryo drum borrows the turquoise-white fibre light. ([regjeringen.no](https://www.regjeringen.no/en/topics/food-fisheries-and-agriculture/agriculture/svalbard-global-seed-vault/mer-om-det-fysiske-anlegget/id2365142/), [Kew](https://www.kew.org/blogs/wakehurst/the-world%E2%80%99s-richest-bank-how-we-store-the-world%E2%80%99s-seeds))
- **Bosco Verticale** (Boeri; balconies about 3 m deep sized to the canopies, 800 trees): the terrace overhang carries the planter row and is what makes a stepped
  tier read "green" from the street (A's step-back decks with their planter rows). ([Dezeen](https://www.dezeen.com/2025/01/20/bosco-verticale-stefano-boeri-21st-century-architecture/amp/))
- **ACROS Fukuoka** (Ambasz; 15 stepped garden terraces on the facade, about 35,000 plants at opening): the master precedent for a stepped green terrace as an
  occupied facade; A's five decks and C's strata. ([Archilovers](https://archilovers.com/projects/274078/acros-fukuoka-prefectural-international-hall.html))
- **Genre.** Deus Ex: Human Revolution's Sarif / LIMB clinics: a clinic as a clean, warm-lit lobby with a service counter; taken for the porcelain base of A and the
  reception bench on I1 (the WORKSHOP gets a warm gold wall so it is not confused with the clinical green). Avoided: the palette (black and gold is not Solace). BioShock's
  Arcadia (an arboreal hub where the plants are dying and the player is locked in until it is fixed; vibrant greens with pink and yellow blossom): taken is the plot beat, the
  plants dying behind the front, which is the Bloom's job here; avoided is the busy foliage, which would fight the route chrome. Prey's Arboretum: I could not find a
  source from the search (no ref taken from it); the point I take from memory is that a glass dome on a station reads as one object, which is C's risk.
  I found no reference text for the LIMB palette either, so nothing from it is quoted.

## Medium mapping (ART_BIBLE 1.2)

- **Map** = cel + ink: the district / HQ park scene (round 5 `--park 1 --plinth 1`, copied as `sd_main.py`), Eevee, the same ink + post passes (`ink.py`, `post.py map`). The
  garden sits on its lot south-east of the HQ plinth, at the Godot city camera (yaw -135, pitch 38, ortho 270 BU).
- **Street netrun** (O2 decision camera) and **inside rooms** = AAA-2 realistic night: Cycles (HIP, GPU lock `solace_garden`), the HQ v5 Cycles settings, the `hq_post.finish`
  post (HDR bloom, rain, grade, vignette, CA, grain) with the exposure solved to a median of 0.13 to 0.14 (AAA-2 target 0.12 to 0.15).
- Route chrome (rings, light columns, slot frames) is a concept proxy, in the Rebel Cell node colours (walked acid, current white, next orange, cut dim). Stickers,
  pencil and CRT are game UI: not designed.
- Cycles only on the street and inside frames; the map and the squints are Eevee / PIL (art-pass addition 5).

## Palette (art-pass addition 2)

- Solace lime (#96FF46) and porcelain / cream on A and C. **B's agar is mint (0.20, 1.0, 0.56): hue 147 degrees against the HQ helix lime (0.59, 1.0, 0.275): hue 94 degrees,
  53 degrees apart**; in the frames B reads teal against the lime helix and it stays a cool green, never the Cell-lime yellow.
- The Bloom is A "Necrosis" (plum-black skin, pink Voronoi veins, a hot hairline front, windows dying behind the front) via a copy of the Bloom 3D world-position node groups
  (`gs_bloom.py`: the front axis, a tide line, a radial mask, a retained 2 % of the original light). Pink appears nowhere on the garden itself. No red cross anywhere.
- Warm gold appears only on the WORKSHOP alcove; the cream door light and the orange O3 / I5 marks are the route chrome.

## Scale check (art-pass addition 3): the HQ is in every map frame

Height: garden **49 / 55 / 44 BU** (A / B / C) against the HQ helix **86 BU** (about 57 / 64 / 51 %). Spec height class 2 holds: taller than a lot block (26 to 44 BU solace kit
heights in the park), clearly below the helix. Measured in the map frame (`gs_ratio.py`: the pixels that change when the building is hidden, plus its shadow, against a 30 px
ring of local background):

| | garden luminance ratio | HQ ratio | garden dE (Lab) to its ring | HQ dE | garden / HQ height in px |
|---|---|---|---|---|---|
| A | 1.04 | 1.11 | 4.9 | 7.1 | 366 / 567 |
| B | 1.08 | 1.11 | 6.0 | 7.6 | 381 / 567 |
| C | 1.09 | 1.10 | 4.5 | 6.7 | 314 / 566 |

All three sit under the HQ on both measures. To get there the *map* tone of the garden is deliberately subdued (cel porcelain, iron and glass x0.45 / 0.50 / 0.62 and the
glass emission x0.45 / 0.50 / 0.62, `--celk`, `--gstr`): at full tone the garden had a luminance ratio of 1.42 (A), 1.26 (B), 1.23 (C) and a dE of 17.8 / 12.8 / 9.5, which would have beaten the HQ
(the porcelain is brighter than the lime helix on a dark lawn). The cost, honestly stated: the garden is a muted landmark in the map and nearly a camouflage at squint for C.
If the designer wants it more present in the map, the lever is `--celk` / `--gstr` (A at 0.55 gives 8.4 dE, at 0.7 gives 10.9). The night plates (street / inside) are not
toned down: there the garden is the stage and the HQ is not in frame.

## Lot size and clearance (what the concept needs)

- Footprint **48 x 42 BU** (spec 48 x 36): the building mass is 48 wide x 28 deep (y -7 to 21 in the lot frame) and the **plaza apron is the front 14 BU (y -21 to -7)**: planters, the lit
  walkway to the door, bollards. The spec's 36 BU depth does not hold a plaza *and* a building, so I ask for **8 x 7 lots** (48 x 42). If the designer keeps 8 x 6 the plaza apron
  shrinks to 8 BU and the O2 plaza frame loses its planter rows.
- Clearance **8 BU** (the border street) kept; the street frames use it as the front avenue lane plus 8 BU side streets.
- Height class 2: 49 / 55 / 44 BU to the finial. The lot is *never* flattened or ghosted (host rule): all frames show it whole; in the inside frames the front glazing is open
  (A: no front glass plane; B and C: an open sector of the wall and the shell), the host's facade being the building itself.

## Slot geometry per level (lot frame BU: x across, y from the front edge at -21, z up)

Numbers from `gs_tables.py` (read from the finals' info jsons; rooms are the open volumes behind the glazing). Slot centres are evenly spaced along the level's width,
slot order = node order, the last slot of I1 is the REST ("ward dose") and the last of I3 is the WORKSHOP alcove. Same level = a walkway through a planter row; rising = a
stair along the glass front (one stair per step, alternating sides); O3 to I1 = the ground-level glass door at x 0, y -6 (A) / -6.7 (B) / -6.4 (C).

**A Glass ward** (5 tiers = I1 to I4 as glass tiers + I5 the domed vault crown)

| level | x | y | z | height | nodes (slot width) |
|---|---|---|---|---|---|
| I1 ground hall | -21..21 | -6..19 | 2.2..11.0 | 8.8 | 3 (9.0) |
| I2 lower terrace | -17..17 | -2..18 | 11.6..19.6 | 8.0 | 2 (9.0) |
| I3 upper terrace | -13..13 | 2..17 | 20.2..28.2 | 8.0 | 3 (6.9); WORKSHOP alcove x 5.2..12.1 |
| I4 glasshouse | -9..9 | 5..16 | 28.8..37.0 | 8.2 | 2 (7.2) |
| I5 seed vault | -7..7 | 5.3..16.1 | 37.5..46.5 | 9.0 | 1 LARGE (14.0): a domed glass crown with a lime-lit core |

**B Culture stack** (5 oval trays, each one petri dish; I5 the cryo drum on the top)

| level | x | y | z | height | nodes (slot width) |
|---|---|---|---|---|---|
| I1 ground hall | -23..23 | -7..21 | 2.3..8.5 | 6.2 | 3 (9.0) |
| I2 lower terrace | -20.2..20.2 | -5.4..19.4 | 10.0..16.2 | 6.2 | 2 (9.0) |
| I3 upper terrace | -17.4..17.4 | -3.8..17.8 | 17.7..23.9 | 6.2 | 3 (9.0); WORKSHOP alcove x 7.1..16.1 |
| I4 glasshouse | -14.6..14.6 | -2.2..16.2 | 25.4..31.6 | 6.2 | 2 (9.0) |
| I5 seed vault | -6.6..6.6 | 0.8..14.0 | 40.0..49.5 | 9.5 | 1 LARGE (13.2): a sealed cryo drum, banded, with a pressure hatch |

**C Hanging mountain** (5 terrace rings round a water core; a two-turn planter-walk ramp; I5 the seed pod in the oculus)

| level | x | y | z | height | nodes (slot width) |
|---|---|---|---|---|---|
| I1 ground hall | -19..19 | -4..18 | 1.0..6.4 | 5.4 | 3 (9.0) |
| I2 lower terrace | -15.8..15.8 | -2.2..16.2 | 6.8..12.2 | 5.4 | 2 (9.0) |
| I3 upper terrace | -12.6..12.6 | -0.4..14.4 | 12.6..18.0 | 5.4 | 3 (6.6); WORKSHOP alcove x 5.1..11.7 |
| I4 glasshouse | -9.4..9.4 | 1.4..12.6 | 18.4..23.8 | 5.4 | 2 (7.6) |
| I5 seed vault | -5..5 | 2..12 | 29.8..41.8 | 12.0 | 1 LARGE (10.0): a glass seed pod with a lime core in the crown |

I5 is unmistakably the goal in all three: the one large slot, a lit core, the only orange frame at its own scale plus a light column rising from it.

## How each direction stacks for taller graphs (5 to N tiers; art-pass addition 4)

- **A**: tier k+1 is the tier k footprint inset by 4 BU in x and about 2 to 4 BU in y, height 8 BU, with a 0.55 BU deck and its own stair; the vault dome stays the cap, so N tiers just
  repeat the step until the half-width reaches the dome's 7 BU (A has 21, 17, 13, 9 and the dome); more tiers than that need a smaller step (2 BU) or a taller class, an open point for the designer.
- **B**: tray k+1 is the tray k oval shrunk by 2.8 x 1.6 BU on a 7.7 BU pitch; trays can be added until rx reaches the drum (about 9 trays, stack height about 70 BU, too tall for class 2:
  cap at 7 and let the extra layers share a tray as paired slots).
- **C**: the mountain is a stack of terrace rings of 3.2 x 1.8 BU step on a 5.8 BU pitch under a shell of fixed shape; extra levels *raise the shell* (the "taller graphs raise the
  glasshouse" rule) and the ramp gains turns, so N tiers cost one more ring and one more turn per level, and the shell stretches in z only.
- In all three the slots come on demand from the game graph in layer order, left to right across the level's width; a level never changes its x extents, so the spec's
  "geometry is a hint and never names the node" holds.

## Values (AAA-2 frames; clean luminance on the post's display value)

| frame | median | under 0.10 | over 0.85 | exposure | Cycles time |
|---|---|---|---|---|---|
| A street | 0.130 | 0.431 | 0.080 | 2.17 | 33.6 s |
| B street | 0.130 | 0.433 | 0.053 | 2.00 | 58.8 s |
| C street | 0.136 | 0.421 | 0.046 | 2.16 | 29.5 s |
| A inside | 0.134 | 0.432 | 0.047 | 3.79 | 27.8 s |
| B inside | 0.136 | 0.412 | 0.040 | 3.56 | 34.4 s |
| C inside | 0.135 | 0.440 | 0.029 | 3.66 | 25.7 s |

All medians are inside the 0.12 to 0.15 target; the share of pixels above 0.85 is 2.9 to 8.0 %, over the 2 % wish on every frame (the lit door, the route chrome and the glass), worst on A street (8.0 %). The exposure
is solved per frame (median target 0.14, highlight limiter 3.5 %), not a shared constant, because the frames differ in how much emission they carry.
Cycles 1920 x 1080 at 128 spp, adaptive, OIDN on the GPU; 640 x 360 tests of 4 to 8 s and 1280 x 720 tests of 15 to 20 s preceded them. The cel maps took 1.4 to 1.5 s (raw) and 2.2 to 3.3 s (ink pass)
per frame, about 15 s with the Blender start; the GPU lock was free every time I asked (the helper waited 0 s).

## Known limits (honest)

- The AAA-2 city behind the garden is a blocks backdrop (windowed boxes, a purple-navy haze): it is not the district's street kit and the avenue is bare. The plates are *garden*
  plates, not street plates; the "street" kit's building masses, signs and facade bands were not ported (too large for a concept round).
- The **Bloom on the street** is the A Necrosis material on the left of the lane, with its front at layer -0.15 against O0 and a gap of 2.15 layers to the operative (CREEPING); the garden itself
  is clean. The "inside" frame shows the front 0.6 of a layer under the I3 floor (CATCHING), so I1 and I2 are INFECTED (their lights dimmed to 12 %), I3 to I5 clean.
  The infected rooms keep their slot frames (the game's chrome draws over them); the slot frames sit in front of the glazing, not in the rooms, so they are cleaner than a real room view.
- The plaza O-route in the street frame is 6 nodes only (O0, 2 x O1, O2 x2, O3) in a simplified layout; the gate fight O3 is at the door. The plaza Terminal is the square-framed ring.
- The map frame's garden tone is subdued by design (see the ratio table); in cel the glass reads as a dark teal block.
- A has the busiest highlight clipping (8 % over 0.85 on the street frame); B's tall stacking posts are an extra vertical read in the street (a lab-equipment cue, but clutter near the door).
- The prey / DX:HR genre refs are thin: no source text for the LIMB palette or the Prey Arboretum came up.

## Rebuild

```
cd solace_vertical/garden/scripts            # all scripts are copies/patches: district sd_main/sd_lib/ink/post, HQ v5 hq_post/hq_preset/hq_kit/look_preset, Bloom 3D gs_bloom
# the three AAA-2 finals per direction (street + inside), each under the GPU lock helper (ME solace_garden), then the post:
bash finals.sh                               # rs.sh A|B|C street|inside NAME 1920x1080 128  -> D:/rc_scratch/solace_v1/garden/out/F_<view>_<dir>.png (+ npy passes, info json)
# the maps (Eevee) + ratio passes:
python gpu_run.py maps bash maps.sh 20,-44,36 270 && python gs_ratio.py A B C
# copy F_street_X.png / F_inside_X.png / M_X_map.png to X_street / X_inside / X_map, then:
python gs_sheet.py ; python gs_tables.py
```
Scene: `gs_garden.py` (the three buildings, `slot_list`, the lot / plaza), `gs_scene.py` (the Cycles scene: blocks, route proxy, slot frames, fog box, Bloom, render), `gs_bloom.py` (the Bloom node
groups with a generalised axis, tide and radial mask), `gs_post.py` (exposure solve + `hq_post.finish`), `gs_ratio.py` / `squint.py` / `gs_sheet.py` / `gs_tables.py`. `sd_main.py` has the
garden hooks (`--garden A|B|C --gx --gy --gdetail --celk --gstr --gvis --nohelix`). Scratch: `D:/rc_scratch/solace_v1/garden/`. The `*.sh` files in `scripts/` are the exact drivers used.
Notes on pitfalls found: a Blender world volume swallows the sun in Cycles (the haze is a bounded box here); `Standard` view transform, no AgX.
