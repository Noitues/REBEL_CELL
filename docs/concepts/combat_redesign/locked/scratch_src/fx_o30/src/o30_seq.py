"""o30_seq: the full E10 p3 resolve beat, sequenced on the final board (O-30, art director fix 4).

Order = the HUD chain on p3 (1 TWIST, 2 TRIGGER, 3 BRACE, 4 GUNS, 5 LANDS, 6 RINGS STEP / W4 enters), opened by SEND IT (fx_commit),
with the GODOT_PORT_SPEC 8.2 spacing: effects run one after another and the next starts 100 ms after the previous one ends
(no two effects share a 100 ms window).  Brace's block plays where the braced landing stops (LANDS), as 8.3 says.

Every effect is the effects designers' own render function (copies in this folder), drawn on a running canvas: each segment's
base plate is the previous segment's settled frame, so nothing pops between effects.  Full 1920x1080 frames.

Sources in the state (f2, E10):
  commit        SEND IT on the best line: p2 pencil marks -> p3 paint
  twist         Twist [1, 1]: ring +1 turns one sector (unit layer of p3 ring +1, -60 deg -> 0)
  trace_add     Trigger played: Trace 3 -> 4 (pip 4 of the p3 HUD)
  trigger_hit   tlog trig_unit: Payload 4's trigger hits Packet 1 in sectors 3 and 4 (the commit has already painted the route,
                so the in-sequence form drops the pencil-yellow ignite and keeps the bursts)
  refund        tlog trig_refund: Packet 1 dies to the trigger, +1 RAM: RAM 2 -> 3 (4 at turn start, Trigger 1 and Brace 1 paid)
  gun_hit       guns: sector 0 BURST shot 1 on Worm 2 (h 1)
  kill          guns: sector 0 BURST shot 2, Worm 2 hp 2 -> 0 (fate dies)
  ricochet_gold guns: sector 4 BURST, 2 shots warded by Packet 6 (h 0)
  shield_block  Worm 3 lands 3 on sector 1 SHIELD: absorbed 2 (two chevrons stop on the plate)
  soak_take     the same landing: soaked 1 (the overflow chevron into the funnel)
  brace_block   the same Worm 3 lands 3 on sector 2 TURRET: braced 3, through 0
  clear         Worm 3 THROUGH 0 (LANDS 3 -> THROUGH 0)
  settle        board hand-off: the landed Worm 3 and the spent gun marks leave ring 0 (260 ms dissolve, the reduce-motion dissolve)
  rings_step    END TURN, schedule [2, 0, 0]
  wave_enter    W4 (Jammer w1 s0, Jammer w2 s4) enters ring +2
"""
import sys, os, math, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import fxlib as FL
import fx_eff as E
import fxk_lib as K
import fx_cdhl as CD

O30 = 'D:/rc_scratch/combat_redesign/locked/fx_o30/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
SK = 'neutral'
GAP = 100
# O-30: the END TURN hand-off holds 400 ms before RINGS STEP (100 ms everywhere else).  Measured: with 100 ms, the clear wash
# leaving and the rings-step cells / tape arrow put 4 flashes inside one second in a 60 px tile at the tape (x 810, y 240).
GAP_AFTER = {'settle': 400}


def load(fp):
    return np.asarray(Image.open(fp).convert('RGB'), np.float32)


P2 = load(FINAL + 'p2_preview.png')
P3 = load(FINAL + 'p3_resolve.png')
P3E = load(O30 + 'work/base_neutral_p3_empty.png')
P3K = load('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/base_neutral_p3kill.png')
H, W = P3.shape[:2]
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RHO = np.hypot(XX - FL.C[0], YY - FL.C[1])

# ------------------------------------------------------------------ HUD pre-state patches (p3 HUD coordinates, measured)
P3PIP = [(1426, 513), (1454, 513), (1482, 513), (1510, 513), (1538, 513)]
TRIG_SLOT = (1268, 790, 1452, 1062)        # the TRIGGER PLAYED slot on p3
RAM_SLOT, RAM_EMPTY = CD.RAM_SLOT, CD.RAM_EMPTY


def patch_trace(img):
    """Trace 3: pip 4 shows as the unlit pip 5"""
    o = img.copy()
    q = 13
    (sx, sy), (tx, ty) = P3PIP[4], P3PIP[3]
    o[ty - q:ty + q, tx - q:tx + q] = img[sy - q:sy + q, sx - q:sx + q]
    return o


