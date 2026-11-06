"""halves.py <out_dir> <files...>: split each strip wider than 2000 px into left / right halves at 1x (with 40 px overlap) for looking"""
import sys, os
from PIL import Image
od = sys.argv[1]
os.makedirs(od, exist_ok=True)
for f in sys.argv[2:]:
    im = Image.open(f)
    w, h = im.size
    b = os.path.splitext(os.path.basename(f))[0]
    if w <= 2000:
        print(f, 'whole', w, h)
        continue
    m = w // 2
    im.crop((0, 0, m + 20, h)).save(os.path.join(od, b + '_L.png'))
    im.crop((m - 20, 0, w, h)).save(os.path.join(od, b + '_R.png'))
    print(b, w, h, 'halves')
