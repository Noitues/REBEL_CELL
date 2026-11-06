"""Build the hybrid frames.  python hb.py [frame ...]   (no args = all)"""
import sys, os, math, time
import numpy as np
from lib import *
from PIL import Image, ImageDraw
import scene as SC
import ui
import hy
import eb as EB
from hy import PX
from glyphs import *
from daemon import *
from common import *

FR = OUT + 'frames/'
os.makedirs(FR, exist_ok=True)
FOG = ui.FOG

HAND = [('GUARD', 'D'), ('GUARD', 'N'), ('SHIFT', 'E'), ('JAM', 'N'), ('GUARD', 'E')]
PROGRAMS = {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}
KN = ('K1', 'K2', 'K3')            # the three known beams: D, N, E (pass 2: all co-visible)
RUN = {'K1': 60, 'K2': 400, 'K3': 215}   # where each parked head waits on its street (arclength past the HQ stub)
IDLE = ('t1_d',)
TALLY = {'UNTOUCHED': 4, 'HOLDS': 4, 'SITES_LOST': 3, 'DAMAGED': 1}


def save(cv, name, post=True):
    a = finish(cv, vig=.38, scan=.07, fringe=1.5) if post else cv.out()
    im = to_img(a)
    im.save(FR + name + '.png')
    print('saved', name)
    return im


def P_(w, r):
    return PX(w.routes[r]['path'])


def forecast_cols(w, r, events):
    """traffic colouring: the stretch leading to each Site takes the tier of what happens there."""
    cols = []
    for sid, tier in events:
        cols.append((w.visit(r, sid), TIER[tier]))
    return cols


def sealed_layers(cv, w, k=1.0, which=('A', 'B', 'C'), length=None):
    for i, r in enumerate(which):
        p = w.routes[r]['path']
        e = plen(p) - 6 if length is None else w.routes[r]['ext'] + length
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, e, width=11, seed=3 + i, k=.9 * k)


def lock_pos(w, i):
    base = np.array([w.hq[0] - 188, w.hq[1] - 70])
    return base + np.array([i * 52, -i * 33])


def locks(cv, w, k=1.0, reveal=None):
    for i, L in enumerate('ABC'):
        c = lock_pos(w, i)
        if reveal and L == reveal:
            ui.lock(cv, c, L, 'open', w.routes[L]['typ'], k=k)
        else:
            ui.lock(cv, c, L, 'locked', k=k * (.5 if reveal else 1))


def hunter(cv, w, k=1.0, locked=None):
    """HUNTER: a WHITE eye (never yellow: yellow is the E beam). Two candidate streets in white dashes with an
    E-ram ghost on each. When locked: reticle snaps on one street, the other street fades out under a strike."""
    cs = []
    for i, h in enumerate(w.hunters):
        p = h['path']
        pt, _ = at(p, plen(p) * .72)
        cs.append(pt)
    c = (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)
    for i, h in enumerate(w.hunters):
        P = PX(h['path'])
        faded = locked is not None and i != locked
        pts = P.sub(0, P.L, 4)
        pl = Lyr(pbox(pts, 10))
        t = 0.0
        while t < P.L:
            seg = P.sub(t, min(t + 9, P.L), 3)
            pl.line([tuple(x) for x in seg], 2.6 if not faded else 1.6, 255)
            t += 16
        kk = k * (.22 if faded else (1.25 if locked is not None else 1.0))
        cv.neonL(pl, WHITE * .85, core=.7 * kk, g1=(3, .4 * kk), g2=None)
        hy.head(cv, P, P.L * .72, 'E', sc=1.0 if not faded else .8, mode='ghost', k=.9 * kk, col=WHITE * .92)
        if faded:
            m = P.at(P.L * .5)[0]
            st = Lyr((m[0] - 30, m[1] - 24, m[0] + 30, m[1] + 24))
            st.line([(m[0] - 22, m[1] - 14), (m[0] + 22, m[1] + 14)], 3, 255)
            st.line([(m[0] - 22, m[1] + 14), (m[0] + 22, m[1] - 14)], 3, 255)
            cv.neonL(st, WHITE * .7, core=.45, g1=None, g2=None)
    ln = Lyr(pbox(cs + [c], 10))
    for i, p in enumerate(cs):
        if locked is not None and i != locked:
            continue
        ln.line([tuple(c + np.array([0, 24])), tuple(p)], 1.6, 255, dash=(3, 5))
    cv.neonL(ln, WHITE * .8, core=.7 * k, g1=(2, .4 * k), g2=None)
    ui.hunter_eye(cv, c, 54, k, col=WHITE * .92 + LATT * .08)
    return cs, c


