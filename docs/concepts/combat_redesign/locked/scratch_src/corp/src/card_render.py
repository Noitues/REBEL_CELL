"""card_render: the REBEL_CELL card system, locked style (ART CALL 53).

    draw_card(card, size, state) -> PIL RGBA

WPAP card (chamfered die-cut, flat facet planes, slanted plates, hard offset drops) with
  * a type plate whose colour is the card TYPE (TOWER = deep teal #006E66 + white word, WAVE = lilac #B4AAFF + ink word; 2026-11-03),
  * a band background in one of the other punk styles (linocut, Ben-Day, collage, Jinx, mural, xerox),
  * the xerox icon (paper-white glyph, black key line + hard drop, spot-ink disc, misregistered second ink) recoloured per card,
  * the black-book layout (see card_titles/LAYOUT.md) and the title rule (neutral fill, hard keyline, cap >= 26 design px).

card   a name from CARDS ('Brace', 'Spin3', ...) or a dict {'name':..., plus any override: cost, loud, txt, nm, fam}
size   (w, h) of the CARD box in output px, or one number = the width (height follows 176:250).
       The returned image is the card box plus MARGIN design px each side (MARGIN * size / 176 px), so drops, the lift print and
       the chamfer shadow are never cut.  Use margin_px(size) to place it: centre of the card = centre of the image.
state  'normal' | 'hover' | 'played' | 'unaffordable' (dim glass + padlock on the cost + NO RAM tab) | 'nowords'  or a dict
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

TYPES = {   # the card TYPE colours (the word on the plate).  2026-11-03 rebuild (AD review 2.2, DR-5 / DR-8): one hue per type,
            # each at CIE76 dE >= 15 from every meaning token (SOAK, SCHEDULE, BOSS_GOLD, TRACE, NET_CYAN, HARM, GAIN, PLAN) and every
            # slice ink; TOWER and WAVE also split by value (dark plate + white word vs light plate + ink word).  Table: rebuild/cards/de.json
    'TOWER': dict(col=hx('006E66'), dk=hx('00403B'), text=WHITE),     # deep teal, white word 5.87:1
    'WAVE':  dict(col=hx('B4AAFF'), dk=hx('5E50C4'), text=INK),       # lilac, ink word 8.94:1
}
TRACE_VIOLET = hx('A03CFF')      # the +Trace tab keeps the HUD Trace violet: violet means Trace only

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
    'Nudge':    dict(style='benday',  bg='3BB8F2', dot='1B4FB8', hi='E8F8FF', disc='1A1250', mis='FFC83A', arcs=1, dot_k=0.55, seed=11),
    'Spin2':    dict(style='benday',  bg='44D9A6', dot='0B5A44', hi='EFFFF8', disc='2A1C8E', mis='FF3DA8', arcs=2, dot_k=0.85, seed=12),
    'Spin3':    dict(style='benday',  bg='FF00F0', dot='4A0846', hi='FFE6FB', disc='1A1250', mis='1AA6E8', arcs=3, dot_k=1.15, seed=13),   # 2026-11-03: magenta, off BOSS_GOLD / TURRET
    'Brace':    dict(style='linocut', bg='2848D8', key='101018', bone='F1EAD6', disc='15121A', mis='FF3DA8', dirn='radial', seed=14),
    'Strike':   dict(style='collage', bg='C9F23C', paper=['F1EAD6', '15121A', '2A4BE0', 'C9F23C'], disc='15121A', mis='FF3DA8', seed=15),
    'Firewall': dict(style='mural',   motif='fire', sky=['2A0612', '5C0A1E', '9E1F1A', 'E8551F'], city='1A0508', flame=['FF7A1A', 'FFC93A', 'FFF2C2'], disc='15121A', mis='FF3DA8', seed=16),
    'Pull':     dict(style='linocut', bg='18A872', key='0B1A14', bone='F1EAD6', disc='15121A', mis='FF3DA8', dirn='down', seed=17),
    'Shove':    dict(style='collage', bg='F1EAD6', paper=['2A4BE0', 'F1EAD6', '15121A', '9BD0FF'], disc='15121A', mis='FF3DA8', slide=True, seed=18),
    'Twist':    dict(style='mural',   motif='rings', sky=['0B2A45', '0E4A63', '137489', '2BA9A5'], ring='8FE3D2', turn='FBFAF4', disc='15121A', mis='FFB347', seed=19),
    'Hold':     dict(style='xerox',   bg='15121A', dot='F2EEE4', spot='12A9E6', disc='FF3DA8', mis='12A9E6', seed=20),
    'Trigger':  dict(style='jinx',    bg='160B2E', neon=['27D3F5', 'FF3DA8'], disc='FF3DA8', mis='C8FF3C', seed=21),
}
STYLE_WHY = {
    'benday': 'Ben-Day dots + speed arcs: the Spin family turns the tower, the arcs count the turns (1, 2, 3)',
    'linocut': 'carved black key on one flat plate: hard, solid, protective (Brace) and straight-down gouges (Pull)',
    'collage': 'torn paper shards and tape: impact (Strike) and sliding strips (Shove)',
    'mural': 'spray mural, one motif per card: a brick wall on fire (Firewall, burn) and three ring bands with the middle one turned (Twist, turn one ring)',
    'xerox': 'black toner and a halftone dot field: dead copier stillness for Hold (the icon is a clamp on a ring step)',
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


def _layered(cv, pieces, cut=1.5):
    """union of glyph pieces, each later piece cut from the earlier ones by a `cut` design-px gap (the ink shows in the gap)"""
    m = np.zeros((cv.H, cv.W), np.float32)
    for p in pieces:
        m = m * (1 - np.clip(grow(cv, p, cut), 0, 1))
        m = np.maximum(m, p)
    return m


def glyph_hold(cv, px, x, y):
    """HOLD (2026-11-03, AD review 3.1): a C-clamp gripping one ring step, not a pause button.
    Three curved ring cells (a piece of the wave ring), the middle one held by a C-clamp: T-handle, screw, pad pressing the cell,
    the frame's spine and lower jaw.  Built from solid shapes; the cut gaps between pieces show the ink."""
    s = px / 64.0
    ou, ov = 1.0, 0.0
    P = lambda u, v: (x + (u + ou) * s, y + (v + ov) * s)
    def rect(u0, v0, u1, v1):
        return poly(cv, [P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)])
    # the ring step: two curved cells of a ring (its centre far below); the left one sits in the clamp's mouth
    rc = (4.0, 84.0); r0, r1 = 64.0, 76.0
    cells = []
    for (a0, a1) in ((-15.0, -1.8), (1.8, 17.0)):
        pts = [P(rc[0] + r1 * math.sin(math.radians(a0 + (a1 - a0) * t / 12)), rc[1] - r1 * math.cos(math.radians(a0 + (a1 - a0) * t / 12))) for t in range(13)]
        pts += [P(rc[0] + r0 * math.sin(math.radians(a1 - (a1 - a0) * t / 12)), rc[1] - r0 * math.cos(math.radians(a1 - (a1 - a0) * t / 12))) for t in range(13)]
        cells.append(_mask(cv, lambda d, q=[cv.p(*p) for p in pts]: d.polygon(q, fill=255)))
    # the C-clamp: back on the left, upper and lower arms, the screw down through the upper arm onto a pad on the cell
    frame = np.maximum.reduce([rect(-28, -18, 9, -11),            # upper arm
                               rect(-28, -18, -21, 30),           # back
                               rect(-28, 24, 9, 30)])             # lower arm (the fixed jaw, under the cell)
    screw = rect(-9.0, -27, -4.0, 4.0)
    pad = rect(-14.5, 3.0, 1.5, 8.5)
    handle = rect(-17.5, -31, 4.5, -25.5)
    return _layered(cv, cells + [frame, screw, pad, handle], 1.6)


