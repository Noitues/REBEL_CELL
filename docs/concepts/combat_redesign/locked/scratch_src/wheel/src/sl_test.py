"""sl_test: render the tower alone. usage: sl_test.py VAR mode out [ss]  mode: f1 | intact | broken"""
import sys, json, copy, os
sys.dont_write_bytecode = True
var, mode, out = sys.argv[1], sys.argv[2], sys.argv[3]
if len(sys.argv) > 4: os.environ['XF_SS'] = sys.argv[4]
import asm_r2 as A
A.setup()
import xf_tower as T
from PIL import Image
T.VAR[0] = var
J = json.load(open('D:/rc_scratch/combat_redesign/locked/wheel/state_e10.json'))
f = copy.deepcopy(J['f1'])
if mode in ('intact', 'broken'):
    for w in f['wheel']:
        w['hp'] = 2; w['hp_after'] = 2 if mode == 'intact' else 0
im, cv = T.render_tower(f, with_trim=False)
scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1
im = cv.to_image(scale=scale)
bg = Image.new('RGBA', im.size, (24, 22, 36, 255)); bg.alpha_composite(im)
bg.convert('RGB').save(out)
print('ok', im.size)
