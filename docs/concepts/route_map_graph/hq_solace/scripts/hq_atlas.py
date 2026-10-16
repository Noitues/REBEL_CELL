"""HQ Solace v4 option B: the interior-mapping ATLAS, rendered once from the hq_office kit.

Run inside Blender:  blender -b --factory-startup --python hq_atlas.py -- <out.png> [variants=6]
For each variant a flat-walled office room (the kit's two storeys: lower floor, mezzanine, upper floor, dropped
ceilings, core, conference rooms, cubicle rows, plants, people) is built once, then five orthographic slices are
rendered at 40 px / BU, TRUE ASPECT (no stretching):
    back wall  20.0 x 8.4 BU  (the last 2.5 BU of depth)      800 x 336
    left wall  10.5 x 8.4 BU  (the last 2.5 BU of the width)   420 x 336
    right wall                                                 420 x 336
    floor      20.0 x 10.5 BU (looking down, the lower storey) 800 x 420
    ceiling    20.0 x 10.5 BU (looking up, the dropped grid)   800 x 420
One atlas row (420 px) per variant, the five tiles side by side: x0 = 0, 800, 1220, 1640, 2440 (width 3240).
Constants are shared with the shader (hq_imap.py): HU 10, D 10.5, H 8.4.
"""
import math
import os
import random
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
if len(sys.argv) > 1 and sys.argv[1] == "assemble":      # system python: tiles -> one atlas (PIL)
    from PIL import Image
    d, out, nv = sys.argv[2], sys.argv[3], int(sys.argv[4])
    T = [("back", 0), ("left", 800), ("right", 1220), ("floor", 1640), ("ceil", 2440)]
    at = Image.new("RGB", (3240, 420 * nv), (0, 0, 0))
    for v in range(nv):
        for n, x0 in T:
            at.paste(Image.open(os.path.join(d, "_tile_%d_%s.png" % (v, n))).convert("RGB"), (x0, v * 420))
    at.save(out)
    print("atlas", out, at.size)
    sys.exit(0)
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import hq_office as OFC  # noqa: E402
OFC.PEOPLE = False

PX = 40
HU, D, H = 10.0, 10.5, 8.4
DP = 1.45
TILES = [("back", 0, 800, 336), ("left", 800, 420, 336), ("right", 1220, 420, 336), ("floor", 1640, 800, 420),
         ("ceil", 2440, 800, 420)]
ROW_W, ROW_H = 3240, 420

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0] if args else ""
NV = int(args[1]) if len(args) > 1 else 6


class MAcc:
    def __init__(self, mat):
        self.mat, self.v, self.f, self.c, self.k = mat, [], [], [], []

    def face(self, pts, col, k=0.0):
        b = len(self.v)
        self.v.extend(tuple(p) for p in pts)
        self.f.append(tuple(range(b, b + len(pts))))
        self.c.append(tuple(col)[:3])
        self.k.append(float(k))

    def build(self, coll, name):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        me.validate()
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        ka = me.attributes.new("k", "FLOAT", "FACE")
        cols = []
        for poly in me.polygons:
            ka.data[poly.index].value = self.k[poly.index]
            for _ in poly.loop_indices:
                cols.extend(tuple(self.c[poly.index]) + (1.0,))
        ca.data.foreach_set("color", cols)
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        ob.data.materials.append(self.mat)
        return ob


