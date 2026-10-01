"""02_city.png: route + waypoints, target ring, OURS, THEM (grease pencil); Heat poster (sticker); HIT THIS (spray)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from kit import *  # noqa


def city_base():
    base = pil2f(Image.open(BASE_CITY))
    # D: neon windows, billboards and node beacons light the facets around them
    return light_spill(base, [box_mask(330, 150, 1700, 1010)], gain=0.8, threshold=0.6)


def pencil_layer(rng):
    L = T.Layer(rng)
    # crisp printed range rings on the threat (A)
    T.print_dashed_circle(L, 1605, 662, 72, (247, 33, 31, 200), width=1.8, ticks=12)
    T.print_dashed_circle(L, 1605, 662, 116, (247, 33, 31, 140), width=1.4, dash=6, gap=10)
    L.flush_print()
    # planned route: yellow, hand-dashed, with printed waypoints
    path = T.chaikin(T.resample([(748, 654), (818, 712), (960, 744), (1112, 736), (1214, 690), (1250, 640)], 10), 3)
    L.strokes(T.arrow_strokes(path, 7, PAL_F["yellow"], rng, head=24, dashed=True, dash=30, gap=17))
    L.flush_print()
    T.print_waypoint(L, 895, 738, "1", col=K_YELLOW + (255,))
    T.print_waypoint(L, 1165, 718, "2", col=K_YELLOW + (255,))
    L.flush_print()
    # target ring (red)
    L.wax_stroke(T.hand_circle(1293, 588, 50, 60, rng), 8, PAL_F["red"])
    # home: OURS (yellow, it's the plan)
    L.wax_stroke(T.hand_circle(712, 612, 46, 66, rng, turns=1.1), 7.5, PAL_F["yellow"])
    L.strokes(T.letter_strokes("OURS", 566, 704, 42, 10.5, PAL_F["yellow"], rng, angle=-0.05))
    # threat
    L.strokes(T.letter_strokes("THEM", 1772, 548, 46, 11, PAL_F["red"], rng, angle=0.05))
    L.strokes(T.arrow_strokes(T.bezier((1712, 580), (1680, 610), (1640, 622)), 7, PAL_F["red"], rng, head=18))
    L.light()
    return L


SMUDGES = [(1480, 250, 64, 50, 0.3, "print"), (360, 840, 280, 66, 0.2, "wipe"), (1050, 960, 58, 46, -0.2, "print")]


def build(save=True):
    rng = np.random.default_rng(202)
    img = city_base()
    img = pencil_composite(img, pencil_layer(rng))
    img = glass(img, np.random.default_rng(12), SMUDGES, band_pos=0.26)
    img = place_sticker(img, PC.heat_poster(curl=dict(corner="bl", amount=0.10)), 1752, 222, angle=-4)
    img = spray_verbs(img, [(verb("HIT THIS", 62, angle=-4, drips=4, drip_len=55, seed=2207), 1452, 462)])
    if save:
        f2pil(img).save(os.path.join(OUT, "02_city.png"))
        print("saved 02_city.png")
    return img


if __name__ == "__main__":
    build()
