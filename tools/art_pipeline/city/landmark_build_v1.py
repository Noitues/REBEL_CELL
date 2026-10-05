"""ART-5 5b: build one corporation landmark in Blender 5.2 headless and export it as glTF 2.0 (v1).

  blender -b --factory-startup --python landmark_build_v1.py -- <job> <outdir> <actions>
    job     : a key of landmark_spec_v1.JOBS (meridian_hq, solace_hq, solace_site, halcyon_hq, halcyon_site,
              orbital_hq, orbital_site, rebel_cell_district)
    actions : comma list of
      glb      -> <outdir>/<job>.glb and <outdir>/<job>.info.json (bounds, nodes, roles, animation, counts)
      preview  -> <outdir>/prev/<job>[_<state>]_{beauty,glow}_{day,night}.png + _{normal,id,depth}.png at the
                  job's reference camera (1280 x 720), around a stand-in city, for landmark_post_v1.py

Ported from art-pass 097a6c0 docs/concepts/round31_meridian_combat/scripts/hq_scene.py (the round 25-31 "one HQ
model" driver): the same builders (concept_r31/: target_corps primitives + materials, heroes24-31, unchanged), the
same seeds (2525 + the concept job name), Site placement (0.80, turned 45 deg) and reference cameras. What is new:
the city around the hero is not built into the asset (the game's CityModel is the city); the export meshes per
material ROLE with COLOR_0 (linear base colour x the per-triangle tone jitter; alpha = part id or a window's own
seeded value); moving parts as their own nodes with glTF animation (Halcyon's eye turns, the Solace chaser and the
Meridian crane + train loop as step-keyed scale flipbooks); Orbital's silo states as two nodes; the REBEL_CELL
district (landmark_district_v1.py).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import landmark_spec_v1 as SPEC  # noqa: E402

_C = os.path.join(_HERE, "concept_r31")
_argv = sys.argv[sys.argv.index("--") + 1:]
JOB, OUTDIR, ACTIONS = _argv[0], _argv[1], _argv[2].split(",")
SP = SPEC.JOBS[JOB]
sys.argv = [sys.argv[0], "--", SP["concept_job"], OUTDIR]  # target_corps reads its variant from argv
_SRC = open(os.path.join(_C, "target_corps.py"), encoding="utf-8-sig").read().splitlines()
exec("\n".join(_SRC[0:314]))  # setup + primitives + materials (scene reset, Acc, box, beam, ..., TOON, NEONM, WINM, SIGNM)

CORP, KIND = SP["corp"], SP["kind"]
VIEW = "close"
STATE = SP["states"][0]
SEED = 2525 + sum(map(ord, SP["concept_job"]))
rng = random.Random(SEED)
U = SPEC.LOT_BU
KH = U / 41.64
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
PLAZA_R = 27.5


def _ex(name):
    exec(open(os.path.join(_C, name), encoding="utf-8-sig").read(), globals())


_ex("heroes24.py")
KN = CORP_KNOBS[CORP]
exec("\n".join(_SRC[504:682]))  # container(), ziggurat(), depot()
_ex("heroes25.py")
_ex("heroes26.py")
_ex("heroes27.py")
if CORP == "meridian" and KIND == "hq":
    for _h in ("heroes28.py", "heroes29.py", "heroes30.py", "heroes31.py"):  # texture A, moat, crane keep, rail yard, loop
        _ex(_h)


def build_at(fn, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    """hq_scene.build_at: run a builder around the origin, then scale and move what it added (geometry and signs)."""
    accs = [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values())
    before = {id(a): len(a.bm.verts) for a in accs}
    objs0 = set(bpy.data.objects)
    fn()
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for acc in [SOLID, NEON, WIN, BEAM, LIT] + ANIM_ACCS + list(EYE_ACC.values()):
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


if KIND == "district":
    exec(open(os.path.join(_HERE, "landmark_district_v1.py"), encoding="utf-8").read(), globals())

# ------------------------------------------------------------------ concept materials (preview) + roles (export)
exec("\n".join(_SRC[693:783]))  # key light, world, MODES, TINT, set_mode, render, override_mat
MODES["day"] = dict(MODES["daycool"])  # the approved round 11b cool day
for _m in MODES.values():
    _m["sign"] = KN["sign"]


def mat_beam():
    """hq_scene.mat_beam: translucent light cones (emission mixed 0.22 over transparent)."""
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
LITM = TOON.copy()  # hq_scene: floodlit surfaces = toon + a warm self-light (emission 0.42 of the colour)
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
_set_mode0 = set_mode


def set_mode(m):
    _set_mode0(m)
    for e, e0 in zip(LIT_RAMP.color_ramp.elements, RAMP.color_ramp.elements):
        e.color = tuple(e0.color)


# role -> (concept preview material, export material name, emissive?)
ROLES = {
    "solid": (TOON, "lm_toon"), "lit": (LITM, "lm_lit"), "neon": (NEONM, "lm_neon"), "win": (WINM, "lm_win"),
    "beam": (BEAMM, "lm_beam"), "sign": (SIGNM, "lm_sign"),
    "lines": (TOON, "lm_toon_lines"), "win_ring": (WINM, "lm_win_ring"), "win_lines": (WINM, "lm_win_lines"),
    "win_fist_home": (WINM, "lm_win_fist_home"), "win_fist_dispatch": (WINM, "lm_win_fist_dispatch"),
}
WINDOW_SEEDED = {"win_ring", "win_lines", "win_fist_home", "win_fist_dispatch", "win"}  # alpha = the window's own value
LANDMARK = []      # every exported object
INFO = dict(job=JOB, corp=CORP, kind=KIND, seed=SEED, nodes=[], roles={}, animation=None, states=SP["states"])


def empty(name, parent=None):
    o = bpy.data.objects.new(name, None)
    scene.collection.objects.link(o)
    o.parent = parent
    LANDMARK.append(o)
    return o


def objectify(acc, role, name, parent):
    """Accumulator -> mesh object with its concept material (preview) and its role (export); None if empty."""
    if len(acc.bm.faces) == 0:
        acc.bm.free()
        return None
    o = acc.obj(ROLES[role][0])
    o.name = name
    o.data.name = name
    o.parent = parent
    o["lm_role"] = role
    LANDMARK.append(o)
    return o


def take_texts(parent, prefix):
    """The concept's sign text objects (FONT curves) -> meshes in the sign role."""
    out = []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in [o for o in bpy.data.objects if o.type == "FONT" and o not in LANDMARK]:
        o.data.resolution_u = SPEC.TEXT_RESOLUTION  # the concept's default 12 makes a sign heavier than its building
        dg.update()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(o.matrix_world)
        col = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        for d in col.data:
            d.color = tuple(KN["sign"]) + (1.0,)
        ob = bpy.data.objects.new("%s__sign_%d" % (prefix, len(out)), me)
        me.name = ob.name
        scene.collection.objects.link(ob)
        me.materials.append(SIGNM)
        ob.parent = parent
        ob["lm_role"] = "sign"
        LANDMARK.append(ob)
        out.append(ob)
        bpy.data.objects.remove(o, do_unlink=True)
    return out


