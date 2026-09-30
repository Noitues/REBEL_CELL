"""Render all seven stills and the contact sheet.  Usage: python render_all.py
Pure Python + Pillow (no Blender needed); fully seeded, so reruns are identical."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
from lowpoly import finalize, font
from city import render_city
import combat
import shop_ext
import closeup

ROOT = os.path.dirname(HERE)
STILLS = os.path.join(ROOT, 'stills')
os.makedirs(STILLS, exist_ok=True)

jobs = [
    ('01_city_day.png', lambda: render_city('day')),
    ('02_city_night.png', lambda: render_city('night')),
    ('03_suspicion_day.png', lambda: render_city('day', suspicion=True)),
    ('04_suspicion_night.png', lambda: render_city('night', suspicion=True)),
    ('05_combat.png', combat.render),
    ('06_spinner_closeup.png', closeup.render),
    ('07_shop_exterior.png', shop_ext.render),
]
for name, fn in jobs:
    finalize(fn()).save(os.path.join(STILLS, name), optimize=True)
    print('wrote', name)

# contact sheet: 3 + 3 + 1 grid with labels
tw, th = 640, 360
pad, lab = 16, 34
sheet = Image.new('RGB', (3 * tw + 4 * pad, 3 * (th + lab) + 4 * pad + 50), (14, 10, 22))
d = ImageDraw.Draw(sheet)
f = font(11)
d.text((pad, 14), 'r2c_geo_vector_v3  -  gritty triangulated vector, variable facets + neon spill', font=font(12), fill=(250, 230, 200))
for k, (name, _) in enumerate(jobs):
    r, c = divmod(k, 3)
    x = pad + c * (tw + pad) + (tw + pad if r == 2 else 0)
    y = 50 + pad + r * (th + lab + pad)
    im = Image.open(os.path.join(STILLS, name)).resize((tw, th), Image.LANCZOS)
    sheet.paste(im, (x, y))
    d.text((x, y + th + 6), name.replace('.png', ''), font=f, fill=(240, 220, 200))
sheet.save(os.path.join(ROOT, 'contact_sheet.jpg'), quality=90)
print('wrote contact_sheet.jpg')