def fc_marks(cv, w, tile_fan=True, k=1.0):
    """tiles with hairline leaders, fanned (declutter rule). Returns nothing."""
    pass


EV = {'K1': [('t3_c', 'UNTOUCHED'), ('t2_virus', 'UNTOUCHED'), ('t1_c', 'HOLDS')],
      'K2': [('t3_b', 'UNTOUCHED'), ('t2_breach', 'UNTOUCHED'), ('t1_b', 'SITES_LOST')],
      'K3': [('t3_core', 'UNTOUCHED'), ('t2_intel', 'UNTOUCHED')]}
# only a Site where something HAPPENS carries a tier mark; a pass-through carries none (declutter)
TARGET = {'K1': ('t1_c', 'HOLDS'), 'K2': ('t1_b', 'SITES_LOST'), 'K3': ('t2_intel', 'UNTOUCHED')}


def forecast_world(w, hand=True, tiles=True, idle=IDLE, programs=None, routes=KN, target=None, home_prev=6, ring_r=None):
    TG = dict(TARGET)
    TG.update(target or {})
    cv = new_canvas(w)
    sealed_layers(cv, w)
    stops = {}
    for r in routes:
        R = w.routes[r]
        P = PX(R['path'])
        s_stop = w.visit(r, TG[r][0])
        stops[r] = s_stop
        hy.ribbon(cv, P, R['typ'], R['ext'], s_stop + 20, k=1.0)
        hy.dead_trail(cv, P, s_stop + 40, P.L - 4)
    for r in routes:                       # tier carriers under the towers: target ring on the ground
        hy.target_ring(cv, w.sites[TG[r][0]]['B'], TG[r][1], r=(ring_r or {}).get(r, 46))
    draw_world(cv, w, {'t1_a': 'DOWN'}, PROGRAMS if programs is None else programs, home_kw=dict(hp=44, preview=home_prev), idle=idle)
    for r in routes:
        R = w.routes[r]
        P = PX(R['path'])
        hy.stop_block(cv, P, stops[r] - 2, TG[r][1])
        hy.head(cv, P, R['ext'] + RUN[r], R['typ'], sc=1.8)
    return cv, stops


def tiles_at(cv, w, items, k=1.0, min_d=66.0):
    """intent tiles on their targets, fanned (declutter rule). items: [(sid_or_xy, tier, num)]"""
    anchors = []
    for it in items:
        src = w.sites[it[0]]['crown'] if isinstance(it[0], str) else it[0]
        anchors.append(np.array(src) + np.array([0, -58]))
    pos = hy.fan(anchors, min_d)
    # keep tiles off the ribbons: lift a tile that sits on a street
    pts = np.vstack([w.routes[r]['path'][::3] for r in KN])
    pos2 = []
    for p in pos:
        p = np.array(p, float)
        for _ in range(4):
            if np.min(np.hypot(*(pts - p).T)) < 44:
                p = p + np.array([0, -46])
        pos2.append(tuple(p))
    pos = pos2
    for it, a, p in zip(items, anchors, pos):
        src = np.array(w.sites[it[0]]['crown']) if isinstance(it[0], str) else np.array(it[0])
        hy.leader(cv, src + np.array([0, -4]), np.array(p) + np.array([0, 22]), k=.7)
        hy.hex_tile(cv, p, it[1], it[2], r=30, k=k)


def forecast_marks(cv, w, hand=True, dim=1.0):
    tiles_at(cv, w, [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)])
    hy.home_chip(cv, w.home, 6)
    hy.tally(cv, (w.home[0] + 10, w.home[1] + 150), TALLY, r=17, gap=34, group_gap=14)


def f_forecast(panels=True, name='04_forecast'):
    w = World('default')
    cv, stops = forecast_world(w)
    forecast_marks(cv, w)
    locks(cv, w)
    hunter(cv, w)
    if panels:
        hy.hand(cv, HAND, y=992)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, name)


def f_panels_removed():
    f_forecast(panels=False, name='11_panels_removed')



# ================================================================== the rest of the loop
def known_ribbons(cv, w, k=1.0, upto=None):
    """PLAN-state ribbons: one per known beam, type colour, chevrons."""
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        e = P.L if upto is None else upto.get(r, P.L)
        hy.ribbon(cv, P, R['typ'], R['ext'], e, k=k)


