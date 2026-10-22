"""Round 32 shared 2D kit for the netrun route mockups (on top of r31lib / sticker_lib19).

Mediums (locked): node kinds = die-cut stickers (never change); links + pads = circuit inlay (the raid's language):
corp colour while the corp owns them, LIME #D4FF00 once the Cell has walked them; live values = CRT terminal;
decrypted Site intel = holo; plans = yellow grease pencil, threats = red grease pencil (true to the rules).
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import r31lib as L
import sticker_lib19 as SL

W, H = 1920, 1080
MER = (255, 140, 26)
LIME = (212, 255, 0)
PINK = (255, 61, 168)
CYAN = (92, 225, 255)
GREY = (120, 116, 130)
SCRATCH = os.path.join(L.OUT, "scratch")
FIN = os.path.join(SCRATCH, "fin")
BL = os.path.join(SCRATCH, "bl")

KIND = {
    "router": dict(col=(40, 36, 52), ring=(92, 225, 255), name="ROUTER", sub="fight, common Firmware", heat="+0"),
    "elite": dict(col=(120, 40, 14), ring=MER, name="ELITE ROUTER", sub="elite fight, better drops", heat="+1"),
    "terminal": dict(col=(14, 60, 36), ring=(61, 255, 139), name="TERMINAL", sub="event", heat="+0"),
    "modem": dict(col=(20, 40, 96), ring=(80, 150, 255), name="MODEM", sub="shop: spend Cycles", heat="+0"),
    "rack": dict(col=(60, 30, 8), ring=MER, name="SERVER RACK", sub="optional: elite fight, banks", heat="+3"),
}


# ------------------------------------------------------------------ node stickers (round 31 icons, MAINFRAME blue modem)
def icon(kind, px):
    S = 2
    out_px = px
    px = max(px, 110)
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = KIND[kind]
    if kind == "rack":
        d.rounded_rectangle([4 * S, 2 * S, P - 4 * S, P - 2 * S], radius=10 * S, fill=k["col"] + (255,), outline=L.INK + (255,), width=3 * S)
        d.rounded_rectangle([9 * S, 7 * S, P - 9 * S, P - 7 * S], radius=7 * S, outline=k["ring"] + (255,), width=4 * S)
        n = 5
        for j in range(n):
            y0 = 18 * S + j * (P - 36 * S) / n
            d.rectangle([20 * S, y0, P - 20 * S, y0 + (P - 36 * S) / n - 5 * S], fill=(28, 22, 18, 255), outline=(120, 80, 40, 255), width=S)
            for q in range(3):
                d.ellipse([26 * S + q * 9 * S, y0 + 4 * S, 31 * S + q * 9 * S, y0 + 9 * S], fill=(255, 190, 60, 255) if (j + q) % 2 else (80, 255, 140, 255))
            d.rectangle([P - 44 * S, y0 + 5 * S, P - 26 * S, y0 + 8 * S], fill=(150, 120, 90, 255))
    else:
        d.ellipse([3 * S, 3 * S, P - 3 * S, P - 3 * S], fill=k["col"] + (255,), outline=L.INK + (255,), width=3 * S)
        d.ellipse([8 * S, 8 * S, P - 8 * S, P - 8 * S], outline=k["ring"] + (255,), width=4 * S)
        g = None
        if kind == "router":
            g = L.glyph("slice_exploit", int(P * 0.5), ow=2 * S)
        elif kind == "elite":
            g = L.glyph("slice_zero_day", int(P * 0.54), fill=(255, 220, 160), ow=2 * S)
        if g is not None:
            im.alpha_composite(g, ((P - g.width) // 2, (P - g.height) // 2))
        if kind == "terminal":
            x0, y0, x1, y1 = P * 0.26, P * 0.3, P * 0.74, P * 0.66
            d.rounded_rectangle([x0, y0, x1, y1], radius=4 * S, fill=(10, 30, 18, 255), outline=(255, 255, 255, 255), width=3 * S)
            d.text((x0 + 7 * S, (y0 + y1) / 2), ">_", font=L.f_mono(int(P * 0.2)), fill=(61, 255, 139, 255), anchor="lm")
            d.rectangle([P * 0.42, y1, P * 0.58, y1 + 6 * S], fill=(255, 255, 255, 255))
        if kind == "modem":
            x0, y0, x1, y1 = P * 0.28, P * 0.3, P * 0.72, P * 0.68
            d.rounded_rectangle([x0, y0, x1, y1], radius=5 * S, fill=(14, 30, 70, 255), outline=(255, 255, 255, 255), width=3 * S)
            d.text((P / 2, (y0 + y1) / 2 + S), "M", font=L.font(L.ANTON, int(P * 0.26)), fill=(120, 190, 255, 255), anchor="mm")
            for q in range(3):
                d.ellipse([P * 0.36 + q * P * 0.1, y1 + 4 * S, P * 0.36 + q * P * 0.1 + 5 * S, y1 + 9 * S], fill=(255, 255, 255, 255))
    return im.resize((out_px, out_px), Image.LANCZOS)


_sd = {}


def node_sd(kind, px, grey=False):
    key = (kind, px, grey)
    if key not in _sd:
        sd = L.sticker_from_art(icon(kind, px), border=5, seed=sum(map(ord, kind)) % 97)
        _sd[key] = L.greyscale(sd, 0.7) if grey else sd
    return _sd[key]


_tok = {}


def token_sd(px=58):
    """The operative token: CELL-9's Breaker emblem as a die-cut sticker (pink, the class colour)."""
    if px not in _tok:
        _tok[px] = L.sticker_from_art(L.glyph("slice_exploit", px, fill=PINK, ow=4), border=6, seed=77)
    return _tok[px]


