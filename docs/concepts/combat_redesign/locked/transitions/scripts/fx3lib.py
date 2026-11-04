"""fx3lib (2026-11-04 rebuild): shared data and helpers for the T5 / T6 bits transitions on the rebuilt board, at 1920x1080.
Layers come from staged.py (layers/<corp>_p1.npz: the generator's own layers, matching the published plate to 2/255).
Bits follow ART_BIBLE 1.2 (LOCKED) and 6.3: Share Tech Mono 0/1 glyphs with a same-colour outline, in the colour of their source,
white-hot for the first 80 ms, flipping 0<->1, tumbling, then pulled along a curve into their target, going round the rim (never across
the wheel face)."""
import numpy as np, os, math, json
from PIL import Image, ImageFont, ImageDraw

HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/'
CORP = os.environ.get('CORP', 'neutral')
W, H = 1920, 1080
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
PUB = {'neutral': 'p1_decide.png', 'solace': 'p1_decide_solace.png'}[CORP]
FONT_BITS = 'D:/rc_scratch/combat_redesign/locked/corp/src/fonts/ShareTechMono-Regular.ttf'     # ART_BIBLE 1.2: Share Tech Mono atlas
TAU = 2 * math.pi


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


INK = hx('#0C0A16')
PINK = hx('#FF3DA8')              # CELL_PINK: the player (halo snap, the T6 spinner keyline)
HOT_WHITE = hx('#DED8CA')         # white-hot = HIT_PAPER, the board's own hot paper (gate 1 capped every board white to it, L* 86)
BIT_L = (55.0, 80.0)              # a bit keeps its source's hue and chroma; its L* is held in 55-80 (reads on the night room, under K type L* 84)
WHITE_HOT_S = 0.08                # ART_BIBLE 1.2: white-hot for the first 60-100 ms
FLIP_S = 0.07                     # a bit flips 0 <-> 1 every 70 ms of its life
SAMPLE_R = 9                      # px: the source disc a bit's colour is read from
SAMPLE_PCT = float(os.environ.get("SAMPLE_PCT", "0.90"))   # the chroma percentile of the source disc a bit takes


def _load():
    Z = np.load(HERE + 'layers/%s_p1.npz' % CORP)
    LY = {}
    for k in Z.files:
        a = Z[k]
        LY[k] = a.astype(np.float32) if (a.ndim == 3 and a.shape[2] == 4) else a[..., :3].astype(np.float32)
    return LY, json.load(open(HERE + 'layers/%s_p1.json' % CORP))


LY, META = _load()
NCARD = len(META['cards'])
BGD = LY['bg'][..., :3]                          # the plate's room: rb2-1 grade + board scrim
ROOM_BARE = LY['room_bare']                      # the v3.1 bare room = the last frame of T4 (street to room)
ROOM_GRADED = LY['room_graded']
K1ROOM = ROOM_BARE                               # T5 K1 and the room T6 hands back to T4 (reversed): the room as the player entered it
PLATE = np.asarray(Image.open(FIN + PUB).convert('RGB')).astype(np.float32)
CX, CY = float(META['C'][0]), float(META['C'][1])
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
R = np.hypot(xx - CX, yy - CY)
TH = np.arctan2(yy - CY, xx - CX)

# radii at 1080p (locked board: tower 196, ring NOW 214-271, +1 271-328, +2 328-385, band 391-417, lanes 436-470, rim 489-500)
R0, R1, R2, RD = 271.0, 328.0, 385.0, 504.0
R_RIM = 500.0
R_ORBIT = (506.0, 532.0)                         # bits travel round the rim, just outside it (ART_BIBLE 1.2 / 6.3); the wheel touches the frame edges


# ------------------------------------------------------------------ easing
def cl(x, a=0.0, b=1.0): return np.minimum(np.maximum(x, a), b)
def eic(x): x = cl(x); return x ** 3
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)
def smooth(x): x = cl(x); return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ compositing (float RGB base, float RGBA layers 0..255)
def over(base, rgb, a):
    return base + (rgb - base) * a[..., None]


def lay(base, L, k=1.0):
    return over(base, L[..., :3], L[..., 3] / 255.0 * k)


