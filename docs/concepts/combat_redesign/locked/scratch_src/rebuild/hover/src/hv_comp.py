"""hv_comp: the hover plate assembly on the rebuilt board: board render (cached on disk) with its masks, the hand layout search (2.6),
the UI layers, the compose, and the FOCUS layer.  Imports hv_core (which imports corp/src read-only)."""
import sys, os, math, json, copy, hashlib
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy import ndimage as ndi
import hv_core as V
from hv_core import Z, R, A, FH, HL, C, W, H, L2, ppx, NOW, CB, RA, AU, hud2, MASKS, LOGD, HS, RBC, RC, obj2, CORP

# ================================================================================================ FOCUS drawn on its own layer (mask for the checks)
FOCUS_MASK = V.FOCUS_MASK


def focus_layer(fn, L, *a, **k):
    T_ = L2()
    r = fn(T_, *a, **k)
    L.im.alpha_composite(T_.im)
    m = np.asarray(V.done_box(T_).split()[3]) >= 96
    FOCUS_MASK['m'] = FOCUS_MASK.get('m', np.zeros((H, W), bool)) | m
    FOCUS_CALLS.append(dict(fn=getattr(fn, '__name__', '?'), thick=bool(a[-1]) if a and isinstance(a[-1], bool) else bool(k.get('thick')), m=m))
    return r


FOCUS_CALLS = []


def focus_slice(L, s, thick=False):
    return focus_layer(Z.focus_slice, L, s, thick)


def focus_cell(L, u, thick=False):
    return focus_layer(Z.focus_cell, L, u, thick)


def focus_adj(L, f, thick=False):
    return focus_layer(Z.focus_adj, L, f, thick)


def focus_col(L, s, thick=False):
    return focus_layer(Z.focus_col, L, s, thick)


def focus_tag(L, d, f, thick=False):
    return focus_layer(Z.focus_tag, L, d, f, thick)


# ================================================================================================ capture for the checks (rb_capture on its own mask dict)
RBM = {}
_put0 = FH.put
RBC.install(R, A, FH, RBM, 'p1')
FH.put = _put0                       # the hover hand is placed by hand_draw (its own record), not through rb_capture's queue
YOU_MASK = V.YOU_MASK
SNAP = {}


def reset_all():
    Z.reset_checks()
    RBM.clear()
    V.PEN_MASKS.clear()
    V.PEN_COV.clear()
    FOCUS_MASK.clear()
    del FOCUS_CALLS[:]
    del TINTS[:]
    V.FIT_LOG.clear()
    YOU_MASK.clear()
    SNAP.clear()
    del RBC.TEXT[:]
    del RBC.CARDS[:]
    del RBC.UNCAPTURED[:]
    Z.HOV.clear()
    Z.HOV.update({'i': None, 'dx': 0.0})


CACHE = V.HERE + 'work/'
os.makedirs(CACHE, exist_ok=True)


def _knobs():
    return dict(T=V.HERO_ROOM_T, B=V.HERO_ROOM_B, DX=V.HERO_DX, GAP=V.HERO_GAP, opt=json.dumps(V.OPT['rows'], sort_keys=True, default=str),
                room=V.HUD_ROOM['on'], pitch=V.OPT_PITCH)


def _jsonable(v):
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, np.generic):
        return v.item()
    return str(v)


