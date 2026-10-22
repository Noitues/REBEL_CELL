"""Solace THE BLOOM v2, A Necrosis on the HQ helix in TUBE coordinates (Blender node groups, Cycles). exec'd by hq_scene.py.

The strand skin mesh carries a per-vertex attribute `tube` = (z, phi, tower) written by hq_build (the same coordinates as
hq_graph.tube_pt). The skin shader reads it, so the front, the tongues and the veins are functions of (z, phi) on the strand
and run along the twist; phi is periodic (cos / sin), so there is no seam. One front height serves BOTH strands.
Windows below the front die: the shared emission material (frame rings, office lamps, floor rings, rungs) is wrapped so that,
on the helix (axis radius < 30, above the plinth), the light below the front fades to a dim pink; route-room emission
(object index 5) is never touched. JOB["bloom"] = {z_front, seed, veins, edge, hatch, ...}.
"""
import math

import bpy

BL = JOB.get("bloom")            # noqa: F821  (hq_scene globals)
_HG = {}


class _HB:
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


def _tube_field():
    ng = bpy.data.node_groups.new("BL_TUBE_FIELD", "ShaderNodeTree")
    for nm in ("Cover", "Vein", "Edge", "Hatch", "Depth", "Ahead"):
        ng.interface.new_socket(nm, in_out="OUTPUT", socket_type="NodeSocketFloat")
    b = _HB(ng)
    out = b.n("NodeGroupOutput")
    at = b.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="tube")
    sp = b.n("ShaderNodeSeparateXYZ")
    b.link(at.outputs["Vector"], sp.inputs[0])
    Z, PHI, TW = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
    sd = float(BL.get("seed", 7))
    RT = float(BL.get("tube_r", 10.0))
    cphi, sphi = b.m("COSINE", PHI), b.m("SINE", PHI)
    ph0 = b.m("MULTIPLY", TW, math.pi)
    # front height: a spiral swell + tongues that are functions of phi only (they run along the strand) + a ragged edge
    swell = b.m("MULTIPLY", b.m("COSINE", b.m("SUBTRACT", b.m("SUBTRACT", PHI, ph0), 0.6)), float(BL.get("swell", 4.5)))
    tg = b.noise(b.comb(b.m("ADD", b.m("MULTIPLY", cphi, 2.2), b.m("MULTIPLY", TW, 17.0)), b.m("MULTIPLY", sphi, 2.2), 3.0), 1.0, 3.0, sd)
    tongue = b.m("MULTIPLY", b.smooth(tg, 0.42, 0.72), float(BL.get("tongue", 17.0)))
    rg = b.noise(b.comb(b.m("MULTIPLY", Z, 0.45), b.m("ADD", b.m("MULTIPLY", cphi, 3.0), TW), b.m("MULTIPLY", sphi, 3.0)), 1.0, 3.0, sd + 4)
    ragged = b.m("MULTIPLY", b.m("SUBTRACT", rg, 0.5), 2.2 * 2.0)
    zf = b.m("ADD", b.m("ADD", b.m("ADD", float(BL["z_front"]), swell), tongue), ragged)
    d = b.m("SUBTRACT", zf, Z)                                      # BU below the local front (positive = infected)
    cover = b.smooth(d, -0.2, 0.6)
    # keep-out: the UP stair band (solid strip between the two windows) keeps the skin clean; the windows are holes in the mesh
    for ti, sp_phi in enumerate((float(BL["stair_phi_A"]), float(BL["stair_phi_B"]))):
        dph = b.m("ABSOLUTE", b.m("SUBTRACT", b.m("MODULO", b.m("ADD", b.m("SUBTRACT", PHI, sp_phi), math.pi), 2 * math.pi), math.pi))
        k = b.m("MULTIPLY", b.m("LESS_THAN", dph, 2.3 / RT), b.m("LESS_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", TW, float(ti))), 0.5))
        cover = b.m("MULTIPLY", cover, b.m("SUBTRACT", 1.0, k))
    # veins: cell borders of a Voronoi on the tube cylinder, stretched along the strand (z * 0.3): they run with the twist
    def cyl(zk, off):
        return b.comb(b.m("ADD", b.m("MULTIPLY", cphi, RT), b.m("MULTIPLY", TW, 31.0 + off)), b.m("MULTIPLY", sphi, RT), b.m("MULTIPLY", Z, zk))
    vs = []
    for k, (sc, w, wt, zk) in enumerate(((float(BL["vscale"]), float(BL["vw"]), 1.0, 0.30), (float(BL["vscale"]) * 2.0, float(BL["vw"]) * 1.7, 0.7, 0.4))):
        vo = b.n("ShaderNodeTexVoronoi", voronoi_dimensions="3D", feature="DISTANCE_TO_EDGE")
        b.link(cyl(zk, 3 * k), vo.inputs["Vector"])
        vo.inputs["Scale"].default_value = sc
        line = b.m("SUBTRACT", 1.0, b.smooth(vo.outputs["Distance"], 0.0, w))
        dens = b.smooth(b.noise(b.comb(b.m("MULTIPLY", cphi, 2.0), b.m("MULTIPLY", sphi, 2.0), b.m("MULTIPLY", Z, 0.02 + 0.01 * k)), 1.0, 2.0, sd + 20 + k), 0.38, 0.55)
        vs.append(b.m("MULTIPLY", b.m("MULTIPLY", line, dens), wt))
    vein = b.m("MULTIPLY", b.m("MAXIMUM", vs[0], vs[1]), b.m("ADD", 0.5, b.m("MULTIPLY", b.smooth(d, 0.0, 25.0), 0.5)))
    edge = b.m("SUBTRACT", 1.0, b.smooth(b.m("ABSOLUTE", b.m("SUBTRACT", d, 0.1)), 0.0, float(BL["ew"])))
    edge = b.m("MULTIPLY", edge, b.m("GREATER_THAN", cover, 0.02))
    fr = b.m("FRACT", b.m("MULTIPLY", b.m("ADD", b.m("MULTIPLY", PHI, RT), Z), float(BL["hatch_k"])))
    hatch = b.m("MULTIPLY", b.m("LESS_THAN", fr, 0.22), b.smooth(d, 0.0, 6.0))
    # fingers: thin veins that crawl out ahead of the front over the clean skin (d < 0), gated by a slow noise along the strand
    fing = b.smooth(b.noise(b.comb(b.m("MULTIPLY", cphi, 3.0), b.m("MULTIPLY", sphi, 3.0), b.m("MULTIPLY", Z, 0.03)), 1.0, 2.0, sd + 40), 0.45, 0.62)
    ahead = b.m("MULTIPLY", b.m("MULTIPLY", vs[0], fing), b.m("MULTIPLY", b.smooth(d, -float(BL.get("reach", 40.0)), -1.0), b.m("SUBTRACT", 1.0, cover)))
    for nm, v in (("Cover", cover), ("Vein", vein), ("Edge", edge), ("Hatch", hatch), ("Depth", d), ("Ahead", ahead)):
        b.link(v, out.inputs[nm])
    return ng


