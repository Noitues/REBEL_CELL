"""Aurelian HQ: the Blender entry. Loads the Aurelian corp modules, then runs Meridian v3's engine hq_scene.py in place
(no copy). blender -b --factory-startup --python hq_scene.py -- <job.json>"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aur_env  # noqa: E402

aur_env.setup(blender=True)
_SRC = os.path.join(aur_env.V3, "hq_scene.py")
exec(compile(open(_SRC, encoding="utf-8").read(), _SRC, "exec"), {"__name__": "__main__", "__file__": _SRC})
