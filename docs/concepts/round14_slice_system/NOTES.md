# Round 14: the slice system, after the designer's round 13 review

This round builds on `round13_slice_system/`, which is left untouched. It uses the same family C slices: live CRT screens in per-slice bezels, with an upright glyph and value on a read plate. The slice frame is covered in `round13_wheel_details/`.

The names used are the game's own:
- `rc.gd`: SliceType and Status;
- `art_asset.md`: sections E2, E3 and E5.

Anything not in the game is labelled **placeholder (not in game)**. Renamed items are labelled **renamed (game name change pending)**.

## Files
| File | What it shows |
|---|---|
| `glyph_set.png` | The full set at 64, 24 and 16 px, in colour and greyscale. Below it, the 16 px confusion score over the whole set. |
| `glyph_changes.png` | Every changed glyph: the round 13 shape next to the new options. Each option is shown at 64 and 16 px with its "twin", the most alike glyph in the whole set. A gold frame marks the choice. |
| `tiers.png` | Tiers I, II and III, with three shape options for tier III. Each is checked in colour, greyscale, deuteranopia and protanopia, on a hero tile and at r = 60. Below that, every program at all three tiers. |
| `states.png` | All 8 overlays. Each is shown on 3 slice colours, on an r = 60 wheel and in greyscale. |
| `states_fx.gif` | The idle loops: 24 frames, 2.7 MB. |
| `contact_sheet.jpg` | All of the above. |
| `scripts/` | The scripts. See "Build" at the end. |

## Glyph changes (numbering follows the review)
1. **WEIGHT** (was INERTIA; renamed, game name change pending).
   - Options: A anvil (twin 0.60), B "1 t" weight (0.67, too close to FIREWALL), C dumbbell (0.58).
   - **Chosen: C.** It no longer clashes with LOCKED.
2. **SANDBOX** (the SHIELD slice: its shield persists across turns, cap 15).
   - Options: A plank box with a mound of sand and a shovel, B top-view frame with a shovel, C box with a bucket and a shovel.
   - **Chosen: A.** It reads best as a kid's sandbox. Its twin scores 0.63; B scores 0.61 but reads less like a sandbox.
3. **PATCH**: two crossed band-aids, each a single constant width. The HEAL pictogram uses the same glyph. DOSE is unchanged.
4. **SHIELD** (placeholder).
   - Options: A heraldic shield, half solid and half outline (twin 0.58); B riot shield (0.66); C double wall (0.63).
   - **Chosen: A.**
5. **RECON**: binoculars.
6. **NULL**.
   - Options: A slashed 0 (twin 0.69, against the tilted CITATION receipt), B ÷0 (0.53), C 1/0 (0.55), D x/0 (0.52).
   - **Chosen: B, ÷0.** At 16 px it reads as a divide sign over a 0.
