"""Round 34 -> route_d_transit.png + .gif: hybrid D, the Site run as a TRANSIT PATH, starting from the Cell's own node.

The link RELAY 4 (a lime raid node the Cell owns) > DEPOT 15, unrolled into the city corridor (r32_scene.py street).
Node states (round 34 rules):
  walked      lime pads + traces (the Cell's now)
  options     the FINITE next step only (2-3 nodes): bright corp colour, numbered on terminal chips
  plannable   every node still reachable later: visible but greyed (grey pads, greyscale stickers); the pencil plans through them
  behind      nodes the run can no longer reach: ghosted (faint pads, no stickers)
The plan is yellow grease pencil: solid to the next pick, dashed what-ifs onward to the Site's Rack.

python route_d_transit.py [png|gif|all]
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
import route_d_city as CITYV

KINDS = {}
PLANC = (176, 172, 196)
WALKED = ["start", "1_2", "2_1"]
PLAN = ["2_1", "3_1", "4_2", "5_2", "6_2", "final"]


def load(anim=False):
    A = json.load(open(os.path.join(U.BL, "street_anim_anchors.json")))[-1] if anim else json.load(open(os.path.join(U.BL, "street_anchors.json")))
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


def layer_of(k):
    return 0 if k == "start" else (7 if k == "final" else int(k.split("_")[0]))


def edge(A, a, b):
    return next(e for e in A["edges"] if e["a"] == a and e["b"] == b)


def compose(bg, A, walked, current, move=None, ui=1.0, plan=None):
    img = bg.convert("RGBA")
    img = L.darken_rect(img, (-200, -200, 2120, 330), a=110, blur=60)
    img = L.darken_rect(img, (-200, 790, 2120, 1300), a=150, blur=50)
    nodes = A["nodes"]
    arrived = bool(move and move[1] >= 0.99)
    if arrived:
        walked = walked + [move[0]]
        current = move[0]
        move = None
    reach = reach_from(A, current)
    opts = [e["b"] for e in A["edges"] if e["a"] == current]
    walked_e = set(zip(walked[:-1], walked[1:]))
    state = {}
    for k in nodes:
        if k == current:
            state[k] = "current"
        elif k in walked:
            state[k] = "walked"
        elif k in opts:
            state[k] = "option"
        elif k in reach:
            state[k] = "plan"
        else:
            state[k] = "behind"
    # ---------------- traces
    inl = U.Inlay()
    sx, sy = nodes["start"]["c"]
    inl.trace([(-20, sy), (sx, sy)], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    moving = (current, move[0]) if move else None
    for e in A["edges"]:
        key = (e["a"], e["b"])
        if key in walked_e or key == moving:
            continue
        if e["a"] == current:
            inl.trace(e["pts"], U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        elif e["a"] in reach and e["b"] in reach:
            inl.trace(e["pts"], PLANC, width=2.0, lanes=2, gap=4.0, glow=0.15, alpha=0.85)
        else:
            inl.trace(e["pts"], (90, 88, 104), width=1.4, lanes=1, gap=4.0, glow=0.0, alpha=0.3)
    for e in A["edges"]:
        if (e["a"], e["b"]) in walked_e:
            inl.trace(e["pts"], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    tok = nodes[current]["c"]
    if move:
        e = edge(A, current, move[0])
        if move[1] > 0.01:
            inl.trace(U.cut_poly(e["pts"], 0, move[1]), U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
        inl.trace(U.cut_poly(e["pts"], move[1], 1), U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        tok = U.point_at(e["pts"], move[1])
    img = inl.lay(img)
    # ---------------- pads
    order = sorted(nodes, key=lambda k: nodes[k]["c"][1])
    for k in order:
        st = state[k]
        q = [tuple(p) for p in nodes[k]["d"]]
        cx, cy = nodes[k]["c"]
        if k in ("final", "start"):
            q = [(cx + (x - cx) * 1.25, cy + (y - cy) * 1.25) for (x, y) in q]
        if k == "start":
            img = U.pad(img, q, U.LIME, lit=1.0, glow=1.0)
            ic = CITYV.cell_icon("relay", 30, U.LIME)
            img.alpha_composite(ic, (int(cx - 15), int(cy - 15)))
            continue
        col = {"walked": U.LIME, "current": U.LIME, "option": U.MER, "plan": PLANC, "behind": (90, 88, 104)}[st]
        lit = {"walked": 0.85, "current": 1.0, "option": 1.0, "plan": 0.7, "behind": 0.25}[st]
        img = U.pad(img, q, col, lit=lit, glow={"option": 0.9, "current": 0.9, "walked": 0.5}.get(st, 0.0),
                    fill_a=210 if st != "behind" else 120, pins=st != "behind")
    # ---------------- stickers: options full, plannable greyscale + dimmed, behind none
    for k in order:
        st = state[k]
        if k == "start" or st == "behind":
            continue
        cx, cy = nodes[k]["c"]
        px, lift = (112, 50) if k == "final" else ({"walked": 50, "current": 62, "option": 72, "plan": 58}[st], 26)
        ang = ((sum(map(ord, k)) % 9) - 4) * 0.8
        img = L.place_sticker(img, U.node_sd(KINDS[k], px, grey=(st == "plan")), cx, cy - lift, angle=ang,
                              opacity=0.82 if st == "plan" else 1.0, hover=0.35 if st == "option" else 0.0)
    # the finite set: numbered terminal chips on the options only
    if not move:
        for n, k in enumerate(sorted(opts, key=lambda k: nodes[k]["c"][1])):
            cx, cy = nodes[k]["c"]
            img = U.chip(img, (cx - 50, cy - 50), str(n + 1), U.MER, 18, bright=True)
    img = U.chip(img, (sx + 96, sy - 54), "RELAY 4  //  YOUR NODE", U.LIME, 14, bright=True)
    cur_l = layer_of(current)
    for l in range(1, 7):
        xs = [nodes[k]["c"][0] for k in nodes if k not in ("start", "final") and layer_of(k) == l]
        img = U.chip(img, (sum(xs) / len(xs), 382), "L%d" % l, U.LIME if l <= cur_l else (U.MER if l == cur_l + 1 else PLANC), 15,
                     bright=(l == cur_l))
    fx, fy = nodes["final"]["c"]
    img = U.chip(img, (fx, 382), "L7  SITE", U.MER, 15)
    # ---------------- pencil: the plan (solid to the next pick, dashed through the greyed nodes)
    plan = plan if plan is not None else PLAN
    p = L.pen(L.GP_YELLOW, seed=351)
    if not move:
        ccx, ccy = nodes[current]["c"]
        p.circle(ccx, ccy - 8, 56, 40, width=9)
        pl = plan[plan.index(current):] if current in plan else []
        for n, (a, b) in enumerate(zip(pl[:-1], pl[1:])):
            pts = U.offset_poly(edge(A, a, b)["pts"], -13)
            if n == 0:
                seg = U.cut_poly(pts, 0.2, 0.84)
                p.stroke(SL.catmull(p.wobble(seg, 0.8), 6), width=9)
                U.arrow_head(p, seg[-2:], width=8, head=18)
            else:
                U.dashed_along(p, edge(A, a, b)["pts"], offset=-13, t0=0.18, t1=0.84, width=7)
        p.text("PLAN", fx - 330, fy + 50, 30, angle=-6)
    img = L.ink(img, p)
    pr = L.pen(L.GP_RED, seed=352)
    pr.circle(fx, fy - 30, 96, 84, width=10)
    pr.text("PORT AUTHORITY", fx + 40, fy + 92, 30, angle=-4)
    img = L.ink(img, pr)
    tx, ty = tok
    img = L.place_sticker(img, U.token_sd(56), tx + 30, ty - 74, angle=-14, hover=0.6)
    if ui > 0:
        img = hud(img, cur_l, ui, sorted(opts, key=lambda k: nodes[k]["c"][1]), [KINDS[k] for k in reach if k != "final"], KINDS.get(current, "router"))
    return img


def hud(img, cur_l, ui, nxt, ahead, here):
    base = img.copy()
    img = L.place_sticker(img, L.sticker_word(["NETRUN"], 70, fills=["yellow"], seed=63), 196, 70, angle=-3)
    strip = L.CRT(1000, 72, U.CYAN, None, header=False, seed=353)
    strip.text((16, 10), "LINK  //  RELAY 4 (YOUR NODE)  >  DEPOT 15  //  T1  //  LAYER %d OF 7" % cur_l, 20, U.CYAN)
    strip.text((16, 42), "lime = walked    orange = reachable now (%d)    grey = plannable    pencil = plan" % len(nxt), 15, (150, 190, 200))
    img = L.paste(img, strip.finish(scan=0.15), 390, 34)
    hb = (1500, 112, 1898, 352)
    img = U.holo(img, hb, U.MER, "SITE 15  //  DEPOT 15", seed=354)
    img = U.meridian_seal(img, (1858, 150), 30)
    d = ImageDraw.Draw(img)
    rows = [("TIER", "T1  (opens CUSTOMS 22)"), ("GUARD", "PORT AUTHORITY"), ("ONWARD", "CUSTOMS 22 > LANE 15"), ("", "> MERIDIAN HQ (climb)")]
    y = 190
    for a, b in rows:
        d.text((1518, y), a, font=L.f_mono(15), fill=(255, 200, 150, 255), anchor="lm")
        d.text((1612, y), b, font=L.f_ui(18, b"SemiBold"), fill=(255, 236, 214, 255), anchor="lm")
        y += 30
    img = U.chip(img, (1800, 330), "DECRYPTED // 7F-A2", U.LIME, 14)
    c = L.CRT(420, 250, U.PINK, "RUNNER", tag="CELL-9", seed=355)
    c.paste(L.glyph("slice_exploit", 40, fill=U.PINK, ow=3), 18, 56)
    c.text((80, 54), "CELL-9  BREAKER  R1", 20, (240, 240, 245))
    c.text((80, 80), "HP 52 / 60", 18, (255, 120, 150))
    c.bar(80, 106, 12, 10, w=20, h=12, gap=4, col=(255, 90, 130))
    c.text((20, 136), "DECK 14      CYCLES 41", 18, (200, 230, 240))
    c.rule(166, dash=True)
    c.text((20, 178), "UNBANKED: 1 asset", 16, (255, 200, 80))
    c.text((20, 202), "banked at a Server Rack or on exit", 14, (160, 160, 150))
    img = L.paste(img, c.finish(), 24, 806)
    c = L.CRT(540, 250, L.YEL, "NEXT", tag="%d CHOICES FROM THE %s" % (len(nxt), U.KIND[here]["name"]), seed=356)
    y = 52
    for i, k in enumerate(nxt):
        kd = KINDS[k]
        c.text((20, y), str(i + 1), 40, L.YEL, fnt=L.f_num(44))
        c.paste(U.icon(kd, 50), 56, y + 2)
        c.text((120, y + 2), U.KIND[kd]["name"], 22, (255, 255, 255), fnt=L.f_num(26))
        c.text((120, y + 34), U.KIND[kd]["sub"], 15, (200, 190, 140))
        c.text((520, y + 8), "HEAT " + U.KIND[kd]["heat"], 17, L.HEAT if U.KIND[kd]["heat"] != "+0" else (150, 220, 150), anchor="ra")
        y += 70
    c.rule(y + 2, dash=True)
    c.text((20, y + 10), "ahead: " + U.ahead_text(ahead), 15, (170, 170, 150))
    c.text((20, y + 30), "end: SERVER RACK at the Site (guarded)", 15, U.MER)
    img = L.paste(img, c.finish(), 466, 806)
    c = L.CRT(400, 250, L.HEAT, "HEAT", tag="CAMPAIGN", seed=357)
    c.text((22, 50), "41", 60, L.HEAT, fnt=L.f_num(76))
    c.text((120, 62), "NOTICED", 22, (255, 190, 120))
    c.text((120, 92), "next: 50 = raid", 14, (200, 170, 150))
    bx, by, bw = 22, 146, 356
    c.d.rectangle([bx, by, bx + bw, by + 16], fill=(40, 20, 16, 255))
    c.d.rectangle([bx, by, bx + int(bw * 0.41), by + 16], fill=L.HEAT + (255,))
    for v in (25, 50, 75):
        x = bx + bw * v / 100
        c.d.line([(x, by - 6), (x, by + 22)], fill=(255, 230, 200, 255), width=2)
        c.text((x, by + 26), str(v), 13, (220, 190, 170), anchor="ma")
    c.text((22, 204), "this run: about +8 by the Rack", 15, (200, 170, 150))
    img = L.paste(img, c.finish(), 1010, 806)
    img = U.term_button(img, (1436, 806, 1896, 880), "GRID VIEW", "[M]  the city, the plan")
    img = U.term_button(img, (1436, 894, 1660, 964), "DECK", "[D]")
    img = U.term_button(img, (1672, 894, 1896, 964), "MENU", "[ESC]")
    img = U.term_button(img, (1436, 978, 1896, 1056), "ABANDON RUN", "[X]  operative lost", accent=(255, 80, 80))
    if ui < 1.0:
        img = Image.blend(base.convert("RGB"), img.convert("RGB"), ui).convert("RGBA")
    return img


def main_png():
    A = load()
    img = compose(Image.open(os.path.join(U.FIN, "street.png")), A, WALKED, "2_1")
    img = L.bloom(img, 0.16, 0.8, 8)
    L.save(img, "route_d_transit.png")


def city_zoom(n):
    """The round 34 city view (no HUD), zooming into the link RELAY 4 > DEPOT 15."""
    cv = CITYV.city_layer(CITYV.base_map()).convert("RGB")
    a, b = CITYV.pos("relay4"), CITYV.pos("depot15")
    foc = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        z = 1.0 + 2.6 * t ** 1.4
        w, h = 1920 / z, 1080 / z
        cx = 960 + (foc[0] - 960) * min(1, t * 1.4)
        cy = 540 + (foc[1] - 540) * min(1, t * 1.4)
        cx = min(max(cx, w / 2), 1920 - w / 2)
        cy = min(max(cy, h / 2), 1080 - h / 2)
        fr = cv.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((1920, 1080), Image.LANCZOS)
        if i == 0:
            fr = CITYV.hud(fr.convert("RGBA")).convert("RGB")
        out.append(fr)
    return out


def main_gif():
    A = load(anim=True)
    frames, durs = [], []
    z = city_zoom(4)
    frames += [f.filter(ImageFilter.GaussianBlur(0.6 if i else 0)) for i, f in enumerate(z)]
    durs += [1400, 140, 140, 140]
    for i, f in enumerate((0, 3, 6, 8, 9)):
        im = Image.open(os.path.join(U.FIN, "street_f%02d.png" % f)).convert("RGB")
        frames.append(im.filter(ImageFilter.GaussianBlur(0.6)) if f < 9 else im)
        durs.append(170)
    bg = Image.open(os.path.join(U.FIN, "street_f09.png")).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    frames.append(compose(bg, A, WALKED, "2_1", ui=0.5).convert("RGB"))
    durs.append(130)
    frames.append(compose(bg, A, WALKED, "2_1").convert("RGB"))
    durs.append(1800)
    for t in (0.2, 0.45, 0.7, 0.92):
        frames.append(compose(bg, A, WALKED, "2_1", move=("3_1", t)).convert("RGB"))
        durs.append(110)
    frames.append(compose(bg, A, WALKED, "2_1", move=("3_1", 1.0)).convert("RGB"))
    durs.append(2000)
    out = os.path.join(L.OUT, "route_d_transit.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(720, 405)))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "png"
    if which in ("png", "all"):
        main_png()
    if which in ("gif", "all"):
        main_gif()
