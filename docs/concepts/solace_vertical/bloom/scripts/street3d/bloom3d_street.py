"""Solace THE BLOOM v2, A Necrosis in 3D: the street netrun frames (street_r2 scene copy, Cycles).

python bloom3d_street.py cfg <gap_layers> <out.json>     write the BLOOM_CFG for a gap (front = OP_LAYER - gap)
python bloom3d_street.py run <test|finals> <state> [res] [spp]   render the DECISION frame (takes the GPU lock "solace_bloom")
python bloom3d_street.py plate <state>                   post (the street_r2 post, the CLEAN plate's exposure) -> plate png + values
States: CREEPING gap 2.5, CLOSE gap 1.25, CATCHING gap 0.6, CLEAN (no Bloom).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

SCR = "D:/rc_scratch/street_r2"
BS = "D:/rc_scratch/solace_v1/bloom3d"
LX = [132.7, 113.7, 101.9, 87.0, 82.2, 80.4, 73.7, 66.0]
OP_LAYER = 2                      # the mock operative stands on L2_1 (screen left of centre) so every front is in view
GAPS = {"CREEPING": 2.5, "CLOSE": 1.25, "CATCHING": 0.6, "CLEAN": None}
PINK_LIN = (1.0, 0.0612, 0.305)
PLUM_LIN = (0.075, 0.030, 0.058)


def layer_x(f):
    if f >= 0:
        i = min(int(f), len(LX) - 2)
        return LX[i] + (LX[i + 1] - LX[i]) * (f - i)
    return LX[0] - 19.0 * f


def make_cfg(gap, tune=None):
    D = json.load(open(os.path.join(SCR, "derive_v3.json")))
    fx = layer_x(OP_LAYER - gap)
    boxes = []
    # route rooms: opening + jamb + frame ring + 10 % margin (the room box, a little deeper in y for the jamb)
    for rid, r in D["rooms"].items():
        pts = r["front"] + r["back"]
        xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
        mx, mz = 0.10 * (max(xs) - min(xs)), 0.10 * (max(zs) - min(zs))
        boxes.append([min(xs) - mx, max(xs) + mx, min(ys) - 0.7, max(ys) + 0.4, min(zs) - mz - 0.15, max(zs) + mz + 0.15])
    # links: the Bloom runs beside a link, never on it (axis-aligned segments + a margin)
    for e in D["edges"]:
        P = e["path"]
        for a, b in zip(P[:-1], P[1:]):
            lo = [min(a[i], b[i]) for i in range(3)]
            hi = [max(a[i], b[i]) for i in range(3)]
            boxes.append([lo[0] - 0.6, hi[0] + 0.6, lo[1] - 0.8, hi[1] + 0.8, lo[2] - 0.6, hi[2] + 0.6])
    boxes = [b for b in boxes if b[1] > fx - 30.0]
    cfg = dict(front_x=fx, seed=7, tend=24.0, tend_h=6.0, vscale=0.7, vw=0.045, ew=0.09, hatch_k=2.5, veins=1.1, edge=1.4, hatch=0.30,
               cover_k=0.89, plum=PLUM_LIN, pink=PINK_LIN, boxes=boxes, gap=gap,
               ribbons=dict(seed=11, n_ground=70, n_facade=36, width=0.09, strength=1.1, y0=-8.0, y1=11.0, z_ground=0.22, reach=24.0, fork=0.04,
                            facade_y=12.4, facade_h=7.0))
    if tune:
        cfg.update(tune)
    return cfg


STATE_TUNE = {"CREEPING": dict(ribbons=dict(seed=11, n_ground=70, n_facade=36, width=0.09, strength=0.6, y0=-8.0, y1=11.0, z_ground=0.22, reach=24.0, fork=0.04, facade_y=12.4, facade_h=7.0)),
              "CLOSE": {}, "CATCHING": dict(veins=1.45, hatch=0.40, plum=[0.085, 0.034, 0.066])}


def run(mode, state, res=1920, spp=48, tune=None):
    tune = tune or STATE_TUNE.get(state)
    env = dict(os.environ, BLOOM_SCR=BS, R2_OUT=os.path.join(BS, "street_" + state.lower()))
    os.makedirs(env["R2_OUT"], exist_ok=True)
    env.pop("BLOOM_CFG", None)
    if state != "CLEAN":
        cf = os.path.join(BS, "cfg_street_%s.json" % state.lower())
        json.dump(make_cfg(GAPS[state], tune), open(cf, "w"))
        env["BLOOM_CFG"] = cf
    if mode == "test":
        args = ["test", "1", "T_dec_closed", "res=%d" % res, "spp=%d" % spp]
    else:
        args = ["finals", "1", "dec_closed", "spp=%d" % spp]
    subprocess.run([sys.executable, os.path.join(HERE, "r2_jobs.py")] + args, env=env, check=False)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "cfg":
        json.dump(make_cfg(float(sys.argv[2])), open(sys.argv[3], "w"))
    elif w == "run":
        run(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 1920, int(sys.argv[5]) if len(sys.argv) > 5 else 48)


SBS = "D:/rc_art/art-pass/docs/concepts/route_map_graph/storyboard/scripts"
EXPO_DEC = 0.372            # the clean DECISION plate's solved exposure (street_r2 plates.json); the same exposure for every state


def plate(state, name, expo=EXPO_DEC, size=(1920, 1080)):
    """Post (street_r2 / storyboard post_aaa 'real') on a state's render with the clean plate's exposure. Returns (PIL image, values)."""
    import numpy as np
    sys.path.insert(1, SBS)
    import post_aaa as PA
    import sb_cams as SB
    d = os.path.join(BS, "street_" + state.lower())
    im = PA.finish(d, "real", shot=name, t=SB.T["b6"] - 0.1, over=dict(exposure=expo)).convert("RGB")
    im = im.resize(size)
    a = np.asarray(im, np.float32) / 255.0
    Lm = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return im, dict(median=round(float(np.median(Lm)), 4), under10=round(float((Lm < 0.10).mean()), 4), over85=round(float((Lm > 0.85).mean()), 4),
                    peak_p999=round(float(np.quantile(Lm, 0.999)), 3))


if __name__ == "__main__" and sys.argv[1] == "plate":
    im, v = plate(sys.argv[2], sys.argv[3])
    out = os.path.join(BS, "plate_%s_%s.png" % (sys.argv[2].lower(), sys.argv[3]))
    im.save(out)
    print(out, v)
