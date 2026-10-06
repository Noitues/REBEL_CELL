"""stats.png: Stats & achievements (build: PARITY/fixes/MENUS.jpg, stats rows).

Media: STATS = yellow title sticker; ONE terminal panel: stat tiles (glyph + bare Anton live number + mono label),
achievements as die-cut sticker badges on a white liner strip (they never change once earned: earned = glossy
vinyl, unearned = an empty kiss-cut outline in the liner), run history as terminal log rows (the Cell's records,
not paper receipts). An Anton outcome sticker appears only for FLATLINED and COMPLETED; JACKED OUT and
ABANDONED stay mono words. One badge (the newest) carries the scheduled sweep.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import b44 as K  # noqa: E402

U, SL = K.U, K.SL

TILES = [('picto_breach', '7', 'CAMPAIGNS STARTED', U.WHITE), ('picto_perfect', '2', 'CAMPAIGNS WON', U.GOLD),
         ('picto_take_dmg', '3', 'CAMPAIGNS LOST', U.HARM), ('picto_again', '61', 'RUNS COMPLETED', U.WHITE),
         ('picto_hp', '9', 'OPERATIVES LOST', U.HARM), ('placeholder_shield', '14 / 3', 'RAIDS HELD / FELL', U.CYAN),
         ('placeholder_storm', '6', 'BEST ICE', U.CYAN), ('picto_target', '212', 'PERFECT LANDINGS', U.GOLD),
         ('placeholder_vault', '38', 'RACKS CAPTURED', U.WHITE), ('picto_ram', '8 940', 'CYCLES EARNED', (120, 255, 200)),
         ('status_cleanse', '0', 'ASSISTED WINS', (150, 160, 178)), ('picto_draw', '5 / 10', 'ACHIEVEMENTS', U.PINK)]

BADGES = [('FIRST BLOOD', 'picto_take_dmg', ((255, 128, 204), (236, 28, 140)), True),
          ('BANKED', 'placeholder_vault', ((150, 240, 255), (40, 170, 230)), True),
          ('BREACH', 'picto_breach', ((255, 238, 96), (255, 170, 14)), True),
          ('CLEAN HANDS', 'status_cleanse', None, False),
          ('AVERAGE IS A LIE', 'picto_target', None, False),
          ('COLD STORAGE', 'state_frozen', ((190, 220, 255), (90, 130, 240)), True),
          ('PURGE SURVIVOR', 'placeholder_burn', None, False),
          ('THE WALL', 'placeholder_shield', ((150, 255, 170), (30, 190, 100)), True),
          ('PERFECTIONIST', 'picto_perfect', None, False),
          ('FINAL FINAL', 'placeholder_kill_process', None, False)]

RUNS = [('10-06', 'solace', 'T2  rack run', 'BREAKER', '+212', '40', 'COMPLETED'),
        ('10-05', 'solace', 'T2  intel run', 'GHOST', '+96', '0', 'FLATLINED'),
        ('10-04', 'solace', 'T1  rack run', 'BREAKER', '+140', '18', 'JACKED OUT'),
        ('10-02', 'halcyon', 'T1  rack run', 'PHANTOM', '+60', '0', 'ABANDONED'),
        ('09-28', 'meridian', 'T3  HQ run', 'WRECKER', '+388', '120', 'COMPLETED')]

FILL_RED = ('grad', (255, 120, 100), (222, 30, 44))
FILL_GREEN = ('grad', (150, 255, 180), (36, 196, 104))


def badge(name, gl, fill, seed, sweep=False):
    S = SL.SS
    r = 40 * S
    art = Image.new('RGBA', (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    c = art.width // 2
    m = Image.new('L', art.size, 0)
    ImageDraw.Draw(m).ellipse([c - r, c - r, c + r, c + r], fill=255)
    top, bot = fill
    g = Image.new('RGBA', art.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for y in range(art.height):
        k = y / art.height
        gd.line([(0, y), (art.width, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
    g.putalpha(m)
    key = SL.dilate(m, 5 * S)
    ink = Image.new('RGBA', art.size, (20, 17, 24, 0))
    ink.putalpha(key)
    art = Image.alpha_composite(art, ink)
    art = Image.alpha_composite(art, g)
    gs = int(r * 1.15)
    ga = K.master(gl, gs, (255, 255, 255)).split()[3]
    gk = Image.new('L', art.size, 0)
    gk.paste(ga, (c - gs // 2, c - gs // 2))
    art = SL.over(art, (20, 17, 24), SL.dilate(gk, 3 * S))
    art = SL.over(art, (255, 255, 255), gk)
    sd = SL.build_sticker(art, border=8, gloss_k=0.3, seed=seed)
    if sweep:
        sd = K.rainbow_sweep(sd, pos=0.46)
    return sd


def kiss_cut(img, cx, cy, r):
    """Unearned: the empty kiss-cut outline left in the liner (a faint cut line + a pale shadowed groove)."""
    d = K.U.BD(img)
    d.ellipse([cx - r + 1, cy - r + 2, cx + r + 1, cy + r + 2], outline=(255, 255, 255, 200), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(150, 150, 156, 255), width=2)
    return img


def main():
    img = K.city_backdrop()
    P = (100, 150, 1820, 990)
    img = K.darken(img, P, 0.45, 50)
    img = U.term_panel(img, P, 'STATS  //  RECORDS  //  CELL-03', seed=46, alpha=236, glow=0.45)
    t = K.stk('STATS', 64, U.FILL_YELLOW, seed=92)
    img = K.place(img, t, 100 + K.sw(t)[0] / 2, 84, angle=-3)
    # ---------------------------------------------- stat tiles
    tw_, th = 271, 78
    for k, (gl, v, lab, col) in enumerate(TILES):
        x = 130 + (k % 6) * (tw_ + 7)
        y = 196 + (k // 6) * (th + 10)
        box = (x, y, x + tw_, y + th)
        img = U.term_panel(img, box, None, accent=U.CYAN, hexbg=False, chamfer=8, header=False, glow=0.0, alpha=200, scan=0.06)
        img = K.paste_at(img, K.master(gl, 26, col), x + 14, y + 14)
        U.live_number(img, (x + 52, y + 27), v, 34, col, 'lm', glow=0.35)
        U.text(img, (x + 16, y + 62), lab, U.F(U.MONO, 15), (150, 176, 200), 'lm', 1.2)
    # ---------------------------------------------- achievements on the liner
    img = K.section(img, 130, 386, 'ACHIEVEMENTS   5 / 10   //   stickers you keep')
    L = (130, 414, 1790, 618)
    lm = U.rect_mask(img.size, L, r=10)
    img = U.shadow(img, lm, (5, 8), 10, 0.55)
    img = U.over(img, K.LINER, lm)
    d = U.BD(img)
    for xx in range(L[0] + 16, L[2] - 16, 22):
        d.line([(xx, L[3] - 12), (xx + 10, L[3] - 12)], fill=(200, 200, 196, 255), width=1)
    U.text(img, (L[2] - 18, L[1] + 14), 'REBEL_CELL // MERIT SHEET', U.F(U.MONO, 13), (160, 160, 160), 'rm', 1.4)
    for k, (name, gl, fill, got) in enumerate(BADGES):
        cx = L[0] + 92 + k * 164
        cy = L[1] + 86
        if got:
            sd = badge(name, gl, fill, seed=200 + k, sweep=(name == 'THE WALL'))
            img = K.place(img, sd, cx, cy, angle=(-4, 3, -2, 0, 0, 5, 0, -3)[k % 8])
            tc = (30, 26, 34)
        else:
            img = kiss_cut(img, cx, cy, 52)
            tc = (150, 150, 156)
        U.text(img, (cx, L[1] + 172), name, U.F(U.MONO, 15), tc, 'mm', 0.6)
    # focus tip on the hovered empty badge (terminal tooltip: what it needs)
    fx = L[0] + 92 + 3 * 164
    img = U.focus_brackets(img, (fx - 60, L[1] + 26, fx + 60, L[1] + 186), gap=4, ln=12)
    tip = (fx - 40, L[3] + 10, fx + 420, L[3] + 58)
    img = U.term_panel(img, tip, None, hexbg=False, chamfer=8, header=False, glow=0.3, alpha=246)
    U.text(img, (tip[0] + 14, tip[1] + 24), 'CLEAN HANDS: win a campaign without losing an operative.', U.F(U.PLEX, 17), U.WHITE, 'lm')
    # ---------------------------------------------- run history (terminal log rows)
    img = K.section(img, 130, 650, 'RUN HISTORY   //   last 5 of 61')
    cols = [(150, 'DATE'), (292, 'TARGET'), (520, 'RUN'), (740, 'OPERATIVE'), (940, 'CYCLES'), (1080, 'BANKED'), (1240, 'OUTCOME')]
    for x, s in cols:
        U.text(img, (x, 692), s, U.F(U.MONO, 14), (110, 140, 170), 'lm', 1.6)
    d = U.BD(img)
    d.line([(140, 706), (1790, 706)], fill=U.CYAN + (70,), width=1)
    names = {'solace': 'SOLACE', 'halcyon': 'HALCYON', 'meridian': 'MERIDIAN'}
    for k, (dt, corp, run, op, cyc, bank, out) in enumerate(RUNS):
        y = 736 + k * 50
        if k % 2 == 0:
            d = U.BD(img)
            d.rectangle([140, y - 22, 1790, y + 22], fill=U.CYAN + (10,))
        U.text(img, (150, y), '2026-' + dt, U.F(U.MONO, 19), (170, 186, 206), 'lm', 0.6)
        img = K.paste_at(img, K.crest(corp, 22, U.CORP[corp]), 292, y - 11)
        U.text(img, (324, y), names[corp], U.F(U.MONO, 19), U.WHITE, 'lm', 1.0)
        U.text(img, (520, y), run, U.F(U.MONO, 19), U.WHITE, 'lm', 0.6)
        U.text(img, (740, y), op, U.F(U.MONO, 19), U.WHITE, 'lm', 1.0)
        U.text(img, (940, y), cyc, U.F(U.MONO, 19), (120, 255, 200), 'lm', 0.6)
        U.text(img, (1080, y), bank, U.F(U.MONO, 19), U.GOLD, 'lm', 0.6)
        if out in ('FLATLINED', 'COMPLETED'):
            sd = K.stk(out, 26, FILL_RED if out == 'FLATLINED' else FILL_GREEN, seed=300 + k, border=7, extrude=4, key_w=3)
            img = K.place(img, sd, 1312, y, angle=(-2 if k % 2 else 2))
        else:
            U.text(img, (1250, y), out, U.F(U.MONO, 19), (150, 160, 178), 'lm', 1.4)
        U.text(img, (1780, y), '> replay seed', U.F(U.MONO, 15), (90, 130, 160), 'rm', 0.6)
    img = K.term_row(img, (110, 1008, 380, 1048), 'BACK', key='[Esc]', size=20)
    img = K.pad_hints(img, 1500, 1028, [('B', 'back'), ('Y', 'replay seed')])
    K.save(img, 'stats.png')


if __name__ == '__main__':
    main()
