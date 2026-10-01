"""Wheel assembly for the CIRCUIT BOARD family: tiles -> rotated wheel, PCB bezel
(gold edge-connector fingers) or Meridian machined bezel, chip hub, pointer, HP arc,
city backdrop, bloom, caption."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from circ_lib import (F_NUM, F_SILK, F_SUB, MERIDIAN, R_IN, R_OUT, blur, glyph_masks, hexc, render_tile,
                      smooth, tonemap, dilate)

PINK = hexc("#FF3DA8")
HP_GREEN = hexc("#7BE07B")


def np_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def to_np(im):
    return np.asarray(im, np.float32) / 255.0


# ----------------------------------------------------------------------------- backdrop
def backdrop(w=1920, h=1080, seed=4, tint=(0.07, 0.035, 0.09)):
    rng = random.Random(seed)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    base = np.zeros((h, w, 3), np.float32)
    base += np.array(tint, np.float32) * (1.1 - yy * 0.7)[..., None]
    city = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(city)
    x = -20
    while x < w:
        bw = rng.randint(60, 190)
        bh = rng.randint(180, 560)
        top = h - bh
        shade = rng.randint(14, 24)
        d.rectangle([x, top, x + bw, h], fill=(shade, shade - 4, shade + 6))
        for wy in range(top + 14, h - 10, 22):
            for wx in range(x + 8, x + bw - 10, 18):
                if rng.random() < 0.28:
                    c = rng.choice([(70, 60, 90), (90, 70, 60), (50, 80, 100), (100, 50, 90)])
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=c)
        x += bw + rng.randint(4, 30)
    c = to_np(city)
    c = blur(c, 5.0)
    base = base + c * 0.85
    # vignette
    X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    v = 1 - 0.55 * np.clip((X ** 2 * 0.7 + Y ** 2) - 0.2, 0, 1)
    return base * v[..., None]


# ----------------------------------------------------------------------------- polar helpers
class Polar:
    def __init__(self, size, ss):
        self.size = size
        self.ss = ss
        self.C = size / 2.0
        ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
        dx = xs + 0.5 - self.C
        dy = ys + 0.5 - self.C
        self.dx, self.dy = dx, dy
        self.rr = np.hypot(dx, dy) / ss          # master px
        self.ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360   # clockwise from up

    def band(self, r0, r1, aa=0.7):
        return smooth(r0 - aa, r0 + aa, self.rr) * (1 - smooth(r1 - aa, r1 + aa, self.rr))


def light_shade(H, ss, k=1.2):
    gy, gx = np.gradient(H)
    nx, ny, nz = -gx * k / ss, -gy * k / ss, np.ones_like(H)
    nn = np.sqrt(nx * nx + ny * ny + nz * nz)
    lx, ly, lz = -0.45, -0.45, 0.77
    ndl = (nx * lx + ny * ly + nz * lz) / nn
    spec = np.clip(((nx * lx + ny * ly + nz * (lz + 1)) / nn) / math.sqrt(lx * lx + ly * ly + (lz + 1) ** 2), 0, 1) ** 30
    return np.clip(1 + 1.5 * (ndl - lz), 0.3, 1.9), spec


# ----------------------------------------------------------------------------- bezels
def bezel_player(P, col=PINK, ro=R_OUT):
    """Dark PCB ring with gold edge-connector fingers on every tick and a neon tube."""
    r0, r1 = ro + 2, ro + 38
    ring = P.band(r0, r1)
    prof = np.clip((P.rr - r0) / (r1 - r0), 0, 1)
    H = np.sin(prof * math.pi) * 4.0 * ring
    # fingers
    a = P.ang % 6.0
    fing = (np.abs(a - 3.0) < 1.25).astype(np.float32) * P.band(ro + 10, ro + 29)
    fing = blur(fing, 0.5 * P.ss)
    H = H + fing * 1.5
    shade, spec = light_shade(H, P.ss)
    sub = np.array([0.075, 0.05, 0.09], np.float32)
    rgb = sub[None, None, :] * shade[..., None] * ring[..., None]
    gold = np.array([0.85, 0.66, 0.30], np.float32)
    rgb = rgb * (1 - fing[..., None]) + (gold * shade[..., None] * 0.85 + spec[..., None] * 0.9) * fing[..., None]
    # silkscreen tick numbers ring + inner lip
    lip = P.band(ro - 1, ro + 3)
    rgb = rgb * (1 - lip[..., None]) + np.array([0.02, 0.015, 0.03]) * lip[..., None]
    # tick notches (30)
    tick = (np.abs((P.ang % 12.0) - 6.0) > 5.6).astype(np.float32) * P.band(ro + 3, ro + 9)
    rgb += tick[..., None] * col * 0.8
    # neon tube on the outer edge
    tube = P.band(ro + 35, ro + 39.5)
    core = P.band(ro + 36.6, ro + 37.8)
    em = tube[..., None] * col * 1.1 + core[..., None] * 0.6
    alpha = np.clip(ring + tube, 0, 1)
    return rgb, em, alpha


def bezel_enemy(P, ro=R_OUT):
    """Meridian: machined orange ring, container stripes, notched hostile edge."""
    r0, r1 = ro + 2, ro + 42
    # notches: every 12 degrees a 3-degree cut 7px deep
    notch = (np.abs((P.ang % 12.0) - 6.0) < 1.6) & (P.rr > r1 - 8)
    ring = P.band(r0, r1) * (~notch)
    prof = np.clip((P.rr - r0) / (r1 - r0), 0, 1)
    H = (np.minimum(prof, 1 - prof) * 2).clip(0, 0.25) * 16 * ring
    shade, spec = light_shade(blur(H, 0.8 * P.ss), P.ss)
    lathe = 1 + 0.06 * np.sin(P.rr * 2.2) + 0.04 * np.sin(P.rr * 0.7)
    metal = MERIDIAN * 0.55 + 0.04
    rgb = metal[None, None, :] * (shade * lathe)[..., None] + spec[..., None] * 0.7
    # container stripes in the middle band (45 deg in the ring's local frame)
    arc = np.radians(P.ang) * P.rr
    st_band = P.band(ro + 12, ro + 28)
    stripe = ((arc + P.rr) % 14.0 < 7.0).astype(np.float32)
    stripe = blur(stripe, 0.5 * P.ss)
    dark = np.array([0.05, 0.04, 0.035], np.float32)
    rgb = rgb * (1 - st_band[..., None]) + st_band[..., None] * (dark * (1 - stripe[..., None]) + (MERIDIAN * 0.9 * shade[..., None]) * stripe[..., None])
    lip = P.band(ro - 1, ro + 3)
    rgb = rgb * (1 - lip[..., None]) + np.array([0.02, 0.015, 0.012]) * lip[..., None]
    rgb *= ring[..., None]
    tube = P.band(ro + 3, ro + 5.5)
    edge = P.band(r1 - 1.5, r1 + 1.0) * (~notch)
    em = tube[..., None] * MERIDIAN * 0.9 + edge[..., None] * MERIDIAN * 0.7
    alpha = np.clip(ring + tube, 0, 1)
    return rgb, em, alpha


# ----------------------------------------------------------------------------- hub
def hub(P, name, sub, col, ri=R_IN, corp=False, glyph=None):
    """The hub as a CPU package: pinned square die inside a dark disc."""
    ss = P.ss
    rd = ri - 4
    disc_m = P.band(-1, rd)
    base = np.array([0.04, 0.035, 0.05], np.float32) if not corp else np.array([0.05, 0.045, 0.04], np.float32)
    rings = 1 + 0.08 * np.sin(P.rr * 1.6)
    rgb = base[None, None, :] * rings[..., None] * disc_m[..., None]
    # die
    hs = ri * 0.56
    ax, ay = np.abs(P.dx / ss), np.abs(P.dy / ss)
    sq = smooth(hs + 0.7, hs - 0.7, np.maximum(ax, ay))
    # pins around the die
    pins = np.zeros_like(sq)
    pitch = 9.0
    for axis_a, axis_b in ((ax, P.dy / ss), (ay, P.dx / ss)):
        pm = (axis_a > hs + 2) & (axis_a < hs + 11) & (np.abs(((axis_b + 400) % pitch) - pitch / 2) < 2.0) & (np.abs(axis_b) < hs - 4)
        pins = np.maximum(pins, pm.astype(np.float32))
    pins = blur(pins, 0.4 * ss)
    gold = np.array([0.82, 0.64, 0.30], np.float32)
    rgb = rgb * (1 - pins[..., None]) + gold * 0.8 * pins[..., None]
    H = sq * 3.0
    shade, spec = light_shade(blur(H, 1.2 * ss), ss)
    die = np.array([0.065, 0.06, 0.075], np.float32)
    rgb = rgb * (1 - sq[..., None]) + (die * shade[..., None] + spec[..., None] * 0.25) * sq[..., None]
    rim = P.band(rd - 2.0, rd + 0.5)
    em = rim[..., None] * col * 1.0
    alpha = np.clip(disc_m + pins, 0, 1)
    # text on the die
    img = Image.new("L", (P.size, P.size), 0)
    img2 = Image.new("L", (P.size, P.size), 0)
    d = ImageDraw.Draw(img)
    d2 = ImageDraw.Draw(img2)
    C = P.C
    words = name.split(" ")
    if len(words) > 1:
        fs = int(26 * ss)
        f = ImageFont.truetype(F_NUM, fs)
        d.text((C, C + 2 * ss), "\n".join(words), font=f, anchor="mm", fill=255, align="center", spacing=int(2 * ss))
    else:
        f = ImageFont.truetype(F_NUM, int(38 * ss))
        d.text((C, C + 6 * ss), name, font=f, anchor="mm", fill=255)
    fs2 = ImageFont.truetype(F_SUB, int(11 * ss))
    d2.text((C, C + hs * ss - 12 * ss), sub, font=fs2, anchor="mm", fill=255)
    if glyph:
        gw, gi = glyph_masks(glyph, 30 * ss)
        hgt = gw.shape[0]
        y0 = int(C - hs * ss + 6 * ss)
        x0 = int(C - hgt / 2)
        g = np.zeros((P.size, P.size), np.float32)
        g[y0:y0 + hgt, x0:x0 + hgt] = gw
        em = em + g[..., None] * col * 0.9
    else:
        # pin-1 dot / status LED
        led = np.exp(-((P.dx / ss + hs - 9) ** 2 + (P.dy / ss + hs - 9) ** 2) / 6.0)
        em = em + led[..., None] * col * 1.4
    t1 = to_np(img)
    t2 = to_np(img2)
    rgb = rgb * (1 - t1[..., None]) + 0.97 * t1[..., None]
    rgb = rgb * (1 - t2[..., None]) + 0.62 * t2[..., None]
    return rgb, em, alpha


# ----------------------------------------------------------------------------- pointer / hp
def pointer(img, cx, top_y, tip_y, ss, col=(1.0, 1.0, 1.0)):
    d = ImageDraw.Draw(img, "RGBA")
    w = 7 * ss
    d.polygon([(cx - w, top_y + 10 * ss), (cx + w, top_y + 10 * ss), (cx + 1.5 * ss, tip_y), (cx - 1.5 * ss, tip_y)], fill=(40, 40, 46, 255))
    d.polygon([(cx - w + 2 * ss, top_y + 10 * ss), (cx, top_y + 10 * ss), (cx, tip_y)], fill=(210, 212, 220, 255))
    d.polygon([(cx, top_y + 10 * ss), (cx + w - 2 * ss, top_y + 10 * ss), (cx, tip_y)], fill=(130, 132, 142, 255))
    r = 13 * ss
    d.ellipse([cx - r, top_y - r, cx + r, top_y + r], fill=(56, 56, 64, 255))
    d.ellipse([cx - r * 0.75, top_y - r * 0.8, cx + r * 0.35, top_y + r * 0.2], fill=(110, 110, 120, 255))
    d.ellipse([cx - r * 0.5, top_y - r * 0.6, cx - r * 0.05, top_y - r * 0.2], fill=(200, 200, 210, 255))


def hp_arc(P, ro, frac=1.0, n=28, col=HP_GREEN):
    a0, a1 = 128.0, 232.0
    span = (a1 - a0) / n
    m = np.zeros_like(P.rr)
    for i in range(n):
        if i / n >= frac:
            break
        c = a0 + span * (i + 0.5)
        m = np.maximum(m, (np.abs(P.ang - c) < span * 0.36).astype(np.float32))
    m = m * P.band(ro + 54, ro + 72)
    return blur(m, 0.5 * P.ss)


# ----------------------------------------------------------------------------- wheel
def build_wheel(slices, t=0.0, ro=R_OUT, ri=R_IN, ss=2, enemy=False, hub_name="BREAKER",
                hub_sub="Breaker Core", bezel_col=PINK, pad=95, hp_frac=1.0, ts=None, start_tick=0,
                icon_scale=1.0):
    """slices: list of boards (ticks taken from board.W.ticks). Returns (rgb, alpha, emissive) at ss."""
    size = int(2 * (ro + pad) * ss)
    P = Polar(size, ss)
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tick = start_tick
    for i, b in enumerate(slices):
        n = b.W.ticks
        theta = (tick + n / 2.0) * 12.0
        tt = t if ts is None else ts[i]
        tile = render_tile(b, tt, light_rot=math.radians(theta), icon_scale=icon_scale)
        full = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        full.paste(tile, (int(round(P.C - b.W.cx)), int(round(P.C - b.W.cy))))
        full = full.rotate(-theta, resample=Image.BICUBIC, center=(P.C, P.C))
        layer.alpha_composite(full)
        tick += n
    wheel = to_np(layer)
    rgb = wheel[..., :3]
    alpha = wheel[..., 3]
    if enemy:
        brgb, bem, ba = bezel_enemy(P, ro)
        hrgb, hem, ha = hub(P, hub_name, hub_sub, MERIDIAN, ri, corp=True, glyph="crane")
    else:
        brgb, bem, ba = bezel_player(P, bezel_col, ro)
        hrgb, hem, ha = hub(P, hub_name, hub_sub, bezel_col, ri)
    em = bem + hem
    rgb = rgb * (1 - ba[..., None]) + brgb * ba[..., None]
    rgb = rgb * (1 - ha[..., None]) + hrgb * ha[..., None]
    alpha = np.clip(alpha + ba + ha, 0, 1)
    hp = hp_arc(P, ro, hp_frac)
    em = em + hp[..., None] * HP_GREEN * 1.2
    alpha = np.clip(alpha + hp, 0, 1)
    glow = blur(em, 3 * ss) * 0.9 + blur(em, 12 * ss) * 0.6
    rgb = rgb + em
    return rgb, alpha, glow, P


def place(frame, rgb, alpha, glow, cx, cy, ss):
    """downsample a wheel layer and composite it onto a 1x float frame (glow added)."""
    h, w = alpha.shape
    sz = (w // ss, h // ss)
    r = to_np(np_img(tonemap(np.clip(rgb, 0, 4))).resize(sz, Image.LANCZOS))
    a = to_np(np_img(alpha).resize(sz, Image.LANCZOS))
    g = np.asarray(Image.fromarray(np.clip(glow * 255, 0, 255).astype(np.uint8)).resize(sz, Image.BILINEAR), np.float32) / 255
    x0, y0 = int(cx - sz[0] / 2), int(cy - sz[1] / 2)
    H, Wd = frame.shape[:2]
    xs0, ys0, xs1, ys1 = max(0, x0), max(0, y0), min(Wd, x0 + sz[0]), min(H, y0 + sz[1])
    sl = (slice(ys0, ys1), slice(xs0, xs1))
    ls = (slice(ys0 - y0, ys1 - y0), slice(xs0 - x0, xs1 - x0))
    # drop shadow under the wheel
    sh = blur(a, 10)[ls] * 0.6
    frame[sl] *= (1 - sh[..., None])
    frame[sl] = frame[sl] * (1 - a[ls][..., None]) + r[ls] * a[ls][..., None]
    frame[sl] += g[ls]
    return frame


def bloom(frame, thr=0.72, k=0.35):
    b = np.clip(frame - thr, 0, None)
    return frame + (blur(b, 5) * 0.6 + blur(b, 18) * 0.5) * k / 0.35 * 0.35


def caption(img, title, sub, x=0, y=None, accent=(255, 61, 168)):
    d = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    y = H - 84 if y is None else y
    f1 = ImageFont.truetype(F_NUM, 30)
    f2 = ImageFont.truetype(F_SILK, 19)
    tw = max(d.textlength(title, font=f1), d.textlength(sub, font=f2)) + 40
    d.rectangle([x, y, x + tw, y + 84], fill=(8, 6, 12, 235))
    d.rectangle([x, y, x + 5, y + 84], fill=accent + (255,))
    d.text((x + 20, y + 10), title, font=f1, fill=(245, 245, 250))
    d.text((x + 20, y + 52), sub, font=f2, fill=(190, 190, 200))


def hp_text(img, cx, y, txt, col=(123, 224, 123)):
    d = ImageDraw.Draw(img, "RGBA")
    f = ImageFont.truetype(F_NUM, 52)
    d.text((cx + 2, y + 3), txt, font=f, anchor="mm", fill=(0, 0, 0, 160))
    d.text((cx, y), txt, font=f, anchor="mm", fill=col)
