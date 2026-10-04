"""Round 34: the Cell's district: painted roofs + the Tokyo canyon (a real grid street), one model for map and combat.
Blender 5.2 headless.

blender -b --factory-startup --python hq34.py -- rebel_cell_hq <outdir> <close|map|preview> canyon [dispatch]
  close: perspective combat close-up 2880 x 1620, night: beauty, glow, normal, id, depth
  map  : orthographic sprite in the game's 2:1 iso projection, transparent, city buildings as holdout
The city is the game's own layout with the fist streets removed and the grid completed (grid27.py ->
../scratch/layout/rc27.json from layout27.py). cfg28.py holds the rules shared with map27.py: which roofs carry the
Cell's paint (the projected crest) and which city buildings make way for the canyon's shophouses.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials

import json
import cfg28

_argv = sys.argv[sys.argv.index("--") + 1:]
JOB, OUTDIR, VIEW, IDEA = _argv[0], _argv[1], _argv[2], _argv[3]
STATE = _argv[4] if len(_argv) > 4 else ""
DISP = STATE == "dispatch"
CORP, KIND = "rebel_cell", "hq"
os.makedirs(OUTDIR, exist_ok=True)
rng = random.Random(2727)
# round 28 knobs (env): PAINT28 strokes|rects|none, FRAME28 = animation frame (-1 = still), CAMSET28 combat|street,
# RES28 "w,h", TAG28 suffix for the output names
cfg28.MODE["paint"] = os.environ.get("PAINT28", "none")  # round 29: painted roofs dropped
FRAME = int(os.environ.get("FRAME28", "-1"))
CAMSET = os.environ.get("CAMSET28", "combat")
RES = {"close": (2880, 1620), "preview": (960, 540), "map": (3000, 3000)}[VIEW]
if os.environ.get("RES28"):
    RES = tuple(int(v) for v in os.environ["RES28"].split(","))
scene.render.resolution_x, scene.render.resolution_y = RES
scene.eevee.taa_render_samples = 8 if VIEW == "preview" else 24
LAY = json.load(open(os.path.join(_HERE, "..", "scratch", "layout", "rc27.json")))
CFG = cfg28.Cfg(LAY["centre"])  # round 29: no painted block (the district keeps the city's own buildings)
CX, CY = LAY["centre"]
U = 6.0
KH = U / 41.64


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 27.5
exec(open(os.path.join(_HERE, "heroes24.py"), encoding="utf-8-sig").read())
KN = CORP_KNOBS[CORP]
exec("\n".join(_SRC[504:682]))  # container(), ziggurat(), depot()
exec(open(os.path.join(_HERE, "heroes25.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(_HERE, "kit26.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(_HERE, "street34.py"), encoding="utf-8-sig").read())

# ------------------------------------------------------------------ the city around it, from the game's layout
CITY = Acc("city")
CNEON = Acc("cneon")
CWIN = Acc("cwin")
GROUND = Acc("ground")
HOLD_ONLY = VIEW == "map"
FAMS_C = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
TERR = LAY["terr"]
PAINT_RED = (2.6, 0.10, 0.12)


def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def paint_roof(top, z, bid, seed, acc=None):
    """The Cell's crude paint on a roof (top = world xy polygon, z = roof height).
    Home: red roller fill (ragged edge), lime / pink graffiti strokes over it, drips down the walls facing the camera.
    DISPATCH: harsh glowing red, glitch bars torn sideways past the roof edge, black corruption blocks."""
    acc = acc or CITY
    pr = random.Random(seed)
    n = len(top)
    cx = sum(p[0] for p in top) / n
    cy = sum(p[1] for p in top) / n
    rag = []
    for (x, y) in top:
        k = pr.uniform(0.96, 1.0)  # round 28: pieces of big strokes: barely inset, so the stroke runs on across roofs
        rag.append((cx + (x - cx) * k + pr.uniform(-0.1, 0.1), cy + (y - cy) * k + pr.uniform(-0.1, 0.1), z + 0.04))
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if DISP:
        NEON.face(rag, (0.95, 0.04, 0.06), (0, 0, 0))
        for _ in range(pr.randint(2, 4)):
            y0 = pr.uniform(min(ys), max(ys))
            hh = pr.uniform(0.3, 1.0)
            off = pr.uniform(-0.45, 0.45) * w
            black = pr.random() < 0.45
            q = [(min(xs) + off, y0, z + 0.1), (max(xs) + off, y0, z + 0.1), (max(xs) + off, y0 + hh, z + 0.1), (min(xs) + off, y0 + hh, z + 0.1)]
            if black:
                acc.face(q, (0.03, 0.02, 0.03), bid)
            else:
                NEON.face(q, (1.0, 0.45, 0.45), (0, 0, 0))
        for _ in range(pr.randint(1, 3)):
            bx, by = pr.uniform(min(xs), max(xs)), pr.uniform(min(ys), max(ys))
            s = pr.uniform(0.5, 1.4)
            acc.face([(bx, by, z + 0.12), (bx + s * 1.6, by, z + 0.12), (bx + s * 1.6, by + s, z + 0.12), (bx, by + s, z + 0.12)], (0.03, 0.02, 0.03), bid)
    else:
        tone = pr.uniform(0.85, 1.08)
        acc.face(rag, tuple(c * tone for c in PAINT_RED), bid)
        for _ in range(1 if pr.random() < 0.3 else 0):  # round 28: sparse lime / pink tags
            c = (2.0, 2.4, 0.0) if pr.random() < 0.55 else (2.4, 0.5, 1.4)
            a = (pr.uniform(min(xs), max(xs)), pr.uniform(min(ys), max(ys)))
            b = (a[0] + pr.uniform(-0.5, 0.5) * w, a[1] + pr.uniform(-0.5, 0.5) * h)
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            tw = pr.uniform(0.15, 0.32)
            ox, oy = -(b[1] - a[1]) / L * tw, (b[0] - a[0]) / L * tw
            acc.face([(a[0] + ox, a[1] + oy, z + 0.07), (a[0] - ox, a[1] - oy, z + 0.07), (b[0] - ox, b[1] - oy, z + 0.07), (b[0] + ox, b[1] + oy, z + 0.07)], c, bid)
    for i in range(n):  # drips down the walls that face the camera side
        j = (i + 1) % n
        a, b = top[i], top[j]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        if L < 1.5:
            continue
        nx, ny = ey / L, -ex / L
        if nx * ((a[0] + b[0]) / 2 - cx) + ny * ((a[1] + b[1]) / 2 - cy) < 0:
            nx, ny = -nx, -ny
        for k in range(int(L / 1.6)):
            if pr.random() < 0.5:
                continue
            t = pr.uniform(0.05, 0.95)
            px, py = a[0] + ex * t + nx * 0.07, a[1] + ey * t + ny * 0.07
            ww = pr.uniform(0.18, 0.5)
            ln = pr.uniform(0.6, 4.5)
            ux, uy = ex / L * ww, ey / L * ww
            pts = [(px - ux, py - uy, z + 0.05), (px + ux, py + uy, z + 0.05), (px + ux * 0.5, py + uy * 0.5, z - ln), (px - ux * 0.5, py - uy * 0.5, z - ln)]
            if DISP:
                NEON.face(pts, (0.75, 0.02, 0.04), (0, 0, 0))
            else:
                acc.face(pts, PAINT_RED, bid)

PAINTED = []
_CO = None  # the canyon origin (world), for the round 30 dressing of the buildings round the canyon


def near_canyon(x, y):
    global _CO
    if _CO is None:
        _CO = W(cfg28.Cfg.canyon_origin())
    cx_, cy_ = y - _CO[1], _CO[0] - x  # world -> canyon frame
    return abs(cx_) < 75 and -150 < cy_ < cfg28.Cfg.canyon_len() + 80  # round 31: the towers by the camera too


def paint_stencil(top, z, bid, seed, acc=None):
    """The crest is a stencil over the rooftops: paint only the part of this roof that the map sees inside it."""
    lot = [(CX + x / U, CY - y / U) for (x, y) in top]
    for k, piece in enumerate(CFG.pieces_lot(lot, z / KH)):
        PAINTED.append(seed)
        paint_roof([W(p) for p in piece], z, bid, seed + k, acc=acc)


def city_building(b):
    qL = b["q"]
    cxl = sum(p[0] for p in qL) / len(qL)
    cyl_ = sum(p[1] for p in qL) / len(qL)
    if CFG.removed(cxl, cyl_):
        return
    q = [W(p) for p in qL]
    n = len(q)
    z0, h = b["z0"] * KH, b["h"] * KH
    ts = b["ts"]
    cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
    top = [(cxq + (x - cxq) * ts, cyq + (y - cyq) * ts) for (x, y) in q]
    if not HOLD_ONLY and h > 30 and near_canyon(cxq, cyq):  # round 31: the bare spires right in front of the camera go
        _cx, _cy = cyq - _CO[1], _CO[0] - cxq
        if _cy < 15 and abs(_cx) > 9:
            return
    fam = FAMS_C[abs(b["key"]) % len(FAMS_C)]
    tc = TERR.get(b["terr"], (0.8, 0.8, 0.8))
    col = mixc(fam, tc, 0.28 if b["terr"] else 0.0)
    bid = rid()
    for i in range(n):
        j = (i + 1) % n
        a, c = q[i], q[j]
        quad = [(a[0], a[1], z0), (c[0], c[1], z0), (top[j][0], top[j][1], z0 + h), (top[i][0], top[i][1], z0 + h)]
        if HOLD_ONLY:
            CITY.face(quad, col, bid)
        else:
            CITY.facet_quad(*quad, col, bid)
        if not HOLD_ONLY and ts >= 0.99 and h > 2.4:
            L = math.hypot(c[0] - a[0], c[1] - a[1])
            if L < 2.0:
                continue
            ux, uy = (c[0] - a[0]) / L, (c[1] - a[1]) / L
            nx, ny = uy, -ux
            if nx * (a[0] - cxq) + ny * (a[1] - cyq) < 0:
                nx, ny = -nx, -ny
            nxw, nzw = int((L - 0.6) / 1.6), int((h - 1.0) / 2.0)
            for u in range(nxw):
                for v in range(nzw):
                    if rng.random() > 0.22:
                        continue
                    t0 = 0.3 + u * 1.6 + 0.4
                    z = z0 + 0.8 + v * 2.0
                    wc = rng.choice(WIN_COLS)
                    s = 0.5 + 0.5 * rng.random()
                    p0 = (a[0] + ux * t0 + nx * 0.05, a[1] + uy * t0 + ny * 0.05)
                    p1 = (p0[0] + ux * 0.8, p0[1] + uy * 0.8)
                    CWIN.face([(p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z + 0.7), (p0[0], p0[1], z + 0.7)],
                              tuple(x * s for x in wc), (0, 0, 0))
    CITY.face([(x, y, z0 + h) for (x, y) in top], tuple(min(1, v * 1.08) for v in col), bid)
    if not HOLD_ONLY and near_canyon(cxq, cyq):  # round 30: balconies, AC units, laundry, pipes, stairs, rooftop life
        lg = random.Random(abs(b["key"]) * 7 + int(b["z0"] * 10))
        for i in range(n):
            a, c = q[i], q[(i + 1) % n]
            ex, ey = c[0] - a[0], c[1] - a[1]
            L_ = math.hypot(ex, ey) or 1
            nx_, ny_ = ey / L_, -ex / L_
            if nx_ * ((a[0] + c[0]) / 2 - cxq) + ny_ * ((a[1] + c[1]) / 2 - cyq) < 0:
                nx_, ny_ = -nx_, -ny_
            hh_ = h * (0.75 if ts < 0.99 else 1.0)
            facade_life(a, c, z0, hh_, (nx_, ny_), lg, lit=2.2 if hh_ > 12 else 1.0)
            tower_skin(a, c, z0, hh_, (nx_, ny_), lg, abs(b["key"]) * 3 + i)  # round 31: no blank tower faces
        if ts > 0.6:
            roof_clutter(top, z0 + h, lg)
    if ts > 0.3 and not HOLD_ONLY:  # (the map paints the city roofs itself: map27.py, same stencil)
        paint_stencil(top, z0 + h, bid, abs(b["key"]) * 31 + int(b["z0"]))
    if not HOLD_ONLY and rng.random() < 0.42 and ts > 0.05:
        for i in range(n):
            j = (i + 1) % n
            beam((top[i][0], top[i][1], z0 + h + 0.08), (top[j][0], top[j][1], z0 + h + 0.08), 0.22, tuple(b["ink"]), acc=CNEON)


for b in LAY["buildings"]:
    city_building(b)

if not HOLD_ONLY:
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
        strip(CNEON, (a[0] - dx * 0.3, a[1] - dy * 0.3), (b[0] + dx * 0.3, b[1] + dy * 0.3), 2 * (half + 0.5), 0.02,
              tuple(v * (0.10 + tr * 0.16) * (1.0 if HOLD_ONLY else (0.12 if CAMSET == "street" else 0.35)) for v in col))  # round 28: the road's wash much dimmer up close
        nl = min(strokes, 3 + int(tr * 9))
        hr = random.Random(t["i"] * 7919 + t["j"])
        for k in range(nl):
            u = (k + 0.5) / nl * 2 - 1
            lane = u * half * 0.8 + (hr.random() - 0.5) * 0.25
            al = 0.55 + 0.35 * hr.random() + tr * 0.15
            strip(CNEON, (a[0] + nx * lane - dx * 0.35, a[1] + ny * lane - dy * 0.35), (b[0] + nx * lane + dx * 0.35, b[1] + ny * lane + dy * 0.35),
                  0.18, 0.04, tuple(min(1, v * al) * (1.0 if HOLD_ONLY else (0.22 if CAMSET == "street" else 0.6)) for v in col))
    for t in LAY["trails"]:
        a, b = W(t["a"]), W(t["b"])
        strip(CNEON, a, b, 0.32, 0.06, tuple(t["col"]))

# ------------------------------------------------------------------ the hero
# the canyon: grid street j = 36 between the cross streets i = 26 and 46, built in its own frame (local Y runs
# along the street toward -x lot, from the camera end) and rotated into the world
_ox, _oy = W(cfg28.Cfg.canyon_origin())
LCAN = cfg28.Cfg.canyon_len()
GAPS[:] = cfg28.Cfg.canyon_gaps()


def C2W(x, y):
    return (_ox - y, _oy + x)  # canyon frame -> world (+90 deg)


def canyon():
    tokyo_street(0.0, LCAN, seed=27, hmin=7, hfar=4, roof_screens=0.5)
    gr = random.Random(127)
    # round 29: no holograms. The head of the street: a billboard across the far crossing, facing down the canyon
    # (home: an ordinary ad; DISPATCH: REBEL_CELL)
    yb = LCAN + 3.0
    for sx in (-1, 1):
        beam((sx * 4.6, yb, 0), (sx * 4.6, yb, 13), 0.45, (0.2, 0.18, 0.2))
    screen((0, yb, 13), (1, 0, 0), (0, 0, 1), (0, -1, 0), 10, 6, "glyph" if not DISP else "text:REBEL_CELL",
           (0.35, 0.85, 1.0) if not DISP else DRED, (0.95, 0.93, 0.86) if not DISP else DRED2, 5, glitch=0.6 if DISP else 0.0)


build_xf(canyon, _ox, _oy, 90.0)

def painted_block():
    """The painted block: one low flat-roof tenement per lot (cfg28.tenement_lots), city-coloured so it blends;
    each roof then takes the stencil."""
    for (i, j), hh in sorted(CFG.ten.items()):
        gr = random.Random(i * 31 + j * 977)
        m = 0.06
        x0, x1 = (i - CX) * U + m, (i + 1 - CX) * U - m
        y0, y1 = -(j + 1 - CY) * U + m, -(j - CY) * U - m
        fam = FAMS_C[(i * 7 + j * 3) % len(FAMS_C)]
        col = mixc(fam, TERR.get("rebel_cell", (0.8, 0.3, 0.3)), 0.28)
        bid = wall_box(x0, y0, 0, x1, y1, hh, col)
        if not HOLD_ONLY:
            windows2(x0, y0, 0, x1, y1, hh, p=0.3, sx=1.8, sz=2.6, ww=0.8, wh=0.7, faces=(0, 1), gr=gr)
        # (round 28: no parapets on the painted block, so the big strokes run unbroken across the roofs)
        if gr.random() < 0.3:
            cyl(gr.uniform(x0 + 1.2, x1 - 1.2), gr.uniform(y0 + 1.2, y1 - 1.2), hh, hh + 1.6, 0.7, (0.3, 0.28, 0.3), n=8)
        paint_stencil([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], hh + 0.08, bid, i * 1000 + j, acc=SOLID)


painted_block()
for n_, (x0, y0, x1, y1, hh) in enumerate(ROOFS_LOCAL):  # the shophouse roofs carry the stencil too
    paint_stencil([C2W(x, y) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], hh + 0.1, rid(), 5000 + n_ * 17, acc=SOLID)
if VIEW != "map":  # other HQs in view (same skyline as the map)
    for other, c in LAY.get("hqs", {}).items():
        if other == "rebel_cell" or math.hypot(c[0] - CX, c[1] - CY) > LAY["radius"] - 4:
            continue
        _st = STATE
        STATE = ""
        wx, wy = W(c)
        build_at(HEROES25[other], wx, wy)
        STATE = _st

exec("\n".join(_SRC[689:692]))  # solid / neon / win objects
cityo = CITY.obj(TOON)
cneono = CNEON.obj(NEONM)
cwino = CWIN.obj(WINM)
groundo = GROUND.obj(TOON)
exec("\n".join(_SRC[693:783]))  # lights, MODES, TINT, set_mode, render, override_mat
try:
    scene.eevee.shadow_pool_size = "1024"
except Exception:
    pass
for _m in MODES.values():
    _m["sign"] = (1.0, 0.18, 0.20) if DISP else (0.83, 1.0, 0.0)
if VIEW != "map":  # round 28: a darker canyon. Signs at ~55 %, windows dimmer, the toon ramp one step down, so the
    # light comes in pools and the gaps between signs stay dark (the alley depth, wires, people read)
    _n = MODES["night"]
    _n["neon"], _n["win"] = 0.72, 0.85  # round 32: brighter than round 28-31 (designer: too dark)
    _n["ramp"] = [tuple(c * 0.92 for c in col) for col in _n["ramp"]]
    _n["sign"] = tuple(c * 0.75 for c in _n["sign"])

# ------------------------------------------------------------------ cameras
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 6000
DIAG = Vector((1, -1, 0)).normalized()
CAM27 = ((0.0, -95.0, 54.0), (0.0, 52.0, 4.0), 54)  # combat zoom: elevated telephoto down the canyon, the street is the focus
if CAMSET == "street":  # round 28: eye height in the canyon, looking down the street into the haze
    CAM27 = ((0.4, 3.0, 1.15), (0.0, 120.0, 6.5), 21)
if VIEW == "map":
    el = math.radians(30)
    ppu = 2 * 34 * math.sqrt(2) / U
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = RES[0] / ppu
    ZC = 450.0 / (math.cos(el) * 34 * math.sqrt(2) / U)
    tgt = Vector((0, 0, ZC))
    d = Vector((DIAG.x * math.cos(el), DIAG.y * math.cos(el), math.sin(el)))
    cam.location = tgt + d * 1400
else:
    (clx, cly, clz), (tlx, tly, tlz), lens = CAM27  # canyon frame: camera and target
    if os.environ.get("CAM27"):  # framing override: "x,y,z,tx,ty,tz,lens" (canyon frame)
        _c = [float(v) for v in os.environ["CAM27"].split(",")]
        (clx, cly, clz), (tlx, tly, tlz), lens = _c[0:3], _c[3:6], _c[6]
    cw, tw = C2W(clx, cly), C2W(tlx, tly)
    tgt = Vector((tw[0], tw[1], tlz))
    cam.location = (cw[0], cw[1], clz)
    cam_data.lens = lens
cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()

tag = "rc34_canyon%s%s" % ("_dispatch" if DISP else "", os.environ.get("TAG28", ""))
if VIEW == "map":
    hold = bpy.data.materials.new("hold")
    hold.node_tree.nodes.clear()
    ho = hold.node_tree.nodes.new("ShaderNodeOutputMaterial")
    hh = hold.node_tree.nodes.new("ShaderNodeHoldout")
    hold.node_tree.links.new(hh.outputs[0], ho.inputs[0])
    cityo.data.materials[0] = hold
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    set_mode("night")
    render(os.path.join(OUTDIR, "%s_map_beauty.png" % tag))
    scene.eevee.taa_render_samples = 4
    for kind in ("normal", "id"):
        ov = override_mat(kind)
        for o in (solid, neon, win):
            o.data.materials[0] = ov
        render(os.path.join(OUTDIR, "%s_map_%s.png" % (tag, kind)))
    print("DONE", flush=True)
else:
    set_mode("night")
    render(os.path.join(OUTDIR, "%s_beauty_night.png" % tag))
    if VIEW == "preview":
        print("DONE", flush=True)
        raise SystemExit
    blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
    for o in (solid, cityo, groundo):
        o.data.materials[0] = blackm
    set_mode("night")
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    render(os.path.join(OUTDIR, "%s_glow_night.png" % tag))
    for o in (solid, cityo, groundo):
        o.data.materials[0] = TOON
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    scene.eevee.taa_render_samples = 4
    for kind in ("normal", "id", "depth"):
        bpy.context.view_layer.material_override = override_mat(kind)
        if kind == "depth":
            bg.inputs["Color"].default_value = (1, 1, 1, 1)
        render(os.path.join(OUTDIR, "%s_%s.png" % (tag, kind)))
    bpy.context.view_layer.material_override = None
    print("DONE", flush=True)
