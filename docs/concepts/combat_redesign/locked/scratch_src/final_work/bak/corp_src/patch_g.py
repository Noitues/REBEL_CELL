p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/e10lib.py'
t = open(p).read()
i = t.index('# ----------------------------------------------------------------------------- landing arcs (PL10 ask 1)')
head = t[:i]
new = '''# ----------------------------------------------------------------------------- landing arcs (PL10 ask 1)
LANE_R = [425, 460, 495]
HALF = 15
CP = 17           # chevron pitch (px along the arc)
DP = 19           # diamond pitch


def _land_start(secs):
    ss = set(secs)
    for s0 in range(6):
        if {(s0 + i) % 6 for i in range(len(ss))} == ss:
            return s0
    return min(ss)


def _diamond(L, x, y, col, r=8):
    L.poly([(x, y - r - 1.5), (x + r, y), (x, y + r + 1.5), (x - r, y)], fill=col, outline=INK, w=2)


def _check(L, x, y):
    L.line([(x - 8, y + 1), (x - 2, y + 7), (x + 9, y - 7)], INK, 7)
    L.line([(x - 8, y + 1), (x - 2, y + 7), (x + 9, y - 7)], GREEN, 3.8)


def _chev_arc(L, r, ang, da, hollow, col=REDC):
    """one chevron on the arc at angle `ang`, pointing inward (toward the tower)"""
    h = 9 * da
    p = [ppx(C, r + 7, ang - h), ppx(C, r - 6, ang), ppx(C, r + 7, ang + h)]
    if hollow:
        L.line(p, INK, 11)
        L.line(p, col, 7)
        L.line(p, (8, 5, 12), 3.2)
    else:
        L.line(p, INK, 9.5)
        L.line(p, col, 5.4)


def landing_arcs(L, f, only=None, words=True):
    """one bezel arc per landing unit (alive, lands within 3 turns after our guns), spanning its landing sectors, drawn clockwise from its first sector.
    On the arc: [kind glyph][wear][twist][dots = turns until, red dot = this END TURN] then, per landing sector, [solid red chevrons = hit at landing + hollow = growth to come]
    [red diamonds = HP through] (cream clamp = braced, orange chevron = soaked pip, green check = nothing through). Arcs pack into the fewest radial lanes."""
    items = []
    for u in f['units']:
        if u['consumed'] or u['trigdead']:
            continue
        if only is not None and u['id'] not in only:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or 'land_hit' not in u:
            continue
        s0 = _land_start(u['land_sectors'])
        a0, a1 = 60 * s0 - 29, 60 * (s0 + u['w'] - 1) + 29
        items.append(dict(u=u, k=fz['k'], a0=a0, a1=a1, s0=s0))
    items.sort(key=lambda it: (it['k'], it['a0'] % 360))
    lanes = []
    for it in items:
        e0, e1 = it['a0'] % 360, it['a0'] % 360 + (it['a1'] - it['a0'])
        lane = 0
        while True:
            clash = False
            for (l_, g0, g1) in lanes:
                if l_ != lane:
                    continue
                for sh in (-360, 0, 360):
                    if e0 < g1 + 2 + sh and g0 + sh < e1 + 2:
                        clash = True
            if not clash:
                break
            lane += 1
        lanes.append((lane, e0, e1))
        it['lane'] = lane
    for it in items:
        u, k = it['u'], it['k']
        r = LANE_R[min(it['lane'], 2)]
        a0, a1 = it['a0'], it['a1']
        col_lane = LANE[u['dep']]['col']
        dash = LANE[u['dep']]['dash']
        da = 57.3 / r
        pts = L.band(C, r - HALF, r + HALF, a0, a1)
        L.poly(pts, fill=(7, 9, 17, 205), outline=None)
        L.line(pts + [pts[0]], INK, 6)
        L.line(pts + [pts[0]], col_lane, 2.6, dash=dash)
        # start cluster: glyph disc, wear mark, twist mark, dots
        gx, gy = ppx(C, r, a0 + 24 * da)
        kc = KCOL[u['kind']]
        L.ellipse([gx - 19, gy - 19, gx + 19, gy + 19], fill=tuple(int(v * 0.62) for v in kc) + (255,), outline=col_lane, w=2.8)
        L.glyph(KIND[u['kind']][1], 28, (gx, gy), WHITE)
        cur = 24 + 24
        if u.get('wear'):
            x_, y_ = ppx(C, r, a0 + (cur + 10) * da)
            L.rect([x_ - 9, y_ - 9, x_ + 9, y_ + 9], fill=GREEN, outline=INK, w=1.6, r=2)
            L.line([(x_ - 4, y_ - 9), (x_, y_ - 2), (x_ - 2, y_ + 2), (x_ + 4, y_ + 9)], WHITE, 2.2)
            cur += 28
        if f.get('twr') and f['twr'][1] and f['twr'][0] == u['dep'] and k > 0:
            x_, y_ = ppx(C, r, a0 + (cur + 12) * da)
            L.ellipse([x_ - 12, y_ - 12, x_ + 12, y_ + 12], fill=(30, 26, 6), outline=YEL, w=2.4)
            L.glyph('C_TWIST', 17, (x_, y_), YEL)
            cur += 30
        if k == 0:
            x_, y_ = ppx(C, r, a0 + (cur + 10) * da)
            L.ellipse([x_ - 8, y_ - 8, x_ + 8, y_ + 8], fill=REDC, outline=WHITE, w=2.2)
            cur += 24
        else:
            for i in range(k):
                x_, y_ = ppx(C, r, a0 + (cur + 7 + i * 14) * da)
                L.ellipse([x_ - 5, y_ - 5, x_ + 5, y_ + 5], fill=WHITE, outline=INK, w=1.4)
            cur += 14 * k + 4
        # per landing sector, centred on the sector
        ng = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
        ns = u['land_hit'] - ng
        for q in range(u['w']):
            sec = (it['s0'] + q) % 6
            th = 60 * (it['s0'] + q)
            thr = u['land_through'].get(str(sec), 0)
            sk = u['land_soak'].get(str(sec), 0)
            br = u['land_brace'].get(str(sec), 0)
            n_items = ns + ng
            wch = n_items * CP
            wdi = (thr * DP) + (sk * 15) + (24 if br else 0) + (24 if (not thr and not br and not sk) else 0)
            tot = wch + 16 + wdi
            x0 = -tot / 2
            if q == 0:
                x0 = max(x0, (cur - 24) - 29 * (r / 57.3) * 0 + 0) if False else x0
            for i in range(n_items):
                _chev_arc(L, r, th + (x0 + CP / 2 + i * CP) * da, da, hollow=i >= ns)
            x1 = x0 + wch + 16
            if br:
                xx_, yy_ = ppx(C, r, th + (x1 + 12) * da)
                L.glyph('C_BRACE', 24, (xx_, yy_), CREAM)
                x1 += 24
            for i in range(thr):
                xx_, yy_ = ppx(C, r, th + (x1 + DP / 2 + i * DP) * da)
                _diamond(L, xx_, yy_, REDC)
            x1 += thr * DP
            for i in range(sk):
                ang_i = th + (x1 + 7.5 + i * 15) * da
                p = [ppx(C, r + 6, ang_i - 6.5 * da), ppx(C, r - 5, ang_i), ppx(C, r + 6, ang_i + 6.5 * da)]
                L.line(p, INK, 8.5)
                L.line(p, SOAK_C, 5)
            x1 += sk * 15
            if not thr and not br and not sk:
                xx_, yy_ = ppx(C, r, th + (x1 + 12) * da)
                _check(L, xx_, yy_)
    return items
'''
open(p, 'w').write(head + new)
p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()
t = t.replace("    r = 484\n    fut = [a for a in arcs if a['state'] == 'future']", "    r = 524\n    fut = [a for a in arcs if a['state'] == 'future']")
t = t.replace("        r += 19\n", "        r -= 17\n")
t = t.replace("L.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(10, 12, 22, 240), outline=kc, w=2)\n            L.glyph(KIND[kind][1], 14, (x, y), WHITE)", "L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 12, 22, 240), outline=kc, w=2)\n            L.glyph(KIND[kind][1], 13, (x, y), WHITE)")
t = t.replace("seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 5, 12, pitch=7)", "seg_run(L, xx, y + 22, 'gold', f['adj']['hp'], 4, 12, pitch=6)")
open(p, 'w').write(t)
