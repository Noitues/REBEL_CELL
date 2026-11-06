"""quick look: every head large (both frames), 24 px, mystery. usage: python quick.py out.png"""
import sys
from PIL import Image
from shapes_h5 import *
from render import *
im = Image.new('RGBA', (2200, 6 * 190), (40, 34, 60, 255))
for r, fk in enumerate(ORDER):
    fam = FAMILIES[fk]
    for c, t in enumerate(TYPES):
        for f in (0, 1):
            paste_head(im, fam['fn'](t, f), 100 + c * 300 + f * 140, 95 + r * 190, 130, 0, t)
        paste_head(im, fam['fn'](t, 0), 1000 + c * 100, 60 + r * 190, 24, -26, t)
        paste_head(im, fam['fn'](t, 0), 1000 + c * 100, 130 + r * 190, 32, 150, t)
    paste_head(im, fam['x']('X'), 1450, 95 + r * 190, 130, 0, 'D', fill=XCOL)
im.convert('RGB').save(sys.argv[1])
