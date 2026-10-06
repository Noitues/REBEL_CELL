"""Export the Cell's rubber stamp (B5; round 44 B_menus `campaign_slots.png`) from the concept script, unchanged.

Designer ruling (2026-10-05): never redraw art the art pass already made. Round 44's campaign slots board draws the
Cell's own red hex-and-fist rubber stamp ("ACTIVE // REBEL_CELL // OWN FILE") with `campaign_slots.cell_stamp`
(`docs/concepts/round44_undesigned/B_menus/scripts/campaign_slots.py` on the art-pass branch). This runs that
function as it is, once per slot state word the game shows, and saves each stamp as a PNG under
`assets/ui/menus/stamps/cell_stamp_<word>.png` (board px, the size the concept draws it: 1920x1080 board = 1080p),
with `meta.json` (word -> file, the hexagon's centre and radius in the image, before the concept's rotation).

The stamp is drawn at the concept's own angle (`angle`) for each slot on the board (-6 + 2 n); the game draws the
stamp unrotated (angle 0 here) and tilts it with a seeded per-slot tilt, so one image serves every slot.

Only paths change: the scripts' font paths point at the shipped faces (`assets/fonts`), and b44's crest folder at
this checkout's `assets/` (b44 reads the build's own exported crests). No drawing code is edited.

Usage (never from stdin on this machine):
    python <scratch>/extract_dir.py origin/art-pass <dir> docs/concepts/round44_undesigned/B_menus/scripts \\
        docs/concepts/round33_ui_chrome/scripts docs/concepts/round33_ui_chrome/fonts docs/concepts/round34_firmware_daemons/scripts
    (or `git archive origin/art-pass <those paths>` extracted to <dir>), then
    python tools/art/export_cell_stamp.py --src <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "ui" / "menus" / "stamps"
# The state words a slot shows (CaseFileCard.state_word, the keys; ACTIVE while the campaign simply runs).
WORDS = ["ACTIVE", "IN A RUN", "WON", "LOST", "ABANDONED"]
# campaign_slots.cell_stamp's own geometry (its canvas, the hexagon's centre and radius): read back for the game.
HEX_CENTRE = (58, 60)
HEX_R = 48


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the extracted art-pass tree (holds docs/concepts/...)")
    a = ap.parse_args()
    src = Path(a.src)
    b_scripts = src / "docs" / "concepts" / "round44_undesigned" / "B_menus" / "scripts"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(b_scripts))
    import b44 as K  # noqa: E402
    import campaign_slots as CS  # noqa: E402
    U = K.U
    U.MONO = str(FONTS / "ShareTechMono-Regular.ttf")
    U._fc.clear()
    K.BA = str(ROOT / "assets")
    K._cc.clear()
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"words": {}, "hex_centre": list(HEX_CENTRE), "hex_r": HEX_R, "board_h": 1080}
    for i, word in enumerate(WORDS):
        img = CS.cell_stamp(word, seed=i + 1, angle=0)
        name = "cell_stamp_%s.png" % word.lower().replace(" ", "_")
        img.save(OUT / name)
        meta["words"][word] = name
        print("wrote", OUT / name, img.size)
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
