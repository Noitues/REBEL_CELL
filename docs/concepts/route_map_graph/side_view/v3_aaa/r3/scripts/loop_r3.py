"""r3 idle loop renders (exec'd by render_aaa.py when the job has "loop"). Camera locked on O_overview.

The loop is 96 frames at 24 fps (4 s). Light transport is linear in the emitters, so the city is rendered ONCE and only
what moves is rendered per frame; the post (post_loop.py) sums the layers per frame:

  statics  (one session, persistent data, 1280 x 720)
    base            the main pass with every loop-animated emitter in its rest state and the moving things removed
    layer_<g>       one emission-only render per flicker group (the group is the only emitter; every surface keeps its
                    material, so the group's spill on walls and its reflection in the puddles come with it):
                    3 neon signs, 3 nav-strobe phases, the VOLTA billboard (ad A) and its alternate (ad B), 3 holo ads
                    (mode "layers" re-renders only these; object custom properties need update_tag() to reach Cycles
                    under persistent data). Windows switch in 2D (post_loop.pick_windows): their spill is negligible.
    trans           transmittance of the heterogeneous media
    + the Eevee data passes and anchors (the regular shot loop, "data" only)
  media    (loop_media.py, through the still's own volume pass) vol_static = every medium, no beams; beams_full =
           the beams only, through every medium (calibrates the per-frame beams)
  beams    (per frame, 640 x 360) the beams only, through the homogeneous back haze only (cheap: no shader media);
           the post scales them by the strata (1 + k tau), k fitted against beams_full
  dyn      (per frame, 1280 x 720, emission-only) the moving emitters: the light-streak traffic (4 street lanes and
           3 sky lanes, loop-periodic) and the rotating ORBITAL globe; their reflections in the wet street come with them

Every pattern is seeded; every motion is periodic in the 4 s loop, so frame 96 = frame 0.
"""
import random as _rl
import time as _t

LOOP = JOB["loop"]
L_T = float(LOOP.get("T", 4.0))
L_FPS = int(LOOP.get("fps", 24))
L_NF = int(round(L_T * L_FPS))
shot = JOB["shots"][0]
set_pose(shot["pose"])
animate(2.0)
sync_moving_lights()
bpy.context.view_layer.update()
scene.render.use_persistent_data = True
try:
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
except AttributeError:
    pass
LDIR = OUTDIR
GROUPS = {}            # name -> dict(kind, ...)


def timed_render(path):
    t0 = _t.time()
    render(path)
    dt = _t.time() - t0
    print("TIME render %s %.1f" % (os.path.basename(path), dt), flush=True)
    return dt


def save_combined(exr, stem, extra=None):
    want = {"Combined": "combined"}
    want.update(extra or {})
    exr_to_npy(exr, stem, want)
    try:
        os.remove(exr)
    except OSError:
        pass


# ------------------------------------------------------------------ gain nodes on the shared emissive materials
def add_gain(mat):
    """Insert a multiply (a Value node) in front of the Emission strength; returns the Value node."""
    nt = mat.node_tree
    em = next(n for n in nt.nodes if n.type == "EMISSION")
    v = nt.nodes.new("ShaderNodeValue")
    v.outputs[0].default_value = 1.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    inp = em.inputs["Strength"]
    if inp.links:
        src = inp.links[0].from_socket
        nt.links.new(src, mul.inputs[0])
    else:
        mul.inputs[0].default_value = inp.default_value
    nt.links.new(v.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], inp)
    return v


GAIN = {m.name: add_gain(m) for m in (NEONM, WINM)}


