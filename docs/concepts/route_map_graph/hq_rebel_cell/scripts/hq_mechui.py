"""HQ Rebel Cell: SYNC STRIKE's 2D language for the concept options (proposal; the kit overlay calls these hooks).

RUNNERS     one token per operative on its current room, with its name in a chip edged in the operative's ACCENT
            (pink BREAKER, cyan GHOST, green RIGGER: an accent only; the route keeps lime / orange / white / grey); the
            same accent runs as a thin edge line beside that operative's walked and option wax
SWITCH      the kill switches: KILL SWITCH 1 / 2 / 3 chips; thrown: THROWN (a red stamp)
COUNTERED   the room DISPATCH has countered: the red COUNTERED stamp, STALL +1 (the runner is held a step)
SHOWDOWN    when the three are thrown together: the two that stay are PARKED (chip: SUPPORT) at their switches, the one
            that enters DISPATCH carries its token to the TARGET
SYNC dial   each operative's switch ETA (earliest-latest), the sync step, SYNC POSSIBLE / OUT OF STEP / SHOWDOWN
"""
import math

from PIL import Image, ImageDraw

import hq_graph as G
import kit44 as KT
import sidekit as S
import ui31 as K

RED = (255, 44, 52)
TINT = G.CP["tint"]
DISPATCH = {
    "start": "> ORDER 0x11. You thought I was your handler. Three switches, three of you, one step. Miss it and I re-arm.",
}


def _stamp(img, x, y, s, size=15, angle=-8):
    st = K.rubber_stamp(s, size, RED, angle=angle, seed=5, pad=6)
    img.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))
    return img


def node_mark(i, state, mech):
    if i in mech.get("countered", ()) and state in ("option", "reach", "current"):
        return dict(chip=("COUNTERED: STALL +1", RED), chip_at="below")
    if G.KIND.get(i) == "switch" and state != "grey":
        return dict(chip=("KILL SWITCH %d" % ("LCR".index(i[0]) + 1), RED), chip_at="below")
    if G.KIND.get(i) == "elite" and state in ("option", "reach"):
        return dict(chip=("MIRROR", (255, 160, 170)), chip_at="below")
    if state == "option" and i.endswith("a"):
        return dict(chip=("DETOUR +1 STEP", S.ORANGE), chip_at="below")
    return None


