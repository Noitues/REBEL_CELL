import sys, numpy as np
import p1lib as L, p1_comp as C
beat = sys.argv[1]; x, y = int(sys.argv[2]), int(sys.argv[3]); r = 60
lay = C.layers(beat)
for k, v in lay.items():
    reg = v[y - r:y + r, x - r:x + r, :3].astype(np.float32)
    print(k, 'max %.2f mean %.3f  area>1: %d' % (reg.max(), reg.mean(), int((reg.max(-1) > 1).sum())), 'alpha mean %.3f' % v[y - r:y + r, x - r:x + r, 3].mean())
