"""Beat renderers, part B: daemon travel + shield flash, lock reveal, hunter lock, HOME hit."""
from stage import *
from scipy.ndimage import gaussian_filter1d
import beats_a as A

S0 = None
FOG = ui.FOG


def cworld(key, pre=None, states=None, programs=None, home_kw=None, idle=('t1_d',), cage_kw=None, skip_marks=False):
    S = stage()

    def build():
        cv = S.cv()
        if pre:
            pre(cv)
        draw_world(cv, S.w, states or {}, programs or {}, home_kw=home_kw or dict(hp=44), idle=idle, cage_kw=cage_kw, skip_marks=skip_marks)
        return cv.img.copy()
    return Cv(S.cached(('cw', key), build))


# ================================================================== DAEMON TRAVEL + SHIELD FLASH
class Daemon:
    """geometry + speed table for K1 (D beam) from its parked head to the guard at t1_c."""
    S_START = 1030.0

    def __init__(self):
        S = stage()
        w = S.w
        self.P = S.route('K1')
        self.tcB = w.sites['t1_c']['B']
        self.wallc = np.array([self.tcB[0] + 34, self.tcB[1] + 12 - 24])
        self.s_stop = nearest_s(w.routes['K1']['path'], self.wallc)
        self.hp = self.wallc
        L = int(self.P.L)
        pts = self.P.sub(0, L, 1.0)
        d = np.diff(pts, axis=0)
        hd = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
        turn = np.abs(hd[12:] - hd[:-12])
        turn = np.concatenate([np.zeros(6), turn, np.zeros(len(hd) + 1 - len(turn) - 6)])[:len(pts)]
        slow = 1 - .40 * np.clip(turn / .9, 0, 1)
        self.slow = gaussian_filter1d(slow, 10)
        self.t_launch = 34
        self.v0 = 14.0   # cruise px/f (daemon_cruise_px_f): 14 f per mean 200 px street block with the corner slow-down
        self._sim(self.v0)
        self.table = self._sim(self.v0)

    def _sim(self, v0):
        s = self.S_START - 10
        out = {}
        f = self.t_launch
        s = self.S_START
        while f < 400:
            ramp = min(1.0, (f - self.t_launch + 1) / 5.0) ** 1.5
            v = v0 * self.slow[int(min(s, len(self.slow) - 1))] * ramp
            rem = self.s_stop - 40 - s
            v = min(v, max(1.4, .30 * rem))
            s += v
            out[f] = s
            if self.s_stop - 40 - s < 1.0:
                break
            f += 1
        self.f_arr = f
        return out

    def _fit(self, target):
        lo, hi = 4.0, 40.0
        for _ in range(30):
            mid = (lo + hi) / 2
            self._sim(mid)
            if self.f_arr > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def s_at(self, f):
        if f < self.t_launch - 4:
            return self.S_START
        if f < self.t_launch:
            return self.S_START - 10 * e('IN_QUAD', f, self.t_launch - 4, self.t_launch)
        return self.table.get(f, self.s_stop - 40)


_D = None


def dmn():
    global _D
    if _D is None:
        _D = Daemon()
    return _D


def _pre_daemon(cv):
    S = stage()
    D = dmn()
    w = S.w
    P2 = S.route('K2')
    hy.ribbon(cv, P2, 'N', w.routes['K2']['ext'], P2.L - 4, k=.28, glow=.3)
    hy.dead_trail(cv, D.P, D.s_stop + 40, D.P.L - 4, k=.6)


def _daemon_world():
    return cworld('daemon', pre=_pre_daemon, programs={'t2_intel': ('SHIFT', 'E')}, states={'t1_a': 'DOWN'})


