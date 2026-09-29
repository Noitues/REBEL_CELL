# E — GLITCH VECTOR CRT

**Pitch:** you see the net through a vector-display cyberdeck: a glowing wireframe city on black. Heat corrupts the screen itself. The Cell's marker and stickers are the only analog things on the glass, and nothing digital can touch them.

## Three pillars
1. **Light is line.** Everything digital is a stroke of phosphor: city, roads, wheels, UI edges. There are no filled textures, only depth, glow and persistence trails.
2. **The screen is the enemy's.** Heat shows as corruption of the display (tearing, RGB split, datamosh, binary rain), from a whisper at COOL to a fight for the picture at HUNTED.
3. **Analog wins.** Paper stickers and pink marker sit *on* the glass, above the glitch. They're never lit, never glitched, never blurred. That contrast is the Cell's voice.

## Palette
| Hex | Role |
|---|---|
| `#020408` void | the black the vectors glow on |
| `#39FF9C` phosphor | city structure (hologram green) |
| `#5CE1FF` NET_CYAN | glass edges, open links, highways, defend |
| `#FF2BD6` holo magenta | billboards, ad holograms, lower deck |
| `#FF3DA8` CELL_PINK | the Cell: HQ tower, marker ink, attack |
| `#D4FF00` CELL_ACID | turf links, needles, focus, prices |
| `#FF8C1A` Meridian | enemy bezel, threat chevrons |
| `#FF4433` HARM | damage, HUNTED, drones |
| paper `#F2EEE4`, note yellow `#F2DC7A`, sticker pink `#F5AFCB`, ink `#111` | analog only |

## Materials and layering (back to front)
1. **CITY**: Grease Pencil wireframe with hidden lines removed, additive, bloom.
2. **WHEELS / FX**: additive holograms, then the light-spill pass.
3. **GLASS**: navy glass, 1 px cyan rule, Share Tech Mono.
4. **CRT**: scanlines, 1 px RGB split and vignette, then the **Heat glitch**. The world layer takes the full glitch and the glass layer a lighter pass.
5. **ANALOG**: stickers (die-cut, hard shadow, tape) and marker (GP, flat pink, a darker edge, dry streaks).

## Lighting (feedback 10)
Every emissive layer is additive on black, so light stacks. A blurred copy of the emissive layer (60–80 px) is **screened onto the glass panels only**, with a stronger rim on panel edges. In the stills the operative panel picks up pink, HOSTILE picks up orange, and the Modem panels take the sign's pink. Stickers and marker are composited after this pass, so they never receive light.

## Motion
- **Marker write-on (6):** the GP stroke is revealed by arc length in write order, with a wet dark tip at the head. When it completes, the drips grow to a bead and **hold** while the game waits. On press, the page lifts and tears out through the glitch while the drips keep running to the bottom edge (strip 05).
- **Sticker slap (8):** scale 1.18 → 1.0, the shadow snaps from far and soft to hard and close, the corner peel flattens, 2 px of settle rotation, one frame of motion blur. Paper, so no glow.
- **Binary damage (5):** 0/1 glyphs (Share Tech Mono) fire from the hit point along the hit normal, at several depths. Each carries a fading phosphor trail. White-hot near the impact, cooling to pink/cyan. There's a slash streak, and a local flash only (T2).
- **Heat glitch (11):** the level runs 0→1 by band. Tear count ∝ L^1.5, RGB split 1→4 px, datamosh blocks ∝ L², flicker bands, and binary rain from FLAGGED up. It can be switched off in Options (shown in 03). Reduce effects turns it off too.
- **Ambient:** traffic heads with persistence tails, flyer glyphs with blinkers, drones blinking on/off, billboard scanlines, needle trail.

## How the spinners get depth (4)
1. **Stacked rings at real heights.** Base plate, bezel, slice fill, glyphs, glass and needle are ~0.3 units apart. A 24° camera tilt gives **parallax offset**: the hub rides ~47 px above the bezel centre.
2. **Translucent additive slice fill**, with bright rims only on the outer edge, so you see through to the rings below.
3. **Glyphs float above the fill**, with a coloured "shadow" copy on the fill plane.
4. **Projected base glow + projector beams** from an emitter ring below: a hologram instrument.
5. **Needle drop-shadow** on the base plate, plus a phosphor sweep trail. A specular arc on the glass.

