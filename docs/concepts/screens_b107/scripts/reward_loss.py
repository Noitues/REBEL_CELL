"""B-107 missing plates (2026-11-17): the netrun room reward screens (vertical slice v49-1 rules), the campaign-loss printout
(T11) with the runner-lost variant, and the raid stop banner spec crop. PIL only, this set's kit.

    python reward_loss.py [a b c d_mid d_final loss stop]      (no argument = all)

Rules drawn (v49-1): ROUTER win = a card pick only (no flat credits, no run health, no Heat); held segments above the asset
cap pay 2 cr each (max 6), unbanked until a rack. ELITE = a richer card pick (a POWER card can appear) + 2 implants (pick 1),
Heat +1. TERMINAL (no fight) = one of: the implant shown / upgrade 2 listed cards / heal 5 run health. SERVER RACK mid =
the ELITE rewards + BANKED + heal 6; final = card + 2 implants, BANKED, SITE CLAIMED, Heat +8 (+3 on a tier 3 site).
MAINFRAME is a shop (not a reward); BLOCK SERVER is HQ-only (not drawn). Amounts are tuning numbers.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *   # noqa

# ------------------------------------------------------------------ netrun card vocabulary
CTYPE = {'HACK': PINK, 'SYSTEM': CYAN, 'GUARD': (120, 230, 90, 255), 'POWER': (255, 196, 40, 255)}
CARDS = {  # name: (ram, type, text, glyph, rarity)  -- real content/cards text; POWER cards are art placeholders (v49 type)
    'STATIC SHOCK': (1, 'HACK', 'Deal [4] damage to the target.', 'picto_target', 0),
    'TAILSPIN': (2, 'SYSTEM', 'Spin a wheel [4] ticks and draw [1] card.', 'picto_spin', 1),
    'SANITIZE': (1, 'GUARD', 'Remove CORRUPTED from a chosen slice and gain [3] block.', 'placeholder_shield', 0),
    'LEECH WORM': (3, 'HACK', 'The enemy slice under your pointer gets a [PARASITE] (half output). Exhaust.', 'placeholder_burn', 2),
    'SHORT CIRCUIT': (3, 'HACK', 'Disable the target Hub for [2] turns. Exhaust.', 'raid_jammer', 2),
    'COLD SNAP': (3, 'SYSTEM', 'The target skips its next respin and you gain [3] block.', 'picto_spin_ccw', 1),
    'BACKDOOR': (2, 'POWER', 'Stays in play. At the start of each turn gain [1] RAM.', 'placeholder_key', 2),
    'ROOT KIT': (1, 'POWER', 'Stays in play. Your first nudge each turn is [free].', 'picto_again', 2),
    'DEAD MAN SWITCH': (2, 'POWER', 'Stays in play. When you take damage, deal [2] back.', 'placeholder_bomb', 2),
    'MIRROR SHARD': (2, 'POWER', 'Stays in play. Your Perfect slices resolve [twice].', 'placeholder_vault', 2),
    'FIREWALL': (1, 'GUARD', 'Gain [6] block.', 'placeholder_shield', 0),
}
IMPLANTS = {  # firmware pool text (content/firmware) shown under the v49 name IMPLANT
    'OVERVOLT': ('ATK and CRIT slices: output [+25%].', 'ATK . CRIT'),
    'SIPHON': ('ATK slice heals you [2] on Good or better.', 'ATK'),
    'TRACER': ('ATK or CRIT slice strips [1] resistance on a Perfect.', 'ATK . CRIT'),
    'STATIC COAT': ('DEF slice also grants [2] shield.', 'DEF'),
    'BULKHEAD': ('DEF and SHIELD slices: output [+50%].', 'DEF . SHIELD'),
}
HEATC = (255, 120, 40, 255)


def net_card(img, x, y, w, h, name, rot=0, sel=False, dim=False, plus=False, unique=False):
    """A netrun deck card in this set's vinyl: white die-cut, ink body, RAM cost disc, type-colour art field with the glyph,
    type band, effect text, rarity pips. POWER cards get a gold keyline."""
    ram, ct, tx, gname, rar = CARDS[name]
    tc = CTYPE[ct]
    L = layer(w + 40, h + 40)
    o = 20
    if sel:
        gl = layer(w + 40, h + 40)
        rrect(gl, [o - 8, o - 8, o + w + 8, o + h + 8], 20, fill=LIME)
        L = glow(L, gl, 12, 1.6)
        rrect(L, [o - 8, o - 8, o + w + 8, o + h + 8], 20, outline=LIME, width=5)
    rrect(L, [o, o, o + w, o + h], 16, fill=WHITE)
    if ct == 'POWER':
        rrect(L, [o + 3, o + 3, o + w - 3, o + h - 3], 14, fill=tc)
    rrect(L, [o + 7, o + 7, o + w - 7, o + h - 7], 12, fill=INK)
    mini = w < 200
    top = 50 if not mini else w * .2
    fh = h * (.40 if not mini else .46)
    fld = vgrad(S(w - 18), S(fh), tuple(int(v * .8) for v in tc[:3]) + (255,), tuple(int(v * .22) for v in tc[:3]) + (255,))
    fld.alpha_composite(halftone(S(w - 18), S(fh), (255, 255, 255, 46), step=7, rmax=2.4, fall=(.2, 1.0)))
    m = Image.new('L', fld.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fld.width, fld.height + S(20)), radius=S(10), fill=255)
    L.paste(fld, (S(o + 9), S(o + 9 + top)), m)
    gs = min(w * .5, fh * .74)
    gx, gy = o + w / 2 - gs / 2, o + 9 + top + fh / 2 - gs / 2
    L.alpha_composite(glyph(gname, int(gs), (0, 0, 0, 130)), (S(gx + 4), S(gy + 6)))
    L.alpha_composite(glyph(gname, int(gs), WHITE), (S(gx), S(gy)))
    # cost + name
    nm = name + ('+' if plus else '')
    if mini:
        cr = top * .36
        ellipse(L, [o + 10, o + 10, o + 10 + 2 * cr, o + 10 + 2 * cr], fill=YEL, outline=INK, width=2)
        text(L, (o + 10 + cr, o + 11 + cr), str(ram), font('anton', int(cr * 1.3)), INK, 'mm')
        fs = int(top * .5)
        while fs > 9 and tw(nm, font('anton', fs)) > w - 2 * cr - 34:
            fs -= 1
        text(L, (o + 18 + 2 * cr, o + 11 + cr), nm, font('anton', fs), YEL if plus else WHITE, 'lm')
        by = o + 9 + top + fh + 4
        rect(L, [o + 9, by, o + w - 9, by + max(12, h * .09)], fill=tc)
        text(L, (o + w / 2, by + max(12, h * .09) / 2), ct, font('anton', max(10, int(h * .07))), INK, 'mm')
    else:
        ellipse(L, [o + 12, o + 12, o + 56, o + 56], fill=YEL, outline=INK, width=3)
        text(L, (o + 34, o + 35), str(ram), font('anton', 30), INK, 'mm')
        f = font('anton', 30 if len(nm) < 12 else (25 if len(nm) < 15 else 21))
        text(L, (o + 66, o + 36), nm, f, YEL if plus else WHITE, 'lm')
        by = o + 9 + top + fh + 6
        rect(L, [o + 9, by, o + w - 9, by + 30], fill=tc)
        text(L, (o + w / 2, by + 15), ct, font('anton', 22), INK, 'mm')
        rich(L, o + 22, by + 44, tx, font('plex', 19), w - 44, (232, 232, 240, 255), YEL, lh=24)
    for k in range(rar + 1 if not mini else 0):
        ellipse(L, [o + w - 26 - k * 16, o + h - 26, o + w - 14 - k * 16, o + h - 14], fill=(tc if rar else DIM))
    if dim:
        sh = layer(w + 40, h + 40); rrect(sh, [o, o, o + w, o + h], 16, fill=(6, 6, 12, 150)); L.alpha_composite(sh)
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(8, 12, 16, 160))
    if unique:
        sticker(img, 'UNIQUE', x + w - 40, y + 12, 110, 34, YEL, None, rot=8, size=22)


def implant_tile(img, x, y, w, h, name, rot=0, sel=False, dim=False):
    """An implant: a die-cut microchip sticker (pins, lime die) beside its name tape, effect and the slices it fits."""
    tx, fits = IMPLANTS[name]
    L = layer(w + 40, h + 40); o = 20
    if sel:
        gl = layer(w + 40, h + 40)
        rrect(gl, [o - 8, o - 8, o + w + 8, o + h + 8], 18, fill=LIME)
        L = glow(L, gl, 12, 1.6)
        rrect(L, [o - 8, o - 8, o + w + 8, o + h + 8], 18, outline=LIME, width=5)
    rrect(L, [o, o, o + w, o + h], 14, fill=WHITE)
    rrect(L, [o + 6, o + 6, o + w - 6, o + h - 6], 10, fill=INK)
    # the chip
    cx0, cy0, cs = o + 22, o + 22, min(96, h - 64)
    for k in range(6):
        px = cx0 + cs * .12 + k * cs * .15
        rect(L, [px, cy0 - 10, px + 6, cy0], fill=(200, 200, 210, 255)); rect(L, [px, cy0 + cs, px + 6, cy0 + cs + 10], fill=(200, 200, 210, 255))
        py = cy0 + cs * .12 + k * cs * .15
        rect(L, [cx0 - 10, py, cx0, py + 6], fill=(200, 200, 210, 255)); rect(L, [cx0 + cs, py, cx0 + cs + 10, py + 6], fill=(200, 200, 210, 255))
    rrect(L, [cx0, cy0, cx0 + cs, cy0 + cs], 8, fill=(40, 44, 58, 255), outline=WHITE, width=3)
    rrect(L, [cx0 + cs * .17, cy0 + cs * .17, cx0 + cs * .83, cy0 + cs * .83], 5, fill=LIME)
    gsz = int(cs * .5)
    L.alpha_composite(glyph('picto_target' if 'ATK' in fits else 'placeholder_shield', gsz, INK), (S(cx0 + cs / 2 - gsz / 2), S(cy0 + cs / 2 - gsz / 2)))
    text(L, (cx0 + cs / 2, cy0 + cs + 24), 'IMPLANT', font('mono', 15), LIME, 'mm')
    X = cx0 + cs + 26
    f = font('anton', 30)
    rect(L, [X - 2, o + 20, X + tw(name, f) + 22, o + 62], fill=WHITE)
    text(L, (X + 10, o + 42), name, f, INK, 'lm')
    rich(L, X, o + 76, tx, font('plex', 19), w - (X - o) - 22, (232, 232, 240, 255), YEL, lh=24)
    text(L, (X, o + h - 30), 'fits  ' + fits, font('mono', 16), DIM, 'lm')
    if dim:
        sh = layer(w + 40, h + 40); rrect(sh, [o, o, o + w, o + h], 14, fill=(6, 6, 12, 150)); L.alpha_composite(sh)
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(8, 12, 16, 160))


# ------------------------------------------------------------------ the frame: the dimmed netrun street + run HUD
def street_bg():
    im = load_bg('transitions/v6/plates/netrun_street_won.png')
    im = im.filter(ImageFilter.GaussianBlur(S(3)))
    im = ImageEnhance.Color(im).enhance(.75)
    return ImageEnhance.Brightness(im).enhance(.44)


def run_hud(img, hp=(31, 50), cr=14, heat=36, banked=False, deck=18, heat_add=None):
    """the netrun HUD as it stands under the reward: runner + run health, unbanked credits, Heat, the deck"""
    glass(img, [18, 14, 760, 86], edge=CYAN)
    art = portrait_art('GUNNER', 56, 56, 5)
    img.paste(art, (S(30), S(22)))
    text(img, (98, 50), 'MAKO', font('anton', 30), WHITE, 'lm')
    put_glyph(img, 'picto_hp', 200, 50, 30, PINK)
    bar(img, 222, 39, 160, 22, hp[0] / hp[1], PINK, seg=10)
    text(img, (392, 51), '%d/%d' % hp, font('anton', 28), WHITE, 'lm')
    ellipse(img, [478, 36, 506, 64], fill=YEL, outline=INK, width=3)
    text(img, (492, 51), '$', font('anton', 20), INK, 'mm')
    text(img, (514, 51), str(cr), font('anton', 32), WHITE, 'lm')
    text(img, (514 + tw(str(cr), font('anton', 32)) + 8, 52), 'BANKED' if banked else 'unbanked', font('mono', 15), LIME if banked else AMB, 'lm')
    put_glyph(img, 'placeholder_burn', 666, 50, 28, HEATC)
    text(img, (684, 51), str(heat), font('anton', 32), (255, 150, 90, 255), 'lm')
    # deck pile, bottom left (where a picked card lands)
    glass(img, [24, 952, 240, 1052], edge=PINK)
    text(img, (44, 972), 'DECK', font('mono', 18), PINK)
    text(img, (222, 1002), str(deck), font('anton', 60), PINK, 'rm')
    text(img, (44, 1028), 'cards', font('mono', 15), DIM)


def crumb(img, s, x=790, y=24):
    f = font('mono', 20)
    w = tw(s, f) + 40
    rrect(img, [x, y, x + w, y + 52], 8, fill=NAVY, outline=CYAN, width=2)
    text(img, (x + 20, y + 27), s, f, CYAN, 'lm')


def section(img, box, title, sub=None, edge=LIME):
    glass(img, box, edge=edge, fill=(8, 20, 12, 236), title=title, tsize=20, rule=edge)
    if sub:
        text(img, (box[2] - 20, box[1] + 22), sub, font('mono', 16), DIM, 'ra')


def heat_sticker(img, cx, cy, s, sub=None, rot=5, w=None):
    sticker(img, s, cx, cy, w or (tw(s, font('anton', 40)) + 56), 64, HEATC, None, rot=rot, size=40)
    if sub:
        text(img, (cx, cy + 56), sub, font('mono', 15), (255, 180, 140, 255), 'mm')


def card_row(img, names, x, y, w=290, h=390, gap=30, sel=None, rots=(-1.5, 0, 1.5), lift=22, unique=()):
    for i, n in enumerate(names):
        yy = y - (lift if i == sel else 0)
        net_card(img, x + i * (w + gap), yy, w, h, n, rot=rots[i % len(rots)] if i != sel else 0, sel=(i == sel), unique=n in unique)


def pick_hint(img, x, y, s='PICK 1', col=YEL):
    hand(img, (x, y), s, 34, col, rot=-3)


def skip_btn(img, cx, cy, label='SKIP'):
    sticker(img, label, cx, cy, tw(label, font('anton', 34)) + 46, 56, WHITE, None, rot=2, size=34)


def continue_btn(img, cx=1720, cy=1004, armed=True):
    sticker(img, 'CONTINUE', cx, cy, 290, 74, PINK if armed else (120, 120, 140, 255), None, rot=-2, size=52)
    chip(img, cx - 30, cy + 50, 'SPACE', font('mono', 15), WHITE, NAVY, CYAN, pad=8)


def deck_arrow(img, sx, sy, s='+1 = 19'):
    arrow_hand(img, [(sx, sy), (sx - 140, sy + 70), (sx - 340, sy + 170), (262, 975)], YEL, 6, head=24, seed=7)
    hand(img, (40, 912), s, 32, YEL, rot=-4)


def seg_ring(img, cx, cy, r, held=12, cap=9, n=12):
    """the fight's wheel, small: segments held up to the asset cap (lime), held above it (amber), not held (grey)"""
    for k in range(n):
        a0, a1 = -90 + k * 360 / n + 2, -90 + (k + 1) * 360 / n - 2
        col = LIME if k < min(held, cap) else (AMB if k < held else (60, 64, 80, 255))
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 8)]
        pts += [(cx + r * .58 * math.cos(math.radians(a)), cy + r * .58 * math.sin(math.radians(a))) for a in np.linspace(a1, a0, 8)]
        poly(img, pts, fill=col, outline=INK, width=2)
    a = -90 + cap * 360 / n
    line(img, [(cx + r * .45 * math.cos(math.radians(a)), cy + r * .45 * math.sin(math.radians(a))),
               (cx + r * 1.2 * math.cos(math.radians(a)), cy + r * 1.2 * math.sin(math.radians(a)))], WHITE, 4)
    text(img, (cx, cy + 1), 'CAP', font('mono', 15), WHITE, 'mm')


