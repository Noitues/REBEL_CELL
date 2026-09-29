# B // TILT-SHIFT DIORAMA

**Pitch:** the city is a premium miniature on the designer's desk, shot through a tilt-shift lens. The system's cold glass floats over it, and the Cell scrawls on the glass in marker.

## Three pillars
1. **A model you could touch.** An orthographic iso city of simple meshes with emissive window grids, wet asphalt, pylons and fog pockets. A depth-of-field band keeps the play plane sharp, and everything else melts.
2. **Hardware you could hold.** Spinners are machined objects lit by the scene: a bezel, a glass dome, frosted slice inlays and a needle. Combat is a close-up of two instruments, with the city far behind them.
3. **Ink on the glass.** The Cell's voice is the only flat 2D layer. Marker, drips, stickers and tape are composited on top, never lit and never blurred.

## Palette
| Hex | Role |
|---|---|
| #05070D / #0C1224 | Night base; world and deep shadow |
| #1C2334 / #221F30 | Slate building masses |
| #FFCF8A / #9FE6FF / #FF7AC8 | Window light, warm, cool and pink (city life, never UI) |
| #FF3DA8 | Cell pink: marker, HQ crown, ATK slices, the operative's bezel rim |
| #D4FF00 | Acid: Cell network links, the needle, focus |
| #5CE1FF | Net cyan: glass edges, DEF slices, open links, highway rails |
| #FF8C1A | Meridian corp hue: the enemy bezel and its stripe pattern |
| #FF4433 / #FF3344 | Harm: threat routes and 0/1 shards (red tail lights are traffic only) |
| #7BE07B | Gain: HP arcs |
| #F2EEE4 / #F2DC7A / #F4C3CF | Sticker paper stock |
| rgba(5,13,28,.8) | Glass tint: the same token as TERMINAL_BG |

## Materials and layering (back to front)
1. **CITY (3D):** slate meshes with procedural window grids, asphalt with noise-driven roughness (puddles), holo planes, beams and volume pockets.
2. **Depth post:** tilt-shift (depth plus a vertical band), bloom, grade and vignette.
3. **GLASS (2D):** a frosted crop of the frame under a navy tint, with scanlines, a 1 px cyan edge and a pink title rule, plus the **light-spill add**.
4. **Map layer:** nodes and links sit on one z plane and are written to the depth pass as "in focus", so they never blur.
5. **PAPER / INK (2D):** Grease Pencil fills for stickers and tape, then GP strokes for marker and drips, then grain.

## Lighting and spill (10)
Every emissive thing is a light. Slice inlays carry small point lights that tint the bezel, needle and glass. Sign tubes light their facade, awning and the wet street. For UI, the bloom source is blurred wide (about 70 px) into a **spill map** that is added into each glass panel and brightens its edge where a glow sits close. The forecast panels pick up the spinners' pink and orange. Marker and stickers are composited after the spill, so they stay flat (the brief excludes them).

## Motion ideas
- **Marker write-on (6):** single-stroke glyphs (`stroke_font.py`) are truncated by arc length. At 0–0.45 s the pen nib leads the stroke, with pressure heavy at landing and lifting at the end.
- **Drips (6):** drips spawn only at stroke ends that are heading down. The bulbs swell for about 0.6 s, then hold while the game waits. On press the page slides up and smears, but the drips detach and keep running down over the next screen.
- **Sticker slaps (8):** a card enters at 114% scale with its shadow offset ×4 (lift = 1). It hits in 90 ms with an overshoot of −3° rotation and white impact ticks, and the shadow snaps to (9, 13). One corner may peel.
- **Binary shards (5):** extruded 3D "0" and "1" glyphs tumble out of a cone at the hit point. Each has a tapered streak back to the impact, a hit flash, and a point light that briefly lights the enemy bezel.
- **Heat glitch (11):** RGB split, a few horizontal slice displacements, red scan ticks, and a slow flicker band. The city takes the full amount and the UI gets 25%. It scales with the Heat band and has an Options toggle.

