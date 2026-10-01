"""Combat mockups on the Cv2 combat base (gritty alley, plates, GO), with the round-4 wheels and hand."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GRITTY = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'round2', 'r2c_geo_vector_gritty', 'scripts')
sys.path.append(GRITTY)
from common import *
import wheels
import cards
import combat as gc        # the Cv2 gritty combat base (backdrop, plates)
import ui as gui


def base_scene():
    img = gc.backdrop().convert('RGBA')
    d = ImageDraw.Draw(img)
    plate = gui.DARK
    panel(d, skew_rect(960 - 130, 26, 260, 56, 12), plate, 0.35, 'round', nu=5, nv=1, gv=-0.3)
    text(d, 966, 54, 'ROUND 3', 30, gui.CREAM, anchor='mm')
    for cx, name, sub, st, seed in ((560, 'CELL-9', 'SALVAGED RIG', NEON['cyan'], 'np1'),
                                    (1360, 'VANTA ICE', 'MERIDIAN SENTRY', NEON['amber'], 'np2')):
        panel(d, skew_rect(cx - 170, 96, 340, 52, 12), plate, 0.4, seed, nu=6, nv=1, gv=-0.3)
        text(d, cx - 122, 122, name, 28, gui.CREAM, anchor='lm')
        text(d, cx + 150, 123, sub, 17, ramp(st, 0.75), anchor='rm', style='Bold SemiCondensed')
    gem(d, 150, 905, 70, 80, NEON['sodium'], 'energy', n=6, base=0.55)
    text(d, 150, 900, '2/3', 38, gui.INK, anchor='mm')
    text(d, 150, 1002, 'RAM', 20, gui.CREAM, anchor='mm', shadow=gui.INK)
    gui.hex_button(d, 1760, 900, 112, 98, R('#1a0c06', '#4a1e0c', '#9a4412', '#e07a1c', '#ffc060', '#fff0c0'), 'GO', 'go',
                   size=70, sub='SPIN BOTH WHEELS')
    return finalize(img).convert('RGBA')


def mockup(wver, cver, name):
    base = base_scene()
    p = wheels.render_wheel(wver, 180, PLAYER, 'player', rot=2.5, status={5}, hp=(36, 50), name='CELL-9')
    e = wheels.render_wheel(wver, 180, ENEMY, 'enemy', rot=3.0, hp=(33, 60), name='VANTA ICE')
    wheels.paste_wheel(base, p, 560, 430)
    wheels.paste_wheel(base, e, 1360, 430)
    # hand at the spec hand size; the focused card lifted at 1.5x
    hand = cards.CARDS + [cards.CARDS[0]]
    n = len(hand)
    hov = None
    for k, c in enumerate(hand):
        off = k - (n - 1) / 2
        x, y = 960 + off * 118, 960 + abs(off) ** 1.6 * 6
        if k == 2:
            hov = (c, x, y)
            continue
        afford = c['cost'] <= 2
        im = cards.render_card(cver, c, 112, 148, afford=afford, angle=-off * 4)
        paste_c(base, im, x, y)
    c, x, y = hov
    im = cards.render_card(cver, c, 168, 222, hover=1.0)
    paste_c(base, im, x, y - 70)
    out = os.path.join(OUT, name)
    base.convert('RGB').save(out, optimize=True)
    print('wrote', name)


if __name__ == '__main__':
    mockup('A', 'C', 'mockup_1.png')
    mockup('D', 'D', 'mockup_2.png')
