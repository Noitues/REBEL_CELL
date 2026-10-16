"""HQ Halcyon: build the spiral compound + the Cell's 360 degree ring city in Blender and render frames (Cycles HIP).

blender -b --factory-startup --python hq_scene.py -- <job.json>
job: layout (hq_graph.dump), out, res [w, h], samples, threshold, step_rate, ov_pose (the overview pose),
     frames: [{name, pose {loc, tgt, lens, shift_x, shift_y}, zoom (LOD 0 overview .. 1 decision),
               room_state {id: state}, scanned [ids], eye {az (deg, rig yaw convention), face, sweep (z or null),
               wash 0..1, beam 0..1}, power {keep, k, boost} | null}]
The scene is built ONCE; every frame only moves the camera and the eye, re-weights rooms / LOD layers and renders
(persistent data). Everything is placed by rule from the layout + halcyon_preset; NOTES lists the gaps.
Seeds: build 4311 (city), 9402 (lanes), 9500 (beams), 9510 (plumes), 9520 (glows); the window grid is in-shader.
"""
import json
import math
import os
import random
import sys
import time

import bpy
from mathutils import Matrix, Vector

T0 = time.time()
argv = sys.argv[sys.argv.index("--") + 1:]
JOB = json.load(open(argv[0]))
LY = json.load(open(JOB["layout"]))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import halcyon_preset as HP  # noqa: E402

P = HP.PRESET
HZ = P["halcyon"]
CP = HZ["compound"]
HF = P["halcyon_fog"]
LOD = P["lod_bands"]
pal = HP.pal
C = LY["const"]
NF = [tuple(v) for v in LY["N"]]
TF = [tuple(v) for v in LY["T"]]
OUT = JOB["out"]
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def log(*a):
    print("[hq %.1fs]" % (time.time() - T0), *a, flush=True)


def sstep(x, a, b):
    t = max(0.0, min(1.0, (x - a) / max(1e-6, b - a)))
    return t * t * (3 - 2 * t)


# ================================================================== mesh accumulators
class Acc:
    def __init__(self, name, mat, idx, coll=None):
        self.name, self.mat, self.idx, self.coll = name, mat, idx, coll
        self.v, self.f, self.c, self.k = [], [], [], []
        self.b, self.cur_bc = [], (0.0, 0.0, 0.0, 0.0, 0.0)  # v3: the occlusion rule's building per face (x y top hx hy)

    def face(self, pts, col, k=0.0):
        b = len(self.v)
        self.v.extend(tuple(p) for p in pts)
        self.f.append(tuple(range(b, b + len(pts))))
        self.c.append(tuple(col)[:3] + (1.0,))
        self.k.append(float(k))
        self.b.append(self.cur_bc)

    def build(self):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.validate()
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        ka = me.attributes.new("k", "FLOAT", "FACE")
        cols = []
        for poly in me.polygons:
            c = self.c[poly.index]
            ka.data[poly.index].value = self.k[poly.index]
            for _ in poly.loop_indices:
                cols.extend(c)
        ca.data.foreach_set("color", cols)
        if any(b_[2] for b_ in self.b):
            ba = me.attributes.new("bc", "FLOAT_VECTOR", "FACE")
            ba.data.foreach_set("vector", [v_ for b_ in self.b for v_ in b_[:3]])
            bh_ = me.attributes.new("bh", "FLOAT_VECTOR", "FACE")
            bh_.data.foreach_set("vector", [v_ for b_ in self.b for v_ in (b_[3], b_[4], 0.0)])
        ob = bpy.data.objects.new(self.name, me)
        (self.coll or scene.collection).objects.link(ob)
        ob.data.materials.append(self.mat)
        ob.pass_index = self.idx
        ob["pwo"] = 1.0
        return ob


def box(acc, x0, y0, z0, x1, y1, z1, col, k=0.0, top=True, bottom=False):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    acc.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], col, k)
    acc.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], col, k)
    acc.face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], col, k)
    acc.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col, k)
    if top:
        acc.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], col, k)
    if bottom:
        acc.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], col, k)


def fp(f, d, u, z):
    n, t = NF[f], TF[f]
    return (n[0] * d + t[0] * u, n[1] * d + t[1] * u, z)


def fbox(acc, f, d0, d1, u0, u1, z0, z1, col, k=0.0, top=True, bottom=False):
    a, b = fp(f, d0, u0, z0), fp(f, d1, u1, z1)
    box(acc, a[0], a[1], z0, b[0], b[1], z1, col, k, top, bottom)


def fquad(acc, f, d, u0, z0, u1, z1, col, k=0.0):
    acc.face([fp(f, d, u0, z0), fp(f, d, u1, z0), fp(f, d, u1, z1), fp(f, d, u0, z1)], col, k)


