"""The ten beats + extras. python frames.py [name ...]"""
import sys, math, random
from build import *

N = lambda s, k: s.sc.nodes[k]
HQ_NODE = lambda s: s.sc.nodes['the_genome_core']


def s_at(path, pt):
    """arclength of the path sample nearest to pt"""
    p = rs(path, 2.0)
    cl = cum(p)
    i = min(range(len(p)), key=lambda i: math.dist(p[i], pt))
    return cl[i]


def flat(f, path, s0, col, alpha=0.5, w=2.6):
    seg = sub(path, s0, plen(path))
    f.L('add', bloom=0.5)
    f.dline(seg, w, tuple(int(v * alpha) for v in col), 5, 7)
    q, d = at(path, s0)
    f.L('over')
    nx, ny = -d[1], d[0]
    f.line([(q[0] + nx * 13, q[1] + ny * 13), (q[0] - nx * 13, q[1] - ny * 13)], 5, (6, 4, 12, 255), cap=False)
    f.line([(q[0] + nx * 12, q[1] + ny * 12), (q[0] - nx * 12, q[1] - ny * 12)], 2.8, (230, 245, 255, 255), cap=False)


def order_tag(f, path, lane, label, col, s=46):
    q, d = at(offset(path, lane) if lane else path, s)
    f.L('over')
    f.ell(q, 12, 12, (6, 10, 20, 255), col, 2.6)
    f.txt(q, label, 15, (255, 255, 255), mono=True)


def beam_cut(st, key, lane, s_cut=None, alpha=1.0, label=None, hot=0.0, head=False, dimflat=0.7):
    t = TYPES[key]
    path = st.paths[key]
    if s_cut is None:
        beam(st.f, path, t, lane=lane, alpha=alpha, hot=hot, head=head)
    else:
        beam(st.f, path, t, lane=lane, s1=s_cut, alpha=alpha, hot=hot, head=head)
        flat(st.f, offset(path, lane), s_cut, TYPE_COL[t], alpha * dimflat)
    if label:
        order_tag(st.f, path, lane, label, TYPE_COL[t])


def ghost_fuse(f, c, t, a=200):
    f.L('add', bloom=0.9)
    a0, a1 = gpt(c, -1.0, 0), gpt(c, 1.0, 0)
    a0, a1 = (a0[0], a0[1] - 9), (a1[0], a1[1] - 9)
    f.dline([a0, a1], 9, (150, 205, 235), 8, 6)
    for q in (a0, a1):
        f.ell(q, 8, 5, None, (230, 245, 255), 2)
    wave_chip(f, (c[0], c[1] - 40), t, 12)


def stop_count(f, c, n, col=TIERC['HOLDS']):
    f.L('over')
    f.ell(c, 13, 13, (4, 20, 24, 255), col, 2.8)
    f.txt(c, str(n), 17, (255, 255, 255), mono=True)