# ------------------------------------------------------------------ circuit inlay traces + pads
def offset_poly(pts, d):
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            nx, ny = -ay, ax
        elif i == n - 1:
            ax, ay = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
            nx, ny = -ay, ax
        else:
            a1 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            a2 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            l1, l2 = math.hypot(*a1) or 1, math.hypot(*a2) or 1
            n1 = (-a1[1] / l1, a1[0] / l1)
            n2 = (-a2[1] / l2, a2[0] / l2)
            nx, ny = n1[0] + n2[0], n1[1] + n2[1]
            ln = math.hypot(nx, ny) or 1
            nx, ny = nx / ln, ny / ln
            cosh = max(0.5, nx * n1[0] + ny * n1[1])
            out.append((pts[i][0] + nx * d / cosh, pts[i][1] + ny * d / cosh))
            continue
        ln = math.hypot(nx, ny) or 1
        out.append((pts[i][0] + nx / ln * d, pts[i][1] + ny / ln * d))
    return out


def polyline_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def cut_poly(pts, t0, t1):
    """The part of a polyline between fractions t0..t1 of its length."""
    tot = polyline_len(pts)
    a, b = t0 * tot, t1 * tot
    out, acc = [], 0.0
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        seg = math.hypot(q[0] - p[0], q[1] - p[1])
        s0, s1 = acc, acc + seg
        if s1 >= a and s0 <= b and seg > 0:
            u0 = max(0.0, (a - s0) / seg)
            u1 = min(1.0, (b - s0) / seg)
            pa = (p[0] + (q[0] - p[0]) * u0, p[1] + (q[1] - p[1]) * u0)
            pb = (p[0] + (q[0] - p[0]) * u1, p[1] + (q[1] - p[1]) * u1)
            if not out:
                out.append(pa)
            out.append(pb)
        acc = s1
    return out


def point_at(pts, t):
    seg = cut_poly(pts, 0, max(1e-4, t))
    return seg[-1] if seg else pts[0]


