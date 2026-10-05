"""Round 43: the designer's HQ mechanics, in the locked netrun language (round 42 overlay kit, compound42.py).

python compound43.py [meridian solace halcyon orbital rebel]
  -> ../hq_<corp>_compound.png + ../hq_<corp>_mechanic.gif ; rebel: ../dispatch_idea_<n>_<name>.png + ../dispatch_sync_strike.gif

Each GIF is a list of FRAMES: (render frame, state) where state = edges, walked path, locked/spotted set, chips, extras.
Links that leave the edge set DE-POWER (2 frames), links that join are REMADE (drawn on over 2 frames). Dynamic links
carry their step number, so "recreated after every move" really re-forms them at every step.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import compound42 as K
import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL

OUT = K.OUT
LIME, MER, WHITE, GOLD, RED, DIM = K.LIME, K.MER, K.WHITE, K.GOLD, K.RED, K.DIM
YEL = L.GP_YELLOW
CYAN = U.CYAN


def nodes_of(tag, f):
    a = K.anchors(tag, f)
    return {k: v for k, v in a["nodes"].items()}


def draw_state(img, nodes, E, Eprev, Eprev2, walked, kinds, locked=(), chips=None, srv_name="", token_at=None, edge_style=None,
               hide_srv=False):
    """The round 42 overlay for one frame. E / Eprev / Eprev2: edge sets now, 1 and 2 frames ago (edges may carry a 3rd
    item, a tag, so re-made links count as new)."""
    chips = chips or {}
    edge_style = edge_style or {}
    P = {k: tuple(v["c"]) for k, v in nodes.items()}

    def ab(e):
        return e[0], e[1]
    E2 = {ab(e) for e in E if e[0] in P and e[1] in P}
    st = K.node_states(nodes, E2, walked, set(locked))
    walked_e = set(zip(walked[:-1], walked[1:]))
    inl = U.Inlay()
    sparks, heads = [], []
    for e in (Eprev | Eprev2) - E:
        a, b = ab(e)
        if a in P and b in P and (a, b) not in E2:
            age = 1 if e in Eprev else 2
            inl.trace([P[a], P[b]], (110, 40, 50) if age == 1 else (60, 40, 50), width=2.0, lanes=2, gap=4.0, glow=0.25 if age == 1 else 0.0,
                      alpha=0.85 if age == 1 else 0.45, pads=False)
            if age == 1:
                for t in (0.3, 0.55, 0.8):
                    sparks.append((P[a][0] + (P[b][0] - P[a][0]) * t, P[a][1] + (P[b][1] - P[a][1]) * t))
    for e in E:
        a, b = ab(e)
        if a not in P or b not in P or (a, b) in walked_e or (b, a) in walked_e:
            continue
        sa, sb = st.get(a), st.get(b)
        style = edge_style.get((a, b))
        if a == walked[-1]:
            col, w, ln, gl, al = MER, 2.6, 3, 0.9, 1.0
        elif sa in ("white", "option", "walked") and sb in ("white", "option"):
            col, w, ln, gl, al = WHITE, 2.0, 2, 0.15, 0.85
        else:
            col, w, ln, gl, al = K.GREY, 1.8, 2, 0.0, 0.75
        if style == "shortcut":
            col, w = (GOLD if col != K.GREY else (150, 120, 60)), w + 0.4
        pa, pb = P[a], P[b]
        if e not in Eprev:
            pb2 = (pa[0] + (pb[0] - pa[0]) * 0.5, pa[1] + (pb[1] - pa[1]) * 0.5)
            inl.trace([pa, pb2], col, width=w + 0.6, lanes=ln, gap=4.0, glow=1.0, alpha=al, pads=False)
            heads.append(pb2)
        elif e not in Eprev2:
            pb2 = (pa[0] + (pb[0] - pa[0]) * 0.85, pa[1] + (pb[1] - pa[1]) * 0.85)
            inl.trace([pa, pb2], col, width=w + 0.3, lanes=ln, gap=4.0, glow=1.0, alpha=al, pads=False)
            heads.append(pb2)
        else:
            inl.trace([pa, pb], col, width=w, lanes=ln, gap=4.0, glow=gl, alpha=al, pads=False)
    for a, b in walked_e:
        if a in P and b in P:
            inl.trace([P[a], P[b]], LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)
    img = inl.lay(img)
    d = ImageDraw.Draw(img)
    for (x, y) in sparks:
        for k in range(5):
            a = k * 72 + 17
            r = 6 + k % 4 * 2
            d.line([(x, y), (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))], fill=(255, 90, 80, 230), width=2)
    for (x, y) in heads:
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 240, 255))
    for k in sorted(nodes, key=lambda k: P[k][1]):
        if k == "srv" and hide_srv:
            continue
        cx, cy = P[k]
        r = 22 if k != "srv" else 34
        img = U.pad(img, [(cx, cy - r * 0.5), (cx + r, cy), (cx, cy + r * 0.5), (cx - r, cy)], K.RING[st[k]], lit=0.9, glow=0.5, fill_a=210, k=0.8)
    for k in sorted(nodes, key=lambda k: P[k][1]):
        if k == "start" or (k == "srv" and hide_srv):
            continue
        s = st[k]
        cx, cy = P[k]
        px = 80 if k == "srv" else 44
        img = L.place_sticker(img, U.node_sd(kinds.get(k, "router"), px), cx, cy - 22, angle=((sum(map(ord, k)) % 9) - 4) * 0.8,
                              opacity=0.8 if s == "grey" else 1.0, hover=0.35 if s == "option" else 0.0)
        img = K.ring(img, cx, cy - 22, px * 0.62, K.RING[s], w=5 if s in ("option", "locked") else 4, glow=0.9 if s in ("option", "locked") else 0.3)
        if k in chips:
            c = chips[k]
            img = U.chip(img, (cx, cy + 20), c, RED if c in ("LOCKED", "IN THE EYE", "SPOTTED") else CYAN, 12)
    if "srv" in P and srv_name and not hide_srv:
        sx, sy = P["srv"]
        img = U.chip(img, (sx, sy + 66), "CENTRAL SERVER  //  " + srv_name, GOLD, 15, bright=True)
        pr = L.pen(L.GP_RED, seed=431)
        pr.circle(sx, sy - 26, 78, 64, width=9)
        pr.text(srv_name, sx + 30, sy - 130, 30, angle=-5)
        img = L.ink(img, pr)
    tx, ty = token_at if token_at else P[walked[-1]]
    img = L.place_sticker(img, U.token_sd(50), tx + 30, ty - 64, angle=-14, hover=0.6)
    return img, st, P


def hud(img, title, rule, tag, extra=None):
    img = L.place_sticker(img, L.sticker_word([title], 44, fills=["yellow"], seed=432), 400, 56, angle=-2)
    import textwrap
    lines = textwrap.wrap(rule, 128)
    c = L.CRT(1240, 52 + 22 * len(lines), CYAN, "HQ MECHANIC", tag=tag, seed=433)
    for i_, ln in enumerate(lines):
        c.text((16, 44 + 22 * i_), ln, 15, (225, 235, 240))
    img = L.paste(img, c.finish(scan=0.15), 20, 1064 - (52 + 22 * len(lines)))
    lg = L.CRT(560, 44, CYAN, None, header=False, seed=434)
    x0 = 14
    for col, s_ in ((LIME, "walked"), (MER, "selectable"), (WHITE, "not yet"), (DIM, "cut off"), (RED, "danger")):
        lg.d.ellipse([x0, 12, x0 + 18, 30], outline=col + (255,), width=3)
        x0 += 24 + int(lg.text((x0 + 24, 12), s_, 14, (215, 225, 230))) + 18
    img = L.paste(img, lg.finish(scan=0.15), 1340, 1020)
    return img


def telegraph(img, x, y, text):
    """The 'NEXT' telegraph: a yellow grease-pencil bracket + label around the container the crane moves next."""
    p = L.pen(YEL, seed=int(x + y) % 97 + 3)
    p.circle(x, y - 22, 52, 44, width=7)
    p.text(text, x + 40, y - 92, 26, angle=-6)
    return L.ink(img, p)


def save_out(corp, frames, durs, key, step=1, size=(960, 540), colors=150):
    L.save(L.bloom(frames[key].convert("RGBA"), 0.12, 0.8, 8), "hq_%s_compound.png" % corp)
    p = os.path.join(OUT, "hq_%s_mechanic.gif" % corp)
    fr = [f.convert("RGB") for f in frames][::step]
    du = [sum(durs[i:i + step]) for i in range(0, len(durs), step)]
    kb = U.save_gif(fr, du, p, size=size, colors=colors) // 1024
    print(corp, "gif KB", kb, flush=True)


# ================================================================== MERIDIAN
MER_KINDS = {"g1": "router", "g2": "router", "t1": "terminal", "wS1": "router", "wS2": "modem", "srv": "rack", "t2": "elite", "wN1": "terminal",
             "wN2": "router", "t3": "modem", "wB": "elite", "car0": "modem", "A": "elite", "B": "router"}
MER_WALL = [("start", "g1"), ("start", "g2"), ("g1", "t1"), ("t1", "wS1"), ("wS1", "wS2"), ("wS2", "srv"), ("g2", "t2"), ("t2", "wN1"), ("wN1", "wN2"),
            ("wN2", "t3"), ("t3", "wB"), ("wB", "srv")]
NORTH = {"t2": 18.0, "wN1": 6.0, "wN2": -6.0, "t3": -18.0}
MER_WALKED = {0: ["start", "g2", "t2"], 1: ["start", "g2", "t2"], 2: ["start", "g2", "t2", "B"], 3: ["start", "g2", "t2", "B", "t2"],
              4: ["start", "g2", "t2", "B", "t2", "wN1"], 5: ["start", "g2", "t2", "B", "t2", "wN1", "B"]}
MER_NEXT = {0: ("A", "NEXT: ONTO THE TRAIN"), 1: ("B", "NEXT: OFF THE TRAIN"), 2: ("B", "NEXT: OFF THE TRAIN"), 3: ("B", "NEXT: INTO THE FORT"),
            4: ("car0", "NEXT: LEAVES"), 5: ("car0", "LEAVING")}


def mer_edges(s, n):
    E = set(MER_WALL)
    for k in ("car0", "A", "B"):         # train cars beside a north-wall node link both ways (re-made every step)
        if k in n and n[k]["w"][1] > 30 and s in (1, 2, 3, 4):
            x = n[k]["w"][0]
            best = min(NORTH, key=lambda q: abs(NORTH[q] - x))
            if abs(NORTH[best] - x) < 9:
                E |= {(best, k, s), (k, best, s)}
    if "B" in n and n["B"]["w"][1] < 10 and s == 5:   # B set down in the yard: a new link across the fortress
        E |= {("wN1", "B", s), ("B", "wS2", s)}
    return E


def meridian():
    tag = "meridian_hq"
    seq = list(range(24))
    states = []
    for f in seq:
        s = f // 4
        n = nodes_of(tag, f)
        states.append((f, s, n, mer_edges(s, n)))
    frames, durs = [], []
    for i, (f, s, n, E) in enumerate(states):
        Ep = states[i - 1][3] if i else E
        Ep2 = states[i - 2][3] if i > 1 else Ep
        img = K.backdrop(tag, f)
        img = SL.over(img, (6, 5, 12), Image.new("L", img.size, 40))
        walked = MER_WALKED[s]
        chips = {k: "ON THE TRAIN" for k in ("car0", "A", "B") if k in n and n[k]["w"][1] > 30}
        if "B" in n and n["B"]["w"][1] < 30 and s < 5 and s >= 3:
            chips["B"] = "ON THE CRANE"
        if "A" in n and n["A"]["w"][1] < 30:
            chips["A"] = "ON THE CRANE"
        img, st, P = draw_state(img, n, E, Ep, Ep2, walked, MER_KINDS, chips=chips, srv_name="THE MASTER MANIFEST")
        k, txt = MER_NEXT[s]
        if k in P:
            img = telegraph(img, P[k][0], P[k][1], txt)
        img = hud(img, "MERIDIAN: CRANE + TRAIN", "Each step the crane or train moves ONE container (telegraphed NEXT); every moved link is re-made. "
                  "The train stands a full turn, so you can step on and back.", "STEP %d" % (s + 1))
        frames.append(img)
        durs.append(240 if f % 4 else 500)
    save_out("meridian", frames, durs, 10, step=2)


# ================================================================== SOLACE
SOL_PATH = ["start", "A0", "A1", "X0", "B2", "B3", "X1", "A4"]


def sol_edges():
    E = {("start", "A0"), ("start", "B0")}
    E |= {("A%d" % j, "A%d" % (j + 1)) for j in range(7)} | {("B%d" % j, "B%d" % (j + 1)) for j in range(6)}
    E |= {("A7", "srv"), ("B6", "srv")}
    for x, (a_in, b_in, a_out, b_out) in enumerate(((1, 1, 2, 2), (3, 3, 4, 4), (5, 5, 6, 6))):
        X = "X%d" % x
        E |= {("A%d" % a_in, X), ("B%d" % b_in, X), (X, "A%d" % a_out), (X, "B%d" % b_out)}
    return E


SOL_KINDS = {**{"A%d" % j: ["elite", "router", "elite", "router", "elite", "router", "elite", "elite"][j] for j in range(8)},
             **{"B%d" % j: ["terminal", "modem", "terminal", "router", "modem", "terminal", "modem"][j] for j in range(7)},
             "X0": "router", "X1": "router", "X2": "router", "srv": "rack"}


def solace():
    tag = "solace_hq"
    E = sol_edges()
    frames, durs = [], []
    nf = 2 * (len(SOL_PATH) - 1) + 1
    for f in range(nf):
        n = nodes_of(tag, f)
        i = f // 2
        walked = SOL_PATH[:i + 1]
        img = K.backdrop(tag, f)
        img = SL.over(img, (6, 5, 12), Image.new("L", img.size, 40))
        chips = {"A0": "STRAND A", "B0": "STRAND B"}
        for x in ("X0", "X1", "X2"):
            chips[x] = "CROSSOVER"
        img, st, P = draw_state(img, n, E, E, E, walked, SOL_KINDS, chips=chips, srv_name="THE GENOME CORE")
        img = hud(img, "SOLACE: CLIMB THE HELIX", "Pick a strand at the start. Strand A: elites + loot. Strand B: terminals + shops. "
                  "Walkway rungs are CROSSOVERS. The camera keeps you centre.", "HEIGHT %d%%" % int(100 * n[walked[-1]]["w"][2] / 115))
        frames.append(img)
        durs.append(600 if f == 0 or f == nf - 1 else 260)
    save_out("solace", frames, durs, 6, size=(800, 450), colors=100)


# ================================================================== HALCYON
SHORTCUTS = [("n4", "n9"), ("n9", "n13"), ("n13", "n17"), ("n17", "n20")]
HAL_SEQ = {0: ["start", "n1", "n2", "n3", "n4"], 1: ["start", "n1", "n2", "n3", "n4", "n9"], 2: ["start", "n1", "n2", "n3", "n4", "n9", "n13"],
           3: ["start", "n1", "n2", "n3", "n4", "n9", "n13", "n14"]}
HAL_KINDS = {**{"n%d" % i: ["router", "terminal", "router", "elite", "modem", "router", "terminal"][i % 7] for i in range(1, 22)}, "srv": "rack"}


def hal_lit(n, f, eye):
    """Nodes in view: the half the eye faces (x < -1.5 left / x > 1.5 right) plus the centre column, always."""
    side = -1 if eye < 0 else 1
    out = set()
    for k, v in n.items():
        if k.startswith("n"):
            x = v["w"][0]
            if abs(x) <= 1.5 or x * side > 1.5:
                out.add(k)
    return out


def halcyon():
    tag = "halcyon_hq"
    base = {("start", "n1")} | {("n%d" % i, "n%d" % (i + 1)) for i in range(1, 21)} | {("n21", "srv")}
    frames, durs = [], []
    spotted = 0
    used = 0
    for f in range(16):
        s, k = divmod(f, 4)
        n = nodes_of(tag, f)
        a = K.anchors(tag, f)
        eye = a.get("eye") or 0.0
        walked = HAL_SEQ[s] if k >= 2 else (HAL_SEQ[s - 1] if s else HAL_SEQ[0][:-0 or None])
        used = sum(1 for e in zip(walked[:-1], walked[1:]) if e in SHORTCUTS)
        sc = set(SHORTCUTS) if used < 2 else set()
        E = base | sc
        lit = hal_lit(n, f, eye)
        style = {e: "shortcut" for e in SHORTCUTS}
        cur = walked[-1]
        locked = {x for x in lit if x not in walked}
        chips = {x: "IN THE EYE" for x in locked if x in ("n9", "n13", "n17", "n20")}
        sp = sum(1 for x in walked if x in hal_lit(n, f, eye) and x in ("n9", "n17"))
        img = K.backdrop(tag, f)
        img = SL.over(img, (6, 5, 12), Image.new("L", img.size, 40))
        img, st, P = draw_state(img, n, E, E, E, walked, HAL_KINDS, locked=locked, chips=chips, srv_name="THE PANOPTICON", edge_style=style)
        d = ImageDraw.Draw(img)
        for (a_, b_) in SHORTCUTS:
            if a_ in P and b_ in P:
                mx, my = (P[a_][0] + P[b_][0]) / 2, (P[a_][1] + P[b_][1]) / 2
                img = U.chip(img, (mx, my), "SHORTCUT", GOLD, 12)
        for kk, v in n.items():
            if kk.startswith("n"):
                x, y = P[kk]
                d.text((x - 26, y - 56), kk[1:], font=L.f_ui(16, b"Bold"), fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 8, 14, 255))
        if k >= 2 and cur in ("n9",):
            img = L.place_sticker(img, L.sticker_word(["SPOTTED: +1 PATROL"], 30, fills=[("grad", (255, 96, 96), (196, 20, 32))], seed=435), P[cur][0] + 150, P[cur][1] - 110, angle=-6)
        img = hud(img, "HALCYON: THE LONG WAY", "21 nodes in switchbacks (6-5-4-3-2-1). Shortcuts 4>9, 9>13, 13>17, 17>20 (max 2). The eye watches one half + the "
                  "centre each step: entering a watched node = SPOTTED.", "SHORTCUTS %d/2   EYE: %s" % (used, "LEFT" if eye < 0 else "RIGHT"))
        frames.append(img)
        durs.append(320 if k else 600)
    save_out("halcyon", frames, durs, 6)


# ================================================================== ORBITAL
LOOP = ["plat", "dishNE", "dishE", "mast", "dishW", "dishSW"]
ORB_KINDS = {"plat": "elite", "dishNE": "router", "dishE": "modem", "mast": "terminal", "dishW": "router", "dishSW": "elite", "missile": "rack", "srv": "rack"}


def prep_bar(img, frac, lap, done):
    c = L.CRT(420, 120, (255, 120, 60), "MISSILE BAY", tag="LAP %d" % lap, seed=436)
    c.text((16, 48), "NEXT MISSILE PREP", 15, (230, 230, 240))
    c.d.rectangle([16, 72, 404, 92], outline=(255, 120, 60, 255), width=2)
    c.d.rectangle([19, 75, 19 + int(382 * frac), 89], fill=(255, 120, 60, 255))
    c.text((16, 96), "SABOTAGED  " + "  ".join("X" if i < done else "-" for i in range(4)), 15, (255, 210, 120))
    return L.paste(img, c.finish(scan=0.15), 1480, 90)


def orbital():
    tag = "orbital_hq"
    seq = []  # (render frame, lap, position index along the loop or special, done)
    for lap, done0 in ((1, 0),):
        for i in range(len(LOOP)):
            seq.append((0, lap, i, done0, "walk"))
        seq.append((1, lap, 0, done0, "sabotage"))
        seq.append((1, lap, 0, done0 + 1, "sabotage"))
    seq.append((0, 2, 3, 1, "walk"))
    seq.append((1, 2, 0, 2, "sabotage"))
    seq.append((0, 3, 3, 2, "walk"))
    seq.append((1, 3, 0, 3, "sabotage"))
    for i in (1, 3, 5):
        seq.append((0, 4, i, 3, "walk4"))
    seq += [(2, 4, 5, 3, "launch"), (2, 4, 5, 4, "boom1"), (2, 4, 5, 4, "boom2"), (2, 4, 5, 4, "boom3")]
    frames, durs = [], []
    prevE, prev2 = None, None
    for gi, (f, lap, i, done, mode) in enumerate(seq):
        n = nodes_of(tag, f)
        n.pop("srv", None)
        if f == 0 or mode.startswith("boom") or mode == "launch":
            n.pop("missile", None) if mode == "walk" or mode == "walk4" else None
        E = {(LOOP[j], LOOP[(j + 1) % len(LOOP)], lap) for j in range(len(LOOP))} | {("start", "plat")}
        if mode == "walk4" or mode in ("launch",) or mode.startswith("boom"):
            E = {(a, b, c) for (a, b, c) in [e if len(e) == 3 else (e[0], e[1], 0) for e in E] if b != "plat" and a != "plat"} | {("dishSW", "dishNE", 4),
                                                                                                                                ("dishSW", "missile", 4)}
            E |= {("start", "plat")}
        if mode == "sabotage":
            E |= {("plat", "missile", lap)}
        walked = ["start"] + (LOOP[:i + 1] if mode == "walk" else (["plat"] if mode == "sabotage" else ["plat", "dishNE", "dishE", "mast", "dishW", "dishSW"][:i + 1]))
        if mode == "sabotage":
            walked = ["start"] + LOOP + ["plat", "missile"] if done > (lap - 1) else ["start"] + LOOP + ["plat"]
        if mode in ("launch",) or mode.startswith("boom"):
            walked = ["start", "plat", "dishNE", "dishE", "mast", "dishW", "dishSW", "missile"]
            n["missile"] = {"c": n["plat"]["c"], "w": [0, 0, 27]}
            ox = (n["dishE"]["c"][0] + n["dishW"]["c"][0]) / 2
            n["missile"]["c"] = [ox, n["plat"]["c"][1] - 170]
        walked = [w for w in walked if w in n]
        Ep = prevE if prevE is not None else E
        Ep2 = prev2 if prev2 is not None else Ep
        img = K.backdrop(tag, f)
        img = SL.over(img, (6, 5, 12), Image.new("L", img.size, 40))
        chips = {"plat": "PLATFORM", "mast": "ANTENNA", "missile": "MISSILE %d" % min(4, done + (0 if mode != "sabotage" else 0) + (1 if mode == "walk4" else 0) or 1)}
        img, st, P = draw_state(img, n, E, Ep, Ep2, walked, ORB_KINDS, chips=chips, srv_name="")
        frac = (i + 1) / len(LOOP) if mode.startswith("walk") else (1.0 if mode == "sabotage" else 0.35)
        img = prep_bar(img, frac, lap, done)
        if mode == "sabotage" and done > lap - 1:
            p = L.pen(L.GP_RED, seed=437)
            mx, my = P["missile"]
            p.stroke([(mx - 50, my - 80), (mx + 50, my + 20)], width=10)
            p.stroke([(mx + 50, my - 80), (mx - 50, my + 20)], width=10)
            img = L.ink(img, p)
        if mode == "walk4":
            img = L.place_sticker(img, L.sticker_word(["LAP 4: BYPASS THE PLATFORM"], 30, fills=["yellow"], seed=438), 960, 160, angle=-3)
        if mode == "launch" or mode.startswith("boom"):
            sx, sy = P["plat"]
            cx, cy = (n["dishE"]["c"][0] + n["dishW"]["c"][0]) / 2, sy - 120
            k = {"launch": 0.3, "boom1": 0.7, "boom2": 1.0, "boom3": 0.8}[mode]
            glow = Image.new("L", img.size, 0)
            ImageDraw.Draw(glow).ellipse([cx - 420 * k, cy - 260 * k, cx + 420 * k, cy + 260 * k], fill=255)
            glow = glow.filter(ImageFilter.GaussianBlur(60))
            img = SL.over(img, (255, 160, 60), SL.scale_mask(glow, 0.95 * k))
            img = SL.over(img, (255, 250, 220), SL.scale_mask(glow.filter(ImageFilter.MinFilter(41)), 0.9 * k))
            if mode != "launch":
                img = L.place_sticker(img, L.sticker_word(["LAUNCHED IN THE BAY", "BASE DESTROYED"], 44, fills=[("grad", (255, 96, 96), (196, 20, 32))], seed=439), 960, 420, angle=-4)
            else:
                img = L.place_sticker(img, L.sticker_word(["MISSILE 4: LAUNCH (DOORS SHUT)"], 30, fills=["yellow"], seed=440), 960, 160, angle=-3)
        img = hud(img, "ORBITAL: THE LAUNCH LOOP", "Clear every node each lap (platform > dishes > antenna > dishes); a missile is prepped meanwhile and "
                  "sabotaged at the platform. Lap 4 bypasses the platform: launch it in the shut bay.", "LAP %d" % lap)
        frames.append(img)
        durs.append(900 if mode in ("sabotage", "boom2") or gi == 0 else 300)
        prev2, prevE = prevE, E
    save_out("orbital", frames, durs, 3)


if __name__ == "__main__":
    which = sys.argv[1:] or ["meridian", "solace", "halcyon", "orbital", "rebel"]
    for w in which:
        if w == "rebel":
            import dispatch43
            dispatch43.main()
        else:
            if w in ("meridian", "solace"):
                K.prep_passes({"meridian": "meridian_hq", "solace": "solace_hq"}[w], 24 if w == "meridian" else 15)
            else:
                K.prep_passes(w + "_hq", 16 if w == "halcyon" else 3)
            globals()[w]()
