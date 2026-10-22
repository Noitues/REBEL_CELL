"""Solace THE BLOOM v2, A Necrosis on the district RAID map as a world material (Eevee cel; exec'd by sd_main.py, map mode).

Blocks overgrown by the material: every cel material is wrapped by BL_RAID. The infection field is a function of the world
position: ground floods where the (noise-warped) distance from the two DEFENDED home-server nodes (helix plaza r 46 BU at the
origin, hospital Site r 42 at (108, -60)) passes a threshold; a lot (24 BU grid, one white-noise value per lot) is overgrown when
its own field passes the same threshold, up to a tide line that rises with the field value. Defended nodes are never recoloured.
The body keeps the cel shading (diffuse -> ShaderToRGB -> constant ramp); veins are Voronoi cell borders, the hatch is a
45 degree world pattern. The threshold `th` comes from the infection percent by calibration renders (bloom3d_raid.py driver).
Env: BLOOM_CFG (json), BLOOM_CAL=1 renders the calibration mask (R = cover, G = defended, B = geometry) instead of the map.
"""
import json
import math
import os

import bpy

_RC = json.load(open(os.environ["BLOOM_CFG"])) if os.environ.get("BLOOM_CFG") else None
_RG = {}


class _RB:
    def __init__(self, nt):
        self.nt = nt

    def n(self, t, **kw):
        n = self.nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def val(self, s, v):
        if isinstance(v, (int, float)):
            s.default_value = v
        else:
            self.link(v, s)

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

    def sel(self, c, a, b):
        """c ? a : b (c is 0 / 1)."""
        return self.m("ADD", self.m("MULTIPLY", c, a), self.m("MULTIPLY", self.m("SUBTRACT", 1.0, c), b))


