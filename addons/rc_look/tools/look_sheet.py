"""LOOK-TOOLBOX module 3: the one-command reference sheet for any rc_look module.

Columns: reference (golden plate or concept) | twin (optional) | Godot, each optionally cropped to the same region,
scaled to a common height, with a labelled header. When the reference and Godot crops have the same size, a fourth
column shows the absolute difference x4. Numbers per image (values.json): median luma, share under 0.10 and over 0.85
(sRGB luma), and the mean hue / saturation of the brightest 5 % (the emissive read). `read` stays empty: numbers alone
never pass, every sheet also gets an ART_BIBLE §1.2 read written by the reviewer (A-020).

    python addons/rc_look/tools/look_sheet.py --module pencil --name aim_arc \
        --ref <png> [--ref-crop x0,y0,x1,y1] [--twin <png>] [--twin-crop ...] --godot <png> [--godot-crop ...] \
        [--height 540] [--out D:/rc_scratch/look_parity]

Writes <out>/<module>_<git sha>/<name>_sheet.png and <name>_values.json, and prints the sheet path.
"""
import argparse
import colorsys
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HEADER_PX = 30
GAP_PX = 8
BG = (16, 16, 20)
LABEL = {"ref": (255, 226, 0), "twin": (176, 77, 255), "godot": (92, 225, 255), "diff": (255, 68, 51)}
TOP_SHARE = 0.05
DIFF_GAIN = 4


def _crop(path, box):
    im = Image.open(path).convert("RGB")
    if box:
        im = im.crop(tuple(int(v) for v in box.split(",")))
    return im


def _numbers(im):
    px = list(im.getdata())
    lum = sorted((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0 for r, g, b in px)
    n = len(lum)
    by_lum = sorted(px, key=lambda p: 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2])
    top = by_lum[int(n * (1.0 - TOP_SHARE)):]
    hs = [colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0) for r, g, b in top]
    return {
        "size": list(im.size),
        "median_luma": round(lum[n // 2], 4),
        "under_010": round(sum(1 for v in lum if v < 0.10) / n, 4),
        "over_085": round(sum(1 for v in lum if v > 0.85) / n, 4),
        "top5_hue": round(sum(h for h, _, _ in hs) / max(len(hs), 1), 4),
        "top5_sat": round(sum(s for _, s, _ in hs) / max(len(hs), 1), 4),
    }


def _sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "nogit"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--module", required=True)
    ap.add_argument("--name", default="sheet")
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref-crop")
    ap.add_argument("--twin")
    ap.add_argument("--twin-crop")
    ap.add_argument("--godot", required=True)
    ap.add_argument("--godot-crop")
    ap.add_argument("--height", type=int, default=540)
    ap.add_argument("--out", default="D:/rc_scratch/look_parity")
    a = ap.parse_args()

    cols = [("ref", _crop(a.ref, a.ref_crop), a.ref)]
    if a.twin:
        cols.append(("twin", _crop(a.twin, a.twin_crop), a.twin))
    cols.append(("godot", _crop(a.godot, a.godot_crop), a.godot))
    values = {"module": a.module, "name": a.name, "sha": _sha(), "read": "", "images": {}}
    for key, im, path in cols:
        values["images"][key] = {"path": path, **_numbers(im)}
    if cols[0][1].size == cols[-1][1].size:
        d = ImageChops.difference(cols[0][1], cols[-1][1]).point(lambda v: min(255, v * DIFF_GAIN))
        cols.append(("diff", d, "abs diff x%d" % DIFF_GAIN))
    tiles = []
    for key, im, path in cols:
        w = round(im.width * a.height / im.height)
        tiles.append((key, im.resize((w, a.height), Image.LANCZOS), path))
    width = sum(t[1].width for t in tiles) + GAP_PX * (len(tiles) + 1)
    sheet = Image.new("RGB", (width, a.height + HEADER_PX + GAP_PX), BG)
    draw = ImageDraw.Draw(sheet)
    x = GAP_PX
    for key, im, path in tiles:
        sheet.paste(im, (x, HEADER_PX))
        draw.text((x, 8), "%s  %s" % (key.upper(), Path(str(path)).name), fill=LABEL[key])
        x += im.width + GAP_PX
    out = Path(a.out) / ("%s_%s" % (a.module, values["sha"]))
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / ("%s_sheet.png" % a.name))
    (out / ("%s_values.json" % a.name)).write_text(json.dumps(values, indent=1))
    print(out / ("%s_sheet.png" % a.name))


if __name__ == "__main__":
    main()
