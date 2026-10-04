"""Round 32: the two strongest netrun-route worlds, Blender 5.2 headless, in the locked Cv2 + E pipeline.

blender -b --factory-startup --python r32_scene.py -- <street|tower> <outdir> <still|anim|preview> [walls]

  street : C, TRANSIT PATH. The link between the Cell's relay (left) and Meridian Depot 15 (right) unrolled into a
           city corridor: four east-west lanes (rows) crossed by a cross street between every pair of layers.
           Route nodes are pads on the lanes; links are circuit traces that jog through the cross streets.
  tower  : B, BUILDING CLIMB. A Meridian container keep in cutaway: 7 tiers of shipping containers (floors = layers),
           each open container a room (node); the crane cab at the top is the final Server Rack.
  still  : 2880 x 1620 (beauty night, glow, normal, id, depth) + anchors.json (node / link screen coords at 1920 x 1080)
  anim   : NF camera frames at 1440 x 810 for the zoom transition GIF (same passes per frame) + anchors per frame
  walls  : tower only: the containers keep their front walls (the closed exterior, for the cutaway reveal)

Shared code is exec'd from the round 30 copy of target_corps.py (setup, primitives, toon/glow materials, container(),
depot(), key light, night mode, render, data-pass overrides). Everything here is seeded.
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv[sys.argv.index("--") + 1:]
SCENE_KIND, OUTDIR = _argv[0], _argv[1]
VIEW = _argv[2] if len(_argv) > 2 else "still"
WALLS = len(_argv) > 3 and _argv[3] == "walls"
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
_saved = sys.argv
sys.argv = ["blender", "--", "meridian_regular", OUTDIR]
exec("\n".join(_SRC[0:314]))  # setup, Acc, box/beam/strip/windows/roof_trim/text_obj, materials
sys.argv = _saved
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 0.0
exec("\n".join(_SRC[505:523]))  # container()
exec("\n".join(_SRC[622:681]))  # depot()
rng = random.Random(3232 if SCENE_KIND == "street" else 3233)
os.makedirs(OUTDIR, exist_ok=True)

RES = {"still": (2880, 1620), "preview": (1280, 720), "anim": (1440, 810)}[VIEW]
scene.render.resolution_x, scene.render.resolution_y = RES
scene.eevee.taa_render_samples = 24 if VIEW == "still" else 10
ASPH = (0.15, 0.15, 0.19)
MER_FAMS = [(0.58, 0.38, 0.22), (0.62, 0.42, 0.24), (0.48, 0.34, 0.26), (0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40)]
TRIMS = [AMBER, AMBER, CYAN, PINK, (0.6, 0.4, 1.0), (0.4, 1.0, 0.6)]
LIME = (0.83, 1.0, 0.0)
ANCH = {}


def lane_street(p0, p1, w, centre, edge, traffic=6, dim=0.16, bright=1.0):
    """A glowing street between two xy points (the city map's lane look)."""
    strip(NEON, p0, p1, w, 0.02, tuple(v * dim for v in centre))
    centre, edge = tuple(v * bright for v in centre), tuple(v * bright for v in edge)
    strip(NEON, p0, p1, 0.6, 0.04, centre)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    for s in (-1, 1):
        o = s * (w / 2 - 0.5)
        strip(NEON, (p0[0] + nx * o, p0[1] + ny * o), (p1[0] + nx * o, p1[1] + ny * o), 0.28, 0.04, edge)
    for k in range(traffic):
        t0 = rng.uniform(0, 0.9)
        o = rng.choice([-1, 1]) * w * 0.22
        a = (p0[0] + dx * t0 + nx * o, p0[1] + dy * t0 + ny * o)
        ln = rng.uniform(5, 14)
        strip(NEON, a, (a[0] + ux * ln, a[1] + uy * ln), 0.2, 0.05, RED if o > 0 else WHITE)


def city_building(x0, y0, x1, y1, h, c=None, trim_p=0.5, win_p=None):
    c = c or rng.choice(MER_FAMS)
    taper = rng.choice([0, 0, 0, 0.4, 0.8]) if h > 14 else 0
    box(x0, y0, 0, x1, y1, h, c, taper=taper)
    windows(x0 + taper, y0 + taper, 0, x1 - taper, y1 - taper, h, p=win_p if win_p is not None else (0.34 if h > 20 else 0.22))
    top = h
    if h > 16 and rng.random() < 0.5:
        i = min(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.28)
        h2 = h + rng.uniform(4, 14)
        box(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, tuple(v * 1.05 for v in c))
        windows(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, p=0.3)
        top = h2
        x0, y0, x1, y1 = x0 + i, y0 + i, x1 - i, y1 - i
    if rng.random() < trim_p:
        roof_trim(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, top + 0.15, rng.choice(TRIMS))
    if rng.random() < 0.35 and x1 - x0 > 4 and y1 - y0 > 4:
        cx, cy = rng.uniform(x0 + 1, x1 - 3), rng.uniform(y0 + 1, y1 - 3)
        box(cx, cy, top, cx + 2, cy + 2, top + 1.4, (0.3, 0.3, 0.34), facet=False)
    if top > 26 and rng.random() < 0.6:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        beam((mx, my, top), (mx, my, top + rng.uniform(5, 12)), 0.25, (0.25, 0.25, 0.3))
        z = top + 8
        NEON.face([(mx - 0.5, my, z), (mx + 0.5, my, z), (mx + 0.5, my, z + 1), (mx - 0.5, my, z + 1)], RED, (0, 0, 0))


def fill_block(x0, y0, x1, y1, hmin, hmax, margin=1.2, trim_p=0.5):
    """1-3 buildings packed into a block."""
    x0, y0, x1, y1 = x0 + margin, y0 + margin, x1 - margin, y1 - margin
    if x1 - x0 < 3 or y1 - y0 < 3:
        return
    n = rng.choice([1, 2, 2, 3]) if x1 - x0 > 14 else 1
    xs = sorted([x0, x1] + [rng.uniform(x0 + 4, x1 - 4) for _ in range(n - 1)])
    for i in range(len(xs) - 1):
        a, b = xs[i] + (0.6 if i else 0), xs[i + 1] - (0.6 if i < len(xs) - 2 else 0)
        if b - a < 2.5:
            continue
        if rng.random() < 0.5 and y1 - y0 > 9:  # split in depth too
            ym = rng.uniform(y0 + 3.5, y1 - 3.5)
            city_building(a, y0, b, ym - 0.4, rng.uniform(hmin, hmax), trim_p=trim_p)
            city_building(a, ym + 0.4, b, y1, rng.uniform(hmin, hmax), trim_p=trim_p)
        else:
            city_building(a, y0, b, y1, rng.uniform(hmin, hmax), trim_p=trim_p)


# =================================================================== C: STREET (transit path)
ROWS = [36.0, 12.0, -12.0, -36.0]           # far -> near (world y)
LX = [-108.0, -70.0, -32.0, 6.0, 44.0, 82.0]  # layers 1..6 (world x)
START = (-150.0, -12.0)
FINAL = (128.0, -12.0)
CROSS = [-129.0, -89.0, -51.0, -13.0, 25.0, 63.0, 105.0]  # a cross street in every gap
STREET_W = {36.0: 8.0, 12.0: 8.0, -12.0: 12.0, -36.0: 8.0}
CROSS_W = 8.0
# the route graph (GDD 4.2): layer -> [(kind, row)]
C_LAYERS = [
    [("router", 0), ("router", 2), ("router", 3)],
    [("router", 0), ("terminal", 1), ("router", 3)],
    [("modem", 0), ("elite", 1), ("router", 2), ("terminal", 3)],
    [("router", 1), ("rack", 2), ("terminal", 3)],
    [("elite", 0), ("modem", 2), ("router", 3)],
    [("router", 1), ("elite", 2)],
]
# edges between consecutive layers as (row_a, row_b); layer 0 = START (row 2), layer 7 = FINAL (row 2)
C_EDGES = [
    [(2, 0), (2, 2), (2, 3)],
    [(0, 0), (0, 1), (2, 1), (3, 3)],
    [(0, 0), (1, 1), (1, 2), (3, 2), (3, 3)],
    [(0, 1), (1, 1), (1, 2), (2, 2), (3, 3)],
    [(1, 0), (2, 2), (2, 3), (3, 3)],
    [(0, 1), (2, 1), (2, 2), (3, 2)],
    [(1, 2), (2, 2)],
]


def street_scene():
    big = VIEW == "anim"
    X0, X1 = (-480, 520) if big else (-260, 300)
    Y0, Y1 = (-420, 520) if big else (-170, 300)
    box(X0, Y0, -1, X1, Y1, 0, ASPH, facet=False)
    MERS = (1.0, 0.55, 0.12)
    for y in ROWS:
        x_end = 116.0 if y != -12.0 else FINAL[0]
        lane_street((START[0] - 20 if y == -12.0 else -146.0, y), (x_end, y), STREET_W[y], MERS if y != -12.0 else AMBER, CYAN,
                    traffic=10 if y == -12.0 else 4, dim=0.09, bright=0.9)
    for x in CROSS:
        lane_street((x, -40.0), (x, 40.0), CROSS_W, (0.75, 0.35, 1.0), (0.4, 0.7, 1.0), traffic=2, dim=0.06, bright=0.6)
    # outer city streets (the rest of the grid) so the corridor sits in the city
    for y in (64.0, 100.0, 150.0, 205.0, 265.0, -64.0, -100.0, -140.0) + ((330.0, 400.0, 470.0, -200.0, -260.0, -330.0) if big else ()):
        lane_street((X0, y), (X1, y), 9.0, rng.choice([AMBER, (0.75, 0.35, 1.0), (0.3, 1.0, 0.6), CYAN]), CYAN, traffic=8, dim=0.05, bright=0.45)
    for x in (-200.0, -136.0, -49.0, 35.0, 124.0, 210.0, 270.0) + ((-300.0, -380.0, -450.0, 330.0, 400.0, 470.0) if big else ()):
        lane_street((x, 40.0), (x, Y1), 8.0, rng.choice([AMBER, (0.75, 0.35, 1.0), CYAN]), CYAN, traffic=4, dim=0.045, bright=0.4)
        lane_street((x, Y0), (x, -40.0), 8.0, rng.choice([AMBER, (0.75, 0.35, 1.0), CYAN]), CYAN, traffic=3, dim=0.045, bright=0.4)
    # the elevated transit line along the far edge (y = 50), with a train
    vz = 11.0
    for x in range(int(X0), int(X1), 16):
        box(x - 0.9, 48.6, 0, x + 0.9, 51.4, vz, (0.22, 0.21, 0.26), facet=False)
    box(X0, 47.0, vz, X1, 53.0, vz + 1.2, (0.30, 0.29, 0.34), facet=False)
    strip(NEON, (X0, 47.2), (X1, 47.2), 0.25, vz + 1.25, CYAN)
    strip(NEON, (X0, 52.8), (X1, 52.8), 0.25, vz + 1.25, CYAN)
    for k in range(4):
        tx = -40 + k * 13.5
        box(tx, 48.0, vz + 1.2, tx + 12.8, 52.0, vz + 5.0, (0.78, 0.76, 0.80))
        for j in range(5):
            NEON.face([(tx + 0.8 + j * 2.4, 47.9, vz + 2.8), (tx + 2.2 + j * 2.4, 47.9, vz + 2.8), (tx + 2.2 + j * 2.4, 47.9, vz + 4.0),
                       (tx + 0.8 + j * 2.4, 47.9, vz + 4.0)], (0.55, 0.95, 1.0), (0, 0, 0))
        NEON.face([(tx, 47.9, vz + 1.6), (tx + 12.8, 47.9, vz + 1.6), (tx + 12.8, 47.9, vz + 2.0), (tx, 47.9, vz + 2.0)], PINK, (0, 0, 0))
    # corridor blocks: between rows and cross streets (low, so nothing hides a lane)
    rows_e = [(40.0 + 4, 60.0), (16.0, 32.0), (-6.0, 8.0), (-32.0, -18.0), (-60.0, -40.0)]
    xs = [-186.0] + CROSS + [124.0]
    for (ya, yb) in rows_e:
        for i in range(len(xs) - 1):
            xa, xb = xs[i] + CROSS_W / 2, xs[i + 1] - CROSS_W / 2
            if xa > 120 or (i == 0 and ya == -32.0):
                continue
            if ya > 40:
                if ya < 47:  # under the viaduct: short sheds only
                    fill_block(xa, ya, xb, 46.5, 2.5, 4.5)
                continue
            if ya < -39:
                fill_block(xa, ya, xb, yb, 2.5, 5.0, trim_p=0.3)
            else:
                fill_block(xa, ya, xb, yb, 2.8, 6.5, trim_p=0.18)
    # the far city (taller toward the back) and the near city (low, it sits in front of the lanes)
    for gx in range(int(X0), int(X1), 18):
        for gy in range(56, int(Y1), 18):
            if (abs(gy - 64) < 9) or any(abs(gy - y) < 9 for y in (100, 150, 205, 265, 330, 400, 470)):
                continue
            if any(abs(gx + 9 - x) < 9 for x in (-200, -136, -49, 35, 124, 210, 270, -300, -380, -450, 330, 400, 470)):
                continue
            far = min(1.0, (gy - 56) / 200.0)
            h = rng.uniform(8, 18) + far * rng.uniform(10, 55)
            if 120 < gx < 210 and gy < 80:
                h = rng.uniform(6, 10)
            w, d = rng.uniform(8, 15), rng.uniform(8, 15)
            city_building(gx + 1, gy + 1, gx + 1 + w, gy + 1 + d, h)
    for gx in range(int(X0), int(X1), 16):
        for gy in range(int(Y0), -42, 16):
            if any(abs(gy + 8 - y) < 9 for y in (-64, -100, -140, -200, -260, -330)):
                continue
            if any(abs(gx + 8 - x) < 8 for x in (-200, -136, -49, 35, 124, 210, 270, -300, -380, -450, 330, 400, 470)):
                continue
            if 118 < gx < 212 and gy > -60:
                continue
            near = min(1.0, (-42 - gy) / 120.0)
            h = rng.uniform(2.5, 5.5) + near * rng.uniform(0, 8 if big else 3)
            city_building(gx + 1, gy + 1, gx + rng.uniform(9, 14), gy + rng.uniform(9, 14), h, win_p=0.15)
    # the Cell's relay at the start: a low building with a lime trim and a dish
    city_building(-166, -30, -154, -20, 5.0, c=(0.40, 0.30, 0.34), trim_p=0.0)
    roof_trim(-165.8, -29.8, -154.2, -20.2, 5.15, LIME, w=0.45)
    beam((-160, -25, 5), (-160, -25, 10), 0.3, (0.3, 0.3, 0.32))
    box(-161.5, -26.5, 10, -158.5, -23.5, 10.6, LIME, facet=False)
    # the target Site: Meridian Depot 15 at the right end of the link, on its own plaza
    SOLID.face([(124, -34, 0.03), (210, -34, 0.03), (210, 44, 0.03), (124, 44, 0.03)], (0.27, 0.25, 0.28), rid())
    for (a, b) in (((125, -33), (209, -33)), ((209, -33), (209, 43)), ((125, 43), (125, -33))):
        strip(NEON, a, b, 0.5, 0.06, (1.0, 0.5, 0.1))
    before = len(SOLID.bm.verts), len(NEON.bm.verts), len(WIN.bm.verts)
    objs0 = set(bpy.data.objects)
    depot()
    s, dx, dy = 0.75, 166.0, 18.0
    for acc, m in ((SOLID, before[0]), (NEON, before[1]), (WIN, before[2])):
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            v.co.x, v.co.y, v.co.z = v.co.x * s + dx, v.co.y * s + dy, v.co.z * s
    for o in set(bpy.data.objects) - objs0:
        o.location = (o.location[0] * s + dx, o.location[1] * s + dy, o.location[2] * s)
        o.scale = (s, s, s)


def c_node_world():
    nodes = {"start": (START[0], START[1]), "final": FINAL}
    for l, layer in enumerate(C_LAYERS):
        for i, (k, r) in enumerate(layer):
            nodes["%d_%d" % (l + 1, r)] = (LX[l], ROWS[r])
    return nodes


def c_edge_paths():
    """Manhattan traces: along the source lane to the gap's cross street, across, then along the target lane.
    Edges that share a stretch of cross street get their own track (offset) so every link stays traceable."""
    out = []
    xs_l = [START[0]] + LX + [FINAL[0]]
    for g, edges in enumerate(C_EDGES):
        xa, xb, xc = xs_l[g], xs_l[g + 1], CROSS[g]
        spans = []
        for (ra, rb) in edges:
            ya = ROWS[ra] if g > 0 else START[1]
            yb = ROWS[rb] if g < 6 else FINAL[1]
            spans.append((ra, rb, ya, yb))
        tracks = []
        for idx, (ra, rb, ya, yb) in enumerate(spans):
            lo, hi = min(ya, yb), max(ya, yb)
            t = 0
            while any(tt == t and not (hi <= l2 + 0.1 or lo >= h2 - 0.1) for (tt, l2, h2) in tracks):
                t += 1
            tracks.append((t if ya != yb else -1, lo, hi))
        for idx, (ra, rb, ya, yb) in enumerate(spans):
            t = tracks[idx][0]
            off = [0.0, -2.6, 2.6, -5.2][t] if ya != yb else 0.0
            x = xc + off
            pts = [(xa, ya), (x - 1.5, ya), (x, ya - 1.5 if yb < ya else ya + 1.5)] if ya != yb else [(xa, ya), (xb, yb)]
            if ya != yb:
                pts += [(x, yb + 1.5 if yb < ya else yb - 1.5), (x + 1.5, yb), (xb, yb)]
            a = "start" if g == 0 else "%d_%d" % (g, ra)
            b = "final" if g == 6 else "%d_%d" % (g + 1, rb)
            out.append((a, b, pts))
    return out


# =================================================================== B: TOWER (building climb)
TW, TH, TD, GAP = 14.0, 5.8, 6.4, 1.8
B_LAYERS = [
    ["router", "router", "router", "router"],
    ["router", "terminal", "router", "router"],
    ["modem", "elite", "router"],
    ["router", "rack", "terminal"],
    ["elite", "modem", "terminal"],
    ["router", "elite"],
    ["rack"],
]
CONT_COLS = [(0.72, 0.18, 0.12), (0.16, 0.36, 0.62), (0.15, 0.5, 0.48), (0.86, 0.42, 0.10), (0.8, 0.78, 0.72), (0.5, 0.52, 0.2)]
ROOM_LIGHT = {"router": (1.0, 0.78, 0.5), "elite": (1.0, 0.35, 0.15), "terminal": (0.45, 1.0, 0.6), "modem": (0.35, 0.65, 1.0), "rack": (1.0, 0.62, 0.15)}


def room_box(t, i):
    n = len(B_LAYERS[t])
    width = n * TW + (n - 1) * GAP
    x0 = -width / 2 + i * (TW + GAP)
    z0 = t * TH
    yf = t * 0.9  # each tier steps back a little
    return x0, yf, z0, x0 + TW, yf + TD, z0 + TH - 0.3


def corrugate_x(x0, x1, y, z0, z1, col, bid, n, out=-1):
    for k in range(1, n):
        xx = x0 + (x1 - x0) * k / n
        SOLID.face([(xx - 0.18, y + out * 0.06, z0 + 0.25), (xx + 0.18, y + out * 0.06, z0 + 0.25), (xx + 0.18, y + out * 0.06, z1 - 0.25),
                    (xx - 0.18, y + out * 0.06, z1 - 0.25)], col, bid)


def room(t, i, kind):
    x0, y0, z0, x1, y1, z1 = room_box(t, i)
    c = CONT_COLS[(t * 3 + i * 5 + 1) % len(CONT_COLS)] if kind != "rack" or t < 6 else (0.86, 0.42, 0.10)
    dark = tuple(v * 0.45 for v in c)
    inner = tuple(v * 0.32 + 0.06 for v in c)
    w = 0.35
    bid = box(x0, y0, z0, x1, y1, z0 + w, c, facet=False)               # floor
    box(x0, y0, z1 - w, x1, y1, z1, c, facet=False, bid=bid)             # roof
    box(x0, y1 - w, z0, x1, y1, z1, c, bid=bid)                          # back wall
    box(x0, y0, z0, x0 + w, y1, z1, c, facet=False, bid=bid)             # end doors
    box(x1 - w, y0, z0, x1, y1, z1, c, facet=False, bid=bid)
    # the frame posts and the cut edge of the front wall (shows it is a cutaway)
    for x in (x0, x1 - 0.5):
        box(x, y0 - 0.15, z0, x + 0.5, y0 + 0.35, z1, dark, facet=False, bid=bid)
    box(x0, y0 - 0.15, z1 - 0.55, x1, y0 + 0.35, z1, dark, facet=False, bid=bid)
    box(x0, y0 - 0.15, z0, x1, y0 + 0.35, z0 + 0.5, dark, facet=False, bid=bid)
    # the interior: dim corrugated back wall, a ceiling light strip, floor plates
    ib = rid()
    SOLID.face([(x0 + w, y1 - w - 0.02, z0 + w), (x1 - w, y1 - w - 0.02, z0 + w), (x1 - w, y1 - w - 0.02, z1 - w), (x0 + w, y1 - w - 0.02, z1 - w)], inner, ib)
    corrugate_x(x0 + w, x1 - w, y1 - w - 0.02, z0 + w, z1 - w, tuple(v * 0.8 for v in inner), ib, 12)
    lc = ROOM_LIGHT[kind]
    NEON.face([(x0 + 1.5, y0 + 1.2, z1 - w - 0.02), (x1 - 1.5, y0 + 1.2, z1 - w - 0.02), (x1 - 1.5, y0 + 1.7, z1 - w - 0.02), (x0 + 1.5, y0 + 1.7, z1 - w - 0.02)],
              lc, (0, 0, 0))
    # warm light pool on the floor
    NEON.face([(x0 + 2, y0 + 0.6, z0 + w + 0.02), (x1 - 2, y0 + 0.6, z0 + w + 0.02), (x1 - 2, y1 - 1.0, z0 + w + 0.02), (x0 + 2, y1 - 1.0, z0 + w + 0.02)],
              tuple(v * 0.12 for v in lc), (0, 0, 0))
    zf = z0 + w
    cx = (x0 + x1) / 2
    if kind in ("router", "elite"):
        # crates + a security cabinet; the elite room has a hulking drone frame with a red eye
        for k in range(rng.choice([2, 3])):
            bx = x0 + 1.2 + k * 2.4
            box(bx, y1 - 2.6, zf, bx + 2.0, y1 - 0.6, zf + rng.choice([1.4, 2.0]), rng.choice([(0.45, 0.32, 0.2), (0.3, 0.3, 0.34)]))
        box(x1 - 3.0, y1 - 2.0, zf, x1 - 1.0, y1 - 0.6, zf + 3.6, (0.2, 0.2, 0.24))
        NEON.face([(x1 - 2.8, y1 - 2.05, zf + 2.6), (x1 - 1.2, y1 - 2.05, zf + 2.6), (x1 - 1.2, y1 - 2.05, zf + 3.1), (x1 - 2.8, y1 - 2.05, zf + 3.1)],
                  (0.5, 0.9, 1.0) if kind == "router" else RED, (0, 0, 0))
        if kind == "elite":
            box(cx - 2.0, y1 - 3.6, zf, cx + 2.0, y1 - 1.0, zf + 1.0, (0.18, 0.17, 0.2))
            box(cx - 1.6, y1 - 3.2, zf + 1.0, cx + 1.6, y1 - 1.2, zf + 4.0, (0.86, 0.42, 0.10))
            box(cx - 1.0, y1 - 3.0, zf + 4.0, cx + 1.0, y1 - 1.4, zf + 4.8, (0.2, 0.2, 0.22))
            NEON.face([(cx - 0.6, y1 - 3.25, zf + 3.0), (cx + 0.6, y1 - 3.25, zf + 3.0), (cx + 0.6, y1 - 3.25, zf + 3.6), (cx - 0.6, y1 - 3.25, zf + 3.6)], RED, (0, 0, 0))
    elif kind == "terminal":
        box(cx - 3.0, y1 - 2.4, zf, cx + 3.0, y1 - 0.8, zf + 1.6, (0.25, 0.24, 0.28))
        box(cx - 2.2, y1 - 1.6, zf + 1.6, cx + 2.2, y1 - 1.2, zf + 3.6, (0.12, 0.12, 0.14))
        NEON.face([(cx - 2.0, y1 - 1.65, zf + 1.8), (cx + 2.0, y1 - 1.65, zf + 1.8), (cx + 2.0, y1 - 1.65, zf + 3.4), (cx - 2.0, y1 - 1.65, zf + 3.4)], (0.3, 1.0, 0.5), (0, 0, 0))
        box(x0 + 1.0, y1 - 2.0, zf, x0 + 2.6, y1 - 0.6, zf + 2.4, (0.3, 0.3, 0.34))
    elif kind == "modem":
        for s in (x0 + 1.0, x1 - 4.0):
            box(s, y1 - 1.6, zf, s + 3.0, y1 - 0.6, zf + 4.0, (0.28, 0.24, 0.22), facet=False)
            for q in range(3):
                NEON.face([(s + 0.2, y1 - 1.65, zf + 0.8 + q * 1.2), (s + 2.8, y1 - 1.65, zf + 0.8 + q * 1.2), (s + 2.8, y1 - 1.65, zf + 1.0 + q * 1.2),
                           (s + 0.2, y1 - 1.65, zf + 1.0 + q * 1.2)], rng.choice([PINK, CYAN, AMBER, (0.5, 1, 0.5)]), (0, 0, 0))
        NEON.face([(cx - 1.8, y1 - w - 0.05, zf + 2.6), (cx + 1.8, y1 - w - 0.05, zf + 2.6), (cx + 1.8, y1 - w - 0.05, zf + 4.4), (cx - 1.8, y1 - w - 0.05, zf + 4.4)],
                  (0.3, 0.55, 1.0), (0, 0, 0))
    elif kind == "rack":
        n = 4 if t < 6 else 5
        for k in range(n):
            bx = x0 + 1.0 + k * (TW - 2.0) / n
            box(bx, y1 - 2.6, zf, bx + (TW - 2.0) / n - 0.5, y1 - 0.8, zf + 4.4, (0.14, 0.13, 0.15))
            for q in range(6):
                for p in range(2):
                    NEON.face([(bx + 0.3 + p * 0.6, y1 - 2.65, zf + 0.6 + q * 0.62), (bx + 0.6 + p * 0.6, y1 - 2.65, zf + 0.6 + q * 0.62),
                               (bx + 0.6 + p * 0.6, y1 - 2.65, zf + 0.85 + q * 0.62), (bx + 0.3 + p * 0.6, y1 - 2.65, zf + 0.85 + q * 0.62)],
                              AMBER if (q + p + k) % 3 else (0.4, 1.0, 0.5), (0, 0, 0))
    if WALLS:  # the closed front wall (its own rng state, so the city stays identical to the cutaway render)
        _st = rng.getstate()
        fb = rid()
        box(x0, y0 - 0.2, z0, x1, y0 + 0.05, z1, c, bid=fb)
        corrugate_x(x0, x1, y0 - 0.2, z0, z1, dark, fb, 10)
        rng.setstate(_st)
    return x0, y0, z0, x1, y1, z1


def tower_scene():
    big = VIEW == "anim"
    X0, X1 = (-420, 420) if big else (-220, 220)
    Y0, Y1 = (-380, 460) if big else (-160, 330)
    box(X0, Y0, -1, X1, Y1, 0, ASPH, facet=False)
    # the street in front, the moat-side road and the city grid
    lane_street((X0, -18.0), (X1, -18.0), 14.0, AMBER, CYAN, traffic=14, dim=0.2)
    for y in (40.0, 90.0, 150.0, 215.0, 290.0) + ((370.0, 440.0, -80.0, -150.0, -230.0, -300.0) if big else (-80.0,)):
        lane_street((X0, y), (X1, y), 10.0, rng.choice([AMBER, (0.75, 0.35, 1.0), CYAN, (0.3, 1.0, 0.6)]), CYAN, traffic=8, dim=0.14)
    for x in (-130.0, -70.0, 70.0, 130.0, -200.0, 200.0) + ((-280.0, 280.0, -360.0, 360.0) if big else ()):
        lane_street((x, Y0), (x, Y1), 9.0, rng.choice([AMBER, (0.75, 0.35, 1.0), CYAN]), CYAN, traffic=6, dim=0.12)
    # plaza around the keep with the orange ring line, and the moat edge
    SOLID.face([(-48, -10, 0.03), (48, -10, 0.03), (48, 30, 0.03), (-48, 30, 0.03)], (0.26, 0.25, 0.28), rid())
    strip(NEON, (-47, -9.5), (47, -9.5), 0.5, 0.06, (1.0, 0.5, 0.1))
    # the keep: 7 tiers of rooms
    rooms = {}
    for t, layer in enumerate(B_LAYERS):
        for i, kind in enumerate(layer):
            rooms["%d_%d" % (t + 1, i)] = room(t, i, kind)
        # ladders in the gaps + a catwalk lip on the tier edge
        n = len(layer)
        width = n * TW + (n - 1) * GAP
        for i in range(n - 1):
            gx = -width / 2 + (i + 1) * TW + i * GAP + GAP / 2
            for s in (-0.5, 0.5):
                beam((gx + s, t * 0.9 + 0.2, t * TH), (gx + s, t * 0.9 + 0.2, (t + 1) * TH), 0.16, (0.24, 0.24, 0.26))
            for k in range(1, int(TH / 0.7)):
                beam((gx - 0.5, t * 0.9 + 0.2, t * TH + k * 0.7), (gx + 0.5, t * 0.9 + 0.2, t * TH + k * 0.7), 0.1, (0.24, 0.24, 0.26))
        # hazard lip along the top of the tier
        hz = (t + 1) * TH - 0.3
        hazard_beam((-width / 2, t * 0.9 - 0.25, hz + 0.05), (width / 2, t * 0.9 - 0.25, hz + 0.05), 0.3, seg=1.6)
    # side buttresses: stacked closed containers flanking the keep (the castle walls)
    for sx in (-1, 1):
        for row in range(3):
            z = 0.0
            for lvl in range(4 - row):
                x = sx * (40 + row * 14)
                z = container(x, 14 + row * 2, z, rot90=False, L=12, W=5.0, Hh=5.2)
            if row == 0:
                beam((sx * 40, 14, z), (sx * 40, 14, z + 9), 0.3, (0.25, 0.25, 0.28))
                box(sx * 40 - 0.6, 13.4, z + 9, sx * 40 + 0.6, 14.6, z + 10, RED, facet=False)
                NEON.face([(sx * 40 - 0.7, 13.35, z + 9.1), (sx * 40 + 0.7, 13.35, z + 9.1), (sx * 40 + 0.7, 13.35, z + 9.9), (sx * 40 - 0.7, 13.35, z + 9.9)], RED, (0, 0, 0))
    # the crane keep on top: an A-frame over the cab (tier 7) with the hazard boom lowered to the right
    ztop = 7 * TH
    yb = 6 * 0.9 + TD / 2
    leg = (0.20, 0.18, 0.18)
    for sy in (-1, 1):
        beam((-12, yb + sy * 3.2, 6 * TH), (0, yb + sy * 1.0, ztop + 16), 1.1, (0.86, 0.42, 0.10))
        beam((12, yb + sy * 3.2, 6 * TH), (0, yb + sy * 1.0, ztop + 16), 1.1, (0.86, 0.42, 0.10))
    beam((-8, yb, ztop + 5.3), (8, yb, ztop + 5.3), 0.8, (0.86, 0.42, 0.10))
    hazard_beam((-26, yb, ztop + 13.5), (40, yb, ztop + 9.0), 1.3, seg=2.2)
    beam((0, yb, ztop + 16), (-26, yb, ztop + 13.5), 0.2, (0.1, 0.1, 0.1))
    beam((0, yb, ztop + 16), (40, yb, ztop + 9.0), 0.2, (0.1, 0.1, 0.1))
    box(-26, yb - 1.5, ztop + 9.0, -21, yb + 1.5, ztop + 13.0, (0.22, 0.2, 0.2))
    box(30, yb - 1.4, ztop + 7.2, 34, yb + 1.4, ztop + 9.2, (0.24, 0.22, 0.22))
    beam((32, yb, ztop + 7.2), (32, yb, ztop + 2.0), 0.15, (0.1, 0.1, 0.1))
    container(32, yb, ztop - 3.4, c=(0.16, 0.36, 0.62), L=8, W=3.4, Hh=3.4)
    box(-0.7, yb - 0.7, ztop + 16, 0.7, yb + 0.7, ztop + 17.2, RED, facet=False)
    NEON.face([(-0.75, yb - 0.75, ztop + 16.1), (0.75, yb - 0.75, ztop + 16.1), (0.75, yb - 0.75, ztop + 17.1), (-0.75, yb - 0.75, ztop + 17.1)], RED, (0, 0, 0))
    # the city around (Meridian district, orange-brown), kept off the keep's footprint and the front street
    for gx in range(int(X0), int(X1), 17):
        for gy in range(int(Y0), int(Y1), 17):
            cxg, cyg = gx + 8.5, gy + 8.5
            if -62 < cxg < 62 and -30 < cyg < 36:
                continue
            if abs(cyg + 18) < 12 or any(abs(cyg - y) < 9 for y in (40, 90, 150, 215, 290, 370, 440, -80, -150, -230, -300)):
                continue
            if any(abs(cxg - x) < 9 for x in (-130, -70, 70, 130, -200, 200, -280, 280, -360, 360)):
                continue
            far = min(1.0, max(0.0, (gy - 30) / 220.0))
            side = min(1.0, abs(cxg) / 150.0)
            if gy < -30 and abs(cxg) < 125:
                continue
            if gy < -30:
                h = rng.uniform(3, 7) + (rng.uniform(0, 10) if big else 0)
            else:
                h = rng.uniform(7, 16) + far * rng.uniform(10, 60) + side * rng.uniform(0, 20)
            w, d = rng.uniform(8, 14), rng.uniform(8, 14)
            city_building(gx + 1, gy + 1, gx + 1 + w, gy + 1 + d, h)
    return rooms


# =================================================================== build + render
if SCENE_KIND == "street":
    street_scene()
else:
    ROOMS = tower_scene()

solid = SOLID.obj(TOON)
neon = NEON.obj(NEONM)
win = WIN.obj(WINM)
exec("\n".join(_SRC[693:783]))  # key light, world, MODES, TINT, set_mode, render, override_mat
try:
    scene.eevee.shadow_pool_size = "1024"
except Exception:
    pass
_ov0 = override_mat
DMAX = 1500.0 if VIEW == "anim" else 700.0


def override_mat(kind):
    m = _ov0(kind)
    if kind == "depth":
        for n in m.node_tree.nodes:
            if n.type == "MAP_RANGE":
                n.inputs["From Max"].default_value = DMAX
    return m

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 6000


def ease(t):
    return t * t * (3 - 2 * t)


def cam_pose(f):
    """Camera for frame f (-1 = the still). Returns (location, target, lens)."""
    if SCENE_KIND == "street":
        fin = (Vector((22.0, -230.0, 292.0)), Vector((22.0, 8.0, 0.0)), 35.0)
        start = (Vector((12.0 + 520 * 0.62, -520 * 0.62, 700.0)), Vector((40.0, 30.0, 0.0)), 35.0)
    else:
        fin = (Vector((0.0, -158.0, 36.0)), Vector((0.0, 0.0, 28.5)), 50.0)
        start = (Vector((300.0, -330.0, 420.0)), Vector((0.0, 10.0, 18.0)), 40.0)
    if f < 0:
        return fin
    t = ease(f / (NF - 1))
    # arc in: the location eases along a curve that drops late (swoop), the target settles early
    tl = t ** 0.8
    loc = start[0].lerp(fin[0], tl)
    loc.z = start[0].z + (fin[0].z - start[0].z) * (t ** 0.65)
    tgt = start[1].lerp(fin[1], min(1.0, t * 1.4))
    lens = start[2] + (fin[2] - start[2]) * t
    return loc, tgt, lens


NF = 10


def set_cam(f):
    loc, tgt, lens = cam_pose(f)
    cam.location = loc
    cam_data.lens = lens
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()


def proj(p, w=1920, h=1080):
    v = world_to_camera_view(scene, cam, Vector(p))
    return (round(v.x * w, 2), round((1 - v.y) * h, 2))


def anchors():
    A = {}
    if SCENE_KIND == "street":
        nodes = c_node_world()
        A["nodes"] = {}
        for k, (x, y) in nodes.items():
            r = 6.5 if k not in ("start", "final") else 8.0
            A["nodes"][k] = dict(c=proj((x, y, 0.1)), d=[proj((x - r, y, 0.1)), proj((x, y + r, 0.1)), proj((x + r, y, 0.1)), proj((x, y - r, 0.1))],
                                 up=proj((x, y, 7.0)))
        A["edges"] = [dict(a=a, b=b, pts=[proj((x, y, 0.12)) for (x, y) in pts]) for (a, b, pts) in c_edge_paths()]
        A["layers"] = [c_layer for c_layer in [[(k, r) for (k, r) in L_] for L_ in C_LAYERS]]
        A["site"] = proj((166.0, 30.0, 10.0))
        A["relay"] = proj((-160.0, -25.0, 10.0))
        A["px_per_unit"] = proj((10.0, 0, 0))[0] - proj((0.0, 0, 0))[0]
    else:
        A["rooms"] = {}
        for k, (x0, y0, z0, x1, y1, z1) in ROOMS.items():
            A["rooms"][k] = dict(rect=[proj((x0, y0, z0)), proj((x1, y0, z0)), proj((x1, y0, z1)), proj((x0, y0, z1))],
                                 c=proj(((x0 + x1) / 2, y0 + 0.5, z0 + 2.9)), floor=proj(((x0 + x1) / 2, y0, z0 + 0.35)),
                                 ceil=proj(((x0 + x1) / 2, y0, z1)), xl=proj((x0, y0, z0 + 0.2)), xr=proj((x1, y0, z0 + 0.2)))
        A["layers"] = B_LAYERS
        A["crane_top"] = proj((0.0, 6 * 0.9 + TD / 2, 7 * TH + 16.5))
    return A


def passes(tag):
    set_mode("night")
    render(os.path.join(OUTDIR, "%s_beauty_night.png" % tag))
    blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
    solid.data.materials[0] = blackm
    set_mode("night")
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    render(os.path.join(OUTDIR, "%s_glow_night.png" % tag))
    solid.data.materials[0] = TOON
    ns = scene.eevee.taa_render_samples
    scene.eevee.taa_render_samples = 4
    for kind in ("normal", "id", "depth"):
        bpy.context.view_layer.material_override = override_mat(kind)
        bg.inputs["Color"].default_value = (1, 1, 1, 1) if kind == "depth" else (0, 0, 0, 1)
        render(os.path.join(OUTDIR, "%s_%s.png" % (tag, kind)))
    bpy.context.view_layer.material_override = None
    scene.eevee.taa_render_samples = ns


base = SCENE_KIND + ("_walls" if WALLS else "")
if VIEW in ("still", "preview"):
    set_cam(-1)
    json.dump(anchors(), open(os.path.join(OUTDIR, base + "_anchors.json"), "w"))
    passes(base)
else:
    allA = []
    frames = range(NF) if (SCENE_KIND == "street" or WALLS) else [NF - 1]
    for f in frames:
        set_cam(f)
        allA.append(anchors())
        passes("%s_f%02d" % (base, f))
    json.dump(allA, open(os.path.join(OUTDIR, base + "_anim_anchors.json"), "w"))
print("DONE", flush=True)
