"""Scene library for the P2 motion tests and boards. Each beat function(f, reduce, mode) returns a uint8 frame.
mode 'test' -> 1280x720 with camera; mode 'board' -> 1920x1080 neutral camera (boards crop it)."""
from m2 import *
import hud as HD

HERO = ['t1_c', 't1_b', 't2_intel', 't1_a', 't2_virus']
SHAKE = [(3, -2), (-3, 2), (2, -1), (-1, 1)]
_G = {}


def nearest_s(R, pt):
    return float(np.argmin(np.hypot(*(R.P - np.asarray(pt)).T)))


def geo():
    if not _G:
        K1, K2, K3 = route('K1'), route('K2'), route('K3')
        tcB = site('t1_c')[0]
        _G['stop'] = {'K1': nearest_s(K1, tcB + np.array([34.0, -12.0])), 'K2': nearest_s(K2, site('t1_b')[0]), 'K3': nearest_s(K3, site('t2_intel')[0])}
        _G['tier'] = {'K1': ('t1_c', 'HOLDS'), 'K2': ('t1_b', 'SITES_LOST'), 'K3': ('t2_intel', 'UNTOUCHED')}
        _G['park'] = {'K1': 1030.0, 'K2': 640.0, 'K3': 760.0}
    return _G


def ptext(P, xy, s, size, col, anchor='mm'):
    P.d.text(((xy[0] - P.x0) * P.ss, (xy[1] - P.y0) * P.ss), s, font=HD.F(int(size * P.ss)), fill=P._c(col), anchor=anchor)


# ------------------------------------------------------------------ the scene
class Scene:
    def __init__(self, city=None):
        self.city = city
        self.dread = []
        self.plum_list = []
        self.plum_k = 0.4
        self.plum_kw = {}
        self.towers = {}
        for sid in world().sites:
            self.towers[sid] = dict(rank='hero' if sid in HERO else 'quiet', hs=1.0, k=1.0)
        self.rings = []
        self.blocks = []
        self.home = dict(hp=44, preview=0)
        self.beams = []
        self.heads = []
        self.tags = []
        self.fx = []        # drawn before heads
        self.fx_top = []    # drawn after heads
        self.cage = 1.0
        self.dim = None
        self.dark_amt = 0.45

    def std_rings(self, down_frac=0.6):
        g = geo()
        self.rings = [dict(sid='t1_c', tier='HOLDS'), dict(sid='t1_b', tier='SITES_LOST'), dict(sid='t2_intel', tier='UNTOUCHED'),
                      dict(sid='t1_a', tier='UNTOUCHED', frac=down_frac)]
        self.blocks = [dict(rid='K1', s=g['stop']['K1'], tier='HOLDS'), dict(rid='K2', s=g['stop']['K2'], tier='SITES_LOST'),
                       dict(rid='K3', s=g['stop']['K3'], tier='UNTOUCHED')]
        self.tags = [dict(sid='t1_c', tier='HOLDS'), dict(sid='t1_b', tier='SITES_LOST'), dict(sid='t2_intel', tier='UNTOUCHED', pips=1)]

    def rest_beams(self, k=0.85, flow_t=0.0, only=None):
        for rid in ('K1', 'K2', 'K3'):
            if only and rid not in only:
                continue
            R = route(rid)
            self.beams.append(dict(rid=rid, s0=R.ext, s1=R.L - 4, gain=k, flow=flow_t * 0.18))

    def render(self, t=0.0):
        fr = Frame(city=self.city)
        fr.dread(self.dread)
        fr.apply_dark(self.dark_amt)
        if self.plum_list:
            fr.plum(self.plum_list, k=self.plum_k, t=t, **self.plum_kw)
        for r in self.rings:
            r = dict(r)
            tier_ring(fr, r.pop('sid'), r.pop('tier'), **r)
        for b in self.blocks:
            b = dict(b)
            stop_block(fr, route(b.pop('rid')), b.pop('s'), b.pop('tier'), **b)
        home_marks(fr, **self.home)
        for b in self.beams:
            b = dict(b)
            R = route(b.pop('rid'))
            ribbon(fr, R, b.pop('s0'), b.pop('s1'), **b)
        order = sorted(self.towers, key=lambda s: site(s)[0][1])
        for sid in order:
            tw = self.towers[sid]
            if tw['hs'] > 0.02 and tw['k'] > 0.02:
                tower(fr, sid, tw['rank'], k=tw['k'], hs=tw['hs'], tint=tw.get('tint'))
        if self.cage > 0:
            cage(fr, k=self.cage)
        for fn in self.fx:
            fn(fr)
        for h in self.heads:
            h = dict(h)
            R = route(h.pop('rid')) if 'rid' in h else None
            if R is not None:
                s = h.pop('s')
                pos = R.pos(s)
                ang = R.ang(s)
                typ = R.typ
            else:
                pos, ang, typ = h.pop('pos'), h.pop('ang'), h.pop('typ')
            head(fr, typ, pos, ang, **h)
        for tg in self.tags:
            tg = dict(tg)
            tag(fr, tg.pop('sid'), tg.pop('tier'), **tg)
        for fn in self.fx_top:
            fn(fr)
        if self.dim is not None:
            c, rad, amt = self.dim
            yy, xx = np.mgrid[0:H:2, 0:W:2].astype(np.float32)
            d = np.hypot(xx - c[0], (yy - c[1]) / 0.72)
            m = smoothstep(rad * .5, rad * 1.3, d) * amt
            m = np.asarray(Image.fromarray(m.astype(np.float32)).resize((W, H), Image.BILINEAR))
            fr.img *= (1 - m)[..., None]
        return fr


