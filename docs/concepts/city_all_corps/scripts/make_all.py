"""City-all-corps: from the raw passes on D: to the deliverables in docs/concepts/city_all_corps/.

python make_all.py            (after run_jobs.py aaa hero,close 1.0 <spp> final  and  run_jobs.py main hero 1.0 16 final_main)
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402
import post_city as PC  # noqa: E402

F = os.path.join(CP.SCR, "final")
FM = os.path.join(CP.SCR, "final_main")
OUT = CP.OUT
st = {}
_, st["hero"] = PC.aaa(os.path.join(F, "hero_aaa"), os.path.join(OUT, "city_all_corps_night.png"))
PC.labels(os.path.join(OUT, "city_all_corps_night.png"), os.path.join(F, "hero_aaa_anchors.json"),
          os.path.join(OUT, "city_all_corps_labeled.png"))
_, st["mainline"] = PC.main_post(os.path.join(FM, "hero_main"), os.path.join(OUT, "city_all_corps_mainline.png"))
_, st["close"] = PC.aaa(os.path.join(F, "close_aaa"), os.path.join(OUT, "tethys_flooded_closeup.png"))
shutil.copy(os.path.join(CP.SCR, "zoning_map.png"), os.path.join(OUT, "zoning_map.png"))
json.dump(st, open(os.path.join(F, "value_checks.json"), "w"), indent=1)
print(json.dumps(st, indent=1))
