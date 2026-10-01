"""03_shop.png - light-pen overlay on the MODEM shop."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from lightpen import *

SRC = BASE_DIR + "round2/r2c_v2_modem/modem_shop.png"
SIZE = (1920, 1080)
BTNS = [("PURCHASE", 818), ("SELL", 895), ("EXIT", 972)]  # y centres of the digital verbs


def edit_base(img):
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    # remove the old marker overlay ("UPGRADE OR DIE!" + crown): hot-pink strokes only
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    pink = (r > 0.78) & (g > 0.15) & (g < 0.6) & (b > 0.45) & (r - g > 0.35)
    region = (xx > 1400) & (xx < 1860) & (yy > 320) & (yy < 725)
    m = dilate((pink & region).astype(np.float32), 2.6)
    valid = (dilate(m, 6) < 0.5) & (yy > 345) & (yy < 700) & (xx > 1380) & (xx < 1870) & ~((xx > 1455) & (xx < 1520) & (yy < 420))
    img = inpaint_textured(img, m, shifts=((40, 0), (-40, 0), (80, 0), (-80, 0), (60, 0), (-60, 0),
                                           (120, 0), (-120, 0), (160, 0), (-160, 0)), valid=valid)
    # replace the taped BUY/SELL/TRADE stickers with a flat digital verb stack (base style)
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([24, 772, 284, 1052], fill=(16, 19, 30, 255))
    d.polygon([(24, 772), (284, 772), (284, 1052), (24, 1052)], outline=(40, 52, 72, 255))
    for label, cy in BTNS:
        x0, x1, y0, y1 = 40, 268, cy - 31, cy + 31
        d.rectangle([x0, y0, x1, y1], fill=(24, 29, 44, 255))
        for x in range(x0, x1, 14):  # dashed cyan border like the shop panels, dimmed
            d.line([(x, y0), (min(x + 7, x1), y0)], fill=(70, 150, 175, 150), width=2)
            d.line([(x, y1), (min(x + 7, x1), y1)], fill=(70, 150, 175, 150), width=2)
        for y in range(y0, y1, 14):
            d.line([(x0, y), (x0, min(y + 7, y1))], fill=(70, 150, 175, 150), width=2)
            d.line([(x1, y), (x1, min(y + 7, y1))], fill=(70, 150, 175, 150), width=2)
        a = 105 if label != "SELL" else 225
        d.text(((x0 + x1) / 2, cy), label, font=font(38, "Bold Condensed"),
               fill=(196, 204, 216, a), anchor="mm")
    img = over(img, layer)
    return img


def tag(cx, cy, w, h, rng):
    """A hand-drawn price tag outline (pointed left, with a hole and a string flick)."""
    x0, x1 = cx - w / 2, cx + w / 2
    j = lambda: rng.normal(0, 1.5)
    pts = [(x0 - h * 0.42, cy + j()), (x0 + j(), cy - h / 2, C), (x1 + j(), cy - h / 2 + j(), C),
           (x1 + j(), cy + h / 2, C), (x0 + j(), cy + h / 2 + j(), C), (x0 - h * 0.42 - 2, cy + 2)]
    out = [polyline(pts)]
    hx = x0 - h * 0.16
    out.append(loop(hx, cy, 4.2, 4.2, rng, turns=1.1, start_deg=0, wob=0.0))
    out.append(curve([(hx - 4, cy - 2), (hx - 22, cy - 18), (hx - 30, cy - 40), (hx - 22, cy - 56)]))
    return out


def mark_this_one(rng):
    paths = [loop(706, 606, 94, 90, rng, turns=1.2, start_deg=-140, tilt_deg=-6)]
    paths += write("THIS ONE!", 682, 828, 52, rng, slant=0.3, rot_deg=-5)
    paths += arrow([(674, 850), (620, 832), (594, 770), (600, 700)], head=20, rng=rng)
    return build(paths, 52, 6, 19, rng)


def mark_buy(rng):
    paths = write("BUY", 76, 772, 68, rng, slant=0.3, rot_deg=-7, track=0.1)
    return build(paths, 72, 12, 32, rng)


def mark_leave(rng):
    paths = write("LEAVE", 52, 938, 58, rng, slant=0.3, rot_deg=-6, track=0.06)
    return build(paths, 58, 8, 26, rng)


def mark_tags(rng):
    paths = tag(700, 758, 108, 46, rng) + tag(1210, 398, 108, 46, rng)
    return build(paths, 40, 1.8, 6, rng)


def render(out_path):
    base = edit_base(load(SRC))
    groups = []
    for seed, fn, col, kw in ((21, mark_this_one, PINK, dict(trail=(-5, 3), light=1.1, veil=0.4)),
                              (22, mark_buy, PINK, dict(trail=(-6, 3), light=1.5, veil=0.5, halo=1.2)),
                              (23, mark_leave, PINK, dict(trail=(-6, 3), light=1.2, veil=0.5)),
                              (24, mark_tags, CYAN, dict(trail=(0, 0), light=0.4, veil=0.1, halo=0.7))):
        m = Masks(SIZE)
        st, _ = fn(np.random.default_rng(seed))
        raster(m, st, np.random.default_rng(seed + 100),
               spark_n=(0, 2) if fn is mark_tags else (2, 5))
        groups.append(dict(masks=m, color=col, **kw))
    out = compose(base, groups)
    save(out, out_path)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else OUT_DIR + "03_shop.png")
