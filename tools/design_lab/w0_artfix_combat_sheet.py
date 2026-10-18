"""W0 ARTFIX combat sheet: panels 1 and 6, before | after, matched states.

BEFORE comes from the previous W0_COMBAT.jpg (the same capture script, main 6f5eac32); AFTER from
plan2_w0_combat_capture PNGs (1_ENRAGE, 6_SATELLITE).

    python tools/design_lab/w0_artfix_combat_sheet.py <old W0_COMBAT.jpg> <capture dir> <out jpg>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 960
H = 540
HEAD = 30
# Panel cells in the old sheet: 2 columns x 3 rows of (W x (H + HEAD)), each with a head strip.
OLD = {"1": (0, 0), "6": (W, 2 * (H + HEAD))}
ROWS = [
    ("1", "ENRAGE 1 badge, turn 10: the tooltip plate stands outside the disc (below-right of the badge, clear of the rim, on the dark plate)", "1_ENRAGE"),
    ("6", "satellite refusal: struck arrows at full size, aim ring shaken + red flash (held 0.3 in), the toast beside the ring", "6_SATELLITE"),
]


def font(size: int) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> None:
    old, src, out = Image.open(sys.argv[1]).convert("RGB"), Path(sys.argv[2]), Path(sys.argv[3])
    sheet = Image.new("RGB", (2 * W, HEAD + len(ROWS) * (H + HEAD)), (18, 18, 22))
    d = ImageDraw.Draw(sheet)
    f = font(18)
    d.text((10, 6), "BEFORE (main 6f5eac32)", fill=(255, 120, 120), font=f)
    d.text((W + 10, 6), "AFTER (W0 ARTFIX)", fill=(120, 255, 160), font=f)
    y = HEAD
    for num, label, stem in ROWS:
        d.text((10, y + 5), "%s  %s" % (num, label), fill=(240, 240, 240), font=f)
        ox, oy = OLD[num]
        sheet.paste(old.crop((ox, oy + HEAD, ox + W, oy + HEAD + H)), (0, y + HEAD))
        sheet.paste(Image.open(src / (stem + ".png")).convert("RGB").resize((W, H), Image.LANCZOS), (W, y + HEAD))
        y += H + HEAD
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=90)


main()
