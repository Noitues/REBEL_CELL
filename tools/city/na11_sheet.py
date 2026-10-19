"""NA-11 capture sheet: HQ page and a street canyon, before | after the layout rules (rows), one JPEG.
Usage: python tools/city/na11_sheet.py --before <dir with hq_lb1p0/beauty.png, street_lb1p0/beauty.png> --after <dir> --out <jpg>
Inputs come from tools/city/na22_lab.gd (`--rules=0` for the before frames)."""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

CELL = (800, 450)
ROWS = [("HQ page (iso, ortho)", "hq_lb1p0"), ("Street canyon (perspective)", "street_lb1p0")]


def font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    head = 34
    sheet = Image.new("RGB", (CELL[0] * 2 + 12, (CELL[1] + head) * len(ROWS) + 8), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    for r, (title, folder) in enumerate(ROWS):
        y = r * (CELL[1] + head) + 4
        for c, (label, root) in enumerate((("BEFORE (no layout rules)", a.before), ("AFTER (NA-11 rules)", a.after))):
            x = c * (CELL[0] + 12)
            d.text((x + 6, y + 6), "%s  |  %s" % (title, label), fill=(230, 230, 235), font=f)
            img = Image.open(os.path.join(root, folder, "beauty.png")).convert("RGB").resize(CELL, Image.LANCZOS)
            sheet.paste(img, (x, y + head))
    sheet.save(a.out, quality=88)
    print("wrote", a.out, sheet.size)


if __name__ == "__main__":
    main()
