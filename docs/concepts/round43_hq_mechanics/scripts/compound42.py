"""Round 42: the HQ-run compound per corp with its UNIQUE MECHANIC, in the locked netrun language.

python compound42.py [corp ...]      -> ../hq_<corp>_compound.png (1920 x 1080 key frame) + ../hq_<corp>_mechanic.gif

Backdrop: hq_scene.py COMPOUND=1 anim frames (the HQ model of rounds 26-31 from above: city azimuth, 55 deg, ortho),
finished with the round 11 style pass (backdrop30.finish). Overlay (round 35-37 netrun language):
  - node = die-cut node-type sticker (full colour, never tinted) on an inlay pad, STATE = one outline ring (option A):
    lime walked, orange selectable, white not yet, dim grey not reachable now; red = LOCKED (Halcyon's eye)
  - links = circuit inlay traces: lime walked, orange from the current node, white reachable, grey otherwise
  - Central Server = big rack sticker, gold chip, red grease-pencil ring + name
  - THE MECHANIC: links whose rule turns off DE-POWER (dark, flickering, with red sparks, then gone); links whose rule
    turns on are REMADE (drawn on from the source with a bright head). Every rule is a pure function of the step/frame.
"""
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import backdrop30 as BD
import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL

OUT = os.path.dirname(HERE)
BL = os.path.join(OUT, "scratch", "bl")
W, H = 1920, 1080
LIME, MER, WHITE, GREY, GOLD = R.LIME, R.MER, R.WHITE, R.GREY, R.GOLD
RED = (255, 52, 64)
ORANGE = MER
DIM = (80, 76, 92)


def ring(img, x, y, r, col, w=4, glow=0.7):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r, x + r, y + r], outline=255, width=w)
    if glow:
        img = SL.over(img, col, SL.scale_mask(m.filter(ImageFilter.GaussianBlur(5)), glow))
    img = SL.over(img, (6, 5, 10), SL.shift(m, 1, 2))
    return SL.over(img, col, m)


# ------------------------------------------------------------------ per-corp rules (pure functions of the frame)
def mer_rules(f, N, A):
    n = A
    E = {("start", "g1"), ("start", "g2"), ("g1", "y1"), ("g1", "t1"), ("g2", "y2"), ("g2", "t2"), ("t1", "srv"), ("t2", "t3"), ("t3", "srv")}
    if "crane" in n:
        wy = n["crane"]["w"][1]
        on_car = 9 <= f <= 14
        if not on_car and wy < 20:              # over the yard: the crane's node links into the yard
            E |= {("y1", "crane"), ("y2", "crane"), ("crane", "t3")}
        elif not on_car and wy >= 20 and 4 <= f <= 8:   # over the stopped train: links onto its cars
            E |= {("crane", k) for k in ("car0", "car2") if k in n}
    for k in ("car0", "car2", "crane"):         # train cars link in only while alongside a front tower
        if k in n and n[k]["w"][1] > 30:
            x = n[k]["w"][0]
            if abs(x - 18) < 24:
                E |= {("t2", k), (k, "srv")}
            elif abs(x + 18) < 24:
                E |= {("t3", k), (k, "srv")}
    chips = {"crane": "ON THE CRANE" if not (9 <= f <= 14) else "ON THE TRAIN", "car0": "ON THE TRAIN", "car2": "ON THE TRAIN"}
    return E, set(), chips


def sol_rules(f, N, A):
    n = A
    E = {("start", "pod0"), ("start", "pod5")}
    E |= {("pod%d" % k, "pod%d" % ((k + 1) % 6)) for k in range(6)}       # the podium ring
    E |= {("w%d" % j, "w%d" % (j + 1)) for j in range(5)} | {("w5", "srv")}
    for k in range(6):                                                   # docking: pod <-> lowest walkways by angle
        pa = 60.0 * k
        for j in (0, 1):
            x, y, _ = n["w%d" % j]["w"]
            wa = math.degrees(math.atan2(y, x)) % 360
            if abs(((wa - pa + 180) % 360) - 180) < 22:
                E.add(("pod%d" % k, "w%d" % j))
    return E, set(), {"w0": "ON THE WALKWAY", "w1": "ON THE WALKWAY"}


