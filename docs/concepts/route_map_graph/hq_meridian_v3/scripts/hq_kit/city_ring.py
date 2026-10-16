"""hq_kit.city_ring: the procedural 360 degree city round an HQ (Blender-side geometry through injected helpers).

    from hq_kit import city_ring
    roofs = city_ring.build(city_cfg, road_cfg, look_preset, acc, geo, pal)
    beams = city_ring.beams_by_azimuth(roofs, city_cfg, look_preset, pal)     # [(origin, dir, colour, power, cone)]
    glows = city_ring.glows_by_azimuth(n=8, radii=(430, 700))                 # [(x, y, which)]

acc: accumulators with .face(points, colour, k) under the keys city, city_neon, city_sign, city_small, city_metal,
     streaks, sky.  geo: box(acc, x0, y0, z0, x1, y1, z1, col, k), fbox(acc, f, d0, d1, u0, u1, z0, z1, col, k),
     fp(f, d, u, z), tube(acc, p0, p1, r, col, k, n).  pal(name) -> colour.
city_cfg keys: seed, rings [{name, r (inner, outer half-size), h, w, neon_p, win_p, far, signs}], billboards,
     beam_sectors, beam_ring, sky_lanes [(half-size, z)], win_p.  road_cfg: plaza, road (inner, outer), walk.
Rules (square annuli = a city grid, so every orbit angle has a near / mid / far layer):
  towers      one seeded tower per grid cell (cell = the ring's max width + 6), 12 % empty
  crown trim  the inward half of the crown only, broken into lit runs (the r3 skyline rule)
  signs       blade signs on the face looking at the compound (signage LOD); near ring: shop fronts, awnings, AC units
  beacons     red roof beacons (small-lights LOD)
  billboards  one per azimuth sector on the mid ring, facing in
  traffic     light streaks only, on the four sides of the ring road (inner lanes white / warm, outer red); sky lanes
              on square loops
  beams       the tallest beam_ring roof per 45 degree sector, leaning radially out, district colours alternating
Seeds: city_cfg seed (towers, billboards), 9402 (lanes), 9500 (beams).
"""
import math
import random

BEACON = (1.0, 0.06, 0.04)


def inward_face(cx, cy):
    """The face of a tower at (cx, cy) that looks at the compound (N[f] points to the centre)."""
    if abs(cx) >= abs(cy):
        return 1 if cx < 0 else 3
    return 2 if cy < 0 else 0