def board(beat, f_board, f_hud, tag, words, arcs_skip=(), hide_units=(), hover_unit=None, cache_key=None, assert_beat=None):
    """the rebuilt board + tower + HUD + YOU strip (no hand, no stickers), cached on disk by (frame, hud frame, skin, words, HUD knobs).
    The draw asserts run on f_board; on a hit the board masks (hz_core MASKS, rb_capture RBM), registries, text log and YOU strip mask are
    restored."""
    key = hashlib.md5(json.dumps([beat, f_board, f_hud, CORP, words, list(arcs_skip), list(hide_units), hover_unit, _knobs(), cache_key, assert_beat],
                                 sort_keys=True, default=str).encode()).hexdigest()[:16]
    fp = CACHE + 'board_%s' % key
    if all(os.path.exists(fp + e) for e in ('.png', '.npz', '.json')) and not os.environ.get('HV_NOCACHE'):
        bg = Image.open(fp + '.png').convert('RGBA')
        z = np.load(fp + '.npz')
        for k_ in z.files:
            cls, _, name = k_.partition('__')
            m = np.unpackbits(z[k_])[:H * W].reshape(H, W).astype(bool)
            {'Z': MASKS, 'R': RBM, 'Y': YOU_MASK}[cls][name] = m
        js = json.load(open(fp + '.json'))
        hud2.R.clear()
        hud2.R.update({k_: (tuple(v) if isinstance(v, list) and k_ not in ('_opt_rows',) else v) for k_, v in js['hud2'].items()})
        obj2.R.clear()
        obj2.R.update({k_: (tuple(v) if isinstance(v, list) else v) for k_, v in js['obj2'].items()})
        A.INFO.update(js['info'])
        LOGD[:] = js['logd']
        RBC.TEXT[:] = js['text']
        RBC.UNCAPTURED[:] = js['unc']
        SNAP.update(js['snap'])
        Z.TEXTLOG[:] = js['textlog']
        SNAP['cache'] = 'hit ' + key
        return bg
    NOW['words'] = words
    you = lambda bg_, f: FH.place_ui(bg_, 'you', not words, f_hud)
    img = R._render(beat, frame=f_board, hud_frame=f_hud, tag=tag, with_ui=False, arcs_skip=arcs_skip, hide_units=hide_units, extra=you,
                    hover_unit=hover_unit)
    bg = img.convert('RGBA')
    im_, (x0, y0) = FH.ui_img('you', not words, f_hud)
    ym = np.zeros((H, W), bool)
    a_ = np.asarray(im_.split()[3]) >= 40
    ym[y0:y0 + a_.shape[0], x0:x0 + a_.shape[1]] = a_[:H - y0, :W - x0]
    YOU_MASK['you'] = ym
    Z.run_board_asserts(assert_beat or ('p1' if beat in ('p1', 'nowords') else beat), f_board, tag)
    SNAP.update(dash=len(R.DASH_LOG), dot=len(R.DOT_LOG), hud_bottom=A.INFO.get('hud_bottom'), hover_tag_box=A.INFO.get('hover_tag_box'), cache='miss ' + key)
    bg.save(fp + '.png')
    arrs = {('Z__' + k_): np.packbits(v) for k_, v in MASKS.items()}
    arrs.update({('R__' + k_): np.packbits(v) for k_, v in RBM.items()})
    arrs.update({('Y__' + k_): np.packbits(v) for k_, v in YOU_MASK.items()})
    np.savez_compressed(fp + '.npz', **arrs)
    js = dict(hud2={k_: _jsonable(v) for k_, v in hud2.R.items() if not callable(v)}, obj2=_jsonable(dict(obj2.R)),
              info=_jsonable({k_: A.INFO.get(k_) for k_ in ('hud_bottom', 'hover_tag_box')}), logd=_jsonable(list(LOGD)), text=_jsonable(list(RBC.TEXT)),
              unc=_jsonable(list(RBC.UNCAPTURED)), snap=_jsonable(dict(SNAP)), textlog=_jsonable(list(Z.TEXTLOG)))
    json.dump(js, open(fp + '.json', 'w'))
    return bg


# ================================================================================================ the hand (2.6), searched per plate
HAND = dict(lift_s=(1.10, 1.07, 1.04), lift_cy=tuple(range(788, 895, 6)), lift_dx=tuple(range(-64, 161, 4)), fan_dx=(0, -4, 4, -8, 8, -12, -16, -24),
            pre_dx=(0, -8, -16, -24, -32, -40, -56, -72), push=(16, 8, 24, 0, 32, 40, 48, 56, 64, 72, 80, 96, 112, 128, 144),
            rest=(16, 8, 0, 24, 32, -8, -16, -24, -32))
HAND_BOTTOM = 1067       # stage 2 (review 2.7): lowest hand pixel, 12 px above y 1080
HAND_BTN_GAP = 2         # px kept between the hand and SEND IT / UNDO
LIFT_REF_CY = 832        # cost reference: the board's p2 lift height (rb_patch LIFT_CY2)
N_REST_KEEP = 120        # cheapest feasible resting layouts tried for the lift
_mcache = {}
BTN = {}
HV_HAND = {}
HAND_MASKS = {}
HL_STATS = {}


