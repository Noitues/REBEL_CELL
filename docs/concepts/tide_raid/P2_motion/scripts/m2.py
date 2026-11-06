"""P2 motion engine: numpy/PIL compositor over the P2 shared base (graded city, occluder mask, depth, pre-rendered heads).
Everything is drawn on the ground plane in 'ab' BU space (a = screen-right, b = screen-down on the ground) so marks share the plate camera:
screen = c + (KX*a, KY*b - KZ*z).  Beams are textured ribbons (P2 textures) so they carry the same pattern as the plates.
Camera = one depth-aware warp (zoom + pan + parallax) of the world layer; HUD and finishing are applied after it."""
import sys, os, math, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_plates/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi
import p1lib as L

BASE = 'D:/rc_scratch/tide_concepts/p2_base/'
TEX = 'D:/rc_scratch/tide_concepts/p2_work/tex/'
W, H = 1920, 1080
OW, OH = 1280, 720
KX = 1.0 / L.BU_PX
KY = KX * 0.6428
KZ = KX * 0.766
LUM = np.array([.2126, .7152, .0722], np.float32)


def hexc(s):
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


PAL = dict(D=hexc('4690FF'), N=hexc('FF40D6'), E=hexc('FFEE3A'),
           UNTOUCHED=hexc('B8FFF2'), HOLDS=hexc('19C9B4'), SITES_LOST=hexc('C98410'), DAMAGED=hexc('FF9A00'), BREACHED=hexc('FF3347'),
           WARM=hexc('F6F1E4'), WHITE=np.ones(3, np.float32), INK=hexc('070515'), DEAD=hexc('2A3150'),
           PLUM_BODY=hexc('1E0A22'), PLUM_MID=hexc('4A1440'), VEIN=hexc('FF3FA8'), HAIR=hexc('FFD6F0'),
           SLATE=hexc('7C88AE'), QUIET=hexc('56608A'), CAGE=hexc('55E0A0'), FOG=hexc('9C8CFF'), LIME=hexc('C6FF2E'),
           LATT=hexc('2FB8E8'), HEAT=hexc('F2B77C'), TEAL=hexc('19C9B4'), BONE=hexc('F6F0DE'), SODIUM=hexc('FF5C14'))
TYPE_HUE = {'D': PAL['D'], 'N': PAL['N'], 'E': PAL['E']}
HW = {'D': 2.1, 'N': 2.2, 'E': 2.4}
LENU = {'D': 16.0, 'N': 12.0, 'E': 16.0}
TOWER_H = {1: 27.0, 2: 35.0, 3: 44.0}
TOWER_A = {1: 4.6, 2: 4.2, 3: 4.8}
TIER_R = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES_LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}
HOME_PX = None


# ------------------------------------------------------------------ easing
def clamp01(x):
    return max(0.0, min(1.0, x))


def prog(f, a, b):
    return clamp01((f - a) / float(max(b - a, 1e-6)))


def _ease(name, t):
    if name == 'LINEAR':
        return t
    if name == 'STEP':
        return 1.0 if t >= 1 else 0.0
    if name == 'OUT_CUBIC':
        return 1 - (1 - t) ** 3
    if name == 'IN_CUBIC':
        return t ** 3
    if name == 'IN_OUT_CUBIC':
        return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
    if name == 'OUT_QUAD':
        return 1 - (1 - t) ** 2
    if name == 'IN_QUAD':
        return t * t
    if name == 'IN_OUT_QUAD':
        return 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2
    if name == 'OUT_EXPO':
        return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)
    if name == 'OUT_BACK':
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
    if name == 'OUT_BACK_SOFT':
        c1 = 0.9
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
    raise KeyError(name)


def e(name, f, a, b):
    return _ease(name, prog(f, a, b))


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, np.float32) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ assets (lazy, per process)
_A = {}


