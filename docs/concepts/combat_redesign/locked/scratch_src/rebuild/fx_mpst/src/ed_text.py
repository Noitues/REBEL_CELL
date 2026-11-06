"""ed_text.py: one-off text pass on mp_eff.py: the spec texts (still, keep, keys, phases, reduce notes) follow the review 2.10 changes
(no echoes, arrow stubs, no wedge tint or SOAK wash, smaller shield plate, brace clamp brackets, Hold stamp hand-over)"""
import re
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py'
s = open(P, encoding='utf-8').read()


def block(fid):
    a = s.index("reg(dict(id='%s'" % fid)
    b = s.index("render=", a)
    return a, b


def set_field(fid, field, value):
    global s
    a, b = block(fid)
    blk = s[a:b]
    m = re.search(r"(\b%s=)'((?:[^'\\]|\\.)*)'" % field, blk)
    assert m, (fid, field)
    v = value.replace("'", "\\'")
    blk = blk[:m.start()] + m.group(1) + "'" + v + "'" + blk[m.end():]
    s = s[:a] + blk + s[b:]


def sub_in(fid, old, new):
    global s
    a, b = block(fid)
    blk = s[a:b]
    assert blk.count(old) == 1, (fid, old[:50])
    s = s[:a] + blk.replace(old, new) + s[b:]


set_field('fx_spin', 'still', "The tower annulus (r 64-211) turns 180 deg; the hub (BREAKER, HP ring) stays put and every slice icon stays upright; a 60 deg pink arrow stub in the gap between the tower and ring NOW runs ahead of slice 0 and is eaten as it arrives. No echoes (review 2.10).")
set_field('fx_spin', 'keep', "pink arrow stub (resolve colour), 3 px with an ink casing; icons upright at rest; the hub never turns; no echoes.")
sub_in('fx_spin', "(240, 'turning, echoes')", "(240, 'turning')")
set_field('fx_spin', 'reduce_note', "No sweep: the arrow stub appears whole (100 ms), the tower dissolves from 0 to 180 deg over 300 ms (easeInOut), the arrow fades (120 ms). Icons and hub as in full motion.")

set_field('fx_twist', 'still', "Ring +1 (r 271-328) turns 60 deg clockwise with its cells, tokens and the Adjuster; the ring tags stay put; each unit on it gets a 30 deg pink arrow stub that runs ahead of the cell along the ring and is eaten as it arrives. No echoes (review 2.10). The corp ring material turns with the ring.")
set_field('fx_twist', 'keep', "pink arrow stub along the ring; the ring tags never travel; no echoes; the hover form (preview) is the same arrow in pencil yellow (hover plates).")
sub_in('fx_twist', "(320, 'echoes')", "(320, 'arriving')")
set_field('fx_twist', 'reduce_note', "The arrow stubs appear whole (100 ms), the ring dissolves from 0 to 60 deg over 300 ms, the arrows fade (120 ms).")

set_field('fx_pull', 'still', "The whole cell (lit glass, token, tray) slides 57 px inward along the sector axis; a pink radial arrow from the cell to its new ring is eaten as the cell moves; the empty glass is left behind. No echoes (review 2.10).")
set_field('fx_pull', 'keep', "pink arrow pointing inward (resolve colour); no echoes; the hover form is pencil yellow.")
sub_in('fx_pull', "(280, 'echoes')", "(280, 'arriving')")
set_field('fx_pull', 'reduce_note', "The arrow appears (100 ms), the cell dissolves from ring +2 to ring +1 over 300 ms, the arrow fades (120 ms).")

set_field('fx_shove', 'still', "The cell slides one sector clockwise along its ring; a 30 deg pink arrow stub runs ahead of it and is eaten as it arrives; the ring tags stay put. No echoes (review 2.10).")
set_field('fx_shove', 'keep', "pink arrow stub along the ring; no echoes; the hover form is pencil yellow.")
sub_in('fx_shove', "(280, 'echoes')", "(280, 'arriving')")
set_field('fx_shove', 'reduce_note', "The arrow stub appears (100 ms), the cell dissolves into the next sector over 300 ms, the arrow fades (120 ms).")

set_field('fx_rings_step', 'still', "After GUNS and LANDS (ring NOW is clear, the old landing arcs are gone): every unit cell on rings +1 and +2 spirals one ring in and 120 deg round; a 32 deg SCHEDULE-orange arrow stub runs ahead of them along the +2 THIS TURN tape and is eaten as they arrive. No echoes (review 2.10).")
set_field('fx_rings_step', 'keep', "SCHEDULE orange only (the clock moves the rings, VISUAL_PLAN E; never pink and never the corp colour); no echoes; the hand-off order GUNS > LANDS > RINGS STEP.")
set_field('fx_rings_step', 'reduce_note', "No spiral: the arrow stub appears (100 ms), every cell dissolves from its old place to its new one over 300 ms, the arrow fades (120 ms).")