def _card_mask(name, nw, mode, scale, ang):
    key = (name, nw, mode, round(scale, 3), round(ang, 3))
    if key in _mcache:
        return _mcache[key]
    im = FH.card_hi(name, nw, mode)
    k = scale / 2.0
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    a = im.split()[3].resize((w, h), Image.LANCZOS)
    if ang:
        a = a.rotate(ang, resample=Image.BICUBIC, expand=True)
    m = np.asarray(a) >= 128
    _mcache[key] = (m, im.width, im.height)
    return _mcache[key]


def _place(m, cx, cy):
    h, w = m.shape
    return int(round(cx - w / 2)), int(round(cy - h / 2))


def _hit(full, m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya:
        return 0
    return int((full[ya:yb, xa:xb] & m[ya - y0:yb - y0, xa - x0:xb - x0]).sum())


def _paste(full, m, x0, y0):
    h, w = m.shape
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb > xa and yb > ya:
        full[ya:yb, xa:xb] |= m[ya - y0:yb - y0, xa - x0:xb - x0]


_rcache = {}


def _region_mask(card, which):
    key = (card['name'], round(card['cx'], 2), round(card['cy'], 2), round(card['ang'], 3), round(card['scale'], 3), which)
    if key not in _rcache:
        cost, rules = RC.card_regions(card)
        _rcache[key] = RC.poly_mask([cost if which == 'cost' else rules])
    return _rcache[key]


def button_masks(words):
    """SEND IT and UNDO as drawn on the plate (FH.ui_img('send') and the stack layer's UNDO box, as rb_capture records them)"""
    BTN.clear()
    im, (x0, y0) = FH.ui_img('send', not words)
    m = np.zeros((H, W), bool)
    a = np.asarray(im.split()[3]) >= 128
    m[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a[:H - y0, :W - x0]
    BTN['send'] = m
    lay, info = R.AS.stack_layer(words, {})
    a = np.asarray(lay.split()[3]) >= 128
    box = np.zeros_like(a)
    box[850:900, 1655:1896] = True
    BTN['undo'] = a & box
    return lay


def _integral(mask):
    """the integral image of mask over its own bbox window (most masks here are a few small polygons): (S, x0, y0, x1, y1)"""
    rows = np.nonzero(mask.any(1))[0]
    if not len(rows):
        return (None, 0, 0, 0, 0)
    cols = np.nonzero(mask.any(0))[0]
    y0, y1, x0, x1 = int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1
    S = np.zeros((y1 - y0 + 1, x1 - x0 + 1), np.int32)
    S[1:, 1:] = mask[y0:y1, x0:x1].astype(np.int32).cumsum(0).cumsum(1)
    return (S, x0, y0, x1, y1)


def _box_sum(Si, x0, y0, x1, y1):
    S, wx0, wy0, wx1, wy1 = Si
    if S is None:
        return 0
    x0, y0, x1, y1 = max(wx0, x0), max(wy0, y0), min(wx1, x1), min(wy1, y1)
    if x1 <= x0 or y1 <= y0:
        return 0
    x0, x1, y0, y1 = x0 - wx0, x1 - wx0, y0 - wy0, y1 - wy0
    return int(S[y1, x1] - S[y0, x1] - S[y1, x0] + S[y0, x0])


_cross = {}


def _mask_cross(m):
    """two rectangles fully inside a card mask (the card's rounded corners and any transparent margin excluded): a hit inside them is a hit.
    (rows over the middle row's span, columns over the middle column's span)"""
    k_ = id(m)
    if k_ not in _cross:
        h, w = m.shape
        boxes = []
        mr = np.nonzero(m[h // 2])[0]
        mc = np.nonzero(m[:, w // 2])[0]
        if len(mr) and len(mc):
            c0, c1 = int(mr[0]), int(mr[-1]) + 1
            r0, r1 = int(mc[0]), int(mc[-1]) + 1
            rows = np.nonzero(m[:, c0:c1].all(1))[0]
            cols = np.nonzero(m[r0:r1, :].all(0))[0]
            if len(rows):
                boxes.append((c0, int(rows[0]), c1, int(rows[-1]) + 1))
            if len(cols):
                boxes.append((int(cols[0]), r0, int(cols[-1]) + 1, r1))
        _cross[k_] = boxes
    return _cross[k_]


def _fast_hit(S, full, m, x0, y0):
    """_hit via the windowed integral image S of full: 0 when the bbox is clear, 1 when a fully covered box of the card holds a pixel, else exact"""
    h, w = m.shape
    if _box_sum(S, x0, y0, x0 + w, y0 + h) == 0:
        return 0
    for bx0, by0, bx1, by1 in _mask_cross(m):
        if _box_sum(S, x0 + bx0, y0 + by0, x0 + bx1, y0 + by1) > 0:
            return 1
    return _hit(full, m, x0, y0)


def _shifts(n, hov, fan, pre, push, rest):
    """per-card x shift: the whole fan by fan; the cards before the lifted one by pre; the card after it by push and the last card by rest,
    the cards between those two interpolated (the fan after the lifted card compresses rather than running into UNDO)"""
    out = []
    for i in range(n):
        d = fan
        if hov is not None:
            if i < hov:
                d += pre
            elif i > hov:
                j0, j1 = hov + 1, n - 1
                if j1 == j0:
                    d += push
                else:
                    t = (i - j0) / float(j1 - j0)
                    d += push + (rest - push) * t
        out.append(d)
    return out


REST_FACE_SLACK = 0      # px a resting card's face may be covered by the resting cards after it beyond the board's own resting fan


def _face_cover(cards_):
    """per resting card (hand order): px of its face under the resting cards after it (union), from the placed masks"""
    out = []
    for a_i, ca in enumerate(cards_):
        ma, ax0, ay0 = ca['_m']
        h, w = ma.shape
        acc = np.zeros((h, w), bool)
        for cb in cards_[a_i + 1:]:
            mb, bx0, by0 = cb['_m']
            hb, wb = mb.shape
            xa, ya, xb, yb = max(ax0, bx0), max(ay0, by0), min(ax0 + w, bx0 + wb), min(ay0 + h, by0 + hb)
            if xb > xa and yb > ya:
                acc[ya - ay0:yb - ay0, xa - ax0:xb - ax0] |= mb[ya - by0:yb - by0, xa - bx0:xb - bx0]
        out.append((ca['name'], int((acc & ma).sum())))
    return out


def board_face_cover(hand, nw):
    """the board's own resting fan of this hand (no lift, no shift): px of each card's face under the cards after it"""
    cards_ = []
    for s, nm in zip(FH.slots(len(hand)), hand):
        m, w2, h2 = _card_mask(nm, nw, 'normal', FH.CARD_SCALE, s['ang'])
        x0, y0 = _place(m, s['cx'], s['cy'])
        cards_.append(dict(name=nm, _m=(m, x0, y0)))
    return dict(_face_cover(cards_))


def hand_layout(hand, lift, nw, forbid_extra=None, keep_faces=True):
    """2.6: the hand layout of one hover plate, searched.  Hard rules (rb_checks check e and the board's hand rules): every card outside r455; the
    lifted card outside r459 and LIFT_ARC_GAP px off the landing marks; no hand pixel within HAND_BTN_GAP px of SEND IT or UNDO; no hand pixel
    below y HAND_BOTTOM; the lifted card on no resting card's cost hex or rules line; no resting card on another resting card's cost hex; with
    keep_faces, no resting card's face more covered by the resting cards after it than on the board's own resting fan (so a fan that closes up
    never hides a name, a rules word or a tab the board shows).  Moves searched: the whole fan (fan_dx), the cards before the lifted one (pre_dx), the card after it (push) and the last card (rest, the
    ones between interpolated), and the lifted card's dx, centre y and scale.  The least total move wins."""
    yy_, xx_ = np.mgrid[0:H, 0:W]
    rho = np.hypot(xx_ - C[0], yy_ - C[1])
    r455 = rho < FH.HAND_MIN_R
    r459 = rho < FH.HAND_MIN_R + Z.LIFT_CLEAR
    below = yy_ > HAND_BOTTOM
    btn = np.zeros((H, W), bool)
    for k_ in ('send', 'undo'):
        if k_ in BTN:
            btn |= BTN[k_]
    btn = ndi.binary_dilation(btn, iterations=HAND_BTN_GAP)
    arcs = MASKS.get('arcs')
    arcs = ndi.binary_dilation(arcs, iterations=Z.LIFT_ARC_GAP) if arcs is not None else np.zeros((H, W), bool)
    bad_rest = r455 | below | btn
    bad_lift = r459 | below | btn | arcs
    if forbid_extra is not None:
        bad_rest = bad_rest | forbid_extra
        bad_lift = bad_lift | forbid_extra
    n = len(hand)
    hov = hand.index(lift) if lift is not None else None
    base = FH.slots(n)
    after = hov is not None and hov < n - 1
    rest_opts = []
    for fan in HAND['fan_dx']:
        for pre in (HAND['pre_dx'] if hov not in (None, 0) else (0,)):
            for push in (HAND['push'] if after else (16,)):
                for rest in (HAND['rest'] + tuple(p for p in HAND['push'] if p > 32) if hov is not None and hov < n - 2 else (push,)):
                    if hov is not None and hov < n - 2 and rest > push:
                        continue
                    cost = abs(fan) * 1.0 + abs(pre) * 0.8 + (abs(push - 16) * 0.6 if after else 0) + (abs(rest - 16) * 0.6 if hov is not None and hov < n - 2 else 0)
                    rest_opts.append((cost, fan, pre, push, rest))
    rest_opts = sorted(set(rest_opts))
    S_rest = _integral(bad_rest)
    face_board = board_face_cover(hand, nw)

    def rest_feasible(opts):
        """the resting layouts that pass, in the order given (lazily)"""
        for cost, fan, pre, push, rest in opts:
            sh = _shifts(n, hov, fan, pre, push, rest)
            sl = [dict(cx=s['cx'] + sh[i], cy=s['cy'], ang=s['ang']) for i, s in enumerate(base)]
            cards, ok = [], True
            for i, nm in enumerate(hand):
                if i == hov:
                    continue
                s = sl[i]
                m, w2, h2 = _card_mask(nm, nw, 'normal', FH.CARD_SCALE, s['ang'])
                x0, y0 = _place(m, s['cx'], s['cy'])
                if _fast_hit(S_rest, bad_rest, m, x0, y0):
                    ok = False
                    break
                cards.append(dict(name=nm, role='rest', cx=float(s['cx']), cy=float(s['cy']), ang=float(s['ang']), scale=float(FH.CARD_SCALE), w2=w2, h2=h2,
                                  _m=(m, x0, y0)))
            if not ok:
                continue
            for a_i in range(len(cards)):
                cm = _region_mask(cards[a_i], 'cost')
                for b_i in range(a_i + 1, len(cards)):
                    m, x0, y0 = cards[b_i]['_m']
                    if _hit(cm, m, x0, y0):
                        ok = False
                        break
                if not ok:
                    break
            if ok and keep_faces:
                for nm_, px_ in _face_cover(cards):
                    if px_ > face_board[nm_] + REST_FACE_SLACK:
                        ok = False
                        break
            if ok:
                yield (cost, fan, pre, push, rest, sl, cards)
    HL_STATS.clear()
    HL_STATS.update(rest_opts=len(rest_opts))
    if lift is None:
        for fr in rest_feasible(rest_opts):
            cost, fan, pre, push, rest, sl, cards = fr
            return dict(cards=cards, lift=None, fan=fan, pre=pre, push=push, rest=rest, cost=cost, tried=0)
        return None
    # the lifted card's free positions against the board (independent of the resting layout), once per slot centre
    free = {}
    S_lift = _integral(bad_lift)

    def lift_free(cx_slot):
        k_ = round(cx_slot, 1)
        if k_ not in free:
            lst = []
            for ls in HAND['lift_s']:
                m, w2, h2 = _card_mask(lift, nw, 'hover', ls * FH.CARD_SCALE, 0.0)
                for cy in HAND['lift_cy']:
                    for dx in HAND['lift_dx']:
                        x0, y0 = _place(m, cx_slot + dx, cy)
                        if _fast_hit(S_lift, bad_lift, m, x0, y0):
                            continue
                        c_ = abs(dx) * 0.9 + abs(cy - LIFT_REF_CY) * 0.15 + 400 * (FH.LIFT_S - ls)
                        lst.append((c_, ls, cy, dx, m, w2, h2, x0, y0))
            lst.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
            free[k_] = lst
        return free[k_]
    ST = dict(best=None, tried=0, n_fr=0)

    def try_rest(fr):
        cost0, fan, pre, push, rest, sl, cards = fr
        best = ST['best']
        ST['n_fr'] += 1
        rm = np.zeros((H, W), bool)
        for c in cards:
            rm |= _region_mask(c, 'cost') | _region_mask(c, 'rules')
        S_rm = _integral(rm)
        s = sl[hov]
        for c_l, ls, cy, dx, m, w2, h2, x0, y0 in lift_free(s['cx']):
            c_ = cost0 + c_l
            if best is not None and c_ >= best['cost']:
                return
            ST['tried'] += 1
            if _fast_hit(S_rm, rm, m, x0, y0):
                continue
            ST['best'] = dict(cards=cards, lift=dict(name=lift, role='lift', cx=float(s['cx'] + dx), cy=float(cy), ang=0.0, scale=float(ls * FH.CARD_SCALE),
                                                     w2=w2, h2=h2, _m=(m, x0, y0), lift_s=ls, dx=dx), fan=fan, pre=pre, push=push, rest=rest, cost=c_)
            return
    # warm start: the layouts that open the widest gap after the lifted card (and before it), so the full pass below can prune by cost
    warm = sorted(rest_opts, key=lambda o: (-(o[3] - o[2]), o[0]))
    k_w = 0
    for fr in rest_feasible(warm):
        try_rest(fr)
        k_w += 1
        if ST['best'] is not None or k_w >= 40:
            break
    for fr in rest_feasible(rest_opts):
        if ST['best'] is not None and fr[0] >= ST['best']['cost']:
            break
        try_rest(fr)
    best, tried, n_fr = ST['best'], ST['tried'], ST['n_fr']
    HL_STATS.update(tried=tried, feasible_rest_tried=n_fr, lift_free={k_: len(v) for k_, v in free.items()})
    if best is not None:
        best['tried'] = tried
        best['n_rest_feasible'] = n_fr
    return best


def hand_draw(base, layout, nw, dim_others):
    """the searched layout: resting cards at REST_V x dim_others (the cards not in play), the lifted card at its lift value on its pink print"""
    rec = []
    for c in layout['cards']:
        ci = FH.card_hi(c['name'], nw)
        a_ = np.asarray(ci).astype(np.float32)
        a_[..., :3] *= FH.REST_V * (dim_others or 1.0)
        _put0(base, Image.fromarray(a_.astype(np.uint8), 'RGBA'), c['cx'], c['cy'], c['ang'], FH.CARD_SCALE)
        rec.append(c)
    L_ = layout.get('lift')
    if L_ is not None:
        im = FH.card_hi(L_['name'], nw, 'hover')
        _put0(base, im, L_['cx'], L_['cy'], 0, L_['scale'], shadow=True, off=(6, 12), blur=10)
        rec.append(L_)
    return rec


def ui_layers(words, hand, lift, forbid_extra=None):
    """the hand (2.6 layout, searched) and the player UI (nameplate, SEND IT, UNDO at STICK_K)"""
    stack = button_masks(words)
    lay = hand_layout(list(hand), lift, not words, forbid_extra)
    faces_kept = lay is not None
    if lay is None:
        # no layout keeps every resting face as the board shows it (the slot-0 lift in a 4-card fan): the least-move layout that keeps the
        # hard rules, with the hidden face area reported (check e fails on it)
        lay = hand_layout(list(hand), lift, not words, forbid_extra, keep_faces=False)
    HV_HAND.clear()
    HV_HAND['ok'] = lay is not None
    HV_HAND['faces_kept'] = faces_kept
    HV_HAND['rest_face_board'] = board_face_cover(list(hand), not words)
    if lay is None:
        lay = dict(cards=[], lift=None)
    HV_HAND['rest_face_plate'] = dict(_face_cover(lay['cards']))
    hand_lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rec = hand_draw(hand_lay, lay, not words, Z.HAND_K / FH.REST_V)
    HV_HAND.update(layout={k_: v for k_, v in lay.items() if k_ not in ('cards', 'lift')},
                   cards=[{k_: (v if k_ != '_m' else None) for k_, v in c.items() if k_ != '_m'} for c in rec])
    HAND_MASKS.clear()
    for i, c in enumerate(rec):
        m, x0, y0 = c['_m']
        full = np.zeros((H, W), bool)
        _paste(full, m, x0, y0)
        HAND_MASKS['card_%d' % i] = full
        HAND_MASKS['hand_' + c['role']] = HAND_MASKS.get('hand_' + c['role'], np.zeros((H, W), bool)) | full
    st = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    m = Image.new('L', stack.size, 0)
    dr = ImageDraw.Draw(m)
    dr.rectangle([1655, 850, 1895, 899], fill=255)
    dr.rectangle([1660, 1028, 1900, 1060], fill=255)
    stack.putalpha(ImageChops.multiply(stack.split()[3], m))
    FH.place_ui(st, 'name', not words)
    FH.place_ui(st, 'send', not words)
    st.alpha_composite(stack)
    a = np.asarray(st).astype(np.float32)
    a[..., :3] *= Z.STICK_K
    st = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return hand_lay, st


# ================================================================================================ value-locked hue tint
TINTS = []
TINT_SS = 4               # supersampling of the tint polygon coverage


def value_tint(poly, col, a):
    """a hover tint over poly that never changes the glass value: each pixel is mixed toward col by a (0-1, sRGB) and then scaled back to its
    own linear luminance.  A flat alpha tint lifted the Firewall column's empty cell from L* 17.0 to 20.9, above every other empty cell on
    its ring, so it became the ring's a-check reference and the lit Packets on that ring fell under 3:1.  Applied in compose, on the dimmed
    board, under every hover mark and under the board marks put back on top."""
    TINTS.append((list(poly), tuple(int(v) for v in col[:3]), float(a)))


def _lin(c):
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def _gam(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c > 0.0031308, 1.055 * np.power(c, 1 / 2.4) - 0.055, c * 12.92)


def _apply_tints(img):
    if not TINTS:
        return img
    a = np.asarray(img.convert('RGB')).astype(np.float64) / 255.0
    wl = np.array([0.2126, 0.7152, 0.0722])
    for poly, col, al in TINTS:
        m = Image.new('L', (W * TINT_SS, H * TINT_SS), 0)
        ImageDraw.Draw(m).polygon([(x * TINT_SS, y * TINT_SS) for x, y in poly], fill=255)
        cov = np.asarray(m.resize((W, H), Image.BOX)).astype(np.float64) / 255.0
        sel = cov > 0
        if not sel.any():
            continue
        px = a[sel]
        lin0 = _lin(px)
        y0 = lin0 @ wl
        mix = px + (al * cov[sel])[:, None] * (np.array(col, np.float64) / 255.0 - px)
        lin1 = _lin(mix)
        y1 = lin1 @ wl
        lin1 = lin1 * (y0 / np.maximum(y1, 1e-9))[:, None]
        a[sel] = _gam(lin1)
    out = Image.fromarray(np.clip(np.round(a * 255.0), 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    return out


# ================================================================================================ compose
def compose(bg, lit_mask, ghosts, marks, hand_lay, stick, insets=(), top=()):
    """hz_core.compose with the YOU strip kept on top too (nothing is drawn over the HP strip): dim, ghosts, hover marks, then the board's own
    marks (digits, labels, tags, badges, tickets, tape, plates, HUD words, YOU strip) back on top; the hand, the stickers, the insets"""
    base = HL.dim_image(bg.convert('RGB'), lit_mask, k=Z.K_DIM, desat=Z.DESAT).convert('RGBA')
    if CORP in Z.HAZARD_SOFTEN:
        base = Z.soften_hazard(base, lit_mask)
    img = _apply_tints(base.copy())
    for g in Z.GHOST_ARCS:
        img.alpha_composite(g)
    for g in ghosts:
        img.alpha_composite(g)
        Z.add_mask('ghost', g, 160)
    for m in marks:
        img.alpha_composite(m)
        Z.add_mask('hover', m, 128)
    for t in top:
        img.alpha_composite(t)
        Z.add_mask('hover', t, 128)
    keep = np.zeros((H, W), bool)
    for c in Z.MARKS + ('tape', 'plates', 'hud_labels'):
        if c in MASKS and c != 'leader':
            keep |= MASKS[c]
    if 'you' in YOU_MASK:
        keep |= YOU_MASK['you']
    keep = ndi.binary_dilation(keep, iterations=1)
    Z.Z_ORDER.clear()
    for hk in ('ghost', 'hover'):
        if hk in MASKS:
            Z.Z_ORDER['%s under board marks px' % hk] = int((MASKS[hk] & keep).sum())
            MASKS[hk] = MASKS[hk] & ~keep
    a = np.asarray(img).copy()
    b = np.asarray(base)
    a[keep] = b[keep]
    img = Image.fromarray(a, 'RGBA')
    img.alpha_composite(hand_lay)
    img.alpha_composite(stick)
    MASKS['hand'] = np.asarray(hand_lay.split()[3]) >= 128
    for ins in insets:
        img.alpha_composite(ins)
        Z.add_mask('inset', ins, 128)
    return img.convert('RGB')
