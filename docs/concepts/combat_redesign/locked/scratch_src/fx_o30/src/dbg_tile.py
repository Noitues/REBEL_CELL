import sys, json, numpy as np
import o30_meter as M
mode, x0, y0, sz = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
L = np.load(M.WK + 'lum_%s.npy' % mode, mmap_mode='r')[:, y0 // 2:(y0 + sz) // 2, x0 // 2:(x0 + sz) // 2].astype(np.float32)
T = L.shape[0]
L = L.reshape(T, -1)
dev = np.abs(L - L[0:1]).max(0); f = dev > 0.02
Lf = L[:, f]
eu, ed = M.pixel_events(Lf)
r = M.region_flashes(eu, ed, Lf)
print('events', [(round(-100 + t * 1000 / 60), s) for t, s in r['region_events']])
print('flashes', [round(-100 + t * 1000 / 60) for t in r['flash_frames']])
mc = r['mean_curve']
for k in range(600, 700, 2): print(round(-100 + k * 1000 / 60), mc[k], end=' | ')
