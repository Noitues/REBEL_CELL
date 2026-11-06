"""f1_hover: the hover plates in F1 (Brace = protect a slice, Twist = turn one ring, Trigger = resolve a unit now) on the redesigned board.
Grammar (VISUAL_PLAN H, R51): lit = what the card touches; everything else x0.40 value, chroma x0.45 (the dim the designer likes).  Motion in hover is grease pencil (PLAN), never pink or orange.
FOCUS = four lime corner brackets only (thin = legal, thick = aimed).  The lifted card carries the pink offset print.  Hover tag text is parked (not drawn)."""
import sys, os, copy, math, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import f1_render as R
import hover_sim as HS
import hv_lib as HL
import f1_tower as FT
import f1_hand as FH
import a2_kit as K2
import a2_plan as P2m
import r2_arcs as RA
import o_arcs as OA
import cv_board as CB
from cv_lib import L2, ppx, C, W, H, NOW
import asm_r2 as A
import hud2

HAND4 = ['Brace', 'Spin3', 'Trigger', 'Twist']
BILL = (1072, 76, 1896, 270)
OBJ = (1072, 278, 1896, 330)
RAMB = (1072, 334, 1896, 386)
HEAD = (1072, 12, 1896, 68)
BEZ = (RA.__dict__.get('BZ0', 388) - 2, 424)
rmid = lambda dep: sum(CB.ring_geom(dep)) / 2.0
PLAN = HL.PLAN


def frames(cards, tag):
    f_live, _, _ = HS.frame([], None, 'live', hand=HAND4)
    f_plan, st, pv = HS.frame(cards, None, tag, hand=HAND4)
    return f_live, f_plan


def uby(f, uid):
    return [u for u in f['units'] if u['id'] == uid][0]


# ------------------------------------------------------------------ lit regions
def lit_tower(Lt):
    Lt.disc(FT.TRIM1 + 6)


def lit_ring(Lt, dep, pad=2):
    ri, ro = CB.ring_geom(dep)
    Lt.annulus(ri - pad, ro + pad)


def lit_arcs_of(Lt, f, ids=None, pad=4):
    for it in RA.layout_items(f, ids):
        r = OA.LANE_R[min(it['lane'], 2)]
        Lt.wedge(r - OA.HALF - 5, r + OA.HALF + 5, it['a0'] - pad, it['a1'] + pad, 2)


def lit_cells(Lt, f, ids):
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            Lt.poly(HL.cell_poly_unit(u), 5)


# ------------------------------------------------------------------ marks
def focus_slice(L, s, thick=False):
    K2.focus_brackets(L, 'band', dict(ri=FT.R_IN - 3, ro=FT.R_OUT + 3, a0=60 * s - 27.5, a1=60 * s + 27.5), 'A', w=5.4 if thick else 3.0, arm=22 if thick else 11, grow=3 if thick else 0)


def focus_cell(L, u, thick=False):
    ri, ro = CB.ring_geom(u['dep'])
    a0 = 60 * u['s'] - 30
    a1 = 60 * (u['s'] + u['w'] - 1) + 30
    K2.focus_brackets(L, 'band', dict(ri=ri + 3, ro=ro - 3, a0=a0 + 2.5, a1=a1 - 2.5), 'A', w=5.4 if thick else 3.0, arm=30 if thick else 17, grow=0)


def bill_marks(L, f_live, f_plan):
    box = hud2.R.get('hero_pair') or (1416, 78, 1574, 168)
    lv, pl = f_live['pv']['eq'], f_plan['pv']['eq']
    th = str(pl['through'])
    tw = L.tw(th, 58, 'anton')
    xt = box[2] - 8 - tw
    if pl['through'] != lv['through']:
        HL.pencil(L, [(xt, 151), (xt + tw, 150.5)], w=3.2, ink=1.5, seed=3, cap=False)
    if pl['lands'] != lv['lands']:
        ls = str(pl['lands'])
        lw = L.tw(ls, 58, 'anton')
        HL.pencil(L, [(box[0] + 8, 151), (box[0] + 8 + lw, 150.5)], w=3.2, ink=1.5, seed=4, cap=False)


def ram_mark(L, before, after):
    for i in range(after, before):
        x, y = 1149 + 32 * i, 359
        L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=HL.INKC, w=6.6)
        L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=PLAN, w=3.2)


def trace_mark(L, before, after):
    for i in range(before, after):
        x, y = 1438 + 29 * i, 359
        L.rect([x - 15, y - 15, x + 15, y + 15], outline=HL.INKC, w=6.6, r=5)
        L.rect([x - 15, y - 15, x + 15, y + 15], outline=PLAN, w=3.2, r=5)