def extract_faces(ob, faces, name):
    """Move the given faces of a merged emissive mesh into their own object, with their own material copy + gain."""
    import bmesh as _bm
    me2 = ob.data.copy()
    bm = _bm.new()
    bm.from_mesh(me2)
    bm.faces.ensure_lookup_table()
    keep = set(faces)
    _bm.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
    bm.to_mesh(me2)
    bm.free()
    bm = _bm.new()
    bm.from_mesh(ob.data)
    bm.faces.ensure_lookup_table()
    _bm.ops.delete(bm, geom=[bm.faces[i] for i in sorted(keep)], context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    ob2 = bpy.data.objects.new(name, me2)
    scene.collection.objects.link(ob2)
    m2 = ob.data.materials[0].copy()
    m2.name = "g_" + name
    me2.materials.clear()
    me2.materials.append(m2)
    gn = next(n for n in m2.node_tree.nodes if n.type == "VALUE")
    GAIN[m2.name] = gn
    NEON_OBJS.append(ob2)
    return ob2, m2


# ------------------------------------------------------------------ group selection (seeded, by screen position)
_A0 = anchors_for(shot)
_dec = [_A0["rooms"][i]["front"] for i, stt in sorted(JOB["room_state"].items()) if stt in ("current", "option")]
_dec_pts = [p for poly in _dec for p in poly if p]
DEC_BOX = (min(p[0] for p in _dec_pts) - 90, min(p[1] for p in _dec_pts) - 120, max(p[0] for p in _dec_pts) + 90,
           max(p[1] for p in _dec_pts) + 60)
print("decision box px (1920)", [round(v) for v in DEC_BOX], flush=True)


def on_screen(b, margin=20):
    return b and b[0] > margin and b[2] < 1920 - margin and b[1] > 130 and b[3] < 1040


def off_decision(b):
    return b[2] < DEC_BOX[0] or b[0] > DEC_BOX[2] or b[3] < DEC_BOX[1] or b[1] > DEC_BOX[3]


def face_px(ob, f):
    c = ob.matrix_world @ f.center
    return proj(tuple(c)), c


def seen(ob, f, c):
    """The face faces the camera and nothing stands between (a ray from the camera hits this object first)."""
    camp = Vector(shot["pose"]["loc"])
    nrm = (ob.matrix_world.to_3x3() @ f.normal).normalized()
    to_cam = (camp - c)
    if nrm.dot(to_cam) <= 0:
        return False
    hit, loc, n_, fi, hob, m_ = scene.ray_cast(bpy.context.evaluated_depsgraph_get(), camp, (c - camp).normalized(),
                                              distance=(c - camp).length + 0.05)
    return hit and (loc - c).length < 0.5          # (the window quad may sit flush on its wall)


def setup_groups():
    # neon text signs: the two largest off the decision set flicker / buzz, the largest street-level one stutters
    cands = []
    for o in TEXT_OBJS:
        if o.type != "FONT":
            continue
        b = obj_bbox_px([o])
        if on_screen(b) and off_decision(b):
            cands.append(((b[2] - b[0]) * (b[3] - b[1]), o.name, b))
    cands.sort(key=lambda c: (-c[0], c[1]))
    up = [c for c in cands if (c[2][1] + c[2][3]) / 2 < 760]
    low = [c for c in cands if (c[2][1] + c[2][3]) / 2 >= 760]
    picks = []
    if up:
        picks.append(("sign_buzz", up[0]))
    if len(up) > 1:
        picks.append(("sign_flicker", up[1]))
    if low:
        picks.append(("sign_broken", low[0]))
    elif len(up) > 2:
        picks.append(("sign_broken", up[2]))
    for g, (_a, nm, b) in picks:
        GROUPS[g] = dict(kind="obj", obj=nm, px=[round(v, 1) for v in b])
    # the VOLTA billboard (ad A) and its alternate content (ad B), the holo ads
    for o in TEXT_OBJS:
        if o.name.startswith("ad_volta"):
            GROUPS["bill_a"] = dict(kind="obj", obj=o.name, px=obj_bbox_px([o]))
            GROUPS["bill_b"] = dict(kind="obj", obj=o.name, alt="noodle", px=obj_bbox_px([o]))
    for o in HOLO_OBJS:
        if o.name.startswith("ad_holo_"):
            b = obj_bbox_px([o])
            if on_screen(b, 0):
                GROUPS["holo_" + o.name.split("_")[2]] = dict(kind="obj", obj=o.name, px=[round(v, 1) for v in b])
    # windows: 3 lit window quads of the route row, off the decision set, seeded pick
    win_ob = next(o for o in NEON_OBJS if o.data.materials and o.data.materials[0] == WINM)
    me = win_ob.data
    cols = me.attributes["col"].data if "col" in me.attributes else None
    wc = []
    for f in me.polygons:
        px, c = face_px(win_ob, f)
        lum_ = sum(cols[f.index].color[:3]) / 3.0 if cols is not None else 1.0
        if px and 200 < px[0] < 1800 and 260 < px[1] < 900 and f.area > 0.6 and lum_ > 0.35:     # lit windows only
            b = (px[0] - 4, px[1] - 4, px[0] + 4, px[1] + 4)
            if off_decision(b) and seen(win_ob, f, c):
                wc.append((round(c.x, 2), round(c.z, 2), f.index, px))
    wc.sort()
    rr = _rl.Random(9601)
    pick = rr.sample(range(len(wc)), min(3, len(wc)))
    win_faces = {}
    for k, pi in enumerate(sorted(pick)):
        win_faces["win_%d" % k] = wc[pi]
    # nav strobes: red beacon panels high up (z > 40), on screen, split into 3 phases by x
    red = []
    for o in list(NEON_OBJS):
        if not o.data.materials or o.data.materials[0] != NEONM or "col" not in o.data.attributes:
            continue
        ca = o.data.attributes["col"]
        if ca.domain != "FACE":
            continue
        for f in o.data.polygons:
            c = ca.data[f.index].color
            if abs(c[0] - 1.0) < 0.02 and abs(c[1] - 0.15) < 0.02 and abs(c[2] - 0.12) < 0.02:
                px, wc_ = face_px(o, f)
                if wc_.z > 40 and px and 0 < px[0] < 1920 and 120 < px[1] < 1000:
                    red.append((round(wc_.x, 2), round(wc_.z, 2), o.name, f.index, px))
    red.sort()
    by_obj = {}
    for k, (x, z, onm, fi, px) in enumerate(red):
        by_obj.setdefault(("strobe_%d" % (k % 3), onm), []).append(fi)
    for (g, onm), fis in sorted(by_obj.items()):
        o2, m2 = extract_faces(bpy.data.objects[onm], fis, "%s_%s" % (g, onm))
        GROUPS.setdefault(g, dict(kind="mats", mats=[], n=0))
        GROUPS[g]["mats"].append(m2.name)
        GROUPS[g]["n"] += len(fis)
    for g, (x, z, fi, px) in sorted(win_faces.items()):
        o2, m2 = extract_faces(win_ob, [fi], g)
        GROUPS[g] = dict(kind="mats", mats=[m2.name], px=[round(px[0], 1), round(px[1], 1)])
    print("GROUPS", json.dumps(GROUPS), flush=True)


# ------------------------------------------------------------------ loop traffic (periodic) and the split globe
_SLP = PRE["street_lanes"]["periods"]
_KLP = PRE["sky_lanes"]["periods"]
LANES = [
    # y, z, head, base k, thickness, period P (BU, one period per loop: speed = P / T), direction, sky
    # (rule-placed: the street lanes from the road transect, the sky lanes from the skyline; rules_r3.py)
    (RULES["street_lanes"][0], 0.72, True, 2.6, 0.11, _SLP[0], 1, False),
    (RULES["street_lanes"][1], 0.74, True, 2.0, 0.11, _SLP[1], 1, False),
    (RULES["street_lanes"][2], 0.92, False, 3.4, 0.12, _SLP[2], -1, False),
    (RULES["street_lanes"][3], 0.90, False, 2.8, 0.12, _SLP[3], -1, False),
] + [(y, z, k == 0, (2.0, 3.0, 1.8)[k % 3], (0.22, 0.24, 0.34)[k % 3], _KLP[k % len(_KLP)], (1, -1, 1)[k % 3], True)
     for k, (y, z) in enumerate(RULES["sky_lanes"])]
LOOP_STREAKS = []      # (object, P, dir)


def streak_mat_loop():
    """hr_streak plus the calm-zone damping by WORLD x (the streaks move, so it can no longer be baked per vertex):
    sky streaks (z > 40) inside x 70-114 drop to 35 %, as in r2."""
    m = STREAK_M.copy()
    m.name = "hr_streak_loop"
    nt = m.node_tree
    em = next(n for n in nt.nodes if n.type == "EMISSION")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sx = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sx.inputs[0])
    inz = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", sx.outputs["X"], CALM[0] - 6),
                 math_n(nt, "LESS_THAN", sx.outputs["X"], CALM[1] + 6))
    sky = math_n(nt, "GREATER_THAN", sx.outputs["Z"], 40.0)
    damp = math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", inz, sky), 0.65))
    inp = em.inputs["Strength"]
    src = inp.links[0].from_socket
    nt.links.new(math_n(nt, "MULTIPLY", src, damp), inp)
    return m


