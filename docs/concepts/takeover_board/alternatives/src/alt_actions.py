"""Wireframes: 'Actions without cards' options, in the direction A (Icebreaker Rig) layout.

Run: python alt_actions.py   (imports helpers from alt_wireframes.py)
"""
import math
import os
from PIL import Image, ImageDraw
from alt_wireframes import (OUT, W, H, BG, RUN, PINK, INK, TEAL, GUN, SYS, SYSF, HARM, TXT, DIM,
                            NOTE, ORANGE, F, M, MB, HAND, PLAN, box, ctext, note, header, wheel,
                            trace_arrows, polar, health_strip, ram_bank, tag)

CX, CY, R, RIN = 960, 556, 380, 170
TYPE_COL = {"CONTROL": (170, 140, 255), "VIRUS": (120, 220, 90), "FIRE": (255, 120, 60),
            "BLOCK": (94, 155, 224), "DELAY": (230, 200, 70)}


def base(d, title_code, title, pitch, hover=11, trace=True):
    """Direction A skeleton: top strip, wheel, corp column; the left column is left to the option."""
    box(d, (0, 14, W, 74), fill=SYSF, outline=SYS)
    d.text((24, 44), "STATIC ALLEY  T1 FIGHT  |  FIREWALL WHEEL", font=M[20], fill=SYS, anchor="lm")
    d.text((W - 24, 44), "TURN 3   ESC from 13   OWNED 3/12 -> 2", font=M[20], fill=SYS, anchor="rm")
    wheel(d, CX, CY, R, RIN, hover=hover)
    if trace:
        trace_arrows(d, CX, CY, R, RIN)
    box(d, (1360, 90, 1904, 1036), fill=(26, 30, 36), outline=TEAL, w=3)
    d.text((1376, 100), "SOLACE DAEMON (as direction A)", font=F[20], fill=TEAL)
    for k, (t, s, l) in enumerate(PLAN):
        y = 140 + k * 96
        box(d, (1376, y, 1888, y + 84), fill=tuple(int(c * [1, .75, .55][k]) for c in (150, 160, 170)),
            outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((1392, y + 10), f"{t}  {s}", font=F[28], fill=INK)
        d.text((1392, y + 50), l, font=M[18], fill=INK)
    d.text((1376, 440), "ARMED ON END TURN / CORP STATUS / ESCALATION", font=F[16], fill=DIM)
    box(d, (1376, 880, 1888, 1020), fill=PINK, outline=INK, w=4)
    ctext(d, (1632, 930), "EXECUTE", F[56], INK)
    ctext(d, (1632, 988), "END TURN [SPACE]   owned 3 -> 2, HP 27 -> 26", F[18], INK)
    header(d, title_code, title, pitch)


def rig_top(d):
    box(d, (16, 90, 560, 1036), fill=(24, 22, 26), outline=PINK, w=3)
    health_strip(d, (32, 104, 544, 182))
    d.text((32, 198), "RAM", font=F[20], fill=SYS)
    ram_bank(d, 90, 194, 3, 3)
    box(d, (260, 196, 380, 226), outline=SYS, label="SHROUD 1", lf=F[16], lc=SYS, r=12)
    box(d, (390, 196, 490, 226), outline=ORANGE, label="TRACED", lf=F[16], lc=ORANGE, r=12)


def piles(d, y, extra=""):
    d.text((32, y), "STACK 7   SPENT 3   PURGED 0" + extra, font=M[22], fill=TXT)
    box(d, (32, y + 40, 250, y + 100), fill=RUN, outline=INK, label="[Z] ROLLBACK", lf=F[20], lc=INK)


def type_pill(d, x, y, word, ok=True):
    tw = d.textlength(word, font=F[16]) + 14
    d.rectangle((x, y, x + tw, y + 22), fill=TYPE_COL[word] if ok else (90, 90, 90))
    d.text((x + 7, y + 11), word, font=F[16], fill=INK, anchor="lm")
    return tw


# ---------------- 1. COMMAND LINE (exploit commands) ----------------
def opt1():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "A1", "COMMAND LINE", "actions are typed-looking commands; the target is an argument")
    rig_top(d)
    d.text((32, 250), "rhee@cell:~$  available commands", font=M[20], fill=SYS)
    box(d, (24, 280, 552, 850), fill=(8, 18, 22), outline=SYS, w=2)
    rows = [("1", "nudge", "--spin +1|-1", 0, "CONTROL", True),
            ("2", "worm", "--hosts 3", 1, "VIRUS", True),
            ("3", "breach", "<host>", 1, "FIRE", True),
            ("4", "guard", "<yours>", 1, "BLOCK", True),
            ("5", "time_bomb", "<host>", 4, "DELAY", False)]
    for k, (key, cmd, arg, cost, word, ok) in enumerate(rows):
        y = 296 + k * 104
        if k == 2:
            d.rectangle((30, y - 6, 546, y + 92), fill=(40, 20, 34), outline=PINK, width=3)
        d.text((40, y), f"[{key}]", font=M[22], fill=DIM)
        d.text((96, y - 4), cmd, font=MB[32], fill=PINK if ok else HARM)
        d.text((96 + d.textlength(cmd, font=MB[32]) + 12, y + 4), arg, font=M[22], fill=DIM)
        d.text((536, y), f"{cost} RAM", font=MB[24], fill=SYS if ok else HARM, anchor="ra")
        tw = type_pill(d, 96, y + 42, word, ok)
        d.text((96 + tw + 10, y + 53), HAND[k][3] if ok else "", font=F[18], fill=TXT, anchor="lm")
        if not ok:
            d.text((96 + tw + 10, y + 53), "! needs 4 RAM, you have 3", font=F[18], fill=HARM, anchor="lm")
    piles(d, 870)
    # the typed line under the wheel, target filled by clicking a wedge
    box(d, (590, 980, 1330, 1036), fill=SYSF, outline=SYS)
    d.text((606, 1008), "$ breach FIREWALL#2    -> 5 becomes 2   [Enter] run  [Esc] cancel",
           font=M[20], fill=SYS, anchor="lm")
    # aim line from prompt to wedge 2
    tx, ty = polar(CX, CY, (R + RIN) / 2, -90 + 60)
    d.line([(1000, 980), (tx, ty + 40)], fill=PINK, width=4)
    note(d, (600, 92), "click a wedge = fill the <host> argument; keys 1-5 pick the command", f=F[16])
    return im


