"""Supersampled drawing canvas: units in, final-pixel widths/sizes. PIL only."""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFont

from geom import TAU, circle_pts, dashes, dist, ellipse_pts, mix, rect_pts, rot

FONT_PATH = 'C:/Windows/Fonts/bahnschrift.ttf'
TITLE_FONT = 'C:/Windows/Fonts/AGENCYB.TTF'
_fonts = {}


def get_font(size, weight='Regular', title=False):
    size = max(6, int(round(size)))
    key = (size, weight, title)
    if key not in _fonts:
        if title:
            f = ImageFont.truetype(TITLE_FONT, size)
        else:
            f = ImageFont.truetype(FONT_PATH, size)
            try:
                f.set_variation_by_name(weight)
            except Exception:
                pass
        _fonts[key] = f
    return _fonts[key]


class Canvas:
    def __init__(self, wu, hu, S, fpu, bg):
        self.wu, self.hu, self.S, self.fpu = wu, hu, S, fpu
        self.f = S / fpu            # supersampled px per final px
        self.W, self.H = int(wu * S), int(hu * S)
        self.img = Image.new('RGB', (self.W, self.H), bg)
        self.d = ImageDraw.Draw(self.img, 'RGBA')

    # ---- coordinate helpers -------------------------------------------------
    def P(self, p):
        return (p[0] * self.S, p[1] * self.S)

    def PL(self, pts):
        S = self.S
        return [(x * S, y * S) for x, y in pts]

    def bbox_ss(self, pts_ss, pad=6):
        xs = [p[0] for p in pts_ss]
        ys = [p[1] for p in pts_ss]
        return (max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad),
                min(self.W, int(max(xs)) + pad + 1), min(self.H, int(max(ys)) + pad + 1))

    # ---- masked painting ------------------------------------------------------
    def masked(self, bbox, draw_fn, color, alpha=1.0, clip=None):
        x0, y0, x1, y1 = bbox
        if x1 <= x0 or y1 <= y0:
            return
        lay = Image.new('L', (x1 - x0, y1 - y0), 0)
        ld = ImageDraw.Draw(lay)
        draw_fn(ld, x0, y0)
        if clip is not None:
            lay = ImageChops.multiply(lay, clip.crop(bbox))
        if alpha < 1:
            lay = lay.point(lambda v: int(v * alpha))
        self.img.paste(color, (x0, y0), lay)

    def poly_mask(self, pts):
        m = Image.new('L', (self.W, self.H), 0)
        ImageDraw.Draw(m).polygon(self.PL(pts), fill=255)
        return m

    # ---- primitives -----------------------------------------------------------
    def poly(self, pts, fill=None, alpha=1.0, outline=None, ow=1.0, oalpha=1.0, clip=None):
        ps = self.PL(pts)
        if fill is not None:
            if clip is None:
                self.d.polygon(ps, fill=tuple(fill) + (int(255 * alpha),))
            else:
                bb = self.bbox_ss(ps)
                self.masked(bb, lambda ld, ox, oy: ld.polygon([(x - ox, y - oy) for x, y in ps], fill=255),
                            fill, alpha, clip)
        if outline is not None:
            self.line(list(pts) + [pts[0]], outline, ow, oalpha, clip=clip)

    def _path(self, ld, ps, w, fill):
        if w <= 1.6:
            ld.line(ps, fill=fill, width=max(1, int(round(w))))
            return
        ld.line(ps, fill=fill, width=int(round(w)))
        r = w / 2.0
        for x, y in ps:
            ld.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def line(self, pts, color, w, alpha=1.0, clip=None, dash=None, cap=True):
        """w is in final px. dash=(on, off) in units."""
        if len(pts) < 2:
            return
        ws = w * self.f
        if dash:
            for seg in dashes(pts, dash[0], dash[1]):
                self.line(seg, color, w, alpha, clip, None, cap)
            return
        ps = self.PL(pts)
        if alpha >= 0.99 and clip is None:
            fill = tuple(color) + (255,)
            self._path(self.d, ps, ws, fill)
            return
        bb = self.bbox_ss(ps, pad=int(ws) + 3)
        self.masked(bb, lambda ld, ox, oy: self._path(ld, [(x - ox, y - oy) for x, y in ps], ws, 255),
                    color, alpha, clip)

    def lines(self, polylines, color, w, alpha=1.0, clip=None, bbox_units=None):
        """Many polylines painted as one masked layer (efficient for textures)."""
        if not polylines:
            return
        ws = w * self.f
        allp = [self.PL(p) for p in polylines if len(p) > 1]
        if not allp:
            return
        if bbox_units is not None:
            x0, y0, x1, y1 = bbox_units
            bb = (max(0, int(x0 * self.S) - 4), max(0, int(y0 * self.S) - 4),
                  min(self.W, int(x1 * self.S) + 4), min(self.H, int(y1 * self.S) + 4))
        else:
            flat = [pt for p in allp for pt in p]
            bb = self.bbox_ss(flat, pad=int(ws) + 3)

        def fn(ld, ox, oy):
            for p in allp:
                self._path(ld, [(x - ox, y - oy) for x, y in p], ws, 255)
        self.masked(bb, fn, color, alpha, clip)

    def polys(self, polygons, color, alpha=1.0, clip=None, bbox_units=None):
        if not polygons:
            return
        allp = [self.PL(p) for p in polygons]
        if bbox_units is not None:
            x0, y0, x1, y1 = bbox_units
            bb = (max(0, int(x0 * self.S) - 4), max(0, int(y0 * self.S) - 4),
                  min(self.W, int(x1 * self.S) + 4), min(self.H, int(y1 * self.S) + 4))
        else:
            flat = [pt for p in allp for pt in p]
            bb = self.bbox_ss(flat)

        def fn(ld, ox, oy):
            for p in allp:
                ld.polygon([(x - ox, y - oy) for x, y in p], fill=255)
        self.masked(bb, fn, color, alpha, clip)

    def circle(self, x, y, r_px, fill=None, outline=None, ow=1.0, alpha=1.0):
        """Circle, radius in final px, centre in units."""
        cx, cy = x * self.S, y * self.S
        r = r_px * self.f
        box = [cx - r, cy - r, cx + r, cy + r]
        fl = None if fill is None else tuple(fill) + (int(255 * alpha),)
        ol = None if outline is None else tuple(outline) + (int(255 * alpha),)
        self.d.ellipse(box, fill=fl, outline=ol, width=max(1, int(round(ow * self.f))) if outline else 0)

    # ---- text -----------------------------------------------------------------
    def text(self, x, y, s, size, fill=(240, 240, 240), angle=0.0, spacing=0.0, halo=True,
             weight='Bold', alpha=255, halo_col=(6, 8, 14), title=False, anchor='mm', halo_w=None):
        """x,y units; size final px; spacing final px; angle degrees (PIL: counter-clockwise)."""
        f = get_font(size * self.f, weight, title)
        widths = [f.getlength(ch) for ch in s]
        sp = spacing * self.f
        total = sum(widths) + sp * (len(s) - 1)
        hh = int(f.size * 1.7)
        pad = int(f.size * 0.5)
        tile = Image.new('RGBA', (int(total) + 2 * pad, hh + 2 * pad), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        sw = 0
        if halo:
            sw = halo_w if halo_w is not None else max(2, int(f.size * 0.13))
        for pas in ((0, 1) if halo else (1,)):
            cx = pad
            for ch, w in zip(s, widths):
                if pas == 0:
                    td.text((cx, pad + hh / 2), ch, font=f, fill=tuple(halo_col) + (230,), anchor='lm',
                            stroke_width=sw, stroke_fill=tuple(halo_col) + (230,))
                else:
                    td.text((cx, pad + hh / 2), ch, font=f, fill=tuple(fill) + (alpha,), anchor='lm')
                cx += w + sp
        if angle:
            tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
        tw, th = tile.size
        px, py = x * self.S, y * self.S
        if anchor == 'mm':
            ox, oy = px - tw / 2, py - th / 2
        elif anchor == 'lm':
            ox, oy = px - pad, py - th / 2
        elif anchor == 'rm':
            ox, oy = px - tw + pad, py - th / 2
        else:
            ox, oy = px - tw / 2, py - th / 2
        self.img.paste(tile, (int(ox), int(oy)), tile)

    def text_lines(self, x, y, lines, size, lead=1.15, **kw):
        n = len(lines)
        for i, s in enumerate(lines):
            self.text(x, y + (i - (n - 1) / 2.0) * size * lead / self.fpu, s, size, **kw)

    # ---- glyphs ---------------------------------------------------------------
    def glyph(self, kind, x, y, rpx=6.0, col=None, badge=True):
        """Category icon. rpx = radius in final px; x,y units."""
        f = self.f
        cx, cy = x * self.S, y * self.S
        R = rpx * f
        u = R / 10.0
        d = self.d
        if badge:
            d.ellipse([cx - R - 1.4 * f, cy - R - 1.4 * f, cx + R + 1.4 * f, cy + R + 1.4 * f],
                      fill=(8, 10, 16, 235))
            d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(18, 22, 32, 255),
                      outline=(col or (200, 205, 215)) + (255,) if col else (150, 156, 170, 255),
                      width=max(1, int(0.9 * f)))

        def P(*pts):
            return [(cx + px * u, cy + py * u) for px, py in pts]
        W = (235, 238, 245, 255)
        if kind == 'hospital':
            c = (255, 80, 90, 255)
            d.polygon(P((-6, -2), (-2, -2), (-2, -6), (2, -6), (2, -2), (6, -2), (6, 2), (2, 2), (2, 6),
                        (-2, 6), (-2, 2), (-6, 2)), fill=c)
        elif kind == 'university':
            c = (255, 226, 120, 255)
            d.polygon(P((-8, -2), (0, -6), (8, -2), (0, 2)), fill=c)
            d.polygon(P((-4, 1), (-4, 5), (4, 5), (4, 1), (0, 3)), fill=c)
        elif kind == 'stadium':
            d.ellipse(P((-7, -5), (7, 5)), outline=W, width=max(1, int(1.2 * f)))
            d.ellipse(P((-3.5, -2.2), (3.5, 2.2)), fill=(90, 220, 120, 255))
        elif kind == 'market':
            c = (255, 70, 210, 255)
            pts = []
            for i in range(10):
                a = -math.pi / 2 + i * math.pi / 5
                rr = 8 if i % 2 == 0 else 3.4
                pts.append((rr * math.cos(a), rr * math.sin(a)))
            d.polygon(P(*pts), fill=c)
        elif kind == 'power':
            d.polygon(P((1.5, -8), (-4.5, 1), (-0.5, 1), (-2, 8), (5, -2), (1, -2)), fill=(255, 230, 60, 255))
        elif kind == 'water':
            c = (110, 200, 255, 255)
            d.polygon(P((0, -8), (-4.5, 0), (4.5, 0)), fill=c)
            d.ellipse(P((-4.6, -1), (4.6, 7.6)), fill=c)
        elif kind == 'sewage':
            c = (170, 150, 100, 255)
            d.polygon(P((0, -8), (-4.5, 0), (4.5, 0)), fill=c)
            d.ellipse(P((-4.6, -1), (4.6, 7.6)), fill=c)
        elif kind == 'cemetery':
            c = (170, 176, 195, 255)
            d.rectangle(P((-1.3, -8), (1.3, 8)), fill=c)
            d.rectangle(P((-5, -4), (5, -1.5)), fill=c)
        elif kind == 'airport':
            c = (220, 236, 255, 255)
            d.polygon(P((-0.9, -8), (0.9, -8), (0.9, 8), (-0.9, 8)), fill=c)
            d.polygon(P((-8, 1), (8, 1), (8, 3), (-8, 3)), fill=c)
            d.polygon(P((-4, 8), (4, 8), (4, 6.5), (-4, 6.5)), fill=c)
        elif kind == 'datacentre':
            c = (80, 255, 200, 255)
            for yy in (-6, -1.5, 3):
                d.rectangle(P((-6, yy), (6, yy + 3.2)), fill=c)
        elif kind == 'arcology':
            pts = [(8 * math.cos(math.pi / 6 + i * math.pi / 3), 8 * math.sin(math.pi / 6 + i * math.pi / 3))
                   for i in range(6)]
            d.polygon(P(*pts), outline=W, width=max(1, int(1.1 * f)))
            pts2 = [(4 * math.cos(math.pi / 6 + i * math.pi / 3), 4 * math.sin(math.pi / 6 + i * math.pi / 3))
                    for i in range(6)]
            d.polygon(P(*pts2), fill=W)
        elif kind == 'megastructure':
            d.rectangle(P((-7, -7), (7, 7)), outline=W, width=max(1, int(1.1 * f)))
            d.rectangle(P((-3.5, -3.5), (3.5, 3.5)), fill=W)
        elif kind == 'checkpoint':
            c = (255, 70, 70, 255)
            d.rectangle(P((-7, -4), (-4, 4)), fill=c)
            d.rectangle(P((4, -4), (7, 4)), fill=c)
            d.rectangle(P((-4, -1), (4, 1)), fill=W)
        elif kind == 'recycling':
            d.polygon(P((0, -7), (7, 5), (-7, 5)), outline=(140, 210, 120, 255), width=max(1, int(1.3 * f)))
        elif kind == 'rebel':
            pts = []
            for i in range(10):
                a = -math.pi / 2 + i * math.pi / 5
                rr = 9 if i % 2 == 0 else 3.8
                pts.append((rr * math.cos(a), rr * math.sin(a)))
            d.polygon(P(*pts), fill=(255, 60, 60, 255))
        elif kind == 'hub':
            d.ellipse(P((-7, -7), (7, 7)), outline=W, width=max(1, int(1.3 * f)))
            d.ellipse(P((-3, -3), (3, 3)), fill=W)
        elif kind == 'fusion':
            d.ellipse(P((-6, -6), (6, 6)), outline=(255, 230, 60, 255), width=max(1, int(1.4 * f)))
            d.ellipse(P((-2.5, -2.5), (2.5, 2.5)), fill=(255, 230, 60, 255))
        elif kind == 'school':
            d.polygon(P((-7, 2), (0, -6), (7, 2)), fill=(180, 220, 255, 255))
            d.rectangle(P((-5, 2), (5, 6)), fill=(180, 220, 255, 255))
        elif kind == 'church':
            d.rectangle(P((-1.2, -8), (1.2, 8)), fill=(205, 190, 150, 255))
            d.rectangle(P((-4, -4), (4, -2)), fill=(205, 190, 150, 255))

    def star(self, x, y, rpx, fill, alpha=1.0):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = rpx if i % 2 == 0 else rpx * 0.42
            pts.append((x * self.S + rr * self.f * math.cos(a), y * self.S + rr * self.f * math.sin(a)))
        self.d.polygon(pts, fill=tuple(fill) + (int(255 * alpha),))

    def shield(self, x, y, s, fill=(250, 250, 245), ink=(15, 18, 26), size=11, w=None):
        f = get_font(size * self.f, 'Bold')
        tw = f.getlength(s)
        pad = size * 0.5 * self.f
        cx, cy = x * self.S, y * self.S
        h = size * 0.82 * self.f
        box = [cx - tw / 2 - pad, cy - h, cx + tw / 2 + pad, cy + h]
        self.d.rounded_rectangle([box[0] - 1.5 * self.f, box[1] - 1.5 * self.f, box[2] + 1.5 * self.f,
                                  box[3] + 1.5 * self.f], radius=h, fill=(8, 10, 14, 255))
        self.d.rounded_rectangle(box, radius=h, fill=tuple(fill) + (255,))
        self.d.text((cx, cy + 0.02 * h), s, font=f, fill=tuple(ink) + (255,), anchor='mm')