def banked_block(img, x, y, heal=None, w=420):
    """BANKED: the credits and raid assets carried so far are safe from here on"""
    section(img, (x, y, x + w, y + 220), 'SERVER RACK  .  BANK')
    stamp(img, 'BANKED', x + 130, y + 104, LIME, rot=-7, size=54)
    text(img, (x + 250, y + 74), '14 cr', font('anton', 34), WHITE)
    text(img, (x + 250, y + 114), '1 raid asset', font('anton', 26), WHITE)
    text(img, (x + 24, y + 168), 'credits and raid assets safe', font('mono', 17), LIME)
    if heal:
        rrect(img, [x, y + 236, x + w, y + 300], 10, fill=NAVY, outline=PINK, width=2)
        put_glyph(img, 'picto_hp', x + 34, y + 268, 32, PINK)
        text(img, (x + 62, y + 268), 'HEAL %d' % heal[0], font('anton', 32), PINK, 'lm')
        text(img, (x + w - 20, y + 268), 'run health %d > %d / 50' % (heal[1], heal[1] + heal[0]), font('mono', 17), WHITE, 'rm')


def finish_reward(img, name, cap):
    frame_caption(img, cap)
    return finish_save(img, name, vig=.3)


# ================================================================== (a) ROUTER
def plate_a():
    img = street_bg()
    run_hud(img, hp=(31, 50), cr=14, heat=36, deck=18)
    crumb(img, 'REWARD  //  SEED VAULT EXCHANGE . T2  //  ROUTER . LAYER 3 OF 7')
    sticker(img, 'ROUTER CLEARED', 330, 160, 470, 92, LIME, None, rot=-4, size=66)
    section(img, (170, 230, 1180, 800), 'CARD  .  PICK 1 OF 3  .  to the deck', sub='skip = keep the deck as it is')
    card_row(img, ['STATIC SHOCK', 'TAILSPIN', 'SANITIZE'], 220, 330, sel=1)
    skip_btn(img, 675, 860)
    deck_arrow(img, 675, 735)
    # held segments over the asset cap -> credits (the only credits a ROUTER pays)
    section(img, (1240, 230, 1890, 600), 'OVER THE ASSET CAP', edge=AMB)
    seg_ring(img, 1340, 360, 62, held=12, cap=9)
    text(img, (1430, 316), 'wheel held 12/12', font('anton', 28), WHITE)
    text(img, (1430, 352), 'asset cap 9: 3 above it', font('plex', 21), AMB)
    text(img, (1270, 484), '+6 cr', font('anton', 56), YEL, 'lm')
    text(img, (1420, 486), '2 cr each, max 6', font('mono', 18), DIM, 'lm')
    rrect(img, [1266, 530, 1600, 568], 8, fill=(40, 26, 6, 255), outline=AMB, width=2)
    text(img, (1282, 549), 'unbanked until a rack', font('mono', 18), AMB, 'lm')
    hand(img, (1250, 626), 'none over the cap: this panel is hidden', 24, DIM, rot=-1)
    # what a ROUTER never pays (spec note, pencil)
    hand(img, (1250, 700), 'ROUTER: no flat credits,', 30, YEL, rot=-2)
    hand(img, (1250, 740), 'no run health, no Heat', 30, YEL, rot=-2)
    continue_btn(img)
    return finish_reward(img, 'netrun_reward_a.png', 'netrun reward (a) ROUTER win: card pick 1 of 3 or SKIP; held segments over the asset cap pay 2 cr each (max 6), unbanked')


