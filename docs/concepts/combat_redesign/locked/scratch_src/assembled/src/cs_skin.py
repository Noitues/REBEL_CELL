"""cs_skin: CORP SKIN token sets for the enemy layers of the REBEL_CELL combat screen (colour + material + pattern + crest per corp).
A skin is one object: pal (palette), cell() / tape() / rim() / annulus() material functions, token_frame(), disc_frame(), ticket(), crest().
install(skin) patches the generator's enemy-layer painters so swapping the corp = swapping the skin.  The game marks (HP, chevrons, hatch, HOT/COLD/FAR,
arrowed outlines) are drawn by the original code on top of the skin and are never touched."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from cv_lib import C, W, H, L2, ppx, INK

# ------------------------------------------------------------------------------------------------ numerics
_trees = {}


def _tree(pitch, seed):
    k = (pitch, seed)
    if k not in _trees:
        r = np.random.default_rng(seed)
        n = int(1200 / pitch) + 3
        gx, gy = np.meshgrid(np.arange(-1, n), np.arange(-1, n))
        px = (gx + 0.1 + 0.8 * r.random(gx.shape)) * pitch
        py = (gy + 0.1 + 0.8 * r.random(gy.shape)) * pitch
        pts = np.c_[px.ravel(), py.ravel()]
        _trees[k] = (cKDTree(pts), pts)
    return _trees[k]


def vor(X, Y, pitch, seed=1):
    """F1, F2 (distance to nearest / second nearest seed), seed id"""
    t, pts = _tree(pitch, seed)
    d, i = t.query(np.c_[X.ravel(), Y.ravel()].astype(np.float64), k=2)
    sh = X.shape
    return d[:, 0].reshape(sh).astype(np.float32), d[:, 1].reshape(sh).astype(np.float32), i[:, 0].reshape(sh), pts


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Acc:
    """premultiplication-free 'over' accumulator for (rgb, alpha) layers"""

    def __init__(self, shape):
        self.rgb = np.zeros(shape + (3,), np.float32)
        self.a = np.zeros(shape, np.float32)

    def add(self, col, a):
        col = np.asarray(col, np.float32)
        if col.ndim == 1:
            col = np.broadcast_to(col, self.rgb.shape)
        a = np.clip(a, 0, 1).astype(np.float32)
        oa = a + self.a * (1 - a)
        self.rgb = (col * a[..., None] + self.rgb * (self.a * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa


def polar(X, Y):
    dx, dy = X - C[0], Y - C[1]
    return np.hypot(dx, dy).astype(np.float32), (np.degrees(np.arctan2(dx, -dy)) % 360).astype(np.float32)


def region_apply(L, polys, fn, pad=2, k=2, strength=1.0, **kw):
    """fn(X, Y, RHO, TH) -> (rgb[h,w,3] 0..255, alpha[h,w]) evaluated at 2x resolution inside the polygons; composited on L.im"""
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    bx0, by0 = int(math.floor(min(xs))) - pad, int(math.floor(min(ys))) - pad
    bx1, by1 = int(math.ceil(max(xs))) + pad, int(math.ceil(max(ys))) + pad
    w, h = (bx1 - bx0) * k, (by1 - by0) * k
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    for pl in polys:
        d.polygon([((x - bx0) * k, (y - by0) * k) for x, y in pl], fill=255)
    m = np.asarray(m, np.float32) / 255.0
    X = (bx0 + (np.arange(w, dtype=np.float32) + 0.5) / k)[None, :].repeat(h, 0)
    Y = (by0 + (np.arange(h, dtype=np.float32) + 0.5) / k)[:, None].repeat(w, 1)
    RHO, TH = polar(X, Y)
    rgb, a = fn(X, Y, RHO, TH, **kw)
    a = a * m * strength
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8)
    L.im.alpha_composite(Image.fromarray(out, 'RGBA'), (bx0 * k, by0 * k))


def faded(L2src, f):
    L2src.im.putalpha(L2src.im.split()[3].point(lambda v: int(v * f)))
    return L2src


def mixc(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ------------------------------------------------------------------------------------------------ base class
class Skin:
    name = 'base'
    pal = {}
    hue_shift = 0.0            # degrees: the SCHEDULE orange is rotated by this onto the corp primary
    hazard = False

    # --- materials (arrays) -------------------------------------------------------------------
    def cell(self, X, Y, RHO, TH, empty=False):
        raise NotImplementedError

    def tape(self, X, Y, RHO, TH):
        raise NotImplementedError

    def bezel(self, X, Y, RHO, TH):
        raise NotImplementedError

    def annulus(self, X, Y, RHO, TH):
        raise NotImplementedError

    def rim(self, X, Y, RHO, TH):
        raise NotImplementedError

    def arcframe(self, X, Y, RHO, TH):
        raise NotImplementedError

    # --- vector pieces ------------------------------------------------------------------------
    def rim_vector(self, L):
        pass

    def cell_detail(self, L, poly, dep, empty, seed):
        pass

    def token_frame(self, L, x, y, R, kind, dep):
        pass

    def disc_frame(self, L, x, y, R):
        pass

    def ticket(self, L, box, nearest, climax):
        pass

    def crest(self, L, x, y, s=1.0):
        pass


# ================================================================================================ SOLACE
class Solace(Skin):
    """Solace Biosystems: leaf-green lab glass, cell membranes and bubbles, porcelain frames, helix crest.  Pink is demoted to rose nuclei under glass."""
    name = 'solace'
    pal = dict(primary=(150, 255, 70), secondary=(255, 70, 150),
               glass=(20, 70, 46), glass_hi=(96, 210, 110), bed=(6, 18, 13), edge=(150, 236, 120),
               porcelain=(226, 238, 216), porcelain_d=(150, 176, 150), strand_a=(110, 214, 70), strand_b=(24, 98, 78),
               nucleus=(226, 120, 160), pale=(236, 248, 226))
    hue_shift = 68.0

    def cell(self, X, Y, RHO, TH, empty=False):
        P = self.pal
        acc = Acc(X.shape)
        # leaf-green glass: one tint over the original slate cell (kind wash survives underneath) + a cool lift toward the outer edge
        ring = np.clip((RHO - 214) / 57.0, 0, 3) % 1.0
        acc.add(P['glass'], 0.40 + 0.06 * ring)
        # cell membranes (voronoi network) + nuclei + bubbles: all low contrast
        f1, f2, ids, pts = vor(X, Y, 30.0, 11)
        mem = 1 - sstep(0.0, 1.5, f2 - f1)
        acc.add(P['glass_hi'], mem * 0.13)
        wall = 1 - sstep(1.5, 4.2, f2 - f1)
        acc.add(P['glass_hi'], wall * 0.04)
        nuc = 1 - sstep(2.6, 4.0, f1)
        has = ((ids * 7919) % 5 == 0).astype(np.float32)           # one cell in five carries a rose nucleus (the Solace secondary, demoted)
        acc.add(P['nucleus'], nuc * has * 0.34)
        nuc2 = 1 - sstep(4.0, 6.5, f1)
        acc.add(P['glass_hi'], nuc2 * (1 - has) * 0.05)
        # bubbles
        g1, g2, bid, bp = vor(X, Y, 44.0, 23)
        rr = 3.0 + ((bid * 131) % 7).astype(np.float32)
        keep = ((bid * 53) % 3 == 0).astype(np.float32)
        ring_b = (1 - sstep(0.0, 0.9, np.abs(g1 - rr))) * keep
        acc.add(P['pale'], ring_b * 0.16)
        spec = (1 - sstep(0.0, 1.3, np.hypot(X - (bp[bid][:, :, 0] - rr * 0.35), Y - (bp[bid][:, :, 1] - rr * 0.35)))) * keep * (g1 < rr)
        acc.add((255, 255, 255), spec * 0.20)
        # glass gloss: a diagonal sheen across each ring (light from the top-left)
        sheen = np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 2 * 0.07
        acc.add((220, 255, 220), sheen)
        return acc.rgb, acc.a

    def bezel(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((16, 46, 34), 1.0)
        acc.add(P['glass'], 0.35 + 0.25 * np.sin(np.pi * u))
        f1, f2, ids, pts = vor(X, Y, 26.0, 5)
        acc.add(P['glass_hi'], (1 - sstep(0.0, 1.4, f2 - f1)) * 0.14)
        acc.add((255, 255, 255), np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 3 * np.exp(-((u - 0.2) / 0.12) ** 2) * 0.10)
        lip = (1 - sstep(0.0, 1.2, np.abs(RHO - 389.2))) + (1 - sstep(0.0, 1.2, np.abs(RHO - 420.8)))
        acc.add(P['porcelain'], np.clip(lip, 0, 1) * 0.55)
        return acc.rgb, acc.a

    def annulus(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((8, 26, 20), 0.55)
        f1, f2, ids, pts = vor(X, Y, 34.0, 31)
        acc.add(P['glass_hi'], (1 - sstep(0.0, 1.4, f2 - f1)) * 0.10)
        g1, g2, bid, bp = vor(X, Y, 52.0, 37)
        rr = 3.0 + ((bid * 131) % 6).astype(np.float32)
        keep = ((bid * 53) % 2 == 0).astype(np.float32)
        acc.add(P['pale'], (1 - sstep(0.0, 0.9, np.abs(g1 - rr))) * keep * 0.12)
        return acc.rgb, acc.a

    def tape(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        f1, f2, ids, pts = vor(X, Y, 16.0, 41)
        acc.add((40, 110, 30), (1 - sstep(0.0, 1.1, f2 - f1)) * 0.20)               # membranes in a darker lime
        g1, g2, bid, bp = vor(X, Y, 20.0, 43)
        rr = 2.0 + ((bid * 131) % 4).astype(np.float32)
        keep = ((bid * 53) % 2 == 0).astype(np.float32)
        acc.add((235, 255, 215), (1 - sstep(0.0, 0.8, np.abs(g1 - rr))) * keep * 0.20)
        u = np.clip((RHO - 391) / 26.0, 0, 1)
        acc.add((255, 255, 235), (1 - sstep(0.0, 0.16, np.abs(u - 0.78))) * 0.18)     # glass gloss line on the outer third
        return acc.rgb, acc.a

    def rim(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 489.0) / 11.0, 0, 1)
        k = 0.80 + 0.20 * np.sin(np.pi * u) + 0.10 * np.cos(np.radians(TH - 315))
        acc.add(np.array(P['porcelain'], np.float32)[None, None] * k[..., None], 1.0)
        return acc.rgb, acc.a

    def arcframe(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((16, 48, 36), 0.55)
        f1, f2, ids, pts = vor(X, Y, 18.0, 47)
        acc.add(P['glass_hi'], (1 - sstep(0.0, 1.2, f2 - f1)) * 0.14)
        return acc.rgb, acc.a

    # ---------------------------------------------------------------- vectors
    def helix(self, L, r, a0, a1, amp=3.0, wl=44.0, w=2.0, alpha=1.0):
        n = int(abs(a1 - a0) / 0.12)
        sa, sb = [], []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            s = math.radians(a) * r
            ph = 2 * math.pi * s / wl
            sa.append((a, math.sin(ph)))
        P = self.pal

        def strand(sign, col):
            return [ppx(C, r + amp * sign * s_, a) for a, s_ in sa]
        pa, pb = strand(1, None), strand(-1, None)
        L.line(pb, (10, 30, 24), w + 2.0)
        L.line(pb, P['strand_b'], w)
        L.line(pa, (10, 30, 24), w + 2.0)
        L.line(pa, P['strand_a'], w)
        # weave: re-draw the stretches where strand B passes in front
        seg = []
        for (a, s_), q in zip(sa, pb):
            if s_ < -0.15:
                seg.append(q)
            else:
                if len(seg) > 1:
                    L.line(seg, (10, 30, 24), w + 2.0)
                    L.line(seg, P['strand_b'], w)
                seg = []
        if len(seg) > 1:
            L.line(seg, (10, 30, 24), w + 2.0)
            L.line(seg, P['strand_b'], w)
        # rungs at the nodes
        step = wl / 8.0
        t = 0.0
        L_len = math.radians(abs(a1 - a0)) * r
        while t < L_len:
            a = a0 + (a1 - a0) * t / L_len
            ph = 2 * math.pi * t / wl
            s_ = math.sin(ph)
            L.line([ppx(C, r + amp * s_ * 0.85, a), ppx(C, r - amp * s_ * 0.85, a)], P['pale'], 1.0)
            t += step

    def rim_vector(self, L):
        self.helix(L, 494.5, 0, 360, amp=3.0, wl=2 * math.pi * 494.5 / 71, w=1.8)
        for k in range(6):
            x, y = ppx(C, 494.5, 30 + 60 * k)
            self.crest(L, x, y, 1.25)

    def crest(self, L, x, y, s=1.0):
        """porcelain roundel with a lime helix 'S'"""
        P = self.pal
        R = 9.0 * s
        L.ellipse([x - R - 1.6, y - R - 1.6, x + R + 1.6, y + R + 1.6], fill=(10, 24, 18))
        L.ellipse([x - R, y - R, x + R, y + R], fill=P['porcelain'])
        L.ellipse([x - R + 1.4, y - R + 1.4, x + R - 1.4, y + R - 1.4], outline=P['porcelain_d'], w=0.9)
        pts = [(x + 4.2 * s * math.sin(t * math.pi * 2), y + (t - 0.5) * 12.5 * s) for t in [i / 20 for i in range(21)]]
        pts2 = [(x - 4.2 * s * math.sin(t * math.pi * 2), y + (t - 0.5) * 12.5 * s) for t in [i / 20 for i in range(21)]]
        L.line(pts2, P['strand_b'], 1.7 * s)
        L.line(pts, P['strand_a'], 1.9 * s)
        for t in (0.25, 0.5, 0.75):
            yy = y + (t - 0.5) * 12.5 * s
            L.line([(x - 3.0 * s * math.sin(t * math.pi * 2), yy), (x + 3.0 * s * math.sin(t * math.pi * 2), yy)], (255, 255, 255), 0.9)

    def cell_detail(self, L, poly, dep, empty, seed):
        P = self.pal
        pp = poly + [poly[0]]
        L.line(pp, mixc(P['edge'], (10, 30, 20), 0.35) + (150,), 1.3)       # glass edge

    def token_frame(self, L, x, y, R, kind, dep):
        """porcelain bezel ring around the disc: a mid-value glazed band with an ink groove against the lane ring, a lime glaze line and a notch at the top"""
        P = self.pal
        Ro = R + 6.0
        L.ellipse([x - Ro - 1.6, y - Ro - 1.6, x + Ro + 1.6, y + Ro + 1.6], fill=(8, 22, 16))
        L.ellipse([x - Ro, y - Ro, x + Ro, y + Ro], fill=mixc(P['porcelain'], (60, 90, 66), 0.30))
        # glaze: lit upper-left arc, shaded lower-right
        L.line(L.arc_pts((x, y), Ro - 1.6, 280, 360 + 40, 14), mixc(P['porcelain'], (255, 255, 255), 0.5), 1.6)
        L.line(L.arc_pts((x, y), Ro - 1.6, 110, 220, 10), P['porcelain_d'], 1.4)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(8, 22, 16))           # ink groove against the lane ring
        # lime glaze dot at 12 o'clock (the crest mark)
        L.ellipse([x - 2.2, y - Ro + 1.0 - 0.8, x + 2.2, y - Ro + 1.0 + 3.6], fill=P['strand_a'], outline=(8, 22, 16), w=0.8)

    def disc_frame(self, L, x, y, R):
        P = self.pal
        Ro = R + 3.6
        L.ellipse([x - Ro - 1.2, y - Ro - 1.2, x + Ro + 1.2, y + Ro + 1.2], fill=(8, 22, 16))
        L.ellipse([x - Ro, y - Ro, x + Ro, y + Ro], fill=mixc(P['porcelain'], (60, 90, 66), 0.30))
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=(8, 22, 16))

    def ticket(self, L, box, nearest, climax):
        P = self.pal
        x0, y0, x1, y1 = box
        pts = [(x0 + 7, y0), (x1 - 7, y0), (x1, y0 + 7), (x1, y1 - 7), (x1 - 7, y1), (x0 + 7, y1), (x0, y1 - 7), (x0, y0 + 7)]   # a lab-slide: chamfered glass
        L.poly(pts, fill=(14, 40, 30, 255))
        L.line(pts + [pts[0]], (8, 22, 16), 4.4)
        L.line(pts + [pts[0]], P['porcelain'] if nearest else P['porcelain_d'], 1.8)
        # membrane hint
        for (cx, cy, rr) in ((x1 - 14, y1 - 16, 6), (x1 - 24, y1 - 12, 4), (x1 - 9, y1 - 26, 3.5)):
            L.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=mixc(P['glass_hi'], (14, 40, 30), 0.55), w=1.0)
        self.crest(L, x1 - 13, y0 + 13, 0.62)


# ================================================================================================ MERIDIAN
class Meridian(Skin):
    """Meridian Freight: container corrugated steel, orange oxide paint, hazard rim, stencilled container numbers, barcodes, rivets, crane-A crest."""
    name = 'meridian'
    pal = dict(primary=(255, 140, 26), secondary=(255, 46, 40),
               steel=(70, 62, 56), oxide=(150, 76, 26), edge=(224, 128, 40), bed=(14, 11, 9),
               paint=(236, 214, 178), hazard_a=(255, 140, 26), hazard_b=(20, 15, 12), rivet=(40, 30, 24))
    hue_shift = 0.0
    hazard = True

    @staticmethod
    def _rib(RHO, TH, pitch):
        dep = np.clip(np.floor((RHO - 214) / 57.0), 0, 2)
        rmid = 214 + 57 * dep + 28.5
        ph = np.radians((TH + 30) % 60) * rmid / pitch
        return 0.5 + 0.5 * np.cos(2 * np.pi * ph)

    def cell(self, X, Y, RHO, TH, empty=False):
        P = self.pal
        acc = Acc(X.shape)
        acc.add(P['oxide'], 0.34)
        rib = self._rib(RHO, TH, 6.5)
        acc.add((20, 12, 8), (1 - rib) ** 2 * 0.17)         # trough
        acc.add((255, 206, 150), rib ** 3 * 0.075)              # ridge
        # weathering: paint scuffs
        n = ndi.gaussian_filter(np.random.default_rng(3).random(X.shape).astype(np.float32), 2.2)
        n = (n - n.mean()) / (n.std() + 1e-6)
        acc.add((16, 10, 8), sstep(1.2, 2.4, n) * 0.10)
        return acc.rgb, acc.a

    def bezel(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((34, 28, 24), 1.0)
        acc.add(P['steel'], 0.35 + 0.2 * np.sin(np.pi * u))
        acc.add((20, 12, 8), (1 - self._rib(RHO, TH, 5.0)) ** 2 * 0.14)
        # hazard lips: outer and inner stripe bands
        arc = np.radians(TH) * RHO
        ph = (TH / 360.0 * 283 + RHO / 9.0) % 1.0
        haz = np.where(ph < 0.5, 1.0, 0.0).astype(np.float32)
        lipm = np.maximum(1 - sstep(0.0, 0.8, np.abs(RHO - 389.6) - 1.4), 1 - sstep(0.0, 0.8, np.abs(RHO - 420.4) - 1.4))
        acc.add(P['hazard_b'], lipm * 0.95)
        acc.add(P['hazard_a'], lipm * haz * 0.85)
        return acc.rgb, acc.a

    def annulus(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((26, 20, 16), 0.55)
        acc.add((20, 12, 8), (1 - self._rib(RHO, TH, 7.0)) ** 2 * 0.14)
        return acc.rgb, acc.a

    def tape(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        # steel plate seen through the orange paint: fine ribs along the tape (concentric), the chevrons cross them
        rib = 0.5 + 0.5 * np.cos(2 * np.pi * RHO / 3.4)
        acc.add((60, 26, 6), (1 - rib) ** 2 * 0.20)
        acc.add((255, 214, 150), rib ** 4 * 0.10)
        u = np.clip((RHO - 391) / 26.0, 0, 1)
        acc.add((255, 220, 160), (1 - sstep(0.0, 0.12, np.abs(u - 0.82))) * 0.14)
        return acc.rgb, acc.a

    def rim(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 489.0) / 11.0, 0, 1)
        acc.add(P['hazard_b'], 1.0)
        arc = np.radians(TH) * RHO
        ph = (TH / 360.0 * 311 + (RHO - 489.0) / 10.0) % 1.0
        stripe = np.where(ph < 0.5, 1.0, 0.0).astype(np.float32)
        k = 0.86 + 0.14 * np.sin(np.pi * u) + 0.10 * np.cos(np.radians(TH - 315))
        acc.add(np.array(P['hazard_a'], np.float32)[None, None] * k[..., None], stripe * 0.94)
        return acc.rgb, acc.a

    def arcframe(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((40, 24, 14), 0.55)
        acc.add((20, 12, 8), (1 - self._rib(RHO, TH, 5.0)) ** 2 * 0.14)
        return acc.rgb, acc.a

    def rim_vector(self, L):
        # rim keylines
        for r in (488.6, 500.2):
            L.line(L.arc_pts(C, r, 0, 360, 360), (10, 8, 7), 1.6)
        for k in range(6):
            x, y = ppx(C, 494.5, 30 + 60 * k)
            self.crest(L, x, y, 1.25)

    def crest(self, L, x, y, s=1.0):
        """crane-A: a black plate, an orange A-frame gantry with a jib and a hook"""
        P = self.pal
        h = 9.5 * s
        L.rect([x - h - 1.6, y - h - 1.6, x + h + 1.6, y + h + 1.6], fill=(10, 8, 7), r=2.0)
        L.rect([x - h, y - h, x + h, y + h], fill=(30, 24, 20), r=1.5)
        o = P['hazard_a']
        # A-frame legs
        L.line([(x - 5.4 * s, y + 6.4 * s), (x - 0.4 * s, y - 6.6 * s), (x + 4.4 * s, y + 6.4 * s)], o, 1.9 * s)
        L.line([(x - 3.0 * s, y + 1.2 * s), (x + 2.2 * s, y + 1.2 * s)], o, 1.5 * s)
        # jib and hook
        L.line([(x - 0.4 * s, y - 6.2 * s), (x + 7.0 * s, y - 4.0 * s)], o, 1.6 * s)
        L.line([(x + 6.2 * s, y - 4.0 * s), (x + 6.2 * s, y + 0.4 * s)], (240, 230, 214), 0.9 * s)
        L.ellipse([x + 5.2 * s, y + 0.2 * s, x + 7.2 * s, y + 2.4 * s], outline=(240, 230, 214), w=0.9 * s)
        for (rx, ry) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            L.ellipse([x + rx * (h - 2.2) - 0.8, y + ry * (h - 2.2) - 0.8, x + rx * (h - 2.2) + 0.8, y + ry * (h - 2.2) + 0.8], fill=(150, 140, 130))

    @staticmethod
    def _rivet(L, x, y, r=1.7):
        L.ellipse([x - r - 0.8, y - r - 0.8, x + r + 0.8, y + r + 0.8], fill=(14, 10, 8, 200))
        L.ellipse([x - r, y - r, x + r, y + r], fill=(122, 100, 84, 235))
        L.ellipse([x - r * 0.9, y - r * 0.9, x - r * 0.1, y - r * 0.1], fill=(226, 206, 184, 235))

    def cell_detail(self, L, poly, dep, empty, seed):
        P = self.pal
        pp = poly + [poly[0]]
        L.line(pp, mixc(P['edge'], (12, 8, 6), 0.35) + (150,), 1.3)        # painted steel edge
        n = len(poly) // 2
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        for idx in (0, n - 1, n, len(poly) - 1):
            px, py = poly[idx]
            d = math.hypot(cx - px, cy - py) + 1e-6
            self._rivet(L, px + (cx - px) / d * 6.0, py + (cy - py) / d * 6.0)

    def token_frame(self, L, x, y, R, kind, dep):
        """container frame: an orange steel octagon with four corner castings; ink groove against the lane ring"""
        P = self.pal
        Ro = R + 6.5
        oc = lambda r: [(x + r * math.cos(math.radians(22.5 + 45 * i)), y + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        L.poly(oc(Ro + 1.6), fill=(10, 8, 7))
        L.poly(oc(Ro), fill=mixc(P['hazard_a'], (60, 30, 10), 0.42))
        # lit top-left edge, shaded bottom-right
        o8 = oc(Ro - 1.2)
        L.line(o8[4:7], mixc(P['hazard_a'], (255, 230, 180), 0.55), 1.5)
        L.line(o8[0:3], mixc(P['hazard_a'], (40, 16, 4), 0.55), 1.5)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(10, 8, 7))
        for i in range(4):          # corner castings at the diagonals
            a = math.radians(45 + 90 * i)
            cx, cy = x + (Ro - 2.2) * math.cos(a) * 0.98, y + (Ro - 2.2) * math.sin(a) * 0.98
            L.rect([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5], fill=(44, 34, 28), outline=(10, 8, 7), w=0.8, r=0.6)
            L.ellipse([cx - 0.9, cy - 0.9, cx + 0.9, cy + 0.9], fill=(210, 190, 170))

    def disc_frame(self, L, x, y, R):
        P = self.pal
        Ro = R + 3.6
        oc = lambda r: [(x + r * math.cos(math.radians(22.5 + 45 * i)), y + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        L.poly(oc(Ro + 1.3), fill=(10, 8, 7))
        L.poly(oc(Ro), fill=mixc(P['hazard_a'], (60, 30, 10), 0.42))
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=(10, 8, 7))

    def ticket(self, L, box, nearest, climax):
        P = self.pal
        x0, y0, x1, y1 = box
        pts = [(x0 + 2, y0), (x1 - 2, y0), (x1, y0 + 2), (x1, y1 - 2), (x1 - 2, y1), (x0 + 2, y1), (x0, y1 - 2), (x0, y0 + 2)]    # a shipping tag: square cut
        L.poly(pts, fill=(34, 26, 20, 255))
        L.line(pts + [pts[0]], (10, 8, 7), 4.4)
        L.line(pts + [pts[0]], P['edge'] if nearest else mixc(P['edge'], (34, 26, 20), 0.35), 1.8)
        # barcode strip, top right
        r = np.random.default_rng(int(x0))
        bx = x1 - 30
        for i in range(11):
            wbar = 1.0 + 1.2 * (r.random() > 0.55)
            L.rect([bx, y0 + 6, bx + wbar, y0 + 17], fill=(214, 196, 170, 200), r=0.2)
            bx += wbar + 0.9
        for (cx, cy) in ((x0 + 5, y0 + 5), (x1 - 5, y0 + 5), (x0 + 5, y1 - 5), (x1 - 5, y1 - 5)):
            self._rivet(L, cx, cy, 1.2)


SKINS = {'solace': Solace(), 'meridian': Meridian()}
