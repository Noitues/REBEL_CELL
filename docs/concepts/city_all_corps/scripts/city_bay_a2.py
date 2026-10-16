"""City-all-corps round 5 (exec'd by city_build.py after city_transit_a2.py): the character of the bay and the coast.

Coast: a smooth sand strip + a faint surf line on the plan's coastline (it hides the cell staircase), a lit promenade where the
coast meets the city. Marinas with moored boats and small piers, harbour buoys down the channel, cargo ships at anchor with
anchor lights, ferries on the plan's ferry routes (lit decks, wakes), a lighthouse on a headland, the Bay Barrier's gate
towers and signal lights, a fort island and a park island.  (The port and Tethys are untouched.)
"""
RBY = random.Random(CP.SEEDS["landmark"] + 301)
SAND = (0.55, 0.50, 0.40) if DAYM else (0.14, 0.13, 0.12)
COAST = [tuple(p) for p in A2D["coast"]]


def resample(pts, step):
    out = [pts[0]]
    carry = 0.0
    for k in range(1, len(pts)):
        a, b = pts[k - 1], pts[k]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-9:
            continue
        t = step - carry
        while t <= L:
            out.append((a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L))
            t += step
        carry = L - (t - step)
    return out


def land_class(lx, ly):
    ci, cj = int(math.floor(lx)), int(math.floor(ly))
    if is_water_cell(ci, cj):
        return -1
    return cls_at(ci, cj) if in_grid(ci, cj) else 13


# ------------------------------------------------------------------ the coast: sand strip, surf line, promenade
CS = resample(COAST, 0.5)                       # a point every 50 m
n_prom = n_sand = 0
coast_pts = []                                  # (lot point, outward unit normal in lots, land class)
for k in range(1, len(CS) - 1):
    p, a, b = CS[k], CS[k - 1], CS[k + 1]
    tx, ty = b[0] - a[0], b[1] - a[1]
    tl = math.hypot(tx, ty) or 1.0
    tx, ty = tx / tl, ty / tl
    n1 = (-ty, tx)
    c1 = land_class(p[0] + n1[0] * 0.9, p[1] + n1[1] * 0.9)
    c2 = land_class(p[0] - n1[0] * 0.9, p[1] - n1[1] * 0.9)
    if c1 >= 0 > c2:
        out = (-n1[0], -n1[1])
        lc = c1
    elif c2 >= 0 > c1:
        out = n1
        lc = c2
    else:
        continue
    if not (-110 < p[0] < 120 and -110 < p[1] < 120):
        continue
    coast_pts.append((p, out, lc))
for k in range(len(coast_pts) - 1):
    (p, out, lc), (q, _, _) = coast_pts[k], coast_pts[k + 1]
    if math.hypot(q[0] - p[0], q[1] - p[1]) > 1.2 or lc == 9 or lc == 1:
        continue
    pw, qw = W(p), W(q)
    strip(GROUND, pw, qw, 3.0, 0.12, SAND if lc not in (11, 12) else sc(SAND, 0.8))
    strip(NEON, pw, qw, 0.35, 0.16, sc((0.55, 0.8, 1.0), 0.07))
    n_sand += 1
    if lc in (11, 12) and k % 10 == 0:                       # the lit promenade: a lamp row just inland
        inl = (p[0] - out[0] * 0.55, p[1] - out[1] * 0.55)
        iw = W(inl)
        bar(SURF, (iw[0], iw[1], 0.0), (iw[0], iw[1], 2.2), 0.12, (0.3, 0.3, 0.32))
        box(NEON, iw[0] - 0.2, iw[1] - 0.2, 2.1, iw[0] + 0.2, iw[1] + 0.2, 2.4, (1.0, 0.78, 0.5))
        n_prom += 1
    if lc in (11, 12) and k % 3 == 0:                        # a warm light line along the promenade
        i2 = W((p[0] - out[0] * 0.45, p[1] - out[1] * 0.45))
        j2 = W((q[0] - out[0] * 0.45, q[1] - out[1] * 0.45))
        strip(NEON, i2, j2, 0.3, 0.2, sc((1.0, 0.72, 0.4), 0.14))
