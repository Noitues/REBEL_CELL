"""Still 02: the city grid at night.

blender -b --factory-startup --python still_02_city.py -- <tex_dir> <out.png> base|overlay
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import riso_bpy as R

argv = sys.argv[sys.argv.index("--") + 1:]
R.init(argv[0])
OUT, MODE = argv[1], argv[2]

if MODE == "base":
    import city_scene
    city_scene.build(heat=False)
else:
    R.reset()
    R.overlay_setup()
    # glass HUD, kept to the edges; paper tags top-left
    def glass(name, tex, w, loc):
        R.card(name, tex, width=w, loc=loc, mat=R.mat_card(name, tex, em=tex, em_strength=0.9, rough=0.3, back=None))
    for i, x in enumerate([-7.3, -6.05, -4.8]):
        R.card(f"tag{i}", f"tag_{[0, 1, 3][i]}", width=1.15, loc=(x, 4.02, 0.2), rot=(0, 0, [-3, 2, -1.5][i]))
    R.card("tape", "tape_2", width=0.5, loc=(-7.2, 4.35, 0.3), rot=(0, 0, 10), mat=R.mat_card("tape2", "tape_2", blended=True, back=None, rough=0.4))
    glass("target", "wash_target", 3.6, (6.0, -3.95, 0.05))
    glass("log", "gl_log", 2.6, (6.55, 2.35, 0.05))
    mk = R.Marker("hud", z=1.0, seed=21)
    mk.words("HIT THIS", 6.0, -4.2, 0.5, rot=4, anchor="center", weight=0.12, drips=[(0, 0.3, "form"), (4, 0.4, "form")])
    mk.circle(-2.25, 1.05, 0.95, 2.45, r=0.035, turns=1.15)
    mk.words("OURS", -5.2, 2.6, 0.5, rot=-6, weight=0.11)
    mk.arrow((-3.75, 2.55), (-3.05, 2.1), bend=-0.3, r=0.03, head=0.22)

R.render(OUT)
