"""abandon_dialog.png: ABANDON RUN confirm over a paused fight. Both buttons are stickers (designer, round 32):
CANCEL = the calm slate sticker (default focus, the safe choice), BURN IT = the hot pink one. The dialog
body stays terminal (the Cell's system); the cost lines follow GDD 4.2 (death: operative lost with
everything unbanked, Heat +10 + tier; Server Racks already banked stay banked)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import ui31 as U  # noqa: E402

W, H = 1920, 1080
BG = os.path.join(U.CONC, 'round30_meridian_castle', 'combat_meridian.jpg')
OUT = os.path.join(U.ROOT, 'abandon_dialog.png')


def main():
    bg = U.fit_cover(Image.open(BG).convert('RGB'), W, H)
    img = U.grade(bg, 0.30, 7, 0.55)
    img = U.vignette(img, 0.55)
    st = U.sticker('PAUSED', 54, U.FILL_YELLOW, seed=60)
    img = U.place(img, st, 200, 86, angle=-3)
    U.text(img, (90, 150), 'NETRUN  //  MERIDIAN FREIGHT  //  LAYER 4 OF 7', U.F(U.MONO, 18), U.CYAN, 'la', 1.2)
    P = (520, 230, 1400, 720)
    img = U.term_panel(img, P, 'CONFIRM  //  ABANDON RUN', accent=U.HARM, tag='CANNOT UNDO', tag_col=U.HARM, seed=7, alpha=244)
    U.text(img, (560, 300), 'Abandon the run?', U.F(U.PLEX_M, 40), U.WHITE, 'la')
    U.text(img, (560, 360), 'GHOST is lost for good, with everything unbanked:', U.F(U.PLEX, 24), (205, 212, 226), 'la')
    rows = [('CYCLES', '140', U.WHITE), ('CARDS ADDED', '2', U.WHITE), ('FIRMWARE', '1', U.WHITE), ('DAEMONS', '1', U.WHITE)]
    for k, (a, b, c) in enumerate(rows):
        x = 560 + (k % 2) * 400
        y = 410 + (k // 2) * 34
        U.text(img, (x, y), a, U.F(U.MONO, 20), (150, 176, 200), 'la', 1.2)
        U.text(img, (x + 330, y), b, U.F(U.MONO, 22), c, 'ra', 1.0)
    U.text(img, (560, 492), 'HEAT  +12   (operative death, tier 2)', U.F(U.MONO, 22), U.HARM, 'la', 1.0)
    U.text(img, (560, 526), 'Schematics already banked at a Server Rack stay banked.', U.F(U.PLEX, 21), U.GREEN, 'la')
    d = U.BD(img)
    d.line([(540, 568), (1380, 568)], fill=U.HARM + (90,), width=1)
    cancel = U.sticker('CANCEL', 50, U.FILL_CALM, seed=41)
    burn = U.sticker('BURN IT', 58, U.FILL_PINK, seed=40)
    img = U.place(img, U.focus_sticker(cancel), 760, 632, angle=2)
    img = U.place(img, burn, 1170, 630, angle=-3)
    U.text(img, (760, 694), 'keep running  [B]', U.F(U.MONO, 16), (170, 190, 210), 'mm', 1.0)
    U.text(img, (1170, 694), 'abandon, lose GHOST  [hold A]', U.F(U.MONO, 16), (255, 150, 170), 'mm', 0.8)
    # ---------------- states strip
    S = (60, 770, 1860, 1050)
    d = U.BD(img)
    d.rectangle(S, fill=(14, 12, 20, 235), outline=(50, 46, 64, 255))
    U.label_tag(img, (78, 782), 'STATES  -  calm sticker = safe choice (default focus), hot sticker = the destructive verb', U.PINK, 17)
    hov = U.sticker('BURN IT', 46, U.FILL_PINK, seed=40, gloss_k=1.0, gloss_pos=0.42, curl=dict(corner='tr', amount=0.12))
    small_c = U.sticker('CANCEL', 40, U.FILL_CALM, seed=41)
    small_b = U.sticker('BURN IT', 46, U.FILL_PINK, seed=40)
    cells = [('CANCEL  idle', lambda im, x: U.place(im, small_c, x, 900, angle=2)),
             ('CANCEL  focus (default)', lambda im, x: U.place(im, U.focus_sticker(small_c), x, 900, angle=2)),
             ('CANCEL  pressed', lambda im, x: U.place(im, small_c, x, 903, angle=2, squash=(1.04, 0.9), shadow=0.5)),
             ('BURN IT  idle', lambda im, x: U.place(im, small_b, x, 900, angle=-3)),
             ('BURN IT  hover', lambda im, x: U.place(im, hov, x, 894, angle=-3, scale=1.05, hover=0.6)),
             ('BURN IT  hold A', None),
             ('BURN IT  pressed', lambda im, x: U.place(im, small_b, x, 903, angle=-3, squash=(1.04, 0.9), shadow=0.5))]
    for k, (lab, fn) in enumerate(cells):
        x = 190 + k * 250
        if fn:
            img = fn(img, x)
        else:
            img = U.place(img, U.focus_sticker(small_b), x, 900, angle=-3)
            d = U.BD(img)
            d.arc([x - 94, 846, x + 94, 954], -90, 160, fill=U.LIME + (255,), width=5)
        U.text(img, (x, 990), lab, U.F(U.MONO, 16), U.LIME if 'focus' in lab or 'hold' in lab else (170, 170, 186), 'mm', 1.0)
    U.text(img, (78, 1024), 'Pad: B = cancel at once; BURN IT needs a 0.8 s hold (lime ring fills) so it is never a stray press. '
           'Mouse: click. Reduce motion: no hover lift, the ring still fills.', U.F(U.MONO, 15), (150, 150, 168), 'la', 0.3)
    img.convert('RGB').save(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
