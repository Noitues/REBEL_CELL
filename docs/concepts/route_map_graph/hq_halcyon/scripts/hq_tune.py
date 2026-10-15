"""Post-only value tuning: re-finish the final still passes with trial post keys and print the r3 value stats.
python hq_tune.py key=value ...   (e.g. exposure=3.2 exposure_zoom_k=0.6 black=0.03 knee_top=0.86)"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_post as PO  # noqa: E402

BIG = r"D:\rc_scratch\halcyon"
ROOT = os.path.dirname(HERE)
ovs = json.load(open(os.path.join(ROOT, "scratch", "ov_stills.json")))
for kv in sys.argv[1:]:
    k, _, v = kv.partition("=")
    PO.P[k] = float(v)
for name in ("H_overview", "H_decision_S", "H_decision_E", "H_hover_S", "H_hover_E"):
    stem = os.path.join(BIG, "bl_stills", name)
    if not os.path.exists(stem + "_combined.npy"):
        continue
    im = PO.finish(stem, ovs[name]["zoom"]).resize((1280, 720))
    a = np.asarray(im, np.float32) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    print("%-14s median %.3f  <0.10 %.1f %%  >0.85 %.2f %%" % (name, np.median(L), (L < 0.1).mean() * 100,
                                                            (L > 0.85).mean() * 100))
