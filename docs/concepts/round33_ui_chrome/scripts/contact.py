"""contact_sheet.jpg: every round 31 board on one page (3 x 2), plus the title loop key frames."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import ui31 as U  # noqa: E402

TW, TH = 620, 349
OUT = os.path.join(U.ROOT, 'contact_sheet.jpg')
ITEMS = [('title_screen.png', '1  TITLE A (locked): glitch DISABLE, fist OVERTHROW'),
         ('title_screen_alt_simulate.png', '2  RECOMMENDED: SIMULATE = tutorial'),
         ('abandon_dialog.png', '3  ABANDON RUN: yellow CANCEL'), ('ui_kit.png', '4  UI KIT (yellow CANCEL)'),
         ('typography.png', '5  TYPOGRAPHY (Courier Prime paper)'), (None, '1b  TITLE LOOP (gif)')]


def main():
    W = 24 + 3 * (TW + 24)
    H = 92 + 2 * (TH + 60) + 10
    img = U.canvas(W, H, (11, 10, 16))
    U.header_bar(img, 'ROUND 33  -  UI CHROME', 'sticker = static words  //  terminal = the Cell\'s systems  //  paper = corp documents  //  '
                 'holo = decrypted corp intel  //  pencil = true plans')
    for k, (fn, lab) in enumerate(ITEMS):
        x = 24 + (k % 3) * (TW + 24)
        y = 104 + (k // 3) * (TH + 60)
        if fn:
            th = Image.open(os.path.join(U.ROOT, fn)).convert('RGBA').resize((TW, TH), Image.LANCZOS)
        else:
            g = Image.open(os.path.join(U.ROOT, 'title_screen.gif'))
            th = Image.new('RGBA', (TW, TH), (0, 0, 0, 255))
            for i, f in enumerate((6, 10, 28, 40)):
                g.seek(f)
                fr = g.convert('RGB').resize((TW // 2, TH // 2), Image.LANCZOS)
                th.paste(fr, ((i % 2) * (TW // 2), (i // 2) * (TH // 2)))
        img.alpha_composite(th, (x, y))
        U.text(img, (x, y + TH + 12), lab, U.F(U.BAHN, 20, 'Bold'), U.WHITE, 'la', 0.8)
    img.convert('RGB').save(OUT, quality=90)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
