"""A3d_gauge.png: the TIDE gauge in all 5 bands (CRT, 2D) and the CAUGHT binary-bits burst (4 frames, pink) over the 3D CATCHING street frame.
2D is the right medium for both (CRT terminal, binary bits). Run: python bloom3d_strip.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import bloom_gauge as G

SW, SH = 2560, 1130
BG = (12, 7, 20)
ANCH = "D:/rc_scratch/street_r2/render_s1/anchors_F_dec_closed.json"
OP_ROOM = "L2_1"


def main():
    base = Image.open(os.path.join(L.OUT, "A3d_street_catching_clean.png")).convert("RGB") if os.path.exists(os.path.join(L.OUT, "A3d_street_catching_clean.png")) \
        else Image.open(os.path.join(L.OUT, "A3d_street_catching.png")).convert("RGB")
    A = json.load(open(ANCH))
    q = A["rooms"][OP_ROOM]["front"]
    cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
    im = Image.new("RGB", (SW, SH), BG)
    d = ImageDraw.Draw(im)
    cw = SW // 5
    for i, band in enumerate(G.BANDS):
        g = G.tide_gauge("A", band, w=216, h=640)
        im.paste(g, (i * cw + (cw - 216) // 2, 28), g)
    steps = [(0.0, 0.0, "CATCHING"), (0.30, 0.0, "CAUGHT"), (0.75, 0.15, "CAUGHT"), (1.0, 0.92, "CAUGHT")]
    for i, (k, fade, band) in enumerate(steps):
        fr = base.copy()
        if k > 0:
            fr = G.bits_burst(fr, cx, cy, k, fade, seed=5 + i, scale=3.2)
        rgba = fr.convert("RGBA")
        gg = G.tide_gauge("A", band, w=170, h=600)
        a = np.asarray(gg.getchannel("A"), np.float32) / 255.0 * (1 - 0.9 * fade)
        gg.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        rgba.alpha_composite(gg, (1920 - 170 - 24, 96))
        t = rgba.convert("RGB").resize((620, 349), Image.LANCZOS)
        x, y = 20 + i * 636, 28 + 640 + 40
        im.paste(t, (x, y))
        d.rectangle([x, y, x + 619, y + 348], outline=(60, 40, 80), width=1)
    L.save_png(np.asarray(im, np.float32) / 255.0, os.path.join(L.OUT, "A3d_gauge.png"))
    print("A3d_gauge saved")


if __name__ == "__main__":
    main()
