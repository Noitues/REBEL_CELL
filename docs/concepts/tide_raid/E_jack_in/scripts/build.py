"""Build the E Jack-in frames.  python build.py [frame ...]   (no args = all)"""
import sys, os, math, time
import numpy as np
from lib import *
import scene as SC
import ui
from glyphs import *
from daemon import *
from common import *
FOG = ui.FOG
HEAT = ui.HEAT

FR = OUT + 'frames/'
os.makedirs(FR, exist_ok=True)

HAND = [('GUARD', 'D'), ('GUARD', 'N'), ('SHIFT', 'E'), ('JAM', 'N'), ('GUARD', 'E')]
PROGRAMS = {'t1_a': ('GUARD', 'N'), 't1_b': ('SHIFT', 'E'), 't1_c': ('GUARD', 'D')}
PROB = [10, 30, 34, 20, 6]  # odds across the five outcome tiers (art values)


def save(cv, name, post=True):
    a = finish(cv) if post else cv.out()
    im = to_img(a)
    im.save(FR + name + '.png')
    print('saved', name)
    return im


# ------------------------------------------------------------------ shared pieces
def sealed_layers(cv, w, k=1.0, which=('A', 'B', 'C'), s_from=None):
    for i, r in enumerate(which):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, plen(p) - 6, width=15, seed=3 + i, k=.9 * k)


def locks(cv, w, state=None, k=1.0, reveal=None):
    base = np.array([w.hq[0] - 188, w.hq[1] - 70])
    for i, L in enumerate('ABC'):
        c = base + np.array([i * 52, -i * 33])
        if reveal and L == reveal:
            ui.lock(cv, c, L, 'open', w.routes[L]['typ'], k=k)
        else:
            ui.lock(cv, c, L, 'locked', k=k * (.5 if reveal else 1))


def hunter_layers(cv, w, k=1.0, locked=None, ghost_k=.8):
    """hunter: an eye over the net + two ghost heads on its two candidate streets."""
    cs = []
    for i, h in enumerate(w.hunters):
        p = h['path']
        col = TYPE_COL[h['typ']]
        s_mid = plen(p) * .55
        pt, _ = at(p, s_mid)
        cs.append(pt)
        if locked is not None and i != locked:
            continue
        pl = Lyr(pbox(p, 10))
        pl.line([tuple(x) for x in p], 2.6, 255, dash=(9, 7))
        cv.neonL(pl, col, core=.6 * k, g1=(3, .4 * k), g2=None)
        draw_daemon(cv, p, plen(p) * .7, h['typ'], mode='ghost', sc=.85, alpha=ghost_k * k, trail=False)
    return cs


def hunter_eye_at(cv, w, cs, k=1.0, locked=None):
    c = (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)
    ln = Lyr(pbox(cs + [c], 10))
    for p in cs:
        ln.line([tuple(c + np.array([0, 24])), tuple(p)], 1.6, 255, dash=(3, 5))
    cv.neonL(ln, HOT, core=.7 * k, g1=(2, .4 * k), g2=None)
    ui.hunter_eye(cv, c, 54, k)
    return c



