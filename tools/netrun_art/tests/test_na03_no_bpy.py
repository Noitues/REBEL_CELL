import importlib
import sys


def test_import_with_bpy_blocked():
    saved = sys.modules.get("bpy", "absent")
    sys.modules["bpy"] = None  # any `import bpy` now raises ImportError
    try:
        for name in ("netrun_art", "netrun_art.seeds", "netrun_art.io"):
            sys.modules.pop(name, None)
            importlib.import_module(name)
    finally:
        if saved == "absent":
            sys.modules.pop("bpy", None)
        else:
            sys.modules["bpy"] = saved