def parked(cv, w, sc=1.5, k=1.0):
    for r, run in RUN.items():
        R = w.routes[r]
        hy.head(cv, PX(R['path']), R['ext'] + run, R['typ'], sc=sc, k=k)


def f_decay():
    w = World('decay')
    cv = new_canvas(w)
    B1, B2 = w.sites['t1_a']['B'], w.sites['t1_b']['B']
    SC.bloom(cv, [B1 + np.array([0, -10]), B2 + np.array([0, -10]), (B1 + B2) / 2 + np.array([0, 30])], [150, 130, 70], seed=5)
    draw_world(cv, w, {'t1_a': 'TAKEN', 't1_b': 'TAKEN'}, {}, home_kw=dict(hp=44), idle=('t1_d', 't1_c'))
    for B in (B1, B2):
        ui.shock(cv, B, 96, VEIN, w=2, k=.4)
    tgt = [(1618, 44), (1618, 44), (1618, 44)]
    src = [B1 + np.array([0, -150]), B2 + np.array([0, -150]), (B1 + B2) / 2 + np.array([0, -190])]
    for i, (s_, t_) in enumerate(zip(src, tgt)):
        f = [.30, .50, .70][i]
        p = s_ + (np.array(t_) - s_) * f + np.array([0, -120 * math.sin(math.pi * f)])
        EB.infected_card(cv, p, angle=-18 + i * 12, sc=1.15 - .3 * f, trail_from=s_)
    hy.hud(cv, 44, 50, 80, 8, 3)
    save(cv, '01_decay')


def f_draw():
    w = World('default')
    cv = new_canvas(w)
    for i, r in enumerate(('A', 'B', 'C')):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, w.routes[r]['ext'] + 380, width=11, seed=3 + i, k=.9)
    DR = {'K1': 640, 'K2': 470, 'K3': 560}
    known_ribbons(cv, w, upto={r: w.routes[r]['ext'] + v for r, v in DR.items()})
    draw_world(cv, w, {'t1_a': 'DOWN'}, {}, home_kw=dict(hp=44), cage_kw=dict(hot=True, phase=.35, alpha=.9), idle=IDLE)
    ui.shock(cv, (w.hq[0] + 140, w.hq[1] - 170), 118, LATT, w=4, k=.9)
    for r, v in DR.items():
        hy.head(cv, PX(w.routes[r]['path']), w.routes[r]['ext'] + v, w.routes[r]['typ'], sc=1.8)
    locks(cv, w)
    c = (w.hq[0] - 330, w.hq[1] - 330)
    ui.hunter_eye(cv, c, 50, .85, col=WHITE * .92 + LATT * .08)
    hy.hand(cv, HAND[:3], y=992)
    for i, (v, t) in enumerate(HAND[3:]):
        hy.vcard(cv, (1230 + i * 150, 840 + i * 40), v, t, angle=26 - i * 14, k=.95)
        tl = Lyr((1250, 780, 1760, 1000))
        tl.line([(1250 + i * 100, 780 + i * 20), (1230 + i * 150, 840 + i * 40)], 2, 255, dash=(4, 8))
        cv.neonL(tl, LATT_D, core=.6, g1=None, g2=None)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '02_draw')


def f_plan():
    w = World('default')
    cv = new_canvas(w)
    sealed_layers(cv, w, k=.8)
    known_ribbons(cv, w)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {'t2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44), idle=IDLE)
    parked(cv, w)
    locks(cv, w, k=.8)
    tc = w.sites['t1_c']['B']
    ui.firewall(cv, tc, 'D', mode='ghost')
    EB.lime_ring(cv, tc + np.array([0, 4]), 50)
    cs, _ = hunter(cv, w, k=.75)
    dp = (720, 770)
    EB.grease_arrow(cv, (dp[0] - 40, dp[1] - 70), (560, 580), (tc[0] + 4, tc[1] + 52))
    hy.hand(cv, HAND, y=992, skip=0)
    hy.vcard(cv, dp, 'GUARD', 'D', angle=-8, lime=True)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '03_plan')


