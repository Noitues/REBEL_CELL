"""whichmask.py <sfx> x y [r]: capture mask classes present within r px of a pixel"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_checks as RC
sfx, x, y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
M = RC.load_masks(sfx)
print([k for k, m in M.items() if m[y - r:y + r + 1, x - r:x + r + 1].any()])
import json
g = json.load(open(RC.WORK + 'chk_%s.json' % sfx))['rb']['geometry']
import numpy as np
print('rho %.1f' % np.hypot(x - 536, y - 540))
