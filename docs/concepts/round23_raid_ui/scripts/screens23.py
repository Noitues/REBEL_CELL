"""Round 23 raid UI: dock preview while dragging across nodes, truthful swap cursor, TAKEN pencil mark, slow BREACHED.

python screens23.py      -> interactions_gifs/*.gif + index.md / index.jpg + contact_sheet.jpg
Builds on screens22 / screens21 (round 22 locked: remove-to-hand, frozen link + frozen unit ice).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screens22 as S22  # noqa: E402
from screens21 import (LY, N, P, U, V, V2, base, deco, gif, seg, ease, INDEX, GIF_FRAMES, GIFS, OUT, SL)  # noqa: E402
import screens21 as S21  # noqa: E402
import netdecal19 as N19  # noqa: E402
import ui22 as K  # noqa: E402

DOCK_R = 95          # cursor distance (px) at which the dock preview takes over
TIP_GAP = 92         # the parked arrow tip stops this far from the node centre (just outside the circle)


def lerp(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def polyline_at(pts, u):
    """Point at fraction u along a screen polyline."""
    d = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    L = sum(d) * min(1.0, max(0.0, u))
    for i, di in enumerate(d):
        if L <= di or i == len(d) - 1:
            return lerp(pts[i], pts[i + 1], min(1.0, L / max(di, 1e-6)))
        L -= di


def arrow_path(s0, tip):
    mx, my = (s0[0] + tip[0]) / 2 + (tip[1] - s0[1]) * 0.18, (s0[1] + tip[1]) / 2 - (tip[0] - s0[0]) * 0.18
    return V2.T.bezier(s0, (mx, my), tip, 40)


def dock_arrow(fr, s0, cur, nodes, entered, t, seed=12):
    """nodes: {key: valid}. If the cursor is within DOCK_R of a node: the arrow tip PARKS just outside that node's
    circle (no redraw) and the circle draws on (yellow = valid; red circle + red X = invalid). Else: tip = cursor.
    entered: {key: time the cursor entered} drives the circle's draw-on."""
    near = None
    for k, ok in nodes.items():
        nx, ny = P(*N[k][:2])
        if math.hypot(cur[0] - nx, cur[1] - ny) < DOCK_R:
            near = (k, ok, nx, ny)
    pen = V2.Pencil(fr, seed)
    if near is None:
        pen.arrow(arrow_path(s0, cur), V2.Y_PEN, 6.5, 18)
    else:
        k, ok, nx, ny = near
        dx, dy = nx - s0[0], ny - s0[1]
        L = math.hypot(dx, dy)
        tip = (nx - dx / L * TIP_GAP, ny - dy / L * TIP_GAP * 0.75)
        pen.arrow(arrow_path(s0, tip), V2.Y_PEN, 6.5, 18)
        prog = min(1.0, (t - entered.get(k, t)) / 0.12 + 0.25)
        if ok:
            pen.circle(nx, ny, 76, 50, V2.Y_PEN, 7.0, turns=1.2, progress=prog)
        else:
            pen.circle(nx, ny, 76, 50, V2.R_PEN, 7.0, turns=1.2, progress=prog)
            pen.x(nx, ny, 28, V2.R_PEN, 8.0, progress=max(0.0, prog * 1.6 - 0.6))
    return pen.composite(), near


class Dyn(N19.Net):
    pass


def link_dying(net, a, b, frac):
    """Draw link a-b lit only where it is still powered: dies segment by segment from `a` outward (frac 0..1 dead)."""
    m = (net.X == net.X)
    em0, dk0 = net.em.copy(), net.dk.copy()
    net.link(a, b, "ok")
    pa, pb = np.array(LY.pt(a), float), np.array(LY.pt(b), float)
    s, ac, L = N19.seg_coords(net.X, net.Y, pa, pb)
    seg_len = 10.0
    idx = np.floor((s - N19.PAD_S) / seg_len)
    nseg = max(1.0, (L - 2 * N19.PAD_S) / seg_len)
    dead_n = frac * nseg
    alive = (idx >= dead_n).astype(np.float32)
    flick = ((idx >= dead_n - 1) & (idx < dead_n)).astype(np.float32) * 0.6
    keep = np.clip(alive + flick, 0, 1)[..., None]
    net.em = em0 + (net.em - em0) * keep
    net.dk = dk0 * (1 - (1 - net.dk / np.maximum(dk0, 1e-6)) * 0.5)


