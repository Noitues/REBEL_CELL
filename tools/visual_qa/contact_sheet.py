"""Contact sheets for a review pack (ART-0 D, ported from art-pass W10; ART_BIBLE §13).

    python tools/visual_qa/contact_sheet.py <pack> [--out <dir>] [--thumb 400] [--cols 4]
        [--format jpg|png] [--combos a,b] [--screens a,b] [--screen-cols input,re]

Reads <pack>/manifest.json (written by capture_pack.py; a folder of <combo>/<screen>.png
without one works too) and writes, into <out> (default <pack>/sheets):

- combo_<combo>.<ext>: every screen of one axis combo, labelled, in capture order;
- screen_<screen>.<ext>: one screen, a row per text scale, a column per input and
  reduce-effects setting (filter none, settings off; --screen-cols input,re,filter,setting
  adds the filters and the accessibility settings).

Thumbnails are at least 400 px wide. Failed screens show as a labelled grey tile with
the reason. Needs Pillow. Run it as a file; never `python -`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pack_axes  # noqa: E402

MIN_THUMB = 400
LABEL_H = 26
GAP = 8
BG = (18, 18, 24)
FG = (235, 235, 235)
WARN = (255, 170, 60)
MISSING = (60, 60, 70)


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _thumb(path: Path | None, w: int, h: int, reason: str, font) -> Image.Image:
    if path is not None and path.exists():
        return Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    tile = Image.new("RGB", (w, h), MISSING)
    ImageDraw.Draw(tile).multiline_text((10, 10), "MISSING\n" + _wrap(reason or "not captured", 44), fill=WARN, font=font)
    return tile


def _wrap(text: str, cols: int) -> str:
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > cols:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    out.append(line)
    return "\n".join(out[:6])


def grid(cells: list[tuple[str, Path | None, str, bool]], cols: int, thumb_w: int, title: str,
         row_labels: list[str] | None = None) -> Image.Image:
    """cells: (label, png or None, missing reason, warn). Returns the sheet."""
    thumb_w = max(thumb_w, MIN_THUMB)
    thumb_h = round(thumb_w * pack_axes.HEIGHT / pack_axes.WIDTH)
    font = _font(15)
    tfont = _font(22)
    rows = (len(cells) + cols - 1) // cols
    left = 90 if row_labels else 0
    head = 44
    w = left + cols * (thumb_w + GAP) + GAP
    h = head + rows * (thumb_h + LABEL_H + GAP) + GAP
    sheet = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(sheet)
    d.text((GAP, 10), title, fill=FG, font=tfont)
    for i, (label, path, reason, warn) in enumerate(cells):
        r, c = divmod(i, cols)
        x = left + GAP + c * (thumb_w + GAP)
        y = head + r * (thumb_h + LABEL_H + GAP)
        d.text((x + 2, y + 4), label, fill=WARN if warn else FG, font=font)
        sheet.paste(_thumb(path, thumb_w, thumb_h, reason, font), (x, y + LABEL_H))
    if row_labels:
        for r, lab in enumerate(row_labels):
            y = head + r * (thumb_h + LABEL_H + GAP) + LABEL_H + thumb_h // 2
            d.text((GAP, y), lab, fill=FG, font=tfont)
    return sheet


def save(img: Image.Image, path: Path, fmt: str) -> Path:
    path = path.with_name(path.name + "." + fmt)  # combo names hold dots (1.0_...)
    if fmt == "jpg":
        img.save(path, quality=85, optimize=True)
    else:
        img.save(path, optimize=True)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--out")
    ap.add_argument("--thumb", type=int, default=MIN_THUMB)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--format", choices=["jpg", "png"], default="jpg")
    ap.add_argument("--combos", help="only these combo folders (comma list)")
    ap.add_argument("--screens", help="only these screens (comma list)")
    ap.add_argument("--screen-cols", default="input,re", help="axes that make the columns of a per-screen sheet")
    ap.add_argument("--no-combo", action="store_true", help="skip the per-combo sheets")
    ap.add_argument("--no-screen", action="store_true", help="skip the per-screen sheets")
    args = ap.parse_args()
    pack = Path(args.pack)
    out = Path(args.out) if args.out else pack / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    entries = pack_axes.load_entries(pack)
    if args.combos:
        keep = set(args.combos.split(","))
        entries = [e for e in entries if e["combo"] in keep]
    if args.screens:
        keep = set(args.screens.split(","))
        entries = [e for e in entries if e["screen"] in keep]
    order = pack_axes.screen_order(entries)
    written = 0
    if not args.no_combo:
        combos = sorted({e["combo"] for e in entries}, key=pack_axes.combo_sort_key)
        for combo in combos:
            by = {e["screen"]: e for e in entries if e["combo"] == combo}
            cells = []
            for s in order:
                e = by.get(s)
                if e is None:
                    continue
                warn = bool(e.get("warnings")) or e.get("status") != "ok"
                cells.append((s + (" !" if warn else ""), pack_axes.png_of(pack, e), e.get("error", ""), warn))
            save(grid(cells, args.cols, args.thumb, "combo " + combo), out / ("combo_" + combo), args.format)
            written += 1
    if not args.no_screen:
        col_axes = [a.strip() for a in args.screen_cols.split(",") if a.strip()]
        for s in order:
            es = [e for e in entries if e["screen"] == s]
            if "filter" not in col_axes:
                es = [e for e in es if e["axes"]["filter"] == "none"] or es
            if "setting" not in col_axes:
                es = [e for e in es if e["axes"].get("setting", "off") == "off"] or es
            scales = sorted({e["axes"]["scale"] for e in es}, key=float)
            cols_keys = sorted({tuple(e["axes"].get(a, "off") for a in col_axes) for e in es})
            if not cols_keys or not scales:
                continue
            index = {(e["axes"]["scale"], tuple(e["axes"].get(a, "off") for a in col_axes)): e for e in es}
            cells = []
            for sc in scales:
                for ck in cols_keys:
                    e = index.get((sc, ck))
                    label = " ".join(pack_axes.axis_word(a, v) for a, v in zip(col_axes, ck))
                    if e is None:
                        cells.append((label, None, "not in pack", True))
                    else:
                        warn = bool(e.get("warnings")) or e.get("status") != "ok"
                        cells.append((label, pack_axes.png_of(pack, e), e.get("error", ""), warn))
            sheet = grid(cells, len(cols_keys), args.thumb, "screen " + s + " (rows: text scale)", ["x" + sc for sc in scales])
            save(sheet, out / ("screen_" + s), args.format)
            written += 1
    print("contact_sheet: %d sheets in %s" % (written, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
