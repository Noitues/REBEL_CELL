"""City-all-corps round 5: the A2 terrain heightfield (pure numpy; called by zoning_a2.py).

H (BU, one value per lot cell centre, over the plan grid + MG cells of margin on every side):
  * the JSON hills (Gaussians, height_m x vertical exaggeration / 16.67 m per BU);
  * foothills and ridged MOUNTAINS rising round the inland edges, from the outer ring (distance d_out in cells): a seeded
    noise ring, a far horizon ridge at the edge of the modelled ground;
  * the coast: beaches (a gentle slope into the water), and cliffs on the stretches a seeded noise picks outside the city;
  * flat zones: the HQ discs (rigid, at the hill's own height), the port, the airport, the spaceport pad.
Every vertex of the city is later lifted by H(x, y) (city_build.Acc.obj), so buildings, decks, piers and lights all follow the
ground; slope and `outer` (the probability of an outer suburb block) tell the builders where not to build.
"""
import math

import numpy as np


def dist_to(mask):
    INF = 1e9
    h, w = mask.shape
    d = np.where(mask, 0.0, INF).astype(np.float64)
    for j in range(h):
        row = d[j]
        prev = d[j - 1] if j else None
        for i in range(w):
            v = row[i]
            if i:
                v = min(v, row[i - 1] + 1.0)
            if prev is not None:
                v = min(v, prev[i] + 1.0)
                if i:
                    v = min(v, prev[i - 1] + 1.414)
                if i < w - 1:
                    v = min(v, prev[i + 1] + 1.414)
            row[i] = v
    for j in range(h - 1, -1, -1):
        row = d[j]
        nxt = d[j + 1] if j < h - 1 else None
        for i in range(w - 1, -1, -1):
            v = row[i]
            if i < w - 1:
                v = min(v, row[i + 1] + 1.0)
            if nxt is not None:
                v = min(v, nxt[i] + 1.0)
                if i < w - 1:
                    v = min(v, nxt[i + 1] + 1.414)
                if i:
                    v = min(v, nxt[i - 1] + 1.414)
            row[i] = v
    return d


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def vnoise(n, cell, seed):
    """smooth value noise over an n x n lattice of cells (vectorised), in [0, 1)."""
    rng = np.random.default_rng(seed)
    m = int(n / cell) + 3
    g = rng.random((m, m))
    ii, jj = np.meshgrid(np.arange(n) / cell, np.arange(n) / cell)
    x0, y0 = np.floor(ii).astype(int), np.floor(jj).astype(int)
    fx, fy = ii - x0, jj - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    v = (g[y0, x0] * (1 - sx) + g[y0, x0 + 1] * sx) * (1 - sy) + (g[y0 + 1, x0] * (1 - sx) + g[y0 + 1, x0 + 1] * sx) * sy
    return v


def build(n2, hi0, hj0, water_p, drowned_p, r2_in_p, hq_lots, flat_masks, hills_lots, cx, cy, P):
    """-> H, slope, outer  (all n2 x n2 float32, index [row j, col i]); hills_lots = [(x_lot, y_lot, sx_cells, sy_cells, h_bu, rot)]."""
    jj, ii = np.mgrid[0:n2, 0:n2]
    xl, yl = ii + hi0 + 0.5, jj + hj0 + 0.5                    # lot coords of the cell centres
    H = np.zeros((n2, n2))
    for (hx, hy, sx, sy, hb, rot) in hills_lots:
        dx, dy = xl - hx, -(yl - hy)                             # east, north (cells)
        c, s = math.cos(rot), math.sin(rot)
        u, v = dx * c + dy * s, -dx * s + dy * c
        H += hb * np.exp(-0.5 * ((u / sx) ** 2 + (v / sy) ** 2))
    d_out = dist_to(r2_in_p)                                      # cells outside the outer ring (0 inside)
    d_w = dist_to(water_p)                                        # cells from the water (0 in it)
    land = ~water_p
    n_a = vnoise(n2, 40.0, P["seed"]) * 0.55 + vnoise(n2, 16.0, P["seed"] + 1) * 0.3 + vnoise(n2, 6.0, P["seed"] + 2) * 0.15
    rid = 1.0 - np.abs(2.0 * vnoise(n2, 48.0, P["seed"] + 3) - 1.0)
    rid2 = 1.0 - np.abs(2.0 * vnoise(n2, 20.0, P["seed"] + 4) - 1.0)
    t_f = smooth(d_out, P["foot"][0], P["foot"][1])
    t_m = smooth(d_out, P["mtn"][0], P["mtn"][1])
    mount = P["foot_h"] * t_f * (0.35 + n_a) + P["mtn_h"] * t_m ** 1.35 * (0.4 + 0.85 * (0.62 * rid + 0.38 * rid2) + 0.35 * n_a)
    mount *= 1.0 + P["edge_k"] * smooth(d_out, P["edge"][0], P["edge"][1])      # the far horizon ridge
    for _ in range(2):                                                            # soften the facets (a box blur of the ridges)
        r_ = 2
        for ax in (0, 1):
            c = np.cumsum(np.pad(mount, [(r_ + 1, r_) if k == ax else (0, 0) for k in range(2)], mode="edge"), axis=ax)
            hi = np.take(c, np.arange(2 * r_ + 1, 2 * r_ + 1 + n2), axis=ax)
            lo = np.take(c, np.arange(0, n2), axis=ax)
            mount = (hi - lo) / (2 * r_ + 1)
    mount *= smooth(d_w, 1.5, 9.0)                                                # no mountain on the beach
    H += mount * land
    H += P["base"]                                                                # the street level (the sea is at 0)
    # cliffs (outside the city only) where a noise says so; beaches elsewhere
    cliff = smooth(vnoise(n2, 30.0, P["seed"] + 7), 0.50, 0.66) * smooth(d_out, 1.0, 6.0)
    H += P["cliff_h"] * cliff * smooth(d_w, 0.5, 3.0) * land * (1.0 - smooth(d_w, 3.0, 9.0))
    beach = 0.35
    ck = smooth(d_w, 1.0, 3.0)
    Hl = H * ck + beach * (1.0 - ck)
    H = np.where(land, Hl, 0.0)
    # flat zones (rigid under the landmarks, the port, the airport, the spaceport)
    for (m, target, soft) in flat_masks:
        d_m = dist_to(m)
        w = 1.0 - smooth(d_m, 0.5, soft)
        tgt = P['base'] if target is not None else P['base']
        H = H * (1 - w) + tgt * w
    for (hx, hy, rin, rout) in hq_lots:
        r = np.hypot(xl - hx, yl - hy)
        w = 1.0 - smooth(r, rin, rout)
        ci, cj = int(hx - hi0), int(hy - hj0)
        t = float(H[min(max(cj, 0), n2 - 1), min(max(ci, 0), n2 - 1)])
        H = H * (1 - w) + t * w
    gy, gx = np.gradient(H)
    slope = np.hypot(gx, gy) / 1.0                                # BU per cell; /6 BU = dimensionless
    slope = slope / 6.0
    # the outer suburbs: a fading probability outside the outer ring on flat low ground
    outer = (1.0 - smooth(d_out, P["outer"][0], P["outer"][1])) * land * (1.0 - smooth(slope, 0.10, 0.28)) * (1.0 - smooth(H, 18.0, 40.0))
    return H.astype(np.float32), slope.astype(np.float32), outer.astype(np.float32), d_w.astype(np.float32)
