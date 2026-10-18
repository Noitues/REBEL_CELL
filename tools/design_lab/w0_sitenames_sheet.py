"""Joins the two w0_sitenames_capture runs into one sheet: before | after, a row per screen.

    python tools/design_lab/w0_sitenames_sheet.py <before dir> <after dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROWS = [
    ("1", "GRID VIEW (a Site selected)", "1_grid"),
    ("2", "RAID MAP", "2_raid"),
    ("3", "NETRUN HEADER", "3_netrun"),
    ("4", "REWARD SCREEN", "4_reward"),
]
W = 960
H = 540
HEAD = 30


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    before, after, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    sheet = Image.new("RGB", (2 * W, HEAD + len(ROWS) * (H + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    d.text((10, 6), "BEFORE (main 19717ea7)", fill=(255, 120, 120), font=f)
    d.text((W + 10, 6), "AFTER (W0 SITENAMES: Site names removed)", fill=(120, 255, 160), font=f)
    y = HEAD
    for num, label, stem in ROWS:
        d.text((10, y + 5), "%s  %s" % (num, label), fill=(240, 240, 240), font=f)
        for col, folder in enumerate((before, after)):
            p = folder / (stem + ".png")
            x = col * W
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
            else:
                d.rectangle((x + 4, y + HEAD + 4, x + W - 4, y + HEAD + H - 4), outline=(90, 90, 90))
        y += H + HEAD
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
