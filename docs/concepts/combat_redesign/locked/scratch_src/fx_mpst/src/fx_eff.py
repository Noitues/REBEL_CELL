"""fx_eff: the M (motion), P (protect), S (system) and T (commit) effects rebuilt on the final locked board.
Every effect: render(t_ms, skin, reduce) -> crop RGB float array.  Timings live in each spec (ms) and go to timings_MPST.json."""
import math, copy
import numpy as np
from scipy import ndimage as ndi
from fxlib import *

FX = {}


def reg(spec):
    FX[spec['id']] = spec
    return spec


# ============================================================================ full-plate helpers (cached per skin)
_full = {}
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
FRHO = np.hypot(XX - C[0], YY - C[1])
FANG = np.degrees(np.arctan2(XX - C[0], -(YY - C[1]))) % 360


def hsv_np(a):
    mx, mn = a.max(2), a.min(2)
    s = (mx - mn) / np.maximum(mx, 1)
    dd = np.maximum(mx - mn, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return h, s, mx / 255.0


def pinkish(a):
    h, s, v = hsv_np(a)
    return (h > 295) & (h < 345) & (s > 0.45) & (v > 0.45)


def unit_alpha(skin):
    """full-plate alpha of everything the units add on the rings (cells, tokens, trays, badges, chevrons): p1 vs p1_empty.
    pink pixels (the Cell's gun marks) never belong to a unit."""
    k = ('ua', skin)
    if k in _full:
        return _full[k]
    full, emp = plate(skin, 'p1'), plate(skin, 'p1_empty')
    d = np.abs(full - emp).max(2)
    m = (d > 14) & ~pinkish(full) & (FRHO > 210.5) & (FRHO < 389.5)
    m = ndi.binary_closing(m, iterations=1)
    m = ndi.binary_dilation(m, iterations=1)
    a = ndi.gaussian_filter(m.astype(np.float32), 0.6)
    a = np.clip(a * 1.25, 0, 1) * ((FRHO > 210.5) & (FRHO < 389.5))
    _full[k] = a
    return a


def clean_empty(skin):
    """p1_empty with its own gun marks removed (r 196-280): the guns have fired and the board is between beats"""
    k = ('ce', skin)
    if k in _full:
        return _full[k]
    emp = plate(skin, 'p1_empty').copy()
    g = pinkish(emp) & (FRHO > 196) & (FRHO < 285)
    # the gun starburst has a white core: take near-white pixels touching pink as well
    wh = (emp.min(2) > 200) & (FRHO > 196) & (FRHO < 285)
    g = ndi.binary_dilation(g, iterations=4)
    g = g | (wh & ndi.binary_dilation(g, iterations=6))
    g = ndi.binary_dilation(g, iterations=2)
    ys, xs = np.nonzero(g)
    rho, ang = FRHO[ys, xs], FANG[ys, xs] - 60.0
    sx, sy = C[0] + rho * np.sin(np.radians(ang)), C[1] - rho * np.cos(np.radians(ang))
    for c in range(3):
        emp[ys, xs, c] = ndi.map_coordinates(emp[..., c], [sy, sx], order=1, mode='nearest')
    _full[k] = emp
    return emp


def board_after_lands(skin):
    """the decide board once guns and landings are done: ring 0 cleared, gun marks gone, tower and the rest as p1"""
    k = ('al', skin)
    if k in _full:
        return _full[k]
    full = plate(skin, 'p1').copy()
    ce = clean_empty(skin)
    m = ((FRHO > 196.5) & (FRHO < 272.0)).astype(np.float32)
    m = ndi.gaussian_filter(m, 0.7)
    out = full * (1 - m[..., None]) + ce * m[..., None]
    # gun lines that still cross the tower gap and ring 1 edges in the full plate
    g = pinkish(full) & (FRHO > 196) & (FRHO < 285)
    g = ndi.binary_dilation(g, iterations=3)
    out[g] = ce[g]
    _full[k] = out
    return out


def sample_full(img, box, srho, sang):
    xs, ys = polar_src(box, srho, sang)
    return sample(img, xs, ys)


def sample_alpha(a, box, srho, sang):
    xs, ys = polar_src(box, srho, sang)
    return ndi.map_coordinates(a, [ys, xs], order=1, mode='constant', cval=0.0).astype(np.float32)


def move_layer(base, skin, box, region, d_ang=0.0, d_r=0.0, echoes=(), tint=None, src=None, ua=None):
    """slide the unit pixels inside `region` (full-plate float mask) by (d_r, d_ang) over `base` (crop).
    echoes: list of (d_r, d_ang, alpha) ghost copies drawn first, tinted toward `tint` by 35 %."""
    src = plate(skin, 'p1') if src is None else src
    ua = unit_alpha(skin) if ua is None else ua
    a_full = ua * region
    out = base.copy()
    for (er, ea, al) in list(echoes) + [(d_r, d_ang, 1.0)]:
        srho = np.maximum(box.RHO - er, 0)
        sang = box.ANG - ea
        al_ = sample_alpha(a_full, box, srho, sang) * al
        if al_.max() <= 0.002:
            continue
        rgb = sample_full(src, box, srho, sang)
        if tint is not None and al < 1.0:
            rgb = rgb * 0.75 + np.array(tint, np.float32) * 0.25
        out = out * (1 - al_[..., None]) + rgb * al_[..., None]
    return out


def sector_region(dep_r0, dep_r1, a0, a1, pad_r=3.0, pad_a=0.6):
    m = ((FRHO > dep_r0 - pad_r) & (FRHO < dep_r1 + pad_r)).astype(np.float32)
    span = (a1 - a0 + 2 * pad_a) % 360
    inside = ((FANG - (a0 - pad_a)) % 360) <= span
    return m * inside


ECHO_A = (0.55, 0.34, 0.17)
ECHO_LAG = (26, 52, 78)
ECHO_U = (0.42, 0.26, 0.13)


def edge_echoes(cur, ghosts, mask, sp, tint=PINK):
    """stroboscopic echoes of a turning disc / ring: each ghost shows only where it differs from the current frame
    (its edges, icons and marks), tinted 25 % toward the motion colour, at 55 / 34 / 17 % x speed."""
    out = cur
    for gh, al in zip(ghosts, ECHO_A):
        dif = np.clip(np.abs(gh - cur).max(2) / 90.0, 0, 1)
        g = gh * 0.75 + np.array(tint, np.float32) * 0.25
        out = mix(out, g, mask * dif * al * sp)
    return out


def echo_set(val_fn, t, lags=(26, 52, 78), alphas=(0.42, 0.26, 0.13), speed=1.0):
    """echo copies at the positions the motion had `lag` ms earlier; alpha scaled by the motion speed (0..1)"""
    return [(val_fn(t - lg), a * speed) for lg, a in zip(lags, alphas)]


def speed_of(fn, t, scale):
    v = abs(fn(t + 8) - fn(t - 8)) / 16.0
    return clamp01(v / scale)


# ============================================================================ M: spin (Spin 3 turns the tower)
ICON_R, ICON_DISC = 121.0, 37.5


def spin_ang(t, reduce=False):
    if t < 140:
        return 0.0
    if t < 680:
        return 183.0 * e_io3(seg(t, 140, 680))
    return 183.0 - 3.0 * e_out3(seg(t, 680, 820))


def spin_render(t, skin, reduce=False):
    s = FX['fx_spin']
    box = s['_box']
    p0, p1 = plate(skin, 'p1'), plate(skin, 'p1_noguns')
    base = mix(box.crop(p0), box.crop(p1), e_out3(seg(t, 0, 120)))
    rmask = ring_mask(box, 63.5, 209.0, feather=1.2)

    def tower_at(d, img):
        r = rotated(img, box, d)
        # icons stay upright: an unrotated disc of each slice icon at its new centre
        for k in range(6):
            a_new = 60 * k + d
            cx, cy = ppx(ICON_R, a_new)
            ox, oy = ppx(ICON_R, 60 * k)
            dx, dy = ox - cx, oy - cy
            m = np.clip((ICON_DISC - np.hypot(box.X - cx, box.Y - cy)) / 1.2 + 0.5, 0, 1)
            if m.max() <= 0:
                continue
            up = sample(img, box.X + dx, box.Y + dy)
            r = r * (1 - m[..., None]) + up * m[..., None]
        return r

    if reduce:
        k = e_io3(seg(t, 140, 420))
        a0 = tower_at(0.0, p1)
        a1 = tower_at(180.0, p1)
        tw = mix(a0, a1, k)
        out = mix(base, tw, rmask)
    else:
        d = spin_ang(t)
        tw = tower_at(d, p1)
        out = mix(base, tw, rmask)
        sp = speed_of(spin_ang, t, 0.55)
        if sp > 0.02:
            out = edge_echoes(out, [tower_at(spin_ang(t - lag), p1) for lag in (9, 18, 27)], rmask, sp * 0.8)
    # the pink arrowed arc: just inside ring 0, clear of the pink scissor halo
    L = Layer(box)
    R_ = 220.0
    if reduce:
        al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 420, 560))
        if al > 0:
            arrow(L, arc_pts(R_, 6, 180), PINK, 5.0, 15.0, 4.0, int(255 * al))
    else:
        if t < 680:
            head = 6 + 174 * e_out3(seg(t, 0, 140))
            tail = 6 + spin_ang(t)
            if head - tail > 4:
                arrow(L, arc_pts(R_, tail, head), PINK, 5.0, 15.0, 4.0)
        else:
            al = 1 - seg(t, 680, 820)
            if al > 0:
                pass
    lay = L.done()
    out = over(out, lay)
    return out