def hal_rules(f, N, A):
    n = A
    E = {("start", "L0"), ("start", "R0")}
    E |= {("L%d" % k, "L%d" % (k + 1)) for k in range(5)} | {("R%d" % k, "R%d" % (k + 1)) for k in range(5)}
    E |= {("L5", "srv"), ("R5", "srv"), ("R1", "L2"), ("L1", "R2"), ("R3", "L4"), ("L3", "R4")}
    eye = A["_eye"]
    look = -90.0 + eye                      # the eye's facing (deg, world): -Y rotated by the eye angle
    locked = set()
    for k, v in n.items():
        if k[0] in "LR":
            az = math.degrees(math.atan2(v["w"][1], v["w"][0]))
            if abs(((az - look + 180) % 360) - 180) < 24:
                locked.add(k)
    E = {(a, b) for a, b in E if a not in locked and b not in locked}
    return E, locked, {k: "LOCKED" for k in locked}


def orb_rules(f, N, A):
    n = A
    sl = A["_sl"]
    E = {("start", "rim_s"), ("rim_s", "dishE"), ("dishE", "dishW"), ("dishW", "srv"), ("rim_n", "srv")}
    if sl < 0.5:                                # doors shut: they bridge the silo (the short route)
        E |= {("rim_s", "doorR"), ("doorR", "doorL"), ("doorL", "rim_n")}
    if A["_rise"] > 0.55:                       # the rocket up: a node on its nose, a launch link to the server
        E |= {("rim_s", "rocket"), ("rocket", "srv")}
    return E, set(), {"doorR": "ON THE DOOR", "doorL": "ON THE DOOR", "rocket": "ON THE ROCKET"}


def rc_rules(f, N, A):
    s = 0 if f < 4 else 1                       # one rehang per step: frames 0-3 = step s, 4-7 = step s+1
    E = {("start", "yard")}
    for k in (s % 6, (s + 3) % 6):
        E.add(("b%d" % k, "srv"))               # the mast (DISPATCH CORE) is cabled to 2 relays
    for k in ((s + 1) % 6, (s + 4) % 6):
        E.add(("yard", "b%d" % k))              # the courtyard reaches 2 relays
    E |= {("b%d" % k, "b%d" % ((k + 1) % 6)) for k in range(6) if k in ((s + 1) % 6, (s + 4) % 6)}
    return E, set(), {}


