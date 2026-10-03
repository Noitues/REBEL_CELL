"""Round 29: every Blender job + finish pass, in order (each Blender run is a child of this process; nothing else is
touched). python render_all28.py [stills] [gif]"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
NFR = 12


def run(jobs, **env):
    e = dict(os.environ)
    for k in ("PAINT28", "TAG28", "CAMSET28", "FRAME28", "RES28"):
        e.pop(k, None)
    e.update({k: str(v) for k, v in env.items()})
    subprocess.run([PY, os.path.join(HERE, "run29.py")] + jobs, env=e, check=True)


def post(tag, *extra):
    subprocess.run([PY, os.path.join(HERE, "post29.py"), tag] + list(extra), check=True)


what = sys.argv[1:] or ["stills", "gif"]
if "street" in what:
    run(["canyon:close", "canyon:close:dispatch"], CAMSET28="street", TAG28="_street")
    post("rc29_canyon_street", "--street")
    post("rc29_canyon_dispatch_street", "--street")
if "stills" in what:
    run(["canyon:close", "canyon:close:dispatch"])
    post("rc29_canyon")
    post("rc29_canyon_dispatch")
    run(["canyon:close", "canyon:close:dispatch"], CAMSET28="street", TAG28="_street")
    post("rc29_canyon_street", "--street")
    post("rc29_canyon_dispatch_street", "--street")
if "gif" in what:
    for f in range(NFR):
        run(["canyon:close:dispatch"], FRAME28=f, TAG28="_f%02d" % f, RES28="1440,810")
        post("rc29_canyon_dispatch_f%02d" % f, "--rain", str(100 + f))
