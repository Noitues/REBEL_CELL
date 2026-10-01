# Round 15: the slice system, after the designer's round 14 review

This round builds on `round14_slice_system/`, which is left untouched. The slices are unchanged: family C screens in per-slice bezels, with an upright glyph and value on a read plate. Placeholders are labelled "placeholder (not in game)", and renamed items "renamed (game name change pending)".

## Files
| File | What it shows |
|---|---|
| `glyph_set.png` | The final set with every pick applied, at 64, 24 and 16 px, in colour and greyscale, with the 16 px confusion score over the whole set. |
| `glyph_changes.png` | Each glyph changed this round: the round 14 pick next to the new shape, at 64 and 16 px, with its nearest twin in the set. |
| `tiers.png` | Three tier-flair options, all inside the border. Each shows I, II and III, every program, colour, grey, deutan and protan, and r = 60 wheels. |
| `states.png` | All 8 overlays: 3 slice colours each, on an r = 60 wheel and in greyscale. |
| `states_fx.gif` | The idle loops: 24 frames, 2.6 MB. |
| `contact_sheet.jpg` | All of the above. |
| `scripts/` | The scripts. See "Build" at the end. |

## Glyphs
**Approved and unchanged:**
- SANDBOX: plank box with a shovel;
- PATCH: crossed band-aids (also the HEAL pictogram);
- SHIELD: option A, heraldic;
- JUDGEMENT: gavel;
- CITATION: receipt;
- UNDOCK, BREACH, EXHAUST, BURN, FIREWALL.

**Changed:**

| # | Glyph | Round 15 |
|---|---|---|
| 1 | WEIGHT | Back to the anvil. |
| 5 | RECON | Two thin lens rings with nothing inside, a bar between them, and two thin eyepiece rectangles above. |
| 6 | NULL | "1/0". |
| 9 | SPOOF | A white oval outline on dark, with thin white ridge lines inside. |
| 10 | CLEANSE | One ESC keycap, the same at every size. |
| 10 | KILL PROCESS (placeholder) | A power button: a broken circle with a bar through the gap at the top. |
| 11 | EMPOWERED | Option A, the chevron stack. |
| 12 | MOMENTUM | The spin arrow plus a pair of numbers (see below). |
| 13 | NUDGE INNER | Now symmetric (see below). |
| 14 | NUDGE | Option A, with the tick replaced by a spinner needle: a pointer on a pivot under the ±1 arc. |
| — | PARASITE mark | The same bug as the new overlay. Its old cut-outs read as a smiley face, so they were replaced by body segments. |

**12. MOMENTUM is a dynamic pictogram.** The spin arrow carries two numbers, written "big/small". The big number is the one that will run.
- No spin yet this turn: **big 2** / small 5.
- After any spin this turn: small 2 / **big 5**.

How it updates:
- The card view reads the turn's "spun this turn" flag from the combat state, through the forecast or preview path. The view never sets the flag.
- It swaps which number gets the big style: font size about 0.62 of the mark height against about 0.34, and white against grey.
- It re-renders when the flag changes, after a spin resolves or after undo or rewind.
- In the atlas, the arrow is a glyph; the numbers are two labels. `make_glyphs.picto` shows the layout with the format `"^2/5"` (the `^` marks the big number).
- The arrow is SPIN's own arrow on purpose. The number pair is what tells MOMENTUM apart.

**13. NUDGE INNER against SPIN.** It is now symmetric, which SPIN's single arrowhead never is:
- full outer and middle rings;
- the middle ring thick, for "inner";
- a bullseye in the centre;
- a small ±1 bar with heads at both ends sitting on top.

| NUDGE INNER against | 24 px | 16 px |
|---|---|---|
| SPIN clockwise | 0.28 | 0.34 |
| SPIN anticlockwise | 0.28 | 0.34 |
| NUDGE | 0.30 | 0.35 |

All three are far from confusable.

**16 px confusion check, whole set.**
- The closest pair is still STORM (placeholder) against HP at 0.67.
- Next: CLEANSE's ESC key against BLOCK at 0.67, then FLIP against PERFECT at 0.66.
- Every other pair is 0.65 or lower. Round 13's worst was 0.71.
- Pairs kept alike on purpose are not scored: SPIN clockwise and anticlockwise, MOMENTUM and SPIN, BURN and BURNING, ENCRYPT and ENCRYPTED, HP and TAKE DAMAGE.

## Tiers (placeholder): flair now INSIDE the border, nothing past the rim
Every option keeps the same glyph and value block, and the 1, 2 or 3 tier-tab pips. Tier I is unchanged: a matte bezel, a dimmer screen, 1 pip.

| Option | II | III |
|---|---|---|
| **a (recommended)** | A thin bright line inset 7.5 master px inside the screen border, with a gap between them. | Gold border; the gap fills with gold cross-hatch. |
| b | Wider steel border with trim (round 14). | Gold border; chevrons along the inner side of the outer arc only; the 4 tick marks and the PERFECT diamond lit gold (dim grey at I and II). |
| c | Wider steel border with trim (round 14). | Gold border; a twisted-rope stripe all the way round the inner border. |

**Why a.** Each step adds structure that hugs the whole screen edge: a single line, then a line plus a filled, hatched band. That reads at r = 60, in greyscale, and in both deutan and protan sims, without relying on gold against steel.
- b concentrates tier III on the outer arc, which is thin at r = 60.
- c's tier II and III differ mainly by colour, plus a fine stripe.

**Risk with a.** At the 0.21-scale roster size, the tier II line is subtle. It reads clearly at hero size and on the r = 60 wheels.

Colour-blind sims use Machado 2009 at full severity, in linear RGB (`make_tiers.cvd`).

Code: `slicekit.TIER_STYLE` (a, b or c), `slicekit.GB` (the band width) and `slicekit.inner_flair`. In Godot this is the same slice shader, with `uniform int tier` and `uniform int tier_style`, using `e_scr`, `u` and `v`. Nothing needs padding past the rim.

## Overlays
| State | Round 15 |
|---|---|
| PARASITE | Only the large translucent bug, latched on, with nothing else drawn. Its legs crawl in alternating pairs (`glyphs15.tick_mask(phase)`, two cycles per loop) and its body pumps. The hub side is drained and the ×0.5 chip stays. The demo slices are now FIREWALL, EXPLOIT and PATCH, because TROJAN's screen has its own RGB glitch. |
| EMPOWERED | Huge translucent gold chevrons rise radially outward behind the value. The rim glow and halo stay. |
| All others | Unchanged from round 14. |

## Build
Run from `scripts/` (Pillow and numpy only):
1. `python make_glyphs.py`
2. `python make_changes.py`
3. `python make_tiers.py`, about 3 minutes
4. `python make_states.py`, about 8 minutes including the GIF
5. `python make_contact.py`

`glyphs15.py` holds this round's shapes and picks. `glyphs14.py` and `glyphs13.py` are kept verbatim as the old references.

## Weakest part
- **The PARASITE bug is faint on light-cyan slices** such as FIREWALL in the GIF. Its body alpha (0.42) could go to about 0.5.
- **Tier a's II line needs to stay at least about 1.5 px on screen** to survive the small roster size.
