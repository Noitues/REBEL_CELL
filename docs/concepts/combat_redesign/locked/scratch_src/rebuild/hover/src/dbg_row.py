import sys
sys.dont_write_bytecode = True
import numpy as np
import hv_checks as HC
name, y, x0, x1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rep, M, lit, rgb, bg, probe = HC.load(name)
for k in ('P__L6_all', 'P__L6_wax', 'P__L5_all', 'Z__hover', 'Z__arcs'):
    m = HC.g(M, k)
    print('%-10s' % k[:10], ''.join('#' if m[y, x] else '.' for x in range(x0, x1)))
print('L*        ', ' '.join('%d' % v for v in HC.T.lstar(HC.T.lum(rgb[y, x0:x1]))))