class Inlay:
    """Collects traces into masks per colour, then lays them in one pass (under-shadow, glow, body, core)."""

    def __init__(self, size=(W, H), k=1.0):
        self.size = size
        self.k = k
        self.layers = []  # (mask, colour, glow)

    def trace(self, pts, col, width=3.0, lanes=3, gap=4.0, glow=0.7, alpha=1.0, pads=True):
        k = self.k
        m = Image.new("L", self.size, 0)
        d = ImageDraw.Draw(m)
        offs = [(i - (lanes - 1) / 2) * gap * k for i in range(lanes)]
        for o in offs:
            pp = offset_poly(pts, o) if o else pts
            d.line(pp, fill=int(255 * alpha), width=max(1, int(round(width * k))), joint="curve")
        if pads:
            for p in (pts[0], pts[-1]):
                pass
            # small solder pads at every bend (the inlay's chip look)
            for p in pts[1:-1]:
                r = 2.6 * k
                d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=int(255 * alpha))
        self.layers.append((m, col, glow))

    def lay(self, canvas):
        if not self.layers:
            return canvas
        un = Image.new("L", self.size, 0)
        for m, _, _ in self.layers:
            un = ImageChops.lighter(un, m)
        sh = un.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5 * self.k))
        canvas = SL.over(canvas, (4, 3, 8), SL.scale_mask(sh, 0.7))
        for m, col, glow in self.layers:
            if glow > 0:
                g = m.filter(ImageFilter.GaussianBlur(7 * self.k))
                lay = Image.new("RGBA", self.size, col + (0,))
                lay.putalpha(SL.scale_mask(g, glow))
                canvas = Image.alpha_composite(canvas, lay)
            lay = Image.new("RGBA", self.size, col + (0,))
            lay.putalpha(m)
            canvas = Image.alpha_composite(canvas, lay)
            core = m.filter(ImageFilter.MinFilter(3)) if self.k >= 1 else m.point(lambda v: v // 3)
            canvas = SL.over(canvas, tuple(min(255, c + 120) for c in col), SL.scale_mask(core, 0.55))
        return canvas


def pad(canvas, quad, col, fill_a=210, glow=0.8, lit=1.0, k=1.0, pins=True):
    """A circuit-inlay socket (the raid node language): dark diamond, outer ring, inner ring, pins."""
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    m = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(m)
    q2 = [(cx + (x - cx) * 0.62, cy + (y - cy) * 0.62) for (x, y) in quad]
    d.line(quad + [quad[0]], fill=255, width=max(1, int(3 * k)), joint="curve")
    d.line(q2 + [q2[0]], fill=200, width=max(1, int(2 * k)))
    if pins:
        for i in range(4):
            a, b = quad[i], quad[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            nx, ny = ey, -ex
            ln = math.hypot(nx, ny) or 1
            # outward normal
            if (nx * ((a[0] + b[0]) / 2 - cx) + ny * ((a[1] + b[1]) / 2 - cy)) < 0:
                nx, ny = -nx, -ny
            nx, ny = nx / ln, ny / ln
            for t in (0.3, 0.5, 0.7):
                px, py = a[0] + ex * t, a[1] + ey * t
                d.line([(px, py), (px + nx * 6 * k, py + ny * 6 * k)], fill=220, width=max(1, int(2 * k)))
    base = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(base).polygon(quad, fill=fill_a)
    canvas = SL.over(canvas, (6, 5, 12), base)
    inner = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(inner).polygon(q2, fill=int(90 * lit))
    canvas = SL.over(canvas, col, inner)
    if glow:
        g = m.filter(ImageFilter.GaussianBlur(8 * k))
        canvas = SL.over(canvas, col, SL.scale_mask(g, glow * lit))
    canvas = SL.over(canvas, col, SL.scale_mask(m, lit))
    return canvas


def poly_wash(canvas, quad, col, k=0.5, glow=0.5, mode="add"):
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).polygon(quad, fill=255)
    if mode == "dark":
        return SL.over(canvas, (6, 5, 12), SL.scale_mask(m, k))
    if mode == "grey":
        rgb = canvas.convert("RGB")
        g = rgb.convert("L").convert("RGB")
        g = Image.blend(g, Image.new("RGB", g.size, (14, 12, 20)), 0.55).convert("RGBA")
        return Image.composite(g, canvas, SL.scale_mask(m, k))
    a = np.asarray(canvas, np.float32)
    mm = np.asarray(m, np.float32)[..., None] / 255 * k
    if glow:
        gg = np.asarray(m.filter(ImageFilter.GaussianBlur(18)), np.float32)[..., None] / 255 * glow
        mm = np.maximum(mm, gg * 0.6)
    a[..., :3] = np.clip(a[..., :3] + np.array(col, np.float32) * mm, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ holo (decrypted corp intel)
def holo(canvas, box, col=MER, title=None, seed=4, alpha=0.8):
    x0, y0, x1, y1 = box
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    canvas = SL.over(canvas, tuple(int(c * 0.16) for c in col), SL.scale_mask(m, alpha))
    sl = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(sl)
    for yy in range(y0, y1, 4):
        d.line([(x0, yy), (x1, yy)], fill=30)
    rng = random.Random(seed)
    for _ in range(4):
        by = rng.randint(y0, y1 - 12)
        d.rectangle([x0, by, x1, by + rng.randint(3, 10)], fill=44)
    canvas = SL.over(canvas, col, ImageChops.multiply(sl, m))
    e = ImageChops.subtract(m, SL.erode(m, 2))
    canvas = SL.over(canvas, (255, 60, 200), SL.scale_mask(SL.shift(e, -2, 0), 0.45))
    canvas = SL.over(canvas, (60, 230, 255), SL.scale_mask(SL.shift(e, 2, 0), 0.45))
    canvas = SL.over(canvas, col, SL.scale_mask(e.filter(ImageFilter.GaussianBlur(8)), 0.6))
    canvas = SL.over(canvas, col, e)
    d = ImageDraw.Draw(canvas)
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx + sx * 4, cy + sy * 4), (cx + sx * 26, cy + sy * 4)], fill=col + (255,), width=3)
        d.line([(cx + sx * 4, cy + sy * 4), (cx + sx * 4, cy + sy * 26)], fill=col + (255,), width=3)
    if title:
        d.text((x0 + 16, y0 + 22), title, font=L.f_ui(22, b"Bold"), fill=tuple(min(255, c + 60) for c in col) + (255,), anchor="lm")
    return canvas