def build(city, road, P, A, geo, pal):
    box, fbox, fp, tube = geo.box, geo.fbox, geo.fp, geo.tube
    bcf = getattr(geo, "bc", None)            # v2: the section clip's building centre (whole towers are cut)
    bct = getattr(geo, "bc_top", None)        # v3: the occlusion rule's building top (set once the crown is known)
    NEON = [pal("district_a"), pal("district_b"), pal("accent_cool"), pal("district_a"), pal("district_b"),
            pal("accent_warm")]
    ROOF = []
    rr = random.Random(city["seed"])

    def tower(cx, cy, w, d, h, ring):
        if bcf:
            bcf(cx, cy, top=h, hx=w / 2, hy=d / 2)
        col = (0.075, 0.07, 0.09) if rr.random() < 0.7 else (0.10, 0.085, 0.09)
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        box(A["city"], x0, y0, 0, x1, y1, h, col, k=1.0 if rr.random() < 0.85 else 0.4)
        fin = inward_face(cx, cy)
        far = ring["far"]
        if rr.random() < 0.55:
            ins = min(w, d) * 0.18
            h2 = h + rr.uniform(6, 18)
            box(A["city"], x0 + ins, y0 + ins, h, x1 - ins, y1 - ins, h2, col, k=0.6)
            if rr.random() < ring["neon_p"]:
                c = NEON[rr.randrange(len(NEON))]
                half = (w if fin in (0, 2) else d) / 2 - ins
                dist = (d if fin in (0, 2) else w) / 2 - ins
                u = -half
                while u < half - 0.5:
                    run = rr.uniform(2.0, 6.0)
                    if rr.random() < 0.55:
                        a = fp(fin, dist + 0.05, u, h2 - 0.9)
                        b = fp(fin, dist + 0.15, min(u + run, half), h2 - 0.6)
                        box(A["city_neon"], a[0] + cx, a[1] + cy, h2 - 0.9, b[0] + cx, b[1] + cy, h2 - 0.6, c, 4.0 * far)
                    u += run + rr.uniform(0.5, 2.0)
            h = h2
        if rr.random() < 0.5:
            tube(A["city_metal"], (cx, cy, h), (cx, cy, h + rr.uniform(8, 22)), 0.25, (0.1, 0.1, 0.12), n=5)
            box(A["city_small"], cx - 0.5, cy - 0.5, h + 8, cx + 0.5, cy + 0.5, h + 9, BEACON, 10.0)
        if ring["signs"]:
            half = (w if fin in (0, 2) else d) / 2
            dist = (d if fin in (0, 2) else w) / 2
            if rr.random() < 0.35 * ring["neon_p"] / 0.45:
                c = NEON[rr.randrange(len(NEON))]
                u = rr.uniform(-half + 1, half - 2)
                z = rr.uniform(h * 0.3, h * 0.7)
                a = fp(fin, dist + 0.2, u, z)
                b = fp(fin, dist + 0.6, u + 1.4, z + rr.uniform(10, 22))
                box(A["city_sign"], a[0] + cx, a[1] + cy, z, b[0] + cx, b[1] + cy, b[2], c, 5.0 * far)
            if ring["name"] == "near":
                c = [(1.0, 0.55, 0.2), pal("district_a"), pal("district_b"), (1.0, 0.7, 0.35)][rr.randrange(4)]
                pts = [fp(fin, dist + 0.05, -half + 1.0, 0.4), fp(fin, dist + 0.05, half - 1.0, 0.4),
                       fp(fin, dist + 0.05, half - 1.0, 3.4), fp(fin, dist + 0.05, -half + 1.0, 3.4)]
                A["city_sign"].face([(p[0] + cx, p[1] + cy, p[2]) for p in pts], tuple(v * 0.7 for v in c), 2.2)
                a = fp(fin, dist, -half + 0.6, 3.6)
                b = fp(fin, dist + 2.4, half - 0.6, 3.9)
                box(A["city_metal"], a[0] + cx, a[1] + cy, 3.6, b[0] + cx, b[1] + cy, 3.9, (0.15, 0.12, 0.12))
                for _ in range(rr.randint(2, 5)):
                    u = rr.uniform(-half + 1, half - 2)
                    z = rr.uniform(6, h * 0.8)
                    a = fp(fin, dist, u, z)
                    b = fp(fin, dist + 0.9, u + 1.4, z + 1.0)
                    box(A["city_metal"], a[0] + cx, a[1] + cy, z, b[0] + cx, b[1] + cy, z + 1.0, (0.2, 0.2, 0.21))
        if bct:
            bct(h)
        ROOF.append((cx, cy, h, ring["name"]))

    for ring in city["rings"]:
        a, b = ring["r"]
        cell = (ring["w"][1] + 6.0)
        n = int(math.ceil(b / cell))
        for gx in range(-n, n):
            for gy in range(-n, n):
                cx = (gx + 0.5) * cell
                cy = (gy + 0.5) * cell
                m = max(abs(cx), abs(cy))
                if m < a or m > b:
                    rr.random()
                    continue
                w = rr.uniform(*ring["w"])
                d = rr.uniform(*ring["w"])
                h = rr.uniform(*ring["h"])
                if rr.random() < 0.12:
                    continue
                ww_, dd_ = min(w, cell - 4) / 2 + 2, min(d, cell - 4) / 2 + 2
                if in_corridor(city, cx - ww_, cy - dd_, cx + ww_, cy + dd_):
                    continue
                h = corridor_low(city, cx, cy, h)[0]                     # rail-side sheds (Meridian v2 freight line)
                tower(cx + rr.uniform(-2, 2), cy + rr.uniform(-2, 2), min(w, cell - 4), min(d, cell - 4), h, ring)
    mid = next(rg for rg in city["rings"] if rg["name"] == city.get("beam_ring", "mid"))
    for k_ in range(city["billboards"]):
        az = 2 * math.pi * (k_ + 0.5) / city["billboards"]
        rad = mid["r"][0] - 6
        cx, cy = rad * math.sin(az), -rad * math.cos(az)
        fin = inward_face(cx, cy)
        c = NEON[k_ % 2]
        bz = rr.uniform(46, 80)
        if bcf:
            bcf(cx, cy, top=bz + 9.0, hx=14.0, hy=14.0)
        pts = [fp(fin, 0.0, -14, bz), fp(fin, 0.0, 14, bz), fp(fin, 0.0, 14, bz + 9), fp(fin, 0.0, -14, bz + 9)]
        A["city_sign"].face([(p[0] + cx, p[1] + cy, p[2]) for p in pts], tuple(v * 0.8 for v in c), 1.6)
        for l_ in range(4):
            L_ = rr.uniform(8, 22)
            pts = [fp(fin, 0.1, -12, bz + 1.2 + l_ * 1.8), fp(fin, 0.1, -12 + L_, bz + 1.2 + l_ * 1.8),
                   fp(fin, 0.1, -12 + L_, bz + 1.8 + l_ * 1.8), fp(fin, 0.1, -12, bz + 1.8 + l_ * 1.8)]
            A["city_sign"].face([(p[0] + cx, p[1] + cy, p[2]) for p in pts], (1, 1, 1), 2.0)
        tube(A["city_metal"], (cx, cy, 0), (cx, cy, bz), 0.8, (0.12, 0.12, 0.14), n=6)
    if bcf:
        bcf(0.0, 0.0, False)
    # traffic: light streaks on the four sides of the ring road, sky lanes on square loops
    SLp = P["street_lanes"]
    lr = random.Random(9402)
    R0, R1 = road["road"]
    half_r = (R1 - R0) / 2
    lanes = [(R0 + half_r * fr, +1) for fr in SLp["fractions_near"]] + [(R1 - half_r * fr, -1) for fr in SLp["fractions_far"]]
    for f in range(4):
        for (dl, dirn) in lanes:
            u = -R1 + lr.uniform(0, 30)
            while u < R1:
                L_ = lr.uniform(*SLp["len"])
                c = ((1.0, 0.92, 0.82) if lr.random() < 0.7 else (1.0, 0.72, 0.45)) if dirn > 0 else (1.0, 0.08, 0.05)
                kk = lr.uniform(2.0, 4.5)
                z0_ = 0.55 + lr.uniform(-0.1, 0.15)
                for s in range(6):
                    f0, f1 = s / 6, (s + 1) / 6
                    fall = (f1 if dirn > 0 else 1 - f0) ** 1.6
                    fbox(A["streaks"], f, dl - 0.08, dl + 0.08, u + L_ * f0, min(u + L_ * f1, R1), z0_, z0_ + 0.16, c,
                         kk * (0.15 + 0.85 * fall))
                u += L_ + lr.uniform(*SLp["gap"])
    for (rad, zz) in city["sky_lanes"]:
        for f in range(4):
            u = -rad + lr.uniform(0, 80)
            while u < rad:
                L_ = lr.uniform(10, 30)
                c = (1.0, 0.9, 0.8) if lr.random() < 0.6 else (1.0, 0.1, 0.06)
                for s in range(5):
                    f0, f1 = s / 5, (s + 1) / 5
                    fbox(A["sky"], f, rad - 0.15, rad + 0.15, u + L_ * f0, u + L_ * f1, zz, zz + 0.35, c, 4.0 * f1 ** 2)
                u += L_ + lr.uniform(80, 200)
    return ROOF


