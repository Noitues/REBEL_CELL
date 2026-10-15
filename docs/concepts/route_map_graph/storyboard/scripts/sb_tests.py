"""Storyboard v2: the four review frames before the full re-render (1280 x 720) -> ../test_frames/
  a  mid-dive: no route visible, the live city at mid LOD
  b  street level: the first walls dissolving into bits, light bleeding out
  c  mid trace: links writing on left to right, the walls following
  d  markers drawn, TARGET written, the route UI in
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import post_aaa as PA  # noqa: E402
import sb_cams as SB  # noqa: E402
import sb_frames as SF  # noqa: E402
import sb_reveal as RV  # noqa: E402
import sb_ui as U  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = os.path.join(ROOT, "test_frames")


def street_plates(f_dyn, size=(1920, 1080)):
    """(closed, opened) finished street plates at the OVERVIEW: the same media, streaks and rain; walls closed / open."""
    d = SF.static_setup("ov", size)
    dyn = SF.dyn_at(d, f_dyn, size)
    out = []
    for nm in ("S_ovc", "S_ov"):
        bl = os.path.join(SCR, "bl_ov")
        if nm == "S_ov":
            comb, emit = d["base"], d["emit"]
        else:
            comb, emit = SF.load("bl_ov", nm + "_combined"), SF.load("bl_ov", nm + "_emit")
            if comb.shape[1] != size[0]:
                comb, emit = SF.rs(comb, size), SF.rs(emit, size)
        inp = dict(comb=np.maximum(comb + dyn, 0), emit=np.maximum(emit + dyn, 0), alb=d["alb"], z=d["z"], vol=d["vol"],
                   T_het=d["T_het"], cache={})
        out.append(PA.finish(bl, "real", shot="S_ov", t=f_dyn / SB.FPS, inp=inp))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    # a) mid-dive
    pose = SB.dive_pose(0.5)
    a = PA.finish(os.path.join(SCR, "bl_t"), "real", shot="t_dive", t=11.95, over=SF.post_over("dive", SB.zoom_at("dive", pose)))
    a = U.title(a.resize((1920, 1080), Image.LANCZOS), 11.95)
    a.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "a_mid_dive_no_route.png"))
    # b, c, d) street level
    A = json.load(open(os.path.join(SCR, "bl_ov", "anchors_S_ov.json")))
    closed, opened = street_plates(330)
    shots = [("b_walls_dissolving.png", 0.22, None), ("c_trace_links_writing.png", RV.link_start(4) + 0.13, None),
             ("d_markers_target_written.png", RV.reveal_len(), RV.marks_len() + 0.05)]
    for name, tr, tm in shots:
        img = RV.reveal_plate(closed, opened, A, tr).convert("RGBA")
        img = RV.reveal_bits(img, A, tr)
        img = RV.draw_links(img, A, tr, zones=tm is not None)
        if tm is not None:
            img = RV.draw_marks(img, A, tm)
            img = RV.route_chrome(img, A, 1.0)
        img = U.title(img.convert("RGB"), 13.45 + tr + (tm or 0.0))
        img.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, name))
        print("saved", name, flush=True)


if __name__ == "__main__":
    main()
