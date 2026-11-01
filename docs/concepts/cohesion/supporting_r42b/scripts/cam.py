"""Security-cam treatment for the Terminal event card's CAM feed (O-9).

cam_feed(option) -> RGBA 560x380 (the card's feed slot).
Pipeline: crop a real frame -> low-res (280x190) -> barrel fisheye -> cel posterize -> Solace duotone tint
-> 2x nearest up -> scanlines, chroma split, grain, roll bar, vignette -> REC / CAM label / timestamp / frame border.
Nothing is painted; every pixel comes from the two source frames.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CONC = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STREET = os.path.join(CONC, "netrun_cel", "zoom_rules", "round6", "street_frame.png")
ROOM = os.path.join(CONC, "combat_backdrop", "v3_1", "room_event_bare.png")

W, H = 560, 380
LW, LH = 280, 190
SOLACE = np.array([61, 255, 139], np.float32)
DARK = np.array([2, 14, 10], np.float32)

# crop boxes are 1920x1080-frame pixels, aspect ~ 560:380
OPTIONS = {
    "A": dict(name="CORNER CAM, HIGH", src=ROOM, crop=(1100, 340, 1860, 856), label="CAM 04  MAINT. WARD", k=0.16,
              tint=0.80, gain=1.3, stamp="03:41:07", circle=(300, 205, 78, 58), ward=(420, 98)),
    "B": dict(name="DOOR CAM, STREET LEVEL", src=ROOM, crop=(1170, 736, 1640, 1055), label="CAM 04  MAINT. WARD", k=0.22,
              tint=0.80, stamp="03:41:07", circle=(268, 215, 96, 66), ward=(430, 108)),
    "C": dict(name="NETRUN STREET, STOREFRONTS", src=STREET, crop=(1330, 504, 1920, 906), label="CAM 04  MAINT. WARD", k=0.24,
              tint=0.74, gain=1.45, stamp="03:41:07", circle=(466, 262, 70, 56), ward=(400, 120)),
}


def fisheye(a, k):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx - w / 2) / (w / 2)
    ny = (yy - h / 2) / (h / 2)
    r2 = nx * nx + ny * ny
    f = 1 + k * r2          # sample further out toward edges -> barrel look (centre magnified less than rim squashed)
    sx = np.clip(nx * f * 0.92 * (w / 2) + w / 2, 0, w - 1.001)
    sy = np.clip(ny * f * 0.92 * (h / 2) + h / 2, 0, h - 1.001)
    x0 = sx.astype(int); y0 = sy.astype(int); fx = (sx - x0)[..., None]; fy = (sy - y0)[..., None]
    o = (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy) +
         a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)
    return o


def cam_feed(key, seed=7):
    o = OPTIONS[key]
    rng = np.random.RandomState(seed)
    src = Image.open(o["src"]).convert("RGB").crop(o["crop"]).resize((LW, LH), Image.LANCZOS)
    a = fisheye(np.asarray(src, np.float32), o["k"])
    # cel: posterize luminance to 6 steps, keep a little of the source hue
    lum = (a * np.array([0.30, 0.59, 0.11], np.float32)).sum(-1) / 255.0
    lum = np.clip((lum - 0.04) * 1.55, 0, 1) ** 0.85
    q = np.round(lum * 6) / 6
    ramp = DARK + (SOLACE - DARK) * q[..., None] ** 1.1
    hue = np.round(a / 255.0 * 4) / 4 * 255.0          # coarse original colour (neon pinks / cyans survive faintly)
    t = o["tint"]
    ramp = ramp * o.get("gain", 1.0)
    out = ramp * t + (hue * (q[..., None] ** 0.8) * 0.7) * (1 - t) * 1.0
    # highlights hot-white-green
    out = out + (q[..., None] > 0.9) * np.array([40, 30, 40], np.float32)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((W, H), Image.NEAREST)
    a = np.asarray(img, np.float32)
    # chroma split (1 px) and scanlines
    a[:, 1:, 0] = a[:, :-1, 0] * 0.9 + a[:, 1:, 0] * 0.1
    a[:, :-1, 2] = a[:, 1:, 2]
    sl = np.ones(H, np.float32)
    sl[0::3] = 0.62
    sl[1::3] = 0.92
    a *= sl[:, None, None]
    # rolling bar and a tear
    y = 238
    a[y:y + 26] *= np.linspace(1.0, 1.28, 26)[:, None, None]
    a[y + 26:y + 40] *= np.linspace(1.28, 1.0, 14)[:, None, None]
    ty = 322
    a[ty:ty + 3, :, :] = np.roll(a[ty:ty + 3, :, :], 9, axis=1)
    # grain + vignette
    a += rng.normal(0, 6.5, (H, W, 1)) * np.array([0.6, 1.0, 0.7], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.1
    a *= np.clip(v, 0.25, 1)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return im


def overlay(im, key, f_mono):
    """HUD: REC dot + label (top left), timestamp (bottom left), channel (bottom right), border."""
    o = OPTIONS[key]
    d = ImageDraw.Draw(im)
    d.rectangle([12, 12, 12 + 8 + 12 + int(f_mono.getlength(o["label"])) + 22, 40], fill=(4, 12, 9, 215))
    d.ellipse([20, 20, 32, 32], fill=(255, 50, 60, 255))
    d.text((40, 26), o["label"], font=f_mono, fill=(215, 255, 228, 255), anchor="lm")
    d.rectangle([12, H - 38, 204, H - 12], fill=(4, 12, 9, 215))
    d.text((20, H - 25), "11.01  " + o["stamp"], font=f_mono, fill=(215, 255, 228, 255), anchor="lm")
    d.text((W - 16, H - 25), "SOL-NET  CH4", font=f_mono, fill=(120, 230, 165, 235), anchor="rm")
    # corner ticks
    for (x, y, sx, sy) in ((6, 6, 1, 1), (W - 7, 6, -1, 1), (6, H - 7, 1, -1), (W - 7, H - 7, -1, -1)):
        d.line([(x, y), (x + 14 * sx, y)], fill=(61, 255, 139, 200), width=2)
        d.line([(x, y), (x, y + 14 * sy)], fill=(61, 255, 139, 200), width=2)
    d.rectangle([0, 0, W - 1, H - 1], outline=(20, 18, 26, 255), width=6)
    return im


def feed_panel_for(key, f_mono):
    return overlay(cam_feed(key), key, f_mono)
