"""Shared drawing helpers for the Solace end-screen concepts (PIL, 2x supersampled)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

K = 2
W, H = 1920, 1080
R = 'D:/rc_art/art-pass/'
FONTS = {
    'anton': R + 'assets/fonts/Anton-Regular.ttf',
    'mono': R + 'assets/fonts/ShareTechMono-Regular.ttf',
    'plex': R + 'assets/fonts/IBMPlexSansCondensed-Medium.ttf',
    'plexr': R + 'assets/fonts/IBMPlexSansCondensed-Regular.ttf',
    'courier': R + 'docs/concepts/round32_ui_chrome/fonts/CourierPrime-Regular.ttf',
    'courierb': R + 'docs/concepts/round32_ui_chrome/fonts/CourierPrime-Bold.ttf',
    'hand': 'C:/Windows/Fonts/Inkfree.ttf',
    'marker': R + 'assets/fonts/PermanentMarker-Regular.ttf',
}
_fc = {}


def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS[name], int(round(size * K)))
    return _fc[k]


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def new(bg=(0, 0, 0, 255)):
    return Image.new('RGBA', (W * K, H * K), bg)


def S(v):
    if isinstance(v, (list, tuple)):
        return [S(x) for x in v]
    return int(round(v * K))


class BD:
    """ImageDraw wrapper that alpha-blends translucent fills/outlines onto RGBA images (plain ImageDraw replaces)."""

    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    @staticmethod
    def _tr(c):
        return isinstance(c, tuple) and len(c) == 4 and c[3] < 255

    @staticmethod
    def _flat(xy):
        out = []
        for v in xy:
            if isinstance(v, (tuple, list)):
                out.extend(v)
            else:
                out.append(v)
        return out

    def _shift(self, xy, dx, dy):
        if isinstance(xy[0], (tuple, list)):
            return [(p[0] - dx, p[1] - dy) for p in xy]
        return [v - (dx if i % 2 == 0 else dy) for i, v in enumerate(xy)]

    def _blend(self, method, xy, pad, kwargs):
        f = self._flat(xy)
        xs, ys = f[0::2], f[1::2]
        x0 = max(0, int(min(xs) - pad)); y0 = max(0, int(min(ys) - pad))
        x1 = min(self.img.width, int(max(xs) + pad) + 1); y1 = min(self.img.height, int(max(ys) + pad) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        box = (x0, y0, x1, y1)
        crop = self.img.crop(box)
        lay = Image.new('RGBA', crop.size, (0, 0, 0, 0))
        getattr(ImageDraw.Draw(lay), method)(self._shift(xy, x0, y0), **kwargs)
        crop.alpha_composite(lay)
        self.img.paste(crop, (x0, y0))

    def _any_tr(self, kw):
        return any(self._tr(kw.get(k)) for k in ('fill', 'outline', 'stroke_fill'))

    def _shape(self, method, xy, **kw):
        if self._any_tr(kw):
            self._blend(method, xy, int(kw.get('width', 1) or 1) + 3, kw)
        else:
            getattr(self.d, method)(xy, **kw)

    def line(self, xy, **kw): self._shape('line', xy, **kw)
    def polygon(self, xy, **kw): self._shape('polygon', xy, **kw)
    def ellipse(self, xy, **kw): self._shape('ellipse', xy, **kw)
    def rectangle(self, xy, **kw): self._shape('rectangle', xy, **kw)
    def rounded_rectangle(self, xy, **kw): self._shape('rounded_rectangle', xy, **kw)
    def arc(self, xy, start, end, **kw): self._shape('arc', xy, start=start, end=end, **kw)

    def text(self, xy, s, **kw):
        if self._any_tr(kw):
            bb = self.d.textbbox(xy, s, font=kw.get('font'), anchor=kw.get('anchor'), stroke_width=kw.get('stroke_width', 0))
            pad = 4
            x0, y0 = max(0, int(bb[0]) - pad), max(0, int(bb[1]) - pad)
            x1, y1 = min(self.img.width, int(bb[2]) + pad), min(self.img.height, int(bb[3]) + pad)
            crop = self.img.crop((x0, y0, x1, y1))
            lay = Image.new('RGBA', crop.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((xy[0] - x0, xy[1] - y0), s, **kw)
            crop.alpha_composite(lay)
            self.img.paste(crop, (x0, y0))
        else:
            self.d.text(xy, s, **kw)

    def multiline_text(self, xy, s, **kw):
        self.d.multiline_text(xy, s, **kw)


def draw(img):
    return BD(img)


def text(img, xy, s, f, fill, anchor='la', stroke=0, stroke_fill=None, spacing=4):
    d = draw(img)
    d.text((xy[0] * K, xy[1] * K), s, font=f, fill=fill, anchor=anchor,
           stroke_width=int(stroke * K), stroke_fill=stroke_fill, spacing=spacing * K)


def tw(s, f):
    return f.getlength(s) / K


def rrect(img, box, r, fill=None, outline=None, width=1):
    draw(img).rounded_rectangle(S(box), radius=S(r), fill=fill, outline=outline, width=int(width * K))


def rect(img, box, fill=None, outline=None, width=1):
    draw(img).rectangle(S(box), fill=fill, outline=outline, width=int(width * K))


def line(img, pts, fill, width=1):
    draw(img).line(S(pts), fill=fill, width=max(1, int(width * K)), joint='curve')


def poly(img, pts, fill=None, outline=None, width=1):
    d = draw(img)
    p = [tuple(S(list(q))) for q in pts]
    if fill is not None:
        d.polygon(p, fill=fill)
    if outline is not None:
        d.line(p + [p[0]], fill=outline, width=max(1, int(width * K)), joint='curve')


def ellipse(img, box, fill=None, outline=None, width=1):
    draw(img).ellipse(S(box), fill=fill, outline=outline, width=int(width * K))


def layer(w, h):
    return Image.new('RGBA', (int(w * K), int(h * K)), (0, 0, 0, 0))


def rotate_paste(base, lay, cx, cy, deg, shadow=True, sh=(6, 8, 14, 110)):
    r = lay.rotate(deg, resample=Image.BICUBIC, expand=True)
    x = int(cx * K - r.width / 2)
    y = int(cy * K - r.height / 2)
    if shadow:
        a = r.split()[3].filter(ImageFilter.GaussianBlur(S(7)))
        s = Image.new('RGBA', r.size, (0, 0, 0, 0))
        s.putalpha(a.point(lambda v: int(v * sh[3] / 255)))
        base.alpha_composite(s, (x + S(sh[0]), y + S(sh[1])))
    base.alpha_composite(r, (x, y))


def glow(img, color_layer, radius, strength=1.0):
    """Additive bloom of a layer onto img."""
    b = color_layer.filter(ImageFilter.GaussianBlur(S(radius)))
    a = np.asarray(img).astype(np.float32)
    g = np.asarray(b).astype(np.float32)
    al = g[..., 3:4] / 255.0
    a[..., :3] = np.clip(a[..., :3] + g[..., :3] * al * strength, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


# ---- chrome ----------------------------------------------------------------
def sticker(img, label, cx, cy, w, h, fill, fg, rot=-2, size=40, border=(255, 255, 255, 255)):
    """Vinyl sticker: Anton lettering, ink keyline, white die-cut border, gloss."""
    pad = 14
    L = layer(w + pad * 2, h + pad * 2)
    d = draw(L)
    d.rounded_rectangle(S([2, 2, w + pad * 2 - 2, h + pad * 2 - 2]), radius=S(18), fill=border)
    d.rounded_rectangle(S([6, 6, w + pad * 2 - 6, h + pad * 2 - 6]), radius=S(15), fill=(20, 12, 28, 255))
    d.rounded_rectangle(S([9, 9, w + pad * 2 - 9, h + pad * 2 - 9]), radius=S(13), fill=border)
    d.rounded_rectangle(S([pad, pad, pad + w, pad + h]), radius=S(11), fill=(18, 10, 24, 255))
    d.rounded_rectangle(S([pad + 3, pad + 3, pad + w - 3, pad + h - 3]), radius=S(9), fill=(24, 16, 34, 255))
    gl = Image.new('RGBA', L.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle(S([pad + 4, pad + 4, pad + w - 4, pad + h * 0.46]), radius=S(8), fill=(255, 255, 255, 56))
    L.alpha_composite(gl)
    f = font('anton', size)
    cxx, cyy = (w + pad * 2) / 2, (h + pad * 2) / 2 + 2
    d.text((cxx * K, cyy * K), label, font=f, fill=(15, 8, 20, 255), anchor='mm',
           stroke_width=int(4 * K), stroke_fill=(0, 0, 0, 255))
    d.text((cxx * K, cyy * K), label, font=f, fill=fill, anchor='mm')
    rotate_paste(img, L, cx, cy, rot)


def buttons(img, new_fill=(255, 62, 160, 255), new_fg=(20, 8, 20, 255), new_label='NEW CAMPAIGN',
            main_xy=(1330, 1032), new_xy=(1590, 1030)):
    sticker(img, 'MAIN MENU', main_xy[0], main_xy[1], 190, 52, (236, 236, 242, 255), None, rot=1, size=30)
    sticker(img, new_label, new_xy[0], new_xy[1], 270, 60, new_fill, None, rot=-1.5, size=38)


def postit(img, box, color, s, rot=3, size=26, fg=(40, 40, 140, 255)):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    L = layer(w + 20, h + 20)
    d = draw(L)
    d.rectangle(S([10, 10, 10 + w, 10 + h]), fill=color)
    d.rectangle(S([10, 10, 10 + w, 10 + h * 0.14]), fill=(255, 255, 255, 38))
    f = font('hand', size)
    d.multiline_text((S(22), S(24 + h * 0.1)), s, font=f, fill=fg, spacing=S(2))
    rotate_paste(img, L, (x0 + x1) / 2, (y0 + y1) / 2, rot)


def stamp(img, s, cx, cy, color, rot=-8, size=76):
    f = font('anton', size)
    wd = tw(s, f) + 34
    hd = size * 1.0 + 26
    L = layer(wd + 20, hd + 20)
    d = draw(L)
    d.rectangle(S([10, 10, 10 + wd, 10 + hd]), outline=color, width=S(5))
    d.rectangle(S([17, 17, 3 + wd, 3 + hd]), outline=color, width=S(2))
    d.text((S((wd + 20) / 2), S((hd + 20) / 2 + 3)), s, font=f, fill=color, anchor='mm')
    arr = np.asarray(L).copy()
    rng = np.random.default_rng(sum(map(ord, s)))
    n = rng.random(arr.shape[:2])
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    drop = n > 0.575
    arr[..., 3] = np.where(drop, arr[..., 3] * 0.22, arr[..., 3] * 0.95).astype(np.uint8)
    L = Image.fromarray(arr, 'RGBA')
    rotate_paste(img, L, cx, cy, rot, shadow=False)


def crt_panel(img, box, edge=(0, 229, 255, 255), title=None, fill=(6, 14, 30, 238)):
    x0, y0, x1, y1 = box
    rrect(img, box, 8, fill=fill, outline=edge, width=2)
    rrect(img, [x0 + 4, y0 + 4, x1 - 4, y1 - 4], 6, outline=(edge[0], edge[1], edge[2], 70), width=1)
    d = draw(img)
    for y in range(int(y0 + 6), int(y1 - 6), 3):
        d.line(S([x0 + 6, y, x1 - 6, y]), fill=(0, 0, 0, 38), width=1)
    if title:
        text(img, (x0 + 18, y0 + 10), title, font('mono', 20), edge, 'la')


def grain(img, amt=7, seed=1):
    a = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def vignette(img, strength=0.45):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = 1 - strength * np.clip(d - 0.55, 0, 1) ** 1.5
    a = np.asarray(img).astype(np.float32)
    a[..., :3] *= v[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def rgb_split(img, px=3):
    r, g, b, a = img.split()
    r = ImageChops.offset(r, S(px), 0)
    b = ImageChops.offset(b, S(-px), 0)
    return Image.merge('RGBA', (r, g, b, a))


def finish(img, path, g=5, seed=1):
    img = grain(img, g, seed)
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(path)
    return out


def hsv_shift(arr, hue_from, hue_to, shift=0.0, sat=1.0, val=1.0, mask=None):
    """arr float RGB 0..1 (h,w,3). Shift hues in [hue_from,hue_to] by `shift`. Returns (rgb, selection)."""
    mx = arr.max(2)
    mn = arr.min(2)
    d = mx - mn + 1e-9
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    s = d / (mx + 1e-9)
    sel = (h >= hue_from) & (h <= hue_to) & (s > 0.25) & (mx > 0.12)
    if mask is not None:
        sel &= mask
    h2 = np.where(sel, (h + shift) % 1.0, h)
    i = np.floor(h2 * 6).astype(int) % 6
    f = h2 * 6 - np.floor(h2 * 6)
    s2 = np.where(sel, np.clip(s * sat, 0, 1), s)
    v2 = np.where(sel, np.clip(mx * val, 0, 1), mx)
    p = v2 * (1 - s2)
    q = v2 * (1 - f * s2)
    t = v2 * (1 - (1 - f) * s2)
    out = np.zeros_like(arr)
    for k, (rr, gg, bb) in enumerate([(v2, t, p), (q, v2, p), (p, v2, t), (p, q, v2), (t, p, v2), (v2, p, q)]):
        m = i == k
        out[..., 0] = np.where(m, rr, out[..., 0])
        out[..., 1] = np.where(m, gg, out[..., 1])
        out[..., 2] = np.where(m, bb, out[..., 2])
    return out, sel
