"""Post for the graffiti shop exterior: exposure solved to a target median, hue-preserving tone map, bloom, vignette, grain.

python gs_post.py <beauty.npy> <out.png> [target_median=0.17] [width=1920]
"""
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def huemap(x, k=0.75):
    m = x.max(-1, keepdims=True)
    t = np.where(m < k, m, k + (1 - k) * (1 - np.exp(-(m - k) / (1 - k))))
    return x * (t / np.maximum(m, 1e-6))


def blur(a, s):
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "round12_modem_facade", "scripts"))
    import post as P
    return P.gblur(a, s)


def tone(lin, e):
    return to_srgb(huemap(np.maximum(lin * e, 0)))


def run(src, out, target=0.17, width=1920, bloom=0.55, solve_bloom=True):
    lin = np.load(src).astype(np.float32)
    lin = np.nan_to_num(lin, nan=0.0, posinf=50.0)
    H, W = lin.shape[:2]

    def disp_median(e):
        d = tone(lin, e)
        y = d @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        return float(np.median(y))
    lo, hi = 1e-3, 1e3
    for _ in range(40):
        mid = (lo * hi) ** 0.5
        if disp_median(mid) < target:
            lo = mid
        else:
            hi = mid
    e = (lo * hi) ** 0.5
    x = lin * e
    s = W / 1920.0
    # bloom from the over-exposed lin values (neon halos), added in linear
    br = np.maximum(x - 0.9, 0)
    glow = 0.5 * blur(br, 3 * s) + 0.35 * blur(br, 10 * s) + 0.25 * blur(br, 32 * s)
    x = x + glow * bloom
    d = to_srgb(huemap(x))
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    d = d * (1 - 0.18 * np.clip(v - 0.35, 0, 1))[..., None]
    rg = np.random.default_rng(3)
    d = d + rg.normal(0, 0.006, d.shape).astype(np.float32)
    im = Image.fromarray((np.clip(d, 0, 1) * 255 + 0.5).astype(np.uint8))
    if width != W:
        im = im.resize((width, width * 9 // 16), Image.LANCZOS)
    im.save(out)
    y = np.asarray(im.convert("L"), np.float32) / 255
    print("post exposure %.4f median %.3f -> %s" % (e, float(np.median(y)), out))
    return float(np.median(y)), e


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.17, int(sys.argv[4]) if len(sys.argv) > 4 else 1920)
