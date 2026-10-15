"""Debug: raw figure masks on a sheet. python preview_figs.py roman|atlantis -> D:/rc_scratch/boss_wheel_v2/figs_<corp>.png"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw  # noqa: E402

import bw_kit as K  # noqa: E402

COLS = {"back": (90, 90, 110), "main": (235, 235, 235), "drape": (150, 40, 120), "arm": (220, 200, 170),
        "detail": (255, 60, 60), "glint": (255, 200, 60), "eye": (60, 255, 200), "ink": (60, 40, 90), "pupil": (10, 10, 10)}


def show(masks):
    any_m = next(iter(masks.values()))
    im = Image.new("RGBA", any_m.size, (20, 22, 30, 255))
    for n in ("back", "ink", "main", "drape", "arm", "detail", "glint", "eye", "pupil"):
        if n in masks:
            im.alpha_composite(K.solid(masks[n], COLS[n]))
    return im


def main(corp):
    if corp == "roman":
        import fig_roman as F
        items = [("chariot 0", F.chariot(400, 0.0, 0.0)), ("chariot .3", F.chariot(400, 0.2, 0.5)), ("chariot 1", F.chariot(400, 0.4, 1.0)),
                 ("lion 0", F.lion(400, 0.0, 0.0)), ("lion 1", F.lion(400, 0.3, 1.0)), ("testudo", F.testudo(400, 0, 0.0)),
                 ("secutor", F.secutor(400, 0, 0)), ("crowd", F.crowd(400, 0, 0)), ("crowd act", F.crowd(400, 0.2, 1.0)),
                 ("emperor", F.emperor(400, 0, 0)), ("pulvinar side", F.pulvinar(400, 0.0)), ("pulvinar down", F.pulvinar(400, -1.0)),
                 ("pulvinar up", F.pulvinar(400, 1.0))]
    else:
        import fig_atlantis as F
        items = F.preview_items()
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * 420, rows * 440), (10, 10, 14, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, m) in enumerate(items):
        im = show(m)
        x, y = (i % cols) * 420 + 10, (i // cols) * 440 + 30
        sheet.alpha_composite(im, (x, y))
        d.text((x, y - 24), name, font=K.f_ui(20), fill=(255, 255, 255))
    sheet.convert("RGB").save(os.path.join(K.SCR, "figs_%s.png" % corp))


if __name__ == "__main__":
    main(sys.argv[1])
