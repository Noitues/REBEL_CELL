"""HQ kit post (from HQ Halcyon): the r3 "real" finish (post_aaa.py) on one Cycles render with the media in it, plus the LOD bands.

finish(stem, zoom, t, flash) -> PIL image (no UI). Order, all linear until the tone map:
  1. the denoised Combined (surfaces + in-scatter, one render: the orbit camera rules out r3's split passes);
  2. LOD: puddles_sharp_at -> the wet ground's reflections blur when zoomed out (index pass 4 = ground);
  3. exposure, HDR bloom (3 radii) + a soft halo from the Volume Direct pass (the beams glow), the max-RGB tone map;
  4. rain in 3 layers, lit by the glow and the beams; small_lights_on_at scales the rain highlights;
  5. the r3 grade (teal-navy shadows, warm highs), vignette, display knee, edge chromatic aberration, grain;
  6. the reveal's lens flash when the eye's beam passes the camera (flash 0..1).
Numbers: look_preset "post" + post_aaa LOOKS["real"] (copied below), seeded noise.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402

P = dict(exposure=2.65, bloom=(0.12, 0.10, 0.08), bloom_thr=1.2, grain=0.03, ca=2.4, vignette=0.38, tint_k=0.30,
         shadow_tint=(0.25, 0.45, 0.6), hi_tint=(1.0, 0.86, 0.86), sat=1.0, contrast=1.12, vol_k=1.3, vol_glow=0.8,
         vol_glow_thr=0.02, rain_vol=1.6, lift=(0.0, 0.0, 0.004))
P.update(HP.PRESET["post"])
P.update(HP.PRESET["hq"].get("post", {}))
LOD = HP.PRESET["lod_bands"]
RAIN_LAYERS = [(4000, (3, 6), 0.05, 1, 0.6), (1800, (14, 24), 0.10, 1, 1.0), (60, (60, 95), 0.25, 3, 1.6)]
KNEE = 0.66


from hq_kit.lod import sstep  # noqa: E402,F401  (the shared LOD bands)


def load(stem, k):
    p = stem + "_" + k + ".npy"
    return np.load(p).astype(np.float32) if os.path.exists(p) else None


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def resize_f(a, size, resample=Image.BILINEAR):
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize(size, resample), np.float32)
    return np.stack([resize_f(a[..., c], size, resample) for c in range(a.shape[2])], axis=-1)


def _box(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def gblur(a, sigma, down=1):
    """Gaussian blur (three box passes, r3 post_aaa), optionally at reduced resolution."""
    if sigma <= 0.3:
        return a
    h, w = a.shape[:2]
    small = resize_f(a, (max(1, w // down), max(1, h // down))) if down > 1 else a
    sg = sigma / down
    r = max(1, int(round((math.sqrt(12 * sg * sg / 3 + 1) - 1) / 2)))
    for _ in range(3):
        small = _box(_box(small, r, 0), r, 1)
    return resize_f(small, (w, h)) if down > 1 else small


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def tonemap(x):
    m = np.maximum(x.max(axis=-1, keepdims=True), 1e-6)
    hp = x * (aces(m) / m)
    w = 0.2 * np.clip((m - 3.0) / 2.0, 0, 1)
    return np.clip(hp * (1 - w) + aces(x) * w, 0, 1)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def finish(stem, zoom=0.0, t=2.0, flash=0.0, seed=7, flash_xy=None):
    comb = load(stem, "combined")
    emit = load(stem, "emit")
    vol = load(stem, "voldir")
    idx = load(stem, "index")
    H, W = comb.shape[:2]
    sc = W / 2560.0
    vol = np.zeros_like(comb) if vol is None else gblur(np.maximum(vol, 0), 2.0 * sc)
    emit = np.zeros_like(comb) if emit is None else emit
    img = comb.copy()
    # LOD: puddle reflections sharpen with zoom (blur the ground when zoomed out)
    if idx is not None:
        ground = (np.abs(idx[..., 0] - 4) < 0.5).astype(np.float32)
        k = 1.0 - sstep(zoom, *LOD["puddles_sharp_at"])
        if k > 0.01:
            gm = gblur(ground, 1.0 * sc)[..., None] * k * 0.85
            img = img * (1 - gm) + gblur(img, 3.0 * sc, 2) * gm
    # exposure by zoom: a close DECISION frame is filled with lit facade, so it is exposed down (deterministic, not
    # metered): exposure x (1 - exposure_zoom_k x zoom)
    expo = P["exposure"] * (1.0 - P.get("exposure_zoom_k", 0.0) * zoom)
    img = img * expo
    hot = np.maximum(img - P["bloom_thr"], 0) + emit * expo * 0.04
    hot = hot + np.maximum(vol - P["vol_glow_thr"], 0) * (P["vol_k"] * expo * P["vol_glow"] * 0.5)
    b1 = gblur(hot, 6 * sc, 2)
    b2 = gblur(hot, 24 * sc, 4)
    b3 = gblur(hot, 135 * sc, 8)
    img = img + b1 * P["bloom"][0] + b2 * P["bloom"][1] + b3 * P["bloom"][2]
    if flash > 0:
        # the eye's beam passes the lens: a veil + an anamorphic streak through the source
        fx, fy = flash_xy or (W / 2, H * 0.3)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        streak = np.exp(-((yy - fy) / (6 * sc + 30 * sc * flash)) ** 2) * np.exp(-np.abs(xx - fx) / (W * 0.45))
        core = np.exp(-(((xx - fx) ** 2 + (yy - fy) ** 2) / (2 * (90 * sc) ** 2)))
        sc_col = np.array(HP.pal("scan"), np.float32)
        img = img + (streak[..., None] * 2.0 + core[..., None] * 3.0 + 0.25) * sc_col * flash
    out = tonemap(img)
    ksm = float(sstep(zoom, *LOD["small_lights_on_at"]))
    lit = np.clip(0.25 + 2.4 * lum(aces(b2 + b3 * 1.5)), 0.25, 2.2)
    lit = lit * (0.55 + 0.45 * ksm) + P["rain_vol"] * np.clip(lum(vol) * P["vol_k"] * expo, 0, 1.5)
    rc = np.clip(aces(gblur(img, 30 * sc, 8)) * 1.6 + 0.25, 0, 1)
    rng = np.random.default_rng(41)
    for (n, (l0, l1), alpha, wid, spd) in RAIN_LAYERS:
        rain = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(rain)
        fall = t * 1400 * sc * spd
        for _ in range(int(n * sc)):
            x, y = rng.uniform(-100, W), rng.uniform(-100, H)
            L = rng.uniform(l0, l1) * sc
            u = rng.uniform(0.8, 1.2)
            y = (y + fall * u) % (H + 100) - 100
            d.line([(x, y), (x + L * 0.2, y + L)], fill=int(rng.uniform(120, 255)), width=max(1, int(wid * sc)))
        r = np.asarray(rain.filter(ImageFilter.GaussianBlur((0.6 if wid < 3 else 1.6) * sc)), np.float32) / 255 * alpha
        r = (r * lit)[..., None]
        out = out * (1 - np.clip(r, 0, 1)) + rc * r
    l1 = lum(out)[..., None]
    st = np.array(P["shadow_tint"], np.float32)
    ht = np.array(P["hi_tint"], np.float32)
    w_sh = np.clip(1 - l1 * 2.2, 0, 1)
    tk = P["tint_k"]
    out = out * (1 - tk * w_sh) + out * st * tk * w_sh
    out = out * (1 - 0.25 * np.clip(l1 * 2 - 0.6, 0, 1)) + out * ht * 0.25 * np.clip(l1 * 2 - 0.6, 0, 1)
    l1 = lum(out)[..., None]
    out = np.clip(l1 + (out - l1) * P["sat"], 0, None)
    out = out + np.array(P["lift"], np.float32) * (1 - out)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    out = out * (1 - P["vignette"] * np.clip(rr - 0.35, 0, 1) ** 1.6)[..., None]
    out = to_srgb(out)
    out = np.clip(0.18 * np.power(np.maximum(out, 0) / 0.18, P["contrast"]), 0, 1)
    bp = P.get("black", 0.0)                 # HQ: a black point (the haze veil over a 360 degree city lifts the floor)
    out = np.clip((out - bp) / (1.0 - bp), 0, 1)
    kn = KNEE
    top = P.get("knee_top", 0.93)
    out = np.where(out > kn, kn + (top - kn) * np.tanh((out - kn) / (top - kn)), out)
    if P["ca"] > 0:
        cx, cy = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
        k = P["ca"] * sc * np.clip(rr - 0.3, 0, 1) ** 1.5

        def samp(ch, s):
            xs = np.clip(np.round(xx + cx * s).astype(np.int32), 0, W - 1)
            ys = np.clip(np.round(yy + cy * s).astype(np.int32), 0, H - 1)
            return ch[ys, xs]
        out = np.stack([samp(out[..., 0], k), out[..., 1], samp(out[..., 2], -k)], axis=-1)
    g = np.random.default_rng(seed + 100).normal(0, 1, (H, W)).astype(np.float32)
    g = gblur(g, 0.55 * sc)
    out = out + (g * P["grain"] * (1.0 - 0.6 * lum(out)))[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    stem, outp = sys.argv[1], sys.argv[2]
    z = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    finish(stem, z).save(outp)
    print("plate", outp)
