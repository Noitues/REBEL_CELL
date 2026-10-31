"""Cohesion redo 1: shared kit for the four map pages on the r42 city.

The old pages were a Blender plate (old violet city, links and node decals rendered into it) with PIL chrome on top.
The chrome is draw code (kit44 / ui31 / hq44 / route44 / raid44, copied unchanged beside this file). What cannot be
reused is the plate: so this module supplies
  - the r42 backdrop (plan_r42.png), optionally cropped and zoomed,
  - an affine lot -> pixel map (Aff) standing in for the Blender camera, tuned so nodes sit on plausible streets,
  - the under-UI dim grade (value band outside / inside the focus rectangle, saturation pulled more on neon),
  - PIL redraws of the link lines and raid node frames that used to be Blender decals.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
CONC = os.path.dirname(os.path.dirname(OUT))                     # docs/concepts
R42 = os.path.join(CONC, "tide_raid", "G1_parity", "r42")
W, H = 1920, 1080

# the three grade strengths: (value outside, value inside, sat pull on buildings, sat pull on neon/avenues)
GRADES = {
    "light": (0.76, 0.92, 0.04, 0.22),
    "mid": (0.68, 0.86, 0.10, 0.38),
    "strong": (0.58, 0.78, 0.18, 0.55),
}


def backdrop(name="plan_r42.png", crop=None):
    im = Image.open(os.path.join(R42, name)).convert("RGB")
    if crop:
        im = im.crop(crop).resize((W, H), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=60, threshold=2))
    return im


class Aff:
    """lot -> pixel. px = O + ex * x + ey * y (an iso diamond). Stands in for the Blender camera the old scripts used."""

    def __init__(self, ox, oy, ex, ey, special=None):
        self.o = np.array([ox, oy], np.float64)
        self.ex = np.array(ex, np.float64)
        self.ey = np.array(ey, np.float64)
        self.special = special or {}
        self.over = {}

    def prj(self, lot):
        key = (round(float(lot[0]), 3), round(float(lot[1]), 3))
        if key in self.special:
            return self.special[key]
        if key in self.over:
            return self.over[key]
        p = self.o + self.ex * lot[0] + self.ey * lot[1]
        return float(p[0]), float(p[1])


def soft_rect(box, blur=80):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0


def soft_ellipse(cx, cy, rx, ry, blur=60):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0


def neon_mask(a):
    """Avenue strips, signage and window glow: bright AND saturated pixels, thin enough to survive a small blur."""
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    m = np.clip((sat - 0.45) / 0.25, 0, 1) * np.clip((mx - 0.55) / 0.25, 0, 1)
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
    return np.asarray(im, np.float32) / 255.0


def grade(img, net_mask, lit_mask=None, strength="mid", lit_k=0.7):
    """Under-UI dim grade. Value x v_out outside the focus rect, x v_in inside it (soft edge); the lit vignette round the
    selected Site lifts back towards 1.0 by lit_k. Saturation is pulled by s_b on buildings and by s_n on neon, so the
    corp hues (lime park, violet towers, cyan/green avenues) stay recognisable but the avenue strips stop competing."""
    v_out, v_in, s_b, s_n = GRADES[strength]
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    nm = neon_mask(a)
    f = v_out + (v_in - v_out) * net_mask
    if lit_mask is not None:
        f = f + (1.0 - f) * lit_mask * lit_k
    lum = (a * np.array([0.30, 0.59, 0.11], np.float32)).sum(axis=2, keepdims=True)
    pull = (s_b + (s_n - s_b) * nm)[..., None]
    a = a * (1 - pull) + lum * pull
    # neon also loses a little extra value so the strips sit under the chrome
    f = f * (1 - 0.12 * nm * (1 - (lit_mask if lit_mask is not None else 0)))
    a = a * f[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------ links (were Blender decals)
def _glow_line(size, pts, col, width, glow_k, glow_r, dash=None, ss=2):
    w, h = size
    lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    P = [(x * ss, y * ss) for x, y in pts]
    if dash is None:
        d.line(P, fill=col + (255,), width=int(width * ss), joint="curve")
    else:
        on, off = dash
        run, drawing = 0.0, True
        for (ax, ay), (bx, by) in zip(P, P[1:]):
            seg = math.hypot(bx - ax, by - ay)
            t = 0.0
            while t < seg:
                step = min((on if drawing else off) * ss - run, seg - t)
                if drawing:
                    d.line([(ax + (bx - ax) * t / seg, ay + (by - ay) * t / seg),
                            (ax + (bx - ax) * (t + step) / seg, ay + (by - ay) * (t + step) / seg)], fill=col + (255,), width=int(width * ss))
                t += step
                run += step
                if run >= (on if drawing else off) * ss - 1e-6:
                    run, drawing = 0.0, not drawing
    core = lay.resize((w, h), Image.LANCZOS)
    glow = core.filter(ImageFilter.GaussianBlur(glow_r))
    ga = np.asarray(glow, np.float32)
    ga[..., 3] = np.clip(ga[..., 3] * glow_k * 2.2, 0, 255)
    return Image.fromarray(ga.astype(np.uint8)), core


def link(img, cam, lot_pts, col, width=4.0, k=1.0, dash=None, glow_r=7, under_dark=True):
    """One link as a lit line: a dark under-stroke (so it reads on busy roofs), a glow, the coloured core."""
    pts = [cam.prj(p) for p in lot_pts]
    glow, core = _glow_line(img.size, pts, col, width, 0.55 * k, glow_r, dash)
    if under_dark:
        dk, dcore = _glow_line(img.size, pts, (2, 2, 8), width + 5, 0.0, 1, dash)
        a = np.asarray(dcore, np.float32)
        a[..., 3] *= 0.55 * min(1.0, k + 0.2)
        img.alpha_composite(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(glow)
    ca = np.asarray(core, np.float32)
    ca[..., 3] *= min(1.0, 0.45 + 0.55 * k)
    img.alpha_composite(Image.fromarray(ca.astype(np.uint8)))
    return img


def diamond(img, cam, lot, half, col, width=4, k=1.0, fill=0.0, dash=None):
    """An iso footprint frame round a node (the raid page's holds / disabled frame)."""
    x, y = lot
    corners = [(x - half, y - half), (x + half, y - half), (x + half, y + half), (x - half, y + half), (x - half, y - half)]
    if fill:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([cam.prj(c) for c in corners[:4]], fill=col + (int(255 * fill),))
        img.alpha_composite(lay)
    return link(img, cam, corners, col, width=width, k=k, dash=dash, glow_r=5, under_dark=True)


def corridor_dim(img, cam, polys, radius=150, k=0.32, blur=60):
    """Extra dim everywhere except a soft corridor round the given lot polylines (the routes lead the eye)."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        pts = [cam.prj(q) for q in p]
        d.line(pts, fill=255, width=int(radius * 2), joint="curve")
        for x, y in pts:
            d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0
    a = np.asarray(img.convert("RGB"), np.float32)
    a = a * (1 - k * (1 - m))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
