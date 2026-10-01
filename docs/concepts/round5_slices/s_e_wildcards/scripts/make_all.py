"""Build every s_e_wildcards deliverable.  python make_all.py [what ...]
what: sheets overview player enemy fx small test  (default: all)
"""
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slicelib as L  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

STYLE_INFO = {
    'holo': ('HOLO FOIL COLLECTIBLE', 'iridescent trading-card foil, embossed emblem, a foil pattern per program',
             'shader: hue + glint follow tilt'),
    'enamel': ('ENAMEL PIN / CLOISONNE', 'gold walls between enamel fields, dark cartouche, glossy dome',
               'shader: specular sweep across the pins'),
    'cv2': ('FACETED CV2 NEON', 'gritty triangulated low-poly, own facet pattern + neon edges per program',
            'shader: facets light up in sequence'),
}
TEX = {
    'holo': {'EXPLOIT': 'diffraction lines', 'ZERO-DAY': 'prism stars + rays', 'FIREWALL': 'brick holo',
             'SANDBOX': 'nested squares', 'PROXY': 'chevron diffraction', 'PATCH': 'hex holo',
             'VIRUS': 'cellular foil', 'TROJAN': 'diamond lattice', 'NULL': 'dead matte foil'},
    'enamel': {'EXPLOIT': 'slash stripes', 'ZERO-DAY': 'sunburst rays', 'FIREWALL': 'gold-mortar bricks',
               'SANDBOX': 'nested frames', 'PROXY': 'chevron bands', 'PATCH': 'bandage strip',
               'VIRUS': 'spore cells', 'TROJAN': 'crate planks + lid', 'NULL': 'grey matte, pewter'},
    'cv2': {'EXPLOIT': 'long sharp shards', 'ZERO-DAY': 'starburst fan', 'FIREWALL': 'layered courses',
            'SANDBOX': 'symmetric enclosure', 'PROXY': 'zigzag reroutes', 'PATCH': 'calm even grid',
            'VIRUS': 'chaotic spread', 'TROJAN': 'shell + hidden core', 'NULL': 'few dead facets'},
}
FXN = {'EXPLOIT': 'glitch bands', 'ZERO-DAY': 'flash', 'FIREWALL': 'scanline sweep', 'SANDBOX': 'border pulse',
       'PROXY': 'lateral reroute', 'PATCH': 'heal ring', 'VIRUS': 'infection wave', 'TROJAN': 'unpacking seam',
       'NULL': 'dead flicker'}

PLAYER = [('EXPLOIT', 4, '8'), ('ZERO-DAY', 2), ('PROXY', 3), ('EXPLOIT', 3), ('FIREWALL', 4),
          ('VIRUS', 3), ('PATCH', 3), ('SANDBOX', 3), ('TROJAN', 3), ('NULL', 2)]
ENEMY = [('EXPLOIT', 3, '7'), ('PROXY', 3), ('FIREWALL', 4, '6'), ('ZERO-DAY', 2, '14'), ('VIRUS', 3, '4'),
         ('NULL', 3), ('EXPLOIT', 3, '9'), ('SANDBOX', 3, '5'), ('TROJAN', 3, '3'), ('NULL', 3)]
MIXED = {'EXPLOIT': 'cv2', 'ZERO-DAY': 'holo', 'FIREWALL': 'enamel', 'SANDBOX': 'enamel', 'PROXY': 'cv2',
         'PATCH': 'cv2', 'VIRUS': 'holo', 'TROJAN': 'cv2', 'NULL': 'cv2'}
ROT = -0.5 * L.TICK  # pointer lands inside the first slice


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, optimize=True)
    print('wrote', p, os.path.getsize(p) // 1024, 'KB', flush=True)


# --------------------------------------------------------------------------- sheets
def sheet_style(style):
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=11)
    title, desc, shd = STYLE_INFO[style]
    L.label(cv, 48, 28, f'S_E WILDCARDS  /  {title}', 44, anchor='lt')
    L.label(cv, 50, 80, f'{desc}   |   {shd}', 0, (190, 190, 205), anchor='lt', fnt=L.mono(19 * 2))
    S = 1.0
    row1 = L.ORDER[:6]
    for i, p in enumerate(row1):
        cx = 160 + i * 320
        L.render_tile(cv, p, 3, cx, 120, S, style, t=0.2, fx=False)
        L.label(cv, cx, 360, p, 30)
        L.label(cv, cx, 394, TEX[style][p], 0, (170, 170, 185), fnt=L.mono(16 * 2))
    row2 = [(p, 3) for p in L.ORDER[6:]] + [('EXPLOIT', 2), ('EXPLOIT', 5)]
    xs = [160, 480, 800, 1110, 1480]
    for (p, tk), cx in zip(row2, xs):
        L.render_tile(cv, p, tk, cx, 440, S, style, t=0.2, fx=False)
        nm = p if tk == 3 else f'{p}  {tk}-TICK'
        L.label(cv, cx, 682, nm, 30, (255, 255, 255) if tk == 3 else (255, 210, 120))
        L.label(cv, cx, 716, TEX[style][p] if tk == 3 else ('narrow: glyph over number' if tk == 2 else 'wide: glyph beside number'),
                0, (170, 170, 185), fnt=L.mono(16 * 2))
    # in-game size row (r = 150) mid-shader
    L.label(cv, 48, 770, 'AT IN-GAME SIZE (outer r = 150 px), shader mid-cycle', 24, (255, 210, 120), anchor='lt')
    S2 = 150 / 360
    for i, p in enumerate(L.ORDER):
        cx = 110 + i * 205
        L.render_tile(cv, p, 3, cx, 815, S2, style, t=0.55)
        L.label(cv, cx, 925, p, 20, (200, 200, 210))
    L.caption(cv, title.split(' /')[0], 'each slice = a program: own texture, own shader, glyph + value on a calmed plate',
              y=996, accent=(255, 61, 168))
    save(cv.finish(), f'programs_sheet_{style}.png')


