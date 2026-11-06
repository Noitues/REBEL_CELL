"""Beat renderers, part A: jack-in, jack-out, card draw, drag and drop."""
from stage import *

TOWER_A = .60


def _tower_state(f, i, first, reduce, out=False):
    """(height scale, alpha) of tower #i (0 = nearest HOME) at frame f for jack-in (out=False) or jack-out."""
    if not out:
        st = 3 + i * (2 if first else 1)
        dur = 8 if first else 6
        if reduce:
            return 1.0, TOWER_A * e('LINEAR', f, 0, 8)
        t = prog(f, st, st + dur)
        return (max(.02, out_back_soft(t)) if t > 0 else 0.0), TOWER_A * clamp(t * 3)
    n = 10
    st = (n - 1 - i) * .5
    if reduce:
        return 1.0, TOWER_A * (1 - e('LINEAR', f, 0, 6))
    t = prog(f, st, st + 4)
    return max(0.0, 1 - in_cubic(t)), (TOWER_A * (1 - clamp(t * 1.2)) if t < 1 else 0.0)


_hud = None


def _paste_full(cv, sp, off, k):
    comp(cv, sp, k, off)


def init():
    global _hud
    if _hud is None:
        _hud = hud_sprite()


init()


def _jackout_glitch(a, f):
    """CP2077-style exit fringe: about 6 frames of chromatic split and a scanline tear (not in reduce-motion)."""
    t = prog(f, 4, 10)
    if not (0 < t < 1):
        return a
    amt = (1 - t) ** .8
    sh = int(round(10 * amt))
    a = a.copy()
    a[..., 0] = np.roll(a[..., 0], sh, 1)
    a[..., 2] = np.roll(a[..., 2], -sh, 1)
    rng = np.random.RandomState(5 + f)
    for _ in range(3):
        y = int(rng.uniform(150, H - 150))
        h = int(rng.uniform(4, 10))
        a[y:y + h] = np.roll(a[y:y + h], int(rng.uniform(-60, 60) * amt), 1)
    y = int(300 + 400 * t)
    a[y:y + 3] = np.clip(a[y:y + 3] + np.array([.5, .2, .8], np.float32) * .6, 0, 1)
    return a


def b_jack(f, reduce=False, first=False, out=False):
    """jack-in (out=False) or jack-out (out=True). f counted from the trigger."""
    S = stage()
    w = S.w
    gf = 24 if first else 10
    front = None
    if not out:
        if reduce:
            m = np.full((H, W), e('IN_OUT_QUAD', f, 0, 8), np.float32)
        else:
            t = e('IN_OUT_CUBIC' if first else 'OUT_CUBIC', f, 0, gf)
            m = radial_mask(S.home, t * 2300, 220)
            front = None if (t >= 1 or t <= 0) else t * 2300
    else:
        if reduce:
            m = np.full((H, W), 1 - e('IN_OUT_QUAD', f, 0, 6), np.float32)
        else:
            t = 1 - e('IN_QUAD', f, 2, 8)
            m = radial_mask(S.home, t * 2300, 160)
            front = None if (t >= 1 or t <= 0) else t * 2300
    m3 = m[..., None]
    img = S.raw * (1 - m3) + S.base * m3
    cv = Cv(img)
    order = S.site_order
    if front is not None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - S.home[0]) ** 2 + ((yy - S.home[1]) / .72) ** 2)
        band = np.clip(1 - np.abs(d - front) / 26, 0, 1) ** 2
        cv.add(LATT, band, .55 if not out else .35)
        cv.add(WHITE, np.clip(1 - np.abs(d - front) / 7, 0, 1), .25)
    for i, sid in enumerate(order):
        s = w.sites[sid]
        hs, al = _tower_state(f, i, first, reduce, out)
        if hs <= .015 or al <= .01:
            continue
        idle = sid == 't1_d'
        SC.tower(cv, s['B'], s['tier'], 'healthy', seed=sum(map(ord, sid)) % 97, alpha=al * (.5 if idle else 1), hs=hs * (.45 if idle else 1))
        if not out and not reduce:
            t = prog(f, 2 + i * .5, 8 + i * .5)
            if 0 < t < 1:
                ui.shock(cv, s['B'], 22 + 40 * out_back(t), LATT, w=3, k=(1 - t) ** .6 * .9)
    if not out:
        hot = (2 <= f <= 8) and not reduce
        al = .58 * (e('LINEAR', f, 0, 8) if reduce else e('OUT_CUBIC', f, 2, 12))
        if al > .02:
            SC.solace_cage(cv, S.hq, alpha=al, hot=hot, phase=f / 30.0)
        t = prog(f, 2, 12)
        if 0 < t < 1 and not reduce:
            ui.shock(cv, S.cage_c, 40 + 260 * out_expo(t), HOT, w=4, k=(1 - t))
    else:
        al = .58 * (1 - e('LINEAR', f, 0, 5))
        if al > .02:
            SC.solace_cage(cv, S.hq, alpha=al)
    SC.home_deck(cv, S.home, hp=44)
    if not out and f < 2 and not reduce:
        ui.flash(cv, S.home + np.array([0, -20]), 170, WHITE, .9 if f == 0 else .55)
        ui.shock(cv, S.home, 80 + 60 * f, LATT, w=3, k=.9)
    HS = _hud
    if not out:
        tt = e('LINEAR' if reduce else 'OUT_CUBIC', f, 4, 10)
    else:
        tt = 1 - e('LINEAR' if reduce else 'IN_CUBIC', f, 0, 6 if reduce else 3)
    dy = 0 if reduce else -80 * (1 - tt)
    if tt > .01:
        _paste_full(cv, HS, (0, dy), tt)
    slots = hand_slots(5)
    for i, (verb, typ) in enumerate(HAND):
        if not out:
            t2 = e('LINEAR', f, 4, 10) if reduce else e('OUT_CUBIC', f, 4 + i * .8, 10 + i * .8)
        else:
            t2 = 1 - e('LINEAR' if reduce else 'IN_CUBIC', f, 0, 6 if reduce else 3)
        if t2 > .01:
            c = slots[i][0] + np.array([0, 150 * (1 - t2)]) * (0 if reduce else 1)
            put_card(cv, verb, typ, c, slots[i][1], k=t2)
    a = cv.out()
    fin = fast_finish(a, vig=.38, scan=.07, fringe=1.5)
    res = a * (1 - m3) + fin * m3
    if out and not reduce:
        res = _jackout_glitch(res, f)
    return res


