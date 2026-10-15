"""New corps: plates + the locked route overlay (stickers, wax links, TARGET, the page chrome) for the HQ overview and
the Site street, plus the HQ mechanic sheets. Identical copy in both scripts/ folders.

The overlay is drawn at 1920 x 1080 on a clear layer with the locked kit (hq_halcyon/scripts: sidekit, kit44, ui31),
upscaled 1.33x and laid on the 2560 x 1440 plate (the r3 method). Anchors come from the render's JSON (projected
room centres), so every sticker sits on its room. Graph states follow the netrun grammar: walked lime solid, the
options orange with number chips, ahead white dashed, closed links grey and broken.

python nc_compose.py <aurelian|tethys> <hq|street|mechanic> [plate=<npy>] [json=<json>]
"""
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nc_kit as K  # noqa: E402  (puts the locked kit on sys.path)
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import kit44 as KT  # noqa: E402
import sidekit as S  # noqa: E402
import nc_post  # noqa: E402

U, SL = K.U, K.SL
W1, H1 = 1920, 1080
LIME, ORANGE, WHITE, GREY = S.LIME, S.ORANGE, S.WHITE, S.GREY
STATE_COL = {"walked": LIME, "current": LIME, "option": ORANGE, "ahead": WHITE, "past": GREY, "target": WHITE}
KIND_CYCLE = ["router", "terminal", "router", "elite", "modem", "router", "rack"]


def load_anchors(path, res):
    A = json.load(open(path))
    sx, sy = W1 / res[0], H1 / res[1]
    return {k: (v[0] * sx, v[1] * sy) for k, v in A.items()}


def plate_of(npy, look, out_png, exposure=None, media=1.0):
    exposure = exposure if exposure is not None else (0.6 if look == "deep" else 1.0)
    nc_post.finish(npy, out_png, look=look, exposure=exposure, media=media)
    return Image.open(out_png).convert("RGBA").resize((2560, 1440), Image.LANCZOS)


# ------------------------------------------------------------------ route drawing
def draw_route(ov, A, nodes, edges, px=40, number=True):
    cab = S.Cables()
    for (a, b, st, via) in edges:
        if a not in A or b not in A:
            continue
        pts = [A[a]] + [A[v] for v in via if v in A] + [A[b]]
        if st == "walked":
            cab.solid(pts, LIME, 7, glow=0)
        elif st == "option":
            cab.solid(pts, ORANGE, 7)
        elif st == "past":
            cab.dashed(pts, GREY, 4, on=10, off=10, a=150)
        elif st == "closed":
            # de-powered: grey, broken in the middle
            mid = len(pts) // 2
            p0, p1 = pts[0], pts[-1]
            m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            cab.dashed([p0, (p0[0] + (m[0] - p0[0]) * 0.8, p0[1] + (m[1] - p0[1]) * 0.8)], GREY, 5, on=10, off=6)
            cab.dashed([(p1[0] + (m[0] - p1[0]) * 0.8, p1[1] + (m[1] - p1[1]) * 0.8), p1], GREY, 5, on=10, off=6)
        else:
            cab.dashed(pts, WHITE, 5, on=14, off=10, a=200)
    ov = cab.comp(ov)
    n_opt = 0
    for name, nd in nodes.items():
        if name not in A:
            continue
        x, y = A[name]
        st = nd["state"]
        if st == "target":
            continue
        col = STATE_COL[st]
        r = px * 0.62
        ov = S.ring(ov, x, y, r, col, 4 if st != "past" else 3, alpha=1.0 if st != "past" else 0.6)
        ov = S.sticker(ov, nd["kind"], x, y, int(px * 0.92), grey=(st == "past"), alpha=1.0 if st != "ahead" else 0.92)
        if st == "option" and number:
            n_opt += 1
            ov = S.number_chip(ov, int(x - r - 8), int(y - r - 6), nd.get("num", n_opt))
        if st == "current":
            ov = S.token(ov, x + r * 0.9, y - r * 1.1, px=34)
    return ov


def target(ov, A, key, word_dx=0, word_dy=-70, r=(46, 40)):
    x, y = A[key]
    pr = S.target_pencil(x, y, r[0], r[1], (x + word_dx, y + word_dy))
    return S.finish_pencil(ov, pr)


