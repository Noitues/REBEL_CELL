"""side-by-side crop of two PNGs plus their amplified difference.  python diff_crop.py <a.png> <b.png> x0 y0 x1 y1 out.png [scale] [gain]"""
import sys
import numpy as np
from PIL import Image

a, b = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
out = sys.argv[7]
s = int(sys.argv[8]) if len(sys.argv) > 8 else 6
gain = float(sys.argv[9]) if len(sys.argv) > 9 else 4.0
A = np.asarray(Image.open(a).convert('RGB')).astype(np.float64)[y0:y1, x0:x1]
B = np.asarray(Image.open(b).convert('RGB')).astype(np.float64)[y0:y1, x0:x1]
D = np.clip(np.abs(A - B) * gain, 0, 255)
row = np.concatenate([A, np.full((y1 - y0, 2, 3), 255.0), B, np.full((y1 - y0, 2, 3), 255.0), D], 1).astype(np.uint8)
im = Image.fromarray(row, 'RGB')
im = im.resize((im.width * s, im.height * s), Image.NEAREST)
im.save(out)
print(im.size)