# ================================================================== (b) ELITE
def plate_b():
    img = street_bg()
    run_hud(img, hp=(24, 50), cr=20, heat=37, deck=19)
    crumb(img, 'REWARD  //  SEED VAULT EXCHANGE . T2  //  ELITE ROUTER . LAYER 5 OF 7')
    sticker(img, 'ELITE DOWN', 300, 160, 400, 92, YEL, None, rot=-4, size=66)
    heat_sticker(img, 640, 146, 'HEAT +1', sub='36 > 37 (elite)')
    section(img, (170, 230, 1180, 800), 'CARD  .  PICK 1 OF 3  .  rarer pool', sub='a POWER card can appear')
    card_row(img, ['LEECH WORM', 'BACKDOOR', 'COLD SNAP'], 220, 330, sel=1)
    skip_btn(img, 675, 872)
    section(img, (1240, 230, 1890, 800), 'IMPLANT  .  PICK 1 OF 2', sub='skip allowed')
    implant_tile(img, 1270, 300, 590, 200, 'OVERVOLT', rot=-1)
    implant_tile(img, 1270, 530, 590, 200, 'SIPHON', rot=1, sel=True)
    skip_btn(img, 1565, 872)
    text(img, (1250, 930), 'two separate picks: a card AND an implant', font('mono', 17), DIM)
    deck_arrow(img, 675, 735, '+1 = 20')
    continue_btn(img)
    return finish_reward(img, 'netrun_reward_b.png', 'netrun reward (b) ELITE win: richer card pick (POWER possible) + implant pick 1 of 2; Heat +1')


