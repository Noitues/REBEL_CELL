import sys, os
sys.path.insert(0, r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scripts")
import sb_ocjobs as OJ
D = OJ.derive()
OJ.run(os.path.join(OJ.SCR, "oc_dry"), [], OJ.oc_block("cycles", D, frames=[], spp=1), "dryc")