def analyzer(f, x0=968, y0=884, w=620, h=176):
    """logic-analyzer strip: one lane per beam in firing order. wave -> fuse/noise -> outcome badge(s). No sentences."""
    f.L('shadow', blur=6)
    f.rr((x0 + 4, y0 + 8, x0 + w + 4, y0 + h + 8), 14, (0, 0, 0, 190))
    f.flush()
    f.L('over')
    f.rr((x0, y0, x0 + w, y0 + h), 14, (4, 14, 22, 244), (110, 226, 255), 2.6)
    for i in range(0, h, 4):
        f.line([(x0 + 6, y0 + i), (x0 + w - 6, y0 + i)], 1, (255, 255, 255, 7), cap=False)
    rows = [('D', 'run', ['HOLDS'], '1'), ('D', 'run', ['HOLDS'], '2'), ('?', 'sealed', ['SITES_LOST', 'HOLDS', 'DAMAGED'], ''),
            ('E', 'hunter', ['UNTOUCHED', 'SITES_LOST'], '')]
    for i, (t, kind, outs, lab) in enumerate(rows):
        y = y0 + 28 + i * 40
        f.line([(x0 + 14, y + 20), (x0 + w - 14, y + 20)], 1, (60, 90, 110, 160), cap=False)
        if kind == 'run':
            col = TYPE_COL[t]
            # waveform runs to the fuse then flatlines
            xs = [x0 + 64 + k for k in range(0, 300, 2)]
            wv = []
            for xx in xs:
                u = ((xx - xs[0]) / 40.0) % 1.0
                v = math.sin(u * 2 * math.pi)
                wv.append((xx, y + (v * 11 if xx < x0 + 290 else 0)))
            f.line(wv, 3.2, col)
            f.line([(x0 + 292, y - 18), (x0 + 292, y + 18)], 3, (230, 245, 255), cap=False)   # the fuse
            fuse_flat(f, (x0 + 292, y), 13)
            f.line([(x0 + 306, y), (x0 + 400, y)], 2, (110, 130, 150), cap=False)
            wave_chip(f, (x0 + 30, y), t, 14)
            f.txt((x0 + 30, y + 0), '', 10, WHITE)
        elif kind == 'sealed':
            rng = random.Random(3)
            for k in range(160):
                f.px(x0 + 64 + k * 1.9, y + rng.uniform(-11, 11), 2, (190, 180, 255, 220))
            glyph(f, 'lock', (x0 + 30, y), 11, (200, 200, 230), 2.4)
        else:
            rng = random.Random(8)
            for k in range(110):
                f.px(x0 + 64 + k * 1.9, y + rng.uniform(-9, 9), 2, (255, 245, 160, 220))
            glyph(f, 'saw', (x0 + 30, y), 12, TYPE_COL['E'], 2.4)
        # outcomes (fork)
        n = len(outs)
        for j, tr in enumerate(outs):
            xx = x0 + w - 70 - (n - 1 - j) * 52 if kind != 'run' else x0 + w - 70
            if kind != 'run':
                f.line([(x0 + 64 + (160 if kind == 'sealed' else 110) * 1.9, y), (xx - 16, y)], 1.8, (130, 140, 170), cap=False)
            tier_badge(f, (xx, y), tr, 13)
    # HOME summary on the right edge of the strip: worst case ring
    f.L('add', bloom=0.8)
    f.line([(x0 + w - 14, y0 + 14), (x0 + w - 14, y0 + h - 14)], 1.5, (60, 90, 110), cap=False)


# ---------------------------------------------------------------- plan / forecast shared map layer
def plan_map(s, placed=True, fuse_c=True, drag=False, cut=True, hunter_lock=None, header=True, known_alpha=1.0):
    f = s.f
    cK = s_at(s.paths['K1'], N(s, 't1_c')) - 6 if cut else None
    cK2 = s_at(offset(s.paths['K2'], 11), N(s, 't1_c')) - 6 if cut else None
    sealed_bands(s)
    beam_cut(s, 'K1', -11, cK, known_alpha, '1')
    beam_cut(s, 'K2', 11, cK2, known_alpha, '2')
    if header:
        sealed_header(s, [('A', 'locked', 'E'), ('B', 'locked', 'D'), ('C', 'locked', 'N')])
    hunter_ghosts(s, lock=hunter_lock)


# ---------------------------------------------------------------- 01 DECAY
def hunter_fork(s, lock=None):
    """two reticles, one on each candidate street, joined by a seesaw arrow: 'one of these two'"""
    f = s.f
    m = [at(s.paths[k], plen(s.paths[k]) * 0.5)[0] for k in ('H0', 'H1')]
    for i, q in enumerate(m):
        reticle(f, q, 58, (255, 255, 255), 3.8)
    f.L('add', bloom=1.2)
    f.dline([m[0], (m[0][0] + (m[1][0] - m[0][0]) * .5, m[0][1] - 70), m[1]], 2.6, (255, 255, 255), 8, 8)
    for a, b in ((m[0], m[1]), (m[1], m[0])):
        d = (a[0] - b[0], a[1] - b[1])
        l = math.hypot(*d) or 1
        q = (a[0] - d[0] / l * 52, a[1] - d[1] / l * 52 - 26)
        f.ell(q, 5, 5, (255, 255, 255))


def f01():
    cen = [NODES['t1_a'], NODES['t1_b']]
    s = Stage(states={'t1_a': 'TAKEN', 't1_b': 'TAKEN'}, infect=(cen + [NODES['t1_c'], NODES['t1_d']], [150, 160, 70, 55], 3, 1.0))
    f = s.f
    tally_fly(s, [N(s, 't1_b')], (428, 46), t=0.55)
    hud(f, 44, 80, 8, 1)
    s.save('01_decay')


