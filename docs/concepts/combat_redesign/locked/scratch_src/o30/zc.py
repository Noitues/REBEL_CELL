"""zc.py <img> <out> x0 y0 x1 y1 [k]   crop + nearest upscale"""
import sys
from PIL import Image
a = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = [int(v) for v in sys.argv[3:7]]
k = int(sys.argv[7]) if len(sys.argv) > 7 else 3
c = a.crop((x0, y0, x1, y1))
c.resize((c.width * k, c.height * k), Image.LANCZOS).save(sys.argv[2])