def chip(ov, xy, s, col):
    ov, _ = KT.chip(ov, xy, s, col, 14, anchor="mm", pad=8)
    return ov


def route_panel(ov, n_opts, lines):
    box = (14, 150, 300, 386)
    ov = KT.term(ov, box, "ROUTE", seed=23)
    f = U.F(U.MONO, 14)
    for i, ln in enumerate(lines):
        U.text(ov, (30, 194 + i * 18), ln, f, (205, 218, 230), "lm", 0.3)
    ov = U.term_button(ov, (30, 262, 284, 300), "CONFIRM", None, state="disabled")
    ov = U.term_button(ov, (30, 306, 284, 342), "GRID VIEW", None)
    ov = U.term_button(ov, (30, 348, 284, 380), "Save & quit", None)
    return ov


def mech_panel(ov, title, rows, accent):
    box = (1560, 140, 1906, 140 + 40 + 24 * len(rows))
    ov = KT.term(ov, box, title, accent=accent, seed=31)
    for i, (k, v, c) in enumerate(rows):
        U.text(ov, (1578, 190 + i * 24), k, U.F(U.MONO, 15), (150, 170, 190), "lm", 0.5)
        U.text(ov, (1700, 190 + i * 24), v, U.F(U.MONO, 15), c, "lm", 0.5)
    return ov


def finish(plate, ov, path):
    big = ov.resize((2560, 1440), Image.LANCZOS)
    out = plate.copy()
    out.alpha_composite(big)
    out.convert("RGB").save(path)
    print("wrote", path)
    return out


