"""R2A LOW-POLY 3D: shared Blender 5.2 helpers.

Flat-shaded, chunky faceted geometry; one soft key light; matte materials.
Seeded randomness only (random.Random instances passed around).
"""
import bpy
import bmesh
import math
import os
import random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
FONT_BOLD = os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf")
FONT_MONO = os.path.join(ROOT, "assets", "fonts", "ShareTechMono-Regular.ttf")
FONT_BODY = os.path.join(ROOT, "assets", "fonts", "IBMPlexSansCondensed-Medium.ttf")
SCRATCH = os.environ.get("R2A_SCRATCH", os.path.join(HERE, "..", "_tmp"))


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)


# ----------------------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def setup_render(sc, w=1920, h=1080, samples=48, view="Standard", exposure=0.0, gamma=1.0, look=None):
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("ENGINE", e)
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    ee = sc.eevee
    ee.taa_render_samples = samples
    for attr, val in (("use_shadows", True), ("shadow_pool_size", "1024"), ("use_raytracing", False),
                      ("use_fast_gi", False)):
        try:
            setattr(ee, attr, val)
        except Exception as e:
            print("EEVEE attr", attr, e)
    try:
        sc.view_settings.view_transform = view
    except TypeError as e:
        print("VIEW", e)
    if look:
        try:
            sc.view_settings.look = look
        except TypeError as e:
            print("LOOK", e)
    sc.view_settings.exposure = exposure
    sc.view_settings.gamma = gamma


def world(sc, col, strength=1.0):
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = hexcol(col)
    bg.inputs[1].default_value = strength
    return w


def sun(name, rot_deg, col, strength, angle=6.0, shadow=True):
    ld = bpy.data.lights.new(name, "SUN")
    ld.color = hexcol(col)[:3]
    ld.energy = strength
    ld.angle = math.radians(angle)
    ld.use_shadow = shadow
    ob = bpy.data.objects.new(name, ld)
    ob.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def point(name, loc, col, power, radius=0.3, shadow=False, spot=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, "SPOT" if spot else "POINT")
    ld.color = hexcol(col)[:3]
    ld.energy = power
    ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    if spot:
        ld.spot_size = math.radians(spot)
        ld.spot_blend = 0.4
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    return ob


