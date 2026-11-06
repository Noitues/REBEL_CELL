"""crop.py <in> <x0> <y0> <x1> <y1> <scale> <out>"""
import sys
from PIL import Image
a = sys.argv
im = Image.open(a[1]).convert('RGB').crop(tuple(int(v) for v in a[2:6]))
s = float(a[6])
im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
im.save(a[7])
print(im.size)
