"""Round 32 -> route_b.png + route_b.gif: B, BUILDING CLIMB. Meridian HQ's container keep in cutaway (Blender,
r32_scene.py tower): 7 tiers of open shipping containers = 7 layers, each container a room = a node; the crane cab on
top is the final Server Rack (The Manifest). Links are inlay traces that run up through the ceilings and along the
floor slabs; walked rooms take the Cell's lime, cut-off rooms go dark.

python route_b.py [png|gif]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import r32ui as U
import sticker_lib19 as SL

B_EDGES = [  # (from room, to room) per gap; gap 0 = the street door (start) to floor 1
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 1), (2, 1), (2, 2), (3, 3)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (3, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (1, 0)],
]
WALKED = ["start", "1_1", "2_1", "3_1"]


def load(anim=False):
    if anim:
        A = json.load(open(os.path.join(U.BL, "tower_anim_anchors.json")))[-1]
    else:
        A = json.load(open(os.path.join(U.BL, "tower_anchors.json")))
    R = A["rooms"]
    kinds = {}
    for t, layer in enumerate(A["layers"]):
        for i, k in enumerate(layer):
            kinds["%d_%d" % (t + 1, i)] = k
    # the street door under floor 1: where the Cell's link comes in
    x0 = R["1_0"]["floor"]
    x1 = R["1_3"]["floor"]
    door = ((x0[0] + x1[0]) / 2, x0[1] + 26)
    edges = []
    for g, gl in enumerate(B_EDGES):
        outs, ins = {}, {}
        for (a, b) in gl:
            outs.setdefault(a, []).append(b)
            ins.setdefault(b, []).append(a)
        rows = []
        for (a, b) in gl:
            ka = "start" if g == 0 else "%d_%d" % (g, a)
            kb = "%d_%d" % (g + 1, b)
            B = R[kb]
            ob = sorted(ins[b])
            j = ob.index(a)
            xb = B["c"][0] + (j - (len(ob) - 1) / 2) * 34
            if g == 0:
                xa, ya = door[0], door[1]
                seam = R[kb]["floor"][1] + 14
            else:
                Aa = R[ka]
                oa = sorted(outs[a])
                i = oa.index(b)
                xa = Aa["c"][0] + (i - (len(oa) - 1) / 2) * 34
                ya = Aa["c"][1] - 30
                seam = (Aa["ceil"][1] + B["floor"][1]) / 2
            rows.append([ka, kb, xa, ya, xb, B["c"][1] + 34, seam])
        # tracks on the seam: overlapping horizontal runs get their own track
        used = []
        for r in rows:
            lo, hi = min(r[2], r[4]), max(r[2], r[4])
            tr = 0
            while any(u[0] == tr and not (hi < u[1] - 4 or lo > u[2] + 4) for u in used) and abs(r[2] - r[4]) > 2:
                tr += 1
            used.append((tr, lo, hi))
            off = [0, -6, 6, -12][tr]
            ka, kb, xa, ya, xb, yb, seam = r
            sy = seam + off
            if abs(xa - xb) < 2:
                pts = [(xa, ya), (xb, yb)] if g > 0 else [(xa, ya), (xa, sy), (xb, yb)]
            else:
                s = 6 if xb > xa else -6
                pts = [(xa, ya), (xa, sy + 6), (xa + s, sy), (xb - s, sy), (xb, sy - 6), (xb, yb)]
            if g == 0:
                pts = [(xa, ya), (xa + (xb - xa) * 0.15, ya), (xb, ya - 10), (xb, yb)] if abs(xb - xa) > 2 else [(xa, ya), (xb, yb)]
            edges.append(dict(a=ka, b=kb, pts=pts))
    return A, R, kinds, door, edges


def reach_from(edges, cur):
    g = {}
    for e in edges:
        g.setdefault(e["a"], []).append(e["b"])
    seen, todo = set(), [cur]
    while todo:
        n = todo.pop()
        for b in g.get(n, []):
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


def compose(bg, data, walked, current, move=None, show_opts=True, ui=1.0, pencil=True):
    A, R, kinds, door, edges = data
    img = bg.convert("RGBA")
    img = L.darken_rect(img, (-200, -200, 410, 1300), a=150, blur=50)
    img = L.darken_rect(img, (1510, -200, 2200, 1300), a=150, blur=50)
    reach = reach_from(edges, current)
    walked_e = set(zip(walked[:-1], walked[1:]))
    opts = [e for e in edges if e["a"] == current]
    arrived = move and move[1] >= 0.99
    cur_k = move[0] if arrived else current
    if arrived:
        reach = reach_from(edges, cur_k)
        walked = walked + [cur_k]
        walked_e = set(zip(walked[:-1], walked[1:]))
    state = {}
    for k in R:
        if k == cur_k:
            st = "current"
        elif k in walked:
            st = "walked"
        elif k in [e["b"] for e in edges if e["a"] == cur_k]:
            st = "option"
        elif k in reach:
            st = "reach"
        else:
            st = "cut"
        state[k] = st
    # ---------------- room light: walked rooms take the Cell's colours, cut-off rooms go dark
    for k, r in R.items():
        q = [tuple(p) for p in r["rect"]]
        st = state[k]
        if st == "cut":
            img = U.poly_wash(img, q, None, 0.9, mode="grey")
            img = U.poly_wash(img, q, None, 0.35, mode="dark")
        elif st in ("walked", "current"):
            img = U.poly_wash(img, q, U.LIME, 0.16 if st == "walked" else 0.24, glow=0.5)
        elif st == "option":
            img = U.poly_wash(img, q, (255, 190, 110), 0.10, glow=0.4)
    # ---------------- traces
    inl = U.Inlay()
    sx, sy = door
    inl.trace([(-20, sy + 8), (sx - 60, sy + 8), (sx - 52, sy), (sx, sy)], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    for e in edges:
        key = (e["a"], e["b"])
        if key in walked_e or (move and e["a"] == current and e["b"] == move[0]):
            continue
        if e["a"] == cur_k:
            inl.trace(e["pts"], U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        elif (e["a"] in reach or e["a"] == cur_k) and e["b"] in reach:
            inl.trace(e["pts"], U.MER, width=1.8, lanes=2, gap=4.0, glow=0.35, alpha=0.65)
        else:
            inl.trace(e["pts"], U.GREY, width=1.6, lanes=2, gap=4.0, glow=0.0, alpha=0.4)
    for e in edges:
        if (e["a"], e["b"]) in walked_e:
            inl.trace(e["pts"], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    tok = R[cur_k]["c"]
    if move and not arrived:
        e = next(e for e in edges if e["a"] == current and e["b"] == move[0])
        t = move[1]
        if t > 0.01:
            inl.trace(U.cut_poly(e["pts"], 0, t), U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
        inl.trace(U.cut_poly(e["pts"], t, 1), U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        tok = U.point_at(e["pts"], t)
    img = inl.lay(img)
    # ---------------- room outlines + stickers
    d = ImageDraw.Draw(img)
    for k, r in R.items():
        st = state[k]
        q = [tuple(p) for p in r["rect"]]
        if st in ("walked", "current"):
            d.line(q + [q[0]], fill=U.LIME + (200 if st == "walked" else 255,), width=2 if st == "walked" else 3)
        elif st == "option":
            d.line(q + [q[0]], fill=U.MER + (255,), width=3)
    for k, r in sorted(R.items(), key=lambda kv: -kv[1]["c"][1]):
        st = state[k]
        cx, cy = r["c"]
        if k == "7_0":
            px = 92
        else:
            px = {"walked": 48, "current": 58, "option": 64, "reach": 56, "cut": 50}[st]
        ang = ((sum(map(ord, k)) % 9) - 4) * 0.8
        img = L.place_sticker(img, U.node_sd(kinds[k], px, grey=(st == "cut")), cx, cy - 4, angle=ang,
                              opacity=0.8 if st == "cut" else 1.0, hover=0.35 if st == "option" else 0.0)
    # floor indicator: terminal chips stepping up the keep's left edge (the current floor lit)
    cur_t = int(cur_k.split("_")[0])
    for t in range(1, 8):
        r = R["%d_0" % t]
        xl, yl = r["rect"][0][0], (r["rect"][0][1] + r["rect"][3][1]) / 2
        img = U.chip(img, (xl - (12 if t < 7 else 70), yl), "L%d" % t if t < 7 else "L7 RACK", U.LIME if t <= cur_t else (U.MER if t == 7 else U.CYAN),
                     15, anchor="rm", bright=(t == cur_t))
    # ---------------- pencil
    if pencil:
        p = L.pen(L.GP_YELLOW, seed=95)
        if not move or arrived:
            cx, cy = R[cur_k]["c"]
            p.circle(cx, cy, 78, 46, width=9)
            if show_opts:
                o2 = sorted([e for e in edges if e["a"] == cur_k], key=lambda e: R[e["b"]]["c"][0])
                for n, e in enumerate(o2):
                    U.dashed_along(p, e["pts"], offset=-12 if n == 0 else 12, t0=0.25, t1=0.92)
                    bx, by = R[e["b"]]["c"]
                    p.text(str(n + 1), bx + (58 if n else -58), by - 22, 42, angle=-6)
        img = L.ink(img, p)
        pr = L.pen(L.GP_RED, seed=96)
        fx, fy = R["7_0"]["c"]
        pr.circle(fx, fy - 2, 150, 60, width=10)
        pr.text("THE MANIFEST", fx + 300, fy - 60, 34, angle=-5)
        img = L.ink(img, pr)
    tx, ty = tok
    img = L.place_sticker(img, U.token_sd(54), tx + 46, ty - 44, angle=-14, hover=0.6)
    if ui > 0:
        nxt = sorted([e["b"] for e in edges if e["a"] == cur_k], key=lambda k: R[k]["c"][0])
        ahead = [kinds[k] for k in reach if k != "7_0"]
        img = hud(img, cur_t, ui, [(k, kinds[k]) for k in nxt], ahead)
    return img


def hud(img, cur_t, ui=1.0, nxt=(), ahead=()):
    base = img.copy()
    img = L.place_sticker(img, L.sticker_word(["NETRUN"], 66, fills=["yellow"], seed=63), 180, 66, angle=-3)
    c = L.CRT(360, 150, U.CYAN, "CLIMB", tag="HQ RUN", seed=71)
    c.text((18, 52), "MERIDIAN HQ: THE KEEP", 19, (230, 245, 250))
    c.text((18, 80), "T4  //  FLOOR %d OF 7" % cur_t, 19, U.CYAN)
    c.text((18, 110), "lime = the Cell's   grey = cut off", 14, (150, 190, 200))
    img = L.paste(img, c.finish(), 24, 126)
    c = L.CRT(360, 236, U.PINK, "RUNNER", tag="CELL-9", seed=72)
    c.paste(L.glyph("slice_exploit", 38, fill=U.PINK, ow=3), 16, 54)
    c.text((72, 52), "CELL-9  BREAKER  R3", 18, (240, 240, 245))
    c.text((72, 78), "HP 51 / 60", 18, (255, 120, 150))
    c.bar(72, 104, 12, 10, w=18, h=12, gap=4, col=(255, 90, 130))
    c.text((18, 134), "DECK 21     CYCLES 64", 17, (200, 230, 240))
    c.rule(162, dash=True)
    c.text((18, 174), "UNBANKED: 1 asset", 16, (255, 200, 80))
    c.text((18, 198), "bank at the floor-4 Rack", 14, (160, 160, 150))
    img = L.paste(img, c.finish(), 24, 296)
    c = L.CRT(360, 300, L.YEL, "NEXT", tag="FLOOR %d" % (cur_t + 1), seed=73)
    y = 52
    for n, k, nm, sub, ht in [(str(i + 1), kd, U.KIND[kd]["name"], U.KIND[kd]["sub"].replace(" fight", ""), U.KIND[kd]["heat"]) for i, (_, kd) in enumerate(nxt)]:
        c.text((16, y), n, 40, L.YEL, fnt=L.f_num(42))
        c.paste(U.icon(k, 46), 48, y + 2)
        c.text((106, y + 2), nm, 21, (255, 255, 255), fnt=L.f_num(24))
        c.text((106, y + 32), sub, 14, (200, 190, 140))
        c.text((344, y + 6), "HEAT " + ht, 15, L.HEAT if ht != "+0" else (150, 220, 150), anchor="ra")
        y += 76
    c.rule(y, dash=True)
    at = U.ahead_text(ahead)
    cut = at.rfind(",", 0, 30) if len(at) > 30 else -1
    c.text((16, y + 10), "up the keep: " + (at[:cut + 1] if cut > 0 else at), 14, (170, 170, 150))
    c.text((16, y + 30), at[cut + 2:] if cut > 0 else "", 14, (170, 170, 150))
    c.text((16, y + 54), "top: THE MANIFEST in the crane cab", 14, U.MER)
    img = L.paste(img, c.finish(), 24, 548)
    img = U.term_button(img, (24, 868, 384, 940), "GRID VIEW", "[M]  the city")
    img = U.term_button(img, (24, 952, 198, 1022), "DECK", "[D]")
    img = U.term_button(img, (210, 952, 384, 1022), "MENU", "[ESC]")
    # right: decrypted HQ intel (holo) + Heat
    hb = (1534, 120, 1898, 420)
    img = U.holo(img, hb, U.MER, "MERIDIAN HQ", seed=6)
    img = U.meridian_seal(img, (1858, 158), 30)
    d = ImageDraw.Draw(img)
    rows = [("TIER", "T4  //  boss run"), ("BOSS", "THE MANIFEST"), ("HUB", "Priority Routing:"), ("", "+4 shield a turn"), ("", "unless breached"),
            ("EXPLOITS", "3 / 3  (breach ready)")]
    y = 200
    for a, b in rows:
        d.text((1552, y), a, font=L.f_mono(15), fill=(255, 200, 150, 255), anchor="lm")
        d.text((1648, y), b, font=L.f_ui(18, b"SemiBold"), fill=(255, 236, 214, 255), anchor="lm")
        y += 30
    img = U.chip(img, (1800, 398), "DECRYPTED // 7F-A2", U.LIME, 14)
    c = L.CRT(364, 210, L.HEAT, "HEAT", tag="CAMPAIGN", seed=74)
    c.text((20, 50), "71", 60, L.HEAT, fnt=L.f_num(74))
    c.text((112, 60), "FLAGGED", 21, (255, 170, 120))
    c.text((112, 88), "75 = raid, +25% strength", 14, (200, 170, 150))
    bx, by, bw = 20, 140, 324
    c.d.rectangle([bx, by, bx + bw, by + 14], fill=(40, 20, 16, 255))
    c.d.rectangle([bx, by, bx + int(bw * 0.71), by + 14], fill=L.HEAT + (255,))
    for v in (25, 50, 75):
        x = bx + bw * v / 100
        c.d.line([(x, by - 6), (x, by + 20)], fill=(255, 230, 200, 255), width=2)
        c.text((x, by + 24), str(v), 13, (220, 190, 170), anchor="ma")
    img = L.paste(img, c.finish(), 1534, 440)
    img = U.term_button(img, (1534, 980, 1898, 1052), "ABANDON RUN", "[X]  operative lost", accent=(255, 80, 80))
    if ui < 1.0:
        img = Image.blend(base.convert("RGB"), img.convert("RGB"), ui).convert("RGBA")
    return img


def main_png():
    data = load()
    bg = Image.open(os.path.join(U.FIN, "tower.png"))
    img = compose(bg, data, WALKED, "3_1")
    img = L.bloom(img, 0.16, 0.8, 8)
    L.save(img, "route_b.png")


def main_gif():
    import route_c
    data = load(anim=True)
    frames, durs = [], []
    zoom = [z.filter(ImageFilter.GaussianBlur(0.7)) for z in route_c.city_zoom_frames(4)]
    frames += zoom
    durs += [800] + [140] * 3
    for i, f in enumerate((0, 3, 6, 8, 9)):
        im = Image.open(os.path.join(U.FIN, "tower_walls_f%02d.png" % f)).convert("RGB")
        frames.append(im.filter(ImageFilter.GaussianBlur(0.6)) if f < 9 else im)
        durs.append(170 if f < 9 else 500)
    walls = Image.open(os.path.join(U.FIN, "tower_walls_f09.png")).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
    cut = Image.open(os.path.join(U.FIN, "tower_f09.png")).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
    # the cutaway reveal: the Cell's scan line sweeps up the keep and peels the front walls off
    R = data[1]
    ytop, ybot = R["7_0"]["rect"][3][1] - 20, R["1_0"]["rect"][0][1] + 10
    for t in (0.3, 0.65, 1.0):
        yl = ybot + (ytop - ybot) * t
        m = Image.new("L", (1920, 1080), 0)
        ImageDraw.Draw(m).rectangle([0, yl, 1920, 1080], fill=255)
        fr = Image.composite(cut, walls, m)
        g = Image.new("L", (1920, 1080), 0)
        ImageDraw.Draw(g).rectangle([380, yl - 3, 1540, yl + 3], fill=255)
        fr = SL.over(fr, U.CYAN, SL.scale_mask(g.filter(ImageFilter.GaussianBlur(10)), 0.9))
        fr = SL.over(fr, (220, 250, 255), g)
        frames.append(fr.convert("RGB"))
        durs.append(150)
    bg = cut
    frames.append(compose(bg, data, WALKED, "3_1", ui=0.6, pencil=False).convert("RGB"))
    durs.append(130)
    frames.append(compose(bg, data, WALKED, "3_1").convert("RGB"))
    durs.append(1500)
    for t in (0.2, 0.45, 0.7, 0.92):
        frames.append(compose(bg, data, WALKED, "3_1", move=("4_1", t), show_opts=False).convert("RGB"))
        durs.append(110)
    frames.append(compose(bg, data, WALKED, "3_1", move=("4_1", 1.0), show_opts=False).convert("RGB"))
    durs.append(500)
    frames.append(compose(bg, data, WALKED, "3_1", move=("4_1", 1.0)).convert("RGB"))
    durs.append(1800)
    out = os.path.join(L.OUT, "route_b.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(720, 405)))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "png"
    if which in ("png", "all"):
        main_png()
    if which in ("gif", "all"):
        main_gif()
