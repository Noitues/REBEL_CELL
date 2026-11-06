"""crop.py <in.png> <out.png> x0 y0 x1 y1 [scale]: a crop for a close look (scale > 1 enlarges with NEAREST)."""
import sys
from PIL import Image
a = sys.argv
im = Image.open(a[1]).convert('RGB').crop(tuple(int(v) for v in a[3:7]))
s = float(a[7]) if len(a) > 7 else 1.0
if s != 1.0:
    im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST if s > 1 else Image.LANCZOS)
im.save(a[2])
