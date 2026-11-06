"""fxlib: shared kit for the M / P / S / T effects on the final locked board.
Pixel work happens in a crop box of the 1920x1080 plate: polar remaps (rotate / radial shift) sample the base plates with
scipy map_coordinates; overlays are drawn at 3x on a crop-sized RGBA layer and downsampled."""
import math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

ME = 'D:/rc_scratch/combat_redesign/locked/fx_mpst/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
FD = 'D:/rc_scratch/combat_redesign/locked/corp/src/fonts/'
C = (536.0, 540.0)
W, H = 1920, 1080
RING = [(214, 271), (271, 328), (328, 385)]
TOWER_R = 196
BAND = (391, 417)
LANES = (436, 453, 470)
RIM = (489, 500)

# colours (game meanings; see NOTES)
PINK = (255, 61, 168)          # the Cell (player) at resolve
PINK_LT = (255, 150, 205)
YEL = (255, 226, 0)            # pencil plan (hover / preview only)
INK = (12, 10, 22)
BONE = (241, 234, 214)         # P plate stock
BONE_D = (196, 186, 160)
SILVER = (206, 212, 222)       # the clock (THIS TURN tape family)
SILVER_HI = (250, 252, 255)
SILVER_D = (118, 126, 140)
SOAK = (58, 126, 243)
HARM = (255, 68, 51)
HARM_UP = (255, 100, 82)
VIOLET = (160, 60, 255)        # Trace only
ENAMEL = (217, 225, 234)       # enemy outline enamel (every skin)
CORP_PRI = {'neutral': (217, 225, 234), 'solace': (150, 255, 70), 'meridian': (255, 140, 26)}
WHITE = (255, 255, 255)


def font(kind, px):
    f = {'anton': 'Anton-Regular.ttf', 'mono': 'ShareTechMono-Regular.ttf', 'plex': 'IBMPlexSansCondensed-Medium.ttf'}[kind]
    return ImageFont.truetype(FD + f, int(px))


# ------------------------------------------------------------------ plates
_cache = {}


def plate(skin, kind):
    """float32 HxWx3 0..255.  kind: p1 p2 p3 p2b (published finals for neutral, renders for corp p2/p3) or a base_ render."""
    key = (skin, kind)
    if key in _cache:
        return _cache[key]
    pub = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p3': 'p3_resolve', 'p2b': 'p2b_hover'}
    sfx = '' if skin == 'neutral' else '_' + skin
    fp = None
    if kind in pub and os.path.exists(FINAL + pub[kind] + sfx + '.png'):
        fp = FINAL + pub[kind] + sfx + '.png'
    else:
        fp = ME + 'work/base_%s_%s.png' % (skin, kind)
    a = np.asarray(Image.open(fp).convert('RGB'), np.float32)
    _cache[key] = a
    return a


# ------------------------------------------------------------------ geometry
def ppx(r, ang, c=C):
    a = math.radians(ang)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


class Box:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = int(x0), int(y0), int(x1), int(y1)
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        yy, xx = np.mgrid[self.y0:self.y1, self.x0:self.x1].astype(np.float32)
        self.X, self.Y = xx, yy
        self.RHO = np.hypot(xx - C[0], yy - C[1])
        self.ANG = np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) % 360

    def crop(self, img):
        return img[self.y0:self.y1, self.x0:self.x1].copy()

    def loc(self, p):
        return (p[0] - self.x0, p[1] - self.y0)


def angdiff(a, b):
    """signed a - b in (-180, 180]"""
    return (a - b + 180.0) % 360.0 - 180.0


def in_sector(ang, a0, a1):
    """ang inside the clockwise span a0 -> a1 (degrees)"""
    span = (a1 - a0) % 360
    return ((ang - a0) % 360) <= span


def sample(img, xs, ys, order=1):
    """bilinear sample a full HxWx3 plate at float coords (crop-shaped arrays)"""
    out = np.empty(xs.shape + (img.shape[2],), np.float32)
    for c in range(img.shape[2]):
        out[..., c] = ndi.map_coordinates(img[..., c], [ys, xs], order=order, mode='nearest')
    return out


def polar_src(box, rho, ang):
    a = np.radians(ang)
    return C[0] + rho * np.sin(a), C[1] - rho * np.cos(a)


def rotated(img, box, d):
    """the plate turned clockwise by d degrees about C, sampled in the box"""
    xs, ys = polar_src(box, box.RHO, box.ANG - d)
    return sample(img, xs, ys)


def shifted(img, box, dr):
    """the plate pushed outward by dr px (dr < 0 = inward) along the radius"""
    xs, ys = polar_src(box, np.maximum(box.RHO - dr, 0), box.ANG)
    return sample(img, xs, ys)


