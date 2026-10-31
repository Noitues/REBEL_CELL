"""Round 31 -> event_screen.png (Terminal event: the story in the Cell's CRT terminal, a world-style feed,
choices as sticker buttons with outcome rows) and event_screen_memo.png (a corp memo, intercepted paper,
drives the event; shown after the pick, with the outcome confirmed on the page).

Text is the real content: content/events/ev_rescue_operative.tres and ev_continuum_memo.tres.

python event.py [main|memo|all]
"""
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round24_targets_hq", "target_solace_regular_night.png")
SOLACE = (61, 255, 139)


def plate_button(num, text, w=430, h=78, plate=(30, 26, 40), txt=(255, 255, 255), acc=L.YEL, seed=1, curl=None, hover=False):
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=12 * S, fill=plate + (255,))
    # number tab
    d.rounded_rectangle([0, 0, 64 * S, h * S - 1], radius=12 * S, fill=acc + (255,))
    d.rectangle([40 * S, 0, 64 * S, h * S - 1], fill=acc + (255,))
    d.text((32 * S, h * S / 2), str(num), font=L.font(L.ANTON, 46 * S), fill=L.INK + (255,), anchor="mm")
    f = L.font(L.ANTON, 40 * S)
    while f.getlength(text) > (w - 96) * S:
        f = L.font(L.ANTON, int(f.size * 0.93))
    d.text((82 * S, h * S / 2 + 1 * S), text, font=f, fill=txt + (255,), anchor="lm", stroke_width=2 * S, stroke_fill=L.INK + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    return L.sticker_from_art(im, border=6, curl=curl, gloss_k=0.6 if hover else 0.22, seed=seed)


def feed_panel(w, h, crop, label):
    src = Image.open(BG).convert("RGB").crop(crop).resize((w, h), Image.LANCZOS)
    src = ImageEnhance.Contrast(src).enhance(1.08)
    im = src.convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(20, 18, 26, 255), width=6)
    d.rectangle([12, 12, 190, 40], fill=(10, 10, 14, 220))
    d.ellipse([20, 20, 32, 32], fill=(255, 50, 60, 255))
    d.text((40, 26), label, font=L.f_mono(16), fill=(230, 230, 230, 255), anchor="lm")
    return im


def story_lines(text, width):
    return textwrap.wrap(text, width)


