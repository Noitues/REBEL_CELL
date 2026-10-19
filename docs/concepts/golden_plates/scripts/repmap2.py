import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "route_map_graph", "proc_vs_custom", "scripts"))
import pvc_metrics as PM
L = PM.luma(PM.load_work(sys.argv[1])); H, W = L.shape
hp = L - PM.box_blur(L, 7); n = 2 * PM.REP_TILE; out = []
for ty in range(0, H - 127, 64):
    for tx in range(0, W - 127, 64):
        t = hp[ty:ty+128, tx:tx+128]; t = t - t.mean()
        if t.std() < 0.012: continue
        F = np.fft.rfft2(t, s=(n, n)); ac = np.fft.fftshift(np.fft.irfft2(F*np.conj(F), s=(n, n))); c = n//2; ac /= ac[c, c]
        win = ac[c-48:c+49, c-48:c+49]; core = win[1:-1, 1:-1]
        nb = np.stack([win[dy:dy+core.shape[0], dx:dx+core.shape[1]] for dy in range(3) for dx in range(3) if not (dy==1 and dx==1)])
        yy, xx = np.mgrid[-47:48, -47:48]
        m = (core > nb.max(0)) & (np.maximum(abs(yy), abs(xx)) >= 4)
        if m.any():
            v = np.where(m, core, -9); i = np.unravel_index(v.argmax(), v.shape)
            out.append((float(v[i]), tx, ty, int(xx[i]), int(yy[i])))
out.sort(reverse=True)
for o in out[:14]: print("peak %.2f tile (%d,%d) lag dx %d dy %d" % o)