PROC_GLYPHS = {'C_HOLD': glyph_hold}

_GL = {}
def glyph(cv, name, px, x, y):
    if name in PROC_GLYPHS:
        return PROC_GLYPHS[name](cv, px, x, y)
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
    dk = A.get('dot_k', 1.0)                       # O-29 fix 7: the dot screen gets denser with the turn count (Nudge < Spin 2 < Spin 3)
    cv.paint(halftone(cv, np.clip(cov * dk, 0, 1), 8.5, 45) * ab, dot)
    cov2 = np.clip(1.0 - (Y - 8) / 100.0, 0, 1) * 0.5 * np.clip((rr - 38) / 18.0, 0, 1) * (2.0 - dk)
    cv.paint(halftone(cv, np.clip(cov2, 0, 1), 8.5, 45, 4.2, 4.2) * ab, hi)
    # (the speed arcs are drawn by spin_arcs() after the WPAP facets, so the facets never wash them out)
    # two lightning bolts (white, ink keyline), off the icon
    def bolt(x, y, s, rot):
        base = [(0, -10), (5, -10), (1, -1), (7, -1), (-4, 12), (-1, 2), (-7, 2)]
        c, sn = math.cos(rot), math.sin(rot)
        return [(x + s * (px * c - py * sn), y + s * (px * sn + py * c)) for px, py in base]
    for (bx, by, s, rt) in ((22, 106, 1.15, -0.25), (154, 24, 1.0, 0.28)):
        m = poly(cv, bolt(bx, by, s, rt))
        cv.paint(grow(cv, m, 1.6) * ab, INK)
        cv.paint(m * ab, hi)


