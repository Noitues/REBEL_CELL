"""Blender-side wrapper: run the Tethys base build (tethys_build.py) with the pier city re-grown in an abyssal bioluminescent style.

blender -b --factory-startup --python abyssal_build.py -- <mode> <cam> <outdir> [res_k] [spp]
The base files are never edited: tethys_landmark.py is read as text, four hooks are substituted (the station generator,
the walkway generator, the breakwater and buoy details), and the patched module is registered before tethys_build.py runs.
Env: TETHYS_SCR (scratch for the base), TETHYS_CPU=1 (CPU preview).
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_tethys", "scripts"))
sys.dont_write_bytecode = True
sys.path.insert(0, BASE)
sys.path.insert(0, HERE)
import tethys_preset as TP  # noqa: E402
import abyssal as AB  # noqa: E402

# the preset points at an old C: worktree; use this one (run time only)
TP.WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
TP.CONCEPTS = os.path.join(TP.WT, "docs", "concepts")
TP.OUT = os.path.join(TP.CONCEPTS, "route_map_graph", "hq_tethys")
TP.CITY_SCRIPTS = os.path.join(TP.OUT, "scripts", "city_base")
TP.FONTS = os.path.join(TP.WT, "assets", "fonts")
sys.path.insert(1, TP.CITY_SCRIPTS)
import city_preset as CP  # noqa: E402
_OLD = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"


def _fix(v):
    if isinstance(v, str):
        return TP.WT + v[len(_OLD):] if v.startswith(_OLD) else v
    if isinstance(v, dict):
        for k_ in v:
            v[k_] = _fix(v[k_])
    elif isinstance(v, list):
        v[:] = [_fix(x) for x in v]
    return v


for _k in [k for k in dir(CP) if not k.startswith("__")]:
    setattr(CP, _k, _fix(getattr(CP, _k)))
# ---- palette / world tweaks (run time only)
P = TP.PIER
P["hull"] = (0.78, 0.68, 0.80)
P["hull_dark"] = (0.24, 0.20, 0.30)
P["titan"] = (0.34, 0.30, 0.44)
P["stilt"] = (0.15, 0.12, 0.19)
P["key"] = dict(power=0.9e6, cone=26.0, col=(0.70, 0.92, 1.0))
TP.WET_LIT = float(os.environ.get("ABY_WET_LIT", "0.40"))      # the drowned city a little darker, so the HQ wins
TP.DAM["flood_power"] *= 0.5
TP.DAM["up_power"] *= 0.45

src = open(os.path.join(BASE, "tethys_landmark.py"), encoding="utf-8").read()


def sub(old, new):
    global src
    assert old in src, old[:60]
    src = src.replace(old, new, 1)


sub("def _stack(ns, cx, cy, s, hs, zb, bed, PR, bid, full=True, main=False):",
    "def _stack(ns, cx, cy, s, hs, zb, bed, PR, bid, full=True, main=False):\n    return AB.stack(ns, cx, cy, s, hs, zb, bed, PR, bid, full, main)\n\n\n"
    "def _stack_old(ns, cx, cy, s, hs, zb, bed, PR, bid, full=True, main=False):")
sub("    def walk(p0, p1, rt=1.0):",
    "    def walk(p0, p1, rt=1.0):\n        return AB.walk(ns, p0, p1, rt, ZW + PR['deck_z'], bed_at, PR)\n\n    def _walk_old(p0, p1, rt=1.0):")
sub('seg_box(SURF, (x0, y0), (x1, y1), BW["w"], ZW + BW["z0"], ZW + BW["z1"], PR["hull_dark"], wet=1)',
    'seg_box(SURF, (x0, y0), (x1, y1), BW["w"], ZW + BW["z0"], ZW + BW["z1"], PR["hull_dark"], wet=1)\n'
    '        AB.crust_breakwater(ns, x0, y0, x1, y1, random.Random(int(x0 * 7 + y0 * 3)))')
sub("cyl(SURF, x, y, ZW - 0.6, ZW + 0.5, 0.35, 8, (0.62, 0.20, 0.22))", "AB.buoy(ns, x, y, k, ZW, hx, hy)")
m = types.ModuleType("tethys_landmark")
m.__file__ = os.path.join(BASE, "tethys_landmark.py")
m.AB = AB
sys.modules["tethys_landmark"] = m
exec(compile(src, m.__file__, "exec"), m.__dict__)

BB = os.path.join(BASE, "tethys_build.py")
g = {"__name__": "__main__", "__file__": BB}
exec(compile(open(BB, encoding="utf-8").read(), BB, "exec"), g)
