"""Backdrop 1: INTERIOR. The room inside the chosen Solace building: a bio-lab hall with tank banks,
a long window onto the lime helix, wet floor. Cel bands + ink, one-point perspective."""
import sys, math, random
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
from cel_lib import *
import numpy as np
from bd_common import *

INK = (5, 12, 12, 255)
VPX, VPY, F = 1290, 462, 640


def P(x, y, z):
    return (VPX + F * x / z, VPY - F * y / z)


def quad(img, pts, fill, ink=True, w=3):
    poly(img, pts, fill=fill, outline=INK if ink else None, width=w)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def sky_window(img, x0, y0, x1, y1):
    """The big window: night city, the lime helix, ink line work."""
    L = layer(W, H)
    rect(L, [x0, y0, x1, y1], fill=(10, 18, 34, 255))
    d = draw(L)
    # sky gradient
    for i in range(int(y1 - y0)):
        t = i / (y1 - y0)
        c = lerp((10, 20, 40), (40, 56, 80), t)
        d.line(S([x0, y0 + i, x1, y0 + i]), fill=c + (255,), width=S(1.2))
    rng = random.Random(3)
    # far towers silhouettes
    x = x0
    while x < x1:
        w = rng.uniform(12, 30)
        h = rng.uniform(30, (y1 - y0) * 0.75)
        rect(L, [x, y1 - h, x + w, y1], fill=(14, 22, 44, 255), outline=(5, 10, 18, 255), width=1.5)
        for k in range(int(h / 9)):
            if rng.random() < 0.28:
                wx = x + rng.uniform(3, w - 5)
                rect(L, [wx, y1 - h + 5 + k * 9, wx + 3, y1 - h + 8 + k * 9], fill=(190, 170, 110, 220))
        x += w + rng.uniform(1, 5)
    # the helix, far and lime (the Solace tell)
    cx = (x0 + x1) * 0.5
    top, bot = y0 + 6, y1 - 4
    pa, pb = [], []
    for i in range(41):
        t = i / 40
        yv = top + (bot - top) * t
        xv = math.sin(t * 6.283 * 2.4) * 22
        pa += [cx + xv, yv]
        pb += [cx - xv, yv]
    glow_l = layer(W, H)
    line(glow_l, pa, (150, 255, 70, 255), 7)
    line(glow_l, pb, (150, 255, 70, 255), 7)
    L = glow(L, glow_l, 10, 0.9)
    line(L, pa, INK, 10)
    line(L, pb, INK, 10)
    line(L, pa, (130, 220, 70, 255), 5)
    line(L, pb, (100, 180, 60, 255), 5)
    # window frame mullions
    for k in range(1, 5):
        xx_ = x0 + (x1 - x0) * k / 5
        line(L, [xx_, y0, xx_, y1], INK, 5)
        line(L, [xx_ + 1, y0, xx_ + 1, y1], (60, 90, 84, 255), 2)
    rect(L, [x0, y0, x1, y1], outline=INK, width=6)
    img.alpha_composite(L)


