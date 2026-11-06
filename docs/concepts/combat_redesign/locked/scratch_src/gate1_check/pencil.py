import sys, numpy as np
from lab import *
p = sys.argv[1]
im = load(p) * 255
L = Ls(Y(im / 255))
def prof(a, r0, r1):
    rs = np.arange(r0, r1, 0.5)
    xs = C[0] + rs * np.sin(np.radians(a)); ys = C[1] - rs * np.cos(np.radians(a))
    px = im[np.round(ys).astype(int), np.round(xs).astype(int)]
    yel = (px[:, 0] > 150) & (px[:, 1] > 140) & (px[:, 2] < 110)
    ink = (px.max(1) < 60)
    return rs, px, yel, ink
for a in map(float, sys.argv[2:]):
    rs, px, yel, ink = prof(a, 280, 400)
    runs = []
    i = 0
    while i < len(yel):
        if yel[i]:
            j = i
            while j < len(yel) and yel[j]: j += 1
            # ink on each side
            li = i
            while li > 0 and ink[li - 1]: li -= 1
            rj = j
            while rj < len(ink) and ink[rj]: rj += 1
            runs.append((rs[i], (j - i) * 0.5, (i - li) * 0.5, (rj - j) * 0.5))
            i = j
        else: i += 1
    print('angle %.0f: yellow runs (r_start, width px, ink before, ink after):' % a, [(round(r, 1), w, b, c) for r, w, b, c in runs if w >= 1.5])
