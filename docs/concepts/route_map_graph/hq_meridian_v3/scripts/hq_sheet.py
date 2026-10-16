"""HQ kit: H_mechanic_states.png, the mechanic's design-language sheet (2560 x 1440), from hq_halcyon's sheet.

Row 1: room crops from the finished decision render, each drawn in a state with the real overlay code (hq_mechui's
       marks included). Row 2: the mechanic shots (hq_graph.SHEET_SHOTS, rendered + composed with the overlay).
Row 3: the dial, then the corp's rule cards. Content: hq_mechui.SHEET.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import hq_graph as G  # noqa: E402
import hq_mechui as MU  # noqa: E402
import hq_overlay as O  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
W, H = 2560, 1440
BG = (12, 10, 18)


def tile_state(plate1920, A, room, state, mech, walked):
    img = plate1920.copy().convert("RGBA")
    poly = O.room_poly(A, room)
    st = {i: "reach" for i in G.NODES}
    st[room] = state
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    m = O.poly_mask(poly, 1)[..., None]
    l3 = O.lum(a)[..., None]
    if state == "grey":
        v = (l3 * 0.55) * 0.5 + np.array((0.06, 0.05, 0.11), np.float32) * 0.5
    elif state == "walked":
        v = (a * 0.55 + l3 * 0.45) * 0.7
    else:
        v = a
    a = a * (1 - m) + v * m
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    Aone = dict(rooms={i: (A["rooms"][i] if i == room else dict(front=None, vis=False)) for i in G.NODES}, edges=[],
                mt=A["mt"])
    opts = [room] if state == "option" else []
    img = O.draw_nodes(img, Aone, st, opts, mech, phase=0.3, walked=walked)
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w = (max(xs) - min(xs)) * 2.0
    h = w * 0.77
    box = (int(cx - w / 2), int(cy - h * 0.55), int(cx + w / 2), int(cy + h * 0.45))
    return img.crop(box).convert("RGB")


def card(sheet, xy, size, title, lines, col, fs=20):
    x, y = xy
    w, h = size
    img = sheet.convert("RGBA")
    img = KT.term(img, (x, y, x + w, y + h), title, accent=col, seed=61)
    f = K.F(K.MONO, fs)
    for k, ln in enumerate(lines):
        K.text(img, (x + 22, y + 62 + k * int(fs * 1.42)), ln, f, (215, 225, 232), "lm", 0.3)
    return img.convert("RGB")


def main():
    SH = MU.SHEET
    ovs = json.load(open(os.path.join(SCR, "ov_stills.json")))
    ov = ovs[SH.get("plate", "H_decision")]
    SFX = __import__("hq_preset").PRESET["hq"].get("suffix", "")       # HQ_REV_V2
    plate = Image.open(os.path.join(ROOT, "plates", SH.get("plate", "H_decision") + SFX + "_plate.png")).convert("RGB")
    plate = plate.resize((1920, 1080), Image.LANCZOS)
    pose = O.pose_of(ov["pose"])
    walked = ov["walked"]
    mt = ov.get("mt", len(walked) - 1)
    A = O.anchors(pose, walked, mt)
    mech = G.mech(walked, int(mt))
    sheet = Image.new("RGB", (W, H), BG)
    img = sheet.convert("RGBA")
    K.text(img, (60, 52), SH["title"], K.F(K.MONO, 30), (240, 238, 232), "lm", 0.6)
    K.text(img, (60, 94), SH["sub"], K.F(K.MONO, 18), (170, 182, 200), "lm", 0.3)
    sheet = img.convert("RGB")
    tw, th = 390, 300
    for k, (lab, room, state, col) in enumerate(SH["tiles"][:6]):
        if not O.room_poly(A, room):
            print("tile room not visible", room)
            continue
        t = tile_state(plate, A, room, state, mech, walked).resize((tw, th), Image.LANCZOS)
        x = 60 + k * (tw + 18)
        sheet.paste(t, (x, 130))
        ImageDraw.Draw(sheet).rectangle([x - 2, 128, x + tw + 1, 131 + th], outline=col, width=3)
        img = sheet.convert("RGBA")
        K.text(img, (x + 6, 130 + th + 24), lab, K.F(K.MONO, 21), col, "lm", 0.6)
        sheet = img.convert("RGB")
    sw, shh = 790, 444
    for k, (name, cap) in enumerate(SH["shots"][:3]):
        p = os.path.join(SCR, "sheet", name + SFX + ".png")
        x = 60 + k * (sw + 25)
        if os.path.exists(p):
            sheet.paste(Image.open(p).convert("RGB").resize((sw, shh), Image.LANCZOS), (x, 500))
        ImageDraw.Draw(sheet).rectangle([x - 2, 498, x + sw + 1, 501 + shh], outline=(90, 96, 110), width=2)
        img = sheet.convert("RGBA")
        for j, ln in enumerate(cap):
            K.text(img, (x + 4, 500 + shh + 22 + j * 24), ln, K.F(K.MONO, 17), (215, 225, 232), "lm", 0.3)
        sheet = img.convert("RGB")
    img = sheet.convert("RGBA")
    img = MU.dial(img, 90, 1060, mech, dict(walked=walked))
    K.text(img, (66, 1250), "the dial (top right of every frame)", K.F(K.MONO, 16), (170, 182, 200), "lm", 0.3)
    sheet = img.convert("RGB")
    x = 420
    for (title, lines, col, wcard) in SH["cards"][:2]:
        sheet = card(sheet, (x, 1040), (wcard, 370), title, lines, col, fs=18)
        x += wcard + 30
    out = os.path.join(ROOT, "H_mechanic_states" + SFX + ".png")
    sheet.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
