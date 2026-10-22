"""Concept M, round 10: MANHUNT on the Invisible, Inc. model (calibration, REVIEW_CALIBRATION.md: certain local
information, unknown escalation). Rules = M9c (ghost2.py, scarce levers); each a designer decision. Changes from M9c,
all from the R9 and calibration critics:
- LOCAL forecast: per sealed candidate, a thumbnail of WHICH nodes that line would find (red) - no computed net and no
  best reaction (the critic: "the forecast hands you the best reaction"). The key bar shows the loss range (best..worst
  candidate) as a hatched segment.
- Candidate lines are told apart by SHAPE (triangle / square / diamond end caps and dash patterns), never numbers;
  numbers are only beam order (1, 2, 3).
- The cause is on screen: run nodes -> Heat -> the cobalt notch -> contact, drawn as a chain, not in a caption.
- Each lever shows its effect and its own currency: ghost = dashed ring, costs Heat (flame); decoy = diamond that stops a
  beam, costs Schematics (coin); go dark = black disc, costs next income (struck coin).
- The hunter rule is drawn as a glyph (first find -> turn down its column).
- The ledger reconciles: the coin is the key bar's change; evading shows its own reward; DOWN nodes carry a wrench.
Every number is ghost2.py output for network concept_m9_base.SEED."""
from __future__ import annotations

from r2_kit import *  # noqa: F403
import concept_m9_base as B
import ghost2 as G2
from ghost import H, NODES, W

NAME = "M10 MANHUNT r10"
MOMENTS = ["1_contact", "2_plan", "3_forecast", "4_playout", "5_aftermath"]
_, ALLOC = B.best_both()
REACT = B.react_plan(ALLOC)
SPOOF = REACT[B.REVEAL][0]
SHAPES = ("tri", "sq", "dia")
DASH = ((18, 8), (6, 6), (14, 4))


def shape(d, c, kind, r=11, col=THREAT_LIGHT, fill=None):
    x, y = c
    if kind == "tri":
        pts = [(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)]
    elif kind == "sq":
        pts = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    else:
        pts = [(x, y - r * 1.2), (x + r, y), (x, y + r * 1.2), (x - r, y)]
    d.polygon(pts, outline=col, fill=fill, width=3)


def dashed_line(d, a, b, col, dash, width=4):
    import math
    length = math.dist(a, b)
    on, off = dash
    n = 0.0
    while n < length:
        e = min(length, n + on)
        d.line([(a[0] + (b[0] - a[0]) * n / length, a[1] + (b[1] - a[1]) * n / length),
                (a[0] + (b[0] - a[0]) * e / length, a[1] + (b[1] - a[1]) * e / length)], fill=col, width=width)
        n = e + off


def cand_line(d, i, faded=False, lit=False):
    ln = B.CANDS[i]
    a, b = B.nx(ln[0]), B.nx(ln[-1])
    ax, ay = a[0] - (B.nx(ln[1])[0] - a[0]) * 0.45, a[1] - (B.nx(ln[1])[1] - a[1]) * 0.45
    bx, by = b[0] + (b[0] - B.nx(ln[-2])[0]) * 0.4, b[1] + (b[1] - B.nx(ln[-2])[1]) * 0.4
    col = (50, 60, 110) if faded else (THREAT if lit else THREAT_LIGHT)
    if lit:
        arrow(d, (ax, ay), (bx, by), col, width=6, shorten=0)
    else:
        dashed_line(d, (ax, ay), (bx, by), col, DASH[i], 4)
    shape(d, (ax, ay), SHAPES[i], 12, col, fill=BG)


def hunter_glyph(d, x, y):
    """first find (red ring) -> turn down its column (dashed arrow): the hunter rule as a picture."""
    d.ellipse((x - 10, y - 10, x + 10, y + 10), outline=DMG, width=3)
    dashed_line(d, (x, y + 14), (x, y + 60), THREAT_LIGHT, (8, 5), 4)
    d.polygon([(x - 7, y + 56), (x + 7, y + 56), (x, y + 68)], fill=THREAT_LIGHT)
    order_badge(d, (x + 26, y + 34), 3)


