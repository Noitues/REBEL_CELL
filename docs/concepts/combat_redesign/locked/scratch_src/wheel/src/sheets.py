"""sheets: the grammar deliverables (line audit, time options, HP options, colour legend, wave compression)"""
import sys, os, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import bb_lib as B
import cv_lib
from cv_lib import L2, C, ppx
import gramlib as GL
from gramlib import *

E = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/explore/grammar/'
BASE10 = 'D:/rc_scratch/combat_redesign/locked/wheel/out/base_p1.png'
BG = (9, 13, 24)
PANEL = (16, 22, 38)
EDGE = (60, 190, 215)
TXT = (230, 238, 250)
MID = (160, 176, 200)
LOW = (110, 124, 148)
mono = lambda px: B.mono(px)
anton = lambda px: B.anton(px)


def plate(n):
    return Image.open(E + 'plate_%s.png' % n).convert('RGB')


def crop(im, cx, cy, w, h, s=1.0):
    c = im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)))
    return c.resize((int(w * s), int(h * s)), Image.LANCZOS)


def sheet(title, sub):
    im = Image.new('RGB', (1920, 1080), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 24), title, font=anton(40), fill=TXT)
    d.text((40, 76), sub, font=mono(17), fill=MID)
    return im, d


def box(d, xy, label=None, col=EDGE):
    d.rounded_rectangle(xy, radius=6, fill=PANEL, outline=col, width=2)
    if label:
        d.text((xy[0] + 10, xy[1] + 6), label, font=mono(15), fill=MID)


def put(im, c, x, y, d=None, label=None):
    im.paste(c, (int(x), int(y)))
    if d is not None:
        d.rectangle([x - 1, y - 1, x + c.width, y + c.height], outline=(70, 84, 110), width=1)
    if label and d is not None:
        d.text((x + 4, y + c.height + 3), label, font=mono(14), fill=MID)


def wrap(d, x, y, s, font, fill, width, lh=None):
    words = s.split()
    line = ''
    lh = lh or font.size + 4
    for w_ in words:
        t = (line + ' ' + w_).strip()
        if d.textlength(t, font=font) > width and line:
            d.text((x, y), line, font=font, fill=fill)
            y += lh
            line = w_
        else:
            line = t
    if line:
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


# ============================================================================================ 1. line audit
AUDIT = [
    ('+2 unit cell outline', 'white dashed 12/8', 'ring +2 cells: "lands in two turns"', 'L8 dotted ENAMEL at 50 percent value; +1 solid thin, NOW solid bold with glow', (185, 470, 230, 170)),
    ('+2 landing arc frame', 'white dashed 10/7', 'arc lands in two turns', 'L8 dotted frame (value 50 percent); +1 thin solid; NOW solid + END notch', (560, 70, 300, 120)),
    ('+1 / +2 threat trim on the tower rim', 'blue solid / white dashed 5/5', 'when the slice is hit', 'COLD thin solid / FAR dotted, all the HARM family, hot = glow', (560, 420, 220, 140)),
    ('gun tracers', 'cyan dashed 12/6', 'the tower shoots here', 'solid painted pink stroke with ink keyline (Player ink); idle stub = short stroke + open ring', (400, 630, 200, 160)),
    ('hollow growth chevrons', 'dashed V 8.5/5.5', 'one more hit still to grow', 'hollow V with a solid channel: no dash. Hollow is growth ONLY', (190, 480, 150, 150)),
    ('future wave arcs W4-W6', 'tape rings + orange tick bands', 'what enters later', 'three tickets in the top-left corner (queue) + one feed arrow', (800, 160, 280, 300)),
    ('tower HP: white slash', 'white 2 px slash on red', 'segment lost at END TURN', 'cross-hatch in the cause colour (red = enemy, indigo = soak, pink = us)', (540, 405, 260, 130)),
    ('HUD YOU row slash', 'white slash on red blocks', 'HP you lose at END TURN', 'same cross-hatch, 12x20 segments, groups of 5', (1230, 122, 330, 60)),
    ('enemy HP tray slash', 'white slash on red tick', 'HP the enemy loses (our shots)', 'pink cross-hatch (we do it), cream ticks kept', (535, 745, 200, 110)),
    ('token lane ring (+2)', 'six long dashes on the disc rim', 'unit is +2 deep', 'solid thin ENAMEL ring graded by time (no dash)', (216, 500, 120, 120)),
    ('ring outline colours', 'red / blue / white', 'lane depth NOW / +1 / +2', 'neutral ENAMEL graded by time: bright+glow / dimmer / dotted', (560, 720, 400, 220)),
    ('turn dots pill on arcs', 'white dots in a pill', 'turns until landing', 'one or two plain turn pips; NOW = END notch', (780, 175, 160, 100)),
]


