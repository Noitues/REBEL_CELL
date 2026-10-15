"""V3 AAA lights and volumes (exec'd into scene_aaa.py after the merged meshes exist). Seeded, no randomness left.

Lights (Cycles, light tree on):
  rooms        every route room: a ceiling area light in its type colour, x the state multiplier from the job
               (options brighter, past rooms dimmer), plus a weak spill light out of the opening onto street and fog.
               Critique pass: ahead rooms are cooled toward 7000 K; options / current / TARGET get a 2700 K key light.
  street       sodium 2000 K / cool-white spot lamps on the kerb (1800 W), the V3 foreground lamp heads (1400 W),
               alley up-lights (pink / cyan / violet, 1500 W) and point lights on the two holograms.
  sky          4 searchlights (spots synced to the V3 cones, thin 2.6 deg), 3 aerial downlights on the front lane,
               a magenta and a cyan backglow far behind the haze (haze only), 6 district-pair city-glow up-lights that
               reach only the fog cards (light linking, fogcards_aaa.py), and a cool moon. No light is camera-visible.
Volumes (only in the volume render; homogeneous boxes, so the post can compute transmittance exactly):
  back haze    behind the route row (y > 16): the depth haze and the god rays live here, the route stays clear.
  street mist  a low layer (z < 4) along the street: lamp cones and shop glow pool in it.
  front air    0.00008: almost none in front of the route row (CRITIQUE §3 #1: no veil over the rooms).
  steam / strata   heterogeneous media, off by default ("vol_steam", "vol_strata"): ~7x the volume cost on this CPU.
"""

LIGHTS = []            # (light object, base energy, group)  group: room:<id> / street / sky / holo
P_ROOM, P_SPILL = 650.0, 220.0
VOL_BOXES = [
    # name,        x0,    y0,   z0,   x1,    y1,    z1,  density, colour
    ("back_haze", -340.0, 16.0, -2.0, 600.0, 700.0, 420.0, 0.0022, (0.82, 0.78, 1.0)),
    ("street_mist", -160.0, -70.0, -1.0, 380.0, 16.0, 4.0, 0.0060, (0.85, 0.85, 1.0)),
    ("front_air", -160.0, -70.0, 4.0, 380.0, 16.0, 120.0, 0.00008, (0.85, 0.85, 1.0)),
]
VOL_ANISO = 0.2      # low: a forward-scatter halo around the backglow read as a blown orb
if LOOK == "real":
    VOL_BOXES[0] = VOL_BOXES[0][:7] + (0.0025,) + VOL_BOXES[0][8:]
    VOL_BOXES[1] = VOL_BOXES[1][:7] + (0.0080,) + VOL_BOXES[1][8:]


