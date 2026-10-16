"""HQ kit: the generic Blender build + render for an HQ run (Cycles HIP; Eevee for layout previews), generalised from
hq_halcyon/scripts/hq_scene.py. The corp's landmark, rooms on it, links and mechanic are built by hq_build.py
(build(K) -> hooks); everything else is shared: materials, the cutaway room kit, plaza / ring road / perimeter, the
hq_kit 360 degree ring city, traffic streaks, the r3 fog + plumes + glows, the city beams, the state ladder, the power
cut, the LOD bands, movers (objects that carry rooms) and the render passes.

blender -b --factory-startup --python hq_scene.py -- <job.json>
job: out, res [w, h], samples, threshold, step_rate, engine ("CYCLES" | "EEVEE"),
     frames: [{name, pose {loc, tgt, lens, shift_x, shift_y}, zoom, mt (mechanic time), room_state {id: state},
               affected [ids], movers {name: [x, y, z]}, mech {..corp..}, power {keep, k, boost} | null}]
Seeds: city (preset), 9402 (lanes), 9500 (beams), 9510 (plumes), 9520 (glows); the corp build uses its own.
"""
import json
import math
import os
import random
import sys
import time
from types import SimpleNamespace

import bpy
from mathutils import Vector

T0 = time.time()
argv = sys.argv[sys.argv.index("--") + 1:]
JOB = json.load(open(argv[0]))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402
import hq_graph as G  # noqa: E402
from hq_kit import city_ring as CRING  # noqa: E402
from hq_kit import states as KST  # noqa: E402

P = HP.PRESET
HZ = P["hq"]
CP = HZ["compound"]
HF = P["hq_fog"]
LOD = P["lod_bands"]
pal = HP.pal
LH = HZ["light"]
NF = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]      # hq_kit square faces S E N W (city ring helpers)
TF = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
OUT = JOB["out"]
os.makedirs(OUT, exist_ok=True)
EEVEE = JOB.get("engine", "CYCLES") != "CYCLES"

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




# ================================================================== instances
M_CIVIC = mat_civic()
M_CUT = mat_plain("cut", rough=0.5, spec=0.4)
M_INT = mat_plain("interior", rough=0.35, spec=0.5, coat=0.2)
M_METAL = mat_plain("metal", rough=0.32, spec=0.6, metal=0.7)
M_ROUGH = mat_plain("rough", rough=0.7, spec=0.35)
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

COLL = {k: bpy.data.collections.new(k) for k in ("compound", "rooms", "city", "ground", "streaks", "movers", "media",
                                                  "lights")}
for c_ in COLL.values():
    scene.collection.children.link(c_)
A = {
    "civic": Acc("civic", M_CIVIC, 1, COLL["compound"]),
    "cut": Acc("cut", M_CUT, 1, COLL["compound"]),
    "metal": Acc("metal", M_METAL, 1, COLL["compound"]),
    "rough": Acc("rough", M_ROUGH, 1, COLL["compound"]),
    "glass": Acc("glass", M_GLASS, 1, COLL["compound"]),
    "trim": Acc("trim", M_EMIT, 1, COLL["compound"]),          # big layer: building light lines
    "gold": Acc("gold", M_EMIT, 1, COLL["compound"]),
    "sign": Acc("sign", M_EMIT, 1, COLL["compound"]),          # LOD signage
    "small": Acc("small", M_EMIT, 1, COLL["compound"]),        # LOD small lights
    "int": Acc("int", M_INT, 5, COLL["rooms"]),
    "ground": Acc("ground", M_GROUND, 4, COLL["ground"]),
    "city": Acc("city", M_CITY, 2, COLL["city"]),
    "city_neon": Acc("city_neon", M_CEMIT, 2, COLL["city"]),
    "city_sign": Acc("city_sign", M_CEMIT, 2, COLL["city"]),
    "city_small": Acc("city_small", M_CEMIT, 2, COLL["city"]),
    "city_metal": Acc("city_metal", M_CMETAL, 2, COLL["city"]),
    "streaks": Acc("streaks", M_CEMIT, 7, COLL["streaks"]),
    "sky": Acc("sky", M_EMIT, 2, COLL["city"]),
}
ROOM_EMIT = {}
CUTC = pal("panel_dark")
LOCK = pal("lockdown")
WHITE = pal("panel")
CONC = pal("concrete")
TYPE_COL = {"router": (0.30, 0.85, 1.0), "elite": (1.0, 0.36, 0.10), "terminal": (0.20, 1.0, 0.50),
            "modem": (0.30, 0.50, 1.0), "rack": (1.0, 0.70, 0.20), "target": (1.0, 0.22, 0.12), "start": (0.83, 1.0, 0.0)}
