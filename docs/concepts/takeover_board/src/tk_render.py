"""tk_render: the Campaign B Takeover fight board in the locked combat family (ART CALL 53), concept plates for build's B-086.

    python tk_render.py [state ...]     states: board play forecast resolve wallseal win   (default: board)

Layout = the prototype's own fight screen (Rebel Cell Campaign B v36): the 12-segment wheel on the left, the HUD on the right,
the hand under the HUD.  Style = the locked family's three layers:
  * runner (player) = punk print: bone paper, linocut black key line with a block drop, pink scissor-cut halo, misregistered ink;
  * corp = enamel: slate glass cells, one hairline, the Solace teal glaze on rim, lip and cell edges; the clock (pointers, plan) in gunmetal;
  * system = cyan terminal glass: the HUD, the RAM coins, the exact END TURN forecast.
Tokens come from the locked rb_tokens; cards from the locked card_render.  Pure PIL / numpy, one process, no Godot.
"""
import math, os, sys
sys.dont_write_bytecode = True
LOCKED = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, LOCKED)
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import rb_tokens as T
import card_render as CR
from tk_states import STATES, TYPE_WORD

# card plate words for the Takeover hand: the prototype's card archetype.  Colour = the locked pair, teal for a card you aim at a
# segment, lilac for a card you do not aim (OPEN for the designer: the Takeover card types are not settled)
for _w in ('FIRE', 'VIRUS', 'BLOCK', 'DELAY'):
    CR.TYPES[_w] = CR.TYPES['TOWER']
CR.TYPES['CONTROL'] = CR.TYPES['WAVE']

OUT = 'D:/rc_art/art-pass/docs/concepts/takeover_board/'
ROOM = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/tr/room_bio_graded.png'
SS = 2                                   # supersampling
W, H = 1920, 1080
FONT = LOCKED + '/fonts/'
ANTON, PLEX, MONO = FONT + 'Anton-Regular.ttf', FONT + 'IBMPlexSansCondensed-Medium.ttf', FONT + 'ShareTechMono-Regular.ttf'

# ---------------------------------------------------------------- colours (locked tokens; local names say the layer)
TK = T.TOKENS
INK = (21, 18, 26); PAPER = T.NEUTRALS['PAPER']; ENAMEL = T.NEUTRALS['ENAMEL']; K_TYPE = T.K_TYPE
PINK = TK['CELL_PINK']; PINK_D = (194, 26, 124)
HARM = TK['HARM']; HARM_UP = T.HARM_UP; HOT_CORE = T.HOT_CORE; COLD = T.COLD_CHEV
GAIN = TK['GAIN']; PLAN = TK['PLAN']; FOCUS = TK['FOCUS']; SCHED = TK['SCHEDULE']; CYAN = TK['NET_CYAN']; TRACE = TK['TRACE_VIOLET']
SOL = T.SKIN_INKS['solace']; TEAL, TEAL_D, TEAL_HI, GLAZE = SOL['teal'], SOL['teal_deep'], SOL['teal_hi'], SOL['porcelain']
CLOCK, CLOCK_LT, CLOCK_GR = (110, 117, 128), (150, 158, 170), (40, 44, 52)
SLATE = (58, 66, 78); SLATE_LO = (40, 46, 56)
GLASS = (9, 22, 30); TEXT_HI = T.NEUTRALS['TEXT_HI']; TEXT_MID = T.NEUTRALS['TEXT_MID']

# ---------------------------------------------------------------- wheel geometry (1x px)
CX, CY = 540, 548
R_HUB, R_CHIP, R_IN, R_OUT, R_RIM = 112, 146, 176, 368, 396
N = 12


def S(v):
    return int(round(v * SS))


def font(path, px):
    return ImageFont.truetype(path, S(px))


def ang(k):
    return math.radians(-90 + 30 * k)


def pol(r, a, cx=CX, cy=CY):
    return (S(cx + r * math.cos(a)), S(cy + r * math.sin(a)))


def wedge(r0, r1, a0, a1, n=24):
    pts = [pol(r1, a0 + (a1 - a0) * t / n) for t in range(n + 1)]
    pts += [pol(r0, a1 - (a1 - a0) * t / n) for t in range(n + 1)]
    return pts


def arc_pts(r, a0, a1, n=24):
    return [pol(r, a0 + (a1 - a0) * t / n) for t in range(n + 1)]


class Layer:
    """an RGBA layer at SS scale with a draw handle"""
    def __init__(self):
        self.im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)


def comp(base, lay):
    base.alpha_composite(lay.im)


def text(d, xy, s, f, fill, anchor='mm', stroke=0, sfill=None):
    d.text((S(xy[0]), S(xy[1])), s, font=f, fill=fill, anchor=anchor, stroke_width=S(stroke), stroke_fill=sfill)


def ink_key(lay_im, mask, key=3.0, drop=(4, 5), col=INK):
    """linocut key line + hard block drop under a mask (L image at SS)"""
    k = mask.filter(ImageFilter.MaxFilter(S(key) * 2 + 1))
    dr = Image.new('L', mask.size, 0); dr.paste(k, (S(drop[0]), S(drop[1])))
    for m in (dr, k):
        lay_im.paste(Image.new('RGBA', mask.size, col + (255,)), (0, 0), m)