# ------------------------------------------------------------------ more shared pieces
def infected_card(cv, c, angle=0, sc=1.0, k=1.0, trail_from=None):
    """an INFECTED card (plum, pink veins, X) flying up to the deck strip."""
    wd, ht = 44, 62
    L = Lyr((0, 0, wd, ht), ss=3, pad=0)
    e = Lyr((0, 0, wd, ht), ss=3, pad=0)
    v = Lyr((0, 0, wd, ht), ss=3, pad=0)
    L.rr(1, 1, wd - 1, ht - 1, 6, 255)
    e.rr(1.5, 1.5, wd - 1.5, ht - 1.5, 6, 255, outline=True, ow=2.4)
    v.line([(10, 12), (20, 24), (14, 34), (30, 48)], 2.0, 255)
    v.line([(34, 10), (26, 26), (36, 38)], 1.6, 255)
    a = L.m[:ht, :wd]; ee = e.m[:ht, :wd]; vv = v.m[:ht, :wd]
    img = np.zeros((ht, wd, 3), np.float32) + PLUM_MID * .9
    img = img + VEIN * ee[..., None] + HOT * vv[..., None] * .9
    rgba = np.dstack([np.clip(img, 0, 1), a])
    im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
    if sc != 1:
        im = im.resize((int(wd * sc), int(ht * sc)), Image.LANCZOS)
    im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox, oy = int(c[0] - arr.shape[1] / 2), int(c[1] - arr.shape[0] / 2)
    cv.add(VEIN, blur(arr[..., 3], 8), .7 * k, (ox, oy))
    cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))
    if trail_from is not None:
        tl = Lyr(pbox([trail_from, c], 12))
        tl.line([tuple(trail_from), tuple(c)], 2.2, 255, dash=(3, 7))
        cv.neonL(tl, VEIN, core=.7 * k, g1=(2, .5), g2=None)


def bez(a, m, b, n=26):
    return [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * m[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * m[1] + t * t * b[1]) for t in np.linspace(0, 1, n)]


def grease_arrow(cv, a, m, b, k=1.0, seed=3):
    """white china-marker drag arrow (the pencil, not lime: lime is the focus halo only)."""
    pts = bez(a, m, b)
    ly = Lyr(pbox(pts, 20))
    for p, q in zip(pts[:-1], pts[1:]):
        ly.line([tuple(p), tuple(q)], 5.2, 255)
    d = np.array(pts[-1]) - np.array(pts[-4]); d = d / np.hypot(*d); n = np.array([-d[1], d[0]])
    tip = np.array(pts[-1]) + d * 6
    ly.line([tuple(tip - d * 20 + n * 13), tuple(tip), tuple(tip - d * 20 - n * 13)], 5.2, 255)
    cv.overL(ly, INK, .55 * k)
    cv.addL(ly, GREASE_W, .95 * k)


def lime_ring(cv, B, r=46, k=1.0):
    ly = Lyr((B[0] - r - 12, B[1] - r - 12, B[0] + r + 12, B[1] + r + 12))
    ly.line(ring_pts(B, r, 80), 4, 255)
    ly.line(ring_pts(B, r + 10, 80), 1.6, 255, dash=(5, 5))
    cv.neonL(ly, LIME, core=1.0 * k, g1=(4, .9 * k), g2=(12, .6 * k))


def husk(cv, w, r, s_head, k=1.0):
    R = w.routes[r]
    draw_daemon(cv, R['path'], s_head, R['typ'], mode='dead', alpha=k, sc=1.8)


def worms_at_hq(cv, w, which, runs, sc=1.8):
    for r, run in zip(which, runs):
        R = w.routes[r]
        draw_daemon(cv, R['path'], w.head_hq(r, run), R['typ'], sc=sc)


def plan_routes(cv, w, k=1.0):
    for r in ('K1', 'K2'):
        R = w.routes[r]
        route_line(cv, R['path'], R['typ'], R['ext'], plen(R['path']), k)


# ================================================================== frames
def f_decay():
    w = World('decay')
    cv = new_canvas(w)
    B1, B2 = w.sites['t1_a']['B'], w.sites['t1_b']['B']
    SC.bloom(cv, [B1 + np.array([0, -10]), B2 + np.array([0, -10]), (B1 + B2) / 2 + np.array([0, 30])], [150, 130, 70], seed=5)
    draw_world(cv, w, {'t1_a': 'TAKEN', 't1_b': 'TAKEN'}, {}, home_kw=dict(hp=44))
    for B in (B1, B2):
        ui.shock(cv, B, 96, VEIN, w=2, k=.35)
    tgt = [(1704, 40), (1730, 40), (1756, 40)]
    src = [B1 + np.array([0, -150]), B2 + np.array([0, -150]), (B1 + B2) / 2 + np.array([0, -190])]
    for i, (s_, t_) in enumerate(zip(src, tgt)):
        f = [.28, .46, .64][i]
        p = s_ + (np.array(t_) - s_) * f + np.array([0, -120 * math.sin(math.pi * f)])
        infected_card(cv, p, angle=-18 + i * 12, sc=1.1 - .25 * f, trail_from=s_)
    ui.hud(cv, 44, 50, 80, 8, 3)
    save(cv, '01_decay')


