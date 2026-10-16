"""HQ Meridian: the yard cycle's 2D language (proposal; the kit overlay calls these hooks).

RIDE        a room on a mover (the train's CAR, the crane's HOOK): a yellow-black hazard badge on its sticker (a loco /
            a hook glyph) and the chip ON THE TRAIN / ON THE CRANE when it is on offer or ahead. Its ring stays in the
            locked state colour (orange = on offer now).
NOW ONLY    a boarding link that exists this step only (the mover moves next step): an orange "NOW ONLY" chip on it.
NEXT MOVE   the mover's position one step ahead, in yellow pencil (bible PENCIL_PLAN #FFE200, round 43's telegraph):
            a ring round where it will be + a pencil arrow from where it is.
THE YARD CYCLE dial (top right): the 6-step clock (now filled, next dashed), what the train and the crane do now and
            next, "train leaves in n".
"""
import math

from PIL import Image, ImageDraw

import hq_graph as G
import hq_cam as CR
import kit44 as KT
import sidekit as S
import ui31 as K

HAZ = (255, 200, 20)
INK = (14, 12, 10)
TRAIN_W = {"arrive": "ARRIVING", "west": "IN, WEST END", "east": "IN, EAST END", "leave": "LEAVING", "gone": "GONE"}
CRANE_W = {"yard": "OVER THE YARD", "swing": "SWINGING OUT", "wall": "AT THE WALL"}
DISPATCH = {
    "start": "Meridian Freight. The yard runs on a clock: train in, shunt, out. The crane swings with it.",
    "n1": "Train's in under you. Ride it east to the tower, or walk on and catch the hook at the crane.",
    "n2": "Walking. The hook's coming over the wall. Be at the crane when it lands.",
    "n3": "Hook's at the wall. Grab it: it swings you into the yard, right under Control.",
    "car": "You're on the car. It shunts east: step off at the tower before it leaves.",
    "hook": "Hold on. Yard side, Control's face. Step off at the top floor.",
}


def _badge(kind):
    cache = {}

    def f(px):
        if px in cache:
            return cache[px]
        S2 = 4
        P = px * S2
        im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([2 * S2, 2 * S2, P - 2 * S2, P - 2 * S2], fill=HAZ + (255,), outline=INK + (255,), width=3 * S2)
        # hazard ticks on the rim
        for k in range(8):
            a = math.radians(k * 45 + 22)
            r0, r1 = P * 0.40, P * 0.47
            d.line([(P / 2 + r0 * math.cos(a), P / 2 + r0 * math.sin(a)), (P / 2 + r1 * math.cos(a), P / 2 + r1 * math.sin(a))],
                   fill=INK + (255,), width=2 * S2)
        if kind == "train":
            d.rectangle([P * 0.22, P * 0.36, P * 0.70, P * 0.60], fill=INK + (255,))
            d.rectangle([P * 0.52, P * 0.26, P * 0.70, P * 0.40], fill=INK + (255,))
            d.polygon([(P * 0.70, P * 0.36), (P * 0.80, P * 0.60), (P * 0.70, P * 0.60)], fill=INK + (255,))
            for x in (0.30, 0.46, 0.62):
                d.ellipse([P * (x - 0.06), P * 0.58, P * (x + 0.06), P * 0.70], fill=INK + (255,))
        else:
            d.line([(P * 0.5, P * 0.18), (P * 0.5, P * 0.55)], fill=INK + (255,), width=int(P * 0.07))
            d.arc([P * 0.30, P * 0.42, P * 0.70, P * 0.80], 0, 200, fill=INK + (255,), width=int(P * 0.08))
            d.rectangle([P * 0.38, P * 0.14, P * 0.62, P * 0.22], fill=INK + (255,))
        cache[px] = im.resize((px, px), Image.LANCZOS)
        return cache[px]
    return f


BADGE = {"car": _badge("train"), "hook": _badge("hook")}
CHIP = {"car": "ON THE TRAIN", "hook": "ON THE CRANE"}


def node_mark(i, state, mech):
    if i in BADGE and state != "grey":
        return dict(badge=BADGE[i], chip=(CHIP[i], HAZ) if state in ("option", "reach", "current") else None,
                    chip_at="below")
    return None


def _centre(poly):
    return (sum(q[0] for q in poly) / 4, sum(q[1] for q in poly) / 4)


