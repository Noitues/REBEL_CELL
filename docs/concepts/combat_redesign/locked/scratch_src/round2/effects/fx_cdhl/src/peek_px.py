"""peek_px.py <png> <x0> <x1> <y> : print RGBA values along a row"""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGBA'))
x0, x1, y = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
for x in range(x0, x1):
    print(x, a[y, x].tolist())
