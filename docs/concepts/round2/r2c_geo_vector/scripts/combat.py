"""Still 04: combat. Two faceted spinners, HP bars, a fanned hand, a GO button, city pushed back."""
from PIL import Image, ImageDraw, ImageFilter
from lowpoly import SS, W, H, R, hexc, mix, ramp, gradient, panel, skew_rect, tri, gem, text, NEON
from city import render_city
import ui


def backdrop():
    city = render_city('night', overlay=False, hud=False)
    veil = gradient(lambda u, v: mix(hexc('#070818'), hexc('#1a0c2e'), v))
    img = Image.blend(city, veil, 0.62)
    return img.filter(ImageFilter.GaussianBlur(2 * SS))


def render():
    img = backdrop().convert('RGBA')
    d = ImageDraw.Draw(img)
    plate = ui.DARK
    # round plate
    panel(d, skew_rect(960 - 130, 26, 260, 56, 12), plate, 0.35, 'round', nu=5, nv=1, gv=-0.3)
    text(d, 966, 54, 'ROUND 3', 30, ui.CREAM, anchor='mm')
    # name plates
    for cx, name, sub, st, seed in ((560, 'CELL-9', 'YOUR RIG', NEON['cyan'], 'np1'),
                                    (1360, 'VANTA ICE', 'CORP SENTRY', NEON['red'], 'np2')):
        panel(d, skew_rect(cx - 170, 96, 340, 52, 12), plate, 0.4, seed, nu=6, nv=1, gv=-0.3)
        tri(d, [(cx - 170, 148), (cx - 158, 96), (cx - 138, 96)], ramp(st, 0.7))
        text(d, cx - 122, 122, name, 28, ui.CREAM, anchor='lm')
        text(d, cx + 150, 123, sub, 17, ramp(st, 0.75), anchor='rm', style='Bold SemiCondensed')
    # spinners
    you = [(5, 'attack', 6), (4, 'block', 4), (3, 'charge', 2), (6, 'attack', 8), (2, 'empty', None),
           (4, 'hack', 3), (3, 'block', 5), (3, 'empty', None)]
    foe = [(6, 'attack', 7), (3, 'empty', None), (5, 'block', 6), (4, 'hack', 4), (2, 'empty', None),
           (7, 'attack', 9), (3, 'charge', 2)]
    ui.spinner(d, 560, 410, 222, you, 'you')
    ui.spinner(d, 1360, 410, 222, foe, 'foe')
    # VS gem
    gem(d, 960, 410, 50, 60, R('#1a0630', '#3e0c5a', '#b8248e', '#f890c0', '#ffe4f0'), 'vs', n=4, base=0.55)
    text(d, 960, 412, 'VS', 30, ui.CREAM, anchor='mm', shadow=ui.INK)
    # hp bars
    ui.hp_bar(d, 350, 660, 400, 42, 0.72, NEON['cyan'], 'HP 36 / 50', 'hp1', shield=4)
    ui.hp_bar(d, 1150, 660, 400, 42, 0.55, NEON['red'], 'HP 33 / 60', 'hp2', shield=6)
    # energy + deck (left) / GO (right)
    gem(d, 150, 905, 70, 80, NEON['amber'], 'energy', n=6, base=0.6)
    text(d, 150, 900, '3/3', 38, ui.INK, anchor='mm')
    text(d, 150, 1002, 'ENERGY', 20, ui.CREAM, anchor='mm', shadow=ui.INK)
    text(d, 150, 1030, 'DECK 12  //  DISCARD 4', 15, hexc('#b8a8c8'), anchor='mm', style='SemiBold')
    ui.hex_button(d, 1760, 900, 118, 104, R('#3a0a10', '#8a1a1a', '#e0502a', '#ffb040', '#fff0b0'), 'GO', 'go', size=72,
                  sub='SPIN BOTH WHEELS')
    # hand
    hand = [
        ('attack', 'RAZOR PING', 1, ['+6 to an ATTACK', 'slice'], 'blade'),
        ('block', 'FIREWALL', 1, ['+4 GUARD slice', 'this spin'], 'shield'),
        ('hack', 'BACKDOOR', 2, ['Shift foe wheel', '3 ticks back'], 'eye'),
        ('charge', 'OVERCLOCK', 0, ['Next slice hits', 'twice'], 'bolt'),
        ('hack', 'WORM', 2, ['Turn a foe slice', 'EMPTY'], 'virus'),
        ('attack', 'BRUTE FORCE', 3, ['Deal 12. Burn', '1 heat'], 'blade'),
    ]
    n = len(hand)
    for k, (kind, title, cost, lines, icon) in enumerate(hand):
        off = k - (n - 1) / 2
        cx = 960 + off * 178
        cy = 905 + abs(off) ** 1.6 * 9
        ang = -off * 4.0
        hover = k == 2
        if hover:
            cy -= 50
        cimg = ui.card_image(kind, title, cost, lines, icon, ('hand', k), hover=hover)
        if k != 2:
            ui.paste_card(img, cimg, cx, cy, ang)
        else:
            hov = (cimg, cx, cy, ang)
    ui.paste_card(img, *hov)
    return img.convert('RGB')
