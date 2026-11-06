"""hz_key: the one-page hover grammar key for the final board.  Marks drawn with the plate code at use size, plus 1x crops of the rendered plates.
python hz_key.py  -> ../out/h00_key.png   (needs ../out/h02_brace.png, h06_shove.png, h05_strike.png, h01_tower_turn.png)"""
import sys, os, math
sys.dont_write_bytecode = True
import hz_core as Z
from hz_core import *
import gramlib as GL

OUT = Z.HERE + 'out/'
TXT_HI, TXT_MID = (242, 246, 255), (175, 192, 214)
CY = (92, 225, 255)


def wrap(L, x, y, s, size, width, col=TXT_MID, kind='mono', lh=25):
    words = s.split(' ')
    ln = ''
    for w in words:
        t = (ln + ' ' + w).strip()
        if L.tw(t, size, kind) > width and ln:
            L.text((x, y), ln, size, kind, fill=col, anchor='lm')
            y += lh
            ln = w
        else:
            ln = t
    L.text((x, y), ln, size, kind, fill=col, anchor='lm')
    return y


def main():
    NOW['words'] = True
    plates = {k: Image.open(OUT + v + '.png').convert('RGB') for k, v in (('h02', 'h02_brace'), ('h06', 'h06_shove'), ('h05', 'h05_strike'), ('h01', 'h01_tower_turn'), ('h04', 'h04_twist'))}
    bg = Image.new('RGBA', (W, H), (8, 10, 22, 255))
    L = L2()
    L.text((60, 62), 'HOVER GRAMMAR', 60, 'anton', fill=TXT_HI, anchor='lm')
    L.text((62, 116), 'one key for every card plate  |  final locked board, neutral skin  |  marks drawn with the plate code at use size, crops at 1x', 19, 'mono', fill=TXT_MID, anchor='lm')
    rows = [
        ('LIT / DIM', 'lit = what the card touches, full value. dim = everything else, value x0.40, chroma x0.45. The cards not in play drop to 70 percent; UNDO, SEND IT and the nameplate to 62 percent.'),
        ('FOCUS: CORNERS ONLY', 'lime corner brackets, 12 px legs. 2 px = a legal target. 3.5 px = the aimed target. Never a full outline.'),
        ('PLAN ARROW', 'PLAN yellow arrowed outline = this will move along here. Movement only: every hover move is this, and nothing else uses it.'),
        ('PENCIL RING', 'a ring round a number = it changes under the plan; pencil brackets ( ) when HUD words leave no room for a ring (the bill digits). Ring on a RAM coin = RAM spent (green = refunded). Square on a TRACE pip = TRACE added.'),
        ('GHOST', 'the sim plan unit at its new place at 74 percent, with a pencil outline = proposal, with its plan landing arc. The origin cell is veiled.'),
        ('HATCH', 'cross-hatch = HP lost at THIS END TURN; the hatch colour is the cause. pink = ours (we take it). red = the enemy takes it from you. indigo = your soak.'),
        ('LIFTED CARD', 'the hovered WPAP card lifts 1.10x on its pink offset print; the fan slides right when needed so the lifted card stays 4 px outside wheel radius 455 and clear of the landing marks. The rest of the hand dims to 70 percent.'),
        ('HIT BURST', 'pink comic starburst = a hit that lands on a unit. It marks a cell or an edge, never an icon.'),
    ]
    Y0, RH = 168, 200
    cols = [60, 990]
    pos = []
    for i, (t, s) in enumerate(rows):
        c, r = divmod(i, 4)
        x, y = cols[c], Y0 + r * (RH + 26)
        pos.append((x, y))
        L.rect([x, y, x + 372, y + RH], fill=(5, 13, 28, 255), outline=CY + (255,), w=2, r=8)
        L.text((x + 400, y + 22), t, 30, 'anton', fill=TXT_HI, anchor='lm')
        wrap(L, x + 400, y + 66, s, 17, 470)
    bg.alpha_composite(L.done())
    # 1 lit / dim: real 1x crops of h02 (a lit slice, a dim ring cell)
    x, y = pos[0]
    h02 = plates['h02']
    bg.paste(h02.crop((570, 410, 740, 560)), (x + 12, y + 12))
    bg.paste(h02.crop((150, 410, 320, 560)), (x + 190, y + 12))
    # 7 lifted card: crop of h02's hand (scaled to fit)
    x7, y7 = pos[6]
    card = h02.crop((950, 745, 1195, 1078))
    card = card.resize((int(card.width * 0.53), int(card.height * 0.53)), Image.LANCZOS)
    bg.paste(card, (x7 + 186 - card.width // 2, y7 + 10))
    # 5 ghost: crop of h06 (veiled origin + ghost)
    x5, y5 = pos[4]
    g = plates['h06'].crop((440, 200, 900, 432)).resize((348, 176), Image.LANCZOS)
    bg.paste(g, (x5 + 12, y5 + 12))
    L = L2()
    L.text((x + 97, y + RH - 14), 'LIT', 16, 'mono', fill=TXT_HI, anchor='mm')
    L.text((x + 275, y + RH - 14), 'DIM', 16, 'mono', fill=TXT_HI, anchor='mm')
    # 2 focus
    x, y = pos[1]
    for (bx, th, lab) in ((x + 30, False, 'legal 2 px'), (x + 210, True, 'aimed 3.5 px')):
        L.rect([bx + 6, y + 40, bx + 126, y + 130], fill=(52, 60, 78, 255), r=4)
        HL.rect_corners(L, (bx + 6, y + 40, bx + 126, y + 130), w=3.5 if th else 2.0, leg=12, pad=5)
        L.text((bx + 66, y + 166), lab, 16, 'mono', fill=TXT_HI, anchor='mm')
    # 3 plan arrow
    x, y = pos[2]
    pc(L, [(x + 26, y + 84), (x + 120, y + 84), (x + 190, y + 44), (x + 300, y + 44)], w=13, head=19)
    pc(L, [(x + 40, y + 146), (x + 330, y + 146)], w=12, head=17, tail_dot=True)
    # 4 pencil ring
    x, y = pos[3]
    L.text((x + 60, y + 62), '12', 58, 'anton', fill=TXT_HI, anchor='mm', stroke=4)
    L.text((x + 128, y + 62), '->', 36, 'anton', fill=TXT_HI, anchor='mm')
    L.text((x + 190, y + 62), '6', 58, 'anton', fill=HARM, anchor='mm', stroke=4)
    HL.pencil_oval(L, x + 190, y + 62, 28, 30, seed=3)
    for pts_ in Z._bracket_pts(x + 60, y + 62, 40, 28, 50, 4):        # brackets: the bill-digit form (O-30)
        HL.pencil(L, pts_, w=3.0, ink=1.6, seed=4, grain=True, cap=True)
    for i in range(4):
        L.ellipse([x + 40 + 32 * i - 12, y + 150 - 12, x + 40 + 32 * i + 12, y + 150 + 12], fill=(92, 225, 255, 255) if i < 3 else (8, 14, 22, 255), outline=CY + (255,), w=2)
    HL.pencil_oval(L, x + 40 + 32 * 3, y + 150, 18.5, 18.5, seed=5, w=3.2, ink=1.6)
    for i in range(3):
        bx = x + 214 + 28 * i
        L.rect([bx - 11, y + 150 - 11, bx + 11, y + 150 + 11], fill=(160, 60, 255, 255) if i < 2 else (28, 20, 44, 255), outline=(160, 60, 255, 255), w=2, r=3)
    HL.pencil_box(L, (x + 214 + 56 - 13, y + 150 - 13, x + 214 + 56 + 13, y + 150 + 13), seed=7, w=3.0, ink=1.6, pad=2)
    # 6 hatch: the board's own pending-loss segments (gramlib.seg_shape), one per cause
    x, y = pos[5]
    for i, (st, lab) in enumerate((('ours', 'pink: ours'), ('harm', 'red: yours'), ('soak', 'indigo: soak'))):
        bx = x + 22 + i * 116
        core = [(bx + 6, y + 40), (bx + 94, y + 40), (bx + 94, y + 130), (bx + 6, y + 130)]
        GL.seg_shape(L, core, 4.0, st, ink_w=1.6, pitch=8.0, lw=2.4, opt='A', glow=False)
        L.text((bx + 50, y + 166), lab, 15, 'mono', fill=TXT_HI, anchor='mm')
    # 8 burst
    x, y = pos[7]
    pink_burst(L, x + 100, y + 96, 40, 3)
    HL.speed_lines(L, x + 250, y + 96, 0, 5, 20, 54, PINK)
    pink_burst(L, x + 250, y + 96, 22, 5)
    bg.alpha_composite(L.done())
    bg.convert('RGB').save(OUT + 'h00_key.png')
    print('ok key')


if __name__ == '__main__':
    main()
