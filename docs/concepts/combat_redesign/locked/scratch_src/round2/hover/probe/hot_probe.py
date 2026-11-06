"""where the HOT marks are on a hover plate, how much of them is lit, and their L* on the plate and on the board image under it.
python hot_probe.py <plate name> [class ...]"""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as T

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
name = sys.argv[1]
classes = sys.argv[2:] or ['chev0', 'arcT0']
z = np.load(HV + 'chk/%s.npz' % name)
H, W = 1080, 1920


def m(k):
    return np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)


lit = z['lit'] if 'lit' in z.files else None
rep = json.load(open(HV + 'chk/%s.json' % name))
key = str((rep.get('snap') or {}).get('cache', '')).split()[-1]
rgb = np.asarray(Image.open(HV + 'out/%s.png' % name).convert('RGB')).astype(np.float64)
bg = np.asarray(Image.open(HV + 'work/board_%s.png' % key).convert('RGB')).astype(np.float64)
Lp, Lb = T.lstar(T.lum(rgb)), T.lstar(T.lum(bg))
for c in classes:
    ks = [k for k in z.files if k.endswith('__' + c)]
    if not ks:
        print(c, 'no mask')
        continue
    mk = np.zeros((H, W), bool)
    for k in ks:
        mk |= m(k)
    ys, xs = np.nonzero(mk)
    print(c, ks, 'px', int(mk.sum()), 'bbox', (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None)
    if lit is not None:
        li = mk & (lit >= 250)
        print('   lit px', int(li.sum()), ' partly lit (10-250)', int((mk & (lit > 10) & (lit < 250)).sum()), ' dim', int((mk & (lit <= 10)).sum()))
        for nm, sel in (('all', mk), ('lit', li)):
            if sel.sum():
                print('   %-4s plate p50 %.1f p95 %.1f p99 %.1f | board p50 %.1f p95 %.1f p99 %.1f' % (
                    nm, np.percentile(Lp[sel], 50), np.percentile(Lp[sel], 95), np.percentile(Lp[sel], 99),
                    np.percentile(Lb[sel], 50), np.percentile(Lb[sel], 95), np.percentile(Lb[sel], 99)))
        lab, n = ndi.label(li)
        for i in range(1, min(n, 12) + 1):
            yy, xx = np.nonzero(lab == i)
            print('     lit comp %d px %d bbox %s p95 plate %.1f board %.1f' % (i, len(xx), (xx.min(), yy.min(), xx.max(), yy.max()),
                                                                          np.percentile(Lp[lab == i], 95), np.percentile(Lb[lab == i], 95)))
