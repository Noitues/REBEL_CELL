"""vsplit.py <img> <out_prefix> <band_h>: cut a tall sheet into bands at 1x for looking"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
h = int(sys.argv[3])
n = 0
for y in range(0, im.height, h):
    im.crop((0, y, im.width, min(im.height, y + h))).save('%s_%02d.png' % (sys.argv[2], n))
    n += 1
print(n, im.size)