def _offset(pts, d):
    out = []
    for k, p in enumerate(pts):
        a = pts[max(0, k - 1)]
        b = pts[min(len(pts) - 1, k + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        out.append((p[0] - dy / L * d, p[1] + dx / L * d))
    return out


def marks(img, A, ov, mech, pose):
    import hq_overlay as O
    walked = ov["walked"]
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for e in A["edges"]:                              # the operative's accent along its walked / option wax
        es = est.get((e["a"], e["b"]))
        ln = G.LANE.get(e["b"]) or G.LANE.get(e["a"])
        if es not in ("walked", "option") or not ln:
            continue
        pts = [q for q in e["pts"] if q is not None]
        if len(pts) > 1:
            d.line(_offset(pts, 7.0), fill=tuple(TINT[ln]) + (230,), width=3, joint="curve")
    img.alpha_composite(lay)
    cur = G.lane_currents(walked)
    entered = mech.get("entered")
    for s in G.LANES:
        i = "srv" if entered == s else cur[s]
        p = O.room_poly(A, i)
        if not p:
            continue
        sc = min(1.8, O.room_scale(A, i))
        x, y = p[1][0] - 30 * sc, p[1][1] - 26 * sc
        img = S.token(img, x, y, px=int(40 * max(0.9, min(1.5, sc * 0.8))))
        lab = G.RUNNERS[s]
        if mech.get("showdown") and entered and entered != s:
            lab += "  PARKED: SUPPORT"
        elif entered == s:
            lab += "  ENTERS"
        img, box = KT.chip(img, (x + 22, y - 26), lab, (255, 230, 230), 12, anchor="lm", pad=5)
        dd = ImageDraw.Draw(img)
        dd.rectangle([box[0] - 2, box[1] - 2, box[2] + 2, box[3] + 2], outline=tuple(TINT[s]) + (255,), width=3)
    for i in mech.get("countered", ()):
        p = O.room_poly(A, i)
        if p:
            img = _stamp(img, (p[0][0] + p[1][0]) / 2, (p[0][1] + p[3][1]) / 2, "COUNTERED", 15)
    for s in mech.get("thrown", ()):
        p = O.room_poly(A, G.SWITCH[s])
        if p:
            img = _stamp(img, (p[0][0] + p[1][0]) / 2, (p[0][1] + p[3][1]) / 2 - 10, "THROWN", 14, angle=6)
    ex = ov.get("extra") or {}
    if ex.get("switch_moment"):
        img, _ = KT.chip(img, (960, 150), "ALL THREE KILL SWITCHES THROWN ON STEP %d: THE FIST LIGHTS UP" % mech["sync"], RED,
                         18, anchor="mm", pad=12)
    if ex.get("showdown"):
        img, _ = KT.chip(img, (960, 150), "SHOWDOWN: %s ENTERS DISPATCH, THE OTHER TWO HOLD THE SWITCHES"
                         % G.RUNNERS[mech.get("entered") or "C"], RED, 18, anchor="mm", pad=12)
    return img


def dial(img, x, y, mech, ov):
    x = x - 30
    box = (x, y, x + 306, y + 170)
    img = KT.term(img, box, "SYNC STRIKE", accent=RED, seed=29)
    f = K.F(K.MONO, 14)
    dd = ImageDraw.Draw(img)
    for k, s in enumerate(G.LANES):
        lo, hi = mech["eta"][s]
        yy = y + 52 + k * 24
        dd.rectangle([x + 14, yy - 6, x + 24, yy + 6], fill=tuple(TINT[s]) + (255,))
        state = "THROWN" if s in mech.get("thrown", ()) else ("step %s" % (("%d" % lo) if lo == hi else "%d-%d" % (lo, hi)))
        K.text(img, (x + 32, yy), "%-8s SWITCH %d  %s" % (G.RUNNERS[s], k + 1, state), f, (255, 210, 210), "lm", 0.2)
    if mech.get("showdown"):
        txt, col = "SHOWDOWN: ONE ENTERS", RED
    elif mech["sync_ok"]:
        txt, col = "SYNC AT STEP %d: POSSIBLE" % mech["sync"], (140, 255, 170)
    else:
        txt, col = "SYNC AT STEP %d: OUT OF STEP" % mech["sync"], RED
    K.text(img, (x + 18, y + 132), txt, K.F(K.MONO, 15), col, "lm", 0.3)
    K.text(img, (x + 18, y + 154), "a lone throw re-arms the switch", K.F(K.MONO, 12), (150, 168, 190), "lm", 0.3)
    return img


def rule_note(i, walked, mech):
    s = G.LANE.get(i)
    if not s:
        return ("DISPATCH: one operative enters; the other two hold their switches (support)", RED) if i == "srv" else None
    lo, hi = mech["eta"][s]
    if i.endswith("a"):
        return ("%s DETOUR: one more room, SWITCH %d at step %d: in step with the GHOST's stall" % (G.RUNNERS[s],
                                                                                                 "LCR".index(s) + 1, hi),
                (255, 210, 210))
    return ("%s: straight on, SWITCH %d at step %d (too early: a lone throw re-arms)" % (G.RUNNERS[s], "LCR".index(s) + 1, lo),
            (255, 210, 210))


def legend_items():
    def stampf(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([2, px * 0.3, px - 2, px * 0.7], outline=RED + (255,), width=2)
        return im

    def tints(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        for k, s in enumerate(G.LANES):
            dd.line([(2, 6 + k * (px - 12) / 2), (px - 2, 6 + k * (px - 12) / 2)], fill=tuple(TINT[s]) + (255,), width=3)
        return im
    return [(stampf, "countered"), (tints, "operatives")]


SHEET = {"title": "", "sub": "", "tiles": [], "shots": [], "cards": []}
