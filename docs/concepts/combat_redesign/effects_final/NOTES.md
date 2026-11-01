# Effects, final family sheets (round 2)

Designer note 7 (slice-wide overlay effects, one visual plan per group), plus notes 2, 3, 5, 10. Binding rules: `VISUAL_PLAN.md` section G and `REVIEW.md` section 3 (AD direction). No dashed line is used anywhere. Cross-hatch (L7) appears only for "lost at this END TURN". Documentation and renders only; nothing in `combat_e10_design/` or the approved E10 plates was touched.

## Files
- `fx_00_overview.png`: 28 effects at peak frame, family key with a greyscale squint row.
- `fx_P_protect.png`, `fx_H_harm.png`, `fx_D_damage.png`, `fx_L_life.png`, `fx_M_motion.png`, `fx_C_corp.png`, `fx_S_system.png`, `fx_T_commit.png`: the family sheets. Every effect has four key frames (anticipate, hit, peak, settle) plus a yellow-framed **REDUCE-EFFECTS still** (peak frame with echoes, sparks, speed lines and misregistration removed; hatch and state change kept). Each header carries STILL, ANIM, SOURCE and **STYLE MUST KEEP**. Variants (`fx_hit_land_worm`, `fx_hit_land_adjuster`, `fx_ricochet_gold`, `fx_shove_bump`) sit under their parent.
- `strips/<id>.png`: the same block per effect (parent plus variants), one file each, 28 files.
- `fx_block_vs_break.png`: the designer's example. Shield block and shield break side by side at peak (colour and greyscale) with both strips.
- `fx_plate_resolve_tower.png`: 1920x1080 in-situ resolve beat on the cutaway room: brace_block (landing lane to the arc), shield_block, hit_land, shield_break, gun_hit, kill, refund, hp_through.
- Source: `D:/rc_scratch/combat_redesign/effects2/src` (`fx2.py` new and changed effects, `sheets2.py`, `plates2.py`; the round-1 kit `fxl/fxb/fxe1-3` is copied there with a few edits).

## What changed from round 1 (the AD fixes)
| Fix | Result |
|---|---|
| Block vs break in one frame | Block = ONE intact plate, white sparks, flat pink wedge tint, no red. Break = same plate in 7 shards, deep red halftone flood, krackle, wedge goes dark. See `fx_block_vs_break.png` |
| brace_block shows the arc stopping | Tall crop from the arc band to the tower. A keylined landing lane runs down the axis; the chevron train stops at the clamp on a flat stop bar and crumples; a small clamp stamp is left on the arc |
| Soak funnel straight | Symmetric triangle on the wedge axis from the rim toward the icon, paper flow chevrons, SOAK #3A7EF3 (the R51 colour), SOAK wash over the wedge, pip hatches SOAK. The old funnel was a skewed band. It is short (38 px) because the wedge interior is short, see open point 3 |
| hp_through | Board, landing arc and HUD in one frame; six diamonds slide to one arc point and ride one shared curve to their own YOU segment |
| Firewall | One low pink flame band per ring cell, 60 percent of cell depth, inked, lighter-pink core, no white |
| Pull, Shove, Twist | Pink at resolve (paper chevrons in the pink L5 outline). Hover form stays pencil yellow, noted in each STILL |
| Merges | worm_wear and adjuster_strike are `fx_hit_land` variants (hook mark, gold rim flash); armor and ward bounce are `fx_ricochet` (steel) and `fx_ricochet_gold` |
| Parked | jam, shield_pop, boss_phase, lockdown are not drawn (no state shows them) |
| Reduce effects | Every effect has a reduce still on its sheet; implementation switch is `REDUCE` in `fxl.py` |

## Families (unchanged, accepted)
P protect (paper plate, no glow), H harm (halftone flood, krackle, X-only dots), D damage (keylined starburst, speed lines), L life (the one soft rising glow), M motion (echoes plus L5 outline: pink for the Cell, orange for the clock), C corp (flat vector scan line and flash), S system (stepped glitch bands), T commit (pencil to pink paint). They separate in greyscale on the overview.

