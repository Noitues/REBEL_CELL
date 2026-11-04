"""rb_probes (2026-11-04, gate 1): the reviewer's measure.py boxes, re-aimed on the rebuilt plates.  Several of the 2026-11-02 boxes no longer
land on what they name (the board moved: lit cells, new ring tags, the Twist ring turn, the HUD at Mono 23).  Each probe here is derived from the
capture masks of the plate (work/masks_<sfx>.npz) or from its geometry, so it follows the board.

Each probe reports:
  box      the box to use in measure.py (the bounding box of the probe's pixels, or a pure inner square on a flat region)
  L        the percentile L* over the probe's own pixels (the mask inside the box): what the box names, nothing else
  L_box    the same percentile over every pixel of the box (what measure.py reads); differs from L where the box holds other marks
  old_box / old_L   the 2026-11-02 measure.py box and its reading on the same plate
run(sfx, png) -> {name: dict(box, pct, L, L_box, px, lands_on, old_box, old_L)}"""
import json, os, sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import rb_tokens as T
import rb_checks as RC

CC = (536, 540)
OLD = {   # measure.py (AD review 2026-11-02), name -> box, percentile
    'schedule sweep (right rim)': ((880, 300, 960, 700), 95), '+2 THIS TURN tape': ((560, 120, 750, 180), 95),
    'HOT red chevrons s0 (top)': ((500, 215, 560, 300), 95), 'tower pink slice': ((470, 380, 600, 470), 95),
    'tower yellow slice': ((600, 560, 700, 660), 95), 'enemy cell slate (ring NOW, s1)': ((640, 200, 760, 260), 95),
    'empty ring +2 cell': ((120, 600, 250, 700), 95), 'unit token disc': ((150, 480, 210, 540), 95),
    'room backdrop (right)': ((1200, 450, 1800, 800), 95), 'left city backdrop': ((0, 200, 60, 900), 95),
    'HUD mono label text': ((1180, 150, 1420, 172), 99), 'card paper (Brace)': ((930, 1000, 1080, 1060), 95),
    'SEND IT sticker': ((1670, 920, 1880, 1000), 95), 'cold chevrons s4 (brown)': ((200, 690, 260, 760), 95)}
_yy, _xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(_xx - CC[0], _yy - CC[1])
ANG = np.degrees(np.arctan2(_xx - CC[0], -(_yy - CC[1]))) % 360
ICON_R, ICON_DISC = 127.0, 44.0       # slice icon disc centre radius and the radius cut round it (the disc is the tower's peak, not the ink)


def sector(s, r0, r1, half=30.0):
    d = np.abs(((ANG - 60 * s + 180) % 360) - 180)
    return (RHO >= r0) & (RHO < r1) & (d <= half)


def bbox(m, pad=0):
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return [int(xs.min()) - pad, int(ys.min()) - pad, int(xs.max()) + 1 + pad, int(ys.max()) + 1 + pad]


def inner_box(m):
    """a square fully inside mask m (largest by distance transform, half side <= 30); the probe pixels are the whole box"""
    from scipy import ndimage as ndi
    if not m.any():
        return None
    d = ndi.distance_transform_edt(m)
    y, x = np.unravel_index(int(np.argmax(d)), d.shape)
    h = int(min(30, max(2, d[y, x] / 1.5)))
    return [int(x - h), int(y - h), int(x + h), int(y + h)]


