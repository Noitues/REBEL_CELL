"""04 combat: two crafted spinners on little ground bases, health bars, a fanned hand of
cards, a chunky GO button. Rendered with transparent film; post.py lays it over the
blurred, darkened night city.

usage: blender -b --factory-startup --python scene_combat.py -- <out.png> [samples]
"""
import os
import math
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_props as Pr
from tt_props import PAL, px, sub, label

args = T.arg_list()
OUT = args[0] if args else os.path.join(T.OUT_ROOT, "stills", "_combat_fg.png")
SAMPLES = int(args[1]) if len(args) > 1 else 32

sc = T.reset()
T.MODE["name"] = "day_ui"
T.MODE["grit"] = 0.8
T.MODE["fake"] = (-0.45, -1.0, 0.75)
T.setup_render(sc, samples=SAMPLES, transparent=True, line=3.2)
T.compositor(sc)
cam = T.camera((0, -30, 0), (0, 0, 0), lens=50)
T.sun(2.0, rot=(60, 0, -30))
ui = Pr.ui_root(cam, depth=30.0)
rng = random.Random(42)

# ---------------------------------------------------------------- top plaques
p = Pr.plaque(ui, 3.6, 0.7, (*px(560, 44), 0), col="#2e3238", trim="#8a6a3a", rng=rng, name="pl_you")
label(p, "YOU  //  CELL-7", 0.36, (0, -0.03, 0.2), PAL["cream"])
p = Pr.plaque(ui, 4.2, 0.7, (*px(1360, 44), 0), col="#4a1e24", trim="#6a6258", rng=rng, name="pl_foe")
label(p, "SEC-DRONE  MK.II", 0.36, (0, -0.03, 0.2), PAL["cream"])
# turn tag
p = Pr.plaque(ui, 2.0, 0.64, (*px(960, 44), 0), col=PAL["iron"], trim=PAL["steel"], rng=rng, bolts=False, name="pl_turn")
label(p, "TURN 3", 0.3, (0, -0.02, 0.2), "#8cff2a")

# ---------------------------------------------------------------- spinners on ground bases
def stand(x, flip):
    g = sub(ui, (*px(x, 660), -1.4), rot=(-72, 0, 0), name="stand")
    Pr.ground_base(g, 2.3, 1.05, (0, 0, 0), rng, fake="ui", tufts=0, rocks=7, top="#6e695e", side="#4a4640")
    # broken concrete: rebar stubs, a puddle, a trash bag
    for k in range(6):
        a = rng.uniform(0, 6.28)
        o = T.cyl(0.03, rng.uniform(0.4, 0.8), (math.cos(a) * 2.2, math.sin(a) * 0.95, -0.2),
                  T.paint("#8a4a2a", fake="ui"), verts=5, bev=0, smooth=False)
        o.rotation_euler = (rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9), 0)
        o.parent = g
    T.prism([(math.cos(i / 10 * 6.28) * 0.7, math.sin(i / 10 * 6.28) * 0.28) for i in range(10)], 0.01,
            (-0.6 * flip, -0.55, 0.07), T.glow("#ff2fb0" if flip > 0 else "#3ff0ff", 0.5), bev=0).parent = g
    T.rock(0.28, (1.1 * flip, -0.55, 0.1), T.paint("#1e1e22", fake="ui", gloss=0.5), rng, flat=0.9).parent = g
    # iron post + crate plinth holding the wheel
    T.box((1.0, 0.8, 0.5), (0, 0.25, 0), T.paint("#5a5048", fake="ui", streak_axis=0, streak=16), bev=0.06,
          wonk=0.04, rng=rng).parent = g
    T.box((0.5, 0.4, 2.2), (0, 0.35, 0.4), T.paint(PAL["iron"], fake="ui", gloss=0.4), bev=0.06, wonk=0.03,
          rng=rng).parent = g
    # warning barrel / junk for diorama feel
    T.cyl(0.32, 0.6, (1.55 * flip, -0.1, 0), T.paint("#c8a030" if flip > 0 else "#3a5a7a", fake="ui", gloss=0.3),
          verts=14, bev=0.05).parent = g
    T.box((0.5, 0.45, 0.35), (-1.45 * flip, 0.1, 0), T.paint("#7a8f99", fake="ui"), bev=0.05, wonk=0.06,
          rng=rng, rot=(0, 0, 18)).parent = g


stand(560, 1)
stand(1360, -1)
Pr.spinner(ui, 2.05, [(PAL["atk"], 6), (PAL["def"], 4), (PAL["atk"], 8), (PAL["hack"], 3), (PAL["def"], 5), (PAL["atk"], 6)],
           (*px(560, 390), 0), rot=(0, 16, 0), frame="#2e3036", rim="#7a6a5a", hub="#3a3a40", pointer=PAL["hack"], spin=0.25, rng=rng, hub_icon="7", name="sp_you")