reg(dict(id='fx_spin', fam='M', title='Spin 3 turns the tower', skins=['neutral'], box=(316, 320, 756, 760), scale=0.9,
         src='f1 hand: Spin 3 ("Turn the tower 3", cost 1): the tower turns 3 sectors (180 deg) clockwise',
         still='The tower annulus (r 64-209) turns 180 deg; the hub (BREAKER, HP ring) stays put and every slice icon stays upright; a pink arrowed arc in the gap between the tower and ring 0 is eaten by the turning slice 0; three pink-tinted echoes trail while it moves.',
         keep='pink arrowed arc (resolve colour), three echoes only while moving, icons upright at rest, hub never turns.',
         timing=dict(phases=[('anticipate: arrow draws, gun preview fades', 0, 140, 'easeOutCubic'), ('turn 183 deg', 140, 680, 'easeInOutCubic'),
                             ('settle back 3 deg, arrow gone', 680, 820, 'easeOutCubic')], total=820),
         keys=[(0, 'rest'), (100, 'arrow draws'), (330, 'turning, echoes'), (480, 'peak speed'), (680, 'overshoot'), (820, 'settled')],
         reduce_note='No echoes, no arc sweep: the arrow appears whole (100 ms fade), the tower dissolves from 0 to 180 deg over 280 ms (easeInOut), the arrow fades out. Icons and hub as in full motion.',
         notes='The gun preview marks fade in the anticipate beat: they aim from the old slice positions and the board re-solves them after the turn (not part of the effect).',
         render=spin_render))


# ============================================================================ M: twist (ring +1 turns one sector)
def twist_ang(t):
    if t < 120:
        return 0.0
    if t < 540:
        return 61.5 * e_io3(seg(t, 120, 540))
    return 61.5 - 1.5 * e_out3(seg(t, 540, 660))


def twist_render(t, skin, reduce=False):
    box = FX['fx_twist']['_box']
    p = plate(skin, 'p1')
    base = box.crop(p)
    rm = ring_mask(box, 270.5, 328.5, feather=1.0)
    if reduce:
        k = e_io3(seg(t, 120, 380))
        out = mix(base, mix(rotated(p, box, 0), rotated(p, box, 60), k), rm)
    else:
        d = twist_ang(t)
        out = mix(base, rotated(p, box, d), rm)
        sp = speed_of(twist_ang, t, 0.20)
        if sp > 0.02:
            out = edge_echoes(out, [rotated(p, box, twist_ang(t - lag)) for lag in ECHO_LAG], rm, sp)
    L = Layer(box)
    for c0 in (210.0, 0.0):            # unit 4 Payload (s3-4, centre 210), unit 5 Packet (s0, centre 0)
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 380, 520))
            if al > 0:
                arrow(L, arc_pts(299.5, c0 + 4, c0 + 60), PINK, 5.0, 15.0, 4.0, int(255 * al))
        elif t < 600:
            head = c0 + 4 + 56 * e_out3(seg(t, 0, 120))
            tail = c0 + 4 + twist_ang(t)
            al = 1 - seg(t, 540, 600)
            if head - tail > 3 and al > 0:
                arrow(L, arc_pts(299.5, tail, head), PINK, 5.0, 15.0, 4.0, int(255 * al))
    return over(out, L.done())


reg(dict(id='fx_twist', fam='M', title='Twist turns ring +1 by a sector', skins=['neutral', 'solace', 'meridian'], box=(36, 40, 560, 1040), scale=0.5,
         src='f2 played Twist [1, 1] (ring 1, one sector clockwise; "Turn one ring 1", cost 0); drawn on the decide board f1',
         still='Ring +1 (r 271-328) turns 60 deg clockwise with its cells, tokens and ring tag; each unit on it gets a pink arrowed arc one sector long that the cell eats as it turns; three pink-tinted echoes while moving. The corp ring material turns with the ring.',
         keep='pink arrowed arc along the ring, one sector; echoes while moving only; the hover form (preview) is the same arrow in pencil yellow (hover plates).',
         timing=dict(phases=[('anticipate: arrows draw', 0, 120, 'easeOutCubic'), ('turn 61.5 deg', 120, 540, 'easeInOutCubic'), ('settle back 1.5 deg', 540, 660, 'easeOutCubic')], total=660),
         keys=[(0, 'rest'), (110, 'arrows drawn'), (280, 'turning'), (400, 'echoes'), (540, 'overshoot'), (660, 'settled')],
         reduce_note='No echoes: the arrows appear whole (100 ms), the ring dissolves from 0 to 60 deg over 260 ms, the arrows fade.',
         notes='The landing arcs on the outer lanes are not moved by the effect; they re-solve when the board redraws after it.',
         render=twist_render))


# ============================================================================ M: pull (a unit one ring inward)
PULL_REG = None


def pull_dr(t):
    if t < 120:
        return 0.0
    if t < 480:
        return -59.0 * e_io3(seg(t, 120, 480))
    return -59.0 + 2.0 * e_out3(seg(t, 480, 600))


def pull_render(t, skin, reduce=False):
    box = FX['fx_pull']['_box']
    p = plate(skin, 'p1')
    reg_ = sector_region(328, 385, 270, 330)
    regc = box.crop(reg_[..., None])[..., 0]
    emp = plate(skin, 'p1_empty')
    ua = unit_alpha(skin)
    hole = box.crop((ua * reg_)[..., None])[..., 0]
    base0 = box.crop(p)
    base = mix(base0, box.crop(emp), hole)
    if reduce:
        k = e_io3(seg(t, 120, 380))
        a = move_layer(base, skin, box, reg_, 0, 0)
        b = move_layer(base, skin, box, reg_, d_r=-57.0)
        out = mix(a, b, k)
    else:
        dr = pull_dr(t)
        sp = speed_of(pull_dr, t, 0.18)
        ech = [(pull_dr(t - lg), 0.0, al * sp) for lg, al in zip((26, 52, 78), ECHO_U)] if sp > 0.02 else []
        out = move_layer(base, skin, box, reg_, d_r=dr, echoes=ech, tint=PINK)
    L = Layer(box)
    if reduce:
        al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 380, 520))
        if al > 0:
            arrow(L, [ppx(372, 300), ppx(284, 300)], PINK, 5.0, 15.0, 4.0, int(255 * al))
    elif t < 560:
        head = 372 - 88 * e_out3(seg(t, 0, 120))
        tail = 372 + pull_dr(t)
        al = 1 - seg(t, 480, 560)
        if tail - head > 3 and al > 0:
            arrow(L, [ppx(tail, 300), ppx(head, 300)], PINK, 5.0, 15.0, 4.0, int(255 * al))
    return over(out, L.done())


reg(dict(id='fx_pull', fam='M', title='Pull drags a unit inward', skins=['neutral', 'solace', 'meridian'], box=(110, 150, 530, 570), scale=0.85,
         src='card Pull ("Pull a unit in", cost 0, loud 1): shown on Packet 7 (ring +2, sector 5) into the empty ring +1 sector 5 of f1',
         still='The whole cell (wash, token, tray) slides 57 px inward along the sector axis behind three pink-tinted echoes; a pink radial arrow from the cell to its new ring is eaten as the cell moves.',
         keep='pink arrow pointing inward (resolve colour); echoes only while moving; the hover form is pencil yellow.',
         timing=dict(phases=[('anticipate: arrow draws', 0, 120, 'easeOutCubic'), ('slide 59 px', 120, 480, 'easeInOutCubic'), ('settle back 2 px', 480, 600, 'easeOutCubic')], total=600),
         keys=[(0, 'rest'), (110, 'arrow drawn'), (250, 'sliding'), (330, 'echoes'), (480, 'overshoot'), (600, 'settled')],
         reduce_note='No echoes: arrow appears (100 ms), the cell dissolves from ring +2 to ring +1 over 260 ms, arrow fades.',
         notes='Pull is loud: its +1 Trace plays fx_trace_add after this. The moved cell keeps its FAR grade until the board redraws in the new ring\'s COLD grade.',
         render=pull_render))


# ============================================================================ M: shove (a unit one sector sideways)
def shove_ang(t):
    if t < 120:
        return 0.0
    if t < 460:
        return 62.0 * e_io3(seg(t, 120, 460))
    return 62.0 - 2.0 * e_out3(seg(t, 460, 580))


def shove_render(t, skin, reduce=False):
    box = FX['fx_shove']['_box']
    p = plate(skin, 'p1')
    reg_ = sector_region(271, 328, -30, 30)
    emp = plate(skin, 'p1_empty')
    ua = unit_alpha(skin)
    hole = box.crop((ua * reg_)[..., None])[..., 0]
    base = mix(box.crop(p), box.crop(emp), hole)
    if reduce:
        k = e_io3(seg(t, 120, 380))
        out = mix(move_layer(base, skin, box, reg_, 0, 0), move_layer(base, skin, box, reg_, d_ang=60.0), k)
    else:
        d = shove_ang(t)
        sp = speed_of(shove_ang, t, 0.20)
        ech = [(0.0, shove_ang(t - lg), al * sp) for lg, al in zip((26, 52, 78), ECHO_U)] if sp > 0.02 else []
        out = move_layer(base, skin, box, reg_, d_ang=d, echoes=ech, tint=PINK)
    L = Layer(box)
    if reduce:
        al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 380, 520))
        if al > 0:
            arrow(L, arc_pts(299.5, 4, 60), PINK, 5.0, 15.0, 4.0, int(255 * al))
    elif t < 540:
        head = 4 + 56 * e_out3(seg(t, 0, 120))
        tail = 4 + shove_ang(t)
        al = 1 - seg(t, 460, 540)
        if head - tail > 3 and al > 0:
            arrow(L, arc_pts(299.5, tail, head), PINK, 5.0, 15.0, 4.0, int(255 * al))
    return over(out, L.done())