# ------------------------------------------------------------------ card draw
DECK = np.array([1700.0, 960.0])


def b_draw(f, reduce=False):
    S = stage()
    cv = S.world('plan', programs={'t2_intel': ('SHIFT', 'E')})
    HS = _hud
    comp(cv, HS)
    s4 = hand_slots(4)
    s5 = hand_slots(5)
    rt = e('OUT_CUBIC', f, 2, 10) if not reduce else (1.0 if f >= 2 else 0.0)
    for i in range(4):
        c = s4[i][0] + (s5[i][0] - s4[i][0]) * rt
        ang = s4[i][1] + (s5[i][1] - s4[i][1]) * rt
        put_card(cv, HAND[i][0], HAND[i][1], c, ang)
    for j in range(3):
        put_card(cv, 'GUARD', 'D', DECK + np.array([-j * 2, -j * 3]), 4, sc=.74, back=True)
    tgt = s5[4][0]
    tang = s5[4][1]
    if f < 2:
        lift = 6 * e('OUT_QUAD', f, 0, 2)
        put_card(cv, HAND[4][0], HAND[4][1], DECK + np.array([-6, -9 - lift]), 4, sc=.74, back=True)
    elif reduce:
        put_card(cv, HAND[4][0], HAND[4][1], tgt, tang, k=e('LINEAR', f, 2, 8))
    else:
        u = e('OUT_CUBIC', f, 2, 12)
        p0 = DECK + np.array([-6, -9])
        p1 = np.array([1480.0, 760.0])
        c = (1 - u) ** 2 * p0 + 2 * u * (1 - u) * p1 + u * u * tgt
        sc = .74 + (.9 - .74) * u
        ang = lerp(4, tang, u)
        fl = prog(f, 6, 10)
        sx = abs(math.cos(math.pi * fl)) if 0 < fl < 1 else 1.0
        back = fl < .5 and f < 10
        if f >= 12:
            sc = .9 * (1 + .06 * (1 - e('OUT_CUBIC', f, 12, 16)))
            c = tgt + np.array([0, 3 * (1 - e('OUT_BACK', f, 12, 16))])
        put_card(cv, HAND[4][0], HAND[4][1], c, ang, sc=sc, scale_x=max(sx, .06), back=back)
        if 12 <= f < 18:
            t = prog(f, 12, 18)
            ui.shock(cv, tgt + np.array([0, 50]), 24 + 40 * out_expo(t), LATT, w=2.5, k=(1 - t) * .8)
    return fast_finish(cv.out())


