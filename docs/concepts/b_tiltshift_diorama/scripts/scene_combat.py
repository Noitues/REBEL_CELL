"""Still 01: a fight. Two physical spinners parented to the camera over a far, defocused city.

blender -b --factory-startup --python scene_combat.py -- <out_dir> [preview]
"""
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diorama_lib as D
import spinner_lib as S
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = len(argv) > 1 and argv[1] == "preview"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FONTS = {"num": os.path.join(ROOT, "assets", "fonts", "Anton-Regular.ttf"),
         "mono": os.path.join(ROOT, "assets", "fonts", "ShareTechMono-Regular.ttf")}

sc = D.reset()
D.setup_render(sc, 960 if PREVIEW else 1920, 540 if PREVIEW else 1080, 8 if PREVIEW else 32,
               view="AgX", look="AgX - Punchy", exposure=0.1)
D.world(sc, "#0a1020", 1.0)

# the city: same generator, a different district, lit lower (it will be dimmed further in post)
N = 13
city = D.City(seed=5, blocks=N, block=3.2, street=1.6, dim=0.8, map_z=99)
city.build_ground()
P = city.pitch
st = lambda k: (k - (N - 1) / 2) * P + P / 2
city.highway([(-60, st(5)), (st(7) - 1.5, st(5)), (st(7), st(5) - 1.5), (st(7), -60)], z=2.3, seed=2)
city.highway([(st(3), 60), (st(3), -60)], z=1.3, seed=3)
city.build_blocks(hq_cell=(-9, -9), height_fn=lambda i, j, d, r: r.uniform(0.5, 3.4) if r.random() > 0.06 else r.uniform(4, 6.5))
city.street_lights(every=1, energy=200.0)
city.street_traffic(seed=7)
city.flying_cars(20, zr=(6, 9), extent=20, seed=9)
for k, (i, j, col) in enumerate([(3, 8, "#5ce1ff"), (8, 4, "#b04dff"), (5, 2, "#ff8c1a"), (9, 9, "#ff3da8")]):
    city.billboard(city.cell_center(i, j) + Vector((0, 0, 4.2)), 3.6, 1.7, col, (k % 2) * math.pi / 2, seed=k + 20,
                   strength=7.0, alpha=0.75)
fr = random.Random(8)
for k in range(10):
    p = city.cell_center(fr.randint(1, N - 2), fr.randint(1, N - 2)) + Vector((0, 0, fr.uniform(0.4, 1.2)))
    city.fog_pocket(p, (fr.uniform(2, 5), fr.uniform(2, 5), fr.uniform(1, 2)), fr.uniform(0.2, 0.8), seed=k + 40)
D.area_light("moon", (-20, 20, 40), (math.radians(35), 0, math.radians(-135)), "#8fb4ff", 4000, 40)

cam = D.iso_camera(sc, target=(0, 0, 1.5), ortho=24.0, dist=90.0, tilt=56.0, yaw=45.0)
cam.data.clip_start = 5
cam.data.clip_end = 160
sc.eevee.use_volume_custom_range = True
sc.eevee.volumetric_start = 55
sc.eevee.volumetric_end = 140

# --- spinners (feedback 4): machined, lit by the scene, sitting well in front of the city
op = S.build_spinner("OP", [("ATK", 5, 6), ("DEF", 5, 5), ("CRIT", 3, 12), ("EVD", 4, 4), ("ATK", 4, 6),
                            ("DEF", 5, 6), ("MISS", 4, None)], owner="op", hub_text="BREAKER\nbreaker core",
                     hp=(60, 60), needle_tick=13.1, fonts=FONTS, seed=1)
en = S.build_spinner("EN", [("AFF", 5, 14), ("DEF", 4, 6), ("ATK", 5, 8), ("MISS", 3, None), ("ATK", 5, 8),
                            ("DEF", 4, 6), ("CRIT", 4, 12)], owner="en", hub_text="COLLECTIONS\nagent // meridian",
                     hp=(40, 40), forecast_loss=12, needle_tick=20.5, fonts=FONTS, seed=2, corp_col="#ff8c1a")
R_PX = 215
S.place_on_camera(op, cam, 560, 440, R_PX, 20.0, tilt=(math.radians(-16), math.radians(12), 0))
S.place_on_camera(en, cam, 1340, 440, R_PX, 20.0, tilt=(math.radians(-16), math.radians(-12), 0))

# hit on the enemy's left edge: binary shards (feedback 5)
S.binary_shards(cam, 1112, 420, 30, seed=7, spread=(105, 250), dist=(70, 330), size_px=(28, 64), depth=16.0,
                fonts=FONTS)

# key/rim lights for the spinner stage (parented so they stay with the frame)
upx = cam.data.ortho_scale / 1920
for name, loc, col, e, size in [("key", (-18, 16, -4), "#cfe0ff", 3500, 14), ("rimP", (-24, -8, -14), "#ff3da8", 1800, 8),
                                ("rimO", (24, -6, -14), "#ff8c1a", 1800, 8)]:
    l = D.area_light(name, loc, (0, 0, 0), col, e, size)
    l.parent = cam
    # aim at the stage centre
    tgt = Vector((0, 0, -20))
    l.rotation_euler = (tgt - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

sc.render.filepath = os.path.join(OUT, "combat_beauty.png")
bpy.ops.render.render(write_still=True)

D.depth_pass(sc, os.path.join(OUT, "combat_depth.png"), near=10, far=130, hide=city.fog_objs)
print("DONE combat")
