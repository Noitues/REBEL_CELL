"""hv_key: the one-page hover grammar key, drawn with the real mark functions at use size + crops of the real plates"""
import sys, os, math
sys.dont_write_bytecode = True
import hv_plates2 as P
from hv_plates2 import *
from PIL import Image, ImageDraw
import hv_final as HF

IN = HF.IN


def main(out):
    NOW['words'] = True
    W_, H_ = 1920, 1080
    bg = Image.new('RGB', (W_, H_), (8, 10, 22))
    d = ImageDraw.Draw(bg)
    d.text((60, 40), 'HOVER GRAMMAR', font=HF.anton(60), fill=(242, 246, 255))
    d.text((62, 112), 'one key for every card plate  |  family and line ids from VISUAL_PLAN B, C, D, H  |  drawn with the plate code at use size', font=HF.mono(19), fill=(175, 192, 214))
    L = L2()
    rows = [
        ('LIT / DIM', 'lit = what the card touches, full value.  dim = everything else, value x0.40 and chroma x0.45.  The cards not in play drop to 70 percent.'),
        ('FOCUS: CORNERS ONLY', 'lime corner brackets, 12 px legs.  2 px = a legal target.  3.5 px = the aimed target.  Never a full-cell outline.'),
        ('PLAN ARROW (L5)', 'PLAN yellow arrowed outline = this will move along here.  Every hover move is this.  Pink and orange arrows exist only in resolve.'),
        ('PENCIL RING (L6)', 'a ring round a number = it changes under the plan.  Ring on a RAM coin = RAM spent.  Square on a TRACE pip = TRACE added.'),
        ('GHOST', 'the thing at its new place at 74 percent, with a pencil outline = proposal.  The origin cell is veiled with ink.'),
        ('HATCH (L7)', 'cross-hatch = lost at THIS END TURN.  pink = ours (we take it).  red = the enemy takes it from you.  indigo = your soak.'),
        ('LIFTED CARD', 'the hovered card grows 1.12x on a pink offset print (P family: hand-cut, hard edge, no glow).  The hand dims.'),
        ('HIT BURST (X)', 'pink comic starburst = a hit that lands.  It marks a cell or an edge, never an icon.'),
    ]
    X0, Y0, RH = 60, 168, 108
    cols = [60, 990]
    pos = []
    for i, (t, s) in enumerate(rows):
        c, r = divmod(i, 4)
        x = cols[c]
        y = Y0 + r * (RH + 90)
        pos.append((x, y))
        d.rounded_rectangle([x, y, x + 372, y + RH + 56], radius=8, fill=(5, 13, 28), outline=(92, 225, 255), width=2)
        d.text((x + 400, y + 6), t, font=HF.anton(30), fill=(242, 246, 255))
        words = s.split(' ')
        ln, yy = '', y + 52
        for w in words:
            tt = (ln + ' ' + w).strip()
            if d.textlength(tt, font=HF.mono(17)) > 480 and ln:
                d.text((x + 400, yy), ln, font=HF.mono(17), fill=(175, 192, 214)); yy += 24; ln = w
            else:
                ln = tt
        d.text((x + 400, yy), ln, font=HF.mono(17), fill=(175, 192, 214))
    # 1 lit / dim: real crops
    h02 = Image.open(IN + 'h02.png').convert('RGB')
    lit = h02.crop((560, 560, 680, 680)).resize((170, 170), Image.LANCZOS).crop((0, 10, 170, 150))
    dim = h02.crop((250, 250, 370, 370)).resize((170, 170), Image.LANCZOS).crop((0, 10, 170, 150))
    x, y = pos[0]
    bg.paste(lit.resize((172, 164)), (x + 10, y + 10)); bg.paste(dim.resize((172, 164)), (x + 190, y + 10))
    d.text((x + 96, y + 190 - 8), 'LIT', font=HF.mono(16), fill=(242, 246, 255), anchor='mm')
    d.text((x + 276, y + 190 - 8), 'DIM', font=HF.mono(16), fill=(242, 246, 255), anchor='mm')
    # 2 focus
    x, y = pos[1]
    for (bx, th, lab) in ((x + 30, False, 'legal'), (x + 210, True, 'aimed')):
        L.rect([bx + 6, y + 36, bx + 126, y + 126], fill=(60, 80, 100, 255), r=4)
        HL.rect_corners(L, (bx + 6, y + 36, bx + 126, y + 126), w=3.5 if th else 2.0, leg=12, pad=5)
        L.text((bx + 66, y + 150), lab + (' 3.5 px' if th else ' 2 px'), 16, 'mono', fill=(242, 246, 255))
    # 3 plan arrow
    x, y = pos[2]
    HL.channel(L, [(x + 26, y + 80), (x + 120, y + 80), (x + 190, y + 40), (x + 290, y + 40)], col=PLAN, w=15, head=22, chev=True, fill=(10, 8, 20, 190))
    HL.channel(L, [(x + 40, y + 130), (x + 330, y + 130)], col=PLAN, w=13, head=19, chev=True, fill=(10, 8, 20, 190), tail_dot=True)
    # 4 pencil ring
    x, y = pos[3]
    L.text((x + 70, y + 60), '12', 58, 'anton', fill=(242, 246, 255))
    L.text((x + 128, y + 60), '->', 40, 'anton', fill=(242, 246, 255))
    L.text((x + 190, y + 60), '6', 58, 'anton', fill=(255, 68, 51))
    HL.pencil_oval(L, x + 190, y + 60, 32, 36, seed=3)
    for i in range(4):
        L.ellipse([x + 40 + 36 * i - 14, y + 135 - 14, x + 40 + 36 * i + 14, y + 135 + 14], fill=(92, 225, 255, 255) if i < 3 else (8, 12, 24, 255))
    HL.pencil_oval(L, x + 40 + 36 * 3, y + 135, 19, 19, seed=5, w=3.2, ink=1.6)
    for i in range(3):
        L.rect([x + 190 + 36 * i - 13, y + 135 - 13, x + 190 + 36 * i + 13, y + 135 + 13], fill=(160, 60, 255, 255) if i < 2 else (8, 12, 24, 255), r=4)
    HL.pencil_box(L, (x + 190 + 36 * 2 - 13, y + 135 - 13, x + 190 + 36 * 2 + 13, y + 135 + 13), seed=7, w=3.0, ink=1.6)
    # 5 ghost
    x, y = pos[4]
    L.rect([x + 24, y + 54, x + 146, y + 134], fill=(8, 10, 20, 255), r=6)
    L.rect([x + 24, y + 54, x + 146, y + 134], outline=(80, 92, 120, 255), w=2, r=6)
    L.rect([x + 200, y + 54, x + 322, y + 134], fill=(61, 84, 102, 188), r=6)
    HL.pencil_poly(L, [(x + 200, y + 54), (x + 322, y + 54), (x + 322, y + 134), (x + 200, y + 134)], w=3.6, ink=2.0, seed=2)
    HL.channel(L, [(x + 150, y + 94), (x + 190, y + 94)], col=PLAN, w=10, head=14, chev=False, fill=(10, 8, 20, 190))
    L.text((x + 85, y + 30), 'origin: veiled', 15, 'mono', fill=(175, 192, 214))
    L.text((x + 262, y + 30), 'ghost: 74 pct', 15, 'mono', fill=(175, 192, 214))
    # 6 hatch
    x, y = pos[5]
    for i, (col, lab) in enumerate(((PINK, 'pink: ours'), (HARM, 'red: yours'), (SOAKC, 'indigo: soak'))):
        bx = x + 18 + i * 116
        PP.hatch_poly(L, [(bx, y + 40), (bx + 100, y + 40), (bx + 100, y + 130), (bx, y + 130)], col, pitch=8.0, lw=2.4, base=(12, 10, 22), edge=2.6)
        L.text((bx + 50, y + 152), lab, 15, 'mono', fill=(242, 246, 255))
    # 8 burst
    x, y = pos[7]
    HL.starburst(L, x + 100, y + 84, 40, PINK, (255, 255, 255), 11, 2.6, 3)
    HL.speed_lines(L, x + 250, y + 84, 0, 5, 20, 54, PINK)
    HL.starburst(L, x + 250, y + 84, 22, PINK, (255, 255, 255), 11, 2.6, 5)
    bg = bg.convert('RGBA')
    bg.alpha_composite(L.done())
    # 7 lifted card: real crop
    x, y = pos[6]
    card = h02.crop((1000, 746, 1220, 1040)).resize((106, 142), Image.LANCZOS)
    bg.paste(card, (x + 133, y + 11))
    bg.convert('RGB').save(out)


if __name__ == '__main__':
    main(sys.argv[1])
    print('ok key')
