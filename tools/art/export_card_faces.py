"""Export the hand cards' sticker faces from the round 31 card generator (M14 asset parity).

The art pass's C-C sticker card (the hand in `combat_typical_v4` / `card_play_v2_storyboard`) is drawn by
`r31lib.card_face` + `r31lib.card_sticker` on tag `art-concepts-r43` (copy in
`docs/concepts/round34_firmware_daemons/scripts/r31lib.py`): a dark faceted body in the card's kind colour,
the art panel (gradient + facets), the kind band, the rarity pips, the yellow cost dot, then the white die-cut
vinyl with its rim and gloss (holo die-cut for Rare). This wrapper calls them unchanged and writes the
art layer out: the words and the glyphs are split off (the wrapper turns `ImageDraw.text` and `glyph` into
no-ops for the call), because the game draws them live (translated title, kind word and rules text; the live
RAM cost; 1C's atlas glyphs for the art and the pictograms).

Output: `assets/cards/face_<kind>_<rarity>.png` (kind wheel | hack | system; rarity common | uncommon | rare |
boss), the sticker at the concept's 2x (SS) resolution, and `assets/cards/manifest.json` with the source, the
face rect inside the image and the layout the game places its live parts by (concept px of the 210 x 280 face).

Usage (never from stdin on this machine):
    git archive -o %TEMP%\\x\\c.tar art-concepts-r43 docs/concepts/round34_firmware_daemons/scripts
    (extract it) then
    python tools/art/export_card_faces.py --src <extracted>/docs/concepts/round34_firmware_daemons/scripts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "cards"
TAG = "art-concepts-r43"
SRC = "docs/concepts/round34_firmware_daemons/scripts/r31lib.py"
KINDS = ["WHEEL", "HACK", "SYSTEM"]
RARITIES = ["Common", "Uncommon", "Rare", "Boss"]
W, H = 210, 280


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the round 34 concept scripts folder (from the tag)")
    args = ap.parse_args()
    sys.path.insert(0, args.src)
    import sticker_lib19 as SL

    for k, f in {"ANTON": "Anton-Regular.ttf", "MARKER": "PermanentMarker-Regular.ttf",
                 "PLEX": "IBMPlexSansCondensed-Medium.ttf", "MONO": "ShareTechMono-Regular.ttf"}.items():
        setattr(SL, k, str(FONTS / f))
    import r31lib as L
    from PIL import Image, ImageDraw

    for k in ("ANTON", "MARKER", "MONO", "PLEX"):
        setattr(L, k, getattr(SL, k))
    # The split: no words, no glyphs in the art layer (the game draws them live).
    ImageDraw.ImageDraw.text = lambda *a, **k: None
    L.glyph = lambda name, px, *a, **k: Image.new("RGBA", (px, px), (0, 0, 0, 0))
    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    size = None
    for kind in KINDS:
        for rar in RARITIES:
            # The facets are seeded by the name: one fixed seed per kind (the kind word), every card of a kind alike.
            c = {"kind": kind, "name": kind, "art": "", "pic": "", "val": "", "text": "", "rar": rar, "cost": 0}
            sd = L.card_sticker(c, W, H)
            im = sd["img"]
            size = im.size
            fn = "face_%s_%s.png" % (kind.lower(), rar.lower())
            im.save(OUT / fn, optimize=True)
            files[fn] = {"kind": kind, "rarity": rar.lower(), "holo_border": rar == "Rare"}
            print("card", fn, im.size, flush=True)
    ss = SL.SS
    extra = int((6 + 6 * 0.5 + 12) * ss)  # build_sticker's padding for border 6, close 3 (sticker_from_art)
    (OUT / "manifest.json").write_text(json.dumps({
        "source_tag": TAG, "source": SRC, "function": "card_sticker(c, 210, 280) with ImageDraw.text and glyph split off",
        "reference": "docs/art_reference/hud/round41_wheel_stack/combat_typical_v4.jpg (hand), "
                     "docs/art_reference/cards_fx/round19_combat_fx/card_play_v2_storyboard.jpg",
        "script": "tools/art/export_card_faces.py", "scale": ss, "image": list(size),
        "face_rect": [extra, extra, W * ss, H * ss], "face_px": [W, H],
        "layout_px": {"cost_centre": [31, 29], "cost_r": 21, "title_centre": [127, 30], "title_w": 126, "title_px": 23,
                      "art_rect": [14, 52, 182, 102], "art_glyph": 0.74, "band_rect": [14, 154, 182, 24], "band_px": 15,
                      "pic_at": [22, 186], "pic_px": 30, "value_px": 34, "text_top": 228, "text_px": 13, "text_line": 17,
                      "text_w": 170},
        "kind_colours": {"WHEEL": [255, 196, 40], "HACK": [255, 61, 168], "SYSTEM": [92, 225, 255]},
        "files": files}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