def build_loop_streaks():
    m = streak_mat_loop()
    rr = _rl.Random(9402)
    for li, (y, z, head, kk, th, P, dirn, sky) in enumerate(LANES):
        cars = []
        x = rr.uniform(0, 20)
        while True:
            L = rr.uniform(6.0, 16.0) if sky else rr.uniform(12.0, 80.0)
            gap = rr.uniform(60.0, 160.0) if sky else rr.uniform(10.0, 55.0)
            if x + L > P - 8.0:
                break
            cars.append((x, L, rr.random(), rr.random(), rr.random(), rr.random(), rr.choice(HEAD) if head else TAIL,
                         rr.uniform(-4.0, 4.0) if sky else rr.uniform(-0.06, 0.06), rr.uniform(0.3, 1.0),
                         rr.uniform(-0.035, 0.035), rr.uniform(0.85, 1.15)))
            x += L + gap
        st = Streaks("loopstreak_%d" % li)
        r2 = _rl.Random(9403 + li)
        lo, hi = -160.0 - P, 380.0 + P
        k0 = int(math.floor(lo / P))
        k1 = int(math.ceil(hi / P))
        for kc in range(k0, k1 + 1):
            for (cx, L, a1, a2, a3, a4, col, dz, ks, sl, tk) in cars:
                xa = kc * P + cx
                if xa + L < lo or xa > hi:
                    continue
                k = kk * ks
                zz = z + dz
                if sky:     # r3 art review: separate vehicles, bright head + fading tail, own angle, no strobe dots
                    st.add(xa, xa + L, y, zz, th * 1.1, col, k * 1.4, r2, slope=(1 if a4 < 0.5 else -1) * (0.05 + 0.07 * a3),
                           calm_k=1.0, head=dirn)
                else:
                    st.add(xa, xa + L, y, zz, th * tk, col, k, r2)
                    if a1 < 0.35:
                        st.add(xa + 0.4, xa + L - 0.4, y + 0.2, zz + (0.3 if head else -0.32), th * 0.7, col, k * 0.35, r2)
                    if a2 < 0.12:
                        st.add(xa + L * 0.3, xa + L, y - 0.1, zz + 0.05, th * 0.8, AMBER_IND, kk * 0.6, r2, dash=1.6)
                    if a3 < 0.10:
                        st.add(xa, xa + L * 0.8, y + 0.3, 2.8, th * 0.8, AMBER_IND, kk * 0.35, r2)
        ob = st.obj()
        ob.data.materials[0] = m
        LOOP_STREAKS.append((ob, P, dirn))
    print("loop streak lanes", len(LOOP_STREAKS), flush=True)


