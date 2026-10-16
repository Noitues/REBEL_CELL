"""Image metrics for the procedural-vs-custom comparison (CPU only, PIL + numpy).

Every metric runs on a copy of the image resampled to WORK_W pixels wide, so images of
different sizes are measured at the same scale. Coordinates in the config are normalised
(0..1) boxes [x0, y0, x1, y1].

Metrics (all on sRGB-encoded values, the critic's measure used in the r3 NOTES):
- luma: Rec.709 weights on sRGB values, 0..1. median, % < 0.10, % > 0.85.
- landmark: mean luma in the landmark box / mean luma in a ring around it (box grown by
  its own size on every side, the box itself removed). Also the p95 ratio.
- edges: mean Sobel magnitude of luma (whole frame), and per band the share of spectral
  power above 1/8 cycles per pixel (Hann window, DC removed).
- palette: hue histogram entropy (36 bins, chromatic pixels only: S > 0.25 and V > 0.15),
  the chromatic share, and the top 6 hue clusters (peaks of a smoothed 72-bin histogram).
- repetition: in the facade band, 128 px tiles (stride 64) of high-passed luma; per tile
  the strongest off-centre local maximum of the normalised autocorrelation (lags 4..48 px).
  Reported as the median tile peak, the p90 tile peak, and the share of tiles with a peak
  over 0.45 ("tiled share"). Regular window grids give strong off-centre peaks.
- skyline (views with a sky or horizon only), two profiles inside a vertical search range:
  (a) sky_*: the built-mass top, the first row with local texture (7x7 luma std > 0.022);
  (b) lit_*: the lit-mass top, the first row where 13 px smoothed luma passes the frame p80.
  (b) reads the bright foreground layer even when a dark wall of towers fills the sky, so it
  is the silhouette measure for the side views; (a) is the horizon measure for the city.
  For each: std of the height profile (frame heights) over the full width, and the minimum
  std over any 1/4-frame window (step 1/16).
- detail distribution: per 64 px tile, mean Sobel. detail_cv = std/mean over tiles (low =
  an even carpet of detail); calm_share = tiles under half the median (quiet areas).
- lights: bright blobs (luma > 0.6) per megapixel at 640 px wide, and focal concentration:
  the share of the top-1 % luma pixels that fall in the densest cell of a 3x3 grid, and
  the distance of their centroid to the nearest rule-of-thirds point (frame-height units).
"""
from __future__ import annotations

import math
import numpy as np
from PIL import Image

WORK_W = 1280
HF_CUTOFF = 0.125          # cycles per pixel; Nyquist is 0.5
REP_TILE = 128
REP_STRIDE = 64
REP_LAG_MIN = 4
REP_LAG_MAX = 48
REP_TILED = 0.45
CHROMA_S = 0.25
CHROMA_V = 0.15
BRIGHT_BLOB = 0.6


def open_src(path: str, crop=None) -> Image.Image:
    """Open an image as RGB, optionally cut to a normalised crop box first."""
    im = Image.open(path).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    return im


def load_work(path: str, crop=None) -> np.ndarray:
    im = open_src(path, crop)
    w, h = im.size
    nh = int(round(h * WORK_W / w))
    im = im.resize((WORK_W, nh), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


def luma(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def box_px(box, shape):
    h, w = shape[:2]
    x0, y0, x1, y1 = box
    return (int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h)))


def valid_mask(shape, masks) -> np.ndarray:
    m = np.ones(shape[:2], bool)
    for b in masks or []:
        x0, y0, x1, y1 = box_px(b, shape)
        m[y0:y1, x0:x1] = False
    return m


def box_blur(a: np.ndarray, r: int) -> np.ndarray:
    """Separable box blur of radius r (window 2r+1), edge-padded."""
    if r <= 0:
        return a
    k = 2 * r + 1
    p = np.pad(a, r, mode="edge")
    c = np.cumsum(p, axis=0)
    c = np.vstack([np.zeros((1, c.shape[1]), c.dtype), c])
    v = (c[k:] - c[:-k]) / k
    c = np.cumsum(v, axis=1)
    c = np.hstack([np.zeros((c.shape[0], 1), c.dtype), c])
    return (c[:, k:] - c[:, :-k]) / k


def sobel_mag(L: np.ndarray) -> np.ndarray:
    p = np.pad(L, 1, mode="edge")
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    return np.sqrt(gx * gx + gy * gy) / 8.0