def _tube_shader():
    ng = bpy.data.node_groups.new("BL_TUBE_SHADER", "ShaderNodeTree")
    ng.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    ng.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    b = _HB(ng)
    gi, go = b.n("NodeGroupInput"), b.n("NodeGroupOutput")
    fld = b.n("ShaderNodeGroup")
    fld.node_tree = _HG["field"]
    diff = b.n("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = tuple(BL["plum"]) + (1,)
    diff.inputs["Roughness"].default_value = 0.7
    em = b.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(BL["pink"]) + (1,)
    k = b.m("ADD", b.m("ADD", b.m("MULTIPLY", fld.outputs["Vein"], float(BL["veins"])), b.m("MULTIPLY", fld.outputs["Edge"], float(BL["edge"]))),
            b.m("MULTIPLY", fld.outputs["Hatch"], float(BL["hatch"])))
    b.link(k, em.inputs["Strength"])
    add = b.n("ShaderNodeAddShader")
    b.link(diff.outputs[0], add.inputs[0])
    b.link(em.outputs[0], add.inputs[1])
    mix = b.n("ShaderNodeMixShader")
    b.link(b.m("MULTIPLY", fld.outputs["Cover"], float(BL["cover_k"])), mix.inputs["Fac"])
    b.link(gi.outputs[0], mix.inputs[1])
    b.link(add.outputs[0], mix.inputs[2])
    pa = b.n("ShaderNodeEmission")
    pa.inputs["Color"].default_value = tuple(BL["pink"]) + (1,)
    b.link(b.m("MULTIPLY", fld.outputs["Ahead"], float(BL.get("ahead", 0.9))), pa.inputs["Strength"])
    add2 = b.n("ShaderNodeAddShader")
    b.link(mix.outputs[0], add2.inputs[0])
    b.link(pa.outputs[0], add2.inputs[1])
    b.link(add2.outputs[0], go.inputs[0])
    return ng


def _win_dim():
    """Shared emission wrapped: on the helix below the front the light fades to dim pink; route rooms (index 5) untouched."""
    ng = bpy.data.node_groups.new("BL_WINDIM", "ShaderNodeTree")
    ng.interface.new_socket("Shader", in_out="INPUT", socket_type="NodeSocketShader")
    ng.interface.new_socket("Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    b = _HB(ng)
    gi, go = b.n("NodeGroupInput"), b.n("NodeGroupOutput")
    geo = b.n("ShaderNodeNewGeometry")
    sp = b.n("ShaderNodeSeparateXYZ")
    b.link(geo.outputs["Position"], sp.inputs[0])
    X, Y, Z = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
    rad = b.m("SQRT", b.m("ADD", b.m("MULTIPLY", X, X), b.m("MULTIPLY", Y, Y)))
    on_helix = b.m("MULTIPLY", b.m("LESS_THAN", rad, float(BL.get("win_r", 30.0))), b.m("GREATER_THAN", Z, float(BL["podium"]) + 2.0))
    oi = b.n("ShaderNodeObjectInfo")
    not_room = b.m("GREATER_THAN", b.m("ABSOLUTE", b.m("SUBTRACT", oi.outputs["Object Index"], 5.0)), 0.5)
    # azimuth-dependent front, the same swell as the skin (A and B are 180 degrees apart, so one swell serves the helix)
    az = b.m("ARCTAN2", Y, X)
    zf = b.m("ADD", b.m("ADD", float(BL["z_front"]), b.m("MULTIPLY", b.m("COSINE", b.m("SUBTRACT", az, 0.6)), float(BL.get("swell", 4.5)))), float(BL.get("win_bias", 0.0)))
    below = b.smooth(b.m("SUBTRACT", zf, Z), -0.2, 0.8)
    fac = b.m("MULTIPLY", b.m("MULTIPLY", on_helix, not_room), below)
    em = b.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(BL["pink"]) + (1,)
    em.inputs["Strength"].default_value = float(BL.get("win_dim", 0.10))
    mix = b.n("ShaderNodeMixShader")
    b.link(fac, mix.inputs["Fac"])
    b.link(gi.outputs[0], mix.inputs[1])
    b.link(em.outputs[0], mix.inputs[2])
    b.link(mix.outputs[0], go.inputs[0])
    return ng


def _wrap(mat, grp):
    nt = mat.node_tree
    out = next((x for x in nt.nodes if x.type == "OUTPUT_MATERIAL"), None)
    if out is None or not out.inputs["Surface"].links:
        return False
    src = out.inputs["Surface"].links[0].from_socket
    g = nt.nodes.new("ShaderNodeGroup")
    g.node_tree = grp
    nt.links.new(src, g.inputs[0])
    nt.links.new(g.outputs[0], out.inputs["Surface"])
    return True


def _wrap_front(mat, grp):
    """Skin only on the FRONT face: the back face is the office wall seen through the windows (keep it)."""
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == "MIX_SHADER" and n.inputs[0].links and n.inputs[0].links[0].from_socket.name == "Backfacing":
            src = n.inputs[1].links[0].from_socket
            g = nt.nodes.new("ShaderNodeGroup")
            g.node_tree = grp
            nt.links.new(src, g.inputs[0])
            nt.links.new(g.outputs[0], n.inputs[1])
            return True
    return False


def haze():
    """Faint pink spore haze just above the front: an emissive volume cylinder round the helix, a few floors tall, fading upward."""
    h = float(BL.get("haze_h", 0)) 
    if h <= 0:
        return
    import bmesh
    m = bpy.data.materials.new("bl_haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vs = nt.nodes.new("ShaderNodeVolumePrincipled")
    vs.inputs["Density"].default_value = 0.0
    b = _HB(nt)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    gz = sp.outputs["Z"]
    fade = b.m("POWER", b.m("SUBTRACT", 1.0, gz), 1.6)
    ramp_in = b.smooth(gz, 0.0, 0.08)
    nz = b.n("ShaderNodeTexNoise", noise_dimensions="3D")
    nz.inputs["Scale"].default_value = float(BL.get("haze_scale", 9.0))
    nz.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
    spec = b.smooth(nz.outputs["Fac"], 0.50, 0.66)
    gx, gy = sp.outputs["X"], sp.outputs["Y"]
    rr = b.m("SQRT", b.m("ADD", b.m("POWER", b.m("SUBTRACT", gx, 0.5), 2.0), b.m("POWER", b.m("SUBTRACT", gy, 0.5), 2.0)))
    radial = b.m("SUBTRACT", 1.0, b.smooth(rr, 0.10, 0.48))
    dens = b.m("MULTIPLY", b.m("MULTIPLY", b.m("MULTIPLY", fade, ramp_in), radial), b.m("ADD", 0.25, spec))
    nt.links.new(b.m("MULTIPLY", dens, float(BL.get("haze_k", 0.02))), vs.inputs["Density"])
    vs.inputs["Emission Color"].default_value = tuple(BL["pink"]) + (1,)
    nt.links.new(b.m("MULTIPLY", dens, float(BL.get("haze_em", 1.2))), vs.inputs["Emission Strength"])
    vs.inputs["Color"].default_value = tuple(BL["pink"]) + (1,)
    nt.links.new(vs.outputs[0], out.inputs["Volume"])
    me = bpy.data.meshes.new("bl_haze")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("bl_haze", me)
    R = float(BL.get("haze_r", 34.0))
    z0 = float(BL["z_front"]) - 2.0
    ob.location = (0.0, 0.0, z0 + h / 2)
    ob.scale = (2 * R, 2 * R, h)
    me.materials.append(m)
    bpy.context.scene.collection.objects.link(ob)
    ob.pass_index = 1
    ob.visible_shadow = False


def apply():
    if not BL:
        return
    _HG["field"] = _tube_field()
    _HG["shader"] = _tube_shader()
    _HG["win"] = _win_dim()
    done = []
    for t in ("A", "B"):
        ob = bpy.data.objects.get("strand_" + t)
        if ob and ob.data.materials and not ob.data.materials[0].get("bl_on"):
            m = ob.data.materials[0]
            if _wrap_front(m, _HG["shader"]):
                m["bl_on"] = True
                done.append(m.name)
    for m in set(o.data.materials[i] for o in bpy.data.objects if o.type == "MESH" for i in range(len(o.data.materials)) if o.data.materials[i]):
        pass
    for nm, mat in (("emit", M_EMIT),):         # noqa: F821  (hq_scene globals)
        if not mat.get("bl_on") and _wrap(mat, _HG["win"]):
            mat["bl_on"] = True
            done.append(mat.name)
    haze()
    print("BLOOM HQ wrapped", done, flush=True)


apply()
