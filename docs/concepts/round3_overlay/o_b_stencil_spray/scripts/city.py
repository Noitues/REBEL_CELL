"""02_city.png: HIT THIS (reticle), OURS (fist), planned-path arrow, THEM warning, Heat poster."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from marks import Overlay, load_base, stencil_word, freehand, icon_layer, OUT
from spraylib import PINK, WHITE, YELLOW, icon_reticle, icon_fist, icon_eye_crossed
from posters import heat_poster


def build():
    rng = np.random.default_rng(2207)
    base = load_base("concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png")
    ov = Overlay()

    # Heat poster, pasted top right, FLAGGED sprayed across it
    poster, flagged = heat_poster(rng)
    ov.place(poster, 1606, 52, angle=-3)
    ov.place(flagged, 1612, 262)

    # planned path: freehand yellow arrow along the streets, home -> target
    path, x0, y0 = freehand([(742, 650), (820, 728), (960, 752), (1110, 722), (1200, 664), (1236, 636)],
                            9, YELLOW, rng, arrow=True, head=30, taper_out=0.10, mist=0.25)
    ov.place(path, x0, y0)

    # target node: stencil reticle sprayed around it + HIT THIS
    ret = icon_layer(icon_reticle(150, ring=0.09, dot=False, tick=0.20), PINK, rng, halo=6, pad=20)
    ov.place(ret, 1293 - ret.size[0] / 2, 586 - ret.size[1] / 2)
    hit = stencil_word("HIT THIS", 64, PINK, rng, angle=-4, drips=4, drip_len=55, drip_w=(4, 6),
                       keyline=(WHITE, 3, 3), sheen=0.45, return_parts=True)
    ov.place_c(hit, 1430, 448)

    # home: OURS + fist
    fist = icon_layer(icon_fist(58, 72), WHITE, rng, halo=6)
    ov.place(fist, 438, 664, angle=6)
    ours = stencil_word("OURS", 60, WHITE, rng, angle=3, drips=2, drip_len=40, drip_w=(3, 5), sheen=0.35,
                        return_parts=True)
    ov.place_c(ours, 588, 722)
    a, x0, y0 = freehand([(640, 678), (668, 650), (690, 626)], 7, WHITE, rng, arrow=True, head=20, mist=0.25)
    ov.place(a, x0, y0)

    # threat: crossed eye + THEM next to the boss node
    eye = icon_layer(icon_eye_crossed(104, 62), YELLOW, rng, halo=6)
    ov.place(eye, 1694, 506)
    them = stencil_word("THEM", 62, YELLOW, rng, angle=-5, sheen=0.4, return_parts=True)
    ov.place_c(them, 1772, 628)
    a2, x0, y0 = freehand([(1700, 650), (1672, 655), (1645, 652)], 7, YELLOW, rng, arrow=True, head=18, mist=0.25)
    ov.place(a2, x0, y0)

    out = ov.apply(base, darken=0.24, desat=0.3, spread=18)
    out.save(os.path.join(OUT, "02_city.png"))
    print("saved 02_city.png")


if __name__ == "__main__":
    build()
