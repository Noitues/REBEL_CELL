"""06 spinner close-up: the player's salvaged wheel as hero hardware - dented welded rim,
hazard arcs, loose wiring, painted slices with faceted crystal inlays, faceted gem hub,
the pointer and the HP bar (faceted pips). Transparent film over the rainy alley plate.

usage: blender -b --factory-startup --python scene_spinner.py -- <out.png> [samples]
"""
import os
import sys
import math
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_props as Pr
import tt_facet as Fc
from tt_props import PAL, px, sub, label

args = T.arg_list()
OUT = args[0] if args else os.path.join(T.OUT_ROOT, "stills", "_spinner_fg.png")
SAMPLES = int(args[1]) if len(args) > 1 else 32

sc = T.reset()
T.MODE["name"] = "day_ui"
T.MODE["grit"] = 0.9
T.MODE["fake"] = (-0.5, -1.0, 0.7)
T.setup_render(sc, samples=SAMPLES, transparent=True, line=3.6)
T.compositor(sc, bloom=(0.95, 0.9, 7))
cam = T.camera((0, -30, 0), (0, 0, 0), lens=50)
ui = Pr.ui_root(cam, depth=30.0)
rng = random.Random(606)

R = 3.7
Pr.spinner(ui, R, [(PAL["atk"], 6), (PAL["def"], 4), (PAL["atk"], 8), (PAL["hack"], 3), (PAL["def"], 5), (PAL["atk"], 6)],
           (*px(900, 470), 0), rot=(6, 14, 0), frame="#2e3036", rim="#7a6a5a", hub="#3a3a40", pointer=PAL["hack"],
           spin=0.25, rng=rng, name="hero", hazard=((2, 6), (15, 18), (24, 26)), inlay_glow=1.3)
# mounting bracket + stand behind the wheel (welded I-beam), junction box with cables
st = sub(ui, (*px(900, 470), -1.2), rot=(6, 14, 0), name="mount")
T.box((0.9, 0.5, 5.8), (0, -3.0, -1.2), T.paint("#3a3c42", fake="ui", gloss=0.3), bev=0.08, wonk=0.02, rng=rng,
      rot=(90, 0, 0), origin_bottom=False).parent = st
jb = sub(ui, (*px(1380, 760), 0.6), rot=(0, 0, -6), name="jbox")
T.box((1.5, 1.1, 0.5), (0, 0, 0), T.paint("#4a4e52", fake="ui", gloss=0.3), bev=0.08, wonk=0.04, rng=rng).parent = jb
for k in range(5):
    T.box((0.24, 0.05, 0.3), (-0.55 + k * 0.28, -0.56, 0.1), T.paint("#e8c030" if k % 2 else "#1c1c1c", fake="ui"),
          bev=0, rot=(0, 30, 0)).parent = jb
Fc.cut_gem(0.16, 0.08, 0.04, n=6, loc=(0.45, 0.3, 0.5), col="#8cff2a", glow=1.8, parent=jb, seed=3)
for j, c in enumerate(("#c0392b", "#e8c030", "#3a7bd5")):
    cu = T.bpy.data.curves.new("wire", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.05
    sp = cu.splines.new("POLY")
    n_ = 12
    sp.points.add(n_ - 1)
    a_ = (-0.4 + j * 0.3, 0.5, 0.2)
    b_ = (-1.6 - j * 0.35, 3.4 + j * 0.25, -1.4)
    for t_ in range(n_):
        u_ = t_ / (n_ - 1)
        x_ = a_[0] + (b_[0] - a_[0]) * u_
        y_ = a_[1] + (b_[1] - a_[1]) * u_ - (1.3 + j * 0.3) * 4 * u_ * (1 - u_)
        z_ = a_[2] + (b_[2] - a_[2]) * u_
        sp.points[t_].co = (x_, y_, z_, 1)
    ow = T.bpy.data.objects.new("wire", cu)
    T.link_obj(ow)
    cu.materials.append(T.paint(c, fake="ui", gloss=0.4))
    ow.parent = jb

# name plate welded to the frame
p = Pr.plaque(ui, 3.4, 0.72, (*px(300, 90), 0.4), col="#2e3238", trim="#8a6a3a", rng=rng, name="pl")
label(p, "CELL-7  //  SALVAGED RIG", 0.3, (0, -0.02, 0.2), "#e8e0cc", fnt="title")
# stat chips (faceted) listing the wheel's slices
for i, (c, t) in enumerate((("#ff5a4a", "ATTACK x3"), ("#3ff0ff", "DEFEND x2"), ("#ffc830", "HACK x1"))):
    g = sub(ui, (*px(160, 190 + i * 70), 0.4), name="chip")
    Fc.cut_gem(0.24, 0.12, 0.05, n=6, loc=(0, 0, 0), col=c, glow=1.2, parent=g, seed=i + 5)
    label(g, t, 0.26, (0.4, -0.03, 0.05), "#e8e0cc", fnt="title", align="LEFT", lined=False)
# HP bar with faceted pips
Pr.meter(ui, 6.0, 0.8, (*px(860, 1000), 0.8), fill="#6fe04a", segs=12, value_txt="48/60", frame="#2e3238",
         name="hp", glow=1.25)
g = sub(ui, (*px(470, 1000), 1.0), name="heart")
Fc.cut_gem(0.36, 0.16, 0.08, n=8, loc=(0, 0, 0), col="#ff4a5a", glow=1.2, parent=g, seed=9)
label(g, "HP", 0.26, (0, -0.03, 0.2), "#fff4f4", fnt="title", lined=False)
# data shards spraying off the pointer
for k in range(22):
    a = rng.uniform(-0.9, 0.9)
    d = rng.uniform(40, 260)
    Fc.shard(rng.uniform(0.05, 0.13), (*px(900 + math.sin(a) * d * 1.4, 40 + math.cos(a) * d * 0.3), rng.uniform(0.5, 1.5)),
             rng.choice(("#3ff0ff", "#ffc830", "#8cff2a")), glow=1.8, rng=rng, parent=ui)

T.render(sc, OUT)
