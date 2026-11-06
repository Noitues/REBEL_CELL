"""Beats 2: HOME hit, lock reveal, Bloom creep, jack-in/out, shield close-up."""
from scenes import *
import scenes as S1
from m2 import _ease

# ================================================================== HOME HIT
N_HOME = 130


def b_home(f, reduce=False, mode='test', f_imp=36):
    R = route('K2')
    end = R.L - 4
    s_wait = end - 118
    s_hit = end - 46
    r = f - f_imp
    S = Scene()
    S.std_rings(0.6)
    S.tags = [t for t in S.tags]
    if not reduce:
        if r < -6:
            sh = s_wait
        elif r < 0:
            sh = lerp(s_wait, s_hit, e('OUT_QUAD', r, -6, 0))
        else:
            sh = s_hit
    else:
        sh = s_wait
    kr = 1.0 if r < 8 else 1.0 - .75 * e('LINEAR', r, 8, 16)
    S.beams.append(dict(rid='K1', s0=520, s1=route('K1').L - 4, gain=.65, flow=f * .05))
    S.beams.append(dict(rid='K3', s0=520, s1=route('K3').L - 4, gain=.65, flow=f * .05))
    if not reduce:
        gm = .9 * kr
        S.beams.append(dict(rid='K2', s0=520, s1=min(sh, end - 8), gain=gm, flow=f * .06,
                            gain_fn=lambda s, sw=sh, gm=gm, kr=kr: gm + 1.3 * kr * np.exp(-np.clip(sw - s, 0, None) / 220.0)))
        if r < 0:
            pass
    else:
        t = e('IN_OUT_QUAD', f, f_imp - 8, f_imp)
        S.beams.append(dict(rid='K2', s0=520, s1=end - 8, gain=(.9 + .5 * t) * (1 if r < 8 else 1 - .6 * e('LINEAR', r, 8, 24)), flow=0.0))
    S.dread = [(R, sh if not reduce else s_wait, 1.0 if r < 0 else 1.0 * (1 - e('LINEAR', r, 0, 10)))]
    S.plum_list = [((1650.0, 470.0), 200.0)]
    S.plum_k = .40
    # HOME state
    hit_t = prog(r if r < 8 else (8 if r < 16 else r - 8), 0, 20)
    if r < 0:
        S.home = dict(hp=44, preview=6)
    elif r < 22:
        S.home = dict(hp=44 - 6, hit=6, hit_t=(hit_t if not reduce else .55), preview=0, pool_k=1.0)
        S.home['hp'] = 38
    else:
        S.home = dict(hp=38, preview=0, crack=e('LINEAR', r, 22, 30))
    # heads
    heads = []
    if r < 0:
        if not reduce:
            heads.append(dict(rid='K2', s=sh, alpha=1.0))
        else:
            t = e('IN_OUT_QUAD', f, f_imp - 8, f_imp)
            heads.append(dict(rid='K2', s=s_wait, alpha=1 - t))
            heads.append(dict(rid='K2', s=s_hit, alpha=t))
    else:
        heads.append(dict(rid='K2', s=s_hit, alpha=1 - e('LINEAR', r, 4 if not reduce else 4, 12), halo=3.0 if r < 10 else 0.0))
    for rid, s in (('K1', 1030.0), ('K3', 760.0)):
        heads.append(dict(rid=rid, s=s, alpha=.45))
    S.heads = heads
    home_fx(S, r, reduce)
    home_tile(S, r, reduce)
    scorch(S, r)
    if r >= 0:
        dk = (1.0 if not reduce else e('LINEAR', r, 0, 6)) * (1 - e('IN_OUT_QUAD', r, 16, 28))
        S.dim = (home_c(), 460, (.5 if not reduce else .25) * dk)
    fr = S.render(f)
    hm = home_c()
    if reduce:
        cam = (1.10, (hm[0] + 330, hm[1] - 150), (0, 0))
    else:
        z = 1.0 + .10 * e('IN_OUT_QUAD', f, 0, 32) + .02 * e('OUT_QUAD', f, 40, 100)
        cam = (z, (lerp(960, hm[0] + 330, e('IN_OUT_QUAD', f, 0, 32)), lerp(540, hm[1] - 150, e('IN_OUT_QUAD', f, 0, 32))), (10 * e('IN_OUT_QUAD', f, 0, 36), 4 * e('IN_OUT_QUAD', f, 0, 36)))
    hp = 44 if r < 3 else 38
    hcol = PAL['DAMAGED'] if 3 <= r < 40 else None
    huds = std_huds(hp=hp, hp_col=hcol)
    shake = SHAKE[r] if (not reduce and 0 <= r < 4) else (0, 0)
    return assemble(fr, f, reduce, mode, cam, huds, shake=shake)


