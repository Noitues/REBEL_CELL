"""fxk_lib: drawing kit, base plates, frame composer and flash meter for the C / D / H / L effects on the locked final board.
All positions are screen px on the 1920x1080 plate. Board centre C = (536, 540); angle 0 = 12 o'clock, clockwise."""
import math, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/work/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
FONTS = 'D:/rc_art/art-pass/assets/fonts/'
C = (536.0, 540.0)
FPS = 60

# ---------------------------------------------------------------- palette (game marks from gramlib; family inks are new)
INK = (12, 10, 22)
PINK = (255, 61, 168)          # the Cell (player): D family
PINKD = (176, 30, 120)
HARM = (255, 68, 51)           # H family
HARMD = (120, 22, 16)
GAIN = (123, 224, 123)         # L family
MINT = (214, 255, 206)         # L strokes on a green REPAIR wedge
CYAN = (92, 225, 255)          # NET_CYAN (RAM)
GOLD = (255, 196, 40)          # boss only
WHITE = (255, 255, 255)
PAPER = (246, 242, 230)
STEEL = (150, 162, 182)
STEELHI = (226, 233, 246)
BED = (7, 9, 18)
# C family: the corp's own frame enamel (slab) + its edge colour, per skin
CORP_ENAMEL = {'neutral': ((188, 200, 214), (116, 128, 144)),
               'solace': ((226, 238, 216), (150, 236, 120)),
               'meridian': ((236, 214, 178), (224, 128, 40))}
RING = [(214, 271), (271, 328), (328, 385)]
TOWER = dict(r_in=71.0, r_out=177.0, half=26.0, icon_r=120.0, seat=37.0, pip_r=167.0, pip_w=8.0, page=192.0)

_fc = {}


def font(name, px):
    k = (name, px)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS + name, px)
    return _fc[k]


def anton(px): return font('Anton-Regular.ttf', px)
def mono(px): return font('ShareTechMono-Regular.ttf', px)
def plex(px): return font('IBMPlexSansCondensed-Medium.ttf', px)


# ---------------------------------------------------------------- maths
def ppx(r, a, c=C):
    t = math.radians(a)
    return (c[0] + r * math.sin(t), c[1] - r * math.cos(t))


