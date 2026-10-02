"""Remove this round's scratch/ folder (render caches, test frames) and nothing else."""
import os
import shutil

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
if os.path.basename(p) == "scratch" and os.path.isdir(p):
    shutil.rmtree(p)
    print("removed", p)
