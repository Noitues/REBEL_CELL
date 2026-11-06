import sys, numpy as np
from PIL import Image
from lab import load, C
plate, out, r0, r1, a0, a1, sc = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:8])
im = load(plate) * 255
H = int((r1 - r0) * sc); W = int((a1 - a0) * sc * 5)
th = np.radians(a0 + np.arange(W) * (a1 - a0) / W)
rr = r1 - np.arange(H) / sc
T, R = np.meshgrid(th, rr)
X = C[0] + R * np.sin(T); Y = C[1] - R * np.cos(T)
xi = np.clip(np.round(X).astype(int), 0, 1919); yi = np.clip(np.round(Y).astype(int), 0, 1079)
Image.fromarray(im[yi, xi].astype(np.uint8)).save(out); print(out, W, H)
