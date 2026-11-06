"""crop: python crop.py in.png out.png x0 y0 x1 y1 [scale]"""
import sys
from PIL import Image
a = sys.argv
im = Image.open(a[1]).crop(tuple(int(v) for v in a[3:7]))
k = float(a[7]) if len(a) > 7 else 1.0
if k != 1.0:
    im = im.resize((int(im.width * k), int(im.height * k)), Image.NEAREST)
im.save(a[2]); print(im.size)