def fresh_accs():
    global SOLID, NEON, WIN, BEAM, LIT
    SOLID, NEON, WIN, BEAM, LIT = Acc("solid"), Acc("neon"), Acc("win"), Acc("beam"), Acc("lit")


def static_objects(prefix, parent):
    objs = []
    for acc, role in ((SOLID, "solid"), (LIT, "lit"), (NEON, "neon"), (WIN, "win"), (BEAM, "beam")):
        o = objectify(acc, role, "%s__%s" % (prefix, role), parent)
        if o:
            objs.append(o)
    if KIND == "district":
        for role, acc in DIST_ACCS.items():
            o = objectify(acc, role, "%s__%s" % (prefix, role), parent)
            if o:
                objs.append(o)
    return objs + take_texts(parent, prefix)


# ------------------------------------------------------------------ build
ROOT = empty(JOB)
STATE_NODES = {}
ANIM = None  # dict(name, n, step, still, flips=[(node, [bool per frame])], slides=[(node, [x per frame])], rots=[(node, [deg per frame])])


def build_hero(state):
    global STATE
    STATE = state
    if KIND == "hq":
        HEROES26.get(CORP, HEROES25[CORP])()
    elif KIND == "site":
        build_at(SITES26[(CORP, state)], s=SPEC.SITE_SCALE, rot=SPEC.SITE_ROT)
    else:
        build_district()


