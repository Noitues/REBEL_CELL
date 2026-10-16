"""hq_kit.downtown: dense city blocks right up to an HQ compound's walls (designer review 2026-10-15, "bring the city
CLOSE to every HQ": no empty perimeter, no plinth belt; a real downtown). Blender-side geometry through injected helpers
(as city_ring), pure python itself.

    from hq_kit import downtown
    out = downtown.build(cfg, A, geo, pal)   # -> dict(roofs=[(cx, cy, h, "down")], lamps=[(x, y, z, col)], n_towers)

geo: box, tube (the kit's), bc(cx, cy) = set the current building centre on every city accumulator (the section clip
     reads it per face, so a building is cut as a whole: flat cut tops, never a sloped slice).
A:   accumulators city, city_neon, city_sign, city_small, city_metal, ground, streaks.
cfg keys (preset hq.downtown):
  seed          the block seed
  keep          ("rect", hx, hy) | ("circle", r): the compound's outer edge (walls + moat / yard / podium) in BU
  street0       the street that runs round the compound (BU): the first block face stands this far from `keep`
  cell, street  block pitch and street width (BU); a block = cell - street square, split in lots
  r_out         half-size of the filled square (the hq_kit ring city starts beyond it)
  h_near, h_far tower height ranges at the compound and at r_out (BU; 1 storey = 8 BU in the r3 units... the city
                windows are on a 3.1 BU pitch: these are the city's own storeys)
  tall_p        share of lots that get a tall tower (x1.6-2.2)
  sign_p        blade sign probability per street face; holo_p roof holo billboards; lamp_step street-lamp spacing
Rules:
  grid          the x grid lines run from +-(hx + street0) outward every `cell` (y likewise from hy): the blocks' inner
                faces line the compound street on every side, so the city meets the walls all round (360 degrees)
  lots          2 x 2 (or 3 x 2) lots per block, no gaps (attached rows), heights by distance from the keep
  dressing      ground-floor shop fronts + awnings on street faces, blade signs, AC units, crown trims, rooftop tanks /
                antennas / red beacons, roof holo billboards facing the compound, street lamps, sidewalks, traffic
Seeds: cfg seed (towers), seed + 1 (dressing), seed + 2 (traffic).
"""
import math
import random

BEACON = (1.0, 0.06, 0.04)
SIGN_COLS = [(1.0, 0.16, 0.6), (0.16, 0.8, 1.0), (1.0, 0.62, 0.22), (0.95, 0.95, 1.0), (1.0, 0.2, 0.25),
             (0.55, 1.0, 0.45), (1.0, 0.85, 0.3)]
SHOP_COLS = [(1.0, 0.62, 0.32), (1.0, 0.78, 0.5), (0.7, 0.85, 1.0), (1.0, 0.4, 0.62), (0.5, 0.95, 1.0)]


def _keep_dist(cfg, x, y):
    """Distance from the keep's edge (0 on it, negative inside)."""
    k = cfg["keep"]
    if k[0] == "rect":
        dx, dy = abs(x) - k[1], abs(y) - k[2]
        if dx <= 0 and dy <= 0:
            return max(dx, dy)
        return math.hypot(max(dx, 0.0), max(dy, 0.0))
    return math.hypot(x, y) - k[1]


def _lines(start, cell, stop):
    out = []
    v = start
    while v < stop:
        out.append(v)
        v += cell
    return out