def cam_apply(img, z, c, par=(0.0, 0.0), zpar=0.0):
    hw, hh = 960.0 / z, 540.0 / z
    cx = float(np.clip(c[0], hw, W - hw))
    cy = float(np.clip(c[1], hh, H - hh))
    return camera(img, z=z, fx=960.0, fy=540.0, pan=(cx - 960.0, cy - 540.0), par=par, zpar=zpar)


def assemble(fr, f, reduce, mode, cam=None, huds=(), shake=(0, 0), fringe_k=1.0, glow=1.0):
    img = fr if isinstance(fr, np.ndarray) else fr.resolve(glow_gain=glow)
    if mode == 'board':
        out = img
        for a in huds:
            if a is not None:
                al = a[..., 3:4]
                out = out * (1 - al) + a[..., :3] * al
        if shake != (0, 0):
            out = np.roll(out, (shake[1] * 2, shake[0] * 2), (0, 1))
        return u8(out)
    z, c, par = cam if cam else (1.0, (960, 540), (0, 0))
    out = cam_apply(img, z, c, par)
    out = HD.comp_hud(out, huds)
    if shake != (0, 0):
        out = np.roll(out, (shake[1], shake[0]), (0, 1))
    out = finish(out, f, scan=not reduce, fringe=not reduce)
    return u8(out)


def std_huds(hp=44, heat=80, infected=0, hand_lift=0.0, chips_k=1.0, dy=0.0, cards=True, hp_col=None, slots=None, hand_k=1.0):
    ch = HD.hud_chips(hp=hp, heat=heat, infected=infected, k=chips_k, dy=dy, hp_col=hp_col)
    layers = [ch]
    if cards:
        sl = slots if slots is not None else HD.slots_default(lift=hand_lift)
        a = HD.hand(sl)
        a[..., 3] *= hand_k
        layers.append(a)
    return layers


def cam_track(z, focus, lag_c=None):
    return (z, focus, (0, 0))


# ------------------------------------------------------------------ daemon sim
class Daemon:
    S_START = 1200.0

    def __init__(self):
        g = geo()
        self.R = route('K1')
        self.s_stop = g['stop']['K1']
        P = self.R.P
        ang = np.unwrap(np.arctan2(np.gradient(P[:, 1]), np.gradient(P[:, 0])))
        turn = np.abs(np.concatenate([np.zeros(6), ang[12:] - ang[:-12], np.zeros(6)]))[:len(P)]
        slow = 1 - .40 * np.clip(turn / .9, 0, 1)
        self.slow = ndi.gaussian_filter1d(slow, 10)
        self.t_launch = 34
        self.v0 = 14.0
        s = self.S_START
        self.table = {}
        f = self.t_launch
        while f < 600:
            ramp = min(1.0, (f - self.t_launch + 1) / 5.0) ** 1.5
            v = self.v0 * self.slow[int(min(s, len(self.slow) - 1))] * ramp
            rem = self.s_stop - 40 - s
            v = min(v, max(1.4, .30 * rem))
            s += v
            self.table[f] = s
            if self.s_stop - 40 - s < 1.0:
                break
            f += 1
        self.f_arr = f

    def s_at(self, f):
        if f < self.t_launch - 4:
            return self.S_START
        if f < self.t_launch:
            return self.S_START - 10 * e('IN_QUAD', f, self.t_launch - 4, self.t_launch)
        return self.table.get(f, self.s_stop - 40)


