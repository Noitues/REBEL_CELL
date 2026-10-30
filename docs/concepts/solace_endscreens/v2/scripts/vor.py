"""Voronoi vein field without scipy.spatial (its import hangs on this machine): EDT-based."""
import numpy as np
from scipy import ndimage as ndi


def edge_dist(h, w, n, seed):
    """Distance in px from each pixel to the nearest Voronoi cell border (n random seeds)."""
    rng = np.random.default_rng(seed)
    m = np.ones((h, w), bool)
    m[rng.integers(0, h, n), rng.integers(0, w, n)] = False
    _, idx = ndi.distance_transform_edt(m, return_indices=True)
    ids = idx[0] * w + idx[1]
    e = np.zeros((h, w), bool)
    e[:, :-1] |= ids[:, :-1] != ids[:, 1:]
    e[:-1, :] |= ids[:-1, :] != ids[1:, :]
    return ndi.distance_transform_edt(~e)
