# Binary damage shards: build notes (ART_FEEDBACK_R2 item 5)

Concept renders for the hit VFX. Each hit throws off 0/1 glyphs at the point of impact. The glyphs take the attacking slice's colour, tumble and fade, then **curve around the rim into the HP arc**, so the damage visibly arrives. The HP number drops per arrival, and the white lag segment drains after the last shard lands.

| File | Shows |
|---|---|
| `01_hit.gif` / `_strip.png` | −7: 17 glyphs, about 24 px, pink (attack slice) |
| `02_big_hit.gif` / `_strip.png` | −18: 33 glyphs, up to 34 px, wider and faster spray |
| `03_crit.gif` / `_strip.png` | −14: 7 code streaks (`0110 1001`) fly out on shattered-glass crack lines, then break into single glyphs that are sucked in |
| `04_blocked.gif` / `_strip.png` | −2 (5 soaked): a hex shield pops up and ripples. 22 dim glyphs bounce off, fall and die; 4 small ones get through to the bar |
| `05_heal.gif` / `_strip.png` | +6: green glyphs (a few `+`) stream in from outside, below the wheel, and converge on the refilling segments |
| `06_greyscale.png` | The peak frame of each variant in greyscale |
| `07_reduce_effects.png` | Reduce-effects end state: HP already set, a static chip, no particles, flash or shake |

Each GIF runs 3 pre-roll frames (the incoming hit line), then 18 effect frames (0.6 s at 30 fps), then a 10-frame hold. Every variant is seeded, so reruns match.

