"""Round 22 raid UI: only the redone gifs (round 21 is locked otherwise) + the evaluation frame + the TAKEN key.

python screens22.py [gifs] [eval] [key] [contact]       (default: all)
Builds on screens21 (helpers, deco, base, path rules, gif writer); outputs in the round 22 folder.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screens21 as S  # noqa: E402
from screens21 import (LY, N, P, U, V, V2, Frame, base, deco, gif, seg, ease, INDEX, GIF_FRAMES, GIFS, OUT, SL)  # noqa: E402
import ui22 as K  # noqa: E402


def tray(fr, skip=(), copies=None):
    return K.hand(fr, skip, copies)


def sticker(fr, name, x, y, ang=0.0, hover=0.15, scale=0.85, copies=None, gloss=0.22):
    return V.place_sticker(fr, K.card(name, copies, gloss), x, y, ang, hover=hover, scale=scale)


def single_bold(pen, s, x, y, cap, col, w=9.0, progress=1.0, angle=-0.04, tracking=0.38):
    """BREACHED: heavy single-pass wax (no doubled letters)."""
    pen.strokes(V2.T.letter_strokes(s, x, y, cap, w, col, pen.rng, angle=angle, tracking=tracking), progress)


def build():
    os.makedirs(GIFS, exist_ok=True)
    INDEX.clear()
    vx, vy = P(*N["vault"][:2])
    fx, fy = P(*N["firewall"][:2])
    rx, ry = P(*N["relay"][:2])
    cx, cy = P(*N["core"][:2])
    px, py = P(*N["proxy"][:2])

    # 01 pick up: the card peels out of its slot and parks JUST ABOVE that slot (no outline)
    b = (640, 340, 1760, 970)
    pk = K.park_pos("ICE LOCK")

    def g01(t, i):
        on = t > 0.45 and int(i / 3) % 2 == 0
        fr = base("setup_h1", deco(flash={k: "hover" for k in ("relay", "firewall", "safe", "vault")} if on else {}), b, "g01%d" % on)
        fr = tray(fr, skip=("ICE LOCK",))
        e = ease(seg(t, 0.0, 0.45))
        fr = sticker(fr, "ICE LOCK", pk[0], K.SLOT_Y + (pk[1] - K.SLOT_Y) * e, K.SLOT_ANG["ICE LOCK"] * (1 - e),
                     hover=0.15 + 0.6 * math.sin(math.pi * e), scale=1.0 - 0.15 * e, gloss=1.0 if 0.3 < t < 0.7 else 0.22)
        if t > 0.45:
            c = (pk[0] + 60 + 140 * seg(t, 0.45, 1.0), pk[1] - 110 - 50 * seg(t, 0.45, 1.0))
            pen = V2.Pencil(fr, 11)
            V2.target_arrow(pen, (pk[0] + 20, pk[1] - 85), c, "free")
            fr = pen.composite()
            fr = V2.cursor(fr, *c)
        return fr
    gif("01_pick_up.gif", 20, g01, size=(800, 450))
    INDEX.append(("01_pick_up.gif", "Pick up a defence", "the card peels out of its slot and parks just ABOVE that slot in the hand; valid sockets pulse; the pencil arrow starts from it", "STICKER + PENCIL + INLAY"))

    # 02 drag valid
    def g02(t, i):
        near = t > 0.55
        fr = base("setup_h1", deco(flash={"vault": "hover"} if near else {}, forecast={"vault": "holds" if near else "disabled", "proxy": "seized"}),
                  b, "g02%d" % near)
        fr = tray(fr, skip=("ICE LOCK",))
        fr = sticker(fr, "ICE LOCK", *pk)
        e = ease(seg(t, 0.0, 0.55))
        s0 = (pk[0] + 20, pk[1] - 85)
        c = (s0[0] + 30 + (vx + 20 - s0[0] - 30) * e, s0[1] - 20 + (vy + 30 - s0[1] + 20) * e)
        pen = V2.Pencil(fr, 12)
        V2.target_arrow(pen, s0, c, "valid" if near else "free", progress=seg(t, 0.55, 0.8) if near else 1.0, node_xy=(vx, vy))
        fr = pen.composite()
        if near:
            fr = V.put_panel(fr, U.terminal("IF PLACED", [("kv", "VAULT", "DISABLED > HOLDS", U.GREEN), ("kv", "HOME", "42 > 45", U.PINK)],
                                            w=260, accent=U.GREEN), b[2] - 290, b[1] + 20)
        return V2.cursor(fr, *c)
    gif("02_drag_valid.gif", 20, g02, size=(800, 450))
    INDEX.append(("02_drag_valid.gif", "Drag over a valid node", "from the card parked above its slot, the arrow follows the cursor and resolves into a yellow circle on the node", "PENCIL + INLAY + TERMINAL"))

    # 03 drag invalid (TURRET over the full FIREWALL RELAY)
    bf = (420, 330, 1540, 960)
    pt = K.park_pos("TURRET")

    def g03(t, i):
        near = 0.5 < t < 0.8
        fr = base("setup_h1", deco(flash={"firewall": "invalid"} if near else {}), bf, "g03%d" % near)
        back = ease(seg(t, 0.82, 1.0))
        fr = tray(fr, skip=("TURRET",))
        fr = sticker(fr, "TURRET", pt[0], pt[1] + (K.SLOT_Y - pt[1]) * back, K.SLOT_ANG["TURRET"] * back, scale=0.85 + 0.15 * back)
        s0 = (pt[0] + 20, pt[1] - 85)
        e = ease(seg(t, 0.0, 0.5))
        c = (s0[0] + 30 + (fx + 20 - s0[0] - 30) * e, s0[1] - 20 + (fy + 30 - s0[1] + 20) * e)
        if t < 0.8:
            pen = V2.Pencil(fr, 13)
            V2.target_arrow(pen, s0, c, "invalid" if near else "free", progress=seg(t, 0.5, 0.65) if near else 1.0, node_xy=(fx, fy))
            fr = pen.composite()
            fr = V2.cursor(fr, *c)
        if near:
            fr = V.put_panel(fr, U.terminal("NO SLOT", [("t", "FIREWALL RELAY: 2/2 ASSET SLOTS", U.HARM)], w=280, accent=U.HARM), bf[2] - 300, bf[1] + 20)
        return fr
    gif("03_drag_invalid.gif", 20, g03, size=(800, 450))
    INDEX.append(("03_drag_invalid.gif", "Invalid drop", "red pencil X at the full socket; on release the card drops back into its slot", "PENCIL + INLAY + STICKER"))

    # 05 remove to hand: the placed ICE LOCK peels off the FIREWALL node (its model goes), flies to the hidden parked
    # zone at the bottom just above its slot, then slots back into the hand (x1 -> x2)
    br = (420, 360, 1540, 990)
    sx_, sy_ = K.SLOT_X["ICE LOCK"], K.SLOT_Y

    def g05(t, i):
        gone = t > 0.15
        fr = base("setup_h1_noice" if gone else "setup_h1", deco(), br, "g05%d" % gone)
        merged = t > 0.85
        fr = tray(fr, skip=("ICE LOCK",) if not merged else (), copies={"ICE LOCK": 2} if merged else None)
        if not merged:
            fr = sticker(fr, "ICE LOCK", sx_, sy_, K.SLOT_ANG["ICE LOCK"], scale=1.0, copies=1)
        if t <= 0.15:
            fr = V2.cursor(fr, fx + 8, fy + 6)
            k = seg(t, 0.05, 0.15)
            fr = sticker(fr, "ICE LOCK", fx, fy - 20 * k, -8, hover=0.2 + 0.5 * k, scale=0.3)
        elif not merged:
            e = ease(seg(t, 0.15, 0.65))
            x = fx + (sx_ - fx) * e
            y = fy - 20 + (K.HIDDEN_Y - fy + 20) * e - 110 * math.sin(math.pi * e)
            if t > 0.65:
                y = K.HIDDEN_Y + (sy_ - K.HIDDEN_Y) * ease(seg(t, 0.65, 0.85))
            fr = sticker(fr, "ICE LOCK", x, y, -8 + 6 * e, hover=0.2 + 0.5 * math.sin(math.pi * e), scale=0.3 + 0.7 * e)
            fr = V2.cursor(fr, fx + 8, fy + 6)
        else:
            fr = V2.cursor(fr, fx + 8, fy + 6)
        return fr
    gif("05_remove_to_hand.gif", 22, g05, size=(800, 450))
    INDEX.append(("05_remove_to_hand.gif", "Remove a defence (back to hand)", "the placed sticker peels off the node (its model is removed), flies to the hidden parked zone at the bottom, slots back into the hand: ICE LOCK x1 > x2", "STICKER + 3D"))

    # 06 one-motion swap: the sticker flies from the node to its parking spot above its slot while the pencil arrow
    # draws from it to the cursor's CURRENT position (the cursor stays on the target node)
    bs = (380, 330, 1500, 960)
    pkI = K.park_pos("ICE LOCK")
    cur = (rx + 20, ry + 30)

    def g06(t, i):
        gone = t > 0.12
        arrived = t > 0.6
        fr = base("setup_h1_noice" if gone else "setup_h1", deco(flash={"relay": "hover"} if arrived else {}), bs, "g06%d%d" % (gone, arrived))
        fr = tray(fr, skip=())
        e = ease(seg(t, 0.12, 0.6))
        x = fx + (pkI[0] - fx) * e
        y = fy - 20 + (pkI[1] - fy + 20) * e - 90 * math.sin(math.pi * e)
        fr = sticker(fr, "ICE LOCK", x, y, -8 * (1 - e) + 2 * e, hover=0.2 + 0.5 * math.sin(math.pi * e), scale=0.3 + 0.55 * e, copies=0)
        if gone:
            s0 = (x + 20 * (0.3 + 0.55 * e), y - 85 * (0.3 + 0.55 * e))
            pen = V2.Pencil(fr, 16)
            V2.target_arrow(pen, s0, cur, "valid" if arrived else "free", progress=seg(t, 0.6, 0.8) if arrived else 1.0, node_xy=(rx, ry))
            fr = pen.composite()
        return V2.cursor(fr, *cur)
    gif("06_swap_one_motion.gif", 24, g06, size=(800, 450))
    INDEX.append(("06_swap_one_motion.gif", "Move / swap in one motion", "remove + play: the sticker leaves the node for its parking spot above its slot while the pencil arrow draws from it to where the cursor already is; on the relay it resolves into a yellow circle", "STICKER + PENCIL + INLAY"))

    # 10 frozen link: ice crystals grow along the inside border, light-blue translucent fill
    bz = S.boxc((fx + cx) / 2, (fy + cy) / 2)

    def g10(t, i):
        amt = seg(t, 0.05, 0.55)
        fr = base("setup_h1", deco(link_states={("core", "firewall"): "frozen"} if amt > 0 else {}), bz, "g10%d" % (amt > 0))
        if amt > 0:
            fr = K.ice(fr, V2.link_mask(fr, "firewall", "core", amt, half=7.0), grow=min(1.0, seg(t, 0.1, 0.8) * 1.1), seed=5, density=11.0, scale=1.5)
        return V.put_panel(fr, U.terminal("LOCKDOWN UNIT", [("t", "FREEZES CORE - FIREWALL FOR THIS RAID", U.ICE)], w=330, accent=U.ICE), bz[0] + 10, bz[1] + 10)
    gif("10_link_frozen.gif", 18, g10)
    INDEX.append(("10_link_frozen.gif", "Link frozen (setup)", "blue/white ice crystals grow inward along the link's border over a light-blue translucent fill; nothing routes or shoots across it", "INLAY + ICE + TERMINAL"))

    # 15 threat held: the unit encased in an ice block (same crystals)
    pth = [tuple(N["proxy"][:2]), tuple(N["firewall"][:2]), tuple(N["core"][:2])]
    bh = S.boxc(fx - 40, fy + 60)

    def g15(t, i):
        if t < 0.3:
            u, held = 0.42 * seg(t, 0, 0.3), 0
        elif t < 0.8:
            u, held = 0.42, (2 if t < 0.55 else 1)
        else:
            u, held = 0.42 + 0.3 * seg(t, 0.8, 1.0), 0
        (x, y), hd = V.path_point(pth, u)
        fr = base("setup_h1", deco(rings=[(x, y, 0.6, "held" if held else "live")], forecast={}), bh, None)
        fr = V.paste_sprite(fr, "INSPECTOR", hd, x, y)
        if held:
            X, Y = P(x, y, 3)
            g = seg(t, 0.3, 0.45)
            fr = K.ice(fr, V2.ellipse_mask(fr, X, Y, 50, 35), grow=g, seed=7, fill=0.45, density=9.0, scale=1.5)
            fr = V.float_num(fr, X, Y - 70, "HELD %d" % held, col=(200, 240, 255), size=22)
        return fr
    gif("15_threat_held_ice.gif", 22, g15)
    INDEX.append(("15_threat_held_ice.gif", "Threat held (ICE LOCK)", "the unit is encased: crystals grow in from the block's border over a light-blue translucent fill; HELD 2 > 1; it thaws and moves on", "3D + ICE + INLAY + FLOAT"))

    # 20 node seized (pencil TAKEN, wipes)  /  21 node taken (after the raid)
    bp = S.boxc(px + 100, py + 10)

    def g20(t, i):
        seized = t > 0.25
        fr = base("setup_h1", deco(st={"proxy": "seized" if seized else "disabled"}, forecast={}), bp, "g20%d" % seized)
        pen = V2.Pencil(fr, 40)
        pen.text("TAKEN", px, py - 60, 22, V.R_PEN, 4.8, progress=seg(t, 0.3, 0.5))
        return pen.composite(wipe=seg(t, 0.8, 1.0))
    gif("20_node_seized.gif", 20, g20)
    INDEX.append(("20_node_seized.gif", "Node seized", "a disabled node hit again: corp hatch + corp glyph, links die; pencil TAKEN writes then wipes", "INLAY + PENCIL"))

    def g21(t, i):
        return base("setup_h1", deco(st={"proxy": "burnt" if t > 0.4 else "seized"}, forecast={}), bp, "g21%d" % (t > 0.4))
    gif("21_node_taken.gif", 10, g21, dur=160)
    INDEX.append(("21_node_taken.gif", "Node TAKEN (after the raid)", "renamed from LOST: the seized node is removed - a burnt socket with embers until reclaimed + reinstalled", "INLAY"))

    # 26 home breached: heavy single-pass BREACHED + underline
    bb = S.boxc(cx, cy - 20)

    def g26(t, i):
        hp = max(0.0, 0.4 - t)
        st = {"core": "burnt"} if hp <= 0 else {}
        fr = base("setup_h1", deco(st=st, health={"core": hp}, forecast={}), bb, "g26%d" % int(hp * 20))
        if 0.4 <= t < 0.75:
            fr = V2.bit_burst(fr, cx, cy - 10, seg(t, 0.4, 0.75), seed=26, col=(255, 60, 50), n=180, radius=190)
            fl = 0.35 * (1 - seg(t, 0.4, 0.55))
            fr.img = fr.img * (1 - fl) + np.array([0.9, 0.08, 0.06], np.float32) * fl
        pen = V2.Pencil(fr, 46)
        single_bold(pen, "BREACHED", cx + 10, cy - 100, 46, V.R_PEN, 9.5, progress=seg(t, 0.45, 0.85))
        pen.line([(cx - 205, cy - 60), (cx + 270, cy - 72)], V.R_PEN, 7.5, progress=seg(t, 0.82, 0.95))
        fr = pen.composite()
        if hp <= 0:
            fr = V.put_panel(fr, U.terminal("RAID RESULT", [("t", "HOME 0  //  CAMPAIGN LOST", U.HARM)], w=280, accent=U.HARM), bb[2] - 300, bb[3] - 70)
        return fr
    gif("26_home_breached.gif", 20, g26)
    INDEX.append(("26_home_breached.gif", "Home breached / lost", "heavy single-pass BREACHED with its underline (no doubled letters), red bit-explosion, CAMPAIGN LOST", "INLAY + FLOAT + PENCIL + TERMINAL"))
    write_index()


def write_index():
    lines = ["# Round 22 interaction gifs (redone only; everything else is locked in round 21)", "",
             "| gif | interaction | feedback | medium |", "|---|---|---|---|"]
    for f, t, d, m in INDEX:
        lines.append("| [%s](%s) | %s | %s | %s |" % (f, f, t, d, m))
    lines += ["", "Unchanged and locked: [round 21 gifs](../../round21_raid_ui/interactions_gifs/index.md) "
              "(04, 07, 08, 09, 11, 12, 13, 14, 16, 17, 18, 19, 22, 23, 24, 25, 27).",
              "Replaced: 05 remove defence -> `05_remove_to_hand`, 06 move/swap -> `06_swap_one_motion`, 21 node lost -> `21_node_taken`.", ""]
    open(os.path.join(GIFS, "index.md"), "w", encoding="utf-8").write("\n".join(lines))
    tw, th = 300, 169
    cols = 4
    rows = (len(INDEX) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 26) + 60), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((12, 14), "ROUND 22  REDONE GIFS (index.md)", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    for k, (n, *_r) in enumerate(INDEX):
        fr = GIF_FRAMES[n][len(GIF_FRAMES[n]) * 2 // 3].convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (k % cols) * (tw + 10), 54 + (k // cols) * (th + 26)
        sheet.paste(fr, (x, y))
        d.text((x + 2, y + th + 4), n, font=U.F(SL.MONO, 12), fill=(92, 225, 255))
    sheet.save(os.path.join(GIFS, "index.jpg"), quality=88)
    print("saved index")


def eval_frame():
    """One labelled evaluation frame with the faint parking outline (the gifs have none)."""
    b = (640, 340, 1760, 970)
    pk = K.park_pos("ICE LOCK")
    fr = base("setup_h1", deco(), b, "eval")
    fr = tray(fr, skip=("ICE LOCK",))
    fr = K.parking_outline(fr, *pk)
    fr = sticker(fr, "ICE LOCK", *pk)
    pen = V2.Pencil(fr, 11)
    V2.target_arrow(pen, (pk[0] + 20, pk[1] - 85), (pk[0] + 200, pk[1] - 160), "free")
    fr = pen.composite()
    fr = V2.cursor(fr, pk[0] + 200, pk[1] - 160)
    img = Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 520, 34], fill=(10, 9, 16))
    d.text((12, 17), "EVALUATION FRAME: parked = just above its slot", font=U.F(SL.MONO, 16), fill=(255, 210, 120), anchor="lm")
    img.save(os.path.join(OUT, "parked_eval.png"))
    print("saved parked_eval.png")


def contact():
    names = [n for n, *_ in INDEX] or sorted(f for f in os.listdir(GIFS) if f.endswith(".gif"))
    tw, th = 460, 259
    items = ["parked_eval.png", "node_status_key.png"] + ["interactions_gifs/" + n for n in names]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 24) + 64), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 14), "ROUND 22  RAID UI: PARKED ABOVE THE SLOT, REMOVE / SWAP, TAKEN, BREACHED, ICE CRYSTALS", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    for k, n in enumerate(items):
        im = Image.open(os.path.join(OUT, n))
        if getattr(im, "n_frames", 1) > 1:
            im.seek(im.n_frames * 2 // 3)
        im = im.convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        x, y = 10 + (k % cols) * (tw + 10), 56 + (k // cols) * (th + 24)
        sheet.paste(im, (x, y))
        d.text((x + 2, y + th + 3), n, font=U.F(SL.MONO, 12), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["gifs", "eval", "contact"]
    if "gifs" in which:
        build()
    if "eval" in which:
        eval_frame()
    if "contact" in which:
        contact()
