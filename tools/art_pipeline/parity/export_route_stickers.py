"""M14 asset parity: the netrun route's node stickers and the operative token (ART-7 3B) from round 37's
own generator.

Runs `docs/concepts/round37_netrun/scripts/r32ui.py` (tag art-concepts-r43) unchanged: `node_sd(kind, px)`
(the round 31 node icon on a die-cut vinyl sticker; `grey=True` is the past / cut-off look) and
`token_sd(px)` (the operative token: the Breaker emblem in Cell pink). The concept builds stickers at
its supersample SS = 2, so each image is already 2x; this wrapper saves it trimmed to the die-cut.

    python tools/art_pipeline/parity/export_route_stickers.py --concepts <extracted>/docs/concepts

Output: assets/netrun/route/*.png + manifest.json. Kinds: router (fight), elite, terminal (event),
modem (shop), rack.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parity_common as PC  # noqa: E402

ROUND = "round37_netrun"
OUT = PC.ROOT / "assets" / "netrun" / "route"
# The concept's sticker size for a route node (hq_views / transit_view: 46 walked .. 60 option).
PX = 54
TOKEN_PX = 54
KINDS = ["router", "elite", "terminal", "modem", "rack"]


def main() -> int:
    a = PC.args(__doc__.splitlines()[0])
    scripts = PC.use_round(a.concepts, ROUND)
    import r32ui as U

    man = PC.Manifest(OUT, "route_stickers", "M14 asset parity: netrun route node stickers and the operative token (ART_BIBLE v2 4.6; round 36/37 option A).",
                      ROUND, ["r32ui.py", "r31lib.py", "sticker_lib19.py"], "tools/art_pipeline/parity/export_route_stickers.py")
    for kind in KINDS:
        sd = U.node_sd(kind, PX)
        man.add(PC.trim(sd["img"], 1), "node_" + kind, "r32ui.node_sd('%s', %d)['img']" % (kind, PX), "SS = 2 image (2x), trimmed to the die-cut")
        sd = U.node_sd(kind, PX, grey=True)
        man.add(PC.trim(sd["img"], 1), "node_%s_past" % kind, "r32ui.node_sd('%s', %d, grey=True)['img']" % (kind, PX),
                "the concept's past / cut-off sticker (greyscale 0.7)")
    sd = U.token_sd(TOKEN_PX)
    man.add(PC.trim(sd["img"], 1), "token_operative", "r32ui.token_sd(%d)['img']" % TOKEN_PX, "the operative token over 'you are here'")
    man.write(scripts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
