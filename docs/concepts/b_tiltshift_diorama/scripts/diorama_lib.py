"""TILT-SHIFT DIORAMA: Blender 5.2 helpers (materials, city, highways, billboards, fog, render).

Imported by scene_*.py scripts. Seeded randomness only.
"""
import bpy
import bmesh
import math
import random
import json
from mathutils import Vector, Matrix, Euler


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    # sRGB -> linear
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)


# ----------------------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    return sc


def setup_render(sc, w=1920, h=1080, samples=24, transparent=False, view="AgX", look=None, exposure=0.0):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_raytracing = True
    try:
        ee.ray_tracing_method = "SCREEN"
    except Exception:
        pass
    ee.use_shadows = True
    ee.shadow_pool_size = "1024"
    ee.volumetric_tile_size = "4"
    ee.volumetric_samples = 48
    ee.use_volumetric_shadows = False
    ee.use_fast_gi = True
    try:
        sc.view_settings.view_transform = view
    except TypeError as e:
        print("view transform fallback", e)
    if look:
        try:
            sc.view_settings.look = look
        except TypeError as e:
            print("look fallback", e)
    sc.view_settings.exposure = exposure


def world(sc, col="#05070d", strength=1.0):
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = hexcol(col)
    bg.inputs[1].default_value = strength
    return w


def link(nt, a, b):
    nt.links.new(a, b)


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m


