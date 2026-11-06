"""mp_eff: the M (motion), P (protect), S (system) and T (commit) effects on the rebuilt board (2026-11-03 rebuild).
render(t_ms, skin, reduce, marks=True) -> the frame crop (RGB float), composited board -> effect -> HUD and hand (review 1.6).
marks=False draws the same moment with the effect's own marks off (arrows, echoes, plates, stamps, sparks): the loudness reference
for motion, so a moving cell is not counted as effect light (review 2.10).  Every total is <= 600 ms (VfxTier T2 cap, review 2.11).
pre(skin) / post(skin): the frame crops the effect starts from and ends on (loudness references).
Timings live in each spec (ms) and go to timings_MPST.json."""
import math, copy
import numpy as np
from scipy import ndimage as ndi
from mp_lib import *

FX = {}
CAP_MS = 600          # VfxTier T2 (REVIEW_RESPONSE 2.11): every effect, full and reduce motion, no per-effect override


def reg(spec):
    FX[spec['id']] = spec
    return spec


# ============================================================================ capture masks (snapshot of the generator's own masks)
_mk = {}


def cmask(skin, beat, cls):
    k = (skin, beat, cls)
    if k not in _mk:
        d = np.load(ME + 'work/masks/masks_%s%s.npz' % (beat, '' if skin == 'neutral' else '_' + skin))
        _mk[k] = np.unpackbits(d[cls])[:H * W].reshape(H, W).astype(bool) if cls in d.files else np.zeros((H, W), bool)
    return _mk[k]


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


_full = {}


def unit_alpha(full, empty, key, r0=210.5, r1=389.5):
    """alpha of the unit layer (cells, lit glass, tokens, trays, badges, chevrons): full vs empty board; gun marks never belong to a unit"""
    if key in _full:
        return _full[key]
    d = np.abs(full - empty).max(2)
    m = (d > 14) & ~pinkish(full) & (FRHO > r0) & (FRHO < r1)
    m = ndi.binary_closing(m, iterations=1)
    m = ndi.binary_dilation(m, iterations=1)
    a = ndi.gaussian_filter(m.astype(np.float32), 0.6)
    a = np.clip(a * 1.25, 0, 1) * ((FRHO > r0) & (FRHO < r1))
    _full[key] = a
    return a


def move_layer(base_c, box, src_full, a_full, d_ang=0.0, d_r=0.0, echoes=(), tint=None):
    """slide the unit pixels of src_full (alpha a_full) by (d_r, d_ang) over base_c (crop).  echoes: (d_r, d_ang, alpha) copies drawn first,
    tinted 25 % toward `tint`"""
    out = base_c.copy()
    for (er, ea, al) in list(echoes) + [(d_r, d_ang, 1.0)]:
        srho = np.maximum(box.RHO - er, 0)
        sang = box.ANG - ea
        xs, ys = polar_src(srho, sang)
        al_ = sample1(a_full, xs, ys) * al
        if al_.max() <= 0.002:
            continue
        rgb = sample(src_full, xs, ys)
        if tint is not None and al < 1.0:
            rgb = rgb * 0.75 + np.array(tint, np.float32) * 0.25
        out = out * (1 - al_[..., None]) + rgb * al_[..., None]
    return out


# review 2.10 (2026-11-03 rebuild): the motion echoes are retired.  On the shared gated meter (fxk_lib.loud_frame, ref = the marks-off
# frame, end = the settled frame) they were the loudest light of every M effect (spin 48 134 -> 2 090 without them, twist 11 747 ->
# 1 076, pull 2 741 -> 371, shove 2 708 -> 1 008), so a state change outshouted every hit.  The eased motion carries the read.
ECHO_A = ()
ECHO_LAG = ()
ECHO_U = ()
ARROW_STUB = dict(spin=60.0, twist=30.0, shove=30.0, rings=32.0, hold=22.0)     # deg: the arrow runs this far ahead of the moving cell


def edge_echoes(cur, ghosts, mask, sp, tint=PINK):
    out = cur
    for gh, al in zip(ghosts, ECHO_A):
        dif = np.clip(np.abs(gh - cur).max(2) / 90.0, 0, 1)
        g = gh * 0.75 + np.array(tint, np.float32) * 0.25
        out = mix(out, g, mask * dif * al * sp)
    return out


def static_tags(out_c, box, src_full, skin):
    """the ring tags (NOW W1 / +1 W2 / +2 W3, K family labels) never travel with a turning ring: paste them back from the base"""
    m = box.crop(ndi.binary_dilation(cmask(skin, 'p1', 'tags'), iterations=1).astype(np.float32)[..., None])[..., 0]
    return mix(out_c, box.crop(src_full), m)


# ============================================================================ M: spin (Spin 3 turns the tower)
ICON_R, ICON_DISC = 120.5, 38.5


def spin_ang(t):
    if t < 100:
        return 0.0
    if t < 500:
        return 183.0 * e_io3(seg(t, 100, 500))
    return 183.0 - 3.0 * e_out3(seg(t, 500, 600))


def _tower_at(img, box, d):
    r = rotated(img, box, d)
    for k in range(6):
        cx, cy = ppx(ICON_R, 60 * k + d)
        ox, oy = ppx(ICON_R, 60 * k)
        m = np.clip((ICON_DISC - np.hypot(box.X - cx, box.Y - cy)) / 1.2 + 0.5, 0, 1)
        if m.max() <= 0:
            continue
        up = sample(img, box.X + (ox - cx), box.Y + (oy - cy))
        r = r * (1 - m[..., None]) + up * m[..., None]
    return r


def spin_render(t, skin, reduce=False, marks=True):
    box = FX['fx_spin']['_box']
    B0, B1 = below(skin, 'p1'), below(skin, 'p1_noguns')
    base = mix(box.crop(B0), box.crop(B1), e_out3(seg(t, 0, 100)))
    rmask = ring_mask(box, 63.5, 211.0, feather=1.2)
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(base, mix(_tower_at(B1, box, 0.0), _tower_at(B1, box, 180.0), k), rmask)
    else:
        out = mix(base, _tower_at(B1, box, spin_ang(t)), rmask)
        sp = speed_of(spin_ang, t, 0.55)
        if marks and sp > 0.02 and ECHO_A:
            out = edge_echoes(out, [_tower_at(B1, box, spin_ang(t - lag)) for lag in (9, 18, 27)], rmask, sp * 0.8)
    if marks:
        L = Layer(box)
        R_ = 220.0
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
            arrow(L, arc_pts(R_, 6, 6 + ARROW_STUB['spin']), PINK, AW, AH, AC, int(255 * al))
        elif t < 500:
            head = 6 + 174 * e_out3(seg(t, 0, 100))
            tail = 6 + spin_ang(t)
            head = min(head, tail + ARROW_STUB['spin'])
            if head - tail > 4:
                arrow(L, arc_pts(R_, tail, head), PINK, AW, AH, AC)
        out = over(out, L.done())
    return comp(out, box.crop(above(skin, 'p1')))


def spin_pre(skin):
    b = FX['fx_spin']['_box']
    return comp(b.crop(below(skin, 'p1')), b.crop(above(skin, 'p1')))


def spin_post(skin):
    b = FX['fx_spin']['_box']
    B1 = below(skin, 'p1_noguns')
    out = mix(b.crop(B1), _tower_at(B1, b, 180.0), ring_mask(b, 63.5, 211.0, feather=1.2))
    return comp(out, b.crop(above(skin, 'p1')))


reg(dict(id='fx_spin', fam='M', tier='state', title='Spin 3 turns the tower', skins=['neutral'], box=(316, 320, 756, 760), scale=0.9,
         src='f1 hand: Spin 3 ("Turn the tower 3", cost 1): the tower turns 3 sectors (180 deg) clockwise',
         still='The tower annulus (r 64-211) turns 180 deg; the hub (BREAKER, HP ring) stays put and every slice icon stays upright; a 60 deg pink arrow stub in the gap between the tower and ring NOW runs ahead of slice 0 and is eaten as it arrives. No echoes (review 2.10).',
         keep='pink arrow stub (resolve colour), 3 px with an ink casing; icons upright at rest; the hub never turns; no echoes.',
         timing=dict(phases=[('anticipate: arrow draws, gun preview fades', 0, 100, 'easeOutCubic'), ('turn 183 deg', 100, 500, 'easeInOutCubic'),
                             ('settle back 3 deg, arrow gone', 500, 600, 'easeOutCubic')], total=600),
         reduce_phases=[('arrow appears', 0, 100, 'easeOutCubic'), ('tower dissolves 0 to 180 deg', 100, 400, 'easeInOutCubic'), ('arrow fades', 400, 520, 'linear')],
         keys=[(0, 'rest'), (80, 'arrow draws'), (240, 'turning'), (330, 'peak speed'), (500, 'overshoot'), (600, 'settled')],
         reduce_note='No sweep: the arrow stub appears whole (100 ms), the tower dissolves from 0 to 180 deg over 300 ms (easeInOut), the arrow fades (120 ms). Icons and hub as in full motion.',
         notes='The gun preview marks fade in the anticipate beat: they aim from the old slice positions and the board re-solves them after the turn (not part of the effect).',
         render=spin_render, pre=spin_pre, post=spin_post))


# ============================================================================ M: twist (ring +1 turns one sector)
def twist_ang(t):
    if t < 90:
        return 0.0
    if t < 430:
        return 61.5 * e_io3(seg(t, 90, 430))
    return 61.5 - 1.5 * e_out3(seg(t, 430, 540))


TW_UNITS = (210.0, 0.0)          # f1 ring +1 units: Payload 4 (s3-4, centre 210), Packet 5 (s0, centre 0); the Adjuster (s2) turns with the ring


def twist_core(t, reduce, marks, B, box, skin, d0=0.0, units=TW_UNITS):
    """ring +1 of the full-frame board B turned by d0 + twist_ang(t) (d0: a start offset, used by the resolve beat)"""
    base = box.crop(B)
    rm = ring_mask(box, 270.5, 328.5, feather=1.0)
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(base, mix(rotated(B, box, d0), rotated(B, box, d0 + 60), k), rm)
    else:
        out = mix(base, rotated(B, box, d0 + twist_ang(t)), rm)
        sp = speed_of(twist_ang, t, 0.20)
        if marks and sp > 0.02 and ECHO_A:
            out = edge_echoes(out, [rotated(B, box, d0 + twist_ang(t - lag)) for lag in ECHO_LAG], rm, sp)
    out = static_tags(out, box, B, skin)
    if marks:
        L = Layer(box)
        for c0 in units:
            c0 = c0 + d0
            if reduce:
                al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
                arrow(L, arc_pts(299.5, c0 + 4, c0 + 4 + ARROW_STUB['twist']), PINK, AW, AH, AC, int(255 * al))
            elif t < 540:
                head = c0 + 4 + 56 * e_out3(seg(t, 0, 90))
                tail = c0 + 4 + twist_ang(t)
                head = min(head, tail + ARROW_STUB['twist'])
                al = 1 - seg(t, 470, 540)
                if head - tail > 3:
                    arrow(L, arc_pts(299.5, tail, head), PINK, AW, AH, AC, int(255 * al))
        out = over(out, L.done())
    return out


