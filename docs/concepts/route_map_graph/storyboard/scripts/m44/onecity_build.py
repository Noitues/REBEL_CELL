"""Storyboard v3 (one continuous city), exec'd inside onecity_scene.py right after the city buildings are built.

The route buildings were built by the city's own builder (city_building, the mainline kit) into their own accumulators
(RB solid / RBW windows / RBN neon), in their normal order, so the rest of the city and the shared stream are unchanged.
Here, by the derivation in sb_onecity.py (the job's "onecity" block):
  - the facade cells and windows of each route building that fall inside a room opening are cut out;
  - each opening gets its own WALL object (the building's colour, the kit's facets and windows): closed in the dive,
    dissolved in the REVEAL;
  - each room is an interior box (floor, ceiling, back, sides) in its node type colour, with a lit back panel and a
    frame; its light is an area light (seen by Cycles only through the opening).
"""
import bmesh as _bm

OC = JOB_OC
ROOM_TL = {"router": (0.36, 0.88, 1.0), "elite": (1.0, 0.38, 0.16), "terminal": (0.24, 1.0, 0.55),
           "modem": (0.35, 0.59, 1.0), "rack": (1.0, 0.77, 0.24), "target": (1.0, 0.17, 0.24), "start": (0.83, 1.0, 0.0)}
OPEN = []          # (room id, axis, face, u0, u1, z0, z1, nrm)
for _i, _r in sorted(OC["rooms"].items()):
    _f = _r["front"]
    _ax = 0 if abs(_f[0][1] - _f[1][1]) < 1e-6 else 1
    _u = [p[_ax] for p in _f]
    _face = _f[0][1] if _ax == 0 else _f[0][0]
    _b = _r["back"]
    _nrm = 1.0 if ((_b[0][1] if _ax == 0 else _b[0][0]) > _face) else -1.0
    OPEN.append((_i, _ax, _face, min(_u), max(_u), _f[0][2], _f[2][2], _nrm))


def _in_open(c, pad=0.12, near=0.45):
    for (i, ax, face, u0, u1, z0, z1, nrm) in OPEN:
        u = c[ax]
        d = c[1 - ax] - face
        if u0 - pad < u < u1 + pad and z0 - pad < c[2] < z1 + pad and -near < d * nrm < 0.25:
            return i
    return None


def _cut(acc):
    dead = [f for f in acc.bm.faces if _in_open(f.calc_center_median()) is not None]
    _bm.ops.delete(acc.bm, geom=dead, context="FACES")
    return len(dead)


n1, n2, n3 = _cut(RB), _cut(RBW), _cut(RBN)
print("ONECITY cut faces", n1, n2, n3, flush=True)

WALLS = {}
ROOM_LIGHTS = []
RINT = Acc("oc_rooms")          # room interiors (surfaces)
RPAN = Acc("oc_panels")         # lit back panels (emissive)
_bcol = {}
for b in LAY["buildings"]:
    if b["key"] in OC["route_keys"]:
        fam = FAMS_C[abs(b["key"]) % len(FAMS_C)]
        tc = TERR.get(b["terr"], (0.8, 0.8, 0.8))
        _bcol[b["key"]] = mixc(fam, tc, 0.28 if b["terr"] else 0.0)
for (i, ax, face, u0, u1, z0, z1, nrm) in OPEN:
    r = OC["rooms"][i]
    col = _bcol.get(r["bld"], (0.4, 0.38, 0.46))
    rr = random.Random(abs(r["bld"]) * 31 + len(i))

    def P(u, d, z):
        return (u, face + d * nrm, z) if ax == 0 else (face + d * nrm, u, z)
    # the wall over the opening: the kit's facade cells + windows, its own object (dissolvable)
    wa, ww = Acc("oc_wall_" + i), Acc("oc_wallw_" + i)
    A_, B_, C_, D_ = P(u0 - 0.12, -0.03, z0 - 0.12), P(u1 + 0.12, -0.03, z0 - 0.12), P(u1 + 0.12, -0.03, z1 + 0.12), P(u0 - 0.12, -0.03, z1 + 0.12)
    _keep = CITY
    CITY = wa
    fgrid(A_, B_, C_, D_, col, rid(), rr)
    CITY = _keep
    nxw = int((u1 - u0 - 0.6) / 1.6)
    for uu in range(max(1, nxw)):
        if rr.random() > 0.35:
            continue
        t0 = u0 + 0.3 + uu * 1.6 + 0.4
        zz = z0 + (z1 - z0) * 0.35
        wc = rr.choice(WIN_COLS)
        s = 0.5 + 0.5 * rr.random()
        ww.face([P(t0, -0.08, zz), P(t0 + 0.8, -0.08, zz), P(t0 + 0.8, -0.08, zz + 0.7), P(t0, -0.08, zz + 0.7)],
                tuple(v * s for v in wc), (0, 0, 0))
    WALLS[i] = (wa, ww)
    # the room: floor, ceiling, back, sides (dark), a lit back panel in the type colour, a cut frame
    tl = ROOM_TL.get(r["kind"], (0.8, 0.8, 0.9))
    dk = tuple(0.18 + 0.25 * v for v in tl)
    dep = 2.4
    RINT.face([P(u0, 0, z0), P(u1, 0, z0), P(u1, dep, z0), P(u0, dep, z0)], tuple(v * 0.7 for v in dk), rid())
    RINT.face([P(u0, dep, z1), P(u1, dep, z1), P(u1, 0, z1), P(u0, 0, z1)], tuple(v * 0.5 for v in dk), rid())
    RINT.face([P(u0, dep, z0), P(u1, dep, z0), P(u1, dep, z1), P(u0, dep, z1)], dk, rid())
    RINT.face([P(u0, 0, z0), P(u0, dep, z0), P(u0, dep, z1), P(u0, 0, z1)], tuple(v * 0.8 for v in dk), rid())
    RINT.face([P(u1, dep, z0), P(u1, 0, z0), P(u1, 0, z1), P(u1, dep, z1)], tuple(v * 0.8 for v in dk), rid())
    pw = min(u1 - u0 - 0.6, 3.2)
    pc = (u0 + u1) / 2
    RPAN.face([P(pc - pw / 2, dep - 0.04, z0 + 0.35), P(pc + pw / 2, dep - 0.04, z0 + 0.35),
               P(pc + pw / 2, dep - 0.04, z1 - 0.3), P(pc - pw / 2, dep - 0.04, z1 - 0.3)], tl, (0, 0, 0))
    for (a_, b_) in (((u0, z0), (u1, z0)), ((u1, z0), (u1, z1)), ((u1, z1), (u0, z1)), ((u0, z1), (u0, z0))):
        beam(P(a_[0], -0.02, a_[1]), P(b_[0], -0.02, b_[1]), 0.16, (0.15, 0.13, 0.19), acc=RINT)
    ROOM_LIGHTS.append((i, P(pc, dep * 0.5, z1 - 0.1), tl, (u1 - u0), dep))

