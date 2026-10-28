"""P1 final plate: 3D composite (tone-mapped) + UI/type (pass-2 kit, re-coloured to the P1 palette) + finishing.
python p1_final.py <beat|all> [--noui]  -> OUT/plates/<NN>_<beat>.png"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1lib as L
sys.path.insert(0, L.H2)
import p2_scale
p2_scale.install()
import lib as PL
from lib import Cv, Lyr, hexc, blur as pblur, WHITE, INK, PLUM, VEIN, HOT, LIME, LATT, LATT_D, TIER, TYPE_COL, pbox, T
import ui, hy, hb, eb as EB, glyphs
p2_scale.patch_modules(hy, ui, hb, EB)
import p1_comp as C
import p2_build as BLD
import p1_heads
import p2_ui

# ---- P1 palette changes (designer ruling 2026-10-27: yellower DAMAGED; tritan fix) written into the pass-2 kit's TIER table in place
TIER['DAMAGED'] = hexc('FF9A00')
TIER['SITES_LOST'] = hexc('C98410')
OUTDIR = L.OUT + ('plates/' if os.environ.get('P2_S', '1') == '1' else 'plates4k/')
os.makedirs(OUTDIR, exist_ok=True)
NN = {'tiers': 'T0', 'plan': '01', 'forecast': '02', 'reveal': '03', 'impact': '04', 'home_hit': '05', 'aftermath': '06', 'city_lost': '07'}
W, H = C.W, C.H


TILE_LOG = []      # beat / site -> distance from the Site tower top to the tile centre (px at 1920 scale); verified 34..64


def tower_top(w, sid):
    s = w.sites[sid]
    return np.array([s['B'][0], s['B'][1] - {1: 27, 2: 35, 3: 44}[s['tier']] * 3.73])


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


def shadow(cv, c, r, k=.55):
    m = Lyr((c[0] - r - 20, c[1] - r - 10, c[0] + r + 20, c[1] + r + 30), pad=0)
    m.ell((c[0] + 3, c[1] + 9), r * .95, r * .8, 255)
    cv.over(INK, pblur(m.m, 7), k, m.off)


def fracture_star(cv, c, r, col, seed=3, k=1.0):
    """HOME-hit non-hue cue: a jagged fracture star (white-hot core, ink-cut cracks, spiked silhouette). Reads in luminance and shape, not hue."""
    rng = np.random.RandomState(seed)
    n = 16
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + rng.uniform(-.05, .05)
        rr = r * (1.0 if i % 2 == 0 else .46) * (rng.uniform(.8, 1.18) if i % 2 == 0 else rng.uniform(.9, 1.1))
        pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr * .72))
    box = (c[0] - r * 1.3, c[1] - r, c[0] + r * 1.3, c[1] + r)
    star = Lyr(box, pad=6, ss=3)
    star.poly(pts, 255)
    core = Lyr(box, pad=6, ss=3)
    core.poly([(c[0] + (p[0] - c[0]) * .5, c[1] + (p[1] - c[1]) * .5) for p in pts], 255)
    crack = Lyr(box, pad=6, ss=3)
    for i in range(0, n * 2, 2):
        a = math.pi * i / n
        crack.line([(c[0] + math.cos(a) * r * .22, c[1] + math.sin(a) * r * .22 * .72), (c[0] + math.cos(a + .08) * r * 1.5, c[1] + math.sin(a + .08) * r * 1.5 * .72)], 1.6, 255)
    cv.over(INK, pblur(star.m, 1.2) * 1.0, .92 * k, star.off)
    cv.add(col, pblur(star.m, 9), .32 * k, star.off)
    cv.over(col * .35 + WHITE * .65, star.m * (1 - core.m * .0), .96 * k, star.off)
    cv.over(WHITE, core.m, 1.0 * k, star.off)
    cv.over(INK, crack.m * (1 - core.m) * .9, .85 * k, crack.off)
    ring = Lyr(box, pad=6, ss=3)
    ring.ell(c, r * 1.02, r * .74, 255, outline=True, ow=2.2)
    cv.over(INK, ring.m, .8 * k, ring.off)


def eye_dots(cv, c, tgts, k=1.0):
    ln = Lyr(pbox(list(tgts) + [c], 10))
    for p in tgts:
        ln.line([tuple(np.array(c) + np.array([0, 24])), tuple(p)], 1.8, 255, dash=(3, 5))
    cv.neonL(ln, WHITE * .8, core=.7 * k, g1=(2, .4 * k), g2=None)


def hunter_pts(B, w):
    pts = []
    for h in (B.ui.get('hunter_px') or []):
        p = np.asarray(h, float)
        L_ = np.cumsum(np.concatenate([[0], np.hypot(*np.diff(p, axis=0).T)]))
        i = int(np.searchsorted(L_, L_[-1] * .72))
        pts.append(p[min(i, len(p) - 1)])
    return pts


def locks_big(cv, w, reveal=None, k=1.0):
    """P2: letter locks at 1.5x (r 31) on a wider diagonal so the silhouettes survive 320 px."""
    base = np.array([w.hq[0] - 214, w.hq[1] - 54])
    for i, L_ in enumerate('ABC'):
        c = base + np.array([i * 76, -i * 48])
        if reveal and L_ == reveal:
            ui.lock(cv, c, L_, 'open', w.routes[L_]['typ'], r=34, k=k)
        else:
            ui.lock(cv, c, L_, 'locked', r=31, k=k * (.55 if reveal else 1))


DOWN_FRAC = {'plan': .78, 'forecast': .70, 'reveal': .62, 'impact': .55, 'home_hit': .48, 'aftermath': .36}


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


def ui_plan(cv, B, w):
    locks_big(cv, w, k=.9)
    hy_eye = (1030, 300)
    ui.hunter_eye(cv, hy_eye, 46, .85, col=WHITE * .92 + LATT * .08)
    dp = (720, 800)
    EB.grease_arrow(cv, (dp[0] - 40, dp[1] - 70), (600, 640), (w.sites['t2_intel']['B'][0] + 4, w.sites['t2_intel']['B'][1] + 52))
    hy.hand(cv, hb.HAND, y=992, skip=0)
    shadow(cv, dp, 60, .6)
    hy.vcard(cv, dp, 'GUARD', 'D', angle=-8, lime=True)
    hy.hud(cv, 44, 50, 80, 8, 0)


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


def ui_reveal(cv, B, w):
    locks_big(cv, w, reveal='A')
    pts = hunter_pts(B, w)
    c = np.array([1030, 300])
    if pts:
        eye_dots(cv, c, [pts[0]])
        ui.hunter_eye(cv, c, 52, 1.0, col=WHITE * .92 + LATT * .08)
        ui.reticle(cv, pts[0], 66, WHITE)
        if len(pts) > 1:
            m = pts[1]
            st = Lyr((m[0] - 30, m[1] - 24, m[0] + 30, m[1] + 24))
            st.line([(m[0] - 22, m[1] - 14), (m[0] + 22, m[1] + 14)], 3, 255)
            st.line([(m[0] - 22, m[1] + 14), (m[0] + 22, m[1] - 14)], 3, 255)
            cv.neonL(st, WHITE * .7, core=.5, g1=None, g2=None)
    ui.bits(cv, w.routes['B']['path'][int(len(w.routes['B']['path']) * .06)], ui.FOG, n=30, r=100, seed=3)
    hy.hud(cv, 44, 50, 80, 8, 0)


def ui_impact(cv, B, w):
    sid = B.ui['site']
    tc = w.sites[sid]['B']
    ui.bits(cv, tc + np.array([4, -40]), TYPE_COL['D'] * .6 + WHITE * .4, n=40, r=140, seed=4)
    tile(cv, w, sid, 'HOLDS', None, off=(48, -38), r=36, tag='impact')
    tile(cv, w, 't1_b', 'SITES_LOST', 1, off=(34, -50), r=34, k=.95, tag='impact')
    hy.hud(cv, 44, 50, 80, 8, 0)


def ui_home_hit(cv, B, w):
    hm = w.home
    c = hm + np.array([0, -30])
    ui.glitch_tear(cv, (170, 790, 640, 850), 0.8, seed=11, bands=5, maxdx=26)
    fracture_star(cv, c + np.array([0, -4]), 66, TIER['DAMAGED'], seed=4, k=.9)
    ui.bits(cv, c, TIER['DAMAGED'], n=40, r=150, seed=9)
    shadow(cv, (hm[0] + 96, hm[1] - 128), 34)
    hy.hex_tile(cv, (hm[0] + 96, hm[1] - 128), 'DAMAGED', None, r=34)
    ui.num_tag(cv, (hm[0] + 176, hm[1] - 126), '-6', TIER['DAMAGED'], 60)
    hy.hud(cv, 38, 50, 80, 8, 0, home_col=TIER['DAMAGED'], flash=.6)


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


def ui_tiers(cv, B, w):
    import p1_beats
    OFF = {'t1_a': (0, -56), 't1_d': (0, -56), 't2_virus': (0, -56), 't3_c': (0, -56), 't3_core': (0, -56)}
    for sid, tier in p1_beats.TIERS_AT:
        tile(cv, w, sid, tier, None, off=OFF[sid], r=44, tag='tiers')
    hy.hud(cv, 44, 50, 80, 8, 0)


UI = {'tiers': ui_tiers, 'plan': ui_plan, 'forecast': ui_forecast, 'reveal': ui_reveal, 'impact': ui_impact, 'home_hit': ui_home_hit, 'aftermath': ui_aftermath, 'city_lost': ui_city_lost}
OPTS = {'tiers': dict(ghost_over=True), 'impact': dict(cap_occ=1.0, cap_spill=0.8), 'home_hit': dict(cap_occ=1.1, cap_spill=0.9)}   # per beat compose overrides


def finish(img, seed=3, vig=0.34, fringe=1.6, grain=0.012, scan=0.04):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - vig * np.clip(d - .5, 0, 1.2) ** 1.6
    img = img * v[..., None]
    edge = np.clip(d - .72, 0, 1)
    sh = int(round(fringe * C.S))
    r = np.roll(img[..., 0], sh, 1); b = np.roll(img[..., 2], -sh, 1)
    k = np.clip(edge * 2.0, 0, 1)
    img[..., 0] = img[..., 0] * (1 - k) + r * k
    img[..., 2] = img[..., 2] * (1 - k) + b * k
    img = img * (1 - scan * (np.mod(np.floor(yy / C.S), 3) == 0))[..., None]
    rng = np.random.RandomState(seed)
    img = img + (rng.randn(H, W, 1).astype(np.float32) * grain)
    return np.clip(img, 0, 1)


def build(beat, ui_on=True, save=True):
    import p1_beats
    B = getattr(p1_beats, beat)(False)
    w = B.w
    opts = dict(OPTS.get(beat, {}))
    if beat == 'aftermath':
        opts['burn'] = [(w.sites['t1_a']['B'][0], w.sites['t1_a']['B'][1], 62), (w.sites['t1_b']['B'][0], w.sites['t1_b']['B'][1], 62), (w.home[0], w.home[1] + 6, 96)]
    lin_img = BLD.compose(beat, **opts)
    base = C.tone(lin_img)
    cv = Cv(base)
    if ui_on:
        ground_marks(beat, cv, B, w)
    hd = B.ui.get('heads', [])
    if beat in ('impact', 'home_hit'):
        hd = [dict(h, halo=True) for h in hd]
    if beat in ('plan', 'forecast', 'reveal'):
        hero = B.ui.get('hero', {}).get(beat)
        hd = [dict(h, mass=(3.0 if h.get('rid') == hero else 0)) for h in hd]
    p1_heads.draw(cv, hd, pblur)
    if ui_on:
        UI[beat](cv, B, w)
    out = finish(cv.out())
    if save:
        im = Image.fromarray((out * 255 + .5).astype(np.uint8))
        im.save(OUTDIR + '%s_%s.png' % (NN[beat], beat))
    return out


if __name__ == '__main__':
    beats = [b for b in NN if b != 'tiers'] if sys.argv[1] == 'all' else [sys.argv[1]]
    for b in beats:
        build(b, ui_on='--noui' not in sys.argv)
        print('built', b)
    import json as _j
    _f = L.OUT + 'tile_distances_%s.json' % ('_'.join(beats) if len(beats) < 3 else 'all')
    _j.dump(TILE_LOG, open(_f, 'w'), indent=1)
