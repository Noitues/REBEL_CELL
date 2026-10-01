"""Wheel assembly: slices -> wheel, corp bezels, hub, pointer, HP arc, background."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import slicelib as sl
from slicelib import R_IN, R_OUT, hexrgb, smoothstep, frac
import themes as th

WC = 1040
C = WC / 2
LIGHT_TH = math.atan2(-0.42, 0.91)    # light direction angle (clockwise from up)


class World:
    def __init__(self, size=WC):
        self.size = size
        c = size / 2
        xs = np.arange(size, dtype=np.float32) + 0.5 - c
        X, Y = np.meshgrid(xs, -xs)
        self.X, self.Y = X, Y
        self.r = np.hypot(X, Y)
        self.th = np.arctan2(X, Y)
        self.c = c

    def px(self, X, Y):
        return (X + self.c, self.c - Y)

    def polar(self, r, deg):
        a = math.radians(deg)
        return self.px(r * math.sin(a), r * math.cos(a))

    def L(self):
        img = Image.new("L", (self.size, self.size), 0)
        return img, ImageDraw.Draw(img)


def band(w, r0, r1):
    return np.clip(np.minimum(w.r - r0, r1 - w.r) + 0.5, 0, 1)


def lit(w, amt=0.45):
    return 1 - amt + amt * (0.5 + 0.5 * np.cos(w.th - LIGHT_TH)) * 2 * 0.75


def ring_bevel(w, r0, r1, k=0.55, bw=4.0):
    """Lighten the edge facing the light, darken the other."""
    d_in = w.r - r0
    d_out = r1 - w.r
    ry = np.cos(w.th - LIGHT_TH)            # radial . light
    s_in = np.clip(1 - d_in / bw, 0, 1) * (-ry)
    s_out = np.clip(1 - d_out / bw, 0, 1) * ry
    return 1 + k * (s_in + s_out)


def angular_blocks(w, n, frac_on, offset_deg=0.0):
    a = frac((np.degrees(w.th) - offset_deg) / (360.0 / n) + 0.5)
    half = frac_on / 2
    # AA in pixels along the arc
    dpx = (half - np.abs(a - 0.5)) * (2 * math.pi * w.r / n)
    return np.clip(dpx + 0.5, 0, 1)


def L2a(img):
    return np.asarray(img, np.float32) / 255.0


class Layer:
    def __init__(self, w):
        self.rgb = np.zeros((w.size, w.size, 3), np.float32)
        self.a = np.zeros((w.size, w.size), np.float32)
        self.emis = np.zeros((w.size, w.size, 3), np.float32)

    def paint(self, mask, col, alpha=1.0):
        m = np.clip(mask * alpha, 0, 1)
        col = np.asarray(col, np.float32)
        if col.ndim == 1:
            col = col[None, None, :]
        self.rgb = self.rgb * (1 - m[..., None]) + col * m[..., None]
        self.a = np.maximum(self.a, m) if alpha >= 1 else 1 - (1 - self.a) * (1 - m)

    def glow(self, mask, col, k=1.0):
        self.emis += np.asarray(col, np.float32) * (mask * k)[..., None]

    def image(self):
        return sl.rgba_from(self.rgb, self.a)


# ----------------------------------------------------------------------------- bezels
def bezel(w, theme, boss=False, seed=3):
    L = Layer(w)
    col = hexrgb(th.THEMES[theme]["col"])
    # dark well behind the tiles
    L.paint(np.clip(R_OUT + 5 - w.r, 0, 1), (0.025, 0.02, 0.035))
    r0, r1 = R_OUT + 5, R_OUT + 46
    deg = np.degrees(w.th)
    if theme == "meridian":
        base = np.array([0.36, 0.17, 0.05], np.float32)
        m = band(w, r0, r1)
        shade = lit(w) * ring_bevel(w, r0, r1)
        L.paint(m, base * shade[..., None])
        hz = band(w, R_OUT + 14, R_OUT + 36)
        s = w.r * w.th + w.r
        stripe = (frac(s / 16.0) < 0.5).astype(np.float32)
        hzcol = np.where(stripe[..., None] > 0, np.array([1.0, 0.55, 0.10]), np.array([0.06, 0.04, 0.03]))
        L.paint(hz, hzcol * lit(w, 0.3)[..., None])
        teeth = band(w, r1 - 1, R_OUT + 60) * angular_blocks(w, 30, 0.55, 6)
        L.paint(teeth, np.array([0.85, 0.42, 0.08]) * (lit(w) * ring_bevel(w, r1 - 1, R_OUT + 60, 0.7))[..., None])
        L.glow(np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2), col, 0.9)
        L.glow(teeth * 0.15, col)
    elif theme == "solace":
        m = band(w, r0, r1)
        shade = lit(w, 0.35) * ring_bevel(w, r0, r1, 0.35)
        L.paint(m, np.array([0.74, 0.82, 0.80]) * shade[..., None])
        spec = np.exp(-((w.r - (R_OUT + 18)) / 3.0) ** 2) * np.clip(np.cos(w.th - LIGHT_TH), 0, 1) ** 3
        L.rgb += (spec * m * 0.25)[..., None]
        cap = band(w, R_OUT + 24, R_OUT + 36) * angular_blocks(w, 30, 0.30, 6)
        L.paint(cap, np.array([0.20, 0.75, 0.50]))
        L.glow(cap * 0.6, col)
        L.paint(band(w, R_OUT + 46, R_OUT + 50), np.array([0.35, 0.9, 0.62]), 0.7)
        L.glow(np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2), col, 0.9)
        L.glow(band(w, R_OUT + 46, R_OUT + 50), col, 0.5)
    elif theme == "halcyon":
        rr1 = R_OUT + (66 if boss else 46)
        m = band(w, r0, rr1)
        L.paint(m, np.array([0.17, 0.15, 0.36]) * (lit(w) * ring_bevel(w, r0, rr1))[..., None])
        tiers = [(R_OUT + 16, R_OUT + 42)] if not boss else [(R_OUT + 14, R_OUT + 36), (R_OUT + 42, R_OUT + 62)]
        for i, (a0, a1) in enumerate(tiers):
            cols = band(w, a0, a1) * angular_blocks(w, 60 if i == 0 else 90, 0.55)
            L.paint(cols, np.array([0.48, 0.44, 0.85]) * (lit(w) * ring_bevel(w, a0, a1, 0.6))[..., None])
        gold = np.array([1.0, 0.80, 0.42], np.float32)
        trim = gold if boss else np.array([0.75, 0.70, 1.0])
        for rr in ([R_OUT + 12, R_OUT + 39, R_OUT + 64] if boss else [R_OUT + 12, R_OUT + 44]):
            tm = np.exp(-((w.r - rr) / 1.0) ** 2)
            L.paint(tm, trim, 0.9)
            L.glow(tm, trim, 0.3)
        if boss:
            cren = band(w, rr1 - 1, R_OUT + 82) * angular_blocks(w, 45, 0.5)
            L.paint(cren, np.array([0.30, 0.26, 0.58]) * (lit(w) * ring_bevel(w, rr1, R_OUT + 82, 0.8))[..., None])
            halo = np.exp(-((w.r - (R_OUT + 100)) / 2.2) ** 2)
            L.paint(halo, np.array([0.95, 0.88, 1.0]), 0.9)
            L.glow(halo, gold * 0.6 + col * 0.6, 1.2)
            # halo struts
            strut = band(w, R_OUT + 82, R_OUT + 99) * angular_blocks(w, 6, 0.012, 30)
            L.paint(strut, np.array([0.6, 0.55, 0.9]))
        else:
            halo = np.exp(-((w.r - (R_OUT + 60)) / 1.6) ** 2)
            L.paint(halo, np.array([0.85, 0.8, 1.0]), 0.8)
            L.glow(halo, col, 1.0)
        L.glow(np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2), col, 0.9)
    elif theme == "orbital":
        m = band(w, r0, r1)
        L.paint(m, np.array([0.13, 0.15, 0.21]) * (lit(w) * ring_bevel(w, r0, r1))[..., None])
        minor = band(w, R_OUT + 36, R_OUT + 44) * angular_blocks(w, 180, 0.18)
        major = band(w, R_OUT + 26, R_OUT + 44) * angular_blocks(w, 36, 0.06)
        L.paint(np.maximum(minor, major), np.array([0.70, 0.80, 1.0]))
        img, d = w.L()
        f = sl.mono(13)
        for a in range(0, 360, 30):
            x, y = w.polar(R_OUT + 17, a)
            txt = "%03d" % a
            bb = f.getbbox(txt)
            d.text((x - (bb[2] - bb[0]) / 2, y - 8), txt, font=f, fill=255)
        L.paint(L2a(img), np.array([0.75, 0.85, 1.0]))
        L.paint(band(w, R_OUT + 46, R_OUT + 49), np.array([0.45, 0.6, 0.95]), 0.8)
        L.glow(np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2), col, 0.9)
        L.glow(major * 0.4, col)
    elif theme == "rebel":
        rng = np.random.default_rng(seed)
        nseg = 24
        segi = np.floor(frac(deg / 360.0) * nseg).astype(np.int32)
        offs = rng.integers(-5, 6, nseg)
        sh = offs[segi].astype(np.float32)
        m = np.clip(np.minimum(w.r - (r0 + sh), (r1 + sh) - w.r) + 0.5, 0, 1)
        gaps = angular_blocks(w, nseg, 0.93, 7.5)
        m = m * gaps
        L.paint(m, np.array([0.11, 0.02, 0.03]) * (lit(w) * ring_bevel(w, r0, r1))[..., None])
        # broken red inner line
        brk = (rng.random(72) > 0.25)[np.floor(frac(deg / 360.0) * 72).astype(np.int32)]
        line = np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2) * brk
        L.paint(line, col)
        L.glow(line, col, 1.2)
        # scan bars on the bezel
        sb = band(w, R_OUT + 22, R_OUT + 26) * (rng.random(120) > 0.6)[np.floor(frac(deg / 360.0) * 120).astype(np.int32)]
        L.paint(sb, col * 0.9)
        L.glow(sb, col, 0.6)
        img, d = w.L()
        for a in range(15, 360, 30):
            x, y = w.polar(R_OUT + 34, a)
            th._inv_hex(d, x, y, 7, 2)
        hx = L2a(img)
        L.paint(hx, np.array([1.0, 0.25, 0.25]))
        L.glow(hx, col, 0.8)
    elif theme == "player":
        m = band(w, r0, r1)
        L.paint(m, np.array([0.12, 0.12, 0.14]) * (lit(w) * ring_bevel(w, r0, r1))[..., None])
        tk = band(w, R_OUT + 30, R_OUT + 42) * angular_blocks(w, 30, 0.06, 6)
        L.paint(tk, np.array([0.75, 0.75, 0.8]))
        L.paint(band(w, R_OUT + 46, R_OUT + 49), np.array([0.5, 0.5, 0.55]))
        line = np.exp(-((w.r - (R_OUT + 7)) / 1.3) ** 2)
        L.paint(line, np.array([0.9, 0.9, 0.95]), 0.8)
        L.glow(line, np.array([0.9, 0.92, 1.0]), 0.5)
    # 30 tick marks on the inner lip (all themes)
    ticks = band(w, R_OUT + 9, R_OUT + 14) * angular_blocks(w, 30, 0.05, 6)
    L.paint(ticks, np.array([0.85, 0.85, 0.9]), 0.7)
    return L


# ----------------------------------------------------------------------------- emblems + hub
def draw_emblem(d, theme, cx, cy, s, fill=255):
    k = s / 100.0
    P = lambda pts: [(cx + (x - 50) * k, cy + (y - 50) * k) for x, y in pts]
    if theme == "meridian":       # gantry crane with hook
        d.line(P([(22, 96), (22, 8), (86, 8)]), fill=fill, width=int(9 * k))
        d.line(P([(22, 30), (44, 8)]), fill=fill, width=int(6 * k))
        d.line(P([(72, 8), (72, 44)]), fill=fill, width=int(5 * k))
        d.rectangle(P([(60, 44), (84, 64)]), fill=fill)
    elif theme == "solace":       # double helix
        for ph in (0, math.pi):
            pts = [(50 + 26 * math.sin(i / 40 * 2 * math.pi + ph), 6 + i * 88 / 40) for i in range(41)]
            d.line(P(pts), fill=fill, width=int(7 * k))
        for i in range(1, 8):
            y = 6 + i * 11
            x = 26 * math.sin((y - 6) / 88 * 2 * math.pi)
            d.line(P([(50 - x, y), (50 + x, y)]), fill=fill, width=int(4 * k))
    elif theme == "halcyon":      # civic pyramid under a halo
        d.polygon(P([(50, 30), (92, 94), (8, 94)]), fill=fill)
        d.ellipse(P([(22, 4), (78, 22)]), outline=fill, width=int(6 * k))
    elif theme == "orbital":      # planet, orbit, satellite
        d.ellipse(P([(32, 32), (68, 68)]), fill=fill)
        pts = _ell(50, 50, 48, 18, -20)
        d.line(P(pts), fill=fill, width=int(5 * k))
        d.rectangle(P([(84, 26), (96, 38)]), fill=fill)
    elif theme == "rebel":        # inverted hexagon
        th._inv_hex(d, cx, cy + 4 * k, 46 * k, int(9 * k))
        th._inv_hex(d, cx, cy + 4 * k, 20 * k, int(7 * k))
    elif theme == "player":       # the Cell: bracketed node
        d.line(P([(26, 10), (10, 10), (10, 90), (26, 90)]), fill=fill, width=int(8 * k))
        d.line(P([(74, 10), (90, 10), (90, 90), (74, 90)]), fill=fill, width=int(8 * k))
        d.ellipse(P([(36, 36), (64, 64)]), fill=fill)


def _ell(cx, cy, a, b, rot_deg, n=60):
    r = math.radians(rot_deg)
    return [(cx + a * math.cos(t) * math.cos(r) - b * math.sin(t) * math.sin(r),
             cy + a * math.cos(t) * math.sin(r) + b * math.sin(t) * math.cos(r))
            for t in [2 * math.pi * i / n for i in range(n + 1)]]


def hub(w, theme, name, corp, boss=False):
    L = Layer(w)
    col = hexrgb(th.THEMES[theme]["col"])
    rr = R_IN - 5
    disc = np.clip(rr - w.r + 0.5, 0, 1)
    g = 0.5 + 0.5 * smoothstep(0, rr, w.r)
    base = np.array([0.045, 0.045, 0.075], np.float32)
    rings = np.exp(-((np.abs(frac(w.r / 9.0 + 0.5) - 0.5) * 9) / 0.6) ** 2) * 0.04
    L.paint(disc, base * (1.3 - 0.5 * g)[..., None] + col * rings[..., None])
    rim = band(w, rr - 7, rr)
    L.paint(rim, col * 0.85 * ring_bevel(w, rr - 7, rr, 0.6)[..., None])
    L.glow(rim, col, 0.7)
    dark = band(w, rr, rr + 3)
    L.paint(dark, (0.02, 0.02, 0.03))
    img, d = w.L()
    draw_emblem(d, theme, w.c, w.c - 58, 46)
    em = L2a(img)
    L.paint(em, col)
    L.glow(em, col, 0.5)
    txt = Image.new("RGBA", (w.size, w.size), (0, 0, 0, 0))
    dt = ImageDraw.Draw(txt)
    lines = name.split("\n")
    fs = 34 if max(len(x) for x in lines) <= 11 else 28
    f = sl.font(fs)
    y = w.c - 8 - (len(lines) - 1) * fs * 0.5
    for ln in lines:
        bb = f.getbbox(ln)
        dt.text((w.c - (bb[2] - bb[0]) / 2 - bb[0], y - fs * 0.45), ln, font=f, fill=(245, 242, 250, 255))
        y += fs * 0.98
    f2 = sl.font(17, "SemiBold")
    bb = f2.getbbox(corp)
    dt.text((w.c - (bb[2] - bb[0]) / 2 - bb[0], y + 6), corp, font=f2,
            fill=tuple(int(v * 255) for v in np.clip(col * 0.9 + 0.1, 0, 1)) + (255,))
    return L, txt


def pointer(w, theme, length=80):
    """Needle: knob at the top, tip at the bottom of the returned image."""
    S = 3
    W, H = 60, length + 30
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W * S / 2
    tip = (H - 1) * S
    d.polygon([(cx - 9 * S, 22 * S), (cx + 9 * S, 22 * S), (cx + 2 * S, tip - 5 * S), (cx, tip), (cx - 2 * S, tip - 5 * S)],
              fill=(30, 28, 36, 255))
    d.polygon([(cx - 6 * S, 24 * S), (cx + 6 * S, 24 * S), (cx + 1 * S, tip - 9 * S), (cx - 1 * S, tip - 9 * S)], fill=(225, 225, 235, 255))
    d.polygon([(cx, 24 * S), (cx + 6 * S, 24 * S), (cx + 1 * S, tip - 9 * S), (cx, tip - 9 * S)], fill=(150, 150, 165, 255))
    d.ellipse([cx - 14 * S, 2 * S, cx + 14 * S, 30 * S], fill=(40, 38, 48, 255))
    d.ellipse([cx - 10 * S, 6 * S, cx + 10 * S, 26 * S], fill=(120, 118, 130, 255))
    d.ellipse([cx - 6 * S, 9 * S, cx + 2 * S, 17 * S], fill=(210, 210, 220, 255))
    img = img.resize((W, H), Image.LANCZOS)
    return img, (W, H)


# ----------------------------------------------------------------------------- assembly
def slice_angles(slices):
    first = slices[0][1]
    a = -first * sl.TICK_DEG / 2
    out = []
    for typ, ticks, val in slices:
        span = ticks * sl.TICK_DEG
        out.append(a + span / 2)
        a += span
    return out


def lod_tex(theme):
    """Small-size LOD: the corp material collapses to a flat tint (type colour for the player)."""
    col = hexrgb(th.THEMES[theme]["col"])

    def tex(ctx):
        k = smoothstep(R_IN, R_OUT, ctx.r)[..., None]
        c = ctx.accent * 0.5 if theme == "player" else col * 0.26 + 0.02
        rgb = c * (0.85 + 0.3 * k)
        return rgb, np.zeros_like(rgb)
    return tex


def render_wheel(theme, slices, name, corp, t=0.35, seed=1, boss=False, rich=False, tile_style=None,
                 phase=None, lod=False):
    w = World()
    tex = th.THEMES[theme]["tex"]
    if rich:
        base_tex = tex
        tex = lambda ctx: base_tex(ctx, rich=True)
    style = dict(tile_style or {})
    if lod:
        tex = lod_tex(theme)
        style.update(glyph_scale=1.55, plate=0.0, tab=1.0, rim=1.3, glyph_glow=0.0)
    if theme == "player":
        style.setdefault("tab", 0.0)
        style.setdefault("rim", 0.75)
        style.setdefault("glyph_glow", 0.0)
    bz = bezel(w, theme, boss=boss, seed=seed)
    out = bz.image()
    emis = bz.emis.copy()
    B = R_OUT + 12
    off = int(w.c - B)
    for i, ((typ, ticks, val), ang) in enumerate(zip(slices, slice_angles(slices))):
        acc = sl.TYPES[typ][1]
        ctx = sl.Ctx(-B, B, -B, B, ticks * sl.TICK_DEG / 2, t=(t + i * 0.137) % 1.0, seed=seed * 10 + i,
                     accent=acc, typ=typ, ticks=ticks, angle_deg=ang)
        img, em = sl.render_tile(ctx, tex, val, style)
        img = img.rotate(-ang, resample=Image.BICUBIC)
        emi = sl.emis_to_img(em).rotate(-ang, resample=Image.BICUBIC)
        out.alpha_composite(img, (off, off))
        emis[off:off + emi.height, off:off + emi.width] += np.asarray(emi, np.float32) / 255
    hb, txt = hub(w, theme, name, corp, boss)
    out.alpha_composite(hb.image())
    emis += hb.emis
    # gloss: soft highlight over the face + a specular crescent on the bezel
    g = 0.10 * np.exp(-(((w.X + 120) ** 2 + (w.Y - 160) ** 2) / (2 * 170.0 ** 2))) * (w.r < R_OUT)
    cres = np.exp(-((w.r - (R_OUT + 26)) / 6.0) ** 2) * np.clip(np.cos(w.th - LIGHT_TH), 0, 1) ** 6 * 0.18
    o = np.asarray(out, np.float32)
    o[..., :3] = o[..., :3] + ((g + cres) * 255)[..., None] * (o[..., 3:4] / 255)
    out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8), "RGBA")
    out = sl.add_glow(out, sl.emis_to_img(emis), radii=((5, 0.8), (16, 0.55), (40, 0.25)))
    out.alpha_composite(txt)
    knob_r = R_OUT + (100 if boss else 60)
    tip_r = R_OUT - 16
    pimg, (pw, ph) = pointer(w, theme, length=int(knob_r - tip_r))
    out.alpha_composite(pimg, (int(w.c - pw / 2), int(w.c - tip_r - ph)))
    if phase is not None:
        phase_marker(out, w, theme, *phase)
    return out


def phase_marker(img, w, theme, cur, total):
    """Boss phase marker: a plaque on the bezel at upper-left with lit pips."""
    d = ImageDraw.Draw(img)
    gold = (255, 205, 110, 255)
    vio = th.THEMES[theme]["col"]
    for i in range(total):
        a = -34 + i * 8
        x, y = w.polar(R_OUT + 100, a)
        s = 11
        poly = [(x, y - s), (x + s, y), (x, y + s), (x - s, y)]
        on = i < cur
        d.polygon(poly, fill=gold if on else (40, 36, 60, 255), outline=(20, 16, 30, 255), width=2)
        if i == cur - 1:
            d.polygon([(x, y - s - 5), (x + s + 5, y), (x, y + s + 5), (x - s - 5, y)], outline=gold, width=2)
    f = sl.font(22)
    x, y = w.polar(R_OUT + 146, -45)
    roman = ["I", "II", "III", "IV"]
    txt = "PHASE %s / %s" % (roman[cur - 1], roman[total - 1])
    bb = f.getbbox(txt)
    d.rounded_rectangle([x - 74, y - 16, x + 74, y + 16], radius=6, fill=(18, 14, 30, 235), outline=gold, width=2)
    d.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - 13), txt, font=f, fill=gold)


# ----------------------------------------------------------------------------- frame helpers
def background(seed=7, tints=()):
    Wf, Hf = 1920, 1080
    ys = np.linspace(0, 1, Hf, dtype=np.float32)[:, None, None]
    top = np.array([0.020, 0.018, 0.035], np.float32)
    bot = np.array([0.055, 0.045, 0.075], np.float32)
    rgb = top + (bot - top) * ys
    rgb = np.broadcast_to(rgb, (Hf, Wf, 3)).copy()
    img = Image.fromarray((rgb * 255).astype(np.uint8), "RGB")
    rng = np.random.default_rng(seed)
    city = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 0))
    d = ImageDraw.Draw(city)
    x = -20
    while x < Wf:
        bw = int(rng.integers(60, 170))
        bh = int(rng.integers(220, 640))
        shade = int(rng.integers(16, 30))
        d.rectangle([x, Hf - bh, x + bw, Hf], fill=(shade, shade - 3, shade + 8, 255))
        for wy in range(Hf - bh + 14, Hf, 22):
            for wx in range(x + 8, x + bw - 8, 16):
                if rng.random() < 0.22:
                    c = (int(rng.integers(90, 160)),) * 2 + (int(rng.integers(120, 190)),)
                    d.rectangle([wx, wy, wx + 6, wy + 8], fill=c + (255,))
        x += bw + int(rng.integers(4, 30))
    city = city.filter(ImageFilter.GaussianBlur(5))
    img = img.convert("RGBA")
    img.alpha_composite(city)
    for (cx, cy, col, rad) in tints:
        glow = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 0))
        dg = ImageDraw.Draw(glow)
        c = tuple(int(v) for v in (hexrgb(col) * 255)) + (60,)
        dg.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=c)
        glow = glow.filter(ImageFilter.GaussianBlur(rad * 0.45))
        img.alpha_composite(glow)
    # vignette
    v = Image.new("L", (Wf, Hf), 0)
    dv = ImageDraw.Draw(v)
    dv.ellipse([-300, -300, Wf + 300, Hf + 300], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGBA", (Wf, Hf), (0, 0, 0, 255))
    img = Image.composite(img, Image.alpha_composite(img, Image.new("RGBA", (Wf, Hf), (0, 0, 0, 150))), v)
    return img


def place(frame, wheel_img, cx, cy, scale):
    s = int(wheel_img.width * scale)
    im = wheel_img.resize((s, s), Image.LANCZOS)
    frame.alpha_composite(im, (int(cx - s / 2), int(cy - s / 2)))


def hp_arc(frame, cx, cy, radius, hp, hpmax, col="#7BE07B", n=30, notches=(), size=13):
    d = ImageDraw.Draw(frame)
    filled = int(round(n * hp / hpmax))
    c = tuple(int(v * 255) for v in hexrgb(col))
    for i in range(n):
        a = math.radians(122 + i * (116 / (n - 1)))
        x, y = cx + radius * math.sin(a), cy - radius * math.cos(a)
        s = size / 2
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-s, -s), (s, -s), (s, s), (-s, s))]
        on = i >= n - filled
        d.polygon(pts, fill=c + (255,) if on else (40, 44, 48, 255))
    for fracv, label in notches:
        a = math.radians(122 + (1 - fracv) * 116)
        x, y = cx + (radius + 22) * math.sin(a), cy - (radius + 22) * math.cos(a)
        x2, y2 = cx + (radius - 14) * math.sin(a), cy - (radius - 14) * math.cos(a)
        d.line([(x, y), (x2, y2)], fill=(255, 205, 110, 255), width=4)
        f = sl.font(20)
        xl, yl = cx + (radius + 40) * math.sin(a), cy - (radius + 40) * math.cos(a)
        bb = f.getbbox(label)
        d.text((xl - (bb[2] - bb[0]) / 2, yl - 12), label, font=f, fill=(255, 205, 110, 255))
    f = sl.font(64)
    txt = "%d/%d" % (hp, hpmax)
    bb = f.getbbox(txt)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy + radius + 26), txt, font=f, fill=c + (255,),
           stroke_width=2, stroke_fill=(10, 20, 10, 255))


def caption(frame, title, sub):
    d = ImageDraw.Draw(frame)
    f1 = sl.font(34)
    f2 = sl.mono(18, False)
    w1 = max(f1.getbbox(title)[2], f2.getbbox(sub)[2]) + 40
    d.rectangle([0, 1000, w1, 1080], fill=(8, 6, 12, 235))
    d.rectangle([0, 1000, 6, 1080], fill=(232, 20, 30, 255))
    d.text((20, 1006), title, font=f1, fill=(245, 245, 250, 255))
    d.text((20, 1050), sub, font=f2, fill=(200, 200, 210, 255))
