"""05 shop (GRITTY): a cramped back-alley black-market stall under a dripping tarp - corrugated
rusty walls, caged goods, cable clutter, a hooded battered robot fence, a flickering sign, prices
scrawled on tape. Transparent film; post.py lays it over the rainy alley plate.

usage: blender -b --factory-startup --python scene_shop.py -- <out.png> [samples]
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
OUT = args[0] if args else os.path.join(T.OUT_ROOT, "stills", "_shop_fg.png")
SAMPLES = int(args[1]) if len(args) > 1 else 32

sc = T.reset()
T.MODE["name"] = "day_ui"
T.MODE["grit"] = 0.8
T.MODE["fake"] = (-0.45, -1.0, 0.75)
T.setup_render(sc, samples=SAMPLES, transparent=True, line=3.2)
T.compositor(sc, bloom=(0.9, 1.1, 7))
cam = T.camera((0, -30, 0), (0, 0, 0), lens=50)
ui = Pr.ui_root(cam, depth=30.0)
rng = random.Random(1337)
F = "ui"


def P(o, g):
    o.parent = g
    return o


def wire(g, pts, col="#15161a", r=0.035):
    cu = T.bpy.data.curves.new("wire", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    o = T.bpy.data.objects.new("wire", cu)
    T.link_obj(o)
    cu.materials.append(T.paint(col, fake=F))
    o.parent = g
    return o


def sag(p0, p1, s, n=10):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t - s * 4 * t * (1 - t)))
    return out


# ---------------------------------------------------------------- the stall (ground plane group)
st = sub(ui, (*px(960, 840), -2.5), rot=(-80, 0, 0), scale=1.08, name="stall")
Pr.ground_base(st, 6.9, 2.5, (0, 0.4, 0), rng, top="#3a3c42", side="#4a4640", fake=F, tufts=0, rocks=9)
# wet ground: puddles with neon reflection
for (x, y, c) in ((-3.0, -1.9, "#ff2fb0"), (2.6, -2.0, "#3ff0ff"), (5.4, -1.4, "#8cff2a")):
    P(T.prism([(math.cos(i / 12 * 6.28) * 1.0 + x, math.sin(i / 12 * 6.28) * 0.3 + y) for i in range(12)], 0.01,
              (0, 0, 0.07), T.glow(c, 0.55), bev=0), st)
# back wall: corrugated rusty sheet panels (vertical ribs), patched
for i in range(8):
    x = -4.9 + i * 1.4
    c = rng.choice(("#5a4a3e", "#6a4a34", "#4a5250", "#57524a"))
    P(T.box((1.42, 0.2, 4.3 + rng.uniform(-0.2, 0.2)), (x, 2.05, 0.0), T.paint(c, fake=F, streak_axis=2, streak=26,
            stroke=0.35), bev=0.04, wonk=0.03, rng=rng, rot=(0, rng.uniform(-2, 2), 0)), st)
    for k in range(5):
        P(T.box((0.08, 0.1, 4.0), (x - 0.56 + k * 0.28, 1.93, 0.1), T.paint(c, fake=F), bev=0.02), st)
for zz in (1.9, 3.1):
    P(T.box((10.4, 0.6, 0.12), (0, 1.75, zz), T.paint("#4a4a4e", fake=F, gloss=0.3), bev=0.03), st)
# caged goods on the shelves: jars, boxes, chips behind bars
for i in range(16):
    zz = 1.9 + 0.12 if i < 8 else 3.1 + 0.12
    x = -4.6 + (i % 8) * 1.25 + rng.uniform(-0.2, 0.2)
    k = rng.random()
    if k < 0.4:
        P(T.cyl(0.22, 0.5, (x, 1.7, zz), T.glow(rng.choice(["#8cff2a", "#ff2fb0", "#3ff0ff"]), 1.4), verts=10, bev=0.04), st)
        P(T.cyl(0.24, 0.1, (x, 1.7, zz + 0.5), T.paint(PAL["iron"], fake=F), verts=10, bev=0.02), st)
    elif k < 0.8:
        P(T.box((0.6, 0.45, 0.4), (x, 1.7, zz), T.paint(rng.choice(["#8a7050", "#5a6048", "#6a4a34"]), fake=F),
                bev=0.04, wonk=0.06, rng=rng, rot=(0, 0, rng.uniform(-12, 12))), st)
    else:
        P(T.box((0.5, 0.1, 0.35), (x, 1.75, zz), T.glow(rng.choice(["#3ff0ff", "#ff9a2a"]), 2.2), bev=0.02), st)
for x0 in (-4.2, 1.4):
    for k in range(13):
        P(T.cyl(0.03, 2.4, (x0 + k * 0.24, 1.3, 1.9), T.paint("#6a6a6a", fake=F, gloss=0.5), verts=5, bev=0), st)
    for zz in (1.9, 3.1, 4.3):
        P(T.box((3.0, 0.06, 0.06), (x0 + 1.44, 1.3, zz), T.paint("#6a6a6a", fake=F), bev=0), st)
    P(T.box((0.3, 0.1, 0.36), (x0 + 1.44, 1.24, 3.4), T.paint("#8a8478", fake=F, gloss=0.6), bev=0.03), st)   # padlock
# scaffold posts
for x in (-5.5, 5.5):
    P(T.box((0.3, 0.3, 5.9), (x, -0.2, 0.0), T.paint("#4a4a4e", fake=F, gloss=0.3), bev=0.04, wonk=0.03, rng=rng), st)
    for zz in (1.5, 3.0, 4.5):
        P(T.cyl(0.05, 0.9, (x, 0.3, zz), T.paint("#8a7a3a", fake=F), verts=6, bev=0, rot=(90, 0, 0), origin_bottom=False), st)
# dripping, patched tarp sagging over the stall
for i in range(4):
    x = -4.2 + i * 2.8
    P(T.box((2.95, 3.0, 0.1), (x, 0.55, 5.55 - 0.12 * (i % 2)), T.paint(rng.choice(("#2e3a48", "#34404a", "#3a3a44")),
            fake=F, stroke=0.35, streak_axis=1), bev=0.05, rot=(-22, rng.uniform(-3, 3), rng.uniform(-2, 2)), wonk=0.06,
            rng=rng), st)
    P(T.box((2.95, 0.1, 0.55), (x, -0.85, 4.9 - 0.12 * (i % 2)), T.paint("#2a343e", fake=F, stroke=0.3), bev=0.04,
            wonk=0.06, rng=rng, rot=(rng.uniform(-6, 6), 0, 0)), st)
    # duct-tape patch
    P(T.box((0.6, 0.02, 0.2), (x + rng.uniform(-0.8, 0.8), -0.93, 5.05), T.paint("#8a8a86", fake=F), bev=0,
            rot=(0, rng.uniform(-30, 30), 0)), st)
    # drips hanging from the tarp edge
    for k in range(4):
        dx = x - 1.2 + k * 0.8 + rng.uniform(-0.15, 0.15)
        ln = rng.uniform(0.15, 0.35)
        P(T.cyl(0.05, ln, (dx, -0.9, 4.62 - 0.12 * (i % 2) - ln), T.paint("#8ac8e0", fake=F, gloss=0.9), r2=0.0, verts=6,
                bev=0, rot=(180, 0, 0), origin_bottom=False), st)
        P(T.cyl(0.05, 0.08, (dx, -0.9, 4.2 - k * 0.3 - 0.12 * (i % 2) - ln), T.paint("#8ac8e0", fake=F, gloss=0.9),
                verts=6, bev=0.02), st)
# cable clutter + a bare bulb
wire(st, sag((-5.5, -0.6, 4.7), (5.5, -0.6, 4.6), 0.2))
wire(st, sag((-5.5, -0.5, 4.5), (-1.2, -0.5, 4.6), 0.35), "#2a2020")
wire(st, sag((1.2, -0.7, 4.7), (5.5, -0.7, 4.2), 0.3), "#1a2226")
wire(st, [(2.0, -0.7, 4.3), (2.0, -0.7, 3.5)])
P(T.cyl(0.18, 0.28, (2.0, -0.7, 3.2), T.glow("#ffc070", 4.0), verts=10, bev=0.05), st)
# counter: welded sheet-metal crates
P(T.box((10.6, 1.5, 1.35), (0, -0.4, 0.0), T.paint("#4a4e52", fake=F, pattern="plank", pat_scale=1.3, streak_axis=2,
        streak=18), bev=0.08, wonk=0.015, rng=rng), st)
P(T.box((11.0, 1.8, 0.2), (0, -0.4, 1.35), T.paint("#34373c", fake=F, streak_axis=0, streak=24), bev=0.06), st)
P(T.box((1.1, 1.0, 0.9), (-6.3, -1.2, 0.0), T.paint("#5a6048", fake=F, pattern="plank"), bev=0.06, wonk=0.06, rng=rng,
        rot=(0, 0, 12)), st)
P(T.box((0.8, 0.8, 0.7), (-6.1, -1.1, 0.9), T.paint("#6a5040", fake=F, pattern="plank"), bev=0.06, wonk=0.06, rng=rng,
        rot=(0, 0, -8)), st)
P(T.cyl(0.55, 1.2, (6.4, -1.0, 0.0), T.paint("#3a4a3a", fake=F, gloss=0.3), verts=14, bev=0.06, wonk=0.06, rng=rng), st)
for (x, y) in ((5.5, -1.9), (6.3, -1.8), (-5.2, -2.0)):
    P(T.rock(0.34, (x, y, 0.1), T.paint("#1e1e22", fake=F, gloss=0.5), rng, flat=0.85), st)

# hooded, battered robot fence: dented body, cloth hood, one cracked eye
rb = sub(st, (0, 0.9, 1.3), name="robot")
P(T.box((1.8, 1.0, 1.5), (0, 0, 0), T.paint("#5a6068", fake=F, gloss=0.3), bev=0.12, wonk=0.06, rng=rng, taper=0.12), rb)
P(T.box((1.7, 1.1, 1.4), (0, 0, 1.6), T.paint("#2a2c30", fake=F), bev=0.15, wonk=0.05, rng=rng, taper=0.1), rb)
P(T.box((1.3, 0.2, 0.9), (0, -0.55, 1.85), T.glow("#0f2020", 1.0), bev=0.06), rb)
P(T.box((0.26, 0.1, 0.3), (-0.3, -0.67, 2.4), T.glow("#8cff2a", 4.0), bev=0.04), rb)
P(T.box((0.26, 0.1, 0.3), (0.3, -0.67, 2.4), T.glow("#2a4a20", 1.0), bev=0.04), rb)    # dead eye
P(T.prism([(0.2, 0.15), (0.34, -0.05), (0.26, -0.18)], 0.02, (0.2, -0.72, 2.3), T.flat_col("#0a0a0a"), bev=0,
          rot=(90, 0, 0)), rb)
P(T.box((0.6, 0.1, 0.1), (0, -0.67, 1.98), T.glow("#8cff2a", 3.0), bev=0.02, rot=(0, -8, 0)), rb)
# hood: draped cloth, big and wonky
P(T.cyl(1.25, 1.7, (0, 0.1, 1.3), T.paint("#3a2e2a", fake=F, stroke=0.35), r2=0.35, verts=8, bev=0.1, wonk=0.1, rng=rng), rb)
P(T.box((2.2, 0.4, 1.3), (0, -0.62, 0.3), T.paint("#3a2e2a", fake=F, stroke=0.35), bev=0.12, wonk=0.08, rng=rng, taper=0.25), rb)
for sx in (-1, 1):
    P(T.box((0.35, 0.35, 1.1), (sx * 1.15, -0.1, 0.4), T.paint("#5a6068", fake=F), bev=0.08, rot=(0, sx * -25, 0)), rb)
P(T.cyl(0.04, 0.7, (0.55, 0.2, 3.2), T.paint(PAL["steel"], fake=F), verts=6, bev=0, rot=(0, 20, 0)), rb)
P(T.cyl(0.1, 0.12, (0.78, 0.2, 3.85), T.glow("#ff2a3a", 5), verts=8, bev=0.02), rb)

# ---------------------------------------------------------------- flickering sign
sg = sub(ui, (*px(960, 96), 0.5), rot=(0, 0, -2.5), name="sign")
Pr.plaque(sg, 7.6, 1.4, (0, 0, 0), col="#1e1c22", trim="#5a5048", rng=rng, depth=0.3)
word = "BLACK MARKET"
dead = {2, 9}   # flickering-out letters
xs = -3.05
for i, ch in enumerate(word):
    if ch == " ":
        xs += 0.35
        continue
    lit = i not in dead
    o = T.text(ch, 0.95, (xs, 0.05, 0.3), rot=(0, 0, 0), mat=T.glow("#ff2fb0", 3.2) if lit else T.paint("#4a2a3a", fake=F),
               fnt="title", extrude=0.1, bev=0, align="LEFT", coll=None)
    o.parent = sg
    xs += 0.56 if ch not in "MW" else 0.72
label(sg, "cash only  -  no questions", 0.24, (0, -0.55, 0.3), "#8cff2a", fnt="title", lined=False)
for sx in (-1, 1):
    P(T.cyl(0.05, 1.3, (sx * 3.2, 0.7, -0.1), T.paint(PAL["iron"], fake=F), verts=6, bev=0), sg)
wire(sg, sag((-3.8, 0.4, 0.0), (-4.6, -1.8, -0.3), 0.3))

# ---------------------------------------------------------------- goods with prices scrawled on tape
def tape_price(x, y, name, price, rot=0.0):
    g = sub(ui, (*px(x, y), 1.4), rot=(0, 0, rot), name="tag")
    P(T.box((1.75, 0.95, 0.04), (0, 0, 0), T.paint("#cdbb86", fake=F, stroke=0.45, blotch=0.35), bev=0.0,
            wonk=0.03, rng=random.Random(int(x))), g)
    label(g, name, 0.2, (0, 0.22, 0.05), "#2a1a12", fnt="title", lined=False)
    label(g, "%d cr" % price, 0.46, (0, -0.2, 0.05), "#101010", fnt="scrawl", lined=False)
    return g


cards = [("OVERCLOCK", 1, "Spin your wheel\n+3 on red slices.", PAL["atk"], Pr.icon_bolt, "ATTACK", 45),
         ("FIREWALL", 1, "Gain 6 block.\nBlue slices +2.", PAL["def"], Pr.icon_shield, "DEFEND", 38),
         ("GLITCH", 1, "Swap two enemy\nslices.", PAL["glitch"], Pr.icon_chip, "HACK", 60)]
for i, (t, c, d, col, ic, kind, price) in enumerate(cards):
    x = 330 + i * 190
    Pr.card(ui, t, c, d, col, (*px(x, 520), 1.0), rot=(0, 0, (i - 1) * -4), icon=ic, kind=kind,
            rng=random.Random(i + 20), name="card_%d" % i)
    tape_price(x, 748, t, price, rot=(i - 1) * 4 + rng.uniform(-3, 3))


def crate_stand(x, y):
    g = sub(ui, (*px(x, y), 0.9), rot=(-70, 0, 0), name="crate")
    P(T.box((1.5, 1.2, 0.5), (0, 0, -0.1), T.paint("#5a5048", fake=F, pattern="plank"), bev=0.05, wonk=0.05, rng=rng), g)
    for k in range(6):   # cage bars around the item
        a = k / 6 * math.tau
        P(T.cyl(0.03, 1.9, (math.cos(a) * 0.62, math.sin(a) * 0.5, 0.4), T.paint("#7a7a7a", fake=F, gloss=0.5), verts=5,
                bev=0), g)
    return g


# part 1: a scorched slice
crate_stand(1210, 650)
g = sub(ui, (*px(1210, 520), 1.2), rot=(0, -10, 0), name="p_slice")
P(T.prism(Pr.sector_poly(0.25, 1.2, math.radians(60), math.radians(120), 10), 0.22, (0, -0.95, 0),
          T.paint(PAL["atk"], fake=F, stroke=0.3, gloss=0.3), bev=0.05), g)
label(g, "+2", 0.36, (0, -0.2, 0.24), PAL["cream"], fnt="sign", thin=False)
tape_price(1210, 748, "HOT SLICE", 52, rot=-4)
# part 2: a stolen pointer
crate_stand(1420, 650)
g = sub(ui, (*px(1420, 520), 1.2), rot=(0, 0, -25), name="p_ptr")
P(T.prism([(-0.4, 0.62), (0.4, 0.62), (0.34, 0.12), (0.0, -0.5), (-0.34, 0.12)], 0.25, (0, 0, 0),
          T.paint("#d9a032", fake=F, gloss=0.6, stroke=0.3), bev=0.06), g)
P(T.cyl(0.15, 0.14, (0, 0.32, 0.22), T.paint(PAL["gem"], fake=F, gloss=0.9), verts=12, bev=0.03), g)
tape_price(1420, 748, "LUCKY POINTER", 75, rot=5)
# part 3: a welded rim
crate_stand(1630, 650)
g = sub(ui, (*px(1630, 510), 1.2), rot=(18, 20, 0), name="p_rim")
for k in range(10):
    a0 = k / 10 * math.tau + 0.02
    a1 = (k + 1) / 10 * math.tau - 0.02
    P(T.prism(Pr.sector_poly(0.55, 0.85, a0, a1, 3), 0.24, (0, 0, 0), T.paint("#e8c030" if k % 2 else "#1c1c1c", fake=F)
              if k in (2, 3, 4) else T.paint("#7a6a5a", fake=F, gloss=0.5), bev=0.04), g)
tape_price(1630, 748, "SCRAP RIM", 90, rot=-3)
# a "HOT" sticker slapped on the pointer
rb_ = sub(ui, (*px(1490, 440), 1.6), rot=(0, 0, 18), name="sale")
Pr.plaque(rb_, 1.3, 0.42, (0, 0, 0), col="#a0201e", trim="#d9a032", rng=rng, bolts=False, depth=0.12)
label(rb_, "STOLEN", 0.22, (0, -0.02, 0.1), PAL["cream"], fnt="title", thin=True)

# ---------------------------------------------------------------- HUD: credits, deck, reroll, leave
g = sub(ui, (*px(1700, 70), 0.6), name="credits")
Pr.plaque(g, 3.4, 0.9, (0, 0, 0), col="#2e3238", trim="#8a6a3a", rng=rng)
Fc.cut_gem(0.36, 0.18, 0.08, n=8, loc=(-1.1, 0, 0.2), col="#ffc830", glow=1.2, parent=g, seed=2)
label(g, "128", 0.56, (0.35, -0.04, 0.16), PAL["cream"], fnt="sign")
g = sub(ui, (*px(220, 70), 0.6), name="deckbtn")
Pr.plaque(g, 3.0, 0.9, (0, 0, 0), col="#2e3238", trim="#6a6258", rng=rng)
label(g, "DECK  14", 0.4, (0, -0.03, 0.16), PAL["cream"], fnt="title")

Pr.button(ui, "LEAVE  >", (*px(1690, 985), 1.2), w=3.2, h=1.1, col="#ff5a3a", size=0.56, name="leave")
Pr.button(ui, "REROLL  10cr", (*px(250, 985), 1.2), w=3.3, h=0.95, col="#3ff0ff", size=0.42, name="reroll")

# hologram projected from the fence's antenna: a low-poly faceted spinner icon + price flicker
def ring_img(u, v):
    cu, cv = u - 0.5, v - 0.5
    d = (cu * cu + cv * cv) ** 0.5
    if d < 0.12:
        return 0
    if 0.24 < d < 0.44:
        return 1 if (math.atan2(cv, cu) * 3 / math.pi) % 1.0 < 0.5 else 2
    return None


Fc.tri_panel(1.5, 1.5, 7, 7, ["#8cff2a", "#3ff0ff", "#ff2fb0"], loc=(*px(1085, 255), 0.8), glow=1.8, seed=5,
             image=ring_img, alpha=0.75, parent=ui)
Fc.tri_panel(0.5, 0.9, 2, 3, ["#3ff0ff"], loc=(*px(1060, 345), 0.7), glow=1.0, seed=6, alpha=0.25, parent=ui)
rr = random.Random(4)
for k in range(16):
    Fc.shard(rr.uniform(0.04, 0.09), (*px(rr.uniform(980, 1200), rr.uniform(170, 340)), rr.uniform(0.5, 1.2)),
             rr.choice(("#3ff0ff", "#8cff2a", "#ff2fb0")), glow=1.7, rng=rr, parent=ui)

T.render(sc, OUT)
