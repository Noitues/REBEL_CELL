"""Round 12 MODEM facade: shared Blender helpers (runs inside Blender 5.2, headless).

Geometry: every surface is a jittered, triangulated grid; each triangle carries its own colour in a
`col` corner attribute (Cv2 gritty facets), plus `emit` (emissive RGB) and `wet` (R = gloss, G = rough).
One toon material bands the light (Shader to RGB -> luminance quantised into constant steps, hue kept).
Camera is fixed: one-point perspective, lens shift; layout coordinates are derived from screen targets.
"""
import json
import math
import os
import random

import bpy
import numpy as np

W, H = 1920, 1080
LENS = 24.0
SENSOR = 36.0
HT = SENSOR / 2 / LENS          # horizontal half-tan
VT = HT * H / W                 # vertical half-tan
CAM = dict(h=6.0, shx=0.169, shy=0.0)


def sx_to_x(sx, d):
    return d * ((sx - W / 2) / (W / 2) * HT + 2 * HT * CAM['shx'])


def sy_to_z(sy, d):
    return CAM['h'] + d * ((H / 2 - sy) / (H / 2) * VT + 2 * HT * CAM['shy'])


def proj(p):
    """World point -> screen px (camera at (0,0,h) looking +y)."""
    x, y, z = p
    sx = W / 2 + (x / y - 2 * HT * CAM['shx']) / HT * (W / 2)
    sy = H / 2 - ((z - CAM['h']) / y - 2 * HT * CAM['shy']) / VT * (H / 2)
    return sx, sy


