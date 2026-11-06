import sys, os
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import lw_render as LW
from PIL import Image
R = LW.R
A = R.A
from cv_lib import L2
L = L2()
f = A.J['f1']
A.S2.SKIP_LABELS[0] = True
A.S2.schedule(L, f['schedule'], {})
A.S2.SKIP_LABELS[0] = False
L.done().crop((470, 110, 640, 200)).resize((680, 360), Image.NEAREST).save('dg_sched.png')
L = L2()
A.S2.digits(L, 'P')
L.done().crop((470, 110, 640, 200)).resize((680, 360), Image.NEAREST).save('dg_dig.png')
L = L2()
A.S2.schedule(L, f['schedule'], {})
A.S2.digits(L, 'P')
R.paint_cells(L, f, 'p1')
L.done().crop((470, 110, 640, 200)).resize((680, 360), Image.NEAREST).save('dg_cells.png')
print(A.S2.__file__, A.S2.digits)
