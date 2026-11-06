"""render the tower alone for A and B, state f1 + an all-pending state"""
import sys, json, copy
sys.dont_write_bytecode = True
import asm_r2 as A
A.setup()
import lc_tower as LT
from PIL import Image
J = json.load(open('D:/rc_scratch/combat_redesign/punk_slices/linocut/state_e10.json'))
O = 'D:/rc_scratch/combat_redesign/punk_slices/linocut/out/'
for v in sys.argv[1:]:
    LT.VARIANT[0] = v
    f = J['f1']
    im, _ = LT.FT.render_tower(f)
    bg = Image.new('RGBA', im.size, (30, 26, 52, 255)); bg.alpha_composite(im)
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save(O + 'tw_%s.png' % v)
    g = copy.deepcopy(f)
    for w in g['wheel']:
        w['hp_after'] = 0
    im, _ = LT.FT.render_tower(g)
    bg = Image.new('RGBA', im.size, (30, 26, 52, 255)); bg.alpha_composite(im)
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save(O + 'tw_%s_allpend.png' % v)
print('ok')
