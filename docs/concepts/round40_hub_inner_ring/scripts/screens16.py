"""Round 16: the player FIREWALL (DEFEND) screen, turned the right way round.

Attacks come from OUTSIDE: shots drop from the outer/top arc (y = 0 is the outer rim) towards the
hub, and the wall sits on the INNER part of the slice near the hub. Each shot falls, hits the wall's
crenellated top, flashes, throws sparks and heats the bricks it struck. Loops over t in [0, 1).
The same rule applies everywhere a wall is shown (card art, forecast chips, the DEFEND hit FX).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from slicelib import f_mono
from programs import base, mul, mix

WALL_TOP = 0.64  # fraction of the screen depth where the wall's top sits (0 = outer rim, 1 = hub side)
SHOTS = [(-0.80, 0.00), (0.55, 0.25), (-0.45, 0.50), (0.85, 0.75)]  # (angle as a fraction of the half span, phase)
FALL = 0.70  # share of each shot's cycle spent falling; the rest is the impact


def firewall(ctx):
    ss, t, W, H = ctx.ss, ctx.t, ctx.W, ctx.H
    im = base(ctx, 0.05)
    d = ImageDraw.Draw(im)
    col = ctx.col
    hot = (255, 70, 120)
    y_top = H * WALL_TOP
    hw_top = max(10.0, ctx.halfw(y_top) * 0.82)

    # incoming-threat ticks along the outer rim (where the shots enter)
    for k in range(-6, 7):
        x = W / 2 + k * 14 * ss
        a = 0.35 + 0.65 * max(0.0, math.sin(2 * math.pi * (t * 2 + k * 0.17)))
        d.polygon([(x - 4 * ss, 3 * ss), (x + 4 * ss, 3 * ss), (x, 8 * ss)], fill=mul(hot, 0.45 + 0.55 * a))

    # shots: position + impact state
    state = []
    def xr(fx, y):  # shots fly RADIALLY inward (constant angle): x narrows towards the hub
        return W / 2 + fx * ctx.halfw(y) * 0.92

    for fx, ph in SHOTS:
        u = (t * 2 + ph) % 1.0
        if u < FALL:
            f = u / FALL
            y = -8 * ss + (y_top + 8 * ss) * f ** 1.35
            state.append((xr(fx, y), y, None, fx))
        else:
            state.append((xr(fx, y_top), y_top, (u - FALL) / (1 - FALL), fx))

    # the wall: brick rows from the top line down to the hub side, crenellated top
    fnt = f_mono(10 * ss)
    brick = "[#]"
    bw = fnt.getlength(brick)
    lh = 12 * ss
    rows = int((H - y_top) // lh) + 2
    for r in range(rows):
        y = y_top + r * lh + 3 * ss
        off = (bw / 2) if r % 2 else 0
        n = int(W // bw) + 2
        for k in range(-1, n):
            x = k * bw + off
            heat = 0.0
            for (sx, sy, p, _f) in state:
                if p is not None and r <= 2:
                    dist = abs(x + bw / 2 - sx)
                    heat = max(heat, (1 - p) * max(0.0, 1 - dist / (bw * 1.6)) * (1.0, 0.6, 0.3)[r])
            c = mix(mul(col, 0.78 - 0.07 * (r % 3)), (255, 255, 255), heat)
            d.text((x, y), brick, font=fnt, fill=c)
    # merlons on top (the crenellation) + the bright top edge
    m = 0
    x = W / 2 - 10 * bw
    while x < W:
        if m % 2 == 0:
            d.rectangle([x, y_top - 6 * ss, x + bw * 0.9, y_top], fill=mul(col, 0.62))
        x += bw
        m += 1
    edge = mul(col, 1.1)
    d.line([(0, y_top), (W, y_top)], fill=edge, width=max(1, int(1.2 * ss)))

    # shots + impacts
    for (x, y, p, fx) in state:
        if p is None:
            L = 34 * ss  # a tapered bolt: white-hot head, hot-pink tail streaming back UP to the rim
            for k in range(8):
                f0, f1 = k / 8, (k + 1) / 8
                w0 = (3.6 * (1 - f0)) * ss
                xa, xb = xr(fx, y - L * f0), xr(fx, y - L * f1)
                d.polygon([(xa - w0, y - L * f0), (xa + w0, y - L * f0), (xb + w0 * 0.8, y - L * f1), (xb - w0 * 0.8, y - L * f1)],
                          fill=mul(hot, 1.0 - 0.8 * f0))
            d.ellipse([x - 3.6 * ss, y - 3.6 * ss, x + 3.6 * ss, y + 3.6 * ss], fill=(255, 240, 250))
        else:
            r = (5 + 22 * p) * ss
            a = 1 - p
            d.ellipse([x - r, y - r * 0.55, x + r, y + r * 0.55], outline=mix(mul(hot, a), (255, 255, 255), 0.4 * a), width=max(1, int(2.2 * ss)))
            d.line([(x - 18 * ss * a, y), (x + 18 * ss * a, y)], fill=mul((255, 255, 255), a), width=max(1, int(2.4 * ss)))
            rng = np.random.default_rng(int(x) % 97)
            for k in range(7):  # sparks kicked back UP, falling again
                ang = math.radians(25 + 130 * rng.random())
                v = (14 + 18 * rng.random()) * ss
                sx = x + math.cos(ang) * v * p
                sy = y - math.sin(ang) * v * p + 30 * ss * p * p
                s2 = 2.0 * ss * (1 - p * 0.6)
                d.rectangle([sx - s2, sy - s2, sx + s2, sy + s2], fill=mix(mul(hot, a), (255, 230, 150), 0.5))
    return im


def install():
    import programs
    programs.PLAYER["FIREWALL"] = firewall
