# Round 17: the FINAL slice system package

This round applies three glyph tweaks to the locked round 16 set, then consolidates everything. Earlier rounds are left untouched.

**Locked:**
- Screens & Data slices;
- the glyph set;
- tiers: option a, V2 "strong";
- the 8 state overlays;
- the player FIREWALL screen;
- NUDGE, JUDGEMENT, and SANDBOX option C.

Content that is not in the game yet is marked **placeholder (not in game)**:
- the slice tiers;
- the FROZEN, LOCKED, BURNING and EMPOWERED states;
- the placeholder glyphs.

Renamed items are marked **renamed (game name change pending)**:
- WEIGHT, which was INERTIA;
- JUDGEMENT, which was TARIFF.

## Files
| File | What it shows |
|---|---|
| `glyph_set.png` | Every final glyph at 64, 24 and 16 px, in colour and greyscale, with the 16 px confusion check. |
| `glyph_changes.png` | Round 17's three tweaks, old against final. |
| `tiers_final.png` | V2 on every program at I, II and III. Includes grey, deutan and protan versions, an r = 60 mixed wheel, and a Meridian corporation-palette example (tiles plus an r = 110 wheel). |
| `slice_system_final.png` | A one-sheet summary: a glyph excerpt, the V2 tiers, the player FIREWALL, the 8 state overlays and an r = 170 wheel combining tiers and states. |
| `glyphs/` | 58 final glyphs, 256 px, white on transparent (alpha is coverage), plus `index.txt`. |
| `scripts/` | The scripts. See "Build" at the end. |

## Round 17 glyph tweaks
1. **RECON.** The cone eyepieces are shorter and filled solid. The lens circles stay thin open rings.
2. **SPOOF.** The horizontal ridges across the bottom are removed; the rest of the print is unchanged.
3. **SOLAR FLARE.** The lower bar is removed, leaving only the horizon line under the sun.

**16 px check, whole final set.** The closest pairs are STORM (placeholder) against HP, and ESC against BLOCK, both at 0.67. Every other pair is 0.66 or lower. The three tweaked glyphs score 0.50 to 0.53 against their nearest twin.

## Final rules
**Glyphs**
- Each glyph is one flat white silhouette with few dark cut-outs, and a dark rounded outline added at render time (outline width = 0.075 × size).
- Strokes are at least 40/512 of the box, cut-outs at least 24/512. Thin-line exceptions: the SPOOF ridges and the RECON rings.
- The outer silhouette alone must identify the glyph at 16 px, with soft IoU against every other glyph below about 0.68.
- Attacks are pointed, defences blocky.
- The game never relies on colour alone.

**Status badges** wrap the mark in a shape that says whether it helps:
- circle: helps;
- diamond: hurts;
- circle with a diamond notch: helps, then hurts;
- rounded square: neutral;
- dashed outline: predicted.

**Pictograms**
- An amount sits at the bottom right of the mark.
- **MOMENTUM is dynamic.** The spin arrow carries "big/small" numbers, and the big one is what will run: before any spin it shows big 2 / small 5; after a spin, small 2 / big 5.
  - The card view reads the turn's "spun this turn" flag and re-styles the two labels: about 0.62 against 0.34 of the mark height, and white against grey.
  - It updates after a spin resolves, and after undo or rewind.

**Tiers (V2)**
- The outer silhouette is identical at every tier; all flair is inside the border. The glyph and value block never changes.
- The tier-tab pips (1, 2, 3) sit in the top centre.

| Tier | Bezel | Screen | Inside the border |
|---|---|---|---|
| I | matte | 60 % gain | — |
| II | brushed steel, type-colour trim | 100 % | a 2.2 px bright line inset, with a 10 px gap |
| III | gold, with holo lip | 142 %, holo sweep | a solid 2.6 px gold strip, then heavy gold cross-hatch filling the gap up to the gold line |

**Overlays**
- An overlay is its own layer, drawn under the read block, so the value is never covered. Inside the read window it thins to 35 % or less.
- The badge goes in the outer-right corner. OVERCLOCKED adds a ×1.5 chip and PARASITE a ×0.5 chip, near the inner edge.
- All loops are seamless over t ∈ [0, 1).

**Player FIREWALL**
- Shots fall radially inward from the outer rim onto a crenellated wall in the inner, hub-side part of the slice.
- The same rule applies everywhere a wall is shown: hits come from outside, and the wall stands on the side of what it protects.