def impact_layers(cv, r, reduce, D, k_world=1.0):
    """the shield flash: r = frames since contact (negative before). Draws wall, flash, ripple, bits, stop block, tile."""
    S = stage()
    hp = D.hp
    tcB = D.tcB
    P = D.P
    sstop = D.s_stop
    # world dim under the flash
    if r >= 0:
        if reduce:
            ui.focus_dim(cv, hp, 430, .30 * e('LINEAR', r, 0, 6) * (1 - e('LINEAR', r, 14, 24)))
        else:
            ui.focus_dim(cv, hp, 430, .5 * e('OUT_QUAD', r, 0, 3) * (1 - e('LINEAR', r, 16, 28) * .6))
    # target ring + stop block: telegraphed ghost, then solid on contact
    pop = clamp(.30 + .70 * e('OUT_BACK_SOFT', r, 0, 6)) if r >= 0 else .30
    hy.target_ring(cv, tcB, 'HOLDS', k=.55 * (1 if r < 0 else 1) + (.45 * e('OUT_CUBIC', r, 0, 6) if r >= 0 else 0), fill=r >= 0)
    # wall
    if r < 0:
        ui.firewall(cv, tcB, 'D')
    else:
        t_sh = .45 * e('OUT_CUBIC', r, 0, 6)
        kw = 1.0 - .35 * e('IN_QUAD', r, 12, 24)
        ui.firewall(cv, tcB, 'D', mode='shatter', impact=tuple(hp), t=t_sh, k=kw)
    hy.stop_block(cv, P, sstop - 2, 'HOLDS', k=pop)
    if r >= 0:
        c_hold = TIER['HOLDS'] * .3 + WHITE * .7
        if reduce:
            kk = min(.55, .55 * e('LINEAR', r, 0, 3)) * (1 - e('LINEAR', r, 12, 24))
            hy.hex_flash(cv, hp + np.array([0, -6]), 58, TIER['HOLDS'] * .4 + LATT * .6, k=kk)
            if r < 3:
                ui.flash(cv, hp + np.array([0, -2]), 80, c_hold, .30)
        else:
            if r <= 3:
                ui.flash(cv, hp + np.array([0, -2]), 95, c_hold, [1.0, .9, .5, .25][r])
            rr = 58 * e('OUT_EXPO', r, 1, 8)
            kk = .95 * (1 - e('IN_QUAD', r, 12, 24)) + .12 * (1 - e('IN_QUAD', r, 12, 24))
            if rr > 4:
                hy.hex_flash(cv, hp + np.array([0, -6]), rr, TIER['HOLDS'] * .4 + LATT * .6, k=kk)
            t = prog(r, 1, 12)
            if 0 < t < 1:
                ui.shock(cv, hp + np.array([0, 20]), 54 * out_expo(t), TIER['HOLDS'], w=3.0, k=.85 * (1 - t))
            tb = prog(r, 2, 22)
            if 0 < tb < 1:
                ui.bits(cv, hp + np.array([4, 0]), TYPE_COL['D'] * .6 + WHITE * .4, n=60, r=150, seed=4,
                        spread=out_quad(prog(r, 2, 20)), k=1 - in_quad(prog(r, 10, 22)))
    # tile: ghost while telegraphed, solid on r>=16
    tp = e('OUT_BACK', r, 16, 22) if r >= 0 else 0
    if r < 16:
        hy.hex_tile(cv, (tcB[0] + 62, tcB[1] - 128), 'HOLDS', None, r=24, k=.42)
    else:
        rr_ = 24 * (1 if reduce else (.72 + .28 * e('OUT_BACK', r, 16, 22)))
        hy.hex_tile(cv, (tcB[0] + 62, tcB[1] - 128), 'HOLDS', None, r=rr_, k=.42 + .58 * e('OUT_CUBIC', r, 16, 19))


def _ribbons(cv, D, s_head, lit_len=330.0, reduce=False, f=0):
    P = D.P
    ext = 520.0
    stop = D.s_stop
    # resting body: dim ghost route all the way, brighter where the daemon has been
    hy.ribbon(cv, P, 'D', ext, stop + 20, k=.40, glow=.35)
    if s_head > ext + 8:
        # lit wake: four slices, brightest at the head, decaying to the resting level over lit_len px (about 20 f)
        n = 4
        for j in range(n):
            a = s_head - lit_len * (j + 1) / n
            b = s_head - lit_len * j / n
            a = max(ext, a)
            if b - a > 4:
                hy.ribbon(cv, P, 'D', a, b, k=(1.05 - .22 * j) * (1.0), glow=1.0 - .15 * j, chev=True)
        old = s_head - lit_len
        if old > ext + 8:
            hy.ribbon(cv, P, 'D', ext, old, k=.55, glow=.6)