def patch_ram(img, src=None):
    """RAM 2: slot 3 shows as the empty slot 4 (the same patch fx_refund uses for its pre-state)"""
    o = img.copy()
    s = img if src is None else src
    sx, sy = int(RAM_EMPTY[0]), int(RAM_EMPTY[1])
    tx, ty = int(RAM_SLOT[0]), int(RAM_SLOT[1])
    o[ty - 23:ty + 23, tx - 17:tx + 17] = s[sy - 23:sy + 23, sx - 17:sx + 17]
    return o


def unpatch_ram(img):
    o = img.copy()
    tx, ty = int(RAM_SLOT[0]), int(RAM_SLOT[1])
    o[ty - 23:ty + 23, tx - 17:tx + 17] = P3[ty - 23:ty + 23, tx - 17:tx + 17]
    return o


def pre_hud(img):
    return patch_ram(patch_trace(img))


# ------------------------------------------------------------------ ring +1 unit layer (twist)
R1 = (270.5, 328.5)
_ua1 = None


ANG = np.degrees(np.arctan2(XX - FL.C[0], -(YY - FL.C[1]))) % 360


def ring1_cells():
    """ring +1 unit cells of the state (f2, dep 1): (a0, a1) degrees; cell = sector s .. s + w, centred on the sector axis"""
    J = json.load(open(O30 + 'state_e10.json'))
    return [(60 * u['s'] - 30, 60 * (u['s'] + u['w']) - 30) for u in J['f2']['units'] if u['dep'] == 1]


def ring1_span_mask(pad=2.0):
    m = np.zeros(ANG.shape, bool)
    for a0, a1 in ring1_cells():
        m |= ((ANG - (a0 - pad)) % 360) <= (a1 - a0 + 2 * pad)
    return m


def ua_ring1():
    global _ua1
    if _ua1 is None:
        d = np.abs(P3 - P3E).max(2)
        m = (d > 14) & ~E.pinkish(P3) & (RHO > R1[0]) & (RHO < R1[1]) & ring1_span_mask()
        m = ndi.binary_closing(m, iterations=1)
        m = ndi.binary_dilation(m, iterations=1)
        a = ndi.gaussian_filter(m.astype(np.float32), 0.6)
        _ua1 = np.clip(a * 1.25, 0, 1) * ((RHO > R1[0]) & (RHO < R1[1]))
    return _ua1


RBOX = FL.Box(200, 204, 873, 877)
R1REG = ((RHO > R1[0] - 1) & (RHO < R1[1] + 1)).astype(np.float32)


def ring1_units():
    """angular centres of the ring +1 unit cells (state f2, dep 1)"""
    return [((a0 + a1) / 2.0) % 360 for a0, a1 in ring1_cells()]


def ring1_units_px():
    """angular centres of the ring +1 unit cells on p3 (from the unit layer)"""
    a = ua_ring1() > 0.5
    lab, n = ndi.label(a)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 300:
            continue
        ang = np.degrees(np.arctan2(xs - FL.C[0], -(ys - FL.C[1]))) % 360
        # circular mean
        c = math.degrees(math.atan2(np.sin(np.radians(ang)).mean(), np.cos(np.radians(ang)).mean())) % 360
        out.append(round(c, 1))
    return sorted(out)


def ring1_move(full, d, echoes=(), src=None):
    """full frame with the ring +1 unit layer turned by d degrees (clockwise +)"""
    src = full if src is None else src
    ua = ua_ring1()
    o = full.copy()
    hole = ua[..., None]
    o = o * (1 - hole) + P3E * hole
    b = RBOX
    cr = E.move_layer(b.crop(o), SK, b, R1REG, d_ang=d, echoes=echoes, tint=FL.PINK, src=src, ua=ua)
    o[b.y0:b.y1, b.x0:b.x1] = cr
    return o


# ------------------------------------------------------------------ segment renderers: r(t, reduce, canvas) -> full frame
def paste(canvas, box, crop):
    o = canvas.copy()
    o[box.y0:box.y1, box.x0:box.x1] = crop
    return o


def r_commit(t, red, cv):
    p2, p3 = pre_hud(P2), pre_hud(P3)
    FL._cache[(SK, 'p2')] = p2
    FL._cache[(SK, 'p3')] = p3
    E._commit.clear() if not hasattr(r_commit, 'ok') else None
    r_commit.ok = True
    box = E.FX['fx_commit']['_box']
    oc = E.commit_render(t, SK, red)
    a2, a3, marks, nd, endp, rest = E.commit_data(SK, box)
    k = E.e_io3(E.seg(t, 200, 500)) if red else E.e_io3(E.seg(t, 560, 760))
    full = p2 * (1 - k) + p3 * k
    inside = (marks | rest)[..., None]
    crop = np.where(inside, oc, oc + (box.crop(full) - a2))
    full = paste(full, box, crop)
    return ring1_move(full, -60.0)