def f_response():
    w = World('default')
    cv, stops = forecast_world(w)
    forecast_marks(cv, w)
    locks(cv, w, k=.9)
    hunter(cv, w, k=.8)
    cv.img *= .62
    ui.shock(cv, (w.hq[0] + 140, w.hq[1] - 170), 118, LATT, w=3.5, k=.7)
    hy.home_chip(cv, w.home, 6)
    hy.tally(cv, (w.home[0] + 10, w.home[1] + 150), TALLY, r=17, gap=34, group_gap=14)
    opts = [('DEPLOY', ['UNTOUCHED', 'SITES_LOST', 'DAMAGED']), ('HOLD', ['HOLDS', 'SITES_LOST', 'DAMAGED']),
            ('MOVE', ['UNTOUCHED', 'HOLDS', 'SITES_LOST']), ('SACRIFICE', ['HOLDS', 'SITES_LOST', 'BREACHED'])]
    for i, (kd, outs) in enumerate(opts):
        hy.stencil_disc(cv, (780 + i * 185, 905), kd, outs, selected=(kd == 'HOLD'), word=kd, seed=5 + i)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '05_response')


def f_playout_impact():
    w = World('default')
    cv = new_canvas(w)
    R = w.routes['K1']
    P = PX(R['path'])
    tcB = w.sites['t1_c']['B']
    wallc = np.array([tcB[0] + 34, tcB[1] + 12 - 24])
    sh = nearest_s(R['path'], wallc)
    hp = wallc
    hy.ribbon(cv, P, 'D', R['ext'], sh, k=1.15)
    P2 = PX(w.routes['K2']['path'])
    hy.ribbon(cv, P2, 'N', w.routes['K2']['ext'], P2.L - 4, k=.28, glow=.3)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44), idle=IDLE)
    ui.focus_dim(cv, hp, 430, .5)
    ui.firewall(cv, tcB, 'D', mode='shatter', impact=tuple(hp), t=.45)
    hy.head(cv, P2, w.routes['K2']['ext'] + 400, 'N', sc=1.5, k=.5)
    ui.flash(cv, hp + np.array([0, -2]), 80, TIER['HOLDS'] * .3 + WHITE * .7, .5)
    hy.hex_flash(cv, hp + np.array([0, -6]), 58, TIER['HOLDS'] * .4 + LATT * .6, k=.95)
    ui.shock(cv, hp + np.array([0, 20]), 54, TIER['HOLDS'], w=3.0, k=.8)
    ui.bits(cv, hp + np.array([4, 0]), TYPE_COL['D'] * .6 + WHITE * .4, n=60, r=150, seed=4)
    hy.head(cv, P, sh - 40, 'D', sc=2.1)
    hy.hex_tile(cv, (tcB[0] + 62, tcB[1] - 128), 'HOLDS', None, r=28)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '06_playout_impact')


def f_playout_home():
    w = World('default')
    cv = new_canvas(w)
    R = w.routes['C']
    P = PX(R['path'])
    end = w.end('C')
    hy.ribbon(cv, P, 'N', R['ext'], end, k=1.2)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    draw_world(cv, w, states, {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44, hit=6, flash=.4), idle=IDLE)
    ui.focus_dim(cv, w.home, 460, .5)
    c = w.home + np.array([0, -18])
    ui.flash(cv, c, 150, TIER['DAMAGED'], .55)
    ui.shock(cv, w.home, 100, TIER['DAMAGED'], w=4)
    ui.shock(cv, w.home, 150, TIER['DAMAGED'], w=2.5, k=.6)
    hy.spark_ticks(cv, w.home, 6, 44)
    ui.bits(cv, c, TIER['DAMAGED'], n=55, r=170, seed=9)
    ui.hex_shards(cv, c, TIER['DAMAGED'], 12, 120, seed=3)
    ui.glitch_tear(cv, (90, 640, 720, 900), 1.0, seed=11, bands=12)
    hy.head(cv, P, end - 46, 'N', sc=2.1)
    hy.hex_tile(cv, (w.home[0] + 96, w.home[1] - 128), 'DAMAGED', None, r=34)
    ui.num_tag(cv, (w.home[0] + 176, w.home[1] - 126), '-6', TIER['DAMAGED'], 60)
    hy.hud(cv, 38, 50, 80, 8, 0, home_col=TIER['DAMAGED'], flash=.6)
    save(cv, '07_playout_home')


def scars(cv, w, k=.5):
    for r in ('K1', 'K2'):
        R = w.routes[r]
        P = PX(R['path'])
        hy.dead_trail(cv, P, R['ext'], P.L - 4, k=k)


