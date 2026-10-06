"""Export the firmware dies and the Daemon CRT tiles from the round 34 concept generator (M14 asset parity).

The art pass drew both with `fwlib.py` on tag `art-concepts-r43`
(`docs/concepts/round34_firmware_daemons/scripts/`): `chip(fid, s, lit, glyph)` is the socketed die of
`firmware_set.png` / `firmware_socket.png`, `daemon_tile(did, s, t, fire)` the CRT tile of `daemon_set.png` /
`daemon_row.png`. This wrapper calls them unchanged and only writes their output out as transparent PNGs:

- `assets/wheel/firmware/die_<rarity>.png` / `die_<rarity>_lit.png`: the socketed die as `put_chip` lays it
  (socket recess with its rarity lip, the body, the flare glow when lit) without its glyph (the
  game stamps 1C's atlas glyph upright on it, as `put_chip` does), `lit` = the trigger flare (lit=1).
  One per rarity (common, uncommon, rare, boss): the body depends on the rarity alone. Pins on the top
  edge, the die centred in the image (`chip_anchor`).
- `assets/wheel/daemons/<id>.png`: a flipbook, FRAMES columns of the idle loop (t = k / FRAMES: the scan
  bar roll, the sigil breath, the heartbeat LED) and one last column with the fire flash (fire = 1).
- `manifest.json` in each folder: source script and tag, settings, cell layout.

The wrapper patches only data: the font paths (the art-pass checkout path is hard-coded in sticker_lib19;
these images draw no text), and a boss-rarity entry for the die (the concept table has no boss firmware;
RAR_COL / RAR_PIPS carry the boss colour and pips).

Usage (never from stdin on this machine):
    git archive -o %TEMP%\\x\\c.tar art-concepts-r43 docs/concepts/round34_firmware_daemons/scripts
    (extract it) then
    python tools/art/export_firmware_daemons.py --src <extracted>/docs/concepts/round34_firmware_daemons/scripts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT_FW = ROOT / "assets" / "wheel" / "firmware"
OUT_DM = ROOT / "assets" / "wheel" / "daemons"
TAG = "art-concepts-r43"
SRC = "docs/concepts/round34_firmware_daemons/scripts/fwlib.py"

## The die width in px (2x the largest in-game chip: 50 master at the 1080p combat wheel is ~60 px).
DIE_PX = 128
## The Daemon tile in px (2x the rack's 40 px tile at 720p x text scale 1.6).
TILE_PX = 128
## Idle loop frames (the rack's `daemon_rack_scan` picks one per beat).
FRAMES = 12
RARITIES = ["common", "uncommon", "rare", "boss"]
## The die image's side as a share of the die width (room for the socket recess and the flare glow).
SOCKET_SIDE = 2.8


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

    for k in ("ANTON", "MARKER", "MONO", "PLEX"):
        setattr(L, k, getattr(SL, k))
    import fwlib as F
    from PIL import Image

    OUT_FW.mkdir(parents=True, exist_ok=True)
    OUT_DM.mkdir(parents=True, exist_ok=True)
    # One representative firmware per rarity (the body is the rarity's alone); boss: a data entry.
    pick = {}
    for fid, _name, rar, _types, _eff in F.FIRMWARE:
        pick.setdefault(rar, fid)
    F.FW["_boss"] = ("_boss", "Boss", 3, [], "")
    pick[3] = "_boss"
    fw_files = {}
    # put_chip stamps the upright effect glyph itself; the game stamps 1C's atlas glyph upright over the
    # rotated die, so the wrapper hands put_chip an empty glyph (a split, as for the sheet's text).
    F.icon_rgba = lambda *a, **k: Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    side = int(DIE_PX * SOCKET_SIDE)
    for rar, name in enumerate(RARITIES):
        for lit in (0.0, 1.0):
            # The socketed die exactly as put_chip lays it on a wheel (socket recess + rarity lip, the body,
            # the flare glow when lit), at angle 180 so the body is unrotated: pins on the top edge.
            im = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            im = F.put_chip(im, pick[rar], side / 2, side / 2, 180.0, DIE_PX, lit=lit)
            fn = "die_%s%s.png" % (name, "_lit" if lit else "")
            im.save(OUT_FW / fn, optimize=True)
            fw_files[fn] = {"rarity": name, "lit": lit, "size": list(im.size)}
    ax, ay = side / 2, side / 2
    (OUT_FW / "manifest.json").write_text(json.dumps({
        "source_tag": TAG, "source": SRC, "function": "put_chip(canvas, fid, c, c, 180, s, lit) with the glyph split off (icon_rgba empty)",
        "reference": "docs/art_reference/wheel/round34_firmware_daemons/firmware_set.jpg, firmware_socket.jpg",
        "script": "tools/art/export_firmware_daemons.py", "die_px": DIE_PX,
        "anchor": [ax, ay], "pins": "top edge (toward the core when drawn)", "files": fw_files}, indent=1), encoding="utf-8")
    dm_files = {}
    for did, _name, rar, fam, _eff, _counter in F.DAEMONS:
        sheet = Image.new("RGBA", (TILE_PX * (FRAMES + 1), TILE_PX), (0, 0, 0, 0))
        for k in range(FRAMES):
            sheet.alpha_composite(F.daemon_tile(did, TILE_PX, t=k / FRAMES), (k * TILE_PX, 0))
        sheet.alpha_composite(F.daemon_tile(did, TILE_PX, t=0.0, fire=1.0), (FRAMES * TILE_PX, 0))
        sheet.save(OUT_DM / ("%s.png" % did), optimize=True)
        dm_files[did] = {"rarity": RARITIES[rar], "family": fam}
        print("daemon", did, flush=True)
    (OUT_DM / "manifest.json").write_text(json.dumps({
        "source_tag": TAG, "source": SRC, "function": "daemon_tile(did, s, t=k/frames) + daemon_tile(did, s, t=0, fire=1)",
        "reference": "docs/art_reference/wheel/round34_firmware_daemons/daemon_set.jpg, daemon_row.jpg, daemon_trigger.gif",
        "script": "tools/art/export_firmware_daemons.py", "tile_px": TILE_PX, "frames": FRAMES,
        "layout": "columns 0..frames-1 = idle loop t = k / frames; column frames = fire flash", "files": dm_files}, indent=1),
        encoding="utf-8")
    print("wrote", len(fw_files), "dies,", len(dm_files), "daemon sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