def build(cfg, A, geo, pal):
    box, tube, bc = geo.box, geo.tube, geo.bc
    rr = random.Random(cfg["seed"])
    rd = random.Random(cfg["seed"] + 1)
    cell, st, R = cfg["cell"], cfg["street"], cfg["r_out"]
    k = cfg["keep"]
    s0 = cfg["street0"]
    hx = (k[1] if k[0] == "rect" else k[1]) + s0
    hy = (k[2] if k[0] == "rect" else k[1]) + s0
    # block origins: inner faces on the compound street, outward every cell (both signs, both axes)
    xs = sorted([-x - (cell - st) for x in _lines(hx, cell, R)] + _lines(hx, cell, R))
    ys = sorted([-y - (cell - st) for y in _lines(hy, cell, R)] + _lines(hy, cell, R))
    # the band between -hx and hx (along the compound's own sides) is filled with the same pitch, centred
    inner_x = _lines(-hx + st * 0.5, cell, hx - (cell - st))
    inner_y = _lines(-hy + st * 0.5, cell, hy - (cell - st))
    xs = sorted(set(round(v, 3) for v in xs + inner_x))
    ys = sorted(set(round(v, 3) for v in ys + inner_y))
    bw = cell - st
    ROOFS, LAMPS = [], []
    n_t = 0
    hn, hf = cfg["h_near"], cfg["h_far"]
    for x0 in xs:
        for y0 in ys:
            x1, y1 = x0 + bw, y0 + bw
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if max(abs(cx), abs(cy)) > R:
                continue
            # the block's distance from the keep (its nearest corner): skip blocks inside the compound street
            dmin = min(_keep_dist(cfg, x, y) for x in (x0, x1, cx) for y in (y0, y1, cy))
            if dmin < s0 - 0.5 and k[0] == "rect":
                continue
            # sidewalk slab
            nx_ = 3 if rr.random() < 0.3 else 2
            ny_ = 2
            if rr.random() < 0.5:
                nx_, ny_ = ny_, nx_
            lots = []
            for i in range(nx_):
                for j in range(ny_):
                    a0, a1 = x0 + bw * i / nx_, x0 + bw * (i + 1) / nx_
                    b0, b1 = y0 + bw * j / ny_, y0 + bw * (j + 1) / ny_
                    lx, ly = (a0 + a1) / 2, (b0 + b1) / 2
                    if _keep_dist(cfg, lx, ly) < s0 + 1.0:
                        continue
                    if in_corridor(cfg, a0, b0, a1, b1):           # a rail viaduct's corridor (Meridian v2)
                        continue
                    lots.append((a0, b0, a1, b1, i, j))
            if not lots:
                continue
            box(A["ground"], x0 - 1.4, y0 - 1.4, -0.02, x1 + 1.4, y1 + 1.4, 0.16, (0.22, 0.22, 0.24), k=1.0)
            for (a0, b0, a1, b1, i, j) in lots:
                lx, ly = (a0 + a1) / 2, (b0 + b1) / 2
                dk = _keep_dist(cfg, lx, ly)
                f = max(0.0, min(1.0, dk / max(1.0, R - hx)))
                lo = hn[0] + (hf[0] - hn[0]) * f
                hi = hn[1] + (hf[1] - hn[1]) * f
                h = rr.uniform(lo, hi)
                if rr.random() < cfg.get("tall_p", 0.08):
                    h *= rr.uniform(1.6, 2.2)
                ins = 0.25
                bx0, by0, bx1, by1 = a0 + ins, b0 + ins, a1 - ins, b1 - ins
                crown = rd.random() < 0.45                               # (drawn first: the occlusion rule needs the top;
                h2 = h + rd.uniform(4, 14) if crown else h               #  the rd stream order is unchanged)
                h, low_ = corridor_low(cfg, lx, ly, h)                   # rail-side sheds (Meridian v2 freight line)
                if low_:
                    crown, h2 = False, h
                bc(lx, ly, top=h2, hx=(bx1 - bx0) / 2, hy=(by1 - by0) / 2)
                col = (0.075, 0.07, 0.09) if rr.random() < 0.65 else (0.10, 0.085, 0.09)
                box(A["city"], bx0, by0, 0.16, bx1, by1, h, col, k=1.0 if rr.random() < 0.85 else 0.45)
                n_t += 1
                # faces on a street: the block's outer row of lots
                faces = []
                if i == 0:
                    faces.append(("x", bx0, -1))
                if i == nx_ - 1:
                    faces.append(("x", bx1, 1))
                if j == 0:
                    faces.append(("y", by0, -1))
                if j == ny_ - 1:
                    faces.append(("y", by1, 1))
                top = h
                if crown:                                                # a setback crown
                    s_ = min(bx1 - bx0, by1 - by0) * 0.18
                    box(A["city"], bx0 + s_, by0 + s_, h, bx1 - s_, by1 - s_, h2, col, k=0.6)
                    top = h2
                for (ax, v, sg) in faces:
                    _street_face(A, box, rd, ax, v, sg, (bx0, by0, bx1, by1), h, cfg, pal)
                # crown trim (lit runs) on the face looking at the compound
                if rd.random() < cfg.get("trim_p", 0.4):
                    c_ = SIGN_COLS[rd.randrange(len(SIGN_COLS))]
                    if abs(lx) > abs(ly):
                        xx = bx0 if lx > 0 else bx1
                        box(A["city_neon"], xx - 0.08, by0 + 0.4, top - 0.9, xx + 0.08, by1 - 0.4, top - 0.55, c_, 3.0)
                    else:
                        yy = by0 if ly > 0 else by1
                        box(A["city_neon"], bx0 + 0.4, yy - 0.08, top - 0.9, bx1 - 0.4, yy + 0.08, top - 0.55, c_, 3.0)
                # roof clutter
                for _ in range(rd.randint(1, 3)):
                    ux, uy = rd.uniform(bx0 + 1.5, bx1 - 1.5), rd.uniform(by0 + 1.5, by1 - 1.5)
                    box(A["city_metal"], ux - 0.9, uy - 0.6, top, ux + 0.9, uy + 0.6, top + 1.1, (0.16, 0.16, 0.17))
                if rd.random() < 0.35:                                   # a water tank on legs
                    ux, uy = rd.uniform(bx0 + 2, bx1 - 2), rd.uniform(by0 + 2, by1 - 2)
                    tube(A["city_metal"], (ux, uy, top + 1.6), (ux, uy, top + 4.2), 1.3, (0.13, 0.11, 0.1), n=8)
                    for (ex, ey) in ((-0.9, -0.9), (0.9, -0.9), (0.9, 0.9), (-0.9, 0.9)):
                        tube(A["city_metal"], (ux + ex, uy + ey, top), (ux + ex, uy + ey, top + 1.6), 0.08,
                             (0.1, 0.1, 0.1), n=4)
                if rd.random() < 0.3:                                    # antenna + red beacon
                    ux, uy = rd.uniform(bx0 + 1, bx1 - 1), rd.uniform(by0 + 1, by1 - 1)
                    ha = rd.uniform(5, 14)
                    tube(A["city_metal"], (ux, uy, top), (ux, uy, top + ha), 0.15, (0.12, 0.12, 0.13), n=4)
                    box(A["city_small"], ux - 0.35, uy - 0.35, top + ha, ux + 0.35, uy + 0.35, top + ha + 0.6, BEACON, 9.0)
                if rd.random() < cfg.get("holo_p", 0.06) and top > 30:      # a roof holo billboard facing the keep
                    c_ = SIGN_COLS[rd.randrange(len(SIGN_COLS))]
                    wbb = min(bx1 - bx0, by1 - by0) * 0.9
                    zb = top + 2.0
                    if abs(lx) > abs(ly):
                        xx = bx0 + 1.0 if lx > 0 else bx1 - 1.0
                        box(A["city_sign"], xx - 0.05, ly - wbb / 2, zb, xx + 0.05, ly + wbb / 2, zb + wbb * 0.45,
                            tuple(v * 0.55 for v in c_), 2.4)
                    else:
                        yy = by0 + 1.0 if ly > 0 else by1 - 1.0
                        box(A["city_sign"], lx - wbb / 2, yy - 0.05, zb, lx + wbb / 2, yy + 0.05, zb + wbb * 0.45,
                            tuple(v * 0.55 for v in c_), 2.4)
                    tube(A["city_metal"], (lx, ly, top), (lx, ly, zb), 0.2, (0.12, 0.12, 0.13), n=4)
                ROOFS.append((lx, ly, top, "down"))
            # street lamps round the block (on the sidewalk edge)
            bc(cx, cy, top=6.4, hx=bw / 2 + 1.5, hy=bw / 2 + 1.5)
            stp = cfg.get("lamp_step", 16.0)
            for (ax, v, sg) in (("x", x0 - 1.0, -1), ("x", x1 + 1.0, 1), ("y", y0 - 1.0, -1), ("y", y1 + 1.0, 1)):
                u = (y0 if ax == "x" else x0) + rd.uniform(2, 6)
                end = (y1 if ax == "x" else x1)
                while u < end - 1:
                    px, py = (v, u) if ax == "x" else (u, v)
                    if _keep_dist(cfg, px, py) > 2.0:
                        tube(A["city_metal"], (px, py, 0.16), (px, py, 6.2), 0.09, (0.1, 0.1, 0.11), n=4)
                        lc = (1.0, 0.62, 0.3) if rd.random() < 0.7 else (0.85, 0.92, 1.0)
                        hx_, hy_ = (px + sg * 0.9, py) if ax == "x" else (px, py + sg * 0.9)
                        box(A["city_small"], min(px, hx_) - 0.25, min(py, hy_) - 0.25, 6.0, max(px, hx_) + 0.25,
                            max(py, hy_) + 0.25, 6.3, lc, 14.0)
                        LAMPS.append((hx_ + sg * 1.5 if ax == "x" else hx_, hy_ + sg * 1.5 if ax == "y" else hy_, 6.0, lc))
                    u += stp
    bc(0.0, 0.0, False)
    _traffic(cfg, A, xs, ys, bw, st, R, hx, hy)
    return dict(roofs=ROOFS, lamps=LAMPS, n_towers=n_t)


