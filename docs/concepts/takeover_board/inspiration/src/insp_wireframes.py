"""Rough 1920x1080 wireframes for the top 3 inspiration concepts + one sheet.

Run: python insp_wireframes.py
Flat blocks + labels. Yellow text is annotation.
"""
import math
import os
import sys

sys.path.insert(0, r"D:/rc_scratch/takeover/alternatives")
from alt_wireframes import (  # noqa: E402
    W, H, F, M, MB, BG, RUN, PINK, INK, CORP, TEAL, GUN, SYS, SYSF, HARM, TXT, DIM, NOTE, ORANGE,
    HAND, PLAN, MINE, TYPES, INTS, ARMED, ctext, box, note, header, wheel, polar, wedge_poly,
    health_strip, ram_bank, tag,
)
from PIL import Image, ImageDraw  # noqa: E402

OUT = r"D:/rc_art/art-pass/docs/concepts/takeover_board/inspiration"
os.makedirs(OUT, exist_ok=True)

CX, CY, R, RIN = 960, 568, 360, 160
SLATE = (40, 47, 56)
# placeholder type colours (the locked type-plate colours would replace these)
TYPEC = {"CONTROL": (176, 150, 255), "VIRUS": (120, 230, 110), "FIRE": (255, 140, 60),
         "BLOCK": (110, 170, 255), "DELAY": (170, 170, 170)}


def topbar(d):
    box(d, (0, 10, W, 62), fill=SYSF, outline=SYS)
    d.text((20, 36), "STATIC ALLEY  T1 FIGHT  |  FIREWALL WHEEL", font=M[20], fill=SYS, anchor="lm")
    d.text((W - 20, 36), "TURN 3   ESC from 13   OWNED 3/12 -> 2   HP 27 -> 26", font=M[20], fill=SYS,
           anchor="rm")


def execute_btn(d, x0, y0, x1, y1, word="EXECUTE"):
    box(d, (x0, y0, x1, y1), fill=PINK, outline=INK, w=4)
    ctext(d, ((x0 + x1) / 2, y0 + 44), word, F[48], INK)
    ctext(d, ((x0 + x1) / 2, y1 - 22), "END TURN [SPACE]  +0 taken -1 lost, HP 27->26", F[16], INK)


def dashed(d, p0, p1, fill, width=4, dash=16, gap=10):
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L // (dash + gap)) + 1
    for k in range(n):
        a = k * (dash + gap) / L
        b = min(1.0, (k * (dash + gap) + dash) / L)
        d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
               fill=fill, width=width)


def arrowhead(d, p0, p1, fill, size=18):
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    a1 = ang + math.radians(150)
    a2 = ang - math.radians(150)
    d.polygon([p1, (p1[0] + size * math.cos(a1), p1[1] + size * math.sin(a1)),
               (p1[0] + size * math.cos(a2), p1[1] + size * math.sin(a2))], fill=fill)


def seg_center(i, r=None):
    return polar(CX, CY, r if r is not None else (R + RIN) / 2 + 12, -90 + i * 30)


def piles_line(d, x, y, words=("QUEUED 7", "SENT 3", "DROPPED 0")):
    d.text((x, y), "   ".join(words), font=M[20], fill=TXT)