# ------------------------------------------------------------------ colour
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexl(h):
    h = h.lstrip('#')
    return tuple(lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def mixc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def scl(a, k):
    return tuple(c * k for c in a)


# ------------------------------------------------------------------ scene
def reset(samples=32):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    pct = int(os.environ.get('MF_PCT', '100'))
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = pct
    ee = sc.eevee
    ee.taa_render_samples = samples
    ee.use_raytracing = True
    try:
        ee.ray_tracing_method = 'SCREEN'
    except Exception:
        pass
    try:
        ee.ray_tracing_options.resolution_scale = '1'
    except Exception:
        pass
    ee.use_shadows = True
    ee.shadow_pool_size = '512'
    try:
        ee.use_fast_gi = False
    except Exception:
        pass
    sc.view_settings.view_transform = 'Standard'
    try:
        sc.view_settings.look = 'None'
    except Exception:
        pass
    sc.render.film_transparent = False
    return sc


def world(col, strength):
    w = bpy.data.worlds.new('W')
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (*col, 1.0)
    bg.inputs[1].default_value = strength
    return w


def camera():
    cd = bpy.data.cameras.new('cam')
    cd.lens = LENS
    cd.sensor_width = SENSOR
    cd.sensor_fit = 'HORIZONTAL'
    cd.shift_x = CAM['shx']
    cd.shift_y = CAM['shy']
    cd.clip_start = 0.3
    cd.clip_end = 600
    ob = bpy.data.objects.new('cam', cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (0, 0, CAM['h'])
    ob.rotation_euler = (math.pi / 2, 0, 0)
    bpy.context.scene.camera = ob
    return ob


# ------------------------------------------------------------------ materials
BANDS_L = [0.0, 0.03, 0.10, 0.30, 0.72, 1.5]             # thresholds (light luminance)
LEVELS = [0.014, 0.055, 0.17, 0.45, 1.0, 1.9]          # representative light per band
KC = 0.6


def _f(L):
    return L / (L + KC)


EMIT = {}


def toon_material():
    m = bpy.data.materials.new('TOON')
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)

    def node(t, **kw):
        n = N.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def math_(op, a, b=None):
        n = node('ShaderNodeMath', operation=op)
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                L.new(x, n.inputs[i])
        return n.outputs[0]

    out = node('ShaderNodeOutputMaterial')
    acol = node('ShaderNodeAttribute', attribute_name='col')
    aemi = node('ShaderNodeAttribute', attribute_name='emit')
    awet = node('ShaderNodeAttribute', attribute_name='wet')
    dif = node('ShaderNodeBsdfDiffuse')
    dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = node('ShaderNodeShaderToRGB')
    L.new(dif.outputs[0], s2r.inputs[0])
    bw = node('ShaderNodeRGBToBW')
    L.new(s2r.outputs['Color'], bw.inputs[0])
    lum = bw.outputs[0]
    f = math_('DIVIDE', lum, math_('ADD', lum, KC))
    ramp = node('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    els = ramp.color_ramp.elements
    while len(els) < len(BANDS_L):
        els.new(0.5)
    for i, (t, lv) in enumerate(zip(BANDS_L, LEVELS)):
        els[i].position = _f(t)
        v = _f(lv)
        els[i].color = (v, v, v, 1)
    L.new(f, ramp.inputs[0])
    fq = ramp.outputs[0]
    sep = node('ShaderNodeSeparateColor')
    L.new(fq, sep.inputs[0])
    fqv = sep.outputs[0]
    lq = math_('MULTIPLY', math_('DIVIDE', fqv, math_('SUBTRACT', 1.0, fqv)), KC)
    ratio = math_('DIVIDE', lq, math_('MAXIMUM', lum, 0.0001))
    vs = node('ShaderNodeVectorMath', operation='SCALE')
    L.new(s2r.outputs['Color'], vs.inputs[0])
    L.new(ratio, vs.inputs['Scale'])
    vm = node('ShaderNodeVectorMath', operation='MULTIPLY')
    L.new(acol.outputs['Color'], vm.inputs[0])
    L.new(vs.outputs[0], vm.inputs[1])
    estr = node('ShaderNodeValue')
    estr.outputs[0].default_value = 1.0
    EMIT['node'] = estr
    ve = node('ShaderNodeVectorMath', operation='SCALE')
    L.new(aemi.outputs['Color'], ve.inputs[0])
    L.new(estr.outputs[0], ve.inputs['Scale'])
    va = node('ShaderNodeVectorMath', operation='ADD')
    L.new(vm.outputs[0], va.inputs[0])
    L.new(ve.outputs[0], va.inputs[1])
    em = node('ShaderNodeEmission')
    L.new(va.outputs[0], em.inputs['Color'])
    em.inputs['Strength'].default_value = 1.0
    # wet gloss layer
    wsep = node('ShaderNodeSeparateColor')
    L.new(awet.outputs['Color'], wsep.inputs[0])
    gl = node('ShaderNodeBsdfGlossy')
    comb = node('ShaderNodeCombineColor')
    for i in range(3):
        L.new(wsep.outputs[0], comb.inputs[i])
    L.new(comb.outputs[0], gl.inputs['Color'])
    L.new(wsep.outputs[1], gl.inputs['Roughness'])
    add = node('ShaderNodeAddShader')
    L.new(em.outputs[0], add.inputs[0])
    L.new(gl.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs['Surface'])
    return m


def sign_material(path, strength):
    m = bpy.data.materials.new('SIGN')
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new('ShaderNodeOutputMaterial')
    tex = N.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(path)
    tex.interpolation = 'Cubic'
    em = N.new('ShaderNodeEmission')
    L.new(tex.outputs['Color'], em.inputs['Color'])
    em.inputs['Strength'].default_value = strength
    tr = N.new('ShaderNodeBsdfTransparent')
    gt = N.new('ShaderNodeMath')
    gt.operation = 'GREATER_THAN'
    gt.inputs[1].default_value = 0.97
    L.new(tex.outputs['Alpha'], gt.inputs[0])
    mx = N.new('ShaderNodeMixShader')
    L.new(gt.outputs[0], mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs['Surface'])
    return m


def aux_material(kind):
    """Override material for aux renders: 'id' -> (pass_index, depth, 0); 'nrm' -> world normal."""
    m = bpy.data.materials.new('AUX_' + kind)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new('ShaderNodeOutputMaterial')
    em = N.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0
    if kind == 'id':
        oi = N.new('ShaderNodeObjectInfo')
        cam = N.new('ShaderNodeCameraData')
        comb = N.new('ShaderNodeCombineXYZ')
        L.new(oi.outputs['Object Index'], comb.inputs[0])
        L.new(cam.outputs['View Z Depth'], comb.inputs[1])
        L.new(comb.outputs[0], em.inputs['Color'])
    else:
        geo = N.new('ShaderNodeNewGeometry')
        ma = N.new('ShaderNodeVectorMath')
        ma.operation = 'MULTIPLY_ADD'
        ma.inputs[1].default_value = (0.5, 0.5, 0.5)
        ma.inputs[2].default_value = (0.5, 0.5, 0.5)
        L.new(geo.outputs['Normal'], ma.inputs[0])
        L.new(ma.outputs[0], em.inputs['Color'])
    L.new(em.outputs[0], out.inputs['Surface'])
    return m


# ------------------------------------------------------------------ geometry
OBJ = {'n': 0, 'kinds': {}}
TOON = {}


class Mesh:
    """Accumulates triangles with per-triangle col/emit/wet; one Mesh -> one object (one ink id)."""

    def __init__(self, name, kind='solid'):
        self.name = name
        self.kind = kind
        self.v = []
        self.f = []
        self.col = []
        self.emi = []
        self.wet = []

    def tri(self, a, b, c, col, emi=(0, 0, 0), wet=(0, 0.4)):
        i = len(self.v)
        self.v += [a, b, c]
        self.f.append((i, i + 1, i + 2))
        self.col.append(col)
        self.emi.append(emi)
        self.wet.append(wet)

    def grid(self, o, u, v, cell=0.7, colfn=None, col=(0.2, 0.2, 0.2), var=0.08, emi=(0, 0, 0), wet=(0, 0.4),
             jit=0.33, seed=0, emifn=None, wetfn=None):
        """Quad o + s*u + t*v (s,t in 0..1) as a jittered triangulated grid. u,v are vectors."""
        lu = math.sqrt(sum(c * c for c in u))
        lv = math.sqrt(sum(c * c for c in v))
        nu = max(1, int(round(lu / cell)))
        nv = max(1, int(round(lv / cell)))
        rng = random.Random(str((self.name, seed, o, nu, nv)))
        P = {}
        for i in range(nu + 1):
            for j in range(nv + 1):
                s, t = i / nu, j / nv
                if 0 < i < nu:
                    s += rng.uniform(-jit, jit) / nu
                if 0 < j < nv:
                    t += rng.uniform(-jit, jit) / nv
                P[i, j] = tuple(o[k] + u[k] * s + v[k] * t for k in range(3)) + (s, t)
        for i in range(nu):
            for j in range(nv):
                a, b, c, d = P[i, j], P[i + 1, j], P[i + 1, j + 1], P[i, j + 1]
                tris = [(a, b, c), (a, c, d)] if rng.random() < 0.5 else [(a, b, d), (b, c, d)]
                for tr in tris:
                    su = sum(p[3] for p in tr) / 3
                    tv = sum(p[4] for p in tr) / 3
                    if colfn:
                        cc = colfn(su, tv, rng)
                    else:
                        k = 1 + rng.uniform(-var, var)
                        cc = scl(col, k)
                    ee = emifn(su, tv, rng) if emifn else emi
                    ww = wetfn(su, tv, rng) if wetfn else wet
                    self.tri(tr[0][:3], tr[1][:3], tr[2][:3], cc, ee, ww)

    def box(self, x0, x1, y0, y1, z0, z1, faces='fblrt', **kw):
        """Axis box; faces: f(-y) b(+y) l(-x) r(+x) t(+z) d(-z)."""
        if 'f' in faces:
            self.grid((x0, y0, z0), (x1 - x0, 0, 0), (0, 0, z1 - z0), **dict(kw, seed=('f', kw.get('seed', 0))))
        if 'b' in faces:
            self.grid((x1, y1, z0), (x0 - x1, 0, 0), (0, 0, z1 - z0), **dict(kw, seed=('b', kw.get('seed', 0))))
        if 'l' in faces:
            self.grid((x0, y1, z0), (0, y0 - y1, 0), (0, 0, z1 - z0), **dict(kw, seed=('l', kw.get('seed', 0))))
        if 'r' in faces:
            self.grid((x1, y0, z0), (0, y1 - y0, 0), (0, 0, z1 - z0), **dict(kw, seed=('r', kw.get('seed', 0))))
        if 't' in faces:
            self.grid((x0, y0, z1), (x1 - x0, 0, 0), (0, y1 - y0, 0), **dict(kw, seed=('t', kw.get('seed', 0))))
        if 'd' in faces:
            self.grid((x0, y1, z0), (x1 - x0, 0, 0), (0, y0 - y1, 0), **dict(kw, seed=('d', kw.get('seed', 0))))

    def obox(self, c, ax, ay, az, **kw):
        """Oriented box: centre c, half-axis vectors ax, ay, az (all six faces)."""
        def P(sx, sy, sz):
            return tuple(c[k] + ax[k] * sx + ay[k] * sy + az[k] * sz for k in range(3))

        def V(a):
            return tuple(2 * x for x in a)
        kw = dict(kw)
        kw.setdefault('cell', 2.0)
        self.grid(P(-1, -1, -1), V(ax), V(az), **kw)                       # front (-ay)
        self.grid(P(1, 1, -1), tuple(-x for x in V(ax)), V(az), **kw)      # back
        self.grid(P(-1, 1, -1), tuple(-x for x in V(ay)), V(az), **kw)     # left
        self.grid(P(1, -1, -1), V(ay), V(az), **kw)                        # right
        self.grid(P(-1, -1, 1), V(ax), V(ay), **kw)                        # top
        self.grid(P(-1, 1, -1), V(ax), tuple(-x for x in V(ay)), **kw)     # bottom

    def build(self):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.update()
        n = len(self.f)
        for nm, arr in (('col', self.col), ('emit', self.emi), ('wet', [(w[0], w[1], 0) for w in self.wet])):
            at = me.color_attributes.new(nm, 'FLOAT_COLOR', 'CORNER')
            buf = np.repeat(np.array([(*c, 1.0) for c in arr], dtype=np.float32), 3, axis=0)
            at.data.foreach_set('color', buf.ravel())
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        me.materials.append(TOON['m'])
        if self.kind in ('city', 'citywin', 'noshadow'):
            ob.visible_shadow = False
        OBJ['n'] += 1
        ob.pass_index = OBJ['n']
        OBJ['kinds'][OBJ['n']] = (self.name, self.kind)
        return ob


def mesh_box(name, *a, kind='solid', **kw):
    m = Mesh(name, kind)
    m.box(*a, **kw)
    return m.build()


def sign_plane(path, rect, y, strength):
    """rect = (x0, z0, x1, z1) of the full sign image (incl. glow margin)."""
    x0, z0, x1, z1 = rect
    me = bpy.data.meshes.new('sign')
    me.from_pydata([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UVMap')
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    ob = bpy.data.objects.new('sign', me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(sign_material(path, strength))
    OBJ['n'] += 1
    ob.pass_index = OBJ['n']
    OBJ['kinds'][OBJ['n']] = ('sign', 'sign')
    return ob


# ------------------------------------------------------------------ lights
def light(kind, loc, col, energy, size=0.2, rot=(0, 0, 0), size_y=None, shadow=True, name='L'):
    ld = bpy.data.lights.new(name, kind)
    ld.color = col
    ld.energy = energy
    ld.use_shadow = shadow
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'
        ld.size = size
        ld.size_y = size_y if size_y else size
    elif kind == 'SUN':
        ld.angle = size
    else:
        ld.shadow_soft_size = size
    for attr, val in (('shadow_maximum_resolution', 0.02), ('shadow_resolution_scale', 0.5)):
        try:
            setattr(ld, attr, val)
        except Exception:
            pass
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def sun_dir_rot(d):
    """Rotation so a sun points along direction d (light travel)."""
    from mathutils import Vector
    v = Vector(d).normalized()
    return v.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ render
def _save_npy(exr, npy):
    img = bpy.data.images.load(exr)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    arr = buf.reshape(h, w, 4)[::-1, :, :3].copy()
    np.save(npy, arr.astype(np.float16) if arr.max() < 60000 else arr)
    bpy.data.images.remove(img)


def render_all(out_prefix, aux=True):
    sc = bpy.context.scene
    sc.render.image_settings.file_format = 'OPEN_EXR'
    sc.render.image_settings.color_depth = '32'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = out_prefix + '_beauty.exr'
    bpy.ops.render.render(write_still=True)
    _save_npy(out_prefix + '_beauty.exr', out_prefix + '_beauty.npy')
    if aux:
        samples = sc.eevee.taa_render_samples
        sc.eevee.taa_render_samples = 1
        sc.render.filter_size = 0.0
        sc.eevee.use_raytracing = False
        vl = bpy.context.view_layer
        bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
        bg.inputs[1].default_value = 0.0
        for kind in ('id', 'nrm'):
            vl.material_override = aux_material(kind)
            sc.render.filepath = out_prefix + '_%s.exr' % kind
            bpy.ops.render.render(write_still=True)
            _save_npy(out_prefix + '_%s.exr' % kind, out_prefix + '_%s.npy' % kind)
        vl.material_override = None
        sc.eevee.taa_render_samples = samples
    with open(out_prefix + '_ids.json', 'w') as fh:
        json.dump({str(k): v for k, v in OBJ['kinds'].items()}, fh)
