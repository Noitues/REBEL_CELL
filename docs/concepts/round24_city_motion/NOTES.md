# Round 24: city motion (living city, Heat levels, incursion)

Builds on the approved round 6 city restyle (`round6_city_restyle/views/restyle_*_full.png`). Answers ART_FEEDBACK_R2 item 7 (city life) and the designer's note "if you make them moving it will read super well".

## Files
| File | What |
|---|---|
| `city_ambient_night.gif` | Calm Heat at night. 960x540, 48 frames x 80 ms (3.84 s), seamless loop, 3.0 MB. |
| `city_ambient_day.gif` | The same by day: no rain, warm haze, coloured cars instead of light streaks. 1.8 MB. |
| `city_heat_levels.gif` | NOTICED > FLAGGED > HUNTED on the map. 800x450 (rendered 960x540 and reduced to stay under 4 MB), 120 frames x 85 ms, 3.7 MB. |
| `city_incursion.gif` | Halcyon Civic incursion warning. 960x540, 84 frames x 85 ms, 3.5 MB. |
| `storyboard_*.png` | One labelled board per GIF: key frames, captions with timings, and a timeline. |
| `motion_layers.png` | The layer breakdown (bottom to top), each layer shown on its own. |
| `scripts/` | `cm.py` (scene + layers), `fx.py` (Heat/raid props), `make_ambient.py`, `make_heat.py`, `make_incursion.py`, `make_boards.py`, `inspect_gif.py`. Run from this folder with `python scripts/<name>.py`. |

## What moves
- **Traffic on real avenues.** Avenue runs come from `city_layout.json` street tiles (lines with 60+ tiles). At night cars are a headlight dot with a short streak one way and red tail lights the other way. By day they are small coloured cars. Cars hide behind towers: a depth buffer is built from the layout's building prims, and a car only draws where no nearer building covers it.
- **Elevated multi-level highways.**
  - A is a double deck over avenue j=4. The lower deck has pink rails and the upper deck cyan rails.
  - B is a single high deck over avenue i=6, with amber rails. It crosses over A in the Sprawl.
  - Both ramp down to street level before the HQs.
  - Each deck has 4 lanes of traffic, plus pylons (also depth-tested) and a day shadow.
- **Flying cars** on three sky lanes, 70-120 px above avenues j=-9, i=21 and j=20. Each car has a light trail and an under-glow. The lane markers are chase lights.
- **Hologram billboards.** There are 8, on tall roofs away from the labels. Each one is a parallelogram on a facade axis with a projector beam. It cycles 3 illegible panels (pictogram + glyph rows, scanlines) every 16 frames with a wipe, plus random dropout and jitter.
- **Fog banks.** Patchy, drifting, and they blur whatever is under them, more where they are thicker. Fog thins around district labels and HQs so nodes stay readable. At night the fog is tinted by the city's own light.
- **Rain (night only).** Streaks at two depths, plus splashes on visible street points.
- **Steam** from 13 vents, on streets and roofs.
- **Aviation lights.** Red blinkers on the 26 tallest towers, and a white double-strobe on the tallest.
- **Tilt-shift.** Blur in the top and bottom bands, with a little distance haze at the top. Labels are redrawn crisp after it.

## Heat on the map (locked language)
| Band | What shows |
|---|---|
| NOTICED 31 | 3 rotating alarm beacons on side buildings round the Cell's turf. Nothing on the target. |
| FLAGGED 58 | 2 searchlights sweeping the sky from side blocks, and 2 alarms ON the target roofs. |
| HUNTED 82 | 13 red/blue police clusters on the turf's streets, 2 searchlights on the target, 2 choppers circling with jiggling spotlights, a 3rd chopper entering from the right, crossing and leaving top-left, and 6 drones with mini spots. |

- The Heat chip flashes and counts up at each cut.
- The Cell's Sites (lime pads) and links (lime, with packets) stay visible in every band.

## Incursion
The sequence runs in this order:
1. Halcyon's HQ raises the alarm: violet rings and amber corner beacons.
2. The INCURSION WARNING banner drops in.
3. Two threat routes draw along real avenues toward two Cell Sites (violet trace, amber chevrons flowing toward the Cell).
4. Two convoys of three armoured carriers roll out. They use the round 20 Halcyon livery: violet hull, white roof plate, amber light bar, violet street spill.
5. Three choppers lift off the pyramid, climb, peel away on separate arcs, switch on their spots and orbit the targets.
6. At 58 frames the banner adds "RAID INBOUND" and the targeted Sites ring red.

## Building it in Godot 4.7
Layers bottom to top (see `motion_layers.png`):
1. **Base.** The baked city texture (or the live city scene) as one Sprite2D. Labels stay a separate Control layer on top of everything.
2. **Occlusion mask.** At map build time, bake a single-channel "front depth" texture from the building footprints. A street sprite samples it in its shader and discards itself when `depth > own_ground_y`. This is the same test the concept uses, and it costs one texture fetch.
3. **Street traffic.**
   - One Path2D per avenue run, generated from the layout.
   - Cars are a MultiMeshInstance2D per direction: one quad per car, with the offset computed in the vertex shader from `TIME * speed + instance_offset`, mod the path length.
   - The path is baked to a 1D position texture (an RGBA32F strip). Use this rather than a PathFollow2D per car, which costs a node per car.
   - Thousands of cars stay one draw call.
