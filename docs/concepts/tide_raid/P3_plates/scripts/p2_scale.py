"""P2 UI kit at scale S (true-2x crops): the pass-2 kit draws in 1920x1080 px. install() swaps lib.Lyr / lib.Cv / lib.blur for versions that take 1920-frame
coordinates and widths and rasterise at S x resolution (no upscaling of finished pixels). Call BEFORE importing ui / hy / hb / eb / glyphs.
S == 1 is a no-op."""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import p1lib as L

S = int(os.environ.get('P2_S', '1'))


def install():
    if S == 1:
        return
    sys.path.insert(0, L.H2)
    import lib as PL
    PL.W, PL.H = 1920 * S, 1080 * S
    # P3 FIX (tier-tile anchor bug): lib.T() centres on W/2,H/2 at call time; with W=3840 every world point (sites, home, hq) shifted by +960,+540 in the UI layer
    PL.T = lambda p, dy=0.0: np.array([(p[0] - PL.CEN[0]) * PL.ZOOM + 960.0, (p[1] + dy - PL.CEN[1]) * PL.ZOOM + 540.0])
    ob = PL.blur

    def blur(a, s):
        return ob(a, s * S)
    PL.blur = blur

    class Lyr(PL.Lyr):
        def __init__(self, box=None, ss=2, pad=30):
            self.ss = ss
            if box is None:
                x0 = y0 = 0
                w, h = 1920, 1080
            else:
                x0 = int(max(0, math.floor(box[0] - pad))); y0 = int(max(0, math.floor(box[1] - pad)))
                x1 = int(min(1920, math.ceil(box[2] + pad))); y1 = int(min(1080, math.ceil(box[3] + pad)))
                w, h = max(2, x1 - x0), max(2, y1 - y0)
            self.x0, self.y0 = x0, y0
            self.off = (x0 * S, y0 * S)
            self.w, self.h = w * S, h * S
            self.im = Image.new('L', (self.w * ss, self.h * ss), 0)
            self.d = ImageDraw.Draw(self.im)

        def P(self, pts):
            k = S * self.ss
            return [((float(x) - self.x0) * k, (float(y) - self.y0) * k) for x, y in pts]

        def _w(self, w):
            return max(1, int(w * S * self.ss))

        def line(self, pts, w=2, v=255, dash=None):
            k = S * self.ss
            P = self.P(pts)
            if dash:
                on, off = dash
                for a, b in zip(P[:-1], P[1:]):
                    a = np.array(a); b = np.array(b)
                    L_ = np.hypot(*(b - a))
                    if L_ < 1e-6:
                        continue
                    u = (b - a) / L_
                    t = 0
                    while t < L_:
                        t2 = min(t + on * k, L_)
                        self.d.line([tuple(a + u * t), tuple(a + u * t2)], fill=v, width=self._w(w))
                        t += (on + off) * k
            else:
                self.d.line(P, fill=v, width=self._w(w), joint='curve')

        def poly(self, pts, v=255, outline=None, ow=1):
            P = self.P(pts)
            if outline is None:
                self.d.polygon(P, fill=v)
            else:
                self.d.polygon(P, fill=v if v is not None else None, outline=outline, width=self._w(ow))

        def ell(self, c, rx, ry=None, v=255, outline=False, ow=2):
            ry = rx if ry is None else ry
            a = self.P([(c[0] - rx, c[1] - ry)])[0]; b = self.P([(c[0] + rx, c[1] + ry)])[0]
            if outline:
                self.d.ellipse((a[0], a[1], b[0], b[1]), outline=v, width=self._w(ow))
            else:
                self.d.ellipse((a[0], a[1], b[0], b[1]), fill=v)

        def rr(self, x0, y0, x1, y1, r, v=255, outline=False, ow=2):
            a = self.P([(x0, y0)])[0]; b = self.P([(x1, y1)])[0]
            k = S * self.ss
            if outline:
                self.d.rounded_rectangle((a[0], a[1], b[0], b[1]), r * k, outline=v, width=self._w(ow))
            else:
                self.d.rounded_rectangle((a[0], a[1], b[0], b[1]), r * k, fill=v)

        def arc(self, c, r, a0, a1, w=2, v=255):
            a = self.P([(c[0] - r, c[1] - r)])[0]; b = self.P([(c[0] + r, c[1] + r)])[0]
            self.d.arc((a[0], a[1], b[0], b[1]), a0, a1, fill=v, width=self._w(w))

        def text(self, xy, t, size, v=255, anchor='mm', mono=False, stroke=0):
            k = S * self.ss
            p = self.P([xy])[0]
            f = PL.font(size * k, mono)
            self.d.text(p, t, font=f, fill=v, anchor=anchor, stroke_width=int(stroke * k), stroke_fill=v)

        def full(self):
            out = np.zeros((PL.H, PL.W), np.float32)
            c = PL._clip(self.off, (self.h, self.w))
            if c:
                out[c[0]] = self.m[c[1]]
            return out

    PL.Lyr = Lyr

    # sprite cards: render the 1x sprite at S x (the sprite builder uses Lyr, so it is already S x) -> place in S px
    return PL


