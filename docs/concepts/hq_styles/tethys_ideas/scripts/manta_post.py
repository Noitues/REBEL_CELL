"""Manta shadow decal: a dark, soft-edged manta silhouette projected on the drowned city under the manta (the water hides a real
shadow, so it is a decal). The outline comes from ideas.idea_E (SHADOW_JSON), is dropped straight down to the drowned roofs and
offset a little along the key light, projected through the golden-plate overview camera, blurred, and multiplied into the plate. The
landmark pixels (object index 1: the manta, the jelly buildings) are not darkened.
python manta_post.py <plate.png> <shadow.json> <index.npy> <out.png> [strength]"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LOC = np.array([-233.3009, 179.8009, 160.8693])
TGT = np.array([-328.75, 275.25, 0.0])
LENS = 30.0


def project(P, W, H):
    f = TGT - LOC
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0])
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    out = []
    for p in P:
        d = np.array(p) - LOC
        z = d @ f
        x = (d @ r) / z * (LENS / 36.0)
        y = (d @ u) / z * (LENS / 36.0)
        out.append((W * (0.5 + x), H * 0.5 - W * y))
    return out


def main():
    plate, sj, idx, out = sys.argv[1:5]
    k = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
    im = Image.open(plate).convert("RGB")
    W, H = im.size
    S = json.load(open(sj))
    zr = S["ZW"] - 9.0                                 # the drowned roofs
    off = (15.0, 10.0)                                 # the key light is low from the left: the shadow falls ahead and to the right of the manta
    poly3 = [(p[0] + off[0], p[1] + off[1], zr) for p in S["outline"]]
    tail = S["tail"][0]
    fwd = S["fwd"]
    # a tail strip behind the body
    cx, cy = S["centre"]
    tl = [(cx - fwd[0] * 24.0 + off[0], cy - fwd[1] * 24.0 + off[1], zr), (tail[0] + off[0], tail[1] + off[1], zr)]
    pts = project(poly3, W, H)
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.polygon(pts, fill=255)
    tp = project(tl, W, H)
    d.line(tp, fill=255, width=max(2, int(W * 0.004)))
    mask = mask.filter(ImageFilter.GaussianBlur(W * 0.007))
    m = np.asarray(mask, np.float32) / 255.0
    try:
        ix = np.load(idx)
        ix = np.asarray(Image.fromarray(ix.astype(np.float32)).resize((W, H), Image.NEAREST)) if ix.shape[:2] != (H, W) else ix
        lm = (np.round(ix.reshape(H, W)) == 1).astype(np.float32)
        lm = np.asarray(Image.fromarray((lm * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255.0
        m = m * (1 - lm)
    except Exception as e:
        print("no index mask:", e)
    # keep the decal off the dam and its causeway: everything below the projected dam crest, and a strip along the causeway
    try:
        O = json.load(open("D:/rc_scratch/hq_styles/tethys_abyssal/scr/zoned_t_over.json"))
        P = O["tethys_dam"]["P"]
        crest = sorted(project([(p[0], p[1], 13.0) for p in P], W, H))
        ex = Image.new("L", (W, H), 0)
        de = ImageDraw.Draw(ex)
        poly = [(0, crest[0][1])] + crest + [(W, crest[-1][1]), (W, H), (0, H)]
        de.polygon(poly, fill=255)
        c0, c1 = O["tethys_causeway"]
        cw = project([(c0[0], c0[1], 5.0), (c1[0], c1[1], 5.0)], W, H)
        de.line(cw, fill=255, width=max(6, int(W * 0.014)))
        ex = ex.filter(ImageFilter.GaussianBlur(W * 0.002))
        m = m * (1 - np.asarray(ex, np.float32) / 255.0)
    except Exception as e:
        print("no dam mask:", e)
    a = np.asarray(im, np.float32) / 255.0
    a = a * (1 - k * m[..., None])
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
    print("shadow", out, "area %.1f%%" % (100 * float((m > 0.5).mean())))


if __name__ == "__main__":
    main()
