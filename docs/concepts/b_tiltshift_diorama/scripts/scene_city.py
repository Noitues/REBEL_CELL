"""Stills 02 (city night) and 03 (high Heat): the diorama city from an ortho iso camera.

blender -b --factory-startup --python scene_city.py -- <out_dir> <city|heat|combat> [preview]
Writes <still>_beauty.png, <still>_depth.png and <still>_layout.json.
"""
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diorama_lib as D
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, MODE = argv[0], argv[1]
PREVIEW = len(argv) > 2 and argv[2] == "preview"
os.makedirs(OUT, exist_ok=True)

sc = D.reset()
HEAT = MODE == "heat"
DIM = 0.8 if HEAT else 1.0
D.setup_render(sc, 960 if PREVIEW else 1920, 540 if PREVIEW else 1080, 8 if PREVIEW else 32,
               view="AgX", look="AgX - Medium High Contrast", exposure=0.3)
D.world(sc, "#0c1224" if not HEAT else "#140a14", 1.4)

N = 17
HI, HJ = 7, 6
HQ_CELL = (HI, HJ)
city = D.City(seed=11, blocks=N, block=3.2, street=1.6, dim=DIM, heat=HEAT, map_z=4.6)
P = city.pitch


def c(di, dj):  # cell centre relative to the HQ cell
    return city.cell_center(HI + di, HJ + dj)


def street(k):  # coordinate of the street line after block k
    return (k - (N - 1) / 2) * P + P / 2


def hfn(i, j, d, r):
    if d < 1.5:
        return r.uniform(0.6, 1.6)  # lower ring around HQ so it reads
    if r.random() < 0.07:
        return r.uniform(4.5, 7.0)
    return r.uniform(0.45, 2.9) * (1.0 if d > 3 else 0.8)


city.build_ground()

# --- elevated highways at four heights (feedback 7.5)
sx, sy = street(HI + 2), street(HJ - 3)
city.highway([(-60, sy), (sx - 1.5, sy), (sx, sy - 1.5), (sx, -60)], z=2.3, seed=21)
city.highway([(street(HI - 1), 60), (street(HI - 1), street(HJ - 1) + 1.5), (street(HI - 1) + 1.5, street(HJ - 1)),
              (60, street(HJ - 1))], z=1.3, seed=22, lanes_col=("#ff3344", "#ffe9c2"))
city.highway([(-60, street(HJ + 1)), (street(HI + 3) - 1.8, street(HJ + 1)), (street(HI + 3), street(HJ + 1) - 1.8),
              (street(HI + 3), -60)], z=3.5, width=1.1, seed=23)
city.highway([(street(HI + 5), 60), (street(HI + 5), -60)], z=0.9, width=0.7, seed=24,
             lanes_col=("#ff5a6a", "#d8f4ff"))
city.highway([(-60, street(HJ - 6)), (60, street(HJ - 6))], z=1.8, width=0.8, seed=25)
city.build_blocks(hq_cell=HQ_CELL, skip={(HI + 3, HJ - 2)}, height_fn=hfn)
city.street_lights(every=1, energy=220.0)
city.street_traffic(seed=6)
city.flying_cars(46 if not HEAT else 26, zr=(5.9, 9.5), extent=30, seed=31)
city.flying_lane(tuple(c(-6, -1))[:2], tuple(c(9, -1))[:2], 7.0, 9 if not HEAT else 4, seed=32)
city.flying_lane(tuple(c(2, -7))[:2], tuple(c(2, 8))[:2], 8.2, 9 if not HEAT else 4, seed=33)

# --- hologram billboards (feedback 7.6)
bb_specs = [
    (c(-2, -1) + Vector((0, 0, 4.0)), 3.2, 1.5, "#5ce1ff", 0),
    (c(4, 2) + Vector((0, 0, 3.9)), 2.6, 1.3, "#ff3da8", math.pi / 2),
    (c(5, -3) + Vector((0, 0, 3.5)), 2.4, 1.1, "#d4ff00", 0),
    (c(2, 4) + Vector((0, 0, 4.1)), 3.0, 1.4, "#b04dff", math.pi / 2),
    (c(-3, 3) + Vector((0, 0, 3.4)), 2.0, 1.1, "#ff8c1a", 0),
    (c(2, -5) + Vector((0, 0, 3.2)), 2.4, 1.1, "#5ce1ff", math.pi / 2),
    (c(0, -3) + Vector((0, 0, 2.6)), 1.6, 0.8, "#ff3da8", 0),
    (c(7, 3) + Vector((0, 0, 3.2)), 2.2, 1.0, "#3dff8b", 0),
    (c(6, 0) + Vector((0, 0, 2.8)), 2.0, 0.9, "#ff8c1a", math.pi / 2),
    (c(-4, -4) + Vector((0, 0, 3.0)), 2.2, 1.0, "#b04dff", math.pi / 2),
]
for k, (p, w, h, col, yaw) in enumerate(bb_specs):
    w, h = w * 1.35, h * 1.35
    p = p + Vector((0, 0, 0.6))
    city.billboard(p, w, h, col, yaw, seed=k + 1, strength=9.0 if not HEAT else 6.0, alpha=0.8)