print("COAST sand %d promenade lamps %d %.1fs" % (n_sand, n_prom, time.time() - T0), flush=True)

# ------------------------------------------------------------------ boats and small ships
BOAT_COLS = [(0.85, 0.85, 0.82), (0.2, 0.3, 0.5), (0.7, 0.15, 0.1), (0.9, 0.7, 0.2), (0.25, 0.25, 0.28)]
CCP2 = [(0.72, 0.30, 0.08), (0.58, 0.22, 0.08), (0.14, 0.36, 0.38), (0.45, 0.42, 0.40), (0.80, 0.46, 0.10), (0.62, 0.12, 0.08), (0.20, 0.30, 0.50)]


def boat(x, y, ux, uy, L=2.6, B=0.9, col=None, lamp=True):
    nx, ny = -uy, ux
    q = [(x - ux * L / 2 - nx * B / 2, y - uy * L / 2 - ny * B / 2), (x + ux * L / 2 - nx * B / 3, y + uy * L / 2 - ny * B / 3),
         (x + ux * L / 2 + nx * B / 3, y + uy * L / 2 + ny * B / 3), (x - ux * L / 2 + nx * B / 2, y - uy * L / 2 + ny * B / 2)]
    prism(SURF, q, ZW - 0.3, ZW + 0.7, col or RBY.choice(BOAT_COLS), top_col=(0.5, 0.5, 0.5))
    if lamp:
        box(NEON, x - 0.12, y - 0.12, ZW + 0.7, x + 0.12, y + 0.12, ZW + 1.4, (1.0, 0.9, 0.7) if RBY.random() < 0.7 else (1.0, 0.3, 0.2))


def ship(x, y, ux, uy, Lh=9.0, Bh=2.0, hull=None, lit=True):
    """a cargo ship (hull, stern bridge, container stacks) with anchor lights."""
    nx, ny = -uy, ux
    pts = []
    for m in range(13):
        t = -1.0 + 2.0 * m / 12
        taper = 1.0 if t < 0.7 else max(0.15, 1.0 - (t - 0.7) / 0.3 * 0.85)
        pts.append((t * Lh, taper))
    top = [(x + ux * u_ + nx * Bh * tp, y + uy * u_ + ny * Bh * tp) for (u_, tp) in pts] + \
          [(x + ux * u_ - nx * Bh * tp, y + uy * u_ - ny * Bh * tp) for (u_, tp) in reversed(pts)]
    prism(SURF, top, ZW - 2.0, ZW + 1.8, hull or RBY.choice([(0.16, 0.18, 0.22), (0.45, 0.10, 0.08), (0.10, 0.20, 0.30)]), top_col=(0.30, 0.30, 0.30))
    br = [(x - ux * Lh * 0.9 + nx * Bh * 0.8, y - uy * Lh * 0.9 + ny * Bh * 0.8), (x - ux * Lh * 0.7 + nx * Bh * 0.8, y - uy * Lh * 0.7 + ny * Bh * 0.8),
          (x - ux * Lh * 0.7 - nx * Bh * 0.8, y - uy * Lh * 0.7 - ny * Bh * 0.8), (x - ux * Lh * 0.9 - nx * Bh * 0.8, y - uy * Lh * 0.9 - ny * Bh * 0.8)]
    prism(SURF, br, ZW + 1.8, ZW + 5.2, (0.85, 0.85, 0.83), wc=(1.0, 0.86, 0.6), wl=0.6 if lit else 0.1, wm=0, bid=RBY.random())
    u_ = -Lh * 0.6
    while u_ < Lh * 0.6:
        for lane in (-0.5, 0.0, 0.5):
            for lv in range(RBY.randint(1, 3)):
                cx_, cy_ = x + ux * u_ + nx * lane * Bh, y + uy * u_ + ny * lane * Bh
                hw_, hd_ = (0.9, 0.5) if abs(ux) > 0.7 else (0.5, 0.9)
                box(SURF, cx_ - hw_, cy_ - hd_, ZW + 1.8 + lv * 0.6, cx_ + hw_, cy_ + hd_, ZW + 2.4 + lv * 0.6, RBY.choice(CCP2))
        u_ += 1.4
    box(NEON, x - ux * Lh * 0.8 - 0.2, y - uy * Lh * 0.8 - 0.2, ZW + 5.2, x - ux * Lh * 0.8 + 0.2, y - uy * Lh * 0.8 + 0.2, ZW + 5.7, (1.0, 0.95, 0.85))
    box(NEON, x + ux * Lh * 0.9 - 0.15, y + uy * Lh * 0.9 - 0.15, ZW + 1.8, x + ux * Lh * 0.9 + 0.15, y + uy * Lh * 0.9 + 0.15, ZW + 3.2, (1.0, 0.95, 0.85))