7. **JUDGEMENT** (Meridian's RAM drain; was TARIFF; renamed) now uses the gavel.
8. **CITATION** (Halcyon; plants PARASITE) now uses the receipt. To leave the receipt without a twin, it is tilted 14° and torn top and bottom. Its closest pair is now FINGERPRINT at 0.65.
9. **SPOOF**: a whole fingerprint, as an oval with closed ridges.
10. **CLEANSE**: CTRL-ALT-DEL.
    - Option A: three keycaps at 64 px. At 48 px and below it reduces to a single DEL keycap (`SMALL` map in `glyphs14.py`). **Chosen.**
    - Option B: stacked keycaps at every size.

    Keycaps are slightly trapezoid, as seen from the front, so they don't read as the square BLOCK wall.

    **KILL PROCESS** (placeholder) uses two keycaps side by side, ALT and F4. That keeps it wide, unlike CLEANSE's single key, which it scored 0.82 against while it was also a single key.
11. **EMPOWERED**.
    - Options: A three bold chevrons (twin 0.62), B an up arrow breaking a bar (0.62), C a star with an up arrow (0.50).
    - **Chosen: B.** It reads as "power up", where A reads as rank. C is the safest pick on the score.
12. **MOMENTUM** (was SPIN n+; "spin 2, or 5 if you already spun this turn").
    - Options: A spin arrow with a chain link, B a double loop with a small arrow inside a big one, C a spin arrow with rising steps.
    - A (0.85) and C (0.88) are too close to SPIN.
    - **Chosen: B** (0.49). The card prints "2>5" beside it.
13. **NUDGE INNER**: a bullseye in a thin outer ring. The middle ring is thick and is itself a two-headed arrow (±1).
14. **NUDGE**.
    - Options: A a short two-headed arc over one tick, B the arc over "±1", C the arc over a three-tick rim ruler.
    - All three are much shorter than SPIN.
    - **Chosen: A** (0.46).
15. **UNDOCK**.
    - Options: A a drone with an outward arrow (0.33), B an open ball-and-socket (0.56).
    - **Chosen: A.**
16. **BREACH**: a lightning bolt over a bullseye.
17. **EXHAUST**: a card torn in two, with no fire.
18. **One flame.** `flame2()` is a single shape with two peaks, used by BURN, the BURNING mark and FIREWALL's flame (wall plus flame).

**Fixed while drafting:**
- RING LOCK became a ring with a padlock hanging off it, because it scored 0.71 against the new BREACH bullseye.
- STORM's bolt now drops out of the cloud, because it was too close to HP.

**16 px confusion score over the whole set.**
- The closest pair is STORM against HP at 0.67. Round 13's worst pair was 0.71.
- Every other pair scores 0.66 or lower.
- The sheet lists the 12 closest pairs.
- Pairs kept alike on purpose are excluded: SPIN clockwise and anticlockwise, BURN and BURNING, ENCRYPT and ENCRYPTED, HP and TAKE DAMAGE.

## Tiers (placeholder: SliceData has no upgrade tier)
**I → II** stays as in round 13: brushed steel, a type-colour trim line, corner brackets and 2 pips.

**II → III** is now a **shape** change past the outer rim, on top of the gold bezel:

| Option | Shape | How it reads |
|---|---|---|
| A crown | 3 spikes standing on the rim | Strong at hero size. At r = 60 it merges into a jagged rim. |
| B double rim | a second, notched rim outside the first | Reads as a thicker rim at r = 60. The notches vanish below r ≈ 100. |
| **C crest (recommended)** | one pointed gold tab with a gem at the rim's centre | Survives greyscale, deuteranopia, protanopia and r = 60 as a single bump. |

The vision check simulates colour blindness with Machado 2009 at full severity, in linear RGB (`make_tiers.cvd`).

All three options stand up to 34 master px past the rim. The wheel frame (the other agent's work) must leave that much room, or let the crest overlap it.

## Overlays (`overlays.py`)
These rules carry over from round 13:
- An overlay is its own layer, drawn under the read block, so the value is never covered.
- Inside the read window it thins to 35 % or less.
- The badge sits in the outer-right corner: circle helps, diamond hurts, notched means helps then hurts, square is neutral.
- Every animation loops seamlessly over t ∈ [0, 1).

| State | Round 14 |
|---|---|
| CORRUPTED (status) | A full-slice glitch shader in pink and green, with no extra icon. Bands of the whole slice, bezel and alpha included, tear sideways, re-rolled 12 times per loop. The outline and bright content split into a pink and a green ghost. The screen gets pink and green bands, scanline flicker and a tear line. In Godot this samples `hint_screen_texture`. |
| OVERCLOCKED (status) | The round 13 look, composited at 45 % so the slice shows through. Keeps the ×1.5 chip. |
| ENCRYPTED (status) | A field of `*` characters scrolling radially outward, up the wedge. The rows are staggered and the loop moves two rows, so it is seamless. Keeps the cyan rim. |
| PARASITE (status) | The tick itself, latched on, large (95 % of the screen height) and translucent. It pumps and wobbles. The hub side is drained, and it keeps the ×0.5 chip. The veins are gone. |
| FROZEN | Kept from round 13. |
| LOCKED | Three rows of padlocks scroll left to right; the screen is dimmed and the bezel turns steel. The shutter is gone. |
| BURNING | Kept from round 13. The flames stay procedural noise fields, because the two-peak glyph shape looked worse as a fire field. The two-peak shape is used for its badge mark. |
| EMPOWERED | Huge translucent gold arrows, pointing outward and moving outward (they ran inward in round 13), with a bright edge. Keeps the rim glow and halo. |

## Godot 4.7 build notes (changes from round 13)
- **Glyph atlas.** It holds the chosen options only. Add the `SMALL` forms (CLEANSE's DEL key) as separate cells, and swap them in when the drawn size is 48 px or less.
- **Tier III shape.** It needs the slice quad padded outward by 34 master px. Draw it in the slice shader for `tier == 3`, from the same `u`, `h = rho - r_out` fields as `slicekit.tier3_shape`, with a `uniform int tier3_style`.
- **CORRUPTED.** One `ColorRect` per slice over the whole padded rect, with `hint_screen_texture`:
  - row-band UV offsets from a hashed `floor(TIME * 12)`;
  - a pink and a green ghost from the alpha gradient, offset ±k px.
- **ENCRYPTED and LOCKED.** Tiled glyph textures (`*` and the padlock) sampled in the wedge's polar UV, scrolling over TIME: v for ENCRYPTED, u for LOCKED.
- **PARASITE.** The parasite glyph from the atlas, drawn as a `TextureRect` child at about 40 % alpha, with a small sine scale and rotation.

## Build
Run from `scripts/` (Pillow and numpy only):
1. `python make_glyphs.py`
2. `python make_changes.py`
3. `python make_tiers.py`, about 2 minutes
4. `python make_states.py`, about 6 minutes including the GIF
5. `python make_contact.py`

Scratch renders go to `../scratch/`, which git ignores and which is cleared after each run.

## Weakest part
- **The ÷ in NULL, and the CTRL / ALT / DEL text at 64 px, depend on the font.** At 24 px the CTRL-ALT-DEL row is unreadable, which is why it swaps to the DEL key.
- **MOMENTUM B is clear but abstract.** The "2>5" on the card does the explaining.
- **Tier III-C's crest needs room outside the wheel frame.**
