"""W10 review packs: the axis names, combo folder names and manifest reading shared by
capture_pack.py, contact_sheet.py, diff_pack.py and lint_report.py.

A combo folder is `<scale>_<input>_re-<off|on>_<filter>`, e.g. `1.0_mouse_re-off_none`.
"""

from __future__ import annotations

import json
from pathlib import Path

WIDTH = 1280
HEIGHT = 720
INPUTS = ("mouse", "pad")
RE = ("off", "on")
FILTERS = ("none", "grey", "deutan")
MANIFEST = "manifest.json"


def scale_text(scale: str | float) -> str:
    """'1' / 1.0 -> '1.0'; '1.60' -> '1.6'."""
    v = float(scale)
    t = ("%.2f" % v).rstrip("0")
    return t + "0" if t.endswith(".") else t


def combo_name(scale: str, inp: str, re: str, flt: str) -> str:
    return "%s_%s_re-%s_%s" % (scale_text(scale), inp, re, flt)


def parse_combo(name: str) -> dict | None:
    parts = name.split("_")
    if len(parts) != 4 or not parts[2].startswith("re-"):
        return None
    try:
        float(parts[0])
    except ValueError:
        return None
    return {"scale": parts[0], "input": parts[1], "re": parts[2][3:], "filter": parts[3]}


def combo_sort_key(name: str):
    a = parse_combo(name) or {"scale": "9", "input": name, "re": "", "filter": ""}
    return (float(a["scale"]), INPUTS.index(a["input"]) if a["input"] in INPUTS else 9,
            RE.index(a["re"]) if a["re"] in RE else 9, FILTERS.index(a["filter"]) if a["filter"] in FILTERS else 9)


def axis_word(axis: str, value: str) -> str:
    if axis == "re":
        return "RE " + value
    if axis == "scale":
        return "x" + value
    return value


def load_manifest(pack: Path) -> dict:
    p = Path(pack) / MANIFEST
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"entries": []}


def load_entries(pack: Path) -> list[dict]:
    """The manifest's entries, or (no manifest) one per <combo>/<screen>.png found."""
    pack = Path(pack)
    m = load_manifest(pack)
    if m.get("entries"):
        return m["entries"]
    out = []
    for d in sorted(p for p in pack.iterdir() if p.is_dir()):
        axes = parse_combo(d.name)
        if axes is None:
            continue
        for png in sorted(d.glob("*.png")):
            out.append({"screen": png.stem, "combo": d.name, "axes": axes, "path": "%s/%s" % (d.name, png.name),
                        "status": "ok", "warnings": []})
    return out


def png_of(pack: Path, entry: dict) -> Path | None:
    if not entry.get("path"):
        return None
    p = Path(pack) / entry["path"]
    return p if p.exists() else None


def screen_order(entries: list[dict]) -> list[str]:
    """Screens in capture order (the manifest's `order` field), then by name."""
    seen: dict[str, int] = {}
    for e in entries:
        o = e.get("order", 999)
        if e["screen"] not in seen or o < seen[e["screen"]]:
            seen[e["screen"]] = o
    return sorted(seen, key=lambda s: (seen[s], s))
