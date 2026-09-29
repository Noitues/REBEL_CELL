"""Still 05: the marker's life in three panels (feedback 6).
1 the words write on stroke by stroke (the pen is still on the glass),
2 drips form and pause while the game waits,
3 on press the page slides away and the drips keep running down the screen.

blender -b --factory-startup --python still_05_marker_strip.py -- <tex_dir> <out.png>
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
rng = random.Random(505)

R.reset()
R.setup(samples=64, world=(30, 30, 34), world_strength=0.7, glare_threshold=1.2, glare_strength=0.4, glare_size=0.5)
R.camera((0, 0, 17.8), (0, 0, 0), lens=40)
R.sun((-30, -24, 0), strength=2.8, angle=5)

R.card("page", "strip_page", width=16.3, loc=(0, 0, -0.05), mat=R.mat_card("page", "strip_page", back=None, rough=1.0))

XS = [-5.25, 0.0, 5.25]
PW, PY = 4.4, -0.1
DRIPS = [(0, 0.5, "form"), (2, 0.75, "form"), (3, 0.35, "form"), (5, 0.6, "form")]


def screen(i, dx=0.0, dy=0.0, rot=0.0, opacity=1.0, z=0.1):
    tex = "strip_screen"
    return R.card(f"scr{i}_{opacity}", tex, width=PW, loc=(XS[i] + dx, PY + dy, z), rot=(0, 0, rot),
                  mat=R.mat_card(f"scr_{opacity}", tex, em=tex, em_strength=0.8, rough=0.25, back=None, blended=opacity < 1.0, opacity=opacity))


def execute(i, dx=0.0, dy=0.0, rot=0.0, opacity=1.0, z=0.14):
    tex = "wash_execute"
    return R.card(f"exe{i}_{opacity}", tex, width=PW * 0.82, loc=(XS[i] + dx, PY - 2.0 + dy, z), rot=(0, 0, rot),
                  mat=R.mat_card(f"exe_{opacity}", tex, em=tex, em_strength=0.8, rough=0.3, back=None, blended=opacity < 1.0, opacity=opacity))


def tapes(i, dx=0.0, dy=0.0):
    for k, (tx, ty, tr) in enumerate([(-PW / 2 + 0.2, 3.25, 35), (PW / 2 - 0.2, 3.25, -35)]):
        R.card(f"tp{i}{k}", f"tape_{(i + k) % 4}", width=0.8, loc=(XS[i] + tx + dx, PY + ty + dy, 0.3), rot=(0, 0, tr),
               mat=R.mat_card(f"tape{(i + k) % 4}", f"tape_{(i + k) % 4}", blended=True, back=None, rough=0.4))


mk = R.Marker("marker", z=1.0, seed=55)

# 1: writing on, the pen still on the glass
screen(0)
execute(0)
tapes(0)
tip = mk.words("SEND IT", XS[0], PY - 2.22, 0.6, rot=5, anchor="center", weight=0.12, progress=0.62)
if tip:
    tx, ty = tip
    # the marker pen: tip cone + barrel + cap, lifted off the glass so it throws a shadow
    body = R.mat_solid("pen_body", (26, 24, 28), 0.35, spec=0.8)
    capm = R.mat_solid("pen_cap", R.C["pink"], 0.3, spec=0.8)
    ang = math.radians(35)
    d = (math.cos(ang), math.sin(ang))
    p0 = (tx + d[0] * 0.18, ty + d[1] * 0.18, 1.05)
    p1 = (tx + d[0] * 2.6, ty + d[1] * 2.6, 2.1)
    p2 = (tx + d[0] * 3.3, ty + d[1] * 3.3, 2.4)
    R.tube("pen_tip", [(tx, ty, 1.0), p0], 0.05, R.mat_solid("pen_nib", R.C["pink_dk"], 0.6))
    R.tube("pen_barrel", [p0, p1], 0.2, body)
    R.tube("pen_cap", [p1, p2], 0.21, capm)
R.card("cap1", "cap_1", width=3.6, loc=(XS[0], PY - 3.78, 0.35), rot=(0, 0, -2))

# 2: done writing; drips form and pause, waiting for the player
screen(1)
execute(1)
tapes(1)
mk.words("SEND IT", XS[1], PY - 2.22, 0.6, rot=5, anchor="center", weight=0.12, drips=DRIPS)
R.card("cap2", "cap_2", width=3.6, loc=(XS[1], PY - 3.78, 0.35), rot=(0, 0, 1.5))

# 3: press. The page slides out left and down (smear copies); the ink stays on the glass and runs
for k, (dy, op) in enumerate([(-0.7, 0.14), (-1.5, 0.3), (-2.6, 1.0)]):
    screen(2, dx=-0.15 * k, dy=dy, rot=-2 - k * 1.5, opacity=op, z=0.1 + k * 0.01)
    execute(2, dx=-0.15 * k - 0.1, dy=dy, rot=-2 - k * 1.5, opacity=op, z=0.14 + k * 0.01)
# the empty slot the page leaves behind: the paper page shows through with a torn tape
R.card("tp_left", "tape_2", width=0.8, loc=(XS[2] + PW / 2 - 0.2, PY + 3.25, 0.3), rot=(0, 0, -35),
       mat=R.mat_card("tape2", "tape_2", blended=True, back=None, rough=0.4))
mk.words("SEND IT", XS[2], PY - 2.22, 0.6, rot=5, anchor="center", weight=0.12,
         drips=[(0, 3.4, "run"), (2, 4.6, "run"), (3, 2.6, "run"), (5, 4.0, "run"), (1, 2.0, "run")])
R.card("cap3", "cap_3", width=3.6, loc=(XS[2], PY - 3.78, 0.35), rot=(0, 0, -1))

R.render(OUT)