def _street_face(A, box, rd, ax, v, sg, bb, h, cfg, pal):
    """Shop front + awning at the ground floor, AC units, blade signs on a street-facing facade."""
    bx0, by0, bx1, by1 = bb
    lo, hi = (by0, by1) if ax == "x" else (bx0, bx1)

    def B(acc, d0, d1, u0, u1, z0, z1, col, k=0.0):
        a, b = v + sg * d0, v + sg * d1
        if ax == "x":
            box(acc, min(a, b), u0, z0, max(a, b), u1, z1, col, k)
        else:
            box(acc, u0, min(a, b), z0, u1, max(a, b), z1, col, k)
    # shop front glow (the ground floor), an awning over it
    if rd.random() < 0.8:
        c = SHOP_COLS[rd.randrange(len(SHOP_COLS))]
        B(A["city_sign"], 0.02, 0.06, lo + 0.6, hi - 0.6, 0.5, 3.0, tuple(x * 0.8 for x in c), rd.uniform(1.2, 2.4))
        B(A["city_metal"], 0.0, 1.8, lo + 0.3, hi - 0.3, 3.2, 3.45, (0.14, 0.11, 0.11))
        if rd.random() < 0.5:                                           # a lit fascia band over the awning
            c2 = SIGN_COLS[rd.randrange(len(SIGN_COLS))]
            B(A["city_sign"], 0.02, 0.08, lo + 0.8, hi - 0.8, 3.6, 4.4, c2, 2.6)
    # AC units / boxes on the facade
    for _ in range(rd.randint(1, 4)):
        u = rd.uniform(lo + 0.6, hi - 1.8)
        z = rd.uniform(5.0, max(5.5, h * 0.8))
        B(A["city_metal"], 0.0, 0.8, u, u + 1.2, z, z + 0.9, (0.19, 0.19, 0.2))
    # blade signs: vertical, projecting from the facade (multilingual blades in the near field)
    if rd.random() < cfg.get("sign_p", 0.55):
        c = SIGN_COLS[rd.randrange(len(SIGN_COLS))]
        u = rd.choice((lo + 0.5, hi - 1.4)) if hi - lo > 3 else lo + 0.5
        z0 = rd.uniform(4.0, 7.0)
        z1 = min(h - 1.0, z0 + rd.uniform(6.0, 16.0))
        if z1 > z0 + 2.0:
            B(A["city_sign"], 0.3, 1.9, u, u + 0.35, z0, z1, c, rd.uniform(2.0, 4.0))
            B(A["city_metal"], 0.0, 0.3, u + 0.1, u + 0.25, z0 + 0.5, z0 + 0.8, (0.2, 0.2, 0.2))


