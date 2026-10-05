"""ART-7 3B: finish every room render into the game's node backdrops (1280x720 JPEG)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finish import finish  # noqa: E402

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
for corp in ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]:
    for kind in ["fight", "elite", "event", "shop", "rack"]:
        tag = "%s_%s" % (corp, kind)
        if not os.path.exists(os.path.join(SRC, tag + "_beauty_night.png")):
            print("missing", tag)
            continue
        im = finish(SRC, tag, (1280, 720), rain_n=2600, seed=7)
        im.convert("RGB").save(os.path.join(OUT, tag + ".jpg"), quality=82, optimize=True)
        print("wrote", tag)
