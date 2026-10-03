"""interchanges.png (close-ups of the interchanges, night + day) and storyboard_ambient_v2.png."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw

import cm

BG = (16, 15, 20)
INK = (236, 228, 210)
DIM = (150, 144, 160)
LIME = (212, 255, 0)

# crop boxes in out px (1x) -> taken from the 2x composite
STACK = (110, 290, 430, 520)
CLOVER = (220, 0, 520, 190)
SPIRAL = (585, 100, 745, 225)


def crop2(img2, box, w):
    c = img2.crop(tuple(v * cm.SS for v in box))
    return c.resize((w, int(w * c.height / c.width)), Image.LANCZOS)


def _wrap(d, xy, text, f, col, w):
    x, y = xy
    line = ''
    for word in text.split(' '):
        t = (line + ' ' + word).strip()
        if d.textlength(t, font=f) > w - 4:
            d.text((x, y), line, font=f, fill=col)
            y += 18
            line = word
        else:
            line = t
    if line:
        d.text((x, y), line, font=f, fill=col)
    return y + 18


def interchanges():
    opts = dict(fog=False, rain=False, steam=False, tilt=False, labels=False, hires=True)
    hn = cm.Scene('night').frame(14, 48, opts=opts)
    hd = cm.Scene('day').frame(14, 48, opts=opts)
    pad, W1 = 24, 1100
    W2 = 520
    panels = [
        ('A  FOUR-LEVEL STACK  (D x E, beside Orbital)', STACK,
         'D (orange rails, deck 20) runs under E (cyan, deck 40). Four directional flyover ramps, one per quadrant: '
         'two at 62 px (amber rails, tight radius) and two at 84 px (pink rails, wide radius) arch over both, so four '
         'levels of traffic cross in one spot. Ramps are one-way, two lanes. Pylons are depth-tested against the '
         'towers.'),
        ('B  CLOVERLEAF  (A x F, north Sprawl)', CLOVER,
         'F (violet rails, deck 44) flies over A\'s double deck (18 / 34). Four 270-degree loop ramps climb from A\'s '
         'lower deck up to F, each tangent to both avenues. Traffic flows round the loops one-way.'),
    ]
    rows = []
    for title, box, note in panels:
        rows.append((title, crop2(hn, box, W1), crop2(hd, box, W2), note))
    sp_n = crop2(hn, SPIRAL, W2)
    sp_d = crop2(hd, SPIRAL, W2)
    H = 110 + sum(r[1].height + 60 for r in rows) + max(sp_n.height, 0) + 90
    sheet = Image.new('RGB', (pad * 3 + W1 + W2, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 20), 'INTERCHANGES  -  round 26 road network', font=cm.font(34), fill=INK)
    d.text((pad, 64), 'Close-ups from the 2x map composite (fog, rain, tilt-shift off). Night left, day right. Every road '
                      'sits on a real avenue of city_layout.json.', font=cm.font(16, False), fill=DIM)
    y = 110
    for title, n_im, d_im, note in rows:
        d.text((pad, y), title, font=cm.font(20), fill=LIME)
        sheet.paste(n_im, (pad, y + 30))
        sheet.paste(d_im, (pad * 2 + W1, y + 30))
        _wrap(d, (pad * 2 + W1, y + 40 + d_im.height), note, cm.font(14, False), DIM, W2)
        y += n_im.height + 60
    d.text((pad, y), 'C  SPIRAL RAMP  (end of C, east Sprawl)  +  FLYOVER CROSSINGS', font=cm.font(20), fill=LIME)
    sheet.paste(sp_n, (pad, y + 30))
    sheet.paste(sp_d, (pad * 2 + W2, y + 30))
    _wrap(d, (pad * 3 + 2 * W2, y + 30),
          'C (mint rails, deck 26) leaves the grid down a 1.75-turn spiral round a core column to street level, '
          'one-way down. On its way C passes UNDER B (52) and UNDER F (44): three decks crossing at three heights.',
          cm.font(14, False), DIM, sheet.width - (pad * 4 + 2 * W2))
    sheet = sheet.crop((0, 0, sheet.width, y + 40 + sp_n.height))
    sheet.save(os.path.join(cm.ROOT, 'interchanges.png'), optimize=True)
    print('interchanges', sheet.size)


def storyboard():
    PW, PH = 640, 360
    pad = 24
    rows = []
    for th in ('night', 'day'):
        s = cm.Scene(th)
        rows.append((th, [s.frame(f, 48) for f in (0, 16, 32)]))
    W = 3 * PW + 4 * pad
    H = 100 + 2 * (PH + 50) + 230
    sh = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sh)
    d.text((pad, 20), 'CITY AMBIENT v2  -  more highways + interchanges on the v3 map', font=cm.font(32), fill=INK)
    d.text((pad, 62), 'city_ambient_night_v2.gif / city_ambient_day_v2.gif  -  960x540, 48 frames x 80 ms = 3.84 s '
                      'seamless loop. Motion layers as locked in round 24.', font=cm.font(16, False), fill=DIM)
    y = 100
    for th, ims in rows:
        for n, im in enumerate(ims):
            x = pad + n * (PW + pad)
            sh.paste(im.resize((PW, PH), Image.LANCZOS), (x, y))
            d.text((x, y + PH + 8), '%s  f%d  /  %.2f s' % (th.upper(), (0, 16, 32)[n], (0, 16, 32)[n] * 0.08),
                   font=cm.font(16), fill=LIME)
        y += PH + 50
    notes = [
        'ROADS  A double deck (j=4) and B (i=6) as round 24; new C (j=-5, deck 26), F (i=-10, deck 44), D (j=43, deck 20), '
        'E (i=17, deck 40). 7 decks + 4 cloverleaf loops + 4 stack ramps + 1 spiral = 16 one- or two-way roads.',
        'TIMING  every lane moves 2-4 car gaps per 3.84 s loop (car spacing 13-20 px / density), so each lane loops '
        'seamlessly; ramps and loops are one-way two-lane, highways two-way four-lane (headlights one way, tail lights '
        'the other at night).',
        'ORDER  decks are painted low to high, back to front; each deck draws its own cars, so upper levels hide lower '
        'traffic, and glow is added only where a deck is the top one. Pylons hide behind towers.',
        'BASE  night = round 25 city_night_hq_v3 (new HQs). Day = round 6 day map, with the v3 changes (new HQs, cleared '
        'fist roads) graded night -> day from round 6\'s own night/day pair (scripts/bases.py) until a true v3 day map exists.',
    ]
    yy = y
    for t in notes:
        yy = _wrap(d, (pad, yy), t, cm.font(15, False), DIM, W - 2 * pad) + 6
    sh.save(os.path.join(cm.ROOT, 'storyboard_ambient_v2.png'), optimize=True)
    print('storyboard', sh.size)


if __name__ == '__main__':
    w = sys.argv[1:] or ['inter', 'story']
    if w == ['inter2']:
        w = []
    if 'inter' in w:
        interchanges()
    if 'story' in w:
        storyboard()


def interchanges_v2():
    """interchanges_v2.png: the same three close-ups with the v3 sky lanes (no decks)."""
    import roads
    roads.Network.sky = True
    opts = dict(fog=False, rain=False, steam=False, tilt=False, labels=False, hires=True)
    sn, sd = cm.Scene('night'), cm.Scene('day')
    pad, W1, W2 = 24, 1100, 520
    rows = []
    for title, box, note in (
            ('A  FOUR-LEVEL STACK  (D x E, beside Orbital)', STACK,
             'The stack as sky lanes: D (orange) and E (cyan) cross, four directional ramps arch over at two more '
             'heights (amber, pink). Only cars, light streaks and faint lane-guide dots: no deck, rail or pylon.'),
            ('B  CLOVERLEAF  (A x F, north Sprawl)', CLOVER,
             'Four 270-degree loops trace between A (pink/cyan) and F (violet). Two-way lanes have a guide-dot row '
             'on each edge; one-way ramps a single centre row in the ramp colour.')):
        n_im = crop2(sn.frame(14, 48, opts=opts), box, W1)
        n2 = crop2(sn.frame(15, 48, opts=opts), box, W1)
        rows.append((title, n_im, crop2(sd.frame(14, 48, opts=opts), box, W2), crop2(sd.frame(15, 48, opts=opts), box, W2), note))
    sp = [crop2(sn.frame(14, 48, opts=opts), SPIRAL, W2), crop2(sd.frame(14, 48, opts=opts), SPIRAL, W2)]
    H = 120 + sum(r[1].height + 60 for r in rows) + sp[0].height + 80
    sheet = Image.new('RGB', (pad * 3 + W1 + W2, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 20), 'INTERCHANGES v2  -  sky lanes (no road surface)', font=cm.font(34), fill=INK)
    d.text((pad, 64), 'Same locked shapes as interchanges.png. Highway traffic about 6x faster (14-20 car gaps per 3.84 s '
                      'loop, was 2-4); street traffic unchanged. Night left, day right; 2x composite, fog/tilt off.',
           font=cm.font(16, False), fill=DIM)
    y = 120
    for title, n_im, d_im, d2, note in rows:
        d.text((pad, y), title, font=cm.font(20), fill=LIME)
        sheet.paste(n_im, (pad, y + 30))
        sheet.paste(d_im, (pad * 2 + W1, y + 30))
        _wrap(d, (pad * 2 + W1, y + 40 + d_im.height), note, cm.font(14, False), DIM, W2)
        y += n_im.height + 60
    d.text((pad, y), 'C  SPIRAL + FLYOVERS AT THREE HEIGHTS', font=cm.font(20), fill=LIME)
    sheet.paste(sp[0], (pad, y + 30))
    sheet.paste(sp[1], (pad * 2 + W2, y + 30))
    _wrap(d, (pad * 3 + 2 * W2, y + 30), 'C spirals down 1.75 turns to street level as a one-way lane of mint streaks; '
          'it crosses under B and F, each lane drawn in height order so the higher streaks pass over.',
          cm.font(14, False), DIM, sheet.width - (pad * 4 + 2 * W2))
    sheet = sheet.crop((0, 0, sheet.width, y + 40 + sp[0].height))
    sheet.save(os.path.join(cm.ROOT, 'interchanges_v2.png'), optimize=True)
    print('interchanges_v2', sheet.size)


if __name__ == '__main__' and 'inter2' in sys.argv[1:]:
    interchanges_v2()
