"""Still 04: combat in a rainy, smoggy alley. Salvaged spinners (enemy's rim cracked), worn sticker cards."""
from PIL import Image, ImageDraw
from lowpoly import SS, W, H, R, hexc, mix, ramp, gradient, panel, skew_rect, tri, gem, text, NEON, rain, smog
from alley import draw_alley
import ui


def backdrop():
    img = draw_alley('combat_alley')
    img = smog(img, 'csmog', [(180, 180, 60, 130), (520, 200, 60, 140)], R('#141218', '#221e24', '#302a2c', '#40362e'))
    img = rain(img, 'crain_far', n=700, col=(140, 150, 170), alpha=(25, 60), length=(30, 70))
    veil = gradient(lambda u, v: mix(hexc('#050508'), hexc('#0e0a0c'), v))
    return Image.blend(img, veil, 0.42)


def render():
    img = backdrop().convert('RGBA')
    d = ImageDraw.Draw(img)
    plate = ui.DARK
    panel(d, skew_rect(960 - 130, 26, 260, 56, 12), plate, 0.35, 'round', nu=5, nv=1, gv=-0.3)
    ui.tape_strip(d, 850, 30, 70, -8, 'rtape', h=18, alpha=220)
    text(d, 966, 54, 'ROUND 3', 30, ui.CREAM, anchor='mm')
    for cx, name, sub, st, seed in ((560, 'CELL-9', 'SALVAGED RIG', NEON['cyan'], 'np1'),
                                    (1360, 'VANTA ICE', 'CORP SENTRY', NEON['red'], 'np2')):
        panel(d, skew_rect(cx - 170, 96, 340, 52, 12), plate, 0.4, seed, nu=6, nv=1, gv=-0.3)
        tri(d, [(cx - 170, 148), (cx - 158, 96), (cx - 138, 96)], ramp(st, 0.7))
        text(d, cx - 122, 122, name, 28, ui.CREAM, anchor='lm')
        text(d, cx + 150, 123, sub, 17, ramp(st, 0.75), anchor='rm', style='Bold SemiCondensed')
    you = [(5, 'attack', 6), (4, 'block', 4), (3, 'charge', 2), (6, 'attack', 8), (2, 'empty', None),
           (4, 'hack', 3), (3, 'block', 5), (3, 'empty', None)]
    foe = [(6, 'attack', 7), (3, 'empty', None), (5, 'block', 6), (4, 'hack', 4), (2, 'empty', None),
           (7, 'attack', 9), (3, 'charge', 2)]
    ui.spinner(d, 560, 410, 212, you, 'you')
    ui.spinner(d, 1360, 410, 212, foe, 'foe', cracked=True, crack_ang=0.55)
    gem(d, 960, 410, 46, 56, R('#1a0618', '#3a0c30', '#8e2a62', '#cc7ea0', '#f0d8e0'), 'vs', n=4, base=0.55)
    text(d, 960, 412, 'VS', 28, ui.CREAM, anchor='mm', shadow=ui.INK)
    ui.hp_bar(d, 350, 662, 400, 42, 0.72, NEON['cyan'], 'HP 36 / 50', 'hp1', shield=4)
    ui.hp_bar(d, 1150, 662, 400, 42, 0.55, NEON['red'], 'HP 33 / 60', 'hp2', shield=6)
    gem(d, 150, 905, 70, 80, NEON['sodium'], 'energy', n=6, base=0.55)
    text(d, 150, 900, '3/3', 38, ui.INK, anchor='mm')
    text(d, 150, 1002, 'ENERGY', 20, ui.CREAM, anchor='mm', shadow=ui.INK)
    text(d, 150, 1030, 'DECK 12  //  DISCARD 4', 15, hexc('#a09890'), anchor='mm', style='SemiBold')
    ui.hex_button(d, 1760, 900, 112, 98, R('#1a0c06', '#4a1e0c', '#9a4412', '#e07a1c', '#ffc060', '#fff0c0'), 'GO', 'go',
                  size=70, sub='SPIN BOTH WHEELS')
    hand = [
        ('attack', 'RAZOR PING', 1, ['+6 to an ATTACK', 'slice'], 'blade'),
        ('block', 'FIREWALL', 1, ['+4 GUARD slice', 'this spin'], 'shield'),
        ('hack', 'BACKDOOR', 2, ['Shift foe wheel', '3 ticks back'], 'eye'),
        ('charge', 'OVERCLOCK', 0, ['Next slice hits', 'twice'], 'bolt'),
        ('hack', 'WORM', 2, ['Turn a foe slice', 'EMPTY'], 'virus'),
        ('attack', 'BRUTE FORCE', 3, ['Deal 12. Burn', '1 heat'], 'blade'),
    ]
    n = len(hand)
    hov = None
    for k, (kind, title, cost, lines, icon) in enumerate(hand):
        off = k - (n - 1) / 2
        cx = 960 + off * 178
        cy = 905 + abs(off) ** 1.6 * 9 - (50 if k == 2 else 0)
        tape = (100, 12, 90, -6) if k in (1, 4) else None
        cimg = ui.card_image(kind, title, cost, lines, icon, ('hand', k), tape=tape)
        if k == 2:
            hov = (cimg, cx, cy, -off * 4.0)
        else:
            ui.paste_card(img, cimg, cx, cy, -off * 4.0)
    ui.paste_card(img, *hov)
    img = rain(img.convert('RGB'), 'crain_near', n=260, col=(170, 180, 200), alpha=(30, 70), length=(60, 140))
    return img
