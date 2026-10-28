"""P1 Blender scene (headless): blender -b --factory-startup --python p1_bl.py -- spec.json
Builds the Godot raid camera, the city as a height-field HOLDOUT (exact occlusion from the Godot depth pass), the Tide layer
(ribbons, ICE towers, rings, blocks, fx) and renders float RGBA layers to .npy (premultiplied, linear):
  <out>_<pass>.npy   passes: world_occ (city holdout), world_ghost (no city), heads_occ, heads_ghost, spill (city lit by the emitters)
Blender coords = Godot (x, -z, y). Never touches a running Blender: this is a fresh headless process."""
import sys, os, json, math, time
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
SPEC = json.load(open(argv[0]))
OUT = SPEC['out']
RES = SPEC.get('res', [1920, 1080])
WORK = SPEC.get('work', 'D:/rc_scratch/tide_concepts/p2_work/')
T0 = time.time()


def log(*a):
    print('[p1 %.0fs]' % (time.time() - T0), *a, flush=True)


# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
if SPEC.get('border'):
    b = SPEC['border']
    scene.render.use_border = True
    scene.render.use_crop_to_border = False
    scene.render.border_min_x, scene.render.border_max_x = b[0] / RES[0], b[2] / RES[0]
    scene.render.border_min_y, scene.render.border_max_y = 1 - b[3] / RES[1], 1 - b[1] / RES[1]
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.display_settings.display_device = 'sRGB'
cy = scene.cycles
cy.samples = SPEC.get('samples', 64)
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.use_denoising = True
cy.denoiser = 'OPENIMAGEDENOISE'
cy.max_bounces = 4
cy.diffuse_bounces = 2
cy.glossy_bounces = 2
cy.transmission_bounces = 8
cy.transparent_max_bounces = 16
cy.sample_clamp_indirect = 12.0
cy.film_exposure = 1.0
if SPEC.get('device', 'GPU') == 'GPU':
    cy.device = 'GPU'
    pref = bpy.context.preferences.addons['cycles'].preferences
    pref.compute_device_type = 'HIP'
    pref.get_devices()
    for d in pref.devices:
        d.use = (d.type == 'HIP')
    print('DEVICES', [(d.name, d.type, d.use) for d in pref.devices], flush=True)
    try:
        cy.denoising_use_gpu = True
    except Exception:
        pass
else:
    cy.device = 'CPU'
world = bpy.data.worlds.new('w')
scene.world = world
world.use_nodes = True
bgn = world.node_tree.nodes['Background']
bgn.inputs[0].default_value = (0, 0, 0, 1)
bgn.inputs[1].default_value = 0.0

# camera (orthographic, Godot raid camera mapped to Blender axes)
cam_d = bpy.data.cameras.new('cam')
cam_d.type = 'ORTHO'
cam_d.ortho_scale = SPEC['cam']['size']
cam_d.clip_start = 1.0
cam_d.clip_end = 6000.0
cam_d.sensor_fit = 'HORIZONTAL'
cam = bpy.data.objects.new('cam', cam_d)
scene.collection.objects.link(cam)
scene.camera = cam


def g2b(v):
    return Vector((v[0], -v[2], v[1]))


R_, U_, B_ = [g2b(SPEC['cam'][k]) for k in ('right', 'up', 'back')]
M = Matrix([[R_.x, U_.x, B_.x, 0], [R_.y, U_.y, B_.y, 0], [R_.z, U_.z, B_.z, 0], [0, 0, 0, 1]])
M.translation = g2b(SPEC['cam']['pos'])
cam.matrix_world = M

collections = {}


def coll(name):
    if name not in collections:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
        collections[name] = c
    return collections[name]


def link(obj, cname):
    coll(cname).objects.link(obj)
    obj['p1grp'] = cname


# ------------------------------------------------------------------ materials
def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


def emission_mat(name, color, strength, alpha=1.0, double=False):
    m, nt = new_mat(name)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = strength
    if alpha >= 0.999:
        nt.links.new(em.outputs[0], out.inputs[0])
    else:
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        mx = nt.nodes.new('ShaderNodeMixShader')
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def tex_emission_mat(name, imgpath, strength, alpha=1.0, flip=False):
    m, nt = new_mat(name)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tx = nt.nodes.new('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(imgpath)
    tx.image.alpha_mode = 'STRAIGHT'
    tx.extension = 'REPEAT'
    tx.interpolation = 'Cubic'
    uv = nt.nodes.new('ShaderNodeUVMap')
    nt.links.new(uv.outputs[0], tx.inputs[0])
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs[1].default_value = strength
    nt.links.new(tx.outputs[0], em.inputs[0])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    am = nt.nodes.new('ShaderNodeMath')
    am.operation = 'MULTIPLY'
    am.inputs[1].default_value = alpha
    nt.links.new(tx.outputs[1], am.inputs[0])
    nt.links.new(am.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def srgb_to_lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def hexlin(h):
    h = h.lstrip('#')
    return tuple(srgb_to_lin(np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])))


