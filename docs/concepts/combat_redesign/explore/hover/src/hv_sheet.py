"""hv_sheet: the hover grammar key plate (1920x1080) and the overview contact sheet of every hover plate."""
import sys, os, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import hv_render as R
from hv_render import *
import hv_lib as HL
from hv_lib import PINK, PLAN, HARM, SOAKC, GAIN, SCHED, ENAMEL, LIME, PAPER, INKC, VIOLET
import plan_patch as PP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = os.path.join(ROOT, 'out', 'final')
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/explore/hover/'

ORDER = [('brace', 'BRACE', 'h02  protect a slice'), ('spin3', 'SPIN 3', 'h01  turn the tower'), ('spin2', 'SPIN 2', 'h01  turn the tower'),
         ('nudge', 'NUDGE', 'h01  turn the tower'), ('trigger', 'TRIGGER', 'h03  resolve a unit now'), ('trigger_f2', 'TRIGGER (after Twist)', 'h03  refund live'),
         ('twist', 'TWIST', 'h04  turn one ring'), ('strike', 'STRIKE', 'h05  damage a unit'), ('shove', 'SHOVE', 'h06  slide a unit'),
         ('shove_bump', 'SHOVE (bump)', 'h06  slide into a neighbour'), ('pull', 'PULL', 'h07  pull a unit inward'), ('hold', 'HOLD', 'h08  stop the rings'),
         ('firewall', 'FIREWALL', 'h09  burn a column')]


def key_plate():
    NOW['words'] = True
    bg = Image.new('RGBA', (W, H), (9, 11, 20, 255))
    # faint room backdrop for context
    try:
        room = Image.open(A.ROOM_BIO).convert('RGBA').resize((W, H))
        room.putalpha(60)
        bg.alpha_composite(room)
    except Exception:
        pass
    L = L2()
    L.text((60, 58), 'HOVER GRAMMAR', 54, 'anton', fill=PAPER, anchor='lm')
    L.text((60, 108), 'one key for every card plate  |  family and line ids from VISUAL_PLAN B, C, D, H', 22, 'mono', fill=(175, 192, 214), anchor='lm')
    rows = []
    y0, dy = 190, 108

    def rowtxt(i, head, l1, l2=None):
        y = y0 + i * dy
        L.text((520, y - 14), head, 30, 'anton', fill=PAPER, anchor='lm')
        L.text((520, y + 16), l1, 20, 'mono', fill=(205, 214, 228), anchor='lm')
        if l2:
            L.text((520, y + 42), l2, 20, 'mono', fill=(150, 166, 190), anchor='lm')
        return y

    # 1 lit / dim
    y = rowtxt(0, 'LIT  /  DIM', 'lit = what the card touches, at full value', 'dim = everything else: value x 0.50, chroma x 0.45 (k kept from E10 p2b)')
    L.rect([70, y - 36, 230, y + 40], fill=(58, 84, 102), outline=ENAMEL, w=3, r=6)
    L.rect([260, y - 36, 420, y + 40], fill=(29, 40, 49), outline=(108, 112, 117), w=3, r=6)
    L.text((150, y + 4), 'LIT', 24, 'anton', fill=PAPER)
    L.text((340, y + 4), 'DIM', 24, 'anton', fill=(120, 128, 140))
    # 2 focus
    y = rowtxt(1, 'FOCUS BRACKETS', 'thin lime corners = a legal target', 'thick lime corners = the aimed target (the one the ghost shows)')
    K2m = K2
    K2m.focus_brackets(L, 'rect', dict(box=(86, y - 24, 190, y + 24)), 'A', w=3.0, arm=14, grow=0)
    K2m.focus_brackets(L, 'rect', dict(box=(286, y - 26, 410, y + 26)), 'A', w=5.4, arm=24, grow=0)
    # 3 ghost / veil
    y = rowtxt(2, 'GHOST  /  VEILED ORIGIN', 'ghost = the thing at its NEW place (74 percent) with a grease-pencil outline = proposal', 'veiled = where it is now: ink at 60 percent, nothing else changes')
    poly = [(86, y + 30), (86, y - 28), (200, y - 28), (200, y + 30)]
    L.poly(poly, fill=(58, 84, 102, 190))
    HL.pencil_poly(L, poly, w=4.0, seed=3)
    poly2 = [(286, y + 30), (286, y - 28), (400, y - 28), (400, y + 30)]
    L.poly(poly2, fill=(58, 84, 102, 255))
    HL.tint_poly(L, poly2, (8, 10, 20), 153)
    # 4 L5 channels
    y = rowtxt(3, 'L5  ARROWED OUTLINE = MOVEMENT', 'edge colour = the owner of the motion:  pink = the tower,  orange = rings / schedule,  yellow pencil = a unit path', 'chevrons point the way of travel; the head ends the move')
    HL.channel(L, [(70, y + 28), (150, y + 28)], col=PINK, w=15, head=22, fill=(10, 8, 20, 190))
    HL.channel(L, [(190, y + 28), (270, y + 28)], col=SCHED, w=15, head=22, fill=(10, 8, 20, 190))
    HL.channel(L, [(310, y + 28), (400, y + 28)], col=PLAN, w=15, head=22, fill=(10, 8, 20, 190))
    # 5 hatch
    y = rowtxt(4, 'L7  CROSS-HATCH = LOST AT THIS END TURN', 'pink = ours (enemy HP your cards and guns take),  red = the enemy takes it from you', 'never future losses, never a block: those have their own looks')
    for i, col in enumerate((PINK, HARM)):
        x0 = 90 + i * 160
        pts = [(x0, y - 24), (x0 + 110, y - 24), (x0 + 110, y + 24), (x0, y + 24)]
        L.rect([x0 - 3, y - 27, x0 + 113, y + 27], fill=(24, 8, 20), outline=col, w=3, r=4)
        PP.hatch_poly(L, pts, col, pitch=7.0, lw=2.2, edge=0)
    # 6 pencil marks
    y = rowtxt(5, 'PENCIL RING / UNDERLINE', 'the number, coin or trace square the plan changes (LANDS / THROUGH, RAM spent, TRACE gained)', 'grease pencil = PLAN yellow: a proposal that SEND IT will burn into paint')
    L.ellipse([88, y - 24, 136, y + 24], outline=INKC, w=6.6)
    L.ellipse([88, y - 24, 136, y + 24], outline=PLAN, w=3.2)
    L.text((112, y), '2', 30, 'anton', fill=PAPER)
    HL.pencil(L, [(200, y + 26), (300, y + 25)], w=3.2, ink=1.5, cap=False)
    L.text((250, y - 4), '12', 44, 'anton', fill=PAPER)
    # 7 starburst
    y = rowtxt(6, 'COMIC HIT FRAME  (X, FX-D)', 'pink starburst = our hit lands on that cell  |  burst + speed lines = Strike', 'bursts mark impact points; they never sit on a unit icon')
    HL.starburst(L, 128, y, 30, PINK, (255, 255, 255), 11, 2.6, 3)
    HL.starburst(L, 270, y, 38, PINK, (255, 255, 255), 12, 2.6, 5)
    HL.speed_lines(L, 270, y, 90, 5, 40, 74, PINK)
    # 8 lifted card
    y = rowtxt(7, 'LIFTED CARD = PLAYER-OWNED', 'a hand-cut pink offset print sits behind the lifted card (P family: misregistered, hard-edged, no glow)', 'the other cards in the hand drop to 70 percent value')
    L.rect([108 + 12, y - 30 + 12, 180 + 12, y + 36 + 12], fill=(12, 10, 22), r=6)
    L.rect([108 + 9, y - 30 + 9, 180 + 9, y + 36 + 9], fill=PINK, r=6)
    L.rect([108, y - 30, 180, y + 36], fill=PAPER, outline=INKC, w=2, r=6)
    L.rect([116, y - 22, 172, y + 8], fill=(40, 120, 130), r=3)
    # ghost footnote
    L.text((60, 1040), 'Stand-in board: the E10 generator copy, patched to the plan (no dashes, neutral lane outlines with time grammar, slate units, hatch HP, pink tracers).', 18, 'mono', fill=(150, 166, 190), anchor='lm')
    bg.alpha_composite(L.done())
    return bg.convert('RGB')


