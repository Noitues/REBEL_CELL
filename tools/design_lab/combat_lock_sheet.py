"""Stitches the combat_lock_capture crops into COMBAT_LOCK_r2.jpg: row 1 = CAP_W1 panel 3 (the lock slash),
row 2 = Q19 panel 2 (the chevron chase), 4 columns of 600x600 crops.

    python tools/design_lab/combat_lock_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROWS = [
    [
        ("r2  held slash, 2x (ring + slash, Q label whole)", "zoom_held"),
        ("refused click: re-scribble mid-frame, 2x", "zoom_scribble"),
        ("held, whole wheel 1x", "lock_2_held"),
    ],
    [
        ("Q19 chase at 1.2 s a lap: frame 1 of 3", "chase_1"),
        ("frame 2 of 3", "chase_2"),
        ("frame 3 of 3", "chase_3"),
    ],
]
S = 600
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
    sheet = Image.new("RGB", (4 * S, len(ROWS) * (S + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    for r, row in enumerate(ROWS):
        for c, (label, stem) in enumerate(row):
            x, y = c * S, r * (S + HEAD)
            d.text((x + 10, y + 6), label, fill=(240, 240, 240), font=f)
            shot = Image.open(src / (stem + ".png")).convert("RGB")
            if stem.startswith("zoom_"):
                shot = shot.resize((S, S), Image.LANCZOS)
            sheet.paste(shot.crop((0, 0, min(S, shot.width), min(S, shot.height))), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


main()
