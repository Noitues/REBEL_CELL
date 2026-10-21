"""Blender-side wrapper for the street panel: r2_scene.py with the graffiti hook patched into its r2_cycles.py exec.

blender -b --factory-startup --python graf_blender_street.py -- meridian_hq <outdir> <cams.json> <job.json>
Env: NET36=net_scope.json, GRAF_CFG (json), GRAF_CPU=1.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
ST = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph", "street_r2", "scripts"))
SRC = os.path.join(ST, "r2_scene.py")
sys.path.insert(0, ST)
import graf_street  # noqa: E402,F401

text = open(SRC, encoding="utf-8").read()
K = 'exec(open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read())'
assert K in text
text = text.replace(K, 'exec(__import__("graf_street").patch_cycles(open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read()))', 1)
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(text, SRC, "exec"), g)
