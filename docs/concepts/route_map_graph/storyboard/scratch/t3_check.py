"""Finish the v3-r3 calibration renders: python t3_check.py <tag> [exposure]"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
sys.dont_write_bytecode = True
import numpy as np
import post_aaa as PA
import sb_frames as SF
import sb_ocjobs as OJ
H = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1]
ex = float(sys.argv[2]) if len(sys.argv) > 2 else 1.1
D = OJ.derive()
im = PA.finish(OJ.OUTC, "real", shot="T3_ov", t=13.45, over=dict(exposure=ex))
l = np.asarray(im.convert("L"), np.float32) / 255
print("T3_ov exp %.2f median %.3f <0.10 %.1f%% p95 %.3f" % (ex, np.median(l), (l < 0.10).mean() * 100, np.percentile(l, 95)))
im.save(os.path.join(H, "t3_%s_ov.png" % tag))
s, c, e = OJ.full_at(300, D)
z = OJ.zoom_of(c, D)
o = SF.post_over("dive", z)
o["exposure"] = o.get("exposure", 2.0) + (ex - 2.4) * OJ.look_w(z)
im = PA.finish(OJ.OUTC, "real", shot="T3_0300", t=12.5, over=o)
im.save(os.path.join(H, "t3_%s_0300.png" % tag))