def hatch_cell(L, u, col, alpha=0.55):
    import plan_patch as PP
    poly = HL.cell_poly_unit(u)
    lay = L2()
    PP.hatch_poly(lay, poly, col, pitch=8.0, lw=2.4, base=None, edge=2.6)
    im = lay.im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    L.im.alpha_composite(im)


def pink_burst(L, x, y, r=24, seed=1):
    HL.starburst(L, x, y, r, HL.PINK, (255, 255, 255), 11, 2.6, seed)


# ------------------------------------------------------------------ the generic plate
def build(f_board, f_hud, words, lift, lit_fn, marks_fn, hide=(), arcs_skip=(), under=None, ghosts=None, tag=None, k=0.40, desat=0.45, hand_beat='p1'):
    NOW['words'] = words
    bg = R.render('p1' if words else 'nowords', frame=f_board, hud_frame=f_hud, hide_units=hide, arcs_skip=arcs_skip, with_ui=False, tag=tag).convert('RGBA')
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = Lt.mask()
    img = HL.dim_image(bg.convert('RGB'), mask, k=k, desat=desat).convert('RGBA')
    if under:
        under(img)
    if ghosts:
        for g in ghosts:
            img.alpha_composite(g)
    Lm = L2()
    marks_fn(Lm)
    img.alpha_composite(Lm.done())
    # the player's hand: the hovered card lifted with the pink print; the others and the stickers sit back (value x0.72 / x0.62)
    f_for_ui = f_hud
    FH.place_ui(img, 'you', not words, f_for_ui)
    FH.draw_hand(img, A.J, hand_beat, nw=not words, lift=lift, dim_others=0.72)
    FH.place_ui(img, 'name', not words)
    FH.place_ui(img, 'send', not words)
    import a2_stick as AS
    from PIL import ImageChops
    lay, info = AS.stack_layer(words, {})
    m = Image.new('L', lay.size, 0)
    dr = ImageDraw.Draw(m)
    dr.rectangle([1655, 850, 1895, 899], fill=255)
    dr.rectangle([1660, 1028, 1900, 1060], fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    arr = np.asarray(lay).astype(np.float32)
    arr[..., :3] *= 0.62
    img.alpha_composite(Image.fromarray(arr.astype(np.uint8), 'RGBA'))
    return img.convert('RGB')


# ================================================================================================ Brace: protect a slice
def brace(words=True, aim=2):
    f_live, f_plan = frames([('Brace', aim)], 'brace')
    fb = copy.deepcopy(f_plan)
    fb['brace_sectors'] = []
    for w in fb['wheel']:
        w['brace'] = False

    def lit(Lt):
        lit_tower(Lt)
        lit_arcs_of(Lt, f_plan)
        Lt.box(*BILL, r=8)
        Lt.box(*RAMB, r=8)

    def marks(L):
        for s in range(6):
            if s != aim:
                focus_slice(L, s)
        focus_slice(L, aim, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        for it in RA.layout_items(f_plan):
            u = it['u']
            for q in range(u['w']):
                sec = (it['s0'] + q) % 6
                if u.get('land_brace', {}).get(str(sec)):
                    r = OA.LANE_R[min(it['lane'], 2)]
                    HL.pencil(L, HL.arc(r + 21, 60 * sec - 18, 60 * sec + 18), w=4.0, ink=2.0, seed=sec)

    def under(img):
        # the clamp at 55 percent on the aimed slice (a proposal), with a grease-pencil outline round the whole wedge
        cv = FT.Canvas(FT.TW, FT.TW, 3, seed=5)
        import f1_fx as FX
        FX.brace_clamp(cv, aim, ghost=True)
        im = cv.down()
        im.putalpha(im.split()[3].point(lambda v: int(v * 0.9)))
        img.alpha_composite(im, (int(C[0] - FT.CT[0]), int(C[1] - FT.CT[1])))
        cv2 = FT.Canvas(FT.TW, FT.TW, 3, seed=6)
        a0, a1 = 60 * aim - 26.5, 60 * aim + 26.5
        for rr in (FT.R_IN - 3, FT.R_OUT + 14):
            FT.pencil(cv2, FT.arc_pts(FT.CT, rr, a0, a1, 0.8), 4.6)
        for sg, a in ((-1, a0), (1, a1)):
            FT.pencil(cv2, [FT.pol(FT.CT, FT.R_IN - 3, a), FT.pol(FT.CT, FT.R_OUT + 14, a)], 4.6)
        im2 = cv2.down()
        img.alpha_composite(im2, (int(C[0] - FT.CT[0]), int(C[1] - FT.CT[1])))
    return build(fb, f_plan, words, 'Brace', lit, marks, under=under, tag='h_brace')


# ================================================================================================ Trigger: resolve a unit now
def trigger(words=True):
    f_live, f_plan = frames([('Trigger', 4)], 'trigger')
    tr_units = [4, 5, 6, 7]
    fb = copy.deepcopy(f_live)
    victim = uby(fb, 1)
    victim['lose'] = [0, victim['hp']]
    tgt = uby(f_live, 4)
    kills = [e for e in f_plan['tlog'] if e[0] == 'trig_unit']

    def lit(Lt):
        lit_cells(Lt, f_live, set(tr_units) | {1})
        lit_arcs_of(Lt, f_plan)
        for s in (3, 4):
            Lt.sector(s, FT.R_IN - 24, FT.TRIM1 + 6, 30, 2)
        Lt.box(*BILL, r=8)
        Lt.box(*RAMB, r=8)

    def marks(L):
        for uid in tr_units:
            if uid != 4:
                focus_cell(L, uby(f_live, uid))
        hatch_cell(L, victim, HL.PINK, 0.55)
        for e in kills:
            sec = e[1]
            ang = 60 * sec + 13
            r0 = CB.ring_geom(tgt['dep'])[1] - 6
            r1 = CB.ring_geom(0)[0] + 26
            HL.channel(L, [ppx(C, r0, ang), ppx(C, r1, ang)], col=PLAN, w=13, head=19, chev=True, fill=(10, 8, 20, 200), tail_dot=True)
        kx, ky = ppx(C, rmid(0) + 2, 60 * 4 + 8)
        pink_burst(L, kx, ky, 25, 3)
        focus_cell(L, tgt, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        bill_marks(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])
    return build(fb, f_plan, words, 'Trigger', lit, marks, arcs_skip={1, 4}, tag='h_trigger')


# ================================================================================================ Twist: turn one ring
def twist(words=True, ring=1, d=1):
    f_live, f_plan = frames([('Twist', (ring, d))], 'twist')
    changed = [u['id'] for u in f_plan['units'] if u['dep'] == ring and uby(f_live, u['id']).get('land_sectors') != u.get('land_sectors')]
    veil_ids = set(changed)

    def lit(Lt):
        lit_ring(Lt, 1)
        lit_ring(Lt, 2)
        Lt.annulus(BEZ[0], BEZ[1])
        lit_arcs_of(Lt, f_plan)
        Lt.box(*BILL, r=8)
        Lt.box(*RAMB, r=8)
        Lt.box(1060, 6, 1908, 70, 10)

    def marks(L):
        r = rmid(ring)
        a_mid = 60 * 1 if ring == 1 else 60 * 0
        pts = HL.arc(r, a_mid - 24 * d, a_mid + 24 * d, 20)
        HL.channel(L, pts, col=PLAN, w=16, head=22, chev=True, fill=(10, 8, 20, 190))        # hover motion = grease pencil (PLAN), never orange
        P2m.twist_badge(L, f_plan, 'A')
        ro = 2 if ring == 1 else 1
        ri_, ro_ = CB.ring_geom(ro)
        K2.focus_brackets(L, 'band', dict(ri=ri_ + 2, ro=ro_ - 2, a0=-28, a1=28), 'A', w=3.0, arm=16, grow=0)
        K2.focus_brackets(L, 'band', dict(ri=CB.ring_geom(ring)[0] + 2, ro=CB.ring_geom(ring)[1] - 2, a0=-28, a1=28), 'A', w=5.4, arm=28, grow=0)
        bill_marks(L, f_live, f_plan)

    ghosts = []
    La = L2()
    import r2_arcs as A2
    A2.landing_arcs(La, f_plan, {}, only=veil_ids)
    ghosts.append(La.done())
    Lo = L2()
    for it in RA.layout_items(f_plan, veil_ids):
        r = OA.LANE_R[min(it['lane'], 2)]
        HL.pencil(Lo, HL.arc(r + OA.HALF + 4, it['a0'] + 4, it['a1'] - 2), w=3.4, ink=1.8, seed=it['u']['id'], cap=False)
    ghosts.append(Lo.done())
    return build(f_live, f_plan, words, 'Twist', lit, marks, ghosts=ghosts, arcs_skip=veil_ids, tag='h_twist')


JOBS = {'hover_brace': lambda: brace(), 'hover_twist': lambda: twist(), 'hover_trigger': lambda: trigger(),
        'hover_brace_nowords': lambda: brace(False), 'hover_twist_nowords': lambda: twist(False), 'hover_trigger_nowords': lambda: trigger(False)}

if __name__ == '__main__':
    for nm in sys.argv[1:]:
        t = time.time()
        im = JOBS[nm]()
        im.save(R.OUT + nm + '.png')
        print('ok', nm, round(time.time() - t, 1), flush=True)
