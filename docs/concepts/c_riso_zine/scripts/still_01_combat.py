"""Still 01: combat. Multiplane paper stack seen from above.

blender -b --factory-startup --python still_01_combat.py -- <tex_dir> <out.png>
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import riso_bpy as R

argv = sys.argv[sys.argv.index("--") + 1:]
R.init(argv[0])
OUT = argv[1]
rng = random.Random(101)

R.reset()
R.setup(samples=64, world=(4, 5, 12), world_strength=0.6, glare_threshold=1.0, glare_strength=0.55, glare_size=0.5)
R.camera((0, 0, 17.8), (0, 0, 0), lens=40)
R.sun((-28, -22, 0), strength=2.6, angle=6)

# --- the city, far below, behind two vellum sheets (feedback 3: desaturated, dim, receding)
R.card("sky", "sky", width=30, loc=(0, 1.0, -7.0), mat=R.mat_card("sky", "sky", back=None, rough=1.0, sat=0.35, val=0.6))
for i, (z, y, w) in enumerate([(-6.0, 2.2, 28), (-5.0, 1.0, 26), (-4.0, -0.4, 24), (-3.0, -2.2, 22)]):
    R.card(f"city{i}", f"city_{i}", width=w, loc=(rng.uniform(-1, 1), y, z),
           mat=R.mat_card(f"cityc{i}", f"city_{i}", em=f"city_{i}_em", em_strength=0.45, back=None, sat=0.3, val=0.8))
R.card("vellum", "vellum", width=19.5, loc=(0, 0, -1.2), mat=R.mat_card("vellum", "vellum", back=None, blended=True, rough=1.0))
R.card("vellum2", "vellum", width=19.5, loc=(0.2, -0.1, -0.6), mat=R.mat_card("vellum2", "vellum", back=None, blended=True, rough=1.0, opacity=0.8))


# --- spinners: stacked cut-paper discs with gaps, so each layer shadows the one below
def spinner(cx, cy, who, rot, s=0.9):
    R.disc(f"{who}_plate", 2.55 * s, 0, 0.06, loc=(cx, cy, 0.0), edge=(20, 20, 26), top_mat=R.mat_solid("plate", (16, 16, 22), 0.8))
    R.disc(f"{who}_bezel", 2.45 * s, 1.96 * s, 0.10, tex=f"sp_bezel_{who}", r_tex=2.45 * s, loc=(cx, cy, 0.07), edge=(40, 40, 50))
    R.disc(f"{who}_slices", 1.92 * s, 1.2 * s, 0.05, tex=f"sp_slices_{who}", r_tex=2.0 * s, loc=(cx, cy, 0.34), rot_z=rot, edge=(250, 248, 240))
    R.disc(f"{who}_inner", 1.17 * s, 0.64 * s, 0.05, tex=f"sp_inner_{who}", r_tex=1.9 * s, loc=(cx, cy, 0.52), edge=(250, 248, 240))
    R.card(f"{who}_hub", f"sp_hub_{who}", width=1.52 * s, loc=(cx, cy, 0.70), rot=(0, 0, rng.uniform(-8, 8)))
    R.lens(f"{who}_lens", 2.0 * s, 0.5, (cx, cy, 0.26))
    rim_col = R.C["cyan"] if who == "op" else R.C["orange"]
    R.torus(f"{who}_rim", 2.5 * s, 0.03, (cx, cy, 0.14), R.mat_emit(f"rim_{who}", rim_col, 3.2))
    R.cone(f"{who}_ptr", 0.2, 0.0, 0.1, (cx, cy + 2.6 * s, 0.9), (0, 0, 0), R.mat_emit("acid_ptr", R.C["acid"], 2.2), seg=3)
    # light spill from the glowing rim onto the glass and paper around it (feedback 10)
    R.point((cx, cy, 1.3), rim_col, power=110, radius=1.2)
    return s


OPX, OPY, ENX, ENY = -3.7, 0.15, 3.3, 0.2
s = spinner(OPX, OPY, "op", -8)
spinner(ENX, ENY, "en", -90)   # the enemy CRIT slice sits under the pointer: that's the hit
R.arc_tube("hp_op", 2.62 * s, 0.05, 205, 335, (OPX, OPY, 0.12), R.mat_emit("hp_op", R.C["gain"], 4.0))
R.arc_tube("hp_en", 2.62 * s, 0.05, 250, 335, (ENX, ENY, 0.12), R.mat_emit("hp_en", R.C["amber"], 4.0))
R.arc_tube("hp_en_lost", 2.62 * s, 0.028, 205, 248, (ENX, ENY, 0.12), R.mat_solid("hp_lost", (90, 34, 28), 0.9))

# the enemy wheel is plastered with the collector's stickers
for (tex, dx, dy, w, rot, pl) in [("stk_comply", -1.45, -0.6, 1.05, 34, False), ("stk_barcode", 1.25, -0.85, 0.75, -32, True),
                                  ("stk_eye", 1.45, 0.55, 0.58, 12, False), ("stk_payup", 0.1, -1.55, 0.95, -6, True),
                                  ("stk_skull", -1.55, 0.55, 0.46, -18, False)]:
    ob = R.card(tex + "_w", tex, width=w, loc=(ENX + dx, ENY + dy, 0.42 + rng.uniform(0, 0.03)), rot=(0, 0, rot), nx=16, ny=16)
    if pl:
        R.peel(ob, (1, -1), 0.28, 60)

# --- glass UI: lit (catches spill) and self-lit like a screen
def glass(name, tex, w, loc):
    R.card(name, tex, width=w, loc=loc, mat=R.mat_card(name, tex, em=tex, em_strength=0.85, rough=0.25, back=None))


glass("fc_op", "gl_fc_op", 4.2, (OPX, 2.98, 0.05))
glass("fc_en", "gl_fc_en", 4.2, (ENX, 2.98, 0.05))
glass("turn", "gl_turn", 8.0, (-3.2, 3.6, 0.03))
glass("execute", "wash_execute", 4.3, (5.35, -3.35, 0.05))

# --- paper: top tags with tape, the Heat poster
for i in range(6):
    x = -7.25 + i * 1.28
    R.card(f"tag{i}", f"tag_{i}", width=1.2, loc=(x, 4.02 - (i % 2) * 0.05, 0.25 + i * 0.01), rot=(0, 0, rng.uniform(-3.5, 3.5)))
    if i in (0, 3, 5):
        R.card(f"tape{i}", f"tape_{i % 4}", width=0.5, loc=(x + 0.1, 4.33, 0.32), rot=(0, 0, rng.uniform(-12, 12)),
               mat=R.mat_card(f"tape{i % 4}", f"tape_{i % 4}", blended=True, back=None, rough=0.4))
R.card("poster", "poster_heat", width=1.15, loc=(7.3, 0.2, 0.3), rot=(0, 0, 5))
R.card("posttape", "tape_1", width=0.55, loc=(7.25, 0.95, 0.36), rot=(0, 0, -8), mat=R.mat_card("tape1", "tape_1", blended=True, back=None, rough=0.4))

# --- hand of cards, slapped on as stickers (feedback 8): angles, overlaps, one mid-slap
hand = [("card_0", -7.0, -3.25, 7, 0.9), ("card_1", -5.8, -3.35, -4, 0.95), ("card_2", -4.6, -3.25, 3, 1.0),
        ("card_3", -3.4, -3.33, -6, 1.05), ("card_4", -2.2, -3.27, 5, 1.1)]
for i, (tex, x, y, rot, z) in enumerate(hand):
    ob = R.card(tex, tex, width=1.12, loc=(x, y, z), rot=(0, 0, rot), nx=18, ny=18)
    if i == 2:
        R.peel(ob, (1, 1), 0.22, 55)
ob = R.card("card_5", "card_5", width=1.12, loc=(-0.75, -3.05, 2.3), rot=(10, -14, -14), nx=18, ny=18)
R.peel(ob, (-1, -1), 0.3, 40)

# --- the hit: CRIT lands under the enemy pointer, binary shards burst out (feedback 5)
hx, hy = ENX, ENY + 1.5 * s + 0.1
R.card("dmg", "stk_dmg", width=1.2, loc=(ENX + 2.35, ENY + 1.95, 1.3), rot=(0, 0, -12))
for k in range(46):
    a = math.radians(rng.uniform(15, 165))
    d = rng.uniform(0.35, 2.6)
    z = 0.9 + d * rng.uniform(0.3, 1.0)
    sz = rng.uniform(0.13, 0.32) * (1 + z * 0.1)
    tex = f"shard_{rng.randrange(4)}"
    R.card(f"sh{k}", tex, width=sz, loc=(hx + math.cos(a) * d * 1.3, hy + math.sin(a) * d * 0.55, z),
           rot=(rng.uniform(-40, 40), rng.uniform(-40, 40), rng.uniform(-60, 60)),
           mat=R.mat_card(tex + "_m", tex, em=tex + "_em", em_strength=1.6, back=(240, 240, 240)))
R.point((hx, hy, 1.2), R.C["pink"], power=70, radius=0.4)

# --- the marker (Grease Pencil): SEND IT over the washed EXECUTE (feedback 9) + hand marks
mk = R.Marker("marker", z=1.6, seed=7)
mk.words("SEND IT", 5.3, -3.62, 0.82, rot=5, anchor="center", weight=0.12, drips=[(0, 0.42, "form"), (2, 0.62, "form"), (3, 0.3, "form"), (5, 0.5, "form")])
mk.circle(hx, hy + 0.02, 0.55, 0.38, r=0.026)
mk.arrow((-0.9, 2.35), (1.0, 1.85), bend=-0.25, r=0.028, head=0.28)
mk.words("NOW", -1.45, 2.4, 0.38, rot=4, weight=0.08)

R.render(OUT)
