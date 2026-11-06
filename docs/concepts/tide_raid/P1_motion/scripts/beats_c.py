"""Beat renderers, part C: wheatpaste poster slam, Bloom creep (DECAY), CITY LOST flood."""
from stage import *
from beats_b import cworld
import beats_a as A

PC = np.array([930.0, 800.0])


# ================================================================== POSTER SLAM
def _after_world():
    return cworld('after', states={'t1_a': 'DOWN', 't1_b': 'DOWN'}, programs={'t1_c': ('GUARD', 'D')},
                  home_kw=dict(hp=38, scar=6))


def _poster_spr():
    S = stage()
    box = (PC[0] - 230, PC[1] - 230, PC[0] + 230, PC[1] + 230)
    return S.cached('poster', lambda: spr(lambda cv: hy.poster(cv, tuple(PC), 'DAMAGED', 'DAMAGED', 292, 266, ang=0.0), box))


JIT = [(5, -3, 2.0), (-4, 3, -1.6), (3, -2, 1.1), (-2, 1, -.7), (1, -1, .3), (0, 0, 0)]


def b_poster(f, reduce=False):
    """wheatpaste slam: pixel-block dissolve 0-10, slap 8-12, jitter 12-18, hold to 48."""
    S = stage()
    cv = _after_world()
    box = (int(PC[0] - 190), int(PC[1] - 180), int(PC[0] + 190), int(PC[1] + 180))
    sp = _poster_spr()
    if not reduce:
        dimk = .35 * e('OUT_QUAD', f, 0, 4) * (1 - e('LINEAR', f, 14, 26))
        ui.focus_dim(cv, PC, 380, dimk * 1.2)
        # dissolve: blocks of the verdict colour appear (0..6) and clear (4..10)
        a_ = prog(f, 0, 6)
        b_ = prog(f, 4, 10)
        if 0 < f < 10:
            m = pixel_blocks(cv, box, 0, seed=3, cell=14)
            vis = ((m < a_) & (m >= b_)).astype(np.float32)
            cv.add(TIER['DAMAGED'] * .8 + PAPER * .2, vis, .75, (box[0], box[1]))
            cv.over(INK, blur(vis, 4) * .0 + vis * 0, 0, (box[0], box[1]))
        # slap
        if f >= 8:
            t = e('IN_CUBIC', f, 8, 12)
            sc = 1.5 - .5 * t
            ang = -9 + 4.5 * t
            off = np.array([0.0, 0.0])
            if f >= 12:
                j = JIT[min(f - 12, 5)]
                off = np.array([j[0], j[1]], float)
                ang = -4.5 + j[2]
            xf = xform(sp, sc, ang)
            kk = e('LINEAR', f, 8, 10)
            P_, a_x, (x0, y0) = xf
            sh_k = .55 * (1 + (sc - 1) * 1.2)
            cv.over(INK, blur(a_x, 9), sh_k * kk, (x0 + int(6 * sc + off[0]), y0 + int(12 * sc + off[1])))
            comp(cv, xf, kk, off)
            if 12 <= f < 17:
                tt = prog(f, 12, 17)
                ui.flash(cv, PC, 210, PAPER, .45 * (1 - tt))
                ui.shock(cv, PC, 120 + 60 * out_expo(tt), PAPER, w=3, k=.55 * (1 - tt))
    else:
        # reduce-motion: cross-fade in place at the final pose, no dissolve, jitter or flash; hold keeps the read
        xf = xform(sp, 1.0, -4.5)
        kk = e('LINEAR', f, 6, 14)
        P_, a_x, (x0, y0) = xf
        cv.over(INK, blur(a_x, 9), .55 * kk, (x0 + 6, y0 + 12))
        comp(cv, xf, kk, (0, 0))
    return cv.out()


# ================================================================== BLOOM CREEP (DECAY)
NEAR = ('t1_a', 't1_b', 't1_c', 't1_d', 't2_breach')
STEP_R = [0, 44, 62, 78, 92, 106, 118, 130, 142, 152, 162]


