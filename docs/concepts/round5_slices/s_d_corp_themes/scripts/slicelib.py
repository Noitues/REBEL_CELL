"""Round 5 / s_d_corp_themes: shared slice-tile renderer (numpy + Pillow).

Coordinates: a tile is rendered in its LOCAL frame, origin at the hub centre, Y up,
slice axis pointing up (+Y).  A wheel rotates each local tile into place.
All randomness is seeded (numpy default_rng) so every render is reproducible.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

R_OUT = 360.0
R_IN = 130.0
TICKS = 30
TICK_DEG = 360.0 / TICKS
GAP = 3.0           # px gap between neighbouring slices
GROUP_R = R_IN + 0.60 * (R_OUT - R_IN)   # glyph+number group centre radius (60% span)

FONT_DIR = "C:/Windows/Fonts/"


def font(size, style="Bold Condensed"):
    f = ImageFont.truetype(FONT_DIR + "bahnschrift.ttf", int(size))
    try:
        f.set_variation_by_name(style)
    except Exception:
        pass
    return f


def mono(size, bold=True):
    return ImageFont.truetype(FONT_DIR + ("consolab.ttf" if bold else "consola.ttf"), int(size))


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


# slice type -> (program, colour)
TYPES = {
    "ATTACK":   ("EXPLOIT",  "#FF3DA8"),
    "CRITICAL": ("ZERO-DAY", "#FF6FD0"),
    "DEFEND":   ("FIREWALL", "#5CE1FF"),
    "SHIELD":   ("SANDBOX",  "#38D8C8"),
    "EVADE":    ("PROXY",    "#7BE07B"),
    "HEAL":     ("PATCH",    "#B4F05A"),
    "AFFLICT":  ("VIRUS",    "#C85AFF"),
    "DEPLOY":   ("TROJAN",   "#B08CFF"),
    "MISS":     ("NULL",     "#6A6A6A"),
}

GLYPH_OF = {"ATTACK": "dagger", "CRITICAL": "burst", "DEFEND": "shield", "SHIELD": "sandbox",
            "EVADE": "chevrons", "HEAL": "plus", "AFFLICT": "drop", "DEPLOY": "payload",
            "MISS": "null"}


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def frac(x):
    return x - np.floor(x)


# ----------------------------------------------------------------------------- context
class Ctx:
    """Pixel grid of a local box [x0,x1] x [y0,y1] (Y up)."""

    def __init__(self, x0, x1, y0, y1, half_deg, t=0.0, seed=1, accent="#FFFFFF", typ="ATTACK",
                 ticks=3, angle_deg=0.0):
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.W = int(round(x1 - x0))
        self.H = int(round(y1 - y0))
        xs = x0 + np.arange(self.W, dtype=np.float32) + 0.5
        ys = y1 - np.arange(self.H, dtype=np.float32) - 0.5
        self.X, self.Y = np.meshgrid(xs, ys)
        self.r = np.hypot(self.X, self.Y)
        self.th = np.arctan2(self.X, self.Y)          # 0 = up, + clockwise
        self.half = math.radians(half_deg)
        self.half_deg = half_deg
        self.t = t
        self.seed = seed
        self.accent = hexrgb(accent)
        self.accent_hex = accent
        self.typ = typ
        self.ticks = ticks
        self.angle = angle_deg                         # world angle of slice axis (clockwise)

    def px(self, X, Y):
        return (X - self.x0, self.y1 - Y)

    def blank_L(self):
        return Image.new("L", (self.W, self.H), 0)

    def arr(self, img):
        return np.asarray(img, dtype=np.float32) / 255.0

    def chord(self, r):
        return 2 * r * math.sin(self.half)


def tile_box(ticks, pad=10):
    half = math.radians(ticks * TICK_DEG / 2)
    hw = R_OUT * math.sin(half) + pad
    y0 = R_IN * math.cos(half) - pad
    return (-hw, hw, y0, R_OUT + pad)


# ----------------------------------------------------------------------------- geometry
def wedge_fields(ctx):
    """Return mask (AA), nearest-edge distance d, and nearest-edge outward normal (nx, ny)."""
    r, th, half = ctx.r, ctx.th, ctx.half
    d_out = R_OUT - r
    d_in = r - R_IN
    d_side = r * np.sin(half - np.abs(th)) - GAP / 2
    d_side = np.where(np.abs(th) < half + 0.5, d_side, -99)
    d = np.minimum(np.minimum(d_out, d_in), d_side)
    mask = np.clip(d + 0.5, 0, 1)
    rx = ctx.X / np.maximum(r, 1e-3)
    ry = ctx.Y / np.maximum(r, 1e-3)
    sgn = np.sign(th)
    snx = sgn * math.cos(half)
    sny = -math.sin(half) * np.ones_like(r)
    nx = np.where(d == d_out, rx, np.where(d == d_in, -rx, snx))
    ny = np.where(d == d_out, ry, np.where(d == d_in, -ry, sny))
    return mask, d, nx, ny


def light_local(angle_deg, lw=(-0.42, 0.91)):
    a = math.radians(angle_deg)
    x, y = lw
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


# ----------------------------------------------------------------------------- glyphs
def _rot_pts(pts, deg, c=(128, 128)):
    a = math.radians(deg)
    out = []
    for x, y in pts:
        dx, dy = x - c[0], y - c[1]
        out.append((c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a)))
    return out


def _ellipse_pts(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def draw_glyph(kind, S=512):
    """Return (fill, detail) L images at S x S (design space 256 scaled by S/256)."""
    k = S / 256.0
    fill = Image.new("L", (S, S), 0)
    det = Image.new("L", (S, S), 0)
    df = ImageDraw.Draw(fill)
    dd = ImageDraw.Draw(det)

    def P(pts):
        return [(x * k, y * k) for x, y in pts]

    if kind == "dagger":
        parts = [
            [(128, 14), (148, 52), (148, 150), (108, 150), (108, 52)],
            [(80, 148), (176, 148), (176, 168), (80, 168)],
            [(116, 166), (140, 166), (140, 212), (116, 212)],
            _ellipse_pts(128, 222, 17, 17),
        ]
        for p in parts:
            df.polygon(P(_rot_pts(p, 40)), fill=255)
        dd.line(P(_rot_pts([(128, 40), (128, 140)], 40)), fill=255, width=int(6 * k))
    elif kind == "burst":
        pts = []
        for i in range(16):
            a = math.pi * 2 * i / 16 - math.pi / 2
            rr = 120 if i % 2 == 0 else 50
            if i % 4 == 2:
                rr = 84
            pts.append((128 + rr * math.cos(a), 128 + rr * math.sin(a)))
        df.polygon(P(pts), fill=255)
        dd.ellipse(P([(110, 110), (146, 146)]), fill=255)
    elif kind == "shield":
        pts = [(128, 16), (226, 50), (220, 128)]
        for i in range(1, 12):
            a = i / 12
            pts.append((220 - 92 * a, 128 + 112 * math.sin(a * math.pi / 2)))
        pts = pts + [(128, 240)]
        left = [(256 - x, y) for x, y in reversed(pts[1:-1])]
        df.polygon(P(pts + left), fill=255)
        for y in (88, 140):
            dd.line(P([(48, y), (208, y)]), fill=255, width=int(10 * k))
        dd.line(P([(128, 40), (128, 88)]), fill=255, width=int(10 * k))
        dd.line(P([(92, 88), (92, 140)]), fill=255, width=int(10 * k))
        dd.line(P([(164, 88), (164, 140)]), fill=255, width=int(10 * k))
        dd.line(P([(128, 140), (128, 200)]), fill=255, width=int(10 * k))
    elif kind == "sandbox":
        hexo = [(128 + 116 * math.cos(math.pi / 3 * i + math.pi / 6), 128 + 116 * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)]
        hexi = [(128 + 84 * math.cos(math.pi / 3 * i + math.pi / 6), 128 + 84 * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)]
        df.polygon(P(hexo), fill=255)
        df.polygon(P(hexi), fill=0)
        df.rectangle(P([(98, 98), (158, 158)]), fill=255)
    elif kind == "chevrons":
        for ox in (-40, 36):
            pts = [(70 + ox, 40), (122 + ox, 40), (190 + ox, 128), (122 + ox, 216), (70 + ox, 216), (138 + ox, 128)]
            df.polygon(P(pts), fill=255)
    elif kind == "plus":
        df.rounded_rectangle(P([(96, 24), (160, 232)]), radius=int(20 * k), fill=255)
        df.rounded_rectangle(P([(24, 96), (232, 160)]), radius=int(20 * k), fill=255)
        for (x, y) in ((128, 60), (128, 196), (60, 128), (196, 128)):
            dd.ellipse(P([(x - 7, y - 7), (x + 7, y + 7)]), fill=255)
    elif kind == "drop":
        pts = [(128, 12)]
        for i in range(0, 41):
            a = math.radians(-35 + 250 * i / 40)
            pts.append((128 + 82 * math.cos(a), 160 + 82 * math.sin(a)))
        # reorder to make a proper teardrop
        body = _ellipse_pts(128, 162, 82, 82, 60)
        df.polygon(P(body), fill=255)
        df.polygon(P([(128, 10), (196, 118), (60, 118)]), fill=255)
        dd.ellipse(P([(88, 150), (118, 180)]), fill=255)
        dd.ellipse(P([(136, 186), (156, 206)]), fill=255)
    elif kind == "payload":
        df.polygon(P([(44, 138), (212, 138), (212, 236), (44, 236)]), fill=255)
        df.polygon(P([(44, 138), (8, 110), (80, 92), (110, 138)]), fill=255)
        df.polygon(P([(212, 138), (248, 110), (176, 92), (146, 138)]), fill=255)
        df.polygon(P([(128, 10), (178, 66), (146, 66), (146, 118), (110, 118), (110, 66), (78, 66)]), fill=255)
        dd.line(P([(70, 178), (186, 178)]), fill=255, width=int(9 * k))
    elif kind == "null":
        df.ellipse(P([(30, 30), (226, 226)]), fill=255)
        df.ellipse(P([(62, 62), (194, 194)]), fill=0)
        df.polygon(P(_rot_pts([(116, 4), (140, 4), (140, 252), (116, 252)], 45)), fill=255)
    return fill, det


_GLYPH_CACHE = {}


def glyph_rgba(kind, size, outline_px=None, accent=None):
    """White glyph with dark outline, size = glyph box in px.  Returns RGBA Image (size+2*margin)."""
    key = (kind, int(size), outline_px, None if accent is None else tuple(np.round(accent, 3)))
    if key in _GLYPH_CACHE:
        return _GLYPH_CACHE[key]
    size = int(size)
    if outline_px is None:
        outline_px = max(2, int(round(size * 0.075)))
    m = outline_px + 2
    S = size * 4
    fill, det = draw_glyph(kind, S)
    fill = fill.resize((size, size), Image.LANCZOS)
    det = det.resize((size, size), Image.LANCZOS)
    W = size + 2 * m
    F = Image.new("L", (W, W), 0)
    F.paste(fill, (m, m))
    D = Image.new("L", (W, W), 0)
    D.paste(det, (m, m))
    o = F.point(lambda v: 255 if v > 60 else 0)
    o = o.filter(ImageFilter.MaxFilter(2 * outline_px + 1)).filter(ImageFilter.GaussianBlur(0.7))
    a_out = np.asarray(o, np.float32) / 255
    a_fill = np.asarray(F, np.float32) / 255
    a_det = np.asarray(D, np.float32) / 255 * a_fill
    rgb = np.zeros((W, W, 3), np.float32)
    dark = np.array([0.04, 0.03, 0.06], np.float32)
    white = np.array([1.0, 0.98, 0.97], np.float32)
    rgb[:] = dark
    rgb = rgb * (1 - a_fill[..., None]) + white * a_fill[..., None]
    detcol = dark if accent is None else accent * 0.45
    rgb = rgb * (1 - a_det[..., None]) + detcol * a_det[..., None]
    alpha = np.maximum(a_out, a_fill)
    img = Image.fromarray(np.dstack([rgb * 255, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")
    _GLYPH_CACHE[key] = img
    return img


def number_rgba(text, fsize, outline=None):
    f = font(fsize)
    if outline is None:
        outline = max(2, int(round(fsize * 0.07)))
    bb = f.getbbox(text, stroke_width=outline)
    W, H = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((2 - bb[0], 2 - bb[1]), text, font=f, fill=(255, 250, 247, 255),
           stroke_width=outline, stroke_fill=(10, 8, 14, 255))
    return img


# ----------------------------------------------------------------------------- tile render
def layout_group(ctx, value, k=1.0):
    """Glyph size, number font size and their local centres (X, Y)."""
    wide = ctx.ticks >= 5
    ch = ctx.chord(GROUP_R)
    if wide:
        g = min(0.30 * ch * k, 76 * k)
        fs = g * 1.35
        return g, fs, (-g * 0.62, GROUP_R), (g * 0.62, GROUP_R)
    g = min(0.34 * ch * k, 62 * k)
    fs = g * 1.30
    if value is None:
        return g * 1.15, fs, (0, GROUP_R), None
    gy = GROUP_R + g * 0.58
    ny = GROUP_R - fs * 0.40
    return g, fs, (0, gy), (0, ny)


def paste_center(base, img, cx, cy):
    base.alpha_composite(img, (int(round(cx - img.width / 2)), int(round(cy - img.height / 2))))


def render_tile(ctx, tex_fn, value, style):
    """Render one slice tile in the local frame.

    tex_fn(ctx) -> (rgb[H,W,3] float, emis[H,W,3] float)
    style: dict(plate=float, rim=float, tab=float, glyph_accent=bool)
    Returns (RGBA Image, emissive float array).
    """
    rgb, emis = tex_fn(ctx)
    mask, d, nx, ny = wedge_fields(ctx)
    g, fs, gpos, npos = layout_group(ctx, value, style.get("glyph_scale", 1.0))

    # readability plate: darken an ellipse under the glyph + number
    plate = style.get("plate", 0.55)
    if plate > 0:
        cy = GROUP_R + (0 if npos is None or ctx.ticks >= 5 else 4)
        sx = (g * 1.25 if ctx.ticks < 5 else g * 1.9)
        sy = g * 1.55
        e = ((ctx.X / sx) ** 2 + ((ctx.Y - cy) / sy) ** 2)
        rgb = rgb * (1 - plate * np.exp(-e * 1.1))[..., None]
        emis = emis * (1 - 0.8 * np.exp(-e * 1.2))[..., None]

    acc = ctx.accent
    # type-colour tab along the outer edge
    tab = style.get("tab", 0.85)
    d_out = R_OUT - ctx.r
    tabm = (smoothstep(13, 10, d_out) * smoothstep(1.5, 3.5, d_out))[..., None] * tab
    rgb = rgb * (1 - tabm) + acc * tabm
    # accent rim stroke (inner glow line)
    rim = style.get("rim", 1.0)
    line = np.exp(-((d - 3.0) / 1.4) ** 2) * rim
    inner = np.exp(-np.maximum(d - 3.0, 0) / 9.0) * 0.22 * rim
    rgb = rgb + acc * (line * 0.85 + inner)[..., None]
    emis = emis + acc * (line * 0.9)[..., None] + acc * (tabm * 0.5)

    # bevel lighting
    lx, ly = light_local(ctx.angle)
    bw = 7.0
    s = np.clip(1 - d / bw, 0, 1)
    facing = nx * lx + ny * ly
    shade = 1 + s * facing * 0.65
    rgb = rgb * shade[..., None]
    rgb = rgb + (np.exp(-((d - 1.2) / 0.9) ** 2) * np.clip(facing, 0, 1) * 0.35)[..., None]
    # soft cavity shadow just inside the bevel
    rgb = rgb * (1 - 0.18 * np.exp(-((d - bw - 2) / 3.0) ** 2))[..., None]

    rgb = np.clip(rgb, 0, 1)
    img = Image.fromarray(np.dstack([rgb * 255, mask * 255]).astype(np.uint8), "RGBA")

    # glyph + number, upright in local frame (reads outward)
    kind = GLYPH_OF[ctx.typ]
    gi = glyph_rgba(kind, g, accent=acc)
    # accent glow halo behind glyph
    if style.get("glyph_glow", 0.55) > 0:
        padn = int(g * 0.5)
        a = np.pad(np.asarray(gi.split()[3], np.float32) / 255, padn)
        halo = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(g * 0.12))
        ha = np.asarray(halo, np.float32) / 255 * style.get("glyph_glow", 0.55)
        hl = Image.fromarray(np.dstack([np.broadcast_to(acc * 255, ha.shape + (3,)), ha * 255]).astype(np.uint8), "RGBA")
        hx, hy = ctx.px(*gpos)
        paste_center(img, hl, hx, hy)
    hx, hy = ctx.px(*gpos)
    paste_center(img, gi, hx, hy)
    if npos is not None and value is not None:
        ni = number_rgba(str(value), fs)
        nxp, nyp = ctx.px(*npos)
        paste_center(img, ni, nxp, nyp)
    # re-mask so glyphs never leave the wedge
    arr = np.asarray(img, np.float32)
    arr[..., 3] = np.minimum(arr[..., 3], mask * 255)
    emis = emis * mask[..., None]
    return Image.fromarray(arr.astype(np.uint8), "RGBA"), emis


def emis_to_img(emis):
    return Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8), "RGB")


# ----------------------------------------------------------------------------- compositing helpers
def add_glow(base_rgba, emis_img, radii=((6, 0.9), (18, 0.6))):
    """Additive bloom of an emissive RGB image onto an RGBA image (alpha kept)."""
    b = np.asarray(base_rgba, np.float32)
    acc = np.zeros(b.shape[:2] + (3,), np.float32)
    for rad, k in radii:
        acc += np.asarray(emis_img.filter(ImageFilter.GaussianBlur(rad)), np.float32) * k
    a0 = b[..., 3:4] / 255.0
    prem = b[..., :3] * a0 + acc
    a = np.clip(np.maximum(a0[..., 0], acc.max(axis=2) / 255.0 * 1.2), 0, 1)
    rgb = prem / np.maximum(a, 1e-3)[..., None]
    a = a * 255
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a]).astype(np.uint8), "RGBA")


def rgba_from(rgb, a):
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 1) * 255, np.clip(a, 0, 1) * 255]).astype(np.uint8), "RGBA")
