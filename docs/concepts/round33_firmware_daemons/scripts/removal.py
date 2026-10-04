"""Round 32 -> removal_options.png: four ways to remove a card sticker / wipe a slice instead of SHRED,
with the best two rendered: A PURGE (an rm -rf keycap; the card dissolves into bits, the locked
dissolve A) and B DEGAUSS (a degaussing coil: the slice's CRT screen rainbow-wobbles to blank, the
sticker's ink slides off). keycap() is also used on shop_v2.png.

python removal.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import r31lib as L
import sticker_lib19 as SL

RED = (232, 20, 30)
CARD = dict(name="Feather Touch", cost=0, kind="WHEEL", art="picto_nudge", pic="picto_nudge", val="1", text="One +-1 nudge.", rar="Common")


def keycap(w=230, pressed=0.0, label="rm -rf", sub="PURGE"):
    """A chunky mechanical keycap in the cel look: top face, skirt, ink line."""
    S = 2
    W2 = w * S
    H2 = int(w * 0.92) * S
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    depth = int((34 - 22 * pressed) * S)
    m = 10 * S
    base = [(m, int(H2 * 0.30)), (W2 - m, int(H2 * 0.30)), (W2 - m, H2 - m), (m, H2 - m)]
    # plate / switch housing under the cap
    d.rounded_rectangle([m - 4 * S, H2 - m - 30 * S, W2 - m + 4 * S, H2 - m + 6 * S], radius=8 * S, fill=(24, 22, 28, 255), outline=L.INK + (255,), width=3 * S)
    top_y0 = int(H2 * 0.12) + int(22 * pressed * S)
    tx0, tx1 = m + 22 * S, W2 - m - 22 * S
    ty0, ty1 = top_y0, H2 - m - 40 * S - depth
    skirt = [(m + 4 * S, ty0 + 18 * S), (W2 - m - 4 * S, ty0 + 18 * S), (W2 - m, ty1 + depth), (m, ty1 + depth)]
    d.polygon(skirt, fill=(150, 12, 20, 255), outline=L.INK + (255,))
    d.polygon([(m, ty1 + depth), (W2 - m, ty1 + depth), (W2 - m - 6 * S, ty1 + depth - 14 * S), (m + 6 * S, ty1 + depth - 14 * S)], fill=(110, 8, 14, 255))
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=14 * S, fill=RED + (255,), outline=L.INK + (255,), width=3 * S)
    # dished top: lighter band
    d.rounded_rectangle([tx0 + 12 * S, ty0 + 10 * S, tx1 - 12 * S, ty0 + 30 * S], radius=8 * S, fill=(255, 90, 96, 255))
    d.text(((tx0 + tx1) / 2, (ty0 + ty1) / 2 + 6 * S), label, font=L.f_mono(int(38 * S * w / 230)), fill=(255, 255, 255, 255), anchor="mm")
    d.text(((tx0 + tx1) / 2, ty1 - 16 * S), sub, font=L.f_num(int(20 * S * w / 230)), fill=(255, 200, 200, 255), anchor="mm")
    # outline the whole object
    a = im.split()[3]
    edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(5)), a)
    im = SL.over(im, L.INK, edge)
    return im.resize((W2 // S, H2 // S), Image.LANCZOS)


def dissolve_down(img, sd, cx, cy, t, sink, seed=1):
    """Locked dissolve A, pouring DOWN into the key: solid above the cut, bits below, drifting to sink."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer = L.place_sticker(layer, sd, cx, cy, shadow=0)
    a = np.asarray(layer, np.float32)
    ys, xs = np.nonzero(a[..., 3] > 10)
    y0, y1 = ys.min(), ys.max()
    rng = np.random.default_rng(seed)
    cols = np.arange(img.size[0])
    jag = np.sin(cols * 0.13 + seed) * 7 + rng.normal(0, 3, img.size[0])
    cut = y1 - (y1 - y0) * t
    yy = np.arange(img.size[1])[:, None]
    solid = (yy < (cut + jag[None, :])).astype(np.float32)
    keep = a.copy()
    keep[..., 3] *= solid
    img = Image.alpha_composite(img, Image.fromarray(keep.astype(np.uint8), "RGBA"))
    d = ImageDraw.Draw(img)
    f = L.f_mono(15)
    for k in rng.integers(0, len(ys), 900):
        py, px = ys[k], xs[k]
        if py < cut + jag[px]:
            continue
        u = rng.random() ** 0.7
        x = px + (sink[0] - px) * u + rng.normal(0, 5)
        y = py + (sink[1] - py) * u
        c = tuple(int(min(255, v * 1.3 + 30)) for v in a[py, px, :3])
        d.text((x, y), "01"[int(rng.random() * 2)], font=f, fill=c + (int(255 * (1 - 0.6 * u)),), anchor="mm")
    return img


