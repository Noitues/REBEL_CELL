"""Round 26: the Cell's base, one model for the city map and the combat close-up. Blender 5.2 headless.

blender -b --factory-startup --python hq26.py -- rebel_cell_hq <outdir> <close|map|preview> <idea> [dispatch]
  idea : tokyo | roofs | skyline | deck | rec        (idea_cfg.py, ideas26.py)
  close: perspective close-up 2880 x 1620, night only: beauty, glow, normal, id, depth
  map  : orthographic sprite in the game's 2:1 iso projection, transparent, city buildings as holdout
The city round the base is the game's own layout (../scratch/layout/rc26.json from layout26.py), rebuilt as in round 25
(hq_scene.py); the round 24/25 pipeline (target_corps.py setup/materials/modes, heroes24/25 primitives) is exec'd.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials

import json
import idea_cfg as IC

_argv = sys.argv[sys.argv.index("--") + 1:]
JOB, OUTDIR, VIEW, IDEA = _argv[0], _argv[1], _argv[2], _argv[3]
STATE = _argv[4] if len(_argv) > 4 else ""
DISP = STATE == "dispatch"
CORP, KIND = "rebel_cell", "hq"
os.makedirs(OUTDIR, exist_ok=True)
rng = random.Random(2626 + sum(map(ord, IDEA)))
MAPRES = {"tokyo": 3600, "roofs": 3000, "skyline": 3800, "deck": 3400, "rec": 4000}
RES = {"close": (2880, 1620), "preview": (960, 540), "map": (MAPRES[IDEA], MAPRES[IDEA])}[VIEW]
scene.render.resolution_x, scene.render.resolution_y = RES
scene.eevee.taa_render_samples = 8 if VIEW == "preview" else 24
LAY = json.load(open(os.path.join(_HERE, "..", "scratch", "layout", "rc26.json")))
CFG = IC.Cfg(LAY)
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
exec(open(os.path.join(_HERE, "ideas26.py"), encoding="utf-8-sig").read())

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


def paint_roof(top, z, bid, seed):
    """Crude red paint on a roof: a ragged inset polygon (roller edge), roller stripes, drips over the front edges."""
    pr = random.Random(seed)
    n = len(top)
    cx = sum(p[0] for p in top) / n
    cy = sum(p[1] for p in top) / n
    rag = []
    for (x, y) in top:
        k = pr.uniform(0.80, 0.97)
        rag.append((cx + (x - cx) * k + pr.uniform(-0.25, 0.25), cy + (y - cy) * k + pr.uniform(-0.25, 0.25), z + 0.04))
    if DISP:  # DISPATCH re-lit the Cell's paint: it glows, and black tar slashes cross it out
        NEON.face(rag, (0.85, 0.03, 0.05), (0, 0, 0))
    else:
        tone = pr.uniform(0.82, 1.08)
        CITY.face(rag, tuple(c * tone for c in PAINT_RED), bid)
        # roller stripes: two lighter / darker bands across the roof
        for s in range(2):
            t0 = pr.uniform(0.15, 0.7)
            a, b = rag[0], rag[1 % n]
            c, d = rag[(n - 1)], rag[(n - 2) % n] if n > 3 else rag[2 % n]
            p0 = [a[i] + (c[i] - a[i]) * t0 for i in range(3)]
            p1 = [b[i] + (d[i] - b[i]) * t0 for i in range(3)]
            p2 = [b[i] + (d[i] - b[i]) * (t0 + 0.12) for i in range(3)]
            p3 = [a[i] + (c[i] - a[i]) * (t0 + 0.12) for i in range(3)]
            CITY.face([(p[0], p[1], z + 0.06) for p in (p0, p1, p2, p3)], tuple(cc * pr.uniform(0.7, 1.15) for cc in PAINT_RED), bid)
    # drips down the walls that face the camera (+x, -y world)
    for i in range(n):
        j = (i + 1) % n
        a, b = top[i], top[j]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey)
        if L < 1.5:
            continue
        nx, ny = ey / L, -ex / L
        if nx * ((a[0] + b[0]) / 2 - cx) + ny * ((a[1] + b[1]) / 2 - cy) < 0:
            nx, ny = -nx, -ny
        if nx - ny < 0.3:
            continue
        for k in range(int(L / 1.6)):
            if pr.random() < 0.45:
                continue
            t = pr.uniform(0.05, 0.95)
            px, py = a[0] + ex * t + nx * 0.07, a[1] + ey * t + ny * 0.07
            w = pr.uniform(0.18, 0.5)
            ln = pr.uniform(0.6, 4.5)
            ux, uy = ex / L * w, ey / L * w
            pts = [(px - ux, py - uy, z + 0.05), (px + ux, py + uy, z + 0.05), (px + ux * 0.5, py + uy * 0.5, z - ln), (px - ux * 0.5, py - uy * 0.5, z - ln)]
            if DISP:
                NEON.face(pts, (0.7, 0.02, 0.04), (0, 0, 0))
            else:
                CITY.face(pts, PAINT_RED, bid)
    if DISP and pr.random() < 0.55:  # tar slash
        a, c = rag[0], rag[(n // 2) % n]
        dx, dy = c[0] - a[0], c[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ox, oy = -dy / L * 0.7, dx / L * 0.7
        CITY.face([(a[0] + ox, a[1] + oy, z + 0.09), (a[0] - ox, a[1] - oy, z + 0.09), (c[0] - ox, c[1] - oy, z + 0.09), (c[0] + ox, c[1] + oy, z + 0.09)],
                  (0.04, 0.03, 0.04), bid)


PAINTED = []


def city_building(b):
    qL = b["q"]
    cxl = sum(p[0] for p in qL) / len(qL)
    cyl_ = sum(p[1] for p in qL) / len(qL)
    if CFG.removed(IDEA, cxl, cyl_):
        return
    q = [W(p) for p in qL]
    n = len(q)
    z0, h = b["z0"] * KH, b["h"] * KH
    ts = b["ts"]
    cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
    top = [(cxq + (x - cxq) * ts, cyq + (y - cyq) * ts) for (x, y) in q]
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
    if ts > 0.3 and CFG.painted(IDEA, cxl, cyl_, b["z0"] + b["h"]):
        PAINTED.append(b["key"])
        ROOF_CREW.append((top, z0 + h))
        if not HOLD_ONLY:
            paint_roof(top, z0 + h, bid, abs(b["key"]) * 31 + int(b["z0"]))
        else:
            CITY.face([(x, y, z0 + h + 0.04) for (x, y) in top], (1, 0, 0), bid)
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
              tuple(v * (0.10 + tr * 0.16) for v in col))
        nl = min(strokes, 3 + int(tr * 9))
        hr = random.Random(t["i"] * 7919 + t["j"])
        for k in range(nl):
            u = (k + 0.5) / nl * 2 - 1
            lane = u * half * 0.8 + (hr.random() - 0.5) * 0.25
            al = 0.55 + 0.35 * hr.random() + tr * 0.15
            strip(CNEON, (a[0] + nx * lane - dx * 0.35, a[1] + ny * lane - dy * 0.35), (b[0] + nx * lane + dx * 0.35, b[1] + ny * lane + dy * 0.35),
                  0.18, 0.04, tuple(min(1, v * al) for v in col))
    for t in LAY["trails"]:
        a, b = W(t["a"]), W(t["b"])
        strip(CNEON, a, b, 0.32, 0.06, tuple(t["col"]))
    fcol = tuple(LAY["fist_col"])
    for s in LAY["fist"]:  # REBEL_CELL's fist roads, as drawn on the map
        a, b = W(s["a"]), W(s["b"])
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = -dy, dx
        Hh = 0.75 * U
        e0, e1 = (a[0] - dx * Hh, a[1] - dy * Hh), (b[0] + dx * Hh, b[1] + dy * Hh)
        strip(GROUND, e0, e1, 2 * (Hh + 0.6), 0.012, (0.12, 0.10, 0.12))
        strip(CNEON, e0, e1, 2 * (Hh + 1.2), 0.02, tuple(v * 0.22 for v in fcol))
        fr = random.Random(int(a[0] * 13 + b[1] * 7))
        for k in range(12):
            u = (k + 0.5) / 12 * 2 - 1
            lane = u * Hh + (fr.random() - 0.5) * 0.4
            over = Hh * (0.4 + 0.6 * fr.random())
            strip(CNEON, (a[0] + nx * lane - dx * over, a[1] + ny * lane - dy * over), (b[0] + nx * lane + dx * over, b[1] + ny * lane + dy * over),
                  0.2, 0.045, tuple(min(1, v * (0.55 + 0.4 * fr.random())) for v in fcol))

# ------------------------------------------------------------------ the hero
build_xf(IDEAS26[IDEA], 0.0, 0.0, 45.0)
if IDEA == "roofs":
    roof_crew_world()
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

# ------------------------------------------------------------------ cameras
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 6000
DIAG = Vector((1, -1, 0)).normalized()
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
    (clx, cly, clz), (tlx, tly, tlz), lens = CAMS26[IDEA]  # local frame (idea_cfg): camera and target
    if os.environ.get("CAM26"):  # debug / framing override: "x,y,z,tx,ty,tz,lens" (local frame)
        _c = [float(v) for v in os.environ["CAM26"].split(",")]
        (clx, cly, clz), (tlx, tly, tlz), lens = _c[0:3], _c[3:6], _c[6]
    cw, tw = L2W(clx, cly), L2W(tlx, tly)
    tgt = Vector((tw[0], tw[1], tlz))
    cam.location = (cw[0], cw[1], clz)
    cam_data.lens = lens
cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()

tag = "rc26_%s%s" % (IDEA, "_dispatch" if DISP else "")
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
