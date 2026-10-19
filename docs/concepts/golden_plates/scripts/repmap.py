"""R-REP-1 tile map: where the autocorrelation peaks sit. python repmap.py <plate.png> [out.png]
Prints p90 and a coarse grid of per-tile peaks; writes a heat overlay when out.png is given."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "route_map_graph", "proc_vs_custom", "scripts"))
sys.dont_write_bytecode = True
import pvc_metrics as PM  # noqa: E402

src = sys.argv[1]
L = PM.luma(PM.load_work(src))
H, W = L.shape
valid = np.ones(L.shape, bool)
hp = L - PM.box_blur(L, 7)
n = 2 * PM.REP_TILE
res = []
for ty in range(0, H - PM.REP_TILE + 1, PM.REP_STRIDE):
    for tx in range(0, W - PM.REP_TILE + 1, PM.REP_STRIDE):
        t = hp[ty:ty + PM.REP_TILE, tx:tx + PM.REP_TILE]
        t = t - t.mean()
        if t.std() < 0.012:
            continue
        F = np.fft.rfft2(t, s=(n, n))
        ac = np.fft.fftshift(np.fft.irfft2(F * np.conj(F), s=(n, n)))
        c = n // 2
        ac = ac / ac[c, c]
        win = ac[c - PM.REP_LAG_MAX:c + PM.REP_LAG_MAX + 1, c - PM.REP_LAG_MAX:c + PM.REP_LAG_MAX + 1]
        core = win[1:-1, 1:-1]
        nb = np.stack([win[dy:dy + core.shape[0], dx:dx + core.shape[1]] for dy in range(3) for dx in range(3) if not (dy == 1 and dx == 1)])
        yy, xx = np.mgrid[-PM.REP_LAG_MAX + 1:PM.REP_LAG_MAX, -PM.REP_LAG_MAX + 1:PM.REP_LAG_MAX]
        cand = core[(core > nb.max(0)) & (np.maximum(np.abs(yy), np.abs(xx)) >= PM.REP_LAG_MIN)]
        res.append((tx, ty, float(cand.max()) if cand.size else 0.0))
a = np.array([r[2] for r in res])
print("size", W, H, "tiles", len(a), "p90 %.3f median %.3f share>0.6 %.3f" % (np.percentile(a, 90), np.median(a), (a > 0.6).mean()))
gx, gy = 8, 6
grid = [[[] for _ in range(gx)] for _ in range(gy)]
for tx, ty, v in res:
    grid[min(gy - 1, int((ty + PM.REP_TILE / 2) / H * gy))][min(gx - 1, int((tx + PM.REP_TILE / 2) / W * gx))].append(v)
for row in grid:
    print(" ".join(("%4.2f/%2d" % (np.mean(c), len(c))) if c else "  -    " for c in row))
if len(sys.argv) > 2:
    im = np.asarray(Image.open(src).convert("RGB"), np.float32) * 0.5
    for tx, ty, v in res:
        if v > 0.6:
            im[ty:ty + PM.REP_TILE, tx:tx + PM.REP_TILE, 0] += 120 * (v - 0.55)
    Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(sys.argv[2])