def group_build(fn):
    """Run `fn` with SOLID / LIT / NEON / WIN / BEAM swapped for fresh accumulators; returns them."""
    global SOLID, LIT, NEON, WIN, BEAM
    g = dict(solid=Acc("g_s"), lit=Acc("g_l"), neon=Acc("g_n"), win=Acc("g_w"), beam=Acc("g_b"))
    old = (SOLID, LIT, NEON, WIN, BEAM)
    SOLID, LIT, NEON, WIN, BEAM = g["solid"], g["lit"], g["neon"], g["win"], g["beam"]
    try:
        fn()
    finally:
        SOLID, LIT, NEON, WIN, BEAM = old
    return g


def _face_key(f):
    return tuple(sorted((round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)) for v in f.verts))


def split_common(groups):
    """Moves the faces every group has (same corners, per role) into a new group and out of each group."""
    shared = dict(solid=Acc("c_s"), lit=Acc("c_l"), neon=Acc("c_n"), win=Acc("c_w"), beam=Acc("c_b"))
    for role in shared:
        sets = [{_face_key(f) for f in g[role].bm.faces} for g in groups]
        common = set.intersection(*sets) if sets else set()
        if not common:
            continue
        src = groups[0][role]
        for f in src.bm.faces:
            if _face_key(f) in common:
                shared[role].face([tuple(v.co) for v in f.verts], tuple(f[src.col])[:3], tuple(f[src.bid])[:3], fj=f[src.fj])
        for g in groups:
            bm = g[role].bm
            dead = [f for f in bm.faces if _face_key(f) in common]
            bmesh.ops.delete(bm, geom=dead, context="FACES")
    return shared


def group_objects(g, name, parent):
    node = empty(name, parent)
    for k in ("solid", "lit", "neon", "win", "beam"):
        objectify(g[k], k, "%s_%s" % (name, k), node)
    return node


if CORP == "meridian" and KIND == "hq":
    def meridian_static():
        """heroes31.fort_v31 without its per-frame loop: the castle, detailing, moat water and rail yard."""
        fort_v29_static()
        bolts_ladders_catwalks()
        faceted_water(S30 + 6.2, S30 + 11.5)
        rail_yard()

    HEROES26["meridian"] = meridian_static

    def meridian_loop():
        """heroes31's 20-frame loop regrouped for real time, frame for frame the same picture: the crane once per
        distinct pose (step flipbook), the train ONCE, slid along the loading track (translation), the container the
        crane sets down riding on it from frame 9 to 14, the motion streaks on frames 11-14 (step flipbook)."""
        loop = empty("%s__anim_loop" % JOB, ROOT)
        keys, groups, frame_pose = [], [], []
        for f in range(NFRAMES):
            c = crane31(f)
            key = (round(c["boom"], 5), round(c["t"], 5), round(c["cz"], 5), bool(c["carry"]))
            if key not in keys:
                rng.seed(SEED + 31)  # same draws per pose, so the parts that do not move come out identical
                keys.append(key)
                groups.append(group_build(lambda c=c: build_at(lambda: crane_dyn(c["boom"], c["t"], c["cz"], c["carry"]), rot=90.0)))
            frame_pose.append(keys.index(key))
        shared = split_common(groups)  # the portal, cabin and A-frame: once, always shown
        group_objects(shared, "%s__crane" % JOB, loop)
        poses = {}
        for i, g in enumerate(groups):
            poses[i] = group_objects(g, "%s__crane_p%02d" % (JOB, i), loop)
        frame_pose = [poses[i] for i in frame_pose]
        flips = [(node, [frame_pose[f] is node for f in range(NFRAMES)]) for node in poses.values()]
        empty_loaded = list(LOADED)
        empty_loaded[EMPTY_K] = False
        g = group_build(lambda: freight_train(0.0, TY, n=len(LOADED), loaded=empty_loaded, d=-1))
        train = group_objects(g, "%s__train" % JOB, loop)
        xk = 17 + 15 * EMPTY_K
        g = group_build(lambda: obox(xk, TY, 1.6, 12.0, 2.5, HC * 0.8, 0, CONT_LIV[(EMPTY_K * 3) % 5]))
        cargo = group_objects(g, "%s__train_cargo" % JOB, train)
        flips.append((cargo, [9 <= f <= 14 for f in range(NFRAMES)]))
        xs = [train_x(f) for f in range(NFRAMES)]
        for f in range(11, 15):
            g = group_build(lambda f=f: streaks(xs[f], TY, train_speed(f - 1) + 18))
            flips.append((group_objects(g, "%s__streaks_f%02d" % (JOB, f), loop), [k == f for k in range(NFRAMES)]))
        return dict(name="loop", n=NFRAMES, still=6, flips=flips, slides=[(train, xs)], rots=[])


