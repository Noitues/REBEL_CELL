"""shop_v4.png (round 34: slice tags tied to their slices): round 33's latest shop layout (offscreen slice wheel, recycle bin; `shop_layout.py` is a copy
of round33_shop/scripts/shop3.py with the section label FIRMWARE and no placeholders) + the real FIRMWARE and DAEMONS rows.

python shop_v3.py
"""
from PIL import Image, ImageDraw, ImageFilter

import fwlib as F
L = F.L
import assets as A
import shop as S1
import shop_layout as SL3

CHIPS = [("overvolt", 80), ("skimmer", 110), ("coolant_loop", 150)]
DAEMONS = [("kernel_sync", 150), ("twin_pointer", 245)]
WALLET = 160


def foam(w, h, seed=4):
    """Pink anti-static foam: loose chips are stored pins-first in it."""
    import numpy as np
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3), np.float32)
    a[:] = (150, 52, 104)
    a += rng.normal(0, 14, (h, w, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype("uint8")).convert("RGBA").filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(60, 18, 44, 255), width=3)
    d.line([(0, 4), (w, 4)], fill=(210, 110, 160, 255), width=2)
    return im


def firmware_row(img):
    x0, y0, x1 = 1180, 172, 1540
    fh = 34
    img = L.drop_shadow(img, foam(x1 - x0 - 16, fh), x0 + 8, y0, blur=8, off=(4, 8), op=0.6)
    for i, (fid, price) in enumerate(CHIPS):
        cx = x0 + 62 + i * 118
        hov = i == 1
        s = 84
        ch = F.chip(fid, s, lit=0.25 if hov else 0.0)
        top = y0 + fh / 2 - (int(s * 0.10) + 2)
        if hov:
            img.alpha_composite(F._glow(img.size, [cx - 60, top + 10, cx + 60, top + 120], F.RAR_COL[F.FW[fid][2]], 20, 0.55))
        img = L.drop_shadow(img, ch, cx - ch.width / 2, top - (6 if hov else 0), blur=7, off=(4, 8), op=0.65)
        lip = foam(int(ch.width * 0.86), 12, seed=10 + i)
        img.alpha_composite(lip, (int(cx - lip.width / 2), int(y0 + fh / 2 - 6)))
        name = S1.dymo(F.FW[fid][1].upper(), 16)
        img = L.drop_shadow(img, name, cx - name.width / 2, y0 + 136, blur=3, off=(2, 3), op=0.6)
        d = ImageDraw.Draw(img)
        r = F.FW[fid][2]
        d.text((cx, y0 + 176), F.RAR_NAME[r], font=L.f_mono(12), fill=F.RAR_COL[r] + (255,), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
        d.text((cx, y0 + 192), F.allowed_text(F.FW[fid][3]), font=L.f_mono(12), fill=(230, 230, 240, 255), anchor="mm", stroke_width=3, stroke_fill=(8, 6, 12, 255))
        img = S1.tag_on(img, price, cx + 18, y0 + 232, afford=price <= WALLET, seed=140 + i, angle=[-5, 3, -2][i])
    c = L.CRT(352, 56, L.CYAN, None, header=False, seed=51)
    c.text((12, 8), "> SKIMMER  ATK: +3 Cycles on a Perfect (x2)", 13, (230, 240, 245))
    c.text((12, 30), "VALID: ATK   drag onto a slot of your wheel", 13, L.LIME)
    tip = c.finish(scan=0.14)
    img = L.crt_glow_under(img, (x0 + 4, 428, x0 + 356, 484), L.CYAN, 0.2)
    img.alpha_composite(tip, (x0 + 4, 428))
    return img


def daemon_row(img):
    x0, y0 = 1180, 548
    for i, (did, price) in enumerate(DAEMONS):
        hx = x0 + 6 + i * 180
        hous = Image.new("RGBA", (92, 100), (0, 0, 0, 0))
        dh = ImageDraw.Draw(hous)
        dh.rounded_rectangle([0, 0, 91, 99], radius=12, fill=(28, 26, 36, 255), outline=(10, 9, 14, 255), width=3)
        dh.rectangle([8, 86, 83, 94], fill=(16, 14, 22, 255))
        for k in range(5):
            dh.rectangle([14 + k * 14, 88, 20 + k * 14, 92], fill=(226, 186, 92, 255))
        img = L.drop_shadow(img, hous, hx, y0, blur=7, off=(4, 8), op=0.6)
        img.alpha_composite(F.daemon_tile(did, 78, t=0.25 + 0.3 * i), (hx + 7, y0 + 6))
        name = S1.dymo(F.DM[did][1].upper(), 14)
        img = L.drop_shadow(img, name, hx + 46 - name.width / 2, y0 + 106, blur=3, off=(2, 3), op=0.6)
        d = ImageDraw.Draw(img)
        r = F.DM[did][2]
        fam = F.DM[did][3]
        d.text((hx + 100, y0 + 14), F.RAR_NAME[r], font=L.f_mono(12), fill=F.RAR_COL[r] + (255,), stroke_width=3, stroke_fill=(8, 6, 12, 255))
        d.text((hx + 100, y0 + 30), fam, font=L.f_mono(12), fill=F.FAM[fam] + (255,), stroke_width=3, stroke_fill=(8, 6, 12, 255))
        img = S1.tag_on(img, price, hx + 140, y0 + 74, afford=price <= WALLET, seed=160 + i, angle=[4, -3][i])
    return img


def main():
    A.shop_wheel12()
    img = SL3.compose()
    img = firmware_row(img)
    img = daemon_row(img)
    p = L.pen(L.GP_YELLOW, seed=88)
    p.text("pins in the foam", 1468, 128, 22, angle=-3)
    img = L.ink(img, p)
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "shop_v4.png")


if __name__ == "__main__":
    main()
