# Whole-city parity: port plan (Blender plate → Godot)

Sources read: `city_all_corps/scripts/terrain_a2.py`, `city_world_a2.py` (ground tiles, seabed, sea), `city_bay_a2.py`
(coast strip, islands, boats), `city_render.py` (`water_fade`, `mat_water_aaa`, `mat_fog`), `city_preset.py` (WATER, TERRAIN).

## How the plate makes its water

The plate has no stack of water layers. It uses one water plane at sea level, and one seabed mesh under it.
The depth feel comes from the materials of whatever sits under the plane.

1. **Seabed geometry.** `sea_depth(d)` is a 3 BU shelf at the shore. It drops on a smoothstep over cells 2–30 from the land
   to 170 BU offshore. Islands stand on shoal banks at −7 BU that slope out from 1.3 × their radius.
   - The seabed colour runs from sand (0.34, 0.31, 0.24) to rock (0.17, 0.19, 0.20) over cells 1–13 from the land.
2. **Clear-water fade** (`water_fade`, applied to every surface below sea level).
   - The light path is `path = d/|I.z| + d`: the view leg plus the light's down leg.
   - Transmittance is `T = exp(−σ·path)`, with σ = (0.090, 0.034, 0.016) per BU, so red dies first.
   - The surface colour becomes `colour·T`, plus `(1−T)·inscatter`, with inscatter = (0.003, 0.018, 0.055).
   - So water is clear near the surface. It fades to deep blue with depth and with grazing view angles.
3. **Caustics on the seabed.** Two ridge-noise layers: scale 0.05/BU and 1.6× that, ridge width 0.22, distortion 0.9.
   - A lit floor of 0.12 under them.
   - A slow patch mask so they drift in patches.
   - They fade as `exp(−d/30)` and only light up-facing faces.
   - They add cyan (0.22, 0.72, 0.78) × 1.1 as emission. This is the plate's turquoise marbling at night.
4. **Surface plane.** The plane is transparent.
   - Reflection: a Fresnel term (IOR 1.33, boosted 1.35× at grazing angles) mirrors the sky.
   - Normal: a broad swell plus a fine ripple.
   - By day it also adds a diffuse body going from deep (0.022, 0.15, 0.31) to shallow (0.09, 0.46, 0.50), with emission (0.01, 0.07, 0.14).
   - Opacity is 0.40 + 0.52 × shallow. The shallow mask is a baked image covering water within 28 cells of the land.
5. **Coast.** A smooth sand strip 3 BU wide and a faint surf line follow the plan's coast polyline. They hide the lot staircase.

## Godot port

Each step ends with a capture. The whole list ends with a blind review.

| # | Step | Godot |
|---|------|-------|
| A1 | Seabed depth profile and colours as in the plate (shelf, 170 BU deep, island shoals) | `CitySeabedKit.bed_z` and its colours |
| A2 | Clear-water fade and caustics on the seabed, in the opaque pass (no depth buffer) | new `city_seabed.gdshader` |
| A3 | Surface plane: Fresnel sky reflection, swell plus ripple, day diffuse body at 0.40 + 0.52 × shallow | `city_water_plane.gdshader` |
| A4 | Coast: smooth sand strip, surf line and animated surf band on the first shelf | coast mesh plus plane shader |
| B | Terrain numbers to match the plate (table below) | `campaign_config.tres` |
| C | Atmosphere: height haze (22 BU falloff), torn low banks, clear air over the bay, an upper sheet at 58 BU, day sun and sky gradient, night cloud deck | volumetric fog and FogVolume noise, sky |
| D | No empty blocks: the plate fills the outer suburbs with low blocks. The fill fades out from 5 to 34 cells past the outer ring, on flat, low ground | whole-pose fill |
| E | Buildings by day: weathering noise, glossy glass windows mirroring the sky, a lit-window share. By night: near-black with dense small warm windows | `city_building.gdshader` |
| F | Foliage: tree clumps on the forest and meadow land and on the parks | `CityVegetationKit` |

Terrain numbers for step B:

| Parameter | Plate | Godot now |
|---|---|---|
| Mountain height | 125 | 60 |
| Foothill height | 20 | 12 |
| Horizon ridge | 95–150 | 78–124 |
| Cliffs (outside the city) | 16 BU | none |

If the A steps don't hold up after two captures, fall back to the designer's stacked-plane method: 4–5 planes from sea level
down, each with its own tint, alpha and noise.
