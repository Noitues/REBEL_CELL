"""RISO PUNK ZINE: Blender 5.2 helpers shared by the still scripts.

Paper cards (image planes with real thickness-less shadows), stacked cut-paper discs,
peeling stickers, and a Grease Pencil v3 marker hand (single-stroke letters, write-on,
drips, circles, arrows, scribbles). Imported by still_*.py.
"""
import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

TEX = None  # set by init()


def init(tex_dir):
    global TEX
    TEX = tex_dir


def lin(c):
    """sRGB 0-255 (or 0-1) tuple -> linear RGBA."""
    out = []
    for v in c[:3]:
        v = v / 255.0 if max(c[:3]) > 1.0 else v
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)


C = {
    "pink": (255, 72, 176), "pink_dk": (200, 30, 120), "cyan": (92, 225, 255), "black": (26, 24, 28),
    "acid": (212, 255, 0), "white": (250, 250, 246), "harm": (255, 68, 51), "amber": (255, 176, 0),
    "orange": (255, 140, 26), "gain": (123, 224, 123), "violet": (176, 77, 255), "paper": (242, 238, 228),
}


# ----------------------------------------------------------------------------- scene
def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)


def setup(samples=48, world=(6, 8, 20), world_strength=1.0, glare=True, glare_threshold=1.0, glare_strength=1.0, glare_size=0.55):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_shadows = True
    sc.eevee.shadow_pool_size = "1024"
    try:
        sc.eevee.use_raytracing = True
        sc.eevee.use_fast_gi = True
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    w = bpy.data.worlds.new("w") if not sc.world else sc.world
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = lin(world)
    bg.inputs[1].default_value = world_strength
    if glare:
        ng = bpy.data.node_groups.new("riso_comp", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        g = ng.nodes.new("CompositorNodeGlare")
        for key, val in (("Type", "Bloom"), ("Quality", "High")):
            try:
                g.inputs[key].default_value = val
            except Exception as e:
                print("glare menu", key, e)
        g.inputs["Threshold"].default_value = glare_threshold
        g.inputs["Strength"].default_value = glare_strength
        g.inputs["Size"].default_value = glare_size
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], g.inputs["Image"])
        ng.links.new(g.outputs[0], out.inputs[0])
        sc.compositing_node_group = ng
    return sc


def camera(loc, rot_deg, lens=40, ortho=None, dof=None):
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens
    cam.sensor_width = 36
    cam.clip_start, cam.clip_end = 0.05, 400
    if ortho:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho
    if dof:
        cam.dof.use_dof = True
        cam.dof.focus_distance = dof[0]
        cam.dof.aperture_fstop = dof[1]
    ob = bpy.data.objects.new("cam", cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot_deg]
    bpy.context.scene.camera = ob
    return ob


def sun(rot_deg, strength=2.0, angle=4.0, color=(255, 246, 232)):
    l = bpy.data.lights.new("sun", "SUN")
    l.energy = strength
    l.angle = math.radians(angle)
    l.color = lin(color)[:3]
    ob = bpy.data.objects.new("sun", l)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = [math.radians(a) for a in rot_deg]
    return ob


