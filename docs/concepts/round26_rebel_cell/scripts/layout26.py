"""Round 26: export the city window round the Cell's palm (round 25 citydata.py rules) WITHOUT the round 25 base plot;
each idea decides in idea_cfg.py which buildings make way. -> ../scratch/layout/rc26.json
"""
import os

import citydata as CD

d = CD.load()
L = CD.Lots(d)
hq = CD.hq_centres(d)
palm = CD.rc_base_centre(d, L)
others = [(v, 5.6) for k, v in hq.items() if k != "rebel_cell"]
o = CD.export(d, L, palm, 80, others, os.path.join(CD.DST, "rc26.json"), extra=dict(corp="rebel_cell", kind="hq", hqs=hq))
print("rc26", palm, len(o["tiles"]), len(o["buildings"]), len(o["fist"]), "screen", L.iso(*palm))
