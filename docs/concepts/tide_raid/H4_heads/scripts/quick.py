"""quick look: every head large (both frames) and at 24 px. usage: python quick.py out.png"""
import sys
from PIL import Image
from shapes import *
from render import *

im = Image.new('RGBA', (1900, 8 * 190), (40, 34, 60, 255))
for r, (fk, fam) in enumerate(FAMILIES.items()):
    for c, t in enumerate(TYPES):
        for f in (0, 1):
            paste_head(im, fam['fn'](t, f), 100 + c * 300 + f * 150, 95 + r * 190, 130 if f == 0 else 130, 0, t)
        paste_head(im, fam['fn'](t, 0), 1100 + c * 120, 60 + r * 190, 24, -26, t)
        paste_head(im, fam['fn'](t, 0), 1100 + c * 120, 130 + r * 190, 32, 150, t)
im.convert('RGB').save(sys.argv[1])