## Per effect: what a style must keep
Core (22), lower (5), still (1). The same text is in each sheet header.
- **shield_block (P, slice-wide)**: intact plate, L10 double line, chevrons stop and spark white, no red, hard shadow, no glow. F1 taped black-book page with marker double line; F2 printed panel with inked double line.
- **brace_block (P, slice-wide)**: clamp round the whole wedge with the icon visible; the lane stops at the clamp; arc stamp stays.
- **soak_take (P)**: symmetric funnel on the axis, SOAK only, pip hatches SOAK.
- **shield_break (H)**: the same plate in 5 to 7 shards, red flood and krackle, wedge ends dark. A style that cannot separate block and break in one frame at 320 px fails.
- **hit_land (H)**: flood over the outer half only (never past r 105); wedge frame flashes HARM once; X-only dots. Worm variant: hook mark. Adjuster variant: one gold rim flash.
- **slice_crack (H)**: white crack beside the icon, stays. **slice_break (H)**: black-out, red stencil X in the outer corner only, halftone fade over the icon.
- **hp_through (H)**: one curve, board and HUD in frame; the YOU strip stays the taped player paper; red slap then L7 hatch then dark.
- **gun_hit, strike (D)**: pink painted tracer, keylined pink starburst with a white core, speed lines. **trigger_hit (D)**: pencil route ignites to paint, starbursts in sector order.
- **kill (D)**: one 2f white flare on the cell only, pink L7 hatch, KO burst with no word, shards, empty cell.
- **ricochet (D)**: no starburst, no HP lost; white glint and sparks (steel) or curved streak (gold).
- **refund (L)**: NET_CYAN RAM coin with plus, one curve to the RAM row.
- **spin, twist, pull, shove (M)**: pink L5 outline at resolve, three echoes; yellow only in hover. **rings_step, hold (M)**: orange only (the clock), THIS TURN cell outline and hourglass stamp.
- **wave_enter (M)**: enamel feed arrow, ticket slides in, solid ticket edges.
- **commit (T)**: pencil to pink paint front to back; no yellow after it.
- Lower: **firewall_burn** (pink band, 60 percent depth, no white), **grow** and **ward_on** (flat vector wipe, gold only for the boss), **trace_add** (stepped violet bands), **repair_mend** (GAIN strokes rising). Still only: **clear** (GAIN check on the arc).

## Safety and time
- Flash cap: no effect contains more than one full-strength flash event per 333 ms. The only whole-cell flash is kill's 2f flare at 70 percent on the cell; the lock-down triple band is parked. Combined effects in one beat (the resolve plate) are sequenced by the layer order in VISUAL_PLAN G, never simultaneous. This is by design and was not measured with a frame-differencing tool.
- Time grammar: every effect is HOT while it plays and settles without glow; no effect touches a future-turn (COLD or FAR) mark.
- Never over the icon: floods end at r 105, the X sits in the outer corner, the clamp is a frame; shield_break and slice_break fade the icon on purpose.
- No new words or numbers; only glyphs (plus, check, hourglass, hook, X).

## Open points and honest caveats
1. The board under the effects is the round-1 stand-in painter: the old tower of r 162, the HP ring on the rim, the E10-sized rings. It is not the R51 layout (tower r 196, HP ring on the hub, rings r 214-430). Effects are built in polar coordinates from the tower centre, so they port by scaling the radii (about 1.2 on the tower) and re-seating the HP ring; the plate is therefore a read of the effects, not a layout proof.
2. Effects are style-neutral (the neutral hand). F1 and F2 skins of P effects were not drawn here; the STYLE MUST KEEP lines define the contract.
3. The soak funnel is geometrically correct but small, because the wedge interior between the rim and the icon is only about 38 px. At the r 196 tower there is more room; check it then.
4. Colour-blind simulation of the effects (pink against HARM) was not run; every meaning is paired with a shape (starburst vs halftone flood vs plate).
5. hp_through and refund are drawn at 1x on a wide crop, so they read smaller on the overview than on their sheets.
6. Hover forms of Pull, Shove and Twist (pencil yellow) are described, not drawn; they belong to the hover plates.