def polar(x, y, c=C):
    dx, dy = x - c[0], y - c[1]
    return math.hypot(dx, dy), math.degrees(math.atan2(dx, -dy)) % 360


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def seg(t, a, b): return clamp((t - a) / float(b - a)) if b > a else float(t >= a)
def eout(t): return 1 - (1 - t) ** 3
def ein(t): return t ** 3
def eio(t): return 3 * t * t - 2 * t * t * t
def eback(t, s=1.70158): t = t - 1; return t * t * ((s + 1) * t + s) + 1      # overshoot out
def mixc(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
def A(c, a): return tuple(c[:3]) + (int(clamp(a) * 255),)


def arc_pts(r, a0, a1, n=None):
    n = n or max(6, int(abs(a1 - a0) / 1.5))
    return [ppx(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def band(r0, r1, a0, a1, n=None):
    return arc_pts(r1, a0, a1, n) + arc_pts(r0, a1, a0, n)


def wedge(s, r0=None, r1=None, half=None):
    r0 = TOWER['r_in'] if r0 is None else r0
    r1 = TOWER['r_out'] if r1 is None else r1
    h = TOWER['half'] if half is None else half
    return band(r0, r1, 60 * s - h, 60 * s + h)


def starburst(cx, cy, R, r, n, rot=0.0, jit=0.18, seed=1):
    rng = np.random.RandomState(seed)
    pts = []
    for i in range(2 * n):
        a = rot + math.pi * i / n
        rr = (R if i % 2 == 0 else r) * (1 + rng.uniform(-jit, jit))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def jag(p0, p1, n, amp, seed):
    rng = np.random.RandomState(seed)
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        t = i / n
        o = 0 if i in (0, n) else rng.uniform(-amp, amp)
        pts.append((x0 + dx * t + nx * o, y0 + dy * t + ny * o))
    return pts


def partial(pts, u):
    """the first fraction u of a polyline"""
    if u <= 0:
        return pts[:1]
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.dist(pts[i - 1], pts[i]))
    tgt = d[-1] * min(1.0, u)
    out = [pts[0]]
    for i in range(1, len(pts)):
        if d[i] <= tgt:
            out.append(pts[i])
        else:
            k = (tgt - d[i - 1]) / max(1e-6, d[i] - d[i - 1])
            out.append((lerp(pts[i - 1][0], pts[i][0], k), lerp(pts[i - 1][1], pts[i][1], k)))
            break
    return out


def bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


# ---------------------------------------------------------------- layer (supersampled, crop local)
class Lay:
    def __init__(self, box, ss=2):
        self.x0, self.y0, self.x1, self.y1 = box
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ss = ss
        self.im = Image.new('RGBA', (self.w * ss, self.h * ss), (0, 0, 0, 0))

    def P(self, pts):
        s = self.ss
        return [((x - self.x0) * s, (y - self.y0) * s) for x, y in pts]

    def new(self):
        return Image.new('RGBA', self.im.size, (0, 0, 0, 0))

    def comp(self, t, op=1.0):
        if op < 1.0:
            a = np.asarray(t).copy()
            a[:, :, 3] = (a[:, :, 3].astype(np.float32) * clamp(op)).astype(np.uint8)
            t = Image.fromarray(a, 'RGBA')
        self.im.alpha_composite(t)

    def poly(self, pts, fill=None, outline=None, w=0.0, op=1.0):
        if op <= 0 or len(pts) < 3:
            return
        t = self.new()
        d = ImageDraw.Draw(t)
        P = self.P(pts)
        if fill is not None:
            d.polygon(P, fill=A(fill, fill[3] / 255 if len(fill) > 3 else 1))
        if outline is not None and w > 0:
            self._line(d, P + [P[0]], outline, w)
        self.comp(t, op)

    def _line(self, d, P, col, w):
        ww = max(1, int(round(w * self.ss)))
        c = A(col, col[3] / 255 if len(col) > 3 else 1)
        d.line(P, fill=c, width=ww, joint='curve')
        r = ww / 2.0
        for x, y in (P[0], P[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)

    def line(self, pts, col, w, op=1.0, key=0.0, keycol=INK):
        if op <= 0 or len(pts) < 2:
            return
        t = self.new()
        d = ImageDraw.Draw(t)
        P = self.P(pts)
        if key > 0:
            self._line(d, P, keycol, w + 2 * key)
        self._line(d, P, col, w)
        self.comp(t, op)

    def lines(self, plist, col, w, op=1.0, key=0.0, keycol=INK):
        if op <= 0:
            return
        t = self.new()
        d = ImageDraw.Draw(t)
        if key > 0:
            for pts in plist:
                self._line(d, self.P(pts), keycol, w + 2 * key)
        for pts in plist:
            self._line(d, self.P(pts), col, w)
        self.comp(t, op)

    def polys(self, plist, fill, outline=None, w=0.0, op=1.0):
        if op <= 0:
            return
        t = self.new()
        d = ImageDraw.Draw(t)
        for pts in plist:
            P = self.P(pts)
            if outline is not None and w > 0:
                self._line(d, P + [P[0]], outline, w)
        for pts in plist:
            d.polygon(self.P(pts), fill=A(fill, fill[3] / 255 if len(fill) > 3 else 1))
        self.comp(t, op)

    def circle(self, cx, cy, r, fill=None, outline=None, w=0.0, op=1.0):
        if op <= 0 or r <= 0:
            return
        t = self.new()
        d = ImageDraw.Draw(t)
        s = self.ss
        x, y = (cx - self.x0) * s, (cy - self.y0) * s
        if outline is not None and w > 0:
            R = (r + w / 2) * s
            d.ellipse([x - R, y - R, x + R, y + R], fill=A(outline, 1))
            R = max(0.5, (r - w / 2)) * s
            if fill is not None:
                d.ellipse([x - R, y - R, x + R, y + R], fill=A(fill, fill[3] / 255 if len(fill) > 3 else 1))
            else:
                d.ellipse([x - R, y - R, x + R, y + R], fill=(0, 0, 0, 0))
        elif fill is not None:
            d.ellipse([x - r * s, y - r * s, x + r * s, y + r * s], fill=A(fill, fill[3] / 255 if len(fill) > 3 else 1))
        self.comp(t, op)

    def glow(self, fn, blur=6.0, op=0.5):
        """fn(lay) draws into a scratch Lay; it is blurred and laid in (the L family only)"""
        if op <= 0:
            return
        g = Lay((self.x0, self.y0, self.x1, self.y1), self.ss)
        fn(g)
        b = g.im.filter(ImageFilter.GaussianBlur(blur * self.ss))
        self.comp(b, op)

    def mask_op(self, m, col, op=1.0):
        """paint col through a float mask (H x W at the layer's supersampled size)"""
        if op <= 0:
            return
        a = np.zeros(self.im.size[::-1] + (4,), np.uint8)
        a[:, :, :3] = col[:3]
        a[:, :, 3] = (np.clip(m, 0, 1) * 255 * clamp(op)).astype(np.uint8)
        self.im.alpha_composite(Image.fromarray(a, 'RGBA'))

    def poly_mask(self, pts):
        m = Image.new('L', self.im.size, 0)
        ImageDraw.Draw(m).polygon(self.P(pts), fill=255)
        return np.asarray(m).astype(np.float32) / 255.0

    def text(self, xy, s, fnt, col, anchor='mm', op=1.0, stroke=0, stroke_col=INK):
        t = self.new()
        d = ImageDraw.Draw(t)
        f = ImageFont.truetype(fnt.path, int(fnt.size * self.ss))
        d.text(((xy[0] - self.x0) * self.ss, (xy[1] - self.y0) * self.ss), s, font=f, fill=A(col, 1), anchor=anchor,
               stroke_width=int(stroke * self.ss), stroke_fill=A(stroke_col, 1))
        self.comp(t, op)

    def erase_circle(self, cx, cy, r):
        m = Image.new('L', self.im.size, 255)
        s = self.ss
        x, y = (cx - self.x0) * s, (cy - self.y0) * s
        ImageDraw.Draw(m).ellipse([x - r * s, y - r * s, x + r * s, y + r * s], fill=0)
        a = np.asarray(self.im).copy()
        a[:, :, 3] = (a[:, :, 3].astype(np.float32) * np.asarray(m) / 255).astype(np.uint8)
        self.im = Image.fromarray(a, 'RGBA')

    def done(self):
        return self.im.reduce(self.ss) if self.ss > 1 else self.im


def grid_X(lay, region, dens_fn, pitch=7.0, col=HARM, key=True, w=1.6, op=1.0, misreg=(0, 0), seed=0):
    """X-only halftone: an X mark on a pitch grid, its size following dens_fn(x, y) in 0..1, clipped to region (screen polygon)"""
    if op <= 0:
        return
    xs = [p[0] for p in region]
    ys = [p[1] for p in region]
    m = Image.new('L', (lay.w, lay.h), 0)
    ImageDraw.Draw(m).polygon([(x - lay.x0, y - lay.y0) for x, y in region], fill=255)
    M = np.asarray(m)
    marks = []
    y = math.floor(min(ys) / pitch) * pitch
    row = 0
    while y <= max(ys):
        x = math.floor(min(xs) / pitch) * pitch + (pitch / 2 if row % 2 else 0)
        while x <= max(xs):
            ix, iy = int(x - lay.x0), int(y - lay.y0)
            if 0 <= ix < lay.w and 0 <= iy < lay.h and M[iy, ix] > 127:
                d = dens_fn(x, y)
                if d > 0.06:
                    s = pitch * 0.5 * min(1.0, d)
                    marks.append([(x - s, y - s), (x + s, y + s)])
                    marks.append([(x + s, y - s), (x - s, y + s)])
            x += pitch
        y += pitch
        row += 1
    if not marks:
        return
    if misreg != (0, 0):
        lay.lines([[(p[0] + misreg[0], p[1] + misreg[1]) for p in mk] for mk in marks], INK, w, op * 0.85)
    lay.lines(marks, col, w, op, key=0.9 if key else 0.0, keycol=HARMD)


# ---------------------------------------------------------------- bases
BASES = {}


def base_path(skin, var):
    if var == 'p1':
        return FINAL + ('p1_decide.png' if skin == 'neutral' else 'p1_decide_%s.png' % skin)
    return W + 'base_%s_%s.png' % (skin, var)


def base(skin, var):
    k = (skin, var)
    if k not in BASES:
        BASES[k] = np.asarray(Image.open(base_path(skin, var)).convert('RGB')).astype(np.float32)
    return BASES[k]


def poly_mask_full(pts, box, feather=1.5):
    x0, y0, x1, y1 = box
    m = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m).astype(np.float32) / 255.0


class Ctx:
    def __init__(self, fx, skin, reduce=False):
        self.fx, self.skin, self.reduce = fx, skin, reduce
        self.box = fx['box']


def frame(fx, skin, t, reduce=False, ss=2):
    """compose one frame: pre base -> post base through the state mask at state(t) -> the effect layer"""
    x0, y0, x1, y1 = box = fx['box']
    pre = base(skin, fx['pre'])[y0:y1, x0:x1]
    img = pre
    ctx = Ctx(fx, skin, reduce)
    if fx.get('post'):
        post = base(skin, fx['post'])[y0:y1, x0:x1]
        k = fx['state'](t, ctx)
        if k > 0:
            mk = ('_smask', skin)
            if mk not in fx:
                m = poly_mask_full(fx['state_region'], box, 1.2)
                diff = (np.abs(post - pre).max(axis=2) > 6).astype(np.float32)
                diff = np.asarray(Image.fromarray((diff * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
                fx[mk] = (m * diff)[:, :, None]
            M = fx[mk] * k
            img = pre * (1 - M) + post * M
    lay = Lay(box, ss)
    fx['draw'](lay, t, ctx)
    ov = np.asarray(lay.done()).astype(np.float32) / 255.0
    a = ov[:, :, 3:4]
    out = img * (1 - a) + ov[:, :, :3] * 255 * a
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGB')


# ---------------------------------------------------------------- flash meter
def rel_lum(rgb):
    c = rgb.astype(np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[:, :, 0] + 0.7152 * lin[:, :, 1] + 0.0722 * lin[:, :, 2]


def flash_check(frames_rgb, fps=FPS, swing=0.10, area=0.25, fp_thr=0.02):
    """frames_rgb: list of HxWx3 uint8 frames at fps (with the pre frame repeated before and the settled frame held after).
    Footprint = pixels whose relative luminance (WCAG, linear sRGB) moves by more than fp_thr at any time.
    Per pixel, the luminance path is cut into swings between local extremes (hysteresis = swing); a transition is a
    swing of >= 0.10 whose darker end is below 0.80. A flash = an opposing pair (up then down or down then up).
    Per frame we count the share of the footprint (and of the whole crop) completing a transition inside a 100 ms window;
    a flash event is when an up-wave and the opposing down-wave each cover more than 25 percent of the region.
    Also reported: the region-mean luminance series, its largest frame-to-frame step and its largest swing."""
    Y = np.stack([rel_lum(np.asarray(f)) for f in frames_rgb])          # T x H x W
    T = Y.shape[0]
    rng_ = Y.max(0) - Y.min(0)
    foot = rng_ > fp_thr
    nfoot = int(foot.sum())
    npx = Y.shape[1] * Y.shape[2]
    # per pixel transitions with hysteresis
    up = np.zeros((T,) + Y.shape[1:], bool)
    dn = np.zeros_like(up)
    ref = Y[0].copy()
    dirn = np.zeros(Y.shape[1:], np.int8)
    for t in range(1, T):
        y = Y[t]
        dark = np.minimum(y, ref) < 0.8
        r_ev = (y - ref >= swing) & dark & (dirn != 1)
        f_ev = (ref - y >= swing) & dark & (dirn != -1)
        up[t] = r_ev
        dn[t] = f_ev
        dirn = np.where(r_ev, 1, np.where(f_ev, -1, dirn)).astype(np.int8)
        ref = np.where(r_ev | f_ev, y, ref)
        ref = np.where((dirn == 1) & (y > ref), y, ref)
        ref = np.where((dirn == -1) & (y < ref), y, ref)
    win = max(1, int(round(0.1 * fps)))

    def wave(ev, denom):
        s = ev.reshape(T, -1).sum(1).astype(np.float64)
        c = np.convolve(s, np.ones(win), 'full')[:T]
        return c / max(1, denom)
    up_f, dn_f = wave(up & foot, nfoot), wave(dn & foot, nfoot)
    up_c, dn_c = wave(up, npx), wave(dn, npx)

    def events(u, d):
        # waves: the moments an up-wave or a down-wave first covers more than `area` of the region (alternating);
        # one flash = an opposing pair of waves, so flashes in a 1 s window = waves in the window // 2
        waves = []
        ev = []
        for t in range(T):
            if u[t] > area and (t == 0 or u[t - 1] <= area):
                ev.append((t, 'u'))
            if d[t] > area and (t == 0 or d[t - 1] <= area):
                ev.append((t, 'd'))
        for t, k in sorted(ev):
            if not waves or waves[-1][0] != k:
                waves.append((k, t))
        ts = [w[1] for w in waves]
        mx = 0
        for t in ts:
            mx = max(mx, sum(1 for s in ts if t <= s < t + fps) // 2)
        return ts, mx
    fl_f, mx_f = events(up_f, dn_f)
    fl_c, mx_c = events(up_c, dn_c)
    mean = (Y * foot).reshape(T, -1).sum(1) / max(1, nfoot)
    meanc = Y.reshape(T, -1).mean(1)
    return dict(frames=T, fps=fps, footprint_px=nfoot, crop_px=npx, footprint_share=round(nfoot / npx, 3),
                peak_up_share_footprint=round(float(up_f.max()), 3), peak_down_share_footprint=round(float(dn_f.max()), 3),
                waves_footprint=len(fl_f), flashes_footprint=len(fl_f) // 2, max_flashes_per_s_footprint=mx_f,
                peak_up_share_crop=round(float(up_c.max()), 3), peak_down_share_crop=round(float(dn_c.max()), 3),
                waves_crop=len(fl_c), flashes_crop=len(fl_c) // 2, max_flashes_per_s_crop=mx_c,
                mean_lum_footprint_range=[round(float(mean.min()), 3), round(float(mean.max()), 3)],
                mean_lum_max_step=round(float(np.abs(np.diff(mean)).max()) if T > 1 else 0.0, 3),
                mean_lum_crop_max_step=round(float(np.abs(np.diff(meanc)).max()) if T > 1 else 0.0, 3),
                mean_series_footprint=[round(float(v), 4) for v in mean],
                passes=bool(mx_f <= 3 and mx_c <= 3))
