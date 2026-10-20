"""NA-25b r6b tiles (art-pass A-054): the jack-out switch frame with its mean / std dev, and SAVED on the street after the settle.

    python tools/city/na25b_r6b_tiles.py <e2e shots dir> <out.jpg>
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

TILE = (960, 540)
LABEL_H = 20


def main() -> int:
    e2e, out = Path(sys.argv[1]), Path(sys.argv[2])
    names = [("jack-out: switch to the HQ", "hq_out_cover"), ("SAVED on the street after the zoom settles (CRT toast)", "chain_8_saved")]
    sheet = Image.new("RGB", (TILE[0] * 2, TILE[1] + LABEL_H), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(names):
        img = Image.open(e2e / (name + ".png")).convert("RGB")
        st = ImageStat.Stat(img)
        stats = "mean RGB %s  std %s" % (tuple(round(m) for m in st.mean), tuple(round(s, 1) for s in st.stddev))
        print(name, stats)
        draw.text((i * TILE[0] + 4, 4), "%s  [%s]" % (label, stats), fill=(230, 230, 230))
        sheet.paste(img.resize(TILE, Image.LANCZOS), (i * TILE[0], LABEL_H))
    sheet.save(out, quality=88)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
