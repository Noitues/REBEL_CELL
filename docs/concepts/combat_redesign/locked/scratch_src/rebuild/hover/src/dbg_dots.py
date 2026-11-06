"""where a pixel dot run comes from: the board, the dimmed board, or the plate"""
import sys, json, numpy as np
sys.dont_write_bytecode = True
from PIL import Image
import hv_checks as HC
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
DA = HC.DA
r0 = DA.audit(Image.fromarray(bg.astype(np.uint8)))
print('board runs', r0['n_runs'], [x['bbox'] for x in r0['runs']])
a = bg.astype(np.float32)
g = a[..., 0:1] * 0.3 + a[..., 1:2] * 0.59 + a[..., 2:3] * 0.11
d = (g + (a - g) * 0.45) * 0.40
mm = (lit.astype(np.float32) / 255.0)[..., None]
dim = np.clip(a * mm + d * (1 - mm), 0, 255).astype(np.uint8)
r1 = DA.audit(Image.fromarray(dim))
print('dimmed board runs', r1['n_runs'], [x['bbox'] for x in r1['runs']])
r2 = DA.audit(Image.fromarray(rgb.astype(np.uint8)))
print('plate runs', r2['n_runs'], [x['bbox'] for x in r2['runs']])