def twist_render(t, skin, reduce=False, marks=True):
    box = FX['fx_twist']['_box']
    out = twist_core(t, reduce, marks, below(skin, 'p1'), box, skin)
    return comp(out, box.crop(above(skin, 'p1')))


def twist_post(skin):
    box = FX['fx_twist']['_box']
    B = below(skin, 'p1')
    out = mix(box.crop(B), rotated(B, box, 60.0), ring_mask(box, 270.5, 328.5, feather=1.0))
    return comp(static_tags(out, box, B, skin), box.crop(above(skin, 'p1')))


def p1_pre(fid):
    def f(skin):
        b = FX[fid]['_box']
        return comp(b.crop(below(skin, 'p1')), b.crop(above(skin, 'p1')))
    return f


reg(dict(id='fx_twist', fam='M', tier='state', title='Twist turns ring +1 by a sector', skins=['neutral', 'solace', 'meridian'], box=(36, 40, 560, 1040), scale=0.5,
         src='f2 played Twist [1, 1] (ring 1, one sector clockwise; "Turn one ring 1", cost 0); drawn on the decide board f1',
         still='Ring +1 (r 271-328) turns 60 deg clockwise with its cells, tokens and the Adjuster; the ring tags stay put; each unit on it gets a 30 deg pink arrow stub that runs ahead of the cell along the ring and is eaten as it arrives. No echoes (review 2.10). The corp ring material turns with the ring.',
         keep='pink arrow stub along the ring; the ring tags never travel; no echoes; the hover form (preview) is the same arrow in pencil yellow (hover plates).',
         timing=dict(phases=[('anticipate: arrows draw', 0, 90, 'easeOutCubic'), ('turn 61.5 deg', 90, 430, 'easeInOutCubic'), ('settle back 1.5 deg, arrows fade', 430, 540, 'easeOutCubic')], total=540),
         reduce_phases=[('arrows appear', 0, 100, 'easeOutCubic'), ('ring dissolves 0 to 60 deg', 100, 400, 'easeInOutCubic'), ('arrows fade', 400, 520, 'linear')],
         keys=[(0, 'rest'), (80, 'arrows drawn'), (220, 'turning'), (320, 'arriving'), (430, 'overshoot'), (540, 'settled')],
         reduce_note='The arrow stubs appear whole (100 ms), the ring dissolves from 0 to 60 deg over 300 ms, the arrows fade (120 ms).',
         notes='The landing arcs on the outer lanes are not moved by the effect; they re-solve when the board redraws after it.',
         render=twist_render, pre=p1_pre('fx_twist'), post=twist_post))


# ============================================================================ M: pull / shove / bump (one unit moves)
def _one_unit(skin, reg_):
    B, E = below(skin, 'p1'), below(skin, 'p1_empty')
    ua = unit_alpha(B, E, ('ua_p1', skin))
    return B, E, ua * reg_


def pull_dr(t):
    if t < 90:
        return 0.0
    if t < 400:
        return -59.0 * e_io3(seg(t, 90, 400))
    return -59.0 + 2.0 * e_out3(seg(t, 400, 500))


PULL_REG = sector_region(328, 385, 270, 330)


def pull_render(t, skin, reduce=False, marks=True):
    box = FX['fx_pull']['_box']
    B, E, a = _one_unit(skin, PULL_REG)
    hole = box.crop(a[..., None])[..., 0]
    base = mix(box.crop(B), box.crop(E), hole)
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(move_layer(base, box, B, a), move_layer(base, box, B, a, d_r=-57.0), k)
    else:
        sp = speed_of(pull_dr, t, 0.18)
        ech = [(pull_dr(t - lg), 0.0, al * sp) for lg, al in zip(ECHO_LAG, ECHO_U)] if (marks and sp > 0.02) else []
        out = move_layer(base, box, B, a, d_r=pull_dr(t), echoes=ech, tint=PINK)
    if marks:
        L = Layer(box)
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
            arrow(L, [ppx(372, 300), ppx(284, 300)], PINK, AW, AH, AC, int(255 * al))
        elif t < 500:
            head = 372 - 88 * e_out3(seg(t, 0, 90))
            tail = 372 + pull_dr(t)
            al = 1 - seg(t, 430, 500)
            if tail - head > 3:
                arrow(L, [ppx(tail, 300), ppx(head, 300)], PINK, AW, AH, AC, int(255 * al))
        out = over(out, L.done())
    return comp(out, box.crop(above(skin, 'p1')))


def pull_post(skin):
    box = FX['fx_pull']['_box']
    B, E, a = _one_unit(skin, PULL_REG)
    base = mix(box.crop(B), box.crop(E), box.crop(a[..., None])[..., 0])
    return comp(move_layer(base, box, B, a, d_r=-57.0), box.crop(above(skin, 'p1')))


reg(dict(id='fx_pull', fam='M', tier='state', title='Pull drags a unit inward', skins=['neutral', 'solace', 'meridian'], box=(110, 150, 530, 570), scale=0.85,
         src='card Pull ("Pull a unit in", cost 0, loud 1): shown on Packet 7 (ring +2, sector 5) into the empty ring +1 sector 5 of f1',
         still='The whole cell (lit glass, token, tray) slides 57 px inward along the sector axis; a pink radial arrow from the cell to its new ring is eaten as the cell moves; the empty glass is left behind. No echoes (review 2.10).',
         keep='pink arrow pointing inward (resolve colour); no echoes; the hover form is pencil yellow.',
         timing=dict(phases=[('anticipate: arrow draws', 0, 90, 'easeOutCubic'), ('slide 59 px', 90, 400, 'easeInOutCubic'), ('settle back 2 px, arrow fades', 400, 500, 'easeOutCubic')], total=500),
         reduce_phases=[('arrow appears', 0, 100, 'easeOutCubic'), ('cell dissolves ring +2 to ring +1', 100, 400, 'easeInOutCubic'), ('arrow fades', 400, 520, 'linear')],
         keys=[(0, 'rest'), (80, 'arrow drawn'), (200, 'sliding'), (280, 'arriving'), (400, 'overshoot'), (500, 'settled')],
         reduce_note='The arrow appears (100 ms), the cell dissolves from ring +2 to ring +1 over 300 ms, the arrow fades (120 ms).',
         notes='Pull is loud: its +1 Trace plays fx_trace_add after this. The moved cell keeps its FAR grade until the board redraws in the new ring\'s COLD grade.',
         render=pull_render, pre=p1_pre('fx_pull'), post=pull_post))


def shove_ang(t):
    if t < 90:
        return 0.0
    if t < 400:
        return 62.0 * e_io3(seg(t, 90, 400))
    return 62.0 - 2.0 * e_out3(seg(t, 400, 500))


SHOVE_REG = sector_region(271, 328, -30, 30)


def shove_render(t, skin, reduce=False, marks=True):
    box = FX['fx_shove']['_box']
    B, E, a = _one_unit(skin, SHOVE_REG)
    base = mix(box.crop(B), box.crop(E), box.crop(a[..., None])[..., 0])
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(move_layer(base, box, B, a), move_layer(base, box, B, a, d_ang=60.0), k)
    else:
        sp = speed_of(shove_ang, t, 0.20)
        ech = [(0.0, shove_ang(t - lg), al * sp) for lg, al in zip(ECHO_LAG, ECHO_U)] if (marks and sp > 0.02) else []
        out = move_layer(base, box, B, a, d_ang=shove_ang(t), echoes=ech, tint=PINK)
    out = static_tags(out, box, B, skin)
    if marks:
        L = Layer(box)
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
            arrow(L, arc_pts(299.5, 4, 4 + ARROW_STUB['shove']), PINK, AW, AH, AC, int(255 * al))
        elif t < 500:
            head = 4 + 56 * e_out3(seg(t, 0, 90))
            tail = 4 + shove_ang(t)
            head = min(head, tail + ARROW_STUB['shove'])
            al = 1 - seg(t, 430, 500)
            if head - tail > 3:
                arrow(L, arc_pts(299.5, tail, head), PINK, AW, AH, AC, int(255 * al))
        out = over(out, L.done())
    return comp(out, box.crop(above(skin, 'p1')))


def shove_post(skin):
    box = FX['fx_shove']['_box']
    B, E, a = _one_unit(skin, SHOVE_REG)
    base = mix(box.crop(B), box.crop(E), box.crop(a[..., None])[..., 0])
    return comp(static_tags(move_layer(base, box, B, a, d_ang=60.0), box, B, skin), box.crop(above(skin, 'p1')))


reg(dict(id='fx_shove', fam='M', tier='state', title='Shove slides a unit one sector', skins=['neutral', 'solace', 'meridian'], box=(370, 130, 900, 500), scale=0.8,
         src='card Shove ("Slide a unit 1", cost 2, loud 2): shown on Packet 5 (ring +1, sector 0) into the empty sector 1 of f1',
         still='The cell slides one sector clockwise along its ring; a 30 deg pink arrow stub runs ahead of it and is eaten as it arrives; the ring tags stay put. No echoes (review 2.10).',
         keep='pink arrow stub along the ring; no echoes; the hover form is pencil yellow.',
         timing=dict(phases=[('anticipate: arrow draws', 0, 90, 'easeOutCubic'), ('slide 62 deg', 90, 400, 'easeInOutCubic'), ('settle back 2 deg, arrow fades', 400, 500, 'easeOutCubic')], total=500),
         reduce_phases=[('arrow appears', 0, 100, 'easeOutCubic'), ('cell dissolves into the next sector', 100, 400, 'easeInOutCubic'), ('arrow fades', 400, 520, 'linear')],
         keys=[(0, 'rest'), (80, 'arrow drawn'), (200, 'sliding'), (280, 'arriving'), (400, 'overshoot'), (500, 'settled')],
         reduce_note='The arrow stub appears (100 ms), the cell dissolves into the next sector over 300 ms, the arrow fades (120 ms).',
         notes='Shove into an occupied cell: see the variant fx_shove_bump below.',
         render=shove_render, pre=p1_pre('fx_shove'), post=shove_post))


def bump_ang(t):
    if t < 90:
        return 0.0
    if t < 200:
        return -7.0 * e_in2(seg(t, 90, 200))
    k = seg(t, 200, 380)
    return -7.0 * (1 - e_out3(k)) + 1.5 * math.sin(math.pi * k) * (1 - k)


def starburst(L, p, r, al=1.0, n=10, col=PINK, core=HIT_PAPER):
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.48
        pts.append((p[0] + rr * math.sin(a), p[1] - rr * math.cos(a)))
    L.poly(pts, col, INK, 2.4, int(255 * al))
    L.circle(p, r * 0.32, fill=core, a=int(255 * al))


