"""hq_tethys: small geometry helpers that write into the city_all_corps face accumulators (Acc.face). No bpy import:
everything here is plain maths, so the modules that use it run inside any Blender build that provides an Acc.

Acc.face(pts, col, uv=None, wc=(0,0,0), wl=0.0, wm=3, bid=0.0, wet=0)   (city_build.Acc)
"""
import math


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def unit2(x, y):
    L = math.hypot(x, y) or 1.0
    return x / L, y / L


def obox(acc, cx, cy, z0, l, w, h, yaw, col, roll=0.0, pitch=0.0, wet=0, top=True, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0):
    """An oriented box: centre (cx, cy), base z0, length l along yaw (rad), width w, height h; roll about its long axis
    and pitch about its cross axis (rad), both about the box centre (a flipped or tilted car, a fallen post)."""
    cu, su = math.cos(yaw), math.sin(yaw)
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    zc = z0 + h / 2
    P = []
    for (a, b, c) in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
        x, y, z = a * l / 2, b * w / 2, c * h / 2
        y, z = y * cr - z * sr, y * sr + z * cr          # roll (about the long axis x)
        x, z = x * cp - z * sp, x * sp + z * cp          # pitch (about the cross axis y)
        P.append((cx + x * cu - y * su, cy + x * su + y * cu, zc + z))
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    if top:
        faces.append((4, 5, 6, 7))
    for f in faces:
        acc.face([P[i] for i in f], col, None, wc, wl, wm, bid, wet)
    return P


def seg_box(acc, p0, p1, w, z0, z1, col, wet=0, top=True):
    """A box along the horizontal segment p0 -> p1 (xy), width w, from z0 to z1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return
    obox(acc, (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z0, L, w, z1 - z0, math.atan2(dy, dx), col, wet=wet, top=top)


def tube(acc, p0, p1, r, n, col, wet=0, caps=False):
    """A round tube between two 3D points (n sides)."""
    ax = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    L = math.sqrt(sum(c * c for c in ax))
    if L < 1e-6:
        return
    d = tuple(c / L for c in ax)
    up = (0.0, 0.0, 1.0) if abs(d[2]) < 0.95 else (1.0, 0.0, 0.0)
    s = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0])
    sl = math.sqrt(sum(c * c for c in s))
    s = tuple(c / sl for c in s)
    t = (d[1] * s[2] - d[2] * s[1], d[2] * s[0] - d[0] * s[2], d[0] * s[1] - d[1] * s[0])
    ring = []
    for k in range(n):
        a = 2 * math.pi * k / n
        ring.append(tuple(s[i] * math.cos(a) * r + t[i] * math.sin(a) * r for i in range(3)))
    for k in range(n):
        j = (k + 1) % n
        acc.face([v_add(p0, ring[k]), v_add(p0, ring[j]), v_add(p1, ring[j]), v_add(p1, ring[k])], col, None, wet=wet)
    if caps:
        acc.face([v_add(p0, ring[k]) for k in range(n)], col, None, wet=wet)
        acc.face([v_add(p1, ring[k]) for k in range(n)], col, None, wet=wet)


def frustum(acc, cx, cy, z0, z1, r0, r1, n, col, wet=0, top=False, bottom=False, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0):
    """A round frustum (r0 at z0, r1 at z1); UV = metres along the rim, height (the window shader's frame)."""
    u = 0.0
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        p = [(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), z0), (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1), z0),
             (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z1), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z1)]
        L = 2 * math.pi * max(r0, r1) / n
        acc.face(p, col, [(u, 0.0), (u + L, 0.0), (u + L, z1 - z0), (u, z1 - z0)], wc, wl, wm, bid, wet)
        u += L
    if top:
        acc.face([(cx + r1 * math.cos(2 * math.pi * k / n), cy + r1 * math.sin(2 * math.pi * k / n), z1) for k in range(n)],
                 col, None, wet=wet)
    if bottom:
        acc.face([(cx + r0 * math.cos(2 * math.pi * k / n), cy + r0 * math.sin(2 * math.pi * k / n), z0) for k in range(n)],
                 col, None, wet=wet)


