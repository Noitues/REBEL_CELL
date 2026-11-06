"""crop.py <png> <x0> <y0> <x1> <y1> [scale] [out]  -> a scaled crop (default work/crop.png), for looking"""
import sys
from PIL import Image
p = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
sc = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
out = sys.argv[7] if len(sys.argv) > 7 else 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/crop.png'
im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS if sc < 1 else Image.NEAREST)
im.save(out)
print(out, im.size)