if CORP == "orbital" and KIND == "hq":  # two silo states, each a full node: "state_closed" (default) and "state_open"
    for st, nm in (("", "state_closed"), ("open", "state_open")):
        rng.seed(SEED)
        fresh_accs()
        build_hero(st)
        node = empty("%s__%s" % (JOB, nm), ROOT)
        STATE_NODES[nm] = node
        if st:  # the sign is the same in both states: keep the first one only, on the root
            for o in [o for o in bpy.data.objects if o.type == "FONT" and o not in LANDMARK]:
                bpy.data.objects.remove(o, do_unlink=True)
        else:
            take_texts(ROOT, JOB)
        static_objects("%s__%s" % (JOB, nm), node)
else:
    build_hero(STATE)
    static_objects(JOB, ROOT)
    if EYE_ACC:  # Halcyon: the eye turns about the pylon axis (origin, z): its own pivot node
        piv = empty("%s__anim_eye" % JOB, ROOT)
        for k, role in (("solid", "solid"), ("neon", "neon"), ("beam", "beam")):
            objectify(EYE_ACC[k], role, "%s__eye_%s" % (JOB, k), piv)
        ANIM = dict(name="eye_scan", n=len(EYE_ANGLES), still=None, still_deg=28.0, flips=[], slides=[],
                    rots=[(piv, list(EYE_ANGLES))])
    elif CORP == "meridian" and KIND == "hq":
        ANIM = meridian_loop()
    elif any(len(a.bm.faces) for a in ANIM_ACCS):  # Solace: the LED chaser, one node per frame
        fl = empty("%s__anim_chaser" % JOB, ROOT)
        flips = []
        for f, a in enumerate(ANIM_ACCS):
            fn = empty("%s__chaser_f%02d" % (JOB, f), fl)
            objectify(a, "neon", "%s__chaser_f%02d_neon" % (JOB, f), fn)
            flips.append((fn, [k == f for k in range(len(ANIM_ACCS))]))
        ANIM = dict(name="chaser", n=len(ANIM_ACCS), still=0, flips=flips, slides=[], rots=[])
FLIP_OBJS = set()
if ANIM:
    for node, _vis in ANIM["flips"]:
        FLIP_OBJS.update(node.children_recursive)


def show_frame(f):
    """Preview: frame f of the moving parts (f < 0 = the concept's still)."""
    if not ANIM:
        return
    if f < 0 and ANIM.get("still") is None:
        for node, angs in ANIM["rots"]:
            node.rotation_euler = (0, 0, math.radians(ANIM["still_deg"]))
        return
    k = (ANIM["still"] if f < 0 else f) % ANIM["n"]
    for node, vis in ANIM["flips"]:
        for o in node.children_recursive:
            if o.type == "MESH" and o.parent is node:
                o.hide_render = not vis[k]
    for node, xs in ANIM["slides"]:
        node.location = (xs[k], 0, 0)
    for node, angs in ANIM["rots"]:
        node.rotation_euler = (0, 0, math.radians(angs[k]))


