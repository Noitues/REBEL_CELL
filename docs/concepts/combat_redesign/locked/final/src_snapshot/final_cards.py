"""final_cards: the card sheet and the card numbers (2026-11-03 rebuild against the AD review: 2.2, 3.1, 3.2, 3.3).
python final_cards.py [sheet|checks|de|all]
  sheet   -> locked/final/card_sheet.jpg  (11 cards x 7 states)
  checks  -> corp/work/card_checks.json   (type word contrast, titles, spin arcs, icon discs)
  de      -> rebuild/cards/de.json         (CIE76 dE table of the type plates and the Spin 3 band against every meaning token and slice ink,
                                             plus L* and word contrast measured on the published card_sheet.jpg)
Cards come from card_render.draw_card (same module the plates use).  In-hand scale is f1_hand.CARD_SCALE (1.10).
The sheet geometry (LW 250, TH 120, cell size, row 0 = normal) is read by final_checks.py for grey_proof.jpg: keep it."""
import sys, os, json, time, re
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import card_render as C

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
DE_OUT = 'D:/rc_scratch/combat_redesign/locked/rebuild/cards/de.json'
FD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/'
SCALE = 1.10
os.makedirs(FINAL, exist_ok=True)

STATES = [('normal (full value)', dict(mode='normal'), 1.0),
          ('resting in hand (dim 0.88)', dict(mode='normal', dim=0.88), 1.0),
          ('lifted / hover (1.10 x)', dict(mode='hover'), 1.10),
          ('played slot (name + PLAYED)', dict(mode='played'), 1.0),
          ('unaffordable (glass + lock + NO RAM)', dict(mode='unaffordable'), 1.0),
          ('nowords', dict(mode='normal', nowords=True), 1.0),
          ('unaffordable, nowords (lock)', dict(mode='unaffordable', nowords=True), 1.0)]
LW, TH = 250, 120


def F(px, name='Anton-Regular.ttf'):
    return ImageFont.truetype(FD + name, px)


def hexs(c):
    return '#%02X%02X%02X' % tuple(int(round(float(v) * 255)) for v in c)


def geom():
    base_w = int(round(176 * SCALE * 1.5))          # the sheet shows the cards at 1.5 x their in-hand size
    marg = C.margin_px(int(base_w * 1.1))
    cell_w, cell_h = int(base_w * 1.1) + 2 * marg + 6, int(250 * base_w / 176 * 1.1) + 2 * marg + 6
    return base_w, cell_w, cell_h


def sheet():
    t = time.time()
    base_w, cell_w, cell_h = geom()
    W = LW + cell_w * len(C.ORDER) + 20
    H = TH + (cell_h + 20) * len(STATES) + 40
    im = Image.new('RGB', (W, H), (38, 42, 54))
    d = ImageDraw.Draw(im)
    T, Wv = C.TYPES['TOWER'], C.TYPES['WAVE']
    d.text((24, 14), 'SHIFTING WAVES: the 11 WPAP cards, 7 states (2026-11-03 rebuild: AD review 2.2, 3.1, 3.2, 3.3)', font=F(40), fill=(250, 248, 240))
    d.text((24, 66), 'TOWER %s (white word) | WAVE %s (ink word) | Spin 3 band %s | all at dE76 >= 15 from the meaning tokens and slice inks | '
           'HOLD = clamp on a ring step | FIREWALL = wall on fire, TWIST = turned ring | cards at 1.5 x the 1.10 x in-hand size'
           % (hexs(T['col']), hexs(Wv['col']), '#' + C.ART['Spin3']['bg']), font=F(19, 'ShareTechMono-Regular.ttf'), fill=(200, 206, 222))
    for r, (sn, st, k) in enumerate(STATES):
        y0 = TH + r * (cell_h + 20)
        words = sn.upper().split(' (')
        d.text((20, y0 + 20), words[0], font=F(24), fill=(240, 236, 224))
        if len(words) > 1:
            d.text((20, y0 + 56), '(' + words[1].lower(), font=F(17, 'ShareTechMono-Regular.ttf'), fill=(190, 196, 212))
        for c, nm in enumerate(C.ORDER):
            card = C.draw_card(nm, int(round(base_w * k)), dict(st)).convert('RGBA')
            cx = LW + c * cell_w + cell_w // 2
            cy = y0 + cell_h // 2
            im.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), card)
    im.save(FINAL + 'card_sheet.jpg', quality=92)
    print('sheet', im.size, round(time.time() - t, 1), flush=True)