def point(loc, color, power=50, radius=0.3, kind="POINT", size=None, rot=None, spot=None, shadow=False):
    l = bpy.data.lights.new("pt", kind)
    l.energy = power
    l.color = lin(color)[:3]
    if kind in ("POINT", "SPOT"):
        l.shadow_soft_size = radius
    l.use_shadow = shadow
    if kind == "AREA":
        l.size = size or 1.0
    if kind == "SPOT" and spot:
        l.spot_size = math.radians(spot[0])
        l.spot_blend = spot[1]
    ob = bpy.data.objects.new("pt", l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if rot:
        ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def overlay_setup(samples=32):
    """A HUD pass: transparent film, ortho camera over a 16x9 board (x -8..8, y -4.5..4.5).
    Rendered separately so the city's tilt-shift DOF never blurs the UI; post.py stacks it."""
    sc = setup(samples=samples, world=(0, 0, 0), world_strength=0.0, glare=True, glare_threshold=1.0, glare_strength=0.5, glare_size=0.5)
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    camera((0, 0, 20), (0, 0, 0), ortho=16.0)
    sun((-28, -22, 0), strength=2.4, angle=6)
    return sc


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


# ----------------------------------------------------------------------------- materials
def img(name):
    p = os.path.join(TEX, name + ".png")
    im = bpy.data.images.load(p, check_existing=True)
    return im


def _hsv(nt, sock, sat, val):
    if sat == 1.0 and val == 1.0:
        return sock
    h = nt.nodes.new("ShaderNodeHueSaturation")
    h.inputs["Saturation"].default_value = sat
    h.inputs["Value"].default_value = val
    nt.links.new(sock, h.inputs["Color"])
    return h.outputs["Color"]


def mat_card(name, tex, em=None, em_strength=4.0, rough=0.85, blended=False, back=(236, 232, 222),
             unlit=False, opacity=1.0, unlit_strength=1.0, tint=None, alpha_clip=False, sat=1.0, val=1.0):
    key = f"m_{name}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ti = nt.nodes.new("ShaderNodeTexImage")
    ti.image = img(tex)
    ti.interpolation = "Cubic"
    ti.extension = "CLIP"
    if unlit:
        sh = nt.nodes.new("ShaderNodeEmission")
        col_out = ti.outputs["Color"]
        if tint:
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs[0].default_value = 1.0
            nt.links.new(ti.outputs["Color"], mix.inputs[6])
            mix.inputs[7].default_value = lin(tint)
            col_out = mix.outputs[2]
        nt.links.new(col_out, sh.inputs["Color"])
        sh.inputs["Strength"].default_value = unlit_strength
        main = sh
    else:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(_hsv(nt, ti.outputs["Color"], sat, val), sh.inputs["Base Color"])
        sh.inputs["Roughness"].default_value = rough
        sh.inputs["Specular IOR Level"].default_value = 0.3
        if em:
            te = nt.nodes.new("ShaderNodeTexImage")
            te.image = img(em)
            te.extension = "CLIP"
            nt.links.new(_hsv(nt, te.outputs["Color"], sat, 1.0), sh.inputs["Emission Color"])
            sh.inputs["Emission Strength"].default_value = em_strength
        main = sh
    # alpha
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    a = ti.outputs["Alpha"]
    if opacity < 1.0:
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(a, mul.inputs[0])
        mul.inputs[1].default_value = opacity
        a = mul.outputs[0]
    if alpha_clip:
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        nt.links.new(a, gt.inputs[0])
        gt.inputs[1].default_value = 0.5
        a = gt.outputs[0]
    shader = main
    if back is not None and not unlit:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        bk = nt.nodes.new("ShaderNodeBsdfDiffuse")
        bk.inputs["Color"].default_value = lin(back)
        mb = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(geo.outputs["Backfacing"], mb.inputs[0])
        nt.links.new(main.outputs[0], mb.inputs[1])
        nt.links.new(bk.outputs[0], mb.inputs[2])
        shader = mb
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a, mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(shader.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED" if blended else "DITHERED"
    m.use_transparent_shadow = True
    m.use_backface_culling = False
    return m


def mat_solid(name, color, rough=0.7, emit=None, emit_strength=0.0, metallic=0.0, alpha=1.0, blended=False, spec=0.5):
    key = f"s_{name}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    sh = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    sh.inputs["Base Color"].default_value = lin(color)
    sh.inputs["Roughness"].default_value = rough
    sh.inputs["Metallic"].default_value = metallic
    sh.inputs["Specular IOR Level"].default_value = spec
    if emit:
        sh.inputs["Emission Color"].default_value = lin(emit)
        sh.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        sh.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED" if blended else "DITHERED"
    return m


def mat_emit(name, color, strength=6.0, alpha=1.0, fade=None):
    """Emission; alpha < 1 mixes with Transparent (BLENDED). NOTE: that mix is additive in
    effect (emission * alpha per face), so a two-sided cone shows it twice. fade='top' makes
    the beam brightest at the mesh's top (Generated Z), 'bottom' at its base."""
    key = f"e_{name}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = lin(color)
    e.inputs["Strength"].default_value = strength
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        if fade:
            tc = nt.nodes.new("ShaderNodeTexCoord")
            sep = nt.nodes.new("ShaderNodeSeparateXYZ")
            nt.links.new(tc.outputs["Generated"], sep.inputs[0])
            z = sep.outputs["Z"]
            if fade == "bottom":
                inv = nt.nodes.new("ShaderNodeMath")
                inv.operation = "SUBTRACT"
                inv.inputs[0].default_value = 1.0
                nt.links.new(z, inv.inputs[1])
                z = inv.outputs[0]
            pw = nt.nodes.new("ShaderNodeMath")
            pw.operation = "POWER"
            nt.links.new(z, pw.inputs[0])
            pw.inputs[1].default_value = 2.2
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            nt.links.new(pw.outputs[0], mul.inputs[0])
            mul.inputs[1].default_value = alpha
            nt.links.new(mul.outputs[0], mx.inputs[0])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(e.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        m.surface_render_method = "BLENDED"
    else:
        nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def mat_glass(name, tint=(180, 230, 255), alpha=0.12):
    """Acetate/glass lens: mostly transparent with a strong specular highlight."""
    key = f"g_{name}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    sh = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    sh.inputs["Base Color"].default_value = lin(tint)
    sh.inputs["Roughness"].default_value = 0.05
    sh.inputs["Specular IOR Level"].default_value = 1.0
    sh.inputs["Coat Weight"].default_value = 0.35
    sh.inputs["Alpha"].default_value = alpha
    m.surface_render_method = "BLENDED"
    m.use_transparent_shadow = True
    return m


# ----------------------------------------------------------------------------- geometry
def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def grid_mesh(name, w, h, nx=1, ny=1):
    verts, faces, uvs = [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            verts.append(((i / nx - 0.5) * w, (j / ny - 0.5) * h, 0.0))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v.x / w + 0.5, v.y / h + 0.5)
    return me


def card(name, tex, width=None, height=None, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, nx=1, ny=1, **mk):
    """An image plane sized from the texture's aspect. rot in degrees (XYZ)."""
    im = img(tex)
    asp = im.size[0] / im.size[1]
    if width is None:
        width = height * asp
    if height is None:
        height = width / asp
    me = grid_mesh(name, width, height, nx, ny)
    me.materials.append(mat or mat_card(tex, tex, **mk))
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def peel(ob, corner=(1, 1), amount=0.35, lift=70.0):
    """Curl one corner of a subdivided card up, sticker-peel style (in local space)."""
    me = ob.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    cx, cy = corner[0] * w / 2, corner[1] * h / 2
    d_axis = Vector((corner[0] * w, corner[1] * h)).normalized()
    fold = (w + h) / 2 * amount
    for v in me.vertices:
        s = Vector((v.co.x - cx, v.co.y - cy)).dot(d_axis)  # 0 at the corner, negative inward
        t = s + fold
        if t > 0:
            # curl: the angle grows along the lifted part so it rolls, not hinges
            ang = math.radians(lift) * min(1.0, 0.35 + t / fold)
            ds = -t + t * math.cos(ang)
            v.co.x += d_axis.x * ds
            v.co.y += d_axis.y * ds
            v.co.z += t * math.sin(ang)
    me.update()


def disc(name, r_out, r_in=0.0, thick=0.04, tex=None, r_tex=None, loc=(0, 0, 0), rot_z=0.0, edge=(236, 232, 222),
         seg=160, top_mat=None, **mk):
    """A cut-paper annulus/disc with a real edge wall (visible thickness)."""
    r_tex = r_tex or r_out
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    top_o, bot_o, top_i, bot_i = [], [], [], []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        ca, sa = math.cos(a), math.sin(a)
        top_o.append(bm.verts.new((r_out * ca, r_out * sa, thick)))
        bot_o.append(bm.verts.new((r_out * ca, r_out * sa, 0)))
        if r_in > 0:
            top_i.append(bm.verts.new((r_in * ca, r_in * sa, thick)))
            bot_i.append(bm.verts.new((r_in * ca, r_in * sa, 0)))
    if r_in <= 0:
        ctr = bm.verts.new((0, 0, thick))
    faces_top = []
    for k in range(seg):
        k2 = (k + 1) % seg
        if r_in > 0:
            f = bm.faces.new((top_i[k], top_o[k], top_o[k2], top_i[k2]))
        else:
            f = bm.faces.new((ctr, top_o[k], top_o[k2]))
        f.material_index = 0
        faces_top.append(f)
        w = bm.faces.new((bot_o[k], bot_o[k2], top_o[k2], top_o[k]))
        w.material_index = 1
        if r_in > 0:
            wi = bm.faces.new((bot_i[k2], bot_i[k], top_i[k], top_i[k2]))
            wi.material_index = 1
    for f in faces_top:
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (0.5 + 0.5 * co.x / r_tex, 0.5 + 0.5 * co.y / r_tex)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(top_mat or (mat_card(tex, tex, back=None, **mk) if tex else mat_solid(name + "_t", edge)))
    me.materials.append(mat_solid(f"edge_{edge}", edge, 0.9))
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    ob.rotation_euler = (0, 0, math.radians(rot_z))
    return ob


def lens(name, r, height, loc):
    """A shallow glass dome over a spinner."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=24, radius=1.0)
    for v in bm.verts:
        v.co.x *= r
        v.co.y *= r
        v.co.z = max(0.0, v.co.z) * height
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat_glass(name))
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    return ob


def torus(name, R, r, loc, mat, seg=128):
    bm = bmesh.new()
    rs = 12
    rings = []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        ring = []
        for j in range(rs):
            b = 2 * math.pi * j / rs
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for k in range(seg):
        for j in range(rs):
            bm.faces.new((rings[k][j], rings[(k + 1) % seg][j], rings[(k + 1) % seg][(j + 1) % rs], rings[k][(j + 1) % rs]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    return ob


def arc_tube(name, R, r, a0, a1, loc, mat, seg=64):
    """A partial torus (HP arc / neon tube arc). Angles in degrees, 0 = +X, CCW."""
    pts = [(R * math.cos(math.radians(a0 + (a1 - a0) * t / seg)), R * math.sin(math.radians(a0 + (a1 - a0) * t / seg)), 0) for t in range(seg + 1)]
    return tube(name, pts, r, mat, loc)


def tube(name, pts, radius, mat, loc=(0, 0, 0), cyclic=False):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (co[0], co[1], co[2], 1.0)
    sp.use_cyclic_u = cyclic
    cu.materials.append(mat)
    ob = link(bpy.data.objects.new(name, cu))
    ob.location = loc
    return ob


def box(name, size, loc, mat, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def cone(name, r0, r1, depth, loc, rot, mat, seg=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=seg, radius1=r0, radius2=r1, depth=depth)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = link(bpy.data.objects.new(name, me))
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


# ----------------------------------------------------------------------------- grease pencil marker
# Single-stroke letters on a unit box (x 0..~0.7, y 0..1, y up).
def _oval(cx, cy, rx, ry, n=18, start=90):
    return [(cx + rx * math.cos(math.radians(start + 360 * k / n)), cy + ry * math.sin(math.radians(start + 360 * k / n))) for k in range(n + 1)]


FONT = {
    "A": [[(0, 0), (0.33, 1), (0.66, 0)], [(0.14, 0.4), (0.52, 0.4)]],
    "B": [[(0, 0), (0, 1), (0.42, 1), (0.58, 0.88), (0.58, 0.64), (0.42, 0.53), (0, 0.53)], [(0.42, 0.53), (0.62, 0.4), (0.62, 0.13), (0.46, 0), (0, 0)]],
    "C": [[(0.62, 0.84), (0.48, 1), (0.2, 1), (0, 0.76), (0, 0.24), (0.2, 0), (0.48, 0), (0.64, 0.16)]],
    "D": [[(0, 0), (0, 1), (0.32, 1), (0.62, 0.76), (0.62, 0.24), (0.32, 0), (0, 0)]],
    "E": [[(0.58, 1), (0, 1), (0, 0), (0.6, 0)], [(0, 0.52), (0.44, 0.52)]],
    "F": [[(0.58, 1), (0, 1), (0, 0)], [(0, 0.52), (0.44, 0.52)]],
    "G": [[(0.62, 0.84), (0.48, 1), (0.2, 1), (0, 0.76), (0, 0.24), (0.2, 0), (0.48, 0), (0.64, 0.18), (0.64, 0.46), (0.36, 0.46)]],
    "H": [[(0, 1), (0, 0)], [(0.6, 1), (0.6, 0)], [(0, 0.5), (0.6, 0.5)]],
    "I": [[(0.08, 1), (0.08, 0)]],
    "J": [[(0.55, 1), (0.55, 0.22), (0.4, 0), (0.14, 0), (0, 0.2)]],
    "K": [[(0, 1), (0, 0)], [(0.58, 1), (0.02, 0.42)], [(0.2, 0.6), (0.62, 0)]],
    "L": [[(0, 1), (0, 0), (0.54, 0)]],
    "M": [[(0, 0), (0.02, 1), (0.36, 0.38), (0.7, 1), (0.72, 0)]],
    "N": [[(0, 0), (0, 1), (0.6, 0), (0.6, 1)]],
    "O": [_oval(0.33, 0.5, 0.33, 0.5)],
    "P": [[(0, 0), (0, 1), (0.44, 1), (0.6, 0.86), (0.6, 0.62), (0.44, 0.5), (0, 0.5)]],
    "Q": [_oval(0.33, 0.5, 0.33, 0.5), [(0.38, 0.26), (0.72, -0.08)]],
    "R": [[(0, 0), (0, 1), (0.44, 1), (0.6, 0.86), (0.6, 0.62), (0.44, 0.5), (0, 0.5)], [(0.28, 0.5), (0.64, 0)]],
    "S": [[(0.6, 0.86), (0.44, 1), (0.16, 1), (0.01, 0.86), (0.01, 0.66), (0.16, 0.54), (0.46, 0.47), (0.61, 0.34), (0.61, 0.14), (0.45, 0), (0.15, 0), (0, 0.14)]],
    "T": [[(0, 1), (0.7, 1)], [(0.35, 1), (0.35, 0)]],
    "U": [[(0, 1), (0, 0.2), (0.16, 0), (0.44, 0), (0.6, 0.2), (0.6, 1)]],
    "V": [[(0, 1), (0.32, 0), (0.64, 1)]],
    "W": [[(0, 1), (0.18, 0), (0.4, 0.62), (0.62, 0), (0.82, 1)]],
    "X": [[(0, 1), (0.6, 0)], [(0.6, 1), (0, 0)]],
    "Y": [[(0, 1), (0.32, 0.5), (0.64, 1)], [(0.32, 0.5), (0.32, 0)]],
    "Z": [[(0, 1), (0.6, 1), (0, 0), (0.62, 0)]],
    "!": [[(0.1, 1), (0.08, 0.3)], [(0.08, 0.06), (0.09, 0.0)]],
    "?": [[(0, 0.8), (0.12, 0.98), (0.4, 1), (0.56, 0.84), (0.52, 0.62), (0.28, 0.46), (0.28, 0.28)], [(0.28, 0.06), (0.29, 0.0)]],
    "'": [[(0.08, 1), (0.05, 0.72)]],
    "0": [_oval(0.28, 0.5, 0.28, 0.5)],
    "1": [[(0.02, 0.8), (0.24, 1), (0.24, 0)]],
    "2": [[(0, 0.8), (0.14, 0.98), (0.42, 1), (0.56, 0.82), (0.5, 0.6), (0, 0), (0.6, 0)]],
    "3": [[(0, 0.9), (0.2, 1), (0.46, 0.98), (0.56, 0.8), (0.46, 0.58), (0.2, 0.54), (0.5, 0.48), (0.6, 0.26), (0.48, 0.04), (0.2, 0), (0, 0.1)]],
    "4": [[(0.46, 0), (0.46, 1), (0, 0.3), (0.64, 0.3)]],
    "+": [[(0.3, 0.8), (0.3, 0.2)], [(0, 0.5), (0.6, 0.5)]],
    "-": [[(0.02, 0.48), (0.5, 0.5)]],
}


class Marker:
    """One Grease Pencil v3 object holding hand marks. World XY plane at height z."""

    def __init__(self, name="marker", z=2.0, seed=1):
        gp = bpy.data.grease_pencils.new(name)
        self.gp = gp
        self.ob = link(bpy.data.objects.new(name, gp))
        self.ob.visible_shadow = False
        self.layer = gp.layers.new("ink")
        self.layer.use_lights = False
        self.draw = self.layer.frames.new(1).drawing
        self.mats = {}
        self.z = z
        self.rng = random.Random(seed)

    def mat(self, key):
        if key not in self.mats:
            m = bpy.data.materials.new(f"gp_{self.gp.name}_{key}")
            bpy.data.materials.create_gpencil_data(m)
            m.grease_pencil.color = lin(C[key]) if isinstance(key, str) and key in C else lin(key)
            self.gp.materials.append(m)
            self.mats[key] = len(self.gp.materials) - 1
        return self.mats[key]

    def stroke(self, pts, radii, color="pink", opacity=1.0):
        if len(pts) < 2:
            return
        self.draw.add_strokes([len(pts)])
        s = self.draw.strokes[len(self.draw.strokes) - 1]
        s.material_index = self.mat(color)
        s.cyclic = False
        rs = radii if isinstance(radii, (list, tuple)) else [radii] * len(pts)
        for p, co, r in zip(s.points, pts, rs):
            p.position = (co[0], co[1], co[2] if len(co) > 2 else self.z)
            p.radius = r
            p.opacity = opacity

    # -- helpers
    def _resample(self, poly, step):
        out = [poly[0]]
        for a, b in zip(poly, poly[1:]):
            L = math.dist(a, b)
            n = max(1, int(L / step))
            for k in range(1, n + 1):
                t = k / n
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        return out

    def _wobble(self, pts, amp, freq=3.0):
        ph = [self.rng.uniform(0, 6.28) for _ in range(4)]
        out = []
        n = len(pts)
        for i, (x, y) in enumerate(pts):
            t = i / max(1, n - 1)
            out.append((x + amp * math.sin(freq * 6.28 * t + ph[0]) + amp * 0.5 * math.sin(freq * 13 * t + ph[1]),
                        y + amp * math.sin(freq * 6.28 * t + ph[2]) + amp * 0.5 * math.sin(freq * 11 * t + ph[3])))
        return out

    def layout(self, text, x, y, size, slant=0.2, track=0.22, rot=0.0):
        """Return list of (strokes_in_world, letter_bbox) for the text; strokes are point lists."""
        rng = self.rng
        cur = 0.0
        letters = []
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for ch in text.upper():
            if ch == " ":
                cur += 0.42
                continue
            g = FONT.get(ch)
            if not g:
                cur += 0.5
                continue
            wmax = max(px for st in g for (px, py) in st)
            sc = rng.uniform(0.92, 1.1)
            base = rng.uniform(-0.06, 0.06)
            lr = math.radians(rng.uniform(-6, 6))
            cl, sl = math.cos(lr), math.sin(lr)
            strokes = []
            for st in g:
                pts = []
                for (px, py) in st:
                    px, py = (px - wmax / 2) * sc, (py - 0.5) * sc
                    px, py = px * cl - py * sl, px * sl + py * cl
                    px += py * slant
                    lx = (cur + wmax / 2 + px) * size
                    ly = (0.5 + py + base) * size
                    pts.append((x + lx * cr - ly * sr, y + lx * sr + ly * cr))
                strokes.append(pts)
            letters.append(strokes)
            cur += wmax + track
        return letters

    def words(self, text, x, y, size, color="pink", slant=0.2, track=0.22, rot=0.0, progress=1.0,
              weight=0.09, drips=None, edge=True, anchor="left"):
        """Marker lettering. drips: list of (letter_index, length_in_size, state) with state in
        'form' (bead), 'run' (long thin run). Returns the list of drip start points."""
        if anchor != "left":
            probe = self.layout(text, 0, 0, size, slant, track, 0)
            xs = [p[0] for L in probe for st in L for p in st]
            wid = max(xs) - min(xs)
            x = x - (wid / 2 if anchor == "center" else wid) * math.cos(math.radians(rot))
            y = y - (wid / 2 if anchor == "center" else wid) * math.sin(math.radians(rot))
        letters = self.layout(text, x, y, size, slant, track, rot)
        step = size * 0.03
        allst = []
        for L in letters:
            for st in L:
                rs = self._wobble(self._resample(st, step), size * 0.008)
                allst.append(rs)
        total = sum(len(s) for s in allst)
        budget = int(total * progress)
        r0 = size * weight
        tip = None
        for s in allst:
            if budget <= 1:
                break
            s2 = s[:budget]
            budget -= len(s2)
            n = len(s2)
            radii = []
            for i in range(n):
                t = i / max(1, len(s) - 1)
                taper = min(1.0, 0.65 + t * 4) * (1.0 - 0.18 * max(0, t - 0.8) / 0.2)
                radii.append(r0 * taper * self.rng.uniform(0.95, 1.05))
            if edge:  # darker pooled edge under the fluoro ink
                self.stroke(s2, [r * 1.16 for r in radii], "pink_dk" if color == "pink" else "black")
            self.stroke(s2, radii, color)
            tip = s2[-1]
        starts = []
        if drips and progress >= 1.0:
            for (li, length, state) in drips:
                if li >= len(letters):
                    continue
                pts = [p for st in letters[li] for p in st]
                bx, by = min(pts, key=lambda p: p[1] + self.rng.uniform(-0.02, 0.02) * size)
                self.drip(bx, by, length * size, r0, state, color)
                starts.append((bx, by))
        return tip

    def drip(self, x, y, length, r0, state="form", color="pink"):
        rng = self.rng
        n = max(3, int(length / (r0 * 0.4)))
        pts, rad = [], []
        for i in range(n + 1):
            t = i / n
            pts.append((x + math.sin(t * 5 + x) * r0 * 0.12, y - length * t))
            if state == "form":
                rad.append(r0 * (0.9 - 0.35 * t))
            else:
                rad.append(r0 * (0.75 - 0.4 * t) * (1 + 0.12 * math.sin(t * 17)))
        self.stroke(pts, rad, color)
        # bead at the end
        bead = r0 * (1.05 if state == "form" else 0.62)
        ex, ey = pts[-1]
        self.stroke([(ex, ey + bead * 0.3), (ex, ey - bead * 0.35)], [bead * 0.8, bead], color)
        if color == "pink":
            self.stroke([(ex - bead * 0.3, ey + bead * 0.1), (ex - bead * 0.28, ey)], bead * 0.22, "white", 0.8)

    def circle(self, cx, cy, rx, ry, color="pink", r=0.03, turns=1.25, seed_amp=0.08):
        n = int(90 * turns)
        a0 = self.rng.uniform(0, 6.28)
        pts, rad = [], []
        for i in range(n):
            t = i / (n - 1)
            a = a0 + t * turns * 2 * math.pi
            k = 1 + seed_amp * math.sin(a * 2.3 + a0) + 0.06 * t
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
            rad.append(r * (0.7 + 0.3 * math.sin(math.pi * t)))
        self.stroke(pts, rad, color)

    def arrow(self, p0, p1, bend=0.25, color="pink", r=0.03, head=0.35):
        (x0, y0), (x1, y1) = p0, p1
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0), (x1 - x0)
        cx, cy = mx + nx * bend, my + ny * bend
        pts = []
        for i in range(40):
            t = i / 39
            pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
        pts = self._wobble(pts, r * 0.3)
        self.stroke(pts, [r * (0.6 + 0.4 * i / 39) for i in range(40)], color)
        dx, dy = x1 - pts[-4][0], y1 - pts[-4][1]
        L = math.hypot(dx, dy) or 1
        dx, dy = dx / L, dy / L
        hl = head
        for s in (1, -1):
            a = math.radians(150 * s)
            hx = x1 + hl * (dx * math.cos(a) - dy * math.sin(a))
            hy = y1 + hl * (dx * math.sin(a) + dy * math.cos(a))
            self.stroke([(x1, y1), (hx, hy)], [r, r * 0.7], color)

    def scribble(self, x0, y0, x1, y1, color="pink", r=0.02, n=14):
        pts = []
        for i in range(n):
            t = i / (n - 1)
            pts.append((x0 + (x1 - x0) * t + self.rng.uniform(-0.05, 0.05), y0 if i % 2 == 0 else y1))
        self.stroke(self._resample(pts, r), r, color)

    def underline(self, x0, x1, y, color="pink", r=0.03, double=False):
        for k in range(2 if double else 1):
            pts = self._wobble(self._resample([(x0, y - k * r * 3), (x1, y - k * r * 3 + self.rng.uniform(-r, r) * 2)], r), r * 0.4, 1.5)
            self.stroke(pts, [r * (0.6 + 0.4 * math.sin(math.pi * i / (len(pts) - 1))) for i in range(len(pts))], color)