STATE_K = KST.STATE_K
RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]


# ================================================================== oriented frames (any outward normal)
def tang(n):
    return (n[1], -n[0])


def rf(rec, dn, du, z):
    """Room / facade frame -> world: dn along the outward normal from the opening plane, du along screen-right."""
    n = rec["n"] or (0.0, 1.0)
    t = tang(n)
    o = rec["o"]
    return (o[0] + n[0] * dn + t[0] * du, o[1] + n[1] * dn + t[1] * du, z)


def obox(acc, rec, u0, u1, dn0, dn1, z0, z1, col, k=0.0, top=True, bottom=False):
    """An oriented box in a frame: u0..u1 along the tangent, dn0..dn1 along the normal, z0..z1."""
    c = [[rf(rec, dn, u, z) for (u, dn) in ((u0, dn0), (u1, dn0), (u1, dn1), (u0, dn1))] for z in (z0, z1)]
    b, t_ = c
    for i in range(4):
        j = (i + 1) % 4
        acc.face([b[i], b[j], t_[j], t_[i]], col, k)
    if top:
        acc.face(t_, col, k)
    if bottom:
        acc.face(list(reversed(b)), col, k)


def oquad(acc, rec, dn, u0, z0, u1, z1, col, k=0.0):
    acc.face([rf(rec, dn, u0, z0), rf(rec, dn, u1, z0), rf(rec, dn, u1, z1), rf(rec, dn, u0, z1)], col, k)


def frame_of(o, n):
    return dict(o=o, n=n)


def seg_box(acc, p, q, w, h, col, k=0.0):
    """A flat walkway / beam box from p to q (w wide across, h thick, top at the path height)."""
    p, q = Vector(p), Vector(q)
    d = q - p
    if d.length < 1e-4:
        return
    side = Vector((-d.y, d.x, 0.0))
    side = side.normalized() * (w / 2) if side.length > 1e-6 else Vector((w / 2, 0, 0))
    dz = Vector((0, 0, -h))
    a = [p - side, q - side, q + side, p + side]
    b = [v + dz for v in a]
    acc.face(a, col, k)
    acc.face(list(reversed(b)), col, k)
    for i in range(4):
        j = (i + 1) % 4
        acc.face([b[i], b[j], a[j], a[i]], col, k)


