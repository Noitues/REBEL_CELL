"""dot_audit (O-30 fix 3): pixel check for runs of evenly spaced dots, i.e. anything that reads as a dotted line at 1:1,
whatever draw call made it (the call-count audit in f1_render.DASH_LOG / DOT_LOG misses beads drawn as single circles).

audit(img) -> dict(runs=[...], n_runs=int)
  1. small spots: |DoG| of luma (sigma 1.0 - 3.0) over SPOT_T, split by sign (bright spots / dark spots), connected components
     with area SPOT_AREA, bbox <= SPOT_BOX px, aspect <= SPOT_ASPECT, fill >= SPOT_FILL
  2. halftone / Ben-Day fields are dropped: a spot with FIELD_N or more spots within FIELD_K x its nearest-neighbour distance is part of a 2-D field
  3. runs: each spot links to its nearest neighbours within GAP px; chains of degree <= 2 are traced; a run is RUN_MIN or more spots
     with spacing CV <= SPACING_CV, area CV <= AREA_CV, colour spread <= COL_D and every turn <= TURN_DEG
python dot_audit.py <png> [...]   prints the runs per file"""
import sys, math, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SPOT_T = 14.0
SPOT_AREA = (3, 70)
SPOT_BOX = 11
SPOT_ASPECT = 1.8
SPOT_FILL = 0.45
FIELD_R = 14.0       # rule A: FIELD_N_A or more spots within FIELD_R px
FIELD_N_A = 4
FIELD_K = 1.5        # rule B: FIELD_N or more spots within FIELD_K x the nearest-neighbour distance (the edge row of a field)
FIELD_N = 3
GAP = (3.5, 16.0)
RUN_MIN = 5
SPACING_CV = 0.18
AREA_CV = 0.40
COL_D = 45.0
TURN_DEG = 30.0


def spots(a):
    l = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    dog = ndi.gaussian_filter(l, 1.0) - ndi.gaussian_filter(l, 3.0)
    out = []
    for sign in (1, -1):
        m = (dog * sign) > SPOT_T
        lab, n = ndi.label(m)
        if n == 0:
            continue
        objs = ndi.find_objects(lab)
        areas = ndi.sum(m, lab, range(1, n + 1))
        for i, sl in enumerate(objs):
            ar = areas[i]
            if not (SPOT_AREA[0] <= ar <= SPOT_AREA[1]):
                continue
            h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if max(h, w) > SPOT_BOX or max(h, w) / max(1, min(h, w)) > SPOT_ASPECT or ar / float(h * w) < SPOT_FILL:
                continue
            sub = lab[sl] == i + 1
            ys, xs = np.nonzero(sub)
            cy, cx = ys.mean() + sl[0].start, xs.mean() + sl[1].start
            col = a[sl][sub].mean(0)
            out.append(dict(x=float(cx), y=float(cy), area=float(ar), col=col, sign=sign))
    return out


def runs_of(sp):
    if len(sp) < RUN_MIN:
        return []
    P = np.array([[s['x'], s['y']] for s in sp])
    # grid neighbour search
    cell = GAP[1]
    grid = {}
    for i, (x, y) in enumerate(P):
        grid.setdefault((int(x // cell), int(y // cell)), []).append(i)

    def near(i, r):
        x, y = P[i]
        gx, gy = int(x // cell), int(y // cell)
        res = []
        k = int(math.ceil(r / cell))
        for dx in range(-k, k + 1):
            for dy in range(-k, k + 1):
                for j in grid.get((gx + dx, gy + dy), ()):
                    if j != i:
                        d = math.hypot(P[j][0] - x, P[j][1] - y)
                        if d <= r:
                            res.append((d, j))
        return sorted(res)
    def field(i):
        """part of a 2-D field: FIELD_N or more spots within FIELD_K x its nearest-neighbour distance (a line spot has 2: before and after;
        a spot on the edge row of a halftone field has its row neighbours plus the row behind)"""
        nb = near(i, FIELD_R)
        if not nb:
            return False
        if len(nb) >= FIELD_N_A:
            return True
        r = nb[0][0] * FIELD_K
        return sum(1 for d, j in nb if d <= r) >= FIELD_N
    keep = [not field(i) for i in range(len(sp))]
    adj = {i: [] for i in range(len(sp)) if keep[i]}
    for i in adj:
        cand = [(d, j) for d, j in near(i, GAP[1]) if d >= GAP[0] and keep[j] and sp[j]['sign'] == sp[i]['sign']]
        adj[i] = [j for d, j in cand[:2]]
    # mutual links only
    links = {i: [j for j in adj[i] if i in adj.get(j, [])] for i in adj}
    seen = set()
    out = []
    for i in links:
        if i in seen or len(links[i]) == 2:
            continue
        # start at an end (degree 0/1)
        path = [i]
        seen.add(i)
        cur, prev = i, None
        while True:
            nx = [j for j in links[cur] if j != prev and j not in seen]
            if not nx:
                break
            prev, cur = cur, nx[0]
            path.append(cur)
            seen.add(cur)
        if len(path) >= RUN_MIN:
            out.extend(_split_ok(path, P, sp))
    return out


def _split_ok(path, P, sp):
    """test the whole chain; report it as one run if it is evenly spaced, same size, same colour and smooth"""
    pts = P[path]
    d = np.hypot(*(pts[1:] - pts[:-1]).T)
    ar = np.array([sp[i]['area'] for i in path])
    cols = np.array([sp[i]['col'] for i in path])
    turns = []
    for k in range(1, len(pts) - 1):
        v1, v2 = pts[k] - pts[k - 1], pts[k + 1] - pts[k]
        c = np.dot(v1, v2) / max(1e-6, np.linalg.norm(v1) * np.linalg.norm(v2))
        turns.append(math.degrees(math.acos(max(-1, min(1, c)))))
    ok = (d.std() / d.mean() <= SPACING_CV and ar.std() / ar.mean() <= AREA_CV and
          np.abs(cols - cols.mean(0)).max() <= COL_D and (max(turns) if turns else 0) <= TURN_DEG)
    if not ok:
        return []
    return [dict(n=len(path), spacing=round(float(d.mean()), 2), spacing_cv=round(float(d.std() / d.mean()), 3),
                 area=round(float(ar.mean()), 1), colour=[int(c) for c in cols.mean(0)],
                 bbox=[int(pts[:, 0].min()), int(pts[:, 1].min()), int(pts[:, 0].max()), int(pts[:, 1].max())],
                 pts=[[round(float(x), 1), round(float(y), 1)] for x, y in pts])]


def audit(img):
    a = np.asarray(img.convert('RGB'), np.float32)
    sp = spots(a)
    r = runs_of(sp)
    return dict(n_spots=len(sp), n_runs=len(r), runs=r)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        res = audit(Image.open(p))
        print(p, 'spots', res['n_spots'], 'runs', res['n_runs'])
        for r in res['runs']:
            print('   n=%d spacing %.1f cv %.3f area %.1f col %s bbox %s' % (r['n'], r['spacing'], r['spacing_cv'], r['area'], r['colour'], r['bbox']))