# ---------------------------------------------------------------- 02 DRAW
def f02():
    s = Stage(states={'t1_a': 'DOWN'})
    f = s.f
    beam_cut(s, 'K1', -11, None, 0.55)
    beam_cut(s, 'K2', 11, None, 0.55)
    sealed_bands(s, 0.7)
    sealed_header(s, [('A', 'locked', 'E'), ('B', 'locked', 'D'), ('C', 'locked', 'N')])
    hunter_ghosts(s)
    # deck pile bottom right, cards fanning into the hand, two still in flight
    deck_slot(f, (1760, 950))
    hand(f, HAND[:5], c=(740, 990), spread=104)
    for i, ((k, t), (x, y, ang)) in enumerate(zip(HAND[5:], [(1250, 905, -16), (1500, 930, -28)])):
        for tr in range(4, 0, -1):
            f.L('over', op=0.14 * (5 - tr))
            paste(f, card(k, t), (x + tr * 34, y + tr * 6), ang, 0.95, shadow=0)
        f.L('over')
        paste(f, card(k, t), (x, y), ang, 1.0)
    hud(f, 44, 80, 8, 0)
    go_button(f, (1840, 1010), (90, 110, 130))
    s.save('02_draw')


# ---------------------------------------------------------------- 03 PLAN
def f03():
    s = Stage(states={'t1_a': 'DOWN'}, defs=[('t1_a', 'N', 'GUARD'), ('t1_b', 'E', 'SHIFT')])
    f = s.f
    plan_map(s, cut=True)
    c = gpt(N(s, 't1_c'), 0.0, 1.9)
    ghost_fuse(f, c, 'D')
    ground_halo(f, gpt(N(s, 't1_c'), 0, 0.9), LIME, 46)
    # drop rings on the other sites a card could go on (dim): chips on the beam paths
    f.L('add', bloom=0.8)
    for k in ('t1_b', 't2_virus', 't2_breach'):
        f.line(ground_ring(N(s, k), 30), 2.0, (100, 190, 210))
    stop_count(f, (c[0] + 36, c[1] - 56), 2)
    # drag: the picked card lifts out of the hand, a dashed wire pulls to the drop ring
    hand(f, HAND[:3] + HAND[4:], c=(720, 992), spread=96, scale=0.92)
    f.L('add', bloom=1.0)
    f.dline([(620, 876), (560, 700), (520, 600), c], 3.2, (255, 255, 255), 10, 8)
    f.L('over')
    paste(f, card('fuse', 'D'), (590, 760), 10, 1.12)
    hud(f, 44, 80, 8, 0)
    go_button(f, (1840, 1010), (90, 110, 130))
    s.save('03_plan')
    return s


# ---------------------------------------------------------------- 04 FORECAST
def forecast_stage(panels=True):
    s = Stage(states={'t1_a': 'DOWN'}, defs=DEF_DEFAULT, preview=4)
    f = s.f
    plan_map(s, cut=True)
    hunter_lock = None
    # probes
    probe(f, gpt(N(s, 't1_c'), 0, 0), 'HOLDS', 2, up=-52, dx=118)
    probe(f, gpt(N(s, 't1_b'), 0, 0), 'SITES_LOST', 1, up=88, dx=56)
    ch = N(s, 'home')
    probe(f, (ch[0] + 4, ch[1] - 14), 'DAMAGED', '-4', up=118, dx=0)
    hunter_fork(s)
    hud(f, 44, 80, 8, 0)
    if panels:
        hand(f, HAND[:3] + HAND[4:], c=(520, 996), spread=84, scale=0.8)
        analyzer(f)
        go_button(f, (1840, 1010), (110, 226, 255))
    return s


def f04():
    s = forecast_stage(True)
    s.save('04_forecast')


def f11():
    s = forecast_stage(False)
    s.save('11_panels_removed')


