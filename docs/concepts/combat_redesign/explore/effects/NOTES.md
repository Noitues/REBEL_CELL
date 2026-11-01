# Slice-wide overlay effects (FX family designs)

Designer notes served: 7 (slice-wide effects, one look per group), 2/3 (time and hatch grammar), 5 (colour = cause or owner), 10 (real redesign).
Binding source: VISUAL_PLAN.md section G. 36 effect ids are drawn (the plan table lists 36 rows; it says 37 in the prose).
No dashed line is used anywhere. Cross-hatch (L7) appears only for "lost at this END TURN" (pending HP, pips, ticks, dying cell).

## Files
- `fx_00_overview.png`: every effect at its peak frame, a family key with a greyscale squint row.
- `fx_P_protect.png`, `fx_H_harm.png`, `fx_D_damage.png`, `fx_L_life.png`, `fx_M_motion.png`, `fx_C_corp.png`, `fx_S_system.png`, `fx_T_commit.png`: one sheet per family. Each effect has a 4-frame strip on a crop of the board at 2x (whole-tower, ring-wide and HUD-spanning effects use 1x to 1.9x so the strip fits). Frames: anticipation, hit, peak, settle. The peak frame is the still.
- `fx_plate_a_resolve_tower.png`: 1920x1080 in-situ plate, resolve beat on the tower: shield_block, hit_land, shield_break, slice_crack, gun_hit, kill, repair_mend, refund, hp_through.
- `fx_plate_b_motion_corp_system.png`: 1920x1080 in-situ plate: spin with echoes, twist, pull, shove, wave_enter feed, grow, ward_on, trace_add glitch.
- Source: `D:/rc_scratch/combat_redesign/effects/src` (`fxl.py` kit, `fxb.py` board painter, `fxe1..3.py` effects, `sheets.py`, `plates.py`).

Caveat: the board under the effects is a painter written for this task in the VISUAL_PLAN language (pink hand-stroked tower, slate vector cells, gunmetal bezel, stencil chevrons). It is a stand-in for the finalist art of the other streams, which is not final. The tower is drawn in a neutral "hand" (wobbled marker strokes); the P effects use the same hand, so they will re-skin with whichever style direction wins. Halftone is used by FX-H on purpose. If G3 Spider-Verse print wins, use the fallback below.

## Families, material and look (greyscale-distinct)
| Family | Material | Signature | Colour |
|---|---|---|---|
| FX-P protect | opaque paper plate, no glow, hard offset shadow | plate slams on, painted double edge (L10), rivets, tally ticks; clamp is a frame so the icon stays visible | PAPER + CELL_PINK; SOAK funnel for soak |
| FX-H harm | print: halftone dots 6 px at 45 deg, black krackle, 3 px misregistration (dark-red plate offset) on impact frames only | flood rolls from the rim over the outer 40 percent, never past the icon (static for jam uses random pixel noise, not dots) | HARM + INK, gold edge for the Adjuster |
| FX-D damage | comic hit frame: keylined starburst, converging speed lines, clean vector shards | pink star with white core at the struck cell; slash and flames for Strike and Firewall | CELL_PINK + white; steel for armor; gold for ward |
| FX-L life | light: soft additive glow, rising brush strokes, sparkles, plus signs | the only soft, rising, glowing family | GAIN (RAM coin is NET_CYAN) |
| FX-M motion | ghosts: three echoes at 30/20/10 percent plus an L5 arrowed outline | arrow colour by owner: pink tower, orange rings, yellow plan (pull, shove) | CELL_PINK / SCHEDULE / PLAN |
| FX-C corp | clean vector: 1 px scan line, flat tint, one flat flash | no texture, no glow | ENAMEL, gold for the boss |
| FX-S system | glitch: horizontal bands, 6 px shear, 2 px channel split, scanlines | acts on whatever is under it | TRACE_VIOLET |
| FX-T commit | pencil to paint | white-hot front burns L5/L6 pencil marks into pink paint | PLAN to CELL_PINK |

