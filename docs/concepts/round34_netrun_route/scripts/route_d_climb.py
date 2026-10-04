"""Round 34 -> route_d_climb.png: hybrid D, the HQ boss run's ENTRY. The transit plan reached Meridian HQ; the Cell's
link arrives at the keep's street door (the breach point). Floor 1 offers a FINITE set (3 rooms; the fourth container is
sealed, not a node). Every floor above is PLANNABLE: visible, greyed, and the pencil plans a climb through it to the
crane cab, where THE MANIFEST waits (red).

python route_d_climb.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw

import r31lib as L
import r32ui as U
import sticker_lib19 as SL
import route_b as RB
import route_d_city as CITYV

RB.B_EDGES = [
    [(0, 1), (0, 2), (0, 3)],
    [(1, 0), (1, 1), (2, 1), (2, 2), (3, 3)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (3, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (1, 0)],
]
PLAN = ["start", "1_2", "2_2", "3_1", "4_1", "5_1", "6_1", "7_0"]
PLANC = (176, 172, 196)


def compose(bg, data):
    A, R, kinds, door, edges = data
    img = bg.convert("RGBA")
    img = L.darken_rect(img, (-200, -200, 410, 1300), a=150, blur=50)
    img = L.darken_rect(img, (1510, -200, 2200, 1300), a=150, blur=50)
    opts = [e["b"] for e in edges if e["a"] == "start"]
    rooms = [k for k in R if kinds[k] != "sealed"]
    # rooms: the 3 entries lit warm, every other floor greyed (plannable), the sealed container left as rendered
    for k in rooms:
        q = [tuple(p) for p in R[k]["rect"]]
        if k in opts:
            img = U.poly_wash(img, q, (255, 190, 110), 0.12, glow=0.4)
        else:
            img = U.poly_wash(img, q, None, 0.75, mode="grey")
    # traces: the Cell's link in from the street; entry links bright; the rest plannable grey
    inl = U.Inlay()
    sx, sy = door
    inl.trace([(-20, sy + 8), (sx - 60, sy + 8), (sx - 52, sy), (sx, sy)], U.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0)
    for e in edges:
        if e["a"] == "start":
            inl.trace(e["pts"], U.MER, width=2.4, lanes=3, gap=4.0, glow=0.9)
        else:
            inl.trace(e["pts"], PLANC, width=2.0, lanes=2, gap=4.0, glow=0.12, alpha=0.8)
    img = inl.lay(img)
    q = [(sx, sy - 16), (sx + 32, sy), (sx, sy + 16), (sx - 32, sy)]
    img = U.pad(img, q, U.LIME, lit=1.0, glow=1.0)
    ic = CITYV.cell_icon("relay", 22, U.LIME)
    img.alpha_composite(ic, (int(sx - 11), int(sy - 11)))
    d = ImageDraw.Draw(img)
    for k in opts:
        qq = [tuple(p) for p in R[k]["rect"]]
        d.line(qq + [qq[0]], fill=U.MER + (255,), width=3)
    for k in sorted(rooms, key=lambda k: -R[k]["c"][1]):
        cx, cy = R[k]["c"]
        px = 92 if k == "7_0" else (64 if k in opts else 54)
        ang = ((sum(map(ord, k)) % 9) - 4) * 0.8
        img = L.place_sticker(img, U.node_sd(kinds[k], px, grey=(k not in opts)), cx, cy - 4, angle=ang,
                              opacity=1.0 if k in opts else 0.85, hover=0.35 if k in opts else 0.0)
    for n, k in enumerate(sorted(opts, key=lambda k: R[k]["c"][0])):
        cx, cy = R[k]["c"]
        img = U.chip(img, (cx - 62, cy - 26), str(n + 1), U.MER, 18, bright=True)
    for t in range(1, 8):
        r = R["%d_0" % t]
        xl, yl = r["rect"][0][0], (r["rect"][0][1] + r["rect"][3][1]) / 2
        img = U.chip(img, (xl - (12 if t < 7 else 70), yl), "L%d" % t if t < 7 else "L7 RACK",
                     U.MER if t == 1 else PLANC, 15, anchor="rm")
    img = U.chip(img, (sx - 150, sy - 34), "BREACH POINT  //  FROM LANE 15", U.LIME, 14, bright=True)
    # pencil: ring the door, solid to the first planned room, dashed up the plan
    p = L.pen(L.GP_YELLOW, seed=361)
    p.circle(sx, sy, 56, 30, width=9)
    ed = {(e["a"], e["b"]): e for e in edges}
    for n, (a, b) in enumerate(zip(PLAN[:-1], PLAN[1:])):
        pts = ed[(a, b)]["pts"]
        if n == 0:
            seg = U.cut_poly(U.offset_poly(pts, 12), 0.15, 0.82)
            p.stroke(SL.catmull(p.wobble(seg, 0.8), 6), width=9)
            U.arrow_head(p, seg[-2:], width=8, head=18)
        else:
            U.dashed_along(p, pts, offset=0, t0=0.06, t1=0.94, width=8, dash=14, gap=8)
    p.text("PLAN: BANK AT", 1660, 700, 26, angle=-5)
    p.text("THE FLOOR-4 RACK", 1680, 744, 26, angle=-5)
    img = L.ink(img, p)
    pr = L.pen(L.GP_RED, seed=362)
    fx, fy = R["7_0"]["c"]
    pr.circle(fx, fy - 2, 150, 60, width=10)
    pr.text("THE MANIFEST", fx + 300, fy - 60, 34, angle=-5)
    img = L.ink(img, pr)
    img = L.place_sticker(img, U.token_sd(54), sx + 44, sy - 52, angle=-14, hover=0.6)
    return hud(img, [(k, kinds[k]) for k in sorted(opts, key=lambda k: R[k]["c"][0])],
               [kinds[k] for k in rooms if k != "7_0"])


def hud(img, nxt, ahead):
    img = L.place_sticker(img, L.sticker_word(["THE CLIMB"], 60, fills=["yellow"], seed=363), 196, 64, angle=-3)
    c = L.CRT(360, 150, U.CYAN, "CLIMB", tag="HQ RUN", seed=364)
    c.text((18, 52), "MERIDIAN HQ: THE KEEP", 19, (230, 245, 250))
    c.text((18, 80), "T4  //  ENTRY, FLOOR 0 OF 7", 19, U.CYAN)
    c.text((18, 110), "orange = reachable   grey = plannable", 14, (150, 190, 200))
    img = L.paste(img, c.finish(), 24, 126)
    c = L.CRT(360, 236, U.PINK, "RUNNER", tag="CELL-9", seed=365)
    c.paste(L.glyph("slice_exploit", 38, fill=U.PINK, ow=3), 16, 54)
    c.text((72, 52), "CELL-9  BREAKER  R3", 18, (240, 240, 245))
    c.text((72, 78), "HP 60 / 60", 18, (255, 120, 150))
    c.bar(72, 104, 12, 12, w=18, h=12, gap=4, col=(255, 90, 130))
    c.text((18, 134), "DECK 22     CYCLES 0", 17, (200, 230, 240))
    c.rule(162, dash=True)
    c.text((18, 174), "fresh run: HP full, deck kept", 15, (180, 220, 200))
    c.text((18, 198), "Exploits 3 / 3 carried in", 14, U.LIME)
    img = L.paste(img, c.finish(), 24, 296)
    c = L.CRT(360, 330, L.YEL, "NEXT", tag="%d DOORS" % len(nxt), seed=366)
    y = 52
    for i, (_, kd) in enumerate(nxt):
        c.text((16, y), str(i + 1), 40, L.YEL, fnt=L.f_num(42))
        c.paste(U.icon(kd, 46), 48, y + 2)
        c.text((106, y + 2), U.KIND[kd]["name"], 21, (255, 255, 255), fnt=L.f_num(24))
        c.text((106, y + 32), "floor 1, " + U.KIND[kd]["sub"].split(",")[0], 14, (200, 190, 140))
        c.text((344, y + 6), "HEAT " + U.KIND[kd]["heat"], 15, (150, 220, 150), anchor="ra")
        y += 64
    c.rule(y, dash=True)
    at = U.ahead_text(ahead)
    cut = at.rfind(",", 0, 30)
    c.text((16, y + 10), "the keep: " + at[:cut + 1], 14, (170, 170, 150))
    c.text((16, y + 30), at[cut + 2:], 14, (170, 170, 150))
    c.text((16, y + 54), "top: THE MANIFEST in the crane cab", 14, U.MER)
    img = L.paste(img, c.finish(), 24, 548)
    img = U.term_button(img, (24, 896, 384, 966), "GRID VIEW", "[M]  the city, the plan")
    img = U.term_button(img, (24, 978, 384, 1048), "MENU", "[ESC]")
    hb = (1534, 120, 1898, 420)
    img = U.holo(img, hb, U.MER, "MERIDIAN HQ", seed=367)
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
    c = L.CRT(364, 210, L.HEAT, "HEAT", tag="CAMPAIGN", seed=368)
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
    return img


def main():
    data = RB.load()
    img = compose(Image.open(os.path.join(U.FIN, "tower.png")), data)
    img = L.bloom(img, 0.16, 0.8, 8)
    L.save(img, "route_d_climb.png")


if __name__ == "__main__":
    main()
