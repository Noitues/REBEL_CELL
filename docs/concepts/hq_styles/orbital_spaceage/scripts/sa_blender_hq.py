"""Blender-side wrapper: exec the Orbital HQ pipeline's hq_scene.py with the space-age hook in front of its render section.
blender -b --factory-startup --python sa_blender_hq.py -- job.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
JOBD = json.load(open(sys.argv[sys.argv.index("--") + 1]))
SRC = JOBD["scene_src"]
text = open(SRC, encoding="utf-8").read()
MARK = "# ================================================================== render"
assert MARK in text, "render marker not found"
HOOK = "import sa_restyle as _SA\n_SA.apply(globals(), JOB.get('sa', {}))\n"
text = text.replace(MARK, HOOK + MARK, 1)
g = {"__name__": "__main__", "__file__": SRC}
sys.path.insert(0, os.path.dirname(SRC))
exec(compile(text, SRC, "exec"), g)
