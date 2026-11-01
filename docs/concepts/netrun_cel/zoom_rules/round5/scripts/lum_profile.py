"""Usage: python lum_profile.py <image> [<image> ...]
Prints, per image, the smoothed row-mean luminance profile summary: the brightest 24 px horizontal (row index and value),
the frame mean, the mean of the upper facade zone (rows 25-60 % of the height), and the ratio brightest / facade.
"""
import sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True


def prof(path):
    im = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
    h = lum.shape[0]
    rows = lum.mean(axis=1)
    k = 24
    sm = np.convolve(rows, np.ones(k) / k, mode="valid")
    i = int(np.argmax(sm))
    y0, y1 = int(h * 0.25), int(h * 0.60)
    fac = float(lum[y0:y1].mean())
    top = i + k // 2
    return {"file": path, "frame_mean": float(lum.mean()), "brightest_row_center": top, "brightest_row_frac": top / h, "brightest_val": float(sm[i]), "facade_mean": fac,
            "ratio": float(sm[i]) / max(fac, 1e-6), "road_mean_80_100": float(lum[int(h * 0.8):].mean())}


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = prof(p)
        print("%s: frame_mean=%.3f brightest 24px row at y=%d (%.0f%% down) value %.3f, facade(25-60%%) mean %.3f, ratio %.2f, road(80-100%%) mean %.3f" % (
            r["file"], r["frame_mean"], r["brightest_row_center"], r["brightest_row_frac"] * 100.0, r["brightest_val"], r["facade_mean"], r["ratio"], r["road_mean_80_100"]))
