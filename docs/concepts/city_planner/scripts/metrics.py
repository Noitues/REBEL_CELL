"""Rough layout metrics: distance of each district centroid from the old-city centroid."""
import importlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

OUT = os.path.join(os.path.dirname(__file__), '..')
res = {}
for key in 'abcde':
    mod = importlib.import_module('design_' + key)
    m = mod.build()
    cents = {}
    for k in ('centre', 'halcyon', 'solace', 'orbital', 'meridian', 'aurelian', 'tethys'):
        a = m.mnp(m.z[k]['mask'])
        ys, xs = np.nonzero(a)
        cents[k] = (float(xs.mean()), float(ys.mean()), int(a.sum()))
    c = cents['centre']
    d = {k: round(math.hypot(v[0] - c[0], v[1] - c[1]), 0) for k, v in cents.items() if k != 'centre'}
    vals = list(d.values())
    land = float(m.mnp(m.land).sum()) / 1e6
    res[key] = dict(dist=d, mean=round(sum(vals) / 6), spread=round(max(vals) / max(1.0, min(vals)), 2), land=round(land, 2),
                    area={k: v[2] for k, v in cents.items()})
    print(key, res[key]['mean'], res[key]['spread'], d)
json.dump(res, open(os.path.join(OUT, 'scripts', 'metrics.json'), 'w'), indent=1)