def degauss_tile(tile, center=(0.55, 0.5), strength=1.0):
    """CRT degauss: a rainbow wobble ring around the coil, the picture swimming toward blank."""
    a = np.asarray(tile, np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = center[0] * w, center[1] * h
    r = np.hypot(xx - cx, yy - cy)
    ang = np.arctan2(yy - cy, xx - cx)
    disp = 9 * strength * np.sin(r / 7.0) * np.exp(-r / (0.7 * w))
    sx = np.clip(xx + disp * np.cos(ang + 1.2), 0, w - 1).astype(int)
    sy = np.clip(yy + disp * np.sin(ang + 1.2), 0, h - 1).astype(int)
    out = a[sy, sx].copy()
    hue = (r / 40.0 + ang / (2 * np.pi)) % 1.0
    rain = np.stack([np.abs(hue * 6 - 3) - 1, 2 - np.abs(hue * 6 - 2), 2 - np.abs(hue * 6 - 4)], -1)
    rain = np.clip(rain, 0, 1) * 255
    k = (np.exp(-((r - 0.32 * w) / (0.16 * w)) ** 2) * 0.55 * strength)[..., None]
    out[..., :3] = out[..., :3] * (1 - k) + rain * k
    # the centre of the coil already wiped: the screen goes to a flat grey-blue
    wipe = np.clip(1 - r / (0.22 * w), 0, 1)[..., None] * strength
    out[..., :3] = out[..., :3] * (1 - wipe) + np.array([40, 46, 60], np.float32) * wipe
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def coil(w=260):
    """A degaussing coil wand: a fat ring with a handle and a button, cel-shaded."""
    S = 2
    W2, H2 = w * S, int(w * 1.25) * S
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R = W2 * 0.42
    cx, cy = W2 / 2, R + 8 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(60, 60, 72, 255), outline=L.INK + (255,), width=4 * S)
    d.ellipse([cx - R * 0.66, cy - R * 0.66, cx + R * 0.66, cy + R * 0.66], fill=(0, 0, 0, 0), outline=L.INK + (255,), width=4 * S)
    d.arc([cx - R * 0.9, cy - R * 0.9, cx + R * 0.9, cy + R * 0.9], 200, 320, fill=(150, 150, 170, 255), width=6 * S)
    hole = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(hole).ellipse([cx - R * 0.66 + 2 * S, cy - R * 0.66 + 2 * S, cx + R * 0.66 - 2 * S, cy + R * 0.66 - 2 * S], fill=255)
    al = ImageChops.subtract(im.split()[3], hole)
    im.putalpha(al)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx - 26 * S, cy + R - 6 * S, cx + 26 * S, H2 - 6 * S], radius=12 * S, fill=(38, 34, 44, 255), outline=L.INK + (255,), width=4 * S)
    d.rounded_rectangle([cx - 12 * S, cy + R + 20 * S, cx + 12 * S, cy + R + 44 * S], radius=5 * S, fill=(92, 225, 255, 255), outline=L.INK + (255,), width=2 * S)
    d.text((cx, cy - R * 0.79), "DEGAUSS", font=L.f_num(int(22 * S * w / 260)), fill=(255, 255, 255, 255), anchor="mm")
    return im.resize((W2 // S, H2 // S), Image.LANCZOS)


def wiped_card(t=0.55):
    """The sticker's ink slides off behind the coil: right of the wipe line is blank vinyl, with a smear."""
    face = L.card_face(CARD, 230, 306)
    w, h = face.size
    a = np.asarray(face, np.float32)
    xx = np.arange(w)[None, :] + np.arange(h)[:, None] * 0.35
    edge = w * t
    blank = (xx > edge)
    out = a.copy()
    out[..., :3][blank] = np.array([244, 242, 236], np.float32)
    # smear: the ink pulled along the wipe direction for a band past the edge
    band = (xx > edge) & (xx < edge + 46)
    sm = np.asarray(face.filter(ImageFilter.BoxBlur(10)), np.float32)
    k = np.clip(1 - (xx - edge) / 46, 0, 1)[..., None] * band[..., None]
    out[..., :3] = out[..., :3] * (1 - k) + sm[..., :3] * k
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def panel_bg(w, h):
    import shop as S1
    return S1.pegboard(w, h)


def render_a(w=900, h=640):
    img = panel_bg(w, h)
    key = keycap(260, pressed=0.6)
    kx, ky = w // 2 - key.width // 2 + 120, h - key.height - 30
    img = L.drop_shadow(img, key, kx, ky, blur=12, off=(8, 12), op=0.6)
    sd = L.card_sticker(CARD, 210, 280, seed=21)
    img = dissolve_down(img, sd, w // 2 + 120, 210, 0.55, (kx + key.width / 2, ky + key.height * 0.35), seed=4)
    c = L.CRT(330, 190, L.CYAN, "PURGE", tag="50 CYCLES", seed=5)
    c.text((16, 54), "$ rm -rf ./deck/", 18, L.CYAN)
    c.text((16, 80), "    feather_touch", 18, L.CYAN)
    c.text((16, 112), ".......... DELETED", 18, (255, 120, 140))
    c.text((16, 146), "deck 18 -> 17   next purge 75", 15, (120, 170, 190))
    img = L.paste(img, c.finish(), 24, 40)
    p = SL.Pen(img.size, L.GP_YELLOW, seed=6)
    p.text("drop it on the key", 200, 330, 32, angle=-6)
    p.arrow([(240, 360), (300, 430), (360, 470)], width=7, head=18)
    img = L.ink(img, p)
    return img


def render_b(w=900, h=640):
    img = panel_bg(w, h)
    tile = L.tile("big_tile_ZERODAY_15_2.png")
    dg = degauss_tile(tile, center=(0.62, 0.55), strength=1.0)
    img = L.drop_shadow(img, dg, 70, 120, blur=8, off=(4, 8), op=0.5)
    wc = wiped_card(0.5)
    sd = L.sticker_from_art(wc, border=6, seed=33)
    img = L.place_sticker(img, sd, 640, 330, angle=3)
    co = coil(250)
    img = L.drop_shadow(img, co, 600, 240, blur=12, off=(10, 16), op=0.6)
    c = L.CRT(300, 120, L.CYAN, "DEGAUSS", tag="50 CYCLES", seed=7)
    c.text((16, 54), "slot 2: ZERO-DAY 15 -> blank", 15, L.CYAN)
    c.text((16, 82), "card ink lifts off the vinyl", 15, (120, 170, 190))
    img = L.paste(img, c.finish(), 40, 500)
    p = SL.Pen(img.size, L.GP_YELLOW, seed=8)
    p.arrow([(560, 600), (620, 560), (690, 540)], width=7, head=18)
    p.text("one pass", 470, 590, 30, angle=-8)
    img = L.ink(img, p)
    return img


def concept_card(title, sub, lines, icon, rec=False):
    c = L.CRT(430, 210, L.YEL if rec else (170, 170, 190), title, tag="RENDERED" if rec else "SKETCH", seed=len(title))
    c.paste(icon, 18, 56)
    y = 56
    c.text((150, y), sub, 17, (255, 255, 255) if rec else (210, 210, 220))
    for ln in lines:
        y += 28
        c.text((150, y), ln, 14, (170, 190, 200))
    return c.finish()


def icon_defrag(px=118):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(2)
    for gy in range(6):
        for gx in range(6):
            if rng.random() < 0.65:
                col = (92, 225, 255) if gy < 3 else (255, 196, 40)
                d.rectangle([4 + gx * 19, 4 + gy * 19, 20 + gx * 19, 20 + gy * 19], fill=col + (255,))
    return im


def icon_bin(px=118):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(18, 30), (100, 30), (90, 112), (28, 112)], outline=(220, 220, 230, 255), width=4)
    for x in range(30, 96, 12):
        d.line([(x, 32), (x - 3 + (x - 59) * -0.12, 110)], fill=(160, 160, 175, 255), width=2)
    d.rectangle([12, 22, 106, 30], fill=(220, 220, 230, 255))
    d.polygon([(46, 8), (76, 2), (84, 26), (52, 34), (40, 22)], fill=(255, 196, 40, 255), outline=L.INK + (255,))
    return im


def main():
    img = Image.new("RGBA", (L.W, L.H), (11, 10, 16, 255))
    sd = L.sticker_word(["REMOVE A CARD / SLICE"], 60, fills=["yellow"], seed=9)
    img = L.place_sticker(img, sd, 420, 62, angle=-2)
    d = ImageDraw.Draw(img)
    d.text((820, 66), "instead of SHRED: 4 concepts, the best 2 rendered", font=L.f_mono(20), fill=(180, 180, 200, 255), anchor="lm")
    a = render_a()
    b = render_b()
    img = L.drop_shadow(img, a, 40, 120, blur=14)
    img = L.drop_shadow(img, b, 980, 120, blur=14)
    d = ImageDraw.Draw(img)
    d.text((50, 776), "A  PURGE  //  the rm -rf key  (recommended)", font=L.f_num(30), fill=(255, 214, 64, 255))
    d.text((990, 776), "B  DEGAUSS  //  the magnet coil", font=L.f_num(30), fill=(230, 230, 240, 255))
    cards = [
        concept_card("PURGE", "rm -rf keycap", ["drop a card / slice on it;", "dissolve A pours into the key.", "same verb for both."], keycap(118), rec=True),
        concept_card("DEGAUSS", "coil wand", ["slices: CRT wobble to blank;", "cards: ink lifts off the vinyl.", "two looks, one tool."], coil(100), rec=True),
        concept_card("DEFRAG", "block compactor", ["the card breaks into blocks", "that pack away. reads as", "'tidy', not 'delete'."], icon_defrag()),
        concept_card("RECYCLE BIN", "wire bin + EMPTY", ["peel, crumple, bin it;", "undo until EMPTY BIN.", "most physical, least cyber."], icon_bin()),
    ]
    for i, c in enumerate(cards):
        img = L.paste(img, c, 40 + i * 465, 830)
    img = L.bloom(img, 0.15, 0.82, 8)
    L.save(img, "removal_options.png")


if __name__ == "__main__":
    main()
