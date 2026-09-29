"""Still 02: the City Grid at night. Renders beauty, fog json and depth (for tilt-shift in tiltshift.py)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rn_lib import *  # noqa
from rn_parts import *  # noqa
from city_scene import City, HQ, NET_Z

BASE = out_arg(os.path.join(STILLS, "_raw_02"))
reset(samples=int(os.environ.get("RN_SAMPLES", "32")))
city = City(heat=0.0, seed=4)
city.camera()
city.compute_focus()
city.gp_fx = GP("gp_fx")
city.gp_net = GP("gp_net")
city.build()
city.net()
city.rain()
city.ui_gp()

# glass UI: district header, node tags, legend (sharp: excluded from tilt-shift)
city.ui_panel(24, 24, 430, 92, title="GRID // DISTRICT 04 · NIGHT")
city.ui_text("MERIDIAN FREIGHT   TURF 3/7   HEAT 18 COOL", 38, 88, 16, "text_hi", 1.8)
city.label_at((HQ[0], HQ[1], NET_Z), "HQ · CYBERDECK", "acid")
city.label_at((city.nodes["e"][0], city.nodes["e"][1], NET_Z), "DEPOT 7 · THREAT", "#FF8C1A")
city.label_at((city.nodes["c"][0], city.nodes["c"][1], NET_Z), "SERVER RACK", "cyan")
city.ui_panel(1560, 900, 336, 150, title="LEGEND")
city.ui_text("== CELL LINK (CLAIMED)", 1576, 960, 15, "acid", 2.0)
city.ui_text(">> CORP THREAT ROUTE", 1576, 990, 15, "#FF8C1A", 2.0)
city.ui_text("== NET LINK", 1576, 1020, 15, "cyan", 2.0)

compositor(bloom=0.9, bloom_thresh=1.2, streak=0.25, streak_thresh=4.0, distortion=-0.01)
render(BASE + "_beauty.png")
city.export_fog(BASE + "_fog.json")
city.depth_pass(BASE + "_depth.png")
