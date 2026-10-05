"""Round 43: DISPATCH (the REBEL_CELL boss run in the Cell's own alley base) - four final-experience ideas.

Backdrop: round34_rebel_cell/canyon_dispatch.jpg (the locked Tokyo-alley DISPATCH base, read-only).
  1 SYNC STRIKE   three operatives run at once; three lock nodes must be hit on the SAME step   (gif)
  2 MIRROR RUN    DISPATCH runs a copy of you (your wheel, your firmware) one step behind
  3 THE PLAYBOOK  DISPATCH learns: every card you play is PATCHED for the rest of the run
  4 MEMORY LANE   the alley is rebuilt from the Sites you cleared; delete memories to open the way
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance

import compound43 as C
import compound42 as K
import r31lib as L
import r32ui as U
import sticker_lib19 as SL

OUT = K.OUT
SRC = os.path.join(OUT, "..", "round34_rebel_cell", "canyon_dispatch.jpg")
RED = (255, 52, 64)
OPS = {"breaker": ((255, 61, 168), "BREAKER"), "ghost": ((92, 225, 255), "GHOST"), "rigger": ((123, 224, 123), "RIGGER")}
_tok = {}


def base():
    im = Image.open(SRC).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.78).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 960, 46], fill=(14, 10, 18, 255))  # cover the round 34 caption bar
    return im


def token(op, px=50):
    if (op, px) not in _tok:
        col = OPS[op][0]
        _tok[(op, px)] = L.sticker_from_art(L.glyph("slice_exploit", px, fill=col, ow=4), border=6, seed=hash(op) % 97)
    return _tok[(op, px)]


def node(n, c):
    return {"c": list(c), "w": [0, 0, 0]}


def panel(img, title, lines, x=1300, y=560, w=600, col=(255, 70, 80)):
    c = L.CRT(w, 64 + 24 * len(lines), col, title, seed=sum(map(ord, title)) % 97)
    for i, s in enumerate(lines):
        c.text((16, 48 + 24 * i), s, 16, (230, 230, 240))
    return L.paste(img, c.finish(scan=0.15), x, y)


def idea_title(img, n, title):
    return L.place_sticker(img, L.sticker_word(["DISPATCH %d: %s" % (n, title)], 40, fills=[("grad", (255, 96, 96), (196, 20, 32))], seed=440 + n),
                           440, 40, angle=-2)


# ------------------------------------------------------------------ 1 SYNC STRIKE
LANES = {"breaker": [(960, 1000), (955, 820), (965, 640), (960, 470)],   # the alley (the red cable lane)
         "ghost": [(720, 960), (700, 780), (730, 600), (750, 440)],      # left rooftops
         "rigger": [(1210, 960), (1240, 780), (1215, 610), (1190, 440)]}  # right rooftops
CORE = (1115, 235)


def sync_nodes():
    n = {}
    for op, pts in LANES.items():
        for i, p in enumerate(pts):
            n["%s%d" % (op[0], i)] = node(None, p)
    n["srv"] = node(None, CORE)
    return n


SYNC_KINDS = {"b0": "router", "b1": "elite", "b2": "router", "b3": "rack", "g0": "terminal", "g1": "router", "g2": "elite", "g3": "rack",
              "r0": "modem", "r1": "router", "r2": "elite", "r3": "rack", "srv": "rack"}
# per gif frame: lane positions (index along each lane), which locks are hit, label
SYNC_SEQ = [
    (dict(breaker=0, ghost=0, rigger=0), set(), "three operatives jack in at once"),
    (dict(breaker=1, ghost=1, rigger=1), set(), "you move ALL THREE each step"),
    (dict(breaker=2, ghost=2, rigger=1), set(), "Rigger stopped: DISPATCH counters its firmware"),
    (dict(breaker=3, ghost=2, rigger=2), {"b3"}, "Breaker hits lock 1 ALONE..."),
    (dict(breaker=3, ghost=2, rigger=2), {"b3x"}, "...lock 1 RE-ARMS (not in sync)"),
    (dict(breaker=3, ghost=3, rigger=3), set(), "all three on their lock nodes"),
    (dict(breaker=3, ghost=3, rigger=3), {"b3", "g3", "r3"}, "SYNC: all three locks hit on the same step"),
    (dict(breaker=3, ghost=3, rigger=3), {"b3", "g3", "r3", "open"}, "the core opens to ONE runner: you pick Breaker"),
    (dict(breaker=4, ghost=3, rigger=3), {"b3", "g3", "r3", "open"}, "Breaker vs DISPATCH (the others hold the locks)"),
]


def sync_frame(i):
    pos, hit, label = SYNC_SEQ[i]
    img = base()
    n = sync_nodes()
    E = set()
    for op, pts in LANES.items():
        for j in range(3):
            E.add(("%s%d" % (op[0], j), "%s%d" % (op[0], j + 1)))
    if "open" in hit:
        E |= {("b3", "srv"), ("g3", "srv"), ("r3", "srv")}
    walked = ["b%d" % k for k in range(min(pos["breaker"], 3) + 1)]
    img, st, P = C.draw_state(img, n, E, E, E, walked, SYNC_KINDS, srv_name="DISPATCH CORE", hide_srv=False,
                              token_at=(-999, -999))
    d = ImageDraw.Draw(img)
    for op, pts in LANES.items():  # the other runners' walked trails (their own colour)
        col = OPS[op][0]
        k = min(pos[op], 3)
        for j in range(k):
            d.line([pts[j], pts[j + 1]], fill=col + (255,), width=6)
    for op in ("ghost", "rigger", "breaker"):
        k = pos[op]
        x, y = (CORE if k >= 4 else LANES[op][k])
        img = L.place_sticker(img, token(op), x + 30, y - 64, angle=-14, hover=0.6)
        img = U.chip(img, (x + 30, y - 106), OPS[op][1], OPS[op][0], 12)
    for op, key in (("breaker", "b3"), ("ghost", "g3"), ("rigger", "r3")):
        x, y = LANES[op][3]
        if key in hit:
            img = K.ring(img, x, y - 22, 46, (255, 230, 80), w=7, glow=1.2)
            img = U.chip(img, (x, y + 24), "LOCK HIT", (255, 230, 80), 13, bright=True)
        elif key + "x" in hit:
            img = K.ring(img, x, y - 22, 46, RED, w=7, glow=1.2)
            img = U.chip(img, (x, y + 24), "RE-ARMED", RED, 13, bright=True)
        else:
            img = U.chip(img, (x, y + 24), "LOCK %s" % {"b3": 1, "g3": 2, "r3": 3}[key], RED, 12)
    if "open" in hit:
        img = K.ring(img, CORE[0], CORE[1] - 26, 90, (255, 230, 80), w=8, glow=1.4)
    if pos["rigger"] == 1 and i == 2:
        x, y = LANES["rigger"][1]
        img = L.place_sticker(img, L.sticker_word(["COUNTERED"], 28, fills=[("grad", (255, 96, 96), (196, 20, 32))], seed=451), x + 80, y - 40, angle=6)
    img = idea_title(img, 1, "SYNC STRIKE")
    img = panel(img, "THE RULE", ["3 operatives run 3 lanes at once (you move each).", "The core's 3 locks must be hit on the SAME step;",
                                  "a lone hit re-arms next step. DISPATCH counters", "whatever it has seen (it knows your firmware).",
                                  "Open: ONE runner goes in; the others hold the locks."], x=1290, y=600)
    img = U.chip(img, (960, 1046), "STEP %d   //   %s" % (i + 1, label.upper()), U.CYAN, 17)
    return img


# ------------------------------------------------------------------ 2 MIRROR RUN
def mirror():
    img = base()
    pts = [(960, 1000), (955, 840), (720, 760), (705, 600), (960, 520), (1215, 450), (1190, 330)]
    n = {"n%d" % i: node(None, p) for i, p in enumerate(pts)}
    n["srv"] = node(None, CORE)
    E = {("n%d" % i, "n%d" % (i + 1)) for i in range(len(pts) - 1)} | {("n6", "srv"), ("n3", "srv")}
    walked = ["n0", "n1", "n2", "n3", "n4"]
    img, st, P = C.draw_state(img, n, E, E, E, walked, {**{"n%d" % i: ["router", "elite", "terminal", "router", "modem", "elite", "router"][i] for i in range(7)},
                                                         "srv": "rack"}, srv_name="DISPATCH CORE")
    d = ImageDraw.Draw(img)
    for a, b in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[3])):
        d.line([a, b], fill=(255, 40, 50, 255), width=7)
    for k in (0, 1, 2):
        img = K.ring(img, pts[k][0], pts[k][1] - 22, 30, RED, w=5, glow=0.9)
        img = U.chip(img, (pts[k][0], pts[k][1] + 22), "RETAKEN", RED, 12)
    ghost = L.sticker_from_art(L.glyph("slice_exploit", 50, fill=(255, 40, 50), ow=4), border=6, seed=7)
    x, y = pts[3]
    img = L.place_sticker(img, ghost, x + 30, y - 64, angle=14, hover=0.6, opacity=0.85)
    img = U.chip(img, (x + 30, y - 106), "YOU (DISPATCH'S COPY)", RED, 12)
    img = idea_title(img, 2, "MIRROR RUN")
    img = panel(img, "THE RULE", ["DISPATCH runs YOU: a copy of your operative, your", "wheel, deck and firmware, one step behind.",
                                  "Every node you leave it RETAKES (red). If it lands", "on you: a mirror fight against your own build.",
                                  "Outpace it, or turn and fight it on your terms."], x=1290, y=600)
    return img


# ------------------------------------------------------------------ 3 THE PLAYBOOK
def playbook():
    img = base()
    pts = [(960, 1000), (720, 820), (1210, 820), (960, 640), (720, 470), (1200, 470)]
    n = {"n%d" % i: node(None, p) for i, p in enumerate(pts)}
    n["srv"] = node(None, CORE)
    E = {("n0", "n1"), ("n0", "n2"), ("n1", "n3"), ("n2", "n3"), ("n3", "n4"), ("n3", "n5"), ("n4", "srv"), ("n5", "srv")}
    walked = ["n0", "n1", "n3"]
    img, st, P = C.draw_state(img, n, E, E, E, walked, {"n0": "router", "n1": "elite", "n2": "terminal", "n3": "router", "n4": "elite", "n5": "modem",
                                                         "srv": "rack"}, srv_name="DISPATCH CORE")
    for k, txt in (("n4", "COUNTERS: HEAVY SPIN"), ("n5", "COUNTERS: ZERO-DAY")):
        img = U.chip(img, (P[k][0], P[k][1] + 24), txt, RED, 12)
    y = 860
    for i, (name, patched) in enumerate((("HEAVY SPIN", True), ("FLICK", False), ("ZERO-DAY", True), ("GHOST STEP", False), ("BULWARK", True))):
        x = 300 + i * 150
        card = Image.new("RGBA", (120, 160), (0, 0, 0, 0))
        dc = ImageDraw.Draw(card)
        dc.rounded_rectangle([0, 0, 119, 159], radius=12, fill=(40, 34, 48, 255), outline=(240, 236, 226, 255), width=4)
        dc.text((60, 30), name.split()[0], font=L.f_num(24), fill=(255, 214, 64, 255), anchor="mm")
        if len(name.split()) > 1:
            dc.text((60, 56), name.split()[1], font=L.f_num(24), fill=(255, 214, 64, 255), anchor="mm")
        sd = L.sticker_from_art(card, border=6, seed=i + 3)
        img = L.place_sticker(img, sd, x, y + (i % 2) * 10, angle=(i - 2) * 4)
        if patched:
            st_ = L.stamp("PATCHED", 26, angle=-14)
            img = L.paste(img, st_, x - st_.width // 2, y - 10)
    img = idea_title(img, 3, "THE PLAYBOOK")
    img = panel(img, "THE RULE", ["DISPATCH has every slice and firmware you ever used,", "and it LEARNS: each card you play is PATCHED for",
                                  "the rest of the run (stamped, unplayable). Nodes", "ahead show what they counter. Spend your best tricks",
                                  "late, or bait it with the ones you can lose."], x=1290, y=600)
    return img


# ------------------------------------------------------------------ 4 MEMORY LANE
def memory():
    img = base()
    pts = [(960, 1000), (720, 840), (1210, 830), (960, 690), (715, 560), (1205, 560), (960, 430)]
    names = ["THE OLD SAFEHOUSE", "FIRST RACK", "RELAY ROOFTOP", "MEMORIAL WALL", "STREET KITCHEN", "THE ARMORY", "DEAD DROP BOX"]
    n = {"n%d" % i: node(None, p) for i, p in enumerate(pts)}
    n["srv"] = node(None, CORE)
    E = {("n0", "n1"), ("n0", "n2"), ("n1", "n3"), ("n2", "n3"), ("n3", "n4"), ("n3", "n5"), ("n4", "n6"), ("n5", "n6"), ("n6", "srv"), ("n1", "n4")}
    walked = ["n0", "n2", "n3"]
    img, st, P = C.draw_state(img, n, E, E, E, walked, {"n%d" % i: ["router", "elite", "terminal", "router", "modem", "elite", "rack"][i] for i in range(7)} |
                              {"srv": "rack"}, srv_name="DISPATCH CORE")
    for i, nm in enumerate(names):
        img = U.chip(img, (P["n%d" % i][0], P["n%d" % i][1] + 24), nm, U.CYAN, 12)
    p = L.pen(L.GP_RED, seed=461)
    x, y = P["n5"]
    p.stroke([(x - 60, y - 70), (x + 60, y + 30)], width=9)
    p.stroke([(x + 60, y - 70), (x - 60, y + 30)], width=9)
    p.text("DELETE? (lose its loot)", x - 40, y - 110, 26, angle=-4)
    img = L.ink(img, p)
    img = idea_title(img, 4, "MEMORY LANE")
    img = panel(img, "THE RULE", ["The alley is rebuilt from the Sites YOU cleared this", "campaign, each held by its old enemy now running",
                                  "your firmware. DELETE a memory to cut through it", "(open a shortcut) - and lose that Site's reward",
                                  "for good. How much of your history will you burn?"], x=1290, y=600)
    return img


def main():
    for i, (fn, name) in enumerate(((lambda: sync_frame(6), "sync_strike"), (mirror, "mirror_run"), (playbook, "the_playbook"), (memory, "memory_lane"))):
        L.save(L.bloom(fn().convert("RGBA"), 0.12, 0.8, 8), "dispatch_idea_%d_%s.png" % (i + 1, name))
    frames = [sync_frame(i).convert("RGB") for i in range(len(SYNC_SEQ))]
    durs = [900, 700, 900, 800, 900, 700, 1100, 1100, 1300]
    p = os.path.join(OUT, "dispatch_sync_strike.gif")
    print("dispatch gif KB", U.save_gif(frames, durs, p, size=(960, 540), colors=150) // 1024, flush=True)


if __name__ == "__main__":
    main()
