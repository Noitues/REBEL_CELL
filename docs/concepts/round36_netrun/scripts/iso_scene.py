"""Round 35: ONE building language for the city map, the raid view and the netrun transit view.

blender -b --factory-startup --python iso_scene.py -- <outdir> <transit|raid|city|anim|preview>

The city is a lot grid of INDIVIDUAL buildings (one footprint per lot, alleys between them, neon roof trims, window
grids): the same kit and the same iso camera as the city map (orthographic, azimuth 45 deg from the south-west,
elevation 35 deg). The transit link is not a separate corridor any more: it is a strip of this city (four lanes along
the link, a cross street between layers), so city > raid > transit is one camera zooming in (ortho_scale 1300 > 640 > 330).

  transit / raid / city : one still per zoom (2880 x 1620 passes + anchors.json at 1920 x 1080)
  anim                  : NF frames of the pure zoom city > transit (1440 x 810), for transition 1
Shared code is exec'd from target_corps.py (round 30 copy): setup, primitives, materials, container(), depot(), passes.
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, VIEW = _argv[0], _argv[1]
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
_saved = sys.argv
sys.argv = ["blender", "--", "meridian_regular", OUTDIR]
exec("\n".join(_SRC[0:314]))
sys.argv = _saved
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 0.0
exec("\n".join(_SRC[505:523]))  # container()
exec("\n".join(_SRC[622:681]))  # depot()
rng = random.Random(3535)
os.makedirs(OUTDIR, exist_ok=True)
STILL = VIEW in ("transit", "raid", "city")
scene.render.resolution_x, scene.render.resolution_y = (2880, 1620) if STILL else ((1280, 720) if VIEW == "preview" else (1440, 810))
scene.eevee.taa_render_samples = 24 if STILL else 10
LIME = (0.83, 1.0, 0.0)
FAMS = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46),
        (0.58, 0.38, 0.22), (0.62, 0.42, 0.24)]
TRIMS = [AMBER, CYAN, PINK, (0.6, 0.4, 1.0), (0.4, 1.0, 0.6), AMBER, PINK]


def lane_street(p0, p1, w, centre, edge, traffic=6, dim=0.06, bright=1.0):
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
        ln = rng.uniform(4, 10)
        strip(NEON, a, (a[0] + ux * ln, a[1] + uy * ln), 0.2, 0.05, RED if o > 0 else WHITE)


def tower(x0, y0, x1, y1, h, far=False, trim=0.4):
    """One building on one lot: the raid view's kit (faceted box, optional setback, window grid, neon roof trim)."""
    c = rng.choice(FAMS)
    box(x0, y0, 0, x1, y1, h, c, facet=not far)
    if not far:
        windows(x0, y0, 0, x1, y1, h, p=0.3 if h > 12 else 0.2, sx=2.2, sz=3.0)
    top = h
    if h > 14 and rng.random() < 0.45:
        i = min(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.25)
        h2 = h + rng.uniform(3, 10)
        box(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, tuple(v * 1.06 for v in c), facet=not far)
        if not far:
            windows(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, p=0.25, sx=2.2, sz=3.0)
        top = h2
        x0, y0, x1, y1 = x0 + i, y0 + i, x1 - i, y1 - i
    if rng.random() < trim:
        roof_trim(x0 + 0.15, y0 + 0.15, x1 - 0.15, y1 - 0.15, top + 0.12, rng.choice(TRIMS), w=0.3)
    if not far and rng.random() < 0.3 and x1 - x0 > 4:
        cx, cy = rng.uniform(x0 + 0.8, x1 - 2.6), rng.uniform(y0 + 0.8, y1 - 2.6)
        box(cx, cy, top, cx + 1.8, cy + 1.8, top + 1.2, (0.3, 0.3, 0.34), facet=False)


def lots(x0, y0, x1, y1, hmin, hmax, lot=9.0, gap=2.6, far=False, trim=0.4):
    """Split a block into individual lots, one building each (never merged)."""
    nx = max(1, int((x1 - x0 + gap) / (lot + gap)))
    ny = max(1, int((y1 - y0 + gap) / (lot + gap)))
    wx = (x1 - x0 - gap * (nx - 1)) / nx
    wy = (y1 - y0 - gap * (ny - 1)) / ny
    for i in range(nx):
        for j in range(ny):
            a, b = x0 + i * (wx + gap), y0 + j * (wy + gap)
            if rng.random() < 0.08:
                continue  # an empty lot / plaza now and then
            ji = rng.uniform(0, 0.8)
            tower(a + ji, b + ji * 0.5, a + wx - ji * 0.4, b + wy - ji, rng.uniform(hmin, hmax), far=far, trim=trim)


