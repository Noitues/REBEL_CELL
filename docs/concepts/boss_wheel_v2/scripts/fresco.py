"""Boss Wheel v2 round 3: paint a god bust as a fresco and tile it into a mosaic.

paint(name, w, key, t, act, S, ox, oy, ascendant, wrath, dark) -> RGBA square sprite (w x w), the bust centred at
(w/2 + ox, w/2 + oy). key = the slice TYPE colour: it becomes the robe and the halo disc (type reads blurred).
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
import fig_gods as G
import render2d as RD

PLASTER = (226, 210, 178)
INKC = (34, 22, 20)
SKIN = (212, 150, 102)
GOLD = (232, 186, 86)


def palette(key, wrath=False, dark=False):
    robe = K.mix(key, (150, 60, 50), 0.22)
    P = {"halo": K.mix(key, (255, 255, 255), 0.25), "robe": robe, "skin": SKIN, "hair": (70, 46, 34), "beard": (96, 66, 44),
         "white": (238, 232, 220), "metal": GOLD, "accent": (196, 52, 44), "dark": INKC}
    if wrath:
        P["skin"] = (196, 104, 84)
        P["halo"] = (255, 90, 40)
    if dark:
        P = {k: K.mul(v, 0.5) for k, v in P.items()}
        P["accent"] = (255, 120, 40)
        P["robe"] = (40, 30, 46)
        P["dark"] = (8, 6, 10)
        P["metal"] = (120, 100, 70)
    return P


def paint(name, w, key, t, act, S, ox=0.0, oy=0.0, ascendant=0.0, wrath=0.0, dark=False, tile=None, seed=0, fig_k=1.0):
    fw = int(w * 0.98 * fig_k)
    masks = G.GODS[name](fw * 2, t, act)
    size2 = masks["robe"].size
    pal = palette(key, wrath > 0.5, dark)
    fig = K.rgba(size2)
    union = K.L(size2)
    for n in G.LAYERS:
        if n == "halo":
            continue
        union = ImageChops.lighter(union, masks[n])
    # ink outline round the whole figure, then flat colours, then one soft shade side + one highlight side
    fig.alpha_composite(K.solid(K.grow(union, 5 * S * 2 / 1.0 * 0.5 + 2), INKC))
    for n in G.LAYERS:
        if n == "halo" or masks[n].getbbox() is None:
            continue
        m = masks[n]
        c = pal[n]
        lay = K.solid(m, c)
        if n not in ("dark",):
            sh = ImageChops.subtract(m, K.shifted(m, -10 * S, -8 * S))
            lay.alpha_composite(K.solid(K.blur(sh, 3 * S), K.mul(c, 0.72), 0.9))
            hi = ImageChops.subtract(m, K.shifted(m, 6 * S, 6 * S))
            lay.alpha_composite(K.solid(K.blur(hi, 2 * S), K.mix(c, (255, 255, 255), 0.35), 0.8))
        fig.alpha_composite(lay)
    fig = fig.resize((fw, int(fw * 0.75)), Image.LANCZOS)
    # the panel: plaster, a halo disc in the type colour behind the head, a red-ochre frame band
    bg = K.rgba((w, w), PLASTER if not dark else (22, 18, 26), 255)
    n = K.noise((w, w), max(3, int(14 * S)), 7 + seed, 3)
    bg = K.tone_map(bg, np.ones((w, w), np.float32), (0.86 + 0.24 * n).astype(np.float32))
    cx, cy = w / 2 + ox, w / 2 + oy
    d = ImageDraw.Draw(bg)
    hr = 92 * S * fig_k / 0.98 * 1.0
    hy = cy - 52 * S * fig_k
    if not dark:
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=pal["halo"] + (255,))
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], outline=INKC + (255,), width=max(1, int(3 * S)))
    if ascendant > 0:     # gold leaf: the halo turns gold, rays fan out
        g = K.L((w, w))
        gd = ImageDraw.Draw(g)
        for j in range(24):
            a = math.radians(j * 15)
            gd.polygon([(cx, hy), (cx + 3 * hr * math.cos(a - 0.05), hy + 3 * hr * math.sin(a - 0.05)),
                        (cx + 3 * hr * math.cos(a + 0.05), hy + 3 * hr * math.sin(a + 0.05))], fill=255)
        gd.ellipse([cx - hr * 1.05, hy - hr * 1.05, cx + hr * 1.05, hy + hr * 1.05], fill=255)
        bg.alpha_composite(K.solid(g, (255, 214, 96), 0.45 * ascendant))
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=(255, 206, 80, 255))
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], outline=INKC + (255,), width=max(1, int(3 * S)))
    hb = K.L((w, w))
    # (figure position: the bust base on the panel's lower edge area)
    fx0, fy0 = int(cx - fw / 2), int(cy + 150 * S * fig_k - fig.height)
    bg.alpha_composite(fig, (fx0, fy0))
    if "halo" in masks and masks["halo"].getbbox() is not None:        # effects: bolt sparks, flames, waves, speed
        fx = masks["halo"].resize((fw, int(fw * 0.75)), Image.LANCZOS)
        lay = K.rgba((w, w))
        lay.alpha_composite(K.solid(fx, pal["halo"] if name != "vulcan" else (255, 140, 40)), (fx0, fy0))
        bg.alpha_composite(lay)
    if wrath > 0:
        bg = K.tone_map(bg, np.ones((w, w), np.float32), np.full((w, w), 1 - 0.2 * wrath, np.float32))
        red = K.solid(K.L((w, w), 255), (200, 40, 20), 0.25 * wrath)
        bg.alpha_composite(red)
    tile = tile or max(3.0, 5.6 * S)
    mos = RD.mosaic(bg, tile, seed=11 + seed, grout=(132, 116, 92) if not dark else (14, 10, 16), gap=0.13)
    if ascendant > 0:   # gold tesserae glint
        tw = K.particles((w, w), 30, int(t * 4) + seed, 1.2 * S, 3 * S, (255, 250, 210), (140, 255),
                         area=(cx - 120 * S, hy - 110 * S, cx + 120 * S, hy + 110 * S))
        mos = K.add(mos, K.blur(tw, 1.2 * S), 1.0 * ascendant)
    return mos