def run(sfx, png):
    M = RC.load_masks(sfx)
    rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
    L = T.lstar(T.lum(rgb))
    get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
    marks = np.zeros((1080, 1920), bool)
    for k in ('chev0', 'chev1', 'chev2', 'arcT0', 'arcT1', 'arcT2', 'tokens', 'badges', 'tags', 'ring_tags', 'tickets', 'hp', 'digits', 'labels',
              'tape', 'plates', 'guns', 'plan', 'adj', 'adj_hp', 'hand', 'hud', 'twist_badge', 'leader'):
        marks |= get(k)
    from scipy import ndimage as ndi
    marks = ndi.binary_dilation(marks, iterations=4)
    over = ndi.binary_dilation(get('plan') | get('leader') | get('guns') | get('twist_badge'), iterations=1)
    chk = json.load(open(RC.WORK + 'chk_%s.json' % sfx))
    g = chk['rb']['geometry']
    out = {}

    def put(name, m, pct, what, box=None):
        """m: the probe's pixels.  box: given (an inner square, whose pixels are all probe) or the bounding box of m"""
        o, op = OLD.get(name, (None, 95))
        if box is not None:
            x0, y0, x1, y1 = box
            m = np.zeros((1080, 1920), bool)
            m[y0:y1, x0:x1] = True
        elif m is not None and m.sum() >= 4:
            box = bbox(m)
        if box is None or m is None or m.sum() < 4:
            out[name] = dict(box=None, pct=pct, L=None, L_box=None, px=0, lands_on=what + ' (not on this plate)',
                             old_box=list(o) if o else None, old_L=None if o is None else round(float(np.percentile(L[o[1]:o[3], o[0]:o[2]], op)), 1))
            return
        x0, y0, x1, y1 = box
        out[name] = dict(box=box, pct=pct, L=round(float(np.percentile(L[m], pct)), 1),
                         L_box=round(float(np.percentile(L[y0:y1, x0:x1], pct)), 1), px=int(m.sum()), lands_on=what,
                         old_box=list(o) if o else None, old_L=None if o is None else round(float(np.percentile(L[o[1]:o[3], o[0]:o[2]], op)), 1))

    put('schedule sweep (right rim)', get('tape') & (_xx > 820), 95, 'K tape (THIS TURN cell) where it runs down the right rim')
    put('+2 THIS TURN tape', get('tape') & (_yy < 200), 95, 'K tape, top (THIS TURN cell and its label)')
    live0 = sorted(c['s'] for c in g['cells'] if c['dep'] == 0 and c['state'] == 'live')
    s_hot = live0[0] if live0 else 1
    put('HOT red chevrons (ring NOW, first live sector)', get('chev0') & sector(s_hot, 214, 271, 12) & ~over, 95, 'T HOT chevrons ring NOW sector %d' % s_hot)
    for s, nm in ((0, 'tower pink slice'), (2, 'tower TURRET slice (was: yellow)')):
        cx, cy = CC[0] + ICON_R * math.sin(math.radians(60 * s)), CC[1] - ICON_R * math.cos(math.radians(60 * s))
        ink = get('tower') & sector(s, 90, 190, 22) & (np.hypot(_xx - cx, _yy - cy) > ICON_DISC)
        put(nm, ink, 95, 'P tower slice ink, sector %d, icon disc cut out (r %.0f round the icon)' % (s, ICON_DISC))
    occ = [c for c in g['cells'] if c['dep'] == 0 and c['state'] == 'live']
    if occ:
        c = occ[0]
        put('enemy cell glass (ring NOW, occupied)', None, 95, 'E occupied glass ring NOW sector %d, marks cut' % c['s'],
            box=inner_box(RC.poly_mask([c['poly']]) & ~marks))
    emp = [c for c in g['cells'] if c['dep'] == 2 and c['state'] == 'empty']
    if emp:
        c = emp[0]
        put('empty ring +2 cell', None, 95, 'E empty glass ring +2 sector %d' % c['s'], box=inner_box(RC.poly_mask([c['poly']]) & ~marks))
    u = next((u_ for u_ in g['units'] if u_.get('token')), None)
    if u:
        x, y = u['token']
        put('unit token disc', get('tokens') & (np.hypot(_xx - x, _yy - y) < 30) & ~over, 95, 'E token disc of unit %d' % u['id'])
    rb_ = (_xx >= T.REVIEW_ROOM_BOX[0]) & (_xx < T.REVIEW_ROOM_BOX[2]) & (_yy >= T.REVIEW_ROOM_BOX[1]) & (_yy < T.REVIEW_ROOM_BOX[3])
    put('room backdrop (right)', None, 95, 'the reviewer room box as is (on p2 / p3 it holds HUD scrim and hand ground)', box=list(T.REVIEW_ROOM_BOX))
    put('left city backdrop', None, 95, 'the city strip left of the board', box=list(T.REVIEW_CITY_BOX))
    lab = get('hud') & (L > 60) & (_xx > 1150) & (_xx < 1900) & (_yy > 150) & (_yy < 180)
    put('HUD mono label text (eq row)', lab, 99, 'S HUD Mono 23 labels RAW / SHOT / BRACE / RIDER / LANDS (type pixels, L* > 60)')
    put('card paper (Brace)', None, 95, 'P card paper, rules panel of the first card', box=inner_box(get('card_0') & (L > 60) & (_yy > 990)))
    put('SEND IT sticker', get('send'), 95, 'P SEND IT sticker')
    live1 = sorted(c['s'] for c in g['cells'] if c['dep'] == 1 and c['state'] == 'live')
    s_c = live1[-1] if live1 else 4
    put('cold chevrons (ring +1, last live sector)', get('chev1') & sector(s_c, 271, 328, 12) & ~over, 95, 'T COLD chevrons ring +1 sector %d' % s_c)
    put('enemy HP ticks (ring NOW unit)', get('hp') & sector(s_hot, 214, 271) & ~over, 99, 'E HP ticks of the ring NOW unit at sector %d' % s_hot)
    put('sector digit 0', get('digits') & sector(0, 380, 430, 10), 99, 'K sector digit disc 0')
    put('ring tag NOW W1', get('ring_tags') & (RHO < 300), 99, 'K ring tag of ring NOW')
    return out
