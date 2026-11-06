import sys
from PIL import Image
src, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
if sc != 1.0:
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
im.save(out)