def _field():
    ng = bpy.data.node_groups.new("BL_RAID_FIELD", "ShaderNodeTree")
    for nm in ("Cover", "Vein", "Edge", "Hatch", "Prot", "Depth"):
        ng.interface.new_socket(nm, in_out="OUTPUT", socket_type="NodeSocketFloat")
    b = _RB(ng)
    out = b.n("NodeGroupOutput")
    geo = b.n("ShaderNodeNewGeometry")
    sp = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Position"], sp.inputs[0])
    X, Y, Z = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
    sd = float(_RC.get("seed", 3))
    th = float(_RC["th"])

    def warp(x, y, w):
        n1 = b.noise(b.comb(b.m("MULTIPLY", x, 0.010), b.m("MULTIPLY", y, 0.010), 0.0), 1.0, 3.0, sd + w)
        n2 = b.noise(b.comb(b.m("MULTIPLY", x, 0.040), b.m("MULTIPLY", y, 0.040), 0.0), 1.0, 2.0, sd + 2 + w)
        return b.m("ADD", b.m("MULTIPLY", b.m("SUBTRACT", n1, 0.5), 60.0), b.m("MULTIPLY", b.m("SUBTRACT", n2, 0.5), 18.0))

    def dist_def(x, y):
        dd = None
        for (cx, cy), r in _RC["defended"]:
            q = b.m("SUBTRACT", b.m("SQRT", b.m("ADD", b.m("POWER", b.m("SUBTRACT", x, cx), 2.0), b.m("POWER", b.m("SUBTRACT", y, cy), 2.0))), r)
            dd = q if dd is None else b.m("MINIMUM", dd, q)
        return dd
    Fg = b.m("ADD", dist_def(X, Y), warp(X, Y, 0))
    li, lj = b.m("FLOOR", b.m("ADD", b.m("MULTIPLY", X, 1 / 24.0), 0.5)), b.m("FLOOR", b.m("ADD", b.m("MULTIPLY", Y, 1 / 24.0), 0.5))
    lcx, lcy = b.m("MULTIPLY", li, 24.0), b.m("MULTIPLY", lj, 24.0)
    wn = b.n("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
    b.link(b.comb(b.m("ADD", li, 50.0), b.m("ADD", lj, 50.0), sd), wn.inputs["Vector"])
    Fl = b.m("ADD", b.m("ADD", dist_def(lcx, lcy), warp(lcx, lcy, 0)), b.m("MULTIPLY", b.m("SUBTRACT", wn.outputs["Value"], 0.5), 30.0))
    ground = b.m("LESS_THAN", Z, 0.6)
    lvl_g, lvl_l = b.m("SUBTRACT", Fg, th), b.m("SUBTRACT", Fl, th)
    zc = b.m("ADD", b.m("ADD", b.m("MULTIPLY", b.m("MAXIMUM", lvl_l, 0.0), 0.9), 14.0),
             b.m("MULTIPLY", b.m("SUBTRACT", b.noise(b.comb(b.m("MULTIPLY", b.m("ADD", X, Y), 0.05), b.m("MULTIPLY", Z, 0.1), 0.0), 1.0, 3.0, sd + 4), 0.5), 6.0))
    d_wall = b.sel(b.m("GREATER_THAN", lvl_l, 0.0), b.m("SUBTRACT", zc, Z), -5.0)
    d = b.sel(ground, lvl_g, d_wall)
    prot = 0.0
    for (cx, cy), r in _RC["defended"]:
        dist = b.m("SQRT", b.m("ADD", b.m("POWER", b.m("SUBTRACT", X, cx), 2.0), b.m("POWER", b.m("SUBTRACT", Y, cy), 2.0)))
        prot = b.m("MAXIMUM", prot, b.smooth(b.m("SUBTRACT", 0.0, dist), -(r + 4.0), -(r - 4.0)))
    cover = b.m("MULTIPLY", b.smooth(d, -0.05, 0.4), b.m("SUBTRACT", 1.0, prot))
    pos = geo.outputs["Position"]
    wv = b.n("ShaderNodeVectorMath", operation="ADD")
    b.link(pos, wv.inputs[0])
    wn3 = b.n("ShaderNodeVectorMath", operation="MULTIPLY")
    b.link(b.n("ShaderNodeTexNoise", noise_dimensions="3D").outputs["Color"], wn3.inputs[0]) if False else None
    nz = b.n("ShaderNodeTexNoise", noise_dimensions="3D")
    nz.inputs["Scale"].default_value = 0.09
    nz.inputs["Detail"].default_value = 2.0
    b.link(pos, nz.inputs["Vector"])
    wv.inputs[1].default_value = (0, 0, 0)
    sc = b.n("ShaderNodeVectorMath", operation="SCALE")
    b.link(nz.outputs["Color"], sc.inputs[0])
    sc.inputs["Scale"].default_value = 6.0
    b.link(sc.outputs[0], wv.inputs[1])
    vs = []
    for k, (s_, w_, wt) in enumerate(((float(_RC["vscale"]), float(_RC["vw"]), 1.0), (float(_RC["vscale"]) * 2.2, float(_RC["vw"]) * 1.7, 0.7))):
        vo = b.n("ShaderNodeTexVoronoi", voronoi_dimensions="3D", feature="DISTANCE_TO_EDGE")
        b.link(wv.outputs[0], vo.inputs["Vector"])
        vo.inputs["Scale"].default_value = s_
        line = b.m("SUBTRACT", 1.0, b.smooth(vo.outputs["Distance"], 0.0, w_))
        dens = b.smooth(b.noise(b.m("MULTIPLY", b.comb(X, Y, Z), 0.0) if False else pos, 0.05 + 0.02 * k, 2.0, sd + 20 + k), 0.40, 0.58)
        vs.append(b.m("MULTIPLY", b.m("MULTIPLY", line, dens), wt))
    vein = b.m("MULTIPLY", b.m("MAXIMUM", vs[0], vs[1]), b.m("ADD", 0.5, b.m("MULTIPLY", b.smooth(d, 0.0, 12.0), 0.5)))
    edge = b.m("MULTIPLY", b.m("SUBTRACT", 1.0, b.smooth(b.m("ABSOLUTE", b.m("SUBTRACT", d, 0.1)), 0.0, float(_RC["ew"]))), b.m("SUBTRACT", 1.0, prot))
    fr = b.m("FRACT", b.m("MULTIPLY", b.m("ADD", b.m("ADD", X, Y), b.m("MULTIPLY", Z, 0.7)), float(_RC["hatch_k"])))
    hatch = b.m("MULTIPLY", b.m("LESS_THAN", fr, 0.25), b.smooth(d, 0.0, 4.0))
    for nm, v in (("Cover", cover), ("Vein", vein), ("Edge", edge), ("Hatch", hatch), ("Prot", prot), ("Depth", d)):
        b.link(v, out.inputs[nm])
    return ng


def _shader():
    ng = bpy.data.node_groups.new("BL_RAID", "ShaderNodeTree")
    ng.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    ng.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    b = _RB(ng)
    gi, go = b.n("NodeGroupInput"), b.n("NodeGroupOutput")
    f = b.n("ShaderNodeGroup")
    f.node_tree = _RG["field"]
    # cel-shaded plum body: diffuse -> ShaderToRGB -> constant 3 band ramp -> x plum
    dif = b.n("ShaderNodeBsdfDiffuse")
    dif.inputs[0].default_value = (1, 1, 1, 1)
    s2 = b.n("ShaderNodeShaderToRGB")
    b.link(dif.outputs[0], s2.inputs[0])
    bw = b.n("ShaderNodeRGBToBW")
    b.link(s2.outputs[0], bw.inputs[0])
    rp = b.n("ShaderNodeValToRGB")
    rp.color_ramp.interpolation = "CONSTANT"
    el = rp.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0.35, 0.35, 0.35, 1)
    el[1].position, el[1].color = 0.20, (0.62, 0.62, 0.62, 1)
    e3 = el.new(0.50)
    e3.color = (1.0, 1.0, 1.0, 1)
    b.link(bw.outputs[0], rp.inputs[0])
    mulc = b.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    mulc.inputs[0].default_value = 1.0
    mulc.inputs[6].default_value = tuple(_RC["plum"]) + (1,)
    b.link(rp.outputs[0], mulc.inputs[7])
    body = b.n("ShaderNodeEmission")
    b.link(mulc.outputs[2], body.inputs[0])
    body.inputs[1].default_value = 1.0
    pk = b.n("ShaderNodeEmission")
    pk.inputs["Color"].default_value = tuple(_RC["pink"]) + (1,)
    k = b.m("ADD", b.m("ADD", b.m("MULTIPLY", f.outputs["Vein"], float(_RC["veins"])), b.m("MULTIPLY", f.outputs["Edge"], float(_RC["edge"]))),
            b.m("MULTIPLY", f.outputs["Hatch"], float(_RC["hatch"])))
    b.link(k, pk.inputs["Strength"])
    add = b.n("ShaderNodeAddShader")
    b.link(body.outputs[0], add.inputs[0])
    b.link(pk.outputs[0], add.inputs[1])
    mix = b.n("ShaderNodeMixShader")
    b.link(f.outputs["Cover"], mix.inputs["Fac"])
    b.link(gi.outputs[0], mix.inputs[1])
    b.link(add.outputs[0], mix.inputs[2])
    b.link(mix.outputs[0], go.inputs[0])
    return ng


