"""Cohesion redo 1: raid_setup.png on the r42 city. Chrome = raid44.py unchanged; node frames, forecast rings and the
network links (Blender decals in the old plate) are redrawn here in PIL. The raid-mode grade is the page grade + 0.9."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ["NET36"] = "net_scope.json"; os.environ["SOLID40"] = "1"
sys.dont_write_bytecode = True
import numpy as np
import r42lib as R
import raid44 as RD
import post40 as P

CAM = R.Aff(690, 318, (17.1, 8.36), (-17.1, 8.36))
GRADE = "mid"
col = lambda a: tuple(int(round(float(v) * 255)) for v in a)
RD.prj = lambda cam, lot: cam.prj(lot)


def plate(routes):
    entries = {r["start"] for r in routes}
    base = R.backdrop().convert("RGBA")
    mine = [n for n in RD.NET["nodes"] if n["state"] in ("owned", "core") or n["id"] in entries]
    pts = [CAM.prj(n["lot"]) for n in mine]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    nm = R.soft_rect((min(xs) - 120, min(ys) - 140, max(xs) + 120, max(ys) + 100), blur=90)
    img = R.grade(base, nm, None, GRADE)
    a = np.asarray(img.convert("RGB"), np.float32) * 0.9            # raid mode steps the city back one more notch
    from PIL import Image
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert("RGBA")
    for l in RD.NET["links"]:
        if l["state"] != "owned":
            continue
        dead = RD.STATE.get(l["a"], ("", 1))[0] == "disabled" or RD.STATE.get(l["b"], ("", 1))[0] == "disabled"
        R.link(img, CAM, l["pts"], col(P.LINK_COL["owned"]), width=3.5 if dead else 4.5, k=0.45 if dead else 1.1)
    GREEN, GREY, PINK, AMB = col(P.GREEN), (140, 140, 150), col(P.PINK), (255, 176, 0)
    for n in RD.NET["nodes"]:
        if n["state"] in ("owned", "core"):
            st, hp = RD.STATE.get(n["id"], ("holds", 1.0))
            c = PINK if n["state"] == "core" else (GREY if st == "disabled" else GREEN)
            R.diamond(img, CAM, n["lot"], 1.6, c, width=4, k=0.5 if st == "disabled" else 1.0, fill=0.25 * (hp if st != "disabled" else 0.0))
        elif n["id"] in entries:
            R.diamond(img, CAM, n["lot"], 1.1, col(P.ORANGE), width=3, k=0.8)
    for nid, c in RD.FORECAST.items():
        R.diamond(img, CAM, RD.NODES[nid]["lot"], 2.6, col(c), width=3, k=1.0, dash=(10, 8))
    return img, CAM


RD.plate = plate
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--grade": GRADE = sys.argv[2]
    RD.build().convert("RGB").save(os.path.join(R.OUT, "raid_setup.png"), optimize=True); print("saved raid_setup")
