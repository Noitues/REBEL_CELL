"""Bake the raid's defence cards (parity RAID-01; round 40 `raid_view_v3`, the dark card row along the
foot; ART_BIBLE v2 §4.8) from the approved concept.

Each card is drawn by the concept's own `asset_card()` on tag `art-concepts-r43`
(`docs/concepts/round19_raid/scripts/ui19.py`: the dark sticker face, the glyph window, the round 17 glyph
in the asset's colour, the colour band along the top; `sticker_lib19.build_sticker`: the white die-cut
border, rim and gloss), called UNCHANGED with the concept's own arguments (its TRAY, the seed each screen
gives it: `screens19.py` 50 + i, SENTRY 61 from `interactions19.py`). Only the card's WORDS are left off
(the wrapper makes the concept's `Pen.text` a no-op): the game writes the name, `INT n`, `xN` and the rule
lines live, translated, at the concept's spots (AssetCard). `build_sticker` returns straight alpha at the
concept's 2x supersampling: the image is cropped to the die-cut and saved at 2x. Nothing is redrawn.

    assets/raid/cards/<asset id>.png
    assets/raid/cards/manifest.json   (the face's box inside the image, for the live words)

Call (B3, review Q5, logged in DECISIONS "B3 — raid, map, route, clutter"; it replaces "Parity fix —
raid"'s vault in pink): HONEYPOT has no concept card; it is the same generator with the atlas's
placeholder hook (`placeholder_phishing`: a honeypot lures like the decoy) in the decoy violet
#B08CFF (pink is attack, the vault glyph is VAULT's), seed 62, until the glyph concept slice draws its
own.

Usage (never from stdin): extract `docs/concepts/round19_raid/scripts/`,
`docs/concepts/round3_overlay/o_a_tactical_glass/scripts/` and `docs/concepts/round17_slice_system/glyphs/`
of the tag under `<root>` keeping their layout, then
    python tools/art_pipeline/raid/bake_defence_cards.py --src <root>/docs/concepts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "cards"
TAG = "art-concepts-r43"
# The concept card's face (ui19.asset_card: card_sticker(150, 172, ...)) and its die-cut border (1x px).
FACE = (150, 172)
BORDER = 7
GLOSS_K = 0.22
# B3 (review Q5): the honeypot's decoy violet #B08CFF.
HONEYPOT_VIOLET = (176, 140, 255)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the extracted docs/concepts folder")
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.src) / "round19_raid" / "scripts"))
    import ui19 as U  # noqa: E402

    # The wrapper: the concept draws its words with Pen.text; the game writes them live.
    U.Pen.text = lambda self, *a, **k: None
    tray = {t[0]: t for t in U.TRAY}
    # Content id -> the concept's (name, glyph, integrity, copies, lines, colour) and seed.
    cards = {
        "turret": (tray["TURRET"], 50),
        "railgun": (tray["RAILGUN"], 51),
        "ice_lock": (tray["ICE LOCK"], 52),
        "flak_array": (tray["FLAK ARRAY"], 53),
        "decoy": (tray["DECOY"], 54),
        "tar_pit": (tray["TAR PIT"], 55),
        "sentry": (("SENTRY", "picto_target", 12, 1, ["3 dmg x2", "own node only"], U.GREEN), 61),
        "honeypot_node": (("HONEYPOT", "placeholder_phishing", 8, 1, ["pull 5", "fake vault"], HONEYPOT_VIOLET), 62),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    meta_cards = {}
    face_box = None
    for cid, (t, seed) in cards.items():
        name, glyph, hp, copies, lines, col = t
        sd = U.asset_card(name, glyph, hp, copies, lines, col, seed, gloss_k=GLOSS_K)
        img = sd["img"]
        box = sd["body"].getbbox()
        img = img.crop(box)
        img.save(OUT / ("%s.png" % cid))
        # The face (the concept's 150 x 172 art) inside the die-cut: centred, BORDER in from each side.
        w, h = img.size
        fw, fh = FACE[0] * U.S, FACE[1] * U.S
        face_box = [(w - fw) / 2.0 / w, (h - fh) / 2.0 / h, fw / w, fh / h]
        meta_cards[cid] = {"file": "%s.png" % cid, "concept_name": name, "glyph": glyph,
                           "color": list(col), "seed": seed, "image_px": [w, h]}
    meta = {"schema": "rebel_cell.art_export/1", "asset": "raid_defence_cards",
            "about": "Parity RAID-01 defence cards (dark sticker card, words left off). Built by "
                     "tools/art_pipeline/raid/bake_defence_cards.py; do not edit by hand.",
            "source": {"tag": TAG, "script": "docs/concepts/round19_raid/scripts/ui19.py (asset_card, TRAY)",
                       "seeds": "screens19.py 50 + i; interactions19.py SENTRY 61; HONEYPOT 62 (call)"},
            "scale": U.S, "face_px": list(FACE), "border_px": BORDER,
            "face_box": face_box, "cards": meta_cards}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("baked %d defence cards into %s" % (len(cards), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
