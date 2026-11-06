"""R2 element list for wave_rings: direction (AD), the R2 pick (R), the one variant (V), the drawing function.  States/crops come from wr_crops.STATES (plate coordinates)."""
import wr_config as CFG
import wr_crops as CR

# id: (AD direction, R2 pick R, variant V, drawing function)
EL2 = {
 'empty_cell': ('A: void tint, one 1.4 px lane hairline at 30%, no orange edge', 'Void tint (17,24,40), ONE 1.4 px hairline in the lane colour at 30%, faint outer sheen, no orange, solid (no dashes)', 'V: darker glass, no sheen', 'wr2_cells.empty_cell'),
 'ring_separators': ('B: 8 px INK gutters aligned with the slice spokes; wide-cell interior hairlines 1.4 px at 30%', 'Gutter bed = INK, every cell inset 4 px, so every gutter is exactly 8 px; interior hairline of wide cells = lane colour at 30%, 1.4 px', 'V: R1 pick (lighter bed, 1.6 px dark spoke with notches)', 'wr2_cells.gutters / interior_hairlines'),
 'unit_cell_screen': ('C: CRT bowl dark inner to lit outer, shared 3 px mesh, mauve values kept', 'Bowl (inner 55% to the dark) on the shared 3 px mesh (white lines both ways every 3 px, 8% lift max); wash ramp unchanged', 'V: gentler bowl, mesh 5%', 'wr2_cells.screen + wr2_lib.mesh'),
 'unit_screen_bezel': ('A: removed', 'Removed (painter draws no bezel)', '-', 'none (wr_cells.bezel_mark returns for A)'),
 'unit_screen_code_text': ('A: none', 'None', '-', 'none'),
 'unit_cell_outline': ('A: ink-sheathed, drawn last; NOW 4 px HARM, +1 3 px LANE_PLUS1, +2 3 px LANE_PLUS2 dash 12/8', 'One ink-sheathed line (+4.5 px ink) on the cell edge, drawn after chevrons, tray and armour; the token alone sits above it', 'V: 7 px sheath, dash 14/8', 'wr2_units.outline'),
 'token_disc': ('A: 54 px, kind colour 26%', '54 px disc, kind colour (from kind_colour_set) at 26%', 'V: 36%', 'wr2_units.disc'),
 'token_lane_base': ('A: rim ring 4/3/3, +2 six long dashes', 'Lane ring ON the rim 4/3/3 with ink; +2 = six dashes, 40 deg on / 20 off', 'V: ring inset 2 px inside an ink rim', 'wr2_units.ring'),
 'token_halo': ('A: tight INK pool 1.5 px, blur 4, 75%', 'INK pool 1.5 px past the disc, blur 4, alpha 191 (75%)', 'V: hard 1.5 px ink keyline plus a light pool', 'wr2_units.halo'),
 'glyph_packet': ('A: cube 37 px', 'Cube, Y cut 38 units (2.7 px at 37 px), no centre dot; drawn at 37 px', 'V: open parcel, right face hollow', 'wr2_glyphs.packet_R/V'),
 'glyph_worm': ('B fixed: one bend, head bulge + eye dot, tapered tail, never S or M at 28 px', 'A hook (J): upright body, one bend at the foot, tail tapering up-left; head bulge r84 with an eye', 'V: a comma / tadpole arc', 'wr2_glyphs.worm_R/V'),
 'glyph_payload': ('A: bomb, fuse >= 2 px at 28 px', 'Bomb with a 46-unit fuse (2.5 px at 28 px), cap, spark and a core eye', 'V: plated bomb, cut band', 'wr2_glyphs.payload_R/V'),
 'glyph_jammer': ('OVERRULED to B: relay pylon with broken broadcast arcs', 'Pylon with a lattice window and a BROKEN broadcast: left inner arc whole, left outer in two pieces, right inner cut, right outer lost', 'V: symmetric broken pair', 'wr2_glyphs.jammer_R/V'),
 'glyph_ring': ('OVERRULED to C: interlocked chain links', 'Two stadium links crossing, over / under gaps at both crossings', 'V: three-link chain', 'wr2_glyphs.ring_R/V'),
 'unit_hp_row': ('A: HP grammar, CREAM kept, HARM + slash lost, capacity tray on the sector axis', 'Rounded r3 pips 18 x 7.5 in a tray of exactly one sector capacity, kept CREAM, lost now HARM + white 2 px slash + ink, gone = dark socket + solid 1.4 px hairline', 'V: 13 px pips, no tray body', 'wr2_units.hp_row + wr2_lib.rseg'),
 'chev_solid_stack': ('A: stem-less V, HARM 6 px on 10.5 ink', 'Stem-less V 27 px wide; pitch 8.4 / depth 6.8, compressed to 7.3 / 4.4 only where the 4-stack must clear the HP tray', 'V: -', 'wr2_units.stack + wr2_lib.chev_params'),
 'chev_hollow': ('B: dashed V (dashed = growth)', 'Dashed V (two dashes per arm), same size and pitch, stacked outward of the solid ones', 'V: -', 'wr2_units.stack'),
 'chev_sector_column': ('A: 1.4 px baseline tick', '1.4 px tick (ink 3.8) on the outer side of each unit stack, 30 px long', 'V: -', 'wr2_units.stack'),
 'armor_cap': ('B: armour tiles + steel cap on the token, STEEL / STEEL_HI', 'Tiles are the tray frame (two 2.5 px rails of 30 px plates, seams, rivets), so armour costs no radial band; steel cap 150 deg on the token with two rivets', 'V: outer rail only, thinner cap', 'wr2_units.rails / armour_rails / armor_cue'),
 'warded_mark': ('A: gold lozenge, skull >= 16 px, beside the token', '34 px lozenge, skull 17 px, docked on the token clockwise shoulder (3 px over the rim), drawn under the chevrons', 'V: 30 px lozenge, skull 16 px', 'wr2_units.warded'),
 'dead_x': ('A: GAIN X badge beside the token, cell + chevrons dimmed to 38%', '28 px GAIN X badge beside the token; cell, outline and chevrons veiled to 38% (true composite); HP row and token stay full', 'V: 34 px badge', 'wr2_units.gone_overlay + dead_badge'),
 'adjuster_cell': ('A: brass gradient glass, 3 px BOSS_GOLD edge, instead of the empty cell', 'Brass gradient glass, 3 px BOSS_GOLD edge + ink, hairline inner edge; nothing else under it (no empty cell, no orange outline, no programme art)', 'V: reversed gradient, 2.4 px edge', 'wr2_boss.cell'),
 'adjuster_diamond': ('A: 72 px double edge, white skull 24 px', '72 px diamond, ink + 5 px gold + 2.4 px pale inner edge, white skull 24 px, ink pool', 'V: skull on a dark core disc', 'wr2_boss.diamond'),
 'adjuster_hp_bar': ('A: BOSS_GOLD, groups of 5', 'Rounded r3 BOSS_GOLD pips 17 px in two groups of 5; the lost pip HARM + white slash + ink', 'V: 15 px pips on an ink tray', 'wr2_boss.hp_bar'),
 'ward_arc': ('A: 3 px BOSS_GOLD strip in the ring-NOW inner gutter', '3 px gold strip, 7 px ink sheath, centred in the 8 px INK gutter', 'V: 4.4 px', 'wr2_boss.ward_arc'),
 'consumed_unit': ('A: ghost 40%, PENCIL_PLAN 3 px outline, Trigger stamp from the library', 'Ghost cell at 38%, solid 3 px PENCIL_PLAN outline with ink, grey token, Trigger stamp = library glyph KA_trigger on a plan-yellow ringed disc beside the token', 'V: 4 px outline, larger stamp', 'wr2_units.ghost'),
 'trigger_killed_unit': ('A: ghost + small GAIN X, outline in wax pencil to match trigger_path, token clear of the pencil X end cap', 'Same ghost, 22 px GAIN X beside the token, outline redrawn as a wobbling 4 px wax line (ink under-stroke, grain streak, closing overshoot) in PENCIL_PLAN; the token sits at the start cap, the pencil X at the axis', 'V: the same wax line in PENCIL_THREAT red', 'wr2_units.ghost + wax_outline'),
 'screen_motif_skull': ('A: none', 'None', '-', 'none'),
 'shield_bracket': ('A: NET_CYAN 3 px under-bar', '3 px NET_CYAN bar under the shielded pips; a lost shield = the gone form (dark socket + solid 1.4 px cyan hairline), never dashed', 'V: -', 'wr2_units.shield_bracket'),
 'adjuster_armor_strike': ('A: unit chevron grammar + steel cap', 'Armour = the same steel rails round the boss HP bar + steel strips on the diamond; strike = the unit stack on the boss cell', 'V: rails only', 'wr2_boss.armor_and_strike'),
 'ring_unit_wide6': ('A: seamed band, end caps, token at the start cap', 'Bowl band with a seam, square lane-colour caps, the token at the start cap by the placement rule, HP trays on every sector axis', 'V: head chevron at the clockwise end', 'wr2_latent.wide6'),
}

ORDER2 = [e[0] for e in CFG.EL]
