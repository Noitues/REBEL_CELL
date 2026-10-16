"""HQ Rebel Cell: H_mechanic_states.png (2560 x 1440): row 1 the red sequence (before, blackout, spreading, full),
row 2 option A's three frames (mid-run, the kill-switch moment, the showdown), row 3 the rule cards and the GDD
questions. Reads ../scratch/RED_SHOTS/*_plate.png and ../scratch/OPTION_SHOTS/*.png (hq_compose.py <FN> all <bl>).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
RED = (255, 44, 52)


def card(sheet, xy, size, title, lines, col, fs=18):
    x, y = xy
    w, h = size
    img = sheet.convert("RGBA")
    img = KT.term(img, (x, y, x + w, y + h), title, accent=col, seed=61)
    for k, ln in enumerate(lines):
        K.text(img, (x + 22, y + 60 + k * int(fs * 1.42)), ln, K.F(K.MONO, fs), (215, 225, 232), "lm", 0.3)
    return img.convert("RGB")


def main():
    W, H = 2560, 1440
    sheet = Image.new("RGB", (W, H), (12, 10, 18))
    img = sheet.convert("RGBA")
    K.text(img, (60, 50), "REBEL_CELL  //  DISPATCH: the red fist and SYNC STRIKE, option A (design-language proposal)",
           K.F(K.MONO, 30), (240, 238, 232), "lm", 0.6)
    K.text(img, (60, 92), "Row 1: the red sequence (round 34's blackout reveal, then the spread). Row 2: option A, three "
           "stacked lanes in a section cut along a street of the real grid.", K.F(K.MONO, 18), (170, 182, 200), "lm", 0.3)
    sheet = img.convert("RGB")
    reds = [("RS_1_before", "BEFORE: the fist barely hinted"), ("RS_2_blackout", "BLACKOUT: the ring + lines go dark"),
            ("RS_3_spreading", "SPREADING from the palm"), ("RS_4_full", "THE FULL FIST")]
    tw, th = 590, 332
    for k, (n, lab) in enumerate(reds):
        p = os.path.join(SCR, "RED_SHOTS", n + "_plate.png")
        x = 60 + k * (tw + 20)
        if os.path.exists(p):
            sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, 120))
        ImageDraw.Draw(sheet).rectangle([x - 2, 118, x + tw + 1, 121 + th], outline=RED, width=2)
        img = sheet.convert("RGBA")
        K.text(img, (x + 4, 120 + th + 22), "%d  %s" % (k + 1, lab), K.F(K.MONO, 19), (255, 200, 200), "lm", 0.4)
        sheet = img.convert("RGB")
    opts = [("OA_1_midrun", "MID-RUN: three operatives, three levels"), ("OA_2_switch", "THE KILL SWITCHES: one step"),
            ("OA_3_showdown", "SHOWDOWN: one enters, two park")]
    ow, oh = 790, 444
    for k, (n, lab) in enumerate(opts):
        p = os.path.join(SCR, "OPTION_SHOTS", n + ".png")
        x = 60 + k * (ow + 25)
        if os.path.exists(p):
            sheet.paste(Image.open(p).convert("RGB").resize((ow, oh), Image.LANCZOS), (x, 500))
        ImageDraw.Draw(sheet).rectangle([x - 2, 498, x + ow + 1, 501 + oh], outline=(90, 96, 110), width=2)
        img = sheet.convert("RGBA")
        K.text(img, (x + 4, 500 + oh + 22), lab, K.F(K.MONO, 19), (215, 225, 232), "lm", 0.4)
        sheet = img.convert("RGB")
    sheet = card(sheet, (60, 1000), (1220, 410), "SYNC STRIKE, OPTION A  (round 43 decision + the review; proposal)", [
        "Three operatives at once: BREAKER on the roofs, GHOST in the street, RIGGER in the service",
        "tunnel under it. Every step each moves one room. The three KILL SWITCHES (one column) must",
        "be thrown ON THE SAME STEP; a lone throw re-arms. DISPATCH counters a room: STALL +1;",
        "the roof and the tunnel have DETOURS (+1) to wait for it. Then ONE takes the shaft into",
        "DISPATCH; the other two PARK at their switches (support). Operative accents: pink / cyan /",
        "green on tokens and a thin edge by their wax; the route keeps its state colours.",
        "The section is cut along a street of the real block grid: the lots along it host the lanes."], RED)
    sheet = card(sheet, (1310, 1000), (1190, 410), "GDD QUESTIONS (for DECISIONS.md)", [
        "1 Turn order: all three choose at once (as drawn) or the turn rotates?",
        "2 HP / RAM: shared, or each operative its own (the stationed crew)?",
        "3 One operative dies before the switches: the strike fails, or two finish?",
        "4 The parked two in the showdown: what support (a buff, a card, absorbing hits)?",
        "5 Mirror combats (round 43, GDD M11): every elite, or one per lane?",
        "6 Decks: one, or one per operative (round 43 open question)?",
        "7 The countered room: from the player's most-used firmware (GDD 8.5)?"], (140, 200, 255))
    sheet.save(os.path.join(ROOT, "H_mechanic_states.png"))
    print("saved H_mechanic_states.png")


if __name__ == "__main__":
    main()