CORPS = {
    "meridian": dict(tag="meridian_hq", N=20, frames=list(range(20)), key=6, rules=mer_rules, walked=["start", "g2", "y2"],
                     kinds={"g1": "router", "g2": "router", "t1": "terminal", "t2": "elite", "t3": "modem", "y1": "router", "y2": "terminal",
                            "crane": "elite", "car0": "modem", "car2": "elite", "srv": "rack"},
                     srv="THE MASTER MANIFEST", title="MERIDIAN: CRANE + TRAIN",
                     rule="STEP CLOCK: the crane lowers its node onto the train in 2 steps; the train leaves next step and returns 2 steps later."),
    "solace": dict(tag="solace_hq", N=12, frames=list(range(12)), key=0, rules=sol_rules, walked=["start", "pod0"],
                   kinds={**{"pod%d" % k: ("terminal" if k % 2 else "router") for k in range(6)}, **{"w%d" % j: ["elite", "router", "modem", "router", "elite", "terminal"][j]
                                                                                                         for j in range(6)}, "srv": "rack"},
                   srv="THE GENOME CORE", title="SOLACE: THE HELIX TURNS",
                   rule="Every 2 steps the helix turns 60 deg: walkway docks re-align to the next podium pod."),
    "halcyon": dict(tag="halcyon_hq", N=12, frames=list(range(12)), key=0, rules=hal_rules, walked=["start", "R0", "R1"],
                    kinds={**{"L%d" % k: ["router", "terminal", "elite", "router", "modem", "elite"][k] for k in range(6)},
                           **{"R%d" % k: ["router", "router", "modem", "elite", "terminal", "router"][k] for k in range(6)}, "srv": "rack"},
                    srv="THE PANOPTICON", title="HALCYON: THE EYE SCANS",
                    rule="The eye turns 35 deg a step (left face > right face > back). Nodes in its beam are LOCKED; their links de-power."),
    "orbital": dict(tag="orbital_hq", N=12, frames=list(range(12)), key=0, rules=orb_rules, walked=["start", "rim_s"],
                    kinds={"rim_s": "router", "doorR": "elite", "doorL": "router", "rim_n": "terminal", "dishE": "modem", "dishW": "router",
                           "rocket": "elite", "srv": "rack"},
                    srv="LAUNCH CONTROL", title="ORBITAL: SILO DOORS",
                    rule="Every 3 steps the silo cycles: doors SHUT = bridge route across; doors OPEN = the rocket node + launch link."),
    "rebel_cell": dict(tag="rebel_cell_hq_dispatch", N=1, frames=[0] * 8, key=0, rules=rc_rules, walked=["start", "yard"],
                       kinds={**{"b%d" % k: ["router", "elite", "terminal", "modem", "router", "elite"][k] for k in range(6)}, "yard": "router",
                              "srv": "rack"},
                       srv="DISPATCH CORE", title="DISPATCH: THE REHANG",
                       rule="Each step DISPATCH rehangs its cables: the mast + courtyard links jump one relay clockwise."),
}


# ------------------------------------------------------------------ frame assembly
def prep_passes(tag, N):
    """Per-frame data passes: the moving corps rendered them per frame; the others share the anim set."""
    for f in range(N):
        v = "%s_f%02d" % (tag, f)
        for k in ("normal", "id", "depth"):
            dst = os.path.join(BL, "%s_%s.png" % (v, k))
            src = os.path.join(BL, "%s_anim_%s.png" % (tag, k))
            if not os.path.exists(dst) and os.path.exists(src):
                shutil.copyfile(src, dst)


_bd = {}


def backdrop(tag, f):
    key = (tag, f)
    if key not in _bd:
        im = BD.finish("%s_f%02d" % (tag, f), "night").convert("RGBA")
        _bd[key] = im
    return _bd[key].copy()


OVERRIDE = {"halcyon_hq": {"srv": (0.0, -5.0, 62.6)}}  # node world positions moved after the render (projected by the fit)


def anchors(tag, f):
    a = json.load(open(os.path.join(BL, "%s_f%02d_anchors.json" % (tag, f))))
    if tag in OVERRIDE:  # the camera is orthographic: screen = affine(world); fit it from the rendered anchors
        ks = list(a["nodes"])
        Wm = np.array([a["nodes"][k]["w"] + [1.0] for k in ks])
        Cm = np.array([a["nodes"][k]["c"] for k in ks])
        M, *_ = np.linalg.lstsq(Wm, Cm, rcond=None)
        for k, p in OVERRIDE[tag].items():
            c = np.array(list(p) + [1.0]) @ M
            a["nodes"][k] = dict(c=[float(c[0]), float(c[1])], w=list(p))
    return a


def edge_on_history(rules, frames, A_by_frame, gi, N):
    """Edges on in gif frame gi, gi-1, gi-2 (cyclic)."""
    out = []
    for d in (0, 1, 2):
        g = (gi - d) % len(frames)
        E, _, _ = rules(g if len(set(frames)) > 1 else g, N, A_by_frame[g])
        out.append(E)
    return out


def node_states(nodes, E, walked, locked):
    cur = walked[-1]
    adj = {}
    for a, b in E:
        adj.setdefault(a, []).append(b)
    opts = set(adj.get(cur, []))
    seen, todo = set(), [cur]
    while todo:
        for b in adj.get(todo.pop(), []):
            if b not in seen:
                seen.add(b)
                todo.append(b)
    st = {}
    for k in nodes:
        if k in walked:
            st[k] = "walked"
        elif k in locked:
            st[k] = "locked"
        elif k in opts:
            st[k] = "option"
        elif k in seen:
            st[k] = "white"
        else:
            st[k] = "grey"
    return st


