"""W0 ARTFIX Site-names sheet: panel 1 (Grid, a Site selected + one hovered, after) and panel 4 (reward header,
before | after). Panel 3 is dropped: the netrun header never showed a Site name.

    python tools/design_lab/w0_artfix_sitenames_sheet.py <old W0_SITENAMES.jpg> <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
    old, src, out = Image.open(sys.argv[1]).convert("RGB"), Path(sys.argv[2]), Path(sys.argv[3])
    sheet = Image.new("RGB", (2 * W, 2 * (H + HEAD) + HEAD), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    d.text((10, 6), "1  GRID: a Site selected (T1 SITE, the type word), another hovered (its tag says Site)", fill=(240, 240, 240), font=f)
    sheet.paste(Image.open(src / "1_grid.png").convert("RGB").resize((W, H), Image.LANCZOS), (0, HEAD))
    y = HEAD + H
    d.text((10, y + 6), "4  REWARD HEADER   BEFORE (main 6f5eac32: LOOT // NETRUN: SITE)", fill=(255, 120, 120), font=f)
    d.text((W + 10, y + 6), "AFTER (LOOT // NETRUN: T1 SITE)", fill=(120, 255, 160), font=f)
    # the old sheet's panel 4 AFTER half (its rows are 570 px, a 30 px head over each 540 px panel)
    sx = old.width / 1920.0
    top = int((30 + 3 * 570 + 30) * sx)
    half = old.crop((int(960 * sx), top, int(1920 * sx), top + int(540 * sx))).resize((W, H), Image.LANCZOS)
    sheet.paste(half, (0, y + HEAD))
    sheet.paste(Image.open(src / "4_reward.png").convert("RGB").resize((W, H), Image.LANCZOS), (W, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
