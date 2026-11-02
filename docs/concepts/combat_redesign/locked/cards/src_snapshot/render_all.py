"""render_all: builds card_sheet.jpg, hand_p1.jpg, type_band_key.jpg, legibility_1x_320.jpg and checks.json from card_render.draw_card.
python render_all.py [sheet|hand|key|checks|all]"""
import sys, os, math, json, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import card_render as C

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/cards/'
WORK = 'D:/rc_scratch/combat_redesign/locked/cards/work/'
BG = 'D:/rc_scratch/combat_redesign/punk/card_titles/out/bg_noui.png'
os.makedirs(OUT, exist_ok=True)
SCALE = 1.15


def F(px, name='Anton-Regular.ttf'):
    return ImageFont.truetype(HERE + '/fonts/' + name, px)


def cw(s=SCALE):
    return int(round(176 * s))


def shadow(im, off=(4, 8), blur=7, alpha=0.6):
    pad = blur * 3 + 12
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.paste(im, (pad, pad))
    a = big.split()[3]
    sh = Image.new('L', big.size, 0)
    sh.paste(a, off)
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    out = Image.new('RGBA', big.size, (8, 6, 14, 0))
    out.putalpha(sh)
    return out, big


def put(base, im, cx, cy, ang=0.0, k=1.0, sh=True, off=(4, 8), blur=7):
    """im is a draw_card image already at the final scale * k (k is the output multiplier 1 or 2 of the whole composite)"""
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    if sh:
        s, big = shadow(im, (int(off[0] * k), int(off[1] * k)), int(blur * k))
        base.alpha_composite(s, (int(round(cx - s.width / 2)), int(round(cy - s.height / 2))))
        base.alpha_composite(big, (int(round(cx - s.width / 2)), int(round(cy - s.height / 2))))
    else:
        base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def hand(k=1, lift=None, nowords=False, names=('Brace', 'Spin3', 'Trigger', 'Twist')):
    X0, Y0, X1, Y1 = 800, 690, 1700, 1080
    bg = Image.open(BG).convert('RGBA').crop((X0, Y0, X1, Y1))
    if k != 1:
        bg = bg.resize((bg.width * k, bg.height * k), Image.LANCZOS)
    n = len(names)
    hov = names.index(lift) if lift else None
    for i, nm in enumerate(names):
        a = (i - (n - 1) / 2) * -4.0
        th = math.radians(a)
        cx = 962 + i * 182 + (30 if (hov is not None and i > hov) else 0)
        cy = 910 + 905.0 * th * th
        if i == hov:
            continue
        im = C.draw_card(nm, cw() * k, dict(mode='normal', dim=0.88, nowords=nowords))
        put(bg, im, (cx - X0) * k, (cy - Y0) * k, a, k)
    if hov is not None:
        im = C.draw_card(names[hov], int(cw() * 1.10) * k, dict(mode='hover', nowords=nowords))
        put(bg, im, (962 + hov * 182 - X0) * k, (856 - Y0) * k, 0, k, off=(6, 12), blur=10)
    return bg


def lab(d, xy, s, px=22, fill=(240, 236, 224), font='Anton-Regular.ttf', anchor='la'):
    d.text(xy, s, font=F(px, font), fill=fill, anchor=anchor)


