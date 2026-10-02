# Round 19: combat FX v2 (preview + slap, dissolves, effects batch 1, Heat alternatives)

**Base:** the locked D4 combat screen, with the standing NEXT arrows stripped from the boss threat ring. The only change is `frames.py` line 967, `telegraph=()`. Earlier rounds are untouched; their scripts were copied here.

## Files
| File | What it is |
|---|---|
| `card_play_v2.gif` + `_storyboard.png` | Hover HEAVY SPIN. The **card-play preview** plays (the round 17 rule: one chevron chase from the top needle, then a ghost blade and a dashed slice at the landing). Then peel, aim, slap, dissolve A, and the spin. The ghost is parented to the slice disc, so it reaches the real blade exactly as the wheel lands: **LANDED = PREVIEW**. |
| `dissolve_A_bitstream.gif` / `_B_scanline.gif` / `_C_crumble.gif` | The same moment and the same 520×520 crop at 1:1, from 120 ms before the slap to 360 ms into the spin. A running `+ms` counter lets them be compared side by side. |
| `effects_list.md` | The full combat-effect inventory, by family, with a motion idea and a priority for each. |
| `fx_block_shield.gif`, `fx_heal.gif`, `fx_corrupt_tick.gif`, `fx_drone.gif`, `fx_evade.gif`, `fx_enemy_defeated.gif` + `fx_batch1_storyboard.png` | Batch 1, the six most important effects. |
| `heat_alternatives.png`, `heat_city.gif`, `heat_trace.gif` | Five Heat displays × 3 bands, and GIFs of the top two. |

## Dissolve A fix (the gold swirl at small size)
In round 18, three trail copies of 14–20 px glyphs plus a strong glow merged into a gold smear at 960 px. Round 19 changes:
- **Cells:** 13 → 17 px, so there are fewer glyphs (about 180 instead of about 300).
- **Glyph size:** 19–25 px, shrinking only to 10 px.
- **Trail:** one faint trail copy at 28 % instead of two.
- **Rim:** a dark rim at 95 % on every glyph.
- **Glow:** 0.55 → 0.35.
- **Timing:** release jitter of 110 ms and travel of 320–520 ms, so the glyphs arrive spread out.

At 960×540 the 0s and 1s now read as glyphs in the dissolve GIF. In the full-screen GIF they are still small but distinct. **A is still the recommendation.**

## Card-play preview in the sticker flow
| t (ms) | Beat |
|---|---|
| 560 | Hover. |
| 900–1500 | Chevron chase (9 chevrons, 46 px, outside the rim, anticlockwise from needle 1). |
| 1400–1600 | The ghost blade fades in; the landing slice is dashed in its program colour. The ghost's window shows the value it will read (14) and an index tab (1). |
| 1560 → press | Labels (`1 LANDS HERE`, `SPIN 9: …`) show only while the card waits. |
| 1700 | Press. The labels go, but the preview holds (chevrons at 50 %) through the peel, the drag and the slap. |
| spin | The chevrons fade in 200 ms. The ghost rides the slices and meets the blade at the landing, where a white ring and a `LANDED = PREVIEW` tag appear. The ghost then fades out (260 ms). |

**Godot:** the `PreviewOverlay` from round 17 (chevron sprites with a staggered modulate tween; dashed ghost sprites). It is shown on card hover and aim, and the forecast drives it. When the play commits, re-parent the ghost to the wheel's rotating `Slices` node. Ghost and landing then can't disagree (the preview must equal the result).

## Batch 1: build and timings
All use 0/1 glyphs from the round 18 atlas in the source slice's colour, vinyl stickers for words and objects, and additive glow. Every effect is VfxTier T2 except enemy defeated, which is T3.

### Block and shield (2.7 s)
- **Block:**
  - The FIREWALL slice flashes (120 ms).
  - 16 cyan glyphs fly to the rim facing the enemy.
  - 17 bricks pop in (1.3→1, out-back, 28 ms apart), crenels last, and a `BLOCK 5` chip appears at HP.
  - The wall settles to 60 % with a 1.2 s shimmer loop.
- **Shield:**
  - A hub pulse.
  - 13 hex plates tile out from the middle (45 ms apart), then a white ripple runs across them.
  - A `SHIELD 4` chip.
- **Godot:** bricks and hexes are pooled `Polygon2D`s (or one atlas), tweened in by index. The stream is a `GPUParticles2D` with `emission_points` and a Bézier process shader (the same shader as dissolve A).

### Heal (1.9 s)
- A green well rises under the segments that will return (300 ms), with an outline of each segment.
- 16 `+`/`1`/`0` glyphs rise in from outside, below the wheel.
- Each segment flashes white→green when its 4 glyphs arrive.
- `+8` pops and flies to HP (27 → 35).
- **Godot:** the same emitter. The arc segment flash is the existing `hit_flash` in green.

### CORRUPTED tick (1.9 s)
There is no poison/DoT in the game; this is its tick.
- The standing overlay is violet tear bands plus the diamond badge.
- On resolve: a white flash, the tears spasm, and a 160 ms pixel tear.
- Violet bits run **around the rim**, never across the face, into the HP arc: −3, with a `CORRUPTED` chip.
- A violet bolt hits the RAM meter, and the 5th pip cracks into 0/1: −1 RAM.
- **Godot:** the slice shader's `tear_amount` uniform for the spasm, plus 2 emitters and a `Line2D` tracer.

