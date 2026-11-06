"""nowords_variant: the screen-wide rule, three options, as a table of non-word forms + the E10 nowords plate crop. Output sheet_nowords_variant.jpg"""
import sys
sys.dont_write_bytecode = True
from a_kit import *
from a_render import render, crop2
from PIL import ImageFont

OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/actions/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
F1 = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 22)
F2 = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 17)
BG = (20, 22, 30)
CELLW, CELLH = 400, 74
ROWS = ['hero digits  12 > 6', 'ring tag  NOW W1', 'card title  TRIGGER', 'verb  SEND IT', 'identity  CELL-9 // BREAKER', 'UNDO [Z]', 'hover tag  PACKET x3 HP 9/9 ...']
RULES = {
 'A': 'A  GLYPH OR TALLY: every word becomes its set glyph, every digit a tally (groups of 5); no placeholder bars; texture text removed.',
 'B': 'B  PLATE STAYS, CONTENT SWAPS: same plates and widths as with words (layout never moves); glyph or tally centred on the plate.',
 'C': 'C  REDACTION: each word becomes one ink bar the width of the word at 60 percent height; digits stay tallies. Conservative, keeps rhythm.',
}


def cell(rule, row):
    im = Image.new('RGBA', (CELLW * 2, CELLH * 2), (10, 12, 20, 255))
    d = ImageDraw.Draw(im)
    S = 2
    cy = CELLH
    if row == 0:        # 12 > 6
        tally(d, 30 * S, cy, 12, 40 * S, WHITE, INK, 4 * S, 12 * S)
        pink(d, [(190 * S, cy), (230 * S, cy)], YEL, 6 * S)
        pink(d, [(215 * S, cy - 14 * S), (232 * S, cy), (215 * S, cy + 14 * S)], YEL, 6 * S)
        tally(d, 260 * S, cy, 6, 40 * S, RED, INK, 4 * S, 12 * S)
        if rule == 'C':
            pass
    elif row == 1:      # ring tag NOW W1
        x0, w = 40 * S, 120 * S
        d.rounded_rectangle([x0, cy - 14 * S, x0 + w, cy + 14 * S], radius=6 * S, fill=(8, 10, 18), outline=(255, 68, 51), width=2 * S)
        if rule == 'C':
            d.rounded_rectangle([x0 + 12 * S, cy - 5 * S, x0 + w - 12 * S, cy + 5 * S], radius=3 * S, fill=(255, 68, 51))
        else:
            for i in range(1):      # ring NOW = lane ordinal: one pip; W1 = one wave tally stroke
                d.ellipse([x0 + 20 * S, cy - 6 * S, x0 + 32 * S, cy + 6 * S], fill=(255, 68, 51), outline=INK, width=S)
            tally(d, x0 + 62 * S, cy, 1, 18 * S, (255, 68, 51), INK, 3 * S, 8 * S)
    elif row == 2:      # card title
        if rule == 'C':
            d.rounded_rectangle([40 * S, cy - 8 * S, 40 * S + 150 * S, cy + 8 * S], radius=4 * S, fill=INK, outline=(90, 90, 100), width=S)
        else:
            d.rounded_rectangle([40 * S, cy - 26 * S, 40 * S + 190 * S, cy + 26 * S], radius=8 * S, fill=(14, 18, 30), outline=(255, 140, 26), width=2 * S) if rule == 'B' else None
            cx = 135 * S if rule == 'B' else 70 * S
            R = 20 * S
            d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=WHITE, width=3 * S)
            pink(d, [(cx - R * 1.5, cy), (cx + R * 1.5, cy)], WHITE, 3 * S)
            pink(d, [(cx, cy - R * 1.5), (cx, cy + R * 1.5)], WHITE, 3 * S)
    elif row == 3:      # SEND IT
        if rule == 'C':
            im2 = vinyl2(240, 70, 62, lambda dd, SS, ox, oy, w, h: dd.rounded_rectangle([ox + 40 * SS, oy + h * SS / 2 - 14 * SS, ox + w * SS - 40 * SS, oy + h * SS / 2 + 14 * SS], radius=6 * SS, fill=INK), VY_TOP, VY_BOT, -3)
        else:
            im2 = vinyl2(240, 70, 62, lambda dd, SS, ox, oy, w, h: g_go_ring(dd, ox + w * SS / 2, oy + h * SS / 2, 26 * SS, INK, VY_TOP), VY_TOP, VY_BOT, -3)
        im2 = im2.resize((int(im2.width * 1.0 * S * 0.8), int(im2.height * S * 0.8)), Image.LANCZOS)
        im.alpha_composite(im2, (30 * S, int(cy - im2.height / 2)))
    elif row == 4:      # CELL-9
        def cont(dd, SS, ox, oy, w, h):
            dd.ellipse([ox + 12 * SS, oy + h * SS / 2 - 22 * SS, ox + 56 * SS, oy + h * SS / 2 + 22 * SS], fill=(16, 40, 60), outline=INK, width=2 * SS)
            g_breaker(dd, ox + 34 * SS, oy + h * SS / 2, 14 * SS, (150, 240, 255), INK)
            if rule == 'C':
                dd.rounded_rectangle([ox + 70 * SS, oy + h * SS / 2 - 8 * SS, ox + w * SS - 14 * SS, oy + h * SS / 2 + 8 * SS], radius=4 * SS, fill=INK)
            else:
                tally(dd, ox + 76 * SS, oy + h * SS / 2, 9, 26 * SS, INK, (150, 240, 255), 3 * SS, 9 * SS)
        im2 = vinyl2(230, 58, 30, cont, VC_TOP, VC_BOT, 2)
        im2 = im2.resize((int(im2.width * S * 0.8), int(im2.height * S * 0.8)), Image.LANCZOS)
        im.alpha_composite(im2, (30 * S, int(cy - im2.height / 2)))
    elif row == 5:      # UNDO
        d.rounded_rectangle([40 * S, cy - 18 * S, 40 * S + 170 * S, cy + 18 * S], radius=8 * S, fill=(5, 13, 28), outline=CYAN, width=2 * S)
        if rule == 'C':
            d.rounded_rectangle([54 * S, cy - 6 * S, 54 * S + 80 * S, cy + 6 * S], radius=3 * S, fill=CRT_TXT)
        else:
            g_undo(d, 62 * S, cy, 11 * S, CRT_TXT, (5, 13, 28))
        d.rounded_rectangle([172 * S, cy - 13 * S, 172 * S + 26 * S, cy + 13 * S], radius=4 * S, outline=CYAN, width=2 * S)
    else:               # hover tag
        w = 330
        d.rounded_rectangle([20 * S, cy - 30 * S, (20 + w) * S, cy + 30 * S], radius=8 * S, fill=(5, 13, 28), outline=YEL, width=2 * S)
        if rule == 'C':
            for i, ww in enumerate((220, 260, 170)):
                d.rounded_rectangle([36 * S, (cy - 22 + i * 16) * S, (36 + ww) * S, (cy - 12 + i * 16) * S], radius=3 * S, fill=(200, 205, 215))
        else:
            g_wormless = None
            x = 40 * S
            d.ellipse([x - 4 * S, cy - 20 * S, x + 20 * S, cy + 4 * S], fill=(130, 70, 110), outline=WHITE, width=2 * S)
            tally(d, 70 * S, cy - 8 * S, 3, 22 * S, WHITE, INK, 3 * S, 9 * S)
            tally(d, 130 * S, cy - 8 * S, 9, 22 * S, GREEN, INK, 3 * S, 8 * S)
            tally(d, 40 * S, cy + 16 * S, 6, 22 * S, RED, INK, 3 * S, 9 * S)
            tally(d, 160 * S, cy + 16 * S, 6, 22 * S, RED, INK, 3 * S, 9 * S)
    return im.resize((CELLW, CELLH), Image.LANCZOS)


