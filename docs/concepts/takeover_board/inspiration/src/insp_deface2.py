"""insp_deface2: DEFACE v2, the hand as ONE stencil sheet (not five stencils), energy as paint in a can, plays as paint on the wheel.

    python insp_deface2.py [df2_rest df2_aim df2_after sheet]      (default: all)

Designer on v1: "Really it's just reshaped cards though, right."  v2 breaks the card shape:
  * one cut sheet per turn, taped on your wall, with five cuts in it.  The cut is the action: its glyph and name are the holes,
    its knife outline is the target class (wedge = a segment, round = the hub).  The type word, the cost (drips) and the target
    are written on the sheet by hand next to the cut; the full rule shows only on hover, in the HUD.
  * DRAW = the roll the sheet came off; DISCARD = clogged cuts (peeled off with the sheet at END TURN); EXHAUST = burnt cuts.
  * energy = paint in the can (a fill gauge), not coins.
  * playing = the cut lifts out of the sheet and is laid on the wedge; confirm sprays it and the paint stays on the wedge.
    Lasting effects are paint that wears (GUARD a shield that fades per hit, a virus a tag that spreads).
Shared drawing (wheel, outcome marks, corp board, HUD panel) is imported from insp_render / tk_render, unchanged.
"""
import copy, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/inspiration')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import insp_render as IR
from insp_render import (TR, S, text, Layer, comp, INK, PAPER, PINK, PINK_D, HARM, FOCUS, CYAN, TEXT_HI, TEXT_MID, ANTON, PLEX, MONO,
                         ACTS, BOARD, PLAY, CX, CY, W, H, SS, plate_cols, tw, wrap, glyph_mask, stencil_text_mask, overspray, place,
                         tape, F_all, base_image, run_health, undo_tab, pile_icon, df_wall_bg)
from tk_states import GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN

OUT = IR.OUT
IR.WALL = (16, 150, 522, 736)          # the wall behind the sheet (shorter than v1: the can and piles sit below it)
SC = 0.60                                     # cut scale on the sheet (1.0 = wheel scale)
SHEET = (30, 196, 508, 712)                   # the sheet on the wall
CUTS = {'NUDGE': (112, 300), 'WORM': (272, 230), 'BREACH': (430, 232), 'GUARD': (190, 470), 'TIMEBOMB': (352, 472)}
# where the hand marks go (x, y of the type word), relative to the cut's anchor
DST = {'NUDGE': 'the hub', 'WORM': '3 corp', 'BREACH': 'next to yours', 'GUARD': 'one of yours', 'TIMEBOMB': 'a corp seg'}
DIM_PAPER = (226, 220, 206)


# ---------------------------------------------------------------- one cut: knife outline (target class) + holes (glyph + name)
def cut_geom(a, sc):
    """returns M (the cut piece, L), C (the holes, L), v (the virtual wheel centre in the image) at SS"""
    hub = a['tgt'] == 'hub'
    if hub:
        r1 = 80 * sc / 0.7
        size = int(S(2 * r1 + 60)); vx = vy = size // 2
        M = Image.new('L', (size, size), 0)
        ImageDraw.Draw(M).ellipse([vx - S(r1), vy - S(r1), vx + S(r1), vy + S(r1)], fill=255)
        g_c, g_px = (vx, vy - S(r1 * 0.32)), S(r1 * 0.62)
        n_c, n_px, maxw = (vx, vy + S(r1 * 0.34)), r1 * 0.42, S(1.5 * r1)
    else:
        r0, r1 = (TR.R_IN - 8) * sc, (TR.R_OUT + 10) * sc
        hw = math.radians(16.5)
        size = int(S(2 * r1 + 60)); vx = vy = size // 2
        M = Image.new('L', (size, size), 0)
        pts = [(vx + S(r1 * math.sin(-hw + 2 * hw * t / 30)), vy - S(r1 * math.cos(-hw + 2 * hw * t / 30))) for t in range(31)]
        pts += [(vx + S(r0 * math.sin(hw - 2 * hw * t / 30)), vy - S(r0 * math.cos(hw - 2 * hw * t / 30))) for t in range(31)]
        ImageDraw.Draw(M).polygon(pts, fill=255)
        rr = lambda f: r0 + f * (r1 - r0)
        n_c, n_px = (vx, vy - S(rr(0.78))), 40 * sc
        g_c, g_px = (vx, vy - S(rr(0.42))), S(70 * sc)
        maxw = S(2 * rr(0.78) * math.sin(math.radians(14.0)) * 0.88)
    C = Image.new('L', M.size, 0)
    gm = glyph_mask(a['g'], g_px)
    C.paste(gm, (int(g_c[0] - gm.width / 2), int(g_c[1] - gm.height / 2)), gm)
    tm = stencil_text_mask(a['nm'], TR.ImageFont.truetype(ANTON, int(S(n_px))))
    if tm.width > maxw:
        tm = tm.resize((int(maxw), int(tm.height * maxw / tm.width)), Image.LANCZOS)
    C.paste(tm, (int(n_c[0] - tm.width / 2), int(n_c[1] - tm.height / 2)), tm)
    return M, C, (vx, vy)