## Effect, family, look
| id | fam | footprint | still (peak frame) |
|---|---|---|---|
| fx_shield_block | P | slice | paper plate on the outer 40 percent, chevrons stop at its edge, white sparks, pink ping ring, 2 tally ticks |
| fx_brace_block | P | slice | clamp frame closes round the wedge, impact ring, chevrons crumple (landing-arc stop is shown with the arc on plate A: no arc in the crop) |
| fx_soak_take | P | slice | indigo funnel rim to pip, overflow chevron shrinks into it, pip hatches SOAK |
| fx_shield_break | H | slice | plate splits into 7 misregistered shards over a red flood, krackle; wedge ends dark |
| fx_hit_land | H | slice | red halftone flood (outer half), krackle, pip hatches red then is gone |
| fx_slice_crack | H | slice | white crack beside the icon, stays as the cracked mark |
| fx_slice_break | H | slice | black-out with halftone fade over the icon, red stencil X in the outer corner |
| fx_hp_through | H | rim to HUD | red diamonds fly an arc to the taped YOU strip; strip takes a halftone slap; segments hatch then go dark |
| fx_worm_wear | H | slice | second small krackle plus a red hook mark on the rim |
| fx_jam | H | slice | red pixel-static bands; holds as COLD (dim icon, two thin bands) |
| fx_adjuster_strike | H | slice | hit_land with gold-edged krackle and one gold rim flash |
| fx_gun_hit | D | cell | painted tracer, pink starburst, speed lines, tick hatches pink |
| fx_strike | D | cell | bigger star plus painted slash with white core |
| fx_trigger_hit | D | cells on path | pencil path burns to paint, stars pop outer to inner |
| fx_firewall_burn | D | sector column | pink flame tongues with white cores sweep out through the rings |
| fx_shove_bump | D | two cells | two small stars on the shared edge, bump line, shards |
| fx_kill | D | cell | one-frame white flare, pink L7 hatch, KO burst (no word), shards, empty cell |
| fx_shield_pop | D | cell | hex pip cracks, vector shards, gone socket |
| fx_armor_bounce | D | cell | tracer hits the steel cap, glint, steel sparks fan away, no HP lost |
| fx_ward_bounce | D | cell | gold streak curves off the lozenge, no starburst |
| fx_repair_mend | L | slice | green strokes rise through the wedge, plus signs, pip fills |
| fx_refund | L | cell to HUD | RAM coin with plus pops and flies with echo to the RAM row |
| fx_clear | L | arc | green wash, would-be chevrons fade, painted check |
| fx_spin | M | tower | 40 percent ghost at the target, pink arrowed arc round the hub, two echoes |
| fx_twist | M | ring | orange arrowed sweep along ring +1, unit smears with echoes |
| fx_rings_step | M | all rings | THIS TURN bezel cell (orange L5), units slide a ring inward with echoes |
| fx_hold | M | bezel | orange hourglass stamp, cells slide a slot (live goes COLD, cold goes FAR), HOLD cell takes the live slot |
| fx_pull | M | two cells | yellow inward arrow, unit smears one ring in |
| fx_shove | M | two cells | yellow sideways arrow, unit smears one sector |
| fx_wave_enter | M | queue to ring +2 | neutral feed arrow lights, W4 ticket slides, tickets shift, cells scan in |
| fx_grow | C | cell | enamel scan line, flat flash, new hollow chevron plus ping |
| fx_ward_on | C | cell | gold edge pulse, gold scan line, flash, lozenge |
| fx_boss_phase | C | cell | gold wipe, flash, steel cap clamps from both ends |
| fx_trace_add | S | HUD and card | violet 6 px band shear on the card, violet square pops on TRACE |
| fx_lockdown | S | board | three violet bands shear the whole board in three steps |
| fx_commit | T | plan marks | pencil to pink paint, front sweeps the route, ping at the end |

## Rules the designs follow
- Time: every effect is HOT while it plays; settled frames drop glow. Future-turn marks are not touched by any effect.
- Never over the icon: floods stop at r 105 (icon top at r 106), the X sits in the outer corner, clamps are frames. Exceptions as the plan allows: fx_slice_break fades the icon on purpose; fx_jam static crosses the icon (jammed = disabled) and the icon dims.
- Never a new word or number. Glyphs only: plus, check, hourglass, hook, X. `W4` etc. and `TRIGGER` are existing text.
- Flash safety: at most 3 changes per second. fx_kill has one 2f flare, only on the cell at 70 percent (never full-frame). fx_lockdown steps in 3 bands over 18f. No white full-frame flash anywhere. Glow is additive and 35 percent or less except sparkle glints (under 60 percent, below 8 px).
- Reduce-effects variant: show the peak frame only; drop halftone shimmer (`mis` = 0), echo copies and sparks; keep the hatch and the state change.