def sheet_overview():
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=12)
    L.label(cv, 40, 22, 'S_E WILDCARDS  /  9 PROGRAMS x 3 MINI-STYLES', 40, anchor='lt')
    L.label(cv, 42, 70, 'same 9 programs, three premium treatments; 2-tick and 5-tick variants at right',
            0, (190, 190, 205), anchor='lt', fnt=L.mono(18 * 2))
    S = 0.5
    for ri, style in enumerate(['holo', 'enamel', 'cv2']):
        top = 140 + ri * 300
        L.label(cv, 40, top - 26, STYLE_INFO[style][0] + '   ' + STYLE_INFO[style][2], 22, (255, 210, 120), anchor='lt')
        x = 90
        for p in L.ORDER:
            L.render_tile(cv, p, 3, x, top, S, style, t=0.2, fx=False)
            L.label(cv, x, top + 128, p, 20, (220, 220, 230))
            x += 152
        for tk, w in ((2, 110), (5, 210)):
            x += w / 2 - 50
            L.render_tile(cv, 'EXPLOIT', tk, x, top, S, style, t=0.2, fx=False)
            L.label(cv, x, top + 128, f'{tk}-TICK', 20, (255, 210, 120))
            x += w / 2 + 70
    save(cv.finish(), 'programs_sheet.png')


# --------------------------------------------------------------------------- wheels
def wheel_single(style, name, fname, t=0.2, stickers=False, title='', sub=''):
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=21)
    bez = {'holo': 'holo', 'enamel': 'enamel'}.get(style if isinstance(style, str) else 'cv2', 'cv2')
    L.render_wheel(cv, 960, 448, 0.96, PLAYER, style=style, t=t, rot=ROT, bezel=bez, accent=(255, 61, 168),
                   name=name, sub='Salvaged Rig', hp=(36, 50), stickers=stickers)
    L.caption(cv, title, sub, y=996)
    save(cv.finish(), fname)


def wheel_player():
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=22)
    S = 0.78
    L.render_wheel(cv, 500, 452, S, PLAYER, style='cv2', t=0.2, rot=ROT, bezel='cv2', name='CELL-9',
                   sub='Cv2 neon, full', hp=(36, 50), stickers=True)
    L.render_wheel(cv, 1420, 452, S, PLAYER, style=MIXED, t=0.2, rot=ROT, bezel='cv2', name='CELL-9',
                   sub='mixed picks', hp=(36, 50), stickers=True)
    L.label(cv, 500, 30, 'CV2 NEON  (full wheel)', 32, (255, 255, 255))
    L.label(cv, 1420, 30, 'MIXED  (best pick per program)', 32, (255, 255, 255))
    L.label(cv, 1420, 66, 'ZERO-DAY + VIRUS holo  |  FIREWALL + SANDBOX enamel  |  rest Cv2', 0, (190, 190, 205),
            fnt=L.mono(17 * 2))
    L.caption(cv, 'PLAYER WHEELS', 'left: faceted Cv2 neon + sticker overlay; right: mixed wheel, rare programs get premium finishes',
              y=996)
    save(cv.finish(), 'wheel_player.png')


