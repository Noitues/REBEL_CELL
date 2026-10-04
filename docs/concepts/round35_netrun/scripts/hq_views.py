"""Round 35 -> hq_climb.png, hq_compound.png, hq_compound_dynamic.gif, hq_compare.png (Meridian HQ boss run).

CLIMB    the keep cutaway (r32_scene.py tower, round 35: thick truss crane, the freight train it loads, every room dressed
         differently). Links MERGE: every edge into a room meets at one socket under it, every edge out leaves from one
         socket above it, so rejoining branches read as rejoining. The top room is the CENTRAL SERVER (THE MANIFEST).
COMPOUND the castle from above (compound_scene.py), raid-style: nodes are pads on the yard's buildings, stacks, the
         crane's load and the train's cars. The map is DYNAMIC: the crane carries a node from the yard to the train
         (its links switch from yard to rail) and the train rolls through (its car nodes link to the yard only while
         alongside the east gate). The Central Server is MANIFEST CONTROL, the building at the back of the yard.
States as everywhere this round: lime walked, orange available, WHITE not yet, GREY past.

python hq_views.py [climb|compound|gif|compare|all]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import transit_view as TV

COLS = TV.COLS

# ------------------------------------------------------------------ CLIMB
C_EDGES = {
    "start": ["1_1", "1_2", "1_3"],
    "1_1": ["2_0", "2_1"], "1_2": ["2_1", "2_2"], "1_3": ["2_2", "2_3"],
    "2_0": ["3_0"], "2_1": ["3_0", "3_1"], "2_2": ["3_1"], "2_3": ["3_2"],
    "3_0": ["4_0", "4_1"], "3_1": ["4_1"], "3_2": ["4_1", "4_2"],
    "4_0": ["5_0"], "4_1": ["5_0", "5_1"], "4_2": ["5_1", "5_2"],
    "5_0": ["6_0"], "5_1": ["6_0", "6_1"], "5_2": ["6_1"],
    "6_0": ["7_0"], "6_1": ["7_0"],
}
C_WALKED = ["start", "1_1", "2_1", "3_0"]


def reach(edges, cur):
    seen, todo = set(), [cur]
    while todo:
        for b in edges.get(todo.pop(), []):
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


def node_states(nodes, edges, walked, current):
    r = reach(edges, current)
    opts = edges.get(current, [])
    st = {}
    for k in nodes:
        st[k] = "current" if k == current else ("walked" if k in walked else ("option" if k in opts else ("white" if k in r else "past")))
    return st


def climb(walked=C_WALKED, current="3_0", ui=True):
    A = json.load(open(os.path.join(U.BL, "tower_anchors.json")))
    R_ = A["rooms"]
    kinds = {}
    for t, layer in enumerate(A["layers"]):
        for i, k in enumerate(layer):
            kinds["%d_%d" % (t + 1, i)] = k
    rooms = {k: v for k, v in R_.items() if kinds[k] != "sealed"}
    door = ((R_["1_1"]["floor"][0] + R_["1_2"]["floor"][0]) / 2, R_["1_1"]["floor"][1] + 24)
    sock_in = {k: (r["c"][0], r["floor"][1] - 6) for k, r in rooms.items()}
    sock_out = {k: (r["c"][0], r["ceil"][1] + 6) for k, r in rooms.items()}
    sock_out["start"] = door
    nodes = dict(rooms)
    nodes["start"] = None
    st = node_states(nodes, C_EDGES, walked, current)
    img = Image.open(os.path.join(U.FIN, "tower.png")).convert("RGBA")
    img = L.darken_rect(img, (-200, -200, 410, 1300), a=150, blur=50)
    img = L.darken_rect(img, (1510, -200, 2200, 1300), a=150, blur=50)
    for k, r in rooms.items():
        q = [tuple(p) for p in r["rect"]]
        s = st[k]
        if s == "past":
            img = U.poly_wash(img, q, None, 0.9, mode="grey")
        elif s in ("walked", "current"):
            img = U.poly_wash(img, q, R.LIME, 0.14 if s == "walked" else 0.22, glow=0.4)
        elif s == "white":
            img = U.poly_wash(img, q, (255, 255, 255), 0.05, glow=0.0)
    walked_e = set(zip(walked[:-1], walked[1:]))
    inl = U.Inlay()
    inl.trace([(-20, door[1] + 30), (door[0] - 80, door[1] + 30), (door[0], door[1])], R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)

    def path(a, b):
        p0, p1 = sock_out[a], sock_in[b]
        if abs(p0[0] - p1[0]) < 2:
            return [p0, p1]
        ym = p0[1] + (p1[1] - p0[1]) * 0.5 if a == "start" else (p0[1] + p1[1]) / 2
        return [p0, (p0[0], ym), (p1[0], ym), p1]

    later = []
    for a, bs in C_EDGES.items():
        for b in bs:
            if (a, b) in walked_e:
                later.append((a, b))
                continue
            sa, sb = (st.get(a) if a != "start" else "walked"), st[b]
            if a == current:
                inl.trace(path(a, b), R.MER, width=2.6, lanes=3, gap=4.0, glow=0.9, pads=False)
            elif sa in ("white", "option") and sb in ("white", "option"):
                inl.trace(path(a, b), R.WHITE, width=2.0, lanes=2, gap=4.0, glow=0.15, alpha=0.85, pads=False)
            else:
                inl.trace(path(a, b), R.GREY, width=1.8, lanes=2, gap=4.0, glow=0.0, alpha=0.8, pads=False)
    for a, b in later:
        inl.trace(path(a, b), R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)
    img = inl.lay(img)
    # sockets: one in / one out per room (where the branches meet)
    for k in rooms:
        col = COLS[st[k]]
        for p in (sock_in[k], sock_out[k]):
            img = U.pad(img, [(p[0], p[1] - 6), (p[0] + 12, p[1]), (p[0], p[1] + 6), (p[0] - 12, p[1])], col, lit=1.0, glow=0.4, k=0.6, pins=False)
    img = U.pad(img, [(door[0], door[1] - 14), (door[0] + 30, door[1]), (door[0], door[1] + 14), (door[0] - 30, door[1])], R.LIME, lit=1.0, glow=1.0)
    d = ImageDraw.Draw(img)
    for k, r in rooms.items():
        s = st[k]
        q = [tuple(p) for p in r["rect"]]
        if s in ("walked", "current", "option"):
            d.line(q + [q[0]], fill=COLS[s] + (255,), width=3)
    for k in sorted(rooms, key=lambda k: -rooms[k]["c"][1]):
        s = st[k]
        cx, cy = rooms[k]["c"]
        px = 88 if k == "7_0" else {"walked": 46, "current": 54, "option": 60, "white": 50, "past": 46}[s]
        sd = TV.white_sd(kinds[k], px) if s == "white" else U.node_sd(kinds[k], px, grey=(s == "past"))
        img = L.place_sticker(img, sd, cx, cy - 6, angle=((sum(map(ord, k)) % 9) - 4) * 0.8, opacity=0.85 if s == "past" else 1.0,
                              hover=0.35 if s == "option" else 0.0)
    fx, fy = rooms["7_0"]["c"]
    img = U.chip(img, (fx, fy - 70), "CENTRAL SERVER", R.GOLD, 16, bright=True)
    pr = L.pen(L.GP_RED, seed=371)
    pr.circle(fx, fy - 4, 140, 58, width=10)
    pr.text("THE MANIFEST", fx + 290, fy - 56, 34, angle=-5)
    img = L.ink(img, pr)
    cx, cy = rooms[current]["c"]
    img = L.place_sticker(img, U.token_sd(52), cx + 48, cy - 46, angle=-14, hover=0.6)
    if ui:
        img = hq_hud(img, "THE CLIMB", "KEEP, FLOOR 3 OF 7")
    return img


def hq_hud(img, title, sub, ry=120):
    img = L.place_sticker(img, L.sticker_word([title], 56, fills=["yellow"], seed=372), 200, 62, angle=-3)
    dz = R.dossier()
    dz = dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS)
    img = L.drop_shadow(img, dz, 22, 120, blur=14, off=(8, 12), op=0.6)
    img = R.node_info(img, (1500, ry, 1898, ry + 210), "MERIDIAN HQ", "T4  (boss)", ["the Exploit set", "campaign win"], "Freight castle",
                      special="KEYS 3 / 3")
    img = R.heat_strip(img, (1500, ry + 230), 71, "FLAGGED", w=398)
    img = U.chip(img, (1700, ry + 320), sub, U.CYAN, 15)
    return img


# ------------------------------------------------------------------ COMPOUND
K_EDGES_STATIC = {
    "start": ["1_0", "1_1", "1_2", "1_3"],
    "1_0": ["2_0"], "1_1": ["2_0", "2_1"], "1_2": ["2_1", "crane"], "1_3": ["2_2"],
    "2_0": ["3_0"], "2_1": ["3_1"], "2_2": ["3_2"],
    "3_0": ["4_0"], "3_1": ["4_0"], "3_2": ["4_1"],
    "4_0": ["7_0"], "4_1": ["7_0"],
}
KINDS_K = {"1_0": "router", "1_1": "router", "1_2": "router", "1_3": "terminal", "2_0": "elite", "2_1": "modem", "2_2": "router",
           "crane": "elite", "3_0": "terminal", "3_1": "router", "3_2": "router", "train_0": "modem", "train_2": "elite",
           "4_0": "rack", "4_1": "elite", "7_0": "rack"}
GATE_Y = (-30.0, 22.0)  # world y range of the east yard gate where the train links in


def compound_edges(A, f):
    E = {k: list(v) for k, v in K_EDGES_STATIC.items()}
    # the crane's node: linked into the yard while low over the yard, onto the rail side once over the train
    t = f / 7.0
    E["crane"] = ["3_1"] if t < 0.5 else ["train_0"] if "train_0" in A["nodes"] else []
    # train cars: linked in from the east yard (2_2) only while alongside the gate
    for k in ("train_0", "train_2"):
        if k in A["nodes"]:
            wy = A["nodes"][k]["wy"]
            if GATE_Y[0] < wy < GATE_Y[1]:
                E.setdefault("2_2", []).append(k)
                E[k] = ["4_1"]
            else:
                E[k] = []
    return E


def compound(f=0, walked=("start", "1_2"), current="1_2", ui=True, fin=None):
    A = json.load(open(os.path.join(U.BL, "compound_f%02d_anchors.json" % f)))
    for k in ("train_0", "train_2"):
        if k in A["nodes"]:
            A["nodes"][k]["wy"] = -46.0 + f * 7.0 + 12 - (0 if k == "train_0" else 28) + 6.25
    nodes = A["nodes"]
    E = compound_edges(A, f)
    st = node_states(nodes, E, list(walked), current)
    st["start"] = "walked"
    if fin is None:
        fin = os.path.join(U.FIN, "compound_full.png") if f == 0 else os.path.join(U.FIN, "compound_f%02d.png" % f)
    img = Image.open(fin).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
    img = ImageEnhance.Brightness(img).enhance(0.85)
    walked_e = set(zip(walked[:-1], walked[1:]))
    inl = U.Inlay()
    sx, sy = nodes["start"]["c"]
    inl.trace([(sx + 300, sy + 170), (sx, sy)], R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)
    for a, bs in E.items():
        for b in bs:
            if a not in nodes or b not in nodes or (a, b) in walked_e:
                continue
            p = [tuple(nodes[a]["c"]), tuple(nodes[b]["c"])]
            sa, sb = st.get(a), st.get(b)
            if a == current:
                inl.trace(p, R.MER, width=2.6, lanes=3, gap=4.0, glow=0.9, pads=False)
            elif sa in ("white", "option") and sb in ("white", "option"):
                inl.trace(p, R.WHITE, width=2.0, lanes=2, gap=4.0, glow=0.15, alpha=0.85, pads=False)
            else:
                inl.trace(p, R.GREY, width=1.8, lanes=2, gap=4.0, glow=0.0, alpha=0.8, pads=False)
    for a, b in walked_e:
        inl.trace([tuple(nodes[a]["c"]), tuple(nodes[b]["c"])], R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)
    img = inl.lay(img)
    order = sorted(nodes, key=lambda k: nodes[k]["c"][1])
    for k in order:
        s = st.get(k, "white")
        cx, cy = nodes[k]["c"]
        r = 22 if k != "7_0" else 34
        img = U.pad(img, [(cx, cy - r * 0.5), (cx + r, cy), (cx, cy + r * 0.5), (cx - r, cy)], COLS[s],
                    lit={"walked": 0.9, "current": 1.0, "option": 1.0, "white": 0.85, "past": 0.6}[s], glow=0.6, fill_a=215, k=0.8)
    for k in order:
        if k == "start":
            continue
        s = st.get(k, "white")
        cx, cy = nodes[k]["c"]
        px = 84 if k == "7_0" else {"walked": 44, "current": 50, "option": 56, "white": 46, "past": 42}[s]
        sd = TV.white_sd(KINDS_K[k], px) if s == "white" else U.node_sd(KINDS_K[k], px, grey=(s == "past"))
        img = L.place_sticker(img, sd, cx, cy - 26, angle=((sum(map(ord, k)) % 9) - 4) * 0.8, opacity=0.85 if s == "past" else 1.0,
                              hover=0.35 if s == "option" else 0.0)
    for k in ("crane", "train_0", "train_2"):
        if k in nodes:
            cx, cy = nodes[k]["c"]
            img = U.chip(img, (cx, cy + 22), {"crane": "ON THE CRANE", "train_0": "ON THE TRAIN", "train_2": "ON THE TRAIN"}[k], U.CYAN, 12)
    fx, fy = nodes["7_0"]["c"]
    img = U.chip(img, (fx, fy + 52), "CENTRAL SERVER  //  MANIFEST CONTROL", R.GOLD, 15, bright=True)
    pr = L.pen(L.GP_RED, seed=373)
    pr.circle(fx, fy - 24, 90, 70, width=10)
    pr.text("THE MANIFEST", fx + 40, fy - 128, 32, angle=-5)
    img = L.ink(img, pr)
    cx, cy = nodes[current]["c"]
    img = L.place_sticker(img, U.token_sd(50), cx + 30, cy - 66, angle=-14, hover=0.6)
    if ui:
        img = hq_hud(img, "THE COMPOUND", "YARD, LAYER 1 OF 5", ry=650)
    return img


def compare(climb_img, comp_img):
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (9, 8, 14, 255))
    img = L.place_sticker(img, L.sticker_word(["MERIDIAN HQ: CLIMB OR COMPOUND?"], 46, fills=["yellow"], seed=374), 470, 52, angle=-2)
    for i, (im, title, pros, cons) in enumerate((
            (climb_img, "A  THE CLIMB (cutaway)", ["up = progress, the boss sits on top", "every room dressed, branches merge",
                                                    "the HQ silhouette you saw all campaign"],
             ["a static map: the crane and train are only scenery", "a server on a crane cab is odd fiction"]),
            (comp_img, "B  THE COMPOUND (raid-style overhead)", ["same camera family as raids: one language",
                                                                  "DYNAMIC: the crane moves a node; train cars link in at the gate",
                                                                  "Central Server = a real building"],
             ["needs per-corp moving pieces + rules (helix, eye, silo)", "harder to read 'how far to the boss'"]))):
        x = 22 + i * 948
        th = im.convert("RGBA").resize((926, 521), Image.LANCZOS)
        img.alpha_composite(th, (x, 110))
        d = ImageDraw.Draw(img)
        d.rectangle([x, 110, x + 926, 631], outline=U.CYAN + (255,), width=2)
        d.text((x, 660), title, font=L.f_ui(28, b"Bold"), fill=U.CYAN + (255,))
        y = 708
        for s in pros:
            d.text((x, y), "+ " + s if not s.startswith(("DYNAMIC", "every", "the", "same", "Central", "up")) or True else s, font=L.f_mono(18),
                   fill=(150, 240, 160, 255))
            y += 28
        y += 10
        for s in cons:
            d.text((x, y), "- " + s, font=L.f_mono(18), fill=(255, 150, 140, 255))
            y += 28
    c = L.CRT(1876, 96, R.LIME, "RECOMMENDATION", seed=375)
    c.text((16, 52), "B for the HQ boss run: it reuses the raid view, makes each corp's HQ play differently (Meridian: crane + train", 17, (225, 240, 225))
    c.text((16, 74), "move nodes), and the Central Server is a place, not a crate. Keep A's room dressing as the per-node close-up art.", 17, (225, 240, 225))
    img = L.paste(img, c.finish(scan=0.15), 22, 966)
    return img


def gif():
    frames, durs = [], []
    for f in range(8):
        im = compound(f, ui=False)
        d = ImageDraw.Draw(im)
        frames.append(im.convert("RGB"))
        durs.append(1200 if f in (0, 7) else 260)
    out = os.path.join(L.OUT, "hq_compound_dynamic.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(960, 540)))


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    ci = co = None
    if w in ("climb", "all", "compare"):
        ci = climb()
        if w != "compare":
            L.save(L.bloom(ci, 0.14, 0.8, 8), "hq_climb.png")
    if w in ("compound", "all", "compare"):
        co = compound(0)
        if w != "compare":
            L.save(L.bloom(co, 0.14, 0.8, 8), "hq_compound.png")
    if w in ("compare", "all"):
        L.save(compare(ci, co), "hq_compare.png")
    if w in ("gif", "all"):
        gif()