RB_OBJ = RB.obj(TOON)
RBW_OBJ = RBW.obj(WINM)
RBN_OBJ = RBN.obj(NEONM)
RINT_OBJ = RINT.obj(TOON)
RPAN_OBJ = RPAN.obj(NEONM)
WALL_OBJS = {}
for i, (wa, ww) in WALLS.items():
    WALL_OBJS[i] = (wa.obj(TOON), ww.obj(WINM))
ONECITY_SOLIDS = [RB_OBJ, RINT_OBJ] + [w[0] for w in WALL_OBJS.values()]
print("ONECITY rooms", len(OPEN), "walls", len(WALL_OBJS), flush=True)


def set_walls(dis):
    """dis: {room: 0 closed .. 1 gone} (the proof renders closed walls in the dive, open for the reveal preview)."""
    for i, (wa, ww) in WALL_OBJS.items():
        h = float(dis.get(i, 0.0)) >= 0.5
        wa.hide_render = h
        ww.hide_render = h


# ------------------------------------------------------------------ the SECTION rule (a continuous city needs it)
# In a real city the blocks across the street stand between any side-view camera and the netrun street. The rule cuts
# them like a section model: inside the corridor in front of the street (the camera side of the street centre line,
# along the street +- corridor_pad), everything above z_cut is not drawn. z_cut follows the zoom (look preset
# section_by_zoom): far above every roof at the HQ, lowering through the dive to a plinth at the street. Same geometry,
# a clip in the materials (in Godot: a section-plane uniform in the city shaders, as for the wall dissolve).
_SC = OC["street"]
_SA, _SCc = _SC["a"], _SC["c"]
_NRM = OC.get("nrm", [0.0, 1.0])
_PAD = float(OC.get("corridor_pad", 30.0))
_X0, _X1 = min(_SA[0], _SCc[0]), max(_SA[0], _SCc[0])
_Y0, _Y1 = min(_SA[1], _SCc[1]), max(_SA[1], _SCc[1])
bpy.context.scene["oc_zcut"] = 1.0e4


def section(mat):
    """Insert the section clip in front of a material's surface output (idempotent)."""
    if mat is None or mat.node_tree is None or mat.get("oc_section"):
        return
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None or not out.inputs["Surface"].links:
        return
    src = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs[0])
    zc = nt.nodes.new("ShaderNodeAttribute")
    zc.attribute_type = "VIEW_LAYER"
    zc.attribute_name = "oc_zcut"

    def M(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for k, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[k].default_value = v
            else:
                nt.links.new(v, n.inputs[k])
        return n.outputs[0]
    X, Y, Z = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
    # the camera side of the street centre line, along the street (+- pad)
    if abs(_NRM[1]) > 0.5:
        side = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", Y, _SA[1]), _NRM[1]), -0.4)
        along = M("MULTIPLY", M("GREATER_THAN", X, _X0 - _PAD), M("LESS_THAN", X, _X1 + _PAD))
    else:
        side = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", X, _SA[0]), _NRM[0]), -0.4)
        along = M("MULTIPLY", M("GREATER_THAN", Y, _Y0 - _PAD), M("LESS_THAN", Y, _Y1 + _PAD))
    above = M("GREATER_THAN", Z, zc.outputs["Fac"])
    cut = M("MULTIPLY", M("MULTIPLY", side, along), above)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cut, mx.inputs[0])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    mat["oc_section"] = True


def section_all(skip=()):
    for m in bpy.data.materials:
        if m.name in skip:
            continue
        section(m)
