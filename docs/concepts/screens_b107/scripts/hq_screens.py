"""B-107 item 3: HQ workshop as separate screens over the city map page (hq_idle, r42, Solace):
RECRUIT (portrait card, details, cost), WEAPONS (a shop + the roster), TALENTS (what the operative has + the dossier of
everything each operative could get). PIL only. Run: python hq_screens.py [recruit|weapons|talents]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

TAL = {  # id: (name, class or '', text)
    'ap': ('AP ROUNDS', '', 'Its hits ignore [armor].'), 'bank': ('BANKER', '', 'Raid interest cap [+2].'),
    'combo': ('CHAIN RUNNER', '', '[+1 energy] a netrun segment; raid [+1] on a hit unit.'),
    'cross': ('CROSS-TRAINED', '', 'Learns one more [trait].'), 'dmg': ('HOLLOW POINTS', '', '[+1] damage per hit.'),
    'exec': ('EXECUTIONER', '', 'Leaves a unit at [2 hp] or less: dead.'),
    'fort': ('FORTIFIER', '', 'Barricades within 1: [+3 hp].'), 'head': ('HEADHUNTER', '', 'First kill each round pays [2 credits].'),
    'holster': ('SECOND HOLSTER', '', 'Holds [one more weapon].'), 'learn': ('FAST LEARNER', '', 'Earns [double XP].'),
    'override': ('OVERRIDE', '', '[+1] damage to a JAMMED unit.'), 'pack': ('PACK RAT', '', 'Keeps [one more] weapon after a raid.'),
    'pierce': ('OVERPENETRATION', '', 'Each hit: [1] to the node behind.'), 'quick': ('QUICK DRAW', '', '[One more action] on tick 1.'),
    'reach': ('LONG ARM', '', '[+1 reach].'), 'reson': ('RESONANCE', '', 'Splash [+1] per unit on the node.'),
    'scope': ('LONG SHOT', '', '[+2] damage at 4+ nodes.'), 'shot': ('EXTRA MAG', '', '[+1 shot] per shooting weapon.'),
    'signal': ('SIGNAL BOOST', '', 'Jams [+1], jam reach [+1].'), 'skeet': ('SKEET', '', '[+2] on Bikes and Drones.'),
    'star': ('STAR POWER', '', 'Weapons count [one star higher].'), 'tank': ('TANK BUSTER', '', '[+2] on Heavies and Riots.'),
    'trainer': ('TRAINER', '', 'Fielded operators [+1 XP] a round.'),
    'rangefinder': ('RANGE FINDER', 'GUNNER', 'No [LONG-band] damage penalty at any reach.'),
    'vethands': ('VETERAN HANDS', 'GUNNER', '[+1] damage a hit per star above 1 of the weapon.'),
    'cqb': ('CLOSE QUARTERS', 'SAPPER', '[+2] damage within 1 cell of its cell.'), 'shrapnel': ('SHRAPNEL', 'SAPPER', 'Splash and blast damage [+2].'),
    'haggle': ('HAGGLER', 'FIXER', 'Raid shop buys cost [1 less] (min 1).'), 'mender': ('MENDER', 'FIXER', 'Barricades within 2 mend [1 hp] a tick.'),
    'overseer': ('OVERSEER', 'FIXER', 'Devices next to it work as if a [TINKER] stood by.'),
    'static': ('STATIC BURST', 'HACKER', 'Units its jam hits take [2] (ignores armor).'),
    'swarmtac': ('SWARM TACTICS', 'HACKER', 'AUTO weapons [+1 shot] per AUTO ally within 2.'),
}
TRAIT = {'COOL HAND': 'First shot each round: the toughest unit in reach, x2.', 'STEADY': '+1 reach.', 'DEMO': 'Barricades from its weapons +3 hp; blasts +1.',
         'BRAWLER': '+1 damage within 1 cell.', 'WIRED': 'Jams +1; units it hits are jammed too.', 'SPOTTER': 'Operators next to it +1 reach.',
         'MASTER': 'A weapon held alone counts one star higher.', 'OPPORTUNIST': '+1 to jammed, slowed or held units.'}


def hq_base(active='CREW', title='RECRUIT', sub=''):
    img = bg_map(.34, 5, keep_hud=False)
    hud_strip(img, credits=31, heat=31)
    # the map's own left column stays (CREW / MARKET / DEFENCE), the door we came through lit
    src = load_bg('cohesion/map_pages_r42/hq_idle.png')
    col = src.crop((0, S(846), S(222), S(1060)))
    img.paste(col, (0, S(846)))
    btn = {'CREW': (18, 846, 218, 914), 'MARKET': (18, 918, 218, 984), 'DEFENCE': (18, 988, 218, 1054)}[active]
    rrect(img, [btn[0] - 4, btn[1] - 4, btn[2] + 4, btn[3] + 4], 6, outline=LIME, width=4)
    # title + where we are + sibling doors (separate screens, not tabs)
    text(img, (640, 26), 'HQ  /  WORKSHOP', font('mono', 18), LIME)
    text(img, (638, 44), title, font('anton', 56), WHITE)
    if sub:
        text(img, (640 + tw(title, font('anton', 56)) + 24, 72), sub, font('plex', 21), DIM, 'lm')
    x = 1460
    for s_ in ('RECRUIT', 'WEAPONS', 'TALENTS'):
        on = s_ == title
        f = font('anton', 22)
        w = tw(s_, f) + 28
        rrect(img, [x, 30, x + w, 72], 8, fill=LIME if on else (18, 20, 30, 220), outline=None if on else (110, 120, 140, 200), width=2)
        text(img, (x + w / 2, 52), s_, f, INK if on else (190, 196, 212, 255), 'mm')
        x += w + 10
    chip(img, 1842 - 4, 30, 'ESC', font('anton', 22), CYAN, bg=NAVY, edge=CYAN, pad=10, h=42)
    return img


# ================================================================ RECRUIT
RECRUITS = [('KESTREL', 'GUNNER', 'overclocker', 2, ['COOL HAND', 'STEADY'], ('Marksman Rifle', 1), 12),
            ('VOSS', 'SAPPER', 'phantom', 9, ['DEMO', 'BRAWLER'], ('Grenade Launcher', 1), 12),
            ('LUMEN', 'HACKER', 'botnet', 4, ['WIRED', 'SPOTTER'], ('Lane Gun', 1), 15)]


def recruit_card(img, x, y, w, h, r, sel=False, rot=0):
    name, cls, bset, idx, traits, wpn, cost = r
    op_card(img, x, y, w, h, name, cls, 1, (0, 6), idx, bset, traits=traits, weapons=[wpn], rot=rot, sel=sel, trait_desc=TRAIT)


def recruit():
    img = hq_base('CREW', 'RECRUIT', 'offer after RAID 3 (held): someone on the block saw you hold it')
    for i, r in enumerate(RECRUITS):
        x = 268 + i * 372
        recruit_card(img, x, 150, 340, 620, r, sel=(i == 1), rot=(-1.5, 0, 1.5)[i])
    for i, r in enumerate(RECRUITS):     # tags last, over the neighbours' badges
        x = 268 + i * 372
        price_tag(img, x + 340 - 50, 186, r[6], rot=9, w=104, h=50)
    hand(img, (300, 800), 'VOSS + URSA = two Sappers on the B road', 30, YEL, rot=-2)
    # the dossier of the selected recruit (our planning file, manila)
    X0, Y0, X1, Y1 = 1388, 112, 1898, 1050
    paper(img, [X0, Y0, X1, Y1], rot=.8, col=(232, 210, 160, 255), seed=31)
    L = layer(X1 - X0, Y1 - Y0)
    text(L, (30, 26), 'CELL FILE . RECRUIT', font('mono', 18), (90, 70, 40, 255))
    text(L, (30, 50), 'VOSS', font('anton', 64), INK)
    text(L, (190, 84), 'SAPPER . R0 . LV1', font('courierb', 22), INK, 'lm')
    text(L, (30, 134), 'blasts, splash, barricades that bite', font('courier', 21), (60, 50, 40, 255))
    yy = 178
    line(L, [(30, yy), (480, yy)], (120, 100, 70, 255), 2)
    text(L, (30, yy + 12), 'TRAITS (rolled)', font('mono', 18), (90, 70, 40, 255))
    yy += 44
    for t in ('DEMO', 'BRAWLER'):
        text(L, (30, yy), t, font('anton', 30), INK)
        yy = rich(L, 30, yy + 38, TRAIT[t], font('courier', 19), 450, (50, 44, 36, 255), (150, 40, 120, 255)) + 8
    line(L, [(30, yy), (480, yy)], (120, 100, 70, 255), 2)
    text(L, (30, yy + 12), 'STARTER WEAPON', font('mono', 18), (90, 70, 40, 255))
    yy += 46
    rrect(L, [30, yy, 100, yy + 70], 8, fill=WHITE, outline=INK, width=2)
    L.alpha_composite(glyph('placeholder_bomb', 54, INK), (S(38), S(yy + 8)))
    text(L, (116, yy + 4), 'GRENADE LAUNCHER', font('anton', 28), INK)
    text(L, (116, yy + 42), 'DMG 2 . 1 shot . reach 1, whole cell', font('courier', 17), (60, 50, 40, 255))
    yy += 92
    line(L, [(30, yy), (480, yy)], (120, 100, 70, 255), 2)
    text(L, (30, yy + 12), 'CAN LEARN (see TALENTS)', font('mono', 18), (90, 70, 40, 255))
    yy += 44
    text(L, (30, yy), 'CLOSE QUARTERS . SHRAPNEL', font('anton', 26), (120, 60, 200, 255))
    text(L, (30, yy + 36), '+ 23 talents any class can learn', font('courier', 19), (60, 50, 40, 255))
    yy += 80
    line(L, [(30, yy), (480, yy)], (120, 100, 70, 255), 2)
    text(L, (30, yy + 14), 'crew after hire', font('courier', 20), INK)
    text(L, (480, yy + 10), '5 / 4', font('anton', 34), INK, 'ra')
    text(L, (30, yy + 50), 'over the crew places: recruit cost applies', font('courier', 17), (110, 60, 40, 255))
    rotate_paste(img, L, (X0 + X1) / 2, (Y0 + Y1) / 2, .8, shadow=False)
    class_badge(img, 'SAPPER', 1850, 318, 28, rot=10)
    tape(img, 1640, 118, 140, 30, rot=-3)
    die_sticker(img, 'HIRE  12 cr', 1640, 990, 300, 70, LIME, rot=-2, size=44)
    # the crew as it stands, where the hire will land
    text(img, (268, 870), 'CREW  4 / 4 places', font('mono', 18), CYAN)
    for i, (n, c, lv, xp, ix) in enumerate(CREW):
        x = 268 + i * 214
        art = portrait_art(c, 96, 110, ix)
        img.paste(art, (S(x), S(900)))
        rect(img, [x, 900, x + 96, 1010], outline=CLASS[c]['col'], width=3)
        text(img, (x + 106, 916), n, font('anton', 28), WHITE)
        text(img, (x + 106, 952), '%s LV%d' % (c, lv), font('mono', 15), CLASS[c]['col'])
    x = 268 + 4 * 214
    for k in range(0, 96, 14):
        line(img, [(x + k, 900), (x + k + 8, 900)], LIME, 3); line(img, [(x + k, 1010), (x + k + 8, 1010)], LIME, 3)
    for k in range(0, 110, 14):
        line(img, [(x, 900 + k), (x, 900 + k + 8)], LIME, 3); line(img, [(x + 96, 900 + k), (x + 96, 900 + k + 8)], LIME, 3)
    text(img, (x + 48, 955), '+', font('anton', 60), LIME, 'mm')
    text(img, (x + 106, 930), 'VOSS', font('anton', 28), LIME)
    frame_caption(img, 'B-107 HQ screen  RECRUIT: portrait card, details, cost (over the hq_idle map page)')
    return finish_save(img, 'hq_recruit.png')


# ================================================================ WEAPONS
ARMORY = [('Rail Rifle', 'HEAVY', 9, 1, 4, 1, 2, ('LONG',), '1 heavy slug at long reach.', 'GUNNER'),
          ('Overload Coil', 'TECH', 8, 1, 2, 2, 2, ('x2 JAMMED',), '2 shots; x2 on a jammed unit.', 'HACKER'),
          ('Bulwark Plate', 'BUILD', 7, 1, -1, -1, -1, ('10 HP WALL',), 'A 10 hp barricade on its cell.', 'FIXER'),
          ('Flamer', 'BLAST', 6, 1, 1, 2, 1, ('WHOLE CELL',), '2 bursts at reach 1.', 'SAPPER'),
          ('Pulse Beam', 'TECH', 9, 1, 2, 1, 6, ('ROW', 'NO ARMOR'), 'A beam along its row, reach 6.', None),
          ('Drone Swarm', 'AUTO', 8, 1, 1, 2, 2, ('AUTO',), '2 shots at long reach.', None),
          ('Razor Wire', 'BUILD', 5, 1, -1, -1, -1, ('BITES',), '2 hp wall, 2 to each smasher.', None),
          ('Long Rifle', 'HEAVY', 14, 2, 3, 1, 4, ('RARE',), 'Shoots the toughest in reach.', 'GUNNER')]


def roster_row(img, x, y, w, name, cls, lvl, idx, slots, locker=None, sel=False, note=None):
    h = 168
    c = CLASS[cls]['col']
    rrect(img, [x, y, x + w, y + h], 14, fill=WHITE)
    rrect(img, [x + 4, y + 4, x + w - 4, y + h - 4], 11, fill=INK)
    if sel:
        rrect(img, [x - 5, y - 5, x + w + 5, y + h + 5], 16, outline=LIME, width=4)
    art = portrait_art(cls, 120, h - 16, idx)
    m = Image.new('L', art.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, art.width, art.height), radius=S(8), fill=255)
    img.paste(art, (S(x + 8), S(y + 8)), m)
    class_badge(img, cls, x + 14, y + 16, 20, rot=-8)
    text(img, (x + 142, y + 28), name, font('anton', 34), WHITE, 'lm')
    text(img, (x + 142, y + 60), '%s . LV%d' % (cls, lvl), font('mono', 16), c, 'lm')
    sx = x + 142
    for s_ in slots:
        sw = 96
        if s_ == 'LOCKED':
            rrect(img, [sx, y + 80, sx + sw, y + 156], 8, fill=(26, 22, 38, 255), outline=(90, 90, 120, 255), width=2)
            put_glyph(img, 'state_locked', sx + sw / 2, y + 106, 26, (120, 120, 150, 255))
            text(img, (sx + sw / 2, y + 140), '+SLOT 30cr', font('mono', 13), (150, 150, 180, 255), 'mm')
        elif s_:
            wn, st = s_
            rrect(img, [sx, y + 80, sx + sw, y + 156], 8, fill=WHITE, outline=INK, width=2)
            put_glyph(img, WGLYPH.get(wn, 'raid_smg'), sx + sw / 2, y + 108, 44, INK)
            stars(img, sx + sw / 2 - 26, y + 134, st, 3, 15)
        else:
            rrect(img, [sx, y + 80, sx + sw, y + 156], 8, fill=(30, 26, 44, 255), outline=LIME, width=2)
            text(img, (sx + sw / 2, y + 118), 'EMPTY', font('mono', 14), LIME, 'mm')
        sx += sw + 10
    if locker is not None:
        line(img, [(sx + 4, y + 84), (sx + 4, y + 152)], (90, 90, 120, 255), 2)
        text(img, (sx + 16, y + 92), 'LOCKER', font('mono', 13), DIM)
        if locker:
            rrect(img, [sx + 16, y + 106, sx + 76, y + 156], 6, fill=(220, 220, 228, 255), outline=INK, width=2)
            put_glyph(img, WGLYPH.get(locker[0], 'raid_smg'), sx + 46, y + 128, 34, INK)
    if note:
        hand(img, (x + 470, y + 26), note, 24, YEL, rot=-3)


def weapons():
    img = hq_base('MARKET', 'WEAPONS', 'the armory, and who carries what')
    # the shop: filters + 8 cards
    x0 = 252
    fx = x0
    for s_, on in (('ALL', True), ('AUTO', False), ('HEAVY', False), ('BLAST', False), ('BUILD', False), ('TECH', False)):
        col = FAMILY.get(s_, LIME)
        fx = chip(img, fx, 112, s_, font('anton', 22), INK if on else col, bg=LIME if on else (18, 20, 30, 230), edge=None if on else col, pad=12, h=40) + 8
    text(img, (fx + 14, 132), 'stock turns over after every raid', font('plex', 19), DIM, 'lm')
    cw, ch = 214, 372
    for i, (n, fam, cost, st, dm, sh, rc, kw, tx, part) in enumerate(ARMORY):
        r_, c_ = divmod(i, 4)
        weapon_card(img, x0 + c_ * (cw + 18), 172 + r_ * (ch + 40), cw, ch, n, fam, cost, st, dm, sh, rc, kw, tx,
                    rot=(-1, .8, -.5, 1.2, .6, -1.1, .9, -.4)[i], partner=part, sel=(i == 0), locked=(i == 7))
    sticker(img, 'RARE', x0 + 3 * (cw + 18) + cw - 30, 172 + ch + 40 + 30, 90, 38, YEL, None, rot=10, size=24)
    hand(img, (x0 + 3 * (cw + 18) + 20, 172 + 2 * (ch + 40) - 64), 'needs 14 cr', 26, PINK, rot=-4)
    # the roster
    RX = 1210
    glass(img, [RX - 16, 100, 1900, 1062], title='ROSTER  .  drag a weapon onto a slot  .  2 alike merge', tsize=18)
    ros = [('MAKO', 'GUNNER', 2, 5, [('Rail Rifle', 2), None, 'LOCKED'], [], True, '-> *** merge'),
           ('URSA', 'SAPPER', 1, 1, [('Breach Shotgun', 2), ('Shaped Charge', 1), 'LOCKED'], [('Flamer', 1)], False, None),
           ('OZZY', 'HACKER', 1, 9, [('Jammer Rig', 1), ('SMG', 1), 'LOCKED'], [], False, None),
           ('NYX', 'FIXER', 1, 6, [('Barrier Kit', 1), None, 'LOCKED'], [], False, None)]
    for i, (n, c, lv, ix, sl, lk, sel, note) in enumerate(ros):
        roster_row(img, RX, 154 + i * 190, 676, n, c, lv, ix, sl, locker=(lk[0] if lk else ()), sel=sel, note=note)
    arrow_hand(img, [(462, 300), (640, 168), (1100, 160), (1390, 262)], LIME, 6)
    text(img, (RX, 932), 'MERGE', font('mono', 18), CYAN)
    text(img, (RX, 958), 'Rail ** + Rail * -> *** (MAKO)', font('anton', 26), WHITE)
    text(img, (RX, 996), 'raid planning merges too', font('plex', 17), DIM)
    die_sticker(img, 'BUY  9 cr', 1760, 1012, 220, 60, LIME, rot=-2, size=38)
    frame_caption(img, 'B-107 HQ screen  WEAPONS: a shop + the roster (over the hq_idle map page)')
    return finish_save(img, 'hq_weapons.png')


# ================================================================ TALENTS
def talent_card(img, x, y, w, h, tid, state='owned', rot=0):
    name, cls, tx = TAL[tid]
    c = CLASS[cls]['col'] if cls else CYAN
    L = layer(w + 30, h + 30); o = 15
    rrect(L, [o, o, o + w, o + h], 10, fill=(244, 240, 228, 255) if state != 'locked' else (190, 188, 182, 255), outline=INK, width=2)
    rect(L, [o, o, o + w, o + 12], fill=c)
    poly(L, [(o + w - 64, o), (o + w, o), (o + w, o + 64)], fill=c)
    text(L, (o + 18, o + 34), 'TALENT . %s' % (cls or 'any class'), font('mono', 15), (90, 90, 96, 255))
    f = font('anton', 30 if len(name) < 13 else 25)
    text(L, (o + 18, o + 58), name, f, INK)
    line(L, [(o + 18, o + 104), (o + w - 18, o + 104)], (180, 170, 150, 255), 2)
    rich(L, o + 18, o + 118, tx, font('plex', 20), w - 36, (40, 40, 48, 255), (190, 40, 120, 255))
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(6, 10, 14, 150))
    if state == 'owned':
        sticker(img, 'OWNED', x + w - 48, y + h - 20, 110, 36, LIME, None, rot=-6, size=24)
    if state == 'offer':
        pencil_circle(img, x + w / 2, y + h / 2, w * .58, h * .56, YEL, 5, seed=int(x))


def talents():
    img = hq_base('CREW', 'TALENTS', 'what MAKO has, and everything MAKO could get')
    op_card(img, 256, 120, 330, 640, 'MAKO', 'GUNNER', 3, (0, 12), 5, traits=['MASTER', 'OPPORTUNIST'],
            talents=['HEADHUNTER', 'VETERAN HANDS'], weapons=[('Rail Rifle', 2), None], trait_desc=TRAIT)
    text(img, (262, 790), 'LEVEL 3 . 1 pick waiting', font('anton', 26), YEL)
    text(img, (262, 826), 'a pick at every level up; picks are', font('plex', 19), DIM)
    text(img, (262, 850), 'drawn from the dossier below', font('plex', 19), DIM)
    # what MAKO has
    text(img, (630, 116), 'MAKO HAS', font('anton', 34), WHITE)
    talent_card(img, 630, 166, 250, 290, 'head', 'owned', rot=-1.2)
    talent_card(img, 900, 166, 250, 290, 'vethands', 'owned', rot=1)
    line(img, [(1182, 130), (1182, 470)], (92, 225, 255, 90), 2)
    text(img, (1210, 116), 'LEVEL UP: PICK 1', font('anton', 34), YEL)
    for i, t in enumerate(('scope', 'rangefinder', 'shot')):
        talent_card(img, 1210 + i * 232, 166, 214, 290, t, 'plain', rot=(-1, .6, 1.4)[i])
    pencil_circle(img, 1210 + 232 + 107, 311, 132, 172, YEL, 5, seed=3)
    hand(img, (1215, 492), 'with the Rail: no LONG penalty', 26, YEL, rot=-2)
    die_sticker(img, 'TAKE RANGE FINDER', 1766, 514, 270, 50, LIME, rot=-2, size=28)
    # the dossier: a manila folder, one tab per operative (planning file, not a tree)
    FX0, FY0, FX1, FY1 = 620, 560, 1900, 1060
    tabs = [('MAKO', 'GUNNER', True), ('URSA', 'SAPPER', False), ('OZZY', 'HACKER', False), ('NYX', 'FIXER', False)]
    for i, (n, c, on) in enumerate(tabs):
        tx0 = FX0 + 30 + i * 170
        poly(img, [(tx0, FY0 + 10), (tx0 + 14, FY0 - 34), (tx0 + 146, FY0 - 34), (tx0 + 160, FY0 + 10)],
             fill=(232, 208, 156, 255) if on else (190, 168, 124, 255), outline=(120, 96, 60, 255), width=2)
        text(img, (tx0 + 80, FY0 - 12), n, font('anton', 24), INK if on else (90, 74, 50, 255), 'mm')
    rrect(img, [FX0, FY0, FX1, FY1], 8, fill=(232, 208, 156, 255), outline=(120, 96, 60, 255), width=3)
    text(img, (FX0 + 26, FY0 + 18), 'DOSSIER . MAKO . GUNNER', font('anton', 30), INK)
    text(img, (FX0 + 420, FY0 + 30), 'every talent MAKO could get: 2 Gunner + 23 any class . planning only', font('courier', 19), (80, 64, 40, 255))
    # gunner block
    gy = FY0 + 72
    text(img, (FX0 + 26, gy), 'GUNNER ONLY', font('mono', 18), CLASS['GUNNER']['col'])
    for i, t in enumerate(('rangefinder', 'vethands')):
        bx = FX0 + 26; by = gy + 30 + i * 96
        rrect(img, [bx, by, bx + 330, by + 84], 6, fill=(246, 236, 210, 255), outline=(150, 120, 80, 255), width=2)
        text(img, (bx + 14, by + 8), TAL[t][0], font('anton', 24), INK)
        rich(img, bx + 14, by + 42, TAL[t][2], font('plex', 16), 300, (60, 52, 40, 255), (190, 40, 120, 255), lh=18)
    tick(img, FX0 + 320, gy + 30 + 96 + 20, 26, (40, 120, 40, 255))
    pencil_circle(img, FX0 + 191, gy + 30 + 42, 180, 52, (200, 120, 0, 255), 4, seed=9)
    # any class grid
    ax = FX0 + 380
    text(img, (ax, gy), 'ANY CLASS', font('mono', 18), (40, 110, 150, 255))
    gen = [k for k, v in TAL.items() if not v[1]]
    owned = {'head'}; offer = {'scope', 'shot'}
    cols = 4; cwid = 214; rh = 36
    for i, t in enumerate(gen):
        c_, r_ = divmod(i, 6)
        bx = ax + c_ * cwid; by = gy + 24 + r_ * 63
        st = 'owned' if t in owned else ('offer' if t in offer else '')
        text(img, (bx, by), TAL[t][0], font('anton', 21), INK if st != '' or True else INK)
        rich(img, bx, by + 28, TAL[t][2], font('plex', 14), cwid - 16, (70, 60, 46, 255), (170, 40, 110, 255), lh=16)
        if st == 'owned':
            tick(img, bx + tw(TAL[t][0], font('anton', 21)) + 8, by + 14, 22, (40, 120, 40, 255), 4)
        if st == 'offer':
            pencil_circle(img, bx + tw(TAL[t][0], font('anton', 21)) / 2, by + 14, tw(TAL[t][0], font('anton', 21)) / 2 + 14, 18, (200, 120, 0, 255), 3, seed=i)
    postit(img, (680, 880, 930, 1030), (255, 230, 90, 255), 'MAKO: go LONG.\nSTAR POWER next,\nthen EXTRA MAG', rot=-3, size=24)
    frame_caption(img, 'B-107 HQ screen  TALENTS: what the operative has + the dossier (over the hq_idle map page)')
    return finish_save(img, 'hq_talents.png')


if __name__ == '__main__':
    which = sys.argv[1:] or ['recruit', 'weapons', 'talents']
    for w_ in which:
        {'recruit': recruit, 'weapons': weapons, 'talents': talents}[w_]()
