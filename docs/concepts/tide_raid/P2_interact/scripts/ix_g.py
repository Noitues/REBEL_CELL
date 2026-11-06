"""P1 boards: input map (06f), refusal reasons (02j), contact boards per sequence, squint + colour-blind strips.
python ix_g.py [inputmap reasons boards squint]"""
import sys, time, os
import numpy as np
from ix_lib import *
import cb

BD = OUTD + 'boards/'
SQ = OUTD + 'squint/'
os.makedirs(BD, exist_ok=True)
os.makedirs(SQ, exist_ok=True)


def f_inputmap():
    cv = Cv(np.zeros((H, W, 3), np.float32) + np.array([.035, .04, .11], np.float32))
    rows = [
        ('move', 'Move the focus (snaps to the best target in a cone)', [('stick', 'all'), ('dpad', 'UDLR')], [('key', 'W'), ('key', 'A'), ('key', 'S'), ('key', 'D')], [('mouse', '')], 'hover'),
        ('place', 'Pick up a card / place it / confirm', [('face', 'S')], [('key', 'Enter'), ('key', 'Space')], [('mouse', 'L')], 'click or drag-drop'),
        ('cancel', 'Cancel / drop back / undo the last placement', [('face', 'E')], [('key', 'Esc'), ('key', 'Bksp')], [('mouse', 'R')], 'right-click'),
        ('undo', 'Take a placed program back to the hand', [('face', 'W')], [('key', 'X')], [('mouse', 'L')], 'drag it off its Site'),
        ('forecast', 'Forecast / launch (a second press confirms)', [('face', 'N')], [('key', 'F')], [('mouse', 'L')], 'click the HOME tally'),
        ('cycle', 'Cycle the hand (tap, wraps)', [('shoulder', 'LB'), ('shoulder', 'RB')], [('key', 'Q'), ('key', 'E')], [('mouse', '')], 'wheel'),
        ('wheel', 'Card wheel (hold, release to pick up)', [('shoulder', 'LB')], [('key', 'R')], [('mouse', '')], 'hold middle'),
        ('pick', 'Walk the focus order / the valid targets', [('shoulder', 'LT'), ('shoulder', 'RT')], [('key', 'Tab'), ('key', 'Sh+Tab')], [], 'n/a'),
        ('hold', 'Pause / menu (when nothing is carried)', [('key', 'Menu')], [('key', 'Esc')], [], 'n/a'),
    ]
    y0, dy = 214, 92
    for i, (act, label, pad, kb, ms, mtxt) in enumerate(rows):
        y = y0 + i * dy
        ui.crt_chip(cv, 30, y - 36, 1890, y + 36, k=.35, r=10)
        act_glyph(cv, (80, y), {'move': 'pick', 'place': 'place', 'cancel': 'cancel', 'undo': 'undo', 'forecast': 'forecast', 'cycle': 'cycle', 'wheel': 'wheel',
                               'pick': 'cycle', 'hold': 'hold'}[act], r=24)
        x = 780
        for kind, arg in pad:
            wd = btn_w(kind, arg, 24)
            draw_btn(cv, (x + wd, y), kind, arg, r=24)
            x += 2 * wd + 16
        x = 1170
        for kind, arg in kb:
            wd = btn_w(kind, arg, 24)
            draw_btn(cv, (x + wd, y), kind, arg, r=24)
            x += 2 * wd + 16
        x = 1600
        for kind, arg in ms:
            wd = btn_w(kind, arg, 24)
            draw_btn(cv, (x + wd, y), kind, arg, r=24)
            x += 2 * wd + 16
    im = to_img(cv.out())
    d = ImageDraw.Draw(im)
    f1, f2, f3 = font(40, False, 800, 75), font(25, False, 600, 78), font(21, False, 560, 78)
    d.text((40, 30), '06f  INPUT MAP  ·  one set of verbs, three input families', font=f1, fill=(240, 243, 255))
    d.text((40, 84), 'glyph-first: the pill that follows the focus shows these glyphs; this table is the designer\'s key', font=f3, fill=(160, 170, 205))
    for x, t in ((780, 'PAD'), (1170, 'KEYBOARD'), (1600, 'MOUSE')):
        d.text((x, 150), t, font=font(30, False, 800, 75), fill=(127, 239, 255))
    for i, (act, label, pad, kb, ms, mtxt) in enumerate(rows):
        y = y0 + i * dy
        d.text((130, y - 14), label, font=f2, fill=(240, 243, 255))
        if mtxt != 'n/a' and not ms:
            pass
        d.text((1690 + 0, y - 12), '' if ms else '', font=f3, fill=(150, 160, 190))
    # mouse text notes under the glyphs
    for i, (act, label, pad, kb, ms, mtxt) in enumerate(rows):
        y = y0 + i * dy
        if mtxt != 'n/a':
            d.text((1670, y - 12), mtxt, font=f3, fill=(190, 198, 225))
    d.text((40, 1020), 'rules: (1) the stick is a direction, never a free pointer; (2) a carried card changes what LT/RT walk (valid targets only); (3) Esc never loses a placement,', font=f3, fill=(160, 170, 205))
    d.text((40, 1046), 'it only drops the carried card; (4) every verb exists on all three families, none needs a hold longer than 250 ms except the wheel.', font=f3, fill=(160, 170, 205))
    im.save(FRD + '06f_input_map.jpg', quality=93, subsampling=0)
    print('saved 06f')