BUMP_REG = sector_region(328, 385, 270, 330)


def bump_render(t, skin, reduce=False, marks=True):
    box = FX['fx_shove_bump']['_box']
    B, E, a = _one_unit(skin, BUMP_REG)
    base = mix(box.crop(B), box.crop(E), box.crop(a[..., None])[..., 0])
    if reduce:
        out = move_layer(base, box, B, a)
    else:
        sp = speed_of(bump_ang, t, 0.12)
        ech = [(0.0, bump_ang(t - lg), al * sp) for lg, al in zip(ECHO_LAG, ECHO_U)] if (marks and sp > 0.02 and t < 200) else []
        out = move_layer(base, box, B, a, d_ang=bump_ang(t), echoes=ech, tint=PINK)
    if marks:
        L = Layer(box)
        al = (e_out3(seg(t, 0, 100)) if reduce else e_out3(seg(t, 0, 90))) * (1 - seg(t, 380, 480))
        if al > 0:
            head = 296 - 22 * (1.0 if reduce else e_out3(seg(t, 0, 90)))
            arrow(L, arc_pts(356.5, 296, head), PINK, AW, AH, AC, int(255 * al))
        k = 0.6 if reduce else seg(t, 200, 320)
        if (reduce and t >= 0) or (0 <= k < 1 and t >= 200):
            fade = 1 - seg(t, 380, 480) if reduce else 1 - k ** 2
            L.line([ppx(331, 270), ppx(382, 270)], INK, 6.0, int(255 * fade))
            L.line([ppx(331, 270), ppx(382, 270)], HIT_PAPER, 2.6, int(255 * fade))
            if not reduce:
                s_ = 0.6 + 0.6 * e_out3(min(1, k * 2.5))
                for rr in (342, 371):
                    starburst(L, ppx(rr, 270), 13.0 * s_, fade)
                for (dr, da) in ((-14, -5), (12, -6), (-6, 6), (16, 5)):
                    c = ppx(356 + dr * k * 1.4, 270 + da * k * 1.2)
                    L.poly([(c[0] - 2.5, c[1] - 1), (c[0] + 2.5, c[1] - 2), (c[0], c[1] + 3)], HIT_PAPER, INK, 1.0, int(255 * fade))
        out = over(out, L.done())
    return comp(out, box.crop(above(skin, 'p1')))


reg(dict(id='fx_shove_bump', fam='M', tier='state', title='Shove collision (variant of fx_shove)', skins=['neutral', 'solace', 'meridian'], box=(90, 330, 430, 640), scale=1.0,
         src='card Shove into an occupied cell: shown on Packet 7 (ring +2, sector 5) shoved anticlockwise into Packet 6 (sectors 2-4) on f1. Registered as a D (damage) effect in the round-2 source; drawn here under its parent',
         still='The pink arrow shows the slide the card asked for; the cell starts to slide, hits the shared edge, a paper bump line and two small keylined pink starbursts sit on the edge with paper shards, and the cell springs back into its own sector.',
         keep='the pink starbursts sit on the shared edge only (D material, small); the cell ends in its own sector; no hatch is drawn by the effect (the board shows any HP tick lost).',
         timing=dict(phases=[('anticipate: arrow draws', 0, 90, 'easeOutCubic'), ('slide toward the edge', 90, 200, 'easeInQuad'), ('contact: bump line, starbursts, shards', 200, 320, 'easeOutCubic'),
                             ('spring back', 200, 380, 'easeOutCubic + 2 deg wobble'), ('arrow and bump line fade', 380, 480, 'linear')], total=480),
         reduce_phases=[('arrow and bump line appear', 0, 100, 'easeOutCubic'), ('hold', 100, 380, '-'), ('fade', 380, 480, 'linear')],
         keys=[(0, 'rest'), (80, 'arrow drawn'), (180, 'sliding'), (215, 'contact'), (270, 'spring back'), (480, 'settled')],
         reduce_note='No slide and no starbursts: the arrow and the bump line on the shared edge appear for 380 ms and fade; the cell never moves.',
         notes='Round 2 stated that both units lose a tick on a bump; that rule is not in the E10 state, so the effect draws no HP change (RULES: open for the designer and the GDD).',
         render=bump_render, pre=p1_pre('fx_shove_bump'), post=p1_pre('fx_shove_bump')))


# ============================================================================ M: rings step (END TURN: rings +1 and +2 come one ring in, the live schedule turns them)
def step_k(t):
    return e_io3(seg(t, 100, 480))


STEP_REG = ((FRHO > 268.0) & (FRHO < 389.5)).astype(np.float32)


def rings_step_core(t, reduce, marks, B_after, B_clean, box, ua):
    """B_after: the board after GUNS and LANDS (ring NOW clear, arcs and gun marks gone); B_clean: the same board with no units;
    ua: the unit alpha (B_after vs B_clean).  The Adjuster is drawn on both, so it never moves (no rule for the boss at END TURN)."""
    a = ua * STEP_REG
    base = mix(box.crop(B_after), box.crop(B_clean), box.crop(a[..., None])[..., 0])
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(move_layer(base, box, B_after, a), move_layer(base, box, B_after, a, d_ang=120.0, d_r=-57.0), k)
    else:
        k = step_k(t)
        sp = speed_of(step_k, t, 0.0035)
        ech = [(-57.0 * step_k(t - lg), 120.0 * step_k(t - lg), al * sp) for lg, al in zip(ECHO_LAG, ECHO_U)] if (marks and sp > 0.02) else []
        out = move_layer(base, box, B_after, a, d_r=-57.0 * k, d_ang=120.0 * k, echoes=ech, tint=SCHED)
    if marks:
        L = Layer(box)
        if reduce:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
            clock_arrow(L, arc_pts(426.5, 3, 3 + ARROW_STUB['rings']), AW, AH, int(255 * al))
        else:
            head = 3 + 114 * e_out3(seg(t, 0, 100))
            tail = 3 + 114 * step_k(t)
            head = min(head, tail + ARROW_STUB['rings'])
            al = 1 - seg(t, 480, 600)
            if head - tail > 3:
                clock_arrow(L, arc_pts(426.5, tail, head), AW, AH, int(255 * al))
        out = over(out, L.done())
    return out


def rings_step_frame(t, skin, box, reduce=False, marks=True):
    B, Cl = below(skin, 'p1_after'), below(skin, 'p1_clean')
    ua = unit_alpha(B, Cl, ('ua_after', skin))
    return rings_step_core(t, reduce, marks, B, Cl, box, ua)


def rings_step_render(t, skin, reduce=False, marks=True):
    box = FX['fx_rings_step']['_box']
    return comp(rings_step_frame(t, skin, box, reduce, marks), box.crop(above(skin, 'p1_after')))


def rings_pre(skin):
    b = FX['fx_rings_step']['_box']
    return comp(b.crop(below(skin, 'p1_after')), b.crop(above(skin, 'p1_after')))


def rings_post(skin):
    b = FX['fx_rings_step']['_box']
    return comp(rings_step_frame(600, skin, b, True, False), b.crop(above(skin, 'p1_after')))


reg(dict(id='fx_rings_step', fam='M', tier='state', title='Rings step in at END TURN', skins=['neutral', 'solace', 'meridian'], box=(36, 40, 1036, 1040), scale=0.46,
         src='f1 schedule [2, 0, 0]: at END TURN every unit comes one ring in and the live +2 turns it 2 sectors (120 deg) clockwise (Packet 5: s0 lands on 2, Packet 7: s5 lands on 1, both match the state)',
         still='After GUNS and LANDS (ring NOW is clear, the old landing arcs are gone): every unit cell on rings +1 and +2 spirals one ring in and 120 deg round; a 32 deg SCHEDULE-orange arrow stub runs ahead of them along the +2 THIS TURN tape and is eaten as they arrive. No echoes (review 2.10).',
         keep='SCHEDULE orange only (the clock moves the rings, VISUAL_PLAN E; never pink and never the corp colour); no echoes; the hand-off order GUNS > LANDS > RINGS STEP.',
         timing=dict(phases=[('anticipate: tape arrow draws', 0, 100, 'easeOutCubic'), ('spiral: -57 px, +120 deg', 100, 480, 'easeInOutCubic'),
                             ('settle: arrow fades', 480, 600, 'linear')], total=600),
         reduce_phases=[('arrow appears', 0, 100, 'easeOutCubic'), ('every cell dissolves to its new place', 100, 400, 'easeInOutCubic'), ('arrow fades', 400, 520, 'linear')],
         keys=[(0, 'after LANDS'), (90, 'tape arrow'), (240, 'spiral'), (290, 'peak speed'), (400, 'arriving'), (600, 'settled')],
         reduce_note='No spiral: the arrow stub appears (100 ms), every cell dissolves from its old place to its new one over 300 ms, the arrow fades (120 ms).',
         notes='Starts on the generator\'s own after-LANDS board (ring NOW empty, no gun marks, no landing arcs). The moved cells keep their old HOT/COLD/FAR grade and the schedule tape keeps its cells until the board redraws for the next turn; the landing arcs re-solve then. Ring +2 is left empty for fx_wave_enter. The Adjuster does not move (no rule for the boss at END TURN in the state).',
         render=rings_step_render, pre=rings_pre, post=rings_post))


# ============================================================================ M: hold (a 0 put in the live schedule cell)
_hold = {}


def hold_extent(skin):
    """the band span that changes between [2, 0, 0] and [0, 2, 0] (deg, clockwise from the live cell)"""
    if skin in _hold:
        return _hold[skin]
    d = np.abs(below(skin, 'p1') - below(skin, 'p1_hold')).max(2) > 10
    band = (FRHO > 380) & (FRHO < 432)
    ang = FANG[d & band]
    ang = np.where(ang > 300, ang - 360, ang)
    _hold[skin] = (float(np.percentile(ang, 0.5)), float(np.percentile(ang, 99.5)))
    return _hold[skin]


STAMP_XY = ppx(404.0, 7.2)