def marks(img, A, ov, mech, pose):
    walked = ov["walked"]
    mt = A.get("mt", len(walked) - 1)
    st, opts = G.states(walked, int(mt))
    pr = KT.pencil(KT.PEN_Y, 611)
    drew = False
    if ov.get("extra", {}).get("no_telegraph"):
        return img
    for m in ("car", "hook"):
        if st.get(m) in ("grey", "walked") and m not in walked[-1:]:
            continue
        now = [pose.proj(p) for p in G.room_front(m, mt)]
        nxt = [pose.proj(p) for p in G.room_front(m, int(mt) + 1)]
        if any(q is None for q in now + nxt):
            continue
        c0, c1 = _centre(now), _centre(nxt)
        if math.hypot(c1[0] - c0[0], c1[1] - c0[1]) < 20:
            continue
        rx = abs(nxt[1][0] - nxt[0][0]) / 2 + 22
        ry = abs(nxt[0][1] - nxt[3][1]) / 2 + 18
        word = "NEXT: SHUNTS EAST" if m == "car" and mech.get("train_next") == "east" else (
            "NEXT: HOOK AT THE WALL" if m == "hook" and mech.get("crane_next") == "wall" else (
                "NEXT: INTO THE YARD" if m == "hook" else "NEXT: LEAVES"))
        if not (0 < c1[0] < 1920 and 0 < c1[1] < 1080):
            # off screen: a pencil arrow from the mover toward where it goes, the word at its head
            if not (0 < c0[0] < 1920 and 0 < c0[1] < 1080):
                continue
            dx, dy = c1[0] - c0[0], c1[1] - c0[1]
            L = math.hypot(dx, dy)
            a0 = (c0[0] + dx / L * 70, c0[1] + dy / L * 40 - 40)
            a1 = (c0[0] + dx / L * 260, c0[1] + dy / L * 120 - 40)
            pr.arrow([a0, ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2 - 18), a1], width=5, head=20)
            pr.text(word, (a0[0] + a1[0]) / 2, min(a0[1], a1[1]) - 34, 24, angle=-4)
            drew = True
            continue
        pr.circle(c1[0], c1[1], rx, ry, width=6)
        # the arrow from now to next, stopping short of both
        dx, dy = c1[0] - c0[0], c1[1] - c0[1]
        L = math.hypot(dx, dy)
        a0 = (c0[0] + dx / L * 60, c0[1] + dy / L * 50)
        a1 = (c1[0] - dx / L * (rx + 8), c1[1] - dy / L * (ry + 8))
        if math.hypot(a1[0] - a0[0], a1[1] - a0[1]) > 40:
            mid = ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2 - 0.12 * L)
            pr.arrow([a0, mid, a1], width=5, head=20)
        word = "NEXT: SHUNTS EAST" if m == "car" and mech.get("train_next") == "east" else (
            "NEXT: HOOK AT THE WALL" if m == "hook" and mech.get("crane_next") == "wall" else (
                "NEXT: INTO THE YARD" if m == "hook" else "NEXT: LEAVES"))
        pr.text(word, c1[0], c1[1] - ry - 22, 26, angle=-4)
        drew = True
    if drew:
        img = S.finish_pencil(img, pr, col=KT.PEN_Y)
    # NOW ONLY on boarding links that vanish next step
    nxt_edges = set(G.base_edges(walked, int(mt) + 1))
    for e in A["edges"]:
        if e["b"] in ("car", "hook") and e["a"] == walked[-1] and (e["a"], e["b"]) not in nxt_edges:
            pts = [q for q in e["pts"] if q]
            if len(pts) >= 2:
                q = pts[len(pts) // 2]
                img, _ = KT.chip(img, (q[0] + 12, q[1]), "NOW ONLY", S.ORANGE, 13, anchor="lm", pad=6)
    return img


def dial(img, x, y, mech, ov):
    x = x - 30
    box = (x, y, x + 306, y + 170)
    img = KT.term(img, box, "THE YARD CYCLE", accent=HAZ, seed=29)
    cx, cy, r = x + 58, y + 98, 40
    i, j = mech["idx"], mech["idx_next"]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for k in range(6):
        a0, a1 = -90 + k * 60 + 3, -90 + (k + 1) * 60 - 3
        bb = [cx - r, cy - r, cx + r, cy + r]
        if k == i:
            ld.pieslice(bb, a0, a1, fill=HAZ + (220,))
        elif k == j:
            ld.arc(bb, a0, a1, fill=HAZ + (200,), width=5)
        else:
            ld.arc(bb, a0, a1, fill=(120, 130, 140, 200), width=3)
    ld.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(10, 10, 14, 255), outline=(150, 160, 170, 255), width=2)
    img.alpha_composite(lay)
    K.text(img, (cx, cy), str(i + 1), K.F(K.ANTON, 20), HAZ, "mm", 0)
    f = K.F(K.MONO, 13)
    tx = x + 112
    K.text(img, (tx, y + 50), "NOW  TRAIN " + TRAIN_W[mech["train"]], f, HAZ, "lm", 0.2)
    K.text(img, (tx, y + 68), "     CRANE " + CRANE_W[mech["crane"]], f, HAZ, "lm", 0.2)
    K.text(img, (tx, y + 94), "NEXT TRAIN " + TRAIN_W[mech["train_next"]], f, (255, 236, 150), "lm", 0.2)
    K.text(img, (tx, y + 112), "     CRANE " + CRANE_W[mech["crane_next"]], f, (255, 236, 150), "lm", 0.2)
    if mech.get("leave_in"):
        K.text(img, (tx, y + 140), "train leaves in %d" % mech["leave_in"], K.F(K.MONO, 12), (150, 168, 190), "lm", 0.3)
    K.text(img, (tx, y + 156), "rides %d / %d" % (mech.get("rides", 0), G.CP["max_shortcuts"]), K.F(K.MONO, 12),
           (150, 168, 190), "lm", 0.3)
    return img


