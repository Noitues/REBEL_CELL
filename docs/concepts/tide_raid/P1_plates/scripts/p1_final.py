"""P1 final plate: 3D composite (tone-mapped) + UI/type (pass-2 kit, re-coloured to the P1 palette) + finishing.
python p1_final.py <beat|all> [--noui]  -> OUT/plates/<NN>_<beat>.png"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1lib as L
sys.path.insert(0, L.H2)
import lib as PL
from lib import Cv, Lyr, hexc, blur as pblur, WHITE, INK, PLUM, VEIN, HOT, LIME, LATT, LATT_D, TIER, TYPE_COL, pbox, T
import ui, hy, hb, eb as EB, glyphs
import p1_comp as C
import p1_build as BLD
import p1_heads

# ---- P1 palette changes (designer ruling 2026-10-27: yellower DAMAGED; tritan fix) written into the pass-2 kit's TIER table in place
TIER['DAMAGED'] = hexc('FF9A00')
TIER['SITES_LOST'] = hexc('C98410')
OUTDIR = L.OUT + 'plates/'
os.makedirs(OUTDIR, exist_ok=True)
NN = {'plan': '01', 'forecast': '02', 'reveal': '03', 'impact': '04', 'home_hit': '05', 'aftermath': '06', 'city_lost': '07'}
W, H = 1920, 1080


def tile_anchor(w, sid, up=64):
    s = w.sites[sid]
    h_px = {1: 27, 2: 35, 3: 44}[s['tier']] * 3.73
    return np.array([s['B'][0], s['B'][1] - h_px - up])


def tile(cv, w, sid, tier, num=None, up=64, dx=0, dy=0, r=30, k=1.0):
    c = tile_anchor(w, sid, up) + np.array([dx, dy])
    src = np.array(w.sites[sid]['B']) + np.array([0, -4])
    hy.leader(cv, src, c + np.array([0, 24]), k=.8)
    shadow(cv, c, r + 6)
    hy.hex_tile(cv, c, tier, num, r=r, k=k)
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
    cv.add(col, pblur(star.m, 9), .8 * k, star.off)
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


def ui_plan(cv, B, w):
    hb.locks(cv, w, k=.85)
    hy_eye = (1030, 300)
    ui.hunter_eye(cv, hy_eye, 46, .85, col=WHITE * .92 + LATT * .08)
    tc = w.sites['t1_c']['B']
    dp = (720, 800)
    EB.grease_arrow(cv, (dp[0] - 40, dp[1] - 70), (600, 640), (w.sites['t2_intel']['B'][0] + 4, w.sites['t2_intel']['B'][1] + 52))
    hy.hand(cv, hb.HAND, y=992, skip=0)
    shadow(cv, dp, 60, .6)
    hy.vcard(cv, dp, 'GUARD', 'D', angle=-8, lime=True)
    hy.hud(cv, 44, 50, 80, 8, 0)


def ui_forecast(cv, B, w):
    hb.locks(cv, w, k=.85)
    ui.hunter_eye(cv, (1030, 300), 40, .7, col=WHITE * .92 + LATT * .08)
    tile(cv, w, 't1_c', 'HOLDS', None, up=34, dx=-34, dy=-10)
    tile(cv, w, 't1_b', 'SITES_LOST', 1, up=34, dx=10, dy=-52)
    tile(cv, w, 't2_intel', 'UNTOUCHED', None, up=34, dx=0, dy=-28)
    hy.home_chip(cv, w.home, 6)
    hy.tally(cv, (w.home[0] + 10, w.home[1] + 150), hb.TALLY, r=17, gap=34, group_gap=14)
    hy.hand(cv, hb.HAND, y=992)
    hy.hud(cv, 44, 50, 80, 8, 0)


def ui_reveal(cv, B, w):
    hb.locks(cv, w, reveal='A')
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
    ui.bits(cv, tc + np.array([4, -40]), TYPE_COL['D'] * .6 + WHITE * .4, n=60, r=150, seed=4)
    tile(cv, w, sid, 'HOLDS', None, up=48, dx=50, dy=-20, r=30)
    hy.hud(cv, 44, 50, 80, 8, 0)


def ui_home_hit(cv, B, w):
    hm = w.home
    c = hm + np.array([0, -30])
    ui.glitch_tear(cv, (90, 640, 720, 900), 1.0, seed=11, bands=12)
    fracture_star(cv, c + np.array([0, -4]), 84, TIER['DAMAGED'], seed=4)
    ui.bits(cv, c, TIER['DAMAGED'], n=55, r=170, seed=9)
    shadow(cv, (hm[0] + 96, hm[1] - 128), 34)
    hy.hex_tile(cv, (hm[0] + 96, hm[1] - 128), 'DAMAGED', None, r=34)
    ui.num_tag(cv, (hm[0] + 176, hm[1] - 126), '-6', TIER['DAMAGED'], 60)
    hy.hud(cv, 38, 50, 80, 8, 0, home_col=TIER['DAMAGED'], flash=.6)


def ui_aftermath(cv, B, w):
    for sid in ('t1_a', 't1_b'):
        s = w.sites[sid]
        ui.grease_down(cv, (s['B'][0], s['B'][1] - 34 - 60), 26, seed=sum(map(ord, sid)) % 50)
        ui.decay_ring(cv, s['B'], frac=.55)
    p = w.sites['t1_c']['B']
    ui.bits(cv, p + np.array([0, -30]), TYPE_COL['D'], n=18, r=80, seed=2, k=.6)
    ui.bits(cv, w.home + np.array([0, -30]), TIER['DAMAGED'], n=16, r=90, seed=5, k=.6)
    hy.poster(cv, (930, 800), 'DAMAGED', 'DAMAGED', 292, 266)
    hy.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + ui.HEAT * .4)


def ui_city_lost(cv, B, w):
    c = (960, 420)
    ui.glitch_tear(cv, (0, 80, 1920, 960), 1.0, seed=21, bands=16)
    pl = Lyr((c[0] - 230, c[1] - 230, c[0] + 230, c[1] + 230))
    glyphs.g_skull(pl, c, 150)
    ring = Lyr((c[0] - 230, c[1] - 230, c[0] + 230, c[1] + 230))
    ring.ell(c, 205, v=255, outline=True, ow=5)
    cv.add(PLUM, pblur(pl.m, 40), 1.2, pl.off)
    cv.over(INK, pblur(pl.m, 14), .6, pl.off)
    cv.neonL(pl, HOT, core=0.92, g1=(5, .45), g2=(26, .25), white=.15)
    cv.neonL(ring, VEIN, core=.9, g1=(4, .8), g2=(14, .5))
    hy.hud(cv, 44, 50, 80, 8, 11, lost=True)


UI = {'plan': ui_plan, 'forecast': ui_forecast, 'reveal': ui_reveal, 'impact': ui_impact, 'home_hit': ui_home_hit, 'aftermath': ui_aftermath, 'city_lost': ui_city_lost}
OPTS = {}   # per beat compose overrides (set in p1_look.py)


def finish(img, seed=3, vig=0.34, fringe=1.6, grain=0.012, scan=0.04):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - vig * np.clip(d - .5, 0, 1.2) ** 1.6
    img = img * v[..., None]
    edge = np.clip(d - .72, 0, 1)
    sh = int(round(fringe))
    r = np.roll(img[..., 0], sh, 1); b = np.roll(img[..., 2], -sh, 1)
    k = np.clip(edge * 2.0, 0, 1)
    img[..., 0] = img[..., 0] * (1 - k) + r * k
    img[..., 2] = img[..., 2] * (1 - k) + b * k
    img = img * (1 - scan * (np.mod(yy, 3) == 0))[..., None]
    rng = np.random.RandomState(seed)
    img = img + (rng.randn(H, W, 1).astype(np.float32) * grain)
    return np.clip(img, 0, 1)


def build(beat, ui_on=True, save=True):
    import p1_beats
    B = getattr(p1_beats, beat)(False)
    w = B.w
    lin_img = BLD.compose(beat, **OPTS.get(beat, {}))
    base = C.tone(lin_img)
    cv = Cv(base)
    p1_heads.draw(cv, B.ui.get('heads', []), pblur)
    if ui_on:
        UI[beat](cv, B, w)
    out = finish(cv.out())
    if save:
        im = Image.fromarray((out * 255 + .5).astype(np.uint8))
        im.save(OUTDIR + '%s_%s.png' % (NN[beat], beat))
    return out


if __name__ == '__main__':
    beats = list(NN) if sys.argv[1] == 'all' else [sys.argv[1]]
    for b in beats:
        build(b, ui_on='--noui' not in sys.argv)
        print('built', b)