# ================================================================== (c) TERMINAL
def plate_c():
    img = street_bg()
    run_hud(img, hp=(31, 50), cr=14, heat=36, deck=18)
    crumb(img, 'TERMINAL  //  SEED VAULT EXCHANGE . T2  //  LAYER 4 OF 7 . no fight')
    sticker(img, 'TERMINAL', 260, 160, 320, 92, CYAN, None, rot=-4, size=66)
    rrect(img, [450, 136, 1500, 184], 6, fill=(20, 10, 4, 235), outline=(255, 140, 40, 255), width=3)
    text(img, (470, 160), 'DISPATCH // a Solace maintenance port, still logged in. take one thing and go.', font('mono', 19), (255, 200, 140, 255), 'lm')
    text(img, (180, 236), 'CHOOSE ONE', font('anton', 44), WHITE)
    text(img, (420, 258), 'the other two close', font('mono', 18), DIM, 'lm')
    cols = [(180, 'IMPLANT'), (750, 'UPGRADE 2 CARDS'), (1320, 'HEAL')]
    for k, (x, ttl) in enumerate(cols):
        hov = k == 1
        box = (x, 300, x + 540, 880)
        if hov:
            gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
            rrect(gl, [x - 6, 294, x + 546, 886], 14, fill=LIME)
            img = glow(img, gl, 14, .9)
        glass(img, box, edge=LIME if hov else CYAN, fill=(8, 20, 12, 240) if hov else NAVY)
        ellipse(img, [x + 20, 318, x + 64, 362], fill=LIME if hov else CYAN, outline=INK, width=3)
        text(img, (x + 42, 341), str(k + 1), font('anton', 28), INK, 'mm')
        text(img, (x + 80, 340), ttl, font('anton', 38), WHITE, 'lm')
    # 1 the implant shown
    implant_tile(img, 200, 400, 500, 200, 'TRACER')
    text(img, (210, 650), 'the implant is shown before you choose', font('plex', 20), DIM)
    # 2 upgrade the two listed cards (named by the terminal, not picked)
    for i, n in enumerate(('STATIC SHOCK', 'FIREWALL')):
        yy = 390 + i * 230
        net_card(img, 776, yy, 150, 214, n, rot=-2)
        text(img, (956, yy + 107), '>', font('anton', 56), LIME, 'mm')
        net_card(img, 986, yy, 150, 214, n, rot=2, plus=True)
        text(img, (1156, yy + 70), {'STATIC SHOCK': '4 > 6', 'FIREWALL': '6 > 9'}[n], font('anton', 34), YEL, 'lm')
        text(img, (1156, yy + 110), 'damage' if i == 0 else 'block', font('mono', 16), DIM, 'lm')
    text(img, (770, 850), 'both, as listed', font('plex', 20), DIM)
    # 3 heal
    put_glyph(img, 'picto_hp', 1420, 500, 110, PINK)
    text(img, (1500, 470), 'HEAL 5', font('anton', 64), PINK)
    text(img, (1340, 610), 'run health', font('mono', 18), DIM)
    bar(img, 1340, 640, 380, 34, 36 / 50, PINK, seg=10)
    rect(img, [1340 + 380 * 31 / 50, 642, 1340 + 380 * 36 / 50, 672], fill=(255, 255, 255, 140))
    text(img, (1734, 657), '31 > 36', font('anton', 30), WHITE, 'lm')
    text(img, (1340, 700), 'not over the max (50)', font('plex', 20), DIM)
    hand(img, (760, 900), 'hover: lime glass, the choice lifts', 26, YEL, rot=-2)
    sticker(img, 'TAKE IT', 1020, 990, 240, 66, LIME, None, rot=-2, size=44)
    hand(img, (1220, 1000), 'no SKIP drawn: open question (notes)', 22, DIM, rot=-1)
    return finish_reward(img, 'netrun_reward_c.png', 'netrun TERMINAL (no fight): choose one: the implant shown / upgrade the 2 listed cards / heal 5 run health')


