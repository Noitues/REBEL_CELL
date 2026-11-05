"""probe_fgring.py <corp> <real.png> -- the round-2 transfer at the r ~ 451 ring: F (flat-0 render), F + 128 T (the flat-128 render), and
the backdrop the real render would need there, (real - F) / T, along a radial line; plus a 6x crop of F, F+128T and the real."""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
W = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/'
z = np.load(W + 'fg_%s.npz' % sys.argv[1])
F = z['F'].astype(np.float32)
T = z['T'].astype(np.float32)
real = np.asarray(Image.open(sys.argv[2]).convert('RGB'), np.float32)
C = (536, 540)
# radial line toward 20 deg below the +x axis (x ~ 960, y ~ 690)
ang = np.radians(19.5)
for r in range(436, 470):
    x = int(round(C[0] + r * np.cos(ang)))
    y = int(round(C[1] + r * np.sin(ang)))
    print(r, (x, y), 'F', F[y, x].astype(int), 'F+128T', (F[y, x] + 128 * T[y, x]).astype(int), 'T', T[y, x].round(3), 'real', real[y, x].astype(int))
box = (900, 600, 990, 700)
ims = [np.clip(F, 0, 255), np.clip(F + 128 * T, 0, 255), real]
out = Image.new('RGB', (90 * 6 * 3 + 16, 100 * 6), (255, 0, 255))
for i, a in enumerate(ims):
    c = Image.fromarray(a.astype(np.uint8)).crop(box).resize((540, 600), Image.NEAREST)
    out.paste(c, (i * 548, 0))
out.save(W + 'fgring_%s.png' % sys.argv[1])