## How the spinners get depth (4)
1. **Real thickness plus tilt:** the bezel runs 0.45 R deep, and the wheel is tilted 12–16° toward the screen centre so the machined side wall shows.
2. **Stacked planes:** the back plate, then the recessed slice well, the frosted inlays with a raised bright lip, the metal divider fins, the hub, the needle under the hub, and the glass dome on top. Each layer catches light differently.
3. **Glass with a glint:** a transparent coated dome with a soft reflected-window arc. Parallax between the dome glint and the inlays sells the glass.
4. **Self-light plus a stage key:** inlay point lights spill onto the bezel. A cool key and pink/orange rims are parented to the camera.
5. **Separation from the world:** the city is far behind (aerial perspective: blur 4.5, 40% saturation, lifted blacks). A soft drop shadow falls from each spinner onto it.

## Feedback answers
- **2 Modem sign:** the vertical MODEM in pink tube, circuit traces with ring pads, and cyan CYBER / SHOP in a rounded pink frame. It is an original redraw lit in 3D, and the BUY/SHRED paper is gone.
- **3 Combat backdrop:** the city recedes through defocus, desaturation and a cool haze rather than going black.
- **4 Spinners:** see above.
- **5 Shards:** 3D 0/1 glyphs.
- **6 Marker:** see the strip.
- **7.1 HQ:** the tower is fully framed, with a hex halo on the map plane.
- **7.2 Fog:** eleven or more noise-shaped volume pockets with different densities. Blur varies with depth.
- **7.3 Tilt-shift:** yes, by depth plus a vertical band.
- **7.4 Map plane:** nodes and links sit on one plane, always sharp.
- **7.5 Traffic:** five highways at 0.9–3.5 u on pylons, ground traffic, sky lanes and hover cars.
- **7.6 Holo billboards:** translucent emissive planes with scan bands and illegible glyph blocks, plus projector beams.
- **7.7 Heat escalation:** helicopters, searchlights, drones, threat routes, corp alarm lights and a police wash.
- **8 Stickered cards:** die-cut stickers with tape and a peel.
- **9 Marker over digital:** SEND IT over EXECUTE, JACK IN over CONNECT, LAY LOW over PROCEED, LEAVE over EXIT.
- **10 Light spill:** the spill map.
- **11 Heat glitch:** as above, with an Options toggle shown on screen.

## Building it in Godot 4.7
- **City:** real-time 3D in a `SubViewport` with an orthographic `Camera3D`. MultiMesh buildings use one shader (window grid from world position plus an instance random). The ground uses SSR for the wet look. Traffic is instanced quads on paths. Holos are unshaded additive planes. Fog pockets are `FogVolume`s. A cheaper fallback is baking per-district plates plus a depth texture offline.
- **Tilt-shift:** a full-screen shader samples a depth texture, or `hint_depth_texture` when real-time, blends 3–4 mip-blur levels, and adds the vertical band. The map layer renders in its own viewport over the blurred city.
- **Spinners:** real 3D in a small `SubViewport`, one per wheel, or pre-rendered layer sprites (bezel, inlay, dome glint, needle) in a 2.5D stack with normal-mapped lighting. Rotation is only a Z rotation of the inlay layer, so sprites are viable.
- **Glass spill:** `BackBufferCopy` plus a blurred emissive buffer that panel shaders add in. Bloom goes in `WorldEnvironment` glow.
- **Ink:** Line2D and Polygon2D driven by the same stroke data. Write-on animates the points; drips are Line2D with a width curve plus a bulb. Stickers are Polygon2D with a shadow; the tween is AnimationPlayer.

## Risks
- **Cost:** GPU cost of a real-time 3D city with DOF and volumes on low-end hardware. Baked plates are the fallback.
- **Readability:** blur must never touch information. The map layer and all UI must stay out of the DOF path, as they do here by construction.
- **Busyness:** window confetti and traffic can compete with UI, so tune window density and scrim per screen.
- **Heat glitch:** it can hurt legibility and comfort. It needs a hard cap on the UI and a toggle, both shown.
- **Hand-drawn font:** the single-stroke marker font must be hand-tuned. It is a placeholder glyph set here.
