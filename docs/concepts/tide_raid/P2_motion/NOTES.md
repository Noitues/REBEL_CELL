# Tide raid, polish iteration 2: motion on the P2 base ("Jack-in over the Night City", depth and camera)

Role: motion design. Scope: art only. Everything is rebuilt on the shared P2 base (`D:/rc_scratch/tide_concepts/p2_base/`, STYLE_CONTRACT.md): the graded city,
the occluder mask, the depth pass and the pre-rendered head rotations. Nothing in P1_*, P2_plates or P2_interact was touched, nothing is committed.

## What is here
| what | where |
|---|---|
| 6 motion tests, each normal + reduce-motion, **1280x720 30 fps MP4**, **640 px 30 fps GIF**, 12-frame contact strip, flash/shake metrics JSON | `tests/{daemon,lock,home,bloom,jack,shield}_{normal,reduce}.mp4/.gif/_sheet.png`, `tests/metrics_*.json` |
| 12 storyboards (frame strip + Gantt + beat table), rebuilt on the P2 look and heads | `boards/board_01_jackin.png` ... `board_12_jackout.png` |
| timing table and paste-ready `tide_look` block (daemon frames updated, camera/depth/new-test keys added) | `TIMING_TABLE.md`, `tide_look_motion.tres.txt` |
| source | `scripts/` (`m2.py` engine, `scenes.py` / `scenes2.py` the six tests, `boardscenes.py` the other board beats, `render.py`, `boards2.py`, `spec2.py`, `table2.py`) |

| test | frames | what it shows (normal / reduce are frame-aligned: same length, same impact frame) |
|---|---|---|
| `daemon` | 150 f (5.0 s) | 30 f telegraph hold with a slow push-in (zoom 1.00 to 1.06) and sideways parallax, 4 f coil, 38 f travel of the D worm along K1 to the HOLDS stop block, impact at **f72**, 78 f of hold and aftermath. Dread shadow ahead of every head, plum creep at the HQ, SITES LOST ink ring, HOLDS bars, HOME white ring with tick gauge. |
| `lock` | 120 f | three lavender fog corridors, the camera dollies in to 1.55x so the lock opens at reading size, rattle, shackle, letter to pixels, E silhouette pop (the real E head), fog clears, the E road is drawn out of the corp, camera pulls back to 1.14x. B and C stay sealed. |
| `home` | 130 f | 30+ f telegraph (6 preview ticks amber), push-in, 6 f decel of the N claw, 2 f white flash, **3 px shake (4 f, only here)**, two ground rings, fracture star, 6 ticks thrown off the gauge, 8 f hit hold, DAMAGED tile and -6, scorch mark, tallies, cracked ring, 30+ f aftermath. |
| `bloom` | 130 f | DOWN rings drain, plum seed, ten 5 f steps (radii 40 to 208 px), the hot hairline **pulses on every step**, windows die behind the front (emissive layer is subtracted), the two Sites become SITES LOST (ink ring + tile) and stumps, HQ pressure creep behind. |
| `jack` (new) | 96 f | pre-jack "plain map" grade (desaturated, lifted, no glow, no towers, no HUD) held 10 f; jack-in from HOME: radial grade with a lit front (10 f), pads, ranked towers (1 f stagger, 6 f rise), cage ignites, HUD and hand slide in; **dolly 1.14x to 1.00x with 26 px parallax** over 26 f; hold; jack-out at f62 (6 f un-grade). |
| `shield` (new) | 90 f | close-up (zoom 1.7 to 1.95) of the D head hitting the HOLDS block: white flash f0-1, hex wall flash, two ripples, 38 thrown bits (hex, triangle, rect), 8 f hold, pip 3 to 2, head redrawn above the flash with a 3 px ink halo. |

## What changed against iteration 1 (the CRITIC_P1 punch list)
- **One look.** Motion now uses the P2 graded city, the H6 heads (worm / refined claw / mine, oriented by the route tangent from the pre-rendered 22.5 degree rotations, blended
  between neighbours so corners never snap), the contract palette (DAMAGED FF9A00, SITES LOST = ink-black ring with white rim and ochre hatch, UNTOUCHED / HOLDS / BREACHED), the P2 ribbon textures
  (D chevron tile, N helix, E hazard chevrons, with the ink casing), ranked towers (five bright, the rest quiet), mint cage, HOME ring r22 BU with the 50-tick gauge, hex tiles with tier glyphs,
  and the HUD / hand cards of the plates.
