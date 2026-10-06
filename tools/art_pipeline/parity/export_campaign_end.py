"""M14 asset parity: the campaign end's pieces (ART-11 4D) from rounds 20 and 21's own generators.

Round 20 `lost20.py` (CAMPAIGN LOST, ransomware lock), unchanged:
  - `padlock(size, col)`: the lock stamped on every node (drawn white; the view tints it the house accent);
  - `motif(style, seed)`: the house style's full-screen motif mask (blueprint, hazard, cells, stars,
    glitch; seed 1 as `ransom` draws it), which the takeover shader tints;
  - `emblem_img(corp, size, col)`: the corp emblem inside `seal` (round 6 slicelib EM_<corp>, exported
    first by round 20's own `emblems20.py`), drawn white for the seal to tint.
Round 21 `dossier21.py` (the audit dossier), unchanged:
  - `postit([], col, w, h, seed)`: the auditor's post-it paper in its four colours (the words stay live text);
  - `sheet(...)` for the print's white stock, `manila(...)` for the folder (its `tape` is a flat translucent rect: drawn).

    python tools/art_pipeline/parity/export_campaign_end.py --concepts <extracted>/docs/concepts

Output: assets/campaign_end/*.png|jpg + manifest.json.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parity_common as PC  # noqa: E402

OUT = PC.ROOT / "assets" / "campaign_end"
CORPS = {"meridian": "MERIDIAN", "solace": "SOLACE", "halcyon": "HALCYON", "orbital": "ORBITAL", "rebel_cell": "REBEL_CELL"}
MOTIFS = ["blueprint", "hazard", "cells", "stars", "glitch"]
# dossier21.compose's post-it colours (the game's END_NOTE_* tokens carry the same values).
NOTES = {"pink": (255, 120, 170), "yellow": (255, 232, 90), "blue": (150, 220, 255), "green": (180, 240, 140)}


def main() -> int:
    a = PC.args(__doc__.splitlines()[0])
    from PIL import Image

    # Round 20: its emblem export first (it writes ../scratch/emblems next to the scripts).
    scripts20 = PC.use_round(a.concepts, "round20_raid_world")
    # emblems20 puts the art-pass checkout's round 6 scripts on sys.path; slicelib from this
    # extraction of the tag is imported first so the tag's copy draws the emblems.
    sys.path.insert(0, str(Path(a.concepts) / "round6_roster" / "scripts"))
    import slicelib  # noqa: F401
    sys.path.pop(0)
    runpy.run_path(str(scripts20 / "emblems20.py"), run_name="__main__")
    import lost20 as LO

    man = PC.Manifest(OUT, "campaign_end", "M14 asset parity: the campaign end's padlock, house motifs, seal emblems and dossier stock (ART_BIBLE v2 4.8).",
                      "round20_raid_world + round21_raid_world", ["lost20.py", "emblems20.py", "ui19.py", "dossier21.py"],
                      "tools/art_pipeline/parity/export_campaign_end.py")
    man.add(LO.padlock(144, (255, 255, 255)), "padlock", "lost20.padlock(144, white)", "2x the CORE's 72 px lock; the keyhole stays its ink")
    for corp, key in CORPS.items():
        man.add(LO.emblem_img(key, 256, (255, 255, 255)), "emblem_" + corp, "lost20.emblem_img('%s', 256, white)" % key,
                "the seal's emblem (round 6 slicelib EM_%s via emblems20.py), a white mask" % key)
    for style in MOTIFS:
        m = LO.motif(style, 1)
        man.add(m, "motif_" + style, "lost20.motif('%s', 1)" % style, "L mask 1920 x 1080 (the concept's screen; 1x)")

    # Round 21: the dossier's stock.
    sys.path.remove(str(scripts20))
    for mod in ("ui19", "sticker_lib19", "lost20", "layout", "finish19", "finish", "icons20", "netdecal19", "roof20", "tg_lib"):
        sys.modules.pop(mod, None)
    PC.use_round(a.concepts, "round21_raid_world")
    import dossier21 as DS

    for name, col in NOTES.items():
        # 2x the compose() note (230 x 200); the concept's blank paper (no words: the view letters them).
        man.add(DS.postit([], col, 460, 400, 41), "postit_" + name, "dossier21.postit([], %s, 460, 400, 41)" % (col,), "blank, 2x; words are live text")
    man.add(DS.sheet(580, 696, (246, 244, 238), 20, 4), "print_stock", "dossier21.sheet(580, 696, (246, 244, 238), 20, 4)",
            "the polaroid's white stock (polaroid(): sheet(w, 1.2 w, ...)), 2x of w 290")
    folder = DS.manila(1920, 1080, 11).convert("RGB")
    path = OUT / "manila.jpg"
    folder.save(path, quality=86, optimize=True)
    man.data["items"].append({"file": path.name, "made_by": "dossier21.manila(1920, 1080, 11)", "size": [1920, 1080],
                              "note": "the folder's stock, one screen (1x), JPEG q86"})
    print("wrote", path.relative_to(PC.ROOT))
    man.write(Path(a.concepts) / "round21_raid_world" / "scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
