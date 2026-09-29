"""05 - the marker's life in three panels: write-on, drips form and pause, drips run
as the page leaves.  blender -b --factory-startup --python still_05_marker_strip.py -- <out.png>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ni_lib import *
from ni_parts import *

PW, PH, GUT, TOP = 612, 980, 22, 70


def plen(p):
    return sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(len(p) - 1))


def cut(p, L):
    out = [p[0]]; acc = 0
    for i in range(len(p) - 1):
        d = math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1])
        if acc + d >= L:
            t = (L - acc) / d if d else 0
            out.append((p[i][0] + (p[i + 1][0] - p[i][0]) * t, p[i][1] + (p[i + 1][1] - p[i][1]) * t))
            return out
        acc += d; out.append(p[i + 1])
    return out


def marker_pen(pl, x, y, hand, ang=-0.7):
    """A felt marker held at the nib (x,y), inked as a quick sketch."""
    L, w = 230, 34
    body = rot_pts([(x + 18, y - w / 2), (x + L, y - w / 2), (x + L, y + w / 2), (x + 18, y + w / 2)], x, y, ang)
    fill_poly(pl, "pen", body, "#161A24", 1)
    ink(pl, "pen", body, "white", 2.2, 1, hand, .6, closed=True)
    cap = rot_pts([(x + 18, y - w / 2), (x + 70, y - w / 2), (x + 70, y + w / 2), (x + 18, y + w / 2)], x, y, ang)
    fill_poly(pl, "pen", cap, "pink", 1)
    ink(pl, "pen", cap, "white", 1.4, 1, hand, .4, closed=True)
    nib = rot_pts([(x, y), (x + 20, y - 10), (x + 20, y + 10)], x, y, ang)
    fill_poly(pl, "pen", nib, "pink", 1)
    ink(pl, "pen", rot_pts([(x + 90, y - w / 2 + 6), (x + 200, y - w / 2 + 6)], x, y, ang), "white", 1, .5, None, 0)


def panel_base(pl, px, py, idx, title, hand):
    fill_poly(pl, "bg", rect(px, py, PW, PH), "#060913", 1)
    # a faint receding city of hairlines (context only)
    r = random.Random(idx)
    for i in range(26):
        x = px + r.uniform(0, PW); h = r.uniform(80, 320); w = r.uniform(30, 90)
        ink(pl, "city", [(x, py + PH), (x, py + PH - h), (x + w, py + PH - h - 14), (x + w, py + PH)], "#2A4058", 1.0, .5, None, 0)
    ink(pl, "frame", rect(px, py, PW, PH), "cyan", 2.0, 0.9, hand, 0.6, closed=True)
    pl.text(title, px + 20, py - 18, 22, "#F2F6FF", FONT_MONO)


def execute_button(pl, x, y, w, h, hand):
    fill_poly(pl, "panel", rect(x, y, w, h), "#050D1C", 0.95)
    ink(pl, "panel", rect(x, y, w, h), "cyan", 1.4, 0.55, hand, .4, closed=True)
    pl.text("EXECUTE", x + w / 2, y + h * 0.66, h * 0.4, "#2C5566", FONT_MONO, align="CENTER")
    for yy in range(int(y) + 6, int(y + h), 4):
        ink(pl, "scan", [(x + 4, yy), (x + w - 4, yy)], "#050D1C", 1.4, 0.55, None, 0, taper=0)


def main():
    sc = reset_scene(16)
    hand = Hand(505)
    base = Plane("base", ("bg", "city", "frame"), blur=0)
    glass = Plane("glass", ("panel", "scan", "notes"), blur=0)
    mk = Plane("marker", ("ink", "pen"), glow=False)
    notes = Plane("notes", ("n",), glow=True)
    fill_poly(base, "bg", rect(-10, -10, W + 20, H + 20), "#020308", 1)
    word = "SEND IT"
    bw, bh = 520, 190
    for idx in range(3):
        px = GUT + idx * (PW + GUT); py = TOP
        panel_base(base, px, py, idx, ["1  WRITE-ON", "2  DRIPS FORM + WAIT", "3  PAGE LEAVES, DRIPS RUN"][idx], hand)
        bx = px + (PW - bw) / 2
        by = py + 330 if idx < 2 else py + 40  # panel 3: the page is sliding up and out
        page_top = py if idx == 2 else by
        if idx == 2:
            # the page moving up: button cut by the panel top + speed lines
            fill_poly(glass, "panel", rect(bx, py + 2, bw, bh - 2 + 40), "#050D1C", 0.95)
            ink(glass, "panel", [(bx, py + 2), (bx, py + bh + 40), (bx + bw, py + bh + 40), (bx + bw, py + 2)], "cyan", 1.4, .55, hand, .4)
            glass.text("CUTE", bx + bw / 2 + 60, py + 80, bh * 0.4, "#2C5566", FONT_MONO, align="CENTER")
            for i in range(9):
                x = bx + 30 + i * 58
                ink(glass, "notes", [(x, py + bh + 70 + (i % 3) * 20), (x, py + bh + 170 + (i % 3) * 30)], "white", 1.2, .5, None, 0)
        else:
            execute_button(glass, bx, by, bw, bh, hand)
        mh = Hand(900)  # same hand each panel: the same writing, three moments
        base_y = by + 138 if idx < 2 else py + 138
        st, _ = marker_word_strokes(word, bx + 30, base_y, 92, slant=0.2, hand=Hand(77))
        strokes = [catmull(s, 6) for _, s in st]
        total = sum(plen(s) for s in strokes)
        reveal = 0.56 if idx == 0 else 1.0
        acc = 0; last = None
        for s in strokes:
            L = plen(s)
            if acc >= total * reveal:
                # ghost of the strokes still to come (panel 1 only): construction hairline
                ink(notes, "n", s, "white", 1.0, 0.25, None, 0, taper=0)
                continue
            part = s if acc + L <= total * reveal else cut(s, total * reveal - acc)
            ink(mk, "ink", part, "pink", 19, 1, mh, 0.4, w_profile=marker_profile if part is s else (lambda t: 1.05 if t < .06 else 1.0))
            last = part[-1]
            acc += L
        if idx == 0:
            marker_pen(mk, last[0], last[1], Hand(3))
            # stroke order notes (the concept artist's margin)
            glass.text("stroke by stroke, ~60 ms per stroke", px + 30, py + PH - 60, 18, "#AFC0D6", FONT_MONO)
            glass.text("ink pools where the nib lands", px + 30, py + PH - 34, 18, "#AFC0D6", FONT_MONO)
            fill_poly(mk, "ink", ellipse(strokes[0][0][0], strokes[0][0][1], 13, 12, 14), "pink", 1)
        # drip roots: the lowest points of letter strokes
        roots = []
        for s in strokes[:]:
            lo = max(s, key=lambda p: p[1])
            if lo[1] > base_y - 14:
                roots.append(lo)
        sel = []
        for p in sorted(roots):
            if all(abs(p[0] - q[0]) > 34 for q in sel):
                sel.append(p)
        roots = sel[:6]
        if idx == 1:
            for j, (x, y) in enumerate(roots):
                L = [26, 14, 38, 18, 30, 10][j]
                drip(mk, "ink", x, y - 4, L, 10, "pink", hand=Hand(40 + j), bulb=1.35)
            # the wait: a pulsing caret + note
            ink(notes, "n", [(bx + bw + 10, by + 40), (bx + bw + 10, by + 150)], "acid", 3, 1, None, 0)
            glass.text("drips grow, then HOLD", px + 30, py + PH - 86, 18, "#AFC0D6", FONT_MONO)
            glass.text("while the game waits on you", px + 30, py + PH - 60, 18, "#AFC0D6", FONT_MONO)
            glass.text("(beads swell 2%, 1.6 s loop)", px + 30, py + PH - 34, 18, "#7A889C", FONT_MONO)
        if idx == 2:
            for j, (x, y) in enumerate(roots):
                L = [640, 520, 760, 590, 700, 460][j]
                L = min(L, py + PH - 30 - y)
                drip(mk, "ink", x, y - 4, L, 11 - j % 3, "pink", hand=Hand(60 + j), bulb=1.5)
                ink(notes, "n", [(x - 16, y + L * 0.3), (x - 16, y + L * 0.3 + 70)], "white", 1, .45, None, 0)
            glass.text("the page slides up on press;", px + 30, py + PH - 60, 18, "#AFC0D6", FONT_MONO)
            glass.text("the ink keeps falling", px + 30, py + PH - 34, 18, "#AFC0D6", FONT_MONO)
    render(sc, [base, glass, notes, mk], out_path("05_marker_strip.png"), bloom=(0.25, 0.6, 0.75))


main()