def camera(name, loc, target, lens=35.0, dof=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 1000
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    return ob


# ----------------------------------------------------------------------------- materials

_MATS = {}


def mat_flat(name, col, rough=0.9, emit=None, emit_str=0.0, spec=0.15):
    """Matte, toy-like surface. Optional emission for neon inserts."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = hexcol(col)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = hexcol(emit)
        b.inputs["Emission Strength"].default_value = emit_str
    _MATS[name] = m
    return m


def mat_emit(name, col, strength=3.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
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
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs[0])
        m.surface_render_method = "BLENDED"
        m.use_backface_culling = False
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    _MATS[name] = m
    return m


def mat_beam(name, col, strength=1.5, a_near=0.25, a_far=0.0, axis=2):
    """Faceted light cone: emissive, alpha fading along generated Z (1 = source)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = a_far
    mr.inputs[4].default_value = a_near
    nt.links.new(sep.outputs[axis], mr.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = hexcol(col)
    em.inputs[1].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


# ----------------------------------------------------------------------------- poly builder

class PB:
    """Accumulates verts/faces with per-face material slot and per-vertex jitter amplitude."""

    def __init__(self):
        self.v = []
        self.j = []
        self.f = []
        self.m = []

    def vert(self, p, jit=0.0):
        self.v.append((float(p[0]), float(p[1]), float(p[2])))
        self.j.append(jit)
        return len(self.v) - 1

    def face(self, idx, mi=0):
        self.f.append(list(idx))
        self.m.append(mi)

    # -- primitives -------------------------------------------------------
    def prism(self, pts, z0, z1, mi_side, mi_top, jit=0.0, top_scale=1.0, cx=0.0, cy=0.0,
              top_center_dz=0.0, bottom=False, mi_bot=None, top_off=(0.0, 0.0)):
        """Extrude a CCW polygon (list of (x,y)) from z0 to z1. Top fan with an optional raised centre."""
        n = len(pts)
        bot = [self.vert((cx + x, cy + y, z0), 0.0) for x, y in pts]
        top = [self.vert((cx + x * top_scale + top_off[0], cy + y * top_scale + top_off[1], z1), jit) for x, y in pts]
        for i in range(n):
            a, b = i, (i + 1) % n
            self.face([bot[a], bot[b], top[b], top[a]], mi_side)
        mx = sum(p[0] for p in pts) / n * top_scale + cx + top_off[0]
        my = sum(p[1] for p in pts) / n * top_scale + cy + top_off[1]
        c = self.vert((mx, my, z1 + top_center_dz), jit)
        for i in range(n):
            self.face([top[i], top[(i + 1) % n], c], mi_top)
        if bottom:
            cb = self.vert((sum(p[0] for p in pts) / n + cx, sum(p[1] for p in pts) / n + cy, z0), 0.0)
            for i in range(n):
                self.face([bot[(i + 1) % n], bot[i], cb], mi_bot if mi_bot is not None else mi_side)
        return bot, top

    def rings(self, per, zs, mats_fn, jit=0.0, taper=0.0, cx=0.0, cy=0.0, cap_dz=0.0, mi_cap=0):
        """Stacked rings of a perimeter -> side quads (material by mats_fn(band, seg)) + top cap."""
        H = zs[-1] if zs[-1] > 0 else 1.0
        ring_ids = []
        for k, z in enumerate(zs):
            s = 1.0 - taper * (z / H)
            jj = 0.0 if k == 0 else jit
            ring_ids.append([self.vert((cx + x * s, cy + y * s, z), jj) for x, y in per])
        n = len(per)
        for k in range(len(zs) - 1):
            for i in range(n):
                a, b = i, (i + 1) % n
                self.face([ring_ids[k][a], ring_ids[k][b], ring_ids[k + 1][b], ring_ids[k + 1][a]], mats_fn(k, i))
        top = ring_ids[-1]
        s = 1.0 - taper
        c = self.vert((cx + sum(p[0] for p in per) / n * s, cy + sum(p[1] for p in per) / n * s, zs[-1] + cap_dz), jit)
        for i in range(n):
            self.face([top[i], top[(i + 1) % n], c], mi_cap)
        return ring_ids

    def build(self, name, mats, seed=0, coll=None, tri=True, loc=(0, 0, 0), shadow=True):
        rng = random.Random(seed)
        vs = []
        for p, a in zip(self.v, self.j):
            if a > 0:
                vs.append((p[0] + rng.uniform(-a, a), p[1] + rng.uniform(-a, a), p[2] + rng.uniform(-a, a)))
            else:
                vs.append(p)
        me = bpy.data.meshes.new(name)
        me.from_pydata(vs, [], self.f)
        for m in mats:
            me.materials.append(m)
        mi = self.m
        for poly, k in zip(me.polygons, mi):
            poly.material_index = k
        if tri:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
            bm.to_mesh(me)
            bm.free()
        for p in me.polygons:
            p.use_smooth = False
        me.update()
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        ob.visible_shadow = shadow
        (coll or bpy.context.scene.collection).objects.link(ob)
        return ob


def ngon(n, r, rot=0.0, sx=1.0, sy=1.0):
    return [(math.cos(rot + i * 2 * math.pi / n) * r * sx, math.sin(rot + i * 2 * math.pi / n) * r * sy) for i in range(n)]


def rect(w, d):
    return [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]


def perimeter(w, d, seg, chamfer=0.0):
    c = rect(w, d)
    if chamfer > 0:
        poly = []
        for i in range(4):
            p = Vector(c[i]); pr = Vector(c[i - 1]); nx = Vector(c[(i + 1) % 4])
            poly.append(tuple(p + (pr - p).normalized() * chamfer))
            poly.append(tuple(p + (nx - p).normalized() * chamfer))
    else:
        poly = c
    out = []
    n = len(poly)
    for i in range(n):
        a = Vector(poly[i]); b = Vector(poly[(i + 1) % n])
        k = max(1, round((b - a).length / seg))
        for t in range(k):
            q = a.lerp(b, t / k)
            out.append((q.x, q.y))
    return out


# ----------------------------------------------------------------------------- objects

def obj_from_pb(pb, name, mats, seed=0, **kw):
    return pb.build(name, mats, seed=seed, **kw)


def ico(name, loc, r, mat, sub=1, jit=0.0, seed=0, scale=(1, 1, 1), coll=None, shadow=True):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    rng = random.Random(seed)
    for v in bm.verts:
        v.co.x = v.co.x * scale[0] + rng.uniform(-jit, jit)
        v.co.y = v.co.y * scale[1] + rng.uniform(-jit, jit)
        v.co.z = v.co.z * scale[2] + rng.uniform(-jit, jit)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.visible_shadow = shadow
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def text(name, body, loc, size, mat, rot=(0, 0, 0), extrude=0.02, align="CENTER", font=FONT_BOLD,
         coll=None, res=2, parent=None, shadow=True, valign="CENTER", spacing=1.0):
    cu = bpy.data.curves.new(name, type="FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = valign
    cu.resolution_u = res if font == FONT_BOLD else max(res, 4)
    cu.space_character = spacing
    if font and os.path.exists(font):
        cu.font = bpy.data.fonts.load(font, check_existing=True)
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = rot
    ob.visible_shadow = shadow
    if parent is not None:
        ob.parent = parent
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


# ----------------------------------------------------------------------------- compositor

def compositor(sc, bloom=(1.0, 0.35, 6), soft=0.0):
    ng = bpy.data.node_groups.new("r2a_comp", "CompositorNodeTree")
    sc.compositing_node_group = ng
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    out = ng.nodes.new("NodeGroupOutput")
    rl = ng.nodes.new("CompositorNodeRLayers")
    cur = rl.outputs["Image"]
    if bloom:
        gl = ng.nodes.new("CompositorNodeGlare")
        try:
            gl.inputs["Type"].default_value = "Bloom"
        except Exception as e:
            print("GLARE type", e)
        for k, v in (("Threshold", bloom[0]), ("Strength", bloom[1]), ("Size", bloom[2])):
            try:
                gl.inputs[k].default_value = v
            except Exception as e:
                print("GLARE", k, e)
        try:
            gl.inputs["Quality"].default_value = "High"
        except Exception:
            pass
        ng.links.new(cur, gl.inputs["Image"])
        cur = gl.outputs["Image"]
    ng.links.new(cur, out.inputs[0])


def render(sc, path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def args():
    import sys
    a = sys.argv
    if "--" in a:
        return a[a.index("--") + 1:]
    return []


# ----------------------------------------------------------------------------- camera-space HUD

class HUD:
    """Places objects in camera space at a fixed depth, by normalised screen coords (0..1, y up)."""

    def __init__(self, cam, depth=4.0, aspect=16 / 9):
        self.cam = cam
        self.depth = depth
        self.hw = depth * math.tan(cam.data.angle / 2)
        self.hh = self.hw / aspect
        self.root = bpy.data.objects.new("HUD_root", None)
        self.root.parent = cam
        bpy.context.scene.collection.objects.link(self.root)

    def pos(self, u, v, dz=0.0):
        return ((u - 0.5) * 2 * self.hw, (v - 0.5) * 2 * self.hh, -self.depth + dz)

    def unit(self):
        """World units per screen height at the HUD depth."""
        return 2 * self.hh

    def adopt(self, ob, u, v, dz=0.0, rot=(0, 0, 0)):
        ob.parent = self.root
        ob.location = self.pos(u, v, dz)
        ob.rotation_euler = rot
        ob.visible_shadow = False
        return ob
