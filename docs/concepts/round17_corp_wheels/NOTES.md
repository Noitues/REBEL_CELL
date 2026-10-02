# Round 17: animated card-play preview, corp palettes and slice fixes

This round builds on round 16 (`round16_corp_wheels`, which is untouched). It uses:
- round 16's glyphs (`round16_slice_system/scripts/glyphs16.py`, with SANDBOX set to option C);
- **tier V2 "strong"** for the corp tiers, redone in each corp's palette.

## Files
| File | What it shows |
|---|---|
| `preview.gif` | The animated card-play preview: 21 frames, about 3.5 MB. |
| `preview_storyboard.png` | Six labelled key frames of the preview. |
| `corp_<meridian/solace/halcyon/orbital/rebel_cell>.png` | Each corp sheet shows every slice type as a 4-frame strip with its loop described, the material, crest and accents, tiers I/II/III, and the regular (I), elite (II) and boss (III) wheels. |
| `motion_<corp>.gif` | All of a corp's slice animations looping: 12 frames, 0.5–0.9 MB. |
| `corps_compare.jpg` | The 5 bosses in phases 1/2/3, plus the 5-corp squint test (sharp and blurred). |
| `scripts/` | Build scripts (see Build below). |

**Build** (from `scripts/`):
- `python preview17.py` makes the preview GIF and storyboard.
- `python make_round17.py corp <corp>` makes one corp's sheet and GIF.
- `python make_round17.py compare` makes `corps_compare.jpg`.
- `python clear_cache.py all` clears the render cache.

**New this round:** `scenes17.py`, `kits17.py`, `preview17.py`, `patch_palette17.py` (a one-off palette patch, kept as a record), and the GIF inspection helpers `gif_frames.py` and `gif_crop.py`.

## Card-play preview (animated)
**Example:** The Civic Core (phase 2) with 2 needles, at ticks 0 and 20, and 1 docked Civic Drone. The player hovers HEAVY SPIN 9. A spin of 9 turns the slices 9 ticks clockwise, so:
- **Needle 1 (the top needle)** lands 9 ticks anticlockwise, right beside the real needle 2. This is the "lands next to another needle" case.
- **Needle 2** lands on the FIREWALL 12 slice.
- **The drone** rides its slice and ends 9 ticks clockwise, near the bottom right, far from where it started.

**The sequence:**
1. NOW: real needles and the drone, labelled.
2. The card is hovered.
3. The chevron chase: large ghosted chevrons outside the rim, from needle 1 to its landing. They light up in turn in the direction of travel.
4. The ghosts fade in: a ghost blade at each needle's landing, both identical with index tabs 1 and 2, and a dashed ghost drone where the drone ends up.
5. Hold, with labels: "1 LANDS HERE", "2 LANDS HERE", "DRONE ENDS HERE".
6. Hold, without labels.

**Rules shown:**
- There is only **one** directional set, the chevrons for the top needle. The other needles' and drones' movement is inferred from their ghosts.
- There are no white trace lines, no aim pips and no gates.

**Godot:** a `PreviewOverlay` driven by the forecast's landing ticks.
- The chevrons are `Sprite2D` instances along the arc, with a modulate tween offset per index to make the chase.
- Ghost blades and drones are dashed-outline sprites at the computed angles.

## Corps
- **Palettes.** I checked these with the squint test on `corps_compare.jpg`.
  - **Solace** moved to lime / leaf green (`#96FF46`) on dark leaf glass.
  - **Orbital** moved to ice white (`#CDF0FF`) with a pale steel bezel on near-black space.
  - **Halcyon** stays violet and amber.
  - Blurred, the five read as orange, lime, violet, pale white-grey and red.
- **Tiers** (V2 strong, in each corp's palette):

  | Tier | Border | Screen | Extra |
  |---|---|---|---|
  | I | primary | dimmed to about 60 % | none |
  | II | secondary | full | bright inset line |
  | III | primary | about 142 % gain | solid strip, heavy cross-hatch, secondary inset line |

  The kit rows are drawn at tier II, so the animations show at full brightness.
- **Solace.** GROWTH is now true mitosis: the nucleus divides, the round cell pinches at the waist, and two separate round cells part.
- **Meridian.**
  - CRIT: a parcel slides in, PRIORITY is stamped onto it, then it ships out.
  - DEFEND: the existing wall courses are offset by half a container, and the crane lays two new containers in a running bond.
  - JUDGEMENT: a courtroom gavel (a cylindrical head with two flat faces and brass bands, its handle entering the middle of the head) swings down. One face strikes the round sound block, with a flash and a shockwave.
  - MISS: the tape peels off, the box opens, then it shreds into strips and flecks and nothing is left. There is no EMPTY label.
- **Halcyon.** ATTACK is option B (the drone lock-on). SHIELD is reverted to the round 15 version (a thrown rock bounces off the riot shield).
- **Orbital and Rebel Cell:** the animations are unchanged.

## Weakest parts / open
- **The preview GIF is 3.5 MB**, close to the 4 MB limit, because it is 820 px wide with a city backdrop.
- **The gavel is small at sheet size;** it reads best in the GIF.
- **Orbital's pale bezel is brighter than the other corps' bezels.** If it competes with slice values, take its base down a step.
