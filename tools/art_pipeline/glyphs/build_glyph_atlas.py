"""ART-1 1C: build the production glyph atlas (bible 3.5, 5.2, 6.2; plan 5.3).

The masters are regenerated from the concept generator scripts (PIL, 512 box, 4x supersampled for the round 34
Firmware/Daemon set) rather than read from the 256 px round 17 PNGs, so the distance field is computed from a
4x master. Output:
  assets/glyphs/glyph_atlas.png           single-channel signed distance field, 128 px cells, manifest order
  assets/glyphs/glyph_atlas_manifest.json names, cell geometry, source tag, per-glyph source ids, twin scores
  assets/glyphs/masters/<name>.png        256 px white-on-transparent copy of every glyph (program names)

Usage (the generator scripts live on tag art-concepts-r43; extract them to a scratch folder first):
  git archive -o <tmp>/src.tar art-concepts-r43 docs/concepts/round40_hub_inner_ring/scripts \
      docs/concepts/round18_corp_wheels/scripts docs/concepts/round34_firmware_daemons/scripts
  tar xf <tmp>/src.tar -C <tmp>/src
  python tools/art_pipeline/glyphs/build_glyph_atlas.py --src <tmp>/src [--check-ref]

--check-ref compares every round 17 master with docs/art_reference/glyphs/<old name>.png (IoU at 256 px).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import glyph_manifest as GM  # noqa: E402

SOURCE_TAG = "art-concepts-r43"
MASTER = 512          # master box (px)
CELL = 128            # atlas cell (px)
BOX = 96              # glyph box inside a cell (px); the rest is room for the outline + AA
SPREAD = 16           # distance range each side of the edge (cell px)
COLUMNS = 16
TWIN_PX = 16          # bible 5.2
SCRIPT_DIRS = {
    "r40": "docs/concepts/round40_hub_inner_ring/scripts",
    "priority": "docs/concepts/round18_corp_wheels/scripts",
    "fw": "docs/concepts/round34_firmware_daemons/scripts",
}
REF_NAMES = {  # atlas name -> round 17 file in docs/art_reference/glyphs (for --check-ref)
    "slice_shim": "slice_exploit", "slice_overflow": "slice_zero_day", "slice_defrag": "slice_firewall",
    "slice_sandbox": "slice_sandbox", "slice_detour": "slice_proxy", "slice_hotfix": "slice_patch",
    "slice_infect": "slice_virus", "slice_trojan": "slice_trojan", "slice_null": "slice_null",
    "special_citation": "special_citation", "special_solar_flare": "special_solar_flare",
    "special_dose": "special_dose", "special_weight": "special_weight", "special_drone": "special_drone",
    "exploit_intel": "placeholder_recon", "exploit_breach": "placeholder_key",
}


# ------------------------------------------------------------------ phase 1: masters (one subprocess per source)
def dump(family, src, tmp):
    sdir = os.path.join(src, SCRIPT_DIRS[family])
    sys.path.insert(0, sdir)
    os.chdir(sdir)
    rows = [r for r in GM.ROWS if r[1] == family]
    if family == "r40":
        import slicelib as SL
        import glyphs40 as G
        get = lambda gid: SL.glyph_mask(G.resolve(gid))
    elif family == "priority":
        import glyph_priority as GP
        get = lambda gid: GP.priority()
    else:
        import fwlib as FW
        get = lambda gid: FW.icon(gid, MASTER)
    for name, _fam, gid, _meaning in rows:
        m = get(gid)
        if m is None:
            raise SystemExit("no master for %s (%s)" % (name, gid))
        m = m.convert("L")
        if m.size != (MASTER, MASTER):
            m = m.resize((MASTER, MASTER), Image.LANCZOS)
        m.save(os.path.join(tmp, name + ".png"))
    print("dumped", family, len(rows), flush=True)


def pending_master():
    m = Image.new("L", (MASTER, MASTER), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([88, 88, 424, 424], radius=72, fill=255)
    d.rounded_rectangle([152, 152, 360, 360], radius=36, fill=0)
    return m


# ------------------------------------------------------------------ phase 2: distance field
def edge_points(m):
    """Sub-pixel points where the coverage crosses 0.5 (master px, pixel centres at +0.5)."""
    m = np.pad(m, 1)
    pts = []
    for axis in (1, 0):
        a = m[:, :-1] if axis == 1 else m[:-1, :]
        b = m[:, 1:] if axis == 1 else m[1:, :]
        cross = (a - 0.5) * (b - 0.5) < 0
        ys, xs = np.nonzero(cross)
        t = (0.5 - a[ys, xs]) / (b[ys, xs] - a[ys, xs])
        if axis == 1:
            pts.append(np.stack([xs + t + 0.5, ys + 0.5], 1))
        else:
            pts.append(np.stack([xs + 0.5, ys + t + 0.5], 1))
    p = np.concatenate(pts, 0) - 1.0  # undo the pad
    return p.astype(np.float32)


def sdf_cell(mask):
    m = np.asarray(mask, np.float32) / 255.0
    scale = BOX / MASTER
    off = (CELL - BOX) / 2.0
    p = edge_points(m) * scale + off
    g = (np.arange(CELL, dtype=np.float32) + 0.5)
    gx, gy = np.meshgrid(g, g)
    q = np.stack([gx.ravel(), gy.ravel()], 1)
    best = np.full(q.shape[0], 1e9, np.float32)
    for i in range(0, q.shape[0], 2048):
        qq = q[i:i + 2048]
        for j in range(0, p.shape[0], 4096):
            pp = p[j:j + 4096]
            d2 = (qq[:, None, 0] - pp[None, :, 0]) ** 2 + (qq[:, None, 1] - pp[None, :, 1]) ** 2
            best[i:i + 2048] = np.minimum(best[i:i + 2048], d2.min(1))
    dist = np.sqrt(best).reshape(CELL, CELL)
    # inside test: bilinear coverage of the master at the cell pixel centre
    mx = (gx - off) / scale - 0.5
    my = (gy - off) / scale - 0.5
    x0 = np.clip(np.floor(mx).astype(int), 0, MASTER - 2)
    y0 = np.clip(np.floor(my).astype(int), 0, MASTER - 2)
    fx = np.clip(mx - x0, 0, 1)
    fy = np.clip(my - y0, 0, 1)
    c = (m[y0, x0] * (1 - fx) * (1 - fy) + m[y0, x0 + 1] * fx * (1 - fy)
         + m[y0 + 1, x0] * (1 - fx) * fy + m[y0 + 1, x0 + 1] * fx * fy)
    outside_box = (mx < 0) | (my < 0) | (mx > MASTER - 1) | (my > MASTER - 1)
    inside = (c >= 0.5) & ~outside_box
    signed = np.where(inside, dist, -dist)
    v = np.clip(0.5 + signed / (2.0 * SPREAD), 0.0, 1.0)
    return (v * 255.0 + 0.5).astype(np.uint8)


def cov16(mask):
    """The round 17 catalogue's 16 px coverage map (glyph_catalog.cov)."""
    m = mask.resize((TWIN_PX, TWIN_PX), Image.BOX).filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(m, np.float32) / 255.0


