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
WORK = SPEC.get('work', 'D:/rc_scratch/tide_concepts/p1_work/')
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

