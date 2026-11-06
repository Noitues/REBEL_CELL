"""the commonest chromatic colours (C* > 25) of a mask class on a hover plate: lit px only, cut by the hover marks (pencil, FOCUS, hover, ghost,
inset; 1 px grown), on the plate and on the board image under it.  python modal_probe.py <plate name> <class> [n]"""
import sys, json
from collections import Counter
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as T

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
name, cls = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
H, W = 1080, 1920
z = np.load(HV + 'chk/%s.npz' % name)


def m(k):
    return np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)


mk = np.zeros((H, W), bool)
for k in z.files:
    if k.endswith('__' + cls) and not k.startswith('Pv__'):
        mk |= m(k)
hov = np.zeros((H, W), bool)
for k in z.files:
    if k.startswith('P__') or k.startswith('F__') or k in ('Z__hover', 'Z__ghost', 'Z__inset'):
        hov |= m(k)
hov = ndi.binary_dilation(hov, iterations=1)
lit = z['lit'] >= 250
sel = mk & lit & ~hov
rep = json.load(open(HV + 'chk/%s.json' % name))
key = str((rep.get('snap') or {}).get('cache', '')).split()[-1]
for lbl, p in (('plate', HV + 'out/%s.png' % name), ('board', HV + 'work/board_%s.png' % key)):
    rgb = np.asarray(Image.open(p).convert('RGB'))
    px = rgb[sel]
    lab = T.lab(px.astype(np.float64))
    ch = np.hypot(lab[:, 1], lab[:, 2]) > 25
    cnt = Counter(tuple(int(v) for v in q) for q in px[ch])
    med = tuple(int(v) for v in np.median(px[ch], 0)) if ch.any() else None
    print(lbl, 'px', int(sel.sum()), 'chromatic', int(ch.sum()), 'median of chromatic #%02X%02X%02X' % med if med else '',
          'dE %.1f' % T.de76(med, tuple(T.TOKENS['CELL_PINK'])) if med else '')
    for c, k in cnt.most_common(n):
        print('   #%02X%02X%02X %5d  dE to CELL_PINK %.1f' % (c + (k, T.de76(c, tuple(T.TOKENS['CELL_PINK'])))))