def line_audit():
    a = Image.open(BASE10).convert('RGB')
    b = plate('base')
    im, d = sheet('LINE AUDIT  //  every dashed or dotted line on the p1 plate', 'left = E10 p1 (before)   right = grammar pass (after).  Dashed lines: none left.  Dotted = two or more turns away, and nothing else.')
    cw, ch = 170, 100
    colx = [40, 990]
    y0 = 118
    rh = 112
    for i, (nm, was, meant, now, (cx, cy, w, h)) in enumerate(AUDIT):
        col, row = divmod(i, 6)
        x = colx[col]
        y = y0 + row * (rh + 8)
        box(d, [x, y, x + 900, y + rh])
        d.ellipse([x + 8, y + 8, x + 34, y + 34], fill=(255, 61, 168))
        d.text((x + 21, y + 21), str(i + 1), font=anton(18), fill=(12, 10, 22), anchor='mm')
        ca = crop(a, cx, cy, w, h, min(cw / w, (ch - 4) / h))
        cb = crop(b, cx, cy, w, h, min(cw / w, (ch - 4) / h))
        put(im, ca, x + 44, y + 6, d)
        put(im, cb, x + 44 + cw + 10, y + 6, d)
        tx = x + 44 + 2 * cw + 24
        d.text((tx, y + 6), nm, font=anton(19), fill=TXT)
        d.text((tx, y + 32), 'WAS: ' + was + '  (' + meant + ')', font=mono(13), fill=(255, 150, 130))
        wrap(d, tx, y + 52, 'NOW: ' + now, mono(13), (150, 235, 160), 900 - (tx - x) - 12, 16)
    d.text((40, 1050), 'Also read as dashes and now grouped: HP ring (15 blocks, groups of 5), unit HP ticks (6 wide, 10 high, 3 gap), slice pips.  Banned: the hazard-tick band on the wave tape.  Kept dotted: +2 only.', font=mono(14), fill=LOW)
    im.convert('RGB').save(E + 'line_audit.jpg', quality=92)


# ============================================================================================ 2. time options
TIME = {
    'A': ('HEAT  (the plan)', 'The mark itself carries time: value, chroma, glow, contour.',
          ['THIS END TURN: full value, solid bold outline, glow, END notch (solid wedge).', '+1: 70 percent value / 45 percent chroma, thin solid line, no glow, ONE pip.', '+2: 50 percent value / 25 percent chroma, round-dot contour (L8), TWO pips.']),
    'B': ('DIAL', 'Contour is the same solid line everywhere (weight only); a fuse dial states the time.',
          ['Dial = pie on a ring: full disc = this END TURN, half = +1, quarter = +2.', 'Same value / chroma step-down as A, no glow, no dots.', 'Dial rides cell corners, landing-arc caps, ring tags.']),
    'C': ('FROST', 'Future rings sit behind frosted glass: blur, desaturate, lift.',
          ['Ring +1 and +2 and their landing arcs are frosted; the pane edge is a hairline at the NOW ring.', 'NOW is crisp. Contour is plain solid in all rings; weight steps only.', 'Reads by focus: what is blurred is not now.']),
}