# --- patchy fog pockets with varied density (feedback 7.2)
fr = random.Random(51)
for k in range(16):
    di, dj = fr.randint(-5, 7), fr.randint(-6, 5)
    p = c(di, dj) + Vector((fr.uniform(-2, 2), fr.uniform(-2, 2), fr.uniform(0.2, 1.0)))
    s = (fr.uniform(2.0, 5.0), fr.uniform(2.0, 5.0), fr.uniform(0.8, 2.0))
    col = fr.choice(["#7d97bd", "#8a7db8", "#6fa5b8", "#b87da8"])
    city.fog_pocket(p, s, fr.uniform(0.2, 0.9), col, seed=k)

# --- grid map on ONE plane (feedback 7.4)
NODES = [("CORE", 0, 0, "hq"), ("Scrub Records", -1, -2, "cell"), ("Billing Farm", -2, 1, "cell"),
         ("Pricing Archive", 1, -2, "open"), ("Kill-Switch Auth.", 3, 0, "corp"), ("Patch Node", 1, 2, "open"),
         ("Burn the Ledger", 3, -3, "corp"), ("Renewal Engine", 5, 2, "boss"), ("Wipe Biometrics", -1, -4, "open"),
         ("Vault 9", 6, -1, "corp"), ("Call Centre", 3, 4, "corp"), ("Orbital Relay", 6, 5, "open")]
nodes = {n: (c(i, j).x, c(i, j).y, k) for n, i, j, k in NODES}
links = [("CORE", "Scrub Records", "cell"), ("CORE", "Billing Farm", "cell"), ("Scrub Records", "Pricing Archive", "cell"),
         ("CORE", "Patch Node", "net"), ("Pricing Archive", "Kill-Switch Auth.", "net"),
         ("Kill-Switch Auth.", "Renewal Engine", "net"), ("Pricing Archive", "Burn the Ledger", "net"),
         ("Burn the Ledger", "Vault 9", "net"), ("Patch Node", "Call Centre", "net"), ("Kill-Switch Auth.", "Patch Node", "net"),
         ("Scrub Records", "Wipe Biometrics", "net"), ("Call Centre", "Orbital Relay", "net"),
         ("Renewal Engine", "Orbital Relay", "net"), ("Vault 9", "Renewal Engine", "net")]
if HEAT:
    links += [("Renewal Engine", "Patch Node", "threat"), ("Vault 9", "Kill-Switch Auth.", "threat"),
              ("Call Centre", "CORE", "threat")]
MAP_Z = 5.4
city.map_layer(nodes, links, z=MAP_Z)

# --- key light (moon) and sky fill
D.area_light("moon", (-20, 20, 40), (math.radians(35), 0, math.radians(-135)), "#8fb4ff", 5000 * DIM, 40)
D.area_light("fill", (30, -10, 25), (math.radians(50), 0, math.radians(70)), "#ff6ab8", 1800 * DIM, 40)