def main_event():
    img = L.backdrop(BG, blur=6, dim=0.42, sat=0.7)
    img = L.vignette(img, 0.7)
    # the Terminal (Cell's own system reading the corp node)
    T = (90, 120, 1330, 1000)
    tw, th = T[2] - T[0], T[3] - T[1]
    c = L.CRT(tw, th, SOLACE, "TERMINAL  //  SOLACE BIOSYSTEMS  //  NODE 4 OF 7", tag="EVENT", seed=31, alpha=242)
    feed = feed_panel(560, 380, (560, 300, 1360, 843), "CAM 04  MAINT. WARD")
    c.paste(feed, 30, 64)
    c.text((620, 66), "LOCKED WARD", 52, (230, 255, 236), fnt=L.f_num(60))
    c.text((622, 136), "STREET  //  terminal log, unsigned", 17, (110, 200, 140))
    c.rule(168, x0=620, x1=tw - 30, col=SOLACE, a=110)
    text = ("Behind the Terminal a maintenance ward is running on battery. Someone is in there: a runner Solace "
            "picked up two weeks ago and forgot to bill. They can still deck.")
    y = 188
    for ln in story_lines(text, 46):
        c.text((622, y), ln, 22, (200, 255, 214))
        y += 34
    c.d.rectangle([622 + L.f_mono(22).getlength(ln) + 6, y - 32, 622 + L.f_mono(22).getlength(ln) + 20, y - 8], fill=SOLACE + (255,))
    c.rule(470, col=SOLACE, a=80, dash=True)
    c.text((30, 484), "> CHOOSE", 18, (110, 200, 140))
    term = c.finish()
    img = L.crt_glow_under(img, T, SOLACE, 0.16)
    img = L.paste(img, term, T[0], T[1])
    # choices: sticker buttons + outcome rows (live medium chips)
    rows = [
        (1, "CUT THEM LOOSE", [("hp", "-12 HP", False), ("crew", "+1 BREAKER", True)], "the door bites"),
        (2, "PAY THE BILL", [("cycles", "-60", False), ("crew", "+1 BREAKER", True)], "wallet 160"),
        (3, "GHOST PAST", [("none", "NO CHANGE", True)], ""),
    ]
    by = 680
    for i, (n, t, out, note) in enumerate(rows):
        hov = (i == 1)
        sd = plate_button(n, t, plate=(30, 26, 40) if not hov else (60, 40, 70), seed=50 + i, hover=hov)
        x = 380 if not hov else 392
        img = L.place_sticker(img, sd, x, by + i * 100 - (8 if hov else 0), angle=[-1.2, 0.8, -0.5][i], hover=0.8 if hov else 0)
        orow = L.outcome_row(out, size=24)
        img = L.paste(img, orow, 640, by + i * 100 - orow.height // 2)
        if note:
            d = ImageDraw.Draw(img)
            d.text((660 + orow.width, by + i * 100), note, font=L.f_mono(17), fill=(110, 170, 130, 255), anchor="lm")
    # right column: who is here (crew effect) + run status
    rs = L.CRT(500, 210, L.CYAN, "RUN", tag="CELL-9 // BREAKER", seed=32)
    rs.paste(L.glyph("picto_hp", 26, fill=(255, 110, 140)), 24, 62)
    rs.text((64, 62), "HP", 22, (255, 140, 170))
    rs.text((476, 56), "41/60", 30, (255, 140, 170), anchor="ra", fnt=L.f_num(34))
    rs.paste(L.cycles_mark(26, L.CYCLE), 24, 110)
    rs.text((64, 110), "CYCLES", 22, L.CYCLE)
    rs.text((476, 104), "160", 30, L.CYCLE, anchor="ra", fnt=L.f_num(34))
    rs.paste(L.crew_mark(26, (230, 230, 240)), 24, 156)
    rs.text((64, 156), "CREW", 22, (230, 230, 240))
    rs.text((476, 150), "4", 30, (230, 230, 240), anchor="ra", fnt=L.f_num(34))
    img = L.paste(img, rs.finish(), 1380, 120)
    sd = L.sticker_word(["TERMINAL"], 64, fills=[(120, 255, 170)], seed=61)
    img = L.place_sticker(img, sd, 1640, 430, angle=4)
    # grease pencil: the slogan (placed once, art_asset) + a plan note on the feed
    p = L.pen(L.GP_YELLOW, seed=21)
    p.text("PLAY IT SAFE??", 1600, 600, 52, angle=-6)
    p.arrow([(1470, 650), (1300, 820), (1000, 880), (800, 880)], width=8, head=24)
    img = L.ink(img, p)
    pr = L.pen(L.GP_RED, seed=22)
    pr.circle(470, 400, 92, 70, width=9)
    pr.text("WARD", 610, 300, 34, angle=-8)
    img = L.ink(img, pr)
    img = L.bloom(img, 0.22, 0.78, 8)
    L.save(img, "event_screen.png")


def memo_doc(chosen=True):
    w, h = 760, 640
    im = L.paper(w, h, seed=14)
    d = ImageDraw.Draw(im)
    # Solace letterhead
    d.ellipse([40, 36, 104, 100], outline=(30, 140, 90, 255), width=4)
    d.line([(72, 48), (72, 88)], fill=(30, 140, 90, 255), width=8)
    d.line([(52, 68), (92, 68)], fill=(30, 140, 90, 255), width=8)
    d.text((124, 44), "SOLACE BIOSYSTEMS", font=L.font(L.ANTON, 36), fill=(30, 120, 80, 255))
    d.text((126, 88), "CONTINUUM CARE  //  PRICING COMMITTEE", font=L.font(L.TYPE, 16), fill=(70, 80, 76, 255))
    d.line([(40, 122), (w - 40, 122)], fill=(30, 120, 80, 255), width=3)
    d.text((40, 142), "INTERNAL MEMO: CONTINUUM PRICING", font=L.font(L.SERIF_B, 30), fill=L.PAPER_INK + (255,))
    d.text((40, 186), "TO: ALL TIER LEADS     FROM: RENEWALS     REF: CP-0418", font=L.font(L.TYPE, 16), fill=(80, 76, 84, 255))
    body = [
        "Renewal price uplift approved: +18% on all",
        "cardiac tiers.",
        "",
        "Churn model predicts 3.1% voluntary lapse.",
        "",
        "Involuntary lapse (bricking) to be reported as",
        "\"service interruption\".",
        "",
        "Do not forward.",
    ]
    y = 236
    for ln in body:
        d.text((40, y), ln, font=L.font(L.TYPE_B, 23), fill=(36, 32, 40, 255))
        y += 34
    for i in range(3):
        d.rectangle([40, 560 + i * 18, 40 + [520, 610, 380][i], 572 + i * 18], fill=(30, 28, 34, 255))
    st = L.stamp("DO NOT FORWARD", 34, angle=7, seed=5)
    im.alpha_composite(st, (w - st.width - 30, 470))
    return im


def memo_event():
    img = L.backdrop(BG, blur=6, dim=0.38, sat=0.6)
    img = L.vignette(img, 0.75)
    T = (90, 120, 1830, 1000)
    tw, th = T[2] - T[0], T[3] - T[1]
    c = L.CRT(tw, th, SOLACE, "TERMINAL  //  SOLACE BIOSYSTEMS  //  NODE 5 OF 7", tag="INTERCEPT", seed=33, alpha=238)
    c.text((960, 70), "INTERCEPTED  //  SOLACE INTERNAL MAIL  //  1 ATTACHMENT", 18, (110, 200, 140))
    c.text((960, 110), "CORPO", 46, (230, 255, 236), fnt=L.f_num(52))
    c.text((1080, 124), "speaker: Solace Biosystems", 17, (110, 200, 140))
    c.rule(170, x0=960, x1=tw - 30, col=SOLACE, a=110)
    c.text((960, 488), "> RESULT", 18, (110, 200, 140))
    y = 528
    for ln in story_lines("Someone will pay for this. Someone always does.", 40):
        c.text((960, y), ln, 26, (210, 255, 222))
        y += 38
    c.d.rectangle([960 + L.f_mono(26).getlength(ln) + 8, y - 36, 960 + L.f_mono(26).getlength(ln) + 24, y - 8], fill=SOLACE + (255,))
    term = c.finish()
    img = L.crt_glow_under(img, T, SOLACE, 0.14)
    img = L.paste(img, term, T[0], T[1])
    # the memo, paper on top of the terminal
    memo = L.rotate_rgba(memo_doc(), -3)
    img = L.drop_shadow(img, memo, 130, 190, blur=18, off=(14, 20), op=0.65)
    tp = L.tape(150, 38, angle=8, seed=2)
    img = L.paste(img, tp, 420, 172)
    # grease pencil notes on the memo (true to the text)
    pr = L.pen(L.GP_RED, seed=31)
    pr.circle(505, 630, 82, 24, width=8, start=-2.9, tilt=0.05)
    pr.text("THEY CALL IT AN INTERRUPTION", 560, 905, 30, angle=-3)
    img = L.ink(img, pr)
    py = L.pen(L.GP_YELLOW, seed=32)
    pts = [(350, 431), (520, 424)]
    py.stroke(SL.catmull(py.wobble([(474, 576), (506, 577), (540, 578)], 0.6), 8), width=7)
    img = L.ink(img, py)
    # choices, after the pick: chosen sticker stays lifted with the CHOSEN stamp, the other greys out
    rows = [(1, "COPY THE MEMO", [("heat", "+1 HEAT", False), ("cycles", "+20", True)]),
            (2, "LEAVE IT", [("none", "NO CHANGE", True)])]
    for i, (n, t, out) in enumerate(rows):
        sd = plate_button(n, t, w=400, seed=70 + i)
        if i == 1:
            sd = L.greyscale(sd, 0.7)
        img = L.place_sticker(img, sd, 1300, 350 + i * 92, angle=[-1, 0.6][i], opacity=1.0 if i == 0 else 0.55)
        orow = L.outcome_row(out, size=22)
        img = L.paste(img, orow, 1520, 350 + i * 92 - orow.height // 2)
    st = L.stamp("CHOSEN", 30, col=(255, 214, 64), angle=-10, seed=9)
    img = L.paste(img, st, 1700, 270)
    # confirmed outcome ticks into the run status
    d = ImageDraw.Draw(img)
    conf = L.outcome_row([("heat", "HEAT 52 > 53", False), ("cycles", "160 > 180", True)], size=26)
    img = L.paste(img, conf, 1052, 760)
    nxt = L.sticker_word(["CONTINUE"], 60, fills=["pink"], seed=72)
    img = L.place_sticker(img, nxt, 1640, 900, angle=-2)
    img = L.bloom(img, 0.2, 0.8, 8)
    L.save(img, "event_screen_memo.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("main", "all"):
        main_event()
    if what in ("memo", "all"):
        memo_event()
