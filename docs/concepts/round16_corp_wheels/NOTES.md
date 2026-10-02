# Round 16: corp wheels, after the round 15 review

This round builds on round 15 (`round15_corp_wheels`), which is left untouched. It uses:
- the locked D4 frame;
- round 15's final glyphs (`round15_slice_system/scripts/glyphs15.py`), so NULL is now 1/0;
- the round 15 "a" tier style (an inset line plus a filled, cross-hatched gap), redone in each corp's palette.

The slice agent's round 16 work is not repeated here: the glyph tweaks, the refined tier "a", the player FIREWALL screen and the SANDBOX glyph.

## Files
| File | What it shows |
|---|---|
| `preview_A2.png` | The card-play preview A2 (below). |
| `corp_<meridian/solace/halcyon/orbital/rebel_cell>.png` | Each corp sheet has: every slice type with 4 frames and a description of its loop; the material, crest and accents; slice tiers I, II and III in the corp palette; then the regular (tier I), elite (tier II) and boss (tier III) wheels. |
| `motion_<corp>.gif` | All of a corp's slice animations, looping. 12 frames, 0.5–1 MB each. |
| `corps_compare.jpg` | The 5 bosses through phases 1, 2 and 3, all on tier III borders. Below them, the squint test: the regulars at r = 46, sharp and blurred. |
| `scripts/` | Run `make_round16.py preview`, `corp <corp>` and `compare`. `clear_cache.py all` clears `scratch/`. New this round: `scenes16.py`, `preview16.py`, `kits16.py`, `patch_palette.py` (a one-off palette patch, kept as a record). |

## Global changes
- **Upright animations.**
  - Corp animations are now composited in screen space, centred on the slice's screen and kept upright, in the same way as the glyph and value block (`slicelib.render_slice`, `ctx.scene_req`). Slices at the bottom of the wheel no longer play upside down.
  - The material still follows the slice.
  - In Godot, sample the scene flipbook in screen-aligned UV around the slice centre, using the same counter-rotation as the read block, and mask it by the screen shape.
- **Corp tiers.** All three are drawn inside the bezel.

  | Tier | Bezel ring and edge | Inside |
  |---|---|---|
  | I | corp primary colour | nothing added |
  | II | corp secondary or threat colour | nothing added |
  | III | primary | the round 15 "a" treatment: a filled gap cross-hatched in the primary colour, and an inset line in the secondary colour |

  Secondary colours: Meridian red, Solace pink, Halcyon amber, Orbital white, Rebel Cell pale pink. These are placeholders; tiers are not in the game data yet.
- **Halcyon vs Orbital.**
  - Halcyon moved to violet `#B06EFF` with amber `#FFAA28`: a violet blueprint with amber annotations, a violet bezel and an amber tier II.
  - Orbital moved to cold cyan `#6EEBFF` with white: a dark teal sky with cyan nebulae, a pale steel bezel and a white tier II.
  - The blurred squint strip on `corps_compare.jpg` shows them as violet against cyan.

## Card-play preview A2
- Every needle gets the **same full ghost blade with a value window**. When there is more than one needle, each blade has a small index tab (1, 2 or 3).
  - The real blades get the same tabs, so needle 2 and ghost 2 pair up.
  - The secondary pins are gone. All needles are full blades (`spec["full_blades"]`).
- **The trace is a plain solid line outside the rim**, running from a dot at the needle to its ghost. The arrowheads are removed.
- **Docked drones ride their slice.** Each one gets a dashed ghost drone where it ends up (a spin of N moves a drone +12N°), a dashed trace along the drone orbit in the corp colour, and an "ENDS HERE" tag.
  - Shown on the Civic Core in phase 2 (3 needles, 2 drones) and on the player wheel with a drone.
- **The gates, aim pips and arrowheads are dropped.**

## Per corp
- **Solace.**
  - ATTACK: the syringe sits inside the slice, with its point inside too. A bead swells at the point and drops fall.
  - DEFEND: a spouted beaker tilted above a test tube pours straight down, and the tube fills with bubbles.
  - GROWTH: a round cell splits into two round cells that drift well apart.
  - DOSE: a static tilted pill bottle with two-tone capsules falling out continuously.
- **Meridian.**
  - Every animation stays above the preset barcode strip; the bottom ~50 px is masked out.
  - CRIT: only the PRIORITY stamp.
  - DEFEND: the crane brings two containers in from the outer edge onto the wall on the inner side.
  - SHIELD: the lid folds shut, then a thin tape is drawn across, starting on the box.
  - JUDGEMENT: the gavel swings down from the top onto its block.
  - MISS: the tape peels off, the box opens and its sides fall, leaving an empty floor labelled EMPTY. There is no tape roller.
  - Box faces are lighter so they read on the brown material.
- **Halcyon.**
  - ATTACK has three options:
    - A, a baton strikes down from the top, with an impact star;
    - B, a patrol drone's spotlight sweeps, then a reticle locks onto a figure ("LOCKED");
    - C, an arrest warrant with a mugshot is stamped WANTED.
    - I lean towards **B**, which is the most civic-surveillance; A reads fastest at small size.
  - CRIT: the jail door just slides shut, with no CLANG and no lines.
  - DEFEND: yellow police tape criss-crosses the slice, with scrolling text.
  - SHIELD: the rock now comes from the top onto a riot shield held across the inner side.
  - MISS: option A, the CLOSED sign.
- **Orbital.** SOLAR FLARE: a loop grows on the sun's limb, detaches and flies off the top. A new loop starts growing for the next cycle.
- **Rebel Cell.**
  - SHIELD is reworked as QUARANTINE: nested pulsing hex barriers, with a cyan player packet bouncing off them.
  - DEFEND: cyan packets fall from the outer arc and burst on a red brick wall on the inner side.
  - The other slices are still the player's own screens in red.
- **Defend rule (every corp).** Attacks come from the outer arc inward, and the wall sits on the inner side: Meridian's container wall, Rebel Cell's brick wall, and Halcyon's shield and tape.
- **Notes for other teams (out of scope):** the Meridian HQ should gain cranes; the Orbital HQ might become a launch pad.

## Weakest parts / open
- **Halcyon ATTACK A (the baton)** is a thin diagonal at r ≈ 150, and the impact star does most of the work. **Rebel Cell NULL** stays dark.
- **The tier II border alone is quiet on the wheels** at sheet size. It reads best on the kit tiles.
- **The Meridian EMPTY label is small.**
