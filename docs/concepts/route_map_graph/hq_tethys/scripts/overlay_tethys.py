"""hq_tethys: the overview TEST overlay: where route rooms could sit (plausible places only, no rules).

python overlay_tethys.py <plate.png> <rooms.json> <out.png>

Draws on the AAA plate: every candidate room (white ring), one example path in grease pencil (yellow walked, orange
next), the drowned part of the path dashed (it runs under the water), the TARGET circle on THE BLACK SMOKER and its
tag, and a small TEST caption. The HUD, stickers and dossier of the real netrun views are not drawn here.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import tethys_preset as TP  # noqa: E402

MONO = os.path.join(TP.FONTS, "ShareTechMono-Regular.ttf")
MARK = os.path.join(TP.FONTS, "PermanentMarker-Regular.ttf")
YEL, ORA, RED, WHITE = (214, 255, 58), (255, 150, 40), (232, 30, 40), (240, 244, 255)
# one example path (lock -> causeway -> the arrival pod -> its inner pod -> the station -> down the shaft -> the vent)
PATH = ["lock", "outer_0", "inner_0", "main_deck", "crown", "vent_cap", "deck_1", "deck_2", "deck_3", "deck_4", "deck_5", "server"]
WALKED = 2            # the first N links are drawn as walked (yellow), the next one as next (orange), the rest dashed


def pencil(d, pts, col, w, rng, dash=None):
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(L / 6))
        seg = []
        for k in range(n + 1):
            t = k / n
            j = 1.2 * math.sin(t * 9.0 + i) + rng.uniform(-0.5, 0.5)
            seg.append((x0 + (x1 - x0) * t - (y1 - y0) / max(L, 1) * j, y0 + (y1 - y0) * t + (x1 - x0) / max(L, 1) * j))
        if dash:
            for k in range(0, len(seg) - 1, 2):
                d.line([seg[k], seg[k + 1]], fill=col, width=w)
        else:
            d.line(seg, fill=col, width=w, joint="curve")


def main(plate, rooms_p, out):
    im = Image.open(plate).convert("RGBA")
    W, H = im.size
    R = json.load(open(rooms_p))
    sx, sy = W / R["res"][0], H / R["res"][1]
    rooms = {k: v["px"] for k, v in R["rooms"].items() if v["px"]}
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = random.Random(TP.SEEDS["pier"])
    f_s = ImageFont.truetype(MONO, int(13 * sx))
    f_m = ImageFont.truetype(MARK, int(30 * sx))
    P = {k: (v[0] * sx, v[1] * sy) for k, v in rooms.items()}
    # the example path
    path = [P[k] for k in PATH if k in P]
    for i in range(len(path) - 1):
        under = PATH[i + 1] in ("vent_cap",) or PATH[i].startswith(("vent", "deck")) or PATH[i + 1].startswith("deck") or PATH[i + 1] == "server"
        col = YEL if i < WALKED else (ORA if i == WALKED else WHITE)
        pencil(d, [path[i], path[i + 1]], col + (235,), max(2, int(4 * sx)), rng, dash=(i > WALKED or under))
    # every candidate room
    r = 8 * sx
    for k, (x, y) in sorted(P.items()):
        tgt = k == "server"
        col = RED if tgt else (YEL if k in PATH[:WALKED + 1] else (ORA if k == PATH[WALKED + 1] else WHITE))
        rad = r * (0.75 if k.startswith(("mid", "deck")) else 1.0)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(12, 16, 30, 210), outline=col + (255,), width=max(2, int(2.5 * sx)))
    # TARGET on the server
    if "server" in P:
        x, y = P["server"]
        pts = [(x + 34 * sx * math.cos(a) * (1 + 0.06 * math.sin(3 * a)), y + 26 * sx * math.sin(a)) for a in [i * 0.15 for i in range(46)]]
        d.line(pts, fill=RED + (240,), width=max(3, int(5 * sx)), joint="curve")
        d.text((x - 150 * sx, y - 62 * sx), "TARGET", font=f_m, fill=RED + (255,))
        tag = "CENTRAL SERVER // THE BLACK SMOKER"
        tw = d.textlength(tag, font=f_s)
        bx, by = x - tw - 46 * sx, y + 16 * sx
        d.rectangle([bx - 6, by - 4, bx + tw + 6, by + 18 * sx], fill=(20, 8, 12, 220), outline=RED + (255,), width=2)
        d.text((bx, by), tag, font=f_s, fill=(255, 120, 120, 255))
    if "lock" in P:
        x, y = P["lock"]
        tag = "DOCK LOCK (entry)"
        d.text((x + 14 * sx, y - 8 * sx), tag, font=f_s, fill=YEL + (255,))
    cap = "TEST // ATLANTIS STATION overview: candidate rooms (rings), one example path; dashed = under the water"
    d.rectangle([10, H - 30 * sy, 20 + d.textlength(cap, font=f_s), H - 8 * sy], fill=(6, 10, 22, 200))
    d.text((15, H - 27 * sy), cap, font=f_s, fill=(170, 200, 255, 255))
    Image.alpha_composite(im, ov).convert("RGB").save(out)
    print("OVERLAY", out, len(P), "rooms")


if __name__ == "__main__":
    main(*sys.argv[1:4])
