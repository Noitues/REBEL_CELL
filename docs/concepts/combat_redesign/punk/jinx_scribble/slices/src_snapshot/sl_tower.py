"""sl_tower: render towers. python sl_tower.py VAR STATEKEY [all]  -> out/tw_VAR_KEY[_all].png ; 'all' = every slice pending loss"""
import sys, json, copy, time
sys.dont_write_bytecode = True
import asm_r2 as AA
AA.setup()
import f1_tower as FT
import js_tower as JT
import js_slices as JS
from PIL import Image
ROOT = 'D:/rc_scratch/combat_redesign/punk_slices/jinx_scribble/'
var, key = sys.argv[1], sys.argv[2]
allp = len(sys.argv) > 3 and sys.argv[3] == 'all'
calm = len(sys.argv) > 3 and sys.argv[3] == 'calm'
mode = sys.argv[4] if len(sys.argv) > 4 else 'new'
JT.install()
if mode == 'new':
    JS.install()
JT.VAR[0] = var
J = json.load(open(ROOT + 'state_e10.json'))
f = copy.deepcopy(J[key])
if calm:
    for w in f['wheel']:
        w['hp_after'] = w['hp']
if allp:
    for w in f['wheel']:
        w['hp_after'] = 0
t = time.time()
im, cv = FT.render_tower(f, name='BREAKER')
out = ROOT + 'out/tw_%s_%s%s%s.png' % (var, key, '_all' if allp else ('_calm' if calm else ''), '' if mode == 'new' else '_old')
im.save(out)
cv.rgba().save(out.replace('.png', '_hi.png'))
print(out, round(time.time() - t))
