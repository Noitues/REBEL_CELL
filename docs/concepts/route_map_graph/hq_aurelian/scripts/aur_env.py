"""Aurelian HQ: the import environment. The corp modules here (hq_preset, hq_graph, hq_build, hq_mechui,
aurelian_landmark) are loaded FIRST, then the engine runs from Meridian v3's scripts in place (no copies) and the kit
from hq_meridian/scripts/hq_kit (the shared one). The engine modules insert their own dir on sys.path when imported,
but every corp module name is already in sys.modules by then, so the engine always gets the Aurelian ones.

    import aur_env; aur_env.setup()        # before importing any engine module
"""
import os
import sys

sys.dont_write_bytecode = True
AUR = os.path.dirname(os.path.abspath(__file__))
ROUTE = os.path.normpath(os.path.join(AUR, "..", ".."))
V3 = os.path.join(ROUTE, "hq_meridian_v3", "scripts")
KIT = os.path.join(ROUTE, "hq_meridian", "scripts")
ROOT = os.path.dirname(AUR)
SCR = os.path.join(ROOT, "scratch")
BIG = r"D:\rc_scratch\aurelian\big"
CORP_MODULES = ("hq_preset", "aurelian_landmark", "hq_graph", "hq_build", "hq_mechui")


def setup(blender=False):
    if "hq_kit" not in sys.modules:
        sys.path.insert(0, KIT)
        import hq_kit  # noqa: F401
        from hq_kit import states, downtown, section, city_ring, lod  # noqa: F401
        sys.path.remove(KIT)
    for p in (V3, AUR):
        if p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, V3)
    sys.path.insert(0, AUR)
    for m in CORP_MODULES:
        if blender and m == "hq_mechui":           # the overlay's UI module (PIL) is not needed inside Blender
            continue
        __import__(m)
    os.makedirs(SCR, exist_ok=True)
    os.makedirs(BIG, exist_ok=True)
