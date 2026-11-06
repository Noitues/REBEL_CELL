"""peek.py <img> <out> [scale] [x0 y0 x1 y1]: downscaled or cropped view of an image."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
sc = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
if len(sys.argv) > 7:
    im = im.crop(tuple(int(v) for v in sys.argv[4:8]))
im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
im.save(sys.argv[2])
print(im.size)
