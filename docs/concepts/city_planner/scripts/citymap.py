"""CityMap: terrain, zones, street textures, network and landmark drawing."""
import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from canvas import Canvas
from geom import (blob, TAU, Noise, arc_pts, catmull, circle_pts, cum, dashes, dist, ellipse_pts, jitter_line,
                  lerp, mix, offset_line, plen, pt_at, rect_pts, resample, rot, seg_intersections, sub)

U = 1000
S = 4
FPU = 2.0  # final px per unit

# ---- palette ---------------------------------------------------------------
COL = {
    'centre': (222, 206, 178),    # old city / rebel cell (bone)
    'halcyon': (236, 62, 84),     # crimson
    'solace': (64, 226, 168),     # mint
    'orbital': (150, 112, 255),   # violet
    'meridian': (255, 148, 36),   # orange
    'aurelian': (244, 204, 64),   # gold
    'tethys': (40, 204, 236),     # cyan
}
OCEAN_DEEP = (10, 24, 46)
OCEAN_SHALLOW = (34, 92, 128)
RIVER = (28, 76, 108)
LAND_LO = (30, 35, 44)
LAND_HI = (66, 72, 76)
PARK = (52, 98, 58)
PARK_DARK = (30, 66, 38)
INDUSTRY = (120, 116, 108)
SLUM = (214, 118, 58)
ROAD_CASING = (6, 8, 12)
ROAD_FILL = (246, 244, 232)
TEXT = (232, 236, 242)


def tint(c, t=0.35):
    return mix(c, (255, 255, 255), t)


