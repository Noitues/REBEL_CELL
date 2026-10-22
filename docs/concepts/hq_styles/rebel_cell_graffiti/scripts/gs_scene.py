"""REBEL_CELL graffiti MAINFRAME shop exterior: Blender 5.2 headless Cycles scene (AAA-2 realistic night).

blender -b --factory-startup --python gs_scene.py -- <out_prefix> <res_w> <spp> [cpu]
Layout and camera follow round12 F1b (one-point street view, tower left with the vertical sign, alley stair,
front building with roll shutters, city behind); eye lowered to street level. Everything is PBR with textures from
gs_tex.py (graffiti atlases, red MAINFRAME sign, blade signs). Writes <prefix>_beauty.npy (linear HDR).
"""
import json
import math
import os
import random
import sys
import time

import bpy
import bmesh
from mathutils import Vector

sys.dont_write_bytecode = True
args = sys.argv[sys.argv.index("--") + 1:]
OUT, RES_W, SPP = args[0], int(args[1]), int(args[2])
CPU = "cpu" in args[3:]
TEX = "D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex"
rng = random.Random(2026)

# ------------------------------------------------------------------ layout (from round12 scene.py)
EYE = 3.2
W, H = 1920, 1080
LENS, SENSOR = 24.0, 36.0
HT = SENSOR / 2 / LENS
VT = HT * H / W
SHX = 0.169
D_SIGN, PY0 = 22.0, 26


def sx_to_x(sx, d):
    return d * ((sx - W / 2) / (W / 2) * HT + 2 * HT * SHX)


SX0, SX1 = sx_to_x(52, D_SIGN), sx_to_x(212, D_SIGN)
SW = SX1 - SX0
SH = SW * 2068 / 500.0
SZ0 = 3.5
SZ1 = SZ0 + SH
SHY = ((SZ1 - EYE) / D_SIGN - (H / 2 - PY0) / (H / 2) * VT) / (2 * HT)
YS = D_SIGN + 0.3          # shop facade plane
XA0, XA1 = -2.0, 2.0       # alley walls
YF, YFB, HF = 21.0, 30.5, 7.0
Y_KERB = 18.3
RX0, RX1, RD, RZ = SX0 + 0.3, XA0 - 1.0, 3.0, 3.0
Y_ST0, Y_ST1, Z_LAND, Y_BACK = 26.0, 36.0, 4.5, 46.0

# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.render.resolution_x, sc.render.resolution_y = RES_W, RES_W * 9 // 16
sc.render.resolution_percentage = 100
N = bpy.data.node_groups

IMGS = {}


def img(name, nc=False):
    key = (name, nc)
    if key not in IMGS:
        im = bpy.data.images.load(f"{TEX}/{name}")
        im.colorspace_settings.name = "Non-Color" if nc else "sRGB"
        im.alpha_mode = "STRAIGHT"
        IMGS[key] = im
    return IMGS[key]


