"""01_combat.png: SEND IT over the GO button, enemy target, tactical note, crew poster."""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from marks import Overlay, load_base, stencil_word, freehand, ellipse_pts, icon_layer, OUT
from spraylib import PINK, WHITE, YELLOW, blur, icon_reticle, icon_fist, darken_under
from posters import crew_poster


def wash_button(base, cx, cy, r, amount=0.42, desat=0.85):
    """The digital button goes washed-out / standby under the human verb."""
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    m = np.clip((r - np.hypot(xx - cx, yy - cy)) / 30, 0, 1)
    arr = np.asarray(base, np.float32) / 255
    g = arr.mean(axis=2, keepdims=True)
    arr = arr * (1 - desat * m[..., None]) + g * desat * m[..., None]
    arr = arr * (1 - amount * m[..., None]) + 0.06 * amount * m[..., None]
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def send_it(rng, reveal=None, drip_lengths=None, drip_specs=None, return_parts=False):
    return stencil_word("SEND\nIT", 122, PINK, rng, angle=-7, drips=7, drip_len=95, drip_w=(5, 9),
                        line_gap=-0.06, align="center", sheen=0.5, halo=10, reveal=reveal,
                        drip_lengths=drip_lengths, drip_specs=drip_specs, return_parts=return_parts,
                        shadow_off=(6, 7), keyline=(WHITE, 4, 4))


def build():
    rng = np.random.default_rng(1104)
    base = load_base("concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png")
    base = wash_button(base, 1760, 895, 135, amount=0.30, desat=0.6)
    ov = Overlay()

    # crew photo: wheat-pasted photocopy, top left beside our rig
    crew = crew_poster(rng)
    ov.place(crew, 70, 128, angle=4)

    # tactical note: small white stencil under the photo
    note = stencil_word("HE GUARDS ON 6.\nBAIT HIM,\nTHEN BURN.", 30, WHITE, rng, angle=3, slice_frac=None,
                        bridge=0.04, line_gap=0.02, sheen=0.3, halo=5, shadow_off=(3, 3), tracking=0.06)
    ov.place(note, 26, 452)
    ul, x0, y0 = freehand([(58, 590), (130, 586), (205, 592)], 6, YELLOW, rng, taper_out=0.35)
    ov.place(ul, x0, y0)

    # target loop around the enemy rig + HIT IT
    pts = ellipse_pts(1362, 410, 272, 258, -2.15, -2.15 + 2 * math.pi + 0.42, n=22, wob=0.025, rng=rng, tilt=0.05)
    loop, x0, y0 = freehand(pts, 10, YELLOW, rng, taper_out=0.12, mist=0.22)
    ov.place(loop, x0, y0)
    hit = stencil_word("HIT IT", 70, YELLOW, rng, angle=6, drips=3, drip_len=48, drip_w=(4, 6), sheen=0.45)
    ov.place(hit, 1628, 480)
    arr_, x0, y0 = freehand([(1700, 492), (1672, 452), (1640, 425)], 9, YELLOW, rng, arrow=True, head=26)
    ov.place(arr_, x0, y0)

    # the verb: SEND IT over the washed GO button
    ov.place_c(send_it(rng, return_parts=True), 1748, 884)

    out = ov.apply(base, darken=0.26, desat=0.3, spread=18)
    out.save(os.path.join(OUT, "01_combat.png"))
    print("saved 01_combat.png")


if __name__ == "__main__":
    build()
