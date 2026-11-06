"""f1_legend: one sheet that answers designer notes 2, 3, 5 and 7 in the F1 hand: who owns a thing (family signature), when it happens (time marks), what is lost (HP states), what a colour means.
All tiles are crops of the real plates (nothing re-drawn), so the sheet shows exactly what the player sees."""
import sys, os
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

OUT = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 15)
mo2 = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 13)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 26)
an2 = ImageFont.truetype(FD + 'Anton-Regular.ttf', 19)
BG = (10, 12, 20)
YEL = (255, 226, 0)
TXT = (214, 224, 240)


def tile(sheet, im, box, xy, scale, title, lines):
    c = im.crop(box)
    c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(sheet)
    x, y = xy
    sheet.paste(c, (x, y + 24))
    d.rectangle([x - 1, y + 23, x + c.width, y + 24 + c.height], outline=(60, 70, 90), width=1)
    d.text((x, y), title, font=an2, fill=YEL)
    for i, ln in enumerate(lines):
        d.text((x, y + 28 + c.height + i * 17), ln, font=mo2, fill=TXT)
    return c.width, c.height + 28 + len(lines) * 17


def build():
    p1 = Image.open(OUT + 'p1_decide.png').convert('RGB')
    p2b = Image.open(OUT + 'p2b_hover.png').convert('RGB')
    fx = Image.open(OUT + 'fx_moment_1_block_vs_break.png').convert('RGB')
    S = Image.new('RGB', (1920, 1080), BG)
    d = ImageDraw.Draw(S)
    d.text((24, 10), 'F1 BLACK-BOOK BURNER: legend (every tile is a crop of the real plate)', font=an, fill=(255, 255, 255))
    d.text((24, 44), 'A family is told by its MATERIAL and LINE, not by colour.  Colour = a cause or an owner.  Dashed lines: none.  Dotted: only the +2 threat trim.', font=mo, fill=TXT)
    # ---- row 1: who (families)
    y = 78
    x = 24
    fam = [
        ('P  PLAYER (ours)', p1, (356, 356, 566, 566), 1.3, ['paper, marker, ballpoint, tape: hand-made', 'L2 tapered ink + pink marker, block drop', 'pink = ours']),
        ('P  the hand', p1, (870, 775, 1090, 1000), 1.2, ['wheat-paste cards, kraft tape, marker rules', 'pink print behind the lifted card', 'SEND IT = the brightest object']),
        ('E  ENEMY (Solace)', p1, (400, 190, 640, 330), 1.1, ['slate glass, enamel hairline, helix rule', 'L3 constant 1.5 px, perfect arcs', 'one outline colour on every ring']),
        ('T  THREAT', p1, (690, 395, 800, 560), 1.5, ['flat HARM stencil, hard ink keyline', 'solid chevron = hit, hollow = growth', 'HOT: glow + END notch']),
        ('K  CLOCK', p1, (14, 14, 340, 110), 1.0, ['gunmetal ticket, engraved groove', 'L4 groove, L5 arrowed outline = movement', 'W6 50 / W5 70 / W4 100 percent + pips']),
        ('N  PLAN (pencil)', p2b, (225, 620, 520, 800), 1.1, ['grease pencil: PLAN yellow, wax grain', 'L6 + L5 = a route that has NOT happened', 'resolve turns it into pink paint']),
    ]
    for t, im, box, sc, lines in fam:
        w, h = tile(S, im, box, (x, y), sc, t, lines)
        x += w + 18
    # ---- row 2: when + hp + effects
    y2 = 470
    x = 24
    w, h = tile(S, p1, (600, 100, 800, 260), (x), 1.0, 'WHEN: this END TURN vs later', ['HOT = solid, full chroma, glow, END notch', 'COLD (+1) thinner, 70 percent value, 1 pip', 'FAR (+2) 50 percent, 2 pips; dots only on the trim']) if False else (0, 0)
    w, h = tile(S, p1, (610, 300, 800, 440), (x, y2), 1.25, 'WHEN  trim + tags', ['HOT: solid red bar, glow, END notch', 'COLD: thinner #D9877C bar + 1 pip', 'FAR: dotted + 2 pips (the only dots)'])
    x += w + 18
    w, h = tile(S, p1, (440, 440, 640, 640), (x, y2), 1.2, 'HP  the hub ring', ['green block = kept; red cross-hatch = lost', 'at THIS END TURN (cause colour = enemy)', 'pending block bulges 2 px'])
    x += w + 18
    w, h = tile(S, p1, (1066, 94, 1416, 152), (x, y2), 0.85, 'HP  the YOU strip (taped on)', ['same 15 blocks in 3 x 5', 'soak = blue hatch, us = pink hatch'])
    x += w + 18
    w, h = tile(S, fx, (600, 330, 790, 500), (x, y2), 1.25, 'X  harm: flood + krackle', ['red halftone from the rim, black krackle', 'plate in shards, 3 px misregistered plate', 'Protect (paper plate) vs Harm (print)'])
    # ---- row 3: colour meaning key (drawn swatches)
    y3 = 820
    d.text((24, y3), 'COLOUR = ONE MEANING EACH', font=an2, fill=YEL)
    sw = [((255, 61, 168), 'PINK ours'), ((255, 68, 51), 'HARM damage to you'), ((123, 224, 123), 'GAIN your life'), ((58, 126, 243), 'SOAK your soak'),
          ((255, 226, 0), 'PLAN not yet'), ((255, 140, 26), 'SCHEDULE rings move'), ((255, 196, 40), 'GOLD the Adjuster'), ((92, 225, 255), 'CYAN terminal / RAM'),
          ((160, 60, 255), 'VIOLET Trace'), ((212, 255, 0), 'LIME focus corners'), ((217, 225, 234), 'ENAMEL neutral: every outline')]
    xx = 24
    for col, nm in sw:
        d.rectangle([xx, y3 + 34, xx + 34, y3 + 60], fill=col, outline=(0, 0, 0))
        d.text((xx + 40, y3 + 36), nm, font=mo2, fill=TXT)
        xx += 40 + int(d.textlength(nm, font=mo2)) + 22
        if xx > 1700:
            xx = 24
            y3 += 34
    lines = ['Line language:  L2 painted stroke = ours | L3 vector hairline = machine | L4 engraved = clock | L5 arrowed outline = movement | L6 pencil = plan | L7 cross-hatch = lost at this END TURN',
             'L8 dots = two turns away (trim only) | L9 glow = live this END TURN | L10 double line = protection (clamp, shield plate).  Shield BLOCK = intact paper plate; shield BREAK = the same plate in shards on a red flood.']
    for i, ln in enumerate(lines):
        d.text((24, 975 + i * 22), ln, font=mo2, fill=TXT)
    S.save(OUT + 'legend_f1.png')
    return S


if __name__ == '__main__':
    build()
    print('legend ok')
