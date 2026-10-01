"""Round 15: corp slice animations as FULL-SCREEN backgrounds (no little motif panel).

scene(ctx, corp, kind, t) draws one frame (t in [0, 1), seamless loop) of the corp's animation for a
slice type onto a transparent RGBA the size of the slice screen texture. The corp material sits under it
(darkened); the white glyph + value read block sits on top (slicelib), as on the player's C slices.

Texture space: y = 0 is the slice's outer edge, y = H its inner edge; x = W/2 is the midline;
ctx.halfw(y) is the visible half-width at row y. The read plate is centred near y = 0.39 H.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_num, f_ui, f_mono

PAL = {
    "meridian": dict(a=(255, 140, 26), dim=(120, 60, 14), hot=(255, 46, 40), paper=(214, 206, 186), ink=(26, 20, 14),
                     card=(132, 86, 44), steel=(150, 150, 158), crane=(255, 196, 40)),
    "solace": dict(a=(61, 255, 139), dim=(20, 110, 80), hot=(255, 70, 150), paper=(226, 244, 238), ink=(8, 34, 30),
                   glass=(170, 255, 225)),
    "halcyon": dict(a=(150, 135, 255), dim=(60, 64, 160), hot=(255, 50, 70), paper=(222, 226, 255), ink=(14, 16, 54),
                    gold=(255, 200, 90), steel=(196, 200, 220), blue=(60, 120, 255)),
    "orbital": dict(a=(140, 192, 255), dim=(60, 90, 170), hot=(255, 226, 150), paper=(236, 244, 255), ink=(8, 14, 40),
                    gold=(255, 215, 120), rock=(150, 120, 100), planet=(60, 110, 200)),
}


def tri(x):
    x = x % 1.0
    return 1 - abs(2 * x - 1)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def rot(pts, ang, cx, cy):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def W_(w):
    return max(1, int(round(w)))


class Sc:
    def __init__(self, ctx, corp):
        self.W, self.H, self.u = ctx.W, ctx.H, ctx.ss
        self.cx = ctx.W / 2
        self.ctx = ctx
        self.P = PAL.get(corp, {})
        self.im = Image.new("RGBA", (ctx.W, ctx.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.gl = Image.new("RGBA", (ctx.W, ctx.H), (0, 0, 0, 0))
        self.g = ImageDraw.Draw(self.gl)

    def X(self, f, y):  # f in -1..1 across the visible width at row y
        return self.cx + f * self.ctx.halfw(y) * 0.92

    def Y(self, f):
        return f * self.H

    def done(self):
        g = self.gl.filter(ImageFilter.GaussianBlur(6 * self.u))
        out = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        out.alpha_composite(g)
        out.alpha_composite(self.im)
        return out


# ================================================================== MERIDIAN
def mer_attack(s, t):  # crates ride the rollers (kept from round 14, now full screen)
    u, d, P = s.u, s.d, s.P
    yb = s.Y(0.70)
    d.rectangle([0, yb, s.W, yb + 14 * u], fill=(36, 30, 26, 255))
    per = 30 * u
    for k in range(-1, int(s.W / per) + 2):
        x = k * per + 15 * u
        d.ellipse([x - 9 * u, yb + 2 * u, x + 9 * u, yb + 20 * u], fill=(90, 86, 84, 255), outline=(20, 16, 14, 255), width=W_(u))
        a = 2 * math.pi * (t * 2 + k * 0.1)
        d.line([(x, yb + 11 * u), (x + 7 * u * math.cos(a), yb + 11 * u + 7 * u * math.sin(a))], fill=(20, 16, 14, 255), width=W_(2 * u))
    gap = 120 * u
    for k in range(-1, int(s.W / gap) + 2):
        x = (k + t) * gap
        w, h = 74 * u, 62 * u
        d.rectangle([x, yb - h, x + w, yb], fill=P["card"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
        d.rectangle([x + w * 0.42, yb - h, x + w * 0.58, yb], fill=(212, 190, 140, 255))
        d.text((x + 6 * u, yb - h + 6 * u), "MRD", font=f_num(int(16 * u)), fill=P["ink"] + (255,))
        for m in range(3):
            d.line([(x - (10 + m * 14) * u, yb - (14 + m * 14) * u), (x - (2 + m * 14) * u, yb - (14 + m * 14) * u)], fill=P["a"] + (200,), width=W_(2 * u))
    for k in range(5):  # push chevrons along the top band
        x = ((k / 5 + t) % 1.0) * s.W
        y = s.Y(0.09)
        d.line([(x - 10 * u, y - 10 * u), (x, y), (x - 10 * u, y + 10 * u)], fill=P["hot"] + (255,), width=W_(4 * u))


def mer_crit(s, t):  # laser over a big barcode + PRIORITY stamp (kept, now full screen)
    u, d, P = s.u, s.d, s.P
    y0, y1 = s.Y(0.06), s.Y(0.32)
    x0, x1 = s.X(-0.85, y1), s.X(0.85, y1)
    d.rectangle([x0, y0, x1, y1], fill=P["paper"] + (235,))
    rng = np.random.default_rng(4)
    x = x0 + 6 * u
    while x < x1 - 6 * u:
        bw = int(rng.integers(1, 4)) * u * 1.4
        d.rectangle([x, y0 + 6 * u, x + bw, y1 - 14 * u], fill=(20, 18, 16, 255))
        x += bw + int(rng.integers(1, 3)) * u * 1.6
    d.text((x0 + 8 * u, y1 - 13 * u), "4 47102 88041 9  PRIORITY", font=f_mono(int(9 * u)), fill=P["ink"] + (255,))
    ly = y0 + 6 * u + (y1 - y0 - 20 * u) * tri(t * 2)
    s.g.line([(x0 - 10 * u, ly), (x1 + 10 * u, ly)], fill=P["hot"] + (255,), width=W_(10 * u))
    d.line([(x0 - 10 * u, ly), (x1 + 10 * u, ly)], fill=(255, 120, 110, 255), width=W_(2.5 * u))
    sx, sy = s.cx, s.Y(0.96)  # scanner fan from the inner edge
    for f in (-0.8, 0, 0.8):
        d.line([(sx, sy), (s.cx + f * (x1 - x0) / 2, y1)], fill=P["hot"] + (120,), width=W_(1.5 * u))
    if t > 0.55:  # stamp lands
        k = ease((t - 0.55) / 0.08)
        f = f_num(int(30 * u))
        txt = "PRIORITY"
        tw = f.getlength(txt)
        st = Image.new("RGBA", (int(tw + 20 * u), int(42 * u)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rectangle([0, 0, st.width - 1, st.height - 1], outline=P["hot"] + (255,), width=W_(3 * u))
        sd.text((10 * u, 2 * u), txt, font=f, fill=P["hot"] + (255,))
        sc = 1.6 - 0.6 * k
        st = st.resize((int(st.width * sc), int(st.height * sc)))
        st = st.rotate(-14, expand=True, resample=Image.BICUBIC)
        s.im.alpha_composite(st, (int(s.cx - st.width / 2), int(s.Y(0.74) - st.height / 2)))


def container(d, x, y, w, h, col, ink, u, label=None):
    d.rectangle([x, y, x + w, y + h], fill=col + (255,), outline=ink + (255,), width=W_(2 * u))
    for k in np.arange(x + 5 * u, x + w - 2 * u, 6 * u):
        d.line([(k, y + 3 * u), (k, y + h - 3 * u)], fill=tuple(int(c * 0.7) for c in col) + (255,), width=W_(1.5 * u))
    d.line([(x + w - 8 * u, y + 4 * u), (x + w - 8 * u, y + h - 4 * u)], fill=ink + (255,), width=W_(2 * u))
    if label:
        d.text((x + 6 * u, y + 4 * u), label, font=f_mono(int(9 * u)), fill=(240, 236, 220, 255))


def mer_defend(s, t):  # a crane sets a container on top of a container wall
    u, d, P = s.u, s.d, s.P
    cols = [(196, 92, 30), (60, 120, 170), (200, 150, 40), (150, 60, 50)]
    wy = s.Y(0.66)
    ch, cw = 34 * u, 76 * u
    for r in range(3):
        y = wy + r * ch
        off = (r % 2) * cw / 2
        for k in range(-2, 4):
            x = s.cx - 1.5 * cw + k * cw - off
            container(d, x, y, cw - 2 * u, ch - 2 * u, cols[(k + r) % 4], P["ink"], u)
    # jib across the outer edge, trolley above the landing slot
    jy = s.Y(0.04)
    d.rectangle([0, jy, s.W, jy + 12 * u], fill=P["crane"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
    for k in np.arange(0, s.W, 16 * u):
        d.line([(k, jy), (k + 16 * u, jy + 12 * u)], fill=P["ink"] + (255,), width=W_(2 * u))
    tx = s.cx + 0.5 * cw
    d.rectangle([tx - 16 * u, jy + 12 * u, tx + 16 * u, jy + 22 * u], fill=(70, 70, 76, 255))
    k = ease(min(1, t / 0.7))
    land = wy - ch
    cy = s.Y(0.16) + (land - s.Y(0.16)) * k
    if t > 0.8:
        cy = land
    d.line([(tx - 10 * u, jy + 22 * u), (tx - cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
    d.line([(tx + 10 * u, jy + 22 * u), (tx + cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
    container(d, tx - cw / 2, cy, cw - 2 * u, ch - 2 * u, (230, 120, 30), P["ink"], u, "MRDU")
    if 0.68 < t < 0.8:  # dust on landing
        for k2 in range(5):
            a = math.radians(160 + k2 * 55 / 4 * 4)
            dx = (t - 0.68) * 300 * u
            d.ellipse([tx - cw / 2 - dx * 0.3 - 4 * u, land + ch - 6 * u, tx - cw / 2 - dx * 0.3 + 4 * u, land + ch + 2 * u], fill=(210, 190, 160, 160))


def mer_shield(s, t):  # a box lid closes, then tape seals it
    u, d, P = s.u, s.d, s.P
    bx0, bx1 = s.cx - 86 * u, s.cx + 86 * u
    by0, by1 = s.Y(0.48), s.Y(0.97)
    d.rectangle([bx0, by0, bx1, by1], fill=P["card"] + (255,), outline=P["ink"] + (255,), width=W_(2.5 * u))
    d.text((bx0 + 10 * u, by1 - 26 * u), "THIS SIDE UP  ^^", font=f_mono(int(10 * u)), fill=P["ink"] + (255,))
    k = ease(min(1, t / 0.45))
    for side in (-1, 1):  # flaps fold down from open (up) to closed (flat on top)
        ang = (1 - k) * 100
        hx = s.cx + side * 86 * u
        L = 86 * u
        tipx = hx - side * L * math.cos(math.radians(ang))
        tipy = by0 - L * math.sin(math.radians(ang))
        d.polygon([(hx, by0), (tipx, tipy), (tipx, tipy - 6 * u), (hx, by0 - 6 * u)], fill=(206, 146, 84, 255), outline=P["ink"] + (255,))
    if t > 0.5:  # tape pulled across the seam
        k2 = ease((t - 0.5) / 0.4)
        xe = bx0 - 10 * u + (bx1 - bx0 + 20 * u) * k2
        d.rectangle([bx0 - 10 * u, by0 - 9 * u, xe, by0 + 7 * u], fill=(225, 200, 140, 230))
        d.ellipse([xe - 14 * u, by0 - 22 * u, xe + 14 * u, by0 + 6 * u], fill=(110, 90, 60, 255), outline=P["ink"] + (255,), width=W_(2 * u))
        d.ellipse([xe - 6 * u, by0 - 14 * u, xe + 6 * u, by0 - 2 * u], fill=(30, 26, 20, 255))
        d.line([(xe + 10 * u, by0 - 20 * u), (xe + 34 * u, by0 - 46 * u)], fill=(60, 50, 40, 255), width=W_(5 * u))


def mer_tariff(s, t):  # JUDGEMENT / TARIFF: a receipt prints out of a machine
    u, d, P = s.u, s.d, s.P
    mx0, mx1 = s.cx - 70 * u, s.cx + 70 * u
    my0 = s.Y(0.74)
    d.rounded_rectangle([mx0, my0, mx1, s.H + 10 * u], radius=10 * u, fill=(46, 44, 48, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.rectangle([mx0 + 14 * u, my0 + 8 * u, mx1 - 14 * u, my0 + 30 * u], fill=(20, 40, 24, 255))
    d.text((mx0 + 20 * u, my0 + 11 * u), "RAM -3 DUE", font=f_mono(int(10 * u)), fill=(120, 255, 140, 255))
    d.rectangle([s.cx - 46 * u, my0 - 3 * u, s.cx + 46 * u, my0 + 3 * u], fill=(10, 10, 12, 255))
    L = s.Y(0.70) * (0.25 + 0.75 * ((t * 1.0) % 1.0))
    top = my0 - L
    pw = 40 * u
    teeth = [(s.cx - pw + k * 8 * u, top - (4 * u if k % 2 else 0)) for k in range(11)]
    d.polygon([(s.cx - pw, my0)] + teeth + [(s.cx + pw, my0)], fill=(250, 248, 240, 255), outline=(120, 110, 100, 255))
    lines = ["JUDGEMENT", "MERIDIAN", "-----", "PKG 4471", "RAM  -3", "LATE FEE", "-----", "TOTAL"]
    for i, ln in enumerate(lines):
        y = my0 - 14 * u - i * 13 * u
        if y < top + 6 * u:
            break
        d.text((s.cx - pw + 6 * u, y), ln, font=f_mono(int(9 * u)), fill=(P["hot"] if "RAM" in ln else (40, 36, 30)) + (255,))


def mer_judgement(s, t):  # JUDGEMENT (RAM drain): a gavel strikes the block - impact flash + shockwave
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx - 10 * u, s.Y(0.84)
    d.rounded_rectangle([bx - 70 * u, by, bx + 70 * u, by + 30 * u], radius=W_(6 * u), fill=(110, 64, 30, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.rectangle([bx - 60 * u, by + 6 * u, bx + 60 * u, by + 10 * u], fill=(160, 100, 50, 255))
    if t < 0.42:
        ang = -70 * (1 - ease(t / 0.42) ** 2)
    elif t < 0.6:
        ang = 0.0
    else:
        ang = -70 * ease((t - 0.6) / 0.4)
    piv = (bx + 170 * u, by - 40 * u)
    head = rect_pts(bx - 46 * u, by - 70 * u, bx + 46 * u, by - 4 * u)
    handle = rect_pts(bx + 30 * u, by - 46 * u, piv[0], by - 30 * u)
    for pts, col in ((handle, (120, 74, 36)), (head, (140, 86, 40))):
        d.polygon(rot(pts, ang, *piv), fill=col + (255,), outline=P["ink"] + (255,))
    for xb in (-30, 30):
        band = rect_pts(bx + (xb - 4) * u, by - 70 * u, bx + (xb + 4) * u, by - 4 * u)
        d.polygon(rot(band, ang, *piv), fill=(220, 180, 90, 255))
    if 0.42 <= t < 0.85:  # impact: flash and shockwave rings
        k = (t - 0.42) / 0.43
        a = int(255 * (1 - k))
        for j, sc in enumerate((1.0, 0.65)):
            rx, ry = (40 + 220 * k * sc) * u, (10 + 50 * k * sc) * u
            s.g.ellipse([bx - rx, by + 4 * u - ry, bx + rx, by + 4 * u + ry], outline=P["a"] + (a,), width=W_(10 * u))
            d.ellipse([bx - rx, by + 4 * u - ry, bx + rx, by + 4 * u + ry], outline=(255, 230, 190, a), width=W_(3 * u))
        if k < 0.35:
            s.g.ellipse([bx - 60 * u, by - 40 * u, bx + 60 * u, by + 40 * u], fill=(255, 240, 200, 255))
        for j in range(8):
            ang2 = math.radians(200 + j * 20)
            r0, r1 = (30 + 80 * k) * u, (50 + 120 * k) * u
            d.line([(bx + r0 * math.cos(ang2), by + r0 * math.sin(ang2) * 0.6), (bx + r1 * math.cos(ang2), by + r1 * math.sin(ang2) * 0.6)],
                   fill=(255, 220, 140, a), width=W_(3 * u))
        f = f_num(int(22 * u))
        d.text((s.X(-0.75, s.Y(0.16)), s.Y(0.12)), "RAM -3", font=f, fill=P["hot"] + (a,))

def mer_miss(s, t):  # a box falls open: nothing inside
    u, d, P = s.u, s.d, s.P
    k = ease(min(1, t / 0.5))
    base = s.Y(0.9)
    w, h = 140 * u, 100 * u
    x0 = s.cx - w / 2
    d.rectangle([x0, base, x0 + w, base + 6 * u], fill=(50, 40, 30, 255))
    if k < 1:
        hh = h * (1 - k)
        d.rectangle([x0, base - hh, x0 + w, base], fill=(40, 30, 22, 255))
    for side in (-1, 1):  # side walls fall outward
        ang = k * 90
        hx = s.cx + side * w / 2
        L = h
        tx = hx + side * L * math.sin(math.radians(ang))
        ty = base - L * math.cos(math.radians(ang))
        d.polygon([(hx, base), (tx, ty), (tx - side * 4 * u, ty), (hx - side * 4 * u, base)], fill=P["card"] + (255,), outline=P["ink"] + (255,))
    fl = base - h * math.cos(math.radians(k * 90))  # front wall falls toward the viewer (shortens)
    d.polygon([(x0, base), (x0 + w, base), (x0 + w, fl), (x0, fl)], fill=(196, 136, 76, 255), outline=P["ink"] + (255,))
    if k >= 1:
        f = f_num(int(26 * u))
        d.text((s.cx - f.getlength("EMPTY") / 2, base - 70 * u), "EMPTY", font=f, fill=(240, 220, 180, int(120 + 100 * tri(t * 3))))
        for j in range(6):  # dust
            dx = (t - 0.5) * 220 * u * (1 if j % 2 else -1)
            d.ellipse([s.cx + dx * (0.3 + j * 0.12) - 5 * u, base - 8 * u - j * 3 * u, s.cx + dx * (0.3 + j * 0.12) + 5 * u, base - j * 3 * u], fill=(210, 190, 160, 110))


# ================================================================== SOLACE
def sol_attack(s, t):  # a syringe at an angle, liquid dripping out
    u, d, P = s.u, s.d, s.P
    ang = 160
    cx, cy = s.cx + 30 * u, s.Y(0.62)
    L, R = 150 * u, 20 * u
    body = rect_pts(cx - L / 2, cy - R, cx + L / 2, cy + R)
    push = 30 * u * tri(t)
    liquid = rect_pts(cx - L / 2 + 40 * u + push, cy - R + 4 * u, cx + L / 2 - 6 * u, cy + R - 4 * u)
    plunger = rect_pts(cx - L / 2 - 50 * u + push, cy - 5 * u, cx - L / 2 + 40 * u + push, cy + 5 * u)
    pad = rect_pts(cx - L / 2 - 56 * u + push, cy - R - 6 * u, cx - L / 2 - 46 * u + push, cy + R + 6 * u)
    head = rect_pts(cx - L / 2 + 34 * u + push, cy - R + 2 * u, cx - L / 2 + 42 * u + push, cy + R - 2 * u)
    needle = rect_pts(cx + L / 2, cy - 2.5 * u, cx + L / 2 + 70 * u, cy + 2.5 * u)
    for pts, col in ((plunger, (200, 230, 220)), (pad, (200, 230, 220)), (body, (200, 255, 235)), (liquid, P["a"]),
                     (head, (40, 60, 56)), (needle, (230, 240, 240))):
        pp = rot(pts, ang, cx, cy)
        a = 70 if col == (200, 255, 235) else 255
        s.d.polygon(pp, fill=col + (a,), outline=(230, 255, 245, 255) if a == 70 else P["ink"] + (255,))
    s.g.polygon(rot(liquid, ang, cx, cy), fill=P["a"] + (200,))
    for k in range(5):  # graduation ticks
        x = cx - L / 2 + 60 * u + k * 26 * u
        p = rot([(x, cy - R), (x, cy - R + 10 * u)], ang, cx, cy)
        d.line(p, fill=P["ink"] + (255,), width=W_(1.5 * u))
    tip = rot([(cx + L / 2 + 70 * u, cy)], ang, cx, cy)[0]
    for k in range(3):  # drops fall from the tip
        ph = (t + k / 3) % 1.0
        y = tip[1] + ph * (s.H - tip[1]) * 1.05
        r = 6 * u * (0.6 + 0.4 * ph)
        d.ellipse([tip[0] - r, y - r * 1.4, tip[0] + r, y + r], fill=P["a"] + (255,))
        s.g.ellipse([tip[0] - r, y - r, tip[0] + r, y + r], fill=P["a"] + (255,))
    d.ellipse([tip[0] - 16 * u, s.H - 10 * u, tip[0] + 16 * u, s.H + 6 * u], fill=P["a"] + (150,))


def ecg_y(x, beat_x, amp):
    dx = x - beat_x
    if -0.10 < dx < -0.06:
        return -0.12 * amp
    if -0.02 < dx < 0.0:
        return 0.25 * amp * (dx + 0.02) / 0.02
    if 0.0 <= dx < 0.03:
        return -1.0 * amp * (1 - abs(dx - 0.015) / 0.015)
    if 0.03 <= dx < 0.05:
        return 0.35 * amp
    if 0.12 < dx < 0.18:
        return -0.2 * amp * math.sin((dx - 0.12) / 0.06 * math.pi)
    return 0.0


def sol_crit(s, t):  # a heartbeat pulse runs across the whole screen
    u, d, P = s.u, s.d, s.P
    base = s.Y(0.66)
    amp = s.Y(0.52)
    head = t
    pts = []
    for i in range(300):
        x = i / 299
        y = 0.0
        for b in (0.25, 0.75):
            y += ecg_y(x, b, 1.0)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        age = (head - x1) % 1.0
        a = int(255 * max(0.12, 1 - age * 1.6))
        col = P["hot"] if abs(y0) > 0.6 else P["a"]
        d.line([(x0 * s.W, base + y0 * amp), (x1 * s.W, base + y1 * amp)], fill=col + (a,), width=W_(4 * u))
        if age < 0.15:
            s.g.line([(x0 * s.W, base + y0 * amp), (x1 * s.W, base + y1 * amp)], fill=col + (255,), width=W_(10 * u))
    hy = sum(ecg_y(head, b, 1.0) for b in (0.25, 0.75))
    hx = head * s.W
    d.ellipse([hx - 8 * u, base + hy * amp - 8 * u, hx + 8 * u, base + hy * amp + 8 * u], fill=(255, 255, 255, 255))
    s.g.ellipse([hx - 18 * u, base + hy * amp - 18 * u, hx + 18 * u, base + hy * amp + 18 * u], fill=P["a"] + (255,))
    f = f_num(int(18 * u))
    d.text((s.X(-0.8, s.Y(0.9)), s.Y(0.86)), "BPM %d" % (148 + int(40 * tri(t))), font=f, fill=P["hot"] + (255,))


def sol_defend(s, t):  # a beaker pours into a vial
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx + 120 * u, s.Y(0.16)
    beaker = [(bx - 40 * u, by - 40 * u), (bx + 40 * u, by - 40 * u), (bx + 34 * u, by + 50 * u), (bx - 34 * u, by + 50 * u)]
    tilt = -(40 + 10 * tri(t))
    bp = rot(beaker, tilt, bx, by)
    d.polygon(bp, fill=(200, 255, 235, 70), outline=P["glass"] + (255,))
    liq = rot([(bx - 36 * u, by + 5 * u), (bx + 36 * u, by + 5 * u), (bx + 34 * u, by + 48 * u), (bx - 34 * u, by + 48 * u)], tilt, bx, by)
    d.polygon(liq, fill=P["a"] + (220,))
    lip = rot([(bx - 40 * u, by - 40 * u)], tilt, bx, by)[0]
    vx, vy = s.cx - 55 * u, s.Y(0.58)
    vw, vh = 40 * u, 80 * u
    pts = []
    for k in range(20):  # pouring stream: arc from the lip to the vial mouth
        q = k / 19
        x = lip[0] + (vx - lip[0]) * q
        y = lip[1] + (vy - lip[1]) * q * q
        pts.append((x, y))
    wob = 1 + 0.25 * math.sin(t * 2 * math.pi * 3)
    s.g.line(pts, fill=P["a"] + (255,), width=W_(10 * u))
    d.line(pts, fill=P["a"] + (255,), width=W_(5 * u * wob))
    d.rounded_rectangle([vx - vw / 2, vy, vx + vw / 2, vy + vh], radius=W_(vw / 2), fill=(200, 255, 235, 60), outline=P["glass"] + (255,), width=W_(2.5 * u))
    lvl = vy + vh - (vh - 12 * u) * (0.15 + 0.8 * t)
    d.rounded_rectangle([vx - vw / 2 + 4 * u, lvl, vx + vw / 2 - 4 * u, vy + vh - 4 * u], radius=W_(vw / 2 - 4 * u), fill=P["a"] + (240,))
    d.rectangle([vx - vw / 2 - 4 * u, vy - 8 * u, vx + vw / 2 + 4 * u, vy + 2 * u], fill=(220, 230, 228, 255), outline=P["ink"] + (255,))
    for k in range(3):  # bubbles rising in the vial
        ph = (t * 2 + k / 3) % 1.0
        yy = vy + vh - 10 * u - ph * (vy + vh - lvl)
        d.ellipse([vx - 4 * u + k * 4 * u, yy - 3 * u, vx + 2 * u + k * 4 * u, yy + 3 * u], outline=(220, 255, 240, 200))


def sol_growth(s, t):  # GROWTH (heal): one cell divides into two
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.64)
    k = ease(t / 0.85) if t < 0.85 else 1.0
    sep = 70 * u * k
    r = 54 * u * (1 - 0.18 * k)
    mem = Image.new("L", s.im.size, 0)
    md = ImageDraw.Draw(mem)
    for sx in (-1, 1):
        md.ellipse([cx + sx * sep / 2 - r, cy - r, cx + sx * sep / 2 + r, cy + r], fill=255)
    if k < 0.75:  # waist bridge until it pinches off
        wst = r * (1 - k / 0.75) * 0.9
        md.rectangle([cx - sep / 2, cy - wst, cx + sep / 2, cy + wst], fill=255)
    memb = mem.filter(ImageFilter.GaussianBlur(3 * u)).point(lambda v: 255 if v > 128 else 0)
    edge = memb.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    fill = Image.new("RGBA", s.im.size, (40, 170, 110, 120))
    s.im.paste(fill, (0, 0), memb)
    line = Image.new("RGBA", s.im.size, P["a"] + (255,))
    s.im.paste(line, (0, 0), edge)
    s.gl.paste(Image.new("RGBA", s.im.size, P["a"] + (200,)), (0, 0), edge)
    d = ImageDraw.Draw(s.im)
    nsep = sep * 1.0 if k > 0.3 else 0
    for sx in ((-1, 1) if k > 0.3 else (0,)):
        nx = cx + sx * nsep / 2
        rn = 16 * u
        d.ellipse([nx - rn, cy - rn, nx + rn, cy + rn], fill=(20, 90, 60, 255), outline=P["a"] + (255,), width=W_(2 * u))
    for j in range(8):  # growth sparkles
        a = j * 45 + t * 90
        rr = (r + 20 * u) * (1 + 0.15 * tri(t * 2 + j / 8))
        x, y = cx + rr * 1.3 * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))
        d.line([(x - 5 * u, y), (x + 5 * u, y)], fill=(220, 255, 235, 220), width=W_(2 * u))
        d.line([(x, y - 5 * u), (x, y + 5 * u)], fill=(220, 255, 235, 220), width=W_(2 * u))


def sol_dose(s, t):  # a pill bottle tips over and pills spill out
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx - 60 * u, s.Y(0.26)
    tilt = 110 * ease(min(1, t / 0.35))
    body = rect_pts(bx - 30 * u, by - 46 * u, bx + 30 * u, by + 46 * u)
    cap = rect_pts(bx - 34 * u, by - 62 * u, bx + 34 * u, by - 46 * u)
    label = rect_pts(bx - 30 * u, by - 18 * u, bx + 30 * u, by + 22 * u)
    piv = (bx + 30 * u, by + 46 * u)
    for pts, col in ((body, (230, 160, 60)), (label, (240, 250, 246)), (cap, (250, 250, 250))):
        d.polygon(rot(pts, tilt, *piv), fill=col + (230,), outline=P["ink"] + (255,))
    lc = rot([(bx, by + 2 * u)], tilt, *piv)[0]
    d.text((lc[0] - 10 * u, lc[1] - 7 * u), "Rx", font=f_num(int(14 * u)), fill=P["hot"] + (255,))
    mouth = rot([(bx, by - 62 * u)], tilt, *piv)[0]
    if t > 0.3:
        rng = np.random.default_rng(3)
        for k in range(7):
            ph = min(1.0, (t - 0.3 - k * 0.05) / 0.5)
            if ph <= 0:
                continue
            vx = (40 + rng.random() * 90) * u
            x = mouth[0] + vx * ph
            y = mouth[1] + s.H * 0.9 * ph * ph
            y = min(y, s.H - 12 * u)
            a = rng.random() * 180 + ph * 200
            cp = rot(rect_pts(x - 12 * u, y - 5 * u, x + 12 * u, y + 5 * u), a, x, y)
            d.polygon(cp, fill=(P["hot"] if k % 2 else (250, 250, 250)) + (255,), outline=P["ink"] + (255,))


def sol_miss(s, t):  # flatline with a bright dot travelling along it
    u, d, P = s.u, s.d, s.P
    y = s.Y(0.68)
    d.line([(0, y), (s.W, y)], fill=P["a"] + (150,), width=W_(3 * u))
    x = t * s.W
    for k in range(12):
        xx = x - k * 9 * u
        d.ellipse([xx - (7 - k * 0.5) * u, y - (7 - k * 0.5) * u, xx + (7 - k * 0.5) * u, y + (7 - k * 0.5) * u], fill=P["a"] + (int(255 * (1 - k / 12)),))
    s.g.ellipse([x - 22 * u, y - 22 * u, x + 22 * u, y + 22 * u], fill=(220, 255, 235, 255))
    d.ellipse([x - 7 * u, y - 7 * u, x + 7 * u, y + 7 * u], fill=(255, 255, 255, 255))
    f = f_mono(int(14 * u))
    d.text((s.X(-0.7, s.Y(0.85)), s.Y(0.80)), "NO PULSE", font=f, fill=P["paper"] + (int(110 + 120 * tri(t * 2)),))


def sol_shield(s, t):  # a membrane bubble inflates round a cell
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.62)
    d.ellipse([cx - 26 * u, cy - 26 * u, cx + 26 * u, cy + 26 * u], fill=(40, 160, 110, 200), outline=P["a"] + (255,), width=W_(2 * u))
    for k in range(4):
        ph = (t + k / 4) % 1.0
        r = (40 + ph * 120) * u
        a = int(230 * (1 - ph))
        d.ellipse([cx - r * 1.3, cy - r, cx + r * 1.3, cy + r], outline=P["glass"] + (a,), width=W_(3 * u))


# ================================================================== HALCYON
def hal_attack(s, t):  # handcuffs close on a wrist
    u, d, P = s.u, s.d, s.P
    wx, wy = s.cx - 10 * u, s.Y(0.72)
    arm = rot(rect_pts(wx - 160 * u, wy - 24 * u, wx + 10 * u, wy + 24 * u), -20, wx, wy)
    d.polygon(arm, fill=(176, 130, 110, 255), outline=P["ink"] + (255,))
    hand = rot([(wx + 10 * u, wy - 26 * u), (wx + 60 * u, wy - 30 * u), (wx + 72 * u, wy), (wx + 60 * u, wy + 28 * u), (wx + 10 * u, wy + 26 * u)], -20, wx, wy)
    d.polygon(hand, fill=(186, 140, 120, 255), outline=P["ink"] + (255,))
    k = ease(min(1, t / 0.55))
    cxw, cyw = rot([(wx - 6 * u, wy)], -20, wx, wy)[0]
    R = 34 * u
    sweep = 200 + 160 * k
    d.arc([cxw - R, cyw - R, cxw + R, cyw + R], -90 - sweep / 2 + 90, -90 + sweep / 2 + 90, fill=P["steel"] + (255,), width=W_(10 * u))
    d.arc([cxw - R, cyw - R, cxw + R, cyw + R], -90 - sweep / 2 + 90, -90 + sweep / 2 + 90, fill=P["ink"] + (255,), width=W_(2 * u))
    if 0.5 < t < 0.65:
        for a in range(0, 360, 45):
            x0, y0 = cxw + (R + 10 * u) * math.cos(math.radians(a)), cyw + (R + 10 * u) * math.sin(math.radians(a))
            d.line([(x0, y0), (x0 + 12 * u * math.cos(math.radians(a)), y0 + 12 * u * math.sin(math.radians(a)))], fill=P["gold"] + (255,), width=W_(3 * u))
    chx, chy = cxw + R + 2 * u, cyw - 10 * u
    for k2 in range(4):  # chain to the open second cuff
        x = chx + k2 * 14 * u
        y = chy - k2 * 8 * u
        d.ellipse([x - 6 * u, y - 4 * u, x + 6 * u, y + 4 * u], outline=P["steel"] + (255,), width=W_(3 * u))
    ox, oy = chx + 80 * u, chy - 50 * u
    d.arc([ox - R, oy - R, ox + R, oy + R], 20, 250, fill=P["steel"] + (255,), width=W_(10 * u))


def hal_crit(s, t):  # a jail door slams shut
    u, d, P = s.u, s.d, s.P
    y0, y1 = s.Y(0.02), s.Y(0.98)
    frame_x = s.cx + 20 * u
    k = ease(min(1, t / 0.5))
    shake = (math.sin(t * 80) * 4 * u * max(0, 1 - (t - 0.5) / 0.15)) if t > 0.5 else 0
    dx = -170 * u * (1 - k) + shake
    for xb in np.arange(frame_x, s.W, 22 * u):  # fixed cell bars on the right
        d.rectangle([xb, y0, xb + 7 * u, y1], fill=P["steel"] + (230,), outline=P["ink"] + (255,))
    door_x0 = frame_x - 160 * u + dx
    for xb in np.arange(door_x0, door_x0 + 160 * u, 22 * u):
        d.rectangle([xb, y0, xb + 8 * u, y1], fill=(230, 232, 245, 255), outline=P["ink"] + (255,))
    for yy in (s.Y(0.18), s.Y(0.82)):
        d.rectangle([door_x0 - 4 * u, yy, door_x0 + 164 * u, yy + 12 * u], fill=(200, 204, 225, 255), outline=P["ink"] + (255,))
    d.rectangle([door_x0 + 130 * u, s.Y(0.5) - 14 * u, door_x0 + 158 * u, s.Y(0.5) + 14 * u], fill=P["gold"] + (255,), outline=P["ink"] + (255,))
    if 0.5 < t < 0.75:
        f = f_num(int(30 * u))
        d.text((frame_x + 10 * u, s.Y(0.62)), "CLANG", font=f, fill=P["hot"] + (255,))
        for j in range(4):
            yy = s.Y(0.2 + j * 0.2)
            d.line([(frame_x - 6 * u, yy), (frame_x - 30 * u, yy - 10 * u)], fill=(255, 255, 255, 220), width=W_(3 * u))


def hal_shield(s, t):  # a rock bounces off a riot shield
    u, d, P = s.u, s.d, s.P
    sx0, sx1 = s.cx + 40 * u, s.cx + 110 * u
    d.rounded_rectangle([sx0, s.Y(0.08), sx1, s.Y(0.94)], radius=W_(20 * u), fill=(190, 210, 255, 90), outline=P["steel"] + (255,), width=W_(4 * u))
    d.rectangle([sx0 + 6 * u, s.Y(0.30), sx1 - 6 * u, s.Y(0.38)], fill=P["ink"] + (230,))
    f = f_num(int(13 * u))
    d.text((sx0 + 9 * u, s.Y(0.305)), "POLICE", font=f, fill=(255, 255, 255, 255))
    hitx, hity = sx0 - 8 * u, s.Y(0.55)
    if t < 0.5:  # thrown in from the left
        q = t / 0.5
        x = s.X(-0.95, s.Y(0.2)) + (hitx - s.X(-0.95, s.Y(0.2))) * q
        y = s.Y(0.2) + (hity - s.Y(0.2)) * q - 60 * u * math.sin(math.pi * q)
    else:  # bounces back up and away
        q = (t - 0.5) / 0.5
        x = hitx - 160 * u * q
        y = hity - 120 * u * q + 260 * u * q * q
    rp = [(x + 13 * u * math.cos(math.radians(a)) * (1 + 0.2 * (a % 3)), y + 11 * u * math.sin(math.radians(a))) for a in range(0, 360, 50)]
    d.polygon(rot(rp, t * 600, x, y), fill=(130, 120, 110, 255), outline=P["ink"] + (255,))
    if 0.47 < t < 0.62:
        for a in range(120, 250, 26):
            d.line([(hitx, hity), (hitx + 26 * u * math.cos(math.radians(a)), hity + 26 * u * math.sin(math.radians(a)))], fill=P["gold"] + (255,), width=W_(3 * u))


def hal_defend(s, t):  # police barricades slide together
    u, d, P = s.u, s.d, s.P
    k = ease(min(1, t / 0.5))
    y = s.Y(0.66)
    for side in (-1, 1):
        x_in = s.cx + side * (6 * u + 140 * u * (1 - k))
        x_out = x_in + side * 150 * u
        xa, xb = min(x_in, x_out), max(x_in, x_out)
        for yy in (y, y + 28 * u):
            d.rectangle([xa, yy, xb, yy + 16 * u], fill=(250, 250, 250, 255), outline=P["ink"] + (255,))
            for xs in np.arange(xa, xb, 18 * u):
                d.polygon([(xs, yy), (xs + 9 * u, yy), (xs + 18 * u, yy + 16 * u), (xs + 9 * u, yy + 16 * u)], fill=P["blue"] + (255,))
        for xl in (xa + 12 * u, xb - 12 * u):
            d.line([(xl, y), (xl - 14 * u, s.H)], fill=(60, 60, 70, 255), width=W_(5 * u))
            d.line([(xl, y), (xl + 14 * u, s.H)], fill=(60, 60, 70, 255), width=W_(5 * u))
    f = f_mono(int(12 * u))
    d.text((s.X(-0.7, s.Y(0.14)), s.Y(0.10)), "POLICE LINE  DO NOT CROSS", font=f, fill=P["gold"] + (int(140 + 110 * tri(t * 2)),))


def hal_heal(s, t):  # an ambulance drives by
    u, d, P = s.u, s.d, s.P
    x = s.cx - 230 * u + 460 * u * t
    y = s.Y(0.84)
    d.rectangle([x - 110 * u, y - 70 * u, x + 20 * u, y], fill=(246, 246, 250, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.polygon([(x + 20 * u, y - 52 * u), (x + 56 * u, y - 52 * u), (x + 76 * u, y - 24 * u), (x + 76 * u, y), (x + 20 * u, y)], fill=(246, 246, 250, 255), outline=P["ink"] + (255,))
    d.polygon([(x + 28 * u, y - 46 * u), (x + 52 * u, y - 46 * u), (x + 66 * u, y - 26 * u), (x + 28 * u, y - 26 * u)], fill=(90, 140, 200, 255))
    d.rectangle([x - 110 * u, y - 30 * u, x + 76 * u, y - 22 * u], fill=P["hot"] + (255,))
    d.rectangle([x - 64 * u, y - 62 * u, x - 44 * u, y - 36 * u], fill=P["hot"] + (255,))
    d.rectangle([x - 68 * u, y - 58 * u, x - 40 * u, y - 40 * u], fill=P["hot"] + (255,))
    for wx in (x - 80 * u, x + 44 * u):
        d.ellipse([wx - 14 * u, y - 10 * u, wx + 14 * u, y + 18 * u], fill=(30, 30, 36, 255))
    on = int(t * 12) % 2
    c1, c2 = (P["hot"], P["blue"]) if on else (P["blue"], P["hot"])
    d.rectangle([x - 30 * u, y - 80 * u, x - 14 * u, y - 70 * u], fill=c1 + (255,))
    d.rectangle([x - 12 * u, y - 80 * u, x + 4 * u, y - 70 * u], fill=c2 + (255,))
    s.g.ellipse([x - 50 * u, y - 100 * u, x + 20 * u, y - 50 * u], fill=c1 + (255,))
    for k in range(3):
        d.line([(x - (130 + k * 20) * u, y - (20 + k * 18) * u), (x - (118 + k * 20) * u - 30 * u, y - (20 + k * 18) * u)], fill=(255, 255, 255, 150), width=W_(3 * u))


def hal_citation(s, t):  # paper gets stamped FINE
    u, d, P = s.u, s.d, s.P
    px0, px1 = s.cx - 90 * u, s.cx + 90 * u
    py0, py1 = s.Y(0.46), s.Y(1.02)
    d.rectangle([px0, py0, px1, py1], fill=(186, 186, 182, 255), outline=P["ink"] + (255,))
    for k in range(6):
        y = py0 + 14 * u + k * 13 * u
        d.line([(px0 + 10 * u, y), (px1 - (10 + (k * 23) % 50) * u, y)], fill=(120, 120, 140, 255), width=W_(2 * u))
    stamp_y_end = py0 + 40 * u
    if t < 0.45:
        k = ease(t / 0.45)
        sy = s.Y(0.0) + (stamp_y_end - 60 * u - s.Y(0.0)) * k
    elif t < 0.55:
        sy = stamp_y_end - 60 * u
    else:
        sy = stamp_y_end - 60 * u - 120 * u * ease((t - 0.55) / 0.45)
    if t >= 0.45:
        f = f_num(int(46 * u))
        st = Image.new("RGBA", (int(f.getlength("FINE") + 24 * u), int(62 * u)), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([0, 0, st.width - 1, st.height - 1], radius=W_(6 * u), outline=P["hot"] + (255,), width=W_(5 * u))
        sd.text((12 * u, 2 * u), "FINE", font=f, fill=P["hot"] + (255,))
        st = st.rotate(10, expand=True, resample=Image.BICUBIC)
        s.im.alpha_composite(st, (int(s.cx - st.width / 2), int(stamp_y_end - st.height / 2 + 8 * u)))
    d.rectangle([s.cx - 40 * u, sy + 40 * u, s.cx + 40 * u, sy + 58 * u], fill=(120, 40, 40, 255), outline=P["ink"] + (255,))
    d.rectangle([s.cx - 10 * u, sy - 20 * u, s.cx + 10 * u, sy + 40 * u], fill=(90, 70, 50, 255), outline=P["ink"] + (255,))
    d.ellipse([s.cx - 24 * u, sy - 46 * u, s.cx + 24 * u, sy - 10 * u], fill=(110, 84, 60, 255), outline=P["ink"] + (255,))


def hal_miss_a(s, t):  # MISS option A: CLOSED sign swinging on its chain
    u, d, P = s.u, s.d, s.P
    ax, ay = s.cx, s.Y(0.04)
    ang = 14 * math.sin(2 * math.pi * t)
    w, h = 170 * u, 70 * u
    top = ay + 70 * u
    board = rect_pts(ax - w / 2, top, ax + w / 2, top + h)
    for sx in (-1, 1):
        p = rot([(ax + sx * w * 0.35, top)], ang, ax, ay)[0]
        d.line([(ax, ay), p], fill=P["steel"] + (255,), width=W_(3 * u))
    d.polygon(rot(board, ang, ax, ay), fill=(240, 236, 220, 255), outline=P["ink"] + (255,))
    st = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(st).text((w / 2, h / 2), "CLOSED", font=f_num(int(44 * u)), fill=P["hot"] + (255,), anchor="mm")
    st = st.rotate(-ang, expand=True, resample=Image.BICUBIC)
    c = rot([(ax, top + h / 2)], ang, ax, ay)[0]
    s.im.alpha_composite(st, (int(c[0] - st.width / 2), int(c[1] - st.height / 2)))
    d.text((s.X(-0.5, s.Y(0.85)), s.Y(0.84)), "OFFICE HOURS 09:00-09:05", font=f_mono(int(10 * u)), fill=P["paper"] + (200,))


def hal_miss_b(s, t):  # MISS option B: NO RECORD - an empty file folder flops open
    u, d, P = s.u, s.d, s.P
    cx, by = s.cx, s.Y(0.94)
    w, h = 190 * u, 120 * u
    d.polygon([(cx - w / 2, by), (cx + w / 2, by), (cx + w / 2, by - h), (cx - w / 2 + 50 * u, by - h), (cx - w / 2 + 40 * u, by - h - 14 * u),
               (cx - w / 2, by - h - 14 * u)], fill=(150, 126, 76, 255), outline=P["ink"] + (255,))
    k = ease(tri(t))
    fh = h * (1 - k)
    d.polygon([(cx - w / 2, by), (cx + w / 2, by), (cx + w / 2 + 20 * u * k, by - fh), (cx - w / 2 - 20 * u * k, by - fh)], fill=(176, 150, 96, 255), outline=P["ink"] + (255,))
    if k > 0.5:
        d.rectangle([cx - 70 * u, by - h + 8 * u, cx + 70 * u, by - h + 70 * u], fill=(250, 250, 246, 255), outline=(150, 150, 160, 255))
        d.text((cx, by - h + 40 * u), "NO RECORD", font=f_num(int(22 * u)), fill=(150, 150, 170, 255), anchor="mm")


# ================================================================== ORBITAL
def planet(s, cx, cy, r):
    P = s.P
    s.g.ellipse([cx - r * 1.08, cy - r * 1.08, cx + r * 1.08, cy + r * 1.08], fill=P["a"] + (180,))
    s.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P["planet"] + (255,), outline=(190, 220, 255, 255), width=W_(2 * s.u))
    for k in range(4):
        y = cy - r * 0.6 + k * r * 0.3
        hw = math.sqrt(max(0, r * r - (y - cy) ** 2))
        s.d.line([(cx - hw * 0.9, y), (cx + hw * 0.9, y + r * 0.05)], fill=(90, 150, 230, 255), width=W_(4 * s.u))


def meteor(s, x, y, r, ang, tail=4.0, col=(255, 200, 120)):
    u, d = s.u, s.d
    tx, ty = x - math.cos(math.radians(ang)) * r * tail * 3, y - math.sin(math.radians(ang)) * r * tail * 3
    s.g.line([(tx, ty), (x, y)], fill=col + (255,), width=W_(r * 1.4))
    d.line([(tx, ty), (x, y)], fill=col + (160,), width=W_(r * 0.9))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 120, 100, 255), outline=(255, 220, 160, 255), width=W_(1.5 * u))


def impact(s, x, y, k, r):
    a = int(255 * (1 - k))
    rr = r * (0.4 + 1.6 * k)
    s.g.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 230, 160, a))
    s.d.ellipse([x - rr * 0.5, y - rr * 0.5, x + rr * 0.5, y + rr * 0.5], fill=(255, 250, 220, a))


def orb_attack(s, t):  # one small meteor hits the planet
    u = s.u
    pcx, pcy, pr = s.cx + 40 * u, s.Y(1.05), 120 * u
    planet(s, pcx, pcy, pr)
    hx, hy = pcx - 50 * u, pcy - math.sqrt(pr * pr - (50 * u) ** 2)
    sx, sy = s.X(-0.9, s.Y(0.06)), s.Y(0.06)
    if t < 0.65:
        q = t / 0.65
        meteor(s, sx + (hx - sx) * q, sy + (hy - sy) * q, 9 * u, math.degrees(math.atan2(hy - sy, hx - sx)))
    else:
        impact(s, hx, hy, (t - 0.65) / 0.35, 40 * u)


def orb_crit(s, t):  # a large meteor and several small ones hit the planet
    u = s.u
    pcx, pcy, pr = s.cx, s.Y(1.10), 140 * u
    planet(s, pcx, pcy, pr)
    rocks = [(-0.85, 0.02, -60, 22, 0.0), (-0.5, 0.0, -10, 8, 0.12), (0.2, 0.0, 40, 7, 0.2), (0.7, 0.04, 70, 9, 0.06), (-0.2, 0.05, 15, 6, 0.3)]
    for (fx, fy, hx_off, r, delay) in rocks:
        sx, sy = s.X(fx, s.Y(fy)), s.Y(fy)
        hx = pcx + hx_off * u
        hy = pcy - math.sqrt(max(0, pr * pr - (hx - pcx) ** 2))
        q = (t - delay) / 0.6
        if 0 <= q < 1:
            meteor(s, sx + (hx - sx) * q, sy + (hy - sy) * q, r * u, math.degrees(math.atan2(hy - sy, hx - sx)))
        elif 1 <= q < 1.5:
            impact(s, hx, hy, (q - 1) / 0.5, (60 if r > 15 else 26) * u)


def orb_defend(s, t):  # a laser destroys a meteor
    u, d, P = s.u, s.d, s.P
    satx, saty = s.X(-0.7, s.Y(0.7)), s.Y(0.7)
    d.rectangle([satx - 10 * u, saty - 10 * u, satx + 10 * u, saty + 10 * u], fill=(230, 235, 245, 255), outline=P["ink"] + (255,))
    for sx in (-1, 1):
        xa, xb = sorted((satx + sx * 12 * u, satx + sx * 42 * u))
        d.rectangle([xa, saty - 6 * u, xb, saty + 6 * u], fill=(60, 110, 230, 255), outline=(200, 210, 230, 255))
    mx, my = s.X(0.55, s.Y(0.18)), s.Y(0.18) + 40 * u * t
    if t < 0.45:
        meteor(s, mx, my, 18 * u, 160)
    if 0.35 < t < 0.55:
        s.g.line([(satx, saty), (mx, my)], fill=(255, 80, 120, 255), width=W_(12 * u))
        d.line([(satx, saty), (mx, my)], fill=(255, 220, 230, 255), width=W_(3 * u))
    if t >= 0.45:
        k = (t - 0.45) / 0.55
        impact(s, mx, my, k, 50 * u)
        rng = np.random.default_rng(8)
        for j in range(7):
            a = rng.random() * 360
            dd = k * (40 + rng.random() * 70) * u
            x, y = mx + dd * math.cos(math.radians(a)), my + dd * math.sin(math.radians(a))
            r = (3 + rng.random() * 5) * u
            d.polygon([(x - r, y), (x, y - r), (x + r * 0.8, y + r * 0.4)], fill=(150, 120, 100, 255), outline=(255, 210, 150, 255))


def orb_evade(s, t):  # a basic spaceship fires its engines and leaves the screen
    u, d, P = s.u, s.d, s.P
    q = ease(t) if t < 0.95 else 1
    x = s.cx - 120 * u + (s.W * 0.75) * (q ** 1.6)
    y = s.Y(0.72) - 80 * u * q
    hull = [(x + 50 * u, y), (x - 20 * u, y - 18 * u), (x - 34 * u, y - 18 * u), (x - 34 * u, y + 18 * u), (x - 20 * u, y + 18 * u)]
    hull = rot(hull, -12, x, y)
    fl = 1 + 0.3 * math.sin(t * 2 * math.pi * 8)
    flame = rot([(x - 34 * u, y - 10 * u), (x - (34 + 50 * fl * (0.4 + q)) * u, y), (x - 34 * u, y + 10 * u)], -12, x, y)
    s.g.polygon(flame, fill=(255, 160, 60, 255))
    d.polygon(flame, fill=(255, 220, 140, 255))
    d.polygon(hull, fill=(230, 236, 250, 255), outline=P["ink"] + (255,))
    for f in (-1, 1):
        fin = rot([(x - 20 * u, y + f * 18 * u), (x - 36 * u, y + f * 34 * u), (x - 40 * u, y + f * 18 * u)], -12, x, y)
        d.polygon(fin, fill=P["hot"] + (255,), outline=P["ink"] + (255,))
    win = rot([(x + 14 * u, y)], -12, x, y)[0]
    d.ellipse([win[0] - 6 * u, win[1] - 6 * u, win[0] + 6 * u, win[1] + 6 * u], fill=(90, 160, 255, 255))


def orb_flare(s, t):  # solar flare (kept): sun, rotating corona, an erupting loop
    u, d, P = s.u, s.d, s.P
    cx, cy, r = s.cx, s.Y(0.86), 60 * u
    s.g.ellipse([cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2], fill=(255, 200, 80, 255))
    for k in range(18):
        a = math.radians(k * 20 + t * 40)
        L = r * (1.4 + 0.35 * ((k % 2) + tri(t * 2 + k / 18)))
        d.line([(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=P["gold"] + (255,), width=W_(4 * u))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 200, 255))
    h = r * (1.0 + 1.8 * tri(t))
    d.arc([cx - r * 0.9, cy - r - h, cx + r * 0.9, cy - r + h * 0.4], 180, 360, fill=(255, 150, 60, 255), width=W_(6 * u))
    s.g.arc([cx - r * 0.9, cy - r - h, cx + r * 0.9, cy - r + h * 0.4], 180, 360, fill=(255, 120, 40, 255), width=W_(14 * u))


def orb_miss(s, t):  # an astronaut drifts away into space
    u, d, P = s.u, s.d, s.P
    q = t
    sc = 1.0 - 0.6 * q
    x = s.cx - 40 * u + 90 * u * q
    y = s.Y(0.66) - s.Y(0.5) * q
    a = 360 * q * 0.6
    def R(px, py):
        return rot([(x + px * sc * u, y + py * sc * u)], a, x, y)[0]
    body = [R(-14, -6), R(14, -6), R(14, 26), R(-14, 26)]
    d.polygon([R(-20, -2), R(-14, -2), R(-14, 22), R(-20, 22)], fill=(200, 200, 210, 255))
    d.polygon(body, fill=(240, 240, 246, 255), outline=P["ink"] + (255,))
    for lx in (-8, 8):
        d.line([R(lx, 26), R(lx * 1.4, 46)], fill=(240, 240, 246, 255), width=W_(9 * u * sc))
    for ax in (-1, 1):
        d.line([R(ax * 14, 0), R(ax * 30, 16)], fill=(240, 240, 246, 255), width=W_(8 * u * sc))
    hc = R(0, -20)
    hr = 15 * u * sc
    d.ellipse([hc[0] - hr, hc[1] - hr, hc[0] + hr, hc[1] + hr], fill=(240, 240, 246, 255), outline=P["ink"] + (255,))
    d.ellipse([hc[0] - hr * 0.65, hc[1] - hr * 0.5, hc[0] + hr * 0.65, hc[1] + hr * 0.5], fill=(255, 200, 100, 255))
    tet = R(-14, 20)
    d.line([tet, (s.X(-0.6, s.Y(0.95)), s.Y(0.95))], fill=(200, 200, 210, 140), width=W_(2 * u))
    d.text((s.X(-0.5, s.Y(0.92)), s.Y(0.88)), "TETHER LOST", font=f_mono(int(10 * u)), fill=P["paper"] + (int(100 + 140 * tri(t * 3)),))


def orb_shield(s, t):  # an energy dome pulses over the planet
    u, d, P = s.u, s.d, s.P
    pcx, pcy, pr = s.cx, s.Y(1.10), 120 * u
    planet(s, pcx, pcy, pr)
    r = pr + 46 * u
    a = int(120 + 120 * tri(t * 2))
    s.g.ellipse([pcx - r, pcy - r, pcx + r, pcy + r], outline=P["a"] + (a,), width=W_(14 * u))
    d.ellipse([pcx - r, pcy - r, pcx + r, pcy + r], outline=(220, 240, 255, a), width=W_(3 * u))


def orb_heal(s, t):  # a satellite unfolds its panels
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.66)
    k = ease(tri(t))
    d.rectangle([cx - 16 * u, cy - 16 * u, cx + 16 * u, cy + 16 * u], fill=(236, 236, 246, 255), outline=P["ink"] + (255,))
    for sx in (-1, 1):
        n = 1 + int(k * 3.99)
        for j in range(n):
            x0 = cx + sx * (20 + j * 30) * u
            d.rectangle([min(x0, x0 + sx * 28 * u), cy - 14 * u, max(x0, x0 + sx * 28 * u), cy + 14 * u], fill=(60, 110, 230, 255), outline=(200, 210, 230, 255))
    d.line([(cx, cy - 16 * u), (cx, cy - 40 * u)], fill=(220, 220, 230, 255), width=W_(2 * u))


# ================================================================== registry
SCENES = {
    "meridian": {"ATTACK": mer_attack, "CRITICAL": mer_crit, "DEFEND": mer_defend, "SHIELD": mer_shield,
                 "SPECIAL": mer_judgement, "MISS": mer_miss},
    "solace": {"ATTACK": sol_attack, "CRITICAL": sol_crit, "DEFEND": sol_defend, "HEAL": sol_growth,
               "SPECIAL": sol_dose, "MISS": sol_miss, "SHIELD": sol_shield},
    "halcyon": {"ATTACK": hal_attack, "CRITICAL": hal_crit, "SHIELD": hal_shield, "DEFEND": hal_defend,
                "HEAL": hal_heal, "SPECIAL": hal_citation, "MISS": hal_miss_a, "MISS_B": hal_miss_b},
    "orbital": {"ATTACK": orb_attack, "CRITICAL": orb_crit, "DEFEND": orb_defend, "EVADE": orb_evade,
                "SPECIAL": orb_flare, "MISS": orb_miss, "SHIELD": orb_shield, "HEAL": orb_heal},
}
FALLBACK = {"EVADE": "ATTACK", "HEAL": "DEFEND", "SHIELD": "DEFEND", "AFFLICT": "SPECIAL", "DEPLOY": "ATTACK"}


def scene(ctx, corp, kind, t):
    tab = SCENES[corp]
    fn = tab.get(kind) or tab.get(FALLBACK.get(kind, "ATTACK"))
    s = Sc(ctx, corp)
    fn(s, t % 1.0)
    return s.done()