def tank(img, sx, sy_base, r, h, lit=1.0, plant=True, seed=0):
    """Glass cylinder with lime liquid. sx centre, sy_base y of base centre, r px radius, h px height."""
    rng = random.Random(seed)
    ry = r * 0.30
    top = sy_base - h
    # base ring + shadow
    ellipse(img, [sx - r * 1.25, sy_base - ry * 1.2, sx + r * 1.25, sy_base + ry * 1.5], fill=(0, 0, 0, 120))
    ellipse(img, [sx - r * 1.12, sy_base - ry * 1.1, sx + r * 1.12, sy_base + ry * 1.1], fill=(30, 46, 44, 255), outline=INK, width=3)
    # body glass
    rect(img, [sx - r, top, sx + r, sy_base], fill=(40, 84, 80, 255))
    ellipse(img, [sx - r, sy_base - ry, sx + r, sy_base + ry], fill=(40, 84, 80, 255))
    # liquid bands
    lq_top = top + h * 0.12
    cols = [(46, 120, 40), (76, 170, 52), (112, 214, 64)]
    cols = [tuple(int(c * lit) for c in cc) + (255,) for cc in cols]
    rect(img, [sx - r + 2, lq_top, sx + r - 2, sy_base], fill=cols[0])
    rect(img, [sx - r * 0.55, lq_top, sx + r * 0.2, sy_base], fill=cols[1])
    rect(img, [sx - r * 0.35, lq_top, sx - r * 0.02, sy_base], fill=cols[2])
    ellipse(img, [sx - r + 2, lq_top - ry, sx + r - 2, lq_top + ry], fill=cols[2], outline=INK, width=2)
    ellipse(img, [sx - r + 2, sy_base - ry, sx + r - 2, sy_base + ry], fill=cols[0])
    if plant:
        for k in range(5):
            px = sx + rng.uniform(-r * 0.5, r * 0.5)
            ph = rng.uniform(h * 0.3, h * 0.65)
            leaf = [(px, sy_base - 4), (px - r * 0.25, sy_base - ph * 0.5), (px + rng.uniform(-r * 0.2, r * 0.2), sy_base - ph), (px + r * 0.25, sy_base - ph * 0.5)]
            poly(img, leaf, fill=(20, 70, 30, 255), outline=INK, width=2)
    # bubbles
    for k in range(int(6 + r / 6)):
        bx = sx + rng.uniform(-r * 0.7, r * 0.7)
        by = rng.uniform(lq_top + 6, sy_base - 6)
        br = rng.uniform(1.5, 3.5)
        ellipse(img, [bx - br, by - br, bx + br, by + br], outline=(220, 255, 200, 190), width=1.2)
    # glass edges + ink + highlight
    line(img, [sx - r, top, sx - r, sy_base], INK, 3)
    line(img, [sx + r, top, sx + r, sy_base], INK, 3)
    ellipse(img, [sx - r, sy_base - ry, sx + r, sy_base + ry], outline=INK, width=3)
    # cap
    ellipse(img, [sx - r * 1.08, top - ry * 1.15, sx + r * 1.08, top + ry * 1.15], fill=(34, 46, 46, 255), outline=INK, width=3)
    ellipse(img, [sx - r * 0.7, top - ry * 0.7, sx + r * 0.7, top + ry * 0.7], fill=(54, 70, 68, 255), outline=INK, width=2)
    line(img, [sx - r * 0.78, top + h * 0.1, sx - r * 0.78, sy_base - h * 0.15], (220, 255, 230, 120), max(2, r * 0.08))
    # pipe to ceiling
    rect(img, [sx - r * 0.12, 0, sx + r * 0.12, top - ry], fill=(30, 40, 42, 255), outline=INK, width=2)


