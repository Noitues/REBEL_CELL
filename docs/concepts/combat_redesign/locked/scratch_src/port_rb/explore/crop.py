"""crop: cut a region of an image to a png for looking at 1x.  usage: python crop.py in out x0 y0 x1 y1"""
import sys
from PIL import Image

im = Image.open(sys.argv[1])
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
im.crop((x0, y0, x1, y1)).save(sys.argv[2])
print(im.size, '->', (x1 - x0, y1 - y0))
