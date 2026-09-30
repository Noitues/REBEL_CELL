"""Still 06: close-up of the player's salvaged spinner as hero hardware."""
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, gradient, panel, skew_rect, tri, gem, text, NEON, rain, smog,
                     line2)
from alley import draw_alley
import ui


def render():
    img = draw_alley('closeup_alley')
    img = smog(img, 'csm', [(260, 260, 60, 130), (640, 240, 60, 130)], R('#140c20', '#24122e', '#361a3a', '#123040'))
    img = Image.blend(img, gradient(lambda u, v: mix(hexc('#040408'), hexc('#0c0810'), v)), 0.55)
    img = rain(img, 'cu_rain', n=500, col=(150, 160, 190), alpha=(25, 60), length=(40, 100))
    img = img.convert('RGBA')
    d = ImageDraw.Draw(img)
    you = [(5, 'attack', 6), (4, 'block', 4), (3, 'charge', 2), (6, 'attack', 8), (2, 'empty', None),
           (4, 'hack', 3), (3, 'block', 5), (3, 'empty', None)]
    cx, cy, Rr = 800, 578, 420
    ui.spinner(d, cx, cy, Rr, you, 'hero', glyphs=True, needle=True, dense=2)
    # stencilled serial plate riveted to the band
    panel(d, skew_rect(cx - 330, cy + Rr * 0.98, 190, 34, 8), ui.METAL, 0.35, 'serial', nu=3, nv=1)
    text(d, cx - 230, cy + Rr * 0.98 + 17, 'CX-30 // SALVAGE', 17, hexc('#d8ccb8'), anchor='mm',
         style='Bold SemiCondensed')
    # right-hand readout panel
    px, py, pw = 1390, 90, 480
    panel(d, skew_rect(px, py, pw, 96, 14), ui.DARK, 0.4, 'cu_title', nu=4, nv=1, gv=-0.3)
    for k in range(9):
        x = px + 20 + k * 22
        tri(d, [(x, py), (x + 11, py), (x - 4, py + 8)], ramp(NEON['sodium'], 0.6))
    text(d, px + 30, py + 36, 'CELL-9', 38, ui.CREAM, anchor='lm')
    text(d, px + 30, py + 74, 'SALVAGED RIG  //  WHEEL MK.II  //  30 TICKS', 16, ramp(NEON['cyan'], 0.75),
         anchor='lm', style='Bold SemiCondensed')
    ui.hp_bar(d, px, py + 128, pw - 90, 46, 0.72, NEON['cyan'], 'HP 36 / 50', 'cu_hp', shield=4)
    rows = [('attack', 'blade', 'ATTACK', 'deal the number as damage'),
            ('block', 'shield', 'GUARD', 'absorb the number next hit'),
            ('hack', 'eye', 'HACK', 'nudge the foe wheel'),
            ('charge', 'bolt', 'CHARGE', 'bank energy for next turn'),
            ('empty', None, 'EMPTY', 'nothing happens')]
    y = py + 222
    for k, (kind, icon, lab, desc) in enumerate(rows):
        panel(d, skew_rect(px, y, pw, 74, 10), ui.DARK, 0.3, ('row', k), nu=3, nv=1, gv=-0.3)
        facet_q = [(px + 14, y + 10), (px + 72, y + 10), (px + 66, y + 64), (px + 8, y + 64)]
        from lowpoly import facet, bil, toner
        facet(d, bil(facet_q), 2, 2, toner(ui.KIND[kind], 0.55, gu=-0.3, var=0.08), ('sw', k), 0.3)
        if icon:
            ui.draw_icon(d, icon, px + 20, y + 16, 42, 42, ui.DARK + [hexc('#5a5460'), ui.CREAM])
        text(d, px + 92, y + 26, lab, 24, ui.CREAM, anchor='lm')
        text(d, px + 92, y + 52, desc, 17, hexc('#a89ca0'), anchor='lm', style='SemiBold')
        y += 86
    # next-tick callout with a leader line to the pointer
    ny = y + 18
    panel(d, skew_rect(px, ny, pw, 70, 12), NEON['sodium'], 0.55, 'next', nu=4, nv=1, gv=-0.3, var=0.06)
    text(d, px + 30, ny + 35, 'NEXT TICK  >  ATTACK 6', 28, ui.INK, anchor='lm')
    return img.convert('RGB')
