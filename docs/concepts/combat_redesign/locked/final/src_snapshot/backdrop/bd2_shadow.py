"""bd2_shadow.py : how much of each beat's room region is darkened by the board / hand / HUD transfer (T_est < 0.85), and the region mean
with and without those pixels; plus the mean by vertical band"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
import bd2_beats as BB
import rb_tokens as TK

for b in BB.BEATS:
    T, reg, pl = BB.transfer(b)
    t = T.mean(-1)
    Y = TK.lum(pl.astype(np.float64))
    sh = reg & (t < 0.85)
    ok = reg & ~sh
    bands = []
    for y0 in range(420, 1080, 110):
        sel = reg.copy(); sel[:y0] = False; sel[y0 + 110:] = False
        bands.append('%d:%s' % (y0, ('%.1f(%dk)' % (float(TK.lstar(Y[sel].mean())), sel.sum() // 1000)) if sel.any() else '-'))
    print('%-8s shadowed %5.1f %%  mean all %.1f  unshadowed %.1f | %s' % (b, 100 * sh.sum() / reg.sum(), float(TK.lstar(Y[reg].mean())),
          float(TK.lstar(Y[ok].mean())), ' '.join(bands)))
