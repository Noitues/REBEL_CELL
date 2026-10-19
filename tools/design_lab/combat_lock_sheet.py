"""Stitches the combat_lock_capture crops into COMBAT_LOCK_r4.jpg: row 1 = the RESPIN chip mark (r4: ring
fitted to the chip's outline, slash corner to corner, label readable) held at 1:1 and 2x and re-scribbled
mid-frame at 2x; row 2 = the approved Q/E wheel mark at 2x for reference.

    python tools/design_lab/combat_lock_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# (label, file stem, scale): 1 = pasted as is, 2 = shown at 2x (zoom crops are 300 px, shown at 600).
ROWS = [
    [
        ("r4  RESPIN chip held, 1:1", "chip_held", 1),
        ("RESPIN chip held, 2x", "chip_held", 2),
        ("RESPIN chip re-scribbled mid-frame, 2x", "chip_scribble", 2),
    ],
    [
        ("wheel mark (Q/E, approved A-036) held, 2x", "zoom_held", 2),
        ("wheel mark re-scribbled, 2x", "zoom_scribble", 2),
        ("whole wheel, held 1x", "lock_2_held", 1),
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
    sheet = Image.new("RGB", (3 * S, len(ROWS) * (S + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    for r, row in enumerate(ROWS):
        for c, (label, stem, scale) in enumerate(row):
            x, y = c * S, r * (S + HEAD)
            d.text((x + 10, y + 6), label, fill=(240, 240, 240), font=f)
            shot = Image.open(src / (stem + ".png")).convert("RGB")
            if scale != 1:
                shot = shot.resize((shot.width * scale, shot.height * scale), Image.LANCZOS)
            sheet.paste(shot.crop((0, 0, min(S, shot.width), min(S, shot.height))), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)


main()