# ================================================================== the cutaway room kit (any frame)
def room_shell(i, rec, accs=None, kind=None):
    """A cutaway room: floor, back wall, side walls, ceiling, the cut frame, ceiling strips and the per-kind dressing.
    rec: dict(o, n, w, h, d) (o = the opening's sill centre). accs: {"int", "cut", "metal", "emit"} (defaults: the
    shared ones + a per-room emission accumulator, whose weight follows the room's state)."""
    acc_int = (accs or {}).get("int", A["int"])
    acc_cut = (accs or {}).get("cut", A["cut"])
    acc_met = (accs or {}).get("metal", A["metal"])
    em = (accs or {}).get("emit") or ROOM_EMIT.setdefault(i, Acc("room_" + i, M_EMIT, 5, COLL["rooms"]))
    ROOM_EMIT[i] = em
    w, h, d = rec["w"], rec["h"], rec["d"]
    z0 = rec["o"][2]
    z1 = z0 + h
    u0, u1 = -w / 2, w / 2
    kind = kind or G.KIND[i]
    inner = (0.50, 0.53, 0.56)

    def rb(a0, a1, din0, din1, zz0, zz1, col, k=0.0, ac=None):
        obox(ac or acc_int, rec, a0, a1, -din1, -din0, zz0, zz1, col, k)

    rb(u0, u1, 0, d, z0 - 0.4, z0, (0.34, 0.35, 0.38))
    oquad(acc_int, rec, -d, u1, z0, u0, z1, inner)
    rb(u0 - 0.3, u0, 0, d, z0, z1, tuple(v * 0.9 for v in inner))
    rb(u1, u1 + 0.3, 0, d, z0, z1, tuple(v * 0.9 for v in inner))
    rb(u0, u1, 0, d, z1, z1 + 0.3, tuple(v * 0.8 for v in inner))
    for (a0, a1, b0, b1) in ((u0 - 0.45, u0, z0 - 0.5, z1 + 0.5), (u1, u1 + 0.45, z0 - 0.5, z1 + 0.5),
                             (u0, u1, z1, z1 + 0.5), (u0, u1, z0 - 0.5, z0 - 0.4)):
        oquad(acc_cut, rec, 0.02, a0, b0, a1, b1, CUTC)
    tc = TYPE_COL.get(kind, (1, 1, 1))
    for frac in (0.3, 0.7):
        rb(u0 + 0.8, u1 - 0.8, d * frac - 0.18, d * frac + 0.18, z1 - 0.12, z1 - 0.02, (0.80, 0.93, 1.0), 4.0, em)
    bk = d
    if kind == "router":
        rb(u0 + w * 0.2, u0 + w * 0.65, 3.6, 5.0, z0, z0 + 1.1, (0.7, 0.72, 0.75))
        for m_ in range(4):
            a = u0 + 1.5 + m_ * (w - 3) / 4
            rb(a, a + (w - 3) / 4 - 0.4, bk - 0.12, bk - 0.02, z0 + 3.2, z0 + 5.4, tc, 3.2, em)
        rb(u1 - 3.4, u1 - 3.0, 6.0, 8.0, z0, z0 + 1.2, (0.4, 0.4, 0.45), ac=acc_met)
    elif kind == "elite":
        for m_ in range(3):
            a = u0 + 1.4 + m_ * (w - 2.8) / 3
            rb(a, a + (w - 2.8) / 3 - 0.6, bk - 1.2, bk - 0.2, z0, z0 + 6.0, (0.18, 0.18, 0.2), ac=acc_met)
            rb(a + 0.2, a + 0.45, bk - 1.25, bk - 1.2, z0 + 0.6, z0 + 5.5, tc, 4.0, em)
        rb(u0 + w * 0.3, u0 + w * 0.7, 5.5, 7.0, z0, z0 + 0.9, (0.3, 0.3, 0.32))
    elif kind == "terminal":
        rb(u0 + 1.4, u1 - 1.4, bk - 0.1, bk - 0.02, z0 + 1.6, z0 + 6.6, tc, 2.6, em)
        rb(u0 + w * 0.35, u0 + w * 0.65, 3.0, 4.5, z0, z0 + 1.0, (0.62, 0.64, 0.66))
    elif kind == "modem":
        for m_ in range(4):
            a = u0 + 1.2 + m_ * (w - 2.4) / 4
            rb(a, a + (w - 2.4) / 4 - 0.5, bk - 1.4, bk - 0.1, z0, z0 + 5.2, (0.3, 0.32, 0.36), ac=acc_met)
            for sh in range(3):
                rb(a + 0.1, a + (w - 2.4) / 4 - 0.6, bk - 1.45, bk - 1.4, z0 + 1.0 + sh * 1.6, z0 + 1.3 + sh * 1.6, tc, 3.0, em)
    return em


def lock_plane(i, rec, col, accs=None, name="lock"):
    """A translucent holo plane over a room's opening (the mechanic's 'affected' state) + a frame in col."""
    acc = Acc("%s_%s" % (name, i), M_LOCK, 5, COLL["rooms"])
    w, h = rec["w"], rec["h"]
    z0 = rec["o"][2]
    oquad(acc, rec, -0.35, -w / 2 + 0.05, z0 + 0.05, w / 2 - 0.05, z0 + h - 0.05, col)
    fr = Acc("%sf_%s" % (name, i), M_EMIT, 5, COLL["rooms"])
    for (a0, a1, b0, b1) in ((-w / 2, -w / 2 + 0.2, z0, z0 + h), (w / 2 - 0.2, w / 2, z0, z0 + h),
                             (-w / 2, w / 2, z0 + h - 0.2, z0 + h), (-w / 2, w / 2, z0, z0 + 0.2)):
        oquad(fr, rec, -0.3, a0, b0, a1, b1, col, 6.0)
    return acc, fr


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
        try:
            ob.light_linking.receiver_collection = receivers
        except AttributeError:
            pass
    LIGHTS.append((ob, energy, group))
    return ob


