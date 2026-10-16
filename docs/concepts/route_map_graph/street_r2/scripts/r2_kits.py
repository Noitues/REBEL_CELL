"""Street round 2 (exec'd inside r2_scene.py): the facade kits of materials.mix, as per-cell generators.

A face is split into cells (one floor tall, about one module wide), so the room cut (r2_build) can remove exactly the
cells inside an opening, and the closed wall over an opening is built by the SAME kit generator. Accumulators by
material: conc (rough concrete), glass (dark glossy curtain glass), panel (painted metal panels, grilles, mullions),
win (lit glazing / windows, emissive), neon (emissive trims).

Kits (module index m = 0..2 from repetition.guard changes the cell width / slat count / slot spacing):
  glass_curtain  glass cells, mullions + spandrel bands in panel, 22 % of floors lit as office strips, a few lit cells
  panel_grille   panel cells, a louvre of 2-4 slats per floor, small warm windows (p 0.35), an AC unit now and then
  lit_atrium     the lowest 2-3 floors fully glazed and lit (warm or teal), concrete above with continuous lit slots
  concrete_band  the mainline kit's own facade (fgrid facets, scattered windows, ledges) - unchanged, in city_building
"""
_KIT_W = {"glass_curtain": (1.4, 1.7, 2.2), "panel_grille": (1.6, 1.9, 2.4), "lit_atrium": (1.7, 2.0, 2.6)}
GLASS_COL = (0.22, 0.26, 0.34)
METAL_COL = (0.20, 0.20, 0.24)


def _lerp3(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t)


def _cell_pts(a, c, z0, z1, u0, u1, nx, ny, off):
    """A face rectangle between along-fractions u0..u1 and heights z0..z1, pushed `off` along the normal."""
    p0 = (a[0] + (c[0] - a[0]) * u0 + nx * off, a[1] + (c[1] - a[1]) * u0 + ny * off)
    p1 = (a[0] + (c[0] - a[0]) * u1 + nx * off, a[1] + (c[1] - a[1]) * u1 + ny * off)
    return [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], z1), (p0[0], p0[1], z1)]


def _boxq(acc, a, c, z0, z1, u0, u1, nx, ny, d0, d1, col, bid):
    """A small box on the face: along u0..u1, heights z0..z1, depth d0..d1 out of the face (5 faces, no back)."""
    f = _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d1)
    b = _cell_pts(a, c, z0, z1, u0, u1, nx, ny, d0)
    acc.face(f, col, bid, fj=0.5)
    acc.face([b[1], b[0], f[0], f[1]], col, bid, fj=0.45)     # bottom
    acc.face([f[3], f[2], b[2], b[3]], col, bid, fj=0.55)     # top


