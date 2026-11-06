import sys
from PIL import Image
from heads6 import *
im = Image.new('RGBA', (4*300, 300), (40, 34, 60, 255))
for i, t in enumerate(TYPES):
    paste_head(im, head(t), 150 + i*300, 150, 256, 0, t)
im.save(sys.argv[1])