def loft(acc, P, N, prof, col_of_edge, wet_of_edge=None, s_of=None):
    """Sweep the open profile prof [(off, z), ...] (off along the per-point normal N, BU) along the polyline P [(x, y)].
    col_of_edge(k) gives the colour of profile edge k; UV = arc length, z."""
    s = s_of or [0.0]
    if s_of is None:
        for i in range(1, len(P)):
            s.append(s[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
    for k in range(len(prof) - 1):
        (o0, z0), (o1, z1) = prof[k], prof[k + 1]
        col = col_of_edge(k)
        wet = wet_of_edge(k) if wet_of_edge else 0
        for i in range(len(P) - 1):
            a0 = (P[i][0] + N[i][0] * o0, P[i][1] + N[i][1] * o0, z0)
            a1 = (P[i + 1][0] + N[i + 1][0] * o0, P[i + 1][1] + N[i + 1][1] * o0, z0)
            b1 = (P[i + 1][0] + N[i + 1][0] * o1, P[i + 1][1] + N[i + 1][1] * o1, z1)
            b0 = (P[i][0] + N[i][0] * o1, P[i][1] + N[i][1] * o1, z1)
            acc.face([a0, a1, b1, b0], col, [(s[i], z0), (s[i + 1], z0), (s[i + 1], z1), (s[i], z1)], wet=wet)


def cap(acc, p, n, prof, col, wet=0):
    """Close a loft end: the profile polygon at point p (normal n)."""
    acc.face([(p[0] + n[0] * o, p[1] + n[1] * o, z) for (o, z) in prof], col, None, wet=wet)


def slab(acc, p, t, n, poly, w, col, wet=0):
    """Extrude a cross-section polygon poly [(off, z)] (off along n) by w along t, centred on p (a fin, a pier)."""
    A = [(p[0] + n[0] * o - t[0] * w / 2, p[1] + n[1] * o - t[1] * w / 2, z) for (o, z) in poly]
    B = [(p[0] + n[0] * o + t[0] * w / 2, p[1] + n[1] * o + t[1] * w / 2, z) for (o, z) in poly]
    m = len(poly)
    for k in range(m):
        j = (k + 1) % m
        acc.face([A[k], A[j], B[j], B[k]], col, None, wet=wet)
    acc.face(A, col, None, wet=wet)
    acc.face(list(reversed(B)), col, None, wet=wet)


def local_box(acc, P, t, n, u0, u1, v0, v1, z0, z1, col, wet=0, top=True, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0):
    """A box in a local frame: u along n (from P), v along t, z absolute. UV = metres along the face, height."""
    def at(u, v):
        return (P[0] + n[0] * u + t[0] * v, P[1] + n[1] * u + t[1] * v)
    q = [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]
    uacc = 0.0
    for i in range(4):
        a, c = q[i], q[(i + 1) % 4]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (c[0], c[1], z1), (a[0], a[1], z1)], col,
                 [(uacc, 0.0), (uacc + L, 0.0), (uacc + L, z1 - z0), (uacc, z1 - z0)], wc, wl, wm if L > 0.9 else 3, bid, wet)
        uacc += L
    if top:
        acc.face([(x, y, z1) for (x, y) in q], col, None, wet=wet)
    return q


def catenary(acc, p0, p1, sag, w, col, n=8, wet=0):
    prev = None
    for k in range(n + 1):
        t = k / n
        p = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t - sag * 4 * t * (1 - t))
        if prev:
            tube(acc, prev, p, w / 2, 4, col, wet=wet)
        prev = p


# ------------------------------------------------------------------ wildlife helpers (fish, shoals)
def _axes(yaw, pitch):
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    f = (cp * cy, cp * sy, sp)
    r = (-sy, cy, 0.0)
    u = (-cy * sp, -sy * sp, cp)
    return f, r, u


def fish(acc, neon, p, yaw, pitch, L, c_top, c_bot, glint=None, glow=None):
    """One fish (a spindle body, 9 triangles) at p heading yaw / pitch (rad), length L. Back = c_top, belly = c_bot.
    glint: an emissive colour for a photophore dot on the flank (written to `neon`), or None."""
    f, r, u = _axes(yaw, pitch)

    def at(a, b, c):
        return (p[0] + f[0] * a + r[0] * b + u[0] * c, p[1] + f[1] * a + r[1] * b + u[1] * c, p[2] + f[2] * a + r[2] * b + u[2] * c)
    nose = at(0.5 * L, 0, 0)
    t_, r_, b_, l_ = at(0.10 * L, 0, 0.17 * L), at(0.10 * L, 0.13 * L, 0), at(0.10 * L, 0, -0.15 * L), at(0.10 * L, -0.13 * L, 0)
    tail = at(-0.40 * L, 0, 0)
    mid = lerp(c_top, c_bot, 0.5)
    acc.face([nose, t_, r_], c_top, wet=1)
    acc.face([nose, r_, b_], mid, wet=1)
    acc.face([nose, b_, l_], mid, wet=1)
    acc.face([nose, l_, t_], c_top, wet=1)
    acc.face([t_, r_, tail], c_top, wet=1)
    acc.face([r_, b_, tail], c_bot, wet=1)
    acc.face([b_, l_, tail], c_bot, wet=1)
    acc.face([l_, t_, tail], c_top, wet=1)
    acc.face([at(-0.36 * L, 0, 0), at(-0.58 * L, 0, 0.22 * L), at(-0.58 * L, 0, -0.22 * L)], mid, wet=1)      # tail fin
    if glow is not None:          # the faint photophore belly: the four belly triangles again, pushed 8 % out, emissive
        c0 = at(0.0, 0.0, 0.0)

        def out(q):
            return tuple(c0[i] + (q[i] - c0[i]) * 1.08 for i in range(3))
        for tri in ((nose, r_, b_), (nose, b_, l_), (r_, b_, tail), (b_, l_, tail)):
            neon.face([out(q) for q in tri], glow, wet=1)
    if glint is not None:
        g = at(0.22 * L, 0.115 * L, 0.02 * L)
        s = 0.07 * L
        for dz in (-s, s):
            neon.face([(g[0] - s, g[1] - s, g[2] + dz), (g[0] + s, g[1] - s, g[2] + dz), (g[0] + s, g[1] + s, g[2] + dz),
                       (g[0] - s, g[1] + s, g[2] + dz)], glint, wet=1)