def kit_face(kit, a, c, z0, z1, nx, ny, col, r, accs, module=0, fl=1.9, lit_low=None, lite=False):
    """Draw one face (a -> c along the bottom, z0..z1) in `kit` into accs (dict conc / glass / panel / win / neon)."""
    L = math.hypot(c[0] - a[0], c[1] - a[1])
    h = z1 - z0
    if L < 0.5 or h < 0.5:
        return
    cw = _KIT_W[kit][module % 3]
    nu = max(1, int(round(L / cw)))
    nf = max(1, int(round(h / fl)))
    du = 1.0 / nu
    zs = [z0 + h * j / nf for j in range(nf + 1)]
    bid = rid()
    floor0 = int(round(z0 / fl))
    if kit == "glass_curtain":
        lit_floor = [r.random() < 0.22 for _ in range(nf)]
        for j in range(nf):
            for i in range(nu):
                u0, u1 = i * du, (i + 1) * du
                accs["glass"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0, u1, nx, ny, 0.0), GLASS_COL, bid, fj=0.5)
                # mullion (left edge of the cell, every cell; module 1: every 2nd heavier) and spandrel (cell bottom)
                mw = 0.06 / max(L, 1e-3)
                if not lite and (module != 1 or i % 2 == 0):
                    accs["panel"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0, u0 + mw * (2 if module == 1 else 1), nx, ny, 0.05),
                                       METAL_COL, bid, fj=0.5)
                if not lite:
                    accs["panel"].face(_cell_pts(a, c, zs[j], zs[j] + 0.22, u0, u1, nx, ny, 0.04), METAL_COL, bid, fj=0.5)
                if lit_floor[j] and r.random() < 0.85:
                    s = 0.5 + 0.5 * r.random()
                    wc = (0.78, 0.9, 1.0) if r.random() < 0.7 else (0.55, 1.0, 0.9)
                    accs["win"].face(_cell_pts(a, c, zs[j] + 0.35, zs[j + 1] - 0.3, u0 + 0.06 * du, u1 - 0.06 * du, nx, ny, 0.02),
                                     tuple(v * s for v in wc), (0, 0, 0), fj=0.5)
                elif r.random() < 0.08:
                    accs["win"].face(_cell_pts(a, c, zs[j] + 0.4, zs[j + 1] - 0.35, u0 + 0.12 * du, u1 - 0.12 * du, nx, ny, 0.02),
                                     tuple(v * (0.4 + 0.4 * r.random()) for v in r.choice(WIN_COLS)), (0, 0, 0), fj=0.5)
    elif kit == "panel_grille":
        slats = 2 + module
        pc = tuple(v * 0.9 for v in col)
        dk = tuple(v * 0.55 for v in col)
        for j in range(nf):
            for i in range(nu):
                u0, u1 = i * du, (i + 1) * du
                accs["panel"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0, u1, nx, ny, 0.0), pc, bid, fj=0.4 + 0.2 * r.random())
                zt = zs[j + 1]
                for k in range(0 if lite else slats):
                    zz = zt - 0.12 - k * 0.2
                    _boxq(accs["panel"], a, c, zz - 0.06, zz, u0, u1, nx, ny, 0.0, 0.2, dk, bid)
                if r.random() < 0.35:
                    s = 0.45 + 0.5 * r.random()
                    um = (u0 + u1) / 2
                    hw = 0.3 / max(L, 1e-3)
                    accs["win"].face(_cell_pts(a, c, zs[j] + 0.45, zs[j] + 1.0, um - hw, um + hw, nx, ny, 0.03),
                                     tuple(v * s for v in r.choice(WIN_COLS[:3] + WIN_COLS[5:])), (0, 0, 0), fj=0.5)
                if r.random() < 0.05 and j > 0:
                    um = (u0 + u1) / 2
                    hw = 0.35 / max(L, 1e-3)
                    _boxq(accs["conc"], a, c, zs[j] + 0.05, zs[j] + 0.5, um - hw, um + hw, nx, ny, 0.0, 0.45, (0.32, 0.32, 0.35), bid)
    elif kit == "lit_atrium":
        low = lit_low if lit_low is not None else 2 + r.randrange(2)
        every = 2 + module
        warm = r.random() < 0.55
        lc = (1.0, 0.74, 0.46) if warm else (0.45, 0.95, 1.0)
        sc = r.choice([(1.0, 0.3, 0.7), (0.3, 0.85, 1.0), (1.0, 0.6, 0.2), (0.7, 0.45, 1.0)])
        for j in range(nf):
            fj_ = floor0 + j
            for i in range(nu):
                u0, u1 = i * du, (i + 1) * du
                if fj_ < low:
                    accs["win"].face(_cell_pts(a, c, zs[j] + 0.08, zs[j + 1] - 0.08, u0 + 0.03 * du, u1 - 0.03 * du, nx, ny, 0.0),
                                     tuple(v * (0.55 + 0.25 * r.random()) for v in lc), (0, 0, 0), fj=0.5)
                    accs["panel"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0, u0 + 0.07 / max(L, 1e-3), nx, ny, 0.04), METAL_COL, bid, fj=0.5)
                    accs["panel"].face(_cell_pts(a, c, zs[j + 1] - 0.1, zs[j + 1], u0, u1, nx, ny, 0.04), METAL_COL, bid, fj=0.5)
                else:
                    accs["conc"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0, u1, nx, ny, 0.0), col, bid, fj=0.45 + 0.1 * r.random())
                    if i % every == 0:
                        hw = 0.11 / max(L, 1e-3)
                        accs["win"].face(_cell_pts(a, c, zs[j], zs[j + 1], u0 + 0.5 * du - hw, u0 + 0.5 * du + hw, nx, ny, 0.03),
                                         tuple(v * 0.75 for v in sc), (0, 0, 0), fj=0.5)
                    elif r.random() < 0.1:
                        accs["win"].face(_cell_pts(a, c, zs[j] + 0.5, zs[j + 1] - 0.4, u0 + 0.2 * du, u1 - 0.2 * du, nx, ny, 0.02),
                                         tuple(v * 0.6 for v in r.choice(WIN_COLS)), (0, 0, 0), fj=0.5)


def roof_clutter(kit, top, zt, r, acc_s, acc_n, kinds):
    """Roof clutter by kit (>= 3 kinds over a frontage): ac, tank, vent_stack, antenna, dish. `kinds` collects them."""
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if x1 - x0 < 2.2 or y1 - y0 < 2.2:
        return
    if kit in ("glass_curtain", "panel_grille"):
        for _ in range(r.randint(1, 3)):                       # vent stacks
            vx, vy = r.uniform(x0 + 0.5, x1 - 0.5), r.uniform(y0 + 0.5, y1 - 0.5)
            cyl36(vx, vy, zt, zt + r.uniform(1.0, 2.4), r.uniform(0.25, 0.45), (0.3, 0.3, 0.34))
        kinds.add("vent_stack")
    if kit in ("panel_grille", "lit_atrium"):
        for _ in range(r.randint(1, 3)):                       # AC units
            vx, vy = r.uniform(x0 + 0.4, x1 - 1.3), r.uniform(y0 + 0.4, y1 - 1.1)
            box(vx, vy, zt, vx + 0.9, vy + 0.7, zt + 0.55, (0.34, 0.34, 0.38), facet=False)
        kinds.add("ac")
    if kit in ("lit_atrium", "glass_curtain") and r.random() < 0.6:   # dish on a stub
        dx, dy = r.uniform(x0 + 1.0, x1 - 1.0), r.uniform(y0 + 1.0, y1 - 1.0)
        beam((dx, dy, zt), (dx, dy, zt + 1.0), 0.14, (0.25, 0.25, 0.3))
        rr = r.uniform(0.6, 1.0)
        pts = [(dx + rr * math.cos(2 * math.pi * k / 10), dy - 0.3, zt + 1.4 + rr * math.sin(2 * math.pi * k / 10)) for k in range(10)]
        SOLID.face(pts, (0.55, 0.55, 0.6), rid())
        kinds.add("dish")
    if r.random() < 0.35:                                     # antenna with a red light
        ax, ay = (x0 + x1) / 2 + r.uniform(-0.5, 0.5), (y0 + y1) / 2
        hh = r.uniform(2.5, 5.5)
        beam((ax, ay, zt), (ax, ay, zt + hh), 0.12, (0.25, 0.25, 0.3))
        acc_n.face([(ax - 0.22, ay, zt + hh), (ax + 0.22, ay, zt + hh), (ax + 0.22, ay, zt + hh + 0.35), (ax - 0.22, ay, zt + hh + 0.35)],
                   RED, (0, 0, 0))
        ANTS.append((ax, ay, zt + hh + 0.2))
        kinds.add("antenna")