# ------------------------------------------------------------------ city height-field (holdout / diffuse)
def build_city():
    z = np.load(SPEC['hf'])
    Hh = z['H'].astype(np.float64); G = z['G'].astype(np.float64)
    x0, z0, c = float(z['x0']), float(z['z0']), float(z['cell'])
    nz, nx = Hh.shape
    # cells that sit on the street/terrain keep the terrain exactly (the ribbons lie on it)
    Hh = np.where(np.abs(Hh - G) < SPEC.get('snap', 0.7), G, Hh)
    gx = x0 + np.arange(nx) * c
    gz = z0 + np.arange(nz) * c
    GX, GZ = np.meshgrid(gx, gz)
    cm = SPEC['cam']
    O = np.array(cm['pos']); Rr = np.array(cm['right']); Uu = np.array(cm['up']); size = cm['size']
    pts = np.stack([GX, Hh, GZ], -1)
    d = pts - O
    sx = (d @ Rr) / size + 0.5
    sy = 0.5 - (d @ Uu) / (size * RES[1] / RES[0])
    inside = (sx > -0.04) & (sx < 1.04) & (sy > -0.06) & (sy < 1.06)
    g_pts = np.stack([GX, G, GZ], -1)
    dg = g_pts - O
    sxg = (dg @ Rr) / size + 0.5
    syg = 0.5 - (dg @ Uu) / (size * RES[1] / RES[0])
    inside |= (sxg > -0.04) & (sxg < 1.04) & (syg > -0.06) & (syg < 1.06)
    # a cell is kept if any of its 4 corners is inside
    keep = inside[:-1, :-1] | inside[1:, :-1] | inside[:-1, 1:] | inside[1:, 1:]
    # also keep a band of cells whose column lies between the camera and any kept cell (nothing: ortho, same footprint)
    vid = -np.ones((nz, nx), np.int64)
    need = np.zeros((nz, nx), bool)
    need[:-1, :-1] |= keep; need[1:, :-1] |= keep; need[:-1, 1:] |= keep; need[1:, 1:] |= keep
    vid[need] = np.arange(need.sum())
    verts = np.stack([GX[need], -GZ[need], Hh[need]], -1).astype(np.float32)
    cz, cx = np.nonzero(keep)
    f = np.stack([vid[cz, cx], vid[cz, cx + 1], vid[cz + 1, cx + 1], vid[cz + 1, cx]], -1)
    log('city mesh verts', len(verts), 'quads', len(f))
    me = bpy.data.meshes.new('city')
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel())
    me.loops.add(len(f) * 4)
    me.loops.foreach_set('vertex_index', f.ravel())
    me.polygons.add(len(f))
    me.polygons.foreach_set('loop_start', np.arange(len(f)) * 4)
    me.update(calc_edges=True)
    # UV = normalised Godot (x, z) over the grid (the Bloom field image uses the same mapping); 'rel' = height above terrain
    gxv = GX[need]; gzv = GZ[need]
    uvv = np.stack([(gxv - x0) / (nx * c), 1.0 - (gzv - z0) / (nz * c)], -1).astype(np.float32)
    uvl = me.uv_layers.new(name='UVMap')
    uvl.data.foreach_set('uv', uvv[f.ravel()].ravel())
    rel = (Hh - G)[need].astype(np.float32)
    at = me.attributes.new('rel', 'FLOAT', 'POINT')
    at.data.foreach_set('value', rel)
    me['grid'] = [x0, z0, c, nx, nz]
    ob = bpy.data.objects.new('city', me)
    link(ob, 'city')
    return ob


city = build_city()
mat_hold, nt = new_mat('hold')
o = nt.nodes.new('ShaderNodeOutputMaterial')
h = nt.nodes.new('ShaderNodeHoldout')
nt.links.new(h.outputs[0], o.inputs[0])

# diffuse albedo from the beauty plate via camera-window projection
mat_diff, nt = new_mat('cityalb')
o = nt.nodes.new('ShaderNodeOutputMaterial')
tc = nt.nodes.new('ShaderNodeTexCoord')
tx = nt.nodes.new('ShaderNodeTexImage')
tx.image = bpy.data.images.load(SPEC['beauty'])
tx.image.colorspace_settings.name = 'sRGB'
tx.interpolation = 'Linear'
tx.extension = 'EXTEND'
nt.links.new(tc.outputs['Window'], tx.inputs[0])
mulc = nt.nodes.new('ShaderNodeMix')
mulc.data_type = 'RGBA'
mulc.blend_type = 'MULTIPLY'
mulc.inputs[0].default_value = 1.0
nt.links.new(tx.outputs[0], mulc.inputs[6])
mulc.inputs[7].default_value = (SPEC.get('albedo_gain', 1.8),) * 3 + (1,)
bs = nt.nodes.new('ShaderNodeBsdfDiffuse')
nt.links.new(mulc.outputs[2], bs.inputs[0])
nt.links.new(bs.outputs[0], o.inputs[0])
city.data.materials.append(mat_hold)



# ================================================================== builders (v2)
def rng_for(s):
    return np.random.RandomState(abs(hash(s)) % (2 ** 31))


