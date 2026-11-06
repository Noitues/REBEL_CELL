"""dbg_cell.py <name> <dep> <sector> : the a-check sample of one cell on a hover plate vs the board under it (L*), crop with the sample tinted"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import hv_checks as HC
RC, T = HC.RC, HC.T

name, dep, sec = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rep, M, lit, rgb, bg, probe = HC.load(name)
Mx = HC.rb_inputs(rep, M)
geo = HC.gate_cells(rep['geometry'], lit, ())
yy, xx = np.mgrid[0:1080, 0:1920]
cut = np.zeros((1080, 1920), bool)
for k in RC.CUT:
    if k in Mx:
        cut |= Mx[k]
cut = HC.dil(cut, 3)
rho = np.hypot(xx - RC.CC[0], yy - RC.CC[1])
tray = np.zeros((1080, 1920), bool)
for u in geo['units']:
    cut |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 8
    tray |= (rho >= u['t_in'] - 3) & (rho <= u['t_out'] + 3)
mx, mn = rgb.max(2), rgb.min(2)
sat = (mx - mn) / np.maximum(mx, 1)
pinkish = (sat > 0.45) & (rgb[..., 0] > 150) & (rgb[..., 2] > 90) & (rgb[..., 1] < 140)
cut |= HC.dil(pinkish, 2)
Y = T.lum(rgb)
Yb = T.lum(bg)
for c in geo['cells']:
    if c['dep'] != dep or c['s'] != sec:
        continue
    full = ndi.binary_erosion(RC.poly_mask([c['poly']]), iterations=4)
    m = full & ~cut & ~tray
    print('cell', c['state'], c.get('uid'), 'lit_frac', c.get('lit_frac'), 'full px', int(full.sum()), 'sample px', int(m.sum()))
    print('  plate L* sample %.1f   board L* same px %.1f   board L* full glass (no cut) %.1f' % (
        T.lstar(Y[m].mean()), T.lstar(Yb[m].mean()), T.lstar(Yb[full & ~tray].mean())))
    print('  lit on sample: min %d mean %.1f' % (lit[m].min(), lit[m].mean()))
    for k in sorted(Mx):
        o = int((Mx[k] & full).sum())
        if o:
            print('   mask %-16s on glass %d px' % (k, o))
    ys, xs = np.nonzero(full)
    x0, y0, x1, y1 = xs.min() - 20, ys.min() - 20, xs.max() + 20, ys.max() + 20
    im = rgb.copy()
    im[m] = im[m] * 0.4 + np.array([0, 255, 255]) * 0.6
    im[full & ~m] = im[full & ~m] * 0.7 + np.array([255, 0, 0]) * 0.3
    Image.fromarray(im[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(
        HC.HERE + 'dbg/cell_%s_%d_%d.png' % (name, dep, sec))
    Image.fromarray(rgb[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(
        HC.HERE + 'dbg/cell_%s_%d_%d_raw.png' % (name, dep, sec))
    Image.fromarray(bg[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST).save(
        HC.HERE + 'dbg/cell_%s_%d_%d_board.png' % (name, dep, sec))
    print('  crop', x0, y0, x1, y1)
