"""Joins the plan2_q19_capture PNGs into one 1600 px wide sheet (three numbered panels).

    python tools/design_lab/plan2_q19_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANELS = [
    ("1  NUDGE: exact numbers", "1_NUDGE"),
    ("2  RESPIN: ? LANDING, ring ghost, ? on the hub, old tag dimmed", "2_RESPIN"),
    ("3  COMPOUND: damage + block exact, ? names the known status", "3_COMPOUND"),
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
    # Optional third argument: the panel numbers to keep, e.g. "2,3" (one row).
    keep = sys.argv[3].split(",") if len(sys.argv) > 3 else [p[1][0] for p in PANELS]
    panels = [p for p in PANELS if p[1][0] in keep]
    rows = (len(panels) + 1) // 2
    sheet = Image.new("RGB", (W * 2, (H + HEAD) * rows), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(panels):
        x, y = (i % 2) * W, (i // 2) * (H + HEAD)
        d.text((x + 8, y + 6), label, fill=(240, 240, 230), font=font(16))
        p = src / (name + ".png")
        if p.exists():
            sheet.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


if __name__ == "__main__":
    main()