reg(dict(id='fx_shove', fam='M', title='Shove slides a unit one sector', skins=['neutral', 'solace', 'meridian'], box=(370, 130, 900, 500), scale=0.8,
         src='card Shove ("Slide a unit 1", cost 2, loud 2): shown on Packet 5 (ring +1, sector 0) into the empty sector 1 of f1',
         still='The cell slides one sector clockwise along its ring behind three pink-tinted echoes; a pink arrowed arc one sector long is eaten as it moves.',
         keep='pink arrowed arc along the ring; echoes only while moving; the hover form is pencil yellow.',
         timing=dict(phases=[('anticipate: arrow draws', 0, 120, 'easeOutCubic'), ('slide 62 deg', 120, 460, 'easeInOutCubic'), ('settle back 2 deg', 460, 580, 'easeOutCubic')], total=580),
         keys=[(0, 'rest'), (110, 'arrow drawn'), (250, 'sliding'), (330, 'echoes'), (460, 'overshoot'), (580, 'settled')],
         reduce_note='No echoes: arrow appears (100 ms), the cell dissolves into the next sector over 260 ms, arrow fades.',
         notes='Shove into an occupied cell: see the variant fx_shove_bump below.',
         render=shove_render))


def bump_ang(t):
    if t < 120:
        return 0.0
    if t < 260:
        return -7.0 * e_in2(seg(t, 120, 260))
    k = seg(t, 260, 440)
    return -7.0 * (1 - e_out3(k)) + 1.5 * math.sin(math.pi * k) * (1 - k)


def starburst(L, p, r, al=1.0, n=10):
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.48
        pts.append((p[0] + rr * math.sin(a), p[1] - rr * math.cos(a)))
    L.poly(pts, PINK, INK, 2.4, int(255 * al))
    L.circle(p, r * 0.32, fill=WHITE, a=int(255 * al))


def bump_render(t, skin, reduce=False):
    box = FX['fx_shove_bump']['_box']
    p = plate(skin, 'p1')
    reg_ = sector_region(328, 385, 270, 330)
    emp = plate(skin, 'p1_empty')
    ua = unit_alpha(skin)
    hole = box.crop((ua * reg_)[..., None])[..., 0]
    base = mix(box.crop(p), box.crop(emp), hole)
    if reduce:
        out = move_layer(base, skin, box, reg_)
    else:
        d = bump_ang(t)
        sp = speed_of(bump_ang, t, 0.12)
        ech = [(0.0, bump_ang(t - lg), al * sp) for lg, al in zip((26, 52, 78), ECHO_U)] if sp > 0.02 and t < 260 else []
        out = move_layer(base, skin, box, reg_, d_ang=d, echoes=ech, tint=PINK)
    L = Layer(box)
    # the pink arrow says where the card tried to slide it; it stops at the shared edge
    al = (e_out3(seg(t, 0, 100)) if reduce else e_out3(seg(t, 0, 120))) * (1 - seg(t, 440, 540))
    if al > 0:
        head = 296 - 22 * (1.0 if reduce else e_out3(seg(t, 0, 120)))
        arrow(L, arc_pts(356.5, 296, head), PINK, 5.0, 15.0, 4.0, int(255 * al))
    # contact: white bump line along the shared edge (270 deg) and two keylined pink starbursts, shards
    k = 0.6 if reduce else seg(t, 260, 400)
    if (reduce and t >= 0) or (0 <= k < 1 and t >= 260):
        fade = 1 - seg(t, 440, 540) if reduce else 1 - k ** 2
        L.line([ppx(331, 270), ppx(382, 270)], INK, 6.0, int(255 * fade))
        L.line([ppx(331, 270), ppx(382, 270)], WHITE, 2.6, int(255 * fade))
        if not reduce:
            s_ = 0.6 + 0.6 * e_out3(min(1, k * 2.5))
            for rr in (342, 371):
                starburst(L, ppx(rr, 270), 13.0 * s_, fade)
            for i, (dr, da) in enumerate(((-14, -5), (12, -6), (-6, 6), (16, 5))):
                q = 6 + 22 * e_out3(k)
                c = ppx(356 + dr * k * 1.4, 270 + da * k * 1.2)
                L.poly([(c[0] - 2.5, c[1] - 1), (c[0] + 2.5, c[1] - 2), (c[0], c[1] + 3)], WHITE, INK, 1.0, int(255 * fade))
    return over(out, L.done())


reg(dict(id='fx_shove_bump', fam='M', title='Shove collision (variant of fx_shove)', skins=['neutral', 'solace', 'meridian'], box=(90, 330, 430, 640), scale=1.0,
         src='card Shove into an occupied cell: shown on Packet 7 (ring +2, sector 5) shoved anticlockwise into Packet 6 (sectors 2-4) on f1. Registered as a D (damage) effect in the round-2 source; drawn here under its parent because no D sheet carries it',
         still='The pink arrow shows the slide the card asked for; the cell starts to slide, hits the shared edge, a white bump line and two small keylined pink starbursts sit on the edge with white shards, and the cell springs back into its own sector.',
         keep='the pink starbursts sit on the shared edge only (D material, small); the cell ends in its own sector; no hatch is drawn by the effect (the board shows any HP tick lost).',
         timing=dict(phases=[('anticipate: arrow draws', 0, 120, 'easeOutCubic'), ('slide toward the edge', 120, 260, 'easeInQuad'), ('contact: bump line, starbursts, shards', 260, 400, 'easeOutCubic'),
                             ('spring back', 260, 440, 'easeOutCubic + 2 deg wobble'), ('arrow and bump line fade', 440, 540, 'linear')], total=540),
         keys=[(0, 'rest'), (110, 'arrow drawn'), (230, 'sliding'), (280, 'contact'), (340, 'spring back'), (540, 'settled')],
         reduce_note='No slide and no starbursts: the arrow and the white bump line on the shared edge appear for 440 ms and fade; the cell never moves.',
         notes='Round 2 stated that both units lose a tick on a bump; that rule is not in the E10 state, so the effect draws no HP change (open point for the designer).',
         render=bump_render))


# ============================================================================ M: rings step (END TURN: one ring in, the live schedule turn)
def step_k(t):
    return e_io3(seg(t, 160, 760))


def rings_step_frame(t, skin, box, reduce=False, with_arrow=True):
    p = plate(skin, 'p1')
    al_board = board_after_lands(skin)
    ce = clean_empty(skin)
    ua = unit_alpha(skin)
    reg_ = ((FRHO > 268.0) & (FRHO < 389.5)).astype(np.float32)        # rings +1 and +2 move; ring 0 has landed
    # the landing arcs on the lanes lift off (they are the old predictions)
    lanes = ((FRHO > 425) & (FRHO < 482)).astype(np.float32)
    start = al_board
    start_c = box.crop(start)
    arcs_off = mix(start_c, box.crop(ce), box.crop(lanes[..., None])[..., 0])
    base = mix(start_c, arcs_off, e_out3(seg(t, 0, 160)))
    hole = box.crop((ua * reg_)[..., None])[..., 0]
    base = mix(base, box.crop(ce), hole)
    if reduce:
        k = e_io3(seg(t, 160, 460))
        out = mix(move_layer(base, skin, box, reg_, 0, 0, ua=ua), move_layer(base, skin, box, reg_, d_ang=120.0, d_r=-57.0, ua=ua), k)
    else:
        k = step_k(t)
        sp = speed_of(step_k, t, 0.0028)
        ech = [(-57.0 * step_k(t - lg), 120.0 * step_k(t - lg), al * sp) for lg, al in zip((26, 52, 78), ECHO_U)] if sp > 0.02 else []
        out = move_layer(base, skin, box, reg_, d_r=-57.0 * k, d_ang=120.0 * k, echoes=ech, tint=SILVER, ua=ua)
    if with_arrow:
        L = Layer(box)
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 460, 600))
            if al > 0:
                silver_arrow(L, arc_pts(426.5, 3, 117), 5.0, 15.0, int(255 * al))
        else:
            head = 3 + 114 * e_out3(seg(t, 0, 160))
            tail = 3 + 114 * step_k(t)
            al = 1 - seg(t, 760, 900)
            if head - tail > 3 and al > 0:
                silver_arrow(L, arc_pts(426.5, tail, head), 5.0, 15.0, int(255 * al))
            # a short silver inward chevron on each moving cell while it travels (the clock moves them, not the Cell)
        out = over(out, L.done())
    return out


def rings_step_render(t, skin, reduce=False):
    return rings_step_frame(t, skin, FX['fx_rings_step']['_box'], reduce)


