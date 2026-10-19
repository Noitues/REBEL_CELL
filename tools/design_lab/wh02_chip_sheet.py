"""Joins the wh02_chip_capture PNGs into one sheet: each size's full frame, then a close crop
of its top bar (where the theme chip sits), for the art-pass review.

    python tools/design_lab/wh02_chip_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 960
HEAD = 30
BAR_SHARE = 0.09  # the top bar's height as a share of the frame (56 px of 720 with headroom)


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows = []
    for name, label in (("1920", "1920x1080"), ("1280", "1280x720")):
        p = src / (name + ".png")
        if not p.exists():
            continue
        img = Image.open(p).convert("RGB")
        full = img.resize((W, round(img.height * W / img.width)))
        bar = img.crop((0, 0, img.width, round(img.height * BAR_SHARE)))
        bar = bar.resize((W, round(bar.height * W / bar.width)))
        rows.append((f"{label}: netrun HUD, theme chip filled (placeholder, WARN)", full))
        rows.append((f"{label}: top bar crop", bar))
    height = sum(HEAD + r[1].height for r in rows)
    sheet = Image.new("RGB", (W, height), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    y = 0
    for label, img in rows:
        d.text((8, y + 6), label, fill=(240, 240, 230), font=font(16))
        sheet.paste(img, (0, y + HEAD))
        y += HEAD + img.height
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


if __name__ == "__main__":
    main()
