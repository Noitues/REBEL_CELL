"""tiles.py <png> <tile_w> <tile_h> [prefix] : cut a published sheet into 1x tiles work/tiles/<prefix>_<row>_<col>.png (for looking at 1x)"""
import sys, os
from PIL import Image
p, tw, th = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
pre = sys.argv[4] if len(sys.argv) > 4 else os.path.splitext(os.path.basename(p))[0]
out = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/tiles/'
os.makedirs(out, exist_ok=True)
im = Image.open(p).convert('RGB')
n = 0
for r, y in enumerate(range(0, im.height, th)):
    for c, x in enumerate(range(0, im.width, tw)):
        im.crop((x, y, min(im.width, x + tw), min(im.height, y + th))).save(out + '%s_%d_%d.png' % (pre, r, c))
        n += 1
print(pre, im.size, n, 'tiles')
