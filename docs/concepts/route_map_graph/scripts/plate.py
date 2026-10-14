"""Route map graph: finish the city plate once (post40, locked translucency v3) with only the Cell's own owned links dim,
and cache it with its camera. The run graph itself is drawn in 2D over it by each direction's script.
SOLID40=1 NET36=net_scope.json python plate.py -> ../scratch/plate_city.png + ../scratch/plate_cam.json"""
import json
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
os.environ.setdefault("RUN_V3", "1")
os.environ.setdefault("SOLID40", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import kit44 as KT  # noqa: E402
import post40 as P  # noqa: E402

SCR = os.path.join(os.path.dirname(HERE), "scratch")


def deco(net):
    for l in P.NET["links"]:
        if l["state"] == "owned":
            net.link(l["pts"], P.LINK_COL["owned"], k=0.3, packets=False)


if __name__ == "__main__":
    img, cam = P.finish("t_run38", decorate=deco, pools=[], t=0.2, sky=False)
    KT.f2p(img).convert("RGB").save(os.path.join(SCR, "plate_city.png"))
    json.dump(cam, open(os.path.join(SCR, "plate_cam.json"), "w"))
    print("plate ok")
