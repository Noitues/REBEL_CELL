"""montage.py <out> <scale> <png> ...: side by side at a scale, for looking"""
import sys
from PIL import Image
out, sc = sys.argv[1], float(sys.argv[2])
ims = [Image.open(p).convert('RGB') for p in sys.argv[3:]]
ims = [im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS if sc < 1 else Image.NEAREST) for im in ims]
W = sum(i.width for i in ims) + 8 * (len(ims) - 1)
H = max(i.height for i in ims)
m = Image.new('RGB', (W, H), (40, 40, 40))
x = 0
for i in ims:
    m.paste(i, (x, 0)); x += i.width + 8
m.save(out)
print('ok', m.size)