def head_tab_mask(typ, w, h, S_):
    """P3 (coordinator A-review): the card tab carries the LOCKED H6 head silhouette (D worm / N thorn claw / E sea-mine), ink on the type-colour tab, from p1_heads.sprite
    (the same source as the on-map heads). Returns a float mask (h*S_, w*S_) with the silhouette centred at (w/2, 25) of the 1x card."""
    import p1_heads
    sz = int(44 * S_)
    im = p1_heads.sprite(typ, 0, sz)
    a = np.asarray(im, np.float32)[..., 3] / 255
    ys, xs = np.nonzero(a > 0.08)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    fit_w, fit_h = 40 * S_, 31 * S_
    k = min(fit_w / a.shape[1], fit_h / a.shape[0])
    pil = Image.fromarray((a * 255).astype(np.uint8)).resize((max(1, int(a.shape[1] * k)), max(1, int(a.shape[0] * k))), Image.LANCZOS)
    a = np.asarray(pil, np.float32) / 255
    m = np.zeros((h * S_, w * S_), np.float32)
    cx, cy = int(w * S_ / 2), int(25 * S_)
    x0 = cx - a.shape[1] // 2; y0 = cy - a.shape[0] // 2
    m[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    return m


def patch_tabs(hy):
    """replace hy.vcard_sprite so the tab glyph is the H6 head silhouette (any S)."""
    def vcard_sprite(verb, typ, w=104, h=140, ss=3):
        col = hy.TYPE_COL[typ]
        outer, inner, gl, tab = (hy.Lyr((0, 0, w, h), ss=ss, pad=0) for _ in range(4))
        outer.rr(1, 1, w - 1, h - 1, 13, 255)
        inner.rr(7, 7, w - 7, h - 7, 8, 255)
        tab.rr(7, 7, w - 7, 43, 8, 255)
        tab.rr(7, 30, w - 7, 43, 0, 255)
        hy.ui.VERB_FN[verb](gl, (w / 2, h * .67), 28)
        hs, ws = h * S, w * S
        o, i_, g_, tb = (x.m[:hs, :ws] for x in (outer, inner, gl, tab))
        t_ = head_tab_mask(typ, w, h, S)
        img = np.zeros((hs, ws, 3), np.float32)
        img[:] = hy.hexc('FBF8EC')
        img = img * (1 - i_[..., None]) + hy.hexc('F1EBD8') * i_[..., None]
        img = img * (1 - tb[..., None]) + col * tb[..., None]
        img = img * (1 - g_[..., None]) + hy.INK * g_[..., None]
        img = img * (1 - t_[..., None]) + hy.INK * t_[..., None]
        return img, o
    hy.vcard_sprite = vcard_sprite


def patch_modules(hy, ui, hb, eb):
    """after the kit modules are imported: their own W/H copies are 1x layout numbers (hand centring etc.)"""
    patch_tabs(hy)
    if S == 1:
        return
    for m in (hy, ui, hb, eb):
        if hasattr(m, 'W'):
            m.W = 1920
        if hasattr(m, 'H'):
            m.H = 1080


    def vcard(cv, c, verb, typ, angle=0.0, lime=False, k=1.0, sc=1.0):
        img, a = hy.vcard_sprite(verb, typ)          # built through the S x Lyr, so img is (140 S, 104 S)
        h, w = a.shape
        im = Image.fromarray((np.clip(np.dstack([img, a]), 0, 1) * 255).astype(np.uint8), 'RGBA')
        if sc != 1.0:
            im = im.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        arr = np.asarray(im, np.float32) / 255
        ox, oy = int(c[0] * S - arr.shape[1] / 2), int(c[1] * S - arr.shape[0] / 2)
        cv.over(hy.INK, hy.blur(arr[..., 3], 7), .6 * k, (ox + 4 * S, oy + 9 * S))
        if lime:
            big = Image.fromarray((arr[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(8 * S + 1))
            ring = np.clip(np.asarray(big, np.float32) / 255 - arr[..., 3], 0, 1)
            cv.add(hy.LIME, hy.blur(arr[..., 3], 6), .9, (ox, oy))
            cv.add(hy.LIME, ring, 1.0, (ox, oy))
        cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))
    hy.vcard = vcard

    _hud = hy.hud

    def hud(cv, *a, flash=0.0, **kw):
        _hud(cv, *a, flash=0.0, **kw)
        if flash:
            cv.add(hy.TIER['DAMAGED'], np.full((56 * S, 226 * S), flash * .3, np.float32), 1, (22 * S, 14 * S))
    hy.hud = hud
    _gt = ui.glitch_tear

    def glitch_tear(cv, box, amount=1.0, seed=7, bands=9, split=True, maxdx=48):
        _gt(cv, tuple(v * S for v in box), amount, seed, bands, split, maxdx * S)
    ui.glitch_tear = glitch_tear
