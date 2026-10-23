# Raid target frames (concept art, not a build spec)

Three 1920x1080 frames of the sweep raid on one board and one camera, so they read as a sequence.
Rendered headless in Blender 5.2 (Eevee, 160 samples, about 10-17 s a frame), graded and
composited with Pillow. Regenerate: `python tools/raid_concepts/target/render_all.py`
(scripts in `tools/raid_concepts/target/`; seeded, output under D:/rc_tmp/raid_design_lab/target/).

The board (4x3, beams enter from the right): R1 asset 4, asset 8 GO DARK, DECOY, asset 8; R2 empty,
empty, asset 4, asset 8 GHOST; R3 empty, empty, asset 8, HOME. Beam 1 runs R1 and stops on the
decoy. Sealed candidates: R2 (square), R3 (circle), R1 from the left (triangle). The hunter turns
down column 4 at the node beam 1 touched.

1. `raid_target_1_plan.png` PLAN. Beam 1 loaded, three sealed shaped candidates dashed, the three
   levers placed (ghost, decoy, dark) and echoed in the kit tray, Heat at the 50 notch.
2. `raid_target_2_reveal.png` REVEAL. The square line ignites and its front races left; the
   circle and triangle are struck out. The spoof window is open: SKIP (marks its target node) and
   JAM (marks the hunter column), each +2 Heat, with a draining decide bar and a countdown ring.
3. `raid_target_3_impact.png` IMPACT. The hunter column blazes down to HOME, HOME flashes red and
   loses one integrity pip (-1), two assets are DOWN (wrench), and the HOME -1 / HOLDS stamp lands.

## Palette
| Role | Hex |
|---|---|
| Threat (beams, pylons, hunter, sealed lines) | `#3D6BFF`, hot core `#9FC0FF` |
| Cell and HOME (assets, links, rim, HOME) | `#FFD24D` gold, `#FFB020` amber, copper links `#C9741A` |
| Heat | `#FF6A1A` |
| Spoof key caps, skip target | `#D4FF00` (cell acid) |
| Damage (HOME -1, shattered pip) | `#FF3D4D` |
| Net (grid, skyline) | `#5CE1FF`, `#3A8FD0`; floor `#060A18`, slab `#0C1224` |
| Dead / dark node | greys `#8A92A6`, `#23252C` |

Fonts: Anton (numbers, stamp, headlines), Share Tech Mono (labels), IBM Plex Sans Condensed (chips).
Text is minimal US English. Sources: STYLE_GUIDE section 1 (the net is wireframe), section 2 tokens,
section 5.3 (raid reads: shot, hit, number; stamps; HOME -N, HOLDS in acid).
