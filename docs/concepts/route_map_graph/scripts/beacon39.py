"""Round 39: the locked R3 class beacon (round 21/22 raid world), self-contained: cone from the pad, cap ring under the
emblem, class colour + emblem + the class idle. Emblems from ../scratch/emblems (emblems20.py)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
EMBLEMS = os.path.join(os.path.dirname(HERE), "scratch", "emblems")
C = lambda *v: np.array(v, np.float32)  # noqa: E731
CLASS_COL = {"breaker": C(1.0, 0.24, 0.66), "wrecker": C(1.0, 0.43, 0.2), "ghost": C(0.36, 0.88, 1.0), "phantom": C(0.86, 0.76, 1.0),
             "rigger": C(0.48, 0.88, 0.48), "overclocker": C(1.0, 0.69, 0.24), "botnet": C(0.38, 0.45, 1.0), "hivemind": C(0.78, 0.35, 1.0)}
CRGB = {k: tuple(int(v * 255) for v in c) for k, c in CLASS_COL.items()}
EMBLEM_OVERRIDE = {}


def to_pil(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


class _RF:
    EMBLEMS = EMBLEMS


RF = _RF()


def beacon(img, px, py, cls, t, scale=1.0):
    """Additive class beacon over img (float HxWx3) from the pad at (px, py). The light is a CONE that opens upward from
    the pad projector and ends at a cap ring UNDER the emblem: no light behind the icon. Each class has its own idle."""
    h, w = img.shape[:2]
    col = np.array(CRGB[cls], np.float32) / 255.0
    s = scale
    Hc, r0, r1 = 210 * s, 7 * s, 62 * s
    es = int(118 * s)
    bob = 0.0
    ex_off = 0.0
    em_alpha = 1.0
    em_rot = 0.0
    em_scale = 1.0
    flutter = 1.0
    if cls == "ghost":
        bob = 10 * s * math.sin(2 * math.pi * t)
        em_alpha = 0.55 + 0.45 * abs(math.sin(2 * math.pi * t * 2))
    elif cls == "wrecker":
        ph = t % 1.0
        bob = -26 * s * math.sin(math.pi * min(1.0, ph / 0.7)) if ph < 0.7 else 6 * s * math.sin((ph - 0.7) / 0.3 * math.pi)
    elif cls == "breaker":
        em_rot = 18 * math.sin(2 * math.pi * t) if t < 0.5 else -26 * math.sin(2 * math.pi * (t - 0.5) * 2) * (t < 0.75)
    elif cls == "overclocker":
        ex_off = 2.5 * s * math.sin(2 * math.pi * t * 7)
        flutter = 0.75 + 0.25 * math.sin(2 * math.pi * t * 4)
    elif cls == "hivemind":
        em_scale = 1.0 + 0.08 * math.sin(2 * math.pi * t * 2)
    top = py - Hc + bob * 0.3
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sp = np.clip((py - yy) / max(1.0, py - top), 0, 1)
    rad = r0 + (r1 - r0) * sp
    inside = (yy <= py) & (yy >= top)
    dxn = np.abs(xx - px) / np.maximum(rad, 1)
    body = np.clip(1 - dxn, 0, 1) ** 0.4 * (dxn < 1)
    edge = np.exp(-((dxn - 0.96) / 0.06) ** 2)
    bands = 0.82 + 0.18 * np.sin(2 * math.pi * (sp * 7 - t * (4 if cls == "overclocker" else 2)))
    fade = (0.35 + 0.65 * (1 - sp) ** 0.7)
    cone = (body * 0.28 + edge * 0.85) * bands * fade * inside * flutter
    if cls == "ghost":
        cone *= 0.75 + 0.25 * np.sin(yy * 0.08 + t * 12)
    # cap ring (ellipse) at the cone mouth + projector glow at the pad
    capr = np.hypot((xx - px) / r1, (yy - top) / (r1 * 0.32))
    cap = np.exp(-((capr - 1.0) / 0.08) ** 2)
    base = np.exp(-(np.hypot((xx - px) / (18 * s), (yy - py) / (7 * s))) ** 2)
    lay = (cone + cap * 0.9 + base * 1.2)[..., None] * col
    # emblem (holo with scanlines) sitting above the cap; the cone is cut by the emblem's dilated silhouette
    ec_x, ec_y = px + ex_off, top - es * 0.58 + bob
    sz = int(es * em_scale)
    g = (EMBLEM_OVERRIDE[cls] if cls in EMBLEM_OVERRIDE else Image.open(os.path.join(RF.EMBLEMS, cls + ".png")).split()[3]).resize((sz, sz), Image.LANCZOS)
    if em_rot:
        g = g.rotate(em_rot, Image.BICUBIC, center=(sz * 0.2, sz * 0.8))
    em = np.zeros((h, w), np.float32)
    x0, y0 = int(ec_x - sz / 2), int(ec_y - sz / 2)
    ga = np.asarray(g, np.float32) / 255.0
    if 0 <= x0 and x0 + sz <= w and 0 <= y0 and y0 + sz <= h:
        em[y0:y0 + sz, x0:x0 + sz] = ga
    halo = np.asarray(to_pil(np.repeat(em[..., None], 3, 2)).filter(ImageFilter.MaxFilter(9)).convert("L"), np.float32) / 255.0
    lay = lay * (1 - halo[..., None])                       # nothing of the beam shows behind the icon
    scan = 0.78 + 0.22 * ((yy.astype(np.int32) // max(1, int(2 * s))) % 2)
    emc = em * scan * em_alpha
    extra = np.zeros((h, w), np.float32)
    extra_col = col
    # ---- signature idles
    if cls == "breaker" and 0.5 <= t < 0.7:                 # spark burst at the strike
        rng = np.random.default_rng(int(t * 100))
        for _ in range(12):
            a = rng.uniform(0, 2 * math.pi)
            L = rng.uniform(20, 60) * s * (1 - (t - 0.5) * 3)
            sx, sy = ec_x + es * 0.32, ec_y - es * 0.3
            im = Image.new("L", (w, h), 0)
            ImageDraw.Draw(im).line([(sx, sy), (sx + L * math.cos(a), sy + L * math.sin(a))], fill=255, width=max(1, int(3 * s)))
            extra = np.maximum(extra, np.asarray(im, np.float32) / 255.0)
        extra_col = np.array([1.0, 0.95, 0.8], np.float32)
    if cls == "wrecker" and t >= 0.68:                      # shock ring on the roof
        k = (t - 0.68) / 0.32
        rr = np.hypot((xx - px) / (40 * s + 140 * s * k), (yy - py) / ((40 * s + 140 * s * k) * 0.45))
        extra = np.exp(-((rr - 1) / 0.05) ** 2) * (1 - k)
    if cls == "ghost":                                      # glitch slices through the emblem
        sl = ((yy.astype(np.int32) // max(1, int(6 * s)) + int(t * 20)) % 5 == 0)
        emc = emc * np.where(sl & (abs(math.sin(2 * math.pi * t * 2)) < 0.5), 0.0, 1.0)
    if cls == "phantom":                                    # afterimage double (cyan) splits and returns
        d = 22 * s * abs(math.sin(math.pi * t))
        sh = np.roll(np.roll(em, int(d), 1), int(-d * 0.3), 0)
        lay = lay + (sh * 0.7 * scan)[..., None] * np.array([0.36, 0.88, 1.0], np.float32)
    if cls == "rigger":                                     # rings climbing the cone
        for k in range(3):
            q = (t + k / 3) % 1.0
            yc = py - (py - top) * q
            rr_ = r0 + (r1 - r0) * q
            ell = np.hypot((xx - px) / rr_, (yy - yc) / (rr_ * 0.3))
            extra = np.maximum(extra, np.exp(-((ell - 1) / 0.07) ** 2) * (1 - q * 0.4))
    if cls == "overclocker":                                # embers
        rng = np.random.default_rng(5)
        for k in range(14):
            q = (t * 1.5 + rng.uniform(0, 1)) % 1.0
            exn = px + rng.uniform(-0.8, 0.8) * (r0 + (r1 - r0) * q) + 4 * s * math.sin(q * 9 + k)
            eyn = py - (py - top) * q
            extra = np.maximum(extra, np.exp(-(np.hypot(xx - exn, yy - eyn) / (2.6 * s)) ** 2) * (1 - q))
        extra_col = np.array([1.0, 0.55, 0.15], np.float32)
    if cls == "botnet":                                     # orbiting drone dots
        for k in range(6):
            a = 2 * math.pi * (t + k / 6)
            ox, oy = ec_x + 78 * s * math.cos(a), ec_y + 26 * s * math.sin(a)
            front = math.sin(a) > -0.2 or True
            extra = np.maximum(extra, np.exp(-(np.hypot(xx - ox, yy - oy) / (5 * s)) ** 2) * (1.0 if math.sin(a) > 0 else 0.55))
    if cls == "hivemind":                                   # hex cells rippling out
        for k in range(2):
            q = (t + k * 0.5) % 1.0
            R = (60 + 120 * q) * s
            hexr = Image.new("L", (w, h), 0)
            dd = ImageDraw.Draw(hexr)
            for j in range(6):
                a = math.pi / 6 + j * math.pi / 3
                cx, cy = ec_x + R * math.cos(a), ec_y + R * 0.55 * math.sin(a)
                dd.regular_polygon((cx, cy, 13 * s), 6, outline=255, width=max(1, int(2 * s)))
            extra = np.maximum(extra, np.asarray(hexr, np.float32) / 255.0 * (1 - q))
    lay = lay + (emc * 0.7)[..., None] * col + (extra * 1.1)[..., None] * extra_col
    blur = np.asarray(to_pil(np.clip(lay, 0, 1)).filter(ImageFilter.GaussianBlur(7 * s)), np.float32) / 255.0
    out = img + lay + blur * 0.8
    # the emblem stays readable: a soft dark plate just behind it (it is a projection in front of the city)
    plate = np.asarray(to_pil(np.repeat(em[..., None], 3, 2)).filter(ImageFilter.GaussianBlur(5 * s)).convert("L"), np.float32) / 255.0
    out = out * (1 - 0.45 * plate[..., None]) + (emc * 1.0)[..., None] * (0.22 + 0.8 * col)
    return np.clip(out, 0, 1)


