"""B-107 item 3: the raid as five separate screens (review, shop, place, execute, result) + the lost result
("TARGET ACQUIRED" in corporate ink). 1920 x 1080 concept plates, PIL only. Run: python raid_screens.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

UNITS = {  # display, icon, hp, armor, line
    'TROOPER': ('heavy', 8, 0, 'Walks 1 a tick. Smashes 1.'),
    'RIOT': ('heavy', 11, 2, 'Armor 2: 1-2 dmg hits do nothing.'),
    'SNIPER': ('heavy', 7, 0, 'Shoots the nearest operator each tick.'),
    'BIKE': ('fast', 7, 0, '2 cells a tick.'),
    'DRONE': ('flying', 5, 0, 'Flies over barricades.'),
    'HEAVY': ('heavy', 18, 1, 'Armor 1. Smashes 3.'),
}
ROUNDS = [('1', [('TROOPER', 5), ('BIKE', 3)]), ('2', [('TROOPER', 4), ('SNIPER', 2), ('DRONE', 3)]),
          ('3', [('RIOT', 2), ('HEAVY', 2), ('TROOPER', 4)]), ('4', [('HEAVY', 1), ('BIKE', 2), ('DRONE', 6)])]


def round_tab(img, rnd='1', of='4', x=1580, y=18, label=None):
    """The folded work order corner (set 8), top right: ROUND n . of; Tab unfolds it."""
    paper(img, [x, y, x + 300, y + 74], rot=1.2, seed=8)
    ellipse(img, [x + 14, y + 12, x + 64, y + 62], outline=CORP_INK, width=4)
    text(img, (x + 39, y + 38), 'S', font('anton', 30), CORP_INK, 'mm')
    text(img, (x + 80, y + 38), label or ('ROUND %s . %s' % (rnd, of)), font('anton', 36), INK, 'lm')
    chip(img, x - 62, y + 22, 'TAB', font('mono', 15), CYAN, bg=NAVY, edge=CYAN, pad=8)


def unit_card(img, x, y, name, count, w=200, h=250, rot=0, seen=True):
    """Enemy unit as a corp ID file (pale corp paper, corp ink stripe, the round 22 Solace icon)."""
    ic, hp, ar, ln = UNITS[name]
    L = layer(w + 30, h + 30); o = 15
    rrect(L, [o, o, o + w, o + h], 8, fill=(222, 228, 220, 255), outline=(60, 80, 70, 255), width=2)
    rect(L, [o, o, o + w, o + 34], fill=CORP_INK)
    text(L, (o + 12, o + 17), 'UNIT FILE', font('mono', 15), (220, 255, 235, 255), 'lm')
    text(L, (o + w - 12, o + 17), 'SOLACE', font('anton', 18), (220, 255, 235, 255), 'rm')
    ui = unit_icon(ic, 96)
    L.alpha_composite(ui, (S(o + w / 2 - 48), S(o + 40)))
    text(L, (o + w / 2, o + 150), name, font('anton', 30), INK, 'mm')
    # hp pips (one pip per hp, two rows of 9 at most)
    yy = o + 172
    put_glyph(L, 'picto_hp', o + 18, yy + 9, 18, (190, 40, 60, 255))
    text(L, (o + 30, yy + 9), str(hp), font('anton', 20), INK, 'lm')
    step = (w - 70) / 9
    for k in range(min(hp, 18)):
        px = o + 58 + (k % 9) * step; py = yy + 1 + (k // 9) * 11
        rect(L, [px, py, px + step - 3, py + 8], fill=(190, 40, 60, 255))
    yy += 28
    if ar:
        put_glyph(L, 'placeholder_shield', o + 18, yy + 10, 18, (40, 70, 130, 255))
        text(L, (o + 32, yy + 10), 'ARMOR %d' % ar, font('anton', 18), (40, 70, 130, 255), 'lm')
        yy += 22
    for k, ln_ in enumerate(wrap(ln, font('courier', 14), w - 24)[:2]):
        text(L, (o + 12, yy + 8 + k * 16), ln_, font('courier', 14), (60, 70, 66, 255), 'lm')
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(5, 8, 12, 140))
    sticker(img, 'x%d' % count, x + w - 6, y + 62, 54, 38, YEL, None, rot=8, size=28)


# ================================================================ (a) REVIEW
def review():
    img = bg_raid(.36)
    tint = Image.new('RGBA', img.size, (120, 0, 10, 46)); img.alpha_composite(tint)
    hud_strip(img); raid_steps(img, 0); round_tab(img, label='INCOMING')
    # the intercepted work order, unfolded, big (corp paper)
    X0, Y0, X1, Y1 = 40, 120, 760, 1040
    paper(img, [X0, Y0, X1, Y1], rot=-1.2, clip=True, seed=11)
    L = layer(X1 - X0, Y1 - Y0)
    text(L, (40, 40), 'SOLACE', font('anton', 54), CORP_INK)
    text(L, (250, 70), 'Field Operations', font('mono', 22), CORP_INK, 'ls')
    line(L, [(40, 108), (680, 108)], CORP_INK, 3)
    text(L, (40, 126), 'WORK ORDER', font('mono', 20), (70, 70, 70, 255))
    text(L, (680, 126), 'SOL-WO-2611-07', font('mono', 20), (70, 70, 70, 255), 'ra')
    text(L, (40, 158), 'RAID ORDER . STATIC ALLEY', font('anton', 44), INK)
    rows = [('TARGET', 'Cell safehouse'), ('TRIGGER', 'Heat 50 crossed'), ('ENTRY', 'A (north), B (dock road)'), ('WINDOW', '4 rounds')]
    yy = 230
    for k, v in rows:
        text(L, (40, yy), k, font('mono', 20), (90, 90, 90, 255))
        text(L, (230, yy - 2), v, font('courier', 24), INK)
        yy += 36
    rect(L, [430, 228, 560, 256], fill=INK)          # redaction
    yy += 12
    for rn, us in ROUNDS:
        line(L, [(40, yy), (680, yy)], (180, 175, 160, 255), 1)
        text(L, (40, yy + 12), 'ROUND %s' % rn, font('anton', 30), INK)
        n = sum(c for _, c in us)
        text(L, (190, yy + 18), '%d units' % n, font('mono', 20), (90, 90, 90, 255))
        ux = 320
        for u, c in us:
            ic = unit_icon(UNITS[u][0], 60)
            L.alpha_composite(ic, (S(ux), S(yy - 2)))
            text(L, (ux + 58, yy + 28), 'x%d' % c, font('anton', 26), INK, 'lm')
            ux += 118
        yy += 70
    line(L, [(40, yy), (680, yy)], (180, 175, 160, 255), 1)
    text(L, (40, yy + 30), 'AUTHORISED', font('mono', 20), (90, 90, 90, 255))
    rect(L, [210, yy + 26, 400, yy + 56], fill=INK)
    text(L, (40, Y1 - Y0 - 60), 'INTERNAL . PAGE 1 OF 1', font('mono', 17), (120, 120, 120, 255))
    rotate_paste(img, L, (X0 + X1) / 2, (Y0 + Y1) / 2, -1.2, shadow=False)
    stamp(img, 'INTERCEPTED', 560, 860, RED, rot=-9, size=58)
    # our pencil on their paper
    pencil_circle(img, 560, 676, 170, 34, YEL, 5, seed=7)
    hand(img, (96, 905), '2 heavies in R3: bring AP', 32, YEL, rot=-3)
    arrow_hand(img, [(330, 880), (380, 760), (430, 700)], YEL, 5)
    tick(img, 700, 452, 24, LIME)
    # ROUTE monitor: the raid on the city (set 8 plan board)
    glass(img, [800, 112, 1890, 610], title='ROUTE  .  2 entries  .  13 street slots  .  ends at the Cell HQ', tsize=19)
    rt = load_bg('raid_v3/set8/r8_plan.png').crop((S(430), S(70), S(1470), S(630)))
    rt = rt.resize((S(1060), S(430)), Image.LANCZOS)
    img.paste(rt, (S(815), S(160)))
    rect(img, [815, 160, 1875, 590], outline=(92, 225, 255, 120), width=2)
    hand(img, (1500, 520), 'B leaks 2 here', 28, YEL, rot=-3)
    arrow_hand(img, [(1490, 520), (1420, 490), (1392, 462)], YEL, 5)
    chip(img, 830, 550, 'HQ 20/20', font('anton', 22), PINK, bg=INK, edge=PINK)
    # THREAT row: unit files
    glass(img, [800, 626, 1890, 966], title='THREAT  .  33 units over 4 rounds  .  the corp sends', tsize=19, rule=RED)
    us = [('TROOPER', 13), ('BIKE', 5), ('SNIPER', 2), ('DRONE', 9), ('RIOT', 2), ('HEAVY', 3)]
    for i, (u, c) in enumerate(us):
        unit_card(img, 822 + i * 177, 676, u, c, w=160, h=272, rot=(-1.5, 1, -0.5, 1.5, -1, .8)[i])
    die_sticker(img, 'TO THE SHOP', 1730, 1022, 260, 60, LIME, rot=-2, size=38)
    text(img, (1560, 1024), 'SPACE', font('mono', 16), DIM, 'rm')
    chip(img, 820, 1000, 'EVACUATE', font('anton', 22), RED, bg=NAVY, edge=RED, pad=12)
    text(img, (970, 1022), 'ends the raid at once (v39 rule)', font('plex', 18), DIM, 'lm')
    frame_caption(img, 'B-107 raid screen 1/5  REVIEW the incoming raid  (concept plate, art-pass 2026-11-16)')
    return finish_save(img, 'raid_1_review.png')


# ================================================================ (b) SHOP
DEVICES = [('BARRICADE', 'picto_block', 3), ('MINE', 'placeholder_bomb', 2), ('SENTRY', 'raid_sentry', 4),
           ('BEACON', 'picto_target', 5), ('MAST', 'raid_jammer', 3), ('TAR', 'placeholder_burn', 3)]
SHOPW = [('Breach Shotgun', 'BLAST', 4, 1, 2, 2, 1, ('SHORT',), '2 blasts at reach 1. BRAWLER makes a BREACHER.', 'SAPPER'),
         ('Slick Grenade', 'BLAST', 4, 1, 1, 1, 2, ('SPLASH', 'SLOW'), 'Hits the whole cell for 1, slows each.', None),
         ('Mortar Tube', 'HEAVY', 5, 1, 2, 1, 5, ('SPLASH', 'DIAMOND'), 'A shell on a diamond of reach 5.', 'SAPPER'),
         ('SMG', 'AUTO', 3, 2, 1, 3, 1, ('AUTO',), '3 quick shots.', 'HACKER'),
         ('Marksman Rifle', 'HEAVY', 4, 1, 3, 1, 2, ('QUIET',), '1 quiet slug; +1 reach is LONG.', 'GUNNER')]


def device_tile(img, x, y, name, g, cost, w=150, h=150, n_owned=0):
    rrect(img, [x, y, x + w, y + h], 12, fill=WHITE)
    yel = name == 'BARRICADE'
    rrect(img, [x + 4, y + 4, x + w - 4, y + h - 4], 9, fill=(255, 214, 40, 255) if yel else (36, 32, 54, 255))
    if yel:
        rect(img, [x + 4, y + h - 40, x + w - 4, y + h - 4], fill=INK)
    put_glyph(img, g, x + w / 2, y + 62, 74, INK if yel else WHITE)
    text(img, (x + w / 2, y + h - 22), name, font('anton', 22), YEL if yel else WHITE, 'mm')
    price_tag(img, x + w - 12, y + 10, cost, rot=12, w=76, h=36)
    if n_owned:
        chip(img, x + 8, y + 8, 'x%d' % n_owned, font('anton', 18), INK, bg=LIME, pad=6)


def tray_op(img, x, y, name, cls, lvl, idx, weapons, w=330, h=184, merge=None, state=None):
    c = CLASS[cls]['col']
    rrect(img, [x, y, x + w, y + h], 14, fill=WHITE)
    rrect(img, [x + 4, y + 4, x + w - 4, y + h - 4], 11, fill=INK)
    art = portrait_art(cls, 120, h - 16, idx)
    m = Image.new('L', art.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, art.width, art.height), radius=S(8), fill=255)
    img.paste(art, (S(x + 8), S(y + 8)), m)
    class_badge(img, cls, x + 16, y + 18, 20, rot=-8)
    text(img, (x + 140, y + 30), name, font('anton', 34), WHITE, 'lm')
    text(img, (x + w - 16, y + 32), 'LV%d' % lvl, font('anton', 22), c, 'rm')
    text(img, (x + 140, y + 60), cls, font('mono', 16), c, 'lm')
    n = len(weapons)
    sw = (w - 150 - (n - 1) * 8) / n
    for i, wv in enumerate(weapons):
        sx = x + 140 + i * (sw + 8); sy = y + 82
        if wv:
            wn, st = wv
            rrect(img, [sx, sy, sx + sw, sy + 86], 8, fill=WHITE, outline=INK, width=2)
            put_glyph(img, WGLYPH.get(wn, 'raid_smg'), sx + sw / 2, sy + 34, 52, INK)
            stars(img, sx + sw / 2 - 26, sy + 62, st, 3, 15)
        else:
            rrect(img, [sx, sy, sx + sw, sy + 86], 8, fill=(30, 26, 44, 255), outline=(110, 110, 140, 255), width=2)
            text(img, (sx + sw / 2, sy + 43), 'SLOT', font('mono', 15), (130, 130, 160, 255), 'mm')
    if merge:
        hand(img, (x + 150, y - 30), merge, 26, LIME, rot=-3)


def shop():
    img = bg_raid(.22, blur=5)
    hud_strip(img, credits=12); raid_steps(img, 1); round_tab(img, '1', '4')
    # left: devices + upgrades
    glass(img, [24, 112, 400, 842], title='DEVICES', tsize=22)
    for i, (n, g, c) in enumerate(DEVICES):
        device_tile(img, 44 + (i % 2) * 176, 166 + (i // 2) * 176, n, g, c, n_owned=1 if n == 'BARRICADE' else 0)
    text(img, (44, 704), 'UPGRADES', font('mono', 20), CYAN)
    ux, uy = 44, 734
    for s_, c in (('REACH +1  2', LIME), ('BELT  2', LIME), ('FORTIFY  4', LIME), ('TRAIN MAKO  5', LIME)):
        nx = chip(img, ux, uy, s_ + ' cr', font('anton', 20), INK, bg=WHITE, edge=INK, pad=10)
        ux = nx + 10
        if ux > 300:
            ux, uy = 44, uy + 44
    # centre: the weapon cards
    text(img, (440, 118), 'WEAPONS', font('anton', 40), WHITE)
    text(img, (630, 136), 'round 1 offer . 5 cards . buy, then drop on an operative', font('plex', 20), DIM)
    cw, ch, gap = 196, 400, 18
    for i, (n, fam, cost, st, dm, sh, rc, kw, tx, part) in enumerate(SHOPW):
        x = 440 + i * (cw + gap)
        weapon_card(img, x, 186, cw, ch, n, fam, cost, st, dm, sh, rc, kw, tx, rot=(-1.2, .8, -.4, 1.1, -.8)[i],
                    partner=part, sel=(i == 0), sold=(i == 3))
    text(img, (1000, 650), 'RARE', font('anton', 26), (190, 190, 210, 255))
    text(img, (1080, 654), 'none this round (auction on round 3)', font('plex', 20), DIM)
    hand(img, (470, 680), 'merges with URSA\'s shotgun -> **', 28, LIME, rot=-2)
    arrow_hand(img, [(540, 720), (550, 830), (556, 930)], LIME, 5)
    # right: bank, reroll, lock, sell
    glass(img, [1520, 112, 1896, 842], title='BANK', tsize=22)
    text(img, (1545, 170), 'CREDITS', font('mono', 18), DIM)
    text(img, (1545, 190), '12', font('anton', 110), LIME)
    text(img, (1700, 250), 'cr', font('anton', 40), LIME)
    text(img, (1545, 330), 'interest at round end', font('plex', 20), DIM)
    for k in range(5):
        on = k < 2
        rrect(img, [1545 + k * 64, 362, 1545 + k * 64 + 54, 396], 6, fill=LIME if on else (40, 44, 60, 255), outline=INK, width=2)
        text(img, (1572 + k * 64, 380), '+1', font('anton', 20), INK if on else (100, 100, 130, 255), 'mm')
    text(img, (1545, 410), 'every 5 cr banked pays 1 (cap 3, BANKER +2)', font('plex', 16), DIM)
    die_sticker(img, 'REROLL 2', 1640, 492, 200, 56, CYAN, rot=-2, size=34)
    put_glyph(img, 'picto_again', 1800, 492, 44, CYAN)
    die_sticker(img, 'LOCK', 1640, 584, 130, 50, WHITE, rot=1.5, size=30)
    put_glyph(img, 'state_locked', 1760, 584, 38, WHITE)
    # sell zone
    d = draw(img)
    for k in range(0, 340, 22):
        line(img, [(1545 + k, 650), (1545 + k + 12, 650)], PINK, 3); line(img, [(1545 + k, 820), (1545 + k + 12, 820)], PINK, 3)
    for k in range(0, 170, 22):
        line(img, [(1545, 650 + k), (1545, 650 + k + 12)], PINK, 3); line(img, [(1880, 650 + k), (1880, 650 + k + 12)], PINK, 3)
    text(img, (1712, 712), 'SELL', font('anton', 44), PINK, 'mm')
    text(img, (1712, 762), 'drop a weapon here: half back', font('plex', 18), PINK, 'mm')
    # bottom: the crew roster tray
    rect(img, [0, 860, 1920, 1080], fill=(8, 6, 16, 235))
    line(img, [(0, 860), (1920, 860)], CYAN, 2)
    text(img, (24, 880), 'CREW  .  drag a bought weapon onto a slot  .  2 alike merge to the next star', font('mono', 18), CYAN)
    ops = [('MAKO', 'GUNNER', 2, 5, [('Rail Rifle', 2), None], None),
           ('URSA', 'SAPPER', 1, 1, [('Breach Shotgun', 1), ('Shaped Charge', 1)], None),
           ('OZZY', 'HACKER', 1, 9, [('Jammer Rig', 1), ('SMG', 1)], None),
           ('NYX', 'FIXER', 1, 6, [('Barrier Kit', 1), None], None)]
    for i, (n, c, lv, ix, ws, mg) in enumerate(ops):
        tray_op(img, 24 + i * 348, 880, n, c, lv, ix, ws, w=336)
    pencil_circle(img, 572, 1010, 52, 52, LIME, 5, seed=3)
    die_sticker(img, 'TO PLACEMENT', 1740, 980, 270, 64, LIME, rot=-2, size=38)
    hand(img, (1440, 1020), 'enter', 22, DIM)
    frame_caption(img, 'B-107 raid screen 2/5  SHOP  (concept plate)')
    return finish_save(img, 'raid_2_shop.png')


# ================================================================ (c) PLACE
def crew_strip(img, y, sel=None, states=None, show_weapons=True, title='CREW'):
    rect(img, [0, y, 1920, 1080], fill=(8, 6, 16, 238))
    line(img, [(0, y), (1920, y)], CYAN, 2)
    ops = [('MAKO', 'GUNNER', 2, 5, [('Rail Rifle', 2), None]), ('URSA', 'SAPPER', 1, 1, [('Breach Shotgun', 2), ('Shaped Charge', 1)]),
           ('OZZY', 'HACKER', 1, 9, [('Jammer Rig', 1), ('SMG', 1)]), ('NYX', 'FIXER', 1, 6, [('Barrier Kit', 1), None])]
    for i, (n, c, lv, ix, ws) in enumerate(ops):
        x = 24 + i * 300
        tray_op(img, x, y + 18, n, c, lv, ix, ws, w=288, h=170)
        if sel == i:
            rrect(img, [x - 6, y + 12, x + 294, y + 194], 16, outline=LIME, width=4)
        if states and states.get(i):
            s_, col = states[i]
            chip(img, x + 144, y + 2, s_, font('anton', 18), INK, bg=col, pad=8)


def place():
    img = load_bg('raid_v3/set8/r8_place.png')
    img = ImageEnhance.Brightness(img).enhance(.95)
    # cover set 8's own HUD (left column, work order, bottom strip, SEND IT) with the new chrome
    shade_rect(img, [0, 0, 430, 860], (8, 6, 16), 225)
    shade_rect(img, [1500, 0, 1920, 860], (8, 6, 16), 246)
    hud_strip(img, credits=4); raid_steps(img, 2); round_tab(img, '1', '4')
    # left: what is left to place
    glass(img, [24, 112, 410, 842], title='TO PLACE', tsize=22)
    items = [('MAKO', 'post', 'GUNNER', 'on b2 (HQ door)', True), ('URSA', 'post', 'SAPPER', 'on b4', True),
             ('OZZY', 'post', 'HACKER', 'on a7', True), ('NYX', 'post', 'FIXER', 'not placed', False)]
    yy = 170
    for n, _, c, where, ok in items:
        class_badge(img, c, 62, yy + 22, 22, rot=-6)
        text(img, (96, yy + 10), n, font('anton', 28), WHITE)
        text(img, (200, yy + 22), where, font('plex', 19), LIME if ok else PINK, 'lm')
        if ok:
            tick(img, 360, yy + 22, 22, LIME, 4)
        yy += 62
    line(img, [(44, yy + 6), (390, yy + 6)], (92, 225, 255, 90), 1)
    yy += 22
    text(img, (44, yy), 'DOCK ON STREET SLOTS', font('mono', 17), CYAN); yy += 34
    for n, g, where, ok in (('Breach Shotgun **', 'raid_shotgun', 'held: drop on a lit slot', None), ('Rail Rifle **', 'raid_rail', 'd6', True),
                            ('SMG *', 'raid_smg', 'd7', True), ('Barrier Kit *', 'picto_block', 'b4 road', True), ('BEACON', 'picto_target', 'not placed', False)):
        rrect(img, [44, yy, 92, yy + 44], 6, fill=WHITE, outline=INK, width=2)
        put_glyph(img, g, 68, yy + 22, 34, INK)
        text(img, (104, yy + 11), n, font('anton', 21), WHITE, 'lm')
        text(img, (104, yy + 35), where, font('plex', 16), LIME if ok else (PINK if ok is False else YEL), 'lm')
        yy += 56
    chip(img, 44, 790, 'UNDO  Z', font('anton', 22), CYAN, bg=NAVY, edge=CYAN, pad=12)
    chip(img, 190, 790, 'EVACUATE', font('anton', 22), RED, bg=NAVY, edge=RED, pad=12)
    # right: the hovered slot forecast
    glass(img, [1512, 112, 1896, 842], title='SLOT d5  .  hover', tsize=22)
    text(img, (1534, 168), 'Breach Shotgun ** on d5', font('anton', 30), WHITE)
    text(img, (1534, 212), 'reach 1 . covers 3 road cells of route A', font('plex', 19), DIM)
    rows = [('kills (round 1)', '6 -> 8', LIME), ('leaks at A', '2 -> 0', LIME), ('HQ hits', '2 -> 0', LIME), ('merge', 'URSA ** (Breacher)', YEL)]
    yy = 262
    for k, v, c in rows:
        text(img, (1534, yy), k, font('plex', 21), (210, 212, 225, 255))
        text(img, (1878, yy), v, font('anton', 26), c, 'ra')
        yy += 44
    line(img, [(1534, yy + 4), (1876, yy + 4)], (92, 225, 255, 90), 1)
    text(img, (1534, yy + 18), 'FORECAST, ROUND 1', font('mono', 17), CYAN)
    for i, (u, ic, n, k) in enumerate((('TROOPER', 'heavy', 5, 5), ('BIKE', 'fast', 3, 3))):
        y2 = yy + 54 + i * 70
        img.alpha_composite(unit_icon(ic, 52), (S(1534), S(y2)))
        text(img, (1600, y2 + 26), u, font('anton', 24), WHITE, 'lm')
        bar(img, 1720, y2 + 16, 120, 20, k / n, LIME, seg=n)
        text(img, (1878, y2 + 26), '%d/%d' % (k, n), font('anton', 22), LIME, 'rm')
    hand(img, (1540, yy + 210), 'all 8 stop before b4', 28, YEL, rot=-3)
    die_sticker(img, 'SEND IT', 1726, 752, 230, 74, PINK, rot=-3, size=50)
    crew_strip(img, 862, sel=1, states={0: ('PLACED', LIME), 1: ('PLACED', LIME), 2: ('PLACED', LIME), 3: ('TO PLACE', PINK)})
    # devices still in hand (right of the crew)
    text(img, (1236, 880), 'DEVICES IN HAND', font('mono', 18), CYAN)
    for i, (n, g, st) in enumerate((('BARRICADE', 'picto_block', 'placed b4'), ('BEACON', 'picto_target', 'drag to a lit side cell'))):
        x = 1236 + i * 170
        rrect(img, [x, 912, x + 150, 1048], 12, fill=WHITE)
        rrect(img, [x + 4, 916, x + 146, 1044], 9, fill=(255, 214, 40, 255) if i == 0 else (36, 32, 54, 255))
        put_glyph(img, g, x + 75, 962, 62, INK if i == 0 else WHITE)
        text(img, (x + 75, 1018), n, font('anton', 22), INK if i == 0 else WHITE, 'mm')
        if i == 0:
            tick(img, x + 118, 932, 22, INK, 5)
    hand(img, (1586, 935), 'BEACON: +1 dmg,', 24, YEL, rot=-3)
    hand(img, (1586, 968), '+1 reach within 2', 24, YEL, rot=-3)
    frame_caption(img, 'B-107 raid screen 3/5  PLACE operatives (board = set 8 r8_place DRAFT; chrome new)')
    return finish_save(img, 'raid_3_place.png')


# ================================================================ (d) EXECUTE
def execute():
    img = load_bg('raid_v3/set8/r8_playback.png')
    shade_rect(img, [0, 0, 430, 860], (8, 6, 16), 225)
    shade_rect(img, [1500, 0, 1920, 860], (8, 6, 16), 246)
    shade_rect(img, [690, 940, 1230, 1020], (8, 6, 16), 255)
    hud_strip(img, credits=4); raid_steps(img, 3); round_tab(img, '1', '4')
    # tick bar, big, top centre of the board
    glass(img, [560, 110, 1360, 190], edge=CYAN)
    text(img, (584, 150), 'TICK', font('mono', 20), DIM, 'lm')
    for k in range(8):
        on = k < 3
        rrect(img, [650 + k * 62, 130, 650 + k * 62 + 52, 170], 6, fill=CYAN if on else (30, 40, 60, 255), outline=INK, width=2)
        text(img, (676 + k * 62, 150), str(k + 1), font('anton', 22), INK if on else (90, 100, 130, 255), 'mm')
    text(img, (1170, 150), 'ROUND 1/4', font('anton', 30), WHITE, 'lm')
    # left: the wave as it stands
    glass(img, [24, 112, 410, 842], title='THE WAVE', tsize=22, rule=RED)
    rows = [('TROOPER', 'heavy', 5, 3, 0), ('BIKE', 'fast', 3, 1, 0)]
    yy = 172
    for u, ic, n, dead, leak in rows:
        img.alpha_composite(unit_icon(ic, 60), (S(44), S(yy)))
        text(img, (116, yy + 18), u, font('anton', 28), WHITE, 'lm')
        for k in range(n):
            px = 116 + k * 44
            rrect(img, [px, yy + 40, px + 36, yy + 66], 5, fill=(70, 74, 92, 255) if k < dead else (61, 255, 139, 255), outline=INK, width=2)
            if k < dead:
                cross(img, px + 18, yy + 53, 18, RED, 4)
        yy += 104
    text(img, (44, yy + 4), 'LEAKS', font('mono', 18), DIM)
    put_glyph(img, 'raid_leak', 60, yy + 56, 40, (120, 200, 255, 255))
    text(img, (96, yy + 56), '0', font('anton', 54), WHITE, 'lm')
    text(img, (200, yy + 4), 'KILLS', font('mono', 18), DIM)
    put_glyph(img, 'raid_kills', 214, yy + 56, 40, WHITE)
    text(img, (250, yy + 56), '4/8', font('anton', 54), LIME, 'lm')
    hand(img, (44, yy + 120), 'B road is quiet', 28, YEL, rot=-3)
    line(img, [(44, yy + 170), (390, yy + 170)], (92, 225, 255, 90), 1)
    text(img, (44, yy + 186), 'NEXT  .  ROUND 2  .  9 units', font('mono', 17), CYAN)
    ux = 44
    for ic, c in (('heavy', 4), ('heavy', 2), ('flying', 3)):
        img.alpha_composite(unit_icon(ic, 46), (S(ux), S(yy + 216)))
        text(img, (ux + 50, yy + 240), 'x%d' % c, font('anton', 24), WHITE, 'lm')
        ux += 112
    # speed controls
    yb = 770
    for i, (s_, on) in enumerate((('II', False), ('1x', False), ('2x', True), ('4x', False))):
        x = 44 + i * 88
        rrect(img, [x, yb, x + 78, yb + 50], 8, fill=CYAN if on else NAVY, outline=CYAN, width=2)
        text(img, (x + 39, yb + 26), s_, font('anton', 26), INK if on else CYAN, 'mm')
    # right: the damage tally per operative (pencil tallies)
    glass(img, [1512, 112, 1896, 842], title='TALLY', tsize=22)
    tal = [('MAKO', 'GUNNER', 5, 9, 2), ('URSA', 'SAPPER', 1, 7, 2), ('OZZY', 'HACKER', 9, 3, 0), ('NYX', 'FIXER', 6, 1, 0)]
    yy = 170
    for n, c, ix, dmg, k in tal:
        art = portrait_art(c, 84, 84, ix)
        mk = Image.new('L', art.size, 0); ImageDraw.Draw(mk).ellipse((0, 0, art.width, art.height), fill=255)
        img.paste(art, (S(1532), S(yy)), mk)
        ellipse(img, [1532, yy, 1616, yy + 84], outline=CLASS[c]['col'], width=4)
        text(img, (1630, yy + 4), n, font('anton', 28), WHITE)
        bar(img, 1630, yy + 44, 200, 18, dmg / 10, CLASS[c]['col'])
        text(img, (1842, yy + 53), str(dmg), font('anton', 24), WHITE, 'lm')
        for t in range(k):                       # kill tallies in pencil
            pencil_line(img, [(1720 + t * 14, yy + 4), (1716 + t * 14, yy + 34)], YEL, 4, seed=t + ix)
        yy += 118
    text(img, (1532, yy + 6), 'firing now: MAKO rail on d6, URSA shotgun on d5', font('plex', 16), DIM)
    die_sticker(img, 'SKIP TO END', 1704, 790, 250, 52, WHITE, rot=1.5, size=30)
    crew_strip(img, 862, states={0: ('FIRING', LIME), 1: ('FIRING', LIME), 2: ('JAM 2', CYAN), 3: ('RELOAD', YEL)})
    # the tick log (mono, newest on top)
    glass(img, [1236, 878, 1896, 1050], title='LOG  .  tick 3', tsize=17)
    logs = [('MAKO rail d6 -> TROOPER 4  KILL', LIME), ('URSA shotgun d5 -> TROOPER x2  2, 2', WHITE),
            ('OZZY jammer a7 -> BIKE jammed', CYAN), ('BARRICADE b4 held: 6 -> 4', YEL)]
    for i, (s_, c) in enumerate(logs):
        text(img, (1258, 922 + i * 30), s_, font('mono', 18), c[:3] + (255 - i * 40,))
    frame_caption(img, 'B-107 raid screen 4/5  EXECUTE (board = set 8 r8_playback DRAFT; chrome new)')
    return finish_save(img, 'raid_4_execute.png')


# ================================================================ (e) RESULT + lost
def receipt(img, x, y, w, rows, total, rot=1.5, title='PAYOUT'):
    h = 120 + len(rows) * 40 + 90
    L = layer(w + 40, h + 40); o = 20
    paper(L, [o, o, o + w, o + h], rot=0, col=(246, 244, 238, 255), seed=4, tear=True)
    text(L, (o + w / 2, o + 40), title, font('anton', 40), INK, 'mm')
    text(L, (o + w / 2, o + 78), 'cell ledger . raid 3', font('courier', 18), (90, 90, 90, 255), 'mm')
    yy = o + 112
    for k, v in rows:
        text(L, (o + 24, yy), k, font('courier', 22), INK)
        text(L, (o + w - 24, yy), v, font('courierb', 24), INK, 'ra')
        yy += 40
    line(L, [(o + 20, yy + 4), (o + w - 20, yy + 4)], INK, 2)
    text(L, (o + 24, yy + 18), 'TOTAL', font('anton', 34), INK)
    text(L, (o + w - 24, yy + 16), total, font('anton', 38), INK, 'ra')
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(6, 10, 14, 140))


def xp_card(img, x, y, name, cls, idx, lvl, xp0, xp1, of, up=False, state=None, w=250, h=130):
    c = CLASS[cls]['col']
    rrect(img, [x, y, x + w, y + h], 12, fill=WHITE)
    rrect(img, [x + 4, y + 4, x + w - 4, y + h - 4], 9, fill=INK)
    art = portrait_art(cls, 96, h - 14, idx, dim=state == 'down')
    m = Image.new('L', art.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, art.width, art.height), radius=S(7), fill=255)
    img.paste(art, (S(x + 7), S(y + 7)), m)
    text(img, (x + 114, y + 30), name, font('anton', 30), WHITE, 'lm')
    text(img, (x + w - 14, y + 30), 'LV%d' % lvl, font('anton', 22), c, 'rm')
    bar(img, x + 114, y + 58, w - 130, 16, xp1 / of, c, seg=of)
    rect(img, [x + 114 + (w - 130) * xp0 / of, y + 60, x + 114 + (w - 130) * xp1 / of, y + 72], fill=(255, 255, 255, 150))
    text(img, (x + 114, y + 96), '+%d XP' % (xp1 - xp0), font('anton', 24), LIME if not state else DIM, 'lm')
    if up:
        sticker(img, 'LEVEL UP', x + w - 58, y + h - 18, 120, 34, YEL, None, rot=-6, size=22)
    if state == 'down':
        stamp(img, 'DOWN 1 RAID', x + w / 2 + 40, y + 96, RED, rot=-6, size=24)


def report(img, lost=False):
    X0, Y0, X1, Y1 = 90, 112, 900, 1040
    paper(img, [X0, Y0, X1, Y1], rot=-1.0, clip=True, seed=21)
    L = layer(X1 - X0, Y1 - Y0)
    text(L, (50, 44), 'SOLACE', font('anton', 58), CORP_INK)
    text(L, (290, 82), 'Field Operations', font('mono', 22), CORP_INK, 'ls')
    line(L, [(50, 116), (760, 116)], CORP_INK, 3)
    text(L, (50, 140), 'AFTER-ACTION REPORT', font('anton', 50), INK)
    text(L, (50, 206), 'REF SOL-AAR-2611-07 . STATIC ALLEY', font('mono', 20), (90, 90, 90, 255))
    rows = [('OPERATION', 'CLEAN SWEEP'), ('TARGET', 'Cell safehouse, grid c7'), ('DURATION', '4 rounds'),
            ('UNITS COMMITTED', '33'), ('UNITS LOST', '31' if not lost else '19'), ('UNITS THROUGH', '0' if not lost else '14'),
            ('TARGET DAMAGE', 'none' if not lost else 'HQ -4, site taken'), ('OUTCOME', ''), ('NEXT ACTION', 'review Heat, resubmit' if not lost else 'garrison CULTURE INTAKE')]
    yy = 262
    for k, v in rows:
        line(L, [(50, yy - 10), (760, yy - 10)], (196, 190, 176, 255), 1)
        text(L, (50, yy), k, font('mono', 22), (70, 70, 70, 255))
        if k == 'OUTCOME' and not lost:
            rect(L, [330, yy - 2, 640, yy + 28], fill=INK)
        else:
            text(L, (330, yy - 4), v, font('courier', 26), INK)
        yy += 56
    text(L, (50, Y1 - Y0 - 120), 'FIELD SUPERVISOR', font('mono', 20), (90, 90, 90, 255))
    pencil_line(L, [(330, Y1 - Y0 - 108), (360, Y1 - Y0 - 126), (380, Y1 - Y0 - 104), (420, Y1 - Y0 - 130), (470, Y1 - Y0 - 110), (520, Y1 - Y0 - 118)], (30, 40, 110, 255), 3)
    text(L, (50, Y1 - Y0 - 60), 'INTERNAL . PAGE 1 OF 1', font('mono', 18), (120, 120, 120, 255))
    rotate_paste(img, L, (X0 + X1) / 2, (Y0 + Y1) / 2, -1.0, shadow=False)
    if not lost:
        pencil_circle(img, 440, 604, 52, 28, YEL, 5)
        hand(img, (540, 590), '31/33', 56, YEL, rot=-6)
        tick(img, 470, 662, 26, YEL); tick(img, 520, 718, 26, YEL)
        sticker(img, 'HELD', 700, 850, 260, 110, YEL, None, rot=-6, size=92)
        stamp(img, 'CLASSIFIED', 640, 300, TEAL, rot=-8, size=50)


def corp_ink_stamp(img, s, cx, cy, rot=-12, size=150, col=(18, 116, 88, 255)):
    """A big rubber stamp in Solace's corporate ink: double frame, uneven ink, speckled dropouts, a second faint strike."""
    f = font('anton', size)
    wd = tw(s, f) + 90; hd = size * 1.45 + 60
    Lc = layer(wd + 40, hd + 40)
    d = draw(Lc)
    rrect(Lc, [20, 20, 20 + wd, 20 + hd], 18, outline=col, width=14)
    rrect(Lc, [38, 38, 2 + wd, 2 + hd], 12, outline=col, width=5)
    text(Lc, ((wd + 40) / 2, 20 + hd * .44), s, f, col, 'mm')
    line(Lc, [(70, 20 + hd - 52), (wd - 30, 20 + hd - 52)], col, 3)
    text(Lc, ((wd + 40) / 2, 20 + hd - 30), 'SOLACE BIOSYSTEMS . FIELD OPERATIONS . VERIFIED', font('mono', 22), col, 'mm')
    arr = np.asarray(Lc).copy()
    rng = np.random.default_rng(7)
    n = rng.random(arr.shape[:2])
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255
    big = np.asarray(Image.fromarray((rng.random(arr.shape[:2]) * 255).astype(np.uint8)).resize((arr.shape[1] // 40, arr.shape[0] // 40)).resize((arr.shape[1], arr.shape[0]), Image.BICUBIC)).astype(np.float32) / 255
    ink = np.clip(.55 + .6 * big - .45 * (n > .6), 0, 1)
    arr[..., 3] = (arr[..., 3] * ink * .92).astype(np.uint8)
    Lc = Image.fromarray(arr, 'RGBA')
    ghost = Lc.copy(); ga = np.asarray(ghost).copy(); ga[..., 3] = (ga[..., 3] * .22).astype(np.uint8); ghost = Image.fromarray(ga, 'RGBA')
    rotate_paste(img, ghost, cx + 14, cy + 10, rot + 2.5, shadow=False)
    rotate_paste(img, Lc, cx, cy, rot, shadow=False)


def result(lost=False):
    img = bg_raid(.26, blur=6)
    if lost:
        img.alpha_composite(Image.new('RGBA', img.size, (20, 60, 46, 60)))
    hud_strip(img, credits=7 if lost else 19, heat=36 if lost else 31, hq=(16, 20) if lost else (20, 20))
    raid_steps(img, 4, lost=lost); round_tab(img, '4', '4')
    report(img, lost)
    if lost:
        corp_ink_stamp(img, 'TARGET ACQUIRED', 520, 640, rot=-14, size=118)
    # our side: payout, crew XP, consequences
    if not lost:
        receipt(img, 960, 120, 380, [('kills  31 x 0.5', '+15'), ('interest  (bank 12)', '+2'), ('HEADHUNTER  (MAKO)', '+2'),
                                     ('rerolls, buys', '-10')], '+9 cr', rot=1.8)
        glass(img, [1390, 112, 1896, 560], title='SALVAGE', tsize=22)
        weapon_card(img, 1420, 170, 190, 330, 'Breach Shotgun', 'BLAST', None, 2, 2, 2, 1, ('SHORT',), None, rot=-2)
        text(img, (1636, 196), 'kept: URSA', font('anton', 30), WHITE)
        text(img, (1636, 236), 'merged ** stays', font('plex', 20), DIM)
        text(img, (1636, 266), 'on its operator', font('plex', 20), DIM)
        text(img, (1636, 330), 'Heat', font('mono', 20), DIM)
        text(img, (1636, 352), '36 -> 31', font('anton', 44), (255, 150, 90, 255))
        text(img, (1636, 420), 'site', font('mono', 20), DIM)
        text(img, (1636, 442), 'HELD', font('anton', 44), LIME)
        glass(img, [960, 600, 1896, 930], title='CREW  .  XP', tsize=22)
        xs = [('MAKO', 'GUNNER', 5, 2, 6, 10, 10, True), ('URSA', 'SAPPER', 1, 1, 3, 6, 6, True), ('OZZY', 'HACKER', 9, 1, 0, 4, 6, False), ('NYX', 'FIXER', 6, 1, 2, 5, 6, False)]
        for i, (n, c, ix, lv, a, b, of, up) in enumerate(xs):
            xp_card(img, 984 + (i % 2) * 456, 656 + (i // 2) * 136, n, c, ix, lv + (1 if up else 0), a, b, of, up, w=430, h=124)
        hand(img, (980, 950), '2 level ups: pick a talent at the HQ', 30, YEL, rot=-2)
        die_sticker(img, 'CONTINUE', 1750, 1010, 240, 64, PINK, rot=-3, size=42)
    else:
        glass(img, [960, 112, 1896, 520], title='WHAT THE CORP TOOK', tsize=22, edge=RED, rule=RED)
        rows = [('site', 'CULTURE INTAKE', 'lost to Solace', RED), ('HQ integrity', '20 -> 16', '14 units got through', RED),
                ('credits', '+7 cr', 'kills only, no interest', DIM), ('Heat', '36 (no change)', 'the corp is satisfied', DIM)]
        yy = 172
        for k, v, s_, c in rows:
            text(img, (990, yy), k, font('mono', 20), DIM)
            text(img, (1190, yy - 6), v, font('anton', 36), WHITE if c is DIM else c)
            text(img, (1190, yy + 38), s_, font('plex', 19), DIM)
            yy += 84
        # the lost site as a polaroid off the city map, crossed in red pencil, the corp's sticker on it
        pol = load_bg('cohesion/map_pages_r42/hq_idle.png').crop((S(810), S(440), S(1050), S(650))).resize((S(250), S(220)), Image.LANCZOS)
        L = layer(290, 300)
        rect(L, [10, 10, 280, 290], fill=(244, 242, 236, 255))
        L.paste(pol, (S(20), S(20)))
        text(L, (145, 266), 'CULTURE INTAKE', font('hand', 24), (40, 40, 120, 255), 'mm')
        rotate_paste(img, L, 1730, 330, 5)
        cross(img, 1730, 300, 150, RED, 9)
        sticker(img, 'SOLACE', 1790, 420, 120, 40, SOL, None, rot=-8, size=26)
        glass(img, [960, 560, 1896, 930], title='CREW', tsize=22, edge=RED, rule=RED)
        xs = [('MAKO', 'GUNNER', 5, 2, 6, 8, 10, None), ('URSA', 'SAPPER', 1, 1, 3, 4, 6, 'down'), ('OZZY', 'HACKER', 9, 1, 0, 2, 6, None), ('NYX', 'FIXER', 6, 1, 2, 3, 6, None)]
        for i, (n, c, ix, lv, a, b, of, st) in enumerate(xs):
            xp_card(img, 984 + (i % 2) * 456, 616 + (i // 2) * 146, n, c, ix, lv, a, b, of, False, st, w=430, h=130)
        hand(img, (980, 950), 'we hold the HQ. take the intake back.', 30, YEL, rot=-2)
        die_sticker(img, 'CONTINUE', 1750, 1010, 240, 64, PINK, rot=-3, size=42)
    frame_caption(img, 'B-107 raid screen 5/5  RESULT %s' % ('LOST: TARGET ACQUIRED in corporate ink' if lost else 'HELD (reward)'))
    return finish_save(img, 'raid_5_result_lost.png' if lost else 'raid_5_result.png')


if __name__ == '__main__':
    which = sys.argv[1:] or ['review', 'shop', 'place', 'execute', 'result', 'lost']
    for w_ in which:
        {'review': review, 'shop': shop, 'place': place, 'execute': execute, 'result': result, 'lost': lambda: result(True)}[w_]()
