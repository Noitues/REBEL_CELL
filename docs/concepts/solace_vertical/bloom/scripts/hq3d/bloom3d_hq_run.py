"""Solace THE BLOOM v2, A Necrosis in 3D on the HQ helix (v5 scene copy, Cycles): A3d_hq_overview.png (CATCHING) and A3d_hq_decision.png (CLOSE).

python bloom3d_hq_run.py <quality: mini|b3d> [overview|decision|clean_overview|clean_decision ...]
Renders go to D:/rc_scratch/solace_v1/bloom3d/hq_<state>/; the plate is the v5 post (hq_post.finish, no UI), the same pipeline as the
golden plate. Takes the GPU lock "solace_bloom" (gpu_run.py). The front is ONE height shared by both strands (z_front), with tongues.
"""
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

import hq_graph as G

BS = "D:/rc_scratch/solace_v1/bloom3d"
OUT = "D:/rc_art/art-pass/docs/concepts/solace_vertical/bloom"
# state -> (still name, front floor (fractional, route-floor interpolation), gap layers)
STATES = {
    "overview": ("H_overview", 9.0, 0.6),            # CATCHING: the front at about floor 9 of 27, both strands
    "decision": ("H_decision", None, 1.25),          # CLOSE: front 1.25 layers behind the operative (B3 = layer 3, floor 9)
}


def front_floor(layer):
    """Route layer (float) -> floor: layer 1 is route floor RF[0] = 3, one layer is 3 floors (RF = 3, 6, 9 ...)."""
    RF = G.RF
    if layer <= 1:
        return RF[0] + (layer - 1) * 3.0
    i = min(int(math.floor(layer)) - 1, len(RF) - 2)
    return RF[i] + (RF[i + 1] - RF[i]) * (layer - 1 - i)


def st_bias(state):
    """Decision frame: the front is lifted 10 BU so the near strand shows it in the lower third (rev 2)."""
    return 28.0 if state == "decision" else 0.0


def cfg_for(state, tune=None):
    nm, ff, gap = STATES[state]
    if ff is None:
        ff = front_floor(3 - gap)
    cfg = dict(z_front=G.floor_z(ff) + 0.5 * G.FH, floor=ff, gap=gap, seed=7, tube_r=G.RT, swell=4.5, tongue=40.0, reach=45.0, ahead=1.0, stair_phi_A=G.stair_phi("A"),
               stair_phi_B=G.stair_phi("B"), vscale=0.24, vw=0.065, ew=1.1, hatch_k=0.12, veins=1.5, edge=45.0, hatch=0.2, cover_k=0.94,
               plum=[0.03, 0.012, 0.024], pink=[1.0, 0.0612, 0.305], podium=G.PODIUM_H, win_dim=0.03, win_r=48.0, win_bias=0.0, haze_h=38.0, haze_k=0.004, haze_em=0.07)
    if st_bias(state):
        cfg["z_front"] += st_bias(state)
    if tune:
        cfg.update(tune)
    return cfg


def run(quality, state, tune=None):
    nm = STATES[state][0] if state in STATES else None
    clean = state.startswith("clean_")
    st = state[6:] if clean else state
    name = STATES[st][0]
    big = os.path.join(BS, "hq_" + ("clean_" if clean else "") + st + "_" + quality)
    os.makedirs(big, exist_ok=True)
    env = dict(os.environ, HQ_BIG=big, HQ_SCR=os.path.join(BS, "hq_scr"))
    os.makedirs(env["HQ_SCR"], exist_ok=True)
    args = [sys.executable, os.path.join(HERE, "gpu_run.py"), "hq3d %s %s" % (quality, state), sys.executable, os.path.join(HERE, "hq_jobs.py"), "stills", quality, name]
    if not clean:
        args.append("bloom=" + json.dumps(cfg_for(st, tune)))
    t0 = time.time()
    subprocess.run(args, env=env, check=False)
    return big, name, time.time() - t0


QUAL_NOW = ["mini"]


def plate(big, name):
    import hq_post as PO
    ov = json.load(open(os.path.join(BS, "hq_scr", "ov_stills.json")))[name]
    stem = os.path.join(big, "bl_stills_" + QUAL_NOW[0], name)
    img = PO.finish(stem, ov["zoom"], t=2.0)
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    Lm = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return img, dict(median=round(float(np.median(Lm)), 4), under10=round(float((Lm < 0.10).mean()), 4), over85=round(float((Lm > 0.85).mean()), 4),
                     peak_p999=round(float(np.quantile(Lm, 0.999)), 3))


if __name__ == "__main__":
    q = sys.argv[1]
    QUAL_NOW[0] = q
    for s in sys.argv[2:]:
        big, name, t = run(q, s)
        img, v = plate(big, name)
        p = os.path.join(BS, "hqplate_%s_%s.png" % (s, q))
        img.save(p)
        print(s, q, "wall %.0f s" % t, v, p, flush=True)
