"""Debug: dump each slice scene sprite of a direction. python try_scene.py roman A [S]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import bw_kit as K  # noqa: E402
import wheel_v2 as W  # noqa: E402
from try_wheel import get_dir  # noqa: E402


def main():
    corp, key = sys.argv[1], sys.argv[2]
    S = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
    act = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    D, M = get_dir(corp, key)
    D._slots = M.SLOTS
    ctx = W.Ctx(S, t=0.3, phase=1, hp=1.0, rot=0.0, still=True)
    ims = []
    for i, s in enumerate(M.SLOTS):
        if s["type"] == "NULL":
            continue
        ims.append(D.scene(s, ctx, act, 0))
    w = ims[0].width
    sheet = Image.new("RGBA", (w * len(ims), w), (0, 0, 0, 255))
    for k, im in enumerate(ims):
        sheet.alpha_composite(im, (k * w, 0))
    sheet.convert("RGB").save(os.path.join(K.SCR, "scenes_%s_%s.png" % (corp, key)))


if __name__ == "__main__":
    main()
