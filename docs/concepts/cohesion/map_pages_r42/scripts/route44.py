"""Round 44 A: the netrun route page, cleaned (REVIEW f, D14, Q4 designer ruling, Q15).

SOLID40=1 RUN_V3=1 NET36=net_scope.json python route44.py [page] [hover]
  page  -> route_page.png            only the links the route uses (walked + the edges to the next options)
  hover -> route_page_hover_all.png  hovering shows ALL links as thin 25 % white hairlines (nodes stay hidden)
Plate: t_run38 (run38.py), the round 38 v3 transit camera (ortho 130) on the unified city, finished with post40 at the
locked translucency v3 (SOLID40: opacity 0.68, x0.86, chroma x1.35) so the city keeps its violet hue (no grey slate).
"""
import math
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
os.environ.setdefault("RUN_V3", "1")
os.environ.setdefault("SOLID40", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import post40 as P  # noqa: E402
import layout36 as L  # noqa: E402
import transit38 as T  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402

P.Net36.runpath1 = T._runpath1
RM = T.RM
WALKED = ["L0_0", "L1_1", "L2_2"]
CUR = "L2_2"
HOVER = "L3_2"                        # the hovered option (a router: FIGHT)
KIND_WORD = {"router": "FIGHT", "elite": "ELITE", "terminal": "EVENT", "modem": "SHOP", "rack": "RACK"}


def prj(cam, lot):
    return L.project(cam, *L.W(lot), 0.0, 1920, 1080)


def plate():
    run = RM.load()
    st = RM.states(run, WALKED, CUR, False)
    E = {(e["a"], e["b"]): T.edge_state(e, st, WALKED) for e in run["edges"]}

    def deco(net):
        for l in P.NET["links"]:                       # the Cell's own network, dim, under the run
            if l["state"] == "owned":
                net.link(l["pts"], P.LINK_COL["owned"], k=0.3, packets=False)
        for e in run["edges"]:
            s = E[(e["a"], e["b"])]
            if s == "walked":
                net.runpath1(e["pts"], P.LIME, k=2.2, width=1.7, on=T.SOLID)
            elif s == "option":
                net.runpath1(e["pts"], P.ORANGE, k=1.8, width=1.1)
    nodes = {n["id"]: n for n in run["nodes"]}
    px, py = L.W(nodes["L5_1"]["lot"])
    img, cam = P.finish("t_run38", decorate=deco, pools=[(px, py, 16.0, 0.3)], t=0.2, sky=False)
    return KT.f2p(img), cam, run, st, E


def stickers(img, cam, run, st):
    nodes = {n["id"]: n for n in run["nodes"]}
    for n in sorted(run["nodes"], key=lambda n: prj(cam, n["lot"])[1]):
        s = st[n["id"]]
        if s == "hidden" or n["kind"] == "start":
            continue
        x, y = prj(cam, n["lot"])
        px = {"walked": 48, "current": 58, "option": 66, "target": 76}[s]
        sd = U32.node_sd(T.STK[n["kind"]], px)
        lift = 36 if s != "target" else 44
        hov = n["id"] == HOVER
        img = RL.place_sticker(img, sd, x, y - lift, angle=((sum(map(ord, n["id"])) % 9) - 4) * 0.8,
                               hover=0.55 if hov else (0.3 if s == "option" else 0.0))
        col = {"walked": KT.LIME, "current": KT.LIME, "option": KT.MER}.get(s)
        if col:
            img = T.S.ring(img, x, y - lift - (6 if hov else 0), px / 2 + 8, col, w=5 if s in ("option", "current") else 3,
                           glow={"option": 0.9, "current": 0.9, "walked": 0.5}.get(s, 0.0))
    # numbered next options (locked: the finite next step) as key hints, no words
    opts = sorted([i for i, s in st.items() if s == "option"], key=lambda i: prj(cam, nodes[i]["lot"])[0])
    for k, i in enumerate(opts):
        x, y = prj(cam, nodes[i]["lot"])
        img = U32.chip(img, (x - 46, y - 84), str(k + 1), KT.MER, 17, bright=True)
    # the operative token = YOU ARE HERE (no words)
    x, y = prj(cam, nodes[CUR]["lot"])
    img = RL.place_sticker(img, U32.token_sd(56), x + 34, y - 96, angle=-14, hover=0.6)
    return img, opts


def target(cam, run):
    nodes = {n["id"]: n for n in run["nodes"]}
    tx, ty = prj(cam, nodes["L7_0"]["lot"])
    pr = KT.pencil(KT.PEN_R, 381)
    pr.circle(tx, ty - 44, 74, 62, width=9)
    pr.text("TARGET", tx + 128, ty - 74, 34, angle=-6)
    return pr


def hairlines(img, cam, run, E):
    """Hover: every link of the run as a thin 25 % white hairline (designer ruling Q4 + Q15). Nodes stay hidden."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for e in run["edges"]:
        if E[(e["a"], e["b"])] in ("walked", "option"):
            continue
        pts = [prj(cam, p) for p in e["pts"]]
        d.line(pts, fill=(255, 255, 255, 64), width=2, joint="curve")
    img.alpha_composite(lay)
    return img


def topstrip(img):
    items = [dict(kind="heat", value=52, w=300), dict(kind="hp", label="HP", value="52", max="/60"),
             dict(kind="cycles", label="CYCLES", value="18")]
    img, box = KT.topbar(img, 250, 14, items, h=66)
    return img


def route_panel(img):
    box = (1636, 14, 1904, 168)
    img = KT.term(img, box, "ROUTE", seed=23)
    img = K.term_button(img, (1652, 56, 1888, 104), "GRID VIEW", "[G]")
    img = K.term_button(img, (1652, 112, 1888, 156), "Save & quit", None)
    return img


def dossier(img):
    R.TYPEF, R.TYPEB = K.COUR, K.COUR_B                  # Courier Prime (bible 2.9), not Courier New
    dz = R.dossier(heat_stamp=None)                       # the Heat number lives in the strip now (no duplicate stamp)
    dz = dz.resize((int(dz.width * 0.62), int(dz.height * 0.62)), Image.LANCZOS)
    return RL.drop_shadow(img, dz, 18, 120, blur=14, off=(6, 12), op=0.55)


def info_holo(img, cam, run):
    nodes = {n["id"]: n for n in run["nodes"]}
    n = nodes[HOVER]
    x, y = prj(cam, n["lot"])
    word = KIND_WORD[n["kind"]]
    w, h = 390, 262
    bx = int(x - 150)
    by = int(y - 426)
    box = (bx, by, bx + w, by + h)
    rows = [("TIER", "T1"), ("TYPE", "Fight: win it for Cycles and loot"), ("REWARDS", "15-25 Cycles, a card"), ("", "maybe a Firmware chip")]
    img = KT.holo_file(img, box, "%s  //  L%d" % (word, n["layer"]), rows, seed=12, key_w=96)
    return img, box, (x, y - 40)


def key_strip(img, hot):
    def ring(col):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"), ("terminal", "EVENT"),
                                                                   ("modem", "SHOP"), ("rack", "RACK"))]
    items += [(ring(KT.LIME), "walked"), (ring(KT.MER), "next")]
    hint = "SHOWING ALL LINKS" if hot else "HOVER: SHOW ALL LINKS"
    return KT.key_strip(img, 470, 1022, items, hint=hint, hot=hot)


def build(hover_all):
    base, cam, run, st, E = plate()
    img = base
    if hover_all:
        img = hairlines(img, cam, run, E)
    img, opts = stickers(img, cam, run, st)
    tpen = target(cam, run)
    img = dossier(img)
    img = KT.place_sticker(img, KT.sticker("NETRUN", 46, "yellow", seed=63), 122, 50, angle=-3)
    img = topstrip(img)
    img = route_panel(img)
    img, kbox = key_strip(img, hover_all)
    if hover_all:
        img = KT.cursor(img, kbox[2] - 120, kbox[1] + 14)
    else:
        img, hbox, cxy = info_holo(img, cam, run)
        img = KT.cursor(img, cxy[0] + 6, cxy[1] - 6)
    img = KT.spill(img, tpen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, tpen)
    return RL.bloom(img, 0.10, 0.84, 8)


if __name__ == "__main__":
    which = sys.argv[1:] or ["page", "hover"]
    if "page" in which:
        KT.save(build(False), "route_page.png")
    if "hover" in which:
        KT.save(build(True), "route_page_hover_all.png")
