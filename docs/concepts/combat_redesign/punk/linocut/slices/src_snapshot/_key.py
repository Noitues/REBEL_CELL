"""key sheet source: clean + all-pending towers per variant, saved at 1x RGBA for wedge crops"""
import sys, json, copy
sys.dont_write_bytecode = True
import asm_r2 as A
A.setup()
import lc_tower as LT
from PIL import Image
J = json.load(open('D:/rc_scratch/combat_redesign/punk_slices/linocut/state_e10.json'))
O = 'D:/rc_scratch/combat_redesign/punk_slices/linocut/out/'
types = ['BURST', 'TURRET', 'SHIELD', 'REPAIR', 'BURST', 'TURRET']
for v in sys.argv[1:]:
    LT.VARIANT[0] = v
    f = copy.deepcopy(J['f1'])
    for i, w in enumerate(f['wheel']):
        w['t'] = types[i]; w['hp_after'] = w['hp']
    im, _ = LT.FT.render_tower(f, name='')
    im.save(O + 'key_%s_clean.png' % v)
    for w in f['wheel']:
        w['hp_after'] = 0
    im, _ = LT.FT.render_tower(f, name='')
    im.save(O + 'key_%s_pend.png' % v)
print('ok')