reg(dict(id='fx_rings_step', fam='M', title='Rings step in at END TURN', skins=['neutral', 'solace', 'meridian'], box=(36, 40, 1036, 1040), scale=0.46,
         src='f1 schedule [2, 0, 0]: at END TURN every unit comes one ring in and the live +2 turns it 2 sectors (120 deg) clockwise (Packet 5: s0 lands on 2, Packet 7: s5 lands on 1, both match the state)',
         still='After GUNS and LANDS (ring 0 is clear): a silver arrow runs the length of the +2 THIS TURN tape; every unit cell on rings +1 and +2 spirals one ring in and 120 deg round behind three silver-tinted echoes, the arrow being eaten as they go.',
         keep='silver only (the clock = the THIS TURN tape stock, never pink and never the corp colour); echoes while moving; the hand-off order GUNS > LANDS > RINGS STEP.',
         timing=dict(phases=[('anticipate: tape arrow draws, landing arcs lift off', 0, 160, 'easeOutCubic'), ('spiral: -57 px, +120 deg', 160, 760, 'easeInOutCubic'),
                             ('settle: arrow fades', 760, 900, 'linear')], total=900),
         keys=[(0, 'after LANDS'), (150, 'tape arrow'), (360, 'spiral'), (460, 'peak speed'), (620, 'arriving'), (900, 'settled')],
         reduce_note='No echoes, no spiral: the arrow appears (100 ms), every cell dissolves from its old place to its new one over 300 ms, the arrow fades.',
         notes='The moved cells keep their old HOT/COLD/FAR grade and the schedule tape keeps its cells until the board redraws for the next turn; the landing arcs re-solve then. Ring +2 is left empty for fx_wave_enter.',
         render=rings_step_render))


# ============================================================================ M: hold (a 0 put in the live schedule cell)
def hold_render(t, skin, reduce=False):
    box = FX['fx_hold']['_box']
    p0, p1 = plate(skin, 'p1'), plate(skin, 'p1_hold')
    base = box.crop(p0)
    end = box.crop(p1)
    bandm = ring_mask(box, 382, 430, feather=1.0)
    stamp_xy = ppx(404.0, 7.2)
    L = Layer(box)
    if reduce:
        k = e_io3(seg(t, 0, 260))
        out = mix(base, mix(base, end, k), bandm)
        al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 540))
        if al > 0:
            silver_arrow(L, arc_pts(426.5, 12, 50), 5.0, 15.0, int(255 * al))
        return over(out, L.done())
    # wipe front clockwise from 0 to 205 deg (the band from the live cell to the end of HOLD THEN)
    front = 205.0 * e_io3(seg(t, 140, 560))
    soft = 5.0
    a_rel = box.ANG % 360
    wipe = np.clip((front - a_rel) / soft + 0.5, 0, 1) * (a_rel < 230)
    out = mix(base, end, bandm * wipe)
    # front edge: a silver foil sliver on the band (the clock turning the cells over)
    if 2 < front < 203:
        L.poly(band_pts(386, 424, front - 1.2, front + 0.4, 0.4), SILVER, INK, 1.4, int(255 * (1 - seg(t, 540, 560))))
    # the stamp slams onto the live cell
    if t >= 0:
        k = e_back(seg(t, 0, 140), 2.2)
        s = 1.6 - 0.6 * k
        al = clamp01(seg(t, 0, 60)) * (1 - seg(t, 560, 700))
        if al > 0:
            R0 = 14.5 * s
            L.circle((stamp_xy[0] + 2.5, stamp_xy[1] + 3.5), R0 + 1.5, fill=INK, a=int(140 * al))
            L.circle(stamp_xy, R0 + 1.5, fill=INK, a=int(255 * al))
            L.circle(stamp_xy, R0, fill=SILVER, a=int(255 * al))
            L.circle(stamp_xy, R0 - 3.0, outline=SILVER_D, w=1.2, a=int(255 * al))
            hx, hy = stamp_xy
            q = 7.0 * s
            L.poly([(hx - q, hy - q), (hx + q, hy - q), (hx, hy), (hx + q, hy + q), (hx - q, hy + q), (hx, hy)], INK, None, 1, int(255 * al))
            L.line([(hx - q - 1.5, hy - q), (hx + q + 1.5, hy - q)], INK, 2.0, int(255 * al))
            L.line([(hx - q - 1.5, hy + q), (hx + q + 1.5, hy + q)], INK, 2.0, int(255 * al))
    # the +2 slides one slot later: silver arrow from the live cell to the new +2 start (40 deg on)
    if 140 <= t < 700:
        head = 12 + 38 * e_out3(seg(t, 140, 300))
        al = 1 - seg(t, 560, 700)
        silver_arrow(L, arc_pts(426.5, 12, head), 5.0, 15.0, int(255 * al))
    return over(out, L.done())


reg(dict(id='fx_hold', fam='M', title='Hold puts a 0 in the schedule', skins=['neutral', 'solace', 'meridian'], box=(380, 50, 1036, 990), scale=0.46,
         src='card Hold ("Pause the wave", cost 0): f1 schedule [2, 0, 0] becomes [0, 2, 0]; the end state is the generator\'s own render of [0, 2, 0]',
         still='A silver hourglass stamp slams onto the live cell; a silver arrow runs one hold slot (40 deg) along the tape; the band turns over clockwise behind a silver foil edge into the new schedule (HOLD THIS TURN, +2 NEXT, HOLD THEN).',
         keep='silver stamp and arrow (the tape stock), the hourglass glyph; the turned-over cells are the generator\'s own schedule drawing.',
         timing=dict(phases=[('stamp slams', 0, 140, 'easeOutBack 2.2'), ('band turns over 205 deg', 140, 560, 'easeInOutCubic'), ('settle: stamp hands over to the printed HOLD glyph', 560, 700, 'linear')], total=700),
         keys=[(0, 'rest'), (70, 'stamp'), (250, 'arrow, wipe'), (400, 'turning over'), (560, 'turned'), (700, 'settled')],
         reduce_note='No stamp slam and no wipe: the arrow appears (100 ms) and the band dissolves to the new schedule over 260 ms.',
         notes='Only the schedule band (r 382-430) changes; the rest of the board is the decide plate.',
         render=hold_render))


# ============================================================================ M: wave enter (W4 ticket into ring +2)
TICKETS = {'W6': (24, 24, 109, 89), 'W5': (115, 24, 201, 89), 'W4': (207, 24, 293, 89)}
W4_CELLS = [(0, 1), (4, 2)]            # lineup W4: Jammer w1 s0, Jammer w2 s4


def _ticket_sprite(skin, name):
    p = plate(skin, 'p1')
    x0, y0, x1, y1 = TICKETS[name]
    return p[y0:y1, x0:x1].copy()


def _paste_sprite(out, box, spr, cx, cy, s=1.0, al=1.0, tint=None, tk=0.35):
    h, w = spr.shape[:2]
    # inverse map of a scale-about-centre
    xs = (box.X - cx) / s + w / 2.0
    ys = (box.Y - cy) / s + h / 2.0
    m = (xs >= 0) & (xs <= w - 1) & (ys >= 0) & (ys <= h - 1)
    if not m.any():
        return out
    rgb = np.empty(box.X.shape + (3,), np.float32)
    for c in range(3):
        rgb[..., c] = ndi.map_coordinates(spr[..., c], [ys, xs], order=1, mode='nearest')
    if tint is not None:
        rgb = rgb * (1 - tk) + np.array(tint, np.float32) * tk
    edge = np.clip(np.minimum.reduce([xs + 0.5, w - 0.5 - xs, ys + 0.5, h - 0.5 - ys]), 0, 1)
    a = edge * m * al
    return out * (1 - a[..., None]) + rgb * a[..., None]


