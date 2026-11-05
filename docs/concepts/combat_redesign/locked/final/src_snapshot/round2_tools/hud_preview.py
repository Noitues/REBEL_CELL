"""C8 preview: the board HUD layer alone (p1 / p2 / p3) on the plate's dark ground, with the hud_rows row record.
python hud_preview.py <corp> <outdir>"""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.environ['CORP'] = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
import numpy as np
from PIL import Image
import lw_render as LW
import hud2, cv_lib, hud_rows
R = LW.R
J = R.A.J
rec = {}
for beat, key in (('p1', 'f1'), ('p2', 'f2'), ('p3', 'f2')):
    L = cv_lib.L2()
    cv_lib.NOW['words'] = True
    saved = hud2.SCHED
    hud2.SCHED = R.ENAMEL if hasattr(R, 'ENAMEL') else saved
    bottom = hud2.draw_hud(L, J[key], beat, None)
    hud2.SCHED = saved
    im = L.done()
    bg = Image.new('RGBA', im.size, (24, 26, 34, 255))
    bg.alpha_composite(im)
    bg.crop((1040, 0, 1920, 700)).convert('RGB').save(OUT + '/hud_%s.png' % beat)
    a = np.asarray(im.split()[3]) >= 32
    ys, xs = np.nonzero(a)
    rec[beat] = dict(bottom=bottom, rows={k: v for k, v in hud_rows.ROWS.items() if not isinstance(v, (list, dict))},
                     alpha_box=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
    print(beat, json.dumps(rec[beat]), flush=True)
json.dump(rec, open(OUT + '/hud_rows.json', 'w'), indent=1)