def spin_arcs(cv, ab, A):
    """speed arcs on the Spin family: arc count = turns (1, 2, 3).  O-29 fix 7: concentric solid ink strokes 3.4 design px
    (3.7-3.9 px on screen) with a paper keyline and an arrow head each, 13 design px apart (clear gap >= 10 px on screen)."""
    cx, cy = IC
    for k in range(A.get('arcs', 0)):
        rad = 46.0 + 13.0 * k
        a0 = math.radians(196)
        a1 = math.radians(262 - 4 * k)
        pts = [(cx + rad * math.cos(a0 + (a1 - a0) * t / 30), cy + rad * math.sin(a0 + (a1 - a0) * t / 30)) for t in range(31)]
        st = stroke(cv, pts, 3.4)
        ex, ey = pts[-1]
        tx, ty = -math.sin(a1), math.cos(a1)
        nx, ny = math.cos(a1), math.sin(a1)
        hd = poly(cv, [(ex + tx * 8.0, ey + ty * 8.0), (ex + nx * 5.6, ey + ny * 5.6), (ex - nx * 5.6, ey - ny * 5.6)])
        m = np.maximum(st, hd)
        cv.paint(grow(cv, m, 1.4) * ab, WHITE)
        cv.paint(m * ab, INK)


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


def _mural_sky(cv, ab, A):
    """stepped spray sky (flat bands, hand-cut edges): the shared mural ground"""
    sky = [hx(c) for c in A['sky']]
    n = len(sky)
    cv.paint(ab, sky[0])
    for i in range(1, n):
        y0 = 8 + (118) * i / n
        pts = [(8, y0 + 4), (CW - 8, y0 - 6), (CW - 8, 126), (8, 126)]
        m = poly(cv, jag(cv, pts, 1.1, A['seed'] + i, 6))
        cv.paint(m * ab, sky[i])
    return sky