def lever_tray(d, x, y, alloc, spoof_left=True):
    g, dk, dc = alloc
    panel(d, (x, y, x + 360, y + 150))
    # ghost: dashed ring, +Heat
    for a in range(0, 360, 30):
        d.arc((x + 22, y + 20, x + 66, y + 64), a, a + 15, fill=CELL if g else DIM, width=3)
    flame(d, (x + 36, y + 98), 8, HEAT)
    text(d, (x + 48, y + 88), f"+{G2.GHOST_HEAT}", 16, HEAT, "mono")
    # decoy: diamond with a stopped beam, -coin
    cx = x + 140
    d.line([(cx - 44, y + 42), (cx - 24, y + 42)], fill=THREAT, width=5)
    d.line([(cx - 22, y + 30), (cx - 22, y + 54)], fill=CELL, width=4)
    d.polygon([(cx + 4, y + 20), (cx + 26, y + 42), (cx + 4, y + 64), (cx - 18, y + 42)], outline=CELL if dc else DIM, width=3)
    coin(d, (cx - 6, y + 98), 7, CELL)
    text(d, (cx + 4, y + 88), f"-{G2.DECOY_COST}", 16, CELL, "mono")
    # go dark: black disc, struck income coin
    cx = x + 235
    d.ellipse((cx - 22, y + 20, cx + 22, y + 64), fill=(10, 10, 16), outline=DIM, width=3)
    coin(d, (cx - 6, y + 98), 7, DIM)
    d.line([(cx - 16, y + 108), (cx + 4, y + 88)], fill=DMG, width=3)
    text(d, (cx + 8, y + 88), f"x{len(dk)}", 16, INK, "mono")
    # spoof: one press held
    cx = x + 315
    d.rounded_rectangle((cx - 26, y + 28, cx + 26, y + 56), radius=5, outline=STAMP_CLEAN if spoof_left else DIM, width=3)
    d.line([(cx - 10, y + 42), (cx + 10, y + 42)], fill=STAMP_CLEAN if spoof_left else DIM, width=3)
    text(d, (cx, y + 88), "x1" if spoof_left else "x0", 16, INK, "mono", anchor="ma")


def base_net(d, alloc, found=(), down=()):
    for c in NODES:
        B.node(d, c, alloc, found)
        if c in down:
            x, y = B.nx(c)
            d.line([(x + 18, y + 18), (x + 34, y + 34)], fill=DMG, width=5)
            d.ellipse((x + 28, y + 28, x + 40, y + 40), outline=DMG, width=3)
    g, dk, dc = alloc
    stop1 = next((c for c in B.B1 if c in dc), None)
    B.beam(d, B.B1, 1, upto=stop1)


def thumb(d, x, y, i, alloc):
    """A 4 x 3 thumbnail: which nodes candidate i would find (red), hidden assets (dashed), evaded = teal check."""
    panel(d, (x, y, x + 150, y + 118), r=6)
    shape(d, (x + 18, y + 18), SHAPES[i], 9, THREAT_LIGHT)
    f = B.found_by(alloc, B.CANDS[i])
    for c in NODES:
        cx, cy = x + 40 + c[0] * 28, y + 30 + c[1] * 28
        v = B.ASSETS.get(c)
        if v is None:
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(50, 54, 80))
        elif c in f:
            d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=DMG)
        else:
            d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), outline=CELL, width=2)
    if not f:
        check(d, (x + 130, y + 18), 10, STAMP_CLEAN)
    return sum(B.ASSETS[c] for c in f)


def key_range(d, x, y, have, lo, hi):
    w = 360
    d.rounded_rectangle((x, y, x + w, y + 18), radius=6, fill=(30, 34, 56), outline=PANEL_EDGE, width=2)
    fw = int(w * have / B.KEY)
    d.rounded_rectangle((x, y, x + fw, y + 18), radius=6, fill=CELL)
    for lose, col in ((hi, (120, 40, 48)), (lo, DMG)):
        lw = int(w * min(lose, have) / B.KEY)
        for xx in range(x + fw - lw, x + fw, 6):
            d.line([(xx, y + 2), (xx + 4, y + 16)], fill=col, width=2)
    d.regular_polygon((x + w + 22, y + 9, 14), 6, outline=THREAT_LIGHT, fill=(40, 30, 70))
    text(d, (x + w + 44, y - 2), f"{have}/{B.KEY}", 18, INK, "mono")