def tube(acc, p0, p1, r, col, k=0.0, n=8):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    if d.length < 1e-4:
        return
    d.normalize()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    ring = [u * math.cos(2 * math.pi * i / n) * r + v * math.sin(2 * math.pi * i / n) * r for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        acc.face([a + ring[i], a + ring[j], b + ring[j], b + ring[i]], col, k)


def fdisc(acc, f, d, u, z, r, col, k=0.0, n=32):
    acc.face([fp(f, d, u + r * math.cos(2 * math.pi * i / n), z + r * math.sin(2 * math.pi * i / n)) for i in range(n)],
             col, k)


# ================================================================== materials
def nn(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        n.inputs[k.replace("_", " ")].default_value = v
    return n


def mth(nt, op, a, b=None, c=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def vsc(nt, vec, s):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = "SCALE"
    nt.links.new(vec, n.inputs[0])
    if isinstance(s, (int, float)):
        n.inputs["Scale"].default_value = s
    else:
        nt.links.new(s, n.inputs["Scale"])
    return n.outputs[0]


def vmul(nt, a, b):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = "MULTIPLY"
    nt.links.new(a, n.inputs[0])
    n.inputs[1].default_value = b
    return n.outputs[0]


def mixc(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = tuple(v)[:3] + (1.0,)
        else:
            nt.links.new(v, sock)
    return n.outputs[2]


def smooth(nt, v, a, b):
    n = nt.nodes.new("ShaderNodeMapRange")
    n.interpolation_type = "SMOOTHSTEP"
    n.inputs["From Min"].default_value = a
    n.inputs["From Max"].default_value = b
    nt.links.new(v, n.inputs["Value"])
    return n.outputs[0]


def attr(nt, name, kind="GEOMETRY"):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_type = kind
    n.attribute_name = name
    return n


def new_mat(name):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:  # noqa: BLE001
        pass
    m.node_tree.nodes.clear()
    return m, m.node_tree


def pos_sep(nt):
    g = nt.nodes.new("ShaderNodeNewGeometry")
    s = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(g.outputs["Position"], s.inputs[0])
    ns = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(g.outputs["Normal"], ns.inputs[0])
    return g, s, ns


def mat_civic():
    """White composite panels, wet: a panel grid on (x + y, z), soft grime, rain streaks, coat."""
    m, nt = new_mat("civic")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    g, ps, ns = pos_sep(nt)
    cxyz = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"]), cxyz.inputs[0])
    nt.links.new(ps.outputs["Z"], cxyz.inputs[1])
    br = nn(nt, "ShaderNodeTexBrick", Scale=1.0, Mortar_Size=0.035, Bias=0.0, Brick_Width=2.3, Row_Height=1.62)
    br.offset = 0.0
    nt.links.new(cxyz.outputs[0], br.inputs["Vector"])
    n1 = nn(nt, "ShaderNodeTexNoise", Scale=0.06, Detail=4.0, Roughness=0.6)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    gm = smooth(nt, n1.outputs["Fac"], 0.3, 0.75)
    n2 = nn(nt, "ShaderNodeTexNoise", Scale=0.9, Detail=3.0)
    nt.links.new(vmul(nt, g.outputs["Position"], (1.0, 1.0, 0.08)), n2.inputs["Vector"])
    streak = smooth(nt, n2.outputs["Fac"], 0.5, 0.78)
    k = mth(nt, "MULTIPLY", mth(nt, "ADD", 0.88, mth(nt, "MULTIPLY", gm, 0.16)),
            mth(nt, "SUBTRACT", 1.0, mth(nt, "MULTIPLY", streak, 0.22)))
    seam = smooth(nt, br.outputs["Fac"], 0.0, 1.0)
    base = vsc(nt, col.outputs["Color"], mth(nt, "MULTIPLY", k, mth(nt, "ADD", 0.78, mth(nt, "MULTIPLY", 0.22, seam))))
    nt.links.new(base, b.inputs["Base Color"])
    nt.links.new(mth(nt, "ADD", 0.16, mth(nt, "MULTIPLY", streak, 0.22)), b.inputs["Roughness"])
    b.inputs["Coat Weight"].default_value = 0.35
    b.inputs["Coat Roughness"].default_value = 0.08
    bump = nn(nt, "ShaderNodeBump", Strength=0.25, Distance=0.05)
    nt.links.new(seam, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_plain(name, rough=0.55, spec=0.5, metal=0.0, coat=0.0):
    m, nt = new_mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    g, ps, ns = pos_sep(nt)
    n1 = nn(nt, "ShaderNodeTexNoise", Scale=0.4, Detail=5.0, Roughness=0.6)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    nt.links.new(vsc(nt, col.outputs["Color"], mth(nt, "ADD", 0.8, mth(nt, "MULTIPLY", n1.outputs["Fac"], 0.4))),
                 b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_glass():
    m, nt = new_mat("glass")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    nt.links.new(col.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["Specular IOR Level"].default_value = 0.9
    b.inputs["Coat Weight"].default_value = 0.5
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_emit(name, k=1.0):
    m, nt = new_mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    col = attr(nt, "col")
    kf = attr(nt, "k")
    pw = attr(nt, "pwo", "OBJECT")
    nt.links.new(col.outputs["Color"], em.inputs["Color"])
    nt.links.new(mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", kf.outputs["Fac"], pw.outputs["Fac"]), k), em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_lock():
    """Red holo lockdown over a scanned room's opening: horizontal scan lines + a vertical grid, translucent."""
    m, nt = new_mat("lockdown")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g, ps, ns = pos_sep(nt)
    col = attr(nt, "col")
    pw = attr(nt, "pwo", "OBJECT")
    wave = nn(nt, "ShaderNodeTexWave", Scale=1.0, Distortion=0.0)
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.wave_profile = "SAW"
    nt.links.new(vsc(nt, g.outputs["Position"], 0.11), wave.inputs["Vector"])
    lines = smooth(nt, wave.outputs["Fac"], 0.80, 0.98)
    u = mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
    cx = mth(nt, "FRACT", mth(nt, "DIVIDE", u, 1.6))
    vx = smooth(nt, mth(nt, "ABSOLUTE", mth(nt, "SUBTRACT", cx, 0.5)), 0.44, 0.5)
    pat = mth(nt, "MAXIMUM", lines, mth(nt, "MULTIPLY", vx, 0.5))
    a = mth(nt, "MULTIPLY", mth(nt, "ADD", 0.10, mth(nt, "MULTIPLY", pat, 0.55)), mth(nt, "MINIMUM", pw.outputs["Fac"], 1.0))
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col.outputs["Color"], em.inputs["Color"])
    nt.links.new(mth(nt, "MULTIPLY", mth(nt, "ADD", 0.25, pat), mth(nt, "MULTIPLY", pw.outputs["Fac"], 3.0)),
                 em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a, mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def mat_ground():
    """Wet plaza tiles (k = 1) and asphalt (k = 0): mirror puddles from a low-frequency noise, ripples."""
    m, nt = new_mat("ground")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    kf = attr(nt, "k")
    g, ps, ns = pos_sep(nt)
    cxyz = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(ps.outputs["X"], cxyz.inputs[0])
    nt.links.new(ps.outputs["Y"], cxyz.inputs[1])
    br = nn(nt, "ShaderNodeTexBrick", Scale=1.0, Mortar_Size=0.04, Bias=0.0, Brick_Width=3.0, Row_Height=3.0)
    nt.links.new(cxyz.outputs[0], br.inputs["Vector"])
    tile = mth(nt, "ADD", mth(nt, "SUBTRACT", 1.0, kf.outputs["Fac"]),
               mth(nt, "MULTIPLY", kf.outputs["Fac"], mth(nt, "ADD", 0.55, mth(nt, "MULTIPLY", br.outputs["Fac"], 0.45))))
    pn = nn(nt, "ShaderNodeTexNoise", Scale=0.075, Detail=5.0, Roughness=0.55)
    nt.links.new(g.outputs["Position"], pn.inputs["Vector"])
    puddle = smooth(nt, pn.outputs["Fac"], 0.47, 0.55)
    alb = mth(nt, "MULTIPLY", tile, mth(nt, "SUBTRACT", 1.0, mth(nt, "MULTIPLY", puddle, 0.55)))
    nt.links.new(vsc(nt, col.outputs["Color"], alb), b.inputs["Base Color"])
    nt.links.new(mth(nt, "ADD", 0.02, mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, puddle), 0.24)), b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.6
    rp = nn(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=3.0, Roughness=0.5)
    nt.links.new(g.outputs["Position"], rp.inputs["Vector"])
    bump = nn(nt, "ShaderNodeBump", Strength=0.08, Distance=0.04)
    nt.links.new(mth(nt, "ADD", mth(nt, "MULTIPLY", rp.outputs["Fac"], mth(nt, "SUBTRACT", 1.0, puddle)),
                     mth(nt, "MULTIPLY", br.outputs["Fac"], mth(nt, "MULTIPLY", kf.outputs["Fac"], 0.6))),
                 bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def mat_city(name, win_k, p_lit):
    """The Cell's grimy towers: dark concrete + grime, a window grid with seeded lit cells (warm / cool / pink)."""
    m, nt = new_mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = attr(nt, "col")
    kf = attr(nt, "k")
    g, ps, ns = pos_sep(nt)
    u = mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
    su, sv = 2.1, 3.1
    cu = mth(nt, "FLOOR", mth(nt, "DIVIDE", u, su))
    cv = mth(nt, "FLOOR", mth(nt, "DIVIDE", ps.outputs["Z"], sv))
    fu = mth(nt, "FRACT", mth(nt, "DIVIDE", u, su))
    fv = mth(nt, "FRACT", mth(nt, "DIVIDE", ps.outputs["Z"], sv))
    wm = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", mth(nt, "GREATER_THAN", fu, 0.28), mth(nt, "LESS_THAN", fu, 0.72)),
             mth(nt, "MULTIPLY", mth(nt, "GREATER_THAN", fv, 0.32), mth(nt, "LESS_THAN", fv, 0.68)))
    vert = mth(nt, "LESS_THAN", mth(nt, "ABSOLUTE", ns.outputs["Z"]), 0.3)
    cid = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(cu, cid.inputs[0])
    nt.links.new(cv, cid.inputs[1])
    nt.links.new(mth(nt, "FLOOR", mth(nt, "DIVIDE", mth(nt, "SUBTRACT", ps.outputs["X"], ps.outputs["Y"]), 7.0)),
                 cid.inputs[2])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(cid.outputs[0], wn.inputs["Vector"])
    fid = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(cv, fid.inputs[0])
    nt.links.new(mth(nt, "FLOOR", mth(nt, "DIVIDE", u, 23.0)), fid.inputs[1])
    fid.inputs[2].default_value = 3.3
    fn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    fn.noise_dimensions = "3D"
    nt.links.new(fid.outputs[0], fn.inputs["Vector"])
    lit = mth(nt, "MULTIPLY", mth(nt, "LESS_THAN", fn.outputs["Value"], 0.5),
              mth(nt, "LESS_THAN", wn.outputs["Value"], mth(nt, "MULTIPLY", kf.outputs["Fac"], p_lit * 2.0)))
    on = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", wm, vert), mth(nt, "GREATER_THAN", kf.outputs["Fac"], 0.01))
    wsep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(wn.outputs["Color"], wsep.inputs[0])
    wcol = mixc(nt, mth(nt, "GREATER_THAN", wsep.outputs[0], 0.78), (1.0, 0.66, 0.40), (0.86, 0.92, 1.0))
    wcol = mixc(nt, mth(nt, "GREATER_THAN", wsep.outputs[0], 0.95), wcol, pal("district_a"))
    lgn = mth(nt, "EXPONENT", mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", wsep.outputs[2], 0.5), 1.7))
    pw = attr(nt, "pwo", "OBJECT")
    wint = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", lgn, win_k), mth(nt, "MULTIPLY", on, lit)),
               pw.outputs["Fac"])
    n1 = nn(nt, "ShaderNodeTexNoise", Scale=0.3, Detail=6.0, Roughness=0.65)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    gr = mth(nt, "ADD", 0.7, mth(nt, "MULTIPLY", n1.outputs["Fac"], 0.6))
    dark = mth(nt, "MULTIPLY", on, mth(nt, "SUBTRACT", 1.0, lit))
    nt.links.new(vsc(nt, col.outputs["Color"], mth(nt, "MULTIPLY", gr, mth(nt, "SUBTRACT", 1.0, mth(nt, "MULTIPLY", dark, 0.5)))),
                 b.inputs["Base Color"])
    nt.links.new(mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", 0.6, mth(nt, "MULTIPLY", dark, 0.5)), 0.05), b.inputs["Roughness"])
    nt.links.new(wcol, b.inputs["Emission Color"])
    nt.links.new(wint, b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


M_CIVIC = mat_civic()
M_CUT = mat_plain("cut", rough=0.5, spec=0.4)
M_INT = mat_plain("interior", rough=0.35, spec=0.5, coat=0.2)
M_METAL = mat_plain("metal", rough=0.32, spec=0.6, metal=0.7)
M_GLASS = mat_glass()
M_EMIT = mat_emit("emit")
M_LOCK = mat_lock()
M_GROUND = mat_ground()
M_CITY = mat_city("city", HZ["city"]["win_k"], HZ["city"]["win_p"])
M_CEMIT = mat_emit("city_emit")
M_CMETAL = mat_plain("city_metal", rough=0.32, spec=0.6, metal=0.7)
from hq_kit import section as KSEC  # noqa: E402
from hq_kit import downtown as KDT  # noqa: E402
for m_ in (M_CITY, M_CEMIT, M_CMETAL):
    KSEC.insert(m_)
KSEC.set_frame(scene, None)
DTC = HZ.get("downtown")

COLL = {k: bpy.data.collections.new(k) for k in ("compound", "rooms", "city", "ground", "streaks", "eye", "media",
                                                  "lights")}
for c_ in COLL.values():
    scene.collection.children.link(c_)
A = {
    "civic": Acc("civic", M_CIVIC, 1, COLL["compound"]),
    "cut": Acc("cut", M_CUT, 1, COLL["compound"]),
    "metal": Acc("metal", M_METAL, 1, COLL["compound"]),
    "glass": Acc("glass", M_GLASS, 1, COLL["compound"]),
    "trim": Acc("trim", M_EMIT, 1, COLL["compound"]),          # big layer: cornice coves, reveals, office slits
    "gold": Acc("gold", M_EMIT, 1, COLL["compound"]),
    "sign": Acc("sign", M_EMIT, 1, COLL["compound"]),          # LOD signage: the plinth lettering + crest
    "small": Acc("small", M_EMIT, 1, COLL["compound"]),        # LOD small lights: bollards, stair LEDs, deck strips
    "int": Acc("int", M_INT, 5, COLL["rooms"]),
    "ground": Acc("ground", M_GROUND, 4, COLL["ground"]),
    "city": Acc("city", M_CITY, 2, COLL["city"]),
    "city_neon": Acc("city_neon", M_CEMIT, 2, COLL["city"]),    # big layer: crown trims
    "city_sign": Acc("city_sign", M_CEMIT, 2, COLL["city"]),    # LOD signage: blade signs, shop fronts, billboards
    "city_small": Acc("city_small", M_CEMIT, 2, COLL["city"]),  # LOD small lights: beacons
    "city_metal": Acc("city_metal", M_CMETAL, 2, COLL["city"]),
    "streaks": Acc("streaks", M_CEMIT, 7, COLL["streaks"]),
    "sky": Acc("sky", M_EMIT, 2, COLL["city"]),
    "eye": Acc("eye", M_METAL, 6, COLL["eye"]),
    "eye_rim": Acc("eye_rim", M_EMIT, 6, COLL["eye"]),
    "eye_iris": Acc("eye_iris", M_EMIT, 6, COLL["eye"]),
}
ROOM_EMIT, ROOM_LOCK = {}, {}

WHITE = pal("panel")
CUTC = pal("panel_dark")
TEAL = pal("civic_teal")
CWHITE = pal("civic_white")
GOLD = pal("gold")
VIOLET = pal("corp_violet")
AMBER = pal("corp_amber")
LOCK = pal("lockdown")
SCAN = pal("scan")
TYPE_COL = {"router": (0.30, 0.85, 1.0), "elite": (1.0, 0.36, 0.10), "terminal": (0.20, 1.0, 0.50),
            "modem": (0.30, 0.50, 1.0), "rack": (1.0, 0.70, 0.20), "target": (1.0, 0.22, 0.12), "start": (0.83, 1.0, 0.0)}
from hq_kit import states as KST  # noqa: E402
from hq_kit import lod as KLOD  # noqa: E402
STATE_K = KST.STATE_K
NODES = LY["nodes"]
TIERS = LY["tiers"]
R = len(CP["rows"])
LH = HZ["light"]
RW, RH, RD = C["RW"], C["RH"], C["RD"]

# ================================================================== the compound: square tiers, rooms on the route face
for t in TIERS:
    r = t["r"]
    hs, z0, z1 = t["hs"], t["z0"], t["z1"]
    core = hs - RD
    box(A["civic"], -core, -core, z0, core, core, z1, WHITE)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(A["civic"], sx * core, sy * core, z0, sx * hs, sy * hs, z1, WHITE)
    route_f = r % 4 if r < R else -1
    zr0 = z0 + C["SLAB"]
    zr1 = zr0 + (CP["target_h"] if r == R else RH)
    for f in range(4):
        if r == R:                                   # the vault: open on all four faces (piers at the corners only)
            fbox(A["civic"], f, core, hs, -core, core, z0, zr0, WHITE)
            fbox(A["civic"], f, core, hs, -core, core, zr1, z1, WHITE)
            continue
        if f != route_f:
            fbox(A["civic"], f, core, hs, -core, core, z0, z1, WHITE)
            # office slits between the fins (big layer: building lights)
            n_sl = int(2 * core / 2.4)
            rr_ = random.Random(1000 * r + f)
            for s in range(n_sl):
                u = -core + 1.2 + s * 2.4
                if rr_.random() < 0.55:
                    fquad(A["trim"], f, hs + 0.02, u - 0.35, zr0 + 1.2, u + 0.35, zr1 - 1.0, (0.75, 0.88, 1.0),
                          (0.35 + 0.5 * rr_.random()) * LH["slit_k"])
        else:
            rooms = sorted((i for i, n in NODES.items() if n["tier"] == r and n["face"] == f and i != "srv"),
                           key=lambda i: NODES[i]["u"])
            fbox(A["civic"], f, core, hs, -core, core, z0, zr0, WHITE)
            fbox(A["civic"], f, core, hs, -core, core, zr1, z1, WHITE)
            cuts = [-core] + [v for i in rooms for v in (NODES[i]["u"] - RW / 2, NODES[i]["u"] + RW / 2)] + [core]
            for a_, b_ in zip(cuts[0::2], cuts[1::2]):
                if b_ - a_ > 0.05:
                    fbox(A["civic"], f, core, hs, a_, b_, zr0, zr1, WHITE, top=False)
        # the colonnade fins (every face), cornice ring, teal cove, glass parapet
        nfin = int(2 * hs / 1.6)
        for s in range(nfin + 1):
            u = -hs + 0.4 + (2 * hs - 0.8) * s / nfin
            if f == route_f and any(abs(u - NODES[i]["u"]) < RW / 2 + 0.3 for i in NODES
                                    if NODES[i]["tier"] == r and NODES[i]["face"] == f and i != "srv"):
                continue
            fbox(A["civic"], f, hs, hs + 0.55, u - 0.16, u + 0.16, zr0 + 0.2, zr1 - 0.2, WHITE)
        fbox(A["civic"], f, hs - 2.5, hs + 1.3, -hs - 1.3, hs + 1.3, z1 - 1.1, z1, WHITE)
        fquad(A["trim"], f, hs + 1.25, -hs - 1.1, z1 - 1.2, hs + 1.1, z1 - 1.12, TEAL, LH["teal_k"])
        fquad(A["trim"], f, hs + 1.32, -hs - 1.1, z1 - 0.62, hs + 1.1, z1 - 0.5, CWHITE, LH["cove_k"] * 0.6)
        fbox(A["glass"], f, hs + 1.05, hs + 1.2, -hs - 1.2, hs + 1.2, z1, z1 + 1.1, (0.05, 0.08, 0.09))
        fbox(A["small"], f, hs + 1.0, hs + 1.22, -hs - 1.2, hs + 1.2, z1 + 1.05, z1 + 1.15, TEAL, LH["teal_k"] * 0.5)
    for sx in (-1, 1):                                # teal corner reveals
        for sy in (-1, 1):
            box(A["trim"], sx * hs - 0.12, sy * hs - 0.12, z0 + 0.6, sx * hs + 0.12, sy * hs + 0.12, z1 - 1.3, TEAL,
                LH["teal_k"] * 0.6)
log("tiers built")

# the podium (square plinth), processional stairs on four sides, the name and the crest (signage LOD)
PX = CP["podium_x"]
PH = C["PODIUM"]
box(A["civic"], -PX, -PX, 0.0, PX, PX, PH, WHITE)
box(A["ground"], -PX, -PX, PH, PX, PX, PH + 0.02, (0.42, 0.44, 0.47), k=1.0)
for f in range(4):
    fquad(A["trim"], f, PX + 0.08, -PX, PH - 0.4, PX, PH - 0.25, TEAL, LH["teal_k"] * 0.7)
    fquad(A["trim"], f, PX + 0.08, -PX, 0.25, PX, 0.4, CWHITE, LH["cove_k"] * 0.5)
    for s in range(8):
        fbox(A["civic"], f, PX, PX + (8 - s) * 1.1, -18, 18, 0, PH * (s + 1) / 8, WHITE)
STENCIL = {
    "H": ["1001", "1001", "1111", "1001", "1001"], "A": ["0110", "1001", "1111", "1001", "1001"],
    "L": ["1000", "1000", "1000", "1000", "1111"], "C": ["0111", "1000", "1000", "1000", "0111"],
    "Y": ["1001", "1001", "0110", "0100", "0100"], "O": ["0110", "1001", "1001", "1001", "0110"],
    "N": ["1001", "1101", "1011", "1001", "1001"], "I": ["111", "010", "010", "010", "111"],
    "V": ["1001", "1001", "1001", "0110", "0110"], " ": ["00", "00", "00", "00", "00"],
}


def stencil(acc, f, d, word, u0, z0, cell, col, k):
    u = u0
    for ch in word:
        g = STENCIL[ch]
        for row, bits in enumerate(g):
            for cix, bit in enumerate(bits):
                if bit == "1":
                    fquad(acc, f, d, u + cix * cell, z0 + (4 - row) * cell, u + (cix + 1) * cell - cell * 0.18,
                          z0 + (5 - row) * cell - cell * 0.18, col, k)
        u += (len(g[0]) + 1) * cell


for f in range(4):
    stencil(A["sign"], f, PX + 0.15, "HALCYON CIVIC", 30.0, 1.6, 0.42, VIOLET, 5.0 * LH["sign_k"])
    for i in range(24):
        a0, a1 = math.pi * i / 24, math.pi * (i + 1) / 24
        for sgn in (1, -1):
            tube(A["sign"], fp(f, PX + 0.15, 30.0 + 22 - 26 + 4.2 * math.cos(a0) - 8, 3.0 + sgn * 1.9 * math.sin(a0)),
                 fp(f, PX + 0.15, 30.0 + 22 - 26 + 4.2 * math.cos(a1) - 8, 3.0 + sgn * 1.9 * math.sin(a1)), 0.16, VIOLET,
                 5.0 * LH["sign_k"], n=6)
    fdisc(A["sign"], f, PX + 0.16, 18.0 - 8 + 0.0, 3.0, 0.95, VIOLET, 5.0 * LH["sign_k"], n=20)


# ------------------------------------------------------------------ rooms (cutaway interiors), in face frames
def room_shell(i, n):
    f = n["face"]
    r = n["tier"]
    hs = TIERS[r]["hs"]
    z0, z1 = n["z"]
    u = n["u"]
    w = CP["target_w"] if i == "srv" else RW
    u0, u1 = u - w / 2, u + w / 2
    kind = n["kind"]
    acc = A["int"]
    em = ROOM_EMIT.setdefault(i, Acc("room_" + i, M_EMIT, 5, COLL["rooms"]))
    inner = (0.50, 0.53, 0.56)

    def rb(a0, a1, din0, din1, zz0, zz1, col, k=0.0, ac=None):
        fbox(ac or acc, f, hs - din1, hs - din0, a0, a1, zz0, zz1, col, k)

    rb(u0, u1, 0, RD, z0 - 0.4, z0, (0.34, 0.35, 0.38))
    fquad(acc, f, hs - RD, u0, z0, u1, z1, inner)
    rb(u0 - 0.3, u0, 0, RD, z0, z1, tuple(v * 0.9 for v in inner))
    rb(u1, u1 + 0.3, 0, RD, z0, z1, tuple(v * 0.9 for v in inner))
    rb(u0, u1, 0, RD, z1, z1 + 0.3, tuple(v * 0.8 for v in inner))
    for (a0, a1, b0, b1) in ((u0 - 0.45, u0, z0 - 0.5, z1 + 0.5), (u1, u1 + 0.45, z0 - 0.5, z1 + 0.5),
                             (u0, u1, z1, z1 + 0.5), (u0, u1, z0 - 0.5, z0 - 0.4)):
        fquad(A["cut"], f, hs + 0.02, a0, b0, a1, b1, CUTC)
    tc = TYPE_COL[kind]
    for frac in (0.3, 0.7):
        rb(u0 + 0.8, u1 - 0.8, RD * frac - 0.18, RD * frac + 0.18, z1 - 0.12, z1 - 0.02, CWHITE, 4.0, em)
    rr = random.Random(sum(map(ord, i)) * 7 + 17)
    bk = RD                                   # depth of the back wall
    if kind == "router":
        rb(u0 + w * 0.2, u0 + w * 0.65, 3.6, 5.0, z0, z0 + 1.1, (0.7, 0.72, 0.75))
        for m_ in range(4):
            a = u0 + 1.5 + m_ * (w - 3) / 4
            rb(a, a + (w - 3) / 4 - 0.4, bk - 0.12, bk - 0.02, z0 + 3.2, z0 + 5.4, tc, 3.2, em)
        rb(u1 - 3.4, u1 - 3.0, 6.0, 8.0, z0, z0 + 1.2, (0.4, 0.4, 0.45), ac=A["metal"])
    elif kind == "elite":
        for m_ in range(3):
            a = u0 + 1.4 + m_ * (w - 2.8) / 3
            rb(a, a + (w - 2.8) / 3 - 0.6, bk - 1.2, bk - 0.2, z0, z0 + 6.0, (0.18, 0.18, 0.2), ac=A["metal"])
            rb(a + 0.2, a + 0.45, bk - 1.25, bk - 1.2, z0 + 0.6, z0 + 5.5, tc, 4.0, em)
        rb(u0 + w * 0.3, u0 + w * 0.7, 5.5, 7.0, z0, z0 + 0.9, (0.3, 0.3, 0.32))
    elif kind == "terminal":
        rb(u0 + 1.4, u1 - 1.4, bk - 0.1, bk - 0.02, z0 + 1.6, z0 + 6.6, tc, 2.6, em)
        rb(u0 + w * 0.35, u0 + w * 0.65, 3.0, 4.5, z0, z0 + 1.0, (0.62, 0.64, 0.66))
    elif kind == "modem":
        for m_ in range(4):
            a = u0 + 1.2 + m_ * (w - 2.4) / 4
            rb(a, a + (w - 2.4) / 4 - 0.5, bk - 1.4, bk - 0.1, z0, z0 + 5.2, (0.3, 0.32, 0.36), ac=A["metal"])
            for sh in range(3):
                rb(a + 0.1, a + (w - 2.4) / 4 - 0.6, bk - 1.45, bk - 1.4, z0 + 1.0 + sh * 1.6, z0 + 1.3 + sh * 1.6, tc, 3.0, em)
    return em


for i, n in sorted(NODES.items(), key=lambda kv: (kv[1]["tier"], kv[1]["k"])):
    if i not in ("start", "srv"):
        room_shell(i, n)
# THE PANOPTICON: the open apex vault, the server core in its centre (a column of red iris rings), racks
tv = TIERS[-1]
vz0 = tv["z0"] + C["SLAB"]
vz1 = vz0 + CP["target_h"]
emv = ROOM_EMIT.setdefault("srv", Acc("room_srv", M_EMIT, 5, COLL["rooms"]))
box(A["int"], -tv["hs"] + 0.3, -tv["hs"] + 0.3, vz0 - 0.4, tv["hs"] - 0.3, tv["hs"] - 0.3, vz0, (0.16, 0.15, 0.2))
box(A["int"], -tv["hs"] + 0.3, -tv["hs"] + 0.3, vz1, tv["hs"] - 0.3, tv["hs"] - 0.3, vz1 + 0.3, (0.12, 0.12, 0.15))
tube(A["metal"], (0, 0, vz0), (0, 0, vz1), 3.2, (0.08, 0.08, 0.1), n=16)
for k_ in range(7):
    zz = vz0 + 1.0 + k_ * 1.25
    tube(emv, (0, 0, zz), (0, 0, zz + 0.25), 3.3, (1.0, 0.22, 0.08), 6.0, n=24)
rr_ = random.Random(77)
for f in range(4):
    for s in (-1, 1):
        a = s * 7.5
        fbox(A["metal"], f, 2.0, 6.0, a - 0.8, a + 0.8, vz0, vz0 + 7.5, (0.1, 0.1, 0.12))
        for led in range(9):
            lz = vz0 + 0.8 + led * 0.72
            fquad(emv, f, 6.02, a - 0.6, lz, a - 0.6 + 0.35 + rr_.random() * 0.8, lz + 0.12,
                  (1.0, 0.18 + 0.4 * rr_.random(), 0.05), 5.0)
log("rooms built")

# the crown and the lighthouse turret (the eye sits on a turntable; built locally, rotated per frame)
ct = LY["crown_top"]
box(A["civic"], -tv["hs"] + 3, -tv["hs"] + 3, tv["z1"], tv["hs"] - 3, tv["hs"] - 3, ct, WHITE)
for f in range(4):
    fquad(A["trim"], f, tv["hs"] - 2.95, -tv["hs"] + 3, ct - 0.5, tv["hs"] - 3, ct - 0.3, TEAL, LH["teal_k"])
EX, EY, EZ = LY["eye"]
EYE = CP["eye"]
tube(A["civic"], (0, 0, ct), (0, 0, EZ - EYE["drum_r"] * 0.6), 2.4, WHITE, n=12)
ring_z = EZ - EYE["drum_r"] - 1.0
tube(A["metal"], (0, 0, ring_z), (0, 0, ring_z + 0.8), 7.0, (0.5, 0.52, 0.55), n=24)
tube(A["small"], (0, 0, ring_z + 0.8), (0, 0, ring_z + 0.95), 7.05, TEAL, 6.0, n=24)
EYE_ACC = {"eye": Acc("eye_body", M_METAL, 6, COLL["eye"]), "rim": Acc("eye_rim", M_EMIT, 6, COLL["eye"]),
           "iris": Acc("eye_iris", M_EMIT, 6, COLL["eye"])}
ew, eh, dr, dd = EYE["w"], EYE["h"], EYE["drum_r"], EYE["drum_d"]
# local frame: the eye looks along +y; the drum's axis is y
tube(EYE_ACC["eye"], (0, -dd * 0.5, 0), (0, dd * 0.5, 0), dr, (0.55, 0.57, 0.6), n=32)
EYE_ACC["eye"].face([(dr * math.cos(2 * math.pi * k / 32), -dd * 0.5, dr * math.sin(2 * math.pi * k / 32))
                     for k in range(32)], (0.5, 0.52, 0.55))
fy = dd * 0.5 + 0.05
EYE_ACC["eye"].face([(dr * 0.98 * math.cos(2 * math.pi * k / 32), fy, dr * 0.98 * math.sin(2 * math.pi * k / 32))
                     for k in reversed(range(32))], (0.02, 0.02, 0.025))


def alm(t, sgn, sx=1.0, sz=1.0):
    a = math.pi * t
    return (-ew / 2 * sx * math.cos(a), fy + 0.4, sgn * eh / 2 * sz * math.sin(a))


for sgn in (1, -1):
    pts = [alm(k / 40, sgn) for k in range(41)]
    for p0, p1 in zip(pts, pts[1:]):
        tube(EYE_ACC["rim"], p0, p1, EYE["tube"], AMBER, HZ["eye"]["rim_k"], n=8)
for j in (-2, -1, 0, 1, 2):
    a = math.radians(90 + j * 24)
    x0_, z0_ = (ew / 2 + 1.5) * 0.62 * math.cos(a), (eh / 2 + 1.6) * math.sin(a)
    tube(EYE_ACC["rim"], (x0_, fy + 0.4, z0_), (x0_ + 4.5 * math.cos(a), fy + 0.4, z0_ + 4.5 * math.sin(a)), 0.7, AMBER,
         HZ["eye"]["rim_k"], n=6)
EYE_ACC["iris"].face([(EYE["iris_r"] * math.cos(2 * math.pi * k / 48), fy + 0.6, EYE["iris_r"] * math.sin(2 * math.pi * k / 48))
                      for k in reversed(range(48))], SCAN, HZ["eye"]["iris_k"])
EYE_ACC["eye"].face([(EYE["iris_r"] * 0.42 * math.cos(2 * math.pi * k / 32), fy + 0.7, EYE["iris_r"] * 0.42 * math.sin(2 * math.pi * k / 32))
                     for k in reversed(range(32))], (0.01, 0.01, 0.012))
for k in range(48):
    a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 0.6) / 48
    r0, r1 = EYE["iris_r"] * 1.06, EYE["iris_r"] * 1.3
    EYE_ACC["eye"].face([(r0 * math.cos(a0), fy + 0.55, r0 * math.sin(a0)), (r1 * math.cos(a0), fy + 0.55, r1 * math.sin(a0)),
                         (r1 * math.cos(a1), fy + 0.55, r1 * math.sin(a1)), (r0 * math.cos(a1), fy + 0.55, r0 * math.sin(a1))],
                        (0.3, 0.32, 0.34))
log("eye built")

# ------------------------------------------------------------------ links: galleries, corner stairs, the ramp, the gatehouse
for e in LY["all_edges"]:
    pts = [Vector(p) for p in e["path"]]
    t = e["type"]
    a_id = e["a"]
    if t == "gallery":
        f = NODES[a_id]["face"]
        hs = TIERS[NODES[a_id]["tier"]]["hs"]
        ua = NODES[a_id]["u"] + RW / 2
        ub = NODES[e["b"]]["u"] - RW / 2
        zz = NODES[a_id]["z"][0]
        fbox(A["glass"], f, hs + 0.15, hs + 2.6, ua, ub, zz, zz + 3.4, (0.03, 0.05, 0.06))
        fbox(A["metal"], f, hs + 0.1, hs + 2.7, ua, ub, zz - 0.25, zz, (0.6, 0.62, 0.66))
        fquad(A["small"], f, hs + 2.72, ua, zz - 0.05, ub, zz + 0.05, TEAL, 4.0)
        for s in range(int((ub - ua) / 1.8) + 1):
            mu = ua + s * (ub - ua) / max(1, int((ub - ua) / 1.8))
            fbox(A["metal"], f, hs + 2.58, hs + 2.68, mu - 0.06, mu + 0.06, zz, zz + 3.4, (0.7, 0.72, 0.75))
    elif t == "corner_stair":
        fa = NODES[a_id]["face"]
        fb = NODES[e["b"]]["face"]
        ra = NODES[a_id]["tier"]
        hs = TIERS[ra]["hs"]
        za = NODES[a_id]["z"][0]
        zb = NODES[e["b"]]["z"][0]
        ua = NODES[a_id]["u"] + RW / 2
        # the deck to the corner (face a), round it, then the flight along face b of the same tier
        fbox(A["metal"], fa, hs + 0.1, hs + 2.7, ua, hs + 2.7, za - 0.25, za, (0.6, 0.62, 0.66))
        fquad(A["small"], fa, hs + 2.72, ua, za - 0.05, hs + 2.7, za + 0.05, TEAL, 4.0)
        run = CP["stair_run"]
        n = max(6, int((zb - za) / 0.7))
        for s in range(n):
            u0 = -hs - 2.7 + (run + 2.7) * s / n
            u1 = -hs - 2.7 + (run + 2.7) * (s + 1) / n
            fbox(A["civic"], fb, hs + 0.1, hs + 2.7, u0, u1, za - 0.25, za + (zb - za) * (s + 1) / n, WHITE)
        tube(A["metal"], fp(fb, hs + 2.6, -hs - 2.7, za + 1.0), fp(fb, hs + 2.6, -hs + run, zb + 1.0), 0.14,
             (0.7, 0.72, 0.75), n=6)
        tube(A["small"], fp(fb, hs + 2.62, -hs - 2.7, za + 1.15), fp(fb, hs + 2.62, -hs + run, zb + 1.15), 0.06, TEAL,
             6.0, n=6)
    elif t == "climb":
        # the exterior climb: a gold maintenance rail (twin rails + rungs) up each facade, a catwalk across each
        # terrace, and a window-washer gantry parked halfway (all on the outside of the face)
        fa_ = NODES[a_id]["face"]
        tng = Vector((TF[fa_][0], TF[fa_][1], 0.0))
        nrm = Vector((NF[fa_][0], NF[fa_][1], 0.0))
        for p, q in zip(pts[1:-1], pts[2:-1]):
            vert = abs(q.z - p.z) > 0.5
            if vert:
                for s_ in (-0.7, 0.7):
                    tube(A["metal"], p + tng * s_, q + tng * s_, 0.12, (0.62, 0.55, 0.38), n=6)
                nr = int(abs(q.z - p.z) / 0.8)
                for k_ in range(nr + 1):
                    c_ = p.lerp(q, k_ / max(1, nr))
                    tube(A["metal"], c_ - tng * 0.7, c_ + tng * 0.7, 0.06, (0.62, 0.55, 0.38), n=4)
                for s_ in (-0.82, 0.82):
                    tube(A["gold"], p + tng * s_, q + tng * s_, 0.05, GOLD, 4.0, n=4)
            else:
                box(A["metal"], min(p.x, q.x) - 0.9, min(p.y, q.y) - 0.9, p.z - 0.25, max(p.x, q.x) + 0.9,
                    max(p.y, q.y) + 0.9, p.z, (0.5, 0.48, 0.42))
        mids = [(p, q) for p, q in zip(pts[1:-1], pts[2:-1]) if abs(q.z - p.z) > 0.5]
        if mids:
            p, q = mids[len(mids) // 2]
            c_ = p.lerp(q, 0.55)
            g0 = c_ - tng * 1.6 + nrm * 0.3
            g1 = c_ + tng * 1.6 + nrm * 2.0
            box(A["metal"], min(g0.x, g1.x), min(g0.y, g1.y), c_.z - 1.2, max(g0.x, g1.x), max(g0.y, g1.y), c_.z - 1.0,
                (0.55, 0.5, 0.4))
            box(A["gold"], min(g0.x, g1.x), min(g0.y, g1.y), c_.z + 1.1, max(g0.x, g1.x), max(g0.y, g1.y), c_.z + 1.2,
                GOLD, 5.0)
            tube(A["small"], c_ + nrm * 1.2 + Vector((0, 0, 1.4)), c_ + nrm * 1.2 + Vector((0, 0, 1.7)), 0.25,
                 (1.0, 0.6, 0.1), 8.0, n=6)
    elif t == "ramp":
        sx_, sy_, _ = LY["start"]
        for s in range(9):
            x0_ = sx_ + 10.0 + 12.0 * s / 9
            box(A["civic"], x0_, -PX - 4.5, 0, x0_ + 12.0 / 9, -PX, PH * (s + 1) / 9, WHITE)
sx_, sy_, _ = LY["start"]
box(A["civic"], sx_ - 4, sy_ - 3, 0, sx_ + 4, sy_ + 3, 4.4, WHITE)
box(A["civic"], sx_ - 4.6, sy_ - 3.6, 4.4, sx_ + 4.6, sy_ + 3.6, 5.0, WHITE)
box(A["glass"], sx_ - 3.2, sy_ - 3.05, 1.4, sx_ + 3.2, sy_ - 3.0, 3.8, (0.05, 0.07, 0.08))
box(A["trim"], sx_ - 4.6, sy_ - 3.65, 4.95, sx_ + 4.6, sy_ - 3.6, 5.05, TEAL, 4.0)
box(A["metal"], sx_ + 4.2, sy_ - 0.5, 0, sx_ + 4.8, sy_ + 0.5, 1.4, (0.5, 0.5, 0.52))
box(A["small"], sx_ + 4.8, sy_ - 0.2, 1.1, sx_ + 13.0, sy_ + 0.2, 1.35, (1.0, 0.1, 0.1), 3.0)
box(A["trim"], sx_ - 4.4, sy_ - 3.2, 1.4, sx_ - 3.4, sy_ - 2.8, 2.8, (0.55, 1.0, 0.0), 6.0)
log("links built")

# ------------------------------------------------------------------ plaza, ring road, walk (a square ring all round)
RDP = HZ["road"]
PL = RDP["plaza"]
R0, R1 = RDP["road"]
W0, W1 = RDP["walk"]
if DTC:
    PL = DTC["keep"][1] + 2.0                                 # HQ_REV_V2: the plaza is only the gate apron now
box(A["ground"], -PL, -PL, -0.02, PL, PL, 0.0, (0.40, 0.42, 0.45), k=1.0)
for f in (range(4) if not DTC else ()):
    fbox(A["ground"], f, R0, R1, -R1, R1, -0.02, 0.0, (0.055, 0.055, 0.06), k=0.0)
    fbox(A["ground"], f, W0, W1, -W1, W1, 0.0, 0.25, (0.30, 0.30, 0.32), k=1.0)
    md = (R0 + R1) / 2
    u = -R1
    while u < R1:
        fbox(A["ground"], f, md - 0.12, md + 0.12, u, u + 4.5, 0.0, 0.012, (0.55, 0.52, 0.42), k=0.0)
        u += 9.0
    u = -PL + 6
    while u < PL - 4:
        if abs(u) > 20:
            fbox(A["civic"], f, PL - 4.2, PL - 3.3, u - 0.45, u + 0.45, 0, 1.6, WHITE)
            fbox(A["small"], f, PL - 4.22, PL - 3.28, u - 0.47, u + 0.47, 1.25, 1.4, TEAL, 6.0)
        u += 12.0
box(A["ground"], -1600, -1600, -0.05, 1600, 1600, -0.02, (0.06, 0.06, 0.07), k=0.0)
# the perimeter belt: wet dark ground, a grid of low teal light pylons, a low wall with red warning lights
PER = HZ["city"]["perimeter"]
for f in (range(4) if not DTC else ()):
    fbox(A["ground"], f, W1, PER["r"][1], -PER["r"][1], PER["r"][1], -0.02, 0.0, (0.16, 0.17, 0.19), k=1.0)
    fbox(A["civic"], f, PER["wall_r"], PER["wall_r"] + 2.0, -PER["wall_r"] - 2.0, PER["wall_r"] + 2.0, 0.0, PER["wall_h"], WHITE)
    fquad(A["trim"], f, PER["wall_r"] - 0.02, -PER["wall_r"], PER["wall_h"] - 0.5, PER["wall_r"], PER["wall_h"] - 0.35, TEAL,
          LH["teal_k"] * 0.6)
    u = -PER["wall_r"] + 8.0
    while u < PER["wall_r"] - 4:
        fbox(A["small"], f, PER["wall_r"] - 0.1, PER["wall_r"] + 0.3, u - 0.3, u + 0.3, PER["wall_h"], PER["wall_h"] + 0.5,
             (1.0, 0.06, 0.04), 8.0)
        u += 24.0
pr_ = random.Random(4312)
step = PER["pylon_step"]
n_ = int(PER["r"][1] / step)
for gx in (range(-n_, n_ + 1) if not DTC else ()):
    for gy in range(-n_, n_ + 1):
        x, y = gx * step, gy * step
        m = max(abs(x), abs(y))
        if m < PER["r"][0] + 8 or m > PER["r"][1] - 8:
            continue
        box(A["civic"], x - 0.5, y - 0.5, 0, x + 0.5, y + 0.5, PER["pylon_h"], WHITE)
        box(A["trim"], x - 0.55, y - 0.55, PER["pylon_h"] - 1.2, x + 0.55, y + 0.55, PER["pylon_h"] - 0.9, TEAL, 5.0)
        box(A["small"], x - 0.2, y - 0.2, PER["pylon_h"], x + 0.2, y + 0.2, PER["pylon_h"] + 0.3, CWHITE, 6.0)

# ------------------------------------------------------------------ the Cell's city: the 360 degree ring (hq_kit)
from types import SimpleNamespace  # noqa: E402
from hq_kit import city_ring as CRING  # noqa: E402
CITY = HZ["city"]
CITY_ACCS = ("city", "city_neon", "city_sign", "city_small", "city_metal")


BLD = []          # v3: every cuttable city building (x, y, top, hx, hy): the occlusion rule's python twin counts them
BC_MARK = {}


def set_bc(cx, cy, on=True, top=None, hx=4.0, hy=4.0):
    t = (float(top) if top is not None else 400.0) if on else 0.0
    for k_ in CITY_ACCS:
        A[k_].cur_bc = (float(cx), float(cy), t, float(hx), float(hy))
        BC_MARK[k_] = len(A[k_].b)
    if on:
        BLD.append([float(cx), float(cy), t, float(hx), float(hy)])


def bc_top(top):
    """The building's final top (once its crown is known): rewrites its faces since the last set_bc."""
    for k_ in CITY_ACCS:
        acc = A[k_]
        acc.cur_bc = acc.cur_bc[:2] + (float(top),) + acc.cur_bc[3:]
        for j in range(BC_MARK.get(k_, len(acc.b)), len(acc.b)):
            acc.b[j] = acc.cur_bc
    if BLD:
        BLD[-1][2] = float(top)


ROOF = CRING.build(CITY, HZ["road"], P, A, SimpleNamespace(box=box, fbox=fbox, fp=fp, tube=tube, bc=set_bc, bc_top=bc_top), pal)
set_bc(0, 0, False)
DT = None
if DTC:
    DT = KDT.build(DTC, A, SimpleNamespace(box=box, tube=tube, bc=set_bc), pal)
    ROOF += DT["roofs"]
    log("downtown towers", DT["n_towers"], "lamps", len(DT["lamps"]))
log("city built, roofs", len(ROOF))

# ------------------------------------------------------------------ build the objects
OBJ = {}
for k_, acc in A.items():
    OBJ[k_] = acc.build()
for k_, acc in EYE_ACC.items():
    OBJ["eye_" + k_] = acc.build()
for i, acc in ROOM_EMIT.items():
    OBJ["room_" + i] = acc.build()
EYE_OBJS = [OBJ["eye_eye"], OBJ["eye_rim"], OBJ["eye_iris"]]
for ob in EYE_OBJS:
    ob.location = (EX, EY, EZ)
log("objects", len([o for o in OBJ.values() if o]))

# ================================================================== lights
LIGHTS = []


def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, spot=None, blend=0.3, group="",
              shadow=True, receivers=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = tuple(col)[:3]
    try:
        ld.use_shadow = shadow
    except AttributeError:
        pass
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size_y or size
    elif kind in ("SPOT", "POINT"):
        ld.shadow_soft_size = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
    ob = bpy.data.objects.new(name, ld)
    COLL["lights"].objects.link(ob)
    ob.location = loc
    if aim is not None:
        ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    try:
        ob.visible_camera = False
    except AttributeError:
        pass
    if receivers is not None:
        ob.light_linking.receiver_collection = receivers
    LIGHTS.append((ob, energy, group))
    return ob


# uplights: every face of every tier, between rooms / at a pitch, cold white (the big layer: building light)
for t in TIERS[:-1]:
    for f in range(4):
        hs = t["hs"]
        rooms = sorted((n for i, n in NODES.items() if n["tier"] == t["r"] and n["face"] == f and i != "srv"),
                       key=lambda n: n["u"])
        if rooms:
            us = [-hs + 2.0] + [(a["u"] + b["u"]) / 2 for a, b in zip(rooms, rooms[1:])] + [hs - 2.0]
        else:
            us = [-hs + 2.0 + s * (2 * hs - 4.0) / max(1, int(hs / 12)) for s in range(int(hs / 12) + 1)]
        for u in us:
            add_light("up_%d_%d_%.0f" % (t["r"], f, u), "SPOT", fp(f, hs + 2.4, u, t["z0"] + 0.4), LH["uplight_w"], CWHITE,
                      aim=fp(f, hs - 1.0, u, t["z1"] + 2.0), size=0.6, spot=LH["uplight_cone"], blend=0.6, group="civic")
for f in range(4):
    for u in (-60, -20, 20, 60):
        add_light("plinth_%d_%d" % (f, u), "SPOT", fp(f, PX + 16, u, 0.5), LH["plinth_wash"], CWHITE,
                  aim=fp(f, PX, u, PH * 0.8), size=0.8, spot=60, blend=0.7, group="civic")
ROOM_LIGHTS = {}
for i, n in NODES.items():
    if i in ("start", "srv"):
        continue
    f = n["face"]
    hs = TIERS[n["tier"]]["hs"]
    z0, z1 = n["z"]
    ROOM_LIGHTS[i] = add_light("room_%s" % i, "AREA", fp(f, hs - RD * 0.45, n["u"], z1 - 0.3), LH["room_w"], (1, 1, 1),
                               aim=fp(f, hs - RD * 0.45, n["u"], z0), size=RW - 1.0, size_y=RD - 1.5, group="room:" + i)
ROOM_LIGHTS["srv"] = add_light("room_srv", "POINT", (0, 0, vz0 + 6.0), 6000.0, (1.0, 0.3, 0.15), size=2.0,
                               group="room:srv")
add_light("gate", "POINT", (sx_, sy_ - 5, 4.0), 900.0, CWHITE, size=1.0, group="civic")
add_light("hack", "POINT", (sx_ - 4.6, sy_ - 3.6, 2.0), 120.0, (0.55, 1.0, 0.0), size=0.3, group="start")
# HQ_REV_V2: the downtown's street lamps nearest the compound light their pools on the wet street (real spots)
if DT:
    lamps = sorted(DT["lamps"], key=lambda l_: (KDT._keep_dist(DTC, l_[0], l_[1]), l_[0], l_[1]))
    for k_, (lx_, ly_, lz_, lc_) in enumerate(lamps[:DTC.get("lamp_lights", 60)]):
        add_light("lamp_%d" % k_, "SPOT", (lx_, ly_, lz_), DTC.get("lamp_w", 1500.0), lc_, aim=(lx_, ly_, 0.0), size=0.4,
                  spot=100, blend=0.9, group="city", shadow=False)
# near-ring shop spill (street level, by azimuth: 12 sectors)
for k_ in range(0 if DT else 12):
    az = 2 * math.pi * (k_ + 0.5) / 12
    rad = HZ["city"]["rings"][0]["r"][0] - 4
    p = (rad * math.sin(az), -rad * math.cos(az), 2.6)
    c = [pal("district_a"), pal("district_b"), (1.0, 0.55, 0.2)][k_ % 3]
    add_light("shop_%d" % k_, "AREA", p, LH["shop_w"], c, aim=(p[0] * 0.8, p[1] * 0.8, 0.0), size=10.0, size_y=2.0,
              group="city")


# ------------------------------------------------------------------ media: one fog box (haze + the field), plumes
def fog_material():
    m, nt = new_mat("fog")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g, ps, ns = pos_sep(nt)
    X, Y, Z = ps.outputs["X"], ps.outputs["Y"], ps.outputs["Z"]
    zoomv = nt.nodes.new("ShaderNodeValue")
    zoomv.name = "ZOOM"
    zoomv.outputs[0].default_value = 0.0
    w1 = nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=2.0)
    v = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mth(nt, "MULTIPLY", X, 0.006), v.inputs[0])
    nt.links.new(mth(nt, "MULTIPLY", Y, 0.006), v.inputs[1])
    nt.links.new(v.outputs[0], w1.inputs["Vector"])
    zw = mth(nt, "ADD", Z, mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", w1.outputs["Fac"], 0.5), 18.0))
    nz = []
    for (sx, sy, sz) in HF["layer_scales"]:
        n_ = nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=3.0, Roughness=0.55)
        vv = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(mth(nt, "MULTIPLY", X, sx), vv.inputs[0])
        nt.links.new(mth(nt, "MULTIPLY", Y, sx * 1.1), vv.inputs[1])
        nt.links.new(mth(nt, "MULTIPLY", zw, sz), vv.inputs[2])
        nt.links.new(vv.outputs[0], n_.inputs["Vector"])
        nz.append(n_.outputs["Fac"])
    # LOD: the wisp octave fades in with zoom (wisps_on_at); the big banks octave is always on
    kw = smooth(nt, zoomv.outputs[0], *LOD["wisps_on_at"])
    mixw = mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", nz[1], 0.5), mth(nt, "MULTIPLY", kw, 1 - HF["layer_mix"]))
    layer = smooth(nt, mth(nt, "ADD", mth(nt, "MULTIPLY", nz[0], HF["layer_mix"]),
                           mth(nt, "ADD", mixw, (1 - HF["layer_mix"]) * 0.5)), *HF["layer_remap"])
    cs = HF["clump_scale"]
    cn = nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=2.0)
    cv = nt.nodes.new("ShaderNodeCombineXYZ")
    for k_, (sock, s_) in enumerate(((X, cs[0]), (Y, cs[0] * 1.2), (Z, cs[2]))):
        nt.links.new(mth(nt, "MULTIPLY", sock, s_), cv.inputs[k_])
    nt.links.new(cv.outputs[0], cn.inputs["Vector"])
    clump = smooth(nt, cn.outputs["Fac"], *HF["clump_remap"])
    # LOD: ragged edges (the fine octave) fade in with zoom (fog_octaves_by_zoom)
    rag = nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=2.0)
    rv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mth(nt, "MULTIPLY", X, 0.05), rv.inputs[0])
    nt.links.new(mth(nt, "MULTIPLY", Y, 0.05), rv.inputs[1])
    nt.links.new(mth(nt, "MULTIPLY", zw, 0.6), rv.inputs[2])
    nt.links.new(rv.outputs[0], rag.inputs["Vector"])
    ko = smooth(nt, zoomv.outputs[0], *LOD["fog_octaves_by_zoom"])
    ragk = mth(nt, "ADD", 1.0, mth(nt, "MULTIPLY", ko, mth(nt, "SUBTRACT", mth(nt, "ADD", 0.45, mth(nt, "MULTIPLY", rag.outputs["Fac"], 0.75)), 1.0)))
    hf = mth(nt, "EXPONENT", mth(nt, "DIVIDE", mth(nt, "MULTIPLY", mth(nt, "MAXIMUM", mth(nt, "SUBTRACT", Z, 30.0), 0.0), -1.0),
                                 HF["height_scale"]))
    flo = smooth(nt, Z, HF["floor"] - 6.0, HF["floor"] + 4.0)
    body = mth(nt, "ADD", HF["base"], mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", layer, clump), ragk))
    cm = HF["calm"]
    sq = mth(nt, "MAXIMUM", mth(nt, "ABSOLUTE", X), mth(nt, "ABSOLUTE", Y))
    calm = mth(nt, "ADD", cm["k"], mth(nt, "MULTIPLY", 1.0 - cm["k"], smooth(nt, sq, cm["r"], cm["r"] + cm["soft"])))
    dens = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", body, hf), mth(nt, "MULTIPLY", flo, calm)),
               HF["peak"] * JOB.get("fog_k", 1.0))
    bk = HF["bank"]
    bank = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", smooth(nt, sq, bk["r"][0] - 10, bk["r"][0]),
                                   mth(nt, "SUBTRACT", 1.0, smooth(nt, sq, bk["r"][1], bk["r"][1] + 10))),
               mth(nt, "MULTIPLY", mth(nt, "SUBTRACT", 1.0, smooth(nt, Z, bk["z"][0], bk["z"][1])), clump))
    dens = mth(nt, "ADD", dens, mth(nt, "MULTIPLY", bank, bk["peak"]))
    dens = mth(nt, "ADD", dens, HF["haze"] * JOB.get("haze_k", 1.0))
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = tuple(HF["colour"]) + (1.0,)
    vs.inputs["Anisotropy"].default_value = HF["aniso"]
    nt.links.new(dens, vs.inputs["Density"])
    nt.links.new(vs.outputs[0], out.inputs["Volume"])
    return m, zoomv


def volume_box(name, b, mat, coll):
    x0, y0, z0, x1, y1, z1 = b
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
                    (x0, y1, z1)], [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


FOG_M, FOG_ZOOM = fog_material()
FOG = volume_box("fog", HF["box"], FOG_M, COLL["media"])


def plume_material(k_):
    m, nt = new_mat("plume_%d" % k_)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    r2 = mth(nt, "ADD", mth(nt, "POWER", mth(nt, "SUBTRACT", sep.outputs[0], 0.5), 2.0),
             mth(nt, "POWER", mth(nt, "SUBTRACT", sep.outputs[1], 0.5), 2.0))
    core = mth(nt, "SUBTRACT", 1.0, smooth(nt, mth(nt, "SQRT", r2), 0.08, 0.15))
    widen = mth(nt, "SUBTRACT", 1.0, smooth(nt, mth(nt, "SQRT", r2), 0.1, 0.5))
    shape = mth(nt, "MAXIMUM", mth(nt, "MULTIPLY", core, mth(nt, "SUBTRACT", 1.0, sep.outputs[2])),
                mth(nt, "MULTIPLY", widen, mth(nt, "MULTIPLY", sep.outputs[2], mth(nt, "SUBTRACT", 1.0, sep.outputs[2]))))
    nz = nn(nt, "ShaderNodeTexNoise", Scale=4.0, Detail=6.0, Roughness=0.6)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    d = mth(nt, "MULTIPLY", mth(nt, "MULTIPLY", shape, smooth(nt, nz.outputs["Fac"], 0.42, 0.7)), P["plumes"]["peak"])
    vk = nt.nodes.new("ShaderNodeValue")
    vk.name = "LODK"
    vk.outputs[0].default_value = 0.0
    d = mth(nt, "MULTIPLY", d, vk.outputs[0])
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = (0.9, 0.88, 1.0, 1.0)
    vs.inputs["Anisotropy"].default_value = 0.4
    nt.links.new(d, vs.inputs["Density"])
    nt.links.new(vs.outputs[0], out.inputs["Volume"])
    return m, vk


PLUME_K = []
pr = random.Random(9510)
near_roofs = sorted([r_ for r_ in ROOF if r_[3] == "near"], key=lambda r_: (r_[0], r_[1]))
pr.shuffle(near_roofs)
picked = []
for (cx, cy, h, _) in near_roofs:
    if any(math.hypot(cx - a, cy - b) < 90 for a, b in picked):
        continue
    picked.append((cx, cy))
    m, vk = plume_material(len(PLUME_K))
    hh = pr.uniform(*P["plumes"]["height"])
    ob = volume_box("plume_%d" % len(PLUME_K), (cx - 9, cy - 9, h, cx + 9, cy + 9, h + hh), m, COLL["media"])
    PLUME_K.append(vk)
    if len(PLUME_K) >= 8:
        break

# city glow under the fog by azimuth (linked to the media only), district colours alternating (hq_kit)
mcol = COLL["media"]
for k_, (gx, gy, which) in enumerate(CRING.glows_by_azimuth(8, (430.0, 700.0))):
    add_light("cityglow_%d" % k_, "AREA", (gx, gy, 6.0), 1.4e5 * LH["cityglow_k"] * JOB.get("glow_k", 1.0), pal(which),
              aim=(gx, gy, 100.0), size=110.0, size_y=60.0, shadow=False, group="city", receivers=mcol)
for k_ in range(8):
    az = 2 * math.pi * k_ / 8
    rad = HF["bank"]["r"][0] + 12
    p = (rad * math.sin(az), -rad * math.cos(az), 0.3)
    add_light("bankglow_%d" % k_, "AREA", p, LH["bank_glow"], TEAL if k_ % 2 else CWHITE, aim=(p[0], p[1], 20), size=30.0,
              size_y=14.0, shadow=False, group="civic", receivers=mcol)

# beams: the civic searchlights (tier corners + podium corners, leaning out on the diagonals) and the city's by azimuth
CB = HZ["civic_beams"]
BEAMS = []
for r in CB["tiers"]:
    t = TIERS[r]
    for sx in (-1, 1):
        for sy in (-1, 1):
            o = (sx * (t["hs"] - 1.0), sy * (t["hs"] - 1.0), t["z1"] + 0.4)
            BEAMS.append((o, (sx * CB["lean"][0] * 1.4, sy * CB["lean"][0] * 1.4, 1.0), CWHITE, CB["power"], CB["cone"]))
if CB["podium"]:
    for sx in (-1, 1):
        for sy in (-1, 1):
            o = (sx * (PX - 2.0), sy * (PX - 2.0), PH + 0.3)
            BEAMS.append((o, (sx * CB["lean"][1], sy * CB["lean"][1], 1.0), CWHITE, CB["power"] * 0.8, CB["cone"]))
BEAMS += CRING.beams_by_azimuth(ROOF, CITY, P, pal, LH["city_beam_k"])
for k_, (o, d, c, pw, cone) in enumerate(BEAMS):
    aim = Vector(o) + Vector(d).normalized() * 100.0
    add_light("beam_%d" % k_, "SPOT", o, pw * JOB.get("beam_k", 1.0), c, aim=aim, size=0.0, spot=cone, blend=0.15, shadow=False, group="beam",
              receivers=mcol)
log("lights", len(LIGHTS), "beams", len(BEAMS), "plumes", len(PLUME_K))

# ------------------------------------------------------------------ the eye's lights (gobo spots, updated per frame)
EYEL = HZ["eye"]
GOBO = []          # (light object, [(dot node, world normal)])


def gobo_light(name, energy, col, cone, nplanes, receivers=None):
    ob = add_light(name, "SPOT", (EX, EY, EZ), energy, col, aim=(EX, EY, EZ - 10), size=0.4, spot=cone, blend=0.08, shadow=False,
                   group="eye", receivers=receivers)
    ld = ob.data
    ld.use_nodes = True
    nt = ld.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputLight")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    fac = None
    planes = []
    for (mode, w, soft) in nplanes:
        dp = nt.nodes.new("ShaderNodeVectorMath")
        dp.operation = "DOT_PRODUCT"
        nt.links.new(tc.outputs["Normal"], dp.inputs[0])
        if mode == "half":
            f = smooth(nt, mth(nt, "MULTIPLY", dp.outputs["Value"], -1.0), -soft, soft)
        else:
            # a band: |dot(d, n) - c| < w (c = the sine of the scan line's elevation, set per frame)
            o = mth(nt, "SUBTRACT", dp.outputs["Value"], 0.0)
            f = mth(nt, "SUBTRACT", 1.0, smooth(nt, mth(nt, "ABSOLUTE", o), w * 0.4, w))
            planes.append(o.node)
        fac = f if fac is None else mth(nt, "MULTIPLY", fac, f)
        planes.append(dp)
    em.inputs["Color"].default_value = tuple(col)[:3] + (1.0,)
    nt.links.new(fac, em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs[0])
    GOBO.append((ob, planes))
    return ob, planes


# the gaze and the blade light the compound only (light-linked): the plaza and the city never catch the scan
GAZE_RX = bpy.data.collections.new("gaze_rx")
for c_ in ("compound", "rooms", "eye"):
    for ob_ in COLL[c_].objects:
        GAZE_RX.objects.link(ob_)
WASH, WASH_P = gobo_light("eye_wash", EYEL["wash_w"], SCAN, EYEL["wash_cone"],
                          [("half", 0, EYEL["wash_soft"]), ("half", 0, EYEL["wash_soft"])], receivers=GAZE_RX)
WASH.visible_volume_scatter = False          # the gaze lights the faces at full power ...
WASHV, WASHV_P = gobo_light("eye_wash_vol", EYEL["wash_w"] * EYEL["wash_vol"], SCAN, EYEL["wash_cone"],
                            [("half", 0, EYEL["wash_soft"]), ("half", 0, EYEL["wash_soft"])], receivers=mcol)
#                                              ... and a weak twin, linked to the media only, draws its cone in the fog
BLADE, BLADE_P = gobo_light("eye_blade", EYEL["blade_w"], SCAN, EYEL["blade_cone"],
                            [("sheet", EYEL["blade_halfwidth"], 0), ("half", 0, EYEL["wash_soft"]),
                             ("half", 0, EYEL["wash_soft"])], receivers=GAZE_RX)
LBEAM = add_light("eye_beam", "SPOT", (EX, EY, EZ), EYEL["beam_w"], SCAN, aim=(EX, EY - 10, EZ), size=0.0,
                  spot=EYEL["beam_cone"][0], blend=0.2, shadow=False, group="eye", receivers=mcol)
LBEAM2 = add_light("eye_beam_soft", "SPOT", (EX, EY, EZ), EYEL["beam_w"] * 0.35, SCAN, aim=(EX, EY - 10, EZ), size=0.0,
                   spot=EYEL["beam_cone"][1], blend=0.6, shadow=False, group="eye", receivers=mcol)
EGLOW = add_light("eye_glow", "POINT", (EX, EY, EZ), EYEL["glow_w"], SCAN, size=2.0, group="eye", shadow=False)


def set_plane(dp, ob, n):
    rot = ob.rotation_euler.to_matrix()
    nl = rot.transposed() @ Vector(n).normalized()
    dp.inputs[1].default_value = tuple(nl)


def set_eye(e):
    """Turn the turret to azimuth az (rig yaw: 0 looks +y / north... looks along (sin az, cos az)), aim the gaze at the
    watched face's quadrant, place the blade's scan line at height `sweep`, and the lighthouse beam along az."""
    az = math.radians(e["az"])
    dvec = Vector((math.sin(az), math.cos(az), 0.0))
    for ob in EYE_OBJS:
        ob.rotation_euler = (0.0, 0.0, -az)
    front = Vector((EX, EY, EZ)) + dvec * (EYE["drum_d"] * 0.5 + 1.2)
    nvec = dvec
    tvec = Vector((-dvec.y, dvec.x, 0.0))          # counter-clockwise tangent
    hs_mid = TIERS[2]["hs"]
    for ob in (WASH, WASHV, BLADE, LBEAM, LBEAM2, EGLOW):
        ob.location = front
    aim = Vector((0, 0, 0)) + nvec * hs_mid * 1.1 + Vector((0, 0, 30.0))
    WASH.rotation_euler = (aim - front).to_track_quat("-Z", "Y").to_euler()
    WASHV.rotation_euler = WASH.rotation_euler
    # the gaze wedge: the quadrant round the azimuth (between the two diagonals); planes keep dot(d, n) < 0
    n1 = (tvec - nvec)
    n2 = (-tvec - nvec)
    set_plane(WASH_P[0], WASH, n1)
    set_plane(WASH_P[1], WASH, n2)
    set_plane(WASHV_P[0], WASHV, n1)
    set_plane(WASHV_P[1], WASHV, n2)
    EK = JOB.get("eye_k", 1.0)
    WASH.data.energy = EYEL["wash_w"] * e.get("wash", 1.0) * EK
    WASHV.data.energy = EYEL["wash_w"] * EYEL["wash_vol"] * e.get("wash", 1.0) * EK
    sweep = e.get("sweep")
    if sweep is None:
        BLADE.data.energy = 0.0
    else:
        z = float(sweep)
        hs_at = max(TIERS[0]["hs"] - (z - PH) / CP["tier_h"] * (C["PITCH"] / 2.0), TIERS[-1]["hs"])
        v = nvec * hs_at + Vector((0, 0, z - front.z))
        aimb = front + v
        BLADE.rotation_euler = (aimb - front).to_track_quat("-Z", "Y").to_euler()
        # the scan line: a band of constant elevation (a cone round the vertical through the eye), so it draws one
        # horizontal line at height z across every face in the sector
        if e.get("sweep_pt"):
            dpt = Vector(e["sweep_pt"]) - front
            BLADE_P[0].inputs[1].default_value = dpt.normalized().z
        else:
            BLADE_P[0].inputs[1].default_value = math.sin(math.atan2(z - front.z, hs_at * 1.12))
        set_plane(BLADE_P[1], BLADE, Vector((0, 0, 1)))
        set_plane(BLADE_P[2], BLADE, n1)
        set_plane(BLADE_P[3], BLADE, n2)
        BLADE.data.energy = EYEL["blade_w"] * e.get("blade", 1.0) * EK
    pitch = math.radians(EYEL["beam_pitch"])
    bd = Vector((dvec.x * math.cos(pitch), dvec.y * math.cos(pitch), -math.sin(pitch)))
    for ob in (LBEAM, LBEAM2):
        ob.rotation_euler = bd.to_track_quat("-Z", "Y").to_euler()
    LBEAM.data.energy = EYEL["beam_w"] * e.get("beam", 1.0) * EK
    LBEAM2.data.energy = EYEL["beam_w"] * 0.35 * e.get("beam", 1.0) * EK
    OBJ["eye_iris"]["pwo"] = float(e.get("iris", 1.0))
    OBJ["eye_iris"].update_tag()


# ================================================================== world, camera
world = bpy.data.worlds.new("w")
scene.world = world
try:
    world.use_nodes = True
except Exception:  # noqa: BLE001
    pass
wnt = world.node_tree
wnt.nodes.clear()
wo = wnt.nodes.new("ShaderNodeOutputWorld")
bg = wnt.nodes.new("ShaderNodeBackground")
geo_w = wnt.nodes.new("ShaderNodeTexCoord")
wsep = wnt.nodes.new("ShaderNodeSeparateXYZ")
wnt.links.new(geo_w.outputs["Generated"], wsep.inputs[0])
ramp = wnt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.10, 0.035, 0.11, 1)
ramp.color_ramp.elements[1].position = 0.42
ramp.color_ramp.elements[1].color = (0.004, 0.005, 0.016, 1)
e_ = ramp.color_ramp.elements.new(0.12)
e_.color = (0.03, 0.016, 0.055, 1)
wnt.links.new(wsep.outputs["Z"], ramp.inputs[0])
wnt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
wnt.links.new(bg.outputs[0], wo.inputs[0])
cam_data = bpy.data.cameras.new("cam")
cam_data.sensor_fit = "HORIZONTAL"
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.5
cam_data.clip_end = 6000.0
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def set_cam(p):
    cam.location = p["loc"]
    cam.rotation_euler = (Vector(p["tgt"]) - Vector(p["loc"])).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = p["lens"]
    cam_data.shift_x = p.get("shift_x", 0.0)
    cam_data.shift_y = p.get("shift_y", 0.0)


def set_pwo(ob, k):
    if ob is not None:
        ob["pwo"] = float(k)
        ob.update_tag()


LOCK_OBJ = {}


def lock_obj(i):
    """The red holo lockdown plane over room i's opening (built on first use)."""
    if i in LOCK_OBJ:
        return LOCK_OBJ[i]
    n = NODES[i]
    f = n["face"]
    hs = TIERS[n["tier"]]["hs"]
    z0, z1 = n["z"]
    u0, u1 = n["u"] - RW / 2, n["u"] + RW / 2
    acc = Acc("lock_" + i, M_LOCK, 5, COLL["rooms"])
    fquad(acc, f, hs - 0.35, u0 + 0.05, z0 + 0.05, u1 - 0.05, z1 - 0.05, LOCK)
    fr = Acc("lockf_" + i, M_EMIT, 5, COLL["rooms"])
    for (a0, a1, b0, b1) in ((u0, u0 + 0.2, z0, z1), (u1 - 0.2, u1, z0, z1), (u0, u1, z1 - 0.2, z1), (u0, u1, z0, z0 + 0.2)):
        fquad(fr, f, hs - 0.3, a0, b0, a1, b1, LOCK, 6.0)
    LOCK_OBJ[i] = (acc.build(), fr.build())
    return LOCK_OBJ[i]


def apply_frame(fr):
    set_cam(fr["pose"])
    KSEC.set_frame(scene, fr.get("section") if not JOB.get("no_section") else None)
    _oc = fr.get("section") if not JOB.get("no_section") else None
    if _oc and "occ_on" in _oc:                   # v3: the occlusion rule's python twin: how many buildings it touched
        _st = [KDT.occlusion_state(_oc, b_) for b_ in BLD]
        log("occlusion %s: flattened %d ghosted %d of %d" % (fr.get("name"), sum(1 for (z_, a_), b_ in zip(_st, BLD)
            if z_ < b_[2] - 0.5), sum(1 for (z_, a_) in _st if a_ < 0.6), len(BLD)))
    zoom = float(fr.get("zoom", 0.0))
    FOG_ZOOM.outputs[0].default_value = zoom
    FOG.update_tag()
    lw = KLOD.weights(zoom, LOD, floors={})
    for vk in PLUME_K:
        vk.outputs[0].default_value = lw["plumes_on_at"]
    ksig = lw["signage_on_at"]
    ksm = lw["small_lights_on_at"]
    st = fr.get("room_state", LY["state"])
    sc = set(fr.get("scanned", LY["scanned"]))
    pw = fr.get("power")
    keep = set(pw["keep"]) if pw else set()
    cut = pw["k"] if pw else 1.0
    boost = pw.get("boost", 1.45) if pw else 1.0
    base = {"sign": ksig * 0.85 + 0.15, "city_sign": ksig, "small": 0.25 + 0.75 * ksm, "city_small": 0.3 + 0.7 * ksm}
    for name, ob in OBJ.items():
        if ob is None or not ob.data.materials or ob.data.materials[0] not in (M_EMIT, M_CITY, M_CEMIT):
            continue
        k = base.get(name, 1.0)
        if name.startswith("room_"):
            i = name[5:]
            k = STATE_K.get(st.get(i, "reach"), 0.3) * (1.3 if i in sc else 1.0)
            if pw and i in keep:
                k *= boost
            elif pw:
                k *= cut
        elif pw and not name.startswith("eye_"):
            k *= cut
        set_pwo(ob, k)
    for i in [n for n in NODES if n not in ("start",)]:
        if i in sc:
            a, b = lock_obj(i)
            for o in (a, b):
                o.hide_render = False
                set_pwo(o, 1.0)
        elif i in LOCK_OBJ:
            for o in LOCK_OBJ[i]:
                o.hide_render = True
    for (lob, e0, grp) in LIGHTS:
        if grp.startswith("room:"):
            i = grp[5:]
            s = st.get(i, "target" if i == "srv" else "reach")
            n = NODES[i]
            tc = TYPE_COL[n["kind"]]
            c = tuple(0.55 * a + 0.45 for a in tc)
            kk = STATE_K.get(s, 0.3) * LH["room_k"]
            if i in sc:
                c = LOCK
                kk = max(kk, 0.3) * LH["lockdown_k"]
            if pw:
                kk *= boost if i in keep else cut
            lob.data.color = c[:3]
            lob.data.energy = e0 * kk
        elif grp in ("civic", "city", "start") and pw:
            lob.data.energy = e0 * cut
        elif grp in ("civic", "city", "start"):
            lob.data.energy = e0
    set_eye(fr["eye"])


# ================================================================== render
def gpu_setup():
    if JOB.get("cpu"):
        return False
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "HIP"
        try:
            prefs.use_hiprt = False
        except (AttributeError, TypeError):
            pass
        prefs.refresh_devices()
        n = 0
        for d in prefs.devices:
            d.use = d.type == "HIP"
            n += d.use
        log("HIP devices", n)
        return n > 0
    except Exception as e:  # noqa: BLE001
        log("HIP setup failed", e)
        return False


scene.render.engine = "CYCLES"
cy = scene.cycles
cy.device = "GPU" if gpu_setup() else "CPU"
cy.samples = JOB.get("samples", 64)
cy.use_adaptive_sampling = True
cy.adaptive_threshold = JOB.get("threshold", 0.02)
cy.adaptive_min_samples = min(16, cy.samples)
cy.use_denoising = True
for k_, v_ in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_input_passes", "RGB_ALBEDO_NORMAL"),
               ("denoising_prefilter", "ACCURATE"), ("denoising_quality", "HIGH"), ("denoising_use_gpu", True)):
    try:
        setattr(cy, k_, v_)
    except (TypeError, AttributeError):
        pass