def _mural_fire(cv, ab, A, X, Y):
    """Firewall (2026-11-03, AD review 3.2): a brick wall on fire.  Flame tongues rise from behind the wall top, the wall is
    flat-cut bricks with dark mortar, two tongues lick over the bricks, spray drips run off the wall."""
    r = np.random.default_rng(A['seed'])
    sky = _mural_sky(cv, ab, A)
    fl = [hx(c) for c in A['flame']]
    wall_top = 96.0
    # the blaze behind the icon: a flat spray disc in the flame orange, then a pale ring (keeps the ink disc >= 2.5:1 against its art)
    cx, cy = IC
    cv.paint(circle(cv, cx, cy, 56.0) * ab, fl[0])
    cv.paint(np.clip(circle(cv, cx, cy, 49.0) - circle(cv, cx, cy, 44.5), 0, 1) * ab, fl[1])
    # three flame layers, back (orange) to front (pale), each a row of jagged tongues
    for k, (col, h0, h1, w) in enumerate(((fl[0], 34, 70, 26), (fl[1], 22, 48, 20), (fl[2], 10, 26, 14))):
        x = 8 - r.uniform(0, w / 2)
        pts = [(8, wall_top + 2)]
        while x < CW - 8 + w:
            h = r.uniform(h0, h1)
            pts += [(x, wall_top - r.uniform(2, 8)), (x + w * 0.5 + r.uniform(-3, 3), wall_top - h), (x + w, wall_top - r.uniform(2, 8))]
            x += w * r.uniform(0.8, 1.1)
        pts += [(CW - 8, wall_top + 2)]
        m = poly(cv, pts)
        cv.paint(grow(cv, m, 1.0) * ab, hx('1A0508'), 0.85)
        cv.paint(m * ab, col)
    # the wall: flat bricks, staggered rows, dark mortar between (no outline dashes: each brick is a solid cut shape)
    brick = hx('8E2A1C'); brick2 = hx('6E1E16'); mortar = hx(A['city'])
    cv.paint(poly(cv, [(8, wall_top), (CW - 8, wall_top - 2), (CW - 8, 126), (8, 126)]) * ab, mortar)
    bh, bw = 9.0, 21.0
    row = 0
    yb = wall_top + 1.6
    while yb < 126:
        off = (bw / 2) * (row % 2) - r.uniform(0, 3)
        xb = 8 - bw + off
        while xb < CW - 8:
            col = brick if r.random() < 0.6 else brick2
            pts = [(xb + 1.0, yb + 0.9), (xb + bw - 1.0, yb + 0.7), (xb + bw - 0.8, yb + bh - 0.9), (xb + 0.8, yb + bh - 0.8)]
            cv.paint(poly(cv, pts) * ab, col)
            xb += bw
        yb += bh; row += 1
    # two tongues licking over the bricks
    for (fx, fw, fh) in ((30, 16, 22), (140, 14, 18)):
        m = poly(cv, jag(cv, [(fx - fw / 2, 126), (fx - fw / 4, wall_top + 2), (fx, wall_top - fh), (fx + fw / 3, wall_top + 4), (fx + fw / 2, 126)], 0.8, A['seed'] + int(fx), 4))
        cv.paint(grow(cv, m, 1.0) * ab, hx('1A0508'))
        cv.paint(m * ab, fl[1])
    # spray drips off the wall top
    for dx in (58, 104, 122):
        st = stroke(cv, [(dx, wall_top + 1), (dx, wall_top + r.uniform(9, 18))], 2.6)
        cv.paint(st * ab, fl[2], 0.85)


def _mural_rings(cv, ab, A, X, Y):
    """Twist (2026-11-03, AD review 3.2): three spray-painted ring bands round the icon, cut into cells; the middle band is turned
    half a cell against the other two (its cell gaps do not line up) and carries an arrow head: one ring turned."""
    r = np.random.default_rng(A['seed'])
    sky = _mural_sky(cv, ab, A)
    cx, cy = IC
    rr = np.hypot(X - cx, Y - cy)
    ang = (np.degrees(np.arctan2(X - cx, -(Y - cy))) + 360) % 360       # 0 = 12 o'clock, clockwise
    cellw, gap = 30.0, 3.2
    ringc, turnc = hx(A['ring']), hx(A['turn'])
    for k, (r0, r1, rot, col) in enumerate(((43.5, 52.0, 0.0, ringc), (55.0, 64.5, cellw / 2 + 4.0, turnc), (67.5, 77.0, 0.0, ringc))):
        band = ((rr >= r0) & (rr < r1)).astype(np.float32)
        a = (ang - rot) % cellw
        gpx = np.degrees(gap / ((r0 + r1) / 2))           # the gap is a constant width in px
        cells = band * (a > gpx).astype(np.float32)
        cv.paint(np.clip(grow(cv, cells, 1.1), 0, 1) * band * ab * 0, INK)
        cv.paint(cells * ab, hx('06121E'), 0.9)            # ink under-print, then the ink, offset: spray layer
        cv.paint(shift(cv, cells, -1.0, -1.0) * ab, col)
    # arrow heads on the turned band (clockwise), at 2 and 8 o'clock
    for a0 in (62.0, 242.0):
        rm = 59.75
        a = math.radians(a0)
        tx, ty = math.cos(a), math.sin(a)                   # clockwise tangent in screen coords for angle-from-12
        px_, py_ = cx + rm * math.sin(a), cy - rm * math.cos(a)
        nx, ny = math.sin(a), -math.cos(a)
        hd = poly(cv, [(px_ + tx * 11, py_ + ty * 11), (px_ + nx * 9, py_ + ny * 9), (px_ - nx * 9, py_ - ny * 9)])
        cv.paint(grow(cv, hd, 1.3) * ab, INK)
        cv.paint(hd * ab, turnc)
    # spray stars in the corners
    for (sx, sy, s_) in ((20, 18, 4.5), (160, 112, 4.0), (156, 20, 3.4), (18, 110, 3.6)):
        pts = []
        for q in range(8):
            rad_ = s_ if q % 2 == 0 else s_ * 0.3
            a = math.pi / 4 * q
            pts.append((sx + rad_ * math.cos(a), sy + rad_ * math.sin(a)))
        cv.paint(poly(cv, pts) * ab, turnc, 0.9)


