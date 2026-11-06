"""crops2.py: tall effect sheets cut into bands for viewing (round2/docs/work/crops/).  usage: python crops2.py <src rel to locked> <n_bands> <width> <prefix>"""
import sys, os
from PIL import Image

LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/docs/work/crops/'
os.makedirs(OUT, exist_ok=True)
src, n, w, pre = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
im = Image.open(LOCK + src).convert('RGB')
W, H = im.size
bh = -(-H // n)
for i in range(n):
    b = im.crop((0, i * bh, W, min(H, (i + 1) * bh)))
    b = b.resize((w, round(b.size[1] * w / W)), Image.LANCZOS)
    b.save(OUT + '%s_%d.jpg' % (pre, i), quality=88)
    print(OUT + '%s_%d.jpg' % (pre, i), b.size)