_D = []


def dmn():
    if not _D:
        _D.append(Daemon())
    return _D[0]


# ------------------------------------------------------------------ shared fx
def shield_fx(S, r, reduce, scale=1.0):
    """HOLDS shield flash at the K1 stop block. r = frames since contact."""
    g = geo()
    R = route('K1')
    s_stop = g['stop']['K1']
    p = R.pos(s_stop)
    ta = R.ab_tan(s_stop)
    na = np.array([-ta[1], ta[0]])
    col = PAL['HOLDS']
    if r < 0:
        return
    rf = r if r < 6 else (6 if r < 14 else r - 8)
    def fx(fr):
        if reduce:
            if r < 3:
                flash(fr, p, 200 * scale, PAL['WHITE'] * .5 + col * .5, .30)
            wk = e('LINEAR', r, 0, 6) * (1 - e('LINEAR', r, 20, 36))
            wall_quad(fr, p, na, 15.0, 15.0, 'D', k=.8 * wk, tint=col, bright=1.2)
            hex_ripple(fr, p, 96 * scale, col, .6 * e('LINEAR', r, 0, 6) * (1 - e('LINEAR', r, 12, 30)), w=3.0)
            bits(fr, p + np.array([0, -10]), col, 26, .85, seed=4, spread=70 * scale, k=e('LINEAR', r, 2, 8) * (1 - e('LINEAR', r, 20, 36)))
            return
        if r <= 1:
            flash(fr, p, 330 * scale, PAL['WHITE'], [.95, .75][r])
        fk = .5 * (1 - e('LINEAR', rf, 0, 14)) * (1 - e('LINEAR', r, 22, 34))
        flash(fr, p, 230 * scale, col, fk * 1.2)
        wk = (1.2 if rf < 8 else 1.2 - e('LINEAR', rf, 8, 16)) * (1 - e('IN_OUT_QUAD', r, 24, 36)) * e('OUT_CUBIC', r, 0, 3)
        wall_quad(fr, p, na, 15.0, 15.0, 'D', k=clamp01(wk) * .95, tint=col, bright=1.0 + .8 * (1 - e('LINEAR', rf, 0, 10)), gk=.6)
        t1 = prog(rf, 0, 12)
        hex_ripple(fr, p, (18 + 110 * e('OUT_EXPO', rf, 0, 12)) * scale, col, (1 - t1) * (1 - e('LINEAR', r, 22, 34)), w=4.0)
        t2 = prog(rf, 3, 15)
        if 0 < t2 < 1:
            hex_ripple(fr, p, (18 + 160 * e('OUT_EXPO', rf, 3, 15)) * scale, PAL['WHITE'], .5 * (1 - t2), w=2.0)
        tb = prog(rf, 0, 20)
        if 0 < tb:
            bits(fr, p + np.array([0, -10]), col, 38, e('OUT_QUAD', rf, 0, 20), seed=4, spread=80 * scale, k=1 - e('IN_QUAD', r, 18, 34))
    S.fx.append(fx)