def bg_mural(cv, ab, A, X, Y):
    if A.get('motif') == 'fire':
        return _mural_fire(cv, ab, A, X, Y)
    if A.get('motif') == 'rings':
        return _mural_rings(cv, ab, A, X, Y)
    r = np.random.default_rng(A['seed'])
    sky = _mural_sky(cv, ab, A)
    n = len(sky)
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
    # O-29 fix 8: a black toner pool round the icon (the spot block stops short of the halo) so the pink disc reads >= 2.5:1
    cv.paint(np.clip((52.0 - rr) / 3.0, 0, 1) * ab, bg)
    # toner speckle
    sp = (r.random((cv.H, cv.W)) > 0.9985).astype(np.float32)
    sp = ndi.maximum_filter(sp, size=max(2, int(cv.R * 0.6)))
    cv.paint(sp * ab, dot, 0.8)
    # copier edge: a hard dot-white band at the very bottom
    cv.paint(poly(cv, [(8, 119), (CW - 8, 114), (CW - 8, 126), (8, 126)]) * ab, dot)


BGS = dict(benday=bg_benday, linocut=bg_linocut, collage=bg_collage, jinx=bg_jinx, mural=bg_mural, xerox=bg_xerox)


FACET_OP = (0.32, 0.28, 0.25)      # O-29 fix 6: type-colour plane, type-dark plane, glint (all inside 25-35 percent)


def facets(cv, ab, A, X, Y, T=None):
    """WPAP: flat translucent planes cut across the art band, tinted in the card's TYPE colour (O-29 fix 6):
    lit planes = type colour at 32 percent, shade planes = the type's dark at 28 percent, one white glint plane at 25 percent.
    Each plane has a hard ink hairline on its cut edge so it reads as a WPAP facet, not as a glow."""
    if T is None:
        return _facets_old(cv, ab, A, X, Y)
    r = np.random.default_rng(A['seed'] * 7 + 3)
    x0, y0, x1, y1 = 8, 8, CW - 8, 126
    def edge_pt(s):
        if s == 0: return (r.uniform(x0, x1), y0)
        if s == 1: return (x1, r.uniform(y0, y1))
        if s == 2: return (r.uniform(x0, x1), y1)
        return (x0, r.uniform(y0, y1))
    sides = [(0, 3), (1, 2), (3, 2), (0, 1)]
    for i in range(4):
        sa, sb = sides[i]
        a, b = edge_pt(sa), edge_pt(sb)
        c = (r.uniform(x0 + 30, x1 - 30), r.uniform(y0 + 25, y1 - 25))
        m = poly(cv, [a, b, c]) * ab
        col, op = (T['col'], FACET_OP[0]) if i % 2 == 0 else (T['dk'], FACET_OP[1])
        cv.paint(m, col, op)
        edge = np.clip(grow(cv, m, 0.7) - m, 0, 1) * ab
        cv.paint(edge, INK, 0.55)
    g = poly(cv, [(x0, y0), (x0 + 58, y0), (x0 + 20, y0 + 40), (x0, y0 + 56)]) * ab
    cv.paint(g, WHITE, FACET_OP[2])