def shift(a, dx, dy):
    dx, dy = int(round(dx)), int(round(dy))
    if dx == 0 and dy == 0:
        return a
    out = np.zeros_like(a)
    ys0, ys1 = max(0, dy), min(H, H + dy); xs0, xs1 = max(0, dx), min(W, W + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def flat(names, under=None):
    b = (BGD if under is None else under).copy()
    for k in names:
        b = lay(b, LY[k])
    return b


def full_plate():
    return flat(['scrim', 'base', 'tower', 'enemy1', 'guns', 'enemy2', 'tickets', 'enemy3', 'hud', 'you'] + ['card%d' % i for i in range(NCARD)] + ['name', 'send'])


def to_pil(a): return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ colour: Lab (D65), the L* clamp, the source sample
_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
_WP = np.array([0.95047, 1.0, 1.08883])


def lin(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def lab(rgb):
    xyz = (lin(rgb) @ _M.T) / _WP
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab2rgb(L, a, b):
    fy = (L + 16) / 116
    f = np.array([fy + a / 500, fy, fy - b / 200])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * _WP
    c = np.clip(np.linalg.solve(_M, xyz), 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return tuple(float(v * 255) for v in c)


def clamp_L(rgb, lo=BIT_L[0], hi=BIT_L[1]):
    L, a, b = lab(np.array(rgb, np.float64))
    L2 = min(max(L, lo), hi)
    if abs(L2 - L) < 1e-6:
        return tuple(float(v) for v in rgb)
    return lab2rgb(L2, a, b)


def sample(img, x, y, r=SAMPLE_R, alpha=None):
    """the colour of the source at (x, y): over the source disc, the pixel at the SAMPLE_PCT (0.90) percentile of chroma (C*ab), so a bit takes the
    element's own colour (glass tint, chevron, slice ink, card art) and not its light edge line or an ink keyline.
    Returns (raw rgb, rgb with the bit L* clamp)."""
    x0, x1 = int(max(0, x - r)), int(min(W, x + r + 1)); y0, y1 = int(max(0, y - r)), int(min(H, y + r + 1))
    py, px = np.mgrid[y0:y1, x0:x1]
    m = (px - x) ** 2 + (py - y) ** 2 <= r * r
    if alpha is not None:
        m &= alpha[y0:y1, x0:x1] > 0.5 * 255
    if not m.any():
        m = (px - x) ** 2 + (py - y) ** 2 <= r * r
    pix = img[y0:y1, x0:x1][m].astype(np.float64)
    lb = lab(pix)
    sal = np.hypot(lb[:, 1], lb[:, 2]) + 0.001 * lb[:, 0]
    i = np.argsort(sal, kind="stable")[int(SAMPLE_PCT * (len(sal) - 1))]
    raw = tuple(float(v) for v in pix[i])
    return raw, clamp_L(raw)


def band_colour(cols):
    """the keyline / ghost / lock colour of a band: the median of its bits' colours (Lab), L* at least 60"""
    lb = lab(np.array(cols, np.float64))
    L, a, b = np.median(lb, 0)
    return lab2rgb(max(L, 60.0), a, b)


# ------------------------------------------------------------------ the bit glyphs (Share Tech Mono, same-colour outline, tumbling)
_MASK = {}


def glyph_mask(ch, size, ang):
    size = int(round(size)); ang = int(round(ang / 15.0)) * 15 % 360
    key = (ch, size, ang)
    if key in _MASK:
        return _MASK[key]
    f = ImageFont.truetype(FONT_BITS, size * 2)
    sw = max(1, int(round(size * 2 / 22.0)))           # ART_BIBLE 6.3: ~1/22 outline, same colour
    w = int(size * 2 * (0.62 * len(ch) + 0.5)) + 4 * sw; h = int(size * 2 * 1.25) + 4 * sw
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((w / 2, h / 2), ch, font=f, fill=255, anchor='mm', stroke_width=sw, stroke_fill=255)
    im = im.resize((max(1, w // 2), max(1, h // 2)), Image.LANCZOS)
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    m = np.asarray(im).astype(np.float32) / 255.0
    _MASK[key] = m
    return m


class Overlay:
    """premultiplied RGBA float overlay at 1920x1080"""
    def __init__(self):
        self.P = np.zeros((H, W, 3), np.float32)
        self.A = np.zeros((H, W), np.float32)
        self.log = []

    def put(self, m, x, y, col, alpha):
        h, w = m.shape
        x0 = int(round(x - w / 2)); y0 = int(round(y - h / 2))
        xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
        if xa >= xb or ya >= yb:
            return
        mm = m[ya - y0:yb - y0, xa - x0:xb - x0] * alpha
        self.P[ya:yb, xa:xb] = self.P[ya:yb, xa:xb] * (1 - mm[..., None]) + np.array(col, np.float32) * mm[..., None]
        self.A[ya:yb, xa:xb] = self.A[ya:yb, xa:xb] * (1 - mm) + mm

    def glyph(self, x, y, ch, col, size, alpha, ang=0.0, tag=None):
        if size < 6 or alpha <= 0.03:
            return
        self.put(glyph_mask(ch, size, ang), x, y, col, float(min(alpha, 1.0)))
        if tag is not None:
            self.log.append((float(x), float(y)) + tuple(tag))

    def ring(self, rp, a0, length, dr, col, w, alpha):
        """antialiased arc of radius rp, from angle a0 along direction dr for `length` rad (>= TAU: full circle), width w px"""
        if alpha <= 0.004:
            return
        ro = rp + w
        y0, y1 = max(0, int(CY - ro - 2)), min(H, int(CY + ro + 3)); x0, x1 = max(0, int(CX - ro - 2)), min(W, int(CX + ro + 3))
        Rc = R[y0:y1, x0:x1]
        rm = cl(w / 2 + 0.5 - np.abs(Rc - rp))
        if length < TAU - 1e-3:
            rel = np.mod((TH[y0:y1, x0:x1] - a0) * dr, TAU)
            rm = rm * cl((length - rel) * rp + 0.5) * cl(rel * rp + 0.5)
        mm = rm * alpha
        self.P[y0:y1, x0:x1] = self.P[y0:y1, x0:x1] * (1 - mm[..., None]) + np.array(col, np.float32) * mm[..., None]
        self.A[y0:y1, x0:x1] = self.A[y0:y1, x0:x1] * (1 - mm) + mm

    def keyline(self, rp, a0, length, dr, col, w_ink, w_col, alpha):
        self.ring(rp, a0, length, dr, INK, w_ink, alpha)
        self.ring(rp, a0, length, dr, col, w_col, alpha)

    def dot(self, x, y, r, col, r_ink):
        x0, x1 = max(0, int(x - r - r_ink - 2)), min(W, int(x + r + r_ink + 3)); y0, y1 = max(0, int(y - r - r_ink - 2)), min(H, int(y + r + r_ink + 3))
        d = np.hypot(xx[y0:y1, x0:x1] - x, yy[y0:y1, x0:x1] - y)
        for rr, c in ((r + r_ink, INK), (r, col)):
            mm = cl(rr + 0.5 - d)
            self.P[y0:y1, x0:x1] = self.P[y0:y1, x0:x1] * (1 - mm[..., None]) + np.array(c, np.float32) * mm[..., None]
            self.A[y0:y1, x0:x1] = self.A[y0:y1, x0:x1] * (1 - mm) + mm

    def onto(self, base):
        return base * (1 - self.A[..., None]) + self.P


# ------------------------------------------------------------------ the route round the rim (ART_BIBLE 1.2 "bits go round the rim"; 6.3)
def polar(x, y):
    return float(np.hypot(x - CX, y - CY)), float(math.atan2(y - CY, x - CX))


def wrap(a):
    return (a + math.pi) % TAU - math.pi


def make_route(sx, sy, tx, ty, rorb):
    """a bit's path from a source outside the rim to a target: in to the orbit radius, round the rim the short way, then radially in
    (or out, for a target outside the rim) at the target's own angle.  Inside the rim a bit only ever moves radially."""
    rs, ths = polar(sx, sy); rt, tht = polar(tx, ty)
    rs = max(rs, rorb + 30.0)
    d = wrap(tht - ths)
    pd = 0.55 + 0.25 * abs(d) / math.pi
    return dict(rs=rs, ths=ths, rt=rt, tht=tht, d=d, rorb=rorb, pd=pd, fl=0.18 + 0.12 * abs(d) / math.pi)


def route_xy(g, p):
    p = float(min(max(p, 0.0), 1.0))
    if p <= g['pd']:
        q = p / g['pd']
        # first in to the orbit (radial, at the source's own angle), then round the rim; the two overlap a little for a soft corner
        th = g['ths'] + g['d'] * float(smooth((q - 0.2) / 0.8))
        r = g['rorb'] + (g['rs'] - g['rorb']) * (1 - float(smooth(q / 0.3)))
    else:
        q = (p - g['pd']) / (1 - g['pd'])
        th = g['tht']
        r = g['rorb'] + (g['rt'] - g['rorb']) * float(smooth(q))
    return CX + r * math.cos(th), CY + r * math.sin(th)


# glyph sources: four spots inside the bio lab cutaway (the building the enemy lives in), one per stream
SRC_CENTRES = [(1420, 560), (1560, 610), (1330, 650), (1640, 660)]
SRC_BOX = (1240, 430, 1760, 760)


def sources(n, seed, which):
    r = np.random.RandomState(seed)
    cx, cy = SRC_CENTRES[which]
    sx = cx + r.randn(n) * 60; sy = cy + r.randn(n) * 40
    return np.clip(sx, SRC_BOX[0], SRC_BOX[2]), np.clip(sy, SRC_BOX[1], SRC_BOX[3])


# ------------------------------------------------------------------ HUD / UI groups at 1080p: (layers, dx, dy) at full offset
HUD_GROUPS = [(['hud', 'you'], 0, -80), (['name'], -80, 0)]
SEND_GROUP = (['send'], 0, 100)


def card_box(i):
    c = META['cards'][i]
    return float(c['cx']), float(c['cy']), float(c['ang'])


def luma_gamma(a): return float((a * np.array([.2126, .7152, .0722])).sum(-1).mean() / 255.0)
