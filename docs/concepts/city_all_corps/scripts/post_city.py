"""City-all-corps: the post (numpy / PIL) and the label overlay.

python post_city.py aaa  <stem> <out.png> [--labels <labeled.png>]   AAA-2 grade, exposure solved to the r3 median
python post_city.py main <stem> <out.png>                            the MAINLINE finish (post40 / sb_mhq values)
python post_city.py stats <png>                                      value checks (median, < 0.10, > 0.85)

AAA-2: linear Combined -> exposure k solved (bisection, deterministic) so the frame median luma hits the r3 target
(0.14) -> 3-scale bloom of the highlights -> extended-Reinhard shoulder -> sRGB -> a cool shadow lift and a vignette.
MAINLINE: post40.finish's order with the mainline numbers (ink from id / normal / depth edges, grime, bloom 0.75,
spill 0.5, low fog patches 0.22, depth haze 0.34, rain 0.11, grade (0.94, 0.92, 1.04)), then sb_mhq's capture match
(sat 0.64, gain (0.76, 0.76, 0.84)).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402

FONTS = os.path.join(CP.WT, "assets", "fonts")
BAHN = "C:/Windows/Fonts/bahnschrift.ttf"
MONO = os.path.join(FONTS, "ShareTechMono-Regular.ttf")


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def srgb(x):
    x = np.clip(x, 0, None)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def _box(a, r, axis):
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, r):
    """Gaussian-like blur (three box passes) of a float HxWxC array, radius ~ r px; big radii work downsampled."""
    h, w = a.shape[:2]
    f = max(1, int(r // 4))
    hs, ws = h // f, w // f
    small = a[:hs * f, :ws * f].reshape(hs, f, ws, f, -1).mean(axis=(1, 3))
    rb = max(1, int(round(r / f / 1.7)))
    for _ in range(3):
        small = _box(_box(small, rb, 0), rb, 1)
    if f == 1:
        out = np.zeros_like(a)
        out[:hs, :ws] = small
        return out
    big = np.zeros((h, w, a.shape[2]), np.float32)
    for c in range(a.shape[2]):
        big[..., c] = np.asarray(Image.fromarray(small[..., c].astype(np.float32), mode="F").resize((w, h), Image.BILINEAR))
    return big


def stats(img):
    l = luma(img)
    return dict(median=float(np.median(l)), under_010=float((l < 0.10).mean()), over_085=float((l > 0.85).mean()),
                mean=float(l.mean()))


# ------------------------------------------------------------------ AAA-2
def tone(x, white=5.0):
    return x * (1 + x / (white * white)) / (1 + x)


def aaa(stem, out, target=None, soft=False):
    T = CP.AAA["targets"]
    target = target or T["median"]
    rgb = np.load(stem + "_rgb.npy").astype(np.float32)
    # black point (art review 4 / 6): the fog veil (a near-uniform airlight over the frame) is taken off at the
    # frame's own 5th-percentile level per channel, so the deep darks come back without crushing the mid-tones
    bp = CP.AAA["black_point"] * np.percentile(rgb.reshape(-1, 3), 5, axis=0).astype(np.float32)
    rgb = np.clip(rgb - bp, 0, None)
    if CP.LAYOUT_MODE == "a2" and os.path.exists(stem + "_z.npy"):
        # round 5: aerial perspective on the far mountains: toward a faint blue-grey haze with distance (the ridgelines fade)
        dz = np.clip(np.load(stem + "_z.npy").astype(np.float32)[..., 0], 0, 60000.0)
        dz = np.asarray(Image.fromarray(dz, mode="F").filter(ImageFilter.MedianFilter(5)), np.float32)
        fz = np.clip((dz - 1900.0) / 1500.0, 0.0, 1.0)[..., None] ** 1.3 * 0.62
        hz = np.array([0.012, 0.017, 0.032], np.float32) + 0.35 * np.percentile(rgb, 30, axis=(0, 1)).astype(np.float32)
        rgb = rgb * (1 - fz) + hz * fz
    h, w = rgb.shape[:2]
    sc = w / 3840.0
    l = luma(rgb)
    hi = np.clip(rgb - 0.9, 0, None) * (l[..., None] > 0.9)
    bloom = blur(hi, 6 * sc + 1) * 0.35 + blur(hi, 24 * sc + 1) * 0.25 + blur(hi, 80 * sc + 1) * 0.12
    if soft:                                          # round 3c realism A/B: bloom halved, no vignette (contrast capped at toe 2.0)
        bloom = bloom * 0.5

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = (1 - (0.0 if soft else 0.32) * np.clip(((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2 * 0.8) / 0.5, 0, 1) ** 1.5)[..., None]

    def finish(k, toe, st=1):
        x = (rgb[::st, ::st] + bloom[::st, ::st]) * k
        y = tone(x)
        y = y + np.array([0.0008, 0.0010, 0.0030], np.float32) * (1 - np.clip(luma(y)[..., None] * 8, 0, 1))
        return np.clip(srgb(y) ** toe * vig[::st, ::st], 0, 1)

    def solve(toe):
        lo_k, hi_k = 0.02, 80.0
        for _ in range(36):                               # exposure solved to the r3 median (deterministic bisection)
            mid = math.sqrt(lo_k * hi_k)
            m = float(np.median(luma(finish(mid, toe, 4))))
            if m < target:
                lo_k = mid
            else:
                hi_k = mid
        return math.sqrt(lo_k * hi_k)
    # the toe (a power on the display values) is raised in steps until 25-40 % of the frame sits under 0.10 at the
    # solved median (r3 targets); deterministic, smallest toe that meets the lower bound
    lo_u = T["under_010"][0] + 0.02
    for toe in ((1.0, 1.1, 1.2, 1.3, 1.4, 1.55, 1.7, 1.85, 2.0) if soft else (1.0, 1.1, 1.2, 1.3, 1.4, 1.55, 1.7, 1.85, 2.0, 2.2, 2.4)):
        k = solve(toe)
        u = float((luma(finish(k, toe, 4)) < 0.10).mean())
        if u >= lo_u:
            break
    img = finish(k, toe)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(out, optimize=True)
    s = stats(img)
    s["exposure"] = k
    s["toe"] = toe
    l_ = luma(img)
    s["p10"], s["p90"] = float(np.percentile(l_, 10)), float(np.percentile(l_, 90))
    s["spread"] = s["p90"] - s["p10"]
    print("AAA", out, {kk: round(vv, 4) for kk, vv in s.items()})
    return img, s


# ------------------------------------------------------------------ DAY (round 3)
def day(stem, out, target=None):
    """the daytime grade: a light black point (part of the haze veil off), a soft bloom of the sun glints, exposure
    solved to the day median (no band set yet: city_preset.DAY target_median), an extended-Reinhard shoulder, a gentle
    contrast and saturation lift, a light vignette."""
    DY = CP.DAY
    target = target or DY["target_median"]
    rgb = np.load(stem + "_rgb.npy").astype(np.float32)
    bp = DY["black_point"] * np.percentile(rgb.reshape(-1, 3), 5, axis=0).astype(np.float32)
    rgb = np.clip(rgb - bp, 0, None)
    # the far aerial perspective (depth pass): toward a pale haze at the level of the lit city, so the sea and the
    # horizon dissolve cleanly (the sea-mist volume is off by day)
    DH = DY["depth_haze"]
    dep = np.load(stem + "_z.npy").astype(np.float32)[..., 0]
    dep = np.clip(dep, 0, 60000.0)
    # the depth pass is per-sample noisy where rays pass the transparent water / glass: a median filter steadies it
    dep = np.asarray(Image.fromarray(dep, mode="F").filter(ImageFilter.MedianFilter(5)), np.float32)
    f = np.clip(1.0 - np.exp(-np.clip(dep - DH["start"], 0, None) / DH["efold"]), 0, DH["max"])[..., None]
    lvl = float(np.percentile(luma(rgb), 80))
    hz = np.array(DY["haze"]["col"], np.float32) * lvl * 1.15
    rgb = rgb * (1 - f) + hz * f
    h, w = rgb.shape[:2]
    sc = w / 3840.0
    l = luma(rgb)
    thr = float(np.percentile(l, 99.7))
    hi = np.clip(rgb - thr, 0, None) * (l[..., None] > thr)
    bloom = blur(hi, 8 * sc + 1) * 0.25 + blur(hi, 40 * sc + 1) * 0.12
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = (1 - 0.16 * np.clip(((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2 * 0.8) / 0.5, 0, 1) ** 1.5)[..., None]

    def finish(k, st=1, con=None):
        con = DY["contrast"] if con is None else con
        x = (rgb[::st, ::st] + bloom[::st, ::st]) * k
        y = srgb(tone(x, DY["white"]))
        y = DY.get("lift", 0.0) + (1.0 - DY.get("lift", 0.0)) * y      # a shadow floor (the references keep p10 near 0.04)
        y = np.clip(target + (y - target) * con, 0, 1)            # contrast about the target median
        lm = y.mean(-1, keepdims=True)
        y = lm + (y - lm) * DY["sat"]
        return np.clip(y * vig[::st, ::st], 0, 1)

    def solve_k(con):
        lo_k, hi_k = 0.02, 200.0
        for _ in range(36):
            mid = math.sqrt(lo_k * hi_k)
            if float(np.median(luma(finish(mid, 4, con)))) < target:
                lo_k = mid
            else:
                hi_k = mid
        return math.sqrt(lo_k * hi_k)
    con = DY["contrast"]
    k = solve_k(con)
    if DY.get("target_spread"):            # designer r3b: the p90 - p10 spread matched to the references
        lo_c, hi_c = 0.6, DY.get("contrast_max", 2.4)
        for _ in range(18):
            con = (lo_c + hi_c) / 2
            k = solve_k(con)
            l4 = luma(finish(k, 4, con))
            if float(np.percentile(l4, 90) - np.percentile(l4, 10)) < DY["target_spread"]:
                lo_c = con
            else:
                hi_c = con
        con = (lo_c + hi_c) / 2
        k = solve_k(con)
    img = finish(k, 1, con)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(out, optimize=True)
    s = stats(img)
    s["exposure"] = k
    s["contrast"] = con
    l_ = luma(img)
    s["p10"], s["p90"] = float(np.percentile(l_, 10)), float(np.percentile(l_, 90))
    s["spread"] = s["p90"] - s["p10"]
    print("DAY", out, {kk: round(vv, 4) for kk, vv in s.items()})
    return img, s


# ------------------------------------------------------------------ MAINLINE
def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // cell + 3) * cell, (h // cell + 3) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def edges(a, thr):
    d = np.abs(a - np.roll(a, -1, 1)).sum(-1) + np.abs(a - np.roll(a, -1, 0)).sum(-1)
    return (d > thr).astype(np.float32)


def main_post(stem, out):
    M = CP.MAINLINE
    lin_rgb = np.load(stem + "_rgb.npy").astype(np.float32)
    beauty = srgb(lin_rgb)
    h, w = beauty.shape[:2]
    sc = w / 2880.0
    nrm = np.asarray(Image.open(stem + "_normal.png").convert("RGB"), np.float32) / 255.0
    ids = np.asarray(Image.open(stem + "_id.png").convert("RGB"), np.float32) / 255.0
    dep = np.load(stem + "_z.npy").astype(np.float32)[..., 0]
    dep = np.where(dep > 1e5, 1e5, dep)
    d0 = float(np.median(dep[dep < 1e5]))
    dd = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
    e_d = (dd > 0.03 * dep).astype(np.float32)
    ink = np.maximum(np.maximum(edges(ids, 0.03), edges(nrm, 0.42)), e_d)
    ink_a = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255 * 0.6
    glow = np.clip(beauty - 0.55, 0, 1) * 2.0
    emis = np.clip(glow.max(axis=2) * 2, 0, 1)
    blot = noise(h, w, max(8, int(90 * sc)), 31) * 0.6 + noise(h, w, max(4, int(22 * sc)), 32) * 0.4
    g = 1 - M["grime"] * (blot - 0.5) * 1.4
    img = beauty * (g[..., None] * (1 - emis[..., None]) + emis[..., None])
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    b1, b2, b3 = blur(glow, 8 * sc + 1), blur(glow, 30 * sc + 1), blur(glow, 90 * sc + 1)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12)
    fn = noise(h, w, max(16, int(160 * sc)), 70) * 0.6 + noise(h, w, max(8, int(60 * sc)), 71) * 0.4
    fa = np.clip((fn - 0.5) * 2.6, 0, 1) * 0.7 * M["fog_k"]
    img = img * (1 - fa[..., None]) + (np.array(M["fog"], np.float32) + b3 * 1.2) * fa[..., None]
    far = np.clip((dep - 0.6 * d0) / (1.2 * d0), 0, 1) ** 1.2
    img = img * (1 - far[..., None] * M["haze_k"]) + np.array(M["haze"], np.float32) * far[..., None] * M["haze_k"]
    rng = np.random.default_rng(41)
    rl = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rl)
    for _ in range(int(2200 * sc * sc) + 200):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        Ln = rng.uniform(30, 80) * sc
        d.line([(x, y), (x + Ln * 0.2, y + Ln)], fill=int(rng.uniform(80, 255)), width=max(1, int(sc)))
    r = np.asarray(rl.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
    img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    img = img * np.array(M["grade"], np.float32)
    l = img.mean(-1, keepdims=True)
    img = np.clip((l + (img - l) * M["match_sat"]) * np.array(M["match_gain"], np.float32), 0, 1)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(out, optimize=True)
    s = stats(img)
    print("MAIN", out, {kk: round(vv, 4) for kk, vv in s.items()})
    return img, s


# ------------------------------------------------------------------ labels (the game's map-label style + crests)
def crest_mask(corp, size):
    if corp in ("aurelian", "tethys"):
        sys.path.insert(0, os.path.join(CP.CONCEPTS, "new_corps", "roman", "scripts"))
        import nc_kit as NK
        m = (NK.g_laurel_arch() if corp == "aurelian" else NK.g_wave_a())
    else:
        p = os.path.join(CP.CONCEPTS, "route_map_graph", "storyboard", "scratch", "emblems", corp + ".png")
        m = Image.open(p).getchannel("A")
    return m.resize((size, size), Image.LANCZOS)


SUB = {"meridian": "HQ // THE CONTAINER FORT", "solace": "HQ // THE HELIX", "halcyon": "HQ // THE PANOPTICON",
       "orbital": "HQ // THE LAUNCH RING", "rebel_cell": "HOME // THE CANYON", "aurelian": "HQ // CIRCVS AVRELIVS",
       "tethys": "HQ // ATLANTIS STATION"}


def labels(img_path, anchors_path, out):
    A = json.load(open(anchors_path))
    im = Image.open(img_path).convert("RGB")
    W_, H_ = im.size
    k = W_ / 3840.0
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(BAHN, int(46 * k))
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    fs = ImageFont.truetype(MONO, int(24 * k))
    boxes = []
    order = sorted([c for c in CP.CORPS if A["anchors"].get(c, {}).get("label")], key=lambda c: A["anchors"][c]["label"][1])
    for corp in order:
        an = A["anchors"][corp]
        x, y = an["label"][0], an["label"][1]
        base = an["crown"] or an["base"]
        col = tuple(int(v * 255) for v in CP.DISTRICTS[corp]["hue"])
        name = CP.DISTRICTS[corp]["name"]
        tw = d.textlength(name, font=f)
        sw = d.textlength(SUB[corp], font=fs)
        cr = int(44 * k)                                  # crest disc radius
        bw = max(tw, sw) + 2 * cr + 64 * k
        bh = 92 * k
        y -= 150 * k
        x0, y0 = x - bw / 2, y - bh / 2
        for (bx0, by0, bx1, by1) in boxes:              # keep tags apart: push up
            if x0 < bx1 and x0 + bw > bx0 and y0 < by1 and y0 + bh > by0:
                y0 = by0 - bh - 14 * k
        x1, y1 = x0 + bw, y0 + bh
        boxes.append((x0, y0, x1, y1))
        # leader: a thin line in the corp hue from the tag to the landmark, a ring on the landmark
        d.line([(x, y1), (base[0], base[1] - 6 * k)], fill=col + (220,), width=max(2, int(3 * k)))
        rr = 10 * k
        d.ellipse([base[0] - rr, base[1] - rr, base[0] + rr, base[1] + rr], outline=col + (255,), width=max(2, int(3 * k)))
        sk = 12 * k
        poly = [(x0 + sk, y0), (x1, y0), (x1 - sk, y1), (x0, y1)]
        d.polygon(poly, fill=(10, 9, 16, 236))
        d.line(poly + [poly[0]], fill=(3, 3, 6, 255), width=max(2, int(4 * k)))
        d.polygon([(x0 + sk, y0), (x0 + sk + 14 * k, y0), (x0 + 14 * k, y1), (x0, y1)], fill=col + (255,))
        # crest disc: navy fill, hue ring, white glyph
        cx, cy = x0 + 26 * k + cr, (y0 + y1) / 2
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(5, 13, 28, 255), outline=col + (255,), width=max(2, int(4 * k)))
        gm = crest_mask(corp, int(cr * 1.5))
        glyph = Image.new("RGBA", gm.size, (240, 238, 232, 255))
        glyph.putalpha(gm)
        lay.alpha_composite(glyph, (int(cx - gm.size[0] / 2), int(cy - gm.size[1] / 2)))
        tx = cx + cr + 18 * k
        d.text((tx, y0 + 30 * k), name, font=f, fill=col + (255,), anchor="lm")
        d.text((tx, y0 + 68 * k), SUB[corp], font=fs, fill=(200, 205, 220, 255), anchor="lm")
    # a quiet corner key
    d.text((40 * k, H_ - 44 * k), "THE CITY // SEVEN DISTRICTS", font=fs, fill=(220, 220, 230, 230), anchor="lm")
    im = Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")
    im.save(out, optimize=True)
    print("LABELS", out)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "aaa":
        aaa(sys.argv[2], sys.argv[3], soft="--soft" in sys.argv)
    elif what == "day":
        day(sys.argv[2], sys.argv[3])
    elif what == "main":
        main_post(sys.argv[2], sys.argv[3])
    elif what == "labels":
        labels(sys.argv[2], sys.argv[3], sys.argv[4])
    elif what == "stats":
        a = np.asarray(Image.open(sys.argv[2]).convert("RGB"), np.float32) / 255
        print({kk: round(vv, 4) for kk, vv in stats(a).items()})
