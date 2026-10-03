"""typography.png: the round 31 type system, one row per medium, at true 1080p sizes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw  # noqa: E402

import ui31 as U  # noqa: E402

W, H = 1920, 1080
OUT = os.path.join(U.ROOT, 'typography.png')


def city_strip(box, seed=0):
    src = Image.open(os.path.join(U.SCR, 'city', 'f%02d.png' % (seed * 7 % 48)))
    x0, y0, x1, y1 = box
    crop = src.crop((200 + seed * 160, 300 + seed * 40, 200 + seed * 160 + (x1 - x0), 300 + seed * 40 + (y1 - y0)))
    return U.grade(crop, 0.45, 2.0, 0.9)


def row_frame(img, y, h, n, title, face, lic, col):
    d = U.BD(img)
    d.rectangle([24, y, W - 24, y + h], fill=(20, 18, 28, 255), outline=(44, 40, 58, 255))
    d.rectangle([24, y, 30, y + h], fill=col + (255,))
    U.text(img, (46, y + 14), n, U.F(U.MONO, 16), col, 'la', 1.2)
    sz = 34
    while U.tw(title, U.F(U.ANTON, sz), 0.8) > 340 and sz > 20:
        sz -= 1
    U.text(img, (46, y + 34 + (34 - sz) // 2), title, U.F(U.ANTON, sz), U.WHITE, 'la', 0.8)
    U.text(img, (46, y + 84), face, U.F(U.BAHN, 19, 'Bold'), (220, 216, 230), 'la', 0.4)
    yy = y + 110
    for line in lic:
        U.text(img, (46, yy), line, U.F(U.MONO, 15), (150, 150, 168), 'la', 0.5)
        yy += 19
    return img


def ladder(img, x, y, rows, face, col=U.WHITE, sample='Ag 0123', var=None):
    """rows: (token, px, use)."""
    yy = y
    for tok, px, use in rows:
        U.text(img, (x, yy + 2), tok, U.F(U.MONO, 15), (150, 150, 168), 'la', 0.4)
        if px:
            U.text(img, (x + 118, yy + 2), '%d px' % px, U.F(U.MONO, 15), U.WHITE, 'ra', 0.4)
        U.text(img, (x + 134, yy + 2), use, U.F(U.MONO, 15), (128, 128, 146), 'la', 0.3)
        yy += 21
    return img


def rules(img, x, y, lines, col=(205, 202, 214), w=440):
    yy = y
    for ln in lines:
        if ln.startswith('!'):
            U.text(img, (x, yy), ln[1:], U.F(U.PLEX_M, 18), U.HARM, 'la')
        else:
            U.text(img, (x, yy), ln, U.F(U.PLEX, 18), col, 'la')
        yy += 23
    return img


def main():
    img = U.canvas(W, H, (11, 10, 16))
    U.header_bar(img, 'TYPE SYSTEM  -  one face per medium',
                 'All sizes are true pixels at 1920x1080 (= UiTheme step @1280x720 x 1.5) and scale with Settings text scale 1.0 / 1.3 / 1.6. '
                 'Stickers scale as whole objects.')
    RH, Y0, G = 182, 104, 8
    X_SPEC, X_LAD, X_RULE = 400, 1010, 1440
    # ---------------- 1 DISPLAY / STICKER
    y = Y0
    img = row_frame(img, y, RH, '01  STICKER / DISPLAY', 'ANTON', 'Anton Regular  (keyline + extrude)',
                    ['OFL 1.1, in repo: assets/fonts/', 'Anton-Regular.ttf  (MSDF import)'], U.PINK)
    img.alpha_composite(city_strip((0, 0, 590, RH - 16), 1), (X_SPEC, y + 8))
    s1 = U.sticker('JACK IN', 92, U.FILL_PINK, seed=31)
    img = U.place(img, s1, X_SPEC + 170, y + 92, angle=3)
    s2 = U.sticker('RAID SETUP', 54, U.FILL_YELLOW, seed=12)
    img = U.place(img, s2, X_SPEC + 450, y + 62, angle=-2)
    U.live_number(img, (X_SPEC + 330, y + 146), '41/60', 64, U.GREEN)
    U.text(img, (X_SPEC + 470, y + 160), '<- live', U.F(U.MONO, 14), (170, 170, 186), 'lm', 0.5)
    ladder(img, X_LAD, y + 14, [('HERO', 144, 'verbs: SEND IT, JACK IN'), ('HERO-', 96, 'screen-title sticker'),
                                ('DISPLAY', 66, 'stamps, verdicts, Heat no.'), ('HEADING', 45, 'HP, slice values'),
                                ('MIN', 36, 'sticker word floor'), ('MIN #', 30, 'bare number floor'),
                                ('TRACK', 0, '+2 % caps; -1 in stickers')], 'anton')
    rules(img, X_RULE, y + 14, ['Stickers: words that never change.',
                                'Titles, primary verbs, card names,',
                                'node types. 5 px ink keyline, 7 px',
                                'extrude, white die-cut, gloss 0.22.',
                                'Bare Anton (no vinyl) = live numbers',
                                'with a 2 px dark rim + soft glow.',
                                '!Never a sticker for a changing value.'])
    # ---------------- 2 TERMINAL
    y += RH + G
    img = row_frame(img, y, RH, '02  TERMINAL / SCREENS & DATA', 'SHARE TECH MONO', 'Share Tech Mono Regular',
                    ['OFL 1.1, in repo: assets/fonts/', 'ShareTechMono-Regular.ttf'], U.CYAN)
    img = U.term_panel(img, (X_SPEC, y + 10, X_SPEC + 590, y + RH - 10), 'YOUR NETWORK', tag='LIVE', seed=3)
    f = U.F(U.MONO, 22)
    U.text(img, (X_SPEC + 16, y + 62), 'FIREWALL RELAY', f, U.WHITE, 'la', 1.6)
    U.text(img, (X_SPEC + 300, y + 62), 'INT 30/30', f, U.CYAN, 'la', 1.0)
    U.text(img, (X_SPEC + 450, y + 62), 'HOLDS', f, U.GREEN, 'la', 1.6)
    U.text(img, (X_SPEC + 16, y + 92), 'VAULT TERMINAL', f, U.WHITE, 'la', 1.6)
    U.text(img, (X_SPEC + 300, y + 92), 'INT 06/20', f, U.CYAN, 'la', 1.0)
    U.text(img, (X_SPEC + 450, y + 92), 'DISABLED', f, U.AMBER, 'la', 1.0)
    U.text(img, (X_SPEC + 16, y + 122), 'turret 3 dmg  //  ice lock  //  station: GHOST R2', U.F(U.MONO, 18), (150, 176, 200), 'la', 0.6)
    U.text(img, (X_SPEC + 28, y + 144), 'RESPIN  4 RAM  [R]', U.F(U.MONO, 18), U.CYAN, 'la', 1.4)
    ladder(img, X_LAD, y + 14, [('TITLE', 33, 'panel titles (rare)'), ('LABEL', 27, 'buttons, row values'),
                                ('BODY', 22, 'rows, list text'), ('HEADER', 18, '"> PANEL" strips, CAPS'),
                                ('CAPTION', 18, 'key hints, legends (floor)'), ('TRACK', 0, '+8 % on CAPS labels'),
                                ('LINE', 0, '1.3 caption, 1.4 body')], 'mono')
    rules(img, X_RULE, y + 14, ['The Cell\'s own systems: panels,',
                                'menus, HUD numbers, logs, tooltips',
                                'heads, key hints, Speed/Skip.',
                                'White or cyan on navy glass (>= 9:1).',
                                'Status words carry their own colour',
                                '+ word (HOLDS / DISABLED / SEIZED).',
                                '!Never below 18 px. Never on paper.'])
    # ---------------- 3 PAPER
    y += RH + G
    img = row_frame(img, y, RH, '03  PAPER / CORP DOCUMENTS', 'TYPEWRITER + LETTERHEAD',
                    'Courier New  +  Bahnschrift Bold',
                    ['Windows system fonts: CONCEPT ONLY,', 'not redistributable. Ship: Courier', 'Prime (OFL) + Plex Sans Cond. Med.'], U.CORP['halcyon'])
    p = U.paper_tex(590, RH - 20, seed=8)
    d = U.BD(p)
    U.text(p, (18, 10), 'HALCYON CIVIC', U.F(U.BAHN, 26, 'Bold'), U.CORP['halcyon'], 'la', 1.0)
    U.text(p, (20, 42), 'COMPLIANCE DIVISION  //  WORK ORDER 58-HC-114', U.F(U.BAHN, 15, 'SemiBold'), (90, 86, 100), 'la', 1.4)
    d.line([(18, 64), (570, 64)], fill=U.CORP['halcyon'] + (255,), width=2)
    U.text(p, (18, 70), 'AFTER-ACTION REPORT', U.F(U.BAHN, 30, 'Bold Condensed'), U.INK, 'la', 0.5)
    U.text(p, (20, 110), 'SUBJECT ...... REBEL_CELL (cell 03)', U.F(U.COUR, 20), (40, 38, 44), 'la')
    U.text(p, (20, 134), 'OUTCOME ...... FAILED', U.F(U.COUR_B, 20), (40, 38, 44), 'la')
    st = U.rubber_stamp('CLASSIFIED', 34, (200, 30, 40), angle=8, seed=4)
    p = U.paste_rgba(p, st, (470, 132))
    img = U.paste_paper(img, p, (X_SPEC, y + 10), angle=0, sh=0.5)
    ladder(img, X_LAD, y + 14, [('LETTER', 30, 'corp name, letterhead'), ('HEAD', 34, 'doc title (cond. bold)'),
                                ('BODY', 20, 'typewriter fields'), ('META', 15, 'refs, case nos. (floor 15:'),
                                ('', 0, '  meta only, never a rule)'), ('STAMP', 34, 'CLASSIFIED, CASE CLOSED'),
                                ('INK', 0, '#28262C on #F2EEE4, 13:1')], 'paper')
    rules(img, X_RULE, y + 14, ['Corp artifacts the Cell intercepted:',
                                'work orders, after-action reports,',
                                'audit dossiers, citations.',
                                'Letterhead in the corp colour; body',
                                'ink black; stamps red or corp ink.',
                                'Readable fields >= 20 px typewriter.',
                                '!Never the Cell\'s own UI.'])
    # ---------------- 4 GREASE PENCIL
    y += RH + G
    img = row_frame(img, y, RH, '04  GREASE PENCIL / PLANS & THREATS', 'PERMANENT MARKER',
                    'Permanent Marker Regular (as wax)',
                    ['Apache 2.0, in repo: assets/fonts/', 'PermanentMarker-Regular.ttf'], U.PEN_Y)
    img.alpha_composite(city_strip((0, 0, 590, RH - 16), 2), (X_SPEC, y + 8))
    pen = U.Pencil(img.size, U.PEN_Y, seed=4)
    pen.text('1. BREACH', X_SPEC + 120, y + 44, 34, angle=2)
    pen.text('2. DISABLE', X_SPEC + 140, y + 92, 34, angle=1)
    pen.text('3. EXFIL', X_SPEC + 118, y + 140, 34, angle=3)
    pen.circle(X_SPEC + 400, y + 92, 80, 44, width=7)
    img = pen.ink(img)
    pr = U.Pencil(img.size, U.PEN_R, seed=5)
    pr.text('RIP', X_SPEC + 400, y + 92, 40, angle=-4)
    pr.arrow([(X_SPEC + 560, y + 40), (X_SPEC + 520, y + 64), (X_SPEC + 488, y + 82)], width=7, head=18)
    img = pr.ink(img)
    ladder(img, X_LAD, y + 14, [('NOTE', 48, 'big plan words'), ('LABEL', 34, 'route letters, marks'),
                                ('SMALL', 28, 'short notes'), ('MIN', 26, 'floor (wax eats counters)'),
                                ('STROKE', 7, 'line width, px'), ('SHADOW', 0, '2/3 px dark under-shadow'),
                                ('COLOUR', 0, 'yellow #FFD60A, red #EC2228')], 'pencil')
    rules(img, X_RULE, y + 14, ['The Cell\'s plans on top of the world:',
                                'yellow = our plan / valid; red =',
                                'threat / invalid / loss. Opaque wax.',
                                'Short words only, always true to the',
                                'rules (routes, targets, TAKEN, RIP).',
                                '!No jokes that lie about the state.',
                                '!No live numbers, no body text.'])
    # ---------------- 5 BODY / TOOLTIP
    y += RH + G
    img = row_frame(img, y, RH - 10, '05  BODY / TOOLTIP', 'IBM PLEX SANS CONDENSED', 'Plex Sans Cond. Regular + Medium',
                    ['OFL 1.1, in repo: assets/fonts/', 'IBMPlexSansCondensed-*.ttf'], U.WHITE)
    img = U.term_panel(img, (X_SPEC, y + 10, X_SPEC + 590, y + RH - 20), 'ZERO-DAY 12', tag='CRIT', tag_col=U.PINK, seed=9)
    img = U.paste_glyph(img, 'slice_zero_day', (X_SPEC + 34, y + 70), 34)
    U.text(img, (X_SPEC + 62, y + 58), 'Hits for 12. On a ', U.F(U.PLEX, 22), U.WHITE, 'la')
    x2 = X_SPEC + 62 + U.F(U.PLEX, 22).getlength('Hits for 12. On a ')
    U.text(img, (x2, y + 58), 'PERFECT', U.F(U.PLEX_M, 22), U.GOLD, 'la')
    x3 = x2 + U.F(U.PLEX_M, 22).getlength('PERFECT')
    U.text(img, (x3, y + 58), ' aim the ring doubles it.', U.F(U.PLEX, 22), U.WHITE, 'la')
    img = U.paste_glyph(img, 'picto_perfect', (X_SPEC + 34, y + 110), 30, U.GOLD)
    U.text(img, (X_SPEC + 62, y + 98), 'Breaker core: the slice resolves twice.', U.F(U.PLEX, 22), (200, 210, 226), 'la')
    U.text(img, (X_SPEC + 62, y + 132), '[RMB] inspect   [TAB] next target', U.F(U.MONO, 18), U.CYAN, 'la', 1.0)
    ladder(img, X_LAD, y + 14, [('BODY', 22, 'tooltips, codex, events'), ('EMPH', 22, 'Medium, never bold'),
                                ('SMALL', 20, 'floor for running text'), ('LINE', 0, '1.4 x size'),
                                ('MEASURE', 0, '36 - 60 characters'), ('PARA', 0, '> 3 lines -> this face')], 'body')
    rules(img, X_RULE, y + 14, ['Anything a player reads as prose:',
                                'tooltip bodies, codex, event text,',
                                'card detail. Mixed case, keywords',
                                'in Medium + their colour + glyph.',
                                'Sits inside terminal (Cell) or',
                                'holo/paper (corp) containers.'])
    # footer
    U.text(img, (30, H - 26), 'Hierarchy:  STICKER (static words) > bare ANTON (live numbers) > TERMINAL MONO (system) > PLEX (prose).  '
           'PAPER and PENCIL live only on their objects.  Translation: 30 % width slack per row; stickers re-cut per language.',
           U.F(U.MONO, 15), (150, 150, 168), 'la', 0.3)
    img.convert('RGB').save(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