# ---------------------------------------------------------------- 05 RESPONSE
def f05():
    s = Stage(states={'t1_a': 'DOWN'}, defs=DEF_DEFAULT, preview=4)
    f = s.f
    plan_map(s, cut=True)
    ch = N(s, 'home')
    probe(f, (ch[0] + 4, ch[1] - 14), 'DAMAGED', '-4', up=118)
    hud(f, 44, 80, 8, 0)
    specs = [('plus', 'DEPLOY', ['HOLDS', 'SITES_LOST', 'DAMAGED']), ('shield', 'HOLD', ['HOLDS', 'SITES_LOST', 'DAMAGED']),
             ('arrow', 'MOVE', ['UNTOUCHED', 'SITES_LOST', 'DAMAGED']), ('x', 'SACRIFICE', ['UNTOUCHED', 'SITES_LOST', 'BREACHED'])]
    f.L('over')
    for i, (g, wd, dots) in enumerate(specs):
        x = 560 + i * 268
        sp = crt_chip(240, 112, g, wd, (110, 226, 255), dots=dots)
        paste(f, sp, (x, 970), 0, 1.0)
    f.L('add', bloom=1.2)
    x = 560 + 268
    f.rr((x - 130, 970 - 66, x + 130, 970 + 66), 16, None, LIME, 4)
    go_button(f, (1840, 1010), (110, 226, 255))
    s.save('05_response')


# ---------------------------------------------------------------- 06 PLAYOUT
def pulse_ready(s):
    f = s.f
    hq = HQ_NODE(s)
    f.L('add', bloom=1.4)
    f.ell(hq, 40, 24, None, (255, 255, 255), 3)


def f06a():
    s = Stage(states={'t1_a': 'DOWN'}, defs=DEF_DEFAULT, blown=('t1_c',), preview=0)
    f = s.f
    fc = gpt(N(s, 't1_c'), 0, 1.9)
    p1 = s.paths['K1']
    sK1 = s_at(offset(p1, -11), N(s, 't1_c')) - 6
    # beam 1 just stopped: the wave runs to the fuse and flat-lines behind it
    beam(f, p1, 'D', lane=-11, s1=sK1, alpha=1.0, hot=0.7, head=True)
    flat(f, offset(p1, -11), sK1, D_BLUE, 0.4)
    beam_cut(s, 'K2', 11, None, 0.30)
    sealed_bands(s, 0.45)
    hunter_ghosts(s)
    # impact at the fuse: flash, sparks, bits, glass shards, shockwave
    f.L('add', bloom=1.6)
    f.ell(fc, 44, 26, (120, 130, 150))
    f.ell(fc, 22, 13, (255, 255, 255))
    for r_, w_ in ((46, 4), (68, 2.5)):
        f.line(ground_ring(fc, r_), w_, tuple(int(v * (1 - (r_ - 46) / 60)) for v in TIERC['HOLDS']))
    sparks(f, (fc[0], fc[1] - 14), 46, 8, 84, seed=4)
    bits(f, (fc[0], fc[1] - 20), 26, 100, seed=2)
    f.L('over')
    rng = random.Random(9)
    for _ in range(12):  # glass shards
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(20, 70)
        q = (fc[0] + math.cos(a) * d, fc[1] - 14 + math.sin(a) * d * .7)
        f.poly([q, (q[0] + rng.uniform(4, 10), q[1] + rng.uniform(-4, 4)), (q[0] + rng.uniform(-4, 4), q[1] + rng.uniform(4, 10))],
               (190, 230, 255, 220), (255, 255, 255), 1)
    # the verdict of this beat floats up: HOLDS badge, beam number
    tier_badge(f, (fc[0] + 10, fc[1] - 120), 'HOLDS', 24)
    order_tag(f, p1, -11, '1', D_BLUE)
    hud(f, 44, 80, 8, 0)
    s.save('06_playout_impact')


def f06b():
    s = Stage(states={'t1_a': 'DOWN', 't1_b': 'healthy'}, defs=DEF_DEFAULT, blown=('t1_c',), hp=44, preview=0)
    f = s.f
    hc = N(s, 'home')
    beam_cut(s, 'K1', -11, None, 0.22)
    p = s.paths['K2']
    beam(f, p, 'N', lane=0, alpha=1.0, hot=0.8, head=True)      # the revealed sealed C: a magenta square wave
    sealed_bands(s, 0.35, which='AB')
    order_tag(f, p, 0, '3', N_MAG, 30)
    # HOME burns: shockwave, sparks, smoke, bits; the ring tears
    f.L('add', bloom=1.6)
    f.ell(hc, 52, 30, (150, 60, 20))
    f.ell(hc, 26, 15, (255, 235, 200))
    for r_ in (70, 100, 132):
        f.line(ground_ring(hc, r_), 4 - (r_ - 70) / 24, tuple(int(v * (1 - (r_ - 70) / 90)) for v in TIERC['DAMAGED']))
    sparks(f, (hc[0], hc[1] - 18), 70, 10, 120, seed=7, cols=((255, 255, 255), (255, 170, 60), (255, 110, 30), (255, 70, 220)))
    smoke(f, (hc[0] + 10, hc[1] - 20), 9, 3)
    bits(f, (hc[0], hc[1] - 30), 34, 130, seed=5, col=(255, 150, 230))
    damage_num(f, (hc[0] + 6, hc[1] - 190), '-4', TIERC['DAMAGED'])
    hud(f, 40, 85, 8, 0, home_flash=1.0)
    s.save('07_playout_home')