def anchor(a):
    """screen point that the cut's virtual centre lands on (wedges: x, top -> centre below; the hub disc: its centre)"""
    x, y = CUTS[a['id']]
    if a['tgt'] == 'hub':
        return (x, y)
    return (x, y + (TR.R_OUT + 10) * SC * 0.985)


def tip_y(a):
    x, y = CUTS[a['id']]
    if a['tgt'] == 'hub':
        return y + 80 * SC / 0.7
    return y + (TR.R_OUT + 10) * SC * 0.985 - (TR.R_IN - 8) * SC * math.cos(math.radians(16.5))


def full(im, v, at, rot=0.0):
    """an L mask placed on a full-screen L canvas"""
    out = Image.new('L', (W * SS, H * SS), 0)
    r = im.rotate(rot, resample=Image.BICUBIC, center=v) if rot else im
    out.paste(r, (int(S(at[0]) - v[0]), int(S(at[1]) - v[1])))
    return out


def arr(m):
    return np.asarray(m, np.float32) / 255.0


def lmask(a_):
    return Image.fromarray((np.clip(a_, 0, 1) * 255).astype(np.uint8))


def paint(lay, mask, col):
    lay.paste(Image.new('RGBA', lay.size, col + (255,)), (0, 0), mask)


# ---------------------------------------------------------------- hand marks (marker on the sheet)
def hand(lay, s, font, col, x, y, ang=-3.0, seed=1, anchor_='lm'):
    """marker writing: each letter slightly turned and off the baseline"""
    rng = np.random.default_rng(seed)
    d0 = ImageDraw.Draw(lay)
    total = d0.textlength(s, font=font)
    cx = S(x) - (total / 2 if anchor_ == 'mm' else 0)
    for ch in s:
        cw = d0.textlength(ch, font=font)
        if ch != ' ':
            t = Image.new('RGBA', (int(cw + S(16)), int(font.size * 1.6)), (0, 0, 0, 0))
            ImageDraw.Draw(t).text((S(8), t.height / 2), ch, font=font, fill=col + (255,), anchor='lm')
            t = t.rotate(ang + rng.uniform(-4, 4), resample=Image.BICUBIC)
            lay.alpha_composite(t, (int(cx - S(8)), int(S(y) - t.height / 2 + S(rng.uniform(-1.6, 1.6)) + (cx - S(x)) * math.tan(math.radians(ang)) * -1)))
        cx += cw
    return total / SS


def drip(d, x, y, r, col, fill=True):
    """a paint drip: a round drop with a pointed top"""
    pts = [(S(x), S(y - r * 2.2)), (S(x + r * 0.9), S(y - r * 0.2)), (S(x - r * 0.9), S(y - r * 0.2))]
    if fill:
        d.polygon(pts, fill=col + (255,))
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col + (255,))
    else:
        d.line(pts + [pts[0]], fill=col + (255,), width=S(1.6))
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], outline=col + (255,), width=S(1.6))


