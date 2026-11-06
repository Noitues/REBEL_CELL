"""ed_loud.py: one-off edit of mp_eff.py / mp_lib.py for review 2.10 (loudness order damage > kill > block > state on one shared meter)"""
P = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/'


def rep(path, pairs):
    s = open(P + path, encoding='utf-8').read()
    for a, b, n in pairs:
        c = s.count(a)
        assert c == n, (path, c, n, a[:70])
        s = s.replace(a, b)
    open(P + path, 'w', encoding='utf-8').write(s)


rep('mp_lib.py', [
    ("def arrow(L, pts, col, w=5.0, head=15.0, casing=4.0, a=255, hl=None):",
     "# review 2.10: the motion arrows are a state change's own light, so they sit under every block, kill and hit: 3 px core, 2.5 px ink casing,\n"
     "# 11 px head (were 5 / 4 / 15), and on the spin, twist, shove and rings step they are a stub that runs ahead of the moving cell\n"
     "AW, AH, AC = 3.0, 11.0, 2.5\n\n\n"
     "def arrow(L, pts, col, w=AW, head=AH, casing=AC, a=255, hl=None):", 1),
])
rep('mp_eff.py', [
    ("ECHO_A = (0.55, 0.34, 0.17)\nECHO_LAG = (26, 52, 78)\nECHO_U = (0.42, 0.26, 0.13)\n",
     "# review 2.10 (2026-11-03 rebuild): the motion echoes are retired.  On the shared gated meter (fxk_lib.loud_frame, ref = the marks-off\n"
     "# frame, end = the settled frame) they were the loudest light of every M effect (spin 48 134 -> 2 090 without them, twist 11 747 ->\n"
     "# 1 076, pull 2 741 -> 371, shove 2 708 -> 1 008), so a state change outshouted every hit.  The eased motion carries the read.\n"
     "ECHO_A = ()\nECHO_LAG = ()\nECHO_U = ()\n"
     "ARROW_STUB = dict(spin=60.0, twist=30.0, shove=30.0, rings=40.0)     # deg: the arrow runs this far ahead of the moving cell\n", 1),
    ("        if marks and sp > 0.02:\n", "        if marks and sp > 0.02 and ECHO_A:\n", 2),
    ("PINK, 5.0, 15.0, 4.0", "PINK, AW, AH, AC", 9),
    (", 5.0, 15.0, int(255", ", AW, AH, int(255", 4),
    # spin stub
    ("            arrow(L, arc_pts(R_, 6, 180), PINK, AW, AH, AC, int(255 * al))",
     "            arrow(L, arc_pts(R_, 6, 6 + ARROW_STUB['spin']), PINK, AW, AH, AC, int(255 * al))", 1),
    ("            tail = 6 + spin_ang(t)\n", "            tail = 6 + spin_ang(t)\n            head = min(head, tail + ARROW_STUB['spin'])\n", 1),
    # twist stub
    ("                arrow(L, arc_pts(299.5, c0 + 4, c0 + 60), PINK, AW, AH, AC, int(255 * al))",
     "                arrow(L, arc_pts(299.5, c0 + 4, c0 + 4 + ARROW_STUB['twist']), PINK, AW, AH, AC, int(255 * al))", 1),
    ("                tail = c0 + 4 + twist_ang(t)\n", "                tail = c0 + 4 + twist_ang(t)\n                head = min(head, tail + ARROW_STUB['twist'])\n", 1),
    # shove stub
    ("            arrow(L, arc_pts(299.5, 4, 60), PINK, AW, AH, AC, int(255 * al))",
     "            arrow(L, arc_pts(299.5, 4, 4 + ARROW_STUB['shove']), PINK, AW, AH, AC, int(255 * al))", 1),
    ("            tail = 4 + shove_ang(t)\n", "            tail = 4 + shove_ang(t)\n            head = min(head, tail + ARROW_STUB['shove'])\n", 1),
    # rings stub
    ("            clock_arrow(L, arc_pts(426.5, 3, 117), AW, AH, int(255 * al))",
     "            clock_arrow(L, arc_pts(426.5, 3, 3 + ARROW_STUB['rings']), AW, AH, int(255 * al))", 1),
    ("            tail = 3 + 114 * step_k(t)\n", "            tail = 3 + 114 * step_k(t)\n            head = min(head, tail + ARROW_STUB['rings'])\n", 1),
    # hold: stamp hands over to the printed glyph earlier, thinner lip
    ("        L.poly(band_pts(386, 424, front - 1.2, front + 0.4, 0.4), GUN_LIP, INK, 1.4, int(255 * (1 - seg(t, 400, 420))))",
     "        L.poly(band_pts(386, 424, front - 0.6, front + 0.2, 0.2), GUN_LIP, INK, 1.0, int(255 * (1 - seg(t, 400, 420))))", 1),
    ("    al = clamp01(seg(t, 0, 40)) * (1 - seg(t, 420, 560))\n", "    al = clamp01(seg(t, 0, 40)) * (1 - seg(t, 200, 320))\n", 1),
    # wave feed chevrons
    ("                L.line(pts, INK, 8.0, int(255 * lit_al))\n                L.line(pts, ENAMEL, 4.0, int(255 * lit_al))",
     "                L.line(pts, INK, 6.0, int(255 * lit_al))\n                L.line(pts, ENAMEL, 2.5, int(255 * lit_al))", 1),
    # trace: one glitch band per step, lower pop
    ("        rows = [(int(rr.integers(card_box[1] + 6, card_box[3] - 20)), int(rr.integers(5, 11)), int(rr.choice([-6, 6]))) for _ in range(3)]",
     "        rows = [(int(rr.integers(card_box[1] + 6, card_box[3] - 20)), int(rr.integers(4, 8)), int(rr.choice([-6, 6]))) for _ in range(TR_ROWS)]", 1),
    ("        scale = [1.7, 1.35, 1.0, 1.0][stp]", "        scale = TR_POP[stp]", 1),
    ("TR_CARD = (1267, 762, 1476, 1052)        # the Trigger card in the p1 hand (generator mask card_2)\n",
     "TR_CARD = (1267, 762, 1476, 1052)        # the Trigger card in the p1 hand (generator mask card_2)\n"
     "TR_ROWS = 1                              # review 2.10: one glitch band per 33 ms step (was 3, 5-11 px; now 4-7 px)\n"
     "TR_POP = [1.45, 1.2, 1.0, 1.0]           # the pip's stepped pop (was 1.7, 1.35)\n", 1),
    # P: no wedge tint, no soak wash; smaller plate; brace corner brackets; thinner lane
    ("SH_A = 60.0 ", "BLOCK_TINT = 0.0             # review 2.10: the flat pink wedge tint is retired (a block sits under a kill), as on the C/D/H/L sheet\n"
     "SOAK_WASH = 0.0              # the same for the SOAK wash on the wedge\nSH_A = 60.0 ", 1),
    ("        tint_al, chev_al = 0.14 * pa, pa", "        tint_al, chev_al = 0.14 * BLOCK_TINT * pa, pa", 1),
    ("        tint_al = 0.14 * seg(t, 160, 190) * (1 - seg(t, 440, 600))", "        tint_al = 0.14 * BLOCK_TINT * seg(t, 160, 190) * (1 - seg(t, 440, 600))", 1),
    ("SH_R = (174.0, 204.0, 23.0)  # plate r_in, r_out, half angle: outside the slice pips (r 163-171), over the trim band",
     "SH_R = (186.0, 204.0, 13.0)  # plate r_in, r_out, half angle: outside the slice pips (r 163-171), on the trim band (review 2.10: was 174-204 x 23 deg)", 1),
    ("        fk, wash, f_al, pip_k, flow, chev = 1.0, 0.14 * k, k, 1.0, 0.25, None", "        fk, wash, f_al, pip_k, flow, chev = 1.0, 0.14 * SOAK_WASH * k, k, 1.0, 0.25, None", 1),
    ("        wash = 0.14 * seg(t, 220, 250) * (1 - seg(t, 470, 600))", "        wash = 0.14 * SOAK_WASH * seg(t, 220, 250) * (1 - seg(t, 470, 600))", 1),
    ("        L.line(pts, INK, 7.0, int(255 * lane_al))\n        L.line(pts, HARM, 3.0, int(255 * lane_al))",
     "        L.line(pts, INK, 5.0, int(255 * lane_al))\n        L.line(pts, HARM, 2.0, int(255 * lane_al))", 1),
    ("""        mid = band_pts(r0 + 4.5, r1 - 4.5, a0 + 2.2, a1 - 2.2, 1.0)
        mid_c = sc(mid) + [sc(mid)[0]]
        Lc.line(mid_c, INK, 12.5)
        Lc.line(mid_c, P_STOCK, 8.0)
        for off in (-2.2, 2.2):
            mm = band_pts(r0 + 4.5 + off, r1 - 4.5 - off, a0 + 2.2 + off / 100 * 57.3, a1 - 2.2 - off / 100 * 57.3, 1.0)
            mm = sc(mm) + [sc(mm)[0]]
            Lc.line(mm, PINK, 1.2)
        for p_ in sc([ppx(r1 - 4.5, a0 + 2.6), ppx(r1 - 4.5, a1 - 2.6), ppx(r0 + 6.5, a0 + 9), ppx(r0 + 6.5, a1 - 9)]):""",
     """        # review 2.10: four clamp brackets on the wedge corners (was a P-stock frame round the whole wedge, louder than a kill)
        ro, ri, ao0, ao1 = r1 - 4.5, r0 + 4.5, a0 + 2.2, a1 - 2.2
        arm_o, arm_i = BR_ARM / ro * 57.3, (BR_ARM + 6) / ri * 57.3
        brackets = [[ppx(ro - BR_ARM, ao0), ppx(ro, ao0)] + arc_pts(ro, ao0, ao0 + arm_o, 0.5),
                    [ppx(ro - BR_ARM, ao1), ppx(ro, ao1)] + arc_pts(ro, ao1 - arm_o, ao1, 0.5)[::-1],
                    [ppx(ri + BR_ARM, ao0 + 6.5), ppx(ri, ao0 + 6.5)] + arc_pts(ri, ao0 + 6.5, ao0 + 6.5 + arm_i, 0.5),
                    [ppx(ri + BR_ARM, ao1 - 6.5), ppx(ri, ao1 - 6.5)] + arc_pts(ri, ao1 - 6.5 - arm_i, ao1 - 6.5, 0.5)[::-1]]
        for bk in brackets:
            Lc.line(sc(bk), INK, 9.0)
        for bk in brackets:
            Lc.line(sc(bk), P_STOCK, 4.5)
        for p_ in sc([ppx(ro, ao0), ppx(ro, ao1), ppx(ri, ao0 + 6.5), ppx(ri, ao1 - 6.5)]):""", 1),
    ("BR_STAMP = (435.0, 125.9)", "BR_ARM = 24.0                # px: each clamp bracket's arms\nBR_STAMP = (435.0, 125.9)", 1),
])
print('ok')
