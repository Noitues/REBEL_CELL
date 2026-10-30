"""Cohesion redo 1: route_page.png on the r42 city (2x crop of the downtown). Chrome = route44.py unchanged."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ["NET36"] = "net_scope.json"; os.environ["RUN_V3"] = "1"; os.environ["SOLID40"] = "1"
sys.dont_write_bytecode = True
import r42lib as R
import kit44 as KT
import route44 as RT
import post40 as P

CAM = R.Aff(-17, -486, (76.5, 37.4), (-76.5, 37.4))
CROP = (330, 330, 1290, 870)
GRADE = "mid"
col = lambda a: tuple(int(round(float(v) * 255)) for v in a)
RT.prj = lambda cam, lot: cam.prj(lot)


def plate():
    run = RT.RM.load()
    st = RT.RM.states(run, RT.WALKED, RT.CUR, False)
    E = {(e["a"], e["b"]): RT.T.edge_state(e, st, RT.WALKED) for e in run["edges"]}
    base = R.backdrop(crop=CROP).convert("RGBA")
    pts = [CAM.prj(n["lot"]) for n in run["nodes"] if st[n["id"]] != "hidden"]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    nm = R.soft_rect((min(xs) - 120, min(ys) - 160, max(xs) + 120, max(ys) + 100), blur=90)
    cx, cy = CAM.prj([24.3, 6.1])
    lit = R.soft_ellipse(cx, cy, 330, 230, blur=90)
    img = R.grade(base, nm, None, GRADE)
    vis = [e["pts"] for e in run["edges"] if E[(e["a"], e["b"])] in ("walked", "option")]
    img = R.corridor_dim(img, CAM, vis, radius=170, k=0.38)
    for e in run["edges"]:
        s = E[(e["a"], e["b"])]
        if s == "walked":
            R.link(img, CAM, e["pts"], col(P.LIME), width=9, k=1.3)
        elif s == "option":
            R.link(img, CAM, e["pts"], col(P.ORANGE), width=6.5, k=1.2, dash=(20, 12))
    return img, CAM, run, st, E


RT.plate = plate
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--grade": GRADE = sys.argv[2]
    RT.build(False).convert("RGB").save(os.path.join(R.OUT, "route_page.png"), optimize=True); print("saved route_page")
