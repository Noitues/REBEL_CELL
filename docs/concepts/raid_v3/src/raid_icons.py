"""raid_icons: the raid's weapon / device / forecast icons in the bible's glyph grammar (3.5: one flat white silhouette, few dark
cut-outs, the dark rounded outline added at render time, width 0.075 x size, #0C0A16; strokes >= 40/512, cut-outs >= 24/512;
attacks pointed, defences blocky; 16 px rule: soft IoU < ~0.68 against the atlas).

Reused from the LOCKED glyph set (round17_slice_system/glyphs, read-only) where one exists; drawn here where none does (marked
'new' = proposal).  New glyphs are written to raid_v3/icons/ (256 px, white on transparent, alpha = coverage), like the locked set.

    python raid_icons.py        -> raid_v3/icons/*.png (the new ones), raid_v3/icons_key.png (the key sheet + twin check)
"""
import math, os, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

L17 = 'D:/rc_art/art-pass/docs/concepts/round17_slice_system/glyphs/'
OUT = 'D:/rc_art/art-pass/docs/concepts/raid_v3/'
NEWD = OUT + 'icons/'
INKC = (12, 10, 22)

# name -> (source, file or None, meaning)
ICONS = {
    # reused, LOCKED set
    'core':      ('reused', 'picto_hp', 'core / Safehouse health (heart)'),
    'holds':     ('reused', 'placeholder_shield', 'a route held at a wall'),
    'reroll':    ('reused', 'picto_again', 'reroll the shop'),
    'undo':      ('reused', 'picto_spin_ccw', 'undo'),
    'locked':    ('reused', 'state_locked', 'shop locked during the round'),
    'resolving': ('reused', 'picto_spin', 'the round is resolving'),
    'heat':      ('reused', 'placeholder_burn', 'Heat (flame)'),
    'BARRICADE': ('reused', 'picto_block', 'device: barricade (a wall: blocky)'),
    'MINE':      ('reused', 'placeholder_bomb', 'device: mine'),
    # new, proposals
    'SMG':       ('new', None, 'weapon: SMG (compact gun, magazine)'),
    'RAIL':      ('new', None, 'weapon: rail (long gun, forked rails)'),
    'SHOTGUN':   ('new', None, 'weapon: shotgun (pump gun, pellet spread)'),
    'JAMMER':    ('new', None, 'weapon: jammer (handset, antenna, waves)'),
    'SENTRY':    ('new', None, 'device: sentry (turret on a tripod)'),
    'kills':     ('new', None, 'units killed (skull)'),
    'leak':      ('new', None, 'units that leak into the core (drop)'),
    'place':     ('new', None, 'if placed here (arrow into a cell)'),
    'evacuate':  ('new', None, 'EVACUATE: leave the site (door, arrow out)'),
    'tab':       ('new', None, 'the Tab key: unfold the work order'),
}