def mat_office():
    m = bpy.data.materials.new("office")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    c = nt.nodes.new("ShaderNodeAttribute")
    c.attribute_name = "col"
    k = nt.nodes.new("ShaderNodeAttribute")
    k.attribute_name = "k"
    nt.links.new(c.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(c.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Roughness"].default_value = 0.6
    nt.links.new(k.outputs["Fac"], b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], o.inputs[0])
    return m


def mat_lamp():
    m = bpy.data.materials.new("lamp")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    c = nt.nodes.new("ShaderNodeAttribute")
    c.attribute_name = "col"
    k = nt.nodes.new("ShaderNodeAttribute")
    k.attribute_name = "k"
    nt.links.new(c.outputs["Color"], e.inputs["Color"])
    nt.links.new(k.outputs["Fac"], e.inputs["Strength"])
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def mat_glass():
    m = bpy.data.materials.new("glass")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    t = nt.nodes.new("ShaderNodeBsdfTransparent")
    g = nt.nodes.new("ShaderNodeBsdfGlossy")
    g.inputs["Roughness"].default_value = 0.05
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.08
    nt.links.new(t.outputs[0], mx.inputs[1])
    nt.links.new(g.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    return m


YC = DP - D / 2.0                      # the kit's centre: the middle of the virtual box (kit y = local v - D/2 + DP)


def mock_G():
    """A straight (unsheared) tube of radius 10 centred in the virtual box; window frame u = x, v = y (kit local axes)."""
    g = types.SimpleNamespace()
    g.RT = 10.0

    def tube_pt(t, z, phi, r=None):
        rr = 10.0 if r is None else r
        return (rr * math.cos(phi), YC + rr * math.sin(phi), z)
    g.tube_pt = tube_pt
    g.win_frame = lambda t, f, side="in": dict(tw=(1.0, 0.0), nw=(0.0, 1.0))
    return g


def render_variant(var, seed):
    sc = bpy.context.scene
    coll = bpy.data.collections.new("v%d" % var)
    sc.collection.children.link(coll)
    G = mock_G()
    mo, ml, mg = mat_office(), mat_lamp(), mat_glass()
    acc = {"off": MAcc(mo), "glass": MAcc(mg), "lamp": MAcc(ml)}
    rng = random.Random(seed)
    CH = 4.0
    zl = 0.0
    zu = zl + CH + 0.4
    OFC.slab(G, "A", 0, acc, (0.22, 0.21, 0.195), (0.12, 0.14, 0.14), 0.20, z0=zl - 2.25, z1=zl)
    OFC.slab(G, "A", 0, acc, (0.22, 0.21, 0.195), (0.12, 0.14, 0.14), 0.20, z0=zl + CH, z1=zu)
    OFC.ceiling_disc(G, "A", zu + CH, acc)
    for zs in (zl, zu):
        OFC.floor_interior(G, "A", 0, acc, rng, 2.4, None, zf=zs, ceil_h=CH)
    # the virtual box's walls (rectangular, so the five slices never show the void): back, left, right, floor, ceiling
    yb, yf = DP - D, DP
    wc, wk = (0.52, 0.50, 0.47), 0.22
    o = acc["off"]
    zt = zu + CH + 0.02
    o.face([(-HU, yb, -0.02), (HU, yb, -0.02), (HU, yb, zt), (-HU, yb, zt)], wc, wk)
    o.face([(-HU, yf, -0.02), (-HU, yb, -0.02), (-HU, yb, zt), (-HU, yf, zt)], wc, wk)
    o.face([(HU, yb, -0.02), (HU, yf, -0.02), (HU, yf, zt), (HU, yb, zt)], wc, wk)
    o.face([(-HU, yb, -0.03), (HU, yb, -0.03), (HU, yf, -0.03), (-HU, yf, -0.03)], (0.22, 0.21, 0.195), 0.2)
    o.face([(-HU, yb, zt), (HU, yb, zt), (HU, yf, zt), (-HU, yf, zt)], (0.42, 0.43, 0.44), 0.06)
    for gx in range(-10, 11, 2):                       # carpet tile seams (the floor slice shows only the carpet)
        o.face([(gx - 0.03, yb, 0.012), (gx + 0.03, yb, 0.012), (gx + 0.03, yf, 0.012), (gx - 0.03, yf, 0.012)], (0.07, 0.07, 0.08), 0.05)
    for gy in range(int(yb) - 1, int(yf) + 1, 2):
        o.face([(-HU, gy - 0.03, 0.012), (HU, gy - 0.03, 0.012), (HU, gy + 0.03, 0.012), (-HU, gy + 0.03, 0.012)], (0.07, 0.07, 0.08), 0.05)
    objs = [a.build(coll, "v%d_%s" % (var, n)) for n, a in acc.items() if a.f]
    return coll, objs


def cam(name, loc, rot, ortho, w, h, cs, ce):
    cd = bpy.data.cameras.new(name)
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_start, cd.clip_end = cs, ce
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob, w, h


def main():
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
    zmid = H / 2.0
    ymid = DP - D / 2.0
    shots = {
        "back": ((0.0, DP, zmid), (math.radians(90), 0, math.radians(180)), 20.0, 800, 336, D - 6.0, D + 0.1),
        "left": ((0.0, ymid, zmid), (math.radians(90), 0, math.radians(90)), D, 420, 336, HU - 6.0, HU + 0.1),
        "right": ((0.0, ymid, zmid), (math.radians(90), 0, math.radians(-90)), D, 420, 336, HU - 6.0, HU + 0.1),
        "floor": ((0.0, ymid, 0.17), (0.0, 0.0, 0.0), 20.0, 800, 420, 0.02, 0.19),
        "ceil": ((0.0, ymid, 0.1), (math.radians(180), 0, 0), 20.0, 800, 420, 7.9, 8.5),
    }
    for var in range(NV):
        coll, objs = render_variant(var, 7100 + 37 * var)
        for n, (loc, rot, ortho, w, h, cs, ce) in shots.items():
            co, _, _ = cam("c_" + n, loc, rot, ortho, w, h, cs, ce)
            sc.camera = co
            sc.render.resolution_x, sc.render.resolution_y = w, h
            sc.render.resolution_percentage = 100
            p = os.path.join(os.path.dirname(OUT), "_tile_%d_%s.png" % (var, n))
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(co)
        for o in objs:
            bpy.data.objects.remove(o)
        sc.collection.children.unlink(coll)
        print("variant", var, "done", flush=True)
    print("tiles done; assemble with: python hq_atlas.py assemble <dir> <out.png> <variants>", flush=True)


main()