cy.seed = 7
cy.use_light_tree = True
cy.max_bounces = 6
cy.diffuse_bounces = 2
cy.glossy_bounces = 3
cy.transmission_bounces = 3
cy.volume_bounces = 0
cy.transparent_max_bounces = 16
cy.sample_clamp_indirect = 6.0
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.volume_step_rate = JOB.get("step_rate", 1.0)
cy.volume_max_steps = int(JOB.get("max_steps", 256))
scene.render.use_persistent_data = True
scene.render.resolution_x, scene.render.resolution_y = JOB["res"]
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
vl = bpy.context.view_layer
vl.use_pass_combined = True
vl.use_pass_z = True
vl.use_pass_emit = True
vl.use_pass_object_index = True
try:
    vl.cycles.use_pass_volume_direct = True
except AttributeError:
    pass
s_ = scene.render.image_settings
try:
    s_.media_type = "MULTI_LAYER_IMAGE"
except (AttributeError, TypeError):
    pass
s_.file_format = "OPEN_EXR_MULTILAYER"
s_.color_depth = "32"
if JOB.get("engine") == "EEVEE":                          # HQ_REV_V2: layout previews (no GPU lock needed)
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue
    for k_, v_ in (("taa_render_samples", int(JOB.get("samples", 16))), ("volumetric_start", 1.0),
                   ("volumetric_end", 2500.0), ("volumetric_tile_size", "4"), ("volumetric_samples", 48),
                   ("use_volumetric_shadows", False), ("use_shadows", True), ("use_raytracing", False)):
        try:
            setattr(scene.eevee, k_, v_)
        except (AttributeError, TypeError):
            pass
    vl.use_pass_object_index = False


