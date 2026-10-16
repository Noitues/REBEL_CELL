"""HQ Orbital: H_launch_board.png (the launch cutscene as a 7-panel storyboard sheet, 2560 x 1440) and
H_launch_strike.png (the city-wide strike moment, 1920 x 1080, no UI) from the launch renders (hq_jobs.py launch).

python hq_launch_board.py [bl_board_dir] [bl_strike_dir]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import hq_post as PO  # noqa: E402
import hq_preset as HP  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
BIG = HP.PRESET["hq"]["out_big"]
PANELS = [
    ("L1_sabotage", "1  SABOTAGE", ["Circuit 2 ends: the bay doors open, the rocket", "rises; the Cell retargets it (RETARGET 2/3)."]),
    ("L2_pullout", "2  PULL OUT", ["The camera pulls out to the city: the HQ small", "in the grid, the struck site far across it."]),
    ("L3_launch", "3  LAUNCH", ["The rocket lifts out of the silo on its plume;", "the trail starts to draw."]),
    ("L4_arc", "4  THE ARC", ["It arcs high over the city: the trail cuts", "across the skyline."]),
    ("L5_descent", "5  DESCENT", ["It comes down on an Orbital facility (the", "COMMONS RELAY 7 roof, east market)."]),
    ("L6_strike", "6  STRIKE", ["Impact: the relay goes up. Orbital, not the", "city (variant: a satellite, a sky strike)."]),
    ("L7_zoom_back", "7  BACK TO THE HQ", ["The camera zooms back into the HQ: the doors", "close, the fire burns on the skyline."]),
]


def main():
    bl = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BIG, "bl_launch_board")
    bls = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BIG, "bl_launch_strike")
    W, H = 2560, 1440
    sheet = Image.new("RGB", (W, H), (12, 10, 18)).convert("RGBA")
    K.text(sheet, (60, 50), "ORBITAL COMMONS  //  THE LAUNCH: a circuit's retarget, as storyboard frames (future cutscene)",
           K.F(K.MONO, 30), (240, 238, 232), "lm", 0.6)
    K.text(sheet, (60, 90), "Rendered from the HQ scene (the same city ring, the same look): the camera, the rocket's arc, "
           "the strike on an Orbital site. Proposal: not in the GDD.", K.F(K.MONO, 18), (170, 182, 200), "lm", 0.3)
    pw, ph = 600, 338
    for k, (name, title, cap) in enumerate(PANELS):
        stem = os.path.join(bl, name)
        x = 60 + (k % 4) * (pw + 20)
        y = 130 + (k // 4) * (ph + 300)
        if os.path.exists(stem + "_combined.npy"):
            im = PO.finish(stem, 0.35, t=2.0 + k * 0.4).convert("RGB").resize((pw, ph), Image.LANCZOS)
            sheet.paste(im, (x, y))
        d = ImageDraw.Draw(sheet)
        d.rectangle([x - 2, y - 2, x + pw + 1, y + ph + 1], outline=(205, 240, 255), width=2)
        K.text(sheet, (x + 4, y + ph + 26), title, K.F(K.ANTON, 26), (205, 240, 255), "lm", 0.4)
        for j, ln in enumerate(cap):
            K.text(sheet, (x + 4, y + ph + 58 + j * 24), ln, K.F(K.MONO, 17), (215, 225, 232), "lm", 0.3)
    x, y = 60 + 3 * (pw + 20), 130 + (ph + 300)
    sheet = KT.term(sheet, (x, y, x + pw, y + ph + 120), "TIMING (24 fps, ~7 s)", accent=(205, 240, 255), seed=61)
    for j, ln in enumerate(["1 sabotage 0.0-0.8 s", "2 pull out 0.8-2.0 s (ease out)", "3 launch 2.0-2.6 s",
                            "4 arc 2.6-4.2 s (the camera pans with it)", "5 descent 4.2-4.8 s", "6 strike 4.8-5.6 s (flash)",
                            "7 back in 5.6-7.0 s", "", "after circuits 1-3; the 4th ends", "with the override (HQ destroyed)."]):
        K.text(sheet, (x + 22, y + 66 + j * 30), ln, K.F(K.MONO, 18), (215, 225, 232), "lm", 0.3)
    sheet.convert("RGB").save(os.path.join(ROOT, "H_launch_board.png"))
    print("saved H_launch_board.png")
    stem = os.path.join(bls, "L6_strike")
    if os.path.exists(stem + "_combined.npy"):
        PO.finish(stem, 0.35, t=2.0).save(os.path.join(ROOT, "H_launch_strike.png"))
        print("saved H_launch_strike.png")


if __name__ == "__main__":
    main()
