"""Round 22: ICE as crystals (no fog), the hand of stickers in a cropped frame, and the parked positions.

ice(): a light-blue translucent fill inside the mask, a crisp blue rim, and blue/white ice crystals (spikes with side
branches) growing inward from the inside border; `grow` 0..1 animates them.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ui19 as U  # noqa: E402
import ui20 as V  # noqa: E402

# ------------------------------------------------------------------ the hand (sticker set at the bottom of the screen)
SLOT_Y = 985
SLOT_X = {t[0]: 560 + i * 162 for i, t in enumerate(U.TRAY)}
SLOT_ANG = {t[0]: [-2, 1.5, -1, 2, -1.5, 1][i] for i, t in enumerate(U.TRAY)}
PARK_Y = 812          # parked = just ABOVE the slot the card was taken from
HIDDEN_Y = 905        # remove-to-hand: the hidden parked zone at the bottom, right above the slot


def card(name, copies=None, gloss=0.22):
    t = next(t for t in U.TRAY if t[0] == name)
    return U.asset_card(t[0], t[1], t[2], t[3] if copies is None else copies, t[4], t[5], 60 + SLOT_X[name] // 162, gloss_k=gloss)


def hand(fr, skip=(), copies=None):
    copies = copies or {}
    for t in U.TRAY:
        if t[0] in skip:
            continue
        fr = V.place_sticker(fr, card(t[0], copies.get(t[0])), SLOT_X[t[0]], SLOT_Y, SLOT_ANG[t[0]])
    return fr


def park_pos(name):
    return SLOT_X[name], PARK_Y


# ------------------------------------------------------------------ ICE crystals
def ice(fr, mask, grow=1.0, seed=3, fill=0.38, density=7.0, scale=1.0):
    h, w = mask.shape
    if mask.max() <= 0.01:
        return fr
    m = np.clip(mask, 0, 1)
    rng = np.random.default_rng(seed)
    img = fr.img
    # translucent light-blue fill (ice), slightly lifted
    tint = np.array([0.62, 0.86, 1.0], np.float32)
    img = img * (1 - m[..., None] * fill) + tint * m[..., None] * fill + m[..., None] * 0.04
    # inner border + inward normals
    mi = Image.fromarray((m * 255).astype(np.uint8))
    er = np.asarray(mi.filter(ImageFilter.MinFilter(3)), np.float32) / 255
    edge = (m > 0.5) & (er < 0.5)
    sm = np.asarray(mi.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    gy, gx = np.gradient(sm)
    ys, xs = np.nonzero(edge)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # crisp rim
    for x, y in zip(xs[::2], ys[::2]):
        d.point((x, y), fill=(130, 205, 255, 255))
    if len(xs):
        n = int(len(xs) / density)
        idx = rng.choice(len(xs), size=max(1, n), replace=False) if n < len(xs) else np.arange(len(xs))
        for i in idx:
            x, y = float(xs[i]), float(ys[i])
            nx, ny = gx[ys[i], xs[i]], gy[ys[i], xs[i]]
            L0 = math.hypot(nx, ny)
            if L0 < 1e-5:
                continue
            nx, ny = nx / L0, ny / L0
            ang = math.atan2(ny, nx) + rng.normal(0, 0.35)
            L = rng.uniform(7, 22) * scale * grow * (0.6 + 0.4 * rng.random())
            if L < 1.5:
                continue
            _spike(d, x, y, ang, L, rng.uniform(2.2, 4.2) * scale)
            for fpos, sgn in ((0.45, 1), (0.62, -1)):
                if rng.random() < 0.75:
                    bx, by = x + math.cos(ang) * L * fpos, y + math.sin(ang) * L * fpos
                    _spike(d, bx, by, ang + sgn * math.radians(rng.uniform(40, 60)), L * rng.uniform(0.3, 0.5), 1.6 * scale)
    a = np.asarray(lay, np.float32) / 255
    img = img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    # glints on a few crystals
    gl = np.asarray(lay.split()[3].filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255
    fr.img = np.clip(img + gl * np.array([0.25, 0.4, 0.55], np.float32) * 0.5, 0, 1.2)
    return fr


def _spike(d, x, y, ang, L, wd):
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    tip = (x + ca * L, y + sa * L)
    b1 = (x + px * wd, y + py * wd)
    b2 = (x - px * wd, y - py * wd)
    mid = (x + ca * L * 0.35, y + sa * L * 0.35)
    d.polygon([b1, tip, b2], fill=(205, 238, 255, 225), outline=(70, 150, 245, 255))
    d.line([mid, tip], fill=(255, 255, 255, 255), width=1)


def parking_outline(fr, x, y, w=170, h=200, label="EVALUATION ONLY: parking zone (not drawn in game)"):
    lay = Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    X0, Y0 = x - w / 2 - fr.ox, y - h / 2 - fr.oy
    for t in range(0, int(2 * (w + h)), 14):
        u = t
        if u < w:
            a, b = (X0 + u, Y0), (X0 + min(w, u + 7), Y0)
        elif u < w + h:
            a, b = (X0 + w, Y0 + u - w), (X0 + w, Y0 + min(h, u - w + 7))
        elif u < 2 * w + h:
            a, b = (X0 + w - (u - w - h), Y0 + h), (X0 + max(0, w - (u - w - h) - 7), Y0 + h)
        else:
            a, b = (X0, Y0 + h - (u - 2 * w - h)), (X0, Y0 + max(0, h - (u - 2 * w - h) - 7))
        d.line([a, b], fill=(230, 236, 245, 90), width=2)
    d.text((X0 + w / 2, Y0 - 14), label, font=U.F(U.SL.MONO, 12), fill=(255, 210, 120, 230), anchor="mm")
    a = np.asarray(lay, np.float32) / 255
    fr.img = fr.img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    return fr