def _traffic(cfg, A, xs, ys, bw, st, R, hx, hy):
    """Light streaks along the streets (the street centre lines between block rows; the compound street too)."""
    lr = random.Random(cfg["seed"] + 2)
    lines_x = sorted(set([round(x + bw + st / 2, 3) for x in xs] + [round(x - st / 2, 3) for x in xs]))
    lines_y = sorted(set([round(y + bw + st / 2, 3) for y in ys] + [round(y - st / 2, 3) for y in ys]))
    lines_x = [x for x in lines_x if abs(x) <= R][::2]
    lines_y = [y for y in lines_y if abs(y) <= R][::2]
    for ax, lines in (("x", lines_x), ("y", lines_y)):
        for c in lines:
            for side, dirn in ((-0.9, 1), (0.9, -1)):
                u = -R + lr.uniform(0, 30)
                while u < R:
                    L_ = lr.uniform(6, 18)
                    pa, pb = u, min(u + L_, R)
                    mid = (pa + pb) / 2
                    px, py = (c + side, mid) if ax == "x" else (mid, c + side)
                    if _keep_dist(cfg, px, py) > 1.0:
                        col = ((1.0, 0.92, 0.82) if lr.random() < 0.7 else (1.0, 0.72, 0.45)) if dirn > 0 else (1.0, 0.08, 0.05)
                        kk = lr.uniform(1.5, 3.5)
                        for s in range(4):
                            f0, f1 = s / 4, (s + 1) / 4
                            fall = (f1 if dirn > 0 else 1 - f0) ** 1.6
                            q0, q1 = pa + (pb - pa) * f0, pa + (pb - pa) * f1
                            if ax == "x":
                                box_ = (c + side - 0.07, q0, 0.5, c + side + 0.07, q1, 0.65)
                            else:
                                box_ = (q0, c + side - 0.07, 0.5, q1, c + side + 0.07, 0.65)
                            _raw_box(A["streaks"], box_, col, kk * (0.15 + 0.85 * fall))
                    u += L_ + lr.uniform(14, 60)