def build():
    img = new((6, 14, 14, 255))
    # ----- ceiling -----
    quad(img, [P(-1.7, 0.8, 0.6), P(1.7, 0.8, 0.6), P(1.7, 0.8, 3.0), P(-1.7, 0.8, 3.0)], (14, 26, 28, 255))
    # ceiling light strips (dimmed lime-white)
    for xs in (-0.7, 0.55):
        for z0 in (0.8, 1.45, 2.1):
            quad(img, [P(xs - 0.14, 0.79, z0), P(xs + 0.14, 0.79, z0), P(xs + 0.14, 0.79, z0 + 0.4), P(xs - 0.14, 0.79, z0 + 0.4)], (120, 200, 120, 255), w=2.5)
    # ----- floor -----
    fl = (16, 30, 30, 255)
    quad(img, [P(-1.7, -0.62, 0.6), P(1.7, -0.62, 0.6), P(1.7, -0.62, 3.0), P(-1.7, -0.62, 3.0)], fl)
    for z in np.arange(0.6, 3.01, 0.45):
        a, b = P(-1.7, -0.62, z), P(1.7, -0.62, z)
        line(img, [a[0], a[1], b[0], b[1]], (6, 14, 14, 255), 2)
    for x in np.arange(-1.7, 1.71, 0.4):
        a, b = P(x, -0.62, 0.6), P(x, -0.62, 3.0)
        line(img, [a[0], a[1], b[0], b[1]], (6, 14, 14, 255), 2)
    # wet reflection streaks of the ceiling lights and window
    for xs in (-0.7, 0.55):
        for z0 in (0.9, 1.6, 2.3):
            quad(img, [P(xs - 0.1, -0.619, z0), P(xs + 0.1, -0.619, z0), P(xs + 0.1, -0.619, z0 + 0.5), P(xs - 0.1, -0.619, z0 + 0.5)], (60, 110, 70, 255), ink=False)
    quad(img, [P(-0.3, -0.619, 1.3), P(0.3, -0.619, 1.3), P(0.45, -0.619, 3.0), P(-0.45, -0.619, 3.0)], (36, 70, 54, 255), ink=False)
    # ----- back wall -----
    zb = 2.45
    bw = [P(-1.7, 0.8, zb), P(1.7, 0.8, zb), P(1.7, -0.62, zb), P(-1.7, -0.62, zb)]
    quad(img, bw, (22, 46, 44, 255), w=4)
    x0, y0 = P(-1.35, 0.58, zb)
    x1, y1 = P(1.35, -0.04, zb)
    sky_window(img, x0, y0, x1, y1)
    # sill + console row under the window
    quad(img, [P(-1.2, -0.05, zb - 0.02), P(1.2, -0.05, zb - 0.02), P(1.2, -0.14, zb - 0.02), P(-1.2, -0.14, zb - 0.02)], (50, 76, 70, 255))
    for i, xc in enumerate(np.arange(-0.95, 1.0, 0.38)):
        a = P(xc - 0.14, -0.14, zb - 0.1)
        b = P(xc + 0.14, -0.40, zb - 0.1)
        rect(img, [a[0], a[1], b[0], b[1]], fill=(26, 40, 40, 255), outline=INK, width=2.5)
        sc = [a[0] + 3, a[1] + 3, b[0] - 3, a[1] + (b[1] - a[1]) * 0.55]
        rect(img, sc, fill=(60, 150, 70, 255) if i % 2 == 0 else (60, 130, 150, 255))
        for k in range(3):
            line(img, [sc[0] + 3, sc[1] + 4 + k * 5, sc[2] - 3 - k * 6, sc[1] + 4 + k * 5], (210, 255, 210, 180), 1.5)
    # ----- right wall (x=+1.7) with tall panels -----
    for z0 in np.arange(0.6, 3.0, 0.6):
        z1 = z0 + 0.6
        tone = (30, 62, 56, 255) if int(z0 / 0.6) % 2 == 0 else (24, 52, 48, 255)
        quad(img, [P(1.7, 0.8, z0), P(1.7, 0.8, z1), P(1.7, -0.62, z1), P(1.7, -0.62, z0)], tone, w=3)
        # window slit on each panel
        quad(img, [P(1.7, 0.45, z0 + 0.12), P(1.7, 0.45, z1 - 0.12), P(1.7, 0.15, z1 - 0.12), P(1.7, 0.15, z0 + 0.12)], (60, 100, 110, 255), w=2.5)
    # left wall
    for z0 in np.arange(0.6, 3.0, 0.6):
        z1 = z0 + 0.6
        tone = (26, 54, 50, 255) if int(z0 / 0.6) % 2 == 0 else (20, 44, 42, 255)
        quad(img, [P(-1.7, 0.8, z0), P(-1.7, 0.8, z1), P(-1.7, -0.62, z1), P(-1.7, -0.62, z0)], tone, w=3)
    # ----- tank banks, far to near -----
    zs = [2.3, 1.9, 1.55, 1.25]
    for i, z in enumerate(zs):
        for side in (-1, 1):
            cx_, cy_ = P(side * 1.25, -0.62, z)
            r = F * 0.19 / z
            h = F * 1.05 / z
            tank(img, cx_, cy_, r, h, lit=1.0 - 0.1 * i, seed=i * 7 + (side > 0))
    # reflections of the tanks in the wet floor
    R_ = layer(W, H)
    for z in zs:
        for side in (-1, 1):
            cx_, cy_ = P(side * 1.25, -0.62, z)
            r = F * 0.19 / z
            for k in range(14):
                a_ = int(70 * (1 - k / 14))
                rect(R_, [cx_ - r * (1 - k * 0.012), cy_ + k * r * 0.28, cx_ + r * (1 - k * 0.012), cy_ + (k + 1) * r * 0.28], fill=(90, 220, 70, a_))
    img.alpha_composite(R_)
    # window haze: cold light from the helix window into the room
    Hz = layer(W, H)
    wx, wy = P(0, 0.3, zb)
    ellipse(Hz, [wx - 520, wy - 140, wx + 520, wy + 330], fill=(150, 235, 190, 70))
    img = glow(img, Hz, 90, 1.0)
    # a floor-level lime light spill from the tanks
    L = layer(W, H)
    for z in zs:
        for side in (-1, 1):
            cx_, cy_ = P(side * 0.85, -0.619, z)
            ellipse(L, [cx_ - 120 / z, cy_ - 10 / z, cx_ + 120 / z, cy_ + 16 / z], fill=(120, 255, 90, 90))
    img = glow(img, L, 14, 0.9)
    return img


def run():
    img = build()
    out = img.convert('RGB').resize((1920, 1080), Image.LANCZOS)
    a = np.asarray(out).astype(np.float32) / 255
    # ink-ish grade: pull toward dark teal, mild vignette to keep the board the first read
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    vg = 1 - 0.38 * np.clip(np.hypot((xx - 1300) / 1100, (yy - 540) / 700) - 0.35, 0, 1)
    a = a * vg[..., None] * 0.78
    rng = np.random.default_rng(1)
    a += rng.normal(0, 0.012, a.shape).astype(np.float32)
    return np.clip(a, 0, 1)


if __name__ == '__main__':
    bd = run()
    save(bd, SCR + 'bd1_interior_raw.png')
    print('ok')