def build():
    os.makedirs(GIFS, exist_ok=True)
    INDEX.clear()
    vx, vy = P(*N["vault"][:2])
    fx, fy = P(*N["firewall"][:2])
    rx, ry = P(*N["relay"][:2])
    cx, cy = P(*N["core"][:2])
    px, py = P(*N["proxy"][:2])

    # 02 drag across nodes: vault (valid) -> firewall (invalid: 2/2 slots) -> away
    b = (430, 300, 1500, 902)
    pk = K.park_pos("ICE LOCK")
    s0 = (pk[0] + 20, pk[1] - 85)
    path = [(s0[0] + 50, s0[1] - 40), (vx - 40, vy + 120), (vx + 8, vy + 6), (vx + 14, vy + 2), (vx + 4, vy + 10),
            (vx - 130, vy - 10), (fx + 150, fy + 10), (fx + 6, fy + 8), (fx - 4, fy + 2), (fx + 8, fy + 12), (fx - 60, fy + 190), (fx - 110, fy + 260)]
    n02 = 40
    ent = {}
    curs = []
    for i in range(n02):
        t = i / n02
        c = polyline_at(path, ease(t) * 0.25 + t * 0.75)
        curs.append(c)
        for k in ("vault", "firewall"):
            nx, ny = P(*N[k][:2])
            inside = math.hypot(c[0] - nx, c[1] - ny) < DOCK_R
            if inside and k not in ent:
                ent[k] = t
            if not inside and k in ent and t > ent[k] + 0.02:
                ent.pop(k)
        curs[-1] = (c, dict(ent))

    def g02(t, i):
        c, entered = curs[i]
        near_v = math.hypot(c[0] - vx, c[1] - vy) < DOCK_R
        near_f = math.hypot(c[0] - fx, c[1] - fy) < DOCK_R
        fl = {"vault": "hover"} if near_v else {"firewall": "invalid"} if near_f else {}
        fr = base("setup_h1", deco(flash=fl, forecast={"vault": "holds" if near_v else "disabled", "proxy": "seized"}), b, "g02%d%d" % (near_v, near_f))
        fr = S22.tray(fr, skip=("ICE LOCK",))
        fr = S22.sticker(fr, "ICE LOCK", *pk)
        fr, near = dock_arrow(fr, s0, c, {"vault": True, "firewall": False}, entered, t)
        if near_v:
            fr = V.put_panel(fr, U.terminal("IF PLACED", [("kv", "VAULT", "DISABLED > HOLDS", U.GREEN), ("kv", "HOME", "42 > 45", U.PINK)],
                                            w=260, accent=U.GREEN), b[2] - 290, b[1] + 20)
        if near_f:
            fr = V.put_panel(fr, U.terminal("NO SLOT", [("t", "FIREWALL RELAY: 2/2 ASSET SLOTS", U.HARM)], w=280, accent=U.HARM), b[2] - 300, b[1] + 20)
        return V2.cursor(fr, *c)
    gif("02_drag_dock_preview.gif", n02, g02, dur=100, size=(800, 450))
    INDEX.append(("02_drag_dock_preview.gif", "Drag across nodes (dock preview)", "near a node the arrow STOPS just outside it and the circle draws on: yellow at the Vault (valid), red circle + red X at the full Firewall (invalid); moving away erases the circle and the arrow snaps back to the cursor", "PENCIL + INLAY + TERMINAL"))

    # 06 swap: the cursor is ON the placed unit (Firewall); press: the sticker peels off and flies to its parking spot,
    # the arrow starts at the cursor there and follows the cursor to the Relay
    bs = (380, 300, 1450, 902)
    pkI = K.park_pos("ICE LOCK")
    cur_path = [(fx + 6, fy + 6), (fx - 30, fy + 120), (rx + 60, ry - 90), (rx + 8, ry + 6)]
    n06 = 32

    def g06(t, i):
        pressed = t > 0.1
        e = ease(seg(t, 0.12, 0.6))
        c = polyline_at(cur_path, ease(seg(t, 0.12, 0.75)))
        near = math.hypot(c[0] - rx, c[1] - ry) < DOCK_R
        fr = base("setup_h1_noice" if pressed else "setup_h1", deco(flash={"relay": "hover"} if near else {}), bs, "g06%d%d" % (pressed, near))
        fr = S22.tray(fr)
        sxy = lerp((fx, fy - 20), pkI, e)
        sy_arc = sxy[1] - 90 * math.sin(math.pi * e)
        if pressed:
            fr = S22.sticker(fr, "ICE LOCK", sxy[0], sy_arc, -8 * (1 - e) + 2 * e, hover=0.2 + 0.5 * math.sin(math.pi * e), scale=0.3 + 0.55 * e, copies=0)
            # the arrow's origin = the sticker (which starts under the cursor on the Firewall)
            sc = 0.3 + 0.55 * e
            origin = (sxy[0] + 20 * sc, sy_arc - 85 * sc)
            if math.hypot(c[0] - origin[0], c[1] - origin[1]) > 14:
                fr, _ = dock_arrow(fr, origin, c, {"relay": True}, {"relay": 0.72}, t, seed=16)
        return V2.cursor(fr, *c)
    gif("06_swap_one_motion.gif", n06, g06, dur=100, size=(800, 450))
    INDEX.append(("06_swap_one_motion.gif", "Move / swap in one motion", "the cursor presses ON the placed unit (Firewall): the sticker peels off and flies to its parking spot above its slot while the pencil arrow runs from it to the cursor, which travels to the Relay; there the arrow stops and the yellow circle draws", "STICKER + PENCIL + INLAY"))

    # 21 node TAKEN: seized at the end of the raid -> a brief TAKEN mark written over the node, then it wipes; the node is removed
    bp = S21.boxc(px + 100, py + 10)

    def g21(t, i):
        removed = t > 0.55
        fr = base("setup_h1", deco(st={"proxy": "burnt" if removed else "seized"}, forecast={}), bp, "g21%d" % removed)
        pen = V2.Pencil(fr, 21)
        pen.text("TAKEN", px + 6, py - 4, 30, V.R_PEN, 6.0, progress=seg(t, 0.12, 0.38))
        return pen.composite(wipe=seg(t, 0.62, 0.82))
    gif("21_node_taken.gif", 22, g21, dur=110)
    INDEX.append(("21_node_taken.gif", "Node TAKEN", "a brief grease-pencil TAKEN is written right over the node, holds a moment, then wipes away like DOWN; the node is removed (burnt socket)", "INLAY + PENCIL"))

    # 26 BREACHED, slowed: CORE drains, a slow bit explosion, the home node and its links die segment by segment,
    # BREACHED writes slowly (single heavy pass + underline)
    bb = S21.boxc(cx, cy - 20, 800, 450)
    core_links = [(a, bb_) for a, bb_ in LY.LINKS if "core" in (a, bb_)]
    n26 = 44

    def g26(t, i):
        hp = max(0.0, 0.45 - t * 1.6)
        dead = seg(t, 0.3, 0.8)
        burnt = t > 0.3

        def extra(net):
            for a, b_ in core_links:
                o = a if a == "core" else b_
                other = b_ if o == a else a
                link_dying(net, "core", other, dead)
        ls = {(a, b_): "dead" for a, b_ in core_links}
        fr = base("setup_h1", deco(st={"core": "burnt"} if burnt else {}, health={"core": hp}, forecast={}, link_states=ls, extra=extra), bb, None)
        if 0.28 <= t < 0.85:
            k = seg(t, 0.28, 0.85)
            fr = V2.bit_burst(fr, cx, cy - 10, k, seed=26, col=(255, 60, 50), n=180, radius=200)
            fl = 0.3 * (1 - seg(t, 0.28, 0.4))
            fr.img = fr.img * (1 - fl) + np.array([0.9, 0.08, 0.06], np.float32) * fl
        pen = V2.Pencil(fr, 46)
        S22.single_bold(pen, "BREACHED", cx + 10, cy - 100, 46, V.R_PEN, 9.5, progress=seg(t, 0.45, 0.9))
        pen.line([(cx - 205, cy - 40), (cx + 270, cy - 52)], V.R_PEN, 7.5, progress=seg(t, 0.9, 0.98))
        fr = pen.composite()
        if t > 0.8:
            fr = V.put_panel(fr, U.terminal("RAID RESULT", [("t", "HOME 0  //  CAMPAIGN LOST", U.HARM)], w=280, accent=U.HARM), bb[2] - 300, bb[3] - 70)
        return fr
    gif("26_home_breached.gif", n26, g26, dur=120, size=(800, 450))
    INDEX.append(("26_home_breached.gif", "Home breached / lost (slowed)", "CORE drains, then a slow bit explosion; CORE and its links de-power segment by segment from the node outward; BREACHED writes slowly (single heavy pass) and is underlined", "INLAY + FLOAT + PENCIL + TERMINAL"))
    write_index()


