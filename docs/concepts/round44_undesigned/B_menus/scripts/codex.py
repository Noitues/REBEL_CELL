"""codex.png: the Codex as the Cell's own knowledge (build: MENUS.jpg codex, on paper = wrong medium, D11).

Media: CODEX = yellow title sticker; ONE terminal glass panel '> CODEX // WHAT THE CELL KNOWS' with the tab plates
(as built) and entries as glyph-tile rows (26 px glyph in a navy tile + Plex text, the tooltip row grammar).
The selected corp entry opens an intercepted HOLO card (hacked intel): crest, rule, bosses on file. Never paper.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import b44 as K  # noqa: E402

U, SL = K.U, K.SL
TABS1 = ['SLICES', 'STATUSES', 'CLASSES', 'CORPORATIONS', 'CARDS', 'FIRMWARE', 'DAEMONS']
TABS2 = ['RING SEGMENTS', 'ENEMIES', 'NODES', 'HOME SERVERS', 'DEFENCE', 'THREATS', 'LEXICON']
ENTRIES = [('solace', None, 'SOLACE BIOSYSTEMS', 'Care on a subscription. Doses drain your RAM.'),
           ('meridian', None, 'MERIDIAN FREIGHT SYSTEMS', 'Logistics. Priority Routing jumps the queue.'),
           ('halcyon', None, 'HALCYON CIVIC', 'The city office. Citations plant PARASITES.'),
           ('orbital', None, 'ORBITAL COMMONS', 'The sky net. Solar Flares overclock its slices.'),
           (None, 'special_citation', 'CITATION', 'Halcyon: a PARASITE on the slice it hits.'),
           (None, 'special_priority', 'PRIORITY ROUTING', 'Meridian: +4 SHIELD when it lands first.'),
           (None, 'special_solar_flare', 'SOLAR FLARE', 'Orbital: OVERCLOCKS the slice under its pointer.'),
           (None, 'special_dose', 'DOSE', 'Solace: CORRUPTS a slice and drains 1 RAM.')]
COLS = {'special_citation': U.CORP['halcyon'], 'special_priority': U.CORP['meridian'],
        'special_solar_flare': U.CORP['orbital'], 'special_dose': U.CORP['solace']}
BOSSES = [('hub_emergency_powers', 'THE CIVIC CORE', 'HQ BOSS', 'Emergency Powers: heals 4 and gains 4 block each turn unless the Hub is breached.'),
          ('hub_compliance_lock', 'CITY MANAGER', 'FINAL RACK', 'Resistance 2. Halcyon\'s local administrator.'),
          ('special_citation', 'ZONING BOARD', 'ELITE', 'Shields, heals and rezones its read head 2 ticks a turn.'),
          ('placeholder_shield', 'RIOT CONTROL', 'ELITE', 'Two readers, heavy block and a Citation for everyone.')]


def wrap(s, font, w):
    out, cur = [], ''
    for word in s.split():
        t = (cur + ' ' + word).strip()
        if font.getlength(t) > w and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    out.append(cur)
    return out


def main():
    img = K.city_backdrop()
    P = (100, 150, 1820, 990)
    img = K.darken(img, P, 0.45, 50)
    img = U.term_panel(img, P, 'CODEX  //  WHAT THE CELL KNOWS', tag='42 / 57 ENTRIES', seed=47, alpha=238, glow=0.45)
    t = K.stk('CODEX', 64, U.FILL_YELLOW, seed=93)
    img = K.place(img, t, 100 + K.sw(t)[0] / 2, 84, angle=-3)
    img, _ = U.tabs(img, (130, 196), TABS1, 3)
    img, _ = U.tabs(img, (130, 246), TABS2, -1, states={6: 'idle'})
    # ---------------------------------------------- entries: glyph-tile rows
    x0, y = 130, 318
    for k, (corp, gl, name, desc) in enumerate(ENTRIES):
        if k == 4:
            img = K.section(img, x0, y - 4, 'CORP RULES')
            y += 30
        col = U.CORP[corp] if corp else COLS[gl]
        sel = name == 'HALCYON CIVIC'
        box = (x0 - 6, y - 6, 930, y + 52)
        if sel:
            m = U.rect_mask(img.size, box, chamfer=8)
            img = U.over(img, U.CYAN, m, 0.12)
            e = K.ImageChops.subtract(m, SL.erode(m, 2))
            img = U.over(img, U.CYAN, e)
            img = U.focus_brackets(img, box, gap=4, ln=12)
            U.text(img, (x0 + 2, y + 23), '>', U.F(U.MONO, 22), U.LIME, 'lm')
        img = K.glyph_tile(img, x0 + 24, y + 4, gl, col, crest_corp=corp)
        U.text(img, (x0 + 76, y + 12), name, U.F(U.PLEX_M, 21), U.WHITE, 'lm')
        U.text(img, (x0 + 76, y + 36), desc, U.F(U.PLEX, 18), (176, 190, 208), 'lm')
        y += 64
    # ---------------------------------------------- the intercepted holo card
    HB = (980, 318, 1790, 930)
    img = K.darken(img, HB, 0.55, 20)
    img = U.holo_panel(img, HB, 'halcyon', title='INTERCEPTED  //  HALCYON CIVIC  //  PUBLIC WORKS FILE', seed=9)
    col = U.CORP['halcyon']
    lite = tuple(min(255, c + 80) for c in col)
    cr = K.crest('halcyon', 120, lite)
    gl = Image.new('L', img.size, 0)
    gl.paste(cr.split()[3], (1010, 372))
    img = U.add_glow(img, gl, col, 14, 0.9)
    img = K.paste_at(img, cr, 1010, 372)
    d = U.BD(img)
    d.ellipse([996, 358, 1144, 506], outline=col + (200,), width=2)
    U.text(img, (1170, 392), 'HALCYON CIVIC', U.F(U.BAHN, 40, 'Bold'), U.WHITE, 'lm', 1.2)
    U.text(img, (1172, 428), 'municipal services  //  32 Sites  //  HQ: the Civic Core', U.F(U.MONO, 17), lite, 'lm', 0.6)
    rule = 'House rule: Citations plant a PARASITE on your slices. A parasite feeds on the slice; it resolves at half output until cleansed.'
    yy = 470
    for ln in wrap(rule, U.F(U.PLEX, 20), 600):
        U.text(img, (1172, yy), ln, U.F(U.PLEX, 20), (230, 226, 255), 'lm')
        yy += 27
    d = U.BD(img)
    d.line([(1004, 556), (1766, 556)], fill=col + (140,), width=1)
    U.text(img, (1006, 578), 'BOSSES ON FILE', U.F(U.MONO, 16), lite, 'lm', 2.0)
    y = 608
    for gname, nm, role, desc in BOSSES:
        img = K.glyph_tile(img, 1006, y, gname, lite)
        U.text(img, (1058, y + 10), nm, U.F(U.PLEX_M, 20), U.WHITE, 'lm')
        U.text(img, (1058 + U.F(U.PLEX_M, 20).getlength(nm) + 14, y + 11), role, U.F(U.MONO, 14), U.CORP2['halcyon'], 'lm', 1.2)
        U.text(img, (1058, y + 34), desc, U.F(U.PLEX, 17), (200, 196, 236), 'lm')
        y += 66
    chip = (1006, 878, 1236, 908)
    d = U.BD(img)
    d.rectangle(chip, outline=(140, 255, 160, 255), width=2)
    U.text(img, (chip[0] + 12, 893), 'DECRYPTED   7F-A2', U.F(U.MONO, 16), (140, 255, 160), 'lm', 1.4)
    U.text(img, (1772, 893), 'seal cracked by GHOST, run 9', U.F(U.MONO, 14), lite, 'rm', 0.6)
    # ---------------------------------------------- footer
    img = K.term_row(img, (110, 1008, 380, 1048), 'BACK', key='[Esc]', size=20)
    U.text(img, (1350, 1028), '[LB] [RB] tab', U.F(U.MONO, 17), U.WHITE, 'lm', 0.8)
    img = K.pad_hints(img, 1540, 1028, [('A', 'open'), ('B', 'back')])
    K.save(img, 'codex.png')


if __name__ == '__main__':
    main()
