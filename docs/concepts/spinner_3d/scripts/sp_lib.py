"""Spinner depth study: shared Blender 5.2 helpers (headless, EEVEE).

Every technique script imports this. Spinner layers are the Pillow textures from
make_textures.py, mapped with object coordinates (texture square = [-R, R] metres), so the
same art is used flat, stacked, normal-lit or wrapped on true 3D geometry.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "work", "tex")
REN = os.path.join(ROOT, "work", "renders")
FONTS = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "assets", "fonts"))
R = 1.45
os.makedirs(REN, exist_ok=True)

OP_TICKS = [3, 3, 4, 2, 3, 3, 3, 3, 2, 4]
EN_TICKS = [4, 3, 4, 3, 3, 2, 3, 4, 4]


def hexc(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0], c[1], c[2], a)


PINK, CYAN, GREEN, MERIDIAN = hexc("#FF3DA8"), hexc("#5CE1FF"), hexc("#7BE07B"), hexc("#FF8C1A")


# ------------------------------------------------------------------ scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup(res=(1200, 1200), samples=32, bloom=(1.05, 0.6, 0.6), transparent=False,
          motion_blur=False, world=(0.004, 0.005, 0.012)):
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("ENGINE", e)
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_shadows = True
    try:
        sc.eevee.use_raytracing = True
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.render.use_motion_blur = motion_blur
    sc.render.motion_blur_shutter = 0.7
    sc.eevee.motion_blur_steps = 6
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = world + (1.0,)
    bg.inputs[1].default_value = 1.0
    if bloom:
        ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        g = ng.nodes.new("CompositorNodeGlare")
        for key, val in (("Type", "Bloom"), ("Quality", "High")):
            try:
                g.inputs[key].default_value = val
            except Exception as e:
                print("glare", key, e)
        g.inputs["Threshold"].default_value = bloom[0]
        g.inputs["Strength"].default_value = bloom[1]
        g.inputs["Size"].default_value = bloom[2]
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], g.inputs["Image"])
        ng.links.new(g.outputs[0], out.inputs[0])
        sc.compositing_node_group = ng
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    return sc


def camera(ortho_scale=3.3, cy=-0.15, tilt_deg=0.0, dist=12.0, cx=0.0):
    cam_d = bpy.data.cameras.new("cam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = ortho_scale
    cam_d.clip_start, cam_d.clip_end = 0.1, 100
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.scene.collection.objects.link(cam)
    t = math.radians(tilt_deg)
    cam.location = (cx, cy - dist * math.sin(t), dist * math.cos(t))
    cam.rotation_euler = (t, 0, 0)
    bpy.context.scene.camera = cam
    return cam


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


# ------------------------------------------------------------------ images + nodes
def img(name, noncolor=False):
    p = os.path.join(TEX, name + ".png")
    im = bpy.data.images.load(p, check_existing=True)
    if noncolor:
        im.colorspace_settings.name = "Non-Color"
    return im


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    try:
        m.surface_render_method = "DITHERED"
        m.use_transparent_shadow = True
    except Exception:
        pass
    return m, nt


def planar(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / (2 * R), 1 / (2 * R), 1)
    mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def tex_node(nt, vec, image):
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = image
    t.extension = "CLIP"
    t.interpolation = "Cubic"
    nt.links.new(vec, t.inputs["Vector"])
    return t


def principled(nt):
    return nt.nodes.new("ShaderNodeBsdfPrincipled")


def add_glow(nt, shader_out, vec, glow_key, strength):
    """Add an emission from a glow map (rims) on top of a shader."""
    if not glow_key or strength <= 0:
        return shader_out
    g = tex_node(nt, vec, img(glow_key))
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(g.outputs["Color"], mul.inputs[6])
    nt.links.new(g.outputs["Alpha"], mul.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(mul.outputs[2], em.inputs["Color"])
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(shader_out, add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    return add.outputs[0]


def layer_mat(key, mode="flat", emit=1.0, glow=0.0, bump=0.0, rough=0.45, spec=0.5):
    """Material for a 2D spinner layer.
    mode flat: unlit emission (today's game look).
    mode lit: principled, lit by scene lights, emission kept low; bump from the height map.
    """
    name = f"{key}_{mode}_{emit}_{glow}_{bump}"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m, nt = new_mat(name)
    vec = planar(nt)
    t = tex_node(nt, vec, img(key))
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if mode == "flat":
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = emit
        nt.links.new(t.outputs["Color"], em.inputs["Color"])
        s = add_glow(nt, em.outputs[0], vec, key + "_g" if glow else None, glow)
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(t.outputs["Alpha"], mix.inputs[0])
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(s, mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        return m
    p = principled(nt)
    nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(t.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = emit
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    if bump > 0:
        h = tex_node(nt, vec, img(key + "_h", noncolor=True))
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = 0.02
        nt.links.new(h.outputs["Color"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    s = add_glow(nt, p.outputs[0], vec, key + "_g" if glow else None, glow)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(t.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(s, mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def emit_mat(name, color, strength=1.0):
    m, nt = new_mat(name)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    em.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def solid_mat(name, color, metallic=0.0, rough=0.4, emit=0.0, emit_col=None):
    m, nt = new_mat(name)
    p = principled(nt)
    p.inputs["Base Color"].default_value = color
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if emit > 0:
        p.inputs["Emission Color"].default_value = emit_col or color
        p.inputs["Emission Strength"].default_value = emit
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    return m


def metal_decal_mat(name, metal_col, decal_key, glow_key=None, glow=0.0, rough=0.3, emit_decal=0.35):
    """Machined metal with painted decals (stickers, rims, stripes) from a decal texture."""
    m, nt = new_mat(name)
    vec = planar(nt)
    metal = principled(nt)
    metal.inputs["Base Color"].default_value = metal_col
    metal.inputs["Metallic"].default_value = 1.0
    # brushed / scratched roughness
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 60.0
    noise.inputs["Detail"].default_value = 8.0
    nt.links.new(vec, noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = rough * 0.85
    ramp.inputs["To Max"].default_value = rough * 1.2
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    nt.links.new(ramp.outputs["Result"], metal.inputs["Roughness"])
    d = tex_node(nt, vec, img(decal_key))
    paint = principled(nt)
    paint.inputs["Roughness"].default_value = 0.75
    paint.inputs["Specular IOR Level"].default_value = 0.2
    nt.links.new(d.outputs["Color"], paint.inputs["Base Color"])
    nt.links.new(d.outputs["Color"], paint.inputs["Emission Color"])
    paint.inputs["Emission Strength"].default_value = emit_decal
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(d.outputs["Alpha"], mix.inputs[0])
    nt.links.new(metal.outputs[0], mix.inputs[1])
    nt.links.new(paint.outputs[0], mix.inputs[2])
    s = add_glow(nt, mix.outputs[0], vec, glow_key, glow)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(s, out.inputs["Surface"])
    return m


def glass_mat(name="glass", tint=(0.6, 0.85, 1.0, 1.0), strength=1.0):
    """Clear dome: transparent, with a fresnel-weighted glossy coat (specular highlight)."""
    m, nt = new_mat(name)
    m.use_transparent_shadow = True
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.10 * strength
    mr.inputs["To Max"].default_value = 0.85 * strength
    nt.links.new(lw.outputs["Fresnel"], mr.inputs["Value"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    try:
        gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    except Exception:
        gl = nt.nodes.new("ShaderNodeBsdfAnisotropic")
    gl.inputs["Color"].default_value = tint
    gl.inputs["Roughness"].default_value = 0.06
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ meshes
def mesh_obj(name, verts, faces, mat=None, loc=(0, 0, 0), smooth=False, parent=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if mat:
        me.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob


def plane(name, mat, z=0.0, half=R, loc_xy=(0, 0)):
    v = [(-half, -half, 0), (half, -half, 0), (half, half, 0), (-half, half, 0)]
    return mesh_obj(name, v, [(0, 1, 2, 3)], mat, (loc_xy[0], loc_xy[1], z))


def polar(r, phi_deg):
    a = math.radians(phi_deg)
    return (r * math.sin(a), r * math.cos(a))


def lathe(name, profile, mat=None, segs=360, closed=True, rfn=None, outer_min=None, loc=(0, 0, 0),
          smooth=False):
    """Revolve an (r, z) profile. rfn(phi)->radius cut for points with r >= outer_min (notches)."""
    verts, faces = [], []
    n = len(profile)
    for i in range(segs):
        phi = 360.0 * i / segs
        for (r, z) in profile:
            rr = r
            if rfn is not None and outer_min is not None and r >= outer_min:
                rr = r - (1.0 - rfn(phi))
            x, y = polar(rr, phi)
            verts.append((x, y, z))
    m = n if closed else n - 1
    for i in range(segs):
        i2 = (i + 1) % segs
        for j in range(m):
            j2 = (j + 1) % n
            faces.append((i * n + j, i2 * n + j, i2 * n + j2, i * n + j2))
    return mesh_obj(name, verts, faces, mat, loc, smooth)


def disc(name, r, mat, z=0.0, segs=256, loc_xy=(0, 0)):
    verts = [(0, 0, 0)] + [(*polar(r, 360 * i / segs), 0) for i in range(segs)]
    faces = [(0, 1 + (i + 1) % segs, 1 + i) for i in range(segs)]
    # flip so normals face +Z
    faces = [(f[0], f[2], f[1]) for f in faces]
    return mesh_obj(name, verts, faces, mat, (loc_xy[0], loc_xy[1], z))


def box(name, sx, sy, sz, mat, loc=(0, 0, 0), taper=1.0):
    """Box centred on loc in x/z, from y=0 to y=sy (use negative sy to extend down)."""
    hx, hz = sx / 2, sz / 2
    tx = hx * taper
    v = [(-hx, 0, -hz), (hx, 0, -hz), (hx, 0, hz), (-hx, 0, hz),
         (-tx, sy, -hz), (tx, sy, -hz), (tx, sy, hz), (-tx, sy, hz)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return mesh_obj(name, v, f, mat, loc)


def cylinder(name, r, h, mat, loc=(0, 0, 0), segs=48):
    return lathe(name, [(0.0, h), (r, h), (r, 0), (0.0, 0)], mat, segs, True, loc=loc)


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    return e


def notch_r(phi, r_out=1.0, depth=0.045, every=15.0, width=5.0):
    f = (phi + every / 2) % every
    return r_out - depth if abs(f - every / 2) < width / 2 else r_out


# ------------------------------------------------------------------ backdrop, lights
def backdrop(cam, wide=False, dist=20.0, scale=1.35):
    """Emission plane parented to the camera (never shadowed, never lit)."""
    im = img("backdrop_wide" if wide else "backdrop_square")
    m, nt = new_mat("backdrop_" + ("w" if wide else "s"))
    tc = nt.nodes.new("ShaderNodeTexCoord")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = im
    t.extension = "EXTEND"
    nt.links.new(tc.outputs["UV"], t.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(t.outputs["Color"], em.inputs["Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    rx = bpy.context.scene.render.resolution_x
    ry = bpy.context.scene.render.resolution_y
    w = cam.data.ortho_scale * scale
    h = w * ry / rx
    me = bpy.data.meshes.new("bd")
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [],
                   [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, c in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = c
    me.materials.append(m)
    ob = bpy.data.objects.new("backdrop", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = cam
    ob.location = (0, 0, -dist)
    ob.visible_shadow = False
    return ob


def light(kind, name, loc, color=(1, 1, 1, 1), energy=10.0, size=0.5, rot=(0, 0, 0), angle=None):
    ld = bpy.data.lights.new(name, kind)
    ld.color = color[:3]
    ld.energy = energy
    if kind == "SUN":
        ld.angle = math.radians(angle or 8)
    elif kind == "AREA":
        ld.size = size
    else:
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def neon_props(x_pink=-1.5, x_cyan=1.5, cy=-0.1, z=0.35, power=(90.0, 70.0)):
    """Pink sign on the left, cyan tube on the right; each with a real raking light."""
    im = img("sign_pink")
    m, nt = new_mat("sign")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = im
    nt.links.new(tc.outputs["UV"], t.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 3.0
    nt.links.new(t.outputs["Color"], em.inputs["Color"])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    w, h = 0.28, 1.1
    me = bpy.data.meshes.new("sign")
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [],
                   [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, c in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = c
    me.materials.append(m)
    sign = bpy.data.objects.new("sign", me)
    bpy.context.scene.collection.objects.link(sign)
    sign.location = (x_pink, cy + 0.3, z)
    sign.visible_shadow = False
    tube = cylinder("tube", 0.028, 1.3, emit_mat("tube", CYAN, 5.0), loc=(0, 0, 0))
    tube.rotation_euler = (math.radians(90), 0, 0)
    tube.location = (x_cyan, cy + 0.55, z)
    tube.visible_shadow = False
    lp = light("POINT", "pink_l", (x_pink + 0.05, cy + 0.3, z), PINK, power[0], 0.25)
    lc = light("POINT", "cyan_l", (x_cyan - 0.05, cy - 0.1, z), CYAN, power[1], 0.25)
    return sign, tube, lp, lc


# ------------------------------------------------------------------ spinner builders
LAYER_ORDER = ("slices", "hp", "hub", "needle", "bezel")


def needle_2d(side, loc, flat=True, emit=1.0):
    """Flat pointer: white triangle with pink outline + target ring; origin = pivot."""
    edge = PINK if side == "op" else MERIDIAN
    piv = empty(side + "_needle", loc)
    if flat:
        mw = emit_mat("needle_w", (1, 1, 1, 1), emit)
        me_ = emit_mat("needle_e_" + side, edge, emit * 1.2)
        mk = emit_mat("needle_k", hexc("#111111"), 1.0)
    else:
        mw = solid_mat("needle_w_l", (0.9, 0.9, 0.9, 1), rough=0.3, emit=0.5, emit_col=(1, 1, 1, 1))
        me_ = solid_mat("needle_e_l_" + side, edge, rough=0.3, emit=0.8)
        mk = solid_mat("needle_k_l", hexc("#111111"), rough=0.4)
    o = mesh_obj("n_out", [(-0.058, 0.01, 0), (0.058, 0.01, 0), (0, -0.2, 0)], [(0, 2, 1)], me_, (0, 0, 0))
    o.parent = piv
    i = mesh_obj("n_in", [(-0.036, 0.0, 0.002), (0.036, 0.0, 0.002), (0, -0.17, 0.002)], [(0, 2, 1)], mw)
    i.parent = piv
    d = disc("n_ring", 0.05, me_, 0.003)
    d.parent = piv
    d2 = disc("n_ring2", 0.036, mw, 0.004)
    d2.parent = piv
    d3 = disc("n_dot", 0.014, mk, 0.005)
    d3.parent = piv
    return piv


def spinner_2d(side="op", mode="flat", z=None, glow=1.6, bump=0.0, emit=None, center=(0, 0)):
    """Spinner as textured planes. z: dict layer->height. Returns dict layer->object."""
    z = z or {}
    emit = emit or {}
    objs = {}
    cx, cy = center
    for layer in ("slices", "hp", "hub", "bezel"):
        e = emit.get(layer, 1.0 if mode == "flat" else 0.35)
        gl = glow if layer in ("slices", "bezel", "hp") else glow * 0.5
        m = layer_mat(f"{side}_{layer}", mode, emit=e, glow=gl, bump=bump)
        objs[layer] = plane(f"{side}_{layer}", m, z.get(layer, 0.0), loc_xy=(cx, cy))
    objs["needle"] = needle_2d(side, (cx, cy + 0.955, z.get("needle", 0.01)), flat=(mode == "flat"),
                               emit=emit.get("needle", 1.0))
    return objs


def spinner_3d(side="op", center=(0, 0), glow=2.0, inlay_emit=0.75):
    """True 3D wheel: machined bezel, recessed emissive slice inlays with dividers,
    hub screen, physical needle with counterweight. Returns dict of parts."""
    cx, cy = center
    parts = {}
    enemy = side == "en"
    metal_col = (0.30, 0.31, 0.35, 1) if not enemy else (0.62, 0.28, 0.07, 1)
    bez_m = metal_decal_mat(side + "_bezel3d", metal_col, side + "_bezel_d", side + "_bezel_g", glow, rough=0.24, emit_decal=0.04)
    prof = [(0.86, -0.03), (0.86, 0.10), (0.878, 0.132), (0.97, 0.142), (0.994, 0.126), (1.004, 0.085),
            (1.0, -0.03)]
    parts["bezel"] = lathe(side + "_bezel", prof, bez_m, segs=720, rfn=(notch_r if enemy else None),
                           outer_min=0.965, loc=(cx, cy, 0))
    # recess floor + inlay (rotating group)
    rot = empty(side + "_wheel", (cx, cy, 0))
    parts["wheel"] = rot
    inlay = layer_mat(f"{side}_slices", "lit", emit=inlay_emit, glow=glow, bump=0.0, rough=0.38, spec=0.35)
    d = plane(side + "_inlay", inlay, 0.0)
    d.parent = rot
    parts["inlay"] = d
    div_m = solid_mat("divider", (0.55, 0.57, 0.62, 1), metallic=1.0, rough=0.25)
    phi = 0.0
    for k, t in enumerate(OP_TICKS if not enemy else EN_TICKS):
        b = box(f"{side}_div{k}", 0.016, 0.44, 0.04, div_m, (0, 0, 0.02))
        b.location = (*polar(0.42, phi), 0.02)
        b.rotation_euler = (0, 0, -math.radians(phi))
        b.parent = rot
        phi += t * 12.0
    # hub (static) with a screen
    hub_m = solid_mat("hub_metal", (0.3, 0.31, 0.35, 1), metallic=1.0, rough=0.32)
    hprof = [(0.0, 0.0), (0.405, 0.0), (0.405, 0.055), (0.385, 0.088), (0.35, 0.088), (0.35, 0.07),
             (0.0, 0.07)][::-1]
    parts["hub"] = lathe(side + "_hub", hprof, hub_m, segs=256, loc=(cx, cy, 0.0))
    scr = layer_mat(f"{side}_hub", "lit", emit=1.0, glow=0.0, rough=0.08, spec=0.9)
    parts["screen"] = plane(side + "_screen", scr, 0.072, loc_xy=(cx, cy))
    # HP arc stays a flat emissive decal on the table
    parts["hp"] = plane(side + "_hp", layer_mat(f"{side}_hp", "flat", 1.0, glow=1.2), -0.012, loc_xy=(cx, cy))
    # needle: pivot over the bezel at 12 o'clock, tip into the slices, counterweight outside
    parts["needle"] = needle_3d(side, (cx, cy + 0.955, 0.2))
    return parts


def needle_3d(side, loc):
    edge = PINK if side == "op" else MERIDIAN
    piv = empty(side + "_needle", loc)
    enamel = solid_mat("enamel", (0.92, 0.92, 0.9, 1), rough=0.25)
    stripe = solid_mat("stripe_" + side, edge, rough=0.3, emit=1.2)
    chrome = solid_mat("chrome", (0.9, 0.9, 0.92, 1), metallic=1.0, rough=0.12)
    dark = solid_mat("weight", (0.08, 0.08, 0.1, 1), metallic=1.0, rough=0.35)
    arm = box("arm", 0.085, -0.24, 0.024, enamel, (0, 0, 0), taper=0.2)
    arm.parent = piv
    st = box("stripe", 0.03, -0.2, 0.026, stripe, (0, -0.01, 0.001), taper=0.22)
    st.parent = piv
    tail = box("tail", 0.03, 0.09, 0.018, enamel, (0, 0, 0))
    tail.parent = piv
    cw = cylinder("cweight", 0.05, 0.04, dark, loc=(0, 0.1, -0.02))
    cw.parent = piv
    cap = cylinder("cap", 0.034, 0.03, chrome, loc=(0, 0, 0.005))
    cap.parent = piv
    post = cylinder("post", 0.018, 0.08, chrome, loc=(0, 0, -0.07))
    post.parent = piv
    return piv


def dome(center=(0, 0), z0=0.14, h=0.2, a=0.86, strength=1.0):
    prof = []
    for i in range(25):
        r = a * (i / 24)
        prof.append((r, z0 + h * math.sqrt(max(0.0, 1 - (r / a) ** 2))))
    ob = lathe("dome", prof, glass_mat(strength=strength), segs=192, closed=False,
               loc=(center[0], center[1], 0), smooth=True)
    ob.visible_shadow = False
    return ob


# ------------------------------------------------------------------ motion
def spin_curve(n, total, stop, wobble=6.0, period=6.0, decay=3.5):
    """Wheel angle (deg clockwise) per frame: ease-out spin, then a damped wobble on the stop."""
    out = []
    for f in range(n):
        if f <= stop:
            u = f / stop
            a = total * (1 - (1 - u) ** 3)
        else:
            a = total
        t0 = stop * 0.8
        if f > t0:
            dt = f - t0
            a += wobble * math.sin(2 * math.pi * dt / period) * math.exp(-dt / decay)
        out.append(a)
    return out


def flap_curve(angles, ticks, sub=10, push=24.0, win=9.0):
    """Needle deflection (deg, +=pushed clockwise-side) per frame from peg contacts,
    with a damped rebound after each snap."""
    bounds = []
    acc = 0.0
    for t in ticks:
        bounds.append(acc)
        acc += t * 12.0
    out = []
    last_snap, snap_amp = -1e9, 0.0
    prev_d = None
    n = len(angles)
    for f in range(n):
        vals = []
        for s in range(sub):
            ft = f + s / sub
            a0 = angles[min(f, n - 1)]
            a1 = angles[min(f + 1, n - 1)]
            a = a0 + (a1 - a0) * s / sub
            d = min(((360 - (b + a)) % 360) for b in bounds)
            if prev_d is not None and d > prev_d + 180:
                last_snap = ft
                snap_amp = push
            prev_d = d
            v = push * (1 - d / win) if d < win else 0.0
            dt = ft - last_snap
            v += -0.45 * snap_amp * math.exp(-dt / 1.6) * math.cos(2 * math.pi * dt / 3.0)
            vals.append(v)
        out.append(vals[0])
    return out


def key_rot(ob, frame, deg_z):
    ob.rotation_euler = (ob.rotation_euler[0], ob.rotation_euler[1], math.radians(deg_z))
    ob.keyframe_insert("rotation_euler", index=2, frame=frame)


def args():
    a = sys.argv
    return a[a.index("--") + 1:] if "--" in a else []


def aim(ob, target):
    from mathutils import Vector
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def stack_lights(key=1.8, spec=140.0, spec_pos=(-2.6, 2.4, 2.4), spec_size=0.55):
    """Key sun from upper-left (shadows fall down-right) + area light for the dome highlight."""
    light("SUN", "key", (0, 0, 5), (1, 0.97, 0.95, 1), key, rot=(-40, -30, 0), angle=5)
    a = light("AREA", "spec", spec_pos, (0.85, 0.93, 1.0, 1), spec, size=spec_size)
    aim(a, (0, 0, 0))
    return a


STACK_Z = {"slices": 0.0, "hp": 0.02, "hub": 0.07, "needle": 0.19, "bezel": 0.16}


PARALLAX_DEPTH = {"slices": -1.0, "hp": 0.0, "bezel": 0.0, "hub": 0.8, "needle": 1.4, "dome": 1.2}


def apply_parallax(objs, p, k=0.055, base=None, backdrop_ob=None, bd_depth=-2.5, depths=None):
    """2D parallax: shift each layer by pointer offset p * k * depth (Parallax2D-style)."""
    depths = depths or PARALLAX_DEPTH
    base = base or {}
    for name, ob in objs.items():
        if name not in depths:
            continue
        bx, by = base.get(name, (ob.location.x, ob.location.y))
        base.setdefault(name, (bx, by))
        d = depths[name]
        ob.location.x = bx + p[0] * k * d
        ob.location.y = by + p[1] * k * d
    if backdrop_ob is not None:
        backdrop_ob.location.x = p[0] * k * bd_depth
        backdrop_ob.location.y = p[1] * k * bd_depth
    return base


def orbit(i, n, ax=1.0, ay=0.7):
    t = 2 * math.pi * i / n
    return (ax * math.cos(t), ay * math.sin(t))


def studio_lights(key=170.0, fills=(160.0, 140.0), rim=0.0, key_spec=1.0):
    """Lighting for the true-3D wheel: soft key top-left, pink fill left, cyan fill right."""
    k = light("AREA", "key3d", (-2.2, 2.0, 3.6), (1, 0.97, 0.94, 1), key, size=1.6)
    k.data.specular_factor = key_spec
    aim(k, (0, 0, 0))
    p = light("AREA", "pinkfill", (-2.6, -0.4, 0.9), PINK, fills[0], size=0.8)
    aim(p, (0, 0, 0))
    c = light("AREA", "cyanfill", (2.6, 0.3, 0.9), CYAN, fills[1], size=0.8)
    aim(c, (0, 0, 0))
    if rim:
        r = light("AREA", "rim", (0.0, 3.0, 0.8), (1, 1, 1, 1), rim, size=1.5)
        aim(r, (0, 0, 0))


SPIN_N, SPIN_STOP, SPIN_TOTAL = 44, 30, 956.0   # rests on crit with the next peg 4 deg short of the flap


def animate_spin(wheel_ob, needle_ob, ticks, n=SPIN_N, stop=SPIN_STOP, total=SPIN_TOTAL, wobble=8.0):
    """Keyframe a spin-down with a damped wobble, and the needle flap ticking on each peg."""
    sc = bpy.context.scene
    ang = spin_curve(n, total, stop, wobble=wobble, period=7.0, decay=4.0)
    flap = flap_curve(ang, ticks)
    for f in range(n):
        key_rot(wheel_ob, f + 1, -ang[f])
        key_rot(needle_ob, f + 1, flap[f])
    sc.frame_start, sc.frame_end = 1, n
    return ang, flap


def render_seq(folder, n=SPIN_N, frames=None):
    sc = bpy.context.scene
    for f in (frames or range(1, n + 1)):
        sc.frame_set(f)
        render(os.path.join(REN, folder, f"f{f:03d}.png"))


def orbit_camera(cam, tilt_deg, az_deg, cy=-0.15, cx=0.0, dist=12.0):
    """Place the ortho camera on a small orbit around the wheel (true 3D parallax)."""
    t, a = math.radians(tilt_deg), math.radians(az_deg)
    from mathutils import Matrix, Vector
    cam.location = (cx + dist * math.sin(t) * math.sin(a), cy - dist * math.sin(t) * math.cos(a),
                    dist * math.cos(t))
    f = (Vector((cx, cy, 0)) - cam.location).normalized()
    r = f.cross(Vector((0, 1, 0))).normalized()   # keep screen-up = world +Y (no roll)
    u = r.cross(f)
    m = Matrix((r, u, -f)).transposed()
    cam.rotation_euler = m.to_euler()