def _raw_box(acc, b, col, k):
    x0, y0, z0, x1, y1, z1 = b
    acc.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], col, k)
    acc.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], col, k)
    acc.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], col, k)


def section_params(pose_loc, cfg, rooms_pts=None, zref=None, margin=1.5):
    """The per-frame SECTION CUT (the storyboard's section, generalised to an orbiting camera; pure python).

    Every city building whose centre lies on the camera's side of the focus, inside a band round the sight line, is
    drawn only up to the camera's sight line to the focus' base:  z_cut = zref + slope * (s - s0) - margin, where s is
    the building's distance from the focus along the horizontal direction to the camera, slope = (camera z - zref) /
    (camera distance - s0). Below z_cut the building is whole (lit windows, shop fronts); above it is not drawn; its
    open top shows a dark poche. So the foreground lowers as the camera descends / closes in, and never covers a room.
      overview (rooms_pts None): focus = the compound centre, s0 = the keep's support toward the camera, band = the
                                 keep's lateral support + 30
      decision / hover         : focus = the centroid of the framed rooms, s0 = their support toward the camera,
                                 band = their lateral support + 24
    Returns a dict for the scene (scene custom properties sec_*)."""
    cx, cy, cz = pose_loc
    k = cfg["keep"]
    if rooms_pts:
        ox = sum(p[0] for p in rooms_pts) / len(rooms_pts)
        oy = sum(p[1] for p in rooms_pts) / len(rooms_pts)
    else:
        ox, oy = 0.0, 0.0
    dx, dy = cx - ox, cy - oy
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    if rooms_pts:
        s0 = max((p[0] - ox) * ux + (p[1] - oy) * uy for p in rooms_pts)
        w0 = max(abs(-(p[0] - ox) * uy + (p[1] - oy) * ux) for p in rooms_pts) + 24.0
        zr = min(p[2] for p in rooms_pts) if zref is None else zref
    else:
        if k[0] == "rect":
            s0 = k[1] * abs(ux) + k[2] * abs(uy)
            w0 = k[1] * abs(uy) + k[2] * abs(ux) + 30.0
        else:
            s0 = k[1]
            w0 = k[1] + 30.0
        zr = 0.0 if zref is None else zref
    slope = (cz - zr) / max(1.0, L - s0)
    if rooms_pts and zref is None:
        zr = zr * cfg.get("zref_k", 1.0)          # a lower sight line target: the near blocks cut lower (less poche)
    return dict(sec_on=1.0, sec_ox=ox, sec_oy=oy, sec_ux=ux, sec_uy=uy, sec_s0=s0, sec_w0=w0, sec_slope=slope,
                sec_zref=zr - margin, sec_widen=0.45, sec_plinth=0.6)