def build_split_globe():
    """The ORBITAL holo, split: the globe (latitudes + longitudes) spins about its own axis; the tilted orbit ring stays.
    One longitude spacing (22.5 deg) per loop, so the spin is seamless."""
    src = bpy.data.objects.get("holo_orbital")
    mat = src.data.materials[0]
    loc, rot = Vector(src.location), src.rotation_euler.copy()
    src.hide_render = True
    HOLO_OBJS.remove(src)

    def fill(bm, part, r=9.0, w=0.16):
        def strut(a, b, n_off):
            a, b = Vector(a), Vector(b)
            d = (b - a)
            if d.length < 1e-6:
                return
            s = d.cross(Vector(n_off)).normalized() * w
            vs = [bm.verts.new(p) for p in (a - s, b - s, b + s, a + s)]
            bm.faces.new(vs)
        if part == "globe":
            for la in range(-3, 4):
                phi = la * math.pi / 8
                for k in range(24):
                    t0, t1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
                    strut((r * math.cos(phi) * math.cos(t0), r * math.cos(phi) * math.sin(t0), r * math.sin(phi)),
                          (r * math.cos(phi) * math.cos(t1), r * math.cos(phi) * math.sin(t1), r * math.sin(phi)), (0, 0, 1))
            for lo in range(8):
                t = math.pi * lo / 8
                for k in range(24):
                    p0, p1 = math.pi * k / 12, math.pi * (k + 1) / 12
                    strut((r * math.cos(p0) * math.cos(t), r * math.cos(p0) * math.sin(t), r * math.sin(p0)),
                          (r * math.cos(p1) * math.cos(t), r * math.cos(p1) * math.sin(t), r * math.sin(p1)),
                          (math.cos(t + 1.57), math.sin(t + 1.57), 0))
        else:
            R2 = r * 1.5
            for k in range(48):
                t0, t1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
                a = Vector((R2 * math.cos(t0), R2 * math.sin(t0), 0.0))
                b = Vector((R2 * math.cos(t1), R2 * math.sin(t1), 0.0))
                rr_ = Matrix.Rotation(math.radians(22), 3, "X")
                strut(tuple(rr_ @ a), tuple(rr_ @ b), (0, 0, 1))
    out = {}
    for part in ("globe", "ring"):
        ob = holo_obj("holo_orbital_" + part, lambda bm, p=part: fill(bm, p), mat, tuple(loc))
        ob.rotation_euler = rot
        out[part] = ob
    return out


