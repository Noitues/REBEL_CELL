"""The pop-up paper city diorama shared by still 02 (night) and still 03 (high Heat).

Standing cut-paper skyline cards in rows, highways as paper strips on stilts at three
heights, flyers hung on thread, acetate hologram billboards on projector beams, vellum
fog patches (each blurred differently), and the grid map lying flat on the table with
node stickers and marker links on that one plane. Ortho camera + DOF = tilt-shift.
"""
import math
import random

import riso_bpy as R

PITCH = 32.0
TARGET = (0.0, 14.0, 3.0)


def stand(name, tex, height, x, y, yaw=0.0, lift=0.0, **mk):
    """A vertical card standing on the table (image up = +Z), sized by height."""
    return R.card(name, tex, height=height, loc=(x, y, lift + height / 2), rot=(90, 0, yaw), **mk)


def build(heat=False, seed=202):
    rng = random.Random(seed)
    R.reset()
    R.setup(samples=64, world=(40, 46, 96), world_strength=0.9 if not heat else 0.6, glare_threshold=1.2, glare_strength=0.45, glare_size=0.45)
    p = math.radians(PITCH)
    D = 60.0
    cam_loc = (TARGET[0], TARGET[1] - D * math.cos(p), TARGET[2] + D * math.sin(p))
    cam = R.camera(cam_loc, (90 - PITCH, 0, 0), ortho=50.0, dof=None)
    # tilt-shift: focus on the grid band; the far skyline and the near table edge go soft (7.3)
    fe = R.bpy.data.objects.new("focus", None)
    R.link(fe)
    fe.location = (0, 4.0, 0)
    cam.data.dof.focus_object = fe
    # moon/sky key from the front-left: casts each card's shadow onto the row behind
    R.sun((62, 0, -28), strength=0.6 if not heat else 0.35, angle=3, color=(170, 185, 255))
    R.sun((-120, 0, 10), strength=0.35, angle=8, color=(255, 120, 200))  # back rim from the neon haze

    # the table: the grid map lying flat
    R.card("ground", "groundmap", width=78, loc=(0, 13.0, 0), mat=R.mat_card("ground", "groundmap", back=None, rough=0.95, em="groundmap", em_strength=0.08))
    # sky backdrop (self-lit print), deep enough to show between rows
    R.card("sky", "sky", width=120, loc=(0, 36, 8), rot=(90, 0, 0), mat=R.mat_card("sky", "sky", unlit=True, back=None,
           unlit_strength=0.9 if not heat else 0.6, tint=(255, 255, 255) if not heat else (255, 140, 140)))

    em_k = 1.7 if not heat else 1.2
    rows = [  # (tex, card height, x, y)
        ("city_0", 13.0, -20, 31), ("city_0", 13.0, 18, 31.5),
        ("city_1", 10.5, -28, 27), ("city_1", 10.5, 3, 27.5), ("city_1", 10.5, 33, 27),
        ("city_5", 8.5, -16, 23.5), ("city_5", 8.5, 16, 23),
        ("city_2", 7.0, 14, 19.5), ("city_2", 7.0, -30, 19.5),
        ("city_3", 5.0, 24, 14.5), ("city_4", 5.0, -28, 14.0),
    ]
    for i, (tex, h, x, y) in enumerate(rows):
        stand(f"row{i}", tex, h, x, y, yaw=rng.uniform(-2, 2),
              mat=R.mat_card(f"row_{tex}", tex, em=tex + "_em", em_strength=em_k, back=(30, 34, 60), rough=0.95))

    # HQ tower, fully framed (feedback 7.1), with its own glow
    stand("hq", "hq", 11.0, -7.0, 17.0, yaw=3, mat=R.mat_card("hq", "hq", em="hq_em", em_strength=em_k + 1.0, back=(30, 34, 60)))
    R.point((-7.0, 14.0, 6.5), R.C["pink"], power=700, radius=1.0)
    R.point((-7.0, 20.0, 9.0), R.C["pink"], power=1500, radius=2.0)  # rim light behind the HQ
    R.point((-7.0, 14.5, 2.0), R.C["acid"], power=260, radius=1.0)

    # highways: three levels of paper strips on stilts, with traffic cut-outs on top (feedback 7.5)
    pillar = R.mat_solid("pillar", (34, 36, 58), 0.9)
    deck_m = R.mat_solid("deck", (52, 54, 86), 0.9)
    for k, (y, z, x0, w, yaw) in enumerate([(21.5, 6.8, -8, 56, -2.5), (16.0, 4.2, 22, 50, 3.0), (11.5, 2.0, -31, 36, -1.5)]):
        tex = f"hwy_{k}"
        sh = w * 90 / 3000
        R.card(f"hwy{k}", tex, width=w, loc=(x0, y, z), rot=(90, 0, yaw),
               mat=R.mat_card(f"hwy{k}", tex, em=tex + "_em", em_strength=4.0, back=(40, 42, 64)))
        R.box(f"deck{k}", (w, 1.6, 0.08), (x0 - 0.8 * math.sin(math.radians(yaw)), y + 0.8, z + sh / 2), deck_m, rot=(0, 0, yaw))
        for px in range(-int(w / 2) + 2, int(w / 2), 6):
            wx = x0 + px * math.cos(math.radians(yaw))
            wy = y + px * math.sin(math.radians(yaw)) + 0.7
            R.box(f"pil{k}_{px}", (0.4, 0.4, z - sh / 2), (wx, wy, (z - sh / 2) / 2), pillar)
        for c in range(14 if not heat else 8):
            cx = rng.uniform(-w / 2 + 2, w / 2 - 2)
            flip = rng.random() < 0.5
            stand(f"car{k}_{c}", "car", 0.5, x0 + cx * math.cos(math.radians(yaw)), y + cx * math.sin(math.radians(yaw)) + rng.uniform(0.3, 1.3),
                  yaw=yaw + (180 if flip else 0), lift=z + sh / 2 + 0.04,
                  mat=R.mat_card("car", "car", em="car_em", em_strength=5.0, back=(30, 30, 40)))

    # flying traffic, hung on thread
    thread = R.mat_solid("thread", (200, 200, 210), 0.6)
    for f in range(8 if not heat else 4):
        x, y, z = rng.uniform(-20, 20), rng.uniform(13, 24), rng.uniform(7.5, 10.5)
        stand(f"fly{f}", "flyer", 1.3, x, y, yaw=rng.choice([0, 180]) + rng.uniform(-8, 8), lift=z,
              mat=R.mat_card("flyer", "flyer", em="flyer_em", em_strength=5.0, back=(30, 30, 40)))
        R.tube(f"thr{f}", [(x, y, z + 0.6), (x, y, 40)], 0.02, thread)
        R.point((x, y - 0.4, z - 0.3), R.C["cyan"], power=30, radius=0.3)

    # projected hologram billboards on acetate + their projector beams (feedback 7.6)
    for b, (tex, x, y, z, h, yaw) in enumerate([("holo_0", 7.0, 19.5, 7.8, 3.0, -6), ("holo_1", -17.0, 24.0, 8.5, 3.2, 5),
                                                ("holo_2", 15.5, 14.5, 4.6, 2.4, 8), ("holo_3", -1.5, 25.0, 10.2, 2.4, -3),
                                                ("holo_4", 22.0, 24.0, 9.4, 2.6, 0)]):
        col = {"holo_0": R.C["cyan"], "holo_1": R.C["pink"], "holo_2": R.C["violet"], "holo_3": R.C["acid"], "holo_4": R.C["amber"]}[tex]
        stand(f"holo{b}", tex, h, x, y, yaw=yaw, lift=z,
              mat=R.mat_card(tex, tex, unlit=True, unlit_strength=2.2 if not heat else 1.4, blended=True, back=None, opacity=0.85))
        w = h * 640 / 360
        R.cone(f"beam{b}", 0.05, w * 0.45, z - 0.4, (x, y + 0.3, (z - 0.4) / 2 + 0.2), (0, 0, 0), R.mat_emit(f"beam{b}", col, 2.0, alpha=0.14, fade="bottom"))
        R.point((x, y - 1.2, z + 1.0), col, power=320, radius=1.5)  # the billboard lights its neighbours (feedback 10)

    # vellum fog patches, each with its own blur (feedback 7.2)
    for f, (tex, x, y, z, h) in enumerate([("fog_0", -2, 12.5, 1.0, 3.2), ("fog_1", 9, 18.0, 1.8, 4.5), ("fog_2", -15, 21.5, 2.5, 6.0),
                                          ("fog_3", 3, 24.5, 3.5, 5.0), ("fog_4", 19, 28.0, 4.0, 8.0), ("fog_5", -22, 15.0, 1.0, 4.0),
                                          ("fog_4", -6, 29.0, 5.0, 9.0), ("fog_2", 20, 14.0, 0.4, 3.5)]):
        stand(f"fog{f}", tex, h, x, y, yaw=rng.uniform(-4, 4), lift=z - h / 2,
              mat=R.mat_card(f"fogm{f}", tex, unlit=True, unlit_strength=0.5 if not heat else 0.45, blended=True, back=None,
                             tint=(215, 205, 255) if not heat else (255, 180, 170)))

    # --- the grid, on ONE plane (feedback 7.4): node stickers flat on the map + marker links
    nodes = {"hq": (-7.0, 9.5), "a": (-16.0, 5.0), "b": (-6.0, 3.0), "c": (3.0, 6.5), "d": (11.0, 2.5),
             "e": (19.0, 7.0), "f": (-1.0, -2.5), "g": (9.0, -3.5), "h": (-15.0, -2.5)}
    tex_of = {"hq": "stk_hq", "a": "stk_node", "b": "stk_node", "c": "stk_node_c", "d": "stk_node_o",
              "e": "stk_node_o", "f": "stk_node", "g": "stk_node_p", "h": "stk_node_c"}
    mk = R.Marker("links", z=0.04, seed=9)
    for (u, v, col) in [("hq", "b", "acid"), ("b", "a", "acid"), ("b", "f", "acid"), ("a", "h", "acid"), ("b", "c", "pink"),
                        ("c", "d", "pink"), ("f", "g", "pink"), ("d", "e", "orange"), ("g", "d", "orange"), ("c", "e", "orange")]:
        (x0, y0), (x1, y1) = nodes[u], nodes[v]
        pts = mk._wobble(mk._resample([(x0, y0), (x1, y1)], 0.2), 0.1, 1.2)
        if col == "orange":  # corp threat route: dashed
            for i in range(0, len(pts), 7):
                mk.stroke(pts[i:i + 4], 0.15, "orange")
        else:
            mk.stroke(pts, 0.17, col)
    for k, (x, y) in nodes.items():
        w = 4.2 if k == "hq" else 3.0
        ob = R.card(f"node_{k}", tex_of[k], width=w, loc=(x, y, 0.06), rot=(0, 0, rng.uniform(-14, 14)), nx=10, ny=10)
        if k in ("d", "hq"):
            R.peel(ob, (1, 1), 0.3, 50)
        R.point((x, y - 0.6, 1.6), R.C["acid"] if tex_of[k] in ("stk_node", "stk_hq") else R.C["pink"], power=30, radius=0.5)
    mk.circle(nodes["g"][0], nodes["g"][1], 2.0, 1.5, r=0.12)
    mk.arrow((16.0, -8.0), (10.8, -5.0), bend=0.3, r=0.13, head=1.2)
    return cam, nodes, rng
