"""list keys and pixel counts of a hover chk npz"""
import sys
import numpy as np
z = np.load(sys.argv[1])
for k in sorted(z.files):
    a = z[k]
    print(k, a.shape, a.dtype, int(a.sum()) if a.dtype == bool else '')
