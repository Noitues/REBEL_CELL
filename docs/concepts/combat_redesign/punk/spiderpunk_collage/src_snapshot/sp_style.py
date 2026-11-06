"""sp_style: style_board.jpg for the Spider-Punk collage concept."""
import sys, os, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sp_lib import *
import sp_tower as SPT

ROOT = 'D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/spiderpunk_collage/'
ANTON, MARK, MONO = ANTON_F, MARKER_F, MONO_F
BG = (22, 18, 30)


def F(p, s):
    return ImageFont.truetype(p, s)


def sample(w, h, fn, S=3, seed=2, bg=None):
    cv = Canvas(w, h, S, seed=seed)
    fn(cv)
    im = cv.down()
    base = Image.new('RGBA', (w, h), (bg or (38, 32, 52)) + (255,))
    base.alpha_composite(im)
    return base.convert('RGB')


def s_halftone(cv):
    f = linear_field(cv, (0, 0), (cv.w, 0))
    cv.over(np.ones((cv.H, cv.W), np.float32), MAG, 1.0)
    cv.over(halftone(cv, f, 5.0, 45), MAG_D, 1.0)


def s_news(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    scrap_text(cv, (cv.w / 2, cv.h / 2, 120, 62), -4, seed=3)


def s_cut(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    m = scissor(cv, [(26, 20), (160, 14), (170, 76), (30, 82)], 0.7)
    cut_layer(cv, m, MAG, edge=2.2, drop=(3, 4))
    m2 = scissor(cv, [(90, 48), (200, 40), (204, 90), (96, 96)], 0.7)
    cut_layer(cv, m2, YEL, edge=2.2, drop=(3, 4))


def s_bolt(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    for i, (c, ph) in enumerate(((YEL, 1), (COB, -1))):
        m = solid(lightning(cv, 0, 20 + i * 0, 190, (20 + i * 14, 40 + i * 44), w0=16, w1=7, zig=7, n=6, phase=ph), cv.S)
        m = cv.poly_mask([(20 + k * 28 + (7 if k % 2 else -7) * ph, 22 + i * 46 + (k % 2) * 4) for k in range(7)] + [(20 + k * 28 + (7 if k % 2 else -7) * ph, 38 + i * 46 + (k % 2) * 4) for k in range(6, -1, -1)])
        cut_layer(cv, solid(m, cv.S), c, edge=1.6, drop=(2.4, 3.2))


def s_ransom(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    ransom(cv, 'CELL-9', (cv.w / 2, cv.h / 2), 34, rot=-3, spacing=2, seed=2)


def s_pin(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    safety_pin(cv, (60, 50), 20, L=70)
    tape(cv, (150, 50), 70, 24, -8, col=(252, 206, 40), alpha=0.95)


def s_lines(cv):
    cv.over(np.ones((cv.H, cv.W), np.float32), (60, 54, 70), 1.0)
    # white cut edge + black drop
    m = scissor(cv, [(14, 10), (150, 8), (152, 30), (16, 32)], 0.5)
    cut_layer(cv, m, MAG, edge=2.0, drop=(3, 4))
    # ink keyline + yellow misregistered plate under a white shape
    sh = scissor(cv, [(176, 8), (214, 8), (214, 34), (176, 34)], 0.4)
    cv.over(np.roll(np.roll(dilate(sh, 2.0, cv.S), int(3 * cv.S), 0), int(3 * cv.S), 1), YEL, 1.0)
    cv.over(dilate(sh, 2.0, cv.S), INK, 1.0)
    cv.over(sh, WHITE, 1.0)
    # marker underline
    marker(cv, [(16, 52), (60, 55), (110, 51), (152, 54)], MAG, w=3.2, alpha=1.0, wob=0.5, taper=(0.1, 0.3))
    # cross-hatch (lost at END TURN, grammar)
    hm = cv.poly_mask([(176, 46), (214, 46), (214, 70), (176, 70)])
    cv.over(hm, (14, 14, 22), 1.0)
    hatch_region(cv, hm[int(46 * cv.S):int(70 * cv.S), int(176 * cv.S):int(214 * cv.S)], int(176 * cv.S), int(46 * cv.S), HARM, ang=45, pitch=4.0, w=1.4, alpha=0.95, over=0, jit=0.05, cross=True)
    # lightning zig edge
    pts = [(16 + k * 12, 74 + (5 if k % 2 else -5)) for k in range(13)]
    marker(cv, pts, YEL, w=3.0, alpha=1.0, wob=0.0, taper=(0, 0), grain=0.0, rough=0.0)


def build():
    A = Image.open(ROOT + 'work/_tw_A.png').convert('RGB') if False else None
    W, H = 2400, 1500
    bd = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(bd)
    # title
    d.text((50, 30), 'SPIDER-PUNK COLLAGE', font=F(ANTON, 84), fill=(255, 204, 0))
    d.text((52, 128), 'the player wheel and hand: cut from a punk poster, pasted up by the Cell', font=F(MARK, 30), fill=(250, 248, 240))
    # palette
    sw = [('CELL MAGENTA', MAG, 'ours: wedges, ink tags'), ('PRINT YELLOW', YEL, 'cut shards, title strips'), ('COBALT', COB, 'flyer shards, B plate'), ('POSTER PURPLE', PUR, 'page, A halftone'),
          ('NEWSPRINT', NEWS, 'scraps, rules paper'), ('PHOTOCOPY BLACK', BLK, 'ink, drops'), ('CUT EDGE', CUT, 'the white cut line'), ('RAM CYAN', (26, 143, 184), 'system, unchanged')]
    x = 50
    d.text((50, 190), 'PALETTE', font=F(MONO, 22), fill=(180, 170, 200))
    for i, (nm, c, role) in enumerate(sw):
        bx = 50 + i * 146
        d.rectangle([bx, 222, bx + 132, 322], fill=c, outline=(250, 248, 240), width=2)
        d.text((bx, 330), nm, font=F(ANTON, 18), fill=(250, 248, 240))
        d.text((bx, 354), '#%02X%02X%02X' % tuple(c), font=F(MONO, 16), fill=(180, 170, 200))
        d.text((bx, 374), role, font=F(MONO, 13), fill=(150, 142, 172))
    # textures and line samples (right of the palette)
    d.text((1260, 190), 'TEXTURES', font=F(MONO, 22), fill=(180, 170, 200))
    tex = [('Ben-Day halftone', sample(220, 100, s_halftone)), ('newsprint scrap', sample(220, 100, s_news)), ('scissor cut + drop', sample(220, 100, s_cut)),
           ('lightning shards', sample(220, 100, s_bolt)), ('ransom-note tiles', sample(220, 100, s_ransom)), ('pin and tape', sample(220, 100, s_pin))]
    for i, (nm, im) in enumerate(tex):
        bx, by = 1260 + (i % 4) * 280, 222 + (i // 4) * 150
        bd.paste(im.resize((260, 118), Image.LANCZOS), (bx, by))
        d.text((bx, by + 122), nm, font=F(MONO, 15), fill=(250, 248, 240))
    ls = sample(240, 100, s_lines)
    bd.paste(ls.resize((260, 108), Image.LANCZOS), (1820, 372))
    d.text((1820, 484), 'line samples', font=F(MONO, 15), fill=(250, 248, 240))
    d.text((50, 530), 'ONE SLICE + THE HUB + ONE CARD', font=F(MONO, 22), fill=(180, 170, 200))
    for k, V in enumerate(('A', 'B')):
        tw = Image.open(ROOT + 'w2_%s/tower_f1_x_1_0__1.png' % V).convert('RGB')
        sl = tw.crop((105, 20, 365, 250)).resize((520, 460), Image.LANCZOS)
        bd.paste(sl, (50 + k * 540, 570))
        d.text((50 + k * 540, 1040), ('A wedge: magenta cut paper, jagged sides, halftone shade' if V == 'A' else 'B wedge: yellow cut edge, xerox grit, cobalt shard'), font=F(MONO, 14), fill=(250, 248, 240))
        hb = tw.crop((235 - 52, 235 - 52, 235 + 52, 235 + 52)).resize((260, 260), Image.LANCZOS)
        bd.paste(hb, (1150 + k * 280, 570))
        d.text((1150 + k * 280, 836), ('A hub: ransom-note name' if V == 'A' else 'B hub: vinyl record'), font=F(MONO, 14), fill=(250, 248, 240))
        ci = Image.open(ROOT + 'w2_%s/card_Trigger_0.png' % V).convert('RGBA')
        pad = Image.new('RGBA', ci.size, BG + (255,))
        pad.alpha_composite(ci)
        pad = pad.convert('RGB').resize((300, 405), Image.LANCZOS)
        bd.paste(pad, (1740 + k * 320, 570))
    d.text((1740, 1000), 'CARD: cost badge, art panel, black TITLE on yellow / white, type band, rules on newsprint', font=F(MONO, 13), fill=(250, 248, 240))
    # manifesto
    d.text((50, 1085), 'MANIFESTO', font=F(MONO, 22), fill=(180, 170, 200))
    lines = ['1  Everything of ours is cut by hand: white scissor edge, black offset drop, magenta ink. The corp has none of that.',
             '2  Solace is clean glass and machine hairlines; we are paper, tape, pins and halftone. You can see who touched the wheel.',
             '3  Loud on purpose: yellow lightning where the slices meet, a ransom-note name for the Breaker. It says: we made this, and we are not asking.']
    for i, ln in enumerate(lines):
        d.text((50, 1125 + i * 50), ln, font=F(MARK, 25), fill=(250, 248, 240))
    d.text((50, 1300), 'Grammar kept: no dashes, HOT/COLD/FAR marks, cross-hatch = pending loss, arrowed outline = movement, no needle.', font=F(MONO, 18), fill=(180, 170, 200))
    bd=bd.crop((0,0,2400,1360)); bd.save(OUT + 'style_board.jpg', quality=90)
    print('style board ok', bd.size)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build()