def home_fx(S, r, reduce):
    hm = home_c()
    c = hm + np.array([0, -16])
    col = PAL['DAMAGED']
    if r < 0:
        return
    rf = r if r < 8 else (8 if r < 16 else r - 8)
    def fx(fr):
        if reduce:
            if r < 3:
                flash(fr, c, 220, PAL['WHITE'] * .5 + col * .5, .30)
            hex_ripple(fr, hm, 100, col, .5 * e('LINEAR', r, 0, 4) * (1 - e('LINEAR', r, 10, 26)), w=3.0)
            fracture_star(fr, c, 130, col, .85 * e('LINEAR', r, 2, 8) * (1 - e('LINEAR', r, 20, 34)))
            bits(fr, c, col, 36, .8, seed=9, spread=110, k=e('LINEAR', r, 2, 8) * (1 - e('LINEAR', r, 20, 34)))
            return
        if r <= 3:
            flash(fr, c, 250, PAL['WHITE'], [.95, .95, .5, .2][r])
        fk = .55 * (1 - e('LINEAR', rf, 0, 14)) * (1 - e('LINEAR', r, 20, 32))
        flash(fr, c, 170, col, fk)
        t1 = prog(rf, 0, 12)
        hex_ripple(fr, hm, 12 + 100 * e('OUT_EXPO', rf, 0, 12), col, (1 - t1) * (1 - e('LINEAR', r, 20, 32)), w=4.5)
        t2 = prog(rf, 3, 15)
        if 0 < t2 < 1:
            hex_ripple(fr, hm, 12 + 150 * e('OUT_EXPO', rf, 3, 15), col, .6 * (1 - t2), w=2.5)
        fracture_star(fr, c, 40 + 110 * e('OUT_EXPO', rf, 0, 10), col, (1 - e('IN_QUAD', rf, 8, 18)) * (1 - e('LINEAR', r, 20, 32)))
        bits(fr, c, col, 52, e('OUT_QUAD', rf, 0, 16), seed=9, spread=120, k=1 - e('IN_QUAD', r, 18, 34))
    S.fx.append(fx)


def home_tile(S, r, reduce):
    if r < 6:
        return
    hm = home_c()
    c = (hm[0] + 96, hm[1] - 128)
    k = e('LINEAR', r, 6, 14) if reduce else e('OUT_CUBIC', r, 6, 9)
    rr = 34 if reduce else 34 * (.8 + .2 * e('OUT_BACK', r, 6, 12))
    def fx(fr):
        P = Pl((c[0] - 60, c[1] - 50, c[0] + 140, c[1] + 50))
        hx = lambda q: [(c[0] + q * math.cos(math.radians(60 * i + 30)), c[1] + q * math.sin(math.radians(60 * i + 30))) for i in range(6)]
        P.poly(hx(rr + 3), PAL['INK'])
        P.poly(hx(rr), PAL['DAMAGED'])
        glyph(P, 'DAMAGED', c, rr, PAL['INK'])
        ptext(P, (c[0] + 82, c[1] + 2), '-6', 44, PAL['DAMAGED'])
        fr.pl(P, gk=.4, k=k)
    S.fx_top.append(fx)


def scorch(S, r):
    """DAMAGED aftermath: burn mark and pencil tallies (grease white) next to HOME."""
    if r < 2:
        return
    hm = home_c()
    def fx(fr):
        k = e('LINEAR', r, 2, 10)
        glow_disc(fr, hm, 30.0, PAL['INK'], .0)
        P = Pl((hm[0] - 190, hm[1] - 120, hm[0] + 190, hm[1] + 120))
        rng = np.random.RandomState(8)
        for i in range(16):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(14, 28)
            q = [gs(hm, rr * math.cos(a), rr * math.sin(a))]
            ln = rng.uniform(6, 16)
            q.append(gs(hm, (rr + ln) * math.cos(a + .1), (rr + ln) * math.sin(a + .1)))
            P.line(q, PAL['INK'], 5.0, .75)
        if r >= 14:
            kt = e('LINEAR', r, 14, 22)
            for i in range(6):
                x0 = hm[0] + 128 + i * 12
                P.line([(x0, hm[1] + 38), (x0 + 3, hm[1] + 66)], PAL['WARM'], 3.0, .95 * kt)
        fr.pl(P, gk=0.0, k=k)
    S.fx.append(fx)


# ================================================================== TEST: daemon travel to the stop block (K1 D -> t1_c)
N_DAEMON = 150


