"""Round 33: export the Cell's district (fist streets removed, grid completed: grid27.py) for hq33.py
-> ../scratch/layout/rc27.json"""
import os

import citydata as CD
import grid27

d = CD.load()
info = grid27.patch(d)
L = CD.Lots(d)
hq = CD.hq_centres(d)
palm = info["palm"]
others = [(v, 5.6) for k, v in hq.items() if k != "rebel_cell"]
os.makedirs(CD.DST, exist_ok=True)
o = CD.export(d, L, palm, 80, others, os.path.join(CD.DST, "rc27.json"), extra=dict(corp="rebel_cell", kind="hq", hqs={k: v for k, v in hq.items() if k != "rebel_cell"}))
print("rc27", palm, "new street cells", info["new_cells"], "filled lots", info["filled"], "tiles", len(o["tiles"]), "blds", len(o["buildings"]))
