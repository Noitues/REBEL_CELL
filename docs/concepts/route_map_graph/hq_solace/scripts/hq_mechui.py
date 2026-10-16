"""HQ Solace: the ladder's 2D language (redesign 2026-10-15; proposal; the kit overlay calls these hooks).

UP / ACROSS every option carries its move: UP (the same tower, the next route floor) or ACROSS (the floor's skybridge to
            the other tower). Ring colours stay the locked state colours.
UNREAD      a room more than `read_ahead` route floors above you: its kind is hidden: a frosted disc with '?' and the
            chip UNREAD; in 3D its room is frosted and dim (round 43 decision 'semi-random sets' + the read rule).
THE SEQUENCE dial (top right): the ladder from your floor up: towers A and B as columns, the read rooms' kind icons,
            '?' for unread, the rungs (bridges), HEIGHT n %.
"""
from PIL import Image, ImageDraw

import hq_graph as G
import kit44 as KT
import r32ui as U32
import sidekit as S
import ui31 as K

FROST = (170, 210, 190)
DISPATCH = {
    "start": "Solace Biosystems. Two towers, one bridge a floor. Climb or cross. You only read two floors ahead.",
    "B3": "Tower B, floor 6. Up reads an event; across is a fight on A. Above floor 10, nothing's read yet.",
    "A1": "Ground floor. Up, or over the bridge to tower B.",
}


def _unread_sticker(img, x, y, px, alpha):
    S2 = 3
    P = px * S2
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([3 * S2, 3 * S2, P - 3 * S2, P - 3 * S2], fill=(36, 48, 44, int(235 * alpha)),
              outline=FROST + (int(255 * alpha),), width=3 * S2)
    d.text((P / 2, P / 2 + S2), "?", font=K.F(K.ANTON, int(P * 0.55)), fill=FROST + (int(255 * alpha),), anchor="mm")
    im = im.resize((px, px), Image.LANCZOS)
    img.alpha_composite(im, (int(x - px / 2), int(y - px / 2)))
    return img


def _move(i, walked):
    cur = walked[-1]
    if cur not in G.TOWER or i not in G.TOWER:
        return None
    return "ACROSS" if G.TOWER[i] != G.TOWER[cur] else "UP"


CUR_WALK = []


def node_mark(i, state, mech):
    if i in mech.get("unread", ()) and state in ("reach", "grey"):
        return dict(sticker_fn=_unread_sticker, chip=("UNREAD", FROST) if mech.get("zoom", 1.0) > 0.5 else None,
                    chip_at="below")
    if state == "option" and mech.get("walked"):
        mv = _move(i, mech["walked"])
        if mv:
            return dict(chip=(mv, S.ORANGE), chip_at="below")
    return None


def marks(img, A, ov, mech, pose):
    return img


def dial(img, x, y, mech, ov):
    CUR_WALK[:] = ov["walked"]
    x = x - 30
    box = (x, y, x + 306, y + 196)
    img = KT.term(img, box, "THE SEQUENCE", accent=(200, 230, 210), seed=29)
    walked = ov["walked"]
    lv = G.LEVEL.get(walked[-1], 0)
    cols = {"A": x + 62, "B": x + 150}
    d = ImageDraw.Draw(img)
    K.text(img, (cols["A"], y + 44), "A", K.F(K.ANTON, 18), (230, 236, 240), "mm", 0)
    K.text(img, (cols["B"], y + 44), "B", K.F(K.ANTON, 18), (230, 236, 240), "mm", 0)
    for r in range(5):
        level = lv + r
        if level < 1 or level > G.NL:
            continue
        yy = y + 178 - r * 27
        d.line([(cols["A"] + 12, yy), (cols["B"] - 12, yy)], fill=(120, 140, 130, 255), width=2)
        for t in ("A", "B"):
            i = "%s%d" % (t, level)
            if i in walked:
                d.ellipse([cols[t] - 10, yy - 10, cols[t] + 10, yy + 10], outline=S.LIME + (255,), width=3)
                if i == walked[-1]:
                    d.ellipse([cols[t] - 5, yy - 5, cols[t] + 5, yy + 5], fill=S.LIME + (255,))
            elif i in mech.get("unread", ()):
                d.ellipse([cols[t] - 10, yy - 10, cols[t] + 10, yy + 10], outline=FROST + (255,), width=2)
                K.text(img, (cols[t], yy), "?", K.F(K.MONO, 13), FROST, "mm", 0)
            else:
                img.alpha_composite(U32.icon(G.KIND[i], 22), (int(cols[t] - 11), int(yy - 11)))
    K.text(img, (x + 196, y + 70), "read:", K.F(K.MONO, 13), (200, 230, 210), "lm", 0.2)
    K.text(img, (x + 196, y + 88), "2 floors", K.F(K.MONO, 13), (200, 230, 210), "lm", 0.2)
    K.text(img, (x + 196, y + 106), "ahead", K.F(K.MONO, 13), (200, 230, 210), "lm", 0.2)
    K.text(img, (x + 196, y + 150), "HEIGHT %d%%" % int(round(100 * mech.get("height", 0))), K.F(K.MONO, 14),
           (230, 236, 240), "lm", 0.3)
    return img


