"""Solace THE BLOOM v2, HQ overview frames: {A,B,C}_hq.png (2560 x 1440), front at floor 9 of 27 on BOTH strands (CATCHING).

World medium (AAA-2): a skin over the golden HQ OVERVIEW plate (Solace v5, Cycles). The helix mask is the plate's object-index
pass (D:/rc_scratch/solace_v1/hq_v5/out/bl_stills/H_overview_index.npy, id 1 = the strands and rungs, id 3 = the plinth). The
front is one height shared by both strands: its screen row comes from the helix's measured base / top rows and the floor
number (27 floors), with tongues that run along the strand. The plinth is the source, so it is infected first.
Run:  python bloom_hq.py [A,B,C]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import bloom_skins as S
import bloom_gauge as G

PLATE = "D:/rc_art/art-pass/docs/concepts/golden_plates/hq_solace_overview.png"
INDEX = "D:/rc_scratch/solace_v1/hq_v5/out/bl_stills/H_overview_index.npy"
W, H = 2560, 1440
FLOORS, FRONT_FLOOR = 27, 9
UNIT = 16.0                       # field units = 16 px

PARAMS = {
    "A": dict(fq=0.28, zT=1.4, zM=4.0, seed=7, hpitch=8, vgain=0.95, ew=2.0, vw=1.7, keep_lo=0.45, body0=0.07, body1=0.06),
    "B": dict(fq=0.5, zT=1.2, zM=2.4, zC=3.0, cap=1.3, seed=7, tw=1.8, matv=0.34, matw=1.6, capp=0.7, gamma=1.5, lump=4.0, fibv=0.9, hsp=30.0, hlen=90.0, hw=2.0),
    "C": dict(fq=0.6, zT=0.8, zM=3.0, bub=2.2, seed=7, rip=60.0, alpha=0.9, see=0.7, spec=0.55, seen=0.6, cau=0.0),
}


def load_mask():
    idx = np.load(INDEX)[..., 0]
    hel = L.blur((idx == 1).astype(np.float32), 1.4)
    pod = L.blur((idx == 3).astype(np.float32), 1.4)
    return S.SM(0.35, 0.65, hel), S.SM(0.35, 0.65, pod)


def front_rows(hel):
    """Screen rows of the helix base and top (the strand body, without the ring), by column-occupancy."""
    rows = np.where(hel.sum(axis=1) > 6)[0]
    return int(rows.max()), int(rows.min())


def build(kind):
    t0 = time.time()
    P = np.asarray(Image.open(PLATE).convert("RGB"), np.float32) / 255.0
    hel, pod = load_mask()
    yb, yt = front_rows(hel)
    # the ring on top is id 1 too: take the top of the strand body at the topmost row with >60 px of helix
    rows = np.where(hel.sum(axis=1) > 60)[0]
    yt = int(rows.min())
    yb = int(rows.max())
    # floors run base -> top; the lower floors are nearer so they take more rows (mild perspective exponent)
    fr = FRONT_FLOOR / FLOORS
    yf = yb - (yb - yt) * (fr ** 0.92)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # tongues along the strand: the front is ragged by +- ~12 px and climbs further in places (functions of x and y)
    rag = 30.0 * (L.fbm(xx * 0.012, yy * 0.01, 5, 3) - 0.5) + 55.0 * S.SM(0.55, 0.8, L.fbm(xx * 0.02 + yy * 0.004, np.zeros_like(xx) + 4.0, 11, 3))
    d = (yy - (yf - rag)) / UNIT
    d = np.where(pod > 0.2, np.maximum(d, 6.0), d)                    # the plinth is the source: deep
    m = np.maximum(hel, pod)
    cover = S.SM(-0.05, 0.12, d) * m
    u, v = xx / UNIT, yy / UNIT
    out = S.SKINS[kind](P, cover, d, u, v, dict(PARAMS[kind]))
    # the ring and the city behind the helix are untouched (cover is zero there)
    still = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    gg = G.tide_gauge(kind, "CATCHING", w=200, h=720)
    still.alpha_composite(gg, (W - 200 - 40, 120))
    img = np.asarray(still.convert("RGB"), np.float32) / 255.0
    mt = dict(plate=L.metrics(P), still=L.metrics(img), front_row=round(float(yf), 1), base_row=yb, top_row=yt, seconds=round(time.time() - t0, 1))
    return img, mt


def main(kinds):
    res = {}
    for k in kinds:
        img, mt = build(k)
        L.save_png(img, os.path.join(L.OUT, "%s_hq.png" % k))
        res[k] = mt
        print(k, mt, flush=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "hq_values_%s.json" % "".join(kinds)), "w"), indent=1)


if __name__ == "__main__":
    main((sys.argv[1] if len(sys.argv) > 1 else "A,B,C").split(","))
