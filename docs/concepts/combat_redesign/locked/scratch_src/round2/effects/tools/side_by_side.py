"""side_by_side.py <out> <x0,y0,x1,y1> <zoom> <img> [<img> ...]: the same crop of several images side by side (zoomed, nearest)"""
import sys
from PIL import Image
out, box, z = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], float(sys.argv[3])
ims = [Image.open(p).convert('RGB').crop(tuple(box)) for p in sys.argv[4:]]
ims = [i.resize((int(i.width * z), int(i.height * z)), Image.NEAREST if z >= 1 else Image.LANCZOS) for i in ims]
S = Image.new('RGB', (sum(i.width for i in ims) + 8 * (len(ims) - 1), ims[0].height), (255, 0, 255))
x = 0
for i in ims:
    S.paste(i, (x, 0))
    x += i.width + 8
S.save(out)
print(S.size)
