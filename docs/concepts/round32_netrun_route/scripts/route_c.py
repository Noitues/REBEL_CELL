"""Round 32 -> route_c.png + route_c.gif: C, TRANSIT PATH. The link from the Cell's Relay 4 to Meridian Depot 15,
unrolled into a city corridor (Blender, r32_scene.py street). Four lanes, a cross street in every gap; route nodes are
circuit-inlay pads on the lanes, links are inlay traces that weave between lanes through the cross streets.

python route_c.py [png|gif]
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
import sticker_lib19 as SL

KINDS = {}


def load_anchors(anim=False):
    if anim:
        A = json.load(open(os.path.join(U.BL, "street_anim_anchors.json")))[-1]
    else:
        A = json.load(open(os.path.join(U.BL, "street_anchors.json")))
    for l, layer in enumerate(A["layers"]):
        for kind, r in layer:
            KINDS["%d_%d" % (l + 1, r)] = kind
    KINDS["final"] = "rack"
    return A


def graph(A):
    out = {}
    for e in A["edges"]:
        out.setdefault(e["a"], []).append(e["b"])
    return out


def reach_from(A, cur):
    g = graph(A)
    seen, todo = set(), [cur]
    while todo:
        n = todo.pop()
        for b in g.get(n, []):
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


def layer_of(k):
    return 0 if k == "start" else (7 if k == "final" else int(k.split("_")[0]))


def compose(bg, A, walked, current, move=None, show_opts=True, ui=1.0, pencil=True, step_t=None):
    """walked: node keys walked so far (ending with current). move: (target, t) = token travelling to target."""
    img = bg.convert("RGBA")
    # calm the far city and the near city a little so the corridor and the panels read
    img = L.darken_rect(img, (-200, -200, 2120, 330), a=110, blur=60)
    img = L.darken_rect(img, (-200, 790, 2120, 1300), a=150, blur=50)
    nodes = A["nodes"]
    reach = reach_from(A, current)
    walked_edges = set(zip(walked[:-1], walked[1:]))
    opts = [e for e in A["edges"] if e["a"] == current]
    # ---------------- traces
    inl = U.Inlay()
    sx, sy = nodes["start"]["c"]
    inl.trace([(-20, sy), (sx, sy)], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    for e in A["edges"]:
        key = (e["a"], e["b"])
        if key in walked_edges:
            continue
        if move and e["a"] == current and e["b"] == move[0]:
            continue
        if e["a"] == current:
            inl.trace(e["pts"], U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        elif e["a"] in reach and e["b"] in reach:
            inl.trace(e["pts"], U.MER, width=1.8, lanes=2, gap=4.0, glow=0.35, alpha=0.62)
        else:
            inl.trace(e["pts"], U.GREY, width=1.6, lanes=2, gap=4.0, glow=0.0, alpha=0.38)
    for e in A["edges"]:
        if (e["a"], e["b"]) in walked_edges:
            inl.trace(e["pts"], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    tok_xy = nodes[current]["c"]
    if move:
        e = next(e for e in A["edges"] if e["a"] == current and e["b"] == move[0])
        t = move[1]
        if t > 0.01:
            inl.trace(U.cut_poly(e["pts"], 0, t), U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
        if t < 0.99:
            inl.trace(U.cut_poly(e["pts"], t, 1), U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        tok_xy = U.point_at(e["pts"], t)
    img = inl.lay(img)
    # ---------------- pads
    order = sorted(nodes.keys(), key=lambda k: nodes[k]["c"][1])
    state = {}
    for k in order:
        if k == "start" or k in walked:
            st = "walked"
        elif k in [e["b"] for e in opts]:
            st = "option"
        elif k in reach:
            st = "reach"
        else:
            st = "cut"
        if k == current and not move:
            st = "current"
        if move and k == move[0] and move[1] >= 0.99:
            st = "current"
        state[k] = st
    for k in order:
        st = state[k]
        q = [tuple(p) for p in nodes[k]["d"]]
        if k == "final":
            cx, cy = nodes[k]["c"]
            q = [(cx + (x - cx) * 1.25, cy + (y - cy) * 1.25) for (x, y) in q]
        col = {"walked": U.LIME, "current": U.LIME, "option": U.MER, "reach": U.MER, "cut": U.GREY}[st]
        lit = {"walked": 0.85, "current": 1.0, "option": 1.0, "reach": 0.6, "cut": 0.4}[st]
        img = U.pad(img, q, col, lit=lit, glow=0.9 if st in ("current", "option") else 0.5)
    # ---------------- stickers (far first)
    for k in order:
        if k == "start":
            continue
        st = state[k]
        kind = KINDS[k]
        cx, cy = nodes[k]["c"]
        if k == "final":
            px, lift = 112, 50
        else:
            px = {"walked": 50, "current": 62, "option": 72, "reach": 62, "cut": 54}[st]
            lift = 26
        ang = ((sum(map(ord, k)) % 9) - 4) * 0.8
        sd = U.node_sd(kind, px, grey=(st == "cut"))
        img = L.place_sticker(img, sd, cx, cy - lift, angle=ang, opacity=0.78 if st == "cut" else 1.0,
                              hover=0.35 if st == "option" else 0.0)
    # the Cell's relay at the start: a terminal chip, not a node sticker (it is the Cell's own system)
    img = U.chip(img, (sx + 4, sy - 44), "RELAY 4", U.LIME, 15, anchor="mm")
    # layer ruler along the top of the corridor (terminal chips; the current layer lit)
    cur_l = layer_of(current if not (move and move[1] >= 0.99) else move[0])
    for l in range(1, 7):
        xs = [nodes[k]["c"][0] for k in nodes if k not in ("start", "final") and layer_of(k) == l]
        x = sum(xs) / len(xs)
        img = U.chip(img, (x, 382), "L%d" % l, U.LIME if l <= cur_l else U.CYAN, 15, bright=(l == cur_l))
    fx, fy = nodes["final"]["c"]
    img = U.chip(img, (fx, 382), "L7  SITE", U.MER, 15)
    # ---------------- grease pencil (plans yellow, threats red)
    if pencil:
        p = L.pen(L.GP_YELLOW, seed=91)
        if not move or move[1] >= 0.99:
            cur_k = current if not move else move[0]
            ccx, ccy = nodes[cur_k]["c"]
            p.circle(ccx, ccy - 8, 56, 40, width=9)
            if show_opts:
                opts2 = [e for e in A["edges"] if e["a"] == cur_k]
                opts2.sort(key=lambda e: nodes[e["b"]]["c"][1])
                for n, e in enumerate(opts2):
                    pts = e["pts"]
                    dashed_end = 0.86
                    U.dashed_along(p, pts, offset=-13 if n == 0 else 13, t0=0.18, t1=dashed_end)
                    bx, by = nodes[e["b"]]["c"]
                    p.text(str(n + 1), bx + 40, by - 66, 44, angle=-6)
        img = L.ink(img, p)
        pr = L.pen(L.GP_RED, seed=92)
        pr.circle(fx, fy - 30, 96, 84, width=10)
        pr.text("PORT AUTHORITY", fx + 40, fy + 92, 30, angle=-4)
        img = L.ink(img, pr)
    # ---------------- operative token
    tx, ty = tok_xy
    img = L.place_sticker(img, U.token_sd(56), tx + 30, ty - 74, angle=-14, hover=0.6)
    if ui > 0:
        ck = current if not (move and move[1] >= 0.99) else move[0]
        nxt = sorted([e["b"] for e in A["edges"] if e["a"] == ck], key=lambda k: nodes[k]["c"][1])
        ahead = [KINDS[k] for k in reach_from(A, ck) if k != "final"]
        img = hud(img, A, cur_l, ui, nxt, ahead, KINDS[ck])
    return img


def hud(img, A, cur_l, ui=1.0, nxt=(), ahead=(), here="elite"):
    base = img.copy()
    sd = L.sticker_word(["NETRUN"], 70, fills=["yellow"], seed=63)
    img = L.place_sticker(img, sd, 196, 70, angle=-3)
    strip = L.CRT(1000, 72, U.CYAN, None, header=False, seed=53)
    strip.text((16, 10), "LINK  //  RELAY 4 (CELL)  >  MERIDIAN DEPOT 15  //  T2  //  LAYER %d OF 7" % cur_l, 20, U.CYAN)
    strip.text((16, 42), "lime = walked, the Cell's now    orange = Meridian's    grey = cut off    pencil = your plan", 15, (150, 190, 200))
    img = L.paste(img, strip.finish(scan=0.15), 390, 34)
    # holo: decrypted Site intel
    hb = (1500, 112, 1898, 352)
    img = U.holo(img, hb, U.MER, "SITE 15  //  DEPOT 15", seed=5)
    img = U.meridian_seal(img, (1858, 150), 30)
    d = ImageDraw.Draw(img)
    rows = [("TIER", "T2"), ("EXPLOIT", "CUSTOMS KEYS (final Rack)"), ("GUARD", "PORT AUTHORITY"), ("ON CLEAR", "this link opens, raids too")]
    y = 190
    for a, b in rows:
        d.text((1518, y), a, font=L.f_mono(15), fill=(255, 200, 150, 255), anchor="lm")
        d.text((1612, y), b, font=L.f_ui(18, b"SemiBold"), fill=(255, 236, 214, 255), anchor="lm")
        y += 30
    img = U.chip(img, (1800, 330), "DECRYPTED // 7F-A2", U.LIME, 14)
    # RUNNER
    c = L.CRT(420, 250, U.PINK, "RUNNER", tag="CELL-9", seed=61)
    c.paste(L.glyph("slice_exploit", 40, fill=U.PINK, ow=3), 18, 56)
    c.text((80, 54), "CELL-9  BREAKER  R2", 20, (240, 240, 245))
    c.text((80, 80), "HP 44 / 60", 18, (255, 120, 150))
    c.bar(80, 106, 12, 9, w=20, h=12, gap=4, col=(255, 90, 130))
    c.text((20, 136), "DECK 17      CYCLES 86", 18, (200, 230, 240))
    c.rule(166, dash=True)
    c.text((20, 178), "UNBANKED: 2 assets, 1 daemon", 16, (255, 200, 80))
    c.text((20, 202), "banked at a Server Rack or on exit", 14, (160, 160, 150))
    img = L.paste(img, c.finish(), 24, 806)
    # NEXT
    c = L.CRT(540, 250, L.YEL, "NEXT", tag="FROM THE " + U.KIND[here]["name"], seed=62)
    rows = [(str(i + 1), KINDS[k], U.KIND[KINDS[k]]["name"], U.KIND[KINDS[k]]["sub"], "HEAT " + U.KIND[KINDS[k]]["heat"]) for i, k in enumerate(nxt)]
    y = 52
    for n, k, nm, sub, ht in rows:
        c.text((20, y), n, 40, L.YEL, fnt=L.f_num(44))
        c.paste(U.icon(k, 50), 56, y + 2)
        c.text((120, y + 2), nm, 22, (255, 255, 255), fnt=L.f_num(26))
        c.text((120, y + 34), sub, 15, (200, 190, 140))
        c.text((520, y + 8), ht, 17, L.HEAT if ht != "HEAT +0" else (150, 220, 150), anchor="ra")
        y += 70
    c.rule(y + 2, dash=True)
    c.text((20, y + 10), "ahead: " + U.ahead_text(ahead), 15, (170, 170, 150))
    c.text((20, y + 30), "end: SERVER RACK at the Site (guarded)", 15, U.MER)
    img = L.paste(img, c.finish(), 466, 806)
    # HEAT
    c = L.CRT(400, 250, L.HEAT, "HEAT", tag="CAMPAIGN", seed=63)
    c.text((22, 50), "52", 60, L.HEAT, fnt=L.f_num(76))
    c.text((120, 62), "FLAGGED", 22, (255, 170, 120))
    c.text((120, 92), "while >= 50: +1 resistance", 14, (200, 170, 150))
    bx, by, bw = 22, 146, 356
    c.d.rectangle([bx, by, bx + bw, by + 16], fill=(40, 20, 16, 255))
    c.d.rectangle([bx, by, bx + int(bw * 0.52), by + 16], fill=L.HEAT + (255,))
    for v in (25, 50, 75):
        x = bx + bw * v / 100
        c.d.line([(x, by - 6), (x, by + 22)], fill=(255, 230, 200, 255), width=2)
        c.text((x, by + 26), str(v), 13, (220, 190, 170), anchor="ma")
    c.text((22, 204), "next: 60 complication  //  75 raid", 15, (200, 170, 150))
    img = L.paste(img, c.finish(), 1010, 806)
    img = U.term_button(img, (1436, 806, 1896, 880), "GRID VIEW", "[M]  the city, this link lit")
    img = U.term_button(img, (1436, 894, 1660, 964), "DECK", "[D]")
    img = U.term_button(img, (1672, 894, 1896, 964), "MENU", "[ESC]")
    img = U.term_button(img, (1436, 978, 1896, 1056), "ABANDON RUN", "[X]  operative lost", accent=(255, 80, 80))
    if ui < 1.0:
        img = Image.blend(base.convert("RGB"), img.convert("RGB"), ui).convert("RGBA")
    return img


WALKED = ["start", "1_2", "2_1", "3_1"]


def main_png():
    A = load_anchors()
    bg = Image.open(os.path.join(U.FIN, "street.png"))
    img = compose(bg, A, WALKED, "3_1")
    img = L.bloom(img, 0.16, 0.8, 8)
    L.save(img, "route_c.png")


# ------------------------------------------------------------------ GIF: pick on the city map -> swoop down the link -> one step
def city_zoom_frames(n, size=(960, 540)):
    """The city map (round 30 v6) zooming toward Meridian, the link pencilled from the Cell to the Site."""
    src = Image.open(os.path.join(L.CONCEPTS, "round30_meridian_castle", "city_night_hq_v6.jpg")).convert("RGB")
    sw, sh = src.size
    cell = (0.49 * sw, 0.80 * sh)
    mer = (0.725 * sw, 0.36 * sh)
    mid = ((cell[0] + mer[0]) / 2, (cell[1] + mer[1]) / 2)
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        z = 1.0 + 2.4 * (t ** 1.5)
        cw, ch = sw / z, sh / z
        foc = (mid[0] + (mer[0] - mid[0]) * t, mid[1] + (mer[1] - mid[1]) * t)
        cx = sw / 2 + (foc[0] - sw / 2) * min(1, t * 1.5)
        cy = sh / 2 + (foc[1] - sh / 2) * min(1, t * 1.5)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        fr = src.crop(tuple(int(v) for v in box)).resize((1920, 1080), Image.LANCZOS).convert("RGBA")

        def to_s(p):
            return ((p[0] - box[0]) / cw * 1920, (p[1] - box[1]) / ch * 1080)
        a, b = to_s(cell), to_s(mer)
        inl = U.Inlay()
        pts = [a, (a[0] + (b[0] - a[0]) * 0.35, a[1] + (b[1] - a[1]) * 0.55), (a[0] + (b[0] - a[0]) * 0.7, a[1] + (b[1] - a[1]) * 0.7), b]
        inl.trace(pts, U.MER, width=3, lanes=3, gap=5, glow=1.0)
        fr = inl.lay(fr)
        p = L.pen(L.GP_YELLOW, seed=93)
        p.circle(b[0], b[1], 90 + 30 * t, 64 + 22 * t, width=10)
        fr = L.ink(fr, p)
        if i == 0:
            fr = L.place_sticker(fr, L.sticker_word(["JACK IN"], 64, fills=["pink"], seed=8), 1640, 960, angle=-3)
        out.append(fr.resize(size, Image.LANCZOS).convert("RGB"))
    return out


def main_gif():
    A = load_anchors(anim=True)
    size = (960, 540)
    frames, durs = [], []
    zoom = [z.filter(ImageFilter.GaussianBlur(0.7)) for z in city_zoom_frames(4)]
    frames += zoom
    durs += [800] + [140] * 3
    flight = [Image.open(os.path.join(U.FIN, "street_f%02d.png" % f)).convert("RGB") for f in (0, 3, 6, 8, 9)]
    # crossfade the map into the first render frame
    for i, f in enumerate(flight):
        frames.append(f.filter(ImageFilter.GaussianBlur(0.6)) if i < len(flight) - 1 else f)
        durs.append(170)
    bg = flight[-1].resize((1920, 1080), Image.LANCZOS)
    # the route builds in: traces + pads + stickers, then pencil, then the panels
    base = compose(bg, A, WALKED, "3_1", pencil=False, ui=0.0).convert("RGB")
    for k in (0.6,):
        frames.append(Image.blend(bg.convert("RGB"), base, k).resize(size, Image.LANCZOS))
        durs.append(110)
    frames.append(compose(bg, A, WALKED, "3_1", ui=0.5).convert("RGB").resize(size, Image.LANCZOS))
    durs.append(110)
    hold = compose(bg, A, WALKED, "3_1").convert("RGB").resize(size, Image.LANCZOS)
    frames.append(hold)
    durs.append(1500)
    # one step: pick 2 (the optional Server Rack); the token rides the link, the link turns lime behind it
    for t in (0.15, 0.35, 0.55, 0.75, 0.92):
        frames.append(compose(bg, A, WALKED, "3_1", move=("4_2", t), pencil=True, show_opts=False).convert("RGB").resize(size, Image.LANCZOS))
        durs.append(110)
    W2 = WALKED + ["4_2"]
    frames.append(compose(bg, A, W2, "4_2", show_opts=False).convert("RGB").resize(size, Image.LANCZOS))
    durs.append(500)
    frames.append(compose(bg, A, W2, "4_2").convert("RGB").resize(size, Image.LANCZOS))
    durs.append(1800)
    out = os.path.join(L.OUT, "route_c.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(720, 405)))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "png"
    if which in ("png", "all"):
        main_png()
    if which in ("gif", "all"):
        main_gif()
