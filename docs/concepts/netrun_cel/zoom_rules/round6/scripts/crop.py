"""Usage: python crop.py in.png out.png x0 y0 x1 y1 scale"""
import sys
from PIL import Image
sys.dont_write_bytecode = True
im = Image.open(sys.argv[1]).convert("RGB")
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
s = float(sys.argv[7])
c = im.crop((x0, y0, x1, y1))
c = c.resize((int(c.width * s), int(c.height * s)), Image.NEAREST)
c.save(sys.argv[2])
