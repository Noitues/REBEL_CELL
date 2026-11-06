import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
sys.dont_write_bytecode = True
import sb_ocjobs as OJ
D = OJ.derive()
for k in ("fc_dive", "fc_move", "fc_street"):
    fr = OJ.full_jobs(k, D)
    print(k, len(fr), fr[0]["name"], fr[-1]["name"])