def _no_ram_fit():
    """the NO RAM word's ink box against its tab and the +Trace tab (design px, measured on a 4x mask)"""
    cv = C.Cv(4.0)
    x0, x1, y0, y1 = C.NO_RAM_TAB
    m = C.text(cv, C.NO_RAM, C.no_ram_cx(), (y0 + y1) / 2, C.NO_RAM_PX, C.ANTON, C.NO_RAM_TRACK, 0.0, -1.5)
    ys, xs = np.where(m > 0.5)
    ink = [float(v) for v in (xs.min() / cv.R - C.MARGIN, xs.max() / cv.R - C.MARGIN, ys.min() / cv.R - C.MARGIN, ys.max() / cv.R - C.MARGIN)]
    lx = C.CW - 54
    gap_top = (lx - 21 - 2.4) - (x1 + 1.8)                     # +Trace plate top-left (minus keyline) vs NO RAM top-right (plus keyline)
    gap_bottom = (lx - 18 - 2.4) - (x1 + 2.0 + 1.8 + 2.2)      # bottom corners, with the NO RAM slant and hard drop
    vx0 = C.NO_RAM_VIS_X0
    return dict(ink_box=[round(v, 1) for v in ink], tab=[x0, x1, y0, y1], visible_from_x=vx0,
                ink_margin_left=round(ink[0] - vx0, 1), ink_margin_right=round(x1 - ink[1], 1),
                fits_tab=bool(ink[0] >= vx0 + 1.0 and ink[1] <= x1 - 1.0 and ink[2] >= y0 and ink[3] <= y1),
                gap_to_trace_tab=dict(top=round(gap_top, 1), bottom=round(gap_bottom, 1)))


def checks():
    r = C.ratio
    out = {}
    out['type_colours'] = {k: dict(col=hexs(v['col']), text=hexs(v['text']), text_vs_plate=round(r(v['text'], v['col']), 2),
                                   plate_vs_paper=round(r(v['col'], C.CREAM), 2), text_rule='>= 4.5') for k, v in C.TYPES.items()}
    out['tower_vs_wave_grey'] = round(r(C.TYPES['TOWER']['col'], C.TYPES['WAVE']['col']), 2)
    out['trace_tab'] = dict(col=hexs(C.TRACE_VIOLET), white_plus_vs_tab=round(r(C.WHITE, C.TRACE_VIOLET), 2))
    out['facet_opacity'] = dict(type_plane=C.FACET_OP[0], type_dark_plane=C.FACET_OP[1], glint=C.FACET_OP[2], rule='25-35 %')
    cap = 0.86
    out['titles_cap_screen_px_at_1p10'] = {nm: round(C._fit_title(C.CARDS[nm]['nm']) * cap * SCALE, 1) for nm in C.ORDER}
    out['title_fill_vs_keyline'] = round(r(C.WHITE, C.INK), 1)
    out['no_ram_word'] = dict(word=C.NO_RAM, px_design=C.NO_RAM_PX, cap_screen_px_at_1p10=round(C.NO_RAM_PX * cap * SCALE, 1), colour=hexs(C.CYAN_HI),
                              **_no_ram_fit(),
                              word_vs_tab=round(r(C.CYAN_HI, C.hx('1C1830')), 2))
    out['spin_arcs_screen_px'] = dict(stroke=round(3.4 * SCALE, 2), centre_pitch=round(13.0 * SCALE, 2), clear_gap_between_inks=round((13.0 - 3.4) * SCALE, 2),
                                      dot_density=dict(Nudge=C.ART['Nudge']['dot_k'], Spin2=C.ART['Spin2']['dot_k'], Spin3=C.ART['Spin3']['dot_k']),
                                      band=dict(Nudge=C.ART['Nudge']['bg'], Spin2=C.ART['Spin2']['bg'], Spin3=C.ART['Spin3']['bg']))
    ic = {}
    k = 2.0
    for nm in C.ORDER:
        A = C.ART[nm]
        card = C.draw_card(nm, int(176 * k), 'normal')
        arr = np.asarray(card.convert('RGB')).astype(np.float32) / 255.0
        mg = C.MARGIN
        cx, cy = (C.IC[0] + mg) * k, (C.IC[1] + mg) * k
        yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
        rr = np.hypot(xx - cx, yy - cy) / k
        m = (rr >= 41) & (rr < 47) & (yy < (126 + mg) * k) & (yy > (10 + mg) * k) & (xx < (166 + mg) * k)
        around = arr[m].mean(0)
        disc = C.hx(A['disc'])
        ic[nm] = dict(disc=A['disc'], disc_vs_art_around=round(r(disc, around), 2), glyph_vs_disc=round(r(C.WHITE, disc), 2),
                      pass_2p5=bool(r(disc, around) >= 2.5))
        print(nm, ic[nm], flush=True)
    out['icon_disc'] = ic
    out['icon_disc_min'] = min(v['disc_vs_art_around'] for v in ic.values())
    out['icon_disc_all_ge_2p5'] = all(v['pass_2p5'] for v in ic.values())
    json.dump(out, open(WORK + 'card_checks.json', 'w'), indent=1)
    print(json.dumps({k_: v for k_, v in out.items() if k_ != 'icon_disc'}, indent=1))