def mesh_obj(name, verts, faces, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return bpy.data.objects.new(name, me)


def strip_mesh(name, pts, w, h, s0=0.0, s1=None, lenbu=16.0, step=1.2):
    """ribbon along a Blender-space polyline: raised flat-top strip with bevelled sides; UV u = arclength / lenbu, v across."""
    P = np.asarray(pts, float)
    seg = np.hypot(*np.diff(P[:, :2], axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    L = cum[-1]
    s1 = L if s1 is None else min(s1, L)
    ss = np.unique(np.concatenate([np.arange(s0, s1, step), [s1]]))
    if len(ss) < 2:
        return None
    X = np.interp(ss, cum, P[:, 0]); Y = np.interp(ss, cum, P[:, 1]); Z = np.interp(ss, cum, P[:, 2])
    pos = np.stack([X, Y, Z], -1)
    tan = np.gradient(pos[:, :2], axis=0)
    tan = tan / np.maximum(np.hypot(tan[:, 0], tan[:, 1])[:, None], 1e-6)
    nrm = np.stack([-tan[:, 1], tan[:, 0]], -1)
    prof = [(-1.0, 0.0), (-0.92, 0.7), (-0.78, 1.0), (0.78, 1.0), (0.92, 0.7), (1.0, 0.0)]
    vs, uvs = [], []
    for i in range(len(ss)):
        for (o_, hf) in prof:
            vs.append((pos[i, 0] + nrm[i, 0] * o_ * w / 2, pos[i, 1] + nrm[i, 1] * o_ * w / 2, pos[i, 2] + hf * h))
            uvs.append((ss[i] / lenbu, (o_ + 1) / 2))
    k = len(prof)
    faces = [(i * k + j, i * k + j + 1, i * k + j + 1 + k, i * k + j + k) for i in range(len(ss) - 1) for j in range(k - 1)]
    ob = mesh_obj(name, vs, faces)
    uv = ob.data.uv_layers.new(name='UVMap')
    uva = np.array(uvs, np.float32)
    li = np.array([l.vertex_index for l in ob.data.loops])
    uv.data.foreach_set('uv', uva[li].ravel())
    return ob, L


def quad_mesh(name, c, ax_u, ax_v, wu, wv):
    """a quad centred on c spanned by unit axes ax_u (len wu) and ax_v (len wv); UV 0..1."""
    c = np.array(c, float); u = np.array(ax_u, float) * wu / 2; v = np.array(ax_v, float) * wv / 2
    vs = [c - u - v, c + u - v, c + u + v, c - u + v]
    ob = mesh_obj(name, vs, [(0, 1, 2, 3)])
    uv = ob.data.uv_layers.new(name='UVMap')
    for i, l in enumerate(ob.data.loops):
        uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][l.vertex_index]
    return ob


def tower_mesh(name, c, tier, a, h, state='healthy'):
    """T1 prism with a chamfered crown, T2 obelisk (prism + pyramid cap), T3 stepped spire. Smooth normals give a glass fresnel gradient."""
    parts = []

    def prism(z0, z1, a0, a1):
        vs = []
        for z, aa in ((z0, a0), (z1, a1)):
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                vs.append((sx * aa, sy * aa, z))
        return vs, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    vs, fs = [], []

    def add(v, f):
        n = len(vs)
        vs.extend(v)
        fs.extend([tuple(i + n for i in q) for q in f])
    if tier == 1:
        add(*prism(0, h * 0.9, a, a))
        add(*prism(h * 0.9, h, a, a * 0.62))
    elif tier == 2:
        add(*prism(0, h * 0.78, a, a * 0.92))
        n = len(vs)
        base = [(sx * a * 0.92, sy * a * 0.92, h * 0.78) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        vs.extend(base + [(0, 0, h)])
        fs.extend([(n, n + 1, n + 4), (n + 1, n + 2, n + 4), (n + 2, n + 3, n + 4), (n + 3, n, n + 4)])
    else:
        add(*prism(0, h * 0.55, a, a * 0.9))
        add(*prism(h * 0.55, h * 0.86, a * 0.62, a * 0.5))
        n = len(vs)
        base = [(sx * a * 0.5, sy * a * 0.5, h * 0.86) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        vs.extend(base + [(0, 0, h * 1.12)])
        fs.extend([(n, n + 1, n + 4), (n + 1, n + 2, n + 4), (n + 2, n + 3, n + 4), (n + 3, n, n + 4)])
    if state == 'down':
        # the upper volume tore away: keep the base 55 % and a few detached slices
        keep = []
        vs2, fs2 = [], []
        add2 = lambda v, f: (fs2.extend([tuple(i + len(vs2) for i in q) for q in f]), vs2.extend(v))
        add2(*prism(0, h * 0.5, a, a))
        for i, zz in enumerate((0.56, 0.64, 0.75)):
            r = rng_for(name + str(i))
            sh = (r.uniform(-1.2, 1.2), r.uniform(-1.2, 1.2))
            v, f = prism(h * zz, h * zz + 0.5, a * 0.95, a * 0.95)
            v = [(x + sh[0], y + sh[1], z) for x, y, z in v]
            add2(v, f)
        vs, fs = vs2, fs2
    ob = mesh_obj(name, vs, fs, smooth=True)
    ob.location = c
    return ob


def holo_mat(name, col, strength=3.0, edge=6.0, fres=1.0, scan=0.5, fill=0.04, wire=0.12, fade=0.4, h=40.0, pulse=0.0):
    """ICE hologram: faint body + fresnel rim + thin wire edges + world-Z data scanlines, transparent elsewhere."""
    m, nt = new_mat(name)
    N = nt.nodes
    o = N.new('ShaderNodeOutputMaterial')
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.5
    wf = N.new('ShaderNodeWireframe'); wf.inputs[0].default_value = wire
    gp = N.new('ShaderNodeNewGeometry')
    sp = N.new('ShaderNodeSeparateXYZ'); nt.links.new(gp.outputs['Position'], sp.inputs[0])
    pp = N.new('ShaderNodeMath'); pp.operation = 'PINGPONG'; pp.inputs[1].default_value = 1.7
    nt.links.new(sp.outputs[2], pp.inputs[0])
    lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.07
    nt.links.new(pp.outputs[0], lt.inputs[0])
    tcn = N.new('ShaderNodeTexCoord')
    so = N.new('ShaderNodeSeparateXYZ'); nt.links.new(tcn.outputs['Object'], so.inputs[0])
    fd = N.new('ShaderNodeMath'); fd.operation = 'MULTIPLY_ADD'; fd.inputs[1].default_value = -fade / max(h, 1.0); fd.inputs[2].default_value = 1.0
    nt.links.new(so.outputs[2], fd.inputs[0])
    fdc = N.new('ShaderNodeMath'); fdc.operation = 'MAXIMUM'; fdc.inputs[1].default_value = 0.2
    nt.links.new(fd.outputs[0], fdc.inputs[0])

    def ma(a_out, mul, add_node=None, add_val=0.0):
        n = N.new('ShaderNodeMath'); n.operation = 'MULTIPLY_ADD'
        nt.links.new(a_out, n.inputs[0]); n.inputs[1].default_value = mul
        if add_node is not None:
            nt.links.new(add_node, n.inputs[2])
        else:
            n.inputs[2].default_value = add_val
        return n.outputs[0]
    i1 = ma(lw.outputs['Fresnel'], fres, None, fill)
    i2 = ma(wf.outputs[0], edge, i1)
    i3 = ma(lt.outputs[0], scan, i2)
    I = N.new('ShaderNodeMath'); I.operation = 'MULTIPLY'
    nt.links.new(i3, I.inputs[0]); nt.links.new(fdc.outputs[0], I.inputs[1])
    em = N.new('ShaderNodeEmission'); em.inputs[0].default_value = (*col, 1)
    sc = N.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = strength
    nt.links.new(I.outputs[0], sc.inputs[0]); nt.links.new(sc.outputs[0], em.inputs[1])
    cl = N.new('ShaderNodeMath'); cl.operation = 'MINIMUM'; cl.inputs[1].default_value = 0.95
    nt.links.new(I.outputs[0], cl.inputs[0])
    tr = N.new('ShaderNodeBsdfTransparent')
    mx = N.new('ShaderNodeMixShader')
    nt.links.new(cl.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    return m


def ink_mat(name):
    m, nt = new_mat(name)
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = (0.004, 0.003, 0.012, 1); e.inputs[1].default_value = 1.0
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def radial_mat(name, col, strength, power=2.0, inner=0.0):
    """flat glow disc: emission fades radially (UV 0..1 centred); alpha = (1-r)^power."""
    m, nt = new_mat(name)
    N = nt.nodes
    o = N.new('ShaderNodeOutputMaterial')
    uv = N.new('ShaderNodeUVMap')
    sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0)
    nt.links.new(uv.outputs[0], sub.inputs[0])
    ln = N.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    nt.links.new(sub.outputs[0], ln.inputs[0])
    r2 = N.new('ShaderNodeMath'); r2.operation = 'MULTIPLY'; r2.inputs[1].default_value = 2.0
    nt.links.new(ln.outputs['Value'], r2.inputs[0])
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(r2.outputs[0], inv.inputs[1])
    cl = N.new('ShaderNodeMath'); cl.operation = 'MAXIMUM'; cl.inputs[1].default_value = 0.0
    nt.links.new(inv.outputs[0], cl.inputs[0])
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    nt.links.new(cl.outputs[0], pw.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs[0].default_value = (*col, 1)
    sc = N.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = strength
    nt.links.new(pw.outputs[0], sc.inputs[0]); nt.links.new(sc.outputs[0], em.inputs[1])
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
    nt.links.new(pw.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    return m


def fog_mat(name, col, strength, seed=1.0, thr=0.30):
    """sealed-route mist: noise-gated emission, lavender speckle + soft body, edges feather by UV v."""
    m, nt = new_mat(name)
    N = nt.nodes
    o = N.new('ShaderNodeOutputMaterial')
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 0.55; nz.inputs['Detail'].default_value = 5.0; nz.inputs['W'].default_value = seed
    nt.links.new(tc.outputs['Generated'] if False else tc.outputs['Object'], nz.inputs['Vector'])
    uv = N.new('ShaderNodeUVMap')
    sp = N.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs[0], sp.inputs[0])
    ed = N.new('ShaderNodeMath'); ed.operation = 'PINGPONG'; ed.inputs[1].default_value = 0.5
    nt.links.new(sp.outputs[1], ed.inputs[0])
    ed2 = N.new('ShaderNodeMath'); ed2.operation = 'MULTIPLY'; ed2.inputs[1].default_value = 2.0
    nt.links.new(ed.outputs[0], ed2.inputs[0])
    prod = N.new('ShaderNodeMath'); prod.operation = 'MULTIPLY'
    nt.links.new(nz.outputs['Fac'], prod.inputs[0]); nt.links.new(ed2.outputs[0], prod.inputs[1])
    ramp = N.new('ShaderNodeMapRange'); ramp.inputs[1].default_value = thr * 0.5; ramp.inputs[2].default_value = thr + 0.25
    nt.links.new(prod.outputs[0], ramp.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs[0].default_value = (*col, 1)
    sc = N.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = strength
    nt.links.new(ramp.outputs[0], sc.inputs[0]); nt.links.new(sc.outputs[0], em.inputs[1])
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
    nt.links.new(ramp.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    try:
        m.cycles.emission_sampling = 'NONE'
    except Exception as e:
        print('emission_sampling', e)
    return m


def bloom_mat(name, fieldpath, strength, hair_strength):
    """Bloom necrosis overlay on the city shell: plum body (voronoi veins) that climbs the facades, hot hairline at the front.
    field image (UV = grid): R = front value (1 inside .. 0 outside, front at 0.5), G = climb height / 64 BU, B = unused."""
    m, nt = new_mat(name)
    N = nt.nodes
    o = N.new('ShaderNodeOutputMaterial')
    uv = N.new('ShaderNodeUVMap')
    tx = N.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(fieldpath); tx.image.colorspace_settings.name = 'Non-Color'
    tx.interpolation = 'Linear'; tx.extension = 'EXTEND'
    nt.links.new(uv.outputs[0], tx.inputs[0])
    sep = N.new('ShaderNodeSeparateColor'); nt.links.new(tx.outputs[0], sep.inputs[0])
    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'rel'; at.attribute_type = 'GEOMETRY'
    # facade rule: infected where rel < climb*64 (+ soft)
    cl = N.new('ShaderNodeMath'); cl.operation = 'MULTIPLY'; cl.inputs[1].default_value = 64.0
    nt.links.new(sep.outputs[1], cl.inputs[0])
    dh = N.new('ShaderNodeMath'); dh.operation = 'SUBTRACT'
    nt.links.new(cl.outputs[0], dh.inputs[0]); nt.links.new(at.outputs['Fac'], dh.inputs[1])
    hm = N.new('ShaderNodeMapRange'); hm.inputs[1].default_value = -1.0; hm.inputs[2].default_value = 1.5
    nt.links.new(dh.outputs[0], hm.inputs[0])
    fm = N.new('ShaderNodeMapRange'); fm.inputs[1].default_value = 0.47; fm.inputs[2].default_value = 0.52
    nt.links.new(sep.outputs[0], fm.inputs[0])
    body = N.new('ShaderNodeMath'); body.operation = 'MULTIPLY'
    nt.links.new(fm.outputs[0], body.inputs[0]); nt.links.new(hm.outputs[0], body.inputs[1])
    # hairline: band around front value 0.5 (on ground) and the climb edge
    hb = N.new('ShaderNodeMath'); hb.operation = 'SUBTRACT'; hb.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs[0], hb.inputs[0])
    ha = N.new('ShaderNodeMath'); ha.operation = 'ABSOLUTE'
    nt.links.new(hb.outputs[0], ha.inputs[0])
    hl = N.new('ShaderNodeMapRange'); hl.inputs[1].default_value = 0.035; hl.inputs[2].default_value = 0.0
    nt.links.new(ha.outputs[0], hl.inputs[0])
    hl_in = N.new('ShaderNodeMath'); hl_in.operation = 'MULTIPLY'
    nt.links.new(hl.outputs[0], hl_in.inputs[0]); nt.links.new(hm.outputs[0], hl_in.inputs[1])
    # climb hairline along facades
    cb = N.new('ShaderNodeMath'); cb.operation = 'ABSOLUTE'
    nt.links.new(dh.outputs[0], cb.inputs[0])
    cm = N.new('ShaderNodeMapRange'); cm.inputs[1].default_value = 0.9; cm.inputs[2].default_value = 0.0
    nt.links.new(cb.outputs[0], cm.inputs[0])
    cm2 = N.new('ShaderNodeMath'); cm2.operation = 'MULTIPLY'
    nt.links.new(cm.outputs[0], cm2.inputs[0]); nt.links.new(fm.outputs[0], cm2.inputs[1])
    hair = N.new('ShaderNodeMath'); hair.operation = 'MAXIMUM'
    nt.links.new(hl_in.outputs[0], hair.inputs[0]); nt.links.new(cm2.outputs[0], hair.inputs[1])
    # veins: voronoi edge distance in world space
    tcn = N.new('ShaderNodeTexCoord')
    vr = N.new('ShaderNodeTexVoronoi'); vr.feature = 'DISTANCE_TO_EDGE'; vr.inputs['Scale'].default_value = 0.4
    nt.links.new(tcn.outputs['Object'], vr.inputs['Vector'])
    vm = N.new('ShaderNodeMapRange'); vm.inputs[1].default_value = 0.032; vm.inputs[2].default_value = 0.0
    nt.links.new(vr.outputs['Distance'], vm.inputs[0])
    # colours
    plum = N.new('ShaderNodeRGB'); plum.outputs[0].default_value = (*hexlin('2E1032'), 1)
    vein = N.new('ShaderNodeRGB'); vein.outputs[0].default_value = (*hexlin('8A2C86'), 1)
    hot = N.new('ShaderNodeRGB'); hot.outputs[0].default_value = (*hexlin('E8B8E0'), 1)
    mixv = N.new('ShaderNodeMix'); mixv.data_type = 'RGBA'
    nt.links.new(vm.outputs[0], mixv.inputs[0]); nt.links.new(plum.outputs[0], mixv.inputs[6]); nt.links.new(vein.outputs[0], mixv.inputs[7])
    emv = N.new('ShaderNodeEmission')
    nt.links.new(mixv.outputs[2], emv.inputs[0])
    vs_ = N.new('ShaderNodeMath'); vs_.operation = 'MULTIPLY_ADD'; vs_.inputs[1].default_value = strength; vs_.inputs[2].default_value = strength * 0.08
    nt.links.new(vm.outputs[0], vs_.inputs[0]); nt.links.new(vs_.outputs[0], emv.inputs[1])
    emh = N.new('ShaderNodeEmission'); nt.links.new(hot.outputs[0], emh.inputs[0]); emh.inputs[1].default_value = hair_strength
    mixh = N.new('ShaderNodeMixShader')
    hcl = N.new('ShaderNodeMath'); hcl.operation = 'MINIMUM'; hcl.inputs[1].default_value = 1.0
    nt.links.new(hair.outputs[0], hcl.inputs[0])
    nt.links.new(hcl.outputs[0], mixh.inputs[0]); nt.links.new(emv.outputs[0], mixh.inputs[1]); nt.links.new(emh.outputs[0], mixh.inputs[2])
    tr = N.new('ShaderNodeBsdfTransparent'); mxa = N.new('ShaderNodeMixShader')
    al = N.new('ShaderNodeMath'); al.operation = 'MAXIMUM'
    nt.links.new(body.outputs[0], al.inputs[0]); nt.links.new(hair.outputs[0], al.inputs[1])
    alc = N.new('ShaderNodeMath'); alc.operation = 'MINIMUM'; alc.inputs[1].default_value = 0.96
    nt.links.new(al.outputs[0], alc.inputs[0])
    nt.links.new(alc.outputs[0], mxa.inputs[0]); nt.links.new(tr.outputs[0], mxa.inputs[1]); nt.links.new(mixh.outputs[0], mxa.inputs[2])
    nt.links.new(mxa.outputs[0], o.inputs[0])
    try:
        m.cycles.emission_sampling = 'NONE'
    except Exception as e:
        print('emission_sampling', e)
    return m


def cyl_mesh(name, c, r, h, nseg=32, nring=12, r_top=None):
    r_top = r if r_top is None else r_top
    vs, fs = [], []
    for j in range(nring + 1):
        t = j / nring
        rr = r + (r_top - r) * t
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            vs.append((math.cos(a) * rr, math.sin(a) * rr, t * h))
    for j in range(nring):
        for i in range(nseg):
            a = j * nseg + i; b = j * nseg + (i + 1) % nseg
            fs.append((a, b, b + nseg, a + nseg))
    ob = mesh_obj(name, vs, fs, smooth=True)
    ob.location = c
    return ob


def dome_mesh(name, c, r, nseg=24, nring=10):
    vs, fs = [], []
    for j in range(nring + 1):
        phi = (math.pi / 2) * j / nring
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            vs.append((math.cos(a) * r * math.cos(phi), math.sin(a) * r * math.cos(phi), r * math.sin(phi) * 1.15))
    for j in range(nring):
        for i in range(nseg):
            a = j * nseg + i; b = j * nseg + (i + 1) % nseg
            fs.append((a, b, b + nseg, a + nseg))
    ob = mesh_obj(name, vs, fs, smooth=True)
    ob.location = c
    return ob


def ring_mesh(name, c, r_out, r_in, z=0.3, seg=96, arc=None, h=0.0):
    a0, a1 = (0, 2 * math.pi) if arc is None else arc
    full = arc is None
    n = seg if full else seg + 1
    vs, fs = [], []
    for i in range(n):
        a = a0 + (a1 - a0) * i / seg
        for rr in (r_out, r_in):
            vs.append((math.cos(a) * rr, math.sin(a) * rr, z))
    for i in range(seg if full else seg):
        j = (i + 1) % n
        fs.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    ob = mesh_obj(name, vs, fs)
    ob.location = c
    return ob


def poly_prism(name, poly, thick, scale, pos, dirv, z0=0.0, tilt=0.0, roll=0.0):
    """extruded 2D polygon (unit radius, x = travel dir) -> mesh at pos facing dirv (Blender XY)."""
    d = np.array(dirv[:2], float); d = d / max(np.hypot(*d), 1e-6)
    n = np.array([-d[1], d[0]])
    pts = [np.array([pos[0], pos[1]]) + (d * x + n * y) * scale for x, y in poly]
    k = len(pts)
    vs = [(p[0], p[1], pos[2] + z0) for p in pts] + [(p[0], p[1], pos[2] + z0 + thick) for p in pts]
    if tilt or roll:
        c0 = np.array([pos[0], pos[1], pos[2] + z0 + thick / 2])
        ax_n = np.array([n[0], n[1], 0.0]); ax_d = np.array([d[0], d[1], 0.0])
        def rot(v, ax, ang):
            v = np.array(v) - c0
            v = v * math.cos(ang) + np.cross(ax, v) * math.sin(ang) + ax * np.dot(ax, v) * (1 - math.cos(ang))
            return tuple(v + c0)
        vs = [rot(rot(v, ax_n, tilt), ax_d, roll) for v in vs]
    fs = [tuple(range(k - 1, -1, -1)), tuple(range(k, 2 * k))]
    for i in range(k):
        j = (i + 1) % k
        fs.append((i, j, k + j, k + i))
    return mesh_obj(name, vs, fs)


def lights_spec(ls):
    for l in ls:
        ld = bpy.data.lights.new('l', 'POINT')
        ld.energy = l['power']
        ld.color = hexlin(l['col'])
        ld.shadow_soft_size = l.get('size', 2.0)
        lo = bpy.data.objects.new('l', ld)
        lo.location = l['pos']
        link(lo, 'lights')


def wire_obj(name, segs, r):
    """square-section tubes for a list of (p0, p1) segments (Blender coords) - real 3D wire that lights its surroundings."""
    vs, fs = [], []
    for p0, p1 in segs:
        p0 = np.array(p0, float); p1 = np.array(p1, float)
        d = p1 - p0
        L_ = np.linalg.norm(d)
        if L_ < 1e-6:
            continue
        d = d / L_
        a = np.cross(d, (0, 0, 1.0))
        if np.linalg.norm(a) < 1e-3:
            a = np.cross(d, (1.0, 0, 0))
        a = a / np.linalg.norm(a) * r
        b = np.cross(d, a / r) * r
        n = len(vs)
        for p in (p0, p1):
            vs.extend([tuple(p + a + b), tuple(p - a + b), tuple(p - a - b), tuple(p + a - b)])
        for i in range(4):
            j = (i + 1) % 4
            fs.append((n + i, n + j, n + 4 + j, n + 4 + i))
    return mesh_obj(name, vs, fs)


def tower_segs(c, tier, a, h, rung=3.4, state='healthy'):
    c = np.array(c, float)
    segs = []

    def loop(z, aa):
        pts = [(-aa, -aa), (aa, -aa), (aa, aa), (-aa, aa)]
        for i in range(4):
            x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % 4]
            segs.append((c + (x0, y0, z), c + (x1, y1, z)))

    def vedges(z0, z1, a0, a1):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            segs.append((c + (sx * a0, sy * a0, z0), c + (sx * a1, sy * a1, z1)))

    def stack(z0, z1, a0, a1):
        vedges(z0, z1, a0, a1)
        n = max(1, int((z1 - z0) / rung))
        for i in range(n + 1):
            t = i / n
            loop(z0 + (z1 - z0) * t, a0 + (a1 - a0) * t)

    def apex(z0, a0, zt):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            segs.append((c + (sx * a0, sy * a0, z0), c + (0, 0, zt)))
    if state == 'down':
        stack(0, h * 0.5, a, a)
        return segs
    if tier == 1:
        stack(0, h * 0.9, a, a); stack(h * 0.9, h, a, a * 0.62)
    elif tier == 2:
        stack(0, h * 0.78, a, a * 0.92); apex(h * 0.78, a * 0.92, h)
    else:
        stack(0, h * 0.55, a, a * 0.9); stack(h * 0.55, h * 0.86, a * 0.62, a * 0.5); apex(h * 0.86, a * 0.5, h * 1.12)
    return segs


def cage_segs(c, r, h, r_top, nrib=24, nring=14, nseg=48):
    c = np.array(c, float)
    segs = []
    for i in range(nrib):
        a = 2 * math.pi * i / nrib
        segs.append((c + (math.cos(a) * r, math.sin(a) * r, 0), c + (math.cos(a) * r_top, math.sin(a) * r_top, h)))
    for j in range(nring + 1):
        t = j / nring
        rr = r + (r_top - r) * t
        for i in range(nseg):
            a0 = 2 * math.pi * i / nseg; a1 = 2 * math.pi * (i + 1) / nseg
            segs.append((c + (math.cos(a0) * rr, math.sin(a0) * rr, t * h), c + (math.cos(a1) * rr, math.sin(a1) * rr, t * h)))
    return segs


# ================================================================== populate from spec
def add(ob, grp, mat):
    if mat is not None:
        ob.data.materials.append(mat)
    link(ob, grp)
    return ob


for r in SPEC.get('ribbons', []):
    res = strip_mesh('rib_' + r['id'], r['pts'], r['w'], r.get('h', 0.5), r.get('s0', 0.0), r.get('s1'), lenbu=r['lenbu'])
    if res is None:
        continue
    ob, L = res
    if r.get('kind') == 'fog':
        mat = fog_mat('fogm_' + r['id'], hexlin(r.get('col', '9C8CFF')), r.get('strength', 3.0), seed=r.get('seed', 1.0))
    else:
        mat = tex_emission_mat('ribm_' + r['id'], r['tex'], r.get('strength', 4.0), r.get('alpha', 1.0))
    add(ob, r.get('grp', 'world'), mat)
    ob.visible_shadow = False

for t in SPEC.get('towers', []):
    ob = tower_mesh('tower_' + t['id'], t['pos'], t['tier'], t['a'], t['h'], t.get('state', 'healthy'))
    mat = holo_mat('towm_' + t['id'], hexlin(t.get('col', '7C88AE')), strength=t.get('strength', 3.0), edge=0.0, fres=t.get('fres', 0.30),
                   scan=t.get('scan', 0.5), fill=t.get('fill', 0.012), wire=0.1, fade=t.get('fade', 0.35), h=t['h'])
    add(ob, 'world', mat)
    ob.visible_shadow = False
    if t.get('wire', True):
      wo = wire_obj('tw_' + t['id'], tower_segs(t['pos'], t['tier'], t['a'], t['h'], state=t.get('state', 'healthy')), t.get('wire_r', 0.16))
      add(wo, 'world', emission_mat('twm_' + t['id'], hexlin(t.get('col', '7C88AE')), t.get('wire_strength', 9.0) * t.get('strength', 3.0) / 3.0))
      wo.visible_shadow = False
    if t.get('spine', True):
        sp_ = cyl_mesh('spine_' + t['id'], (t['pos'][0], t['pos'][1], t['pos'][2]), 0.28, t['h'] * (0.5 if t.get('state') == 'down' else 0.96), nseg=8, nring=1)
        add(sp_, 'world', emission_mat('spm_' + t['id'], hexlin(t.get('col', '7C88AE')), t.get('spine_strength', 8.0)))
    if t.get('pad', True):
        pd = quad_mesh('pad_' + t['id'], (t['pos'][0], t['pos'][1], t['pos'][2] + 0.25), (1, 0, 0), (0, 1, 0), t['a'] * 3.4, t['a'] * 3.4)
        add(pd, 'world', radial_mat('padm_' + t['id'], hexlin(t.get('col', '7C88AE')), t.get('pad_strength', 2.5), power=1.6))

for c_ in SPEC.get('cages', []):
    ob = cyl_mesh('cage', c_['pos'], c_['r'], c_['h'], nseg=36, nring=14, r_top=c_.get('r_top'))
    add(ob, 'world', holo_mat('cagem', hexlin(c_.get('col', '7C88AE')), strength=c_.get('strength', 3.0), edge=0.0, fres=0.5, scan=c_.get('scan', 0.5), fill=0.01, wire=0.1, fade=0.2, h=c_['h']))
    ob.visible_shadow = False
    wo = wire_obj('cagew', cage_segs(c_['pos'], c_['r'], c_['h'], c_.get('r_top') or c_['r'], nrib=16, nring=7, nseg=40), 0.10)
    add(wo, 'world', emission_mat('cagewm', hexlin(c_.get('col', '7C88AE')), c_.get('wire_strength', 5.0)))
    wo.visible_shadow = False

for rg in SPEC.get('rings', []):
    ob = ring_mesh('ring_' + rg['id'], rg['pos'], rg['r'], rg['r'] - rg['w'], rg.get('z', 0.45), arc=rg.get('arc'))
    add(ob, rg.get('grp', 'world'), emission_mat('ringm_' + rg['id'], hexlin(rg['col']), rg.get('strength', 6.0), rg.get('alpha', 1.0)))
    if rg.get('fill'):
        q = quad_mesh('rfill_' + rg['id'], (rg['pos'][0], rg['pos'][1], rg['pos'][2] + 0.3), (1, 0, 0), (0, 1, 0), rg['r'] * 2, rg['r'] * 2)
        add(q, rg.get('grp', 'world'), radial_mat('rfm_' + rg['id'], hexlin(rg['col']), rg['fill'], power=rg.get('fill_pow', 1.4)))

for b in SPEC.get('blocks', []):
    ob = quad_mesh('blk_' + b['id'], (b['pos'][0], b['pos'][1], b['pos'][2] + b.get('z', 0.55)), b['along'], b['across'], b['len'], b['wid'])
    add(ob, 'world', tex_emission_mat('blkm_' + b['id'], b['tex'], b.get('strength', 5.0), 1.0))

for w_ in SPEC.get('walls', []):
    ob = quad_mesh('wall_' + w_['id'], (w_['pos'][0], w_['pos'][1], w_['pos'][2] + w_['h'] / 2), w_['dir'], (0, 0, 1), w_['w'], w_['h'])
    add(ob, 'world', tex_emission_mat('wallm_' + w_['id'], w_['tex'], w_.get('strength', 4.0), w_.get('alpha', 1.0)))
    ob.visible_shadow = False

for d_ in SPEC.get('domes', []):
    ob = dome_mesh('dome_' + d_['id'], d_['pos'], d_['r'])
    add(ob, 'world', holo_mat('domem_' + d_['id'], hexlin(d_.get('col', 'DDE6FF')), strength=d_.get('strength', 5.0), edge=d_.get('edge', 8.0), fres=1.2, scan=0.0, fill=0.03, wire=0.10, fade=0.0, h=d_['r']))
    ob.visible_shadow = False

for h_ in SPEC.get('heads', []):
    polys = h_['polys']
    for pi, poly in enumerate(polys):
        ink = poly_prism('hk%d' % pi, poly, h_.get('thick', 1.6), h_['scale'] * 1.22, h_['pos'], h_['dir'], z0=h_.get('z', 0.7) - 0.15)
        add(ink, 'heads', ink_mat('hinkm'))
        top = poly_prism('ht%d' % pi, poly, 0.4, h_['scale'], h_['pos'], h_['dir'], z0=h_.get('z', 0.7) + h_.get('thick', 1.6) - 0.1)
        add(top, 'heads', emission_mat('htm', hexlin(h_['col']), h_.get('strength', 9.0)))
        side = poly_prism('hs%d' % pi, poly, h_.get('thick', 1.6), h_['scale'] * 0.96, h_['pos'], h_['dir'], z0=h_.get('z', 0.7))
        add(side, 'heads', emission_mat('hsm', tuple(0.5 * np.array(hexlin(h_['col']))), h_.get('strength', 9.0) * 0.5))

for d_ in SPEC.get('glows', []):
    q = quad_mesh('glow', (d_['pos'][0], d_['pos'][1], d_['pos'][2] + d_.get('z', 0.5)), (1, 0, 0), (0, 1, 0), d_['r'] * 2, d_['r'] * 2)
    add(q, d_.get('grp', 'world'), radial_mat('glowm', hexlin(d_['col']), d_['strength'], power=d_.get('power', 2.0)))

for s_ in SPEC.get('shards', []):
    ob = poly_prism('shard', s_['poly'], s_.get('thick', 0.25), s_['scale'], s_['pos'], s_['dir'], z0=s_.get('z', 0.0), tilt=s_.get('tilt', 0.0), roll=s_.get('roll', 0.0))
    add(ob, s_.get('grp', 'world'), emission_mat('shm', hexlin(s_['col']), s_.get('strength', 10.0)))

for hm in SPEC.get('homes', []):
    c0 = hm['pos']
    ob = cyl_mesh('home', c0, hm['r'], hm['h'], nseg=6, nring=1)
    add(ob, 'world', holo_mat('homem', hexlin(hm.get('col', 'EAF0FF')), strength=hm.get('strength', 4.0), edge=0.0, fres=0.5, scan=0.3, fill=0.05, wire=0.1, fade=0.0, h=hm['h']))
    wo = wire_obj('homew', cage_segs(c0, hm['r'], hm['h'], hm['r'], nrib=6, nring=2, nseg=6), 0.12)
    add(wo, 'world', emission_mat('homewm', hexlin(hm.get('col', 'EAF0FF')), hm.get('wire_strength', 8.0)))
    cap = cyl_mesh('homecap', (c0[0], c0[1], c0[2] + hm['h']), hm['r'] * 0.94, 0.15, nseg=6, nring=1)
    add(cap, 'world', emission_mat('homecapm', hexlin(hm.get('cap', '0B0F26')), 0.4))
    pd = quad_mesh('homepad', (c0[0], c0[1], c0[2] + 0.3), (1, 0, 0), (0, 1, 0), hm['r'] * 5, hm['r'] * 5)
    add(pd, 'world', radial_mat('homepadm', hexlin(hm.get('glow', 'EAF0FF')), hm.get('pad_strength', 2.0), power=1.5))

for b_ in SPEC.get('bloom', []):
    me = city.data.copy()
    ob = bpy.data.objects.new('bloom', me)
    ob.location = (0, 0, b_.get('lift', 0.12))
    ob.data.materials.clear()
    add(ob, 'world', bloom_mat('bloomm', b_['field'], b_.get('strength', 1.4), b_.get('hair', 14.0)))

lights_spec(SPEC.get('lights', []))


# ================================================================== render passes
def set_vis(group, vis):
    for ob in bpy.data.objects:
        if ob.get('p1grp') == group:
            ob.hide_render = not vis


def dump(name):
    path = OUT + '_' + name
    scene.render.filepath = path + '.exr'
    scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.image_settings.color_depth = '16'
    scene.render.image_settings.color_mode = 'RGBA'
    t = time.time()
    bpy.ops.render.render(write_still=True)
    log('rendered', name, '%.1fs' % (time.time() - t))
    img = bpy.data.images.load(path + '.exr')
    img.colorspace_settings.name = 'Non-Color'
    iw, ih = img.size
    buf = np.empty(iw * ih * 4, np.float32)
    img.pixels.foreach_get(buf)
    arr = buf.reshape(ih, iw, 4)[::-1]
    if (iw, ih) != (RES[0], RES[1]):
        def lin_up(a, n, axis):
            src = (np.arange(n) + 0.5) * (a.shape[axis] / n) - 0.5
            i0 = np.clip(np.floor(src).astype(int), 0, a.shape[axis] - 1); i1 = np.clip(i0 + 1, 0, a.shape[axis] - 1)
            t = (src - np.floor(src)).astype(np.float32)
            sh = [1, 1, 1]; sh[axis] = n
            return np.take(a, i0, axis=axis) * (1 - t.reshape(sh)) + np.take(a, i1, axis=axis) * t.reshape(sh)
        arr = lin_up(lin_up(arr.astype(np.float32), RES[1], 0), RES[0], 1)
    arr = arr.astype(np.float16)
    np.save(path + '.npy', arr)
    bpy.data.images.remove(img)
    os.remove(path + '.exr')


S0 = SPEC.get('samples', 64)
for p in SPEC.get('passes', ['world_occ']):
    city.hide_render = False
    for ob in bpy.data.objects:
        ob.visible_camera = True
    set_vis('world', True); set_vis('heads', True); set_vis('lights', True)
    city.data.materials.clear()
    if p == 'world_occ':
        city.data.materials.append(mat_hold); set_vis('heads', False)
        cy.samples = S0
    elif p == 'world_ghost':
        city.hide_render = True; set_vis('heads', False); set_vis('lights', False)
        cy.samples = max(16, S0 // 3)
    elif p == 'heads_occ':
        city.data.materials.append(mat_hold); set_vis('world', False); set_vis('lights', False)
        cy.samples = max(24, S0 // 2)
    elif p == 'heads_ghost':
        city.hide_render = True; set_vis('world', False); set_vis('lights', False)
        cy.samples = max(16, S0 // 3)
    elif p == 'spill':
        city.data.materials.append(mat_diff)
        mo = SPEC.get('moon')
        if mo:
            sd = bpy.data.lights.new('moon', 'SUN')
            sd.energy = mo['sun']
            sd.color = hexlin(mo.get('col', '8FA8FF'))
            sd.angle = 0.12
            so = bpy.data.objects.new('moon', sd)
            d = Vector(mo['dir']).normalized()
            so.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
            link(so, 'lights')
            bgn.inputs[0].default_value = (*hexlin(mo.get('sky_col', '22305F')), 1)
            bgn.inputs[1].default_value = mo.get('sky', 0.2)
        for ob in bpy.data.objects:
            if ob.get('p1grp') in ('world', 'heads'):
                ob.visible_camera = False
        cy.samples = min(SPEC.get('spill_samples', 128), 48)
        scene.render.resolution_percentage = 50     # P2: the spill is low-frequency light; half-res + 48 spp, upscaled on load
    dump(p)
    scene.render.resolution_percentage = 100
log('done')
