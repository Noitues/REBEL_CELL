"""crop a region of a png at 1x (or a zoom factor): python crop.py src.png x0 y0 x1 y1 out.png [zoom]"""
import sys
sys.dont_write_bytecode = True
from PIL import Image
a = sys.argv[1:]
im = Image.open(a[0]).convert('RGB')
x0, y0, x1, y1 = map(int, a[1:5])
c = im.crop((x0, y0, x1, y1))
z = float(a[6]) if len(a) > 6 else 1.0
if z != 1.0:
    c = c.resize((int(c.width * z), int(c.height * z)), Image.NEAREST if z > 1 else Image.LANCZOS)
c.save(a[5])
print('ok', c.size)