# ================================================================== movers (objects that carry rooms)
MOVERS = {}          # name -> dict(accs {key: Acc}, objs [], lights [(ob, local loc)])


def mover(name):
    if name not in MOVERS:
        mats = {"struct": M_CIVIC, "rough": M_ROUGH, "metal": M_METAL, "int": M_INT, "cut": M_CUT, "glass": M_GLASS,
                "emit": M_EMIT, "trim": M_EMIT, "small": M_EMIT, "lock": M_LOCK}
        MOVERS[name] = dict(accs={k: Acc("mv_%s_%s" % (name, k), m, 6 if k != "int" else 5, COLL["movers"])
                                  for k, m in mats.items()}, objs=[], lights=[])
    return MOVERS[name]


def mover_room(i, name, rec_local):
    """Build room i into mover `name` in local coordinates (rec_local['o'] is relative to the mover origin)."""
    mv = mover(name)
    em = Acc("room_" + i, M_EMIT, 5, COLL["movers"])
    ROOM_EMIT[i] = em
    room_shell(i, rec_local, accs={"int": mv["accs"]["int"], "cut": mv["accs"]["cut"], "metal": mv["accs"]["metal"],
                                   "emit": em})
    mv.setdefault("rooms", []).append(i)
    return em


# ================================================================== plaza, ring road, walk, perimeter (square rings)
RDP = HZ["road"]
PL = RDP["plaza"]
R0, R1 = RDP["road"]
W0, W1 = RDP["walk"]
if not HZ.get("no_plaza") and not HZ.get("downtown"):
    box(A["ground"], -PL, -PL, -0.02, PL, PL, 0.0, (0.40, 0.42, 0.45), k=1.0)
    for f in range(4):
        fbox(A["ground"], f, R0, R1, -R1, R1, -0.02, 0.0, (0.055, 0.055, 0.06), k=0.0)
        fbox(A["ground"], f, W0, W1, -W1, W1, 0.0, 0.25, (0.30, 0.30, 0.32), k=1.0)
        md = (R0 + R1) / 2
        u = -R1
        while u < R1:
            fbox(A["ground"], f, md - 0.12, md + 0.12, u, u + 4.5, 0.0, 0.012, (0.55, 0.52, 0.42), k=0.0)
            u += 9.0
box(A["ground"], -1600, HZ.get("ground_cut_y") or -1600, -0.05, 1600, 1600, -0.02, (0.06, 0.06, 0.07), k=0.0)
PER = HZ["city"]["perimeter"]
if PER and not HZ.get("downtown"):
    for f in range(4):
        fbox(A["ground"], f, W1, PER["r"][1], -PER["r"][1], PER["r"][1], -0.02, 0.0, (0.16, 0.17, 0.19), k=1.0)
        fbox(A["rough"], f, PER["wall_r"], PER["wall_r"] + 2.0, -PER["wall_r"] - 2.0, PER["wall_r"] + 2.0, 0.0,
             PER["wall_h"], CONC)
        u = -PER["wall_r"] + 8.0
        while u < PER["wall_r"] - 4:
            fbox(A["small"], f, PER["wall_r"] - 0.1, PER["wall_r"] + 0.3, u - 0.3, u + 0.3, PER["wall_h"],
                 PER["wall_h"] + 0.5, (1.0, 0.06, 0.04), 8.0)
            u += 24.0

# ------------------------------------------------------------------ the Cell's city: the 360 degree ring (hq_kit)
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
if HZ.get("downtown"):
    DT = KDT.build(HZ["downtown"], A, SimpleNamespace(box=box, tube=tube, bc=set_bc), pal)
    ROOF += DT["roofs"]
    log("downtown towers", DT["n_towers"], "lamps", len(DT["lamps"]))
log("city built, roofs", len(ROOF))

