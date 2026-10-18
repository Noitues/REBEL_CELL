"""Image metrics for the NA-04 checks (CPU only, numpy and Pillow).

Ported from the art-pass `pvc_metrics.py` (commit 6a58733c, CHECKS_SPEC section 8) and `hq_values.py` (12.1, 12.2).
Every number that is a tunable comes from the `checks.composition.constants` block of `composition.json`; only the
algorithm shape (blur radii of the local-std window, the 3 x 3 Sobel, the 2 x 2 blob average) is fixed here.
No Blender, Godot or network imports. All box arguments are normalised `[x0, y0, x1, y1]`.
"""
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

NAN = float("nan")


def load_rgb(path: str, crop: Optional[Sequence[float]] = None) -> Image.Image:
    """Open an image as RGB, optionally cut to a normalised crop box first."""
    im = Image.open(path).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    return im


def to_array(im: Image.Image) -> np.ndarray:
    """RGB image to float32 array in 0..1 (native size, sRGB-encoded values)."""
    return np.asarray(im.convert("RGB")).astype(np.float32) / 255.0


def work_array(im: Image.Image, work_w: int) -> np.ndarray:
    """Resample to `work_w` pixels wide (LANCZOS, height `round(h * work_w / w)`), RGB 0..1."""
    w, h = im.size
    nh = int(round(h * work_w / w))
    return to_array(im.resize((work_w, nh), Image.LANCZOS))


def luma(rgb: np.ndarray) -> np.ndarray:
    """Rec.709 weights applied to sRGB-encoded values (no linearisation)."""
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def box_px(box: Sequence[float], shape: Tuple[int, ...]) -> Tuple[int, int, int, int]:
    """Normalised box to pixel box `(x0, y0, x1, y1)` with `round`."""
    h, w = shape[:2]
    x0, y0, x1, y1 = box
    return (int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h)))


def valid_mask(shape: Tuple[int, ...], masks: Optional[Sequence[Sequence[float]]]) -> np.ndarray:
    """All-True mask with the listed normalised boxes cleared (captures have no UI: pass `None`)."""
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
    """Sobel magnitude of luma divided by 8."""
    p = np.pad(L, 1, mode="edge")
    gx = (p[:-2, 2:] + 2 * p[1:-1, 2:] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[1:-1, :-2] + p[2:, :-2])
    gy = (p[2:, :-2] + 2 * p[2:, 1:-1] + p[2:, 2:]) - (p[:-2, :-2] + 2 * p[:-2, 1:-1] + p[:-2, 2:])
    return np.sqrt(gx * gx + gy * gy) / 8.0


