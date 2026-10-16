"""HQ Orbital: the retarget cycle's 2D language (revised after the designer's review; proposal; the kit overlay calls
these hooks).

ANTENNA     its two rooms are elite vaults: the chip ANTENNA ELITE (the dangerous part of every circuit)
ROCKET      the circuit's sabotage node: chip RETARGET n/3 (the bay doors open at the circuit's end)
OVERRIDE    the shortcut to LAUNCH CONTROL: drawn in RED PENCIL as the TARGET path, labelled LAUNCH OVERRIDE (doors
            SHUT); before the last circuit it is a dashed pencil line labelled LOCKED: RETARGET n/3
ROCKET VIEW (H_rocket): a holo readout beside the rocket: RETARGET n/3, the new target, the hacked bands
THE RETARGET CYCLE dial (top right): CIRCUIT n, RETARGET cells (3), the bay doors (SHUT / OPEN), the override state
"""
import math

from PIL import Image, ImageDraw

import hq_graph as G
import kit44 as KT
import sidekit as S
import ui31 as K

ICE = (205, 240, 255)
HOT = (255, 110, 40)
RED = (255, 44, 52)
LIME = (212, 255, 0)
TARGETS = ["ORBITAL UPLINK 3, NORTH DOCKS", "COMMONS RELAY 7, EAST MARKET", "SAT-9 (LOW ORBIT)"]
DISPATCH = {
    "start": "Orbital Commons. Every circuit ends at the rocket: retarget it onto their own uplinks. Three, then we end it.",
    "ant2": "Antenna's ours. Third retarget's done: the override's live. Fire it now, doors shut. Or run one more circuit.",
    "sw": "Doors are opening. Get to the rocket: second retarget. It hits their east market relay, not the city.",
}


def node_mark(i, state, mech):
    if i in ("ant1", "ant2") and state in ("option", "reach", "current"):
        return dict(chip=("ANTENNA ELITE", RED), chip_at="below")
    if i == "rocket" and state in ("option", "reach", "current"):
        return dict(chip=("RETARGET %d/%d" % (min(mech["retarget"] + 1, 3), mech["retargets"]), LIME), chip_at="below")
    if i == "srv" and mech.get("override"):
        return dict(chip=("LAUNCH OVERRIDE", RED), chip_at="below")
    return None


def _pen_path(img, pts, locked, label):
    pr = KT.pencil(KT.PEN_R, 377)
    pts = [p for p in pts if p is not None]
    if len(pts) < 2:
        return img
    if locked:
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(1, int(L / 26))
            for k in range(0, n, 2):
                p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                q = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                pr.stroke([p, q], width=5)
    else:
        pr.arrow(pts, width=6, head=24)
    a, b = pts[0], pts[1]
    pr.text(label, (a[0] + b[0]) / 2 - 150, (a[1] + b[1]) / 2 + 30, 24, angle=-5)
    return S.finish_pencil(img, pr)


def marks(img, A, ov, mech, pose):
    # the override path (the TARGET path) in red pencil
    path = G.edge_path("ant2", "srv")
    pts = [pose.proj(p) for p in path]
    if mech.get("override"):
        img = _pen_path(img, pts, False, "LAUNCH OVERRIDE")
    else:
        img = _pen_path(img, pts, True, "LOCKED: RETARGET %d/3" % mech["retarget"])
    if (ov.get("extra") or {}).get("rocket_view"):
        rk = G.CP["rocket"]
        p = pose.proj((0.0, 0.0, G.PH + rk["h"] * 0.55))
        if p:
            x, y = p[0] + 120, p[1] - 160
            box = (int(x), int(y), int(x + 360), int(y + 190))
            img = KT.term(img, box, "ROCKET // RETARGET", accent=LIME, seed=41)
            n = min(mech["retarget"] + 1, 3)
            K.text(img, (x + 18, y + 54), "RETARGET %d/3" % n, K.F(K.ANTON, 30), LIME, "lm", 0.5)
            d = ImageDraw.Draw(img)
            for k in range(3):
                d.rectangle([x + 200 + k * 46, y + 40, x + 238 + k * 46, y + 68], fill=(LIME + (255,)) if k < n else (30, 36, 30, 255),
                            outline=LIME + (220,), width=2)
            K.text(img, (x + 18, y + 96), "NEW TARGET:", K.F(K.MONO, 14), (180, 200, 190), "lm", 0.3)
            K.text(img, (x + 18, y + 118), TARGETS[(n - 1) % 3], K.F(K.MONO, 15), (235, 245, 235), "lm", 0.3)
            K.text(img, (x + 18, y + 146), "hacked bands lit on the hull", K.F(K.MONO, 12), (150, 168, 190), "lm", 0.3)
            K.text(img, (x + 18, y + 168), "the bay doors: OPEN", K.F(K.MONO, 12), HOT, "lm", 0.3)
            d.line([(x, y + 95), (p[0] + 10, p[1])], fill=LIME + (200,), width=2)
    return img