def b_daemon(f, reduce=False):
    """test A frame f. Normal: hold 30, anticipation 4, travel, impact at D.f_arr. Reduce: hold 30, 8 f cross-fade, impact at 42."""
    S = stage()
    D = dmn()
    cv = _daemon_world()
    P = D.P
    stop = D.s_stop
    if not reduce:
        f_imp = D.f_arr
        r = f - f_imp
        s_head = D.s_at(f) if f < f_imp else stop - 40
        pre_hold = f < D.t_launch - 4
        _ribbons(cv, D, s_head if f >= D.t_launch - 4 else 0, reduce=False, f=f)
        # telegraph pulse on the ghost stop block (slow, not a flicker)
        if r < 0:
            hy.head(cv, P, s_head, 'D', sc=1.8)
        else:
            hy.head(cv, P, stop - 40, 'D', sc=1.8, k=1 - e('LINEAR', r, 0, 5))
        # tower ripple when the head passes t2_virus
        pv = nearest_s(S.w.routes['K1']['path'], S.w.sites['t2_virus']['B'])
        fa = [ff for ff, ss in D.table.items() if ss >= pv]
        if fa:
            t = prog(f, fa[0], fa[0] + 7)
            if 0 < t < 1:
                ui.shock(cv, S.w.sites['t2_virus']['B'], 20 + 40 * out_cubic(t), LATT, w=3, k=.8 * (1 - t))
    else:
        f_imp = 42
        r = f - f_imp
        # state cut: ghost route -> lit route cross-fade 30..38, head moves by cross-fade
        t = e('IN_OUT_QUAD', f, 30, 38)
        hy.ribbon(cv, P, 'D', 520.0, stop + 20, k=.40 + .60 * t, glow=.35 + .65 * t)
        hy.head(cv, P, D.S_START, 'D', sc=1.8, k=1 - t if r < 0 else 0)
        if r < 0:
            hy.head(cv, P, stop - 40, 'D', sc=1.8, k=t)
        else:
            hy.head(cv, P, stop - 40, 'D', sc=1.8, k=1 - e('LINEAR', r, 0, 8))
    impact_layers(cv, r, reduce, D)
    return cv.out()


def b_shield(f, reduce=False):
    """board frame: f = frames since contact (board 07). The head is parked at the wall, ribbon lit behind it."""
    D = dmn()
    cv = _daemon_world()
    P = D.P
    _ribbons(cv, D, D.s_stop - 40, lit_len=60)
    if f < 0:
        hy.head(cv, P, D.s_stop - 40, 'D', sc=1.8)
    else:
        hy.head(cv, P, D.s_stop - 40, 'D', sc=1.8, k=1 - e('LINEAR', f, 0, 5))
    impact_layers(cv, f, reduce, D)
    return cv.out()


# ================================================================== LOCK REVEAL
_L = {}


def lock_geo():
    S = stage()
    w = S.w
    base = np.array([w.hq[0] - 188, w.hq[1] - 70])
    return [base + np.array([i * 52, -i * 33]) for i in range(3)]


def _fog(cv, w, which):
    for i, r in enumerate('ABC'):
        if r not in which:
            continue
        p = w.routes[r]['path']
        ui.fog_band(cv, p, w.routes[r]['ext'] + 10, plen(p) - 6, width=11, seed=3 + i, k=.9)


