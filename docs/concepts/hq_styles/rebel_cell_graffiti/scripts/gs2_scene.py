"""Blender wrapper: run the ORIGINAL F1b scene (round33/scripts/scene.py = round12 F1b + the red MAINFRAME sign hook, Eevee toon)
and inject the graffiti layer (gs2_extras.extras) before its figure/city/ground/lights are built. Nothing in round12/round33 is edited.

blender -b --factory-startup --python gs2_scene.py -- <out_prefix>     (env MF_SAMPLES, MF_PCT as in the original)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
R33 = os.path.join(CON, "round33_mainframe_sign", "scripts")
sys.path.insert(0, HERE)
import gs2_extras as GX

prefix = sys.argv[sys.argv.index("--") + 1]
os.environ.setdefault("MF_VAR", "b")
os.environ["MF_SIGN_PNG"] = "D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex2/sign_clean.png"
os.environ.setdefault("MF_SPILL", "#ff2a2a")
os.environ.setdefault("MF_SPILL_K", "1.0")
sys.argv = [sys.argv[0], "--", "f1", "night", prefix]
src = open(os.path.join(R33, "scene.py"), encoding="utf-8").read()
key = "    sign_and_spill_geo()\n    figure()"
assert key in src
src = src.replace(key, "    sign_and_spill_geo()\n    GX.extras(globals())\n    figure()", 1)
src = src.replace("    print('DONE', OUT)", "    print('DONE', OUT)", 1)
g = {"__file__": os.path.join(R33, "scene.py"), "__name__": "__main__", "GX": GX}
exec(compile(src, os.path.join(R33, "scene.py"), "exec"), g)
