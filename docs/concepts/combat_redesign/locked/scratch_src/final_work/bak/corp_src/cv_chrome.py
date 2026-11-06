"""Bible chrome for the converged plates: header plate, YOU bill (HP result chips), NEXT forecast rows, Adjuster HP + range plate, terminal RAM/Trace,
CELL-9 sticker, SEND IT vinyl, UNDO chip, vinyl sticker cards with TOWER/WAVE bands. Every number is passed in from the sim dump."""
import sys
sys.dont_write_bytecode = True
from cv_lib import *

CARDS = {
    'Nudge': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 1', x='1', nm='NUDGE'),
    'Spin2': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 2', x='2', nm='SPIN 2'),
    'Spin3': dict(cost=1, fam='TOWER', g='PI_SPIN_CW', txt='Turn the tower 3', x='3', nm='SPIN 3'),
    'Firewall': dict(cost=2, fam='WAVE', g='BURN', txt='Burn 2 units, -4 HP', loud=2),
    'Pull': dict(cost=0, fam='WAVE', g='C_PULL', txt='Pull a unit or the Adjuster in', loud=1),
    'Twist': dict(cost=0, fam='WAVE', g='C_TWIST', txt='Whole wave turns 1 extra', loud=1),
}


def card_img(name, curl=False, liner=False):
    c = CARDS[name]
    Wc, Hc = 176, 236
    im = Image.new('RGBA', (Wc + 24, Hc + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox = oy = 12
    if liner:
        d.rounded_rectangle([ox, oy, ox + Wc, oy + Hc], radius=16, outline=(160, 175, 200, 200), width=3)
        g = glyph_rgba(c['g'], 54, 4, fill=(120, 130, 150))
        im.alpha_composite(g, (int(ox + Wc / 2 - g.width / 2), int(oy + Hc / 2 - g.height / 2)))
        d.text((ox + Wc / 2, oy + Hc / 2 + 50), 'PLAYED', font=mono(17), fill=(160, 175, 200, 255), anchor='mm')
        return im
    d.rounded_rectangle([ox, oy, ox + Wc, oy + Hc], radius=16, fill=(250, 250, 246, 255), outline=(20, 18, 28, 255), width=2)
    fam = CYAN if c['fam'] == 'TOWER' else ORANGE
    famd = tuple(int(v * 0.55) for v in fam)
    bx = [ox + 9, oy + 9, ox + Wc - 9, oy + Hc - 9]
    d.rounded_rectangle(bx, radius=10, fill=(16, 18, 30, 255))
    d.rectangle([bx[0], bx[1] + 34, bx[2], bx[1] + 128], fill=famd + (255,))
    for yy in range(bx[1] + 36, bx[1] + 128, 4):
        d.line([(bx[0], yy), (bx[2], yy)], fill=(0, 0, 0, 55))
    g = glyph_rgba(c['g'], 70, 5)
    im.alpha_composite(g, (int((bx[0] + bx[2]) / 2 - g.width / 2 - (20 if c.get('x') else 0)), int(bx[1] + 82 - g.height / 2)))
    if c.get('x') and NOW['words']:
        d.text(((bx[0] + bx[2]) / 2 + 40, bx[1] + 84), '×' + c['x'], font=anton(40), fill=(255, 255, 255, 255), anchor='mm', stroke_width=3, stroke_fill=(10, 8, 16, 255))
    if NOW['words']:
        d.text((bx[0] + 10, bx[1] + 148), c.get('nm', name.upper()), font=anton(28), fill=(255, 255, 255, 255), anchor='lm')
    d.rectangle([bx[0], bx[1] + 164, bx[2], bx[1] + 184], fill=fam + (255,))
    if NOW['words']:
        d.text(((bx[0] + bx[2]) / 2, bx[1] + 174), c['fam'], font=mono(16), fill=(12, 10, 22, 255), anchor='mm')
    words, lines, cur = c['txt'].split(), [], ''
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > 16:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + ' ' + wd).strip()
    lines.append(cur)
    for li, ln in enumerate(lines[:2] if NOW['words'] else []):
        d.text((bx[0] + 8, bx[1] + 196 + li * 17), ln, font=plex(16), fill=(235, 240, 250, 255), anchor='lm')
    d.ellipse([ox - 4, oy - 4, ox + 44, oy + 44], fill=(255, 214, 40, 255), outline=(20, 18, 28, 255), width=3)
    if NOW['words']:
        d.text((ox + 20, oy + 22), str(c['cost']), font=anton(30), fill=(20, 18, 28, 255), anchor='mm')
    if c.get('loud'):
        d.rounded_rectangle([ox + Wc - 66, oy + 4, ox + Wc - 6, oy + 34], radius=12, fill=(40, 10, 14, 255), outline=RED + (255,), width=2)
        g = glyph_rgba('X_EYE', 22, 2, fill=RED)
        im.alpha_composite(g, (int(ox + Wc - 52 - g.width / 2), int(oy + 19 - g.height / 2)))
        if NOW['words']:
            d.text((ox + Wc - 36, oy + 19), '+%d' % c['loud'], font=anton(22), fill=RED + (255,), anchor='lm')
    if curl:
        d.polygon([(ox + Wc - 34, oy + Hc), (ox + Wc, oy + Hc - 34), (ox + Wc, oy + Hc)], fill=(220, 224, 232, 255))
    return im


def hand(base, names, x0=985, hover=None, played=(), cy0=940):
    slots = [(nm, False) for nm in names] + [(nm, True) for nm in played]
    n = len(slots)
    step = 140 if n <= 5 else 120
    for i, (nm, liner) in enumerate(slots):
        ci = card_img(nm, liner=True) if liner else card_img(nm)
        ang = (i - (n - 1) / 2) * -3.5
        cx = x0 + 88 + i * step
        cy = cy0 + abs(i - (n - 1) / 2) * 5
        if hover == i and not liner:
            ci = card_img(nm, curl=True).resize((int(200 * 1.22), int(260 * 1.22)), Image.LANCZOS)
            cy = 890
        else:
            ci = ci.rotate(ang, resample=Image.BICUBIC, expand=True)
        shadow_paste(base, ci, (cx - ci.width / 2, cy - ci.height / 2), 0.5, 8, (4, 8))


def header(L, turn, adj_hp):
    terminal(L, (1010, 12, 1900, 84))
    L.text((1455, 36), 'TURN %d  |  SHIFTING WAVES' % turn, 32, 'anton', fill=WHITE)
    L.text((1455, 66), 'NETRUN // MERIDIAN FREIGHT // THE DEPOT // ADJUSTER %d HP' % adj_hp, 16, 'mono', fill=TXT_MID)


def you_block(L, y, hp, mx, thru, absorbed, slost, pencil=False):
    """bible 3.1: HP value + result chips in order [final] (absorbed) -other."""
    L.text((1012, y + 8), 'YOU  CELL-9', 18, 'mono', fill=CRT_TXT, anchor='lm')
    s = '%d/%d' % (hp, mx)
    L.text((1012, y + 56), s, 66, 'anton', fill=GREEN, anchor='lm', stroke=3, sf=(6, 16, 8))
    x = 1012 + L.tw(s, 66, 'anton') + 22
    if thru is None:
        return x
    b1 = chip(L, x, y + 30, '-%d' % thru if thru else '0', RED if thru else GREEN, 34, 52)
    b2 = chip(L, b1[2] + 10, y + 30, '(%d' % absorbed, CYAN, 34, 52, icon='X_HP', box=False, pad=2)
    L.text((b2[2] + 1, y + 57), ')', 34, 'anton', fill=CYAN, anchor='lm')
    b3 = chip(L, b2[2] + 20, y + 30, '-%d' % slost, RED, 34, 52, icon='X_HP', box=False, pad=2)
    if pencil:
        pts = [(1006, y + 92), (b3[2] + 6, y + 97)]
        L.line(pts, (6, 3, 8), 9)
        L.line(pts, YEL, 6)
    return b3[2]


def closing_line(L, y, txt):
    terminal(L, (1012, y, 1900, y + 30))
    L.text((1024, y + 15), txt, 17, 'mono', fill=CRT_TXT, anchor='lm')


def next_row(L, y, label, thru, absorbed, slost, col=YEL, strip=None, sel=False, note=None):
    """amendment 1: NEXT forecast chip row, same chip grammar as the HP bill; optional 6-cell sector strip (raw landing per sector)."""
    h = 54
    L.rect([1012, y, 1900, y + h], fill=(6, 10, 20, 235), outline=col if sel else (110, 120, 140), w=3 if sel else 2, r=8)
    L.text((1026, y + h / 2 + 1), label, 20, 'mono', fill=col, anchor='lm')
    x = 1026 + max(L.tw(label, 20, 'mono'), 110) + 10
    if strip is not None:
        for s in range(6):
            v = strip[s]
            bx = x + s * 50
            L.rect([bx, y + 6, bx + 46, y + h - 6], fill=(60, 14, 22) if v else (14, 18, 30), outline=RED if v else (60, 70, 90), w=2, r=5)
            L.text((bx + 23, y + 17), str(s), 16, 'mono', fill=TXT_MID if not v else (255, 190, 180), anchor='mm')
            L.text((bx + 23, y + 38), str(v) if v else '-', 22, 'anton', fill=WHITE if v else (90, 100, 120), anchor='mm')
        x += 6 * 50 + 12
    else:
        x += 20
    b1 = chip(L, x, y + 6, '-%d' % thru if thru else '0', RED if thru else GREEN, 28, 42)
    b2 = chip(L, b1[2] + 8, y + 6, '(%d' % absorbed, CYAN, 28, 42, icon='X_HP', box=False, pad=2)
    L.text((b2[2] + 1, y + 28), ')', 28, 'anton', fill=CYAN, anchor='lm')
    chip(L, b2[2] + 14, y + 6, '-%d' % slost, RED, 28, 42, icon='X_HP', box=False, pad=2)
    if note:
        L.text((1890, y + h / 2), note, 17, 'mono', fill=TXT_MID, anchor='rm')
    return y + h


def adjuster_block(L, y, hp, mx, dealt, in_range, strikes_next):
    L.text((1012, y + 8), 'ADJUSTER', 18, 'mono', fill=CRT_TXT, anchor='lm')
    s = '%d/%d' % (hp, mx)
    L.text((1012, y + 50), s, 56, 'anton', fill=GREEN, anchor='lm', stroke=3, sf=(6, 16, 8))
    x = 1012 + L.tw(s, 56, 'anton') + 20
    b = chip(L, x, y + 28, '-%d' % dealt if dealt else '0', RED if dealt else GREEN, 30, 46, icon='U_PACKET', icon_after=True)
    L.text((b[2] + 10, y + 52), 'to units', 17, 'mono', fill=TXT_MID, anchor='lm')
    terminal(L, (1012, y + 86, 1560, y + 124))
    labs = ['FAR', 'IN RANGE', 'STRIKES']
    xs = [1050, 1190, 1380]
    cur = 1 if in_range else 0
    for i, (lb, xx) in enumerate(zip(labs, xs)):
        on = i == cur
        L.text((xx, y + 105), lb, 17, 'mono', fill=(255, 255, 255) if on else (120, 140, 160), anchor='lm')
        if on:
            L.ellipse([xx - 22, y + 99, xx - 10, y + 111], fill=YEL, outline=INK, w=2)
    if strikes_next:
        L.text((1572, y + 105), 'strikes next turn', 17, 'mono', fill=AMBER, anchor='lm')
    return y + 124


def ram_trace(L, y, ram, ram_max, trace, trace_cap, heat):
    terminal(L, (1012, y, 1900, y + 100))
    L.text((1030, y + 24), 'RAM', 20, 'mono', fill=CRT_TXT, anchor='lm')
    for i in range(ram_max):
        bx = 1100 + i * 46
        on = i < ram
        L.rect([bx, y + 12, bx + 38, y + 36], fill=CYAN if on else (20, 34, 52), outline=CYAN, w=2, r=4)
    L.text((1030, y + 66), 'TRACE', 20, 'mono', fill=CRT_TXT, anchor='lm')
    for i in range(trace_cap):
        bx = 1108 + i * 42
        on = i < trace
        L.rect([bx, y + 54, bx + 34, y + 78], fill=RED if on else (28, 14, 18), outline=RED, w=2, r=4)
        if i == trace_cap - 1:
            for q in range(0, 34, 7):
                L.line([(bx + q, y + 78), (bx + q + 10, y + 54)], (255, 255, 255, 110), 2)
    L.text((1420, y + 22), 'FIGHT ENDS NOW', 18, 'mono', fill=AMBER, anchor='lm')
    L.text((1420, y + 48), '= %d HEAT' % heat, 24, 'mono', fill=AMBER, anchor='lm')
    L.text((1420, y + 82), '6 = LOCKDOWN -14 HP', 17, 'mono', fill=TXT_MID, anchor='lm')
    return y + 100


def stickers(base, L):
    st = vinyl('CELL-9 // BREAKER', 36, PINK, tilt=2)
    shadow_paste(base, st, (24, 944))
    se = vinyl('SEND IT', 62, PINK, tilt=-3, pad=(24, 6))
    shadow_paste(base, se, (1655, 968))
    terminal(L, (1740, 918, 1890, 958))
    L.text((1815, 938), 'UNDO [Z]', 18, 'mono', fill=CRT_TXT)
    L.text((1780, 1070), '> turn_resolve.exe', 16, 'mono', fill=TXT_MID)