def _lock_world(with_a):
    S = stage()
    w = S.w

    def pre(cv):
        _fog(cv, w, 'ABC' if with_a else 'BC')
    return cworld('lock_%s' % with_a, pre=pre, programs={'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, states={'t1_a': 'DOWN'})


def lock_anim(cv, c, letter='A', typ='E', r=21, shackle=0.0, diss=0.0, tcol=0.0, pop=0.0, jit=(0, 0), k=1.0, pulse=0.0):
    """letter lock that opens into its type silhouette. shackle 0..1 open, diss 0..1 letter dissolve, tcol 0..1 hue FOG->type,
    pop 0..1+ silhouette scale."""
    c = np.array(c, float) + np.array(jit, float)
    col = FOG * (1 - tcol) + TYPE_COL[typ] * tcol
    bx = (c[0] - r - 30, c[1] - r - 46, c[0] + r + 30, c[1] + r + 30)
    f_, e_, sh, tx = Lyr(bx), Lyr(bx), Lyr(bx), Lyr(bx)
    hexp = [(c[0] + r * math.cos(math.radians(60 * i + 30)), c[1] + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    f_.poly(hexp)
    e_.line(hexp + [hexp[0]], 2.8, 255)
    u = shackle
    ax = c[0] + r * .4 * u
    ay = c[1] - r * (.75 + .06 * u)
    sh.arc((ax, ay), r * .52, 180, 360, 3.2)
    sh.line([(c[0] - r * .52 + r * .40 * u * .0, ay), (c[0] - r * .52 + r * .40 * u * .0, c[1] - r * .3)], 3.2)
    if u < .5:
        sh.line([(c[0] + r * .52 + r * .4 * u, ay), (c[0] + r * .52 + r * .4 * u, c[1] - r * .3 - r * .4 * u)], 3.2)
    cv.overL(f_, INK, .92 * k)
    cv.neonL(e_, col, core=1.0 * k, g1=(3, (.7 + .4 * pulse) * k), g2=(10, .4 * k))
    cv.neonL(sh, col, core=1.0 * k, g1=(2, .5 * k), g2=None)
    # letter -> pixel blocks
    if diss < 1.0:
        tx.text((c[0], c[1] + 1), letter, r * 1.15, 255)
        m = tx.m
        cell = 3
        rng = np.random.RandomState(7)
        nyy, nxx = m.shape[0] // cell + 1, m.shape[1] // cell + 1
        thr = rng.rand(nyy, nxx).astype(np.float32)
        tm = np.kron(thr, np.ones((cell, cell), np.float32))[:m.shape[0], :m.shape[1]]
        keep = m * (tm > diss)
        cv.add(WHITE * .85 + col * .15, keep, 1.0 * k, tx.off)
        cv.add(col, blur(keep, 2), .5 * k, tx.off)
        if diss > 0:
            fly = Lyr(bx, ss=1)
            ys, xs = np.where((m > .5) & (tm <= diss))
            sel = rng.permutation(len(ys))[:70]
            for ii in sel:
                y, x = ys[ii], xs[ii]
                tt = diss - tm[y, x]
                ang = rng.uniform(0, 2 * math.pi)
                dd = tt * 34 * rng.uniform(.5, 1.2)
                px = tx.off[0] + x + math.cos(ang) * dd
                py = tx.off[1] + y + math.sin(ang) * dd * .8 - tt * 14
                fly.poly([(px, py), (px + 3, py), (px + 3, py + 3), (px, py + 3)], int(255 * (1 - tt / max(diss, 1e-3) * .6)))
            cv.add(TYPE_COL[typ] * .6 + WHITE * .4, fly.m, .9 * k, fly.off)
    if pop > 0:
        sc = r * .58 * pop
        g = Lyr(bx)
        g_type(g, typ, c + np.array([0, 0]), sc)
        cv.neonL(g, col, core=1.0 * k, g1=(2, .6 * k), g2=None, white=.4)


def b_lock(f, reduce=False):
    """test B frame f. normal: hold 0-14, rattle 14-17, shackle 17-21, dissolve 18-30, pop 28-34, corridor 30-50, hold to 96."""
    S = stage()
    w = S.w
    RA = w.routes['A']
    PA = PX(RA['path'])
    pos = lock_geo()
    clear = e('OUT_CUBIC', f, 30, 50)
    if reduce:
        clear = e('LINEAR', f, 28, 36)
    cvA = _lock_world(True)
    if clear > .001:
        cvB = _lock_world(False)
        cv = Cv(cvA.img * (1 - clear) + cvB.img * clear)
    else:
        cv = cvA
    # ribbon draws out from the HQ along the street as the fog clears
    end = plen(RA['path']) - 6
    if reduce:
        if clear > .01:
            hy.ribbon(cv, PA, 'E', RA['ext'], end, k=clear)
    else:
        L = RA['ext'] + (end - RA['ext']) * clear
        if clear > .005:
            hy.ribbon(cv, PA, 'E', RA['ext'], L, k=1.1)
    if clear > .05:
        hy.head(cv, PA, RA['ext'] + 330, 'E', sc=1.9, k=min(1, clear * 1.3))
    # B, C locks (dim once A opens)
    dimk = 1.0 - .5 * e('LINEAR', f, 17, 24)
    for i in (1, 2):
        ui.lock(cv, pos[i], 'ABC'[i], 'locked', k=dimk)
    # A lock
    jit = (0, 0)
    pulse = 0.0
    if reduce:
        pulse = .6 * math.sin(math.pi * clamp(prog(f, 14, 20)))
        sh = 1.0 if f >= 17 else 0.0
        diss = e('LINEAR', f, 20, 28)
        tcol = e('LINEAR', f, 20, 28)
        pop = e('LINEAR', f, 22, 30)
        # letter cross-fades into the silhouette: keep both, fade by diss
        lock_anim(cv, pos[0], 'A', 'E', shackle=sh, diss=0.0 if diss < .5 else 1.0, tcol=tcol, pop=pop * (1 if diss >= .5 else 0), pulse=pulse)
    else:
        if 14 <= f < 17:
            rng = np.random.RandomState(f)
            jit = (rng.choice([-2, 2]), rng.choice([-1, 1]))
        sh = e('OUT_BACK', f, 17, 21)
        diss = e('LINEAR', f, 18, 30)
        tcol = e('LINEAR', f, 18, 26)
        pop = out_back(prog(f, 28, 34)) if f >= 28 else 0.0
        if 28 <= f < 34:
            rng = np.random.RandomState(100 + f)
            jit = (rng.uniform(-2, 2), rng.uniform(-2, 2))
        lock_anim(cv, pos[0], 'A', 'E', shackle=sh, diss=diss, tcol=tcol, pop=pop, jit=jit)
        if 28 <= f < 34:
            t = prog(f, 28, 34)
            ui.shock(cv, pos[0], 22 + 40 * out_expo(t), TYPE_COL['E'], w=2.5, k=.8 * (1 - t))
    return cv.out()


# ================================================================== HUNTER RETICLE LOCK
def hunter_geo():
    S = stage()
    w = S.w
    cs = []
    for h in w.hunters:
        pt, _ = at(h['path'], plen(h['path']) * .72)
        cs.append(pt)
    c = (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)
    return cs, np.array(c)


def b_hunter(f, reduce=False):
    S = stage()
    w = S.w
    cs, ec = hunter_geo()
    cv = cworld('hunter', programs={'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, states={'t1_a': 'DOWN'})
    fade = e('IN_OUT_QUAD', f, 26, 34) if not reduce else e('LINEAR', f, 26, 34)
    strike = e('OUT_CUBIC', f, 26, 33)
    for i, h in enumerate(w.hunters):
        P = PX(h['path'])
        faded = i != 0
        kk = 1.0 if not faded else (1 - .78 * fade)
        if not faded:
            kk *= 1.0 + .25 * e('OUT_CUBIC', f, 24, 28)
        pts = P.sub(0, P.L, 4)
        pl = Lyr(pbox(pts, 10))
        t = 0.0
        while t < P.L:
            seg = P.sub(t, min(t + 9, P.L), 3)
            pl.line([tuple(x) for x in seg], 2.6 if not (faded and fade > .5) else 1.6, 255)
            t += 16
        cv.neonL(pl, WHITE * .85, core=.7 * kk, g1=(3, .4 * kk), g2=None)
        hy.head(cv, P, P.L * .72, 'E', sc=1.0 if not faded else (1 - .2 * fade), mode='ghost', k=.9 * kk, col=WHITE * .92)
        if faded and strike > 0:
            m = P.at(P.L * .5)[0]
            st = Lyr((m[0] - 30, m[1] - 24, m[0] + 30, m[1] + 24))
            a1 = clamp(strike * 2)
            a2 = clamp(strike * 2 - 1)
            st.line([(m[0] - 22, m[1] - 14), (m[0] - 22 + 44 * a1, m[1] - 14 + 28 * a1)], 3, 255)
            if a2 > 0:
                st.line([(m[0] - 22, m[1] + 14), (m[0] - 22 + 44 * a2, m[1] + 14 - 28 * a2)], 3, 255)
            cv.neonL(st, WHITE * .7, core=.6, g1=None, g2=None)
    # dashed leaders eye -> street points
    ln = Lyr(pbox(list(cs) + [ec], 10))
    for i, p in enumerate(cs):
        if i != 0 and fade > .5:
            continue
        ln.line([tuple(ec + np.array([0, 24])), tuple(p)], 1.6, 255, dash=(3, 5))
    cv.neonL(ln, WHITE * .8, core=.7, g1=(2, .4), g2=None)
    # eye: opens (dilates) at 12..16, scans before that, breathes after
    if reduce:
        open_ = 1.0
        off = 0.0
        br = 1.0
    else:
        open_ = .82 + .18 * out_back(prog(f, 12, 16)) if f >= 12 else .82
        off = 7 * math.sin(2 * math.pi * f / 24.0) * (1 - e('LINEAR', f, 12, 16)) if f < 16 else 0.0
        br = 1.0 + .08 * math.sin(2 * math.pi * f / 24.0)
    ui.hunter_eye(cv, ec + np.array([off, 0]), 54 * open_, k=.9 * br * (.75 + .25 * open_), col=WHITE * .92 + LATT * .08)
    # reticle
    if f >= 16:
        if reduce:
            ui.reticle(cv, cs[0], 66, WHITE, k=e('LINEAR', f, 16, 22))
        else:
            r0 = 66 * (1 + 2.2 * (1 - e('OUT_EXPO', f, 16, 24)))
            r0 *= 1 - .14 * math.sin(math.pi * clamp(prog(f, 24, 28)))
            ui.reticle(cv, cs[0], r0, WHITE, k=e('LINEAR', f, 16, 19))
            if f == 24:
                ui.flash(cv, cs[0], 90, WHITE, .5)
    # fire: white ram dashes ahead, yellow body behind
    if f >= 64:
        P = PX(w.hunters[0]['path'])
        t = e('LINEAR', f, 64, 76) if not reduce else 1.0
        s_h = P.L * .72 * t
        if reduce:
            hy.ribbon(cv, P, 'E', 0, P.L * .72, k=e('LINEAR', f, 64, 72))
        else:
            if s_h > 10:
                hy.ribbon(cv, P, 'E', 0, s_h, k=1.0)
            hy.head(cv, P, s_h, 'E', sc=1.5)
    return cv.out()


# ================================================================== HOME HIT
_HM = {}


def _home_pre(cv):
    S = stage()
    w = S.w
    R = w.routes['C']
    P = PX(R['path'])
    end = w.end('C')
    hy.ribbon(cv, P, 'N', R['ext'], end - 112, k=1.2)


def _home_world():
    return cworld('homehit', pre=_home_pre, states={'t1_a': 'DOWN', 't1_b': 'DOWN'},
                  programs={'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44, alpha=0))


def _deck(kind):
    S = stage()
    hm = S.home
    box = (hm[0] - 190, hm[1] - 190, hm[0] + 190, hm[1] + 170)
    kw = {'full': dict(hp=44), 'prev': dict(hp=44, preview=6), 'hit': dict(hp=44, hit=6, flash=.4), 'hit0': dict(hp=44, hit=6, flash=0.0),
          'scar': dict(hp=38, scar=6)}[kind]
    return S.cached(('deck', kind), lambda: spr(lambda cv: SC.home_deck(cv, hm, **kw), box))


def sparks(cv, home, n, hp, t, k=1.0, seed=2, R=74):
    rng = np.random.RandomState(seed)
    ly = Lyr((home[0] - 260, home[1] - 190, home[0] + 260, home[1] + 190))
    for i in range(hp - n, hp):
        ang = math.radians(-90 + i * 360 / 50)
        p0 = np.array([home[0] + (R - 2) * math.cos(ang), home[1] + (R - 2) * .643 * math.sin(ang)])
        d = np.array([math.cos(ang), math.sin(ang) * .7])
        dist = rng.uniform(40, 120) * t
        p1 = p0 + d * dist + np.array([0, -rng.uniform(10, 40) * t])
        ly.line([tuple(p0 + d * 12 * t), tuple(p1)], 2.4, 255, dash=(3, 3))
        ly.line([tuple(p1), tuple(p1 + d * 9)], 4.2, 255)
    cv.neonL(ly, TIER['DAMAGED'], core=1.0 * k, g1=(3, .9 * k), g2=(9, .5 * k), white=.5)


SHAKE = [(3, -2), (-3, 2), (2, -1), (-1, 1)]


def b_home(f, reduce=False, f_imp=36):
    """test C / board 08 frame. impact at f_imp. before it: telegraph hold; approach during the 6 f before impact."""
    S = stage()
    w = S.w
    R = w.routes['C']
    P = PX(R['path'])
    end = w.end('C')
    hm = S.home
    r = f - f_imp
    cv = _home_world()
    c = hm + np.array([0, -18])
    # head + dynamic ribbon end
    s_wait = end - 118
    if r < -6:
        s_head = s_wait
    elif r < 0:
        s_head = s_wait + (end - 46 - s_wait) * e('OUT_QUAD', r, -6, 0)
    else:
        s_head = end - 46
    kr = 1.2 if r < 8 else 1.2 - .75 * e('LINEAR', r, 8, 16)
    if s_head > end - 112:
        hy.ribbon(cv, P, 'N', end - 112, s_head, k=kr)
    # HOME deck by phase
    if r < 0:
        comp(cv, _deck('prev'))
    elif r < 22:
        comp(cv, _deck('hit' if r < 6 else 'hit0'))
    else:
        t = e('LINEAR', r, 22, 28)
        comp(cv, _deck('hit0'), 1 - t)
        comp(cv, _deck('scar'), t)
    # dim
    if r >= 0:
        dim = (1.0 if not reduce else e('LINEAR', r, 0, 6)) * (1 - e('IN_OUT_QUAD', r, 16, 28))
        ui.focus_dim(cv, hm, 460, (.5 if not reduce else .25) * dim)
    rf = r if r < 8 else (8 if r < 16 else r - 8)   # HIT HOLD: the effect layers freeze at their peak for 8 f
    if r >= 0:
        if reduce:
            if r < 3:
                ui.flash(cv, c, 170, TIER['DAMAGED'] * .5 + WHITE * .5, .30)
            kk = .45 * e('LINEAR', r, 0, 4) * (1 - e('LINEAR', r, 10, 24))
            ui.shock(cv, hm, 100, TIER['DAMAGED'], w=3, k=kk)
            hy.spark_ticks(cv, hm, 6, 44, k=.55 * e('LINEAR', r, 2, 8) * (1 - e('LINEAR', r, 12, 24)))
        else:
            if r <= 3:
                ui.flash(cv, c, 230, WHITE, [.95, .95, .5, .2][r])
            fk = .55 * (1 - e('LINEAR', rf, 0, 14))
            if fk > 0:
                ui.flash(cv, c, 150, TIER['DAMAGED'], fk)
            t1 = prog(rf, 0, 12)
            if t1 < 1:
                ui.shock(cv, hm, 100 * out_expo(t1) + 6, TIER['DAMAGED'], w=4, k=1 - t1)
            t2 = prog(rf, 3, 15)
            if 0 < t2 < 1:
                ui.shock(cv, hm, 150 * out_expo(t2) + 6, TIER['DAMAGED'], w=2.5, k=.6 * (1 - t2))
            ts = prog(rf, 1, 16)
            if 0 < ts < 1:
                sparks(cv, hm, 6, 44, out_quad(ts), k=1 - in_quad(prog(rf, 10, 16)))
            tb = prog(rf, 0, 20)
            if 0 < tb < 1:
                ui.bits(cv, c, TIER['DAMAGED'], n=55, r=170, seed=9, spread=out_quad(prog(rf, 0, 16)), k=1 - in_quad(prog(rf, 10, 20)))
            th = prog(rf, 0, 18)
            if 0 < th < 1:
                ui.hex_shards(cv, c, TIER['DAMAGED'], 12, max(10, 120 * out_quad(prog(rf, 0, 10))), seed=3, k=1 - in_quad(prog(rf, 8, 18)))
            if 2 <= rf < 10:
                ui.glitch_tear(cv, (60, 640, 720, 900), 1.0 * (1 - prog(rf, 2, 10)), seed=11 + rf, bands=12)
    # head
    if r < 0:
        hy.head(cv, P, s_head, 'N', sc=2.1)
    elif r < 4 and not reduce:
        hy.head(cv, P, s_head, 'N', sc=2.1, k=1 - e('LINEAR', r, 0, 4))
    elif r < 8 and reduce:
        hy.head(cv, P, s_head, 'N', sc=2.1, k=1 - e('LINEAR', r, 0, 8))
    # tile + number
    if r >= 6:
        tp = e('LINEAR', r, 6, 14) if reduce else e('OUT_CUBIC', r, 6, 9)
        rr = 34 if reduce else 34 * (.8 + .2 * e('OUT_BACK', r, 6, 12))
        hy.hex_tile(cv, (hm[0] + 96, hm[1] - 128), 'DAMAGED', None, r=rr, k=tp)
        ui.num_tag(cv, (hm[0] + 176, hm[1] - 126), '-6', TIER['DAMAGED'], 60, k=tp)
    img = cv.out()
    if not reduce and 0 <= r < 4:
        img = shift_img(img, *SHAKE[r])
    return img