def rule_note(i, walked, mech):
    mv = _move(i, walked)
    if mv == "ACROSS":
        return ("ACROSS: the floor's skybridge to tower %s (%s). Then up tower %s, or back over a higher bridge"
                % (G.TOWER[i], G.WORD[G.KIND[i]], G.TOWER[i]), (230, 236, 240))
    if mv == "UP":
        return ("UP: tower %s, the next route floor (%s)" % (G.TOWER[i], G.WORD[G.KIND[i]]), (230, 236, 240))
    return None


def legend_items():
    def unread(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        return _unread_sticker(im, px / 2, px / 2, px - 2, 1.0)
    return [(unread, "unread")]


SHEET = {
    "title": "SOLACE BIOSYSTEMS  //  THE LADDER: up or across, and the read rule (design-language proposal)",
    "sub": "Row 1: rooms of the decision render in each state (the real overlay code). Two floors above you are read; "
           "higher rooms are UNREAD: kind hidden ('?'), frosted and dim in 3D.",
    "tiles": [("OPTION: UP", "B4", "option", S.ORANGE), ("OPTION: ACROSS", "A3", "option", S.ORANGE),
              ("CURRENT", "B3", "current", S.LIME), ("AHEAD (READ)", "B5", "reach", S.WHITE),
              ("UNREAD", "B6", "reach", FROST), ("WALKED", "B2", "walked", S.LIME)],
    "shots": [("S_ground_floor", ["Floor 2 (the first route floor): up tower A,", "or across the bridge to tower B."]),
              ("S_mid_climb", ["Floor 10 on tower A after crossing at 10:", "up only (the room across is walked)."]),
              ("S_top", ["Floor 16: the last rooms; the crown joins the", "towers: THE GENOME CORE."])],
    "cards": [("THE LADDER  (designer redesign; round 43 Solace adapted)", [
        "Two twisting towers, a bow-tie skybridge on every floor (the DNA rungs).",
        "Route floors 2, 4 .. 16 on both towers (16 rooms). From a room: UP the same",
        "tower, or ACROSS that floor's bridge. No room twice: a crossing is",
        "one-way per floor. The towers meet in the crown: THE GENOME CORE.",
        "Round 43 decision: each tower's rooms are a SEMI-RANDOM set (seeded).",
        "READ rule (proposal): 2 route floors ahead are read; above, '?'."], (200, 230, 210), 1020),
        ("WHAT IS REAL (GDD) AND WHAT IS PROPOSED", [
            "GDD 11.7: Solace's Central Server is THE GENOME CORE (8.3 / App. A",
            "call the final server / boss the Renewal Engine: flagged).",
            "Not in the GDD: the towers, the ladder, the read rule (all proposals).",
            "Bible 2.4: Solace lime never on a link or a ring: it stays in the 3D",
            "(the atrium slots, window tints); the overlay keeps the state colours.",
            "Camera: the orbit-and-rise (faces the options' floor, rises with it)."], (140, 200, 255), 1030)],
}
