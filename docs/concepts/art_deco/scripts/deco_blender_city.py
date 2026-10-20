"""Blender-side wrapper for the whole-city panel: run city_build.py (A2 layout) with the deco hooks patched in at run time.

blender -b --factory-startup --python deco_blender_city.py -- <mode> <cam> <outdir> <res_k> <spp>
Env: CITY_CPU=1 for a CPU run, DECO_CFG='{"key": value}' for deco overrides.
Hooks (text patches of the exec'd sources, nothing on disk is edited):
  1. before `def building(b):` in city_build.py   -> prism() is wrapped so every tower body is recorded
  2. city_render.py, before the final `stem = ...`   -> deco_city.apply_city(globals()): materials, landmarks, fans, fog
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
CITY = os.path.normpath(os.path.join(HERE, "..", "..", "city_all_corps", "scripts"))
SRC = os.path.join(CITY, "city_build.py")
sys.path.insert(0, CITY)
import deco_city as DC  # noqa: E402

DC._prep_preset()
text = open(SRC, encoding="utf-8").read()
A = "def building(b):\n"
assert A in text
text = text.replace(A, "import deco_city as _DC\nprism = _DC.wrap_prism(prism)\n\n" + A, 1)
B = 'exec(open(os.path.join(HERE, _f), encoding="utf-8").read())'
assert B in text
text = text.replace(B, 'exec(_DC.patch_src(_f, open(os.path.join(HERE, _f), encoding="utf-8").read()), globals())', 1)
sys.argv = sys.argv  # city_build reads sys.argv after "--"
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(text, SRC, "exec"), g)