def hf_share(L: np.ndarray) -> float:
    h, w = L.shape
    if h < 16 or w < 16:
        return float("nan")
    a = L - L.mean()
    win = np.outer(np.hanning(h), np.hanning(w))
    P = np.abs(np.fft.fft2(a * win)) ** 2
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.sqrt(fx * fx + fy * fy)
    P[0, 0] = 0.0
    tot = P.sum()
    return float(P[r > HF_CUTOFF].sum() / tot) if tot > 0 else float("nan")


def rgb_to_hsv(rgb: np.ndarray):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    nz = d > 1e-6
    rc = np.where(nz, (mx - r) / np.maximum(d, 1e-6), 0)
    gc = np.where(nz, (mx - g) / np.maximum(d, 1e-6), 0)
    bc = np.where(nz, (mx - b) / np.maximum(d, 1e-6), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(nz, h, 0)
    return h, s, mx


def palette(rgb: np.ndarray, valid: np.ndarray):
    h, s, v = rgb_to_hsv(rgb)
    chrom = valid & (s > CHROMA_S) & (v > CHROMA_V)
    share = float(chrom.sum() / max(valid.sum(), 1))
    hv = h[chrom]
    wts = (s * v)[chrom]
    if hv.size < 50:
        return {"hue_entropy_bits": float("nan"), "chroma_share": share, "hue_top_share": float("nan"), "clusters": []}
    hist36, _ = np.histogram(hv, bins=36, range=(0, 1), weights=wts)
    p = hist36 / hist36.sum()
    ent = float(-(p[p > 0] * np.log2(p[p > 0])).sum())
    hist72, _ = np.histogram(hv, bins=72, range=(0, 1), weights=wts)
    sm = hist72.copy()
    for k in (1, 2):
        sm = sm + 0.5 ** k * (np.roll(hist72, k) + np.roll(hist72, -k))
    tot = hist72.sum()
    clusters = []
    work = sm.copy()
    taken = np.zeros(72, bool)
    for _ in range(6):
        i = int(np.argmax(work))
        if work[i] <= 0:
            break
        lo, hi = i - 3, i + 4
        idx = [j % 72 for j in range(lo, hi) if not taken[j % 72]]
        mass = float(hist72[idx].sum() / tot)
        taken[idx] = True
        # mean colour of the pixels in this hue range, for the swatch
        hc = (i + 0.5) / 72.0
        dh = np.abs(((hv - hc + 0.5) % 1.0) - 0.5)
        sel = dh < 3.5 / 72.0
        col = rgb[chrom][sel].mean(0) if sel.any() else np.array([hc, hc, hc])
        clusters.append({"hue_deg": round(hc * 360.0, 1), "share": round(mass, 3),
                         "rgb": [int(round(c * 255)) for c in col]})
        for j in range(i - 3, i + 4):
            work[j % 72] = 0
    top = max((c["share"] for c in clusters), default=float("nan"))
    return {"hue_entropy_bits": ent, "chroma_share": share, "hue_top_share": top, "clusters": clusters}


def repetition(L: np.ndarray, valid: np.ndarray, band):
    x0, y0, x1, y1 = box_px(band, L.shape)
    hp = L - box_blur(L, 7)
    peaks = []
    n = 2 * REP_TILE
    for ty in range(y0, max(y0 + 1, y1 - REP_TILE + 1), REP_STRIDE):
        for tx in range(x0, max(x0 + 1, x1 - REP_TILE + 1), REP_STRIDE):
            t = hp[ty:ty + REP_TILE, tx:tx + REP_TILE]
            vm = valid[ty:ty + REP_TILE, tx:tx + REP_TILE]
            if t.shape != (REP_TILE, REP_TILE) or vm.mean() < 0.95:
                continue
            t = t - t.mean()
            if t.std() < 0.012:      # empty sky or flat fog: nothing to repeat
                continue
            F = np.fft.rfft2(t, s=(n, n))
            ac = np.fft.irfft2(F * np.conj(F), s=(n, n))
            ac = np.fft.fftshift(ac)
            c = n // 2
            ac = ac / ac[c, c]
            win = ac[c - REP_LAG_MAX:c + REP_LAG_MAX + 1, c - REP_LAG_MAX:c + REP_LAG_MAX + 1]
            core = win[1:-1, 1:-1]
            nb = np.stack([win[dy:dy + core.shape[0], dx:dx + core.shape[1]]
                           for dy in range(3) for dx in range(3) if not (dy == 1 and dx == 1)])
            locmax = core > nb.max(0)
            yy, xx = np.mgrid[-REP_LAG_MAX + 1:REP_LAG_MAX, -REP_LAG_MAX + 1:REP_LAG_MAX]
            far = np.maximum(np.abs(yy), np.abs(xx)) >= REP_LAG_MIN
            cand = core[locmax & far]
            peaks.append(float(cand.max()) if cand.size else 0.0)
    if not peaks:
        return {"rep_median": float("nan"), "rep_p90": float("nan"), "rep_tiled_share": float("nan"), "rep_tiles": 0}
    a = np.array(peaks)
    return {"rep_median": float(np.median(a)), "rep_p90": float(np.percentile(a, 90)),
            "rep_tiled_share": float((a > REP_TILED).mean()), "rep_tiles": int(a.size)}


def skyline(L: np.ndarray, rng):
    """Height profile of the built mass inside the vertical search range rng = [y0, y1]."""
    h, w = L.shape
    y0, y1 = int(rng[0] * h), int(rng[1] * h)
    # (a) built-mass top: the first texture (window edges, trims) from the top. Smooth haze
    #     gradients have no local texture, so fog and sky glow do not count as built.
    loc_std = np.sqrt(np.maximum(box_blur(L * L, 3) - box_blur(L, 3) ** 2, 0))
    built = (loc_std > 0.022)[y0:y1]
    run = box_blur(built.astype(np.float32), 5)
    prof = _first_rows(run > 0.35, y1 - y0, h)
    # (b) lit-mass top: the first row where the 13 px smoothed luma passes the frame's p80.
    #     Reads the bright foreground layer even when a dark wall of towers fills the sky.
    S = box_blur(L, 6)
    lit = (S > np.percentile(L, 80))[y0:y1]
    prof_lit = _first_rows(lit, y1 - y0, h)
    a = _profile_stats(prof)
    b = _profile_stats(prof_lit)
    return {"sky_std": a[0], "sky_min_q_std": a[1], "sky_mean_h": float(prof.mean()),
            "lit_std": b[0], "lit_min_q_std": b[1],
            "profile": prof, "profile_lit": prof_lit, "range": rng}


def _first_rows(mask: np.ndarray, span: int, h: int) -> np.ndarray:
    w = mask.shape[1]
    any_ = mask.any(0)
    first = np.where(any_, mask.argmax(0), span)
    prof = (span - first) / h
    pad = np.pad(prof, 6, mode="edge")      # median of 13 columns drops rain streaks and antennas
    return np.median(np.stack([pad[i:i + w] for i in range(13)]), 0)


def _profile_stats(prof: np.ndarray):
    w = prof.size
    win = w // 4
    step = max(1, w // 16)
    stds = [float(prof[i:i + win].std()) for i in range(0, w - win + 1, step)]
    return float(prof.std()), float(min(stds))


def landmark(L: np.ndarray, valid: np.ndarray, box):
    h, w = L.shape
    x0, y0, x1, y1 = box_px(box, L.shape)
    bw, bh = x1 - x0, y1 - y0
    X0, Y0 = max(0, x0 - bw), max(0, y0 - bh)
    X1, Y1 = min(w, x1 + bw), min(h, y1 + bh)
    ring = np.zeros_like(valid)
    ring[Y0:Y1, X0:X1] = True
    ring[y0:y1, x0:x1] = False
    ring &= valid
    inner = np.zeros_like(valid)
    inner[y0:y1, x0:x1] = True
    inner &= valid
    li, lr = L[inner], L[ring]
    return {"lm_ratio": float(li.mean() / max(lr.mean(), 1e-4)),
            "lm_p95_ratio": float(np.percentile(li, 95) / max(np.percentile(lr, 95), 1e-4)),
            "lm_centre_thirds_dist": float(_thirds_dist(((x0 + x1) / 2 / w, (y0 + y1) / 2 / h), w / h))}


def _thirds_dist(c, aspect):
    pts = [(a, b) for a in (1 / 3, 2 / 3) for b in (1 / 3, 2 / 3)]
    return min(math.hypot((c[0] - a) * aspect, c[1] - b) for a, b in pts)


def lights(L: np.ndarray, valid: np.ndarray):
    h, w = L.shape
    # blobs at 640 wide
    s = 2
    Ls = L[:h - h % s, :w - w % s].reshape(h // s, s, w // s, s).mean((1, 3))
    vs = valid[:h - h % s, :w - w % s].reshape(h // s, s, w // s, s).min((1, 3))
    b = (Ls > BRIGHT_BLOB) & vs
    n = _count_components(b)
    mp = vs.sum() * s * s / 1e6      # valid megapixels at the working resolution
    # focal concentration on the full working image
    vals = L[valid]
    thr = np.percentile(vals, 99)
    top = (L >= thr) & valid
    ys, xs = np.nonzero(top)
    cells = np.zeros((3, 3))
    np.add.at(cells, (np.minimum(ys * 3 // h, 2), np.minimum(xs * 3 // w, 2)), 1)
    conc = float(cells.max() / max(cells.sum(), 1))
    cen = (xs.mean() / w, ys.mean() / h) if xs.size else (0.5, 0.5)
    return {"blobs_per_mp": float(n / max(mp, 1e-6)),
            "focal_conc": conc, "focal_thirds_dist": float(_thirds_dist(cen, w / h)),
            "focal_centroid": [round(float(cen[0]), 3), round(float(cen[1]), 3)]}


def _count_components(b: np.ndarray) -> int:
    """4-connected components with a run-based union-find (no scipy)."""
    parent: list[int] = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    prev_runs: list[tuple[int, int, int]] = []
    for y in range(b.shape[0]):
        row = b[y]
        d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
        starts = np.nonzero(d == 1)[0]
        ends = np.nonzero(d == -1)[0]
        runs = []
        j = 0
        for s0, e0 in zip(starts, ends):
            lab = len(parent)
            parent.append(lab)
            while j < len(prev_runs) and prev_runs[j][1] <= s0:
                j += 1
            k = j
            while k < len(prev_runs) and prev_runs[k][0] < e0:
                a, bb = find(prev_runs[k][2]), find(lab)
                if a != bb:
                    parent[max(a, bb)] = min(a, bb)
                k += 1
            runs.append((int(s0), int(e0), lab))
        prev_runs = runs
    return len({find(i) for i in range(len(parent))})


def detail_variation(L: np.ndarray, valid: np.ndarray, tile: int = 64):
    """How unevenly detail is spread. Per 64 px tile: mean Sobel magnitude.
    detail_cv = std / mean over tiles (low = an even carpet of detail, no rest areas).
    calm_share = share of tiles under half the median tile (the quiet areas that let a focus read)."""
    S = sobel_mag(L)
    h, w = L.shape
    vals = []
    for y in range(0, h - tile + 1, tile):
        for x in range(0, w - tile + 1, tile):
            if valid[y:y + tile, x:x + tile].mean() < 0.9:
                continue
            vals.append(float(S[y:y + tile, x:x + tile].mean()))
    a = np.array(vals)
    if a.size < 4:
        return {"detail_cv": float("nan"), "calm_share": float("nan")}
    return {"detail_cv": float(a.std() / max(a.mean(), 1e-6)),
            "calm_share": float((a < 0.5 * np.median(a)).mean())}


def measure(path: str, spec: dict) -> dict:
    rgb = load_work(path, spec.get("crop"))
    L = luma(rgb)
    valid = valid_mask(L.shape, spec.get("mask"))
    v = L[valid]
    out = {
        "w_src": open_src(path, spec.get("crop")).size[0],
        "median": float(np.median(v)),
        "p95": float(np.percentile(v, 95)),
        "under_010": float((v < 0.10).mean()),
        "over_085": float((v > 0.85).mean()),
        "sobel_mean": float(sobel_mag(L)[valid].mean()),
    }
    bands = spec.get("bands") or {"upper": [0, 0, 1, 1 / 3], "lower": [0, 2 / 3, 1, 1]}
    for name in ("upper", "lower"):
        x0, y0, x1, y1 = box_px(bands[name], L.shape)
        out[f"hf_{name}"] = hf_share(L[y0:y1, x0:x1])
        out[f"sobel_{name}"] = float(sobel_mag(L)[y0:y1, x0:x1].mean())
    out.update(detail_variation(L, valid))
    out.update(palette(rgb, valid))
    out.update(repetition(L, valid, spec.get("facade", [0, 0, 1, 1])))
    if spec.get("landmark"):
        out.update(landmark(L, valid, spec["landmark"]))
    if spec.get("skyline"):
        out.update(skyline(L, spec["skyline"]))
    out.update(lights(L, valid))
    return out