# ------------------------------------------------------------------ the link (route graph = round 32's transit graph)
ROWS = [27.0, 9.0, -9.0, -27.0]
LX = [-108.0, -72.0, -36.0, 0.0, 36.0, 72.0]
START = (-146.0, -9.0)
FINAL = (110.0, -9.0)
CROSS = [-127.0, -90.0, -54.0, -18.0, 18.0, 54.0, 91.0]
SW = 7.0
C_LAYERS = [
    [("router", 0), ("router", 2), ("router", 3)],
    [("router", 0), ("terminal", 1), ("router", 3)],
    [("modem", 0), ("elite", 1), ("router", 2), ("terminal", 3)],
    [("router", 1), ("rack", 2), ("terminal", 3)],
    [("elite", 0), ("modem", 2), ("router", 3)],
    [("router", 1), ("elite", 2)],
]
C_EDGES = [
    [(2, 0), (2, 2), (2, 3)],
    [(0, 0), (0, 1), (2, 1), (3, 3)],
    [(0, 0), (1, 1), (1, 2), (3, 2), (3, 3)],
    [(0, 1), (1, 1), (1, 2), (2, 2), (3, 3)],
    [(1, 0), (2, 2), (2, 3), (3, 3)],
    [(0, 1), (2, 1), (2, 2), (3, 2)],
    [(1, 2), (2, 2)],
]
EXT = 640.0 if VIEW in ("anim", "city") else (360.0 if VIEW == "raid" else 230.0)


def build():
    box(-EXT - 100, -EXT - 100, -1, EXT + 100, EXT + 100, 0, (0.15, 0.15, 0.19), facet=False)
    # the city's street grid: E-W streets every 40 (the corridor's four lanes are four of them), N-S every 36
    ew = sorted(set([y for y in ROWS] + [45.0 + 40 * k for k in range(int(EXT / 40) + 1)] + [-45.0 - 40 * k for k in range(int(EXT / 40) + 1)]))
    ns = sorted(set(CROSS + [91.0 + 37 * k for k in range(1, int(EXT / 37) + 2)] + [-127.0 - 37 * k for k in range(1, int(EXT / 37) + 2)]))
    for y in ew:
        corr = y in ROWS
        lane_street((-EXT, y), (EXT, y), SW if corr else 8.0, AMBER if corr else rng.choice([AMBER, (0.75, 0.35, 1.0), CYAN]), CYAN,
                    traffic=int(EXT / 25), dim=0.07 if corr else 0.05, bright=0.9 if corr else 0.5)
    for x in ns:
        lane_street((x, -EXT), (x, EXT), SW, (0.75, 0.35, 1.0) if x in CROSS else rng.choice([AMBER, CYAN]), CYAN,
                    traffic=int(EXT / 30), dim=0.05, bright=0.6 if x in CROSS else 0.45)
    # blocks between streets, filled lot by lot
    for i in range(len(ns) - 1):
        for j in range(len(ew) - 1):
            x0, x1 = ns[i] + 4.5, ns[i + 1] - 4.5
            y0, y1 = ew[j] + 4.5, ew[j + 1] - 4.5
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            if 116 < cx < 200 and -40 < cy < 45:
                continue  # the Site's plaza
            if -175 < cx < -140 and -30 < cy < 0:
                continue  # the Cell's relay lot
            far = max(abs(cx), abs(cy)) > 260
            in_corr = -31 < cy < 31 and -150 < cx < 120
            if in_corr:
                lots(x0, y0, x1, y1, 2.2, 4.6, lot=8.0, trim=0.15)
            elif cy < -31:  # the camera side: low, so the lanes stay in view
                near = -31 > cy > -90 and -200 < cx < 220
                lots(x0, y0, x1, y1, 2.2, 4.0 if near else 12.0, far=far, trim=0.25)
            else:
                d = min(1.0, (cy - 31) / 160.0)
                lots(x0, y0, x1, y1, 7.0 + 8 * d, 16.0 + 34 * d, far=far)
    # the elevated transit line on the north edge of the corridor
    vz = 11.0
    for x in range(int(-EXT), int(EXT), 16):
        box(x - 0.8, 43.8, 0, x + 0.8, 46.2, vz, (0.22, 0.21, 0.26), facet=False)
    box(-EXT, 42.0, vz, EXT, 48.0, vz + 1.2, (0.30, 0.29, 0.34), facet=False)
    strip(NEON, (-EXT, 42.2), (EXT, 42.2), 0.25, vz + 1.25, CYAN)
    for k in range(4):
        tx = -60 + k * 13.5
        box(tx, 43.0, vz + 1.2, tx + 12.8, 47.0, vz + 5.0, (0.78, 0.76, 0.80))
        for q in range(5):
            NEON.face([(tx + 0.8 + q * 2.4, 42.9, vz + 2.8), (tx + 2.2 + q * 2.4, 42.9, vz + 2.8), (tx + 2.2 + q * 2.4, 42.9, vz + 4.0),
                       (tx + 0.8 + q * 2.4, 42.9, vz + 4.0)], (0.55, 0.95, 1.0), (0, 0, 0))
    # the Cell's relay at the start
    tower(-166, -26, -154, -14, 5.0)
    roof_trim(-165.8, -25.8, -154.2, -14.2, 5.2, LIME, w=0.45)
    beam((-160, -20, 5), (-160, -20, 10), 0.3, (0.3, 0.3, 0.32))
    box(-161.5, -21.5, 10, -158.5, -18.5, 10.6, LIME, facet=False)
    # the target Site: Meridian Depot 15
    SOLID.face([(120, -40, 0.03), (200, -40, 0.03), (200, 40, 0.03), (120, 40, 0.03)], (0.27, 0.25, 0.28), rid())
    before = len(SOLID.bm.verts), len(NEON.bm.verts), len(WIN.bm.verts)
    objs0 = set(bpy.data.objects)
    depot()
    s, dx, dy = 0.7, 160.0, 12.0
    for acc, m in ((SOLID, before[0]), (NEON, before[1]), (WIN, before[2])):
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            v.co.x, v.co.y, v.co.z = v.co.x * s + dx, v.co.y * s + dy, v.co.z * s
    for o in set(bpy.data.objects) - objs0:
        o.location = (o.location[0] * s + dx, o.location[1] * s + dy, o.location[2] * s)
        o.scale = (s, s, s)


