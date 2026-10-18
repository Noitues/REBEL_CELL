"""Stitches the plan2_w0_combat_capture panels into one sheet: 2 columns x 3 rows of 960x540 panels, each titled.

    python tools/design_lab/plan2_w0_combat_sheet.py <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PANELS = [
    ("1  ENRAGE 1 badge on a boss at turn 10, tooltip open", "1_ENRAGE"),
    ("2  two adjacent needles (gap 1), each with its leader tag", "2_NEEDLES"),
    ("3  resistance +N grease-pen mark at the turn refresh (RESIST 4, +4)", "3_RESIST"),
    ("4  BLOCK / SHIELD / SANDBOX on slices, 2 charges, LAST TURN: EVADED 4", "4_DEFENSE"),
    ("5  PARKED -18 chip at the 68% phase threshold", "5_PARKED"),
    ("6  satellite refusal toast, its nudge arrows disabled", "6_SATELLITE"),
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
    f = font(18)
    for i, (label, stem) in enumerate(PANELS):
        x, y = (i % 2) * W, (i // 2) * (H + HEAD)
        d.text((x + 10, y + 5), label, fill=(240, 240, 240), font=f)
        sheet.paste(Image.open(src / (stem + ".png")).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