## Readability without colour
- **Hit / big hit:** an outward spray that curves back. The shard count and glyph size scale with the damage number.
- **Crit:** long straight **text streaks** radiating in a star, with crack lines. These are the only straight, velocity-aligned shapes.
- **Blocked:** **hex plates**, plus shards that reverse and fall away under gravity. Only a trickle reaches the bar.
- **Heal:** motion runs **inward, from outside**. No burst point, no flash, and a few upright `+` glyphs (the bible's rising plus-signs).
- A hot white core on fresh glyphs, which lasts 0.1 s, keeps the burst the brightest thing in greyscale.

## Godot 4.7 build
**Recommended node: `GPUParticles2D` with a glyph atlas, one emitter per hit, pooled in the FX layer.**
- **Atlas:** a 4×1 `CanvasTexture`/`AtlasTexture` with `0`, `1`, `+` and a blank cell, baked from the font at 2× the largest size (64 px cells).
  - Set `CanvasItemMaterial.particles_animation = true` with `h_frames = 4`.
  - Pick the glyph per particle with `anim_offset_min = 0` / `max = 1` and `anim_speed = 0`. Heal uses 3 cells, a hit uses 2 (limit the frame range through a custom `ParticleProcessMaterial` or two emitters).
- **Burst:**
  - `one_shot = true`, `explosiveness = 1.0`, `amount` = `shard_base + shard_per_dmg × dmg` (clamped).
  - `direction` = the rim normal at the hit, `spread` = 75° (100° for big hits).
  - `initial_velocity` 325–725 px/s, `damping` about 4.5/s, `gravity` (0, 260).
  - `angular_velocity` ±900°/s, `scale_min/max` from damage.
  - `color` = the slice colour, with a `color_ramp` alpha of 1 → 0.55.
- **Suck into the HP bar:** the stock attractors are 3D only (`GPUParticlesAttractor3D`), so use a small **particle process shader** instead.
  - After each particle's `attract_delay`, lerp `TRANSFORM[3].xy` along a quadratic Bézier. The control point sits on the rim-side angle bisector at 1.5 × R_out, so shards go **around** the wheel and never across its face.
  - The shader gets the target segment's arc position as a uniform (spread over the drained segments by `INDEX`).
  - Use ease-in cubic, and scale 1 → 0.45 on arrival.
  - The CPU fallback is `CPUParticles2D` plus a script that does the same per-particle lerp. It's fine for these small counts (≤ 40).
- **Arrival:** the view can't read GPU particles back, so it **precomputes arrival times** with the same formula (`delay + i/n × stagger + travel`).
  - It schedules the HP tick-down per arrival, the segment flash (the existing `hit_flash`) and the white lag drain (the existing trailing-segment entry).
  - The chip pops at the first arrival. The view never changes game state; the HP value shown is presentation only.
- **Crit:**
  - 7 `Label`/`Sprite2D` streaks, pooled, with velocity-aligned rotation, flying 0.17 s.
  - At break, spawn a second `GPUParticles2D` with `emission_points` from the streak character positions (`emission_shape = POINTS`), then run the same suck shader.
  - The crack lines are a `Line2D` fan fading over 6 frames.
- **Blocked:**
  - The hex shield is a `Polygon2D` cluster (or the existing shield hit shape), scaled 0.8 → 1 over 3 frames, with an outward ripple through `modulate`.
  - The bouncing shards are a separate emitter with no suck, gravity 450 and a lifetime of 0.3–0.45 s.
  - The pass-through emitter is 4 particles at size 15 px.
- **Glow:** additive `CanvasItemMaterial` (blend add) on the emitter, plus the existing HDR 2D glow. One additive pass is enough; two turn a dense big hit into a blob (seen in the renders).
- **Tier:**
  - `tier = T2_OUTCOME`: ≤ 0.6 s, local only, a flash ≤ 60% alpha on the hit point (a 2-frame white disc), a 1–2 px shake on the wheel only, and the existing 2-frame `hit_freeze`.
  - The burst stays inside the wheel plus 25% of its region.
  - A crit on a kill is T3 and keeps these shapes.
- **Flash limiter:** the impact disc and the segment flash request a slot from the global limiter (≤ 3/s). When it's denied, skip the flash but keep the particles.
  - The segment flash is batched per frame: several arrivals in one frame make one flash, not n.
- **Reduce effects:** don't instantiate emitters. Set the HP to its end value, show the static chip (`07_reduce_effects.png`), and use no shake and no flash. Colour and number carry the meaning.

## Glyph font
**Share Tech Mono** (already in `assets/fonts`, OFL). It's monospaced and technical, and its `0` and `1` stay distinct when rotated.
- It's a thin face, so bake the atlas with a **~1/22-size outline in the same colour** (`FontVariation` / `outline_size`) to thicken the strokes. The renders do this.
- Consolas is Windows-only and not redistributable. Use Anton only for the chip number, as the HP counter already does.

## Timings for `ui_motion.tres`
All are T2 unless noted. Amplitude units follow the entry doc.

| id | duration | delay | amplitude | notes |
|---|---|---|---|---|
| `hit_shards_burst` | 0.19 | 0.0 | 1.0 (radius multiplier) | Free flight before the suck starts |
| `hit_shards_stagger` | 0.10 | – | – | Spread of suck start across the shards (first → last) |
| `hit_shards_suck` | 0.19 | – | 0.45 (end scale) | Bézier into the arc, ease-in cubic |
| `hit_shards_fade` | 0.19 | 0.08 | 0.55 (alpha floor) | Tumble fade before the suck brightens them back to 0.95 |
| `hit_shards_core` | 0.10 | 0.0 | 1.0 | White core on fresh glyphs |
| `hit_crit_streak` | 0.17 | 0.0 | 7 (count) | Streak flight before shattering |
| `hit_crit_cracks` | 0.20 | 0.0 | 4 (px width) | Crack line fan |
| `hit_block_shield` | 0.60 | 0.0 | 0.9 (alpha) | Pop 0.1 s, hold to 45%, fade |
| `hit_block_through` | – | – | 0.2 (share) | The share of shards that reach the bar (4 of 22 in the render) |
| `heal_shards_inflow` | 0.29 | 0.0 | 0.24 (stagger s) | From outside to the bar, 0.26–0.32 s each |
| `hit_lag_drain` | 0.10 | 0.04 | – | White lag after the last arrival (may reuse the existing entry) |

The damage scaling numbers go in content config, not code:
- `shard_base` 8, `shard_per_dmg` 1.4, `shard_max` 40
- `glyph_px_base` 18, `glyph_px_per_dmg` 0.9, `glyph_px_max` 38 (1× px)

## Open questions for the designer
1. Should an enemy hitting the player use the enemy slice colour, so the same colour rule applies to both sides (slice colour = slice type)? The renders use the attack slice's pink.
2. Should the blocked shards that don't reach the bar land on the shield hex *number* instead (the shield visibly "eating" them)? That would reuse the same suck path.
3. The heal shards spawn off the wheel. Should they come from the **heal slice** that fired instead? That's more causal, but less "from outside".

## Scripts
- `scripts/bd_backdrop.py`: the Blender 5.2 headless city backdrop, seeded. It writes `backdrop.png`.
  - Gotcha: `scene.node_tree` no longer exists in 5.x, so compositor glare was skipped and the glow is done in Pillow.
- `scripts/bd_render.py`: all GIFs, strips, greyscale, reduce-effects and contact sheet, using Pillow only. Run `python bd_render.py backdrop.png`. It takes about 30 s.
- `scripts/bd_debug_frames.py`: dumps chosen full-size frames of one variant.