def time_sheet(k):
    pl = plate('time_%s' % k if k != 'A' else 'base')
    nm, line, rules = TIME[k]
    im, d = sheet('TIME GRAMMAR  //  option %s  %s' % (k, nm), line)
    board = pl.crop((0, 0, 1070, 1080)).resize((700, 707), Image.LANCZOS)
    put(im, board, 40, 120, d, 'full board, 1920x1080 plate: plate_%s.png' % ('time_' + k if k != 'A' else 'base'))
    crops = [('NOW ring (0): outline, chevrons, notch', (535, 738, 180, 140)), ('rings +1 / +2: outline, pips, chevrons', (535, 835, 180, 140)), ('landing arcs, right side', (905, 745, 180, 140)),
             ('tower trim + HP ring', (560, 415, 180, 140)), ('ring tags NOW / +1 / +2', (650, 300, 180, 140)), ('token + cell corner (+2)', (215, 505, 180, 140))]
    x0, y0 = 780, 118
    for i, (lbl, (cx, cy, w, h)) in enumerate(crops):
        cc = crop(pl, cx, cy, w, h, 2.0)
        xx = x0 + (i % 3) * 372
        yy = y0 + (i // 3) * 300
        put(im, cc, xx, yy, d, lbl)
    yy = 735
    box(d, [780, yy, 1880, 980], 'rules')
    ty = yy + 34
    for r in rules:
        ty = wrap(d, 800, ty, '- ' + r, mono(16), TXT, 1060, 22) + 4
    ty += 8
    d.text((800, ty), 'Reads without colour: see time_compare_grey.jpg.   Tokens: HOT / COLD / FAR (VISUAL_PLAN C), lines L5 L8 L9.', font=mono(14), fill=MID)
    im.save(E + 'time_%s.jpg' % k, quality=92)


def time_compare():
    im, d = sheet('TIME GRAMMAR  //  the three options side by side, colour and greyscale', 'same state f1; board only; the greyscale row is the acceptance test (law 3)')
    for i, k in enumerate('ABC'):
        pl = plate('time_%s' % k if k != 'A' else 'base')
        bd = pl.crop((20, 20, 1050, 1060)).resize((600, 606), Image.LANCZOS)
        put(im, bd, 40 + i * 620, 120, d, 'option %s  %s' % (k, TIME[k][0]))
        g = bd.convert('L').convert('RGB')
        put(im, g.crop((0, 0, 600, 300)), 40 + i * 620, 750 if False else 760, d)
    im.save(E + 'time_compare_grey.jpg', quality=92)


# ============================================================================================ 3. HP
def hp_swatches(opt, k=6):
    """the whole HP vocabulary at 2x layer scale for one option; returns RGB image at 3x"""
    OPT = GL.OPT
    OPT['hp'] = opt
    Ls = L2()
    cols = [('current', 'lit'), ('lost, harm', 'harm'), ('lost, soak', 'soak'), ('lost, ours', 'ours'), ('+1 forecast', 'cold_harm'), ('mend', 'mend'), ('gone', 'gone')]
    kinds = [('tower ring 50x7', 50, 7, 2.6, 3.4), ('slice pip 38x8', 38, 8, 2.6, 3.4), ('enemy tick 18x8', 18, 8, 2.2, 3.4), ('HUD seg 12x20', 12, 20, 3.0, 3.8)]
    X0, Y0 = 40, 40
    for r_, (kn, w, h, rad, pitch) in enumerate(kinds):
        y = Y0 + r_ * 44
        for c_, (cn, st) in enumerate(cols):
            x = X0 + c_ * 70
            hh = h
            core = [(x + rad, y + rad), (x + w - rad, y + rad), (x + w - rad, y + hh - rad), (x + rad, y + hh - rad)]
            if kn.startswith('enemy'):
                stt = {'lit': 'enemy', 'harm': 'ours', 'soak': 'ours'}.get(st, st)
            else:
                stt = st
            if kn.startswith('enemy') and st in ('soak',):
                continue
            seg_shape(Ls, core, rad, stt, pitch=pitch, lw=1.25, opt=opt, glow=(h >= 7))
    return Ls.im.crop((60, 60, 1060, 400))


def hp_sheet(opt):
    names = {'A': 'CROSS-HATCH (the plan)', 'B': 'HAZARD STRIPE', 'C': 'DRAIN CORE'}
    descs = {'A': 'Two directions at 45 / 135 degrees, 5 px pitch (3.4 px on the 7 px tower ring), solid 2 px edge in the cause colour, glow 4 px: it goes at THIS END TURN.',
             'B': 'One direction, fat 45 degree stripes alternating cause colour and ink (caution tape), solid edge, no glow: reads from far away, loses the cell-mesh feel.',
             'C': 'No hatch: dark socket, solid cause-colour outline and a solid core bar that sits inside it (the segment is draining). Quietest, but looks like the +1 forecast at a glance.'}
    pl = plate('base' if opt == 'A' else 'hp_%s' % opt)
    im, d = sheet('HP GRAMMAR  //  pending damage option %s  %s' % (opt, names[opt]), '')
    wrap(d, 40, 78, descs[opt], mono(15), MID, 1840, 18)
    sw = hp_swatches(opt)
    bgp = Image.new('RGB', sw.size, (12, 16, 28))
    bgp.paste(sw, (0, 0), sw)
    put(im, bgp, 40, 150, d)
    d.text((40, 150 + bgp.height + 4), '2x: current | lost harm | lost soak | lost ours | +1 forecast | mend | gone;  rows: tower ring, slice pip, enemy tick, HUD seg', font=mono(13), fill=MID)
    # protection and shield states
    Lp = L2()
    x, y = 60, 60
    seg_shape(Lp, [(x + 3, y + 3), (x + 45, y + 3), (x + 45, y + 5), (x + 3, y + 5)], 3, 'lit')
    double_line(Lp, [(x - 6, y - 12), (x + 56, y - 12)], PINK, 2.4, 3.0)
    for i in range(4):
        hx, hy = x + 150 + i * 22, y + 4
        hp_ = hex_pts(hx, hy, 8)
        if i < 3:
            Lp.poly(hp_, fill=(20, 28, 40), outline=ENAMEL, w=1.8)
        else:
            Lp.poly(hp_, fill=SOCK, outline=SOCK_LINE, w=1.4)
    double_line(Lp, [(x + 138, y - 12), (x + 238, y - 12)], ENAMEL, 2.0, 3.0)
    for rr, c in ((0, STEEL_HI), (5, STEEL)):
        Lp.line([(x + 300, y - 6 + rr), (x + 360, y - 6 + rr)], INK, 4.4)
    for rr, c in ((0, STEEL_HI), (5, STEEL)):
        Lp.line([(x + 300, y - 6 + rr), (x + 360, y - 6 + rr)], c, 2.2)
    seg_shape(Lp, [(x + 303, y + 14), (x + 355, y + 14), (x + 355, y + 17), (x + 303, y + 17)], 3.5, 'enemy')
    pim = Lp.im.crop((30, 30, 760, 200))
    pbg = Image.new('RGB', pim.size, (12, 16, 28))
    pbg.paste(pim, (0, 0), pim)
    put(im, pbg, 40 + 0, 150 + bgp.height + 30, d)
    d.text((40, 150 + bgp.height + 30 + pbg.height + 4), 'blocked: lit segment behind a pink double-line plate (L10) | enemy shield: hex pips in a double bracket | armor: steel double-line cap over the tick row', font=mono(13), fill=MID)
    # in situ
    xs = 1010
    ins = [('tower ring + slice pips (3x)', (560, 405, 190, 120)), ('unit HP tray, pink = our shots (3x)', (535, 748, 170, 100)), ('HUD YOU row (3x)', (1240, 122, 240, 44))]
    yy = 150
    for lbl, (cx, cy, w, h) in ins:
        cc = crop(pl, cx, cy, w, h, 3)
        cc = cc.resize((min(cc.width, 870), int(cc.height * min(1, 870 / cc.width))))
        put(im, cc, xs, yy, d, lbl)
        yy += cc.height + 28
    # whole tower in situ
    tw = crop(pl, 535, 540, 340, 340, 1.0)
    put(im, tw, 40, 150 + bgp.height + 30 + pbg.height + 34, d, 'tower in situ (1x)')
    im.save(E + 'hp_%s.jpg' % opt, quality=92)


# ============================================================================================ 4. colour
LEG = [
    ('CELL_PINK', (255, 61, 168), 'ours: tower, guns, our damage', 'painted stroke'),
    ('HARM', (255, 68, 51), 'damage to you', 'chevron, diamond, red hatch'),
    ('GAIN', (123, 224, 123), 'your life: HP, pips, nothing through', 'segment, check, plus'),
    ('SOAK', (70, 78, 255), 'your soak choice', 'chevron notch, funnel'),
    ('PLAN', (255, 226, 0), 'your plan / preview', 'grease pencil'),
    ('SCHEDULE', (255, 140, 26), 'the rings move', 'bezel step cell'),
    ('BOSS_GOLD', (255, 196, 40), 'the Adjuster and its ward', 'diamond, lozenge'),
    ('NET_CYAN', (92, 225, 255), 'the terminal and RAM', 'HUD plate edge, RAM coin'),
    ('TRACE_VIOLET', (160, 60, 255), 'Trace', 'square'),
    ('CRT_AMBER', (255, 176, 0), 'Heat', 'flame'),
    ('RESIST_GOLD', (255, 210, 77), 'stars', 'star'),
    ('FOCUS', (212, 255, 0), 'keyboard / target focus', 'four corner brackets'),
]
OLD = [('red lane outline', (255, 68, 51), 'lands this turn', 'neutral ENAMEL, HOT (bright + glow)'),
       ('blue lane outline', (120, 170, 255), 'lands next turn', 'neutral ENAMEL, COLD'),
       ('white dashed lane outline', (236, 240, 255), 'lands in 2 turns', 'neutral ENAMEL dotted, FAR'),
       ('slice frames green / pink / teal / lime', (123, 224, 123), 'slice type', 'one pink frame; type = icon only'),
       ('cyan hub rim and code rings', (92, 225, 255), 'ours', 'pink rim (P paint); cyan = terminal only'),
       ('mauve unit washes', (137, 63, 108), 'enemy kinds', 'cool slate washes (player is pink now)'),
       ('teal enamel bezel', (50, 90, 86), 'nothing', 'gunmetal; orange only on schedule cells'),
       ('orange WAVES LEFT chip', (255, 140, 26), 'nothing', 'neutral enamel')]


def colour_sheets():
    im, d = sheet('OUTLINE COLOUR LEGEND  //  twelve meanings, everything else neutral', 'a colour is a cause or an owner. It always rides one shape, so no meaning rests on hue alone. No lane colours, no slice-type colours.')
    for i, (nm, c, mean, shape) in enumerate(LEG):
        col, row = divmod(i, 6)
        x = 40 + col * 470
        y = 120 + row * 78
        box(d, [x, y, x + 450, y + 68])
        d.rounded_rectangle([x + 10, y + 10, x + 58, y + 58], radius=6, fill=c, outline=(12, 10, 22), width=3)
        d.text((x + 70, y + 8), nm, font=mono(17), fill=TXT)
        d.text((x + 70, y + 30), mean, font=mono(13), fill=MID)
        d.text((x + 70, y + 47), 'shape: ' + shape, font=mono(12), fill=LOW)
    # neutral
    d.text((40, 600), 'NEUTRAL (no meaning):', font=mono(15), fill=MID)
    for i, c in enumerate([(217, 225, 234), (38, 43, 51), (92, 100, 114), (12, 10, 22), (242, 238, 228), (175, 192, 214), (150, 162, 182), (255, 244, 214)]):
        d.rounded_rectangle([280 + i * 50, 592, 320 + i * 50, 628], radius=4, fill=c, outline=(80, 90, 110))
    d.text((700, 598), 'ENAMEL, gunmetal, groove, INK, PAPER, TEXT, STEEL, CREAM', font=mono(13), fill=LOW)
    # old -> new
    box(d, [1000, 120, 1880, 620], 'WHAT EACH E10 OUTLINE COLOUR MEANT, AND WHAT IT IS NOW (note 5)')
    for i, (nm, c, was, now) in enumerate(OLD):
        y = 160 + i * 56
        d.rounded_rectangle([1016, y, 1052, y + 36], radius=5, fill=c, outline=(12, 10, 22), width=2)
        d.text((1064, y), nm + '  =  ' + was, font=mono(14), fill=(255, 170, 150))
        d.text((1064, y + 19), '-> ' + now, font=mono(14), fill=(150, 235, 160))
    # colour checks
    import wr2_lib as W
    d.text((40, 650), 'COLOUR-BLIND CHECK (dE76, min over deutan / protan / tritan; need >= 12):', font=mono(15), fill=TXT)
    pairs = [('CELL_PINK vs HARM', PINK, HARM), ('SOAK vs TRACE_VIOLET', SOAKC, (160, 60, 255)), ('CELL_PINK vs SOAK', PINK, SOAKC), ('GAIN vs FOCUS', GAIN, (212, 255, 0))]
    for i, (nm, a_, b_) in enumerate(pairs):
        v = [W.dE(W.sim_rgb(a_, k), W.sim_rgb(b_, k)) for k in ('deutan', 'protan', 'tritan')]
        ok = min(v) >= 12
        d.text((60, 680 + i * 26), '%-24s deutan %5.1f  protan %5.1f  tritan %5.1f   %s' % (nm, v[0], v[1], v[2], 'PASS' if ok else 'FAIL: pair by shape (chevron notch) or keep E10 #3A7EF3'), font=mono(15), fill=(150, 235, 160) if ok else (255, 150, 130))
    d.text((60, 790), 'Pink is not red: CELL_PINK sits 23 dE or more from HARM in all three sims, so the fallback #FF4FD0 is not needed.', font=mono(14), fill=MID)
    for i, (nm, c) in enumerate([('red hatch = enemy', HARM), ('indigo hatch = your soak', SOAKC), ('pink hatch = our hits', PINK)]):
        Ls = L2()
        seg_shape(Ls, [(60, 60), (150, 60), (150, 72), (60, 72)], 3, ['harm', 'soak', 'ours'][i], pitch=3.8, lw=1.25, glow=True)
        pim = Ls.im.crop((100, 100, 340, 180)).resize((360, 120), Image.LANCZOS)
        pb = Image.new('RGB', pim.size, (12, 16, 28))
        pb.paste(pim, (0, 0), pim)
        put(im, pb, 40 + i * 380, 830, d, nm)
    im.save(E + 'colour_legend.jpg', quality=92)

    # applied
    a = Image.open(BASE10).convert('RGB')
    b = plate('base')
    im, d = sheet('OUTLINE COLOURS  //  applied to the plate', 'left E10 p1, right the reduced set.  Same game state.  Ring depth is no longer a colour.')
    for i, (src, nm) in enumerate(((a, 'E10: red / blue / white dashed lanes, mauve units, teal bezel, cyan tower'), (b, 'grammar pass: ENAMEL by time, slate units, gunmetal bezel, pink tower'))):
        bd = src.crop((20, 20, 1050, 1060)).resize((900, 908), Image.LANCZOS)
        put(im, bd, 40 + i * 930, 130, d, nm)
    im.save(E + 'colour_applied.jpg', quality=92)


# ============================================================================================ 5. waves
def wave_sheets():
    a = Image.open(BASE10).convert('RGB')
    im, d = sheet('WAVE COMPRESSION PAST W3  //  E10 vs the two options', 'a wave has no sectors until it enters ring +2, so W4-W6 need kinds and widths only.  E10 spent three full rim rings (r 470-510).')
    lanes = [('E10: three outer arcs, W4 / W5 / W6', a, 'about 22 percent of the board'), ('A: queue tickets, top-left corner + feed arrow', plate('base'), 'corner only; rim free for landing arcs (now r 436 / 474)'), ('B: one rim lane, three plates + arrow', plate('wave_B'), 'a quarter of one ring')]
    for i, (nm, src, note) in enumerate(lanes):
        bd = src.crop((0, 0, 1070, 1080)).resize((600, 606), Image.LANCZOS)
        put(im, bd, 40 + i * 620, 120, d, nm)
        d.text((40 + i * 620, 760), note, font=mono(14), fill=MID)
    z = [crop(a, 760, 150, 360, 220, 1.6), crop(plate('base'), 150, 70, 300, 120, 2.0), crop(plate('wave_B'), 230, 120, 360, 200, 1.6)]
    for i, c in enumerate(z):
        c = c.resize((min(c.width, 590), int(c.height * min(1, 590 / c.width))))
        put(im, c, 40 + i * 620, 790, d)
    # area numbers
    ring_area = math.pi * (512 ** 2 - 470 ** 2)
    board_area = math.pi * 512 ** 2
    d.text((40, 1050), 'E10 arc band r 470-510 = %.0f percent of the board disc.  A uses 228 x 88 px in the corner (0 percent of the disc).  B uses a 31 deg strip of r 491-511.' % (100 * ring_area / board_area), font=mono(14), fill=LOW)
    im.save(E + 'waves_compare.jpg', quality=92)


if __name__ == '__main__':
    what = sys.argv[1:] or ['audit', 'time', 'hp', 'colour', 'waves']
    if 'audit' in what:
        line_audit()
    if 'time' in what:
        for k in 'ABC':
            time_sheet(k)
        time_compare()
    if 'hp' in what:
        for o in 'ABC':
            hp_sheet(o)
    if 'colour' in what:
        colour_sheets()
    if 'waves' in what:
        wave_sheets()
