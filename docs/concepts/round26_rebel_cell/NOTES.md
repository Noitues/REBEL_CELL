# Round 26: the REBEL_CELL base (home, and DISPATCH after the betrayal)

Round 25's base was rejected: "crappy up close, not great from afar". This round tries four directions, each
rendered as a city-map crop, a night close-up and a DISPATCH close-up, and combines the best into one option.

## The rules every image follows
- **One model, one layout.** `scripts/hq26.py` rebuilds the game's own streets and buildings round the palm of the
  fist roads from `round6_city_restyle/city_layout.json` (round 25 `citydata.py`). It renders:
  - the perspective close-up;
  - the orthographic map sprite in the game's 2:1 iso projection.

  `scripts/map26.py` pastes that sprite into the round 6 restyled map.
- **Shared rules.** `scripts/idea_cfg.py` decides, for both views:
  - which city buildings make way for each hero;
  - which roofs carry paint.

  The map and the close-up therefore always agree.
- **Home and DISPATCH share one layout.** The RNG draws are identical in both states, so only colours, dead signs,
  glitches and red cables change.
- **Colours.** Lime #D4FF00 for turf and links, pink #FF3DA8 for verbs. DISPATCH is red: dead signs, torn screens,
  red cables, "DISPATCH" on the signs.

## The ideas (`options_sheet.jpg`, `idea_<n>_*_{map,close,dispatch}.jpg`)
| # | Idea | Fist from the map? | Up close? |
|---|---|---|---|
| 1 | **Tokyo Street.** A hijacked sign canyon along the fist road under the thumb, ending in the Cell tower (giant fist screen, relay mast). | Only through the roads. The tower covers the palm. | **Best.** Stacked blade signs, wires, lanterns, vending machines. This is the "home" feeling. |
| 2 | **Painted Roofs.** Roofs inside the fist outline (tested at their *projected* map position) are crudely painted red, with drips and roller stripes. A paint-works crew base sits in the palm. | Subtle, as asked: it thickens the road fist. | Gritty and believable, but there is no single HQ to fight at. |
| 3 | **Hijacked Skyline.** A block of screen-covered towers projecting a giant scanline hologram fist. | The loudest fist, **but it covers the road fist's fingers.** | A strong beacon. Its sky position sits in the gap between the wheels. |
| 4 | **Knuckle Deck** (own idea). A converted parking structure whose plan *is* the crest: wrist (2 levels with ramps), thumb (3 levels), four finger decks (6 / 7 / 7 / 6 levels). | **Yes, at a glance.** The crest sits in the palm. | It is a real building with a fist silhouette: four knuckles rising behind the thumb. |

## Recommended (`recommended_*.jpg`, `combat_rebel_cell.png`)
**The Knuckle Deck at the head of a hijacked canyon.**
- The deck is rotated onto the axis of the thumb road. A shorter Tokyo canyon runs along that road to the deck's
  wrist.
- The deck carries a hijacked screen on each knuckle, fist banners on the thumb, tags on every parapet, a ramp front,
  and the relay mast.
- **Map:** the crest building sits inside the road fist.
- **Combat:** the camera looks over the canyon at the knuckles. The two middle knuckle screens (fists) land in the gap
  between the wheels.
- **DISPATCH:** the same model turned red and corrupted. `combat_rebel_cell.png` reuses the round 25 composite: locked
  D4 wheels, the DISPATCH boss wheel, sticker cards and SEND IT.
- **Also kept:** idea 1's street-level camera is the strongest "home" image. It could serve the non-boss Cell
  screens.

## Regular site: `site_modem_red_night.png`
The locked F1B tenement facade (round 12 scripts), with the round 4 MODEM sign recoloured to DISPATCH red
(`scripts/modem/red_sign.py`):
- the pink tubes become red;
- CYBER SHOP becomes red-orange;
- the "D" is a dying tube.

The sign spill lights are red too.

## Weakest parts / open
- **The ideas outscale the city's grain.** Hero buildings use 2–5-lot footprints and the city uses lots under 1. The
  deck reads as a landmark. The Tokyo tower dominates the palm.
- **Glyphs are blocky placeholder "kanji".** Many lime plates read lime-on-olive once the bloom spill is added.
- **Painted roofs:** the DISPATCH version differs little from home (the glowing paint is close to the painted red).
- **Map sprites are lit in Blender.** They are toned and painted to match the map, but they are still smoother than
  the round 6 facets.
- **The rec close-up's left edge** is a plain canyon wall. It sits behind the player wheel in combat.

## Build (from `scripts/`, all seeded)
1. `python layout26.py`
2. `python run26.py <idea>:close[:dispatch] <idea>:map ...` (Blender 5.2, about 15 s per job)
3. `python post26.py rc26_<idea>[_dispatch] ...`
4. `python map26.py`
5. `python make_sheet26.py`
6. Wheels: `wheels_r18/render_bosses24.py rebel_cell`, `wheels_r18/dump_boss_slots24.py`,
   `combat_r23/render_player24.py`
7. `python make_combat26.py`
8. `python modem/run_red.py`

The `CAM26="x,y,z,tx,ty,tz,lens"` environment variable overrides the close-up camera for framing.
