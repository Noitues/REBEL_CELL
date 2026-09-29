"""W10 runtime visual lint report (ART_BIBLE §13 "Lint", §3.7, §4.2-4.3).

    python tools/visual_qa/lint_report.py <pack> [--detail-cap 12]

Reads each captured screen's <combo>/<screen>.lint.json (the visible text Controls the
harness exported after layout settled) and its PNG, and writes

    <pack>/<combo>/lint.json   findings per screen of that combo
    <pack>/lint.json           every finding, all combos
    <pack>/lint_report.md      summary and details

Rules:
  a  font      effective size under 12 x text_scale (on screen, after any Control scale),
               or a font_size override that is not a §4.2 step x text_scale
  b  overlap   the text areas of two visible text Controls intersect (ancestors and
               descendants excluded)
  c  clipped   ellipsis overrun that doesn't fit, fewer visible lines than lines outside a
               ScrollContainer, clip_text that cuts, or text holding "…"
  d  contrast  font colour against the background estimated from the PNG (median of a
               ring of pixels just outside the text area) under 4.5:1 (3:1 at >= 24 px);
               "measured" is the strongest glyph pixel inside, for a second opinion
  e  custom    Controls whose script draws its own text (draw_string): the tree walk can't
               lint those; they are listed per screen

A report, not a CI gate: it needs a renderer. Only unfiltered pictures are linted (the
grey and deutan pictures share the same layout). Run it as a file; never `python -`.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pack_axes  # noqa: E402

FLOOR = 12
STEPS = (12, 15, 18, 22, 30, 44)
HERO = (64, 96)
BODY_MIN = 4.5
LARGE_MIN = 3.0
LARGE_PX = 24
RING = 4
MIN_OVERLAP = 3.0
MIN_ALPHA = 0.05
RULES = ("font", "overlap", "clipped", "contrast")
## Strongest glyph-to-background contrast under which a text Control counts as not in the
## picture (covered by a modal).
HIDDEN_BELOW = 1.25


def _lum(c) -> float:
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _clamp_box(r, w, h):
    x0, y0 = max(0, int(r[0])), max(0, int(r[1]))
    x1, y1 = min(w, int(r[0] + r[2] + 0.999)), min(h, int(r[1] + r[3] + 0.999))
    return x0, y0, x1, y1


def background(img: Image.Image, ink) -> tuple | None:
    w, h = img.size
    x0, y0, x1, y1 = _clamp_box(ink, w, h)
    if x1 <= x0 or y1 <= y0:
        return None
    px = img.load()
    ring = []
    for x in range(max(0, x0 - RING), min(w, x1 + RING)):
        for y in list(range(max(0, y0 - RING), y0)) + list(range(y1, min(h, y1 + RING))):
            ring.append(px[x, y])
    for y in range(y0, y1):
        for x in list(range(max(0, x0 - RING), x0)) + list(range(x1, min(w, x1 + RING))):
            ring.append(px[x, y])
    if not ring:
        return None
    return tuple(int(statistics.median(p[i] for p in ring)) for i in range(3))


def strongest(img: Image.Image, ink, bg) -> float:
    w, h = img.size
    x0, y0, x1, y1 = _clamp_box(ink, w, h)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    crop = img.crop((x0, y0, x1, y1))
    colours = crop.getcolors(max(1, crop.size[0] * crop.size[1]))
    best = 1.0
    for _n, c in colours or []:
        best = max(best, ratio(c, bg))
    return best


def _short(path: str) -> str:
    """The node path's last two names (parent/name): enough to find it in the view."""
    return "/".join(path.split("/")[-2:])


def derived_sizes(ts: float) -> set[int]:
    out = {round(s * ts) for s in STEPS}
    out |= set(range(round(HERO[0] * ts), round(HERO[1] * ts) + 1))
    return out