def hold_core(t, reduce, marks, B0, B1, box, skin):
    base, end = box.crop(B0), box.crop(B1)
    bandm = ring_mask(box, 380, 432, feather=1.0)
    a_lo, a_hi = hold_extent(skin)
    L = Layer(box)
    if reduce:
        k = e_io3(seg(t, 100, 400))
        out = mix(base, end, bandm * k)
        if marks:
            al = e_out3(seg(t, 0, 100)) * (1 - seg(t, 400, 520))
            clock_arrow(L, arc_pts(426.5, 12, 50), AW, AH, int(255 * al))
            out = over(out, L.done())
        return out
    front = a_lo + (a_hi + 2 - a_lo) * e_io3(seg(t, 100, 420))
    a_rel = np.where(box.ANG > 300, box.ANG - 360, box.ANG)
    wipe = np.clip((front - a_rel) / 5.0 + 0.5, 0, 1) * (a_rel < a_hi + 25) * (a_rel > a_lo - 25)
    out = mix(base, end, bandm * wipe)
    if not marks:
        return out
    if a_lo + 2 < front < a_hi:
        L.poly(band_pts(386, 424, front - 0.6, front + 0.2, 0.2), GUN_LIP, INK, 1.0, int(255 * (1 - seg(t, 400, 420))))
    # the stamp (K gunmetal, the hourglass in ink) slams onto the live cell and hands over to the printed HOLD glyph
    k = e_back(seg(t, 0, 100), 2.2)
    s = 1.6 - 0.6 * k
    al = clamp01(seg(t, 0, 40)) * (1 - seg(t, 100, 200))
    if al > 0:
        R0 = 11.5 * s
        L.circle((STAMP_XY[0] + 2.5, STAMP_XY[1] + 3.5), R0 + 1.5, fill=INK, a=int(140 * al))
        L.circle(STAMP_XY, R0 + 1.5, fill=INK, a=int(255 * al))
        L.circle(STAMP_XY, R0, fill=GUN, a=int(255 * al))
        L.circle(STAMP_XY, R0 - 3.0, outline=GUN_LIP, w=1.2, a=int(255 * al))
        hx, hy = STAMP_XY
        q = 7.0 * s
        L.poly([(hx - q, hy - q), (hx + q, hy - q), (hx, hy), (hx + q, hy + q), (hx - q, hy + q), (hx, hy)], INK, None, 1, int(255 * al))
        L.line([(hx - q - 1.5, hy - q), (hx + q + 1.5, hy - q)], INK, 2.0, int(255 * al))
        L.line([(hx - q - 1.5, hy + q), (hx + q + 1.5, hy + q)], INK, 2.0, int(255 * al))
    # the +2 slides one slot later: SCHEDULE arrow from the live cell to the new +2 start (40 deg on)
    if 100 <= t < 560:
        head = 12 + 38 * e_out3(seg(t, 100, 240))
        clock_arrow(L, arc_pts(426.5, max(12.0, head - ARROW_STUB['hold']), head), AW, AH, int(255 * (1 - seg(t, 420, 560))))
    return over(out, L.done())


def hold_render(t, skin, reduce=False, marks=True):
    box = FX['fx_hold']['_box']
    out = hold_core(t, reduce, marks, below(skin, 'p1'), below(skin, 'p1_hold'), box, skin)
    return comp(out, box.crop(above(skin, 'p1')))


def hold_post(skin):
    b = FX['fx_hold']['_box']
    return comp(b.crop(below(skin, 'p1_hold')), b.crop(above(skin, 'p1')))


reg(dict(id='fx_hold', fam='M', tier='state', title='Hold puts a 0 in the schedule', skins=['neutral', 'solace', 'meridian'], box=(380, 50, 1036, 990), scale=0.46,
         src='card Hold ("Pause the wave", cost 0): f1 schedule [2, 0, 0] becomes [0, 2, 0]; the end state is the generator\'s own render of [0, 2, 0]',
         still='A gunmetal hourglass stamp (the clock\'s own material) slams onto the live cell and hands over to the printed HOLD glyph; a 22 deg SCHEDULE-orange arrow stub runs the hold slot (40 deg) along the tape; the band turns over clockwise behind a thin gunmetal lip edge into the new schedule (HOLD THIS TURN, +2 NEXT, HOLD THEN).',
         keep='gunmetal stamp with the hourglass, SCHEDULE arrow stub (Hold\'s slide is the clock moving, VISUAL_PLAN E); the turned-over cells are the generator\'s own schedule drawing.',
         timing=dict(phases=[('stamp slams', 0, 100, 'easeOutBack 2.2'), ('stamp hands over to the printed HOLD glyph', 100, 200, 'linear'), ('band turns over, arrow stub runs the slot', 100, 420, 'easeInOutCubic'), ('arrow fades', 420, 560, 'linear')], total=560),
         reduce_phases=[('arrow appears', 0, 100, 'easeOutCubic'), ('band dissolves to the new schedule', 100, 400, 'easeInOutCubic'), ('arrow fades', 400, 520, 'linear')],
         keys=[(0, 'rest'), (50, 'stamp'), (180, 'arrow, wipe'), (300, 'turning over'), (420, 'turned'), (560, 'settled')],
         reduce_note='No stamp slam and no wipe: the arrow appears (100 ms) and the band dissolves to the new schedule over 300 ms; the arrow fades (120 ms).',
         notes='Only the schedule band (r 380-432) changes; the rest of the board is the decide plate.',
         render=hold_render, pre=p1_pre('fx_hold'), post=hold_post))


# ============================================================================ M: wave enter (W4 ticket into ring +2)
_tk = {}


def ticket_boxes(skin):
    """W6 / W5 / W4 ticket boxes and the feed arrow box, from the generator's own 'tickets' mask (left to right)"""
    if skin in _tk:
        return _tk[skin]
    m = cmask(skin, 'p1', 'tickets')
    col = m.any(0)
    runs, x = [], 0
    while x < W:
        if col[x]:
            x0 = x
            while x < W and col[x]:
                x += 1
            runs.append((x0, x))
        x += 1
    ys = np.nonzero(m.any(1))[0]
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    tw = runs[0][1] - runs[0][0]                      # the three tickets are one width; the W4 run also holds the feed arrow
    w6 = (runs[0][0], y0, runs[0][1], y1)
    w5 = (runs[1][0], y0, runs[1][1], y1)
    w4 = (runs[2][0], y0, runs[2][0] + tw, y1)
    feed = (runs[2][0] + tw, y0, runs[2][1], y1)
    out = dict(W6=w6, W5=w5, W4=w4, feed=feed)
    _tk[skin] = out
    return out


W4_CELLS = [(0, 1), (4, 2)]            # lineup W4: Jammer w1 s0, Jammer w2 s4


def _sprite(full, b):
    x0, y0, x1, y1 = b
    return full[y0:y1, x0:x1].copy()


def _paste_sprite(out, box, spr, cx, cy, s=1.0, al=1.0, tint=None, tk=0.35):
    h, w = spr.shape[:2]
    xs = (box.X - cx) / s + w / 2.0
    ys = (box.Y - cy) / s + h / 2.0
    m = (xs >= 0) & (xs <= w - 1) & (ys >= 0) & (ys <= h - 1)
    if not m.any() or al <= 0:
        return out
    rgb = np.empty(box.X.shape + (3,), np.float32)
    for c in range(3):
        rgb[..., c] = ndi.map_coordinates(spr[..., c], [ys, xs], order=1, mode='nearest')
    if tint is not None:
        rgb = rgb * (1 - tk) + np.array(tint, np.float32) * tk
    edge = np.clip(np.minimum.reduce([xs + 0.5, w - 0.5 - xs, ys + 0.5, h - 0.5 - ys]), 0, 1)
    a = edge * m * al
    return out * (1 - a[..., None]) + rgb * a[..., None]


def glass_gain(skin, B_occ, B_empty):
    """ring +2 occupied glass vs empty glass, per channel (median over Packet 7's cell, f1 ring +2 sector 5, marks excluded)"""
    k = ('gg', skin)
    if k in _full:
        return _full[k]
    m = (FRHO > 340) & (FRHO < 372) & (FANG > 280) & (FANG < 320)
    occ = B_occ[m]
    emp = B_empty[m]
    lo = np.percentile(occ.sum(1), 20)
    hi = np.percentile(occ.sum(1), 70)
    sel = (occ.sum(1) >= lo) & (occ.sum(1) <= hi)
    g = np.median(occ[sel], 0) / np.maximum(np.median(emp[sel], 0), 1.0)
    _full[k] = g.astype(np.float32)
    return _full[k]