def bsdf_of(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def mat_pbr(name, col, rough=0.5, metal=0.0, emit=None, emit_str=0.0, alpha=1.0, spec=0.5):
    m = new_mat(name)
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = hexcol(col)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = hexcol(emit)
        b.inputs["Emission Strength"].default_value = emit_str
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    return m


def mat_emit(name, col, strength=4.0, alpha=1.0):
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = hexcol(col)
    em.inputs[1].default_value = strength
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = alpha
        link(nt, tr.outputs[0], mix.inputs[1])
        link(nt, em.outputs[0], mix.inputs[2])
        link(nt, mix.outputs[0], out.inputs[0])
        m.surface_render_method = "BLENDED"
    else:
        link(nt, em.outputs[0], out.inputs[0])
    return m


def mat_beam(name, col, strength=1.5, a_near=0.22, a_far=0.02):
    """Light beam volume stand-in: emissive, alpha fading from the source (generated z=1) to the ground (z=0)."""
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    link(nt, tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = a_far
    mr.inputs[4].default_value = a_near
    link(nt, sep.outputs[2], mr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = hexcol(col)
    em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    link(nt, mr.outputs[0], mix.inputs[0])
    link(nt, tr.outputs[0], mix.inputs[1])
    link(nt, em.outputs[0], mix.inputs[2])
    link(nt, mix.outputs[0], out.inputs[0])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


def mat_glass(name, tint="#9fdcff", alpha=0.12, rough=0.04):
    m = new_mat(name)
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = hexcol(tint)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.02
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


def mat_building(name, base="#141a26", wins=("#ffcf8a", "#9fe6ff", "#ff7ac8", "#e8f0ff"), lit=0.35,
                 win_str=2.2, cols_per_unit=5.0, rows_per_unit=4.0, dim=1.0):
    """Slate building with an emissive window grid on side faces (world-space, per-object random)."""
    m = new_mat(name)
    nt = m.node_tree
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = hexcol(base)
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.4
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    link(nt, geo.outputs["Position"], sep.inputs[0])
    # u = (x + y) * cols, v = z * rows
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    link(nt, sep.outputs[0], add.inputs[0]); link(nt, sep.outputs[1], add.inputs[1])
    u = nt.nodes.new("ShaderNodeMath"); u.operation = "MULTIPLY"; u.inputs[1].default_value = cols_per_unit
    link(nt, add.outputs[0], u.inputs[0])
    v = nt.nodes.new("ShaderNodeMath"); v.operation = "MULTIPLY"; v.inputs[1].default_value = rows_per_unit
    link(nt, sep.outputs[2], v.inputs[0])

    def fr(src):
        f = nt.nodes.new("ShaderNodeMath"); f.operation = "FRACT"; link(nt, src, f.inputs[0]); return f

    def fl(src):
        f = nt.nodes.new("ShaderNodeMath"); f.operation = "FLOOR"; link(nt, src, f.inputs[0]); return f

    def band(src, lo, hi):
        a = nt.nodes.new("ShaderNodeMath"); a.operation = "GREATER_THAN"; a.inputs[1].default_value = lo
        c = nt.nodes.new("ShaderNodeMath"); c.operation = "LESS_THAN"; c.inputs[1].default_value = hi
        link(nt, src, a.inputs[0]); link(nt, src, c.inputs[0])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = "MULTIPLY"
        link(nt, a.outputs[0], mm.inputs[0]); link(nt, c.outputs[0], mm.inputs[1])
        return mm

    inwin_u = band(fr(u.outputs[0]).outputs[0], 0.18, 0.82)
    inwin_v = band(fr(v.outputs[0]).outputs[0], 0.28, 0.78)
    inwin = nt.nodes.new("ShaderNodeMath"); inwin.operation = "MULTIPLY"
    link(nt, inwin_u.outputs[0], inwin.inputs[0]); link(nt, inwin_v.outputs[0], inwin.inputs[1])
    # per-cell random
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    link(nt, fl(u.outputs[0]).outputs[0], comb.inputs[0])
    link(nt, fl(v.outputs[0]).outputs[0], comb.inputs[1])
    rmul = nt.nodes.new("ShaderNodeMath"); rmul.operation = "MULTIPLY"; rmul.inputs[1].default_value = 97.0
    link(nt, oi.outputs["Random"], rmul.inputs[0])
    link(nt, rmul.outputs[0], comb.inputs[2])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"
    link(nt, comb.outputs[0], wn.inputs["Vector"])
    litc = nt.nodes.new("ShaderNodeMath"); litc.operation = "GREATER_THAN"; litc.inputs[1].default_value = 1.0 - lit
    link(nt, wn.outputs["Value"], litc.inputs[0])
    # side faces only
    nsep = nt.nodes.new("ShaderNodeSeparateXYZ"); link(nt, geo.outputs["Normal"], nsep.inputs[0])
    nabs = nt.nodes.new("ShaderNodeMath"); nabs.operation = "ABSOLUTE"; link(nt, nsep.outputs[2], nabs.inputs[0])
    side = nt.nodes.new("ShaderNodeMath"); side.operation = "LESS_THAN"; side.inputs[1].default_value = 0.5
    link(nt, nabs.outputs[0], side.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    link(nt, inwin.outputs[0], m1.inputs[0]); link(nt, litc.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    link(nt, m1.outputs[0], m2.inputs[0]); link(nt, side.outputs[0], m2.inputs[1])
    # window colour from object random + cell random
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "CONSTANT"
    for i, c in enumerate(wins):
        if i < len(cr.elements):
            e = cr.elements[i]
            e.position = i / len(wins)
        else:
            e = cr.elements.new(i / len(wins))
        e.color = hexcol(c)
    mixr = nt.nodes.new("ShaderNodeMath"); mixr.operation = "ADD"
    link(nt, oi.outputs["Random"], mixr.inputs[0])
    wr = nt.nodes.new("ShaderNodeMath"); wr.operation = "MULTIPLY"; wr.inputs[1].default_value = 0.35
    link(nt, wn.outputs["Value"], wr.inputs[0]); link(nt, wr.outputs[0], mixr.inputs[1])
    frr = nt.nodes.new("ShaderNodeMath"); frr.operation = "FRACT"; link(nt, mixr.outputs[0], frr.inputs[0])
    link(nt, frr.outputs[0], ramp.inputs[0])
    strength = nt.nodes.new("ShaderNodeMath"); strength.operation = "MULTIPLY"
    strength.inputs[1].default_value = win_str * dim
    link(nt, m2.outputs[0], strength.inputs[0])
    link(nt, ramp.outputs[0], b.inputs["Emission Color"])
    link(nt, strength.outputs[0], b.inputs["Emission Strength"])
    return m


def mat_asphalt(name="asphalt", col="#0b0e14"):
    m = new_mat(name)
    nt = m.node_tree
    b = bsdf_of(m)
    b.inputs["Base Color"].default_value = hexcol(col)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.35
    noise.inputs["Detail"].default_value = 6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.02, 1)
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (0.55, 0.55, 0.55, 1)
    link(nt, noise.outputs["Fac"], ramp.inputs[0])
    link(nt, ramp.outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.7
    return m


def mat_holo(name, col, strength=5.0, alpha=0.55, seed=0, bands=38.0):
    """Hologram billboard: blocky illegible glyph rows x scan bands, translucent emissive."""
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); link(nt, tc.outputs["UV"], sep.inputs[0])
    # glyph cells
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 14.0
    mv = nt.nodes.new("ShaderNodeMath"); mv.operation = "MULTIPLY"; mv.inputs[1].default_value = 6.0
    link(nt, sep.outputs[0], mu.inputs[0]); link(nt, sep.outputs[1], mv.inputs[0])
    fu = nt.nodes.new("ShaderNodeMath"); fu.operation = "FLOOR"; link(nt, mu.outputs[0], fu.inputs[0])
    fv = nt.nodes.new("ShaderNodeMath"); fv.operation = "FLOOR"; link(nt, mv.outputs[0], fv.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ"); link(nt, fu.outputs[0], comb.inputs[0]); link(nt, fv.outputs[0], comb.inputs[1])
    comb.inputs[2].default_value = seed * 1.37
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"
    link(nt, comb.outputs[0], wn.inputs["Vector"])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.45
    link(nt, wn.outputs["Value"], gt.inputs[0])
    # sub-cell shape: fract bands
    ffu = nt.nodes.new("ShaderNodeMath"); ffu.operation = "FRACT"; link(nt, mu.outputs[0], ffu.inputs[0])
    ffv = nt.nodes.new("ShaderNodeMath"); ffv.operation = "FRACT"; link(nt, mv.outputs[0], ffv.inputs[0])
    lu = nt.nodes.new("ShaderNodeMath"); lu.operation = "LESS_THAN"; lu.inputs[1].default_value = 0.78
    lv = nt.nodes.new("ShaderNodeMath"); lv.operation = "LESS_THAN"; lv.inputs[1].default_value = 0.55
    link(nt, ffu.outputs[0], lu.inputs[0]); link(nt, ffv.outputs[0], lv.inputs[0])
    g1 = nt.nodes.new("ShaderNodeMath"); g1.operation = "MULTIPLY"; link(nt, lu.outputs[0], g1.inputs[0]); link(nt, lv.outputs[0], g1.inputs[1])
    g2 = nt.nodes.new("ShaderNodeMath"); g2.operation = "MULTIPLY"; link(nt, g1.outputs[0], g2.inputs[0]); link(nt, gt.outputs[0], g2.inputs[1])
    # scan bands
    sb = nt.nodes.new("ShaderNodeMath"); sb.operation = "MULTIPLY"; sb.inputs[1].default_value = bands
    link(nt, sep.outputs[1], sb.inputs[0])
    sn = nt.nodes.new("ShaderNodeMath"); sn.operation = "SINE"; link(nt, sb.outputs[0], sn.inputs[0])
    sm = nt.nodes.new("ShaderNodeMapRange"); sm.inputs[1].default_value = -1; sm.inputs[2].default_value = 1
    sm.inputs[3].default_value = 0.45; sm.inputs[4].default_value = 1.0
    link(nt, sn.outputs[0], sm.inputs[0])
    # frame border glow: base 0.25 everywhere + glyphs
    base = nt.nodes.new("ShaderNodeMath"); base.operation = "MULTIPLY_ADD"
    base.inputs[1].default_value = 0.85; base.inputs[2].default_value = 0.18
    link(nt, g2.outputs[0], base.inputs[0])
    tot = nt.nodes.new("ShaderNodeMath"); tot.operation = "MULTIPLY"
    link(nt, base.outputs[0], tot.inputs[0]); link(nt, sm.outputs[0], tot.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = hexcol(col)
    es = nt.nodes.new("ShaderNodeMath"); es.operation = "MULTIPLY"; es.inputs[1].default_value = strength
    link(nt, tot.outputs[0], es.inputs[0]); link(nt, es.outputs[0], em.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    am = nt.nodes.new("ShaderNodeMath"); am.operation = "MULTIPLY"; am.inputs[1].default_value = alpha
    link(nt, tot.outputs[0], am.inputs[0])
    link(nt, am.outputs[0], mix.inputs[0])
    link(nt, tr.outputs[0], mix.inputs[1]); link(nt, em.outputs[0], mix.inputs[2])
    link(nt, mix.outputs[0], out.inputs[0])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


def mat_fog(name, density=0.25, col="#8aa6c8", scale=0.6, seed=0):
    """Patchy volumetric fog pocket: noise-shaped density with a soft spherical falloff."""
    m = new_mat(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = hexcol(col)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.noise_dimensions = "4D"
    noise.inputs["W"].default_value = seed * 3.1
    noise.inputs["Scale"].default_value = 2.2 * scale
    noise.inputs["Detail"].default_value = 3
    link(nt, tc.outputs["Object"], noise.inputs["Vector"])
    # radial falloff from object centre (object coords in -1..1)
    vl = nt.nodes.new("ShaderNodeVectorMath"); vl.operation = "LENGTH"
    link(nt, tc.outputs["Object"], vl.inputs[0])
    fall = nt.nodes.new("ShaderNodeMapRange"); fall.inputs[1].default_value = 1.0; fall.inputs[2].default_value = 0.2
    link(nt, vl.outputs["Value"], fall.inputs[0])
    nr = nt.nodes.new("ShaderNodeMapRange"); nr.inputs[1].default_value = 0.42; nr.inputs[2].default_value = 0.72
    link(nt, noise.outputs["Fac"], nr.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    link(nt, fall.outputs[0], mul.inputs[0]); link(nt, nr.outputs[0], mul.inputs[1])
    d = nt.nodes.new("ShaderNodeMath"); d.operation = "MULTIPLY"; d.inputs[1].default_value = density
    link(nt, mul.outputs[0], d.inputs[0])
    link(nt, d.outputs[0], vol.inputs["Density"])
    # faint self-glow so pockets read as lit mist from the neon around them
    em = nt.nodes.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = 0.35
    link(nt, d.outputs[0], em.inputs[0])
    vol.inputs["Emission Color"].default_value = hexcol(col)
    link(nt, em.outputs[0], vol.inputs["Emission Strength"])
    link(nt, vol.outputs[0], out.inputs["Volume"])
    return m


# ----------------------------------------------------------------------------- geometry

def box(name, loc, size, mat=None, coll=None, rot=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def cyl(name, loc, r, depth, mat=None, verts=24, rot=None, coll=None, r2=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def plane(name, loc, sx, sy, mat=None, rot=None, coll=None):
    me = bpy.data.meshes.new(name)
    hx, hy = sx / 2, sy / 2
    me.from_pydata([(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)], [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    uv = me.uv_layers[0].data
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv[i].uv = c
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    if mat:
        me.materials.append(mat)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def catmull(pts, n=10):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1]), Vector(P[i + 2]))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Vector(pts[-1]))
    return out


def fillet_path(pts, z, r=1.8, step=0.6, arc_seg=10):
    """Straight roads with round fillets at the corners (no spline overshoot loops)."""
    P = [Vector((x, y, z)) for x, y in pts]
    ends = []
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        din = (b - a).normalized()
        dout = (c - b).normalized()
        rr = min(r, (b - a).length * 0.45, (c - b).length * 0.45)
        p0, p1 = b - din * rr, b + dout * rr
        # straight run to p0
        L = (p0 - out[-1]).length
        n = max(1, int(L / step))
        for k in range(1, n + 1):
            out.append(out[-1].lerp(p0, 1 / (n - k + 1)))
        for k in range(1, arc_seg + 1):
            t = k / arc_seg
            out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p1)
    L = (P[-1] - out[-1]).length
    n = max(1, int(L / step))
    last = out[-1].copy()
    for k in range(1, n + 1):
        out.append(last.lerp(P[-1], k / n))
    return out


def ribbon(name, path, width, thick, mat, coll=None, offset=0.0, zoff=0.0):
    """Box-profile sweep along a polyline (list of Vector). offset shifts sideways."""
    verts, faces = [], []
    n = len(path)
    for i, p in enumerate(path):
        a = path[max(0, i - 1)]
        b = path[min(n - 1, i + 1)]
        t = (b - a)
        t.z = 0
        if t.length < 1e-6:
            t = Vector((1, 0, 0))
        t.normalize()
        side = Vector((-t.y, t.x, 0))
        c = p + side * offset + Vector((0, 0, zoff))
        hw = width / 2
        verts += [c - side * hw, c + side * hw, c + side * hw - Vector((0, 0, thick)), c - side * hw - Vector((0, 0, thick))]
    for i in range(n - 1):
        o, q = i * 4, (i + 1) * 4
        faces += [(o, o + 1, q + 1, q), (o + 1, o + 2, q + 2, q + 1), (o + 2, o + 3, q + 3, q + 2), (o + 3, o, q, q + 3)]
    faces += [(0, 3, 2, 1), ((n - 1) * 4, (n - 1) * 4 + 1, (n - 1) * 4 + 2, (n - 1) * 4 + 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def dashed(name, path, width, mat, rng, dash=(0.25, 1.2), gap=(0.15, 0.9), offset=0.0, zoff=0.05, coll=None):
    """Light-trail dashes along a path, merged into one mesh."""
    verts, faces = [], []
    # arc-length param
    L = [0.0]
    for a, b in zip(path, path[1:]):
        L.append(L[-1] + (b - a).length)

    def at(s):
        for i in range(len(L) - 1):
            if L[i + 1] >= s:
                t = (s - L[i]) / max(1e-6, L[i + 1] - L[i])
                p = path[i].lerp(path[i + 1], t)
                d = (path[i + 1] - path[i])
                d.z = 0
                d.normalize()
                return p, d
        d = path[-1] - path[-2]; d.z = 0; d.normalize()
        return path[-1], d

    s = rng.uniform(0, 1.0)
    while s < L[-1] - 0.1:
        ln = rng.uniform(*dash)
        seg = []
        k = 4
        for j in range(k + 1):
            p, d = at(min(L[-1], s + ln * j / k))
            side = Vector((-d.y, d.x, 0))
            c = p + side * offset + Vector((0, 0, zoff))
            seg.append((c - side * width / 2, c + side * width / 2))
        base = len(verts)
        for a, b in seg:
            verts += [tuple(a), tuple(b)]
        for j in range(k):
            o = base + j * 2
            faces.append((o, o + 1, o + 3, o + 2))
        s += ln + rng.uniform(*gap)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def text_obj(name, body, loc, size, mat, rot=(0, 0, 0), extrude=0.0, align="CENTER", coll=None, font=None):
    cu = bpy.data.curves.new(name, type="FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    if font:
        cu.font = bpy.data.fonts.load(font, check_existing=True)
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = rot
    cu.materials.append(mat)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def tube_poly(name, pts, radius, mat, coll=None, cyclic=False):
    """Neon tube along 3D points (a bevelled poly curve)."""
    cu = bpy.data.curves.new(name, type="CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def point_light(name, loc, col, energy, radius=0.2, coll=None, shadow=False):
    ld = bpy.data.lights.new(name, "POINT")
    ld.use_shadow = shadow
    ld.color = hexcol(col)[:3]
    ld.energy = energy
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def spot_light(name, loc, rot, col, energy, angle=0.4, blend=0.3, coll=None, radius=0.1):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.color = hexcol(col)[:3]
    ld.energy = energy
    ld.spot_size = angle
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def area_light(name, loc, rot, col, energy, size=4.0, coll=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.color = hexcol(col)[:3]
    ld.energy = energy
    ld.size = size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def iso_camera(sc, target=(0, 0, 0), ortho=40.0, dist=60.0, tilt=58.0, yaw=45.0, name="Cam"):
    cd = bpy.data.cameras.new(name)
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_start = 1.0
    cd.clip_end = 200.0
    cam = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(cam)
    rot = Euler((math.radians(tilt), 0, math.radians(yaw)), "XYZ")
    fwd = rot.to_matrix() @ Vector((0, 0, -1))
    cam.location = Vector(target) - fwd * dist
    cam.rotation_euler = rot
    sc.camera = cam
    return cam


# ----------------------------------------------------------------------------- city

INKS = ["#ff3da8", "#5ce1ff", "#d4ff00", "#b04dff", "#ff8c1a"]


class City:
    """Procedural diorama city. All placement from one seeded RNG."""

    def __init__(self, seed=7, blocks=9, block=3.2, street=1.1, dim=1.0, hq=(0, 0), heat=False, map_z=4.6, win_scale=1.0):
        self.rng = random.Random(seed)
        self.blocks = blocks
        self.block = block
        self.street = street
        self.pitch = block + street
        self.dim = dim
        self.hq = hq
        self.heat = heat
        self.map_z = map_z
        self.coll = bpy.data.collections.new("City")
        bpy.context.scene.collection.children.link(self.coll)
        self.fog_objs = []
        self.map_objs = []
        self.nodes = []
        r = self.rng
        self.mats_b = [
            mat_building(f"bld{i}", base=b, lit=l, dim=dim, cols_per_unit=c * win_scale, rows_per_unit=rr * win_scale)
            for i, (b, l, c, rr) in enumerate([
                ("#1c2334", 0.22, 3.2, 2.6), ("#221f30", 0.3, 4.0, 3.2), ("#182030", 0.16, 2.6, 2.2),
                ("#232a3a", 0.34, 5.0, 4.0), ("#1a1d28", 0.12, 3.0, 2.4)])
        ]
        self.m_side = mat_pbr("sidewalk", "#1a1f29", rough=0.35)
        self.m_asph = mat_asphalt()
        self.m_roof = mat_pbr("roofkit", "#232a36", rough=0.6, metal=0.3)
        self.m_ink = [mat_emit(f"ink{i}", c, 6.0 * dim) for i, c in enumerate(INKS)]
        self.m_blink = mat_emit("blink_red", "#ff2a2a", 30.0)

    def cell_center(self, i, j):
        n = self.blocks
        o = (n - 1) / 2
        return Vector(((i - o) * self.pitch, (j - o) * self.pitch, 0))

    def build_ground(self):
        size = self.blocks * self.pitch + 30
        plane("ground", (0, 0, 0), size, size, self.m_asph, coll=self.coll)

    def build_blocks(self, hq_cell=(4, 4), skip=(), height_fn=None):
        r = self.rng
        n = self.blocks
        for i in range(n):
            for j in range(n):
                c = self.cell_center(i, j)
                box(f"walk_{i}_{j}", c + Vector((0, 0, 0.06)), (self.block, self.block, 0.12), self.m_side, self.coll)
                if (i, j) in skip:
                    continue
                if (i, j) == hq_cell:
                    self.build_hq(c)
                    continue
                # 2x2 or 3x3 lots per block
                lots = r.choice([2, 2, 3])
                lot = (self.block - 0.3) / lots
                d = math.dist((i, j), hq_cell)
                for a in range(lots):
                    for b in range(lots):
                        if r.random() < 0.08:
                            continue
                        lx = c.x - self.block / 2 + 0.15 + lot * (a + 0.5)
                        ly = c.y - self.block / 2 + 0.15 + lot * (b + 0.5)
                        base_h = height_fn(i, j, d, r) if height_fn else r.uniform(0.6, 3.6)
                        cap = self.height_cap(lx, ly)
                        if cap is not None:
                            base_h = min(base_h, cap)
                        self.building(Vector((lx, ly, 0.12)), lot * r.uniform(0.72, 0.92), base_h)

    def height_cap(self, x, y):
        """Buildings under an elevated highway stay below its deck."""
        cap = None
        for path in getattr(self, "hw_paths", []):
            for a, b in zip(path, path[1:]):
                ab = Vector((b.x - a.x, b.y - a.y))
                ap = Vector((x - a.x, y - a.y))
                t = max(0.0, min(1.0, ap.dot(ab) / max(ab.length_squared, 1e-6)))
                dd = (ap - ab * t).length
                if dd < 2.1:
                    zc = (a.z - 0.5) / 1.6
                    cap = zc if cap is None else min(cap, zc)
        return None if cap is None else max(0.25, cap)

    def building(self, p, w, h):
        r = self.rng
        m = r.choice(self.mats_b)
        wx, wy = w * r.uniform(0.8, 1.0), w * r.uniform(0.8, 1.0)
        b = box("b", p + Vector((0, 0, h / 2)), (wx, wy, h), m, self.coll)
        top = h
        if h > 1.6 and r.random() < 0.55:  # setback tier
            h2 = h * r.uniform(0.25, 0.6)
            box("b2", p + Vector((0, 0, top + h2 / 2)), (wx * 0.7, wy * 0.7, h2), m, self.coll)
            top += h2
        if r.random() < 0.3:  # neon trim ring
            ink = r.choice(self.m_ink)
            box("trim", p + Vector((0, 0, h - 0.04)), (wx + 0.03, wy + 0.03, 0.035), ink, self.coll)
        if r.random() < 0.5:  # roof kit
            box("hvac", p + Vector((r.uniform(-0.2, 0.2) * wx, r.uniform(-0.2, 0.2) * wy, top + 0.08)),
                (wx * 0.3, wy * 0.25, 0.16), self.m_roof, self.coll)
        if top > 3.0 and r.random() < 0.5:
            cyl("ant", p + Vector((0, 0, top + 0.4)), 0.02, 0.8, self.m_roof, 6, coll=self.coll)
            cyl("blink", p + Vector((0, 0, top + 0.82)), 0.05, 0.06, self.m_blink, 8, coll=self.coll)
        return top

    def build_hq(self, c):
        """The Cell's HQ: tall stepped tower, pink crown, CELL_ACID beacon."""
        m = mat_building("hq_mat", base="#1a1624", wins=("#ff7ac8", "#ffd0ea", "#9fe6ff"), lit=0.45,
                         dim=self.dim, cols_per_unit=4, rows_per_unit=3.2)
        pink = mat_emit("hq_pink", "#ff3da8", 9.0 * self.dim)
        acid = mat_emit("hq_acid", "#d4ff00", 14.0 * self.dim)
        z = 0.12
        tiers = [(3.0, 4.4), (2.4, 4.2), (1.8, 3.6), (1.25, 3.0)]
        for k, (w, h) in enumerate(tiers):
            box(f"hq{k}", c + Vector((0, 0, z + h / 2)), (w, w, h), m, self.coll)
            for sx, sy in ((1, 1), (1, -1), (-1, -1)):  # neon corner strips on the visible edges
                box("hqedge", c + Vector((sx * w / 2, sy * w / 2, z + h / 2)), (0.05, 0.05, h * 0.96), pink, self.coll)
            box(f"hqtrim{k}", c + Vector((0, 0, z + h - 0.05)), (w + 0.05, w + 0.05, 0.06), pink, self.coll)
            z += h
        # crown fins
        for k in range(4):
            a = k * math.pi / 2
            box("fin", c + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, z + 0.7)), (0.08, 0.08, 1.4), pink, self.coll)
        cyl("mast", c + Vector((0, 0, z + 1.4)), 0.05, 2.8, self.m_roof, 8, coll=self.coll)
        # Cell hex halo around the crown and a hex emblem on the two camera-facing faces
        hexr = [(c.x + 1.25 * math.cos(k * math.pi / 3 + math.pi / 6), c.y + 1.25 * math.sin(k * math.pi / 3 + math.pi / 6), z + 0.5) for k in range(6)]
        tube_poly("hq_halo", hexr, 0.045, pink, self.coll, cyclic=True)
        zz = 0.12 + tiers[0][1] + tiers[1][1] * 0.5
        for fx, fy, ax in ():
            w1 = tiers[1][0] / 2 + 0.04
            pts = []
            for k in range(6):
                a = k * math.pi / 3 + math.pi / 2
                u, v = 0.8 * math.cos(a), 0.8 * math.sin(a)
                if ax == "x":
                    pts.append((c.x + u, c.y + fy * w1, zz + v))
                else:
                    pts.append((c.x + fx * w1, c.y + u, zz + v))
            tube_poly("hq_hex", pts, 0.06, acid, self.coll, cyclic=True)
        point_light("hq_face", c + Vector((1.8, -1.8, zz)), "#d4ff00", 250 * self.dim, 0.5, self.coll)
        cyl("beacon", c + Vector((0, 0, z + 2.85)), 0.14, 0.14, acid, 12, coll=self.coll)
        point_light("hq_glow", c + Vector((0, 0, z + 1.0)), "#ff3da8", 900 * self.dim, 1.0, self.coll)
        # vertical CELL blade sign on tower face
        self.hq_top = z + 3.0
        self.hq_c = c
        return z

    def street_traffic(self, seed=5):
        """Ground-level traffic: head/tail light dashes along every street."""
        r = random.Random(seed)
        n = self.blocks
        half = (n * self.pitch) / 2
        tail = mat_emit("gtail", "#ff3344", 9 * self.dim)
        head = mat_emit("ghead", "#ffe6c0", 8 * self.dim)
        for k in range(n + 1):
            s = (k - n / 2) * self.pitch
            if k % 2:
                continue
            for axis in (0, 1):
                a = Vector((s, -half, 0.02)) if axis == 0 else Vector((-half, s, 0.02))
                b = Vector((s, half, 0.02)) if axis == 0 else Vector((half, s, 0.02))
                path = [a.lerp(b, t / 40) for t in range(41)]
                dashed("gt", path, 0.06, tail, r, dash=(0.15, 0.5), gap=(1.5, 5.0), offset=0.3, zoff=0.0, coll=self.coll)
                dashed("gh", path, 0.06, head, r, dash=(0.15, 0.5), gap=(1.5, 5.0), offset=-0.3, zoff=0.0, coll=self.coll)

    def street_lights(self, every=2, energy=60.0):
        r = self.rng
        n = self.blocks
        for i in range(n + 1):
            for j in range(n + 1):
                if (i + j) % every:
                    continue
                c = self.cell_center(i, j) - Vector((self.pitch / 2, self.pitch / 2, 0))
                warm = r.random() < 0.55
                col = r.choice(["#ffb35c", "#ff9a3d"]) if warm else r.choice(["#5cd0ff", "#7fa8ff", "#ff5cc0"])
                point_light("sl", c + Vector((r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), 0.5)), col,
                            energy * self.dim * r.uniform(0.6, 1.3), 0.3, self.coll)

    def highway(self, pts, z, lanes_col=("#ff3344", "#fff2d8"), width=0.9, n_pylons=8, seed=1):
        r = random.Random(seed)
        path = fillet_path(pts, z)
        if not hasattr(self, "hw_paths"):
            self.hw_paths = []
        self.hw_paths.append(path)
        deck = mat_pbr("deck", "#20252f", rough=0.45, metal=0.2)
        ribbon("hw", path, width, 0.16, deck, self.coll)
        rail = mat_emit("rail", "#5ce1ff", 2.5 * self.dim)
        ribbon("rail_l", path, 0.03, 0.03, rail, self.coll, offset=width / 2, zoff=0.06)
        ribbon("rail_r", path, 0.03, 0.03, rail, self.coll, offset=-width / 2, zoff=0.06)
        tail = mat_emit("tail", lanes_col[0], 14 * self.dim)
        head = mat_emit("head", lanes_col[1], 12 * self.dim)
        dashed("trail_t", path, 0.07, tail, r, offset=width * 0.22, zoff=0.03, coll=self.coll)
        dashed("trail_h", path, 0.07, head, r, offset=-width * 0.22, zoff=0.03, coll=self.coll)
        pyl = mat_pbr("pylon", "#262b35", rough=0.7)
        acc, nxt = 0.0, 2.0
        for a, b in zip(path, path[1:]):
            acc += (b - a).length
            if acc < nxt:
                continue
            nxt += 4.3
            p = b
            cyl("pylon", Vector((p.x, p.y, (p.z - 0.16) / 2)), 0.12, p.z - 0.16, pyl, 10, coll=self.coll)
        return path

    def flying_cars(self, count, zr=(5.5, 8.5), extent=16.0, seed=3):
        r = random.Random(seed)
        body = mat_pbr("car", "#2a2f3a", rough=0.3, metal=0.6)
        t_red = mat_emit("car_tail", "#ff3355", 16 * self.dim)
        t_cy = mat_emit("car_tail_c", "#8ff0ff", 16 * self.dim)
        for k in range(count):
            p = Vector((r.uniform(-extent, extent), r.uniform(-extent, extent), r.uniform(*zr)))
            yaw = r.choice([0, math.pi / 2, math.pi, -math.pi / 2]) + r.uniform(-0.1, 0.1)
            d = Vector((math.cos(yaw), math.sin(yaw), 0))
            box("fcar", p, (0.6, 0.28, 0.14), body, self.coll, rot=(0, 0, yaw))
            box("fcar_top", p + Vector((0, 0, 0.09)), (0.3, 0.22, 0.06), body, self.coll, rot=(0, 0, yaw))
            m = t_red if r.random() < 0.6 else t_cy
            # light trail behind (tapered segments)
            for s in range(7):
                q = p - d * (0.4 + s * 0.3)
                box("ftrail", q, (0.28, 0.06 * (1 - s / 8), 0.03), m, self.coll, rot=(0, 0, yaw))

    def flying_lane(self, p0, p1, z, count, seed, cols=("#ff3355", "#8ff0ff")):
        """A sky lane: evenly spaced hover-cars with long light trails (motion read in a still)."""
        r = random.Random(seed)
        body = mat_pbr("lanecar", "#3a404c", rough=0.3, metal=0.6)
        mats = [mat_emit(f"lane_{c}", c, 18 * self.dim) for c in cols]
        a, b = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
        d = (b - a).normalized()
        yaw = math.atan2(d.y, d.x)
        for k in range(count):
            t = (k + r.uniform(-0.3, 0.3)) / count
            p = a.lerp(b, t) + Vector((0, 0, r.uniform(-0.25, 0.25)))
            fwd = 1 if k % 2 else -1
            box("lcar", p, (0.7, 0.3, 0.16), body, self.coll, rot=(0, 0, yaw))
            box("lcar_top", p + Vector((0, 0, 0.11)), (0.34, 0.24, 0.07), body, self.coll, rot=(0, 0, yaw))
            m = mats[0] if fwd > 0 else mats[1]
            L = r.uniform(1.5, 3.2)
            box("ltrail", p - d * fwd * (0.35 + L / 2), (L, 0.05, 0.03), m, self.coll, rot=(0, 0, yaw))
            box("ltrail2", p - d * fwd * (0.35 + L / 3), (L * 0.66, 0.1, 0.02), mat_emit("ltr_soft", "#ffb0c0", 4 * self.dim, alpha=0.35), self.coll, rot=(0, 0, yaw))

    def billboard(self, loc, w, h, col, yaw, seed, projector=True, alpha=0.6, strength=5.0):
        m = mat_holo(f"holo{seed}", col, strength * self.dim, alpha, seed)
        pl = plane("holo", loc, w, h, m, rot=(math.pi / 2, 0, yaw), coll=self.coll)
        frame = mat_emit(f"hframe{seed}", col, 5 * self.dim)
        if projector:
            # projector beam: translucent emissive frustum from a base emitter
            beam = mat_emit(f"beam{seed}", col, 1.4 * self.dim, alpha=0.13)
            base = Vector(loc) - Vector((0, 0, h / 2 + 0.9))
            d = Vector((math.cos(yaw), math.sin(yaw), 0))
            corners = [Vector(loc) + d * sx * w / 2 + Vector((0, 0, sz * h / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            me = bpy.data.meshes.new("beam")
            vs = [tuple(base)] + [tuple(c) for c in corners]
            me.from_pydata(vs, [], [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)])
            me.materials.append(beam)
            ob = bpy.data.objects.new("beam", me)
            self.coll.objects.link(ob)
            cyl("proj", base, 0.08, 0.06, frame, 10, coll=self.coll)
            self.fog_objs.append(ob)  # excluded from depth pass like fog
        self.fog_objs.append(pl)
        return pl

    def fog_pocket(self, loc, size, density, col="#7d97bd", seed=0):
        m = mat_fog(f"fog{seed}", density, col, seed=seed)
        me = bpy.data.meshes.new("fog")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        ob = bpy.data.objects.new("fog", me)
        ob.location = loc
        ob.scale = size
        self.coll.objects.link(ob)
        self.fog_objs.append(ob)
        return ob

    # --- the raid/grid map: nodes AND links on one plane (feedback 7.4)
    def map_layer(self, nodes, links_, z=None):
        z = self.map_z if z is None else z
        coll = bpy.data.collections.new("Map")
        bpy.context.scene.collection.children.link(coll)
        colmat = {}

        def mm(c, s, a=1.0):
            k = (c, s, a)
            if k not in colmat:
                colmat[k] = mat_emit(f"map_{c}_{s}", c, s, alpha=a)
            return colmat[k]

        plate = mat_glass("mapglass", "#0a1a2e", alpha=0.10, rough=0.2)
        for (a, b, kind) in links_:
            pa = Vector((nodes[a][0], nodes[a][1], z))
            pb = Vector((nodes[b][0], nodes[b][1], z))
            col = {"cell": "#d4ff00", "threat": "#ff4433", "net": "#5ce1ff"}[kind]
            wid = 0.2 if kind != "net" else 0.12
            ob = ribbon("link", [pa, pb], wid, 0.02, mm(col, 7.0), coll)
            self.map_objs.append(ob)
        for name, (x, y, kind) in nodes.items():
            col = {"cell": "#d4ff00", "corp": "#3dff8b", "boss": "#ff4433", "hq": "#ff3da8", "open": "#5ce1ff"}[kind]
            p = Vector((x, y, z))
            if kind == "hq":  # the CORE: a hex halo ring around the tower on the same plane
                for rr, ww in ((2.3, 0.14), (2.0, 0.05)):
                    pts = [(p.x + rr * math.cos(k * math.pi / 3), p.y + rr * math.sin(k * math.pi / 3), z) for k in range(6)]
                    self.map_objs.append(tube_poly("corering", pts, ww, mm(col, 9.0), coll, cyclic=True))
                self.nodes.append((name, p, kind))
                continue
            # hex pad (6-sided disc) + ring
            pad = cyl("pad", p, 1.0, 0.05, plate, 6, coll=coll)
            ring = cyl("ring", p + Vector((0, 0, 0.03)), 1.0, 0.02, mm(col, 9.0), 6, coll=coll)
            inner = cyl("inner", p + Vector((0, 0, 0.04)), 0.84, 0.03, mat_pbr("padin", "#0b1220", rough=0.3), 6, coll=coll)
            dot = cyl("dot", p + Vector((0, 0, 0.06)), 0.26, 0.02, mm(col, 14.0), 6, coll=coll)
            self.map_objs += [pad, ring, inner, dot]
            self.nodes.append((name, p, kind))
        return coll


# ----------------------------------------------------------------------------- render passes

def depth_pass(sc, path, near, far, keep_sharp=(), hide=()):
    """Render a depth PNG (0=near, 1=far). keep_sharp objects are written as depth=focus (0.0)."""
    dm = new_mat("DEPTH")
    nt = dm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    cd = nt.nodes.new("ShaderNodeCameraData")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[1].default_value = near
    mr.inputs[2].default_value = far
    em = nt.nodes.new("ShaderNodeEmission")
    link(nt, cd.outputs["View Z Depth"], mr.inputs[0])
    link(nt, mr.outputs[0], em.inputs[0])
    link(nt, em.outputs[0], out.inputs[0])
    sharp = mat_emit("SHARP", "#000000", 0.0)
    sharp_ids = {o.name for o in keep_sharp}
    hide_ids = {o.name for o in hide}
    for ob in sc.objects:
        if ob.name in hide_ids:
            ob.hide_render = True
            continue
        if ob.type in ("MESH", "CURVE", "FONT"):
            m = sharp if ob.name in sharp_ids else dm
            data = ob.data
            if len(data.materials) == 0:
                data.materials.append(m)
            for i in range(len(data.materials)):
                data.materials[i] = m
        if ob.type == "LIGHT":
            ob.hide_render = True
    next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs[0].default_value = (1, 1, 1, 1)
    for vt in ("Raw", "Standard"):
        try:
            sc.view_settings.view_transform = vt
            break
        except TypeError:
            pass
    try:
        sc.view_settings.look = "None"
    except TypeError:
        pass
    sc.view_settings.exposure = 0.0
    sc.render.film_transparent = False
    sc.render.image_settings.color_mode = "BW"
    sc.render.image_settings.color_depth = "16"
    sc.eevee.taa_render_samples = 4
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def project(sc, cam, p):
    from bpy_extras.object_utils import world_to_camera_view
    co = world_to_camera_view(sc, cam, Vector(p))
    return (co.x * sc.render.resolution_x, (1 - co.y) * sc.render.resolution_y)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
