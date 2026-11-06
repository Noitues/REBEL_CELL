"""mp_lib: shared kit for the M / P / S / T effects on the rebuilt board (2026-11-03 rebuild, stage 2, gate 1).
Every effect is drawn BETWEEN the board layer and the HUD-and-up layer of the generator's own split render (review 1.6, ART_BIBLE 6.4):
    frame = board (below)  ->  effect  ->  HUD, YOU strip, hand, UNDO, nameplate, SEND IT (above)
Only fx_trace_add (S) is drawn over the HUD and the hand (REVIEW_RESPONSE 1.6: hp_through, refund and trace_add may cross).
Pixel work happens in a crop box; polar remaps sample full-frame canvases with scipy map_coordinates; overlays are drawn at 3x."""
import math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
BASES = ME + 'work/bases/'
OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
FD = 'D:/rc_scratch/combat_redesign/locked/corp/src/fonts/'
C = (536.0, 540.0)
W, H = 1920, 1080
RING = [(214, 271), (271, 328), (328, 385)]
TOWER_R = 196
BAND = (391, 417)
LANES = (436, 453, 470)

# ------------------------------------------------------------------ tokens (VISUAL_PLAN E; rb_tokens) and the family stocks
PINK = (255, 61, 168)          # CELL_PINK: the Cell's card moves things at resolve (VISUAL_PLAN E "motion colour")
SCHED = (255, 140, 26)         # SCHEDULE: the clock moves the rings (rings step, Hold's slide), VISUAL_PLAN E
SCHED_HI = (255, 200, 140)     # the clock arrow's core line (a value step of SCHEDULE, no new hue)
GUN = (110, 117, 128)          # K clock gunmetal (#6E7580, VISUAL_PLAN A.4 2026-11-03)
GUN_LIP = (150, 158, 170)      # its engraved lip #969EAA
GUN_D = (38, 43, 51)           # #262B33 dial fill
YEL = (255, 226, 0)            # PLAN pencil (hover / preview only; never in resolve)
INK = (12, 10, 22)
PAPER = (242, 238, 228)
# FX-P stock (review 3.10): its own pink-tinted paper, not card bone #F1EAD6 / PAPER #F2EEE4.  ONE stock for the plate in every sheet:
# #F6C8DE with its edge shade #D696B8, the same values the C/D/H/L designer uses for the break shards (fxk_lib P_STOCK / P_STOCK_EDGE),
# so the block and the break show the same paper.  stock_de.py: Lab (85.1, 19.7, -4.7), L* 85.1, nearest K_TYPE dE76 20.4, HOT_CORE
# 20.8, ENAMEL 21.1 (floor 15, rb_tokens.DE_MIN).  pick_stock.py's best (#F7B3D6, min dE 30.9) was dropped to keep one stock.
P_STOCK = (246, 200, 222)
P_STOCK_D = (214, 150, 184)    # the stock's own shade (rivet heads, fibre, torn edge)
SOAK = (58, 126, 243)
HARM = (255, 68, 51)
HARM_UP = (255, 100, 82)
VIOLET = (160, 60, 255)        # TRACE_VIOLET: Trace only
ENAMEL = (217, 225, 234)       # enemy outline enamel
K_TYPE = (203, 210, 219)
HIT_PAPER = (222, 216, 202)
WHITE = (255, 255, 255)
# the enemy owns a wave entering: its cell-edge hue (DR-6 + ART_BIBLE 2.4 note: corp hue on the rim, lip, crest and CELL EDGES only)
CORP_EDGE = {'neutral': ENAMEL, 'solace': (150, 255, 70), 'meridian': (216, 138, 78)}


def font(kind, px):
    f = {'anton': 'Anton-Regular.ttf', 'mono': 'ShareTechMono-Regular.ttf', 'plex': 'IBMPlexSansCondensed-Medium.ttf'}[kind]
    return ImageFont.truetype(FD + f, int(px))


# ------------------------------------------------------------------ base plates (split)
_cache = {}


def below(skin, kind):
    k = ('b', skin, kind)
    if k not in _cache:
        _cache[k] = np.asarray(Image.open(BASES + '%s_%s_below.png' % (skin, kind)).convert('RGB'), np.float32)
    return _cache[k]


def above(skin, kind):
    k = ('a', skin, kind)
    if k not in _cache:
        _cache[k] = np.asarray(Image.open(BASES + '%s_%s_above.png' % (skin, kind)).convert('RGBA'), np.float32)
    return _cache[k]


