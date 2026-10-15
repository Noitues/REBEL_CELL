"""New corps: Blender-side library (runs inside headless Blender 5.2). Identical copy in both scripts/ folders.

Geometry is generated, merged per material and triangulated; every face gets a seeded tone jitter (`fj`) that the
materials multiply in (the Cv2 facet grain). Lights, fog media, the camera, the render and the anchors file live here.
All randomness comes from seeded random.Random streams.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


# ------------------------------------------------------------------ job args
def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    for s in a:
        if "=" in s:
            k, v = s.split("=", 1)
            try:
                out[k] = json.loads(v)
            except ValueError:
                out[k] = v
    return out


def log(*a):
    print("[nc]", *a, flush=True)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0], c[1], c[2], a)


# ------------------------------------------------------------------ materials
_M = {}


def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt


def _jitter(nt, base_rgb, amp):
    """Base colour x (1 - amp + 2 amp fj): the per-face tone jitter."""
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "fj"
    at.attribute_type = "GEOMETRY"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs[3].default_value = 1 - amp
    mr.inputs[4].default_value = 1 + amp
    nt.links.new(at.outputs["Fac"], mr.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    mix.inputs[6].default_value = base_rgb
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(mr.outputs[0], comb.inputs[i])
    nt.links.new(comb.outputs[0], mix.inputs[7])
    return mix.outputs[2]


def mat_solid(name, rgb, rough=0.6, metal=0.0, jitter=0.12, spec=0.5, emit=None, emit_k=0.0, wet=None):
    """Principled with the facet jitter. wet = (scale, k): puddle roughness from noise (world xy)."""
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    nt = _nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], out.inputs[0])
    nt.links.new(_jitter(nt, rgb, jitter), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    try:
        p.inputs["Specular IOR Level"].default_value = spec
    except KeyError:
        pass
    if emit is not None:
        p.inputs["Emission Color"].default_value = emit
        p.inputs["Emission Strength"].default_value = emit_k
    if wet:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = wet[0]
        nz.inputs["Detail"].default_value = 3.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = 0.45
        mr.inputs[2].default_value = 0.55
        mr.inputs[3].default_value = wet[1]
        mr.inputs[4].default_value = rough
        nt.links.new(nz.outputs["Fac"], mr.inputs[0])
        nt.links.new(mr.outputs[0], p.inputs["Roughness"])
    _M[name] = m
    return m


def mat_emit(name, rgb, k=6.0, alpha=1.0):
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    nt = _nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = rgb
    e.inputs[1].default_value = k
    if alpha < 1.0:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(e.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        try:
            m.surface_render_method = "BLENDED"
        except (AttributeError, TypeError):
            pass
    else:
        nt.links.new(e.outputs[0], out.inputs[0])
    _M[name] = m
    return m


def mat_glass(name, rgb, rough=0.08, alpha=0.25, emit=None, emit_k=0.0):
    """Thin glass: mostly transparent with a fresnel sheen (domes, tubes, windows seen from outside)."""
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    nt = _nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = rgb
    p.inputs["Roughness"].default_value = rough
    p.inputs["Alpha"].default_value = alpha
    if emit is not None:
        p.inputs["Emission Color"].default_value = emit
        p.inputs["Emission Strength"].default_value = emit_k
    nt.links.new(p.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        pass
    _M[name] = m
    return m


def mat_volume(name, rgb, density, aniso=0.4, absorb=None, noise=None, height=None, emit=None, emit_k=0.0):
    """A fog medium: density x noise remap x exp height falloff (object coords: the box is 0..1 in generated)."""
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    nt = _nodes(m)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = rgb
    v.inputs["Anisotropy"].default_value = aniso
    if absorb is not None:
        v.inputs["Absorption Color"].default_value = absorb
    if emit is not None:
        v.inputs["Emission Color"].default_value = emit
        v.inputs["Emission Strength"].default_value = emit_k
    dens = None
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if noise:
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 4.0
        nz.inputs["Roughness"].default_value = 0.6
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs[1].default_value = noise[1]
        mr.inputs[2].default_value = noise[2]
        nt.links.new(nz.outputs["Fac"], mr.inputs[0])
        dens = mr.outputs[0]
    if height:
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        mth = nt.nodes.new("ShaderNodeMath")
        mth.operation = "MULTIPLY"
        mth.inputs[1].default_value = -height
        nt.links.new(sep.outputs["Z"], mth.inputs[0])
        ex = nt.nodes.new("ShaderNodeMath")
        ex.operation = "EXPONENT"
        nt.links.new(mth.outputs[0], ex.inputs[0])
        if dens is not None:
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            nt.links.new(dens, mul.inputs[0])
            nt.links.new(ex.outputs[0], mul.inputs[1])
            dens = mul.outputs[0]
        else:
            dens = ex.outputs[0]
    if dens is not None:
        k = nt.nodes.new("ShaderNodeMath")
        k.operation = "MULTIPLY"
        k.inputs[1].default_value = density
        nt.links.new(dens, k.inputs[0])
        nt.links.new(k.outputs[0], v.inputs["Density"])
    else:
        v.inputs["Density"].default_value = density
    nt.links.new(v.outputs[0], out.inputs["Volume"])
    _M[name] = m
    return m


# ------------------------------------------------------------------ geometry accumulation
class Geo:
    """Accumulate faces per material key, then build one triangulated object per key."""

    def __init__(self, seed=1):
        self.parts = {}
        self.rng = random.Random(seed)

    def _p(self, key):
        if key not in self.parts:
            self.parts[key] = ([], [])
        return self.parts[key]

    def poly_faces(self, key, verts, faces):
        V, F = self._p(key)
        o = len(V)
        V.extend(verts)
        F.extend([tuple(i + o for i in f) for f in faces])

    def box(self, key, c, s, rz=0.0):
        """Box centred at c=(x,y,z) with full sizes s=(sx,sy,sz), rotated rz about z."""
        x, y, z = c
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        cr, sr = math.cos(rz), math.sin(rz)
        vs = []
        for dz in (-hz, hz):
            for dx, dy in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)):
                vs.append((x + dx * cr - dy * sr, y + dx * sr + dy * cr, z + dz))
        fs = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.poly_faces(key, vs, fs)

    def quad(self, key, pts):
        self.poly_faces(key, pts, [(0, 1, 2, 3)])

    def prism(self, key, pts2, depth, origin, rz=0.0):
        """Extrude a 2D outline (local u along the facade, v up) by depth (local w, into the building)."""
        ox, oy, oz = origin
        cr, sr = math.cos(rz), math.sin(rz)
        n = len(pts2)
        vs = []
        for w in (0.0, depth):
            for u, v in pts2:
                vs.append((ox + u * cr - w * sr, oy + u * sr + w * cr, oz + v))
        fs = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for i in range(n):
            j = (i + 1) % n
            fs.append((i, j, n + j, n + i))
        self.poly_faces(key, vs, fs)

    def cyl(self, key, c, r, h, n=8, r2=None, cap=True, rot0=0.0):
        x, y, z = c
        r2 = r if r2 is None else r2
        vs = []
        for k in range(n):
            a = rot0 + 2 * math.pi * k / n
            vs.append((x + r * math.cos(a), y + r * math.sin(a), z))
        for k in range(n):
            a = rot0 + 2 * math.pi * k / n
            vs.append((x + r2 * math.cos(a), y + r2 * math.sin(a), z + h))
        fs = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        if cap:
            fs += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        self.poly_faces(key, vs, fs)

    def ring(self, key, c, r0, r1, h, n=48, a0=0.0, a1=2 * math.pi):
        """An annular sector wall (r0 inner, r1 outer) from z to z+h."""
        x, y, z = c
        m = max(2, int(n * (a1 - a0) / (2 * math.pi)) + 1)
        vs = []
        for zz in (z, z + h):
            for rr in (r0, r1):
                for k in range(m):
                    a = a0 + (a1 - a0) * k / (m - 1)
                    vs.append((x + rr * math.cos(a), y + rr * math.sin(a), zz))
        def I(zi, ri, k):
            return zi * 2 * m + ri * m + k
        fs = []
        for k in range(m - 1):
            fs.append((I(0, 0, k), I(0, 1, k), I(0, 1, k + 1), I(0, 0, k + 1)))     # bottom
            fs.append((I(1, 0, k), I(1, 0, k + 1), I(1, 1, k + 1), I(1, 1, k)))     # top
            fs.append((I(0, 1, k), I(1, 1, k), I(1, 1, k + 1), I(0, 1, k + 1)))     # outer
            fs.append((I(0, 0, k), I(0, 0, k + 1), I(1, 0, k + 1), I(1, 0, k)))     # inner
        if a1 - a0 < 2 * math.pi - 1e-3:
            for k in (0, m - 1):
                fs.append((I(0, 0, k), I(1, 0, k), I(1, 1, k), I(0, 1, k)))
        self.poly_faces(key, vs, fs)

    def dome(self, key, c, r, n=16, rings=6, z_scale=1.0, a_top=math.pi / 2):
        x, y, z = c
        vs = []
        for j in range(rings + 1):
            phi = a_top * j / rings
            for k in range(n):
                a = 2 * math.pi * k / n
                vs.append((x + r * math.cos(phi) * math.cos(a), y + r * math.cos(phi) * math.sin(a), z + r * z_scale * math.sin(phi)))
        fs = []
        for j in range(rings):
            for k in range(n):
                a, b = j * n + k, j * n + (k + 1) % n
                fs.append((a, b, b + n, a + n))
        self.poly_faces(key, vs, fs)

    def sphere(self, key, c, r, n=10, rings=6):
        x, y, z = c
        vs = [(x, y, z - r)]
        for j in range(1, rings):
            phi = -math.pi / 2 + math.pi * j / rings
            for k in range(n):
                a = 2 * math.pi * k / n
                vs.append((x + r * math.cos(phi) * math.cos(a), y + r * math.cos(phi) * math.sin(a), z + r * math.sin(phi)))
        vs.append((x, y, z + r))
        fs = [(0, 1 + (k + 1) % n, 1 + k) for k in range(n)]
        for j in range(rings - 2):
            for k in range(n):
                a, b = 1 + j * n + k, 1 + j * n + (k + 1) % n
                fs.append((a, b, b + n, a + n))
        top = len(vs) - 1
        base = 1 + (rings - 2) * n
        fs += [(base + k, base + (k + 1) % n, top) for k in range(n)]
        self.poly_faces(key, vs, fs)

    def tube(self, key, pts, r, n=8):
        """A tube along a polyline (kelp, cables, conduits)."""
        for a, b in zip(pts, pts[1:]):
            A, B = Vector(a), Vector(b)
            d = B - A
            L = d.length
            if L < 1e-6:
                continue
            q = d.normalized().to_track_quat("Z", "Y")
            M = Matrix.Translation(A) @ q.to_matrix().to_4x4()
            vs, fs = [], []
            for zz in (0, L):
                for k in range(n):
                    t = 2 * math.pi * k / n
                    vs.append(tuple(M @ Vector((r * math.cos(t), r * math.sin(t), zz))))
            fs = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
            self.poly_faces(key, vs, fs)

    def finish(self, mats, coll=None, seed=7, flags=None):
        rng = random.Random(seed)
        out = {}
        for key, (V, F) in self.parts.items():
            if not F:
                continue
            me = bpy.data.meshes.new(key)
            me.from_pydata(V, [], F)
            me.validate()
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(me)
            bm.free()
            at = me.attributes.new("fj", "FLOAT", "FACE")
            vals = [rng.random() for _ in range(len(me.polygons))]
            at.data.foreach_set("value", vals)
            ob = bpy.data.objects.new(key, me)
            (coll or bpy.context.scene.collection).objects.link(ob)
            m = mats.get(key) if isinstance(mats, dict) else mats(key)
            if m is not None:
                me.materials.append(m)
            if flags and key in flags:
                for k, v in flags[key].items():
                    setattr(ob, k, v)
            out[key] = ob
        return out


# ------------------------------------------------------------------ lights, camera, world, text
def light(kind, loc, energy, rgb=(1, 1, 1), size=1.0, aim=None, spot=None, blend=0.3, shadow=True, name=None, shape=None, size_y=None):
    ld = bpy.data.lights.new(name or kind, kind)
    ld.energy = energy
    ld.color = rgb[:3]
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "AREA":
        ld.size = size
        if size_y:
            ld.shape = "RECTANGLE"
            ld.size_y = size_y
    if kind == "SPOT":
        ld.spot_size = math.radians(spot or 20)
        ld.spot_blend = blend
    if kind == "SUN":
        ld.angle = math.radians(size)
    try:
        ld.use_shadow = shadow
    except AttributeError:
        pass
    ob = bpy.data.objects.new(ld.name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if aim is not None:
        d = Vector(aim) - Vector(loc)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def camera(loc, target, lens=35.0, shift=(0.0, 0.0), clip=(0.5, 6000.0)):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.shift_x, cd.shift_y = shift
    cd.clip_start, cd.clip_end = clip
    ob = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    return ob


def world(top, bottom, k=1.0):
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    nt = _nodes(w)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs[1].default_value = k
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = bottom
    ramp.color_ramp.elements[1].color = top
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return w


def text_obj(s, loc, size, mat, rz=0.0, rx=math.pi / 2, align="CENTER", extrude=0.05):
    cu = bpy.data.curves.new("t_" + s[:8], "FONT")
    cu.body = s
    cu.size = size
    cu.align_x = align
    cu.extrude = extrude
    ob = bpy.data.objects.new("t_" + s[:8], cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (rx, 0, rz)
    cu.materials.append(mat)
    return ob


def volume_box(name, lo, hi, mat):
    me = bpy.data.meshes.new(name)
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(V, [], F)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


# ------------------------------------------------------------------ render
def gpu_setup():
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "HIP"
        try:
            prefs.use_hiprt = False
        except (AttributeError, TypeError):
            pass
        prefs.refresh_devices()
        n = 0
        for d in prefs.devices:
            d.use = d.type == "HIP"
            n += d.use
        log("HIP devices", n)
        return n > 0
    except Exception as e:  # noqa: BLE001
        log("HIP setup failed", e)
        return False


def setup_render(J):
    sc = bpy.context.scene
    eng = J.get("engine", "eevee")
    sc.render.resolution_x, sc.render.resolution_y = J.get("res", [1280, 720])
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    if eng == "cycles":
        sc.render.engine = "CYCLES"
        cy = sc.cycles
        cy.device = "CPU" if J.get("cpu") else ("GPU" if gpu_setup() else "CPU")
        cy.samples = J.get("samples", 96)
        cy.use_adaptive_sampling = True
        cy.adaptive_threshold = J.get("threshold", 0.03)
        cy.use_denoising = True
        for k_, v_ in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_use_gpu", True)):
            try:
                setattr(cy, k_, v_)
            except (TypeError, AttributeError):
                pass
        cy.seed = 7
        cy.max_bounces = 5
        cy.diffuse_bounces = 2
        cy.glossy_bounces = 2
        cy.transmission_bounces = 3
        cy.volume_bounces = 0
        cy.transparent_max_bounces = 12
        cy.sample_clamp_indirect = 5.0
        cy.caustics_reflective = False
        cy.caustics_refractive = False
        cy.volume_step_rate = J.get("step_rate", 2.0)
        cy.volume_max_steps = 192
        try:
            cy.use_light_tree = True
        except AttributeError:
            pass
    else:
        for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            try:
                sc.render.engine = e
                break
            except TypeError:
                continue
        ee = sc.eevee
        for k_, v_ in (("taa_render_samples", J.get("samples", 24)), ("use_volumetric_shadows", True),
                       ("volumetric_tile_size", "4"), ("volumetric_samples", 48), ("volumetric_end", J.get("vol_end", 900.0)),
                       ("use_shadows", True), ("use_raytracing", True)):
            try:
                setattr(ee, k_, v_)
            except (AttributeError, TypeError):
                pass
    s_ = sc.render.image_settings
    s_.file_format = "OPEN_EXR"
    s_.color_depth = "16"
    s_.exr_codec = "ZIP"


def render(J, anchors=None):
    """Render to <out>.exr, dump float pixels to <out>.npy (h, w, 4, float16) and the anchors to <out>.json."""
    import numpy as np
    sc = bpy.context.scene
    out = J["out"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out + ".exr"
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(out + ".exr")
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1].astype(np.float16)
    np.save(out + ".npy", a)
    log("saved", out + ".npy", a.shape)
    if anchors is not None:
        from bpy_extras.object_utils import world_to_camera_view
        cam = sc.camera
        res = {}
        for k, p in anchors.items():
            q = world_to_camera_view(sc, cam, Vector(p))
            res[k] = [q.x * w, (1 - q.y) * h, q.z]
        with open(out + ".json", "w") as f:
            json.dump(res, f)
    try:
        os.remove(out + ".exr")
    except OSError:
        pass
