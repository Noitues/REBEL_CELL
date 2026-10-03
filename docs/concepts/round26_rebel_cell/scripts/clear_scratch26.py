"""Round 26: remove this round's own scratch folder and caches (only paths inside round26_rebel_cell)."""
import os
import shutil

R26 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for p in [os.path.join(R26, "scratch")] + [os.path.join(dp, d) for dp, dn, _ in os.walk(os.path.join(R26, "scripts")) for d in dn
                                           if d in ("__pycache__", "scratch")]:
    if os.path.isdir(p) and os.path.normpath(p).startswith(R26):
        shutil.rmtree(p)
        print("removed", p)
