"""Blender-side wrapper: exec the HQ pipeline's hq_scene.py with the deco hook in front of its render section.

blender -b --factory-startup --python deco_blender_hq.py -- job.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import time

import bpy

_HB = os.path.join(os.path.dirname(os.path.abspath(sys.argv[sys.argv.index("--") + 1])), "heartbeat.txt")
_HB_LAST = [0.0]


@bpy.app.handlers.persistent
def _heartbeat(*a):
    """Render progress marker for the GPU watchdog (mg_gpu.py): touched at most every 10 s while Cycles reports stats."""
    t = time.time()
    if t - _HB_LAST[0] > 10.0:
        _HB_LAST[0] = t
        try:
            with open(_HB, "w") as f:
                f.write("%.0f" % t)
        except OSError:
            pass


for _h in ("render_stats", "render_post", "render_init"):
    try:
        getattr(bpy.app.handlers, _h).append(_heartbeat)
    except AttributeError:
        pass
JOBP = sys.argv[sys.argv.index("--") + 1]
JOBD = json.load(open(JOBP))
SRC = JOBD["scene_src"]
text = open(SRC, encoding="utf-8").read()
MARK = "# ================================================================== render"
assert MARK in text, "render marker not found"
HOOK = "import %s as _DR\n_DR.apply_hq(globals(), JOB.get('deco', {}))\n" % os.environ.get("MG_RESTYLE", "mg_restyle_v2" if os.path.exists(r"D:/rc_scratch/hq_styles/meridian_mughal/USE_V2") else "mg_restyle")
text = text.replace(MARK, HOOK + MARK, 1)
g = {"__name__": "__main__", "__file__": SRC}
sys.path.insert(0, os.path.dirname(SRC))
exec(compile(text, SRC, "exec"), g)
