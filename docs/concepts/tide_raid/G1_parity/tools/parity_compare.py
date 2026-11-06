"""G1 parity compare: plate | Godot side by side, a difference heatmap, per-band metrics and squint rows.
usage: python parity_compare.py --godot g.png --target city_target.png --plate plate.png --out <dir> --name iter01 [--prev metrics_prev.json]
The metrics are taken on the city-only target (the offline pipeline without beams / UI, make_city_target.py); the side by side shows the real plate.
Written as a file (never python from stdin). Needs numpy, scipy, PIL."""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)
BANDS = {
    "all": (0.0, 1.0, 0.0, 1.0),
    "top": (0.0, 1.0, 0.0, 0.33),
    "mid": (0.0, 1.0, 0.33, 0.66),
    "bottom": (0.0, 1.0, 0.66, 1.0),
    "left": (0.0, 0.5, 0.0, 1.0),
    "right": (0.5, 1.0, 0.0, 1.0),
}
LIGHT_THR = 0.62
HUE_BINS = 12
UI_MASK_TOP = 0.0


def load(p):
    return np.asarray(Image.open(p).convert("RGB"), np.float32) / 255.0


def hsv(a):
    mx = a.max(-1)
    mn = a.min(-1)
    d = mx - mn
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60.0
    h = np.where(d > 1e-6, h, 0.0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def region(a, box):
    h, w = a.shape[:2]
    x0, x1, y0, y1 = box
    return a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]


def band_metrics(a):
    lum = (a * LUMW).sum(-1)
    h, s, v = hsv(a)
    out = {"luma": float(lum.mean()), "sat": float(s.mean()), "luma_p95": float(np.percentile(lum, 95)), "luma_p05": float(np.percentile(lum, 5))}
    wgt = s * v
    hist = np.zeros(HUE_BINS)
    idx = np.minimum((h / 360.0 * HUE_BINS).astype(int), HUE_BINS - 1)
    for k in range(HUE_BINS):
        hist[k] = wgt[idx == k].sum()
    hist = hist / max(hist.sum(), 1e-9)
    out["hue_hist"] = [round(float(x), 4) for x in hist]
    warm = ((h < 70) | (h > 330)) * wgt
    cool = ((h > 170) & (h < 280)) * wgt
    tot = max(float(warm.sum() + cool.sum()), 1e-9)
    out["warm"] = float(warm.sum() / tot)
    out["cool"] = float(cool.sum() / tot)
    lit = ndi.gaussian_filter(lum, 1.0) > LIGHT_THR
    lab, n = ndi.label(lit)
    out["light_points"] = int(n)
    out["light_area"] = float(lit.mean())
    # street reflection energy: luma in a 40 px column band under each light blob, excluding the blob (vertical smears)
    dil = ndi.binary_dilation(lit, structure=np.ones((41, 3)), origin=(-20, 0))
    refl = dil & ~ndi.binary_dilation(lit, iterations=2)
    out["refl_energy"] = float(lum[refl].mean() if refl.any() else 0.0)
    return out


def squint(a, w=320):
    im = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def blur4(a):
    return np.stack([ndi.gaussian_filter(a[..., i], 4.0) for i in range(3)], -1)


def heat(d):
    t = np.clip(d / 0.35, 0, 1)
    stops = np.array([[0, 0, 0], [40, 20, 120], [200, 30, 120], [255, 160, 20], [255, 255, 200]], np.float32) / 255
    x = t * (len(stops) - 1)
    i = np.minimum(x.astype(int), len(stops) - 2)
    f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


def label_img(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 14], fill=(8, 8, 20))
    d.text((4, 1), text, fill=(235, 235, 235))
    return im


