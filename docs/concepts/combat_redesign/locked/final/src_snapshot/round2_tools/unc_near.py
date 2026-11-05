"""for each unclassed bright pixel (rb_checks_r2 C3 rule) of a plate: its L*, rgb and the capture classes within 4 px.
python unc_near.py <sfx> <png>"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_checks as RC
import rb_tokens as T
sfx, png = sys.argv[1], sys.argv[2]
M = RC.load_masks(sfx)
rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
Ls = T.lstar(T.lum(rgb))
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
cls = np.zeros((1080, 1920), bool)
for k, m in M.items():
    if k != 'scrim':
        cls |= m
unc = (Ls >= T.UNCLASSED_L) & (rho < T.UNCLASSED_R) & ~ndi.binary_dilation(cls, iterations=1)
for y, x in zip(*np.nonzero(unc)):
    near = sorted(k for k, m in M.items() if m[max(0, y - 4):y + 5, max(0, x - 4):x + 5].any())
    print(x, y, 'L* %.1f' % Ls[y, x], 'rgb', rgb[y, x].astype(int).tolist(), 'r %.1f' % rho[y, x], near)
