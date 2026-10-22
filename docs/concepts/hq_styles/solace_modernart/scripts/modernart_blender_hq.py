"""Blender-side wrapper: exec the Solace pipeline's hq_scene.py with the modernart hook in front of its render section.
blender -b --factory-startup --python modernart_blender_hq.py -- job.json"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "art_deco", "scripts"))   # read-only import of deco_restyle helpers
sys.path.insert(0, HERE)
sys.path.insert(0, DECO)
sys.dont_write_bytecode = True
JOBP = sys.argv[sys.argv.index("--") + 1]
JOBD = json.load(open(JOBP))
SRC = JOBD["scene_src"]
text = open(SRC, encoding="utf-8").read()
MARK = "# ================================================================== render"
assert MARK in text, "render marker not found"
HOOK = "import modernart_restyle as _NR\n_NR.apply(globals(), JOB.get('deco', {}))\n"
text = text.replace(MARK, HOOK + MARK, 1)
g = {"__name__": "__main__", "__file__": SRC}
sys.path.insert(0, os.path.dirname(SRC))
exec(compile(text, SRC, "exec"), g)
