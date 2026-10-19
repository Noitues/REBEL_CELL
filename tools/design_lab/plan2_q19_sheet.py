"""Joins the plan2_q19_capture PNGs into one 1600 px wide sheet (three numbered panels).

    python tools/design_lab/plan2_q19_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANELS = [
    ("1  NUDGE: exact numbers", "1_NUDGE"),
    ("2  RESPIN: ? over the ghosted needle", "2_RESPIN"),
    ("3  COMPOUND: damage + block exact, ? on the random status", "3_COMPOUND"),
]
W = 800
H = 450
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
    rows = 2
    sheet = Image.new("RGB", (W * 2, (H + HEAD) * rows), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(PANELS):
        x, y = (i % 2) * W, (i // 2) * (H + HEAD)
        d.text((x + 8, y + 6), label, fill=(240, 240, 230), font=font(16))
        p = src / (name + ".png")
        if p.exists():
            sheet.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


if __name__ == "__main__":
    main()
