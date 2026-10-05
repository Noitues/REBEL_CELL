"""Round 35 -> transit_view.png (Heat A), transit_view_heat_b.png (Heat B), transit_step.gif.

The Site run along the link, rendered in the ONE iso building language (iso_scene.py: individual buildings per lot, the
city map's camera, zoomed in). No planning marks, no NEXT panel, no reward preview. Node TYPE reads from the sticker.
  walked / current   lime (the current node carries the operative token)
  available now      Meridian orange: every out-edge of the current node (the graph decides how many)
  not yet            WHITE pads + white-washed stickers (still readable)
  past / cut off     GREY pads + greyscale stickers (kept, never removed)
The Site's info window is the same as the city map's. The guardian keeps its red circle and name.

python transit_view.py [png|gif|all]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV

KINDS = {}
WALKED = ["start", "1_2", "2_1"]


def load(path="iso_transit_anchors.json", idx=None):
    A = json.load(open(os.path.join(U.BL, path)))
    if idx is not None:
        A = A[idx]
    for l, layer in enumerate(A["layers"]):
        for kind, r in layer:
            KINDS["%d_%d" % (l + 1, r)] = kind
    KINDS["final"] = "rack"
    return A


def reach_from(A, cur):
    g = {}
    for e in A["edges"]:
        g.setdefault(e["a"], []).append(e["b"])
    seen, todo = set(), [cur]
    while todo:
        for b in g.get(todo.pop(), []):
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


_wsd = {}


def white_sd(kind, px):
    key = (kind, px)
    if key not in _wsd:
        sd = dict(U.node_sd(kind, px))
        im = sd["img"]
        a = im.split()[3]
        w = Image.blend(im.convert("RGB"), Image.new("RGB", im.size, (246, 244, 250)), 0.55).convert("RGBA")
        w.putalpha(a)
        sd["img"] = w
        _wsd[key] = sd
    return _wsd[key]


def states(A, walked, current):
    reach = reach_from(A, current)
    opts = [e["b"] for e in A["edges"] if e["a"] == current]
    st = {}
    for k in A["nodes"]:
        if k == current:
            st[k] = "current"
        elif k in walked:
            st[k] = "walked"
        elif k in opts:
            st[k] = "option"
        elif k in reach:
            st[k] = "white"
        else:
            st[k] = "past"
    return st, opts


COLS = {"walked": R.LIME, "current": R.LIME, "option": R.MER, "white": R.WHITE, "past": R.GREY}


def compose(bg, A, walked, current, move=None, heat="A", ui=1.0, flash=None):
    img = bg.convert("RGBA")
    img = ImageEnhance.Brightness(img).enhance(0.82)
    nodes = A["nodes"]
    if move and move[1] >= 0.99:
        walked, current, move = walked + [move[0]], move[0], None
    st, opts = states(A, walked, current)
    walked_e = set(zip(walked[:-1], walked[1:]))
    moving = (current, move[0]) if move else None
    inl = U.Inlay()
    sx, sy = nodes["start"]["c"]
    inl.trace([(sx - 400, sy + 230), (sx, sy)], R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0, pads=False)
    for e in A["edges"]:
        key = (e["a"], e["b"])
        if key in walked_e or key == moving:
            continue
        if e["a"] == current:
            inl.trace(e["pts"], R.MER, width=2.6, lanes=3, gap=4.0, glow=0.9)
        elif st.get(e["a"]) in ("white", "option") and st.get(e["b"]) in ("white", "option"):
            inl.trace(e["pts"], R.WHITE, width=1.8, lanes=2, gap=4.0, glow=0.15, alpha=0.8)
        else:
            inl.trace(e["pts"], R.GREY, width=1.6, lanes=2, gap=4.0, glow=0.0, alpha=0.7)
    for e in A["edges"]:
        if (e["a"], e["b"]) in walked_e:
            inl.trace(e["pts"], R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0)
    tok = nodes[current]["c"]
    if move:
        e = next(e for e in A["edges"] if e["a"] == current and e["b"] == move[0])
        if move[1] > 0.01:
            inl.trace(U.cut_poly(e["pts"], 0, move[1]), R.LIME, width=2.8, lanes=3, gap=4.5, glow=1.0)
        inl.trace(U.cut_poly(e["pts"], move[1], 1), R.MER, width=2.6, lanes=3, gap=4.0, glow=0.9)
        tok = U.point_at(e["pts"], move[1])
    img = inl.lay(img)
    order = sorted(nodes, key=lambda k: nodes[k]["c"][1])
    for k in order:
        s = st[k] if k != "start" else "walked"
        q = [tuple(p) for p in nodes[k]["d"]]
        cx, cy = nodes[k]["c"]
        if k in ("start", "final"):
            q = [(cx + (x - cx) * 1.3, cy + (y - cy) * 1.3) for (x, y) in q]
        img = U.pad(img, q, COLS[s], lit={"walked": 0.9, "current": 1.0, "option": 1.0, "white": 0.85, "past": 0.6}[s],
                    glow={"option": 0.9, "current": 1.0, "walked": 0.5}.get(s, 0.08), fill_a=215)
        if k == "start":
            ic = CV_icon()
            img.alpha_composite(ic, (int(cx - ic.width / 2), int(cy - ic.height / 2)))
    for k in order:
        if k == "start":
            continue
        s = st[k]
        cx, cy = nodes[k]["c"]
        px = 96 if k == "final" else {"walked": 46, "current": 54, "option": 62, "white": 50, "past": 46}[s]
        ang = ((sum(map(ord, k)) % 9) - 4) * 0.8
        if s == "white":
            sd = white_sd(KINDS[k], px)
        else:
            sd = U.node_sd(KINDS[k], px, grey=(s == "past"))
        if flash and k in flash:  # the newly available nodes pop out of white
            img = L.place_sticker(img, sd, cx, cy - 30 - 10 * flash[k], angle=ang, scale=1 + 0.12 * flash[k], hover=0.5 * flash[k])
        else:
            img = L.place_sticker(img, sd, cx, cy - (44 if k == "final" else 26), angle=ang,
                                  opacity=0.85 if s == "past" else 1.0, hover=0.35 if s == "option" else 0.0)
    fx, fy = nodes["final"]["c"]
    pr = L.pen(L.GP_RED, seed=352)
    pr.circle(fx, fy - 26, 92, 76, width=10)
    pr.text("PORT AUTHORITY", fx + 150, fy + 70, 30, angle=-4)
    img = L.ink(img, pr)
    tx, ty = tok
    img = L.place_sticker(img, U.token_sd(54), tx + 28, ty - 70, angle=-14, hover=0.6)
    img = U.chip(img, (sx - 110, sy + 6), "RELAY 4", R.LIME, 14, bright=True)
    if heat == "B":
        img = R.heat_diegetic(img, [(1720, -40, 1180, 360, 120), (200, -60, 640, 520, 110)], [(1560, 610), (1000, 900)])
    if ui > 0:
        img = hud(img, heat, ui)
    return img


def CV_icon():
    import route_d_city as RC
    return RC.cell_icon("relay", 30, R.LIME)


def hud(img, heat, ui):
    base = img.copy()
    img = L.place_sticker(img, L.sticker_word(["NETRUN"], 64, fills=["yellow"], seed=63), 170, 62, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 41: WATCH LIST" if heat == "B" else None)
    dz = dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS)
    img = L.drop_shadow(img, dz, 22, 116, blur=14, off=(8, 12), op=0.6)
    img = R.node_info(img, (1480, 820, 1898, 1030), "DEPOT 15", "T1", ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    if heat == "A":
        img = R.heat_strip(img, (700, 22), 41, "NOTICED", w=520)
    img = U.term_button(img, (24, 980, 230, 1050), "DECK", "[D]")
    img = U.term_button(img, (242, 980, 448, 1050), "MENU", "[ESC]")
    if ui < 1:
        img = Image.blend(base.convert("RGB"), img.convert("RGB"), ui).convert("RGBA")
    return img


def main_png():
    A = load()
    bg = Image.open(os.path.join(U.FIN, "iso_transit.png"))
    for heat, name in (("A", "transit_view.png"), ("B", "transit_view_heat_b.png")):
        img = compose(bg, A, WALKED, "2_1", heat=heat)
        img = L.bloom(img, 0.14, 0.8, 8)
        L.save(img, name)


def main_gif():
    A = load()
    bg = Image.open(os.path.join(U.FIN, "iso_transit.png"))
    frames, durs = [], []
    frames.append(compose(bg, A, WALKED, "2_1"))
    durs.append(1500)
    for t in (0.2, 0.45, 0.7, 0.92):
        frames.append(compose(bg, A, WALKED, "2_1", move=("3_1", t)))
        durs.append(110)
    new = [e["b"] for e in A["edges"] if e["a"] == "3_1"]
    for f in (1.0, 0.5):
        frames.append(compose(bg, A, WALKED + ["3_1"], "3_1", flash={k: f for k in new}))
        durs.append(120)
    frames.append(compose(bg, A, WALKED + ["3_1"], "3_1"))
    durs.append(2000)
    out = os.path.join(L.OUT, "transit_step.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(960, 540)))


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "png"
    if w in ("png", "all"):
        main_png()
    if w in ("gif", "all"):
        main_gif()