def add_light(name, kind, loc, rot, energy, col, group, size=None, size_y=None, spot=None, blend=0.4, radius=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = col
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size = size or 1.0
        ld.size_y = size_y or size or 1.0
    if kind == "SPOT":
        ld.spot_size = math.radians(spot or 45)
        ld.spot_blend = blend
        ld.shadow_soft_size = radius if radius is not None else 0.3
    if kind == "POINT":
        ld.shadow_soft_size = radius if radius is not None else 0.5
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    ob.visible_camera = False          # light shapes are never seen directly (a backglow quad read as an orb)
    LIGHTS.append([ob, energy, group])
    return ob


ROOM_K = JOB.get("room_k", {})
# r2: option 1 (L4_0, a cyan fight room) read too close to the cool ahead rooms: a warmer, stronger 2700 K key and a
# more saturated type colour (teal-cyan), so it reads as a lit, warm-floored option, not an ahead room
WARM_KEY = {"L4_0": JOB.get("opt1_key", 0.7)}
TYPE_OVERRIDE = {"L4_0": (0.05, 0.85, 1.0)}
ROOM_STATE = JOB.get("room_state", {})
for i, n in sorted(LY["nodes"].items()):
    x0, z0, x1, z1 = n["room"]
    y0 = n["dy"]
    c = TYPE_OVERRIDE.get(i, TYPE_LIGHT[n["kind"]])
    k = ROOM_K.get(i, 1.0)
    st_ = ROOM_STATE.get(i, "")
    if st_ == "reach":
        c = tuple(0.35 * v + 0.65 * w for v, w in zip(c, (0.78, 0.86, 1.0)))     # cool ~7000 K, desaturated
    add_light("room_%s" % i, "AREA", ((x0 + x1) / 2, y0 + DEPTH / 2, z1 - 0.35), (0, 0, 0), P_ROOM * k, c, "room:" + i,
              size=x1 - x0 - 1.4, size_y=DEPTH - 3.0)
    if st_ in ("option", "target", "current"):
        add_light("key_%s" % i, "AREA", ((x0 + x1) / 2, y0 + 3.0, z1 - 0.5), (math.radians(20), 0, 0),
                  P_ROOM * k * WARM_KEY.get(i, 0.25),
                  (1.0, 0.66, 0.40), "room:" + i, size=(x1 - x0) * 0.5, size_y=2.0)        # 2700 K practical key
    add_light("spill_%s" % i, "AREA", ((x0 + x1) / 2, y0 + 1.2, (z0 + z1) / 2 + 1.0), (math.radians(-70), 0, 0),
              P_SPILL * k, c, "room:" + i, size=x1 - x0 - 2.0, size_y=(z1 - z0) * 0.6)

# kerb lamps (poles are geometry in SOLID / NEON; built before the merge would be cleaner, so they get their own mesh)
_lamp = Acc("lamps_s")
_lampn = Acc("lamps_n")
_k = 0
for lx in range(-24, 220, 26):
    if not free_x(lx) or not free_x(lx + 2.4):
        continue
    sod = _k % 3 != 2
    col = (1.0, 0.48, 0.16) if sod else (0.62, 0.8, 1.0)       # sodium 2000 K / cool LED
    set_sem(DRESS_SEM, 0, 0)
    beam((lx, -9.0, 0), (lx, -9.0, 8.5), 0.26, (0.12, 0.12, 0.14), acc=_lamp)
    beam((lx, -9.0, 8.4), (lx + 2.6, -9.0, 8.7), 0.16, (0.12, 0.12, 0.14), acc=_lamp)
    _lampn.face([(lx + 1.6, -9.2, 8.48), (lx + 2.9, -9.2, 8.48), (lx + 2.9, -8.8, 8.48), (lx + 1.6, -8.8, 8.48)],
                tuple(v * 1.6 for v in col), (0, 0, 0))
    add_light("kerb_%d" % _k, "SPOT", (lx + 2.25, -9.0, 8.35), (0, 0, 0), 1800.0, col, "street", spot=82, blend=0.55, radius=0.4)
    _k += 1
SOLID_OBJS.append(_lamp.obj(TOON, "kerb_lamps_s"))
NEON_OBJS.append(_lampn.obj(NEONM, "kerb_lamps_n"))
for k, lx in enumerate((-6.0, 34.0, 76.0, 118.0, 160.0, 204.0)):
    add_light("fglamp_%d" % k, "SPOT", (lx + 2.5, -36.0, 11.0), (0, 0, 0), 1400.0, (1.0, 0.55, 0.22), "street", spot=80, blend=0.6)
# alley up-lights between the route columns (they paint the side walls and stand up in the back haze)
for l in range(7):
    xa = LY["cols"][str(l)][1]
    xb = LY["cols"][str(l + 1)][0]
    c = (PINK, CYAN, VIOLET, PINK, CYAN, (0.9, 0.3, 1.0), CYAN)[l]
    add_light("alley_%d" % l, "AREA", ((xa + xb) / 2, 19.0, 0.6), (math.pi, 0, 0), 1500.0, c, "street", size=3.0, size_y=6.0)
# holograms: light their surroundings and the haze
_HOLO_LIGHT = {"holo_orbital": (0.35, 0.8, 1.0), "holo_solace": (0.95, 0.5, 1.0)}
for ob in HOLO_OBJS:
    if ob.name in _HOLO_LIGHT:
        add_light("holo_%s" % ob.name, "POINT", tuple(ob.location), (0, 0, 0), 9000.0, _HOLO_LIGHT[ob.name], "holo", radius=4.0)
# r2: the SOLACE holo ad (it replaced the lotus; its mesh is at world coordinates, so the light is placed by hand)
add_light("holo_solace_ad", "POINT", (40.0, 38.5, 70.0), (0, 0, 0), 6000.0, (0.8, 0.5, 1.0), "holo", radius=4.0)
# shop / stall glow onto the wet street (helps the light tree: big soft sources where the eye looks)
for (sx, sc) in ((18.0, PINK), (67.5, CYAN), (141.0, AMBER), (163.0, PINK)):
    if free_x(sx):
        add_light("stall_%d" % int(sx), "AREA", (sx, -6.4, 1.6), (math.radians(-60), 0, 0), 500.0, sc, "street", size=3.0, size_y=1.0)
# searchlights (synced to the V3 cones per shot) and aerial downlights (ride their cars)
SPOTS_SEARCH = []
for ob, base, k in SEARCH:
    sl = add_light("search_%d" % k, "SPOT", tuple(ob.location), (0, 0, 0), 2.0e6, (0.75, 0.8, 1.0), "sky", spot=2.6, blend=0.25,
                   radius=1.2)
    SPOTS_SEARCH.append((sl, ob))
SPOTS_AIR = []
for idx in ():                   # r2: no cars, so no aerial downlights (designer note 1)
    objs, x0, y, z, sp = TRAFFIC[idx]
    sl = add_light("air_down_%d" % idx, "SPOT", (0, 0, 0), (0, 0, 0), 5.0e4, (0.85, 0.9, 1.0), "sky", spot=5.5, blend=0.3,
                   radius=0.6)
    SPOTS_AIR.append((sl, objs[0]))
add_light("backglow_m", "AREA", (40.0, 1000.0, 15.0), (math.radians(-90), 0, 0), 3.5e8, (1.0, 0.32, 0.75), "sky", size=700.0, size_y=160.0)
add_light("backglow_c", "AREA", (330.0, 1000.0, 10.0), (math.radians(-90), 0, 0), 2.1e8, (0.3, 0.75, 1.0), "sky", size=400.0, size_y=120.0)



# sky-group lights that exist for the haze only (city glow, backglow, searchlights): they must not flood far facades
# (reference study: facades stay dark, the light lives in the air and on wet ground)
def haze_only(prefixes=("backglow", "search_", "cityglow")):
    for ob, e0, grp in LIGHTS:
        if ob.name.startswith(prefixes):
            for attr_ in ("visible_diffuse", "visible_glossy", "visible_transmission"):
                try:
                    setattr(ob, attr_, False)
                except AttributeError:
                    pass


def sync_moving_lights():
    """After animate(t): searchlights follow their cones (cone axis +Z, spot axis -Z), downlights follow their cars."""
    flip = Matrix.Rotation(math.pi, 4, "X")
    for sl, ob in SPOTS_SEARCH:
        sl.matrix_world = ob.matrix_world @ flip
    for sl, car in SPOTS_AIR:
        sl.location = (car.location[0], car.location[1], car.location[2] - 1.0)
        sl.rotation_euler = (0, 0, 0)


# ------------------------------------------------------------------ volumes
def vol_mat(name, density, col, noise=False):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = tuple(col) + (1,)
    vs.inputs["Anisotropy"].default_value = VOL_ANISO
    if noise:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nn(nt, "ShaderNodeTexNoise", Scale=1.6, Detail=5.0, Roughness=0.6)
        nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
        mr = nn(nt, "ShaderNodeMapRange", From_Min=0.45, From_Max=0.8, To_Min=0.0, To_Max=1.0)
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        sx = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sx.inputs[0])
        fall = math_n(nt, "POWER", math_n(nt, "SUBTRACT", 1.0, sx.outputs["Z"]), 1.6)
        # radial falloff in xy
        dx = math_n(nt, "SUBTRACT", sx.outputs["X"], 0.5)
        dy = math_n(nt, "SUBTRACT", sx.outputs["Y"], 0.5)
        rr = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "MULTIPLY", dx, dx), math_n(nt, "MULTIPLY", dy, dy)))
        rad = math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MULTIPLY", rr, 2.0)), 0.0)
        d = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", mr.outputs[0], fall), math_n(nt, "MULTIPLY", rad, density))
        nt.links.new(d, vs.inputs["Density"])
    else:
        vs.inputs["Density"].default_value = density
    nt.links.new(vs.outputs[0], out.inputs["Volume"])
    return m


