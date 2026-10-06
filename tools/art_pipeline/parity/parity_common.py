"""M14 asset parity (city and screens): shared helpers for the export wrappers in this folder.

Every wrapper runs a concept generator script from tag `art-concepts-r43` with its drawing code
unchanged (designer ruling 2026-10-05 "reuse the art pass's assets, never redraw them"): it imports
the round's own modules from an extraction of the tag and calls their drawing functions, then writes
each item as its own transparent PNG at 2x next to a manifest naming its source.

Extract the concepts once (read only; never merge the tag):
    git archive -o concepts.tar art-concepts-r43 docs/concepts/<round>/scripts docs/concepts/round17_slice_system/glyphs
    tar -xf concepts.tar -C <dir>
then pass `--concepts <dir>/docs/concepts`.

The concept scripts read their fonts from the art-pass worktree (sticker_lib19.ROOT); the read-only
art-pass checkout carries them, so nothing here writes there.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

TAG = "art-concepts-r43"
TAG_COMMIT = "9a62cec89be362d89ad58ce8e2c2e2a126c8a3a1"
ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCHEMA = "rebel_cell.art_export/1"


def args(about: str) -> argparse.Namespace:
    """The common command line: --concepts <extracted docs/concepts>."""
    ap = argparse.ArgumentParser(description=about)
    ap.add_argument("--concepts", required=True, help="docs/concepts of an extraction of tag %s" % TAG)
    return ap.parse_args()


def use_round(concepts: str, round_dir: str) -> Path:
    """Puts round `round_dir`'s scripts first on sys.path and returns that folder."""
    scripts = Path(concepts) / round_dir / "scripts"
    if not scripts.is_dir():
        raise SystemExit("missing %s (extract it from the tag first)" % scripts)
    sys.path.insert(0, str(scripts))
    os.chdir(scripts)
    return scripts


def sha256_of(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


class Manifest:
    """One asset folder's manifest: every file with the concept function and arguments that drew it."""

    def __init__(self, out_dir: Path, asset: str, about: str, round_dir: str, scripts: list[str], driver: str):
        self.out_dir = out_dir
        self.data = {
            "schema": SCHEMA,
            "asset": asset,
            "about": about + " Built by %s; do not edit by hand." % driver,
            "source": {
                "tag": TAG,
                "commit": TAG_COMMIT,
                "round": "docs/concepts/" + round_dir,
                "scripts": scripts,
                "driver": driver,
                "drawing_code": "unchanged (designer ruling 2026-10-05: reuse the art pass's assets)",
            },
            "scale": "2x the concept's size unless an item says otherwise",
            "items": [],
        }
        out_dir.mkdir(parents=True, exist_ok=True)

    def add(self, im, name: str, made_by: str, note: str = "") -> None:
        """Saves RGBA image `im` as <name>.png and records how it was made."""
        path = self.out_dir / (name + ".png")
        im.save(path, optimize=True)
        item = {"file": path.name, "made_by": made_by, "size": [im.width, im.height]}
        if note:
            item["note"] = note
        self.data["items"].append(item)
        print("wrote", path.relative_to(ROOT), im.size)

    def write(self, concept_scripts: Path) -> None:
        used = [concept_scripts / s for s in self.data["source"]["scripts"]]
        self.data["source"]["scripts_sha256"] = sha256_of([p for p in used if p.exists()])
        (self.out_dir / "manifest.json").write_text(json.dumps(self.data, indent=1) + "\n", encoding="utf-8")
        print("wrote", (self.out_dir / "manifest.json").relative_to(ROOT))


def trim(im, margin: int = 2):
    """Crops transparent RGBA `im` to its content plus `margin` px, centred on the original centre
    (so the item's centre stays the drawing's anchor)."""
    box = im.getbbox()
    if box is None:
        return im
    cx, cy = im.width / 2, im.height / 2
    half_w = max(cx - box[0], box[2] - cx) + margin
    half_h = max(cy - box[1], box[3] - cy) + margin
    return im.crop((int(cx - half_w), int(cy - half_h), int(cx + half_w + 0.5), int(cy + half_h + 0.5)))
