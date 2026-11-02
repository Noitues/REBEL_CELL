"""final_cards: the O-29 card sheet and the card contrast numbers.
python final_cards.py [sheet|checks|all]  ->  locked/final/card_sheet.jpg, corp/work/card_checks.json
Cards come from card_render.draw_card (same module the plates use).  In-hand scale is f1_hand.CARD_SCALE (1.10)."""
import sys, os, json, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import card_render as C

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
FD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/'
SCALE = 1.10
os.makedirs(FINAL, exist_ok=True)


def F(px, name='Anton-Regular.ttf'):
    return ImageFont.truetype(FD + name, px)


def hexs(c):
    return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in c)


def sheet():
    t = time.time()
    states = [('normal (in hand: 88 % value)', dict(mode='normal'), 1.0), ('lifted / hover (1.10 x)', dict(mode='hover'), 1.10),
              ('played slot (name + PLAYED)', dict(mode='played'), 1.0), ('unaffordable (dim glass)', dict(mode='unaffordable'), 1.0),
              ('nowords', dict(mode='normal', nowords=True), 1.0)]
    base_w = int(round(176 * SCALE * 1.5))          # the sheet shows the cards at 1.5 x their in-hand size
    marg = C.margin_px(int(base_w * 1.1))
    cell_w, cell_h = int(base_w * 1.1) + 2 * marg + 6, int(250 * base_w / 176 * 1.1) + 2 * marg + 6
    LW, TH = 250, 120
    W = LW + cell_w * len(C.ORDER) + 20
    H = TH + (cell_h + 20) * len(states) + 60
    im = Image.new('RGB', (W, H), (38, 42, 54))
    d = ImageDraw.Draw(im)
    T, Wv = C.TYPES['TOWER'], C.TYPES['WAVE']
    d.text((24, 14), 'SHIFTING WAVES: the 11 WPAP cards, 5 states (final, O-29 fixes 1, 4, 6, 7, 8)', font=F(40), fill=(250, 248, 240))
    d.text((24, 66), 'TOWER %s (white text)  |  WAVE %s (ink text; bone #F1EAD6 read as the card paper, so warm orange)  |  +Trace tab stays violet %s  |  shown at 1.5 x the 1.10 x in-hand size'
           % (hexs(T['col']), hexs(Wv['col']), hexs(C.TRACE_VIOLET)), font=F(20, 'ShareTechMono-Regular.ttf'), fill=(200, 206, 222))
    for r, (sn, st, k) in enumerate(states):
        y0 = TH + r * (cell_h + 20)
        d.text((20, y0 + 20), sn.upper(), font=F(22), fill=(240, 236, 224))
        for c, nm in enumerate(C.ORDER):
            stt = dict(st)
            if r == 0:
                stt['dim'] = None
            card = C.draw_card(nm, int(round(base_w * k)), stt).convert('RGBA')
            cx = LW + c * cell_w + cell_w // 2
            cy = y0 + cell_h // 2
            im.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), card)
    im.save(FINAL + 'card_sheet.jpg', quality=92)
    print('sheet', im.size, round(time.time() - t, 1), flush=True)


def checks():
    r = C.ratio
    out = {}
    out['type_colours'] = {k: dict(col=hexs(v['col']), text=hexs(v['text']), text_vs_plate=round(r(v['text'], v['col']), 2),
                                   plate_vs_paper=round(r(v['col'], C.CREAM), 2), text_rule='>= 4.5') for k, v in C.TYPES.items()}
    out['wave_variant'] = C.WAVE_VARIANT
    out['bone_vs_paper_if_used'] = round(r(C.hx('F1EAD6'), C.CREAM), 2)
    out['tower_vs_wave_grey'] = round(r(C.TYPES['TOWER']['col'], C.TYPES['WAVE']['col']), 2)
    out['trace_tab'] = dict(col=hexs(C.TRACE_VIOLET), white_plus_vs_tab=round(r(C.WHITE, C.TRACE_VIOLET), 2))
    out['facet_opacity'] = dict(type_plane=C.FACET_OP[0], type_dark_plane=C.FACET_OP[1], glint=C.FACET_OP[2], rule='25-35 %')
    cap = 0.86
    out['titles_cap_screen_px_at_1p10'] = {nm: round(C._fit_title(C.CARDS[nm]['nm']) * cap * SCALE, 1) for nm in C.ORDER}
    out['title_fill_vs_keyline'] = round(r(C.WHITE, C.INK), 1)
    # spin arcs on screen (1.10 x): stroke and clear gap between the arcs (incl. the paper keyline 1.4 each side)
    out['spin_arcs_screen_px'] = dict(stroke=round(3.4 * SCALE, 2), stroke_with_keyline=round((3.4 + 2.8) * SCALE, 2),
                                      centre_pitch=round(13.0 * SCALE, 2), clear_gap_between_inks=round((13.0 - 3.4) * SCALE, 2),
                                      clear_gap_between_keylines=round((13.0 - 3.4 - 2.8) * SCALE, 2),
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
                      glyph_vs_keyline=round(r(C.WHITE, C.INK), 1), pass_2p5=bool(r(disc, around) >= 2.5))
        print(nm, ic[nm], flush=True)
    out['icon_disc'] = ic
    out['icon_disc_min'] = min(v['disc_vs_art_around'] for v in ic.values())
    out['icon_disc_all_ge_2p5'] = all(v['pass_2p5'] for v in ic.values())
    json.dump(out, open(WORK + 'card_checks.json', 'w'), indent=1)
    print(json.dumps({k_: v for k_, v in out.items() if k_ != 'icon_disc'}, indent=1))


if __name__ == '__main__':
    w = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if w in ('checks', 'all'):
        checks()
    if w in ('sheet', 'all'):
        sheet()