def beams_by_azimuth(roofs, city, P, pal, power_k=1.0):
    """The tallest beam_ring roof per sector gets a beam leaning radially out; colours alternate by sector."""
    BB = P["beams"]
    br_ = random.Random(9500)
    nsec = city["beam_sectors"]
    out = []
    for k_ in range(nsec):
        a0, a1 = 2 * math.pi * k_ / nsec, 2 * math.pi * (k_ + 1) / nsec
        cands = [r_ for r_ in roofs if r_[3] == city["beam_ring"] and a0 <= (math.atan2(r_[0], -r_[1]) % (2 * math.pi)) < a1]
        if not cands:
            continue
        cx, cy, h, _ = max(cands, key=lambda r_: (r_[2], r_[0], r_[1]))
        rad = math.hypot(cx, cy)
        c = pal(["district_a", "district_b", "accent_warm", "accent_cool"][k_ % 4 if k_ % 2 else (k_ // 2) % 2])
        lean = br_.uniform(*BB["lean"])
        out.append(((cx, cy, h + 1.0), (cx / rad * lean, cy / rad * lean, 1.0), c,
                    BB["thin"][1] * BB["power_k"] * 0.6 * power_k, BB["thin"][0]))
    return out


def glows_by_azimuth(n=8, radii=(430.0, 700.0)):
    """City glow positions under the fog: n sectors, alternating radius and district (a / b)."""
    out = []
    for k_ in range(n):
        az = 2 * math.pi * (k_ + 0.5) / n
        rad = radii[k_ % 2]
        out.append((rad * math.sin(az), -rad * math.cos(az), "district_a" if k_ % 2 == 0 else "district_b"))
    return out


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
