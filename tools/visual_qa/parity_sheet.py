"""Art-pass parity sheets (M14 parity audit, designer ruling 2026-10-05 "main looks just like art pass").

    python tools/visual_qa/parity_sheet.py --art <art pass pack combo dir> --main <main pack combo dir>
        --concepts <art-pass copy>/docs/concepts --pairs tools/visual_qa/parity_pairs.json
        --out docs/art_review/PARITY [--only a,b]

For every pair in the pairs file it writes <out>/<sheet>.jpg: the references on the left (the art
pass build's picture and/or the locked concept image), main on the right, labelled, with every
difference's rectangle marked by its id; and per difference <out>/<id>.jpg: the same 1280x720
rectangle cut from every picture, side by side, with its note (one sheet per id, so the designer
can rule on each one alone).

A reference is "<screen>" (a picture of the art pass review pack, same screen names as its
tools/visual_qa/review_pack.gd), "concept:<path under docs/concepts>" (tag art-concepts-r43) or
"file:<abs path>" (e.g. a lab frame). "main" is a screen of main's pack, or "file:<abs path>".
Every picture is fitted (letterboxed) into 1280x720 first, so one crop rectangle cuts the same
place from all of them (both review packs lay out at 1280x720; the concepts are 16:9).

Pairs file: {"pairs": [{"sheet": "title", "refs": ["title", "concept:round33_ui_chrome/title_screen.png"],
    "main": "title", "crops": [{"id": "TITLE-01", "rect": [x, y, w, h], "note": "..."}]}]}

Needs Pillow. Run it as a file; never `python -`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FRAME = (1280, 720)
## Width of the whole sheet; the top row splits it between the pictures.
SHEET_W = 1440
GAP = 8
LABEL_H = 26
## Largest blow-up of a crop.
CROP_MAX_SCALE = 1.5
JPEG_QUALITY = 55
BG = (18, 18, 24)
FG = (235, 235, 235)
REF_TAG = (255, 200, 60)
MAIN_TAG = (80, 200, 255)
MARK = (255, 60, 200)
MISSING = (60, 20, 30)


def _font(size: int):
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Letterboxes img into size (keeps its aspect)."""
    img = img.convert("RGB")
    s = min(size[0] / img.width, size[1] / img.height)
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    out = Image.new("RGB", size, BG)
    out.paste(img.resize((w, h), Image.LANCZOS), ((size[0] - w) // 2, (size[1] - h) // 2))
    return out


def _load(path: Path | None, label: str) -> Image.Image:
    if path is None or not path.exists():
        img = Image.new("RGB", FRAME, MISSING)
        ImageDraw.Draw(img).text((40, 340), "NO PICTURE: %s" % label, fill=FG, font=_font(36))
        return img
    img = Image.open(path)
    if img.size != FRAME:
        return _fit(img, FRAME)
    return img.convert("RGB")


## Main screen name -> the art pass pack's own name, for screens the art pass names with a word
## main has since renamed (filled from --art-rename; the pairs file uses main's names).
ART_RENAMES: dict[str, str] = {}


def _resolve(name: str, pack: Path, concepts: Path | None, renames: dict | None = None) -> Path | None:
    if not name:
        return None
    if name.startswith("concept:"):
        return (concepts / name[len("concept:"):]) if concepts else None
    if name.startswith("file:"):
        return Path(name[len("file:"):])
    return pack / ((renames or {}).get(name, name) + ".png")


def _short(name: str) -> str:
    if name.startswith("concept:"):
        return "CONCEPT " + name[len("concept:"):]
    if name.startswith("file:"):
        return Path(name[len("file:"):]).name
    return "ART PASS BUILD " + name


def build(pair: dict, art_dir: Path, main_dir: Path, concepts: Path | None, out: Path) -> Path:
    refs = pair.get("refs", [])
    main_name = pair.get("main", "")
    pics = [(_short(r), REF_TAG, _load(_resolve(r, art_dir, concepts, ART_RENAMES), r)) for r in refs]
    pics.append(("MAIN " + main_name.replace("file:", ""), MAIN_TAG, _load(_resolve(main_name, main_dir, None), main_name)))
    n = len(pics)
    cell_w = (SHEET_W - GAP * (n - 1)) // n
    cell = (cell_w, round(cell_w * FRAME[1] / FRAME[0]))
    k = cell[0] / FRAME[0]
    font = _font(17)
    small = _font(16)
    crops = pair.get("crops", [])
    rows = []
    for c in crops:
        x, y, w, h = c["rect"]
        s = min(CROP_MAX_SCALE, cell_w / w)
        size = (max(1, round(w * s)), max(1, round(h * s)))
        rows.append(([p[2].crop((x, y, x + w, y + h)).resize(size, Image.LANCZOS) for p in pics], c))
    out.mkdir(parents=True, exist_ok=True)
    # The screen sheet: the full pictures side by side, each difference's rectangle marked with its id.
    sheet = Image.new("RGB", (SHEET_W, LABEL_H + cell[1]), BG)
    d = ImageDraw.Draw(sheet)
    for i, (label, tag, img) in enumerate(pics):
        x0 = i * (cell[0] + GAP)
        d.text((x0 + 4, 4), label[:60], fill=tag, font=font)
        small_img = img.resize(cell, Image.LANCZOS)
        sd = ImageDraw.Draw(small_img)
        for j, (_c, c) in enumerate(rows):
            x, y, w, h = c["rect"]
            sd.rectangle((x * k, y * k, (x + w) * k, (y + h) * k), outline=MARK, width=2)
            sd.text((x * k + 3, y * k + 2), c.get("id", str(j + 1)), fill=MARK, font=small)
        sheet.paste(small_img, (x0, LABEL_H))
    path = out / (pair["sheet"] + ".jpg")
    sheet.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    # One crop sheet per difference id: the same rectangle from every picture, side by side.
    for j, (imgs, c) in enumerate(rows):
        cid = c.get("id", "%s-%02d" % (pair["sheet"], j + 1))
        cw = sum(im.width for im in imgs) + GAP * (len(imgs) - 1)
        crop_sheet = Image.new("RGB", (max(cw, 640), LABEL_H * 2 + imgs[0].height), BG)
        cd = ImageDraw.Draw(crop_sheet)
        cd.text((6, 4), "%s  %s" % (cid, c.get("note", ""))[:150], fill=FG, font=small)
        xx = 0
        for (label, tag, _img), im in zip(pics, imgs):
            cd.text((xx + 4, LABEL_H + 2), label[:40], fill=tag, font=small)
            crop_sheet.paste(im, (xx, LABEL_H * 2))
            xx += im.width + GAP
        crop_sheet.save(out / (cid + ".jpg"), "JPEG", quality=JPEG_QUALITY, optimize=True)
    return path


## Motion strips: frames picked from a motion lab Movie Maker run (--demo-anim=<id>, 30 fps).
MOTION_START = 6
MOTION_FPS = 30
MOTION_COUNT = 8
MOTION_STEP = 4
## The lab's stage (right of its 380 px control column), in 1280x720.
MOTION_CROP = (380, 0, 900, 720)
MOTION_CELL_W = 200


def motion(art_root: Path, main_root: Path, demo: str, out: Path, sheet_id: str) -> Path:
    """One strip pair: the art pass's frames of `demo` on the top row, main's under it,
    MOTION_COUNT frames every MOTION_STEP from MOTION_START, labelled in ms."""
    small = _font(15)
    x, y, w, h = MOTION_CROP
    cell = (MOTION_CELL_W, round(MOTION_CELL_W * h / w))
    rows = []
    for label, tag, root in (("ART PASS BUILD", REF_TAG, art_root), ("MAIN", MAIN_TAG, main_root)):
        frames = sorted((root / demo).glob("f*.png"))
        row = []
        for i in range(MOTION_COUNT):
            k = MOTION_START + i * MOTION_STEP
            img = _load(frames[k] if k < len(frames) else None, "%s f%d" % (demo, k))
            row.append((round((k - MOTION_START) * 1000 / MOTION_FPS), img.crop((x, y, x + w, y + h)).resize(cell, Image.LANCZOS)))
        rows.append((label, tag, row))
    width = MOTION_COUNT * (cell[0] + GAP)
    sheet = Image.new("RGB", (width, LABEL_H + 2 * (LABEL_H + cell[1] + GAP)), BG)
    d = ImageDraw.Draw(sheet)
    d.text((6, 4), "%s  motion lab --demo-anim=%s (30 fps, from its start frame)" % (sheet_id, demo), fill=FG, font=small)
    yy = LABEL_H
    for label, tag, row in rows:
        d.text((6, yy + 4), label, fill=tag, font=small)
        yy += LABEL_H
        for i, (ms, im) in enumerate(row):
            sheet.paste(im, (i * (cell[0] + GAP), yy))
            d.text((i * (cell[0] + GAP) + 4, yy + 2), "%d ms" % ms, fill=MARK, font=small)
        yy += cell[1] + GAP
    out.mkdir(parents=True, exist_ok=True)
    path = out / (sheet_id + ".jpg")
    sheet.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--art", required=True, help="art pass pack combo folder (its <screen>.png files)")
    ap.add_argument("--main", required=True, help="main pack combo folder")
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--concepts", default="", help="docs/concepts of tag art-concepts-r43 (e.g. the art-pass copy's)")
    ap.add_argument("--only", default="", help="comma list of sheet names")
    ap.add_argument("--motion", default="", help="id=demo,... : motion strip pairs from --art / --main "
                    "folders holding one Movie Maker folder per demo (the pairs file is then ignored)")
    ap.add_argument("--art-rename", default="", help="main=art,... : screens the art pass pack names "
                    "differently (e.g. the shop screens, renamed on main)")
    args = ap.parse_args()
    for item in filter(None, args.art_rename.split(",")):
        k, v = item.split("=")
        ART_RENAMES[k.strip()] = v.strip()
    if args.motion:
        for item in args.motion.split(","):
            sheet_id, demo = item.split("=")
            print(motion(Path(args.art), Path(args.main), demo, Path(args.out), sheet_id))
        return 0
    pairs = json.loads(Path(args.pairs).read_text(encoding="utf-8"))["pairs"]
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    concepts = Path(args.concepts) if args.concepts else None
    count = 0
    for p in pairs:
        if only and p["sheet"] not in only:
            continue
        print(build(p, Path(args.art), Path(args.main), concepts, Path(args.out)))
        count += 1
    print("parity_sheet: %d sheets" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
