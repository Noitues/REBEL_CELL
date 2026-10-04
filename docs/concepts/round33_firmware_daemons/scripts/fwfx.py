"""Round 33 firmware trigger FX on a socketed wheel: the scene (wheel + pointer at the top), the gold PCB trace
from the chip, the neighbour ghost (Mirror), the 1.5x neighbour (Shunt), the Heat / RAM pops.

A scene is built for a landing target k (the wheel slice list is rotated so k sits at the top, read blocks upright)
and a small rotation `rot` (degrees clockwise) = where inside the slice the pointer landed.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import fwlib as F
L = F.L

GOLD = (255, 206, 92)
SLICES = [("EXPLOIT", 6, 1, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
          ("EXPLOIT", 8, 2, None), ("ZERO-DAY", 12, 1, "OVERCLOCKED"), ("NULL", None, 1, None)]
FWS = ["mirror", None, "shunt", "leech", "burner", "recycler"]
READ_RHO = 268.0


class Scene:
    def __init__(self, k, r_px=220, slices=None, fws=None, key="fx"):
        S = slices or SLICES
        W = fws or FWS
        self.n = len(S)
        self.k = k
        self.S = S[k:] + S[:k]
        self.W = W[k:] + W[:k]
        self.r = r_px
        self.key = "%s_k%d" % (key, k)
        self.base = F.wheel_cached(self.S, r_px, self.key)
        self.size = self.base.width
        self.c = self.size / 2
        self.kk = r_px / 360.0

    def wheel(self, rot=0.0, lit=None, lit_k=1.0, blur=0.0):
        img = self.base.copy()
        s = F.chip_px(self.r)
        for i, f in enumerate(self.W):
            if f:
                x, y, a = F.socket_pos(self.n, i, self.r, img.width)
                img = F.put_chip(img, f, x, y, a, s, lit=(lit_k if lit == i else 0.0))
        if blur < 1:
            return img.rotate(-rot, Image.BICUBIC) if rot else img
        nn = int(min(10, max(3, blur / 4)))
        acc = np.zeros((img.height, img.width, 4), np.float32)
        pm = img.convert("RGBa")
        for j in range(nn):
            acc += np.asarray(pm.rotate(-(rot - blur * j / nn), Image.BICUBIC), np.float32)
        return Image.fromarray((acc / nn).astype(np.uint8), "RGBa").convert("RGBA")

    def pos(self, rho_master, ang, rot=0.0):
        a = math.radians(ang + rot)
        r = rho_master * self.kk
        return self.c + r * math.sin(a), self.c - r * math.cos(a)

    def chip_xy(self, i, rot=0.0):
        span = 360 / self.n
        ang = i * span - span / 2 * F.SOCKET_DA
        return self.pos(F.SOCKET_RHO, ang, rot), ang + rot

    def read_xy(self, i, rot=0.0):
        return self.pos(READ_RHO, i * 360 / self.n, rot)


def pointer(img, x, y, col=(255, 255, 255), size=22, tick=0.0):
    d = ImageDraw.Draw(img)
    d.polygon([(x - size * 0.7, y - size * 1.3), (x + size * 0.7, y - size * 1.3), (x, y + size * 0.2)], fill=col + (255,), outline=L.INK + (255,))
    if tick > 0:
        g = Image.new("L", img.size, 0)
        ImageDraw.Draw(g).ellipse([x - 30, y - 30, x + 30, y + 30], fill=int(160 * tick))
        img = L.SL.over(img, (255, 255, 255), g.filter(ImageFilter.GaussianBlur(12)))
    return img


def glow_line(img, pts, col=GOLD, w=4, k=1.0, pulse=None):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).line(pts, fill=255, width=w, joint="curve")
    g = m.filter(ImageFilter.GaussianBlur(w * 2.2)).point(lambda v: min(255, int(v * 2.2 * k)))
    img = L.SL.over(img, col, g)
    img = L.SL.over(img, tuple(min(255, int(c * 0.6 + 110)) for c in col), m.point(lambda v: int(v * k)))
    if pulse is not None:
        x, y = path_at(pts, pulse)
        p = Image.new("L", img.size, 0)
        ImageDraw.Draw(p).ellipse([x - w * 2.4, y - w * 2.4, x + w * 2.4, y + w * 2.4], fill=255)
        img = L.SL.over(img, col, p.filter(ImageFilter.GaussianBlur(w * 2)))
        img = L.SL.over(img, (255, 255, 255), p.filter(ImageFilter.GaussianBlur(1)))
    return img


def path_at(pts, u):
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    tot = sum(seg)
    t = u * tot
    for i, s in enumerate(seg):
        if t <= s or i == len(seg) - 1:
            f = 0 if s == 0 else min(1.0, t / s)
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        t -= s
    return pts[-1]


def sub_path(pts, u):
    """The first u (0..1) of a polyline."""
    if u >= 1:
        return pts
    seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    tot = sum(seg)
    t = u * tot
    out = [pts[0]]
    for i, s in enumerate(seg):
        if t <= s:
            f = 0 if s == 0 else t / s
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
            return out
        out.append(pts[i + 1])
        t -= s
    return out


def trace_path(sc, i_from, ang_to, rot, rho_in=292.0):
    """PCB trace: from the chip, along the rim (at the socket radius) to ang_to, then radially in to the read block."""
    (x0, y0), a0 = sc.chip_xy(i_from, rot)
    pts = [(x0, y0)]
    a_from = a0
    n = 14
    for j in range(1, n + 1):
        a = a_from + (ang_to + rot - a_from) * j / n
        pts.append(sc.pos(F.SOCKET_RHO, a - rot, rot))
    pts.append(sc.pos(rho_in, ang_to, rot))
    return pts


def ghost_read(img, sc, i_src, at_xy, k=1.0, col=(92, 225, 255), cover=True):
    """A phosphor ghost of slice i_src's read block (glyph + value), drawn at at_xy. cover: dim the read block
    already there first (Mirror: this slice now reads as its neighbour)."""
    if cover:
        x, y = at_xy
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).ellipse([x - 96 * sc.r / 220, y - 46 * sc.r / 220, x + 104 * sc.r / 220, y + 46 * sc.r / 220], fill=int(255 * k))
        img = L.SL.over(img, (10, 8, 16), m.filter(ImageFilter.GaussianBlur(3)))
    prog, val, tier, st = sc.S[i_src][:4]
    gname = {"EXPLOIT": "slice_exploit", "FIREWALL": "slice_firewall", "PROXY": "slice_proxy", "ZERO-DAY": "slice_zero_day",
             "NULL": "slice_null", "PATCH": "slice_patch", "VIRUS": "slice_virus", "SANDBOX": "slice_sandbox", "TROJAN": "slice_trojan"}[prog]
    gs = int(46 * sc.r / 220)
    g = L.glyph(gname, gs, fill=col)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x, y = at_xy
    lay.alpha_composite(g, (int(x - gs - 4), int(y - gs / 2)))
    d = ImageDraw.Draw(lay)
    d.text((x + 6, y), str(val if val is not None else "1/0"), font=L.f_num(int(66 * sc.r / 220)), fill=col + (255,), anchor="lm")
    a = lay.split()[3].point(lambda v: int(v * 0.85 * k))
    glow = a.filter(ImageFilter.GaussianBlur(6))
    img = L.SL.over(img, col, glow)
    lay.putalpha(a)
    img.alpha_composite(lay)
    return img


def outline_slice(img, sc, i, rot, col, k=1.0, w=5):
    span = 360 / sc.n
    r_o = 360 * sc.kk + 2
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    a0 = -90 + i * span - span / 2 + rot
    d.arc([sc.c - r_o, sc.c - r_o, sc.c + r_o, sc.c + r_o], a0 + 1, a0 + span - 1, fill=255, width=w)
    for a in (a0 + 1, a0 + span - 1):
        ra = math.radians(a)
        d.line([(sc.c + 130 * sc.kk * math.cos(ra), sc.c + 130 * sc.kk * math.sin(ra)), (sc.c + r_o * math.cos(ra), sc.c + r_o * math.sin(ra))], fill=255, width=w)
    g = m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: min(255, int(v * 2 * k)))
    img = L.SL.over(img, col, g)
    return L.SL.over(img, col, m.point(lambda v: int(v * k)))


def term_chip(text, col, size=18):
    f = L.f_mono(size)
    w = int(f.getlength(text)) + 22
    h = int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=tuple(int(c * 0.14) for c in col) + (235,), outline=col + (255,), width=2)
    d.text((w / 2, h / 2 + 1), text, font=f, fill=col + (255,), anchor="mm")
    return im


def pop(img, im, x, y, k=1.0, rise=0.0):
    if k <= 0:
        return img
    lay = im.copy()
    a = lay.split()[3].point(lambda v: int(v * k))
    lay.putalpha(a)
    img.alpha_composite(lay, (int(x - im.width / 2), int(y - im.height / 2 - rise)))
    return img


def ram_bar(img, x, y, n, filled, flash=0.0):
    c = L.CRT(250, 58, L.CYAN, None, header=False, seed=5)
    c.text((12, 8), "RAM", 14, (150, 220, 240))
    c.text((12, 24), "%d/12" % filled, 22, L.CYAN, fnt=L.f_num(26))
    c.bar(84, 22, 12, filled, w=10, h=18, gap=3)
    im = c.finish(scan=0.15)
    if flash > 0:
        g = Image.new("L", im.size, 0)
        ImageDraw.Draw(g).rectangle([84 + (filled - 1) * 13 - 4, 18, 84 + (filled - 1) * 13 + 14, 44], fill=int(255 * flash))
        im = L.SL.over(im, (255, 255, 255), g.filter(ImageFilter.GaussianBlur(4)))
    img.alpha_composite(im, (int(x), int(y)))
    return img


def ram_pip(img, x, y, k=1.0):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x - 7, y - 10, x + 7, y + 10], radius=3, fill=255)
    img = L.SL.over(img, L.CYAN, m.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 2 * k))))
    return L.SL.over(img, (230, 250, 255), m.point(lambda v: int(v * k)))