def sheet():
    t = time.time()
    states = [('normal', dict(mode='normal'), 1.0), ('hovered / lifted (1.10 x)', dict(mode='hover'), 1.10),
              ('played (liner)', dict(mode='played'), 1.0), ('unaffordable (dim glass)', dict(mode='unaffordable'), 1.0),
              ('nowords', dict(mode='normal', nowords=True), 1.0)]
    base_w = cw()
    marg = C.margin_px(base_w)
    cell_w, cell_h = base_w + 2 * marg + 8, int(250 * SCALE) + 2 * marg + 8
    LW, TH = 230, 90
    W = LW + cell_w * len(C.ORDER) + 20
    H = TH + (cell_h + 30) * len(states) + 150
    im = Image.new('RGB', (W, H), (36, 30, 48))
    d = ImageDraw.Draw(im)
    lab(d, (24, 14), 'SHIFTING WAVES: the 11 cards, 5 states (WPAP card, band art from the other punk styles, recoloured xerox icon)', 34)
    lab(d, (24, 56), 'TOWER band = teal  |  WAVE band = violet  |  cards drawn at 1.15 x (202 px wide); the lifted card at 1.10 x that', 17, fill=(190, 184, 206), font='ShareTechMono-Regular.ttf')
    for r, (sn, st, k) in enumerate(states):
        y0 = TH + r * (cell_h + 30)
        lab(d, (24, y0 + 10), sn.upper(), 22)
        for c, nm in enumerate(C.ORDER):
            card = C.draw_card(nm, int(round(base_w * k)), st).convert('RGBA')
            x0 = LW + c * cell_w
            cx = x0 + cell_w // 2
            cy = y0 + 10 + cell_h // 2
            tmp = Image.new('RGBA', im.size, (0, 0, 0, 0))
            im.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), card)
    # the "in hand at rest" dim reference: a thin strip of the 88 percent value on the last rows is shown in hand_p1.jpg
    # footer legend: style per card
    yf = TH + len(states) * (cell_h + 30) + 6
    lab(d, (24, yf), 'BAND ART PER CARD', 22)
    xs = 24
    for i, nm in enumerate(C.ORDER):
        A = C.ART[nm]
        lab(d, (24 + (i % 4) * 560, yf + 34 + (i // 4) * 30), '%s: %s' % (C.CARDS[nm]['nm'], A['style']), 20, font='ShareTechMono-Regular.ttf')
    im.save(OUT + 'card_sheet.jpg', quality=92)
    print('sheet', im.size, round(time.time() - t, 1))


def handsheet():
    t = time.time()
    h1 = hand(1)
    h2 = hand(2)
    hl = hand(1, lift='Trigger')
    W = h2.width
    H = 100 + h1.height + 40 + h2.height + 20
    im = Image.new('RGB', (W, H), (30, 26, 40))
    d = ImageDraw.Draw(im)
    lab(d, (20, 12), 'P1 HAND on the bio cutaway: Brace / Spin 3 / Trigger / Twist (decide beat). 1x = real 1920x1080 pixels; 2x below.', 24)
    lab(d, (20, 62), '1x   decide beat (all four at 88 percent value)', 20)
    lab(d, (940, 62), '1x   Trigger lifted (1.10 x, full value, pink print, the rest pushed 30 px)', 20)
    y = 96
    im.paste(h1.convert('RGB'), (0, y)); im.paste(hl.convert('RGB'), (900, y)); y += h1.height + 10
    lab(d, (20, y), '2x', 22); y += 30
    im.paste(h2.convert('RGB'), (0, y))
    im.save(OUT + 'hand_p1.jpg', quality=92)
    # legibility strip: true 1x pixels and 320 px wide
    h1c = h1.convert('RGB').crop((60, 20, 860, 340))
    s320 = h1c.resize((320, int(320 * h1c.height / h1c.width)), Image.LANCZOS)
    nw = hand(1, nowords=True).convert('RGB').crop((60, 20, 860, 340))
    W2 = max(h1c.width, 700)
    L = Image.new('RGB', (W2 + 360, h1c.height + 80), (30, 26, 40))
    d = ImageDraw.Draw(L)
    lab(d, (14, 8), 'LEGIBILITY: 1x pixels (left) and the same hand at 320 px wide (right, true pixels)', 22)
    L.paste(h1c, (0, 50))
    L.paste(s320, (W2 + 20, 50))
    L.paste(nw.resize((320, int(320 * nw.height / nw.width)), Image.LANCZOS), (W2 + 20, 60 + s320.height))
    L.save(OUT + 'legibility_1x_320.jpg', quality=92)
    print('hand', round(time.time() - t, 1))


def checks():
    out = {}
    # title rule numbers
    cap_ratio = 0.86
    T = {}
    for nm in C.ORDER:
        s = C.CARDS[nm]['nm']
        px = C._fit_title(s)
        T[nm] = dict(name=s, px=round(px, 2), width=round(C.text_w(s, C.ANTON, px, 1.0), 1), cap_design=round(px * cap_ratio, 1), cap_1p15=round(px * cap_ratio * 1.15, 1))
    out['titles'] = T
    r = C.ratio
    out['title_fill_vs_keyline'] = round(r(C.WHITE, C.INK), 1)
    out['title_keyline_vs_paper'] = round(r(C.INK, C.CREAM), 1)
    out['title_plate_vs_paper'] = round(r(C.INK, C.CREAM), 1)
    out['rules_ink_vs_paper'] = round(r(C.INK, C.CREAM), 1)
    out['type_text_vs_plate'] = {k: round(r(v['text'], v['col']), 1) for k, v in C.TYPES.items()}
    out['type_plate_vs_paper'] = {k: round(r(v['col'], C.CREAM), 1) for k, v in C.TYPES.items()}
    out['tower_vs_wave'] = round(r(C.TYPES['TOWER']['col'], C.TYPES['WAVE']['col']), 2)
    # icon: measured from the render (disc vs the art around it, glyph vs disc)
    ic = {}
    for nm in C.ORDER:
        A = C.ART[nm]
        card = C.draw_card(nm, 176 * 4, 'normal')
        s = 4.0
        mg = C.MARGIN
        arr = np.asarray(card.convert('RGB')).astype(np.float32) / 255.0
        cx, cy = (C.IC[0] + mg) * s, (C.IC[1] + mg) * s
        yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
        rr = np.hypot(xx - cx, yy - cy) / s
        def avg(lo, hi):
            m = (rr >= lo) & (rr < hi)
            m &= (yy < (126 + mg) * s) & (yy > (10 + mg) * s) & (xx < (CW_ := (176 - 10 + mg) * s))
            return arr[m].mean(0)
        around = avg(41.0, 47.0)
        disc = C.hx(A['disc'])
        ic[nm] = dict(disc_vs_around=round(r(disc, around), 2), halo_vs_around=round(r(C.WHITE, around), 2), glyph_vs_disc=round(r(C.WHITE, disc), 2),
                      disc_vs_halo=round(r(disc, C.WHITE), 2), keyline_vs_halo=round(r(C.INK, C.WHITE), 1), around_rgb=[int(v * 255) for v in around], disc_hex=A['disc'])
    out['icon'] = ic
    json.dump(out, open(WORK + 'checks.json', 'w'), indent=1)
    print(json.dumps(out, indent=1)[:3000])


def key():
    t = time.time()
    W, H = 2200, 1580
    im = Image.new('RGB', (W, H), (36, 30, 48))
    d = ImageDraw.Draw(im)
    lab(d, (30, 20), 'TYPE BAND KEY: the colour behind each card type', 44)
    lab(d, (30, 76), 'The state names two card types for Shifting Waves, TOWER (acts on the tower) and WAVE (acts on the enemy rings). Each owns one band colour; nothing else on a card uses it as a type signal.', 19, font='IBMPlexSansCondensed-Medium.ttf', fill=(200, 194, 214))
    # two big plates
    for i, fam in enumerate(('TOWER', 'WAVE')):
        T = C.TYPES[fam]
        x0 = 40 + i * 1060
        d.rounded_rectangle([x0, 120, x0 + 1000, 300], 14, fill=(244, 238, 224))
        pl = Image.new('RGBA', (1000, 180), (0, 0, 0, 0))
        dd = ImageDraw.Draw(pl)
        col = tuple(int(v * 255) for v in T['col'])
        dd.polygon([(180, 40), (820, 28), (800, 150), (160, 160)], fill=(21, 18, 26))
        dd.polygon([(190, 50), (812, 40), (792, 138), (172, 148)], fill=col)
        im.paste(pl, (x0, 120), pl)
        d.text((x0 + 490, 214), fam, font=F(92), fill=(21, 18, 26), anchor='mm')
        hexs = '#%02X%02X%02X' % tuple(int(v * 255) for v in T['col'])
        cards = [n for n in C.ORDER if C.CARDS[n]['fam'] == fam]
        lab(d, (x0, 312), '%s  %s   ink text on plate %.1f:1   plate on paper %.1f:1' % (fam, hexs, C.ratio(T['text'], T['col']), C.ratio(T['col'], C.CREAM)), 22, font='ShareTechMono-Regular.ttf')
        lab(d, (x0, 346), 'cards: ' + ', '.join(C.CARDS[n]['nm'] for n in cards), 22, font='ShareTechMono-Regular.ttf')
    # card rows under each plate
    for i, fam in enumerate(('TOWER', 'WAVE')):
        x0 = 40 + i * 1060
        cards = [n for n in C.ORDER if C.CARDS[n]['fam'] == fam]
        w = 142
        for j, n in enumerate(cards):
            card = C.draw_card(n, w, 'normal')
            xx = x0 + (j % 6) * (w + 24 + 6)
            yy = 400 + (j // 6) * 270
            im.paste(card, (xx, yy), card)
    # where the type colour shows on a card (annotated big card)
    big = C.draw_card('Spin3', 340, 'normal')
    big2 = C.draw_card('Twist', 340, 'normal')
    yb = 800
    im.paste(big, (60, yb), big); im.paste(big2, (460, yb), big2)
    lab(d, (860, yb + 10), 'Where the type colour sits on a card (three places, always together)', 26)
    notes = ['1  the type plate under the title (the word TOWER / WAVE, ink on colour)',
             '2  a thin rule along the top edge of the title plate',
             '3  the corner facet at the bottom left of the paper',
             '(Spin cards also carry the multiplier plate in TOWER teal)',
             '',
             'Why these two hues: teal and violet are the only cool pair not already owned.',
             'Pink = owner (cost-free, never a type).  Cyan coin = RAM cost.  Yellow = plan marks.',
             'Orange = the rings schedule.  Red = harm.  Green = HP / Solace.  So no type uses them.',
             'Both plates are light so ink text reads (>= 7:1) and the plates stay apart from each other',
             'in grey (see the ratio line above) and on the paper (ink keyline, hard drop).',
             '',
             'RESERVED: if build adds a third type, use cobalt #2F5BFF (white text) or bone #F1EAD6 (ink text).',
             'Do not use pink, yellow, orange, red or green.']
    for k, s in enumerate(notes):
        lab(d, (860, yb + 56 + k * 30), s, 21, font='IBMPlexSansCondensed-Medium.ttf')
    # style legend across the bottom
    yl = 1530
    lab(d, (60, yl), 'BAND ART STYLE (not a type signal): ' + '   '.join('%s = %s' % (k, ', '.join(C.CARDS[n]['nm'] for n in C.ORDER if C.ART[n]['style'] == k)) for k in ('benday', 'linocut', 'collage', 'mural', 'xerox', 'jinx')), 17, font='ShareTechMono-Regular.ttf')
    im.save(OUT + 'type_band_key.jpg', quality=92)
    print('key', round(time.time() - t, 1))


if __name__ == '__main__':
    w = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if w in ('checks', 'all'): checks()
    if w in ('hand', 'all'): handsheet()
    if w in ('key', 'all'): key()
    if w in ('sheet', 'all'): sheet()