# ------------------------------------------------------------------ dE table
TOKENS = {'SOAK': '3A7EF3', 'SCHEDULE': 'FF8C1A', 'BOSS_GOLD': 'FFC428', 'TRACE': 'A03CFF', 'NET_CYAN': '5CE1FF',
          'HARM': 'FF4433', 'GAIN': '7BE07B', 'PLAN': 'FFE200'}
OLD = {'TOWER': '2F5BFF', 'WAVE': 'FF8A1F', 'Spin3_band': 'FFD21F'}       # O-29 / O-30 values the review flagged


def _lab(c):
    c = np.asarray(c, np.float64)
    l = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = l @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def de76(a, b):
    return float(np.linalg.norm(_lab(a) - _lab(b)))


def _refs():
    import xf_slices as XS
    fk = float(re.search(r'^FILL_K\s*=\s*([0-9.]+)', open(os.path.dirname(os.path.abspath(__file__)) + '/lw_tower.py').read(), re.M).group(1))
    ref = {k: C.hx(v) for k, v in TOKENS.items()}
    for t, p in XS.PAL['A'].items():
        ref['slice_' + t] = C.hx(p['fill'])
        ref['slice_' + t + '_on_board_x%.2f' % fk] = C.hx(p['fill']) * fk
    return ref, fk


def _measure_sheet():
    """L* and word contrast of the type plates and the Spin 3 band, measured on the published card_sheet.jpg (row 0, normal)"""
    sh = np.asarray(Image.open(FINAL + 'card_sheet.jpg').convert('RGB')).astype(np.float64) / 255.0
    base_w, cell_w, cell_h = geom()
    k = base_w / 176.0
    out = {}
    for c, nm in enumerate(C.ORDER):
        cx = LW + c * cell_w + cell_w // 2
        cy = TH + cell_h // 2
        X0 = cx - (176 / 2) * k; Y0 = cy - (250 / 2) * k                 # card box top-left on the sheet
        fam = C.CARDS[nm]['fam']
        tw = 92 if fam == 'TOWER' else 80
        # plate: a box left of the word, inside the slanted plate
        px0, px1 = 88 - tw / 2 + 2, 88 - tw / 2 + 12
        plate = sh[int(Y0 + 168 * k):int(Y0 + 180 * k), int(X0 + px0 * k):int(X0 + px1 * k)].reshape(-1, 3)
        pc = np.median(plate, 0)
        # word: pixels of the word box that sit far from the plate colour, the darkest or lightest decile
        wb = sh[int(Y0 + 167 * k):int(Y0 + 181 * k), int(X0 + 62 * k):int(X0 + 110 * k)].reshape(-1, 3)
        dd = np.linalg.norm(wb - pc, axis=1)
        far = wb[dd > np.percentile(dd, 80)]
        wc = np.median(far, 0)
        row = dict(type=fam, plate_rgb_measured=hexs(pc), plate_Lstar=round(float(_lab(pc)[0]), 1), word_rgb_measured=hexs(wc),
                   word_Lstar=round(float(_lab(wc)[0]), 1), word_vs_plate_measured=round(C.ratio(wc, pc), 2))
        if nm == 'Spin3':
            # the band ink as printed: the most common colour (16-level bins) in the art band outside the icon halo
            yy, xx = np.mgrid[int(Y0 + 12 * k):int(Y0 + 122 * k), int(X0 + 12 * k):int(X0 + 164 * k)]
            m = np.hypot(xx - (X0 + C.IC[0] * k), yy - (Y0 + C.IC[1] * k)) > 58 * k
            band = sh[yy[m], xx[m]]
            # pixels within 20 deg of the design hue and at least half its chroma = the printed band ink (dots and facets excluded)
            L_ = _lab(band); d_ = _lab(C.hx(C.ART['Spin3']['bg']))
            hue = np.degrees(np.arctan2(L_[:, 2], L_[:, 1])); hd = np.degrees(np.arctan2(d_[2], d_[1]))
            ch = np.hypot(L_[:, 1], L_[:, 2]); cd = np.hypot(d_[1], d_[2])
            sel = (np.abs((hue - hd + 180) % 360 - 180) < 20) & (ch > 0.5 * cd)
            bc = np.median(band[sel], 0)
            row['band_rgb_measured'] = hexs(bc); row['band_Lstar'] = round(float(_lab(bc)[0]), 1)
            row['band_ink_share_of_band'] = round(float(sel.mean()), 3)
            row['band_dE_measured_vs_design'] = round(de76(bc, C.hx(C.ART['Spin3']['bg'])), 1)
        out[nm] = row
    return out


