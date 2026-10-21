"""Pack the per-HQ style explorations into one sheet: current golden plate | style render(s) per row.

Run from anywhere: python style_sheet.py  (writes hq_styles/style_sheet.jpg)
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.dirname(HERE)
GP = os.path.join(CON, "golden_plates")
W = 2560
CELL_W = W // 3
CELL_H = CELL_W * 9 // 16
HEAD = 34
LBL = 24

ROWS = [
    ("Halcyon: art deco (v1) and deco + Chrysler corner arcs (v2)", [
        ("CURRENT", os.path.join(GP, "hq_halcyon_overview.png")),
        ("DECO v1", os.path.join(CON, "art_deco", "02_halcyon_deco.png")),
        ("DECO v2", os.path.join(CON, "art_deco", "02_halcyon_deco_v2.png"))]),
    ("Solace: Art Nouveau", [
        ("CURRENT", os.path.join(GP, "hq_solace_overview.png")),
        ("NOUVEAU", os.path.join(HERE, "solace_nouveau", "solace_nouveau.png"))]),
    ("Meridian: Streamline Moderne", [
        ("CURRENT", os.path.join(GP, "hq_meridian_overview.png")),
        ("STREAMLINE", os.path.join(HERE, "meridian_streamline", "meridian_streamline.png"))]),
    ("Orbital: space-age retrofuturism", [
        ("CURRENT", os.path.join(GP, "hq_orbital_overview.png")),
        ("SPACE-AGE", os.path.join(HERE, "orbital_spaceage", "orbital_spaceage.png"))]),
    ("Tethys: abyssal bioluminescent", [
        ("CURRENT", os.path.join(GP, "hq_tethys_overview.png")),
        ("ABYSSAL", os.path.join(HERE, "tethys_abyssal", "tethys_abyssal.png"))]),
    ("Aurelian: Rationalist Rome", [
        ("CURRENT", os.path.join(GP, "hq_aurelian_overview.png")),
        ("RATIONALIST", os.path.join(HERE, "aurelian_rationalist", "aurelian_rationalist.png"))]),
]


def font(sz):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    fh, fl = font(24), font(16)
    sheet = Image.new("RGB", (W, len(ROWS) * (HEAD + CELL_H)), (14, 14, 16))
    d = ImageDraw.Draw(sheet)
    y = 0
    for title, cells in ROWS:
        d.text((10, y + 5), title, fill=(240, 220, 170), font=fh)
        y += HEAD
        for i, (lbl, path) in enumerate(cells):
            im = Image.open(path).convert("RGB")
            # cover-fit to 16:9 cell
            s = max(CELL_W / im.width, CELL_H / im.height)
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            l, t = (im.width - CELL_W) // 2, (im.height - CELL_H) // 2
            sheet.paste(im.crop((l, t, l + CELL_W, t + CELL_H)), (i * CELL_W, y))
            d.rectangle((i * CELL_W, y, i * CELL_W + 8 + len(lbl) * 10, y + LBL), fill=(0, 0, 0))
            d.text((i * CELL_W + 5, y + 3), lbl, fill=(255, 255, 255), font=fl)
        y += CELL_H
    sheet.save(os.path.join(HERE, "style_sheet.jpg"), quality=88)


if __name__ == "__main__":
    main()
