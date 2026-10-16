"""City-all-corps round 3: the pure rules shared by zoning.py (CPython) and the Blender build (no bpy, no numpy).

  ab(x, y) / from_ab(a, b)   lots <-> the screen-aligned plane (a right, b away from the map camera; the coast at +b)
  urban_u(a, b)              the organic urban-core factor (city_preset.URBAN, rule H3): 1 in the core, 0 in the sprawl
  district_weights(a, b, hq_ab, u)  the influence weights per corp + the sprawl weight (rule H2)
  draw_district(key, w)      the seeded draw of a building's district from those weights (per building key)
  in_footprint(corp, dx, dy) a world-BU offset from an HQ lot inside that corp's landmark footprint (+ margin)
All randomness is a pure function of a seed and a content id (city_preset.SEEDS / INFLUENCE / URBAN), never of order.
"""
import math
import random

import city_preset as CP

R2 = math.sqrt(2.0)
CX, CY = 6.0, 6.0


A2_MODE = CP.LAYOUT_MODE == "a2"


def ab(x, y):
    """lots -> the screen-aligned plane (a right, b away from the camera). Legacy: the diamond map rotated 45 degrees; A2:
    a = east, b = north in lots (the plan's X, Y over 100 m)."""
    dx, dy = x - CX, y - CY
    if A2_MODE:
        return dx, -dy
    return (dx - dy) / R2, -(dx + dy) / R2


def from_ab(a, b):
    if A2_MODE:
        return CX + a, CY - b
    return CX + (a - b) / R2, CY + (-a - b) / R2


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def _hash01(*ints):
    """A fixed integer hash -> [0, 1) (no Python hash(): it is salted per process for strings)."""
    h = 1469598103934665603
    for v in ints:
        h ^= (int(v) & 0xFFFFFFFFFFFFFFFF)
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        h ^= h >> 29
    return (h % 1000003) / 1000003.0


def value_noise(x, y, cell, seed):
    """2D value noise in [0, 1): smooth interpolation of hashed lattice values (cell in lots)."""
    gx, gy = x / cell, y / cell
    i, j = math.floor(gx), math.floor(gy)
    fx, fy = gx - i, gy - j
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    v00, v10 = _hash01(seed, i, j), _hash01(seed, i + 1, j)
    v01, v11 = _hash01(seed, i, j + 1), _hash01(seed, i + 1, j + 1)
    return (v00 * (1 - sx) + v10 * sx) * (1 - sy) + (v01 * (1 - sx) + v11 * sx) * sy


_U = CP.URBAN
_rh = random.Random(_U["seed"])
_HARM = [(k, _rh.uniform(0.0, 2 * math.pi), _rh.uniform(0.5, 1.0) / k ** 0.8) for k in range(2, _U["kmax"] + 1)]
_HSUM = sum(c for _, _, c in _HARM)
B_COAST_K = 0.72          # the core is squashed toward the coast (+b): the waterfront stays city, the sea bounds it


def urban_edge(theta):
    return _U["r0"] * (1.0 + _U["amp"] * sum(c * math.sin(k * theta + ph) for k, ph, c in _HARM) / _HSUM)


_FLD = {}


def a2_fields():
    """the A2 raster fields (zoning_a2.py): u (urban factor), dist (district id per cell), cls (cell class)."""
    if not _FLD:
        import numpy as _np
        z = _np.load(CP.A2_FIELDS)
        _FLD.update(u=z["u"].astype(float), dist=z["dist"], cls=z["cls"], i0=int(z["i0"]), j0=int(z["j0"]), n=int(z["n"]),
                    names=[str(v) for v in z["names"]])
        if "H" in z.files:
            _FLD.update(H=z["H"].astype(float), slope=z["slope"].astype(float), outer=z["outer"].astype(float), dwat=z["dwat"].astype(float), hi0=int(z["hi0"]), hj0=int(z["hj0"]), hn=int(z["hn"]))
    return _FLD


def a2_cell(a, b):
    """-> (row, col) of the raster cell holding the screen-plane point (a, b), or None outside the grid."""
    F = a2_fields()
    i, j = int(math.floor(a + CX)) - F["i0"], int(math.floor(CY - b)) - F["j0"]
    if 0 <= i < F["n"] and 0 <= j < F["n"]:
        return j, i
    return None


def a2_district(a, b):
    """the corp whose polygon holds the point ('' none; 'rebel_cell' for the Old City)."""
    c = a2_cell(a, b)
    if c is None:
        return ""
    k = int(a2_fields()["dist"][c])
    return a2_fields()["names"][k] if k > 0 else ""


