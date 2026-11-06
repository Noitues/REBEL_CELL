"""bake_cards: proof bake of the card atlas for the Godot port (GODOT_PORT_SPEC.md section 4.3).
Imports the locked card_render read-only. Writes, under D:/rc_scratch/combat_redesign/locked/port/work/:
  cards_art_atlas.png   11 cards, ART ONLY (every text call returns an empty mask: plates stay, words go), 4 x 3 cells of 424 x 572
  cards_ref_atlas.png   the same with words (what the Godot labels must reproduce on top of the art layer)
  cards_atlas.json      cell rects, card id, type, text anchors in cell px
  cards_proof.jpg       art vs ref side by side, for looking
usage: python bake_cards.py"""
import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import card_render as CR

OUT = 'D:/rc_scratch/combat_redesign/locked/port/work/'
SIZE = 352                       # card width in px = 2.0 x design (176); canvas adds margin_px(352) = 36 on each side
COLS = 4

orig_text = CR.text


def no_text(cv, txt, x, y, px, *a, **k):
    m = orig_text(cv, txt, x, y, px, *a, **k)
    return m * 0.0


def bake(words):
    CR.text = orig_text if words else no_text
    CR._BASE.clear()
    ims = [CR.draw_card(n, SIZE, 'normal') for n in CR.ORDER]
    CR.text = orig_text
    return ims


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


def main():
    art = bake(False)
    ref = bake(True)
    a_at, rects = atlas(art)
    r_at, _ = atlas(ref)
    a_at.save(OUT + 'cards_art_atlas.png')
    r_at.save(OUT + 'cards_ref_atlas.png')
    s = SIZE / CR.CW
    m = CR.margin_px(SIZE)
    to_cell = lambda x, y: [round((x + CR.MARGIN) * s, 1), round((y + CR.MARGIN) * s, 1)]
    meta = dict(size_px=SIZE, scale_vs_design=s, margin_px=m, cell=list(art[0].size),
                anchors_design_px=dict(title=[87.5, 144.5], type_word=[85.5, 174.4], rules=[80, 206], cost=[21.5, 22.2],
                                       trace=[CR.CW - 43, 17.6], mult=[139, 107], played_name=[88, 159], played_word=[88, 181]),
                cards=[])
    for n, rc in zip(CR.ORDER, rects):
        sp = CR._spec(n)
        meta['cards'].append(dict(id=n, rect=rc, type=sp['fam'], name=sp['nm'], rules=sp['txt'], cost=sp['cost'],
                                  trace=sp['loud'], mult=sp.get('mult'), style=CR.ART[n]['style'],
                                  anchors_cell_px={k: to_cell(*v) for k, v in meta['anchors_design_px'].items()}))
    json.dump(meta, open(OUT + 'cards_atlas.json', 'w'), indent=1)
    # proof sheet: art | ref per card, on the room-dark ground
    cw, ch = art[0].size
    sheet = Image.new('RGBA', (cw * 2 * 4 + 40, ch * 3 + 20), (16, 14, 26, 255))
    for i in range(len(art)):
        x, y = (i % 4) * (cw * 2 + 10), (i // 4) * ch
        sheet.alpha_composite(art[i], (x, y))
        sheet.alpha_composite(ref[i], (x + cw, y))
    sheet.convert('RGB').resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(OUT + 'cards_proof.jpg', quality=88)
    a = np.asarray(a_at)
    print('atlas', a_at.size, 'cell', art[0].size, 'alpha px', int((a[..., 3] > 0).sum()))


if __name__ == '__main__':
    main()
