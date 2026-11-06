"""C14 determinism assert (round 2; runs before every publish): in ONE process render p3 <skin>, then p1_clean (f1 with no units, no guns,
no arcs), then p3 <skin> again; the two p3 renders must be pixel-identical, the KA_* glyph registry must still hold the asm_glyphs master
entries after every render (rb4_patch.registry_ok), and the old e10 card library must have loaded (so the restore was exercised).
Exit status 0 = pass, 1 = fail.  Writes <outdir>/c14_assert.json.
python c14_assert.py <skin> <outdir>"""
import sys, os, copy, time, json
sys.dont_write_bytecode = True
skin = sys.argv[1]
OUT = sys.argv[2]
os.environ['CORP'] = skin
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
os.makedirs(OUT, exist_ok=True)
CW = OUT + '/tower_cache/'
os.makedirs(CW, exist_ok=True)
import lw_render as LW
import bd_grade as BG
import numpy as np
from PIL import Image
import rb4_patch as RB4
import wr2_units as W2U
R = LW.R
R.WORK = CW
A = R.A
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(skin, 'bio')
J = A.J
rep = dict(skin=skin, steps=[])
ims = []
for i, kind in enumerate(('p3', 'p1_clean', 'p3')):
    t = time.time()
    if kind == 'p3':
        im = R.render('p3', room=ROOM)
    else:
        f1 = copy.deepcopy(J['f1'])
        ids = tuple(u['id'] for u in f1['units'])
        f1['units'] = []
        og = R.FG.make_guns
        R.FG.make_guns = lambda f, k, w: (Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)), None)
        try:
            im = R.render('p1', room=ROOM, frame=f1, tag='r2_f1clean', arcs_skip=ids)
        finally:
            R.FG.make_guns = og
    ok, bad = RB4.registry_ok()
    rep['steps'].append(dict(i=i, kind=kind, s=round(time.time() - t, 1), registry_ok=ok, registry_bad=bad, old_library_loaded='k' in W2U._LIB,
                             restored=RB4.INFO.get('c14_library_restored')))
    print(rep['steps'][-1], flush=True)
    if kind == 'p3':
        ims.append(np.asarray(im.convert('RGB'), np.int16))
        im.save(OUT + '/%d_p3_%s.png' % (i, skin))
d = np.abs(ims[0] - ims[1]).max(axis=2)
rep['p3_vs_p3_max_diff'] = int(d.max())
rep['p3_vs_p3_px_differing'] = int((d > 0).sum())
rep['pass'] = rep['p3_vs_p3_px_differing'] == 0 and all(s['registry_ok'] for s in rep['steps']) and any(s['old_library_loaded'] for s in rep['steps'])
json.dump(rep, open(OUT + '/c14_assert.json', 'w'), indent=1)
print('C14 ASSERT', 'PASS' if rep['pass'] else 'FAIL', rep['p3_vs_p3_px_differing'], 'px differ', flush=True)
sys.exit(0 if rep['pass'] else 1)