def cause_chain(d):
    """Run nodes -> Heat -> notch -> contact, drawn."""
    for i in range(4):
        x = 70 + i * 46
        d.ellipse((x - 14, 600 - 14, x + 14, 600 + 14), outline=CELL, width=3)
        check(d, (x, 600), 7, CELL)
    arrow(d, (250, 600), (320, 600), HEAT, width=4, shorten=0)
    flame(d, (350, 604), 14, HEAT)
    arrow(d, (380, 600), (450, 600), HEAT, width=4, shorten=0)
    shield(d, (480, 596), 16, THREAT)
    arrow(d, (510, 600), (580, 600), THREAT, width=4, shorten=0)
    d.rectangle((600, 584, 632, 616), outline=THREAT_LIGHT, width=3)


def f1():
    img, d = new_frame(NAME, "contact")
    B.contact_hud(d)
    base_net(d, ((), (), ()))
    cause_chain(d)
    header(d, NAME, 1, "Contact: the nodes you ran raised Heat past the notch; the front reaches your network (assets = your haul)")
    return img


def f2():
    img, d = new_frame(NAME, "plan")
    B.contact_hud(d)
    base_net(d, ALLOC)
    for i in range(3):
        cand_line(d, i)
    hunter_glyph(d, 760, 470)
    lever_tray(d, 860, 90, ALLOC)
    header(d, NAME, 2, "Plan: beam 1 is shown; beam 2 is one of three shapes (sealed); beam 3 hunts the first find's column; one ghost, one decoy, go dark, one spoof held")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    B.contact_hud(d)
    base_net(d, ALLOC)
    for i in range(3):
        cand_line(d, i)
    losses = [thumb(d, 760 + i * 165, 110, i, ALLOC) for i in range(3)]
    key_range(d, 760, 270, B.KEY_HAVE, min(losses), max(losses))
    lever_tray(d, 860, 340, ALLOC)
    header(d, NAME, 3, f"Forecast (local): what each sealed line would find with this plan (red); key at risk {min(losses)}-{max(losses)}; the spoof is held for after the reveal")
    return img


def f4():
    img, d = new_frame(NAME, "playout")
    B.contact_hud(d)
    base_net(d, ALLOC)
    for i in range(3):
        cand_line(d, i, faded=i != B.REVEAL, lit=i == B.REVEAL)
    x, y = B.nx(SPOOF[1])
    d.ellipse((x - 42, y - 42, x + 42, y + 42), outline=STAMP_CLEAN, width=4)
    step_track(d, 760, 470, 400, 3, 2, "BEAM")
    speed_controls(d, 760, 510)
    d.rounded_rectangle((760, 570, 1160, 620), radius=10, fill=(40, 44, 70), outline=CELL, width=3)
    d.rectangle((760 + 170, 574, 760 + 230, 616), fill=STAMP_CLEAN)
    lever_tray(d, 860, 90, ALLOC)
    header(d, NAME, 4, "Playout: the triangle line unseals; you aim the held spoof at the node it threatens (teal ring) and press in the window")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    b2 = B.CANDS[B.REVEAL]
    found = B.found_by(ALLOC, b2, SPOOF)
    B.contact_hud(d)
    base_net(d, ALLOC, found=found, down=found)
    B.beam(d, b2, 2)
    loss = sum(B.ASSETS[c] for c in found)
    stamp(img, (1040, 170), "CELL HOLDS", STAMP_HOLD if found else STAMP_CLEAN, 50,
          sub=f"{len(found)} DOWN" if found else "EVADED")
    B.key_bar(d, 760, 300, B.KEY_HAVE, lose=loss)
    coin(d, (780, 370), 12)
    text(d, (800, 356), f"-{loss}" if loss else f"+{G2.EVADE}", 26, DMG if loss else STAMP_CLEAN, "mono")
    lever_tray(d, 860, 430, ALLOC, spoof_left=False)
    header(d, NAME, 5, f"Aftermath: {len(found)} DOWN (wrench: stays down until repaired); the repair {loss} comes off the key ({B.KEY_HAVE} -> {B.KEY_HAVE - loss})")
    return img


FRAMES = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    print("alloc", ALLOC, "spoof", SPOOF, "react", REACT)
