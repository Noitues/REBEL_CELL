s = open('a2_hover.py').read()
a = """    anc = (tp[0] + (st[0] - tp[0]) / d * 20, tp[1] + (st[1] - tp[1]) / d * 20)
    mid = (st[0] - 34, st[1])
    pl = [anc, (mid[0] - 40, st[1] + (anc[1] - st[1]) * 0.1), mid, st]
"""
b = """    mid = (st[0] - 34, st[1])
    base_ang = math.atan2(st[1] - tp[1], st[0] - tp[0])
    bad = [(AU.badge_xy(u, AU.BADGE_D, e_['side']), e_['size'] / 2.0 + 2.5 + 3.3 + 6.0) for e_ in AU.BADGE_LOG if e_['uid'] == u['id']]

    def _path(ang):
        an = (tp[0] + math.cos(ang) * 20, tp[1] + math.sin(ang) * 20)
        return an, [an, (mid[0] - 40, st[1] + (an[1] - st[1]) * 0.1), mid, st]

    def _clear(pl_):       # assembly: layout-aware, the wax leader (6.5 px casing + anchor dot) keeps off the unit's badge
        for (bp, rr) in bad:
            for i in range(len(pl_) - 1):
                (x1, y1), (x2, y2) = pl_[i], pl_[i + 1]
                for t in [k / 40.0 for k in range(41)]:
                    if math.hypot(x1 + (x2 - x1) * t - bp[0], y1 + (y2 - y1) * t - bp[1]) < rr:
                        return False
        return True
    anc, pl = _path(base_ang)
    for dg in (0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90, 110, -110, 130, -130):
        an_, pl_ = _path(base_ang + math.radians(dg))
        if _clear(pl_):
            anc, pl = an_, pl_
            break
"""
assert a in s
s = s.replace(a, b)
open('a2_hover.py','w').write(s)
t = open('r2_sched.py').read()
a = "arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + NAMES[k].split()[0], 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)\n\n\n"
assert a in t
t = t.replace(a, a.replace('a0 + 25', 'a0 + 27.2'))
open('r2_sched.py','w').write(t)