- **Depth and camera.** Beams and heads are occluded by the occluder mask; the occluded part is drawn as a ghost pass (dashed x-ray core at 0.8 gain) and the city under it darkens 22 %.
  A depth-aware camera warp (zoom + pan + parallax proportional to `0.5 - depth`) gives a push-in on the telegraph, a lock dolly, a HOME push-in and the jack-in dolly. The only shake is still the 3 px HOME jolt.
- **Pressure layers**: dread shadow (45 % dark corridor, 220 px ahead of each head, tapering), plum creep from the cage base, draining ring on DOWN Sites.
- **Fixed iteration-1 weak points**: (1) normal and reduce variants are frame-aligned in every test (same frame count, same impact frame). (2) The Bloom hairline pulses per step. (3) The HOME-hit burst keeps
  its non-hue cues (fracture star, thrown ticks, bits) in reduce-motion (they fade in at their end positions, no travel). (4) The lock is shown at reading size (dolly) and the "plain map" before jack-in is now a defined grade (`plain_grade_sat`).
- **Two new tests**: jack-in / jack-out grade shift and the shield flash with bits.
- **Boards**: all 12 re-rendered on the P2 look. Daemon board and table updated to the new timeline (impact f72, 150 f).

## Measured (rendered videos, `tests/metrics_*.json`)
`max_dlum` = largest frame-to-frame change of mean luminance (flash proxy; 0.10 or more would be a general-flash candidate). `max_big_frac` is the largest fraction of pixels that change by more than 25 %; **with a moving camera
this number is inflated by camera motion and parallax, not by flashes**, and `max_shift_px` likewise counts camera moves (4 px steps; the HOME jolt itself is 6 px frame to frame). The honest flash read is `max_dlum` and `lum_jumps_gt10pct`.

| test | normal max_dlum / jumps >10 % / max shift | reduce max_dlum / jumps / shift |
|---|---|---|
| daemon | 0.033 / 0 / 4 px (camera) | 0.003 / 0 / 0 |
| lock | 0.003 / 0 / 12 px (dolly) | 0.001 / 0 / 0 |
| home | 0.070 / 0 / 8 px (jolt + push-in) | 0.010 / 0 / 0 |
| bloom | 0.002 / 0 / 0 | 0.009 / 0 / 0 |
| jack | 0.030 / 0 / 8 px (dolly) | 0.013 / 0 / 0 |
| shield | **0.111 / 1 / 4 px** (one flash frame, the contact) | 0.010 / 0 / 0 |

Reduce-motion removes every camera move, shake, jitter, fringe and scanline, and replaces every flash with one 3 f step at alpha .30. The one normal-variant flash above 10 % is the shield contact frame (white at .95);
it is a single frame well inside the 3-flashes-per-second limit.

## Honest Motion score against the bar of 9: **8.5 (a half point short, not a beat)**
Why it moved up from 8: the pixels now match the plates' look (same city, heads, palette, textures), there is real depth behaviour (occlusion with a ghost pass, parallax that follows the depth pass, dolly and push-in),
the pressure layers move, the hairline pulses, and the reduce variants are A/B-able frame for frame. The timing language (held impact, asymmetric in/out, one telegraph that waits, skip codes, reduce rules) was already
the strongest part and is unchanged.
Why not 9: (1) it is still a 2D composite with a depth-warped camera, not a real 3D camera: parallax stretches roofs at the edges (no disocclusion fill), beams are ground-plane strips and do not respond to light.
(2) The frames are visibly less luminous and less "bloomed" than the P2 plates (see the weak points); a critic comparing a video frame to plate 02 will see the plate as richer. (3) Nothing was seen in the engine, no audio.
(4) The head at the contract's 44 px is 29 px in the 1280 video; it reads, but it is the smallest important thing on screen.