# ---------------------------------------------------------------- the eight segment types as vector glyphs (unit box, centre 0,0, size 1)
def glyph(d, kind, cx, cy, s, fill, w):
    P = lambda x, y: (S(cx + x * s), S(cy + y * s))
    lw = max(1, S(w))
    if kind == 'CACHE':          # a coin stack
        for j in range(3):
            y = 0.28 - j * 0.24
            d.ellipse([P(-0.42, y - 0.12), P(0.42, y + 0.12)], outline=fill, width=lw)
    elif kind == 'CORE':         # a cut diamond
        d.polygon([P(0, -0.5), P(0.42, 0), P(0, 0.5), P(-0.42, 0)], outline=fill, width=lw)
        d.line([P(-0.42, 0), P(0.42, 0)], fill=fill, width=lw)
    elif kind == 'FIREWALL':     # a brick wall
        d.rectangle([P(-0.46, -0.36), P(0.46, 0.36)], outline=fill, width=lw)
        d.line([P(-0.46, 0), P(0.46, 0)], fill=fill, width=lw)
        for x in (-0.14, 0.2):
            d.line([P(x, -0.36), P(x, 0)], fill=fill, width=lw)
        d.line([P(0.02, 0), P(0.02, 0.36)], fill=fill, width=lw)
    elif kind == 'ICE':          # a crystal
        for a in (0, 60, 120):
            r = math.radians(a)
            d.line([P(-0.48 * math.cos(r), -0.48 * math.sin(r)), P(0.48 * math.cos(r), 0.48 * math.sin(r))], fill=fill, width=lw)
    elif kind == 'NODE':         # a node and three links
        for a in (-90, 30, 150):
            r = math.radians(a)
            d.line([P(0, 0), P(0.44 * math.cos(r), 0.44 * math.sin(r))], fill=fill, width=lw)
            d.ellipse([P(0.44 * math.cos(r) - 0.09, 0.44 * math.sin(r) - 0.09), P(0.44 * math.cos(r) + 0.09, 0.44 * math.sin(r) + 0.09)], fill=fill)
        d.ellipse([P(-0.16, -0.16), P(0.16, 0.16)], fill=fill)
    elif kind == 'RELAY':        # two opposed arrows
        d.line([P(-0.46, -0.16), P(0.4, -0.16)], fill=fill, width=lw); d.polygon([P(0.46, -0.16), P(0.24, -0.32), P(0.24, 0.0)], fill=fill)
        d.line([P(0.46, 0.18), P(-0.4, 0.18)], fill=fill, width=lw); d.polygon([P(-0.46, 0.18), P(-0.24, 0.02), P(-0.24, 0.34)], fill=fill)
    elif kind == 'SPAWNER':      # a pod with a plus
        d.ellipse([P(-0.36, -0.46), P(0.36, 0.46)], outline=fill, width=lw)
        d.line([P(0, -0.2), P(0, 0.2)], fill=fill, width=lw); d.line([P(-0.2, 0), P(0.2, 0)], fill=fill, width=lw)
    elif kind == 'TURRET':       # a crosshair
        d.ellipse([P(-0.34, -0.34), P(0.34, 0.34)], outline=fill, width=lw)
        for a, b in (((0, -0.5), (0, -0.16)), ((0, 0.5), (0, 0.16)), ((-0.5, 0), (-0.16, 0)), ((0.5, 0), (0.16, 0))):
            d.line([P(*a), P(*b)], fill=fill, width=lw)


