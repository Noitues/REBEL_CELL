"""the lifted card's mask bbox and the REFUND tab box of a hover plate, and their overlap.  python lift_tab_probe.py <plate name> [...]"""
import sys, json
import numpy as np

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
H, W = 1080, 1920
for name in sys.argv[1:]:
    z = np.load(HV + 'chk/%s.npz' % name)
    rep = json.load(open(HV + 'chk/%s.json' % name))
    out = [name]
    lm = None
    if 'Hd__hand_lift' in z.files:
        lm = np.unpackbits(z['Hd__hand_lift'])[:H * W].reshape(H, W).astype(bool)
        ys, xs = np.nonzero(lm)
        out.append('lift bbox %s' % ((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),))
    tab = (rep.get('obj2_R') or {}).get('refund_tab')
    out.append('tab %s' % (tab,))
    if tab and lm is not None:
        x0, y0, x1, y1 = (int(round(v)) for v in tab)
        out.append('overlap px %d' % int(lm[y0:y1 + 1, x0:x1 + 1].sum()))
    print('  '.join(out))
