"""Kit sheet renders: every module and prop on a lit floor pad, same cel/ink as the scene.
blender -b --factory-startup -P bl_kit.py -- <outdir>     -> <outdir>/<group>__<item>.png (transparent) """
import bpy, sys, os, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit_lib as K
import kit_gen

OUTDIR = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUTDIR, exist_ok=True)
P = K.PAL
RW, RH = 520, 540

GROUPS = {
    'modules': ['floor_plate', 'wall_panel', 'window_module', 'door_module', 'cut_edge', 'corner_post'],
    'bio_lab': ['vat', 'vat_bank', 'bench', 'centrifuge', 'incubator_pod', 'monitor_cart', 'helix_tank'],
    'server_room': ['rack', 'rack_row', 'cooling', 'console', 'ups', 'cable_tray', 'core_tower'],
    'greenhouse': ['planter', 'plant_tank', 'seed_wall', 'grow_lamp', 'cistern', 'seed_tree'],
    'records_office': ['desk', 'cabinet', 'shelf_stack', 'copier', 'box_pile', 'archive_tower'],
    'lobby': ['reception', 'kiosk', 'seats', 'planter_lobby', 'emblem_sculpture'],
    'clutter': ['crate', 'crate_stack', 'barrel', 'cable_run', 'box_small'],
    'event_room': ['holo_table', 'exam_bed', 'privacy_screen', 'folding_chairs', 'med_cabinet', 'iv_stand', 'scanner_arch', 'trestle'],
    'shop': ['display_island', 'counter', 'shelf_unit', 'gondola', 'cooler', 'vending', 'crate_display', 'basket_rack'],
}
ONLY = sys.argv[sys.argv.index('--') + 2].split(',') if len(sys.argv) > sys.argv.index('--') + 2 else None
LIGHT = {'bio_lab': 'lime', 'server_room': 'cyan', 'greenhouse': 'lime', 'records_office': 'amber', 'lobby': 'lime', 'modules': 'lime', 'clutter': 'lime', 'event_room': 'violet', 'shop': 'lime_p'}
CORP = {'lime': P['lime'], 'cyan': P['cyan'], 'pink': P['pink'], 'amber': P['amber'], 'violet': P['violet'], 'lime_p': P['lime_p']}


def mk(name, layer, mat, coll):
    verts, faces, cols = K.G.layers[layer]
    if not verts:
        return None
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(cols):
        ca.data[i].color = c
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cy.device = 'CPU'; cy.samples = 16; cy.use_denoising = False; cy.max_bounces = 0; cy.filter_width = 1.0
    sc.render.resolution_x, sc.render.resolution_y = RW, RH
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = 'ABSOLUTE'
    sc.render.line_thickness = 1.0
    inkc = bpy.data.collections.new('inkc')
    sc.collection.children.link(inkc)
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(105)
    for ls in list(fs.linesets):
        fs.linesets.remove(ls)
    ls = fs.linesets.new('ink')
    ls.select_silhouette = ls.select_border = ls.select_crease = True
    ls.select_by_collection = True
    ls.collection = inkc
    ls.linestyle.color = (0.03, 0.02, 0.08)
    ls.linestyle.thickness = 2.4
    ls.linestyle.use_chaining = True
    m = bpy.data.materials.new('vc')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    at = nt.nodes.new('ShaderNodeAttribute')
    at.attribute_name = 'Col'
    nt.links.new(at.outputs['Color'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    cd = bpy.data.cameras.new('cam')
    cd.type = 'ORTHO'
    cd.clip_end = 900
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc, inkc, m, cam, cd


SC, INKC, MAT, CAM, CD = setup()


def pad(x0, y0, x1, y1, z=0.0):
    K.box('ink', x0 - 0.05, y0 - 0.05, z - 0.3, x1 - x0 + 0.1, y1 - y0 + 0.1, 0.3, P['slab'])
    for i in range(int(x0), int(x1)):
        for j in range(int(y0), int(y1)):
            a = P['floor_a'] if (i + j) % 2 == 0 else P['floor_b']
            K.quad_z('fx', z + 0.012, i + 0.025, i + 0.975, j + 0.025, j + 0.975, a)


def render(group, item, tgt, px):
    for o in list(SC.collection.all_objects):
        if o.type == 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
    mk('ink', 'ink', MAT, INKC)
    mk('fx', 'fx', MAT, SC.collection)
    el = math.radians(35.264)
    CD.ortho_scale = RW / px
    CD.shift_x = 0
    CD.shift_y = 0
    dirv = Vector((math.cos(el) * 0.70710678, -math.cos(el) * 0.70710678, math.sin(el)))
    CAM.location = tgt + dirv * 200
    CAM.rotation_euler = (-dirv).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    for _ in range(3):
        v = world_to_camera_view(SC, CAM, tgt)
        CD.shift_x -= (0.5 - v.x)
        CD.shift_y -= (0.55 - v.y) * (RH / RW)
        bpy.context.view_layer.update()
    SC.render.filepath = os.path.join(OUTDIR, '%s__%s.png' % (group, item))
    bpy.ops.render.render(write_still=True)


def shell_spec(wins, door):
    return dict(windows=wins, door=door, W=3, D=3)


for group, items in GROUPS.items():
    if ONLY and group not in ONLY:
        continue
    for item in items:
        G = K.reset()
        G.haze_k = 0.0
        lc = CORP[LIGHT[group]]
        if group == 'modules':
            G.room_zone = (-0.5, -0.5, 0, 3.5, 3.5, 4.0)
            G.amb = 0.6
            G.lights.append(dict(p=Vector((1.6, 1.4, 1.2)), col=P['lime'], r=4.0, zone=G.room_zone, k=1.0))
            if item == 'floor_plate':
                pad(0, 0, 4, 4)
                tgt, px = Vector((2, 2, 0.2)), 120
            elif item == 'corner_post':
                pad(0, 0, 3, 3)
                K.box('ink', 0.9, 0.9, 0.0, 0.2, 0.3, 3.3, P['metal_d'])
                K.box('fx', 0.9, 0.87, 0.0, 0.04, 0.3, 3.3, P['lime'], emit=True)
                tgt, px = Vector((1.0, 1.0, 1.7)), 110
            else:
                spec = {'wall_panel': shell_spec([], None),
                        'window_module': shell_spec([('back', 0, 2), ('left', 0, 2)], None),
                        'door_module': shell_spec([], dict(wall='back', pos=0.9, w=1.4)),
                        'cut_edge': shell_spec([], None)}[item]
                K.room_shell(3, 3, 0.6, spec, corp='lime')
                tgt, px = ((Vector((1.5, 1.5, 2.2)), 105) if item != 'cut_edge' else (Vector((2.4, -0.2, 0.3)), 230))
        else:
            cat = kit_gen.CAT[item]
            w, d, h = cat
            G.room_zone = (-2, -2, 0, w + 3, d + 3, 5)
            G.amb = 0.7
            G.lights.append(dict(p=Vector((w / 2, d / 2, 1.2)), col=lc, r=3.6 + max(w, d), zone=G.room_zone, k=1.0))
            pad(-1, -1, w + 1, d + 1)
            K.place_prop(item, 0, 0, 0, 0.0, kit_gen.CAT, seed=7)
            tgt, px = Vector((w / 2, d / 2, h * 0.45)), 100 if max(w, d) < 3 else 88
        render(group, item, tgt, px)
print('KIT DONE')