def can(L, F, x, y, n, nmax, cost=0):
    """energy = paint in the can: a spray can with a fill gauge (one band per energy); cost previews as a hatched band"""
    d = L.d
    w_, h_ = 74, 128
    # cap and nozzle
    d.rectangle([S(x + 22), S(y - 26), S(x + 52), S(y - 4)], fill=(60, 58, 66, 255), outline=INK + (255,), width=S(2))
    d.rectangle([S(x + 30), S(y - 38), S(x + 44), S(y - 26)], fill=PAPER + (255,), outline=INK + (255,), width=S(2))
    d.polygon([(S(x + 44), S(y - 35)), (S(x + 56), S(y - 38)), (S(x + 56), S(y - 28)), (S(x + 44), S(y - 30))], fill=INK + (255,))
    # body: ink with the pink label band and a hard drop
    d.rounded_rectangle([S(x + 4), S(y + 5), S(x + w_ + 4), S(y + h_ + 5)], radius=S(10), fill=INK + (255,))
    d.rounded_rectangle([S(x), S(y), S(x + w_), S(y + h_)], radius=S(10), fill=(44, 40, 50, 255), outline=INK + (255,), width=S(3))
    d.rectangle([S(x + 3), S(y + 14), S(x + w_ - 3), S(y + 36)], fill=PINK + (255,))
    text(d, (x + w_ / 2, y + 25), 'PAINT', F['a20'], INK + (255,))
    # the gauge: a window with one band per energy, filled from the bottom
    gx0, gx1, gy0, gy1 = x + 18, x + w_ - 18, y + 46, y + h_ - 12
    d.rectangle([S(gx0 - 3), S(gy0 - 3), S(gx1 + 3), S(gy1 + 3)], fill=PAPER + (255,), outline=INK + (255,), width=S(2))
    bh = (gy1 - gy0) / nmax
    for k in range(nmax):
        b1 = gy1 - k * bh; b0 = b1 - bh + 3
        box = [S(gx0), S(b0), S(gx1), S(b1)]
        if k < n - cost:
            d.rectangle(box, fill=PINK + (255,), outline=INK + (255,), width=S(1.5))
        elif k < n:
            d.rectangle(box, fill=PAPER + (255,))
            for t in range(0, 4):
                d.line([(S(gx0 + t * 8), S(b1)), (S(gx0 + t * 8 + 12), S(b0))], fill=HARM + (255,), width=S(2.2))
            d.rectangle(box, outline=INK + (255,), width=S(1.5))
        else:
            d.rectangle(box, fill=(200, 194, 182, 255), outline=INK + (255,), width=S(1.5))
    # reading
    text(d, (x + w_ + 22, y + 26), 'ENERGY', F['m18'], TEXT_MID + (255,), anchor='lm')
    s_ = '%d/%d' % (n, nmax) if not cost else '%d \u2192 %d' % (n, n - cost)
    text(d, (x + w_ + 22, y + 66), s_, F['a40'], (TEXT_HI if not cost else (255, 120, 110)) + (255,), anchor='lm')
    text(d, (x + w_ + 22, y + 104), 'paint left in the can', F['m16'], TEXT_MID + (255,), anchor='lm')


