"""Blender entry: blender -b --factory-startup --python rat_blender.py -- job.json
Loads the Aurelian corp modules (aur_env), patches them in memory (rat_patch), then execs the engine's hq_scene.py with the
rationalist hook (rat_style.apply) inserted in front of its render section."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
JOBD = json.load(open(sys.argv[sys.argv.index("--") + 1]))
AUR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_aurelian", "scripts"))
sys.path.insert(0, AUR)
import aur_env  # noqa: E402
aur_env.setup(blender=True)
sys.path.insert(0, HERE)
import rat_patch  # noqa: E402
rat_patch.apply_pre(JOBD.get("rat", {}))
if JOBD.get("rat", {}).get("v4"):
    import rat_patch4
    rat_patch4.apply_pre(JOBD.get("rat", {}))
elif JOBD.get("rat", {}).get("v2"):
    import rat_patch2
    rat_patch2.apply_pre(JOBD.get("rat", {}))
SRC = os.path.join(aur_env.V3, "hq_scene.py")
text = open(SRC, encoding="utf-8").read()
MARK = "# ================================================================== render"
assert MARK in text
HOOK = "import rat_style as _RS\n_RS.apply(globals(), JOB.get('rat', {}))\n"
text = text.replace(MARK, HOOK + MARK, 1)
exec(compile(text, SRC, "exec"), {"__name__": "__main__", "__file__": SRC})
