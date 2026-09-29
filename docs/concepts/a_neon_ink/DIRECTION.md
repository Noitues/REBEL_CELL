# A — NEON INK

**Pitch:** the whole game is a concept artist's ink pass, lit in neon. Every building, wheel and cable is a hand-drawn line that glows, and the Cell's marker and stickers are the only solid, matte things on screen.

## Three pillars
1. **The line is the material.** Silhouettes are thick, detail is hairline, and corners overshoot like construction lines. Fills are used only where they're needed to occlude or to read.
2. **Glow is information.** Only strokes that mean something glow at full strength: the wheels, nodes, routes, the HQ and the Modem sign. The generic city is drawn at 55% line opacity, and the backdrop in combat is grey ink.
3. **The Cell doesn't glow.** Marker, stickers and paper sit above the bloom pass and throw no light (feedback 10). That keeps the zine special and readable.

## Palette
| Role | Hex |
|---|---|
| Void background / glass fill | `#04050A` / `#050D1C` |
| City faces (right / left / top: value gives form) | `#04060C` / `#090D18` / `#0D1322` |
| Geometry ink (buildings, glass edges, defend) | `#5CE1FF` cyan |
| Cables, brand, marker, attack | `#FF3DA8` pink (neon core `#FFD0EA`) |
| Focus, needle, claimed turf | `#D4FF00` acid |
| Holograms, fifth ink / Halcyon enemy | `#B04DFF` / `#8C7BFF` |
| Harm, binary shards, Heat HUNTED | `#FF4433` (police `#FF2A3A` / `#3A6BFF`) |
| Receding combat city | `#3E5670` lines on `#10141D` |
| Paper / ink / sticker border | `#F2EEE4` / `#111111` / `#FBFAF6` |

## Materials and layering (back to front)
City depth bands (each on its own blurred plane) → fog patches → holograms (additive) → flyers → the grid overlay on the ground plane → glass UI → wheels → FX → **bloom** → stickers and paper → marker. The depth comes from stacking these planes, from line weight (3.6 px bezels, 1 px ticks) and from three value steps per box. There are no textures.

## Lighting and spill (10)
A compositor bloom runs on the glowing planes only. Each emitter also gets an explicit additive **spill pool**: a pink ellipse under the operative wheel, a halo under the enemy wheel in its corp hue, the Modem sign's pink wash over the left edges of the shop panels, the HQ's pink pool on its street, and a gradient on the bottom edge of each forecast tag, lit from the wheel below it. Marker and stickers are composited after the bloom, so they never cast light.

## Motion
- **Marker write-on (6):** each glyph is a single-stroke path. It's revealed by arc length at about 60 ms per stroke, with an ink pool where the nib lands and a dry flick at the end. Drips grow from the lowest points of the letters, then **hold**: the beads swell 2% on a 1.6 s loop while the game waits. On press the page slides up while the drip lines keep extending down the screen.
- **Sticker slap (8):** each card scales from 122% to 100% with a 2-frame overshoot. The hard shadow shortens from 44 px to 9 px, impact ticks flash, and a peeled corner settles flat.
- **Binary shards (5):** 30–50 inked `0`/`1` glyphs and glass chips fly out on the hit's outward cone, each with a streak. They're HARM-coloured with white cores, last 0.5 s, and are local to the T2 hit.
- **Heat glitch (11):** a screen shader scales with Heat. It does a 1–2 px chromatic split, adds a few tear bands and block slips, adds scanline flicker, and pulses red at the screen edges at HUNTED. It's off under Reduce Effects or its own toggle.
- The line "boils" at 8 fps: the wobble seed swaps every few frames, which gives the living-sketch feel. It's T0 and stops under Reduce Effects.

## How the spinners get depth (4)
1. **Stacked rings at real heights.** The bezel face, the recessed glass, the raised hub and the floating needle each sit at their own height, projected on a disc tilted about 37°, so they shift against each other.
2. **Visible side walls.** The outer bezel wall is hatched, darkest at the sides. The inner recess wall shows on the far side, so the glass reads as sunk into the bezel.
3. **Cast shadows by height.** A soft drop shadow falls under the whole wheel, and the needle casts its own offset shadow onto the glass.
4. **Glass inlays.** Slices are 30% translucent fills with a bright outer rim and dark seams, with two specular sheen arcs floating above everything.
5. **Line-weight hierarchy.** The bezel is 3.6 px, the rims 2 px and the ticks 1 px. The HP arc is a separate thick ring that sits under the wheel on the table.

## Feedback answers
2 The Modem sign is redrawn as hollow neon tubes (body, dark core, hot filament) inside a double rounded frame, with circuit traces. MODEM runs vertically in pink and CYBER SHOP in cyan. The BUY/SHRED paper stickers are gone and replaced by glass price chips. · 3 The combat city is grey ink at 75% opacity, blurred 6–9 px and under a 45% scrim. · 4 See the spinner section above. · 5 Binary shards. · 6 See the marker strip (05). · 7.1 The HQ is a 13-storey pink-rimmed tower, fully in frame, with the skyline cleared around it. 7.2 Fog comes as patches on three planes blurred 6, 16 and 40 px. 7.3 Tilt-shift uses five depth bands, blurred 7, 4.5, 2, 0 and 5 px. 7.4 Nodes and links are drawn on the ground plane and routed along streets, with no risers. 7.5 There are five highways at 1.5–4.6 tiles of height, with pillars and two-way traffic, plus about 20 flyers with trails. 7.6 Six projected holograms with light cones and illegible type. 7.7 Helicopters, searchlight cones and pools, drones with scan fans, and red/blue flicker. 7.8 Cables between roofs, lit windows, blade signs and traffic. · 8 Hand-of-cards stickers (combat) and shop stickers on the glass. · 9 SEND IT and JACK OUT are scrawled over washed EXECUTE and DISCONNECT. · 10 See the lighting section above. · 11 See the Heat glitch under Motion.

## Building it in Godot 4.7
- **Wheels, marker, shards and HUD are real-time `Line2D`/`Polygon2D`** drawn by code from the same projection maths (`wproj`). Write-on is a `Line2D` whose points grow by arc length. The boil is a vertex-jitter shader keyed to a stepped time.
- **The city is pre-rendered per district**: one sprite per depth band (already blurred for tilt-shift), plus the additive hologram and fog layers. Traffic, flyers, blinkers and holograms are live sprites or `Line2D` on top. Bands give cheap parallax.
- **Glow uses a `WorldEnvironment` 2D glow (HDR) on a SubViewport** that holds only the glowing layers. Stickers and marker sit on a later CanvasLayer that the glow doesn't reach. The spill pools are additive `Sprite2D` gradients.
- **Heat glitch** is one `canvas_item` screen shader on the top BackBufferCopy.

## Risks
- The city can become wall-to-wall cyan noise. It needs strict opacity discipline, and the HQ, nodes and routes must always win.
- Text on hand-drawn wobble has to stay legible, so UI type stays crisp mesh or font type and is never inked.
- The boil animation can tire players or trigger motion sensitivity, so it needs a slow cadence and the Reduce Effects kill switch.
- Pre-rendered bands must be re-baked when districts change.
- Performance: thousands of `Line2D` points on low-end hardware. Bake anything static.