def exr_to_npy(path, stem, want):
    import OpenImageIO as oiio
    import numpy as np
    inp = oiio.ImageInput.open(path)
    found = []
    k = 0
    while inp.seek_subimage(k, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        pas = ".".join(names[0].split(".")[1:-1]) if names[0].count(".") >= 2 else names[0]
        found.append(pas)
        if pas in want:
            px = np.asarray(inp.read_image(k, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
            keepc = [ci for ci, nm in enumerate(names) if not nm.endswith(".A")]
            arr = px[..., keepc]
            if pas in ("Depth", "Object Index"):
                np.save(stem + "_" + want[pas] + ".npy", arr[..., :1].astype(np.float32))
            else:
                np.save(stem + "_" + want[pas] + ".npy", arr[..., :3].astype(np.float16))
        k += 1
    inp.close()
    return found


if JOB.get("save_blend"):
    apply_frame(JOB["frames"][0])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "scene.blend"))
for fr in JOB["frames"]:
    stem = os.path.join(OUT, fr["name"])
    if os.path.exists(stem + "_combined.npy") and not JOB.get("force"):
        continue
    apply_frame(fr)
    scene.render.filepath = stem + ".exr"
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    found = exr_to_npy(stem + ".exr", stem, {"Combined": "combined", "Emission": "emit", "Object Index": "index",
                                             "Volume Direct": "voldir"})
    os.remove(stem + ".exr")
    log("frame", fr["name"], "%.1f s" % (time.time() - t1), "passes", found if fr is JOB["frames"][0] else "")
log("done")
# OCC_V3
