

# ------------------------------------------------------------------ round 4: one continuous park (direction D, --park 1)
def _pc(night, celnight, day, celday):
    if DAYV:
        return celday if CEL else day
    return celnight if CEL else night


LAWN_A = _pc((0.022, 0.075, 0.028), (0.07, 0.22, 0.10), (0.07, 0.20, 0.06), (0.12, 0.38, 0.14))
LAWN_B = _pc((0.04, 0.115, 0.04), (0.10, 0.30, 0.12), (0.11, 0.28, 0.08), (0.17, 0.48, 0.17))
GRAVEL = _pc((0.09, 0.10, 0.08), (0.22, 0.25, 0.22), (0.50, 0.45, 0.36), (0.40, 0.37, 0.32))
LANE = _pc((0.03, 0.03, 0.04), (0.10, 0.09, 0.18), (0.09, 0.09, 0.10), (0.14, 0.14, 0.18))
CLEAR = _pc((0.10, 0.12, 0.11), (0.14, 0.22, 0.19), (0.46, 0.44, 0.38), (0.40, 0.40, 0.36))
WATERC = _pc((0.01, 0.05, 0.07), (0.06, 0.22, 0.30), (0.05, 0.20, 0.24), (0.20, 0.55, 0.60))
HX, HY = 4.5 * PITCH, -2.5 * PITCH
KITLOTS = {k for k, p in PLAN.items() if p["kind"] == "solace"}
FEATLOTS = {k for k, p in PLAN.items() if p["kind"] == "park" and hr(k[0], k[1], 5) < 0.2}
PONDLOTS = {k for k, p in PLAN.items() if p["kind"] == "park" and k not in FEATLOTS and hr(k[0], k[1], 9) < 0.2 and inside_blob(p["x"], p["y"], 20.0)}
FLATLOTS = KITLOTS | FEATLOTS | PONDLOTS


def _roll(x, y):
    return 0.8 * (1.1 + 0.9 * math.sin(x * 0.038 + 1.3) * math.cos(y * 0.031 + 0.4) + 0.7 * math.sin((x * 0.6 + y) * 0.062 + 0.5) + 0.35 * math.sin(x * 0.11) * math.sin(y * 0.09)) + 0.3


def _flat_mask(x, y):
    i, j = round(x / PITCH), round(y / PITCH)
    d = 1e9
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if (i + di, j + dj) in FLATLOTS:
                d = min(d, max(abs(x - (i + di) * PITCH), abs(y - (j + dj) * PITCH)))
    d = min(d, math.hypot(x, y) - 38.0, math.hypot(x - HX, y - HY) - 36.0)
    return smoothstep(10.0, 26.0, d)


def GZ(x, y):
    """Ground height of the lawn: rolling in the open, flat under buildings and clearings, tapering to the street level at the edge."""
    r = math.hypot(x, y)
    th = math.atan2(y, x)
    edge = smoothstep(Rb(th), Rb(th) - 24.0, r)
    return 0.24 + _roll(x, y) * _flat_mask(x, y) * edge


def _lawn_col(x, y):
    t = 0.5 + 0.5 * math.sin(x * 0.051 + math.sin(y * 0.043) * 2.2) * math.sin(y * 0.037 + 0.8 + math.sin(x * 0.029) * 1.7)
    t = max(0.0, min(1.0, t))
    return tuple(LAWN_A[k] + (LAWN_B[k] - LAWN_A[k]) * t for k in range(3))


def _chaikin(pts, it=2, q=0.2):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
            out.append((a[0] + (b[0] - a[0]) * (1 - q), a[1] + (b[1] - a[1]) * (1 - q)))
        out.append(pts[-1])
        pts = out
    return pts


def _resample(pts, step=3.0):
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        if L_ < 1e-6:
            continue
        t = step - carry
        while t <= L_:
            out.append((a[0] + (b[0] - a[0]) * t / L_, a[1] + (b[1] - a[1]) * t / L_))
            t += step
        carry = L_ - (t - step)
    out.append(pts[-1])
    return out


