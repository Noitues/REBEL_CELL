"""Solace culture garden: the AAA-2 night frames (Cycles). blender -b --factory-startup --python gs_scene.py -- --dir A --view street|inside ...

  street  : the decision camera on the border street / plaza (O2): the garden as the stage, the O-route nodes, the Bloom A front CREEPING in the street gap
  inside  : the garden with its front glazing open, I1 / I3 (workshop alcove) / I5 (seed vault) lit, the Bloom CATCHING on the lower levels

Output: a multilayer EXR -> npy passes (combined, emit, voldir) in --out (the stem), post by gs_post.py. District / HQ v5 / Bloom 3D scenes are the sources:
materials = sd_lib (district), look = HQ v5 Cycles settings, Bloom A = gs_bloom.py (the Bloom 3D world-position node groups, generalised axis).
"""
import json
import math
import os
import random
import sys
import time

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import sd_lib as L  # noqa: E402
import gs_garden as GG  # noqa: E402
import gs_bloom as BL  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
A = {"dir": "A", "view": "street", "size": "1920x1080", "spp": "64", "out": "D:/rc_scratch/solace_v1/garden/out/t_street", "bloom": "1", "seed": "7",
     "cam": "", "lens": "", "expo_probe": "0", "cpu": "0", "fog": "", "room": "", "front": "", "moon": "1.0", "gk": "1.0", "sky": "1.0", "winmul": "1.0", "rc": "0", "probe": "0"}
for i in range(0, len(argv), 2):
    A[argv[i].lstrip("-")] = argv[i + 1]
KIND, VIEW = A["dir"], A["view"]
W, H = [int(x) for x in A["size"].split("x")]
SEED = int(A["seed"])
STREET = VIEW == "street"
BLOOM_ON = A["bloom"] == "1"
LIME, MINT, CREAM, WARM = GG.LIME, GG.MINT, GG.CREAM, GG.WARM

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = 100
L.Z_FLAT = False
L.DAY = False
L.EMIT_K = 1.0

BUILD = {}


def mb(key, smooth=False):
    k = (key, smooth)
    if k not in BUILD:
        BUILD[k] = L.MB("%s_%s" % (key, "s" if smooth else "f"))
    return BUILD[k]


