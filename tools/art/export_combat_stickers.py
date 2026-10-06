"""Export the combat's vinyl stickers from the round 19-39 concept generators (M14 asset parity).

Runs the art pass's own drawing code on tag `art-concepts-r43` (copy in
`docs/concepts/round39_landing_exploits/scripts/`, which carries round 19's `effects_batch1.py`, round 22's
`fx_r22.py` and round 39's `landing.py`) and writes each sticker out as a transparent PNG, cropped to its alpha:

- `send_it.png`: the SEND IT sticker (`fx_r22.send_sticker`'s lettering + `build_sticker`, same arguments) with
  its gloss left to the runtime material (`gloss_k=0`): VinylSticker's shader gives the rest gloss 0.22 and the
  hover sweep, as the concept's states do (idle 0.22, hover 1.0), and greys it when disabled.
- `word_perfect.png`, `word_good.png`, `word_weak.png`: the precision landing words (`landing.word` ->
  `effects_batch1.vinyl_word`, same colours, sizes and tilt).
- `evade_token.png`: the `>>` EVADE token sticker (`effects_batch1.token_sticker`).
- `drone.png` and `drone_piece_<k>.png`: the drone sticker (`fx_r22.drone_sticker`, its HP number split off:
  the game shows the live HP) and the six pieces it breaks into (`fx_r22._pieces_from`), with each piece's
  offset and direction in the manifest.
- `manifest.json`: source, tag, the call and settings of each file.

The wrapper patches only data: the font paths (the art-pass checkout path is hard-coded) and, for the drone,
`ImageDraw.text` while it draws (the split).

Usage (never from stdin on this machine): extract `content`, `assets/fonts` and
`docs/concepts/round39_landing_exploits/scripts` and `docs/concepts/round17_slice_system/glyphs` from the tag
into one folder (the scripts read the content and the round 17 glyphs by relative path), then
    python tools/art/export_combat_stickers.py --src <extracted>/docs/concepts/round39_landing_exploits/scripts
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "fx" / "stickers"
TAG = "art-concepts-r43"
SRC = "docs/concepts/round39_landing_exploits/scripts/"


def crop(im):
    bb = im.split()[3].getbbox()
    return im.crop(bb) if bb else im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the round 39 concept scripts folder (from the tag)")
    args = ap.parse_args()
    sys.path.insert(0, args.src)
    os.chdir(args.src)
    import sticker_lib19 as SL

    fonts = {"ANTON": "Anton-Regular.ttf", "MARKER": "PermanentMarker-Regular.ttf",
             "PLEX": "IBMPlexSansCondensed-Medium.ttf", "MONO": "ShareTechMono-Regular.ttf"}
    old_anton = SL.ANTON
    for k, f in fonts.items():
        setattr(SL, k, str(FONTS / f))
    d = list(SL.lettering.__defaults__)
    d = [str(FONTS / fonts["ANTON"]) if v == old_anton else v for v in d]
    SL.lettering.__defaults__ = tuple(d)
    from PIL import Image, ImageDraw

    import effects_batch1 as EB
    import fx_r22 as R22
    import landing as LD

    OUT.mkdir(parents=True, exist_ok=True)
    files = {}
    # SEND IT: send_sticker's own lettering and die-cut, gloss left to the runtime material.
    art = SL.lettering(["SEND IT"], 74, [R22.FILL_PINK], key_w=6, extrude=9, seed=21, jitter=4.0, track=1, holo_seed=61)
    sd = SL.build_sticker(art, border=15, material="gloss", seed=21, close=15 * 1.25, gloss_k=0.0)
    im = crop(sd["img"])
    im.save(OUT / "send_it.png", optimize=True)
    files["send_it.png"] = {"call": "SL.lettering(['SEND IT'], 74, [FILL_PINK], key_w=6, extrude=9, seed=21, jitter=4.0, track=1, "
                            "holo_seed=61) + SL.build_sticker(border=15, close=18.75, seed=21, gloss_k=0.0)",
                            "from": "fx_r22.send_sticker", "scale": SL.SS, "lettering_px": 74, "size": list(im.size)}
    # The precision words.
    for tier, info in LD.TIERS.items():
        size = 50 if tier != "good" else 42
        im = crop(EB.vinyl_word(info["word"], info["col"], ink=LD.MC.INK, size=size, tilt=-5))
        fn = "word_%s.png" % tier
        im.save(OUT / fn, optimize=True)
        files[fn] = {"call": "EB.vinyl_word(%r, %r, size=%d, tilt=-5)" % (info["word"], info["col"], size), "from": "landing.word",
                     "scale": 1, "lettering_px": size, "size": list(im.size)}
    # The EVADE token.
    im = crop(EB.token_sticker())
    im.save(OUT / "evade_token.png", optimize=True)
    files["evade_token.png"] = {"call": "EB.token_sticker()", "scale": 1, "size": list(im.size)}
    # The drone sticker without its HP number, and its six pieces.
    text0 = ImageDraw.ImageDraw.text
    ImageDraw.ImageDraw.text = lambda *a, **k: None
    try:
        spr = R22.drone_sticker(5)
        pieces = R22._pieces_from(spr)
    finally:
        ImageDraw.ImageDraw.text = text0
    spr.save(OUT / "drone.png", optimize=True)
    files["drone.png"] = {"call": "fx_r22.drone_sticker(hp) with ImageDraw.text split off", "scale": 1, "size": list(spr.size),
                          "hp_plate_centre": [40 + 2, 2 * 40 - 4], "hex_centre": [42, 42]}
    for k, p in enumerate(pieces):
        fn = "drone_piece_%d.png" % k
        p["im"].save(OUT / fn, optimize=True)
        files[fn] = {"call": "fx_r22._pieces_from(drone_sticker)[%d]" % k, "offset": [round(v, 2) for v in p["off"]],
                     "dir": round(p["dir"], 4), "dir_deg": round(math.degrees(p["dir"]), 2), "size": list(p["im"].size)}
    (OUT / "manifest.json").write_text(json.dumps({
        "source_tag": TAG, "source": SRC + "{fx_r22.py, effects_batch1.py, landing.py, sticker_lib19.py}",
        "reference": "docs/art_reference/hud/round22_combat_fx/send_it_sticker.jpg; cards_fx/round39_landing_exploits/landing_*.frames.jpg; "
                     "cards_fx/round23_combat_fx/fx_evade_v4.gif; cards_fx/round19_combat_fx/fx_drone.gif; "
                     "cards_fx/round22_combat_fx/fx_drone_destroyed_v3.gif",
        "script": "tools/art/export_combat_stickers.py", "cropped_to_alpha": True, "files": files}, indent=1), encoding="utf-8")
    print("wrote", len(files), "stickers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
