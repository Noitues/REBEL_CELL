import re
s = open('p1_final.py').read()


def repl(name, new):
    global s
    m = re.search(r'\ndef %s\(' % name, s)
    assert m, name
    a = m.start() + 1
    n = re.search(r'\n(def |UI = |OPTS = |DOWN_FRAC)', s[m.end():])
    b = m.end() + n.start() + 1
    s = s[:a] + new.strip('\n') + '\n\n\n' + s[b:]


repl('tile_anchor', '''
TILE_LOG = []      # beat / site -> distance from the Site tower top to the tile centre (px at 1920 scale); verified 34..64


def tower_top(w, sid):
    s = w.sites[sid]
    return np.array([s['B'][0], s['B'][1] - {1: 27, 2: 35, 3: 44}[s['tier']] * 3.73])
''')
repl('tile', '''
def tile(cv, w, sid, tier, num=None, off=(0, -52), r=30, k=1.0, tag=''):
    """P3 tile: centre = the Site tower top + off (|off| must be 34..64 px so the tile is on its own Site), hairline leader from the tower top."""
    top = tower_top(w, sid)
    d = float(np.hypot(*off))
    assert 34.0 <= d <= 64.0, (sid, off, d)
    c = top + np.array(off, float)
    TILE_LOG.append(dict(beat=tag, site=sid, tier=tier, dist_px=round(d, 1), r=r, centre=[round(float(c[0]), 1), round(float(c[1]), 1)]))
    u = (top - c) / max(np.hypot(*(top - c)), 1e-6)
    if d > r + 5:
        hy.leader(cv, c + u * (r + 2), top + np.array([0, -2]), k=.8)
    shadow(cv, c, r + 6)
    p2_ui.tile(cv, c, tier, num, r=r, k=k)
    return c
''')
repl('ground_marks', '''
def occluder(B):
    """ground marks hide behind buildings: a pixel hides a ground object when height above ground > 1.5 BU and class building (the contract)."""
    geo = BLD.static()[0]
    m = ((geo['idm'] == 2) & (geo['hag'] > 1.5)).astype(np.float32)
    return pblur(m, 0.7)


def ground_marks(beat, cv, B, w):
    """ground-level marks drawn BEFORE the heads: the DOWN clock as a drained ring (pressure before the hit). Hidden behind buildings (P3)."""
    if beat in DOWN_FRAC:
        orig = cv.img.copy()
        p2_ui.drain_ring(cv, w.sites['t1_a']['B'] + np.array([0, 2]), DOWN_FRAC[beat], r=50)
        if beat == 'aftermath':
            p2_ui.drain_ring(cv, w.sites['t1_b']['B'] + np.array([0, 2]), .62, r=50)
        occ = occluder(B)[..., None]
        cv.img = cv.img * (1 - occ) + orig * occ
''')
repl('ui_forecast', '''
def ui_forecast(cv, B, w):
    locks_big(cv, w, k=.9)
    ui.hunter_eye(cv, (1030, 300), 40, .7, col=WHITE * .92 + LATT * .08)
    tile(cv, w, 't1_c', 'HOLDS', None, off=(-34, -44), r=44, tag='forecast')
    tile(cv, w, 't1_b', 'SITES_LOST', 1, off=(34, -50), r=44, tag='forecast')
    tile(cv, w, 't2_intel', 'UNTOUCHED', None, off=(0, -56), r=44, tag='forecast')
    hy.home_chip(cv, w.home, 6)
    hy.tally(cv, (w.home[0] + 10, w.home[1] + 150), hb.TALLY, r=17, gap=34, group_gap=14)
    hy.hand(cv, hb.HAND, y=992)
    hy.hud(cv, 44, 50, 80, 8, 0)
''')
repl('ui_impact', '''
def ui_impact(cv, B, w):
    sid = B.ui['site']
    tc = w.sites[sid]['B']
    ui.bits(cv, tc + np.array([4, -40]), TYPE_COL['D'] * .6 + WHITE * .4, n=40, r=140, seed=4)
    tile(cv, w, sid, 'HOLDS', None, off=(48, -38), r=36, tag='impact')
    tile(cv, w, 't1_b', 'SITES_LOST', 1, off=(34, -50), r=34, k=.95, tag='impact')
    hy.hud(cv, 44, 50, 80, 8, 0)
''')
repl('ui_aftermath', '''
def scorch_route(cv, B, rid, upto=None, seed=1, k=1.0):
    """burnt remnant of a beam: ink-black charred segments with ember ends along the route, broken by gaps (the beam is gone, the street is not)."""
    p = np.asarray(B.ui['route_px'][rid], float)
    cs = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
    end = cs[-1]
    if upto is not None:
        end = cs[int(np.argmin(np.hypot(*(p - np.asarray(upto)).T)))]
    rng = np.random.RandomState(seed)
    s0 = 0.0
    ch = Lyr(pbox([tuple(q) for q in p], 14)); em = Lyr(pbox([tuple(q) for q in p], 14)); dots = []
    while s0 < end:
        ln = rng.uniform(22, 52); gap = rng.uniform(26, 70)
        s1 = min(s0 + ln, end)
        ss = np.arange(s0, s1, 4.0)
        if len(ss) > 1:
            pts = [(float(np.interp(t, cs, p[:, 0])), float(np.interp(t, cs, p[:, 1]))) for t in ss]
            ch.line(pts, 8.0, 255)
            dots += [pts[0], pts[-1]]
        s0 = s1 + gap
    for q in dots:
        em.ell(q, 3.2, 2.4, 255)
    cv.over(INK, ch.m, .72 * k, ch.off)
    cv.add(hexc('FF5A10'), em.m, 1.3 * k, em.off)
    cv.add(hexc('FF5A10'), pblur(em.m, 4), 1.0 * k, em.off)


def ui_aftermath(cv, B, w):
    """06 is WORDLESS and tells the raid on the map: burnt beam remnants (N all the way to HOME, D ends at the HOLDS ring, E at its UNTOUCHED Site), grease slashes on the DOWN Sites,
    the SITES LOST tile on its tower, the DAMAGED tile above a cracked HOME ring, a 4-pip HOME gauge and six pencil tally strokes. No poster."""
    scorch_route(cv, B, 'K2', None, seed=3)
    scorch_route(cv, B, 'K1', w.sites['t1_c']['B'], seed=5)
    scorch_route(cv, B, 'K3', w.sites['t2_intel']['B'], seed=8, k=.8)
    for sid in ('t1_a', 't1_b'):
        s = w.sites[sid]
        ui.grease_down(cv, (s['B'][0], s['B'][1] - 34 - 60), 26, seed=sum(map(ord, sid)) % 50)
    tile(cv, w, 't1_b', 'SITES_LOST', 1, off=(34, -50), r=40, tag='aftermath')
    tile(cv, w, 't1_c', 'HOLDS', None, off=(-34, -44), r=36, k=.95, tag='aftermath')
    p = w.sites['t1_c']['B']
    ui.bits(cv, p + np.array([0, -30]), TYPE_COL['D'], n=14, r=70, seed=2, k=.5)
    hm = w.home
    p2_ui.cracked_ring(cv, hm + np.array([0, 4]), r=94)
    c = np.array([hm[0] + 100, hm[1] - 130])
    shadow(cv, c, 42)
    hy.hex_tile(cv, c, 'DAMAGED', None, r=40)
    for i in range(4):          # 4-pip HOME gauge: three lit, the last one cracked
        pc = (hm[0] - 52 + i * 26, hm[1] - 128)
        pl = Lyr(pbox([pc], 14))
        pl.poly(hy.hexpts(pc, 10), 255)
        cv.overL(pl, INK, .95)
        if i < 3:
            cv.addL(pl, hexc('F6F1E4'), .95)
        else:
            cv.addL(pl, TIER['DAMAGED'], .95)
            cr = Lyr(pbox([pc], 14)); cr.line([(pc[0] - 6, pc[1] - 8), (pc[0] + 1, pc[1]), (pc[0] - 3, pc[1] + 8)], 2.2, 255)
            cv.overL(cr, INK, .95)
    p2_ui.pencil_tally(cv, (hm[0] + 160, hm[1] - 40), 6, seed=4, size=34)
    hy.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + ui.HEAT * .4)
''')
repl('ui_city_lost', '''
def ui_city_lost(cv, B, w):
    """07: ONE effect (the plum flood with its climb edge), a small skull, and the SITES LOST tiles in context (ink-black on the lost towers); no datamosh."""
    c = (700, 560)
    pl = Lyr((c[0] - 120, c[1] - 120, c[0] + 120, c[1] + 120))
    glyphs.g_skull(pl, c, 74)
    ring = Lyr((c[0] - 120, c[1] - 120, c[0] + 120, c[1] + 120))
    ring.ell(c, 104, v=255, outline=True, ow=3.5)
    cv.add(PLUM, pblur(pl.m, 30), 1.0, pl.off)
    cv.over(INK, pblur(pl.m, 10), .6, pl.off)
    cv.neonL(pl, WHITE * .92, core=0.95, g1=(4, .3), g2=(18, .18), white=.1)
    cv.neonL(ring, hexc('B04AA0'), core=.8, g1=(3, .5), g2=(10, .3))
    tile(cv, w, 't1_b', 'SITES_LOST', 1, off=(34, -50), r=40, tag='city_lost')
    tile(cv, w, 't2_intel', 'SITES_LOST', 1, off=(0, -56), r=40, tag='city_lost')
    hy.hud(cv, 44, 50, 80, 8, 11, lost=True)
''')
repl('ui_tiers', '''
def ui_tiers(cv, B, w):
    import p1_beats
    for sid, tier in p1_beats.TIERS_AT:
        tile(cv, w, sid, tier, None, off=(0, -56), r=44, tag='tiers')
    hy.hud(cv, 44, 50, 80, 8, 0)
''')
open('p1_final.py', 'w').write(s)
print('ok')
