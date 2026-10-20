"""Blender-side wrapper for the street panel: r2_scene.py with the deco hook patched into its r2_cycles.py exec.

blender -b --factory-startup --python deco_blender_street.py -- meridian_hq <outdir> <cams.json> <job.json>
Env: NET36=net_scope.json, DECO_CFG (json), DECO_CPU=1, DECO_OFF=1 (baseline: no hook).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
ST = os.path.normpath(os.path.join(HERE, "..", "..", "route_map_graph", "street_r2", "scripts"))
SRC = os.path.join(ST, "r2_scene.py")
sys.path.insert(0, ST)
import deco_street as DS  # noqa: E402

text = open(SRC, encoding="utf-8").read()
K = 'exec(open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read())'
assert K in text
if os.environ.get("DECO_OFF"):
    rep = 'exec(open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read().replace(\'cy.device = "GPU"\', \'cy.device = "CPU"\') if os.environ.get("DECO_CPU") else open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read())'
else:
    rep = 'exec(__import__("deco_street").patch_cycles(open(os.path.join(_ME, "r2_cycles.py"), encoding="utf-8").read()))'
text = text.replace(K, rep, 1)
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(text, SRC, "exec"), g)
