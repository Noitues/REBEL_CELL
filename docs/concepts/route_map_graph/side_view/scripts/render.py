"""Run the Blender street scene headless.  python render.py <side|tq> [preview]
Writes the passes into ../scratch/bl and the Blender log into ../scratch/bl_<cam>.log (never piped)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(os.path.dirname(HERE), "scratch")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import sgraph  # noqa: E402

cam = sys.argv[1]
extra = sys.argv[2:]
os.makedirs(os.path.join(SCR, "bl"), exist_ok=True)
lay = os.path.join(SCR, "layout.json")
sgraph.dump(lay)
log = os.path.join(SCR, "bl_%s.log" % cam)
with open(log, "w") as f:
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "street_scene.py"), "--", lay,
                        os.path.join(SCR, "bl"), cam] + extra, stdout=f, stderr=subprocess.STDOUT)
print("exit", r.returncode, "log", log)