def urban_u(a, b):
    if A2_MODE:
        F = a2_fields()
        fx, fy = a + CX - F["i0"] - 0.5, CY - b - F["j0"] - 0.5
        i0, j0 = int(math.floor(fx)), int(math.floor(fy))
        n = F["n"]
        if i0 < 0 or j0 < 0 or i0 >= n - 1 or j0 >= n - 1:
            return 0.0
        tx, ty = fx - i0, fy - j0
        u = F["u"]
        return float((u[j0, i0] * (1 - tx) + u[j0, i0 + 1] * tx) * (1 - ty) + (u[j0 + 1, i0] * (1 - tx) + u[j0 + 1, i0 + 1] * tx) * ty)
    bb = b * B_COAST_K if b > 0 else b
    p = _U["p"]
    r = (abs(a) ** p + abs(bb) ** p) ** (1.0 / p)
    th = math.atan2(bb, a)
    edge = urban_edge(th) + _U["amp_n"] * (2.0 * value_noise(a, b, _U["cell"], _U["seed"]) - 1.0)
    # AD r3 review: a fine ragged term (block scale) so the boundary never follows the map's diamond outline
    edge += _U.get("amp_f", 0.0) * (2.0 * value_noise(a, b, _U.get("cell_f", 4.0), _U["seed"] + 1) - 1.0)
    return smoothstep(-0.5, 0.5, (edge - r) / _U["fade"])


_I = CP.INFLUENCE


def district_weights(a, b, hq_ab, u):
    """hq_ab: {corp: (a, b)} -> ({corp: weight}, sprawl weight). Corp weights are scaled by the urban factor u."""
    lam = _I["lam"]
    w = {}
    for k in sorted(hq_ab):
        d = math.hypot(a - hq_ab[k][0], b - hq_ab[k][1])
        w[k] = math.exp(-d / (lam * _I["lam_k"].get(k, 1.0))) * u
    if A2_MODE:                                   # A2: a corp's own polygon holds its colour (the districts are the plan's shapes)
        own = a2_district(a, b)
        if own in w:
            w[own] *= _I.get("own_k", 8.0)
    return w, math.exp(-_I["d0"] / lam)


def draw_district(key, w, w0, salt=0):
    """Seeded per building key: the district drawn from the weights ('' = the sprawl). Order: sorted corp ids."""
    tot = sum(w.values()) + w0
    x = random.Random(_I["seed"] * 1000003 + int(key) * 7 + salt).random() * tot
    for k in sorted(w):
        if x < w[k]:
            return k
        x -= w[k]
    return ""


def glow_mix(w, w0):
    """the district glow colour at a point: the hue mix by weight (sprawl / REBEL_CELL: the sprawl glow)."""
    w0 = w0 * 0.5                 # the sprawl counts half in the glow colour (the district hues stay readable in the fog)
    tot = sum(w.values()) + w0
    c = [0.0, 0.0, 0.0]
    for k in sorted(w):
        col = palette(k)["sec" if k == "aurelian" else "hue"]
        for i in range(3):
            c[i] += col[i] * w[k] / tot
    sp = CP.DISTRICTS[""]["hue"]
    for i in range(3):
        c[i] += sp[i] * w0 / tot
    return tuple(c)


def catmull_rom(pts, step, closed=False, alpha=0.5):
    """centripetal Catmull-Rom through pts [(x, y), ...] sampled about every `step` units; open curves pass through the
    first and last points (end tangents from mirrored phantoms), closed curves loop. -> [(x, y), ...]"""
    P = [tuple(map(float, p)) for p in pts]
    if closed:
        ext = [P[-1]] + P + [P[0], P[1]]
    else:
        ext = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1])] + P + [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1])]
    out = []
    nseg = len(P) if closed else len(P) - 1
    for i in range(nseg):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]

        def tj(ti, a, b):
            return ti + max(1e-6, math.hypot(b[0] - a[0], b[1] - a[1])) ** alpha
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for k in range(n):
            t = t1 + (t2 - t1) * k / n

            def L(a, b, ta, tb):
                w = (t - ta) / (tb - ta)
                return (a[0] + (b[0] - a[0]) * w, a[1] + (b[1] - a[1]) * w)
            A1, A2, A3 = L(p0, p1, t0, t1), L(p1, p2, t1, t2), L(p2, p3, t2, t3)
            B1, B2 = L(A1, A2, t0, t2), L(A2, A3, t1, t3)
            out.append(L(B1, B2, t1, t2))
    if not closed:
        out.append(P[-1])
    return out


