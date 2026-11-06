import sys, os
sys.path.insert(0, r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts")
import sb_ocjobs as OJ
D = OJ.derive()
cams = []
for u, tag, op in ((1.0, "p_street", True), (0.0, "p_hq", False)):
    c = OJ.pose_at(u, D)
    cams.append(dict(tag=tag, persp=dict(loc=c["persp"]["loc"], tgt=c["persp"]["tgt"], lens=c["persp"]["lens"], sx=c["persp"]["sx"], sy=c["persp"]["sy"]),
                     res=[960, 540], samples=4, zcut=OJ.zcut(OJ.zoom_of(c, D)), dis={i: 1.0 for i in D["rooms"]} if op else {}))
OJ.run(os.path.join(OJ.SCR, "oc_prev"), cams, OJ.oc_block("mainline", D), "prev")
