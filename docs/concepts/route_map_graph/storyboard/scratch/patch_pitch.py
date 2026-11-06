import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "sb_onecity.py"
s = open(p, encoding="utf-8").read()
s = s.replace("""             min_width=2.5, max_setback=0.6, extend=(12.0, 60.0))""",
"""             min_width=2.5, max_setback=0.6, extend=(12.0, 60.0),
             # OVERVIEW pose (designer note v3-r2: the frontage faces the camera, the street a thin wet strip in front):
             # a near-level axis (ov_pitch) and the frame shifted so the frontage base sits at ov_base_frac of the height;
             # the steepest ground ray in frame is then ~10 deg (was ~20), the camera ~10 BU over the street (was 17.7)
             ov_pitch=2.0, ov_base_frac=0.815)""", 1)
old = """        ov = frame(pts, y0 - sgn * 7.2, 6.0, 40.0, 0.95, 0.90)
"""
new = """        ov = frame(pts, y0 - sgn * 7.2, RULES["ov_pitch"], 40.0, 0.95, 0.90)
        fb = [p for r in rooms.values() for p in r["front"] if p[2] < 0.5]
        by = max(proj(ov, p)[1] for p in fb) if fb else None
        if by is not None:
            ps = dict(ov["persp"])
            ov = cam(ov["target"], ov["yaw"], ov["pitch"], ov["dist"], ps["lens"], ps["sx"],
                     ps["sy"] + (RULES["ov_base_frac"] * H_ - by) / W_)
"""
assert old in s
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("ok")