# ------------------------------------------------------------------ drag and drop
def _nolock(cv, c, r=34, k=1.0, seed=2):
    """nudge-lock mark: a red grease-pencil circle-slash (the Site refuses this card)."""
    ly = Lyr((c[0] - r - 20, c[1] - r - 20, c[0] + r + 20, c[1] + r + 20))
    rng = np.random.RandomState(seed)
    pts = []
    for a in np.linspace(0, 2 * math.pi * 1.06, 34):
        rr = r * (1 + rng.uniform(-.04, .04))
        pts.append((c[0] + rr * math.cos(a + .5), c[1] + rr * math.sin(a + .5)))
    ly.line(pts, 6.5, 255)
    pts2 = []
    for a in np.linspace(0, 2 * math.pi * .9, 30):
        rr = r * (.96 + rng.uniform(-.04, .04))
        pts2.append((c[0] + rr * math.cos(a + .75), c[1] + rr * math.sin(a + .75)))
    ly.line(pts2, 4.2, 255)
    ui.scribble(ly, (c[0] - r * .7, c[1] - r * .7), (c[0] + r * .7, c[1] + r * .7), 6.5, seed + 3)
    cv.overL(ly, INK, .7 * k)
    cv.addL(ly, GREASE_R, 1.0 * k)
    cv.add(GREASE_R, blur(ly.m, 5), .4 * k, ly.off)


def b_drag(f, valid=True, reduce=False):
    S = stage()
    w = S.w
    cv = S.world('plan', programs={'t2_intel': ('SHIFT', 'E')})
    HS = _hud
    comp(cv, HS)
    sid = 't1_c' if valid else 't1_d'
    B = w.sites[sid]['B']
    drop = B + np.array([0, -24])
    slots = hand_slots(5)
    h0, a0 = slots[0]
    for i in range(1, 5):
        put_card(cv, HAND[i][0], HAND[i][1], slots[i][0], slots[i][1])
    lift_p = np.array([h0[0], h0[1] - 40])
    ang = 0.0
    sc = 1.12
    card_k = 1.0
    if f < 3:
        u = e('OUT_BACK', f, 0, 3)
        c = h0 + (lift_p - h0) * u
        sc = .9 + .22 * u
        ang = a0 * (1 - u)
    elif f < 14:
        u = e('IN_OUT_QUAD', f, 3, 10)
        mid = np.array([lift_p[0] + (drop[0] - lift_p[0]) * .5, min(lift_p[1], drop[1]) - 70])
        c = (1 - u) ** 2 * lift_p + 2 * u * (1 - u) * mid + u * u * drop
        vel = (drop - lift_p)[0] / 7.0
        ang = clamp(-vel * .12, -9, 9) * (1 - e('OUT_QUAD', f, 8, 12))
    else:
        c = drop.copy()
    hov = f >= 10
    if valid:
        if hov and f < 26:
            EB.lime_ring(cv, B + np.array([0, 4]), 50, k=min(1, (f - 10 + 1) / 2.0))
            ui.firewall(cv, B, 'D', mode='ghost', k=1.0)
        tp = e('OUT_CUBIC', f, 10, 16)
        if tp > 0:
            r = 24 if reduce else 24 * (.7 + .3 * out_back(prog(f, 10, 16)))
            hy.hex_tile(cv, (B[0] + 62, B[1] - 128), 'HOLDS', None, r=r, k=min(1, tp * 1.4))
        if f >= 14:
            tt = e('OUT_CUBIC', f, 14, 26)
            c = drop + (B + np.array([0, -30]) - drop) * tt
            sc = 1.12 * (1 - .62 * tt)
            card_k = 1 - clamp((f - 22) / 4.0)
        if f >= 24:
            t2 = e('OUT_CUBIC', f, 24, 32)
            ui.firewall(cv, B + np.array([0, 26 * (1 - t2)]), 'D', k=t2)
        if 24 <= f < 32 and not reduce:
            t = prog(f, 24, 30)
            ui.shock(cv, B + np.array([0, 4]), 30 + 50 * out_expo(t), TIER['HOLDS'], w=3.5, k=(1 - t))
    else:
        if hov and f < 38:
            _nolock(cv, B + np.array([0, -14]), k=min(1, (f - 10 + 1) / 2.0) * (1 - e('LINEAR', f, 30, 38)))
        if 14 <= f < 20 and not reduce:
            osc = math.sin((f - 14) * math.pi * 1.0) * 6 * (1 - prog(f, 14, 20))
            c = drop + np.array([osc, 0])
        if f >= 20:
            t = e('OUT_CUBIC', f, 20, 32)
            tgt = lift_p + (h0 - lift_p) * t
            c = drop + (tgt - drop) * t
            sc = 1.12 - .22 * t
            ang = a0 * t
    if card_k > .01:
        put_card(cv, HAND[0][0], HAND[0][1], c, ang, sc=sc, k=card_k, lime=(3 <= f < 14 and valid))
        if 3 <= f < 14:
            hbar_cur(cv, c + np.array([26, 44]), sc=1.1)
        if not valid and 10 <= f < 22:
            _nolock(cv, c + np.array([34, -48]), r=14, k=.95)
    return fast_finish(cv.out())