# ---------------- 2. RADIAL TOOL RING (target first) ----------------
def opt2():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "A2", "TOOL RING", "pick the target first; a radial ring of tools opens on it", hover=2, trace=False)
    rig_top(d)
    d.text((32, 250), "TOOL BELT (loaded tools, icon + key)", font=F[18], fill=DIM)
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        x = 32 + k * 104
        d.ellipse((x, 280, x + 92, 372), fill=RUN if ok else (120, 110, 104),
                  outline=HARM if not ok else TYPE_COL[word], width=6)
        ctext(d, (x + 46, 318), name[:2], F[32], INK)
        ctext(d, (x + 46, 390), f"{k + 1}", M[20], DIM)
        d.rectangle((x + 60, 276, x + 92, 304), fill=INK)
        ctext(d, (x + 76, 290), str(cost), F[20], SYS if ok else HARM)
    note(d, (32, 420), "belt = the hand: order, cost, key at a glance", f=F[16])
    box(d, (32, 460, 544, 560), fill=(30, 28, 34), outline=DIM)
    d.text((44, 470), "no-target tools (NUDGE, WORM) sit on the hub ring", font=F[18], fill=TXT)
    d.text((44, 500), "hover a tool = full line + type word here", font=F[18], fill=TXT)
    piles(d, 870)
    # radial menu on wedge 2 (corp FIREWALL)
    a = -90 + 60
    mx, my = polar(CX, CY, R + 10, a)
    d.ellipse((mx - 30, my - 30, mx + 30, my + 30), outline=SYS, width=4)
    opts = [("BREACH", 1, "FIRE", True, "3 dmg"), ("TIME BOMB", 4, "DELAY", False, "needs 4 RAM"),
            ("GUARD", 1, "BLOCK", False, "only on yours")]
    for k, (n, c, w_, ok, why) in enumerate(opts):
        ang = a + 130 + k * 50
        px, py = polar(mx, my, 150, ang)
        d.line([(mx, my), (px, py)], fill=SYS if ok else HARM, width=3)
        d.rounded_rectangle((px - 90, py - 44, px + 90, py + 44), 22, fill=RUN if ok else (60, 20, 20),
                            outline=TYPE_COL[w_] if ok else HARM, width=4)
        ctext(d, (px, py - 20), f"{n}  {c}", F[20], INK if ok else TXT)
        ctext(d, (px, py + 4), w_, F[16], INK if ok else TXT)
        ctext(d, (px, py + 26), why, F[16], INK if ok else HARM)
    # hub ring for no-target tools
    for k, n in enumerate(["NUDGE 0", "WORM 1"]):
        px, py = polar(CX, CY, RIN - 24, 200 + k * 40)
        d.rounded_rectangle((px - 60, py - 18, px + 60, py + 18), 18, fill=RUN, outline=PINK, width=3)
        ctext(d, (px, py), n, F[18], INK)
    note(d, (1180, 92), "click / Tab a segment: its legal tools fan out; red = why not", f=F[16], anchor="ma")
    return im