# ============================ 1. PACKET LADDER ============================
def c1():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    topbar(d)
    # runner column: punk print host header + lifeline
    LX = 488
    box(d, (20, 74, 470, 150), fill=RUN, outline=PINK, w=3)
    d.text((34, 82), "HOST  rhee@cell  (you)", font=F[20], fill=INK)
    ram_bank(d, 34, 110, 3, 3, size=22)
    d.text((150, 112), "RAM 3/3", font=F[20], fill=INK)
    d.text((262, 112), "SHROUD 1  TRACED", font=F[16], fill=INK)
    d.line([(LX, 74), (LX, 1000)], fill=PINK, width=6)
    d.text((20, 166), "OUTBOX  (hand): one packet per action", font=F[18], fill=DIM)
    ys = [200, 300, 400, 500, 600]
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        y = ys[k]
        sel = k == 2
        fill = RUN if ok else (110, 100, 96)
        box(d, (20, y, 460, y + 86), fill=fill, outline=PINK if sel else (HARM if not ok else INK),
            w=4 if sel or not ok else 2)
        # header fields: len (cost) | flag (type word) | dst (target rule)
        d.rectangle((20, y, 82, y + 86), fill=INK)
        ctext(d, (51, y + 30), str(cost), F[32], SYS)
        ctext(d, (51, y + 64), "len", F[14], SYS)
        d.text((94, y + 6), f"[{k + 1}] {name}", font=F[28], fill=INK)
        tw = d.textlength(word, font=F[16]) + 14
        d.rectangle((94, y + 46, 94 + tw, y + 70), fill=TYPEC[word])
        d.text((101, y + 58), word, font=F[16], fill=INK, anchor="lm")
        dst = {"NUDGE": "dst HUB", "WORM": "dst 3x THEIRS", "BREACH": "dst THEIRS*", "GUARD": "dst YOURS",
               "TIME BOMB": "dst THEIRS"}[name]
        d.text((94 + tw + 10, y + 58), dst, font=M[18], fill=INK, anchor="lm")
        if not ok:
            d.rectangle((300, y + 6, 454, y + 34), fill=HARM)
            ctext(d, (377, y + 20), "RST: needs 4", F[16], TXT)
        # port on the lifeline
        d.line([(460, y + 43), (LX, y + 43)], fill=PINK if sel else (90, 80, 90), width=3)
        d.ellipse((LX - 9, y + 34, LX + 9, y + 52), fill=PINK if sel else RUN, outline=INK, width=2)
    note(d, (20, 694), "* BREACH: a corp segment next to yours", f=F[16])
    # aim: dashed packet arrow from BREACH port to CORE (wedge 10)
    src = (LX, 443)
    tgt = seg_center(10, R - 40)
    dashed(d, src, tgt, PINK, width=5)
    arrowhead(d, src, tgt, PINK, 22)
    tag(d, (660, 176), "P1  BREACH  CORE 7 -> 4", PINK, fill=RUN, tc=INK)
    d.line([(640, 190), (560, 436)], fill=PINK, width=2)
    # legal targets ring: CORE (10) and FIREWALL (2)
    piles_line(d, 20, 740)
    d.text((20, 774), "queued = draw   sent = discard   dropped = exhaust", font=F[16], fill=DIM)
    box(d, (20, 940, 250, 1000), fill=RUN, outline=INK, label="[Z] ROLLBACK", lf=F[22], lc=INK)
    health_strip(d, (20, 820, 470, 910), label="RHEE  LINK")
    # wheel
    wheel(d, CX, CY, R, RIN, hover=None)
    for i in (2, 10):
        a0 = -90 + i * 30 - 15
        d.line(wedge_poly(CX, CY, RIN, R, a0 + 0.8, a0 + 29.2) + [polar(CX, CY, R, a0 + 0.8)], fill=PINK,
               width=5)
    # corp column: lifeline + schedule packets
    RX = 1432
    d.line([(RX, 74), (RX, 1000)], fill=TEAL, width=6)
    box(d, (1450, 74, 1900, 150), fill=CORP, outline=TEAL, w=3)
    d.text((1464, 82), "HOST  solace.sys  (corp)", font=F[20], fill=TEAL)
    d.text((1464, 114), "ANTIVIRUS 2    ESC from turn 13", font=F[16], fill=TXT)
    d.text((1450, 166), "INBOUND  (corp plan, fires on END TURN)", font=F[18], fill=DIM)
    for k, (t, s, l) in enumerate(PLAN):
        y = 200 + k * 100
        v = [1.0, 0.75, 0.55][k]
        fill = tuple(int(c * v) for c in (150, 160, 170))
        box(d, (1450, y, 1900, y + 86), fill=fill, outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((1466, y + 8), f"{t}  {s}", font=F[28], fill=INK)
        d.text((1466, y + 50), l, font=M[18], fill=INK)
        d.line([(RX, y + 43), (1450, y + 43)], fill=TEAL, width=3)
        d.ellipse((RX - 9, y + 34, RX + 9, y + 52), fill=CORP, outline=TEAL, width=2)
    # NOW packet routes to the hub (B-088: the plan strikes from the hub)
    rim_pt = polar(CX, CY, R + 22, -42)
    dashed(d, (RX, 243), rim_pt, TEAL, width=3)
    arrowhead(d, (RX, 243), rim_pt, TEAL, 16)
    tag(d, (1330, 200), "11.1 via hub", TEAL, fill=SYSF, tc=SYS)
    d.text((1450, 512), "ARMED  (pointers land)", font=F[18], fill=DIM)
    for k, s in enumerate(["CACHE  lockout  draw -1", "CORE  repair  +2 adjacent"]):
        box(d, (1450, 540 + k * 50, 1900, 582 + k * 50), fill=(40, 20, 20), outline=HARM)
        d.text((1466, 561 + k * 50), s, font=F[20], fill=TXT, anchor="lm")
    d.text((1450, 660), "LOG  (last END TURN, numbered)", font=F[18], fill=DIM)
    for k, s in enumerate(["8.1  RELAY -> CORE  +2", "11.1 STRIKE -> ICE  -2", "13.1 CORE -> ICE  -3"]):
        d.text((1466, 690 + k * 32), s, font=M[20], fill=TXT)
    execute_btn(d, 1450, 860, 1900, 1000, "SEND")
    note(d, (540, 72), "both flanks are hosts on a flow graph; the wheel is the wire between them", f=F[16])
    note(d, (520, 1012), "pick a packet (1-5): its dst field lights legal wedges; click a wedge: dashed arrow + P1 "
         "preview on the wedge; Enter sends", f=F[16])
    header(d, "1", "PACKET LADDER", "actions are packets on your lifeline; the aim, the forecast and the replay "
           "are one numbered-arrow grammar")
    return im


# ============================ 2. SPLICE (signal) ============================
def wave(d, x0, y0, x1, y1, word, col, w=3, amp_scale=1.0):
    """Draw a type-word waveform in the box (x0..x1, centred on (y0+y1)/2)."""
    ym = (y0 + y1) / 2
    A = (y1 - y0) / 2 * 0.8 * amp_scale
    pts = []
    n = int(x1 - x0)
    for k in range(0, n, 2):
        t = k / n
        x = x0 + k
        if word == "CONTROL":      # square wave
            y = ym - A if int(t * 8) % 2 == 0 else ym + A
        elif word == "VIRUS":      # noise
            y = ym + A * math.sin(k * 1.7) * math.sin(k * 0.31) * math.cos(k * 0.07 + 1)
        elif word == "FIRE":       # single spike train
            ph = (t * 4) % 1
            y = ym - A * (1 - ph * 6) if ph < 0.16 else ym + A * 0.15
        elif word == "BLOCK":      # clamped flatline between rails
            y = ym - A * 0.15 * math.sin(k * 0.2)
        else:                      # DELAY: pulse train with a gap, then a pulse
            ph = (t * 6) % 1
            y = ym - A if (ph < 0.12 and t > 0.62) else ym
        pts.append((x, y))
    d.line(pts, fill=col, width=w)
    if word == "BLOCK":
        d.line([(x0, ym - A * 0.5), (x1, ym - A * 0.5)], fill=col, width=1)
        d.line([(x0, ym + A * 0.5), (x1, ym + A * 0.5)], fill=col, width=1)


def rim_wave(d, i, word, col, r_in, r_out, sel=False):
    """Waveform drawn along the outer band of wedge i (angle = x, radius = y)."""
    a0 = -90 + i * 30 - 13
    a1 = a0 + 26
    rm = (r_in + r_out) / 2
    A = (r_out - r_in) / 2 * 0.9
    pts = []
    n = 120
    for k in range(n + 1):
        t = k / n
        a = a0 + (a1 - a0) * t
        if word == "FIRE":
            ph = (t * 3) % 1
            r = rm + (A * (1 - ph * 6) if ph < 0.16 else -A * 0.15)
        elif word == "BLOCK":
            r = rm + A * 0.12 * math.sin(k * 0.6)
        elif word == "VIRUS":
            r = rm + A * math.sin(k * 1.7) * math.sin(k * 0.31)
        else:
            r = rm
        pts.append(polar(CX, CY, r, a))
    d.line(pts, fill=col, width=5 if sel else 3)


def c2():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    topbar(d)
    # left: payload channels (logic analyser)
    box(d, (14, 74, 520, 1000), fill=(14, 22, 26), outline=SYS, w=2)
    health_strip(d, (26, 84, 508, 160), label="RHEE  LINK")
    d.text((26, 172), "PAYLOAD  CH1-CH5  (hand)", font=F[18], fill=SYS)
    ram_bank(d, 300, 168, 3, 3, size=20)
    d.text((388, 172), "3 / 3", font=F[18], fill=SYS)
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        y = 206 + k * 128
        sel = k == 2
        col = TYPEC[word] if ok else (110, 110, 110)
        box(d, (26, y, 508, y + 118), fill=(22, 34, 40) if not sel else (44, 30, 44),
            outline=PINK if sel else (HARM if not ok else (50, 70, 80)), w=4 if sel or not ok else 2)
        # label column = punk print chip
        d.rectangle((26, y, 196, y + 118), fill=RUN if ok else (110, 100, 96))
        d.text((36, y + 8), f"CH{k + 1}", font=F[16], fill=INK)
        d.text((190, y + 8), f"{cost} RAM", font=F[16], fill=INK, anchor="ra")
        d.text((36, y + 30), name, font=F[24] if len(name) > 6 else F[28], fill=INK)
        tw = d.textlength(word, font=F[16]) + 14
        d.rectangle((36, y + 66, 36 + tw, y + 90), fill=col)
        d.text((43, y + 78), word, font=F[16], fill=INK, anchor="lm")
        tgt = {"NUDGE": "o hub", "WORM": "x3 theirs", "BREACH": "> theirs", "GUARD": "< yours",
               "TIME BOMB": "> theirs"}[name]
        d.text((36, y + 96), tgt, font=M[16], fill=INK)
        # the trace
        d.line([(206, y + 59), (500, y + 59)], fill=(40, 60, 70), width=1)
        wave(d, 210, y + 14, 498, y + 104, word, col, w=4 if sel else 3)
        if not ok:
            d.rectangle((300, y + 4, 502, y + 30), fill=HARM)
            ctext(d, (401, y + 17), "NO SIGNAL: needs 4", F[16], TXT)
    piles_line(d, 26, 852, ("BUFFER 7", "LOGGED 3", "BURNT 0"))
    d.text((26, 884), "buffer = draw   logged = discard   burnt = exhaust", font=F[16], fill=DIM)
    box(d, (26, 926, 250, 986), fill=RUN, outline=INK, label="[Z] ROLLBACK", lf=F[22], lc=INK)
    # wheel with a signal band on the rim
    wheel(d, CX, CY, R, RIN, hover=None)
    # persistent splices: GUARD (BLOCK) on wedge 11, VIRUS on wedge 6
    rim_wave(d, 11, "BLOCK", TYPEC["BLOCK"], R - 44, R - 8)
    rim_wave(d, 6, "VIRUS", TYPEC["VIRUS"], R - 44, R - 8)
    # aimed BREACH preview on CORE (10)
    rim_wave(d, 10, "FIRE", PINK, R - 44, R - 8, sel=True)
    # probe line from the channel trace to the wedge
    p0 = (508, 206 + 2 * 128 + 59)
    p1 = polar(CX, CY, R - 26, -90 + 10 * 30)
    dashed(d, p0, p1, PINK, width=4)
    tag(d, (630, 236), "splice: CORE 7 -> 4", PINK, fill=RUN, tc=INK)
    tag(d, (700, 960), "VIRUS splice stays on RELAY", TYPEC["VIRUS"])
    tag(d, (640, 170), "GUARD clamp on your ICE", TYPEC["BLOCK"])
    note(d, (560, 1012), "the corp's rim is a live band; your actions are waveforms spliced into a wedge's band",
         f=F[16])
    # right: carrier waterfall (corp plan + history)
    box(d, (1400, 74, 1906, 1000), fill=(18, 22, 28), outline=TEAL, w=2)
    d.text((1414, 84), "CARRIER  solace.sys  (plan falls toward NOW)", font=F[18], fill=TEAL)
    rows = [("T+2", "SURGE 3", "from CORE, both ways", 0.45), ("T+1", "WALL", "both sides of CORE", 0.65),
            ("NOW", "STRIKE 2", "your weakest segment", 1.0)]
    for k, (t, s, l, v) in enumerate(rows):
        y = 120 + k * 104
        fill = tuple(int(c * v) for c in (150, 160, 170))
        box(d, (1414, y, 1892, y + 92), fill=fill, outline=ORANGE if t == "NOW" else TEAL,
            w=4 if t == "NOW" else 2)
        d.text((1430, y + 10), f"{t}  {s}", font=F[28], fill=INK)
        d.text((1430, y + 52), l, font=M[18], fill=INK)
    d.text((1414, 440), "WATERFALL  (past turns scroll down, fading)", font=F[16], fill=DIM)
    for k in range(10):
        y = 466 + k * 18
        g = int(110 - k * 9)
        d.rectangle((1414, y, 1892, y + 14), fill=(g // 3, g // 2, g // 2))
        for j in range(12):
            if (j * 7 + k * 3) % 5 == 0:
                d.rectangle((1414 + j * 40, y, 1414 + j * 40 + 30, y + 14), fill=(g, int(g * 1.6), int(g * 1.5)))
    d.text((1414, 662), "ARMED  (pointers land)", font=F[18], fill=DIM)
    for k, s in enumerate(["CACHE  lockout  draw -1", "CORE  repair  +2 adjacent"]):
        box(d, (1414, 690 + k * 48, 1892, 730 + k * 48), fill=(40, 20, 20), outline=HARM)
        d.text((1430, 710 + k * 48), s, font=F[20], fill=TXT, anchor="lm")
    execute_btn(d, 1414, 846, 1892, 986, "TRANSMIT")
    header(d, "2", "SPLICE", "actions are signals on your channels; the type word is the waveform; aim = probe "
           "a wedge's rim band")
    return im


# ============================ 3. ROTOR ============================
def c3():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    topbar(d)
    # left: the cylinder (stack of disks seen edge-on)
    health_strip(d, (20, 74, 500, 150), label="RHEE  LINK")
    d.text((20, 164), "CYLINDER  (your rotor stack)", font=F[18], fill=DIM)
    ram_bank(d, 290, 160, 3, 3, size=20)
    d.text((380, 164), "RAM 3/3", font=F[18], fill=SYS)
    for k, (name, cost, word, line, ok) in enumerate(HAND):
        y = 200 + k * 100
        sel = k == 2
        # edge-on disk: a long rounded band with a notch tab
        fill = RUN if ok else (110, 100, 96)
        d.rounded_rectangle((20, y, 470, y + 86), 40, fill=fill, outline=PINK if sel else (HARM if not ok else INK),
                            width=4 if sel or not ok else 2)
        # cost = notches cut into the band edge
        for c in range(max(cost, 0)):
            d.rectangle((60 + c * 22, y, 74 + c * 22, y + 12), fill=BG)
        if cost == 0:
            d.text((60, y + 2), "0", font=F[14], fill=INK)
        d.text((48, y + 18), f"[{k + 1}] {name}", font=F[28], fill=INK)
        tw = d.textlength(word, font=F[16]) + 14
        d.rectangle((48, y + 54, 48 + tw, y + 78), fill=TYPEC[word])
        d.text((55, y + 66), word, font=F[16], fill=INK, anchor="lm")
        d.text((48 + tw + 10, y + 66), f"{cost} RAM  {line}", font=F[16], fill=INK, anchor="lm")
        if not ok:
            d.rectangle((300, y + 14, 462, y + 42), fill=HARM)
            ctext(d, (381, y + 28), "BINDS: needs 4", F[16], TXT)
    # rest of the stack as thin disks
    for k in range(7):
        y = 712 + k * 9
        d.rounded_rectangle((40, y, 450, y + 6), 3, fill=(120, 112, 104))
    d.text((20, 784), "STACK 7  (draw)", font=M[20], fill=TXT)
    d.text((250, 784), "SPENT 3   PURGED 0", font=M[20], fill=TXT)
    for k in range(3):
        y = 820 + k * 9
        d.rounded_rectangle((250, y, 470, y + 6), 3, fill=(80, 74, 70))
    box(d, (20, 940, 250, 1000), fill=RUN, outline=INK, label="[Z] ROLLBACK", lf=F[22], lc=INK)
    note(d, (20, 860), "spent disks drop to the bottom of the cylinder", f=F[16])
    # wheel + the drawn rotor ring around it
    wheel(d, CX, CY, R, RIN, hover=None)
    RR0, RR1 = R + 22, R + 52
    d.ellipse((CX - RR1, CY - RR1, CX + RR1, CY + RR1), outline=PINK, width=6)
    d.ellipse((CX - RR0, CY - RR0, CX + RR0, CY + RR0), outline=PINK, width=2)
    # detents: legal (2, 10) bright, illegal dim red
    for i in range(12):
        a = -90 + i * 30
        p0 = polar(CX, CY, RR0, a)
        p1 = polar(CX, CY, RR1 + 10, a)
        legal = i in (2, 10)
        d.line([p0, p1], fill=SYS if legal else (110, 40, 40), width=8 if legal else 3)
    # the ring's notch sits on CORE (10): engraved stamp preview
    nx, ny = polar(CX, CY, RR1 + 30, -90 + 10 * 30)
    d.polygon([polar(CX, CY, RR1 + 2, -90 + 300), polar(CX, CY, RR1 + 46, -90 + 294),
               polar(CX, CY, RR1 + 46, -90 + 306)], fill=PINK, outline=INK)
    tag(d, (710, 96), "BREACH ring: notch on CORE 7 -> 4", PINK, fill=RUN, tc=INK)
    tag(d, (1290, 230), "FIREWALL: legal detent", SYS, fill=SYSF, tc=SYS)
    tp = polar(CX, CY, RR1 + 6, 30)
    d.line([tp, (1250, 946)], fill=HARM, width=2)
    tag(d, (1250, 960), "TURRET: binds (not next to yours)", HARM)
    # hub step arrows for no-target CONTROL (NUDGE)
    note(d, (20, 896), "NUDGE (no target) steps the hub ring +1 / -1", f=F[16])
    # right: key sheet
    box(d, (1440, 74, 1904, 1000), fill=(26, 30, 36), outline=TEAL, w=3)
    d.text((1456, 84), "KEY SHEET  solace.sys", font=F[20], fill=TEAL)
    for k, (t, s, l) in enumerate(PLAN):
        y = 120 + k * 100
        v = [1.0, 0.75, 0.55][k]
        fill = tuple(int(c * v) for c in (150, 160, 170))
        box(d, (1456, y, 1888, y + 88), fill=fill, outline=ORANGE if k == 0 else TEAL, w=4 if k == 0 else 2)
        d.text((1472, y + 8), f"{t}  {s}", font=F[28], fill=INK)
        d.text((1472, y + 50), l, font=M[18], fill=INK)
    d.text((1456, 432), "SPIN SCHEDULE  -2  then +1 +1 -2", font=F[20], fill=ORANGE)
    d.text((1456, 476), "ARMED  (pawls land)", font=F[18], fill=DIM)
    for k, s in enumerate(["CACHE  lockout  draw -1", "CORE  repair  +2 adjacent"]):
        box(d, (1456, 504 + k * 48, 1888, 544 + k * 48), fill=(40, 20, 20), outline=HARM)
        d.text((1472, 524 + k * 48), s, font=F[20], fill=TXT, anchor="lm")
    d.text((1456, 620), "ANTIVIRUS 2    ESC from turn 13", font=F[18], fill=TXT)
    execute_btn(d, 1456, 846, 1888, 986, "TURN KEY")
    note(d, (540, 1012), "pick a disk: it rises as a ring round the wheel; turn it (mouse angle, Q/E, Tab) "
         "and it clicks only into legal detents", f=F[16])
    header(d, "3", "ROTOR", "actions are cipher rings; aim = turn the ring to a detent; the wheel's own geometry")
    return im


def sheet(paths):
    tw, th = 960, 540
    pad, top = 16, 70
    S = Image.new("RGB", (tw * 2 + pad * 3, top + (th + pad) * 2), (10, 10, 12))
    d = ImageDraw.Draw(S)
    d.text((pad, 34), "Takeover: inspiration concepts, top 3 wireframes + ranking (2026-11-14)", font=F[32],
           fill=NOTE, anchor="lm")
    for k, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        x = pad + (k % 2) * (tw + pad)
        y = top + (k // 2) * (th + pad)
        S.paste(im, (x, y))
    # 4th cell: ranking
    x = pad + tw + pad
    y = top + th + pad
    d.rectangle((x, y, x + tw, y + th), fill=(18, 20, 26), outline=NOTE, width=2)
    lines = [("RANKING", NOTE, F[28]),
             ("1  PACKET LADDER  (recommended)", PINK, F[24]),
             ("   aim, forecast and replay share one numbered-arrow grammar", TXT, F[18]),
             ("2  SPLICE", TXT, F[24]),
             ("   type word = waveform; lasting effects live on the rim band", TXT, F[18]),
             ("3  ROTOR", TXT, F[24]),
             ("   cipher rings turned to legal detents; most wheel-native", TXT, F[18]),
             ("4  FOOTPRINT  (text only)", DIM, F[24]),
             ("   each action is its target shape, a key whose bitting fits", DIM, F[18]),
             ("5  DEFACE  (text only)", DIM, F[24]),
             ("   stencil tags over corp enamel; the punk layer as the hack", DIM, F[18]),
             ("Borrow: SPLICE waveform as the type glyph on each packet.", NOTE, F[20])]
    yy = y + 24
    for s, c, f in lines:
        d.text((x + 24, yy), s, font=f, fill=c)
        yy += 40 if f in (F[24], F[28]) else 32
    S.save(os.path.join(OUT, "inspiration_sheet.jpg"), quality=88)


if __name__ == "__main__":
    paths = []
    for fn, name in ((c1, "insp_1_packet_ladder.png"), (c2, "insp_2_splice.png"), (c3, "insp_3_rotor.png")):
        p = os.path.join(OUT, name)
        fn().save(p)
        paths.append(p)
    sheet(paths)
    print("ok", paths)
