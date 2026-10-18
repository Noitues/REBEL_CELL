import importlib
import inspect
import pkgutil
import sys

import netrun_art


def _modules():
    names = []
    for m in pkgutil.walk_packages(netrun_art.__path__, "netrun_art."):
        if ".tests" in m.name or m.name.endswith("__main__"):
            continue
        names.append(m.name)
    return sorted(names)


def test_import_with_bpy_blocked():
    saved = sys.modules.get("bpy", "absent")
    sys.modules["bpy"] = None  # any `import bpy` now raises ImportError
    try:
        names = _modules()
        for must in ("layout", "zoning", "derive.street", "hq.slots", "rig", "lod", "occlusion", "section", "states", "dress",
                     "seeds", "io", "poses", "contract"):
            assert "netrun_art." + must in names, must
        for name in ["netrun_art"] + names:
            sys.modules.pop(name, None)
        for name in ["netrun_art"] + names:
            importlib.import_module(name)
    finally:
        if saved == "absent":
            sys.modules.pop("bpy", None)
        else:
            sys.modules["bpy"] = saved


def test_modules_under_600_lines_and_documented():
    for name in _modules():
        mod = importlib.import_module(name)
        src = inspect.getsource(mod)
        assert src.count("\n") <= 600, name
        assert mod.__doc__, name
        for fn_name, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__ == name and not fn_name.startswith("_"):
                assert fn.__doc__, f"{name}.{fn_name}"
