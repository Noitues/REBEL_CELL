"""Solace THE BLOOM v2, direction A "Necrosis" as a WORLD material (Blender shader node groups, Cycles).

exec'd inside the street_r2 scene copy (r2_build.section and r2_cycles). Two node groups:
  BL_FIELD   (no inputs)  uses the shading point's world position; outputs Cover, Vein, Edge, Hatch (floats 0..1)
  BL_SHADER  (Shader in)  Original shader mixed with the Bloom shader by Cover; windows below the front keep 10 % of their light
Everything is a function of world position (x along the street, y across, z up), so the skin follows every facade, kerb and
roof; veins are the cell borders of a distorted 3D Voronoi, so they follow the surface; the hatch is a 45 degree world pattern.
Config (BLOOM_CFG json): front_x (world x of the front on the ground), seed, boxes (keep-out AABBs: route rooms + links),
tend, veins, edge, body, plum, pink. No randomness at render time.
"""
import json
import math
import os

import bpy

CFG = None


def set_cfg(c):
    global CFG
    CFG = c
_GROUPS = {}


class _B:
    def __init__(self, nt):
        self.nt = nt

    def n(self, t, **kw):
        n = self.nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def val(self, sock, v):
        if isinstance(v, (int, float)):
            sock.default_value = v
        else:
            self.link(v, sock)

    def m(self, op, a, b=None, c=None):
        n = self.n("ShaderNodeMath", operation=op)
        self.val(n.inputs[0], a)
        if b is not None:
            self.val(n.inputs[1], b)
        if c is not None:
            self.val(n.inputs[2], c)
        return n.outputs[0]

    def smooth(self, v, a, b):
        mr = self.n("ShaderNodeMapRange")
        mr.interpolation_type = "SMOOTHSTEP"
        self.val(mr.inputs["From Min"], a)
        self.val(mr.inputs["From Max"], b)
        self.val(mr.inputs["Value"], v)
        return mr.outputs[0]

    def comb(self, x, y, z):
        n = self.n("ShaderNodeCombineXYZ")
        self.val(n.inputs[0], x)
        self.val(n.inputs[1], y)
        self.val(n.inputs[2], z)
        return n.outputs[0]

    def noise(self, vec, scale=1.0, detail=3.0, w=0.0):
        n = self.n("ShaderNodeTexNoise", noise_dimensions="4D")
        self.link(vec, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["W"].default_value = w
        return n.outputs["Fac"]

    def vmul(self, vec, k):
        n = self.n("ShaderNodeVectorMath", operation="MULTIPLY")
        self.link(vec, n.inputs[0])
        n.inputs[1].default_value = (k, k, k) if isinstance(k, (int, float)) else k
        return n.outputs[0]


def _box_mask(b, X, Y, Z, bx):
    """1 inside the AABB (x0, x1, y0, y1, z0, z1)."""
    x0, x1, y0, y1, z0, z1 = bx
    t = None
    for v, lo, hi in ((X, x0, x1), (Y, y0, y1), (Z, z0, z1)):
        a = b.m("MULTIPLY", b.m("GREATER_THAN", v, lo), b.m("LESS_THAN", v, hi))
        t = a if t is None else b.m("MULTIPLY", t, a)
    return t


def build_field():
    ng = bpy.data.node_groups.new("BL_FIELD", "ShaderNodeTree")
    for nm in ("Cover", "Vein", "Edge", "Hatch"):
        ng.interface.new_socket(nm, in_out="OUTPUT", socket_type="NodeSocketFloat")
    b = _B(ng)
    out = b.n("NodeGroupOutput")
    geo = b.n("ShaderNodeNewGeometry")
    sep = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Position"], sep.inputs[0])
    X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    sd = float(CFG.get("seed", 7))
    ax = CFG.get("axis", "x")
    sgn = float(CFG.get("sgn", 1.0))
    AX = {"x": X, "y": Y, "z": Z}
    others = {"x": (Z, Y), "y": (Z, X), "z": (X, Y)}[ax]
    C = b.m("MULTIPLY", AX[ax], sgn)                                   # the route coordinate (infected where C > front)
    zk = float(CFG.get("zk", 1.1))
    fn = b.noise(b.comb(b.m("MULTIPLY", others[0], 0.5), b.m("MULTIPLY", others[1], 0.08), b.m("MULTIPLY", AX[ax], 0.05)), 1.0, 3.0, sd)
    fn2 = b.noise(b.comb(b.m("MULTIPLY", others[0], 1.7), b.m("MULTIPLY", AX[ax] if ax != "x" else X, 0.05), 0.0), 1.0, 2.0, sd + 5)
    fing = b.m("ADD", b.m("MULTIPLY", b.m("SUBTRACT", fn, 0.35), float(CFG.get("fing", 7.5))), b.m("MULTIPLY", b.m("SUBTRACT", fn2, 0.5), 3.5))
    tn = b.noise(b.comb(b.m("MULTIPLY", Y, 0.35), b.m("MULTIPLY", Z, 0.9), b.m("MULTIPLY", X, 0.12)), 1.0, 3.0, sd + 3)
    tend = b.m("MULTIPLY", b.m("MULTIPLY", b.smooth(tn, 0.42, 0.58), float(CFG["tend"])),
               b.m("SUBTRACT", 1.0, b.smooth(Z, 0.4, float(CFG["tend_h"]))))
    zc = b.m("MINIMUM", b.m("MAXIMUM", Z, 0.0), 14.0)
    local = b.m("SUBTRACT", b.m("SUBTRACT", b.m("ADD", float(CFG["front_c"]), b.m("MULTIPLY", zc, zk)), fing), tend)
    d = b.m("SUBTRACT", C, local)                                   # BU behind the front (positive = infected)
    cover = b.smooth(d, -0.05, 0.15)
    tide = CFG.get("tide")
    if tide:                                                          # walls flood to a tide line that rises with the depth behind the front
        th = b.m("MINIMUM", b.m("ADD", float(tide[0]), b.m("MULTIPLY", b.m("MAXIMUM", d, 0.0), float(tide[1]))), float(tide[2]))
        cover = b.m("MULTIPLY", cover, b.m("SUBTRACT", 1.0, b.smooth(Z, b.m("SUBTRACT", th, 4.0), th)))
    rad = CFG.get("rad")
    if rad:                                                          # a radial mask: the Bloom belongs to the garden's neighbourhood only
        dist = b.m("SQRT", b.m("ADD", b.m("POWER", b.m("SUBTRACT", X, float(rad[0])), 2.0), b.m("POWER", b.m("SUBTRACT", Y, float(rad[1])), 2.0)))
        cover = b.m("MULTIPLY", cover, b.m("SUBTRACT", 1.0, b.smooth(dist, float(rad[2]), float(rad[3]))))
    # keep-out: route rooms (opening, jamb, frame ring + 10 %) and the links (+ margin): the Bloom is masked to zero inside
    keep = 0.0
    for bx in CFG["boxes"]:
        keep = b.m("MAXIMUM", keep, _box_mask(b, X, Y, Z, bx))
    cover = b.m("MULTIPLY", cover, b.m("SUBTRACT", 1.0, keep))
    # veins: borders of a domain-warped 3D Voronoi (cracked necrotic skin), two scales, density-masked, sparse near the front
    pos = geo.outputs["Position"]
    warp = b.vmul(b.noise(b.vmul(pos, 0.35), 1.0, 2.0, sd + 9), 1.1)
    wpos = b.n("ShaderNodeVectorMath", operation="ADD")
    b.link(pos, wpos.inputs[0])
    b.link(warp, wpos.inputs[1])
    vs = []
    for k, (sc, w, wt) in enumerate(((float(CFG["vscale"]), float(CFG["vw"]), 1.0), (float(CFG["vscale"]) * 2.1, float(CFG["vw"]) * 1.7, 0.7))):
        vo = b.n("ShaderNodeTexVoronoi", voronoi_dimensions="3D", feature="DISTANCE_TO_EDGE")
        b.link(wpos.outputs[0], vo.inputs["Vector"])
        vo.inputs["Scale"].default_value = sc
        vo.inputs["Randomness"].default_value = 1.0
        line = b.m("SUBTRACT", 1.0, b.smooth(vo.outputs["Distance"], 0.0, w))
        dens = b.smooth(b.noise(b.vmul(pos, 0.12 + 0.05 * k), 1.0, 2.0, sd + 20 + k), 0.46, 0.64)
        vs.append(b.m("MULTIPLY", b.m("MULTIPLY", line, dens), wt))
    vein = b.m("MAXIMUM", vs[0], vs[1])
    vein = b.m("MULTIPLY", vein, b.m("ADD", 0.45, b.m("MULTIPLY", b.smooth(d, 0.0, 9.0), 0.55)))
    # the hairline hot front edge (a thin band at d = 0, inside the cover's keep-out mask)
    edge = b.m("SUBTRACT", 1.0, b.smooth(b.m("ABSOLUTE", b.m("SUBTRACT", d, 0.03)), 0.0, float(CFG["ew"])))
    edge = b.m("MULTIPLY", edge, b.m("SUBTRACT", 1.0, keep))
    # 45 degree world hatch (x + z diagonal on facades, x + y on the ground), fading in behind the front
    diag = b.m("ADD", b.m("ADD", X, Z), b.m("MULTIPLY", Y, 0.25))
    fr = b.m("FRACT", b.m("MULTIPLY", diag, float(CFG["hatch_k"])))
    hatch = b.m("MULTIPLY", b.m("LESS_THAN", fr, 0.22), b.smooth(d, 0.0, 3.0))
    for nm, v in (("Cover", cover), ("Vein", vein), ("Edge", edge), ("Hatch", hatch)):
        b.link(v, out.inputs[nm])
    return ng


def build_shader():
    ng = bpy.data.node_groups.new("BL_SHADER", "ShaderNodeTree")
    ng.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    ng.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    b = _B(ng)
    gi = b.n("NodeGroupInput")
    go = b.n("NodeGroupOutput")
    fld = b.n("ShaderNodeGroup")
    fld.node_tree = _GROUPS["field"]
    diff = b.n("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = tuple(CFG["plum"]) + (1,)
    diff.inputs["Roughness"].default_value = 0.7
    em = b.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(CFG["pink"]) + (1,)
    k = b.m("ADD", b.m("ADD", b.m("MULTIPLY", fld.outputs["Vein"], float(CFG["veins"])),
                       b.m("MULTIPLY", fld.outputs["Edge"], float(CFG["edge"]))), b.m("MULTIPLY", fld.outputs["Hatch"], float(CFG["hatch"])))
    b.link(k, em.inputs["Strength"])
    add = b.n("ShaderNodeAddShader")
    b.link(diff.outputs[0], add.inputs[0])
    b.link(em.outputs[0], add.inputs[1])
    mix = b.n("ShaderNodeMixShader")
    b.link(b.m("MULTIPLY", fld.outputs["Cover"], float(CFG["cover_k"])), mix.inputs["Fac"])
    b.link(gi.outputs[0], mix.inputs[1])
    ret = b.n("ShaderNodeMixShader")
    ret.inputs[0].default_value = float(CFG.get("retain", 0.08))
    b.link(add.outputs[0], ret.inputs[1])
    b.link(gi.outputs[0], ret.inputs[2])
    b.link(ret.outputs[0], mix.inputs[2])
    b.link(mix.outputs[0], go.inputs[0])
    return ng


def ensure():
    if "field" not in _GROUPS:
        _GROUPS["field"] = build_field()
        _GROUPS["shader"] = build_shader()


SKIP = ("route", "bl_", "sky", "oc_")


def inject(mat, src):
    """Return the socket that replaces `src` (the material's surface source): the Bloom group wrapped round it."""
    if CFG is None or mat is None or mat.node_tree is None or mat.get("bl_on") or mat.name.startswith(SKIP):
        return src
    ensure()
    nt = mat.node_tree
    g = nt.nodes.new("ShaderNodeGroup")
    g.node_tree = _GROUPS["shader"]
    nt.links.new(src, g.inputs[0])
    mat["bl_on"] = True
    return g.outputs[0]


def sweep():
    """Materials that never went through section() (the ground): wrap their surface output."""
    if CFG is None:
        return 0
    n = 0
    for m in bpy.data.materials:
        if m.node_tree is None or m.get("bl_on") or m.name.startswith(SKIP):
            continue
        out = next((x for x in m.node_tree.nodes if x.type == "OUTPUT_MATERIAL"), None)
        if out is None or not out.inputs["Surface"].links:
            continue
        s = out.inputs["Surface"].links[0].from_socket
        m.node_tree.links.new(inject(m, s), out.inputs["Surface"])
        n += 1
    return n