# ---------------------------------------------------------------- 08 AFTERMATH
def f08(states_only=False):
    st = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    s = Stage(states=st, defs=DEF_DEFAULT, blown=('t1_c',), hp=40, preview=0)
    f = s.f
    hc = N(s, 'home')
    s.sc.decay_clock(gpt(N(s, 't1_a'), 0, 0), 0.9, True)
    s.sc.decay_clock(gpt(N(s, 't1_b'), 0, 0), 0.3, False)
    # scorched HOME: soot, a thin smoke wisp
    f.L('shadow', blur=10)
    f.ell((hc[0], hc[1] + 6), 54, 28, (0, 0, 0, 120))
    f.flush()
    smoke(f, (hc[0] + 12, hc[1] - 24), 5, 6)
    # the verdict: a corp-paper tag hung off HOME, stamped
    f.L('over')
    tp = (hc[0] + 250, hc[1] + 90)
    f.line([(hc[0] + 40, hc[1] + 10), (hc[0] + 100, hc[1] + 50), (tp[0] - 140, tp[1] - 6)], 2.6, (220, 220, 230, 255))
    paste(f, tag('DAMAGED', TIERC['DAMAGED']), tp, 4, 1.0)
    hud(f, 40, 85, 8, 0)
    s.save('08_aftermath')


# ---------------------------------------------------------------- 09 HQ STEP
def token(glyph_name, num, col=(110, 226, 255), r=30, hot=False):
    s = Sprite(r * 2 + 40, r * 2 + 64)
    cx, cy = r + 20, r + 20
    s.ell((cx, cy), r, r, (6, 16, 26), col, 3.4)
    s.ell((cx, cy), r - 6, r - 6, None, (60, 90, 110), 1.2)
    glyph(s, glyph_name, (cx, cy), r * .5, col, 3.6, col)
    if num is not None:
        s.rr((cx - 28, cy + r - 4, cx + 28, cy + r + 24), 10, (6, 16, 26), col, 2.4)
        s.txt((cx, cy + r + 10), str(num), 22, (255, 255, 255), mono=True)
    return s


def f09():
    st = {'t1_a': 'DOWN', 't1_b': 'DOWN'}
    s = Stage(states=st, defs=DEF_DEFAULT, blown=('t1_c',), hp=40, preview=0)
    f = s.f
    hc = N(s, 'home')
    s.sc.decay_clock(gpt(N(s, 't1_a'), 0, 0), 0.9, True)
    s.sc.decay_clock(gpt(N(s, 't1_b'), 0, 0), 0.3, False)
    offers = [('t1_a', 'wrench', 20, (-30, -118), True), ('t1_b', 'wrench', 10, (46, -108), False),
              ('home', 'heart', 25, (-70, -124), False)]
    f.L('add', bloom=0.9)
    pos = {}
    for k, g, n, (dx, dy), foc in offers:
        c = N(s, k)
        q = (c[0] + dx, c[1] + dy)
        pos[k] = q
        f.dline([c, q], 2.4, (230, 160, 100), 6, 6)
    f.L('over')
    for k, g, n, d, foc in offers:
        gg = 'plus' if g == 'heart' else g
        paste(f, token('wrench' if g == 'wrench' else 'heart', n, (110, 226, 255)), pos[k], 0, 1.0)
        if g == 'heart':
            glyph(f, 'plus', (pos[k][0] + 15, pos[k][1] - 15), 6, (110, 226, 255), 2.6)
    # lime focus on the most urgent DOWN chip (decay about to take it)
    ground_halo(f, gpt(N(s, 't1_a'), 0, 0), LIME, 46)
    # a card-shop token (buy a component) + end-turn chevrons
    paste(f, token('card_plus', 15, (110, 226, 255)), (860, 930), 0, 1.0)
    go_button(f, (1840, 1010), (110, 226, 255))
    hud(f, 40, 85, 8, 0)
    s.save('09_hq_step')


