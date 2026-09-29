"""Still 04: the Modem shop. A street-corner miniature with the vertical MODEM / CYBER SHOP neon sign
(an original redraw in the spirit of the pre-W8c sign) lighting its facade and the wet street.

blender -b --factory-startup --python scene_modem.py -- <out_dir> [preview]
"""
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diorama_lib as D
import stroke_font as SF
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = len(argv) > 1 and argv[1] == "preview"

sc = D.reset()
D.setup_render(sc, 960 if PREVIEW else 1920, 540 if PREVIEW else 1080, 8 if PREVIEW else 32,
               view="AgX", look="AgX - Punchy", exposure=0.2)
D.world(sc, "#0a1020", 1.0)

# ---- background city (a normal diorama block grid behind the shop)
N = 11
city = D.City(seed=23, blocks=N, block=3.2, street=1.6, dim=0.9, map_z=99, win_scale=1.8)
city.build_ground()
P = city.pitch
city.highway([(-60, 7.2), (60, 7.2)], z=2.6, seed=4)
city.highway([(-60, 16.8), (60, 16.8)], z=1.6, seed=5, lanes_col=("#ff3344", "#ffe9c2"))
city.highway([(-60, 26.4), (60, 26.4)], z=3.6, seed=6)
city.build_blocks(hq_cell=(-9, -9), skip={(i, j) for i in range(N) for j in range(N) if j <= 5},
                  height_fn=lambda i, j, d, r: r.uniform(0.8, 4.0) if r.random() > 0.1 else r.uniform(4.5, 7.5))
city.street_lights(every=1, energy=180.0)
city.street_traffic(seed=8)
city.flying_cars(24, zr=(5.5, 9), extent=20, seed=12)
for k, (x, y, z, col, w) in enumerate([(-6, 10, 5.5, "#5ce1ff", 3.4), (9, 12, 6.0, "#b04dff", 3.0), (3, 20, 6.5, "#d4ff00", 2.8),
                                       (-12, 18, 5.0, "#ff8c1a", 3.0)]):
    city.billboard((x, y, z), w, w * 0.45, col, 0, seed=k + 60, strength=8.0, alpha=0.8)
fr = random.Random(3)
for k in range(8):
    city.fog_pocket((fr.uniform(-14, 14), fr.uniform(2, 22), fr.uniform(0.4, 1.4)),
                    (fr.uniform(2, 5), fr.uniform(2, 4), fr.uniform(0.8, 1.6)), fr.uniform(0.25, 0.8), seed=k + 70)

# ---- the Modem building, front and centre-left, facing -Y (the camera)
SX, SY = -3.2, 1.2
facade = D.mat_building("modem_facade", base="#1a1a26", wins=("#ffcf8a", "#9fe6ff"), lit=0.12, cols_per_unit=5,
                        rows_per_unit=3.6, win_str=1.2)
D.box("modem_bldg", (SX, SY + 1.6, 4.2), (4.6, 3.2, 8.4), facade)
D.box("modem_roof", (SX, SY + 1.6, 8.45), (4.8, 3.4, 0.1), D.mat_pbr("roof", "#262b36", rough=0.6, metal=0.4))
# storefront: lit glass with shelves of glowing stock
D.box("store", (SX + 0.4, SY - 0.02, 0.9), (3.2, 0.05, 1.5), D.mat_emit("store_glass", "#3aa8c8", 1.4))
for k in range(4):
    D.box("shelf", (SX + 0.4, SY - 0.05, 0.4 + k * 0.36), (3.0, 0.03, 0.04), D.mat_emit(f"shelf{k}", ["#ff3da8", "#d4ff00", "#5ce1ff", "#b04dff"][k], 4.0))
D.box("awning", (SX + 0.4, SY - 0.45, 1.8), (3.6, 0.9, 0.06), D.mat_pbr("awn", "#2a1830", rough=0.5))
D.box("awning_lip", (SX + 0.4, SY - 0.9, 1.78), (3.6, 0.03, 0.08), D.mat_emit("awl", "#ff3da8", 6.0))
# neighbour buildings
nb = D.mat_building("nb", base="#161c2a", lit=0.15, cols_per_unit=5, rows_per_unit=3.6, win_str=1.2)
D.box("nb1", (SX - 4.4, SY + 2.2, 2.4), (3.6, 3.6, 4.8), nb)
D.box("nb2", (SX + 4.4, SY + 2.0, 1.2), (3.8, 4.0, 2.4), nb)
D.box("nb3", (SX + 8.6, SY + 2.4, 1.6), (4.0, 4.8, 3.2), nb)

# ---- the sign: vertical blade frame, MODEM stacked, CYBER / SHOP below, circuit traces
pink = D.mat_emit("neon_pink", "#ff3da8", 14.0)
pink_dim = D.mat_emit("neon_pink_dim", "#ff3da8", 5.0)
cyan = D.mat_emit("neon_cyan", "#5ce1ff", 12.0)
backer = D.mat_pbr("sign_backer", "#0c0d16", rough=0.4, metal=0.5)
FX, FY, FZ = SX - 1.0, SY - 0.5, 1.95    # frame bottom-left anchor in the sign plane (x right, z up)
FW, FH = 2.0, 6.3
D.box("sign_backer", (FX + FW / 2, FY + 0.08, FZ + FH / 2), (FW + 0.1, 0.12, FH + 0.1), backer)
for zz in (FZ + 1.0, FZ + FH - 1.0):
    D.box("bracket", (FX + FW + 0.2, FY + 0.35, zz), (0.5, 0.6, 0.08), D.mat_pbr("br", "#3a3f48", metal=1, rough=0.3))