def _new(name):
    """a new glyph at 512 px: white silhouette (255) with cut-outs (0)"""
    m = Image.new('L', (512, 512), 0); d = ImageDraw.Draw(m)
    if name == 'SMG':
        d.polygon([(40, 196), (96, 196), (104, 214), (372, 214), (372, 236), (474, 236), (474, 274), (372, 274), (372, 300), (104, 300),
                   (40, 262)], fill=255)                               # stock, receiver, barrel
        d.polygon([(232, 296), (296, 296), (316, 452), (256, 460)], fill=255)          # magazine, raked forward
        d.polygon([(118, 296), (178, 296), (164, 410), (100, 404)], fill=255)          # grip
        d.rectangle([150, 236, 330, 258], fill=0)                                     # the ejection slot (cut-out)
    elif name == 'RAIL':
        d.polygon([(20, 228), (150, 212), (150, 312), (20, 300)], fill=255)            # stock
        d.rectangle([140, 196, 300, 316], fill=255)                                   # body
        d.polygon([(296, 184), (470, 196), (500, 214), (296, 236)], fill=255)          # upper rail, pointed
        d.polygon([(296, 276), (470, 292), (500, 310), (296, 330)], fill=255)          # lower rail, pointed
        for x in (334, 384, 434):                                                     # coils bridging the rails
            d.rectangle([x, 230, x + 26, 282], fill=255)
        d.polygon([(170, 312), (226, 312), (214, 420), (156, 414)], fill=255)          # grip
        d.rectangle([166, 236, 270, 260], fill=0)                                     # cut-out
    elif name == 'SHOTGUN':
        d.polygon([(16, 262), (150, 214), (176, 214), (176, 302), (40, 328)], fill=255)  # stock
        d.rectangle([170, 204, 280, 300], fill=255)                                   # receiver
        d.rectangle([270, 206, 396, 244], fill=255)                                   # barrel
        d.rounded_rectangle([280, 252, 380, 296], radius=14, fill=255)                # pump
        d.polygon([(196, 296), (244, 296), (232, 380), (184, 376)], fill=255)          # grip
        for a in (-38, 0, 38):                                                        # the pellet spread
            t = math.radians(a)
            x, y = 408 + 92 * math.cos(t), 225 + 92 * math.sin(t)
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=255)
    elif name == 'JAMMER':
        d.rounded_rectangle([110, 210, 290, 452], radius=34, fill=255)                # handset
        d.rectangle([236, 70, 270, 214], fill=255)                                    # antenna
        d.ellipse([228, 52, 278, 102], fill=255)
        d.rounded_rectangle([146, 252, 254, 320], radius=12, fill=0)                  # screen cut-out
        for r in (110, 180):                                                          # waves off the antenna tip
            d.arc([253 - r, 77 - r, 253 + r, 77 + r], -60, 20, fill=255, width=44)
    elif name == 'SENTRY':
        d.pieslice([120, 120, 380, 380], 180, 360, fill=255)                         # dome
        d.rectangle([120, 244, 380, 284], fill=255)
        d.polygon([(330, 186), (488, 196), (500, 214), (488, 232), (330, 238)], fill=255)  # barrel, pointed
        d.ellipse([214, 174, 262, 222], fill=0)                                       # the eye cut-out
        for (x0, y0, x1, y1) in ((240, 280, 130, 470), (250, 280, 250, 480), (260, 280, 370, 470)):
            d.line([(x0, y0), (x1, y1)], fill=255, width=44)
        d.rectangle([200, 270, 300, 312], fill=255)
    elif name == 'kills':
        d.ellipse([80, 40, 432, 360], fill=255)
        d.rounded_rectangle([150, 300, 362, 470], radius=26, fill=255)
        d.ellipse([140, 170, 236, 266], fill=0); d.ellipse([276, 170, 372, 266], fill=0)
        d.polygon([(256, 280), (232, 326), (280, 326)], fill=0)
        for x in (206, 256, 306):
            d.rectangle([x - 12, 392, x + 12, 470], fill=0)
    elif name == 'leak':
        pts = [(256, 26)] + [(256 + 168 * math.cos(math.radians(t)), 318 + 168 * math.sin(math.radians(t))) for t in range(-28, 209, 6)]
        d.polygon(pts, fill=255)
        d.ellipse([160, 300, 226, 380], fill=0)                                       # highlight cut-out
    elif name == 'place':
        d.polygon([(256, 300), (480, 390), (256, 480), (32, 390)], fill=255)           # the cell
        d.polygon([(256, 344), (390, 390), (256, 436), (122, 390)], fill=0)
        d.polygon([(210, 30), (302, 30), (302, 190), (370, 190), (256, 320), (142, 190), (210, 190)], fill=255)   # the arrow
    elif name == 'evacuate':
        d.rectangle([60, 50, 300, 470], fill=255)                                     # door frame
        d.rectangle([110, 100, 250, 470], fill=0)
        d.polygon([(150, 222), (330, 222), (330, 150), (480, 260), (330, 370), (330, 298), (150, 298)], fill=255)   # out
    elif name == 'tab':
        d.polygon([(40, 210), (300, 210), (300, 130), (430, 256), (300, 382), (300, 302), (40, 302)], fill=255)
        d.rectangle([436, 110, 480, 402], fill=255)
    return m


def mask(name, px):
    """the glyph as an L mask, long side = px"""
    src, fn, _ = ICONS[name]
    if src == 'reused':
        g = Image.open(L17 + fn + '.png').convert('RGBA').split()[3]
    else:
        g = _new(name)
    g = g.crop(g.getbbox())
    k = px / max(g.size)
    return g.resize((max(1, int(round(g.width * k))), max(1, int(round(g.height * k)))), Image.LANCZOS)


def glyph(name, px, col=(255, 255, 255), outline=True, alpha=255):
    """RGBA: the white silhouette (or col) with the bible's dark rounded outline (0.075 x size), long side px"""
    m = mask(name, px)
    ow = max(1, int(round(0.075 * px))) if outline else 0
    W_, H_ = m.width + 2 * ow + 2, m.height + 2 * ow + 2
    base = Image.new('L', (W_, H_), 0); base.paste(m, (ow + 1, ow + 1))
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    if ow:
        o = base.filter(ImageFilter.MaxFilter(2 * ow + 1)).filter(ImageFilter.GaussianBlur(ow * 0.25))
        im.paste(Image.new('RGBA', (W_, H_), INKC + (alpha,)), (0, 0), o)
    col_l = Image.new('RGBA', (W_, H_), tuple(col) + (alpha,))
    im.paste(col_l, (0, 0), base)
    return im