def de_table():
    ref, fk = _refs()
    picks = {'TOWER': C.TYPES['TOWER']['col'], 'WAVE': C.TYPES['WAVE']['col'], 'Spin3_band': C.hx(C.ART['Spin3']['bg'])}
    res = dict(method='CIE76 dE on CIE Lab (D65) from sRGB; L* = CIE L*.  Floor: 15 (AD review section 3, check 4).',
               refs={k: hexs(v) for k, v in ref.items()}, slice_ink_FILL_K=fk,
               note='slice inks read live from corp/src xf_slices.PAL["A"] and lw_tower.FILL_K at run time; re-run `python final_cards.py de` after a slice ink change')
    tab, worst = {}, {}
    for name, col in picks.items():
        row = {k: round(de76(col, v), 1) for k, v in ref.items()}
        row['_vs_other_picks'] = {o: round(de76(col, oc), 1) for o, oc in picks.items() if o != name}
        tab[name] = dict(hex=hexs(col), Lstar=round(float(_lab(col)[0]), 1), dE=row)
        mn = min(row[k] for k in ref)
        worst[name] = dict(min_dE=mn, nearest=min(ref, key=lambda k: row[k]), pass_15=bool(mn >= 15 and min(row['_vs_other_picks'].values()) >= 15))
    res['picks'] = tab
    res['summary'] = worst
    old = {}
    for name, h in OLD.items():
        row = {k: round(de76(C.hx(h), v), 1) for k, v in ref.items()}
        mn = min(row.values())
        old[name] = dict(hex='#' + h, min_dE=mn, nearest=min(row, key=row.get), below_15=[k for k, v in row.items() if v < 15])
    res['before_O30'] = old
    res['type_word'] = {k: dict(word=hexs(v['text']), plate=hexs(v['col']), ratio_design=round(C.ratio(v['text'], v['col']), 2),
                                plate_Lstar=round(float(_lab(v['col'])[0]), 1), word_Lstar=round(float(_lab(v['text'])[0]), 1), rule='>= 4.5')
                        for k, v in C.TYPES.items()}
    if os.path.exists(FINAL + 'card_sheet.jpg'):
        ms = _measure_sheet()
        for nm, row in ms.items():
            for key in ('plate', 'band'):
                if key + '_rgb_measured' in row:
                    mc = C.hx(row[key + '_rgb_measured'])
                    dd = {k: de76(mc, v) for k, v in ref.items()}
                    row[key + '_measured_min_dE'] = round(min(dd.values()), 1)
                    row[key + '_measured_nearest'] = min(dd, key=dd.get)
        res['measured_on_published_card_sheet'] = ms
        res['measured_min_dE'] = min(v[k] for v in ms.values() for k in ('plate_measured_min_dE', 'band_measured_min_dE') if k in v)
        res['measured_word_min'] = min(v['word_vs_plate_measured'] for v in ms.values())
    res['all_pass'] = all(v['pass_15'] for v in worst.values()) and all(v['ratio_design'] >= 4.5 for v in res['type_word'].values()) \
        and res.get('measured_word_min', 99) >= 4.5
    os.makedirs(os.path.dirname(DE_OUT), exist_ok=True)
    json.dump(res, open(DE_OUT, 'w'), indent=1)
    print(json.dumps(dict(summary=worst, before=old, type_word=res['type_word'], measured_word_min=res.get('measured_word_min'), all_pass=res['all_pass']), indent=1))


if __name__ == '__main__':
    w = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if w in ('checks', 'all'):
        checks()
    if w in ('sheet', 'all'):
        sheet()
    if w in ('de', 'all'):
        de_table()