OCC = dict(margin=0.10, stub=6.4, ghost=0.18, edge=0.6, tsoft=0.035, vsoft=0.025)
NK = 5                  # depth knots of the cone (= section.NK)


def occlusion_params(cam, pts, cfg=None):
    """The OCCLUSION rule's per-frame cone (camera-rig rule; NOTES "Occlusion"). Pure python.

    cam  the camera position (x, y, z); pts the TARGET VOLUME: the active room + the visible route nodes (front points).
    Horizontal frame: u = the direction from the camera to the targets' centroid. For every target, the lateral tangent
    t = across / along and the vertical tangent v = (z - cam z) / along; the cone is [tmin, tmax] x [vmin, ..] widened
    by `margin` (10 %) of its span; amax = the farthest target's along (nothing beyond it can occlude).
    cfg (preset hq.downtown) may override the OCC numbers through cfg["occ"]. Returns the occ_* dict for section.py."""
    o = dict(OCC, **((cfg or {}).get("occ") or {}))
    cx, cy, cz = cam
    pts = [tuple(p) for p in pts]
    ox = sum(p[0] for p in pts) / len(pts)
    oy = sum(p[1] for p in pts) / len(pts)
    L = math.hypot(ox - cx, oy - cy) or 1.0
    ux, uy = (ox - cx) / L, (oy - cy) / L
    T, Vv, AL = [], [], []
    for (x, y, z) in pts:
        al = max((x - cx) * ux + (y - cy) * uy, 1.0)
        la = (y - cy) * ux - (x - cx) * uy
        T.append(la / al)
        Vv.append((z - cz) / al)
        AL.append(al)
    # the margin from the whole target volume's span (10 %), applied to every knot's sub-cone
    msp_t = o["margin"] * max(max(T) - min(T), 0.02)
    msp_v = o["margin"] * max(max(Vv) - min(Vv), 0.02)
    a0, a1 = min(AL), max(AL)
    out = dict(occ_on=1.0, occ_cx=cx, occ_cy=cy, occ_cz=cz, occ_ux=ux, occ_uy=uy, occ_tsoft=o["tsoft"], occ_a0=a0,
               occ_amax=a1, occ_vsoft=o["vsoft"], occ_stub=o["stub"], occ_ghost=o["ghost"], occ_edge=o["edge"])
    for k in range(NK):
        ak = a0 + (a1 - a0) * k / (NK - 1)
        sub = [j for j in range(len(AL)) if AL[j] >= ak - 1e-6] or [AL.index(a1)]
        out["occ_t%d" % k] = min(T[j] for j in sub) - msp_t
        out["occ_T%d" % k] = max(T[j] for j in sub) + msp_t
        out["occ_v%d" % k] = min(Vv[j] for j in sub) - msp_v
    return out


def _knot(p, key, a):
    f = (a - p["occ_a0"]) / max(p["occ_amax"] - p["occ_a0"], 1.0) * (NK - 1)
    f = max(0.0, min(NK - 1.0, f))
    v = p["occ_%s0" % key]
    for k in range(1, NK):
        v += max(0.0, min(1.0, f - (k - 1))) * (p["occ_%s%d" % (key, k)] - p["occ_%s%d" % (key, k - 1)])
    return v


