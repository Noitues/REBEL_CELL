"""Round 26: one HQ model, two cameras (round 25 pipeline + heroes26.py, closer combat framing, animation frames).

Round 25 header:
Round 25: one HQ model, two cameras. Blender 5.2 headless.

blender -b --factory-startup --python hq_scene.py -- <corp>_<hq|site> <outdir> <close|map|preview> [state]
  close   : perspective combat close-up (2880 x 1620): beauty day + night, glow, normal, id, depth passes
  map     : orthographic city-map sprite, the game's iso projection (2:1, 30 deg), transparent, the city's own
            buildings as HOLDOUT so whatever stands in front of the HQ on the map also hides it here
  preview : close at 960 x 540
  state   : orbital "open" | rebel_cell "dispatch" (default: doors closed / the Cell's home)

The scene around the HQ is NOT procedural any more: ../scratch/layout/<job>.json (citydata.py) holds the city's
own street tiles (lane colours, traffic), buildings (footprint, base, height, taper), plazas, trails and the fist
roads, all converted from the game's iso screen space back to lots. 1 lot = 6 BU; heights h_px -> h * 6 / 41.64.

Shared code: the round 24 target pipeline (target_corps.py lines 1-314: setup, geometry accumulators, primitives,
materials; 505-682: container / ziggurat / depot; 694-783: lights, modes, render, data passes) is exec'd from the
copied file, then heroes24.py (round 24 regular sites + helpers) and heroes25.py (the five HQs).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = open(os.path.join(_HERE, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials

import json

_argv = sys.argv[sys.argv.index("--") + 1:]
JOB, OUTDIR = _argv[0], _argv[1]
VIEW = _argv[2] if len(_argv) > 2 else "close"
STATE = _argv[3] if len(_argv) > 3 else ""
CORP, KIND = JOB.rsplit("_", 1)
os.makedirs(OUTDIR, exist_ok=True)
rng = random.Random(2525 + sum(map(ord, JOB)))
RES = {"close": (2880, 1620), "preview": (1280, 720), "map": (2800, 2800), "mapprev": (1400, 1400), "anim": (1280, 720)}[VIEW]
scene.render.resolution_x, scene.render.resolution_y = RES
scene.eevee.taa_render_samples = 8 if VIEW == "preview" else 24
LAY = json.load(open(os.path.join(_HERE, "..", "scratch", "layout", JOB + ".json")))
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
exec(open(os.path.join(_HERE, "heroes26.py"), encoding="utf-8-sig").read())
exec(open(os.path.join(_HERE, "heroes27.py"), encoding="utf-8-sig").read())  # round 27: fortress options, Halcyon Sites

# ------------------------------------------------------------------ the city around it, from the game's layout
CITY = Acc("city")
CNEON = Acc("cneon")
CWIN = Acc("cwin")
GROUND = Acc("ground")
HOLD_ONLY = VIEW in ("map", "mapprev")
FAMS_C = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
TERR = LAY["terr"]


def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def city_building(b):
    q = [W(p) for p in b["q"]]
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
        if not HOLD_ONLY and ts >= 0.99 and h > 2.4:  # window grid on the face
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
    if not HOLD_ONLY and rng.random() < 0.42 and ts > 0.05:  # the game's neon roof trim, in the building's own ink
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
    for t in LAY["tiles"]:  # the game's street tiles + its glowing lanes (round 6 restyler rules, in lots)
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
    for s in LAY["fist"]:  # REBEL_CELL's fist roads, as drawn on the map (wide, red, many lanes)
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

# ------------------------------------------------------------------ the hero (HQ / base / Site)
def build_at(fn, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    """Run a builder around the origin, then scale and move what it added (geometry and sign objects)."""
    before = {id(a): len(a.bm.verts) for a in [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values())}
    objs0 = set(bpy.data.objects)
    fn()
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for acc in [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values()):
        m = before.get(id(acc), 0)
        acc.bm.verts.ensure_lookup_table()
        for v in acc.bm.verts[m:]:
            v.co.x = v.co.x * s + dx
            v.co.y = v.co.y * s + dy
            v.co.z *= s
    for o in set(bpy.data.objects) - objs0:
        x0, y0 = o.location[0] * s, o.location[1] * s
        o.location = (x0 * cr - y0 * sr + dx, x0 * sr + y0 * cr + dy, o.location[2] * s)
        o.rotation_euler = (o.rotation_euler[0], o.rotation_euler[1], o.rotation_euler[2] + math.radians(rot))
        o.scale = (s, s, s)


if KIND == "hq":
    HEROES26.get(CORP, HEROES25[CORP])()
else:
    # Sites: scaled onto their 6 x 6 lot block; the new Sites (front = -y) turn 45 deg to face the close-up camera
    _new = (CORP, STATE) in SITES26
    build_at(SITES26.get((CORP, STATE)) or HEROES.get((CORP, "regular")) or depot, s=0.80 if _new else (0.62 if CORP != "meridian" else 0.42),
             rot=45.0 if _new else 0.0)
if VIEW not in ("map", "mapprev"):  # every other HQ that stands in view, so the close-up shows the same skyline as the map
    _st = STATE
    for other, c in LAY.get("hqs", {}).items():
        if KIND == "hq" and other == CORP:
            continue
        if math.hypot(c[0] - CX, c[1] - CY) > LAY["radius"] - 4:
            continue
        STATE = ""
        wx, wy = W(c)
        _had_eye = bool(EYE_ACC)
        _a0 = [len(a.bm.faces) for a in ANIM_ACCS]
        build_at(HEROES26.get(other, HEROES25[other]), wx, wy)
        if EYE_ACC and not _had_eye:  # another HQ's eye: static, merged into the scene, no searchlight
            EYE_STATIC.append((EYE_ACC.pop("solid"), EYE_ACC.pop("neon")))
            EYE_ACC.pop("beam").bm.free()
    STATE = _st

exec("\n".join(_SRC[689:692]))  # solid / neon / win objects
cityo = CITY.obj(TOON)
cneono = CNEON.obj(NEONM)
cwino = CWIN.obj(WINM)
groundo = GROUND.obj(TOON)


def mat_beam():
    m = bpy.data.materials.new("beam")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    a = attr(nt, "col")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.22
    nt.links.new(a.outputs["Color"], em.inputs["Color"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    for k, v in (("surface_render_method", "BLENDED"), ("blend_method", "HASHED")):
        try:
            setattr(m, k, v)
        except Exception:
            pass
    return m


BEAMM = mat_beam()
LITM = TOON.copy()
_nt = LITM.node_tree
_em = next(n for n in _nt.nodes if n.type == "EMISSION")
_out = next(n for n in _nt.nodes if n.type == "OUTPUT_MATERIAL")
_ac = attr(_nt, "col")
_e2 = _nt.nodes.new("ShaderNodeEmission")
_e2.inputs["Strength"].default_value = 0.42
_nt.links.new(_ac.outputs["Color"], _e2.inputs["Color"])
_add = _nt.nodes.new("ShaderNodeAddShader")
_nt.links.new(_em.outputs[0], _add.inputs[0])
_nt.links.new(_e2.outputs[0], _add.inputs[1])
_nt.links.new(_add.outputs[0], _out.inputs[0])
LIT_RAMP = next(n for n in _nt.nodes if n.type == "VALTORGB")
lito = LIT.obj(LITM)
beamo = BEAM.obj(BEAMM)
for _s, _n in EYE_STATIC:
    _s.obj(TOON)
    _n.obj(NEONM)
anim_objs = [a.obj(NEONM) for a in ANIM_ACCS]
eye_objs = []
if EYE_ACC:
    eye_objs = [EYE_ACC["solid"].obj(TOON), EYE_ACC["neon"].obj(NEONM), EYE_ACC["beam"].obj(BEAMM)]
    if VIEW in ("map", "mapprev"):
        eye_objs[2].hide_render = True


def set_frame(f):
    for i, o in enumerate(anim_objs):
        o.hide_render = (i != (f % len(anim_objs)) if f >= 0 else i != 0)
    if eye_objs:
        ang = EYE_ANGLES[f % len(EYE_ANGLES)] if f >= 0 else EYE_STILL
        for o in eye_objs:
            o.rotation_euler = (0, 0, math.radians(ang))


EYE_STILL = 28.0  # the still / combat: the eye has turned toward the left of the frame
set_frame(-1)
exec("\n".join(_SRC[693:783]))  # lights, MODES, TINT, set_mode, render, override_mat
MODES["day"] = dict(MODES["daycool"])  # the approved round 11b cool day
_set_mode0 = set_mode


def set_mode(m):
    _set_mode0(m)
    for e, e0 in zip(LIT_RAMP.color_ramp.elements, RAMP.color_ramp.elements):
        e.color = tuple(e0.color)



try:
    scene.eevee.shadow_pool_size = "1024"  # big scene: a larger shadow pool keeps sun shadows clean (no blotches)
except Exception:
    pass
try:
    scene.eevee.shadow_resolution_scale = 1.0
except Exception:
    pass
for _m in MODES.values():
    _m["sign"] = KN["sign"]

# ------------------------------------------------------------------ cameras
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 5000
DIAG = Vector((1, -1, 0)).normalized()
if VIEW == "map":
    el = math.radians(30)
    ppu = 2 * 34 * math.sqrt(2) / U  # sprite rendered at 2x city px
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2800 / ppu
    ZC = 450.0 / (math.cos(el) * 34 * math.sqrt(2) / U)  # frame centre = 450 city px above the HQ's ground centre
    tgt = Vector((0, 0, ZC))
    d = Vector((DIAG.x * math.cos(el), DIAG.y * math.cos(el), math.sin(el)))
    cam.location = tgt + d * 900
else:
    # round 26: much closer; the HQ fills the gap between the wheels (the wheels may overlap it). Meridian looks
    # straight at the drawbridge (+X); the others keep the map's diagonal.
    CAMS = {"hq": {"meridian": ((1, 0), 140, 72, 18), "solace": (DIAG, 240, 84, 60), "halcyon": (DIAG, 205, 86, 50),
                   "orbital": (DIAG, 120, 70, 22), "rebel_cell": (DIAG, 215, 265, 0)},
            "site": (DIAG, 80, 54, 9)}
    dv, D, Hc, Zt = CAMS["hq"][CORP] if KIND == "hq" else CAMS["site"]
    dv = Vector((dv[0], dv[1], 0)).normalized()
    tgt = Vector((0, 0, Zt))
    cam.location = (dv.x * D, dv.y * D, Hc)
    cam_data.lens = 34
cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
bpy.context.view_layer.update()

tag = JOB + ("_" + STATE if STATE else "")
if VIEW in ("map", "mapprev"):
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
        for o in [solid, neon, win, beamo, lito] + anim_objs + eye_objs:
            o.data.materials[0] = ov
        render(os.path.join(OUTDIR, "%s_map_%s.png" % (tag, kind)))
    print("DONE", flush=True)
else:
    if VIEW == "anim":  # animation frames: beauty + glow per frame, the data passes once
        for f in range(NFRAMES):
            set_frame(f)
            set_mode("night")
            render(os.path.join(OUTDIR, "%s_f%02d_beauty_night.png" % (tag, f)))
        blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
        for o in [solid, cityo, groundo, lito] + eye_objs[:1]:
            o.data.materials[0] = blackm
        for f in range(NFRAMES):
            set_frame(f)
            set_mode("night")
            bg.inputs["Color"].default_value = (0, 0, 0, 1)
            render(os.path.join(OUTDIR, "%s_f%02d_glow_night.png" % (tag, f)))
        for o in [solid, cityo, groundo, lito] + eye_objs[:1]:
            o.data.materials[0] = TOON
        set_frame(-1)
        beamo.hide_render = True
        if eye_objs:
            eye_objs[2].hide_render = True
        bg.inputs["Color"].default_value = (0, 0, 0, 1)
        scene.eevee.taa_render_samples = 4
        for kind in ("normal", "id", "depth"):
            bpy.context.view_layer.material_override = override_mat(kind)
            if kind == "depth":
                bg.inputs["Color"].default_value = (1, 1, 1, 1)
            render(os.path.join(OUTDIR, "%s_anim_%s.png" % (tag, kind)))
        print("DONE", flush=True)
        raise SystemExit
    modes = ("night",) if (KIND == "site" or STATE) else ("day", "night")
    if VIEW == "preview":
        modes = ("night",)
    for m in modes:
        set_mode(m)
        render(os.path.join(OUTDIR, "%s_beauty_%s.png" % (tag, m)))
    if VIEW == "preview":
        print("DONE", flush=True)
        raise SystemExit
    blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
    for o in [solid, cityo, groundo, lito] + eye_objs[:1]:
        o.data.materials[0] = blackm
    for m in modes:
        set_mode(m)
        bg.inputs["Color"].default_value = (0, 0, 0, 1)
        render(os.path.join(OUTDIR, "%s_glow_%s.png" % (tag, m)))
    for o in [solid, cityo, groundo, lito] + eye_objs[:1]:
        o.data.materials[0] = TOON
    beamo.hide_render = True  # translucent light cones stay out of the ink / depth passes
    if eye_objs:
        eye_objs[2].hide_render = True
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    scene.eevee.taa_render_samples = 4
    for kind in ("normal", "id", "depth"):
        bpy.context.view_layer.material_override = override_mat(kind)
        if kind == "depth":
            bg.inputs["Color"].default_value = (1, 1, 1, 1)
        render(os.path.join(OUTDIR, "%s_%s.png" % (tag, kind)))
    bpy.context.view_layer.material_override = None
    print("DONE", flush=True)
