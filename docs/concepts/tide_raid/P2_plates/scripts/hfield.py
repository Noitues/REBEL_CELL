"""P1: heightfield + ground model from the recon npz. python hfield.py recon.npz out_hf.npz [cell]
H: max world Y per (X,Z) cell (roofs, walls, ground).  G: smooth terrain under the city (class-4 ground pixels, interpolated)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.interpolate import griddata
z = np.load(sys.argv[1])
P = z['P']; idm = z['idm']
cell = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
m = idm != 0
X = P[..., 0][m]; Y = P[..., 1][m]; Zc = P[..., 2][m]
x0, z0 = X.min() - 1, Zc.min() - 1
nx = int((X.max() - x0) / cell) + 3
nz = int((Zc.max() - z0) / cell) + 3
ix = ((X - x0) / cell).astype(np.int64); iz = ((Zc - z0) / cell).astype(np.int64)
H = np.full((nz, nx), -1e9, np.float32)
np.maximum.at(H, (iz, ix), Y.astype(np.float32))
known = H > -1e8
# ground model from class-4 pixels (min per coarse cell), interpolated and smoothed
g = idm == 4
gc = cell * 6
gnx = int(nx * cell / gc) + 2; gnz = int(nz * cell / gc) + 2
Gm = np.full((gnz, gnx), 1e9, np.float32)
gx = ((P[..., 0][g] - x0) / gc).astype(np.int64); gz = ((P[..., 2][g] - z0) / gc).astype(np.int64)
np.minimum.at(Gm, (gz, gx), P[..., 1][g].astype(np.float32))
pts = np.argwhere(Gm < 1e8)
vals = Gm[Gm < 1e8]
yy, xx = np.mgrid[0:gnz, 0:gnx]
Gi = griddata(pts, vals, (yy, xx), method='linear')
Gn = griddata(pts, vals, (yy, xx), method='nearest')
Gi = np.where(np.isnan(Gi), Gn, Gi)
Gi = ndi.gaussian_filter(Gi, 1.2)
G = ndi.zoom(Gi, (nz / gnz * 1.0, nx / gnx * 1.0), order=1)[:nz, :nx]
if G.shape != H.shape:
    G2 = np.zeros(H.shape, np.float32); G2[:G.shape[0], :G.shape[1]] = G[:H.shape[0], :H.shape[1]]; G = G2
# hidden cells: terrain G (never a roof); known cells keep H (>= G)
Hf = np.where(known, np.maximum(H, G), G).astype(np.float32)
print('grid', nx, nz, 'known', known.mean(), 'G range', G.min(), G.max())
np.savez_compressed(sys.argv[2], H=Hf, G=G.astype(np.float32), known=known, x0=x0, z0=z0, cell=cell)
v = np.clip((Hf - Hf.min()) / (np.percentile(Hf, 99.8) - Hf.min()), 0, 1)
Image.fromarray((v * 255).astype(np.uint8)).save(sys.argv[2].replace('.npz', '_h.png'))
v = np.clip((G - G.min()) / (G.max() - G.min()), 0, 1)
Image.fromarray((v * 255).astype(np.uint8)).save(sys.argv[2].replace('.npz', '_g.png'))