# ---------------------------------------------------------------- 10 CITY LOST
def f10():
    ids = ['t1_a', 't1_b', 't1_c', 't1_d']
    cen = [NODES[k] for k in ids] + [NODES[k] for k in ('home', 't2_virus', 't2_breach', 't2_intel', 't3_b', 't3_c', 't3_core')] + [(1180, 300), (700, 900)]
    rad = [200, 200, 200, 200, 170, 220, 220, 200, 230, 230, 200, 260, 220]
    s = Stage(states={k: 'INFECTED' for k in ids}, hp=40, infect=(cen, rad, 5, 1.0), marks=True)
    f = s.f
    hud(f, 40, 85, 4, 5)
    # the skull, the verdict glyph
    c = (960, 470)
    f.L('shadow', blur=26)
    f.ell(c, 230, 200, (20, 4, 28, 235))
    f.flush()
    f.L('add', bloom=1.2)
    f.ell(c, 150, 150, None, (255, 120, 200), 3)
    f.L('over')
    glyph(f, 'skull', c, 150, (243, 230, 242), 4, (243, 230, 242))
    f.L('add', bloom=1.0)
    for r_ in (176, 200):
        f.ell(c, r_, r_, None, (120, 40, 100), 2)
    s.save('10_city_lost')


# ---------------------------------------------------------------- extras: wordless sealed reveal + hunter lock
def f12():
    s = Stage(states={'t1_a': 'DOWN'}, defs=DEF_DEFAULT)
    f = s.f
    beam_cut(s, 'K1', -11, None, 0.28)
    beam_cut(s, 'K2', 11, None, 0.28)
    sealed_bands(s, 0.55, which='BC')
    # A resolves from static into a yellow sawtooth: the ciphertext collapses into the signal
    pA = s.paths['A']
    LA = plen(pA)
    beam(f, offset(pA, 0), 'E', lane=26, s1=LA, alpha=1.0, hot=0.5)
    hq = HQ_NODE(s)
    f.L('add', bloom=1.5)
    f.ell(hq, 44, 26, None, (255, 240, 120), 3)
    sealed_header(s, [('A', 'open', 'E'), ('B', 'locked', 'D'), ('C', 'locked', 'N')])
    hunter_ghosts(s)
    hud(f, 44, 80, 8, 0)
    s.save('12_sealed_reveal')


def f13():
    s = Stage(states={'t1_a': 'DOWN'}, defs=DEF_DEFAULT, blown=('t1_c',))
    f = s.f
    beam_cut(s, 'K1', -11, None, 0.18)
    beam_cut(s, 'K2', 11, None, 0.18)
    sealed_header(s, [('A', 'dead', 'E'), ('B', 'dead', 'D'), ('C', 'dead', 'N')])
    p0, p1 = s.paths['H0'], s.paths['H1']
    f.L('add', bloom=0.5)
    f.dline(p0, 1.8, (80, 76, 100), 4, 12)
    beam(f, p1, 'E', lane=0, alpha=1.0, hot=0.6, head=True)
    mid = at(p1, plen(p1) * 0.5)[0]
    reticle(f, mid, 42, (255, 255, 255), 4.0)
    reticle(f, mid, 62, (255, 226, 26), 2.4)
    f.L('add', bloom=1.4)
    f.ell(mid, 6, 6, (255, 255, 255))
    mid0 = at(p0, plen(p0) * 0.5)[0]
    reticle(f, mid0, 70, (90, 86, 110), 1.8)
    hud(f, 44, 80, 8, 0)
    s.save('13_hunter_lock')


FRAMES = {'01_decay': f01, '02_draw': f02, '03_plan': f03, '04_forecast': f04, '05_response': f05, '06a': f06a, '06b': f06b,
          '08_aftermath': f08, '09_hq_step': f09, '10_city_lost': f10, '11_panels_removed': f11, '12': f12, '13': f13}

if __name__ == '__main__':
    want = sys.argv[1:] or list(FRAMES)
    for k in want:
        FRAMES[k]()
