"""Rebuild every S2 sheet: Blender tiles -> Pillow sheets + contact sheet + layout.json.

  python build_all.py [samples]   (default 24; R2E_TMP picks the temp tile folder, deleted afterwards)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="s2t_", dir=os.environ.get("R2E_TMP"))
subprocess.run([sys.executable, os.path.join(HERE, "build_items.py"), TMP, sys.argv[1] if len(sys.argv) > 1 else "24"],
               check=True, timeout=3600)
subprocess.run([sys.executable, os.path.join(HERE, "sheets.py"), TMP, os.path.join(HERE, "..")], check=True, timeout=600)
shutil.rmtree(TMP, ignore_errors=True)
print("DONE")
