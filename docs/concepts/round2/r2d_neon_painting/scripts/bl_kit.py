"""Blender helpers: materials, meshes, light arcs, fog, render setup (Blender 5.2)."""
import math
import bpy
from mathutils import Vector

_MATS = {}


def _nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt.nodes, nt.links


def _set(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def rgba(c):
    return (c[0], c[1], c[2], 1.0)


def m_emit(col, strength, additive=False, alpha=1.0, key=None):
    k = key or ("E", tuple(round(x, 3) for x in col), round(strength, 3), additive, alpha)
    if k in _MATS:
        return _MATS[k]
    mat = bpy.data.materials.new("emit")
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(col)
    em.inputs["Strength"].default_value = strength
    if additive or alpha < 1.0:
        tr = nodes.new("ShaderNodeBsdfTransparent")
        if additive:
            mix = nodes.new("ShaderNodeAddShader")
            links.new(tr.outputs[0], mix.inputs[0])
            links.new(em.outputs[0], mix.inputs[1])
        else:
            mix = nodes.new("ShaderNodeMixShader")
            mix.inputs[0].default_value = alpha
            links.new(tr.outputs[0], mix.inputs[1])
            links.new(em.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], out.inputs["Surface"])
        mat.surface_render_method = "BLENDED"
    else:
        links.new(em.outputs[0], out.inputs["Surface"])
    _MATS[k] = mat
    return mat


def m_pbr(base, rough=0.4, metal=0.0, emit=None, es=0.0, film=0.0, alpha=1.0, coat=0.0, name="pbr"):
    mat = bpy.data.materials.new(name)
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    p = nodes.new("ShaderNodeBsdfPrincipled")
    _set(p, "Base Color", rgba(base))
    _set(p, "Roughness", rough)
    _set(p, "Metallic", metal)
    _set(p, "Coat Weight", coat)
    if emit is not None:
        _set(p, "Emission Color", rgba(emit))
        _set(p, "Emission Strength", es)
    if film > 0:
        _set(p, "Thin Film Thickness", film)
        _set(p, "Thin Film IOR", 1.45)
    _set(p, "Alpha", alpha)
    if alpha < 1.0:
        mat.surface_render_method = "BLENDED"
    links.new(p.outputs[0], out.inputs["Surface"])
    return mat


