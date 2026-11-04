"""bake_cards (port-2, 2026-11-04): the card atlas for the Godot port (GODOT_PORT_SPEC.md 4.8 / 6.2), baked from the module that
renders the new card sheet (final/card_sheet.jpg: corp/src/card_render.py via final_cards.py).  card_render is imported read-only
(no bytecode written, nothing in its folder touched).  Every text anchor in the JSON is logged from the real text() call made while
the card is drawn; nothing is typed here.

Atlases (written to D:/rc_scratch/combat_redesign/locked/port_rb/work/ unless a folder is given):
  cards_art_atlas.png     11 cards, normal state, ART ONLY: every text() call returns an empty mask and the pink rules bar is left out
                          (Godot draws the rules bar from the label's width, so a re-worded label keeps its bar)
  cards_ref_atlas.png     the same with words and bar (what the Godot labels + bar must reproduce over the art layer)
  cards_liner_atlas.png   the played-slot liner per card, ART ONLY (Godot labels the card name and PLAYED)
Written next to this folder (locked/port/):
  cards_atlas.json        cell rects, card data, logged text anchors (design px and cell px), rules-bar quads, state recipes
  cards_proof.jpg         art | ref | liner per card, at the in-hand size, for looking
usage: python bake_cards.py [work_dir] [port_dir]"""
import sys, os, json, hashlib, inspect
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
import numpy as np
from PIL import Image
import card_render as CR

WORK = sys.argv[1] if len(sys.argv) > 1 else 'D:/rc_scratch/combat_redesign/locked/port_rb/work/'
PORT = sys.argv[2] if len(sys.argv) > 2 else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/'
SHEET = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/card_sheet.jpg'
SIZE = 2 * CR.CW                 # card width in px = 2.0 x design; the canvas adds margin_px(SIZE) on each side
COLS = 4

_orig = dict(text=CR.text, rules_lines=CR.rules_lines, render_base=CR.render_base, poly=CR.poly, paint=CR.Cv.paint)
LOG = dict(words=True, texts=[], masks={}, in_base=False, bar_pending=False, last_poly=None, bars=[])


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def hexs(c):
    c = np.asarray(c, np.float64).reshape(-1)[:3]
    return '#%02X%02X%02X' % tuple(int(round(float(v) * 255)) for v in np.clip(c, 0, 1))


def w_text(cv, txt, x, y, px, name=CR.ANTON, track=0.0, skew=0.0, rot=0.0):
    m = _orig['text'](cv, txt, x, y, px, name, track, skew, rot)
    if not LOG['words']:
        m = m * 0.0
    LOG['texts'].append(dict(txt=txt, x=round(float(x), 3), y=round(float(y), 3), px=round(float(px), 3), font=name,
                             track=round(float(track), 3), skew=round(float(skew), 3), rot=round(float(rot), 3), colour=None))
    LOG['masks'][id(m)] = len(LOG['texts']) - 1
    return m


def w_rules_lines(txt, px=CR.RULES_PX):
    out = _orig['rules_lines'](txt, px)
    if LOG['in_base']:
        LOG['bar_pending'] = True
        LOG['rules'] = [dict(line=a, y=float(b), w=round(float(c), 3)) for a, b, c in out]
    return out


def w_render_base(spec, nowords=False, R=4.0, seed=0):
    LOG['in_base'] = True
    try:
        return _orig['render_base'](spec, nowords, R, seed)
    finally:
        LOG['in_base'] = False
        LOG['bar_pending'] = False


def w_poly(cv, pts):
    LOG['last_poly'] = [(round(float(a), 3), round(float(b), 3)) for a, b in pts]
    return _orig['poly'](cv, pts)


def w_paint(self, m, col, op=1.0):
    k = LOG['masks'].pop(id(m), None)
    if k is not None and LOG['texts'][k]['colour'] is None:
        c = np.asarray(col, np.float32)
        LOG['texts'][k]['colour'] = hexs(c) if c.ndim == 1 else 'per-pixel'
    if LOG['bar_pending'] and np.asarray(col).ndim == 1 and np.allclose(np.asarray(col, np.float32), np.asarray(CR.PINK, np.float32)):
        LOG['bar_pending'] = False
        LOG['bars'].append(dict(quad_design_px=LOG['last_poly'], colour=hexs(col)))
        if not LOG['words']:
            return None
    return _orig['paint'](self, m, col, op)


def install():
    CR.text = w_text
    CR.rules_lines = w_rules_lines
    CR.render_base = w_render_base
    CR.poly = w_poly
    CR.Cv.paint = w_paint