# ---------------- 3. DAEMONS (agents dispatched onto segments) ----------------
def daemon(d, x, y, word, ok=True, s=1.0, label=None):
    r = 34 * s
    col = TYPE_COL[word] if ok else (100, 90, 90)
    d.regular_polygon((x, y, r), 6, fill=RUN if ok else (120, 110, 104), outline=col)
    d.regular_polygon((x, y, r - 6), 6, outline=col)
    if label:
        ctext(d, (x, y), label, F[20] if s >= 1 else F[16], INK)


def opt3():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "A3", "DAEMONS", "you dispatch small agents onto segments; lingering ones stay visible", trace=False)
    rig_top(d)
    d.text((32, 250), "DAEMON BAY (loaded)", font=F[18], fill=DIM)
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        y = 284 + k * 108
        box(d, (24, y, 552, y + 96), fill=(36, 32, 38) if ok else (50, 20, 20),
            outline=HARM if not ok else (PINK if k == 2 else (70, 66, 74)), w=4 if (k == 2 or not ok) else 2)
        daemon(d, 76, y + 48, word, ok, label=name[:2])
        d.text((128, y + 10), name, font=F[28], fill=TXT if ok else HARM)
        d.text((536, y + 12), f"{cost} RAM", font=F[24], fill=SYS if ok else HARM, anchor="ra")
        tw = type_pill(d, 128, y + 52, word, ok)
        d.text((128 + tw + 10, y + 63), line if ok else "needs 4 RAM, you have 3", font=F[18],
               fill=TXT if ok else HARM, anchor="lm")
        d.text((44, y + 74), f"[{k + 1}]", font=M[16], fill=DIM)
    piles(d, 846, "  (used -> SPENT)")
    # dispatched BREACH en route to wedge 2
    sx, sy = 560, 500
    tx, ty = polar(CX, CY, R - 40, -90 + 60)
    d.line([(sx, sy), (tx, ty)], fill=PINK, width=4)
    daemon(d, (sx + tx) / 2, (sy + ty) / 2, "FIRE", label="BR")
    tag(d, ((sx + tx) / 2 + 80, (sy + ty) / 2 - 40), "aim: 5 -> 2", SYS, fill=SYSF, tc=SYS)
    # lingering daemons parked on the wheel
    gx, gy = polar(CX, CY, R - 34, -90 - 30)      # GUARD parked on your ICE
    daemon(d, gx, gy, "BLOCK", s=0.8, label="G3")
    bx, by = polar(CX, CY, R - 34, -90 + 120)     # TIME BOMB from an earlier turn on TURRET
    daemon(d, bx, by, "DELAY", s=0.8, label="2")
    vx, vy = polar(CX, CY, R - 34, -90 + 180)
    daemon(d, vx, vy, "VIRUS", s=0.8, label="V1")
    note(d, (1000, 92), "parked daemons = BLOCK, DELAY charge, VIRUS: the board shows what persists",
         f=F[16], anchor="ma")
    note(d, (bx + 40, by + 30), "TIME BOMB: 2 turns", f=F[16])
    note(d, (gx + 30, gy - 60), "GUARD: block 3", f=F[16])
    return im