def _bloom_far():
    S = stage()
    w = S.w

    def build():
        cv = S.cv()
        SC.solace_cage(cv, S.hq, alpha=.58)
        items = [(s['B'][1], sid) for sid, s in w.sites.items() if sid not in NEAR]
        items.append((w.home[1], 'home'))
        for _, sid in sorted(items):
            if sid == 'home':
                SC.home_deck(cv, w.home, hp=44)
                continue
            s = w.sites[sid]
            SC.tower(cv, s['B'], s['tier'], 'healthy', seed=sum(map(ord, sid)) % 97, alpha=.60, hs=1.0)
            pr = PROGRAMS.get(sid)
            if pr:
                verb, typ = pr
                if verb == 'SHIFT':
                    ui.decoy(cv, s['B'], typ, s['tier'])
        return cv.img.copy()
    return Cv(S.cached('bloomfar', build))


def _tower_spr(sid, state, hs=1.0):
    S = stage()
    s = S.w.sites[sid]
    B = s['B']
    box = (B[0] - 90, B[1] - 190, B[0] + 90, B[1] + 50)
    return S.cached(('tw', sid, state), lambda: spr(lambda cv: SC.tower(cv, B, s['tier'], state, seed=sum(map(ord, sid)) % 97, alpha=.60), box))


def _mark_spr(sid, kind):
    S = stage()
    B = S.w.sites[sid]['B']
    box = (B[0] - 90, B[1] - 110, B[0] + 90, B[1] + 50)

    def fn(cv):
        if kind == 'DOWN':
            ui.grease_down(cv, (B[0], B[1] - 34), 26, seed=sum(map(ord, sid)) % 50)
        else:
            ui.grease_taken(cv, (B[0], B[1] - 30), 26, seed=sum(map(ord, sid)) % 50)
    return S.cached(('mk', sid, kind), lambda: spr(fn, box))


def bloom_radius(f, reduce=False, f0=26):
    """radius of the front at frame f: 10 steps, one every 5 f, each 3 f OUT_QUAD."""
    if reduce:
        return 150.0 * e('LINEAR', f, 20, 28) if False else (STEP_R[-1] if f >= 28 else 0.0)
    R = 0.0
    for j in range(1, len(STEP_R)):
        a = f0 + 5 * (j - 1)
        t = e('OUT_QUAD', f, a, a + 3)
        R = STEP_R[j - 1] + (STEP_R[j] - STEP_R[j - 1]) * t if t > 0 else R
        if t <= 0:
            break
    return R


def _bloom_frame(f, R, down, reduce):
    S = stage()
    w = S.w
    cv = _bloom_far()
    Ba, Bb = w.sites['t1_a']['B'], w.sites['t1_b']['B']
    cen = [Ba + np.array([0, -10]), Bb + np.array([0, -10]), (Ba + Bb) / 2 + np.array([0, 30])]
    seed_r = 40 * (e('LINEAR', f, 20, 26) if reduce else e('OUT_BACK', f, 20, 26))
    rad = [max(seed_r, R), max(seed_r, R), max(R * .5, 0) if R > 40 else 0]
    if R > 0 or seed_r > 2:
        if rad[2] < 1:
            SC.bloom(cv, cen[:2], rad[:2], seed=5)
        else:
            SC.bloom(cv, cen, rad, seed=5)
    return cv


def b_bloom(f, reduce=False):
    """test D frame f (0..105). DOWN clock 0-20, seed 20-26, creep 26-74 in 5 f steps, hold to 96. Reduce: state cut 20-28."""
    S = stage()
    w = S.w
    if reduce:
        if f < 20:
            cv = _bloom_far()
            R = 0
            taken = 0.0
        else:
            t = e('IN_OUT_QUAD', f, 20, 28)
            cvA = _bloom_far()
            cvB = _bloom_frame(99, STEP_R[-1], False, False)
            cv = Cv(cvA.img * (1 - t) + cvB.img * t)
            taken = t
    else:
        R = bloom_radius(f)
        cv = _bloom_frame(f, R, f < 20, reduce)
        taken = 1.0 if f >= 20 else 0.0
    # sites near the front: DOWN until 20 (clock drains), TAKEN stumps after
    for sid in NEAR:
        st = 'healthy'
        if sid in ('t1_a', 't1_b'):
            st = 'TAKEN' if (taken > .5) else 'DOWN'
        sp = _tower_spr(sid, st)
        comp(cv, sp)
        if sid in ('t1_a', 't1_b'):
            B = w.sites[sid]['B']
            if st == 'DOWN':
                comp(cv, _mark_spr(sid, 'DOWN'))
                ui.decay_ring(cv, B, k=.9, frac=1 - .85 * (f / 20.0 if f < 20 else 1))
            else:
                comp(cv, _mark_spr(sid, 'TAKEN'), taken if reduce else 1.0)
    return cv.out()


