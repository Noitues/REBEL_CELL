"""05 shop: a black-market stall diorama (awning, neon sign, robot fence behind the counter)
with cards and spinner parts for sale, hanging price tags, credits and a LEAVE button.
Transparent film; post.py lays it over the blurred night city.

usage: blender -b --factory-startup --python scene_shop.py -- <out.png> [samples]
"""
import os
import sys
import math
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_props as Pr
from tt_props import PAL, px, sub, label

args = T.arg_list()
OUT = args[0] if args else os.path.join(T.OUT_ROOT, "stills", "_shop_fg.png")
SAMPLES = int(args[1]) if len(args) > 1 else 32

sc = T.reset()
T.MODE["name"] = "day"
T.MODE["fake"] = (-0.45, -1.0, 0.75)
T.setup_render(sc, samples=SAMPLES, transparent=True, line=3.2)
T.compositor(sc, bloom=(0.95, 0.8, 7))
cam = T.camera((0, -30, 0), (0, 0, 0), lens=50)
ui = Pr.ui_root(cam, depth=30.0)
rng = random.Random(1337)
F = "ui"


def P(o, g):
    o.parent = g
    return o


# ---------------------------------------------------------------- the stall (ground plane group)
st = sub(ui, (*px(960, 840), -2.5), rot=(-80, 0, 0), scale=1.08, name="stall")
Pr.ground_base(st, 6.9, 2.5, (0, 0.4, 0), rng, top="#4f5566", side="#6b4630", fake=F, tufts=22, rocks=5)
# back wall of planks + shelves
for i in range(9):
    x = -4.8 + i * 1.2
    P(T.box((1.18, 0.25, 4.2 + rng.uniform(-0.15, 0.15)), (x, 2.0, 0.0), T.paint("#7a4a2c" if i % 2 else "#8a5634", fake=F,
          streak_axis=2, streak=20, stroke=0.3), bev=0.05, wonk=0.03, rng=rng), st)
for zz in (1.9, 3.1):
    P(T.box((10.4, 0.6, 0.14), (0, 1.75, zz), T.paint(PAL["wood_d"], fake=F, streak_axis=0, streak=20), bev=0.04), st)
# shelf clutter: jars, boxes, glowing chips
for i in range(16):
    zz = 1.9 + 0.14 if i < 8 else 3.1 + 0.14
    x = -4.6 + (i % 8) * 1.25 + rng.uniform(-0.2, 0.2)
    k = rng.random()
    if k < 0.4:
        P(T.cyl(0.22, 0.5, (x, 1.7, zz), T.paint(rng.choice(["#4ff0ff", "#9ee03a", "#ff4fb8"]), fake=F, gloss=0.8),
                verts=10, bev=0.04), st)
        P(T.cyl(0.24, 0.1, (x, 1.7, zz + 0.5), T.paint(PAL["iron"], fake=F), verts=10, bev=0.02), st)
    elif k < 0.75:
        P(T.box((0.6, 0.45, 0.4), (x, 1.7, zz), T.paint(rng.choice(["#c8a068", "#8f9a6a", "#a86a3a"]), fake=F),
                bev=0.04, wonk=0.05, rng=rng, rot=(0, 0, rng.uniform(-12, 12))), st)
    else:
        P(T.box((0.5, 0.1, 0.35), (x, 1.75, zz), T.glow(rng.choice(["#4ff0ff", "#ffd24f"]), 2.5), bev=0.02), st)
# posts + striped awning
for x in (-5.5, 5.5):
    P(T.box((0.35, 0.35, 5.9), (x, -0.2, 0.0), T.paint(PAL["wood"], fake=F, streak_axis=2, streak=22), bev=0.05,
            wonk=0.03, rng=rng), st)
