"""Blender-side wrapper: exec the HQ pipeline's hq_scene.py with the deco hook in front of its render section.

blender -b --factory-startup --python deco_blender_hq.py -- job.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
JOBP = sys.argv[sys.argv.index("--") + 1]
JOBD = json.load(open(JOBP))
SRC = JOBD["scene_src"]
text = open(SRC, encoding="utf-8").read()
MARK = "# ================================================================== render"
assert MARK in text, "render marker not found"
HOOK = ("import deco_restyle as _DR\n_DR.apply_hq(globals(), JOB.get('deco', {}))\n")
text = text.replace(MARK, HOOK + MARK, 1)
g = {"__name__": "__main__", "__file__": SRC}
sys.path.insert(0, os.path.dirname(SRC))
exec(compile(text, SRC, "exec"), g)
