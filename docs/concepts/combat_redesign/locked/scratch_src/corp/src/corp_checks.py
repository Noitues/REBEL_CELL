"""corp_checks: tape neutrality across skins, pink share in the enemy zone, rings crop.  python corp_checks.py"""
import sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import colorsys
from cv_lib import C
O = '../out/'
names = ['neutral', 'solace', 'meridian']
files = {'neutral': O + 'as_p1.png', 'solace': O + 'as_p1_solace.png', 'meridian': O + 'as_p1_meridian.png'}
ims = {n: np.asarray(Image.open(f).convert('RGB')).astype(np.float32) for n, f in files.items() if __import__('os').path.exists(f)}
Y, X = np.mgrid[0:1080, 0:1920]
rho = np.hypot(X - C[0], Y - C[1])
ring = (rho > 214) & (rho < 500)
res = {}
def hsv(a):
    mx, mn = a.max(2), a.min(2)
    s = (mx - mn) / np.maximum(mx, 1)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, s, mx / 255
base = ims['neutral']
h, s, v = hsv(base)
tape = ring & (s < 0.18) & (v > 0.62)
res['tape_px'] = int(tape.sum())
for n in names:
    if n not in ims: continue
    a = ims[n]
    d = np.abs(a - base).max(2)
    res['tape_%s_equal_pct' % n] = round(float((d[tape] <= 6).mean() * 100), 1)
    hh, ss, vv = hsv(a)
    pink = ring & (hh > 315) & (hh < 350) & (ss > 0.40) & (vv > 0.5)
    res['pink_px_%s' % n] = int(pink.sum())
    res['pink_pct_ring_%s' % n] = round(float(pink.sum() / ring.sum() * 100), 3)
json.dump(res, open('../work/corp_checks.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