def _cal_material():
    m = bpy.data.materials.new("bl_cal")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    b = _RB(nt)
    out = b.n("ShaderNodeOutputMaterial")
    f = b.n("ShaderNodeGroup")
    f.node_tree = _RG["field"]
    em = b.n("ShaderNodeEmission")
    b.link(b.comb(f.outputs["Cover"], f.outputs["Prot"], 1.0), em.inputs["Color"])
    b.link(em.outputs[0], out.inputs[0])
    return m


def apply():
    if _RC is None:
        return
    _RG["field"] = _field()
    _RG["shader"] = _shader()
    n = 0
    for mat in bpy.data.materials:
        if mat.node_tree is None or mat.get("bl_on") or mat.name.startswith("bl_"):
            continue
        out = next((x for x in mat.node_tree.nodes if x.type == "OUTPUT_MATERIAL"), None)
        if out is None or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        g = mat.node_tree.nodes.new("ShaderNodeGroup")
        g.node_tree = _RG["shader"]
        mat.node_tree.links.new(src, g.inputs[0])
        mat.node_tree.links.new(g.outputs[0], out.inputs["Surface"])
        mat["bl_on"] = True
        n += 1
    print("BLOOM raid wrapped", n, flush=True)
    if os.environ.get("BLOOM_CAL") == "1":
        bpy.context.view_layer.material_override = _cal_material()
        scene.view_settings.view_transform = "Raw"        # noqa: F821  (sd_main globals)


apply()