def f_draw():
    w = World('default')
    cv = new_canvas(w)
    for i, r in enumerate(('A', 'B', 'C')):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, w.routes[r]['ext'] + 330, width=15, seed=3 + i, k=.9)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {}, home_kw=dict(hp=44), cage_kw=dict(hot=True, phase=.35))
    ui.shock(cv, w.hq + np.array([0, -4]), 120, LATT, w=4, k=.9)
    worms_at_hq(cv, w, ('K1', 'K2'), (75, 235))
    locks(cv, w)
    c = (w.hq[0] - 330, w.hq[1] - 330)
    ui.hunter_eye(cv, c, 50, .8)
    ui.hand(cv, HAND[:3], dim=1.0, spread=122)
    for i, (v, t) in enumerate(HAND[3:]):
        ui.card(cv, (1260 + i * 170, 830 + i * 40), v, t, angle=26 - i * 14, k=.95)
        tl = Lyr((1300, 780, 1760, 1000))
        tl.line([(1300 + i * 100, 780 + i * 20), (1260 + i * 170, 830 + i * 40)], 2, 255, dash=(4, 8))
        cv.neonL(tl, LATT_D, core=.6, g1=None, g2=None)
    ui.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '02_draw')


def f_plan(panels=True, name='03_plan'):
    w = World('default')
    cv = new_canvas(w)
    for i, r in enumerate(('A', 'B', 'C')):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, plen(p) - 6, width=15, seed=3 + i, k=.5)
    plan_routes(cv, w, 1.15)
    progs = {'t1_a': ('GUARD', 'N'), 't1_b': ('SHIFT', 'E')}
    draw_world(cv, w, {'t1_a': 'DOWN'}, progs, home_kw=dict(hp=44))
    worms_at_hq(cv, w, ('K1', 'K2'), (80, 240))
    locks(cv, w, k=.8)
    tc = w.sites['t1_c']['B']
    ui.firewall(cv, tc, 'D', mode='ghost')
    lime_ring(cv, tc + np.array([0, 4]), 50)
    ui.hud(cv, 44, 50, 80, 8, 0)
    if panels:
        drag_pos = (720, 760)
        grease_arrow(cv, (drag_pos[0] - 40, drag_pos[1] - 70), (560, 560), (tc[0] + 4, tc[1] + 52))
        ui.hand(cv, HAND, dim=.9, skip=0)
        ui.card(cv, drag_pos, 'GUARD', 'D', angle=-8, lime=True)
    save(cv, name)


def f_panels_removed():
    f_plan(panels=False, name='11_panels_removed')


