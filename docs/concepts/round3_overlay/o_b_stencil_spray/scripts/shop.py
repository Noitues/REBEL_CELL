"""03_shop.png: BUY over PURCHASE, LEAVE over EXIT, THIS ONE! on a buffed patch, sprayed price tags."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from marks import Overlay, load_base, stencil_word, freehand, ellipse_pts, bahn, OUT
from spraylib import (PINK, WHITE, YELLOW, BLACK, Layer, spray, stencil_shadow, stencil_text, buff_mask, blur, to_mask,
                      IMPACT)

CYAN = (88, 214, 236)


def system_buttons(base):
    """Digital PURCHASE / EXIT buttons in the base UI language (covering the old sticker overlay).

    Drawn washed-out: the human verbs sit on top of them.
    """
    img = base.convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle((18, 752, 294, 1058), fill=(14, 16, 30, 250))
    # dashed frame like the shop panels
    for x in range(18, 294, 14):
        d.line((x, 752, x + 7, 752), fill=CYAN + (200,), width=3)
        d.line((x, 1058, x + 7, 1058), fill=CYAN + (200,), width=3)
    for y in range(752, 1058, 14):
        d.line((18, y, 18, y + 7), fill=CYAN + (200,), width=3)
        d.line((294, y, 294, y + 7), fill=CYAN + (200,), width=3)
    f = bahn(34, "SemiBold")
    for (y0, y1, label) in [(772, 900, "PURCHASE"), (916, 1040, "EXIT")]:
        d.rectangle((36, y0, 276, y1), fill=(24, 30, 50, 255), outline=(60, 120, 140, 255), width=2)
        d.polygon([(36, y0), (52, y0), (36, y0 + 16)], fill=(70, 150, 170, 255))
        d.text((156, y0 + 30), label, font=f, fill=(104, 146, 160, 255), anchor="mm")
    return Image.alpha_composite(img, lay).convert("RGB")


def price_tag(value, rng, w=86, h=46, ss=3):
    """Sprayed stencil price tag: the digits are cut out, so the glass shows through them."""
    img = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (w * 0.78 * ss, 0), (w * ss, h * 0.5 * ss), (w * 0.78 * ss, h * ss), (0, h * ss)], fill=255)
    r = h * 0.11 * ss
    hx, hy = w * 0.80 * ss, h * 0.5 * ss
    d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=0)
    tag = to_mask(img, ss)
    digits = stencil_text(value, 34, font=IMPACT, rng=rng, slice_frac=None, bridge=0.055, pad=0.1)
    dh, dw = digits.shape
    oy, ox = (h - dh) // 2 + 1, int(w * 0.38 - dw / 2)
    cut = np.zeros_like(tag)
    cut[max(0, oy):oy + dh, max(0, ox):ox + dw] = digits[: h - max(0, oy), : w - max(0, ox)]
    M = np.clip(tag - cut, 0, 1)
    pad = 16
    Mp = np.pad(M, pad)
    L = Layer(Mp.shape[1], Mp.shape[0])
    stencil_shadow(L, Mp, rng, dx=3, dy=4, amt=0.75)
    spray(L, Mp, YELLOW, rng, halo=6, sheen=0.35)
    return L.to_image()


def build():
    rng = np.random.default_rng(3319)
    base = load_base("concepts/round2/r2c_v2_modem/modem_shop.png")
    base = system_buttons(base)
    ov = Overlay()

    # buff the old marker scrawl with black spray
    bw, bh = 492, 404
    B = np.pad(buff_mask(bw, bh, rng, inset=6), 20)
    L = Layer(B.shape[1], B.shape[0])
    spray(L, B, np.array([0.055, 0.05, 0.065], np.float32), rng, halo=14, halo_amt=0.5, speck=0.8,
          mottling=0.0, grain=0.0, edge_build=0, opacity=1.0)
    # sweep texture in the black (colour only, so nothing underneath ghosts through)
    from spraylib import fbm
    sw = fbm(B.shape[0], B.shape[1] * 3, rng, scales=(60, 14), weights=(0.7, 0.3))[:, ::3]
    spray(L, B * np.clip((sw - 0.45) * 1.6, 0, 1), np.array([0.13, 0.12, 0.15], np.float32), rng, halo=2,
          halo_amt=0.0, speck=0.0, mottling=0.0, grain=0.2, edge_build=0, opacity=0.6)
    ov.place(L.to_image(), 1376 - 20, 322 - 20)

    # circle the card + THIS ONE! sprayed over the buff
    loop, x0, y0 = freehand(ellipse_pts(1222, 602, 106, 90, 2.6, 2.6 + 6.283 + 0.5, n=18, wob=0.03, rng=rng, tilt=-0.08),
                            10, YELLOW, rng, taper_out=0.12, mist=0.22)
    ov.place(loop, x0, y0)
    this = stencil_word("THIS\nONE!", 100, PINK, rng, angle=-6, drips=6, drip_len=70, drip_w=(5, 8),
                        line_gap=-0.04, keyline=(WHITE, 4, 4), sheen=0.5, halo=10, return_parts=True)
    ov.place_c(this, 1636, 482)
    a, x0, y0 = freehand([(1482, 584), (1420, 612), (1352, 606)], 10, PINK, rng, arrow=True, head=28, mist=0.25)
    ov.place(a, x0, y0)

    # sprayed price tags beside two prices (never over them)
    ov.place(price_tag("25", rng), 478, 362, angle=8)
    ov.place(price_tag("60", rng), 1240, 722, angle=-5)

    # verbs over the washed-out system buttons
    buy = stencil_word("BUY", 92, PINK, rng, angle=-5, drips=4, drip_len=40, drip_w=(5, 8),
                       keyline=(WHITE, 4, 4), sheen=0.5, halo=10, return_parts=True)
    ov.place_c(buy, 158, 852)
    leave = stencil_word("LEAVE", 66, WHITE, rng, angle=4, drips=3, drip_len=36, drip_w=(4, 6), sheen=0.35,
                         return_parts=True)
    ov.place_c(leave, 158, 990)

    out = ov.apply(base, darken=0.22, desat=0.3, spread=16)
    out.save(os.path.join(OUT, "03_shop.png"))
    print("saved 03_shop.png")


if __name__ == "__main__":
    build()
