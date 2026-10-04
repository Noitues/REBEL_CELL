"""shop_v3.png: the round 32 MAINFRAME shop with the real MICROCHIPS (Firmware) and DAEMONS rows in place of the
placeholders. Everything else is round 32's shop2.py unchanged (the sign is still round 32's placeholder).

python shop3.py
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

import fwlib as F
import fwfx as X
L = F.L
import assets as A
import shop as S1
import shop2 as S2

CHIPS = [("overvolt", 80), ("skimmer", 110), ("coolant_loop", 150)]
DAEMONS = [("kernel_sync", 150), ("twin_pointer", 245)]
WALLET = S2.WALLET


def foam(w, h, seed=4):
    """Pink anti-static foam strip: chips are pushed into it pins-first (that's how loose chips are stored)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3), np.float32)
    a[:] = (150, 52, 104)
    a += rng.normal(0, 14, (h, w, 1))
    for _ in range(int(w * h / 30)):
        x, y = rng.integers(0, w), rng.integers(0, h)
        a[y, x] *= 0.55
    im = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).convert("RGBA").filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(60, 18, 44, 255), width=3)
    d.line([(0, 4), (w, 4)], fill=(210, 110, 160, 255), width=2)
    return im


def microchips(img):
    x0, y0, x1, y1 = 1290, 196, 1860, 500
    fw, fh = x1 - x0 - 40, 46
    img = L.drop_shadow(img, foam(fw, fh), x0 + 20, y0 + 6, blur=8, off=(4, 8), op=0.6)
    d = ImageDraw.Draw(img)
    for x in (x0 + 34, x1 - 34):
        d.ellipse([x - 7, y0 + 22, x + 7, y0 + 36], fill=(150, 150, 160, 255), outline=(30, 30, 36, 255), width=2)
    for i, (fid, price) in enumerate(CHIPS):
        cx = x0 + 110 + i * 175
        hov = i == 1
        ch = F.chip(fid, 112, lit=0.25 if hov else 0.0)
        ax, ay = F.chip_anchor(112)
        # pins sink into the foam: the chip's top pin row sits at the foam's centre line
        top = y0 + 6 + fh / 2 - (int(112 * 0.10) + 2)
        if hov:
            img.alpha_composite(F._glow(img.size, [cx - 80, top + 10, cx + 80, top + 160], F.RAR_COL[F.FW[fid][2]], 26, 0.55))
        img = L.drop_shadow(img, ch, cx - ch.width / 2, top - (8 if hov else 0), blur=8, off=(5, 9), op=0.65)
        # foam lip over the pins
        lip = foam(int(ch.width * 0.86), 16, seed=10 + i)
        img.alpha_composite(lip, (int(cx - lip.width / 2), int(y0 + 6 + fh / 2 - 8)))
        name = S1.dymo(F.FW[fid][1].upper(), 20)
        img = L.drop_shadow(img, name, cx - name.width / 2, y0 + 196, blur=3, off=(2, 3), op=0.6)
        img = S1.tag_on(img, price, cx + 40, y0 + 262, afford=price <= WALLET, seed=140 + i, angle=[-5, 3, -2][i])
        d = ImageDraw.Draw(img)
        r = F.FW[fid][2]
        d.text((cx - 30, y0 + 252), F.RAR_NAME[r], font=L.f_mono(12), fill=F.RAR_COL[r] + (255,), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
        d.text((cx - 30, y0 + 270), F.allowed_text(F.FW[fid][3]), font=L.f_mono(12), fill=(230, 230, 240, 255), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
    # hover: terminal tooltip on Skimmer
    c = L.CRT(390, 80, L.CYAN, "SKIMMER", tag="FIRMWARE", seed=51)
    c.text((14, 43), "ATK slice: +3 Cycles on a Perfect (x2/combat)", 14, (230, 240, 245))
    c.text((14, 61), "VALID: ATK      drag onto a slot", 13, L.LIME)
    tip = c.finish(scan=0.14)
    tx, ty = 1380, 470
    img = L.crt_glow_under(img, (tx, ty, tx + 390, ty + 80), L.CYAN, 0.2)
    img.alpha_composite(tip, (tx, ty))
    return img


def daemons(img):
    x0, y0, x1, y1 = 1140, 610, 1490, 920
    d = ImageDraw.Draw(img)
    for i, (did, price) in enumerate(DAEMONS):
        cx = x0 + 90 + i * 170
        # a shelf bracket + the tile in a cartridge housing (a Daemon is sold as a running process)
        hx0, hy0 = cx - 70, y0 + 34
        img = S1.hook(img, cx, y0 + 6)
        hous = Image.new("RGBA", (140, 150), (0, 0, 0, 0))
        dh = ImageDraw.Draw(hous)
        dh.rounded_rectangle([0, 0, 139, 149], radius=14, fill=(28, 26, 36, 255), outline=(10, 9, 14, 255), width=3)
        dh.rectangle([10, 128, 129, 140], fill=(16, 14, 22, 255))
        for k in range(6):
            dh.rectangle([18 + k * 18, 131, 26 + k * 18, 137], fill=(226, 186, 92, 255))
        img = L.drop_shadow(img, hous, hx0, hy0, blur=8, off=(5, 9), op=0.6)
        t = F.daemon_tile(did, 118, t=0.25 + 0.3 * i)
        img.alpha_composite(t, (hx0 + 11, hy0 + 8))
        name = S1.dymo(F.DM[did][1].upper(), 19)
        img = L.drop_shadow(img, name, cx - name.width / 2, y0 + 196, blur=3, off=(2, 3), op=0.6)
        img = S1.tag_on(img, price, cx + 36, y0 + 268, afford=price <= WALLET, seed=160 + i, angle=[4, -3][i])
        d = ImageDraw.Draw(img)
        r = F.DM[did][2]
        d.text((cx - 40, y0 + 258), F.RAR_NAME[r], font=L.f_mono(12), fill=F.RAR_COL[r] + (255,), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
        d.text((cx - 40, y0 + 276), F.DM[did][3], font=L.f_mono(12), fill=F.FAM[F.DM[did][3]] + (255,), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
    return img


def main():
    A.shop_wheel()
    S2.placeholder = lambda img, box, title, note: img      # round 33 fills both boxes
    img = S2.compose()
    img = microchips(img)
    img = daemons(img)
    p = L.pen(L.GP_YELLOW, seed=88)
    p.text("pins in the foam", 1600, 150, 24, angle=-3)
    p.text("can't afford", 1418, 946, 22, angle=-4)
    img = L.ink(img, p)
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "shop_v3.png")


if __name__ == "__main__":
    main()