def _facets_old(cv, ab, A, X, Y):
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
COST_C = (21.0, 21.0)


def cost_badge(cv, spec, nowords):
    """the cost: cyan RAM hexagon with the digit (or a tally in nowords)"""
    hx_, hy_ = COST_C
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


def lock_glyph(cv, x, y, s=1.0):
    """padlock: bone body with a keyhole, ink shackle, ink keyline + hard drop.  (x, y) = body centre, s = scale (body 15 x 12)"""
    body = poly(cv, [(x - 7.5 * s, y - 5.5 * s), (x + 7.5 * s, y - 5.5 * s), (x + 7.5 * s, y + 6.5 * s), (x - 7.5 * s, y + 6.5 * s)])
    sh = np.zeros_like(body)
    pts = [(x + 4.6 * s * math.cos(math.radians(a)), y - 5.5 * s - 5.6 * s * math.sin(math.radians(a))) for a in range(0, 181, 10)]
    sh = stroke(cv, [(x + 4.6 * s, y - 4.0 * s)] + pts + [(x - 4.6 * s, y - 4.0 * s)], 3.0 * s, cap=False)
    allm = np.maximum(body, sh)
    cv.paint(extrude(cv, grow(cv, allm, 1.6), 1.8, 2.2), INK)
    cv.paint(grow(cv, allm, 1.6), INK)
    cv.paint(sh * (1 - body), hx('C9C2B0'))
    cv.paint(body, WHITE)
    kh = np.maximum(circle(cv, x, y - 0.4 * s, 2.0 * s), poly(cv, [(x - 1.0 * s, y), (x + 1.0 * s, y), (x + 1.5 * s, y + 4.0 * s), (x - 1.5 * s, y + 4.0 * s)]))
    cv.paint(kh, INK)


NO_RAM = 'NO RAM'
NO_RAM_PX = 17.0                           # 2026-11-03 stage 2: Anton 17 x 1.10 = 16.1 px cap (was 15.5 = 14.7 px)
NO_RAM_TRACK = -0.5
NO_RAM_TAB = (32.0, 92.5, 10.0, 30.0)      # x0, x1, y0, y1 (design px); the plate slants 2 px to the right at the bottom
NO_RAM_VIS_X0 = 42.5                       # the badge (with its keyline) covers the tab left of this


def no_ram_cx():
    return (NO_RAM_VIS_X0 + NO_RAM_TAB[1]) / 2 - 0.3


def unaffordable_marks(R, spec, nowords):
    """AD review 3.3 (2026-11-03): the unaffordable state is told by marks, not only by the dim glass.  Drawn at full value over the
    dimmed card: the cost badge again (it is the reason), a padlock on the badge's lower right, and a 'NO RAM' tab beside it
    (ink plate, RAM cyan word).  nowords: the lock only."""
    cv = Cv(R)
    if not nowords:
        # the tab runs out from under the cost badge (its left end is hidden by the badge) and stops short of the +Trace tab
        x0, x1, y0, y1 = NO_RAM_TAB
        tab = poly(cv, [(x0, y0 + 1.0), (x1, y0 - 1.0), (x1 + 2.0, y1 - 1.0), (x0 + 2.0, y1 + 1.0)])
        cv.paint(extrude(cv, grow(cv, tab, 1.8), 2.2, 2.8), INK)
        cv.paint(grow(cv, tab, 1.8), INK)
        cv.paint(tab, hx('1C1830'))
        cv.paint(text(cv, NO_RAM, no_ram_cx(), (y0 + y1) / 2, NO_RAM_PX, ANTON, NO_RAM_TRACK, 0.0, -1.5), CYAN_HI)
    cost_badge(cv, spec, nowords)
    lock_glyph(cv, COST_C[0] + 17.5, COST_C[1] + 21.0, 1.15)     # on the badge's lower-right edge, clear of the digit
    return cv.img()