# ------------------------------------------------------------------ AURELIAN: the Circus Aurelius
def aur_graph(P):
    Q = P["hq"]
    rooms = Q["rooms"]
    nodes, edges = {}, []
    k = 0
    order = []
    for i, angs in enumerate(rooms):
        js = list(range(len(angs)))
        for j in js:
            order.append((i, j))
    cur = tuple(Q["current"])
    for (i, j) in order:
        name = "room_%d_%d" % (i, j)
        kind = KIND_CYCLE[(i * 3 + j) % len(KIND_CYCLE)]
        st = "ahead"
        if i == cur[0] and j < cur[1]:
            st = "walked"
        if (i, j) == cur:
            st = "current"
        nodes[name] = dict(kind=kind, state=st)
    # along-ring links
    for i, angs in enumerate(rooms):
        for j in range(len(angs) - 1):
            a, b = "room_%d_%d" % (i, j), "room_%d_%d" % (i, j + 1)
            st = "walked" if (i == cur[0] and j + 1 <= cur[1]) else "ahead"
            edges.append((a, b, st, []))
    # gate drops: from ring i room j to the ring i+1 room nearest each gate opening (open now) or closed
    open_gates = []
    for i in range(len(rooms) - 1):
        for g in Q["gates_now"][i]:
            ja = min(range(len(rooms[i])), key=lambda j: abs(((rooms[i][j] - g + 180) % 360) - 180))
            jb = min(range(len(rooms[i + 1])), key=lambda j: abs(((rooms[i + 1][j] - g + 180) % 360) - 180))
            if abs(((rooms[i][ja] - g + 180) % 360) - 180) > 20:
                continue
            gate = "gate_%d_%d" % (i, g)
            edges.append(("room_%d_%d" % (i, ja), "room_%d_%d" % (i + 1, jb), "ahead", [gate]))
            open_gates.append((i, ja, i + 1, jb, gate))
    # closed (shut) drops: every other room pair with no gate this step
    for i in range(len(rooms) - 1):
        for j, ad in enumerate(rooms[i]):
            if any(o[0] == i and o[1] == j for o in open_gates):
                continue
            if j % 2 == 0:
                jb = min(range(len(rooms[i + 1])), key=lambda q: abs(rooms[i + 1][q] - ad))
                edges.append(("room_%d_%d" % (i, j), "room_%d_%d" % (i + 1, jb), "closed", []))
    # the options from the current room: along the ring + the open gate down (if one sits at the current room)
    num = 1
    nxt = "room_%d_%d" % (cur[0], cur[1] + 1)
    nodes[nxt]["state"], nodes[nxt]["num"] = "option", num
    edges = [(a, b, "option" if (a == "room_%d_%d" % cur and b == nxt) else s, v) for (a, b, s, v) in edges]
    for (i, ja, i2, jb, gate) in open_gates:
        if (i, ja) == cur:
            num += 1
            b = "room_%d_%d" % (i2, jb)
            nodes[b]["state"], nodes[b]["num"] = "option", num
            edges = [(a, bb, "option" if (a == "room_%d_%d" % cur and bb == b) else s, v) for (a, bb, s, v) in edges]
    last = len(rooms) - 1
    edges.append(("room_%d_%d" % (last, len(rooms[last]) // 2), "server", "ahead", []))
    nodes["server"] = dict(kind="rack", state="target")
    return nodes, edges


def aur_hq(npy, js, res):
    import roman_preset as RP
    P = RP.PRESET
    plate = plate_of(npy, "night", os.path.join(K.SCR, "roman_hq_plate.png"))
    A = load_anchors(js, res)
    nodes, edges = aur_graph(P)
    ov = Image.new("RGBA", (W1, H1), (0, 0, 0, 0))
    # gate state marks: open gates = verdigris chips, the next-step gate = yellow pencil telegraph
    pen = KT.pencil(S.PEN_Y, 77)
    for k, v in A.items():
        if k.startswith("gate_"):
            i = int(k.split("_")[1])
            g = int(k.split("_")[2])
            if 0 < g < 180 and i == 0:
                ov = chip(ov, (v[0] - 70, v[1] + 24), "GATE OPEN", (41, 219, 166))
    nxt_ring = 1
    g_now = P["hq"]["gates_now"][nxt_ring][0]
    g_next = (g_now + P["hq"]["gate_step"][nxt_ring]) % 360
    ri = P["hq"]["rings"][nxt_ring][1]
    fz = P["hq"]["rings"][nxt_ring][2]
    # project the next opening from the two gate anchors on that ring (interpolate in screen space by angle)
    ov = draw_route(ov, A, nodes, edges)
    if "gate_1_%d" % g_now in A:
        x, y = A["gate_1_%d" % g_now]
        tx, ty = x + 120, y + 30
        pen.circle(tx, ty, 34, 22, width=7)
        pen.arrow([(x + 10, y), (x + 60, y + 18), (tx - 36, ty)], width=6, head=16)
        pen.text("NEXT STEP: GATE TURNS HERE", tx + 10, ty + 48, 22, angle=-3)
    ov = KT.ink(ov, pen)
    ov = target(ov, A, "server", word_dx=90, word_dy=-60, r=(60, 52))
    ov = chip(ov, (A["server"][0] + 190, A["server"][1] + 40), "CENTRAL SERVER: THE ROSTRUM", (255, 90, 90))
    ov = S.chrome_top(ov, "Gate's open under you now. Go down, or walk the ring and catch the next turn. Rostrum's in the middle.")
    ov = route_panel(ov, 2, ["PICK A ROOM: 1 walks the", "ring, 2 drops through the", "open gate. Keys 1-2."])
    ov = mech_panel(ov, "THE TURNING GATES", [("STEP", "3 of a 4-step turn", (240, 240, 244)), ("RING 1", "gates 100 / 280  CW", (41, 219, 166)),
                                              ("RING 2", "gates 60 / 240  CCW", (41, 219, 166)), ("RING 3", "gates 118 / 298  CW", (41, 219, 166)),
                                              ("RING 4", "gates 80 / 260  CCW", (41, 219, 166)), ("RULE", "drop only where aligned", (255, 214, 64))],
                    (41, 219, 166))
    ov = S.legend(ov, cx=960)
    return finish(plate, ov, os.path.join(K.NC, "roman", "hq_overview.png"))


# ------------------------------------------------------------------ TETHYS: ATLANTIS STATION
def teth_graph(P):
    Q = P["hq"]
    decks = Q["decks"]
    cur = tuple(Q["current"])
    nodes, edges = {}, []
    Ld = Q["deck_len"]
    xs = {}
    for i, (z, n) in enumerate(decks):
        for j in range(n):
            x = -Ld / 2 + 18 + j * (Ld - 36) / max(1, n - 1) if n > 1 else 0.0
            xs[(i, j)] = x
            st = "ahead"
            if i < cur[0] or (i == cur[0] and j < cur[1]):
                st = "walked" if (i == cur[0] or (i == 0)) else "past"
            if (i, j) == cur:
                st = "current"
            nodes["room_%d_%d" % (i, j)] = dict(kind=KIND_CYCLE[(i * 2 + j) % len(KIND_CYCLE)], state=st)
        for j in range(n - 1):
            a, b = "room_%d_%d" % (i, j), "room_%d_%d" % (i, j + 1)
            st = "walked" if nodes[a]["state"] in ("walked",) and nodes[b]["state"] in ("walked", "current") else "ahead"
            edges.append((a, b, st, []))
    # walked so far: deck 0 left to right, down the first drop
    drops = Q["drops"]
    for i, dl in enumerate(drops):
        for (x, st) in dl:
            ja = min(range(decks[i][1]), key=lambda j: abs(xs[(i, j)] - x))
            jb = min(range(decks[i + 1][1]), key=lambda j: abs(xs[(i + 1, j)] - x))
            e_st = "closed" if st == "flooded" else "ahead"
            edges.append(("room_%d_%d" % (i, ja), "room_%d_%d" % (i + 1, jb), e_st, ["drop_%d_%d" % (i, int(x))]))
    # the walked path: deck 0 rooms 0..2 then the open drop at -64 to deck 1 room 0, then room 1 (current)
    walked = ["room_0_0", "room_0_1", "room_1_0", "room_1_1"]
    for n_ in ("room_0_0", "room_0_1", "room_1_0"):
        nodes[n_]["state"] = "walked"
    for k in ("room_0_2", "room_0_3", "room_0_4"):
        nodes[k]["state"] = "past"
    new = []
    for (a, b, s, v) in edges:
        if (a, b) in (("room_0_0", "room_0_1"), ("room_0_1", "room_1_0"), ("room_1_0", "room_1_1")):
            s = "walked"
        if a == "room_0_1" and b == "room_1_0":
            s = "walked"
        new.append((a, b, s, v))
    edges = new
    walked_set = {"room_0_0", "room_0_1", "room_1_0", "room_1_1"}
    edges = [(a, b, ("walked" if (a in walked_set and b in walked_set) else ("past" if s == "walked" else s)), v) for (a, b, s, v) in edges]
    if not any(a == "room_0_1" and b == "room_1_0" for a, b, _, _ in edges):
        edges.append(("room_0_1", "room_1_0", "walked", ["drop_0_-64"]))
    # options: along the deck (room_1_2) and the airlock drop at -48 to deck 2
    nodes["room_1_2"].update(state="option", num=1)
    nodes["room_2_1"].update(state="option", num=2)
    edges = [(a, b, "option" if (a == "room_1_1" and b == "room_1_2") else s, v) for (a, b, s, v) in edges]
    edges.append(("room_1_1", "room_2_1", "option", ["drop_1_-48"]))
    last = len(decks) - 1
    edges.append(("room_%d_0" % last, "server", "ahead", []))
    nodes["server"] = dict(kind="rack", state="target")
    return nodes, edges


def teth_hq(npy, js, res):
    import tethys_preset as TP
    P = TP.PRESET
    plate = plate_of(npy, "deep", os.path.join(K.SCR, "atlantis_hq_plate.png"))
    A = load_anchors(js, res)
    nodes, edges = teth_graph(P)
    ov = Image.new("RGBA", (W1, H1), (0, 0, 0, 0))
    ov = draw_route(ov, A, nodes, edges)
    for k, v in A.items():
        if k.startswith("drop_"):
            i, x = int(k.split("_")[1]), int(k.split("_")[2])
            st = dict((int(xx), s) for xx, s in P["hq"]["drops"][i])[x]
            col = {"open": (124, 242, 228), "flooded": (90, 140, 255), "airlock": (255, 90, 110)}[st]
            ov = chip(ov, (v[0] + 58, v[1]), {"open": "DRY", "flooded": "FLOODED", "airlock": "AIRLOCK"}[st], col)
    pen = KT.pencil(S.PEN_Y, 79)
    tx, ty = A["tide"]
    nx, ny = A["tide_next"]
    pen.stroke([(tx - 40, ty), (tx + 40, ty)], width=7)
    pen.stroke([(nx - 40, ny), (nx + 40, ny)], width=5)
    pen.arrow([(tx + 54, ty - 4), (tx + 70, (ty + ny) / 2), (nx + 50, ny + 6)], width=6, head=16)
    pen.text("NEXT: RISING", nx + 30, ny - 30, 24, angle=-4)
    ov = KT.ink(ov, pen)
    ov = target(ov, A, "server", word_dx=110, word_dy=-30, r=(70, 50))
    ov = chip(ov, (A["server"][0] - 240, A["server"][1] - 10), "CENTRAL SERVER: THE BLACK SMOKER", (255, 90, 90))
    ov = S.chrome_top(ov, "Tide's coming up two decks. Airlock's slow but it's dry. Or walk the deck and wait it out.")
    ov = route_panel(ov, 2, ["PICK A ROOM: 1 walks the", "deck, 2 cycles the airlock", "down. Keys 1-2."])
    ov = mech_panel(ov, "THE BALLAST TIDE", [("CYCLE", "LOW RISE HIGH FALL", (240, 240, 244)), ("NOW", "RISING (deck 3)", (90, 140, 255)),
                                             ("NEXT", "HIGH (deck 2)", (255, 214, 64)), ("DRY", "open drop", (124, 242, 228)),
                                             ("FLOODED", "closed this step", (90, 140, 255)), ("AIRLOCK", "open, +1 step", (255, 90, 110))],
                    (47, 107, 255))
    ov = S.legend(ov, cx=960)
    return finish(plate, ov, os.path.join(K.NC, "atlantis", "hq_overview.png"))


# ------------------------------------------------------------------ the Site street (both)
STREET_EDGES = [("S", "L1_0"), ("L1_0", "L2_0"), ("L1_0", "L2_1"), ("L2_0", "L3_0"), ("L2_1", "L3_1"), ("L3_0", "L4_0"),
                ("L3_0", "L4_1"), ("L3_1", "L4_1"), ("L4_0", "L5_1"), ("L4_1", "L5_0"), ("L5_0", "L6_1"), ("L5_1", "L6_0"),
                ("L6_0", "L7"), ("L6_1", "L7")]
STREET_KIND = {"S": "start", "L1_0": "router", "L2_0": "terminal", "L2_1": "router", "L3_0": "modem", "L3_1": "elite",
               "L4_0": "router", "L4_1": "elite", "L5_0": "terminal", "L5_1": "router", "L6_0": "router", "L6_1": "elite", "L7": "rack"}


def street(corp, npy, js, res):
    plate = plate_of(npy, "night" if corp == "aurelian" else "deep", os.path.join(K.SCR, corp + "_street_plate.png"))
    A = load_anchors(js, res)
    walked = ["S", "L1_0", "L2_0", "L3_0"]
    nodes = {}
    for k, kind in STREET_KIND.items():
        st = "walked" if k in walked else "ahead"
        if k == "L3_0":
            st = "current"
        if k in ("L2_1",):
            st = "past"
        nodes[k] = dict(kind=kind, state=st)
    nodes["L4_0"].update(state="option", num=1)
    nodes["L4_1"].update(state="option", num=2)
    nodes["L7"]["state"] = "target"
    edges = []
    for a, b in STREET_EDGES:
        st = "ahead"
        if a in walked and b in walked:
            st = "walked"
        if a == "L3_0" and b in ("L4_0", "L4_1"):
            st = "option"
        if "L2_1" in (a, b) or "L3_1" in (a, b):
            st = "closed" if a in walked else "ahead"
        edges.append((a, b, st, []))
    ov = Image.new("RGBA", (W1, H1), (0, 0, 0, 0))
    ov = draw_route(ov, A, nodes, edges, px=44)
    x, y = A["L7"]
    ov = S.sticker(ov, "rack", x, y, 44)
    ov = target(ov, A, "L7", word_dx=-20, word_dy=-70, r=(52, 44))
    disp = {"aurelian": "Games tonight, so the Lictors are at the arena. Two ways up: the shop, or the elite on the aqueduct side.",
            "tethys": "Pumps are off two blocks over. Two ways on: the tube with the shop, or the elite in the dome."}[corp]
    ov = S.chrome_top(ov, disp)
    ov = route_panel(ov, 2, ["PICK A FLOOR: click a", "numbered room, then CONFIRM.", "Keys 1-2 go now."])
    ov = S.legend(ov, cx=960)
    return finish(plate, ov, os.path.join(K.NC, K.CORPS[corp]["folder"], "site_street.png"))


KIT_LABELS = {"aurelian": [("INSULA + PEDIMENT", "colonnade ground floor, arched windows, verdigris cornice trims"),
                           ("INSULA + STATUE", "a rooftop bronze as the billboard mount, uplit"),
                           ("INSULA + CROWN", "setback crown, neon line"),
                           ("CAMPANILE", "round, upright: arcaded rings per level, belfry crown, flat top"),
                           ("BASILICA", "podium colonnade, drum + dome, gilt lantern"),
                           ("AQUEDUCT", "two arch tiers; the channel carries the lit data stream"),
                           ("TRIUMPH GATE", "street gate: attic sign, statue, laurel holo"),
                           ("PIAZZA", "paved square, fountain + statue group, lit jets")],
              "tethys": [("PRESSURE DOME", "titanium ring with portholes, ribbed glass, a lit township inside"),
                         ("DROWNED TOWER", "wet hull, sparse lit floors, algae skirt, photophore strips"),
                         ("PUMP TOWER", "the seawall pumps: abyss rings, red lights"),
                         ("PENTHOUSE DOME", "a pressure dome on a drowned roof (the paid-up floor)"),
                         ("TUBE WALK", "ribbed glass tube between two domes, dive-light strip"),
                         ("CABLE VAULT", "the BUOY RELAY Site on the bed: sea cables run out"),
                         ("COLD VAULT", "data pods in rows, photophore ports, bubbles"),
                         ("KELP + SUB", "kelp with glowing tips; a sub with its wake")]}


def kit(corp, npy, js, res):
    plate = plate_of(npy, "night" if corp == "aurelian" else "deep", os.path.join(K.SCR, corp + "_kit_plate.png"), media=0.25)
    A = load_anchors(js, res)
    ov = Image.new("RGBA", (W1, H1), (0, 0, 0, 0))
    tt = K.word_sticker(["BUILDING KIT"], 46, U.FILL_YELLOW, seed=4)
    ov = SL.place(ov, tt, 170, 54, angle=-2)
    U.text(ov, (330, 54), "%s  //  every shape generated by rules (scripts/%s_scene.py), one seed, no hand placement" % (
        K.CORPS[corp]["name"], "roman" if corp == "aurelian" else "tethys"), U.F(U.MONO, 16), (220, 224, 234), "lm", 0.5)
    for i, (t, s_) in enumerate(KIT_LABELS[corp]):
        k = "k%d" % i
        if k not in A:
            continue
        x, y = A[k]
        ov, _ = KT.chip(ov, (x, y + 18), t, K.col(corp, "primary"), 15, anchor="mm", pad=8)
        U.text(ov, (x, y + 44), s_, U.F(U.PLEX, 14), (220, 226, 236), "mm", 0)
    return finish(plate, ov, os.path.join(K.NC, K.CORPS[corp]["folder"], "building_kit.png"))


if __name__ == "__main__":
    corp, what = sys.argv[1], sys.argv[2]
    kw = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    res = json.loads(kw.get("res", "[2560,1440]"))
    if what == "hq":
        (aur_hq if corp == "aurelian" else teth_hq)(kw["plate"], kw["json"], res)
    elif what == "kit":
        kit(corp, kw["plate"], kw["json"], res)
    elif what == "street":
        street(corp, kw["plate"], kw["json"], res)
