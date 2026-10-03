"""Round 27: run Blender jobs. python run26.py <idea>:<view>[:dispatch] ...   (view: close | map | preview)
Close/preview passes -> ../scratch/bl, map sprites -> ../scratch/map; logs in ../scratch/logs."""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "scratch")
BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
os.makedirs(os.path.join(SC, "logs"), exist_ok=True)
for job in sys.argv[1:]:
    parts = job.split(":")
    idea, view = parts[0], parts[1]
    state = parts[2] if len(parts) > 2 else ""
    out = os.path.join(SC, "map" if view == "map" else "bl")
    log = os.path.join(SC, "logs", "%s_%s_%s.log" % (idea, view, state))
    t = time.time()
    with open(log, "w") as fh:
        subprocess.run([BL, "-b", "--factory-startup", "--python", os.path.join(HERE, "hq27.py"), "--", "rebel_cell_hq", out, view, idea]
                       + ([state] if state else []), stdout=fh, stderr=subprocess.STDOUT)
    txt = open(log, encoding="utf-8", errors="replace").read()
    ok = "DONE" in txt
    print(job, "ok" if ok else "FAILED", "%.0fs" % (time.time() - t), flush=True)
    if not ok:
        i = txt.find("Traceback")
        print(txt[i:i + 2500] if i >= 0 else txt[-2500:])

