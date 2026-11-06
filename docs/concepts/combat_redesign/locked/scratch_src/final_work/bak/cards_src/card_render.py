"""card_render: the REBEL_CELL card system, locked style (ART CALL 53).

    draw_card(card, size, state) -> PIL RGBA

WPAP card (chamfered die-cut, flat facet planes, slanted plates, hard offset drops) with
  * a type band whose colour is the card TYPE (TOWER = teal, WAVE = violet),
  * a band background in one of the other punk styles (linocut, Ben-Day, collage, Jinx, mural, xerox),
  * the xerox icon (paper-white glyph, black key line + hard drop, spot-ink disc, misregistered second ink) recoloured per card,
  * the black-book layout (see card_titles/LAYOUT.md) and the title rule (neutral fill, hard keyline, cap >= 26 design px).

card   a name from CARDS ('Brace', 'Spin3', ...) or a dict {'name':..., plus any override: cost, loud, txt, nm, fam}
size   (w, h) of the CARD box in output px, or one number = the width (height follows 176:250).
       The returned image is the card box plus MARGIN design px each side (MARGIN * size / 176 px), so drops, the lift print and
       the chamfer shadow are never cut.  Use margin_px(size) to place it: centre of the card = centre of the image.
state  'normal' | 'hover' | 'played' | 'unaffordable' | 'nowords'  or a dict
       {'mode': ..., 'dim': 0.88 (value of a resting hand card), 'nowords': bool}
       hover = lifted: the caller scales the box (1.10 x) - draw_card draws the card at the size it is given, full value,
       with the pink misregistered print behind it and a longer hard drop.
Pure numpy / scipy / PIL; glyph PNGs and fonts live beside this file.  No Godot, no network.
"""
import math, os, sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
CW, CH, MARGIN = 176, 250, 18
IC = (88.0, 66.0)       # icon centre (design px)

# ------------------------------------------------------------------ palette
def hx(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0

INK = hx('15121A'); CREAM = hx('F4EEE0'); CREAM_D = hx('E6DCC4'); WHITE = hx('FBFAF4')
PINK = hx('FF3DA8'); PINK_D = hx('C21A7C'); WINK = hx('1B0B33')
CYAN_COIN = hx('1A8FB8'); CYAN_HI = hx('5CE1FF')

TYPES = {   # the card TYPE colours (the word on the plate): the key sheet explains them
    'TOWER': dict(col=hx('19D3BC'), dk=hx('0B7F73'), text=INK),
    'WAVE':  dict(col=hx('A683FF'), dk=hx('5A33C9'), text=INK),
}

# ------------------------------------------------------------------ the 11 Shifting Waves cards (state_e10.json cards: [RAM, Trace]; text from E10 build10)
CARDS = {
    'Nudge':    dict(fam='TOWER', g='PI_SPIN_CW', nm='NUDGE',    txt='Turn the tower 1', mult='1', cost=1, loud=0),
    'Spin2':    dict(fam='TOWER', g='PI_SPIN_CW', nm='SPIN 2',   txt='Turn the tower 2', mult='2', cost=1, loud=0),
    'Spin3':    dict(fam='TOWER', g='PI_SPIN_CW', nm='SPIN 3',   txt='Turn the tower 3', mult='3', cost=1, loud=0),
    'Brace':    dict(fam='TOWER', g='C_BRACE',    nm='BRACE',    txt='Block a slice', cost=1, loud=0),
    'Strike':   dict(fam='TOWER', g='C_STRIKE',   nm='STRIKE',   txt='Hit a unit for 2', cost=1, loud=0),
    'Firewall': dict(fam='WAVE',  g='BURN',       nm='FIREWALL', txt='Burn 2 units', cost=2, loud=2),
    'Pull':     dict(fam='WAVE',  g='C_PULL',     nm='PULL',     txt='Pull a unit in', cost=0, loud=1),
    'Shove':    dict(fam='WAVE',  g='C_SHOVE',    nm='SHOVE',    txt='Slide a unit 1', cost=2, loud=2),
    'Twist':    dict(fam='WAVE',  g='C_TWIST',    nm='TWIST',    txt='Turn one ring 1', cost=0, loud=0),
    'Hold':     dict(fam='WAVE',  g='C_HOLD',     nm='HOLD',     txt='Pause the wave', cost=0, loud=0),
    'Trigger':  dict(fam='WAVE',  g='C_TRIG',     nm='TRIGGER',  txt='Resolve a unit', cost=1, loud=1),
}
ORDER = ['Nudge', 'Spin2', 'Spin3', 'Brace', 'Strike', 'Firewall', 'Pull', 'Shove', 'Twist', 'Hold', 'Trigger']

# per card: background style, its palette, and the recoloured xerox icon (disc = spot ink, mis = second misprinted ink)
ART = {
    'Nudge':    dict(style='benday',  bg='3BB8F2', dot='1B4FB8', hi='E8F8FF', disc='C81E78', mis='FFC83A', arcs=1, seed=11),
    'Spin2':    dict(style='benday',  bg='44D9A6', dot='0E7A5C', hi='EFFFF8', disc='2A4BE0', mis='FF3DA8', arcs=2, seed=12),
    'Spin3':    dict(style='benday',  bg='FF8A1E', dot='B5330F', hi='FFF1D8', disc='2B1F9E', mis='1AA6E8', arcs=3, seed=13),
    'Brace':    dict(style='linocut', bg='2848D8', key='101018', bone='F1EAD6', disc='FF3DA8', mis='101018', dirn='radial', seed=14),
    'Strike':   dict(style='collage', bg='C9F23C', paper=['F1EAD6', '15121A', '2A4BE0', 'C9F23C'], disc='15121A', mis='FF3DA8', seed=15),
    'Firewall': dict(style='mural',   sky=['0B2A45', '0E4A63', '137489', '2BA9A5'], city='06182A', disc='FF3DA8', mis='FFC83A', seed=16),
    'Pull':     dict(style='linocut', bg='18A872', key='0B1A14', bone='F1EAD6', disc='FF3DA8', mis='0B1A14', dirn='down', seed=17),
    'Shove':    dict(style='collage', bg='F1EAD6', paper=['2A4BE0', 'F1EAD6', '15121A', '9BD0FF'], disc='3A1C9E', mis='FF7A1A', slide=True, seed=18),
    'Twist':    dict(style='mural',   sky=['4A1C8C', 'A3267E', 'EE5B5B', 'FFB347'], city='2A0C4A', disc='5B2BE0', mis='15121A', seed=19),
    'Hold':     dict(style='xerox',   bg='15121A', dot='F2EEE4', spot='12A9E6', disc='FF3DA8', mis='12A9E6', seed=20),
    'Trigger':  dict(style='jinx',    bg='160B2E', neon=['27D3F5', 'FF3DA8'], disc='7A2CFF', mis='C8FF3C', seed=21),
}
STYLE_WHY = {
    'benday': 'Ben-Day dots + speed arcs: the Spin family turns the tower, the arcs count the turns (1, 2, 3)',
    'linocut': 'carved black key on one flat plate: hard, solid, protective (Brace) and straight-down gouges (Pull)',
    'collage': 'torn paper shards and tape: impact (Strike) and sliding strips (Shove)',
    'mural': 'spray sunset over a skyline: the waves (Twist) and the burn (Firewall) belong to the city',
    'xerox': 'black toner and a halftone dot field: dead copier stillness for Hold',
    'jinx': 'neon scribble on night ink: aim and lock-on (Trigger)',
}


# ------------------------------------------------------------------ canvas
class Cv:
    def __init__(self, R):
        self.R = R
        self.W = int((CW + 2 * MARGIN) * R); self.H = int((CH + 2 * MARGIN) * R)
        self.rgb = np.zeros((self.H, self.W, 3), np.float32)
        self.a = np.zeros((self.H, self.W), np.float32)

    def p(self, x, y):
        return ((x + MARGIN) * self.R, (y + MARGIN) * self.R)

    def paint(self, m, col, op=1.0):
        m = m * op
        c = np.asarray(col, np.float32)
        if c.ndim == 3:
            self.rgb = self.rgb * (1 - m[..., None]) + c * m[..., None]
        else:
            self.rgb = self.rgb * (1 - m[..., None]) + c[None, None, :] * m[..., None]
        self.a = self.a + m * (1 - self.a)

    def img(self):
        a = np.clip(self.a, 0, 1)
        rgb = np.where(a[..., None] > 1e-4, self.rgb, 0)
        return Image.fromarray(np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).astype(np.uint8), 'RGBA')

    def grid(self):
        y, x = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        return x / self.R - MARGIN, y / self.R - MARGIN


