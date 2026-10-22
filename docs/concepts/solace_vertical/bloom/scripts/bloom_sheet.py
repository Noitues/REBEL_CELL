"""Solace THE BLOOM v2 sheet.jpg: rows A / B / C, columns street / HQ / raid / gauge strip, captions (2560 px wide)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

import solace_lib as L

OUT = L.OUT
ROWS = [("A  NECROSIS", "plum-black skin, pink veins, hairline hot front edge, windows dying behind the front"),
        ("B  MYCELIUM", "pale hyphae first, then dark mats with glowing pink spore caps; it climbs and webs"),
        ("C  CULTURE SPILL", "glossy pink agar tide: meniscus edge, bubbles and cells; the name TIDE made literal")]
COLS = [("street netrun, CLOSE", "_street.png", 560, 315), ("HQ overview, floor 9 / 27 CATCHING", "_hq.png", 560, 315),
        ("raid map, infection 60 %", "_raid.png", 560, 315), ("TIDE gauge x5 bands + CAUGHT bits", "_gauge.png", 760, 335)]
GAP, CAP, HEAD = 10, 22, 44


def main():
    W = 2560
    cw = [c[2] * 2 + 0 for c in COLS]
    sc = (W - GAP * 5) / sum(cw)
    cws = [int(c * sc) for c in cw]
    ch = [int(c[3] * 2 * sc) for c in COLS]
    rh = max(ch)
    H = HEAD + 3 * (rh + CAP * 2 + GAP + 24)
    im = Image.new("RGB", (W, H), (12, 7, 20))
    d = ImageDraw.Draw(im)
    d.text((GAP, 10), "SOLACE  THE BLOOM v2  -  three directions, same frames", font=L.font(24), fill=(255, 70, 150))
    y = HEAD
    for r in range(3):
        t, desc = ROWS[r]
        d.text((GAP, y), t + "   " + desc, font=L.font(18), fill=(235, 235, 245))
        y += CAP + 4
        x = GAP
        for (cap, suf, _, _), w in zip(COLS, cws):
            p = Image.open(os.path.join(OUT, "ABC"[r] + suf)).convert("RGB")
            h = int(p.size[1] * w / p.size[0])
            im.paste(p.resize((w, h), Image.LANCZOS), (x, y))
            d.text((x + 6, y + 4), cap, font=L.font(15), fill=(255, 235, 245))
            x += w + GAP
        y += rh + GAP + 4
    im = im.crop((0, 0, W, y))
    im.save(os.path.join(OUT, "sheet.jpg"), quality=88)
    print(im.size)


if __name__ == "__main__":
    main()
