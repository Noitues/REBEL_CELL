"""deck_viewer.png + deck_viewer_spinner.png: the loadout window (build: PARITY/fixes/CARDFACE_deck.jpg).

Media: ONE terminal window (the Cell's loadout). DECK tab: the hand's own C-C card faces (round 34 r31lib
card_sticker, the face the build exports) stuck on the white liner sheet #F7F7F2 with kiss-cut slot outlines,
like the loot sheet (cards are stickers on a sheet). The focused card lifts with the peel curl (ruling 3) and
shows its empty kiss-cut slot; it carries the one scheduled sweep. The card detail is a column of the same
terminal: notes as tooltip glyph rows (26 px glyph tile + Plex). SPINNER tab: the locked D4 player wheel
(round 41 combat_typical_v4, cropped, never redrawn) at combat size on a dimmed pool of the city, with its
slices as glyph rows.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import b44 as K  # noqa: E402

U, SL, R = K.U, K.SL, K.R
P = (90, 130, 1830, 1000)

JOLT = dict(name='Jolt', kind='WHEEL', art='picto_spin', pic='picto_spin', val='3', text='Spin a wheel 3 ticks.', rar='Common', cost=1)
BRUTE = dict(name='Brute Spin', kind='WHEEL', art='picto_spin', pic='picto_spin', val='6', text='Spin a wheel 6 ticks.', rar='Common', cost=2)
FINE = dict(name='Fine Tune', kind='WHEEL', art='picto_nudge', pic='picto_nudge', val='2', text='Two +/-1 nudges on one ring.', rar='Common', cost=1)
MIRROR = dict(name='Mirror Flip', kind='WHEEL', art='picto_flip', pic='picto_flip', val='', text='Flip a wheel. Blocked while the target has resistance.', rar='Uncommon', cost=3)
OVER = dict(name='Overdrive', kind='HACK', art='status_overclocked', pic='status_overclocked', val='',
            text='OVERCLOCK your slice under the pointer: 1.5x, then CORRUPTED.', rar='Uncommon', cost=1)
DECK = [JOLT, JOLT, JOLT, JOLT, BRUTE, BRUTE, FINE, FINE, MIRROR, OVER]


def window(img, tab):
    img = K.darken(img, P, 0.45, 50)
    img = U.term_panel(img, P, 'LOADOUT  //  BREAKER 1  //  %s' % ('DECK  //  10 CARDS' if tab == 0 else 'SPINNER  //  6 SLICES'),
                       accent=U.PINK, seed=49, alpha=236, glow=0.45)
    img, _ = U.tabs(img, (120, 176), ['DECK', 'SPINNER', 'NEXT OPERATIVE  >'], tab, accent=U.PINK)
    U.text(img, (1800, 196), '[LB] [RB] tab', U.F(U.MONO, 16), (180, 140, 170), 'rm', 0.8)
    return img


def note_rows(img, x, y, rows, w=440):
    for gl, col, txt in rows:
        img = K.glyph_tile(img, x, y, gl, col)
        lines, cur = [], ''
        f = U.F(U.PLEX, 19)
        for word in txt.split():
            t = (cur + ' ' + word).strip()
            if f.getlength(t) > w and cur:
                lines.append(cur)
                cur = word
            else:
                cur = t
        lines.append(cur)
        for k, ln in enumerate(lines):
            U.text(img, (x + 52, y + 12 + k * 25), ln, f, (220, 226, 236), 'lm')
        y += max(48, 12 + len(lines) * 25 + 14)
    return img, y


def deck():
    img = K.city_backdrop()
    img = window(img, 0)
    # ---------------------------------------------- the liner sheet
    L = (120, 240, 1300, 966)
    lm = U.rect_mask(img.size, L, r=12)
    img = U.shadow(img, lm, (6, 10), 12, 0.6)
    img = U.over(img, K.LINER, lm)
    U.text(img, (L[0] + 22, L[1] + 24), 'LOADOUT SHEET  //  BREAKER 1  //  10 STICKERS', U.F(U.MONO, 16), (80, 80, 86), 'lm', 1.6)
    U.text(img, (L[2] - 22, L[1] + 24), 'PEEL TO INSPECT', U.F(U.MONO, 16), (150, 150, 156), 'rm', 1.6)
    d = U.BD(img)
    for xx in range(L[0] + 20, L[2] - 20, 24):
        d.line([(xx, L[3] - 16), (xx + 12, L[3] - 16)], fill=(205, 205, 200, 255), width=1)
    cw, ch = 210, 280
    for k, c in enumerate(DECK):
        i, j = k % 5, k // 5
        cx = L[0] + 30 + i * 230 + cw / 2 + 8
        cy = L[1] + 76 + j * 312 + ch / 2 + 8
        # kiss-cut slot outline (stays when a card is peeled)
        d = U.BD(img)
        d.rounded_rectangle([cx - cw / 2 - 5, cy - ch / 2 - 4, cx + cw / 2 + 7, cy + ch / 2 + 6], 26, outline=(255, 255, 255, 220), width=2)
        d.rounded_rectangle([cx - cw / 2 - 6, cy - ch / 2 - 6, cx + cw / 2 + 6, cy + ch / 2 + 5], 26, outline=(168, 168, 172, 255), width=2)
        foc = k == 0
        sd = R.card_sticker(c, cw, ch, seed=10 + k)
        if foc:
            sd = K.rainbow_sweep(sd, pos=0.5)
            x0, y0, x1, y1 = sd['body'].getbbox()
            sd = SL.apply_curl(sd, corner='br', amount=40 * SL.SS / math.hypot((x1 - x0) / 2, (y1 - y0) / 2))
            img = R.place_sticker(img, sd, cx - 16, cy - 20, angle=-3.5, scale=1.04, hover=0.6)
        else:
            img = R.place_sticker(img, sd, cx, cy, angle=0.0)
    # ---------------------------------------------- card detail column (same terminal)
    X = 1336
    d = U.BD(img)
    d.line([(X - 14, 240), (X - 14, 966)], fill=U.PINK + (60,), width=1)
    img = K.section(img, X, 244, 'CARD DETAIL', col=U.PINK)
    sd = K.stk('JOLT', 58, ('grad', (255, 238, 96), (255, 182, 14)), seed=140)
    img = K.place(img, sd, X + K.bw(sd)[0] / 2 + 6, 316, angle=-2)
    U.text(img, (X + K.bw(sd)[0] + 34, 300), '1 RAM  //  WHEEL', U.F(U.MONO, 20), U.WHITE, 'lm', 1.2)
    U.text(img, (X + K.bw(sd)[0] + 34, 328), 'COMMON  //  4 in deck', U.F(U.MONO, 16), (180, 190, 206), 'lm', 1.0)
    rows = [('picto_spin', (255, 196, 40), 'SPIN 3: turns the wheel clockwise by 3 ticks (counter-clockwise when negative).'),
            ('picto_target', (255, 196, 40), 'WHEEL card: it turns, nudges or flips a wheel. Aim it at any wheel.'),
            ('picto_ram', U.CYAN, 'Costs 1 RAM from this turn\'s pool.'),
            ('picto_draw', (150, 160, 178), 'COMMON: one pip. Shops sell it; rewards offer it often.')]
    img, y = note_rows(img, X, 380, rows)
    d = U.BD(img)
    d.line([(X, y + 6), (1800, y + 6)], fill=U.PINK + (60,), width=1)
    img = K.section(img, X, y + 22, 'RAM CURVE', col=U.PINK)
    for k, (cost, n) in enumerate(((0, 0), (1, 7), (2, 2), (3, 1))):
        bx = X + 10 + k * 104
        by = y + 160
        d = U.BD(img)
        d.rectangle([bx, by - n * 14, bx + 60, by], fill=U.PINK + (200,))
        d.rectangle([bx, by - 7 * 14, bx + 60, by], outline=U.PINK + (70,), width=1)
        U.text(img, (bx + 30, by + 18), '%d RAM' % cost, U.F(U.MONO, 15), (200, 180, 196), 'mm', 0.6)
        U.text(img, (bx + 30, by - n * 14 - 14), str(n), U.F(U.MONO, 17), U.WHITE, 'mm')
    img = K.pad_hints(img, 1336, 1030, [('A', 'peel'), ('Y', 'codex'), ('B', 'close')])
    img = K.term_row(img, (100, 1012, 370, 1050), 'CLOSE', key='[Esc]', size=20, accent=U.PINK)
    K.save(img, 'deck_viewer.png')


def wheel_crop():
    src = Image.open(os.path.join(K.CONC, 'round41_wheel_stack', 'combat_typical_v4.png')).convert('RGBA')
    cx, cy, r = 480, 492, 264
    box = (cx - r - 10, cy - 330, cx + r + 10, cy + r + 10)
    c = src.crop(box)
    m = Image.new('L', c.size, 0)
    d = ImageDraw.Draw(m)
    ox, oy = cx - box[0], cy - box[1]
    d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=255)
    d.polygon([(ox - 34, oy - 330), (ox + 34, oy - 330), (ox + 34, oy - 200), (ox - 34, oy - 200)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    c.putalpha(m)
    return c, (ox, oy)


def spinner():
    img = K.city_backdrop(dim=0.62)
    img = window(img, 1)
    # dimmed pool: the window glass opens onto the dimmed city round the wheel (concept: world at ~55 %)
    W0 = (120, 240, 1110, 966)
    wc, (ox, oy) = wheel_crop()
    cx, cy = 600, 616
    world = K.city_backdrop(dim=0.5, blur=4, sat=0.8)
    wm = U.rect_mask(img.size, W0, r=10)
    world.putalpha(wm)
    img = Image.alpha_composite(img, world)
    pool = Image.new('L', img.size, 0)
    ImageDraw.Draw(pool).ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=120)
    img = U.over(img, (2, 2, 6), K.ImageChops.multiply(pool.filter(ImageFilter.GaussianBlur(70)), wm))
    e = K.ImageChops.subtract(wm, SL.erode(wm, 1))
    img = U.over(img, U.PINK, e, 0.5)
    full = Image.new('L', img.size, 0)
    full.paste(wc.split()[3], (int(cx - ox), int(cy - oy)))
    img = U.shadow(img, full, (10, 16), 18, 0.7)
    img = K.paste_at(img, wc, cx - ox, cy - oy)
    U.text(img, (W0[0] + 18, 958), 'D4 SPINNER  //  BREAKER CORE  //  combat size', U.F(U.MONO, 15), (190, 160, 186), 'lm', 1.2)
    # slice list (same terminal), glyph rows
    X = 1150
    d = U.BD(img)
    d.line([(X - 18, 240), (X - 18, 966)], fill=U.PINK + (60,), width=1)
    img = K.section(img, X, 244, 'SLICES  //  read clockwise from the needle', col=U.PINK)
    sl = [('slice_overflow', (255, 80, 120), 'OVERFLOW 12', 'CRIT: deals high damage at each pointer of the target wheel.'),
          ('slice_shim', U.PINK, 'SHIM 6', 'ATTACK: deals damage at each pointer of the target wheel.'),
          ('slice_infect', (200, 90, 255), 'INFECT 3', 'AFFLICT: a status or a drain on the target slice.'),
          ('slice_shim', U.PINK, 'SHIM 6  + PARASITE', 'A Citation feeds on it: half output until cleansed.'),
          ('slice_defrag', U.CYAN, 'DEFRAG 5', 'DEFEND: gain block. Block expires at the start of your next turn.'),
          ('slice_detour', (123, 224, 123), 'DETOUR 4', 'EVADE: cancels the next incoming SHIM or OVERFLOW.')]
    y = 290
    for gl, col, nm, desc in sl:
        img = K.glyph_tile(img, X, y, gl, col)
        U.text(img, (X + 52, y + 10), nm, U.F(U.PLEX_M, 21), U.WHITE, 'lm')
        U.text(img, (X + 52, y + 36), desc, U.F(U.PLEX, 17), (200, 206, 220), 'lm')
        y += 70
    d = U.BD(img)
    d.line([(X, y + 4), (1800, y + 4)], fill=U.PINK + (60,), width=1)
    img = K.section(img, X, y + 20, 'FIRMWARE  //  HUB', col=U.PINK)
    img = K.glyph_tile(img, X, y + 54, 'fw_overvolt', (212, 255, 120))
    U.text(img, (X + 52, y + 64), 'OVERVOLT  //  in the SHIM slice socket', U.F(U.PLEX_M, 20), U.WHITE, 'lm')
    U.text(img, (X + 52, y + 90), 'Socketed firmware: hover the socket for its rule.', U.F(U.PLEX, 17), (200, 206, 220), 'lm')
    img = K.glyph_tile(img, X, y + 124, 'hub_breaker_core', U.PINK)
    U.text(img, (X + 52, y + 134), 'BREAKER CORE', U.F(U.PLEX_M, 20), U.WHITE, 'lm')
    U.text(img, (X + 52, y + 160), 'Perfect landings resolve the slice twice.', U.F(U.PLEX, 17), (200, 206, 220), 'lm')
    img = K.pad_hints(img, 1336, 1030, [('Y', 'codex'), ('B', 'close')])
    img = K.term_row(img, (100, 1012, 370, 1050), 'CLOSE', key='[Esc]', size=20, accent=U.PINK)
    K.save(img, 'deck_viewer_spinner.png')


if __name__ == '__main__':
    deck()
    spinner()
