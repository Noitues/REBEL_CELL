"""City-all-corps: before / after crops (v1 backup vs the current deliverables), side by side, one per review item.

python crops.py      -> D:/rc_scratch/city_all_corps/crops/*.jpg   (left: v1, right: now; same camera, same pixels)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402

V1 = os.path.join(CP.SCR, "v1")
OUTD = os.path.join(CP.SCR, "crops")
os.makedirs(OUTD, exist_ok=True)
# (name, file, box x0, y0, x1, y1 in the full-resolution frame)
CROPS = [
    ("1_outlines_sprawl", "city_all_corps_night.png", (2700, 1100, 3700, 1700)),
    ("2a_rebel_cell", "city_all_corps_night.png", (1500, 1650, 2400, 2160)),
    ("2b_meridian_rail", "city_all_corps_night.png", (2000, 650, 3000, 1250)),
    ("2c_aurelian_solace", "city_all_corps_night.png", (1300, 650, 2200, 1350)),
    ("2d_orbital", "city_all_corps_night.png", (1050, 1250, 1750, 1700)),
    ("3_bay_horizon", "city_all_corps_night.png", (900, 0, 2900, 700)),
    ("4_fog_strata_full", "city_all_corps_night.png", (0, 0, 3840, 2160)),
    ("5_beams_lower_left", "city_all_corps_night.png", (0, 1100, 1200, 2160)),
    ("6a_close_drowned", "tethys_flooded_closeup.png", (0, 350, 1100, 1000)),
    ("6b_close_shore", "tethys_flooded_closeup.png", (0, 900, 2560, 1440)),
    ("6c_close_full", "tethys_flooded_closeup.png", (0, 0, 2560, 1440)),
]
MAXW = 1100
font = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 22)
for name, fn, bx in CROPS:
    a = Image.open(os.path.join(V1, fn)).convert("RGB").crop(bx)
    b = Image.open(os.path.join(CP.OUT, fn)).convert("RGB").crop(bx)
    k = min(1.0, MAXW / a.size[0])
    sz = (int(a.size[0] * k), int(a.size[1] * k))
    a, b = a.resize(sz, Image.LANCZOS), b.resize(sz, Image.LANCZOS)
    im = Image.new("RGB", (sz[0] * 2 + 12, sz[1] + 36), (12, 12, 16))
    im.paste(a, (0, 36))
    im.paste(b, (sz[0] + 12, 36))
    d = ImageDraw.Draw(im)
    d.text((8, 6), "v1 (first pass)  %s" % name, font=font, fill=(220, 220, 230))
    d.text((sz[0] + 20, 6), "revision", font=font, fill=(220, 220, 230))
    p = os.path.join(OUTD, name + ".jpg")
    im.save(p, quality=90)
    print(p, im.size)