GLOBE = None


def set_loop_time(t):
    """Every loop-driven transform at time t (s): streak lanes, globe spin, beams."""
    p = (t % L_T) / L_T
    for ob, P, dirn in LOOP_STREAKS:
        ob.location = (dirn * p * P, 0.0, 0.0)
    if GLOBE:
        g = GLOBE["globe"]
        g.rotation_euler = GLOBE["rot0"]
        base = g.rotation_euler.to_matrix()
        spin = Matrix.Rotation(p * math.pi / 8, 3, "Z")
        g.rotation_euler = (base @ spin).to_euler()
    set_beams(t)


# ------------------------------------------------------------------ render modes
_WBG = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
_TOON_BSDF = next(n for n in TOON.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_SAVE = {}


def emission_only(on_objs=(), on_mats=(), alt=None):
    """Lights, world, the window grid, every other emitter off; only the given objects / materials emit."""
    _SAVE["wbg"] = _WBG.inputs["Strength"].default_value
    _SAVE["gs"] = _TOON_BSDF.inputs["Emission Strength"].default_value
    _WBG.inputs["Strength"].default_value = 0.0
    _TOON_BSDF.inputs["Emission Strength"].default_value = 0.0
    _SAVE["lights"] = {}
    for ob, e0, grp in LIGHTS:
        _SAVE["lights"][ob.name] = ob.hide_render
        ob.hide_render = True
    moon = bpy.data.objects.get("moon")
    if moon:
        _SAVE["moon"] = moon.hide_render
        moon.hide_render = True
    _SAVE["air"] = []
    for m in (AIRM, TRAILM, STEAMM):     # strength changes only (toggling meshes would rebuild the BVH)
        em = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
        _SAVE["air"].append((em, em.inputs["Strength"].default_value))
        em.inputs["Strength"].default_value = 0.0
    for nm, v in GAIN.items():
        v.outputs[0].default_value = 1.0 if nm in on_mats else 0.0
    _SAVE["pwo"] = {}
    for o in TEXT_OBJS + HOLO_OBJS:
        _SAVE["pwo"][o.name] = o.get("pwo", None)
        o["pwo"] = (_SAVE["pwo"][o.name] or 0.0) if o.name in on_objs else -1.0
        o.update_tag()      # a custom-property change alone does not reach Cycles under persistent data
    if alt:
        ob = bpy.data.objects[alt[0]]
        tex = next(n for n in ob.data.materials[0].node_tree.nodes if n.type == "TEX_IMAGE")
        _SAVE["alt"] = (tex, tex.image)
        tex.image = bpy.data.images.load(os.path.join(ADS_DIR, alt[1] + ".png"))


def restore_all():
    _WBG.inputs["Strength"].default_value = _SAVE["wbg"]
    _TOON_BSDF.inputs["Emission Strength"].default_value = _SAVE["gs"]
    for ob, e0, grp in LIGHTS:
        ob.hide_render = _SAVE["lights"][ob.name]
    moon = bpy.data.objects.get("moon")
    if moon:
        moon.hide_render = _SAVE["moon"]
    for em, v0 in _SAVE.pop("air", []):
        em.inputs["Strength"].default_value = v0
    for nm, v in GAIN.items():
        v.outputs[0].default_value = 1.0
    for o in TEXT_OBJS + HOLO_OBJS:
        pv = _SAVE["pwo"].get(o.name)
        if pv is None:
            if "pwo" in o:
                del o["pwo"]
        else:
            o["pwo"] = pv
        o.update_tag()
    if "alt" in _SAVE:
        tex, img = _SAVE.pop("alt")
        tex.image = img


_VOL_SAVED = {}
_OFF0 = set(ob.name for ob, e0, grp in LIGHTS if ob.hide_render)


def vol_wrap():
    for o in all_surface_objs():
        mats = list(o.data.materials)
        _VOL_SAVED[o.name] = mats
        for si, m in enumerate(mats):
            if m is not None:
                o.data.materials[si] = wrapped(m, is_see_through(m))
    for o in ATMOS_OBJS:
        o.hide_render = True
    WORLD_CAM_MUL.inputs[1].default_value = 1.0
    neon_fog(False)


def vol_unwrap():
    for o in all_surface_objs():
        for si, m in enumerate(_VOL_SAVED.get(o.name, [])):
            o.data.materials[si] = m
    for o in VOLUME_OBJS:
        o.hide_render = True
    for o in ATMOS_OBJS:
        o.hide_render = False
    WORLD_CAM_MUL.inputs[1].default_value = 0.0
    neon_fog(True)


def vol_show(strata, mist, homog, beams, others):
    het_strata = set(o.name for o, ms, ma in HET if o.name.startswith("r3strata"))
    for o in VOLUME_OBJS:
        if o.name in het_strata:
            o.hide_render = not strata
        elif o.name == "r3mist":
            o.hide_render = not mist
        else:
            o.hide_render = (not homog) or o in STEAM_OBJS
    for ob, e0, grp in LIGHTS:
        if ob.name in _OFF0:            # lights the build switched off (r2's hand-placed city glow) stay off
            ob.hide_render = True
            continue
        ob.hide_render = not (beams if ob.name.startswith("beam_") else others)
        # a linked light whose receivers are all hidden would light EVERYTHING (Cycles drops an empty link set):
        # switch it off instead (the backglow, linked to the back haze, lit the strata-only render at full power)
        rc = ob.light_linking.receiver_collection
        if rc is not None and not ob.name.startswith("beam_") and all(o.hide_render for o in rc.objects):
            ob.hide_render = True


# the original streaks are replaced by the loop lanes; the globe is split
for _o in STREAK_OBJS:
    _o.hide_render = True
    if _o in HOLO_OBJS:
        HOLO_OBJS.remove(_o)
build_loop_streaks()
GLOBE = build_split_globe()
GLOBE["rot0"] = GLOBE["globe"].rotation_euler.copy()
setup_groups()
DYN = [o for o, P, d in LOOP_STREAKS] + [GLOBE["globe"]]
with open(os.path.join(LDIR, "groups.json"), "w") as _f:
    json.dump(dict(groups=GROUPS, T=L_T, fps=L_FPS, nf=L_NF, dec_box=DEC_BOX), _f, indent=1)
for _o in BEAM_HEADS:
    _o.hide_render = True

MODE_L = LOOP.get("mode")
RES = tuple(LOOP.get("res", (1280, 720)))
VRES = tuple(LOOP.get("vres", (640, 360)))
_T0 = _t.time()

if MODE_L == "statics":
    set_loop_time(0.0)
    for o in DYN:
        o.hide_render = True
    for o in VOLUME_OBJS:
        o.hide_render = True
    WORLD_CAM_MUL.inputs[1].default_value = 0.0
    cycles_setup(int(LOOP.get("main_spp", 128)), RES, 0.01)
    timed_render(os.path.join(LDIR, "base.exr"))
    save_combined(os.path.join(LDIR, "base.exr"), os.path.join(LDIR, "base"),
                  {"Emission": "emit", "Denoising Albedo": "albedo", "Depth": "z", "Diffuse Color": "diffcol"})
    # emission-only layers (same resolution, fewer samples: only one small emitter each)
    cycles_setup(int(LOOP.get("layer_spp", 64)), RES, 0.01)
    for g, d in sorted(GROUPS.items()):
        if d["kind"] == "obj":
            emission_only(on_objs=(d["obj"],), alt=(d["obj"], d["alt"]) if d.get("alt") else None)
        else:
            emission_only(on_mats=tuple(d["mats"]))
        timed_render(os.path.join(LDIR, "layer_%s.exr" % g))
        save_combined(os.path.join(LDIR, "layer_%s.exr" % g), os.path.join(LDIR, "layer_" + g))
        restore_all()
    # volumes (no beams): the strata alone (they drift in 2D) and the rest; then the beams through every medium
    vol_wrap()
    # the static media at the full loop resolution (a half-res in-scatter blurred tower silhouettes into "slabs")
    cycles_setup(int(LOOP.get("vol_spp", 48)), RES, 0.01)
    for nm, flags in (("vol_strata", (True, False, False, False, True)), ("vol_rest", (False, True, True, False, True)),
                      ("beams_full", (True, True, True, True, False))):
        vol_show(*flags)
        timed_render(os.path.join(LDIR, nm + ".exr"))
        save_combined(os.path.join(LDIR, nm + ".exr"), os.path.join(LDIR, nm))
    vol_show(True, True, True, True, True)
    vol_unwrap()
    trans_pass(os.path.join(LDIR, "static"), RES, int(LOOP.get("trans_spp", 32)))
    RENDERS[:] = ["data"]
    print("STATICS DONE %.1f s" % (_t.time() - _T0), flush=True)
elif MODE_L == "layers":              # the emission-only flicker layers only
    set_loop_time(0.0)
    for o in DYN:
        o.hide_render = True
    for o in VOLUME_OBJS:
        o.hide_render = True
    cycles_setup(int(LOOP.get("layer_spp", 64)), RES, 0.01)
    for g, d in sorted(GROUPS.items()):
        if d["kind"] == "obj":
            emission_only(on_objs=(d["obj"],), alt=(d["obj"], d["alt"]) if d.get("alt") else None)
        else:
            emission_only(on_mats=tuple(d["mats"]))
        timed_render(os.path.join(LDIR, "layer_%s.exr" % g))
        save_combined(os.path.join(LDIR, "layer_%s.exr" % g), os.path.join(LDIR, "layer_" + g))
        restore_all()
    print("LAYERS DONE %.1f s" % (_t.time() - _T0), flush=True)
    JOB["shots"] = []
elif MODE_L == "statics_vol":         # the static media only (re-render after a lighting fix)
    set_loop_time(0.0)
    vol_wrap()
    cycles_setup(int(LOOP.get("vol_spp", 48)), RES, 0.01)
    for nm, flags in (("vol_strata", (True, False, False, False, True)), ("vol_rest", (False, True, True, False, True)),
                      ("beams_full", (True, True, True, True, False))):
        vol_show(*flags)
        timed_render(os.path.join(LDIR, nm + ".exr"))
        save_combined(os.path.join(LDIR, nm + ".exr"), os.path.join(LDIR, nm))
    vol_unwrap()
    print("STATICS_VOL DONE %.1f s" % (_t.time() - _T0), flush=True)
    JOB["shots"] = []
elif MODE_L == "beams":
    vol_wrap()
    vol_show(False, False, True, True, False)
    cycles_setup(int(LOOP.get("beam_spp", 32)), VRES, 0.02)
    for f in range(int(LOOP.get("f0", 0)), int(LOOP.get("f1", L_NF))):
        set_loop_time(f / L_FPS)
        p = os.path.join(LDIR, "beams_%03d.exr" % f)
        timed_render(p)
        save_combined(p, os.path.join(LDIR, "beams_%03d" % f))
    print("BEAMS DONE %.1f s" % (_t.time() - _T0), flush=True)
    JOB["shots"] = []
elif MODE_L == "dyn":
    for o in VOLUME_OBJS:
        o.hide_render = True
    emission_only(on_objs=tuple(o.name for o in DYN))
    cycles_setup(int(LOOP.get("dyn_spp", 64)), RES, 0.02)
    for f in range(int(LOOP.get("f0", 0)), int(LOOP.get("f1", L_NF))):
        set_loop_time(f / L_FPS)
        p = os.path.join(LDIR, "dyn_%03d.exr" % f)
        timed_render(p)
        save_combined(p, os.path.join(LDIR, "dyn_%03d" % f))
    print("DYN DONE %.1f s" % (_t.time() - _T0), flush=True)
    JOB["shots"] = []
else:
    JOB["shots"] = []
