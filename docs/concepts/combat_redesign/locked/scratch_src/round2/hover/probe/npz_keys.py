"""list the mask keys of a hover plate's npz with their px counts and bboxes.  python npz_keys.py <plate name> [substring]"""
import sys
import numpy as np

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
z = np.load(HV + 'chk/%s.npz' % sys.argv[1])
sub = sys.argv[2] if len(sys.argv) > 2 else ''
H, W = 1080, 1920
for k in sorted(z.files):
    if sub not in k:
        continue
    if k == 'lit':
        print(k, z[k].shape)
        continue
    try:
        m = np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)
    except Exception:
        print(k, 'not a mask', z[k].shape)
        continue
    ys, xs = np.nonzero(m)
    print('%-28s %8d  %s' % (k, int(m.sum()), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else '-'))
