"""V3 AAA post: finish the Cycles passes into a plate (no UI) per look. Seeded; numpy + PIL only.

python post_aaa.py <bl_dir> <out.png> [look]
Order (all in linear light until the tone map):
  1. surfaces = the denoised Cycles Combined (no volume objects in it);
  2. "cel" / "hybrid": the lighting (Combined - Emission) / Albedo is banded into soft toon steps (hue kept), so the
     light is path traced but the shading reads as our cel ramp; "real" skips this;
  3. ink lines from the Eevee id / normal / depth passes (1.5x res, downsampled = anti-aliased), "real" has none;
  4. volume: surfaces x T + in-scatter. T is exact for the homogeneous boxes (camera rays vs. boxes, up to the Cycles
     depth); the in-scatter is the half-res Cycles volume render (holdout surfaces), upsampled;
  5. background classes (mid row, far city) desaturated and dimmed per look, so the route leads;
  6. exposure, a filmic shoulder (ACES fit), HDR bloom (3 radii), lit rain, grade, vignette, chromatic aberration at the
     edges, film grain.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LOOKS = {
    # every number used by the post, per look (NOTES.md quotes these). Shared critique values: exposure 0.75,
    # vol_k 1.3, tint 0.30 teal-navy, sat 1.0, contrast 1.25 @ 0.18, bloom thr 1.2 (0.12, 0.10, 0.08), lift ~0.
    "cel": dict(exposure=2.6, band=1.0, band_stops=1.25, band_soft=0.10, ink=0.95, ink_bg=0.35, bg_desat=0.40,
                bg_dim=0.58, vol_k=1.3, tint_k=0.30, bloom=(0.12, 0.10, 0.08), bloom_thr=1.2, grain=0.022, ca=1.6,
                vignette=0.30, ambient=(0.035, 0.028, 0.075), lift=(0.0, 0.0, 0.004), shadow_tint=(0.25, 0.45, 0.6),
                hi_tint=(1.0, 0.93, 0.95), sat=1.0, contrast=1.25),
    "hybrid": dict(exposure=2.8, band=0.45, band_stops=1.25, band_soft=0.18, ink=0.62, ink_bg=0.22, bg_desat=0.38,
                   bg_dim=0.58, vol_k=1.3, tint_k=0.30, bloom=(0.12, 0.10, 0.08), bloom_thr=1.2, grain=0.026, ca=2.0,
                   vignette=0.34, ambient=(0.018, 0.016, 0.04), lift=(0.0, 0.0, 0.004), shadow_tint=(0.25, 0.45, 0.6),
                   hi_tint=(1.0, 0.90, 0.88), sat=1.0, contrast=1.25),
    "real": dict(exposure=2.65, band=0.0, band_stops=1.0, band_soft=0.2, ink=0.0, ink_bg=0.0, bg_desat=0.30, bg_dim=0.6,
                 vol_k=1.3, tint_k=0.30, bloom=(0.12, 0.10, 0.08), bloom_thr=1.2, grain=0.03, ca=2.4,
                 vignette=0.38, ambient=(0.0, 0.0, 0.0), lift=(0.0, 0.0, 0.004), shadow_tint=(0.25, 0.45, 0.6),
                 hi_tint=(1.0, 0.86, 0.86), sat=1.0, contrast=1.12,    # r2: exposure 2.6 -> 3.0, contrast 1.25 -> 1.12
                 vol_soft=0.25, rain_vol=1.6, vol_glow=0.8, vol_glow_thr=0.02),     # r3: the beams need head-room (soft clamp 0.08 -> 0.25); rain in beams
}
RAIN_LAYERS = [
    # count (at 2560), length px, alpha, width, speed  (CRITIQUE §3 #10: far mist / mid / near)
    (4000, (3, 6), 0.05, 1, 0.6),
    (1800, (14, 24), 0.10, 1, 1.0),
    (60, (60, 95), 0.25, 3, 1.6),
]
RAIN_ON_ROUTE = 0.25
KNEE = 0.66
VOL_SOFT = 0.08     # vol p99 is ~0.04: only hot spots roll off


def load_npy(p):
    return np.load(p).astype(np.float32)


def load_png(path):
    im = Image.open(path)
    if im.mode.startswith("I;16") or im.mode == "I":
        return np.asarray(im, np.float32) / 65535.0
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def resize_f(a, size, resample=Image.BICUBIC):
    """Resize a float array (h, w[, c]) to size = (w, h)."""
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize(size, resample), np.float32)
    return np.stack([resize_f(a[..., c], size, resample) for c in range(a.shape[2])], axis=-1)


def _box(a, r, axis):
    """Box blur of half-width r along an axis (cumulative sum, edge-clamped)."""
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
    """Gaussian blur (three box passes) of a float array, optionally at reduced resolution."""
    if sigma <= 0:
        return a
    h, w = a.shape[:2]
    small = resize_f(a, (max(1, w // down), max(1, h // down)), Image.BILINEAR) if down > 1 else a
    sg = sigma / down
    r = max(0, int(round((math.sqrt(12 * sg * sg / 3 + 1) - 1) / 2)))
    if r == 0 and sg > 0.3:
        k = np.array([sg, 1.0, sg], np.float32) * 0 + np.array([0.25, 0.5, 0.25], np.float32)
        for ax in (0, 1):
            small = (np.roll(small, 1, ax) * k[0] + small * k[1] + np.roll(small, -1, ax) * k[2]).astype(np.float32)
    for _ in range(3):
        small = _box(_box(small, r, 0), r, 1)
    return resize_f(small, (w, h), Image.BILINEAR) if down > 1 else small


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((h // cell + 2, w // cell + 2)).astype(np.float32)
    im = Image.fromarray(n, "F").resize(((w // cell + 2) * cell, (h // cell + 2) * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w]


def diff_edges(a, thr):
    e = np.zeros(a.shape[:2], np.float32)
    for dy, dx in ((0, 1), (1, 0), (1, 1)):
        b = np.roll(np.roll(a, -dy, 0), -dx, 1)
        d = np.abs(a - b)
        d = d.sum(axis=2) if d.ndim == 3 else d
        e = np.maximum(e, (d > thr).astype(np.float32))
    return e


def warp(mask, seed, amp):
    h, w = mask.shape
    ox = (noise(h, w, 48, seed) - 0.5) * 2 * amp
    oy = (noise(h, w, 48, seed + 1) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w]
    xs = np.clip(np.round(xx + ox).astype(np.int32), 0, w - 1)
    ys = np.clip(np.round(yy + oy).astype(np.int32), 0, h - 1)
    return mask[ys, xs]


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def tonemap(x):
    """Max-RGB hue-preserving shoulder: out = c * T(m) / m with m = max(r, g, b), so a neon tube keeps its hue up to the
    core; only where m > 4 does 20 % of the per-channel ACES result come in, so the very hottest pixel can whiten."""
    m = np.maximum(x.max(axis=-1, keepdims=True), 1e-6)
    hp = x * (aces(m) / m)
    w = 0.2 * np.clip((m - 3.0) / 2.0, 0, 1)
    return np.clip(hp * (1 - w) + aces(x) * w, 0, 1)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def cam_rays(A, W, H):
    """World-space ray origin and (unnormalised, camera-z = -1) directions for every pixel, Blender camera model."""
    M = np.array(A["cam_world"], np.float64)
    lens, sensor = A["lens"], A["sensor"]
    sx, sy = A["shift"]
    k = sensor / lens
    xs = ((np.arange(W) + 0.5) / W - 0.5 + sx) * k
    ys = ((0.5 - (np.arange(H) + 0.5) / H) * (H / W) + sy) * k
    X, Y = np.meshgrid(xs, ys)
    d = np.stack([X, Y, -np.ones_like(X)], axis=-1)
    Rm = M[:3, :3]
    dw = d @ Rm.T
    return M[:3, 3], dw


def transmittance(A, z, W, H):
    o, d = cam_rays(A, W, H)
    zz = np.minimum(z, 4000.0)
    tau = np.zeros((H, W, 3), np.float64)
    for b in A["vol_boxes"]:
        x0, y0, z0, x1, y1, z1, dens, col = b
        lo = np.array([x0, y0, z0])
        hi = np.array([x1, y1, z1])
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = 1.0 / d
            t0 = (lo - o) * inv
            t1 = (hi - o) * inv
        tmin = np.nanmax(np.minimum(t0, t1), axis=-1)
        tmax = np.nanmin(np.maximum(t0, t1), axis=-1)
        tmin = np.maximum(tmin, 0.0)
        tmax = np.minimum(tmax, zz)
        seg = np.clip(tmax - tmin, 0, None) * np.linalg.norm(d, axis=-1)
        tau += seg[..., None] * dens * np.array(col)[None, None, :]
    return np.exp(-tau).astype(np.float32)


def band(L, stops, soft):
    """Soft toon steps of the lighting luminance in log2 space (hue kept)."""
    l = np.maximum(lum(L), 1e-5)
    x = np.log2(l) / stops
    f = x - np.floor(x)
    s = np.clip((f - (0.5 - soft)) / (2 * soft), 0, 1)
    s = s * s * (3 - 2 * s)
    xb = np.floor(x) + s
    lb = np.power(2.0, xb * stops)
    return L * (lb / l)[..., None]


def route_mask(A, W, H):
    """1 inside the current room + options (+12 px) and along every route cable (6 px dilation), at render size."""
    import sgraph3 as G
    sx = W / 1920.0
    st, opts = G.states(G.WALK_START)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for i in [G.WALK_START[-1]] + list(opts) + ["L7_0"]:
        p = A["rooms"][i]["front"]
        if p and all(q is not None for q in p):
            d.polygon([(q[0] * sx, q[1] * sx) for q in p], fill=255)
    for e in A["edges"]:
        pts = [(q[0] * sx, q[1] * sx) for q in e["pts"] if q is not None]
        if len(pts) > 1:
            d.line(pts, fill=255, width=int(14 * sx))
    m = m.filter(ImageFilter.MaxFilter(2 * int(6 * sx) + 1)).filter(ImageFilter.GaussianBlur(3 * sx))
    return np.asarray(m, np.float32) / 255.0


def finish(bl, look, shot="O_overview", t=2.0, seed=7, over=None, inp=None):
    """inp (r3 loop): the per-frame arrays instead of the pass files: comb, emit, alb, z, vol (at vol res), T_het (at
    vol res), loop_p (the loop phase, for loop-safe rain) and a cache dict (route mask, box transmittance)."""
    P = dict(LOOKS[look])
    P.update(over or {})
    A = json.load(open(os.path.join(bl, "anchors_%s.json" % shot)))
    if inp is None:
        comb = load_npy(os.path.join(bl, shot + "_combined.npy"))
        emit = load_npy(os.path.join(bl, shot + "_emit.npy"))
        alb = load_npy(os.path.join(bl, shot + "_albedo.npy"))
        z = load_npy(os.path.join(bl, shot + "_z.npy"))[..., 0]
    else:
        comb, emit, alb, z = inp["comb"], inp["emit"], inp["alb"], inp["z"]
    cache = inp.get("cache", {}) if inp else {}
    H, W = comb.shape[:2]
    sc = W / 2560.0
    sky = z > 5000
    vpath = os.path.join(bl, shot + "_vol_combined.npy")
    # the in-scatter is low frequency: a 1.2 px blur at half res removes the last denoiser mottling before upsampling
    if inp is not None:
        vol = resize_f(gblur(inp["vol"], 1.2), (W, H))
    else:
        vol = resize_f(gblur(load_npy(vpath), 1.2), (W, H)) if os.path.exists(vpath) else np.zeros_like(comb)
    vol = np.maximum(vol, 0)
    # soft clamp: haze lives around 0.01-0.2; a forward-scatter hot spot (backglow seen through a tower gap) read as a
    # blown orb, so in-scatter rolls off above ~0.35
    vol = vol / (1.0 + lum(vol)[..., None] / P.get("vol_soft", VOL_SOFT))
    DW = None
    sem_p = os.path.join(bl, shot + "_sem.png")
    if os.path.exists(sem_p):
        sem_hi = load_png(sem_p)
        DW = sem_hi.shape[1]
        cls = np.asarray(Image.fromarray((sem_hi[..., 0] * 255).astype(np.uint8)).resize((W, H), Image.NEAREST), np.float32) / 255
    else:
        cls = np.zeros((H, W), np.float32)
    ground = np.abs(cls - 0.2) < 0.04
    bgm = ((np.abs(cls - 0.6) < 0.04) | (np.abs(cls - 0.85) < 0.04)).astype(np.float32)
    # 2. banded light (cel / hybrid)
    surf = comb.copy()
    if P["band"] > 0:
        a = np.maximum(alb, 0.03)
        Lgt = np.maximum(comb - emit, 0) / a
        Lb = band(Lgt, P["band_stops"], P["band_soft"])
        Lb = np.maximum(Lb, np.array(P["ambient"], np.float32))   # the cel ramp's violet floor
        cel = alb * Lb + emit
        m = ((~ground) & (~sky) & (lum(alb) > 0.02)).astype(np.float32)
        m = gblur(m, 0.6)[..., None] * P["band"]
        surf = surf * (1 - m) + cel * m
    # 3. ink
    if P["ink"] > 0 and DW:
        nrm = load_png(os.path.join(bl, shot + "_normal.png"))
        ids = load_png(os.path.join(bl, shot + "_id.png"))
        dep = load_png(os.path.join(bl, shot + "_depth.png"))
        if dep.ndim == 3:
            dep = dep[..., 0]
        dep = ((dep + 0.055) / 1.055) ** 2.4
        hs = DW / 2560.0
        e_id = diff_edges(ids, 0.03)
        e_n = diff_edges(nrm, 0.42)
        rel = np.abs(dep - np.roll(dep, -1, 1)) + np.abs(dep - np.roll(dep, -1, 0))
        e_d = (rel / np.maximum(dep, 1e-3) > 0.012).astype(np.float32)
        ink = np.maximum(np.maximum(e_id, e_n), e_d)
        ink = warp(ink, seed, 1.4 * hs)
        ink = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
        ink = resize_f(ink, (W, H), Image.BOX)
        dist = dep_to_dist = resize_f(dep, (W, H), Image.BILINEAR) * 1500.0
        cam_d = A["cam"].get("dist", 268.0)
        fade = np.clip(1.0 - (dist - cam_d * 1.1) / 260.0, 0.25, 1.0)
        k = P["ink"] * (1 - bgm) + P["ink_bg"] * bgm
        ia = np.clip(ink * fade * k, 0, 1)
        ia = ia * (1 - np.clip(lum(emit) * 0.8 - 0.2, 0, 1))
        ia = np.where(sky, 0, ia)
        inkc = np.array((0.010, 0.008, 0.022), np.float32)
        surf = surf * (1 - ia[..., None]) + inkc * ia[..., None]
        del dep_to_dist
    # storyboard LOD: puddle reflections sharpen with zoom (a blur on the wet ground, sigma puddle_blur px at 2560)
    if P.get("puddle_blur", 0.0) > 0.05:
        gm = gblur(ground.astype(np.float32), 2.0 * sc)[..., None]
        surf = surf * (1 - gm) + gblur(surf, P["puddle_blur"] * sc, 2) * gm
    # background emitters (far roof trims, mid-row billboards) give up 45 % so they never out-shout the route
    surf = surf - emit * (P.get("bg_emit_cut", 0.65) * bgm)[..., None]
    # 4. volume
    if "T_box" not in cache:
        cache["T_box"] = transmittance(A, z, W, H)
    T = cache["T_box"]
    tpath = os.path.join(bl, shot + "_trans_combined.npy")
    if inp is not None and inp.get("T_het") is not None:
        T = T * np.clip(resize_f(gblur(inp["T_het"], 0.8), (W, H)), 0, 1)
    elif os.path.exists(tpath):     # r3: the heterogeneous strata and mist (Cycles transmittance pass), times the boxes
        T = T * np.clip(resize_f(gblur(load_npy(tpath), 0.8), (W, H)), 0, 1)
    img = surf * T + vol * P["vol_k"]
    # 5. background quieter
    l3 = lum(img)[..., None]
    bg = (img * (1 - P["bg_desat"]) + l3 * P["bg_desat"]) * P["bg_dim"]
    img = img * (1 - bgm[..., None]) + bg * bgm[..., None]
    # 6. exposure, bloom (HDR), tone map
    img = img * P["exposure"]
    hot = np.maximum(img - P["bloom_thr"], 0) + emit * P["exposure"] * 0.04
    # r3: the lit fog and the beams glow a little (a soft halo round the shafts and the band undersides)
    hot = hot + np.maximum(vol - P.get("vol_glow_thr", 0.0), 0) * (P["vol_k"] * P["exposure"] * P.get("vol_glow", 0.0))
    b1 = gblur(hot, 6 * sc, 2)
    b2 = gblur(hot, 24 * sc, 4)
    b3 = gblur(hot, 135 * sc, 8)
    img = img + b1 * P["bloom"][0] + b2 * P["bloom"][1] + b3 * P["bloom"][2]
    out = tonemap(img)
    # rain: 3 depth layers, lit by the glow around them, cut to x0.25 over the protected rooms and the route cables
    if "keep" not in cache:
        cache["keep"] = route_mask(A, W, H)
    keep = cache["keep"]
    lit = np.clip(0.25 + 2.4 * lum(aces(b2 + b3 * 1.5)), 0.25, 2.2)
    # r3: rain catches the beams and the lit fog: drops brighten with the local in-scatter (the shafts)
    lit = lit + P.get("rain_vol", 0.0) * np.clip(lum(vol) * P["vol_k"] * P["exposure"], 0, 1.5)
    rc = np.clip(aces(gblur(img, 30 * sc, 8)) * 1.6 + 0.25, 0, 1)
    rng = np.random.default_rng(41)
    for (n, (l0, l1_), alpha, wid, spd) in RAIN_LAYERS:
        rain = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(rain)
        fall = t * 1400 * sc * spd
        loop_p = inp.get("loop_p") if inp else None
        for _ in range(int(n * sc)):
            x, y = rng.uniform(-100, W), rng.uniform(-100, H)
            L = rng.uniform(l0, l1_) * sc
            u = rng.uniform(0.8, 1.2)
            if loop_p is None:
                y = (y + fall * u) % (H + 100) - 100
            else:
                # loop-safe: each drop falls a whole number of wraps per loop, so frame 96 = frame 0
                wraps = max(1, int(round(inp["loop_T"] * 1400 * sc * spd * u / (H + 100))))
                y = (y + wraps * (H + 100) * loop_p) % (H + 100) - 100
            d.line([(x, y), (x + L * 0.2, y + L)], fill=int(rng.uniform(120, 255)), width=max(1, int(wid * sc)))
        r = np.asarray(rain.filter(ImageFilter.GaussianBlur((0.6 if wid < 3 else 1.6) * sc)), np.float32) / 255 * alpha * P.get("rain_k", 1.0)
        r = (r * lit * (1 - (1 - RAIN_ON_ROUTE) * keep))[..., None]
        out = out * (1 - np.clip(r, 0, 1)) + rc * r
    # grade: teal-navy shadows, warm highlights, saturation, lift
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
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    out = out * (1 - P["vignette"] * np.clip(rr - 0.35, 0, 1) ** 1.6)[..., None]
    out = to_srgb(out)
    out = np.clip(0.18 * np.power(np.maximum(out, 0) / 0.18, P["contrast"]), 0, 1)   # contrast @ 0.18
    # display knee: above 0.70 the plate rolls off toward 0.93, so only the option rooms (and the 2D overlay drawn
    # after this) reach the top of the range (CRITIQUE §5: <= 2.5 % of the frame over 0.85)
    kn = KNEE
    out = np.where(out > kn, kn + (0.93 - kn) * np.tanh((out - kn) / (0.93 - kn)), out)
    # chromatic aberration (edges only): R pushed out, B pulled in
    if P["ca"] > 0:
        cx, cy = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
        k = P["ca"] * sc * np.clip(rr - 0.3, 0, 1) ** 1.5
        def samp(ch, s):
            xs = np.clip(np.round(xx + cx * s).astype(np.int32), 0, W - 1)
            ys = np.clip(np.round(yy + cy * s).astype(np.int32), 0, H - 1)
            return ch[ys, xs]
        out = np.stack([samp(out[..., 0], k), out[..., 1], samp(out[..., 2], -k)], axis=-1)
    # grain (seeded, luminance-weighted, finer in highlights)
    g = np.random.default_rng(seed + 100).normal(0, 1, (H, W)).astype(np.float32)
    g = gblur(g, 0.55 * sc)
    out = out + (g * P["grain"] * (1.0 - 0.6 * lum(out)))[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    bl, outp = sys.argv[1], sys.argv[2]
    look = sys.argv[3] if len(sys.argv) > 3 else json.load(open(os.path.join(bl, "anchors_O_overview.json")))["look"]
    finish(bl, look).save(outp)
    print("plate", outp)


# r3: the "real" look reads its grade from the look preset (look_preset.py), so a new layout uses the same numbers
try:
    import look_preset as _LP
    LOOKS["real"].update(_LP.PRESET["post"])
except ImportError:
    pass
