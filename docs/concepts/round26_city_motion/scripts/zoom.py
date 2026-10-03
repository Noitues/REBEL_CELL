"""zoom.py src x0,y0,x1,y1 out [scale]: nearest-neighbour enlargement of a crop, for review."""
import sys
from PIL import Image
src, box, out = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(',')), sys.argv[3]
k = int(sys.argv[4]) if len(sys.argv) > 4 else 2
im = Image.open(src).convert('RGB').crop(box)
im.resize((im.width * k, im.height * k), Image.NEAREST).save(out)
