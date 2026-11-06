"""beat_look.py [red] T [T ...]: render beat frames -> work/look/beat_<T>.png (full size) and a half-size montage work/look/beat_m.png"""
import sys, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import mp_beat as B
from mp_lib import to_img
a = sys.argv[1:]
red = a[0] == 'red'
if red:
    a = a[1:]
ims = []
for x in a:
    t0 = time.time()
    T = float(x)
    im = to_img(B.frame(T, red))
    im.save(B.ME + 'work/look/beat_%s%d.png' % ('r' if red else '', T))
    ims.append(im.resize((960, 540), Image.LANCZOS))
    print(x, round(time.time() - t0, 2), 's', flush=True)
n = len(ims)
cols = min(n, 2)
rows = (n + cols - 1) // cols
m = Image.new('RGB', (cols * 960 + (cols - 1) * 6, rows * 540 + (rows - 1) * 6), (30, 30, 30))
for i, im in enumerate(ims):
    m.paste(im, ((i % cols) * 966, (i // cols) * 546))
m.save(B.ME + 'work/look/beat_m.png')
print('total', B.TOTAL_MS)
