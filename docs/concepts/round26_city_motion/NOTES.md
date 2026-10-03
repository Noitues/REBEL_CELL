# Round 26: city motion v2 (more highways, complex interchanges, v3 HQs)

This round builds on round 24, whose motion layers are locked (designer: "The city life looks amazing! All of the layered things look great."). The layers themselves are unchanged. What is new:
- more elevated highways and interchanges;
- the base is now the current map with the new HQs.

## Files
| File | What |
|---|---|
| `city_ambient_night_v2.gif` | 960x540, 48 frames x 80 ms (3.84 s), seamless loop, 3.6 MB. |
| `city_ambient_day_v2.gif` | Same, by day, 2.0 MB. |
| `interchanges.png` | Close-ups, night and day, from the 2x composite with fog, rain and tilt-shift off. A is the four-level stack, B the cloverleaf, C the spiral ramp and flyover crossings. |
| `storyboard_ambient_v2.png` | Key frames for night and day, with timings and notes. |
| `scripts/` | `cm.py` (round 24 scene, copied and patched for the v3 bases and the road network), `roads.py` (new), `bases.py` (new), `fx.py`, `make_ambient.py`, `make_boards.py`, `inspect_gif.py`, `zoom.py`, `clean_scratch.py`. Run them from this folder with `python scripts/<name>.py`. |

## Road network
Every road runs along a real avenue of `round6_city_restyle/city_layout.json`. Deck heights are in output px.

| Road | Avenue | Deck | Rails | What it does |
|---|---|---|---|---|
| A | j=4 | 18 / 34 | pink / cyan | Double deck, as in round 24. Ramps down in the Sprawl. |
| B | i=6 | 52 | amber | As in round 24. Ramps down by the Cell's turf. |
| **C** | j=-5 | 26 | mint | Passes under B (52) and under F (44), which makes two **flyover crossings at three heights**. It then leaves the grid down a **1.75-turn spiral ramp** round a core column to street level. The spiral is one-way, down. |
| **F** | i=-10 | 44 | violet | Meets A in a **cloverleaf**: four 270-degree loop ramps climb from A's lower deck up to F. Each loop is tangent to both avenues and one-way. Ramps down near Orbital. |
| **D** | j=43 | 20 | orange | Crosses E in a **four-level stack** beside Orbital (see below). |
| **E** | i=17 | 40 | cyan | Crosses D in the stack. |

The stack has four directional flyover ramps, one per quadrant: two at 62 (amber rails, tight radius) and two at 84 (pink rails, wide radius). The ramps are one-way with two lanes.

That gives 16 roads in total.

**Traffic** follows the round 24 language:
- Highways are four-lane and two-way, with headlights one way and tail lights the other at night, and coloured cars by day.
- Ramps and loops are two-lane and one-way.
- Every lane moves a whole number of car gaps per loop, so the GIF loops seamlessly.

**Drawing order:**
- Decks are painted low to high, then back to front, and each deck draws its own cars. Upper levels therefore hide the traffic underneath them.
- Glow for rails and car lights is added only where that deck is the top one. A coverage buffer of deck heights is built once.
- Pylons are depth-tested against the towers, using the same building depth buffer as round 24's street traffic.
- Billboards are kept off any spot a deck covers.

## Bases
- **Night:** `round25_hq_targets/city_night_hq_v3.jpg`. It has the new HQs and the same framing as round 24. The labels are redrawn crisp on top.
- **Day:** there is no v3 day map yet, so `bases.py` derives one:
  - Everywhere the v3 night map matches round 6's night map, it uses round 6's day map.
  - Where they differ (the new HQs and the cleared fist roads), it takes the v3 night pixels and grades them night → day. The grade is a per-channel quantile curve fitted from round 6's own night/day pair.
  - The result reads well for Halcyon and the Cell's base. Orbital's base stays a little bright.
  - Swap in a true v3 day render when round 25/26 produces one.