def rgb_to_hsv(rgb: np.ndarray):
    """Hue (0..1), saturation, value arrays."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    nz = d > 1e-6
    rc = np.where(nz, (mx - r) / np.maximum(d, 1e-6), 0)
    gc = np.where(nz, (mx - g) / np.maximum(d, 1e-6), 0)
    bc = np.where(nz, (mx - b) / np.maximum(d, 1e-6), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(nz, h, 0)
    return h, s, mx


# ---------------------------------------------------------------- 12.1 value band
def value_stats(L: np.ndarray, valid: Optional[np.ndarray], c: Dict[str, Any]) -> Dict[str, float]:
    """`median`, `under_010` (share below `dark`) and `over_085` (share above `bright`) over valid pixels.

    `c` is the `checks.value` block.
    """
    v = L[valid] if valid is not None else L.ravel()
    if v.size == 0:
        return {"median": NAN, "under_010": NAN, "over_085": NAN}
    return {"median": float(np.median(v)), "under_010": float((v < c["dark"]).mean()),
            "over_085": float((v > c["bright"]).mean())}


# ---------------------------------------------------------------- 12.7 palette
def palette(rgb: np.ndarray, valid: np.ndarray, k: Dict[str, Any]) -> Dict[str, float]:
    """`hue_entropy_bits` and `hue_top_share` (the biggest of the hue clusters); NaN under `chroma_min_px` pixels."""
    h, s, v = rgb_to_hsv(rgb)
    chrom = valid & (s > k["chroma_s"]) & (v > k["chroma_v"])
    share = float(chrom.sum() / max(valid.sum(), 1))
    hv = h[chrom]
    wts = (s * v)[chrom]
    if hv.size < k["chroma_min_px"]:
        return {"hue_entropy_bits": NAN, "chroma_share": share, "hue_top_share": NAN}
    nb, nf, half = k["hue_bins"], k["hue_fine_bins"], k["hue_cluster_half"]
    hist, _ = np.histogram(hv, bins=nb, range=(0, 1), weights=wts)
    p = hist / hist.sum()
    ent = float(-(p[p > 0] * np.log2(p[p > 0])).sum())
    fine, _ = np.histogram(hv, bins=nf, range=(0, 1), weights=wts)
    sm = fine.copy()
    for j in (1, 2):
        sm = sm + 0.5 ** j * (np.roll(fine, j) + np.roll(fine, -j))
    tot = fine.sum()
    work = sm.copy()
    taken = np.zeros(nf, bool)
    shares: List[float] = []
    for _ in range(k["hue_clusters"]):
        i = int(np.argmax(work))
        if work[i] <= 0:
            break
        idx = [j % nf for j in range(i - half, i + half + 1) if not taken[j % nf]]
        shares.append(round(float(fine[idx].sum() / tot), 3))
        taken[idx] = True
        for j in range(i - half, i + half + 1):
            work[j % nf] = 0
    return {"hue_entropy_bits": ent, "chroma_share": share, "hue_top_share": max(shares) if shares else NAN}


# ---------------------------------------------------------------- 12.7 repetition
def repetition(L: np.ndarray, valid: np.ndarray, band: Sequence[float], k: Dict[str, Any]) -> Dict[str, float]:
    """`rep_p90`: 90th percentile of the per-tile autocorrelation peaks in the facade band."""
    tile, stride = k["rep_tile"], k["rep_stride"]
    lag_min, lag_max = k["rep_lag"]
    x0, y0, x1, y1 = box_px(band, L.shape)
    hp = L - box_blur(L, k["rep_hp_radius"])
    peaks: List[float] = []
    n = 2 * tile
    for ty in range(y0, max(y0 + 1, y1 - tile + 1), stride):
        for tx in range(x0, max(x0 + 1, x1 - tile + 1), stride):
            t = hp[ty:ty + tile, tx:tx + tile]
            vm = valid[ty:ty + tile, tx:tx + tile]
            if t.shape != (tile, tile) or vm.mean() < k["rep_valid"]:
                continue
            t = t - t.mean()
            if t.std() < k["rep_min_std"]:
                continue
            F = np.fft.rfft2(t, s=(n, n))
            ac = np.fft.fftshift(np.fft.irfft2(F * np.conj(F), s=(n, n)))
            c = n // 2
            ac = ac / ac[c, c]
            win = ac[c - lag_max:c + lag_max + 1, c - lag_max:c + lag_max + 1]
            core = win[1:-1, 1:-1]
            nb = np.stack([win[dy:dy + core.shape[0], dx:dx + core.shape[1]]
                           for dy in range(3) for dx in range(3) if not (dy == 1 and dx == 1)])
            locmax = core > nb.max(0)
            yy, xx = np.mgrid[-lag_max + 1:lag_max, -lag_max + 1:lag_max]
            far = np.maximum(np.abs(yy), np.abs(xx)) >= lag_min
            cand = core[locmax & far]
            peaks.append(float(cand.max()) if cand.size else 0.0)
    if not peaks:
        return {"rep_p90": NAN, "rep_tiles": 0}
    return {"rep_p90": float(np.percentile(np.array(peaks), 90)), "rep_tiles": len(peaks)}


# ---------------------------------------------------------------- 12.7 skyline
def _first_rows(mask: np.ndarray, span: int, h: int, med: int) -> np.ndarray:
    w = mask.shape[1]
    first = np.where(mask.any(0), mask.argmax(0), span)
    prof = (span - first) / h
    r = med // 2
    pad = np.pad(prof, r, mode="edge")
    return np.median(np.stack([pad[i:i + w] for i in range(med)]), 0)


def _profile_stats(prof: np.ndarray) -> Tuple[float, float]:
    w = prof.size
    win = w // 4
    step = max(1, w // 16)
    stds = [float(prof[i:i + win].std()) for i in range(0, w - win + 1, step)]
    return float(prof.std()), float(min(stds))


def skyline(L: np.ndarray, rng: Sequence[float], k: Dict[str, Any]) -> Dict[str, float]:
    """Built-mass top (`sky_*`, R-HOR-1) and lit-mass top (`lit_*`, R-SIL) profile statistics inside `rng`."""
    h, w = L.shape
    y0, y1 = int(rng[0] * h), int(rng[1] * h)
    if y1 - y0 < 1 or w < 16:
        return {"sky_std": NAN, "sky_min_q_std": NAN, "lit_std": NAN, "lit_min_q_std": NAN}
    med = int(k["profile_median"])
    loc_std = np.sqrt(np.maximum(box_blur(L * L, 3) - box_blur(L, 3) ** 2, 0))
    built = (loc_std > k["built_std"])[y0:y1]
    run = box_blur(built.astype(np.float32), 5)
    prof = _first_rows(run > k["built_run"], y1 - y0, h, med)
    S = box_blur(L, 6)
    lit = (S > np.percentile(L, k["lit_percentile"]))[y0:y1]
    prof_lit = _first_rows(lit, y1 - y0, h, med)
    a = _profile_stats(prof)
    b = _profile_stats(prof_lit)
    return {"sky_std": a[0], "sky_min_q_std": a[1], "lit_std": b[0], "lit_min_q_std": b[1]}


# ---------------------------------------------------------------- 12.7 landmark ring
def landmark_ring(L: np.ndarray, valid: np.ndarray, box: Sequence[float]) -> Dict[str, float]:
    """`lm_ratio` = mean luma in the box / mean luma in the ring (box grown by its own size, box removed).

    NaN when the box or the ring holds no valid pixel.
    """
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
    if not inner.any() or not ring.any():
        return {"lm_ratio": NAN}
    return {"lm_ratio": float(L[inner].mean() / max(L[ring].mean(), 1e-4))}


# ---------------------------------------------------------------- 12.7 lights and detail
def _count_components(b: np.ndarray) -> int:
    """4-connected components with a run-based union-find (no scipy)."""
    parent: List[int] = []

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    prev_runs: List[Tuple[int, int, int]] = []
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
            kk = j
            while kk < len(prev_runs) and prev_runs[kk][0] < e0:
                a, bb = find(prev_runs[kk][2]), find(lab)
                if a != bb:
                    parent[max(a, bb)] = min(a, bb)
                kk += 1
            runs.append((int(s0), int(e0), lab))
        prev_runs = runs
    return len({find(i) for i in range(len(parent))})


def blobs(L: np.ndarray, valid: np.ndarray, k: Dict[str, Any]) -> Dict[str, float]:
    """`blobs_per_mp`: bright blobs on a 2 x 2 averaged image per valid megapixel at working size."""
    h, w = L.shape
    s = 2
    Ls = L[:h - h % s, :w - w % s].reshape(h // s, s, w // s, s).mean((1, 3))
    vs = valid[:h - h % s, :w - w % s].reshape(h // s, s, w // s, s).min((1, 3))
    n = _count_components((Ls > k["bright_blob"]) & vs)
    mp = vs.sum() * s * s / 1e6
    return {"blobs_per_mp": float(n / max(mp, 1e-6))}


def detail_variation(L: np.ndarray, valid: np.ndarray, k: Dict[str, Any]) -> Dict[str, float]:
    """`detail_cv` (std / mean of per-tile Sobel) and `calm_share` (tiles under `calm_frac` of the median)."""
    S = sobel_mag(L)
    h, w = L.shape
    tile = int(k["detail_tile"])
    vals = []
    for y in range(0, h - tile + 1, tile):
        for x in range(0, w - tile + 1, tile):
            if valid[y:y + tile, x:x + tile].mean() < k["valid_tile_share"]:
                continue
            vals.append(float(S[y:y + tile, x:x + tile].mean()))
    a = np.array(vals)
    if a.size < k["detail_min_tiles"]:
        return {"detail_cv": NAN, "calm_share": NAN}
    return {"detail_cv": float(a.std() / max(a.mean(), 1e-6)),
            "calm_share": float((a < k["calm_frac"] * np.median(a)).mean())}


def composition_metrics(rgb: np.ndarray, valid: np.ndarray, k: Dict[str, Any], facade: Sequence[float],
                        skyline_rng: Optional[Sequence[float]] = None,
                        landmark_box: Optional[Sequence[float]] = None) -> Dict[str, float]:
    """All 12.7 metric values on a working-size image `rgb` (0..1) with its valid mask."""
    L = luma(rgb)
    out: Dict[str, float] = {"sobel_mean": float(sobel_mag(L)[valid].mean()) if valid.any() else NAN}
    out.update(detail_variation(L, valid, k))
    out.update(palette(rgb, valid, k))
    out.update(repetition(L, valid, facade, k))
    out.update(blobs(L, valid, k))
    if landmark_box is not None:
        out.update(landmark_ring(L, valid, landmark_box))
    if skyline_rng is not None:
        out.update(skyline(L, skyline_rng, k))
    return out


# ---------------------------------------------------------------- 12.2 landmark ratio (id.png)
def class_mask(idx: np.ndarray, classes: Sequence[int]) -> np.ndarray:
    """Pixels whose rounded R value is in `classes`."""
    return np.isin(np.round(idx), list(classes))


def resize_ids(idx: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """Nearest-neighbour resample of a class array to `(w, h)` when it differs from the plate."""
    if (idx.shape[1], idx.shape[0]) == tuple(size):
        return idx
    return np.asarray(Image.fromarray(idx.astype(np.float32), "F").resize(size, Image.NEAREST))


def landmark_bbox(lm: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Inclusive `(x0, y0, x1, y1)` bounding box of a boolean mask, or None when empty."""
    ys, xs = np.nonzero(lm)
    if ys.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def landmark_stats(L: np.ndarray, idx: np.ndarray, c: Dict[str, Any]) -> Dict[str, Any]:
    """12.2 values: `landmark` (median luma of the landmark classes), `local_bg` (median luma of the background
    classes inside the box grown by `grow`), `ratio`, `landmark_share`. Missing parts are None."""
    lm = class_mask(idx, c["classes_landmark"])
    bb = landmark_bbox(lm)
    if bb is None:
        return {"landmark": None, "local_bg": None, "ratio": None, "landmark_share": 0.0}
    x0, y0, x1, y1 = bb
    gy, gx = int((y1 - y0) * c["grow"]), int((x1 - x0) * c["grow"])
    box = np.zeros_like(lm)
    box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
    bg = box & class_mask(idx, c["classes_background"])
    out: Dict[str, Any] = {"landmark": float(np.median(L[lm])), "local_bg": None, "ratio": None,
                           "landmark_share": float(lm.mean())}
    if bg.any():
        out["local_bg"] = float(np.median(L[bg]))
        out["ratio"] = out["landmark"] / max(1e-4, out["local_bg"])
    return out


def thumbnail(im: Image.Image, width: int) -> Image.Image:
    """Review thumbnail `width` wide (the 12.2 silhouette sheet; manual, no threshold)."""
    return im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)


def box_from_mask(lm: np.ndarray) -> Optional[List[float]]:
    """Normalised `[x0, y0, x1, y1]` of a boolean mask's bounding box (right and bottom edges exclusive)."""
    bb = landmark_bbox(lm)
    if bb is None:
        return None
    h, w = lm.shape
    return [bb[0] / w, bb[1] / h, (bb[2] + 1) / w, (bb[3] + 1) / h]


def is_nan(v: Any) -> bool:
    """True for None and NaN."""
    return v is None or (isinstance(v, float) and math.isnan(v))