Pr.spinner(ui, 2.05, [(PAL["atk"], 9), (PAL["glitch"], 2), (PAL["atk"], 5), (PAL["def"], 6), (PAL["atk"], 7), (PAL["glitch"], 3)],
           (*px(1360, 390), 0), rot=(0, -16, 0), frame="#241c20", rim="#5a5a62", hub="#4a1e24", pointer=PAL["atk"], cracked=True, hazard=((20, 24),),
           spin=-0.4, rng=rng, hub_icon="!", name="sp_foe")

# VS badge
g = sub(ui, (*px(960, 390), 0.4), name="vs")
T.cyl(0.62, 0.3, (0, 0, 0), T.paint(PAL["ink"], fake="ui"), verts=8, bev=0.05, rot=(0, 0, 22.5)).parent = g
for o in Pr.ring(0.5, 0.66, 0.34, (0, 0, 0.0), T.paint(PAL["brass"], fake="ui", gloss=0.7), g, bev=0.04, segs=16):
    pass
label(g, "VS", 0.56, (0, -0.02, 0.3), PAL["hack"])

# health bars
Pr.meter(ui, 3.2, 0.8, (*px(530, 728), 0.2), fill=PAL["hp_g"], segs=10, value_txt="48/60", name="hp_you")
Pr.meter(ui, 3.2, 0.5, (*px(1330, 728), 0.2), fill=PAL["hp_r"], segs=10, value_txt="36/72", name="hp_foe")
for x, c in ((340, PAL["hp_r"]), (1140, PAL["hp_r"])):
    g = sub(ui, (*px(x - 44, 728), 0.4), name="heart")
    T.cyl(0.26, 0.2, (0, 0, 0), T.paint(c, fake="ui", gloss=0.6), verts=12, bev=0.05).parent = g
    label(g, "+", 0.4, (0, -0.02, 0.18), PAL["cream"], fnt="sign")

# ---------------------------------------------------------------- hand of cards
cards = [
    ("OVERCLOCK", 1, "Spin your wheel\n+3 on red slices.", PAL["atk"], Pr.icon_bolt, "ATTACK"),
    ("FIREWALL", 1, "Gain 6 block.\nBlue slices +2.", PAL["def"], Pr.icon_shield, "DEFEND"),
    ("BRUTE SPIN", 2, "Spin 2 ticks.\nDeal slice x2.", "#d9772e", Pr.icon_spin, "ATTACK"),
    ("GLITCH", 1, "Swap two enemy\nslices.", PAL["glitch"], Pr.icon_chip, "HACK"),
    ("CRASH", 2, "Enemy pointer\nskips 1 slice.", "#6b7a88", Pr.icon_skull, "HACK"),
]
n = len(cards)
for i, (t, c, d, col, ic, kind) in enumerate(cards):
    k = i - (n - 1) / 2
    x = 880 + k * 205
    y = 902 + abs(k) ** 1.6 * 16
    lift = -16 if i == 2 else 0
    Pr.card(ui, t, c, d, col, (*px(x, y + lift), 0.8 + i * 0.05), rot=(0, 0, -k * 5.5), icon=ic, kind=kind,
            rng=random.Random(i + 3), name="card_%d" % i)

# deck pile + RAM orb (left)
g = sub(ui, (*px(150, 935), 0.4), rot=(0, 0, 6), name="deck")
for j in range(4):
    T.prism(Pr.rrect_poly(1.5, 2.1, 0.18), 0.1, (j * 0.04, j * 0.05, j * 0.11), T.paint("#2e3440", fake="ui"), bev=0.03).parent = g
label(g, "12", 0.62, (0.12, 0.1, 0.55), PAL["cream"], fnt="sign")
label(g, "DECK", 0.3, (0.12, -0.6, 0.55), PAL["hack"], lined=False)
g = sub(ui, (*px(150, 740), 0.6), name="ram")
T.cyl(0.62, 0.36, (0, 0, 0), T.paint(PAL["gem"], fake="ui", gloss=0.9, stroke=0.2), verts=6, bev=0.08).parent = g
T.cyl(0.74, 0.22, (0, 0, -0.1), T.paint(PAL["brass"], fake="ui", gloss=0.7), verts=6, bev=0.05).parent = g
label(g, "3/4", 0.46, (0, -0.03, 0.38), PAL["cream"], fnt="sign")
label(g, "RAM", 0.24, (0, -0.95, 0.1), PAL["cream"])

# GO button
Pr.button(ui, "GO!", (*px(1720, 930), 0.6), w=2.9, h=1.3, col="#8cff2a", size=0.86, name="go")
g = sub(ui, (*px(1720, 815), 0.4), name="go_hint")
label(g, "SPIN  [SPACE]", 0.26, (0, 0, 0), PAL["cream"], fnt="title", lined=False)

T.render(sc, OUT)