def twist_d(t):
    return E.twist_ang(t) - 60.0


def r_twist(t, red, cv):
    base = pre_hud(P3)
    if red:
        k = E.e_io3(E.seg(t, 120, 380))
        a = ring1_move(base, -60.0, src=base)
        b = ring1_move(base, 0.0, src=base)
        out = a * (1 - k) + b * k
    else:
        d = twist_d(t)
        sp = E.speed_of(E.twist_ang, t, 0.20)
        ech = [(0.0, twist_d(t - lg), al * sp) for lg, al in zip(E.ECHO_LAG, E.ECHO_U)] if sp > 0.02 else []
        out = ring1_move(base, d, ech, src=base)
    b = RBOX
    L = FL.Layer(b)
    for cpost in R1U:
        c0 = cpost - 60.0                 # one sector long, from the old centre to the new one (fx_twist draws c0 + 4 .. c0 + 60)
        if red:
            al = FL.e_out3(FL.seg(t, 0, 100)) * (1 - FL.seg(t, 380, 520))
            if al > 0:
                FL.arrow(L, FL.arc_pts(299.5, c0 + 4, c0 + 60), FL.PINK, 5.0, 15.0, 4.0, int(255 * al))
        elif t < 600:
            head = c0 + 4 + 56 * FL.e_out3(FL.seg(t, 0, 120))
            tail = c0 + 4 + E.twist_ang(t)
            al = 1 - FL.seg(t, 540, 600)
            if head - tail > 3 and al > 0:
                FL.arrow(L, FL.arc_pts(299.5, tail, head), FL.PINK, 5.0, 15.0, 4.0, int(255 * al))
    out[b.y0:b.y1, b.x0:b.x1] = FL.over(b.crop(out), L.done())
    return out


TBOX = FL.Box(1240, 470, 1620, 1080)