def rounded_rect(cx, cy, hx, hy, r, step):
    """a closed rounded rectangle (centre, half sizes, corner radius) sampled about every `step`, counter-clockwise."""
    out = []
    corners = [(cx + hx - r, cy + hy - r, 0.0), (cx - hx + r, cy + hy - r, 90.0), (cx - hx + r, cy - hy + r, 180.0), (cx + hx - r, cy - hy + r, 270.0)]
    for (ox, oy, a0) in corners:
        n = max(3, int(r * math.pi / 2 / step))
        for k in range(n + 1):
            t = math.radians(a0 + 90.0 * k / n)
            out.append((ox + r * math.cos(t), oy + r * math.sin(t)))
        # the straight to the next corner is implied (the next corner's first point)
    res = []
    for i in range(len(out)):
        a, b = out[i], out[(i + 1) % len(out)]
        res.append(a)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m = int(L / step)
        for k in range(1, m):
            res.append((a[0] + (b[0] - a[0]) * k / m, a[1] + (b[1] - a[1]) * k / m))
    return res


def pick(table, x):
    """table: [(weight, value), ...]; x in [0, 1) -> the value (cumulative, table order)."""
    tot = sum(w for w, _ in table)
    x *= tot
    for w, v in table:
        if x < w:
            return v
        x -= w
    return table[-1][1]


def palette(k):
    """the colour set a district wears in this key art (REBEL_CELL wears the sprawl's: note 8)."""
    if k == "rebel_cell":
        return CP.DISTRICTS[CP.REBEL_KEYART_PALETTE]
    return CP.DISTRICTS[k]


def in_footprint(corp, dx, dy, margin=0.0):
    """dx, dy: world BU from the HQ lot centre (x east, y north)."""
    fp = CP.LANDMARK_FP.get(corp)
    if not fp:
        return False
    if fp[0] == "sq":
        return max(abs(dx), abs(dy)) < fp[1] + margin
    if fp[0] == "ell":
        return (dx / (fp[1] + margin)) ** 2 + (dy / (fp[2] + margin)) ** 2 < 1.0
    return math.hypot(dx, dy) < fp[1] + margin