4. **Highways.** Static deck and pylon sprites (or a Polygon2D strip) at deck height, rails as additive Line2D, and lane traffic as in layer 3 with paths offset up by the elevation.
5. **Billboards.**
   - One quad per sign, skewed to its facade axis.
   - A shader samples an atlas of illegible panels and handles everything else: `panel = floor(TIME / period + phase)`, a wipe edge, scanlines (`fract(UV.y * lines)`), and flicker (hash of the floored time).
   - Draw with additive blend (`render_mode blend_add`) and keep the alpha low by day.
6. **Aviation lights and beacons.** One MultiMesh of additive dots; blink phase is per instance (INSTANCE_CUSTOM).
7. **Fog.**
   - A full-screen ColorRect shader.
   - Density comes from two samples of a tileable noise texture (NoiseTexture2D, seamless) scrolled in opposite phase and crossfaded. Multiply by a "keep" mask texture (thin round labels/HQs) and by a vertical gradient (thicker far away).
   - For the varying blur, read `textureLod(screen_texture, uv, density * max_lod)` with `hint_screen_texture, filter_linear_mipmap`, then mix in the fog tint.
8. **Rain and steam.**
   - Rain is a GPUParticles2D covering the view: 2 emitters for the 2 depths, a streak texture, fixed direction, and a collision-free splash sub-emitter fed from visible street points.
   - Steam uses one GPUParticles2D per vent: a soft puff texture, scale curve up, alpha curve out, slight wind.
   - Night only for rain.
9. **Sky lanes.** Path2D lanes and the same MultiMesh car technique, with a Line2D trail (or a stretched quad) per car. Drawn above the fog.
10. **Raid and Heat props.**
    - Choppers and drones are AnimatedSprite2D or low-poly sprites on PathFollow2D (circle and bezier paths).
    - Spotlight cones are additive sprites (cone texture + pool ellipse) parented to the craft. Jitter comes from a small noise offset on the pool, not on the craft.
    - Sky searchlights are an additive cone sprite with a rotation tween (ping-pong).
    - Police strobes are a MultiMesh of additive spill ellipses plus cores, with phase per instance.
11. **Tilt-shift.** A last post pass on a BackBufferCopy or CanvasLayer: `textureLod(screen, uv, mask * max_lod)` with a mask of top/bottom bands, max'd with fog density. Bloom comes from the WorldEnvironment glow (2D HDR on) on additive layers only.
12. **UI.** Labels, Heat chip, banner. Never blurred.

All speeds, periods, counts and densities belong in the city config `.tres`: lane speeds, billboard period, fog drift, rain count, choppers per band, and so on. Per-band Heat props are a table keyed by band (NOTICED/FLAGGED/HUNTED), matching GDD 4.3 thresholds 25/50/75. Randomness (car offsets, billboard phases, vent positions) comes from a seeded RngService stream so the map looks the same on reload.

## Performance
Targets assume the full 1080p map on mid hardware:
- **Traffic.** About 1,500 street cars + 300 highway cars + 30 flyers in 6-8 MultiMesh draws. Animation is vertex-shader only, so there is no per-car script.
- **Fog and tilt-shift.** Two full-screen passes using mip LOD, not multi-tap gaussians. Run them at half resolution on low settings.
- **Rain.** 1,200 + 100 particles. Halve them on low.
- **Steam.** 13 emitters x about 8 puffs.
- **Billboards.** 8 quads, all in one atlas.
- **Occlusion mask.** Bake once per map, about 2 MB as R16 at screen size. Rebake only when the city changes.
- **Heat props.** At most 3 choppers + 6 drones + 13 clusters, all additive sprites.
- **Pausing.** Pause every ambient layer when the map is covered by a panel or the window is unfocused (`process_mode`, emitter `emitting = false`).

## Reduced motion
This hooks into the Settings reduced-motion switch:
- **Ambient.**
  - Traffic stays, at 40% speed with no streaks (static dots that drift slowly).
  - Billboards hold one panel; no flicker, jitter or wipes.
  - Fog is static (no drift); its blur stays.
  - Rain is replaced by a faint static wet-sheen tint.
  - Steam is off. Sky lanes show their markers, without moving cars.
  - Aviation lights glow steadily (no blinking). Tilt-shift stays, since it does not move.
- **Heat.**
  - Beacons and police show as steady coloured glows, with no rotation or strobe. Never flash faster than 3 Hz.
  - Searchlights hold still at fixed angles.
  - Choppers and drones are parked over the target with steady spots: no orbit, no jiggle, no rotor spin.
  - The Heat chip changes value without the flash.
- **Incursion.**
  - The routes appear complete, with static chevrons.
  - Convoys and choppers jump to their final positions with one 300 ms fade.
  - The HQ rings are replaced by a steady violet outline. The banner fades in instead of dropping.

## Notes and open points
- The two incursion routes and the Cell Sites (tiles 26,24 / 30,31 / 26,31) are placeholders chosen on real avenues. In game, routes come from the raid's threat routes.
- The heat GIF is 800x450 to stay under 4 MB. The source frames are 960x540.
- The GIF encoder treats a pixel as unchanged when its colour moved by less than about 20-30 levels; this is what keeps the files small. The palette is a general median cut plus 72 colours cut from the most saturated pixels, so lime, amber and police red/blue survive. Some glows band slightly as a result. Frames rendered in Godot will not have this.