# rules text (2026-11-03 stage 2, AD review check c): IBM Plex Sans Condensed Medium at 21 design px is a 16.2 px cap at the 1.10x hand scale
# (cap ratio 0.70).  It is never shrunk.  A text that is wider than RULES_FIT_W wraps at the word break that gives the narrowest longest
# line (Turn the / tower 3, Turn one / ring 1, Pause / the wave); one line sits at y 206 as before, two lines at y 200 / 221.5, clear of the
# type plate's drop above and the owner triangles (x >= 134, y >= 219) on the right.  The pink bar runs under the last line.
RULES_PX = 21.0
RULES_FIT_W = 124.0
RULES_CX = 80.0
RULES_LY1 = (206.0,)
RULES_LY2 = (200.0, 221.5)
RULES_BAR = {0: (11.5, 18.5), 1: (13.0, 20.0)}     # bar band under the last line (y offsets), one-line / two-line layout


def rules_lines(txt, px=RULES_PX):
    """[(line, y, width)] of a card's rules text in design px (one or two lines, centred at RULES_CX)"""
    w = text_w(txt, PLEX, px)
    if w <= RULES_FIT_W:
        return [(txt, RULES_LY1[0], w)]
    words = txt.split(' ')
    best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        m = max(text_w(a, PLEX, px), text_w(b, PLEX, px))
        if best is None or m < best[0]:
            best = (m, a, b)
    _, a, b = best
    return [(a, RULES_LY2[0], text_w(a, PLEX, px)), (b, RULES_LY2[1], text_w(b, PLEX, px))]


def rules_box(txt, px=RULES_PX):
    """the rules block's polygon in design px (text plus the pink bar), for the hand clearance check"""
    ls = rules_lines(txt, px)
    wmax = max(w for _, _, w in ls)
    y0 = ls[0][1] - px * 0.62
    y1 = ls[-1][1] + RULES_BAR[len(ls) - 1][1]
    return [(RULES_CX - wmax / 2 - 6, y0), (RULES_CX + wmax / 2 + 6, y0), (RULES_CX + wmax / 2 + 6, y1), (RULES_CX - wmax / 2 - 6, y1)]


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
    facets(cv, ab, A, X, Y, T)
    spin_arcs(cv, ab, A)
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
                cv.paint(stroke(cv, [(122 + k * 11, 98), (123 + k * 11, 118)], 4.2) * ab, T['text'])
        else:
            m = text(cv, '\u00d7' + spec['mult'], 139, 107, 30, ANTON, 0.5, 0.0, -3)
            cv.paint(m, T['text'])
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
    # ---------------- rules text (2026-11-03 stage 2: never shrunk below the 16 px cap floor; a long line wraps to two, rules_lines())
    lines = rules_lines(spec['txt'])
    cxr = RULES_CX
    for li, (s_, ly, wt) in enumerate(lines):
        last = li == len(lines) - 1
        if nowords:
            cv.paint(poly(cv, [(cxr - wt / 2, ly - 4), (cxr + wt / 2, ly - 5), (cxr + wt / 2, ly + 5), (cxr - wt / 2, ly + 6)]) * cm, INK)
            continue
        if last:
            b0, b1 = RULES_BAR[len(lines) - 1]
            bar = poly(cv, [(cxr - wt / 2 - 4, ly + b0 + 2.0), (cxr + wt / 2 + 6, ly + b0), (cxr + wt / 2 + 4, ly + b1 - 2.0), (cxr - wt / 2 - 6, ly + b1)])
            cv.paint(bar * cm, PINK)
        m = text(cv, s_, cxr, ly, RULES_PX, PLEX, 0.0, 0.0, -0.8)
        cv.paint(m, INK)
    # ---------------- owner mark: three flat pink-family triangles bottom right
    bx, by = CW - 26, CH - 17
    for k, (cc, d) in enumerate(((PINK, (-9, 5)), (hx('FF8AD0'), (0, -6)), (hx('9A2AFF'), (9, 5)))):
        t2 = poly(cv, [(bx + d[0] - 7, by + d[1] + 6), (bx + d[0] + 7, by + d[1] + 6), (bx + d[0], by + d[1] - 8)])
        cv.paint(grow(cv, t2, 1.2) * cm, INK)
        cv.paint(t2 * cm, cc)
    # ---------------- cost badge: cyan hexagon (RAM)
    cost_badge(cv, spec, nowords)
    # ---------------- loud tab (+N Trace): violet eye plate, top right
    if spec['loud']:
        lx, ly2 = CW - 54, 17
        bxp = poly(cv, [(lx - 21, ly2 - 12), (lx + 18, ly2 - 14), (lx + 22, ly2 + 12), (lx - 18, ly2 + 14)])
        cv.paint(extrude(cv, grow(cv, bxp, 2.4), 2.2, 2.8), INK)
        cv.paint(grow(cv, bxp, 2.4), INK)
        cv.paint(bxp, TRACE_VIOLET)
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
    """dim glass: value x0.5, chroma x0.4, two flat glass planes.  draw_card then lays unaffordable_marks() on top at full value
    (cost badge, padlock, NO RAM tab), so the state is told by a glyph and a word, not only by the dim."""
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


