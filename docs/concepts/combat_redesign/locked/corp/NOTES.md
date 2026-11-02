# Corp skins on the locked board (Solace, Meridian), O-27 follow-ups

Plates (1920x1080, bio cutaway, E10 state, locked wheel + WPAP cards): p1_decide_solace/meridian.png, p2b_hover_solace/meridian.png, rings_crop.jpg (2x, Solace on top, Meridian below). Checks: checks_*.json, de_kinds.json, corp_checks*.json. Source: src_snapshot/ (full generator at D:/rc_scratch/combat_redesign/locked/corp/src; run `CORP=solace|meridian|neutral python asm_render.py p1|p2b bio 1`).

## What was done
- The assembled generator already had the corp hooks (lw_install + lw_skin.NeutralSkin + NeutralTape). The material skins (cs_skin.Solace / Meridian) plug into the same hook names, so the port was: select the skin by env CORP, add one new field (`kind_gain`), and one hook (corp_kinds.use, called inside paint_cells). Nothing else in the player layers changed.
- THIS TURN tape: neutral silver for every corp. The skin's tape() and hue_shift are never called (lw_install._remap uses NeutralTape only). Read-back on p1: tape pixels equal to the neutral plate within 6/255 on 100 % (neutral), 97.7 % (Solace), 98.0 % (Meridian); the 2 % are token frames and unit cells that overlap the tape band, not tape tint. Meridian orange no longer collides with the tape (it was the O-27 risk).
- Solace pink stays tiny: pink-hue pixels (hue 315-350, sat > 0.4) in the enemy zone r214-500: neutral 1796, Solace 1795, Meridian 1801 (0.28 % of the zone each, all from the game marks). The rose nuclei are under glass at about 34 % alpha and fall under the threshold.
- Unit-kind separation: the corp tint collapsed it (Solace worst), so each skin carries `kind_gain` per ring: a Lab push of the four kind washes away from their mean, applied before the corp material goes on. Gains were solved so the skinned min dE2000 is not below the NEUTRAL skin's min per ring (6.8 / 4.3 / 2.3).

## dE2000 between unit kind washes (Packet, Worm, Jammer, Payload; real painter, flat cell centre; min / mean per ring)
| skin | ring 0 | ring 1 | ring 2 | kind_gain |
|---|---|---|---|---|
| unskinned F1 | 9.1 / 14.4 | 6.0 / 9.9 | 3.5 / 6.5 | - |
| neutral | 6.8 / 10.4 | 4.3 / 6.7 | 2.3 / 4.2 | 1 |
| Solace, before fix | 3.8 / 6.9 | 2.2 / 4.0 | 1.1 / 2.4 | 1 |
| Solace, fixed | 6.8 / 15.3 | 4.3 / 8.5 | 2.5 / 4.7 | 2.4, 2.1, 2.0 |
| Meridian, before fix | 7.2 / 11.8 | 3.9 / 6.3 | 2.1 / 3.5 | 1 |
| Meridian, fixed | 7.2 / 11.8 | 4.5 / 7.0 | 2.7 / 4.2 | 1.0, 1.1, 1.2 |

Read-back on the real p1 plate (median colour of each unit cell, so marks included): Packet vs Worm ring 0: neutral 14.6 / 9.5, Solace 20.8 / 16.8, Meridian 15.8 / 7.8; Payload vs Packet ring 1: 4.4 / 5.3 / 4.7. Consistent with the table. Ring 2 has one kind only in this state (only Packet), so it is measured on swatches, not on the plate. The kind glyph still carries kind; the wash is the second channel.

## Checks run on all four plates
Draw asserts 60/60 (p1) and 21/21 (p2b) for both corps, collision overlaps 0 px on every pair, 0 dash calls and 0 dotted-mark calls. Squint, grey proof, text-vs-state and the card checks were not re-run (the player layers are the assembled ones, byte-identical code). I looked at both p1 plates, the Solace p2b plate and the rings crop.

## Skin data format for Godot (one CorpSkin resource per corp)
```
CorpSkin {
  id: "solace" | "meridian" | "neutral"
  pal: { bed, panel, panel_hi, steel, line, ink, accent ... }  # Color table; Solace: primary lime #96FF46, glass #14462E, porcelain #E2EED8; Meridian: orange #FF8C1A, oxide #964C1A, steel #463E38
  kind_gain: [g_ring0, g_ring1, g_ring2]     # float; kind wash = mean + g * (kind - mean) in Lab, computed at import/bake time, then the cell material goes on top
  cell_tex: Texture2D (512, tileable) + cell_alpha: 0.10-0.20 ; tint_alpha 0.40-0.46 (Solace), 0.34 (Meridian)
  bezel_tex, annulus_tex, arcframe_tex: ring textures or polar shader params
  rim: ring strip texture (71 helix turns Solace / 311 hazard stripes Meridian, integer turns so it closes) + 6 crest sprites at the spokes
  token_frame: 64x64 sprite (porcelain ring / steel octagon), disc_frame: 32x32 sprite
  ticket: 9-patch
  # NOT in the skin: THIS TURN / +N tape (one neutral silver, lo #768E8E..hi #E8EEF4 remap of the schedule colour), HP, hatch, HOT/COLD/FAR, outlines
}
```
Cell material is a world-space polar shader on the ring-cell mesh (membrane voronoi for Solace, polar sine ribs for Meridian). The kind wash must be baked from `kind_gain` (or computed once per skin swap), not recomputed per frame.

## Risks
- Solace gain 2.4 is a strong push; ring 0 now shows teal vs grey-violet clearly but the mean dE (15.3) is above the unskinned 14.4, so some kind pairs are louder than the F1 board. If that reads busy, lower ring 0 to 2.0 (min dE falls to about 5.5).
- Ring 2 kinds are close on every skin (min 2.3-2.7), as in the unskinned board (3.5). Kind there leans on the glyph. Only Packet exists on ring 2 in this state, so it was not checked on the plate.
- Gains were solved on the flat cell colour at one sector; the cell material has gloss and pattern that add 1-2 dE of local variation.
- Meridian: oxide cells are brown and low in contrast with the dark rim and the amber HOLD tape; the hazard rim is the loudest enemy mass now, replacing the Solace lime tape. Squint on the corp ring zone not run; the neutral tape is bright (silver) on both skins and is the loudest single item in the ring zone.
- Hover (p2b): dimmed units on Solace go grey-green; the hovered unit's frame reads. Meridian p2b was rendered but only the Solace one was inspected closely.
- The HOLD amber tape and the plan yellow are untouched, Meridian avoids yellow; BOSS_GOLD was not in this state.
- Meridian stencilled numbers still not drawn (hook `empty_marks` exists). Meridian stays hibernated in the slice, so it is a palette proof only.
- Process: I ran a bare `python -` once by mistake (empty heredoc, no code, wrote nothing) and `python -c` one-liners twice; all real work ran from script files. No Godot or Blender, nothing committed, nothing under D:/Godot/rebel_cell.
