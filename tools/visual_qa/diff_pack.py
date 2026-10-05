"""Review-pack diff (ART-0 D, ported from art-pass W10) (ART_BIBLE §13 "Diff against the previous build").

    python tools/visual_qa/diff_pack.py <before> <after> <out> [--threshold 16] [--scale 0.5] [--format png|jpg]

For every PNG that exists at the same relative path in both packs (e.g.
1.0_mouse_re-off_none/combat_start.png) it writes <out>/<same path> as one image:
before | after | heatmap (changed pixels red over a dimmed grey of the after picture,
brighter where the change is bigger), labelled, plus <out>/diff_report.md with the
changed-pixel percentage of each pair, largest first, and the pictures only one pack has.

A pixel counts as changed when any channel differs by more than --threshold (default 16
of 255), so compression noise and anti-aliasing shimmer stay out. Needs Pillow. Run it as a
file; never `python -`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

LABEL_H = 28
## Pictures only one pack has are listed one by one up to this many, else counted per combo.
ONLY_LISTED = 60
BG = (18, 18, 24)
FG = (235, 235, 235)


def _font(size: int):
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def pngs(root: Path) -> set[str]:
    out = set()
    for p in root.rglob("*.png"):
        rel = p.relative_to(root).as_posix()
        if rel.split("/")[0] in ("sheets", "_runs", "diff"):
            continue
        out.add(rel)
    return out


def diff_pair(a: Image.Image, b: Image.Image, threshold: int) -> tuple[float, Image.Image]:
    """(changed %, heatmap) for two same-size RGB images."""
    d = ImageChops.difference(a, b)
    r, g, bl = d.split()
    mag = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    mask = mag.point(lambda v: 255 if v > threshold else 0)
    changed = mask.histogram()[255]
    pct = 100.0 * changed / (a.size[0] * a.size[1])
    base = b.convert("L").point(lambda v: v // 3).convert("RGB")
    strength = mag.point(lambda v: 0 if v <= threshold else min(255, 96 + v * 2))
    red = Image.new("RGB", a.size, (255, 40, 40))
    heat = Image.composite(red, base, strength)
    return pct, heat


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("out")
    ap.add_argument("--threshold", type=int, default=16)
    ap.add_argument("--scale", type=float, default=0.5, help="size of each panel (0.5 = 640x360)")
    ap.add_argument("--format", choices=["png", "jpg"], default="png")
    args = ap.parse_args()
    before, after, out = Path(args.before), Path(args.after), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pb, pa = pngs(before), pngs(after)
    both = sorted(pb & pa)
    font = _font(18)
    rows = []
    for rel in both:
        a = Image.open(before / rel).convert("RGB")
        b = Image.open(after / rel).convert("RGB")
        note = ""
        if a.size != b.size:
            note = "sizes differ (%dx%d vs %dx%d); after resized" % (a.size + b.size)
            b = b.resize(a.size, Image.LANCZOS)
        pct, heat = diff_pair(a, b, args.threshold)
        w, h = round(a.size[0] * args.scale), round(a.size[1] * args.scale)
        sheet = Image.new("RGB", (w * 3, h + LABEL_H), BG)
        d = ImageDraw.Draw(sheet)
        for i, (img, label) in enumerate(((a, "BEFORE"), (b, "AFTER"), (heat, "CHANGED %.2f%%" % pct))):
            sheet.paste(img.resize((w, h), Image.LANCZOS), (i * w, LABEL_H))
            d.text((i * w + 8, 4), label + ("  " + rel if i == 0 else ""), fill=FG, font=font)
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst = dst.with_name(dst.stem + "." + args.format)
        if args.format == "jpg":
            sheet.save(dst, quality=85, optimize=True)
        else:
            sheet.save(dst, optimize=True)
        rows.append((pct, rel, dst.relative_to(out).as_posix(), note))
    rows.sort(key=lambda r: (-r[0], r[1]))
    L = ["# Review-pack diff", "", "- before: `%s`" % before, "- after: `%s`" % after,
         "- changed pixel: any channel differs by more than %d/255" % args.threshold, "",
         "| changed % | picture | side by side | note |", "|---:|---|---|---|"]
    for pct, rel, img, note in rows:
        L.append("| %.2f | %s | [%s](%s) | %s |" % (pct, rel, img, img, note))
    only_b = sorted(pb - pa)
    only_a = sorted(pa - pb)
    for title, only in (("Only in before", only_b), ("Only in after", only_a)):
        if not only:
            continue
        L += ["", "## %s (%d)" % (title, len(only)), ""]
        if len(only) <= ONLY_LISTED:
            L += ["- %s" % r for r in only]
        else:
            # A subset pack against the full baseline: count per combo folder instead.
            per: dict[str, int] = {}
            for r in only:
                per[r.split("/")[0]] = per.get(r.split("/")[0], 0) + 1
            L += ["- %s: %d pictures" % (k, per[k]) for k in sorted(per)]
    (out / "diff_report.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    (out / "diff.json").write_text(json.dumps([{"changed_pct": round(p, 4), "picture": r, "image": i, "note": n}
                                               for p, r, i, n in rows], indent=1), encoding="utf-8")
    print("diff_pack: %d pairs, %d only before, %d only after -> %s" % (len(rows), len(only_b), len(only_a), out / "diff_report.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
