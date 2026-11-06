import sys
from PIL import Image
f, x0, y0, x1, y1, sc = sys.argv[1], *map(int, sys.argv[2:6]), float(sys.argv[6])
im = Image.open(f).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((int((x1 - x0) * sc), int((y1 - y0) * sc)), Image.LANCZOS)
im.save('D:/rc_scratch/tide_concepts/h_work/crop.png')
