# Round 20: combat FX fixes, Heat H1 polish, batch 2

**Base:** the locked D4 combat screen (no NEXT arrows), as in round 19. The round 19 scripts were copied here; earlier rounds are untouched. All the new code is in `scripts/fx_r20.py`.

## Files
| File | What it is |
|---|---|
| `fx_corrupt_tick_v2.gif` | The CORRUPTED tick with its new on-slice animation; the RAM and HP parts are unchanged. |
| `fx_evade_v2.gif` | Evade v2: the token flies off and the attack chases it. |
| `heat_city_v2.gif` + `heat_city_v2_strip.png` | Heat H1 "city reacts", with a stronger NOTICED band. |
| `fx_nudge_resist.gif`, `fx_respin.gif`, `fx_corrupt_apply.gif`, `fx_drone_destroyed.gif`, `fx_phase_change.gif`, `fx_ram_gain.gif` + `fx_batch2_storyboard.png` | Batch 2. |

## 1. CORRUPTED tick v2
- The standing tear bars are fixed rectangles clipped to the slice. The diamond badge stays.
- **On resolve (300–640 ms):** a thin bright scan line sweeps **left to right** across the slice.
  - Behind it, every bar is cut into 10 px cells. Each cell becomes a pink 0/1 glyph (white-hot, 60 ms hold).
  - The bits then run round the outside of the rim into the HP arc: −3.
  - There is no spasm and no pixel tear.
- **The RAM part is unchanged:** a violet bolt hits the RAM meter, a pip cracks, and `-1 RAM` shows.
- **1500–1800 ms:** the tears write back on, left to right. The status persists until cleansed, so the slice reads as still CORRUPTED.
- **Godot:** in the slice overlay shader, add a `wipe_x` uniform (0 to 1 across the slice bounding box) and discard bars where `x < wipe_x`. The bits are a `GPUParticles2D` with `emission_points` sampled from the bar cells. Each point's spawn delay is proportional to its x, set through `lifetime_randomness` and a custom process shader.

## 2. Evade v2
- PROXY resolves and the green `>>` token sticker slaps onto the rim. The incoming attack is the same comet as the damage hits.
- At the moment of impact (1000 ms):
  1. The token **lifts** (×1.2, shadow grows) and flies to the **top-left** along a Bézier: 770 ms, ease-in (t^1.25).
  2. The attack's head **bends off the wheel and chases** the token, 170 ms behind it. It sheds a few orange bits on the way.
- Both fade normally as they near the screen edge (alpha = distance to edge / 170 px).
- `EVADED` slaps beside the wheel.
- There is no side-step and no after-images; the wheel never moves.
- **Godot:** the token is a `Sprite2D` on a `Path2D` (or a tweened Bézier). The attack head is a `Line2D` comet whose target the script switches from the pointer to `token.global_position` with a 170 ms delay buffer. Modulate alpha is derived from the distance to the viewport rect.

## 3. Heat H1 v2 (backdrop only)
| Band | Police lights | Pulse | Searchlights | Helicopters | Siren wash* |
|---|---|---|---|---|---|
| NOTICED 25–49 | 9 (was 5) | 0.82 s | **1** (was 0) | – | 5 % |
| FLAGGED 50–74 | 13 | 0.65 s | 2 | – | 8 % |
| HUNTED 75+ | 18 | 0.48 s | 3 | 2 | 11 % |

\* The siren wash is a faint red/blue tint that alternates over the city backdrop only, never over the HUD or wheels.

- NOTICED now has its own searchlight sweeping the target building, plus brighter, bigger street lights with visible light-bar cores. The first band therefore reads at a glance.
- **Godot:** the backdrop `HeatCity` node. Band values belong in `campaign_config.tres`.
- **Reduce motion:** no pulsing and no sweep; the counts stay.

## 4. Batch 2
Picked from `effects_list.md`: the P1 items not yet animated, plus the most-seen P2s.

| Effect | Beats | Tier |
|---|---|---|
| **Nudge + resistance absorb** | 1. The free E press: the boss strains 3° and springs back. 2. The `RESIST 1` chip cracks into grey bits: `ABSORBED 0 TICKS`. 3. A second, paid press: a 12° step (out-back 1.8), plus a yellow 1-tick notch on the telemetry ring. | T1 |
| **Respin** | 1. The RESPIN button flashes and 4 RAM pips crack into cyan bits that stream into the hub. 2. A hub kick, then the wheel spins 876° (2 turns + 13 ticks) ease-out with blur by speed. 3. A landing ring on the blade window, and the `CHECKPOINT` vinyl slaps on. | T2 |
| **Apply CORRUPTED** | 1. Pink bits arc from the CORRUPT PACKET card to the slice under the needle. 2. A white flash. 3. Tear bars **write on left to right** (the mirror of the tick's wipe). 4. The diamond badge slaps on, and a rule chip appears. | T2 |
| **Drone destroyed** | 1. A shot aimed at the needle bends to the docked drone (bodyguard). 2. Flash, a 3 px shake, cracks grow, and an `HP 0` chip. 3. The hex splits into 6 with a shockwave and 34 big orange 0/1; the clamp springs open. 4. The pieces pixelate and fall, with `DRONE DESTROYED`. | T2 |
| **Boss phase change** | 1. HP crosses 66 %: a 120 ms hit-stop, a white flash, and the phase pip rings. 2. The banner flips (scale-y through 0) to PHASE 2. 3. Orange bits pour to the bezel, a crowned **second needle** extrudes at tick 15 with its value chip, the `PHASE 2` vinyl slaps on, and a rule chip shows. | T3 |
| **RAM gain** | 1. At turn start the class core pulses. 2. 16 cyan 0/1 swing down into the RAM meter, 4 per pip. 3. Each pip flashes as its bits land. 4. The plate glows once and `+4 RAM` rises. | T1 |

- **Full-screen readability:** glyph bursts in batch 2 are 22–38 px (batch 1 used 16–24). The drone and heal effects now use 24–34 px glyphs and more of them.
- **Reduce effects:** no streams, bursts or blur. Wheels step to their end rotation in one 120 ms tween. Chips, badges and needles appear with a 1-frame outline.

## Weakest parts / open
- **The phase-2 needle is drawn as an overlay**, not by the frame renderer (D4 draws one blade). In game it is just a second blade instance at `pointers[1]`. Its value chip sits beside it so it clears the boss HP number.
- **Respin uses a rotated copy of the wheel** during the fastest frames, so the glyphs turn too; the blur hides it. Real upright renders take over below 7°/frame.
- **Heat FLAGGED and HUNTED both have searchlights now.** They are told apart by count, pulse rate and the helicopters.

## Build
Run from `scripts/`:
- `python plates.py warm`
- `python fx_r20.py corrupt_tick_v2 evade_v2 heat batch2`

The render cache goes in `scratch/`, which is git-ignored and cleared.