def assets():
    if _A:
        return _A
    city = np.asarray(Image.open(BASE + 'city_default.png').convert('RGB'), np.float32) / 255
    occ = np.asarray(Image.open(BASE + 'layers/occluder_mask.png'), np.float32) / 255
    occ = ndi.gaussian_filter(occ, 0.7)
    dep = np.asarray(Image.open(BASE + 'layers/depth_norm_16.png'), np.float32) / 65535
    emis = np.asarray(Image.open(BASE + 'layers/city_emissive.png').convert('RGB'), np.float32) / 255
    street = np.asarray(Image.open(BASE + 'layers/street_mask.png'), np.float32) / 255
    heads = {}
    for t in 'DNE':
        for k in range(16):
            im = Image.open(BASE + 'heads/%s_%03d.png' % (t, int(k * 22.5))).convert('RGBA')
            a = np.asarray(im, np.float32) / 255
            heads[(t, k)] = a
    _A.update(city=city, occ=occ, dep=dep, emis=emis, street=street, heads=heads)
    _A['dep_o'] = np.asarray(Image.fromarray(dep).resize((OW, OH), Image.BILINEAR), np.float32)
    rng = np.random.RandomState(11)
    n = lambda sc, s: ndi.gaussian_filter(rng.rand(H // 2, W // 2).astype(np.float32), s)
    n1 = n(0, 14); n1 = (n1 - n1.min()) / (n1.max() - n1.min())
    n2 = n(0, 5); n2 = (n2 - n2.min()) / (n2.max() - n2.min())
    _A['n1'] = n1
    _A['n2'] = n2
    ys, xs = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
    _A['yy2'], _A['xx2'] = ys * 2 + 1, xs * 2 + 1
    return _A


FONT = None


def font(sz):
    for p in ('C:/Windows/Fonts/bahnschrift.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/arial.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


# ------------------------------------------------------------------ world: routes / sites
_W = {}


def world():
    if not _W:
        _W['w'] = L.load_world()
    return _W['w']


def gs(c, a, b, z=0.0):
    return (c[0] + KX * a, c[1] + KY * b - KZ * z)


def ab_of(p):
    return np.array([p[0] / KX, p[1] / KY])


class Route:
    def __init__(self, rid, path=None, typ=None):
        w = world()
        r = w.routes[rid] if path is None else dict(path=path, typ=typ, ext=0.0, sites=[])
        self.rid = rid
        self.typ = r['typ']
        self.ext = float(r['ext'])
        p = np.asarray(r['path'], float)
        d = np.hypot(*np.diff(p, axis=0).T)
        cs = np.concatenate([[0], np.cumsum(d)])
        self.L = float(cs[-1])
        sv = np.arange(0, self.L, 1.0)
        self.P = np.stack([np.interp(sv, cs, p[:, 0]), np.interp(sv, cs, p[:, 1])], -1)
        self.sites = r['sites']
        self._rb = None

    def pos(self, s):
        s = np.clip(s, 0, len(self.P) - 1.001)
        i = int(s)
        t = s - i
        return self.P[i] * (1 - t) + self.P[i + 1] * t

    def ang(self, s, d=24):
        a = self.pos(max(s - d, 0))
        b = self.pos(min(s + d, len(self.P) - 1.01))
        return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))

    def ab_tan(self, s, d=12):
        a = ab_of(self.pos(max(s - d, 0)))
        b = ab_of(self.pos(min(s + d, len(self.P) - 1.01)))
        t = b - a
        return t / max(np.hypot(*t), 1e-6)

    def ribbon_map(self):
        """precompute the strip (screen pixel list with arclength s, BU arclength u and signed lateral offset)."""
        if self._rb is not None:
            return self._rb
        hw = HW[self.typ]
        cas = 1.0
        P = self.P
        ab = P / np.array([KX, KY])
        t = np.gradient(ab, axis=0)
        t = ndi.uniform_filter1d(t, 9, axis=0)
        t /= np.maximum(np.hypot(t[:, 0], t[:, 1]), 1e-6)[:, None]
        n = np.stack([-t[:, 1], t[:, 0]], -1)
        seg = np.hypot(*np.diff(ab, axis=0).T)
        u = np.concatenate([[0], np.cumsum(seg)])
        sub = 0.5
        sidx = np.arange(0, len(P) - 1, sub)
        Pi = np.stack([np.interp(sidx, np.arange(len(P)), P[:, 0]), np.interp(sidx, np.arange(len(P)), P[:, 1])], -1)
        ni = np.stack([np.interp(sidx, np.arange(len(P)), n[:, 0]), np.interp(sidx, np.arange(len(P)), n[:, 1])], -1)
        ui = np.interp(sidx, np.arange(len(P)), u)
        offs = np.arange(-(hw + cas), hw + cas + 1e-6, 0.11)
        sx = Pi[:, 0:1] + KX * ni[:, 0:1] * offs[None]
        sy = Pi[:, 1:2] + KY * ni[:, 1:2] * offs[None]
        ix = np.round(sx).astype(np.int32)
        iy = np.round(sy).astype(np.int32)
        ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        S = np.broadcast_to(sidx[:, None], ix.shape)
        U = np.broadcast_to(ui[:, None], ix.shape)
        O = np.broadcast_to(offs[None], ix.shape)
        flat = (iy * W + ix)[ok]
        # last write wins -> keep the sample nearest the centre line per pixel
        order = np.argsort(-np.abs(O[ok]), kind='stable')
        flat = flat[order]
        Sv, Uv, Ov = S[ok][order], U[ok][order], O[ok][order]
        m = np.full(H * W, -1, np.int64)
        m[flat] = np.arange(len(flat))
        sel = m[m >= 0]
        fl = flat[sel]
        self._rb = dict(iy=(fl // W).astype(np.int32), ix=(fl % W).astype(np.int32), s=Sv[sel].astype(np.float32),
                        u=Uv[sel].astype(np.float32), off=Ov[sel].astype(np.float32), hw=hw, cas=cas)
        return self._rb


_R = {}


def route(rid):
    if rid not in _R:
        _R[rid] = Route(rid)
    return _R[rid]


_TX = {}


def ribbon_tex(typ):
    if typ not in _TX:
        im = Image.open(TEX + 'ribbon_%s.png' % typ).convert('RGBA')
        im = im.resize((256, 36), Image.BOX)
        a = np.asarray(im, np.float32) / 255
        _TX[typ] = a
    return _TX[typ]


SITE_B = {}


def site(sid):
    if sid not in SITE_B:
        SITE_B[sid] = (np.asarray(world().sites[sid]['B'], float), world().sites[sid]['tier'])
    return SITE_B[sid]


def home_c():
    return np.asarray(world().home, float)


# ------------------------------------------------------------------ paint layer (2x supersampled PIL, replace semantics)
class Pl:
    def __init__(self, box, ss=2):
        x0, y0, x1, y1 = [int(v) for v in box]
        self.x0, self.y0 = x0 // 4 * 4, y0 // 4 * 4
        self.x1, self.y1 = -(-x1 // 4) * 4, -(-y1 // 4) * 4
        self.x0, self.y0 = max(self.x0, 0), max(self.y0, 0)
        self.x1, self.y1 = min(self.x1, W), min(self.y1, H)
        self.ss = ss
        self.w, self.h = max(self.x1 - self.x0, 4), max(self.y1 - self.y0, 4)
        self.im = Image.new('RGBA', (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [((x - self.x0) * self.ss, (y - self.y0) * self.ss) for x, y in pts]

    @staticmethod
    def _c(col, a=1.0):
        c = np.clip(np.asarray(col, np.float32), 0, 1)
        return (int(c[0] * 255 + .5), int(c[1] * 255 + .5), int(c[2] * 255 + .5), int(clamp01(a) * 255 + .5))

    def poly(self, pts, col, a=1.0):
        if len(pts) >= 3:
            self.d.polygon(self._p(pts), fill=self._c(col, a))

    def clear_poly(self, pts):
        self.d.polygon(self._p(pts), fill=(0, 0, 0, 0))

    def line(self, pts, col, wpx, a=1.0):
        self.d.line(self._p(pts), fill=self._c(col, a), width=max(1, int(round(wpx * self.ss))), joint='curve')

    def circle(self, c, r, col, a=1.0):
        x, y = self._p([c])[0]
        rr = r * self.ss
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=self._c(col, a))

    def arrays(self):
        im = self.im.resize((self.w, self.h), Image.BOX) if self.ss != 1 else self.im
        a = np.asarray(im, np.float32) / 255
        return a[..., :3], a[..., 3]


def ell(c, r, n=72, z=0.0, a0=0.0, a1=2 * math.pi):
    t = np.linspace(a0, a1, n, endpoint=(a1 - a0) < 2 * math.pi - 1e-6)
    return [gs(c, r * math.cos(x), r * math.sin(x), z) for x in t]


def poly_ab(c, pts_ab, z=0.0):
    return [gs(c, p[0], p[1], z) for p in pts_ab]


def rot(pts, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x * ca - y * sa, x * sa + y * ca) for x, y in pts]


def bbox_pts(pts, pad=6):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


# ------------------------------------------------------------------ the frame
class Frame:
    def __init__(self, scn='default', city=None):
        A = assets()
        self.A = A
        self.img = (A['city'] if city is None else city).copy()
        self.gl = np.zeros((H // 4, W // 4, 3), np.float32)
        self.dark = np.zeros((H // 4, W // 4), np.float32)
        self.post = []            # deferred full-frame ops (flash)

    # ---- dense layers
    def over(self, rgb, a, x0, y0, gk=0.5, occ=0.0, k=1.0):
        """straight-alpha RGBA patch. occ in 0..1: how much the occluder mask hides it (1 = fully)."""
        h, w = a.shape
        x1, y1 = x0 + w, y0 + h
        cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        rgb = rgb[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        a = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * k
        if occ > 0:
            o = self.A['occ'][cy0:cy1, cx0:cx1]
            a = a * (1 - occ * o)
        sub = self.img[cy0:cy1, cx0:cx1]
        sub[:] = sub * (1 - a[..., None]) + rgb * a[..., None]
        if gk > 0:
            self.glow_add(rgb * a[..., None] * gk, cx0, cy0)

    def add(self, rgb, a, x0, y0, gk=0.4, occ=0.0, k=1.0):
        h, w = a.shape[:2]
        cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        a = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * k
        if rgb.ndim == 3:
            rgb = rgb[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        if occ > 0:
            a = a * (1 - occ * self.A['occ'][cy0:cy1, cx0:cx1])
        add = (rgb * a[..., None]) if a.ndim == 2 else rgb * a
        self.img[cy0:cy1, cx0:cx1] += add
        if gk > 0:
            self.glow_add(add * gk, cx0, cy0)

    def glow_add(self, rgb, x0, y0):
        h, w = rgb.shape[:2]
        ax0, ay0 = x0 // 4 * 4, y0 // 4 * 4
        ax1, ay1 = -(-(x0 + w) // 4) * 4, -(-(y0 + h) // 4) * 4
        pad = np.zeros((ay1 - ay0, ax1 - ax0, 3), np.float32)
        pad[y0 - ay0:y0 - ay0 + h, x0 - ax0:x0 - ax0 + w] = rgb
        q = pad.reshape((ay1 - ay0) // 4, 4, (ax1 - ax0) // 4, 4, 3).mean((1, 3))
        gy0, gx0 = ay0 // 4, ax0 // 4
        sl = self.gl[gy0:gy0 + q.shape[0], gx0:gx0 + q.shape[1]]
        sl += q[:sl.shape[0], :sl.shape[1]]

    def pl(self, p, gk=0.5, occ=0.0, k=1.0, add=False):
        rgb, a = p.arrays()
        if add:
            self.add(rgb, a, p.x0, p.y0, gk=gk, occ=occ, k=k)
        else:
            self.over(rgb, a, p.x0, p.y0, gk=gk, occ=occ, k=k)

    # ---- sparse (ribbon) paint with occlusion + ghost pass
    def sparse(self, iy, ix, rgb, a, ghost_rgb=None, ghost_a=None, gk=0.5, corridor=None, gw=None):
        occ = self.A['occ'][iy, ix]
        vis = a * (1 - occ)
        cur = self.img[iy, ix]
        self.img[iy, ix] = cur * (1 - vis[:, None]) + rgb * vis[:, None]
        if ghost_a is not None:
            ga = ghost_a * occ
            cur = self.img[iy, ix]
            self.img[iy, ix] = cur * (1 - ga[:, None]) + ghost_rgb * ga[:, None]
        if gk > 0:
            em = rgb * vis[:, None] * gk * (1.0 if gw is None else (gw ** 1.5)[:, None])
            if ghost_a is not None:
                em = em + ghost_rgb * (ghost_a * occ)[:, None] * gk * .5
            fl = (iy // 4) * (W // 4) + (ix // 4)
            for c in range(3):
                self.gl[..., c] += np.bincount(fl, weights=em[:, c] / 16.0, minlength=(H // 4) * (W // 4)).reshape(H // 4, W // 4)

    def darken_corridor(self, iy, ix, k):
        occ = self.A['occ'][iy, ix]
        self.img[iy, ix] *= (1 - k * occ)[:, None]

    # ---- masks
    def dread(self, items):
        """items: (route, s_head, k): city darkens up to 45% in a tapering corridor 220 px ahead of the head."""
        for R, s, k in items:
            if k <= 0:
                continue
            ss = np.arange(s + 14, min(s + 230, R.L - 1), 9.0)
            if len(ss) == 0:
                continue
            for sv in ss:
                p = R.pos(sv) / 4.0
                f = (1 - (sv - s) / 230.0)
                sig = 9 + 6 * f
                x0, x1 = int(max(p[0] - 3 * sig, 0)), int(min(p[0] + 3 * sig + 1, W // 4))
                y0, y1 = int(max(p[1] - 3 * sig, 0)), int(min(p[1] + 3 * sig + 1, H // 4))
                if x1 <= x0 or y1 <= y0:
                    continue
                yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
                g = np.exp(-((xx - p[0]) ** 2 + ((yy - p[1]) / 0.7) ** 2) / (2 * sig * sig)) * f ** 0.8 * k
                self.dark[y0:y1, x0:x1] = np.maximum(self.dark[y0:y1, x0:x1], g)

    def apply_dark(self, amt=0.45):
        if self.dark.max() <= 0:
            return
        m = np.asarray(Image.fromarray(self.dark).resize((W, H), Image.BILINEAR), np.float32)
        self.img *= (1 - amt * m)[..., None] * 1.0 + np.array([0, 0, 0], np.float32)
        # a hint of cool shadow
        self.img += (amt * m)[..., None] * np.array([0.004, 0.006, 0.016], np.float32)

    def plum(self, centers, k=0.4, t=0.0, step_pulse=0.0, hair=True, dim_lights=0.0):
        """plum creep / Bloom. centers: list of ((x,y), R) in 1920 px. half-res field, ellipse metric (iso)."""
        A = self.A
        xx, yy, n1, n2 = A['xx2'], A['yy2'], A['n1'], A['n2']
        best = None
        for (c, R) in centers:
            if R <= 1:
                continue
            d = np.sqrt((xx - c[0]) ** 2 + ((yy - c[1]) / 0.643) ** 2)
            warp = R * (1 + 0.30 * (n1 - .5) * 2) + 7 * (n2 - .5) * 2
            sd = warp - d                       # >0 inside
            best = sd if best is None else np.maximum(best, sd)
        if best is None:
            return
        m = np.clip(best / 5.0 + .5, 0, 1)
        if m.max() <= 0:
            return
        near = np.exp(-np.clip(best, 0, None) / 38.0)           # 1 at the front, fades inward
        if k >= 0.9:
            near = np.maximum(near, 0.30 + 0.35 * n1)          # full Bloom: body stays plum-lit, not black
        body = PAL['PLUM_BODY']
        mid = PAL['PLUM_MID']
        col = body[None, None] * (1 - near[..., None] * .8) + mid[None, None] * (near[..., None] * .8)
        veins = np.clip((1 - np.abs(2 * n2 - 1) - .94) * 24, 0, 1) * np.clip(near * 1.4, 0, 1) * (m > .5)
        a = m * k * (.78 if k < .9 else .70)
        h_lo = np.stack([self.img[::2, ::2, c] for c in range(3)], -1) if False else None
        # build full-res alpha / colour by bilinear upsample
        up = lambda z: np.asarray(Image.fromarray(z.astype(np.float32)).resize((W, H), Image.BILINEAR), np.float32)
        a_f = up(a)
        colf = np.stack([up(col[..., c]) for c in range(3)], -1)
        self.img[:] = self.img * (1 - a_f[..., None]) + colf * a_f[..., None]
        if dim_lights > 0:
            self.img -= self.A['emis'] * (up(m) * dim_lights)[..., None] * .85
            np.clip(self.img, 0, None, out=self.img)
        vf = up(veins) * k
        self.img += PAL["VEIN"][None, None] * (vf * .5)[..., None]
        if hair:
            edge = np.exp(-(best / 2.2) ** 2) * (best > -4)
            hf = up(edge) * (0.22 * k + step_pulse * .75)
            self.img += PAL['HAIR'][None, None] * (hf[..., None]) * .9
            self.gl += np.asarray(Image.fromarray(hf.astype(np.float32)).resize((W // 4, H // 4), Image.BILINEAR), np.float32)[..., None] * PAL['VEIN'] * .6

    # ---- finish: glow composite
    def resolve(self, glow_gain=1.45):
        g = self.gl
        out = np.zeros_like(g)
        for s, wt in ((1.0, .55), (3.0, .38), (8.0, .30)):
            out += ndi.gaussian_filter(g, (s, s, 0), mode='nearest') * wt
        up = np.stack([np.asarray(Image.fromarray(out[..., c]).resize((W, H), Image.BILINEAR), np.float32) for c in range(3)], -1)
        img = (self.img + up * glow_gain) * 1.06
        # soft shoulder
        img = np.where(img > .85, .85 + .15 * (1 - np.exp(-(img - .85) / .15)), img)
        return np.clip(img, 0, 1)


# ------------------------------------------------------------------ ribbons
def ribbon(fr, R, s0, s1, gain=1.0, flow=0.0, alpha=1.0, ghost=True, gk=1.7, gain_fn=None, ghost_gain=0.8, dash=3.0):
    rb = R.ribbon_map()
    s = rb['s']
    sel = (s >= s0) & (s <= s1)
    if not sel.any():
        return
    iy, ix, u, off = rb['iy'][sel], rb['ix'][sel], rb['u'][sel], rb['off'][sel]
    ss = s[sel]
    hw = rb['hw']
    tx = ribbon_tex(R.typ)
    th, tw = tx.shape[:2]
    uu = ((u - flow) % LENU[R.typ]) / LENU[R.typ] * tw
    vv = (np.clip(off, -hw, hw) + hw) / (2 * hw) * (th - 1)
    samp = np.zeros((len(uu), 4), np.float32)
    for c in range(4):
        pad = np.concatenate([tx[..., c], tx[:, :2, c]], axis=1)
        samp[:, c] = ndi.map_coordinates(pad, [vv, uu], order=1, mode='nearest')
    inside = np.clip((hw - np.abs(off)) * 3.6 + .5, 0, 1)
    casing = np.clip((hw + rb['cas'] - np.abs(off)) * 3.6 + .5, 0, 1) * .92
    g = gain if gain_fn is None else gain_fn(ss)
    g = np.broadcast_to(np.asarray(g, np.float32), ss.shape)
    tex_a = samp[:, 3] * inside
    ink = PAL['INK']
    a_t = tex_a
    # ink casing under, texture over
    rgb_c = np.broadcast_to(ink, (len(ss), 3))
    cas_a = casing * alpha * np.minimum(g, 1.0) ** .8
    col = rgb_c * (1 - a_t[:, None]) + samp[:, :3] * a_t[:, None]
    a_tot = np.maximum(cas_a, a_t * alpha * np.minimum(g, 1.2))
    a_tot = np.clip(a_tot, 0, 1)
    colg = col * np.clip(g, 0, 1.6)[:, None] ** .6
    core = np.clip(1 - np.abs(off) / (hw * .30), 0, 1) * np.clip(g - .55, 0, 1) * 0.55 * (a_t > .5)
    colg = colg * (1 - core[:, None]) + (PAL['WHITE'] * .85 + PAL[R.typ] * .15)[None] * core[:, None]
    gha = None
    gh_rgb = None
    if ghost:
        pat = (0.55 + 0.45 * (np.sin(u / dash * 2 * math.pi) > 0)) * (np.abs(off) < hw * .62)
        gh_rgb = np.broadcast_to(PAL[R.typ] * 0.9 + .1, (len(ss), 3))
        gha = pat * alpha * ghost_gain * np.minimum(g, 1.0)
        # corridor of the city under the beam darkens 22 % (occluded part only)
        fr.darken_corridor(iy, ix, 0.22 * np.minimum(g, 1.0) * (np.abs(off) < hw + 1.0))
    fr.sparse(iy, ix, colg * 1.0, a_tot, gh_rgb, gha, gk=gk, gw=np.clip(g, 0, 1.8))


# ------------------------------------------------------------------ heads
def head(fr, typ, pos, ang, alpha=1.0, scale=1.0, halo=0.0, ghost=0.5):
    """pre-rendered rotation set (every 22.5 deg), blended between the two nearest; occluded part drawn as a ghost."""
    A = fr.A
    a = (ang % 360) / 22.5
    k0 = int(math.floor(a)) % 16
    k1 = (k0 + 1) % 16
    t = a - math.floor(a)
    sp = A['heads'][(typ, k0)] * (1 - t) + A['heads'][(typ, k1)] * t
    if scale != 1.0:
        im = Image.fromarray((np.clip(sp, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
        n = max(4, int(round(sp.shape[0] * scale)))
        sp = np.asarray(im.resize((n, n), Image.LANCZOS), np.float32) / 255
    h, w = sp.shape[:2]
    fx, fy = pos[0] - w / 2.0, pos[1] - h / 2.0
    x0, y0 = int(math.floor(fx)), int(math.floor(fy))
    dx, dy = fx - x0, fy - y0
    sp = ndi.shift(sp, (dy, dx, 0), order=1, mode='constant')
    rgb, al = sp[..., :3], sp[..., 3] * alpha
    if halo > 0:
        big = ndi.maximum_filter(al, size=int(halo * 2 + 1))
        big = ndi.gaussian_filter(big, .8)
        fr.over(np.broadcast_to(PAL['INK'], rgb.shape), np.clip(big * .95, 0, 1), x0, y0, gk=0, occ=0.0)
    cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    o = A['occ'][cy0:cy1, cx0:cx1]
    rg = rgb[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    aa = al[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    vis = aa * (1 - o * .92 * (0 if halo > 0 else 1))
    gh = aa * o * ghost * (0 if halo > 0 else 1)
    sub = fr.img[cy0:cy1, cx0:cx1]
    sub[:] = sub * (1 - vis[..., None]) + rg * vis[..., None]
    sub[:] = sub * (1 - gh[..., None]) + (rg * .8 + .2) * gh[..., None]
    fr.glow_add(PAL[typ][None, None] * ((vis + gh) * .6)[..., None], cx0, cy0)
    if alpha > .05 and halo == 0:
        glow_disc(fr, (pos[0], pos[1] + 6), 5.5 * scale, PAL[typ], .38 * alpha, gk=0.0, power=1.8)


# ------------------------------------------------------------------ ground marks
def glow_disc(fr, c, r_bu, col, k, z=0.0, gk=0.0, power=1.6):
    rx, ry = r_bu * KX, r_bu * KY
    x0, x1 = int(c[0] - rx - 2), int(c[0] + rx + 3)
    y0, y1 = int(c[1] - ry - KZ * z - 2), int(c[1] + ry + 3)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, W), min(y1, H)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xx - c[0]) / rx) ** 2 + ((yy - (c[1] - KZ * z)) / ry) ** 2)
    g = np.clip(1 - d, 0, 1) ** power
    fr.add(np.asarray(col, np.float32)[None, None] * np.ones((y1 - y0, x1 - x0, 1), np.float32), g, x0, y0, gk=gk, k=k)


def tier_ring(fr, sid, tier, k=1.0, frac=1.0, pulse=0.0, c=None, rscale=1.0, hatch_phase=0.0):
    cB, _ = site(sid)
    c = cB if c is None else c
    ro = TIER_R[tier] * rscale
    ri = ro - 2.8
    col = PAL[tier]
    pts = lambda r, a0=0.0, a1=2 * math.pi: ell(c, r, 80, a0=a0, a1=a1)
    box = bbox_pts(pts(ro + 3.0), 10)
    glow_disc(fr, c, ro, col, .22 * k, gk=0.2)
    P = Pl(box)
    if tier == 'SITES_LOST':
        P.poly(pts(ro + 1.3), PAL['INK'], .96)
        P.poly(pts(ro + .85), PAL['WHITE'], 1.0)
        P.poly(pts(ro + .40), PAL['INK'], 1.0)
        P.poly(pts(ri - 1.3 + 1.3), PAL['INK'], 1.0)
        P.poly(pts(ri), PAL['WHITE'], 1.0)
        P.poly(pts(ri - .45), PAL['INK'], 1.0)
        P.clear_poly(pts(ri - 1.6))
        # bold ochre diagonal hatch in the band
        rm0, rm1 = ri + .1, ro + .25
        for i in range(0, 120):
            ang = i * (2 * math.pi / 120)
            p0 = gs(c, rm0 * math.cos(ang), rm0 * math.sin(ang))
            ang2 = ang + 0.075
            p1 = gs(c, rm1 * math.cos(ang2), rm1 * math.sin(ang2))
            P.line([p0, p1], col, 2.6)
    else:
        P.poly(pts(ro + 1.3), PAL['INK'], .92)
        P.poly(pts(ro), col, 1.0)
        P.poly(pts(ri + .45), PAL['WHITE'], 1.0)
        P.poly(pts(ri), PAL['INK'], 1.0 if False else .92)
        P.clear_poly(pts(ri - 1.3))
        # pattern (a non-hue cue) in the band
        rm = (ri + ro) / 2 + .2
        if tier == 'HOLDS':
            for i in range(28):
                ang = i * 2 * math.pi / 28
                P.line([gs(c, (rm - 1.0) * math.cos(ang), (rm - 1.0) * math.sin(ang)), gs(c, (rm + 1.0) * math.cos(ang), (rm + 1.0) * math.sin(ang))], PAL['INK'], 2.2, .9)
        elif tier == 'UNTOUCHED':
            for i in range(36):
                ang = i * 2 * math.pi / 36
                p = gs(c, rm * math.cos(ang), rm * math.sin(ang))
                P.circle(p, 2.0, PAL['INK'], .75)
        elif tier == 'DAMAGED':
            for i in range(18):
                ang = i * 2 * math.pi / 18
                pp = [gs(c, (rm - .7) * math.cos(ang - .05), (rm - .7) * math.sin(ang - .05)), gs(c, (rm + .1) * math.cos(ang + .03), (rm + .1) * math.sin(ang + .03)),
                      gs(c, (rm - .7) * math.cos(ang + .11), (rm - .7) * math.sin(ang + .11))]
                P.line(pp, PAL['INK'], 2.2, .9)
        elif tier == 'BREACHED':
            for i in range(40):
                ang = i * 2 * math.pi / 40
                P.line([gs(c, (rm - 1.2) * math.cos(ang), (rm - 1.2) * math.sin(ang)), gs(c, (rm + 1.2) * math.cos(ang + .16), (rm + 1.2) * math.sin(ang + .16))], PAL['INK'], 1.6, .85)
    if frac < 0.999:
        # draining: erase the part of the band that has drained away (clockwise from the top)
        a_end = -math.pi / 2 + 2 * math.pi * frac
        wedge = [gs(c, 0, 0)] + [gs(c, (ro + 2.5) * math.cos(a), (ro + 2.5) * math.sin(a)) for a in np.linspace(a_end, -math.pi / 2 + 2 * math.pi, 40)]
        P.clear_poly(wedge)
    fr.pl(P, gk=0.35 + pulse, occ=0.8, k=k)


def stop_block(fr, R, s, tier, k=1.0, t=0.0, pulse_hz=1.2, motion=True, wide=1.0):
    p = R.pos(s)
    ta = R.ab_tan(s)
    na = np.array([-ta[1], ta[0]])
    L_, T_ = 13.5 * .5 * wide, 10.0 * .5
    ch = 1.6
    def quad(l, tt, cut):
        pts = [(-l, -tt + cut), (-l + cut, -tt), (l - cut, -tt), (l, -tt + cut), (l, tt - cut), (l - cut, tt), (-l + cut, tt), (-l, tt - cut)]
        return [gs(p, na[0] * x + ta[0] * y, na[1] * x + ta[1] * y) for x, y in pts]
    col = PAL[tier]
    box = bbox_pts(quad(L_ + 3, T_ + 3, ch), 8)
    P = Pl(box)
    if tier == 'SITES_LOST':
        P.poly(quad(L_ + .35 + 1.2, T_ + .35 + 1.2, ch), PAL['INK'])
        P.poly(quad(L_ + .35, T_ + .35, ch), PAL['WHITE'])
        P.poly(quad(L_, T_, ch), PAL['INK'])
    else:
        P.poly(quad(L_ + 1.2 + .35, T_ + 1.2 + .35, ch), PAL['INK'], .95)
        P.poly(quad(L_ + .35, T_ + .35, ch), PAL['WHITE'])
        P.poly(quad(L_, T_, ch), col)
    def at(x, y, z=0.0):
        return gs(p, na[0] * x + ta[0] * y, na[1] * x + ta[1] * y, z)
    if tier == 'HOLDS':
        ph = 0.5 + 0.5 * math.sin(2 * math.pi * pulse_hz * t / 30.0) if motion else 1.0
        for i, x in enumerate((-3.6, 0.0, 3.6)):
            P.poly([at(x - .9, -3.4), at(x + .9, -3.4), at(x + .9, 3.4), at(x - .9, 3.4)], PAL['INK'], .55 + .4 * ph)
    elif tier == 'UNTOUCHED':
        for x in np.linspace(-L_ + 2.2, L_ - 2.2, 7):
            P.circle(at(x, 0), 2.2, PAL['INK'], .85)
    elif tier == 'SITES_LOST':
        for i in range(-12, 12):
            x = i * 1.2
            P.line([at(x, -T_ + .4), at(x + T_ * 1.0, T_ - .4)], col, 2.8)
    elif tier == 'BREACHED':
        for i in range(-10, 11):
            P.line([at(i * 1.4, -T_ + .5), at(i * 1.4 + 3, T_ - .5)], PAL['INK'], 1.8, .85)
            P.line([at(i * 1.4, T_ - .5), at(i * 1.4 + 3, -T_ + .5)], PAL['INK'], 1.8, .85)
    elif tier == 'DAMAGED':
        for x in np.linspace(-L_ + 2.5, L_ - 2.5, 5):
            P.line([at(x - .7, -1.4), at(x + .7, 0), at(x - .7, 1.4)], PAL['INK'], 2.6, .9)
    fr.pl(P, gk=0.4, occ=0.8, k=k)


def hex_pts(c, r, z=0.0, a0=0.0):
    return [gs(c, r * math.cos(a0 + math.radians(60 * i)), r * math.sin(a0 + math.radians(60 * i)), z) for i in range(6)]


def home_marks(fr, hp=44, hpmax=50, preview=0, hit=0, hit_t=0.0, ring_k=1.0, crack=0.0, pool_k=1.0, pulse=0.0, seed=3, hit_col='DAMAGED', scar=0):
    c = home_c()
    glow_disc(fr, c, 20.0, PAL['WARM'], .85 * pool_k, gk=0.6 * pool_k, power=1.3)
    # ring r22 BU, width 2.2: white core, ink under-stroke
    ro, ri = 22.0 + 1.1, 22.0 - 1.1
    box = bbox_pts(ell(c, ro + 22), 10)
    P = Pl(box)
    P.poly(ell(c, ro + .9), PAL['INK'], .9)
    P.poly(ell(c, ro), PAL['WARM'], 1.0)
    P.poly(ell(c, ro - .5), PAL['WHITE'], 1.0)
    P.poly(ell(c, ri), PAL['INK'], .9)
    P.clear_poly(ell(c, ri - .9))
    if crack > 0:
        # cracked ring (aftermath): dark gaps along the ring
        rng = np.random.RandomState(4)
        for i in range(5):
            ang = rng.uniform(0, 2 * math.pi)
            for dr in (-1.0, 1.0):
                pass
            gp = [gs(c, (ro + 1.5) * math.cos(ang), (ro + 1.5) * math.sin(ang)), gs(c, (ri - 1.5) * math.cos(ang + .02), (ri - 1.5) * math.sin(ang + .02))]
            P.line(gp, PAL['INK'], 4.0 * crack)
    fr.pl(P, gk=1.7 * ring_k, occ=0.6, k=ring_k)
    # tick gauge: 50 radial ticks at r19
    P2 = Pl(box)
    flying = []
    rng = np.random.RandomState(seed)
    for i in range(hpmax):
        ang = math.radians(-90 + 360 * i / hpmax)
        major = (i % 10 == 0)
        ln = 4.2 if major else 3.2
        r0, r1 = 19.0 - ln / 2, 19.0 + ln / 2
        wd = 0.5
        if i < hp:
            col, al = PAL['WARM'], 1.0
        elif i < hp + hit:
            flying.append((i, ang, ln))
            continue
        elif i < hp + hit + preview:
            col, al = PAL['DAMAGED'], 0.0
        else:
            col, al = PAL['DEAD'], 1.0
        ca, sa = math.cos(ang), math.sin(ang)
        quad = [(r0 * ca - wd * sa, r0 * sa + wd * ca), (r0 * ca + wd * sa, r0 * sa - wd * ca), (r1 * ca + wd * sa, r1 * sa - wd * ca), (r1 * ca - wd * sa, r1 * sa + wd * ca)]
        qs = [gs(c, x, y) for x, y in quad]
        if i < hp + hit + preview and i >= hp + hit:
            P2.line(qs + [qs[0]], PAL['DAMAGED'], 2.0)
            P2.poly(qs, PAL['INK'], .5)
        else:
            P2.poly(qs, col, al)
    fr.pl(P2, gk=0.5, occ=0.5)
    # flying ticks (hit): thrown out and up, tumbling
    if flying:
        P3 = Pl(bbox_pts(ell(c, 70), 40))
        for j, (i, ang, ln) in enumerate(flying):
            r_ = np.random.RandomState(seed * 31 + i)
            dist = r_.uniform(10, 34) * hit_t ** .6
            up = r_.uniform(14, 38) * math.sin(math.pi * min(hit_t, 1) * .9)
            spin = r_.uniform(-3, 3) * hit_t
            cc = 19.0 + dist
            px, py = cc * math.cos(ang), cc * math.sin(ang)
            la = ang + spin
            ca, sa = math.cos(la), math.sin(la)
            pts = [(-ln / 2, -.6), (ln / 2, -.6), (ln / 2, .6), (-ln / 2, .6)]
            qs = [gs(c, px + x * ca - y * sa, py + x * sa + y * ca, up) for x, y in pts]
            P3.poly(qs, PAL[hit_col] if hit_t > .02 else PAL['WARM'], clamp01(1.4 - hit_t * .8))
        fr.pl(P3, gk=1.0)
    # hex deck: hex prism r8, 9 BU high, white rims, spine
    P4 = Pl(bbox_pts(hex_pts(c, 10, z=26), 16))
    r = 8.0
    base = hex_pts(c, r, 0)
    topp = hex_pts(c, r, 9.0)
    for i in range(6):
        j = (i + 1) % 6
        nb = (math.sin(math.radians(60 * i + 30)) + 0) # facing +b (down-screen) visible
        if math.sin(math.radians(60 * i + 30)) > -0.05:
            q = [base[i], base[j], topp[j], topp[i]]
            sh = .35 + .35 * math.cos(math.radians(60 * i + 30)) ** 2
            P4.poly(q, PAL['SLATE'] * sh + .12, 1.0)
            P4.line(q + [q[0]], PAL['WARM'], 1.3)
    P4.poly(topp, PAL['WARM'] * .55 + .12, 1.0)
    P4.line(topp + [topp[0]], PAL['WHITE'], 1.8)
    spine = [gs(c, 0, 0, 9.0), gs(c, 0, 0, 22.0)]
    P4.line(spine, PAL['WHITE'], 2.2)
    fr.pl(P4, gk=2.4 * ring_k, occ=0.0)
    if pulse > 0:
        fr.add(PAL['WARM'][None, None], np.ones((1, 1), np.float32) * 0, 0, 0, gk=0)


def tower(fr, sid, rank='hero', k=1.0, state='healthy', hs=1.0, tint=None, wire_k=1.0):
    cB, tier = site(sid)
    hh = TOWER_H[tier] * hs
    a = TOWER_A[tier]
    hero = rank == 'hero'
    col = PAL['SLATE'] * .62 if hero else PAL['QUIET']
    if tint is not None:
        col = tint
    base = [(-a, -a), (a, -a), (a, a), (-a, a)]          # world gx,gz corners
    def ab(x, z):
        return ((x - z) / math.sqrt(2), (x + z) / math.sqrt(2))
    B = [ab(x, z) for x, z in base]
    P = Pl(bbox_pts([gs(cB, p[0], p[1], hh + 6) for p in B] + [gs(cB, p[0], p[1], -2) for p in B], 14))
    bs = [gs(cB, p[0], p[1], 0) for p in B]
    ts = [gs(cB, p[0], p[1], hh) for p in B]
    # faces visible: +gx (corner 1-2) and +gz (2-3)
    gl_a = (.22 if hero else .15) * k
    for (i, j, sh) in ((1, 2, 1.0), (2, 3, .75)):
        q = [bs[i], bs[j], ts[j], ts[i]]
        P.poly(q, col * sh * .8 + np.array([.02, .03, .10]), gl_a + .10)
        if hero:
            for zz in np.arange(3, hh, 4.5):
                P.line([gs(cB, B[i][0], B[i][1], zz), gs(cB, B[j][0], B[j][1], zz)], col * 1.3 + .1, 1.0, .35)
    P.poly(ts, col * 1.1 + .1, (gl_a + .25) if hero else .14)
    if hero:
        wc = np.clip(PAL['SLATE'] * 1.25 + .28, 0, 1)
        wp = 2.0 * wire_k
        for i, j in ((1, 2), (2, 3)):
            P.line([bs[i], ts[i]], wc, wp, .95)
            P.line([bs[j], ts[j]], wc, wp, .95)
            P.line([bs[i], bs[j]], wc, wp, .8)
        P.line(ts + [ts[0]], wc, wp, .95)
        P.line([bs[1], bs[0]], wc, 1.0, .35)
        P.line([gs(cB, 0, 0, 0), gs(cB, 0, 0, hh)], PAL['WHITE'], 2.2, .9)
    fr.pl(P, gk=(.55 if hero else .0), occ=0.0, k=k)


def cage(fr, k=1.0, reveal=1.0):
    """Solace ICE cage at the HQ helix foot: mint-green wire cylinder at 60 % brightness."""
    c = np.array([1650.0, 470.0])
    r, h = 24.0, 92.0 * reveal
    P = Pl((c[0] - r * KX - 30, c[1] - KZ * 100 - r * KY - 20, c[0] + r * KX + 30, c[1] + r * KY + 30))
    col = PAL['CAGE'] * .9 + .03
    for z in np.linspace(0, h, 9):
        P.line(ell(c, r, 60, z=z), col, 1.4, .8)
    for i in range(18):
        ang = i * 2 * math.pi / 18
        if math.sin(ang) > -.2:
            P.line([gs(c, r * math.cos(ang), r * math.sin(ang), 0), gs(c, r * math.cos(ang), r * math.sin(ang), h)], col, 1.2, .7)
    fr.pl(P, gk=.7, k=k)


def glyph(P, kind, c, r, col, wpx=2.6):
    x, y = c
    if kind == 'UNTOUCHED':
        P.line([(x + r * .55 * math.cos(a), y + r * .55 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 24)], col, wpx)
    elif kind == 'HOLDS':
        sh = [(x, y - r * .7), (x + r * .6, y - r * .45), (x + r * .55, y + r * .15), (x, y + r * .7), (x - r * .55, y + r * .15), (x - r * .6, y - r * .45), (x, y - r * .7)]
        P.line(sh, col, wpx)
        P.line([(x - r * .28, y), (x - r * .05, y + r * .25), (x + r * .32, y - r * .22)], col, wpx)
    elif kind == 'SITES_LOST':
        P.line([(x - r * .35, y + r * .6), (x - r * .35, y - r * .5), (x + r * .35, y - r * .5), (x + r * .35, y + r * .6), (x - r * .35, y + r * .6)], col, wpx)
        P.poly([(x - r * .3, y), (x + r * .3, y), (x, y + r * .42)], col)
    elif kind == 'DAMAGED':
        pts = []
        for a in np.linspace(0, 2 * math.pi, 40):
            hx = 16 * math.sin(a) ** 3
            hy = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((x + hx * r * .035, y - hy * r * .035 - r * .08))
        P.poly(pts, col)
        P.line([(x + r * .05, y - r * .5), (x - r * .15, y - r * .1), (x + r * .12, y + r * .1), (x - r * .05, y + r * .5)], PAL['INK'], wpx * 1.1)
    elif kind == 'BREACHED':
        P.line([(x - r * .45, y - r * .45), (x + r * .45, y + r * .45)], col, wpx * 1.3)
        P.line([(x + r * .45, y - r * .45), (x - r * .45, y + r * .45)], col, wpx * 1.3)


def tag(fr, sid, tier, k=1.0, lift=52, scale=1.0, pips=3, state=None, num=None):
    """hex tile r30 floating above the tower top on a hairline leader."""
    cB, t_ = site(sid)
    hh = TOWER_H[t_]
    top = gs(cB, 0, 0, hh)
    c = (top[0], top[1] - lift * scale)
    r = 30 * scale
    P = Pl((c[0] - r - 40, c[1] - r - 8, c[0] + r + 70, top[1] + 8))
    hexp = [(c[0] + r * math.cos(math.radians(60 * i + 30)), c[1] + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    P.line([(c[0], c[1] + r * .9), (top[0], top[1])], PAL['WARM'], 1.2, .7)
    col = PAL[tier]
    if tier in ('DAMAGED', 'BREACHED'):
        P.poly(hexp, PAL['INK'])
        P.poly([(c[0] + (r - 2) * math.cos(math.radians(60 * i + 30)), c[1] + (r - 2) * math.sin(math.radians(60 * i + 30))) for i in range(6)], col)
        glyph(P, tier, c, r, PAL['INK'] if tier == 'DAMAGED' else PAL['WHITE'])
        if tier == 'BREACHED':
            P.line(hexp + [hexp[0]], PAL['WHITE'], 2.0)
    elif tier == 'SITES_LOST':
        P.poly(hexp, PAL['WHITE'])
        P.poly([(c[0] + (r - 2.2) * math.cos(math.radians(60 * i + 30)), c[1] + (r - 2.2) * math.sin(math.radians(60 * i + 30))) for i in range(6)], PAL['INK'])
        glyph(P, tier, c, r, PAL['SITES_LOST'])
    else:
        P.poly(hexp, PAL['INK'], .95)
        P.line(hexp + [hexp[0]], col, 3.2)
        glyph(P, tier, c, r, col)
    for i in range(pips):
        px = c[0] + r + 10 + i * 9
        P.circle((px, c[1] + r * .5), 3.2, PAL['WARM'] if tier != 'DAMAGED' else PAL['DAMAGED'])
    fr.pl(P, gk=.35, k=k)
    return c


# ------------------------------------------------------------------ bursts / bits
def hex_ripple(fr, c, r_px, col, k, w=3.0, z=0.0):
    """iso ring (ground ellipse) of width w px."""
    if k <= 0.01 or r_px < 2:
        return
    P = Pl((c[0] - r_px - 12, c[1] - r_px * .643 - 12 - KZ * z, c[0] + r_px + 12, c[1] + r_px * .643 + 12))
    rb = r_px / KX
    P.poly(ell(c, rb + w / KX / 2, 72, z=z), col, 1.0)
    P.clear_poly(ell(c, max(rb - w / KX / 2, .1), 72, z=z))
    fr.pl(P, gk=.9, k=k)


def bits(fr, c, col, n, t, seed=1, spread=60.0, size=3.0, up=26.0, k=1.0, shape='mix'):
    """thrown shards (hex / tri / rect) that fly out and fall: a non-hue cue."""
    if t <= 0 or k <= 0:
        return
    rng = np.random.RandomState(seed)
    P = Pl((c[0] - spread * 1.6 - 20, c[1] - spread - up * 2 - 20, c[0] + spread * 1.6 + 20, c[1] + spread * .9 + 30))
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(.3, 1.0) * spread * (1 - (1 - min(t, 1)) ** 2)
        hgt = rng.uniform(.4, 1) * up * math.sin(math.pi * min(t, 1) * .85)
        p = (c[0] + d * math.cos(ang) * 1.0, c[1] + d * math.sin(ang) * .643 - hgt)
        sz = size * rng.uniform(.7, 1.6)
        sp = rng.uniform(-4, 4) * t
        kind = i % 3
        if kind == 0:
            pts = [(p[0] + sz * math.cos(sp + math.radians(60 * j)), p[1] + sz * math.sin(sp + math.radians(60 * j))) for j in range(6)]
        elif kind == 1:
            pts = [(p[0] + sz * 1.3 * math.cos(sp + math.radians(120 * j)), p[1] + sz * 1.3 * math.sin(sp + math.radians(120 * j))) for j in range(3)]
        else:
            ca, sa = math.cos(sp), math.sin(sp)
            pts = [(p[0] + x * ca - y * sa, p[1] + x * sa + y * ca) for x, y in ((-sz * 1.4, -sz * .6), (sz * 1.4, -sz * .6), (sz * 1.4, sz * .6), (-sz * 1.4, sz * .6))]
        P.poly(pts, col if i % 4 else PAL['WHITE'], clamp01(1.5 - t))
    fr.pl(P, gk=.8, k=k)


def fracture_star(fr, c, r_px, col, k, n=14, seed=2, w=2.4):
    """non-hue cue: a fracture star of ink-cored lines radiating from the hit (ground plane)."""
    if k <= .01 or r_px < 2:
        return
    rng = np.random.RandomState(seed)
    P = Pl((c[0] - r_px - 10, c[1] - r_px * .64 - 10, c[0] + r_px + 10, c[1] + r_px * .64 + 10))
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-.12, .12)
        rr = r_px * rng.uniform(.55, 1.0)
        p0 = (c[0] + 8 * math.cos(ang), c[1] + 8 * math.sin(ang) * .643)
        mid = (c[0] + rr * .5 * math.cos(ang + .06), c[1] + rr * .5 * math.sin(ang + .06) * .643)
        p1 = (c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang) * .643)
        P.line([p0, mid, p1], PAL['INK'], w + 3.0, .9)
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-.12, .12)
        rr = r_px * rng.uniform(.55, 1.0)
        p0 = (c[0] + 8 * math.cos(ang), c[1] + 8 * math.sin(ang) * .643)
        mid = (c[0] + rr * .5 * math.cos(ang + .06), c[1] + rr * .5 * math.sin(ang + .06) * .643)
        p1 = (c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang) * .643)
        P.line([p0, mid, p1], col, w, 1.0)
    fr.pl(P, gk=.6, k=k)


def flash(fr, c, r_px, col, k):
    if k <= 0.01:
        return
    glow_disc(fr, c, r_px / KX, col, k, gk=0.0, power=1.2)


def column(fr, c, h_px, col, k, w=10):
    """vertical light column (rises from a hit point)."""
    if k <= 0.01:
        return
    x0, x1 = int(c[0] - w * 3), int(c[0] + w * 3)
    y0, y1 = int(max(c[1] - h_px, 0)), int(c[1] + 4)
    if y1 <= y0 or x1 <= x0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-((xx - c[0]) / w) ** 2) * np.clip((yy - y0) / max(h_px, 1), 0, 1) ** 1.5
    fr.add(np.asarray(col, np.float32)[None, None] * np.ones((y1 - y0, x1 - x0, 1), np.float32), g, x0, y0, gk=0.3, k=k)


# ------------------------------------------------------------------ camera
def camera(img, z=1.0, fx=960.0, fy=540.0, pan=(0.0, 0.0), par=(0.0, 0.0), zpar=0.0):
    """world (H,W,3) float -> (OH,OW,3). z = zoom about (fx,fy), pan in 1920 px (source moves by pan), par = parallax px at depth extreme.
    Near (low depth value) layers move more than far layers."""
    A = assets()
    xo = (np.arange(OW, dtype=np.float32) + .5) * (W / OW)
    yo = (np.arange(OH, dtype=np.float32) + .5) * (H / OH)
    XO, YO = np.meshgrid(xo, yo)
    d = A['dep_o'] - 0.5
    zz = z * (1 + zpar * -d)
    sx = fx + (XO - fx) / zz + pan[0] + par[0] * -d
    sy = fy + (YO - fy) / zz + pan[1] + par[1] * -d
    src = ndi.gaussian_filter(img, (0.55, 0.55, 0)) if z < 1.2 else img
    out = np.empty((OH, OW, 3), np.float32)
    for c in range(3):
        out[..., c] = ndi.map_coordinates(src[..., c], [sy, sx], order=1, mode='nearest')
    return out


def finish(img, f=0, scan=True, fringe=True, vig=0.30, grain=0.012):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    img = img * (1 - vig * np.clip(r - .45, 0, 1) ** 1.6)[..., None]
    if fringe:
        m = np.clip(r - .5, 0, 1)
        sh = np.roll(img[..., 0], 1, axis=1)
        img[..., 0] = img[..., 0] * (1 - m * .5) + sh * m * .5
        sh = np.roll(img[..., 2], -1, axis=1)
        img[..., 2] = img[..., 2] * (1 - m * .5) + sh * m * .5
    if scan:
        img = img * (1 - 0.04 * (np.arange(h) % 2 == 0))[:, None, None]
    if grain:
        rng = np.random.RandomState(1000 + f)
        img = img + (rng.rand(h, w, 1).astype(np.float32) - .5) * grain * 2
    return np.clip(img, 0, 1)


def u8(img):
    return (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)


# ------------------------------------------------------------------ textured quads (walls)
def _persp_coeffs(dst, src):
    """PIL PERSPECTIVE coefficients mapping output (dst) pixels back to source (src) pixels."""
    A = []
    B = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float))


_WT = {}


def wall_tex(typ):
    if typ not in _WT:
        _WT[typ] = Image.open(TEX + 'wall_%s.png' % typ).convert('RGBA')
    return _WT[typ]


def wall_quad(fr, p_ab_center, na, h_bu, w_bu, typ, k=1.0, tint=None, gk=0.4, bright=1.0):
    """vertical wall standing across the street: centre on the ground (screen px), lateral direction na (ab space), width w_bu, height h_bu."""
    l = w_bu / 2
    g0 = gs(p_ab_center, -na[0] * l, -na[1] * l, 0)
    g1 = gs(p_ab_center, na[0] * l, na[1] * l, 0)
    t0 = gs(p_ab_center, -na[0] * l, -na[1] * l, h_bu)
    t1 = gs(p_ab_center, na[0] * l, na[1] * l, h_bu)
    dst = [t0, t1, g1, g0]
    bx = bbox_pts(dst, 6)
    x0, y0 = int(bx[0]), int(bx[1])
    x1, y1 = int(bx[2]) + 1, int(bx[3]) + 1
    tex = wall_tex(typ)
    w0, h0 = tex.size
    src = [(0, 0), (w0, 0), (w0, h0), (0, h0)]
    co = _persp_coeffs([(p[0] - x0, p[1] - y0) for p in dst], src)
    im = tex.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(co), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255
    rgb = a[..., :3] * bright
    if tint is not None:
        rgb = rgb * .5 + np.asarray(tint, np.float32) * .5 * a[..., 3:4]
    fr.over(np.clip(rgb, 0, 1.5), a[..., 3], x0, y0, gk=gk, k=k)
    return dst
