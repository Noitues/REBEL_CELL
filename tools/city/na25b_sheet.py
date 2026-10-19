"""NA-25b r6 review sheet (art-pass A-046): the jack-in chain with NO wheel, then the jack-out reverse.

    python tools/city/na25b_sheet.py <e2e shots dir> <out.jpg>

The e2e dir comes from `na25_e2e_lab.tscn --mode=shots` through tools/run_windowed.py. 12 tiles, 3 columns: terminal, rain, CRT line,
dot, the dive at start / mid / end, SAVED after the entry, then the jack-out reverse (the dive back, the switch, CRT dot opening, rain).
A tile whose frame was not captured is a labelled gap, never skipped silently.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

TILE = (640, 360)
LABEL_H = 18
COLS = 3

TILES = [
    ("1 terminal types jack --from ... --to ...", "chain_1_terminal"),
    ("2 binary rain along the chosen link", "chain_2_rain"),
    ("3 CRT collapse: the line", "chain_3_collapse"),
    ("3 CRT collapse: the dot (hands straight to the dive)", "chain_3b_dot"),
    ("4 dive start (HQ camera, walls closed)", "dive_0.05"),
    ("4 dive mid", "dive_1.50"),
    ("4 dive end / reveal", "reveal_mid"),
    ("SAVED shown after the entry", "chain_8_saved"),
    ("slow load: CRT hold on the terminal panel's own glass", "chain_4b_crt_hold"),
    ("jack-out: the dive reversed", "rev_dive"),
    ("jack-out: switch to the HQ", "hq_out_cover"),
    ("jack-out: the CRT dot opening", "hq_out_crt_on"),
    ("jack-out: rain rises", "hq_out_rain"),
]


def main() -> int:
    e2e, out = Path(sys.argv[1]), Path(sys.argv[2])
    rows = (len(TILES) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TILE[0], rows * (TILE[1] + LABEL_H)), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(TILES):
        x, y = (i % COLS) * TILE[0], (i // COLS) * (TILE[1] + LABEL_H)
        path = e2e / (name + ".png")
        if path.exists():
            draw.text((x + 4, y + 3), label, fill=(230, 230, 230))
            sheet.paste(Image.open(path).convert("RGB").resize(TILE, Image.LANCZOS), (x, y + LABEL_H))
        else:
            draw.text((x + 4, y + 3), label + "  [NOT CAPTURED]", fill=(255, 120, 120))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    print("wrote", out, sheet.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