# ------------------------------------------------------------------ materials (night, AAA-2)
def ghost_glass(name, strength=0.25, refl=0.10, rough=0.04):
    """See-through glass: Transparent <-> glossy by a fresnel-ish weight, plus a faint tint emission from the vertex colour."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    nb = L.NB(nt)
    out = nb.node("ShaderNodeOutputMaterial")
    colN = nb.attr("col")
    prmN = nb.attr("prm")
    _r, _g, _b = nb.sepc(prmN.outputs["Color"])
    tr = nb.node("ShaderNodeBsdfTransparent")
    gl = nb.node("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = rough
    nb.link(colN.outputs["Color"], gl.inputs["Color"])
    lw = nb.node("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    fac = nb.m("ADD", refl, nb.m("MULTIPLY", lw.outputs["Fresnel"], 0.6))
    mx = nb.node("ShaderNodeMixShader")
    nb.link(fac, mx.inputs[0])
    nb.link(tr.outputs[0], mx.inputs[1])
    nb.link(gl.outputs[0], mx.inputs[2])
    em = nb.node("ShaderNodeEmission")
    nb.link(colN.outputs["Color"], em.inputs["Color"])
    nb.val(em.inputs["Strength"], nb.m("MULTIPLY", _r, strength))
    ad = nb.node("ShaderNodeAddShader")
    nb.link(mx.outputs[0], ad.inputs[0])
    nb.link(em.outputs[0], ad.inputs[1])
    nb.link(ad.outputs[0], out.inputs[0])
    return m


def route_mat():
    m = bpy.data.materials.new("route")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    nb = L.NB(nt)
    out = nb.node("ShaderNodeOutputMaterial")
    colN = nb.attr("col")
    prmN = nb.attr("prm")
    r, g_, b_ = nb.sepc(prmN.outputs["Color"])
    em = nb.node("ShaderNodeEmission")
    nb.link(colN.outputs["Color"], em.inputs["Color"])
    nb.val(em.inputs["Strength"], nb.m("MULTIPLY", r, 1.0))
    nb.link(em.outputs[0], out.inputs[0])
    return m


M = {}
M["plain"] = L.make_material("plain", "win", "night", plain=True, rough=0.30, metal=0.0, coat=0.35)
M["tw"] = L.make_material("tw", "win", "night", cw=100.0, ch=4.2, win=(0.0, 1.0, 0.22, 0.72), strength=0.25, rough=0.35)
M["ord"] = L.make_material("ord", "win", "night", cw=3.4, ch=3.8, win=(0.2, 0.75, 0.25, 0.7), strength=0.15, rough=0.45)
M["neon"] = L.make_material("neon", "neon", "night", strength=0.7)
M["neon_s"] = L.make_material("neon_s", "neon", "night", strength=1.1)
M["neon_l"] = L.make_material("neon_l", "neon", "night", strength=0.32)
M["agar"] = L.make_material("agar", "neon", "night", strength=0.65)
M["water"] = L.make_material("water", "water", "night")
M["ground"] = L.make_material("ground", "ground", "night")
M["glass"] = ghost_glass("glass", 0.04, 0.10)
M["glassB"] = ghost_glass("glassB", 0.05, 0.08)
M["route"] = route_mat()


def build_all():
    for (key, smooth), b in BUILD.items():
        ob = b.build(M[key], smooth, coll)
        if ob is not None:
            ob.pass_index = {"ground": 4}.get(key, 1)


class Ctx:
    def __init__(self):
        self.cel = False
        self.seed = 3

    def mb(self, key, smooth=False):
        return mb(key, smooth)


CTX = Ctx()
rr = random.Random(SEED)


# ------------------------------------------------------------------ the world around the lot
def blocks():
    """Ordinary night-city blocks around the lot: a ring in the distance and flank walls beside the plaza. Never on the sight line (street view)."""
    om = mb("ord")
    for j in range(-9, 10):
        for i in range(-9, 10):
            cx, cy = i * 24.0, j * 24.0 + 10.0
            if abs(cx) < 40.0 and cy < 52.0 and cy > -140.0:                 # the garden lot and the avenue in front of it
                continue
            if STREET and (abs(cx) < 60.0 and cy < 80.0 or cy < -16.0 and abs(cx) < 130.0):
                continue
            if not STREET and math.hypot(cx, cy - 7.0) < 100.0:
                continue
            r = math.hypot(cx, cy)
            if r < 52.0:
                continue
            h = rr.uniform(20.0, 55.0) + 55.0 * rr.random() ** 3 * min(1.0, r / 150.0)
            if STREET and cy < -30.0 and abs(cx) < 80.0:
                h = rr.uniform(10.0, 22.0)                                          # the near side stays low: the camera sees over it
            hw = 7.2 + 0.8 * rr.random()
            col = (0.035, 0.032, 0.055) if rr.random() < 0.6 else (0.04, 0.045, 0.06)
            L.box(om, cx - hw, cy - hw, 0.0, cx + hw, cy + hw, h, col, ((0.45 if rr.random() < 0.7 else 0.2) if STREET else 0.25, 0.0, 0.0, rr.random() * 8.0 + 0.5))
            if rr.random() < 0.55:
                L.box(om, cx - hw * 0.6, cy - hw * 0.6, h, cx + hw * 0.6, cy + hw * 0.6, h + rr.uniform(3.0, 9.0), col, (0.7, 0, 0, rr.random() * 9 + 0.5))
            if rr.random() < 0.35:                                                   # a cool or amber sign strip near the top
                sc = (0.25, 0.8, 1.0) if rr.random() < 0.5 else (1.0, 0.62, 0.2)
                L.box(mb("neon"), cx - hw - 0.1, cy - 2.0, h * 0.62, cx - hw, cy + 2.0, h * 0.62 + 5.0, sc, (0.35, 0, 0, 1))


def ground_world():
    g = mb("ground")
    ext = 900.0
    L.flat_poly(g, [(-ext, -ext, -0.05), (ext, -ext, -0.05), (ext, ext, -0.05), (-ext, ext, -0.05)], tuple(c * float(A['gk']) for c in (0.030, 0.032, 0.052)), (0.5, 1.0, 0, 1))
    # the avenue / border street in front of the lot, the side streets
    asph = tuple(c * float(A['gk']) for c in (0.028, 0.030, 0.045))
    L.box(g, -140.0, -62.0, 0.0, 140.0, -21.0, 0.12, asph, (0.5, 1.0, 0, 1))
    L.box(g, -32.0, -21.0, 0.0, -24.0, 21.0, 0.12, asph, (0.5, 1.0, 0, 1))
    L.box(g, 24.0, -21.0, 0.0, 32.0, 21.0, 0.12, asph, (0.5, 1.0, 0, 1))
    L.box(g, -32.0, 21.0, 0.0, 32.0, 29.0, 0.12, asph, (0.5, 1.0, 0, 1))
    n = mb("neon")
    for q in range(-34, 35):                                                                                  # lane dashes on the avenue
        for y in (-41.5, -52.0):
            L.box(n, q * 4.0 - 1.0, y - 0.08, 0.12, q * 4.0 + 1.0, y + 0.08, 0.16, (0.9, 0.7, 0.35), (0.10, 0, 0, 1))
    for q in range(-30, 31):                                                                                  # kerb light along the lot edge
        L.box(n, q * 4.5, -29.4, 0.12, q * 4.5 + 2.0, -29.3, 0.17, LIME, (0.05, 0, 0, 1))
    # lamp posts along the avenue edge (warm heads)
    for q in range(-9, 10):
        x = q * 14.0 + 3.0
        L.cyl(mb("plain"), x, -62.5, 0.0, 7.5, 0.12, 5, (0.03, 0.03, 0.035), (0, 0, 0, 0.5), cap=False)
        L.box(mb("neon_s"), x - 0.8, -62.9, 7.5, x + 0.8, -62.1, 7.62, (1.0, 0.78, 0.45), (0.5, 0, 0, 1))


def route_nodes(room):
    """Concept proxy of the street route (the game draws the real chrome): rings + light columns + links on the ground."""
    R = mb("route")
    ORANGE, WHITE, ACID, DIM = (1.0, 0.55, 0.10), (1.0, 0.97, 0.9), (0.83, 1.0, 0.0), (0.55, 0.66, 0.78)
    nodes = {"O0": (-34.0, -26.0, "walked", "start"), "O1a": (-22.0, -29.5, "walked", "fight"), "O1b": (-22.0, -22.5, "cut", "fight"),
             "O2a": (-8.0, -15.0, "current", "fight"), "O2b": (8.0, -15.0, "cut", "terminal"), "O3": (0.0, -9.6, "next", "fight")}
    links = [("O0", "O1a", "walked"), ("O0", "O1b", "cut"), ("O1a", "O2a", "walked"), ("O1b", "O2b", "cut"), ("O2a", "O3", "next"), ("O2b", "O3", "cut")]
    col = {"walked": ACID, "current": WHITE, "next": ORANGE, "cut": DIM}
    hgt = {"walked": 5.0, "current": 15.0, "next": 19.0, "cut": 7.0}
    strn = {"walked": 0.55, "current": 0.9, "next": 0.7, "cut": 0.28}
    for k, (x, y, st, kind) in nodes.items():
        c = col[st]
        s = strn[st]
        rad = 3.6 if st in ("current", "next") else 2.8
        L.torus(R, x, y, 0.32, rad, 0.3, 28, 5, c, (s * 3.0, 0, 0, 1))
        L.cyl(R, x, y, 0.2, 0.34, rad - 0.2, 28, c, (s * 0.10, 0, 0, 1))
        if kind == "terminal":                                                       # a square frame marks the event kind
            L.box(R, x - 3.3, y - 3.3, 0.2, x + 3.3, y - 3.0, 0.5, c, (s * 3.0, 0, 0, 1))
            L.box(R, x - 3.3, y + 3.0, 0.2, x + 3.3, y + 3.3, 0.5, c, (s * 3.0, 0, 0, 1))
            L.box(R, x - 3.3, y - 3.0, 0.2, x - 3.0, y + 3.0, 0.5, c, (s * 3.0, 0, 0, 1))
            L.box(R, x + 3.0, y - 3.0, 0.2, x + 3.3, y + 3.0, 0.5, c, (s * 3.0, 0, 0, 1))
        if kind == "start":
            L.torus(R, x, y, 0.32, rad + 1.0, 0.14, 28, 5, c, (s * 3.0, 0, 0, 1))
        L.cyl(R, x, y, 0.3, hgt[st], (0.26 if k != "O3" else 0.15) if st != "cut" else 0.16, 8, c, (s * 4.0, 0, 0, 1), cap=False)
        L.sphere(R, x, y, hgt[st] + 0.5, 1.1 if st in ("current", "next") else 0.65, 8, c, (s * 5.0, 0, 0, 1))
        if st == "current":                                                          # a soft pillar of light (a wider pale sleeve)
            L.cyl(R, x, y, 0.3, hgt[st], 0.7, 10, c, (s * 0.18, 0, 0, 1), cap=False)
    for a, b, st in links:
        (x0, y0, _s0, _k0), (x1, y1, _s1, _k1) = nodes[a], nodes[b]
        c = col[st]
        n = 1 if st != "cut" else 7
        if st == "cut":
            for q in range(n):
                t0, t1 = q / n, (q + 0.55) / n
                L.strip(R, (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1), 0.16, 0.30, c, (0.8, 0, 0, 1))
        else:
            L.strip(R, (x0, y0), (x1, y1), 0.5 if st == "next" else 0.36, 0.31, c, (1.6 if st == "next" else 1.0, 0, 0, 1))
    for sx in (-1, 1):                                                              # orange gate posts frame the door: O3 (next) reads at the squint
        L.cyl(R, sx * 4.2, -8.4, 0.3, 11.5, 0.22, 8, ORANGE, (1.8, 0, 0, 1), cap=False)
        L.sphere(R, sx * 4.2, -8.4, 12.0, 0.7, 8, ORANGE, (2.2, 0, 0, 1))
    L.box(R, -4.2, -8.5, 11.4, 4.2, -8.3, 11.7, ORANGE, (2.0, 0, 0, 1))
    # the operative: a cyan token on O2a
    x, y = nodes["O2a"][0] + 2.3, nodes["O2a"][1] - 1.2
    L.cyl(R, x, y, 0.3, 3.4, 0.5, 8, (0.36, 0.88, 1.0), (1.2, 0, 0, 1))
    L.sphere(R, x, y, 4.0, 0.85, 8, (0.36, 0.88, 1.0), (1.6, 0, 0, 1))
    L.torus(R, x, y, 0.4, 1.4, 0.16, 20, 5, (0.36, 0.88, 1.0), (1.2, 0, 0, 1))
    return nodes


def slot_frames():
    """Concept proxy of the route's room slots inside the garden (the game draws the real chrome): a thin frame at the glazing line of every slot
    (I1 3, I2 2, I3 3, I4 2, I5 1 large). States: I1 walked (acid), I3 current (white) and its WORKSHOP slot (gold), I4 next (orange, thin), I5 the target
    (orange, LARGE) plus a light column over the vault; the rest are dim (later / cut)."""
    R = mb("route")
    ACID, WHITE, ORANGE, DIM, GOLD = (0.83, 1.0, 0.0), (1.0, 0.97, 0.9), (1.0, 0.55, 0.10), (0.55, 0.66, 0.78), (1.0, 0.72, 0.22)
    SL = GG.slot_list(LEV)

    def front_y(lv, xc):
        if KIND == "A":
            return lv["y"][0] - 0.25
        x0, x1 = lv["x"]
        y0, y1 = lv["y"]
        rx, ry, cy_ = (x1 - x0) / 2.0, (y1 - y0) / 2.0, (y0 + y1) / 2.0
        return cy_ - ry * math.sqrt(max(0.02, 1.0 - (xc / rx) ** 2)) - 0.3

    def frame(xc, w, z0, z1, y, col, s, r):
        x0, x1 = xc - w / 2, xc + w / 2
        for (a, b) in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
            L.seg_tube(R, (a[0], y, a[1]), (b[0], y, b[1]), r, 5, col, (s, 0, 0, 1))
        for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            L.sphere(R, x, y, z, r * 1.7, 6, col, (s * 1.4, 0, 0, 1))
    state = {("I1", 0): (ACID, 1.4, 0.2), ("I2", 1): (ACID, 1.0, 0.16), ("I3", 1): (WHITE, 1.5, 0.22), ("I3", 2): (GOLD, 2.0, 0.22),
             ("I4", 0): (ORANGE, 0.9, 0.14), ("I4", 1): (ORANGE, 0.9, 0.14)}
    out = {}
    for name, slots in SL.items():
        lv = LEV[name]
        z0, z1 = lv["z"]
        for i, (xc, w) in enumerate(slots):
            if name == "I5":
                continue
            col, s, r = state.get((name, i), (DIM, 0.32, 0.1))
            frame(xc, w, z0 + 0.5, z1 - 0.9, front_y(lv, xc), col, s, r)
            out[(name, i)] = (round(xc, 2), round(w, 2))
    lv = LEV["I5"]
    z0, z1 = lv["z"]
    xc, w = SL["I5"][0]
    frame(xc, w + 0.8, z0 + 0.2, z1 - 0.1, front_y(lv, 0.0) - 0.05, ORANGE, 3.0, 0.26)
    L.cyl(R, 0.0, (lv["y"][0] + lv["y"][1]) / 2, z1 + 3.5, z1 + 32.0, 0.22, 8, ORANGE, (1.8, 0, 0, 1), cap=False)           # the target's light column
    L.cyl(R, 0.0, (lv["y"][0] + lv["y"][1]) / 2, z1 + 3.5, z1 + 32.0, 0.9, 10, ORANGE, (0.10, 0, 0, 1), cap=False)
    out[("I5", 0)] = (round(xc, 2), round(w, 2))
    return out


# ------------------------------------------------------------------ assemble
t_start = time.time()
ground_world()
blocks()
LEV = GG.build(KIND, CTX, 0.0, 0.0, detail=1 if STREET else 2, cut=not STREET)
GG.lot(CTX, 0.0, 0.0, detail=1 if STREET else 2)
NODES = route_nodes(A["room"]) if STREET else slot_frames()
build_all()
if A.get('probe') == '1':
    pm = bpy.data.materials.new('probe'); pm.use_nodes = True
    me_ = bpy.data.meshes.new('probe'); me_.from_pydata([(-6,-6,0),(6,-6,0),(6,6,0),(-6,6,0),(-6,-6,12),(6,-6,12),(6,6,12),(-6,6,12)], [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    po = bpy.data.objects.new('probe', me_); po.data.materials.append(pm); po.location = (-30, -60, 0); coll.objects.link(po)


# ------------------------------------------------------------------ world: graded sky + haze, lights
def world():
    w = bpy.data.worlds.new("w")
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ab = nt.nodes.new("ShaderNodeMath")
    ab.operation = "ABSOLUTE"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(geo.outputs["Incoming"], sep.inputs[0])
    nt.links.new(sep.outputs[2], ab.inputs[0])
    nt.links.new(ab.outputs[0], ramp.inputs[0])
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, tuple(c * float(A['sky']) for c in (0.26, 0.17, 0.44)) + (1,)
    e[1].position, e[1].color = 0.6, (0.014, 0.018, 0.05, 1)
    e2 = e.new(0.22)
    e2.color = tuple(c * float(A['sky']) for c in (0.07, 0.05, 0.14)) + (1,)
    bg.inputs[1].default_value = 1.0
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    # the haze is a bounded box (a world volume is infinite and swallows the sun and the moon): x +-420, y -260..320, z 0..140
    me = bpy.data.meshes.new("fog")
    x0, x1, y0, y1, z0, z1 = -420.0, 420.0, -260.0, 320.0, -1.0, 140.0
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], [],
                   [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    ob = bpy.data.objects.new("fog", me)
    fm = bpy.data.materials.new("sky_fog")
    fm.use_nodes = True
    fnt = fm.node_tree
    fnt.nodes.clear()
    fo = fnt.nodes.new("ShaderNodeOutputMaterial")
    vol = fnt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.55, 0.50, 0.85, 1)
    vol.inputs["Density"].default_value = float(A["fog"] or (0.0030 if STREET else 0.0030))
    vol.inputs["Anisotropy"].default_value = 0.35
    fnt.links.new(vol.outputs[0], fo.inputs[2])
    me.materials.append(fm)
    coll.objects.link(ob)
    ob.visible_shadow = False


def add_light(kind, loc, col, power, size=1.0, rot=None, angle=0.05):
    ld = bpy.data.lights.new(kind, kind)
    ld.color = col
    ld.energy = power
    if kind == "SUN":
        ld.angle = angle
    elif kind == "AREA":
        ld.size = size
    else:
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(kind, ld)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    coll.objects.link(ob)
    return ob


def lights():
    add_light("SUN", (0, 0, 300), (0.55, 0.62, 1.0), float(A["moon"]), rot=(math.radians(28), 0, math.radians(-40)), angle=0.05)
    add_light("SUN", (0, 0, 300), (0.75, 0.55, 0.95), 0.25, rot=(math.radians(35), 0, math.radians(140)), angle=0.1)
    if STREET:
        add_light("POINT", (0, -15, 24), (0.9, 1.0, 0.9), 2.5e4, size=6)            # the garden's own glow on the plaza
        add_light("POINT", (0, -9, 4), CREAM, 6e3, size=3)                           # the door's spill
    else:
        zfront = ZF_INFO
        for name, lv in LEV.items():
            if name.endswith("workshop"):
                continue
            cxl = (lv["x"][0] + lv["x"][1]) / 2
            cyl = (lv["y"][0] + lv["y"][1]) / 2
            czl = lv["z"][0] + (lv["z"][1] - lv["z"][0]) * 0.55
            big = lv.get("large")
            col = MINT if KIND == "B" else LIME
            k = 0.12 if (BLOOM_ON and lv["z"][1] < zfront + 4.0) else 1.0           # dying light under the front
            lp = lv.get("light")
            if lp and not big:
                add_light("POINT", lp, (0.92, 1.0, 0.92), 2.4e3 * k, size=2.5)
                add_light("POINT", (lp[0], lp[1] + 1.0, lp[2] + 0.5), col, 1.0e3 * k, size=2.0)
                continue
            add_light("POINT", (cxl, cyl - 3.0, czl), (0.92, 1.0, 0.92), (0.7e3 if not big else 2.2e3) * k, size=3.0)
            add_light("POINT", (cxl, cyl, czl), col, (0.25e3 if not big else 1.2e3) * k, size=2.0)
        add_light("POINT", (0, -16, 6), (0.9, 1.0, 0.9), 4e3, size=5)


ZF_INFO = 0.0
if not STREET:
    _z3, _z2 = LEV['I3']['z'][0], LEV['I2']['z'][0]
    ZF_INFO = float(A['front'] or (_z3 - 0.6 * (_z3 - _z2)))
world()
lights()
for _o in coll.objects:
    if _o.type == 'LIGHT':
        print('LIGHT', _o.name, _o.data.type, round(_o.data.energy, 1), tuple(round(v, 2) for v in _o.rotation_euler), flush=True)

# ------------------------------------------------------------------ camera
cam = bpy.data.cameras.new("cam")
cob = bpy.data.objects.new("cam", cam)
coll.objects.link(cob)
scene.camera = cob
cam.sensor_width = 36.0
cam.clip_start, cam.clip_end = 0.5, 4000
if STREET:
    loc, tgt, lens = (-12.0, -104.0, 30.0), (-6.0, -14.0, 16.0), 30.0
else:
    loc, tgt, lens = (0.0, -88.0, 36.0), (0.0, 7.0, 23.0), 29.0
if A["cam"]:
    v = [float(x) for x in A["cam"].split(",")]
    loc, tgt = tuple(v[:3]), tuple(v[3:6])
    if len(v) > 6:
        lens = v[6]
if A["lens"]:
    lens = float(A["lens"])
cam.lens = lens
cob.location = loc
cob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ the Bloom (A Necrosis), world-position material, wrapped round every look
PINK_LIN = (1.0, 0.0612, 0.305)
PLUM_LIN = (0.075, 0.030, 0.058)
BLOOM_INFO = {}
if BLOOM_ON:
    cfg = dict(seed=7, tend=5.0, tend_h=2.5, vscale=0.7, vw=0.045, ew=0.45, hatch_k=2.5, veins=0.9, edge=7.0, hatch=0.08, cover_k=0.89,
               plum=PLUM_LIN, pink=PINK_LIN, boxes=[], retain=0.02)
    if STREET:
        xf = float(A["front"] or -35.8)           # the front x on the street: layer -0.15 against O0 -34 and layer spacing 12 (gap to O2 = 2.15, CREEPING)
        cfg.update(axis="x", sgn=-1.0, front_c=-xf, zk=1.1, tend=6.0, tend_h=4.0, fing=4.0, tide=[9.0, 0.5, 30.0])
        BLOOM_INFO = dict(front_x=xf, gap_layers=2.15)
    else:
        # the front on the height axis: operative on I3, front 0.6 of a layer under the I3 floor (CATCHING: gap < 1.0)
        z3, z2 = LEV["I3"]["z"][0], LEV["I2"]["z"][0]
        zf = float(A["front"] or (z3 - 0.6 * (z3 - z2)))
        cfg.update(axis="z", sgn=-1.0, front_c=-zf, zk=0.0, tend=0.0, tend_h=1.0, fing=3.0, rad=[0.0, 5.0, 30.0, 52.0], veins=0.85, hatch=0.05)
        BLOOM_INFO = dict(front_z=round(zf, 2), I3_floor=z3, I2_floor=z2)
    BL.set_cfg(cfg)
    for m in bpy.data.materials:
        if m.name in ("ord",) and not STREET:
            m["bl_on"] = True                                                 # the backdrop city is not the garden's: no skin on it (inside view)
    print("BLOOM sweep", BL.sweep(), BLOOM_INFO, flush=True)
    if STREET:                                                                  # vein ribbons crawl ahead of the front on the ground
        import bmesh
        rnd = random.Random(11)
        bm = bmesh.new()
        mat = bpy.data.materials.new("bl_ribbon")
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        o_ = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = PINK_LIN + (1,)
        em.inputs["Strength"].default_value = 1.0
        nt.links.new(em.outputs[0], o_.inputs[0])
        mat["bl_on"] = True

        def walk(p, ang, length, depth):
            pts = [p]
            for _ in range(int(length / 0.6)):
                ang += rnd.gauss(0, 0.22)
                ang *= 0.93
                q = (pts[-1][0] + math.cos(ang) * 0.6, pts[-1][1] + math.sin(ang) * 0.6, 0.2)
                if q[1] > -22.0 or q[1] < -61.0:
                    break
                if abs(q[1] + 26.0) < 8.0 and abs(q[0] + 34.0) < 3.0 or abs(q[0] + 22.0) < 3.0 and abs(q[1] + 26.0) < 6.5:
                    pass
                pts.append(q)
                if depth < 2 and rnd.random() < 0.05:
                    walk(q, ang + rnd.choice((-1, 1)) * 0.7, length * 0.5, depth + 1)
            if len(pts) < 3:
                return
            w = 0.10 * (1.0 if depth == 0 else 0.65)
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                t = 1.0 - i / len(pts)
                nx, ny = -(b[1] - a[1]), (b[0] - a[0])
                Ln = math.hypot(nx, ny) or 1.0
                nx, ny = nx / Ln * w * t * 0.5, ny / Ln * w * t * 0.5
                v = [bm.verts.new((a[0] - nx, a[1] - ny, a[2])), bm.verts.new((a[0] + nx, a[1] + ny, a[2])), bm.verts.new((b[0] + nx, b[1] + ny, b[2])), bm.verts.new((b[0] - nx, b[1] - ny, b[2]))]
                try:
                    bm.faces.new(v)
                except ValueError:
                    pass
        for i in range(70):
            x0 = xf + rnd.uniform(-1.5, 3.0)
            y0 = rnd.uniform(-60.0, -23.0)
            walk((x0, y0, 0.2), rnd.gauss(0, 0.3), rnd.uniform(5.0, 20.0), 0)
        me = bpy.data.meshes.new("bl_ribbons")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("bl_ribbons", me)
        me.materials.append(mat)
        coll.objects.link(ob)
print("BUILD %.1f s" % (time.time() - t_start), flush=True)
if A.get('rc') == '1':
    dg = bpy.context.evaluated_depsgraph_get()
    sun = [o for o in coll.objects if o.type == 'LIGHT' and o.data.type == 'SUN'][0]
    d = sun.matrix_world.to_3x3() @ Vector((0, 0, 1))
    for p in ((0, -120, 0.5), (-60, -60, 0.5), (0, -30, 0.5)):
        hit = scene.ray_cast(dg, Vector(p), d)
        print('RAYCAST', p, tuple(round(v, 2) for v in d), hit[0], hit[4].name if hit[0] else None, flush=True)


# ------------------------------------------------------------------ Cycles (HQ v5 look settings)
scene.render.engine = "CYCLES"
cy = scene.cycles
cy.samples = int(A["spp"])
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.adaptive_min_samples = min(16, cy.samples)
cy.use_denoising = True
for k_, v_ in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_input_passes", "RGB_ALBEDO_NORMAL"), ("denoising_prefilter", "ACCURATE"),
               ("denoising_quality", "HIGH"), ("denoising_use_gpu", True)):
    try:
        setattr(cy, k_, v_)
    except (TypeError, AttributeError):
        pass
cy.seed = 7
cy.use_light_tree = True
cy.max_bounces = 7
cy.diffuse_bounces = 3
cy.glossy_bounces = 4
cy.transmission_bounces = 4
cy.volume_bounces = 0
cy.transparent_max_bounces = 20
cy.sample_clamp_indirect = 6.0
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.volume_step_rate = 1.0
cy.volume_max_steps = 256
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
vl = bpy.context.view_layer
vl.use_pass_combined = True
vl.use_pass_z = True
vl.use_pass_emit = True
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
if A["cpu"] == "1":
    cy.device = "CPU"
else:
    cy.device = "GPU"
    pref = bpy.context.preferences.addons["cycles"].preferences
    pref.compute_device_type = "HIP"
    try:
        pref.use_hiprt = False
    except (AttributeError, TypeError):
        pass
    pref.refresh_devices()
    n_ = 0
    for d in pref.devices:
        d.use = d.type == "HIP"
        n_ += d.use
    print("HIP devices", n_, flush=True)

stem = A["out"]
os.makedirs(os.path.dirname(stem), exist_ok=True)
scene.render.filepath = stem + ".exr"
t0 = time.time()
bpy.ops.render.render(write_still=True)
rt = time.time() - t0
print("RENDER_SECONDS %.1f" % rt, flush=True)


def exr_to_npy(path, stem, want):
    import OpenImageIO as oiio
    import numpy as np
    inp = oiio.ImageInput.open(path)
    k = 0
    while inp.seek_subimage(k, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        pas = ".".join(names[0].split(".")[1:-1]) if names[0].count(".") >= 2 else names[0]
        if pas in want:
            px = np.asarray(inp.read_image(k, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
            keepc = [ci for ci, nm in enumerate(names) if not nm.endswith(".A")]
            np.save(stem + "_" + want[pas] + ".npy", px[..., keepc][..., :3].astype(np.float16))
        k += 1
    inp.close()


exr_to_npy(stem + ".exr", stem, {"Combined": "combined", "Emission": "emit", "Volume Direct": "voldir", "Volume Light": "voldir"})
os.remove(stem + ".exr")
json.dump(dict(render_seconds=round(rt, 1), size=[W, H], kind=KIND, view=VIEW, bloom=BLOOM_INFO, levels=LEV), open(stem + "_info.json", "w"))
print("DONE", flush=True)