def shoal_sim(rng, n, centre, kind, R, zlim, steps=9, axis=0.0, spin=1):
    """A small boids run for one shoal: n fish seeded in a blob, then `steps` rounds of separation, alignment,
    cohesion and a field (kind 'ball' / 'ring': a swirl round the vertical axis through `centre`; 'stream': a drift along
    `axis` (rad)). Positions stay inside zlim = (zlo, zhi). -> [(x, y, z, yaw, pitch)]."""
    cx, cy, cz = centre
    P, V = [], []
    for _ in range(n):
        if kind == "ring":
            a, rr = rng.uniform(0, 2 * math.pi), R * rng.uniform(0.75, 1.15)
            P.append([cx + rr * math.cos(a), cy + rr * math.sin(a), cz + rng.uniform(-0.35, 0.35) * R])
        elif kind == "stream":
            a = rng.uniform(-1, 1) * 2.2 * R
            w = rng.uniform(-1, 1) * 0.55 * R
            P.append([cx + math.cos(axis) * a - math.sin(axis) * w, cy + math.sin(axis) * a + math.cos(axis) * w,
                      cz + rng.uniform(-0.4, 0.4) * R])
        else:
            u, v = rng.uniform(-1, 1), rng.uniform(0, 2 * math.pi)
            rr = R * rng.random() ** 0.5
            P.append([cx + rr * math.cos(v), cy + rr * math.sin(v), cz + u * 0.55 * R])
        a0 = rng.uniform(0, 2 * math.pi)
        V.append([math.cos(a0) * 0.6, math.sin(a0) * 0.6, rng.uniform(-0.1, 0.1)])
    sp = 1.1
    for _ in range(steps):
        NP, NV = [], []
        for i in range(n):
            x, y, z = P[i]
            sx = sy = sz = ax = ay = az = mx = my = mz = 0.0
            k = 0
            for j in range(n):
                if j == i:
                    continue
                dx, dy, dz = P[j][0] - x, P[j][1] - y, P[j][2] - z
                d2 = dx * dx + dy * dy + dz * dz
                if d2 < 9.0:
                    k += 1
                    mx += dx
                    my += dy
                    mz += dz
                    ax += V[j][0]
                    ay += V[j][1]
                    az += V[j][2]
                    if d2 < 0.5:
                        sx -= dx
                        sy -= dy
                        sz -= dz
            vx, vy, vz = V[i]
            if k:
                vx += 0.10 * mx / k + 0.25 * (ax / k - vx) + 0.9 * sx
                vy += 0.10 * my / k + 0.25 * (ay / k - vy) + 0.9 * sy
                vz += 0.10 * mz / k + 0.25 * (az / k - vz) + 0.9 * sz
            dx, dy = x - cx, y - cy
            rho = math.hypot(dx, dy) or 1e-6
            if kind == "stream":
                vx += 0.35 * math.cos(axis) * sp - 0.03 * dx * math.sin(axis) ** 2
                vy += 0.35 * math.sin(axis) * sp - 0.03 * dy * math.cos(axis) ** 2
            else:
                vx += spin * 0.35 * (-dy / rho) * sp - 0.10 * (rho - R) * dx / rho
                vy += spin * 0.35 * (dx / rho) * sp - 0.10 * (rho - R) * dy / rho
            vz += -0.12 * (z - cz)
            vl = math.sqrt(vx * vx + vy * vy + vz * vz) or 1e-6
            if vl > 1.25 * sp:
                vx, vy, vz = vx * 1.25 * sp / vl, vy * 1.25 * sp / vl, vz * 1.25 * sp / vl
            NV.append([vx, vy, vz])
            NP.append([x + vx * 0.9, y + vy * 0.9, min(zlim[1], max(zlim[0], z + vz * 0.9))])
        P, V = NP, NV
    out = []
    for p, v in zip(P, V):
        vl = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1e-6
        out.append((p[0], p[1], p[2], math.atan2(v[1], v[0]), math.asin(max(-1.0, min(1.0, v[2] / vl)))))
    return out
