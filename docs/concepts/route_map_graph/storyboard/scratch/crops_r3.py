"""Before/after crops for the v3-r3 review: python crops_r3.py <frames dir> <tag>"""
import os, sys
from PIL import Image
FR, TAG = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r3_crops")
os.makedirs(OUT, exist_ok=True)
CROPS = [("beams_f0300", 300, (300, 0, 1060, 300)), ("beams_f0390", 390, (300, 0, 1100, 330)),
         ("fg_f0390", 390, (0, 470, 1280, 720)), ("fg_f0580", 580, (0, 470, 1280, 720))]
for nm, f, box in CROPS:
    im = Image.open(os.path.join(FR, "f_%04d.png" % f)).crop(box)
    im.save(os.path.join(OUT, "%s_%s.png" % (nm, TAG)))
print("crops ->", OUT)