def build():
    cur = render('nowords')
    left = crop2(cur, (1066, 0, 1920, 540), 0.55)
    left2 = crop2(cur, (1380, 840, 1920, 1080), 0.9)
    pad = 12
    W_ = 2380
    colw = CELLW
    head = 150
    rows_h = CELLH + 22
    H_ = 70 + head + len(ROWS) * rows_h + 60 + max(left.height, 10) + 20
    sh = Image.new('RGB', (W_, H_), BG)
    d = ImageDraw.Draw(sh)
    d.text((pad, 14), 'nowords_variant  one rule for every word-carrying element (words off)', font=F1, fill=(240, 244, 255))
    y = 56
    for ci, r in enumerate('ABC'):
        x = 250 + ci * (colw + 40)
        txt = RULES[r]
        words = txt.split()
        line, ly = '', y
        for wd in words:
            t = (line + ' ' + wd).strip()
            if d.textlength(t, font=F2) > colw + 20 and line:
                d.text((x, ly), line, font=F2, fill=(120, 230, 255)); ly += 21; line = wd
            else:
                line = t
        d.text((x, ly), line, font=F2, fill=(120, 230, 255))
    y += head
    for ri, rn in enumerate(ROWS):
        d.text((pad, y + 28), rn, font=F2, fill=(255, 200, 90))
        for ci, r in enumerate('ABC'):
            x = 250 + ci * (colw + 40)
            sh.paste(cell(r, ri).convert('RGB'), (x, y))
        y += rows_h
    d.text((pad, y + 6), 'CURRENT E10 nowords plate (proxy bars, blank plates; words survive inside slice and unit textures)', font=F2, fill=(255, 200, 90))
    y += 36
    sh.paste(left.convert('RGB'), (pad, y))
    sh.paste(left2.convert('RGB'), (pad + left.width + 20, y))
    sh = sh.crop((0, 0, W_, min(H_, y + max(left.height, left2.height) + 12)))
    sh.save(OUTD + 'sheet_nowords_variant.jpg', quality=88)
    print(sh.size)


if __name__ == '__main__':
    build()