set_field('fx_hold', 'still', "A gunmetal hourglass stamp (the clock's own material) slams onto the live cell and hands over to the printed HOLD glyph; a 22 deg SCHEDULE-orange arrow stub runs the hold slot (40 deg) along the tape; the band turns over clockwise behind a thin gunmetal lip edge into the new schedule (HOLD THIS TURN, +2 NEXT, HOLD THEN).")
set_field('fx_hold', 'keep', "gunmetal stamp with the hourglass, SCHEDULE arrow stub (Hold's slide is the clock moving, VISUAL_PLAN E); the turned-over cells are the generator's own schedule drawing.")
sub_in('fx_hold', "timing=dict(phases=[('stamp slams', 0, 100, 'easeOutBack 2.2'), ('band turns over', 100, 420, 'easeInOutCubic'), ('settle: stamp hands over to the printed HOLD glyph', 420, 560, 'linear')], total=560)",
       "timing=dict(phases=[('stamp slams', 0, 100, 'easeOutBack 2.2'), ('stamp hands over to the printed HOLD glyph', 120, 220, 'linear'), ('band turns over, arrow stub runs the slot', 100, 420, 'easeInOutCubic'), ('arrow fades', 420, 560, 'linear')], total=560)")

set_field('fx_wave_enter', 'still', "The feed arrow lights (ENAMEL, the queue is K), the W4 ticket lifts and rides the arrow into the bezel entry, a scan line in the corp's cell-edge hue draws each new ring +2 cell (lit ring +2 glass, enamel outline), the Jammer glyphs drop in, and W5 / W6 move up one slot. No echoes (review 2.10).")
set_field('fx_wave_enter', 'keep', "the corp hue only on the scan line that draws the new cell edges (DR-6: rim, lip, crest, cell edges); the feed arrow neutral; solid ticket edges, no dashes.")
set_field('fx_wave_enter', 'reduce_note', "No travel: the W4 ticket fades out, the new cells fade in with their outlines and glyphs, and W5 / W6 cross-fade one slot right, all over 300 ms.")

set_field('fx_shield_block', 'still', "The two incoming chevrons run down the sector axis across the corp rings and stop dead on one small intact plate of the P stock (pink-tinted paper #F6C8DE, fibre grain) seated on the trim band of the wedge (r 186-204 x 26 deg, clear of the icon and the pips); paper spark ticks fly back; two engraved ticks = absorbed 2. No wedge tint, no red on the plate, no glow, no starburst (review 2.10, 3.10).")
set_field('fx_shield_block', 'keep', "ONE intact plate (never cracked), its own pink-tinted paper stock with fibre grain (never card bone), ink key line + pink double line + rivets, hard offset shadow, paper sparks, no red on the plate, no glow; a block sits under every kill and hit (review 2.10).")
sub_in('fx_shield_block', "('plate, tint, ticks and stopped chevrons appear', 0, 200, 'linear')", "('plate, ticks and stopped chevrons appear', 0, 200, 'linear')")
set_field('fx_shield_block', 'reduce_note', "No slam and no sparks: the plate, its ticks and the two chevrons stopped at the plate edge appear over 200 ms (linear), hold, and dissolve over 300 ms (linear); no hard shadow in reduce motion (with it the reduce form counted 2 flashes per s, the full form 1).")

set_field('fx_brace_block', 'still', "The landing lane runs from the arc down the sector axis to the tower; four clamp brackets of the P stock (ink key, rivets, fibre, hard shadow) close on the corners of the TURRET wedge with the icon left clear; the three chevrons (braced 3) stop on a flat stop bar and crumple; a clamp stamp slams onto the board's brace glyph on the arc and hands over to it.")
set_field('fx_brace_block', 'keep', "the clamp brackets hold the whole wedge at its four corners, icon visible; the lane stops at the bar (never through); P stock, not card bone; the stamp lands on the printed brace glyph; a block sits under every kill and hit (review 2.10).")
sub_in('fx_brace_block', "('clamp closes (1.12 to 1.0)', 60, 180, 'easeOutBack 2.0')", "('clamp brackets close (1.12 to 1.0)', 60, 180, 'easeOutBack 2.0')")
sub_in('fx_brace_block', "('stamp slams on the arc glyph', 330, 400, 'easeOutBack 2.2')", "('stamp slams on the arc glyph (1.2 to 1.0)', 330, 400, 'easeOutBack 2.2')")

set_field('fx_soak_take', 'still', "The overflow chevron reaches the rim; a symmetric SOAK-blue funnel (ink key, P-stock inner line) draws in on the wedge axis from the rim toward the icon; the chevron shrinks into the mouth and turns SOAK; P-stock flow chevrons run inward; the soaked pip fills SOAK and hands over to the board's own SOAK hatch. No SOAK wash on the wedge (review 2.10).")
sub_in('fx_soak_take', "('funnel, wash and pip fill lift off', 470, 600, 'linear')", "('funnel and pip fill lift off', 470, 600, 'linear')")
sub_in('fx_soak_take', "('funnel, wash and filled pip appear', 0, 200, 'linear')", "('funnel and filled pip appear', 0, 200, 'linear')")
set_field('fx_soak_take', 'reduce_note', "No travel: the funnel and the filled pip appear over 200 ms with the flow chevrons still, hold, and dissolve over 300 ms. The overflow chevron is not shown.")

set_field('fx_trace_add', 'still', "One violet stepped glitch band (4-7 px) per 33 ms step shears the Trigger card (6 px offset, R/B split, scanlines) for five steps; then the fourth TRACE pip pops in three stepped scales (1.45, 1.2, 1.0) with a one-band glitch on the TRACE row and settles as the HUD's own lit pip.")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