def node_world():
    nodes = {"start": START, "final": FINAL}
    for l, layer in enumerate(C_LAYERS):
        for (k, r) in layer:
            nodes["%d_%d" % (l + 1, r)] = (LX[l], ROWS[r])
    return nodes


def edge_paths():
    out = []
    xs_l = [START[0]] + LX + [FINAL[0]]
    for g, edges in enumerate(C_EDGES):
        xc = CROSS[g]
        spans = []
        for (ra, rb) in edges:
            ya = ROWS[ra] if g > 0 else START[1]
            yb = ROWS[rb] if g < 6 else FINAL[1]
            spans.append((ra, rb, ya, yb))
        tracks = []
        for (ra, rb, ya, yb) in spans:
            lo, hi = min(ya, yb), max(ya, yb)
            t = 0
            if ya != yb:
                while any(tt == t and not (hi <= l2 + 0.1 or lo >= h2 - 0.1) for (tt, l2, h2) in tracks):
                    t += 1
            tracks.append((t if ya != yb else -1, lo, hi))
        for idx, (ra, rb, ya, yb) in enumerate(spans):
            t = tracks[idx][0]
            x = xc + ([0.0, -2.2, 2.2, -4.4][t] if t >= 0 else 0.0)
            if ya == yb:
                pts = [(xs_l[g], ya), (xs_l[g + 1], yb)]
            else:
                s = -1.2 if yb < ya else 1.2
                pts = [(xs_l[g], ya), (x - 1.2, ya), (x, ya + s), (x, yb - s), (x + 1.2, yb), (xs_l[g + 1], yb)]
            a = "start" if g == 0 else "%d_%d" % (g, ra)
            b = "final" if g == 6 else "%d_%d" % (g + 1, rb)
            out.append((a, b, pts))
    return out


build()
solid = SOLID.obj(TOON)
neon = NEON.obj(NEONM)
win = WIN.obj(WINM)
exec("\n".join(_SRC[693:783]))
_ov0 = override_mat


def override_mat(kind):
    m = _ov0(kind)
    if kind == "depth":
        for n in m.node_tree.nodes:
            if n.type == "MAP_RANGE":
                n.inputs["From Max"].default_value = 3000.0
    return m


cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 8000
EL = math.radians(35.0)
DIR = Vector((-math.cos(EL) / math.sqrt(2), -math.cos(EL) / math.sqrt(2), math.sin(EL)))
SCALES = {"transit": 355.0, "raid": 640.0, "city": 1300.0}
TGT = Vector((8.0, 2.0, 0.0))
NF = 9


def set_cam(scale, tgt=TGT):
    cam_data.ortho_scale = scale
    cam.location = tgt + DIR * 2000.0
    cam.rotation_euler = (-DIR).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()


def proj(p):
    v = world_to_camera_view(scene, cam, Vector(p))
    return (round(v.x * 1920, 2), round((1 - v.y) * 1080, 2))


def anchors():
    A = {"nodes": {}}
    for k, (x, y) in node_world().items():
        r = 6.0 if k not in ("start", "final") else 7.5
        A["nodes"][k] = dict(c=proj((x, y, 0.1)), d=[proj((x - r, y, 0.1)), proj((x, y + r, 0.1)), proj((x + r, y, 0.1)), proj((x, y - r, 0.1))])
    A["edges"] = [dict(a=a, b=b, pts=[proj((x, y, 0.12)) for (x, y) in pts]) for (a, b, pts) in edge_paths()]
    A["layers"] = [[(k, r) for (k, r) in L_] for L_ in C_LAYERS]
    A["site"] = proj((160.0, 22.0, 10.0))
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


if VIEW in SCALES or VIEW == "preview":
    v = "transit" if VIEW == "preview" else VIEW
    set_cam(SCALES[v])
    json.dump(anchors(), open(os.path.join(OUTDIR, "iso_%s_anchors.json" % v), "w"))
    passes("iso_%s" % v)
else:
    allA = []
    for f in range(NF):
        t = f / (NF - 1)
        e = t * t * (3 - 2 * t)
        set_cam(math.exp(math.log(1300.0) * (1 - e) + math.log(355.0) * e))
        allA.append(anchors())
        passes("iso_f%02d" % f)
    json.dump(allA, open(os.path.join(OUTDIR, "iso_anim_anchors.json"), "w"))
print("DONE", flush=True)
