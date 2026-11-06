"""grammar_check: roadmap step 3, the time / HP grammar on the final skins (neutral, Solace, Meridian).
python grammar_check.py  ->  locked/final/grammar_check.jpg + corp/work/grammar_check.json
Zoomed crops from the final plates: HOT/COLD/FAR (ring tags + the sector-3 chevron column + the rim landing marks), the pending-loss
hatch (tower slices, every slice colour, the enemy HP trays, and red / pink / blue hatch swatches laid on each skin's own ring cell),
the arrowed movement outline and the enemy outline (p2b).  Numbers: luma contrast and dE2000 of each mark against what is behind it."""
import sys, os, json, copy, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
FD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/'
an = lambda px: ImageFont.truetype(FD + 'Anton-Regular.ttf', px)
mo = lambda px: ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', px)
CC = (536, 540)
SKINS = [('neutral', ''), ('solace', '_solace'), ('meridian', '_meridian')]
RINGS = [(214, 271), (271, 328), (328, 385)]
HARM = (255, 68, 51)
PINK = (255, 61, 168)
SOAK = (58, 126, 243)
INK = (12, 10, 22)


def rgb2lab(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def de(a, b):
    import de_kinds as DK
    return DK.de2000(rgb2lab(a), rgb2lab(b))


def rl(c):
    c = np.asarray(c, np.float64) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def cr(a, b):
    la, lb = rl(a), rl(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def hsv(a):
    mx, mn = a.max(2), a.min(2)
    s = (mx - mn) / np.maximum(mx, 1)
    dd = np.maximum(mx - mn, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return h, s, mx / 255.0


Y, X = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(X - CC[0], Y - CC[1])
ANG = np.degrees(np.arctan2(X - CC[0], -(Y - CC[1]))) % 360


def chev_cols():
    import f1_board as FB
    return [(255, 100, 82), FB.COLD_CHEV, FB.FAR_CHEV]


def chevron_read(a, ang=180.0):
    """median chevron colour and median cell colour per ring in the sector column at `ang`.  Chevron pixels = within RGB distance 40
    of the ring's graded harm colour (HOT HARM_UP, COLD #D9877C, FAR f1_board.FAR_CHEV); cell = the band beside the column."""
    exp = chev_cols()
    out = []
    for d, (r0, r1) in enumerate(RINGS):
        band = (RHO > r0 + 4) & (RHO < r1 - 4)
        da = np.abs(((ANG - ang + 180) % 360) - 180)
        col = band & (da < 5.5)
        dist = np.sqrt(((a - np.array(exp[d], np.float32)) ** 2).sum(2))
        chev = col & (dist < 40)
        side = band & (da > 12) & (da < 20) & (dist > 60)
        if chev.sum() < 10 or side.sum() < 10:
            out.append(dict(ring=d, grammar=('HOT', 'COLD', 'FAR')[d], found_px=int(chev.sum()), note='no chevron of the expected colour found in this column'))
            continue
        cc = np.median(a[chev], 0)
        bg = np.median(a[side], 0)
        out.append(dict(ring=d, grammar=('HOT', 'COLD', 'FAR')[d], chevron_rgb=[int(x) for x in cc], cell_rgb=[int(x) for x in bg],
                        luma_contrast=round(cr(cc, bg), 2), dE2000=round(de(cc, bg), 1), px=int(chev.sum())))
    return out


def hatch_swatch(bg, cols, pitch=6.4, w=1.6, k=3):
    """lay the pending-loss cross-hatch (the tower's parameters: 45/135 deg, pitch 6.4, line 1.6, ink keyline 0.85) over a cell crop"""
    W, H = bg.size
    out = []
    for c in cols:
        big = bg.resize((W * k, H * k), Image.NEAREST).convert('RGBA')
        m = Image.new('L', big.size, 0)
        d = ImageDraw.Draw(m)
        mk = Image.new('L', big.size, 0)
        dk = ImageDraw.Draw(mk)
        L = W + H
        t = -L
        while t < L:
            for (p0, p1) in (((t * k, 0), ((t + H) * k, H * k)), ((t * k, H * k), ((t + H) * k, 0))):
                dk.line([p0, p1], fill=255, width=int((w + 1.7) * k))
                d.line([p0, p1], fill=255, width=int(w * k))
            t += pitch
        ink = Image.new('RGBA', big.size, INK + (255,))
        ink.putalpha(mk.point(lambda v: int(v * 0.92)))
        big.alpha_composite(ink)
        hc = Image.new('RGBA', big.size, c + (255,))
        hc.putalpha(m)
        big.alpha_composite(hc)
        out.append(big.resize((W, H), Image.LANCZOS).convert('RGB'))
    return out


def tower_all_hatched():
    """the locked tower with every slice type pending loss (sector 4 soaked = blue hatch): player layer, identical on every corp skin"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lw_render as LW
    import lw_tower as LT
    A = LW.R.A
    f = copy.deepcopy(A.J['f1'])
    types = ['BURST', 'SHIELD', 'TURRET', 'REPAIR', 'BURST', 'REPAIR']
    for i, w in enumerate(f['wheel']):
        w['t'] = types[i]
        w['hp'], w['hp_after'] = 2, 0
        w['soaked'] = 1 if i in (4, 5) else 0
        w['brace'] = w['soak'] = False
    tw, cv = LT.render_tower(f, with_trim=False)
    fills = {t: [int(v * 255 * LT.FILL_K) for v in LT.XS.palette('A', t)[0]] for t in ('BURST', 'SHIELD', 'TURRET', 'REPAIR')}
    return tw, fills, types


def main():
    rep = {}
    plates = {n: Image.open(FINAL + 'p1_decide%s.png' % s).convert('RGB') for n, s in SKINS}
    hov = {n: Image.open(FINAL + 'p2b_hover%s.png' % s).convert('RGB') for n, s in SKINS}
    # ---------------- numbers
    rep['chevrons_sector3'] = {n: chevron_read(np.asarray(im, np.float32)) for n, im in plates.items()}
    rep['chevrons_sector0'] = {n: chevron_read(np.asarray(im, np.float32), 0.0) for n, im in plates.items()}
    cellbox = (300, 236, 352, 276)            # a flat stretch of ring 2 cell (top left), same place on every skin
    rep['hatch_on_cell'] = {}
    for n, im in plates.items():
        bgc = np.median(np.asarray(im.crop(cellbox), np.float32).reshape(-1, 3), 0)
        rep['hatch_on_cell'][n] = dict(cell_rgb=[int(v) for v in bgc], **{k: dict(luma_contrast=round(cr(c, bgc), 2), dE2000=round(de(c, bgc), 1), vs_ink_keyline=round(cr(c, INK), 2))
                                                                          for k, c in (('red_HARM', HARM), ('pink_ours', PINK), ('blue_soak', SOAK))})
    tw, fills, types = tower_all_hatched()
    rep['hatch_on_slices'] = {t: dict(fill_rgb=fc, red_luma_contrast=round(cr(HARM, fc), 2), red_dE2000=round(de(HARM, fc), 1),
                                      blue_luma_contrast=round(cr(SOAK, fc), 2), blue_dE2000=round(de(SOAK, fc), 1),
                                      note='the hatch always rides on a 0.85 px ink keyline (red vs ink %.1f:1, blue vs ink %.1f:1)' % (cr(HARM, INK), cr(SOAK, INK)))
                              for t, fc in fills.items()}
    json.dump(rep, open(WORK + 'grammar_check.json', 'w'), indent=1)
    # ---------------- sheet
    Z = 2
    crops = [('HOT / COLD / FAR: ring tags + pips', (586, 200, 766, 340), 2, plates),
             ('chevron column, sector 3 (HOT ring 0 > COLD > FAR)', (466, 700, 606, 900), 2, plates),
             ('rim landing marks (outer annulus)', (60, 540, 240, 790), 1.6, plates),
             ('pending loss on the tower (red = enemy hit)', (566, 386, 736, 706), 1.25, plates),
             ('pending loss on enemy trays (pink = our guns)', (262, 372, 402, 482), 2.3, plates),
             ('arrowed outline (movement only, p2b)', (250, 630, 560, 880), 1.03, hov),
             ('enemy outline (p2b hovered unit, p1 cells)', (800, 500, 960, 620), 2.0, hov)]
    sw_w = 330
    cell_w = [int((b[2] - b[0]) * z) for _, b, z, _ in crops] + [sw_w]
    row_h = max(int((b[3] - b[1]) * z) for _, b, z, _ in crops)
    Wt = 170 + sum(cell_w) + 12 * len(cell_w)
    Ht = 120 + (row_h + 60) * 3 + 520
    sheet = Image.new('RGB', (Wt, Ht), (16, 16, 22))
    d = ImageDraw.Draw(sheet)
    d.text((16, 10), 'STEP 3: GRAMMAR ON THE FINAL SKINS (neutral, Solace, Meridian), zoomed crops of the final plates', font=an(40), fill=(255, 255, 255))
    d.text((16, 62), 'HOT = this END TURN (full value, notch, glow) | COLD = +1 (lifted, 1 pip) | FAR = +2 (50 % value, 2 pips) | cross-hatch = HP lost at this END TURN, hatch colour = cause | arrowed outline = movement only',
           font=mo(19), fill=(200, 206, 222))
    for ri, (n, s) in enumerate(SKINS):
        y = 120 + ri * (row_h + 60)
        d.text((16, y + 20), n.upper(), font=an(34), fill=(255, 226, 0))
        x = 170
        for (t, box, z, src) in crops:
            c = src[n].crop(box)
            c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)
            sheet.paste(c, (x, y + 30))
            if ri == 0:
                import textwrap
                for li, line in enumerate(textwrap.wrap(t, max(10, int(c.width / 8.2)))[:2]):
                    d.text((x, y - 22 + li * 17), line, font=mo(15), fill=(220, 220, 230))
            x += c.width + 12
        # hatch swatches on this skin's own ring cell
        bgc = plates[n].crop(cellbox).resize((96, 74), Image.LANCZOS)
        sws = hatch_swatch(bgc, [HARM, PINK, SOAK])
        if ri == 0:
            d.text((x, y - 22), 'hatch swatches on the skin', font=mo(15), fill=(220, 220, 230))
            d.text((x, y - 5), 'cell: red, pink, blue', font=mo(15), fill=(220, 220, 230))
        for k, sw in enumerate(sws):
            sheet.paste(sw.resize((100, 77), Image.LANCZOS), (x + k * 108, y + 30))
        hc = rep['hatch_on_cell'][n]
        d.text((x, y + 116), 'cell %s' % (tuple(hc['cell_rgb']),), font=mo(15), fill=(220, 220, 230))
        for k, key in enumerate(('red_HARM', 'pink_ours', 'blue_soak')):
            d.text((x, y + 136 + k * 20), '%s %.1f:1 dE %.0f' % (key.split('_')[0], hc[key]['luma_contrast'], hc[key]['dE2000']), font=mo(15), fill=(220, 220, 230))
        ch = rep['chevrons_sector3'][n]
        d.text((x, y + 206), 'chevrons vs cell (sector 3):', font=mo(15), fill=(220, 220, 230))
        for k, e in enumerate(ch):
            if e and 'luma_contrast' in e:
                d.text((x, y + 226 + k * 20), '%s %.2f:1 dE %.0f' % (e['grammar'], e['luma_contrast'], e['dE2000']), font=mo(15), fill=(220, 220, 230))
    # bottom row: every slice colour hatched
    y = 120 + 3 * (row_h + 60) + 10
    d.text((16, y), 'PENDING-LOSS HATCH ON EVERY SLICE COLOUR (player layer: the same on every corp skin). Red = enemy hit, blue = soaked (sectors 4, 5).', font=an(26), fill=(255, 255, 255))
    bg = Image.new('RGBA', tw.size, (22, 24, 30, 255))
    bg.alpha_composite(tw)
    bg = bg.convert('RGB').resize((int(tw.width * 1.15), int(tw.height * 1.15)), Image.LANCZOS)
    sheet.paste(bg, (170, y + 44))
    xx = 170 + bg.width + 30
    for k, (t, e) in enumerate(rep['hatch_on_slices'].items()):
        d.text((xx, y + 60 + k * 32), '%-7s fill %s  red %.2f:1 dE %.0f  blue %.2f:1 dE %.0f' % (t, tuple(e['fill_rgb']), e['red_luma_contrast'], e['red_dE2000'], e['blue_luma_contrast'], e['blue_dE2000']),
               font=mo(20), fill=(230, 230, 236))
    d.text((xx, y + 60 + 4 * 32 + 10), 'Every hatch line sits on an ink keyline, so it separates from any slice ink by the keyline even where the hue is close.', font=mo(18), fill=(200, 206, 222))
    d.text((xx, y + 60 + 5 * 32 + 10), 'The O-28 seat ring keeps the slice type readable under the hatch.', font=mo(18), fill=(200, 206, 222))
    sheet = sheet.crop((0, 0, Wt, y + 44 + bg.height + 20))
    sheet.save(FINAL + 'grammar_check.jpg', quality=90)
    print(json.dumps({k: v for k, v in rep.items() if k != 'hatch_on_slices'}, indent=1)[:4000])
    print(json.dumps(rep['hatch_on_slices'], indent=1))


if __name__ == '__main__':
    main()
