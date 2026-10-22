"""Solace THE BLOOM v2, raid map frames: {A,B,C}_raid.png (1920 x 1080), campaign infection ~60 %.

Cel + ink (Blender Eevee) map of the Solace district at the game's raid zoom. The Eevee render is the clean R5 raw plus a world
position pass (raid_scene/sd_main.py with BLOOM_POS=1: Eevee, 7 s). Every pixel decodes to a world (x, y, z); the skin is laid in
world space (ground: x, y; walls: x + y and height; roofs: x, y), re-inked with the same ink pass and post, then the CRT gauge
(bare Anton %) goes on top in PIL. The infection field is a distance from the two DEFENDED home-server nodes (the helix
plaza and the hospital), warped by noise and ragged per lot; ground floods first, walls up to a tide line that rises with the
field value. Defended nodes are never recoloured. Run:  python bloom_raid.py [A,B,C] [pct]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

import solace_lib as L
import bloom_skins as S
import bloom_gauge as G

D_OUT = "D:/rc_scratch/solace_v1/district/out"
POS = "D:/rc_scratch/solace_v1/bloom/out/raid_pos.npy"
RAW = D_OUT + "/R5_raid_raw.png"
INK = D_OUT + "/R5_raid_ink.png"
SCR = "D:/rc_scratch/solace_v1/bloom/out"
RS = os.path.join(HERE, "raid_scene")
W, H = 1920, 1080
PITCH = 24.0
DEFENDED = [((0.0, 0.0), 46.0), ((108.0, -60.0), 42.0)]       # helix plaza + hospital Site (home-server nodes)

PARAMS = {
    "A": dict(fq=0.22, zT=6.0, zM=18.0, seed=7, hpitch=8, vgain=0.9, ew=1.8, vw=1.5, keep_lo=0.5, body0=0.10, body1=0.10, vein=1.0),
    "B": dict(fq=0.2, zT=3.0, zM=7.0, zC=9.0, cap=2.6, seed=7, tw=2.0, matv=0.55, matw=1.6, capp=0.7, gamma=1.3, lump=4.0, fibv=0.9, hsp=26.0, hlen=70.0, hw=2.0, cel=True),
    "C": dict(fq=0.15, zT=3.0, zM=12.0, bub=5.5, seed=7, rip=40.0, alpha=0.93, see=0.5, spec=0.6, seen=0.8, cau=0.0, cel=True),
}


def load():
    pos = np.load(POS)
    X, Y, Z = [L.boxblur(pos[..., i], 1, 1) for i in range(3)]
    valid = Z > -1.0
    raw = np.asarray(Image.open(RAW).convert("RGB"), np.float32) / 255.0
    return X, Y, Z, valid, raw


def fields(X, Y, Z, valid, pct, seed=3):
    gy, gx = np.gradient(Z)
    gz = np.hypot(gx, gy)
    ground = (Z < 0.6) & valid
    wall = (gz > 0.12) & (Z >= 0.6) & valid
    # nearest defended node distance (BU, 0 at the node rim), warped by noise
    dn = np.full(X.shape, 1e9, np.float32)
    for (cx, cy), r in DEFENDED:
        dn = np.minimum(dn, np.hypot(X - cx, Y - cy) - r)
    warp = 60.0 * (L.fbm(X * 0.010, Y * 0.010, seed, 4) - 0.5) + 18.0 * (L.fbm(X * 0.04, Y * 0.04, seed + 2, 3) - 0.5)
    Fg = dn + warp                                                  # continuous field for the ground
    li, lj = np.round(X / PITCH), np.round(Y / PITCH)
    lh = L._hash(li.astype(np.int64) + 50, lj.astype(np.int64) + 50, seed + 9)
    lcx, lcy = li * PITCH, lj * PITCH
    dl = np.full(X.shape, 1e9, np.float32)
    for (cx, cy), r in DEFENDED:
        dl = np.minimum(dl, np.hypot(lcx - cx, lcy - cy) - r)
    Fl = dl + 60.0 * (L.fbm(lcx * 0.010, lcy * 0.010, seed, 4) - 0.5) + 18.0 * (L.fbm(lcx * 0.04, lcy * 0.04, seed + 2, 3) - 0.5) + 30.0 * (lh - 0.5)     # one value per lot
    prot = np.zeros(X.shape, np.float32)
    for (cx, cy), r in DEFENDED:
        prot = np.maximum(prot, S.SM(r + 4.0, r - 4.0, np.hypot(X - cx, Y - cy)))
    # pick the threshold so that `pct` of the visible, non-defended area is infected (by the ground field for the ground,
    # by the lot field for the rest)
    sel = valid & (prot < 0.5)
    tn = 6.0 * (L.fbm(X * 0.05 + Y * 0.05, Z * 0.1, seed + 4, 3) - 0.5)

    def dfun(th):
        lvl_g, lvl_l = Fg - th, Fl - th
        zc = np.clip(lvl_l, 0, None) * 0.9 + 14.0 + tn            # tide line height on walls (BU)
        return np.where(ground, lvl_g, np.where(lvl_l > 0, zc - Z, -5.0))
    lo, hi = -80.0, 160.0                                          # bisect the threshold so `pct` of the non-defended area is infected
    for _ in range(14):
        mid = (lo + hi) / 2
        share = float(((dfun(mid) > 0) & sel).sum() / max(sel.sum(), 1))
        if share > pct:
            lo = mid
        else:
            hi = mid
    th = (lo + hi) / 2
    d = dfun(th)
    # texture coordinates: ground & roofs (x, y); walls (x + y along the facade, height)
    u = np.where(wall, (X + Y) * 0.7071, X)
    v = np.where(wall, Z * 0.8, Y)
    infected_share = float(((d > 0) & sel).sum() / max(sel.sum(), 1))
    return d, u, v, prot, th, infected_share, dict(ground=ground, wall=wall)


def render(kind, pct=0.60, scratch_only=False):
    t0 = time.time()
    X, Y, Z, valid, raw = load()
    d, u, v, prot, th, share, cl = fields(X, Y, Z, valid, pct)
    cover = S.SM(-0.05, 0.4, d) * valid * (1 - prot)
    out = S.SKINS[kind](raw, cover, d, u, v, dict(PARAMS[kind]))
    L.save_png(out, SCR + "/raid_%s_raw.png" % kind)
    subprocess.run([sys.executable, os.path.join(RS, "ink.py"), SCR + "/raid_%s_raw.png" % kind, INK, SCR + "/raid_%s_inked.png" % kind, "2.6"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, os.path.join(RS, "post.py"), "mapraid", SCR + "/raid_%s_inked.png" % kind, SCR + "/raid_%s_post.png" % kind], check=True)
    img = Image.open(SCR + "/raid_%s_post.png" % kind).convert("RGBA")
    panel, num = G.raid_gauge(kind, pct)
    img.alpha_composite(panel, (36, 30))
    img.alpha_composite(num, (36 + panel.size[0] + 6, 18))
    arr = np.asarray(img.convert("RGB"), np.float32) / 255.0
    clean = np.asarray(Image.open("D:/rc_art/art-pass/docs/concepts/solace_vertical/district/D_raid_park_r5.png").convert("RGB"), np.float32) / 255.0
    mt = dict(clean=L.metrics(clean), still=L.metrics(arr), infected_share_of_nondefended=round(share, 3), seconds=round(time.time() - t0, 1),
              infected_area_of_frame=round(float(((d > 0) & valid & (prot < 0.5)).mean()), 3))
    return arr, mt


def main(kinds, pct):
    res = {}
    for k in kinds:
        img, mt = render(k, pct)
        L.save_png(img, os.path.join(L.OUT, "%s_raid.png" % k))
        res[k] = mt
        print(k, mt, flush=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "raid_values_%s.json" % "".join(kinds)), "w"), indent=1)


if __name__ == "__main__":
    main((sys.argv[1] if len(sys.argv) > 1 else "A,B,C").split(","), float(sys.argv[2]) if len(sys.argv) > 2 else 0.60)
