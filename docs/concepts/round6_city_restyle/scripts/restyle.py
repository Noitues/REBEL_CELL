"""Round 6: the game's own city (exported by tools/design_lab/city_export.gd) re-rendered with
our buildings: Cv2 triangle facets, E's 3 hard toon bands, wobbly ink, painted grime.

Kept from the game: the layout (every extrusion's footprint, base, height and taper, in the
game's own draw order), the HQ designs (their extrusions restyled, their decoration and
neon kept), the glowing neon streets (same inks, traffic widths, glow), the fist roads,
traffic trails and beacons. Replaced: every building's surface (faceted, banded, inked,
grimed, district-tinted, with window lights and neon roof trims).

Usage: python restyle.py <city_layout.json>      (writes ../after_night.png, crops, compare)
"""
import json
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import lowpoly
from lowpoly import SS, R, hexc, mix, ramp, facet, bil, tri, line2, poly_fpos
import toon
from toon import ink_line, ink_poly, hull, paint_texture
from city import FAM

OUT = os.path.dirname(HERE)
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'


def c255(c):
    return tuple(int(round(max(0, min(1, v)) * 255)) for v in c[:3])


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


# night toon bands (see round 5): cool moonlit shadows, violet-lit tops
toon.TINT = ((hexc('#120e3a'), 0.30), (hexc('#1a1446'), 0.10), (hexc('#8a7cff'), 0.08))
toon.BEVEL = hexc('#9a8ec8')
BANDS = (0.30, 0.50, 0.70)
FAMKEYS = ['soot', 'concrete', 'corp', 'oily', 'brick', 'concrete', 'corp', 'rust']
NIGHT_DARK = hexc('#05061a')


def h01(*v):
    return lowpoly.hsh(*v)


