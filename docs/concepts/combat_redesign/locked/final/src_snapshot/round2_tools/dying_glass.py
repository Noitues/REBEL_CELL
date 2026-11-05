"""dying_glass (round 2, C7 / REVIEW_REBUILD dying rows): the dying cells measured three ways on the published board PNGs.
  gated   = check a's round-2 region (whole glass, erosion 2, hatch included, marks / tray / guns cut)
  glass   = the same region with the L7 hatch lines (saturated pink pixels, 1 px dilated) cut: the lit glass between the hatch lines
  old     = the gate-1 region (erosion 4, the pink-colour cut that also removed the hatch)
python dying_glass.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_checks as RC
import rb_tokens as T
import rb_set as RS

BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
out = {}
for c in RS.CORPS:
    for b in RS.BEATS:
        sfx, nm = RS.sfx(b, c), RS.plate_name(b, c)
        chk = json.load(open(RC.WORK + 'chk_%s.json' % sfx))
        g = chk['rb']['geometry']
        M = RC.load_masks(sfx)
        rgb = np.asarray(Image.open(BOARD + nm + '.png').convert('RGB')).astype(np.float64)
        Y = T.lum(rgb)
        yy, xx = np.mgrid[0:1080, 0:1920]
        cut = np.zeros((1080, 1920), bool)
        for k in RC.CUT:
            if k in M:
                cut |= M[k]
        cut = RC.dil(cut, 3)
        tray = np.zeros((1080, 1920), bool)
        rho = np.hypot(xx - RC.CC[0], yy - RC.CC[1])
        for u in g['units']:
            tx, ty = u['token']
            cut |= np.hypot(xx - tx, yy - ty) <= u['tok_r'] + 8
            tray |= (rho >= u['t_in'] - 3) & (rho <= u['t_out'] + 3)
        for k in M:
            if k.startswith('pen_') or k == 'focus':
                cut |= RC.dil(M[k], 3)
        mx, mn = rgb.max(2), rgb.min(2)
        sat = (mx - mn) / np.maximum(mx, 1)
        pinkish = (sat > 0.45) & (rgb[..., 0] > 150) & (rgb[..., 2] > 90) & (rgb[..., 1] < 140)
        guns = M.get('guns', np.zeros((1080, 1920), bool))
        hatch = M.get('kill_hatch', np.zeros((1080, 1920), bool))
        rows = []
        for cc in g['cells']:
            if cc['state'] != 'dying':
                continue
            poly = RC.poly_mask([cc['poly']])
            gated = ndi.binary_erosion(poly, iterations=2) & ~(cut | RC.dil(guns, 2)) & ~tray
            # kill_hatch is a changed-pixel capture (the hatch AND the lifted glass), so the hatch lines are found by colour: the pink test
            glass = gated & ~RC.dil(pinkish, 1)
            old = ndi.binary_erosion(poly, iterations=4) & ~(cut | RC.dil(pinkish, 2)) & ~tray
            r = dict(ring=cc['dep'], sector=cc['s'], kind=cc['kind'])
            for k, m in (('gated', gated), ('glass', glass), ('old', old)):
                r[k + '_px'] = int(m.sum())
                r[k + '_L'] = round(float(T.lstar(Y[m].mean())), 1) if m.any() else None
                r[k + '_Y'] = float(Y[m].mean()) if m.any() else None
            rows.append(r)
        if rows:
            out[nm] = rows
CK = json.load(open(BOARD + 'checks.json'))['rb_checks']
for nm, rows in out.items():
    ref = CK[nm]['a_cell_contrast']['rings']['0']['reference_L']
    refY = ((ref + 16) / 116.0) ** 3
    for r in rows:
        r['ref_L'] = ref
        for k in ('gated', 'glass', 'old'):
            r[k + '_ratio'] = round(r[k + '_Y'] / refY, 2) if r[k + '_Y'] else None
    print(nm, 'ref', ref, [(r['ring'], r['sector'], 'gated', r['gated_px'], r['gated_L'], r['gated_ratio'], 'glass', r['glass_px'], r['glass_L'],
                           r['glass_ratio'], 'old', r['old_px'], r['old_L'], r['old_ratio']) for r in rows])
json.dump(out, open('D:/rc_scratch/combat_redesign/locked/round2/board/work/dying_glass.json', 'w'), indent=1)
