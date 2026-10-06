"""Round 36: THE one city model (Blender 5.2 headless). City Grid, raid and netrun transit are cameras on it.

blender -b --factory-startup --python unified36.py -- meridian_hq <outdir> <camsfile.json>
  camsfile: [{"tag": name, "t": [lot_x, lot_y], "ortho": BU, "res": [w, h]}, ...]   (layout36.cam convention)
Per cam: <tag>_beauty_night.png, _glow_night.png, _normal.png, _id.png, _pos.npy, _scene.json

Built on the round 25-30 HQ pipeline (hq_scene.py): target_corps.py primitives + materials, heroes24-30 (the five
locked HQs: Meridian container fortress with crane + rail yard, Solace helix, Halcyon civic core, Orbital silo, the
Cell's base) and the game's own city layout (../scratch/layout/unified.json from layout36.py: every street tile with
its lane colours, every building extrusion). Round 36 adds the raid-level detail to EVERY city building (it is one
model: small things simply stop resolving at the city zoom), the uplink pads + risers on the Cell's node buildings,
the round 34 red windows in the Cell's crest, holo billboards and the round 26 sky-lane traffic.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials

import json
import numpy as np

sys.path.insert(0, _HERE)
import layout36 as LY36

_argv = sys.argv[sys.argv.index("--") + 1:]
JOB, OUTDIR, CAMS = _argv[0], _argv[1], json.load(open(_argv[2]))
CORP, KIND = "meridian", "hq"
VIEW, STATE = "close", ""
os.makedirs(OUTDIR, exist_ok=True)
rng = random.Random(3636)
LAY = json.load(open(os.path.join(_HERE, "..", "scratch", "layout", "unified.json")))
NET = LY36.load_net()
CX, CY = LAY["centre"]
U = LY36.U
KH = U / 41.64 * 1.15          # game height px -> BU (a touch taller than round 25: the real skyline is spiky)


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
LIME = (0.83, 1.0, 0.0)
PLAZA_R = 27.5
exec(open(os.path.join(_HERE, "heroes24.py"), encoding="utf-8-sig").read())
KN = CORP_KNOBS[CORP]
exec("\n".join(_SRC[504:682]))  # container(), ziggurat(), depot()
for _h in ("heroes25.py", "heroes26.py", "heroes27.py", "heroes28.py", "heroes29.py", "heroes30.py"):
    exec(open(os.path.join(_HERE, _h), encoding="utf-8-sig").read())

# ------------------------------------------------------------------ the city: the game's layout + raid-level detail
CITY = Acc("city")
CNEON = Acc("cneon")
GLANE = Acc("glane")         # round 37: street-level glow (lanes, trails, car lights) - kept in the ground-only pass
CWIN = Acc("cwin")
GROUND = Acc("ground")
FAMS_C = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
TERR = LAY["terr"]
CAMDIR = (0.7071, -0.7071)    # horizontal direction from the scene toward the camera (yaw 135)
FIST = [(W(a), W(b)) for a, b in NET.get("fist", [])]
SIGNC = [(1.0, 0.3, 0.65), (0.3, 0.85, 1.0), (1.0, 0.62, 0.15), (0.75, 0.45, 1.0), (0.4, 1.0, 0.6), (1.0, 0.25, 0.25)]
CREST_RED = (0.95, 0.24, 0.22)
ANTS = []                    # round 37: aircraft-light positions (they blink in post)
BUILT = []                    # (centre, footprint quad, top z, terr) for the node props


def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def seg_d(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t))


def in_crest(p):
    return any(seg_d(p, a, b) < 1.9 * U for a, b in FIST)


def fgrid(A, B, C, D, col, bid, r, cell=1.7):
    """Quad split into a jittered grid of triangles (edges kept straight, so the ink stays clean)."""
    A, B, C, D = map(Vector, (A, B, C, D))
    n = (B - A).cross(D - A)
    if n.length < 1e-6:
        return
    n.normalize()
    nu = max(2, min(12, int(round((B - A).length / cell))))
    nv = max(2, min(30, int(round((D - A).length / cell))))
    grid = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            p = A.lerp(B, u).lerp(D.lerp(C, u), v)
            if 0 < i < nu and 0 < j < nv:
                p = p + (B - A) / nu * r.uniform(-0.28, 0.28) + (D - A) / nv * r.uniform(-0.28, 0.28) + n * r.uniform(-0.12, 0.12)
            row.append(tuple(p))
        grid.append(row)
    patch = r.random()
    for j in range(nv):
        for i in range(nu):
            p00, p10, p11, p01 = grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]
            f1 = 0.5 + (patch - 0.5) * 0.6 + r.uniform(-0.4, 0.4)
            f2 = 0.5 + (patch - 0.5) * 0.6 + r.uniform(-0.4, 0.4)
            if (i + j) % 2 == 0:
                CITY.face([p00, p10, p11], col, bid, fj=f1)
                CITY.face([p00, p11, p01], col, bid, fj=f2)
            else:
                CITY.face([p00, p10, p01], col, bid, fj=f1)
                CITY.face([p10, p11, p01], col, bid, fj=f2)


def city_building(b):
    r = random.Random(b["key"] * 7 + 13)
    q = [W(p) for p in b["q"]]
    n = len(q)
    z0, h = b["z0"] * KH, b["h"] * KH
    ts = b["ts"]
    cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
    top = [(cxq + (x - cxq) * ts, cyq + (y - cyq) * ts) for (x, y) in q]
    fam = FAMS_C[abs(b["key"]) % len(FAMS_C)]
    tc = TERR.get(b["terr"], (0.8, 0.8, 0.8))
    col = mixc(fam, tc, 0.28 if b["terr"] else 0.0)
    crest = in_crest((cxq, cyq))
    bid = rid()
    wp = 0.3 if not crest else 0.6
    for i in range(n):
        j = (i + 1) % n
        a, c = q[i], q[j]
        quad = [(a[0], a[1], z0), (c[0], c[1], z0), (top[j][0], top[j][1], z0 + h), (top[i][0], top[i][1], z0 + h)]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        ux, uy = (c[0] - a[0]) / (L or 1), (c[1] - a[1]) / (L or 1)
        nx, ny = uy, -ux
        if nx * (a[0] - cxq) + ny * (a[1] - cyq) < 0:
            nx, ny = -nx, -ny
        seen = nx * CAMDIR[0] + ny * CAMDIR[1] > 0.1
        if seen and L > 2.0 and h > 3.0:
            fgrid(*quad, col, bid, r)          # the raid-level triangulated facade (round 19 ~2.6 m cells)
        else:
            CITY.facet_quad(*quad, col, bid)
        if L < 1.2 or ts < 0.99:
            continue
        if seen and h > 6.0 and r.random() < 0.12:   # a drain pipe down the facade
            t0 = r.uniform(0.3, L - 0.3)
            px_, py_ = a[0] + ux * t0 + nx * 0.12, a[1] + uy * t0 + ny * 0.12
            beam((px_, py_, z0), (px_, py_, z0 + h - 0.2), 0.14, (0.22, 0.22, 0.26))
        # window grid (crest: red, denser - the round 34 locked fist of red lights)
        if h > 2.4:
            nxw, nzw = int((L - 0.6) / 1.6), int((h - 1.6) / 1.9)
            for u in range(nxw):
                for v in range(nzw):
                    if r.random() > wp:
                        continue
                    t0 = 0.3 + u * 1.6 + 0.4
                    z = z0 + 1.6 + v * 1.9
                    wc = CREST_RED if crest and r.random() < 0.8 else r.choice(WIN_COLS)
                    s = 0.5 + 0.5 * r.random()
                    p0 = (a[0] + ux * t0 + nx * 0.05, a[1] + uy * t0 + ny * 0.05)
                    p1 = (p0[0] + ux * 0.8, p0[1] + uy * 0.8)
                    CWIN.face([(p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z + 0.7), (p0[0], p0[1], z + 0.7)],
                              tuple(x * s for x in wc), (0, 0, 0))
        if not seen or z0 > 0.5:
            continue
        # street level on the faces the camera sees: a lit shopfront band, sometimes an awning
        if L > 2.5 and h > 2.0 and r.random() < 0.55:
            m0, m1 = 0.4, L - 0.4
            p0 = (a[0] + ux * m0 + nx * 0.06, a[1] + uy * m0 + ny * 0.06)
            p1 = (a[0] + ux * m1 + nx * 0.06, a[1] + uy * m1 + ny * 0.06)
            sc = r.choice([(1.0, 0.75, 0.45), (1.0, 0.5, 0.8), (0.5, 0.9, 1.0), (1.0, 0.85, 0.6)])
            CWIN.face([(p0[0], p0[1], 0.15), (p1[0], p1[1], 0.15), (p1[0], p1[1], 1.05), (p0[0], p0[1], 1.05)], tuple(v * 0.8 for v in sc), (0, 0, 0))
            if r.random() < 0.4:
                aw = r.choice([(0.25, 0.55, 0.45), (0.6, 0.22, 0.3), (0.3, 0.3, 0.5), (0.55, 0.42, 0.2)])
                e0 = (p0[0] + nx * 0.7, p0[1] + ny * 0.7)
                e1 = (p1[0] + nx * 0.7, p1[1] + ny * 0.7)
                CITY.face([(p0[0], p0[1], 1.45), (p1[0], p1[1], 1.45), (e1[0], e1[1], 1.2), (e0[0], e0[1], 1.2)], aw, bid)
        # ledges every few floors (catch the ink: reads as floors at raid / transit zoom)
        if h > 7.0:
            k = 1
            while 3.0 * k < h - 1.0:
                zl = z0 + 3.0 * k + 0.9
                beam((a[0] + nx * 0.12, a[1] + ny * 0.12, zl), (c[0] + nx * 0.12, c[1] + ny * 0.12, zl), 0.16, tuple(v * 0.8 for v in col))
                k += 2
        # a blade sign (vertical neon) on some street faces
        if h > 5.0 and L > 2.0 and r.random() < 0.16:
            sc = r.choice(SIGNC)
            t0 = r.uniform(0.6, L - 0.6)
            bx, by = a[0] + ux * t0 + nx * 0.5, a[1] + uy * t0 + ny * 0.5
            zb = r.uniform(1.6, max(2.0, min(h - 2.6, 7.0)))
            beam((bx, by, zb), (bx, by, zb + r.uniform(1.6, 3.2)), 0.36, sc, acc=CNEON)
    CITY.face([(x, y, z0 + h) for (x, y) in top], tuple(min(1, v * 1.08) for v in col), bid)
    zt = z0 + h
    if r.random() < 0.42 and ts > 0.05:          # the game's neon roof trim, in the building's own ink
        for i in range(n):
            j = (i + 1) % n
            beam((top[i][0], top[i][1], zt + 0.08), (top[j][0], top[j][1], zt + 0.08), 0.22, tuple(b["ink"]), acc=CNEON)
    if ts >= 0.99:
        xs, ys = [p[0] for p in top], [p[1] for p in top]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        if x1 - x0 > 2.0 and y1 - y0 > 2.0:
            for _ in range(r.randint(0, 2)):        # AC units / vents
                vx, vy = r.uniform(x0 + 0.4, x1 - 1.3), r.uniform(y0 + 0.4, y1 - 1.1)
                box(vx, vy, zt, vx + 0.9, vy + 0.7, zt + 0.55, (0.34, 0.34, 0.38), facet=False)
            if r.random() < 0.18:                    # water tank on legs
                tx, ty = r.uniform(x0 + 1.0, x1 - 1.0), r.uniform(y0 + 1.0, y1 - 1.0)
                for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
                    beam((tx + dx, ty + dy, zt), (tx + dx, ty + dy, zt + 0.9), 0.12, (0.2, 0.2, 0.24))
                cyl36(tx, ty, zt + 0.9, zt + 2.1, 0.8, (0.45, 0.38, 0.32))
            if h > 22 and r.random() < 0.45:         # antenna with a red aircraft light
                ax, ay = (x0 + x1) / 2, (y0 + y1) / 2
                hh = r.uniform(3, 7)
                beam((ax, ay, zt), (ax, ay, zt + hh), 0.18, (0.25, 0.25, 0.3))
                CNEON.face([(ax - 0.3, ay, zt + hh), (ax + 0.3, ay, zt + hh), (ax + 0.3, ay, zt + hh + 0.5), (ax - 0.3, ay, zt + hh + 0.5)], RED, (0, 0, 0))
                ANTS.append((ax, ay, zt + hh + 0.25))
            if h > 14 and r.random() < 0.16:         # holo billboard (round 26): a lit panel standing on the roof
                hc = r.choice([(1.0, 0.3, 0.7), (0.3, 0.9, 1.0), (0.7, 0.45, 1.0), (1.0, 0.65, 0.2)])
                bx, by = (x0 + x1) / 2, (y0 + y1) / 2
                wv = r.uniform(4.0, 7.5)
                hv = wv * 0.6
                ex, ey = -0.7071 * wv / 2, -0.7071 * wv / 2      # panel faces the camera (normal +x -y)
                zb = zt + 1.0
                beam((bx, by, zt), (bx, by, zb), 0.2, (0.2, 0.2, 0.24))
                CNEON.face([(bx + ex, by - ey, zb), (bx - ex, by + ey, zb), (bx - ex, by + ey, zb + hv), (bx + ex, by - ey, zb + hv)],
                           tuple(v * 0.75 for v in hc), (0, 0, 0))
    BUILT.append(((cxq, cyq), q, z0 + h, b["terr"], ts, b["key"]))


def cyl36(cx, cy, z0, z1, rad, col, n=8):
    bid = rid()
    pts = [(cx + rad * math.cos(2 * math.pi * k / n), cy + rad * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        a, c = pts[k], pts[(k + 1) % n]
        SOLID.face([(a[0], a[1], z0), (c[0], c[1], z0), (c[0], c[1], z1), (a[0], a[1], z1)], col, bid)
    SOLID.face([(p[0], p[1], z1) for p in pts], col, bid)


for b in LAY["buildings"]:
    city_building(b)
print("BUILDINGS", len(BUILT), "faces", len(CITY.bm.faces), flush=True)

# ground: asphalt, plazas, the game's street tiles + glowing lanes (round 6 restyler rules, in lots)
GROUND.face([(-3000, -3000, -0.02), (3000, -3000, -0.02), (3000, 3000, -0.02), (-3000, 3000, -0.02)], (0.20, 0.20, 0.25), (0, 0, 0))
for pz in LAY["plazas"]:
    q = [W(p) for p in pz["q"]]
    tc = TERR.get(pz["terr"], (0.8, 0.8, 0.8))
    GROUND.face([(x, y, 0.005) for (x, y) in q], mixc((0.26, 0.25, 0.30), tc, 0.12), (0, 0, 0))
for t in LAY["tiles"]:
    q = [W(p) for p in t["q"]]
    GROUND.face([(x, y, 0.01) for (x, y) in q], (0.13, 0.13, 0.16), (0, 0, 0))
    if not t["ab"] or not t["col"]:
        continue
    a, b = W(t["ab"][0]), W(t["ab"][1])
    col, tr = tuple(t["col"]), t["tr"]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -dy, dx
    strokes = 7 + int(tr * 23)
    half = (1.5 + strokes * 0.42) / 38.0 * U
    strip(GLANE, (a[0] - dx * 0.3, a[1] - dy * 0.3), (b[0] + dx * 0.3, b[1] + dy * 0.3), 2 * (half + 0.5), 0.02,
          tuple(v * (0.10 + tr * 0.16) for v in col))
    nl = min(strokes, 3 + int(tr * 9))
    hr = random.Random(t["i"] * 7919 + t["j"])
    for k in range(nl):
        u = (k + 0.5) / nl * 2 - 1
        lane = u * half * 0.8 + (hr.random() - 0.5) * 0.25
        al = 0.55 + 0.35 * hr.random() + tr * 0.15
        strip(GLANE, (a[0] + nx * lane - dx * 0.35, a[1] + ny * lane - dy * 0.35), (b[0] + nx * lane + dx * 0.35, b[1] + ny * lane + dy * 0.35),
              0.18, 0.04, tuple(min(1, v * al) for v in col))
for t in LAY["trails"]:
    a, b = W(t["a"]), W(t["b"])
    strip(GLANE, a, b, 0.32, 0.06, tuple(t["col"]))
# street traffic: cars on the lanes (head / tail lights) - only resolves from the raid zoom in
CARS = random.Random(1936)
for t in LAY["tiles"]:
    if not t["ab"] or CARS.random() > 0.08 + 0.25 * t["tr"]:
        continue
    a, b = W(t["ab"][0]), W(t["ab"][1])
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -dy, dx
    sd = CARS.choice((-1, 1))
    u = CARS.uniform(0.2, 0.8)
    x, y = a[0] + (b[0] - a[0]) * u + nx * sd * 1.1, a[1] + (b[1] - a[1]) * u + ny * sd * 1.1
    fw = (dx * sd, dy * sd)
    cc = CARS.choice([(0.35, 0.33, 0.4), (0.5, 0.2, 0.2), (0.25, 0.3, 0.45), (0.6, 0.6, 0.62)])
    hl, hw = 0.85, 0.42
    pts = [(x + fw[0] * hl - nx * hw, y + fw[1] * hl - ny * hw), (x + fw[0] * hl + nx * hw, y + fw[1] * hl + ny * hw),
           (x - fw[0] * hl + nx * hw, y - fw[1] * hl + ny * hw), (x - fw[0] * hl - nx * hw, y - fw[1] * hl - ny * hw)]
    bid = rid()
    for k in range(4):
        p0, p1 = pts[k], pts[(k + 1) % 4]
        SOLID.face([(p0[0], p0[1], 0.1), (p1[0], p1[1], 0.1), (p1[0], p1[1], 0.55), (p0[0], p0[1], 0.55)], cc, bid)
    SOLID.face([(p[0], p[1], 0.55) for p in pts], tuple(v * 1.2 for v in cc), bid)
    strip(GLANE, (x + fw[0] * hl, y + fw[1] * hl), (x + fw[0] * (hl + 0.15), y + fw[1] * (hl + 0.15)), 0.8, 0.35, (1.0, 0.95, 0.8))
    strip(GLANE, (x - fw[0] * hl, y - fw[1] * hl), (x - fw[0] * (hl + 0.1), y - fw[1] * (hl + 0.1)), 0.8, 0.35, RED)

# ------------------------------------------------------------------ sky lanes (round 26 locked: flying cars at altitude)
SKY = random.Random(2626)
_lines = sorted({t["i"] for t in LAY["tiles"] if t.get("ab")})
for k in range(0):
    tile = SKY.choice(LAY["tiles"])
    if not tile.get("ab"):
        continue
    a, b = W(tile["ab"][0]), W(tile["ab"][1])
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    z = SKY.choice([26.0, 32.0, 38.0])
    x, y = a
    hc = SKY.choice([(1.0, 0.95, 0.85), (0.4, 0.9, 1.0), (1.0, 0.4, 0.7)])
    box(x - 0.6, y - 0.6, z, x + 0.6, y + 0.6, z + 0.45, (0.3, 0.3, 0.36), facet=False)
    strip(CNEON, (x + dx * 0.7, y + dy * 0.7), (x + dx * 0.9, y + dy * 0.9), 0.9, z + 0.25, hc)
    strip(CNEON, (x - dx * 0.7, y - dy * 0.7), (x - dx * 9.0, y - dy * 9.0), 0.25, z + 0.2, tuple(v * 0.45 for v in RED))

# ------------------------------------------------------------------ round 38: flying cars as low-poly MODELS (CARS38=models)
def flying_car(c, s=1.0):
    """A small low-poly hover car on its sky lane: wedge body, glass cabin, side pods, lane-colour stripe + under-glow,
    white headlights at the nose, red tail lights at the back. Heading (dx, dy); size in world units."""
    x, y, z = c["x"], c["y"], c["z"]
    fx, fy = c["dx"], c["dy"]
    nx, ny = -fy, fx
    col = c["col"]
    Lh, Wh, Hh = 1.7 * s, 0.75 * s, 0.32 * s

    def P(u, v, h):
        return (x + fx * u + nx * v, y + fy * u + ny * v, z + h)
    body = (0.26, 0.25, 0.32)
    bid = rid()
    # wedge body: low nose, higher tail
    b = [P(-Lh, -Wh, 0), P(Lh, -Wh * 0.7, 0), P(Lh, Wh * 0.7, 0), P(-Lh, Wh, 0)]
    t = [P(-Lh * 0.9, -Wh * 0.9, Hh * 1.4), P(Lh * 0.85, -Wh * 0.6, Hh * 0.6), P(Lh * 0.85, Wh * 0.6, Hh * 0.6), P(-Lh * 0.9, Wh * 0.9, Hh * 1.4)]
    for i in range(4):
        j = (i + 1) % 4
        SOLID.face([b[i], b[j], t[j], t[i]], body, bid)
    SOLID.face(t, (0.34, 0.33, 0.42), bid)
    SOLID.face(list(reversed(b)), (0.12, 0.12, 0.16), bid)
    # cabin (dark glass)
    cb = [P(-Lh * 0.35, -Wh * 0.55, Hh * 1.2), P(Lh * 0.35, -Wh * 0.45, Hh * 0.9), P(Lh * 0.35, Wh * 0.45, Hh * 0.9), P(-Lh * 0.35, Wh * 0.55, Hh * 1.2)]
    ct = [P(-Lh * 0.25, -Wh * 0.4, Hh * 2.0), P(Lh * 0.1, -Wh * 0.35, Hh * 1.8), P(Lh * 0.1, Wh * 0.35, Hh * 1.8), P(-Lh * 0.25, Wh * 0.4, Hh * 2.0)]
    for i in range(4):
        j = (i + 1) % 4
        SOLID.face([cb[i], cb[j], ct[j], ct[i]], (0.08, 0.1, 0.16), bid)
    SOLID.face(ct, (0.1, 0.12, 0.2), bid)
    # lane-colour stripe along both flanks + under-glow plate
    for side in (-1, 1):
        CNEON.face([P(-Lh * 0.9, side * Wh * 0.97, Hh * 0.55), P(Lh * 0.8, side * Wh * 0.72, Hh * 0.3), P(Lh * 0.8, side * Wh * 0.72, Hh * 0.45),
                    P(-Lh * 0.9, side * Wh * 0.97, Hh * 0.75)], col, (0, 0, 0))
    CNEON.face([P(-Lh * 0.8, -Wh * 0.8, -0.12 * s), P(Lh * 0.7, -Wh * 0.6, -0.12 * s), P(Lh * 0.7, Wh * 0.6, -0.12 * s), P(-Lh * 0.8, Wh * 0.8, -0.12 * s)],
               tuple(v * 0.7 for v in col), (0, 0, 0))
    # headlights (nose) + tail lights (rear)
    for side in (-1, 1):
        CNEON.face([P(Lh * 1.0, side * Wh * 0.15, Hh * 0.2), P(Lh * 1.0, side * Wh * 0.6, Hh * 0.2), P(Lh * 0.96, side * Wh * 0.6, Hh * 0.5),
                    P(Lh * 0.96, side * Wh * 0.15, Hh * 0.5)], (1.0, 0.97, 0.85), (0, 0, 0))
        CNEON.face([P(-Lh * 1.0, side * Wh * 0.2, Hh * 0.7), P(-Lh * 1.0, side * Wh * 0.85, Hh * 0.7), P(-Lh * 0.98, side * Wh * 0.85, Hh * 1.1),
                    P(-Lh * 0.98, side * Wh * 0.2, Hh * 1.1)], (1.0, 0.12, 0.1), (0, 0, 0))


if os.environ.get("CARS38", "") == "models":
    import skylanes as SK
    for c in SK.cars(float(os.environ.get("CARS38_T", "0.15"))):
        flying_car(c, s=float(os.environ.get("CARS38_S", "1.0")))
    print("CARS", len(SK.cars(0.15)), flush=True)


# ------------------------------------------------------------------ the five HQs + the Cell's base, on their lots
def build_at(fn, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    before = {id(a): len(a.bm.verts) for a in [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values())}
    for g in MOVE_FRAMES:
        for a in g.values():
            before[id(a)] = len(a.bm.verts)
    objs0 = set(bpy.data.objects)
    fn()
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    accs = [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values()) + [a for g in MOVE_FRAMES for a in g.values()]
    for acc in accs:
        m = before.get(id(acc), 0)
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            x0, y0 = v.co.x * s, v.co.y * s
            v.co.x = x0 * cr - y0 * sr + dx
            v.co.y = x0 * sr + y0 * cr + dy
            v.co.z *= s
    for o in set(bpy.data.objects) - objs0:
        x0, y0 = o.location[0] * s, o.location[1] * s
        o.location = (x0 * cr - y0 * sr + dx, x0 * sr + y0 * cr + dy, o.location[2] * s)
        o.rotation_euler = (o.rotation_euler[0], o.rotation_euler[1], o.rotation_euler[2] + math.radians(rot))
        o.scale = (s, s, s)


EYE_STATIC = []
for corp, c in sorted(LAY["hqs"].items()):
    wx, wy = W(c)
    _had_eye = bool(EYE_ACC)
    build_at(HEROES26.get(corp, HEROES25[corp]), wx, wy)
    if EYE_ACC and not _had_eye:
        EYE_STATIC.append((EYE_ACC.pop("solid"), EYE_ACC.pop("neon")))
        EYE_ACC.pop("beam").bm.free()
    print("HQ", corp, flush=True)
_cb = W(LAY["cell_base"])
build_at(HEROES25["rebel_cell"], _cb[0], _cb[1])

# ------------------------------------------------------------------ the Cell's nodes: uplink pads + risers (raid language B)
NODE_BLD = {}
for nd in NET["nodes"]:
    if nd["state"] not in ("owned", "core"):
        continue
    sx, sy = W(nd["lot"])
    best = None
    for (c, q, zt, terr, ts, key) in BUILT:
        if ts < 0.99 or zt < 3.0:
            continue
        dd = math.hypot(c[0] - sx, c[1] - sy)
        if dd < 1.9 * U and (best is None or dd < best[0]):
            best = (dd, c, q, zt)
    if best is None:
        continue
    _, c, q, zt = best
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    hs = min(max(xs) - min(xs), max(ys) - min(ys)) * 0.32
    box(c[0] - hs, c[1] - hs, zt, c[0] + hs, c[1] + hs, zt + 0.35, (0.13, 0.13, 0.17), facet=False)
    for (p0, p1) in (((c[0] - hs, c[1] - hs), (c[0] + hs, c[1] - hs)), ((c[0] + hs, c[1] - hs), (c[0] + hs, c[1] + hs)),
                     ((c[0] + hs, c[1] + hs), (c[0] - hs, c[1] + hs)), ((c[0] - hs, c[1] + hs), (c[0] - hs, c[1] - hs))):
        strip(CNEON, p0, p1, 0.22, zt + 0.37, LIME)
    mx, my = c[0] + hs + 0.3, c[1] + hs + 0.3
    beam((mx, my, zt), (mx, my, zt + 2.2), 0.14, (0.2, 0.2, 0.24))
    CNEON.face([(mx - 0.22, my, zt + 2.2), (mx + 0.22, my, zt + 2.2), (mx + 0.22, my, zt + 2.6), (mx - 0.22, my, zt + 2.6)], LIME, (0, 0, 0))
    # riser: three lime traces up the building corner that faces the socket
    k = min(range(len(q)), key=lambda i: math.hypot(q[i][0] - sx, q[i][1] - sy))
    px, py = q[k]
    for off in (-0.25, 0.0, 0.25):
        beam((px + off * 0.7, py - off * 0.7, 0.05), (px + off * 0.7, py - off * 0.7, zt), 0.07, LIME, acc=CNEON)
    NODE_BLD[nd["id"]] = dict(centre=list(c), top=zt, pad=hs, corner=[px, py])

# ------------------------------------------------------------------ objects, lights, modes
exec("\n".join(_SRC[689:692]))  # solid / neon / win objects
cityo = CITY.obj(TOON)
cneono = CNEON.obj(NEONM)
glaneo = GLANE.obj(NEONM)
cwino = CWIN.obj(WINM)
groundo = GROUND.obj(TOON)
LITM = TOON.copy()
_nt = LITM.node_tree
_em = next(n_ for n_ in _nt.nodes if n_.type == "EMISSION")
_out = next(n_ for n_ in _nt.nodes if n_.type == "OUTPUT_MATERIAL")
_ac = attr(_nt, "col")
_e2 = _nt.nodes.new("ShaderNodeEmission")
_e2.inputs["Strength"].default_value = 0.42
_nt.links.new(_ac.outputs["Color"], _e2.inputs["Color"])
_add = _nt.nodes.new("ShaderNodeAddShader")
_nt.links.new(_em.outputs[0], _add.inputs[0])
_nt.links.new(_e2.outputs[0], _add.inputs[1])
_nt.links.new(_add.outputs[0], _out.inputs[0])
LIT_RAMP = next(n_ for n_ in _nt.nodes if n_.type == "VALTORGB")
lito = LIT.obj(LITM)
BEAM.bm.free()                                   # translucent light cones: off in this all-city still
EYE_SOLIDS = []
for _s, _n in EYE_STATIC:
    EYE_SOLIDS.append(_s.obj(TOON))
    _n.obj(NEONM)
anim_objs = [a.obj(NEONM) for a in ANIM_ACCS]
move_objs = [dict(solid=g["solid"].obj(TOON), lit=g["lit"].obj(LITM), neon=g["neon"].obj(NEONM)) for g in MOVE_FRAMES]
eye_objs = [EYE_ACC["solid"].obj(TOON), EYE_ACC["neon"].obj(NEONM)] if EYE_ACC else []
for i, o in enumerate(anim_objs):
    o.hide_render = i != 0
for i, g in enumerate(move_objs):
    for o in g.values():
        o.hide_render = i != 0

exec("\n".join(_SRC[693:783]))  # lights, MODES, TINT, set_mode, render, override_mat
_set_mode0 = set_mode


def set_mode(m):
    _set_mode0(m)
    for e, e0 in zip(LIT_RAMP.color_ramp.elements, RAMP.color_ramp.elements):
        e.color = tuple(e0.color)


try:
    scene.eevee.shadow_pool_size = "1024"
except Exception:
    pass
for _m in MODES.values():
    _m["sign"] = KN["sign"]


def override_pos(kind):
    m = bpy.data.materials.new("ov_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    L_ = nt.links.new
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    off = nt.nodes.new("ShaderNodeVectorMath")
    off.operation = "ADD"
    off.inputs[1].default_value = (4000.0, 4000.0, 4000.0)
    L_(geo.outputs["Position"], off.inputs[0])
    op = nt.nodes.new("ShaderNodeVectorMath")
    if kind == "pos_hi":
        dv = nt.nodes.new("ShaderNodeVectorMath")
        dv.operation = "DIVIDE"
        dv.inputs[1].default_value = (16.0, 16.0, 16.0)
        L_(off.outputs[0], dv.inputs[0])
        op.operation = "FLOOR"
        L_(dv.outputs[0], op.inputs[0])
    else:
        op.operation = "MODULO"
        op.inputs[1].default_value = (16.0, 16.0, 16.0)
        L_(off.outputs[0], op.inputs[0])
    L_(op.outputs[0], em.inputs["Color"])
    L_(em.outputs[0], out.inputs[0])
    return m


def load_exr(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    buf = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    os.remove(path)
    return buf.reshape(h, w, 4)[::-1, :, :3]


cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.clip_start = 1.0
cam_data.clip_end = 8000
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
from mathutils import Vector  # noqa: E402

SOLIDS = [solid, cityo, groundo, lito] + eye_objs[:1] + EYE_SOLIDS + [g[k] for g in move_objs for k in ("solid", "lit")]
ALLM = [o for o in bpy.data.objects if o.type == "MESH"]


def shoot(spec):
    c = LY36.cam(spec["t"], spec["ortho"])
    r_, u_, f_ = LY36.basis(c)
    t = c["target"]
    cam.location = (t[0] - f_[0] * c["dist"], t[1] - f_[1] * c["dist"], t[2] - f_[2] * c["dist"])
    cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()
    cam_data.ortho_scale = c["ortho"]
    scene.render.resolution_x, scene.render.resolution_y = spec["res"]
    bpy.context.view_layer.update()
    P = lambda s: os.path.join(OUTDIR, "%s_%s" % (spec["tag"], s))
    scene.view_settings.view_transform = "Standard"
    scene.eevee.taa_render_samples = spec.get("samples", 16)
    scene.render.filter_size = 1.5
    set_mode("night")
    render(P("beauty_night.png"))
    mats = {o.name: list(o.data.materials) for o in ALLM}
    blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
    for o in SOLIDS:
        o.data.materials[0] = blackm
    set_mode("night")
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    render(P("glow_night.png"))
    for o in ALLM:
        for i, m in enumerate(mats[o.name]):
            o.data.materials[i] = m
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    scene.eevee.taa_render_samples = 1
    scene.render.filter_size = 0.01
    for kind in ("normal", "id"):
        bpy.context.view_layer.material_override = override_mat(kind)
        render(P(kind + ".png"))
    try:
        scene.view_settings.view_transform = "Raw"
    except TypeError:
        pass
    for kind in ("pos_hi", "pos_lo"):
        bpy.context.view_layer.material_override = override_pos(kind)
        scene.render.image_settings.file_format = "OPEN_EXR"
        scene.render.image_settings.color_depth = "32"
        render(P(kind + ".exr"))
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_depth = "16"
    arr = np.round(load_exr(P("pos_hi.exr"))) * 16.0 + load_exr(P("pos_lo.exr")) - 4000.0
    np.save(P("pos.npy"), arr.astype(np.float32))
    # ground-only position: the network decals are also evaluated here, so a node / link hidden behind a building
    # can be drawn through it as a ghost (x-ray), like a depth-test-GREATER stencil pass in Godot
    hidden = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o is not groundo and not o.hide_render:
            o.hide_render = True
            hidden.append(o)
    for kind in ("pos_hi", "pos_lo"):
        bpy.context.view_layer.material_override = override_pos(kind)
        scene.render.image_settings.file_format = "OPEN_EXR"
        scene.render.image_settings.color_depth = "32"
        render(P("g" + kind + ".exr"))
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_depth = "16"
    bpy.context.view_layer.material_override = None
    if spec.get("ghost"):
        glaneo.hide_render = False
        scene.view_settings.view_transform = "Standard"
        scene.eevee.taa_render_samples = spec.get("samples", 16)
        scene.render.filter_size = 1.5
        set_mode("night")
        render(P("gbeauty_night.png"))
        groundo.data.materials[0] = blackm
        bg.inputs["Color"].default_value = (0, 0, 0, 1)
        render(P("gglow_night.png"))
        groundo.data.materials[0] = TOON
        glaneo.hide_render = True
        scene.eevee.taa_render_samples = 1
        scene.render.filter_size = 0.01
        try:
            scene.view_settings.view_transform = "Raw"
        except TypeError:
            pass
    for o in hidden:
        o.hide_render = False
    arr = np.round(load_exr(P("gpos_hi.exr"))) * 16.0 + load_exr(P("gpos_lo.exr")) - 4000.0
    np.save(P("gpos.npy"), arr.astype(np.float32))
    json.dump(dict(cam=c, res=spec["res"], node_bld=NODE_BLD, ants=ANTS), open(P("scene.json"), "w"), indent=1)
    print("SHOT", spec["tag"], flush=True)


for spec in CAMS:
    shoot(spec)
print("DONE", flush=True)