for i in range(8):
    x = -5.6 + i * 1.6 + 0.8
    col = "#9a5ee0" if i % 2 else "#27b5ad"
    P(T.box((1.62, 2.8, 0.16), (x, 0.6, 5.65), T.paint(col, fake=F, stroke=0.25, streak_axis=1), bev=0.05,
            rot=(-24, 0, 0), wonk=0.02, rng=rng), st)
    # valance strip + scalloped edge hanging at the front
    P(T.box((1.6, 0.14, 0.7), (x, -0.85, 4.85), T.paint(col, fake=F, stroke=0.25), bev=0.04, wonk=0.02, rng=rng), st)
    P(T.prism(Pr.sector_poly(0.0, 0.5, math.pi, 2 * math.pi, 10), 0.14, (x, -0.78, 4.87), T.paint(col, fake=F),
              bev=0.03, rot=(90, 0, 0)), st)
# counter
P(T.box((10.6, 1.5, 1.35), (0, -0.4, 0.0), T.paint("#8a5634", fake=F, pattern="plank", pat_scale=1.3, streak_axis=0,
        streak=18), bev=0.08, wonk=0.01, rng=rng), st)
P(T.box((11.0, 1.8, 0.2), (0, -0.4, 1.35), T.paint("#5b3a26", fake=F, streak_axis=0, streak=24), bev=0.06), st)
for x in (-5.0, -1.8, 1.8, 5.0):
    P(T.box((0.25, 0.1, 1.3), (x, -1.18, 0.02), T.paint(PAL["brass"], fake=F, gloss=0.6), bev=0.03), st)
# crates + barrel at the sides
P(T.box((1.1, 1.0, 0.9), (-6.3, -1.2, 0.0), T.paint("#b07a44", fake=F, pattern="plank"), bev=0.06, wonk=0.05, rng=rng,
        rot=(0, 0, 12)), st)
P(T.box((0.8, 0.8, 0.7), (-6.1, -1.1, 0.9), T.paint("#c28a50", fake=F, pattern="plank"), bev=0.06, wonk=0.05, rng=rng,
        rot=(0, 0, -8)), st)
P(T.cyl(0.55, 1.2, (6.4, -1.0, 0.0), T.paint("#3f86c8", fake=F, gloss=0.4), verts=16, bev=0.06), st)
P(T.cyl(0.58, 0.1, (6.4, -1.0, 0.3), T.paint(PAL["iron"], fake=F), verts=16, bev=0.02), st)
P(T.cyl(0.58, 0.1, (6.4, -1.0, 0.95), T.paint(PAL["iron"], fake=F), verts=16, bev=0.02), st)

# robot fence behind the counter (boxy body, CRT head with a painted face, hood)
rb = sub(st, (0, 0.9, 1.3), name="robot")
P(T.box((1.8, 1.0, 1.5), (0, 0, 0), T.paint("#6b7a88", fake=F, gloss=0.4), bev=0.12, wonk=0.03, rng=rng, taper=0.12), rb)
P(T.box((2.1, 1.3, 1.7), (0, 0, 1.55), T.paint("#3a3548", fake=F), bev=0.2, wonk=0.03, rng=rng, taper=0.1), rb)
P(T.box((1.6, 0.2, 1.1), (0, -0.62, 1.85), T.glow("#1f3a3a", 1.0), bev=0.08), rb)
for sx in (-1, 1):
    P(T.box((0.28, 0.1, 0.34), (sx * 0.38, -0.74, 2.5), T.glow("#6bffb8", 3.5), bev=0.04), rb)
P(T.box((0.7, 0.1, 0.12), (0, -0.74, 2.02), T.glow("#6bffb8", 3.5), bev=0.03, rot=(0, 8, 0)), rb)
P(T.cyl(0.05, 0.9, (0.6, 0, 3.2), T.paint(PAL["steel"], fake=F), verts=6, bev=0), rb)
P(T.cyl(0.14, 0.14, (0.6, 0, 4.1), T.glow("#ff4fb8", 5), verts=10, bev=0.02), rb)
for sx in (-1, 1):
    P(T.box((0.35, 0.35, 1.1), (sx * 1.15, -0.1, 0.4), T.paint("#6b7a88", fake=F), bev=0.08, rot=(0, sx * -25, 0)), rb)