# ---------------------------------------------------------------- the sheet
def draw_sheet(img, F, state):
    """state: rest | aim | after.  aim: the BREACH cut is lifted out (an empty window); after: it is back, clogged with paint"""
    sheet_m = Image.new('L', (W * SS, H * SS), 0)
    x0, y0, x1, y1 = SHEET
    rng = np.random.default_rng(4)
    bottom = [(x1 - (x1 - x0) * t / 14, y1 + rng.uniform(-5, 4)) for t in range(15)]       # torn off the roll at the bottom
    ImageDraw.Draw(sheet_m).polygon([(S(x0), S(y0)), (S(x1), S(y0 + 2))] + [(S(x), S(y)) for x, y in bottom], fill=255)
    holes = np.zeros((H * SS, W * SS), np.float32)
    knife = np.zeros_like(holes)
    clog = np.zeros_like(holes)
    burnt = np.zeros_like(holes)
    for a in ACTS:
        M, C, v = cut_geom(a, SC)
        at = anchor(a)
        Mf, Cf = arr(full(M, v, at)), arr(full(C, v, at))
        edge = np.clip(arr(full(M.filter(ImageFilter.MaxFilter(3)), v, at)) - Mf, 0, 1)
        if state == 'aim' and a['id'] == 'BREACH':
            holes = np.maximum(holes, Mf)                 # the whole cut piece is out: a wedge-shaped window
        elif state == 'after' and a['id'] == 'BREACH':
            clog = np.maximum(clog, Cf)                   # back in, its holes clogged with this turn's paint
            knife = np.maximum(knife, edge)
        else:
            holes = np.maximum(holes, Cf)
            knife = np.maximum(knife, edge)
    Sa = arr(sheet_m)
    paper_a = Sa * (1 - holes)
    L = Layer()
    # pink scissor halo + linocut key around the sheet (it is the runner's print)
    halo = sheet_m.filter(ImageFilter.MaxFilter(S(4) * 2 + 1))
    paint(L.im, halo, PINK)
    TR.ink_key(L.im, sheet_m, key=2.4, drop=(4, 5))
    # the wall shows through every hole (punch the key and halo out where the holes are)
    a_ = np.asarray(L.im, np.float32)
    a_[..., 3] *= (1 - holes)
    L.im = Image.fromarray(a_.astype(np.uint8), 'RGBA'); L.d = ImageDraw.Draw(L.im)
    paint(L.im, lmask(paper_a), PAPER)
    fib = (np.random.default_rng(2).random(paper_a.shape) < 0.01) * paper_a
    paint(L.im, lmask(fib), (196, 188, 172))
    # old overspray round every hole (sprayed through before), and the knife line round each cut piece
    hm = lmask(holes)
    os_ = arr(overspray(hm, S(4), 0.5, 3)) * paper_a
    paint(L.im, lmask(os_), PINK)
    paint(L.im, lmask(np.clip(arr(hm.filter(ImageFilter.MaxFilter(3))) - holes, 0, 1) * Sa), INK)
    paint(L.im, lmask(knife * Sa * 0.85), (70, 60, 70))
    if clog.any():                                         # clogged: the holes full of wet pink, darker where it pooled
        paint(L.im, lmask(clog), PINK)
        gunk = (np.random.default_rng(8).random(clog.shape) < 0.18) * clog
        paint(L.im, lmask(gunk), PINK_D)
    comp(img, L)
    # tape at the top corners, the roll it came off, hand marks per cut
    L = Layer(); d = L.d
    tape(d, x0 + 10, y0 + 6, -35, 46, 14); tape(d, x1 - 10, y0 + 8, 35, 46, 14)
    for a in ACTS:
        x, y = CUTS[a['id']]
        ty = tip_y(a)
        seed = len(a['nm'])
        dead = bool(a.get('why'))
        lifted = state == 'aim' and a['id'] == 'BREACH'
        # the key: a circled number in marker at the cut's top-left
        kx, ky = (x - 66, y - 46) if a['tgt'] == 'hub' else (x - 62, y + 8)
        d.ellipse([S(kx - 15), S(ky - 15), S(kx + 15), S(ky + 15)], outline=INK + (255,), width=S(2.6))
        hand(L.im, a['key'], F['a24'], INK, kx - 5, ky, 0, seed)
        # the type word in the type plate's ink (lilac's deep tone on paper), by hand under the cut
        col, dk, tc = plate_cols(a['fam'])
        ink = dk if a['fam'] == 'CONTROL' else col
        hand(L.im, a['fam'], F['a26'], ink, x, ty + 22, -3, seed, anchor_='mm')
        # cost as drips + the number, and the target in pencil
        nd = max(a['cost'], 1)
        cx_ = x - (nd * 11 + 22 + tw(d, DST[a['id']], F['p19'])) / 2          # the cost + target line, centred under the cut
        cc = HARM if dead else PINK
        for k in range(max(a['cost'], 1)):
            drip(d, cx_ + 2 + k * 11, ty + 52, 4.2, cc, fill=a['cost'] > 0)
        hand(L.im, str(a['cost']), F['a24'], INK if not dead else HARM, cx_ + max(a['cost'], 1) * 11 + 2, ty + 48, 0, seed + 3)
        text(d, (cx_ + max(a['cost'], 1) * 11 + 22, ty + 50), DST[a['id']], F['p19'], (92, 86, 96, 255), anchor='lm')
        if lifted:
            hand(L.im, 'lifted', F['m18'], PINK_D, x, ty - 64, 0, 3, anchor_='mm')
        if state == 'after' and a['id'] == 'BREACH':
            hand(L.im, 'used', F['a24'], INK, x, ty - 14, -6, 5, anchor_='mm')
        if dead:                       # can't use: red tape across the cut, written on: needs 4
            cy_ = y + 70
            p0, p1 = (x - 76, cy_ + 18), (x + 76, cy_ - 14)
            d.line([(S(p0[0] + 2), S(p0[1] + 4)), (S(p1[0] + 2), S(p1[1] + 4))], fill=INK + (255,), width=S(34))
            d.line([(S(p0[0]), S(p0[1])), (S(p1[0]), S(p1[1]))], fill=HARM + (255,), width=S(30))
            ang_ = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            hand(L.im, 'needs 4', F['a26'], INK, x, cy_ + 3, -ang_, 7, anchor_='mm')
    comp(img, L)


