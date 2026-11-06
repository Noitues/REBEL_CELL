"""dbg_band2.py <name> <x> <y> : 9x9 neighbourhood of a pixel: plate rgb, board rgb, pen_all / wax / lit / hover masks"""
import sys
sys.dont_write_bytecode = True
import numpy as np
import hv_checks as HC
g = HC.g
name, x, y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rep, M, lit, rgb, bg, probe = HC.load(name)
pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = HC.board_mask_sets(M)
r = 4
for yy in range(y - r, y + r + 1):
    row = []
    for xx in range(x - r, x + r + 1):
        c = rgb[yy, xx].astype(int)
        f = ('A' if pen_all[yy, xx] else '.') + ('w' if pen_wax[yy, xx] else '.') + ('h' if hover[yy, xx] else '.') + ('L' if lit[yy, xx] >= 128 else '.')
        row.append('%3d,%3d,%3d %s' % (c[0], c[1], c[2], f))
    print(' | '.join(row))
print('board')
for yy in range(y - r, y + r + 1):
    print(' | '.join('%3d,%3d,%3d' % tuple(bg[yy, xx].astype(int)) for xx in range(x - r, x + r + 1)))
