"""python hz_mont.py out.jpg scale a.png b.png ...  -> 2-column montage"""
import sys
from PIL import Image
out, s = sys.argv[1], float(sys.argv[2])
ims = [Image.open(p).convert('RGB') for p in sys.argv[3:]]
w, h = int(ims[0].width * s), int(ims[0].height * s)
cols = 2
rows = (len(ims) + 1) // 2
M = Image.new('RGB', (cols * w + 8, rows * h + 8 * rows), (40, 40, 40))
for i, im in enumerate(ims):
    M.paste(im.resize((w, h), Image.LANCZOS), ((i % 2) * (w + 8), (i // 2) * (h + 8)))
M.save(out, quality=88)
