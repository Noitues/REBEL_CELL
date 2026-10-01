"""programs_sheet.png: the nine programs as 3-tick tiles + EXPLOIT at 2 and 5 ticks."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from circ_lib import OUT, F_NUM, F_SILK, ORDER, PROGRAMS, make_board, render_tile, hexc  # noqa: E402
from wheel_lib import backdrop, caption, np_img  # noqa: E402

SS = 2
RO, RI = 420, 420 * 130 / 360
KEY_T = {"EXPLOIT": 0.04, "ZERO-DAY": 0.72, "FIREWALL": 0.42, "SANDBOX": 0.30, "PROXY": 0.30,
         "PATCH": 0.56, "VIRUS": 0.55, "TROJAN": 0.62, "NULL": 0.0}
BEHAV = {
    "EXPLOIT": "diagonal traces converge on a breach via; packets accelerate in; spark + row tear",
    "ZERO-DAY": "one chip with a white-hot core; once a loop its traces light in a cascade",
    "FIREWALL": "dense parallel bus, brick-staggered pads; scan bar sweeps out; heat shimmer",
    "SANDBOX": "hatched ground plane boxed by a via-stitched guard ring; containment pulse",
    "PROXY": "traces detour around a blocked via; signal + slipping ghost take the detour",
    "PATCH": "broken traces get a solder bridge; green glow travels the mended trace",
    "VIRUS": "patient-zero node; violet infection front spreads; corruption blocks",
    "TROJAN": "innocent board; the N/C chip lid splits, payload LED blinks, traces arm",
    "NULL": "dead grey board, oxidised copper, burnt trace; no glow, only grain",
}


def wrap(text, n):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines


def tile_img(name, ticks, t, value="default"):
    b = make_board(name, ticks, RO, RI, SS, value=value)
    im = render_tile(b, t)
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)


def main():
    frame = backdrop(seed=2) * 0.7
    img = np_img(frame).convert("RGB")
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(F_NUM, 40)
    f_name = ImageFont.truetype(F_NUM, 30)
    f_small = ImageFont.truetype(F_SILK, 14)
    d.text((40, 22), "CIRCUIT BOARD PROGRAMS  -  s_a_circuit", font=f_title, fill=(245, 240, 250))
    d.text((40, 82), "3-tick tiles at 420 px radius (master 360 x 1.17); key frame of each shader shown", font=f_small, fill=(170, 170, 185))

    def put(im, x, y, name, sub=None):
        img.paste(im, (int(x), int(y)), im)
        col = tuple(int(c * 255) for c in hexc(PROGRAMS[name][1]))
        if name == "NULL":
            col = (170, 170, 170)
        cx = x + im.width / 2
        label = name if sub is None else f"{name}  {sub}"
        d.text((cx, y + im.height + 18), label, font=f_name, anchor="mm", fill=col)
        d.text((cx, y + im.height + 40), PROGRAMS[name][0], font=f_small, anchor="mm", fill=(150, 150, 165))
        if sub is None:
            for i, ln in enumerate(wrap(BEHAV[name], 36)):
                d.text((cx, y + im.height + 60 + i * 17), ln, font=f_small, anchor="mm", fill=(195, 195, 205))

    y1 = 100
    x = 40
    for name in ORDER[:5]:
        im = tile_img(name, 3, KEY_T[name])
        put(im, x, y1, name)
        x += im.width + 96
    y2 = 560
    x = 40
    for name in ORDER[5:]:
        im = tile_img(name, 3, KEY_T[name])
        put(im, x, y2, name)
        x += im.width + 30
    # size variants
    d.line([(x - 15, y2 - 10), (x - 15, y2 + 340)], fill=(90, 80, 110), width=2)
    im2 = tile_img("EXPLOIT", 2, 0.04, value=4)
    put(im2, x, y2, "EXPLOIT", "2-tick")
    x += im2.width + 20
    im5 = tile_img("EXPLOIT", 5, 0.04, value=11)
    put(im5, x, y2, "EXPLOIT", "5-tick")
    d.text((x + im5.width / 2, y2 + im5.height + 60), "wide wedge: glyph beside the number", font=f_small, anchor="mm", fill=(195, 195, 205))
    img.save(os.path.join(OUT, "programs_sheet.png"))
    print("sheet ok", img.size, flush=True)


if __name__ == "__main__":
    main()
