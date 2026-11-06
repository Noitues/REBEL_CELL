"""fxk_lib: drawing kit, base layers, the split frame composer, the flash meter and the loudness meter for the C / D / H / L effects on the
rebuilt board (2026-11-03 rebuild as published in locked/final, gate 1).  All positions are screen px on the 1920x1080 plate.
Board centre C = (536, 540); angle 0 = 12 o'clock, clockwise.

Layer order (review 1.6, ART_BIBLE 6.4 "wheels -> FX world layer -> HUD -> stickers -> hand"): every effect draws into the UNDER layer, which
sits on the board (f1_render.SPLIT['below']) and under the HUD, YOU strip, hand, UNDO, nameplate and SEND IT (SPLIT['above']).  Only the
effects the review allows (hp_through, refund, trace_add) draw into the OVER layer, above the HUD."""
import math, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as RT                       # read-only: the rebuild's token table and its sRGB -> Lab / L* maths

W = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
FONTS = 'D:/rc_art/art-pass/assets/fonts/'
C = (536.0, 540.0)
FPS = 60
T2_CAP_MS = 600                # ART_BIBLE 5.3 VfxTier T2 outcome: max duration 0.6 s.  Every effect fits it; no per-effect override
T2_FLASH = 0.60                # T2: 60 % local flash at most
CROSS_OK = ('fx_hp_through', 'fx_refund', 'fx_trace_add')     # review 1.6: the only effects that may draw above the HUD

# ---------------------------------------------------------------- palette (game marks from rb_tokens; family inks are new)
INK = (12, 10, 22)
PINK = RT.TOKENS['CELL_PINK']  # the Cell (player): D family, and the cause colour of our kills (review 1.8)
PINKD = (176, 30, 120)
PINKCORE = (255, 190, 224)     # the light core of a pink hit frame: a tint of CELL_PINK
HARM = RT.TOKENS['HARM']       # H family
HARMD = (120, 22, 16)
GAIN = RT.TOKENS['GAIN']       # L family
MINT = (214, 255, 206)         # L strokes on a green REPAIR wedge
CYAN = RT.TOKENS['NET_CYAN']   # RAM
GOLD = RT.TOKENS['BOSS_GOLD']  # BOSS_GOLD #D69A1A (2026-11-03 re-pick; the old fx used #FFC428): the boss only
GOLD_HI = RT.BOSS_GOLD_HI
WHITE = (255, 255, 255)
HIT_PAPER = RT.HIT_PAPER       # #DED8CA (L* 86): the board's gun hit star and tracer highlight
PAPER = (246, 242, 230)
P_STOCK = (246, 200, 222)      # review 3.10: the FX-P plate's own stock, pink-tinted paper #F6C8DE (not the card bone PAPER #F2EEE4)
P_STOCK_EDGE = (214, 150, 184) # its torn-edge shade
STEEL = (150, 162, 182)
STEELHI = RT.STEEL_HI_E        # #C4CBD8 (gate 1)
ENAMEL = RT.NEUTRALS['ENAMEL']
BED = (7, 9, 18)
FOCUS = RT.TOKENS['FOCUS']     # never drawn by an effect
LIME = (150, 254, 70)          # the a_kit lime / Solace leaf: never drawn by an effect
# C family (VISUAL_PLAN G "FX-C: a clean vector scan-wipe, ENAMEL; BOSS_GOLD for the boss"): the scan line takes the skin's own enamel ink
# (DR-6: corp hue on the cell edges).  Solace uses its celadon (the leaf greens sit near GAIN and FOCUS), Meridian its rust highlight.
CORP_ENAMEL = {'neutral': (ENAMEL, (116, 128, 144)),
               'solace': (RT.SKIN_INKS['solace']['porcelain'], (80, 120, 104)),
               'meridian': (RT.SKIN_INKS['meridian']['rust_hi'], (120, 64, 30))}
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


# ---------------------------------------------------------------- bases: the split layers of the rebuilt board (base_render.py)
BASES = {}


def _load(skin, var, part):
    k = (skin, var, part)
    if k not in BASES:
        if part == 'below':
            BASES[k] = np.asarray(Image.open(W + 'base_%s_%s_below.png' % (skin, var)).convert('RGB')).astype(np.float32)
        else:
            BASES[k] = np.asarray(Image.open(W + 'base_%s_%s_above.png' % (skin, var)).convert('RGBA')).astype(np.float32)
    return BASES[k]


def below(skin, var):
    return _load(skin, var, 'below')


def above(skin, var):
    return _load(skin, var, 'above')


def base(skin, var):
    """the composited plate (below + above), as published"""
    k = (skin, var, 'full')
    if k not in BASES:
        b, a = below(skin, var), above(skin, var)
        al = a[:, :, 3:4] / 255.0
        BASES[k] = b * (1 - al) + a[:, :, :3] * al
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


