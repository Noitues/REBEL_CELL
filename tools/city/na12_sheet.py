"""NA-12 capture sheet: the per-seed city on the City Grid page, one JPEG of labelled panels (two per row).
Usage: python tools/city/na12_sheet.py --shots <dir> --out <jpg> --panels "file.png=Label;file2.png=Label 2;..."
Inputs come from tools/city/na12_capture.gd (grid_<seed>, city_<seed>, shore_<seed>, look_<seed>, day_<seed>)."""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

CELL = (800, 450)
COLS = 2


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
    ap.add_argument("--panels", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    panels = [p.split("=", 1) for p in a.panels.split(";") if p]
    head = 30
    gap = 10
    rows = (len(panels) + COLS - 1) // COLS
    sheet = Image.new("RGB", (CELL[0] * COLS + gap * (COLS - 1), (CELL[1] + head) * rows + 6), (12, 12, 16))
    d = ImageDraw.Draw(sheet)
    f = font(16)
    for k, (name, label) in enumerate(panels):
        x = (k % COLS) * (CELL[0] + gap)
        y = (k // COLS) * (CELL[1] + head) + 3
        d.text((x + 6, y + 6), label, fill=(230, 230, 235), font=f)
        img = Image.open(os.path.join(a.shots, name)).convert("RGB").resize(CELL, Image.LANCZOS)
        sheet.paste(img, (x, y + head))
    sheet.save(a.out, quality=88)
    print("wrote", a.out, sheet.size)


if __name__ == "__main__":
    main()