def comp(bel, abv):
    """board crop (RGB float) + HUD-and-up crop (RGBA float) -> the frame crop"""
    a = abv[..., 3:4] / 255.0
    return bel * (1 - a) + abv[..., :3] * a


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

    def t(self):
        return (self.x0, self.y0, self.x1, self.y1)


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
FRHO = np.hypot(XX - C[0], YY - C[1])
FANG = np.degrees(np.arctan2(XX - C[0], -(YY - C[1]))) % 360


def sample(img, xs, ys, order=1):
    out = np.empty(xs.shape + (img.shape[2],), np.float32)
    for c in range(img.shape[2]):
        out[..., c] = ndi.map_coordinates(img[..., c], [ys, xs], order=order, mode='nearest')
    return out


def sample1(a, xs, ys):
    return ndi.map_coordinates(a, [ys, xs], order=1, mode='constant', cval=0.0).astype(np.float32)


def polar_src(rho, ang):
    a = np.radians(ang)
    return C[0] + rho * np.sin(a), C[1] - rho * np.cos(a)


def rotated(img, box, d):
    """the full-frame canvas turned clockwise by d degrees about C, sampled in the box"""
    xs, ys = polar_src(box.RHO, box.ANG - d)
    return sample(img, xs, ys)


def ring_mask(box, r0, r1, feather=1.0):
    m = np.clip((box.RHO - r0) / feather + 0.5, 0, 1) * np.clip((r1 - box.RHO) / feather + 0.5, 0, 1)
    return m.astype(np.float32)


def sector_region(r0, r1, a0, a1, pad_r=3.0, pad_a=0.6):
    m = ((FRHO > r0 - pad_r) & (FRHO < r1 + pad_r)).astype(np.float32)
    span = (a1 - a0 + 2 * pad_a) % 360
    inside = ((FANG - (a0 - pad_a)) % 360) <= span
    return m * inside


def mix(a, b, t):
    if np.ndim(t) == 2:
        t = t[..., None]
    return a + (b - a) * t


# ------------------------------------------------------------------ easing
def clamp01(x):
    return max(0.0, min(1.0, x))


