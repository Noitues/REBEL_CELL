"""small_and_grey.png: the player wheel at radius 60 px (naive downscale vs a small-size LOD)
and the hero wheel in greyscale."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from circ_lib import OUT, F_NUM, F_SILK, make_board  # noqa: E402
from make_wheels import PLAYER  # noqa: E402
from wheel_lib import build_wheel, place, np_img, backdrop, caption  # noqa: E402

SS = 2
R_SMALL = 60


def small_wheel(lod):
    """render at master geometry, then reduce to radius 60 (factor 6)."""
    bs = [make_board(n, tk, 360, 130, SS, seed=100 + i, value=v, lod=lod) for i, (n, tk, v, _) in enumerate(PLAYER)]
    ts = [p[3] for p in PLAYER]
    kw = dict(ts=ts, ss=SS, start_tick=-1.5)
    if lod:
        kw["icon_scale"] = 1.55     # small-size LOD: glyph+number take the whole tile
    rgb, a, g, P = build_wheel(bs, **kw)
    frame = np.zeros((a.shape[0] // SS, a.shape[1] // SS, 3), np.float32) + np.array([0.04, 0.03, 0.05])
    frame = place(frame, rgb, a, g, frame.shape[1] / 2, frame.shape[0] / 2, SS)
    big = np_img(frame).convert("RGB")
    k = 360 / R_SMALL
    small = big.resize((int(big.width / k), int(big.height / k)), Image.LANCZOS)
    return small


def main():
    img = np_img(backdrop(seed=5) * 0.55).convert("RGB")
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(F_NUM, 28)
    f2 = ImageFont.truetype(F_SILK, 15)
    d.text((40, 24), "SMALL (r = 60 px)  and  GREYSCALE (hero)", font=f1, fill=(240, 236, 248))
    rows = [("naive: hero tiles shrunk 6x", 0), ("LOD for small sizes: icon x1.55, no silk text", 1)]
    x = 30
    for label, lod in rows:
        sm = small_wheel(lod)
        y = 90
        d.text((x, y), label, font=f2, fill=(200, 200, 210))
        img.paste(sm, (x, y + 30))
        d.text((x + sm.width + 14, y + 30 + sm.height / 2), "1:1  (r = 60)", font=f2, fill=(160, 160, 170))
        z = sm.resize((sm.width * 3, sm.height * 3), Image.NEAREST)
        img.paste(z, (x, y + 60 + sm.height))
        d.text((x, y + 66 + sm.height + z.height), "same pixels at 3x (nearest)", font=f2, fill=(160, 160, 170))
        x += z.width + 24
        print("small", lod, sm.size, flush=True)
    # greyscale hero: the published player wheel, wheel region only
    hero = Image.open(os.path.join(OUT, "wheel_player.png")).convert("L")
    crop = hero.crop((960 - 460, 0, 960 + 460, 1000))
    ImageDraw.Draw(crop).rectangle([820, 30, 920, 95], fill=0)   # hide the legend text that falls in the crop
    crop = crop.resize((int(crop.width * 0.98), int(crop.height * 0.98)), Image.LANCZOS)
    img.paste(crop.convert("RGB"), (1920 - crop.width - 20, 40))
    d.text((1920 - crop.width, 1040), "hero wheel, luminance only: white glyph + number over dark plates hold", font=f2, fill=(200, 200, 210))
    img.save(os.path.join(OUT, "small_and_grey.png"))
    print("small_and_grey ok", flush=True)


if __name__ == "__main__":
    main()
