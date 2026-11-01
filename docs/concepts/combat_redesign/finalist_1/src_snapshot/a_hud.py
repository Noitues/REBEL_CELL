"""refund_token placements in the HUD (RAM row, option chips, chain strip): copies of build10 draws with the one shared token. tok = option key ('cur','A','B','C')"""
import sys
sys.dont_write_bytecode = True
import build10 as B10
from build10 import *
from a_kit import refund_token

SZ = dict(board=44, row=30, chip=26, strip=20)       # the fixed ladder


def token(L, cx, cy, where, tok):
    if tok == 'cur':
        return None
    refund_token(L, cx, cy, SZ[where], tok)


def ram_trace(L, f, y, tok='cur'):
    terminal(L, (X0 - 4, y, X1, y + 48))
    label(L, X0 + 12, y + 24, 'RAM', CRT_TXT, 16)
    for i in range(f['ram_max']):
        bx = X0 + 58 + i * 34
        L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)
        if f.get('refunds') and i == f['ram'] - 1 and i >= 0:
            if tok == 'cur':
                burst(L, bx + 14, y + 24, 20, 30, 12)
                L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN, outline=INK, w=2.4, r=4)
                L.line([(bx + 14, y + 17), (bx + 14, y + 31)], INK, 3.4)
                L.line([(bx + 7, y + 24), (bx + 21, y + 24)], INK, 3.4)
            else:
                # the refunded pip IS the token: it sits on the pip's own slot, the burst never reaches a neighbour
                L.rect([bx, y + 11, bx + 28, y + 37], fill=(20, 34, 52), outline=CYAN, w=2, r=4)
                token(L, bx + 14, y + 24, 'row', tok)
    label(L, X0 + 230, y + 24, 'TRACE', CRT_TXT, 16)
    for i in range(f['tcap']):
        bx = X0 + 292 + i * 32
        on = i < f['trace']
        L.rect([bx, y + 11, bx + 26, y + 37], fill=(160, 60, 255) if on else (28, 20, 44), outline=(160, 60, 255), w=2, r=4)
        if i == f['tcap'] - 1:
            for q in range(0, 26, 7):
                L.line([(bx + q, y + 37), (bx + q + 8, y + 11)], (255, 255, 255, 110), 2)
    label(L, X0 + 520, y + 24, 'ENDS = HEAT', AMBER, 16)
    seg_run(L, X0 + 640, y + 24, 'gold', f['pv']['trace_after'], 11, 18) if f['pv']['trace_after'] else None
    return y + 52


def option_chip(L, y, name, plan, soak, eq, sel=False, solid=True, refund=False, tok='cur'):
    h = 40
    L.rect([X0 - 4, y, X1, y + h], fill=(6, 10, 20, 235), outline=YEL if sel else (110, 120, 140), w=3 if sel else 2, r=8)
    x = X0 + 10
    for c in plan:
        g = ICON.get(c[0])
        if g:
            L.glyph(g, 20, (x + 10, y + 20), CREAM if c[0] == 'Brace' else (YEL if c[0] == 'Trigger' else CYAN))
            x += 26
    if soak:
        for dx in (0, 6):
            L.line([(x + dx - 3, y + 14), (x + dx + 4, y + 21), (x + dx - 3, y + 28)], INK, 6)
            L.line([(x + dx - 3, y + 14), (x + dx + 4, y + 21), (x + dx - 3, y + 28)], SOAK_C, 3.4)
        x += 18
    if refund:
        if tok == 'cur':
            burst(L, x + 12, y + 20, 7, 15, 9)
            L.rect([x + 28, y + 12, x + 46, y + 28], fill=CYAN, outline=INK, w=1.6, r=3)
            L.line([(x + 37, y + 15), (x + 37, y + 25)], INK, 2.6)
            L.line([(x + 32, y + 20), (x + 42, y + 20)], INK, 2.6)
            x += 54
        else:
            token(L, x + 16, y + 20, 'chip', tok)
            x += 40
    label(L, X0 + 190 if x < X0 + 185 else x + 8, y + 20, name, YEL if sel else WHITE, 16)
    x = X0 + 400
    x = seg_run(L, x, y + 20, 'through', eq['through'], 11, 20, pitch=13) if eq['through'] else x
    n_so, n_ab = eq['soaked'], eq['absorbed']
    xx = x + (6 if eq['through'] else 0)
    if n_so:
        xx = seg_run(L, xx, y + 20, 'soak', n_so, 11, 20, pitch=13) + 4
    if n_ab:
        seg_run(L, xx, y + 20, 'absorb', n_ab, 11, 20, pitch=13)
    L.text((X1 - 16, y + 20), '%d > %d' % (eq['lands'], eq['through']), 24, 'anton', fill=WHITE, anchor='rm', stroke=2)
    return y + h + 4


def chain_strip(L, f, y, tok='cur'):
    steps = f['chain']
    h = 24
    L.rect([X0 - 4, y, X1, y + 12 + len(steps) * h], fill=(8, 12, 22, 218), outline=(110, 120, 140), w=2, r=8)
    yy = y + 6
    for i, st in enumerate(steps):
        cy = yy + h / 2
        L.ellipse([X0 + 6, cy - 11, X0 + 28, cy + 11], fill=(10, 9, 16), outline=WHITE, w=2)
        L.text((X0 + 17, cy + 1), str(i + 1), 16, 'anton', fill=WHITE)
        L.glyph(st['glyph'], 20, (X0 + 50, cy), tuple(st['col']))
        L.text((X0 + 68, cy), st['name'], 16, 'mono', fill=tuple(st['col']), anchor='lm')
        x = X0 + 250
        for kind, n in st['pips']:
            if kind == 'txt':
                L.text((x, cy), n, 16, 'mono', fill=TXT_MID, anchor='lm')
                x += L.tw(n, 16, 'mono') + 10
            elif kind == 'refund':
                if tok == 'cur':
                    burst(L, x + 14, cy, 7, 14, 9)
                    L.rect([x + 30, cy - 9, x + 56, cy + 9], fill=CYAN, outline=INK, w=2, r=3)
                    L.line([(x + 43, cy - 5), (x + 43, cy + 5)], INK, 3)
                    L.line([(x + 38, cy), (x + 48, cy)], INK, 3)
                    x += 68
                else:
                    token(L, x + 14, cy, 'strip', tok)
                    x += 38
            elif n:
                x = seg_run(L, x, cy, kind, n, 10, 16) + 10
        yy += h
    return y + 12 + len(steps) * h + 4
