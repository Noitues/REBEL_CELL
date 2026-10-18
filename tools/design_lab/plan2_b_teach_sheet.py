"""Joins the two plan2_b_teach_capture runs into one 1600 px wide sheet: before | after, one numbered row per beat.

    python tools/design_lab/plan2_b_teach_sheet.py <before dir> <after dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROWS = [
    ("1", "THE TAGS", "1_THE_TAGS"),
    ("2", "AIM (one nudge off: tag not PERFECT)", "2_AIM"),
    ("3", "AIM done (nudged back: PERFECT, step moves on)", "3_AIM_PERFECT"),
    ("4", "FREE NUDGE", "4_FREE_NUDGE"),
    ("5", "STAGED (Jolt played, waits in THIS TURN)", "5_STAGED"),
    ("6", "RAM FORECAST (a card hovered)", "6_RAM_FORECAST"),
    ("7", "UNDO", "7_UNDO"),
    ("8", "CODEX: Lexicon, the Nudge entry", "8_CODEX"),
]
W = 800
H = 450
HEAD = 30
GUTTER = 0


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    before, after, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    # Optional: row numbers to keep (e.g. 2,6,7), then the two column headings.
    keep = sys.argv[4].split(",") if len(sys.argv) > 4 else [r[0] for r in ROWS]
    rows = [r for r in ROWS if r[0] in keep]
    left = sys.argv[5] if len(sys.argv) > 5 else "BEFORE (main 04bf2973)"
    right = sys.argv[6] if len(sys.argv) > 6 else "AFTER (B-TEACH + B-CODEX)"
    sheet = Image.new("RGB", (2 * W, HEAD + len(rows) * (H + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    d.text((10, 6), left, fill=(255, 120, 120), font=f)
    d.text((W + 10, 6), right, fill=(120, 255, 160), font=f)
    y = HEAD
    for num, label, stem in rows:
        d.text((10, y + 5), "%s  %s" % (num, label), fill=(240, 240, 240), font=f)
        for col, folder in enumerate((before, after)):
            p = folder / (stem + ".png")
            x = col * W
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + HEAD))
            else:
                d.rectangle((x + 4, y + HEAD + 4, x + W - 4, y + HEAD + H - 4), outline=(90, 90, 90))
                d.text((x + 30, y + HEAD + H // 2 - 10), "(no such step on this tree)", fill=(150, 150, 150), font=f)
        y += H + HEAD
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
