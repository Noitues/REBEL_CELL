import sys
from PIL import Image
# wr2_crop.py in out x0 y0 x1 y1 scale
a = sys.argv
im = Image.open(a[1]).convert('RGB').crop(tuple(map(int, a[3:7])))
s = float(a[7])
im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS).save(a[2])
