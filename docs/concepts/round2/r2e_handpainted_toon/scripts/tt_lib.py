"""R2E HAND-PAINTED TOON: shared Blender 5.2 helpers.

Painted toon materials (emission-output colour built from a toon-quantised light term,
brush-stroke noise, bottom grime and top highlight), chunky wonky beveled primitives,
extruded text, Freestyle ink lines, render + compositor setup.
Seeded randomness only (random.Random instances).
"""
import bpy
import bmesh
import colorsys
import math
import os
import random
import sys
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
FONT_DIR = "C:/Windows/Fonts/"
FONTS = {
    "title": "GILLUBCD.TTF",   # chunky condensed display face
    "sign": "ROCKEB.TTF",      # slab serif, wood-sign numbers
    "body": "segoeuib.ttf",    # small readable body text
    "round": "BRITANIC.TTF",
}
INK = "#1c1210"

MODE = {"name": "day", "fake": (-0.4, -1.0, 0.8)}   # name: day|night|alarm palette logic; fake: UI light dir (world)


def arg_list():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


# ------------------------------------------------------------------ colour
def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(h, a=1.0):
    r, g, b = hex_rgb(h)
    return (s2l(r), s2l(g), s2l(b), a)


def rgb_lin(rgb, a=1.0):
    return (s2l(rgb[0]), s2l(rgb[1]), s2l(rgb[2]), a)


def shift(h, dh=0.0, ds=1.0, dv=1.0, toward=None, t=0.0):
    """HSV tweak of an sRGB hex -> sRGB tuple."""
    r, g, b = hex_rgb(h) if isinstance(h, str) else h
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh + dh) % 1.0
    s = max(0.0, min(1.0, s * ds))
    v = max(0.0, min(1.0, v * dv))
    out = colorsys.hsv_to_rgb(hh, s, v)
    if toward is not None:
        tr = hex_rgb(toward)
        out = tuple(a + (b2 - a) * t for a, b2 in zip(out, tr))
    return out


def hue_toward(h, target_h, amt):
    d = ((target_h - h + 0.5) % 1.0) - 0.5
    return (h + d * amt) % 1.0


def palette_pair(base_hex):
    """Painted light / shadow pair for a base colour under the current MODE."""
    r, g, b = hex_rgb(base_hex)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    mode = MODE["name"]
    # lit: warmer, a touch brighter
    lh = hue_toward(h, 0.12, 0.06) if s > 0.08 else h
    lit = colorsys.hsv_to_rgb(lh, min(1, s * 1.02), min(1, v * 1.10 + 0.03))
    # shadow: cooler, purple-leaning, saturated (hand-painted shadows are never grey)
    sh_h = hue_toward(h, 0.72, 0.16)
    shade = colorsys.hsv_to_rgb(sh_h, min(1, s * 1.08 + 0.10), v * 0.52)
    if mode == "night":
        lit = tuple(a * 0.75 + bb for a, bb in zip(colorsys.hsv_to_rgb(hue_toward(h, 0.62, 0.30), min(1, s * 0.9 + 0.1), v * 0.80), (0.0, 0.03, 0.08)))
        shade = tuple(a * 0.6 + bb for a, bb in zip(colorsys.hsv_to_rgb(hue_toward(h, 0.68, 0.40), min(1, s * 0.8 + 0.2), v * 0.45), (0.03, 0.035, 0.09)))
    elif mode == "alarm":
        lit = tuple(a * 0.62 + bb for a, bb in zip(colorsys.hsv_to_rgb(hue_toward(h, 0.93, 0.35), min(1, s * 0.9 + 0.15), v * 0.70), (0.06, 0.0, 0.03)))
        shade = tuple(a * 0.55 + bb for a, bb in zip(colorsys.hsv_to_rgb(hue_toward(h, 0.80, 0.45), min(1, s * 0.8 + 0.25), v * 0.38), (0.06, 0.01, 0.05)))
    return lit, shade