def ferry(x, y, ux, uy):
    nx, ny = -uy, ux
    L, B = 4.2, 1.15
    q = [(x - ux * L - nx * B, y - uy * L - ny * B), (x + ux * L * 0.7 - nx * B, y + uy * L * 0.7 - ny * B), (x + ux * L, y + uy * L),
         (x + ux * L * 0.7 + nx * B, y + uy * L * 0.7 + ny * B), (x - ux * L + nx * B, y - uy * L + ny * B)]
    prism(SURF, q, ZW - 0.6, ZW + 1.2, (0.9, 0.9, 0.92), top_col=(0.6, 0.6, 0.62))
    q2 = [(x - ux * L * 0.8 - nx * B * 0.8, y - uy * L * 0.8 - ny * B * 0.8), (x + ux * L * 0.5 - nx * B * 0.8, y + uy * L * 0.5 - ny * B * 0.8),
          (x + ux * L * 0.5 + nx * B * 0.8, y + uy * L * 0.5 + ny * B * 0.8), (x - ux * L * 0.8 + nx * B * 0.8, y - uy * L * 0.8 + ny * B * 0.8)]
    prism(SURF, q2, ZW + 1.2, ZW + 2.6, (0.88, 0.88, 0.9), wc=(1.0, 0.9, 0.7), wl=0.95, wm=1, bid=RBY.random())
    box(NEON, x + ux * L * 0.95 - 0.15, y + uy * L * 0.95 - 0.15, ZW + 1.2, x + ux * L * 0.95 + 0.15, y + uy * L * 0.95 + 0.15, ZW + 1.9, (0.3, 1.0, 0.4))
    for sd in (-1, 1):                                       # the wake
        strip(NEON, (x - ux * L, y - uy * L), (x - ux * (L + 9.0) + nx * sd * 3.0, y - uy * (L + 9.0) + ny * sd * 3.0), 0.5, ZW + 0.05, sc((0.7, 0.85, 1.0), 0.07))


# ------------------------------------------------------------------ marinas (a pier with moored boats) along the city coast of the bay
BAYBOX = (-3700.0, 3500.0, -7400.0, -2000.0)


def in_bay(p):
    X, Y = (p[0] - CX) * 100.0, (CY - p[1]) * 100.0
    return BAYBOX[0] < X < BAYBOX[1] and BAYBOX[2] < Y < BAYBOX[3]


cands = [cp for cp in coast_pts if in_bay(cp[0]) and cp[2] in (11, 12, 13, 3)]
RBY.shuffle(cands)
marinas = []
for (p, out, lc) in cands:
    if len(marinas) >= 7:
        break
    if any(math.hypot(p[0] - m[0], p[1] - m[1]) < 11.0 for m in marinas):
        continue
    if any(not is_water_cell(int(math.floor(p[0] + out[0] * d)), int(math.floor(p[1] + out[1] * d))) for d in (1.2, 2.0, 3.0)):
        continue
    marinas.append(p)
    pw = W(p)
    ow = (out[0], -out[1])                                 # outward direction in world (lot y flips)
    nxw, nyw = -ow[1], ow[0]
    Lp = RBY.uniform(14.0, 22.0)
    q = [(pw[0] - nxw * 0.6, pw[1] - nyw * 0.6), (pw[0] + ow[0] * Lp - nxw * 0.6, pw[1] + ow[1] * Lp - nyw * 0.6),
         (pw[0] + ow[0] * Lp + nxw * 0.6, pw[1] + ow[1] * Lp + nyw * 0.6), (pw[0] + nxw * 0.6, pw[1] + nyw * 0.6)]
    prism(SURF, q, ZW - 0.5, ZW + 0.35, (0.3, 0.26, 0.22), top_col=(0.34, 0.3, 0.26))
    for m in range(0, int(Lp), 3):
        bx_, by_ = pw[0] + ow[0] * (m + 1.5), pw[1] + ow[1] * (m + 1.5)
        box(NEON, bx_ - 0.1, by_ - 0.1, ZW + 0.35, bx_ + 0.1, by_ + 0.1, ZW + 1.0, (1.0, 0.82, 0.55))
        for sd in (-1, 1):
            if RBY.random() < 0.8:
                boat(bx_ + nxw * sd * 2.0, by_ + nyw * sd * 2.0, ow[0], ow[1], L=RBY.uniform(2.0, 3.0), B=0.9)
    box(NEON, pw[0] + ow[0] * Lp - 0.2, pw[1] + ow[1] * Lp - 0.2, ZW + 0.35, pw[0] + ow[0] * Lp + 0.2, pw[1] + ow[1] * Lp + 0.2, ZW + 1.6,
        (1.0, 0.15, 0.1) if len(marinas) % 2 else (0.2, 1.0, 0.35))