def f_forecast(panels=True, name='04_forecast'):
    w = World('default')
    cv = new_canvas(w)
    sealed_layers(cv, w)
    for r in ('K1', 'K2'):
        R = w.routes[r]
        s_stop = w.visit(r, 't1_c')
        route_line(cv, R['path'], R['typ'], R['ext'], s_stop, 1.2)
        route_line(cv, R['path'], R['typ'], s_stop + 6, plen(R['path']), .5, dead=True, w=2.0)
    draw_world(cv, w, {'t1_a': 'DOWN'}, PROGRAMS, home_kw=dict(hp=44, preview=6))
    for r in ('K1', 'K2'):
        R = w.routes[r]
        s_stop = w.visit(r, 't1_c')
        for sid in R['sites'][1:-3]:
            s_ = w.visit(r, sid)
            if s_ < s_stop - 30:
                draw_daemon(cv, R['path'], s_ - 4, R['typ'], mode='ghost', sc=1.2, alpha=.55, trail=False)
        draw_daemon(cv, R['path'], s_stop - 6, R['typ'], mode='ghost', sc=1.6, alpha=1.0, trail=False)
    worms_at_hq(cv, w, ('K1', 'K2'), (75, 235))
    sB = w.sites['t1_b']['B']
    ui.tier_chip(cv, (sB[0] + 30, sB[1] - 98), 'SITES_LOST', r=17, num=1)
    sC = w.sites['t1_c']['B']
    ui.tier_chip(cv, (sC[0] + 50, sC[1] - 96), 'HOLDS', r=17)
    locks(cv, w)
    cs = hunter_layers(cv, w)
    hunter_eye_at(cv, w, cs)
    ui.odds_chart(cv, (40, 690), PROB)
    ui.hud(cv, 44, 50, 80, 8, 0)
    if panels:
        ui.hand(cv, HAND, dim=.9)
    save(cv, name)


def f_response():
    w = World('default')
    cv = new_canvas(w)
    sealed_layers(cv, w, k=.8)
    for r in ('K1', 'K2'):
        R = w.routes[r]
        s_stop = w.visit(r, 't1_c')
        route_line(cv, R['path'], R['typ'], R['ext'], s_stop, 1.2)
        route_line(cv, R['path'], R['typ'], s_stop + 6, plen(R['path']), .5, dead=True, w=2.0)
    draw_world(cv, w, {'t1_a': 'DOWN'}, PROGRAMS, home_kw=dict(hp=44, preview=6), cage_kw=dict(hot=True, phase=.6))
    worms_at_hq(cv, w, ('K1', 'K2'), (75, 235))
    ui.shock(cv, w.hq + np.array([0, -4]), 120, LATT, w=3.5, k=.8)
    locks(cv, w)
    cs = hunter_layers(cv, w, k=.8)
    hunter_eye_at(cv, w, cs, k=.8)
    ui.hud(cv, 44, 50, 80, 8, 0)
    opts = [('DEPLOY', ['HOLDS', 'HOLDS', 'SITES_LOST']), ('HOLD', ['HOLDS', 'SITES_LOST', 'DAMAGED']),
            ('MOVE', ['UNTOUCHED', 'SITES_LOST', 'DAMAGED']), ('SACRIFICE', ['SITES_LOST', 'SITES_LOST', 'BREACHED'])]
    for i, (kd, pips) in enumerate(opts):
        ui.resp_key(cv, (960 + (i - 1.5) * 150, 960), kd, pips, selected=(kd == 'HOLD'))
    save(cv, '05_response')


def f_playout_impact():
    w = World('default')
    cv = new_canvas(w)
    R = w.routes['K2']
    sC = w.visit('K2', 't1_c')
    sh = sC - 12
    route_line(cv, R['path'], R['typ'], R['ext'], sh, 1.3)
    route_line(cv, w.routes['K1']['path'], 'D', w.routes['K1']['ext'], w.visit('K1', 't1_c'), .7, dead=True)
    tcB = w.sites['t1_c']['B']
    wallc = np.array([tcB[0] + 34, tcB[1] + 12 - 24])
    sh = nearest_s(R['path'], wallc) - 30
    hp = wallc
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    progs = {'t1_a': ('GUARD', 'N'), 't1_b': ('SHIFT', 'E')}
    draw_world(cv, w, states, progs, home_kw=dict(hp=44))
    ui.focus_dim(cv, hp, 420, .5)
    ui.firewall(cv, tcB, 'D', mode='shatter', impact=tuple(hp), t=.5)
    husk(cv, w, 'K1', w.visit('K1', 't1_c') - 20, .9)
    draw_daemon(cv, R['path'], sh + 30, 'D', mode='full', sc=1.8)
    ui.flash(cv, hp + np.array([4, 4]), 120, TYPE_COL['D'] * .6 + WHITE * .4, .55)
    ui.shock(cv, hp + np.array([4, 14]), 62, TYPE_COL['D'], w=3.5)
    ui.bits(cv, hp + np.array([4, 0]), TYPE_COL['D'], n=60, r=150, seed=4)
    ui.hex_shards(cv, hp + np.array([4, 0]), TYPE_COL['D'], 16, 110, seed=6)
    ui.tier_chip(cv, (tcB[0] + 56, tcB[1] - 112), 'HOLDS', r=20)
    ui.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '06_playout_impact')