## Consistency with P2
Same city image (`city_default.png`, so grade, hero light, wet reflections and signage are identical), same occluder mask for beams and heads, same ribbon textures and the contract's pattern per tier, same ring / block / tile specs
(radii, band 2.8 BU, ink under-stroke 1.3 BU, white rim .45 BU, chamfered 13.5 x 10 BU block), same ranked towers (heights 27/35/44 BU, five bright), same HOME spec (white ring r22, 50 ticks at r19, major every 10th),
same layer order (ground marks, ghost, beams, towers, effects, heads, tags, HUD, finishing), heads above beams and below tags, head redrawn above the flash with a 3 px ink halo at peak. Deliberate approximations:
marks are drawn in 2D on the ground plane (affine of the raid camera), not rendered in Blender, so rim light and AO on towers and blocks are simpler than the plates; the cage is a wire cylinder, not the plate's glass volume.
The P2 plates were still being written while this was built (only 01 to 04 existed); frames were compared against `02_forecast` and the glow/exposure was raised after the first full render to close most of the gap.

## Weak points (honest)
- **Luminance and bloom gap to the plates.** Even after one correction pass the video frames are about one stop flatter than the plates: no per-light bloom columns, no rain streaks near lights, a weaker HOME glow and cage. A Godot capture would close it.
- **Parallax is a pixel warp.** Roofs smear at the frame edge under the larger dolly (lock 1.55x, shield close-up); there is no disocclusion fill. Kept small outside those two tests.
- **Ground-plane approximation.** Everything is placed with the affine ground map of the raid camera and ignores terrain height; a few Site marks sit a pixel or two off the plate's Blender-projected positions.
- **Beams are dashed where the city occludes them.** The route threads between towers, so on a dense frame a long part of K1 is a ghost dash; it is correct to the occluder mask but busy. The ghost core at 0.8 gain is a judgement call (the contract does not say how it looks).
- **Heads are small** (44 px at 1920, 29 px in the 720p video). I kept the contract size; 1.3x would read better and is a one-line change (`head(... scale=1.3)`).
- **Loop cross-fade.** The 9 f cross-fade into frame 0 (kept from iteration 1) double-exposes the camera position at the end of every GIF; the MP4s carry the same fade. `jack` needs none.
- **Metrics conflate camera moves with flashes** (see above); the shake proxy cannot tell a jolt from a dolly.
- **Board beats 02, 03, 06, 09, 11 are illustrative.** The card draw, drag, hunter reticle, poster and city-lost frames are new P2-look renderers, not motion-tested videos. The poster is wordless (heart-break glyph + tallies), which changes board 09 from iteration 1 (that one had a word).
- **Sound** is still written, not authored.
- Process slips (rule: no `python -`): I once ran a bare `python -` (stopped through TaskStop, my own task) and once a `python -` with an empty heredoc (exited at once). No stray process remains. No wildcard deletes; frame clean-up used
  `scripts/del_frames.py` with exact names.

## Build notes
- Everything in `TIMING_TABLE.md` still maps to `tide_look`; new keys are `cam_*`, `jackin_dolly_zoom`, `jackin_parallax_px`, `plain_grade_sat`, `shield_hold_f`, `bloom_step_f`, `bloom_step_hairline_boost`.
- Godot needs: a depth-aware camera move (zoom + dolly + parallax from the depth buffer, free in a real 3D camera), a global grade parameter for the plain map, the occluder pass with a ghost x-ray and the 22 % corridor darkening, a per-step hairline pulse
  on the Bloom shell, a head sprite oriented by the route tangent (16 rotations or a quaternion), and the reduce-motion switch routing camera moves to a static framing.

## Re-render
`cd scripts`; `python render.py all` (frames cached in `D:/rc_scratch/tide_concepts/p2m_work/frames`, 5 processes, about 35 min, then MP4/GIF/sheets/metrics), `python boards2.py [slug ...]`, `python table2.py`.
Needs numpy, scipy, Pillow, the P2 base, the P2 textures and the iteration-1 H2/P1 scripts (read-only: `tl.py`, `lib.py`).
