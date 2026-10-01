# Round 15: corp wheels with full-screen slice animations, and preview A

These are built on round 14 (`round14_corp_wheels`, which is unchanged).
- **Frame:** D4 "Lens & rail".
- **Glyphs:** round 14's picks, loaded from `round14_slice_system/scripts/glyphs13.py` and `glyphs14.py` (copied into `scripts/`). So JUDGEMENT is the gavel, CITATION the torn receipt, NULL "÷0", SANDBOX the sandbox and so on.
- **New crest glyphs:** the Halcyon EYE and the REBEL_CELL raised FIST. Both are in `scripts/crests15.py`.

## Files
| File | What it shows |
|---|---|
| `preview_A.png` | The card-play preview, option A, revised. See below. |
| `corp_<meridian/solace/halcyon/orbital/rebel_cell>.png` | Per corp: every slice type as a 4-frame strip of its animation (t = 0, .25, .5, .75), with the loop described, then the material, crest and accents, then the regular, elite and boss wheels. |
| `motion_<corp>.gif` | Every slice type of that corp, looping (12 frames, about 1 MB each). |
| `corps_compare.jpg` | The 5 bosses: phases 1, 2 and 3 in rows. |
| `scripts/` | Everything needed to rebuild. |

**Rebuild:**
- `python scripts/make_round15.py preview`
- `python scripts/make_round15.py corp <corp>` (the 5 corps can run in parallel)
- `python scripts/make_round15.py compare`

`python scripts/clear_cache.py all` clears `scratch/`.

**New code:**
- `scenes.py`: the full-screen corp animations, one function per corp and type. Each takes t ∈ [0,1), loops seamlessly and is seeded.
- `preview15.py`: preview A.
- `kits15.py`: what each corp kit shows.
- `make_round15.py`: builds the sheets.

**Changes to copied code:**
- `skins.corp_texture`: the corp material is darkened to 62 % and the scene is composited over the whole screen. The small round 14 motif panel is gone.
- `skins.rebel_program`: the player's own C program for that slice type, recoloured red.
- `roster_wheel`: Halcyon's emblem is now EYE and REBEL_CELL's is now FIST. Tariff uses the JUDGEMENT glyph.

## Card-play preview, option A
- **Each needle gets its own ghost at its landing tick.** The primary needle gets a ghost blade with a value window in the landing slice's colour. Extra readers get ghost pins (an in-rim pin with a round value window).
- **The landing slice is outlined** with dashes in the slice's colour.
- **The move is traced outside the rim.** The trace starts with a dot at the needle and runs to the landing tick. White arrowheads every 18° give the direction, and a large arrowhead in the landing colour marks the end.
  - A spin moves the slices clockwise, so the trace runs anticlockwise. Each needle's landing is pointer − 12 × N degrees.
- **No aim pips.**
- **When a docked drone sits at a landing tick,** the drone keeps its dock. The ghost collapses to an in-rim pin, so it never covers the drone. The drone gets a dashed "lands here" ring and a value tag (for example "FIREWALL 12").
  - The sheet shows this on The Civic Core P2 (3 readers and a docked Civic Drone) and on a single-needle player wheel.
- **Future: gates (concept only).** A gate is a pair of posts on the trace radius, and it fires when a needle rotates through it.
  - A crossed gate lights gold on the trace, with the label "PASSES THROUGH GATE: +2 RAM".
  - A gate outside every trace stays grey, labelled "GATE (not crossed)".
  - The gate effects shown are placeholders.
- **Godot:** a `PreviewOverlay` node fed by the forecast system's landing ticks per pointer. It is the same code path as the forecast, so the preview always equals the real result. The trace is a `Line2D` on an arc, with arrowhead sprites placed along it.

## Corps: what changed
In every corp the animation now fills the whole slice screen, like the player's C slices. The white glyph and value sit on top on the usual read plate. The motif panel is removed.

| Corp | Slice animations | Notes |
|---|---|---|
| Meridian | ATTACK: crates on rollers (kept). CRIT: laser over the barcode plus a PRIORITY stamp (kept). DEFEND: a crane lowers a container onto a container wall. SHIELD: a box lid folds shut, then tape is pulled across. **JUDGEMENT** (RAM drain): a gavel strikes the block, with an impact flash, shockwave rings and "RAM −3". MISS: the box falls open with nothing inside. | Container look, colours and crest kept. **HQ note (out of scope): the HQ should gain cranes to match.** |
| Solace | ATTACK: an angled syringe whose plunger pushes, with drops falling. CRIT: a heartbeat pulse races across. DEFEND: a beaker pours into a vial and it fills. **GROWTH (heal)**: one cell splits into two. DOSE: a pill bottle tips and pills spill. MISS: a flatline with a bright dot travelling along it. SHIELD (extra): membrane rings. | Green, bubbles, DNA, heartbeat and crest kept. **HEAL is labelled "GROWTH (heal)"; the game name change is pending.** |
| Halcyon | ATTACK: handcuffs close on a wrist. CRIT: a jail door slams shut (CLANG). SHIELD: a thrown rock bounces off a riot shield. CITATION: a paper is stamped FINE. HEAL: an ambulance drives by. DEFEND: police barricades slide together (my pick; not briefed). **MISS, two options: A, a CLOSED sign swinging on its chain; B, an empty file folder that flops open to show NO RECORD.** | Radar and blueprint material kept. **The crest's halo is replaced by an EYE.** |
| Orbital | ATTACK: one small meteor hits the planet. CRIT: a large meteor and a shower of small ones. DEFEND: a satellite laser destroys a meteor. EVADE: a spaceship fires its engine and leaves the screen. SOLAR FLARE: kept (corona plus an erupting loop). MISS: an astronaut drifts away (TETHER LOST). SHIELD and HEAL (extra): an energy dome; solar panels unfolding. | Material and crest kept. **HQ note (out of scope): the HQ might become a launch pad.** |
| REBEL_CELL | Every slice runs the **player's own C program**: the same screen and animation as on the player wheel, recoloured into a red palette. It sits on the Cell's corrupted PCB material, with the broken black-and-red rim. | **Crest: a raised REBEL FIST.** Concept: the player, turned against himself. |

**Inheritance is unchanged from round 14.**
- The corp level owns the material, the scene set per type, the rim, the crest and the accents.
- The enemy level owns the data.
- The tier and phase levels own the frame extras and the P2 and P3 effects.
- The only change: the motif atlas becomes a full-screen flipbook per corp and type (8–12 frames), sampled in the slice's polar UV, which is the same path as the player programs.
- The Rebel Cell reuses the player's program flipbooks with a `palette = red` uniform, so there are no extra assets.

## Weakest parts / open
- **Scenes are drawn in the slice's polar texture space,** like the player screens, so on the wheel each scene turns with its slice. On the slices at the bottom of the wheel, scenes such as the ambulance and the astronaut are upside down. If the designer wants upright scenes, they need the same counter-rotation the read block has.
- **Several animations are subtle at r ≈ 150:** the rock on the riot shield, the Halcyon handcuffs, and Meridian's tape. They read best on the hero tiles and in the GIFs.
- **Halcyon DEFEND (barricades) and the extra Solace and Orbital SHIELD and HEAL scenes were not briefed.** They are proposals.
- **On the Rebel Cell wheel, the player's NULL and PATCH screens are dark in red,** so they read weaker than the bright EXPLOIT and ZERO-DAY.