def vol_box(name, x0, y0, z0, x1, y1, z1, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    me.materials.append(mat)
    scene.collection.objects.link(ob)
    VOLUME_OBJS.append(ob)
    return ob


for (nm, x0, y0, z0, x1, y1, z1, d, c) in [v for v in VOL_BOXES if not (JOB.get("no_back_haze") and v[0] == "back_haze")]:
    vol_box("vol_" + nm, x0, y0, z0, x1, y1, z1, vol_mat("vm_" + nm, d, c))
_steam_m = vol_mat("vm_steam", 0.22, (0.9, 0.9, 0.95), noise=True)

# fog strata (designer feedback): thin layered bands at different heights behind the route row, wind-sheared and
# stretched in X (anisotropic noise: features ~170 BU long, ~25 deep, ~3 high), lit from below by the city glow.
STRATA = [
    # z0,   z1,   peak density, shear (x per z)
    (30.0, 38.0, 0.030, 2.5),
    (48.0, 54.0, 0.024, 3.5),
    (66.0, 75.0, 0.030, 2.0),
    (90.0, 97.0, 0.022, 4.0),
    (118.0, 128.0, 0.026, 3.0),
    (150.0, 158.0, 0.018, 2.5),
]


def strata_mat(name, peak, shear, seed):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = (0.85, 0.8, 1.0, 1)
    vs.inputs["Anisotropy"].default_value = 0.3
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], sx.inputs[0])
    xs = math_n(nt, "ADD", sx.outputs["X"], math_n(nt, "MULTIPLY", sx.outputs["Z"], shear))
    cv = nt.nodes.new("ShaderNodeCombineXYZ")
    L(math_n(nt, "MULTIPLY", xs, 0.004), cv.inputs[0])
    L(math_n(nt, "MULTIPLY", sx.outputs["Y"], 0.015), cv.inputs[1])
    L(math_n(nt, "MULTIPLY", sx.outputs["Z"], 0.25), cv.inputs[2])
    nz = nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=float(JOB.get("strata_detail", 4.0)), Roughness=0.62, Distortion=0.6)
    try:
        nz.noise_dimensions = "4D"
        nz.inputs["W"].default_value = seed
    except (AttributeError, TypeError, KeyError):
        pass
    L(cv.outputs[0], nz.inputs["Vector"])
    mr = nn(nt, "ShaderNodeMapRange", From_Min=0.50, From_Max=0.78, To_Min=0.0, To_Max=1.0)
    L(nz.outputs["Fac"], mr.inputs["Value"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gz = nt.nodes.new("ShaderNodeSeparateXYZ")
    L(tc.outputs["Generated"], gz.inputs[0])
    prof = math_n(nt, "MULTIPLY", 4.0, math_n(nt, "MULTIPLY", gz.outputs["Z"], math_n(nt, "SUBTRACT", 1.0, gz.outputs["Z"])))
    prof = math_n(nt, "POWER", math_n(nt, "MAXIMUM", prof, 0.0), 1.5)
    d = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", math_n(nt, "POWER", mr.outputs[0], 1.4), prof), peak)
    L(d, vs.inputs["Density"])
    L(vs.outputs[0], out.inputs["Volume"])
    return m


if JOB.get("vol_strata"):        # path-traced strata (7x the volume cost here); the default is fogcards_aaa.py
    for k, (z0, z1, pk, sh) in enumerate(STRATA):
        vol_box("strata_%d" % k, -340.0, 20.0, z0, 600.0, 520.0, z1, strata_mat("vm_strata_%d" % k, pk, sh, 3.7 * k + 1.3))
# the city glow that lights the strata from below: broad, dim up-lights over the street grid behind the route row
for k, (gx, gy, gz, c) in enumerate(((-40.0, 50.0, 6.0, (1.0, 0.16, 0.54)), (150.0, 70.0, 6.0, (0.16, 0.83, 1.0)),
                                      (260.0, 60.0, 6.0, (1.0, 0.16, 0.54)), (400.0, 120.0, 6.0, (0.16, 0.83, 1.0)),
                                      (20.0, 160.0, 6.0, (0.16, 0.83, 1.0)), (180.0, 200.0, 6.0, (1.0, 0.16, 0.54)))):
    add_light("cityglow_%d" % k, "AREA", (gx, gy, gz), (math.pi, 0, 0), 1.2e5, c, "sky", size=160.0, size_y=80.0)
for (sx, sy, sz, sr, sh) in (STEAM_SPOTS if JOB.get("vol_steam") else []):
    if sz == 0 and not free_x(sx):
        continue
    STEAM_OBJS.append(vol_box("steam_%d_%d" % (int(sx), int(sz)), sx - sr * 2.2, sy - sr * 2.2, sz, sx + sr * 2.2, sy + sr * 2.2,
                              sz + sh, _steam_m))


# ------------------------------------------------------------------ the hover power cut (3D)
def power_cut(cfg):
    """cfg = {"keep": [node ids], "boost": 1.45, "k": 0.25, "room_k": {node: state factor}}.
    Room faces get their state factor (room_k / 1.8, so an option = 1). With "keep", emitters and lights outside the
    kept rooms also drop to k (the hover power cut)."""
    keep = set(cfg.get("keep", []))
    cut = bool(keep)
    k = cfg.get("k", 0.25) if cut else 1.0
    boost = cfg.get("boost", 1.45) if cut else 1.0
    keep_idx = {ROOM_IDX[i] for i in keep}
    state = {ROOM_IDX[i]: v / 1.8 for i, v in cfg.get("room_k", {}).items()}
    import numpy as _np
    for o in NEON_OBJS:
        me = o.data
        if "sem" not in me.attributes:
            continue
        n = len(me.polygons)
        sem = _np.zeros(n * 4, _np.float32)
        me.attributes["sem"].data.foreach_get("color", sem)
        sem = sem.reshape(n, 4)
        idx = _np.rint(sem[:, 1] * 32.0).astype(_np.int32)
        room = _np.abs(sem[:, 0] - 0.5) < 0.04
        kept = room & _np.isin(idx, list(keep_idx)) if cut else room
        sk = _np.array([state.get(int(v), 1.0) for v in idx], _np.float32)
        pw = _np.where(kept, boost, k).astype(_np.float32) * _np.where(room, sk, 1.0).astype(_np.float32)
        a = me.attributes.get("pw") or me.attributes.new("pw", "FLOAT", "FACE")
        a.data.foreach_set("value", pw)
    if not cut:
        return
    for o in TEXT_OBJS + HOLO_OBJS:
        o["pwo"] = k
    for ob, e0, grp in LIGHTS:
        if grp.startswith("room:"):
            ob.data.energy = e0 * (boost if grp[5:] in keep else k)
        else:
            ob.data.energy = e0 * k
    bsdf = next(n for n in TOON.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Emission Strength"].default_value = LK["gs"] * k
    for m in (AIRM, TRAILM, STEAMM):
        em = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
        em.inputs["Strength"].default_value *= k

haze_only()