def rule_note(i, walked, mech):
    if i == "car":
        return ("RIDE THE TRAIN: next step it shunts to the NE tower (skips 3). Leaves in %d: still aboard = "
                "ejected at the gate, Heat +1" % mech.get("leave_in", 0), HAZ)
    if i == "hook":
        return ("RIDE THE HOOK: next step it swings into the yard, beside Control's top floor (skips 3)", HAZ)
    return ("WALK THE RAMPART: the hook reaches the wall by the crane in 2 steps", (140, 255, 170))


def legend_items():
    def ringy(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=KT.PEN_Y + (255,), width=4)
        return im
    return [(BADGE["car"], "ride"), (ringy, "next move")]


SHEET = {
    "title": "MERIDIAN FREIGHT  //  THE YARD CYCLE: rides, telegraphs and room states (design-language proposal)",
    "sub": "Row 1: rooms of the decision render in each state (the real overlay code). A ride = a room on a mover: hazard "
           "badge + ON THE TRAIN / ON THE CRANE; yellow pencil = where it goes next.",
    "tiles": [("OPEN (next)", "n2", "option", S.ORANGE), ("RIDE ON OFFER", "car", "option", S.ORANGE),
              ("CURRENT", "n1", "current", S.LIME), ("AHEAD", "n3", "reach", S.WHITE),
              ("WALKED", "t1", "walked", S.LIME), ("PAST", "n4", "grey", S.GREY)],
    "shots": [("S_on_the_train", ["STEP 7  the train shunts east with you aboard:", "step off at the NE tower (n2-n4 skipped)."]),
              ("S_hook_at_wall", ["STEP 8  the hook hangs at the wall by the crane:", "board it from n3, NOW ONLY."]),
              ("S_hook_in_yard", ["STEP 9  the crane swings it into the yard:", "step off at Control's top floor."])],
    "cards": [("THE YARD CYCLE  (round 43 crane / train cycle, adapted)", [
        "6 steps: train ARRIVES / IN WEST / SHUNTS EAST / IN EAST / LEAVES / GONE;",
        "crane: YARD / SWINGS OUT / AT THE WALL x2 / INTO THE YARD x2.",
        "Rooms ride the movers (round 43: nodes ride the crane and the train).",
        "Boarding exists only while the mover is beside you (NOW ONLY);",
        "a ride skips 3 rooms. Max 1 ride a run (proposal; preset key).",
        "Still aboard when the train LEAVES: ejected at the gate, Heat +1",
        "(round 43 open question; proposal)."], HAZ, 1020),
        ("WHAT IS REAL (GDD) AND WHAT IS PROPOSED", [
            "GDD 11.7: the boss Site is Meridian's Central Server, THE MASTER",
            "MANIFEST (8.4b still says 'The Manifest': flagged). Netrun = GDD 4.2.",
            "Not in the GDD: the HQ compound, the yard cycle, rides, ejection.",
            "Bible 4.4: container fortress, gantry crane keep, rail yard, train.",
            "Visual language here: hazard badge, ride chips, NOW ONLY, yellow",
            "pencil telegraph (round 43), the cycle dial. Route colours unchanged."], (140, 200, 255), 1030)],
}