def _smask(fx, skin, pre_b, post_b, pre_a, post_a):
    mk = ('_smask', skin)
    if mk not in fx:
        m = poly_mask_full(fx['state_region'], fx['box'], 1.2)
        d = np.maximum(np.abs(post_b - pre_b).max(axis=2), np.abs(post_a - pre_a).max(axis=2))
        diff = (d > 6).astype(np.float32)
        diff = np.asarray(Image.fromarray((diff * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
        fx[mk] = (m * diff)[:, :, None]
    return fx[mk]


def _over(img, rgba):
    a = rgba[:, :, 3:4] / 255.0
    return img * (1 - a) + rgba[:, :, :3] * a


def frame_parts(fx, skin, t, reduce=False, ss=2):
    """one frame, split: returns (img, ref, under, over, above) as float arrays over the crop.
    img   = board(t) -> UNDER effect layer -> HUD + hand (t) -> OVER effect layer (only CROSS_OK effects)
    ref   = the same frame with both effect layers empty (the state change alone): the loudness meter measures img against it
    under / over = the effect layers (RGBA 0-255) ; above = the HUD + hand layer at t (RGBA)"""
    x0, y0, x1, y1 = box = fx['box']
    pb, pa = below(skin, fx['pre'])[y0:y1, x0:x1], above(skin, fx['pre'])[y0:y1, x0:x1]
    B, Ab = pb, pa
    ctx = Ctx(fx, skin, reduce)
    if fx.get('post'):
        qb, qa = below(skin, fx['post'])[y0:y1, x0:x1], above(skin, fx['post'])[y0:y1, x0:x1]
        k = fx['state'](t, ctx)
        if k > 0:
            M = _smask(fx, skin, pb, qb, pa, qa) * k
            B = pb * (1 - M) + qb * M
            Ab = pa * (1 - M) + qa * M
    lay = Lay(box, ss)
    fx['draw'](lay, t, ctx)
    under = np.asarray(lay.done()).astype(np.float32)
    over = None
    if fx.get('draw_over'):
        if fx['id'] not in CROSS_OK:
            raise ValueError('%s may not draw above the HUD (review 1.6)' % fx['id'])
        lo = Lay(box, ss)
        fx['draw_over'](lo, t, ctx)
        over = np.asarray(lo.done()).astype(np.float32)
    ref = _over(B, Ab)
    img = _over(_over(B, under), Ab)
    if over is not None:
        img = _over(img, over)
    return np.clip(img, 0, 255), np.clip(ref, 0, 255), under, over, Ab


def frame(fx, skin, t, reduce=False, ss=2):
    img = frame_parts(fx, skin, t, reduce, ss)[0]
    return Image.fromarray(img.astype(np.uint8), 'RGB')


# ---------------------------------------------------------------- loudness meter (review 2.10: damage > kill > block > state)
def lstar_img(rgb):
    return RT.lstar(RT.lum(rgb))


def loud_frame(img, ref, end=None, de_thr=5.0):
    """area x value of what the effect adds to one frame (review 2.10).  A pixel counts when the frame differs from the same frame without the
    effect (ref: the pre-state, or the state change at t) by dE76 > de_thr; each counted pixel is weighted by its L* / 100.
    Unit: full-value px (a 100 px patch at L* 100 = 100).
    end (the settled frame): with it, a pixel must ALSO differ from the settled frame, so only the transient (the light and print that come and
    go: flashes, bursts, floods, sparks) counts, not the mark the effect leaves (a gone tick, the dark wedge, the block plate, the new chevron).
    Returns (area x value, area px, summed |dL*| / 100)."""
    la, lb = RT.lab(img), RT.lab(ref)
    ch = np.linalg.norm(la - lb, axis=2) > de_thr
    if end is not None:
        ch &= np.linalg.norm(la - RT.lab(end), axis=2) > de_thr
    return float((la[:, :, 0] * ch).sum() / 100.0), int(ch.sum()), float((np.abs(la[:, :, 0] - lb[:, :, 0]) * ch).sum() / 100.0)


TOKEN_GUARD = {'GAIN': GAIN, 'FOCUS': FOCUS, 'LIME': LIME}


def colour_guard(layer, cols=TOKEN_GUARD, de_max=15.0, a_min=128):
    """px of an effect layer (RGBA) drawn within dE76 de_max of each guarded token (review 1.8: no GAIN / FOCUS / lime on a kill or a hit)"""
    if layer is None:
        return {k: 0 for k in cols}
    m = layer[:, :, 3] >= a_min
    if not m.any():
        return {k: 0 for k in cols}
    lab = RT.lab(layer[:, :, :3][m])
    return {k: int((np.linalg.norm(lab - RT.lab(np.array(c, np.float64)), axis=1) < de_max).sum()) for k, c in cols.items()}


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