def wave_render(t, skin, reduce=False):
    box = FX['fx_wave_enter']['_box']
    # the board this starts from: rings_step's settled frame
    ck = ('wave_base', skin, box.x0, box.y0)
    if ck not in _full:
        _full[ck] = rings_step_frame(900, skin, box, False, with_arrow=False)
    base = _full[ck]
    p = plate(skin, 'p1')
    col = CORP_PRI[skin]
    # queue area background (under the tickets): the room plate has no ticket-free version, so a vacated slot is drawn as an empty slot
    L = Layer(box)
    w4 = _ticket_sprite(skin, 'W4')
    w5 = _ticket_sprite(skin, 'W5')
    w6 = _ticket_sprite(skin, 'W6')
    out = base.copy()

    def blank(name, al=1.0):
        x0, y0, x1, y1 = TICKETS[name]
        L2_ = Layer(box)
        L2_.d.rounded_rectangle([(x0 - box.x0) * 3, (y0 - box.y0) * 3, (x1 - box.x0) * 3, (y1 - box.y0) * 3], radius=12, fill=(14, 16, 24, int(235 * al)),
                                outline=(70, 78, 94, int(255 * al)), width=4)
        return L2_.done()

    entry = ppx(486, -19.5)
    cx4, cy4 = (TICKETS['W4'][0] + TICKETS['W4'][2]) / 2, (TICKETS['W4'][1] + TICKETS['W4'][3]) / 2
    path = [(cx4, cy4), (cx4 + 60, cy4 + 6), (entry[0] - 12, entry[1] - 18), entry]
    if reduce:
        k = e_io3(seg(t, 120, 420))
        for nm in ('W4', 'W5', 'W6'):
            out = over(out, blank(nm, k))
        out = _paste_sprite(out, box, w4, cx4, cy4, 1.0, 1 - k)
        out = _paste_sprite(out, box, w5, cx4, cy4, 1.0, k)
        out = _paste_sprite(out, box, w6, (TICKETS['W5'][0] + TICKETS['W5'][2]) / 2, cy4, 1.0, k)
        out = _paste_sprite(out, box, w5, (TICKETS['W5'][0] + TICKETS['W5'][2]) / 2, cy4, 1.0, 1 - k)
        out = _paste_sprite(out, box, w6, (TICKETS['W6'][0] + TICKETS['W6'][2]) / 2, cy4, 1.0, 1 - k)
        cells_k = k
    else:
        # feed arrow lights (corp enamel), in three 40 ms steps
        lit = int(min(3, t // 40 + 1)) if t >= 0 else 0
        lit_al = 1 - seg(t, 620, 760)
        for i in range(3 if t >= 120 else lit):
            x = 304 + i * 22
            pts = [(x, 52), (x + 16, 64), (x, 76)]
            arrow_c = col
            L.line(pts, INK, 8.0, int(255 * lit_al))
            L.line(pts, arrow_c, 4.0, int(255 * lit_al))
        # tickets: W4 travels, W5 / W6 move up the queue
        k4 = e_io3(seg(t, 120, 440))
        for nm in ('W4',):
            out = over(out, blank(nm))
        out = over(out, blank('W5', seg(t, 560, 600)))
        out = over(out, blank('W6', seg(t, 560, 600)))
        if t < 120:
            out = _paste_sprite(out, box, w4, cx4, cy4, 1.0 + 0.06 * e_out3(seg(t, 0, 120)))
        elif t < 520:
            pos = path_cut(path, k4)[-1]
            sc = 1.06 - 0.5 * k4
            sp = speed_of(lambda q: e_io3(seg(q, 120, 440)) * 300, t, 1.0)
            for lg, al in zip((26, 52, 78), ECHO_U):
                kk = e_io3(seg(t - lg, 120, 440))
                pe_ = path_cut(path, kk)[-1]
                out = _paste_sprite(out, box, w4, pe_[0], pe_[1], 1.06 - 0.5 * kk, al * sp, tint=col)
            fade = 1 - seg(t, 440, 520)
            out = _paste_sprite(out, box, w4, pos[0], pos[1], sc * (1 - 0.4 * seg(t, 440, 520)), fade)
        # queue shift 560-760
        kq = e_io3(seg(t, 560, 760))
        x5 = (TICKETS['W5'][0] + TICKETS['W5'][2]) / 2
        x6 = (TICKETS['W6'][0] + TICKETS['W6'][2]) / 2
        if t < 560:
            pass
        else:
            sp = speed_of(lambda q: e_io3(seg(q, 560, 760)) * 92, t, 0.9)
            for lg, al in zip((26, 52, 78), ECHO_U):
                kk = e_io3(seg(t - lg, 560, 760))
                out = _paste_sprite(out, box, w5, x5 + (cx4 - x5) * kk, cy4, 1.0, al * sp, tint=col)
                out = _paste_sprite(out, box, w6, x6 + (x5 - x6) * kk, cy4, 1.0, al * sp, tint=col)
            out = _paste_sprite(out, box, w5, x5 + (cx4 - x5) * kq, cy4)
            out = _paste_sprite(out, box, w6, x6 + (x5 - x6) * kq, cy4)
        cells_k = seg(t, 440, 640)
    out = over(out, L.done())
    # W4 cells scan in on ring +2: a corp-colour scan line sweeps each cell, leaving the enemy enamel outline
    L3 = Layer(box)
    for (s, w) in W4_CELLS:
        a0, a1 = 60 * s - 30, 60 * (s + w) - 30
        if reduce:
            k = cells_k
            if k > 0:
                L3.poly(band_pts(332, 381, a0 + 1.5, a1 - 1.5), (40, 44, 56), None, 1, int(150 * k))
                pts = band_pts(332, 381, a0 + 1.5, a1 - 1.5)
                L3.poly(pts, None, INK, 5.5, int(255 * k))
                L3.poly(pts, None, ENAMEL, 2.4, int(255 * k))
            continue
        k = e_out3(cells_k)
        if k <= 0:
            continue
        am = a0 + 1.5 + (a1 - a0 - 3) * k
        L3.poly(band_pts(332, 381, a0 + 1.5, am), (40, 44, 56), None, 1, 150)
        pts = arc_pts(332, a0 + 1.5, am) + arc_pts(381, am, a0 + 1.5)
        L3.line(arc_pts(381, a0 + 1.5, am), INK, 5.5)
        L3.line(arc_pts(332, a0 + 1.5, am), INK, 5.5)
        L3.line([ppx(332, a0 + 1.5), ppx(381, a0 + 1.5)], INK, 5.5)
        L3.line(arc_pts(381, a0 + 1.5, am), ENAMEL, 2.4)
        L3.line(arc_pts(332, a0 + 1.5, am), ENAMEL, 2.4)
        L3.line([ppx(332, a0 + 1.5), ppx(381, a0 + 1.5)], ENAMEL, 2.4)
        if k < 1:
            L3.line([ppx(330, am), ppx(383, am)], INK, 6.0)
            L3.line([ppx(330, am), ppx(383, am)], col, 3.0)
        else:
            L3.line([ppx(332, a1 - 1.5), ppx(381, a1 - 1.5)], INK, 5.5)
            L3.line([ppx(332, a1 - 1.5), ppx(381, a1 - 1.5)], ENAMEL, 2.4)
    out = over(out, L3.done())
    # the Jammer glyphs from the ticket drop into the cells
    gk = 1.0 if reduce and cells_k >= 1 else (seg(t, 600, 700) if not reduce else cells_k)
    if gk > 0:
        # the two Jammer glyphs on the W4 ticket (left: w1, right: w2)
        g1 = w4[22:62, 6:42]
        g2 = w4[22:62, 44:80]
        for (s, w), g in zip(W4_CELLS, (g1, g2)):
            am = 60 * s - 30 + 30 * w
            x, y = ppx(356.5, am)
            out = _paste_sprite(out, box, g, x, y, 1.5, gk)
    return out


reg(dict(id='fx_wave_enter', fam='M', title='The next wave enters ring +2', skins=['neutral', 'solace', 'meridian'], box=(0, 0, 740, 640), scale=0.62,
         src='state: queue ticket W4 (lineup: Jammer w1 s0, Jammer w2 s4) enters ring +2 at RINGS STEP ("W4 enters"), after fx_rings_step',
         still='The feed arrow lights in the corp colour, the W4 ticket lifts and rides the arrow into the bezel entry behind three corp-tinted echoes, a corp-colour scan line sweeps each new ring +2 cell and leaves the enemy enamel outline, the Jammer glyphs drop in, and W5 / W6 move up one slot.',
         keep='corp colour on the feed arrow, echoes and scan line only (the enemy owns this motion); enamel outline on the new cells; solid ticket edges, no dashes.',
         timing=dict(phases=[('feed arrow lights, ticket lifts', 0, 120, 'step 40 ms / easeOutCubic'), ('ticket rides into the entry', 120, 520, 'easeInOutCubic'),
                             ('cells scan in, glyphs drop', 440, 700, 'easeOutCubic'), ('queue moves up one slot', 560, 760, 'easeInOutCubic')], total=760),
         keys=[(0, 'after RINGS STEP'), (110, 'arrow lit'), (300, 'ticket rides'), (500, 'scan in'), (660, 'queue moves'), (760, 'settled')],
         reduce_note='No travel and no echoes: the W4 ticket fades out, the new cells fade in with their outlines and glyphs, and W5 / W6 cross-fade one slot right, all over 300 ms.',
         notes='The new cells are drawn as enamel outlines with the ticket glyphs; the board redraws them as full unit cells after the effect. The vacated queue slot is an empty dark slot.',
         render=wave_render))


# ============================================================================ P: protect (bone plate stock, ink key line, pink double line, rivets, hard offset shadow, no glow)
def plate_shape(L, pts, al=1.0, rivets=(), dbl=True, inset_pts=None):
    a = int(255 * al)
    L.poly(pts, BONE, INK, 3.4, a)
    if inset_pts is not None and dbl:
        for ip in inset_pts:
            L.poly(ip, None, PINK, 1.6, a)
    for (x, y) in rivets:
        L.circle((x, y), 2.6, fill=INK, a=a)
        L.circle((x - 0.6, y - 0.6), 1.1, fill=BONE_D, a=a)


def chevron_pts(r, ang, size=9.0, inward=True):
    """a chevron on the sector axis pointing at the tower"""
    s = 1 if inward else -1
    return [ppx(r + size * s, ang - size * 0.9 / r * 57.3 * 1.6), ppx(r, ang), ppx(r + size * s, ang + size * 0.9 / r * 57.3 * 1.6)]


def draw_chev(L, r, ang, size=9.0, al=1.0, col=HARM_UP, squash=0.0):
    pts = chevron_pts(r, ang, size * (1 - 0.6 * squash))
    if squash > 0:
        # flatten toward a bar
        mid = ppx(r, ang)
        pts = [(p[0] + (mid[0] - p[0]) * 0 , p[1] + (mid[1] - p[1]) * 0) for p in pts]
    L.line(pts, INK, 7.0, int(255 * al))
    L.line(pts, col, 3.6, int(255 * al))


def sparks(L, p, ang_out, k, n=6, length=16.0, al=1.0):
    """white spark ticks thrown back from an impact point (P: no starburst)"""
    for i in range(n):
        a = math.radians(ang_out + (i - (n - 1) / 2) * 24)
        r0 = 4 + 10 * k
        r1 = r0 + length * (1 - 0.5 * k)
        x0, y0 = p[0] + r0 * math.sin(a), p[1] - r0 * math.cos(a)
        x1, y1 = p[0] + r1 * math.sin(a), p[1] - r1 * math.cos(a)
        L.line([(x0, y0), (x1, y1)], INK, 4.0, int(200 * al))
        L.line([(x0, y0), (x1, y1)], WHITE, 2.0, int(255 * al))


def shield_render(t, skin, reduce=False):
    box = FX['fx_shield_block']['_box']
    base = box.crop(plate(skin, 'p3'))
    A = 180.0
    r_in, r_out, half = 171.0, 203.0, 24.0
    L = Layer(box)
    tint_al = 0.0
    if reduce:
        pa = e_out3(seg(t, 0, 100)) * (1 - seg(t, 600, 760))
        tint_al = 0.18 * pa
        chev_r = [r_out + 9, r_out + 24]
        chev_al = pa
        ps, impact_k = 1.0, -1
    else:
        # chevrons (hit 2) travel the axis from the lane to the plate edge and stop dead
        k = e_in2(seg(t, 0, 240))
        chev_r = [470 - (470 - (r_out + 9)) * k, 485 - (485 - (r_out + 24)) * k]
        chev_al = 1 - seg(t, 260, 320)
        pk = e_back(seg(t, 170, 250), 2.0)
        ps = 1.25 - 0.25 * pk
        pa = seg(t, 170, 200) * (1 - seg(t, 760, 920))
        tint_al = 0.18 * seg(t, 240, 270) * (1 - seg(t, 760, 920))
        impact_k = seg(t, 240, 400)
    # flat pink tint over the wedge (P: flat, no glow)
    if tint_al > 0:
        Lt = Layer(box)
        Lt.poly(band_pts(64, 196, A - 29, A + 29), PINK, None, 1, 255)
        base = over(base, Lt.done(), tint_al)
    if pa > 0:
        # plate with a hard offset shadow, scaled about its centre
        rc, ac = (r_in + r_out) / 2, A

        def sc(pts):
            cx, cy = ppx(rc, ac)
            return [(cx + (x - cx) * ps, cy + (y - cy) * ps) for x, y in pts]
        Lp = Layer(box)
        outer = sc(band_pts(r_in, r_out, A - half, A + half, 1.0))
        ins1 = sc(band_pts(r_in + 4.0, r_out - 4.0, A - half + 1.6, A + half - 1.6, 1.0))
        ins2 = sc(band_pts(r_in + 7.0, r_out - 7.0, A - half + 2.7, A + half - 2.7, 1.0))
        riv = sc([ppx(rc, A - half + 4.5), ppx(rc, A + half - 4.5)])
        plate_shape(Lp, outer, 1.0, riv, True, [ins1, ins2])
        if t >= 300 or reduce:
            for dd in (-2.2, 2.2):        # absorbed 2: two engraved ticks
                Lp.line([ppx(rc - 6, A + dd), ppx(rc + 6, A + dd)], INK, 2.2)
        lp = Lp.done()
        sh = shadow(lp, (3, 5), 0.55)
        base = over(base, sh, pa)
        base = over(base, lp, pa)
    for r_, in zip(chev_r):
        if chev_al > 0:
            draw_chev(L, r_, A, 9.0, chev_al)
    if not reduce and 0 <= impact_k < 1 and t >= 240:
        sparks(L, ppx(r_out + 2, A), 180.0, impact_k, 6, 15.0, 1 - impact_k)
    return over(base, L.done())


reg(dict(id='fx_shield_block', fam='P', title='SHIELD slice absorbs a landing', skins=['neutral', 'solace', 'meridian'], box=(420, 610, 652, 1010), scale=1.0,
         src='f2: Packet 5 lands on sector 3 SHIELD, hit 2, absorbed 2, through 0 (land_abs {3: 2})',
         still='The two incoming chevrons run down the sector axis across the corp rings and stop dead on an intact bone plate seated on the outer band of the wedge (r 171-203, clear of the icon and the pips); white spark ticks fly back; a flat pink tint sits on the wedge; two engraved ticks = absorbed 2. No red on the plate, no glow.',
         keep='ONE intact plate (never cracked), ink key line + pink double line + rivets, hard offset shadow, white sparks, no red on the plate, no glow.',
         timing=dict(phases=[('chevrons arrive', 0, 240, 'easeInQuad'), ('plate slams (1.25 to 1.0)', 170, 250, 'easeOutBack 2.0'), ('impact: stop dead, sparks', 240, 400, 'linear'),
                             ('hold', 400, 760, '-'), ('plate lifts off', 760, 920, 'linear')], total=920),
         keys=[(110, 'chevrons arrive'), (200, 'plate slams'), (260, 'impact'), (330, 'sparks'), (600, 'hold'), (920, 'cleared')],
         reduce_note='No slam and no sparks: plate, tint, ticks and the two chevrons stopped at the plate edge fade in over 100 ms, hold, and fade out.',
         notes='Base is the resolve plate p3 (state f2).',
         render=shield_render))


def brace_render(t, skin, reduce=False):
    box = FX['fx_brace_block']['_box']
    base = box.crop(plate(skin, 'p3'))
    A = 120.0
    lane_r0, lane_r1 = 436.0, 211.0
    bar_r = 205.0
    L = Layer(box)
    if reduce:
        lane_k, clamp_al, cs, stamp_al, stamp_s = 1.0, e_out3(seg(t, 0, 120)) * (1 - seg(t, 760, 920)), 1.0, e_out3(seg(t, 0, 120)), 1.0
        chev_pos = [bar_r + 8, bar_r + 13, bar_r + 18]
        crumple = 1.0
        chev_al = clamp_al
        lane_al = clamp_al
    else:
        lane_k = e_out3(seg(t, 0, 120))
        lane_al = 1 - seg(t, 900, 1060)
        ck = e_back(seg(t, 80, 240), 2.0)
        cs = 1.12 - 0.12 * ck
        clamp_al = seg(t, 80, 120) * (1 - seg(t, 900, 1060))
        kk = e_in2(seg(t, 120, 380))
        crumple = seg(t, 380, 480)
        sp0 = [lane_r0 - 6, lane_r0 + 18, lane_r0 + 42]
        tgt = [bar_r + 10 + 14 * i * (1 - crumple) + 4 * i * crumple for i in range(3)]
        chev_pos = [s0 + (tg - s0) * kk for s0, tg in zip(sp0, tgt)]
        chev_al = 1 - seg(t, 480, 560)
        sk = e_back(seg(t, 480, 560), 2.2)
        stamp_s = 1.5 - 0.5 * sk
        stamp_al = seg(t, 480, 510)
    # the landing lane: the enemy's own path, from the lane to the clamp (HARM, ink cased) and it stops there
    if lane_al > 0:
        pts = path_cut([ppx(lane_r0, A), ppx(bar_r + 6, A)], lane_k)
        L.line(pts, INK, 7.0, int(255 * lane_al))
        L.line(pts, HARM, 3.0, int(255 * lane_al))
    lay_lane = L.done()
    base = over(base, lay_lane)
    if clamp_al > 0:
        Lc = Layer(box)
        cx, cy = ppx(130.0, A)

        def sc(pts):
            return [(cx + (x - cx) * cs, cy + (y - cy) * cs) for x, y in pts]
        a0, a1, r0, r1 = A - 30.5, A + 30.5, 62.0, 201.0
        outer = band_pts(r0, r1, a0, a1, 1.0)
        inner = band_pts(r0 + 9.0, r1 - 9.0, a0 + 9.0 / 130 * 57.3 * 0.8, a1 - 9.0 / 130 * 57.3 * 0.8, 1.0)
        # frame = outer minus inner: draw the bone band as a thick outline along the wedge edge
        mid = band_pts(r0 + 4.5, r1 - 4.5, a0 + 2.2, a1 - 2.2, 1.0)
        mid_c = sc(mid) + [sc(mid)[0]]
        Lc.line(mid_c, INK, 12.5)
        Lc.line(mid_c, BONE, 8.0)
        for off in (-2.2, 2.2):
            mm = band_pts(r0 + 4.5 + off, r1 - 4.5 - off, a0 + 2.2 + off / 100 * 57.3, a1 - 2.2 - off / 100 * 57.3, 1.0)
            mm = sc(mm) + [sc(mm)[0]]
            Lc.line(mm, PINK, 1.2)
        for p_ in sc([ppx(r1 - 4.5, a0 + 2.6), ppx(r1 - 4.5, a1 - 2.6), ppx(r0 + 6.5, a0 + 9), ppx(r0 + 6.5, a1 - 9)]):
            Lc.circle(p_, 2.6, fill=INK)
            Lc.circle((p_[0] - 0.6, p_[1] - 0.6), 1.1, fill=BONE_D)
        # the flat stop bar across the axis, outside the clamp
        bar = sc(band_pts(bar_r - 3.0, bar_r + 4.0, A - 7.0, A + 7.0, 0.5))
        Lc.poly(bar, BONE, INK, 2.6)
        lc = Lc.done()
        base = over(base, shadow(lc, (3, 5), 0.55), clamp_al)
        base = over(base, lc, clamp_al)
    L2_ = Layer(box)
    if chev_al > 0:
        for i, r_ in enumerate(chev_pos):
            draw_chev(L2_, r_, A, 9.0 * (1 - 0.45 * crumple), chev_al)
    # the clamp stamp left on the arc (stays)
    if stamp_al > 0:
        sx, sy = ppx(lane_r0, A)
        q = 9.0 * stamp_s
        L2_.d.rectangle([(sx - q + 2.5 - box.x0) * 3, (sy - q + 3.5 - box.y0) * 3, (sx + q + 2.5 - box.x0) * 3, (sy + q + 3.5 - box.y0) * 3], fill=INK + (int(140 * stamp_al),))
        L2_.d.rectangle([(sx - q - box.x0) * 3, (sy - q - box.y0) * 3, (sx + q - box.x0) * 3, (sy + q - box.y0) * 3], fill=BONE + (int(255 * stamp_al),), outline=INK + (int(255 * stamp_al),), width=8)
        b = q * 0.55
        for sgn in (-1, 1):
            L2_.line([(sx + sgn * b * 0.4, sy - b), (sx + sgn * b, sy - b), (sx + sgn * b, sy + b), (sx + sgn * b * 0.4, sy + b)], INK, 2.0, int(255 * stamp_al))
    return over(base, L2_.done())


reg(dict(id='fx_brace_block', fam='P', title='Brace blocks a whole landing', skins=['neutral', 'solace', 'meridian'], box=(560, 440, 1010, 860), scale=0.85,
         src='f2: Brace on sector 2 TURRET (brace_sectors 2, braced_hit true): Worm 3 lands 3 there, brace 1, through 0',
         still='The landing lane runs from the arc down the sector axis to the tower; a bone clamp frame (ink key, pink double line, rivets, hard shadow) closes round the WHOLE wedge with the icon left clear; the three chevrons stop on a flat stop bar and crumple; a small clamp stamp is left on the arc.',
         keep='the clamp encloses the whole wedge, icon visible; the lane stops at the bar (never through); the arc stamp stays.',
         timing=dict(phases=[('lane draws in', 0, 120, 'easeOutCubic'), ('clamp closes (1.12 to 1.0)', 80, 240, 'easeOutBack 2.0'), ('chevrons run the lane', 120, 380, 'easeInQuad'),
                             ('chevrons crumple on the bar', 380, 480, 'linear'), ('stamp slams on the arc', 480, 560, 'easeOutBack 2.2'), ('hold', 560, 900, '-'), ('clamp, bar and lane lift off (stamp stays)', 900, 1060, 'linear')], total=1060),
         keys=[(0, 'rest'), (120, 'lane, clamp'), (300, 'chevrons run'), (440, 'crumple'), (560, 'stamp'), (1060, 'stamp stays')],
         reduce_note='No closing or crumple motion: lane, clamp, bar, the crumpled chevrons and the stamp fade in over 120 ms, hold, then everything but the stamp fades.',
         notes='Base is the resolve plate p3 (state f2).',
         render=brace_render))


def soak_render(t, skin, reduce=False):
    box = FX['fx_soak_take']['_box']
    base = box.crop(plate(skin, 'p3'))
    A = 60.0
    mouth_r, apex_r, mouth_h = 203.0, 158.0, 17.0
    L = Layer(box)
    if reduce:
        fk, wash, chev_al, pip_k = 1.0, 0.16 * e_out3(seg(t, 0, 120)) * (1 - seg(t, 800, 960)), 0.0, 1.0
        f_al = e_out3(seg(t, 0, 120)) * (1 - seg(t, 800, 960))
        flow = 0.0
        chev = None
    else:
        ck = e_in2(seg(t, 0, 160))
        cr = 300 - (300 - (mouth_r + 6)) * ck
        sh = seg(t, 300, 440)
        chev = (cr - 26 * sh, 1 - 0.7 * sh, sh)
        chev_al = 1 - seg(t, 400, 440)
        fk = e_out3(seg(t, 120, 300))
        f_al = seg(t, 120, 150) * (1 - seg(t, 800, 960))
        wash = 0.16 * seg(t, 300, 340) * (1 - seg(t, 800, 960))
        pip_k = e_out3(seg(t, 440, 600))
        flow = (t - 300) / 420.0
    if wash > 0:
        Lw = Layer(box)
        Lw.poly(band_pts(64, 196, A - 29, A + 29), SOAK, None, 1, 255)
        base = over(base, Lw.done(), wash)
    if f_al > 0:
        Lf = Layer(box)
        tip = mouth_r - (mouth_r - apex_r) * fk
        # symmetric funnel on the axis: mouth on the rim, apex toward the icon
        hw = mouth_h / mouth_r * 57.3
        poly = [ppx(mouth_r, A - hw), ppx(mouth_r, A + hw), ppx(tip, A)]
        Lf.poly(poly, SOAK, INK, 3.2)
        inner = [ppx(mouth_r - 2.5, A - hw * 0.78), ppx(mouth_r - 2.5, A + hw * 0.78), ppx(tip + 4, A)]
        Lf.poly(inner, None, BONE, 1.2)
        # paper flow chevrons inside, pointing inward
        if fk > 0.6:
            for i in range(2):
                ph = ((flow if not reduce else 0.25) + i * 0.5) % 1.0
                rr = mouth_r - 6 - (mouth_r - apex_r - 14) * ph
                w_ = 0.55 * (rr - tip) / (mouth_r - tip) * hw
                if w_ > 0.6:
                    Lf.line([ppx(rr + 3.0, A - w_), ppx(rr - 1.5, A), ppx(rr + 3.0, A + w_)], WHITE, 1.6)
        lf = Lf.done()
        base = over(base, lf, f_al)
    # the soaked pip drains (SOAK sweep over the first pip, settling into the board's own SOAK hatch)
    if pip_k > 0:
        Lp = Layer(box)
        a0, a1 = A - 16.0, A - 2.5
        am = a0 + (a1 - a0) * pip_k
        al = 1 - seg(t, 800, 960) if not reduce else (1 - seg(t, 800, 960))
        Lp.poly(band_pts(161, 169, a0, am, 0.5), SOAK, INK, 1.2, int(255 * al * 0.85))
        base = over(base, Lp.done())
    if chev is not None and chev_al > 0:
        r_, s_, sh = chev
        col = tuple(int(HARM_UP[i] + (SOAK[i] - HARM_UP[i]) * sh) for i in range(3))
        draw_chev(L, r_, A, 9.0 * s_, chev_al, col)
    return over(base, L.done())


reg(dict(id='fx_soak_take', fam='P', title='A soaked slice takes the overflow', skins=['neutral'], box=(585, 345, 805, 565), scale=1.8,
         src='f2: sector 1 SHIELD soaked 1 (Worm 3 lands 3: absorbed 2, soak 1, through 0)',
         still='The overflow chevron reaches the rim; a symmetric SOAK-blue funnel (ink key, bone inner line) draws in on the wedge axis from the rim toward the icon; the chevron shrinks into the mouth and turns SOAK; paper flow chevrons run inward; the soaked pip fills SOAK; a flat SOAK wash on the wedge.',
         keep='funnel symmetric on the axis, rim to icon; SOAK #3A7EF3 only (never pink); flow chevrons point inward; the pip ends in the board\'s own SOAK hatch.',
         timing=dict(phases=[('overflow chevron arrives', 0, 160, 'easeInQuad'), ('funnel draws in', 120, 300, 'easeOutCubic'), ('chevron shrinks into the mouth', 300, 440, 'linear'),
                             ('pip drains', 440, 600, 'easeOutCubic'), ('hold, flow scrolls', 600, 800, 'linear'), ('funnel and wash lift off', 800, 960, 'linear')], total=960),
         keys=[(90, 'chevron arrives'), (200, 'funnel draws'), (380, 'into the mouth'), (520, 'pip drains'), (700, 'hold'), (960, 'cleared')],
         reduce_note='No travel: funnel, wash and the filled pip fade in over 120 ms with the flow chevrons still, hold, fade out. The overflow chevron is not shown.',
         notes='Player-only (the tower wedge): the same on every corp skin, so drawn on the neutral board only. Base p3 (f2).',
         render=soak_render))


# ============================================================================ S: trace add (Trigger, +1 Trace)
CARD_BOX = (1262, 788, 1442, 1080)
PIP = [(1440, 358), (1468, 358), (1496, 358), (1524, 358), (1552, 358)]


def glitch(img_c, box, rows, shift, rng, region):
    """stepped horizontal glitch bands inside `region` (x0, y0, x1, y1 screen): each band shifts its pixels by `shift` px,
    splits R/B by 3 px, takes a 35 % violet tint and dark scanlines."""
    out = img_c.copy()
    x0, y0, x1, y1 = [int(v) for v in region]
    for (ry, rh, sx) in rows:
        a, b = ry - box.y0, ry + rh - box.y0
        c0, c1 = x0 - box.x0, x1 - box.x0
        a, b = max(0, a), min(box.h, b)
        if b <= a:
            continue
        strip = img_c[a:b, c0:c1].copy()
        st = np.roll(strip, sx, axis=1)
        st[..., 0] = np.roll(strip[..., 0], sx + 3, axis=1)
        st[..., 2] = np.roll(strip[..., 2], sx - 3, axis=1)
        st = st * 0.65 + np.array(VIOLET, np.float32) * 0.35
        st[::2] *= 0.72
        out[a:b, c0:c1] = st
    return out


def trace_render(t, skin, reduce=False):
    box = FX['fx_trace_add']['_box']
    p = plate(skin, 'p1')
    out = box.crop(p)
    # the lit pip, cut from pip 3 of the same HUD
    sx, sy = PIP[2]
    tx, ty = PIP[3]
    q = 13
    lit = p[sy - q:sy + q, sx - q:sx + q].copy()
    rng = np.random.default_rng(49)
    steps_card = [0, 33, 67, 100, 133]
    if not reduce and 16 <= t < 166:
        i = min(4, int((t - 16) // 30.0))
        rr = np.random.default_rng(100 + i)
        rows = []
        for _ in range(3):
            y = int(rr.integers(CARD_BOX[1] + 6, CARD_BOX[3] - 20))
            rows.append((y, int(rr.integers(5, 11)), int(rr.choice([-6, 6]))))
        out = glitch(out, box, rows, 6, rr, (CARD_BOX[0] - 8, CARD_BOX[1], CARD_BOX[2] + 8, CARD_BOX[3]))
    # pip pops in 3 stepped scales, then holds lit
    if t >= 166:
        if reduce:
            k = 1.0
        else:
            k = 1.0
        stp = 0 if reduce else min(3, int((t - 166) // 33.4))
        scale = [1.7, 1.35, 1.0, 1.0][stp]
        Lp = Layer(box)
        if stp < 2 and not reduce:
            hq = 11 * scale
            Lp.d.rectangle([(tx - hq - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq - box.x0) * 3, (ty + hq - box.y0) * 3], fill=VIOLET + (255,), outline=INK + (255,), width=6)
            # RGB split ghosts, stepped
            Lp.d.rectangle([(tx - hq - 4 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx - hq - 1 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(255, 40, 120, 200))
            Lp.d.rectangle([(tx + hq + 1 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq + 4 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(40, 200, 255, 200))
            out = over(out, Lp.done())
        else:
            a, b = ty - q - box.y0, tx - q - box.x0
            out[a:a + 2 * q, b:b + 2 * q] = lit
        if not reduce and 166 <= t < 266:
            j = int((t - 166) // 33.4)
            rr = np.random.default_rng(300 + j)
            rows = [(int(rr.integers(345, 368)), 4, int(rr.choice([-6, 6])))]
            out = glitch(out, box, rows, 6, rr, (1350, 340, 1600, 376))
    return out


reg(dict(id='fx_trace_add', fam='S', title='A loud card adds Trace', skins=['neutral'], box=(1240, 330, 1620, 1080), scale=0.8,
         src='f2: Trigger played (cost 1, loud 1): Trace 3 to 4 (f1 trace 3, f2 trace 4, cap 6)',
         still='Violet stepped glitch bands shear the Trigger card (6 px offsets, R/B split, scanlines) for five 33 ms steps; then the fourth TRACE pip pops in three stepped scales (1.7, 1.35, 1.0) with a one-band glitch on the TRACE row and settles as the HUD\'s own lit pip.',
         keep='violet = Trace only; stepped bands, never smooth; the settled pip is the HUD\'s own lit pip.',
         timing=dict(phases=[('card glitch, 5 steps', 0, 166, 'step 33 ms'), ('pip pops, 3 steps; row glitch', 166, 266, 'step 33 ms'), ('settled', 266, 400, '-')], total=400),
         keys=[(0, 'played'), (40, 'glitch'), (110, 'glitch'), (180, 'pip pops'), (215, 'pip steps'), (400, 'settled')],
         reduce_note='No glitch bands: the fourth pip simply lights at 166 ms (one step, no scale).',
         notes='Also played by Pull (+1) and Shove (+2, two pips one after the other, 120 ms apart).',
         render=trace_render))


# ============================================================================ T: commit (pencil marks burn into pink paint)
_commit = {}


def commit_data(skin, box):
    k = (skin, box.x0, box.y0)
    if k in _commit:
        return _commit[k]
    p2, p3 = plate(skin, 'p2'), plate(skin, 'p3')
    a2, a3 = box.crop(p2), box.crop(p3)
    h2, s2, v2 = hsv_np(a2)
    yel = (h2 > 40) & (h2 < 66) & (s2 > 0.55) & (v2 > 0.55)
    pk3 = pinkish(a3) | ((hsv_np(a3)[0] > 290) & (hsv_np(a3)[1] > 0.35))
    diff = np.abs(a2 - a3).max(2) > 22
    onb = (box.RHO > 205) & (box.RHO < 500)
    m = yel & onb & (np.abs(a2 - a3).max(2) > 40)
    m = ndi.binary_opening(m, iterations=1) | (m & ndi.binary_dilation(m, iterations=1))
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sizes = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 40])
    marks = ndi.binary_dilation(keep, iterations=3) & diff
    # the burn order: geodesic distance along the marks from the route start, component by component
    seed = FX['fx_commit'].get('seed', (440, 760))
    sx, sy = seed[0] - box.x0, seed[1] - box.y0
    lab2, n2 = ndi.label(marks, structure=np.ones((3, 3)))
    dist = np.full(marks.shape, np.inf, np.float32)
    ys, xs = np.nonzero(marks)
    comps = []
    for ci in range(1, n2 + 1):
        cm = lab2 == ci
        cy, cx = np.nonzero(cm)
        d0 = np.hypot(cx - sx, cy - sy)
        j = int(np.argmin(d0))
        comps.append((float(d0[j]), ci, (cy[j], cx[j])))
    comps.sort()
    from collections import deque
    for (d0, ci, (y0, x0)) in comps:
        cm = lab2 == ci
        dd = np.full(cm.shape, np.inf, np.float32)
        dd[y0, x0] = d0
        q = deque([(y0, x0)])
        while q:
            y, x = q.popleft()
            v = dd[y, x]
            for dy, dx, w in ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < cm.shape[0] and 0 <= xx < cm.shape[1] and cm[yy, xx] and dd[yy, xx] > v + w:
                    dd[yy, xx] = v + w
                    q.append((yy, xx))
        dist = np.where(cm, dd, dist)
    fin = np.isfinite(dist)
    dmax = float(dist[fin].max()) if fin.any() else 1.0
    nd = np.where(fin, dist / dmax, 2.0).astype(np.float32)
    # end point of the route (for the ping)
    j = np.unravel_index(np.argmax(np.where(fin, dist, -1)), dist.shape)
    endp = (j[1] + box.x0, j[0] + box.y0)
    rest = (np.abs(a2 - a3).max(2) > 6) & ~marks & onb
    _commit[k] = (a2, a3, marks, nd, endp, rest)
    return _commit[k]


def commit_render(t, skin, reduce=False):
    box = FX['fx_commit']['_box']
    a2, a3, marks, nd, endp, rest = commit_data(skin, box)
    out = a2.copy()
    if reduce:
        k = e_io3(seg(t, 0, 300))
        out = np.where(marks[..., None], mix(a2, a3, k), out)
        out = np.where(rest[..., None], mix(a2, a3, e_io3(seg(t, 200, 500))), out)
        return out
    front = 1.08 * e_io3(seg(t, 80, 560))
    burnt = marks & (nd <= front)
    out = np.where(burnt[..., None], a3, out)
    # the front is white-hot for 2 frames' worth of path
    hot = marks & (nd > front - 0.035) & (nd <= front) & (front < 1.06)
    hotc = mix(a3, np.full_like(a3, 255.0), 0.75)
    out = np.where(hot[..., None], hotc, out)
    # the rest of the board steps from preview to resolve once the marks are paint (guns 58 % to full etc.)
    out = np.where(rest[..., None], mix(a2, a3, e_io3(seg(t, 560, 760))), out)
    L = Layer(box)
    pk = seg(t, 560, 700)
    if 0 < pk < 1:
        r = 6 + 16 * e_out3(pk)
        L.circle(endp, r, outline=INK, w=4.6, a=int(255 * (1 - pk)))
        L.circle(endp, r, outline=PINK, w=2.4, a=int(255 * (1 - pk)))
    return over(out, L.done())


reg(dict(id='fx_commit', fam='T', title='SEND IT burns pencil marks into paint', skins=['neutral', 'solace', 'meridian'], box=(180, 470, 880, 960), scale=0.6,
         seed=(372, 836),
         src='SEND IT on the best line (f2: Twist, Trigger, Brace): p2 preview marks (pencil yellow) to the p3 resolve marks (pink)',
         still='Every pencil-yellow plan mark on the board burns into the pink painted mark front to back along its own length (geodesic order from the route start); the burn front is white-hot for two frames; a pink ping rings the route end; then the rest of the board steps from preview to resolve.',
         keep='yellow to PINK front to back; white-hot front for 2 frames; ping at the route end; no yellow left after the beat.',
         timing=dict(phases=[('SEND IT press, hold', 0, 80, '-'), ('burn front runs the marks', 80, 560, 'easeInOutCubic'), ('ping at the route end', 560, 700, 'easeOutCubic'),
                             ('board steps preview to resolve', 560, 760, 'easeInOutCubic')], total=760),
         keys=[(0, 'pencil plan'), (200, 'burn starts'), (330, 'front runs'), (480, 'front arrives'), (620, 'ping'), (760, 'committed paint')],
         reduce_note='No burn front and no ping: the marks cross-fade yellow to pink over 300 ms, then the board steps to resolve over 300 ms.',
         notes='Both ends are the generator\'s own plates (p2 and p3 of each skin); only the path between them is the effect.',
         render=commit_render))


for _s in FX.values():
    _s['_box'] = Box(*_s['box'])
