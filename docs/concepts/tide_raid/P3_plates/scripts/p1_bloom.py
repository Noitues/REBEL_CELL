"""Bloom necrosis field for the city shell: image over the height-field grid (row = Godot z index, col = x index).
R: front value (0.5 = the hot hairline, >0.5 infected), G: climb height / 64 BU (how far up the facades it has crept)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import p1lib as L


def fbm_grid(shape, seed, scales=(96, 40, 18)):
    rng = np.random.RandomState(seed)
    out = np.zeros(shape, np.float32)
    amp = 1.0
    for sc in scales:
        g = rng.rand(shape[0] // sc + 3, shape[1] // sc + 3).astype(np.float32)
        z = ndi.zoom(g, sc, order=3)[:shape[0], :shape[1]]
        out += (z - 0.5) * amp
        amp *= 0.55
    return out


def make_field(B, name, spread=1.0, seed=11):
    hf = L.hf()
    nz, nx = hf['H'].shape
    c = float(hf['cell']); x0 = float(hf['x0']); z0 = float(hf['z0'])
    gx = x0 + (np.arange(nx) + 0.5) * c
    gz = z0 + (np.arange(nz) + 0.5) * c
    GX, GZ = np.meshgrid(gx, gz)
    warp = fbm_grid((nz, nx), seed)
    wx = GX + warp * 30.0 * spread
    wz = GZ + fbm_grid((nz, nx), seed + 1) * 30.0 * spread
    # sources: Godot world (x, z) of the Sites it has eaten, HOME, and tendrils along the route streets
    srcs = []
    for sid in ('t1_a', 't1_b', 't1_c', 't1_d', 't2_breach', 't2_virus', 't2_intel'):
        g = B.site_g(sid)
        srcs.append((g[0], g[2], 46.0 * spread))
    hg = L.screen_to_ground(B.w.home.reshape(1, 2))[0]
    srcs.append((hg[0], hg[2], 44.0 * spread))
    s = np.full((nz, nx), -1e9, np.float32)
    for (sx, sz, r) in srcs:
        d = np.hypot(wx - sx, wz - sz)
        s = np.maximum(s, r - d)
    # tendrils along the K1/K2 streets (world x,z)
    for rid in ('K1', 'K2'):
        R = B.routes[rid]
        pts = L.g2b  # (unused)
        g = R.gw
        for a, b in zip(g[:-1:2], g[2::2]):
            for t in np.linspace(0, 1, 3):
                p = a + (b - a) * t
                d = np.hypot(wx - p[0], wz - p[2])
                s = np.maximum(s, 9.0 * spread - d * 1.2 + 6.0)
    sn = np.clip(0.5 + s / 80.0, 0, 1)
    climb = np.clip(s * 0.9 + 6.0, 0, 62) + (fbm_grid((nz, nx), seed + 2) * 14.0)
    climb = np.clip(climb, 0, 63.9)
    img = np.zeros((nz, nx, 3), np.uint8)
    img[..., 0] = (sn * 255).astype(np.uint8)
    img[..., 1] = (climb / 64.0 * 255).astype(np.uint8)
    path = L.WORK + 'tex/bloom_%s.png' % name
    Image.fromarray(img).save(path)
    return path
