"""Still 01: combat. Two lit spinners on a dark console over a rain-blurred silhouette city."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rn_lib import *  # noqa
from rn_parts import *  # noqa

OUT = out_arg(os.path.join(STILLS, "_raw_01_combat.png"))
SAMPLES = int(os.environ.get("RN_SAMPLES", "32"))
reset(samples=SAMPLES)
world("#010203", 1.0, vol_density=0.0025, vol_color="#8494ab", aniso=0.5)
sun((math.radians(-62), 0, math.radians(8)), "#9fb2d0", 0.35, name="backlight")  # moonlit haze, rims roofs from behind
front_camera(50, fstop=0.12)

gp_back = GP("gp_back")    # rain behind the UI, city linework
gp_ui = GP("gp_ui")        # panel edges, fx
gp_mk = GP("gp_marker")    # marker ink (unlit, excluded from spill)

# ---------------------------------------------------------------- city silhouette (recedes: mono, dim, blurred)
wm = [mat_windows("cw%d" % i, wall="#0a0d13", lit=("#8fa3bd", "#b9aa92"), density=0.2 + 0.05 * i, strength=1.0, scale=2.0 + i * 0.4, seed=i * 3.1) for i in range(3)]


def skyline_h(x, y, rng):
    half = 5.4 * (CAM_D + y) / CAM_D          # visible half-height at that depth
    return max(3.0, rng.uniform(-0.35, 0.72) * half + 5.8)


blocks = city_blocks(11, (-95, 95), (40, 260), 170, 0, 0, 5, 16, wm, z0=-5.8, hfn=skyline_h,
                     lines=None)
# a few far neon signs, dim (the only colour left in the city)
for i, (cx, cy, h, c) in enumerate([(-38, 120, 9, "#8a3a66"), (44, 150, 12, "#2f6f85"), (-70, 210, 14, "#6a5a2a"), (18, 190, 8, "#5a2f70")]):
    box("sign%d" % i, (cx, cy - 6, 4 + i * 5), (1.2, 0.3, h), mat_emit("sign%d" % i, c, 3.0))
# hologram ad flickering on a facade
holo = rrect("holo_ad", 14, 20, 0.2, (-24, 88, 14), mat_holo("holo_ad", "#3d8fb0", 2.2, seed=4.0, bands=90), rot=(R90, 0, 0))
# searchlight shafts in the haze far behind
spot((-30, 160, 70), (-10, 110, -5), "#b8c8e0", 250000, angle=6, blend=0.4, name="heli_beam")
spot((55, 200, 60), (35, 150, -5), "#b8c8e0", 180000, angle=5, blend=0.4, name="heli_beam2")
for i in range(5):
    spot((-60 + i * 30, 70 + i * 17, 16), (-60 + i * 30, 70 + i * 17, -6), "#e0c8a0" if i % 2 else "#a8c0e0", 9000, angle=35, blend=0.8, name="street%d" % i)
# local haze pockets (patchy)
for i, (x, y, z, s) in enumerate([(-20, 60, -2, 18), (25, 90, 2, 24), (-55, 130, 5, 30), (60, 55, -3, 16)]):
    ob = disc("haze%d" % i, 1, 1, mat_volume("haze%d" % i, 0.05, "#7c8aa0", noise_scale=1.8, seed=i), (x, y, z))
    ob.scale = (s, s * 0.7, s * 0.45)

# wet ground plane (reflects spinner glow and neon)
sky_glow("sky", (0, 330, 124), 900, 260, low="#3a4e6c", strength=2.2)
wet_ground("ground", (0, 150, -5.8 - 0.05), (400, 320, 0.1))
splashes(gp_back, 500, 5, (-30, 30), (2, 60), -5.8, size=(0.05, 0.25))

# ---------------------------------------------------------------- lights for the console
area((0, -14, 9), (math.radians(55), 0, 0), "#b9c9e4", 900, size=18, size_y=4, name="fill")          # cool monitor fill
area((-6.2, -7, 6.5), (math.radians(40), 0, math.radians(-20)), "#e8f0ff", 500, size=3.0, size_y=0.5, name="softbox_L")  # dome highlight
area((6.8, -7, 6.5), (math.radians(40), 0, math.radians(20)), "#e8f0ff", 500, size=3.0, size_y=0.5, name="softbox_R")
area((0, 6, 7), (math.radians(-60), 0, 0), "#9fb4d8", 1500, size=20, size_y=2, name="rim_back")   # rim from behind/above

# ---------------------------------------------------------------- spinners
op_slices = [("atk", 5, 6), ("def", 4, 5), ("atk", 5, 6), ("crit", 3, 12), ("atk", 5, 8), ("def", 4, 6), ("evd", 4, 2)]
en_slices = [("afl", 4, 14), ("atk", 5, 6), ("def", 5, 6), ("atk", 5, 8), ("def", 4, 6), ("atk", 4, 8), ("miss", 3, 0)]
spinner("op", 590, 470, 178, op_slices, "pink", "rivets", "BREAKER", "breaker core", tilt=(13, 7), spill=700, hp=(60, 60))
spinner("en", 1330, 470, 178, en_slices, "violet", "rings", "COLLECTIONS", "halcyon civic", tilt=(13, -7), spill=650, hp=(26, 40), rot_offset_ticks=2)

# HP numbers under the wheels
ui_text("60/60", 590, 770, 34, "gain", 3.0, ANTON, "CENTER", depth=-0.2)
ui_text("26/40", 1330, 770, 34, "amber", 3.0, ANTON, "CENTER", depth=-0.2)
ui_text("-14", 1105, 330, 58, "harm", 6.0, ANTON, "CENTER", depth=-0.8)

# ---------------------------------------------------------------- binary shards off the hit (enemy wheel, left rim)
shards(gp_ui, (1152, 420), 70, 21, depth=-0.3, spread=(30, 420), dir_deg=165, cone=150)

# ---------------------------------------------------------------- glass UI
glass_panel(gp_ui, "p_top", 0, 0, 1920, 46, depth=0.3, title=None, alpha=0.9, rough=0.6)
ui_text("TURN 2  //  NUDGE YOUR WHEEL  ·  Q/E", 22, 23, 17, "text_mid", 1.4, depth=0.25)
ui_text("HEAT 18  COOL", 1560, 23, 17, "text_mid", 1.4, depth=0.25)
ui_text("[ESC]", 1850, 23, 17, "text_lo", 1.2, depth=0.25)
glass_panel(gp_ui, "p_fc_op", 400, 76, 380, 84, depth=0.2, title="IF YOU SEND IT")
ui_text("DEFEND · HALF POWER   +3 BLOCK", 414, 134, 18, "cyan", 2.2, depth=0.15)
glass_panel(gp_ui, "p_fc_en", 1140, 76, 380, 84, depth=0.2, title="ENEMY INTENT", rule="violet")
ui_text("AFFLICT · CORRUPT   14", 1154, 134, 18, "afflict", 2.4, depth=0.15)
glass_panel(gp_ui, "p_log", 1660, 180, 240, 300, depth=0.25, title="SYS.LOG")
for i, l in enumerate(["> tick 07 ATK 6", "> tick 12 CRIT 12", "> shield 0", "> corrupt pending", "> heat +2", "> ..."]):
    ui_text(l, 1674, 240 + i * 30, 15, "text_lo", 1.3, depth=0.2)

# SEND IT over a washed-out digital EXECUTE (feedback 9)
glass_panel(gp_ui, "p_exec", 1520, 918, 360, 118, depth=0.15, edge="#3a5a70")
ui_text("EXECUTE", 1700, 978, 62, "#8aa4bf", 0.9, MONO, "CENTER", depth=0.1)
ui_text("[SPACE]", 1862, 1022, 14, "text_lo", 1.0, MONO, "RIGHT", depth=0.1)
marker(gp_mk, "SEND IT", 1478, 1012, 66, depth=-0.3, seed=11, angle_deg=-4, drips={"stage": "forming", "count": 4})

# ---------------------------------------------------------------- hand of cards slapped on as stickers (feedback 8)
cards = [("JOLT", 1, "Spin a wheel 3 ticks."), ("FINE TUNE", 1, "+-1 nudge, one ring."), ("BRUTE SPIN", 2, "Spin 6. Lock 1."),
         ("JOLT", 1, "Spin a wheel 3 ticks."), ("MIRROR", 3, "Flip a wheel.")]
xs = [120, 290, 470, 650, 820]
rots = [-3, 2, -8, 3, -2]
for i, ((t, c, d), x, r) in enumerate(zip(cards, xs, rots)):
    slap = i == 2
    sticker_card(gp_ui, "card%d" % i, x, 952 - (18 if slap else 0), 150 * (1.14 if slap else 1), 200 * (1.14 if slap else 1), r, t, c,
                 accent="pink" if i != 1 else "cyan", desc=d, depth=-0.1 - (0.5 if slap else 0) - i * 0.01, slap=slap, seed=i + 2)
ui_text("RAM 3/5", 60, 834, 15, "text_mid", 1.4, depth=0.1)

# ---------------------------------------------------------------- rain (mostly behind the UI plane, sparse in front)
rain(gp_back, 2600, 1, (-60, 60), (4, 120), (-6, 30), length=(2.0, 6.0), radius=(0.006, 0.018), alpha=(0.08, 0.3))
rain(gp_ui, 90, 2, (-10, 10), (-8, -2), (-5, 5), length=(0.4, 1.0), radius=(0.004, 0.01), alpha=(0.08, 0.22))
# beads of rain on the glass UI plane
rng = random.Random(9)
mb = gp_ui.mat("bead", "#d6e6ff", 0.5)
for _ in range(160):
    x, y = rng.uniform(0, 1920), rng.uniform(60, 880)
    p = P(x, y, -0.05)
    L = S(rng.uniform(4, 40), -0.05)
    gp_ui.stroke("beads", [p, p + Vector((0, 0, -L))], [S(1.8, 0), S(1.2, 0)], mb, rng.uniform(0.15, 0.4))

compositor(bloom=0.8, bloom_thresh=1.0, streak=0.3, streak_thresh=3.0)
render(OUT)