## Godot 4.7 build notes
### Glyph atlas and SVG export
- **Source of truth:** `glyphs/*.png` at 256 px, alpha only.
- **Atlas:** build an MSDF/SDF atlas from these files, in 128 px cells, packed in `index.txt` order. Draw it with one CanvasItem shader:
  - fill white at `smoothstep(0.5 ± aa)`;
  - outline `#0C0A16` at width `uniform float outline = 0.075`.

  One atlas covers 16 to 64 px.
- **SVG alternative:** trace each PNG with potrace (`potrace -s --flat`) to `glyphs_svg/<same name>.svg`, and import it at 1×, 2× and 4×.
- **Aliases** reuse a file:

  | Pictogram | Uses |
  |---|---|
  | FREEZE | `state_frozen` |
  | RESIST | `special_weight` |
  | DAMAGE | `slice_exploit` |
  | SHIELD pts | `placeholder_shield` |
  | EVADE | `slice_proxy` |
  | HEAL | `slice_patch` |

  BURN and BURNING share the flame; ENCRYPT and ENCRYPTED differ.

**Export list (58 files):**
- `slice_`: `exploit`, `zero_day`, `firewall`, `sandbox`, `proxy`, `patch`, `virus`, `trojan`, `null`
- `special_`: `judgement`, `citation`, `solar_flare`, `dose`, `weight`, `drone`
- `placeholder_`: `phishing`, `shield`, `encrypt`, `recon`, `burn`, `bomb`, `vault`, `key`, `spoof`, `storm`, `kill_process`
- `status_`: `corrupted`, `parasite`, `overclocked`, `encrypted`, `cleanse`
- `state_`: `frozen`, `locked`, `burning`, `empowered`
- `picto_`: `spin`, `spin_ccw`, `momentum`, `respin`, `nudge`, `nudge_inner`, `free_nudge`, `again`, `flip`, `snap`, `ring_lock`, `perfect`, `draw`, `ram`, `breach`, `undock`, `block`, `all_targets`, `take_dmg`, `exhaust`, `target`, `no_damage`, `hp`

The `.png` suffix is omitted throughout. The slice and status icons go into `SliceData.icon` (Texture2D); content stays read-only.

### Slice shader (tier uniforms)
**Per-slice ShaderMaterial on the wedge.** All are uniforms:
- `slice_color`, `span_deg`, `r_in`, `r_out`, `time`;
- `screen_tex`, a flipbook or SubViewport of the program screen;
- `tier` (int 1 to 3);
- `tier_gap_px = 10.0`, `tier_line_px = 2.2`, `tier_border_px = 2.6`;
- `tier_hatch_duty = 0.46`, `tier_hatch_period_px = 5.4`;
- `screen_gain` (0.60, 1.00 or 1.42), from a tier table in config, not hard-coded;
- `bezel_material` (0 matte, 1 steel, 2 gold).

**Distance fields:**
- `e_scr`: the signed distance inside the screen;
- `u`: arc length from the midline;
- `v`: depth from the outer screen edge.

These come from `slicekit.geom` and port line for line. The tier-tab pips are drawn in the same pass. No padding is needed beyond the rim.

### Layer order per slice (top-most last)
1. The wedge with the slice shader: screen, then bezel, then tier.
2. The **overlay layer**: a sibling `ColorRect` padded about 34 master px outward (flames and halo) with its own ShaderMaterial.
   - Uniforms: `state` (int), wedge uniforms, `read_center`, `read_radii`, `seed`.
   - CORRUPTED uses `hint_screen_texture`; the others are procedural.
   - PARASITE draws the bug texture at about 40 % alpha, with an animated leg phase.
3. The **read block**: the glyph `TextureRect` plus the value `Label`, kept upright (counter-rotated), on a darkened ellipse plate.
4. The **front marks**: the state badge (outer-right) and the rule chip (inner edge).

The view only reads runtime slice state, through the "signal up, call down" rule. It never mutates Resources.

## Build
Run from `scripts/` (Pillow and numpy only):
1. `python make_glyphs.py`
2. `python make_changes.py`
3. `python make_final.py`, which writes `glyphs/`, `tiers_final.png` and `slice_system_final.png`, in about 3 minutes.

`glyphs17.py` holds the final shapes. `glyphs13` to `glyphs16` remain as the history.