def anim_tracks():
    """The loop as glTF tracks (gltf_anim_v1): flipbooks = step-keyed scale 1 / 0, slides = translation (linear,
    with a jump key where the train wraps round), turns = rotation about +Y (linear)."""
    if not ANIM:
        return None
    n, step = ANIM["n"], SPEC.FRAME_S[JOB]
    times = [round(i * step, 6) for i in range(n + 1)]
    tracks = []
    for node, vis in ANIM["flips"]:
        vals = [[1.0, 1.0, 1.0] if vis[i % n] else [0.0, 0.0, 0.0] for i in range(n + 1)]
        tracks.append(dict(node=node.name, path="scale", interp="STEP", times=times, values=vals))
    for node, xs in ANIM["slides"]:
        ts, vs = [], []
        for i in range(n + 1):
            x = xs[i % n]
            if i and abs(x - xs[(i - 1) % n]) > 200.0:  # the wrap: jump just after the previous frame
                ts.append(round(times[i - 1] + 0.001, 6))
                vs.append([x, 0.0, 0.0])
            ts.append(times[i])
            vs.append([x, 0.0, 0.0])
        tracks.append(dict(node=node.name, path="translation", interp="LINEAR", times=ts, values=vs))
    for node, angs in ANIM["rots"]:
        vals = []
        for i in range(n + 1):
            h = math.radians(angs[i % n]) / 2
            vals.append([0.0, math.sin(h), 0.0, math.cos(h)])
        tracks.append(dict(node=node.name, path="rotation", interp="LINEAR", times=times, values=vals))
    return tracks


def bounds(objs):
    lo, hi = [1e9] * 3, [-1e9] * 3
    for o in objs:
        if o.type != "MESH":
            continue
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            for i in range(3):
                lo[i], hi[i] = min(lo[i], w[i]), max(hi[i], w[i])
    return [round(x, 3) for x in lo], [round(x, 3) for x in hi]