## Build notes for Godot
- Layering (per the plan): board, T, FX-M, FX-P/H on the tower and FX-D/C on rings, FX-L, FX-S, HUD. Every effect is a child of its slice or cell node so it rotates with the tower (fx_spin echoes are copies of the tower node at -14 and -28 deg, 22 and 12 percent).
- Masks: slice effects use a wedge mask (annular sector r 44-143, half-angle 26.5 deg). Build it once as a `Polygon2D` used as a `CanvasGroup` clip, or as a shader using polar coordinates (`atan` and `length` from the board centre) as `fxl.Cv.wedge_mask` does.
- Halftone: one canvas shader. Dot screen at 45 deg, pitch 6 px at 1080p (scale with the board), coverage field = clamp(1 - depth / D, 0, 1)^0.85, dot radius = 0.74 * sqrt(coverage) of the half-pitch. Drive `D` (0 to 38 px for a landing, to 48 for shield break) by tween with `ease_out`. Misregistration = the same dots in dark red (#9C1F14) offset 3 px right and 2 px down, only for 8f around the impact.
- Krackle: 4 pre-baked spiky polygons (INK fill, HARM 2 px outline) scaled 6 to 18 px, placed on the rim at +-16 deg; offset the ink layer 3 px at impact only.
- Shatter (shield break): bake the plate to a texture, split by a 7-seed Voronoi into `Polygon2D` pieces, tween each outward 6 to 34 px with up to 40 deg of spin, fade 55 to 75 percent of the beat. Piece edges get a 2 px INK keyline.
- Paper plate: a `Polygon2D` with a 4 px INK edge, a darker fold band on the inner 10 px, two pink painted double-edge strokes (use the style direction's stroke atlas), rivets as sprites, a 3,4 px soft shadow (black 60 percent). Slide: radial 38 px plus 3 deg of twist, `ease_out`, 6f.
- Comic hit frame: 9-10 point star polygon (fill CELL_PINK, 5.5 px INK keyline) plus a smaller white star, jitter 16 percent per point; speed lines are 14 thin triangles converging on the centre, drawn for 8f only; shards are 7 vector triangles in ENAMEL with INK keylines.
- Echo (FX-M): duplicate the moving node three times with a delay of 2f each, modulate alpha 30, 20, 10 percent. Arrowed outlines use the shared L5 builder (channel 12 to 16 px, chevrons every 22 px, arrowhead 18 to 22 px) and draw on by tweening the head along the path.
- Scan-wipe (FX-C): a 1.6 px ENAMEL line sweeps along the sector angle in 8f; the swept area takes ENAMEL at 22 percent; one 2f flat flash at 40 percent on the cell polygon only.
- Glitch (FX-S): sample the screen texture, shift horizontal strips +-6 px, split red and blue channels 2 px, tint TRACE_VIOLET at 30 percent, 4 px scanlines. Step between 1, 2 and 3 bands; never animate smoothly (stepping keeps within the flash cap).
- fx_hp_through, fx_refund and fx_trace_add cross from the board to the HUD: spawn on the top-level effects layer, not under the tower node.
- Frame times: the strips use t of 0, about 0.3, about 0.55 and 1.0 of the stated frame counts.

## Open points for review
1. The P effects are drawn in the neutral hand. If G1 street graffiti wins, add spray fade to the plate edge and a tag mark in place of tally ticks. If G2 sketchbook wins, plates become torn graph paper with ballpoint rivets. If G3 print wins, drop halftone from the board: FX-H switches to speed-line floods and flat red slabs with a 3 px misregistered ink plate (halftone belongs to X only while G3 is off).
2. fx_jam static crosses the icon on purpose (jammed means disabled). If the designer wants the icon kept clean, restrict the bands to r > 104.
3. Pull and shove arrows use PLAN yellow (player intent) while ring motion uses SCHEDULE orange, per the plan's owner-colour rule. This reading needs designer confirmation.
4. fx_brace_block does not show the landing arc stop: the arc is outside the strip's crop. See the landing arc in plate A for the arc/diamond language; a brace clamp glyph on the arc is the K family's `arc_brace_glyph`.
5. Colour-blind check of CELL_PINK vs HARM for these effects has not been run; the effects use shape pairing (star vs halftone flood) so no meaning depends on hue alone.