# ------------------------------------------------------------------ scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def setup_render(sc, w=1920, h=1080, samples=32, transparent=False, bg="#3f5566",
                 line=3.0, line_col=INK, crease=138.0):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    try:
        sc.eevee.taa_render_samples = samples
    except Exception:
        pass
    try:
        sc.eevee.use_shadows = True
        sc.eevee.shadow_pool_size = "512"
    except Exception:
        pass
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    try:
        sc.view_settings.look = "None"
    except TypeError:
        pass
    wd = bpy.data.worlds.new("W")
    sc.world = wd
    wd.use_nodes = True
    bgn = next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND")
    bgn.inputs[0].default_value = lin(bg)
    bgn.inputs[1].default_value = 1.0
    freestyle(sc, line, line_col, crease)
    add_line_set(sc, "thin", thin_coll(), max(1.2, line * 0.45), line_col)
    return sc


_NOLINE = {}


def noline_coll():
    sc = bpy.context.scene
    if "NOLINE" not in bpy.data.collections:
        c = bpy.data.collections.new("NOLINE")
        sc.collection.children.link(c)
    return bpy.data.collections["NOLINE"]


def thin_coll():
    """Objects here get a thin, steady ink line (small text); nested in NOLINE so the main
    line set skips them."""
    if "THIN" not in bpy.data.collections:
        c = bpy.data.collections.new("THIN")
        noline_coll().children.link(c)
    return bpy.data.collections["THIN"]


def freestyle(sc, thick=3.0, col=INK, crease=138.0):
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 1.0
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(crease)
    fs.use_smoothness = False
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("LineSet")
    ls.select_by_visibility = True
    ls.visibility = "VISIBLE"
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_external_contour = True
    ls.select_by_collection = True
    ls.collection = noline_coll()
    ls.collection_negation = "EXCLUSIVE"
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("ink")
    st = ls.linestyle
    st.color = lin(col)[:3]
    st.thickness = thick
    st.thickness_position = "CENTER"
    st.caps = "ROUND"
    st.chaining = "PLAIN"
    st.use_same_object = True
    st.use_length_min = True
    st.length_min = 4.0
    # hand-inked: tapered ends, slight wobble, tiny overshoot
    tm = st.thickness_modifiers.new("taper", "ALONG_STROKE")
    tm.mapping = "CURVE"
    tm.value_min = 0.35
    tm.value_max = 1.25
    cm = tm.curve
    pts = cm.curves[0].points
    pts[0].location = (0.0, 0.2)
    pts[1].location = (1.0, 0.2)
    pts.new(0.5, 1.0)
    pts.new(0.15, 0.8)
    pts.new(0.85, 0.8)
    cm.update()
    tm.blend = "MULTIPLY"
    gm = st.geometry_modifiers.new("wobble", "PERLIN_NOISE_1D")
    gm.frequency = 6.0
    gm.amplitude = 1.1
    gm.octaves = 2
    gm.seed = 7
    bb = None  # backbone stretcher breaks stroke resampling on tiny strokes

    return st


def add_line_set(sc, name, coll, thick, col=INK):
    """Extra line set (e.g. thinner lines for small HUD text) limited to a collection."""
    vl = sc.view_layers[0]
    ls = vl.freestyle_settings.linesets.new(name)
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_external_contour = True
    ls.select_by_collection = True
    ls.collection = coll
    ls.collection_negation = "INCLUSIVE"
    ls.linestyle = bpy.data.linestyles.new(name + "_ls")
    ls.linestyle.color = lin(col)[:3]
    ls.linestyle.thickness = thick
    ls.linestyle.caps = "ROUND"
    return ls


