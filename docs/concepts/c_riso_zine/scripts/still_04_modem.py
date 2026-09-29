"""Still 04: the Modem cyber shop. The vertical MODEM / CYBER SHOP neon sign is redrawn
as real bent tubes (feedback 2: the original sign's spirit; no BUY/SHRED paper stickers),
glass shop panels with zine stickers and marker verbs over washed system words.

blender -b --factory-startup --python still_04_modem.py -- <tex_dir> <out.png>
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
rng = random.Random(404)

R.reset()
R.setup(samples=64, world=(4, 5, 12), world_strength=0.6, glare_threshold=1.0, glare_strength=0.7, glare_size=0.55)
R.camera((0, 0, 17.8), (0, 0, 0), lens=40)
R.sun((-28, -22, 0), strength=2.4, angle=6)

# city far below behind vellum (same recede treatment as combat)
R.card("sky", "sky", width=30, loc=(0, 1.0, -7.0), mat=R.mat_card("sky", "sky", back=None, rough=1.0, sat=0.35, val=0.6))
for i, (z, y, w) in enumerate([(-6.0, 2.2, 28), (-5.0, 1.0, 26), (-4.0, -0.4, 24), (-3.0, -2.2, 22)]):
    R.card(f"city{i}", f"city_{i}", width=w, loc=(rng.uniform(-1, 1), y, z),
           mat=R.mat_card(f"cityc{i}", f"city_{i}", em=f"city_{i}_em", em_strength=0.45, back=None, sat=0.3, val=0.8))
R.card("vellum", "vellum", width=19.5, loc=(0, 0, -1.2), mat=R.mat_card("vellum", "vellum", back=None, blended=True, rough=1.0))
R.card("vellum2", "vellum", width=19.5, loc=(0.2, -0.1, -0.6), mat=R.mat_card("vellum2", "vellum", back=None, blended=True, rough=1.0, opacity=0.8))

# ------------------------------------------------------------------ the MODEM sign (neon tubes)
SX, SY = -6.35, -0.2
R.box("signboard", (2.75, 8.1, 0.14), (SX, SY, 0.07), R.mat_solid("signboard", (12, 12, 20), 0.6, spec=0.6))
pink_tube = R.mat_emit("tube_pink", R.C["pink"], 9.0)
cyan_tube = R.mat_emit("tube_cyan", R.C["cyan"], 8.0)
trace_m = R.mat_emit("trace_pink", R.C["pink"], 3.0)
dead_m = R.mat_solid("tube_glass", (60, 40, 60), 0.2, spec=1.0)


def tube_letter(ch, x, y, s, mat, r, z=0.32, wide=1.0):
    for st in R.FONT[ch]:
        pts = [(x + (px - 0.33) * s * wide, y + (py - 0.5) * s, z) for (px, py) in st]
        R.tube(f"t_{ch}_{x:.2f}_{y:.2f}", pts, r, mat)
        # the unlit glass holder under the tube, offset so it reads as a bent tube on clips
        R.tube(f"h_{ch}_{x:.2f}_{y:.2f}", [(p[0] + 0.03, p[1] - 0.03, z - 0.12) for p in pts], r * 1.1, dead_m)


# frame: a rounded neon rectangle
fr = []
w2, h2, rr = 1.22, 3.9, 0.35
for (cx, cy, a0) in [(w2 - rr, h2 - rr, 0), (-w2 + rr, h2 - rr, 90), (-w2 + rr, -h2 + rr, 180), (w2 - rr, -h2 + rr, 270)]:
    for k in range(9):
        a = math.radians(a0 + 90 * k / 8)
        fr.append((SX + cx + rr * math.cos(a), SY + cy + rr * math.sin(a), 0.3))
fr.append(fr[0])
R.tube("frame", fr, 0.045, pink_tube)
for i, ch in enumerate("MODEM"):
    tube_letter(ch, SX, SY + 3.05 - i * 1.12, 0.92, pink_tube, 0.06, wide=1.55)
for i, ch in enumerate("CYBER"):
    tube_letter(ch, SX - 0.88 + i * 0.44, SY - 2.75, 0.42, cyan_tube, 0.035, wide=0.85)
for i, ch in enumerate("SHOP"):
    tube_letter(ch, SX - 0.66 + i * 0.44, SY - 3.35, 0.42, cyan_tube, 0.035, wide=0.85)
# circuit traces around the letters (orthogonal runs ending in solder rings)
for k in range(16):
    side = -1 if k % 2 == 0 else 1
    y0 = SY + 3.4 - k * 0.37
    x0 = SX + side * 1.05
    x1 = SX + side * rng.uniform(0.62, 0.8)
    y1 = y0 + rng.uniform(-0.25, 0.25)
    pts = [(x0, y0, 0.24), (x1 + side * 0.1, y0, 0.24), (x1, y1, 0.24)]
    R.tube(f"tr{k}", pts, 0.014, trace_m)
    R.torus(f"sol{k}", 0.045, 0.012, (x1, y1, 0.24), trace_m, seg=24)
# neon spill onto the shop glass and paper next to it (feedback 10)
R.point((SX + 0.5, SY + 1.5, 1.4), R.C["pink"], power=260, radius=1.0)
R.point((SX + 0.5, SY - 3.0, 1.2), R.C["cyan"], power=90, radius=0.8)


# ------------------------------------------------------------------ glass shop panels
def glass(name, tex, w, loc):
    return R.card(name, tex, width=w, loc=loc, mat=R.mat_card(name, tex, em=tex, em_strength=0.85, rough=0.25, back=None))


glass("head", "gl_head", 6.6, (0.2, 3.45, 0.04))
glass("chips", "gl_chips", 4.4, (-1.95, 1.3, 0.05))
glass("cards", "gl_cards", 5.4, (3.9, 1.05, 0.05))
glass("slices", "gl_slices", 4.4, (-1.95, -1.55, 0.05))
glass("remove", "gl_remove", 4.4, (3.2, -2.55, 0.05))
glass("purchase", "wash_purchase", 3.2, (-1.95, -3.55, 0.05))
glass("disconnect", "wash_disconnect", 3.3, (6.1, -3.75, 0.05))

# top tags
for i in range(5):
    R.card(f"tag{i}", f"tag_{i}", width=1.1, loc=(-2.4 + i * 1.18, 4.05, 0.25), rot=(0, 0, rng.uniform(-3, 3)))
R.card("tapeh", "tape_3", width=0.5, loc=(-2.3, 4.35, 0.32), rot=(0, 0, -9), mat=R.mat_card("tape3", "tape_3", blended=True, back=None, rough=0.4))

# shop cards: stickers slapped onto the glass, price stickers slapped onto them
for i, (tex, x, rot, price) in enumerate([("card_5", 2.35, -5, "stk_price1"), ("card_4", 3.95, 3, "stk_price2"), ("card_3", 5.55, -2, "stk_price3")]):
    ob = R.card(f"shop_{tex}", tex, width=1.35, loc=(x, 0.85, 0.35 + i * 0.02), rot=(0, 0, rot), nx=14, ny=14)
    if i == 1:
        R.peel(ob, (-1, 1), 0.2, 50)
    R.card(f"pr{i}", price, width=0.85, loc=(x + 0.25, 0.0, 0.5 + i * 0.02), rot=(0, 0, rng.uniform(-14, 10)))

# a tiny spinner on the remove panel: stacked discs, like combat
R.disc("mini_plate", 0.95, 0, 0.04, loc=(5.0, -2.55, 0.1), edge=(20, 20, 26), top_mat=R.mat_solid("plate", (16, 16, 22), 0.8))
R.disc("mini_slices", 0.78, 0.48, 0.04, tex="sp_slices_op", r_tex=0.81, loc=(5.0, -2.55, 0.26), rot_z=20, edge=(250, 248, 240))
R.card("mini_hub", "stk_fist", width=0.8, loc=(5.0, -2.55, 0.4))

# zine stickers slapped over the glass
for (tex, x, y, w, rot, pl) in [("stk_nofuture", 1.0, -0.35, 2.0, -8, False), ("stk_nope", -3.55, -0.2, 1.2, 14, True),
                                ("stk_cell", 0.9, 2.95, 1.7, 4, False), ("stk_skull", -0.35, -2.45, 0.6, -20, False),
                                ("stk_hot", 7.25, 2.95, 1.05, 12, False)]:
    ob = R.card(f"z_{tex}", tex, width=w, loc=(x, y, 0.55), rot=(0, 0, rot), nx=16, ny=16)
    if pl:
        R.peel(ob, (1, -1), 0.3, 60)

# ------------------------------------------------------------------ marker verbs over system words
mk = R.Marker("marker", z=1.6, seed=44)
mk.words("GRAB IT", -1.95, -3.72, 0.5, rot=4, anchor="center", weight=0.12, drips=[(0, 0.4, "form"), (3, 0.55, "form")])
mk.words("BAIL", 6.1, -3.95, 0.55, rot=-6, anchor="center", weight=0.13, drips=[(1, 0.45, "form"), (3, 0.3, "form")])
mk.circle(3.95, 0.95, 0.95, 1.2, r=0.028)
mk.words("THIS ONE", 3.1, 2.45, 0.3, rot=3, weight=0.1)
mk.arrow((4.6, 2.5), (4.2, 2.05), bend=0.3, r=0.024, head=0.18)

R.render(OUT)
