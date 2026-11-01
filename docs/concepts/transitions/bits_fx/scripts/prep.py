# Builds the shared layers (960x540) for the bits FX options. Run: python prep.py
import numpy as np, os
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'work')
PLATE = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/p1_decide.png'
BARE = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png'
W, H = 960, 540
P = np.asarray(Image.open(PLATE).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
B = Image.open(BARE).convert('RGB').resize((W, H), Image.LANCZOS)
best = None
for sig in (0, 1, 2, 3, 4, 6):
    Bb = np.asarray(B.filter(ImageFilter.GaussianBlur(sig)) if sig else B).astype(np.float32)
    reg = (slice(200, 400), slice(560, 940))
    fit = np.zeros_like(Bb); err = 0
    for c in range(3):
        x = Bb[reg][..., c].ravel(); y = P[reg][..., c].ravel()
        a, b = np.polyfit(x, y, 1); fit[..., c] = a * Bb[..., c] + b
        err += np.abs(a * x + b - y).mean()
    print('sigma', sig, 'err', err / 3)
    if best is None or err < best[0]: best = (err, sig, fit)
fit = best[2]; print('chosen sigma', best[1])
yy, xx = np.mgrid[0:H, 0:W]
CX, CY, RD = 267.5, 267.5, 259.0
r = np.hypot(xx - CX, yy - CY)
disk = r <= RD
diff = np.abs(P - fit).max(-1)
m = diff > 30
m = ndi.binary_closing(m, iterations=3)
m = ndi.binary_opening(m, iterations=1)
m = ndi.binary_dilation(m, iterations=2)
m = ndi.binary_fill_holes(m)
rects = np.zeros_like(m)
for (x0, y0, x1, y1) in [(528, 2, 952, 198), (498, 400, 832, 540), (822, 420, 952, 536), (8, 478, 120, 534)]:
    rects[y0:y1, x0:x1] = True
m &= rects
m |= disk
# drop tiny blobs outside the disk
lab, n = ndi.label(m & ~disk)
sizes = ndi.sum(m & ~disk, lab, range(1, n + 1))
for i, s in enumerate(sizes, 1):
    if s < 300: m[lab == i] = False
mf = ndi.gaussian_filter(m.astype(np.float32), 0.8)
mf = np.where(disk, 1.0, mf)
mr = np.maximum(ndi.gaussian_filter(rects.astype(np.float32), 0.8), mf)
bgfull = P * (1 - mr[..., None]) + fit * mr[..., None]
np.savez_compressed(os.path.join(OUT, 'layers.npz'), P=P, bare=np.asarray(B).astype(np.float32), fit=fit, M=mf, bgfull=bgfull, disk=disk)
Image.fromarray((mf * 255).astype(np.uint8)).save(os.path.join(OUT, 'mask.png'))
Image.fromarray(np.clip(bgfull, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'bgfull.png'))
# radial profile of salient pixels in the disk
sat = P.max(-1) - P.min(-1); lum = P.mean(-1)
sal = disk & ((sat > 90) | (lum > 150))
rr = r[sal].astype(int)
hist = np.bincount(rr, minlength=int(RD) + 1)
print('hist peaks'); 
pk = [i for i in range(2, len(hist) - 2) if hist[i] > 40 and hist[i] == hist[i - 2:i + 3].max()]
print(pk, [int(hist[i]) for i in pk])
