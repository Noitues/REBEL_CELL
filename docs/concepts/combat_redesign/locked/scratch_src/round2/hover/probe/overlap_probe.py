"""which other mask classes overlap the lit px of one class on a hover plate.  python overlap_probe.py <plate name> <class>"""
import sys
import numpy as np

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
name, cls = sys.argv[1], sys.argv[2]
H, W = 1080, 1920
z = np.load(HV + 'chk/%s.npz' % name)


def m(k):
    return np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)


base = np.zeros((H, W), bool)
for k in z.files:
    if k.endswith('__' + cls) and not k.startswith('Pv__'):
        base |= m(k)
lit = z['lit'] >= 250
sel = base & lit
print(cls, 'lit px', int(sel.sum()))
rows = []
for k in z.files:
    if k == 'lit' or k.startswith('Pv__') or k.endswith('__' + cls):
        continue
    try:
        o = int((m(k) & sel).sum())
    except Exception:
        continue
    if o:
        rows.append((o, k))
for o, k in sorted(rows, reverse=True)[:20]:
    print('   %-28s %6d' % (k, o))