def _mask(cv, fn):
    im = Image.new('L', (cv.W, cv.H), 0)
    fn(ImageDraw.Draw(im))
    return np.asarray(im, np.float32) / 255.0


def poly(cv, pts):
    P = [cv.p(*q) for q in pts]
    return _mask(cv, lambda d: d.polygon(P, fill=255))


def circle(cv, x, y, r):
    cx, cy = cv.p(x, y)
    return _mask(cv, lambda d: d.ellipse([cx - r * cv.R, cy - r * cv.R, cx + r * cv.R, cy + r * cv.R], fill=255))


def stroke(cv, pts, w, cap=True):
    P = [cv.p(*q) for q in pts]
    def f(d):
        d.line(P, fill=255, width=max(1, int(round(w * cv.R))), joint='curve')
        if cap:
            for (x, y) in (P[0], P[-1]):
                r = w * cv.R / 2
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return _mask(cv, f)


def grow(cv, m, r):
    if r <= 0:
        return m
    d = ndi.distance_transform_edt(m < 0.5)
    return (d <= r * cv.R).astype(np.float32)


def shift(cv, m, dx, dy):
    return ndi.shift(m, (dy * cv.R, dx * cv.R), order=0, mode='constant')


def extrude(cv, m, dx, dy):
    n = max(2, int(max(abs(dx), abs(dy)) * cv.R / 2))
    out = m.copy()
    for k in range(1, n + 1):
        out = np.maximum(out, shift(cv, m, dx * k / n, dy * k / n))
    return out


_FC = {}
def font(name, px):
    k = (name, int(px))
    if k not in _FC:
        _FC[k] = ImageFont.truetype(HERE + '/fonts/' + name, max(4, int(px)))
    return _FC[k]

ANTON = 'Anton-Regular.ttf'; PLEX = 'IBMPlexSansCondensed-Medium.ttf'; MONO = 'ShareTechMono-Regular.ttf'


def text_w(txt, name, px, track=0.0):
    f = font(name, px * 8)
    return f.getlength(txt) / 8.0 + track * max(0, len(txt) - 1)