# ------------------------------------------------------------------ round 3c: road geometry (lots), ramps, interchanges
class LotPath:
    """a polyline in lots with arc length; at(s) -> (point, unit tangent); nearest(p) -> (s, distance)."""

    def __init__(self, pts, closed=False):
        P = [tuple(map(float, p)) for p in pts]
        if closed and P[0] != P[-1]:
            P = P + [P[0]]
        self.P, self.closed = P, closed
        self.S = [0.0]
        for i in range(1, len(P)):
            self.S.append(self.S[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
        self.L = self.S[-1]

    def at(self, s):
        s = (s % self.L) if self.closed else min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.S) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.S[m] <= s:
                lo = m
            else:
                hi = m
        a, b = self.P[lo], self.P[hi]
        seg = max(1e-9, self.S[hi] - self.S[lo])
        t = (s - self.S[lo]) / seg
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / seg, (b[1] - a[1]) / seg)

    def nearest(self, p):
        best = (1e18, 0.0)
        for i in range(len(self.P) - 1):
            a, b = self.P[i], self.P[i + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l2 = dx * dx + dy * dy
            t = 0.0 if l2 < 1e-12 else min(1.0, max(0.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
            d = math.hypot(p[0] - a[0] - dx * t, p[1] - a[1] - dy * t)
            if d < best[0]:
                best = (d, self.S[i] + math.sqrt(l2) * t)
        return best[1], best[0]


def intersections(A, B):
    """crossings of two LotPaths -> [(sA, sB, (x, y))] sorted by sA."""
    out = []
    for i in range(len(A.P) - 1):
        p, r = A.P[i], (A.P[i + 1][0] - A.P[i][0], A.P[i + 1][1] - A.P[i][1])
        for j in range(len(B.P) - 1):
            q, sv = B.P[j], (B.P[j + 1][0] - B.P[j][0], B.P[j + 1][1] - B.P[j][1])
            den = r[0] * sv[1] - r[1] * sv[0]
            if abs(den) < 1e-12:
                continue
            t = ((q[0] - p[0]) * sv[1] - (q[1] - p[1]) * sv[0]) / den
            u = ((q[0] - p[0]) * r[1] - (q[1] - p[1]) * r[0]) / den
            if 0.0 <= t < 1.0 and 0.0 <= u < 1.0:
                sa = A.S[i] + t * math.hypot(*r)
                sb = B.S[j] + u * math.hypot(*sv)
                if not out or abs(sa - out[-1][0]) > 3.0:
                    out.append((sa, sb, (p[0] + r[0] * t, p[1] + r[1] * t)))
    return out


def hermite(p0, t0, p1, t1, step, k=1.0):
    """cubic Hermite from p0 (unit tangent t0) to p1 (unit tangent t1), tangent length = chord x k -> points every ~step."""
    ch = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    m0 = (t0[0] * ch * k, t0[1] * ch * k)
    m1 = (t1[0] * ch * k, t1[1] * ch * k)
    n = max(4, int(ch * 1.3 / step))
    out = []
    for i in range(n + 1):
        t = i / n
        h00, h10, h01, h11 = 2 * t ** 3 - 3 * t * t + 1, t ** 3 - 2 * t * t + t, -2 * t ** 3 + 3 * t * t, t ** 3 - t * t
        out.append((h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0], h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1]))
    return out


def slip(A, sa, da, B, sb, db, step):
    """a slip ramp: leaves road A at arc sa heading da (+1 / -1 along it), joins road B at sb heading db."""
    pa, ta = A.at(sa)
    pb, tb = B.at(sb)
    return hermite(pa, (ta[0] * da, ta[1] * da), pb, (tb[0] * db, tb[1] * db), step, 1.1)


def cloverleaf(A, sa_x, B, sb_x, d, step):
    """the four 270-degree loop ramps of a cloverleaf where A (at sa_x) and B (at sb_x) cross; d = tangent distance (lots).
    -> [(pts, dict(a=(road end sA), b=...))]; each loop leaves one road past the crossing and joins the other heading back."""
    X, ta = A.at(sa_x)
    _, tb = B.at(sb_x)
    out = []
    for qa in (1, -1):
        for qb in (1, -1):
            ua, ub = (ta[0] * qa, ta[1] * qa), (tb[0] * qb, tb[1] * qb)
            c = max(-1.0, min(1.0, ua[0] * ub[0] + ua[1] * ub[1]))
            phi = math.acos(c)
            if phi < math.radians(35) or phi > math.radians(105):
                continue
            r = d * math.tan(phi / 2.0)
            ex, ey = ua[0] + ub[0], ua[1] + ub[1]
            el = math.hypot(ex, ey)
            ex, ey = ex / el, ey / el
            cc = (X[0] + ex * r / math.sin(phi / 2.0), X[1] + ey * r / math.sin(phi / 2.0))
            t1 = (X[0] + ua[0] * d, X[1] + ua[1] * d)
            t2 = (X[0] + ub[0] * d, X[1] + ub[1] * d)
            a1 = math.atan2(t1[1] - cc[1], t1[0] - cc[0])
            a2 = math.atan2(t2[1] - cc[1], t2[0] - cc[0])
            best = None
            for sgn in (1, -1):
                da = (a2 - a1) * sgn
                while da <= 0:
                    da += 2 * math.pi
                am = a1 + sgn * da / 2.0
                mid = (cc[0] + r * math.cos(am), cc[1] + r * math.sin(am))
                dm = math.hypot(mid[0] - X[0], mid[1] - X[1])
                if best is None or dm > best[0]:
                    best = (dm, sgn, da)
            _, sgn, da = best
            n = max(8, int(r * da / step))
            arc = [(cc[0] + r * math.cos(a1 + sgn * da * k / n), cc[1] + r * math.sin(a1 + sgn * da * k / n)) for k in range(n + 1)]
            lead = 3.5
            pre = (X[0] + ua[0] * (d - lead), X[1] + ua[1] * (d - lead))
            post = (X[0] + ub[0] * (d - lead), X[1] + ub[1] * (d - lead))
            pts = catmull_rom([pre] + arc[::2] + [arc[-1], post], step)
            out.append((pts, dict(a_s=sa_x + qa * (d - lead), b_s=sb_x + qb * (d - lead))))
    return out


def ring_profile(urban_r, rmax, margin, dil_deg, sig1_deg, sig2_deg, n=180):
    """radii (n samples round the circle) of the perimeter ring: the urban edge dilated, smoothed, pushed out by margin, held
    inside rmax(theta); two Gaussian passes (circular)."""
    raw = [urban_r(2 * math.pi * k / n) for k in range(n)]
    w = int(round(dil_deg / (360.0 / n)))
    dil = [max(raw[(k + j) % n] for j in range(-w, w + 1)) for k in range(n)]

    def gs(v, sg):
        h = max(1, int(round(sg / (360.0 / n))))
        wts = [math.exp(-0.5 * (j / h) ** 2) for j in range(-3 * h, 3 * h + 1)]
        tw = sum(wts)
        return [sum(wts[j + 3 * h] * v[(k + j) % n] for j in range(-3 * h, 3 * h + 1)) / tw for k in range(n)]
    r1 = gs(dil, sig1_deg)
    r1 = [min(r1[k] + margin, rmax(2 * math.pi * k / n)) for k in range(n)]
    r2 = gs(r1, sig2_deg)
    return [min(r2[k], rmax(2 * math.pi * k / n)) for k in range(n)]