class CityMap(Canvas):
    def __init__(self, seed=1):
        super().__init__(U, U, S, FPU, OCEAN_DEEP)
        self.seed = seed
        self.rng = random.Random(seed)
        self.land = None
        self.ocean = None
        self.water_extra = Image.new('L', (self.W, self.H), 0)
        self._dry = None
        self._np_cache = {}
        self.z = {}              # zone key -> dict(mask, poly, color)
        self.roads = []
        self.rails = []
        self.coast = []
        self.E = None
        self.stations = []
        self.gate_pts = []
        self.occupied = Image.new('L', (self.W, self.H), 0)

    # ------------------------------------------------------------------ base
    def set_ocean(self, coast, closing, noise_amp=5.0, noise_wl=110.0, extra_polys=()):
        """coast: control points of the shoreline (open polyline). closing: raw polygon corners that
        close the ocean region (usually off-map)."""
        nz = Noise(self.seed + 3, 4, noise_wl, 0.55)
        dense = catmull(coast, closed=False, step=3.0)
        dense = jitter_line(dense, nz, noise_amp, 3.0)
        self.coast = dense
        poly = dense + list(closing)
        om = Image.new('L', (self.W, self.H), 0)
        od = ImageDraw.Draw(om)
        od.polygon(self.PL(poly), fill=255)
        for ep in extra_polys:
            od.polygon(self.PL(ep), fill=255)
        self.ocean = om
        self.land = ImageChops.invert(om)
        return dense

    def set_islands(self, polys, noise_amp=3.0, noise_wl=90.0):
        """Land = union of island polygons (control pts, smooth flag); everything else is water."""
        nz = Noise(self.seed + 3, 4, noise_wl, 0.55)
        lm = Image.new('L', (self.W, self.H), 0)
        ld = ImageDraw.Draw(lm)
        coast = []
        for poly, smooth in polys:
            if smooth:
                dense = catmull(poly, closed=True, step=3.0)
            else:
                dense = resample(list(poly) + [poly[0]], 3.0)
            dense = jitter_line(dense + [dense[0]], nz, noise_amp, 3.0)
            coast.extend(dense)
            ld.polygon(self.PL(dense), fill=255)
        self.land = lm
        self.ocean = ImageChops.invert(lm)
        self.coast = coast

    def sunken(self, poly, col=(24, 72, 92), grid_angle=8, sp=7, seed=2):
        """Drowned streets visible under open water (does not touch land)."""
        pts = catmull(poly, closed=True, step=3.0)
        gm = ImageChops.multiply(self.poly_mask(pts), self.ocean)
        self.img.paste(col, mask=gm.point(lambda v: int(v * 0.45)))
        self.tex_grid(gm, grid_angle, sp, jitter=0.12, warp_amp=2, warp_wl=60, color=(110, 200, 220),
                      a_minor=0.34, a_major=0.55, major=4, w_minor=0.7, w_major=1.0, seed=seed)
        rng = random.Random(seed)
        bb = self.bbox_u(gm, 0)
        rects = []
        for _ in range(int((bb[2] - bb[0]) * (bb[3] - bb[1]) / 40)):
            p = self.rand_in(gm, rng)
            if p:
                rects.append(rect_pts(p[0], p[1], rng.uniform(1.5, 3.5), rng.uniform(1.5, 3.5), rng.uniform(0, 3)))
        self.polys(rects, (120, 190, 205), 0.3, clip=gm, bbox_units=bb)
        return gm

    def base(self, bumps, light=(-0.7, -0.7), noise_amp=0.05, contour=0.045, seed=5, hi=LAND_HI, lo=LAND_LO):
        """Render ocean (depth shading) + land (elevation, hillshade, contours)."""
        n = U
        lm = self.land.resize((n, n), Image.BILINEAR).filter(ImageFilter.GaussianBlur(20))
        g = np.asarray(lm).astype(float) / 255.0
        t = np.clip(g * 1.9, 0, 1) ** 0.9
        deep = np.array(OCEAN_DEEP, dtype=float)
        shal = np.array(OCEAN_SHALLOW, dtype=float)
        oc = deep[None, None, :] + (shal - deep)[None, None, :] * t[..., None]
        for lvl, a in ((0.30, 0.16), (0.16, 0.13), (0.07, 0.11)):
            e = (g >= lvl)
            edge = e ^ np.roll(e, 1, 0) | e ^ np.roll(e, 1, 1)
            oc[edge] = oc[edge] * (1 - a) + np.array([90, 150, 190]) * a
        ocean_img = Image.fromarray(oc.clip(0, 255).astype(np.uint8)).resize((self.W, self.H), Image.BICUBIC)
        # elevation
        X, Y = np.meshgrid(np.arange(n) + 0.5, np.arange(n) + 0.5)
        E = np.zeros((n, n))
        for cx, cy, sx, sy, h, ang in bumps:
            ca, sa = math.cos(ang), math.sin(ang)
            xr = (X - cx) * ca + (Y - cy) * sa
            yr = -(X - cx) * sa + (Y - cy) * ca
            E += h * np.exp(-0.5 * ((xr / sx) ** 2 + (yr / sy) ** 2))
        nz = Noise(seed, 4, 260.0, 0.5)
        E += nz.np(X, Y) * noise_amp
        # flatten towards the sea
        E *= np.clip((g - 0.45) * 5.0, 0.0, 1.0)
        E = np.clip(E, 0, 1)
        self.E = E
        gy, gx = np.gradient(E)
        shade = (gx * light[0] + gy * light[1]) * 60.0
        shade = np.clip(shade, -0.5, 0.5)
        base = np.array(lo, dtype=float)[None, None, :] + (np.array(hi, dtype=float) - np.array(lo, dtype=float))[None, None, :] * np.clip(E * 1.4, 0, 1)[..., None]
        base = base * (1 + shade[..., None] * 1.7)
        lvl = np.floor(E / contour)
        edge = (lvl != np.roll(lvl, 1, 0)) | (lvl != np.roll(lvl, 1, 1))
        idx = (np.floor(E / (contour * 5)) != np.roll(np.floor(E / (contour * 5)), 1, 0)) | \
              (np.floor(E / (contour * 5)) != np.roll(np.floor(E / (contour * 5)), 1, 1))
        base[edge & (E > 0.04)] = base[edge & (E > 0.04)] * 0.80 + 255 * 0.20 * 0.62
        base[idx & (E > 0.06)] = base[idx & (E > 0.06)] * 0.68 + 255 * 0.32 * 0.62
        land_img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).resize((self.W, self.H), Image.BICUBIC)
        comp = Image.composite(land_img, ocean_img, self.land)
        self.img.paste(comp)

    def elev(self, x, y):
        return float(self.E[min(U - 1, max(0, int(y))), min(U - 1, max(0, int(x)))])

    # ---- masks ---------------------------------------------------------------
    @property
    def dry(self):
        if self._dry is None:
            self._dry = ImageChops.subtract(self.land, self.water_extra)
        return self._dry

    def mnp(self, M):
        a = getattr(M, '_mnp', None)
        if a is None:
            a = np.asarray(M.resize((U, U), Image.BILINEAR)) > 127
            M._mnp = a
        return a

    def wet_np(self):
        w = ImageChops.lighter(self.ocean, self.water_extra)
        return np.asarray(w.resize((U, U), Image.BILINEAR)) > 127

    def bbox_u(self, M, pad=8):
        bb = getattr(M, '_bb', None)
        if bb is None:
            bb = M.getbbox() or (0, 0, 10, 10)
            M._bb = bb
        return (max(0, bb[0] / S - pad), max(0, bb[1] / S - pad), min(U, bb[2] / S + pad), min(U, bb[3] / S + pad))

    def inside(self, M, x, y):
        a = self.mnp(M)
        xi, yi = int(x), int(y)
        if xi < 0 or yi < 0 or xi >= U or yi >= U:
            return False
        return bool(a[yi, xi])

    def rand_in(self, M, rng, tries=60):
        a = self.mnp(M)
        bb = self.bbox_u(M, 0)
        for _ in range(tries):
            x = rng.uniform(bb[0], bb[2])
            y = rng.uniform(bb[1], bb[3])
            if a[min(U - 1, int(y)), min(U - 1, int(x))]:
                return (x, y)
        return None

    # ---- water -----------------------------------------------------------------
    def river(self, pts, w0, w1, smooth=True, jitter=0.0, bank=True, col=RIVER, step=2.0):
        dense = catmull(pts, step=3.0) if smooth else resample(pts, 3.0)
        if jitter:
            dense = jitter_line(dense, Noise(self.seed + 9, 3, 90.0), jitter, 2.0)
        dense = resample(dense, step)
        c = cum(dense)
        L = c[-1]
        wd = ImageDraw.Draw(self.water_extra)
        for i, p in enumerate(dense):
            w = lerp(w0, w1, c[i] / L)           # final px
            r = w * self.f / 2.0
            x, y = p[0] * S, p[1] * S
            if bank:
                rb = r + 1.6 * self.f
                self.d.ellipse([x - rb, y - rb, x + rb, y + rb], fill=mix(col, (140, 190, 220), 0.35) + (255,))
        for i, p in enumerate(dense):
            w = lerp(w0, w1, c[i] / L)
            r = w * self.f / 2.0
            x, y = p[0] * S, p[1] * S
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
            wd.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=255)
        self._dry = None
        return dense

    def lake(self, poly, col=RIVER, smooth=True):
        pts = catmull(poly, closed=True, step=3.0) if smooth else poly
        m = self.poly_mask(pts)
        m = ImageChops.multiply(m, self.land)
        self.img.paste(mix(col, (140, 190, 220), 0.35), mask=ImageChops.subtract(m.filter(ImageFilter.MaxFilter(7)), Image.new('L', (self.W, self.H), 0)))
        self.img.paste(col, mask=m)
        self.water_extra = ImageChops.lighter(self.water_extra, m)
        self._dry = None
        return pts

    def drowned(self, poly, col=(24, 72, 92), grid_angle=8, sp=7, seed=2, over_ocean=False):
        """Flooded old quarter: shallow water over a visible street grid and ruined blocks."""
        pts = catmull(poly, closed=True, step=3.0)
        pm = self.poly_mask(pts)
        m = ImageChops.multiply(pm, self.land)
        gm = pm if over_ocean else m
        self.img.paste(col, mask=m.point(lambda v: int(v * 0.96)))
        if over_ocean:
            self.img.paste(col, mask=ImageChops.subtract(pm, m).point(lambda v: int(v * 0.35)))
        self.tex_grid(gm, grid_angle, sp, jitter=0.12, warp_amp=2, warp_wl=60, color=(110, 200, 220),
                      a_minor=0.30, a_major=0.5, major=4, w_minor=0.7, w_major=1.0, seed=seed)
        rng = random.Random(seed)
        bb = self.bbox_u(gm, 0)
        rects = []
        for _ in range(int((bb[2] - bb[0]) * (bb[3] - bb[1]) / 40)):
            p = self.rand_in(gm, rng)
            if p:
                rects.append(rect_pts(p[0], p[1], rng.uniform(1.5, 3.5), rng.uniform(1.5, 3.5), rng.uniform(0, 3)))
        self.polys(rects, (120, 190, 205), 0.28, clip=gm, bbox_units=bb)
        edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
        self.img.paste((130, 220, 240), mask=edge.point(lambda v: int(v * 0.5)))
        self.water_extra = ImageChops.lighter(self.water_extra, m)
        self._dry = None
        return gm

    # ---- zones -----------------------------------------------------------------
    def zone(self, key, poly, color, tint_a=0.26, smooth=True, water_ok=False, add=False, edge_a=0.8, edge_w=1.2,
             fill=True, step=3.0):
        pts = catmull(poly, closed=True, step=step) if smooth else list(poly)
        m = self.poly_mask(pts)
        if not water_ok:
            m = ImageChops.multiply(m, self.dry)
        if add and key in self.z:
            m = ImageChops.lighter(m, self.z[key]['mask'])
        if fill:
            self.img.paste(color, mask=m.point(lambda v: int(v * tint_a)))
        if edge_a and edge_w:
            self.line(pts + [pts[0]], tint(color, 0.15), edge_w, edge_a, clip=self.land if water_ok else self.dry)
        self.z[key] = dict(mask=m, poly=pts, color=color)
        self.occupy(m)
        return m

    def occupy(self, M):
        self.occupied = ImageChops.lighter(self.occupied, M)

    def free_mask(self, poly, smooth=True, mark=True):
        """Polygon area that is dry and not yet claimed by another zone."""
        pts = catmull(poly, closed=True, step=3.0) if smooth else list(poly)
        m = self.poly_mask(pts)
        m = ImageChops.multiply(m, self.dry)
        m = ImageChops.subtract(m, self.occupied)
        if mark:
            self.occupy(m)
        return m, pts

    def fabric(self, key, poly, color, tint_a=0.10, smooth=True):
        m, pts = self.free_mask(poly, smooth)
        self.img.paste(color, mask=m.point(lambda v: int(v * tint_a)))
        self.z[key] = dict(mask=m, poly=pts, color=color)
        return m

    def strip_poly(self, pts, w, f0=0.0, f1=1.0):
        """Polygon of half-width w around part of a polyline (parks along rivers etc.)."""
        p = sub(pts, f0, f1)
        left = offset_line(p, w)
        right = offset_line(p, -w)
        return left + right[::-1]

    def mask_union(self, *keys):
        m = self.z[keys[0]]['mask']
        for k in keys[1:]:
            m = ImageChops.lighter(m, self.z[k]['mask'])
        return m

    def sub_mask(self, poly, key_parent=None, smooth=True):
        pts = catmull(poly, closed=True, step=3.0) if smooth else list(poly)
        m = self.poly_mask(pts)
        m = ImageChops.multiply(m, self.dry)
        if key_parent:
            m = ImageChops.multiply(m, self.z[key_parent]['mask'])
        return m, pts

    # ---- textures ------------------------------------------------------------------
    def _chop(self, pts, rng, gap, seg, step):
        out = []
        i = 0
        n = len(pts)
        while i < n - 1:
            ln = int(rng.uniform(*seg) / step) + 1
            piece = pts[i:i + ln + 1]
            if rng.random() > gap and len(piece) > 1:
                out.append(piece)
            i += ln
        return out

    def tex_grid(self, M, angle=0.0, sp=8.0, sp2=None, jitter=0.1, warp_amp=0.0, warp_wl=120.0, gap=0.0,
                 seg=(25, 70), major=0, color=(220, 220, 220), a_minor=0.5, a_major=0.85, w_minor=0.8,
                 w_major=1.6, seed=0, step=4.0, bbox=None):
        rng = random.Random(seed * 7919 + int(angle * 10) + int(sp * 100))
        bb = bbox or self.bbox_u(M, 12)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        R = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 6
        nzx = Noise(seed + 11, 3, warp_wl)
        nzy = Noise(seed + 12, 3, warp_wl)
        ang = math.radians(angle)
        minor, maj = [], []
        for axis in (0, 1):
            s_ = sp if axis == 0 else (sp2 or sp)
            pos = -R
            idx = 0
            while pos < R:
                pts = []
                t = -R
                while t <= R:
                    u, v = (t, pos) if axis == 0 else (pos, t)
                    x, y = rot((cx + u, cy + v), ang, (cx, cy))
                    if warp_amp:
                        x2 = x + nzx(x, y) * warp_amp
                        y2 = y + nzy(x, y) * warp_amp
                        x, y = x2, y2
                    if bb[0] - 20 <= x <= bb[2] + 20 and bb[1] - 20 <= y <= bb[3] + 20:
                        pts.append((x, y))
                    t += step
                if len(pts) > 1:
                    if major and idx % major == 0:
                        maj.append(pts)
                    elif gap > 0:
                        minor.extend(self._chop(pts, rng, gap, seg, step))
                    else:
                        minor.append(pts)
                idx += 1
                pos += s_ * (1 + rng.uniform(-jitter, jitter))
        self.lines(minor, color, w_minor, a_minor, clip=M, bbox_units=bb)
        self.lines(maj, color, w_major, a_major, clip=M, bbox_units=bb)

    def tex_walks(self, M, n=120, length=(30, 90), turn=0.25, step=3.0, color=(220, 220, 220), a=0.5, w=0.8,
                  seed=0):
        rng = random.Random(seed + 77)
        bb = self.bbox_u(M, 6)
        paths = []
        for _ in range(n):
            p = self.rand_in(M, rng)
            if not p:
                continue
            ang = rng.uniform(0, TAU)
            ln = rng.uniform(*length)
            pts = [p]
            x, y = p
            s = 0.0
            while s < ln:
                ang += rng.uniform(-turn, turn)
                x += math.cos(ang) * step
                y += math.sin(ang) * step
                pts.append((x, y))
                s += step
            paths.append(pts)
        self.lines(paths, color, w, a, clip=M, bbox_units=bb)

    def tex_curvi(self, M, c, r0, r1, sp=7.0, a0=0.0, a1=TAU, gap=0.25, spoke_sp=18.0, color=(220, 220, 220),
                  a=0.5, w=0.8, cul=40, seed=0):
        """Curvilinear 'suburban' pattern: concentric arcs, radial connectors, cul-de-sac stubs."""
        rng = random.Random(seed + 5)
        bb = self.bbox_u(M, 6)
        arcs, spokes = [], []
        r = r0
        while r < r1:
            n = max(8, int((a1 - a0) * r / 3.0))
            pts = [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n))
                   for i in range(n + 1)]
            arcs.extend(self._chop(pts, rng, gap, (30, 90), 3.0))
            r += sp * (1 + rng.uniform(-0.2, 0.2))
        ang = a0
        while ang < a1:
            for rr in (r0, r1):
                pass
            pts = [(c[0] + rr * math.cos(ang + 0.02 * math.sin(rr * 0.05)), c[1] + rr * math.sin(ang + 0.02 * math.sin(rr * 0.05)))
                   for rr in np.arange(r0, r1, 3.0)]
            spokes.extend(self._chop(pts, rng, 0.2, (20, 60), 3.0))
            ang += spoke_sp / ((r0 + r1) / 2)
        stubs = []
        for _ in range(cul):
            p = self.rand_in(M, rng)
            if not p:
                continue
            a_ = rng.uniform(0, TAU)
            q = (p[0] + 9 * math.cos(a_), p[1] + 9 * math.sin(a_))
            stubs.append([p, q])
            stubs.append([(q[0] + 2.2 * math.cos(t), q[1] + 2.2 * math.sin(t)) for t in np.linspace(0, TAU, 12)])
        self.lines(arcs, color, w, a, clip=M, bbox_units=bb)
        self.lines(spokes, color, w, a * 0.8, clip=M, bbox_units=bb)
        self.lines(stubs, color, w, a, clip=M, bbox_units=bb)

    def tex_radial(self, M, c, r0, r1, nspokes=24, ring_sp=10.0, color=(220, 220, 220), a=0.5, w=0.8, seed=0,
                   gap=0.1):
        rng = random.Random(seed + 9)
        bb = self.bbox_u(M, 6)
        rings, spokes = [], []
        r = r0
        while r < r1:
            n = max(12, int(TAU * r / 3.0))
            pts = [(c[0] + r * math.cos(TAU * i / n), c[1] + r * math.sin(TAU * i / n)) for i in range(n + 1)]
            rings.extend(self._chop(pts, rng, gap, (40, 120), 3.0))
            r += ring_sp
        for k in range(nspokes):
            ang = TAU * k / nspokes
            pts = [(c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang)) for rr in np.arange(r0, r1, 3.0)]
            spokes.append(pts)
        self.lines(rings, color, w, a, clip=M, bbox_units=bb)
        self.lines(spokes, color, w * 1.4, min(1, a * 1.5), clip=M, bbox_units=bb)

    def tex_super(self, M, angle=0.0, size=34.0, color=(220, 220, 220), bcolor=None, a=0.9, w=1.6, seed=0,
                  fill_prob=0.9, inset=0.12):
        """Superblock pattern: a coarse arterial grid; each cell holds one or more big plates / towers."""
        rng = random.Random(seed + 21)
        bb = self.bbox_u(M, 6)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        R = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 6
        ang = math.radians(angle)
        lines, plates, towers = [], [], []
        n = int(R / size) + 1
        for i in range(-n, n + 1):
            lines.append([rot((cx + i * size, cy + j), ang, (cx, cy)) for j in (-R, R)])
            lines.append([rot((cx + j, cy + i * size), ang, (cx, cy)) for j in (-R, R)])
        for i in range(-n, n):
            for j in range(-n, n):
                if rng.random() > fill_prob:
                    continue
                x0, y0 = cx + i * size, cy + j * size
                kind = rng.random()
                m = size * inset
                if kind < 0.5:
                    plates.append([rot(p, ang, (cx, cy)) for p in
                                   [(x0 + m, y0 + m), (x0 + size - m, y0 + m), (x0 + size - m, y0 + size - m),
                                    (x0 + m, y0 + size - m)]])
                elif kind < 0.8:
                    hw = size * 0.5 - m
                    for (ox, oy) in ((m, m), (size * 0.5 + 1, m), (m, size * 0.5 + 1), (size * 0.5 + 1, size * 0.5 + 1)):
                        if rng.random() < 0.75:
                            plates.append([rot(p, ang, (cx, cy)) for p in
                                           [(x0 + ox, y0 + oy), (x0 + ox + hw - 1, y0 + oy),
                                            (x0 + ox + hw - 1, y0 + oy + hw - 1), (x0 + ox, y0 + oy + hw - 1)]])
                else:
                    p = rot((x0 + size / 2, y0 + size / 2), ang, (cx, cy))
                    towers.append(circle_pts(p[0], p[1], size * 0.32, 18))
        self.lines(lines, color, w, a, clip=M, bbox_units=bb)
        self.polys(plates, bcolor or color, 0.42, clip=M, bbox_units=bb)
        self.polys(towers, bcolor or color, 0.55, clip=M, bbox_units=bb)

    def tex_industry(self, M, angle=0.0, cell=(15, 9), color=(150, 146, 138), a=0.55, seed=0, fill_prob=0.8):
        rng = random.Random(seed + 31)
        bb = self.bbox_u(M, 6)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        R = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 6
        ang = math.radians(angle)
        rects, roads = [], []
        n = int(R / min(cell)) + 1
        y = -R
        while y < R:
            h = cell[1] * rng.uniform(0.8, 1.4)
            x = -R
            while x < R:
                w = cell[0] * rng.uniform(0.7, 1.7)
                if rng.random() < fill_prob:
                    rects.append([rot((cx + x + 1, cy + y + 1), ang, (cx, cy)), rot((cx + x + w - 1.2, cy + y + 1), ang, (cx, cy)),
                                  rot((cx + x + w - 1.2, cy + y + h - 1.2), ang, (cx, cy)), rot((cx + x + 1, cy + y + h - 1.2), ang, (cx, cy))])
                x += w
            roads.append([rot((cx - R, cy + y), ang, (cx, cy)), rot((cx + R, cy + y), ang, (cx, cy))])
            y += h
        self.polys(rects, color, a, clip=M, bbox_units=bb)
        self.lines(roads, mix(color, (255, 255, 255), 0.3), 0.7, 0.35, clip=M, bbox_units=bb)

    def tex_slum(self, M, density=0.9, color=SLUM, a=0.7, seed=0, size=(0.9, 2.2)):
        rng = random.Random(seed + 41)
        bb = self.bbox_u(M, 0)
        area = float(self.mnp(M).sum())
        rects = []
        for _ in range(int(area * density)):
            p = self.rand_in(M, rng, 12)
            if p:
                rects.append(rect_pts(p[0], p[1], rng.uniform(*size), rng.uniform(*size), rng.uniform(0, 3.14)))
        self.polys(rects, color, a, clip=M, bbox_units=bb)

    def tex_dots(self, M, n, col, a=0.7, r=0.9, seed=0):
        rng = random.Random(seed + 51)
        bb = self.bbox_u(M, 0)
        polys = []
        for _ in range(n):
            p = self.rand_in(M, rng, 12)
            if p:
                polys.append(circle_pts(p[0], p[1], r * rng.uniform(0.7, 1.3), 8))
        self.polys(polys, col, a, clip=M, bbox_units=bb)

    def hatch(self, M, angle=45.0, sp=5.0, color=(200, 200, 200), a=0.2, w=0.8):
        bb = self.bbox_u(M, 4)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        R = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 4
        ang = math.radians(angle)
        lns = []
        pos = -R
        while pos < R:
            lns.append([rot((cx - R, cy + pos), ang, (cx, cy)), rot((cx + R, cy + pos), ang, (cx, cy))])
            pos += sp
        self.lines(lns, color, w, a, clip=M, bbox_units=bb)

    def fill_mask(self, M, color, alpha=1.0):
        self.img.paste(color, mask=M.point(lambda v: int(v * alpha)))

    def outline_mask(self, M, color, alpha=0.8, w=3):
        edge = M.filter(ImageFilter.FIND_EDGES)
        if w > 1:
            edge = edge.filter(ImageFilter.MaxFilter(w | 1))
        self.img.paste(color, mask=edge.point(lambda v: int(v * alpha)))

    # ---- green / civic -------------------------------------------------------------
    def park(self, poly, n_trees=None, seed=0, a=0.85, col=PARK, smooth=True, paths=True, free=False):
        if free:
            m, pts = self.free_mask(poly, smooth)
        else:
            m, pts = self.sub_mask(poly, None, smooth)
            self.occupy(m)
        self.fill_mask(m, col, a)
        bb = self.bbox_u(m, 0)
        area = float(self.mnp(m).sum())
        self.tex_dots(m, n_trees if n_trees is not None else int(area * 0.35), PARK_DARK, 0.9, 0.95, seed)
        self.line(pts + [pts[0]], (96, 150, 98), 0.8, 0.7, clip=self.dry)
        return m

    def plaza(self, poly, col=(214, 208, 190), a=0.55, smooth=False):
        m, pts = self.sub_mask(poly, None, smooth)
        self.occupy(m)
        self.fill_mask(m, col, a)
        self.line(pts + [pts[0]], (240, 236, 220), 0.8, 0.8, clip=self.dry)
        return m

    def built(self, poly, col, a=0.5, smooth=False, outline=True, free=False):
        if free:
            m, pts = self.free_mask(poly, smooth)
        else:
            m, pts = self.sub_mask(poly, None, smooth)
        self.fill_mask(m, col, a)
        if outline:
            self.line(pts + [pts[0]], tint(col, 0.4), 0.8, 0.8, clip=self.dry)
        return m

    # ---- network ---------------------------------------------------------------------
    def add_road(self, name, pts, cls='motorway', smooth=True, tunnels=(), ramp=False, step=3.0, label=None):
        dense = catmull(pts, step=step) if smooth and len(pts) > 2 else resample(pts, step)
        r = dict(name=name, pts=dense, cls=cls, tunnels=list(tunnels), ramp=ramp, label=label)
        self.roads.append(r)
        return r

    def add_rail(self, name, pts, kind='freight', smooth=True, tunnels=(), step=3.0):
        dense = catmull(pts, step=step) if smooth and len(pts) > 2 else resample(pts, step)
        r = dict(name=name, pts=dense, kind=kind, tunnels=list(tunnels))
        self.rails.append(r)
        return r

    @staticmethod
    def _split(pts, tunnels):
        """Split into [(sub_pts, is_tunnel)] by arclength fractions."""
        if not tunnels:
            return [(pts, False)]
        cuts = sorted(tunnels)
        out = []
        prev = 0.0
        for a, b in cuts:
            if a > prev:
                out.append((sub(pts, prev, a), False))
            out.append((sub(pts, a, b), True))
            prev = b
        if prev < 1.0:
            out.append((sub(pts, prev, 1.0), False))
        return out

    def draw_rails(self):
        for r in self.rails:
            for pts, tun in self._split(r['pts'], r['tunnels']):
                if r['kind'] == 'freight':
                    if tun:
                        self.line(pts, (210, 210, 215), 1.6, 0.5, dash=(3, 3))
                        continue
                    self.line(pts, (6, 8, 12), 5.6)
                    self.line(pts, (232, 232, 236), 3.4)
                    self.line(pts, (24, 26, 34), 3.4, dash=(2.1, 2.1))
                elif r['kind'] == 'commuter':
                    if tun:
                        self.line(pts, (200, 205, 220), 1.6, 0.5, dash=(3, 3))
                        continue
                    self.line(pts, (6, 8, 12), 4.4)
                    self.line(pts, (190, 198, 214), 2.4)
                else:  # metro
                    if tun:
                        self.line(pts, (255, 255, 255), 1.8, 0.7, dash=(2.5, 2.5))
                        continue
                    self.line(pts, (6, 8, 12), 4.6)
                    self.line(pts, (255, 255, 255), 2.4)

    def _road_style(self, cls):
        return {
            'ring': (11.5, 8.0, ROAD_FILL),
            'motorway': (9.5, 6.4, ROAD_FILL),
            'truck': (9.0, 6.0, (210, 214, 220)),
            'arterial': (4.8, 3.0, (196, 202, 214)),
            'collector': (3.2, 1.8, (170, 176, 190)),
        }[cls]

    def draw_roads(self, bridges=True):
        wet = self.wet_np() if bridges else None
        order = ['collector', 'arterial', 'truck', 'motorway', 'ring']
        for cls in order:
            rs = [r for r in self.roads if r['cls'] == cls]
            if not rs:
                continue
            cw, fw, fc = self._road_style(cls)
            for r in rs:
                for pts, tun in self._split(r['pts'], r['tunnels']):
                    if tun:
                        self.line(pts, (6, 8, 12), cw * 0.55, 0.65, dash=(3, 3))
                        self.line(pts, fc, fw * 0.45, 0.55, dash=(3, 3))
            for r in rs:
                for pts, tun in self._split(r['pts'], r['tunnels']):
                    if not tun:
                        self.line(pts, ROAD_CASING, cw)
            for r in rs:
                for pts, tun in self._split(r['pts'], r['tunnels']):
                    if not tun:
                        self.line(pts, fc, fw)
                        if cls == 'truck':
                            self.line(pts, (255, 150, 30), 1.4, dash=(3, 3))
            if wet is not None and cls in ('truck', 'motorway', 'ring', 'arterial'):
                for r in rs:
                    self._bridges(r, cw, fw, fc, wet)

    def _bridges(self, r, cw, fw, fc, wet):
        pts = r['pts']
        run = []
        runs = []
        for p in pts:
            x, y = int(p[0]), int(p[1])
            w = 0 <= x < U and 0 <= y < U and wet[y, x]
            if w:
                run.append(p)
            else:
                if len(run) > 2:
                    runs.append(run)
                run = []
        if len(run) > 2:
            runs.append(run)
        for run in runs:
            if plen(run) < 6:
                continue
            self.line(run, (236, 246, 255), cw + 2.4)
            self.line(run, ROAD_CASING, cw)
            self.line(run, fc, fw)

    def interchange(self, p, a, b, style='stack', size=1.0):
        """Draw a grade-separated interchange with ramps. a, b = directions (rad) of the two roads."""
        f = self.f
        a %= math.pi
        b %= math.pi
        m = (a + b) / 2
        R = 8.0 * size
        x, y = p
        if style == 'stack':
            for k in range(4):
                bis = m + k * math.pi / 2
                cxu = x + math.cos(bis) * R * 0.66 / FPU
                cyu = y + math.sin(bis) * R * 0.66 / FPU
                self.circle(cxu, cyu, R * 0.46, None, ROAD_CASING, 3.4)
            for k in range(4):
                bis = m + k * math.pi / 2
                cxu = x + math.cos(bis) * R * 0.66 / FPU
                cyu = y + math.sin(bis) * R * 0.66 / FPU
                self.circle(cxu, cyu, R * 0.46, None, (255, 214, 120), 1.5)
            self.circle(x, y, R * 0.35, (10, 12, 18), (255, 255, 255), 1.4)
        elif style == 'diamond':
            t = (math.cos(a), math.sin(a))
            n = (-t[1], t[0])
            for sgn in (-1, 1):
                for k in (-1, 1):
                    p0 = (x + t[0] * sgn * 9, y + t[1] * sgn * 9)
                    p1 = (x + t[0] * sgn * 2.6 + n[0] * k * 3.0, y + t[1] * sgn * 2.6 + n[1] * k * 3.0)
                    p2 = (x + t[0] * sgn * 9 + n[0] * k * 2.0, y + t[1] * sgn * 9 + n[1] * k * 2.0)
                    self.line([p0, p2, p1], ROAD_CASING, 3.4)
            for sgn in (-1, 1):
                for k in (-1, 1):
                    p0 = (x + t[0] * sgn * 9, y + t[1] * sgn * 9)
                    p1 = (x + t[0] * sgn * 2.6 + n[0] * k * 3.0, y + t[1] * sgn * 2.6 + n[1] * k * 3.0)
                    p2 = (x + t[0] * sgn * 9 + n[0] * k * 2.0, y + t[1] * sgn * 2.0 * 0 + t[1] * sgn * 9 + n[1] * k * 2.0)
                    self.line([p0, p2, p1], (255, 214, 120), 1.3)
            self.circle(x, y, 2.4, (10, 12, 18), (255, 255, 255), 1.1)

    def auto_interchanges(self, min_sep=9.0, arterial_ramps=True, skip=()):
        mclasses = ('ring', 'motorway', 'truck')
        done = []
        found = []
        for i, r1 in enumerate(self.roads):
            for j, r2 in enumerate(self.roads):
                if j <= i:
                    continue
                c1, c2 = r1['cls'], r2['cls']
                if c1 in mclasses and c2 in mclasses:
                    sty = 'stack'
                elif arterial_ramps and ((c1 in mclasses and c2 == 'arterial' and r2['ramp']) or
                                         (c2 in mclasses and c1 == 'arterial' and r1['ramp'])):
                    sty = 'diamond'
                else:
                    continue
                for p, aa, bb in seg_intersections(r1['pts'], r2['pts']):
                    if any(dist(p, q) < min_sep for q in done):
                        continue
                    if any(dist(p, q) < 6 for q in skip):
                        continue
                    done.append(p)
                    found.append((p, aa, bb, sty))
        found.sort(key=lambda t: 0 if t[3] == 'diamond' else 1)
        for p, aa, bb, sty in found:
            self.interchange(p, aa, bb, sty)
        return [t[0] for t in found]

    def junction(self, p, style='stack', ang_a=0.0, ang_b=math.pi / 2):
        self.interchange(p, ang_a, ang_b, style)

    def station(self, x, y, kind='metro', label=None, ldx=0, ldy=-7, size=10):
        if kind == 'metro':
            self.circle(x, y, 3.6, (255, 255, 255), (8, 10, 14), 1.4)
        elif kind == 'rail':
            self.circle(x, y, 4.0, (200, 206, 224), (8, 10, 14), 1.6)
            self.circle(x, y, 1.6, (8, 10, 14))
        elif kind == 'freight':
            self.circle(x, y, 3.4, (255, 190, 90), (8, 10, 14), 1.4)
        elif kind == 'hub':
            self.circle(x, y, 8.0, (8, 10, 14), (255, 255, 255), 2.0)
            self.circle(x, y, 4.0, (255, 255, 255), (8, 10, 14), 1.2)
        elif kind == 'depot':
            self.circle(x, y, 3.2, (130, 134, 150), (8, 10, 14), 1.2)
        if label:
            self.text(x + ldx, y + ldy, label, size, TEXT, weight='SemiBold')

    # ---- walls and cyber overlays ---------------------------------------------------------
    def wall(self, pts, color, closed=False, clip=True):
        pts = list(pts) + ([pts[0]] if closed else [])
        c = self.dry if clip else None
        self.line(pts, (6, 8, 12), 4.6, 0.9, clip=c)
        self.line(pts, tint(color, 0.25), 2.6, 0.95, clip=c, dash=(9, 1.6))
        return pts

    def gates_on(self, wall_pts, roads=None, glyph_r=5.0, min_sep=14.0, classes=('ring', 'motorway', 'truck', 'arterial')):
        done = []
        for r in (roads or self.roads):
            if r['cls'] not in classes:
                continue
            for p, aa, bb in seg_intersections(wall_pts, r['pts']):
                if any(dist(p, q) < min_sep for q in done):
                    continue
                done.append(p)
                self.glyph('checkpoint', p[0], p[1], glyph_r)
        self.gate_pts += done
        return done

    def seawall(self, pts, w=3.4):
        L = plen(pts)
        self.line(pts, (6, 8, 12), w + 2.2, 0.9)
        self.line(pts, (206, 220, 236), w)
        # teeth on the land side
        landnp = self.mnp(self.land)
        res = resample(pts, 5.0)
        ticks = []
        for i in range(1, len(res) - 1):
            a, b = res[i - 1], res[i + 1]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            nx, ny = -math.sin(ang), math.cos(ang)
            for sg in (1, -1):
                qx, qy = res[i][0] + nx * sg * 3, res[i][1] + ny * sg * 3
                xi, yi = int(qx), int(qy)
                if 0 <= xi < U and 0 <= yi < U and landnp[yi, xi]:
                    ticks.append([res[i], (res[i][0] + nx * sg * 2.2, res[i][1] + ny * sg * 2.2)])
        for tk in ticks:
            self.line(tk, (206, 220, 236), 1.0, 0.8)

    def dam(self, pts, w=5.0, sluices=True):
        self.line(pts, (6, 8, 12), w + 2.4)
        self.line(pts, (225, 232, 240), w)
        self.line(pts, (60, 70, 90), w * 0.35, dash=(2.0, 2.0))
        if sluices:
            res = resample(pts, 12.0)
            for i in range(1, len(res) - 1):
                a, b = res[i - 1], res[i + 1]
                ang = math.atan2(b[1] - a[1], b[0] - a[0])
                nx, ny = -math.sin(ang) * 3.2, math.cos(ang) * 3.2
                self.line([(res[i][0] + nx, res[i][1] + ny), (res[i][0] - nx, res[i][1] - ny)], (6, 8, 12), 2.6)
                self.line([(res[i][0] + nx, res[i][1] + ny), (res[i][0] - nx, res[i][1] - ny)], (255, 214, 120), 1.2)

    def drone_corridor(self, pts, color=(80, 235, 255), w=1.3, a=0.85, smooth=True):
        dense = catmull(pts, step=3.0) if smooth and len(pts) > 2 else resample(pts, 3.0)
        self.line(dense, color, w, a, dash=(4, 3))
        res = resample(dense, 70.0)
        for i in range(1, len(res)):
            p, q = res[i - 1], res[i]
            ang = math.atan2(q[1] - p[1], q[0] - p[0])
            m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            s = 3.0
            tri = [(m[0] + s * math.cos(ang), m[1] + s * math.sin(ang)),
                   (m[0] + s * 0.7 * math.cos(ang + 2.5), m[1] + s * 0.7 * math.sin(ang + 2.5)),
                   (m[0] + s * 0.7 * math.cos(ang - 2.5), m[1] + s * 0.7 * math.sin(ang - 2.5))]
            self.poly(tri, color, a)

    def undercity(self, poly, color=(190, 130, 255)):
        m, pts = self.sub_mask(poly, None, True)
        self.hatch(m, 45, 4.5, color, 0.22, 0.8)
        self.line(pts + [pts[0]], color, 1.4, 0.9, dash=(2, 2.5), clip=self.dry)
        return m

    def label_curved(self, text, pts, size=16, color=TEXT, spacing=6, halo=True, frac=0.5, weight='Bold', alpha=255):
        p, ang = pt_at(pts, plen(pts) * frac)
        deg = -math.degrees(ang)
        if deg < -90:
            deg += 180
        if deg > 90:
            deg -= 180
        self.text(p[0], p[1], text, size, color, angle=deg, spacing=spacing, halo=halo, weight=weight, alpha=alpha)

    # ---- landmarks (plan view) ----------------------------------------------------------------
    def panopticon(self, x, y, s, col=COL['halcyon'], cone_to=None, cone_w=0.35):
        if cone_to is not None:
            ang = math.atan2(cone_to[1] - y, cone_to[0] - x)
            L = dist((x, y), cone_to)
            tri = [(x, y), (x + L * math.cos(ang - cone_w), y + L * math.sin(ang - cone_w)),
                   (x + L * math.cos(ang + cone_w), y + L * math.sin(ang + cone_w))]
            self.poly(tri, col, 0.07)
            self.line([(x, y), (x + L * math.cos(ang - cone_w), y + L * math.sin(ang - cone_w))], col, 0.8, 0.45, dash=(3, 3))
            self.line([(x, y), (x + L * math.cos(ang + cone_w), y + L * math.sin(ang + cone_w))], col, 0.8, 0.45, dash=(3, 3))
        self.poly(circle_pts(x, y, s * 1.25, 48), col, 0.14)
        for k in range(24):
            a = TAU * k / 24
            self.line([(x + s * 0.75 * math.cos(a), y + s * 0.75 * math.sin(a)),
                       (x + s * 1.25 * math.cos(a), y + s * 1.25 * math.sin(a))], col, 0.8, 0.6)
        self.line(circle_pts(x, y, s * 1.25, 48) + [circle_pts(x, y, s * 1.25, 48)[0]], col, 1.2, 0.9)
        sq = rect_pts(x, y, s * 1.1, s * 1.1, 0)
        self.poly(sq, (22, 8, 12), 1.0, tint(col, 0.2), 2.0)
        for q in sq:
            self.line([q, (x, y)], col, 1.0, 0.85)
        self.poly(rect_pts(x, y, s * 0.55, s * 0.55, 0), None, 1.0, col, 1.2)
        self.poly(ellipse_pts(x, y, s * 0.3, s * 0.17, 0, 24), col, 1.0)
        self.circle(x, y, max(2.0, s * FPU * 0.09), (14, 6, 8))

    def helix(self, x, y, s, ang=0.0, col=COL['solace']):
        self.poly(ellipse_pts(x, y, s * 1.5, s * 0.95, ang, 40), col, 0.14, col, 1.0, 0.8)
        cax, say = math.cos(ang), math.sin(ang)
        for sg in (-1, 1):
            p = (x + sg * s * 0.62 * cax, y + sg * s * 0.62 * say)
            self.poly(circle_pts(p[0], p[1], s * 0.38, 28), (6, 24, 20), 1.0, tint(col, 0.2), 2.0)
            spiral = []
            for t in np.linspace(0, 2.6 * math.pi, 28):
                r = s * 0.34 * (t / (2.6 * math.pi))
                spiral.append((p[0] + r * math.cos(t * sg), p[1] + r * math.sin(t * sg)))
            self.line(spiral, col, 1.2, 0.95)
        n = 32
        for ph in (0.0, math.pi):
            pts = []
            for i in range(n + 1):
                t = i / n
                lx = (t - 0.5) * s * 1.24
                ly = math.sin(t * 3 * math.pi + ph) * s * 0.32
                pts.append(rot((x + lx, y + ly), ang, (x, y)))
            self.line(pts, tint(col, 0.35), 1.6, 0.95)
        for i in range(2, n - 1, 3):
            t = i / n
            lx = (t - 0.5) * s * 1.24
            ly = math.sin(t * 3 * math.pi) * s * 0.32
            self.line([rot((x + lx, y + ly), ang, (x, y)), rot((x + lx, y - ly), ang, (x, y))], col, 0.8, 0.8)

    def launch_ring(self, x, y, s, az, col=COL['orbital'], zone_r=None, zone_a=0.12):
        if zone_r:
            zp = circle_pts(x, y, zone_r, 90)
            self.poly(zp, (255, 80, 90), zone_a)
            self.line(zp + [zp[0]], (255, 90, 100), 1.2, 0.9, dash=(5, 3))
            self.text(x + zone_r * 0.62 * math.cos(az + 1.9), y + zone_r * 0.62 * math.sin(az + 1.9),
                      'EXCLUSION ZONE', 9, (255, 150, 150), spacing=1.5, weight='SemiBold')
        ring = circle_pts(x, y, s, 60)
        self.poly(ring, (10, 8, 24), 0.95)
        self.line(ring + [ring[0]], tint(col, 0.2), 3.4)
        self.line(ring + [ring[0]], (10, 8, 24), 1.0)
        for k in range(8):
            a = TAU * k / 8
            self.line([(x + s * 0.2 * math.cos(a), y + s * 0.2 * math.sin(a)),
                       (x + s * 0.95 * math.cos(a), y + s * 0.95 * math.sin(a))], col, 0.9, 0.7)
        # rocket silhouette along azimuth
        L = s * 1.0
        def R(px, py):
            return rot((x + px, y + py), az, (x, y))
        body = [R(L * 0.55, 0), R(L * 0.3, -L * 0.11), R(-L * 0.38, -L * 0.11), R(-L * 0.38, L * 0.11), R(L * 0.3, L * 0.11)]
        fins = [R(-L * 0.2, -L * 0.11), R(-L * 0.5, -L * 0.3), R(-L * 0.38, -L * 0.11)]
        fins2 = [R(-L * 0.2, L * 0.11), R(-L * 0.5, L * 0.3), R(-L * 0.38, L * 0.11)]
        self.poly(body, (240, 240, 250), 1.0)
        self.poly(fins, tint(col, 0.3), 1.0)
        self.poly(fins2, tint(col, 0.3), 1.0)
        if zone_r:
            p0 = (x + (s + 4) * math.cos(az), y + (s + 4) * math.sin(az))
            p1 = (x + zone_r * 1.3 * math.cos(az), y + zone_r * 1.3 * math.sin(az))
            self.line([p0, p1], (255, 150, 150), 1.4, 0.95, dash=(4, 3))
            tri = [p1, (p1[0] - 6 * math.cos(az - 0.4), p1[1] - 6 * math.sin(az - 0.4)),
                   (p1[0] - 6 * math.cos(az + 0.4), p1[1] - 6 * math.sin(az + 0.4))]
            self.poly(tri, (255, 150, 150), 0.95)

    def gantry_castle(self, x, y, s, ang=0.0, col=COL['meridian'], cranes=(0.0,), crane_len=2.0):
        wall = rect_pts(x, y, s * 2.2, s * 2.2, ang)
        self.poly(wall, (24, 14, 6), 0.9, tint(col, 0.2), 2.4)
        for q in wall:
            self.poly(circle_pts(q[0], q[1], s * 0.2, 14), (24, 14, 6), 1.0, tint(col, 0.3), 1.6)
        keep = rect_pts(x, y, s * 0.95, s * 0.95, ang)
        self.poly(keep, col, 0.9, (255, 235, 200), 1.4)
        for k in range(1, 4):
            self.poly(rect_pts(x, y, s * (0.95 - 0.2 * k), s * (0.95 - 0.2 * k), ang), None, 1.0, (60, 30, 6), 0.9)
        for cdir in cranes:
            a = ang + cdir
            base = (x + s * 1.1 * math.cos(a), y + s * 1.1 * math.sin(a))
            tip = (x + s * (1.1 + crane_len) * math.cos(a), y + s * (1.1 + crane_len) * math.sin(a))
            nx, ny = -math.sin(a) * s * 0.34, math.cos(a) * s * 0.34
            for sg in (-1, 1):
                self.line([(base[0] + sg * nx, base[1] + sg * ny), (tip[0] + sg * nx, tip[1] + sg * ny)],
                          tint(col, 0.3), 1.8)
            n = 6
            for i in range(n + 1):
                t = i / n
                px, py = lerp(base[0], tip[0], t), lerp(base[1], tip[1], t)
                self.line([(px + nx, py + ny), (px - nx, py - ny)], tint(col, 0.2), 1.0, 0.9)
            self.line([base, tip], col, 1.0, 0.9)

    def circus(self, x, y, s, ang=0.0, col=COL['aurelian']):
        # colosseum
        self.poly(ellipse_pts(x, y, s * 1.3, s * 1.0, ang, 56), (28, 22, 6), 0.95, tint(col, 0.25), 2.2)
        self.poly(ellipse_pts(x, y, s * 0.98, s * 0.72, ang, 56), None, 1.0, tint(col, 0.1), 1.2)
        for k in range(32):
            a = TAU * k / 32
            p0 = rot((x + s * 0.98 * math.cos(a), y + s * 0.72 * math.sin(a)), ang, (x, y))
            p1 = rot((x + s * 1.3 * math.cos(a), y + s * 1.0 * math.sin(a)), ang, (x, y))
            self.line([p0, p1], col, 0.9, 0.85)
        self.poly(ellipse_pts(x, y, s * 0.6, s * 0.38, ang, 40), (230, 200, 120), 0.8)
        self.poly(ellipse_pts(x, y, s * 0.6, s * 0.38, ang, 40), None, 1.0, (80, 60, 10), 1.0)

    def pier_city(self, x, y, s, ang=0.0, col=COL['tethys'], n=9, spread=1.9):
        """Plan of a floating pier city: dome hub + fan of piers + ring promenade."""
        self.poly(circle_pts(x, y, s * 0.9, 40), col, 0.12)
        for i in range(n):
            a = ang + (i / (n - 1) - 0.5) * spread
            ln = s * (1.1 + 0.5 * math.sin(i * 1.7) ** 2)
            w = s * 0.11
            p0 = (x + s * 0.3 * math.cos(a), y + s * 0.3 * math.sin(a))
            p1 = (x + ln * math.cos(a), y + ln * math.sin(a))
            self.line([p0, p1], (6, 14, 20), 6.2)
            self.line([p0, p1], tint(col, 0.2), 4.0)
            self.circle(p1[0], p1[1], 4.4, (10, 30, 40), tint(col, 0.2), 1.4)
        arc = arc_pts(x, y, s * 0.6, ang - spread / 2 - 0.1, ang + spread / 2 + 0.1, 24)
        self.line(arc, (6, 14, 20), 4.4)
        self.line(arc, tint(col, 0.35), 2.6)
        self.poly(circle_pts(x, y, s * 0.3, 28), (6, 24, 32), 1.0, tint(col, 0.2), 2.0)
        self.circle(x, y, 4.0, tint(col, 0.5))

    def port_piers(self, specs, col=(120, 130, 146), cont_cols=((200, 90, 60), (70, 130, 200), (210, 190, 70), (90, 170, 120))):
        rng = random.Random(self.seed + 71)
        for (x, y, ln, wd, ang) in specs:
            r = rect_pts(x + ln / 2 * math.cos(ang), y + ln / 2 * math.sin(ang), ln, wd, ang)
            self.poly(r, (6, 8, 12), 1.0, None)
            self.poly([(p[0], p[1]) for p in r], col, 1.0, (200, 210, 224), 0.9)
            # container stacks
            k = int(ln / 3.0)
            for i in range(k):
                px = x + (i + 0.5) * ln / k * math.cos(ang)
                py = y + (i + 0.5) * ln / k * math.sin(ang)
                for sg in (-1, 1):
                    q = rect_pts(px + sg * wd * 0.25 * -math.sin(ang), py + sg * wd * 0.25 * math.cos(ang),
                                 ln / k * 0.82, wd * 0.34, ang)
                    self.poly(q, rng.choice(cont_cols), 0.85)

    def container_yard(self, cx, cy, w, h, ang=0.0, cell=(2.6, 1.1), seed=0, clip=None):
        rng = random.Random(seed + 88)
        cols = ((200, 90, 60), (70, 130, 200), (210, 190, 70), (90, 170, 120), (150, 150, 160), (210, 120, 150))
        by_col = {c: [] for c in cols}
        nx, ny = int(w / cell[0]), int(h / cell[1])
        for i in range(nx):
            if i % 7 == 6:
                continue
            for j in range(ny):
                if j % 6 == 5:
                    continue
                if rng.random() < 0.12:
                    continue
                px = -w / 2 + (i + 0.5) * cell[0]
                py = -h / 2 + (j + 0.5) * cell[1]
                q = rect_pts(cx, cy, 0, 0, 0)
                pts = [rot((cx + px + dx, cy + py + dy), ang, (cx, cy))
                       for dx, dy in ((-cell[0] * 0.42, -cell[1] * 0.4), (cell[0] * 0.42, -cell[1] * 0.4),
                                      (cell[0] * 0.42, cell[1] * 0.4), (-cell[0] * 0.42, cell[1] * 0.4))]
                by_col[rng.choice(cols)].append(pts)
        for c, lst in by_col.items():
            self.polys(lst, c, 0.8, clip=clip)

    # ---- extra helpers ------------------------------------------------------------------------------
    def coast_seg(self, pred, min_len=8):
        runs, cur = [], []
        for p in self.coast:
            if pred(p):
                cur.append(p)
            else:
                if len(cur) >= min_len:
                    runs.append(cur)
                cur = []
        if len(cur) >= min_len:
            runs.append(cur)
        return runs

    def industry(self, poly, color=INDUSTRY, angle=0.0, seed=0, cell=(15, 9), smooth=False, a=0.55, tint_a=0.16,
                 free=True):
        if free:
            m, pts = self.free_mask(poly, smooth)
        else:
            m, pts = self.sub_mask(poly, None, smooth)
        self.fill_mask(m, color, tint_a)
        self.tex_industry(m, angle, cell, mix(color, (255, 255, 255), 0.15), a, seed)
        self.line(pts + [pts[0]], mix(color, (255, 255, 255), 0.4), 0.8, 0.8, clip=self.dry)
        return m

    def stations_along(self, line, fracs, kind='metro'):
        c = cum(line['pts'])
        out = []
        for f in fracs:
            p, _a = pt_at(line['pts'], c[-1] * f, c)
            self.station(p[0], p[1], kind)
            out.append(p)
        return out

    def airport(self, cx, cy, ang, rw_len=95, rw_gap=14, col=(230, 236, 250)):
        a = ang
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        for sg in (-1, 1):
            c0 = (cx + nx * sg * rw_gap / 2, cy + ny * sg * rw_gap / 2)
            p0 = (c0[0] - ca * rw_len / 2, c0[1] - sa * rw_len / 2)
            p1 = (c0[0] + ca * rw_len / 2, c0[1] + sa * rw_len / 2)
            self.line([p0, p1], (6, 8, 12), 5.6)
            self.line([p0, p1], (150, 156, 170), 3.8)
            self.line([p0, p1], col, 1.0, dash=(3, 3))
        # terminal + apron
        t0 = (cx + nx * 0, cy + ny * 0)
        self.poly(rect_pts(cx - ca * 8, cy - sa * 8, 30, 5, a), (60, 70, 90), 1.0, (200, 210, 230), 1.0)
        self.poly(rect_pts(cx - ca * 8 + nx * 0, cy - sa * 8, 8, 8, a), (120, 130, 150), 1.0)

    def ferry(self, pts, color=(150, 225, 255), terminals=True):
        dense = catmull(pts, step=3.0) if len(pts) > 2 else resample(pts, 3.0)
        self.line(dense, color, 1.2, 0.8, dash=(1.6, 2.4))
        if terminals:
            for p in (pts[0], pts[-1]):
                self.circle(p[0], p[1], 3.0, (8, 10, 16), color, 1.4)
        res = resample(dense, 90.0)
        for i in range(1, len(res) - 1):
            a, b = res[i - 1], res[i + 1]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            q = res[i]
            hull = [(q[0] + 4 * math.cos(ang), q[1] + 4 * math.sin(ang)),
                    (q[0] + 2.4 * math.cos(ang + 2.5), q[1] + 2.4 * math.sin(ang + 2.5)),
                    (q[0] + 2.4 * math.cos(ang - 2.5), q[1] + 2.4 * math.sin(ang - 2.5))]
            self.poly(hull, color, 0.9)

    def windfarm(self, poly, sp=14.0, seed=0):
        rng = random.Random(seed + 5)
        m_, pts = self.sub_mask_water(poly)
        bb = self.bbox_u(m_, 0)
        y = bb[1]
        row = 0
        while y < bb[3]:
            x = bb[0] + (sp / 2 if row % 2 else 0)
            while x < bb[2]:
                if self.mnp(m_)[min(U - 1, int(y)), min(U - 1, int(x))]:
                    self.circle(x, y, 1.6, (230, 240, 250), None)
                    for k in range(3):
                        a = k * 2.094 + rng.uniform(0, 1)
                        self.line([(x, y), (x + 3.2 * math.cos(a), y + 3.2 * math.sin(a))], (230, 240, 250), 0.9, 0.9)
                x += sp
            y += sp * 0.9
            row += 1
        self.line(pts + [pts[0]], (230, 240, 250), 0.8, 0.35, dash=(3, 3))

    def sub_mask_water(self, poly):
        pts = catmull(poly, closed=True, step=3.0)
        m = ImageChops.multiply(self.poly_mask(pts), self.ocean)
        return m, pts

    def town(self, cx, cy, r, seed=0, name=None, angle=None):
        """Small satellite town: organic core + grid fringe, drawn on free land."""
        rng = random.Random(seed + 61)
        poly = blob(cx, cy, r, r * 0.8, rng, 0.2, 10, rng.uniform(0, 3))
        mk, pts = self.free_mask(poly, True)
        self.fill_mask(mk, (200, 190, 170), 0.16)
        self.tex_walks(mk, int(r * 2.2), (10, 30), 0.4, color=(215, 205, 185), a=0.6, seed=seed)
        self.tex_grid(mk, angle if angle is not None else rng.uniform(0, 90), 6, jitter=0.2, gap=0.3, color=(215, 205, 185),
                      a_minor=0.4, seed=seed)
        self.line(pts + [pts[0]], (215, 205, 185), 0.8, 0.5, clip=self.dry)
        if name:
            self.text(cx, cy + r * 0.8 + 8, name, 7.5, (200, 205, 215), weight='Regular')

    # ---- frame, scale, north --------------------------------------------------------------------
    def grid_ticks(self):
        for k in range(1, 4):
            v = k * 250
            self.line([(v, 0), (v, U)], (200, 220, 240), 0.6, 0.07, dash=(3, 6))
            self.line([(0, v), (U, v)], (200, 220, 240), 0.6, 0.07, dash=(3, 6))

    def scalebar(self, x, y):
        self.poly([(x - 12, y - 24), (x + 275, y - 24), (x + 275, y + 18), (x - 12, y + 18)], (6, 8, 12), 0.82,
                  (120, 130, 150), 1.0, 0.6)
        for i in range(5):
            x0 = x + i * 50
            self.poly([(x0, y - 6), (x0 + 50, y - 6), (x0 + 50, y + 2), (x0, y + 2)],
                      (240, 240, 240) if i % 2 == 0 else (30, 34, 44), 1.0, (240, 240, 240), 0.8)
        for i, t in enumerate(('0', '1', '2', '3', '4', '5 km')):
            self.text(x + i * 50 + (6 if i == 5 else 0), y - 15, t, 10, TEXT, weight='SemiBold')

    def north(self, x, y, r=22):
        self.poly(circle_pts(x, y, r + 8, 40), (6, 8, 12), 0.82, (120, 130, 150), 1.0, 0.6)
        self.poly([(x, y - r), (x + r * 0.28, y), (x, y - r * 0.2), (x - r * 0.28, y)], (240, 240, 240), 1.0)
        self.poly([(x, y + r), (x + r * 0.28, y), (x, y + r * 0.2), (x - r * 0.28, y)], (90, 96, 110), 1.0)
        self.text(x, y - r - 12, 'N', 13, TEXT)

    def title_block(self, x, y, title, sub):
        self.text(x, y, title, 40, TEXT, spacing=3, title=True, anchor='lm', halo_w=5)
        self.text(x, y + 22, sub, 13, (170, 180, 200), anchor='lm', weight='SemiBold')

    def save_map(self, path, size=2000):
        self.img.resize((size, size), Image.LANCZOS).save(path)
        return path

    def final(self, size=2000):
        return self.img.resize((size, size), Image.LANCZOS)