def f_playout_home():
    w = World('default')
    cv = new_canvas(w)
    R = w.routes['C']
    end = w.end('C')
    route_line(cv, R['path'], 'N', R['ext'], end, 1.2)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    draw_world(cv, w, states, dict(PROGRAMS), home_kw=dict(hp=44, hit=6, flash=.4))
    ui.focus_dim(cv, w.home, 460, .5)
    draw_daemon(cv, R['path'], end - 10, 'N', sc=1.85)
    c = w.home + np.array([0, -18])
    ui.flash(cv, c, 150, TIER['DAMAGED'], .55)
    ui.shock(cv, w.home, 100, TIER['DAMAGED'], w=4)
    ui.shock(cv, w.home, 150, TIER['DAMAGED'], w=2.5, k=.6)
    ui.bits(cv, c, TIER['DAMAGED'], n=55, r=170, seed=9)
    ui.hex_shards(cv, c, TIER['DAMAGED'], 12, 120, seed=3)
    ui.glitch_tear(cv, (90, 640, 720, 900), 1.0, seed=11, bands=12)
    ui.num_tag(cv, (w.home[0] + 8, w.home[1] - 150), '-6', TIER['DAMAGED'], 58)
    ui.hud(cv, 38, 50, 80, 8, 0, home_col=TIER['DAMAGED'], flash=.6)
    save(cv, '07_playout_home')


def f_aftermath():
    w = World('default')
    cv = new_canvas(w)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    draw_world(cv, w, states, {'t1_c': ('GUARD', 'D')}, home_kw=dict(hp=38, scar=6))
    for sid in ('t1_a', 't1_b'):
        ui.decay_ring(cv, w.sites[sid]['B'])
    p = w.sites['t1_c']['B']
    ui.bits(cv, p + np.array([0, -30]), TYPE_COL['D'], n=18, r=80, seed=2, k=.6)
    ui.bits(cv, w.home + np.array([0, -30]), TIER['DAMAGED'], n=16, r=90, seed=5, k=.6)
    ui.stamp(cv, (1000, 190), 'DAMAGED', 'DAMAGED', angle=-5, size=1.0)
    ui.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + HEAT * .4)
    save(cv, '08_aftermath')


def f_hq_step():
    w = World('default')
    cv = new_canvas(w)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    ta = w.sites['t1_a']['B']
    draw_world(cv, w, states, {'t1_c': ('GUARD', 'D')}, home_kw=dict(hp=38, scar=6))
    for sid in ('t1_a', 't1_b'):
        ui.decay_ring(cv, w.sites[sid]['B'], k=.8)
    SC.tower(cv, ta, 1, 'healthy', tint=TIER['UNTOUCHED'], alpha=.5, seed=4)
    hm = w.home
    cb = bez(hm + np.array([20, -30]), (hm[0] + 40, ta[1] + 90), ta + np.array([0, 8]))
    ly = Lyr(pbox(cb, 14))
    ly.line(cb, 3.2, 255, dash=(10, 6))
    cv.neonL(ly, LATT, core=1.0, g1=(3, .8), g2=(10, .5), white=.4)
    ui.glyph_disc(cv, (ta[0] + 6, ta[1] - 130), 24, LATT, g_wrench)
    coins = [(g_wrench, 10, True, hm + np.array([120, -60])), (g_cardx, 20, False, hm + np.array([205, 10])),
             (g_snow, 25, False, hm + np.array([270, 90]))]
    for fn, price, sel, p in coins:
        if sel:
            ring = Lyr((p[0] - 60, p[1] - 60, p[0] + 60, p[1] + 60))
            ring.ell(p, 53, v=255, outline=True, ow=4)
            cv.neonL(ring, LIME, core=1.0, g1=(4, .9), g2=(12, .6))
        ui.glyph_disc(cv, p, 44, LATT if sel else LATT_D, fn, gscale=.52, k=1.0 if sel else .75, ring_w=3)
        ui.ntext(cv, (p[0], p[1] + 66), str(price), 26, WHITE * .8 + LATT * .2, k=1.0 if sel else .75)
    ui.glyph_disc(cv, (1660, 960), 48, LATT, lambda l, c_, r_: g_chev(l, c_, r_, 2), gscale=.55, ring_w=3.4)
    ui.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + HEAT * .4)
    save(cv, '09_hq_step')


