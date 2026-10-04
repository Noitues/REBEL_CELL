"""Round 34: map stills (A + ring, home / DISPATCH) and the REVEAL frames: the sector starts fully lit (the hand washed
out), then the blackout ring and the hand's black lines go dark and the fist appears. One child process per job."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
Q = [0.0, 0.0, 0.0, 0.1, 0.22, 0.36, 0.5, 0.64, 0.78, 0.9, 1.0, 1.0, 1.0, 1.0]
jobs = ["A:home", "A:dispatch", "A:home:ring:1.0", "A:dispatch:ring:1.0"]
for st in ("home", "dispatch"):
    for f, q in enumerate(Q):
        jobs.append("A:%s:reveal:%.3f:%d" % (st, q, f))
for j in (sys.argv[1:] or jobs):
    subprocess.run([sys.executable, os.path.join(HERE, "map34.py"), j], check=True)