## Building it in Godot 4.7 (additions to round 24's NOTES)
- **Each road** is a Path2D baked into a curve. It carries an elevation curve (a Curve resource sampled by offset), so ramps, loops and spirals are the same node type as straight decks.
- **Decks** are a Polygon2D strip (top + side) generated from the path in a tool script, then baked to a texture or atlas per interchange. The decks never change, so they cost nothing at runtime.
- **Draw order:** give each deck strip a `z_index` from its elevation band (`round(elev / 3)`) and use y-sort within a band. Cars are a MultiMesh child of their deck, so they share its z.
- **Cars:** as in round 24, a vertex shader moves each MultiMesh instance along a baked position texture. For ramps, add elevation to the texture's y.
- **Glow:** render only the top-deck lights into the glow layer by baking a deck-coverage mask. The shader discards a light when `coverage > own_elev`.
- **Performance:** 16 roads come to about 900 deck cars. That is 16 MultiMesh draws (or about 6 if roads are merged per interchange) on top of round 24's budget.
- **Reduced motion:** as round 24. Ramp and loop traffic runs at 40% speed with no streaks, and the spiral shows static cars.
- **Tuning:** deck heights, lane counts and speeds belong in the city config `.tres`.

## Notes
- The cloverleaf sits in the upper tilt-shift band, so in the GIF it reads soft (depth). `interchanges.png` shows it sharp.
- To stay under 4 MB, the night GIF's encoder treats colour changes under 28 levels as unchanged (day: 20). Small glows band slightly as a result.
- The labels in the close-ups (`THE SPRAWL`, `R…`) are baked into the base map. They are not overlays.

## v3: sky lanes (designer: shapes locked, decks out, faster)
| File | What |
|---|---|
| `city_ambient_night_v3.gif` | 960x540, 48 x 80 ms, 3.2 MB. |
| `city_ambient_day_v3.gif` | 3.0 MB. |
| `interchanges_v2.png` | The stack, cloverleaf and spiral/flyovers as sky lanes, night + day. |

- **The road shapes are unchanged.** Same 16 paths and heights as v2, with no deck surface, side, rail, pylon, spiral column or day shadow. Each lane is now just:
  - fast cars, each with a light streak, a dark body and an under-glow;
  - faint lane-guide dots every 9 px. Two-way lanes get one row along each edge; one-way ramps get a single centre row in the ramp colour.
- **Night lanes** use headlights one way and tail lights the other, as before. **By day** the streaks take the lane colour (pink, cyan, amber, violet, mint, orange) so the shapes still read against the bright city.
- **Speed.** Highway cars now move 14-20 car gaps per 3.84 s loop (was 2-4), about 6x faster. Spacing is 1.4x wider so the lanes don't smear. Street-level traffic is unchanged.
- **Draw order.** Cars are sorted by height band, then screen y, so higher streaks pass over lower ones.
- **Script.** Set by `roads.Network.sky = True`. Run `python scripts/make_ambient.py v3` and `python scripts/make_boards.py inter2`. v2 is kept.
- **GIF compression.** The night v3 GIF treats colour changes under 36 levels as unchanged, to stay under 4 MB, so streak tails band a little.
- **Godot.** Drop the deck Polygon2D strips. Each lane is its Path2D + elevation curve, a MultiMesh of car quads with a stretched additive streak, and one MultiMesh of guide dots per road.

## v4: mixed lane colours (designer: flying cars and speed locked)
- `city_ambient_night_v4.gif` (3.4 MB) and `city_ambient_day_v4.gif` (3.2 MB): 960x540, 48 frames x 80 ms.
- **Colours.** Each sky-lane car picks one of the six lane colours at random (pink, cyan, amber, violet, mint, orange). The pick is seeded per car, and it applies day and night to the streak and the under-glow.
- **Mixing.** Every lane carries all six colours. The lane-guide dots keep their lane colour.
- **Unchanged from v3:** speed, shapes and street traffic.
- **At night** the white headlight dot stays at the nose, so travel direction still reads.
- **Script.** Set by `roads.Network.mixed = True`. Run `python scripts/make_ambient.py v4`. v3 is kept.
- **Godot.** A per-instance colour (INSTANCE_CUSTOM) on the car MultiMesh, picked from a 6-colour palette in config by a seeded RngService stream.