# ================================================================== (d) SERVER RACK
def plate_d(final=False):
    img = street_bg()
    run_hud(img, hp=(24, 50) if not final else (19, 50), cr=14, heat=38 if not final else 41, banked=True, deck=20)
    if not final:
        crumb(img, 'REWARD  //  SEED VAULT EXCHANGE . T2  //  SERVER RACK . LAYER 4 OF 7 (mid)')
        sticker(img, 'RACK TAKEN', 300, 160, 400, 92, LIME, None, rot=-4, size=66)
        section(img, (170, 230, 1180, 800), 'CARD  .  PICK 1 OF 3  .  elite pool', sub='a POWER card can appear')
        card_row(img, ['SHORT CIRCUIT', 'ROOT KIT', 'TAILSPIN'], 220, 330, sel=1)
        skip_btn(img, 675, 860)
        section(img, (1240, 230, 1890, 610), 'IMPLANT  .  PICK 1 OF 2')
        implant_tile(img, 1266, 284, 600, 150, 'STATIC COAT', rot=-1, sel=True)
        implant_tile(img, 1266, 446, 600, 150, 'BULKHEAD', rot=1)
        banked_block(img, 1240, 628, heal=(6, 24), w=650)
        deck_arrow(img, 675, 735, '+1 = 21')
        continue_btn(img)
        hand(img, (760, 930), 'mid rack = ELITE rewards + BANKED + heal 6', 24, YEL, rot=-1)
        return finish_reward(img, 'netrun_reward_d_mid.png', 'netrun reward (d) SERVER RACK, mid (layer 4): elite card pick + implant pick, BANKED (credits + raid assets safe), heal 6')
    crumb(img, 'REWARD  //  SEED VAULT EXCHANGE . T2  //  SERVER RACK . LAYER 7 OF 7 (final)')
    sticker(img, 'SITE CLAIMED', 330, 158, 460, 96, LIME, None, rot=-4, size=68)
    heat_sticker(img, 730, 140, 'HEAT +8', sub='+3 more on a tier 3 site', rot=6)
    section(img, (170, 230, 1180, 760), 'CARD  .  PICK 1 OF 3', sub='tier 3: may hold a UNIQUE card')
    card_row(img, ['LEECH WORM', 'BACKDOOR', 'TAILSPIN'], 220, 320, sel=0, h=360)
    skip_btn(img, 1060, 722)
    section(img, (1240, 230, 1890, 610), 'IMPLANT  .  PICK 1 OF 2')
    implant_tile(img, 1266, 284, 600, 150, 'OVERVOLT', rot=-1)
    implant_tile(img, 1266, 446, 600, 150, 'TRACER', rot=1, sel=True)
    banked_block(img, 1240, 640, w=650)
    # variant note: tier 3
    paper(img, (250, 784, 1180, 1046), rot=-.6, col=(246, 240, 214, 255), seed=12)
    text(img, (280, 802), 'VARIANT  .  TIER 3 SITES', font('mono', 18), (90, 70, 40, 255))
    text(img, (280, 830), 'first tier 3 site: the pick is 3 POWER cards', font('courierb', 21), INK)
    text(img, (280, 860), 'any tier 3 site: one offer may be a UNIQUE card', font('courierb', 21), INK)
    for i, n in enumerate(('BACKDOOR', 'DEAD MAN SWITCH', 'MIRROR SHARD')):
        net_card(img, 290 + i * 118, 898, 100, 136, n, rot=(-3, 0, 3)[i])
    hand(img, (640, 960), '3 POWER', 30, (150, 90, 0, 255), rot=-4)
    net_card(img, 840, 898, 100, 136, 'SHORT CIRCUIT', rot=3)
    sticker(img, 'UNIQUE', 1040, 940, 130, 40, YEL, None, rot=-6, size=26)
    hand(img, (980, 990), 'tier 3 only', 24, (150, 90, 0, 255), rot=-4)
    continue_btn(img)
    return finish_reward(img, 'netrun_reward_d_final.png', 'netrun reward (d) SERVER RACK, final (layer 7): card + implant picks, BANKED, SITE CLAIMED, Heat +8 (+3 tier 3); tier 3 variants')