def plane_pts(pts2d):
    return [(FX + x, FY, FZ + z) for x, z in pts2d]


def rrect2d(x0, z0, w, h, r, n=6):
    pts = []
    for cx, cz, a0 in ((x0 + w - r, z0 + r, 270), (x0 + w - r, z0 + h - r, 0), (x0 + r, z0 + h - r, 90), (x0 + r, z0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


D.tube_poly("frame", plane_pts(rrect2d(0.05, 0.05, FW - 0.1, FH - 0.1, 0.35)), 0.045, pink, cyclic=True)
D.tube_poly("frame_in", plane_pts(rrect2d(0.16, 0.16, FW - 0.32, FH - 0.32, 0.26)), 0.018, pink_dim, cyclic=True)


def neon_glyph(ch, x, z, h, mat, rad, name):
    for k, poly in enumerate(SF.GLYPHS[ch]):
        sm = SF._resample(SF._chaikin([(px, py) for px, py in poly], 1), 0.05)
        D.tube_poly(f"{name}_{k}", plane_pts([(x + px * h, z + py * h) for px, py in sm]), rad, mat)


# MODEM, stacked top to bottom, outline-style double tube (outer bright, inner dim)
LH = 0.72
for k, ch in enumerate("MODEM"):
    gw = SF.glyph_width(ch) * LH
    x = FW / 2 - gw / 2
    z = FH - 0.42 - (k + 1) * (LH + 0.12)
    neon_glyph(ch, x, z, LH, pink, 0.05, f"L{k}")
# circuit traces with ring pads, branching to the frame (the original's circuitry motif, redrawn)
rng = random.Random(9)
for k in range(10):
    side = -1 if k % 2 else 1
    z = FH - 0.8 - k * 0.42 + rng.uniform(-0.1, 0.1)
    x0 = FW / 2 + side * 0.48
    x1 = FW / 2 + side * (0.72 + rng.uniform(0, 0.12))
    pts = [(x0, z), (x1 - side * 0.12, z), (x1, z - 0.14 * side * (1 if k % 3 else -1))]
    D.tube_poly(f"trace{k}", plane_pts(pts), 0.012, pink_dim)
    ring = [(pts[-1][0] + 0.05 * math.cos(a / 8 * 2 * math.pi), pts[-1][1] + 0.05 * math.sin(a / 8 * 2 * math.pi)) for a in range(8)]
    D.tube_poly(f"pad{k}", plane_pts(ring), 0.012, pink_dim, cyclic=True)
# CYBER / SHOP in cyan
for row, word in enumerate(("CYBER", "SHOP")):
    h = 0.32
    total = sum(SF.glyph_width(c) * h + 0.07 for c in word) - 0.07
    x = FW / 2 - total / 2
    z = 0.95 - row * 0.46
    for k, ch in enumerate(word):
        neon_glyph(ch, x, z, h, cyan, 0.026, f"C{row}_{k}")
        x += SF.glyph_width(ch) * h + 0.07
# the sign lights its facade, the awning and the wet street (feedback 10)
for k in range(5):
    D.point_light("sign_glow", (FX + FW / 2, FY - 0.6, FZ + 1.6 + k * 1.1), "#ff3da8", 160, 0.6)
D.point_light("sign_glow_c", (FX + FW / 2, FY - 0.6, FZ + 0.6), "#5ce1ff", 120, 0.5)
D.point_light("store_glow", (SX + 0.4, SY - 1.0, 0.8), "#3aa8c8", 120, 0.8)
# street in front: puddle-rich asphalt, a couple of parked hover-bikes
bike = D.mat_pbr("bike", "#2a2f3a", rough=0.3, metal=0.7)
for k, x in enumerate((SX + 2.6, SX + 3.5)):
    D.box("bike", (x, SY - 2.2, 0.35), (0.7, 0.24, 0.16), bike, rot=(0, 0, 0.1 * k))
    D.box("bike_l", (x - 0.36, SY - 2.2, 0.36), (0.04, 0.18, 0.05), D.mat_emit(f"bl{k}", "#ff3344", 12))
D.area_light("moon", (-20, -10, 40), (math.radians(30), 0, math.radians(-40)), "#8fb4ff", 2500, 40)

# ---- camera: long lens, high three-quarter view, the sign fully framed on the left third
cd = bpy.data.cameras.new("cam")
cd.lens = 85
cd.clip_start = 1
cd.clip_end = 300
cam = bpy.data.objects.new("cam", cd)
sc.collection.objects.link(cam)
target = Vector((SX + 6.4, SY + 2.0, 2.4))
cam.location = target + Vector((-4.0, -46.0, 25.0))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sc.eevee.use_volume_custom_range = True
sc.eevee.volumetric_start = 20
sc.eevee.volumetric_end = 110

sc.render.filepath = os.path.join(OUT, "modem_beauty.png")
bpy.ops.render.render(write_still=True)
D.save_json(os.path.join(OUT, "modem_layout.json"), {
    "sign_top": D.project(sc, cam, Vector((FX + FW / 2, FY, FZ + FH))),
    "sign_bot": D.project(sc, cam, Vector((FX + FW / 2, FY, FZ))),
    "res": [sc.render.resolution_x, sc.render.resolution_y]})
D.depth_pass(sc, os.path.join(OUT, "modem_depth.png"), near=30, far=110, hide=city.fog_objs)
print("DONE modem")