RING = {"walked": LIME, "option": ORANGE, "white": WHITE, "grey": DIM, "locked": RED}


def compose(corp, gi):
    C = CORPS[corp]
    frames = C["frames"]
    f = frames[gi]
    tag = C["tag"]
    A_by = []
    for g, fr in enumerate(frames):
        a = anchors(tag, fr)
        nd = {k: v for k, v in a["nodes"].items()}
        nd["_eye"] = a.get("eye") or 0.0
        if corp == "orbital":
            nd["_sl"] = max(0.0, min(1.0, (lambda u: u * u * (3 - 2 * u))(max(0.0, min(1.0, (fr - 2) / 4.0)))))
            nd["_rise"] = (lambda u: u * u * (3 - 2 * u))(max(0.0, min(1.0, (fr - 5) / 5.0)))
        A_by.append(nd)
    hist = []
    for d in (0, 1, 2):
        g = (gi - d) % len(frames)
        hist.append(C["rules"](g if corp == "rebel_cell" else frames[g], C["N"], A_by[g]))
    (E, locked, chips), (E1, _, _), (E2, _, _) = hist
    A = A_by[gi]
    nodes = {k: v for k, v in A.items() if not k.startswith("_")}
    if corp == "orbital" and A["_sl"] > 0.8:
        nodes.pop("doorL", None)
        nodes.pop("doorR", None)
    if corp == "orbital" and A["_rise"] < 0.35:
        nodes.pop("rocket", None)
    img = backdrop(tag, f)
    img = SL.over(img, (6, 5, 12), Image.new("L", img.size, 40))  # a touch darker under the inlay
    walked = C["walked"]
    st = node_states(nodes, {e for e in E if e[0] in nodes and e[1] in nodes}, walked, locked)
    walked_e = set(zip(walked[:-1], walked[1:]))
    P = {k: tuple(v["c"]) for k, v in nodes.items()}
    inl = U.Inlay()
    sparks = []
    # links that de-power (on 1-2 frames ago, off now)
    for e in (E1 | E2) - E:
        a, b = e
        if a in P and b in P:
            age = 1 if e in E1 else 2
            inl.trace([P[a], P[b]], (110, 40, 50) if age == 1 else (60, 40, 50), width=2.0, lanes=2, gap=4.0, glow=0.25 if age == 1 else 0.0,
                      alpha=0.85 if age == 1 else 0.45, pads=False)
            for t in (0.3, 0.55, 0.8) if age == 1 else (0.5,):
                sparks.append((P[a][0] + (P[b][0] - P[a][0]) * t, P[a][1] + (P[b][1] - P[a][1]) * t))
    heads = []
    for a, b in E:
        if a not in P or b not in P or (a, b) in walked_e:
            continue
        sa, sb = st.get(a), st.get(b)
        if a == walked[-1]:
            col, w, ln, gl, al = ORANGE, 2.6, 3, 0.9, 1.0
        elif sa in ("white", "option", "walked") and sb in ("white", "option"):
            col, w, ln, gl, al = WHITE, 2.0, 2, 0.15, 0.85
        else:
            col, w, ln, gl, al = GREY, 1.8, 2, 0.0, 0.75
        pa, pb = P[a], P[b]
        if (a, b) not in E1:            # being remade: half drawn this frame, a bright head
            t = 0.5
            pb2 = (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
            inl.trace([pa, pb2], col, width=w + 0.6, lanes=ln, gap=4.0, glow=1.0, alpha=al, pads=False)
            heads.append(pb2)
        elif (a, b) not in E2:          # second frame: almost done
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
            a = (k * 72 + gi * 37) % 360
            r = 6 + (k * 3 + gi) % 7
            d.line([(x, y), (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))], fill=(255, 90, 80, 230), width=2)
    for (x, y) in heads:
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 240, 255))
    # nodes
    for k in sorted(nodes, key=lambda k: P[k][1]):
        s = st[k]
        cx, cy = P[k]
        r = 22 if k != "srv" else 34
        img = U.pad(img, [(cx, cy - r * 0.5), (cx + r, cy), (cx, cy + r * 0.5), (cx - r, cy)], RING[s], lit=0.9, glow=0.5, fill_a=210, k=0.8)
    for k in sorted(nodes, key=lambda k: P[k][1]):
        if k == "start":
            continue
        s = st[k]
        cx, cy = P[k]
        px = 80 if k == "srv" else 48
        img = L.place_sticker(img, U.node_sd(C["kinds"][k], px), cx, cy - 24, angle=((sum(map(ord, k)) % 9) - 4) * 0.8,
                              opacity=0.8 if s == "grey" else 1.0, hover=0.35 if s == "option" else 0.0)
        img = ring(img, cx, cy - 24, px * 0.62, RING[s], w=5 if s in ("option", "locked") else 4, glow=0.9 if s in ("option", "locked") else 0.3)
        if k in chips:
            img = U.chip(img, (cx, cy + 20), chips[k], RED if chips[k] == "LOCKED" else U.CYAN, 12)
    sx, sy = P["srv"]
    img = U.chip(img, (sx, sy + 66), "CENTRAL SERVER  //  " + C["srv"], GOLD, 15, bright=True)
    pr = L.pen(L.GP_RED, seed=421)
    pr.circle(sx, sy - 26, 78, 64, width=9)
    pr.text(C["srv"], sx + 30, sy - 130, 30, angle=-5)
    img = L.ink(img, pr)
    cx, cy = P[walked[-1]]
    img = L.place_sticker(img, U.token_sd(50), cx + 30, cy - 66, angle=-14, hover=0.6)
    # HUD: title sticker + the rule terminal
    img = L.place_sticker(img, L.sticker_word([C["title"]], 44, fills=["yellow"], seed=422), 380, 56, angle=-2)
    c = L.CRT(1180, 74, U.CYAN, "HQ MECHANIC", tag="STEP %d" % (1 if gi < len(frames) // 2 else 2), seed=423)
    c.text((16, 46), C["rule"], 15, (225, 235, 240))
    img = L.paste(img, c.finish(scan=0.15), 20, 990)
    lg = L.CRT(560, 44, U.CYAN, None, header=False, seed=424)
    x0 = 14
    for col, s_ in ((LIME, "walked"), (ORANGE, "selectable"), (WHITE, "not yet"), (DIM, "cut off"), (RED, "locked")):
        lg.d.ellipse([x0, 12, x0 + 18, 30], outline=col + (255,), width=3)
        x0 += 24 + int(lg.text((x0 + 24, 12), s_, 14, (215, 225, 230))) + 18
    img = L.paste(img, lg.finish(scan=0.15), 1340, 1020)
    return img


def run(corp):
    C = CORPS[corp]
    prep_passes(C["tag"], C["N"])
    frames = []
    for gi in range(len(C["frames"])):
        frames.append(compose(corp, gi).convert("RGB"))
        print(corp, "frame", gi, flush=True)
    still = frames[C["key"]]
    L.save(L.bloom(still.convert("RGBA"), 0.12, 0.8, 8), "hq_%s_compound.png" % corp)
    durs = [700 if i in (0, len(frames) - 1) else 180 for i in range(len(frames))]
    if corp == "meridian":
        frames = frames[::2]
        durs = [260] * len(frames)
    if corp == "rebel_cell":
        durs = [900, 300, 300, 300, 900, 300, 300, 300]
    p = os.path.join(OUT, "hq_%s_mechanic.gif" % corp)
    print(corp, "gif KB", U.save_gif(frames, durs, p, size=(960, 540), colors=150) // 1024, flush=True)


if __name__ == "__main__":
    for corp in (sys.argv[1:] or list(CORPS)):
        run(corp)