# ================================================================== LOCK REVEAL
N_LOCK = 120
STEP_LOCK = dict(rattle=(14, 17), shackle=(17, 21), diss=(18, 30), tcol=(18, 26), pop=(28, 34), clear=(30, 50))


def lock_geo2():
    hq = np.asarray(world().hq, float)
    base = np.array([hq[0] - 188, hq[1] - 70])
    return [base + np.array([i * 52, -i * 33]) for i in range(3)]


def fog_layer(fr, items, t, k=0.62):
    """lavender mist corridors along routes; items: (route, s0, s1, strength)."""
    acc = np.zeros((H // 4, W // 4), np.float32)
    n2 = fr.A['n2']
    for R, s0, s1, st in items:
        if st <= 0:
            continue
        for sv in np.arange(s0, min(s1, R.L - 2), 9.0):
            p = R.pos(sv) / 4.0
            sig = 7.5
            x0, x1 = int(max(p[0] - 3 * sig, 0)), int(min(p[0] + 3 * sig + 1, W // 4))
            y0, y1 = int(max(p[1] - 3 * sig, 0)), int(min(p[1] + 3 * sig + 1, H // 4))
            if x1 <= x0 or y1 <= y0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            g = np.exp(-((xx - p[0]) ** 2 + ((yy - p[1]) / .75) ** 2) / (2 * sig * sig)) * st
            acc[y0:y1, x0:x1] = np.maximum(acc[y0:y1, x0:x1], g)
    if acc.max() <= 0:
        return
    nz = n2[::2, ::2]
    nz = np.roll(nz, int(t * .6), axis=1)
    nz = nz[:H // 4, :W // 4]
    acc = acc * (0.7 + 0.5 * nz)
    a = np.asarray(Image.fromarray(np.clip(acc, 0, 1).astype(np.float32)).resize((W, H), Image.BILINEAR), np.float32) * k
    fr.img[:] = fr.img * (1 - a[..., None]) + (PAL['FOG'] * .9)[None, None] * a[..., None]
    fr.gl += np.asarray(Image.fromarray((a * .3).astype(np.float32)).resize((W // 4, H // 4), Image.BILINEAR))[..., None] * PAL['FOG']


def lock_draw(fr, c, letter, typ, r=32, shackle=0.0, diss=0.0, tcol=0.0, pop=0.0, jit=(0, 0), k=1.0, pulse=0.0):
    c = (c[0] + jit[0], c[1] + jit[1])
    col = PAL['FOG'] * (1 - tcol) + PAL[typ] * tcol
    P = Pl((c[0] - r - 20, c[1] - r - 60, c[0] + r + 20, c[1] + r + 20))
    hexp = lambda q: [(c[0] + q * math.cos(math.radians(60 * i + 30)), c[1] + q * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    P.poly(hexp(r + 3), PAL['INK'])
    P.poly(hexp(r), col)
    P.poly(hexp(r - 4), PAL['INK'], .96)
    u = shackle
    ax = c[0] + r * .4 * u
    ay = c[1] - r * (.72 + .06 * u)
    arc = [(ax + r * .5 * math.cos(a), ay - r * .5 * abs(math.sin(a)) * 1.0 + r * 0.0) for a in np.linspace(math.pi, 2 * math.pi, 14)]
    arc = [(ax + r * .5 * math.cos(a), ay + r * .5 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 14)]
    P.line([(c[0] - r * .5, c[1] - r * .3), (c[0] - r * .5, ay)] + arc, PAL['INK'], 7.0)
    P.line([(c[0] - r * .5, c[1] - r * .3), (c[0] - r * .5, ay)] + arc, col, 3.6)
    if u < .5:
        P.line([(ax + r * .5, ay), (c[0] + r * .5 + r * .4 * u, c[1] - r * .3 - r * .4 * u)], PAL['INK'], 7.0)
        P.line([(ax + r * .5, ay), (c[0] + r * .5 + r * .4 * u, c[1] - r * .3 - r * .4 * u)], col, 3.6)
    fr.pl(P, gk=.7 + .5 * pulse, k=k)
    if diss < 1.0:
        tmp = Image.new('L', (int(2 * r), int(2 * r)), 0)
        ImageDraw.Draw(tmp).text((r, r + 1), letter, font=HD.F(int(r * 1.15)), fill=255, anchor='mm')
        m = np.asarray(tmp, np.float32) / 255
        cell = 3
        rng = np.random.RandomState(7)
        thr = rng.rand(m.shape[0] // cell + 1, m.shape[1] // cell + 1).astype(np.float32)
        tm = np.kron(thr, np.ones((cell, cell), np.float32))[:m.shape[0], :m.shape[1]]
        keep = m * (tm > diss)
        x0, y0 = int(c[0] - r), int(c[1] - r)
        fr.add((PAL['WHITE'] * .85 + col * .15)[None, None], keep, x0, y0, gk=.5, k=k)
        if diss > 0:
            ys, xs = np.where((m > .5) & (tm <= diss))
            sel = rng.permutation(len(ys))[:70]
            Pf = Pl((c[0] - r - 60, c[1] - r - 60, c[0] + r + 60, c[1] + r + 60), ss=1)
            for ii in sel:
                y, x = ys[ii], xs[ii]
                tt = diss - tm[y, x]
                ang = rng.uniform(0, 2 * math.pi)
                dd = tt * 34 * rng.uniform(.5, 1.2)
                px = x0 + x + math.cos(ang) * dd
                py = y0 + y + math.sin(ang) * dd * .8 - tt * 14
                Pf.poly([(px, py), (px + 3, py), (px + 3, py + 3), (px, py + 3)], PAL[typ] * .6 + .4, clamp01(1 - tt / max(diss, 1e-3) * .6))
            fr.pl(Pf, gk=.8, k=k)
    if pop > 0:
        pr = r * .75 * pop
        head(fr, typ, (c[0], c[1] + 2), -90 + 0, alpha=min(1.0, pop), scale=max(.3, pr / 26.0), halo=2.0)


def b_lock(f, reduce=False, mode='test'):
    S = Scene()
    S.std_rings(0.6)
    S.tags = [t for t in S.tags if t['sid'] != 't1_b']
    RA, RB, RC = route('A'), route('B'), route('C')
    pos = lock_geo2()
    st = STEP_LOCK
    clear = e('OUT_CUBIC', f, *st['clear']) if not reduce else e('LINEAR', f, 28, 36)
    S.blocks = [b for b in S.blocks if b['rid'] != 'K3']
    S.beams.append(dict(rid='K1', s0=520, s1=route('K1').L - 4, gain=.70, flow=f * .05))
    S.beams.append(dict(rid='K2', s0=520, s1=route('K2').L - 4, gain=.65, flow=f * .05))
    end = RA.L - 6
    if clear > .005:
        if reduce:
            S.beams.append(dict(rid='A', s0=RA.ext, s1=end, gain=.9, alpha=clear))
        else:
            S.beams.append(dict(rid='A', s0=RA.ext, s1=RA.ext + (end - RA.ext) * clear, gain=1.0, flow=f * .1))
    S.plum_list = [((1650.0, 470.0), 190.0)]
    S.plum_k = .40
    hs = RA.ext + 330
    if clear > .05:
        S.heads.append(dict(rid='A', s=hs, alpha=min(1, clear * 1.4)))
        S.dread = [(RA, hs, min(1.0, clear))]
    fr = S.render(f)
    # fog: B and C always; A until the reveal
    items = [(RB, RB.ext + 10, RB.L - 6, 1.0), (RC, RC.ext + 10, RC.L - 6, 1.0), (RA, RA.ext + 10, RA.L - 6, 1 - clear)]
    fog_layer(fr, items, f, k=.62)
    # locks
    dimk = 1.0 - .5 * e('LINEAR', f, 17, 24)
    for i in (1, 2):
        lock_draw(fr, pos[i], 'ABC'[i], 'E', k=dimk)
    jit = (0, 0)
    pulse = 0.0
    if reduce:
        pulse = .6 * math.sin(math.pi * clamp01(prog(f, 14, 20)))
        sh = 1.0 if f >= 17 else 0.0
        dis = e('LINEAR', f, 20, 28)
        tcol = dis
        pop = e('LINEAR', f, 22, 30)
        lock_draw(fr, pos[0], 'A', 'E', shackle=sh, diss=0.0 if dis < .5 else 1.0, tcol=tcol, pop=pop if dis >= .5 else 0, pulse=pulse)
    else:
        if st['rattle'][0] <= f < st['rattle'][1]:
            rng = np.random.RandomState(f)
            jit = (rng.choice([-2, 2]), rng.choice([-1, 1]))
        shk = e('OUT_BACK', f, *st['shackle'])
        dis = e('LINEAR', f, *st['diss'])
        tcol = e('LINEAR', f, *st['tcol'])
        pop = _ease('OUT_BACK', prog(f, *st['pop'])) if f >= st['pop'][0] else 0.0
        if st['pop'][0] <= f < st['pop'][1]:
            rng = np.random.RandomState(100 + f)
            jit = (rng.uniform(-2, 2), rng.uniform(-2, 2))
        lock_draw(fr, pos[0], 'A', 'E', shackle=shk, diss=dis, tcol=tcol, pop=pop, jit=jit)
        if st['pop'][0] <= f < st['pop'][1]:
            t = prog(f, *st['pop'])
            hex_ripple(fr, pos[0] + np.array([0, 24]), 30 + 60 * e('OUT_EXPO', t, 0, 1), PAL['E'], .8 * (1 - t), w=2.5)
    if reduce:
        cam = (1.2, (1250, 560), (0, 0))
    else:
        z = lerp(1.0, 1.55, e('IN_OUT_QUAD', f, 0, 24))
        z = lerp(z, 1.14, e('OUT_CUBIC', f, 32, 78))
        cx = lerp(lerp(960, pos[0][0], e('IN_OUT_QUAD', f, 0, 24)), 1050, e('OUT_CUBIC', f, 32, 78))
        cy = lerp(lerp(540, pos[0][1], e('IN_OUT_QUAD', f, 0, 24)), 560, e('OUT_CUBIC', f, 32, 78))
        cam = (z, (cx, cy), (12 * e('IN_OUT_QUAD', f, 0, 60), 4 * e('IN_OUT_QUAD', f, 0, 60)))
    return assemble(fr, f, reduce, mode, cam, std_huds())


# ================================================================== BLOOM CREEP
N_BLOOM = 130
STEP_R = [40, 70, 95, 118, 138, 156, 172, 186, 198, 208]
F0_BLOOM = 26


def bloom_radius(f):
    R = 0.0
    for j in range(len(STEP_R)):
        a = F0_BLOOM + 5 * j
        t = e('OUT_QUAD', f, a, a + 3)
        if t <= 0:
            break
        prev = STEP_R[j - 1] if j > 0 else 0.0
        R = prev + (STEP_R[j] - prev) * t
    return R


def bloom_pulse(f):
    p = 0.0
    for j in range(len(STEP_R)):
        a = F0_BLOOM + 5 * j
        if a <= f < a + 4:
            p = max(p, 1 - (f - a) / 4.0)
    return p


def _bloom_scene(f, state, reduce):
    """state: 'before' | 'after' | 'live' (normal)."""
    S = Scene()
    S.std_rings(0.6)
    S.tags = []
    S.blocks = []
    S.rest_beams(.65, flow_t=f)
    S.plum_list = [((1650.0, 470.0), 190.0 + .5 * f)]
    S.plum_k = .40
    if state == 'before':
        R, pulse = 0.0, 0.0
        taken = 0.0
    elif state == 'after':
        R, pulse = STEP_R[-1], 0.0
        taken = 1.0
    else:
        R = bloom_radius(f)
        pulse = bloom_pulse(f)
        taken = e('IN_QUAD', f, 20, 26)
    drain = 1 - .85 * min(f / 20.0, 1.0) if state == 'live' else (1.0 if state == 'before' else .15)
    S.rings = [r for r in S.rings if r['sid'] not in ('t1_a', 't1_b')]
    if taken < .5:
        S.rings += [dict(sid='t1_a', tier='UNTOUCHED', frac=drain), dict(sid='t1_b', tier='UNTOUCHED', frac=drain)]
    else:
        S.rings += [dict(sid='t1_a', tier='SITES_LOST', k=e('OUT_CUBIC', f, 22, 28) if state == 'live' else 1.0),
                    dict(sid='t1_b', tier='SITES_LOST', k=e('OUT_CUBIC', f, 22, 28) if state == 'live' else 1.0)]
        S.tags = [dict(sid='t1_a', tier='SITES_LOST', k=e('OUT_BACK', f, 26, 32) if state == 'live' else 1.0, pips=0),
                  dict(sid='t1_b', tier='SITES_LOST', k=e('OUT_BACK', f, 28, 34) if state == 'live' else 1.0, pips=0)]
    for sid in ('t1_a', 't1_b'):
        S.towers[sid]['hs'] = 1 - .72 * taken
        S.towers[sid]['tint'] = PAL['PLUM_MID'] * taken + PAL['SLATE'] * .62 * (1 - taken)
    return S, R, pulse


def b_bloom(f, reduce=False, mode='test'):
    Ba, Bb = site('t1_a')[0], site('t1_b')[0]
    cen = [Ba + np.array([0, -10]), Bb + np.array([0, -10])]
    def build(state):
        S, R, pulse = _bloom_scene(f, state, reduce)
        fr = S.render(f)
        seed_r = 40 * (e('OUT_BACK', f, 20, 26) if state == 'live' else 0)
        if state == 'after':
            Rr = STEP_R[-1]
        else:
            Rr = max(seed_r, R)
        fr.plum([(cen[0], Rr), (cen[1], Rr)], k=1.0, t=f, step_pulse=pulse, dim_lights=.8)
        return fr
    if reduce:
        if f < 20:
            fr = build('before')
            img = None
        else:
            t = e('IN_OUT_QUAD', f, 20, 28)
            if t <= 0.001:
                fr = build('before'); img = None
            elif t >= .999:
                fr = build('after'); img = None
            else:
                fa, fb = build('before'), build('after')
                img = fa.resolve() * (1 - t) + fb.resolve() * t
        cam = (1.12, (620, 520), (0, 0))
        src = img if img is not None else fr
    else:
        src = build('live')
        z = 1.0 + .12 * e('IN_OUT_QUAD', f, 0, 80)
        cam = (z, (lerp(960, 640, e('IN_OUT_QUAD', f, 0, 60)), lerp(540, 540, 1.0)), (10 * e('IN_OUT_QUAD', f, 0, 80), 3))
    return assemble(src, f, reduce, mode, cam, std_huds(infected=0 if f < 26 else (2 if f < 40 else 5)))


# ================================================================== JACK-IN / OUT
N_JACK = 96
T_IN, T_OUT = 10, 62


def plain_city():
    A = assets()
    if 'plain' not in A:
        c = A['city']
        lum = (c * LUM).sum(-1, keepdims=True)
        p = lum + (c - lum) * .22
        p = np.minimum(p, .72) * .78 + np.array([.10, .115, .14], np.float32)
        A['plain'] = p.astype(np.float32)
    return A['plain']


def b_jack(f, reduce=False, mode='test'):
    A = assets()
    home = home_c()
    gi, go = f - T_IN, f - T_OUT
    outp = f >= T_OUT
    d = None
    if not reduce:
        if not outp:
            t = e('OUT_CUBIC', gi, 0, 10)
        else:
            t = 1 - e('IN_QUAD', go, 2, 8)
        R = t * 2300
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - home[0]) ** 2 + ((yy - home[1]) / .72) ** 2)
        m = np.clip((R - d) / 220.0 + .5, 0, 1)
        front = R if 0 < t < 1 else None
    else:
        m = np.full((H, W), e('IN_OUT_QUAD', gi, 0, 8) if not outp else 1 - e('IN_OUT_QUAD', go, 0, 6), np.float32)
        front = None
    city = plain_city() * (1 - m[..., None]) + A['city'] * m[..., None]
    S = Scene(city=city)
    S.dark_amt = 0.0
    on = (gi >= 0) and not (outp and go > 6)
    order = sorted(world().sites, key=lambda s: float(np.hypot(*(site(s)[0] - home))))
    # towers
    for i, sid in enumerate(order):
        if reduce:
            k = e('LINEAR', gi, 0, 8) if not outp else 1 - e('LINEAR', go, 0, 6)
            hs = 1.0
        else:
            hs = e('OUT_BACK_SOFT', gi, 3 + i, 9 + i) if not outp else 1 - e('IN_QUAD', go, 0, 4)
            k = 1.0
        S.towers[sid]['hs'] = hs
        S.towers[sid]['k'] = k
    pk = (e('OUT_CUBIC', gi, 2, 8) if not reduce else e('LINEAR', gi, 0, 8)) if not outp else 1 - e('LINEAR', go, 0, 3)
    S.std_rings(0.6)
    for r in S.rings:
        r['k'] = pk
        if not reduce:
            r['rscale'] = .6 + .4 * e('OUT_BACK', gi, 2, 8) if not outp else 1.0
    for b in S.blocks:
        b['k'] = pk
    S.tags = [dict(t, k=pk, lift=52 * (1 if reduce else .6 + .4 * pk)) for t in S.tags]
    S.home = dict(hp=44, preview=0, ring_k=pk, pool_k=pk)
    S.cage = pk * (1 if reduce else .2 + .8 * e('OUT_CUBIC', gi, 2, 12))
    ak = (e('OUT_CUBIC', gi, 4, 14) if not outp else 1 - e('LINEAR', go, 0, 3))
    for rid, g_ in (('K1', .9), ('K2', .8), ('K3', .8)):
        R = route(rid)
        S.beams.append(dict(rid=rid, s0=R.ext, s1=R.L - 4, gain=g_, alpha=ak, flow=f * .1))
    S.plum_list = [((1650.0, 470.0), 190.0)] if pk > .3 else []
    S.plum_k = .4 * pk
    if pk <= .02:
        S.rings, S.blocks, S.tags, S.beams = [], [], [], []
        S.home = dict(hp=44, preview=0, ring_k=0.0, pool_k=0.0)
    fr = S.render(f)
    if front is not None:
        band = np.clip(1 - np.abs(d - front) / 26, 0, 1) ** 2
        fr.img += PAL['LATT'][None, None] * (band * (.55 if not outp else .35))[..., None]
        fr.img += (np.clip(1 - np.abs(d - front) / 7, 0, 1) * .25)[..., None]
    if not reduce and 0 <= gi < 2:
        flash(fr, home + np.array([0, -20]), 170, PAL['WHITE'], .9 if gi == 0 else .55)
        hex_ripple(fr, home, 80 + 60 * gi, PAL['LATT'], .9, w=3.0)
    if reduce and 0 <= gi < 3:
        flash(fr, home + np.array([0, -20]), 170, PAL['WHITE'], .30)
    # camera: dolly + parallax on jack-in, pull on jack-out
    if reduce:
        cam = (1.0, (960, 540), (0, 0))
    else:
        pin = e('OUT_CUBIC', gi, 0, 26)
        pout = e('IN_QUAD', go, 0, 10)
        z = lerp(1.14, 1.0, pin) if not outp else lerp(1.0, 1.06, pout)
        cx = lerp(560, 960, pin) if not outp else lerp(960, 760, pout)
        cy = lerp(660, 540, pin) if not outp else lerp(540, 600, pout)
        par = (lerp(26, 0, pin) if not outp else lerp(0, -10, pout), lerp(8, 0, pin))
        cam = (z, (cx, cy), par)
    tt = (e('LINEAR', gi, 4, 10) if reduce else e('OUT_CUBIC', gi, 4, 10)) if not outp else 1 - (e('LINEAR', go, 0, 6) if reduce else e('IN_CUBIC', go, 0, 3))
    dy = 0 if reduce else -80 * (1 - tt)
    slots = HD.slots_default()
    cards = []
    for i, s in enumerate(slots):
        if not outp:
            t2 = e('LINEAR', gi, 4, 10) if reduce else e('OUT_CUBIC', gi, 4 + i * .8, 10 + i * .8)
        else:
            t2 = tt
        s = dict(s, k=t2, y=s['y'] + (0 if reduce else 150 * (1 - t2)))
        cards.append(s)
    huds = []
    if tt > .01:
        huds.append(HD.hud_chips(k=tt, dy=dy))
        a = HD.hand([c for c in cards if c['k'] > .01])
        huds.append(a)
    return assemble(fr, f, reduce, mode, cam, huds)


# ================================================================== SHIELD FLASH WITH BITS (close-up)
N_SHIELD = 90
F_SH = 14


def b_shield(f, reduce=False, mode='test'):
    g = geo()
    R = route('K1')
    s_stop = g['stop']['K1']
    s_arr = s_stop - 40
    r = f - F_SH
    S = Scene()
    S.std_rings(0.6)
    S.tags = [t for t in S.tags if t['sid'] == 't1_c']
    S.tags[0]['pips'] = 3 if r < 8 else 2
    S.blocks = [dict(rid='K1', s=s_stop, tier='HOLDS', t=f)]
    S.rings = [x for x in S.rings if x['sid'] == 't1_c']
    S.rings[0]['pulse'] = .5 * math.exp(-max(r, 0) / 6.0) if r >= 0 else 0.0
    if not reduce:
        sh = lerp(s_arr - 90, s_arr, e('OUT_QUAD', f, 0, F_SH)) if r < 0 else s_arr
    else:
        sh = s_arr - 90 if f < F_SH - 8 else s_arr
    gm = .90
    S.beams.append(dict(rid='K1', s0=R.ext, s1=s_stop + 20, gain=gm, flow=f * .1,
                        gain_fn=lambda s, sw=sh, gm=gm: gm + 1.35 * np.exp(-np.clip(sw - s, 0, None) / 200.0) * (s <= sw + 6)))
    S.dread = [(R, sh, 1.0 if r < 0 else 1.0 * (1 - e('LINEAR', r, 0, 10)))]
    heads = []
    if r < 0:
        if not reduce:
            heads.append(dict(rid='K1', s=sh))
        else:
            t = e('IN_OUT_QUAD', f, F_SH - 8, F_SH)
            heads.append(dict(rid='K1', s=s_arr - 90, alpha=1 - t))
            heads.append(dict(rid='K1', s=s_arr, alpha=t))
    else:
        heads.append(dict(rid='K1', s=s_arr, alpha=1 - e('LINEAR', r, 4, 12), halo=3.0 if r < 12 else 0.0))
    S.heads = heads
    shield_fx(S, r, reduce, scale=1.0)
    fr = S.render(f)
    pb = R.pos(s_stop)
    if reduce:
        cam = (1.9, (pb[0] - 20, pb[1] - 30), (0, 0))
    else:
        z = 1.7 + .25 * e('OUT_CUBIC', f, 0, F_SH) + .05 * e('OUT_QUAD', f, F_SH, 70)
        cam = (z, (pb[0] - 20, pb[1] - 30), (6 * e('IN_OUT_QUAD', f, 0, 60), 2))
    return assemble(fr, f, reduce, mode, cam, std_huds(cards=False))


TESTS = {
    'daemon': (S1.b_daemon, S1.N_DAEMON),
    'lock': (b_lock, N_LOCK),
    'home': (b_home, N_HOME),
    'bloom': (b_bloom, N_BLOOM),
    'jack': (b_jack, N_JACK),
    'shield': (b_shield, N_SHIELD),
}