def compositor(sc, bloom=None, kuwahara=0, vignette=False):
    ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    out = ng.nodes.new("NodeGroupOutput")
    rl = ng.nodes.new("CompositorNodeRLayers")
    cur = rl.outputs["Image"]
    if kuwahara:
        kw = ng.nodes.new("CompositorNodeKuwahara")
        kw.inputs["Size"].default_value = kuwahara
        try:
            kw.inputs["Type"].default_value = "Anisotropic"
        except Exception:
            pass
        ng.links.new(cur, kw.inputs["Image"])
        cur = kw.outputs["Image"]
    if bloom:
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Threshold"].default_value = bloom[0]
        gl.inputs["Strength"].default_value = bloom[1]
        gl.inputs["Size"].default_value = bloom[2]
        try:
            gl.inputs["Quality"].default_value = "High"
        except Exception:
            pass
        ng.links.new(cur, gl.inputs["Image"])
        cur = gl.outputs["Image"]
    ng.links.new(cur, out.inputs[0])


def render(sc, path):
    sc.render.filepath = os.path.abspath(path)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


# ------------------------------------------------------------------ lights / camera
def sun(energy=3.0, col="#fff1d6", rot=(50, 0, 35), shadow=True, angle=3.0):
    d = bpy.data.lights.new("sun", "SUN")
    d.energy = energy
    d.color = lin(col)[:3]
    d.use_shadow = shadow
    d.angle = math.radians(angle)
    o = bpy.data.objects.new("sun", d)
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = [math.radians(a) for a in rot]
    return o


