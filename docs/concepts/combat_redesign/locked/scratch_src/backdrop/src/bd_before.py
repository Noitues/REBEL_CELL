"""bd_before: the current (locked final) backdrop grade on all 7 rooms behind the neutral p1 board; measure; cache the plates."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image
import bd_measure as M

out = {}
real = np.asarray(Image.open(M.HERE + 'work/real_p1_neutral.png'), np.float32)
pub = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p1_decide.png').convert('RGB'), np.float32)
out['_check_generator_vs_published_p1'] = dict(mean_abs=float(np.abs(real - pub).mean()), max=float(np.abs(real - pub).max()))
for corp, rooms in (('neutral', M.ROOMS), ('solace', ['bio']), ('meridian', ['bio'])):
    reg = M.regions(corp)
    for r in rooms:
        bd = M.before_backdrop(r)
        pl = M.compose(bd, corp)
        Image.fromarray(pl.astype(np.uint8)).save(M.HERE + 'work/before_%s_%s.png' % (r, corp))
        np.save(M.HERE + 'work/before_bd_%s.npy' % r, bd.astype(np.uint8)) if corp == 'neutral' else None
        out['%s_%s' % (r, corp)] = M.measure(pl, corp, reg)
        print(r, corp, json.dumps(out['%s_%s' % (r, corp)]), flush=True)
json.dump(out, open(M.HERE + 'work/before.json', 'w'), indent=1)
