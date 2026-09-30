"""Render the wide gritty-E city with the helix HQ -> ../city_day.png and ../hq_closeup.png

  python build_wide.py [samples]     (default 32; R2E_TMP picks the temp folder)
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
TMP = tempfile.mkdtemp(prefix="r2ew_", dir=os.environ.get("R2E_TMP"))
with open(os.path.join(TMP, "wide.log"), "w") as f:
    subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "scene_wide.py"), "--", TMP, SAMPLES],
                   stdout=f, stderr=subprocess.STDOUT, timeout=900, check=True)
subprocess.run([sys.executable, os.path.join(HERE, "post_wide.py"), TMP, ROOT], check=True, timeout=300)
shutil.rmtree(TMP, ignore_errors=True)
print("DONE")