def wheel_enemy():
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=31, tint=(0.06, 0.045, 0.04))
    L.render_wheel(cv, 720, 448, 0.96, ENEMY, style='meridian', t=0.2, rot=ROT, bezel='cv2_enemy',
                   accent=(255, 138, 31), name='COLLECTIONS\nAGENT', sub='Meridian Freight', hp=(40, 40),
                   enemy=True, mark='meridian')
    L.label(cv, 1500, 60, 'MERIDIAN  /  one material family', 34, (255, 170, 80))
    L.label(cv, 1500, 104, 'orange Cv2 facets on every slice;', 0, (200, 200, 210), fnt=L.mono(18 * 2))
    L.label(cv, 1500, 130, 'type = glyph + program-colour accent', 0, (200, 200, 210), fnt=L.mono(18 * 2))
    L.label(cv, 1500, 156, '(neon rim, inner band, lit facet edges)', 0, (200, 200, 210), fnt=L.mono(18 * 2))
    S = 0.62
    for i, (p, v) in enumerate([('EXPLOIT', '7'), ('FIREWALL', '6'), ('VIRUS', '4')]):
        cx = 1300 + i * 200
        L.render_tile(cv, p, 3, cx, 230, S, 'meridian', t=0.2, value=v)
        L.label(cv, cx, 390, p, 24, (255, 230, 210))
    for i, (p, v) in enumerate([('ZERO-DAY', '14'), ('SANDBOX', '5'), ('NULL', '')]):
        cx = 1300 + i * 200
        L.render_tile(cv, p, 3, cx, 450, S, 'meridian', t=0.2, value=v)
        L.label(cv, cx, 610, p, 24, (255, 230, 210))
    L.label(cv, 1500, 680, 'hazard-stripe machined bezel, notched teeth,', 0, (200, 200, 210), fnt=L.mono(18 * 2))
    L.label(cv, 1500, 706, 'orderly corporate facets (low jitter)', 0, (200, 200, 210), fnt=L.mono(18 * 2))
    L.caption(cv, 'ENEMY: MERIDIAN CORPORATE (Cv2 neon)', 'one cohesive orange facet material; program colour only as the accent',
              y=996, accent=(255, 138, 31))
    save(cv.finish(), 'wheel_enemy.png')


# --------------------------------------------------------------------------- fx
FX_PROGS = ['EXPLOIT', 'ZERO-DAY', 'FIREWALL', 'PROXY', 'VIRUS', 'TROJAN']


def fx_frame(t, W=1100, H=640, S=0.5):
    cv = L.Canvas(W, H, 2)
    L.background(cv, seed=41)
    L.label(cv, 16, 10, 'S_E WILDCARDS  shader loop', 24, anchor='lt')
    for ri, style in enumerate(['holo', 'enamel', 'cv2']):
        top = 70 + ri * 190
        L.label(cv, 16, top + 50, STYLE_INFO[style][0].split(' ')[0], 20, (255, 210, 120), anchor='lt')
        L.label(cv, 16, top + 76, STYLE_INFO[style][2].replace('shader: ', ''), 0, (170, 170, 185), anchor='lt',
                fnt=L.mono(12 * 2))
        for i, p in enumerate(FX_PROGS):
            cx = 250 + i * 150
            L.render_tile(cv, p, 3, cx, top, S, style, t=t)
            if ri == 0:
                pass
            L.label(cv, cx, top + 126, f'{p}', 16, (220, 220, 230))
            L.label(cv, cx, top + 146, FXN[p], 0, (160, 160, 175), fnt=L.mono(11 * 2))
    return cv.finish(glow_r=3)


