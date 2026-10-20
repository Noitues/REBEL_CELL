"""NA-25b r6c tiles (art-pass A-055): the forward and jack-out switch frames (frozen frame, no wireframe, no flat panel) with their mean / std dev
and the dive's frames for comparison.

    python tools/city/na25b_r6c_tiles.py <e2e shots dir> <out.jpg>
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

TILE = (960, 540)
LABEL_H = 20


def stats(img: Image.Image) -> str:
    st = ImageStat.Stat(img)
    return "mean RGB %s std %s" % (tuple(round(m) for m in st.mean), tuple(round(s, 1) for s in st.stddev))


def main() -> int:
    e2e, out = Path(sys.argv[1]), Path(sys.argv[2])
    names = [
        ("forward switch frame (HQ map frozen under the dot)", "chain_4_dot_to_dive"),
        ("jack-out switch frame (reversed dive's last frame, frozen)", "hq_out_cover"),
    ]
    sheet = Image.new("RGB", (TILE[0] * 2, TILE[1] + LABEL_H), (16, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for i, (label, name) in enumerate(names):
        img = Image.open(e2e / (name + ".png")).convert("RGB")
        text = "%s [%s]" % (label, stats(img))
        print(name, stats(img))
        draw.text((i * TILE[0] + 4, 4), text, fill=(230, 230, 230))
        sheet.paste(img.resize(TILE, Image.LANCZOS), (i * TILE[0], LABEL_H))
    for name in ("dive_0.40", "rev_dive", "chain_3b_dot"):
        p = e2e / (name + ".png")
        if p.exists():
            print("compare", name, stats(Image.open(p).convert("RGB")))
    sheet.save(out, quality=88)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