def b_daemon(f, reduce=False, mode='test'):
    D = dmn()
    g = geo()
    R1, R2, R3 = route('K1'), route('K2'), route('K3')
    S = Scene()
    S.std_rings(0.6)
    f_imp = D.f_arr
    r = f - f_imp
    s_stop = D.s_stop
    s_arr = s_stop - 40
    if not reduce:
        sh = D.s_at(f) if f < f_imp else s_arr
    else:
        sh = D.S_START if f < f_imp - 8 else (D.S_START if f < f_imp - 8 else s_arr)
    # beams: all three at rest; K1 lit wake behind its head
    gm = 0.90
    S.beams.append(dict(rid='K2', s0=R2.ext, s1=R2.L - 4, gain=.80, flow=f * .06))
    S.beams.append(dict(rid='K3', s0=R3.ext, s1=R3.L - 4, gain=.80, flow=f * .06))
    if not reduce:
        sw = min(sh, s_stop + 20)
        S.beams.append(dict(rid='K1', s0=R1.ext, s1=R1.L - 4, gain=gm, flow=f * .06,
                            gain_fn=lambda s, sw=sw: gm + 1.35 * np.exp(-np.clip(sw - s, 0, None) / 200.0) * (s <= sw + 6)))
    else:
        t = e('IN_OUT_QUAD', f, f_imp - 8, f_imp)
        S.beams.append(dict(rid='K1', s0=R1.ext, s1=R1.L - 4, gain=gm + .6 * t, flow=0.0))
    # dread shadow ahead of every head along its route
    S.dread = [(R1, sh if not reduce else (D.S_START if f < f_imp - 4 else s_arr), 1.0 if r < 0 else 1.0 * (1 - e('LINEAR', r, 0, 10))), (R2, g['park']['K2'], .7), (R3, g['park']['K3'], .7)]
    S.plum_list = [((1650.0, 470.0), 190.0 + .3 * f)]
    S.plum_k = 0.40
    S.home = dict(hp=44, preview=0)
    # pass-through ripple on t2_virus
    if not reduce:
        pv = nearest_s(R1, site('t2_virus')[0])
        fa = [ff for ff, ss in D.table.items() if ss >= pv]
        if fa:
            t = prog(f, fa[0], fa[0] + 8)
            if 0 < t < 1:
                S.fx.append(lambda fr, t=t: hex_ripple(fr, site('t2_virus')[0], 40 + 70 * e('OUT_CUBIC', t, 0, 1), PAL['D'], .8 * (1 - t), w=3.0))
    # heads
    p_pos = lambda s: R1.pos(s)
    heads = []
    for R, s in ((R2, g['park']['K2']), (R3, g['park']['K3'])):
        heads.append(dict(rid=R.rid, s=s, alpha=.55))
    if r < 0:
        if not reduce:
            heads.append(dict(rid='K1', s=sh, alpha=1.0))
        else:
            t = e('IN_OUT_QUAD', f, f_imp - 8, f_imp)
            heads.append(dict(rid='K1', s=D.S_START, alpha=1 - t))
            heads.append(dict(rid='K1', s=s_arr, alpha=t))
    else:
        heads.append(dict(rid='K1', s=s_arr, alpha=1 - e('LINEAR', r, 4, 12), halo=3.0 if r < 12 else 0.0))
    S.heads = heads
    # impact
    shield_fx(S, r, reduce)
    if r >= 0:
        # block surges, tag pip drops, tower t1_c brightens for a moment
        S.towers['t1_c']['k'] = 1.0
        S.blocks[0]['t'] = f
        S.tags[0]['pips'] = 3 if r < 8 else 2
    else:
        S.blocks[0]['t'] = f
    if mode == 'board' and False:
        pass
    S.towers['t2_virus']['k'] = 1.0
    fr = S.render(f)
    # camera: slow push-in on the telegraph, track the head, settle on the block
    pb = R1.pos(s_stop)
    if reduce:
        cam = (1.10, (pb[0] + 120, pb[1] - 50), (0, 0))
    else:
        zt = 1.0 + .06 * e('IN_OUT_QUAD', f, 0, 34)
        zt += .08 * e('IN_OUT_QUAD', f, 34, f_imp)
        zt += .03 * e('OUT_QUAD', f, f_imp, f_imp + 40)
        hp_ = R1.pos(sh)
        w_ = e('IN_OUT_QUAD', f, 24, f_imp)
        foc = (lerp((D_foc0()[0]), hp_[0] * .55 + pb[0] * .45, w_), lerp(D_foc0()[1], hp_[1] * .55 + pb[1] * .45, w_))
        par = (14 * e('IN_OUT_QUAD', f, 0, f_imp), 6 * e('IN_OUT_QUAD', f, 0, f_imp))
        cam = (zt, foc, par)
    huds = std_huds()
    return assemble(fr, f, reduce, mode, cam, huds)


def D_foc0():
    D = dmn()
    a = route('K1').pos(D.S_START)
    b = route('K1').pos(D.s_stop)
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
