"""gramlib: grammar primitives for the combat redesign (line / time / HP / colour / wave).  Pure drawing helpers on cv_lib.L2 layers.
Nothing here edits the E10 generator; gram.py monkeypatches the E10 functions to call these."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import cv_lib
from cv_lib import C, ppx

# ---- tokens (VISUAL_PLAN E)
INK = (12, 10, 22)
PINK = (255, 61, 168)
HARM = (255, 68, 51)
HARM_UP = (255, 100, 82)
GAIN = (123, 224, 123)
SOAKC = (58, 126, 243)            # R51 review: back to #3A7EF3 (#464EFF fails protan vs Trace)
PLANY = (255, 226, 0)
SCHED = (255, 140, 26)
GOLD = (255, 196, 40)
CYAN = (92, 225, 255)
ENAMEL = (217, 225, 234)
CREAM = (255, 244, 214)
TMID = (175, 192, 214)
BED = (7, 9, 18)
SOCK = (14, 16, 30)
SOCK_LINE = (58, 65, 80)
GUN_A = (38, 43, 51)
GUN_HI = (92, 100, 114)
STEEL = (150, 162, 182)
STEEL_HI = (226, 233, 246)


def mixc(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def grade(c, k, bed=BED):
    """time grade of a colour: k 0 HOT (as is), 1 COLD (70 percent value, 45 percent chroma), 2 FAR (50 percent value, 25 percent chroma)"""
    if k <= 0:
        return tuple(c[:3])
    sat, val = (1.0, 0.45, 0.25)[k], (1.0, 0.70, 0.50)[k]
    lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    g = tuple(lum + (c[i] - lum) * sat for i in range(3))
    return tuple(int(round(bed[i] + (g[i] - bed[i]) * val)) for i in range(3))


# ---- paths ---------------------------------------------------------------------------------------------------
def resample(pts, step):
    out = [pts[0]]
    carry = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        t = step - carry
        while t <= seg:
            out.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg))
            t += step
        carry = seg - (t - step)
    return out


def dotted(L, pts, col, dia=4.0, pitch=9.0, ink=True, closed=False, al=255):
    """L8 dotted: round dots (dia px) at a pitch.  The only 'broken' line left on the board: it means two or more turns away."""
    pp = list(pts) + ([pts[0]] if closed else [])
    for x, y in resample(pp, pitch):
        r = dia / 2
        if ink:
            L.ellipse([x - r - 1.2, y - r - 1.2, x + r + 1.2, y + r + 1.2], fill=INK + (al,))
    for x, y in resample(pp, pitch):
        r = dia / 2
        L.ellipse([x - r, y - r, x + r, y + r], fill=tuple(col[:3]) + (al,))


def glow_line(L, pts, col, w, blur=4, strength=0.35):
    L.glow(lambda dd: dd.line(L.P(pts), fill=tuple(col[:3]) + (255,), width=int(w * L.k), joint='curve'), blur=blur, strength=strength)


# ---- local masks ---------------------------------------------------------------------------------------------
def bbox_of(pts, pad):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return int(min(xs)) - pad, int(min(ys)) - pad, int(max(xs)) + pad + 1, int(max(ys)) + pad + 1


class Loc:
    """a small RGBA canvas at the layer's scale covering a 1x bbox; blit() composites it onto the layer"""
    def __init__(self, L, box):
        self.L = L
        self.k = L.k
        x0, y0, x1, y1 = box
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(cv_lib.W, x1), min(cv_lib.H, y1)
        self.x0, self.y0, self.w, self.h = x0, y0, max(1, x1 - x0), max(1, y1 - y0)
        self.im = Image.new('RGBA', (self.w * self.k, self.h * self.k), (0, 0, 0, 0))

    def P(self, pts):
        return [((x - self.x0) * self.k, (y - self.y0) * self.k) for x, y in pts]

    def mask(self, core, rad):
        """rounded shape = core polygon dilated by rad px"""
        m = Image.new('L', self.im.size, 0)
        d = ImageDraw.Draw(m)
        pp = self.P(core)
        d.polygon(pp, fill=255)
        if rad > 0:
            d.line(pp + [pp[0]], fill=255, width=max(1, int(2 * rad * self.k)), joint='curve')
            for x, y in pp:
                r = rad * self.k
                d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        return m

    def erode(self, m, px):
        n = int(px * self.k)
        if n <= 0:
            return m
        return m.filter(ImageFilter.MinFilter(2 * n + 1))

    def dilate(self, m, px):
        n = int(px * self.k)
        if n <= 0:
            return m
        return m.filter(ImageFilter.MaxFilter(2 * n + 1))

    def fill(self, m, col, al=255):
        lay = Image.new('RGBA', self.im.size, tuple(col[:3]) + (255,))
        a = m if al == 255 else m.point(lambda v: int(v * al / 255))
        lay.putalpha(a)
        self.im.alpha_composite(lay)

    def hatch_mask(self, m, angs=(45, 135), pitch=4.4, lw=1.5):
        """lines (global-grid anchored so neighbouring segments line up) clipped to mask m"""
        hm = Image.new('L', self.im.size, 0)
        d = ImageDraw.Draw(hm)
        W_, H_ = self.w, self.h
        for ang in angs:
            if ang == 45:     # lines x + y = c
                c0 = int((self.x0 + self.y0) // pitch) * pitch
                c = c0
                while c < self.x0 + self.y0 + W_ + H_ + pitch:
                    x_a, y_a = c - self.y0 - self.y0 * 0, 0
                    # points on line x + y = c in global coords -> local
                    p0 = (c - (self.y0 + 0) - self.x0, 0)
                    p1 = (c - (self.y0 + H_) - self.x0, H_)
                    d.line([(p0[0] * self.k, p0[1] * self.k), (p1[0] * self.k, p1[1] * self.k)], fill=255, width=max(1, int(lw * self.k)))
                    c += pitch
            else:             # lines x - y = c
                c0 = int((self.x0 - self.y0 - H_) // pitch) * pitch
                c = c0
                while c < self.x0 - self.y0 + W_ + pitch:
                    p0 = (c + self.y0 - self.x0, 0)
                    p1 = (c + (self.y0 + H_) - self.x0, H_)
                    d.line([(p0[0] * self.k, p0[1] * self.k), (p1[0] * self.k, p1[1] * self.k)], fill=255, width=max(1, int(lw * self.k)))
                    c += pitch
        return ImageChops.multiply(hm, m)

    def blit(self):
        self.L.im.alpha_composite(self.im, (self.x0 * self.k, self.y0 * self.k))


# ---- HP segment states ---------------------------------------------------------------------------------------
PEND = {'harm': HARM, 'soak': SOAKC, 'ours': PINK}      # who takes it
OPT = {'hp': 'A'}                                      # A cross-hatch, B hazard stripe, C drain core


def seg_shape(L, core, rad, st, lit_col=GAIN, ink_w=1.3, pitch=4.2, lw=1.4, plus=True, tick_pts=None, cold_al=0.7, opt=None, glow=True):
    """one HP segment of any geometry.  core = polygon (list of 1x pts) that is dilated by rad.
    st: lit | enemy | boss | harm | soak | ours | cold_harm | cold_soak | cold_ours | mend | gone | blocked_lit"""
    opt = opt or OPT['hp']
    box = bbox_of(core, int(rad + ink_w + 8))
    A = Loc(L, box)
    m = A.mask(core, rad)
    bb_ = m.getbbox()
    th_ = min(bb_[2] - bb_[0], bb_[3] - bb_[1]) / A.k if bb_ else 12.0      # thickness of the segment in px
    if st in PEND:
        m = A.dilate(m, 1.0)                                                # R51 review: the pending segment bulges 2 px thicker than a lit one
        if th_ < 12.0:                                                      # R51 review: single-direction 45 deg hatch, 1.6 px lines, 4 px pitch under 12 px; never dropped at 320 px
            pitch, lw = max(4.0, min(pitch, 4.4)), 1.6
    ink = A.dilate(m, ink_w)
    if st in PEND:
        col = PEND[st]
        if glow:
            g = A.im.copy()
            gl = Image.new('RGBA', A.im.size, col + (255,))
            gl.putalpha(m.filter(ImageFilter.GaussianBlur(3 * A.k)).point(lambda v: int(v * 0.55)))
            A.im.alpha_composite(gl)
        A.fill(ink, INK)
        if opt == 'A':
            A.fill(m, SOCK)
            A.fill(A.hatch_mask(m, (45, 135) if th_ >= 12.0 else (45,), pitch, lw), col)
            edge = ImageChops.subtract(m, A.erode(m, 1.7))
            A.fill(edge, col)
        elif opt == 'B':
            A.fill(m, INK)
            A.fill(A.hatch_mask(m, (45,), pitch * 1.45, lw * 2.3), col)
            edge = ImageChops.subtract(m, A.erode(m, 1.3))
            A.fill(edge, col)
        else:     # C drain: dark socket, solid cause-colour outline, a thin core of the same colour
            A.fill(m, SOCK)
            edge = ImageChops.subtract(m, A.erode(m, 1.7))
            A.fill(edge, col)
            th = min(m.size[0], m.size[1]) / A.k
            bb = m.getbbox()
            th = min((bb[2] - bb[0]), (bb[3] - bb[1])) / A.k if bb else 8
            core_m = A.erode(m, max(0.0, th / 2 - 1.5 - 1.7)) if th > 6 else A.erode(m, 2.6)
            A.fill(core_m, col)
    elif st.startswith('cold_'):
        col = grade(PEND[st[5:]], 1)
        A.fill(ink, INK)
        A.fill(m, SOCK)
        A.fill(m, col, 115)
        edge = ImageChops.subtract(m, A.erode(m, 1.5))
        A.fill(edge, col)
    elif st == 'mend':
        A.fill(ink, INK)
        A.fill(m, (8, 22, 14))
        A.fill(ImageChops.subtract(m, A.erode(m, 1.8)), GAIN)
    elif st == 'gone':
        A.fill(A.dilate(m, 0.6), INK)
        A.fill(m, SOCK_LINE)
        A.fill(A.erode(m, 1.4), SOCK)
    else:
        col = {'lit': lit_col, 'enemy': CREAM, 'boss': GOLD, 'blocked_lit': lit_col}.get(st, lit_col)
        A.fill(ink, INK)
        A.fill(m, col)
    A.blit()
    if st == 'mend' and plus:
        xs = [p[0] for p in core]
        ys = [p[1] for p in core]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        s = min(3.6, max(2.2, (max(ys) - min(ys)) / 3))
        L.line([(cx - s, cy), (cx + s, cy)], GAIN, 1.8)
        L.line([(cx, cy - s), (cx, cy + s)], GAIN, 1.8)
        if tick_pts:
            L.poly(tick_pts, fill=GAIN)


# ---- time marks ----------------------------------------------------------------------------------------------
def end_notch(L, x, y, ang, col=ENAMEL, s=6.0):
    """HOT mark: a solid wedge (8 px) pointing along ang (deg, 0 = up, clockwise), ink keyline"""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    pts = [(x + ux * s * 1.3, y + uy * s * 1.3), (x - ux * s * 0.5 + nx * s, y - uy * s * 0.5 + ny * s), (x - ux * s * 0.5 - nx * s, y - uy * s * 0.5 - ny * s)]
    L.poly(pts, fill=col, outline=INK, w=2.0)


def pips(L, x, y, k, ang=90, gap=10.0, r=3.2):
    """k turn pips along a direction (ang = direction of the run in deg, 90 = rightwards)"""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    for i in range(k):
        px, py = x + ux * gap * i, y + uy * gap * i
        L.ellipse([px - r - 1.4, py - r - 1.4, px + r + 1.4, py + r + 1.4], fill=INK)
        L.ellipse([px - r, py - r, px + r, py + r], fill=TMID)


def dial(L, x, y, k, r=7.5, col=None):
    """fuse dial: full disc = this END TURN, half = +1, quarter = +2 (a pie on a ring)."""
    col = col or (HARM_UP if k == 0 else grade(ENAMEL, k))
    L.ellipse([x - r - 1.6, y - r - 1.6, x + r + 1.6, y + r + 1.6], fill=INK)
    L.ellipse([x - r, y - r, x + r, y + r], fill=(14, 16, 28), outline=col, w=1.6)
    sweep = (360, 180, 90)[k]
    pts = [(x, y)] + [(x + (r - 2.4) * math.sin(math.radians(a)), y - (r - 2.4) * math.cos(math.radians(a))) for a in np.linspace(0, sweep, 14)]
    if k == 0:
        L.ellipse([x - r + 2.0, y - r + 2.0, x + r - 2.0, y + r - 2.0], fill=col)
    else:
        L.poly(pts, fill=col)
    # 12 o'clock index mark
    L.line([(x, y - r - 1.6), (x, y - r + 2.2)], ENAMEL if k else INK, 1.4)


def double_line(L, pts, col, w=2.4, gap=3.0, ink=True):
    """L10: two solid strokes with a 3 px gap (protection).  pts is a centre path; offsets are taken along the normal."""
    p = list(pts)
    n = len(p)
    off = []
    for i in range(n):
        a = p[max(0, i - 1)]
        b = p[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        off.append((-dy / ln, dx / ln))
    for s in (-1, 1):
        q = [(p[i][0] + off[i][0] * s * (gap / 2 + w / 2), p[i][1] + off[i][1] * s * (gap / 2 + w / 2)) for i in range(n)]
        if ink:
            L.line(q, INK, w + 2.4)
    for s in (-1, 1):
        q = [(p[i][0] + off[i][0] * s * (gap / 2 + w / 2), p[i][1] + off[i][1] * s * (gap / 2 + w / 2)) for i in range(n)]
        L.line(q, col, w)


def hex_pts(x, y, r):
    return [(x + r * math.cos(math.radians(60 * i + 30)), y + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
