"""Stitches the plan2_w1_combat_capture panels into one sheet: 2 columns x 3 rows of 960x540 panels, each titled.

    python tools/design_lab/plan2_w1_combat_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANELS = [
    ("1  N8 x2 stack badge on a slice, tooltip plate (text = the view's own; plate drawn by the capture)", "1_N8_STACKS"),
    ("2  N6 listener chip on the enemy wheel from a hovered nudge's preview", "2_N6_LISTENER"),
    ("3  N7 NUDGE LOCKED / RESPIN LOCKED chips + the refusal toast after a nudge attempt", "3_N7_LOCKS"),
    ("4  N12 combat disc, uneven spans 9 3 6 0 4 8 ticks (the 0 is an empty arc)", "4_N12_DISC"),
    ("5  N12 loadout SPINNER tab: sub-tick map per slot under the uneven wheel", "5_N12_LOADOUT"),
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
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows = (len(PANELS) + 1) // 2
    sheet = Image.new("RGB", (2 * W, rows * (H + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(16)
    for i, (label, stem) in enumerate(PANELS):
        x, y = (i % 2) * W, (i // 2) * (H + HEAD)
        d.text((x + 10, y + 6), label, fill=(240, 240, 240), font=f)
        sheet.paste(Image.open(src / (stem + ".png")).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
