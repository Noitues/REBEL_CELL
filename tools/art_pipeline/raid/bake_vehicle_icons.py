"""Bake the raid's threat vehicle icons v4 (ART-6 3A; ART_BIBLE v2 4.8) from the approved concept.

The icons are drawn by the concept script `icons22.py` on tag `art-concepts-r43`
(`docs/concepts/round22_raid_world/scripts/icons22.py`, sheet `vehicle_icons_v4.png`). This runs its
`icon()` UNCHANGED (designer 2026-10-05: "never redraw art that the art pass already made") and writes
each icon as its own transparent PNG at 2x of the game's map size into `assets/raid/icons/`, with
`manifest.json` naming the source script, the tag and every file:

    <corp>_<type>_<status>_hp<NNN>.png   type fast/heavy/special/flying, status none/slowed/frozen,
                                         hp 100/075/050/025/000 (the fill drains from the top)
    <corp>_<type>_up_hp100.png           UPGRADED (two white chevrons, double rim)

The heading arrow (hover only) turns with the threat, so the game draws it; everything else is the
concept's pixels.

Usage (never from stdin on this machine): extract the concept files, keeping their layout under one root
(`<root>/round22_raid_world/scripts/icons22.py` and `<root>/round17_slice_system/glyphs/*.png`, e.g. with
`git show art-concepts-r43:docs/concepts/<path>`), then
    python tools/art_pipeline/raid/bake_vehicle_icons.py --src <root>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "icons"
TAG = "art-concepts-r43"
SCRIPT = "docs/concepts/round22_raid_world/scripts/icons22.py"
SHEET = "docs/concepts/round22_raid_world/vehicle_icons_v4.png"
# The game's map icon: the shape's radius is 11 px; icons22 draws the shape at 0.4 x `size`, so 1x is
# size 27.5 and 2x is this.
SIZE = 56
CORPS = {"meridian": "MERIDIAN", "solace": "SOLACE", "halcyon": "HALCYON", "orbital": "ORBITAL", "rebel_cell": "REBEL_CELL"}
TYPES = ["FAST", "HEAVY", "SPECIAL", "FLYING"]
STATUSES = {"none": (), "slowed": ("SLOWED",), "frozen": ("FROZEN",)}
HP = [1.0, 0.75, 0.5, 0.25, 0.0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="root holding round22_raid_world/ and round17_slice_system/")
    args = ap.parse_args()
    scripts = Path(args.src) / "round22_raid_world" / "scripts"
    sys.path.insert(0, str(scripts))
    import icons22  # noqa: E402  (the concept's own drawing, unchanged)

    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for corp, key in CORPS.items():
        for t in TYPES:
            for st, sts in STATUSES.items():
                for hp in HP:
                    name = "%s_%s_%s_hp%03d.png" % (corp, t.lower(), st, round(hp * 100))
                    icons22.icon(t, key, size=SIZE, hp=hp, statuses=sts).save(OUT / name)
                    files.append(name)
            name = "%s_%s_up_hp100.png" % (corp, t.lower())
            icons22.icon(t, key, up=True, size=SIZE).save(OUT / name)
            files.append(name)
    w = icons22.icon("HEAVY", "HALCYON", size=SIZE).size[0]
    manifest = {
        "schema": "rebel_cell.art_export/1",
        "asset": "raid_vehicle_icons_v4",
        "about": "ART-6 3A threat vehicle icons v4 (ART_BIBLE v2 4.8). Built by tools/art_pipeline/raid/bake_vehicle_icons.py; do not edit by hand.",
        "source": {"tag": TAG, "script": SCRIPT, "function": "icon(t, corp, up, size, hp, statuses)", "sheet": SHEET,
                   "glyphs": "docs/concepts/round17_slice_system/glyphs"},
        "size": SIZE, "image_px": w, "shape_radius_px": SIZE * 0.4,
        "types": [t.lower() for t in TYPES], "statuses": list(STATUSES), "hp": [round(h * 100) for h in HP],
        "files": files,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("baked %d icons (%d px) into %s" % (len(files), w, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
