"""P2 per-pixel geometry from the Godot depth recon: height above ground (hag), surface normal, street / park / water masks, facade walls.
python p2_geo.py -> WORK/geo.npz"""
import numpy as np
from scipy import ndimage as ndi
import p1lib as L

import os
S = int(os.environ.get('P2_S', '1'))
W, H = 1920 * S, 1080 * S
REC = 'recon15.npz' if S == 1 else 'recon30.npz'
GEO = 'geo.npz' if S == 1 else 'geo30.npz'


def build():
    z = np.load(L.WORK + REC)
    P = z['P'].astype(np.float32); idm = z['idm']
    g = L.ground(P[..., 0], P[..., 2]).astype(np.float32)
    hag = P[..., 1] - g
    Ps = np.stack([ndi.gaussian_filter(P[..., i], 0.8 * S) for i in range(3)], -1)
    dx = np.gradient(Ps, axis=1); dy = np.gradient(Ps, axis=0)
    n = np.cross(dx, dy)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    # orient towards camera (BACK)
    s = np.sign((n * L.BACK).sum(-1, keepdims=True)); s[s == 0] = 1
    n = n * s
    np.savez_compressed(L.WORK + GEO, hag=hag, n=n.astype(np.float16), idm=idm)
    return hag, n, idm


if __name__ == '__main__':
    hag, n, idm = build()
    print(hag.min(), hag.max(), np.percentile(hag, [5, 50, 95]))
