import sys, os
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
os.chdir('D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import lw_render as LW
R = LW.R
A = R.A
import wr2_cells as W2C, asm_r2
print('W2C.screen', W2C.screen.__module__, W2C.screen.__qualname__)
print('asm_r2.W2C is W2C', asm_r2.W2C is W2C, 'R.paint_cells', R.paint_cells.__module__)
from cv_lib import L2
from PIL import Image
f = A.J['f1']
L = L2()
R.paint_cells(L, f, 'p1')
bg = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
bg.alpha_composite(L.done())
bg.convert('RGB').save('D:/rc_scratch/combat_redesign/locked/rebuild/work/dbg_cells.png')
L = L2()
W2C.screen(L, [u for u in f['units'] if u['id'] == 1][0])
bg = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
bg.alpha_composite(L.done())
bg.convert('RGB').save('D:/rc_scratch/combat_redesign/locked/rebuild/work/dbg_screen.png')
import gram as G
print(G.kind_wash('Packet', 0, ramp=(0, 0, 0)))
import rb_patch as RB
print(RB.at_lstar(G.kind_wash('Packet', 0, ramp=(0, 0, 0)), 44.5))
