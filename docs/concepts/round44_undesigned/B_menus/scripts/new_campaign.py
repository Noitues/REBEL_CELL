"""new_campaign.png: the new-campaign form (build: PARITY/fixes/NEWC.jpg) in our language.

Media: NEW CAMPAIGN = yellow screen-title sticker; START = the one sticker verb (pink, focus curl, the scheduled
sweep); TRUST NO ONE = a small ink sticker slogan (no pencil: it is a motto, not a plan); everything else is
ONE terminal panel: target / ICE / home server / crew tiles, the city seed, and TODAY'S RUN + SHARE CODES as
terminal rows. Selected tile = cyan edge + a SELECTED word (never a fill); the pad focus = lime brackets.
Corp tiles carry the corp crest on a small holo chip (intel on the target).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import ImageChops  # noqa: E402

import b44 as K  # noqa: E402

U, SL = K.U, K.SL

CORPS = [('solace', 'SOLACE', 'BIOSYSTEMS', 'best ICE 6', False),
         ('meridian', 'MERIDIAN', 'FREIGHT SYSTEMS', 'best ICE 4', False),
         ('halcyon', 'HALCYON', 'CIVIC', 'best ICE 2', False),
         ('orbital', 'ORBITAL', 'COMMONS', 'UNLOCK  160', True),
         (None, 'CLASSIFIED', 'opens at ICE 10', '', True)]
HOMES = [('STANDARD', 'home server', '', False),
         ('BUNKER', 'home server', 'UNLOCK  40', True),
         ('RELAY NEST', 'home server', 'UNLOCK  50', True),
         ('GHOST HOME', 'server', 'UNLOCK  60', True),
         ('FORTRESS', 'home server', 'UNLOCK  80', True)]
CREW = [('breaker', 'BREAKER', False), ('ghost', 'GHOST', False), ('hivemind', 'HIVEMIND', True),
        ('overclocker', 'OVERCLOCK', True), ('phantom', 'PHANTOM', True), ('wrecker', 'WRECKER', True),
        ('botnet', 'BOTNET', True), ('rigger', 'RIGGER', True)]


def tile_frame(img, box, selected=False, locked=False, focus=False):
    m = U.rect_mask(img.size, box, chamfer=8)
    img = U.over(img, (8, 16, 30), m, 0.92)
    e = ImageChops.subtract(m, SL.erode(m, 3 if selected else 1))
    if selected:
        img = U.add_glow(img, e, U.CYAN, 8, 0.7)
        img = U.over(img, U.CYAN, e)
    else:
        img = U.over(img, (90, 110, 130) if locked else U.CYAN, e, 0.35 if locked else 0.5)
    if locked:
        hatch = K.Image.new('L', img.size, 0)
        d = K.ImageDraw.Draw(hatch)
        x0, y0, x1, y1 = box
        for k in range(x0 - (y1 - y0), x1, 10):
            d.line([(k, y1), (k + (y1 - y0), y0)], fill=18, width=2)
        img = U.over(img, (150, 160, 180), ImageChops.multiply(hatch, m))
    if focus:
        img = U.focus_brackets(img, box, gap=6, ln=12)
    return img


def sel_tag(img, x, y):
    d = U.BD(img)
    f = U.F(U.MONO, 13)
    w = U.tw('SELECTED', f, 1.0) + 12
    d.rectangle([x - w, y, x, y + 18], fill=U.CYAN + (255,))
    U.text(img, (x - w / 2, y + 9), 'SELECTED', f, U.NAVY, 'mm', 1.0)
    return img


def lock(img, x, y, txt):
    img = K.paste_at(img, K.master('state_locked', 14, (130, 146, 166)), x, y - 7)
    U.text(img, (x + 20, y), txt, U.F(U.MONO, 14), (130, 146, 166), 'lm', 1.0)
    return img


def main():
    img = K.city_backdrop()
    P = (70, 150, 1850, 905)
    img = K.darken(img, (P[0] - 20, P[1] - 20, P[2] + 20, P[3] + 140), 0.45, 50)
    img = U.term_panel(img, P, 'NEW CAMPAIGN  //  [HQ] THE DECK IS WARM. JACK A CAMPAIGN IN.', seed=44, alpha=238, glow=0.45)
    LX = 100
    # -------------------------------------------------- TARGET
    img = K.section(img, LX, 202, 'TARGET', glyph='picto_target')
    tw_, th, gap = 228, 92, 12
    for k, (corp, a, b, c, locked) in enumerate(CORPS):
        x = LX + k * (tw_ + gap)
        box = (x, 232, x + tw_, 232 + th)
        img = tile_frame(img, box, selected=(k == 0), locked=(corp is None), focus=(k == 0))
        if corp:
            img = K.holo_chip(img, (x + 12, 244, x + 80, 312), corp, seed=k + 3)
        else:
            d = U.BD(img)
            d.rectangle([x + 12, 244, x + 80, 312], outline=(90, 104, 124, 255), width=1)
            U.text(img, (x + 46, 278), '?', U.F(U.ANTON, 40), (100, 114, 134), 'mm')
        tc = (150, 160, 178) if corp is None else U.WHITE
        U.text(img, (x + 92, 254), a, U.F(U.MONO, 20), tc, 'lm', 1.2)
        U.text(img, (x + 92, 278), b, U.F(U.MONO, 15), (170, 186, 206) if corp else (120, 132, 150), 'lm', 0.8)
        if locked and corp:
            img = lock(img, x + 92, 304, c)
        elif c:
            U.text(img, (x + 92, 304), c, U.F(U.MONO, 14), (120, 190, 220), 'lm', 0.8)
        if k == 0:
            img = sel_tag(img, x + tw_ - 10, 232 - 9)
    # -------------------------------------------------- ICE
    img = K.section(img, LX, 352, 'ICE DIFFICULTY  (0-13)', glyph='placeholder_storm')
    img = K.stepper(img, LX, 380, 0)
    U.text(img, (LX + 190, 400), 'ICE 0: the baseline rules.', U.F(U.PLEX, 21), (200, 210, 224), 'lm')
    U.text(img, (LX + 470, 400), 'each step adds one corp rule; ICE 1 opens after your first win', U.F(U.MONO, 15), (120, 146, 170), 'lm', 0.4)
    # -------------------------------------------------- HOME SERVER
    img = K.section(img, LX, 446, 'HOME SERVER', glyph='slice_firewall')
    hw, hh = 228, 66
    for k, (a, b, c, locked) in enumerate(HOMES):
        x = LX + k * (hw + gap)
        box = (x, 476, x + hw, 476 + hh)
        img = tile_frame(img, box, selected=(k == 0), locked=locked)
        U.text(img, (x + 16, 496), a, U.F(U.MONO, 20), U.WHITE if not locked else (170, 180, 196), 'lm', 1.2)
        if locked:
            img = lock(img, x + 16, 524, c)
        else:
            U.text(img, (x + 16, 524), b, U.F(U.MONO, 15), (170, 186, 206), 'lm', 0.8)
        if k == 0:
            img = sel_tag(img, x + hw - 10, 476 - 9)
    # -------------------------------------------------- CREW
    img = K.section(img, LX, 570, 'CREW', glyph='picto_hp')
    cw, ch = 134, 150
    for k, (cls, name, locked) in enumerate(CREW):
        x = LX + k * (cw + 7)
        box = (x, 600, x + cw, 600 + ch)
        img = tile_frame(img, box, selected=(k == 0), locked=locked)
        b = K.bust(cls, 92, grey=locked)
        img = K.paste_at(img, b.crop((0, 0, b.width, 96)), x + (cw - 92) / 2, 606)
        U.text(img, (x + cw / 2, 716), name, U.F(U.MONO, 16), U.WHITE if not locked else (150, 160, 178), 'mm', 1.0)
        if locked:
            img = lock(img, x + 24, 738, '60' if k < 6 else '80')
        else:
            U.text(img, (x + cw / 2, 738), 'class R1' if k else 'class R2', U.F(U.MONO, 13), (120, 190, 220), 'mm', 0.8)
        if k == 0:
            img = sel_tag(img, x + cw - 10, 600 - 9)
    # -------------------------------------------------- CITY SEED
    img = K.section(img, LX, 774, 'CITY SEED  (same seed, same city)')
    d = U.BD(img)
    d.rectangle([LX, 802, LX + 220, 842], fill=(4, 10, 20, 255), outline=U.CYAN + (140,), width=1)
    U.text(img, (LX + 14, 822), '20261006', U.F(U.MONO, 22), U.WHITE, 'lm', 2.0)
    img = U.term_button(img, (LX + 236, 802, LX + 436, 842), 'NEXT SEED', None, 'idle')
    U.text(img, (LX + 456, 822), 'the grid, Sites and links are rebuilt from the seed', U.F(U.MONO, 15), (120, 146, 170), 'lm', 0.4)
    # -------------------------------------------------- right column: TODAY'S RUN + SHARE CODES (terminal rows)
    RX = 1340
    d = U.BD(img)
    d.line([(RX - 26, 196), (RX - 26, 880)], fill=U.CYAN + (60,), width=1)
    img = K.section(img, RX, 202, "TODAY'S RUN  //  2026-10-06")
    rows = [('SEED', '20261006'), ('TARGET', 'Halcyon Civic'), ('ICE', '3'), ('HOME', 'Bunker home server'),
            ('CREW', 'Phantom'), ('MODIFIER', 'Heat +5 per Site cleared')]
    y = 244
    for a, b in rows:
        U.text(img, (RX + 4, y), '>', U.F(U.MONO, 18), (90, 140, 170), 'lm')
        U.text(img, (RX + 28, y), a, U.F(U.MONO, 18), (150, 176, 200), 'lm', 1.2)
        U.text(img, (RX + 160, y), b, U.F(U.MONO, 18), U.WHITE, 'lm', 0.6)
        y += 30
    img = K.term_row(img, (RX, y + 4, 1820, y + 48), 'PLAY TODAY\'S RUN', key='one try a day', size=20)
    y += 92
    img = K.section(img, RX, y, 'SHARE CODES')
    U.text(img, (RX, y + 38), 'A code holds a whole plan: target, ICE,', U.F(U.PLEX, 19), (190, 200, 214), 'lm')
    U.text(img, (RX, y + 62), 'city seed, home server and crew.', U.F(U.PLEX, 19), (190, 200, 214), 'lm')
    y += 88
    d = U.BD(img)
    d.rectangle([RX, y, 1820, y + 40], fill=(4, 10, 20, 255), outline=U.CYAN + (140,), width=1)
    U.text(img, (RX + 12, y + 20), 'RC1-solace-0-20261006-standard-breaker', U.F(U.MONO, 16), (200, 220, 236), 'lm', 0.2)
    y += 54
    img = K.term_row(img, (RX, y, 1820, y + 44), 'COPY THIS PLAN', key='[C]', size=20)
    img = K.term_row(img, (RX, y + 52, 1820, y + 96), 'START FROM A CODE', key='[V]', size=20)
    # -------------------------------------------------- stickers: title, slogan, START (the one verb)
    t = K.stk('NEW CAMPAIGN', 58, U.FILL_YELLOW, seed=81)
    img = K.place(img, t, 70 + K.sw(t)[0] / 2 + 6, 92, angle=-2)
    slog = K.stk('TRUST NO ONE', 30, K.FILL_WHITE, seed=82, border=9)
    img = K.place(img, slog, 70 + K.sw(t)[0] + K.sw(slog)[0] / 2 - 10, 110, angle=4)
    U.text(img, (1560, 952), 'Solace Biosystems  //  ICE 0  //  Standard home  //  Breaker', U.F(U.MONO, 18), U.CYAN, 'rm', 1.0)
    img = K.pad_hints(img, 100, 952, [('A', 'select'), ('B', 'back'), ('X', 'today\'s run')])
    st = K.stk('START', 92, U.FILL_PINK, seed=83, focus=True, sweep=True, curl_px=24)
    img = K.place(img, st, 1716, 968, angle=-3, focus=True)
    K.save(img, 'new_campaign.png')


if __name__ == '__main__':
    main()
