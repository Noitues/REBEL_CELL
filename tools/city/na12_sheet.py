"""NA-12 capture sheet: the per-seed city on the City Grid page, one column per campaign seed (rows: the Grid as fitted, the
whole city zoomed out), one JPEG.
Usage: python tools/city/na12_sheet.py --shots <dir with grid_<seed>.png, city_<seed>.png> --seeds 1,2,3 --out <jpg>
       [--labels "<text>;<text>;<text>"]
Inputs come from tools/city/na12_capture.gd."""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

CELL = (640, 360)
ROWS = [("Grid page (as fitted)", "grid"), ("Whole city (zoomed out)", "city")]


def font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", required=True)
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--labels", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    seeds = a.seeds.split(",")
    labels = a.labels.split(";") if a.labels else ["campaign seed %s" % s for s in seeds]
    head = 30
    gap = 10
    sheet = Image.new("RGB", (CELL[0] * len(seeds) + gap * (len(seeds) - 1), (CELL[1] + head) * len(ROWS) + 6), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    f = font(15)
    for r, (title, prefix) in enumerate(ROWS):
        y = r * (CELL[1] + head) + 3
        for c, s in enumerate(seeds):
            x = c * (CELL[0] + gap)
            d.text((x + 6, y + 6), "%s  |  %s" % (title, labels[c]), fill=(230, 230, 235), font=f)
            img = Image.open(os.path.join(a.shots, "%s_%s.png" % (prefix, s))).convert("RGB").resize(CELL, Image.LANCZOS)
            sheet.paste(img, (x, y + head))
    sheet.save(a.out, quality=88)
    print("wrote", a.out, sheet.size)


if __name__ == "__main__":
    main()