print("MARINAS", len(marinas), "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ cargo ships at anchor in the bay + harbour buoys down the channel
anch = []
tries = 0
while len(anch) < 10 and tries < 400:
    tries += 1
    X, Y = RBY.uniform(-3000, 2400), RBY.uniform(-7000, -3000)
    lx_, ly_ = X / 100 + CX, CY - Y / 100
    ci, cj = int(math.floor(lx_)), int(math.floor(ly_))
    if not is_water_cell(ci, cj) or dland_at(ci, cj) < 7 or any(math.hypot(lx_ - a[0], ly_ - a[1]) < 9.0 for a in anch):
        continue
    if (-4000 < X < -2200 and -6800 < Y < -3600) or (700 < X < 1900 and -6900 < Y < -5800) or (-1200 < X < -200 and -6400 < Y < -5400):
        continue                                         # the pier city, the park island and the fort island stay clear
    anch.append((lx_, ly_))
    wx, wy = W((lx_, ly_))
    ang = RBY.uniform(0, 2 * math.pi)
    ship(wx, wy, math.cos(ang), math.sin(ang), Lh=RBY.uniform(6.5, 10.0), Bh=RBY.uniform(1.5, 2.2))
bu = 0
for t in range(0, 14):                                  # buoys: red and green pairs down the channel to the barrier gap
    f = t / 13.0
    X, Y = -150.0 * (1 - f), -4200.0 * (1 - f) + -7750.0 * f
    for sd, col in ((-1, (1.0, 0.1, 0.08)), (1, (0.15, 1.0, 0.3))):
        wx, wy = (X * 0.06 + sd * (9.0 + 4.0 * f), Y * 0.06)
        cyl(SMOOTH, wx, wy, ZW - 0.2, ZW + 0.9, 0.35, 8, (0.8, 0.8, 0.8))
        box(NEON, wx - 0.18, wy - 0.18, ZW + 0.9, wx + 0.18, wy + 0.18, ZW + 1.3, col)
        bu += 1
print("ANCHORED", len(anch), "buoys", bu, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ ferries on the plan's ferry routes (lit boats, wakes, terminal lights)
nf = 0
for route in A2D["ferries"]:
    rw = [W(p) for p in route]
    if len(rw) < 2:
        continue
    for k in (0.3, 0.7):
        i = int(k * (len(rw) - 1))
        a, b = rw[i], rw[min(i + 1, len(rw) - 1)]
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        t = (k * (len(rw) - 1)) - i
        ferry(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
        nf += 1
    for end in (rw[0], rw[-1]):
        box(NEON, end[0] - 0.3, end[1] - 0.3, ZW + 0.4, end[0] + 0.3, end[1] + 0.3, ZW + 3.0, (1.0, 0.8, 0.5))
print("FERRIES", nf, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ a lighthouse on the most exposed headland of the bay
best = None
for (p, out, lc) in coast_pts:
    if not in_bay(p) or lc not in (11, 12, 13, 3):
        continue
    exp_ = sum(1 for dx in range(-8, 9, 2) for dy in range(-8, 9, 2) if is_water_cell(int(math.floor(p[0] + dx)), int(math.floor(p[1] + dy))))
    key = (-exp_, round(p[0], 2), round(p[1], 2))
    if best is None or key < best[0]:
        best = (key, p, out)
if best is not None:
    p, out = best[1], best[2]
    lh = W((p[0] - out[0] * 1.0, p[1] - out[1] * 1.0))
    cyl(SURF, lh[0], lh[1], 0.0, 2.0, 3.2, 12, (0.3, 0.3, 0.32))
    for m in range(6):
        cyl(SURF, lh[0], lh[1], 2.0 + m * 3.2, 5.2 + m * 3.2, 2.1 - m * 0.18, 12, (0.9, 0.9, 0.9) if m % 2 == 0 else (0.75, 0.12, 0.1), ts=0.92)
    ztop = 5.2 + 6 * 3.2
    ring_line(NEON, lh[0], lh[1], ztop, 2.4, 0.3, (1.0, 0.85, 0.5), n=12)
    cyl(SURF, lh[0], lh[1], ztop, ztop + 2.0, 0.9, 10, (0.4, 0.4, 0.42))
    box(NEON, lh[0] - 0.7, lh[1] - 0.7, ztop + 0.3, lh[0] + 0.7, lh[1] + 0.7, ztop + 1.8, (1.0, 0.95, 0.8))
    cyl(SURF, lh[0], lh[1], ztop + 2.0, ztop + 2.6, 1.1, 10, (0.75, 0.12, 0.1))
    ob = (out[0], -out[1])
    if not DAYM:
        for ang in (0.0, 1.6, -1.6):
            ca, sa = math.cos(ang), math.sin(ang)
            dx_, dy_ = ob[0] * ca - ob[1] * sa, ob[0] * sa + ob[1] * ca
            LIGHT_SPOTS.append(dict(loc=(lh[0], lh[1], ztop + 1.0), tgt=(lh[0] + dx_ * 90.0, lh[1] + dy_ * 90.0, 0.0), col=(1.0, 0.92, 0.7), power=2.5e5,
                                    cone=14.0, blend=0.5, k=1.0))
    print("LIGHTHOUSE at lot", [round(v, 1) for v in p], flush=True)

# ------------------------------------------------------------------ the Bay Barrier: gate towers with signal lights and swing gates at the lock gap
for d_ in A2D["dams"]:
    if d_["kind"] != "barrier":
        continue
    pe = W(d_["pts"][-1]) if abs(d_["pts"][-1][0] - CX) < abs(d_["pts"][0][0] - CX) else W(d_["pts"][0])
    sgn = -1.0 if pe[0] < 0 else 1.0
    box(SURF, pe[0] - 1.6, pe[1] - 1.6, ZW, pe[0] + 1.6, pe[1] + 1.6, 11.0, (0.34, 0.35, 0.39), wc=(1.0, 0.85, 0.55), wl=0.6, wm=0, bid=0.4)
    box(NEON, pe[0] - 1.7, pe[1] - 1.7, 11.0, pe[0] + 1.7, pe[1] + 1.7, 11.3, (1.0, 0.3, 0.2) if sgn < 0 else (0.2, 1.0, 0.4))
    for k in range(3):
        box(NEON, pe[0] - 0.2, pe[1] - 1.9, 4.0 + k * 2.2, pe[0] + 0.2, pe[1] - 1.6, 4.5 + k * 2.2, (1.0, 0.1, 0.08) if k % 2 == 0 else (0.2, 1.0, 0.4))
    bar(SURF, (pe[0], pe[1], 6.0), (pe[0] - sgn * 12.0, pe[1] + 4.0, 6.0), 0.6, (0.9, 0.9, 0.2))
    bar(NEON, (pe[0], pe[1], 6.3), (pe[0] - sgn * 12.0, pe[1] + 4.0, 6.3), 0.2, (1.0, 0.2, 0.15))
    P_ = [W(p) for p in d_["pts"]]
    for k in range(0, len(P_), 2):
        for sd in (-1, 1):
            bx_, by_ = P_[k][0], P_[k][1] + sd * 1.8
            bar(SURF, (bx_, by_, 0.0), (bx_, by_, 3.2), 0.12, (0.3, 0.3, 0.32))
            box(NEON, bx_ - 0.2, by_ - 0.2, 3.1, bx_ + 0.2, by_ + 0.2, 3.5, (1.0, 0.8, 0.5))


# ------------------------------------------------------------------ the islands of the bay: a fort and a park
def island(X, Y, r, top_col, shore_col):
    wx, wy = X * 0.06, Y * 0.06
    zb = -9.0
    rb = r * 1.45                                          # a short skirt on the shoal
    cyl(SURF, wx, wy, zb, ZW + 0.5, rb, 28, shore_col, ts=r * 0.95 / rb, top=False)
    cyl(SURF, wx, wy, ZW + 0.5, ZW + 1.4, r * 0.88, 28, top_col, ts=0.92, top_col=top_col)
    ring_line(NEON, wx, wy, ZW + 0.5, r * 0.9, 0.18, sc((0.55, 0.8, 1.0), 0.08), n=40)
    return wx, wy


fx, fy = island(-700.0, -5900.0, 22.0, (0.22, 0.22, 0.24), (0.26, 0.25, 0.24))
for k in range(20):                                       # the fort: a ring wall, four corner towers, a keep
    a0, a1 = 2 * math.pi * k / 20, 2 * math.pi * (k + 1) / 20
    q = [(fx + 15.0 * math.cos(a0), fy + 15.0 * math.sin(a0)), (fx + 15.0 * math.cos(a1), fy + 15.0 * math.sin(a1)),
         (fx + 13.4 * math.cos(a1), fy + 13.4 * math.sin(a1)), (fx + 13.4 * math.cos(a0), fy + 13.4 * math.sin(a0))]
    prism(SURF, q, ZW + 1.4, ZW + 5.4, (0.32, 0.30, 0.28), wc=(1.0, 0.8, 0.5), wl=0.25, wm=0, bid=k / 20.0)
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2
    tx_, ty_ = fx + 15.0 * math.cos(a), fy + 15.0 * math.sin(a)
    cyl(SURF, tx_, ty_, ZW + 1.4, ZW + 9.5, 2.3, 10, (0.34, 0.32, 0.30), wc=(1.0, 0.8, 0.5), wl=0.4, wm=0, bid=k * 0.2)
    box(NEON, tx_ - 0.5, ty_ - 0.5, ZW + 9.5, tx_ + 0.5, ty_ + 0.5, ZW + 10.2, (1.0, 0.7, 0.35))
cyl(SURF, fx, fy, ZW + 1.4, ZW + 12.0, 5.0, 14, (0.36, 0.34, 0.32), wc=(1.0, 0.82, 0.55), wl=0.5, wm=0, bid=0.7)
ring_line(NEON, fx, fy, ZW + 12.1, 5.1, 0.25, (1.0, 0.75, 0.4), n=14)
box(NEON, fx - 0.6, fy - 0.6, ZW + 12.0, fx + 0.6, fy + 0.6, ZW + 14.5, (1.0, 0.85, 0.6))
px, py = island(1300.0, -6400.0, 17.0, PK["lawn"], (0.24, 0.23, 0.2))
park_trees(px - 12, py - 12, px + 12, py + 12, random.Random(7761), 7, (3, 5))
box(SURF, px - 2.0, py - 2.0, ZW + 1.4, px + 2.0, py + 2.0, ZW + 3.6, (0.5, 0.48, 0.45), wc=(1.0, 0.85, 0.6), wl=0.6, wm=0, bid=0.3)
ring_line(NEON, px, py, ZW + 3.7, 2.4, 0.2, (1.0, 0.8, 0.5), n=12)
for k in range(10):
    a = 2 * math.pi * k / 10
    box(NEON, px + 8.5 * math.cos(a) - 0.15, py + 8.5 * math.sin(a) - 0.15, ZW + 1.4, px + 8.5 * math.cos(a) + 0.15, py + 8.5 * math.sin(a) + 0.15, ZW + 2.4, (1.0, 0.8, 0.5))
print("BAY done %.1fs" % (time.time() - T0), flush=True)
