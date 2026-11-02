"""Scene harness for the card cluster: the E10 plate on room_bio_bare (board + HUD cached per beat), the hand drawn by the original
generator (current) or by kcard (options), stickers on top.  final(beat, V) -> RGBA 1920x1080."""
import sys, os, math, json, copy
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import build10 as B10
from build10 import *
import cv_chrome as CH
import cv_board as CB9
import kcard2 as KC
from kcard2 import K, P

ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png'
CACHE = ROOT + 'cache/'
os.makedirs(CACHE, exist_ok=True)
BEATS = {'p1': 'f1', 'nowords': 'f1', 'p2': 'f2', 'p3': 'f2'}
_plate = {}


def board_cached(beat):
    keep = beat == 'p2'
    nm = 'bd_%s_%s_%s.npy' % ('f2' if beat in ('p2', 'p3') else 'f1', int(keep), int(beat == 'nowords'))
    p = CACHE + nm
    if os.path.exists(p):
        return Image.fromarray(np.load(p), 'RGBA')
    NOW['words'] = beat != 'nowords'
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    b = render_board(board_frame(J[BEATS[beat]], keep_all=keep), CONS)
    np.save(p, np.asarray(b))
    return b


def plate_base(beat):
    """room + board + board overlays + HUD, no hand, no stickers"""
    if beat in _plate:
        return _plate[beat]
    fp = CACHE + 'plate_%s.png' % beat
    if os.path.exists(fp):
        _plate[beat] = Image.open(fp).convert('RGBA')
        return _plate[beat]
    reg_reset()
    NOW['words'] = beat != 'nowords'
    CB9.HUB['name'] = 'Breaker' if beat != 'nowords' else ''
    f = copy.deepcopy(J[BEATS[beat]])
    bg = Image.open(ROOM).convert('RGBA')
    board = board_cached(beat)
    gb = grade_units(board, f, keep_all=(beat == 'p2'), dim_ids=None)
    sh = np.asarray(gb.split()[3], np.float32)
    sh = np.asarray(Image.fromarray(sh.astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    sh = np.roll(np.roll(sh, 10, 0), 6, 1)
    a = np.asarray(bg, np.float32)
    a[..., :3] *= (1 - 0.38 * sh[..., None])
    bg = Image.fromarray(a.astype(np.uint8), 'RGBA')
    bg.alpha_composite(gb)
    L = L2()
    O.hp_ring(L, f['hp'], f['pv']['hp_after'], f['maxhp'])
    bezel9(L, f['schedule'])
    O.sector_digits(L)
    occ = {(u['dep'], q) for u in f['units'] for q in sectors(u)}
    for d in range(3):
        for q in range(6):
            if (d, q) not in occ:
                O.cell_border(L, d, q, alpha=70)
    wave_arcs10(L, arcs_data(f))
    ward_arc(L, f)
    tower_slice_bars(L, f)
    if beat in ('p1', 'nowords'):
        threat_trim(L, f)
    draw_units(L, f)
    adjuster_body(L, f['adj'])
    if beat in ('p1', 'nowords'):
        gun_tracers10(L, f)
    landing_arcs(L, f)
    ring_tags(L, f)
    nudge_ghost(L)
    if beat in ('p2', 'p3'):
        twist_badge(L, f)
        refund_marks(L, f)
    if beat == 'p2':
        for tr in J['trigs']:
            trigger_paths(L, f, dict(tr, entries=[e for e in tr['entries'] if e[0] != 'refund']))
    if beat == 'p3':
        for e_ in f['log']:
            if e_[0] == 'fire' and e_[3] is not None:
                s_, dep_ = e_[1], e_[5]
                L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))
    bg.alpha_composite(L.done())
    L = L2()
    header(L, f)
    y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None), twist_pay=(J['twist_payoff'] if beat in ('p2', 'p3') else None))
    if beat == 'p2':
        y = option_chip(L, y, 'TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], refund=J['f2t']['refunds'] > 0)
        y = option_chip(L, y, 'BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'])
        y = option_chip(L, y, 'BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], sel=True, refund=f['refunds'] > 0)
    elif beat == 'p3':
        y = chain_strip(L, f, y)
    y = stars_row(L, f, y + 2)
    y = ram_trace(L, f, y)
    bg.alpha_composite(L.done())
    bg.save(fp)
    _plate[beat] = bg
    return bg


def hand_lists(beat):
    f = J[BEATS[beat]]
    f1 = J['f1']
    played = [a[0] for a in f['played']]
    hand = list(f['hand'])
    if beat == 'p3':
        hand = list(f1['hand'])
        for c_ in played:
            hand.remove(c_)
    hover_i = hand.index('Trigger') if beat == 'p2' else None
    return hand, (played if beat == 'p3' else []), hover_i


# ------------------------------------------------------------------ fans (hand_fan)
FANS = {
    # P: shingle arc, 5 deg/card about a far pivot, ends drop 15 px, step 144 so the hand ends 20 px left of SEND IT
    'P': dict(W=168, H=232, step=148, left=1022, dang=5.0, arc=905.0, cy0=934, hov_cy=880, hov_s=1.12),
    # V: calmer 4.5 deg, step 148, one notch lower
    'V': dict(W=172, H=232, step=152, left=1008, dang=4.5, arc=1000.0, cy0=940, hov_cy=880, hov_s=1.12),
}


def fan_slots(V, n):
    F = FANS[V['fan']]
    out = []
    for i in range(n):
        a = (i - (n - 1) / 2) * -F['dang']
        th = math.radians(a)
        out.append(dict(cx=F['left'] + F['W'] / 2 + i * F['step'], cy=F['cy0'] + F['arc'] * th * th, ang=a, W=F['W'], H=F['H']))
    return out


_cache = {}
HOVINFO = {}
HOV_PUSH = 28      # fix 10: cards right of the lifted one move out 28 px AND the lift is capped at x1.12 (was 1.22): 44 px would put the Twist card under the UNDO tab


def card_cached(name, V, state, nw, W, H):
    key = (name, tuple(sorted(V.items())), state, nw, W, H)
    if key not in _cache:
        _cache[key] = KC.card_hi(name, V, state, nw, W, H)[0]
    return _cache[key]


def liner_cached(name, V, W, H):
    key = ('L', name, V['liner'], W, H)
    if key not in _cache:
        _cache[key] = KC.liner_hi(name, V, W, H)
    return _cache[key]


def place(base, hi, cx, cy, ang, scale=1.0, shadow=None):
    im = hi
    if ang:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    w, h = im.width / K * scale, im.height / K * scale
    im = im.resize((max(1, int(round(w))), max(1, int(round(h)))), Image.LANCZOS)
    xy = (cx - im.width / 2, cy - im.height / 2)
    if shadow:
        KC_k, blur, off = shadow
        shadow_paste(base, im, xy, KC_k, blur, off)
    else:
        base.alpha_composite(im, (int(round(xy[0])), int(round(xy[1]))))
    return im


def hand_new(base, beat, V):
    nw = beat == 'nowords'
    hand, played, hov = hand_lists(beat)
    slots_n = len(hand) + len(played)
    slots = fan_slots(V, slots_n)
    if hov is not None:      # fix 10: while a card is lifted, every card to its right moves outward (the lifted card is 1.22x wide: it covered the neighbour's title)
        for k_ in range(hov + 1, slots_n):
            slots[k_]['cx'] += HOV_PUSH
    sh = KC.SHADOW
    F = FANS[V['fan']]
    for i, nm in enumerate(hand):
        s = slots[i]
        if i == hov:
            continue
        place(base, card_cached(nm, V, 'rest', nw, s['W'], s['H']), s['cx'], s['cy'], s['ang'], 1.0, sh)
    for j, nm in enumerate(played):
        s = slots[len(hand) + j]
        place(base, liner_cached(nm, V, s['W'], s['H']), s['cx'], s['cy'], s['ang'], 1.0, None)
    HOVINFO.clear()
    if hov is not None:
        s = slots[hov]
        W, H = s['W'], s['H']
        hs = F['hov_s']
        hcy = F['hov_cy']
        place(base, card_cached(hand[hov], V, 'hover', nw, W, H), s['cx'], hcy, 0, hs, KC.SHADOW_GROWN)
        HOVINFO.update(cx=s['cx'], cy=hcy, s=hs, W=W, H=H)
    return slots


def hand_cur(base, beat):
    hand, played, hov = hand_lists(beat)
    NOW['words'] = beat != 'nowords'
    CH.hand(base, hand, x0=1000, hover=hov, played=played, cy0=948)


def final(beat, V=None, orig=False):
    base = plate_base(beat).copy()
    NOW['words'] = beat != 'nowords'
    if orig:
        hand_cur(base, beat)
        slots = fan_slots(dict(BASE_V_, fan='P'), 4)
        HOVINFO.clear()
        if beat == 'p2':
            HOVINFO.update(cx=slots[2]['cx'], cy=890, s=1.22, W=200 / 1.0, H=260)
    else:
        slots = hand_new(base, beat, V)
    L3 = L2()
    stickers(base, L3)
    base.alpha_composite(L3.done())
    return base, slots


BASE_V_ = dict(KC.BASE_V)


def crop(im, box, k=2):
    c = im.crop(tuple(int(v) for v in box)).convert('RGB')
    return c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