# ---------------------------------------------------------------- backdrop
def backdrop():
    room = Image.open(ROOM).convert('RGB').resize((W * SS, H * SS), Image.LANCZOS)
    a = np.asarray(room).astype(np.float32)
    yy, xx = np.mgrid[0:H * SS, 0:W * SS].astype(np.float32) / SS
    rr = np.hypot(xx - CX, yy - CY)
    scrim = np.clip((rr - 300) / 260, 0, 1) * 0.35 + 0.42          # the wheel sits in a dark pool; the room reads at the edges
    a *= scrim[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')


# ---------------------------------------------------------------- the wheel
def seg_angles(i, rot):
    k = (i + rot) % N
    am = ang(k)
    return am - math.radians(15) + 0.012, am + math.radians(15) - 0.012, am


def draw_rim(img, st):
    """the corp's rim: Solace teal glaze rope (corp material), gunmetal groove inside it"""
    L = Layer(); d = L.d
    d.ellipse([pol(R_RIM + 18, math.pi, CX, CY)[0], S(CY - R_RIM - 18), S(CX + R_RIM + 18), S(CY + R_RIM + 18)], fill=TEAL_D + (255,))
    n = 52
    for j in range(n):
        a0 = 2 * math.pi * j / n; a1 = a0 + 2 * math.pi / n * 0.62
        d.polygon([pol(R_RIM + 15, a0), pol(R_RIM + 15, a1), pol(R_RIM + 2, a1 + 0.05), pol(R_RIM + 2, a0 + 0.05)], fill=TEAL + (255,))
        d.line([pol(R_RIM + 14, a0 + 0.01), pol(R_RIM + 4, a0 + 0.06)], fill=TEAL_HI + (255,), width=S(1.5))
    d.ellipse([S(CX - R_RIM), S(CY - R_RIM), S(CX + R_RIM), S(CY + R_RIM)], fill=CLOCK_GR + (255,))
    d.ellipse([S(CX - R_OUT - 6), S(CY - R_OUT - 6), S(CX + R_OUT + 6), S(CY + R_OUT + 6)], fill=SLATE_LO + (255,))
    d.ellipse([S(CX - R_RIM - 18), S(CY - R_RIM - 18), S(CX + R_RIM + 18), S(CY + R_RIM + 18)], outline=INK + (255,), width=S(2))
    comp(img, L)


def draw_corp_seg(L, g, a0, a1, am):
    d = L.d
    d.polygon(wedge(R_IN, R_OUT, a0, a1), fill=SLATE + (255,))
    # enamel gloss: a lighter band on the outer third
    d.polygon(wedge(R_OUT - 58, R_OUT - 6, a0 + 0.02, a1 - 0.02), fill=(70, 80, 94, 255))
    d.line(arc_pts(R_OUT - 5, a0 + 0.02, a1 - 0.02), fill=TEAL + (255,), width=S(2))          # the corp hue on the cell edge only
    d.line(arc_pts(R_IN + 4, a0 + 0.02, a1 - 0.02), fill=TEAL_D + (255,), width=S(1.5))
    for a in (a0, a1):
        d.line([pol(R_IN + 2, a), pol(R_OUT - 2, a)], fill=(28, 32, 40, 255), width=S(3))


def punk_mask(a0, a1):
    m = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(m).polygon(wedge(R_IN + 3, R_OUT - 3, a0 + 0.012, a1 - 0.012), fill=255)
    return m


def draw_runner_segs(img, segs, rot):
    """the runner's segments: bone paper, pink Ben-Day, black linocut key with a block drop, pink scissor-cut halo"""
    mine = [i for i, g in enumerate(segs) if g['owner'] == 'us']
    if not mine:
        return
    M = Image.new('L', (W * SS, H * SS), 0)
    for i in mine:
        a0, a1, am = seg_angles(i, rot)
        M.paste(255, (0, 0), punk_mask(a0, a1))
    halo = M.filter(ImageFilter.MaxFilter(S(5) * 2 + 1))
    # scissor-cut: jag the halo edge with a fixed noise
    rng = np.random.default_rng(7)
    nz = Image.fromarray((rng.random((H * SS // 6 + 1, W * SS // 6 + 1)) * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.NEAREST)
    halo2 = Image.fromarray(np.where(np.asarray(nz) > 110, np.asarray(halo), np.asarray(M.filter(ImageFilter.MaxFilter(S(3) * 2 + 1)))).astype(np.uint8))
    L = Layer()
    L.im.paste(Image.new('RGBA', M.size, PINK + (255,)), (0, 0), halo2)
    ink_key(L.im, M, key=2.6, drop=(3, 4))
    paper = Image.new('RGBA', M.size, PAPER + (255,))
    L.im.paste(paper, (0, 0), M)
    # pink Ben-Day dots inside the paper (the player's print), coverage 14 %
    dots = Image.new('L', M.size, 0); dd = ImageDraw.Draw(dots)
    p = S(9)
    for y in range(0, H * SS, p):
        for x in range((y // p % 2) * p // 2, W * SS, p):
            dd.ellipse([x - S(1.9), y - S(1.9), x + S(1.9), y + S(1.9)], fill=255)
    dots = Image.fromarray(np.minimum(np.asarray(dots), np.asarray(M.filter(ImageFilter.MinFilter(S(6) * 2 + 1)))))
    L.im.paste(Image.new('RGBA', M.size, (248, 170, 210, 255)), (0, 0), dots)
    comp(img, L)


def draw_segment_marks(img, st, f_type, f_num, f_small):
    """type glyph, type word and integrity on every segment; statuses; armed HOT arcs"""
    L = Layer(); d = L.d
    for i, g in enumerate(st['segs']):
        a0, a1, am = seg_angles(i, st['rot'])
        us = g['owner'] == 'us'
        # one upright label group per segment (glyph, integrity, type word), centred at r 276, so side segments never overlap
        ox, oy = CX + 276 * math.cos(am), CY + 276 * math.sin(am)
        gx, gy = ox, oy - 44
        nx, ny = ox, oy + 2
        wx, wy = ox, oy + 42
        if us:
            # misregistered pink glyph under the ink glyph
            glyph(d, g['type'], gx + 2.5, gy + 2.5, 34, PINK + (255,), 4.0)
            glyph(d, g['type'], gx, gy, 34, INK + (255,), 4.0)
            text(d, (wx, wy), TYPE_WORD[g['type']], f_small, INK + (255,))
            text(d, (nx, ny), str(g['hp']), f_num, INK + (255,))
        else:
            glyph(d, g['type'], gx, gy, 34, K_TYPE + (255,), 3.2)
            text(d, (wx, wy), TYPE_WORD[g['type']], f_small, TEXT_MID + (255,))
            text(d, (nx, ny), str(g['hp']), f_num, K_TYPE + (255,))
        # statuses: small stamped tags on the inner edge (pink keyline = the runner put it there, teal = the corp's own)
        for j, (word, side) in enumerate(g.get('st', [])):
            tx, ty = CX + (R_IN + 22) * math.cos(am + (j - (len(g['st']) - 1) / 2) * 0.17), CY + (R_IN + 22) * math.sin(am + (j - (len(g['st']) - 1) / 2) * 0.17)
            bb = d.textbbox((S(tx), S(ty)), word, font=f_small, anchor='mm')
            pad = S(4)
            d.rounded_rectangle([bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad], radius=S(3), fill=INK + (255,), outline=(PINK if side == 'runner' else TEAL) + (255,), width=S(2))
            text(d, (tx, ty), word, f_small, (PAPER if side == 'runner' else K_TYPE) + (255,))
        if g.get('armed') and not us:            # HOT: this END TURN the pointer arms this type; a white-hot core carries it
            d.line(arc_pts(R_OUT - 12, a0 + 0.06, a1 - 0.06), fill=HARM_UP + (255,), width=S(9))
            d.line(arc_pts(R_OUT - 12, a0 + 0.08, a1 - 0.08), fill=HOT_CORE + (255,), width=S(3))
    comp(img, L)


def draw_hub(img, st, f_big, f_mid, f_small):
    """the corp's spin: gunmetal clock disc with the Solace lip; this END TURN's spin and the next three"""
    L = Layer(); d = L.d
    d.ellipse([S(CX - R_HUB - 8), S(CY - R_HUB - 8), S(CX + R_HUB + 8), S(CY + R_HUB + 8)], fill=TEAL + (255,))
    d.ellipse([S(CX - R_HUB), S(CY - R_HUB), S(CX + R_HUB), S(CY + R_HUB)], fill=CLOCK_GR + (255,))
    d.ellipse([S(CX - R_HUB + 10), S(CY - R_HUB + 10), S(CX + R_HUB - 10), S(CY + R_HUB - 10)], fill=CLOCK + (255,))
    d.ellipse([S(CX - R_HUB + 14), S(CY - R_HUB + 14), S(CX + R_HUB - 14), S(CY + R_HUB - 14)], fill=(52, 58, 68, 255))
    hub = st.get('hub')
    if hub:
        text(d, (CX, CY - 46), hub['top'], f_small, K_TYPE + (255,))
        text(d, (CX, CY + 2), hub['big'], f_big, hub.get('col', SCHED) + (255,))
        text(d, (CX, CY + 54), hub['bot'], f_small, TEXT_MID + (255,))
    # the spin arrow round the big number (clock motion = SCHEDULE)
    if hub and hub.get('arrow'):
        sgn = hub['arrow']
        a0, a1 = math.radians(-150), math.radians(-30)
        pts = arc_pts(R_HUB - 30, a0, a1)
        d.line(pts, fill=SCHED + (255,), width=S(5))
        tip = pts[-1] if sgn > 0 else pts[0]
        ta = a1 if sgn > 0 else a0
        dirn = 1 if sgn > 0 else -1
        bx, by = tip
        t1 = (bx + S(12) * math.cos(ta + dirn * math.pi / 2), by + S(12) * math.sin(ta + dirn * math.pi / 2))
        d.polygon([(bx + S(9) * math.cos(ta), by + S(9) * math.sin(ta)), (bx - S(9) * math.cos(ta), by - S(9) * math.sin(ta)), t1], fill=SCHED + (255,))
    comp(img, L)


def draw_chips(img, st, f):
    """the exact forecast on the wheel (system layer): integrity after END TURN in cyan glass chips; teal fill = becomes yours,
    red fill = lost; a SCHEDULE ring = this segment fires at END TURN"""
    fc = st.get('chips')
    if not fc:
        return
    L = Layer(); d = L.d
    for i, c in enumerate(fc):
        a0, a1, am = seg_angles(i, st['rot'])
        x, y = CX + R_CHIP * math.cos(am), CY + R_CHIP * math.sin(am)
        fill = {'take': (16, 70, 66), 'lose': (92, 20, 30)}.get(c.get('k'), GLASS)
        edge = SCHED if c.get('fires') else {'take': GAIN, 'lose': HARM}.get(c.get('k'), (70, 120, 140))
        r = 15
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=fill + (235,), outline=edge + (255,), width=S(3 if c.get('fires') else 2))
        text(d, (x, y + 1), str(c['hp']), f, (TEXT_HI if c.get('k') else CYAN) + (255,))
    comp(img, L)


def draw_pointers(img, st):
    """the corp's pointers: gunmetal clock blades outside the rim; a firing pointer takes the SCHEDULE edge"""
    L = Layer(); d = L.d
    for p in st['ptrs']:
        a = ang(p)
        fire = p in st.get('firing', [])
        tip = R_RIM + 10; back = R_RIM + 62
        pts = [pol(tip, a), pol(back, a - 0.075), pol(back + 8, a), pol(back, a + 0.075)]
        if fire:
            glow = [pol(tip - 6, a), pol(back + 6, a - 0.1), pol(back + 16, a), pol(back + 6, a + 0.1)]
            d.polygon(glow, fill=SCHED + (255,))
        d.polygon([(x + S(3), y + S(4)) for x, y in pts], fill=INK + (255,))
        d.polygon(pts, fill=CLOCK + (255,), outline=INK + (255,))
        d.line([pol(tip + 4, a), pol(back - 2, a)], fill=CLOCK_LT + (255,), width=S(3))
        c = pol(back - 12, a)
        d.ellipse([c[0] - S(5), c[1] - S(5), c[0] + S(5), c[1] + S(5)], fill=CLOCK_GR + (255,), outline=CLOCK_LT + (255,), width=S(1))
    comp(img, L)


def draw_walls_seals(img, st, f_small):
    """walls are physical pieces on a boundary, seals are lids on a segment, for both sides:
    corp = enamel steel with the teal edge; runner = punk print plank / tape with the black key and pink halo"""
    L = Layer(); d = L.d
    for b, side in st.get('walls', []):          # boundary b = between segment b and b+1
        a = seg_angles(b, st['rot'])[1] + 0.012
        r0, r1 = R_IN - 14, R_RIM + 6
        if side == 'corp':
            pts = [pol(r0, a - 0.035), pol(r1, a - 0.018), pol(r1, a + 0.018), pol(r0, a + 0.035)]
            d.polygon([(x + S(3), y + S(4)) for x, y in pts], fill=INK + (255,))
            d.polygon(pts, fill=(150, 160, 172, 255), outline=TEAL + (255,), width=S(2))
            for r in range(int(r0) + 24, int(r1), 40):
                c = pol(r, a)
                d.ellipse([c[0] - S(3), c[1] - S(3), c[0] + S(3), c[1] + S(3)], fill=CLOCK_GR + (255,))
        else:
            pts = [pol(r0, a - 0.04), pol(r1, a - 0.022), pol(r1, a + 0.022), pol(r0, a + 0.04)]
            d.polygon([(x + S(4), y + S(5)) for x, y in pts], fill=INK + (255,))
            d.polygon([pol(r0 - 3, a - 0.05), pol(r1 + 3, a - 0.03), pol(r1 + 3, a + 0.03), pol(r0 - 3, a + 0.05)], fill=PINK + (255,))
            d.polygon(pts, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
            for r in range(int(r0) + 14, int(r1) - 6, 22):
                d.line([pol(r, a - 0.02), pol(r + 10, a + 0.02)], fill=PINK_D + (255,), width=S(3))
    for i, side in st.get('seals', []):
        a0, a1, am = seg_angles(i, st['rot'])
        x, y = CX + 196 * math.cos(am), CY + 196 * math.sin(am)
        if side == 'corp':
            d.polygon(wedge(R_IN + 6, R_OUT - 6, a0 + 0.05, a1 - 0.05), outline=GLAZE + (255,), width=S(4))
            d.rounded_rectangle([S(x - 30), S(y - 13), S(x + 30), S(y + 13)], radius=S(4), fill=GLAZE + (255,), outline=TEAL_D + (255,), width=S(2))
            text(d, (x, y + 1), 'SEALED', f_small, INK + (255,))
        else:
            # the runner's seal: a strip of pink tape across the segment's outer edge, black key, stencil word
            d.line(arc_pts(R_OUT - 20, a0 + 0.03, a1 - 0.03), fill=INK + (255,), width=S(30))
            d.line(arc_pts(R_OUT - 20, a0 + 0.04, a1 - 0.04), fill=PINK + (255,), width=S(24))
            sx, sy = CX + (R_OUT - 20) * math.cos(am), CY + (R_OUT - 20) * math.sin(am)
            text(d, (sx, sy + 1), 'SEAL', f_small, INK + (255,))
    comp(img, L)


def draw_overlays(img, st, f_tag, f_small):
    """per-state marks: FOCUS corners on legal targets, PLAN pencil on the aimed take, HARM -HP tags on forecast retakes,
    resolve arrows (corp = HARM, runner = PINK) and the retake burst"""
    L = Layer(); d = L.d
    for i in st.get('focus', []):
        a0, a1, am = seg_angles(i, st['rot'])
        aimed = i == st.get('aim')
        w = S(3.5 if aimed else 2.2)
        for r, sgn in ((R_IN + 6, 1), (R_OUT - 6, -1)):
            for a, da in ((a0 + 0.03, 1), (a1 - 0.03, -1)):
                p = pol(r, a)
                d.line([p, pol(r + sgn * 13, a)], fill=FOCUS + (255,), width=w)
                d.line([p, pol(r, a + da * 13 / r)], fill=FOCUS + (255,), width=w)
    if st.get('aim') is not None and st.get('pencil'):
        a0, a1, am = seg_angles(st['aim'], st['rot'])
        for k in range(2):        # the grease pencil: wax line with an ink edge, drawn twice, slightly off
            off = 0.004 * k
            d.line(arc_pts(R_OUT + 2, a0 + 0.05 + off, a1 - 0.05 + off), fill=INK + (255,), width=S(13))
            d.line(arc_pts(R_OUT + 2, a0 + 0.05 + off, a1 - 0.05 + off), fill=PLAN + (255,), width=S(7))
        x, y = CX + (R_RIM + 34) * math.cos(am + 0.2), CY + (R_RIM + 34) * math.sin(am + 0.2)
        text(d, (x, y), st['pencil'], f_tag, PLAN + (255,), stroke=3, sfill=INK + (255,))
    for i in st.get('retake_tags', []):
        a0, a1, am = seg_angles(i, st['rot'])
        x, y = CX + (R_RIM + 40) * math.cos(am - 0.13), CY + (R_RIM + 40) * math.sin(am - 0.13)
        bb = d.textbbox((S(x), S(y)), '\u22121 HP', font=f_tag, anchor='mm')
        d.rounded_rectangle([bb[0] - S(7), bb[1] - S(5), bb[2] + S(7), bb[3] + S(5)], radius=S(4), fill=HARM + (255,), outline=INK + (255,), width=S(2))
        text(d, (x, y), '\u22121 HP', f_tag, INK + (255,))
    for (i, j, side) in st.get('arrows', []):        # i = from (pointer index or segment), j = to segment
        a_from = ang(i) if side == 'ptr' else seg_angles(i, st['rot'])[2]
        a_to = seg_angles(j, st['rot'])[2]
        r_from = R_RIM + 8 if side == 'ptr' else 300
        col = HARM if side in ('corp', 'ptr') else PINK
        p0 = pol(r_from, a_from); p1 = pol(300, a_to)
        mid = pol(220, (a_from + a_to) / 2)
        pts = [tuple(np.array(p0) * (1 - t) ** 2 + np.array(mid) * 2 * t * (1 - t) + np.array(p1) * t * t) for t in np.linspace(0, 1, 24)]
        d.line(pts, fill=INK + (255,), width=S(9)); d.line(pts, fill=col + (255,), width=S(5))
        v = np.array(pts[-1]) - np.array(pts[-3]); v = v / (np.linalg.norm(v) + 1e-6); nrm = np.array([-v[1], v[0]])
        tip = np.array(pts[-1]) + v * S(6)
        d.polygon([tuple(tip), tuple(tip - v * S(20) + nrm * S(11)), tuple(tip - v * S(20) - nrm * S(11))], fill=col + (255,), outline=INK + (255,))
    for i in st.get('burst', []):                  # the retake: a HARM star burst on the segment the corp takes back
        a0, a1, am = seg_angles(i, st['rot'])
        x, y = CX + 282 * math.cos(am), CY + 282 * math.sin(am)
        pts = []
        for k in range(16):
            r = 62 if k % 2 == 0 else 30
            pts.append((S(x + r * math.cos(k * math.pi / 8 + 0.2)), S(y + r * math.sin(k * math.pi / 8 + 0.2))))
        d.polygon([(px + S(4), py + S(5)) for px, py in pts], fill=INK + (255,))
        d.polygon(pts, fill=HARM + (255,), outline=INK + (255,), width=S(3))
        text(d, (x, y), 'RETAKE', f_small, HOT_CORE + (255,), stroke=2, sfill=INK + (255,))
    comp(img, L)


# ---------------------------------------------------------------- HUD (system layer: cyan terminal glass)
HX0, HX1 = 1046, 1900


def glass(d, box, edge=CYAN, alpha=226, w=2):
    x0, y0, x1, y1 = box
    d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=GLASS + (alpha,))
    d.rectangle([S(x0), S(y0), S(x1), S(y1)], outline=edge + (255,), width=S(w))
    c = 14
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(S(x), S(y + dy * c)), (S(x), S(y)), (S(x + dx * c), S(y))], fill=CYAN + (255,), width=S(4))


def draw_hud(img, st, F):
    L = Layer(); d = L.d
    h = st['hud']
    # 1. the fight header: site, wheel kind, its rule (one line)
    glass(d, (HX0, 20, HX1, 112))
    text(d, (HX0 + 22, 50), h['title'], F['h1'], TEXT_HI + (255,), anchor='lm')
    text(d, (HX1 - 22, 50), h['kind'], F['h1'], TEAL_HI + (255,), anchor='rm')
    text(d, (HX0 + 22, 88), h['rule'], F['body'], TEXT_MID + (255,), anchor='lm')
    # 2. the run row: OWNED, ENERGY (RAM coins), TURN, escalation
    glass(d, (HX0, 124, HX1, 222))
    text(d, (HX0 + 22, 152), 'OWNED', F['lab'], TEXT_MID + (255,), anchor='lm')
    text(d, (HX0 + 22, 190), '%d/12' % sum(1 for g in st['segs'] if g['owner'] == 'us'), F['num'], TEXT_HI + (255,), anchor='lm')
    if h.get('owned_after') is not None:
        text(d, (HX0 + 132, 192), '\u2192 %d' % h['owned_after'], F['mid'], (GAIN if h['owned_after'] >= sum(1 for g in st['segs'] if g['owner'] == 'us') else HARM) + (255,), anchor='lm')
    text(d, (HX0 + 250, 152), 'ENERGY', F['lab'], TEXT_MID + (255,), anchor='lm')
    en, emax = h['energy']
    for k in range(emax):
        x = HX0 + 266 + k * 40; y = 192
        if k < en:
            d.ellipse([S(x - 15), S(y - 15), S(x + 15), S(y + 15)], fill=(26, 143, 184, 255), outline=CYAN + (255,), width=S(3))
            d.ellipse([S(x - 7), S(y - 7), S(x + 7), S(y + 7)], outline=(190, 245, 255, 255), width=S(2))
        else:
            d.ellipse([S(x - 15), S(y - 15), S(x + 15), S(y + 15)], outline=(60, 110, 130, 255), width=S(2))
    text(d, (HX0 + 420, 152), 'TURN', F['lab'], TEXT_MID + (255,), anchor='lm')
    text(d, (HX0 + 420, 190), str(h['turn']), F['num'], TEXT_HI + (255,), anchor='lm')
    text(d, (HX0 + 520, 152), 'ESCALATION', F['lab'], TEXT_MID + (255,), anchor='lm')
    text(d, (HX0 + 520, 190), h['esc'], F['mid'], TEXT_HI + (255,), anchor='lm')
    # 3. the runner: the YOU strip, punk print taped onto the terminal (health pips; the forecast loss as the red loss hatch)
    yy = 236
    tape = [(S(HX0 + 4), S(yy)), (S(HX1 - 4), S(yy + 4)), (S(HX1 - 8), S(yy + 70)), (S(HX0), S(yy + 66))]
    d.polygon([(x + S(4), y + S(5)) for x, y in tape], fill=INK + (255,))
    d.polygon(tape, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
    text(d, (HX0 + 22, yy + 35), h['runner'], F['you'], INK + (255,), anchor='lm')
    hp, hpm = h['hp']; lose = h.get('hp_loss', 0)
    x0 = HX0 + 300; pw = 9.6
    for k in range(hpm):
        x = x0 + k * (pw + 3.0); box = [S(x), S(yy + 20), S(x + pw), S(yy + 52)]
        if k < hp - lose:
            d.rectangle(box, fill=GAIN + (255,), outline=INK + (255,), width=S(2))
        elif k < hp:
            d.rectangle(box, fill=PAPER + (255,), outline=INK + (255,), width=S(2))
            for t in range(-2, 4):
                d.line([(S(x + t * 6), S(yy + 52)), (S(x + t * 6 + 12), S(yy + 20))], fill=HARM + (255,), width=S(2.4))
            d.rectangle(box, outline=INK + (255,), width=S(2))
        else:
            d.rectangle(box, fill=(196, 190, 176, 255), outline=INK + (255,), width=S(2))
    hp_txt = '%d/%d' % (hp, hpm) if not lose else '%d \u2192 %d' % (hp, hp - lose)
    text(d, (HX1 - 22, yy + 35), hp_txt, F['you'], (INK if not lose else (200, 24, 30)) + (255,), anchor='rm')
    # 4. statuses (runner) and the corp plan strip (enamel tickets: this turn's step is live, the next steps step down in value)
    yy = 322
    glass(d, (HX0, yy, HX1, yy + 172))
    text(d, (HX0 + 22, yy + 26), 'CORP PLAN', F['lab'], TEXT_MID + (255,), anchor='lm')
    plan = h['plan']
    if not plan:
        text(d, (HX0 + 22, yy + 80), 'no plan: the fight is over', F['tick'], TEXT_MID + (255,), anchor='lm')
    tx = HX0 + 22; vals = (1.0, 0.72, 0.52)
    for k, (nm, sub) in enumerate(plan):
        tw = 262 if k == 0 else 254
        v = vals[k]
        body = tuple(int(c * v) for c in (196, 205, 214))
        edge = SCHED if k == 0 else tuple(int(c * v) for c in TEAL)
        box = [S(tx), S(yy + 46), S(tx + tw), S(yy + 116)]
        d.rectangle([box[0] + S(3), box[1] + S(4), box[2] + S(3), box[3] + S(4)], fill=INK + (255,))
        d.rectangle(box, fill=body + (255,), outline=edge + (255,), width=S(4 if k == 0 else 2))
        text(d, (tx + 14, yy + 66), ('NOW  ' if k == 0 else 'T+%d  ' % k) + nm, F['tick'], INK + (255,), anchor='lm')
        text(d, (tx + 14, yy + 97), sub, F['small'], (40, 46, 56, 255), anchor='lm')
        tx += tw + 14
    text(d, (HX0 + 22, yy + 146), 'STATUS', F['lab'], TEXT_MID + (255,), anchor='lm')
    sx = HX0 + 120
    for word, side in h.get('status', []):
        bb = d.textbbox((S(sx), S(yy + 146)), word, font=F['small'], anchor='lm')
        col = CYAN if side == 'buff' else (255, 181, 71)
        d.rounded_rectangle([bb[0] - S(8), bb[1] - S(6), bb[2] + S(8), bb[3] + S(6)], radius=S(11), outline=col + (255,), width=S(2))
        text(d, (sx, yy + 146), word, F['small'], col + (255,), anchor='lm')
        sx += (bb[2] - bb[0]) / SS + 30
    text(d, (HX1 - 22, yy + 146), 'DRAW %d \u00b7 DISCARD %d' % h['piles'], F['small'], TEXT_MID + (255,), anchor='rm')
    # 5. the exact END TURN forecast (always shown; itemised when END TURN is hovered)
    yy = 508
    fc = h['forecast']
    hh = 52 + 34 * (len(fc) - 1)
    glass(d, (HX0, yy, 1700, yy + hh), edge=CYAN if not h.get('fc_hot') else SCHED, w=2 if not h.get('fc_hot') else 4)
    for k, line in enumerate(fc):
        spans = line if isinstance(line, list) else [(line, TEXT_HI)]
        x = HX0 + 22
        f = F['fc1'] if k == 0 else F['fc2']
        for s_, col in spans:
            text(d, (x, yy + 27 + 34 * k), s_, f, col + (255,), anchor='lm')
            bb = d.textbbox((0, 0), s_, font=f)
            x += (bb[2] - bb[0]) / SS + 10
    comp(img, L)


# ---------------------------------------------------------------- hand and END TURN
HAND_X0, HAND_Y = 944, 790
CARD_W = 194                       # 1.10 x the 176 design width: the locked hand scale (rules cap >= 16 px)
STEP = 182


def draw_hand(img, st, F):
    hand = st['hand']
    m = CR.margin_px(CARD_W)
    order = list(range(len(hand)))
    lift = st.get('lift')
    if lift is not None:
        order.remove(lift); order.append(lift)
    for i in order:
        c = hand[i]
        spec = dict(name=c['base'], nm=c['nm'], txt=c['txt'], cost=c['cost'], fam=c['fam'], loud=0)
        if 'mult' not in c:
            spec['mult'] = ''
        x = HAND_X0 + i * STEP
        y = HAND_Y + (abs(i - 2) ** 1.6) * 3
        rot = (i - 2) * -1.2
        if i == lift:
            im = CR.draw_card(spec, round(CARD_W * 1.10), 'hover')
            y -= 92; rot = 0
            mm = CR.margin_px(round(CARD_W * 1.10))
        elif c.get('why'):
            im = CR.draw_card(spec, CARD_W, 'unaffordable')
            mm = m
        else:
            im = CR.draw_card(spec, CARD_W, dict(mode='normal', dim=0.92))
            mm = m
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        big = im.resize((im.width * SS, im.height * SS), Image.LANCZOS)
        L = Layer()
        L.im.alpha_composite(big, (S(x - mm), S(y - mm)))
        if c.get('why'):                        # an unusable card is red and says why
            d = L.d
            cw, ch = CARD_W, CARD_W * 250 / 176
            d.rectangle([S(x - 2), S(y - 2), S(x + cw + 2), S(y + ch + 2)], outline=HARM + (255,), width=S(5))
            bb = (x + 6, y + ch * 0.27, x + cw - 6, y + ch * 0.27 + 58)
            d.rectangle([S(bb[0]), S(bb[1]), S(bb[2]), S(bb[3])], fill=HARM + (255,), outline=INK + (255,), width=S(2))
            text(d, ((bb[0] + bb[2]) / 2, bb[1] + 17), 'CAN\'T PLAY', F['why1'], INK + (255,))
            text(d, ((bb[0] + bb[2]) / 2, bb[1] + 42), c['why'], F['why2'], INK + (255,))
        comp(img, L)


def draw_end_turn(img, st, F):
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 1716, 604, 1904, 740
    hot = st['hud'].get('fc_hot')
    pts = [(S(x0), S(y0 + 6)), (S(x1), S(y0)), (S(x1 - 4), S(y1)), (S(x0 + 4), S(y1 - 4))]
    d.polygon([(x + S(6), y + S(8)) for x, y in pts], fill=INK + (255,))
    d.polygon([(x + S(3 if hot else 0), y - S(3 if hot else 0)) for x, y in pts], fill=PINK + (255,), outline=INK + (255,), width=S(4))
    b1, b2 = st.get('btn', ('END', 'TURN'))
    if b2:
        text(d, ((x0 + x1) / 2, y0 + 44), b1, F['end'], (255, 255, 255, 255), stroke=2.4, sfill=INK + (255,))
        text(d, ((x0 + x1) / 2, y0 + 96), b2, F['end'], (255, 255, 255, 255), stroke=2.4, sfill=INK + (255,))
    else:
        text(d, ((x0 + x1) / 2, (y0 + y1) / 2), b1, F['mid'], (255, 255, 255, 255), stroke=2.0, sfill=INK + (255,))
    if st.get('btn'):
        comp(img, L)
        return
    # UNDO: the player's paper tab
    ux0, uy0, ux1, uy1 = 1736, 512, 1904, 560
    d.polygon([(S(ux0 + 3), S(uy0 + 4)), (S(ux1 + 3), S(uy0 + 2)), (S(ux1 + 3), S(uy1 + 4)), (S(ux0 + 3), S(uy1 + 4))], fill=INK + (255,))
    d.polygon([(S(ux0), S(uy0)), (S(ux1), S(uy0 - 2)), (S(ux1), S(uy1)), (S(ux0), S(uy1))], fill=PAPER + (255,), outline=INK + (255,), width=S(2))
    text(d, ((ux0 + ux1) / 2 - 18, (uy0 + uy1) / 2), 'UNDO', F['undo'], INK + (255,))
    d.rectangle([S(ux1 - 38), S(uy0 + 9), S(ux1 - 10), S(uy1 - 9)], fill=INK + (255,))
    text(d, (ux1 - 24, (uy0 + uy1) / 2), 'Z', F['key'], PAPER + (255,))
    text(d, (1810, 584), 'SPACE', F['key'], TEXT_MID + (255,))
    comp(img, L)


def draw_banner(img, st, F):
    b = st.get('banner')
    if not b:
        return
    L = Layer(); d = L.d
    x0, y0, x1, y1 = CX - 250, CY - 62, CX + 250, CY + 62
    pts = [(S(x0), S(y0 + 8)), (S(x1), S(y0)), (S(x1 - 8), S(y1)), (S(x0 + 6), S(y1 - 6))]
    d.polygon([(x + S(-6), y + S(-6)) for x, y in pts], fill=PINK + (255,))
    d.polygon([(x + S(8), y + S(10)) for x, y in pts], fill=INK + (255,))
    d.polygon(pts, fill=PAPER + (255,), outline=INK + (255,), width=S(4))
    text(d, (CX, CY - 10), b[0], F['win'], INK + (255,))
    text(d, (CX, CY + 40), b[1], F['you'], (130, 20, 90, 255))
    comp(img, L)


def fonts():
    return dict(h1=font(MONO, 28), body=font(MONO, 23), lab=font(MONO, 20), num=font(ANTON, 44), mid=font(ANTON, 30),
                you=font(ANTON, 32), tick=font(ANTON, 25), small=font(MONO, 21), fc1=font(ANTON, 30), fc2=font(ANTON, 26),
                why1=font(ANTON, 22), why2=font(PLEX, 21), end=font(ANTON, 50), undo=font(ANTON, 26), key=font(MONO, 20),
                win=font(ANTON, 64), seg_num=font(ANTON, 40), seg_small=font(MONO, 19), seg_type=font(ANTON, 26),
                chip=font(MONO, 21), tag=font(ANTON, 24), hub_big=font(ANTON, 58), hub_small=font(MONO, 20))


def render(name):
    st = STATES[name]
    F = fonts()
    img = backdrop()
    draw_rim(img, st)
    L = Layer()
    for i, g in enumerate(st['segs']):
        if g['owner'] != 'us':
            a0, a1, am = seg_angles(i, st['rot'])
            draw_corp_seg(L, g, a0, a1, am)
    comp(img, L)
    draw_runner_segs(img, st['segs'], st['rot'])
    draw_segment_marks(img, st, F['seg_type'], F['seg_num'], F['seg_small'])
    draw_walls_seals(img, st, F['seg_small'])
    draw_hub(img, st, F['hub_big'], F['mid'], F['hub_small'])
    draw_chips(img, st, F['chip'])
    draw_pointers(img, st)
    draw_overlays(img, st, F['tag'], F['seg_small'])
    draw_banner(img, st, F)
    draw_hud(img, st, F)
    draw_hand(img, st, F)
    draw_end_turn(img, st, F)
    out = img.resize((W, H), Image.LANCZOS).convert('RGB')
    os.makedirs(OUT, exist_ok=True)
    p = OUT + 'tk_%s.png' % name
    out.save(p)
    print('ok', p)
    return out


if __name__ == '__main__':
    for n in (sys.argv[1:] or ['board']):
        render(n)
