"""Solace THE BLOOM v2: {A,B,C}_gauge.png, a 2D strip: the TIDE gauge in all 5 bands (DORMANT .. CAUGHT) on top, the CAUGHT binary-bits
burst in 4 frames below (over the direction's own CATCHING street frame). CRT gauge, pink bits. Run: python bloom_strip.py [A,B,C]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import bloom_gauge as G
import bloom_street as B

SW, SH = 2560, 1130
BG = (12, 7, 20)


def burst_frames(sc, kind):
    """4 frames (960 x 540 each, no gauge in the street frame; the gauge goes on per frame)."""
    base, mt, f, vis = B.render(sc, kind, "CATCHING", with_ui=True, forecast=False, gauge=False)
    base_img = Image.fromarray((np.clip(base, 0, 1) * 255 + 0.5).astype(np.uint8))
    q = vis[B.OP_ROOM]
    cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
    steps = [(0.0, 0.0, "CATCHING"), (0.30, 0.0, "CAUGHT"), (0.75, 0.15, "CAUGHT"), (1.0, 0.92, "CAUGHT")]
    out = []
    for i, (k, fade, band) in enumerate(steps):
        fr = base_img.copy()
        if k > 0:
            fr = G.bits_burst(fr, cx, cy, k, fade, seed=5 + i, scale=3.2)
        rgba = fr.convert("RGBA")
        gg = G.tide_gauge(kind, band, w=170, h=600)
        a = np.asarray(gg.getchannel("A"), np.float32) / 255.0 * (1 - 0.9 * fade)
        gg.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        rgba.alpha_composite(gg, (B.W - 170 - 24, 96))
        out.append(rgba.convert("RGB").resize((620, 349), Image.LANCZOS))
    return out


def main(kinds):
    sc = B.Scene()
    for kind in kinds:
        im = Image.new("RGB", (SW, SH), BG)
        d = ImageDraw.Draw(im)
        cw = SW // 5
        for i, band in enumerate(G.BANDS):
            g = G.tide_gauge(kind, band, w=216, h=640, seed_off=0)
            im.paste(g, (i * cw + (cw - 216) // 2, 28), g)
        fr = burst_frames(sc, kind)
        for i, f in enumerate(fr):
            im.paste(f, (20 + i * 636, 28 + 640 + 40))
            d.rectangle([20 + i * 636, 28 + 640 + 40, 20 + i * 636 + 619, 28 + 640 + 40 + 348], outline=(60, 40, 80), width=1)
        L.save_png(np.asarray(im, np.float32) / 255.0, os.path.join(L.OUT, "%s_gauge.png" % kind))
        print(kind, "strip saved", flush=True)


if __name__ == "__main__":
    main((sys.argv[1] if len(sys.argv) > 1 else "A,B,C").split(","))
