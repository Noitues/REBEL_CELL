"""Usage: python squint_stats.py <out_dir_for_squints> <image> [<image> ...]
For each image: squint = 1/16 scale (BOX) + gaussian blur 0.6 (at the small size); prints mean luminance, p95, share of squint pixels above 0.38 ("loud"),
the brightest 24 px horizontal band of the FULL image (row centre, share of the height, value) like the street rounds' lum_profile, and the upper-frame (25-60 %) mean.
Writes squint_<name>.png (image | squint, side by side at half size). Written as a file: never python from stdin."""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.dont_write_bytecode = True


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def stats(path, out_dir):
    im = Image.open(path).convert("RGB")
    if im.size != (1920, 1080):
        im = im.resize((1920, 1080), Image.LANCZOS)
    sq = im.resize((120, 68), Image.BOX).filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(sq, dtype=np.float64) / 255.0
    l = lum(a)
    full = lum(np.asarray(im, dtype=np.float64) / 255.0)
    rows = full.mean(axis=1)
    k = 24
    sm = np.convolve(rows, np.ones(k) / k, mode="valid")
    i = int(np.argmax(sm))
    h = full.shape[0]
    up = full[int(h * 0.25):int(h * 0.60)].mean()
    name = os.path.splitext(os.path.basename(path))[0]
    big = sq.resize((1920, 1080), Image.BICUBIC)
    sh = Image.new("RGB", (1920, 540))
    sh.paste(im.resize((960, 540), Image.LANCZOS), (0, 0))
    sh.paste(big.resize((960, 540), Image.LANCZOS), (960, 0))
    os.makedirs(out_dir, exist_ok=True)
    sh.save(os.path.join(out_dir, "squint_%s.png" % name))
    return {"name": name, "mean": float(l.mean()), "p95": float(np.percentile(l, 95)), "loud": float((l > 0.38).mean()),
            "row_y": i + k // 2, "row_frac": (i + k // 2) / h, "row_val": float(sm[i]), "upper": float(up), "frame_mean": float(full.mean())}


if __name__ == "__main__":
    out = sys.argv[1]
    for p in sys.argv[2:]:
        r = stats(p, out)
        print("%s: squint mean=%.3f p95=%.3f loud(>0.38)=%.3f | brightest 24px row y=%d (%.0f%% down) val %.3f | upper(25-60%%) mean %.3f | full-frame mean %.3f" % (
            r["name"], r["mean"], r["p95"], r["loud"], r["row_y"], r["row_frac"] * 100.0, r["row_val"], r["upper"], r["frame_mean"]))
