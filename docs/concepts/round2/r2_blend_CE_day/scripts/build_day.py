"""Render the C x E blend day city -> ../city_day.png

  python build_day.py [samples]   (default 32; set R2E_TMP to choose the temp folder)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SAMPLES = sys.argv[1] if len(sys.argv) > 1 else "32"
TMP = tempfile.mkdtemp(prefix="r2b_", dir=os.environ.get("R2E_TMP"))
raw = os.path.join(TMP, "day.png")
with open(os.path.join(TMP, "day.log"), "w") as f:
    subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "scene_city.py"), "--",
                    raw, "day", SAMPLES, "1"], stdout=f, stderr=subprocess.STDOUT, timeout=900, check=True)
subprocess.run([sys.executable, os.path.join(HERE, "post.py"), "city", raw, os.path.join(ROOT, "city_day.png"), "day"],
               check=True, timeout=300)
if "--keep" not in sys.argv:
    shutil.rmtree(TMP, ignore_errors=True)
print("DONE")
