# Round 12: MODEM shop facade (shop screen backdrop)

A fixed exterior street view that sits behind the MODEM shop UI. One camera, one layout, three facade
designs, three lighting states each. Style is locked: Cv2 gritty triangulated low-poly with E cel
shading (banded toon light, wobbly ink lines), glowing street, neon spill on nearby facets, rain/haze.

## Composition (1920x1080, all options share it; v2 after review)

Reference: ref6 panel 05 "MODEM CYBER SHOP", rendered in our style.

```
 x:0     240      520   800                        1510        1920
   +------+--------+-----+--------------------------+-----------+
   | M    | shop   |alley|  city depth: towers, lit windows,    |
   | O    | tower  | ^ / |  holo billboard, haze (calm)         |
   | D    | fire   |stair|------ shop wing / back row ----------|
   | E    | escape | |   |  FRONT BUILDING (smaller): shutters, | lamp
   | M    |        | |   |  posters, AC, pipes, holo ad, ledge  |
   | CYBER|        |steam|  lights, roof clutter                |
   +--FOYER: screens, door, figure --+------------------------------+
   |  wet pavement + kerb, long sign reflections on asphalt         |
   +----------------------------------------------------------------+
```

- **Camera**: eye 6 m across the street, 24 mm, no pitch (verticals stay vertical). The lens shift
  puts the vanishing point down the alley (x ~636) and keeps the sign plate at x 52-212, y 26-688.
- **Shop tower** (left) carries the vertical MODEM sign (round 4 `sign_rgba.png`, used as-is). The
  **foyer** is a recess beneath it: cyan display screens, a lit door, a soffit light, an optional
  figure.
- **Alley**: a narrow passage straight ahead between the tower and the front building. A lit stair
  rises away and turns right behind the front building, with a door light, cables, glyph signs,
  steam and puddles.
- **Front building** (smaller, right): covers the shop's low wing. Its alley wall takes the sign spill.
- **Street**: wet asphalt and a kerb in the foreground, with long reflections of the sign.
- **Calm space**: centre/right (x ~840-1890, y ~60-1000) is the front building face, the back row and
  the hazed city: darker, simpler mid-values, still detailed. No baked UI, no readable text other
  than the sign, no paper stickers.

## Facade options

| | Shop building | Front building | Alley |
|---|---|---|---|
| **F1 Tenement** | narrow concrete-brick tenement, window grid, zig-zag fire escape, AC units, drain pipes; shop glass + half-raised grille | two-storey noodle-bar block, closed roll shutter, awning, dim glyph lightbox | metal stair up to the fire escape |
| **F2 Garage** | converted industrial garage: corrugated cladding, steel I-beam lintel, half-raised roll shutter showing a lit workshop, roof water tank | stacked shipping-container block | steel ramp-stair to a loading catwalk |
| **F3 Kiosk stack** | stacked container pods / market kiosks cantilevered off a concrete core, lit hatches, pipe bundles and cable runs, sign on a pipe scaffold | low market stall block with corrugated awning and pipes | stair between kiosk pods |

## Lighting states

- **RAIN**: overcast dusk, soft sky, wet reflective ground with puddles, rain streaks, haze. Sign at
  medium strength, pink spill readable.
- **DAY**: low hard sun from the right; the front building casts its shadow across the alley mouth,
  the pavement and the lower shop facade. Sign lit but subtle (no bloom halo), small damp patches only.
- **NIGHT**: sign is the key light: strong pink/cyan spill, coloured reflections in the wet street,
  lit windows, cold alley light, light drizzle.

## How it is made (concept)

Blender 5.2 headless (EEVEE) builds the geometry: every surface is a jittered, triangulated grid with a
per-triangle colour (`col` attribute), so the facets come from the mesh. One shared material
quantises the light (Shader to RGB, luminance banded into constant steps, hue kept) and adds `emit`
and a wet glossy layer; real lights and sun shadows give the spill and the day shadow. Extra aux
renders (object id, depth, normal) drive the post in Pillow+numpy: wobbly ink on silhouettes and
creases, depth haze, bloom, rain streaks and splashes, paint texture. All randomness is seeded.

## How it would be built in Godot

The backdrop is a static scene, so it ships as baked layers rather than live 3D:

1. **Parallax planes** (`Parallax2D` / `TextureRect`s, each a baked PNG with the cel+ink look):
   `far_haze` (skyline + sky), `shop_building` (with foyer and the alley interior), `front_building`.
   A tiny mouse/idle drift (2-6 px) separates them; nothing moves enough to fight the UI.
2. **Sign**: `sign_rgba.png` as its own `Sprite2D` (pivot per `sign_anchor.json`), plate opaque, glow
   drawn additively (`CanvasItemMaterial` blend add) or through 2D HDR glow. Flicker/warm-up via a
   small shader on a per-letter mask (round 4 `warmup_strip.png`); Reduce Effects = static lit frame.
3. **Spill**: one baked additive light texture per state (`spill_pink.png`, `spill_cyan.png`): the
   pink wash on facade, foyer and front wall, plus the street reflection streak. Drawn with blend add
   on top of the building layers; its alpha follows the sign's flicker so the street pulses with it.
   (`PointLight2D` with a texture is the alternative; the baked wash is cheaper and matches the art.)
4. **Rain**: `GPUParticles2D` (thin slanted streak texture, 2 depth layers with different speed and
   alpha) + a splash particle emitter on the foyer floor; a scrolling ripple texture on the wet floor.
   Off in DAY; light in NIGHT.
5. **States**: the three lighting states are three sets of baked layers (same layout), picked by the
   campaign clock/weather. Lit windows and the alley strip get a slow random blink (seeded).
6. UI panels sit on the calm area; a 30-40 % dark scrim behind them is enough, no blur needed.
