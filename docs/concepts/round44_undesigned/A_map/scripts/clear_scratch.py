"""Round 40: clear this round's scratch/ (and the scripts' __pycache__) only."""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [os.path.join(ROOT, "scratch")] + [os.path.join(d, "__pycache__") for d in (os.path.join(ROOT, "scripts"), os.path.join(ROOT, "scripts", "raidui"))]:
    if os.path.isdir(p):
        shutil.rmtree(p)
        print("removed", p)