def b_bloom_board(f):
    """board 10: the test frame plus the INFECTED cards that fly off to the deck strip (30-46)."""
    a = b_bloom(f)
    return a


# ================================================================== CITY LOST FLOOD
def b_lost(f, reduce=False):
    """board 11: HOME's last hit 0-8, flood 8-56 (IN_OUT_QUAD), desaturate 20-44, tear 44-50, skull 56-62, ring 60-70."""
    S = stage()
    w = S.w
    ids = ['t1_a', 't1_b', 't1_c', 't1_d']
    Bs = [w.sites[i]['B'] for i in ids]
    cen = [b + np.array([0, -20]) for b in Bs] + [w.sites['t2_breach']['B'], w.sites['t2_virus']['B'], w.home]
    full = [700, 680, 680, 640, 560, 520, 560]
    cv = S.cv()
    if reduce:
        t = e('LINEAR', f, 8, 20)
    else:
        t = e('IN_OUT_QUAD', f, 8, 56)
    if t > .005 and not reduce:
        SC.bloom(cv, cen, [max(8, r * t) for r in full], seed=7)
    elif reduce and t > .005:
        SC.bloom(cv, cen, full, seed=7)
    states = {i: 'TAKEN' for i in ids} if t > .35 else {'t1_a': 'DOWN'}
    draw_world(cv, w, states, {}, home_kw=dict(hp=44, tint=(VEIN * .6 + HOT * .4) if t > .6 else None), cage_kw=dict(hot=t > .5, phase=.8))
    if reduce and t < 1:
        base = S.cv()
        draw_world(base, w, {'t1_a': 'DOWN'}, {}, home_kw=dict(hp=44))
        cv.img = base.img * (1 - t) + cv.img * t
    if f < 8 and not reduce:
        c = S.home + np.array([0, -18])
        ui.flash(cv, c, 230, WHITE, [.95, .95, .6, .4, .3, .2, .1, .05][f])
        ui.shock(cv, S.home, 100 * out_expo(prog(f, 0, 8)) + 6, TIER['BREACHED'], w=4, k=1 - prog(f, 0, 8))
    img = cv.out()
    lum = (img * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    d = .55 * e('LINEAR' if reduce else 'IN_OUT_QUAD', f, 20, 44)
    img = img * (1 - d) + (lum * np.array([1.0, .9, 1.05], np.float32)) * d
    cv2 = Cv(img)
    if not reduce and 44 <= f < 50:
        ui.glitch_tear(cv2, (0, 80, 1920, 960), 1.0 * (1 - prog(f, 44, 50)), seed=21 + f, bands=16)
    # skull
    if f >= 56:
        c = (960, 420)
        if reduce:
            ks = e('LINEAR', f, 56, 68)
            sc_ = 1.0
            off = (0, 0)
        else:
            ks = 1.0
            t_ = prog(f, 56, 62)
            sc_ = 1.0 + .6 * (1 - out_back(t_)) if t_ < 1 else 1.0
            off = (0, 0)
            if 62 <= f < 66:
                j = [(3, -2), (-2, 2), (1, -1), (0, 0)][f - 62]
                off = j
        cc = (c[0] + off[0], c[1] + off[1])
        pl = Lyr((cc[0] - 340, cc[1] - 340, cc[0] + 340, cc[1] + 340))
        g_skull(pl, cc, 150 * sc_)
        ring = Lyr((cc[0] - 340, cc[1] - 340, cc[0] + 340, cc[1] + 340))
        tr = 1.0 if reduce else prog(f, 60, 70)
        if tr > 0:
            ring.line(ring_pts_full(cc, 205 * sc_, 100, 360 * tr), 5, 255)
        cv2.add(PLUM, blur(pl.m, 40), 1.2 * ks, pl.off)
        cv2.over(INK, blur(pl.m, 14), .6 * ks, pl.off)
        cv2.neonL(pl, HOT, core=1.0 * ks, g1=(5, 1.0 * ks), g2=(26, .8 * ks), white=.6 * ks)
        cv2.neonL(ring, VEIN, core=.9 * ks, g1=(4, .8 * ks), g2=(14, .5 * ks))
    return cv2.out()


def ring_pts_full(c, r, n, deg):
    return [(c[0] + r * math.cos(math.radians(-90 + a)), c[1] + r * math.sin(math.radians(-90 + a))) for a in np.linspace(0, deg, n)]
