"""Landmark read check: the pyramid's luma vs the local background, from the object-index pass of a still.
landmark = compound + rooms + eye (pass index 1, 5, 6); local background = everything else inside the landmark's
bounding box grown by 35 %. Target (designer): landmark median ~1.5-2x the local background median.
Also writes a 320 px wide thumbnail for the silhouette check.
python hq_landmark.py <stem in D:/rc_scratch/halcyon/bl_stills> <plate.png> <thumb.png>"""
import sys

import numpy as np
from PIL import Image

stem, plate, thumb = sys.argv[1:4]
idx = np.load(stem + "_index.npy")[..., 0]
im = Image.open(plate).convert("RGB")
a = np.asarray(im.resize((idx.shape[1], idx.shape[0])), np.float32) / 255.0
L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
lm = np.isin(np.round(idx).astype(int), (1, 5, 6))
ys, xs = np.nonzero(lm)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
gy, gx = int((y1 - y0) * 0.35), int((x1 - x0) * 0.35)
box = np.zeros_like(lm)
box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
bg = box & ~lm
ml, mb = np.median(L[lm]), np.median(L[bg])
print("landmark median %.3f  local background median %.3f  ratio %.2f  (landmark mean %.3f, bg mean %.3f)" % (
    ml, mb, ml / max(mb, 1e-4), L[lm].mean(), L[bg].mean()))
im.resize((320, int(320 * im.height / im.width)), Image.LANCZOS).save(thumb)