def wave_core(t, reduce, marks, base_full, B_after, B_clean, p1_full, box, skin):
    """base_full: the board after RINGS STEP (full frame).  The tickets come from p1_full (the queue as drawn).  The new W4 cells take
    the ring +2 occupied glass value (lit glass, VISUAL_PLAN A.2) with an enamel outline; the corp hue is on the scan line that draws
    the cell edge (DR-6: hue on cell edges only); the feed arrow and ticket echoes are neutral ENAMEL (VISUAL_PLAN F: the feed is K)."""
    tb = ticket_boxes(skin)
    edge = CORP_EDGE[skin]
    out = box.crop(base_full)
    w4, w5, w6 = (_sprite(p1_full, tb[n]) for n in ('W4', 'W5', 'W6'))
    cxs = {n: ((tb[n][0] + tb[n][2]) / 2.0, (tb[n][1] + tb[n][3]) / 2.0) for n in ('W4', 'W5', 'W6')}
    entry = ppx(486, -19.5)
    cx4, cy4 = cxs['W4']
    path = [(cx4, cy4), (cx4 + 60, cy4 + 6), (entry[0] - 12, entry[1] - 18), entry]
    L = Layer(box)

    def blank(nm, al=1.0):
        x0, y0, x1, y1 = tb[nm]
        Lb = Layer(box)
        Lb.d.rounded_rectangle([(x0 - box.x0) * 3, (y0 - box.y0) * 3, (x1 - box.x0) * 3, (y1 - box.y0) * 3], radius=12, fill=(14, 16, 24, int(235 * al)),
                               outline=(70, 78, 94, int(255 * al)), width=4)
        return Lb.done()
    if reduce:
        k = e_io3(seg(t, 100, 400))
        for nm in ('W4', 'W5', 'W6'):
            out = over(out, blank(nm, k))
        out = _paste_sprite(out, box, w4, cx4, cy4, 1.0, 1 - k)
        out = _paste_sprite(out, box, w5, cx4, cy4, 1.0, k)
        out = _paste_sprite(out, box, w6, cxs['W5'][0], cy4, 1.0, k)
        out = _paste_sprite(out, box, w5, cxs['W5'][0], cy4, 1.0, 1 - k)
        out = _paste_sprite(out, box, w6, cxs['W6'][0], cy4, 1.0, 1 - k)
        cells_k = k
    else:
        if marks:
            fb = tb['feed']
            lit_al = 1 - seg(t, 480, 600)
            nlit = 3 if t >= 80 else int(min(3, t // 27 + 1))
            for i in range(nlit):
                x = fb[0] + 8 + i * 22
                ym = (fb[1] + fb[3]) / 2.0
                pts = [(x, ym - 12), (x + 16, ym), (x, ym + 12)]
                L.line(pts, INK, 6.0, int(255 * lit_al))
                L.line(pts, ENAMEL, 2.5, int(255 * lit_al))
        k4 = e_io3(seg(t, 80, 360))
        out = over(out, blank('W4'))
        out = over(out, blank('W5', seg(t, 360, 400)))
        out = over(out, blank('W6', seg(t, 360, 400)))
        if t < 80:
            out = _paste_sprite(out, box, w4, cx4, cy4, 1.0 + 0.06 * e_out3(seg(t, 0, 80)))
        elif t < 420:
            pos = path_cut(path, k4)[-1]
            sp = speed_of(lambda q: e_io3(seg(q, 80, 360)) * 300, t, 1.0)
            if marks:
                for lg, al in zip(ECHO_LAG, ECHO_U):
                    kk = e_io3(seg(t - lg, 80, 360))
                    pe_ = path_cut(path, kk)[-1]
                    out = _paste_sprite(out, box, w4, pe_[0], pe_[1], 1.06 - 0.5 * kk, al * sp, tint=ENAMEL)
            fade = 1 - seg(t, 340, 420)
            out = _paste_sprite(out, box, w4, pos[0], pos[1], (1.06 - 0.5 * k4) * (1 - 0.4 * seg(t, 340, 420)), fade)
        kq = e_io3(seg(t, 360, 540))
        if t >= 360:
            sp = speed_of(lambda q: e_io3(seg(q, 360, 540)) * 92, t, 0.9)
            x5, x6 = cxs['W5'][0], cxs['W6'][0]
            if marks:
                for lg, al in zip(ECHO_LAG, ECHO_U):
                    kk = e_io3(seg(t - lg, 360, 540))
                    out = _paste_sprite(out, box, w5, x5 + (cx4 - x5) * kk, cy4, 1.0, al * sp, tint=ENAMEL)
                    out = _paste_sprite(out, box, w6, x6 + (x5 - x6) * kk, cy4, 1.0, al * sp, tint=ENAMEL)
            out = _paste_sprite(out, box, w5, x5 + (cx4 - x5) * kq, cy4)
            out = _paste_sprite(out, box, w6, x6 + (x5 - x6) * kq, cy4)
        cells_k = seg(t, 300, 480)
    out = over(out, L.done())
    # the new W4 cells: lit ring +2 glass (gain over the clean empty glass), drawn in by a scan line in the corp's cell-edge hue
    gain = glass_gain(skin, below(skin, 'p1_after'), B_clean)
    lit = np.clip(box.crop(B_clean) * gain, 0, 255)
    for (s, w) in W4_CELLS:
        a0, a1 = 60 * s - 30 + 1.5, 60 * (s + w) - 30 - 1.5
        kk = cells_k if reduce else e_out3(cells_k)
        if kk <= 0:
            continue
        am = a0 + (a1 - a0) * (1.0 if reduce else kk)
        span = (am - a0) % 360
        inside = (((box.ANG - a0) % 360) <= span) & (box.RHO > 332) & (box.RHO < 381)
        al = kk if reduce else 1.0
        out = mix(out, lit, inside.astype(np.float32) * al)
        L3 = Layer(box)
        aa = int(255 * al)
        L3.line(arc_pts(381, a0, am), INK, 5.5, aa)
        L3.line(arc_pts(332, a0, am), INK, 5.5, aa)
        L3.line([ppx(332, a0), ppx(381, a0)], INK, 5.5, aa)
        L3.line(arc_pts(381, a0, am), ENAMEL, 2.0, aa)
        L3.line(arc_pts(332, a0, am), ENAMEL, 2.0, aa)
        L3.line([ppx(332, a0), ppx(381, a0)], ENAMEL, 2.0, aa)
        if not reduce and kk < 1 and marks:
            L3.line([ppx(330, am), ppx(383, am)], INK, 6.0)
            L3.line([ppx(330, am), ppx(383, am)], edge, 3.0)
        elif kk >= 1 or reduce:
            L3.line([ppx(332, a1), ppx(381, a1)], INK, 5.5, aa)
            L3.line([ppx(332, a1), ppx(381, a1)], ENAMEL, 2.0, aa)
        out = over(out, L3.done())
    # the Jammer glyphs from the W4 ticket drop into the cells
    gk = (cells_k if reduce else seg(t, 400, 480))
    if gk > 0:
        x0, y0, x1, y1 = tb['W4']
        hw = (x1 - x0) // 2
        g1 = w4[18:y1 - y0 - 14, 4:hw]
        g2 = w4[18:y1 - y0 - 14, hw:(x1 - x0) - 4]
        for (s, w), g in zip(W4_CELLS, (g1, g2)):
            am = 60 * s - 30 + 30 * w
            x, y = ppx(356.5, am)
            out = _paste_sprite(out, box, g, x, y, 1.3, gk)
    return out


def wave_render(t, skin, reduce=False, marks=True):
    box = FX['fx_wave_enter']['_box']
    ck = ('wave_base', skin)
    if ck not in _full:
        rb = Box(0, 0, W, H)
        bf = below(skin, 'p1_after').copy()
        r = Box(36, 40, 1036, 1040)
        bf[r.y0:r.y1, r.x0:r.x1] = rings_step_frame(600, skin, r, True, False)
        _full[ck] = bf
    out = wave_core(t, reduce, marks, _full[ck], below(skin, 'p1_after'), below(skin, 'p1_clean'), below(skin, 'p1'), box, skin)
    return comp(out, box.crop(above(skin, 'p1_after')))


def wave_pre(skin):
    box = FX['fx_wave_enter']['_box']
    wave_render(0, skin, True, False)
    return comp(box.crop(_full[('wave_base', skin)]), box.crop(above(skin, 'p1_after')))


def wave_post(skin):
    return wave_render(600, skin, True, False)


reg(dict(id='fx_wave_enter', fam='M', tier='state', title='The next wave enters ring +2', skins=['neutral', 'solace', 'meridian'], box=(0, 0, 740, 640), scale=0.62,
         src='state: queue ticket W4 (lineup: Jammer w1 s0, Jammer w2 s4) enters ring +2 at RINGS STEP ("W4 enters"), after fx_rings_step',
         still='The feed arrow lights (ENAMEL, the queue is K), the W4 ticket lifts and rides the arrow into the bezel entry, a scan line in the corp\'s cell-edge hue draws each new ring +2 cell (lit ring +2 glass, enamel outline), the Jammer glyphs drop in, and W5 / W6 move up one slot. No echoes (review 2.10).',
         keep='the corp hue only on the scan line that draws the new cell edges (DR-6: rim, lip, crest, cell edges); the feed arrow neutral; solid ticket edges, no dashes.',
         timing=dict(phases=[('feed arrow lights, ticket lifts', 0, 80, 'step 27 ms / easeOutCubic'), ('ticket rides into the entry', 80, 360, 'easeInOutCubic'),
                             ('cells scan in, glyphs drop', 300, 480, 'easeOutCubic'), ('queue moves up one slot', 360, 540, 'easeInOutCubic'), ('settled', 540, 600, '-')], total=600),
         reduce_phases=[('ticket fades out, cells and queue cross-fade in', 100, 400, 'easeInOutCubic'), ('settled', 400, 600, '-')],
         keys=[(0, 'after RINGS STEP'), (70, 'arrow lit'), (220, 'ticket rides'), (380, 'scan in'), (460, 'queue moves'), (600, 'settled')],
         reduce_note='No travel: the W4 ticket fades out, the new cells fade in with their outlines and glyphs, and W5 / W6 cross-fade one slot right, all over 300 ms.',
         notes='The new cells are lit glass with an enamel outline and the ticket glyphs; their tokens and HP come from the next board redraw (no HP is drawn: the state has no W4 HP yet). The vacated queue slot is an empty dark slot (no plate exists without the tickets).',
         render=wave_render, pre=wave_pre, post=wave_post))


# ============================================================================ P: protect.  Own stock (review 3.10): pink-tinted paper P_STOCK, never card bone;
# 3.4 px ink key line, a pink double line (L10), ink rivets, paper fibre grain, a hard offset shadow; no glow, no starburst (D), no red (H).
RED_FIN, RED_FOUT = (0, 200), (300, 600)        # reduce motion: appear 0-200 linear, hold, dissolve 300-600 linear, and no hard offset shadow
# (tune_red.py / tune_red2.py: with the shadow the plate's light fill and its dark shadow swing opposite ways at once, 2 flashes per s on
#  shield and brace in reduce motion against 1 in full motion; without it both count 1)
RED_SHADOW = 0.0


# per block (tune_red3.py, 2026-11-04): appear window, dissolve window; each counts 1 flash per s in reduce motion, as its full motion does
RED_WIN = dict(shield=((0, 150), (250, 600)), brace=((0, 300), (300, 600)), soak=((0, 200), (300, 600)))


def _red_k(t, w=None):
    fin, fout = RED_WIN[w] if w is not None else (RED_FIN, RED_FOUT)
    return seg(t, *fin) * (1 - seg(t, *fout))


_grain = {}


def stock_grain(lp, seed):
    """paper fibre on the P stock pixels of an RGBA layer: +-5 % value, 1.4 px correlated, seeded (determinism)"""
    k = (lp.shape, seed)
    if k not in _grain:
        rng = np.random.default_rng(seed)
        n = ndi.gaussian_filter(rng.standard_normal(lp.shape[:2]).astype(np.float32), 1.4)
        _grain[k] = n / max(1e-6, n.std())
    n = _grain[k]
    rgb = lp[..., :3]
    near = np.abs(rgb - np.array(P_STOCK, np.float32)).max(2) < 40
    g = 1 + 0.05 * np.clip(n, -2.5, 2.5) * near
    lp = lp.copy()
    lp[..., :3] = np.clip(rgb * g[..., None], 0, 255)
    return lp


def plate_shape(L, pts, al=1.0, rivets=(), inset_pts=None):
    a = int(255 * al)
    L.poly(pts, P_STOCK, INK, 3.4, a)
    for ip in inset_pts or ():
        L.poly(ip, None, PINK, 1.6, a)
    for (x, y) in rivets:
        L.circle((x, y), 2.6, fill=INK, a=a)
        L.circle((x - 0.6, y - 0.6), 1.1, fill=P_STOCK_D, a=a)


def chevron_pts(r, ang, size=9.0):
    return [ppx(r + size, ang - size * 0.9 / r * 57.3 * 1.6), ppx(r, ang), ppx(r + size, ang + size * 0.9 / r * 57.3 * 1.6)]


def draw_chev(L, r, ang, size=9.0, al=1.0, col=HARM_UP):
    pts = chevron_pts(r, ang, size)
    L.line(pts, INK, 7.0, int(255 * al))
    L.line(pts, col, 3.6, int(255 * al))


def sparks(L, p, ang_out, k, n=5, length=12.0, al=1.0):
    """paper spark ticks thrown back from an impact point (P: no starburst, no white flash)"""
    for i in range(n):
        a = math.radians(ang_out + (i - (n - 1) / 2) * 26)
        r0 = 4 + 9 * k
        r1 = r0 + length * (1 - 0.5 * k)
        x0, y0 = p[0] + r0 * math.sin(a), p[1] - r0 * math.cos(a)
        x1, y1 = p[0] + r1 * math.sin(a), p[1] - r1 * math.cos(a)
        L.line([(x0, y0), (x1, y1)], INK, 3.6, int(200 * al))
        L.line([(x0, y0), (x1, y1)], P_STOCK, 1.8, int(255 * al))


BLOCK_TINT = 0.0             # review 2.10: the flat pink wedge tint is retired (a block sits under a kill), as on the C/D/H/L sheet
SOAK_WASH = 0.0              # the same for the SOAK wash on the wedge
SH_A = 60.0                  # f2: Worm 3 lands 3 on sector 1 SHIELD: absorbed 2 (+ soaked 1, fx_soak_take)
SH_R = (186.0, 204.0, 13.0)  # plate r_in, r_out, half angle: outside the slice pips (r 163-171), on the trim band (review 2.10: was 174-204 x 23 deg)


def shield_core(t, reduce, marks, B, box, A=SH_A, n_abs=2):
    base = box.crop(B)
    if not marks:
        return base
    r_in, r_out, half = SH_R
    L = Layer(box)
    if reduce:
        pa = _red_k(t, 'shield')
        tint_al, chev_al = 0.14 * BLOCK_TINT * pa, pa
        chev_r = [r_out + 9, r_out + 24]
        ps, impact_k = 1.0, -1
    else:
        k = e_in2(seg(t, 0, 160))
        chev_r = [470 - (470 - (r_out + 9)) * k, 485 - (485 - (r_out + 24)) * k]
        chev_al = 1 - seg(t, 170, 230)
        ps = 1.2 - 0.2 * e_back(seg(t, 110, 170), 2.0)
        pa = seg(t, 110, 130) * (1 - seg(t, 440, 600))
        tint_al = 0.14 * BLOCK_TINT * seg(t, 160, 190) * (1 - seg(t, 440, 600))
        impact_k = seg(t, 160, 280)
    if tint_al > 0:
        Lt = Layer(box)
        Lt.poly(band_pts(64, 196, A - 29, A + 29), PINK, None, 1, 255)
        base = over(base, Lt.done(), tint_al)
    if pa > 0:
        rc = (r_in + r_out) / 2
        cx, cy = ppx(rc, A)

        def sc(pts):
            return [(cx + (x - cx) * ps, cy + (y - cy) * ps) for x, y in pts]
        Lp = Layer(box)
        outer = sc(band_pts(r_in, r_out, A - half, A + half, 1.0))
        ins1 = sc(band_pts(r_in + 4.0, r_out - 4.0, A - half + 1.6, A + half - 1.6, 1.0))
        ins2 = sc(band_pts(r_in + 7.0, r_out - 7.0, A - half + 2.7, A + half - 2.7, 1.0))
        riv = sc([ppx(rc, A - half + 4.5), ppx(rc, A + half - 4.5)])
        plate_shape(Lp, outer, 1.0, riv, [ins1, ins2])
        if t >= 200 or reduce:
            for i in range(n_abs):                    # absorbed N: N engraved ticks
                dd = (i - (n_abs - 1) / 2) * 4.4
                Lp.line([ppx(rc - 6, A + dd), ppx(rc + 6, A + dd)], INK, 2.2)
        lp = stock_grain(Lp.done(), 311)
        base = over(base, shadow(lp, (3, 5), 0.55 * (RED_SHADOW if reduce else 1.0)), pa)
        base = over(base, lp, pa)
    for r_ in chev_r:
        if chev_al > 0:
            draw_chev(L, r_, A, 9.0, chev_al)
    if not reduce and 0 <= impact_k < 1 and t >= 160:
        sparks(L, ppx(r_out + 2, A), A, impact_k, 5, 12.0, 1 - impact_k)
    return over(base, L.done())


def p3_pre(fid):
    def f(skin):
        b = FX[fid]['_box']
        return comp(b.crop(below(skin, 'p3')), b.crop(above(skin, 'p3')))
    return f


def shield_render(t, skin, reduce=False, marks=True):
    box = FX['fx_shield_block']['_box']
    return comp(shield_core(t, reduce, marks, below(skin, 'p3'), box), box.crop(above(skin, 'p3')))


reg(dict(id='fx_shield_block', fam='P', tier='block', title='SHIELD slice absorbs a landing', skins=['neutral', 'solace', 'meridian'], box=(560, 300, 900, 600), scale=1.0,
         src='f2: Worm 3 lands 3 on sector 1 SHIELD: absorbed 2 (log hit 1; the third hit is the soak, fx_soak_take); eq absorbed 2',
         still='The two incoming chevrons run down the sector axis across the corp rings and stop dead on one small intact plate of the P stock (pink-tinted paper #F6C8DE, fibre grain) seated on the trim band of the wedge (r 186-204 x 26 deg, clear of the icon and the pips); paper spark ticks fly back; two engraved ticks = absorbed 2. No wedge tint, no red on the plate, no glow, no starburst (review 2.10, 3.10).',
         keep='ONE intact plate (never cracked), its own pink-tinted paper stock with fibre grain (never card bone), ink key line + pink double line + rivets, hard offset shadow, paper sparks, no red on the plate, no glow; a block sits under every kill and hit (review 2.10).',
         timing=dict(phases=[('chevrons arrive', 0, 160, 'easeInQuad'), ('plate slams (1.2 to 1.0)', 110, 170, 'easeOutBack 2.0'), ('impact: stop dead, sparks', 160, 280, 'linear'),
                             ('hold', 280, 440, '-'), ('plate lifts off', 440, 600, 'linear')], total=600),
         reduce_phases=[('plate, ticks and stopped chevrons appear', 0, 150, 'linear'), ('hold', 150, 250, '-'), ('dissolve', 250, 600, 'linear')],
         keys=[(80, 'chevrons arrive'), (130, 'plate slams'), (175, 'impact'), (230, 'sparks'), (380, 'hold'), (600, 'cleared')],
         reduce_note='No slam and no sparks: the plate, its ticks and the two chevrons stopped at the plate edge appear over 150 ms (linear), hold 100 ms, and dissolve over 350 ms (linear); no hard shadow in reduce motion. Measured: this form counts 1 flash per s, as full motion (the 0-200 / 300-600 form counted 2).',
         notes='Base is the resolve plate p3 (state f2). Moved from sector 3 (Packet 5, which lands NEXT turn, k = 1) to sector 1, the landing that happens at this END TURN, so the strip and the resolve beat show the same block.',
         render=shield_render, pre=p3_pre('fx_shield_block'), post=p3_pre('fx_shield_block')))


BR_A = 120.0                 # f2: Brace on sector 2 TURRET, Worm 3 lands 3 there: braced 3, through 0
BR_ARM = 20.0                # px: each clamp bracket's arms
BR_STAMP = (435.0, 125.9)    # the board's own brace glyph on the sector 2 landing arc (p3): the stamp lands on it and hands over


def brace_core(t, reduce, marks, B, box, A=BR_A):
    base = box.crop(B)
    if not marks:
        return base
    lane_r0, bar_r = 436.0, 205.0
    if reduce:
        clamp_al = _red_k(t, 'brace')
        stamp_al = clamp_al
        lane_k, cs, stamp_s, crumple = 1.0, 1.0, 1.0, 1.0
        chev_pos = [bar_r + 8, bar_r + 13, bar_r + 18]
        chev_al = clamp_al
        lane_al = clamp_al
    else:
        lane_k = e_out3(seg(t, 0, 80))
        lane_al = 1 - seg(t, 460, 600)
        cs = 1.12 - 0.12 * e_back(seg(t, 60, 180), 2.0)
        clamp_al = seg(t, 60, 90) * (1 - seg(t, 460, 600))
        kk = e_in2(seg(t, 80, 260))
        crumple = seg(t, 260, 330)
        sp0 = [lane_r0 - 6, lane_r0 + 18, lane_r0 + 42]
        tgt = [bar_r + 10 + 14 * i * (1 - crumple) + 4 * i * crumple for i in range(3)]
        chev_pos = [s0 + (tg - s0) * kk for s0, tg in zip(sp0, tgt)]
        chev_al = 1 - seg(t, 330, 400)
        stamp_s = 1.2 - 0.2 * e_back(seg(t, 330, 400), 2.2)
        stamp_al = seg(t, 330, 350) * (1 - seg(t, 460, 600))      # hands over to the board's printed brace glyph
    L = Layer(box)
    if lane_al > 0:
        pts = path_cut([ppx(lane_r0, A), ppx(bar_r + 6, A)], lane_k)
        L.line(pts, INK, 5.0, int(255 * lane_al))
        L.line(pts, HARM, 2.0, int(255 * lane_al))
    base = over(base, L.done())
    if clamp_al > 0:
        Lc = Layer(box)
        cx, cy = ppx(130.0, A)

        def sc(pts):
            return [(cx + (x - cx) * cs, cy + (y - cy) * cs) for x, y in pts]
        a0, a1, r0, r1 = A - 30.5, A + 30.5, 62.0, 201.0
        # review 2.10: four clamp brackets on the wedge corners (was a P-stock frame round the whole wedge, louder than a kill)
        ro, ri, ao0, ao1 = r1 - 4.5, r0 + 4.5, a0 + 2.2, a1 - 2.2
        arm_o, arm_i = BR_ARM / ro * 57.3, (BR_ARM + 6) / ri * 57.3
        brackets = [[ppx(ro - BR_ARM, ao0), ppx(ro, ao0)] + arc_pts(ro, ao0, ao0 + arm_o, 0.5),
                    [ppx(ro - BR_ARM, ao1), ppx(ro, ao1)] + arc_pts(ro, ao1 - arm_o, ao1, 0.5)[::-1],
                    [ppx(ri + BR_ARM, ao0 + 6.5), ppx(ri, ao0 + 6.5)] + arc_pts(ri, ao0 + 6.5, ao0 + 6.5 + arm_i, 0.5),
                    [ppx(ri + BR_ARM, ao1 - 6.5), ppx(ri, ao1 - 6.5)] + arc_pts(ri, ao1 - 6.5 - arm_i, ao1 - 6.5, 0.5)[::-1]]
        for bk in brackets:
            Lc.line(sc(bk), INK, 9.0)
        for bk in brackets:
            Lc.line(sc(bk), P_STOCK, 4.5)
        for p_ in sc([ppx(ro, ao0), ppx(ro, ao1), ppx(ri, ao0 + 6.5), ppx(ri, ao1 - 6.5)]):
            Lc.circle(p_, 2.6, fill=INK)
            Lc.circle((p_[0] - 0.6, p_[1] - 0.6), 1.1, fill=P_STOCK_D)
        bar = sc(band_pts(bar_r - 2.0, bar_r + 3.0, A - 7.0, A + 7.0, 0.5))
        Lc.poly(bar, P_STOCK, INK, 2.6)
        lc = stock_grain(Lc.done(), 313)
        base = over(base, shadow(lc, (3, 5), 0.55 * (RED_SHADOW if reduce else 1.0)), clamp_al)
        base = over(base, lc, clamp_al)
    L2_ = Layer(box)
    if chev_al > 0:
        for r_ in chev_pos:
            draw_chev(L2_, r_, A, 9.0 * (1 - 0.45 * crumple), chev_al)
    if stamp_al > 0:
        sx, sy = ppx(*BR_STAMP)
        q = 8.0 * stamp_s
        k3 = 3
        L2_.d.rectangle([(sx - q + 2.5 - box.x0) * k3, (sy - q + 3.5 - box.y0) * k3, (sx + q + 2.5 - box.x0) * k3, (sy + q + 3.5 - box.y0) * k3], fill=INK + (int(140 * stamp_al * (RED_SHADOW if reduce else 1.0)),))
        L2_.d.rectangle([(sx - q - box.x0) * k3, (sy - q - box.y0) * k3, (sx + q - box.x0) * k3, (sy + q - box.y0) * k3], fill=P_STOCK + (int(255 * stamp_al),), outline=INK + (int(255 * stamp_al),), width=8)
        b = q * 0.55
        for sgn in (-1, 1):
            L2_.line([(sx + sgn * b * 0.4, sy - b), (sx + sgn * b, sy - b), (sx + sgn * b, sy + b), (sx + sgn * b * 0.4, sy + b)], INK, 2.0, int(255 * stamp_al))
    return over(base, L2_.done())


def brace_render(t, skin, reduce=False, marks=True):
    box = FX['fx_brace_block']['_box']
    return comp(brace_core(t, reduce, marks, below(skin, 'p3'), box), box.crop(above(skin, 'p3')))


reg(dict(id='fx_brace_block', fam='P', tier='block', title='Brace blocks a whole landing', skins=['neutral', 'solace', 'meridian'], box=(560, 440, 1010, 860), scale=0.85,
         src='f2: Brace on sector 2 TURRET (brace_sectors 2, braced_hit true): Worm 3 lands 3 there, braced 3, through 0 (log hit 2)',
         still='The landing lane runs from the arc down the sector axis to the tower; four clamp brackets of the P stock (ink key, rivets, fibre, hard shadow) close on the corners of the TURRET wedge with the icon left clear; the three chevrons (braced 3) stop on a flat stop bar and crumple; a clamp stamp slams onto the board\'s brace glyph on the arc and hands over to it.',
         keep='the clamp brackets hold the whole wedge at its four corners, icon visible; the lane stops at the bar (never through); P stock, not card bone; the stamp lands on the printed brace glyph; a block sits under every kill and hit (review 2.10).',
         timing=dict(phases=[('lane draws in', 0, 80, 'easeOutCubic'), ('clamp brackets close (1.12 to 1.0)', 60, 180, 'easeOutBack 2.0'), ('chevrons run the lane', 80, 260, 'easeInQuad'),
                             ('chevrons crumple on the bar', 260, 330, 'linear'), ('stamp slams on the arc glyph (1.2 to 1.0)', 330, 400, 'easeOutBack 2.2'), ('hold', 400, 460, '-'),
                             ('clamp, bar, lane and stamp lift off (the printed glyph stays)', 460, 600, 'linear')], total=600),
         reduce_phases=[('lane, clamp brackets, bar, crumpled chevrons and stamp appear', 0, 300, 'linear'), ('dissolve', 300, 600, 'linear')],
         keys=[(0, 'rest'), (90, 'lane, clamp'), (200, 'chevrons run'), (300, 'crumple'), (380, 'stamp'), (600, 'glyph stays')],
         reduce_note='No closing or crumple motion: lane, clamp, bar, the crumpled chevrons and the stamp appear over 300 ms with no hard shadow and dissolve over 300 ms (measured 1 flash per s, as full motion; with a 200 ms appear it counted 2); the board\'s own brace glyph and brace edge stay.',
         notes='Base is the resolve plate p3 (state f2), which already prints the brace glyph on the arc and the brace double line on the TURRET rim; the effect hands over to both.',
         render=brace_render, pre=p3_pre('fx_brace_block'), post=p3_pre('fx_brace_block')))


SOAK_PIP = (163.5, 171.0, 61.0, 74.0)     # the soaked pip of sector 1 on the rebuilt tower (r0, r1, a0, a1), where p3 prints its SOAK hatch


def soak_core(t, reduce, marks, B, box, A=SH_A):
    base = box.crop(B)
    if not marks:
        return base
    mouth_r, apex_r, mouth_h = 204.0, 158.0, 32.0
    L = Layer(box)
    if reduce:
        k = _red_k(t, 'soak')
        fk, wash, f_al, pip_k, flow, chev = 1.0, 0.14 * SOAK_WASH * k, k, 1.0, 0.25, None
        pip_al = k
    else:
        ck = e_in2(seg(t, 0, 120))
        cr = 300 - (300 - (mouth_r + 6)) * ck
        sh = seg(t, 220, 320)
        chev = (cr - 26 * sh, 1 - 0.7 * sh, sh)
        chev_al = 1 - seg(t, 290, 320)
        fk = e_out3(seg(t, 80, 220))
        f_al = seg(t, 80, 110) * (1 - seg(t, 470, 600))
        wash = 0.14 * SOAK_WASH * seg(t, 220, 250) * (1 - seg(t, 470, 600))
        pip_k = e_out3(seg(t, 300, 420))
        pip_al = 1 - seg(t, 470, 600)
        flow = (t - 220) / 300.0
    if wash > 0:
        Lw = Layer(box)
        Lw.poly(band_pts(64, 196, A - 29, A + 29), SOAK, None, 1, 255)
        base = over(base, Lw.done(), wash)
    if f_al > 0:
        Lf = Layer(box)
        tip = mouth_r - (mouth_r - apex_r) * fk
        hw = mouth_h / mouth_r * 57.3
        Lf.poly([ppx(mouth_r, A - hw), ppx(mouth_r, A + hw), ppx(tip, A)], SOAK, INK, 3.2)
        Lf.poly([ppx(mouth_r - 2.5, A - hw * 0.78), ppx(mouth_r - 2.5, A + hw * 0.78), ppx(tip + 4, A)], None, P_STOCK, 1.2)
        if fk > 0.6:
            for i in range(2):
                ph = (flow + i * 0.5) % 1.0
                rr = mouth_r - 6 - (mouth_r - apex_r - 14) * ph
                w_ = 0.55 * (rr - tip) / (mouth_r - tip) * hw
                if w_ > 0.6:
                    Lf.line([ppx(rr + 3.0, A - w_), ppx(rr - 1.5, A), ppx(rr + 3.0, A + w_)], P_STOCK, 2.2)
        base = over(base, Lf.done(), f_al)
    if pip_k > 0 and pip_al > 0:
        r0, r1, a0, a1 = SOAK_PIP
        Lp = Layer(box)
        Lp.poly(band_pts(r0, r1, a0, a0 + (a1 - a0) * pip_k, 0.5), SOAK, INK, 1.2, int(255 * pip_al * 0.85))
        base = over(base, Lp.done())
    if chev is not None and chev_al > 0:
        r_, s_, sh = chev
        col = tuple(int(HARM_UP[i] + (SOAK[i] - HARM_UP[i]) * sh) for i in range(3))
        draw_chev(L, r_, A, 9.0 * s_, chev_al, col)
    return over(base, L.done())


def soak_render(t, skin, reduce=False, marks=True):
    box = FX['fx_soak_take']['_box']
    return comp(soak_core(t, reduce, marks, below(skin, 'p3'), box), box.crop(above(skin, 'p3')))


reg(dict(id='fx_soak_take', fam='P', tier='block', title='A soaked slice takes the overflow', skins=['neutral'], box=(585, 345, 805, 565), scale=1.8,
         src='f2: sector 1 SHIELD soaked 1 (Worm 3 lands 3: absorbed 2, soak 1, through 0; soak_sectors [1])',
         still='The overflow chevron reaches the rim; a symmetric SOAK-blue funnel (ink key, P-stock inner line) draws in on the wedge axis from the rim toward the icon; the chevron shrinks into the mouth and turns SOAK; P-stock flow chevrons run inward; the soaked pip fills SOAK and hands over to the board\'s own SOAK hatch. No SOAK wash on the wedge (review 2.10).',
         keep='funnel symmetric on the axis, rim to icon; SOAK #3A7EF3 only (never pink); flow chevrons point inward; the pip ends in the board\'s own SOAK hatch.',
         timing=dict(phases=[('overflow chevron arrives', 0, 120, 'easeInQuad'), ('funnel draws in', 80, 220, 'easeOutCubic'), ('chevron shrinks into the mouth', 220, 320, 'linear'),
                             ('pip fills', 300, 420, 'easeOutCubic'), ('hold, flow scrolls', 420, 470, 'linear'), ('funnel and pip fill lift off', 470, 600, 'linear')], total=600),
         reduce_phases=[('funnel and filled pip appear', 0, 200, 'linear'), ('hold', 200, 300, '-'), ('dissolve', 300, 600, 'linear')],
         keys=[(60, 'chevron arrives'), (150, 'funnel draws'), (280, 'into the mouth'), (360, 'pip fills'), (450, 'hold'), (600, 'cleared')],
         reduce_note='No travel: the funnel and the filled pip appear over 200 ms with the flow chevrons still, hold, and dissolve over 300 ms. The overflow chevron is not shown.',
         notes='Player-only (the tower wedge): the same on every corp skin, so drawn on the neutral board only. Base p3 (f2).',
         render=soak_render, pre=p3_pre('fx_soak_take'), post=p3_pre('fx_soak_take')))


# ============================================================================ S: trace add (Trigger, +1 Trace).  The one M/P/S/T effect drawn OVER the HUD and the hand
# (REVIEW_RESPONSE 1.6: hp_through, refund and trace_add may cross): it glitches the card that was played and lights the HUD's own pip.
TR_ROW = {'p1': 416.5, 'p2': 550.5, 'p3': 612.5}
TR_X0, TR_PITCH = {'p1': 1436.5, 'p2': 1422.5, 'p3': 1422.5}, 28.0
TR_CARD = (1267, 762, 1476, 1052)        # the Trigger card in the p1 hand (generator mask card_2)
TR_ROWS = 1                              # review 2.10: one glitch band per 33 ms step (was 3, 5-11 px; now 4-7 px)
TR_POP = [1.45, 1.2, 1.0, 1.0]           # the pip's stepped pop (was 1.7, 1.35)


def glitch(img_c, box, rows, region):
    out = img_c.copy()
    x0, y0, x1, y1 = [int(v) for v in region]
    for (ry, rh, sx) in rows:
        a, b = max(0, ry - box.y0), min(box.h, ry + rh - box.y0)
        c0, c1 = max(0, x0 - box.x0), min(box.w, x1 - box.x0)
        if b <= a or c1 <= c0:
            continue
        strip = img_c[a:b, c0:c1].copy()
        st = np.roll(strip, sx, axis=1)
        st[..., 0] = np.roll(strip[..., 0], sx + 3, axis=1)
        st[..., 2] = np.roll(strip[..., 2], sx - 3, axis=1)
        st = st * 0.65 + np.array(VIOLET, np.float32) * 0.35
        st[::2] *= 0.72
        out[a:b, c0:c1] = st
    return out


def trace_core(t, reduce, marks, frame_c, box, lit_src, pip_xy, card_box, seeds=(100, 300)):
    """frame_c: the composited frame crop (HUD already on); lit_src: full frame holding the lit pip at pip_xy - (28, 0)"""
    out = frame_c.copy()
    tx, ty = pip_xy
    sx = tx - TR_PITCH
    q = 13
    lit = lit_src[int(ty) - q:int(ty) + q, int(sx) - q:int(sx) + q].copy()
    if marks and not reduce and 16 <= t < 166:
        i = min(4, int((t - 16) // 30.0))
        rr = np.random.default_rng(seeds[0] + i)
        rows = [(int(rr.integers(card_box[1] + 6, card_box[3] - 20)), int(rr.integers(4, 8)), int(rr.choice([-6, 6]))) for _ in range(TR_ROWS)]
        out = glitch(out, box, rows, (card_box[0] - 8, card_box[1], card_box[2] + 8, card_box[3]))
    if t >= 166:
        stp = 3 if reduce else min(3, int((t - 166) // 33.4))
        scale = TR_POP[stp]
        if stp < 2 and marks:
            Lp = Layer(box)
            hq = 11 * scale
            Lp.d.rectangle([(tx - hq - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq - box.x0) * 3, (ty + hq - box.y0) * 3], fill=VIOLET + (255,), outline=INK + (255,), width=6)
            Lp.d.rectangle([(tx - hq - 4 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx - hq - 1 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(255, 40, 120, 200))
            Lp.d.rectangle([(tx + hq + 1 - box.x0) * 3, (ty - hq - box.y0) * 3, (tx + hq + 4 - box.x0) * 3, (ty + hq - box.y0) * 3], fill=(40, 200, 255, 200))
            out = over(out, Lp.done())
        else:
            a, b = int(ty) - q - box.y0, int(tx) - q - box.x0
            out[a:a + 2 * q, b:b + 2 * q] = lit
        if marks and not reduce and 166 <= t < 266:
            j = int((t - 166) // 33.4)
            rr = np.random.default_rng(seeds[1] + j)
            rows = [(int(rr.integers(int(ty) - 13, int(ty) + 10)), 4, int(rr.choice([-6, 6])))]
            out = glitch(out, box, rows, (tx - 120, ty - 18, tx + 90, ty + 18))
    return out


def trace_render(t, skin, reduce=False, marks=True):
    box = FX['fx_trace_add']['_box']
    full = comp(below(skin, 'p1'), above(skin, 'p1'))
    pip = (TR_X0['p1'] + 3 * TR_PITCH, TR_ROW['p1'])
    return trace_core(t, reduce, marks, box.crop(full), box, full, pip, TR_CARD)


def trace_post(skin):
    return trace_render(400, skin, True, False)


reg(dict(id='fx_trace_add', fam='S', tier='state', title='A loud card adds Trace', skins=['neutral'], box=(1240, 330, 1620, 1080), scale=0.8,
         src='f2: Trigger played (cost 1, loud 1): Trace 3 to 4 (f1 trace 3, f2 trace 4, cap 6)',
         still='One violet stepped glitch band (4-7 px) per 33 ms step shears the Trigger card (6 px offset, R/B split, scanlines) for five steps; then the fourth TRACE pip pops in three stepped scales (1.45, 1.2, 1.0) with a one-band glitch on the TRACE row and settles as the HUD\'s own lit pip.',
         keep='violet = Trace only; stepped bands, never smooth; the settled pip is the HUD\'s own lit pip; the one effect of the four families allowed over the HUD and the hand (REVIEW_RESPONSE 1.6).',
         timing=dict(phases=[('card glitch, 5 steps', 0, 166, 'step 33 ms'), ('pip pops, 3 steps; row glitch', 166, 266, 'step 33 ms'), ('settled', 266, 400, '-')], total=400),
         reduce_phases=[('pip lights in one step', 166, 166, 'step'), ('settled', 166, 400, '-')],
         keys=[(0, 'played'), (40, 'glitch'), (110, 'glitch'), (180, 'pip pops'), (215, 'pip steps'), (400, 'settled')],
         reduce_note='No glitch bands: the fourth pip simply lights at 166 ms (one step, no scale).',
         notes='Also played by Pull (+1) and Shove (+2, two pips one after the other, 120 ms apart).',
         render=trace_render, pre=lambda skin: trace_render(0, skin, True, False), post=trace_post))


# ============================================================================ T: commit (pencil marks burn into pink paint)
_commit = {}
COMMIT_HOT = (0.018, 0.6)      # review 2.10: the white-hot burn front, share of the route length and white mix (was 0.035, 0.75: gated loudness 1277, over every block)


def commit_data(key, a2, a3, box, seed):
    """a2 / a3: board crops of the preview (p2) and resolve (p3_pre) boards.  The pencil marks = yellow in a2 that change in a3;
    the burn order = geodesic distance along each mark from the route start."""
    if key in _commit:
        return _commit[key]
    h2, s2, v2 = hsv_np(a2)
    yel = (h2 > 40) & (h2 < 66) & (s2 > 0.55) & (v2 > 0.55)
    diff = np.abs(a2 - a3).max(2) > 22
    onb = (box.RHO > 205) & (box.RHO < 500)
    m = yel & onb & (np.abs(a2 - a3).max(2) > 40)
    m = ndi.binary_opening(m, iterations=1) | (m & ndi.binary_dilation(m, iterations=1))
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    sizes = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 40])
    marks = ndi.binary_dilation(keep, iterations=3) & diff
    sx, sy = seed[0] - box.x0, seed[1] - box.y0
    lab2, n2 = ndi.label(marks, structure=np.ones((3, 3)))
    dist = np.full(marks.shape, np.inf, np.float32)
    comps = []
    for ci in range(1, n2 + 1):
        cy, cx = np.nonzero(lab2 == ci)
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
    j = np.unravel_index(np.argmax(np.where(fin, dist, -1)), dist.shape)
    endp = (j[1] + box.x0, j[0] + box.y0)
    rest = (np.abs(a2 - a3).max(2) > 6) & ~marks
    _commit[key] = (marks, nd, endp, rest)
    return _commit[key]


def commit_core(t, reduce, marks_on, B2, B3, U2, U3, box, key, seed, split=False):
    """board: p2 -> p3_pre with the pencil marks burning front to back; HUD and hand (U2 -> U3) step from preview to resolve with the board.
    split=True returns (board crop, HUD-and-hand crop RGBA) for the resolve beat, which draws other effects between the two."""
    a2, a3 = box.crop(B2), box.crop(B3)
    marks, nd, endp, rest = commit_data(key, a2, a3, box, seed)
    if reduce:
        k = e_io3(seg(t, 0, 300))
        out = np.where(marks[..., None], mix(a2, a3, k), a2)
        kr = e_io3(seg(t, 300, 600))
        out = np.where(rest[..., None], mix(a2, a3, kr), out)
    else:
        front = 1.08 * e_io3(seg(t, 60, 400))
        burnt = marks & (nd <= front)
        out = np.where(burnt[..., None], a3, a2)
        if marks_on:
            hot = marks & (nd > front - COMMIT_HOT[0]) & (nd <= front) & (front < 1.06)
            out = np.where(hot[..., None], mix(a3, np.full_like(a3, 255.0), COMMIT_HOT[1]), out)
        kr = e_io3(seg(t, 400, 600))
        out = np.where(rest[..., None], mix(a2, a3, kr), out)
        if marks_on:
            L = Layer(box)
            pk = seg(t, 400, 520)
            if 0 < pk < 1:
                r = 6 + 16 * e_out3(pk)
                L.circle(endp, r, outline=INK, w=4.6, a=int(255 * (1 - pk)))
                L.circle(endp, r, outline=PINK, w=2.4, a=int(255 * (1 - pk)))
            out = over(out, L.done())
    u = mix(box.crop(U2), box.crop(U3), kr)
    return (out, u) if split else comp(out, u)


def commit_render(t, skin, reduce=False, marks=True):
    box = FX['fx_commit']['_box']
    return commit_core(t, reduce, marks, below(skin, 'p2'), below(skin, 'p3'), above(skin, 'p2'), above(skin, 'p3'), box, ('c', skin), FX['fx_commit']['seed'])


reg(dict(id='fx_commit', fam='T', tier='state', title='SEND IT burns pencil marks into paint', skins=['neutral', 'solace', 'meridian'], box=(0, 0, 1920, 1080), scale=0.32,
         seed=(372, 836),
         src='SEND IT on the best line (f2: Twist, Trigger, Brace): p2 preview marks (pencil yellow) to the p3 resolve marks (pink)',
         still='Every pencil-yellow plan mark on the board burns into the pink painted mark front to back along its own length (geodesic order from the route start); a thin white-hot edge (1.8 % of the route length, 60 % white) rides the burn front; a pink ping rings the route end; then the rest of the board, the HUD and the hand step from preview to resolve.',
         keep='yellow to PINK front to back; thin white-hot edge on the front (quieter than every block: review 2.10); ping at the route end; no yellow left on the board marks after the beat; the burn is a board mark (under the HUD and the hand).',
         timing=dict(phases=[('SEND IT press, hold', 0, 60, '-'), ('burn front runs the marks', 60, 400, 'easeInOutCubic'), ('ping at the route end', 400, 520, 'easeOutCubic'),
                             ('board, HUD and hand step preview to resolve', 400, 600, 'easeInOutCubic')], total=600),
         reduce_phases=[('marks cross-fade yellow to pink', 0, 300, 'easeInOutCubic'), ('board, HUD and hand step to resolve', 300, 600, 'easeInOutCubic')],
         keys=[(0, 'pencil plan'), (120, 'burn starts'), (230, 'front runs'), (360, 'front arrives'), (450, 'ping'), (600, 'committed paint')],
         reduce_note='No burn front and no ping: the marks cross-fade yellow to pink over 300 ms, then the board, the HUD and the hand step to resolve over 300 ms.',
         notes='Both ends are the generator\'s own plates (p2 and p3 of each skin); only the path between them is the effect.',
         render=commit_render, pre=lambda skin: commit_render(0, skin, True, False), post=lambda skin: commit_render(600, skin, True, False)))


for _s in FX.values():
    _s['_box'] = Box(*_s['box'])
    assert _s['timing']['total'] <= CAP_MS, _s['id']
    assert max(p[2] for p in _s['timing']['phases']) <= _s['timing']['total'], _s['id']
    assert max(p[2] for p in _s['reduce_phases']) <= CAP_MS, _s['id']
