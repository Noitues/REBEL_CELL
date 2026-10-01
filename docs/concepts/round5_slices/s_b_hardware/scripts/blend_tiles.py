"""Blender 5.2 headless: bevelled, lit hardware tiles (Cycles, orthographic, top-down).

Usage (from build_all.py):
  blender -b --factory-startup --python blend_tiles.py -- <job> <out.png> [samples] [scale]
jobs: sheet | player | enemy | test

Every tile is an Empty at the hub centre; its parts are meshes whose vertices are in the
tile-local frame (axis +Y), so the materials read Object coordinates as the atlas cell UV.
"""
import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["test", "test.png"]
JOB = ARGS[0]
OUTP = os.path.abspath(ARGS[1])
SAMPLES = int(ARGS[2]) if len(ARGS) > 2 else 64
SCALE = float(ARGS[3]) if len(ARGS) > 3 else 1.0


# ---------------------------------------------------------------- scene
def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        pass
    sc.cycles.max_bounces = 8
    sc.cycles.transmission_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.012, 0.010, 0.018, 1)
    bg.inputs[1].default_value = 1.0
    return sc


def camera(sc, cx, cy, ortho, resx, resy):
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_end = 200
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    cam.location = (cx, cy, 30)
    sc.camera = cam
    sc.render.resolution_x = int(resx * SCALE)
    sc.render.resolution_y = int(resy * SCALE)
    sc.render.resolution_percentage = 100


def lights(sc, extent):
    def add(kind, name, loc, energy, color=(1, 1, 1), **kw):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = color
        for k, v in kw.items():
            setattr(ld, k, v)
        ob = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(ob)
        ob.location = loc
        return ob

    sun = add("SUN", "key", (0, 0, 10), 2.0, (1.0, 0.97, 0.93), angle=math.radians(6))
    sun.rotation_euler = (math.radians(38), 0, math.radians(-135))  # from upper-left
    fill = add("SUN", "fill", (0, 0, 10), 0.6, (0.75, 0.85, 1.0), angle=math.radians(20))
    fill.rotation_euler = (math.radians(55), 0, math.radians(60))
    # overhead softbox: what flat metal tops reflect (invisible to the camera)
    me = bpy.data.meshes.new("softbox")
    e = extent * 1.6
    me.from_pydata([(-e, -e, 0), (e, -e, 0), (e, e, 0), (-e, e, 0)], [], [(3, 2, 1, 0)])
    ob = bpy.data.objects.new("softbox", me)
    sc.collection.objects.link(ob)
    ob.location = (0, 0, 45)
    ob.visible_camera = False
    ob.visible_shadow = False
    m = bpy.data.materials.new("softbox")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    # brighter toward the upper-left, with a soft band (the "studio window")
    add_ = nt.nodes.new("ShaderNodeMath")
    add_.operation = "SUBTRACT"
    nt.links.new(sep.outputs["Y"], add_.inputs[0])
    nt.links.new(sep.outputs["X"], add_.inputs[1])
    mr.inputs["From Min"].default_value = -2 * e
    mr.inputs["From Max"].default_value = 2 * e
    mr.inputs["To Min"].default_value = 0.2
    mr.inputs["To Max"].default_value = 1.15
    nt.links.new(add_.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], em.inputs["Strength"])
    em.inputs["Color"].default_value = (1.0, 0.98, 0.96, 1)
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    # low coloured grazing strips: catch the bevels like the reference's neon
    for name, loc, rot, col, pw in (
        ("rim_pink", (-extent * 0.9, extent * 0.2, 1.4), (0, math.radians(-80), 0), (1.0, 0.35, 0.7), 900),
        ("rim_cyan", (extent * 0.9, -extent * 0.2, 1.4), (0, math.radians(80), 0), (0.35, 0.85, 1.0), 700),
    ):
        ob = add("AREA", name, loc, pw * (extent / 6.0), col, shape="RECTANGLE", size=0.4, size_y=extent * 2)
        ob.rotation_euler = rot
        ob.data.specular_factor = 1.0