def text(cv, txt, x, y, px, name=ANTON, track=0.0, skew=0.0, rot=0.0):
    """mask of centred text (anchor mm), tracking in design px, skew (x shift per y), rotation in degrees (screen, clockwise +)"""
    R = cv.R
    f = font(name, px * R)
    w = text_w(txt, name, px, track) * R
    pad = int(px * R * 0.8)
    Wt, Ht = int(w + 2 * pad), int(px * R * 2.2)
    im = Image.new('L', (Wt, Ht), 0)
    d = ImageDraw.Draw(im)
    cx = pad
    for ch in txt:
        d.text((cx, Ht / 2), ch, font=f, fill=255, anchor='lm')
        cx += f.getlength(ch) + track * R
    # centre vertically on the glyph "H" body so mm means the cap middle
    cap = f.getbbox('H')
    ycap = (cap[1] + cap[3]) / 2 - f.getbbox('H', anchor='lm')[1] * 0  # lm anchor: baseline-mid of text line; use bbox with anchor lm
    bb = f.getbbox('H', anchor='lm')
    capmid = Ht / 2 + (bb[1] + bb[3]) / 2
    if skew or rot:
        a = math.radians(rot)
        c, s = math.cos(a), math.sin(a)
        # affine maps output->input: centre (Wt/2, capmid)
        cx0, cy0 = Wt / 2, capmid
        M = np.array([[c, s], [-s, c]]) @ np.array([[1, 0], [0, 1]])
        # skew: x' = x + skew*(y)
        Sk = np.array([[1, -skew], [0, 1]])
        A = Sk @ M
        off = np.array([cx0, cy0]) - A @ np.array([cx0, cy0])
        im = im.transform(im.size, Image.AFFINE, (A[0, 0], A[0, 1], off[0], A[1, 0], A[1, 1], off[1]), resample=Image.BILINEAR)
    arr = np.asarray(im, np.float32) / 255.0
    out = np.zeros((cv.H, cv.W), np.float32)
    px0, py0 = cv.p(x, y)
    ox, oy = int(round(px0 - Wt / 2)), int(round(py0 - capmid))
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(cv.H, oy + Ht), min(cv.W, ox + Wt)
    if ys1 > ys0 and xs1 > xs0:
        out[ys0:ys1, xs0:xs1] = arr[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out


_GL = {}
def glyph(cv, name, px, x, y):
    if name not in _GL:
        _GL[name] = Image.open(HERE + '/glyphs/' + name + '.png').convert('L')
    g = _GL[name]
    # trim to bbox so px is the glyph's long side
    bb = g.getbbox()
    gc = g.crop(bb)
    k = px * cv.R / max(gc.size)
    gc = gc.resize((max(1, int(gc.width * k)), max(1, int(gc.height * k))), Image.LANCZOS)
    arr = np.asarray(gc, np.float32) / 255.0
    out = np.zeros((cv.H, cv.W), np.float32)
    px0, py0 = cv.p(x, y)
    ox, oy = int(round(px0 - arr.shape[1] / 2)), int(round(py0 - arr.shape[0] / 2))
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(cv.H, oy + arr.shape[0]), min(cv.W, ox + arr.shape[1])
    out[ys0:ys1, xs0:xs1] = arr[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out


def halftone(cv, cov, pitch, ang=45.0, ox=0.0, oy=0.0):
    """dot screen; cov: coverage 0..1 (H,W); pitch in design px; dot area = coverage"""
    X, Y = cv.grid()
    a = math.radians(ang)
    u = (X - ox) * math.cos(a) + (Y - oy) * math.sin(a)
    v = -(X - ox) * math.sin(a) + (Y - oy) * math.cos(a)
    fu = (u / pitch) - np.floor(u / pitch) - 0.5
    fv = (v / pitch) - np.floor(v / pitch) - 0.5
    d = np.hypot(fu, fv)
    r = np.sqrt(np.clip(cov, 0, 1) / math.pi) * 1.0
    r = np.minimum(r, 0.72)
    return (d < r).astype(np.float32)


def lerp(a, b, t):
    return a + (b - a) * t


def lum(c):
    c = np.asarray(c, np.float32)
    l = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def jag(cv, pts, amp, seed, n=6):
    """roughen a polygon edge (torn paper): subdivide, jitter"""
    r = np.random.default_rng(seed)
    out = []
    for i in range(len(pts)):
        a, b = np.array(pts[i], float), np.array(pts[(i + 1) % len(pts)], float)
        L = np.hypot(*(b - a))
        k = max(1, int(L / n))
        for j in range(k):
            t = j / k
            q = a + (b - a) * t
            nrm = np.array([-(b - a)[1], (b - a)[0]]) / (L + 1e-6)
            q = q + nrm * r.uniform(-amp, amp)
            out.append(tuple(q))
    return out


# ------------------------------------------------------------------ geometry of the card
CH_ = 16     # chamfer
SHAPE = [(0, 0), (CW - CH_, 0), (CW, CH_), (CW, CH), (CH_, CH), (0, CH - CH_)]
BAND = [(8, 8), (CW - 8 - 14, 8), (CW - 8, 22), (CW - 8, 126), (8, 126)]


# ------------------------------------------------------------------ band backgrounds (each paints inside band mask `ab`)
def bg_benday(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    bg, dot, hi = hx(A['bg']), hx(A['dot']), hx(A['hi'])
    cv.paint(ab, bg)
    cx, cy = IC
    # big dark dot screen rising from the lower left, a small light screen over it
    cov = np.clip((Y - 20) / 110.0, 0, 1) * 0.95 * np.clip((X < 200) * 1.0 - (X - 8) / 330.0, 0.25, 1)
    rr = np.hypot(X - cx, Y - cy)
    cov = cov * np.clip((rr - 36) / 20.0, 0, 1)
    cv.paint(halftone(cv, cov, 8.5, 45) * ab, dot)
    cov2 = np.clip(1.0 - (Y - 8) / 100.0, 0, 1) * 0.5 * np.clip((rr - 38) / 18.0, 0, 1)
    cv.paint(halftone(cv, cov2, 8.5, 45, 4.2, 4.2) * ab, hi)
    # speed arcs: arcs = number of turns this card makes (1, 2, 3)
    for k in range(A['arcs']):
        rad = 43 + 7.0 * k
        a0 = math.radians(205 + 22 * k)
        a1 = math.radians(205 + 22 * k + 78 - 8 * k)
        pts = [(cx + rad * math.cos(a0 + (a1 - a0) * t / 24), cy + rad * math.sin(a0 + (a1 - a0) * t / 24)) for t in range(25)]
        st = stroke(cv, pts, 4.2 - 0.5 * k)
        cv.paint(grow(cv, st, 1.6) * ab, INK)
        cv.paint(st * ab, hi)
    # two lightning bolts (white, ink keyline), off the icon
    def bolt(x, y, s, rot):
        base = [(0, -10), (5, -10), (1, -1), (7, -1), (-4, 12), (-1, 2), (-7, 2)]
        c, sn = math.cos(rot), math.sin(rot)
        return [(x + s * (px * c - py * sn), y + s * (px * sn + py * c)) for px, py in base]
    for (bx, by, s, rt) in ((22, 106, 1.15, -0.25), (154, 24, 1.0, 0.28)):
        m = poly(cv, bolt(bx, by, s, rt))
        cv.paint(grow(cv, m, 1.6) * ab, INK)
        cv.paint(m * ab, hi)


def _linocut_halo(cv, A, seed):
    r = np.random.default_rng(seed)
    cx, cy = IC
    n = 17
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rad = 42.5 + (r.uniform(-2.4, 2.4)) + (2.6 if i % 2 else 0)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return poly(cv, pts)


def bg_linocut(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    bg, key, bone = hx(A['bg']), hx(A['key']), hx(A['bone'])
    cv.paint(ab, bg)
    cx, cy = IC
    ang = np.arctan2(Y - cy, X - cx)
    rr = np.hypot(X - cx, Y - cy)
    if A['dirn'] == 'radial':
        n = 30
        mk = np.zeros_like(X)
        for i in range(n):
            a = 2 * math.pi * i / n + r.uniform(-0.04, 0.04)
            L0 = r.uniform(52, 66); L1 = L0 + r.uniform(30, 90)
            w0 = r.uniform(0.020, 0.040)
            da = np.angle(np.exp(1j * (ang - a)))
            tt = np.clip((rr - L0) / (L1 - L0), 0, 1)
            inside = (rr > L0) & (rr < L1) & (np.abs(da) < w0 * (1 - tt) * (1 + 0.0))
            mk = np.maximum(mk, inside.astype(np.float32))
        cv.paint(mk * ab, key)
    else:
        # straight-down gouges, long and short, converging on the icon
        mk = np.zeros_like(X)
        for i in range(22):
            x0 = 8 + (i + r.uniform(0.2, 0.8)) * (CW - 16) / 22
            top = r.uniform(8, 60) if abs(x0 - cx) > 40 else r.uniform(112, 120)
            L = r.uniform(30, 70) if abs(x0 - cx) > 40 else r.uniform(5, 12)
            pts = [(x0 - 2.6, top), (x0 + 2.6, top), (x0 + 0.4, top + L)]
            mk = np.maximum(mk, poly(cv, pts))
        cv.paint(mk * ab, key)
        # arrowheads converge down
        for i in range(3):
            yy = 14 + i * 14
            cv.paint(poly(cv, [(18, yy), (30, yy + 9), (42, yy)]) * 0, key)
    # punch dots and chips
    for i in range(30):
        x = r.uniform(10, CW - 10); y = r.uniform(10, 124)
        if math.hypot(x - cx, y - cy) < 52:
            continue
        cv.paint(circle(cv, x, y, r.uniform(0.9, 1.8)) * ab, key)
    # solid dark lower plate chunk (the black key's mass) at the bottom, with a rough bone edge
    ch = poly(cv, jag(cv, [(8, 114), (CW - 8, 108), (CW - 8, 126), (8, 126)], 1.3, A['seed'] + 5, 5))
    cv.paint(ch * ab, key)
    cv.paint(shift(cv, ch, 0, -2.6) * (1 - ch) * ab * 0.0, bone)
    # scissor halo: bone cut-out round the icon, with a hard ink drop
    halo = _linocut_halo(cv, A, A['seed'] + 3)
    cv.paint(extrude(cv, grow(cv, halo, 1.6), 3.0, 3.4) * ab, key)
    cv.paint(grow(cv, halo, 1.6) * ab, key)
    cv.paint(halo * ab, bone)


def _torn(cv, pts, seed, amp=1.4):
    return poly(cv, jag(cv, pts, amp, seed, 5))


def bg_collage(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    pal = [hx(c) for c in A['paper']]
    cv.paint(ab, pal[0] if not A.get('slide') else hx('F1EAD6'))
    cx, cy = IC
    shapes = []
    if A.get('slide'):
        # sliding strips: 5 horizontal strips offset sideways, shove direction to the right, motion tail
        ys = [10, 34, 58, 82, 104]
        for i, y0 in enumerate(ys):
            off = (i - 2) * 9 + r.uniform(-3, 3)
            h = 21 if i < 4 else 22
            shapes.append(([(0 + off, y0), (CW + off, y0 - 2), (CW + off, y0 + h - 2), (0 + off, y0 + h)], pal[i % len(pal)] if i % 2 == 0 else pal[(i + 1) % len(pal)]))
    else:
        shards = [
            [(0, 8), (110, 8), (60, 70)], [(70, 8), (CW, 8), (CW, 90)],
            [(0, 40), (70, 126), (0, 126)], [(90, 126), (CW, 50), (CW, 126)],
        ]
        for i, s in enumerate(shards):
            shapes.append((s, pal[(i + 1) % len(pal)] if i % 3 else pal[0]))
    for i, (pts, col) in enumerate(shapes):
        m = _torn(cv, pts, A['seed'] * 10 + i, 1.5) * ab
        cv.paint(extrude(cv, grow(cv, m, 1.5), 2.2, 2.8) * ab, INK, 0.9)
        cv.paint(grow(cv, m, 1.5) * ab, INK)
        cv.paint(m * ab, col)
        # a halftone on every other piece
        if i % 2 == 0:
            cov = np.clip((Y - 8) / 118.0, 0, 1) * 0.8
            cv.paint(halftone(cv, cov, 6.5, 45) * m * ab, INK if lum(col) > 0.25 else hx('F1EAD6'), 0.9)
    # tape
    for (tx, ty, rot) in ((20, 14, -24), (150, 112, -18)):
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = [(tx + px * c - py * s, ty + px * s + py * c) for px, py in ((-16, -6), (16, -6), (16, 6), (-16, 6))]
        m = poly(cv, pts)
        cv.paint(grow(cv, m, 1.2) * ab, INK)
        cv.paint(m * ab, hx('F6F3EA'), 0.92)
    # the lightning shard for Strike / nothing for Shove
    if not A.get('slide'):
        base = [(0, -10), (5, -10), (1, -1), (7, -1), (-4, 12), (-1, 2), (-7, 2)]
        for (bx, by, sc, rt) in ((142, 40, 2.3, 0.3), (28, 96, 2.1, -0.3)):
            c, sn = math.cos(rt), math.sin(rt)
            m = poly(cv, [(bx + sc * (px * c - py * sn), by + sc * (px * sn + py * c)) for px, py in base])
            cv.paint(extrude(cv, grow(cv, m, 1.6), 2.4, 3.0) * ab, INK)
            cv.paint(grow(cv, m, 1.6) * ab, INK)
            cv.paint(m * ab, hx('F6F3EA'))
    else:
        # motion bar: three solid speed bars left of the icon
        for i, (yy, L) in enumerate(((52, 38), (66, 52), (80, 30))):
            m = poly(cv, [(12, yy - 3), (12 + L, yy - 3), (12 + L + 6, yy), (12 + L, yy + 3), (12, yy + 3)])
            cv.paint(grow(cv, m, 1.2) * ab, INK)
            cv.paint(m * ab, hx('FF7A1A'))
    return


def _wob(r, n, amp):
    v = r.normal(0, 1, n)
    k = np.ones(3) / 3
    return np.convolve(v, k, 'same') * amp


def bg_jinx(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    bg = hx(A['bg'])
    cv.paint(ab, bg)
    cx, cy = IC
    # flat deep planes (night ink) for depth
    cv.paint(poly(cv, [(8, 8), (90, 8), (8, 90)]) * ab, hx('1E1040'))
    cv.paint(poly(cv, [(CW - 8, 126), (CW - 8, 60), (100, 126)]) * ab, hx('0F0620'))
    cols = [hx(c) for c in A['neon']]
    def scrib(pts, col, w):
        st = stroke(cv, pts, w)
        cv.paint(shift(cv, grow(cv, st, 0.6), 1.2, 1.2) * ab, hx('06020F'))
        cv.paint(st * ab, col)
    # spiral hugging the disc
    n = 90
    th = np.linspace(0, 3.6 * math.pi, n)
    rad = 44 + 4.0 * th / (3.6 * math.pi) * 3 + _wob(r, n, 0.7)
    pts = [(cx + rad[i] * math.cos(th[i] - 0.8), cy + rad[i] * math.sin(th[i] - 0.8)) for i in range(n)]
    scrib(pts, cols[0], 2.2)
    # zig-zag
    zz = [(14, 112), (30, 96), (40, 114), (58, 100), (68, 116)]
    scrib(zz, cols[1], 2.2)
    zz = [(106, 18), (120, 30), (130, 14), (146, 28), (158, 12)]
    scrib(zz, cols[0], 2.0)
    # loops
    for (lx, ly, s) in ((26, 28, 1.0), (150, 96, 0.9)):
        t = np.linspace(0, 2 * math.pi * 1.7, 50)
        pts = [(lx + s * (6 + 1.3 * q) * math.cos(q) * 0.8, ly + s * (6 + 1.3 * q) * math.sin(q) * 0.8) for q in t]
        scrib(pts, cols[1], 1.9)
    # stars and crosses
    def star(x, y, rr, col):
        pts = []
        for q in range(8):
            rad_ = rr if q % 2 == 0 else rr * 0.28
            a = math.pi / 4 * q - math.pi / 2
            pts.append((x + rad_ * math.cos(a), y + rad_ * math.sin(a)))
        cv.paint(poly(cv, pts) * ab, col)
    star(20, 62, 6, cols[0]); star(158, 56, 5, cols[1]); star(132, 112, 4.5, cols[0]); star(44, 20, 4, cols[1])
    for (x, y) in ((70, 20), (12, 84), (162, 80)):
        scrib([(x - 4, y), (x + 4, y)], cols[1], 1.8); scrib([(x, y - 4), (x, y + 4)], cols[1], 1.8)


def bg_mural(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    sky = [hx(c) for c in A['sky']]
    n = len(sky)
    # stepped spray sky (flat bands, hand-cut edges)
    cv.paint(ab, sky[0])
    for i in range(1, n):
        y0 = 8 + (118) * i / n
        pts = [(8, y0), (CW - 8, y0 - 5 - 3 * i)]
        pts = [(8, y0 + 4), (CW - 8, y0 - 6), (CW - 8, 126), (8, 126)]
        m = poly(cv, jag(cv, pts, 1.1, A['seed'] + i, 6))
        cv.paint(m * ab, sky[i])
    cx, cy = IC
    # big spray sun / swirl behind the icon: flat rings in the lightest sky colour
    for k, (rad, col) in enumerate(((58, sky[-1]), (52, sky[-2]))):
        m = circle(cv, cx, cy + 6, rad)
        cv.paint(m * ab, col, 0.55 if k == 0 else 0.0)
    ring = circle(cv, cx, cy, 50) - circle(cv, cx, cy, 46.5)
    cv.paint(np.clip(ring, 0, 1) * ab, hx('FBFAF4'), 0.85)
    # skyline: blocks with lit windows
    city = hx(A['city'])
    x = 8
    blocks = []
    while x < CW - 8:
        w = r.uniform(12, 22); h = r.uniform(16, 44)
        blocks.append((x, w, h)); x += w + r.uniform(0, 2)
    for (bx, bw, bh) in blocks:
        m = poly(cv, [(bx, 126 - bh), (bx + bw, 126 - bh), (bx + bw, 126), (bx, 126)])
        cv.paint(m * ab, city)
        for wy in np.arange(126 - bh + 5, 120, 7):
            for wx in np.arange(bx + 3, bx + bw - 3, 5):
                if r.random() < 0.3:
                    cv.paint(poly(cv, [(wx, wy), (wx + 2.4, wy), (wx + 2.4, wy + 3), (wx, wy + 3)]) * ab, sky[-1])
    # spray drips from the top edge of the skyline sign: three drips
    for dx in (24, 71, 132):
        top = 126 - 24 - r.uniform(0, 12)
        st = stroke(cv, [(dx, top), (dx, top + r.uniform(10, 20))], 2.8)
        cv.paint(st * ab, hx('FBFAF4'), 0.85)


def bg_xerox(cv, ab, A, X, Y):
    r = np.random.default_rng(A['seed'])
    bg, dot, spot = hx(A['bg']), hx(A['dot']), hx(A['spot'])
    cv.paint(ab, bg)
    cx, cy = IC
    # flat spot-ink block, slapped off-register behind the icon
    blk = poly(cv, [(8, 52), (CW - 8, 40), (CW - 8, 92), (8, 100)])
    cv.paint(blk * ab, spot)
    cv.paint(extrude(cv, grow(cv, blk, 0.0), 0, 0) * 0, INK)
    cov = np.clip((Y - 10) / 116.0, 0, 1) * 1.0
    rr = np.hypot(X - cx, Y - cy)
    cov = cov * np.clip((rr - 38) / 20.0, 0, 1)
    cv.paint(halftone(cv, cov, 7.0, 45) * ab, dot)
    cv.paint(halftone(cv, cov * 0.6, 7.0, 45, 3.5, 3.5) * blk * ab, INK, 0.9)
    # toner speckle
    sp = (r.random((cv.H, cv.W)) > 0.9985).astype(np.float32)
    sp = ndi.maximum_filter(sp, size=max(2, int(cv.R * 0.6)))
    cv.paint(sp * ab, dot, 0.8)
    # copier edge: a hard dot-white band at the very bottom
    cv.paint(poly(cv, [(8, 119), (CW - 8, 114), (CW - 8, 126), (8, 126)]) * ab, dot)


BGS = dict(benday=bg_benday, linocut=bg_linocut, collage=bg_collage, jinx=bg_jinx, mural=bg_mural, xerox=bg_xerox)


def facets(cv, ab, A, X, Y):
    """WPAP: flat translucent planes cut across the art band (lit planes white, shade planes ink); the glint plane is the lightest"""
    r = np.random.default_rng(A['seed'] * 7 + 3)
    cx, cy = IC
    x0, y0, x1, y1 = 8, 8, CW - 8, 126
    def edge_pt():
        s = r.integers(0, 4)
        if s == 0: return (r.uniform(x0, x1), y0)
        if s == 1: return (x1, r.uniform(y0, y1))
        if s == 2: return (r.uniform(x0, x1), y1)
        return (x0, r.uniform(y0, y1))
    for i in range(4):
        a, b = edge_pt(), edge_pt()
        c = (r.uniform(x0 + 30, x1 - 30), r.uniform(y0 + 25, y1 - 25))
        m = poly(cv, [a, b, c]) * ab
        # keep facets quiet around the icon so the disc reads
        cv.paint(m, WHITE if i % 2 == 0 else INK, 0.10 if i % 2 == 0 else 0.15)
    # the glint plane: one sliver across the upper left
    g = poly(cv, [(x0, y0), (x0 + 58, y0), (x0 + 20, y0 + 40), (x0, y0 + 56)]) * ab
    cv.paint(g, WHITE, 0.11)


# ------------------------------------------------------------------ the card
def _fit_title(nm, maxw=128.0, px0=38.0, track=1.0, floor=30.5):
    px = px0
    while text_w(nm, ANTON, px, track) > maxw and px > floor:
        px -= 0.25
    return px


def render_base(spec, nowords=False, R=4.0, seed=0):
    """the card art (normal state, full value), RGBA at R px per design px"""
    cv = Cv(R)
    X, Y = cv.grid()
    A = ART[spec['name']]
    fam = spec['fam']; T = TYPES[fam]
    disc, mis = hx(A['disc']), hx(A['mis'])
    cm = poly(cv, SHAPE)
    # drop + ink border + paper
    drop = extrude(cv, cm, 5.0, 6.0)
    cv.paint(drop * (1 - grow(cv, cm, 2.6)), hx('78105C'))
    cv.paint(grow(cv, cm, 2.7), INK)
    cv.paint(cm, CREAM)
    # WPAP paper facets: two flat planes on the cream (lower right shade, lower left type-colour corner)
    cv.paint(poly(cv, [(CW, 160), (CW, CH), (96, CH)]) * cm, CREAM_D)
    cv.paint(poly(cv, [(0, 200), (0, CH - CH_), (CH_, CH), (52, CH)]) * cm, T['col'])
    cv.paint(poly(cv, [(0, 200), (0, CH - CH_), (CH_, CH), (52, CH)]) * cm * 0, INK)
    # ---------------- art band
    ab = poly(cv, BAND) * cm
    cv.paint(grow(cv, ab, 2.0), INK)
    # keep paper edge outside the ink: redraw cream under the ink ring is not needed (ink ring is the band keyline)
    BGS[A['style']](cv, ab, A, X, Y)
    facets(cv, ab, A, X, Y)
    cx, cy = IC
    # ---------------- the xerox icon, recoloured
    # scissor-cut bone halo, black key ring, spot disc, second ink misprinted
    halo = circle(cv, cx, cy, 39.6)
    if A['style'] == 'linocut':
        halo = circle(cv, cx, cy, 38.4)
    cv.paint(extrude(cv, halo, 2.6, 3.2) * ab, INK, 0.9)
    cv.paint(halo * ab, WHITE)
    ring = circle(cv, cx, cy, 36.6)
    cv.paint(ring * ab, INK)
    dsc = circle(cv, cx, cy, 34.2)
    cv.paint(dsc * ab, disc)
    mp = shift(cv, dsc, -4.2, 3.4) * (1 - shift(cv, dsc, 0, 0))
    cv.paint(mp * dsc * 0, mis)
    mp2 = shift(cv, dsc, -4.2, 3.4)
    cv.paint(np.clip(mp2 - 0.0, 0, 1) * dsc * 0.0, mis)
    # misprint crescent (second ink, inside the disc, lower left) + halftone on it
    cres = np.clip(dsc - shift(cv, dsc, 6.0, -5.0), 0, 1) * dsc
    cv.paint(cres, mis, 0.92)
    cv.paint(halftone(cv, np.clip(cres, 0, 1) * 0.5, 3.6, 45) * cres * (lum(mis) < 0.3) , WHITE, 0.0)
    gm = glyph(cv, spec["g"], 56, cx, cy)
    gm = np.clip((gm - 0.5) * 3 + 0.5, 0, 1)
    cv.paint(extrude(cv, grow(cv, gm, 2.5), 3.2, 3.6) * dsc, INK)
    cv.paint(grow(cv, gm, 2.5) * dsc, INK)
    cv.paint(gm * dsc, WHITE)
    # multiplier plate (Nudge / Spin 2 / Spin 3)
    if spec.get('mult'):
        pm = poly(cv, [(112, 94), (162, 90), (164, 120), (114, 124)])
        cv.paint(extrude(cv, grow(cv, pm, 2.0), 2.2, 2.6) * ab, INK)
        cv.paint(grow(cv, pm, 2.0) * ab, INK)
        cv.paint(pm * ab, T['col'])
        if nowords:
            for k in range(int(spec['mult'])):
                cv.paint(stroke(cv, [(122 + k * 11, 98), (123 + k * 11, 118)], 4.2) * ab, INK)
        else:
            m = text(cv, '\u00d7' + spec['mult'], 139, 107, 30, ANTON, 0.5, 0.0, -3)
            cv.paint(m, INK)
    # ---------------- title: a slanted ink plate, white title, black keyline, hard offset drop
    tb = poly(cv, [(0, 130), (CW, 124), (CW, 160), (0, 166)]) * cm
    cv.paint(extrude(cv, tb, 0, 3.0) * (1 - tb) * cm, hx('78105C'))
    cv.paint(tb, INK)
    cv.paint(poly(cv, [(0, 130), (CW, 124), (CW, 127), (0, 133)]) * cm, T['col'])   # type colour runs the top edge of the plate
    nm = spec['nm']
    px = _fit_title(nm)
    if nowords:
        cv.paint(poly(cv, [(30, 140), (CW - 30, 136), (CW - 30, 152), (30, 156)]) * cm, WHITE)
    else:
        m = text(cv, nm, 87.5, 144.5, px, ANTON, 1.0, 0.0, -2.0)
        cv.paint(shift(cv, m, 2.6, 3.0), PINK)
        cv.paint(grow(cv, m, 1.4), INK)      # the keyline: INK on the ink plate, white fill inside it
        cv.paint(m, WHITE)
    # ---------------- type plate (the colour behind WAVE / TOWER)
    tw = 92 if fam == 'TOWER' else 80
    ty = 174.0
    pl = poly(cv, [(88 - tw / 2 - 5, ty - 11), (88 + tw / 2 + 5, ty - 12.5), (88 + tw / 2 - 3, ty + 11), (88 - tw / 2 - 11, ty + 12.5)])
    cv.paint(extrude(cv, grow(cv, pl, 1.6), 2.2, 2.8), INK)
    cv.paint(grow(cv, pl, 1.6), INK)
    cv.paint(pl, T['col'])
    cv.paint(poly(cv, [(88 - tw / 2 - 11, ty + 12.5), (88 + tw / 2 - 3, ty + 11), (88 + tw / 2 - 4, ty + 6), (88 - tw / 2 - 10, ty + 7.5)]), T['dk'], 0.0)
    if nowords:
        cv.paint(poly(cv, [(88 - tw / 2 + 6, ty - 3), (88 + tw / 2 - 8, ty - 4), (88 + tw / 2 - 8, ty + 4), (88 - tw / 2 + 6, ty + 5)]), INK)
    else:
        m = text(cv, fam, 85.5, ty + 0.4, 19, ANTON, 2.2, 0.0, -1.2)
        cv.paint(m, T['text'])
    # ---------------- rules text
    txt = spec['txt']
    pxr = 21.0
    while text_w(txt, PLEX, pxr) > 120 and pxr > 15:
        pxr -= 0.5
    ly = 206.0
    wt = text_w(txt, PLEX, pxr)
    if nowords:
        bw = wt
        cv.paint(poly(cv, [(80 - bw / 2, ly - 4), (80 + bw / 2, ly - 5), (80 + bw / 2, ly + 5), (80 - bw / 2, ly + 6)]) * cm, INK)
    else:
        bar = poly(cv, [(80 - wt / 2 - 4, ly + 13.5), (80 + wt / 2 + 6, ly + 11.5), (80 + wt / 2 + 4, ly + 16.5), (80 - wt / 2 - 6, ly + 18.5)])
        cv.paint(bar * cm, PINK)
        m = text(cv, txt, 80, ly, pxr, PLEX, 0.0, 0.0, -0.8)
        cv.paint(m, INK)
    # ---------------- owner mark: three flat pink-family triangles bottom right
    bx, by = CW - 26, CH - 17
    for k, (cc, d) in enumerate(((PINK, (-9, 5)), (hx('FF8AD0'), (0, -6)), (hx('9A2AFF'), (9, 5)))):
        t2 = poly(cv, [(bx + d[0] - 7, by + d[1] + 6), (bx + d[0] + 7, by + d[1] + 6), (bx + d[0], by + d[1] - 8)])
        cv.paint(grow(cv, t2, 1.2) * cm, INK)
        cv.paint(t2 * cm, cc)
    # ---------------- cost badge: cyan hexagon (RAM)
    hx_, hy_ = 21, 21
    hexa = [(hx_ + 19 * math.cos(math.radians(30 + 60 * k)), hy_ + 19 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    hm = poly(cv, hexa)
    cv.paint(extrude(cv, grow(cv, hm, 2.0), 2.4, 3.0), INK)
    cv.paint(grow(cv, hm, 2.2), INK)
    cv.paint(hm, CYAN_COIN)
    up = poly(cv, [(hx_ - 19, hy_ - 12), (hx_ + 8, hy_ - 19), (hx_ + 19, hy_ - 10), (hx_ + 1, hy_ + 2), (hx_ - 19, hy_ + 9)]) * hm
    cv.paint(up, CYAN_HI)
    if nowords:
        c = int(spec['cost'])
        if c == 0:
            cv.paint(circle(cv, hx_, hy_ + 1, 3.0), INK)
        for q in range(c):
            xq = hx_ + (q - (c - 1) / 2) * 7.0
            cv.paint(stroke(cv, [(xq, hy_ - 8), (xq + 0.4, hy_ + 9)], 3.2), INK)
    else:
        cv.paint(text(cv, str(spec['cost']), hx_ + 0.5, hy_ + 1.2, 27, ANTON), INK)
    # ---------------- loud tab (+N Trace): violet eye plate, top right
    if spec['loud']:
        lx, ly2 = CW - 54, 17
        bxp = poly(cv, [(lx - 21, ly2 - 12), (lx + 18, ly2 - 14), (lx + 22, ly2 + 12), (lx - 18, ly2 + 14)])
        cv.paint(extrude(cv, grow(cv, bxp, 2.4), 2.2, 2.8), INK)
        cv.paint(grow(cv, bxp, 2.4), INK)
        cv.paint(bxp, hx('A03CFF'))
        e2 = poly(cv, [(lx - 17, ly2), (lx - 9, ly2 - 5.5), (lx - 1, ly2), (lx - 9, ly2 + 5.5)])
        cv.paint(e2, WHITE)
        cv.paint(circle(cv, lx - 9, ly2, 2.9), INK)
        if nowords:
            for q in range(int(spec['loud'])):
                cv.paint(stroke(cv, [(lx + 6 + q * 7, ly2 - 7), (lx + 7 + q * 7, ly2 + 8)], 3.0), WHITE)
        else:
            cv.paint(text(cv, '+' + str(spec['loud']), lx + 11, ly2 + 0.6, 21, ANTON), WHITE)
    return cv


# ------------------------------------------------------------------ states
_BASE = {}


def _spec(card):
    if isinstance(card, str):
        s = dict(CARDS[card]); s['name'] = card
    else:
        s = dict(CARDS[card['name']]); s.update(card)
    return s


def margin_px(size):
    w = size[0] if isinstance(size, (tuple, list)) else size
    return int(round(MARGIN * w / CW))


def _post_dim(im, k):
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def _unaffordable(im):
    """dim glass: value x0.5, chroma x0.4, two flat glass planes; the cost badge keeps its colour (it is the reason)"""
    a = np.asarray(im).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3:]
    g = rgb.mean(-1, keepdims=True)
    rgb = (g + (rgb - g) * 0.40) * 0.55 + np.array([8, 6, 14], np.float32) * 0.45
    H, W = al.shape[:2]
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (x + y * 0.55) / W
    gl = ((u > 0.42) & (u < 0.62)).astype(np.float32) * 0.10 + ((u > 0.70) & (u < 0.76)).astype(np.float32) * 0.08
    rgb = rgb + gl[..., None] * (255 - rgb)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), 'RGBA')


def _liner(R, nowords, spec):
    cv = Cv(R)
    cm = poly(cv, SHAPE)
    ln = np.clip(grow(cv, cm, 1.5) - cm, 0, 1)
    col = hx('A0AFC8')
    cv.paint(ln, col, 0.9)
    gm = glyph(cv, spec['g'], 54, CW / 2, CH / 2 - 8)
    cv.paint(gm, hx('7A88A2'), 0.8)
    if not nowords:
        cv.paint(text(cv, 'PLAYED', CW / 2, CH / 2 + 40, 17, MONO, 1.5), col, 0.9)
    return cv.img()


def draw_card(card, size, state='normal'):
    spec = _spec(card)
    if isinstance(state, str):
        state = dict(mode=state)
    mode = state.get('mode', 'normal')
    nowords = bool(state.get('nowords')) or mode == 'nowords'
    w = size[0] if isinstance(size, (tuple, list)) else size
    s = w / CW
    ss = 3 if s <= 1.5 else 2
    R = s * ss
    ck = (spec['name'], nowords, round(R, 3), json.dumps({k: spec[k] for k in ('cost', 'loud', 'txt', 'nm', 'fam')}))
    if mode == 'played':
        im = _liner(R, nowords, spec)
    else:
        if ck not in _BASE:
            if len(_BASE) > 40:
                _BASE.clear()
            _BASE[ck] = render_base(spec, nowords, R).img()
        im = _BASE[ck].copy()
        if mode == 'hover':
            # pink misregistered print behind the lifted card (silhouette incl. its drop), hard longer drop under it
            a = np.asarray(im)[..., 3].astype(np.float32) / 255.0
            sil = (a > 0.5).astype(np.float32)
            pk = ndi.shift(sil, (6 * R, -9 * R), order=0)
            sh = ndi.shift(sil, (11 * R, 7 * R), order=0)
            H, W = sil.shape
            base = np.zeros((H, W, 4), np.float32)
            base[..., :3] = np.array([8, 6, 14])
            base[..., 3] = sh * 0.55 * 255
            pkl = np.zeros((H, W, 4), np.float32); pkl[..., :3] = np.array([255, 61, 168]); pkl[..., 3] = pk * 255
            comp = Image.fromarray(base.astype(np.uint8), 'RGBA')
            comp.alpha_composite(Image.fromarray(pkl.astype(np.uint8), 'RGBA'))
            comp.alpha_composite(im)
            im = comp
        elif mode == 'unaffordable':
            im = _unaffordable(im)
        elif state.get('dim'):
            im = _post_dim(im, float(state['dim']))
    out_w = int(round((CW + 2 * MARGIN) * s)); out_h = int(round((CH + 2 * MARGIN) * s))
    if mode == 'played':
        im = im.resize((out_w, out_h), Image.LANCZOS)
    else:
        im = im.resize((out_w, out_h), Image.LANCZOS)
    if not isinstance(size, (tuple, list)):
        pass
    return im


if __name__ == '__main__':
    out = 'D:/rc_scratch/combat_redesign/locked/cards/work/'
    names = sys.argv[1:] or ORDER
    for n in names:
        draw_card(n, 176 * 2).save(out + 'one_%s.png' % n)