class View:
    def __init__(self, x0, y0, scale, w, h):
        self.x0, self.y0, self.s, self.w, self.h = x0, y0, scale, w, h
        self.k = scale / 0.633      # stroke widths relative to the full view

    def p(self, x, y):
        return ((x - self.x0) * self.s, (y - self.y0) * self.s)

    def pts(self, flat):
        return [self.p(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]

    def visible(self, pts, pad=40):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return max(xs) > -pad and min(xs) < self.w + pad and max(ys) > -pad and min(ys) < self.h + pad


class Restyler:
    def __init__(self, data, view):
        self.d = data
        self.v = view
        self.ctxs = data['contexts']
        self.terr_col = {t['id']: c255(t['color']) for t in data['territories']}
        self.fams = {}

    # ---- colour families
    def fam_for(self, ctx_i):
        if ctx_i in self.fams:
            return self.fams[ctx_i]
        ctx = self.ctxs[ctx_i] if ctx_i >= 0 else {'kind': 'bld', 'terr': ''}
        terr = ctx.get('terr', '')
        if ctx['kind'] == 'hq':
            base = FAM['corp']
            amt = 0.42
        else:
            key = FAMKEYS[int(h01(ctx_i, 3) * len(FAMKEYS))]
            base = FAM[key]
            amt = 0.3 if terr else 0.0
            # border blend: some buildings take the neighbour's colour
            if ctx.get('border', 0) > 0 and h01(ctx_i, 41) < ctx['border'] * 0.5:
                terr = ctx.get('next', terr)
        col = self.terr_col.get(terr, (200, 200, 200))
        st = [mix(mix(s, col, amt), NIGHT_DARK, 0.28) for s in base]
        self.fams[ctx_i] = (st, col)
        return st, col

    @staticmethod
    def bcol(stops, band, j=0.0):
        return toon.tint(ramp(stops, BANDS[band] + j), band)

    # ---- an extrusion, restyled
    def ext(self, d, pr, gl):
        v = self.v
        base = v.pts(pr['b'])
        z0, hh, ts = pr['z0'] * v.s, pr['h'] * v.s, pr['ts']
        n = len(base)
        c = (sum(p[0] for p in base) / n, sum(p[1] for p in base) / n)
        bot = [(p[0], p[1] - z0) for p in base]
        top = [(c[0] + (p[0] - c[0]) * ts, c[1] + (p[1] - c[1]) * ts - z0 - hh) for p in base]
        if not v.visible(bot + top):
            return
        ci = pr['ctx']
        stops, tcol = self.fam_for(ci)
        ink = c255(pr['ink'])
        hq = ci >= 0 and self.ctxs[ci]['kind'] == 'hq'
        seed = (ci, pr['key'], round(pr['z0']))
        faces = []
        cz = (c[0], c[1] - z0)
        for k in range(n):
            a, b = bot[k], bot[(k + 1) % n]
            ex, ey = b[0] - a[0], b[1] - a[1]
            L = math.hypot(ex, ey) or 1.0
            nx, ny = ey / L, -ex / L
            mx, my = (a[0] + b[0]) / 2 - cz[0], (a[1] + b[1]) / 2 - cz[1]
            if nx * mx + ny * my < 0:
                nx, ny = -nx, -ny
            if ts >= 0.99 and ny <= 0.02:
                continue
            faces.append((k, nx, ny, (a[1] + b[1]) / 2, L))
        faces.sort(key=lambda f: f[3])
        for k, nx, ny, _, L in faces:
            k2 = (k + 1) % n
            q = [top[k], top[k2], bot[k2], bot[k]]
            lam = 0.5 - nx * 0.5
            band = 2 if lam > 0.66 else (1 if lam > 0.36 else 0)
            nu = max(1, int(L / 26))
            nv = max(1, int(hh / 30))
            facet(d, bil(q), nu, nv, lambda u, vv, i, j, kk, rc, band=band: self.bcol(stops, band, rc.uniform(-0.03, 0.03) - 0.04 * vv),
                  (seed, 'f', k), 0.28)
            if hh > 26 * v.k and not hq:
                self.grime(d, q, stops, band, (seed, k), hh)
            if ts >= 0.99 and hh > 12 * v.k:
                self.windows(d, bot[k], bot[k2], hh, ink, (seed, k), band)
        if ts > 0.05:
            facet(d, poly_fpos(top, (sum(p[0] for p in top) / n, sum(p[1] for p in top) / n)), max(4, n), 1,
                  lambda u, vv, i, j, kk, rc: self.bcol(stops, 2, 0.04 + rc.uniform(-0.03, 0.03)), (seed, 'roof'), 0.2,
                  wrap_u=True)
        # ink: silhouette thick, roof rim and front vertical thin, bevel on the lit front rim
        kk = v.k
        sil = hull(bot + top)
        ink_poly(d, sil, (2.6 if hq else 1.9) * kk, (seed, 'sil'))
        if ts > 0.05:
            for k in range(n):
                ink_line(d, top[k], top[(k + 1) % n], 1.0 * kk, (seed, 'rim', k))
            front = max(range(n), key=lambda k: top[k][1] + top[(k + 1) % n][1])
            a, b = top[front], top[(front + 1) % n]
            line2(d, (a[0], a[1] + 1.4 * kk), (b[0], b[1] + 1.4 * kk), 1.1 * kk, toon.BEVEL)
            # neon roof trim in the building's own ink (the game's neon), on part of the city
            if hq or h01(ci, pr['key'], 77) < 0.42:
                for k in range(n):
                    if top[k][1] + top[(k + 1) % n][1] >= 2 * (sum(p[1] for p in top) / n) - 0.5:
                        line2(d, top[k], top[(k + 1) % n], 1.3 * kk, ink)
                        line2(gl, top[k], top[(k + 1) % n], 2.4 * kk, ink)
        lo = max(range(n), key=lambda k: bot[k][1])
        ink_line(d, bot[lo], top[lo], 1.0 * kk, (seed, 'v'))

    def grime(self, d, q, stops, band, seed, hh):
        rng = random.Random(str(('g', seed)))
        rust = hexc('#5e3018')
        base = self.bcol(stops, band)
        for _ in range(rng.randint(1, 3)):
            u = rng.uniform(0.12, 0.88)
            ln = rng.uniform(0.15, 0.45)
            wd = rng.uniform(0.03, 0.07)
            P = bil(q)
            tri(d, [P(u - wd, 0.02), P(u + wd, 0.02), P(u, ln)], mix(base, rust, rng.uniform(0.35, 0.55)))
        if rng.random() < 0.5:
            u = rng.choice([0.04, 0.96])
            P = bil(q)
            tri(d, [P(u, rng.uniform(0.2, 0.8)), P(u + (0.06 if u < 0.5 else -0.06), rng.uniform(0.2, 0.8)),
                    P(u, rng.uniform(0.2, 0.8))], mix(base, hexc('#cfc4ae'), 0.35))

    def windows(self, d, a, b, hh, ink, seed, band):
        v = self.v
        rng = random.Random(str(('w', seed)))
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        nx = max(1, int(L / (7.0 * v.k)))
        ny = max(1, int(hh / (8.0 * v.k)))
        warm = hexc('#ffc872')
        for i in range(nx):
            for j in range(ny):
                if rng.random() > 0.2:
                    continue
                u = (i + 0.5) / nx
                z = (j + 0.6) / (ny + 0.4) * hh
                x = a[0] + (b[0] - a[0]) * u
                y = a[1] + (b[1] - a[1]) * u - z
                w2 = 1.6 * v.k
                dy = (b[1] - a[1]) / L * w2
                col = ink if rng.random() < 0.45 else warm
                if band == 0:
                    col = mix(col, (0, 0, 0), 0.25)
                d.polygon([((x - w2) * SS, (y - dy - 1.6 * v.k) * SS), ((x + w2) * SS, (y + dy - 1.6 * v.k) * SS),
                           ((x + w2) * SS, (y + dy + 1.0 * v.k) * SS), ((x - w2) * SS, (y - dy + 1.0 * v.k) * SS)], fill=col)

    # ---- raw decoration (HQ details, roof signs) and lines
    def raw(self, d, gl, pr):
        v = self.v
        pts = v.pts(pr['p'])
        if not v.visible(pts):
            return
        col = pr['c'][0]
        rgb, a = c255(col), col[3]
        ci = pr['ctx']
        hq = ci >= 0 and self.ctxs[ci]['kind'] == 'hq'
        if a >= 0.9 and lum(rgb) < 70:
            # a dark solid part (tube, box, deck): faceted and inked
            stops, _ = self.fam_for(ci)
            band = 1 if pts[0][0] < pts[min(1, len(pts) - 1)][0] else 0
            facet(d, poly_fpos(pts), len(pts), 1, lambda u, vv, i, j, k, rc: self.bcol(stops, band, rc.uniform(-0.03, 0.03)),
                  ('raw', ci, round(pts[0][0]), round(pts[0][1])), 0.0, wrap_u=True)
            if hq:
                ink_poly(d, pts, 1.0 * v.k, ('rawink', round(pts[0][0]), round(pts[0][1])))
        elif a >= 0.9:
            d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=rgb)
            gl.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=rgb)
        else:
            d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=rgb + (int(a * 255),))
            gl.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=mix(rgb, (0, 0, 0), 1 - a))

    def ink(self, d, gl, pr):
        v = self.v
        a, b = v.pts(pr['p'])
        if not v.visible([a, b]):
            return
        col = pr['c'][0]
        rgb, al = c255(col), col[3]
        w = max(0.8, pr['w'] * v.s * 1.15)
        d.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=rgb + (int(255 * min(1, al * 1.2)),), width=max(1, int(w * SS)))
        gl.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=mix(rgb, (0, 0, 0), 1 - al), width=max(1, int(w * 2 * SS)))

    def sign(self, d, gl, pr):
        v = self.v
        x, y = v.p(pr['p'][0], pr['p'][1])
        rgb = c255(pr['c'][0])
        f = ImageFont.truetype(BAHN, int(26 * v.k * SS))
        try:
            f.set_variation_by_name('Bold')
        except Exception:
            pass
        tw = d.textlength(pr['text'], font=f) / SS
        x0, y0, x1, y1 = x, y - 18 * v.k, x + tw + 24 * v.k, y + 18 * v.k
        d.polygon([(x0 * SS, y0 * SS), (x1 * SS, y0 * SS), (x1 * SS, y1 * SS), (x0 * SS, y1 * SS)], fill=(10, 9, 16))
        for (p0, p1) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            line2(d, p0, p1, 2.0 * v.k, rgb)
            line2(gl, p0, p1, 4.0 * v.k, rgb)
        d.text(((x0 + 12 * v.k) * SS, ((y0 + y1) / 2) * SS), pr['text'], font=f, fill=rgb, anchor='lm')

    # ---- streets (the game's glowing neon marker streets)
    def streets(self, gd, sd, gl):
        v = self.v
        street = c255(self.d['colors']['street'])
        for st in self.d['streets']:
            q = v.pts(st['p'])
            if not v.visible(q):
                continue
            gd.polygon([(p[0] * SS, p[1] * SS) for p in q], fill=street)
        for st in self.d['streets']:
            if 'ab' not in st:
                continue
            a, b = v.pts(st['ab'])
            if not v.visible([a, b]):
                continue
            col = c255(st['col'])
            tr = st['traffic']
            strokes = 7 + int(tr * 23)
            half = (1.5 + strokes * 0.42) * v.s
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, ny = -dy, dx
            g = 0.05 + tr * 0.08
            gw = half + 3 * v.s
            quad = [(a[0] - nx * gw, a[1] - ny * gw), (b[0] - nx * gw, b[1] - ny * gw), (b[0] + nx * gw, b[1] + ny * gw),
                    (a[0] + nx * gw, a[1] + ny * gw)]
            sd.polygon([(p[0] * SS, p[1] * SS) for p in quad], fill=col + (int(255 * g * 2.2),))
            key = st['i'] if st['ai'] else st['j']
            nl = min(strokes, 3 + int(tr * 9))
            for k in range(nl):
                t = (k + 0.5) / nl * 2 - 1
                lane = t * half * 0.8 + (h01(key, k, 81) - 0.5) * 1.2 * v.s
                al = 0.5 + 0.35 * h01(key + k, 3, 85) + tr * 0.15
                p0 = (a[0] + nx * lane - dx * 1.5 * v.s, a[1] + ny * lane - dy * 1.5 * v.s)
                p1 = (b[0] + nx * lane + dx * 1.5 * v.s, b[1] + ny * lane + dy * 1.5 * v.s)
                w = max(1, int((0.9 + h01(k, key, 86) * 0.6) * v.s * SS * 1.1))
                sd.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=col + (int(255 * min(1, al)),), width=w)
                gl.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=mix(col, (0, 0, 0), 1 - min(1, al) * 0.8),
                        width=w * 2)

    def fist(self, gd, sd, gl):
        v = self.v
        col = c255(self.d['colors']['fist'])
        street = c255(self.d['colors']['street'])
        H = self.d['fist_half'] * v.s
        for n, sg in enumerate(self.d['fist']):
            a, b = v.pts(sg)
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < 1:
                continue
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, ny = -dy, dx
            e0 = (a[0] - dx * H, a[1] - dy * H)
            e1 = (b[0] + dx * H, b[1] + dy * H)
            for w, fill, layer in ((H + 4 * v.s, street, gd), (H + 6 * v.s, col + (36,), sd)):
                quad = [(e0[0] - nx * w, e0[1] - ny * w), (e1[0] - nx * w, e1[1] - ny * w), (e1[0] + nx * w, e1[1] + ny * w),
                        (e0[0] + nx * w, e0[1] + ny * w)]
                layer.polygon([(p[0] * SS, p[1] * SS) for p in quad], fill=fill)
            for k in range(12):
                t = (k + 0.5) / 12 * 2 - 1
                lane = t * H + (h01(n, k, 87) - 0.5) * 1.6 * v.s
                over = H * (0.4 + 0.6 * h01(k, n, 88))
                al = 0.55 + 0.4 * h01(n + k, 5, 89)
                p0 = (a[0] + nx * lane - dx * over, a[1] + ny * lane - dy * over)
                p1 = (b[0] + nx * lane + dx * over, b[1] + ny * lane + dy * over)
                w = max(1, int(1.1 * v.s * SS))
                sd.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=col + (int(255 * al),), width=w)
                gl.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=mix(col, (0, 0, 0), 1 - al), width=w * 2)

    def trails(self, sd, gl):
        v = self.v
        for t in self.d['trails']:
            a = v.p(*t['a'])
            b = v.p(*t['b'])
            if not v.visible([a, b]):
                continue
            col = c255(t['col'])
            w = max(1, int(2.0 * v.s * SS))
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            sd.line([(a[0] * SS, a[1] * SS), (mid[0] * SS, mid[1] * SS)], fill=col + (110,), width=w)
            sd.line([(mid[0] * SS, mid[1] * SS), (b[0] * SS, b[1] * SS)], fill=mix(col, (255, 255, 255), 0.4) + (240,), width=w)
            gl.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=col, width=w * 3)

    def beacons(self, d, gl):
        v = self.v
        for b in self.d['beacons']:
            x, y = v.p(*b['p'])
            if not (-10 < x < v.w + 10 and -10 < y < v.h + 10):
                continue
            col = c255(b['col'])
            r = 2.6 * v.k
            tri(d, [(x - r, y), (x, y - r * 1.3), (x + r, y)], mix(col, (255, 255, 255), 0.3))
            tri(d, [(x - r, y), (x, y + r * 1.3), (x + r, y)], col)
            gl.ellipse([(x - r * 3) * SS, (y - r * 3) * SS, (x + r * 3) * SS, (y + r * 3) * SS], fill=mix(col, (0, 0, 0), 0.4))

    def plazas(self, gd):
        v = self.v
        g = c255(self.d['colors']['ground'])
        for pz in self.d['plazas']:
            q = v.pts(pz['p'])
            if not v.visible(q):
                continue
            col = self.terr_col.get(pz['terr'], (200, 200, 200))
            shade = mix(mix(g, col, 0.1), (60, 58, 80), 0.25 if (pz['i'] + pz['j']) % 2 else 0.18)
            gd.polygon([(p[0] * SS, p[1] * SS) for p in q], fill=shade)

    # ---- the whole picture
    def render(self):
        v = self.v
        W2, H2 = v.w * SS, v.h * SS
        ground = c255(self.d['colors']['ground'])
        img = Image.new('RGB', (W2, H2), ground)
        gd = ImageDraw.Draw(img)
        # faceted ground (calm big facets) under everything
        facet(gd, bil([(0, 0), (v.w, 0), (v.w, v.h), (0, v.h)]), 24, 14,
              lambda u, vv, i, j, k, rc: mix(ground, (24, 22, 40), rc.uniform(0.0, 0.5)), 'ground', 0.35)
        self.plazas(gd)
        sharp = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sharp, 'RGBA')
        glow = Image.new('RGB', (W2, H2), (0, 0, 0))
        gl = ImageDraw.Draw(glow)
        self.streets(gd, sd, gl)
        self.fist(gd, sd, gl)
        self.trails(sd, gl)
        img = self.bloom(img, glow, 7, 1.0)
        img = Image.alpha_composite(img.convert('RGBA'), sharp).convert('RGB')
        del sharp
        # standing: the game's own draw order
        d = ImageDraw.Draw(img, 'RGBA')
        bglow = Image.new('RGB', (W2, H2), (0, 0, 0))
        bg = ImageDraw.Draw(bglow)
        for n, pr in enumerate(self.d['prims']):
            t = pr['t']
            if t == 'ext':
                self.ext(d, pr, bg)
            elif t in ('quad', 'tri', 'poly'):
                self.raw(d, bg, pr)
            elif t == 'ink':
                self.ink(d, bg, pr)
        for pr in self.d['prims']:
            if pr['t'] == 'sign':
                self.sign(d, bg, pr)
        self.beacons(d, bg)
        img = img.convert('RGB')
        img = paint_texture(img)
        # neon spill: the streets' and roofs' glow bleeding over the facades, then the trims' bloom
        img = self.bloom(img, glow, 34, 0.55)
        img = self.bloom(img, bglow, 6, 0.9)
        return img.resize((v.w, v.h), Image.LANCZOS)

    @staticmethod
    def bloom(img, src, radius, amount):
        small = src.resize((max(1, src.width // 4), max(1, src.height // 4)), Image.BILINEAR)
        small = small.filter(ImageFilter.GaussianBlur(max(1, radius * SS / 4)))
        g = small.resize(src.size, Image.BILINEAR)
        if amount != 1.0:
            g = g.point(lambda x: int(x * amount))
        return ImageChops.screen(img.convert('RGB'), g)


def labels(img, data, view):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(BAHN, int(40 * view.k))
    try:
        f.set_variation_by_name('Bold')
    except Exception:
        pass
    names = {'': 'THE SPRAWL', 'solace': 'SOLACE', 'meridian': 'MERIDIAN', 'halcyon': 'HALCYON', 'orbital': 'ORBITAL',
             'rebel_cell': 'REBEL_CELL'}
    for t in data['territories']:
        x, y = view.p(*t['screen'])
        y -= 120 * view.k
        if not (0 < x < view.w and 0 < y < view.h):
            continue
        col = c255(t['color'])
        s = names[t['id']]
        tw = d.textlength(s, font=f)
        x0, y0 = x - tw / 2 - 24 * view.k, y - 30 * view.k
        x1, y1 = x + tw / 2 + 24 * view.k, y + 30 * view.k
        d.polygon([(x0 + 8 * view.k, y0), (x1, y0), (x1 - 8 * view.k, y1), (x0, y1)], fill=(10, 9, 16))
        d.line([(x0 + 8 * view.k, y0), (x1, y0), (x1 - 8 * view.k, y1), (x0, y1), (x0 + 8 * view.k, y0)], fill=(3, 3, 6),
               width=max(2, int(4 * view.k)))
        d.polygon([(x0 + 8 * view.k, y0), (x0 + 20 * view.k, y0), (x0 + 12 * view.k, y1), (x0, y1)], fill=col)
        d.text((x + 6 * view.k, y), s, font=f, fill=col, anchor='mm')
    return img


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, 'city_layout.json')
    data = json.load(open(path))
    vw = data['view']
    # full view: the poster framing (city px * zoom), rendered at 3840x2160, saved at 2560x1440
    full = View(0, 0, vw['zoom'], vw['w'], vw['h'])
    lowpoly.W, lowpoly.H = full.w, full.h
    img = Restyler(data, full).render()
    img = labels(img, data, full)
    img.resize((2560, 1440), Image.LANCZOS).save(os.path.join(OUT, 'after_night.png'), optimize=True)
    print('wrote after_night.png')
    # title framing: the in-game zoom (1 city px = 1.5 px at 1080p), Solace's HQ low and centred
    sol = next(t for t in data['territories'] if t['id'] == 'solace')
    sx, sy = sol['screen']
    tv = View(sx - 960 / 1.5, sy - 760 / 1.5, 1.5, 1920, 1080)
    lowpoly.W, lowpoly.H = tv.w, tv.h
    Restyler(data, tv).render().save(os.path.join(OUT, 'after_title_crop.png'), optimize=True)
    print('wrote after_title_crop.png')
    # before / after
    before = Image.open(os.path.join(OUT, 'before.png')).convert('RGB')
    if before.size != (2560, 1440):
        before = before.resize((2560, 1440), Image.LANCZOS)
        before.save(os.path.join(OUT, 'before.png'), optimize=True)
    after = Image.open(os.path.join(OUT, 'after_night.png')).convert('RGB')
    sheet = Image.new('RGB', (2 * 1600 + 60, 900 + 110), (16, 15, 20))
    sheet.paste(before.resize((1600, 900), Image.LANCZOS), (20, 70))
    sheet.paste(after.resize((1600, 900), Image.LANCZOS), (1640, 70))
    dd = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(BAHN, 36)
    dd.text((24, 36), 'BEFORE  -  the game\'s NeonCity', font=f, fill=(236, 228, 210), anchor='lm')
    dd.text((1644, 36), 'AFTER  -  same city, Cv2 facets + E cel buildings', font=f, fill=(236, 228, 210), anchor='lm')
    sheet.save(os.path.join(OUT, 'before_after.jpg'), quality=90)
    print('wrote before_after.jpg')


if __name__ == '__main__':
    main()
