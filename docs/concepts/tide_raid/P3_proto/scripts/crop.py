import sys
from PIL import Image
src, out, x0, y0, x1, y1, scale = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:8])
im = Image.open(src).convert("RGB").crop((x0, y0, x1, y1))
im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
im.save(out)