def draw_left(img, F, state, energy):
    L = Layer(); d = L.d
    run_health(d, F, 24, 516, 18)
    sx = 32
    for wd, side in BOARD['hud']['status']:                         # statuses under the health tape
        col = CYAN if side == 'buff' else (255, 181, 71)
        w_ = tw(d, wd, F['m20'])
        d.rounded_rectangle([S(sx - 6), S(114), S(sx + w_ + 6), S(142)], radius=S(12), fill=(9, 22, 30, 220), outline=col + (255,), width=S(2))
        text(d, (sx, 128), wd, F['m20'], col + (255,), anchor='lm')
        sx += w_ + 26
    comp(img, L)
    df_wall_bg(img)
    # the roll this sheet came off (DRAW)
    L = Layer(); d = L.d
    x0, y0, x1, y1 = IR.SHEET if hasattr(IR, 'SHEET') else SHEET
    d.rounded_rectangle([S(24), S(160), S(514), S(194)], radius=S(16), fill=(222, 214, 198, 255), outline=INK + (255,), width=S(3))
    d.ellipse([S(14), S(158), S(48), S(196)], fill=(236, 230, 216, 255), outline=INK + (255,), width=S(3))
    d.arc([S(22), S(168), S(40), S(186)], 30, 320, fill=INK + (255,), width=S(2))
    text(d, (66, 177), 'DRAW %d' % BOARD['hud']['piles'][0], F['a24'], INK + (255,), anchor='lm')
    text(d, (170, 178), "the roll: next turn's cuts", F['m18'], (70, 64, 70, 255), anchor='lm')
    comp(img, L)
    draw_sheet(img, F, state)
    L = Layer(); d = L.d
    disc = BOARD['hud']['piles'][1] + (1 if state == 'after' else 0)
    pile_icon(d, F, 40, 760, 'peeled', 'DISCARD', 'clogged cuts', disc)
    pile_icon(d, F, 290, 760, 'burnt', 'EXHAUST', 'burnt cuts', 0)
    cost = 1 if state == 'aim' else 0
    can(L, F, 40, 858, energy, BOARD['hud']['energy'][1], cost=cost)
    undo_tab(d, F, 300, 990, 508, 1038, word='UNDO')
    comp(img, L)


# ---------------------------------------------------------------- paint on the wheel
def wedge_paint_masks(st):
    """lasting effects as paint that wears.  GUARD (G2) = a painted shield, worn per hit; a virus (V1) = a tag spreading in
    small marks toward the next segment"""
    m = Image.new('L', (W * SS, H * SS), 0); dm = ImageDraw.Draw(m)
    shield = Image.new('L', (W * SS, H * SS), 0); ds = ImageDraw.Draw(shield)
    ink_txt = []
    for i, g in enumerate(st['segs']):
        for word, side in g.get('st', []):
            if side != 'runner':
                continue
            a0, a1, am = TR.seg_angles(i, st['rot'])
            da = 0.16 if math.sin(am) > 0 else -0.17
            x, y = CX + (TR.R_OUT - 34) * math.cos(am + da), CY + (TR.R_OUT - 34) * math.sin(am + da)
            if word.startswith('G'):
                s_ = 22
                pts = [(x - s_, y - s_ * 0.9), (x + s_, y - s_ * 0.9), (x + s_, y + s_ * 0.1), (x, y + s_ * 1.2), (x - s_, y + s_ * 0.1)]
                dm.polygon([(S(px), S(py)) for px, py in pts], fill=255)
                ds.polygon([(S(px), S(py)) for px, py in pts], fill=255)
                ink_txt.append((x, y - 2, word[1:]))
            else:
                dm.text((S(x), S(y)), word, font=TR.font(ANTON, 30), fill=255, anchor='mm')
                for k in range(3):                        # the spread: smaller tags walking toward the next segment
                    aa = am + da + 0.05 * (1 if da > 0 else -1)
                    rr = TR.R_OUT - 58 - 16 * k             # spreading down the wedge's free edge, toward the hub
                    px, py = CX + rr * math.cos(aa), CY + rr * math.sin(aa)
                    rad = 5 - k * 1.2
                    dm.line([(S(px - rad), S(py - rad)), (S(px + rad), S(py + rad))], fill=255, width=S(3))
                    dm.line([(S(px - rad), S(py + rad)), (S(px + rad), S(py - rad))], fill=255, width=S(3))
    return m, ink_txt, shield


