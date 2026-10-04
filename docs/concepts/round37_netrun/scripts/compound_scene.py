"""Round 35: Meridian HQ as a RAID-STYLE OVERHEAD COMPOUND (the boss run alternative to the climb).

blender -b --factory-startup --python compound_scene.py -- <outdir> <frame|-1> [preview]

The container castle seen from above with the city's iso azimuth (45 deg) at a steeper 55 deg elevation, so it reads like
the raid view. Container walls with a gate, a moat, a rail yard with a freight train on the east side, the gantry crane
(the keep) straddling the yard with its boom reaching over the wall to the track, and MANIFEST CONTROL (the Central
Server's building) under the crane. Moving parts (train, trolley + the container it carries) are built LAST, so the
static compound is identical in every frame (seeded rng order). Frame f in 0..NF-1 sets:
  train   y = TRAIN_Y0 + f * TRAIN_STEP           (it rolls north; two node flatcars ride on it)
  trolley x = lerp(yard, track) over the frames  (the crane carries a node container from the yard to the train)
Writes passes + compound_anchors_fXX.json (node screen positions at 1920 x 1080).
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, FRAME = _argv[0], int(_argv[1])
PREVIEW = len(_argv) > 2
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
_saved = sys.argv
sys.argv = ["blender", "--", "meridian_regular", OUTDIR]
exec("\n".join(_SRC[0:314]))
sys.argv = _saved
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 0.0
exec("\n".join(_SRC[505:523]))  # container()
rng = random.Random(3570)
os.makedirs(OUTDIR, exist_ok=True)
scene.render.resolution_x, scene.render.resolution_y = (1280, 720) if PREVIEW else (2880, 1620)
scene.eevee.taa_render_samples = 8 if PREVIEW else 20
MER = (0.86, 0.42, 0.10)
CCOLS = [(0.72, 0.18, 0.12), (0.16, 0.36, 0.62), (0.15, 0.5, 0.48), MER, (0.8, 0.78, 0.72), (0.5, 0.52, 0.2)]
NF = 8
TRAIN_X = 92.0
TRAIN_Y0, TRAIN_STEP = -46.0, 7.0
YARD_PICK = (34.0, 18.0)


def cc(i):
    return CCOLS[i % len(CCOLS)]


def ground():
    box(-400, -400, -1, 400, 400, 0, (0.15, 0.15, 0.19), facet=False)
    # plaza inside the moat
    SOLID.face([(-74, -58, 0.02), (74, -58, 0.02), (74, 58, 0.02), (-74, 58, 0.02)], (0.27, 0.25, 0.28), rid())
    # the moat: dark faceted water ring with orange glints
    for (x0, y0, x1, y1) in ((-84, -68, 84, -58), (-84, 58, 84, 68), (-84, -58, -74, 58), (74, -58, 84, 58)):
        SOLID.face([(x0, y0, -0.4), (x1, y0, -0.4), (x1, y1, -0.4), (x0, y1, -0.4)], (0.12, 0.22, 0.36), rid())
        for k in range(40):
            gx, gy = rng.uniform(x0, x1), rng.uniform(y0, y1)
            NEON.face([(gx, gy, -0.3), (gx + 1.5, gy, -0.3), (gx + 1.5, gy + 0.3, -0.3), (gx, gy + 0.3, -0.3)], (1.0, 0.5, 0.15), (0, 0, 0))
    # the drawbridge at the gate (south)
    box(-7, -70, 0, 7, -56, 0.6, (0.32, 0.24, 0.18), facet=False)
    for x in (-7, 7):
        strip(NEON, (x, -70), (x, -56), 0.3, 0.7, AMBER)
    # city streets around
    for y in (-96.0, 96.0, 160.0, -160.0):
        strip(NEON, (-400, y), (400, y), 9.0, 0.02, (0.05, 0.04, 0.02))
        strip(NEON, (-400, y), (400, y), 0.5, 0.04, AMBER)
    for x in (-110.0, 130.0, -180.0, 200.0):
        strip(NEON, (x, -400), (x, 400), 8.0, 0.02, (0.03, 0.04, 0.05))
        strip(NEON, (x, -400), (x, 400), 0.5, 0.04, CYAN)
    strip(NEON, (0, -400), (0, -70), 10.0, 0.02, (0.06, 0.04, 0.02))
    strip(NEON, (0, -400), (0, -70), 0.6, 0.04, AMBER)


def walls():
    """Container walls, two high, with corner towers three high; the gate gap in the south wall."""
    i = 0
    for y in (-54.0, 54.0):
        for x in range(-66, 67, 12):
            if y < 0 and -12 < x < 12:
                continue
            z = 0
            for lvl in range(2 if abs(x) < 60 else 3):
                z = container(x, y, z, c=cc(i + lvl), L=12, W=4.6, Hh=4.6)
            i += 1
    for x in (-70.0, 70.0):
        for y in range(-42, 43, 12):
            z = 0
            for lvl in range(2):
                z = container(x, y, z, rot90=True, c=cc(i + lvl), L=12, W=4.6, Hh=4.6)
            i += 1
    for x in (-14.0, 14.0):  # gate towers
        z = 0
        for lvl in range(3):
            z = container(x, -54, z, rot90=True, c=MER, L=8, W=4.6, Hh=4.6)
        box(x - 0.6, -54.6, z, x + 0.6, -53.4, z + 1.0, RED, facet=False)


def track():
    for x in (TRAIN_X - 2.2, TRAIN_X + 2.2):
        strip(SOLID, (x, -400), (x, 400), 0.5, 0.25, (0.55, 0.55, 0.6))
    for y in range(-200, 200, 3):
        strip(SOLID, (TRAIN_X - 3.2, y), (TRAIN_X + 3.2, y), 0.8, 0.12, (0.25, 0.2, 0.16))
    for y in (-30.0, 30.0):
        beam((TRAIN_X + 7, y, 0), (TRAIN_X + 7, y, 14), 0.5, (0.22, 0.22, 0.24))
        box(TRAIN_X + 5.5, y - 0.8, 14, TRAIN_X + 8.5, y + 0.8, 15.2, (0.9, 0.9, 0.85), facet=False)
        NEON.face([(TRAIN_X + 5.5, y - 0.85, 14.1), (TRAIN_X + 8.5, y - 0.85, 14.1), (TRAIN_X + 8.5, y - 0.85, 15.1), (TRAIN_X + 5.5, y - 0.85, 15.1)],
                  (1.0, 0.95, 0.8), (0, 0, 0))


ROOMS = {}


def room(key, x, y, kind, z=0.0):
    """A node 'room' in the yard: each one gets its own detailing."""
    if kind == "workshop":
        box(x - 8, y - 6, z, x + 8, y + 6, z + 6, (0.42, 0.36, 0.32))
        for k in range(3):
            NEON.face([(x - 7 + k * 5, y - 6.05, z + 1), (x - 4 + k * 5, y - 6.05, z + 1), (x - 4 + k * 5, y - 6.05, z + 4.5), (x - 7 + k * 5, y - 6.05, z + 4.5)],
                      (1.0, 0.78, 0.45), (0, 0, 0))
        top = z + 6
    elif kind == "office":
        box(x - 6, y - 5, z, x + 6, y + 5, z + 9, (0.36, 0.38, 0.46))
        windows(x - 6, y - 5, z, x + 6, y + 5, z + 9, p=0.6, sx=2.0, sz=2.6, cols=[(0.45, 1.0, 0.6), (0.4, 0.9, 1.0)])
        beam((x + 3, y, z + 9), (x + 3, y, z + 14), 0.25, (0.3, 0.3, 0.32))
        top = z + 9
    elif kind == "kiosk":
        box(x - 5, y - 4, z, x + 5, y + 4, z + 4.5, (0.18, 0.2, 0.32))
        roof_trim(x - 5, y - 4, x + 5, y + 4, z + 4.6, (0.3, 0.55, 1.0), w=0.4)
        NEON.face([(x - 4, y - 4.05, z + 2), (x + 4, y - 4.05, z + 2), (x + 4, y - 4.05, z + 3.6), (x - 4, y - 4.05, z + 3.6)], (0.3, 0.55, 1.0), (0, 0, 0))
        top = z + 4.5
    elif kind == "racks":
        box(x - 7, y - 5, z, x + 7, y + 5, z + 5, (0.2, 0.19, 0.22))
        for k in range(6):
            NEON.face([(x - 6 + k * 2.2, y - 5.05, z + 1), (x - 5 + k * 2.2, y - 5.05, z + 1), (x - 5 + k * 2.2, y - 5.05, z + 4), (x - 6 + k * 2.2, y - 5.05, z + 4)],
                      AMBER if k % 2 else (0.4, 1.0, 0.5), (0, 0, 0))
        roof_trim(x - 7, y - 5, x + 7, y + 5, z + 5.1, AMBER, w=0.4)
        top = z + 5
    elif kind == "stack":
        zz = z
        for lvl in range(3):
            zz = container(x, y, zz, c=cc(len(ROOMS) + lvl), L=12, W=4.8, Hh=4.4)
        top = zz
    elif kind == "drones":
        SOLID.face([(x - 7, y - 7, 0.05), (x + 7, y - 7, 0.05), (x + 7, y + 7, 0.05), (x - 7, y + 7, 0.05)], (0.3, 0.3, 0.34), rid())
        for k in range(4):
            dx, dy = (k % 2) * 7 - 3.5, (k // 2) * 7 - 3.5
            box(x + dx - 1.2, y + dy - 1.2, 0.05, x + dx + 1.2, y + dy + 1.2, 1.0, MER, facet=False)
        strip(NEON, (x - 7, y - 7), (x + 7, y - 7), 0.3, 0.1, AMBER)
        strip(NEON, (x - 7, y + 7), (x + 7, y + 7), 0.3, 0.1, AMBER)
        top = 1.0
    elif kind == "pallets":
        for k in range(6):
            px, py = x - 6 + (k % 3) * 6, y - 3 + (k // 3) * 6
            box(px - 2, py - 2, z, px + 2, py + 2, z + 1.5 + (k % 2), (0.55, 0.42, 0.26))
        top = z + 2.5
    elif kind == "control":
        box(x - 9, y - 7, z, x + 9, y + 7, z + 8, (0.3, 0.28, 0.32))
        box(x - 6, y - 4, z + 8, x + 6, y + 4, z + 12, (0.86, 0.42, 0.10))
        windows(x - 9, y - 7, z, x + 9, y + 7, z + 8, p=0.7, sx=2.0, sz=2.4, cols=[(1.0, 0.66, 0.26)])
        roof_trim(x - 6, y - 4, x + 6, y + 4, z + 12.1, (1.0, 0.55, 0.12), w=0.5)
        top = z + 12
    else:
        top = z
    ROOMS[key] = (x, y, top)


def crane_static():
    """The keep: a gantry straddling the yard (legs at x -16/+16, y -22/+22), the boom running east over the wall and
    the moat to the track. Thick truss legs, hazard girders."""
    hz = 34
    leg = (0.20, 0.18, 0.18)
    for sx in (-16, 16):
        for sy in (-22, 22):
            beam((sx, sy, 0), (sx, sy, hz), 3.0, leg)
        beam((sx, -22, 6), (sx, 22, 26), 1.0, leg)
        beam((sx, 22, 6), (sx, -22, 26), 1.0, leg)
        beam((sx, -22, hz - 4), (sx, 22, hz - 4), 1.6, leg)
    for sy in (-6, 6):
        hazard_beam((-24, sy, hz + 1), (TRAIN_X + 6, sy, hz + 1), 3.2, seg=3.0)
    for x in range(-24, int(TRAIN_X) + 7, 8):
        beam((x, -6, hz + 1), (x, 6, hz + 1), 1.0, leg)
    box(-26, -8, hz - 1, -18, 8, hz + 6, (0.24, 0.22, 0.22))  # counterweight + machine house
    for sx in (-24, TRAIN_X + 6):
        for sy in (-6, 6):
            box(sx - 0.8, sy - 0.8, hz + 2.6, sx + 0.8, sy + 0.8, hz + 3.8, RED, facet=False)


def moving(f):
    """Train + trolley + the carried container. Built last; returns their node positions."""
    out = {}
    ty = TRAIN_Y0 + f * TRAIN_STEP
    # locomotive + 4 flatcars, two carry node containers
    box(TRAIN_X - 2.8, ty + 26, 0.6, TRAIN_X + 2.8, ty + 38, 5.4, MER)
    for k in range(4):
        NEON.face([(TRAIN_X - 2.85, ty + 27 + k * 2.6, 3.0), (TRAIN_X - 2.85, ty + 28.4 + k * 2.6, 3.0), (TRAIN_X - 2.85, ty + 28.4 + k * 2.6, 4.2),
                   (TRAIN_X - 2.85, ty + 27 + k * 2.6, 4.2)], AMBER if k % 2 else (0.06, 0.05, 0.05), (0, 0, 0))
    NEON.face([(TRAIN_X - 2, ty + 38.05, 3.6), (TRAIN_X + 2, ty + 38.05, 3.6), (TRAIN_X + 2, ty + 38.05, 4.6), (TRAIN_X - 2, ty + 38.05, 4.6)], WHITE, (0, 0, 0))
    for k in range(4):
        y0 = ty + 12 - k * 14
        box(TRAIN_X - 2.6, y0, 0.6, TRAIN_X + 2.6, y0 + 12.5, 1.6, (0.28, 0.26, 0.26), facet=False)
        if k in (0, 2):
            container(TRAIN_X, y0 + 6.25, 1.6, rot90=True, c=(0.16, 0.36, 0.62) if k == 0 else (0.72, 0.18, 0.12), L=11, W=4.4, Hh=4.2)
            out["train_%d" % k] = (TRAIN_X, y0 + 6.25, 5.8)
    # trolley on the boom: from the yard pick to the track over the frames, the container hangs under it
    t = f / (NF - 1)
    e = t * t * (3 - 2 * t)
    tx = YARD_PICK[0] + (TRAIN_X - YARD_PICK[0]) * e
    lift = 4.4 + 18 * math.sin(math.pi * e)
    hz = 34
    box(tx - 3, -7, hz + 2.6, tx + 3, 7, hz + 5, (0.24, 0.22, 0.22))
    for (cx, cy) in ((tx - 2, -1.5), (tx + 2, -1.5), (tx - 2, 1.5), (tx + 2, 1.5)):
        beam((cx, cy, hz), (cx, cy, lift + 4.4), 0.2, (0.1, 0.1, 0.1))
    container(tx, 0, lift, rot90=True, c=(0.5, 0.52, 0.2), L=11, W=4.4, Hh=4.4)
    out["crane"] = (tx, 0.0, lift + 4.4)
    return out


# ------------------------------------------------------------------ build
ground()
walls()
track()
LAYOUT = [  # key, x, y, kind  (node rooms in the yard; south = the gate side)
    ("1_0", -44, -36, "pallets"), ("1_1", -14, -40, "workshop"), ("1_2", 22, -38, "stack"), ("1_3", 50, -36, "drones"),
    ("2_0", -50, -12, "stack"), ("2_1", -26, -16, "office"), ("2_2", 44, -12, "kiosk"),
    ("3_0", -48, 14, "racks"), ("3_1", -24, 22, "stack"), ("3_2", 52, 16, "workshop"),
    ("4_0", -48, 38, "office"), ("4_1", 40, 40, "stack"),
    ("7_0", -4, 40, "control"),
]
for k, x, y, kind in LAYOUT:
    room(k, x, y, kind)
crane_static()
# the yard stack the crane picks from (empty slot once the pick is lifted)
box(YARD_PICK[0] - 6, YARD_PICK[1] - 2.4, 0, YARD_PICK[0] + 6, YARD_PICK[1] + 2.4, 0.3, (0.3, 0.28, 0.3), facet=False)
MOV = moving(max(0, FRAME))
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
cam_data.ortho_scale = 296.0
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 8000
EL = math.radians(55.0)
DIR = Vector((-math.cos(EL) / math.sqrt(2), -math.cos(EL) / math.sqrt(2), math.sin(EL)))
TGT = Vector((4.0, 10.0, 0.0))
cam.location = TGT + DIR * 2000.0
cam.rotation_euler = (-DIR).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()


def proj(p):
    v = world_to_camera_view(scene, cam, Vector(p))
    return (round(v.x * 1920, 2), round((1 - v.y) * 1080, 2))


A = {"nodes": {}}
for k, (x, y, top) in ROOMS.items():
    A["nodes"][k] = dict(c=proj((x, y, top + 0.2)), ground=proj((x, y, 0.1)))
for k, (x, y, z) in MOV.items():
    A["nodes"][k] = dict(c=proj((x, y, z + 0.2)), ground=proj((x, y, 0.1)))
A["nodes"]["start"] = dict(c=proj((0, -66, 0.8)), ground=proj((0, -66, 0.1)))
A["gate"] = proj((0, -56, 0.8))
A["kinds"] = {k: kind for k, x, y, kind in LAYOUT}
tag = "compound_f%02d" % FRAME if FRAME >= 0 else "compound"
json.dump(A, open(os.path.join(OUTDIR, tag + "_anchors.json"), "w"))
set_mode("night")
render(os.path.join(OUTDIR, "%s_beauty_night.png" % tag))
blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
solid.data.materials[0] = blackm
bg.inputs["Color"].default_value = (0, 0, 0, 1)
render(os.path.join(OUTDIR, "%s_glow_night.png" % tag))
solid.data.materials[0] = TOON
scene.eevee.taa_render_samples = 4
for kind in ("normal", "id", "depth"):
    bpy.context.view_layer.material_override = override_mat(kind)
    bg.inputs["Color"].default_value = (1, 1, 1, 1) if kind == "depth" else (0, 0, 0, 1)
    render(os.path.join(OUTDIR, "%s_%s.png" % (tag, kind)))
print("DONE", flush=True)