def ring_mask(box, r0, r1, a0=None, a1=None, feather=1.0):
    m = np.clip((box.RHO - r0) / feather + 0.5, 0, 1) * np.clip((r1 - box.RHO) / feather + 0.5, 0, 1)
    if a0 is not None:
        # feather the angular edges by ~1 px of arc
        arc = np.maximum(box.RHO, 1) * np.pi / 180
        da0 = ((box.ANG - a0 + 180) % 360 - 180) * arc
        da1 = ((a1 - box.ANG + 180) % 360 - 180) * arc
        m = m * np.clip(da0 / feather + 0.5, 0, 1) * np.clip(da1 / feather + 0.5, 0, 1)
    return m.astype(np.float32)


def mix(a, b, t):
    if np.ndim(t) == 2:
        t = t[..., None]
    return a + (b - a) * t


# ------------------------------------------------------------------ easing
def clamp01(x):
    return max(0.0, min(1.0, x))


def e_lin(t):
    return clamp01(t)


def e_out3(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def e_in2(t):
    t = clamp01(t)
    return t * t


def e_io3(t):
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def e_back(t, s=1.70158):
    t = clamp01(t) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def seg(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp01((t - t0) / (t1 - t0))


# ------------------------------------------------------------------ overlay layer (3x supersampled, crop coords given in screen px)
class Layer:
    def __init__(self, box, k=3):
        self.b, self.k = box, k
        self.im = Image.new('RGBA', (box.w * k, box.h * k), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [((x - self.b.x0) * self.k, (y - self.b.y0) * self.k) for x, y in pts]

    @staticmethod
    def c(col, a=255):
        col = tuple(int(v) for v in col)
        return col if len(col) == 4 else col + (int(a),)

    def line(self, pts, col, w, a=255):
        if len(pts) < 2:
            return
        self.d.line(self.P(pts), fill=self.c(col, a), width=max(1, int(round(w * self.k))), joint='curve')
        r = w * self.k / 2
        for (x, y) in (self.P(pts)[0], self.P(pts)[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=self.c(col, a))

    def poly(self, pts, fill=None, outline=None, w=1, a=255):
        self.d.polygon(self.P(pts), fill=None if fill is None else self.c(fill, a))
        if outline is not None:
            pp = self.P(pts)
            self.d.line(pp + [pp[0]], fill=self.c(outline, a), width=max(1, int(round(w * self.k))), joint='curve')

    def circle(self, p, r, fill=None, outline=None, w=1, a=255):
        x, y = self.P([p])[0]
        R = r * self.k
        self.d.ellipse([x - R, y - R, x + R, y + R], fill=None if fill is None else self.c(fill, a),
                       outline=None if outline is None else self.c(outline, a), width=max(1, int(round(w * self.k))))

    def done(self):
        im = self.im.resize((self.b.w, self.b.h), Image.LANCZOS)
        return np.asarray(im, np.float32)

    def paste_layer(self, other_rgba_np, alpha=1.0):
        pass


def over(base, rgba, alpha=1.0):
    """composite a crop-sized RGBA float array over an RGB float array"""
    a = rgba[..., 3:4] / 255.0 * alpha
    return base * (1 - a) + rgba[..., :3] * a


def arc_pts(r, a0, a1, step=1.5):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [ppx(r, a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]


def band_pts(r0, r1, a0, a1, step=1.5):
    return arc_pts(r1, a0, a1, step) + arc_pts(r0, a1, a0, step)


def shadow(rgba, off=(3, 5), k=0.55, blur=0.0):
    """hard offset drop shadow (P family: no glow).  returns RGBA float array"""
    a = rgba[..., 3]
    s = np.zeros_like(a)
    dx, dy = off
    h, w = a.shape
    s[max(0, dy):h - max(0, -dy) if dy < 0 else h, max(0, dx):w] = a[0:h - max(0, dy), 0:w - max(0, dx)]
    if blur:
        s = ndi.gaussian_filter(s, blur)
    out = np.zeros_like(rgba)
    out[..., :3] = np.array(INK, np.float32)
    out[..., 3] = s * k
    return out


# ------------------------------------------------------------------ the M family's arrowed outline (movement only): ink-cased wax stroke + open head
def arrow(L, pts, col, w=6.0, head=17.0, casing=4.5, a=255, hl=None):
    """pts: polyline in screen px.  open V head at the end; ink casing under everything (the board's movement-line form)."""
    if len(pts) < 2:
        return
    x1, y1 = pts[-1]
    j = max(0, len(pts) - 4)
    x0, y0 = pts[j]
    if math.hypot(x1 - x0, y1 - y0) < 1e-3:
        x0, y0 = pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    hp = []
    for s in (-1, 1):
        hp.append((x1 - head * math.cos(ang + s * 0.62), y1 - head * math.sin(ang + s * 0.62)))
    L.line(pts, INK, w + casing, a)
    L.line([hp[0], (x1, y1), hp[1]], INK, w + casing, a)
    L.line(pts, col, w, a)
    L.line([hp[0], (x1, y1), hp[1]], col, w, a)
    if hl is not None:
        L.line(pts, hl, max(1.0, w * 0.28), a)


def path_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def path_cut(pts, t):
    """the first fraction t of a polyline"""
    if t <= 0:
        return pts[:1]
    tot = path_len(pts)
    want = tot * min(1.0, t)
    out = [pts[0]]
    acc = 0.0
    for i in range(len(pts) - 1):
        seg_ = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        if acc + seg_ >= want:
            f = (want - acc) / max(seg_, 1e-6)
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            return out
        acc += seg_
        out.append(pts[i + 1])
    return out


def silver_arrow(L, pts, w=6.0, head=17.0, a=255):
    """the clock's arrow: silver foil (same stock as the THIS TURN tape), ink casing, a white specular core line"""
    arrow(L, pts, SILVER, w, head, 4.5, a, hl=SILVER_HI)
    # a darker foil edge on one side gives the metal read in grey
    if len(pts) >= 2:
        L.line(pts, SILVER_D, max(1.0, w * 0.22), int(a * 0.0))


# ------------------------------------------------------------------ luminance and the flash check
def rel_lum(rgb):
    c = np.asarray(rgb, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def flash_check(frames, fps=60, swing=0.10, area=0.25, win=6, foot_thr=0.02):
    """frames: list of crop RGB arrays at `fps`.
    footprint R = pixels whose relative luminance (WCAG, linear sRGB) moves > foot_thr from frame 0 at any time.
    per pixel: a swing event is logged when L moves >= `swing` (absolute relative luminance) away from the last extreme in the
    opposite direction (an extremum tracker, so slow ramps count once and jitter < swing never counts).
    region event: within any `win`-frame window (100 ms) >= `area` of R swung the same way.  flash = two opposite region
    events (up then down or down then up).  pass: no 1 s window holds more than 3 flashes.
    also: the per-frame mean luminance of R (curve) and its largest frame-to-frame step."""
    Ls = np.stack([rel_lum(f)[::2, ::2] for f in frames])          # 2x2 decimated: area fractions are unchanged
    T = Ls.shape[0]
    dev = np.abs(Ls - Ls[0:1]).max(0)
    R = dev > foot_thr
    nR = int(R.sum())
    if nR == 0:
        return dict(footprint_px=0, flashes=0, max_flashes_per_s=0, passed=True, mean_curve=[0.0] * T, max_area_swing=0.0)
    L = Ls[:, R]                                                   # T x N
    N = L.shape[1]
    ext = L[0].copy()
    mn, mx_ = L[0].copy(), L[0].copy()
    dirn = np.zeros(N, np.int8)                                    # +1 last swing up, -1 down, 0 none yet
    up = np.zeros(T, np.float32)
    dn = np.zeros(T, np.float32)
    ev_up = np.zeros((T, N), bool)
    ev_dn = np.zeros((T, N), bool)
    for t in range(1, T):
        v = L[t]
        z = dirn == 0
        mn = np.where(z, np.minimum(mn, v), mn)
        mx_ = np.where(z, np.maximum(mx_, v), mx_)
        u0 = z & (v - mn >= swing)
        d0 = z & ~u0 & (mx_ - v >= swing)
        pu = dirn == 1
        pd = dirn == -1
        ext = np.where(pu & (v > ext), v, ext)
        ext = np.where(pd & (v < ext), v, ext)
        d1 = pu & (ext - v >= swing)
        u1 = pd & (v - ext >= swing)
        u_ = u0 | u1
        d_ = d0 | d1
        ev_up[t], ev_dn[t] = u_, d_
        dirn = np.where(u_, 1, np.where(d_, -1, dirn)).astype(np.int8)
        ext = np.where(u_ | d_, v, ext)
    for t in range(T):
        lo = max(0, t - win + 1)
        up[t] = ev_up[lo:t + 1].any(0).mean()
        dn[t] = ev_dn[lo:t + 1].any(0).mean()
    # region events (rising edges of the area test), then pair opposite ones into flashes
    events = []
    for t in range(T):
        for sgn, arr in ((1, up), (-1, dn)):
            if arr[t] >= area and (t == 0 or arr[t - 1] < area):
                events.append((t, sgn))
    events.sort()
    flashes = []
    last = None
    for t, s in events:
        if last is not None and s != last[1]:
            flashes.append(t)
            last = None
        else:
            last = (t, s)
    mx = 0
    for t in flashes:
        mx = max(mx, sum(1 for u in flashes if t <= u < t + fps))
    mc = L.mean(1)
    return dict(footprint_px=nR * 4, frames=T, fps=fps, flashes=len(flashes), flash_frames=flashes, max_flashes_per_s=mx,
                passed=mx <= 3, max_area_swing_up=round(float(up.max()), 3), max_area_swing_down=round(float(dn.max()), 3),
                region_events=len(events), mean_curve=[round(float(x), 4) for x in mc],
                max_mean_step=round(float(np.abs(np.diff(mc)).max()) if T > 1 else 0.0, 4),
                mean_range=round(float(mc.max() - mc.min()), 4))


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