# ------------------------------------------------------------------ the corp's landmark, rooms, links, mechanic
import hq_build as B  # noqa: E402
K = SimpleNamespace(A=A, Acc=Acc, COLL=COLL, box=box, fbox=fbox, fquad=fquad, fp=fp, tube=tube, fdisc=fdisc, obox=obox,
                    oquad=oquad, rf=rf, tang=tang, seg_box=seg_box, room_shell=room_shell, lock_plane=lock_plane,
                    add_light=add_light, mover=mover, mover_room=mover_room, MOVERS=MOVERS, ROOM_EMIT=ROOM_EMIT,
                    pal=pal, P=P, HZ=HZ, CP=CP, LH=LH, G=G, log=log, JOB=JOB, ROOF=ROOF, TYPE_COL=TYPE_COL,
                    M=dict(civic=M_CIVIC, cut=M_CUT, int=M_INT, metal=M_METAL, rough=M_ROUGH, glass=M_GLASS,
                           emit=M_EMIT, lock=M_LOCK, ground=M_GROUND, city=M_CITY),
                    nn=nn, mth=mth, smooth=smooth, attr=attr, new_mat=new_mat, pos_sep=pos_sep, vsc=vsc, vmul=vmul,
                    mixc=mixc, scene=scene, Vector=Vector, sstep=sstep)
HOOKS = B.build(K)
log("landmark built")

# ------------------------------------------------------------------ build the objects
OBJ = {}
for k_, acc in A.items():
    OBJ[k_] = acc.build()
for k_, acc in HOOKS.get("accs", {}).items():
    OBJ[k_] = acc.build()
for i, acc in ROOM_EMIT.items():
    OBJ["room_" + i] = acc.build()
for name, mv in MOVERS.items():
    for k_, acc in mv["accs"].items():
        ob = acc.build()
        if ob is not None:
            mv["objs"].append(ob)
            OBJ["mv_%s_%s" % (name, k_)] = ob
    for i in mv.get("rooms", []):
        if OBJ.get("room_" + i) is not None:
            mv["objs"].append(OBJ["room_" + i])
if "post_build" in HOOKS:
    HOOKS["post_build"](OBJ)
log("objects", len([o for o in OBJ.values() if o]))

# room lights (one area light per room, state-driven); mover rooms' lights ride their mover
ROOM_LIGHTS = {}
for i in G.NODES:
    if i in ("start",) or i in HOOKS.get("no_room_light", ()):
        continue
    mvn = next((n_ for n_, mv in MOVERS.items() if i in mv.get("rooms", [])), None)
    rec = HOOKS["local_rec"](i) if mvn else G.room_rec(i, JOB["frames"][0].get("mt"))
    z0 = rec["o"][2]
    if rec["n"] is None:
        ROOM_LIGHTS[i] = add_light("room_%s" % i, "POINT", (rec["o"][0], rec["o"][1], z0 + rec["h"] * 0.6),
                                   LH["room_w"] * 2.0, (1.0, 0.3, 0.15), size=2.0, group="room:" + i)
    else:
        loc = rf(rec, -rec["d"] * 0.45, 0.0, z0 + rec["h"] - 0.3)
        ROOM_LIGHTS[i] = add_light("room_%s" % i, "AREA", loc, LH["room_w"], (1, 1, 1),
                                   aim=rf(rec, -rec["d"] * 0.45, 0.0, z0), size=rec["w"] - 1.0, size_y=rec["d"] - 1.5,
                                   group="room:" + i)
    if mvn:
        MOVERS[mvn]["lights"].append((ROOM_LIGHTS[i], tuple(ROOM_LIGHTS[i].location)))
for name, mv in MOVERS.items():
    for (lob, loc) in HOOKS.get("mover_lights", {}).get(name, []):
        mv["lights"].append((lob, loc))
# HQ_REV_V2: the downtown's street lamps nearest the compound light their pools on the wet street (real spots)
if DT:
    DTC = HZ["downtown"]
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
BG = HZ.get("bank_glow_cols", ["yard_white", "yard_cool"])
for k_ in range(8):
    az = 2 * math.pi * k_ / 8
    rad = HF["bank"]["r"][0] + 12
    p = (rad * math.sin(az), -rad * math.cos(az), 0.3)
    add_light("bankglow_%d" % k_, "AREA", p, LH["bank_glow"], pal(BG[k_ % len(BG)]), aim=(p[0], p[1], 20), size=30.0,
              size_y=14.0, shadow=False, group="civic", receivers=mcol)