def point(loc, col="#ff3fb4", energy=200, radius=0.3, shadow=False):
    d = bpy.data.lights.new("pt", "POINT")
    d.energy = energy
    d.color = lin(col)[:3]
    d.shadow_soft_size = radius
    d.use_shadow = shadow
    o = bpy.data.objects.new("pt", d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o


def spot(loc, target, col="#ffffff", energy=2000, size=20, blend=0.3, shadow=False):
    d = bpy.data.lights.new("spot", "SPOT")
    d.energy = energy
    d.color = lin(col)[:3]
    d.spot_size = math.radians(size)
    d.spot_blend = blend
    d.use_shadow = shadow
    o = bpy.data.objects.new("spot", d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def look_at(o, target):
    d = Vector(target) - Vector(o.location)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50, ortho=None):
    c = bpy.data.cameras.new("cam")
    c.lens = lens
    c.clip_start = 0.1
    c.clip_end = 500
    if ortho:
        c.type = "ORTHO"
        c.ortho_scale = ortho
    o = bpy.data.objects.new("cam", c)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    bpy.context.scene.camera = o
    return o


# ------------------------------------------------------------------ materials
_MATS = {}


def _nt(m):
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt


def _math(nt, op, a=None, b=None, v1=None, v2=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    if a is not None:
        nt.links.new(a, n.inputs[0])
    elif v1 is not None:
        n.inputs[0].default_value = v1
    if b is not None:
        nt.links.new(b, n.inputs[1])
    elif v2 is not None:
        n.inputs[1].default_value = v2
    return n.outputs[0]


def _mix(nt, fac, a, b, blend="MIX"):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    n.blend_type = blend
    if isinstance(fac, float) or isinstance(fac, int):
        n.inputs[0].default_value = fac
    else:
        nt.links.new(fac, n.inputs[0])
    for sock, val in ((n.inputs[6], a), (n.inputs[7], b)):
        if isinstance(val, tuple):
            sock.default_value = val
        else:
            nt.links.new(val, sock)
    return n.outputs[2]


def paint(base, name=None, stroke=0.16, blotch=0.20, streak_axis=2, streak=10.0, grime=0.30,
          toplight=0.22, gloss=0.0, emit=None, emit_str=0.0, seed=0, scale=1.0, flat=False, fake=None, pattern=None, pat_scale=1.0, edge=False):
    """Hand-painted toon material. Output is emission of a painted colour, so the palette is
    exact under the Standard view; light only picks between the painted shadow and lit tones
    (per channel, so coloured neon light still tints)."""
    kw_in = dict(name=name, stroke=stroke, blotch=blotch, streak_axis=streak_axis, streak=streak, grime=grime,
                 toplight=toplight, gloss=gloss, emit=emit, emit_str=emit_str, seed=seed, scale=scale, flat=flat,
                 fake=fake, pattern=pattern, pat_scale=pat_scale)
    if isinstance(fake, str):
        fake = tuple(MODE["fake"])
    key = (name or base, MODE["name"], stroke, blotch, streak_axis, grime, gloss, emit, emit_str, seed, scale, flat, fake, pattern, pat_scale, edge)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name or ("paint_" + base))
    m.use_nodes = True
    nt = _nt(m)
    L = nt.links
    lit, shade = palette_pair(base)
    if edge:
        lit = tuple(min(1.0, c * 1.22 + 0.10) for c in shift(lit, dh=0.0, ds=0.85))
        shade = tuple(min(1.0, c * 1.35 + 0.06) for c in shade)
        pattern = None
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    # light term
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    dif.inputs[0].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    L.new(dif.outputs[0], s2r.inputs[0])
    curve = nt.nodes.new("ShaderNodeRGBCurve")
    c = curve.mapping.curves[3]
    c.points[0].location = (0.0, 0.0)
    c.points[1].location = (1.0, 1.0)
    c.points.new(0.10, 0.12)
    c.points.new(0.30, 0.50)
    c.points.new(0.60, 0.86)
    curve.mapping.update()
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    if fake is not None:
        # UI props: fixed light direction (independent of scene lights), still toon-curved
        nt.nodes.remove(s2r); nt.nodes.remove(dif)
        dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
        L.new(geo.outputs["Normal"], dot.inputs[0])
        dot.inputs[1].default_value = Vector(fake).normalized()
        f = _math(nt, "MULTIPLY", dot.outputs["Value"], v2=0.62)
        f = _math(nt, "ADD", f, v2=0.40)
        cc = nt.nodes.new("ShaderNodeCombineColor")
        L.new(f, cc.inputs[0]); L.new(f, cc.inputs[1]); L.new(f, cc.inputs[2])
        L.new(cc.outputs[0], curve.inputs[1])
        toplight = 0.0
    else:
        L.new(s2r.outputs[0], curve.inputs[1])
    light = curve.outputs[0]
    # geometry helpers
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nsep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Normal"], nsep.inputs[0])
    if not flat:
        # top light: faces pointing up catch painted highlight
        up = _math(nt, "MAXIMUM", nsep.outputs[2], v2=0.0)
        up = _math(nt, "POWER", up, v2=2.0)
        up = _math(nt, "MULTIPLY", up, v2=toplight)
        va0 = nt.nodes.new("ShaderNodeVectorMath"); va0.operation = "ADD"
        L.new(light, va0.inputs[0]); L.new(up, va0.inputs[1])
        light = va0.outputs[0]
    # painted colour = shade + (lit - shade) * light   (per channel)
    vsub = nt.nodes.new("ShaderNodeVectorMath"); vsub.operation = "SUBTRACT"
    vsub.inputs[0].default_value = rgb_lin(lit)[:3]
    vsub.inputs[1].default_value = rgb_lin(shade)[:3]
    vmul = nt.nodes.new("ShaderNodeVectorMath"); vmul.operation = "MULTIPLY"
    L.new(vsub.outputs[0], vmul.inputs[0]); L.new(light, vmul.inputs[1])
    vadd = nt.nodes.new("ShaderNodeVectorMath"); vadd.operation = "ADD"
    L.new(vmul.outputs[0], vadd.inputs[0])
    vadd.inputs[1].default_value = rgb_lin(shade)[:3]
    col = vadd.outputs[0]
    # brush texture
    rng = random.Random(seed * 7919 + len(base))
    mp = nt.nodes.new("ShaderNodeMapping")
    L.new(tc.outputs["Object"], mp.inputs[0])
    mp.inputs["Location"].default_value = (rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50))
    mp.inputs["Scale"].default_value = (2.2 * scale, 2.2 * scale, 2.2 * scale)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Detail"].default_value = 4.0
    nz.inputs["Roughness"].default_value = 0.62
    nz.inputs["Distortion"].default_value = 0.9
    L.new(mp.outputs[0], nz.inputs["Vector"])
    blot = _math(nt, "SUBTRACT", nz.outputs["Fac"], v2=0.5)
    blot = _math(nt, "MULTIPLY", blot, v2=blotch * 2.2)
    blot = _math(nt, "ADD", blot, v2=1.0)
    vs = nt.nodes.new("ShaderNodeVectorMath"); vs.operation = "SCALE"
    L.new(col, vs.inputs[0]); L.new(blot, vs.inputs["Scale"])
    col = vs.outputs[0]
    # streaks: anisotropic noise, lighter warm strokes
    mp2 = nt.nodes.new("ShaderNodeMapping")
    L.new(tc.outputs["Object"], mp2.inputs[0])
    sc3 = [3.0 * scale, 3.0 * scale, 3.0 * scale]
    sc3[streak_axis] = streak * scale
    mp2.inputs["Scale"].default_value = sc3
    mp2.inputs["Location"].default_value = (rng.uniform(0, 50), rng.uniform(0, 50), 0)
    nz2 = nt.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Detail"].default_value = 2.0
    nz2.inputs["Scale"].default_value = 3.0
    L.new(mp2.outputs[0], nz2.inputs["Vector"])
    st = _math(nt, "SUBTRACT", nz2.outputs["Fac"], v2=0.5)
    st = _math(nt, "MULTIPLY", st, v2=stroke * 3.0)
    st = _math(nt, "ADD", st, v2=1.0)
    vs2 = nt.nodes.new("ShaderNodeVectorMath"); vs2.operation = "SCALE"
    L.new(col, vs2.inputs[0]); L.new(st, vs2.inputs["Scale"])
    col = vs2.outputs[0]
    # painted pattern: bricks / planks drawn as darker mortar lines (u = x + y, v = z)
    if pattern:
        sxyz = nt.nodes.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sxyz.inputs[0])
        cxyz = nt.nodes.new("ShaderNodeCombineXYZ")
        if pattern == "tiles":
            L.new(sxyz.outputs[0], cxyz.inputs[0]); L.new(sxyz.outputs[1], cxyz.inputs[1])
        else:
            u = _math(nt, "ADD", sxyz.outputs[0], sxyz.outputs[1])
            L.new(u, cxyz.inputs[0]); L.new(sxyz.outputs[2], cxyz.inputs[1])
        br = nt.nodes.new("ShaderNodeTexBrick")
        L.new(cxyz.outputs[0], br.inputs["Vector"])
        br.inputs["Color1"].default_value = (1, 1, 1, 1)
        br.inputs["Color2"].default_value = (0.86, 0.86, 0.86, 1)
        br.inputs["Mortar"].default_value = (0.66, 0.62, 0.7, 1)
        br.inputs["Mortar Size"].default_value = 0.035 if pattern == "brick" else 0.05
        br.inputs["Mortar Smooth"].default_value = 0.4
        if pattern == "brick":
            br.inputs["Scale"].default_value = 2.4 * pat_scale
            br.inputs["Brick Width"].default_value = 0.6
            br.inputs["Row Height"].default_value = 0.28
        elif pattern == "tiles":
            br.inputs["Scale"].default_value = 1.2 * pat_scale
            br.inputs["Brick Width"].default_value = 1.0
            br.inputs["Row Height"].default_value = 0.7
        else:  # planks
            br.inputs["Scale"].default_value = 1.6 * pat_scale
            br.inputs["Brick Width"].default_value = 2.6
            br.inputs["Row Height"].default_value = 0.3
        vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "MULTIPLY"
        L.new(col, vm.inputs[0]); L.new(br.outputs["Color"], vm.inputs[1])
        col = vm.outputs[0]
    # grime toward the bottom of each object
    if grime > 0 and not flat:
        gsep = nt.nodes.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Generated"], gsep.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = 0.0
        mr.inputs[2].default_value = 0.35
        mr.inputs[3].default_value = 1.0 - grime
        mr.inputs[4].default_value = 1.0
        L.new(gsep.outputs[2], mr.inputs[0])
        vs3 = nt.nodes.new("ShaderNodeVectorMath"); vs3.operation = "SCALE"
        L.new(col, vs3.inputs[0]); L.new(mr.outputs[0], vs3.inputs["Scale"])
        col = vs3.outputs[0]
    # AO in crevices
    if not flat:
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.inputs["Distance"].default_value = 0.6
        aom = nt.nodes.new("ShaderNodeMapRange")
        aom.inputs[3].default_value = 0.62
        aom.inputs[4].default_value = 1.0
        L.new(ao.outputs["AO"], aom.inputs[0])
        vs4 = nt.nodes.new("ShaderNodeVectorMath"); vs4.operation = "SCALE"
        L.new(col, vs4.inputs[0]); L.new(aom.outputs[0], vs4.inputs["Scale"])
        col = vs4.outputs[0]
    # painted glints
    if gloss > 0:
        gl = nt.nodes.new("ShaderNodeBsdfGlossy")
        gl.inputs["Roughness"].default_value = 0.18
        s2 = nt.nodes.new("ShaderNodeShaderToRGB")
        L.new(gl.outputs[0], s2.inputs[0])
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        L.new(s2.outputs[0], bw.inputs[0])
        mr2 = nt.nodes.new("ShaderNodeMapRange")
        mr2.inputs[1].default_value = 0.35
        mr2.inputs[2].default_value = 0.6
        mr2.inputs[3].default_value = 0.0
        mr2.inputs[4].default_value = gloss
        L.new(bw.outputs[0], mr2.inputs[0])
        va = nt.nodes.new("ShaderNodeVectorMath"); va.operation = "ADD"
        L.new(col, va.inputs[0]); L.new(mr2.outputs[0], va.inputs[1])
        col = va.outputs[0]
    em = nt.nodes.new("ShaderNodeEmission")
    L.new(col, em.inputs[0])
    em.inputs[1].default_value = 1.0
    shader = em.outputs[0]
    if emit:
        em2 = nt.nodes.new("ShaderNodeEmission")
        em2.inputs[0].default_value = lin(emit)
        em2.inputs[1].default_value = emit_str
        ad = nt.nodes.new("ShaderNodeAddShader")
        L.new(shader, ad.inputs[0]); L.new(em2.outputs[0], ad.inputs[1])
        shader = ad.outputs[0]
    L.new(shader, out.inputs[0])
    _MATS[key] = m
    _PARAMS[m.name] = (base, kw_in)
    return m


