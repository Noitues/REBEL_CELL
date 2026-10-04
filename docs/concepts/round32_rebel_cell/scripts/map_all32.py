"""Round 32: every map render (4 stills + the ring blackout animation frames, home and DISPATCH). One child per job."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NF = 12
jobs = ["A:home", "A:dispatch", "A:home:ring:1.0", "A:dispatch:ring:1.0"]
for st in ("home", "dispatch"):
    for f in range(NF):
        p = min(1.0, f / (NF - 3))  # the blackout spreads over 9 frames, then holds (still flickering at the front)
        jobs.append("A:%s:ring:%.3f:%d" % (st, p, f))
for j in jobs:
    subprocess.run([sys.executable, os.path.join(HERE, "map32.py"), j], check=True)