def fresh_paint(st, a_id='BREACH'):
    """the BREACH cut sprayed onto its wedge: glyph + name in wet pink, turned to the wedge, with drips"""
    a = [x for x in ACTS if x['id'] == a_id][0]
    M, C, v = cut_geom(a, 1.0)
    am = TR.seg_angles(st['aim'], st['rot'])[2]
    rot = -(math.degrees(am) + 90)
    Cf = full(C, v, (CX, CY), rot)
    return Cf


def draw_wheel_painted(img, st, F, state):
    s2 = copy.deepcopy(st)
    TR.draw_rim(img, s2)
    L = Layer()
    for i, g in enumerate(s2['segs']):
        if g['owner'] != 'us':
            a0, a1, am = TR.seg_angles(i, s2['rot'])
            TR.draw_corp_seg(L, g, a0, a1, am)
    comp(img, L)
    TR.draw_runner_segs(img, s2['segs'], s2['rot'])
    # your paint lives on the wheel's surface, under the engraved labels
    m, ink_txt, shield = wedge_paint_masks(s2)
    wear = np.random.default_rng(11).random((H * SS // 3 + 1, W * SS // 3 + 1))
    wear = np.asarray(Image.fromarray((wear * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BILINEAR), np.float32) / 255.0
    ma = arr(m)
    sa = arr(shield)
    worn = ma * (1 - sa) + sa * np.where(wear > 0.42, 1.0, 0.25)      # the shield is worn patchy (hits); the virus tag is fresh
    L = Layer()
    paint(L.im, lmask(np.clip(arr(m.filter(ImageFilter.MaxFilter(S(2) * 2 + 1))) - ma, 0, 1) * 0.9), INK)
    paint(L.im, lmask(arr(overspray(m, S(4), 0.3, 9))), PINK)
    paint(L.im, lmask(worn), PINK)
    for x, y, n in ink_txt:
        text(L.d, (x, y), n, F['a24'], INK + (255,))
    if state == 'after':
        Cf = fresh_paint(s2)
        ca = arr(Cf)
        paint(L.im, lmask(arr(overspray(Cf, S(6), 0.55, 12)) * 0.9), PINK)
        paint(L.im, lmask(ca), PINK)
        # wet drips from the lower edge of the paint, straight down
        ys, xs = np.nonzero(ca[::SS * 2, ::SS * 2] > 0.5)
        if len(xs):
            order = np.argsort(-ys)
            pick = [order[k] for k in range(0, min(len(order), 400), 80)]
            for k_, j in enumerate(pick[:5]):
                x_, y_ = xs[j] * 2, ys[j] * 2
                ln = 8 + 6 * (k_ % 3)
                L.d.line([(S(x_), S(y_)), (S(x_), S(y_ + ln))], fill=PINK + (255,), width=S(3))
                L.d.ellipse([S(x_ - 2.6), S(y_ + ln - 2.6), S(x_ + 2.6), S(y_ + ln + 2.6)], fill=PINK + (255,))
    comp(img, L)
    TR.draw_segment_marks(img, dict(s2, segs=[dict(g, st=[]) for g in s2['segs']]), F['seg_type'], F['seg_num'], F['seg_small'])
    if state == 'after':
        L = Layer(); d = L.d
        i = s2['aim']; g = s2['segs'][i]
        am = TR.seg_angles(i, s2['rot'])[2]
        ox, oy = CX + 276 * math.cos(am), CY + 276 * math.sin(am)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2)):
            TR.glyph(d, g['type'], ox + dx, oy - 44 + dy, 34, INK + (255,), 3.2)
        TR.glyph(d, g['type'], ox, oy - 44, 34, TR.K_TYPE + (255,), 3.2)
        text(d, (ox, oy + 2), str(g['hp']), F['seg_num'], TR.K_TYPE + (255,), stroke=3, sfill=INK + (255,))
        text(d, (ox, oy + 42), g['type'], F['seg_small'], TR.K_TYPE + (255,), stroke=2.5, sfill=INK + (255,))
        comp(img, L)
    TR.draw_hub(img, s2, F['hub_big'], F['mid'], F['hub_small'])
    TR.draw_pointers(img, s2)
    s3 = dict(s2); s3['pencil'] = None
    TR.draw_overlays(img, s3, F['tag'], F['seg_small'])


def held_piece(img, st):
    """aim: the BREACH cut piece out of the sheet, laid on the wedge at its angle; through its holes, the paint to come"""
    a = [x for x in ACTS if x['id'] == 'BREACH'][0]
    M, C, v = cut_geom(a, 1.0)
    im = Image.new('RGBA', M.size, (0, 0, 0, 0))
    Ca, Ma = arr(C), arr(M)
    TR.ink_key(im, M, key=2.2, drop=(5, 7))
    paint(im, lmask(Ma * (1 - Ca)), (236, 230, 216))
    paint(im, lmask(arr(overspray(C, S(5), 0.5, 4)) * Ma), PINK)
    paint(im, C, PINK)
    paint(im, lmask(np.clip(arr(C.filter(ImageFilter.MaxFilter(3))) - Ca, 0, 1) * Ma), INK)
    am = TR.seg_angles(st['aim'], st['rot'])[2]
    rot = -(math.degrees(am) + 90) - 1.2
    at = (CX + 4 * math.cos(am + 0.6), CY + 4 * math.sin(am + 0.6))
    sh = im.split()[3].point(lambda p: int(p * 0.55))
    shadow = Image.new('RGBA', im.size, INK + (0,)); shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(S(6))))
    place(img, shadow, v, (at[0] + 10, at[1] + 14), rot)
    place(img, im, v, at, rot)