def m_veil(col, amount):
    """Flat see-through tint: mix(transparent, emission col)."""
    mat = bpy.data.materials.new("veil")
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    tr = nodes.new("ShaderNodeBsdfTransparent")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgba(col)
    em.inputs["Strength"].default_value = 1.0
    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = amount
    links.new(tr.outputs[0], mix.inputs[1])
    links.new(em.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


def ramp(nodes, stops, interp="LINEAR"):
    r = nodes.new("ShaderNodeValToRGB")
    cr = r.color_ramp
    cr.interpolation = interp
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    cr.elements[0].position = stops[0][0]
    cr.elements[0].color = rgba(stops[0][1])
    for pos, c in stops[1:]:
        e = cr.elements.new(pos)
        e.color = rgba(c)
    return r


def m_screen(stops, strength, scale=0.18, name="screen"):
    """Painted neon 'laptop screen' gradient: noise -> multi-stop ramp -> emission."""
    mat = bpy.data.materials.new(name)
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    tc = nodes.new("ShaderNodeTexCoord")
    nz = nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    _set(nz, "Detail", 3.0)
    _set(nz, "Distortion", 1.2)
    links.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = ramp(nodes, stops)
    links.new(nz.outputs["Fac"], r.inputs[0])
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    links.new(r.outputs[0], em.inputs["Color"])
    links.new(em.outputs[0], out.inputs["Surface"])
    return mat


def m_volume(col, density, emit=(0, 0, 0), es=0.0, aniso=0.2):
    mat = bpy.data.materials.new("fog")
    nodes, links = _nodes(mat)
    out = nodes.new("ShaderNodeOutputMaterial")
    v = nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = rgba(col)
    v.inputs["Density"].default_value = density
    v.inputs["Anisotropy"].default_value = aniso
    v.inputs["Emission Color"].default_value = rgba(emit)
    v.inputs["Emission Strength"].default_value = es
    links.new(v.outputs[0], out.inputs["Volume"])
    return mat


# ---- geometry -------------------------------------------------------------

def link(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def mesh_obj(name, verts, faces, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, mats=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    if mats:
        for m in mats:
            me.materials.append(m)
    elif mat is not None:
        me.materials.append(mat)
    return link(ob, parent)


class MeshBuf:
    """Accumulate many boxes / polys into one mesh (fast)."""

    def __init__(self):
        self.v = []
        self.f = []
        self.mi = []

    def box(self, cx, cy, z0, sx, sy, sz, rot=0.0, bottom=False, m=0):
        c, s = math.cos(rot), math.sin(rot)
        b = len(self.v)
        for dz in (z0, z0 + sz):
            for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
                self.v.append((cx + dx * c - dy * s, cy + dx * s + dy * c, dz))
        faces = [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        if bottom:
            faces.append((3, 2, 1, 0))
        for f in faces:
            self.f.append(tuple(b + i for i in f))
            self.mi.append(m)

    def poly(self, pts, m=0):
        b = len(self.v)
        self.v.extend(pts)
        self.f.append(tuple(range(b, b + len(pts))))
        self.mi.append(m)

    def prism(self, pts2d, z0, z1, xf=None, m=0):
        """Extruded polygon; xf maps a local (x,y,z) to world."""
        n = len(pts2d)
        b = len(self.v)
        for z in (z0, z1):
            for x, y in pts2d:
                p = (x, y, z)
                self.v.append(xf(p) if xf else p)
        self.f.append(tuple(b + n + i for i in range(n)))
        self.mi.append(m)
        self.f.append(tuple(b + i for i in reversed(range(n))))
        self.mi.append(m)
        for i in range(n):
            j = (i + 1) % n
            self.f.append((b + i, b + j, b + n + j, b + n + i))
            self.mi.append(m)

    def build(self, name, mats, loc=(0, 0, 0), parent=None):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        for m in mats:
            me.materials.append(m)
        if len(mats) > 1:
            me.polygons.foreach_set("material_index", self.mi)
        me.update()
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        return link(ob, parent)


def rrect(w, h, r, seg=6):
    pts = []
    cs = [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]
    for cx, cy, a in cs:
        for k in range(seg + 1):
            t = math.radians(a + 90.0 * k / seg)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def curve_obj(name, pts3, thick, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, cyclic=False, radii=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thick
    cu.bevel_resolution = 1
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts3) - 1)
    for i, p in enumerate(pts3):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
        if radii:
            sp.points[i].radius = radii[i]
    sp.use_cyclic_u = cyclic
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, parent)


def arc(name, radius, a0, a1, thick, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, spiral=0.0, taper=True, seg=None):
    """Light arc in the local XY plane from angle a0 to a1 (degrees). spiral grows the radius."""
    n = seg or max(8, int(abs(a1 - a0) / 3))
    pts, rad = [], []
    for k in range(n + 1):
        t = k / n
        a = math.radians(a0 + (a1 - a0) * t)
        r = radius * (1.0 + spiral * t)
        pts.append((r * math.cos(a), r * math.sin(a), 0.0))
        rad.append(max(0.08, math.sin(math.pi * t)) if taper else 1.0)
    return curve_obj(name, pts, thick, mat, loc, rot, parent, radii=rad)


def swirl(rng, name, loc, rot, r_min, r_max, n, palette, strength, thick=(0.01, 0.05),
          parent=None, tilt=0.0, spiral=(-0.08, 0.12), span=(40, 300)):
    """A cluster of swirling light arcs (the reference's rings of light)."""
    objs = []
    for k in range(n):
        t = rng.random()
        r = r_min + (r_max - r_min) * t
        idx = min(len(palette) - 1, int(t * len(palette)))
        col = palette[idx]
        s = strength * (0.6 + 0.8 * rng.random())
        a0 = rng.uniform(0, 360)
        a1 = a0 + rng.uniform(*span)
        th = rng.uniform(*thick)
        rr = (rot[0] + rng.uniform(-tilt, tilt), rot[1] + rng.uniform(-tilt, tilt), rot[2])
        objs.append(arc(f"{name}{k}", r, a0, a1, th, m_emit(col, s), loc, rr, parent,
                        spiral=rng.uniform(*spiral)))
    return objs


def fog_box(center, size, mat):
    b = MeshBuf()
    b.box(center[0], center[1], center[2] - size[2] / 2, size[0], size[1], size[2], bottom=True)
    return b.build("fog", [mat])


def point_light(loc, col, energy, radius=0.5, shadow=False, parent=None):
    ld = bpy.data.lights.new("pl", "POINT")
    ld.color = col
    ld.energy = energy
    ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    ob = bpy.data.objects.new("pl", ld)
    ob.location = loc
    return link(ob, parent)


def spot_light(loc, target, col, energy, size_deg, blend=0.3, shadow=True):
    ld = bpy.data.lights.new("spot", "SPOT")
    ld.color = col
    ld.energy = energy
    ld.spot_size = math.radians(size_deg)
    ld.spot_blend = blend
    ld.use_shadow = shadow
    ld.shadow_soft_size = 0.2
    ob = bpy.data.objects.new("spot", ld)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return link(ob)


def sun(dir_rot, col, energy, angle=2.0):
    ld = bpy.data.lights.new("sun", "SUN")
    ld.color = col
    ld.energy = energy
    ld.angle = math.radians(angle)
    ob = bpy.data.objects.new("sun", ld)
    ob.rotation_euler = [math.radians(a) for a in dir_rot]
    return link(ob)


def camera(loc, target, lens):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.clip_start = 0.1
    cd.clip_end = 1500
    ob = bpy.data.objects.new("cam", cd)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def world(top, horizon, strength, ground=None):
    w = bpy.data.worlds.new("world")
    bpy.context.scene.world = w
    nodes, links = _nodes(w)
    out = nodes.new("ShaderNodeOutputWorld")
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.15
    mr.inputs["From Max"].default_value = 0.6
    links.new(sep.outputs["Z"], mr.inputs["Value"])
    r = ramp(nodes, [(0.0, ground or horizon), (0.2, horizon), (1.0, top)])
    links.new(mr.outputs["Result"], r.inputs[0])
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    links.new(r.outputs[0], bg.inputs["Color"])
    links.new(bg.outputs[0], out.inputs["Surface"])


def setup_render(samples=64, bloom=(0.9, 0.6, 0.75)):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    ee = sc.eevee
    ee.taa_render_samples = samples
    for k, v in (("use_raytracing", True), ("volumetric_end", 450.0), ("volumetric_start", 0.5),
                 ("volumetric_tile_size", "4"), ("volumetric_samples", 96),
                 ("use_volumetric_shadows", True), ("volumetric_light_clamp", 0.0),
                 ("shadow_pool_size", "1024"), ("bokeh_max_size", 60.0), ("use_fast_gi", True)):
        try:
            setattr(ee, k, v)
        except Exception as e:  # noqa
            print("EEVEE set fail", k, e)
    try:
        sc.view_settings.view_transform = "Standard"
    except Exception as e:
        print("VT", e)
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    tree = bpy.data.node_groups.new("comp", "CompositorNodeTree")
    sc.compositing_node_group = tree
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = tree.nodes.new("CompositorNodeRLayers")
    gl = tree.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = bloom[0]
    gl.inputs["Strength"].default_value = bloom[1]
    gl.inputs["Size"].default_value = bloom[2]
    out = tree.nodes.new("NodeGroupOutput")
    tree.links.new(rl.outputs["Image"], gl.inputs["Image"])
    tree.links.new(gl.outputs["Image"], out.inputs[0])