def write_index():
    lines = ["# Round 23 interaction gifs (redone only)", "", "| gif | interaction | feedback | medium |", "|---|---|---|---|"]
    for f, t, d, m in INDEX:
        lines.append("| [%s](%s) | %s | %s | %s |" % (f, f, t, d, m))
    lines += ["", "02 replaces round 22's 02 + 03 (valid and invalid now in one drag).",
              "Locked and unchanged: round 22 [01, 05 remove-to-hand, 10 frozen link, 15 frozen unit, 20](../../round22_raid_ui/interactions_gifs/index.md); "
              "everything else in [round 21](../../round21_raid_ui/interactions_gifs/index.md).", ""]
    open(os.path.join(GIFS, "index.md"), "w", encoding="utf-8").write("\n".join(lines))
    tw, th = 440, 248
    sheet = Image.new("RGB", (2 * (tw + 10) + 10, 2 * (th + 26) + 60), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((12, 14), "ROUND 23  REDONE GIFS (index.md)", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    for k, (n, *_r) in enumerate(INDEX):
        fr = GIF_FRAMES[n][len(GIF_FRAMES[n]) * 2 // 5].convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (k % 2) * (tw + 10), 54 + (k // 2) * (th + 26)
        sheet.paste(fr, (x, y))
        d.text((x + 2, y + th + 4), n, font=U.F(SL.MONO, 12), fill=(92, 225, 255))
    sheet.save(os.path.join(GIFS, "index.jpg"), quality=88)
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved index + contact")


if __name__ == "__main__":
    build()
