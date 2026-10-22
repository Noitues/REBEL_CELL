"""Run the Tethys base build with one of the five idea blockouts (env IDEA=A..E; FLAP, BANK for E).
blender -b --factory-startup --python ideas_build.py -- aaa t_over <outdir> <res_k> <spp>
Reuses the abyssal wrapper (run-time patching of the base pipeline, cooled dam) and swaps the landmark for ideas.landmark()."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AB_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "tethys_abyssal", "scripts"))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
sys.path.insert(0, AB_DIR)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_tethys", "scripts")))
os.environ["ABY_V2"] = "1"
import ideas as IDEAS  # noqa: E402

src = open(os.path.join(AB_DIR, "abyssal_build.py"), encoding="utf-8").read()
assert "AB.landmark_v2(ns)" in src
src = src.replace("AB.landmark_v2(ns)", "IDEAS.landmark(ns)").replace("r=52.0, s=0.19", "r=36.0, s=0.19").replace("calm_r=50.0", "calm_r=44.0").replace("m.AB = AB", "m.AB = AB\nm.IDEAS = IDEAS")
g = {"__name__": "__main__", "__file__": os.path.join(AB_DIR, "abyssal_build.py"), "IDEAS": IDEAS}
exec(compile(src, g["__file__"], "exec"), g)
