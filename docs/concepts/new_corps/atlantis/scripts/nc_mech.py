"""New corps: the HQ mechanic sheets (PROPOSALS): the visual states of THE TURNING GATES (Aurelian) and THE BALLAST
TIDE (Tethys), drawn as step-by-step schematics in the locked overlay grammar (state rings, node stickers, wax links,
yellow pencil telegraph one step ahead, de-power / re-make). Identical copy in both scripts/ folders.

python nc_mech.py <aurelian|tethys>
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nc_kit as K  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import sidekit as S  # noqa: E402

U, SL = K.U, K.SL
W, H = 2560, 1440
S.W, S.H = W, H                                   # the sidekit layers follow this sheet size
KT.W, KT.H = W, H
LIME, ORANGE, WHITE, GREY = S.LIME, S.ORANGE, S.WHITE, S.GREY
VERD = (41, 219, 166)
ABYSS = (47, 107, 255)
REDW = (255, 90, 110)


def panel(img, box, title, accent):
    img = U.term_panel(img, box, title=title, accent=accent, seed=hash(title) % 97, hexbg=False, glow=0.2)
    return img


def wax(img, pts, col, w=6, dashed=False):
    pen = KT.pencil(col, 11 + len(pts))
    if dashed:
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            n = max(1, int(L / 22))
            for k in range(n):
                if k % 2 == 0:
                    t0, t1 = k / n, (k + 1) / n
                    pen.stroke([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], width=w)
    else:
        pen.stroke(pts, width=w)
    return KT.ink(img, pen)


def link(img, a, b, st):
    d = ImageDraw.Draw(img)
    if st == "walked":
        d.line([a, b], fill=(8, 6, 14, 255), width=12)
        d.line([a, b], fill=LIME + (255,), width=7)
    elif st == "option":
        d.line([a, b], fill=(8, 6, 14, 255), width=12)
        d.line([a, b], fill=ORANGE + (255,), width=7)
    elif st == "closed":                                         # de-powered: dark red, broken, two sparks
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for p, q in ((a, (a[0] + (m[0] - a[0]) * 0.75, a[1] + (m[1] - a[1]) * 0.75)), ((b[0] + (m[0] - b[0]) * 0.75, b[1] + (m[1] - b[1]) * 0.75), b)):
            d.line([p, q], fill=(110, 30, 40, 255), width=6)
        for s in (-1, 1):
            d.line([(m[0] + s * 6, m[1] - 8), (m[0] + s * 14, m[1] - 18)], fill=(255, 200, 120, 255), width=2)
    elif st == "remade":                                         # re-made: drawn on from the source, bright head
        d.line([a, b], fill=(8, 6, 14, 255), width=12)
        d.line([a, b], fill=WHITE + (255,), width=6)
        d.ellipse([b[0] - 9, b[1] - 9, b[0] + 9, b[1] + 9], fill=(255, 255, 255, 255))
    else:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / 16))
        for k in range(0, n, 2):
            t0, t1 = k / n, min(1, (k + 1) / n)
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=WHITE + (210,), width=4)
    return img


def node(img, x, y, kind, st, px=34, num=None):
    col = {"walked": LIME, "current": LIME, "option": ORANGE, "ahead": WHITE, "past": GREY}[st]
    img = S.ring(img, x, y, px * 0.62, col, 4)
    img = S.sticker(img, kind, x, y, int(px * 0.9), grey=st == "past")
    if num:
        img = S.number_chip(img, int(x - px * 0.7), int(y - px * 0.7), num)
    if st == "current":
        img = S.token(img, x + px * 0.6, y - px * 0.7, px=28)
    return img


# ------------------------------------------------------------------ AURELIAN: the turning gates
def aurelian():
    import roman_preset as RP
    Q = RP.PRESET["hq"]
    img = K.board(W, H, top=(30, 12, 24), bot=(4, 4, 8), seed=3)
    tt = K.word_sticker(["HQ MECHANIC"], 60, U.FILL_YELLOW, seed=5)
    img = SL.place(img, tt, 230, 70, angle=-2)
    U.text(img, (450, 70), "THE TURNING GATES  //  Circus Aurelius  //  PROPOSAL (not a GDD rule)", U.F(U.MONO, 24), (226, 230, 238), "lm", 1)
    radii = [262, 198, 136, 78]
    steps = 4
    walked_path = [[(0, 0), (0, 1), (0, 2)], [(0, 0), (0, 1), (0, 2), (1, 2)], [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)],
                   [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (2, 2)]]
    for s in range(steps):
        x0 = 30 + s * 632
        box = (x0, 130, x0 + 610, 860)
        img = panel(img, box, "STEP %d" % (s + 1), VERD)
        cx, cy = x0 + 305, 610
        d = ImageDraw.Draw(img)
        for i, r in enumerate(radii):
            d.ellipse([cx - r, cy - r * 0.82, cx + r, cy + r * 0.82], outline=(90, 74, 50, 255), width=3)
        # gates per ring at this step
        gpos = {}
        for i in range(4):
            gs = [(g + Q["gate_step"][i] * (s - 2)) % 360 for g in Q["gates_now"][i]]   # step 3 = the overview's state
            gpos[i] = gs
            r = radii[i] - 24
            for g in gs:
                a = math.radians(g)
                gx, gy = cx + r * math.cos(a), cy - r * 0.82 * math.sin(a)
                d.rectangle([gx - 9, gy - 9, gx + 9, gy + 9], fill=VERD + (255,), outline=(8, 20, 16, 255), width=2)
            # the next step's openings: yellow pencil telegraph
        img2 = img
        for i in range(4):
            r = radii[i] - 24
            for g in Q["gates_now"][i]:
                gn = (g + Q["gate_step"][i] * (s - 1)) % 360
                a = math.radians(gn)
                gx, gy = cx + r * math.cos(a), cy - r * 0.82 * math.sin(a)
                if 20 < gn < 160:
                    pen = KT.pencil(S.PEN_Y, 31 + i + s)
                    pen.circle(gx, gy, 16, 12, width=4)
                    img2 = KT.ink(img2, pen)
        img = img2
        # rooms (far half) and links
        P = {}
        for i, angs in enumerate(Q["rooms"]):
            r = radii[i]
            for j, ad in enumerate(angs):
                a = math.radians(ad)
                P[(i, j)] = (cx + r * math.cos(a), cy - r * 0.82 * math.sin(a))
        wp = walked_path[s]
        cur = wp[-1]
        for i, angs in enumerate(Q["rooms"]):
            for j in range(len(angs) - 1):
                st = "walked" if ((i, j) in wp and (i, j + 1) in wp) else "ahead"
                img = link(img, P[(i, j)], P[(i, j + 1)], st)
        opts = []
        for i in range(3):
            for j, ad in enumerate(Q["rooms"][i]):
                open_ = any(abs(((ad - g + 180) % 360) - 180) < 13 for g in gpos[i])
                jb = min(range(len(Q["rooms"][i + 1])), key=lambda q: abs(Q["rooms"][i + 1][q] - ad))
                st = "ahead" if open_ else "closed"
                if (i, j) in wp and (i + 1, jb) in wp:
                    st = "walked"
                if (i, j) == cur and open_:
                    st = "option"
                    opts.append((i + 1, jb))
                img = link(img, P[(i, j)], P[(i + 1, jb)], st)
        if cur[1] + 1 < len(Q["rooms"][cur[0]]):
            opts.insert(0, (cur[0], cur[1] + 1))
            img = link(img, P[cur], P[(cur[0], cur[1] + 1)], "option")
        kinds = ["router", "terminal", "router", "elite", "modem", "router", "rack"]
        for (i, j), p in P.items():
            st = "walked" if (i, j) in wp else "ahead"
            if (i, j) == cur:
                st = "current"
            num = None
            if (i, j) in opts:
                st, num = "option", opts.index((i, j)) + 1
            img = node(img, p[0], p[1], kinds[(i * 3 + j) % 7], st, 27, num)
        pen = KT.pencil(S.PEN_R, 90 + s)
        pen.circle(cx, cy, 30, 22, width=5)
        img = KT.ink(img, pen)
        cap = ["Ring 1 gate stands at room 3: the drop is open.", "Dropped. Ring 2's gates turn CCW; one stands at room 4.",
               "Walked one room; the gate turned to meet us.", "Down again. Ring 3's gate is two bays away: wait or walk."][s]
        for k, ln in enumerate(K.wrap(cap, 52)):
            U.text(img, (x0 + 24, 172 + k * 26), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    # the visual states row
    y0 = 900
    img = K.section(img, (40, y0), "VISUAL STATES", "the same grammar on the map, in the overview and in the HQ room view", VERD)
    cells = [("GATE OPEN", "lit verdigris jambs, the stair down; the link is a normal route link"),
             ("GATE SHUT", "bronze barrier; the link de-powers (dark red, 2 sparks)"),
             ("NEXT STEP", "yellow pencil ring where a gate will stand after this step"),
             ("RE-MADE", "a link that opens is drawn on from its source, bright head"),
             ("THE ROSTRUM", "red pencil TARGET; reachable only from ring 4")]
    for k, (t, s_) in enumerate(cells):
        x = 60 + k * 500
        yy = y0 + 110
        if k == 0:
            ImageDraw.Draw(img).rectangle([x + 20, yy - 20, x + 60, yy + 20], fill=VERD + (255,), outline=(8, 20, 16, 255), width=3)
        elif k == 1:
            img = link(img, (x, yy), (x + 120, yy), "closed")
        elif k == 2:
            pen = KT.pencil(S.PEN_Y, 5)
            pen.circle(x + 40, yy, 26, 18, width=5)
            img = KT.ink(img, pen)
        elif k == 3:
            img = link(img, (x, yy), (x + 120, yy), "remade")
        else:
            pen = KT.pencil(S.PEN_R, 6)
            pen.circle(x + 40, yy, 30, 22, width=6)
            img = KT.ink(img, pen)
        U.text(img, (x, yy + 50), t, U.F(U.ANTON, 30), (240, 240, 244), "la", 1)
        for j, ln in enumerate(K.wrap(s_, 40)):
            U.text(img, (x, yy + 94 + j * 24), ln, U.F(U.PLEX, 18), (190, 200, 214), "la", 0)
    img = U.term_panel(img, (40, 1230, 2520, 1420), title="RULE (PROPOSAL, round 43 style)", accent=VERD, seed=7)
    rule = ["Four seating rings, rooms on each (6, 5, 4, 3 = 18 + THE ROSTRUM). Walking along a ring is always open. Each ring has a bronze gate ring",
            "with two gates; every step each gate ring turns one bay (rings alternate CW / CCW, preset gate_step). You can drop to the next ring only",
            "where a gate stands at your room. The next step's gates are pencilled one step ahead, so waiting (walking a room) is a real plan, never a gamble.",
            "Tie to the house rule: a drop taken on a Perfect-landing turn could skip the next room's fight (designer question)."]
    for k, ln in enumerate(rule):
        U.text(img, (62, 1282 + k * 32), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    return img


# ------------------------------------------------------------------ TETHYS: the ballast tide
def tethys():
    import tethys_preset as TP
    Q = TP.PRESET["hq"]
    img = K.board(W, H, top=(6, 16, 40), bot=(2, 4, 10), seed=4)
    tt = K.word_sticker(["HQ MECHANIC"], 60, U.FILL_YELLOW, seed=5)
    img = SL.place(img, tt, 230, 70, angle=-2)
    U.text(img, (450, 70), "THE BALLAST TIDE  //  ATLANTIS STATION  //  PROPOSAL (not a GDD rule)", U.F(U.MONO, 24), (226, 230, 238), "lm", 1)
    names = ["LOW", "RISING", "HIGH", "FALLING"]
    levels = [0.08, 0.40, 0.66, 0.40]           # water level as a fraction of the station height (decks 5 .. 1)
    decks = Q["decks"]
    n = len(decks)
    for s in range(4):
        x0 = 30 + s * 632
        box = (x0, 130, x0 + 610, 860)
        img = panel(img, box, "STEP %d  //  TIDE %s" % (s + 1, names[s]), ABYSS)
        top, bot = 210, 740
        ys = [top + (bot - top) * i / (n - 1) for i in range(n)]
        lvl_y = bot + 30 - (bot - top + 60) * levels[s]
        nxt_y = bot + 30 - (bot - top + 60) * levels[(s + 1) % 4]
        d = ImageDraw.Draw(img)
        # water (the ballast) behind everything below the line
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle([x0 + 20, lvl_y, x0 + 590, bot + 60], fill=(30, 80, 220, 90))
        img.alpha_composite(lay)
        d = ImageDraw.Draw(img)
        for xx in range(x0 + 20, x0 + 590, 6):
            d.line([(xx, lvl_y + 4 * math.sin(xx / 9)), (xx + 6, lvl_y + 4 * math.sin((xx + 6) / 9))], fill=(150, 210, 255, 255), width=3)
        # decks
        xr = {}
        for i, (z, cnt) in enumerate(decks):
            y = ys[i]
            d.rounded_rectangle([x0 + 50, y - 12, x0 + 560, y + 12], radius=12, outline=(110, 130, 160, 255), width=2)
            for j in range(cnt):
                xx = x0 + 90 + j * (430 / max(1, cnt - 1)) if cnt > 1 else x0 + 305
                xr[(i, j)] = (xx, y)
        # drop tubes: open above the water, flooded below it; the airlock alternates (open on odd steps)
        drops = []
        for i in range(n - 1):
            for k, (dx, st0) in enumerate(Q["drops"][i]):
                fx = (dx + Q["deck_len"] / 2) / Q["deck_len"]
                xx = x0 + 50 + fx * 510
                ytop, ybot = ys[i] + 14, ys[i + 1] - 14
                st = "airlock" if st0 == "airlock" else ("flooded" if ybot > lvl_y + 4 else "open")
                if st == "airlock" and s % 2 == 1:
                    st = "airlock_shut"
                drops.append((i, xx, ytop, ybot, st))
                col = {"open": (124, 242, 228), "flooded": (60, 110, 255), "airlock": REDW, "airlock_shut": (120, 60, 70)}[st]
                d.rectangle([xx - 8, ytop, xx + 8, ybot], outline=col + (255,), width=3)
                if st == "flooded":
                    d.rectangle([xx - 6, ytop + 2, xx + 6, ybot - 2], fill=(60, 110, 255, 200))
                if st.startswith("airlock"):
                    ym = (ytop + ybot) / 2
                    d.ellipse([xx - 14, ym - 14, xx + 14, ym + 14], outline=col + (255,), width=4)
                    if st == "airlock_shut":
                        d.line([(xx - 10, ym - 10), (xx + 10, ym + 10)], fill=col + (255,), width=4)
                # will it flood next step? pencil it
                if st == "open" and ybot > nxt_y + 4:
                    pen = KT.pencil(S.PEN_Y, 40 + i + s)
                    pen.circle(xx, (ytop + ybot) / 2, 20, 30, width=4)
                    img = KT.ink(img, pen)
                    d = ImageDraw.Draw(img)
        kinds = ["router", "terminal", "router", "elite", "modem", "router", "rack"]
        for (i, j), p in xr.items():
            if j + 1 in [jj for (ii, jj) in xr if ii == i]:
                img = link(img, p, xr[(i, j + 1)], "ahead")
        for (i, xx, ytop, ybot, st) in drops:
            ja = min([j for (ii, j) in xr if ii == i], key=lambda j: abs(xr[(i, j)][0] - xx))
            jb = min([j for (ii, j) in xr if ii == i + 1], key=lambda j: abs(xr[(i + 1, j)][0] - xx))
            img = link(img, xr[(i, ja)], xr[(i + 1, jb)], "closed" if st in ("flooded", "airlock_shut") else "ahead")
        for (i, j), p in xr.items():
            img = node(img, p[0], p[1], kinds[(i * 2 + j) % 7], "ahead", 30)
        pen = KT.pencil(S.PEN_Y, 70 + s)
        pen.stroke([(x0 + 570, nxt_y), (x0 + 600, nxt_y)], width=5)
        pen.text("NEXT", x0 + 560, nxt_y - 22, 18, angle=-4)
        img = KT.ink(img, pen)
        pen = KT.pencil(S.PEN_R, 80 + s)
        pen.circle(x0 + 305, bot + 50, 26, 16, width=5)
        img = KT.ink(img, pen)
        cap = ["All drops dry. The fast way down is open; the airlock cycles.", "The water climbs to deck 4: those drops flood, pencilled a step ahead.",
               "High tide: only the top decks connect. Walk the deck and wait.", "Falling: the lower drops drain again; the airlock is open."][s]
        for k, ln in enumerate(K.wrap(cap, 52)):
            U.text(img, (x0 + 24, 790 + k * 26), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    y0 = 900
    img = K.section(img, (40, y0), "VISUAL STATES", "the same grammar in the overview (hq_overview.png) and the room view", ABYSS)
    cells = [("DRY", "a lit tube, a dive-light strip: a normal link"), ("FLOODED", "water fills the tube; the link de-powers"),
             ("FLOODS NEXT", "yellow pencil ring on a dry tube the tide will reach"), ("AIRLOCK", "red hatch ring; cycles every other step"),
             ("WATERLINE", "the ballast column's glowing line + the NEXT pencil mark")]
    for k, (t, s_) in enumerate(cells):
        x = 60 + k * 500
        yy = y0 + 110
        d = ImageDraw.Draw(img)
        if k == 0:
            d.rectangle([x + 20, yy - 30, x + 40, yy + 30], outline=(124, 242, 228, 255), width=3)
        elif k == 1:
            d.rectangle([x + 20, yy - 30, x + 40, yy + 30], outline=(60, 110, 255, 255), width=3)
            d.rectangle([x + 22, yy - 28, x + 38, yy + 28], fill=(60, 110, 255, 220))
        elif k == 2:
            pen = KT.pencil(S.PEN_Y, 7)
            pen.circle(x + 30, yy, 22, 34, width=5)
            img = KT.ink(img, pen)
        elif k == 3:
            d.ellipse([x + 14, yy - 16, x + 46, yy + 16], outline=REDW + (255,), width=4)
        else:
            d.line([(x, yy), (x + 100, yy)], fill=(150, 210, 255, 255), width=5)
        U.text(img, (x, yy + 50), t, U.F(U.ANTON, 30), (240, 240, 244), "la", 1)
        for j, ln in enumerate(K.wrap(s_, 40)):
            U.text(img, (x, yy + 94 + j * 24), ln, U.F(U.PLEX, 18), (190, 200, 214), "la", 0)
    img = U.term_panel(img, (40, 1230, 2520, 1420), title="RULE (PROPOSAL, round 43 style)", accent=ABYSS, seed=8)
    rule = ["Five pressure decks (5, 4, 4, 3, 2 = 18 rooms + THE BLACK SMOKER at the vent). Walking along a deck is always open. The station's ballast",
            "water cycles LOW > RISING > HIGH > FALLING, one step per move; a drop tube below the waterline is FLOODED (closed). Airlocks ignore the tide",
            "but are open only every other step. The tide is the same four-step cycle the combat house rule uses (TIDE), so the HUD shows one clock for both.",
            "The tide that will flood a dry tube is pencilled one step ahead: waiting is a plan. Designer question: can you swim a flooded drop for HP?"]
    for k, ln in enumerate(rule):
        U.text(img, (62, 1282 + k * 32), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    return img


if __name__ == "__main__":
    corp = sys.argv[1]
    img = aurelian() if corp == "aurelian" else tethys()
    K.save(img, os.path.join(K.NC, K.CORPS[corp]["folder"], "hq_mechanic.png"))
