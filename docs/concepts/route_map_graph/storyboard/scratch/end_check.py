import os, sys
sys.path.insert(0, r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts")
import numpy as np
import post_aaa as PA
import sb_ocjobs as OJ
import sb_ui as U
S = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\\"
os.makedirs(S + "test_frames", exist_ok=True)
for ex in [float(v) for v in sys.argv[1:]] or [2.4]:
    for nm in ("E_closed", "E_open"):
        im = PA.finish(OJ.OUTC, "real", shot=nm, t=13.45, over=dict(exposure=ex))
        l = np.asarray(im.convert("L"), np.float32) / 255
        print("exp %.2f %s median %.3f p95 %.3f <0.10 %.1f%% >0.85 %.2f%%" % (ex, nm, np.median(l), np.percentile(l, 95),
              (l < 0.10).mean() * 100, (l > 0.85).mean() * 100))
        im.save(S + "scratch\\end_%s_%.2f.png" % (nm, ex))