def lint_screen(data: dict, png: Path) -> dict:
    ts = float(data.get("text_scale", 1.0))
    floor = round(FLOOR * ts)  # the caption step as UiTheme rounds it (19 at 1.6)
    img = Image.open(png).convert("RGB") if png.exists() else None
    ok_sizes = derived_sizes(ts)
    items = [c for c in data.get("controls", [])
             if c.get("alpha", 1.0) >= MIN_ALPHA and c["color"][3] >= MIN_ALPHA and not c.get("self_draws")]
    found = {r: [] for r in RULES}
    hidden = []
    if img is not None:
        # Text with no glyph pixel standing out of its surroundings isn't in the picture:
        # a modal covers it (the walk can't see occlusion). It is left out of every rule.
        seen = []
        for c in items:
            bg = background(img, c["ink"])
            if bg is not None and strongest(img, c["ink"], bg) < HIDDEN_BELOW:
                hidden.append({"path": c["path"], "text": c["text"][:60]})
            else:
                seen.append(c)
        items = seen
    for c in items:
        where = {"path": c["path"], "text": c["text"][:60], "owner": c.get("owner_script", "")}
        px = min(float(c["font_px"]), float(c.get("screen_px", c["font_px"])))
        if px < floor - 0.01:
            found["font"].append(dict(where, why="%.1f px < %d px floor" % (px, floor)))
        if c.get("override", -1) >= 0 and c["override"] not in ok_sizes:
            found["font"].append(dict(where, why="font_size override %d is not a §4.2 step x %.1f" % (c["override"], ts)))
        whys = []
        if c.get("ellipsis"):
            whys.append('text holds "…"')
        if c.get("overrun", 0) != 0 and not c.get("fits", True):
            whys.append("overrun trims text that doesn't fit")
        if c.get("clip") and not c.get("fits", True):
            whys.append("clip_text cuts text that doesn't fit")
        if c.get("visible_lines", 1) < c.get("lines", 1) and not c.get("in_scroll"):
            whys.append("%d of %d lines visible, no scroll" % (c["visible_lines"], c["lines"]))
        if c["class"] == "RichTextLabel" and not c.get("fits", True) and not c.get("in_scroll"):
            whys.append("content taller than the box")
        if whys:
            found["clipped"].append(dict(where, why="; ".join(whys)))
        if img is not None:
            bg = background(img, c["ink"])
            if bg is not None:
                col = c["color"]
                a = max(0.0, min(1.0, col[3] * c.get("alpha", 1.0)))
                fg = tuple(round((col[i] * a) * 255 + bg[i] * (1 - a)) for i in range(3))
                r = ratio(fg, bg)
                need = LARGE_MIN if px >= LARGE_PX * ts else BODY_MIN
                if r < need:
                    m = strongest(img, c["ink"], bg)
                    found["contrast"].append(dict(where, why="%.2f:1 < %.1f:1 (font %s on bg %s; measured %.2f:1%s)" % (
                        r, need, "#%02x%02x%02x" % fg, "#%02x%02x%02x" % bg, m, ", low confidence" if m >= need else "")))
    # b: overlaps between text areas, ancestors and descendants excluded.
    for i in range(len(items)):
        a = items[i]
        ra = a["ink"]
        for j in range(i + 1, len(items)):
            b = items[j]
            pa, pb = a["path"], b["path"]
            if pb.startswith(pa + "/") or pa.startswith(pb + "/"):
                continue
            rb = b["ink"]
            ox = min(ra[0] + ra[2], rb[0] + rb[2]) - max(ra[0], rb[0])
            oy = min(ra[1] + ra[3], rb[1] + rb[3]) - max(ra[1], rb[1])
            if ox >= MIN_OVERLAP and oy >= MIN_OVERLAP:
                found["overlap"].append({"path": pa, "text": a["text"][:40], "owner": a.get("owner_script", ""),
                                         "other": pb, "other_text": b["text"][:40],
                                         "why": "%.0fx%.0f px overlap" % (ox, oy)})
    custom = sorted({d["script"] for d in data.get("custom_draw", [])})
    return {"screen": data["screen"], "text_scale": ts, "controls": len(items), "findings": found,
            "hidden": hidden, "custom_draw_scripts": custom}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--detail-cap", type=int, default=12, help="findings listed per screen and rule")
    ap.add_argument("--detail-combos", help="combos with per-screen details (default: every unfiltered combo)")
    args = ap.parse_args()
    pack = Path(args.pack)
    entries = [e for e in pack_axes.load_entries(pack) if e["axes"]["filter"] == "none" and e.get("status") == "ok"]
    by_combo: dict[str, dict] = defaultdict(dict)
    for e in entries:
        lint = pack / (e.get("lint") or "%s/%s.lint.json" % (e["combo"], e["screen"]))
        if not lint.exists():
            continue
        data = json.loads(lint.read_text(encoding="utf-8"))
        by_combo[e["combo"]][e["screen"]] = lint_screen(data, pack / e["path"])
    combos = sorted(by_combo, key=pack_axes.combo_sort_key)
    order = pack_axes.screen_order(entries)
    for c in combos:
        (pack / c / "lint.json").write_text(json.dumps(by_combo[c], indent=1), encoding="utf-8")
    (pack / "lint.json").write_text(json.dumps(by_combo, indent=1), encoding="utf-8")
    # Markdown.
    L = ["# Runtime visual lint", "",
         "Generated by `tools/visual_qa/lint_report.py` from `%s`. A report, not a gate (it needs a renderer)." % pack.name, "",
         "Rules: **font** (a: < 12 x text scale, or a size override off the §4.2 scale), **overlap** (b), "
         "**clipped** (c), **contrast** (d: < 4.5:1, 3:1 at >= 24 px, background sampled from the PNG). "
         "(e) Text drawn by a script's own `_draw` (`draw_string`) is invisible to the tree walk; each screen lists "
         "those scripts under *custom-drawn*. Overlap counts pairs; a modal over a page also counts (the walk can't "
         "see occlusion). Contrast marked *low confidence* had a glyph pixel that does reach the minimum (the "
         "declared colour may not be what is drawn).", ""]
    L += ["## Totals per combo", "", "| combo | screens | " + " | ".join(RULES) + " |", "|---|---|" + "---|" * len(RULES)]
    for c in combos:
        t = Counter()
        for s in by_combo[c].values():
            for r in RULES:
                t[r] += len(s["findings"][r])
        L.append("| %s | %d | %s |" % (c, len(by_combo[c]), " | ".join(str(t[r]) for r in RULES)))
    L += ["", "## Findings per screen (all combos summed)", "", "| screen | " + " | ".join(RULES) + " | custom-drawn scripts |",
          "|---|" + "---|" * (len(RULES) + 1)]
    for s in order:
        t = Counter()
        custom = set()
        for c in combos:
            if s in by_combo[c]:
                for r in RULES:
                    t[r] += len(by_combo[c][s]["findings"][r])
                custom |= set(by_combo[c][s]["custom_draw_scripts"])
        L.append("| %s | %s | %d |" % (s, " | ".join(str(t[r]) for r in RULES), len(custom)))
    owners = Counter()
    for c in combos:
        for s in by_combo[c].values():
            for r in RULES:
                for f in s["findings"][r]:
                    owners[(f.get("owner") or "(no game script)", r)] += 1
    L += ["", "## Findings per owning script and rule (all combos)", "", "| script | rule | findings |", "|---|---|---|"]
    for (o, r), n in owners.most_common(40):
        L.append("| %s | %s | %d |" % (o.replace("res://", ""), r, n))
    detail = set(args.detail_combos.split(",")) if args.detail_combos else set(combos)
    for c in combos:
        if c not in detail:
            continue
        L += ["", "## Details: %s" % c]
        for s in order:
            res = by_combo[c].get(s)
            if res is None:
                continue
            n = sum(len(res["findings"][r]) for r in RULES)
            L += ["", "### %s (%d text controls, %d findings)" % (s, res["controls"], n)]
            for r in RULES:
                fs = res["findings"][r]
                if not fs:
                    continue
                L.append("- **%s** (%d)" % (r, len(fs)))
                for f in fs[:args.detail_cap]:
                    tail = (" vs `%s` \"%s\"" % (_short(f["other"]), f["other_text"])) if r == "overlap" else ""
                    L.append("  - `%s` \"%s\"%s: %s" % (_short(f["path"]), f["text"].replace("\n", " "), tail.replace("\n", " "), f["why"]))
                if len(fs) > args.detail_cap:
                    L.append("  - ... %d more (lint.json)" % (len(fs) - args.detail_cap))
            if res.get("hidden"):
                L.append("- not in the picture (covered, left out): %d" % len(res["hidden"]))
            if res["custom_draw_scripts"]:
                L.append("- custom-drawn (not linted): " + ", ".join(x.replace("res://scripts/ui/", "") for x in res["custom_draw_scripts"]))
    (pack / "lint_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("lint_report: %d combos, %d screens -> %s" % (len(combos), sum(len(v) for v in by_combo.values()), pack / "lint_report.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
