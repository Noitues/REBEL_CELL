import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T
from rb_patch import at_lstar
for nm, c in (('CREAM', T.hx('FFF4D6')), ('ENAMEL', T.hx('D9E1EA')), ('WHITE', (242, 246, 255)), ('FULL', (235, 240, 248))):
    for L in (80, 82, 84):
        o = at_lstar(c, L)
        print(nm, L, '#%02X%02X%02X' % o, o, round(float(T.lstar(T.lum(np.array(o, float)))), 1))