def sheet():
    from cv_lib import anton, mono
    cols, tw_, th_ = 4, 700, 394
    gx, gy = 28, 64
    n = len(ORDER) + 1
    rows = (n + cols - 1) // cols
    Wd = cols * tw_ + (cols + 1) * gx
    top = 150
    Hd = top + rows * (th_ + gy) + 40
    im = Image.new('RGB', (Wd, Hd), (11, 12, 20))
    d = ImageDraw.Draw(im)
    d.text((gx, 30), 'HOVER PLATES  |  one per card effect type, Shifting Waves', font=anton(54), fill=(242, 238, 228), anchor='lm')
    d.text((gx, 96), 'lifted card + lit what it touches + dim the rest + ghost / arrow / hatch of the result  |  board = E10 stand-in patched to VISUAL_PLAN  |  hatch pink = ours, red = yours to lose', font=mono(22), fill=(175, 192, 214), anchor='lm')
    items = [(k, a, b) for k, a, b in ORDER] + [('key', 'GRAMMAR KEY', 'marks used on every plate')]
    for i, (k, a, b) in enumerate(items):
        c, r = i % cols, i // cols
        x = gx + c * (tw_ + gx)
        y = top + r * (th_ + gy)
        fn = os.path.join(FIN, 'hover_%s.png' % k) if k != 'key' else os.path.join(FIN, 'hover_key.png')
        t = Image.open(fn).convert('RGB').resize((tw_, th_), Image.LANCZOS)
        im.paste(t, (x, y + 30))
        d.rectangle([x - 1, y + 29, x + tw_, y + 30 + th_], outline=(70, 78, 98), width=1)
        d.text((x, y + 12), a, font=anton(28), fill=(242, 238, 228), anchor='lm')
        d.text((x + tw_, y + 12), b, font=mono(18), fill=(150, 166, 190), anchor='rm')
    return im


if __name__ == '__main__':
    os.makedirs(FIN, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == 'key':
        key_plate().save(os.path.join(FIN, 'hover_key.png'))
        print('key ok')
    else:
        sheet().save(os.path.join(FIN, 'hover_overview.png'))
        print('sheet ok')
