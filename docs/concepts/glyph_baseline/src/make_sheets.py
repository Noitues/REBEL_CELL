"""Glyph / unit-picture baseline (designer ruling 8, 2026-11-16): the old pass is the baseline; only new or changed
items go to the designer. Reads the game's shipped assets (a checkout of port-campaign-b d44936b37) and the art-pass
drafts, writes baseline_sheet.jpg (kept, small) and review_sheet.jpg (new / changed, larger, one line why each).

Run: python src/make_sheets.py [GAME_CHECKOUT]   (from docs/concepts/glyph_baseline; default D:/rc_art/jack_time)
Solace only: no other corporation's icons are read.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPTS = os.path.dirname(HERE)
GAME = sys.argv[1] if len(sys.argv) > 1 else 'D:/rc_art/jack_time'
A = GAME + '/assets/'
FONTS = A + 'fonts/'
ANTON = FONTS + 'Anton-Regular.ttf'
MONO = FONTS + 'ShareTechMono-Regular.ttf'
if not os.path.exists(MONO):
    MONO = FONTS + 'CourierPrime-Regular.ttf'

BG = (16, 16, 22)
TILE = (34, 38, 50)
EDGE = (70, 78, 96)
TEXT_HI = (238, 240, 246)
TEXT_MID = (160, 166, 182)
KEEP_C = (64, 200, 180)
NEW_C = (255, 92, 178)
CHG_C = (255, 176, 64)

# raid_look.tres (port-campaign-b): the B classes' sticker colours and the art-picked glyphs / beacons
CLASSES = [
    ('GUNNER', (246, 115, 50), 'picto_target', 'breaker', (255, 61, 168)),
    ('HACKER', (64, 130, 242), 'placeholder_key', 'ghost', (92, 224, 255)),
    ('FIXER', (76, 193, 90), 'placeholder_vault', 'rigger', (122, 224, 122)),
    ('SAPPER', (154, 103, 230), 'placeholder_bomb', 'wrecker', (255, 110, 51)),
]
CLASS_WHY = {
    'GUNNER': 'CHANGE: beacon is the Breaker\'s (crowbar emblem, pink); Gunner\'s sticker is orange. Glyph (target) fine.',
    'HACKER': 'CHANGE (small): beacon is the Ghost\'s emblem, cyan vs Hacker blue. Glyph (key) fine.',
    'FIXER': 'CONFIRM: beacon is the Rigger\'s emblem (green matches). Glyph = vault: art\'s pick.',
    'SAPPER': 'CHANGE: glyph = bomb, the same as MINE and BOMBARD; beacon is the Wrecker\'s (orange vs violet).',
}
UNIT_TYPES = [('fast', 'Bike, Flanker'), ('flying', 'Drone, EMP Drone'), ('heavy', 'Trooper, Riot, Sniper, Heavy'),
              ('special', 'Mortar, Wrecker')]
DEV_KEEP = [('BARRICADE', 'picto_block'), ('MINE', 'placeholder_bomb')]
DEV_EMPTY = [('BEACON', 'boosts damage'), ('DECOY', 'draws ranged fire'), ('DRONE', 'Repair Drone'), ('LURE', 'catches ground'),
             ('MAST', 'Relay Mast')]
WPN_DRAFT = [('SMG', 'raid_smg'), ('RAIL', 'raid_rail'), ('SHOTGUN', 'raid_shotgun'), ('JAMMER', 'raid_jammer')]
WPN_EMPTY = ['BARRIER', 'BLADE', 'BOUNTYG', 'BULWARK', 'CHARGE', 'COIL', 'CROSS', 'DRONES', 'FLAK', 'FLAMER', 'GL',
             'LANCE', 'LANEG', 'LONG', 'MARKS', 'MORTAR', 'NAIL', 'PISTOL', 'PULSE', 'SLICK', 'WIRE']
HUD_DRAFT = [('kills', 'raid_kills'), ('leak', 'raid_leak'), ('place', 'raid_place'), ('EVACUATE', 'raid_evacuate'),
             ('Tab', 'raid_tab'), ('SENTRY', 'raid_sentry')]
CHAIN = [('HELD', 'placeholder_shield', ''), ('BOMBARD', 'placeholder_bomb', 'same as MINE, SAPPER'),
         ('BLOCK', 'picto_block', 'same as BARRICADE'), ('SNIPE', 'raid_rail', 'same as RAIL')]
LOCKED = [('core', 'picto_hp'), ('holds', 'placeholder_shield'), ('reroll', 'picto_again'), ('undo', 'picto_spin_ccw'),
          ('locked', 'state_locked'), ('resolving', 'picto_spin'), ('Heat', 'placeholder_burn')]


def font(p, s):
    return ImageFont.truetype(p, s)


def glyph(name, px, col=(255, 255, 255)):
    """a raid glyph (white, alpha = coverage) tinted, at px"""
    im = Image.open(A + 'raid/glyphs/%s.png' % name).convert('RGBA').resize((px, px), Image.LANCZOS)
    out = Image.new('RGBA', im.size, col + (0,))
    out.putalpha(im.split()[3])
    return out


def on_tile(img, size, fill=TILE, edge=EDGE, dashed=False):
    t = Image.new('RGBA', (size, size), fill + (255,))
    d = ImageDraw.Draw(t)
    if dashed:
        for k in range(0, size, 10):
            for a, b in (((k, 0), (k + 5, 0)), ((k, size - 1), (k + 5, size - 1)), ((0, k), (0, k + 5)), ((size - 1, k), (size - 1, k + 5))):
                d.line([a, b], fill=edge, width=2)
    else:
        d.rectangle([0, 0, size - 1, size - 1], outline=edge, width=2)
    if img is not None:
        im = img.copy()
        im.thumbnail((size - 12, size - 12), Image.LANCZOS)
        t.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return t


def chip(name, px, col):
    """a class die-cut stand-in: the class colour plate with its white glyph"""
    t = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rounded_rectangle([2, 2, px - 3, px - 3], radius=px // 6, fill=(250, 250, 252, 255))
    d.rounded_rectangle([6, 6, px - 7, px - 7], radius=px // 7, fill=col + (255,))
    g = glyph(name, int(px * 0.62))
    t.alpha_composite(g, ((px - g.width) // 2, (px - g.height) // 2))
    return t


def beacon(cls):
    strip = Image.open(A + 'raid/beacons/%s.png' % cls).convert('RGBA')
    fr = strip.crop((0, 0, 220, 260))
    bb = fr.getbbox()
    return fr.crop(bb) if bb else fr


def bust(cls):
    return Image.open(A + 'portraits/busts_%s.png' % cls).convert('RGBA').crop((0, 0, 240, 266))


def unit(t, status='none', hp=100):
    return Image.open(A + 'raid/icons/solace_%s_%s_hp%03d.png' % (t, status, hp)).convert('RGBA')


def devkey_crop(box, scale):
    im = Image.open(CONCEPTS + '/raid_v3/set8/r8_devhere_key.png').convert('RGBA').crop(box)
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)


def label(d, xy, s, f, col=TEXT_HI, anchor='la'):
    d.text(xy, s, font=f, fill=col, anchor=anchor)


# --------------------------------------------------------------------------------------------- baseline (kept)
def baseline(path):
    W = 820
    tile = 84
    fa, fs, ft = font(ANTON, 34), font(MONO, 14), font(ANTON, 22)
    groups = []
    groups.append(('Corp units, Solace v4 icons (round 22; bible 4.8, designer ruling 2 of 2026-11-15)',
                   [(unit(t), t) for t, _ in UNIT_TYPES] +
                   [(unit('heavy', 'frozen'), 'held ring'), (unit('heavy', 'slowed'), 'slowed ring'), (unit('heavy', 'none', 50), 'health 50%')]))
    groups.append(('LOCKED glyph set (round 17), reused in the raid', [(glyph(n, 128), w) for w, n in LOCKED]))
    groups.append(('Devices with a LOCKED glyph', [(glyph(n, 128), w) for w, n in DEV_KEEP]))
    H = 110 + len(groups) * (tile + 70) + 40
    sh = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(sh)
    label(d, (24, 18), 'Glyph / unit-picture BASELINE: kept as is, no review needed', fa)
    label(d, (24, 62), 'game assets @ port-campaign-b d44936b37 (assets/raid/icons, assets/raid/glyphs); Solace only', fs, TEXT_MID)
    y = 104
    for title, items in groups:
        label(d, (24, y), title, ft, KEEP_C)
        y += 34
        x = 24
        for im, w in items:
            sh.alpha_composite(on_tile(im, tile), (x, y))
            label(d, (x + tile // 2, y + tile + 4), w, fs, TEXT_MID, 'ma')
            x += tile + 22
        y += tile + 36
    sh.convert('RGB').save(path, quality=92)
    print('ok', path)


# --------------------------------------------------------------------------------------------- review (new / changed)
def review(path):
    W = 1900
    fa, fb, fs, ft = font(ANTON, 36), font(ANTON, 24), font(MONO, 15), font(ANTON, 20)
    rows = []

    def row(title, tag, height, draw):
        rows.append((title, tag, height, draw))

    # 1. classes
    def classes(sh, d, y):
        x = 24
        for name, col, g, bcn, bcol in CLASSES:
            label(d, (x, y), name, fb, col)
            sh.alpha_composite(on_tile(chip(g, 110, col), 130), (x, y + 34))
            label(d, (x, y + 168), 'glyph ' + g + ' | beacon ' + bcn, fs, TEXT_MID)
            sh.alpha_composite(on_tile(beacon(bcn), 130), (x + 140, y + 34))
            sw = Image.new('RGBA', (60, 14), col + (255,))
            sh.alpha_composite(sw, (x + 140, y + 192))
            sw2 = Image.new('RGBA', (60, 14), bcol + (255,))
            sh.alpha_composite(sw2, (x + 210, y + 192))
            label(d, (x, y + 191), 'sticker | beacon', fs, TEXT_MID)
            words = CLASS_WHY[name]
            lines, cur = [], ''
            for w in words.split(' '):
                if len(cur) + len(w) > 44:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + ' ' + w).strip()
            lines.append(cur)
            for k, ln in enumerate(lines):
                label(d, (x, y + 214 + k * 18), ln, fs, CHG_C if 'CHANGE' in words else TEXT_HI)
            x += 470
    row('1  The four Campaign B classes: glyph, sticker colour, beacon (old pass = the 8 netrun classes; B maps 4 onto them)',
        'CHANGE', 290, classes)

    # 2. pinned
    def pinned(sh, d, y):
        sh.alpha_composite(on_tile(None, 130, dashed=True, edge=NEW_C), (24, y))
        label(d, (89, y + 56), 'PINNED', fb, NEW_C, 'ma')
        label(d, (174, y + 10), 'NEW, empty slot. The operative fixed on its site is "pinned" (designer ruling 6). The CREW sticker', fs)
        label(d, (174, y + 30), 'shows the station in red pencil and the map its beacon; nothing marks "pinned" itself.', fs)
        label(d, (174, y + 50), 'Needed: one mark for the sticker and the beacon cap (art proposes nothing yet; no old-pass glyph fits).', fs)
    row('2  Pinned operative', 'NEW', 150, pinned)

    # 3. unit kinds
    def units(sh, d, y):
        x = 24
        for t, kinds in UNIT_TYPES:
            sh.alpha_composite(on_tile(unit(t), 130), (x, y))
            label(d, (x + 65, y + 136), t, fs, TEXT_HI, 'ma')
            label(d, (x + 65, y + 156), kinds, fs, CHG_C, 'ma')
            x += 300
        label(d, (24, y + 184), 'CONFIRM / CHANGE: 10 Solace unit kinds share the 4 v4 type icons (art\'s map in raid_look.tres). Trooper, Riot, Sniper', fs)
        label(d, (24, y + 204), 'and Heavy look alike; the set 7 plates drew Riot (shield plate) and Sniper (barrel) as their own shapes. One mark per kind?', fs)
    row('3  Corp units by kind (Solace)', 'CHANGE', 240, units)

    # 4. devices
    def devices(sh, d, y):
        x = 24
        items = [(glyph('raid_sentry', 128), 'SENTRY', 'draft: set 7 proposal'),
                 (devkey_crop((300, 40, 356, 100), 2.0), 'TAR', 'draft: set 8 badge mark'),
                 (devkey_crop((205, 505, 320, 615), 1.0), 'SHOCK fence', 'draft: set 8 badge mark'),
                 (devkey_crop((465, 505, 580, 615), 1.0), 'GATE', 'draft: set 8 badge mark')]
        for im, w, why in items:
            sh.alpha_composite(on_tile(im, 130, edge=NEW_C), (x, y))
            label(d, (x + 65, y + 136), w, fs, TEXT_HI, 'ma')
            label(d, (x + 65, y + 156), why, fs, NEW_C, 'ma')
            x += 196
        for w, why in DEV_EMPTY:
            sh.alpha_composite(on_tile(None, 130, dashed=True, edge=NEW_C), (x, y))
            label(d, (x + 65, y + 56), w, ft, NEW_C, 'ma')
            label(d, (x + 65, y + 136), why, fs, TEXT_MID, 'ma')
            label(d, (x + 65, y + 156), 'NEW, empty', fs, NEW_C, 'ma')
            x += 196
        label(d, (24, y + 186), 'v42 has 11 devices; BARRICADE and MINE have LOCKED glyphs (baseline). TAR and SHOCK are weak at 1:1 (set 8 note): need real glyphs.', fs)
    row('4  Devices (v42 rules)', 'NEW', 220, devices)

    # 5. weapons
    def weapons(sh, d, y):
        x = 24
        for w, n in WPN_DRAFT:
            sh.alpha_composite(on_tile(glyph(n, 128), 100, edge=NEW_C), (x, y))
            label(d, (x + 50, y + 104), w, fs, TEXT_HI, 'ma')
            x += 116
        label(d, (x - 4, y + 124), '', fs)
        x0 = x + 20
        for k, w in enumerate(WPN_EMPTY):
            cx = x0 + (k % 11) * 116
            cy = y + (k // 11) * 84
            t = on_tile(None, 56, dashed=True, edge=NEW_C)
            sh.alpha_composite(t, (cx, cy))
            label(d, (cx + 28, cy + 58), w, fs, TEXT_MID, 'ma')
        label(d, (24, y + 172), 'NEW: 4 of 25 weapons have a glyph (set 7 proposals, in the game but never reviewed); 21 show their abbreviation on the gear tag.', fs)
    row('5  Raid weapons', 'NEW', 200, weapons)

    # 6. hud proposals
    def hud(sh, d, y):
        x = 24
        for w, n in HUD_DRAFT[:-1]:
            sh.alpha_composite(on_tile(glyph(n, 128), 100, edge=NEW_C), (x, y))
            label(d, (x + 50, y + 104), w, fs, TEXT_HI, 'ma')
            x += 130
        label(d, (x + 10, y + 30), 'NEW (drafts in the game): set 7 proposals in the bible glyph grammar, 16 px twin check passed', fs)
        label(d, (x + 10, y + 50), '(raid_v3/icons_key.png); not yet seen by the designer as glyphs.', fs)
    row('6  Raid strip / order glyphs from set 7', 'NEW', 140, hud)

    # 7. chain tokens
    def chain(sh, d, y):
        x = 24
        for w, n, why in CHAIN:
            sh.alpha_composite(on_tile(glyph(n, 128), 100, edge=CHG_C), (x, y))
            label(d, (x + 50, y + 104), w, fs, TEXT_HI, 'ma')
            label(d, (x + 50, y + 122), why, fs, CHG_C, 'ma')
            x += 210
        label(d, (x + 10, y + 30), 'CHANGE: chain tokens are art\'s picks from other glyphs; BOMBARD, BLOCK and SNIPE', fs)
        label(d, (x + 10, y + 50), 'reuse a device / weapon glyph, so a chain pill and a device read the same.', fs)
    row('7  Raid chain tokens', 'CHANGE', 160, chain)

    # 8. class pictures
    def pictures(sh, d, y):
        x = 24
        for name, col, g, bcn, bcol in CLASSES:
            sh.alpha_composite(on_tile(bust(bcn), 150, fill=(230, 230, 236)), (x, y))
            label(d, (x + 75, y + 156), '%s ? (%s bust)' % (name, bcn), fs, TEXT_HI, 'ma')
            x += 190
        label(d, (x + 10, y + 30), 'NEW: the class pick, HQ roster and recruit are text only. The old-pass busts (rounds 38-39)', fs)
        label(d, (x + 10, y + 50), 'are the 8 netrun classes, coloured as those classes. Reuse the mapped four re-tinted, or', fs)
        label(d, (x + 10, y + 70), 'no class pictures in Campaign B? (designer call)', fs)
    row('8  Class pictures (portrait busts)', 'NEW', 190, pictures)

    H = 100 + sum(h + 52 for _, _, h, _ in rows) + 20
    sh = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(sh)
    label(d, (24, 16), 'Glyph / unit pictures: NEW or CHANGED, for the designer', fa)
    label(d, (24, 62), 'baseline = the old pass (kept items on baseline_sheet.jpg). pink = new (draft or empty slot), orange = change / confirm. Solace only.', fs, TEXT_MID)
    y = 100
    for title, tag, h, draw in rows:
        col = NEW_C if tag == 'NEW' else CHG_C
        d.rectangle([12, y - 4, W - 12, y + h + 40], outline=col, width=2)
        label(d, (24, y + 2), title, fb, col)
        draw(sh, d, y + 40)
        y += h + 52
    sh.convert('RGB').save(path, quality=92)
    print('ok', path)


if __name__ == '__main__':
    baseline(os.path.join(HERE, 'baseline_sheet.jpg'))
    review(os.path.join(HERE, 'review_sheet.jpg'))
