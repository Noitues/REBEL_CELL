"""Stitches the plan2_w0_menusheet_capture panels, before | after, one row per change, titled.

    python tools/design_lab/plan2_w0_menusheet_sheet.py <before dir> <after dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANELS = [
    ("1  C6  pause menu: Abandon run set apart from the Quit rows", "1_PAUSE"),
    ("2  C7  New Campaign: locked tile price names Schematics, currency line", "2_UNLOCK"),
    ("3  C8  loot card pick: toast names what was taken", "3_TAKEN"),
    ("4  G14 Firmware into an occupied socket: confirm names both chips", "4_SOCKET"),
    ("5  C4  Heat tooltip: next threshold effect", "5_HEAT"),
]
W = 800
H = 450
HEAD = 28


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    before, after, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    sheet = Image.new("RGB", (2 * W, len(PANELS) * (H + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(17)
    for i, (label, stem) in enumerate(PANELS):
        y = i * (H + HEAD)
        d.text((10, y + 5), label + "      [BEFORE]", fill=(240, 240, 240), font=f)
        d.text((W + 10, y + 5), "[AFTER]", fill=(190, 255, 120), font=f)
        for x, src in ((0, before), (W, after)):
            sheet.paste(Image.open(src / (stem + ".png")).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


main()