def _wobble(pts, amp, wl, phase):
    out = []
    s_ = 0.0
    for i, p in enumerate(pts):
        if i > 0:
            s_ += math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        o = amp * math.sin(s_ / wl * 6.283 + phase)
        out.append((p[0] - ty / n * o, p[1] + tx / n * o))
    return out


def _ribbon(mbd, pts, w, zoff, col, prm):
    vs = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / n * w / 2, tx / n * w / 2
        z = GZ(p[0], p[1]) + zoff
        vs.append((mbd.v((p[0] - nx, p[1] - ny, z), col, prm), mbd.v((p[0] + nx, p[1] + ny, z), col, prm)))
    for (a0, a1), (b0, b1) in zip(vs, vs[1:]):
        mbd.f(a0, a1, b1, b0)


def _blob_poly(cx, cy, R, wob, ph, n=40, sx=1.0, sy=1.0, rot=0.0):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        r = R * (1 + wob * math.sin(3 * t + ph) + wob * 0.6 * math.sin(5 * t + ph * 1.7) + wob * 0.4 * math.sin(2 * t + ph * 0.6))
        x, y = r * math.cos(t) * sx, r * math.sin(t) * sy
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def _nodes_route(start, head, out_goal, rr):
    blocked = lambda x, y: 84 < x < 132 and -84 < y < -36
    nodes = [start]
    h = head
    for _ in range(26):
        x, y = nodes[-1]
        r = math.hypot(x, y) or 1.0
        ox, oy = (x / r, y / r) if out_goal else (-x / r, -y / r)
        cands = [(h, 0.55), ((-h[1], h[0]), 0.225), ((h[1], -h[0]), 0.225)]
        sc = []
        for d_, w_ in cands:
            nx, ny = x + d_[0] * PITCH, y + d_[1] * PITCH
            if blocked(nx, ny):
                sc.append(0.0)
                continue
            sc.append(w_ * (0.35 + max(0.0, d_[0] * ox + d_[1] * oy)) * (0.6 + rr.random()))
        if sum(sc) <= 0:
            break
        k = max(range(3), key=lambda i: sc[i])
        h = cands[k][0]
        nodes.append((x + h[0] * PITCH, y + h[1] * PITCH))
        rn = math.hypot(*nodes[-1])
        if out_goal and rn > Rb(math.atan2(nodes[-1][1], nodes[-1][0])) + 55:
            break
        if (not out_goal) and rn < 46:
            break
    return nodes