def f_aftermath():
    w = World('default')
    cv = new_canvas(w)
    scars(cv, w, .45)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    draw_world(cv, w, states, {'t1_c': ('GUARD', 'D')}, home_kw=dict(hp=38, scar=6), idle=IDLE)
    for sid in ('t1_a', 't1_b'):
        ui.decay_ring(cv, w.sites[sid]['B'], frac=.55)
    p = w.sites['t1_c']['B']
    ui.bits(cv, p + np.array([0, -30]), TYPE_COL['D'], n=18, r=80, seed=2, k=.6)
    ui.bits(cv, w.home + np.array([0, -30]), TIER['DAMAGED'], n=16, r=90, seed=5, k=.6)
    hy.poster(cv, (930, 800), 'DAMAGED', 'DAMAGED', 292, 266)
    hy.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + ui.HEAT * .4)
    save(cv, '08_aftermath')


def f_hq_step():
    w = World('default')
    cv = new_canvas(w)
    scars(cv, w, .3)
    states = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    ta = w.sites['t1_a']['B']
    draw_world(cv, w, states, {'t1_c': ('GUARD', 'D')}, home_kw=dict(hp=38, scar=6), idle=IDLE)
    for sid in ('t1_a', 't1_b'):
        ui.decay_ring(cv, w.sites[sid]['B'], k=.8, frac=.55)
    SC.tower(cv, ta, 1, 'healthy', tint=TIER['UNTOUCHED'], alpha=.6, seed=4)
    hm = w.home
    cb = EB.bez(hm + np.array([20, -30]), (hm[0] + 40, ta[1] + 90), ta + np.array([0, 8]))
    ly = Lyr(pbox(cb, 14))
    ly.line(cb, 3.2, 255, dash=(10, 6))
    cv.neonL(ly, LATT, core=1.0, g1=(3, .8), g2=(10, .5), white=.4)
    ui.glyph_disc(cv, (ta[0] + 6, ta[1] - 118), 24, LATT, g_wrench)
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
    hy.hud(cv, 38, 50, 87, 8, 0, home_col=TIER['DAMAGED'], heat_tint=TIER['DAMAGED'] * .6 + ui.HEAT * .4)
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
    hy.hud(cv, 44, 50, 80, 8, 11, lost=True)
    save(cv, '10_city_lost')


def f_reveal():
    """sealed A opens (the E enforcer is out), B and C stay fogged; the hunter's reticle locks one street, the other fades."""
    w = World('default')
    cv = new_canvas(w)
    for i, r in enumerate(('B', 'C')):
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, w.routes[r]['ext'] + 520, width=11, seed=3 + i, k=.7)
    scars(cv, w, .3)
    RA = w.routes['A']
    PA = PX(RA['path'])
    hy.ribbon(cv, PA, 'E', RA['ext'], PA.L - 4, k=1.1)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44), idle=IDLE)
    hy.head(cv, PA, RA['ext'] + 330, 'E', sc=1.9)
    locks(cv, w, reveal='A')
    cs, ec = hunter(cv, w, locked=0)
    ui.reticle(cv, cs[0], 66, WHITE)
    ui.bits(cv, w.routes['B']['path'][int(len(w.routes['B']['path']) * .06)], FOG, n=30, r=100, seed=3)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '12_reveal_sealed_hunter')




def f_declutter():
    """13: the t1 cluster before / after the declutter rules (a stress case: four targets in the cluster)."""
    w = World('default')
    items = [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t1_d', 'UNTOUCHED', None), ('t1_a', 'SITES_LOST', 2)]
    crops = []
    for rules in (False, True):
        cv, stops = forecast_world(w, idle=IDLE if rules else ())
        if rules:
            tiles_at(cv, w, items)
        else:
            for sid, tier, num in items:
                c = np.array(w.sites[sid]['crown']) + np.array([0, -30])
                hy.hex_tile(cv, c, tier, num, r=30)
        a = finish(cv, vig=.2, scan=.05, fringe=0)
        crops.append(to_img(a).crop((340, 270, 820, 750)).resize((940, 940), Image.LANCZOS))
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    sheet.paste(crops[0], (10, 130))
    sheet.paste(crops[1], (970, 130))
    d = ImageDraw.Draw(sheet)
    f1 = font(46, False, 800, 75)
    f2 = font(26, False, 600, 75)
    d.text((20, 18), 'NAIVE: 4 targets, every Site full height, tiles on the towers', font=f2, fill=(200, 210, 235))
    d.text((980, 18), 'RULES: idle Sites collapse, one fanned tile per target on a hairline leader', font=f2, fill=(127, 239, 255))
    d.text((20, 62), '1  idle collapse    2  one tile per target, fan >= 66 px    3  two lanes max (+-13 px)    4  programs on the ground side', font=f2, fill=(150, 160, 190))
    sheet.save(FR + '13_declutter_t1.png')
    print('saved 13_declutter_t1')


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