def seg(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp01((t - t0) / (t1 - t0))


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


def speed_of(fn, t, scale):
    v = abs(fn(t + 8) - fn(t - 8)) / 16.0
    return clamp01(v / scale)


# ------------------------------------------------------------------ overlay layer (3x supersampled; coords in screen px)
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
        return col if len(col) == 4 else col + (int(max(0, min(255, a))),)

    def line(self, pts, col, w, a=255):
        if len(pts) < 2 or a <= 0:
            return
        self.d.line(self.P(pts), fill=self.c(col, a), width=max(1, int(round(w * self.k))), joint='curve')
        r = w * self.k / 2
        for (x, y) in (self.P(pts)[0], self.P(pts)[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=self.c(col, a))

    def poly(self, pts, fill=None, outline=None, w=1, a=255):
        if a <= 0:
            return
        self.d.polygon(self.P(pts), fill=None if fill is None else self.c(fill, a))
        if outline is not None:
            pp = self.P(pts)
            self.d.line(pp + [pp[0]], fill=self.c(outline, a), width=max(1, int(round(w * self.k))), joint='curve')

    def circle(self, p, r, fill=None, outline=None, w=1, a=255):
        if a <= 0:
            return
        x, y = self.P([p])[0]
        R = r * self.k
        self.d.ellipse([x - R, y - R, x + R, y + R], fill=None if fill is None else self.c(fill, a),
                       outline=None if outline is None else self.c(outline, a), width=max(1, int(round(w * self.k))))

    def done(self):
        im = self.im.resize((self.b.w, self.b.h), Image.LANCZOS)
        return np.asarray(im, np.float32)


def over(base, rgba, alpha=1.0):
    a = np.clip(rgba[..., 3:4] / 255.0 * alpha, 0, 1)
    return base * (1 - a) + np.clip(rgba[..., :3], 0, 255) * a


def arc_pts(r, a0, a1, step=1.5):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [ppx(r, a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]


def band_pts(r0, r1, a0, a1, step=1.5):
    return arc_pts(r1, a0, a1, step) + arc_pts(r0, a1, a0, step)


def shadow(rgba, off=(3, 5), k=0.55):
    """hard offset drop shadow (P family: no glow)"""
    a = rgba[..., 3]
    s = np.zeros_like(a)
    dx, dy = off
    h, w = a.shape
    s[dy:, dx:] = a[:h - dy, :w - dx]
    out = np.zeros_like(rgba)
    out[..., :3] = np.array(INK, np.float32)
    out[..., 3] = s * k
    return out


def path_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def path_cut(pts, t):
    if t <= 0:
        return pts[:1]
    tot = path_len(pts)
    want = tot * min(1.0, t)
    out = [pts[0]]
    acc = 0.0
    for i in range(len(pts) - 1):
        s_ = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        if acc + s_ >= want:
            f = (want - acc) / max(s_, 1e-6)
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            return out
        acc += s_
        out.append(pts[i + 1])
    return out


# ------------------------------------------------------------------ the M family's arrowed outline (movement only): ink-cased stroke + open head
def arrow(L, pts, col, w=5.0, head=15.0, casing=4.0, a=255, hl=None):
    if len(pts) < 2 or a <= 0:
        return
    x1, y1 = pts[-1]
    j = max(0, len(pts) - 4)
    x0, y0 = pts[j]
    if math.hypot(x1 - x0, y1 - y0) < 1e-3:
        x0, y0 = pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    hp = [(x1 - head * math.cos(ang + s * 0.62), y1 - head * math.sin(ang + s * 0.62)) for s in (-1, 1)]
    L.line(pts, INK, w + casing, a)
    L.line([hp[0], (x1, y1), hp[1]], INK, w + casing, a)
    L.line(pts, col, w, a)
    L.line([hp[0], (x1, y1), hp[1]], col, w, a)
    if hl is not None:
        L.line(pts, hl, max(1.0, w * 0.28), a)


def clock_arrow(L, pts, w=5.0, head=15.0, a=255):
    """the clock moves the rings: SCHEDULE orange (VISUAL_PLAN E), ink casing, a lighter core line (value step, same hue)"""
    arrow(L, pts, SCHED, w, head, 4.0, a, hl=SCHED_HI)


# ------------------------------------------------------------------ luminance, L*, the flash check and the loudness measure
def rel_lum(rgb):
    c = np.asarray(rgb, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar(Y):
    Y = np.asarray(Y, np.float32)
    return np.where(Y > 216 / 24389, 116 * np.cbrt(Y) - 16, Y * 24389 / 27)


def flash_check(frames, fps=60, swing=0.10, area=0.25, win=6, foot_thr=0.02):
    """the NOTES_MPST flash meter, unchanged: WCAG relative luminance (2x2 decimated); footprint = pixels moving > foot_thr from
    frame 0 at any time; per pixel an extremum tracker logs a swing event at >= `swing` away from the last extreme; a region event
    is >= `area` of the footprint swinging the same way within `win` frames (100 ms); a flash = two opposite region events;
    pass = no 1 s window holds more than 3 flashes."""
    Ls = np.stack([rel_lum(f)[::2, ::2] for f in frames])
    T = Ls.shape[0]
    dev = np.abs(Ls - Ls[0:1]).max(0)
    R = dev > foot_thr
    nR = int(R.sum())
    if nR == 0:
        return dict(footprint_px=0, frames=T, flashes=0, flash_frames=[], max_flashes_per_s=0, passed=True, mean_curve=[0.0] * T,
                    max_area_swing_up=0.0, max_area_swing_down=0.0, region_events=0, max_mean_step=0.0, mean_range=0.0)
    L = Ls[:, R]
    N = L.shape[1]
    ext = L[0].copy()
    mn, mx_ = L[0].copy(), L[0].copy()
    dirn = np.zeros(N, np.int8)
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
    up = np.zeros(T, np.float32)
    dn = np.zeros(T, np.float32)
    for t in range(T):
        lo = max(0, t - win + 1)
        up[t] = ev_up[lo:t + 1].any(0).mean()
        dn[t] = ev_dn[lo:t + 1].any(0).mean()
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


LOUD_DL = 5.0          # an effect pixel: L* at least this much above BOTH end states (and above the marks-off render)


def loudness(frames, ref_frames):
    """review 2.10: peak area x value of the light an effect ADDS.  frames: the effect's frames (crop RGB); ref_frames: for each frame,
    the per-pixel reference it is measured against (the brighter of the pre-state, the post-state and, for motion, the same frame
    with the effect's own marks off, so a moving cell is not counted as effect light).  Per frame: A = pixels whose L* is >= LOUD_DL
    over the reference, V = their mean L*; loudness = A x V / 100 (px at full value).  Returns the peak and its frame."""
    best = dict(av=0.0, area_px=0, mean_L=0.0, p95_L=0.0, frame=0)
    curve = []
    for i, (f, r) in enumerate(zip(frames, ref_frames)):
        Lf = lstar(rel_lum(f))
        Lr = lstar(rel_lum(r))
        m = (Lf - Lr) >= LOUD_DL
        n = int(m.sum())
        v = float(Lf[m].mean()) if n else 0.0
        av = n * v / 100.0
        curve.append(round(av, 1))
        if av > best['av']:
            best = dict(av=round(av, 1), area_px=n, mean_L=round(v, 1), p95_L=round(float(np.percentile(Lf[m], 95)), 1) if n else 0.0, frame=i)
    best['curve'] = curve
    return best


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