# ------------------------------------------------------------------ preview renders (concept toon + passes)
def stand_in_city():
    """A seeded stand-in skyline around the hero for the reference comparisons only (never exported)."""
    r = random.Random(77)
    fill, filln, fillw = Acc("fill"), Acc("filln"), Acc("fillw")
    fams = KN["fams"] or [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.48, 0.44, 0.36)]
    trims = KN["trims"] or [AMBER, AMBER, CYAN, PINK]
    wins = KN["win"] or WIN_COLS
    cam_p, _, _ = SP["cam"] if SP["cam"] != "iso" else ((0, 0, 0), None, None)
    cx, cy = cam_p[0], cam_p[1]
    D = math.hypot(cx, cy) or 1.0
    keep = (34.0 if KIND == "hq" else 22.0)
    R = 260.0 if KIND == "hq" else 150.0
    n = int(R / U)
    fill.face([(-R * 2, -R * 2, -0.05), (R * 2, -R * 2, -0.05), (R * 2, R * 2, -0.05), (-R * 2, R * 2, -0.05)], (0.13, 0.13, 0.16), (0, 0, 0))
    lane = KN["lanes"]
    for i in range(-n, n + 1):
        if i % 4:
            continue
        c = i * U + U / 2
        for (a, b) in (((c, -R), (c, R)), ((-R, c), (R, c))):
            col = lane[abs(i // 4) % 2]
            strip(filln, a, b, U * 0.85, 0.02, tuple(v * 0.12 for v in col))
            strip(filln, a, b, 0.25, 0.04, tuple(v * 0.8 for v in col))
    for i in range(-n, n):
        for j in range(-n, n):
            if i % 4 == 0 or j % 4 == 0:
                continue
            x0, y0 = i * U, j * U
            xm, ym = x0 + U / 2, y0 + U / 2
            if max(abs(xm), abs(ym)) < keep or math.hypot(xm, ym) > R:
                continue
            t = (xm * cx + ym * cy) / (D * D)
            if 0 < t < 1 and abs(xm * cy - ym * cx) / D < 26:  # the view corridor (concept citydata.blocks_view)
                continue
            if r.random() < 0.08:
                continue
            hr = r.random()
            h = 4 + 24 * hr * hr + (r.uniform(14, 36) if r.random() < 0.06 else 0)
            ins = r.uniform(0.5, 1.2)
            col = fams[r.randrange(len(fams))]
            bid = (r.random(), r.random(), r.random())
            x0, y0, x1, y1 = x0 + ins, y0 + ins, x0 + U - ins, y0 + U - ins
            b = [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]
            u_ = [(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)]
            for k in range(4):
                fill.facet_quad(b[k], b[(k + 1) % 4], u_[(k + 1) % 4], u_[k], col, bid)
            fill.face(u_, tuple(min(1, v * 1.08) for v in col), bid)
            for (pa, pb, nx, ny) in (((x0, y0), (x1, y0), 0, -1), ((x1, y0), (x1, y1), 1, 0)):
                L = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
                for uu in range(int((L - 0.6) / 1.6)):
                    for vv in range(int((h - 1.6) / 1.9)):
                        if r.random() > 0.22:
                            continue
                        t0 = 0.7 + uu * 1.6
                        ux, uy = (pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L
                        p0 = (pa[0] + ux * t0 + nx * 0.05, pa[1] + uy * t0 + ny * 0.05)
                        p1 = (p0[0] + ux * 0.8, p0[1] + uy * 0.8)
                        z = 1.6 + vv * 1.9
                        wc = wins[r.randrange(len(wins))]
                        s = 0.5 + 0.5 * r.random()
                        fillw.face([(p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z + 0.7), (p0[0], p0[1], z + 0.7)], tuple(c * s for c in wc), (0, 0, 0))
            if r.random() < 0.42:
                ink = trims[r.randrange(len(trims))]
                for k in range(4):
                    beam(u_[k], u_[(k + 1) % 4], 0.22, ink, acc=filln)
    return [fill.obj(TOON), filln.obj(NEONM), fillw.obj(WINM)]


def preview():
    pdir = os.path.join(OUTDIR, "prev")
    os.makedirs(pdir, exist_ok=True)
    extra = stand_in_city() if KIND != "district" else []
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.clip_end = 5000
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    if SP["cam"] == "iso":
        import landmark_crest_v1 as CR
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = SP["iso_ortho"]
        tgt = Vector(CR.UP) * CR.YC
        cam.location = tuple(tgt - Vector(CR.FWD) * 2600)
    else:
        loc, tgt, lens = SP["cam"]
        tgt = Vector(tgt)
        cam.location = loc
        cam_data.lens = lens
    cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    try:
        scene.eevee.shadow_pool_size = "1024"
    except Exception:
        pass
    scene.eevee.taa_render_samples = 16
    show_frame(-1)
    meshes = [o for o in LANDMARK if o.type == "MESH"] + extra
    variants = [("", None)]
    if STATE_NODES:
        variants = [("_" + k.replace("state_", ""), k) for k in STATE_NODES]
    if KIND == "district":
        variants = [("_home_lit", "lit"), ("_home", "home"), ("_dispatch", "dispatch")]

    def pick(v):
        for o in LANDMARK:
            if o.type != "MESH":
                continue
            hide = False
            if STATE_NODES and v:
                hide = o.parent in STATE_NODES.values() and o.parent is not STATE_NODES[v]
            role = o.get("lm_role", "")
            if KIND == "district":
                if role in ("win_ring", "win_lines"):
                    hide = v != "lit"
                elif role == "win_fist_home":
                    hide = v == "dispatch"
                elif role == "win_fist_dispatch":
                    hide = v != "dispatch"
            if o in FLIP_OBJS:
                continue
            o.hide_render = hide

    blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
    for tag, v in variants:
        pick(v)
        modes = ("day", "night") if (tag in ("", "_closed", "_home")) else ("night",)
        base = os.path.join(pdir, JOB + tag)
        saved = {o.name: o.data.materials[0] for o in meshes}
        for m in modes:
            set_mode(m)
            render(base + "_beauty_%s.png" % m)
        for o in meshes:
            if saved[o.name] in (TOON, LITM):
                o.data.materials[0] = blackm
        for m in modes:
            set_mode(m)
            bg.inputs["Color"].default_value = (0, 0, 0, 1)
            render(base + "_glow_%s.png" % m)
        for o in meshes:
            o.data.materials[0] = saved[o.name]
        hidden = [o for o in meshes if saved[o.name] is BEAMM and not o.hide_render]
        for o in hidden:
            o.hide_render = True
        bg.inputs["Color"].default_value = (0, 0, 0, 1)
        scene.eevee.taa_render_samples = 4
        for kind in ("normal", "id", "depth"):
            bpy.context.view_layer.material_override = override_mat(kind)
            if kind == "depth":
                bg.inputs["Color"].default_value = (1, 1, 1, 1)
            render(base + "_%s.png" % kind)
        bpy.context.view_layer.material_override = None
        for o in hidden:
            o.hide_render = False
        scene.eevee.taa_render_samples = 16
    for o in extra:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.objects.remove(cam, do_unlink=True)


# ------------------------------------------------------------------ glTF export
def part_alpha(bid):
    """The part value of a concept part id, for material-edge ink: the shader writes it to ROUGHNESS, so it stays in
    0.55-1.0 (art_export/1, as 8p: >= 0.5 marks a building for the spike post pass; neighbouring parts differ)."""
    h = math.sin(bid[0] * 12.9898 + bid[1] * 78.233 + bid[2] * 37.719) * 43758.5453
    return SPEC.PART_ALPHA[0] + (SPEC.PART_ALPHA[1] - SPEC.PART_ALPHA[0]) * (h - math.floor(h))


def export_material(name, role):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "COLOR_0"
    nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 1.0
    bs.inputs["Metallic"].default_value = 0.0
    if role == "beam":
        bs.inputs["Alpha"].default_value = 0.22
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    nt.links.new(bs.outputs[0], out.inputs[0])
    return m


def prep_export(o):
    """Face attributes -> one CORNER colour attribute COLOR_0 (linear; rgb = col x tone, a = part id / window value)."""
    me = o.data
    role = o.get("lm_role", "solid")
    if role == "sign":
        src = me.color_attributes["col"]
        dst = me.color_attributes.new("COLOR_0", "FLOAT_COLOR", "CORNER")
        for i, d in enumerate(src.data):
            dst.data[i].color = tuple(KN["sign"]) + (1.0,)
        me.color_attributes.remove(me.color_attributes["col"])
    else:
        col = me.attributes["col"].data
        fj = me.attributes["fj"].data
        bid = me.attributes["bid"].data
        dst = me.color_attributes.new("COLOR_0", "FLOAT_COLOR", "CORNER")
        toon = role in ("solid", "lit", "lines")
        for p in me.polygons:
            c = col[p.index].color
            t = fj[p.index].value
            k = (SPEC.TONE[0] + (SPEC.TONE[1] - SPEC.TONE[0]) * t) if toon else 1.0
            a = t if role in WINDOW_SEEDED else part_alpha(bid[p.index].color)
            rgba = (c[0] * k, c[1] * k, c[2] * k, a)
            for li in p.loop_indices:
                dst.data[li].color = rgba
        for nm in ("col", "fj", "bid"):
            me.attributes.remove(me.attributes[nm])
    me.color_attributes.active_color = dst
    me.color_attributes.render_color_index = me.color_attributes.find("COLOR_0")
    me.materials.clear()
    me.materials.append(export_material(ROLES[role][1], role))


def rest_pose():
    """The exported rest pose = the concept's still: flipbook nodes at scale 1 only on the still frame, the train at
    its still position, the eye turned to its still angle (so a landmark that is not animated shows the still)."""
    if not ANIM:
        return
    if ANIM.get("still") is None:
        for node, _a in ANIM["rots"]:
            node.rotation_euler = (0, 0, math.radians(ANIM["still_deg"]))
        return
    k = ANIM["still"]
    for node, vis in ANIM["flips"]:
        s = 1.0 if vis[k] else 0.0
        node.scale = (s, s, s)
    for node, xs in ANIM["slides"]:
        node.location = (xs[k], 0, 0)


def export_glb():
    import gltf_anim_v1
    for o in list(bpy.data.objects):
        if o not in LANDMARK:
            bpy.data.objects.remove(o, do_unlink=True)
    for o in LANDMARK:
        o.hide_render = False
        o.hide_viewport = False
        if o.type == "MESH":
            prep_export(o)
    meshes = [o for o in LANDMARK if o.type == "MESH"]
    moving = set(FLIP_OBJS)
    if ANIM:
        for node, _x in ANIM["slides"]:
            moving.update(node.children_recursive)
    rest_pose()
    bpy.context.view_layer.update()
    lo, hi = bounds([o for o in meshes if o not in moving])
    INFO["bounds_concept"] = dict(min=lo, max=hi)
    INFO["bounds_gltf"] = dict(min=[lo[0], lo[2], -hi[1]], max=[hi[0], hi[2], -lo[1]])
    INFO["triangles"] = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    INFO["triangles_by_role"] = {}
    for o in meshes:
        r = ROLES[o["lm_role"]][1]
        INFO["triangles_by_role"][r] = INFO["triangles_by_role"].get(r, 0) + sum(len(p.vertices) - 2 for p in o.data.polygons)
    for o in LANDMARK:
        INFO["nodes"].append(o.name)
        if o.type == "MESH":
            r = o["lm_role"]
            INFO["roles"].setdefault(ROLES[r][1], 0)
            INFO["roles"][ROLES[r][1]] += 1
    path = os.path.join(OUTDIR, JOB + ".glb")
    props = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    # NORMAL per SPEC.EXPORT_NORMALS (shading uses the facet normal from screen derivatives; shadows use NORMAL)
    kw = dict(filepath=path, export_format="GLB", export_yup=True, export_apply=False, export_texcoords=False,
              export_normals=SPEC.EXPORT_NORMALS, export_materials="EXPORT", export_cameras=False, export_lights=False,
              export_animations=False, export_extras=False)
    for k, v in (("export_vertex_color", "ACTIVE"), ("export_all_vertex_colors", False), ("export_tangents", False),
                 ("export_attributes", False), ("export_active_vertex_color_when_no_material", True),
                 ("export_shared_accessors", True)):
        if k in props:
            kw[k] = v
    bpy.ops.export_scene.gltf(**kw)
    tracks = anim_tracks()
    if tracks:
        gltf_anim_v1.add_animations(path, {ANIM["name"]: tracks})
        INFO["animation"] = dict(name=ANIM["name"], frames=ANIM["n"], seconds_per_frame=SPEC.FRAME_S[JOB],
                                 loop_seconds=round(ANIM["n"] * SPEC.FRAME_S[JOB], 3), still_frame=ANIM.get("still"),
                                 still_deg=ANIM.get("still_deg"), tracks=len(tracks),
                                 note="rest pose = the concept's still; play the animation looped")
    INFO["exporter_settings"] = {k: v for k, v in kw.items() if k != "filepath"}
    INFO["blender"] = bpy.app.version_string
    with open(os.path.join(OUTDIR, JOB + ".info.json"), "w", encoding="utf-8") as f:
        json.dump(INFO, f, indent=1)
    print("EXPORTED", path, os.path.getsize(path), flush=True)


if "preview" in ACTIONS:
    preview()
if "glb" in ACTIONS:
    export_glb()
print("DONE", flush=True)
