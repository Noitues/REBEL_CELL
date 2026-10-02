# Round 16: the slice system, after the designer's round 15 review

Built on `round15_slice_system/`, which is left untouched. The **state overlays are locked** ("ship it"): `overlays.py` is carried over unchanged, and `states.png` and `states_fx.gif` are not re-delivered.

Placeholders are labelled "placeholder (not in game)" and renamed items "renamed (game name change pending)".

## Files
| File | What it shows |
|---|---|
| `glyph_set.png` | The final set at 64, 24 and 16 px, in colour and greyscale, with the 16 px confusion score over the whole set. |
| `glyph_changes.png` | The round 15 shape next to the round 16 one for the 5 glyphs changed this round, plus the 3 SANDBOX options. |
| `tiers.png` | Tier option a (agreed) at 3 strengths. Each shows I, II and III, every program, colour, grey, deutan and protan, and r = 60. |
| `firewall_screen.png` | The new player FIREWALL screen: a hero tile beside the old one, a 4-frame strip, greyscale, an r = 150 wheel and r = 60 wheels. |
| `firewall_fx.gif` | The FIREWALL loop: 24 frames, 0.3 MB. |
| `contact_sheet.jpg` | All of the above. |
| `scripts/` | The scripts. See "Build" at the end. |

## Glyphs (`glyphs16.py`)
1. **RECON.** Thin lens rings. Each eyepiece is a flat-topped cone: a short top edge, with lines from its ends down to the outer edges of the lens circle. A bar joins the lenses.
2. **SPOOF.**
   - A thin outline (18/512).
   - Inside it, a right-slant loop print: nested loops with legs sweeping down-right, a short core rod, and lower ridges flowing across.
   - Some ridges break off (ridge endings) and two fork. Every line wobbles slightly.
   - The ridges are thin white lines (12/512), clipped to the oval.
3. **NUDGE.** The spinner needle now sits on top, on its pivot, pointing down through the ±1 arc. A dark gap separates it from the arc.
4. **JUDGEMENT.** The gavel is raised and tilted, with its strike face aimed at the block, and a clear gap above the strike block.
5. **SANDBOX.** A sand pile with grain cut-outs in front, a pail behind, and a shovel with its blade showing. The pile overlaps the pail and the shovel through a dark gap.

   | Option | Arrangement | Twin |
   |---|---|---|
   | A | pail on the right, shovel stuck in the pile | 0.61 |
   | B | pail on the left, blade sticking out at the top right | 0.60 |
   | **C (chosen)** | pail behind the centre, shovel planted blade-up beside the pile | 0.64 |

   C was chosen because it shows the most blade and reads most clearly as a beach set.

**16 px check.** The closest pairs are unchanged:
- STORM (placeholder) against HP: 0.67;
- ESC against BLOCK: 0.67;
- FLIP against PERFECT: 0.66.

Every new glyph's nearest twin is at or below 0.64: RECON 0.53, SPOOF 0.55, NUDGE 0.44, JUDGEMENT 0.45, SANDBOX C 0.64.

## Tiers (placeholder): option a, three strengths
- The outer slice silhouette is identical at every tier and strength. All flair sits inside the border.
- The glyph and value block, and the 1, 2 or 3 tier-tab pips, are kept.
- Settings live in `slicekit.STRENGTH`, selected with `slicekit.TIER_STRENGTH`.

| | V1 (round 15 strength) | **V2 strong (recommended)** | V3 max |
|---|---|---|---|
| II bezel | matte | brushed steel | brushed steel |
| II inset line / gap | about 1 px / 7.5 px | 2.2 px bright / 10 px | 3 px / 12 px |
| III fill | gold border + thin hatch | solid gold strip (2.6 px) + heavy cross-hatch | thicker gold strip + bold gold chevrons running round the border |
| Screen gain, I / II / III | 70 / 100 / 122 % | 60 / 100 / 142 % | 52 / 100 / 160 % |

**Why V2.** I, II and III differ in three ways at once:
- the bezel material;
- line structure, from no line to a line plus a gap to a filled band;
- screen brightness.

Each step survives greyscale, deutan, protan and r = 60. V3 is louder still, but its chevrons compete with busy screens (VIRUS, ZERO-DAY), and its 12 px band eats into the screen at small spans.

**In Godot:** the slice shader takes `uniform int tier` and `uniform int tier_strength`, plus `gap`, `line_w`, `border_w`, `hatch_duty` and `screen_gain` uniforms filled from a small table. It uses the same `e_scr`, `u` and `v` fields, and nothing needs padding.

## Player FIREWALL screen (`screens16.py`)
The screen now reads as defence:
- Attacks come from **outside**. Threat ticks flicker along the outer rim.
- Four shots per volley, two volleys per loop, drop **radially inward** at a constant angle, so they converge towards the hub. They fly beside the value block, not behind it.
- The **wall stands on the inner part of the slice**, by the hub: brick rows from 64 % of the screen depth down to the hub side, with a crenellated top and a bright top edge.
- On impact, each shot flashes a ring and a white strike line, kicks sparks back up and outward that then fall, and heats the top three brick rows around the hit.
- It loops over t ∈ [0, 1) with no seam.

It is installed by `slicekit.setup()`, which registers it as the player's FIREWALL screen in `programs.PLAYER`.

**Applies everywhere a wall is shown:** card art, DEFEND forecast chips and the DEFEND hit effect all follow the same rule. Hits come from outside or above, and the wall is on the side of the thing being protected.

In Godot, it can be a flipbook baked from `screens16.firewall`. Alternatively, a shader with 4 shot lanes (angle and phase uniforms), a brick tile below `WALL_TOP` and an impact ring, both driven by TIME.

## Build
Run from `scripts/` (Pillow and numpy only):
1. `python make_glyphs.py`
2. `python make_changes.py`
3. `python make_tiers.py`, about 3 minutes
4. `python make_firewall.py`, about 1 minute
5. `python make_contact.py`

`glyphs15.py`, `glyphs14.py` and `glyphs13.py` are the verbatim references for older shapes.

## Weakest part
- **The FIREWALL shots read well at hero size but are small at r = 60.** The wall and the impact flash carry the meaning there.
- **The SPOOF ridges merge into a textured oval at 16 px.** That is acceptable as a silhouette (twin 0.55).
