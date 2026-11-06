"""kf_row.py <out> <scale> <png> [<png> ...]: keyframes side by side at one scale (look only)"""
import sys
from PIL import Image
out, s = sys.argv[1], float(sys.argv[2])
ims = [Image.open(p).convert('RGB') for p in sys.argv[3:]]
ims = [i.resize((int(i.width * s), int(i.height * s)), Image.LANCZOS if s < 1 else Image.NEAREST) for i in ims]
S = Image.new('RGB', (sum(i.width for i in ims) + 6 * (len(ims) - 1), max(i.height for i in ims)), (255, 0, 255))
x = 0
for i in ims:
    S.paste(i, (x, 0))
    x += i.width + 6
S.save(out)
print(S.size)
