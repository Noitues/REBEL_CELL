"""Still 03: the same city at Heat HUNTED. Helicopters with searchlight cones through the rain, drone swarms,
red/blue rim flicker on corp towers, threat routes converging on the HQ. Glitch + desaturation happen in post."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rn_lib import *  # noqa
from rn_parts import *  # noqa
from city_scene import City, HQ, NET_Z

BASE = out_arg(os.path.join(STILLS, "_raw_03"))
reset(samples=int(os.environ.get("RN_SAMPLES", "32")))
city = City(heat=1.0, seed=4)          # same seed: same streets, now hunted
city.camera()
city.compute_focus()
city.gp_fx = GP("gp_fx")
city.gp_net = GP("gp_net")
city.build()
city.net(claimed=("hq", "a", "b"), threat=("e", "f", "c", "d"))
city.rain(8000)
city.ui_gp()
rng = random.Random(33)
g = city.gp_fx


def helicopter(name, p, yaw, target, k=1.9):
    rot = (0, 0, yaw)
    body = mat_pbr("heli", "#161b24", 0.35, 0.7)
    d = Vector((math.cos(yaw), math.sin(yaw), 0))
    box(name + "_body", p, (4.2 * k, 1.8 * k, 1.6 * k), body, rot=rot)
    box(name + "_nose", p + d * 2.4 * k + Vector((0, 0, -0.2 * k)), (1.2 * k, 1.4 * k, 1.0 * k), mat_pbr("heli_glass", "#0a0f18", 0.05, 0.2, coat=1.0), rot=rot)
    box(name + "_tail", p - d * 4.0 * k + Vector((0, 0, 0.4 * k)), (4.0 * k, 0.35 * k, 0.35 * k), body, rot=rot)
    box(name + "_fin", p - d * 5.9 * k + Vector((0, 0, 0.9 * k)), (0.6 * k, 0.15 * k, 1.2 * k), body, rot=rot)
    box(name + "_skid", p + Vector((0, 0, -1.1 * k)), (3.6 * k, 1.9 * k, 0.12 * k), body, rot=rot)
    # cool rim so the dark hull reads against the city
    point(p + Vector((-3, 3, 5)), "#9fb4d8", 900, radius=2, name=name + "_rim")
    disc(name + "_lamp", 0.5 * k, 0.3, mat_emit("lamp_white", "#ffffff", 25), p + d * 2.4 * k + Vector((0, 0, -1.3 * k)))
    # rotor blur disc (GP) + nav lights
    mr = g.mat("rotor", "#d0dcee", 0.75, fill="#8090a8")
    # GP silhouette linework: hull outline so the dark airframe reads against the city
    ml = g.mat("heli_line", "#c8d6ea", 0.8)
    sd = Vector((-d.y, d.x, 0))
    hull = [p + d * 3.0 * k + sd * 0.5 * k, p + d * 2.1 * k + sd * 0.9 * k, p - d * 2.1 * k + sd * 0.9 * k, p - d * 6.0 * k + sd * 0.15 * k,
            p - d * 6.0 * k - sd * 0.15 * k, p - d * 2.1 * k - sd * 0.9 * k, p + d * 2.1 * k - sd * 0.9 * k, p + d * 3.0 * k - sd * 0.5 * k]
    g.stroke("heli", [v + Vector((0, 0, 0.8 * k)) for v in hull], 0.24, ml, 1.0, cyclic=True)
    ring = [p + Vector((0, 0, 1.05 * k)) + Vector((math.cos(t) * 5.2 * k, math.sin(t) * 5.2 * k, 0)) for t in [i * math.pi / 24 for i in range(48)]]
    g.stroke("rotor", ring, 0.1, mr, 0.55, cyclic=True, fill=True)
    for k in range(3):
        a = rng.uniform(0, math.pi * 2)
        g.stroke("rotor", [p + Vector((0, 0, 1.1 * k)), p + Vector((math.cos(a) * 5.2 * k, math.sin(a) * 5.2 * k, 1.1 * k))], 0.12, g.mat("blade", "#2a3140", 0.6), 0.5)
    disc(name + "_nr", 0.28, 0.2, mat_emit("nav_red", "harm", 40), p + d * 1.6 + Vector((0, -0.9, -0.6)))
    disc(name + "_nb", 0.28, 0.2, mat_emit("nav_blue", "siren_blue", 40), p + d * 1.6 + Vector((0, 0.9, -0.6)))
    point(p + Vector((0, 0, -2)), "harm", 2500, radius=0.5, name=name + "_red")
    point(p + Vector((2, 0, -2)), "siren_blue", 2500, radius=0.5, name=name + "_blue")
    # searchlight: real spot (lights the wet street) + a visible volumetric beam through the rain
    src = p + d * 2.4 * k + Vector((0, 0, -1.5 * k))
    spot(src, target, "#eef4ff", 3.0e6, angle=9, blend=0.35, radius=0.2, name=name + "_search", vol=3.0)
    L = (Vector(target) - src).length
    import bmesh as _bm
    bm = _bm.new()
    _bm.ops.create_cone(bm, cap_ends=False, segments=24, radius1=0.25, radius2=L * math.tan(math.radians(4.5)), depth=L)
    me = bpy.data.meshes.new(name + "_beam"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name + "_beam", me)
    ob.location = src + (Vector(target) - src) / 2
    ob.rotation_euler = (Vector(target) - src).to_track_quat("Z", "Y").to_euler()  # radius1 (thin) at the source
    me.materials.append(mat_volume("beam", 0.02, "#dfe8ff", emit="#dfe8ff", emit_str=0.22))
    link(ob)
    city.hide_depth.append(ob)
    # a bright pool where the cone lands
    t = Vector(target)
    pool = [t + Vector((math.cos(a) * 5.5, math.sin(a) * 5.5, 0.15)) for a in [i * math.pi / 16 for i in range(32)]]
    g.stroke("pool", pool, 0.25, g.mat("pool", "#eef4ff", 0.5), 0.6, cyclic=True)


helicopter("h1", Vector((18, -40, 50)), math.radians(140), (6, -30, 9))        # sweeps the lower highway
helicopter("h2", Vector((-50, 28, 38)), math.radians(-30), (-26, 8, 0))       # lights the street beside HQ
helicopter("h3", Vector((56, 26, 47)), math.radians(200), (40, 8, 12))

# drone swarms converging on the HQ
m_dr = mat_emit("drone_r", "harm", 30)
m_db = mat_emit("drone_b", "siren_blue", 30)
mtr = g.mat("dtrail_r", "harm", 0.6)
mtb = g.mat("dtrail_b", "siren_blue", 0.6)
for (cx, cy, cz, n) in ((10, -20, 38, 26), (-36, -8, 42, 22), (28, 34, 44, 24)):
    to_hq = (Vector((HQ[0], HQ[1], 36)) - Vector((cx, cy, cz))).normalized()
    for i in range(n):
        p = Vector((cx + rng.gauss(0, 5), cy + rng.gauss(0, 5), cz + rng.gauss(0, 2.5)))
        red = i % 2 == 0
        box("drone", p, (1.1, 1.1, 0.35), m_dr if red else m_db)
        tl = rng.uniform(3, 7)
        g.stroke("drones", [p - to_hq * tl, p], [0.02, 0.1], mtr if red else mtb, [0.0, 0.7])
    point(Vector((cx, cy, cz)), "harm", 3000, radius=3, name="swarm_r")
    point(Vector((cx + 3, cy, cz)), "siren_blue", 3000, radius=3, name="swarm_b")

# red/blue rim flicker on corp towers
tall = sorted([b for b in city.blocks if b[4] > 18], key=lambda b: -b[4])[:10]
m_rr = mat_emit("rim_red", "harm", 8)
m_rb = mat_emit("rim_blue", "siren_blue", 8)
for (x, y, w, d, hh) in tall:
    box("rimr", (x + w / 2 + 0.05, y - d / 2 - 0.05, hh / 2), (0.25, 0.25, hh), m_rr)
    box("rimb", (x - w / 2 - 0.05, y - d / 2 - 0.05, hh / 2), (0.25, 0.25, hh), m_rb)

# UI: Heat warning (glass, HARM) and a raid tag on the HQ
city.ui_panel(24, 24, 600, 150, title="HEAT // CORP SWEEP", edge="harm", rule="harm")
city.ui_text("82", 38, 96, 56, "harm", 4.0, ANTON)
city.ui_text("HUNTED", 120, 98, 42, "harm", 3.2, ANTON)
city.ui_text("3 AIR UNITS / 3 SWARMS / RAID IN 2", 318, 98, 16, "text_hi", 2.0)
city.ui_panel(38, 140, 572, 16, alpha=0.9, edge="#5a2a2a")
city.ui.append(rrect("heatfill", city.upx(468), city.upx(10), city.upx(2), city.cam_ui(40 + 234, 148, -19.85), mat_emit("heatfill", "harm", 4.0), rot=(0, 0, 0), parent=city.cam))
city.label_at((HQ[0], HQ[1], NET_Z), "HQ · RAID INBOUND 2 TURNS", "harm")
city.ui_panel(1560, 900, 336, 150, title="LEGEND")
city.ui_text("== CELL LINK (CLAIMED)", 1576, 960, 15, "acid", 2.0)
city.ui_text(">> CORP THREAT ROUTE", 1576, 990, 15, "#FF8C1A", 2.0)
city.ui_text("(!) AIR UNIT / SWARM", 1576, 1020, 15, "harm", 2.4)

compositor(bloom=1.0, bloom_thresh=1.1, streak=0.35, streak_thresh=3.5, distortion=-0.012, dispersion=0.006)
render(BASE + "_beauty.png")
city.export_fog(BASE + "_fog.json")
city.depth_pass(BASE + "_depth.png")
