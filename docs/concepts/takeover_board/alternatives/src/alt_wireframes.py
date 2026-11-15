"""Rough wireframe thumbnails for the Takeover screen alternatives.

Flat blocks + labels, 1920x1080, one per direction, plus a contact sheet.
Run: python alt_wireframes.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"D:/rc_art/art-pass/docs/concepts/takeover_board/alternatives"
W, H = 1920, 1080
FONTS = r"C:/Windows/Fonts/"

BG = (14, 17, 22)
RUN = (238, 228, 214)        # runner: bone paper (punk print)
PINK = (255, 70, 150)        # runner accent
INK = (20, 20, 24)
CORP = (54, 62, 72)          # corp: slate enamel
TEAL = (92, 196, 176)        # Solace edge
GUN = (120, 128, 136)        # gunmetal (pointers)
SYS = (80, 220, 240)         # system: cyan glass
SYSF = (16, 36, 44)
HARM = (232, 52, 52)
TXT = (222, 232, 236)
DIM = (130, 146, 156)
NOTE = (255, 208, 60)        # wireframe annotation colour
ORANGE = (255, 150, 40)


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


F = {s: font("bahnschrift.ttf", s) for s in (14, 16, 18, 20, 22, 24, 28, 32, 40, 48, 56, 72)}
M = {s: font("consola.ttf", s) for s in (14, 16, 18, 20, 22, 24, 28)}
MB = {s: font("consolab.ttf", s) for s in (16, 18, 20, 24, 28, 32)}

# ---- shared sample state (same numbers as the B-088 plates) ----
TYPES = ["NODE", "FIREWALL", "FIREWALL", "CACHE", "TURRET", "NODE",
         "RELAY", "SPAWNER", "ICE", "NODE", "CORE", "ICE"]
INTS = [6, 4, 5, 3, 6, 5, 5, 4, 5, 5, 7, 3]
MINE = {0, 1, 11}
OUTCOME = {11: ("LOST -1HP", HARM), 10: ("->9", SYS), 5: ("->4", SYS)}
ARMED = {3, 10}
POINTERS = [0, 4, 8]
HAND = [  # name, cost, type word, line, playable
    ("NUDGE", 0, "CONTROL", "spin 1 more or 1 less", True),
    ("WORM", 1, "VIRUS", "1 virus on 3 corp segs", True),
    ("BREACH", 1, "FIRE", "3 dmg next to yours", True),
    ("GUARD", 1, "BLOCK", "block 3 on yours", True),
    ("TIME BOMB", 4, "DELAY", "6 dmg in 2 turns", False),
]
PLAN = [("NOW", "STRIKE 2", "your weakest segment"),
        ("T+1", "WALL", "both sides of CORE"),
        ("T+2", "SURGE 3", "from CORE, both ways")]


def ctext(d, xy, s, f, fill=TXT, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def box(d, xy, fill=None, outline=None, w=2, label=None, lf=None, lc=TXT, r=0):
    if r:
        d.rounded_rectangle(xy, r, fill=fill, outline=outline, width=w)
    else:
        d.rectangle(xy, fill=fill, outline=outline, width=w)
    if label:
        x0, y0, x1, y1 = xy
        ctext(d, ((x0 + x1) / 2, (y0 + y1) / 2), label, lf or F[20], lc)


def note(d, xy, s, anchor="la", f=None):
    d.text(xy, s, font=f or F[18], fill=NOTE, anchor=anchor)


def header(d, code, name, pitch):
    d.rectangle((0, 0, W, 6), fill=NOTE)
    d.rectangle((0, H - 34, W, H), fill=(0, 0, 0))
    d.text((16, H - 17), f"{code}  {name}", font=F[20], fill=NOTE, anchor="lm")
    d.text((W - 16, H - 17), pitch, font=F[18], fill=DIM, anchor="rm")


def wedge_poly(cx, cy, r0, r1, a0, a1, n=14):
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a)))
    for k in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a)))
    return pts


def polar(cx, cy, r, a):
    a = math.radians(a)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def seg_label(d, x, y, i, scale=1.0, hot=True):
    mine = i in MINE
    col = INK if mine else TXT
    f_big = F[int(40 * scale)] if int(40 * scale) in F else F[40]
    ctext(d, (x, y - 4 * scale), str(INTS[i]), f_big, col)
    f_small = F[16] if scale < 1.1 else F[18]
    ctext(d, (x, y + 28 * scale), TYPES[i], f_small, (60, 60, 60) if mine else DIM)


def outcome_tag(d, x, y, i):
    if i not in OUTCOME:
        return
    s, c = OUTCOME[i]
    tw = d.textlength(s, font=F[18]) + 14
    d.rectangle((x - tw / 2, y - 13, x + tw / 2, y + 13), fill=c if c == HARM else SYSF,
                outline=c, width=2)
    ctext(d, (x, y), s, F[18], TXT if c == HARM else SYS)


def wheel(d, cx, cy, R, rin, hub_label=("CORP SPIN", "-2", "then +1 +1 -2"), ptr_style="tri",
          hover=11, rot=0):
    d.ellipse((cx - R - 16, cy - R - 16, cx + R + 16, cy + R + 16), fill=CORP, outline=TEAL, width=10)
    for i in range(12):
        a0 = -90 + i * 30 - 15 + rot
        a1 = a0 + 30
        mine = i in MINE
        d.polygon(wedge_poly(cx, cy, rin, R, a0 + 0.8, a1 - 0.8),
                  fill=RUN if mine else (40, 47, 56),
                  outline=PINK if mine else TEAL)
        if i in ARMED:
            d.arc((cx - R + 8, cy - R + 8, cx + R - 8, cy + R - 8), a0 + 4, a1 - 4, fill=HARM, width=8)
        lx, ly = polar(cx, cy, (R + rin) / 2 + 12, -90 + i * 30 + rot)
        seg_label(d, lx, ly, i, scale=R / 400)
        tx, ty = polar(cx, cy, rin + 2, -90 + i * 30 + rot)
        outcome_tag(d, tx, ty, i)
    if hover is not None:
        a0 = -90 + hover * 30 - 15 + rot
        d.line(wedge_poly(cx, cy, rin, R, a0 + 0.8, a0 + 29.2) + [polar(cx, cy, R, a0 + 0.8)],
               fill=SYS, width=4)
    d.ellipse((cx - rin + 30, cy - rin + 30, cx + rin - 30, cy + rin - 30), fill=(30, 36, 44),
              outline=TEAL, width=4)
    if hub_label:
        ctext(d, (cx, cy - rin * 0.32), hub_label[0], F[18], TXT)
        ctext(d, (cx, cy + 2), hub_label[1], F[56], ORANGE)
        ctext(d, (cx, cy + rin * 0.36), hub_label[2], F[16], DIM)
    for p in POINTERS:
        a = -90 + p * 30
        if ptr_style == "tri":
            tip = polar(cx, cy, R + 4, a)
            b1 = polar(cx, cy, R + 70, a - 5)
            b2 = polar(cx, cy, R + 70, a + 5)
            d.polygon([tip, b1, b2], fill=GUN, outline=(200, 200, 200))
    return cx, cy


def trace_arrows(d, cx, cy, R, rin):
    """Hover trace into wedge 11 (ICE), numbered by resolution order."""
    tgt = polar(cx, cy, (R + rin) / 2, -90 + 11 * 30 - 6)
    # 11.1 plan strike from hub
    d.line([polar(cx, cy, rin - 40, -110), tgt], fill=HARM, width=5)
    tag(d, polar(cx, cy, rin - 70, -150), "11.1  -2", HARM)
    # 11.2 GUARD block
    tag(d, polar(cx, cy, R + 50, -125), "11.2  BLOCK 2", PINK, fill=RUN, tc=INK)
    # 13.1 CORE counter
    src = polar(cx, cy, (R + rin) / 2, -90 + 10 * 30)
    d.line([src, tgt], fill=HARM, width=5)
    tag(d, polar(cx, cy, R - 10, -146), "13.1  -3", HARM)
    lx, ly = polar(cx, cy, rin + 2, -120)
    tag(d, (lx + 6, ly + 32), "16.1 -1 HP", SYS)


def tag(d, xy, s, c, fill=None, tc=None):
    x, y = xy
    tw = d.textlength(s, font=F[18]) + 14
    d.rectangle((x - tw / 2, y - 14, x + tw / 2, y + 14), fill=fill or (40, 10, 10), outline=c, width=2)
    ctext(d, (x, y), s, F[18], tc or TXT)


def program_chip(d, xy, card, style="chip", sel=False, key=None):
    name, cost, word, line, ok = card
    x0, y0, x1, y1 = xy
    edge = HARM if not ok else (PINK if sel else INK)
    d.rectangle(xy, fill=RUN if ok else (120, 110, 104), outline=edge, width=4 if (sel or not ok) else 2)
    # RAM pins on the left edge (energy cost as memory pins)
    pin_x = x0 + 12
    d.rectangle((x0, y0, x0 + 64, y1), fill=INK)
    ctext(d, (x0 + 32, y0 + 26), str(cost), F[32], SYS)
    ctext(d, (x0 + 32, y0 + 54), "RAM", F[14], SYS)
    if key:
        ctext(d, (x0 + 32, y1 - 16), f"[{key}]", M[14], DIM)
    d.text((x0 + 78, y0 + 10), name.lower().replace(" ", "_") + ".exe", font=MB[24], fill=INK)
    tw = d.textlength(word, font=F[16]) + 14
    d.rectangle((x0 + 78, y0 + 42, x0 + 78 + tw, y0 + 64), fill=PINK if ok else (90, 90, 90))
    d.text((x0 + 85, y0 + 53), word, font=F[16], fill=INK, anchor="lm")
    d.text((x0 + 78 + tw + 10, y0 + 53), line, font=F[18], fill=INK, anchor="lm")
    if not ok:
        d.rectangle((x1 - 210, y0 + 6, x1 - 6, y0 + 34), fill=HARM)
        ctext(d, (x1 - 108, y0 + 20), "NO RAM: needs 4", F[16], TXT)


def health_strip(d, xy, label="RHEE  NEURAL LINK"):
    x0, y0, x1, y1 = xy
    d.rectangle(xy, fill=RUN, outline=PINK, width=3)
    d.text((x0 + 14, y0 + 8), label, font=F[18], fill=INK)
    bx0, by0, bx1, by1 = x0 + 14, y0 + 36, x1 - 130, y1 - 10
    n = 28
    step = (bx1 - bx0) / n
    for k in range(n):
        c = (60, 200, 90) if k < 26 else ((200, 60, 60) if k == 26 else (80, 80, 80))
        d.rectangle((bx0 + k * step + 1, by0, bx0 + (k + 1) * step - 2, by1), fill=c)
    ctext(d, (x1 - 64, (y0 + y1) / 2), "27->26", F[28], HARM)


def ram_bank(d, x, y, n=3, cap=3, size=36):
    for k in range(cap):
        d.rectangle((x + k * (size + 8), y, x + k * (size + 8) + size, y + size + 14),
                    fill=SYS if k < n else SYSF, outline=SYS, width=2)


# ========================= A. ICEBREAKER RIG =========================
def dir_a():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # top system strip
    box(d, (0, 14, W, 74), fill=SYSF, outline=SYS)
    d.text((24, 44), "STATIC ALLEY  T1 FIGHT  |  FIREWALL WHEEL: next to a corp FIREWALL takes 1 less per hit",
           font=M[20], fill=SYS, anchor="lm")
    d.text((W - 24, 44), "TURN 3   ESCALATION from turn 13   OWNED 3/12 -> 2", font=M[20], fill=SYS, anchor="rm")
    # left: runner rig
    box(d, (16, 90, 560, 1036), fill=(24, 22, 26), outline=PINK, w=3)
    d.text((32, 100), "RUNNER RIG  (punk print on the deck)", font=F[20], fill=PINK)
    health_strip(d, (32, 132, 544, 210))
    d.text((32, 226), "RAM", font=F[20], fill=SYS)
    ram_bank(d, 90, 222, 3, 3)
    d.text((260, 226), "STATUS", font=F[18], fill=DIM)
    box(d, (340, 222, 450, 252), outline=SYS, label="SHROUD 1", lf=F[16], lc=SYS, r=12)
    box(d, (456, 222, 544, 252), outline=ORANGE, label="TRACED", lf=F[16], lc=ORANGE, r=12)
    d.text((32, 290), "LOADED PROGRAMS (hand)", font=F[18], fill=DIM)
    for k, c in enumerate(HAND):
        y = 316 + k * 112
        program_chip(d, (32, y, 544, y + 100), c, sel=(k == 2), key=str(k + 1))
    d.text((32, 884), "STACK 7   SPENT 3   PURGED 0", font=M[22], fill=TXT)
    note(d, (32, 920), "draw / discard / exhaust as the rig's file system", f=F[16])
    box(d, (32, 950, 270, 1020), fill=RUN, outline=INK, label="[Z] ROLLBACK", lf=F[22], lc=INK)
    # wheel
    cx, cy, R, rin = 960, 556, 380, 170
    wheel(d, cx, cy, R, rin)
    trace_arrows(d, cx, cy, R, rin)
    note(d, (1010, 118), "pointers = fixed trace heads (gunmetal)")
    # bottom command line under wheel
    box(d, (590, 980, 1330, 1036), fill=SYSF, outline=SYS)
    d.text((606, 1008), "> run breach.exe --target 02    (preview on the wedges)", font=M[20], fill=SYS, anchor="lm")
    # right: corp
    box(d, (1360, 90, 1904, 1036), fill=(26, 30, 36), outline=TEAL, w=3)
    d.text((1376, 100), "SOLACE DAEMON  (corp enamel)", font=F[20], fill=TEAL)
    d.text((1376, 140), "SCHEDULE (plan)", font=F[18], fill=DIM)
    for k, (t, s, l) in enumerate(PLAN):
        y = 168 + k * 104
        v = [1.0, 0.75, 0.55][k]
        fill = tuple(int(c * v) for c in (150, 160, 170))
        box(d, (1376, y, 1888, y + 92), fill=fill, outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((1392, y + 12), f"{t}  {s}", font=F[32], fill=INK)
        d.text((1392, y + 56), l, font=M[20], fill=INK)
    d.text((1376, 490), "ARMED ON END TURN (pointers land)", font=F[18], fill=DIM)
    for k, s in enumerate(["CACHE  lockout: draw 1 fewer", "CORE  +2 to adjacent", "ICE (yours)  fires for you"]):
        box(d, (1376, 520 + k * 54, 1888, 566 + k * 54), fill=(40, 20, 20) if k < 2 else RUN,
            outline=HARM if k < 2 else PINK)
        d.text((1392, 543 + k * 54), s, font=F[20], fill=TXT if k < 2 else INK, anchor="lm")
    d.text((1376, 700), "CORP STATUS", font=F[18], fill=DIM)
    box(d, (1376, 728, 1520, 760), outline=TEAL, label="ANTIVIRUS 2", lf=F[16], lc=TEAL, r=12)
    d.text((1376, 790), "ESCALATION   from turn 13", font=F[22], fill=TXT)
    # END TURN
    box(d, (1376, 880, 1888, 1020), fill=PINK, outline=INK, w=4)
    ctext(d, (1632, 930), "EXECUTE", F[56], INK)
    ctext(d, (1632, 988), "END TURN  [SPACE]   owned 3 -> 2, HP 27 -> 26", F[18], INK)
    note(d, (590, 92), "wheel centred: both flanks are used", f=F[16])
    header(d, "A", "ICEBREAKER RIG", "wheel centred; runner rig left, corp daemon right; programs as chips")
    return im


# ========================= B. SHELL =========================
def dir_b():
    im = Image.new("RGB", (W, H), (8, 12, 14))
    d = ImageDraw.Draw(im)
    # pane frames (tmux style)
    panes = {
        "whoami": (12, 12, 520, 250),
        "rig": (12, 258, 520, 862),
        "wheel": (528, 12, 1392, 862),
        "cron": (1400, 12, 1908, 520),
        "ps": (1400, 528, 1908, 862),
        "prompt": (12, 870, 1908, 1036),
    }
    for k, xy in panes.items():
        box(d, xy, fill=(10, 20, 24), outline=SYS, w=2)
    d.text((24, 22), "[0] whoami", font=M[18], fill=SYS)
    d.rectangle((24, 54, 508, 118), fill=RUN, outline=PINK, width=3)
    d.text((36, 86), "rhee  hp 27/28 -> 26", font=MB[28], fill=INK, anchor="lm")
    d.text((24, 136), "ram  [###]  3/3", font=M[24], fill=SYS)
    d.text((24, 172), "stat shroud:1  traced", font=M[24], fill=ORANGE)
    d.text((24, 208), "fs   stack 7  spent 3  purged 0", font=M[22], fill=TXT)
    d.text((24, 268), "[1] ls ~/rig/loaded", font=M[18], fill=SYS)
    for k, (n, c, w_, l, ok) in enumerate(HAND):
        y = 306 + k * 108
        col = TXT if ok else HARM
        if k == 2:
            d.rectangle((20, y - 8, 512, y + 92), fill=(40, 20, 34), outline=PINK, width=3)
        d.text((32, y), f"{k + 1}  {n.lower().replace(' ', '_')}", font=MB[28], fill=PINK if ok else HARM)
        d.text((460, y), f"{c}R", font=MB[28], fill=SYS if ok else HARM, anchor="ra")
        d.text((32, y + 40), f"   {w_:<8}{l}", font=M[20], fill=col)
        if not ok:
            d.text((32, y + 66), "   ! cannot run: needs 4 RAM", font=M[18], fill=HARM)
    d.text((540, 22), "[2] netstat --ring  (target host)", font=M[18], fill=SYS)
    cx, cy, R, rin = 960, 450, 360, 160
    wheel(d, cx, cy, R, rin)
    trace_arrows(d, cx, cy, R, rin)
    d.text((1412, 22), "[3] crontab -l  solace", font=M[18], fill=SYS)
    for k, (t, s, l) in enumerate(PLAN):
        y = 60 + k * 140
        box(d, (1412, y, 1896, y + 124), fill=(54, 62, 72) if k == 0 else (36, 42, 50),
            outline=ORANGE if k == 0 else TEAL, w=3 if k == 0 else 2)
        d.text((1428, y + 14), f"{t}  {s}", font=MB[32], fill=TXT)
        d.text((1428, y + 70), f"# {l}", font=M[22], fill=DIM)
    d.text((1412, 538), "[4] ps --armed", font=M[18], fill=SYS)
    for k, s in enumerate(["CACHE   lockout   draw -1", "CORE    repair    +2 adj", "ICE*    yours     fires",
                           "esc     +1 hp all from t13", "status  ANTIVIRUS 2"]):
        d.text((1412, 574 + k * 52), s, font=M[24], fill=HARM if k < 2 else (PINK if k == 2 else TXT))
    d.text((24, 880), "[5] rhee@cell:~$", font=M[18], fill=SYS)
    d.text((24, 930), "rhee@cell:~$ breach --target 02 ", font=MB[32], fill=PINK)
    d.rectangle((610, 914, 628, 950), fill=PINK)
    d.text((24, 986), "diff: FIREWALL 5 -> 2   |   END TURN: owned 3 -> 2, hp 27 -> 26 (16.1)", font=M[24],
           fill=SYS)
    box(d, (1500, 900, 1896, 1024), fill=PINK, outline=INK, w=4)
    ctext(d, (1698, 946), "commit", F[56], INK)
    ctext(d, (1698, 998), "END TURN  [SPACE]   rollback [Z]", F[18], INK)
    note(d, (540, 820), "keys 1-5 pick a program; arrows or click pick a host; Enter runs", f=F[16])
    header(d, "B", "SHELL", "a tiled terminal: every panel is a window; the prompt is where you act")
    return im


# ========================= C. TOKEN RING =========================
def track_slots():
    """12 slot rectangles on a stadium track: 5 top, 1 right, 5 bottom, 1 left (clockwise, 0 = top middle)."""
    slots = []
    sw, sh = 236, 180
    xs = [482 + k * (sw + 8) for k in range(5)]   # 482..1458
    top_y, bot_y = 96, 806
    # top row indices: 10,11,0,1,2 left->right  (0 is the top middle)
    order_top = [10, 11, 0, 1, 2]
    order_bot = [8, 7, 6, 5, 4]
    rect = {}
    for k, i in enumerate(order_top):
        rect[i] = (xs[k], top_y, xs[k] + sw, top_y + sh)
    for k, i in enumerate(order_bot):
        rect[i] = (xs[k], bot_y, xs[k] + sw, bot_y + sh)
    rect[3] = (1712, 360, 1900, 720)
    rect[9] = (20, 360, 208, 720)
    return rect


def dir_c():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    rect = track_slots()
    # track bed
    d.rounded_rectangle((8, 84, 1912, 998), 300, fill=(30, 36, 44), outline=TEAL, width=8)
    d.rounded_rectangle((226, 290, 1694, 792), 150, fill=BG, outline=TEAL, width=4)
    # corner slots are drawn on the curves as bigger cells
    corner = {10: None}
    for i, xy in rect.items():
        mine = i in MINE
        d.rectangle(xy, fill=RUN if mine else (44, 52, 62), outline=PINK if mine else TEAL, width=3)
        x0, y0, x1, y1 = xy
        seg_label(d, (x0 + x1) / 2, (y0 + y1) / 2 - 6, i, scale=1.1)
        if i in ARMED:
            d.rectangle((x0 + 4, y0 + 4, x1 - 4, y0 + 12) if y0 < 500 else (x0 + 4, y1 - 12, x1 - 4, y1 - 4),
                        fill=HARM)
        if i in OUTCOME:
            ox = (x0 + x1) / 2
            oy = y1 + 16 if y0 < 300 else (y0 - 16 if y0 > 700 else (y0 + y1) / 2)
            if i in (3, 9):
                ox = x0 - 60 if i == 3 else x1 + 60
            outcome_tag(d, ox, oy, i)
    # hover outline on 11
    d.rectangle(rect[11], outline=SYS, width=5)
    # pointers: sentries outside the track at fixed spots
    for i, (px, py, up) in {0: (1080 - 120 + 0, 88, True), 4: (1458 + 118, 994, False),
                            8: (482 + 118, 994, False)}.items():
        pass
    sentries = [((1088, 52), "down"), ((1576 - 118 + 118, 1030), "up"), ((600, 1030), "up")]
    for (x, y), dr in sentries:
        if dr == "down":
            d.polygon([(x, y + 40), (x - 26, y - 8), (x + 26, y - 8)], fill=GUN, outline=TXT)
        else:
            d.polygon([(x, y - 40), (x - 26, y + 8), (x + 26, y + 8)], fill=GUN, outline=TXT)
    note(d, (1010, 30), "fixed sentries (pointers) sit off the track", f=F[16])
    note(d, (1712, 734), "the ring shifts round the track", f=F[16])
    # infield: plan + spin + hand
    box(d, (300, 300, 560, 420), fill=(30, 36, 44), outline=TEAL, w=3)
    ctext(d, (430, 330), "CORP SHIFT", F[18], TXT)
    ctext(d, (430, 376), "-2  then +1 +1 -2", F[24], ORANGE)
    for k, (t, s, l) in enumerate(PLAN):
        x = 580 + k * 300
        box(d, (x, 300, x + 290, 420), fill=(150, 160, 170) if k == 0 else (90, 98, 108),
            outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((x + 12, 310), f"{t}  {s}", font=F[28], fill=INK)
        d.text((x + 12, 360), l, font=F[18], fill=INK)
    box(d, (1480, 300, 1680, 420), fill=SYSF, outline=SYS, w=2)
    d.text((1492, 312), "TURN 3", font=F[20], fill=SYS)
    d.text((1492, 342), "ESC from 13", font=F[20], fill=SYS)
    d.text((1492, 372), "OWNED 3 -> 2", font=F[20], fill=SYS)
    # hand (programs as packets in the infield)
    for k, c in enumerate(HAND):
        x = 300 + k * 230
        name, cost, word, line, ok = c
        box(d, (x, 436, x + 220, 620), fill=RUN if ok else (120, 110, 104),
            outline=HARM if not ok else (PINK if k == 2 else INK), w=4 if (k == 2 or not ok) else 2)
        d.rectangle((x, 436, x + 50, 486), fill=INK)
        ctext(d, (x + 25, 461), str(cost), F[32], SYS)
        d.text((x + 60, 446), name, font=F[28], fill=INK)
        d.rectangle((x + 10, 496, x + 120, 520), fill=PINK if ok else (90, 90, 90))
        d.text((x + 16, 508), word, font=F[16], fill=INK, anchor="lm")
        d.text((x + 10, 540), line, font=F[18], fill=INK)
        if not ok:
            d.rectangle((x + 6, 576, x + 214, 612), fill=HARM)
            ctext(d, (x + 110, 594), "NO RAM: needs 4", F[18], TXT)
    box(d, (1460, 436, 1680, 620), fill=PINK, outline=INK, w=4)
    ctext(d, (1570, 506), "SEND", F[48], INK)
    ctext(d, (1570, 566), "END TURN [SPACE]", F[18], INK)
    # health + ram + piles strip in infield bottom
    health_strip(d, (300, 636, 1000, 716))
    d.text((1020, 650), "RAM", font=F[20], fill=SYS)
    ram_bank(d, 1070, 646, 3, 3, 30)
    d.text((1200, 650), "SHROUD 1  TRACED", font=F[20], fill=ORANGE)
    d.text((1020, 694), "STACK 7  SPENT 3  [Z] ROLLBACK", font=M[20], fill=TXT)
    note(d, (300, 728), "infield = runner + plan; the track = the corp network", f=F[16])
    # trace arrow example from 10 (CORE) to 11 (ICE)
    d.line([((rect[10][0] + rect[10][2]) / 2 + 60, 200), ((rect[11][0] + rect[11][2]) / 2 - 40, 200)],
           fill=HARM, width=6)
    tag(d, ((rect[10][2] + rect[11][0]) / 2, 230), "13.1 -3", HARM)
    header(d, "C", "TOKEN RING", "the 12 segments as a stadium-shaped network loop that fills the 16:9 frame")
    return im


# ========================= D. VERSUS =========================
def dir_d():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # runner column
    box(d, (16, 16, 470, 840), fill=(40, 30, 36), outline=PINK, w=4)
    box(d, (36, 36, 450, 420), fill=RUN, outline=INK, w=3, label="RUNNER PORTRAIT (punk print)", lf=F[22], lc=INK)
    d.text((36, 436), "RHEE", font=F[48], fill=PINK)
    # vertical health
    d.rectangle((370, 436, 450, 820), fill=RUN, outline=PINK, width=3)
    for k in range(28):
        y = 812 - k * 13.4
        c = (60, 200, 90) if k < 26 else ((200, 60, 60) if k == 26 else (80, 80, 80))
        d.rectangle((382, y - 10, 438, y), fill=c)
    ctext(d, (300, 520), "27", F[72], TXT)
    ctext(d, (300, 584), "-> 26", F[32], HARM)
    d.text((36, 520), "RAM", font=F[22], fill=SYS)
    ram_bank(d, 36, 556, 3, 3, 44)
    d.text((36, 640), "SHROUD 1", font=F[24], fill=SYS)
    d.text((36, 676), "TRACED", font=F[24], fill=ORANGE)
    d.text((36, 740), "STACK 7  SPENT 3", font=M[22], fill=TXT)
    # corp column
    box(d, (1450, 16, 1904, 840), fill=(30, 36, 44), outline=TEAL, w=4)
    box(d, (1470, 36, 1884, 300), fill=(60, 70, 80), outline=TEAL, w=3, label="SOLACE SYSOP AVATAR (enamel)",
        lf=F[22], lc=TXT)
    d.text((1470, 316), "PLAN", font=F[22], fill=DIM)
    for k, (t, s, l) in enumerate(PLAN):
        y = 350 + k * 110
        box(d, (1470, y, 1884, y + 100), fill=(150, 160, 170) if k == 0 else (90, 98, 108),
            outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((1484, y + 12), f"{t}  {s}", font=F[32], fill=INK)
        d.text((1484, y + 60), l, font=F[18], fill=INK)
    d.text((1470, 690), "ESCALATION", font=F[22], fill=DIM)
    d.rectangle((1470, 724, 1884, 754), outline=TEAL, width=2)
    d.rectangle((1470, 724, 1470 + 414 * 3 // 13, 754), fill=TEAL)
    d.text((1470, 770), "turn 3 of 13   ANTIVIRUS 2", font=F[22], fill=TXT)
    # wheel center
    cx, cy, R, rin = 960, 430, 360, 150
    wheel(d, cx, cy, R, rin)
    trace_arrows(d, cx, cy, R, rin)
    d.text((960, 20), "STATIC ALLEY  T1  |  FIREWALL WHEEL rule  |  OWNED 3 -> 2", font=M[20], fill=SYS,
           anchor="ma")
    # hand: fanned exploit chips along the bottom
    for k, c in enumerate(HAND):
        ang = (k - 2) * 4
        x = 520 + k * 178
        y = 860 + abs(k - 2) * 10
        name, cost, word, line, ok = c
        chip = Image.new("RGBA", (170, 190), (0, 0, 0, 0))
        cd = ImageDraw.Draw(chip)
        cd.rectangle((0, 0, 169, 189), fill=RUN if ok else (120, 110, 104),
                     outline=HARM if not ok else (PINK if k == 2 else INK), width=4)
        cd.rectangle((0, 0, 44, 44), fill=INK)
        cd.text((22, 22), str(cost), font=F[28], fill=SYS, anchor="mm")
        cd.text((52, 10), name if len(name) < 8 else "T.BOMB", font=F[24], fill=INK)
        cd.rectangle((8, 56, 110, 78), fill=PINK if ok else (90, 90, 90))
        cd.text((14, 67), word, font=F[16], fill=INK, anchor="lm")
        words = line.split()
        cd.text((8, 92), " ".join(words[:3]), font=F[18], fill=INK)
        cd.text((8, 116), " ".join(words[3:]), font=F[18], fill=INK)
        if not ok:
            cd.rectangle((4, 148, 165, 184), fill=HARM)
            cd.text((84, 166), "needs 4 RAM", font=F[18], fill=TXT, anchor="mm")
        chip = chip.rotate(-ang, expand=True, resample=Image.BICUBIC)
        im.paste(chip, (x, y), chip)
    box(d, (1460, 870, 1904, 1030), fill=PINK, outline=INK, w=4)
    ctext(d, (1682, 930), "JACK OUT TURN", F[48], INK)
    ctext(d, (1682, 990), "END TURN [SPACE]   UNDO [Z]", F[20], INK)
    note(d, (20, 860), "fighting-game frame:\nrunner left, corp right,\nhand fans under the wheel", f=F[18])
    header(d, "D", "VERSUS", "runner and sysop face off across the wheel; hand fans along the bottom")
    return im


# ========================= E. PLATTER =========================
def dir_e():
    im = Image.new("RGB", (W, H), (34, 32, 36))
    d = ImageDraw.Draw(im)
    # deck chassis
    d.rounded_rectangle((10, 10, 1910, 1040), 40, fill=(48, 46, 52), outline=(90, 88, 96), width=6)
    # stickers on chassis (runner punk)
    for (x, y, s) in [(60, 940, "NO GODS NO SYSOPS"), (1520, 40, "CELL-9")]:
        d.rectangle((x, y, x + d.textlength(s, font=F[24]) + 24, y + 40), fill=PINK)
        d.text((x + 12, y + 20), s, font=F[24], fill=INK, anchor="lm")
    # platter
    cx, cy, R, rin = 900, 392, 330, 130
    wheel(d, cx, cy, R, rin, hub_label=("SPINDLE", "-2", "then +1 +1 -2"), ptr_style=None)
    # read heads (actuator arms) for pointers
    for p, pivot in zip(POINTERS, [(900, 22), (1330, 700), (470, 700)]):
        a = -90 + p * 30
        tip = polar(cx, cy, R - 6, a)
        d.line([pivot, tip], fill=GUN, width=22)
        d.ellipse((pivot[0] - 34, pivot[1] - 34, pivot[0] + 34, pivot[1] + 34), fill=GUN, outline=TXT, width=3)
        d.rectangle((tip[0] - 16, tip[1] - 16, tip[0] + 16, tip[1] + 16), fill=(200, 200, 205), outline=INK)
    note(d, (1000, 30), "pointers = read heads on fixed arms; the platter spins", f=F[16])
    trace_arrows(d, cx, cy, R, rin)
    # left: LEDs/RAM sticks + EKG
    d.rectangle((40, 60, 300, 230), fill=(10, 30, 20), outline=(90, 88, 96), width=4)
    d.text((54, 70), "VITALS", font=M[18], fill=(80, 240, 120))
    pts = [(54 + k * 8, 160 + (0 if k % 9 else -50) + (20 if k % 9 == 1 else 0)) for k in range(30)]
    d.line(pts, fill=(80, 240, 120), width=3)
    d.text((54, 196), "HP 27 -> 26", font=MB[24], fill=HARM)
    d.text((40, 260), "RAM DIMMS", font=M[18], fill=SYS)
    for k in range(3):
        d.rectangle((40 + k * 70, 290, 96 + k * 70, 470), fill=(20, 60, 40), outline=SYS, width=3)
        d.ellipse((58 + k * 70, 440, 78 + k * 70, 460), fill=SYS)
    d.text((40, 500), "SHROUD 1  TRACED", font=M[20], fill=ORANGE)
    d.text((40, 536), "STACK 7  SPENT 3", font=M[20], fill=TXT)
    # right: corp ticker printer
    d.rectangle((1380, 110, 1880, 640), fill=(26, 30, 36), outline=TEAL, width=4)
    d.text((1396, 122), "INCOMING: SOLACE SCHEDULE (printer tape)", font=F[18], fill=TEAL)
    for k, (t, s, l) in enumerate(PLAN):
        y = 160 + k * 120
        d.rectangle((1400, y, 1860, y + 108), fill=(232, 236, 232) if k == 0 else (170, 176, 172),
                    outline=ORANGE if k == 0 else TEAL, width=4 if k == 0 else 2)
        d.text((1414, y + 12), f"{t}  {s}", font=MB[32], fill=INK)
        d.text((1414, y + 62), l, font=M[22], fill=INK)
    d.text((1396, 540), "TURN 3   ESC from 13", font=M[22], fill=TXT)
    d.text((1396, 576), "OWNED 3 -> 2", font=M[22], fill=SYS)
    # bottom: cartridge slots (programs) on the keyboard deck
    d.rectangle((320, 900, 1880, 1030), fill=(30, 28, 34), outline=(90, 88, 96), width=3)
    for k, c in enumerate(HAND):
        name, cost, word, line, ok = c
        x = 340 + k * 236
        d.rectangle((x, 760, x + 220, 1012), fill=RUN if ok else (120, 110, 104),
                    outline=HARM if not ok else (PINK if k == 2 else INK), width=4 if (k == 2 or not ok) else 2)
        d.rectangle((x + 20, 960, x + 200, 1012), fill=(200, 170, 60))  # contacts
        for pin in range(10):
            d.line([(x + 30 + pin * 17, 966), (x + 30 + pin * 17, 1006)], fill=(120, 90, 30), width=4)
        d.text((x + 10, 770), name, font=F[28], fill=INK)
        d.text((x + 200, 772), f"{cost}", font=F[32], fill=SYS if ok else HARM, anchor="ra")
        d.rectangle((x + 10, 812, x + 120, 836), fill=PINK if ok else (90, 90, 90))
        d.text((x + 16, 824), word, font=F[16], fill=INK, anchor="lm")
        d.text((x + 10, 852), line, font=F[18], fill=INK)
        if not ok:
            d.rectangle((x + 6, 900, x + 214, 940), fill=HARM)
            ctext(d, (x + 110, 920), "NO RAM: needs 4", F[18], TXT)
    d.rounded_rectangle((1540, 690, 1880, 880), 18, fill=PINK, outline=INK, width=6)
    ctext(d, (1710, 762), "EXEC", F[72], INK)
    ctext(d, (1710, 836), "END TURN [SPACE]", F[20], INK)
    d.rounded_rectangle((1540, 900, 1700, 1020), 12, fill=RUN, outline=INK, width=4)
    ctext(d, (1620, 960), "BKSP\n[Z] undo", F[20], INK)
    header(d, "E", "PLATTER DECK", "the screen is the cyberdeck: wheel = disk platter, pointers = read heads")
    return im


def sheet(paths):
    tw, th = 960, 540
    cols = 2
    rows = (len(paths) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16 + 60), (8, 8, 10))
    d = ImageDraw.Draw(sh)
    d.text((16, 30), "Takeover screen: alternative directions (wireframes, 2026-11-14)", font=F[28], fill=NOTE,
           anchor="lm")
    for k, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        x = 16 + (k % cols) * (tw + 16)
        y = 60 + 16 + (k // cols) * (th + 16)
        sh.paste(im, (x, y))
    return sh


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for code, fn, name in [("a", dir_a, "icebreaker_rig"), ("b", dir_b, "shell"), ("c", dir_c, "token_ring"),
                           ("d", dir_d, "versus"), ("e", dir_e, "platter_deck")]:
        p = os.path.join(OUT, f"alt_{code}_{name}.png")
        fn().save(p)
        paths.append(p)
        print("wrote", p)
    sp = os.path.join(OUT, "alternatives_sheet.jpg")
    sheet(paths).save(sp, quality=90)
    print("wrote", sp)