def r_trace(t, red, cv):
    """fx_trace_add on the p3 HUD: card glitch on the TRIGGER PLAYED slot, then pip 4 of the TRACE row lights"""
    box = TBOX
    out = box.crop(cv)
    p = P3
    sx, sy = P3PIP[2]
    tx, ty = P3PIP[3]
    q = 13
    lit = p[sy - q:sy + q, sx - q:sx + q].copy()
    if not red and 16 <= t < 166:
        i = min(4, int((t - 16) // 30.0))
        rr = np.random.default_rng(100 + i)
        rows = []
        for _ in range(3):
            y = int(rr.integers(TRIG_SLOT[1] + 6, TRIG_SLOT[3] - 20))
            rows.append((y, int(rr.integers(5, 11)), int(rr.choice([-6, 6]))))
        out = E.glitch(out, box, rows, 6, rr, (TRIG_SLOT[0] - 8, TRIG_SLOT[1], TRIG_SLOT[2] + 8, TRIG_SLOT[3]))
    if t >= 166:
        stp = 0 if red else min(3, int((t - 166) // 33.4))
        scale = [1.7, 1.35, 1.0, 1.0][stp]
        if stp < 2 and not red:
            Lp = FL.Layer(box)
            hq = 11 * scale
            Lp.d.rectangle([(tx - hq - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq - box.x0) * 3, (ty + hq - box.y0) * 3], fill=FL.VIOLET + (255,), outline=FL.INK + (255,), width=6)
            Lp.d.rectangle([(tx - hq - 4 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx - hq - 1 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(255, 40, 120, 200))
            Lp.d.rectangle([(tx + hq + 1 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq + 4 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(40, 200, 255, 200))
            out = FL.over(out, Lp.done())
        else:
            a, b_ = ty - q - box.y0, tx - q - box.x0
            out[a:a + 2 * q, b_:b_ + 2 * q] = lit
        if not red and 166 <= t < 266:
            j = int((t - 166) // 33.4)
            rr = np.random.default_rng(300 + j)
            rows = [(int(rr.integers(ty - 13, ty + 10)), 4, int(rr.choice([-6, 6])))]
            out = E.glitch(out, box, rows, 6, rr, (1330, ty - 18, 1600, ty + 18))
    return paste(cv, box, out)


def d_trigger_hit_seq(lay, t, c):
    """fx_trigger_hit inside the sequence: the commit has already burned the pencil route into paint, so the pencil
    layer and the pencil Xs are not drawn again; the bursts and speed lines run on the same clock as the stand-alone effect."""
    red = c.reduce
    for (x, y), t0, sd in ((CD.X3, 230, 3), (CD.X4, 420, 4)):
        if t >= t0 or red:
            tt = t - t0
            k = 1.0 if red else CD.eback(CD.seg(tt, 0, 70))
            fd = 1 - CD.seg(tt, 200, 330)
            if red:
                fd = 1 - CD.seg(t, 300, 500)
            if not red:
                CD.speed_lines(lay, x, y, 22, 54, 10, math.sin(math.pi * CD.seg(tt, 0, 180)), op=fd, seed=sd)
            CD.burst(lay, x, y, 20, k, seed=sd, op=fd)


def cd_render(fid, draw=None, post=None):
    fx = dict(CD.BYID[fid])
    if draw is not None:
        fx['draw'] = draw
    fx['skins'] = (SK,)

    def r(t, red, cv):
        K.BASES[(SK, 'p3')] = cv
        K.BASES[(SK, fx['pre'])] = cv
        if fx.get('post'):
            K.BASES[(SK, fx['post'])] = post if post is not None else cv
        x0, y0, x1, y1 = fx['box']
        im = np.asarray(K.frame(fx, SK, t, reduce=red), np.float32)
        o = cv.copy()
        o[y0:y1, x0:x1] = im
        return o
    return r


def r_refund_factory():
    base = cd_render('fx_refund')

    def r(t, red, cv):
        return base(t, red, unpatch_ram(cv))
    return r


# ---- P family on the real sectors of this landing (Worm 3: sector 1 SHIELD absorbed 2 + soaked 1, sector 2 TURRET braced 3)
SH_BOX = FL.Box(590, 240, 1000, 520)


def mp_render(fid):
    def r(t, red, cv):
        FL._cache[(SK, 'p3')] = cv
        box = E.FX[fid]['_box']
        return paste(cv, box, E.FX[fid]['render'](t, SK, red))
    return r


LANES = ((RHO > 425) & (RHO < 482)).astype(np.float32)[..., None]


def r_settle(t, red, cv):
    """hand-off before RINGS STEP: the landed Worm 3 and the spent gun marks leave ring 0, and the old landing arcs, the clear
    wash and the brace stamp lift off the lanes, in one 260 ms dissolve (fx_rings_step lifts the arcs in its own 0-160 ms
    anticipate when it plays alone; in the sequence that lift moves here so it never shares a window with the tape arrow)"""
    al = AL_BOARD()
    tgt = al * (1 - LANES) + E.clean_empty(SK) * LANES
    k = E.e_io3(E.seg(t, 0, 260))
    return cv * (1 - k) + tgt * k


_al = {}


def AL_BOARD():
    return E.board_after_lands(SK)


def rings_setup(cv):
    FL._cache[(SK, 'p1')] = cv
    FL._cache[(SK, 'p1_empty')] = P3E
    for k in list(E._full.keys()):
        del E._full[k]


def r_rings(t, red, cv):
    box = E.FX['fx_rings_step']['_box']
    return paste(cv, box, E.rings_step_frame(t, SK, box, red))


def r_wave(t, red, cv):
    box = E.FX['fx_wave_enter']['_box']
    return paste(cv, box, E.wave_render(t, SK, red))


# the shield render, retargeted to sector 1 (angle 60): a copy of fx_eff.shield_render with A as a parameter
def make_shield(A_deg):
    def shield(t, skin, reduce=False):
        box = SH_BOX
        base = box.crop(FL.plate(skin, 'p3'))
        A = A_deg
        r_in, r_out, half = 171.0, 203.0, 24.0
        L = FL.Layer(box)
        if reduce:
            pa, tint_al, chev_al = E.shield_reduce_alpha(t)
            chev_r = [r_out + 9, r_out + 24]
            ps, impact_k = 1.0, -1
        else:
            k = FL.e_in2(FL.seg(t, 0, 240))
            chev_r = [470 - (470 - (r_out + 9)) * k, 485 - (485 - (r_out + 24)) * k]
            chev_al = 1 - FL.seg(t, 260, 320)
            pk = FL.e_back(FL.seg(t, 170, 250), 2.0)
            ps = 1.25 - 0.25 * pk
            pa = FL.seg(t, 170, 200) * (1 - FL.seg(t, 760, 920))
            tint_al = 0.18 * FL.seg(t, 240, 270) * (1 - FL.seg(t, 760, 920))
            impact_k = FL.seg(t, 240, 400)
        if tint_al > 0:
            Lt = FL.Layer(box)
            Lt.poly(FL.band_pts(64, 196, A - 29, A + 29), FL.PINK, None, 1, 255)
            base = FL.over(base, Lt.done(), tint_al)
        if pa > 0:
            rc, ac = (r_in + r_out) / 2, A

            def sc(pts):
                cx, cy = FL.ppx(rc, ac)
                return [(cx + (x - cx) * ps, cy + (y - cy) * ps) for x, y in pts]
            Lp = FL.Layer(box)
            outer = sc(FL.band_pts(r_in, r_out, A - half, A + half, 1.0))
            ins1 = sc(FL.band_pts(r_in + 4.0, r_out - 4.0, A - half + 1.6, A + half - 1.6, 1.0))
            ins2 = sc(FL.band_pts(r_in + 7.0, r_out - 7.0, A - half + 2.7, A + half - 2.7, 1.0))
            riv = sc([FL.ppx(rc, A - half + 4.5), FL.ppx(rc, A + half - 4.5)])
            E.plate_shape(Lp, outer, 1.0, riv, True, [ins1, ins2])
            if t >= 300 or reduce:
                for dd in (-2.2, 2.2):
                    Lp.line([FL.ppx(rc - 6, A + dd), FL.ppx(rc + 6, A + dd)], FL.INK, 2.2)
            lp = Lp.done()
            base = FL.over(base, FL.shadow(lp, (3, 5), 0.55 * (E.RED_SHIELD.get('shadow', 1.0) if reduce else 1.0)), pa)
            base = FL.over(base, lp, pa)
        for r_ in chev_r:
            if chev_al > 0:
                E.draw_chev(L, r_, A, 9.0, chev_al)
        if not reduce and 0 <= impact_k < 1 and t >= 240:
            E.sparks(L, FL.ppx(r_out + 2, A), A, impact_k, 6, 15.0, 1 - impact_k)
        return FL.over(base, L.done())
    return shield


SHIELD_S1 = make_shield(60.0)


def r_shield(t, red, cv):
    FL._cache[(SK, 'p3')] = cv
    return paste(cv, SH_BOX, SHIELD_S1(t, SK, red))


R1U = []


def segments():
    """(name, fx id for timings, dur_ms, renderer, setup(canvas) or None)"""
    def ph_end(fid):
        sp = E.FX.get(fid)
        if sp is not None:
            return max([sp['timing']['total']] + [p[2] for p in sp['timing']['phases']])
        fx = CD.BYID[fid]
        return max([fx['timing']['total']] + [v[1] for v in fx['timing']['phases'].values()])
    S = [
        ('commit', 'fx_commit', ph_end('fx_commit'), r_commit, None),
        ('twist', 'fx_twist', ph_end('fx_twist'), r_twist, None),
        ('trace_add', 'fx_trace_add', ph_end('fx_trace_add'), r_trace, None),
        ('trigger_hit', 'fx_trigger_hit', ph_end('fx_trigger_hit'), cd_render('fx_trigger_hit', d_trigger_hit_seq), None),
        ('refund', 'fx_refund', ph_end('fx_refund'), r_refund_factory(), None),
        ('gun_hit', 'fx_gun_hit', ph_end('fx_gun_hit'), cd_render('fx_gun_hit'), None),
        ('kill', 'fx_kill', ph_end('fx_kill'), cd_render('fx_kill', post=P3K), None),
        ('ricochet_gold', 'fx_ricochet_gold', ph_end('fx_ricochet_gold'), cd_render('fx_ricochet_gold'), None),
        ('shield_block', 'fx_shield_block', ph_end('fx_shield_block'), r_shield, None),
        ('soak_take', 'fx_soak_take', ph_end('fx_soak_take'), mp_render('fx_soak_take'), None),
        ('brace_block', 'fx_brace_block', ph_end('fx_brace_block'), mp_render('fx_brace_block'), None),
        ('clear', 'fx_clear', ph_end('fx_clear'), cd_render('fx_clear'), None),
        ('settle', None, 260, r_settle, rings_setup),
        ('rings_step', 'fx_rings_step', ph_end('fx_rings_step'), r_rings, rings_setup),
        ('wave_enter', 'fx_wave_enter', ph_end('fx_wave_enter'), r_wave, 'keep'),
    ]
    out = []
    t0 = 0
    for nm, fid, dur, r, setup in S:
        out.append(dict(name=nm, fid=fid, start=t0, dur=int(dur), render=r, setup=setup))
        t0 += int(dur) + GAP_AFTER.get(nm, GAP)
    return out


SEGS = None


def init():
    global SEGS, R1U
    R1U = ring1_units()
    SEGS = segments()
    return SEGS


def total_ms():
    s = SEGS[-1]
    return s['start'] + s['dur'] + 300