def dial(img, x, y, mech, ov):
    x = x - 30
    box = (x, y, x + 306, y + 170)
    img = KT.term(img, box, "THE RETARGET CYCLE", accent=ICE, seed=29)
    f = K.F(K.MONO, 14)
    K.text(img, (x + 18, y + 50), "CIRCUIT %d" % mech["circuit"], K.F(K.ANTON, 22), ICE, "lm", 0.4)
    d = ImageDraw.Draw(img)
    K.text(img, (x + 130, y + 50), "RETARGET", f, LIME, "lm", 0.3)
    for k in range(3):
        on = k < mech["retarget"]
        d.rectangle([x + 216 + k * 28, y + 41, x + 238 + k * 28, y + 59], fill=(LIME + (255,)) if on else (30, 36, 30, 255),
                    outline=LIME + (200,), width=2)
    K.text(img, (x + 18, y + 86), "BAY DOORS: " + ("OPEN (sabotage)" if mech["doors"] == "open" else "SHUT"), f,
           HOT if mech["doors"] == "open" else ICE, "lm", 0.3)
    if mech.get("override"):
        K.text(img, (x + 18, y + 116), "OVERRIDE: LIVE at the antenna", f, RED, "lm", 0.3)
        K.text(img, (x + 18, y + 138), "fire early, doors shut: HQ gone", K.F(K.MONO, 12), (255, 150, 150), "lm", 0.3)
    else:
        K.text(img, (x + 18, y + 116), "OVERRIDE: locked until 3/3", f, (150, 168, 190), "lm", 0.3)
    return img


def rule_note(i, walked, mech):
    if i == "srv":
        return ("LAUNCH OVERRIDE: fire the rocket one round early, into the SHUT bay doors: the HQ goes up. The run ends.",
                RED)
    if i == "nw":
        return ("ONE MORE CIRCUIT: the ring again (loot, fights); the override stays live at the antenna", (140, 255, 170))
    if i in ("ant1", "ant2"):
        return ("THE ANTENNA: an elite vault on a deck of the tower", RED)
    if i == "rocket":
        return ("SABOTAGE: retarget the rocket onto an Orbital site (RETARGET +1)", LIME)
    return None


def legend_items():
    def pen(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        ImageDraw.Draw(im).line([(3, px - 6), (px - 4, 6)], fill=KT.PEN_R + (255,), width=4)
        return im
    return [(pen, "override")]


SHEET = {
    "title": "ORBITAL COMMONS  //  THE RETARGET CYCLE: the antenna, the rocket and the override (design-language proposal)",
    "sub": "Row 1: rooms of the decision render in each state (the real overlay code). Every circuit climbs the antenna "
           "(two elite vaults) and ends at the rocket; after 3 retargets the override fires it into the shut doors.",
    "tiles": [("OPTION: ONE MORE CIRCUIT", "nw", "option", S.ORANGE), ("CURRENT: ANTENNA DECK 2", "ant2", "current", S.LIME),
              ("WALKED: ANTENNA DECK 1", "ant1", "walked", S.LIME), ("AHEAD", "sw", "reach", S.WHITE),
              ("THE OVERRIDE (TARGET)", "srv", "option", RED), ("THE PAD (walked)", "start", "walked", S.LIME)],
    "shots": [("S_ring", ["Circuit 2 starts: the PAD, the SE dish;", "the doors SHUT, the override LOCKED."]),
              ("S_antenna", ["The antenna tower: deck 1 (elite) cleared,", "deck 2's vault next: the dangerous part."]),
              ("S_sabotage", ["SW dish: the bay doors OPEN, the rocket rises:", "RETARGET 2/3 (the launch board follows)."])],
    "cards": [("THE RETARGET CYCLE  (designer review on round 43's missile loop)", [
        "A circuit: PAD > SE > NE > ANTENNA deck 1 > deck 2 > NW > SW > ROCKET.",
        "The bay doors stay SHUT; at the circuit's end they OPEN, the rocket",
        "rises and the Cell RETARGETS it: it strikes an Orbital facility in the",
        "city or a satellite (the launch cutscene: H_launch_board).",
        "After 3 retargets the antenna's top room unlocks the LAUNCH OVERRIDE:",
        "fire the rocket one round early into the shut doors: the HQ is",
        "destroyed, the run is won (a planned cutscene)."], ICE, 1020),
        ("WHAT IS REAL (GDD) AND WHAT IS PROPOSED", [
            "GDD 11.7: Orbital's Central Server is LAUNCH CONTROL (8.4d: 'the",
            "Commons Array'; round 43: 'the missile bay'): names flagged.",
            "GDD win = breach the final server (1.3): here the breach IS the",
            "override at LAUNCH CONTROL. Retargeting, strikes on Orbital sites",
            "and destroying the HQ are the review's story: not in the GDD.",
            "Camera: front and centre on the active room, orbiting the ring."], (140, 200, 255), 1030)],
}
