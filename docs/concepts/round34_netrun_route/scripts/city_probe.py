"""Check helper: the city-map crop used by route_d_city with an iso lattice overlay (scratch only)."""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
CITY = os.path.join(os.path.dirname(OUT), "round30_meridian_castle", "city_night_hq_v6.jpg")
CROP = (820, 330, 2340, 1185)
O = (430, 960)
S = 96
im = Image.open(CITY).convert("RGB").crop(CROP).resize((1920, 1080), Image.LANCZOS)
d = ImageDraw.Draw(im)
for i in range(-2, 16):
    for j in range(-6, 8):
        x = O[0] + i * S - j * S
        y = O[1] - i * S * 0.5 - j * S * 0.5
        if 0 <= x < 1920 and 0 <= y < 1080:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 0))
            d.text((x + 5, y - 12), "%d,%d" % (i, j), fill=(255, 255, 255))
im.save(os.path.join(OUT, "scratch", "probe.png"))
