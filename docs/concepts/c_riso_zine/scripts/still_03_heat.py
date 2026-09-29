"""Still 03: the same city at high Heat (HUNTED). Helicopters with searchlights, drones,
red/blue corp flicker, heavier haze; the screen-wide heat glitch is added in post.py.

blender -b --factory-startup --python still_03_heat.py -- <tex_dir> <out.png> base|overlay
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import riso_bpy as R
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
R.init(argv[0])
OUT, MODE = argv[1], argv[2]


def beam(name, top, bottom, r_top, r_bot, mat):
    """A searchlight cone of acetate light from top to bottom."""
    t, b = Vector(top), Vector(bottom)
    d = t - b
    ob = R.cone(name, r_bot, r_top, d.length, tuple((t + b) / 2), (0, 0, 0), mat)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.normalized().to_track_quat("Z", "Y")
    return ob


def spot(top, bottom, color, power, size):
    ob = R.point(top, color, power=power, radius=0.2, kind="SPOT", spot=(size, 0.4), shadow=True)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = (Vector(bottom) - Vector(top)).normalized().to_track_quat("-Z", "Y")
    return ob


if MODE == "base":
    import city_scene
    stand = city_scene.stand
    cam, nodes, rng = city_scene.build(heat=True)
    rng = random.Random(303)
    light_m = R.mat_emit("searchlight", (255, 250, 225), 3.0, alpha=0.16, fade="top")
    thread = R.mat_solid("thread", (200, 200, 210), 0.6)
    # helicopters, each pinning a searchlight on the grid (the HQ is being looked for)
    for k, (x, y, z, gx, gy) in enumerate([(-13.0, 14.0, 10.0, -8.0, 7.5), (11.0, 18.0, 11.0, 4.0, 5.5), (2.0, 11.0, 9.2, -4.5, 1.5)]):
        flip = 180 if k == 1 else 0
        stand(f"heli{k}", "heli", 3.4, x, y, yaw=flip + rng.uniform(-6, 6), lift=z,
              mat=R.mat_card("heli", "heli", em="heli_em", em_strength=5.0, back=(30, 30, 40)))
        R.tube(f"hthr{k}", [(x, y, z + 2.2), (x, y, 40)], 0.02, thread)
        R.point((x, y - 2.0, z + 1.8), (255, 225, 205), power=900, radius=0.8)
        beam(f"hbeam{k}", (x - 0.8 * (1 if not flip else -1), y - 0.2, z + 0.5), (gx, gy, 0.0), 0.12, 2.4, light_m)
        spot((x, y - 0.3, z + 0.5), (gx, gy, 0), (255, 248, 225), 9000, 16)
        R.point((x + 1.8, y - 0.6, z + 0.8), R.C["harm"], power=60, radius=0.2)
    # ground searchlights sweeping the sky from the corp towers
    for k, (x, y, tx, ty, tz) in enumerate([(14.0, 22.0, 4.0, 30.0, 26.0), (-20.0, 24.0, -6.0, 32.0, 24.0), (22.0, 16.0, 30.0, 30.0, 22.0)]):
        beam(f"gbeam{k}", (tx, ty, tz), (x, y, 1.0), 2.6, 0.2, R.mat_emit(f"gb{k}", (230, 235, 255), 3.0, alpha=0.12, fade="bottom"))
    # drone swarm closing on the HQ
    for k in range(12):
        x, y, z = -7.0 + rng.uniform(-9, 11), rng.uniform(10, 20), rng.uniform(4.5, 9.5)
        stand(f"drone{k}", "drone", rng.uniform(0.9, 1.3), x, y, yaw=rng.uniform(-10, 10), lift=z,
              mat=R.mat_card("drone", "drone", em="drone_em", em_strength=6.0, back=(30, 30, 40)))
        R.tube(f"dthr{k}", [(x, y, z + 0.5), (x, y, 40)], 0.012, thread)
    # red/blue corp flicker on the towers (<= 1 Hz in game; frozen here mid-flash)
    for k in range(8):
        x = rng.uniform(-24, 26)
        y = rng.uniform(18, 30)
        R.point((x, y - 1.5, rng.uniform(4, 9)), R.C["harm"] if k % 2 == 0 else (60, 90, 255), power=900, radius=1.5)
    # heavier haze
    for f in range(6):
        stand(f"hfog{f}", f"fog_{rng.randrange(6)}", rng.uniform(4, 8), rng.uniform(-24, 24), rng.uniform(12, 28), lift=rng.uniform(0, 3),
              mat=R.mat_card(f"hfogm{f}", f"fog_{f}", unlit=True, unlit_strength=0.5, blended=True, back=None, tint=(255, 170, 170)))
else:
    R.reset()
    R.overlay_setup()

    def glass(name, tex, w, loc):
        R.card(name, tex, width=w, loc=loc, mat=R.mat_card(name, tex, em=tex, em_strength=0.9, rough=0.3, back=None))

    for i, x in enumerate([-7.3, -6.05, -4.8]):
        R.card(f"tag{i}", f"tag_{[0, 2, 3][i]}", width=1.15, loc=(x, 4.02, 0.2), rot=(0, 0, [-3, 2, -1.5][i]))
    # the Heat poster slapped big, a WANTED sticker slapped over the corner, mid-peel
    R.card("poster", "poster_hunted", width=1.9, loc=(6.7, 2.65, 0.3), rot=(0, 0, -7))
    R.card("ptape", "tape_0", width=0.7, loc=(6.6, 3.85, 0.4), rot=(0, 0, 6), mat=R.mat_card("tape0", "tape_0", blended=True, back=None, rough=0.4))
    ob = R.card("wanted", "stk_wanted", width=2.4, loc=(5.2, 1.3, 0.6), rot=(0, 0, 12), nx=18, ny=18)
    R.peel(ob, (1, -1), 0.25, 55)
    R.point((6.7, 2.4, 2.0), R.C["harm"], power=40, radius=0.5)
    glass("evade", "wash_evade", 3.6, (6.1, -3.85, 0.05))
    mk = R.Marker("hud", z=1.0, seed=33)
    mk.words("RUN", 6.1, -4.3, 0.85, rot=-5, anchor="center", weight=0.13, drips=[(0, 0.5, "form"), (1, 0.9, "form"), (2, 0.4, "form")])
    mk.words("THEM", -3.9, 3.05, 0.5, rot=6, weight=0.11)
    mk.arrow((-3.95, 3.0), (-4.25, 2.5), bend=0.35, r=0.03, head=0.2)
    mk.arrow((-1.9, 3.3), (0.3, 1.95), bend=-0.25, r=0.03, head=0.22)
    mk.circle(-2.25, 1.05, 0.95, 2.45, r=0.035, turns=1.1)
    mk.words("HOLD", -1.55, -0.95, 0.42, rot=-4, weight=0.1)

R.render(OUT)