def meridian_seal(canvas, xy, r, col=MER):
    """Meridian's crest: the gantry-crane A in a ring with the corp name."""
    x, y = xy
    d = ImageDraw.Draw(canvas)
    d.ellipse([x - r, y - r, x + r, y + r], outline=col + (230,), width=3)
    d.ellipse([x - r + 7, y - r + 7, x + r - 7, y + r - 7], outline=col + (150,), width=1)
    f = L.f_mono(max(9, r // 4))
    label = "MERIDIAN FREIGHT * "
    for i, ch in enumerate(label * 2):
        a = -math.pi / 2 + i * 2 * math.pi / (len(label) * 2)
        rr = r - 13
        lay = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((15, 15), ch, font=f, fill=col + (220,), anchor="mm")
        lay = lay.rotate(-math.degrees(a) - 90, Image.BICUBIC)
        canvas.alpha_composite(lay, (int(x + rr * math.cos(a) - 15), int(y + rr * math.sin(a) - 15)))
    d = ImageDraw.Draw(canvas)
    s = r * 0.4
    d.line([(x - s * 0.8, y + s * 0.7), (x, y - s), (x + s * 0.8, y + s * 0.7)], fill=col + (255,), width=4)
    d.line([(x - s * 0.45, y + s * 0.1), (x + s * 0.45, y + s * 0.1)], fill=col + (255,), width=3)
    d.line([(x - s * 1.1, y - s * 0.55), (x + s * 1.2, y - s * 0.75)], fill=col + (255,), width=3)
    return canvas


# ------------------------------------------------------------------ terminal chip button + small helpers
def term_button(canvas, box, label, key=None, accent=CYAN):
    x0, y0, x1, y1 = box
    c = L.CRT(x1 - x0, y1 - y0, accent, None, header=False, seed=x0)
    c.text(((x1 - x0) / 2, (y1 - y0) / 2 - (6 if key else 0)), label, 22, (235, 245, 250), anchor="mm")
    if key:
        c.text(((x1 - x0) / 2, (y1 - y0) / 2 + 16), key, 14, accent, anchor="mm")
    return L.paste(canvas, c.finish(scan=0.15), x0, y0)


def chip(canvas, xy, s, col=CYAN, size=15, anchor="mm", fill_a=220, bright=False):
    f = L.f_mono(size)
    tw = f.getlength(s)
    x, y = xy
    w, h = tw + 14, size + 10
    if anchor == "mm":
        x0, y0 = x - w / 2, y - h / 2
    elif anchor == "lm":
        x0, y0 = x, y - h / 2
    else:
        x0, y0 = x - w, y - h / 2
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=4, fill=(col if bright else (8, 10, 16)) + (fill_a,), outline=col + (255,), width=1)
    d.text((x0 + w / 2, y0 + h / 2), s, font=f, fill=((10, 10, 14) if bright else col) + (255,), anchor="mm")
    return canvas


def dashed_along(pen, pts, offset=12.0, dash=16.0, gap=11.0, width=7, t0=0.0, t1=1.0):
    """Grease-pencil what-if: dashes that follow the real link (true to the rules), set off to one side."""
    pp = offset_poly(cut_poly(pts, t0, t1), offset) if offset else cut_poly(pts, t0, t1)
    tot = polyline_len(pp)
    s = 0.0
    while s < tot:
        seg = cut_poly(pp, s / tot, min(1.0, (s + dash) / tot))
        if len(seg) >= 2:
            pen.stroke(SL.catmull(pen.wobble(seg, 0.6), 4) if len(seg) > 2 else seg, width=width, taper=False)
        s += dash + gap


def save_gif(frames, durs, path, size=(800, 450), colors=200):
    """One global palette (built from a mosaic of every frame) so unchanged pixels stay unchanged between frames."""
    fr = [f.convert("RGB").resize(size, Image.LANCZOS) for f in frames]
    tw, th = size[0] // 4, size[1] // 4
    cols = 8
    rows = (len(fr) + cols - 1) // cols
    mos = Image.new("RGB", (tw * cols, th * rows))
    for i, f in enumerate(fr):
        mos.paste(f.resize((tw, th), Image.BILINEAR), ((i % cols) * tw, (i // cols) * th))
    pal = mos.quantize(colors=colors, method=Image.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in fr]
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False, disposal=1)
    return os.path.getsize(path)


def ahead_text(kinds):
    """'2 elites, 1 modem, 3 routers' from the node kinds still reachable (final Rack excluded)."""
    order = (("elite", "elite", "elites"), ("modem", "modem", "modems"), ("terminal", "terminal", "terminals"),
             ("router", "router", "routers"), ("rack", "Rack", "Racks"))
    parts = []
    for k, one, many in order:
        n = sum(1 for x in kinds if x == k)
        if n:
            parts.append("%d %s" % (n, one if n == 1 else many))
    return ", ".join(parts)


def arrow_head(pen, pts, width=7, head=18):
    ex, ey = pts[-1]
    px, py = pts[-2] if len(pts) > 1 else (ex - 1, ey)
    ang = math.atan2(ey - py, ex - px)
    for s in (-0.5, 0.5):
        a = ang + math.pi + s
        pen.stroke([(ex + head * math.cos(a), ey + head * math.sin(a)), (ex, ey)], width=width, taper=False)
