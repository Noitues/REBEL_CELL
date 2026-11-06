"""js_big: renders the 3x tower (A or B) and the line-sample strip for the style board.  python js_big.py A"""
import sys, json, time
sys.dont_write_bytecode = True
import asm_r2 as AA
AA.setup()
import f1_tower as FT
import js_tower as JT
from f1_lib import Canvas
from PIL import Image
ROOT = 'D:/rc_scratch/combat_redesign/punk/jinx_scribble/'
var = sys.argv[1]
JT.install()
JT.VAR[0] = var
J = json.load(open(ROOT + 'state_e10.json'))
t = time.time()
im, cv = FT.render_tower(J['f1'], name='BREAKER')
cv.rgba().save(ROOT + 'work/big_tower_%s.png' % var)
print('tower', time.time() - t)
