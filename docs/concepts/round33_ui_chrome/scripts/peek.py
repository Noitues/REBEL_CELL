"""Save a crop of an image to scratch/peek.png: python scripts/peek.py path x0 y0 x1 y1 [scale]"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

if __name__ == '__main__':
    p = sys.argv[1]
    x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
    k = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    out = os.path.join(ROOT, 'scratch', 'peek.png')
    im.save(out)
    print(out, im.size)