def soft16(name):
    m = mask(name, 15)
    c = Image.new('L', (16, 16), 0); c.paste(m, ((16 - m.width) // 2, (16 - m.height) // 2))
    a = np.asarray(c.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
    return a


def twin_check():
    """soft IoU at 16 px of every raid icon against the whole locked set and the other raid icons"""
    atlas = {}
    for fn in os.listdir(L17):
        if fn.endswith('.png'):
            g = Image.open(L17 + fn).convert('RGBA').split()[3]
            g = g.crop(g.getbbox()); k = 15 / max(g.size)
            g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)
            c = Image.new('L', (16, 16), 0); c.paste(g, ((16 - g.width) // 2, (16 - g.height) // 2))
            atlas[fn[:-4]] = np.asarray(c.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255
    res = {}
    for n, (src, fn, _) in ICONS.items():
        a = soft16(n)
        best = (0, '')
        others = dict(atlas)
        others.update({'raid:' + m: soft16(m) for m in ICONS if m != n and ICONS[m][0] == 'new'})
        for k, b in others.items():
            if src == 'reused' and k == fn:
                continue
            iou = float(np.minimum(a, b).sum() / max(np.maximum(a, b).sum(), 1e-6))
            if iou > best[0]:
                best = (iou, k)
        res[n] = best
    return res


def key_sheet():
    os.makedirs(NEWD, exist_ok=True)
    for n, (src, fn, _) in ICONS.items():
        if src == 'new':
            m = _new(n).resize((256, 256), Image.LANCZOS)
            im = Image.new('RGBA', (256, 256), (255, 255, 255, 0)); im.putalpha(m)
            im.save(NEWD + 'raid_%s.png' % n.lower())
    tw = twin_check()
    names = list(ICONS)
    cols, cw, ch = 4, 470, 132
    rows = (len(names) + cols - 1) // cols
    sh = Image.new('RGB', (cols * cw + 24, rows * ch + 120), (24, 22, 32))
    d = ImageDraw.Draw(sh)
    fa = ImageFont.truetype('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/Anton-Regular.ttf', 30) if os.path.exists('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/Anton-Regular.ttf') else ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 26)
    fm = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 17)
    d.text((14, 12), 'Raid icons, bible glyph grammar: reused from the LOCKED set (teal) and new proposals (pink)', font=fa, fill=(236, 236, 240))
    d.text((14, 58), 'each at 34 px (target size on screen) and 16 px (the 16 px rule); max soft IoU at 16 px vs the locked set + the other new icons (< 0.68 passes)',
           font=fm, fill=(170, 170, 184))
    for k, n in enumerate(names):
        src, fn, mean = ICONS[n]
        x, y = 14 + (k % cols) * cw, 100 + (k // cols) * ch
        d.rounded_rectangle([x, y, x + cw - 14, y + ch - 12], radius=10, fill=(34, 32, 44), outline=((90, 214, 200) if src == 'reused' else (255, 110, 196)), width=2)
        g = glyph(n, 68); sh.paste(g, (x + 12 + (76 - g.width) // 2, y + 12 + (76 - g.height) // 2), g)
        g = glyph(n, 34); sh.paste(g, (x + 100 + (40 - g.width) // 2, y + 30 + (40 - g.height) // 2), g)
        g = glyph(n, 16); sh.paste(g, (x + 150 + (20 - g.width) // 2, y + 40 + (20 - g.height) // 2), g)
        iou, who = tw[n]
        d.text((x + 186, y + 12), n, font=fa if len(n) < 12 else fm, fill=(236, 236, 240))
        d.text((x + 186, y + 54), ('reused: ' + fn) if src == 'reused' else 'new (proposal)', font=fm, fill=(90, 214, 200) if src == 'reused' else (255, 140, 200))
        d.text((x + 186, y + 76), 'IoU %.2f %s' % (iou, who[:22]), font=fm, fill=(255, 120, 110) if iou >= 0.68 else (170, 170, 184))
        d.text((x + 12, y + 96), mean[:52], font=fm, fill=(150, 150, 164))
    sh.save(OUT + 'icons_key.png')
    print('ok', OUT + 'icons_key.png')
    for n in names:
        print('%-10s %-7s IoU %.2f vs %s' % (n, ICONS[n][0], tw[n][0], tw[n][1]))


if __name__ == '__main__':
    key_sheet()
