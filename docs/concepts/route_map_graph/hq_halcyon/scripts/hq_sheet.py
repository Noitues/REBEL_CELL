"""HQ Halcyon: H_scan_states.png, the room-state design language sheet (2560 x 1440).

Row 1: one room crop from the finished south-face decision render, drawn in each state with the real overlay code
       (the 3D room light / lockdown plane is what that state renders as in the plate it is cut from):
       OPEN (option) | IN THE EYE (scanned option) | WALKED | CURRENT | AHEAD | PAST
Row 2: the scan beam: the eye's gaze + blade crop from the overview, the lighthouse dial, the rule card
       (the round 43 SPOTTED wording and the brief's LOCKED wording, side by side), the 3D lockdown close-up.
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
import hq_overlay as O  # noqa: E402
import kit44 as KT  # noqa: E402
import sidekit as S  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
W, H = 2560, 1440
BG = (12, 10, 18)


def tile_state(plate1920, A, room, state, scanned=False, label=""):
    """Draw room `room` in `state` with the real overlay functions on a copy of the plate; return a crop round it."""
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
    Aone = dict(rooms={i: (A["rooms"][i] if i == room else dict(front=None, vis=False)) for i in G.NODES}, edges=[])
    opts = [room] if state == "option" else []
    img = O.draw_nodes(img, Aone, st, opts, {room} if scanned else set(), phase=0.3)
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w = (max(xs) - min(xs)) * 1.9
    h = w * 0.72
    box = (int(cx - w / 2), int(cy - h * 0.58), int(cx + w / 2), int(cy + h * 0.42))
    return img.crop(box).convert("RGB")


def card(sheet, xy, size, title, lines, col):
    x, y = xy
    w, h = size
    img = sheet.convert("RGBA")
    img = KT.term(img, (x, y, x + w, y + h), title, accent=col, seed=61)
    f = K.F(K.MONO, 21)
    for k, ln in enumerate(lines):
        K.text(img, (x + 22, y + 66 + k * 30), ln, f, (215, 225, 232), "lm", 0.3)
    return img.convert("RGB")


def main():
    ovs = json.load(open(os.path.join(SCR, "ov_stills.json")))
    ov = ovs["H_decision_S"]
    plate = Image.open(os.path.join(ROOT, "plates", "H_decision_S_plate.png")).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    pose = O.pose_of(ov["pose"])
    A = O.anchors(pose, ov["walked"])
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    K.text_img = None
    img = sheet.convert("RGBA")
    K.text(img, (60, 56), "HALCYON CIVIC  //  IN THE EYE: room states and the scan beam (design-language proposal)",
           K.F(K.MONO, 30), (240, 238, 232), "lm", 0.6)
    K.text(img, (60, 100), "Row 1: one room of the south-face decision render in every state (the real overlay code). "
           "Red = in the eye: ring, eye badge, holo scan lines, IN THE EYE chip; the 3D room goes to red lockdown light.",
           K.F(K.MONO, 18), (170, 182, 200), "lm", 0.3)
    sheet = img.convert("RGB")
    tiles = [("OPEN (next)", "n19", "option", False, S.ORANGE), ("IN THE EYE", "n4", "option", True, O.RED),
             ("WALKED", "n2", "walked", False, S.LIME), ("CURRENT", "n3", "current", False, S.LIME),
             ("AHEAD, IN THE EYE", "n20", "reach", True, O.RED), ("PAST", "n1", "grey", False, S.GREY)]
    tw, th = 390, 300
    for k, (lab, room, state, scn, col) in enumerate(tiles):
        t = tile_state(plate, A, room, state, scn).resize((tw, th), Image.LANCZOS)
        x = 60 + k * (tw + 18)
        sheet.paste(t, (x, 150))
        dd = ImageDraw.Draw(sheet)
        dd.rectangle([x - 2, 148, x + tw + 1, 151 + th], outline=col, width=3)
        img = sheet.convert("RGBA")
        K.text(img, (x + 6, 150 + th + 26), lab, K.F(K.MONO, 22), col, "lm", 0.6)
        sheet = img.convert("RGB")
    # row 2: the beam (overview crop round the eye), the 3D lockdown close-up, the dial, the rule card
    ovp = Image.open(os.path.join(ROOT, "plates", "H_overview_plate.png")).convert("RGB")
    oov = ovs["H_overview"]
    po = O.pose_of(oov["pose"])
    e = G.eye_pos()
    p = po.proj(e, w=ovp.width)
    cw, ch = int(ovp.width * 0.36), int(ovp.width * 0.36 * 0.75)
    cx, cy = int(p[0]), int(p[1] + ch * 0.32)
    crop = ovp.crop((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)).resize((780, 585), Image.LANCZOS)
    sheet.paste(crop, (60, 560))
    img = sheet.convert("RGBA")
    K.text(img, (66, 1170), "THE SCAN BEAM: the eye turns 45 deg a step; its gaze lights a 90 deg sector,", K.F(K.MONO, 18),
           (215, 225, 232), "lm", 0.3)
    K.text(img, (66, 1196), "the blade (a white scan line) sweeps down the rooms in it; the lighthouse beam reads", K.F(K.MONO, 18),
           (215, 225, 232), "lm", 0.3)
    K.text(img, (66, 1222), "from any orbit angle.", K.F(K.MONO, 18), (215, 225, 232), "lm", 0.3)
    sheet = img.convert("RGB")
    full = Image.open(os.path.join(ROOT, "plates", "H_decision_S_plate.png")).convert("RGB")
    s2 = full.width / 1920
    poly = O.room_poly(A, "n4")
    xs = [q[0] * s2 for q in poly]
    ys = [q[1] * s2 for q in poly]
    bw = (max(xs) - min(xs)) * 1.5
    lock = full.crop((int(min(xs) - bw * 0.25), int(min(ys) - bw * 0.2), int(min(xs) + bw * 1.25), int(min(ys) + bw * 0.85)))
    lock = lock.resize((520, int(520 * lock.height / lock.width)), Image.LANCZOS)
    sheet.paste(lock, (870, 560))
    img = sheet.convert("RGBA")
    K.text(img, (876, 560 + lock.height + 26), "3D: red lockdown light + holo scan-line plane", K.F(K.MONO, 18),
           O.RED, "lm", 0.3)
    img = O.eye_compass(img, 1420, 560, 135.0, 180.0)
    K.text(img, (1426, 730), "the dial (top right of every frame)", K.F(K.MONO, 16), (170, 182, 200), "lm", 0.3)
    sheet = img.convert("RGB")
    sheet = card(sheet, (1420, 780), (1080, 300), "RULE WORD: TWO READINGS (designer to pick)", [
        "Round 43 / bible 4.7 (LOCKED good-for-now): entering a room in the eye",
        "  = SPOTTED: an alarm encounter (+1 enforcer). The room stays enterable.",
        "Rounds 35 / 42 + this brief: a room in the eye is LOCKED this step.",
        "Same visual either way: red ring, eye badge, scan lines, IN THE EYE.",
        "Preset key halcyon.eye.consequence = 'spotted' | 'blocked'.",
        "The stills use 'spotted' (the locked round); the hover note shows it."], O.RED)
    sheet = card(sheet, (1420, 1100), (1080, 280), "WHY THE CHOICE IS REAL", [
        "A climb lands straight above its start (same u), the long way moves",
        "along the face: a corner-centred sector splits them (3 -> 4 is lit,",
        "3 -> 19 is dark). Every 8 steps the eye completes a turn.",
        "Max 2 climbs (round 43); a climb skips a whole turn of the spiral."], (255, 196, 60))
    sheet.save(os.path.join(ROOT, "H_scan_states.png"))
    print("saved H_scan_states.png")


if __name__ == "__main__":
    main()
