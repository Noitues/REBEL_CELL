# W7 city — frame time (ART_BIBLE §13)

Machine: Windows 10, 6 cores, RX 6700 XT, Vulkan Forward+. Window **1920×1080** (the 720p canvas
stretched 1.5×), vsync off, through `tools/run_windowed.py` with a private APPDATA.
Tool: `tools/design_lab/city_perf.gd` (new): loads the scene, waits until every city bake has
landed and 120 more frames, then times 900 frames. `--legacy` switches the W7 layer off in the same
build (the "before"); `--tier=N` picks the quality tier. Runs were interleaved (legacy, tier 2,
tier 1, tier 0 per scene, per round) because other work on this machine moved single runs by
±30 %. Numbers are the median of the rounds.

Scenes: **title** (`title_scene.tscn`, the panning menu), **grid** (`hq_scene.tscn --demo-grid`),
**combat** (`combat_scene.tscn`, the demo fight).

## Final build (2 interleaved rounds, after the per-pixel ink match was reduced to one per pixel)

| Scene | Before (legacy) frame / GPU | W7 tier 2 (default) | W7 tier 1 | W7 tier 0 |
|---|---|---|---|---|
| title | 1.54 ms / 0.63 ms | 1.90 ms / 0.95 ms | 1.99 / 0.92 | 1.95 / 0.80 |
| grid | 4.06 ms / 1.32 ms | 4.94 ms / 2.13 ms | 4.43 / 1.93 | 5.03 / 1.75 |
| combat | 1.72 ms / 0.83 ms | 1.93 ms / 1.04 ms | 1.82 / 0.99 | 2.01 / 1.04 |

A first run of three rounds (before that shader change) gave the same picture: legacy frame 1.68 /
4.45 / 1.93 ms, tier 2 2.33 / 5.37 / 2.24 ms, GPU +0.64 / +1.09 / +0.38 ms.

## Reading

- **60 fps at 1080p: met with a wide margin** on every scene (worst: grid 4.9 ms ≈ 200 fps).
- **Relative regression.** The frame time tracks the GPU time on this machine (the frames
  serialise), and the GPU cost of the lit composite is **+0.2 to +0.8 ms** at 1080p. Against these
  very light scenes that is **+12 % (combat), +23 % (title), +22 % (grid)** in frame time, so the
  15 % rule is exceeded on title and grid in relative terms.
- **Quality tier added** (as the brief asks): `CityAtmosphere.quality` / `city_look.tres`
  `quality_glow_taps` = 0 / 6 / 12 glow taps; tier 0 also turns the wet-street reflections off.
  Tier 0 removes about half of the GPU cost on the grid (2.13 → 1.75 ms); the rest is the haze,
  the grade and the extra layers (billboards, turf, life), which every tier keeps.
- **CPU:** the atmosphere's own work is ~0.13 ms a frame for two cities (profiled: process 63 µs
  per city, life draw 57 µs). The billboards (CorpPattern fills) were 1.5–3 ms a frame until they
  moved to a layer that redraws only when a board changes frame (every 3 s) or the camera moves.
  The title's pan pushes only the screen-space uniforms each frame.
- **Not measured:** the Steam Deck (§13's "60 fps locked on Steam Deck"). The Deck's GPU is roughly
  4–5× slower than this one: the grid's +0.8 ms would be ~3–4 ms of a 16.7 ms frame. Recommendation:
  default the Deck to tier 1 (W9's device probe already detects it; one line in Settings'
  first-run defaults, W9's file).

Raw logs: the rounds' outputs are summarised above; `city_perf.gd` prints one line per run.