# ================================================================== loss printout (T11) + runner lost (T4 L5) variant
def typed(L, x, y, k, v, vcol=INK, kw=300, size=22):
    text(L, (x, y), k, font('courier', size), (60, 60, 60, 255))
    text(L, (x + kw, y), v, font('courierb', size), vcol)


def plate_loss():
    img = load_bg('transitions/v4/plates/raid_city_capture.jpg')
    img = ImageEnhance.Color(img.filter(ImageFilter.GaussianBlur(S(3)))).enhance(.45)
    img = ImageEnhance.Brightness(img).enhance(.3)
    img.alpha_composite(Image.new('RGBA', img.size, (20, 60, 46, 50)))
    # ---- the dossier folder (T11 K4 composition): survey photo + sample log left, the memo right
    FX0, FY0, FX1, FY1 = 30, 70, 1330, 1050
    poly(img, [(FX0 + 60, FY0 + 6), (FX0 + 90, FY0 - 40), (FX0 + 470, FY0 - 40), (FX0 + 500, FY0 + 6)], fill=(214, 182, 122, 255), outline=(120, 96, 60, 255), width=2)
    text(img, (FX0 + 110, FY0 - 18), 'SB-7718  //  CELL-03', font('courierb', 22), INK, 'lm')
    rrect(img, [FX0, FY0, FX1, FY1], 10, fill=(214, 182, 122, 255), outline=(120, 96, 60, 255), width=3)
    line(img, [(FX0 + 650, FY0 + 10), (FX0 + 650, FY1 - 10)], (150, 120, 76, 255), 3)
    # survey photo (the T11 survey: every node crossed), taped
    src = Image.open(ART + 'solace_endscreens/v2/lose_B.png').convert('RGBA').crop((120, 140, 890, 610))
    ph = layer(600, 420)
    rect(ph, [0, 0, 600, 420], fill=(244, 244, 238, 255))
    ph.alpha_composite(src.resize((S(570), S(340)), Image.LANCZOS), (S(15), S(15)))
    text(ph, (300, 386), 'SITE SURVEY 7  //  NETWORK LOST', font('hand', 26), (40, 60, 160, 255), 'mm')
    rotate_paste(img, ph, FX0 + 330, FY0 + 250, 1.5, sh=(6, 10, 14, 140))
    tape(img, FX0 + 70, FY0 + 50, 120, 30, rot=-30); tape(img, FX0 + 590, FY0 + 50, 120, 30, rot=28)
    # sample log: the crew as identified
    paper(img, (FX0 + 24, FY0 + 490, FX0 + 630, FY1 - 20), rot=-.5, col=(240, 238, 228, 255), seed=8)
    L = layer(600, 460)
    text(L, (20, 20), 'SAMPLE LOG  //  IDENTIFIED OPERATIVES', font('courierb', 21), INK)
    line(L, [(20, 52), (580, 52)], INK, 2)
    rows = [('MAKO', 'GUNNER LV3', 'ON SITE (HQ)', False), ('URSA', 'SAPPER LV2', 'ON SITE (HQ)', False),
            ('OZZY', 'HACKER LV1', 'DECEASED  run 6', True), ('NYX', 'FIXER LV2', 'DECEASED  run 11', True),
            ('VOSS', 'SAPPER LV1', 'ON SITE (A3)', False)]
    for i, (n, c, st, dead) in enumerate(rows):
        yy = 74 + i * 62
        text(L, (24, yy), n, font('courierb', 24), INK)
        text(L, (24, yy + 28), c, font('courier', 17), (90, 90, 90, 255))
        text(L, (300, yy + 4), st, font('courierb', 20), RED if dead else INK)
        if dead:
            line(L, [(20, yy + 14), (180, yy + 14)], INK, 2)
    text(L, (24, 400), 'runners lost: 2 of 5', font('courier', 19), (90, 90, 90, 255))
    rotate_paste(img, L, FX0 + 327, FY0 + 715, -.5, shadow=False)
    stamp(img, 'FILED', FX0 + 540, FY0 + 470, (30, 130, 60, 255), rot=-6, size=46)
    # the memo (right page)
    MX0, MY0, MX1, MY1 = FX0 + 680, FY0 + 24, FX1 - 24, FY1 - 24
    paper(img, (MX0, MY0, MX1, MY1), rot=.4, col=(240, 242, 236, 255), clip=True, seed=14)
    M = layer(MX1 - MX0, MY1 - MY0)
    ellipse(M, [24, 24, 84, 84], outline=CORP_INK, width=4)
    M.alpha_composite(glyph('placeholder_vault', 34, CORP_INK), (S(37), S(37)))
    text(M, (100, 26), 'SOLACE BIOSYSTEMS', font('anton', 36), CORP_INK)
    text(M, (102, 72), 'INTERNAL MEMORANDUM  //  NOT FOR DISTRIBUTION', font('mono', 15), INK)
    rect(M, [24, 100, 590, 104], fill=(60, 200, 90, 255))
    for i, (k, v) in enumerate((('TO:', 'BIOSAFETY DIVISION'), ('FROM:', 'SECURITY OPS (M. OKAFOR)'), ('RE:', 'DISPOSAL OF CELL-03 (REBEL_CELL)'))):
        typed(M, 24, 118 + i * 28, k, v, kw=80, size=18)
    line(M, [(24, 210), (590, 210)], INK, 2)
    text(M, (24, 222), 'CAMPAIGN SUMMARY', font('courierb', 20), INK)
    summ = [('DAYS ACTIVE', '23'), ('SITES CLAIMED', '7'), ('SITES LOST', '4  (retaken)'), ('RUNNERS LOST', '2'),
            ('RAIDS HELD', '3'), ('RAIDS LOST', '4'), ('FINAL HEAT', '88'), ('HQ INTEGRITY', '0 / 20')]
    for i, (k, v) in enumerate(summ):
        yy = 252 + i * 32
        if i % 2 == 0:
            rect(M, [20, yy - 4, 594, yy + 28], fill=(200, 230, 206, 120))
        typed(M, 28, yy, k + ' ' + '.' * (16 - len(k)), v, vcol=RED if k in ('HQ INTEGRITY', 'RUNNERS LOST', 'SITES LOST', 'RAIDS LOST') else INK, kw=290, size=21)
    # Heat line
    gy = 712
    text(M, (24, gy), 'HEAT (subject\'s exposure), final 88:', font('courier', 18), INK)
    pts = [(40 + i * 54, gy + 130 - v * 1.0) for i, v in enumerate((6, 14, 22, 25, 33, 41, 48, 52, 61, 70, 79, 88))]
    for gv in (25, 50, 75):
        line(M, [(36, gy + 130 - gv * 1.0), (640, gy + 130 - gv * 1.0)], (180, 180, 180, 255), 1)
        text(M, (14, gy + 130 - gv * 1.0), str(gv), font('mono', 12), (120, 120, 120, 255), 'lm')
    line(M, pts, INK, 2)
    for i, p in enumerate(pts):
        ellipse(M, [p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=RED if i in (3, 6, 9) else INK)
    text(M, (24, gy + 150), 'no appeal is offered. your station is now a clean surface.', font('courier', 17), INK)
    text(M, (24, gy + 174), 'filed by: M. OKAFOR, SECURITY OPS 7', font('courier', 15), (100, 100, 100, 255))
    text(M, (440, gy + 160), 'M.Okafor', font('hand', 34), (30, 40, 140, 255))
    rotate_paste(img, M, (MX0 + MX1) / 2, (MY0 + MY1) / 2, .4, shadow=False)
    corp_ink_stamp_(img, 'TARGET ACQUIRED', MX0 + 300, MY0 + 612, rot=-6, size=58)
    postit(img, (MX1 - 120, MY0 + 150, MX1 + 50, MY0 + 290), (190, 240, 120, 255), 'HQ sealed.\nall strains\naccounted for.', rot=4, size=21, fg=(40, 60, 40, 255))
    postit(img, (FX0 + 430, FY1 - 128, FX0 + 640, FY1 - 6), (255, 230, 90, 255), 'they will be\nback. log the\nnext cell.', rot=-4, size=22)
    buttons(img, main_xy=(980, 1032), new_xy=(1200, 1030))
    # ---- variant panel: a runner lost on a netrun (T4 L5 trace printout)
    VX0 = 1380
    text(img, (VX0, 70), 'VARIANT  .  RUNNER LOST ON A NETRUN', font('mono', 18), AMB)
    text(img, (VX0, 94), 'T4 L5 trace printout (not the campaign end)', font('mono', 15), DIM)
    slip(img, VX0, 130, 500, 540, saved=False)
    slip(img, VX0 + 20, 700, 480, 320, saved=True)
    frame_caption(img, 'T11 campaign lost (HQ integrity 0): Solace dossier + run summary, MAIN MENU / NEW CAMPAIGN; variant: runner lost / SAFETY NET USED')
    return finish_save(img, 'loss_printout.png', vig=.3)


def corp_ink_stamp_(img, s, cx, cy, rot=-12, size=150):
    from raid_screens import corp_ink_stamp
    corp_ink_stamp(img, s, cx, cy, rot=rot, size=size)


def slip(img, x, y, w, h, saved=False):
    """trace printout slip (design C): tractor holes, Solace header, typed rows"""
    L = layer(w + 40, h + 40); o = 20
    rect(L, [o, o, o + w, o + h], fill=(236, 238, 230, 255))
    for yy in range(o + 16, o + h - 6, 26):
        ellipse(L, [o + 8, yy, o + 20, yy + 12], fill=(40, 40, 44, 255)); ellipse(L, [o + w - 20, yy, o + w - 8, yy + 12], fill=(40, 40, 44, 255))
    X = o + 36
    if not saved:
        ellipse(L, [X, o + 18, X + 40, o + 58], outline=CORP_INK, width=3)
        text(L, (X + 52, o + 18), 'SOLACE BIOSYSTEMS', font('anton', 26), INK)
        text(L, (X + 52, o + 50), 'SECURITY OPS // INTRUSION TRACE', font('mono', 13), INK)
    line(L, [(X, o + 76), (o + w - 36, o + 76)], INK, 2)
    if not saved:
        text(L, (X, o + 86), 'RUNNER LOST', font('anton', 46), INK)
        rows = [('RUNNER', 'NYX // FIXER LV2', INK), ('STATUS', 'FLATLINED, for good', RED), ('SITE', 'SEED VAULT EXCH. T2', INK),
                ('', '', INK), ('LOST WITH RUNNER', '', INK), ('DECK', '19 cards', RED), ('UNBANKED CR', '14', RED), ('RAID ASSETS', '1 unbanked', RED),
                ('', '', INK), ('HEAT', '+12 +2 (tier 2) = +14', HEATC)]
        yy = o + 156
        for k, v, c in rows:
            if k == 'LOST WITH RUNNER':
                text(L, (X, yy), k, font('courierb', 19), INK)
                line(L, [(X, yy + 24), (X + 260, yy + 24)], INK, 1)
            elif k:
                text(L, (X, yy), k + ' ' + '.' * (12 - len(k)), font('courier', 18), (70, 70, 70, 255))
                text(L, (X + 180, yy), v, font('courierb', 18), c)
            yy += 31 if k else 14
        text(L, (X, o + 440), 'banked credits and assets: safe at HQ', font('courier', 15), (90, 90, 90, 255))
    else:
        text(L, (X, o + 86), 'RUNNER EXTRACTED', font('anton', 36), INK)
        rows = [('RUNNER', 'NYX lives (to HQ)', (30, 130, 60, 255)), ('DECK', 'kept', (30, 130, 60, 255)),
                ('UNBANKED CR', '14 lost', RED), ('RAID ASSETS', '1 lost', RED), ('HEAT', '+12 +2 (tier 2)', HEATC), ('SAFETY NET', '1 > 0 left', INK)]
        yy = o + 142
        for k, v, c in rows:
            text(L, (X, yy), k + ' ' + '.' * (12 - len(k)), font('courier', 18), (70, 70, 70, 255))
            text(L, (X + 180, yy), v, font('courierb', 18), c)
            yy += 28
    rotate_paste(img, L, x + w / 2, y + h / 2, -1 if not saved else 1.2, sh=(6, 10, 14, 150))
    if not saved:
        stamp(img, 'TRACE BURNED', x + w - 150, y + 500, RED, rot=-10, size=34)
        sticker(img, 'GRID VIEW', x + 120, y + h + 6, 190, 50, PINK, None, rot=-2, size=30)
    else:
        stamp(img, 'SAFETY NET USED', x + w / 2 + 10, y + 50, (30, 130, 60, 255), rot=-4, size=34)
        text(img, (x + 40, y + h + 26), 'same footer: GRID VIEW', font('mono', 15), DIM)


# ================================================================== stop banner spec crop
def plate_stop():
    import raid_world as RW
    img = Image.new('RGBA', (W * K, H * K), (12, 13, 20, 255))
    text(img, (40, 26), 'STOP BANNER', font('anton', 64), LIME)
    text(img, (440, 52), 'raid top centre . 1:1 . as on raid_a..e . Solace only', font('mono', 22), DIM)
    states = [('STOP REACHED', 'fighting stop 1; the next stops wait', [('D4', 'cur'), ('A3', 'next'), ('HQ', 'end')], 0, 'raid_a, b, c'),
              ('HELD', 'the stop held: the raid ends here', [('D4', 'held'), ('A3', 'next'), ('HQ', 'end')], 0, 'raid_f_result_held'),
              ('FELL', 'stop 1 fell; the raid walks on to stop 2', [('D4', 'fell'), ('A3', 'cur'), ('HQ', 'end')], 1, 'raid_d_site_falls'),
              ('HQ STOP', 'both stops fell; the fight is at our HQ', [('D4', 'fell'), ('A3', 'fell'), ('HQ', 'cur')], 2, 'raid_e_hq_stop')]
    b = RW.base()
    for i, (ttl, sub, stops, cur, where) in enumerate(states):
        y = 130 + i * 150
        bb = b.copy()
        RW.stop_banner(bb, stops, cur)                       # drawn where it lives (x 700, y 18) on the city, then cropped 1:1
        piece = bb.crop(tuple(S([660, 0, 1300, 104])))
        img.alpha_composite(piece, (S(560), S(y)))
        rect(img, [560, y, 1200, y + 104], outline=GREY, width=2)
        text(img, (40, y + 18), ttl, font('anton', 40), WHITE)
        text(img, (40, y + 70), sub, font('plex', 20), DIM)
        text(img, (1230, y + 30), 'seen on', font('mono', 16), DIM)
        text(img, (1230, y + 54), where, font('mono', 20), CYAN)
    # chip anatomy
    y = 760
    text(img, (40, y), 'CHIPS', font('anton', 40), WHITE)
    f = font('anton', 30)
    items = [('cur', 'D4', 'current stop', RED, WHITE, WHITE), ('next', 'A3', 'not yet', INK, WHITE, WHITE), ('end', 'HQ', 'END: our HQ', INK, PINK, WHITE),
             ('fell', 'D4', 'fell: grey, struck red', (60, 60, 72, 255), GREY, GREY), ('held', 'D4', 'held: lime', LIME, INK, INK)]
    for k, (st, lab, desc, fill, edge, fg) in enumerate(items):
        x = 40 + k * 300
        wl = tw(lab, f) + 26
        rrect(img, [x, y + 70, x + wl, y + 112], 8, fill=fill, outline=edge, width=3)
        text(img, (x + wl / 2, y + 91), lab, f, fg, 'mm')
        if st == 'fell':
            line(img, [(x + 4, y + 108), (x + wl - 4, y + 74)], RED, 5)
        text(img, (x + wl + 14, y + 91), st, font('mono', 20), WHITE, 'lm')
        text(img, (x, y + 136), desc, font('plex', 19), DIM)
    text(img, (40, y + 196), 'STOP n/3 counts the stop being fought (cyan). The chips follow the route on the corp order: TARGET > THEN > END (our HQ).',
         font('plex', 20), DIM)
    text(img, (40, y + 226), 'Glass: navy, cyan edge, 580 x 66 at 1080p, top centre; never covers the HUD tape (left) or the corp order (right).',
         font('plex', 20), DIM)
    frame_caption(img, 'raid stop banner spec crop: STOP REACHED / HELD / FELL / HQ STOP at 1:1, plus the chip states')
    img = vignette(img, .2)
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(OUT + 'stop_banner.png')
    print('wrote stop_banner.png')


PLATES = dict(a=plate_a, b=plate_b, c=plate_c, d_mid=lambda: plate_d(False), d_final=lambda: plate_d(True), loss=plate_loss, stop=plate_stop)

if __name__ == '__main__':
    for k in (sys.argv[1:] or list(PLATES)):
        PLATES[k]()