def _tree_ok(x, y, pathgrid, extra=0.0):
    if not inside_blob(x, y, 7.0):
        return False
    i, j = round(x / PITCH), round(y / PITCH)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if (i + di, j + dj) in FLATLOTS and max(abs(x - (i + di) * PITCH), abs(y - (j + dj) * PITCH)) < 11.0 + extra:
                return False
    if math.hypot(x, y) < 44.0 or math.hypot(x - HX, y - HY) < 42.0:
        return False
    gx, gy = int(x // 5), int(y // 5)
    for a in (gx - 1, gx, gx + 1):
        for b in (gy - 1, gy, gy + 1):
            for (px, py, pw) in pathgrid.get((a, b), ()):
                if (px - x) ** 2 + (py - y) ** 2 < (pw / 2 + 2.4) ** 2:
                    return False
    return True


def park_world():
    """One continuous park: rolling lawn, organic clearings, curving footpaths and service lanes, ponds, tree clumps, a tree line."""
    g = mb("ground", True)
    rr = random.Random(SEED + 400)
    # ---- the lawn: a polar mesh out to the organic boundary
    NR, NA = 48, 220
    rings = []
    cvert = g.v((0, 0, GZ(0, 0) + 0.04), _lawn_col(0, 0), (0.9, 0.0, 0, 1))
    for k in range(1, NR + 1):
        u = k / NR
        row = []
        for a_ in range(NA + 1):
            th = 2 * math.pi * (a_ % NA) / NA
            R_ = Rb(th) * u
            x, y = R_ * math.cos(th), R_ * math.sin(th)
            row.append(g.v((x, y, GZ(x, y) + 0.04), _lawn_col(x, y), (0.9, 0.0, 0, 1)))
        rings.append(row)
    for a_ in range(NA):
        g.f(cvert, rings[0][a_ + 1], rings[0][a_])
    for k in range(NR - 1):
        for a_ in range(NA):
            g.f(rings[k][a_], rings[k][a_ + 1], rings[k + 1][a_ + 1], rings[k + 1][a_])
    # ---- clearings round the helix and the hospital
    for (cx, cy, R, ph) in ((0.0, 0.0, 40.0, 0.4), (HX, HY, 38.0, 1.9)):
        poly = _blob_poly(cx, cy, R, 0.07, ph, 44)
        idx = [g.v((x, y, GZ(x, y) + 0.1), CLEAR, (0.55, 0.0, 0, 1)) for (x, y) in poly]
        c0 = g.v((cx, cy, GZ(cx, cy) + 0.1), CLEAR, (0.55, 0.0, 0, 1))
        for k in range(len(idx)):
            g.f(c0, idx[k], idx[(k + 1) % len(idx)])
    # lit loop paths in the clearings (wobbly rings)
    for (cx, cy, R, ph, col) in ((0.0, 0.0, 19.0, 0.4, PINKC), (0.0, 0.0, 27.5, 0.9, LIME), (0.0, 0.0, 35.0, 1.4, LIME), (HX, HY, 31.0, 1.9, LIME)):
        poly = _blob_poly(cx, cy, R, 0.045, ph, 64)
        _ribbon(mb("neon"), poly + [poly[0]], 0.42, 0.16, col, (0.8 if not CEL else 1, 0, 0, 1))
    # ---- footpaths and service lanes: curving routes along the old corridors, meandering, running out into the city streets
    routes = []
    n_out = 9
    for k in range(n_out):
        th0 = 2 * math.pi * k / n_out + (hr(k, 0, 51) - 0.5) * 0.5
        x0, y0 = 46 * math.cos(th0), 46 * math.sin(th0)
        a, b = round(x0 / PITCH - 0.5), round(y0 / PITCH - 0.5)
        start = ((a + 0.5) * PITCH, (b + 0.5) * PITCH)
        ox, oy = math.cos(th0), math.sin(th0)
        head = max(((1, 0), (0, 1), (-1, 0), (0, -1)), key=lambda d: d[0] * ox + d[1] * oy)
        routes.append((_nodes_route(start, head, True, random.Random(SEED + 500 + k)), "lane" if k in (1, 4, 7) else "foot"))
    routes.append((_nodes_route((132.0, -60.0), (1, 0), True, random.Random(SEED + 530)), "foot"))
    routes.append((_nodes_route((84.0, -60.0), (-1, 0), False, random.Random(SEED + 531)), "foot"))
    pathgrid = {}
    for ri, (nodes, kind) in enumerate(routes):
        if len(nodes) < 2:
            continue
        pts = _chaikin(nodes, 2, 0.2)
        pts = _resample(pts, 3.0)
        pts = _wobble(pts, 1.3 if kind == "foot" else 0.8, 46.0, ri * 1.7)
        w = 2.6 if kind == "foot" else 5.0
        _ribbon(g, pts, w, 0.12, GRAVEL if kind == "foot" else LANE, (0.8, 1.0 if kind == "lane" else 0.0, 0, 1))
        if kind == "foot":
            _ribbon(mb("neon"), pts, 0.2, 0.2, LIME, (0.55 if not CEL else 1, 0, 0, 1))
        else:
            for sgn in (-1, 1):
                off = []
                for i, p in enumerate(pts):
                    a_ = pts[max(0, i - 1)]
                    b_ = pts[min(len(pts) - 1, i + 1)]
                    tx, ty = b_[0] - a_[0], b_[1] - a_[1]
                    n_ = math.hypot(tx, ty) or 1.0
                    off.append((p[0] - ty / n_ * sgn * 2.2, p[1] + tx / n_ * sgn * 2.2))
                for q in range(0, len(off) - 3, 4):
                    _ribbon(mb("neon"), off[q:q + 3], 0.16, 0.2, LIME if sgn > 0 else (0.9, 0.7, 0.3), (0.7 if not CEL else 1, 0, 0, 1))
        for p in pts:
            pathgrid.setdefault((int(p[0] // 5), int(p[1] // 5)), []).append((p[0], p[1], w))
    # ---- ponds
    wm = mb("water")
    ponds = []
    for (i, j) in sorted(PONDLOTS):
        cx, cy = i * PITCH + (hr(i, j, 10) - 0.5) * 6, j * PITCH + (hr(i, j, 11) - 0.5) * 6
        poly = _blob_poly(cx, cy, 6.5 + 3.0 * hr(i, j, 12), 0.12, hr(i, j, 13) * 6, 28, 1.0, 0.65 + 0.3 * hr(i, j, 14), hr(i, j, 15) * 3.14)
        idx = [wm.v((x, y, GZ(x, y) + 0.1), WATERC, (0.1, 0, 0, 1)) for (x, y) in poly]
        c0 = wm.v((cx, cy, GZ(cx, cy) + 0.1), WATERC, (0.1, 0, 0, 1))
        for k in range(len(idx)):
            wm.f(c0, idx[k], idx[(k + 1) % len(idx)])
        ponds.append((cx, cy))
    # ---- tree clumps
    nt = 0
    for c in range(240):
        a = rr.random() * 6.283
        r = math.sqrt(rr.random()) * 205.0
        cx, cy = r * math.cos(a), r * math.sin(a)
        if not inside_blob(cx, cy, 10.0):
            continue
        n = 4 + int(rr.random() * 8)
        rad = 4.0 + 6.0 * rr.random()
        for k in range(n):
            ang = rr.random() * 6.283
            d = abs(rr.gauss(0, rad * 0.55))
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            if not _tree_ok(x, y, pathgrid):
                continue
            if any((x - px) ** 2 + (y - py) ** 2 < 100 for (px, py) in ponds):
                continue
            glow = (D and BUNDLE.get((round(x / PITCH), round(y / PITCH))) == "A" and rr.random() < 0.12)
            tree(x, y, rr, h=5.5 + 5.0 * rr.random(), z=GZ(x, y), glow=glow)
            nt += 1
    # ---- the tree line along the organic boundary (gaps where a path runs out)
    ntl = int(2 * math.pi * 205 / 4.5)
    for k in range(ntl):
        th = 2 * math.pi * k / ntl + rr.random() * 0.02
        for row in (0, 1):
            r = Rb(th) - 3.0 - row * 4.5 + (rr.random() - 0.5) * 3.0
            x, y = r * math.cos(th), r * math.sin(th)
            gx, gy = int(x // 5), int(y // 5)
            near = any((px - x) ** 2 + (py - y) ** 2 < (pw / 2 + 2.8) ** 2 for a in (gx - 1, gx, gx + 1) for b in (gy - 1, gy, gy + 1) for (px, py, pw) in pathgrid.get((a, b), ()))
            if near:
                continue
            tree(x, y, rr, h=7.0 + 5.0 * rr.random(), z=GZ(x, y))
            nt += 1
    print("PARK trees", nt, "ponds", len(ponds), "routes", [len(r[0]) for r in routes], flush=True)
    # ---- the plinth drum at the helix (as the plaza, minus the geometric rings)
    cyl(mb("plain"), 0, 0, 0.3, 2.5, 12.0, sd(32), (0.38, 0.44, 0.42) if not CEL else (0.7, 0.78, 0.74), (0, 0, 0, 0.2))
    torus(mb("neon"), 0, 0, 2.55, 12.05, 0.28, sd(40), 5, LIME, (1.3 if not CEL else 1, 0, 0, 1))
