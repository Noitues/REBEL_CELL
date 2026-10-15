"""AAA-2 r2: render and label the building-shapes sheet -> ../buildings_sheet.png (2560 x 1100).

python sheet_r2.py [render|finish|all]
The sheet is built by shapes_sheet_r2.py inside the normal AAA-2 scene (same kit, same materials, same GPU setup), in a
row far off to the side of the street, so it shows exactly the geometry the key art uses.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import jobs_aaa as J  # noqa: E402
import post_aaa as P  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
X0, STEP, N = 3000.0, 46.0, 9
CX = X0 + STEP * 4
POSE = dict(loc=[CX, -470.0, 92.0], tgt=[CX, 0.0, 24.0], lens=40.0, shift_x=0.0, shift_y=0.06)
RES = [2560, 1100]
LABELS = [("ROUND TOWER", "drum + setbacks"), ("CUT DRUM (ROUTE)", "rooms in the cut"), ("ZIGGURAT", "5 stepped tiers"),
          ("CURVED FACADE", "convex face"), ("CRESCENT", "concave face"), ("TERRACED RUN", "shared walls"),
          ("PODIUM PAIR (ROUTE)", "route cols 1 + 2"), ("FAT BLOCK", "rounded corners"), ("DRUM MEGA", "far skyline, 1:6")]
EXPOSURE = 0.38


def render():
    job, tag = J.make("real", "test")
    job.update(shapes_sheet=True, renders=["main"], res=RES, samples=96, threshold=0.02,
               shots=[dict(name="O_sheet", pose=POSE, t=2.0, protect=[])], out=os.path.join(J.SCR, "bl_sheet"))
    return J.run(job, "sheet")


def project(p, W, H):
    loc, tgt = np.array(POSE["loc"]), np.array(POSE["tgt"])
    f = tgt - loc
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = np.array(p) - loc
    x, y, z = d @ r, d @ u, d @ f
    fpx = POSE["lens"] / 36.0 * W
    return W / 2 + fpx * (x / z) - W * POSE["shift_x"], H / 2 - fpx * (y / z) + W * POSE["shift_y"]


def finish():
    bl = os.path.join(J.SCR, "bl_sheet")
    c = np.load(os.path.join(bl, "O_sheet_combined.npy")).astype(np.float32)
    H, W = c.shape[:2]
    z = np.load(os.path.join(bl, "O_sheet_z.npy"))[..., 0]
    sky = z > 3000                       # no ground behind the row: a dark studio backdrop instead of the city world
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    back = np.array((0.010, 0.008, 0.018), np.float32) * (1.0 + 0.8 * yy)
    c = np.where(sky[..., None], back, c)
    img = P.tonemap(c * EXPOSURE)
    img = P.to_srgb(img)
    img = np.clip(0.18 * np.power(np.maximum(img, 0) / 0.18, 1.08), 0, 1)
    im = Image.fromarray((img * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for k, (t, sub) in enumerate(LABELS):
        x, y = project((X0 + STEP * k, -14.0, -1.0), W, H)
        d.text((x, y + 30), "%d  %s" % (k + 1, t), font=K.F(K.ANTON, 26), fill=(255, 226, 0), anchor="mm")
        d.text((x, y + 62), sub, font=K.F(K.MONO, 20), fill=(205, 210, 230), anchor="mm")
    d.text((40, 34), "AAA-2 r2  //  NEW BUILDING SHAPES  (designer note 5)", font=K.F(K.ANTON, 40), fill=(242, 246, 255))
    d.text((40, 86), "Same kit, materials and GPU path tracing as the key art. Route buildings: 2 (column 5) and 7 (columns 1 + 2; "
                     "column 0 also gets a fat stepped annex). Mid row / far city: 1, 3, 4, 5, 6, 8, 9.", font=K.F(K.MONO, 22), fill=(170, 176, 196))
    out = os.path.join(ROOT, "buildings_sheet.png")
    im.convert("RGB").save(out)
    print("saved", out)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render()
    if what in ("finish", "all"):
        finish()
