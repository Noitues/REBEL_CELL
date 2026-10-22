"""Debug: v4 bay widths per tier (equal arc-length piers), no Blender."""
import math
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AUR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_aurelian", "scripts"))
sys.path.insert(0, AUR)
import aur_env
aur_env.setup()
sys.path.insert(0, HERE)
import aurelian_landmark as AL
import hq_graph as G
import rat_patch4 as P4
AL.ARC_PIER_H = 0.78
AL.ENTRY_OPEN = 2.6
bays = AL.bays_for(G.SLOTS) + list(AL.portal_arcs(getattr(G, "CONCEPT", "R")))
print("openings", len(bays), "portal t", round(AL.ENTRY_T, 1), [round(g["t"], 1) for g in AL.gates(getattr(G, "CONCEPT", "R")) if g["kind"] == "outer"])
for k in range(3):
    piers = P4.uniform_piers(AL.A, AL.BK, 60, [(t0, t1) for (kb, t0, t1) in bays if kb == k])
    n = len(piers)
    ws = []
    for i in range(n):
        ta, ha = piers[i]
        tb, hb = piers[(i + 1) % n]
        if tb <= ta:
            tb += 2 * math.pi
        rate = AL._arc_rate(AL.A, AL.BK, (ta + tb) / 2)
        ws.append((round(math.degrees(ta) % 360, 1), round((tb - ta) * rate - ha - hb, 2)))
    print("tier", k, "piers", n, "min", min(w for _, w in ws), "max", max(w for _, w in ws))
    print("  odd widths (not 1.3-1.6):", [x for x in ws if not 1.3 <= x[1] <= 1.6])