## Feedback 2–11
- **2:** vertical MODEM / CYBER SHOP redrawn in my own hand as vector neon tubes: stacked wide letters, cyan CYBER SHOP, circuit pads, one flickering E. No BUY/SHRED stickers.
- **3:** the combat city is desaturated to 30%, dimmed to 46%, blurred and tilt-shifted, with a soft scrim under each wheel.
- **4:** see above.
- **5:** 46 binary shards at mixed depths with trails.
- **6:** strip 05 shows all three phases.
- **7.1:** the HQ tower is centred, fully framed and kept sharp. A plaza in front keeps its base visible.
- **7.2:** 10–16 fog banks, each with its own blur (5–80 px).
- **7.3:** vertical tilt-shift, depth-aware: the HQ and the gunships (high = near) are kept sharp.
- **7.4:** nodes, links, labels and the grid all lie on one glass plane above the roofs. The HQ tower pierces it with a collar ring. No street-to-roof lines.
- **7.5:** four elevated routes on three levels plus a double deck, with two-way persistence traffic, street streams and flyers.
- **7.6:** ten projected billboards, fed by beams from projectors. The text is scrambled glyphs.
- **7.7:** gunships with rotor discs and cones, rooftop searchlights, and a swarm of 70 blinking drones.
- **7.8:** see 7.5, plus window dashes and blinkers.
- **8:** the hand is die-cut stickers, and the newest card is caught mid-slap.
- **9:** SEND IT over EXECUTE, JACK IN over DEPLOY, LEAVE over EXIT SHOP, RUN on the Heat poster.
- **10:** see Lighting.
- **11:** 03 shows HUNTED full-screen plus a four-band scale strip. The other stills sit at COOL or NOTICED.

## Building it in Godot 4.7
- **City:** pre-rendered per district, but as **layers**: static wireframe, a highway/traffic path set, a sky layer, and a billboard sprite set.
  - Traffic, flyers and drones run live as `Line2D` or `MultiMesh` points, with a trail shader that fades by segment age. That is cheap and matches the persistence look.
  - Grid nodes and links stay live 2D on the projected plane.
- **Wheels:** real-time `Node2D` stacks. One `Polygon2D`/`Line2D` layer per ring, each offset by `parallax * tilt` (a `Vector2` tuned per wheel), with additive `CanvasItemMaterial`, plus a radial-glow sprite. Glow uses `WorldEnvironment` 2D glow (HDR 2D on).
- **Glitch:** a full-screen `ColorRect` shader in two passes, one on the world `CanvasLayer` and one lighter pass on the UI layer. Uniforms: tear rows, split px, block hash and rain texture scroll, all driven by the Heat band. Stickers and marker live on a top `CanvasLayer` outside both passes.
- **Light spill:** a half-res blur of the emissive layer (a `BackBufferCopy` or `SubViewport`), sampled by a glass-panel shader.
- **Marker:** strokes as authored point lists: a `Line2D` with a width curve, revealed by a progress uniform. Drips are `Line2D`s grown in `_process`, each with a bead sprite. Pre-baked stroke data comes from the Blender script.

## Risks
- **Clutter:** a wireframe city is busy. It needs the hidden-line removal, depth fade and tilt-shift, or it becomes noise behind the UI.
- **Glitch vs readability and comfort:** HUNTED can hurt readability and photosensitive players. It needs the UI-layer split, the flash limiter, the Options toggle and reduce effects.
- **"Generic cyberpunk":** chrome-free, but holograms are close to the bible's anti-words. The analog layer has to stay loud to keep it REBEL_CELL.
- **Cost of the marker hand:** a stroke font needs hand-authored glyphs for every verb.
- **Blender specifics that won't transfer:** GP v3 strokes do not depth-test against meshes in EEVEE, so occlusion was done by ray casts. Godot needs baked hidden-line output, not live 3D.
