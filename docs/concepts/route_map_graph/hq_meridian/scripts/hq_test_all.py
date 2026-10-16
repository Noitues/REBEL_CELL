"""HQ others: ONE GPU-locked batch of Cycles test frames for several corps (1280 x 720, 'test' quality), each composed
into its ../scratch/test/ (stills, with the value checks) or ../scratch/<FN>/ (shot lists), the lock held here.

python hq_test_all.py meridian:H_overview,H_decision solace:H_overview rebel_cell:@OPTION_SHOTS rebel_cell:@RED_SHOTS!
  corp:names       stills through that corp's hq_test.py
  corp:@FN         the shot list G.FN (hq_jobs.py shots FN test), composed after the lock is released
  a trailing '!'   renders with HQ_DISTRICT_ONLY=1 (Rebel Cell's whole-district build)
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpu_lock  # noqa: E402

BASE = os.path.dirname(os.path.dirname(HERE))
jobs = [a.split(":", 1) for a in sys.argv[1:]]
gpu_lock.acquire("test frames " + " ".join(a for a in sys.argv[1:]))
later = []
try:
    for corp, names in jobs:
        d = os.path.join(BASE, "hq_" + corp, "scripts")
        env = dict(os.environ, HQ_LOCK_HELD="1")
        dist = names.endswith("!")
        names = names.rstrip("!")
        if dist:
            env["HQ_DISTRICT_ONLY"] = "1"
        t0 = time.time()
        log = os.path.join(BASE, "hq_" + corp, "scratch", "test_run_%s.log" % names.replace(",", "_").replace("@", ""))
        with open(log, "w") as f:
            if names.startswith("@"):
                fn = names[1:]
                subprocess.run([sys.executable, "hq_jobs.py", "shots", fn, "test"], cwd=d, env=env, stdout=f,
                               stderr=subprocess.STDOUT)
                later.append((d, env, fn))
            else:
                subprocess.run([sys.executable, "hq_test.py", names, "test"], cwd=d, env=env, stdout=f,
                               stderr=subprocess.STDOUT)
        print(corp, names, "%.0f s" % (time.time() - t0), flush=True)
finally:
    gpu_lock.release()
for d, env, fn in later:
    big = os.path.join(r"D:\rc_scratch", "hq_" + os.path.basename(os.path.dirname(d))[3:], "bl_%s_test" % fn)
    subprocess.run([sys.executable, "hq_compose.py", fn, "all", big], cwd=d, env=env)
print("done", flush=True)
