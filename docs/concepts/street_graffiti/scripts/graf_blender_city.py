"""Blender-side wrapper for the whole-city panel: run city_build.py (A2 layout) with the graffiti hook patched in at run time.

blender -b --factory-startup --python graf_blender_city.py -- <mode> <cam> <outdir> <res_k> <spp>
Env: CITY_CPU=1 for a CPU run, GRAF_CFG='{"key": value}' for look overrides. Nothing on disk is edited.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
CITY = os.path.normpath(os.path.join(HERE, "..", "..", "city_all_corps", "scripts"))
SRC = os.path.join(CITY, "city_build.py")
sys.path.insert(0, CITY)
import graf_city  # noqa: E402,F401
import city_preset as _CP  # noqa: E402

for _k, _v in graf_city.CFG.get("aaa", {}).items():   # preset overrides (fog density etc.), in memory only
    _CP.AAA[_k] = _v

text = open(SRC, encoding="utf-8").read()
B = 'exec(open(os.path.join(HERE, _f), encoding="utf-8").read())'
assert B in text
text = text.replace(B, 'exec(__import__("graf_city").patch_src(_f, open(os.path.join(HERE, _f), encoding="utf-8").read()), globals())', 1)
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(text, SRC, "exec"), g)
