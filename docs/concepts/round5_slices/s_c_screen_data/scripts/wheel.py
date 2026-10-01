"""Wheel assembly: back plate, slices, bezel ring, hub, pointer, HP arc, frame."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import (R_OUT, R_IN, TICK_DEG, PROGRAMS, MERIDIAN, MERIDIAN_DIM, render_slice, paste_rgba,
                      f_num, f_ui, f_mono, glyph_rgba, bloom, c01, smooth, to_img)

PLAYER_LAYOUT = [("EXPLOIT", 4, 6), ("ZERO-DAY", 2, 12), ("PROXY", 3, 4), ("PATCH", 3, 3), ("VIRUS", 4, 3),
                 ("TROJAN", 3, 2), ("NULL", 3, None), ("FIREWALL", 4, 5), ("SANDBOX", 4, 8)]
ENEMY_LAYOUT = [("EXPLOIT", 3, 6), ("PROXY", 3, 3), ("VIRUS", 3, 4), ("EXPLOIT", 3, 9), ("FIREWALL", 3, 6),
                ("ZERO-DAY", 2, 14), ("NULL", 3, None), ("EXPLOIT", 4, 8), ("SANDBOX", 3, 6), ("PATCH", 3, 4)]

PINK = (255, 61, 168)
HP_GREEN = (123, 224, 123)

CW, CH = 960, 1010  # wheel canvas (master px)
CX, CY = 480, 470


def _rings(canvas, ss, theme):
    H, W = canvas.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx + 0.5 - CX * ss, yy + 0.5 - CY * ss
    rho = np.hypot(dx, dy) / ss
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    rgb = np.zeros((H, W, 3), np.float32)
    a = np.zeros((H, W, 1), np.float32)

    def over(col, alpha):
        nonlocal rgb, a
        al = np.clip(alpha, 0, 1)[..., None]
        rgb = rgb * (1 - al) + np.asarray(col, np.float32) * al
        a = a * (1 - al) + al

    # back plate under the slices (shows in the gaps)
    over([0.025, 0.022, 0.035], np.clip(R_OUT + 3 - rho, 0, 1))
    # outer bezel ring
    R0, R1 = R_OUT + 1, R_OUT + 40
    ring = np.clip(rho - R0, 0, 1) * np.clip(R1 - rho, 0, 1)
    u = (rho - R0) / (R1 - R0)
    light = 0.8 + 0.35 * np.cos(np.radians(th - 315))
    if theme == "player":
        base = np.array([0.07, 0.06, 0.09], np.float32)
        acc = c01(PINK)
        col = base[None, None] * (0.7 + 0.6 * np.sin(np.pi * u))[..., None] * light[..., None]
    else:
        rng = np.random.default_rng(5)
        brushed = (rng.random(720).astype(np.float32) * 0.08)[(th * 2).astype(np.int32) % 720]
        base = np.array([0.17, 0.175, 0.19], np.float32)
        acc = c01(MERIDIAN)
        col = (base[None, None] * (0.75 + 0.45 * np.sin(np.pi * u))[..., None] + brushed[..., None]) * light[..., None]
    rgb = rgb * (1 - ring[..., None]) + col * ring[..., None]
    a = np.maximum(a, ring[..., None])
    # neon / hairline rims
    for r, w, k in ((R1 - 1.5, 1.6, 1.3), (R0 + 1.5, 1.0, 0.7)):
        g = np.exp(-((rho - r) / w) ** 2) * k
        rgb = rgb + g[..., None] * acc
        a = np.maximum(a, np.clip(g, 0, 1)[..., None])
    # tick marks: 30 ticks
    tk = (th % TICK_DEG)
    tk = np.minimum(tk, TICK_DEG - tk) * np.pi / 180 * rho
    tick = np.clip(1.2 - tk, 0, 1) * ((rho > R0 + 22) & (rho < R0 + 32))
    tcol = np.array([0.8, 0.8, 0.85], np.float32) if theme == "player" else acc
    rgb = rgb + tick[..., None] * tcol * 0.6
    canvas[..., :3] = canvas[..., :3] * (1 - a) + rgb * a  # rgb is straight colour
    canvas[..., 3:] = np.maximum(canvas[..., 3:], a)
    return rho, th


def _hub(canvas, ss, theme, name, sub):
    R = R_IN - 4
    S = int((R * 2 + 20) * ss)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    acc = PINK if theme == "player" else MERIDIAN
    fill = (14, 12, 20) if theme == "player" else (18, 20, 24)
    d.ellipse([c - R * ss, c - R * ss, c + R * ss, c + R * ss], fill=fill + (255,), outline=acc + (255,), width=int(2.5 * ss))
    for rr in range(20, int(R) - 6, 9):
        d.ellipse([c - rr * ss, c - rr * ss, c + rr * ss, c + rr * ss], outline=(255, 255, 255, 10), width=ss)
    if theme == "player":
        # terminal-prompt badge
        bw, bh = 46 * ss, 34 * ss
        d.rounded_rectangle([c - bw / 2, c - 78 * ss, c + bw / 2, c - 78 * ss + bh], radius=5 * ss, outline=acc + (255,), width=int(2 * ss))
        fm = f_mono(20 * ss)
        d.text((c - 15 * ss, c - 75 * ss), ">_", font=fm, fill=acc + (255,))
    else:
        # Meridian mark: three stacked chevrons in a hexagon
        r = 20 * ss
        hx = [(c + r * math.cos(math.radians(60 * i + 30)), c - 62 * ss + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
        d.polygon(hx, outline=acc + (255,), width=int(2 * ss))
        for k in range(3):
            y = c - 72 * ss + k * 7 * ss
            d.line([(c - 9 * ss, y + 6 * ss), (c, y), (c + 9 * ss, y + 6 * ss)], fill=acc + (255,), width=int(2 * ss))
    lines = name.split("\n")
    fb = f_num(30 * ss)
    y = c - (12 if len(lines) == 1 else 26) * ss
    for ln in lines:
        w = fb.getlength(ln)
        d.text((c - w / 2, y), ln, font=fb, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
        y += 30 * ss
    fs = f_ui(13 * ss)
    w = fs.getlength(sub)
    d.text((c - w / 2, y + 10 * ss), sub, font=fs, fill=(200, 200, 210, 255))
    paste_rgba(canvas, im, CX * ss - S / 2, CY * ss - S / 2)


def _pointer(canvas, ss, theme):
    S = 120 * ss
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    tip = 112 * ss
    acc = PINK if theme == "player" else MERIDIAN
    pts = [(c - 11 * ss, 30 * ss), (c + 11 * ss, 30 * ss), (c, tip)]
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(pts, fill=acc + (200,))
    glow = glow.filter(ImageFilter.GaussianBlur(6 * ss))
    im.alpha_composite(glow)
    d.polygon(pts, fill=(245, 245, 250, 255), outline=(10, 8, 16, 255), width=int(2.5 * ss))
    d.line([(c, 34 * ss), (c, tip - 10 * ss)], fill=(170, 170, 185, 255), width=int(2 * ss))
    d.ellipse([c - 14 * ss, 6 * ss, c + 14 * ss, 34 * ss], fill=(60, 60, 72, 255), outline=(10, 8, 16, 255), width=int(2.5 * ss))
    d.ellipse([c - 6 * ss, 12 * ss, c + 1 * ss, 19 * ss], fill=(200, 200, 210, 255))
    paste_rgba(canvas, im, CX * ss - S / 2, (CY - R_OUT - 80) * ss)


def _hp(canvas, ss, hp, hpmax):
    S = canvas.shape
    im = Image.new("RGBA", (S[1], S[0]), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = 30
    a0, a1 = 128, 232
    r0, r1 = (R_OUT + 52) * ss, (R_OUT + 78) * ss
    for i in range(n):
        aa = a0 + (a1 - a0) * (i + 0.12) / n
        ab = a0 + (a1 - a0) * (i + 0.88) / n
        on = i < round(n * hp / hpmax)
        col = HP_GREEN if on else (40, 60, 44)
        pts = []
        for r, ang in ((r0, aa), (r1, aa), (r1, ab), (r0, ab)):
            pts.append((CX * ss + r * math.sin(math.radians(ang)), CY * ss - r * math.cos(math.radians(ang))))
        d.polygon(pts, fill=col + (255,))
    txt = "%d/%d" % (hp, hpmax)
    f = f_num(62 * ss)
    w = f.getlength(txt)
    d.text((CX * ss - w / 2, (CY + R_OUT + 80) * ss), txt, font=f, fill=HP_GREEN + (255,), stroke_width=int(2 * ss), stroke_fill=(8, 20, 10, 255))
    paste_rgba(canvas, im, 0, 0)


def render_wheel(layout, theme="player", t=0.0, ss=2, opts=None, name="GHOST.CELL", sub="operative core",
                 hp=(60, 60), start=None, t_offsets=True):
    canvas = np.zeros((CH * ss, CW * ss, 4), np.float32)
    _rings(canvas, ss, theme)
    total = sum(s for _, s, _ in layout)
    assert total == 30, total
    a = -layout[0][1] * TICK_DEG / 2 if start is None else start
    for i, (p, ticks, val) in enumerate(layout):
        span = ticks * TICK_DEG
        tt = (t + (i * 0.137 if t_offsets else 0)) % 1.0
        render_slice(canvas, CX * ss, CY * ss, p, a, span, val, tt, theme, ss, opts, seed=i)
        a += span
    _hub(canvas, ss, theme, name, sub)
    _pointer(canvas, ss, theme)
    if hp:
        _hp(canvas, ss, *hp)
    rgba = (np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    return im.resize((CW, CH), Image.LANCZOS)


# ----------------------------------------------------------------- frame
def background(W=1920, H=1080, tint=(255, 61, 168), seed=3, tint2=(92, 225, 255)):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.zeros((H, W, 3), np.float32)
    top = np.array([0.055, 0.045, 0.075], np.float32)
    bot = np.array([0.02, 0.02, 0.03], np.float32)
    g += top + (bot - top) * (yy / H)[..., None]
    im = to_img(g)
    rng = np.random.default_rng(seed)
    city = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(city)
    x = 0
    while x < W:
        bw = int(rng.integers(80, 220))
        bh = int(rng.integers(250, 650))
        d.rectangle([x, H - bh, x + bw, H], fill=(14, 13, 20))
        for wy in range(H - bh + 20, H, 26):
            for wx in range(x + 12, x + bw - 12, 22):
                if rng.random() < 0.28:
                    c = (60, 55, 80) if rng.random() < 0.8 else (90, 70, 40)
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=c)
        x += bw + int(rng.integers(6, 30))
    city = city.filter(ImageFilter.GaussianBlur(5))
    im = Image.fromarray(np.clip(np.asarray(im, np.float32) + np.asarray(city, np.float32) * 0.8, 0, 255).astype(np.uint8))
    return im


def caption(im, title, sub, accent=PINK):
    d = ImageDraw.Draw(im)
    W, H = im.size
    f1 = f_num(40)
    f2 = f_mono(19, bold=False)
    w = max(f1.getlength(title), f2.getlength(sub)) + 40
    d.rectangle([0, H - 88, w, H], fill=(8, 8, 12))
    d.rectangle([0, H - 88, 6, H], fill=accent)
    d.text((22, H - 84), title, font=f1, fill=(255, 255, 255))
    d.text((22, H - 34), sub, font=f2, fill=(200, 200, 210))


def glow_behind(im, cx, cy, r, col, k=0.22):
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None] * c01(col) * k
    arr = np.asarray(im, np.float32) / 255 + g
    return to_img(arr)
