"""layer_check.py <skin> <ids...>: review 1.6, measured. For every 60 fps frame of each effect (0 .. total + 100 ms, full and reduce motion):
the px where the HUD-and-hand layer of that frame is opaque (alpha >= 250) and the frame with the effect differs from the same frame
without the effect's marks (marks=False) by more than 6 levels in any channel. 0 = the effect never shows on the HUD or the hand.
The HUD layer is the one each render passes to comp() (captured by wrapping mp_eff.comp).  -> work/layer_<id>_<skin>.json"""
import sys, json
sys.dont_write_bytecode = True
import numpy as np
import mp_eff as E
from mp_lib import ME

skin = sys.argv[1]
_cap = {}
_comp0 = E.comp


def _comp(bel, abv):
    _cap['a'] = abv[..., 3]
    return _comp0(bel, abv)


E.comp = _comp
for fid in sys.argv[2:]:
    s = E.FX[fid]
    out = dict(id=fid, skin=skin, method=__doc__, full=[], reduce=[])
    for red in (False, True):
        tot = s['timing']['total'] if not red else max(p[2] for p in s['reduce_phases'])
        worst = 0
        hud_px = 0
        for i in range(int((tot + 100) * 60 / 1000) + 1):
            t = i * 1000.0 / 60
            _cap.clear()
            f = np.clip(s['render'](t, skin, red), 0, 255)
            a = _cap.get('a')
            r = np.clip(s['render'](t, skin, red, marks=False), 0, 255)
            if a is None or a.shape != f.shape[:2]:
                if fid != 'fx_trace_add':
                    raise SystemExit('no HUD layer captured for %s' % fid)
                a = np.full(f.shape[:2], 255.0)           # trace_add draws over the HUD (allowed): every px it changes counts
            op = a >= 250
            d = np.abs(f - r).max(2) > 6
            n = int((op & d).sum())
            worst = max(worst, n)
            hud_px = int(op.sum())
        out['reduce' if red else 'full'] = dict(max_px_on_opaque_hud=worst, opaque_hud_px_in_box=hud_px, frames=i + 1)
    json.dump(out, open(ME + 'work/layer_%s_%s.json' % (fid, skin), 'w'), indent=1)
    print(fid, skin, 'full', out['full']['max_px_on_opaque_hud'], 'reduce', out['reduce']['max_px_on_opaque_hud'], 'of', out['full']['opaque_hud_px_in_box'], flush=True)