_PARAMS = {}


def glow(col, strength=3.0, name=None, alpha=1.0, core=None):
    """Neon / screen emission. `core` whitens the centre (generated-z band) for tube neon."""
    key = ("glow", col, strength, alpha, core)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name or ("glow_" + col))
    m.use_nodes = True
    nt = _nt(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = lin(col)
    em.inputs[1].default_value = strength
    sh = em.outputs[0]
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(sh, mx.inputs[2])
        sh = mx.outputs[0]
        m.surface_render_method = "BLENDED"
        m.use_backface_culling = False
    nt.links.new(sh, out.inputs[0])
    _MATS[key] = m
    return m


def beam(col, strength=1.2, a_near=0.35, a_far=0.0, name="beam"):
    """Searchlight cone: alpha fades from the source (generated z=1) to the ground (z=0)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = _nt(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = a_far
    mr.inputs[4].default_value = a_near
    nt.links.new(sep.outputs[2], mr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = lin(col)
    em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


def flat_col(col, name=None):
    """Unlit flat colour (shadow decals, ink fills)."""
    key = ("flat", col)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name or ("flat_" + col))
    m.use_nodes = True
    nt = _nt(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = lin(col)
    nt.links.new(em.outputs[0], out.inputs[0])
    _MATS[key] = m
    return m


# ------------------------------------------------------------------ geometry
def link_obj(o, coll=None):
    (coll or bpy.context.scene.collection).objects.link(o)
    return o


def set_mat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def bevel(o, width=0.06, segs=2, angle=40):
    b = o.modifiers.new("bev", "BEVEL")
    b.width = width
    b.segments = segs
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle)
    b.harden_normals = False
    me = o.data
    if EDGE_HI["on"] and me is not None and len(me.materials) == 1 and me.materials[0] is not None:
        em = edge_variant(me.materials[0])
        if em is not None:
            me.materials.append(em)
            b.material = 1
    return b


EDGE_HI = {"on": True}


def edge_variant(m):
    """Painted edge highlight: same paint, lifted and warmed (hand-painted worn edges)."""
    prm = _PARAMS.get(m.name)
    if prm is None:
        return None
    base, kw = prm
    if kw.get("edge"):
        return None
    kw = dict(kw)
    kw["edge"] = True
    kw["name"] = (kw.get("name") or ("paint_" + base)) + "_edge"
    return paint(base, **kw)


def mesh_from_bm(bm, name):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def box(size, loc=(0, 0, 0), mat=None, bev=0.06, wonk=0.0, rng=None, rot=(0, 0, 0), name="box",
        coll=None, taper=0.0, segs=2, origin_bottom=True):
    """Chunky box; `wonk` jitters the corners (fraction of size) for the crafted look."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    rng = rng or random.Random(11)
    for v in bm.verts:
        x, y, z = v.co
        top = z > 0
        k = (1.0 - taper) if top else 1.0
        v.co = Vector((x * sx * k, y * sy * k, (z + (0.5 if origin_bottom else 0.0)) * sz))
        if wonk:
            v.co.x += rng.uniform(-1, 1) * wonk * sx
            v.co.y += rng.uniform(-1, 1) * wonk * sy
            v.co.z += rng.uniform(-1, 1) * wonk * sz * (0.5 if top else 0.0)
    o = bpy.data.objects.new(name, mesh_from_bm(bm, name))
    link_obj(o, coll)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if mat:
        set_mat(o, mat)
    if bev:
        bevel(o, bev, segs)
    return o


def cyl(r, h, loc=(0, 0, 0), mat=None, verts=16, bev=0.05, r2=None, wonk=0.0, rng=None, rot=(0, 0, 0),
        name="cyl", coll=None, segs=2, origin_bottom=True, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h)
    rng = rng or random.Random(5)
    for v in bm.verts:
        if origin_bottom:
            v.co.z += h / 2
        if wonk:
            v.co.x += rng.uniform(-1, 1) * wonk * r
            v.co.y += rng.uniform(-1, 1) * wonk * r
    if smooth:
        for f in bm.faces:
            f.smooth = abs(f.normal.z) < 0.5
    o = bpy.data.objects.new(name, mesh_from_bm(bm, name))
    link_obj(o, coll)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if mat:
        set_mat(o, mat)
    if bev:
        bevel(o, bev, segs, angle=50)
    return o


def rock(r, loc, mat, rng, flat=0.6, name="rock", coll=None):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts:
        v.co *= rng.uniform(0.75, 1.2)
        v.co.z *= flat
    o = bpy.data.objects.new(name, mesh_from_bm(bm, name))
    link_obj(o, coll)
    o.location = loc
    o.rotation_euler = (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0, 6.28))
    set_mat(o, mat)
    return o


