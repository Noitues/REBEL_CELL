"""Round 44: print where nodes and HQs land for a candidate camera.  python plan_cam.py tx ty ortho"""
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout36 as L  # noqa: E402

tx, ty, o = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
net = L.load_net()
cam = L.cam((tx, ty), o)
for n in net["nodes"]:
    x, y = L.project(cam, *L.W(n["lot"]))
    on = 0 <= x <= 1920 and 0 <= y <= 1080
    print("%-20s %-9s (%5d,%5d) %s" % (n["id"], n["state"], x, y, "" if on else "OFF"))
for k, v in net["hq"].items():
    x, y = L.project(cam, *L.W(v))
    print("HQ %-10s (%5d,%5d)" % (k, x, y))