class NT:
    """Small node-graph helper."""

    def __init__(self, mat):
        mat.use_nodes = True
        self.t = mat.node_tree
        self.n, self.l = self.t.nodes, self.t.links
        for x in list(self.n):
            self.n.remove(x)
        self.out = self.n.new("ShaderNodeOutputMaterial")

    def node(self, t, **kw):
        nd = self.n.new(t)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.l.new(a, b)

    def val(self, v):
        nd = self.node("ShaderNodeValue")
        nd.outputs[0].default_value = v
        return nd.outputs[0]

    def math(self, op, a, b=None, clamp=False):
        nd = self.node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                nd.inputs[i].default_value = x
            else:
                self.link(x, nd.inputs[i])
        return nd.outputs[0]

    def mix(self, fac, a, b):
        nd = self.node("ShaderNodeMix", data_type="RGBA")
        if isinstance(fac, (int, float)):
            nd.inputs[0].default_value = fac
        else:
            self.link(fac, nd.inputs[0])
        for i, x in ((6, a), (7, b)):
            if isinstance(x, tuple):
                nd.inputs[i].default_value = (*x[:3], 1.0)
            else:
                self.link(x, nd.inputs[i])
        return nd.outputs[2]

    def maprange(self, v, a0, a1, b0, b1):
        nd = self.node("ShaderNodeMapRange")
        self.link(v, nd.inputs[0])
        nd.inputs[1].default_value, nd.inputs[2].default_value = a0, a1
        nd.inputs[3].default_value, nd.inputs[4].default_value = b0, b1
        return nd.outputs[0]


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexl(h):
    h = h.lstrip("#")
    return tuple(lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def principled(nt, **kw):
    p = nt.node("ShaderNodeBsdfPrincipled")
    for k, v in kw.items():
        if k in p.inputs:
            if isinstance(v, (int, float, tuple)):
                p.inputs[k].default_value = v if not isinstance(v, tuple) else (*v[:3], 1.0)
            else:
                nt.link(v, p.inputs[k])
    nt.link(p.outputs[0], nt.out.inputs["Surface"])
    return p


def mat_simple(name, col, rough=0.6, metal=0.0, emit=None, emit_k=0.0):
    m = bpy.data.materials.new(name)
    nt = NT(m)
    p = principled(nt, **{"Base Color": col, "Roughness": rough, "Metallic": metal})
    if emit:
        p.inputs["Emission Color"].default_value = (*emit[:3], 1.0)
        p.inputs["Emission Strength"].default_value = emit_k
    return m


def mat_emit(name, col, k):
    m = bpy.data.materials.new(name)
    nt = NT(m)
    e = nt.node("ShaderNodeEmission")
    e.inputs[0].default_value = (*col[:3], 1.0)
    e.inputs[1].default_value = k
    nt.link(e.outputs[0], nt.out.inputs["Surface"])
    return m


def mat_noise_bump(nt, p, scale=60, strength=0.15, coord="Object"):
    tc = nt.node("ShaderNodeTexCoord")
    nz = nt.node("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 6
    nt.link(tc.outputs[coord], nz.inputs["Vector"])
    bp = nt.node("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    nt.link(nz.outputs["Fac"], bp.inputs["Height"])
    nt.link(bp.outputs[0], p.inputs["Normal"])


def mat_facade(name, base, off, zhi=30.0, paint_k=1.0):
    """Concrete/brick wall with the world-box-projected graffiti atlas; fluoro paint self-glows a little."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    tc = nt.node("ShaderNodeTexCoord")
    mp = nt.node("ShaderNodeMapping")
    mp.inputs["Location"].default_value = off
    mp.inputs["Scale"].default_value = (1 / 41.0, 1 / 41.0, 1 / 20.5)
    nt.link(tc.outputs["Object"], mp.inputs[0])

    def box(imname, nc):
        it = nt.node("ShaderNodeTexImage", projection="BOX", interpolation="Linear")
        it.projection_blend = 0.0
        it.image = img(imname, nc)
        nt.link(mp.outputs[0], it.inputs[0])
        return it
    alb, glow = box("graf_albedo.png", False), box("graf_glow.png", True)
    # heaven layer: a bigger tile, high up
    mp2 = nt.node("ShaderNodeMapping")
    mp2.inputs["Location"].default_value = (off[0] * 0.3 + 0.1, off[1] * 0.3, off[2] * 0.3)
    mp2.inputs["Scale"].default_value = (1 / 70.0, 1 / 70.0, 1 / 35.0)
    nt.link(tc.outputs["Object"], mp2.inputs[0])
    hv = nt.node("ShaderNodeTexImage", projection="BOX")
    hv.projection_blend = 0.0
    hv.image = img("heaven_albedo.png", False)
    nt.link(mp2.outputs[0], hv.inputs[0])
    sep = nt.node("ShaderNodeSeparateXYZ")
    nt.link(tc.outputs["Object"], sep.inputs[0])
    zone = nt.maprange(sep.outputs[2], 5.0, 11.0, 1.0, 0.0)
    pz = nt.node("ShaderNodeTexNoise")
    pz.inputs["Scale"].default_value = 0.10
    pz.inputs["Detail"].default_value = 2
    nt.link(tc.outputs["Object"], pz.inputs["Vector"])
    patch = nt.maprange(pz.outputs["Fac"], 0.34, 0.47, 0.0, 1.0)
    zone = nt.math("MULTIPLY", zone, patch)
    hz = nt.maprange(sep.outputs[2], 12.0, 20.0, 0.0, 1.0)
    pa = nt.math("MULTIPLY", nt.math("MULTIPLY", alb.outputs["Alpha"], zone), paint_k, clamp=True)
    ha = nt.math("MULTIPLY", nt.math("MULTIPLY", hv.outputs["Alpha"], hz), 0.95, clamp=True)
    # base: concrete with vertical grime streaks
    nz = nt.node("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 8
    mp3 = nt.node("ShaderNodeMapping")
    mp3.inputs["Scale"].default_value = (3.0, 3.0, 0.35)
    nt.link(tc.outputs["Object"], mp3.inputs[0])
    nt.link(mp3.outputs[0], nz.inputs["Vector"])
    base_c = nt.mix(nt.math("MULTIPLY", nz.outputs["Fac"], 0.8), base, (base[0] * 0.25, base[1] * 0.25, base[2] * 0.3))
    # lower wall darker / wetter
    low = nt.maprange(sep.outputs[2], 0.0, 1.4, 0.55, 1.0)
    paint_c = nt.mix(0.3, alb.outputs["Color"], (0.30, 0.28, 0.34))
    c1 = nt.mix(pa, base_c, paint_c)
    c2 = nt.mix(ha, c1, hv.outputs["Color"])
    cdark = nt.mix(nt.math("SUBTRACT", 1.0, low), c2, (0.01, 0.01, 0.015))
    p = principled(nt, **{"Base Color": cdark, "Roughness": 0.72})
    nt.link(nt.math("SUBTRACT", 0.8, nt.math("MULTIPLY", pa, 0.2)), p.inputs["Roughness"])
    nt.link(alb.outputs["Color"], p.inputs["Emission Color"])
    nt.link(nt.math("MULTIPLY", nt.math("MULTIPLY", glow.outputs["Color"], pa), 0.45), p.inputs["Emission Strength"]) \
        if False else None
    gk = nt.math("MULTIPLY", nt.math("MULTIPLY", glow.outputs[0], pa), 0.9)
    nt.link(gk, p.inputs["Emission Strength"])
    p.inputs["Emission Strength"].default_value = 0.0
    mat_noise_bump(nt, p, 40, 0.12)
    return m


def mat_paint_panel(name, k, rough=0.45, metal=0.35, slat=True, glow_k=0.5):
    """A roll shutter: its own fully bombed panel texture (UV 0..1), corrugation bump, glow on fluoro paint."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    a = nt.node("ShaderNodeTexImage")
    a.image = img(f"shutter{k}_albedo.png", False)
    g = nt.node("ShaderNodeTexImage")
    g.image = img(f"shutter{k}_glow.png", True)
    uv = nt.node("ShaderNodeTexCoord")
    nt.link(uv.outputs["UV"], a.inputs[0])
    nt.link(uv.outputs["UV"], g.inputs[0])
    p = principled(nt, **{"Roughness": rough, "Metallic": metal})
    # slat grooves: horizontal sine across v (about 44 slats per panel), darkens the groove
    sp = nt.node("ShaderNodeSeparateXYZ")
    nt.link(uv.outputs["UV"], sp.inputs[0])
    wv = nt.node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Y")
    wv.inputs["Scale"].default_value = 30.0
    wv.inputs["Distortion"].default_value = 0.0
    nt.link(uv.outputs["UV"], wv.inputs["Vector"])
    bp = nt.node("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.6
    bp.inputs["Distance"].default_value = 0.02
    nt.link(wv.outputs["Fac"], bp.inputs["Height"])
    nt.link(bp.outputs[0], p.inputs["Normal"])
    groove = nt.maprange(wv.outputs["Fac"], 0.0, 1.0, 0.62, 1.0)
    col = nt.mix(nt.math("SUBTRACT", 1.0, groove), a.outputs["Color"], (0.0, 0.0, 0.0))
    nt.link(col, p.inputs["Base Color"])
    nt.link(a.outputs["Color"], p.inputs["Emission Color"])
    nt.link(nt.math("MULTIPLY", g.outputs[0], glow_k * 5.0), p.inputs["Emission Strength"])
    return m


def mat_decal(name, imname, k_emit=0.15, alpha_cut=True, scale=1.0):
    m = bpy.data.materials.new(name)
    nt = NT(m)
    a = nt.node("ShaderNodeTexImage", projection="FLAT")
    a.image = img(imname, False)
    uv = nt.node("ShaderNodeTexCoord")
    nt.link(uv.outputs["UV"], a.inputs[0])
    p = principled(nt, **{"Roughness": 0.5})
    nt.link(a.outputs["Color"], p.inputs["Base Color"])
    nt.link(a.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = k_emit
    tr = nt.node("ShaderNodeBsdfTransparent")
    mx = nt.node("ShaderNodeMixShader")
    gt = nt.math("GREATER_THAN", a.outputs["Alpha"], 0.5)
    nt.link(gt, mx.inputs[0])
    nt.link(tr.outputs[0], mx.inputs[1])
    nt.link(p.outputs[0], mx.inputs[2])
    nt.link(mx.outputs[0], nt.out.inputs["Surface"])
    return m


def mat_box_tex(name, imname, base, tile=(1 / 20.0, 1 / 20.0, 1 / 20.0), rough=0.45, metal=0.3, emit=0.15):
    """Opaque object (pole, box, bin) with a box-projected sticker sheet over a base colour."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    tc = nt.node("ShaderNodeTexCoord")
    mp = nt.node("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = tile
    nt.link(tc.outputs["Object"], mp.inputs[0])
    it = nt.node("ShaderNodeTexImage", projection="BOX")
    it.projection_blend = 0.0
    it.image = img(imname, False)
    nt.link(mp.outputs[0], it.inputs[0])
    col = nt.mix(it.outputs["Alpha"], base, it.outputs["Color"])
    p = principled(nt, **{"Roughness": rough, "Metallic": metal})
    nt.link(col, p.inputs["Base Color"])
    nt.link(it.outputs["Color"], p.inputs["Emission Color"])
    nt.link(nt.math("MULTIPLY", it.outputs["Alpha"], emit), p.inputs["Emission Strength"])
    return m


def mat_sign_plate():
    m = bpy.data.materials.new("SIGN_RED")
    nt = NT(m)
    a = nt.node("ShaderNodeTexImage", interpolation="Cubic")
    a.image = img("sign_red.png", False)
    uv = nt.node("ShaderNodeTexCoord")
    nt.link(uv.outputs["UV"], a.inputs[0])
    em = nt.node("ShaderNodeEmission")
    nt.link(a.outputs["Color"], em.inputs[0])
    em.inputs[1].default_value = 30.0
    tr = nt.node("ShaderNodeBsdfTransparent")
    mx = nt.node("ShaderNodeMixShader")
    nt.link(nt.math("GREATER_THAN", a.outputs["Alpha"], 0.5), mx.inputs[0])
    nt.link(tr.outputs[0], mx.inputs[1])
    nt.link(em.outputs[0], mx.inputs[2])
    nt.link(mx.outputs[0], nt.out.inputs["Surface"])
    return m


def mat_blade(name, imname, k, cell, grid):
    """Lit sign face: one cell of an atlas (cell=(c,r), grid=(cols,rows)); emissive with a faint PBR coat."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    uv = nt.node("ShaderNodeTexCoord")
    mp = nt.node("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / grid[0], 1 / grid[1], 1)
    mp.inputs["Location"].default_value = (cell[0] / grid[0], 1 - (cell[1] + 1) / grid[1], 0)
    nt.link(uv.outputs["UV"], mp.inputs[0])
    a = nt.node("ShaderNodeTexImage")
    a.image = img(imname, False)
    nt.link(mp.outputs[0], a.inputs[0])
    em = nt.node("ShaderNodeEmission")
    nt.link(a.outputs["Color"], em.inputs[0])
    em.inputs[1].default_value = k
    nt.link(em.outputs[0], nt.out.inputs["Surface"])
    return m


def mat_ground(name, base, wet_k=1.0, tile=0.6, puddle_k=0.55):
    """Wet pavement/asphalt: noise puddles go mirror-glossy, wet film elsewhere; faint scratches via bump."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    tc = nt.node("ShaderNodeTexCoord")
    n1 = nt.node("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 0.35
    n1.inputs["Detail"].default_value = 4
    n1.inputs["Distortion"].default_value = 0.4
    nt.link(tc.outputs["Object"], n1.inputs["Vector"])
    n2 = nt.node("ShaderNodeTexNoise")
    n2.inputs["Scale"].default_value = 9.0
    n2.inputs["Detail"].default_value = 8
    nt.link(tc.outputs["Object"], n2.inputs["Vector"])
    pud = nt.maprange(n1.outputs["Fac"], puddle_k - 0.04, puddle_k + 0.04, 0.0, 1.0)
    rough = nt.maprange(n2.outputs["Fac"], 0.3, 0.7, 0.10, 0.34)
    rough = nt.mix(pud, rough, (0.02, 0.02, 0.02))      # rgb mix reused as scalar
    sepr = nt.node("ShaderNodeSeparateColor")
    nt.link(rough, sepr.inputs[0])
    p = principled(nt, **{"Base Color": base, "Metallic": 0.0})
    nt.link(sepr.outputs[0], p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.9
    bp = nt.node("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    nt.link(n2.outputs["Fac"], bp.inputs["Height"])
    nt.link(bp.outputs[0], p.inputs["Normal"])
    # tile grid for the pavement
    if tile:
        br = nt.node("ShaderNodeTexBrick")
        br.inputs["Scale"].default_value = 1.0 / tile
        br.inputs["Mortar Size"].default_value = 0.012
        br.inputs["Color1"].default_value = (*base, 1.0)
        br.inputs["Color2"].default_value = (base[0] * 1.5, base[1] * 1.5, base[2] * 1.5, 1.0)
        br.inputs["Mortar"].default_value = (0.01, 0.01, 0.012, 1.0)
        nt.link(tc.outputs["Object"], br.inputs["Vector"])
        nt.link(br.outputs["Color"], p.inputs["Base Color"])
    return m


def mat_citywin(name, wall, scale=(1.7, 1.7, 3.2), lit_p=0.28, k=3.0):
    """Cheap tower: dark wall + procedural lit windows (hash on the cell, warm / cyan / pink)."""
    m = bpy.data.materials.new(name)
    nt = NT(m)
    tc = nt.node("ShaderNodeTexCoord")
    mp = nt.node("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale[0], 1 / scale[1], 1 / scale[2])
    nt.link(tc.outputs["Object"], mp.inputs[0])
    sep = nt.node("ShaderNodeSeparateXYZ")
    nt.link(mp.outputs[0], sep.inputs[0])
    uu = nt.math("ADD", sep.outputs[0], sep.outputs[1])
    vv = sep.outputs[2]
    cu, cv = nt.math("FLOOR", uu), nt.math("FLOOR", vv)
    cmb = nt.node("ShaderNodeCombineXYZ")
    nt.link(cu, cmb.inputs[0])
    nt.link(cv, cmb.inputs[1])
    wn = nt.node("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
    nt.link(cmb.outputs[0], wn.inputs["Vector"])
    fu, fv = nt.math("FRACT", uu), nt.math("FRACT", vv)

    def band(v, a, b):
        return nt.math("MULTIPLY", nt.math("GREATER_THAN", v, a), nt.math("LESS_THAN", v, b))
    win = nt.math("MULTIPLY", band(fu, 0.2, 0.8), band(fv, 0.25, 0.8))
    on = nt.math("MULTIPLY", win, nt.math("LESS_THAN", wn.outputs["Value"], lit_p))
    hue = nt.node("ShaderNodeValToRGB")
    hue.color_ramp.elements[0].color = (1.0, 0.62, 0.30, 1)
    hue.color_ramp.elements[1].color = (0.45, 0.85, 1.0, 1)
    e2 = hue.color_ramp.elements.new(0.5)
    e2.color = (1.0, 0.35, 0.8, 1)
    sepc = nt.node("ShaderNodeSeparateXYZ")
    nt.link(wn.outputs["Color"], sepc.inputs[0])
    nt.link(sepc.outputs[1], hue.inputs[0])
    p = principled(nt, **{"Base Color": wall, "Roughness": 0.6})
    nt.link(hue.outputs[0], p.inputs["Emission Color"])
    nt.link(nt.math("MULTIPLY", on, k), p.inputs["Emission Strength"])
    return m


# ------------------------------------------------------------------ geometry accumulators
class Acc:
    def __init__(self, name, mat):
        self.name, self.mat = name, mat
        self.v, self.f, self.uv = [], [], []

    def quad(self, o, u, v, uvs=None):
        """Quad o, o+u, o+u+v, o+v with UV in metres (or uvs=(umax, vmax))."""
        i = len(self.v)
        o, u, v = Vector(o), Vector(u), Vector(v)
        self.v += [tuple(o), tuple(o + u), tuple(o + u + v), tuple(o + v)]
        self.f.append((i, i + 1, i + 2, i + 3))
        um, vm = uvs if uvs else (u.length, v.length)
        self.uv += [(0, 0), (um, 0), (um, vm), (0, vm)]

    def box(self, x0, x1, y0, y1, z0, z1, faces="fblrtd", uvs=None):
        if "f" in faces:
            self.quad((x0, y0, z0), (x1 - x0, 0, 0), (0, 0, z1 - z0), uvs)       # faces -y (toward camera)
        if "b" in faces:
            self.quad((x1, y1, z0), (x0 - x1, 0, 0), (0, 0, z1 - z0), uvs)
        if "l" in faces:
            self.quad((x0, y1, z0), (0, y0 - y1, 0), (0, 0, z1 - z0), uvs)
        if "r" in faces:
            self.quad((x1, y0, z0), (0, y1 - y0, 0), (0, 0, z1 - z0), uvs)
        if "t" in faces:
            self.quad((x0, y0, z1), (x1 - x0, 0, 0), (0, y1 - y0, 0), uvs)
        if "d" in faces:
            self.quad((x0, y1, z0), (x1 - x0, 0, 0), (0, y0 - y1, 0), uvs)

    def obox(self, c, ax, ay, az, faces="fblrtd"):
        """Oriented box: centre c, half-axis vectors."""
        c, ax, ay, az = map(Vector, (c, ax, ay, az))
        P = lambda sx, sy, sz: c + ax * sx + ay * sy + az * sz
        if "f" in faces:
            self.quad(P(-1, -1, -1), ax * 2, az * 2)
        if "b" in faces:
            self.quad(P(1, 1, -1), -ax * 2, az * 2)
        if "l" in faces:
            self.quad(P(-1, 1, -1), -ay * 2, az * 2)
        if "r" in faces:
            self.quad(P(1, -1, -1), ay * 2, az * 2)
        if "t" in faces:
            self.quad(P(-1, -1, 1), ax * 2, ay * 2)
        if "d" in faces:
            self.quad(P(-1, 1, -1), ax * 2, -ay * 2)

    def tube(self, p0, p1, r, n=6):
        a, b = Vector(p0), Vector(p1)
        d = (b - a)
        dn = d.normalized()
        up = Vector((0, 0, 1)) if abs(dn.z) < 0.9 else Vector((1, 0, 0))
        e1 = dn.cross(up).normalized()
        e2 = dn.cross(e1).normalized()
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            o = a + (e1 * math.cos(t0) + e2 * math.sin(t0)) * r
            q = a + (e1 * math.cos(t1) + e2 * math.sin(t1)) * r
            self.quad(o, q - o, d, uvs=(1, 1))

    def build(self):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        uvl = me.uv_layers.new(name="UVMap")
        k = 0
        for poly in me.polygons:
            for li in poly.loop_indices:
                uvl.data[li].uv = self.uv[li]
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        sc.collection.objects.link(ob)
        me.materials.append(self.mat)
        return ob


ACC = {}


def acc(name, mat=None):
    if name not in ACC:
        ACC[name] = Acc(name, mat)
    return ACC[name]


def flush():
    for a in ACC.values():
        a.build()
    ACC.clear()


def add_light(kind, loc, rot, col, power, size=1.0, size_y=None, name="L", spot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.color = col
    ld.energy = power
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size_y or size
    elif kind == "SPOT":
        ld.shadow_soft_size = size
        ld.spot_size = spot or 1.2
        ld.spot_blend = 0.5
    else:
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def aim(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------ materials
FAC = [mat_facade("fac_a", hexl("#7a6670"), (0.0, 0.0, 0.0)),
       mat_facade("fac_b", hexl("#52606e"), (0.37, 0.21, 0.0)),
       mat_facade("fac_c", hexl("#6e6254"), (0.71, 0.55, 0.0)),
       mat_facade("fac_d", hexl("#5e5678"), (0.13, 0.83, 0.0))]
M_ROAD = mat_ground("road", (0.018, 0.018, 0.022), tile=0, puddle_k=0.50)
M_PAVE = mat_ground("pave", (0.07, 0.065, 0.07), tile=0.9, puddle_k=0.46)
M_KERB = mat_simple("kerb", hexl("#7a7870"), 0.5)
M_DARK = mat_simple("darkmetal", hexl("#17181c"), 0.45, 0.8)
M_STEEL = mat_simple("steel", hexl("#3e444c"), 0.4, 0.85)
M_CONC = mat_simple("conc", hexl("#4a4844"), 0.7)
M_WINDARK = mat_simple("windark", hexl("#07080d"), 0.35, 0.0)
M_CABLE = mat_simple("cable", (0.01, 0.01, 0.012), 0.35)
M_ROOF = mat_simple("roofstuff", hexl("#5c5a58"), 0.6, 0.3)
M_FOYER = mat_simple("foyer", hexl("#2c2a30"), 0.5)
M_TOWER = [mat_citywin("tower%d" % i, hexl(c), lit_p=lp) for i, (c, lp) in enumerate((("#161a26", 0.30), ("#1a1822", 0.22), ("#12202a", 0.34)))]

LIT = {}


def lit(name, hexc, k):
    if name not in LIT:
        LIT[name] = mat_emit(name, hexl(hexc), k)
    return LIT[name]


# ------------------------------------------------------------------ the street, tower, alley
def ground():
    r = acc("road", M_ROAD)
    r.quad((-140, 2.0, 0), (300, 0, 0), (0, Y_KERB - 2.0, 0), uvs=(1, 1))
    r.quad((-140, Y_BACK, 0), (300, 0, 0), (0, 160, 0), uvs=(1, 1))
    p = acc("pave", M_PAVE)
    p.quad((-140, Y_KERB, 0.18), (300, 0, 0), (0, YS - Y_KERB, 0), uvs=(1, 1))
    p.quad((XA0, YS, 0.18), (XA1 - XA0, 0, 0), (0, Y_ST0 - YS, 0), uvs=(1, 1))
    acc("kerb", M_KERB).quad((-140, Y_KERB, 0), (300, 0, 0), (0, 0, 0.18), uvs=(1, 1))
    # road paint: dashes and a crossing at the right (emissive-free, wet-white)
    lp = acc("lanepaint", mat_simple("lanepaint", hexl("#8a8780"), 0.35))
    for x0 in range(-60, 100, 8):
        lp.quad((x0, 9.0, 0.005), (3.4, 0, 0), (0, 0.22, 0), uvs=(1, 1))
    for k in range(10):
        lp.quad((14 + k * 0.85, 4.6, 0.005), (0.45, 0, 0), (0, 3.6, 0), uvs=(1, 1))


def wall(x0, x1, y0, y1, z0, z1, fi, faces="fblrt"):
    acc("fac%d" % fi, FAC[fi]).box(x0, x1, y0, y1, z0, z1, faces)


def windows(face_y, xs, zs, w, h, lit_p, seed, frame=True):
    r = random.Random(seed)
    pal = [("#ffcf8a", 12.0), ("#ffb36b", 12.0), ("#9ff3ff", 10.0), ("#ff7ad1", 10.0), ("#ffe3b0", 11.0)]
    for x in xs:
        for z in zs:
            on = r.random() < lit_p
            if on:
                c, k = r.choice(pal)
                acc("w_" + c, mat_emit("w_" + c, hexl(c), k)).quad((x, face_y - 0.03, z), (w, 0, 0), (0, 0, h), uvs=(1, 1))
            else:
                acc("windark", M_WINDARK).quad((x, face_y - 0.03, z), (w, 0, 0), (0, 0, h), uvs=(1, 1))
            if frame:
                acc("wframe", M_DARK).box(x - 0.08, x + w + 0.08, face_y - 0.20, face_y, z - 0.12, z, "ftl")


def tower():
    top = 42.0
    # shop tower (left): front wall with the foyer recess
    wall(-70, RX0, YS, YS + 0.4, 0.18, top, 0, "fblt")
    wall(RX1, XA0, YS, YS + 0.4, 0.18, top, 0, "fblt")
    wall(RX0, RX1, YS, YS + 0.4, RZ, top, 0, "fblt")
    wall(XA0 - 0.4, XA0, YS, 60, 0.18, top, 1, "r")                     # alley wall (+x facing)
    # recess interior
    rc = acc("foyer", M_FOYER)
    rc.quad((RX0, YS + RD, 0.18), (RX1 - RX0, 0, 0), (0, 0, RZ - 0.18), uvs=(1, 1))
    rc.quad((RX0, YS + RD, 0.18), (0, -RD, 0), (0, 0, RZ - 0.18), uvs=(1, 1))
    rc.quad((RX1, YS, 0.18), (0, RD, 0), (0, 0, RZ - 0.18), uvs=(1, 1))
    rc.quad((RX0, YS + RD, RZ), (RX1 - RX0, 0, 0), (0, -RD, 0), uvs=(1, 1))
    acc("foyerfloor", M_PAVE).quad((RX0, YS, 0.19), (RX1 - RX0, 0, 0), (0, RD, 0), uvs=(1, 1))
    # cyan display screens + lit door at the back of the recess, soffit strip
    x = RX0 + 0.4
    for k in range(4):
        w = 0.9
        hz = 1.0 + 0.5 * (k % 2)
        acc("scr", mat_emit("scr", hexl("#4fe8ff"), 5.0)).quad((x, YS + RD - 0.05, 0.9), (w, 0, 0), (0, 0, hz), uvs=(1, 1))
        x += w + 0.25
    acc("door", mat_emit("door", hexl("#7ffcf0"), 6.0)).quad((RX1 - 1.6, YS + RD - 0.05, 0.2), (1.1, 0, 0), (0, 0, 2.3), uvs=(1, 1))
    acc("soffit", mat_emit("soffit", hexl("#e8fbff"), 7.0)).quad((RX0 + 0.3, YS + 0.5, RZ - 0.05), (RX1 - RX0 - 0.6, 0, 0), (0, 0.12, 0), uvs=(1, 1))
    acc("counter", M_DARK).box(RX0 + 0.2, RX1 - 2.1, YS + RD - 0.8, YS + RD - 0.1, 0.2, 0.85, "fti")
    # windows: left of the sign and right of it
    windows(YS + 0.0, [x for x in range(-40, -12, 3)], [4.2 + 3.3 * j for j in range(9)], 1.2, 1.5, 0.45, "twl")
    windows(YS + 0.0, [-6.4, -4.8], [8.0, 11.3, 14.6, 17.9, 21.2, 24.5], 1.1, 1.5, 0.5, "twr")
    windows(YS + 0.0, [-11.6 - 2.2 * k for k in range(1)], [4.0, 7.3], 1.2, 1.5, 0.5, "twm")
    # sign brackets + housing behind the plate
    hs = acc("signhousing", M_DARK)
    hs.box(SX0 - 0.12, SX1 + 0.12, D_SIGN + 0.02, YS, SZ0 - 0.12, SZ1 + 0.12, "ftlr")
    for z in (SZ0 + 0.6, (SZ0 + SZ1) / 2, SZ1 - 0.6):
        for x in (SX0 + 0.3, SX1 - 0.3):
            hs.box(x - 0.07, x + 0.07, D_SIGN + 0.05, YS, z - 0.07, z + 0.07, "ft")
    # fire escape on the right of the tower facade
    fe = acc("fireescape", M_STEEL)
    zs = [4.4 + 3.4 * k for k in range(5)]
    for k, z in enumerate(zs):
        fe.box(-6.6, -2.3, YS - 1.5, YS - 0.05, z - 0.06, z, "ftbl")
        fe.box(-6.6, -2.3, YS - 1.5, YS - 1.45, z, z + 0.95, "f")          # rail
        fe.box(-6.6, -6.55, YS - 1.5, YS - 0.05, z, z + 0.95, "l")
        if k < len(zs) - 1:
            n = 15
            for s in range(n):
                t = s / n
                xx = (-2.7 - 3.6 * t) if k % 2 == 0 else (-6.3 + 3.6 * t)
                fe.box(xx - 0.12, xx + 0.12, YS - 1.5, YS - 0.8, z + (zs[k + 1] - z) * (s + 1) / n - 0.05, z + (zs[k + 1] - z) * (s + 1) / n, "ft")
    # a few cables on the tower, dark bundle conduit down the alley edge
    acc("conduit", M_STEEL).tube((XA0 + 0.1, YS - 0.1, 0.2), (XA0 + 0.1, YS - 0.1, 30), 0.06, 6)


def alley():
    st = acc("stairs", mat_simple("stairs", hexl("#4a4640"), 0.35))
    n = 24
    for i in range(n):
        y = Y_ST0 + (Y_ST1 - Y_ST0) * i / n
        z = 0.18 + (Z_LAND - 0.18) * (i + 1) / n
        st.box(XA0 + 0.3, XA1 - 0.3, y, y + (Y_ST1 - Y_ST0) / n + 0.02, 0.0, z, "ft")
    acc("landing", M_CONC).box(XA0, XA1, Y_ST1, Y_BACK, 0.0, Z_LAND, "ft")
    for x in (XA0 + 0.35, XA1 - 0.35):
        ang = math.atan2(Z_LAND, Y_ST1 - Y_ST0)
        L = math.hypot(Y_ST1 - Y_ST0, Z_LAND) / 2
        acc("rail", M_STEEL).obox((x, (Y_ST0 + Y_ST1) / 2, Z_LAND / 2 + 1.0), (0.03, 0, 0), (0, math.cos(ang) * L, math.sin(ang) * L), (0, -math.sin(ang) * 0.04, math.cos(ang) * 0.04))
        acc("alley_strip", mat_emit("alley_strip", hexl("#62f0d8"), 9.0)).obox((x, (Y_ST0 + Y_ST1) / 2, Z_LAND / 2 + 0.35), (0.02, 0, 0), (0, math.cos(ang) * L, math.sin(ang) * L), (0, -math.sin(ang) * 0.03, math.cos(ang) * 0.03))
    # closing wall + lit door
    wall(-14, 16, Y_BACK, Y_BACK + 1, 0, 30, 3, "fl")
    acc("door2", mat_emit("door2", hexl("#7ffcf0"), 9.0)).quad((-1.0, Y_BACK - 0.04, Z_LAND), (1.3, 0, 0), (0, 0, 2.3), uvs=(1, 1))
    # right alley wall (front building side and the wing behind)
    wall(XA1, XA1 + 0.4, YFB, Y_BACK, 0.18, 14.0, 2, "l")
    # alley glyph boxes (decorative lit signs on the walls)
    for (y, z, c) in ((YS + 3.5, 4.6, "#ff4fb4"), (YS + 9.0, 6.8, "#7dffb0"), (YS + 14.0, 8.0, "#4fe8ff")):
        acc("glyph" + c, mat_emit("glyph" + c, hexl(c), 7.0)).quad((XA0 + 0.03, y, z), (0, 1.6, 0), (0, 0, 0.6), uvs=(1, 1))
    # steam vent box
    acc("vent", M_STEEL).box(XA0 + 0.1, XA0 + 0.9, YS + 2.0, YS + 2.8, 0.18, 0.9, "fblrt")


def front_building():
    wall(XA1, 17.0, YF, YFB, 0.18, HF, 2, "fblt")
    wall(17.0, 90, YF, YFB + 2, 0.18, 18.0, 1, "fblt")                   # the taller run to the right
    wall(-70, XA0, YS + 0.4, YS + 40, 0.18, 42, 3, "")
    # shutters (bombed), the second half open
    shx = [2.5, 7.0, 11.5]
    for i, x0 in enumerate(shx):
        w, hh = 4.2, 2.9
        m = mat_paint_panel("shutter%d" % i, i)
        z0 = 0.18 + (1.1 if i == 1 else 0.0)
        a = Acc("shutter%d" % i, m)
        a.quad((x0, YF - 0.08, z0), (w, 0, 0), (0, 0, hh - (1.1 if i == 1 else 0.0)), uvs=(1, 1))
        a.build()
        acc("shbox", M_DARK).box(x0 - 0.15, x0 + w + 0.15, YF - 0.42, YF, 3.08, 3.45, "fldt")
        acc("shfrm", M_STEEL).box(x0 - 0.12, x0, YF - 0.12, YF, 0.18, 3.1, "fl")
        acc("shfrm", M_STEEL).box(x0 + w, x0 + w + 0.12, YF - 0.12, YF, 0.18, 3.1, "fr")
        if i == 1:
            acc("shoplight", mat_emit("shoplight", hexl("#ffb860"), 4.0)).quad((x0, YF - 0.02, 0.18), (w, 0, 0), (0, 0, 1.1), uvs=(1, 1))
    # right-end door/shutter of the tall run is a 4th and 5th shutter further right
    for j, x0 in enumerate([18.5, 23.5, 28.5, 33.5]):
        a = Acc("shutterR%d" % j, mat_paint_panel("shutterR%d" % j, 3 + j))
        a.quad((x0, YF - 0.08, 0.18), (4.4, 0, 0), (0, 0, 3.2), uvs=(1, 1))
        a.build()
        acc("shbox", M_DARK).box(x0 - 0.15, x0 + 4.55, YF - 0.4, YF - 0.05, 3.4, 3.75, "fldt")
    # magenta neon strip under the cornice, cornice, ledge
    acc("cornice", M_DARK).box(XA1 - 0.4, 17.0, YF - 0.5, YFB, HF - 0.05, HF + 0.4, "fflt")
    acc("ledge", mat_emit("ledge", hexl("#ff4fb4"), 22.0)).quad((XA1, YF - 0.52, HF - 0.14), (15.0, 0, 0), (0, 0, 0.09), uvs=(1, 1))
    # awning (stripes) over the right shutter
    aw = acc("awning", mat_simple("awning", hexl("#8a2e3e"), 0.7))
    aw.obox((13.6, YF - 0.9, 3.5), (2.3, 0, 0), (0, 0.9, -0.28), (0, 0.012, 0.03), "ftbl")
    # AC units, pipes, roof clutter
    for x in (5.6, 9.9):
        acc("ac", M_ROOF).box(x, x + 0.95, YF - 0.6, YF, 4.4, 5.05, "fltrd")
    for x in (XA1 + 0.35, 16.6):
        acc("pipe", M_STEEL).tube((x, YF - 0.15, 0.18), (x, YF - 0.15, HF), 0.08, 6)
    acc("pipe", M_STEEL).tube((XA1 + 0.35, YF - 0.25, 3.8), (16.6, YF - 0.25, 3.8), 0.07, 6)
    x = XA1 + 1.0
    while x < 15:
        w = rng.uniform(0.9, 2.2)
        acc("roof", M_ROOF).box(x, x + w, YF + 0.8, YF + 0.8 + rng.uniform(0.8, 1.8), HF + 0.4, HF + 0.4 + rng.uniform(0.5, 1.4), "fltr")
        x += w + rng.uniform(0.6, 2.4)
    acc("tank", M_ROOF).tube((9.5, 24.0, HF + 0.4), (9.5, 24.0, HF + 3.4), 1.2, 10)
    windows(YF, [20 + 3 * k for k in range(14)], [5.4, 8.7, 12.0, 15.0], 1.2, 1.4, 0.35, "rw")
    windows(YF, [XA1 + 0.7, 5.0, 9.0, 13.0], [HF + 6.0], 1.2, 1.4, 0.3, "rw2")   # building behind
    # corner pole + wall-mounted conduits on the tall run
    acc("conduit", M_STEEL).tube((17.15, YF - 0.15, 0.2), (17.15, YF - 0.15, 18.0), 0.07, 6)


def cityscape():
    r = random.Random("city")
    layers = [(40, 0.7, (30, 60)), (62, 0.85, (40, 85)), (95, 1.0, (50, 110)), (150, 1.3, (70, 150))]
    n = 0
    for (y, sc_, hr) in layers:
        x = -170 - r.uniform(0, 20)
        while x < 220:
            w = r.uniform(9, 22) * sc_
            h = r.uniform(*hr)
            yy = y + r.uniform(-6, 6)
            if y == 40 and -14 < x < 20:   # keep the line of the alley open
                x += w + 4
                continue
            acc("tw%d" % (n % 3), M_TOWER[n % 3]).box(x, x + w, yy, yy + w, 0, h, "fblr")
            if r.random() < 0.4:
                acc("tw%d" % (n % 3), M_TOWER[n % 3]).box(x + w * 0.2, x + w * 0.8, yy + w * 0.2, yy + w * 0.8, h, h + r.uniform(6, 18), "fblr")
            if h > 70 and r.random() < 0.6:
                acc("beacon", mat_emit("beacon", hexl("#ff3030"), 30.0)).box(x + w / 2 - 0.5, x + w / 2 + 0.5, yy + w / 2 - 0.5, yy + w / 2 + 0.5, h, h + 1.0, "fblrt")
            n += 1
            x += w + r.uniform(2, 9) * sc_
    # giant holo billboards on two mid towers (pink and cyan blocks)
    for (hx, hy, c) in ((22.0, 60.0, "#ff4fd0"), (-30.0, 58.0, "#56f2ff")):
        acc("billboardbase", M_DARK).box(hx - 1, hx + 19, hy + 1, hy + 18, 0, 38, "fblr")
        rr = random.Random(hx)
        for i in range(8):
            for j in range(5):
                if rr.random() < 0.6:
                    acc("bb" + c, mat_emit("bb" + c, hexl(c), 9.0)).quad((hx + i * 1.7 + 0.2, hy - 0.05, 20 + j * 2.0), (1.2, 0, 0), (0, 0, 1.4), uvs=(1, 1))


# ------------------------------------------------------------------ blade signs, cables, poles, props
SIGN_V = [(i % 8, i // 8) for i in range(24)]


def blade(x, y, z, w, h, cell, rotz=0.0, kind="v", k=9.0, flat=False, wy=None):
    """A lit sign (vertical cell of signs_v, or horizontal of signs_h), double-faced box with a dark frame, slightly tilted."""
    grid = (8, 3) if kind == "v" else (2, 8)
    imname = "signs_v.png" if kind == "v" else "signs_h.png"
    c = cell % (24 if kind == "v" else 16)
    cr = (c % grid[0], c // grid[0]) if kind == "v" else (c % 2, c // 2)
    m = mat_blade("bl_%s_%d" % (kind, c), imname, k, cr, grid)
    depth = 0.28
    for side in (1, -1):
        a = Acc("blade", m)
        if flat:    # facing -y, parallel to the wall
            a.quad((x - w / 2, y - depth / 2, z), (w, 0, 0), (0, 0, h), uvs=(1, 1))
            ob = a.build()
            ob.location = (0, 0, 0)
            break
        # blade perpendicular to the wall (faces +/-x), rotated about z toward the camera
        a.quad((0, -0.5 * w * side + 0 * side, 0), (0, w * side, 0), (0, 0, h), uvs=(1, 1)) if False else None
        a.quad((side * depth / 2, w / 2 * side, 0) if False else (side * depth / 2, -w / 2 * side, 0), (0, w * side, 0), (0, 0, h), uvs=(1, 1))
        ob = a.build()
        ob.location = (x, y, z)
        ob.rotation_euler = (0, 0, rotz)
    fr = Acc("bladeframe", M_DARK)
    if flat:
        fr.box(x - w / 2 - 0.05, x + w / 2 + 0.05, y - depth / 2 + 0.01, y + depth / 2, z - 0.05, z + h + 0.05, "fltrdb")
        o = fr.build()
        return
    fr.box(-depth / 2, depth / 2 - 0.02, -w / 2 - 0.04, w / 2 + 0.04, -0.05, h + 0.05, "fblrtd")
    o = fr.build()
    o.location = (x, y, z)
    o.rotation_euler = (0, 0, rotz)
    # bracket to the wall
    acc("bracket", M_DARK).box(x - 0.04, x + 0.04, y, (wy if wy else (YS if y > YF + 1.4 else YF)), z + h * 0.2, z + h * 0.2 + 0.07, "fblrt")


def wing():
    """The taller run behind the front building (right of the alley): dense Tokyo-canyon face with blades, windows, boards."""
    X0, X1, Y0 = XA1 + 0.4, 60.0, YFB + 1.0
    wall(X0, X1, Y0, Y0 + 12, 0.18, 26.0, 1, "fblt")
    windows(Y0, [X0 + 1.0 + 2.6 * k for k in range(18)], [HF + 4.2 + 3.4 * j for j in range(5)], 1.1, 1.3, 0.5, "wing")
    r = random.Random(99)
    for k in range(13):
        x = X0 + 1.5 + k * 2.1 + r.uniform(-0.3, 0.3)
        z = r.uniform(HF + 2.0, 21.0)
        if r.random() < 0.3:
            blade(x, Y0 - 0.15, z, r.uniform(2.4, 3.6), 0.95, r.randrange(16), 0, "h", flat=True, k=10.0)
        else:
            blade(x, Y0 - 1.0, z, 1.0, r.uniform(2.8, 5.0), r.randrange(24), r.uniform(0.2, 0.6), k=10.0, wy=Y0)
    # taller backdrop buildings (with their own lit boards) so the canyon walls close in
    wall(X0 + 6, X1 + 40, Y0 + 14, Y0 + 24, 0.18, 52.0, 0, "fblt")
    windows(Y0 + 14, [X0 + 8 + 2.8 * k for k in range(14)], [10 + 3.5 * j for j in range(10)], 1.3, 1.6, 0.4, "wing2")
    for k in range(8):
        blade(X0 + 9 + k * 3.7, Y0 + 13.0, r.uniform(10, 36), 1.1, r.uniform(3.4, 6.0), r.randrange(24), r.uniform(0.2, 0.5), k=10.0, wy=Y0 + 14)
    # lit billboard ad panels (pink / cyan) high on the wing
    for (x, z, c) in ((X0 + 11, 22.0, "#ff4fb4"), (X0 + 29, 17.5, "#4fe8ff")):
        acc("ad" + c, mat_emit("ad" + c, hexl(c), 10.0)).quad((x, Y0 - 0.05, z), (4.0, 0, 0), (0, 0, 2.2), uvs=(1, 1))


def doorframe():
    """The MAINFRAME shopfront (under the hero sign): sticker-bombed door posts and lintel, a roll shutter half up, a lit counter
    glimpse under it, a red fascia board. This is the shop; the centre stall is demoted."""
    sm = mat_box_tex("door_stick", "stickers.png", hexl("#2a2c34"), tile=(1 / 4.0, 1 / 4.0, 1 / 4.0), emit=1.0)
    d = Acc("doorframe", sm)
    d.box(RX0 - 0.32, RX0, YS - 0.38, YS, 0.18, RZ + 0.38, "fltr")
    d.box(RX1, RX1 + 0.32, YS - 0.38, YS, 0.18, RZ + 0.38, "fltr")
    acc("lintel", M_DARK).box(RX0 - 0.32, RX1 + 0.32, YS - 0.38, YS, RZ, RZ + 0.38, "flrd")
    d.build()
    # roll shutter pulled half up: the top 1.2 m of the opening, lightly bombed
    a = Acc("mf_shutter", mat_paint_panel("mf_shutter", 7))
    a.quad((RX0, YS - 0.1, RZ - 1.25), (RX1 - RX0, 0, 0), (0, 0, 1.25), uvs=(1, 1))
    a.build()
    acc("mf_roll", M_DARK).box(RX0, RX1, YS - 0.3, YS - 0.05, RZ - 0.1, RZ + 0.05, "fd")
    acc("mf_bar", M_STEEL).box(RX0, RX1, YS - 0.14, YS - 0.06, RZ - 1.32, RZ - 1.25, "fd")
    # lit counter glimpse under the shutter: warm strip, shelves of stock, pink back light
    acc("mf_strip", mat_emit("mf_strip", hexl("#ffd9a8"), 16.0)).quad((RX0 + 0.3, YS + 0.7, RZ - 1.3), (RX1 - RX0 - 2.4, 0, 0), (0, 0.12, 0), uvs=(1, 1))
    for i in range(7):
        c = ("#ff4fb4", "#4fe8ff", "#ffe27a")[i % 3]
        acc("mf_stock" + c, mat_emit("mf_stock" + c, hexl(c), 9.0)).quad((RX0 + 0.5 + i * 0.7, YS + RD - 0.08, 1.05), (0.5, 0, 0), (0, 0, 0.35), uvs=(1, 1))
    acc("mf_back", mat_emit("mf_back", hexl("#ff6a8a"), 3.0)).quad((RX0 + 0.1, YS + RD - 0.09, 0.9), (RX1 - RX0 - 2.0, 0, 0), (0, 0, 0.6), uvs=(1, 1))
    # fascia board right of the plate
    fm = mat_blade("fascia", "mainframe_h.png", 12.0, (0, 0), (1, 1))
    f = Acc("fascia", fm)
    f.quad((-7.0, YS - 0.06, 3.2), (3.9, 0, 0), (0, 0, 0.975), uvs=(1, 1))
    f.build()
    acc("fasciaframe", M_DARK).box(-7.08, -3.02, YS - 0.2, YS - 0.07, 3.12, 4.25, "ltrd")


def upper():
    """Upper half: lit windows, AC units and one more blade sign, no graffiti up there."""
    r = random.Random(31)
    windows(YS, [-10.6, -8.6, -6.6, -4.6], [16.8, 19.8, 22.8, 25.8, 29.0], 1.2, 1.5, 0.55, "twu")
    for (x, z) in ((-4.4, 17.2), (-8.9, 20.2), (-6.3, 26.2), (-10.5, 23.2)):
        acc("tac", M_ROOF).box(x, x + 0.95, YS - 0.6, YS, z, z + 0.65, "fltrd")
    Y0 = YFB + 1.0
    for k in range(16):
        if r.random() < 0.5:
            x = XA1 + 1.4 + 2.6 * k
            z = HF + 3.1 + 3.4 * r.randrange(4)
            acc("wac", M_ROOF).box(x, x + 0.9, Y0 - 0.55, Y0, z, z + 0.6, "fltrd")
    blade(-3.2, YS - 1.3, 21.5, 0.9, 3.4, 12, 0.12)
    blade(XA1 + 17.0, Y0 - 1.0, 15.0, 1.0, 4.4, 18, 0.35, k=10.0, wy=Y0)
    blade(XA1 + 5.0, Y0 - 1.0, 17.5, 1.0, 3.8, 2, 0.3, k=10.0, wy=Y0)


def signs():
    r = random.Random(77)
    # strip of tower facade in frame (right of the hero sign)
    blade(-10.6, YS - 1.2, 8.0, 0.9, 3.4, 7, -0.25)
    blade(-4.2, YS - 0.2, 7.4, 2.8, 0.9, 5, 0, "h", flat=True)
    blade(-11.5, YS - 1.3, 4.0, 0.9, 3.6, 14, -0.35)
    blade(-2.4, YS - 1.4, 16.0, 0.9, 3.8, 20, 0.1)
    blade(-2.4, YS - 1.4, 9.5, 0.9, 3.2, 4, 0.15)
    blade(XA1 - 0.4, YF - 1.0, 3.7, 0.9, 3.0, 1, -0.2)
    blade(XA1 - 0.4, YF - 1.0, 9.0, 0.9, 3.4, 13, -0.3)
    blade(17.2, YF - 0.9, 4.6, 0.9, 4.2, 17, 0.3)
    blade(7.4, YF - 0.3, 3.6, 4.2, 0.9, 7, 0, "h", flat=True, k=3.0)
    blade(XA0 + 0.5, YS + 6, 6.5, 0.7, 2.4, 21, 1.4)
    blade(XA1 - 0.5, 33.0, 7.0, 0.7, 2.6, 8, -1.4)
    blade(XA0 + 0.5, YS + 16, 9.0, 0.7, 2.6, 9, 1.4)


def signs_old():
    r = random.Random(77)
    # tower, left of the hero sign: blades at varied heights, rotated toward the camera
    n = 0
    for x in [-48, -44.5, -41, -38, -35.5, -33, -30.5, -28, -25.5, -23, -20.5, -18, -15.5, -13]:
        for lvl in range(r.choice([1, 2, 2])):
            z = 3.4 + lvl * r.uniform(5.0, 7.5) + r.uniform(-0.3, 1.5)
            h = r.uniform(2.6, 4.8)
            if r.random() < 0.28:
                blade(x, YS - 0.15, z, r.uniform(2.2, 3.4), 0.9, r.randrange(16), 0, "h", flat=True)
            else:
                blade(x, YS - 0.2 - 0.9, z, 0.9, h, r.randrange(24), r.uniform(-0.55, -0.15))
            n += 1
    # near the hero sign (small, right of the fire escape and left of it, keep the plate clear)
    blade(-11.9, YS - 1.1, 4.2, 0.9, 3.4, 6, -0.30)
    blade(-6.2, YS - 1.6, 10.0, 0.9, 3.2, 4, -0.1)
    blade(-2.5, YS - 1.2, 14.5, 0.9, 3.6, 15, 0.1)
    # front building corner + tall run to the right
    blade(XA1 - 0.4, YF - 1.0, 3.7, 0.9, 3.0, 1, -0.2)
    blade(17.2, YF - 0.9, 4.6, 0.9, 4.2, 17, 0.3)
    for x in [20, 24.5, 28, 32, 36, 40, 45, 50, 56]:
        for lvl in range(r.choice([1, 2, 3])):
            z = 4.5 + lvl * r.uniform(4.0, 5.5)
            if r.random() < 0.3:
                blade(x, YF - 0.2, z, r.uniform(2.2, 3.4), 0.9, r.randrange(16), 0, "h", flat=True)
            else:
                blade(x, YF - 0.6, z, 0.9, r.uniform(2.4, 4.4), r.randrange(24), r.uniform(0.15, 0.6))
    # shop sign over the shutters: a hanging horizontal
    blade(7.4, YF - 0.3, 3.6, 5.2, 0.9, 11, 0, "h", k=8.0, flat=True)
    # alley signs
    blade(XA0 + 0.5, YS + 6, 6.5, 0.7, 2.4, 21, 1.4)
    blade(XA1 - 0.5, 30.0, 7.0, 0.7, 2.6, 8, -1.4)
    blade(XA0 + 0.5, YS + 16, 9.0, 0.7, 2.6, 9, 1.4)


def curve_tube(name, pts, r, mat):
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = r
    cd.bevel_resolution = 1
    sp = cd.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1.0)
    ob = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def cable(p0, p1, sag, r=0.03, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t - sag * math.sin(math.pi * t)))
    curve_tube("cable", pts, r, M_CABLE)


def cables():
    r = random.Random(5)
    # alley: two wall-to-wall cables with brackets
    for k, (y, z0, z1) in enumerate(((YS + 1.0, 5.6, 5.0), (YS + 3.6, 6.0, 5.4))):
        cable((XA0, y, z0), (XA1, y + 0.4, z1), 0.7)
        for q, dx in (((XA0, y, z0), 0.12), ((XA1, y + 0.4, z1), -0.12)):
            acc("bracket", M_DARK).box(min(q[0], q[0] + dx), max(q[0], q[0] + dx), q[1] - 0.06, q[1] + 0.06, q[2] - 0.08, q[2] + 0.08, "fltrd")
    # across the street mouth: tower to front building (above the alley)
    for k in range(5):
        cable((XA0, YS + 0.2 + k * 1.2, 7.4 + k * 0.5), (XA1 + 0.3, YF + 0.2 + k * 1.0, 6.8 + k * 0.4), r.uniform(0.6, 1.2))
    # along the street: pole to pole and sign to sign, many sagging runs
    for i in range(34):
        x0 = r.uniform(-60, 55)
        x1 = x0 + r.uniform(5, 16)
        y0 = r.choice([YS - 1.0, 18.8, 18.3, YS - 0.4])
        z0 = r.uniform(3.2, 14.0)
        cable((x0, y0, z0), (x1, y0 + r.uniform(-0.5, 0.5), z0 + r.uniform(-1.2, 1.2)), r.uniform(0.4, 1.6), r.choice([0.02, 0.03, 0.045]))
    # diagonals: from the tall wall across to the front building roof
    for i in range(14):
        cable((r.uniform(-30, -2), YS - 0.5, r.uniform(8, 18)), (r.uniform(4, 40), 18.9, r.uniform(5.5, 9)), r.uniform(0.8, 2.2), 0.025)


def poles():
    # utility pole beside the hero sign, plastered with stickers; and one on the right
    m = mat_box_tex("pole_stick", "stickers.png", hexl("#2c2f35"), tile=(1 / 11.0, 1 / 11.0, 1 / 11.0), emit=1.2)
    a = Acc("pole", m)
    a.box(-6.45, -6.1, 18.75, 19.1, 0.18, 9.5, "fblr")
    a.box(-6.45, -6.1, 18.75, 19.1, 0.18, 9.5, "t")
    a.build()
    m2 = mat_box_tex("pole_stick2", "stickers.png", hexl("#2c2f35"), tile=(1 / 19.0, 1 / 17.0, 1 / 21.0), emit=1.2)
    b = Acc("pole2", m2)
    b.box(12.5, 12.85, 18.75, 19.1, 0.18, 9.0, "fblrt")
    b.build()
    for px, pz in ((-6.28, 9.0), (12.67, 8.6)):
        acc("crossarm", M_DARK).box(px - 1.4, px + 1.4, 18.8, 19.05, pz, pz + 0.12, "fblrt")
        for dx in (-1.1, -0.4, 0.4, 1.1):
            acc("insul", M_STEEL).tube((px + dx, 18.92, pz + 0.12), (px + dx, 18.92, pz + 0.4), 0.05, 5)
    # transformer can + wall-mount light on the pole
    acc("xfmr", M_STEEL).tube((-6.28, 19.5, 7.2), (-6.28, 19.5, 8.4), 0.32, 8)
    # street lamp with a warm head at the right
    acc("lamp", M_DARK).tube((19.2, 18.6, 0.18), (19.2, 18.6, 7.0), 0.09, 6)
    acc("lamp", M_DARK).tube((19.2, 18.6, 7.0), (19.2, 19.9, 7.5), 0.07, 6)
    acc("lamphead", mat_emit("lamphead", hexl("#ffd9a0"), 40.0)).box(18.8, 19.6, 19.6, 20.3, 7.3, 7.45, "fbtdlr")
    add_light("AREA", (19.2, 19.95, 7.2), (math.pi, 0, 0), (1.0, 0.78, 0.5), 900, 0.9, name="lamp")
    # vending machine at the alley mouth, sticker-bombed
    vm = mat_box_tex("vend", "stickers.png", hexl("#2a2f3a"), tile=(1 / 8.0, 1 / 8.0, 1 / 8.0), emit=0.2)
    v = Acc("vend", vm)
    v.box(-3.3, -2.4, 20.6, 21.6, 0.18, 2.1, "blrt")
    v.build()
    acc("vendface", mat_emit("vendface", hexl("#9ff3ff"), 5.0)).quad((-3.2, 20.58, 0.7), (0.7, 0, 0), (0, 0, 1.2), uvs=(1, 1))
    acc("vendface2", mat_emit("vendface2", hexl("#ff7ad1"), 6.0)).quad((-3.2, 20.58, 1.95), (0.7, 0, 0), (0, 0, 0.1), uvs=(1, 1))


def decals():
    """Sticker sheets / wheat-paste around the sign plate (the graffiti 'crowds' the plate)."""
    m = mat_decal("sticker_decal", "stickers.png", 0.2)
    a = Acc("decals", m)
    y = YS - 0.02
    # strips left, right, below and above the plate; sheet mapped 1 tile = 20 m / 2048 px => about 100 px/m
    # use a UV window of the sheet per strip
    def strip(x0, z0, w, h, u0, v0):
        a.quad((x0, y, z0), (w, 0, 0), (0, 0, h), uvs=(1, 1))
        base = len(a.uv) - 4
        s = 0.1
        a.uv[base:base + 4] = [(u0, v0), (u0 + w * s, v0), (u0 + w * s, v0 + h * s), (u0, v0 + h * s)]
    strip(SX0 - 2.0, 2.6, 1.8, 11.0, 0.05, 0.05)
    strip(SX1 + 0.15, 2.6, 1.4, 11.0, 0.40, 0.05)
    strip(SX0 - 0.1, 2.4, SW + 0.2, 1.0, 0.25, 0.65)
    strip(SX0 - 0.1, SZ1 + 0.1, SW + 0.2, 1.3, 0.55, 0.55)
    a.build()


def recycle_bin():
    """The sidewalk RECYCLE BIN: tapered steel drum with the cyan wire grid + lime emblem + tags, lime lid ring."""
    m = bpy.data.materials.new("bin")
    nt = NT(m)
    a = nt.node("ShaderNodeTexImage")
    a.image = img("bin.png", False)
    uv = nt.node("ShaderNodeTexCoord")
    nt.link(uv.outputs["UV"], a.inputs[0])
    p = principled(nt, **{"Roughness": 0.4, "Metallic": 0.5})
    nt.link(a.outputs["Color"], p.inputs["Base Color"])
    nt.link(a.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 0.35
    bx, by = -1.0, 19.9
    seg = 40
    prof = [(0.5, 0.18), (0.68, 1.75)]
    me = bpy.data.meshes.new("bin")
    vs, fs, uvs = [], [], []
    for i in range(seg + 1):
        t = i / seg
        ang = 2 * math.pi * t
        for (r, z) in prof:
            vs.append((bx + r * math.cos(ang), by + r * math.sin(ang), z))
    for i in range(seg):
        a0, a1 = i * 2, (i + 1) * 2
        fs.append((a0, a1, a1 + 1, a0 + 1))
    me.from_pydata(vs, [], fs)
    ul = me.uv_layers.new(name="UVMap")
    for pi, poly in enumerate(me.polygons):
        t0, t1 = pi / seg, (pi + 1) / seg
        corners = [(t0, 0), (t1, 0), (t1, 1), (t0, 1)]
        for k, li in enumerate(poly.loop_indices):
            ul.data[li].uv = corners[k]
    me.update()
    ob = bpy.data.objects.new("bin", me)
    sc.collection.objects.link(ob)
    me.materials.append(m)
    # lid: dark disc + lime emissive ring + inner dark
    acc("binlid", M_DARK).tube((bx, by, 1.73), (bx, by, 1.80), 0.70, 24)
    acc("binring", mat_emit("binring", hexl("#a8ff30"), 14.0)).tube((bx, by, 1.80), (bx, by, 1.815), 0.58, 24)
    acc("bindark", mat_simple("bindark", (0.002, 0.002, 0.003), 0.9)).tube((bx, by, 1.816), (bx, by, 1.825), 0.50, 24)
    # price tag + hanging kraft tag, label slap
    acc("bintag", mat_simple("kraft", hexl("#b88a54"), 0.8)).box(bx + 0.30, bx + 0.70, by - 0.5, by - 0.48, 0.9, 1.15, "f")
    add_light("POINT", (bx, by - 0.4, 2.0), (0, 0, 0), (0.66, 1.0, 0.19), 400, 0.1, name="binlight")


def lathe(name, prof, mat, cx, cy, cz, seg=28, scale=1.0, closed=False):
    me = bpy.data.meshes.new(name)
    vs, fs = [], []
    for i in range(seg):
        ang = 2 * math.pi * i / seg
        for (r, z) in prof:
            vs.append((cx + r * scale * math.cos(ang), cy + r * scale * math.sin(ang), cz + z * scale))
    m = len(prof)
    for i in range(seg):
        j = (i + 1) % seg
        for k in range(m - 1):
            fs.append((i * m + k, j * m + k, j * m + k + 1, i * m + k + 1))
    me.from_pydata(vs, [], fs)
    me.update()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def holo_material(name, c0, c1, alpha=0.55):
    m = bpy.data.materials.new(name)
    nt = NT(m)
    tc = nt.node("ShaderNodeTexCoord")
    sep = nt.node("ShaderNodeSeparateXYZ")
    nt.link(tc.outputs["Object"], sep.inputs[0])
    zz = sep.outputs[2]
    gradient = nt.maprange(zz, 0.0, 1.0, 0.0, 1.0)
    ramp = nt.node("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c0, 1)
    ramp.color_ramp.elements[1].color = (*c1, 1)
    nt.link(gradient, ramp.inputs[0])
    scan = nt.math("SINE", nt.math("MULTIPLY", zz, 260.0))
    scan = nt.maprange(scan, -1.0, 1.0, 0.35, 1.2)
    lw = nt.node("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.3
    rim = nt.math("ADD", 0.6, nt.math("MULTIPLY", lw.outputs["Facing"], -0.0))
    em = nt.node("ShaderNodeEmission")
    nt.link(ramp.outputs[0], em.inputs[0])
    nt.link(nt.math("MULTIPLY", scan, 10.0), em.inputs[1])
    tr = nt.node("ShaderNodeBsdfTransparent")
    mx = nt.node("ShaderNodeMixShader")
    fa = nt.math("ADD", alpha, nt.math("MULTIPLY", lw.outputs["Fresnel"], 0.8), clamp=True)
    nt.link(fa, mx.inputs[0])
    nt.link(tr.outputs[0], mx.inputs[1])
    nt.link(em.outputs[0], mx.inputs[2])
    nt.link(mx.outputs[0], nt.out.inputs["Surface"])
    return m


def hologram():
    """A food holo: floating ramen bowl (bowl, noodles, egg, narutomaki, chopsticks) on a projector pad, scan-lined."""
    cx, cy, cz, S = 17.2, 20.1, 9.7, 1.7      # floating above the RAMEN blade sign, 3rd floor, right of the front building
    mh = holo_material("holo_bowl", (0.2, 0.95, 1.0), (1.0, 0.35, 0.95), 0.5)
    mn = holo_material("holo_noodle", (1.0, 0.8, 0.25), (1.0, 0.45, 0.6), 0.8)
    mg = holo_material("holo_egg", (1.0, 0.95, 0.7), (1.0, 0.6, 0.3), 0.8)
    # normalise Z so the gradient runs 0..1 over the holo: build the holo at origin, then move
    bowl = [(0.0, 0.0), (0.18, 0.0), (0.30, 0.04), (0.42, 0.14), (0.50, 0.26), (0.52, 0.30), (0.48, 0.30), (0.46, 0.26), (0.38, 0.14), (0.26, 0.07), (0.0, 0.05)]
    objs = [lathe("holo_bowl", bowl, mh, 0, 0, 0.0, 36, 1.0)]
    # broth surface + egg halves + narutomaki
    objs.append(lathe("holo_broth", [(0.0, 0.26), (0.44, 0.26)], mh, 0, 0, 0.0, 36, 1.0))
    # noodles: waving ropes over the broth
    for k in range(9):
        pts = []
        ph = k * 0.7
        for i in range(44):
            t = i / 43
            ang = ph + t * 6.0
            rr = 0.38 * (1 - 0.5 * t) * (0.6 + 0.4 * math.sin(t * 9 + k))
            pts.append((rr * math.cos(ang), rr * math.sin(ang), 0.30 + 0.12 * math.sin(t * 14 + k) + 0.16 * t))
        objs.append(curve_tube("holo_noodle", pts, 0.012, mn))
    # lift noodles: a few long strands going up (chopsticks pulling)
    for k in range(4):
        pts = []
        for i in range(30):
            t = i / 29
            pts.append((0.12 + 0.03 * math.sin(t * 20 + k), 0.05 + 0.02 * math.cos(t * 17 + k) + 0.02 * k, 0.34 + 0.7 * t))
        objs.append(curve_tube("holo_noodle", pts, 0.010, mn))
    for (ex, ey) in ((0.2, -0.15), (-0.18, 0.1)):
        objs.append(lathe("holo_egg", [(0.0, 0.0), (0.08, 0.01), (0.14, 0.05), (0.15, 0.09), (0.08, 0.13), (0.0, 0.14)], mg, ex, ey, 0.30, 16, 1.0))
    for sgn in (1, -1):
        objs.append(curve_tube("holo_stick", [(0.1 + sgn * 0.02, 0.18, 1.05), (0.36 + sgn * 0.02, -0.1, 0.55)], 0.012, mh))
    # steam wisps
    for k in range(5):
        pts = [(0.15 * math.sin(i * 0.5 + k) , 0.1 * math.cos(i * 0.4 + k), 0.45 + i * 0.075) for i in range(14)]
        objs.append(curve_tube("holo_steam", pts, 0.008, mh))
    for ob in objs:
        ob.scale = (S, S, S)
        ob.location = (cx, cy, cz + ob.location.z)
    # small emitter on top of the RAMEN blade sign, and a faint projector cone up to the bowl
    ez = 8.9
    acc("emitter", M_DARK).box(cx - 0.16, cx + 0.16, cy - 0.16, cy + 0.16, ez - 0.12, ez + 0.02, "fblrt")
    acc("emitled", mat_emit("emitled", hexl("#56f2ff"), 30.0)).box(cx - 0.07, cx + 0.07, cy - 0.17, cy - 0.15, ez - 0.08, ez - 0.02, "f")
    lathe("holo_cone", [(0.08, ez + 0.02), (0.95, cz - 0.1)], holo_material("holo_cone", (0.2, 0.9, 1.0), (1.0, 0.4, 0.9), 0.16), cx, cy, 0, 28, 1.0)
    add_light("POINT", (cx - 0.4, cy - 1.2, cz + 0.6), (0, 0, 0), (0.45, 0.95, 1.0), 1200, 0.4, name="holo_c")
    add_light("POINT", (cx + 0.5, cy - 1.2, cz + 0.4), (0, 0, 0), (1.0, 0.35, 0.8), 700, 0.4, name="holo_m")


# ------------------------------------------------------------------ lights, world, camera
def lighting():
    mid = (SX0 + SX1) / 2
    # the hero sign: red spill on the facade, the pole, the street
    a = add_light("AREA", (mid, D_SIGN - 3.0, (SZ0 + SZ1) / 2), (0, 0, 0), (1.0, 0.10, 0.12), 26000, 3.0, 10.0, name="sign_spill")
    aim(a, (mid, YS, (SZ0 + SZ1) / 2))
    a = add_light("AREA", (mid, D_SIGN - 2.0, SZ0 + 0.5), (0, 0, 0), (1.0, 0.12, 0.14), 5000, 5.0, 2.0, name="sign_floor")
    aim(a, (mid, 18.0, 0.0))
    # cyan alley glow + stair
    a = add_light("AREA", (0.0, 40.0, 6.5), (0, 0, 0), (0.25, 1.0, 0.85), 9000, 2.5, 2.5, name="alley_door")
    aim(a, (0, 30, 3.0))
    a = add_light("AREA", (0.0, 30.0, 8.0), (0, 0, 0), (0.30, 0.95, 0.85), 3000, 2.0, 4.0, name="alley_down")
    aim(a, (0, 30, 0))
    # magenta strip on the front building
    a = add_light("AREA", (9.0, YF - 1.2, HF - 0.3), (0, 0, 0), (1.0, 0.25, 0.7), 5200, 15.0, 0.3, name="strip")
    aim(a, (9.0, 10.0, 0.0))
    # foyer cyan, warm shop-light, pink fill from the far billboard
    a = add_light("AREA", (-6.0, YS - 0.5, 2.5), (0, 0, 0), (1.0, 0.85, 0.8), 9000, 5.0, 1.0, name="foyer")
    aim(a, (-6.0, 14.0, 0.0))
    a = add_light("AREA", (7.0, YF - 1.0, 1.0), (0, 0, 0), (1.0, 0.7, 0.35), 1600, 4.0, 1.0, name="shopwarm")
    aim(a, (7.0, 12.0, 0.2))
    # gooseneck shop lamps over each bombed shutter (the pieces have to read)
    for x0, c in ((2.5, (1.0, 0.85, 0.65)), (7.0, (0.7, 0.9, 1.0)), (11.5, (1.0, 0.6, 0.85))):
        a = add_light("AREA", (x0 + 2.1, YF - 1.3, 3.9), (0, 0, 0), c, 2600, 4.0, 0.8, name="shutter_lamp")
        aim(a, (x0 + 2.1, YF, 1.4))
    # general violet / teal canyon fill from the upper street (as neon haze would)
    a = add_light("AREA", (-18.0, 8.0, 20.0), (0, 0, 0), (0.55, 0.30, 1.0), 42000, 30.0, 14.0, name="haze_v")
    aim(a, (-14.0, 22.0, 4.0))
    a = add_light("AREA", (24.0, 10.0, 20.0), (0, 0, 0), (0.25, 0.75, 1.0), 36000, 30.0, 14.0, name="haze_c")
    aim(a, (24.0, 20.0, 4.0))
    # street-side neon fill (the signs across the street, behind the camera): pink-violet on the facades
    a = add_light("AREA", (-4.0, 2.0, 9.0), (0, 0, 0), (1.0, 0.35, 0.85), 30000, 24.0, 10.0, name="street_pink")
    aim(a, (-8.0, 22.0, 6.0))
    a = add_light("AREA", (12.0, 2.0, 8.0), (0, 0, 0), (0.45, 0.8, 1.0), 26000, 24.0, 10.0, name="street_cyan")
    aim(a, (14.0, 21.0, 4.0))
    # world: faint violet sky
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs[0].default_value = (0.05, 0.03, 0.10, 1)
    bg.inputs[1].default_value = 0.35
    # volumetric haze (neon-lit by the lights above)
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.85, 0.70, 1.0, 1)
    vol.inputs["Density"].default_value = 0.0030
    vol.inputs["Anisotropy"].default_value = 0.45
    out = nt.nodes["World Output"]
    nt.links.new(vol.outputs[0], out.inputs["Volume"])


def camera():
    cd = bpy.data.cameras.new("cam")
    cd.lens, cd.sensor_width, cd.sensor_fit = LENS, SENSOR, "HORIZONTAL"
    cd.shift_x, cd.shift_y = SHX, SHY
    cd.clip_start, cd.clip_end = 0.3, 900
    ob = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(ob)
    ob.location = (0, 0, EYE)
    ob.rotation_euler = (math.pi / 2, 0, 0)
    sc.camera = ob


def sign_plane():
    s = Acc("sign", mat_sign_plate())
    s.quad((SX0, D_SIGN, SZ0), (SW, 0, 0), (0, 0, SH), uvs=(1, 1))
    s.build()


def render_setup():
    cy = sc.cycles
    prefs = bpy.context.preferences.addons["cycles"].preferences
    if not CPU:
        prefs.compute_device_type = "HIP"
        try:
            prefs.use_hiprt = False
        except Exception:
            pass
        prefs.refresh_devices()
        for d in prefs.devices:
            d.use = d.type == "HIP"
        cy.device = "GPU"
    else:
        cy.device = "CPU"
        sc.render.threads_mode = "FIXED"
        sc.render.threads = 5
    cy.samples = SPP
    cy.use_adaptive_sampling = False
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 7, 2, 4
    cy.transmission_bounces, cy.volume_bounces = 4, 0
    cy.transparent_max_bounces = 24
    cy.sample_clamp_indirect = 10.0
    cy.sample_clamp_direct = 0.0
    cy.volume_step_rate = 4.0
    cy.time_limit = float(os.environ.get("GS_TIME_LIMIT", "0" if CPU else "1080"))
    cy.volume_max_steps = 64
    print("[gs] devices:", [(d.name, d.type, d.use) for d in prefs.devices], "cy.device", cy.device, "limit", cy.time_limit, flush=True)
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    sc.render.image_settings.color_mode = "RGB"


def main():
    t0 = time.time()
    ground()
    tower()
    alley()
    front_building()
    wing()
    upper()
    cityscape()
    signs()
    cables()
    poles()
    doorframe()
    recycle_bin()
    sign_plane()
    flush()
    hologram()
    flush()
    lighting()
    camera()
    render_setup()
    print("[gs] scene built %.1f s, %d objects" % (time.time() - t0, len(bpy.data.objects)), flush=True)
    sc.render.filepath = OUT + "_beauty.exr"
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    print("[gs] render %.1f s" % (time.time() - t1), flush=True)
    import numpy as np
    im = bpy.data.images.load(OUT + "_beauty.exr")
    w, h = im.size
    buf = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(buf)
    arr = buf.reshape(h, w, 4)[::-1, :, :3].copy()
    np.save(OUT + "_beauty.npy", arr)
    print("[gs] saved", arr.shape, "mean %.4f" % float(arr.mean()), flush=True)


main()