def prism(poly, h, loc=(0, 0, 0), mat=None, bev=0.05, name="prism", coll=None, rot=(0, 0, 0), segs=2):
    """Extrude a 2D polygon (list of (x,y)) up by h."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in poly]
    f = bm.faces.new(vs)
    if f.normal.z < 0:
        f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = bpy.data.objects.new(name, mesh_from_bm(bm, name))
    link_obj(o, coll)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if mat:
        set_mat(o, mat)
    if bev:
        bevel(o, bev, segs, angle=35)
    return o


def ribbon(pts, width, z, mat, name="ribbon", coll=None, thick=0.03):
    """Flat strip following 2D points (for paths on the ground plane)."""
    bm = bmesh.new()
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = Vector(pts[max(0, i - 1)]); b = Vector(pts[min(n - 1, i + 1)])
        d = (b - a).normalized()
        nrm = Vector((-d.y, d.x))
        left.append(bm.verts.new((p[0] + nrm.x * width / 2, p[1] + nrm.y * width / 2, z)))
        right.append(bm.verts.new((p[0] - nrm.x * width / 2, p[1] - nrm.y * width / 2, z)))
    for i in range(n - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    if thick:
        r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
        for v in [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]:
            v.co.z += thick
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = bpy.data.objects.new(name, mesh_from_bm(bm, name))
    link_obj(o, coll)
    set_mat(o, mat)
    return o


_FONT_CACHE = {}


def font(key):
    f = FONTS.get(key, key)
    if f not in _FONT_CACHE:
        _FONT_CACHE[f] = bpy.data.fonts.load(FONT_DIR + f)
    return _FONT_CACHE[f]


def text(body, size, loc=(0, 0, 0), rot=(90, 0, 0), mat=None, fnt="title", extrude=0.04, bev=0.012,
         align="CENTER", valign="CENTER", name="txt", coll=None, to_mesh=True, spacing=1.0, width=None):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = font(fnt)
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bev
    cu.bevel_resolution = 1
    cu.align_x = align
    cu.align_y = valign
    cu.space_character = spacing
    if width:
        cu.text_boxes[0].width = width
    o = bpy.data.objects.new(name, cu)
    link_obj(o, coll)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if mat:
        cu.materials.append(mat)
    if to_mesh:
        dg = bpy.context.evaluated_depsgraph_get()
        oe = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(oe)
        o2 = bpy.data.objects.new(name, me)
        link_obj(o2, coll)
        o2.matrix_world = o.matrix_world.copy()
        bpy.data.objects.remove(o)
        # merge the extrusion vertices so Freestyle sees clean borders
        return o2
    return o


def parent_keep(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def empty(name="grp", loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    e = bpy.data.objects.new(name, None)
    link_obj(e)
    e.location = loc
    e.rotation_euler = [math.radians(a) for a in rot]
    e.scale = (scale, scale, scale)
    return e


def group(objs, parent):
    for o in objs:
        if o.parent is None:
            o.parent = parent


def tuft(loc, rng, mat_a, mat_b, s=1.0, blades=6, coll=None):
    """Grass tuft: chunky bent leaf blades (flattened cones)."""
    objs = []
    for i in range(blades):
        a = i / blades * 6.283 + rng.uniform(-0.4, 0.4)
        h = s * rng.uniform(0.18, 0.34)
        o = cyl(0.13 * s, h, (loc[0] + math.cos(a) * 0.03 * s, loc[1] + math.sin(a) * 0.03 * s, loc[2]),
                mat_a if i % 2 else mat_b, verts=4, bev=0, r2=0.0, name="blade", coll=coll, smooth=False)
        o.scale = (1.0, 0.35, 1.0)
        o.rotation_euler = (math.cos(a + 1.57) * 0.0 + rng.uniform(0.35, 0.75) * math.sin(a) * -1,
                            rng.uniform(0.35, 0.75) * math.cos(a), a + 1.57)
        objs.append(o)
    return objs
