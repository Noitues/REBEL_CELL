p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
old = s[s.index("def focus_slice(L, s, thick=False):"):s.index("def focus_col(")]
new = '''CORNER_LOG = []


def _forbid(strict):
    m = np.zeros((H, W), bool)
    for c in MARKS + (('units',) if strict else ()):
        if c in MASKS:
            m |= MASKS[c]
    return m


def safe_corners(L, ri, ro, a0, a1, w=2.0, leg=LEG, tag=''):
    """FOCUS corners on a ring band, one corner at a time: a corner that would touch a board mark (digit, label, tag, badge, ticket) or a unit
    slides inward along the band (up to 12 deg / 8 px); if it never clears, it is left out and logged"""
    forb_s, forb = _forbid(True), _forbid(False)
    for r, dr in ((ri, 1), (ro, -1)):
        for a, da in ((a0, 1), (a1, -1)):
            done = False
            for forbid, lab in ((forb_s, 'clear'), (forb, 'over_unit')):
                for k in range(0, 9):
                    rr = r + dr * k * 1.0
                    aa = a + da * k * 1.5
                    T = L2()
                    poly = [ppx(C, rr + dr * leg, aa), ppx(C, rr, aa)] + [ppx(C, rr, aa + da * math.degrees(leg / rr) * i / 4) for i in range(1, 5)]
                    HL._ink_then(T, [poly], LIME, w)
                    im = T.done()
                    m = np.asarray(im.split()[3]) >= 40
                    if not (m & forbid).any():
                        L.im.alpha_composite(T.im)
                        CORNER_LOG.append(dict(tag=tag, r=round(r), a=round(a, 1), slide=k, ok=lab))
                        done = True
                        break
                if done:
                    break
            if not done:
                CORNER_LOG.append(dict(tag=tag, r=round(r), a=round(a, 1), slide=None, ok='dropped'))


def focus_slice(L, s, thick=False):
    HL.band_corners(L, T_IN + 4, T_PAGE - 4, 60 * s - 26.5, 60 * s + 26.5, w=3.5 if thick else 2.0, leg=LEG)


def focus_cell(L, u, thick=False):
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    safe_corners(L, ri + 3.5, ro - 3.5, a0 + 2.5, a1 - 2.5, w=3.5 if thick else 2.0, tag='unit %d' % u['id'])


def focus_adj(L, f, thick=False):
    a = f['adj']
    ri, ro = CB.ring_geom(a['ring'])
    safe_corners(L, ri + 3.5, ro - 3.5, 60 * a['s'] - 27.5, 60 * a['s'] + 27.5, w=3.5 if thick else 2.0, tag='adjuster')


'''
s = s.replace(old, new)
s = s.replace("def reset_checks():\n    MASKS.clear()", "def reset_checks():\n    CORNER_LOG.clear() if 'CORNER_LOG' in globals() else None\n    MASKS.clear()")
open(p, 'w', encoding='utf-8').write(s)
p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_plates.py'
s = open(p, encoding='utf-8').read()
s = s.replace("lift_dx=Z.HOV.get('dx'), lift_cy=Z.HOV.get('lift_cy'))", "lift_dx=Z.HOV.get('dx'), lift_cy=Z.HOV.get('lift_cy'), corners=list(Z.CORNER_LOG))")
# trigger arrows clear of the tokens
s = s.replace("            ang = 60 * e[1] - 15\n", "            ang = 60 * e[1] + 12\n")
# strike burst along the ring, off the token
s = s.replace("""        x, y = AU.token_pos(lv)
        pink_burst(L, x + 30, y - 4, 22, 5)
        HL.speed_lines(L, x + 30, y - 4, 120, 5, 26, 52, PINK)""", """        x, y = AU.token_pos(lv)
        ta = math.degrees(math.atan2(x - C[0], -(y - C[1])))
        bx, by = ppx(C, math.hypot(x - C[0], y - C[1]), ta + 9.5)
        pink_burst(L, bx, by, 20, 5)
        HL.speed_lines(L, bx, by, math.degrees(math.atan2(by - y, bx - x)) + 180 + 90, 5, 24, 46, PINK)""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
