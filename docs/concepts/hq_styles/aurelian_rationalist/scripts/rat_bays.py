"""Debug: list the arcade bay (opening) widths per tier for the HQ's room bays + portals (no Blender)."""
import math
import os
import sys
sys.dont_write_bytecode = True
AUR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "route_map_graph", "hq_aurelian", "scripts"))
sys.path.insert(0, AUR)
import aur_env
aur_env.setup()
import aurelian_landmark as AL
import hq_graph as G

bays = AL.bays_for(G.SLOTS) + list(AL.portal_arcs(getattr(G, "CONCEPT", "R")))
print("room/portal bays", len(bays), "entry t", round(AL.ENTRY_T, 1))
for k in range(3):
    piers = AL.arcade_piers(AL.A, AL.BK, 60, [(t0, t1) for (kb, t0, t1) in bays if kb == k])
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
    print("  narrow (<0.95):", [x for x in ws if x[1] < 0.95])
    print("  wide (>1.8):", [x for x in ws if x[1] > 1.8])