# played slot (2026-11-03 stage 2, AD review 2.3; VISUAL_PLAN B "played-card empty slot: torn-paper outline (P)"): the card leaves a flat
# torn-paper outline, drawn upright (the hand places it with no fan tilt), filled with a dark toner wash so a neighbouring slot's outline never
# shows through it (crossing outlines read as a wireframe cage).  P family: torn paper edge in PAPER, no vector hairline, no chamfer cage.
LINER_TEAR = 1.7            # design px, amplitude of the torn edge
LINER_RIM = 2.2             # design px, the paper rim
LINER_FILL = (hx('15121A'), 0.86)
LINER_PAPER_V = 0.62        # the rim's value (PAPER x this)
LINER_WORD_PX = 21.0        # Share Tech Mono 21 x 1.10 = 16.2 px cap
LINER_WORD_V = (0.62, 0.74)  # card name, PLAYED


def _liner(R, nowords, spec):
    cv = Cv(R)
    seed = sum(ord(c) for c in spec['name'])
    rect_ = [(3, 3), (CW - 3, 3), (CW - 3, CH - 3), (3, CH - 3)]
    torn = poly(cv, jag(cv, rect_, LINER_TEAR, seed, n=5))
    body =np.clip(1.0 - grow(cv, 1.0 - torn, LINER_RIM), 0, 1)          # the torn shape shrunk by the rim width
    cv.paint(torn, LINER_FILL[0], LINER_FILL[1])
    paper = np.array([0xF2, 0xEE, 0xE4], np.float32) / 255.0
    rim = np.clip(torn - body, 0, 1)
    cv.paint(rim, paper * LINER_PAPER_V)
    fib = np.clip(body - np.clip(1.0 - grow(cv, 1.0 - body, 1.0), 0, 1), 0, 1)                  # fibre edge just inside the tear
    cv.paint(fib * (halftone(cv, np.full_like(fib, 0.35), 2.6, 30) > 0.5), paper * LINER_PAPER_V, 0.55)
    gm = glyph(cv, spec['g'], 54, CW / 2, CH / 2 - 14)
    cv.paint(gm, paper * 0.46)
    if not nowords:
        # O-29 fix 4 kept: the played slot keeps the card name above PLAYED, mono small caps
        cv.paint(text(cv, spec['nm'], CW / 2, CH / 2 + 32, LINER_WORD_PX, MONO, 1.0), paper * LINER_WORD_V[0])
        cv.paint(text(cv, 'PLAYED', CW / 2, CH / 2 + 58, LINER_WORD_PX, MONO, 1.0), paper * LINER_WORD_V[1])
    return cv.img()


# the lifted card's pink misregistered print and hard drop, (down, right) in design px.  Round 1: print (6, -9) (down-left), drop (11, 7).
# 2026-11-04 round 2 (C6): rb_lift sets the print to the right so the straight-up lift adds nothing over its LEFT neighbour (the x3 plate and
# the title band of the card it rises out of) or the REFUND tab
HOVER_PRINT_OFF = [6, -9]
HOVER_DROP_OFF = [11, 7]


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
            pk = ndi.shift(sil, (HOVER_PRINT_OFF[0] * R, HOVER_PRINT_OFF[1] * R), order=0)
            sh = ndi.shift(sil, (HOVER_DROP_OFF[0] * R, HOVER_DROP_OFF[1] * R), order=0)
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
            im.alpha_composite(unaffordable_marks(R, spec, nowords))
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
