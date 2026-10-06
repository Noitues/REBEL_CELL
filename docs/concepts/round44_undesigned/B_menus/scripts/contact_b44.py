"""contact_B.jpg: each round 44 B render beside the build capture it replaces (build left, concept right)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw  # noqa: E402

import b44 as K  # noqa: E402

U = K.U
FIX = K.BUILD + '/docs/art_review/PARITY/fixes/'
ROWS = [('new_campaign.png', 'NEWC.jpg', (1280, 25, 1920, 385), 'NEW CAMPAIGN  //  build: NEWC after 1.0'),
        ('campaign_slots.png', 'SLOTS_c.jpg', (0, 580, 635, 945), 'CAMPAIGN SLOTS  //  build: SLOTS_c'),
        ('stats.png', 'MENUS.jpg', (10, 1959, 635, 2314), 'STATS  //  build: MENUS stats text 1.0'),
        ('codex.png', 'MENUS.jpg', (10, 610, 635, 965), 'CODEX  //  build: MENUS codex text 1.0 (paper)'),
        ('pause.png', 'PAUSE_b.jpg', (480, 310, 960, 580), 'PAUSE  //  build: PAUSE_b netrun text 1.6'),
        ('pause_abandon.png', 'PAUSE_b.jpg', (480, 890, 960, 1160), 'ABANDON CONFIRM  //  build: PAUSE_b fight abandon 1.6'),
        ('deck_viewer.png', 'CARDFACE_deck.jpg', (1280, 25, 1920, 385), 'LOADOUT DECK  //  build: CARDFACE_deck after 1.0'),
        ('deck_viewer_spinner.png', None, None, 'LOADOUT SPINNER  //  no build capture of the SPINNER tab'),
        ('options.png', 'MENUS.jpg', (10, 4518, 635, 4873), 'OPTIONS  //  build: MENUS title options 1.0')]
TW, TH, G, LH = 640, 360, 20, 34


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    out = Image.new('RGB', (w, h), (18, 16, 24))
    out.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out


def main():
    W = G * 3 + TW * 2
    H = 70 + len(ROWS) * (TH + LH + G)
    sheet = Image.new('RGBA', (W, H), (14, 12, 20, 255))
    U.text(sheet, (G, 20), 'ROUND 44 B  //  MENU SCREENS  //  build (left)  vs  concept (right)', U.F(U.MONO, 22), U.WHITE, 'la', 1.0)
    cache = {}
    y = 70
    for concept, src, box, label in ROWS:
        U.text(sheet, (G, y + 6), label, U.F(U.MONO, 17), U.CYAN, 'la', 0.8)
        y += LH
        if src:
            if src not in cache:
                cache[src] = Image.open(FIX + src).convert('RGB')
            b = fit(cache[src].crop(box), TW, TH)
        else:
            b = Image.new('RGB', (TW, TH), (18, 16, 24))
            ImageDraw.Draw(b).text((TW // 2, TH // 2), 'the build shows a mini wheel in the window (no capture)',
                                   font=U.F(U.MONO, 16), fill=(140, 140, 160), anchor='mm')
        sheet.paste(b, (G, y))
        c = fit(Image.open(os.path.join(K.B, concept)).convert('RGB'), TW, TH)
        sheet.paste(c, (G * 2 + TW, y))
        U.text(sheet, (G + 8, y + TH - 22), 'BUILD', U.F(U.MONO, 15), (255, 200, 80), 'la', 1.0)
        U.text(sheet, (G * 2 + TW + 8, y + TH - 22), 'CONCEPT  ' + concept, U.F(U.MONO, 15), (212, 255, 0), 'la', 0.6)
        y += TH + G
    p = os.path.join(K.B, 'contact_B.jpg')
    sheet.convert('RGB').save(p, quality=88)
    print('wrote', p)


if __name__ == '__main__':
    main()