# hanging lanterns + cable
for x in (-3.6, 3.6):
    P(T.cyl(0.03, 0.6, (x, -0.6, 3.7), T.paint(PAL["ink"], fake=F), verts=5, bev=0), st)
    P(T.cyl(0.3, 0.5, (x, -0.6, 3.25), T.glow("#ffb54f", 3.0), verts=10, bev=0.06), st)
    P(T.cyl(0.34, 0.1, (x, -0.6, 3.72), T.paint("#c0392b", fake=F), verts=10, bev=0.02), st)

# ---------------------------------------------------------------- shop sign
sg = sub(ui, (*px(960, 96), 0.5), rot=(0, 0, -1.5), name="sign")
Pr.plaque(sg, 7.6, 1.4, (0, 0, 0), col="#2c2433", trim=PAL["brass"], rng=rng, depth=0.3)
label(sg, "BLACK MARKET", 0.95, (0, 0.05, 0.3), "#ff5fd0", fnt="title", extrude=0.1)
label(sg, "no questions  -  no refunds", 0.24, (0, -0.55, 0.3), "#6bffb8", fnt="title", thin=True)
for sx in (-1, 1):
    P(T.cyl(0.05, 1.3, (sx * 3.2, 0.7, -0.1), T.paint(PAL["iron"], fake=F), verts=6, bev=0), sg)

# ---------------------------------------------------------------- goods
def price_tag(x, y, name, price, rot=0.0):
    g = sub(ui, (*px(x, y), 1.4), rot=(0, 0, rot), name="tag")
    P(T.cyl(0.03, 0.5, (0, 0.55, -0.05), T.paint(PAL["ink"], fake=F), verts=5, bev=0), g)
    Pr.plaque(g, 1.75, 0.95, (0, 0, 0), col="#e9d3a0", trim=PAL["wood_d"], rng=random.Random(int(x)), bolts=False,
              depth=0.16)
    label(g, name, 0.21, (0, 0.2, 0.12), "#3a2418", fnt="title", lined=False)
    P(T.cyl(0.17, 0.08, (-0.42, -0.17, 0.1), T.paint("#f2c230", fake=F, gloss=0.8), verts=16, bev=0.02), g)
    label(g, "c", 0.2, (-0.42, -0.2, 0.2), "#7a4a10", fnt="sign", lined=False)
    label(g, str(price), 0.38, (0.12, -0.2, 0.1), "#3a2418", fnt="sign", thin=True)
    return g


cards = [("OVERCLOCK", 1, "Spin your wheel\n+3 on red slices.", PAL["atk"], Pr.icon_bolt, "ATTACK", 45),
         ("FIREWALL", 1, "Gain 6 block.\nBlue slices +2.", PAL["def"], Pr.icon_shield, "DEFEND", 38),
         ("GLITCH", 1, "Swap two enemy\nslices.", PAL["glitch"], Pr.icon_chip, "HACK", 60)]
for i, (t, c, d, col, ic, kind, price) in enumerate(cards):
    x = 330 + i * 190
    Pr.card(ui, t, c, d, col, (*px(x, 520), 1.0), rot=(0, 0, (i - 1) * -4), icon=ic, kind=kind,
            rng=random.Random(i + 20), name="card_%d" % i)
    price_tag(x, 745, t, price, rot=(i - 1) * 3)


def cushion(x, y):
    g = sub(ui, (*px(x, y), 0.9), rot=(-70, 0, 0), name="cushion")
    P(T.cyl(0.85, 0.35, (0, 0, 0), T.paint("#8a2f4a", fake=F, stroke=0.25), verts=20, bev=0.14, segs=3), g)
    P(T.cyl(0.5, 0.2, (0, 0, 0.3), T.paint(PAL["brass"], fake=F, gloss=0.6), verts=20, bev=0.05), g)
    return g


