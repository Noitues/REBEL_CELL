"""ART-5 5b: finish the Blender previews into the concept look and make the reference comparison crops (v1); write the
REBEL_CELL crest mask.

finish(): ported from art-pass 097a6c0 docs/concepts/round31_meridian_combat/scripts/backdrop30.py (finish(): ink from
id / normal / depth edges with the wobble, painted grime, bloom + light spill from the glow pass, depth haze, rain;
the day grade), unchanged in its numbers, at the preview size. Used for review only: the game draws the same steps
in its own toon + ink pass (tools/spike/city/shaders, then 1B's kit).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import landmark_spec_v1 as SPEC  # noqa: E402

MODE = {
    "night": dict(ink=(0.05, 0.04, 0.09), haze=(0.09, 0.07, 0.17), haze_k=0.5, bloom=0.75, spill=0.45, rain=(0.75, 0.82, 1.0),
                  rain_a=0.16, grime=0.16),
    "day": dict(ink=(0.08, 0.08, 0.11), haze=(0.60, 0.67, 0.78), haze_k=0.22, bloom=0.4, spill=0.3, rain=(0.82, 0.88, 0.96),
                rain_a=0.11, grime=0.26),
}


def _load(path):
    im = Image.open(path)
    if im.mode.startswith("I;16") or im.mode == "I":
        return np.asarray(im, np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def _blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def _blur_f(a, r, down=4):
    h, w = a.shape[:2]
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((max(1, w // down), max(1, h // down)), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(r / down)).resize((w, h), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255.0


def _noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def _edges(a, thr):
    e = np.zeros(a.shape[:2], np.float32)
    for dy, dx in ((0, 1), (1, 0), (1, 1)):
        b = np.roll(np.roll(a, -dy, 0), -dx, 1)
        d = np.abs(a - b)
        d = d.sum(axis=2) if d.ndim == 3 else d
        e = np.maximum(e, (d > thr).astype(np.float32))
    return e


def _warp(mask, seed, amp=1.6):
    h, w = mask.shape
    ox = (_noise(h, w, 48, seed) - 0.5) * 2 * amp
    oy = (_noise(h, w, 48, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w]
    return mask[np.clip(np.round(yy + oy).astype(np.int32), 0, h - 1), np.clip(np.round(xx + ox).astype(np.int32), 0, w - 1)]


def finish(base, mode, passes):
    """backdrop30.finish on <base>_beauty_<mode>.png etc.; `passes` = the prefix of the normal / id / depth pass files."""
    M = MODE[mode]
    beauty = _load(base + "_beauty_%s.png" % mode)
    glow = _load(base + "_glow_%s.png" % mode)
    nrm = _load(passes + "_normal.png")
    ids = _load(passes + "_id.png")
    dep = _load(passes + "_depth.png")
    if dep.ndim == 3:
        dep = dep[..., 0]
    dep = ((dep + 0.055) / 1.055) ** 2.4
    h, w = dep.shape
    ink = np.maximum(np.maximum(_edges(ids, 0.03), _edges(nrm, 0.42)),
                     ((np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))) / np.maximum(dep, 1e-3) > 0.09).astype(np.float32))
    ink = _warp(ink, 7)
    thick = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    near = np.clip(1.25 - dep * 2.2, 0.35, 1.0)
    ink_a = _blur((np.clip(thick * near, 0, 1) * 0.9)[..., None].repeat(3, 2), 0.7)[..., 0]
    blot = _noise(h, w, 90, 31) * 0.6 + _noise(h, w, 22, 32) * 0.4
    speck = np.random.default_rng(33).random((h, w)).astype(np.float32)
    g = 1 - M["grime"] * (blot - 0.5) * 1.4 - 0.05 * (speck > 0.985)
    streak = Image.fromarray((thick * 255).astype(np.uint8)).resize((w, max(1, h // 6))).filter(ImageFilter.BoxBlur(1)).resize((w, h))
    streak = np.roll(np.asarray(streak.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255, 6, 0) * _noise(h, w, 6, 34)
    g = np.where(dep > 0.97, 1.0, g - 0.10 * streak)
    emis = glow.max(axis=2)
    img = beauty * (g[..., None] * (1 - np.clip(emis * 2, 0, 1))[..., None] + np.clip(emis * 2, 0, 1)[..., None])
    ink_a = ink_a * (1 - np.clip(emis * 1.6 - 0.4, 0, 1))
    img = img * (1 - ink_a[..., None]) + np.array(M["ink"], np.float32) * ink_a[..., None]
    k = w / 2880.0  # the concept's radii are for 2880 px renders
    b1, b2, b3 = _blur_f(glow, 10 * k * 1.5, 2), _blur_f(glow, 36 * k * 1.5, 4), _blur_f(glow, 110 * k * 1.5, 8)
    img = img * (1 + M["spill"] * (b2 * 0.8 + b3 * 1.0)) + M["bloom"] * (b1 * 0.55 + b2 * 0.4 + b3 * 0.12)
    hz = np.clip((dep - 0.32) / 0.55, 0, 1) ** 1.2 * M["haze_k"]
    img = img * (1 - hz[..., None]) + np.array(M["haze"], np.float32) * hz[..., None]
    rng = np.random.default_rng(41 if mode == "night" else 42)
    rain = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rain)
    for _ in range(int(2600 * (w * h) / (2880 * 1620))):
        x, y = rng.uniform(-100, w), rng.uniform(-100, h)
        L = rng.uniform(30, 90) * k * 1.5
        d.line([(x, y), (x + L * 0.22, y + L)], fill=int(rng.uniform(90, 255)), width=1)
    r = np.asarray(rain.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * M["rain_a"]
    img = img * (1 - r[..., None]) + np.array(M["rain"], np.float32) * r[..., None]
    if mode == "day":
        img = img * np.array([0.96, 0.99, 1.05], np.float32)
        lum = img.mean(axis=2, keepdims=True)
        img = (lum + (img - lum) * 1.18 - 0.5) * 1.1 + 0.5
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


PAIRS = {  # (Blender preview tag, Godot shot tag, mode, reference index in SPEC.JOBS[job]["refs"])
    "meridian_hq": [("meridian_hq", "meridian_hq_ref", "night", 0)],
    "solace_hq": [("solace_hq", "solace_hq_ref", "night", 0), ("solace_hq", "solace_hq_ref", "day", 1)],
    "solace_site": [("solace_site", "solace_site_ref", "night", 0)],
    "halcyon_hq": [("halcyon_hq", "halcyon_hq_ref", "night", 0), ("halcyon_hq", "halcyon_hq_ref", "day", 1)],
    "halcyon_site": [("halcyon_site", "halcyon_site_ref", "night", 0)],
    "orbital_hq": [("orbital_hq_closed", "orbital_hq_closed_ref", "night", 0), ("orbital_hq_open", "orbital_hq_open_ref", "night", 1),
                   ("orbital_hq_closed", "orbital_hq_closed_ref", "day", 2)],
    "orbital_site": [("orbital_site", "orbital_site_ref", "night", 0)],
    "rebel_cell_district": [("rebel_cell_district_home", "rebel_cell_district_home_iso", "night", 0),
                            ("rebel_cell_district_home_lit", "rebel_cell_district_lit_iso", "night", 1)],
}


def sheet(panels, out_path, size=(533, 300)):
    """Side by side with a caption bar: [(label, image or path), ...]."""
    im = Image.new("RGB", (len(panels) * (size[0] + 6) - 6, size[1] + 22), (20, 18, 26))
    d = ImageDraw.Draw(im)
    for i, (label, src) in enumerate(panels):
        a = (Image.open(src) if isinstance(src, str) else src).convert("RGB").resize(size, Image.LANCZOS)
        im.paste(a, (i * (size[0] + 6), 22))
        d.text((i * (size[0] + 6) + 6, 5), label, fill=(230, 230, 240))
    im.save(out_path, quality=82)


def finish_job(job, src, root):
    """Finish every Blender preview of `job` in `src`/prev into <tag>_final_<mode>.jpg (the concept recipe)."""
    pdir = os.path.join(src, "prev")
    for fn in sorted(os.listdir(pdir)):
        if "_beauty_" not in fn:
            continue
        tag, mode = fn[:-4].split("_beauty_")
        finish(os.path.join(pdir, tag), mode, os.path.join(pdir, tag)).save(os.path.join(pdir, "%s_final_%s.jpg" % (tag, mode)), quality=88)
        print("finished", tag, mode, flush=True)


def sheets(scratch, godot_dir, root):
    """docs/art_review/ART-5/5b/<tag>_<mode>_compare.jpg: Godot real-time | Blender concept recipe | reference."""
    review = os.path.join(root, "docs", "art_review", "ART-5", "5b")
    os.makedirs(review, exist_ok=True)
    for fn in os.listdir(review):
        if fn.endswith("_compare.jpg"):
            os.remove(os.path.join(review, fn))
    for job, pairs in PAIRS.items():
        for btag, gtag, mode, ri in pairs:
            ref = SPEC.JOBS[job]["refs"][ri]
            panels = [("Godot glTF (real time): %s %s" % (gtag, mode), os.path.join(godot_dir, "%s_%s.png" % (gtag, mode))),
                      ("Blender source, concept finish", os.path.join(scratch, job, "prev", "%s_final_%s.jpg" % (btag, mode))),
                      ("reference: " + os.path.basename(ref), os.path.join(root, "docs", "art_reference", ref))]
            out = os.path.join(review, "%s_%s_compare.jpg" % (btag, mode))
            sheet(panels, out)
            print("sheet", out, flush=True)


def crest_mask(path, px=512):
    """REBEL_CELL crest rule as an RGB texture on the iso screen plane (no alpha, so import never touches it):
    R = home zone, G = DISPATCH zone (0 outside, 128 detail line, 255 fist), B = blackout ring weight (0-255)."""
    import landmark_crest_v1 as CR
    w_bu = 2.2 * CR.RX * 2
    h_bu = 2.2 * CR.RY * 2
    pw, ph = px, int(round(px * h_bu / w_bu))
    x0, y1 = -w_bu / 2, CR.YC + h_bu / 2
    a = np.zeros((ph, pw, 3), np.uint8)
    zv = {0: 0, 1: 255, 2: 128}
    for j in range(ph):
        Y = y1 - (j + 0.5) * h_bu / ph
        for i in range(pw):
            X = x0 + (i + 0.5) * w_bu / pw
            a[j, i, 0] = zv[CR.zone(X, Y)]
            a[j, i, 1] = zv[CR.zone(X, Y, dispatch=True)]
            a[j, i, 2] = int(round(CR.ring_weight(X, Y) * 255))
    Image.fromarray(a, "RGB").save(path, optimize=True)
    return dict(job="rebel_cell_crest", file=os.path.basename(path), kind="mask",
                what="The round 34 crest rule for the CityModel window shader: project a window's world position onto the iso "
                     "screen plane (X = dot(p, right), Y = dot(p, up); camera yaw 135, pitch 40) relative to the palm's ground "
                     "point, then sample. R = home zone, G = DISPATCH zone (0 outside, 128 detail line = no windows, 255 = red "
                     "fist window), B = blackout ring weight.",
                mask=dict(width_px=pw, height_px=ph, screen_rect_bu=dict(x_min=round(x0, 3), x_max=round(-x0, 3),
                                                                           y_min=round(y1 - h_bu, 3), y_max=round(y1, 3)),
                          v_axis="image row 0 = screen y_max (up)", crest_h_bu=SPEC.CREST_H_BU, crest_lift_bu=SPEC.CREST_LIFT_BU,
                          right_godot=[round(CR.RIGHT[0], 6), 0.0, round(-CR.RIGHT[1], 6)],
                          up_godot=[round(CR.UP[0], 6), round(CR.UP[2], 6), round(-CR.UP[1], 6)]),
                reveal=dict(q_per_frame=SPEC.REVEAL_Q, seconds_per_frame=SPEC.FRAME_S["rebel_cell_district"],
                            rule="q 0 = the sector fully lit (ring windows at 0.9 density, detail lines lit), 1 = revealed: "
                                 "ring windows off where their value < q (flicker within 0.12 of the front), detail-line "
                                 "windows off, detail-line buildings darkened 0.55 x q toward (8, 6, 12)/255, the red fist steady"),
                window_density=SPEC.WIN_DENSITY, red_srgb=SPEC.RED)