# ---------------------------------------------------------------- node helpers
def mat_begin(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    return m, nt, bsdf, out


def link(nt, a, b):
    nt.links.new(a, b)


def setv(node, name, v):
    node.inputs[name].default_value = v


def obj_xyz(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    link(nt, tc.outputs["Object"], sep.inputs[0])
    return tc, sep


def tile_uv(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / C.TEX_SIZE, 1 / C.TEX_SIZE, 1)
    mp.inputs["Location"].default_value = (-C.TEX_X0 / C.TEX_SIZE, -C.TEX_Y0 / C.TEX_SIZE, 0)
    link(nt, tc.outputs["Object"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


_IMG = {}


def tex(nt, uv, fname):
    if fname not in _IMG:
        im = bpy.data.images.load(os.path.join(C.WORK, fname))
        im.colorspace_settings.name = "Non-Color"
        _IMG[fname] = im
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = _IMG[fname]
    n.extension = "EXTEND"
    n.interpolation = "Cubic"
    link(nt, uv, n.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    link(nt, n.outputs["Color"], sep.inputs[0])
    return sep.outputs  # Red, Green, Blue


def mix_rgb(nt, fac, a, b, blend="MIX"):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = blend
    ins = [s for s in n.inputs if s.type == "RGBA"]
    for sock, val in ((ins[0], a), (ins[1], b)):
        if isinstance(val, tuple):
            sock.default_value = val
        else:
            link(nt, val, sock)
    if isinstance(fac, (int, float)):
        n.inputs[0].default_value = fac
    else:
        link(nt, fac, n.inputs[0])
    return next(s for s in n.outputs if s.type == "RGBA")


def lerp(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMapRange")
    link(nt, fac, n.inputs["Value"])
    n.inputs["To Min"].default_value = a
    n.inputs["To Max"].default_value = b
    return n.outputs[0]


def math_(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            link(nt, v, n.inputs[i])
    return n.outputs[0]


def bump(nt, height, strength, dist=0.01, normal=None):
    b = nt.nodes.new("ShaderNodeBump")
    link(nt, height, b.inputs["Height"])
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = dist
    if normal is not None:
        link(nt, normal, b.inputs["Normal"])
    return b.outputs["Normal"]


def noise(nt, vec, scale, detail=4.0, rough=0.55, stretch=None):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    if vec is not None:
        if stretch is not None:
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.inputs["Scale"].default_value = stretch
            link(nt, vec, mp.inputs["Vector"])
            vec = mp.outputs["Vector"]
        link(nt, vec, n.inputs["Vector"])
    return n.outputs["Fac"]


def radius(nt):
    tc, sep = obj_xyz(nt)
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    link(nt, sep.outputs["X"], cmb.inputs["X"])
    link(nt, sep.outputs["Y"], cmb.inputs["Y"])
    vl = nt.nodes.new("ShaderNodeVectorMath")
    vl.operation = "LENGTH"
    link(nt, cmb.outputs[0], vl.inputs[0])
    return vl.outputs["Value"], sep, tc


def brushed_rings(nt, r, freq=140.0):
    """Concentric machining marks: 1D noise along the radius."""
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    link(nt, math_(nt, "MULTIPLY", r, freq), cmb.inputs["X"])
    cmb.inputs["Y"].default_value = 0.37
    return noise(nt, cmb.outputs[0], 1.0, detail=6, rough=0.7)


# ---------------------------------------------------------------- materials
_M = {}


def material(key):
    if key in _M:
        return _M[key]
    m = globals()["m_" + key]()
    _M[key] = m
    return m


def m_dark_metal():
    m, nt, b, _ = mat_begin("dark_metal")
    setv(b, "Base Color", (0.035, 0.035, 0.045, 1))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.42)
    return m


def m_exploit():
    m, nt, b, _ = mat_begin("exploit")
    uv = tile_uv(nt)
    s = tex(nt, uv, "exploit_scratch.png")["Red"]
    tc, sep = obj_xyz(nt)
    grain = noise(nt, tc.outputs["Object"], 1.0, detail=8, rough=0.6, stretch=(3, 90, 3))
    base = mix_rgb(nt, grain, C.lin("#FF3DA8", 0.62), C.lin("#FF3DA8", 0.9))
    col = mix_rgb(nt, math_(nt, "MULTIPLY", s, 0.85, clamp=True), base, (0.62, 0.6, 0.64, 1))
    link(nt, col, b.inputs["Base Color"])
    setv(b, "Metallic", 1.0)
    link(nt, lerp(nt, s, 0.24, 0.42), b.inputs["Roughness"])
    setv(b, "Anisotropic", 0.35)
    link(nt, bump(nt, math_(nt, "MULTIPLY", s, -1.0), 0.55, 0.004), b.inputs["Normal"])
    return m


def m_core():
    m, nt, b, _ = mat_begin("core")
    tc, sep = obj_xyz(nt)
    # brighter toward the impact point (outer side), magenta toward the edges
    dx = math_(nt, "SUBTRACT", sep.outputs["X"], 0.42)
    dy = math_(nt, "SUBTRACT", sep.outputs["Y"], 3.05)
    d = math_(nt, "SQRT", math_(nt, "ADD", math_(nt, "MULTIPLY", dx, dx), math_(nt, "MULTIPLY", dy, dy)))
    f = math_(nt, "SUBTRACT", 1.0, math_(nt, "DIVIDE", d, 2.2), clamp=True)
    col = mix_rgb(nt, math_(nt, "POWER", f, 1.6), C.lin("#B0106A"), C.lin("#FFB0E2"))
    setv(b, "Base Color", (0.02, 0.0, 0.01, 1))
    link(nt, col, b.inputs["Emission Color"])
    link(nt, lerp(nt, f, 0.6, 1.8), b.inputs["Emission Strength"])
    return m


def m_glass():
    m, nt, b, _ = mat_begin("zd_glass")
    uv = tile_uv(nt)
    c = tex(nt, uv, "zeroday_cracks.png")["Red"]
    setv(b, "Base Color", (1.0, 0.86, 0.95, 1))
    setv(b, "Transmission Weight", 1.0)
    setv(b, "IOR", 1.52)
    link(nt, lerp(nt, c, 0.03, 0.55), b.inputs["Roughness"])
    setv(b, "Emission Color", (1.0, 0.85, 0.97, 1))
    link(nt, math_(nt, "MULTIPLY", c, 0.9), b.inputs["Emission Strength"])
    link(nt, bump(nt, c, 0.8, 0.01), b.inputs["Normal"])
    return m


def m_fw_base():
    m, nt, b, _ = mat_begin("fw_base")
    setv(b, "Base Color", C.lin("#5CE1FF", 0.16))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.45)
    return m


def m_fw_fin():
    m, nt, b, _ = mat_begin("fw_fin")
    r, sep, tc = radius(nt)
    br = noise(nt, tc.outputs["Object"], 1.0, detail=8, rough=0.6, stretch=(2.5, 70, 2.5))
    link(nt, mix_rgb(nt, br, C.lin("#5CE1FF", 0.55), C.lin("#5CE1FF", 0.95)), b.inputs["Base Color"])
    setv(b, "Metallic", 1.0)
    link(nt, lerp(nt, br, 0.22, 0.36), b.inputs["Roughness"])
    return m


def m_sb_tray():
    m, nt, b, _ = mat_begin("sb_tray")
    setv(b, "Base Color", C.lin("#3FD6C8", 0.3))
    setv(b, "Metallic", 0.0)
    setv(b, "Roughness", 0.5)
    setv(b, "Emission Color", C.lin("#3FD6C8"))
    setv(b, "Emission Strength", 0.15)
    return m


def m_acrylic():
    m, nt, b, _ = mat_begin("acrylic")
    setv(b, "Base Color", C.lin("#9FF7EC"))
    setv(b, "Transmission Weight", 1.0)
    setv(b, "IOR", 1.49)
    setv(b, "Roughness", 0.32)
    setv(b, "Coat Weight", 0.4)
    setv(b, "Coat Roughness", 0.05)
    return m


def m_cube():
    m, nt, b, _ = mat_begin("cube")
    setv(b, "Base Color", (0.02, 0.05, 0.05, 1))
    setv(b, "Emission Color", C.lin("#7FFFF0"))
    setv(b, "Emission Strength", 14.0)
    return m


def m_carbon():
    m, nt, b, _ = mat_begin("carbon")
    uv = tile_uv(nt)
    ch = tex(nt, uv, "proxy_weave.png")
    h, d = ch["Red"], ch["Green"]
    tone = mix_rgb(nt, d, C.lin("#7BE07B", 0.06), C.lin("#7BE07B", 0.16))
    col = mix_rgb(nt, h, (0.35, 0.35, 0.35, 1), (1, 1, 1, 1))
    link(nt, mix_rgb(nt, 1.0, tone, col, "MULTIPLY"), b.inputs["Base Color"])
    setv(b, "Roughness", 0.4)
    setv(b, "Metallic", 0.2)
    setv(b, "Coat Weight", 1.0)
    setv(b, "Coat Roughness", 0.04)
    link(nt, bump(nt, h, 0.45, 0.004), b.inputs["Normal"])
    return m


def m_mirror():
    m, nt, b, _ = mat_begin("mirror")
    setv(b, "Base Color", C.lin("#E6FFE6"))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.03)
    return m


def m_pcb():
    m, nt, b, _ = mat_begin("pcb")
    uv = tile_uv(nt)
    ch = tex(nt, uv, "patch_pcb.png")
    t, p, tp = ch["Red"], ch["Green"], ch["Blue"]
    col = mix_rgb(nt, t, C.lin("#1F6B2A", 0.75), C.lin("#58B85C", 0.9))
    col = mix_rgb(nt, p, col, (0.72, 0.72, 0.70, 1))
    col = mix_rgb(nt, math_(nt, "MULTIPLY", tp, 0.75), col, C.lin("#7BE07B", 0.85))
    link(nt, col, b.inputs["Base Color"])
    link(nt, math_(nt, "MULTIPLY", p, math_(nt, "SUBTRACT", 1.0, tp)), b.inputs["Metallic"])
    rough = lerp(nt, p, 0.32, 0.18)
    link(nt, rough, b.inputs["Roughness"])
    setv(b, "Coat Weight", 0.5)
    h = math_(nt, "ADD", math_(nt, "MULTIPLY", t, 0.5), math_(nt, "ADD", p, math_(nt, "MULTIPLY", tp, 0.8)))
    link(nt, bump(nt, h, 0.5, 0.006), b.inputs["Normal"])
    return m


def m_solder():
    m, nt, b, _ = mat_begin("solder")
    setv(b, "Base Color", (0.82, 0.83, 0.85, 1))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.28)
    return m


def m_chip():
    m, nt, b, _ = mat_begin("chip")
    setv(b, "Base Color", (0.02, 0.02, 0.022, 1))
    setv(b, "Roughness", 0.35)
    return m


def m_silicone():
    m, nt, b, _ = mat_begin("silicone")
    tc, sep = obj_xyz(nt)
    n1 = noise(nt, tc.outputs["Object"], 2.2, detail=5, rough=0.6)
    vein = math_(nt, "POWER", math_(nt, "ABSOLUTE", math_(nt, "SUBTRACT", n1, 0.5)), 0.6)
    link(nt, mix_rgb(nt, vein, C.lin("#7A2AA8", 0.9), C.lin("#C85AFF", 0.75)), b.inputs["Base Color"])
    setv(b, "Roughness", 0.5)
    setv(b, "Subsurface Weight", 0.3)
    setv(b, "Subsurface Radius", (0.6, 0.2, 0.8))
    setv(b, "Subsurface Scale", 0.05)
    setv(b, "Coat Weight", 0.3)
    setv(b, "Coat Roughness", 0.25)
    link(nt, bump(nt, n1, 0.15, 0.02), b.inputs["Normal"])
    return m


def m_pustule():
    m, nt, b, _ = mat_begin("pustule")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    f = math_(nt, "SUBTRACT", 1.0, lw.outputs["Facing"])
    setv(b, "Base Color", C.lin("#D88CFF", 0.9))
    setv(b, "Roughness", 0.35)
    setv(b, "Subsurface Weight", 0.5)
    setv(b, "Subsurface Radius", (0.8, 0.2, 1.0))
    setv(b, "Subsurface Scale", 0.06)
    setv(b, "Coat Weight", 0.6)
    setv(b, "Emission Color", C.lin("#E070FF"))
    link(nt, math_(nt, "MULTIPLY", math_(nt, "POWER", f, 3.0), 2.2), b.inputs["Emission Strength"])
    return m


def m_trojan():
    m, nt, b, _ = mat_begin("trojan")
    uv = tile_uv(nt)
    ch = tex(nt, uv, "trojan_panel.png")
    g, rb = ch["Red"], ch["Green"]
    tc, sep = obj_xyz(nt)
    br = noise(nt, tc.outputs["Object"], 1.0, detail=8, rough=0.6, stretch=(80, 3, 3))
    plate = mix_rgb(nt, br, C.lin("#B08CFF", 0.62), C.lin("#B08CFF", 0.85))
    col = mix_rgb(nt, rb, plate, C.lin("#5B2FB8", 0.9))
    col = mix_rgb(nt, g, col, (0.03, 0.02, 0.05, 1))
    link(nt, col, b.inputs["Base Color"])
    link(nt, lerp(nt, rb, 0.85, 0.0), b.inputs["Metallic"])
    link(nt, lerp(nt, rb, 0.3, 0.45), b.inputs["Roughness"])
    link(nt, rb, b.inputs["Sheen Weight"])
    setv(b, "Sheen Tint", C.lin("#E8D8FF"))
    setv(b, "Emission Color", C.lin("#E9DDFF"))
    link(nt, math_(nt, "MULTIPLY", g, 0.5), b.inputs["Emission Strength"])
    h = math_(nt, "SUBTRACT", math_(nt, "MULTIPLY", rb, 0.8), g)
    link(nt, bump(nt, h, 0.6, 0.008), b.inputs["Normal"])
    return m


def m_ribbon():
    m, nt, b, _ = mat_begin("ribbon")
    setv(b, "Base Color", C.lin("#6A3FD0", 0.9))
    setv(b, "Roughness", 0.4)
    setv(b, "Sheen Weight", 1.0)
    setv(b, "Sheen Tint", C.lin("#F0E4FF"))
    setv(b, "Coat Weight", 0.3)
    return m


def m_primer():
    m, nt, b, _ = mat_begin("primer")
    tc, sep = obj_xyz(nt)
    n1 = noise(nt, tc.outputs["Object"], 3.0, detail=6, rough=0.6)
    n2 = noise(nt, tc.outputs["Object"], 160.0, detail=2, rough=0.5)
    link(nt, mix_rgb(nt, n1, C.lin("#5A5A5C", 0.85), C.lin("#7A7A7A", 0.95)), b.inputs["Base Color"])
    setv(b, "Roughness", 0.88)
    link(nt, bump(nt, n2, 0.12, 0.01), b.inputs["Normal"])
    return m


def m_rivet():
    m, nt, b, _ = mat_begin("rivet")
    setv(b, "Base Color", (0.32, 0.32, 0.33, 1))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.55)
    return m


def m_dead_led():
    m, nt, b, _ = mat_begin("dead_led")
    setv(b, "Base Color", (0.04, 0.04, 0.04, 1))
    setv(b, "Roughness", 0.2)
    return m


def led_mat(hexc):
    key = "led_" + hexc
    if key in _M:
        return _M[key]
    m, nt, b, _ = mat_begin(key)
    setv(b, "Base Color", C.lin(hexc))
    setv(b, "Emission Color", C.lin(hexc))
    setv(b, "Emission Strength", 5.0)
    _M[key] = m
    return m


def emit_mat(hexc, strength):
    key = "emit_%s_%s" % (hexc, strength)
    if key in _M:
        return _M[key]
    m, nt, b, _ = mat_begin(key)
    setv(b, "Base Color", (0, 0, 0, 1))
    setv(b, "Emission Color", C.lin(hexc))
    setv(b, "Emission Strength", strength)
    _M[key] = m
    return m


def m_steel():
    m, nt, b, _ = mat_begin("steel")
    r, sep, tc = radius(nt)
    br = brushed_rings(nt, r)
    link(nt, mix_rgb(nt, br, (0.45, 0.46, 0.48, 1), (0.72, 0.73, 0.75, 1)), b.inputs["Base Color"])
    setv(b, "Metallic", 1.0)
    link(nt, lerp(nt, br, 0.16, 0.3), b.inputs["Roughness"])
    return m


def hazard(nt, a_freq, r):
    """Diagonal hazard stripes in polar coords: fract(angle*k + r*m) < 0.5."""
    tc, sep = obj_xyz(nt)
    ang = math_(nt, "ARCTAN2", sep.outputs["Y"], sep.outputs["X"])
    s = math_(nt, "ADD", math_(nt, "MULTIPLY", ang, a_freq), math_(nt, "MULTIPLY", r, 2.6))
    fr = math_(nt, "FRACT", s)
    return math_(nt, "GREATER_THAN", fr, 0.5)


def m_meridian():
    """Enemy tile: steel hub band | orange powder coat | hazard rim, one material."""
    m, nt, b, _ = mat_begin("meridian")
    r, sep, tc = radius(nt)
    br = brushed_rings(nt, r)
    steel = mix_rgb(nt, br, (0.42, 0.43, 0.45, 1), (0.7, 0.71, 0.73, 1))
    peel = noise(nt, tc.outputs["Object"], 90.0, detail=2, rough=0.5)
    orange = mix_rgb(nt, peel, C.lin("#D8661A", 0.66), C.lin("#F07A22", 0.76))
    hz = hazard(nt, 9.0, r)
    stripes = mix_rgb(nt, hz, (0.012, 0.012, 0.014, 1), C.lin("#FFC21A", 0.9))
    in_steel = math_(nt, "LESS_THAN", r, 1.66)
    in_haz = math_(nt, "GREATER_THAN", r, 3.24)
    col = mix_rgb(nt, in_steel, orange, steel)
    col = mix_rgb(nt, in_haz, col, stripes)
    link(nt, col, b.inputs["Base Color"])
    link(nt, in_steel, b.inputs["Metallic"])
    link(nt, lerp(nt, in_steel, 0.55, 0.22), b.inputs["Roughness"])
    setv(b, "Specular IOR Level", 0.25)
    # grooves at the band boundaries
    g1 = math_(nt, "LESS_THAN", math_(nt, "ABSOLUTE", math_(nt, "SUBTRACT", r, 1.66)), 0.02)
    g2 = math_(nt, "LESS_THAN", math_(nt, "ABSOLUTE", math_(nt, "SUBTRACT", r, 3.24)), 0.02)
    h = math_(nt, "SUBTRACT", math_(nt, "MULTIPLY", peel, 0.15), math_(nt, "ADD", g1, g2))
    link(nt, bump(nt, h, 0.4, 0.01), b.inputs["Normal"])
    return m


def m_gunmetal():
    m, nt, b, _ = mat_begin("gunmetal")
    r, sep, tc = radius(nt)
    br = brushed_rings(nt, r, 90.0)
    link(nt, mix_rgb(nt, br, (0.06, 0.06, 0.075, 1), (0.13, 0.13, 0.15, 1)), b.inputs["Base Color"])
    setv(b, "Metallic", 1.0)
    link(nt, lerp(nt, br, 0.3, 0.45), b.inputs["Roughness"])
    return m


def m_hub_player():
    m, nt, b, _ = mat_begin("hub_player")
    setv(b, "Base Color", (0.03, 0.028, 0.04, 1))
    setv(b, "Roughness", 0.5)
    setv(b, "Coat Weight", 0.6)
    return m


def m_hazard_ring():
    m, nt, b, _ = mat_begin("hazard_ring")
    r, sep, tc = radius(nt)
    hz = hazard(nt, 40.0, r)
    link(nt, mix_rgb(nt, hz, (0.015, 0.015, 0.017, 1), C.lin("#FFB21A", 0.9)), b.inputs["Base Color"])
    setv(b, "Roughness", 0.45)
    return m


def m_orange():
    m, nt, b, _ = mat_begin("orange")
    tc, sep = obj_xyz(nt)
    peel = noise(nt, tc.outputs["Object"], 90.0, detail=2, rough=0.5)
    link(nt, mix_rgb(nt, peel, C.lin("#D8661A", 0.66), C.lin("#F07A22", 0.76)), b.inputs["Base Color"])
    setv(b, "Roughness", 0.55)
    link(nt, bump(nt, peel, 0.12, 0.01), b.inputs["Normal"])
    return m


def m_chrome():
    m, nt, b, _ = mat_begin("chrome")
    setv(b, "Base Color", (0.85, 0.86, 0.88, 1))
    setv(b, "Metallic", 1.0)
    setv(b, "Roughness", 0.12)
    return m


# ---------------------------------------------------------------- geometry
def arc(r, a0, a1, step=math.radians(1.0)):
    n = max(2, int(abs(a1 - a0) / step) + 1)
    return [(r * math.cos(a0 + (a1 - a0) * i / (n - 1)), r * math.sin(a0 + (a1 - a0) * i / (n - 1)))
            for i in range(n)]


def outline(ticks, r0, r1, gap=C.GAP, notch=None):
    ar0, ar1 = C.edge_angle(ticks, r0, +1, gap), C.edge_angle(ticks, r1, +1, gap)
    al0, al1 = C.edge_angle(ticks, r0, -1, gap), C.edge_angle(ticks, r1, -1, gap)
    outer = arc(r1, ar1, al1)
    if notch is not None:
        nc, nw, nd = notch  # centre angle, angular width, depth
        lo, hi = nc - nw / 2, nc + nw / 2
        keep_lo = [p for p in outer if math.atan2(p[1], p[0]) < lo]
        keep_hi = [p for p in outer if math.atan2(p[1], p[0]) > hi]
        v = [(r1 * math.cos(lo), r1 * math.sin(lo)),
             ((r1 - nd) * math.cos(lo + nw * 0.2), (r1 - nd) * math.sin(lo + nw * 0.2)),
             ((r1 - nd * 0.8) * math.cos(lo + nw * 0.55), (r1 - nd * 0.8) * math.sin(lo + nw * 0.55)),
             ((r1 - nd * 0.25) * math.cos(hi - nw * 0.05), (r1 - nd * 0.25) * math.sin(hi - nw * 0.05)),
             (r1 * math.cos(hi), r1 * math.sin(hi))]
        outer = keep_lo + v + keep_hi
    inner = arc(r0, al0, ar0)
    return outer + inner


def link_ob(ob, parent):
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent


def slab(name, pts, z0, z1, mat, parent=None, bev=0.03, segs=3):
    n = len(pts)
    verts = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link_ob(ob, parent)
    if bev > 0:
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = bev
        md.segments = segs
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(30)
        md.harden_normals = True
    return ob


def rect_pts(cx, cy, w, h, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for sx, sy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        out.append((cx + sx * ca - sy * sa, cy + sx * sa + sy * ca))
    return out


def blob(name, x, y, z, r, squash, mat, parent=None, segs=(32, 16)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=r)
    for v in bm.verts:
        v.co.z *= squash
        v.co.x += x
        v.co.y += y
        v.co.z += z
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link_ob(ob, parent)
    return ob


def cube(name, x, y, z, edge, rot, mat, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=edge)
    from mathutils import Euler, Vector
    R = Euler(rot).to_matrix()
    for v in bm.verts:
        v.co = R @ v.co + Vector((x, y, z))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link_ob(ob, parent)
    md = ob.modifiers.new("bev", "BEVEL")
    md.width = 0.025
    md.segments = 2
    return ob


def led(parent, hexc, ticks, y=3.43):
    if not C.inside(ticks, 0, y, 0.06):
        return
    m = material("dead_led") if hexc is None else led_mat(hexc)
    blob("led", 0, y, 0.15, 0.045, 0.6, m, parent, (16, 8))


# ---------------------------------------------------------------- tiles
def tile(typ, ticks, loc=(0, 0), rot_deg=0.0, enemy=False):
    e = bpy.data.objects.new("tile_%s_%d" % (typ, ticks), None)
    bpy.context.scene.collection.objects.link(e)
    e.location = (loc[0], loc[1], 0)
    e.rotation_euler = (0, 0, math.radians(rot_deg))
    full = outline(ticks, C.R_IN, C.R_OUT)
    name, hexc, _ = C.PROGRAMS[typ]
    T = 0.16
    if enemy:
        slab("body", full, 0, T, material("meridian"), e, 0.05)
        inl = outline(ticks, 3.18, 3.29, C.GAP + 0.12)
        slab("inlay", inl, T - 0.01, T + 0.012, emit_mat(hexc, 2.2), e, 0.0)
        return e
    if typ == "ATTACK":
        h = C.half_angle(ticks)
        notch = (math.pi / 2 - h * 0.42, min(math.radians(7.0), h * 0.5), 0.36)
        slab("body", outline(ticks, C.R_IN, C.R_OUT, notch=notch), 0, T, material("exploit"), e, 0.05)
        led(e, hexc, ticks)
    elif typ == "CRITICAL":
        slab("tray", full, 0, 0.04, material("dark_metal"), e, 0.015)
        core = outline(ticks, C.R_IN + C.CORE_INSET, C.R_OUT - C.CORE_INSET, C.GAP + 2 * C.CORE_INSET)
        slab("core", core, 0.04, 0.075, material("core"), e, 0.01, 2)
        slab("glass", full, 0.08, 0.24, material("glass"), e, 0.04, 4)
    elif typ == "DEFEND":
        slab("base", full, 0, 0.07, material("fw_base"), e, 0.02)
        r = C.R_IN + 0.15
        while r + C.FIN_W < C.R_OUT - 0.1:
            fin = outline(ticks, r, r + C.FIN_W, C.GAP + 0.16)
            slab("fin", fin, 0.07, 0.29, material("fw_fin"), e, 0.022, 2)
            r += C.FIN_PITCH
    elif typ == "SHIELD":
        slab("tray", full, 0, 0.05, material("sb_tray"), e, 0.015)
        box = outline(ticks, C.R_IN + 0.05, C.R_OUT - 0.05, C.GAP + 0.1)
        slab("acrylic", box, 0.05, 0.44, material("acrylic"), e, 0.05, 4)
        cx, cy, ed = C.CUBE
        cube("cube", cx, cy, 0.245, ed, (math.radians(35), math.radians(12), math.radians(40)),
             material("cube"), e)
        ld = bpy.data.lights.new("cube_glow", "POINT")
        ld.energy = 40.0
        ld.color = (0.45, 1.0, 0.92)
        ld.shadow_soft_size = 0.12
        lo = bpy.data.objects.new("cube_glow", ld)
        link_ob(lo, e)
        lo.location = (cx, cy, 0.25)
    elif typ == "EVADE":
        slab("body", full, 0, T, material("carbon"), e, 0.05)
        size, ang, pts = C.mirror_tiles()
        for i, (x, y) in enumerate(pts):
            if C.inside(ticks, x, y, size * 0.75):
                slab("mir%d" % i, rect_pts(x, y, size, size, ang), T, T + 0.03, material("mirror"), e, 0.008, 1)
        led(e, hexc, ticks)
    elif typ == "HEAL":
        slab("body", full, 0, 0.14, material("pcb"), e, 0.04)
        sx, sy, sr = C.SOLDER
        blob("solder", sx, sy, 0.13, sr, 0.55, material("solder"), e)
        for i, (x, y, w, h) in enumerate(((-0.62, 3.0, 0.24, 0.15), (0.66, 2.92, 0.18, 0.26),
                                         (-0.48, 1.72, 0.2, 0.13), (0.95, 3.25, 0.14, 0.1))):
            if C.inside(ticks, x, y, max(w, h) * 0.7):
                slab("chip%d" % i, rect_pts(x, y, w, h, 0.1), 0.14, 0.19, material("chip"), e, 0.008, 1)
        led(e, hexc, ticks)
    elif typ == "AFFLICT":
        slab("body", full, 0, T, material("silicone"), e, 0.06, 4)
        for i, (x, y, r) in enumerate(C.pustules()):
            if C.inside(ticks, x, y, r * 1.05):
                blob("pus%d" % i, x, y, T - r * 0.2, r, 0.7, material("pustule"), e)
    elif typ == "DEPLOY":
        slab("body", full, 0, T, material("trojan"), e, 0.05)
        y0, y1 = C.RIBBON_Y
        rib = outline(ticks, y0, y1, C.GAP + 0.02)
        slab("ribbon", rib, T - 0.01, T + 0.045, material("ribbon"), e, 0.015, 2)
        ym = (y0 + y1) / 2
        for sx in (-1, 1):
            blob("bow%d" % sx, sx * 0.17, ym + 0.02, T + 0.05, 0.13, 0.4, material("ribbon"), e, (24, 12))
        blob("knot", 0, ym, T + 0.06, 0.07, 0.6, material("ribbon"), e, (16, 8))
        led(e, hexc, ticks, y=3.47)
    elif typ == "MISS":
        slab("body", full, 0, 0.14, material("primer"), e, 0.045)
        for rr in (C.R_IN + 0.22, C.R_OUT - 0.2):
            for side in (+1, -1):
                a = C.edge_angle(ticks, rr, side) + (-1 if side < 0 else 1) * math.asin(0.2 / rr)
                blob("rivet", rr * math.cos(a), rr * math.sin(a), 0.135, 0.06, 0.55, material("rivet"), e,
                     (16, 8))
        led(e, None, ticks)
    return e


# ---------------------------------------------------------------- wheel parts
def ring(name, r0, r1, z0, z1, mat, bev=0.03, teeth=None):
    """Full annulus as a slab: outer loop then inner loop joined by a seam-less bridge."""
    step = math.radians(0.75)
    n = int(2 * math.pi / step)
    outer = []
    for i in range(n):
        a = i * step
        rr = r1
        if teeth is not None:
            cnt, depth, duty = teeth
            if ((a * cnt / (2 * math.pi)) % 1.0) > duty:
                rr = r1 - depth
        outer.append((rr * math.cos(a), rr * math.sin(a)))
    inner = [(r0 * math.cos(i * step), r0 * math.sin(i * step)) for i in range(n)]
    verts = []
    for z in (z0, z1):
        verts += [(x, y, z) for x, y in outer] + [(x, y, z) for x, y in inner]
    faces = []
    O, I = 0, n
    TO, TI = 2 * n, 3 * n
    for i in range(n):
        j = (i + 1) % n
        faces.append((TO + i, TO + j, TI + j, TI + i))  # top
        faces.append((O + i, I + i, I + j, O + j))                  # bottom
        faces.append((O + i, O + j, TO + j, TO + i))                # outer wall
        faces.append((I + j, I + i, TI + i, TI + j))                # inner wall
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    link_ob(ob, None)
    if bev > 0:
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = bev
        md.segments = 3
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(30)
        md.harden_normals = True
    return ob


def disc(name, r, z0, z1, mat, bev=0.04):
    pts = [(r * math.cos(a), r * math.sin(a)) for a in [i * math.radians(1.0) for i in range(360)]]
    return slab(name, pts, z0, z1, mat, None, bev)


def pointer(hexc):
    top = C.R_OUT + 0.95
    pts = [(0, C.R_OUT - 0.32), (0.17, top - 0.25), (0.0, top), (-0.17, top - 0.25)]
    slab("needle", pts, 0.5, 0.62, material("chrome"), None, 0.02, 2)
    tip = [(0, C.R_OUT - 0.3), (0.07, C.R_OUT + 0.05), (-0.07, C.R_OUT + 0.05)]
    slab("needle_tip", tip, 0.62, 0.64, emit_mat(hexc, 5.0), None, 0.0)
    blob("needle_cap", 0, top - 0.12, 0.62, 0.2, 0.45, material("chrome"))


def wheel(spec, enemy):
    for typ, t, v, cdeg in C.wheel_slices(spec):
        tile(typ, t, (0, 0), cdeg - 90.0, enemy)
    if enemy:
        disc("backing", C.R_OUT + 0.1, -0.12, 0.0, material("steel"), 0.02)
        ring("bezel_haz", C.R_OUT + 0.04, C.R_OUT + 0.36, -0.05, 0.3, material("hazard_ring"), 0.03)
        ring("bezel_orange", C.R_OUT + 0.36, C.R_OUT + 0.7, -0.05, 0.36, material("orange"), 0.03,
             teeth=(30, 0.12, 0.62))
        ring("bezel_lip", C.R_OUT + 0.33, C.R_OUT + 0.39, 0.0, 0.4, material("steel"), 0.01)
        disc("hub", C.R_IN - 0.06, 0.0, 0.3, material("steel"), 0.05)
        disc("hub_face", C.R_IN - 0.2, 0.3, 0.33, material("gunmetal"), 0.02)
        ring("hub_glow", C.R_IN - 0.22, C.R_IN - 0.17, 0.3, 0.335, emit_mat("#FF8A1E", 4.0), 0.0)
        pointer("#FF8A1E")
    else:
        disc("backing", C.R_OUT + 0.1, -0.12, 0.0, material("gunmetal"), 0.02)
        ring("bezel", C.R_OUT + 0.04, C.R_OUT + 0.62, -0.05, 0.34, material("gunmetal"), 0.06)
        ring("bezel_glow", C.R_OUT + 0.05, C.R_OUT + 0.1, 0.0, 0.36, emit_mat("#FF3DA8", 3.0), 0.0)
        for i in range(C.TICKS):
            a = math.radians(90 - i * C.TICK_DEG)
            rr = C.R_OUT + 0.42
            slab("tick%d" % i, rect_pts(rr * math.cos(a), rr * math.sin(a), 0.035, 0.18, a - math.pi / 2),
                 0.34, 0.36, material("chrome"), None, 0.0)
        for i in range(8):
            a = math.radians(22.5 + i * 45)
            rr = C.R_OUT + 0.3
            blob("screw%d" % i, rr * math.cos(a), rr * math.sin(a), 0.33, 0.07, 0.45, material("chrome"), None,
                 (16, 8))
        disc("hub", C.R_IN - 0.06, 0.0, 0.3, material("gunmetal"), 0.05)
        disc("hub_face", C.R_IN - 0.2, 0.3, 0.33, material("hub_player"), 0.02)
        ring("hub_glow", C.R_IN - 0.22, C.R_IN - 0.17, 0.3, 0.335, emit_mat("#FF3DA8", 3.5), 0.0)
        pointer("#FF3DA8")


# ---------------------------------------------------------------- jobs
def main():
    sc = reset()
    if JOB == "sheet":
        camera(sc, 0, 0, C.SHEET_ORTHO, 1920, 1080)
        lights(sc, 10.0)
        for typ, t, v, x, y in C.SHEET:
            tile(typ, t, (x, y))
    elif JOB in ("player", "enemy"):
        camera(sc, 0, 0, C.WHEEL_ORTHO, C.WHEEL_RES, C.WHEEL_RES)
        lights(sc, 5.0)
        wheel(C.PLAYER_WHEEL if JOB == "player" else C.ENEMY_WHEEL, JOB == "enemy")
    elif JOB == "enemy_sheet":
        camera(sc, 0, 0, C.SHEET_ORTHO, 1920, 1080)
        lights(sc, 10.0)
        for typ, t, v, x, y in C.SHEET:
            tile(typ, t, (x, y), enemy=True)
    else:  # test: three tiles
        camera(sc, 0, 2.4, 8.0, 800, 400)
        lights(sc, 4.0)
        for i, typ in enumerate(("ATTACK", "CRITICAL", "SHIELD")):
            tile(typ, 3, (-2.6 + 2.6 * i, 0))
    os.makedirs(os.path.dirname(OUTP), exist_ok=True)
    sc.render.filepath = OUTP
    bpy.ops.render.render(write_still=True)
    print("RENDERED", OUTP)


main()