# ---------------------------------------------------------------- the right flank: the corp board + HUD, as v1, with this plate's hint
HINT = None
_fp = IR.forecast_panel


def _forecast_panel(d, F, box, st, aim_hint=None):
    x0, y0, x1, y1 = box
    h = 136 + (52 if len(st['hud']['forecast']) > 1 else 0) + 28 * len(HINT or []) + (10 if HINT else 0)
    _fp(d, F, (x0, y0, x1, y0 + h), st, aim_hint=HINT)


IR.forecast_panel = _forecast_panel


def render(state):
    global HINT
    F = F_all()
    if state == 'rest':
        st = copy.deepcopy(BOARD); HINT = None; energy = 3
    elif state == 'aim':
        st = copy.deepcopy(PLAY); energy = 3
        HINT = ['rule: 3 damage, a corp segment next to', 'yours.  Enter: spray  \u00b7  Esc: put back']
    else:
        st = copy.deepcopy(PLAY); energy = 2
        st['focus'] = []; st['aim'] = 2
        st['hud']['energy'] = (2, 3)
        st['hud']['forecast'] = [[('BREACH', S_PLAN), ('sprayed: FIREWALL 5 \u2192 2, TAKEN', S_HI)],
                                 st['hud']['forecast'][-1]]
        HINT = ['Z: undo the spray (paint back in the can)']
    img = base_image()
    draw_wheel_painted(img, st, F, state)
    if state == 'aim':
        held_piece(img, st)
    TR.draw_outcomes(img, st, F)
    draw_left(img, F, state, energy)
    IR.df_right(img, F, st, False)
    if state == 'aim':
        L = Layer()
        text(L.d, (32, 1060), 'BREACH fits CORE and FIREWALL (next to yours)', F['m18'], FOCUS + (255,), anchor='lm')
        comp(img, L)
    return img


def sheet():
    names = [('df2_rest', 'DEFACE v2, rest', "one cut sheet: five cuts, hand marks, paint can"),
             ('df2_aim', 'DEFACE v2, aim', 'the BREACH cut lifted and laid on FIREWALL; can previews -1'),
             ('df2_after', 'DEFACE v2, after', 'wet paint on FIREWALL, TAKEN; cut clogged; can 2/3')]
    tw_, th_ = 900, 506
    pad, cap = 14, 64
    sh = Image.new('RGB', (3 * tw_ + 4 * pad, th_ + cap + 2 * pad + 56), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = TR.ImageFont.truetype(MONO, 18); fa = TR.ImageFont.truetype(ANTON, 24); fb = TR.ImageFont.truetype(ANTON, 32)
    d.text((pad, 12), 'DEFACE v2: one stencil sheet per turn, energy as paint, plays as paint on the wheel', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + k * (tw_ + pad); y = 60
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 6), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 40), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'df2_sheet.jpg', quality=90)
    print('ok', OUT + 'df2_sheet.jpg')


if __name__ == '__main__':
    for n in (sys.argv[1:] or ['df2_rest', 'df2_aim', 'df2_after', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = render(n.split('_')[1])
        img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + n + '.png')
        print('ok', OUT + n + '.png')
