p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:90])
    t = t.replace(old, new)


rep("        chevrons(L, u, u['hit'])\n        if u['warded']:", """        grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
        chevrons_h(L, u, u['hit'], grow)
        if u['warded']:""")
rep("    bg.alpha_composite(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS))",
    "    bg.alpha_composite(grade_units(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS), f, keep_all=(beat == 'p2')))")
rep("    wave_arcs(L, arcs_data(f))\n", "    wave_arcs10(L, arcs_data(f))\n")
rep("    adjuster_satellite(L, f['adj'])\n    if beat != 'p2b':\n        rim_chips(L, f)\n",
    "    adjuster_body(L, f['adj'])\n    if beat != 'p2b':\n        landing_arcs(L, f)\n    else:\n        landing_arcs(L, f, only={J['hover']['id']})\n")
rep("    ring_tags(L, f)\n    nudge_ghost(L)\n", """    ring_tags(L, f)
    nudge_ghost(L)
    if beat in ('p2', 'p3'):
        twist_badge(L, f)
        refund_marks(L, f)
""")
rep("def ring_tags(L, f):", '''def twist_badge(L, f):
    """the Twist played this turn: a yellow twist badge on its ring's tag (ring +1 turns one extra sector clockwise at END TURN)"""
    ring, dirn = f['twr']
    if not dirn:
        return
    ri, ro = CB.ring_geom(ring)
    x, y = ppx(C, (ri + ro) / 2, 30)
    lane = LANE[ring]
    s = lane['name'] + (' W%d' % (f['rings_wave'][ring] + 1) if f['rings_wave'][ring] >= 0 else '')
    wd = L.tw(s, 17, 'anton') + 14
    bx, by = x + wd / 2 + 24, y
    L.ellipse([bx - 17, by - 17, bx + 17, by + 17], fill=(26, 22, 4, 250), outline=YEL, w=3)
    L.glyph('C_TWIST', 24, (bx, by), YEL)
    for q in (0, 1):
        xx = bx + 25 + q * 9
        L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], INK, 6.5)
        L.line([(xx - 4, by - 8), (xx + 4, by), (xx - 4, by + 8)], YEL, 3.4) if q == 0 or abs(dirn) > 1 else None


def refund_marks(L, f):
    """E10: a Trigger kill pays +1 RAM (once a turn): a gold burst on the killed unit's cell and a cyan RAM pip popping out of it"""
    if not f.get('refunds'):
        return
    kl = f['kills'][-1]
    ri, ro = CB.ring_geom(kl['dep'])
    x, y = ppx(C, (ri + ro) / 2, 60 * kl['sector'])
    burst(L, x, y, 14, 30, 12)
    ram_pip_pop(L, x + 30, y - 24)


def wave_arcs10(L, arcs):
    """FUTURE waves: thin arcs outside the landing lanes (compact: 19 px apart), unit glyphs on them, a W<n> tab staggered at the arc start"""
    r = 484
    fut = [a for a in arcs if a['state'] == 'future']
    for i, a in enumerate(fut):
        col_w = RED if a.get('climax') else ORANGE
        L.line(L.arc_pts(C, r, E8.ARC_START, E8.ARC_START + 359, 120), col_w + (235,), 3)
        ang = E8.ARC_START
        for (kind, w) in a['units']:
            a1 = ang + 60 * w
            kc = KCOL.get(kind, WHITE)
            m = (ang + a1) / 2
            x, y = ppx(C, r, m)
            L.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(10, 12, 22, 240), outline=kc, w=2)
            L.glyph(KIND[kind][1], 14, (x, y), WHITE)
            for q in range(1, w):
                x2, y2 = ppx(C, r, ang + 60 * q)
                L.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=WHITE + (200,))
            ang = a1
        if a.get('climax'):
            for k in range(E8.ARC_START, E8.ARC_START + 360, 14):
                L.line([ppx(C, r - 5, k), ppx(C, r + 5, k + 6)], (255, 226, 0, 190), 2.4)
        if NOW['words']:
            x, y = ppx(C, r, E8.ARC_START - 3.6 - 3.2 * i)
            lab = 'W%d' % (a['wave'] + 1)
            L.rect([x - 22, y - 11, x + 22, y + 11], fill=(8, 10, 18, 255), outline=col_w, w=2, r=5)
            L.text((x, y + 1), lab, 16, 'mono', fill=col_w)
        r += 19


def ring_tags(L, f):''')
open(p, 'w').write(t)
print('ok')
