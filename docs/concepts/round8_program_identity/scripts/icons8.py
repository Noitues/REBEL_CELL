"""Round 8: bold program identity art ("hacker splash screens").

Every image is drawn on a 1024 canvas from shaded silhouette layers:
dark outline -> vertical gradient fill -> top-left rim light -> bottom-right core shadow,
plus coloured glows. Then it is placed in the slice's CRT screen (behind the glyph, over a
dimmed copy of the program's own screen), so C's scanlines/phosphor apply on top.
Animation: every drawer takes t in [0, 1) and loops.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from slicelib import font, f_num, f_mono, PROGRAMS, CORPS

N = 1024

# ----------------------------------------------------------------- palettes
ATK = dict(glow=(255, 60, 110), hot=(255, 150, 60))
DEF = dict(glow=(92, 225, 255), steel_t=(228, 244, 252), steel_b=(58, 98, 128))
UTI = dict(glow=(123, 224, 123), violet=(190, 120, 255))
BONE = ((255, 244, 238), (196, 120, 140))
STEEL = ((228, 244, 252), (58, 98, 128))
WOOD = ((255, 186, 120), (140, 52, 36))
PAPER = ((255, 246, 236), (205, 170, 180))
GREEN = ((220, 255, 200), (50, 140, 80))
GREY = ((210, 210, 218), (70, 70, 80))
INK = (10, 6, 16)


def L():
    return Image.new("L", (N, N), 0)


def _grad(mask, top, bot):
    bb = mask.getbbox() or (0, 0, N, N)
    y = np.arange(N, dtype=np.float32)[:, None, None]
    k = np.clip((y - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)
    top = np.array(top, np.float32)
    bot = np.array(bot, np.float32)
    return np.broadcast_to(top + (bot - top) * k, (N, N, 3))


def _over(base, rgb, alpha):
    """base: float RGBA array (N,N,4) 0..1; rgb (N,N,3) 0..255 or tuple; alpha (N,N) 0..1."""
    rgb = np.asarray(rgb, np.float32) / 255
    a = alpha[..., None]
    base[..., :3] = base[..., :3] * (1 - a) + rgb * a
    base[..., 3:] = base[..., 3:] * (1 - a) + a


def _m(mask):
    return np.asarray(mask, np.float32) / 255


def paint(base, mask, top, bot, rim=(255, 255, 255), rim_k=0.55, edge=INK, edge_w=11, shade_k=0.35):
    """Bold shaded silhouette: outline, gradient, rim light, core shadow."""
    if edge_w:
        dil = mask.filter(ImageFilter.GaussianBlur(edge_w * 0.55)).point(lambda v: 255 if v > 10 else 0)
        _over(base, edge, _m(dil))
    g = _grad(mask, top, bot).copy()
    m = _m(mask)
    sh = ImageChops.offset(mask, 10, 12)
    rimm = _m(ImageChops.subtract(mask, sh).filter(ImageFilter.GaussianBlur(3)))
    g = g * (1 - rimm[..., None] * rim_k) + np.array(rim, np.float32) * rimm[..., None] * rim_k
    sh2 = ImageChops.offset(mask, -14, -16)
    dark = _m(ImageChops.subtract(mask, sh2).filter(ImageFilter.GaussianBlur(5)))
    g = g * (1 - dark[..., None] * shade_k)
    _over(base, g, m)


def flat(base, mask, col, k=1.0):
    _over(base, np.broadcast_to(np.array(col, np.float32), (N, N, 3)), _m(mask) * k)


def glow(base, mask, col, radius=40, k=0.9):
    gm = _m(mask.filter(ImageFilter.GaussianBlur(radius)))
    c = np.array(col, np.float32) / 255
    base[..., :3] = base[..., :3] + gm[..., None] * c * k
    base[..., 3:] = np.maximum(base[..., 3:], np.clip(gm * k, 0, 1)[..., None])


def new_base():
    return np.zeros((N, N, 4), np.float32)


# ----------------------------------------------------------------- shared shapes
def skull_masks(cx, cy, s, jaw=0.0):
    m = L()
    d = ImageDraw.Draw(m)
    d.ellipse([cx - s, cy - 1.1 * s, cx + s, cy + 0.62 * s], fill=255)
    d.polygon([(cx - 0.86 * s, cy + 0.15 * s), (cx + 0.86 * s, cy + 0.15 * s), (cx + 0.66 * s, cy + 0.72 * s), (cx - 0.66 * s, cy + 0.72 * s)], fill=255)
    d.rounded_rectangle([cx - 0.6 * s, cy + (0.62 + jaw) * s, cx + 0.6 * s, cy + (1.12 + jaw) * s], radius=0.14 * s, fill=255)
    eyes = L()
    de = ImageDraw.Draw(eyes)
    for sx in (-1, 1):
        de.polygon([(cx + sx * 0.12 * s, cy - 0.1 * s), (cx + sx * 0.72 * s, cy - 0.28 * s), (cx + sx * 0.66 * s, cy + 0.22 * s),
                    (cx + sx * 0.22 * s, cy + 0.3 * s)], fill=255)
    nose = [(cx, cy + 0.34 * s), (cx - 0.13 * s, cy + 0.58 * s), (cx + 0.13 * s, cy + 0.58 * s)]
    de.polygon(nose, fill=255)
    m = ImageChops.subtract(m, eyes)
    d = ImageDraw.Draw(m)
    for k in range(5):
        x = cx + (-0.4 + k * 0.2) * s
        d.line([(x, cy + (0.72 + jaw) * s), (x, cy + (1.06 + jaw) * s)], fill=0, width=int(0.06 * s))
    d.line([(cx - 0.6 * s, cy + (0.66 + jaw * 0.5) * s), (cx + 0.6 * s, cy + (0.66 + jaw * 0.5) * s)], fill=0, width=int(0.05 * s))
    return m, eyes


def flame_mask(cx, base_y, w, h, t, seed, tongues=6, sharp=0.075):
    rng = np.random.default_rng(seed)
    pos = np.sort(rng.random(tongues) * 0.84 + 0.08)
    hs = 0.55 + 0.45 * rng.random(tongues)
    ph = rng.random(tongues)
    pts = []
    for i in range(121):
        u = i / 120
        env = math.sin(math.pi * u) ** 0.7
        v = 0.0
        for p, hh, pp in zip(pos, hs, ph):
            wob = 0.72 + 0.28 * math.sin(2 * math.pi * (t * 2 + pp))
            sway = 0.025 * math.sin(2 * math.pi * (t + pp))
            v = max(v, hh * wob * math.exp(-((u - p - sway) / sharp) ** 2))
        v = max(v * env, 0.3 * env)
        pts.append((cx - w / 2 + u * w, base_y - h * v))
    m = L()
    d = ImageDraw.Draw(m)
    d.polygon(pts + [(cx + w / 2, base_y), (cx - w / 2, base_y)], fill=255)
    d.ellipse([cx - w / 2, base_y - w * 0.12, cx + w / 2, base_y + w * 0.12], fill=255)
    return m


def fire(base, cx, base_y, w, h, t, seed=1, cool=False):
    outer = flame_mask(cx, base_y, w, h, t, seed)
    glow(base, outer, (255, 90, 30), 50, 1.0)
    paint(base, outer, (255, 120, 40), (200, 20, 60), rim=(255, 230, 160), rim_k=0.4, edge_w=8, shade_k=0.2)
    mid = flame_mask(cx, base_y, w * 0.72, h * 0.78, t + 0.17, seed + 5)
    paint(base, mid, (255, 210, 80), (255, 90, 30), rim=(255, 255, 220), rim_k=0.4, edge_w=0, shade_k=0.1)
    core = flame_mask(cx, base_y, w * 0.42, h * 0.5, t + 0.33, seed + 9, tongues=3, sharp=0.12)
    flat(base, core, (255, 250, 220))


def spark(base, x, y, r, t):
    k = 0.75 + 0.25 * math.sin(2 * math.pi * t * 3)
    m = L()
    d = ImageDraw.Draw(m)
    pts = []
    for i in range(16):
        rr = r * k * (1.0 if i % 2 == 0 else 0.35)
        a = math.radians(i * 22.5 + t * 90)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=255)
    glow(base, m, (255, 200, 80), 30, 1.2)
    flat(base, m, (255, 252, 220))


def bomb_shape(base, cx, cy, r, t, fuse=True):
    m = L()
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    paint(base, m, (110, 100, 130), (14, 10, 24), rim=(255, 160, 140), rim_k=0.7)
    hl = L()
    ImageDraw.Draw(hl).ellipse([cx - r * 0.62, cy - r * 0.66, cx - r * 0.22, cy - r * 0.36], fill=255)
    flat(base, hl.filter(ImageFilter.GaussianBlur(6)), (255, 255, 255), 0.7)
    cap = L()
    dc = ImageDraw.Draw(cap)
    a = math.radians(-45)
    capc = (cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a))
    capm = Image.new("L", (N, N), 0)
    ImageDraw.Draw(capm).rounded_rectangle([capc[0] - r * 0.28, capc[1] - r * 0.2, capc[0] + r * 0.28, capc[1] + r * 0.2], radius=10, fill=255)
    capm = capm.rotate(45, center=capc)
    paint(base, capm, STEEL[0], STEEL[1], edge_w=8)
    if fuse:
        f = L()
        x0, y0 = capc[0] + r * 0.18, capc[1] - r * 0.18
        pts = [(x0 + k * r * 0.07, y0 - r * 0.35 * math.sin(k / 6 * math.pi) - k * r * 0.05) for k in range(8)]
        ImageDraw.Draw(f).line(pts, fill=255, width=int(r * 0.09), joint="curve")
        paint(base, f, (240, 210, 160), (150, 100, 60), edge_w=6)
        spark(base, pts[-1][0], pts[-1][1], r * 0.32, t)


def envelope(base, x0, y0, x1, y1, open_flap=True, front_alpha=1.0):
    back = L()
    ImageDraw.Draw(back).rectangle([x0, y0, x1, y1], fill=255)
    paint(base, back, PAPER[0], PAPER[1], rim_k=0.3)
    if open_flap:
        fl = L()
        ImageDraw.Draw(fl).polygon([(x0, y0), ((x0 + x1) / 2, y0 - (y1 - y0) * 0.62), (x1, y0)], fill=255)
        paint(base, fl, (240, 220, 225), (180, 140, 160), rim_k=0.3)


def envelope_front(base, x0, y0, x1, y1):
    fr = L()
    ImageDraw.Draw(fr).polygon([(x0, y0 + (y1 - y0) * 0.25), ((x0 + x1) / 2, y0 + (y1 - y0) * 0.62), (x1, y0 + (y1 - y0) * 0.25), (x1, y1), (x0, y1)], fill=255)
    paint(base, fr, (255, 250, 245), (215, 180, 190), rim_k=0.35)


def hook(base, cx, top, t):
    line = L()
    ImageDraw.Draw(line).line([(cx, 0), (cx, top)], fill=255, width=8)
    flat(base, line, (230, 230, 240), 0.8)
    m = L()
    d = ImageDraw.Draw(m)
    d.ellipse([cx - 34, top - 10, cx + 34, top + 58], outline=255, width=20)
    d.line([(cx, top + 50), (cx, top + 420)], fill=255, width=46)
    d.arc([cx - 260, top + 250, cx + 24, top + 560], 0, 180, fill=255, width=46)
    d.polygon([(cx - 262, top + 400), (cx - 300, top + 300), (cx - 210, top + 360)], fill=255)
    paint(base, m, (255, 225, 235), (150, 60, 90), rim=(255, 255, 255), rim_k=0.7)


def vgrid_static(base, mask, seed, t, k=0.9):
    rng = np.random.default_rng(seed + int(t * 24))
    nz = rng.random((N // 8, N // 8)).astype(np.float32)
    nz = np.kron(nz, np.ones((8, 8), np.float32))
    m = _m(mask)
    rgb = np.stack([nz * 220, nz * 220, nz * 235], 2)
    _over(base, rgb, m * k)


def chip(base, x0, y0, x1, y1, top=(70, 70, 84), bot=(16, 16, 22)):
    pins = L()
    d = ImageDraw.Draw(pins)
    n = 6
    for i in range(n):
        y = y0 + (i + 0.5) * (y1 - y0) / n
        d.rectangle([x0 - 60, y - 14, x1 + 60, y + 14], fill=255)
        x = x0 + (i + 0.5) * (x1 - x0) / n
        d.rectangle([x - 14, y0 - 60, x + 14, y1 + 60], fill=255)
    paint(base, pins, (240, 230, 190), (150, 130, 80), edge_w=6, rim_k=0.4)
    body = L()
    ImageDraw.Draw(body).rounded_rectangle([x0, y0, x1, y1], radius=24, fill=255)
    paint(base, body, top, bot, rim=(200, 255, 220), rim_k=0.45)
    dot = L()
    ImageDraw.Draw(dot).ellipse([x0 + 30, y0 + 30, x0 + 70, y0 + 70], fill=255)
    flat(base, dot, (40, 40, 48))


def text_mask(txt, x, y, px, anchor="mm", var=b"Bold Condensed"):
    m = L()
    f = font("bahnschrift.ttf", px, var)
    ImageDraw.Draw(m).text((x, y), txt, font=f, fill=255, anchor=anchor)
    return m


# ================================================================== the images
def a_flaming_skull(t):
    b = new_base()
    fire(b, 512, 720, 760, 860, t, seed=3)
    sk, eyes = skull_masks(512, 560, 250)
    paint(b, sk, BONE[0], BONE[1], rim=(255, 255, 255), rim_k=0.6)
    glow(b, eyes, (255, 80, 40), 26, 1.4)
    flat(b, eyes, (255, 110 + int(60 * math.sin(2 * math.pi * t * 2)), 40))
    small = flame_mask(512, 470, 380, 260, t + 0.5, 21, tongues=4)
    flat(b, ImageChops.multiply(small, eyes.filter(ImageFilter.MaxFilter(9))), (255, 230, 120), 0.8)
    return b


def a_fire(t):
    b = new_base()
    fire(b, 512, 930, 720, 960, t, seed=7)
    return b


def a_bomb(t):
    b = new_base()
    bomb_shape(b, 470, 600, 300, t)
    sk, eyes = skull_masks(470, 590, 120)
    flat(b, sk, (255, 70, 120), 0.85)
    return b


def a_skull(t):
    b = new_base()
    jaw = 0.06 * max(0.0, math.sin(2 * math.pi * t * 2))
    sk, eyes = skull_masks(512, 470, 340, jaw)
    glow(b, sk, (255, 60, 150), 60, 0.9)
    paint(b, sk, BONE[0], BONE[1], rim=(255, 255, 255), rim_k=0.65)
    glow(b, eyes, (255, 40, 150), 30, 1.5)
    flat(b, eyes, (255, 60, 170))
    cr = L()
    ImageDraw.Draw(cr).line([(560, 140), (600, 230), (560, 300), (620, 380)], fill=255, width=14)
    flat(b, cr, INK)
    # glitch slice
    k = int(t * 24)
    if k % 6 in (2, 3):
        y = 300 + (k * 97) % 400
        b[y:y + 40] = np.roll(b[y:y + 40], 30, axis=1)
    return b


def a_skull_fuse(t):
    b = new_base()
    sk, eyes = skull_masks(470, 560, 280)
    paint(b, sk, BONE[0], BONE[1], rim_k=0.65)
    glow(b, eyes, (255, 80, 40), 30, 1.4)
    flat(b, eyes, (255, 120, 50))
    f = L()
    pts = [(560, 250), (610, 170), (690, 140), (760, 100), (820, 110)]
    ImageDraw.Draw(f).line(pts, fill=255, width=26, joint="curve")
    paint(b, f, (240, 210, 160), (150, 100, 60), edge_w=6)
    spark(b, 830, 105, 90, t)
    return b


def a_crossbones(t):
    b = new_base()
    bones = L()
    d = ImageDraw.Draw(bones)
    for (p0, p1) in (((150, 820), (874, 260)), ((150, 260), (874, 820))):
        d.line([p0, p1], fill=255, width=70)
        for p in (p0, p1):
            for o in (-34, 34):
                d.ellipse([p[0] - 52 + o * 0.6, p[1] - 52 - o * 0.6, p[0] + 52 + o * 0.6, p[1] + 52 - o * 0.6], fill=255)
    paint(b, bones, BONE[0], BONE[1], rim_k=0.5)
    sk, eyes = skull_masks(512, 430, 250)
    paint(b, sk, BONE[0], BONE[1], rim_k=0.6)
    flat(b, eyes, (255, 60, 150))
    glow(b, eyes, (255, 40, 150), 26, 1.2)
    return b


def a_poison_vial(t):
    b = new_base()
    glass = L()
    d = ImageDraw.Draw(glass)
    d.ellipse([260, 360, 764, 880], fill=255)
    d.rectangle([430, 170, 594, 420], fill=255)
    d.rounded_rectangle([400, 150, 624, 200], radius=16, fill=255)
    paint(b, glass, (120, 90, 150), (30, 14, 50), rim=(255, 220, 255), rim_k=0.8, shade_k=0.2)
    liq = L()
    dl = ImageDraw.Draw(liq)
    wave = [(x, 560 + 18 * math.sin(x / 50 + t * 2 * math.pi)) for x in range(250, 780, 10)]
    dl.polygon(wave + [(780, 900), (250, 900)], fill=255)
    inside = L()
    ImageDraw.Draw(inside).ellipse([290, 390, 734, 850], fill=255)
    liq = ImageChops.multiply(liq, inside)
    glow(b, liq, (200, 60, 255), 60, 1.0)
    paint(b, liq, (230, 120, 255), (90, 0, 140), rim=(255, 220, 255), rim_k=0.6, edge_w=0)
    for k in range(6):  # bubbles
        y = 820 - ((t + k * 0.17) % 1.0) * 260
        x = 380 + k * 55
        bm = L()
        ImageDraw.Draw(bm).ellipse([x - 16, y - 16, x + 16, y + 16], outline=255, width=6)
        flat(b, bm, (255, 220, 255), 0.9)
    sk, eyes = skull_masks(512, 650, 95)
    flat(b, sk, (255, 245, 250))
    flat(b, eyes, (60, 0, 80))
    cork = L()
    ImageDraw.Draw(cork).rounded_rectangle([450, 60, 574, 165], radius=18, fill=255)
    paint(b, cork, WOOD[0], WOOD[1])
    for k in range(2):  # drips running down the neck
        u = (t + k * 0.5) % 1.0
        y = 200 + u * 700
        x = 410 - k * 0 if u < 0.25 else 300 - k * 30
        x = 405 if k == 0 else 610
        dm = L()
        dd = ImageDraw.Draw(dm)
        dd.ellipse([x - 22, y - 10, x + 22, y + 34], fill=255)
        dd.polygon([(x - 18, y + 4), (x + 18, y + 4), (x, y - 44)], fill=255)
        glow(b, dm, (200, 60, 255), 20, 1.0)
        paint(b, dm, (240, 150, 255), (110, 0, 170), edge_w=5)
    return b


def a_bio_bug(t):
    b = new_base()
    legs = L()
    d = ImageDraw.Draw(legs)
    wig = 14 * math.sin(2 * math.pi * t * 3)
    for sx in (-1, 1):
        for k, y in enumerate((470, 590, 710)):
            d.line([(512, y), (512 + sx * 300, y - 60 + k * 40 + wig * sx), (512 + sx * 380, y + 60 + k * 30)], fill=255, width=30, joint="curve")
        d.line([(512 + sx * 40, 300), (512 + sx * 170, 130 + wig), (512 + sx * 230, 110)], fill=255, width=18)
    paint(b, legs, (120, 40, 70), (30, 6, 20), edge_w=6)
    body = L()
    db = ImageDraw.Draw(body)
    db.ellipse([300, 380, 724, 900], fill=255)
    db.ellipse([400, 250, 624, 430], fill=255)
    glow(b, body, (255, 60, 110), 50, 0.8)
    paint(b, body, (255, 120, 150), (110, 10, 50), rim=(255, 230, 240), rim_k=0.7)
    hz = L()  # biohazard mark
    dh = ImageDraw.Draw(hz)
    c = (512, 650)
    for k in range(3):
        a = math.radians(-90 + k * 120)
        ox, oy = c[0] + 70 * math.cos(a), c[1] + 70 * math.sin(a)
        dh.ellipse([ox - 70, oy - 70, ox + 70, oy + 70], fill=255)
    for k in range(3):
        a = math.radians(-90 + k * 120)
        ox, oy = c[0] + 95 * math.cos(a), c[1] + 95 * math.sin(a)
        dh.ellipse([ox - 50, oy - 50, ox + 50, oy + 50], fill=0)
    dh.ellipse([c[0] - 30, c[1] - 30, c[0] + 30, c[1] + 30], fill=0)
    dh.ellipse([c[0] - 100, c[1] - 100, c[0] + 100, c[1] + 100], outline=255, width=18)
    flat(b, hz, (30, 6, 20))
    eyes = L()
    for sx in (-1, 1):
        ImageDraw.Draw(eyes).ellipse([512 + sx * 50 - 22, 310, 512 + sx * 50 + 22, 354], fill=255)
    flat(b, eyes, (255, 240, 120))
    glow(b, eyes, (255, 240, 120), 14, 1.2)
    return b


def cloud_mask(cx, cy, s):
    m = L()
    d = ImageDraw.Draw(m)
    for (dx, dy, r) in ((-0.55, 0.15, 0.42), (-0.15, -0.18, 0.55), (0.35, -0.05, 0.48), (0.7, 0.2, 0.34), (0.05, 0.25, 0.45)):
        d.ellipse([cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s], fill=255)
    d.rounded_rectangle([cx - 0.95 * s, cy + 0.05 * s, cx + 1.02 * s, cy + 0.55 * s], radius=0.25 * s, fill=255)
    return m


def a_storm_cloud(t):
    b = new_base()
    rng = np.random.default_rng(5)
    rain = L()
    d = ImageDraw.Draw(rain)
    for k in range(26):
        x = 160 + rng.random() * 700
        y = 520 + ((rng.random() + t) % 1.0) * 480
        s = 16 + rng.random() * 18
        d.rectangle([x, y, x + s, y + s], fill=255)
    glow(b, rain, (200, 60, 255), 16, 1.0)
    flat(b, rain, (230, 120, 255))
    cm = cloud_mask(512, 330, 400)
    paint(b, cm, (120, 100, 140), (34, 22, 48), rim=(230, 200, 255), rim_k=0.6)
    on = (int(t * 24) % 8) < 5
    bolt = L()
    ImageDraw.Draw(bolt).polygon([(560, 420), (430, 700), (520, 690), (440, 960), (650, 620), (560, 630), (640, 420)], fill=255)
    glow(b, bolt, (255, 200, 120), 40, 1.6 if on else 0.6)
    paint(b, bolt, (255, 255, 220), (255, 170, 60), edge_w=8, rim_k=0.3)
    return b


def a_trojan_horse(t):
    b = new_base()
    m = L()
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([170, 430, 760, 640], radius=90, fill=255)  # body
    d.polygon([(640, 470), (700, 250), (770, 150), (900, 170), (960, 270), (900, 300), (820, 290), (780, 480)], fill=255)  # neck+head
    for x in (220, 320, 600, 700):
        d.rectangle([x, 600, x + 60, 800], fill=255)
    d.rectangle([140, 790, 820, 840], fill=255)
    d.polygon([(170, 470), (60, 560), (90, 600), (190, 540)], fill=255)  # tail
    for x in (220, 420, 620, 780):
        d.ellipse([x - 48, 810, x + 48, 906], fill=255)
    paint(b, m, WOOD[0], WOOD[1], rim=(255, 230, 190), rim_k=0.55)
    pl = L()
    dp = ImageDraw.Draw(pl)
    for y in (480, 530, 580):
        dp.line([(200, y), (740, y)], fill=255, width=6)
    flat(b, pl, (90, 30, 20), 0.8)
    mane = L()
    dm = ImageDraw.Draw(mane)
    for k in range(6):
        x, y = 700 + k * 14, 240 + k * 40
        dm.polygon([(x, y), (x - 70, y + 20), (x - 10, y + 40)], fill=255)
    paint(b, mane, (255, 120, 80), (150, 30, 30), edge_w=6)
    eye = L()
    ImageDraw.Draw(eye).ellipse([840, 200, 872, 232], fill=255)
    k = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    flat(b, eye, (255, int(60 + 120 * (1 - k)), 60))
    hatch = L()
    ImageDraw.Draw(hatch).rectangle([380, 470, 560, 620], fill=255)
    glow(b, hatch, (255, 40, 90), 50, 1.4)
    flat(b, hatch, (40, 0, 20))
    sk, eyes = skull_masks(470, 535, 58)
    flat(b, sk, (255, 70 + int(80 * k), 140))
    door = L()
    ImageDraw.Draw(door).polygon([(380, 620), (560, 620), (600, 720), (420, 720)], fill=255)
    paint(b, door, WOOD[0], WOOD[1], edge_w=6)
    return b


def a_envelope_bomb(t):
    b = new_base()
    envelope(b, 180, 520, 844, 900)
    bomb_shape(b, 512, 470, 210, t)
    envelope_front(b, 180, 520, 844, 900)
    at = text_mask("@", 300, 800, 150)
    flat(b, at, (220, 40, 90))
    return b


def a_phish_hook(t):
    b = new_base()
    sway = 20 * math.sin(2 * math.pi * t)
    hook(b, 600 + sway, 120, t)
    env = Image.new("L", (N, N), 0)
    envelope(b, 200 + sway, 640, 640 + sway, 920, open_flap=False)
    envelope_front(b, 200 + sway, 640, 640 + sway, 920)
    at = text_mask("@", 420 + sway, 820, 140)
    flat(b, at, (220, 40, 90))
    return b


def a_hook_password(t):
    b = new_base()
    sway = 20 * math.sin(2 * math.pi * t)
    hook(b, 640 + sway, 100, t)
    card = L()
    ImageDraw.Draw(card).rounded_rectangle([150 + sway, 600, 700 + sway, 860], radius=30, fill=255)
    paint(b, card, (60, 30, 50), (20, 8, 18), rim=(255, 150, 200), rim_k=0.6)
    tx = text_mask("***", 425 + sway, 760, 260)
    glow(b, tx, (255, 60, 150), 20, 1.2)
    flat(b, tx, (255, 230, 240))
    return b


def bricks(base, x0, y0, x1, y1, rows, top, bot, seed=0):
    m = L()
    d = ImageDraw.Draw(m)
    rh = (y1 - y0) / rows
    bw = rh * 2.1
    for r in range(rows):
        off = (bw / 2) * (r % 2)
        x = x0 - off
        while x < x1:
            d.rectangle([max(x0, x) + 6, y0 + r * rh + 6, min(x1, x + bw) - 6, y0 + (r + 1) * rh - 6], fill=255)
            x += bw
    paint(base, m, top, bot, rim=(240, 255, 255), rim_k=0.6, edge_w=6)
    return m


def d_burning_wall(t):
    b = new_base()
    fire(b, 512, 540, 940, 560, t, seed=11)
    bricks(b, 40, 470, 984, 960, 5, (200, 238, 255), (40, 90, 130))
    return b


def d_wall_shield(t):
    b = new_base()
    bricks(b, 40, 120, 984, 960, 8, (190, 225, 245), (40, 80, 120))
    sh = shield_mask(512, 300, 360)
    glow(b, sh, (92, 225, 255), 50, 1.0)
    paint(b, sh, STEEL[0], STEEL[1], rim_k=0.7)
    return b


def shield_mask(cx, y0, w):
    m = L()
    ImageDraw.Draw(m).polygon([(cx - w, y0), (cx + w, y0), (cx + w, y0 + w * 0.8), (cx, y0 + w * 1.75), (cx - w, y0 + w * 0.8)], fill=255)
    return m


def d_vault_door(t):
    b = new_base()
    c = 512
    seal = 0.5 - 0.5 * math.cos(2 * math.pi * t)  # 0 open .. 1 sealed
    hinge = L()
    ImageDraw.Draw(hinge).rectangle([40, 360, 160, 660], fill=255)
    paint(b, hinge, STEEL[0], STEEL[1])
    bolts = L()
    db = ImageDraw.Draw(bolts)
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = 380, 440 + 50 * seal
        p = [(c + r0 * math.cos(a) - 22 * math.sin(a), c + r0 * math.sin(a) + 22 * math.cos(a)),
             (c + r1 * math.cos(a) - 22 * math.sin(a), c + r1 * math.sin(a) + 22 * math.cos(a)),
             (c + r1 * math.cos(a) + 22 * math.sin(a), c + r1 * math.sin(a) - 22 * math.cos(a)),
             (c + r0 * math.cos(a) + 22 * math.sin(a), c + r0 * math.sin(a) - 22 * math.cos(a))]
        db.polygon(p, fill=255)
    paint(b, bolts, (240, 250, 255), (110, 140, 160), edge_w=6)
    ring = L()
    ImageDraw.Draw(ring).ellipse([c - 420, c - 420, c + 420, c + 420], fill=255)
    glow(b, ring, (92, 225, 255), 40, 0.6)
    paint(b, ring, STEEL[0], STEEL[1], rim_k=0.7)
    door = L()
    ImageDraw.Draw(door).ellipse([c - 340, c - 340, c + 340, c + 340], fill=255)
    paint(b, door, (170, 205, 225), (40, 70, 95), rim_k=0.5)
    gr = L()
    dg = ImageDraw.Draw(gr)
    for r in (300, 250):
        dg.ellipse([c - r, c - r, c + r, c + r], outline=255, width=8)
    flat(b, gr, (30, 50, 70), 0.8)
    wheel = L()
    dw = ImageDraw.Draw(wheel)
    dw.ellipse([c - 170, c - 170, c + 170, c + 170], outline=255, width=40)
    rot = t * 180
    for k in range(4):
        a = math.radians(rot + k * 90)
        dw.line([(c, c), (c + 210 * math.cos(a), c + 210 * math.sin(a))], fill=255, width=40)
        dw.ellipse([c + 210 * math.cos(a) - 30, c + 210 * math.sin(a) - 30, c + 210 * math.cos(a) + 30, c + 210 * math.sin(a) + 30], fill=255)
    dw.ellipse([c - 60, c - 60, c + 60, c + 60], fill=255)
    paint(b, wheel, (250, 255, 255), (90, 130, 150), rim_k=0.7)
    if seal > 0.85:
        lamp = L()
        ImageDraw.Draw(lamp).ellipse([c - 20, c - 20, c + 20, c + 20], fill=255)
        glow(b, lamp, (92, 225, 255), 30, 1.5)
        flat(b, lamp, (200, 255, 255))
    return b


def d_steel_safe(t):
    b = new_base()
    box = L()
    ImageDraw.Draw(box).rounded_rectangle([150, 130, 874, 900], radius=30, fill=255)
    paint(b, box, STEEL[0], STEEL[1], rim_k=0.6)
    door = L()
    ImageDraw.Draw(door).rounded_rectangle([210, 190, 814, 840], radius=20, fill=255)
    paint(b, door, (180, 210, 230), (50, 80, 105), rim_k=0.5, edge_w=8)
    dial = L()
    ImageDraw.Draw(dial).ellipse([300, 380, 560, 640], fill=255)
    paint(b, dial, (240, 250, 255), (80, 110, 130), rim_k=0.7)
    tk = L()
    dt = ImageDraw.Draw(tk)
    for k in range(24):
        a = math.radians(k * 15 + t * 360)
        dt.line([(430 + 100 * math.cos(a), 510 + 100 * math.sin(a)), (430 + 125 * math.cos(a), 510 + 125 * math.sin(a))], fill=255, width=6)
    flat(b, tk, (20, 30, 40))
    hd = L()
    ImageDraw.Draw(hd).rounded_rectangle([650, 400, 710, 640], radius=24, fill=255)
    paint(b, hd, (250, 255, 255), (90, 130, 150))
    for y in (250, 720):
        hg = L()
        ImageDraw.Draw(hg).rectangle([180, y, 240, y + 80], fill=255)
        paint(b, hg, (240, 250, 255), (90, 110, 130), edge_w=6)
    return b


def d_riveted_shield(t):
    b = new_base()
    sh = shield_mask(512, 90, 380)
    glow(b, sh, (92, 225, 255), 50, 0.9)
    paint(b, sh, STEEL[0], STEEL[1], rim_k=0.75)
    inner = shield_mask(512, 150, 320)
    paint(b, inner, (160, 200, 225), (40, 70, 100), rim_k=0.4, edge_w=6)
    band = L()
    ImageDraw.Draw(band).rectangle([470, 150, 554, 800], fill=255)
    band = ImageChops.multiply(band, inner)
    paint(b, band, STEEL[0], STEEL[1], edge_w=4)
    riv = L()
    dr = ImageDraw.Draw(riv)
    for k in range(9):
        y = 180 + k * 70
        dr.ellipse([512 - 14, y - 14, 512 + 14, y + 14], fill=255)
    for (x, y) in ((190, 170), (834, 170), (190, 450), (834, 450), (330, 690), (694, 690)):
        dr.ellipse([x - 20, y - 20, x + 20, y + 20], fill=255)
    paint(b, riv, (255, 255, 255), (110, 140, 160), edge_w=4)
    boss = L()
    ImageDraw.Draw(boss).ellipse([432, 380, 592, 540], fill=255)
    paint(b, boss, (255, 255, 255), (90, 130, 150), rim_k=0.8)
    return b


def d_blast_door(t):
    b = new_base()
    gap = 70 * (0.5 + 0.5 * math.cos(2 * math.pi * t))
    frame = L()
    ImageDraw.Draw(frame).rectangle([90, 80, 934, 960], fill=255)
    paint(b, frame, (60, 80, 95), (14, 20, 26))
    light = L()
    ImageDraw.Draw(light).rectangle([512 - gap / 2, 120, 512 + gap / 2, 920], fill=255)
    glow(b, light, (92, 225, 255), 40, 1.2)
    flat(b, light, (180, 250, 255))
    for side in (-1, 1):
        h = L()
        x0, x1 = (130, 512 - gap / 2) if side < 0 else (512 + gap / 2, 894)
        ImageDraw.Draw(h).rectangle([x0, 120, x1, 920], fill=255)
        paint(b, h, STEEL[0], STEEL[1], rim_k=0.6, edge_w=8)
        hz = L()
        dz = ImageDraw.Draw(hz)
        ex = x1 if side < 0 else x0
        for y in range(120, 920, 80):
            dz.polygon([(ex - side * 0, y), (ex - side * 70, y + 40), (ex - side * 70, y + 80), (ex, y + 40)], fill=255)
        dz.rectangle([min(ex, ex - side * 70), 120, max(ex, ex - side * 70), 920], outline=0)
        hz = ImageChops.multiply(hz, h)
        flat(b, hz, (20, 26, 30), 0.9)
        rv = L()
        dr = ImageDraw.Draw(rv)
        for y in range(170, 900, 90):
            for x in (x0 + 40, (x0 + x1) / 2):
                dr.ellipse([x - 13, y - 13, x + 13, y + 13], fill=255)
        paint(b, rv, (255, 255, 255), (110, 140, 160), edge_w=4)
    return b


def lock_shape(b, cx, y0, w, t, password=False):
    sh = L()
    lift = 30 * max(0.0, math.sin(2 * math.pi * t)) if not password else 0
    ImageDraw.Draw(sh).arc([cx - w * 0.36, y0 - lift, cx + w * 0.36, y0 + w * 0.72 - lift], 180, 360, fill=255, width=int(w * 0.13))
    d2 = ImageDraw.Draw(sh)
    d2.rectangle([cx - w * 0.36, y0 + w * 0.36 - lift, cx - w * 0.36 + w * 0.13, y0 + w * 0.6], fill=255)
    d2.rectangle([cx + w * 0.36 - w * 0.13, y0 + w * 0.36 - lift, cx + w * 0.36, y0 + w * 0.6], fill=255)
    paint(b, sh, (240, 250, 255), (90, 120, 140), rim_k=0.7)
    body = L()
    ImageDraw.Draw(body).rounded_rectangle([cx - w / 2, y0 + w * 0.52, cx + w / 2, y0 + w * 1.22], radius=int(w * 0.08), fill=255)
    glow(b, body, (92, 225, 255), 40, 0.7)
    paint(b, body, STEEL[0], STEEL[1], rim_k=0.65)
    return body


def d_padlock_password(t):
    b = new_base()
    body = lock_shape(b, 512, 60, 660, t, password=True)
    fld = L()
    ImageDraw.Draw(fld).rounded_rectangle([250, 560, 774, 760], radius=24, fill=255)
    paint(b, fld, (20, 40, 56), (8, 16, 24), rim=(120, 230, 255), rim_k=0.6, edge_w=6)
    n = 3 if (int(t * 24) % 8) < 6 else 2
    tx = text_mask("*" * n + ("_" if n < 3 else ""), 512, 690, 230)
    glow(b, tx, (92, 225, 255), 18, 1.4)
    flat(b, tx, (220, 250, 255))
    return b


def d_padlock(t):
    b = new_base()
    body = lock_shape(b, 512, 80, 700, t)
    kh = L()
    d = ImageDraw.Draw(kh)
    d.ellipse([462, 560, 562, 660], fill=255)
    d.polygon([(482, 640), (542, 640), (562, 790), (462, 790)], fill=255)
    flat(b, kh, (8, 14, 20))
    return b


def u_anon_mask(t):
    """Original anonymous theatre mask: smooth face, slanted slits, cheek bars, thin smile, crack."""
    b = new_base()
    m = L()
    d = ImageDraw.Draw(m)
    d.ellipse([230, 110, 794, 760], fill=255)
    d.polygon([(260, 500), (764, 500), (640, 900), (512, 950), (384, 900)], fill=255)
    glow(b, m, (190, 120, 255), 60, 0.9)
    paint(b, m, (250, 250, 255), (150, 160, 190), rim=(255, 255, 255), rim_k=0.5, shade_k=0.45)
    cut = L()
    dc = ImageDraw.Draw(cut)
    for sx in (-1, 1):
        dc.polygon([(512 + sx * 60, 420), (512 + sx * 230, 360), (512 + sx * 250, 400), (512 + sx * 80, 450)], fill=255)
    flat(b, cut, (14, 8, 24))
    eye_glow = cut.filter(ImageFilter.MinFilter(7))
    glow(b, eye_glow, (123, 224, 123), 14, 1.4)
    flat(b, eye_glow, (160, 255, 160))
    marks = L()
    dm = ImageDraw.Draw(marks)
    for sx in (-1, 1):
        for k in range(2):
            x = 512 + sx * (190 + k * 34)
            dm.line([(x, 500), (x - sx * 10, 640)], fill=255, width=16)
    dm.arc([392, 640, 632, 780], 20, 160, fill=255, width=12)
    dm.line([(392, 690), (360, 660)], fill=255, width=12)
    dm.line([(632, 690), (664, 660)], fill=255, width=12)
    for sx in (-1, 1):
        dm.arc([512 + sx * 150 - 120, 270, 512 + sx * 150 + 120, 380], 200 if sx < 0 else 250, 290 if sx < 0 else 340, fill=255, width=12)
    flat(b, marks, (110, 60, 170))
    cr = L()
    ImageDraw.Draw(cr).line([(600, 130), (640, 230), (610, 300), (660, 380)], fill=255, width=9)
    flat(b, cr, (40, 30, 60))
    k = int(t * 24)
    if k % 5 in (1, 2):  # glitch slices
        for y, dx in ((300 + (k * 53) % 300, 40), (600 + (k * 31) % 200, -30)):
            b[y:y + 36] = np.roll(b[y:y + 36], dx, axis=1)
            b[y:y + 36, :, 0] *= 0.6
    return b


def u_cloud(t):
    b = new_base()
    sl = L()
    d = ImageDraw.Draw(sl)
    for k, y in enumerate((380, 480, 580)):
        x0 = 60 + ((t * 300 + k * 90) % 200)
        d.rounded_rectangle([x0, y, x0 + 220, y + 22], radius=11, fill=255)
    flat(b, sl, (180, 255, 180), 0.8)
    cm = cloud_mask(580, 480, 330)
    glow(b, cm, (123, 224, 123), 50, 0.8)
    paint(b, cm, (240, 255, 240), (90, 170, 120), rim_k=0.5)
    return b


def u_key(t):
    b = new_base()
    km = L()
    d = ImageDraw.Draw(km)
    d.ellipse([90, 290, 450, 650], fill=255)
    d.rectangle([420, 430, 930, 510], fill=255)
    for x, h in ((700, 120), (790, 80), (870, 140)):
        d.rectangle([x, 500, x + 50, 500 + h], fill=255)
    d.ellipse([190, 390, 350, 550], fill=0)
    km = km.rotate(25, center=(512, 512), resample=Image.BICUBIC)
    glow(b, km, (123, 224, 123), 50, 0.9)
    paint(b, km, (230, 255, 200), (60, 140, 70), rim=(255, 255, 230), rim_k=0.7)
    sp = (0.5 + 0.5 * math.sin(2 * math.pi * t))
    spark(b, 300, 330, 60 * (0.4 + 0.6 * sp), t)
    return b


def u_fingerprint(t):
    b = new_base()
    m = L()
    d = ImageDraw.Draw(m)
    rng = np.random.default_rng(4)
    for k in range(11):
        rx, ry = 60 + k * 32, 90 + k * 38
        a0 = rng.integers(0, 60)
        d.arc([512 - rx, 520 - ry, 512 + rx, 520 + ry], 180 + a0, 360 + 160 - a0 * 0.5, fill=255, width=16)
    glow(b, m, (123, 224, 123), 30, 1.0)
    paint(b, m, (220, 255, 210), (60, 150, 80), edge_w=5, rim_k=0.4)
    y = 140 + ((t * 2) % 1.0) * 760
    sc = L()
    ImageDraw.Draw(sc).rectangle([100, y, 924, y + 14], fill=255)
    glow(b, sc, (180, 255, 180), 20, 1.2)
    flat(b, sc, (230, 255, 230))
    return b


def u_chip_repair(t):
    b = new_base()
    chip(b, 270, 270, 754, 754)
    cr = L()
    pts = [(300, 420), (420, 470), (380, 560), (520, 600), (480, 680), (720, 700)]
    ImageDraw.Draw(cr).line(pts, fill=255, width=16)
    flat(b, cr, (8, 8, 10))
    prog = (t * 1.25) % 1.0
    n = max(2, int(len(pts) * prog) + 1)
    fx = L()
    ImageDraw.Draw(fx).line(pts[:n], fill=255, width=10)
    glow(b, fx, (123, 255, 140), 20, 1.4)
    flat(b, fx, (200, 255, 210))
    spark(b, pts[n - 1][0], pts[n - 1][1], 60, t)
    return b


def u_magnifier_static(t):
    b = new_base()
    hd = L()
    ImageDraw.Draw(hd).line([(640, 640), (900, 900)], fill=255, width=90)
    paint(b, hd, (120, 120, 130), (30, 30, 36))
    lens = L()
    ImageDraw.Draw(lens).ellipse([170, 170, 690, 690], fill=255)
    vgrid_static(b, lens, 3, t, 0.75)
    ring = L()
    ImageDraw.Draw(ring).ellipse([150, 150, 710, 710], outline=255, width=56)
    paint(b, ring, GREY[0], GREY[1], rim_k=0.7)
    gl = L()
    ImageDraw.Draw(gl).arc([230, 230, 610, 610], 200, 250, fill=255, width=22)
    flat(b, gl, (255, 255, 255), 0.7)
    return b


def u_unplugged_chip(t):
    b = new_base()
    chip(b, 160, 300, 560, 700, top=(90, 90, 98), bot=(24, 24, 28))
    cab = L()
    ImageDraw.Draw(cab).line([(1024, 880), (860, 760), (780, 600)], fill=255, width=40, joint="curve")
    paint(b, cab, (90, 90, 96), (30, 30, 34), edge_w=8)
    plug = L()
    ImageDraw.Draw(plug).rounded_rectangle([700, 470, 860, 620], radius=20, fill=255)
    paint(b, plug, GREY[0], GREY[1])
    pr = L()
    dp = ImageDraw.Draw(pr)
    dp.rectangle([720, 420, 750, 470], fill=255)
    dp.rectangle([810, 420, 840, 470], fill=255)
    paint(b, pr, (230, 220, 170), (140, 120, 70), edge_w=4)
    z = text_mask("z z", 780, 280, 120)
    flat(b, z, (150, 150, 160), 0.7)
    return b


def u_magnifier_code(t):
    b = new_base()
    hd = L()
    ImageDraw.Draw(hd).line([(640, 640), (900, 900)], fill=255, width=90)
    paint(b, hd, (120, 200, 130), (30, 70, 40))
    lens = L()
    ImageDraw.Draw(lens).ellipse([170, 170, 690, 690], fill=255)
    code = L()
    dc = ImageDraw.Draw(code)
    f = font("consolab.ttf", 46)
    rng = np.random.default_rng(9)
    off = int(t * 60) % 60
    for k in range(10):
        s = "".join(rng.choice(list("0123456789ABCDEF")) for _ in range(12))
        dc.text((190, 170 + k * 60 - off), s, font=f, fill=255)
    code = ImageChops.multiply(code, lens)
    flat(b, lens, (10, 30, 14), 0.9)
    glow(b, code, (123, 224, 123), 10, 1.0)
    flat(b, code, (190, 255, 190))
    ring = L()
    ImageDraw.Draw(ring).ellipse([150, 150, 710, 710], outline=255, width=56)
    paint(b, ring, GREEN[0], GREEN[1], rim_k=0.7)
    return b


def u_debug_bug(t):
    b = new_base()
    legs = L()
    d = ImageDraw.Draw(legs)
    for sx in (-1, 1):
        for y in (460, 580, 700):
            d.line([(512, y), (512 + sx * 330, y - 40), (512 + sx * 380, y + 40)], fill=255, width=26, joint="curve")
    paint(b, legs, (80, 140, 90), (20, 50, 30), edge_w=6)
    body = L()
    db = ImageDraw.Draw(body)
    db.ellipse([320, 370, 704, 890], fill=255)
    db.ellipse([410, 250, 614, 420], fill=255)
    paint(b, body, (200, 255, 180), (40, 120, 60), rim_k=0.6)
    tx = text_mask("</>", 512, 640, 200)
    flat(b, tx, (20, 50, 30))
    return b


def u_password(t):
    b = new_base()
    win = L()
    ImageDraw.Draw(win).rounded_rectangle([110, 250, 914, 780], radius=30, fill=255)
    paint(b, win, (60, 90, 70), (16, 30, 20), rim=(180, 255, 180), rim_k=0.6)
    bar = L()
    ImageDraw.Draw(bar).rectangle([130, 270, 894, 340], fill=255)
    flat(b, bar, (123, 224, 123), 0.8)
    fld = L()
    ImageDraw.Draw(fld).rounded_rectangle([190, 450, 834, 640], radius=20, fill=255)
    flat(b, fld, (8, 16, 10))
    n = 1 + int(t * 4) % 4
    tx = text_mask("*" * n + "_", 512, 560, 200)
    glow(b, tx, (123, 224, 123), 16, 1.3)
    flat(b, tx, (220, 255, 220))
    return b


# ----------------------------------------------------------------- registry
ART = {
    # attack
    "flaming_skull": (a_flaming_skull, "attack"), "fire": (a_fire, "attack"), "bomb": (a_bomb, "attack"),
    "skull": (a_skull, "attack"), "skull_fuse": (a_skull_fuse, "attack"), "crossbones": (a_crossbones, "attack"),
    "poison_vial": (a_poison_vial, "attack"), "bio_bug": (a_bio_bug, "attack"), "storm_cloud": (a_storm_cloud, "attack"),
    "trojan_horse": (a_trojan_horse, "attack"), "envelope_bomb": (a_envelope_bomb, "attack"),
    "phish_hook": (a_phish_hook, "attack"), "hook_password": (a_hook_password, "attack"),
    # defence
    "burning_wall": (d_burning_wall, "defence"), "wall_shield": (d_wall_shield, "defence"),
    "vault_door": (d_vault_door, "defence"), "steel_safe": (d_steel_safe, "defence"),
    "riveted_shield": (d_riveted_shield, "defence"), "blast_door": (d_blast_door, "defence"),
    "padlock_password": (d_padlock_password, "defence"), "padlock": (d_padlock, "defence"),
    # utility
    "anon_mask": (u_anon_mask, "utility"), "cloud": (u_cloud, "utility"), "key": (u_key, "utility"),
    "fingerprint": (u_fingerprint, "utility"), "chip_repair": (u_chip_repair, "utility"),
    "magnifier_static": (u_magnifier_static, "utility"), "unplugged_chip": (u_unplugged_chip, "utility"),
    "magnifier_code": (u_magnifier_code, "utility"), "debug_bug": (u_debug_bug, "utility"), "password": (u_password, "utility"),
}
CAT_GLOW = {"attack": (255, 60, 110), "defence": (92, 225, 255), "utility": (123, 224, 123)}
PRIMARY = {"EXPLOIT": "flaming_skull", "ZERO-DAY": "skull", "VIRUS": "poison_vial", "TROJAN": "trojan_horse",
           "FIREWALL": "burning_wall", "SANDBOX": "vault_door", "PROXY": "anon_mask", "PATCH": "key",
           "NULL": "magnifier_static"}
SPECIAL_ART = {"tariff": "phish_hook", "dose": "poison_vial", "citation": "padlock", "solar_flare": "storm_cloud"}

_cache = {}


def art(name, S, t):
    key = (name, S, int(t * 24))
    if key not in _cache:
        f, cat = ART[name]
        arr = f(t)
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGBA")
        _cache[key] = im.resize((S, S), Image.LANCZOS)
        if len(_cache) > 400:
            _cache.clear()
    return _cache[key]


def screen(ctx, base_im):
    """Compose the splash art into the slice screen: dimmed program screen + glow + bold art."""
    o = getattr(ctx, "opts", {}) or {}
    amap = o.get("art_map") or {}
    name = None
    if getattr(ctx, "special", None):
        name = SPECIAL_ART.get(ctx.special)
    name = name or amap.get(ctx.prog) or PRIMARY.get(ctx.prog)
    if not name:
        return base_im
    cat = ART[name][1]
    W, H = base_im.size
    arr = np.asarray(base_im, np.float32) / 255 * 0.30
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.45
    g = np.exp(-(((xx - cx) / (W * 0.45)) ** 2 + ((yy - cy) / (H * 0.55)) ** 2))[..., None]
    gc = np.array(CAT_GLOW[cat] if ctx.prog != "NULL" else (150, 150, 160), np.float32) / 255
    if ctx.theme in CORPS:
        gc = gc * 0.4 + np.array(CORPS[ctx.theme]["col"], np.float32) / 255 * 0.6
    arr = arr + g * gc * 0.35
    S = int(min(H * 1.02, W * 0.95))
    a = art(name, S, ctx.t)
    aa = np.asarray(a, np.float32) / 255
    if ctx.theme in CORPS:  # tint the art toward the corp colour
        cc = np.array(CORPS[ctx.theme]["col"], np.float32) / 255
        lum = aa[..., :3].max(axis=2, keepdims=True)
        aa[..., :3] = aa[..., :3] * 0.55 + lum * cc * 0.45
    x0, y0 = int(cx - S / 2), int(cy - S / 2)
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(W, x0 + S), min(H, y0 + S)
    sub = aa[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
    al = sub[..., 3:]
    arr[ys0:ys1, xs0:xs1] = arr[ys0:ys1, xs0:xs1] * (1 - al) + sub[..., :3] * al
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
