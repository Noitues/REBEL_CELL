"""city_geo: world <-> screen for the clean Solace night city render (tide_concepts/p2_base, read-only).

The render is an orthographic camera, so screen = A @ (x, y, z) + b exactly (affine).  We fit A, b by least squares on the
per-pixel world positions (layers/world_pos_f16.npz 'P'), then
  - project any world point (ground cells, beacon cones, unit icons at height),
  - test visibility by comparing the world position stored at that pixel (occluded = a building/tree stands in front),
  - build a top-down ground-height map and a top-down street map (1 BU bins) from the visible ground pixels.
The street lattice: the city is laid out on 6 BU lots with edges at 3 mod 6 BU, in world x and z (inspected).
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

BASE = 'D:/rc_scratch/tide_concepts/p2_base/'
LOT = 6.0                    # BU, the city's lot lattice
LOT0 = 3.0                   # lattice edge offset (edges at 3 mod 6)


class City:
    def __init__(self):
        z = np.load(BASE + 'layers/world_pos_f16.npz')
        self.P = z['P'].astype(np.float32)
        self.idm = z['idm']
        self.street = np.asarray(Image.open(BASE + 'layers/street_mask.png')) > 127
        self.occ = np.asarray(Image.open(BASE + 'layers/occluder_mask.png')) > 127
        self.H, self.W = self.P.shape[:2]
        self._fit()
        self._topdown()

    # ------------------------------------------------------------------ the ortho camera
    def _fit(self):
        P = self.P
        ys, xs = np.mgrid[0:self.H:4, 0:self.W:4]
        w = P[ys, xs].reshape(-1, 3)
        X = np.hstack([w, np.ones((len(w), 1), np.float32)]).astype(np.float64)
        sx, sy = xs.ravel().astype(np.float64), ys.ravel().astype(np.float64)
        # robust: two passes, dropping the worst residuals (sky / water far plane, fringes)
        keep = np.ones(len(w), bool)
        for _ in range(3):
            cx, *_ = np.linalg.lstsq(X[keep], sx[keep], rcond=None)
            cy, *_ = np.linalg.lstsq(X[keep], sy[keep], rcond=None)
            r = np.hypot(X @ cx - sx, X @ cy - sy)
            keep = r < max(2.0, np.percentile(r[keep], 95))
        self.cx, self.cy = cx, cy
        self.fit_res = (float(np.median(r)), float(np.percentile(r, 95)))
        A = np.array([cx[:3], cy[:3]])
        # the view direction = the null space of A (points along it project to the same pixel); sign: towards the camera
        _, _, vt = np.linalg.svd(A)
        v = vt[-1]
        if v[1] < 0:                       # the camera looks down: the towards-camera direction has +y
            v = -v
        self.view = v

    def proj(self, x, y, z):
        x, y, z = np.asarray(x, np.float64), np.asarray(y, np.float64), np.asarray(z, np.float64)
        return (self.cx[0] * x + self.cx[1] * y + self.cx[2] * z + self.cx[3],
                self.cy[0] * x + self.cy[1] * y + self.cy[2] * z + self.cy[3])

    # ------------------------------------------------------------------ top-down maps (1 BU bins)
    def _topdown(self):
        P = self.P
        self.tx0, self.tz0 = -600.0, -400.0
        tw, th = 560, 560
        ground = (self.idm == 4) | self.street
        ys, xs = np.nonzero(ground)
        wx, wy, wz = P[ys, xs, 0], P[ys, xs, 1], P[ys, xs, 2]
        ix = np.clip((wx - self.tx0).astype(int), 0, tw - 1)
        iz = np.clip((wz - self.tz0).astype(int), 0, th - 1)
        hsum = np.zeros((th, tw)); hn = np.zeros((th, tw))
        np.add.at(hsum, (iz, ix), wy); np.add.at(hn, (iz, ix), 1)
        ssum = np.zeros((th, tw))
        np.add.at(ssum, (iz, ix), self.street[ys, xs].astype(float))
        self.th_n = hn
        h = np.where(hn > 0, hsum / np.maximum(hn, 1), np.nan)
        # fill holes by growing the mean of known neighbours
        for _ in range(60):
            m = np.isnan(h)
            if not m.any():
                break
            hp = np.pad(h, 1, constant_values=np.nan)
            nb = np.stack([hp[:-2, 1:-1], hp[2:, 1:-1], hp[1:-1, :-2], hp[1:-1, 2:]])
            fill = np.nanmean(np.where(np.isnan(nb), np.nan, nb), axis=0) if True else None
            h = np.where(m & ~np.isnan(fill), fill, h)
        self.hmap = np.nan_to_num(h, nan=0.0)
        self.smap = np.where(hn > 0, ssum / np.maximum(hn, 1), -1.0)      # -1 = never seen

    def ground_h(self, x, z):
        ix = int(np.clip(x - self.tx0, 0, self.hmap.shape[1] - 1))
        iz = int(np.clip(z - self.tz0, 0, self.hmap.shape[0] - 1))
        return float(self.hmap[iz, ix])

    def ground_h_area(self, x0, z0, x1, z1):
        a = self.hmap[int(z0 - self.tz0):int(z1 - self.tz0), int(x0 - self.tx0):int(x1 - self.tx0)]
        return float(np.median(a)) if a.size else 0.0

    def street_frac(self, x0, z0, x1, z1):
        a = self.smap[int(z0 - self.tz0):int(z1 - self.tz0), int(x0 - self.tx0):int(x1 - self.tx0)]
        seen = a >= 0
        return float(a[seen].mean()) if seen.any() else -1.0

    # ------------------------------------------------------------------ visibility
    def visible(self, x, y, z, tol=2.5):
        """True when the world point is what the camera sees at its pixel (nothing stands in front)"""
        px, py = self.proj(x, y, z)
        ix, iy = int(round(float(px))), int(round(float(py)))
        if not (0 <= ix < self.W and 0 <= iy < self.H):
            return False
        q = self.P[iy, ix]
        d = q - np.array([x, y, z], np.float32)
        return float(d @ self.view) < tol

    def vis_mask_for(self, pts_world, tol=2.5):
        return np.array([self.visible(*p, tol=tol) for p in pts_world])

    def occlusion_screen(self, tol=2.5):
        """per-pixel: the pixel's own surface is higher than the ground (a building / tree face): marks on the ground under it
        are hidden.  Returned as float 0..1 (1 = something stands here above the local ground)."""
        P = self.P
        ix = np.clip((P[..., 0] - self.tx0).astype(int), 0, self.hmap.shape[1] - 1)
        iz = np.clip((P[..., 2] - self.tz0).astype(int), 0, self.hmap.shape[0] - 1)
        hg = self.hmap[iz, ix]
        return (P[..., 1] - hg) > tol


def lot_edge(v):
    """the lattice edge at or below v"""
    return np.floor((v - LOT0) / LOT) * LOT + LOT0