heat_objs = []
pre_heat = {o.name for o in sc.objects}
if HEAT:
    hr = random.Random(61)
    body = D.mat_pbr("heli", "#9aa3b3", rough=0.35, metal=0.3)
    rotor = D.mat_pbr("rotor", "#3a3f48", rough=0.4, alpha=0.25)
    red = D.mat_emit("h_red", "#ff2233", 40)
    blue = D.mat_emit("h_blue", "#3d7bff", 40)
    heli_pos = [tuple(c(di, dj) + Vector((0, 0, z))) for di, dj, z in ((1, -2, 8.6), (4, 1, 9.2), (-2, 2, 9.0), (6, -2, 8.4), (3, 4, 9.6))]
    HS = 2.2  # miniature hero scale for the choppers
    for k, hp in enumerate(heli_pos):
        hp = Vector(hp)
        yaw = hr.uniform(0, math.pi * 2)
        g = D.box("heli_body", hp, (1.3 * HS, 0.55 * HS, 0.5 * HS), body, city.coll, rot=(0, 0, yaw))
        heat_objs.append(g)
        D.point_light("heli_key", hp + Vector((1.5, -1.5, 1.5)), "#dfe8ff", 120, 0.3, city.coll)
        d = Vector((math.cos(yaw), math.sin(yaw), 0))
        D.box("heli_glass", hp + d * 0.5 * HS + Vector((0, 0, 0.05 * HS)), (0.4 * HS, 0.5 * HS, 0.35 * HS), D.mat_emit("hglass", "#9fdcff", 2.0), city.coll, rot=(0, 0, yaw))
        D.box("heli_tail", hp - d * 1.1 * HS + Vector((0, 0, 0.1 * HS)), (1.2 * HS, 0.12 * HS, 0.12 * HS), body, city.coll, rot=(0, 0, yaw))
        D.box("heli_bar", hp + Vector((0, 0, 0.3 * HS)), (0.5 * HS, 0.12 * HS, 0.06 * HS), red if k % 2 else blue, city.coll, rot=(0, 0, yaw))
        D.point_light("heli_bar_l", hp + Vector((0, 0, -1.0)), "#ff2233" if k % 2 else "#3d7bff", 900, 0.4, city.coll)
        city.fog_objs.append(D.cyl("heli_rotor", hp + Vector((0, 0, 0.36 * HS)), 1.5 * HS, 0.01, rotor, 32, coll=city.coll))
        for bl in (0.3, 0.3 + math.pi / 2):
            D.box("heli_blade", hp + Vector((0, 0, 0.37 * HS)), (3.0 * HS, 0.07 * HS, 0.02), body, city.coll, rot=(0, 0, yaw + bl))
        D.box("heli_skid", hp + Vector((0, 0, -0.34 * HS)), (1.1 * HS, 0.5 * HS, 0.03 * HS), body, city.coll, rot=(0, 0, yaw))
        D.cyl("heli_r", hp - d * 0.3 * HS + Vector((0, 0, -0.3 * HS)), 0.12 * HS, 0.1 * HS, red if k % 2 else blue, 8, coll=city.coll)
        D.cyl("heli_r2", hp - d * 1.6 * HS + Vector((0, 0, 0.2 * HS)), 0.08 * HS, 0.08 * HS, blue if k % 2 else red, 8, coll=city.coll)
        # searchlight: spot to a street target
        tgt = Vector((hp.x + hr.uniform(-4, 4), hp.y + hr.uniform(-4, 4), 0))
        dirv = (tgt - hp).normalized()
        rot = dirv.to_track_quat("-Z", "Y").to_euler()
        D.spot_light("search", hp - Vector((0, 0, 0.2)), rot, "#e8f2ff", 30000, angle=0.24, blend=0.3, coll=city.coll)
        # visible beam cone mesh (soft emissive) for readability
        beam = D.mat_beam(f"sbeam{k}", "#e6eeff", 1.6, a_near=0.3, a_far=0.03)
        L = (tgt - hp).length
        cone = D.cyl("beamcone", hp + dirv * (L / 2), L * math.tan(0.11), L, beam, 20, coll=city.coll, r2=0.1)
        cone.rotation_euler = (dirv.to_track_quat("-Z", "Y")).to_euler()
        city.fog_objs.append(cone)
    # patrol drones with red/blue strobes
    for k in range(26):
        p = c(hr.uniform(-3, 7), hr.uniform(-5, 5)) + Vector((0, 0, hr.uniform(6.4, 9.2)))
        heat_objs.append(D.box("drone", p, (0.6, 0.6, 0.1), body, city.coll))
        for sx_, sy_ in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            city.fog_objs.append(D.cyl("rotor_d", p + Vector((sx_ * 0.36, sy_ * 0.36, 0.06)), 0.22, 0.01, rotor, 12, coll=city.coll))
        heat_objs.append(D.cyl("strobe", p + Vector((0, 0, -0.08)), 0.13, 0.05, red if k % 2 else blue, 8, coll=city.coll))
        D.point_light("strobe_l", p - Vector((0, 0, 0.3)), "#ff2233" if k % 2 else "#3d7bff", 60, 0.1, city.coll)
    # red/blue rim flicker lights on corp blocks
    for k, (i, j) in enumerate([(3, 0), (3, -3), (5, 2), (6, -1), (3, 4)]):
        D.point_light("corp_alarm", c(i, j) + Vector((0, 0, 3.0)), "#ff2a3a" if k % 2 else "#3d6bff", 700, 1.0, city.coll)
    # everything airborne stays in focus (a miniature's hero props), except beam volumes
    fog_names = {o.name for o in city.fog_objs}
    heat_objs = [o for o in sc.objects if o.name not in pre_heat and o.type == "MESH" and o.name not in fog_names]

# --- camera: HQ fully framed (feedback 7.1)
hq = c(0, 0)
cam = D.iso_camera(sc, target=(hq.x, hq.y, 6.5), ortho=56.0, dist=80.0, tilt=56.0, yaw=45.0)
cam.data.shift_x = 0.16
cam.data.shift_y = -0.02
cam.data.clip_start = 25
cam.data.clip_end = 150
sc.eevee.use_volume_custom_range = True
sc.eevee.volumetric_start = 45
sc.eevee.volumetric_end = 125

sc.render.filepath = os.path.join(OUT, f"{MODE}_beauty.png")
bpy.ops.render.render(write_still=True)

# layout for the post pass
lay = {"nodes": [], "hq_top": D.project(sc, cam, hq + Vector((0, 0, city.hq_top))),
       "hq_base": D.project(sc, cam, hq), "res": [sc.render.resolution_x, sc.render.resolution_y]}
for name, p, kind in city.nodes:
    lay["nodes"].append([name, kind] + list(D.project(sc, cam, p)))
if HEAT:
    lay["helis"] = [D.project(sc, cam, Vector(h)) for h in heli_pos]
D.save_json(os.path.join(OUT, f"{MODE}_layout.json"), lay)

D.depth_pass(sc, os.path.join(OUT, f"{MODE}_depth.png"), near=50, far=120,
             keep_sharp=city.map_objs + heat_objs, hide=city.fog_objs)
print("DONE", MODE)