def score(m_g, m_t):
    """one number per run, lower is better: normalised distances over the bands (luma, sat, warm/cool, hue, lights, reflection)."""
    s = 0.0
    n = 0
    for b in BANDS:
        g, t = m_g[b], m_t[b]
        s += abs(g["luma"] - t["luma"]) / max(t["luma"], 0.02)
        s += abs(g["sat"] - t["sat"]) / max(t["sat"], 0.05)
        s += abs(g["warm"] - t["warm"])
        s += 0.5 * float(np.abs(np.array(g["hue_hist"]) - np.array(t["hue_hist"])).sum())
        s += abs(np.log((g["light_points"] + 1) / (t["light_points"] + 1)))
        s += abs(g["refl_energy"] - t["refl_energy"]) / max(t["refl_energy"], 0.02)
        n += 6
    return s / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--plate", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    G = load(a.godot)
    T = load(a.target)
    P = load(a.plate) if a.plate else T
    mg = {b: band_metrics(region(G, box)) for b, box in BANDS.items()}
    mt = {b: band_metrics(region(T, box)) for b, box in BANDS.items()}
    mp = {b: band_metrics(region(P, box)) for b, box in BANDS.items()} if a.plate else mt
    bg, bt = blur4(G), blur4(T)
    sql1 = float(np.abs(bg - bt).mean() / max(float(bt.mean()), 1e-3))
    sc = score(mg, mt) + 2.0 * sql1
    res = {"name": a.name, "score": sc, "squint_l1": sql1, "godot": mg, "target": mt, "plate": mp}
    with open(os.path.join(a.out, a.name + "_metrics.json"), "w") as f:
        json.dump(res, f, indent=1)
    W = 960
    def half(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255 + .5).astype(np.uint8)).resize((W, 540), Image.LANCZOS)
    dl = np.abs((G * LUMW).sum(-1) - (T * LUMW).sum(-1))
    dc = np.abs(G - T).max(-1)
    hm = heat(np.maximum(dl, dc * 0.6))
    row1 = Image.new("RGB", (W * 2, 540))
    row1.paste(label_img(half(P), "plate " + os.path.basename(a.plate or a.target)), (0, 0))
    row1.paste(label_img(half(G), "godot " + a.name), (W, 0))
    row2 = Image.new("RGB", (W * 2, 540))
    row2.paste(label_img(half(T), "city-only target (offline pipeline, no beams / UI)"), (0, 0))
    row2.paste(label_img(half(hm), "difference (luma / chroma), 0..0.35"), (W, 0))
    sq = Image.new("RGB", (W * 2, 180 * 2 + 14))
    for i, (src, nm) in enumerate(((T, "target"), (G, "godot"))):
        pass
    s_t = squint(T); s_g = squint(G)
    b_t = squint(blur4(T)); b_g = squint(blur4(G))
    strip = Image.new("RGB", (W * 2, 180 + 14), (8, 8, 20))
    for k, im in enumerate((s_t, s_g, b_t, b_g)):
        strip.paste(im, (k * 480, 14))
    d = ImageDraw.Draw(strip)
    for k, t in enumerate(("target 320 px", "godot 320 px", "target blur 4 px", "godot blur 4 px")):
        d.text((k * 480 + 4, 1), t, fill=(235, 235, 235))
    sheet = Image.new("RGB", (W * 2, 540 * 2 + strip.height))
    sheet.paste(row1, (0, 0))
    sheet.paste(row2, (0, 540))
    sheet.paste(strip, (0, 1080))
    sheet.save(os.path.join(a.out, a.name + "_sheet.jpg"), quality=90)
    print("score %.4f (squint L1 %.4f)" % (sc, sql1))
    for b in ("all", "top", "mid", "bottom"):
        g, t = mg[b], mt[b]
        print("%-6s luma %.3f/%.3f sat %.3f/%.3f warm %.2f/%.2f lights %d/%d refl %.3f/%.3f" % (b, g["luma"], t["luma"], g["sat"], t["sat"], g["warm"], t["warm"], g["light_points"], t["light_points"], g["refl_energy"], t["refl_energy"]))


if __name__ == "__main__":
    main()