def _sstep(x, w):
    t = max(0.0, min(1.0, x / max(w, 1e-4)))
    return t * t * (3 - 2 * t)


def occlusion_state(p, b):
    """The rule's OUTPUT for one building b = (x, y, top, hx, hy): (cut height, opacity). The exact twin of the
    section.py shader (and of the Godot per-instance values): cut height = top (+ roof clutter) outside the cone, the
    stub inside; opacity = 1, or `ghost` when the stub still reaches into the cone."""
    x, y, top, hx, hy = b
    r = max(math.hypot(hx, hy), 0.5)
    dx, dy = x - p["occ_cx"], y - p["occ_cy"]
    al = dx * p["occ_ux"] + dy * p["occ_uy"]
    la = dy * p["occ_ux"] - dx * p["occ_uy"]
    alc = max(al, 1.0)
    tmin, tmax, vmin = _knot(p, "t", al - r), _knot(p, "T", al - r), _knot(p, "v", al - r)
    lat = _sstep((la + r) / alc - tmin, p["occ_tsoft"]) * _sstep(tmax - (la - r) / alc, p["occ_tsoft"])
    front = (1.0 if al > 0 else 0.0) * _sstep(p["occ_amax"] - (al - r), 6.0)

    def blocks(z):
        return _sstep((z - p["occ_cz"]) / max(al + r, 1.0) - vmin, p["occ_vsoft"])
    fc = p["occ_on"] * lat * front * blocks(top)
    stub = min(p["occ_stub"], top)
    zc = stub + (1.0 - fc) * (top + 25.0 - stub)
    g = fc * blocks(stub)
    return min(zc, top), 1.0 - g * (1.0 - p["occ_ghost"])


def in_corridor(cfg, x0, y0, x1, y1):
    """True if the rectangle x0..x1, y0..y1 meets a corridor segment (cfg["corridor"]: [(ax, ay, bx, by, half)])."""
    import math as _m
    for (ax, ay, bx, by, hw) in cfg.get("corridor", ()):
        # the distance from the segment to the rectangle, sampled along the segment
        L = _m.hypot(bx - ax, by - ay) or 1.0
        n = int(L / 2.0) + 1
        for k in range(n + 1):
            px, py = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            dx = max(x0 - px, 0.0, px - x1)
            dy = max(y0 - py, 0.0, py - y1)
            if _m.hypot(dx, dy) < hw:
                return True
    return False


def corridor_dist(cfg, x, y):
    """The distance from (x, y) to the nearest corridor axis (inf without corridors)."""
    import math as _m
    best = float("inf")
    for (ax, ay, bx, by, hw) in cfg.get("corridor", ()):
        vx, vy = bx - ax, by - ay
        L2 = vx * vx + vy * vy or 1.0
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
        best = min(best, _m.hypot(x - ax - vx * t, y - ay - vy * t))
    return best


def corridor_low(cfg, x, y, h):
    """cfg["corridor_low"] = (dist, hmax): within dist of a corridor axis the city is low rail-side sheds / warehouses
    (height capped at hmax with a deterministic spread), so an elevated viaduct reads above them. -> (h, capped)"""
    cl = cfg.get("corridor_low")
    if not cl or corridor_dist(cfg, x, y) > cl[0]:
        return h, False
    cap = cl[1]
    if len(cl) >= 7:                      # the cap follows a deck on a grade (Meridian: 3 %, 2 storeys of clearance)
        import math as _m
        ax, ay, bx, by, _hw = cfg["corridor"][0]
        L = _m.hypot(bx - ax, by - ay) or 1.0
        s = ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / L
        deck = min(cl[4], max(0.0, (s - cl[2]) * cl[3]))
        cap = max(cl[6], min(cl[1], deck - cl[5]))
    return min(h, cap * (0.7 + 0.3 * ((h * 7.31) % 1.0))), True