# beams: the corp's (rule-placed by hq_build) and the city's by azimuth (hq_kit)
BEAMS = list(HOOKS.get("beams", []))
BEAMS += CRING.beams_by_azimuth(ROOF, CITY, P, pal, LH["city_beam_k"])
for k_, (o, d, c, pw, cone) in enumerate(BEAMS):
    aim = Vector(o) + Vector(d).normalized() * 100.0
    add_light("beam_%d" % k_, "SPOT", o, pw * JOB.get("beam_k", 1.0), c, aim=aim, size=0.0, spot=cone, blend=0.15,
              shadow=False, group="beam", receivers=mcol)
log("lights", len(LIGHTS), "beams", len(BEAMS), "plumes", len(PLUME_K))


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
    kp = sstep(zoom, *LOD["plumes_on_at"])
    for vk in PLUME_K:
        vk.outputs[0].default_value = kp
    ksig = sstep(zoom, *LOD["signage_on_at"])
    ksm = sstep(zoom, *LOD["small_lights_on_at"])
    st = fr.get("room_state", {})
    pw = fr.get("power")
    keep = set(pw["keep"]) if pw else set()
    cut = pw["k"] if pw else 1.0
    boost = pw.get("boost", 1.45) if pw else 1.0
    base = {"sign": ksig * 0.85 + 0.15, "city_sign": ksig, "small": 0.25 + 0.75 * ksm, "city_small": 0.3 + 0.7 * ksm}
    base.update({k: f(zoom) for k, f in HOOKS.get("lod_weights", {}).items()})
    for name, ob in OBJ.items():
        if ob is None or not ob.data.materials or ob.data.materials[0] not in (M_EMIT, M_CITY, M_CEMIT):
            continue
        k = base.get(name, 1.0)
        if name.startswith("room_"):
            i = name[5:]
            k = STATE_K.get(st.get(i, "reach"), 0.3)
            if pw and i in keep:
                k *= boost
            elif pw:
                k *= cut
        elif pw and not name.startswith(tuple(HOOKS.get("no_cut", ()))):
            k *= cut
        set_pwo(ob, k)
    # movers: every object and light of a mover follows its origin
    for name, loc in (fr.get("movers") or {}).items():
        mv = MOVERS.get(name)
        if not mv:
            continue
        for ob in mv["objs"]:
            ob.location = loc
        for lob, l0 in mv["lights"]:
            lob.location = (l0[0] + loc[0], l0[1] + loc[1], l0[2] + loc[2])
    for (lob, e0, grp) in LIGHTS:
        if grp.startswith("room:"):
            i = grp[5:]
            s = st.get(i, "target" if i == "srv" else "reach")
            tc = TYPE_COL[G.KIND[i]] if G.KIND[i] in TYPE_COL else (1, 1, 1)
            c = tuple(0.55 * a + 0.45 for a in tc)
            kk = STATE_K.get(s, 0.3) * LH["room_k"]
            if pw:
                kk *= boost if i in keep else cut
            lob.data.color = c[:3]
            lob.data.energy = e0 * kk
        elif grp in ("civic", "city", "start", "corp") and pw:
            lob.data.energy = e0 * cut
        elif grp in ("civic", "city", "start", "corp"):
            lob.data.energy = e0
    if "apply" in HOOKS:
        HOOKS["apply"](fr, dict(OBJ=OBJ, LIGHTS=LIGHTS, set_pwo=set_pwo, cut=cut if pw else 1.0, keep=keep, zoom=zoom))


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
cy.device = "GPU" if (not EEVEE and gpu_setup()) else "CPU"
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


if EEVEE:
    # layout previews only (the GPU queue allows short Eevee previews without the lock): no light linking guarantee,
    # no object index; the post copes with the missing passes
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue
    ee = scene.eevee
    for k_, v_ in (("taa_render_samples", int(JOB.get("samples", 16))), ("volumetric_start", 1.0),
                   ("volumetric_end", 2500.0), ("volumetric_tile_size", "4"), ("volumetric_samples", 48),
                   ("use_volumetric_shadows", False), ("use_shadows", True), ("use_raytracing", False)):
        try:
            setattr(ee, k_, v_)
        except (AttributeError, TypeError):
            pass
    vl.use_pass_object_index = False

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
                                             "Volume Direct": "voldir", "Volume Light": "voldir"})
    os.remove(stem + ".exr")
    log("frame", fr["name"], "%.1f s" % (time.time() - t1), "passes", found if fr is JOB["frames"][0] else "")
log("done")
# OCC_V3