### Drone (2.9 s)
- **Deploy:**
  - A hub pulse.
  - 26 orange glyphs stream to the dock point and pack into a hex outline.
  - The drone sticker slaps on (×1.35 → squash 1.12/0.88), and a clamp line locks it to the bezel. An `HP 5` chip.
- **Attack:**
  - The lens ring charges for 300 ms.
  - A mini tracer to your pointer slice, S-tier shards, −3, and an 8 px recoil.
- **Godot:** the drone is a `Sprite2D` sticker child of the rotating slice node (it rides the wheel). The attack reuses the damage-shard emitter at tier S.
- Drone destroyed (P1, not in this batch): the hex cracks and pops into 0/1, and the clamp springs open.

### Evade (2.3 s)
- PROXY resolves, and green `>`/`0`/`1` glyphs form a `>>` token sticker on the rim, with an `EVADE 1` chip.
- The hit flies in.
- The wheel side-steps 34 px in 80 ms, leaving cyan and magenta after-images (16 % and 12 %).
- The tracer passes through and fizzles into grey bits.
- The token peels off and flies away, `EVADED` slaps on, and the wheel eases back (300 ms).
- **Godot:** the wheel root's `position` tween. The after-images are two `CanvasGroup` copies modulated cyan and magenta, fading. The token uses the peel shader.

### Enemy defeated (2.7 s, T3)
- Lethal crit (−24, `LETHAL`), a 120 ms hit-stop and a 4 px shake.
- White cracks grow along every slice seam (500 ms), then the whole wheel flashes.
- The render is cut into its 6 slices, the hub, 8 ring chunks and the banner. They fly apart (radial plus up, gravity 900 px/s², spinning), pixelate as they fall (NEAREST downscale 1→10) and shed 0/1 in their own colours.
- A hub shockwave ring.
- `DELETED` slaps on, and HP reads `0/400` in grey.
- **Godot:** cut the pieces with `Polygon2D` UVs over a `ViewportTexture` of the wheel (one viewport snapshot at death), then tween each piece. The pixelation is a `pixel_size` uniform. Each piece gets a one-shot emitter.

**Reduced** (reduce effects, for all six): no streams, bursts, after-images or pieces. Chips and numbers are set at once. Walls, hexes, drones and badges appear with a 1-frame outline. Defeated is a 300 ms fade to grey plus the `DELETED` sticker.

## Heat alternatives (`heat_alternatives.png`)
| Option | What | Intrusion | Obvious? |
|---|---|---|---|
| **H1 City reacts** | **Backdrop only.** Police red/blue light spill on the streets: 5, 8, then 12 sources, pulsing faster per band. Searchlights sweep the target building (0, 1, then 2). Helicopter silhouettes with blinking beacons appear at HUNTED. | none: behind the wheels | high at FLAGGED and HUNTED; NOTICED is mild |
| H2 Frame gauge | A thermometer arc on the player wheel's left frame with 25/50/75 ticks, plus a warm glow on the bezel. | low | medium: small, reads up close |
| H3 Telemetry warnings | Your telemetry ring turns into a heat-coloured `TRACE n% // BAND //` band (60°, 110°, then 170°); it blinks at HUNTED. | low–medium: it takes over the ring's slice telemetry | high |
| H4 Siren spill | Red (left) and blue (right) light pulses in from the screen edges (period 1.4, 0.9, then 0.55 s). | low | medium; tiring if overdone |
| H5 Trace line | A heat-coloured line runs round the screen border, clockwise from top centre. Its length is the Heat value, with 25/50/75 marks and a pulsing head. | very low | medium: it reads as a meter, not a mood |

**Recommendation:** **H1 City reacts**, with **H5** as its quiet numeric twin on the border.
- H1 is diegetic (the city is hunting the Cell, matching the HQ window's searchlights in art_asset C2). It is obvious at a glance and can never cover a value, because it lives on the backdrop layer behind the wheels' darkened pools.
- The round 18 screen glitch stays as an **Options extra** (off by default, or set to a "spicy" preset).
- **Godot:** H1 is a backdrop `Node2D`:
  - light-spill sprites (additive, `modulate` tween per band);
  - searchlight cones (additive `Polygon2D` with a soft gradient texture, rotation tween);
  - helicopters (`Sprite2D` on a path, with a blinking beacon).
  - Band counts and periods go in `campaign_config.tres`.
- **Reduce motion:** the lights stop pulsing, the searchlights hold still, and there are no helicopters.

## Weakest parts / open
- **H1 at NOTICED (25–49) is subtle.** Only a few street lights change. If a band change must read instantly, add a one-off "squad car arrives" beat when the Heat crosses a threshold.
- **Defeated:**
  - The pieces are cut on screen-space angles, so the banner and blade go as one chunk.
  - The dark backdrop pool remains where the wheel was. It reads as a hole, which works, but the pool should fade in-game.
- **Effects stage on the full screen:** the GIFs are crops of the full screen at 0.5–0.67 scale, so a few chips are small.
- **Round 18 bug, fixed here:** the tracer head lingered after impact in round 18's `damage_shards.gif` (a small white dot). This copy fixes it; round 18 itself is unchanged.

## Build (from `scripts/`)
- `python plates.py warm`
- `python card_play_v2.py`
- `python card_play_v2.py dissolves`
- `python effects_batch1.py`
- `python heat_alts.py`

The render cache goes in `scratch/r` (git-ignored). The output folder is about 30 MB.
