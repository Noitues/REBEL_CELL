"""quick look at all heads large and at 24 px (x8 nearest). usage: python quick.py out.png"""
import sys
from PIL import Image
from shapes import *
from render import *

im = Image.new('RGBA', (1500, 1100), (40, 34, 60, 255))
for r, (fk, fam) in enumerate(FAMILIES.items()):
    for c, t in enumerate(TYPES):
        ops = fam['fn'](t)
        paste_head(im, ops, 150 + c * 300, 140 + r * 260, 220, 0, t)
        paste_head(im, ops, 1000 + c * 150, 90 + r * 260, 24, -26, t)
        paste_head(im, ops, 1000 + c * 150, 190 + r * 260, 32, 150, t)
im.convert('RGB').save(sys.argv[1])
