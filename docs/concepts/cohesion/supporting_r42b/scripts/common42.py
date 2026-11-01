"""Supporting screens on the r42 city: shared backdrop + grade + renamed save.

The old backdrops were pre-rendered violet-city / facade plates under PIL chrome. Here they are replaced by
  city    tide_raid/G1_parity/r42/plan_r42.png (the approved r42 city), or
  cutaway combat_backdrop/v2/room_bio_bare.png (the picked iso cutaway: Solace lab over a wet street),
graded with the map-pages STRONG under-UI grade (r42lib.grade: value x0.58 outside / x0.78 inside the focus rect,
saturation pull 0.18 on buildings and 0.55 on neon), then a light blur so the chrome leads.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CONC = os.path.dirname(os.path.dirname(OUT))
import r42lib as R42  # noqa: E402

W, H = 1920, 1080
CUTAWAY = os.path.join(CONC, "combat_backdrop", "v2", "room_bio_bare.png")


def bg(kind="city", focus=None, strength="strong", blur=2.0, shift=(0, 0), crop=None, lit=None, extra=1.0):
    """focus: list of (x0,y0,x1,y1) rects where the grade is the lighter 'inside' value (the UI footprint)."""
    if kind == "city":
        im = R42.backdrop("plan_r42.png", crop=crop)
    else:
        im = Image.open(CUTAWAY).convert("RGB")
        if crop:
            im = im.crop(crop).resize((W, H), Image.LANCZOS)
    if shift != (0, 0):
        im = im.transform(im.size, Image.AFFINE, (1, 0, -shift[0], 0, 1, -shift[1]), Image.BICUBIC)
    m = np.zeros((H, W), np.float32)
    for b in focus or []:
        m = np.maximum(m, R42.soft_rect(b, 70))
    lm = None
    if lit:
        lm = np.zeros((H, W), np.float32)
        for (cx, cy, rx, ry) in lit:
            lm = np.maximum(lm, R42.soft_ellipse(cx, cy, rx, ry, 70))
    out = R42.grade(im, m, lm, strength)
    if extra != 1.0:
        a = np.asarray(out.convert("RGB"), np.float32) * extra
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    if blur:
        out = out.filter(ImageFilter.GaussianBlur(blur))
    return out.convert("RGBA")


def patch_save(L, names):
    """Redirect L.save so each old plate name is written under its new name."""
    orig = L.save

    def save(img, name, q=None):
        return orig(img, names.get(name, name), q)
    L.save = save