# part 1: a hot slice (wedge)
cushion(1210, 640)
g = sub(ui, (*px(1210, 520), 1.2), rot=(0, -10, 0), name="p_slice")
P(T.prism(Pr.sector_poly(0.25, 1.2, math.radians(60), math.radians(120), 10), 0.22, (0, -0.95, 0),
          T.paint(PAL["atk"], fake=F, stroke=0.25, gloss=0.3), bev=0.05), g)
label(g, "+2", 0.36, (0, -0.2, 0.24), PAL["cream"], fnt="sign", thin=False)
price_tag(1210, 745, "HOT SLICE", 52, rot=-2)
# part 2: a lucky pointer
cushion(1420, 640)
g = sub(ui, (*px(1420, 520), 1.2), rot=(0, 0, -25), name="p_ptr")
P(T.prism([(-0.4, 0.62), (0.4, 0.62), (0.34, 0.12), (0.0, -0.5), (-0.34, 0.12)], 0.25, (0, 0, 0),
          T.paint("#f2c230", fake=F, gloss=0.7, stroke=0.2), bev=0.06), g)
P(T.cyl(0.15, 0.14, (0, 0.32, 0.22), T.paint(PAL["gem"], fake=F, gloss=0.9), verts=12, bev=0.03), g)
price_tag(1420, 745, "LUCKY POINTER", 75, rot=3)
# part 3: a brass rim
cushion(1630, 640)
g = sub(ui, (*px(1630, 510), 1.2), rot=(18, 20, 0), name="p_rim")
for o in Pr.ring(0.55, 0.85, 0.24, (0, 0, 0), T.paint(PAL["brass"], fake=F, gloss=0.8), g, bev=0.05, segs=20):
    pass
for i in range(10):
    a = i / 10 * math.tau
    P(T.cyl(0.06, 0.06, (math.cos(a) * 0.7, math.sin(a) * 0.7, 0.24), T.paint(PAL["steel"], fake=F, gloss=0.9), verts=8,
            bev=0.02), g)
price_tag(1630, 745, "BRASS RIM", 90, rot=-3)
# "SOLD OUT" stamp on nothing -> keep the shelf honest: sale ribbon on the pointer
rb_ = sub(ui, (*px(1490, 440), 1.6), rot=(0, 0, 18), name="sale")
Pr.plaque(rb_, 1.3, 0.42, (0, 0, 0), col=PAL["atk"], trim="#f2c230", rng=rng, bolts=False, depth=0.12)
label(rb_, "-20%", 0.24, (0, -0.02, 0.1), PAL["cream"], fnt="title", thin=True)

# ---------------------------------------------------------------- HUD: credits, reroll, leave
g = sub(ui, (*px(1700, 70), 0.6), name="credits")
Pr.plaque(g, 3.4, 0.9, (0, 0, 0), col=PAL["wood"], rng=rng)
P(T.cyl(0.32, 0.16, (-1.1, 0, 0.12), T.paint("#f2c230", fake=F, gloss=0.8), verts=18, bev=0.04), g)
label(g, "c", 0.34, (-1.1, -0.04, 0.3), "#7a4a10", fnt="sign")
label(g, "128", 0.56, (0.35, -0.04, 0.16), PAL["cream"], fnt="sign")
g = sub(ui, (*px(220, 70), 0.6), name="deckbtn")
Pr.plaque(g, 3.0, 0.9, (0, 0, 0), col=PAL["iron"], trim=PAL["steel"], rng=rng)
label(g, "DECK  14", 0.4, (0, -0.03, 0.16), PAL["cream"], fnt="title")

Pr.button(ui, "LEAVE  >", (*px(1690, 985), 1.2), w=3.2, h=1.1, col="#e8573c", size=0.56, name="leave")
Pr.button(ui, "REROLL  c10", (*px(250, 985), 1.2), w=3.3, h=0.95, col=PAL["def"], size=0.44, name="reroll")

T.render(sc, OUT)