def f_reasons():
    def crop(name, c, size=(620, 400)):
        im = Image.open(CLD + name + '.jpg').convert('RGB')
        x0 = int(c[0] - size[0] / 2)
        y0 = int(c[1] - size[1] / 2)
        x0 = max(0, min(W - size[0], x0))
        y0 = max(0, min(H - size[1], y0))
        return im.crop((x0, y0, x0 + size[0], y0 + size[1]))
    panels = [
        ('LEGAL  ·  MATCH', '02b_drag_over_match', (560, 480), 'lit pad in the type hue + the same glyph; preview shows', (60, 200, 140)),
        ('LEGAL, FLAGGED  ·  wrong type', '02c_drag_over_dud', (1137, 420), 'card glyph != beam glyph on a grey pad; no preview', (200, 200, 90)),
        ('LEGAL, FLAGGED  ·  already covered', '02i_drag_over_same', (630, 440), '"=" chip: a standing wall already answers it', (200, 200, 90)),
        ('LEGAL, FLAGGED  ·  hidden route only', '02a_drag_pickup', (1050, 400), 'fog "?" pad: only a sealed route crosses; type never leaked', (200, 200, 90)),
        ('REFUSED  ·  occupied', '02d_drag_over_occupied', (849, 480), 'red grease circle-slash on the program; tether goes red', (255, 60, 80)),
        ('REFUSED  ·  no beam / Site DOWN', '02h_drag_over_none', (600, 640), 'hollow grey ring cut by a slash; nothing lights', (255, 60, 80)),
        ('REFUSED  ·  2-guard limit', '02g_drag_limit', (1250, 880), 'both sockets turn red; every pad refuses', (255, 60, 80)),
    ]
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), '02j  WHY A DROP IS (NOT) ALLOWED  ·  seven reasons, shown without a word', font=font(34, False, 800, 75), fill=(240, 243, 255))
    fh, fc = font(24, False, 800, 75), font(20, False, 560, 78)
    for i, (t, fn, c, cap, col) in enumerate(panels):
        x, y = 24 + (i % 3) * 630, 70 + (i // 3) * 330
        if fn == '02g_drag_limit':
            im = Image.new('RGB', (610, 250))
            im.paste(crop(fn, (640, 500), (305, 250)), (0, 0))
            im.paste(crop(fn, (1300, 900), (305, 250)), (305, 0))
        else:
            im = crop(fn, c, (610, 250))
        sheet.paste(im, (x, y + 34))
        d.rounded_rectangle((x - 2, y + 32, x + 612, y + 286), 4, outline=col, width=3)
        d.text((x, y + 2), t, font=fh, fill=col)
        d.text((x, y + 290), cap, font=fc, fill=(190, 198, 225))
    # legend cell
    x, y = 24 + 1 * 630, 70 + 2 * 330
    d.text((x + 10, y + 8), 'one rule: lit = yes, grey = legal but flagged,', font=fh, fill=(240, 243, 255))
    d.text((x + 10, y + 40), 'red slash = refused. Never colour alone: shape + glyph', font=fc, fill=(190, 198, 225))
    d.text((x + 10, y + 70), 'carry the reason (!=, =, ?, slash, red sockets).', font=fc, fill=(190, 198, 225))
    sheet.save(BD + '02j_reasons_board.jpg', quality=93, subsampling=0)
    print('saved reasons')


def board(name, items, title, cols=3):
    rows = (len(items) + cols - 1) // cols
    cw, ch = W // cols, int(H / max(rows, 1))
    cw = 640
    ch = 360
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    d = ImageDraw.Draw(sheet)
    f = font(22, False, 800, 75)
    for i, (fn, lab) in enumerate(items):
        im = Image.open(fn).convert('RGB').resize((cw, ch), Image.LANCZOS)
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(im, (x, y))
        d.rounded_rectangle((x + 8, y + ch - 36, x + 8 + d.textlength(lab, font=f) + 20, y + ch - 8), 6, fill=(246, 241, 228))
        d.text((x + 18, y + ch - 33), lab, font=f, fill=(10, 10, 28))
        d.rectangle((x, y, x + cw - 1, y + ch - 1), outline=(8, 6, 20), width=2)
    sheet.save(BD + name + '.jpg', quality=92, subsampling=0)
    print('saved', name)


def f_boards():
    F = FRD
    board('01_focus_board', [(F + '01a_focus_site.jpg', '01a Site'), (F + '01b_focus_beam.jpg', '01b beam'), (F + '01c_focus_card.jpg', '01c card'),
                             (F + '01d_focus_home.jpg', '01d HOME'), (F + '04a_disc_deploy.jpg', '04a disc DEPLOY'), (F + '04b_disc_hold.jpg', '04b disc HOLD'),
                             (F + '04c_disc_move.jpg', '04c disc MOVE'), (F + '04d_disc_sacrifice.jpg', '04d disc SACRIFICE'), (F + '05a_sealed_lock_hover.jpg', '05a lock')], 'focus')
    board('02_drag_board', [(F + '02a_drag_pickup.jpg', '02a pick up'), (F + '02b_drag_over_match.jpg', '02b match'), (F + '02c_drag_over_dud.jpg', '02c wrong type'),
                            (F + '02d_drag_over_occupied.jpg', '02d occupied'), (F + '02e_drag_snap.jpg', '02e snap'), (F + '02f_drag_cancel.jpg', '02f cancel'),
                            (F + '02g_drag_limit.jpg', '02g limit'), (F + '02h_drag_over_none.jpg', '02h none'), (F + '02i_drag_over_same.jpg', '02i same')], 'drag')
    board('03_whatif_board', [(F + '03a_whatif_t3c.jpg', '03a t3_c'), (F + '03b_whatif_t2v.jpg', '03b t2_virus'), (F + '03c_whatif_t1c.jpg', '03c t1_c'),
                              (F + '03d_whatif_t3b.jpg', '03d t3_b (dud)')], 'whatif', cols=2)
    board('05_sealed_board', [(F + '05a_sealed_lock_hover.jpg', '05a lock'), (F + '05b_hunter_hover.jpg', '05b hunter'), (F + '05c_sealed_site_locks.jpg', '05c Site -> locks')], 'sealed')
    board('06_input_board', [(F + '06a_focus_order.jpg', '06a order'), (F + '06b_cursor_snap.jpg', '06b snap'), (F + '06c_prompts.jpg', '06c prompts'),
                             (F + '06d_radial_wheel.jpg', '06d wheel'), (F + '06e_shoulder_cycle.jpg', '06e cycle'), (F + '06f_input_map.jpg', '06f map')], 'input')
    board('08_onboarding_board', [(F + '08a_first_raid.jpg', '08a first raid'), (F + '08c_type_code.jpg', '08c type code'), (F + '08d_tier_code.jpg', '08d tier code'),
                                  (F + '08b_demo_1.jpg', '08b-1'), (F + '08b_demo_3.jpg', '08b-3'), (F + '08b_demo_4.jpg', '08b-4')], 'onboarding')


def f_squint():
    names = ['01a_focus_site', '01b_focus_beam', '01d_focus_home', '02a_drag_pickup', '02b_drag_over_match', '03a_whatif_t3c', '03c_whatif_t1c', '04a_disc_deploy', '04c_disc_move', '05a_sealed_lock_hover', '08a_first_raid']
    for n in names:
        src = CLD + n + '.jpg'
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert('RGB')
        cw, ch = 384, 216
        small = im.resize((320, 180), Image.LANCZOS).resize((cw, ch), Image.NEAREST)
        blurred = im.resize((cw, ch), Image.LANCZOS).filter(ImageFilter.GaussianBlur(4))
        de = cb.sim(im, cb.DEUT).resize((cw, ch), Image.LANCZOS)
        tr = cb.sim(im, cb.TRIT).resize((cw, ch), Image.LANCZOS)
        row = Image.new('RGB', (cw * 5, ch + 26), (8, 6, 20))
        for i, x in enumerate([im.resize((cw, ch), Image.LANCZOS), small, blurred, de, tr]):
            row.paste(x, (i * cw, 26))
        d = ImageDraw.Draw(row)
        for i, t in enumerate(['normal', '320 px squint', 'blur 4', 'deutan', 'tritan']):
            d.text((i * cw + 8, 3), n[:6] + '  ' + t, font=font(18, False, 700, 78), fill=(220, 226, 245))
        row.save(SQ + n + '_strip.jpg', quality=92)
        de.resize((960, 540), Image.LANCZOS)
        cb.sim(im, cb.DEUT).save(OUT + 'sims/' + n + '_deutan.jpg', quality=92)
        cb.sim(im, cb.TRIT).save(OUT + 'sims/' + n + '_tritan.jpg', quality=92)
        print('squint', n)


if __name__ == '__main__':
    want = sys.argv[1:] or ['inputmap', 'reasons', 'boards', 'squint']
    for n in want:
        globals()['f_' + n]()
