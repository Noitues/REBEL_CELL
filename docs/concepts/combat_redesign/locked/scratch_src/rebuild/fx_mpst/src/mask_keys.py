import sys, numpy as np
d = np.load(sys.argv[1])
for k in d.files:
    a = np.unpackbits(d[k])[:1080 * 1920].reshape(1080, 1920).astype(bool)
    ys, xs = np.nonzero(a)
    print(k, d[k].shape, int(a.sum()), (xs.min(), ys.min(), xs.max(), ys.max()) if a.any() else None)