def make_fx():
    n = 24
    frames = []
    for k in range(n):
        t0 = time.time()
        frames.append(fx_frame(k / n))
        print('frame', k, round(time.time() - t0, 1), flush=True)
    pal_src = Image.new('RGB', (frames[0].width, frames[0].height * 3))
    for i, k in enumerate((0, 8, 16)):
        pal_src.paste(frames[k], (0, i * frames[0].height))
    pal = pal_src.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, 'shader_fx.gif')
    q[0].save(p, save_all=True, append_images=q[1:], duration=83, loop=0, optimize=True, disposal=1)
    print('gif', os.path.getsize(p) // 1024, 'KB')
    # strip: 3 styles x 6 programs x 4 time samples
    cv = L.Canvas(1920, 1080, 2)
    L.background(cv, seed=42)
    L.label(cv, 30, 18, 'SHADER STRIP  /  each program at t = 0, .25, .5, .75  (per style)', 34, anchor='lt')
    S = 0.27
    for ri, style in enumerate(['holo', 'enamel', 'cv2']):
        top = 110 + ri * 320
        L.label(cv, 30, top - 34, STYLE_INFO[style][0] + '   ' + STYLE_INFO[style][2], 22, (255, 210, 120), anchor='lt')
        for i, p in enumerate(FX_PROGS):
            x0 = 40 + i * 312
            for k in range(4):
                L.render_tile(cv, p, 3, x0 + 38 + k * 76, top + 10, S, style, t=k / 4)
            L.label(cv, x0 + 152, top + 100, p, 20, (230, 230, 240))
            L.label(cv, x0 + 152, top + 126, FXN[p], 0, (160, 160, 175), fnt=L.mono(14 * 2))
            for k in range(4):
                L.label(cv, x0 + 38 + k * 76, top + 160, f't={k / 4:.2f}', 0, (120, 120, 135), fnt=L.mono(11 * 2))
    # bigger single-program frames under it: the three style shaders on ZERO-DAY
    save(cv.finish(), 'shader_fx_strip.png')


# --------------------------------------------------------------------------- small + grey
def make_small():
    cv = L.Canvas(1920, 1080, 4)
    L.background(cv, seed=51)
    S = 60 / 360
    cells = [('cv2', 'CV2 NEON', 'cv2'), (MIXED, 'MIXED', 'cv2'), ('holo', 'HOLO', 'holo'), ('enamel', 'ENAMEL', 'enamel')]
    for i, (st, nm, bez) in enumerate(cells):
        cx = 110 + (i % 2) * 430
        cy = 200 + (i // 2) * 430
        L.render_wheel(cv, cx, cy, S, PLAYER, style=st, t=0.2, rot=ROT, bezel=bez, mini=True, lod=1.35, hp=None)
        L.label(cv, cx, cy + 80, f'{nm}  r=60', 18, (230, 230, 240))
    img = cv.finish(glow_r=4)
    # 3x zoom (nearest) next to each small wheel for inspection
    for i in range(4):
        cx = 110 + (i % 2) * 430
        cy = 200 + (i // 2) * 430
        crop = img.crop((cx - 64, cy - 64, cx + 64, cy + 64)).resize((384 // 2 * 1, 384 // 2 * 1), Image.NEAREST)
        crop = img.crop((cx - 64, cy - 64, cx + 64, cy + 64)).resize((256, 256), Image.NEAREST)
        img.paste(crop, (cx + 80, cy - 128))
    # hero greyscale
    cv2 = L.Canvas(960, 1080, 2)
    L.background(cv2, seed=52)
    L.render_wheel(cv2, 480, 470, 0.9, PLAYER, style='cv2', t=0.2, rot=ROT, bezel='cv2', name='CELL-9',
                   sub='Salvaged Rig', hp=(36, 50), stickers=True)
    hero = cv2.finish(grey=True)
    img.paste(hero, (960, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.text((30, 20), 'r = 60 px (LOD: glyph+number x1.35, stronger plate)   + 2x nearest zoom', font=L.font(26),
           fill=(255, 210, 120))
    d.text((990, 20), 'HERO, GREYSCALE (Cv2 neon)', font=L.font(26), fill=(255, 255, 255))
    d.text((30, 1040), 'left: actual pixels at outer radius 60; zoom only enlarges the same pixels', font=L.mono(18),
           fill=(170, 170, 185))
    save(img, 'small_and_grey.png')


def test():
    cv = L.Canvas(1200, 520, 2)
    L.background(cv)
    for i, st in enumerate(['holo', 'enamel', 'cv2', 'meridian']):
        L.render_tile(cv, 'EXPLOIT' if i != 1 else 'FIREWALL', 3, 150 + i * 280, 40, 1.0, st, t=0.1)
    save(cv.finish(), 'scripts/_test.png')


if __name__ == '__main__':
    what = sys.argv[1:] or ['sheets', 'overview', 'player', 'enemy', 'fx', 'small']
    t0 = time.time()
    if 'test' in what:
        test()
    if 'sheets' in what:
        for s in ('holo', 'enamel', 'cv2'):
            sheet_style(s)
    if 'overview' in what:
        sheet_overview()
    if 'player' in what:
        wheel_player()
        wheel_single('cv2', 'CELL-9', 'wheel_player_cv2.png', stickers=True, title='PLAYER: CV2 NEON (master size)',
                     sub='faceted Cv2 neon, each program its own facet pattern; vinyl stickers on the bezel')
        wheel_single(MIXED, 'CELL-9', 'wheel_player_mixed.png', stickers=True, title='PLAYER: MIXED PICKS (master size)',
                     sub='ZERO-DAY + VIRUS holo foil, FIREWALL + SANDBOX enamel, the rest Cv2 neon')
        wheel_single('holo', 'CELL-9', 'wheel_player_holo.png', title='PLAYER: HOLO FOIL (master size)',
                     sub='every slice a foil card; chrome rainbow bezel')
        wheel_single('enamel', 'CELL-9', 'wheel_player_enamel.png', title='PLAYER: ENAMEL PIN (master size)',
                     sub='every slice a hard-enamel pin; gold bezel with enamel inset')
    if 'enemy' in what:
        wheel_enemy()
    if 'fx' in what:
        make_fx()
    if 'small' in what:
        make_small()
    print('done', round(time.time() - t0, 1), 's')
