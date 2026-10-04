"""Delete cached renders in ../scratch/r whose names start with the given prefixes (or the whole scratch with 'all')."""
import os
import shutil
import sys

SCR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
if sys.argv[1:] == ["all"]:
    shutil.rmtree(SCR, ignore_errors=True)
else:
    rc = os.path.join(SCR, "r")
    for f in os.listdir(rc):
        if any(f.startswith(p) for p in sys.argv[1:]):
            os.remove(os.path.join(rc, f))
            print("removed", f)