# ---------------- 4. PATCH BAY (sockets and cables) ----------------
def opt4():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    base(d, "A4", "PATCH BAY", "actions are jacks on the deck; you patch a cable into a segment's port", trace=False)
    rig_top(d)
    d.text((32, 250), "JACKS (loaded)", font=F[18], fill=DIM)
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        y = 290 + k * 106
        d.ellipse((470, y, 540, y + 70), fill=(20, 20, 24), outline=TYPE_COL[word] if ok else HARM, width=8)
        d.ellipse((494, y + 24, 516, y + 46), fill=SYS if ok else HARM)
        d.text((40, y + 2), f"[{k + 1}] {name}", font=F[28], fill=TXT if ok else HARM)
        d.text((440, y + 6), f"{cost}", font=F[32], fill=SYS if ok else HARM, anchor="ra")
        tw = type_pill(d, 40, y + 44, word, ok)
        d.text((40 + tw + 10, y + 55), line if ok else "needs 4 RAM", font=F[18], fill=TXT if ok else HARM,
               anchor="lm")
    piles(d, 846)
    # ports on every segment rim; legal ones lit
    for i in range(12):
        px, py = polar(CX, CY, R + 30, -90 + i * 30)
        legal = i in (2, 10)   # corp segments next to yours, for BREACH
        d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=(20, 20, 24), outline=SYS if legal else GUN,
                  width=4)
    # cable from BREACH jack to port of wedge 2 (bezier-ish polyline)
    sx, sy = 540, 290 + 2 * 106 + 35
    tx, ty = polar(CX, CY, R + 30, -90 + 60)
    pts = []
    for t in [k / 20 for k in range(21)]:
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * 900 + t * t * tx
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * 1000 + t * t * ty
        pts.append((x, y))
    d.line(pts, fill=TYPE_COL["FIRE"], width=10)
    # a persistent DELAY cable from an earlier turn, with timer
    tx2, ty2 = polar(CX, CY, R + 30, -90 + 120)
    d.line([(tx2, ty2), (tx2 + 80, ty2 + 60)], fill=TYPE_COL["DELAY"], width=10)
    tag(d, (tx2 + 130, ty2 + 80), "TIME BOMB 2", TYPE_COL["DELAY"], fill=(40, 34, 10))
    note(d, (980, 92), "lit ports = legal targets; no-target jacks patch into the hub", f=F[16], anchor="ma")
    return im


def sheet(paths):
    tw, th = 960, 540
    sh = Image.new("RGB", (2 * tw + 48, 2 * th + 108), (8, 8, 10))
    d = ImageDraw.Draw(sh)
    d.text((16, 30), "Takeover: actions without cards (wireframes, direction A layout, 2026-11-14)", font=F[28],
           fill=NOTE, anchor="lm")
    for k, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        sh.paste(im, (16 + (k % 2) * (tw + 16), 76 + (k // 2) * (th + 16)))
    return sh


if __name__ == "__main__":
    paths = []
    for code, fn in [("1_command_line", opt1), ("2_tool_ring", opt2), ("3_daemons", opt3), ("4_patch_bay", opt4)]:
        p = os.path.join(OUT, f"alt_act_{code}.png")
        fn().save(p)
        paths.append(p)
        print("wrote", p)
    sp = os.path.join(OUT, "alt_actions_sheet.jpg")
    sheet(paths).save(sp, quality=90)
    print("wrote", sp)
