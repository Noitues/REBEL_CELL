import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
os.chdir(os.path.join(HERE, "..", "scripts"))
import sb_onecity as OC
D = json.load(open(os.path.join(HERE, "oc_derive.json")))
for nm in ("overview", "decision"):
    c = D[nm]
    pts = [p for r in D["rooms"].values() for p in r["front"]]
    q = [OC.proj(c, p) for p in pts]
    print(nm, "pitch", c["pitch"], "dist %.1f" % c["dist"], "loc", [round(v, 1) for v in c["persp"]["loc"]], "sy %.3f" % c["persp"]["sy"],
          "rooms y %.0f..%.0f x %.0f..%.0f" % (min(p[1] for p in q), max(p[1] for p in q), min(p[0] for p in q), max(p[0] for p in q)), "span", D["span"])