def f_city_lost():
    w = World('lost', beat='city_lost')
    cv = new_canvas(w)
    ids = ['t1_a', 't1_b', 't1_c', 't1_d']
    Bs = [w.sites[i]['B'] for i in ids]
    cen = [b + np.array([0, -20]) for b in Bs] + [w.sites['t2_breach']['B'], w.sites['t2_virus']['B'], w.home]
    SC.bloom(cv, cen, [330, 330, 330, 300, 220, 200, 240], seed=7)
    draw_world(cv, w, {i: 'TAKEN' for i in ids}, {}, home_kw=dict(hp=44, tint=VEIN * .6 + HOT * .4), cage_kw=dict(hot=True, phase=.8))
    c = (960, 420)
    ui.glitch_tear(cv, (0, 80, 1920, 960), 1.0, seed=21, bands=16)
    pl = Lyr((c[0] - 230, c[1] - 230, c[0] + 230, c[1] + 230))
    g_skull(pl, c, 150)
    ring = Lyr((c[0] - 230, c[1] - 230, c[0] + 230, c[1] + 230))
    ring.ell(c, 205, v=255, outline=True, ow=5)
    cv.add(PLUM, blur(pl.m, 40), 1.2, pl.off)
    cv.over(INK, blur(pl.m, 14), .6, pl.off)
    cv.neonL(pl, HOT, core=1.0, g1=(5, 1.0), g2=(26, .8), white=.6)
    cv.neonL(ring, VEIN, core=.9, g1=(4, .8), g2=(14, .5))
    ui.ntext(cv, (c[0], c[1] + 215), 'CITY LOST', 44, HOT, stroke=3)
    ui.hud(cv, 44, 50, 80, 8, 11, lost=True)
    save(cv, '10_city_lost')


def f_reveal():
    """bonus: sealed A opens (the E enforcer is out), B and C dissolve; the hunter locks one street."""
    w = World('default')
    cv = new_canvas(w)
    for i, r in enumerate(('B', 'C')):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, w.routes[r]['ext'] + 520, width=15, seed=3 + i, k=.35)
    RA = w.routes['A']
    route_line(cv, RA['path'], 'E', RA['ext'], plen(RA['path']), 1.1)
    draw_world(cv, w, {'t1_a': 'DOWN'}, PROGRAMS, home_kw=dict(hp=44))
    draw_daemon(cv, RA['path'], RA['ext'] + 330, 'E', sc=1.8)
    locks(cv, w, reveal='A')
    cs = hunter_layers(cv, w, locked=0)
    hunter_eye_at(cv, w, cs[:1], locked=0)
    ui.reticle(cv, cs[0], 44, WHITE)
    ui.bits(cv, w.routes['B']['path'][int(len(w.routes['B']['path']) * .06)], FOG, n=30, r=100, seed=3)
    ui.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '12_reveal_sealed_hunter')


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
