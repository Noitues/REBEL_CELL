import numpy as np
from lab import *
im = load('p1_decide')
row = (im[276, 1480:1580] * 255).astype(int)
for x in range(0, 100, 2):
    print(1480 + x, tuple(row[x]), end=' | ')
print()