def uninstall():
    CR.text = _orig['text']
    CR.rules_lines = _orig['rules_lines']
    CR.render_base = _orig['render_base']
    CR.poly = _orig['poly']
    CR.Cv.paint = _orig['paint']


def draw(n, mode, words):
    LOG.update(words=words, texts=[], masks={}, bars=[], rules=None)
    CR._BASE.clear()
    im = CR.draw_card(n, SIZE, mode)
    return im, [dict(t) for t in LOG['texts']], list(LOG['bars']), LOG.get('rules')


def role(t, sp, mode):
    s = t['txt']
    if mode == 'played':
        return 'played_name' if s == sp['nm'] else ('played_word' if s == 'PLAYED' else 'other')
    if s == sp['nm']:
        return 'title'
    if s == sp['fam']:
        return 'type_word'
    if s == str(sp['cost']):
        return 'cost'
    if sp.get('loud') and s == '+' + str(sp['loud']):
        return 'trace'
    if sp.get('mult') and s.endswith(str(sp['mult'])) and len(s) == len(str(sp['mult'])) + 1:
        return 'mult'
    if s == CR.NO_RAM:
        return 'no_ram'
    return 'rules'


def atlas(ims):
    cw, ch = ims[0].size
    rows = (len(ims) + COLS - 1) // COLS
    at = Image.new('RGBA', (cw * COLS, ch * rows), (0, 0, 0, 0))
    rects = []
    for i, im in enumerate(ims):
        x, y = (i % COLS) * cw, (i // COLS) * ch
        at.alpha_composite(im, (x, y))
        rects.append([x, y, cw, ch])
    return at, rects


def src_ref(fn):
    lines, start = inspect.getsourcelines(fn)
    return dict(file='corp/src/card_render.py', line=start, n_lines=len(lines), source=''.join(lines))


def main():
    os.makedirs(WORK, exist_ok=True)
    install()
    try:
        art, ref, liner, un_ref = [], [], [], []
        logs = {}
        for n in CR.ORDER:
            a, ta, ba, ra = draw(n, 'normal', False)
            r, tr, br, rr = draw(n, 'normal', True)
            lv, tl, _, _ = draw(n, 'played', False)
            u, tu, _, _ = draw(n, 'unaffordable', True)
            art.append(a); ref.append(r); liner.append(lv); un_ref.append(u)
            logs[n] = dict(art=ta, ref=tr, liner=tl, unaff=tu, bars_art=ba, bars_ref=br, rules=rr)
    finally:
        uninstall()
    a_at, rects = atlas(art)
    r_at, _ = atlas(ref)
    l_at, _ = atlas(liner)
    files = {}
    for nm, im in (('cards_art_atlas.png', a_at), ('cards_ref_atlas.png', r_at), ('cards_liner_atlas.png', l_at)):
        im.save(WORK + nm)
        files[nm] = dict(size=list(im.size), md5=md5(WORK + nm), alpha_px=int((np.asarray(im)[..., 3] > 0).sum()))
    s = SIZE / CR.CW
    m = CR.margin_px(SIZE)
    to_cell = lambda x, y: [round((x + CR.MARGIN) * s, 1), round((y + CR.MARGIN) * s, 1)]
    try:
        import f1_hand
        hand_scale = float(f1_hand.CARD_SCALE)
    except Exception as e:                       # noqa: BLE001
        hand_scale = None
    meta = dict(version='port-2', doc='GODOT_PORT_SPEC.md 4.8 / 6.2; written by port/src/bake_cards.py, do not edit by hand',
                sources={'corp/src/card_render.py': md5(SRC + '/card_render.py'), 'final/card_sheet.jpg': md5(SHEET)},
                note_snapshot='cards/src_snapshot/card_render.py md5 ' + md5('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/cards/src_snapshot/card_render.py')
                              + ' is the card session\'s older snapshot (before the stage-2 NO RAM and rules-wrap change); the atlas follows corp/src',
                size_px=SIZE, scale_vs_design=s, margin_px=m, cell=list(art[0].size), cols=COLS, design_card=[CR.CW, CR.CH],
                design_margin=CR.MARGIN, hand_scale=hand_scale, files=files,
                fonts=dict(ANTON=CR.ANTON, PLEX=CR.PLEX, MONO=CR.MONO),
                rules=dict(px=CR.RULES_PX, fit_w=CR.RULES_FIT_W, cx=CR.RULES_CX, ly1=list(CR.RULES_LY1), ly2=list(CR.RULES_LY2),
                           bar_band={str(k): list(v) for k, v in CR.RULES_BAR.items()}, bar_colour=hexs(CR.PINK),
                           wrap='a text wider than fit_w wraps at the word break giving the narrowest longest line (card_render.rules_lines)'),
                no_ram=dict(word=CR.NO_RAM, px=CR.NO_RAM_PX, track=CR.NO_RAM_TRACK, tab_design_px=list(CR.NO_RAM_TAB),
                            vis_x0=CR.NO_RAM_VIS_X0, cx=round(CR.no_ram_cx(), 3), cost_c=list(CR.COST_C)),
                liner=dict(tear=CR.LINER_TEAR, rim=CR.LINER_RIM, fill=[hexs(CR.LINER_FILL[0]), CR.LINER_FILL[1]],
                           paper_v=CR.LINER_PAPER_V, word_px=CR.LINER_WORD_PX, word_v=list(CR.LINER_WORD_V)),
                state_recipes=dict(unaffordable_dim=src_ref(CR._unaffordable), unaffordable_marks=src_ref(CR.unaffordable_marks),
                                   lock_glyph=src_ref(CR.lock_glyph), liner=src_ref(CR._liner), draw_card=src_ref(CR.draw_card)),
                cards=[])
    for n, rc in zip(CR.ORDER, rects):
        sp = CR._spec(n)
        L = logs[n]
        def rows(ts, mode):
            out = []
            for t in ts:
                t = dict(t)
                t['role'] = role(t, sp, mode)
                t['cell_px'] = to_cell(t['x'], t['y'])
                out.append(t)
            return out
        tr = rows(L['ref'], 'normal')
        ta = rows(L['art'], 'normal')
        assert [(t['txt'], t['x'], t['y']) for t in tr] == [(t['txt'], t['x'], t['y']) for t in ta], n + ': art and ref draw different text'
        assert all(t['colour'] for t in tr), n + ': a text colour was not caught'
        assert len(L['bars_ref']) == 1 and len(L['bars_art']) == 1 and L['bars_ref'] == L['bars_art'], n + ': rules bar not caught once'
        bar = dict(L['bars_ref'][0])
        bar['quad_cell_px'] = [to_cell(x, y) for x, y in bar['quad_design_px']]
        un = [t for t in rows(L['unaff'], 'normal') if t['role'] in ('no_ram', 'cost') and t not in []]
        meta['cards'].append(dict(id=n, rect=rc, type=sp['fam'], name=sp['nm'], rules=sp['txt'], cost=sp['cost'], trace=sp['loud'],
                                  mult=sp.get('mult'), style=CR.ART[n]['style'], glyph=sp.get('g'),
                                  rules_lines=L['rules'], rules_bar=bar, texts=tr, liner_texts=rows(L['liner'], 'played'),
                                  unaffordable_texts=un[-2:]))
    json.dump(meta, open(PORT + 'cards_atlas.json', 'w', encoding='utf-8'), indent=1)
    # proof: art | ref | liner per card, scaled to the in-hand size (design x hand_scale), on the room-dark ground
    k = (hand_scale or 1.0) / s
    cw, ch = art[0].size
    tw, th = int(round(cw * k)), int(round(ch * k))
    per_row = 4
    gap = 14
    rows_n = (len(art) + per_row - 1) // per_row
    sheet = Image.new('RGBA', (per_row * (3 * tw + gap), rows_n * th), (16, 14, 26, 255))
    for i in range(len(art)):
        x, y = (i % per_row) * (3 * tw + gap), (i // per_row) * th
        for j, im in enumerate((art[i], ref[i], liner[i])):
            sheet.alpha_composite(im.resize((tw, th), Image.LANCZOS), (x + j * tw, y))
    sheet.convert('RGB').save(PORT + 'cards_proof.jpg', quality=90)
    print('atlas', a_at.size, 'cell', art[0].size, 'hand', hand_scale, 'proof', sheet.size,
          {k_: v['alpha_px'] for k_, v in files.items()})
    for c in meta['cards']:
        print(c['id'], [(t['role'], t['txt'], t['colour']) for t in c['texts']], 'bar', c['rules_bar']['quad_design_px'][:1],
              'liner', [(t['role'], t['colour']) for t in c['liner_texts']], 'un', [(t['role'], t['txt']) for t in c['unaffordable_texts']])


if __name__ == '__main__':
    main()