def soft_iou(a, b):
    return float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum()))


def git_sha(tag):
    try:
        return subprocess.check_output(["git", "rev-list", "-n", "1", tag], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        return ""


def build(src, out, tmp, check_ref):
    os.makedirs(tmp, exist_ok=True)
    for fam in ("r40", "priority", "fw"):
        subprocess.check_call([sys.executable, os.path.abspath(__file__), "--dump", fam, "--src", src, "--tmp", tmp])
    pending_master().save(os.path.join(tmp, "pending.png"))
    masters = {n: Image.open(os.path.join(tmp, n + ".png")).convert("L") for n in GM.NAMES}
    if len(set(GM.NAMES)) != len(GM.NAMES):
        raise SystemExit("duplicate atlas names")
    rows = int(math.ceil(len(GM.NAMES) / COLUMNS))
    atlas = np.zeros((rows * CELL, COLUMNS * CELL), np.uint8)
    os.makedirs(os.path.join(out, "masters"), exist_ok=True)
    for i, name in enumerate(GM.NAMES):
        cx, cy = (i % COLUMNS) * CELL, (i // COLUMNS) * CELL
        atlas[cy:cy + CELL, cx:cx + CELL] = sdf_cell(masters[name])
        im = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
        im.putalpha(masters[name].resize((256, 256), Image.LANCZOS))
        im.save(os.path.join(out, "masters", name + ".png"), optimize=True)
        print("cell", i, name, flush=True)
    Image.fromarray(atlas, "L").save(os.path.join(out, "glyph_atlas.png"), optimize=True)
    # 16 px twin scores over the whole atlas (pending excluded), the closest pairs kept for the record
    names = [n for n in GM.NAMES if n != "pending"]
    covs = {n: cov16(masters[n]) for n in names}
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pairs.append((round(soft_iou(covs[names[i]], covs[names[j]]), 3), names[i], names[j]))
    pairs.sort(reverse=True)
    ref = {}
    if check_ref:
        for name, old in REF_NAMES.items():
            p = os.path.join(ROOT, "docs", "art_reference", "glyphs", old + ".png")
            a = np.asarray(Image.open(p).getchannel("A"), np.float32) / 255.0
            b = np.asarray(masters[name].resize((256, 256), Image.LANCZOS), np.float32) / 255.0
            ref[name] = round(float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum())), 4)
        for r in GM.ROWS:
            if r[1] == "r40" and r[0].split("_")[0] in ("status", "state", "picto"):
                old = r[0]
                p = os.path.join(ROOT, "docs", "art_reference", "glyphs", old + ".png")
                if os.path.exists(p):
                    a = np.asarray(Image.open(p).getchannel("A"), np.float32) / 255.0
                    b = np.asarray(masters[old].resize((256, 256), Image.LANCZOS), np.float32) / 255.0
                    ref[old] = round(float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum())), 4)
        p = os.path.join(ROOT, "docs", "art_reference", "glyphs", "round18_corp_wheels", "special_priority.png")
        a = np.asarray(Image.open(p).getchannel("A"), np.float32) / 255.0
        b = np.asarray(masters["special_priority"].resize((256, 256), Image.LANCZOS), np.float32) / 255.0
        ref["special_priority"] = round(float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum())), 4)
    manifest = {
        "source_tag": SOURCE_TAG, "source_commit": git_sha(SOURCE_TAG),
        "script": "tools/art_pipeline/glyphs/build_glyph_atlas.py",
        "master_px": MASTER, "cell_px": CELL, "box_px": BOX, "spread_px": SPREAD, "columns": COLUMNS,
        "encoding": "L8: 0.5 + signed_distance / (2 * spread_px), inside positive, cell px",
        "glyphs": [{"name": r[0], "source": r[1], "source_id": r[2], "meaning": r[3]} for r in GM.ROWS],
        "twin_px": TWIN_PX, "closest_pairs": [list(p) for p in pairs[:24]],
        "reference_iou_256": ref,
    }
    with open(os.path.join(out, "glyph_atlas_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    print("atlas", atlas.shape, "glyphs", len(GM.NAMES))
    print("closest 16 px pairs:")
    for p in pairs[:16]:
        print("  %.3f %s / %s" % p)
    if ref:
        print("lowest reference IoU:", sorted(ref.items(), key=lambda kv: kv[1])[:6])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "glyphs"))
    ap.add_argument("--tmp", default=os.path.join(os.environ.get("TEMP", "/tmp"), "glyph_masters"))
    ap.add_argument("--dump", default="")
    ap.add_argument("--check-ref", action="store_true")
    a = ap.parse_args()
    if a.dump:
        dump(a.dump, os.path.abspath(a.src), os.path.abspath(a.tmp))
    else:
        build(os.path.abspath(a.src), os.path.abspath(a.out), os.path.abspath(a.tmp), a.check_ref)
